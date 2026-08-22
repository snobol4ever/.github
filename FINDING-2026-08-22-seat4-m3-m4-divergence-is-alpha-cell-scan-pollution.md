# FINDING — beauty's m3-vs-m4 3x run-only divergence is alpha-cell table pollution, not a codegen arm

**Session:** 2026-08-22 seat4 (THE LOOP fleet), row `m3-executes-three-times-m4-on-beauty`, rank 0.
**Instrument:** valgrind callgrind (Ir, deterministic), gdb (breakpoint + hit sampling), source read. RT_OPT=-O0. SCRIP `77b79602`, corpus `4e5fa2d0` at start (corpus witness landed this session at `600ed820`).
**Status:** ROOT-CAUSED, witness minted and checked in, NOT CURED — checked in RED per the brief's own DONE-WHEN alternative. Reason for not curing this session: the mechanism is a hot, previously-corruption-prone shared table (see `AB_FNCELL_MAX` abort comment, `src/emitter/emit.cpp:1368`, citing "R-1 s94: the old arm aliased slot 0 SILENTLY") that underpins the M1 fixed point; a correct fix is identified but sizeable enough to want its own gated rung rather than a rushed change riding this bug hunt.

## 1. THE NUMBER, REPRODUCED INDEPENDENTLY

Brief's claim: m3 run-only 14,504,364,847 Ir vs m4 run 4,833,116,241 Ir = 3.00x, compile subtracted via C3−C1.

My own measurement, same method, same program, current tree:

| | Ir | source |
|---|---|---|
| m3 full compile+run (C3) | 27,781,107,194 | `valgrind --tool=callgrind ./scrip beauty.sno < beauty.sno` |
| m3 compile-only, empty stdin (C1) | 12,996,103,775 | same, `< /dev/null` |
| **m3 run-only (C3−C1)** | **14,785,003,419** | |
| **m4 run-only** | **4,833,116,573** | `valgrind --tool=callgrind` on the linked `beauty.prog < beauty.sno` (compile and run are already separate processes for m4, no subtraction needed) |
| **ratio** | **3.06x** | |

m4's figure reproduces the brief's to 6 significant digits (4,833,116,573 vs 4,833,116,241); m3's is ~2% higher, consistent with ordinary commit drift between sessions the same day, not a different mechanism. Correctness re-verified before measuring: beauty self-host is still the fixed point in both modes (output byte-identical to the 40,971-byte input, and m3-output byte-identical to m4-output) at this tree state.

## 2. THE MECHANISM, FOUND BY PROFILING BEAUTY ITSELF, NOT BY GUESSING

`callgrind_annotate --tree=caller` on the real beauty run isolates one call edge:

```
12,166,805,125 Ir (43.80% of m3's 27.78G FULL total)  <  src/emitter/emit.cpp:bb_ab_fn_cell_ptr (551,979x)
 2,638,240,544 Ir (54.59% of m4's  4.83G run-only total) <  src/emitter/emit.cpp:bb_ab_fn_cell_ptr (551,216x)
```

`bb_ab_fn_cell_ptr` is called **the same ~551K times in both media** — confirming the call SITE is medium-symmetric, exactly as the architecture promises ("modes 3 and 4 share one codegen"). What differs is the cost of each call:

```c
// src/emitter/emit.cpp:1360-1376
#define AB_FNCELL_MAX 1024
static void * g_ab_fn_cells[AB_FNCELL_MAX];
static int    g_ab_fn_cell_n = 0;
static char   g_ab_fn_names[AB_FNCELL_MAX][64];
static int bb_ab_slot_for(const char * fname) {
    for (int i = 0; i < g_ab_fn_cell_n; i++) if (!strncmp(g_ab_fn_names[i], fname, sizeof g_ab_fn_names[0] - 1)) return i;
    ...  // not found: append a new slot
}
void * bb_ab_cell_addr(const char * fname) { return MEDIUM_BINARY ? (void *)&g_ab_fn_cells[bb_ab_slot_for(fname)] : (void *)0; }
void * bb_ab_fn_cell_ptr(const char * fname) { return (void *)&g_ab_fn_cells[bb_ab_slot_for(fname)]; }
```

`bb_ab_slot_for` is a flat **O(N) linear scan** (`strncmp`) with **insert-on-miss** growth, no hashing. Dividing strncmp calls by `bb_ab_fn_cell_ptr` calls gives the average scan depth each call pays:

| | bb_ab_fn_cell_ptr calls | strncmp calls | avg scan depth |
|---|---|---|---|
| m3 | 551,979 | 269,752,048 | **488.7** |
| m4 | 551,216 | 57,445,760 | **104.2** |

