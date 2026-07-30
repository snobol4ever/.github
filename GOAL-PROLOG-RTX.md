# GOAL-PROLOG-RTX.md — The Prolog Runtime in Optimized x86-64 Assembly

**Minted s221-PL (2026-07-30) on Lon's directive:** *"Notice how GOAL-SNOBOL4-RTX and GOAL-ICON-RTX are
proceding with replacing the C runtime with highly optimized register-aware ASM code. You do the same.
Join the coordination that is setup by the two, and y'all will be come three."*

**Ladder name:** `PL-RTX` — the **third** RTX ladder, running CONCURRENTLY with `GOAL-SNOBOL4-RTX.md`
(`SN4-RTX`), `GOAL-ICON-RTX.md` (`ICON-RTX`), and `GOAL-PROLOG-BB.md` (the ζ / PL-SINK ladder).

**Contract:** `ARCH-PROLOG-RTX.md` — read it before any rung. It does NOT restate step 0; it points at
`ARCH-SNOBOL4-RTX.md` §7, which is the shared checklist, and records only Prolog's deltas.

---

## ⛔⛔ SYMBOL OWNERSHIP IS NOT IN THIS FILE — IT IS IN `RTX-CLAIMS.md`

The runtime is SHARED (~20,000 lines, one `.so`, six languages). **Three** RTX ladders now work it.
Check a symbol OUT in that ledger — **and PUSH the claim before the work, not with it** — before writing
code. Run `CUR_SESSION=<n> bash scripts/util_rtx_claims.sh` at session start and session close.

⭐ **Prolog's advantage: its hot surface is almost entirely Prolog-EXCLUSIVE** (`rt_pl_dop_*`), so this
ladder can run for many sessions with **no arbitration against SN4-RTX or ICON-RTX at all.**
⛔ **Prolog's disadvantage, and it is the whole scope problem: its hot surface COLLIDES with its own BB
ladder's PL-SINK rungs.** See §SCOPE below. That collision, not inter-RTX contention, is this ladder's
governing constraint.

---

## ⛔ LIVE CURSOR — s221-PL (2026-07-30): **⭐⭐ LADDER OPENED. THE SURFACE IS MEASURED, STATIC RANKING IS INVERTED ACROSS A 400× SPREAD, TWO LEDGER-NAMED TOP SYMBOLS ARE PHANTOMS, AND NINE OF THE TOP ELEVEN COLLIDE WITH AN OPEN PL-SINK RUNG. NO ASM WRITTEN — DELIBERATELY.**

SCRIP `b1ca896e` **UNMODIFIED (zero source edits — measurement session).** RT_OPT=`-O0` throughout.
FINDING: `FINDING-2026-07-30-CLAUDE-PL-RTX-0-LADDER-OPENED-AND-SINK-MAKES-RTX-VACUOUS-BY-CONSTRUCTION.md`

1. ⭐⭐ **THE GOVERNING FACT: A LANDED PL-SINK RUNG MAKES THE CORRESPONDING PL-RTX RUNG VACUOUS BY
   CONSTRUCTION.** SINK makes the EMITTER inline a fast path; RTX rewrites the CALLEE in asm. An inline
   fast path **removes the arrivals an asm port would accelerate.** Proof, measured not argued:
   `rt_pl_dop_trail_mark` has **5,814 static sites** (static rank 5) and **22 dynamic calls across all 22
   van Roy benchmarks** = exactly 1/program = **the setup floor** (`hello.pl` also measures 1), because
   `src/templates/bb_call_fn.cpp:347` is PL-SINK-8's emitted fast path and its own comment calls
   `rt_pl_dop_trail_mark` *"the slow-path oracle."* ⇒ **fourth shape of the bypassed-family disease and a
   new one: s211-ICN's rule "port the arm the guard REJECTS" does not apply, because the callee is left
   holding NOTHING.** ⛔ Also falsifies PL-SINK-8's own *"pairs 1:1 with SINK-9"* — **22 vs 2,114,931.**
