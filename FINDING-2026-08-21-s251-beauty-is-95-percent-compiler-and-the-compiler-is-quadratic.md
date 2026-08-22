# FINDING — s251 HQ: beauty self-host is 95% COMPILER, the compiler is O(N²), and one linear scan is 43% of it

**Date:** 2026-08-21 · **Seat:** HQ (`/home/claude`, Claude Opus 5) · **Topic:** BEAUTY-10X first measurement · **Status:** MEASURED, culprit named, fix not yet applied
**Machine:** AMD Ryzen 7 PRO 8840U (Zen 4), governor `performance`. **RT_OPT `-O0`** (repo default). SCRIP `6049726df`. Instruments: `perf stat -r 20`, `valgrind --tool=callgrind` 3.22.0.
**Supersedes the working assumption** in `ARCH-PERF-TOOLING.md` §3 Q1 that beauty would prove bad-speculation or frontend bound. It is neither. See §2.

## 1. THE HEADLINE, AND IT IS NOT THE ONE WE WANTED

beauty self-host (`scrip beauty.sno < beauty.sno`), verified this session as a **true fixed point** — output byte-identical to the 40,971-byte input — and **byte-identical to SPITBOL's output** on the same input. Correctness is not in question. Speed is:

| | wall clock | instructions | IPC | branch-miss | frontend idle |
|---|---|---|---|---|---|
| SCRIP m3 | **1.8185 s** ± 2.26% | 26,205 M | **3.20** | **0.14%** | 4.93% |
| SPITBOL `-bf` | **0.0785 s** ± 0.60% | 810 M | 2.33 | 0.83% | 22.70% |

**SCRIP is 23.2× SLOWER than SPITBOL on beauty self-host, executing 32.3× more instructions.** The 10x banner is currently a 232x gap.

## 2. ⛔ THE MACHINE IS NOT THE PROBLEM — RETIRE THE MICRO-OPTIMIZATION PRIOR

SCRIP's execution quality is **excellent and beats SPITBOL on every microarchitectural axis**: IPC 3.20 vs 2.33 (near Zen 4 peak), branch mispredicts 0.14% vs 0.83% (6× better), frontend idle 4.93% vs 22.70%. The compile-time port wiring is doing exactly what it was designed to do.

**Consequence, and it is the important one:** SCRIP is not bad-speculation bound, not frontend bound, not cache bound. It is **instruction-count bound**. Therefore:
- **Hand-written register-aware asm cannot deliver 10x.** It attacks IPC, which is already 3.20; the ceiling is ~4–5, i.e. **at most ~1.4×**.
- **Box fusion cannot deliver 10x.** It attacks mispredicts and I-footprint, already 0.14% and 4.93%. Nearly nothing left there.
- The only lever with 10x in it is **executing fewer instructions**, which is an *algorithmic* fix, not a codegen one.

This does not retire the asm campaign — it **re-sequences** it. Asm is the last 1.4×, applied after the algorithmic work, not the first move.

## 3. THE SPLIT: 94.8% OF beauty SELF-HOST IS SCRIP COMPILING beauty

Isolated by running each engine with empty stdin (beauty then does no work) and subtracting:

| phase | SCRIP m3 | SPITBOL | ratio |
|---|---|---|---|
| **compile** | **25,516 M** (94.8%) | 11.3 M | **SCRIP 2,258× worse** |
| **run** (beautify 40 KB) | 1,387 M | 798 M | SCRIP 1.74× worse |
| total | 26,903 M | 810 M | 33.2× |

*(Caveat: "compile" here is compile + a near-empty run, so it marginally overstates compile on both sides. The 2,258× is not sensitive to that.)*

**The emitted-code story is fine.** 1.74× off a mature hand-tuned SIL implementation, with better IPC and better prediction, is a good place to be — and *that* number is what box fusion, concat/store inlining, the table path, and asm all target. Getting the run phase to 10× SPITBOL means 798→80 M, a 17× cut. Hard, but that is the honest codegen goal.