**The table mode 3 scans is 4.7x deeper than the table mode 4 scans, for the identical sequence of lookups.** (12,166,805,125 − 2,638,240,544) = 9,528,564,581 Ir of the 9,951,886,846 Ir total run-only gap — **this one mechanism explains 95.7% of the divergence.**

## 3. WHO IS CALLING IT, AND WHY THE TABLE DEPTHS DIFFER

gdb, breakpoint on `rt_dyn_alpha_fn`, live beauty run, first ~105K hits sampled:

```
54,776 EXPR$31 · 1,666 EXPR$111 · 1,638 EXPR$112 · 1,346 EXPR$126 · 1,346 EXPR$125 · ...
```

Every name is `EXPR$NN` — compiler-synthesized **deferred-expression-fragment thunks**, not user `DEFINE`s. These come from SNOBOL4's `*expr` unevaluated/deferred-evaluation operator (`TT_DEFER`, grammar `snobol4.y:170`; collected by `sno_expr_collect`/`sno_expr_collect_wn`, `src/lower/lower_snobol4.c:84-98`), the mechanism behind recursive-descent pattern grammars (`factor = *factor mulop *term . *Binary()` idiom — see `corpus/crosscheck/control/expr_eval.sno`). This is exactly the brief's own lead: "its deferred-call density, its EVAL/pattern machinery." beauty is a large, pattern-heavy source beautifier; its grammar mints hundreds of these.

Call path: `rt_call_proc_descr` (`src/runtime/rt/rt.c:825-847`) → when `p->dyn_scope` → `rt_dyn_alpha_fn(name, fallback)` (`rt.c:849-856`) → `snprintf("alpha$%s", name)` → `bb_ab_fn_cell_ptr` → `bb_ab_slot_for` (the scan). EXPR$ thunks are registered `dyn_scope=1` at `src/lower/lower_snobol4.c:2221`.

**Why the tables differ in size — the process model, not a medium-gated instruction:**
- **Mode 3 (BINARY):** the compiler and the running program are the **same process**. Every procedure/EXPR$-thunk the emitter bakes a direct-call cell for during compilation (`bb_call_proc_staged.cpp`, `bb_define.cpp`, unconditional, for every proc processed) registers a slot in `g_ab_fn_cells` — and that registration is **still there** when the program starts executing, because it never left the process. By the time beauty starts running, its table already holds every compile-time bake.
- **Mode 4 (TEXT):** `scrip --compile` runs in a **separate, short-lived process**; its `g_ab_fn_cells` is discarded when that process exits. The **linked binary starts a fresh process with an empty table**, seeded only by explicit upfront `rt_proc_seal_alpha` calls the driver bakes into the `.s` startup sequence — and that seal loop **explicitly excludes any name containing `$`**:
  ```c
  // src/driver/scrip.c:661
  if (sn4_m4_alpha_seal() && pe->name && strncmp(pe->name, "LBL__", 5) != 0 && !strchr(pe->name, '$')) { ... call rt_proc_seal_alpha ... }
  ```
  So EXPR$-named cells are **never upfront-sealed in mode 4** at all; they enter mode 4's table only lazily, on first miss, via `bb_ab_slot_for`'s own insert-on-miss — keeping mode 4's table small for exactly the class of name that dominates the dynamic-dispatch traffic.

⭐ **Correction to the brief's framing:** this is not "an arm being taken in one medium and not the other" in the sense of divergent codegen. The SAME arm (`rt_dyn_alpha_fn` → `bb_ab_slot_for`) fires the same ~551K times in both media — that part of "modes 3 and 4 share one codegen" holds. What diverges is the **population of a shared, unpartitioned, linearly-scanned runtime table**, and that population is asymmetric for a structural reason (JIT single-process vs compile-then-exec two-process) with one incidental amplifier (the `$`-name exclusion at `scrip.c:661`), not because a template branches on `MEDIUM_BINARY`/`MEDIUM_TEXT` at the call site.

## 4. SMALLER WITNESS, CHECKED IN: `corpus/probe/m3m4div/alpha_scan_pollution.sno`

Body = `corpus/crosscheck/control/expr_eval.sno` unchanged (the small oracle-verified recursive-descent expression parser that already uses `*Push()`/`*Unary()`/`*Binary()` deferred calls — confirmed by profiling to route through this exact mechanism). Prepended: 100 unused `DEFINE`d procedures that inflate `g_ab_fn_cells` at compile time without changing program semantics or `.ref`.