2. ⭐⭐ **STATIC RANKING FALSIFIED, SIXTH TIME ON THE PROJECT, WORST SPREAD YET.** `rt_pl_dop_cmp_ne`:
   **102 static sites → rank 5 by execution (880,792 calls).** `rt_pl_dop_mkc`: **40,854 sites (400×
   more) → rank 4.** Three more phantoms-by-execution totalling ~11,300 sites: `rt_proc_call_open`
   (5,626 sites, **0 calls in 22/22**), `rt_call_arr_gen` (498, 0), `rt_faildescr` (171, 0).
3. ⛔⛔ **TWO SYMBOLS `RTX-CLAIMS.md`'s PROSE NAMES AS PROLOG'S #3 AND #4 ARE DECLARATION-ONLY
   PHANTOMS.** `rt_node_to_term` = 2 tree occurrences, **both declarations** (`rt/rt.h:60`,
   `bb_common.h:24`); `resolve_cp_current` = **1 declaration** (`builtins/resolution.h:52`). Zero
   definitions, zero call sites, absent from the `.so`. **The repaired gate correctly omits both — the
   PROSE in the same file was never re-derived from it.** ⭐ And it falsifies that prose's own caveat
   *"presence is robust (corruption drops matches, it does not invent symbol names)"*: **presence was not
   robust**, because a *different* defect (matching header declarations) invents names that corruption
   never would.
4. ⭐ **THE COMPILE-PHASE CONFOUND IS FAMILY-SPECIFIC, NOT UNIVERSAL — MEASURED.** ICON-RTX voided its
   s218 ranking at s220 as ~100% compile phase and adopted `count(4N) − count(N)`. I used that method
   AND measured the floor: **every `rt_pl_dop_*` symbol counts ZERO on `hello.pl`** ⇒ the `dop` family is
   emitted-code-only, so for Prolog absolute counts already ARE run-phase counts. Delta stays correct,
   is not load-bearing here. **Measure the floor (one `hello` run); do not inherit either verdict.**
5. ⛔⛔ **0(d) SCALING IS A PROPERTY OF THE (SYMBOL, WORKLOAD) PAIR, NOT OF THE SYMBOL — AND THIS ONE
   SHOULD CHANGE BOTH OTHER LADDERS' PRACTICE.** I ranked twice on hand-picked scaled workloads with
   exact scaling verified (`nrev` 4.00×, `fib` 2.62× = φ² exactly). **The corpus rank-1 symbol
   `rt_pl_dop_trail_unwind` measured ZERO on BOTH.** A clean 4.00× proves a symbol is hot *there*, not
   that it matters. Both other ladders rank on one workload; the failure is silent.
6. ⚠ **CORPUS CONCENTRATION — QUOTE IT WITH EVERY NUMBER.** `queensn` + `queens` = **~78% of all
   counted arrivals** across 22 programs. The ranking is substantially a statement about two
   backtracking-search programs. **Reach (programs-touched) is reported beside every count for this
   reason, and it is why rung 1 is the rank-2 symbol.**
7. **GATES:** Prolog watermark **ESTABLISHED GREEN — `test_prolog_rung_suite.sh` 164/164 interp +
   164/164 compile, FAIL=0**, full build `-O0`. Ledger gate `CUR_SESSION=221`: **3 FATAL / 36 WARN**, and
   ⛔ **all 3 fatals are pre-existing on OTHER ladders' rows — I edited none** (`rt_frame` = ICON-RTX
   rot; `rt_defer_close` + `rt_defer_open` = SN4-RTX rows non-`DONE` while already asm, **reported by
   s216-ICN five sessions ago and still open**). Surface: 1,367 icon / 211 snobol4 / **839 prolog**
   programs.

**WATERMARK:** SCRIP `b1ca896e` UNMODIFIED / corpus `<none>` / `.github` FINDING + this file +
`ARCH-PROLOG-RTX.md` + `RTX-CLAIMS.md` edits — **PUSH BLOCKED, credential needed.**