**The headline number is not that.** Even with an *infinitely fast runtime*, beauty self-host still takes 1.738 s vs SPITBOL's 0.0754 s — **still 23× slower**. No amount of codegen work can move the milestone while the compiler burns 1.74 seconds.

## 4. THE COMPILER IS O(N²)

Synthetic valid programs of N statements (` X = i` ×N + `END`), compile-only, `perf stat -r 3`:

| N | instructions | ×2 growth, floor-adjusted |
|---|---|---|
| 50 | 34.7 M | — |
| 100 | 76.3 M | 2.76× |
| 200 | 213.4 M | 3.10× |
| 400 | 701.9 M | 3.41× |
| 800 | 2,536.8 M | 3.66× |

Doubling N multiplies cost by a ratio **climbing monotonically toward 4**. Fixed startup floor is 11.1 M (a 2-line program). This is quadratic with a lower-order term, not linear.

⚠️ **A false signal was caught and discarded en route:** `head -311 beauty.sno` compiled in 18.5 M, which looked like beautiful sub-linear scaling. It had exited `rc=1` — `cannot open include 'global.inc'` — having done nothing. Arbitrary prefixes of `beauty.sno` are not valid programs (`board_beauty_m1.sh` says so in its own header) and relative includes resolve against the CWD. The synthetic series above replaced it. This is the "non-empty is not alive" class again, third distinct form.

## 5. THE CULPRIT, NAMED

`callgrind` on the N=400 case (698 M Ir), exclusive cost:

| Ir | % | site |
|---|---|---|
| 299,820,192 | **42.93%** | `src/optimizer/dead_goto.c:dg_index_of` |
| 118,682,258 | 16.99% | `src/emitter/emit.cpp:codegen_flat_chain_body` |
| 40,570,324 | **5.81%** | `src/optimizer/branch_chain.c:bc_index_of` |
| 39,549,930 | 5.66% | `src/emitter/emit.cpp:zd_plan` |
| 28,048,705 | 4.02% | `src/templates/x86_asm.h:bb_emit_x86` |
| 21,938,939 | 3.14% | `src/lower/lower_common.c:bb_src_of` |

Both `*_index_of` are the same one-line linear scan, byte-identical across the two files:

```c
static int dg_index_of(IR_graph_t * g, IR_t * p) { for (int i = 0; i < g->n; i++) if (g->all[i] == p) return i; return -1; }
```

`dead_goto.c:14` calls it **inside a loop over every node, once per operand** — O(N × operands × N). `bc_index_of` is the same shape. **Together: 48.7% of all compile instructions, and they are the entire quadratic term.**

## 6. THE FIX, AND WHY IT NEEDS NO GLOBAL GRANT

Build a pointer→index map once per `dg_run` / `bc_*` invocation — O(N) build, O(1) lookup — instead of scanning per query. The map is a **function-local allocation**, not file-scope state, so the no-new-globals rule is not engaged and no in-chat grant is required. No signature changes, no `IR_t`/`BB_t` field additions (PEERS RULE intact), no per-op filtering.

Expected: removes ~49% of compile instructions at N=400 **and removes the quadratic term entirely**, so the win *grows* with program size. beauty.sno pulls in `.inc` files and is far larger than N=400, so its quadratic share is materially higher than 49% — the measured 42.93% is a floor, not an estimate of the beauty case.

**Verification required before any verdict:** `make pristine`, re-run the scaling series (the growth ratio must go flat), re-run beauty self-host for the fixed point AND SPITBOL-identical output, then the named gates.

## 7. WHAT THIS RE-ORDERS

The `ARCH-PERF-TOOLING.md` §4 ranking was written for the *run* phase and stands for it — but it is now the **second** campaign, not the first:

1. **⭐ NEW #1 — de-quadratic the compiler.** `dg_index_of` + `bc_index_of` first; then re-measure, since removing the dominant term will re-rank everything beneath it (`codegen_flat_chain_body` at 17% is the next suspect and should be checked for the same shape).
2. Then the run-phase ranking as written: table path (s199, 91%) → inline concat/store (s200) → box fusion (s250) → kill the PLT → asm on what survives.