| variant | bb_ab_fn_cell_ptr calls (m3≈m4) | avg scan depth m3 / m4 | m3/m4 run-only Ir ratio |
|---|---|---|---|
| unpadded expr_eval.sno | 147,024 / 147,008 | 3.96 / 1.98 | 1.02x |
| +100 unused DEFINEs (checked-in witness) | 147,024 / 147,008 | (grows with table size) | **1.29x** |

Same direction, same mechanism, smaller magnitude — the ratio moves monotonically with how many compile-time-only names get registered, exactly as the beauty-scale story predicts. This witness could not be pushed further toward beauty's 3.06x: `lower_snobol4.c` enforces a **128-DEFINE ceiling** ("too many DEFINEs in one program... outside the landed subset", `lower_snobol4.c:2189/2338/2356`) and a **4096-entry GLOBAL_MAX** on synthesized `EXPR$` globals, both hit while scaling this witness up (see repro commands below) — real, documented, deliberate boundaries of the current implementation, not something this row should route around. beauty simply has far more distinct DEFINEs and pattern-grammar productions than either ceiling allows a hand-built witness to reach.

**Repro:**
```bash
cd SCRIP
./scrip corpus/probe/m3m4div/alpha_scan_pollution.sno < corpus/probe/m3m4div/alpha_scan_pollution.input | cmp - corpus/probe/m3m4div/alpha_scan_pollution.ref   # m3, silent = match
./scrip --compile corpus/probe/m3m4div/alpha_scan_pollution.sno > /tmp/asp.s && gcc -no-pie /tmp/asp.s -Lout -lscrip_rt -lm -Wl,-rpath,"$PWD/out" -o /tmp/asp.prog
/tmp/asp.prog < corpus/probe/m3m4div/alpha_scan_pollution.input | cmp - corpus/probe/m3m4div/alpha_scan_pollution.ref   # m4, silent = match
```

## 5. THE FIX IS ALREADY IDENTIFIED — CONVERGENCE WITH A SIBLING FINDING

`FINDING-2026-08-22-hq-scrip-spends-under-one-percent-of-its-instructions-running-the-program.md` (same day, HQ) independently ranked `bb_ab_slot_for` **#1** for cure, for a different reason (43.8% of m3's total Ir vs SPITBOL): "Bake or hash `bb_ab_slot_for`... a bake, not a hash — though a hash alone recovers most of it."

⭐ **That fix would cure both problems at once.** An O(1) hash lookup (same `g_ab_fn_cells`/`g_ab_fn_names` storage, hash-then-probe instead of linear-scan-from-0 — no new global needed, just a different algorithm over the existing arrays) doesn't care how deep the table is, so mode 3's carried-forward compile-time pollution would stop costing anything, closing this row's divergence as a side effect of closing that one.

**Why this session did not attempt it:** `bb_ab_slot_for`'s own abort message (`emit.cpp:1368`) cites a prior **silent-corruption** class at this exact site ("the old arm aliased slot 0 SILENTLY"); it is reached from at least four sites across three files with two distinct "faces" (`bb_ab_cell_addr` NULL-in-TEXT vs `bb_ab_fn_cell_ptr` never-NULL) whose exact TEXT-vs-BINARY operand rendering lives inside `x86_asm.h`'s `[rip@cell + __]` handling (not independently re-verified byte-for-byte this session); and it sits directly under beauty's M1 fixed point, which per `PLAN.md` took 4.5 months to earn. RULES.md's GATE-BEFORE-LAND and killswitch/MD5-blast-radius requirements for any codegen change are appropriately heavy for a change here — this deserves its own gated rung with full corpus + beauty-fixed-point re-verification, not a same-session addendum to a bug hunt. Recommending it be queued (or folded into whatever rung eventually lands the sibling finding's #1 item) rather than landing a hurried version here.

## 6. DONE-WHEN, CHECKED

- ✅ Divergence root-caused to a named mechanism at file:line: `src/emitter/emit.cpp:1366-1376` (`bb_ab_slot_for`/`bb_ab_cell_addr`/`bb_ab_fn_cell_ptr`), reached via `src/runtime/rt/rt.c:849-856` (`rt_dyn_alpha_fn`), asymmetry rooted in `src/driver/scrip.c:661`'s `$`-name exclusion plus the JIT-vs-compile-then-exec process-model difference.
- ✅ A witness smaller than beauty reproduces it: `corpus/probe/m3m4div/alpha_scan_pollution.sno` (357 lines vs beauty's several thousand across includes), same mechanism, ratio moves 1.02x→1.29x under a controlled knob.
- ⛔ Not cured this session — checked in RED per the brief's own alternative, with this FINDING stating the mechanism and pointing at the already-identified, already-ranked fix.