**BANKED (inherited from `GOAL-PROLOG-BB.md`, all still live):** `unary_not.sno` emits a `.string` from
uninitialised memory (poisons every `.s` byte-identity sweep); engine-wide silent-fail on undefined
predicates; int/float standard-order conflation; lexer escape three-site/two-behaviour; NO-LCO segfault;
nested-`\+` binding leak; `retractall/1` gaps.

8. ⚠⚠ **NARROWED, NOT RESOLVED — AND IT MAY OUTRANK RTX-1-PL, SO IT GOES FIRST (⇒ RTX-13-PL).** `_det0`…`_det4` all measure **ZERO** while generic `_det` measures **430,081** ⇒ `det_fuse` is false at Prolog's hot sites, which also forces `dc` false (PL-DC requires it). **ESTABLISHED:** `lower_prolog.c:388` sets `IR_LIT(nd).sval = pl_pi_name("$call", t->n)`, and `pl_pi_name` is `snprintf("%s/%d")` ⇒ Prolog's `IR_CALL_PROC_STAGED` sites carry the **synthetic arity-qualified name `"$call/N"`, NOT the callee predicate's own registered name.** ⛔ **NOT ESTABLISHED — DO NOT QUOTE A CAUSE YET:** `det_fuse = (det_idx >= 0 && x86_zc_frame() == ZC_FRAME_RSP && det_nA >= 0 && det_nA <= 4)`, and I did **not** determine which conjunct fails. `"$call` does appear 3× in `scrip.c`/`lower_prolog.c`, so `$call/N` **may well be a registered dispatcher** and `det_idx` may resolve fine — in which case the failing conjunct is the FRAME REGIME or the ARITY, not the name. **I ran out of session before instrumenting it and I am not guessing: naming a cause on a partial read is the s209 mistake this project has recorded twice.** ⇒ **RTX-13-PL STEP 1 IS A ONE-LINE EMIT-TIME INSTRUMENT** printing the three conjuncts at each Prolog `IR_CALL_PROC_STAGED` site. **If the fuse can be made to fire, it lights up TWO already-built optimizations (PL-REGAIN-4 + PL-DC) for Prolog at once and removes the crossing that RTX-1-PL would merely make faster — a LOWERING fix that beats an ASM fix.** Measure it before writing any asm.

**NEXT:** ⭐ **(0) RTX-13-PL step 1 — the `det_fuse` conjunct instrument (item 8). It may make RTX-1-PL moot; do it FIRST.** Then the §SCOPE ruling from Lon, then **RTX-1-PL on `rt_proc_call_open_det`** (step 0 partially
done — 0(c), 0(f-pre), 0(g) all owed before asm).

---

## ⛔⛔ SCOPE — THE RULING THIS LADDER NEEDS FROM LON

Nine of the top eleven Prolog symbols are already-SINK'd or claimed by an **OPEN** PL-SINK rung in
`GOAL-PROLOG-BB.md`, which is a **concurrently running session**:

| RTX rank | symbol | corpus calls | reach | PL-SINK rung | SINK status | PL-RTX |
|---:|---|---:|---|---|---|---|
| 1 | `rt_pl_dop_trail_unwind` | 2,114,931 | 10/22 | **SINK-9** | ⏳ OPEN | ⛔ COLLISION |
| 2 | `rt_proc_call_open_det` | 2,060,043 | **19/22** | **none** | — | ✅ **CLEAR** |
| 3 | `rt_pl_dop_unify` | 1,108,786 | **22/22** | SINK-1 | ✅ s142 | ⚠ reduced |
| 4 | `rt_pl_dop_mkc` | 1,018,100 | 19/22 | SINK-3 | ✅ s145 | ⚠ reduced |
| 5 | `rt_pl_dop_cmp_ne` | 880,792 | 5/22 | **SINK-7** | ⏳ OPEN | ⛔ COLLISION |
| 6 | `rt_pl_dop_unwind_nothrow` | 873,060 | 16/22 | **SINK-9** | ⏳ OPEN | ⛔ COLLISION |
| 7 | `rt_pl_dop_is_v` | 735,898 | 14/22 | **SINK-5** | ⏳ OPEN | ⛔ COLLISION |
| 8 | `rt_pl_dop_ax_sub` | 731,498 | 12/22 | **SINK-6** | ⏳ OPEN | ⛔ COLLISION |
| 9 | `rt_pl_dop_unify_cs` | 622,812 | 12/22 | SINK-1 fam | ✅ | ⚠ reduced |
| 10 | `rt_pl_dop_ax_add` | 573,678 | 6/22 | **SINK-6** | ⏳ OPEN | ⛔ COLLISION |
| 11 | `rt_pl_dop_ix_g` | 289,004 | 15/22 | SINK-4 | ✅ s148, **kk==4 deferred** | ✅ deferred arm CLEAR |
| — | `rt_pl_dop_trail_mark` | **22** | 22/22 | SINK-8 | ✅ s146 | ⛔ **VESTIGIAL** |