Also worth noting for §4-item-4: the PLT tax is real but these top functions all live in `libscrip_rt.so`, so the *compiler itself* is paying cross-.so indirection on every one of these calls too.

## 8. RESULT — TWO PASSES LANDED, 1.72× ON BEAUTY, THE QUADRATIC TERM SURVIVES

| | beauty wall | beauty instructions | N=800 synthetic |
|---|---|---|---|
| s251 baseline | 1.8185 s | 26,205 M | 2,536.8 M |
| after `8ffcd5ea` (optimizer `*_index_of` class) | 1.1399 s | 15,358 M | 1,143.9 M |
| after `1a812667` (emitter RPO visited-set) | **1.0574 s** | **14,240 M** | **1,024.5 M** |
| **cumulative** | **1.72×** | **1.84×** | **2.48×** |

Correctness held at every step: beauty self-host fixed point in **both** modes, m3 byte-identical to SPITBOL `-bf`, corpus m3 339/341 and m4 338/341+1 SKIP (the standing reds exactly), gates `emit_no_lang` + `template_medium_invisible` rc=0.

**The quadratic TERM is not gone.** Growth per doubling is still climbing — 2.36 → 2.58 → 2.89 → 3.23 — so O(N²) still dominates asymptotically; we removed constant factors and one of its sources, not the shape. vs SPITBOL beauty went 23.2× → **13.5× slower**.

Remaining sites, all the same "linear scan for pointer membership" shape:
- `emit.cpp:flat_beta_used_scan` — explicit `for a in operands: for k in n: if nodes[k] == operands[a]`
- `emit.cpp:zd_plan` — `for _bi in n: for _bj <= _bi`
- `emit.cpp:codegen_flat_chain_body` — the floater double-loop over `g_emit_cfg->n` (two nested full scans)
- `lower_common.c:bb_src_of` (6.1%) and `__strcmp_avx2` (4.55%) — name lookups by string compare, a *different* class worth its own pass

**Retired as not worth touching:** `pat_fold.c` (its `pf_run` is `{ (void)g; return 0; }` — the whole pass is dead code, a finding in itself), `region_report.c` and `scrip_ir.c:bb_index_of` (diagnostic `--dump-ir` paths, absent from every profile).

## 9. PROTOCOL — ICON AND PROLOG ARE OUT OF THE WORKFLOW (Lon s251)

Lon, in-chat: *"remove the fact that Icon or Prolog are even being checked in your work flow. Just quit running that script"*, and *"There is no Icon or Prolog work really possible now."* The blocking set is now **`test_corpus_snobol4.sh` + `test_gate_emit_no_lang.sh` + `test_gate_template_medium_invisible.sh` + the goal file's named gate**. `test_smoke_{icon,prolog,snocone,rebus}.sh` and `test_gate_icn_*.sh` are not to be run at all. ⛔ The scripts were NOT edited to return 0 — a lying test is the `make test` false-green trap. They stay truthful on disk; we stop running them. Reverts when SNOBOL4 is solid.

Baseline-verified before the policy landed, for the record: Prolog smoke 3/5 and Snocone 4/5 were **already red on an unmodified tree**. The two Prolog reds were diagnosed to a precise mechanism before the campaign was dropped: a body goal of **arity 0** (`nl`, `true`, or a user `p.`) loses the head-variable bindings — `t(X) :- write(X), nl.` prints nothing while `t(X) :- write(X), write(y).` prints `3y`. `--dump-ir` shows the arity-0 case wiring a `SUSPEND` where the working sibling wires `MOVE_LABEL`, and leaving the `DISJUNCTION` off the emit spine ("unreached"). Independently, an unbound-variable query against a **multi-clause** predicate returns nothing (`f(a). f(b).` fails where `f(a).` alone works). Not fixed; recorded so the next Prolog session starts from the mechanism, not from scratch.