**THE QUESTION.** When a Prolog symbol is hot and has an open SINK rung, does it get
**(a)** SINK (emitter inline fast path), **(b)** RTX (runtime body in asm), or
**(c)** SINK for the guarded fast arm **+ RTX for the arm SINK deliberately defers to C**?

⭐ **RECOMMENDED: (c)** — the only option under which both ladders keep working. SINK's inline path takes
the arrivals it guards, so **RTX's honest scope is the residue SINK refuses**, which is already
enumerated in `GOAL-PROLOG-BB.md`: SINK-4's `kk==4` per-site intern cache, SINK-7's out-of-2⁵³ range
arm, SINK-6's `div`/`idiv`/`mod` guard arms (`b==0`, `b==−1`) and any `DT_R`, SINK-5's non-`{I,R}` tags —
**plus every symbol with no SINK rung at all**, which is where rung 1 lives.
Under (a) this ladder has ~2 live rungs. Under (b) two concurrent sessions fight over one
emitter/runtime boundary per symbol, and per RULES.md concurrency that is safe for FILES and **not** safe
for a shared performance claim.

⛔ **UNTIL RULED: this ladder works ONLY symbols with no SINK rung, or SINK-deferred arms.** Rung 1
satisfies both.

---

## THE LADDER

### - [ ] RUNG RTX-1-PL — `rt_proc_call_open_det` (the deterministic predicate-call open)
**WHY IT IS FIRST, AND IT IS FIRST UNDER EVERY SCOPE OPTION:** rank **2** by execution (2,060,043),
rank **1 by REACH (19/22 programs — the broadest of any Prolog symbol)**, **no PL-SINK rung**, **not a
`dop`** so structurally outside SINK's `$op` territory, **Prolog-dominant** (5,291 static sites),
**absent from `RTX-CLAIMS.md` entirely**, and in the CALL family where SN4-RTX has already paid for the
lessons (`rt_proc_call_epilogue_γ/ω` are `DONE:SN4-RTX:881ea03d`).
⭐ **Its sibling `rt_proc_call_open` measures ZERO calls in 22/22 programs** despite 5,626 static sites —
**the `_det` variant takes the entire path, and only the dynamic sweep could show that.**

**STEP 0 STATUS — PARTIALLY DONE s221; THE REST IS OWED BEFORE ANY ASM:**
- [x] **0(a) live definition exists** — exported `T` in `out/libscrip_rt.so`.
- [x] **0(b) spelling round-trips** — taken from `nm -D --defined-only`, not from prose. ⚠ Note the
  neighbouring `rt_proc_call_epilogue_γ/ω` carry literal UTF-8 GREEK; **this symbol does not**, but any
  new sibling in the family must be taken as the tree spells it (RTX-4 s165 truncation class).
- [x] **0(d) executed + scales** — 13,226 → 52,901 at nrev N=25→100 (**4.00× exact**); 2,060,043
  corpus-wide across 19/22 programs. ⚠ **ZERO on `fib`** — per cursor item 5, that is a statement about
  `fib`, not about the symbol.
- [x] **0(e) not already assembly** — grep run **with `--include=*.S`** (the load-bearing flag, s200).
- [x] ✅ **0(c) DONE — AND IT FIRED. SLICE 0 LANDED (SCRIP `1f91a433`).** `nm out/rt_pic/rt.o` showed **three of the five things the port needs were `static` and unreferenceable from `.S`**: `g_rt_gen_procs` `b`, `g_rt_gen_proc_count` `b`, `g_pcall_cap` `b` — plus TWO `static` FUNCTIONS, `rt_proc_call_prologue_lex` `t` and `rt_pcall_grow` `t`. **The `.so` reported all of them fine**, exactly as s209 said it structurally must. Promoted the three globals to `visibility("hidden")` after checking **s214 axis 2 first** (zero template/emitter refs ⇒ not named in emitted mode-4 TEXT ⇒ `hidden` is safe); verified **absent from the dynamic table** after ⇒ direct `[rip+sym]`. Now all nine cluster globals are `B`/`D`. Gates: **Prolog 164/164 + 164/164 · SNOBOL4 7/0 · Icon 14/14 m3 + 14/14 m4**, all green, visibility-only change.
- [x] ✅ **0(f-pre) DONE — NOT straight-line, so 0(f) is NOT discharged in advance.** All six family members share one shape: two decline guards (`idx` range; `!p->fn || p->dyn_scope`) → optional `g_call_args` copies → **a call to `rt_proc_call_prologue_lex`** → `return p->fn`. ⭐ **COST DECOMPOSITION, and it is FAVOURABLE — the opposite of the RTX-4/`rt_make_list` shape:** the callee chain bottoms out in cheap, inlinable work. `rt_proc_call_prologue_lex` is ~12 stores + 2 increments + `fbytes` arithmetic **whose result every caller DISCARDS via `(void)`** ⇒ dead work on this path. Its one call, `rt_pcall_grow`, is **`if (g_pcall_top < g_pcall_cap) return;`** — a capacity guard whose common case returns immediately ⇒ the ideal inline-with-bail arm. Its other call, `rt_value_trail_mark`, is **`{ return g_pl_trail.top; }`** — one global load. ⇒ **the entire cluster can be absorbed with NO call remaining in the success path.** Absorbing a `static` callee into a gated wrapper's asm is precedented TWICE (s211 `rt_parse_num_d`, s216 `data_field_ptr`) and needs no contract amendment.
- [x] ✅ **0(g) DONE — THE LIVE ARM IS THE GENERIC FORM, AND THE "OPTIMIZED" ARMS ARE DEAD.** `bb_call_proc_staged.cpp` emits a THREE-TIER ladder: (1) **PL-DC** direct `call proc_X_dcα` (no open crossing at all, gated `rt_pl_dc_ok`), (2) **fused `rt_proc_call_open_detN`** (≤4 args, `ZC_FRAME_RSP`), (3) **classic generic `rt_proc_call_open_det`**. ⭐⭐ **MEASURED on `queens.pl`: generic `_det` = 430,081 · `_det0`…`_det4` = ZERO, all five.** ⇒ **porting the generic form ports the live arm.** ⛔ **AND THE WHOLE PL-REGAIN-4 FUSED FAMILY IS DEAD ON THE HOTTEST PROLOG PROGRAM** — it exists to collapse `{rt_arg_stage × nargs + open_det}` into one crossing, and `rt_arg_stage` independently measures **8 calls across 22 programs**. Since `dc` requires `det_fuse`, **PL-DC is dead here too.** ⇒ **an entire shipped two-rung optimization pair is bypassed on the hot path, and only the dynamic sweep could show it.** ⚠ **OWED: WHY `det_fuse` is false for Prolog's hot sites** (`det_idx < 0` / frame regime / `nargs > 4`) — Prolog carries 5,291 static `_det` sites, so if the fused arm can be made to fire that may outrank the asm port entirely. **Measure before porting: this is a possible RTX-13-PL (fix the eligibility) that would beat RTX-1-PL.**
- [ ] ⛔ **REMAINING 0(c) for the port itself:** `rt.o`, not
  `libscrip_rt.so`: `B`/`D` = linkable, `b`/`d` = `static` and **unreferenceable from `.S`** (s209 —
  the `.so` is structurally incapable of separating `static` from `visibility("hidden")`).
  ⛔ **AND s214's second axis:** if any such global is ALSO named by a template in emitted mode-4 TEXT it
  must stay **DYNAMICALLY EXPORTED**, and then every `.so`-internal access must become `@GOTPCREL` or a
  `-no-pie` copy relocation silently makes it a DIFFERENT VARIABLE.
- [ ] ⛔ **0(f-pre) READ THE C BODY AND ENUMERATE ITS ARMS.** If it is straight-line (no arm, no call, no
  early return) then entries==commits by construction and 0(f) is discharged before the asm exists
  (s217). Otherwise the ported arm's liveness must be established.
- [ ] ⛔ **0(g) READ THE EMITTING TEMPLATE FIRST (s211-ICN, and Prolog is the language where this bites
  hardest).** Grep the `bb_*.cpp` that emits the call for an inline `cmp`/`je` tag guard. **PL-SINK is
  an entire ladder of exactly such guards** — cursor item 1 is what happens when one lands. If a guard
  steers arrivals away from the arm I intend to port, **port the arm the guard REJECTS**, or refuse.
- [ ] Then, and only then: port behind gate `SCRIP_RTX_PLCALL`, C body → `c_rt_proc_call_open_det`.

**GATES OWED AT LANDING:** Prolog `test_prolog_rung_suite.sh` **164/164 + 164/164** (the watermark
established this session) · SNOBOL4 + Icon batteries as **no-regression only** (⛔ per
`ARCH-SNOBOL4-RTX.md` §7 step 2b, **an unmoved battery may NOT be cited as evidence the asm executes**) ·
`util_rtx_arm_census.sh` with `COMMITS > 0` · `test_gate_rtx_killswitch_sets.sh PLCALL` (N≥4 per arm,
hash SETS — the s217/s219 correction) · 3-arm `bench_rtx_3arm.sh` reporting **ON/PRISTINE** as the answer.

### - [ ] RUNG RTX-2-PL — the SINK-deferred arms (scope option (c) only)
Enumerated residue the SINK ladder explicitly leaves in C: SINK-4 `kk==4` (per-site intern cache),
SINK-7 out-of-2⁵³ range (the double-compare trap — `cvtsi2sd`/`comisd`, and `x86_asm.h` has only ~12 xmm
hits so **verify the encoder forms exist for BOTH media before choosing**), SINK-6 `div`/`idiv`/`mod`
guards (`b==0`, `b==−1` — `INT_MIN/−1` traps on x86) and any `DT_R`, SINK-5 non-`{I,R}` tags.
⛔ **Do not open before the §SCOPE ruling.**

### - [ ] RUNG RTX-0d-PL — extend the workload set beyond two backtracking programs
Cursor item 6: `queensn`+`queens` are ~78% of arrivals. The ranking needs list/arith/IO-shaped run-phase
workloads before any rung is prioritised **on rank alone**. ⚠ Mirrors ICON-RTX's RTX-21-ICN exactly.

### - [ ] RUNG RTX-12-PL — eradication (LAST)
Delete gate + `c_*` body. ⛔ Cross-language per ledger hard rule 4: requires **all three** watermarks
green and every beneficiary row `DONE`.

---

## ARCHITECTURE NOTE — WHY PROLOG'S SURFACE LOOKS DIFFERENT

Prolog's hot symbols are `rt_pl_dop_*`: the runtime sinks for lowered `$op` nodes emitted by
`lower_prolog.c` through the four-port (α/β/γ/ω, δ/ε) BB machine documented in `GOAL-PROLOG-BB.md`.
They are **emitted-code-only** — the compile phase never calls them (cursor item 4) — which is why
Prolog's absolute dynamic counts are already run-phase counts and why its surface is the largest of the
three languages (**112 distinct symbols** vs Icon's 90 and SNOBOL4's 54) while being almost entirely
uncontested.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
