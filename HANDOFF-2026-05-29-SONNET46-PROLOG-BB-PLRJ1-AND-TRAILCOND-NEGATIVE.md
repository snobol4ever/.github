# HANDOFF — Prolog BB — PLR-J-1 landed + PL-TRAIL-COND verified-unsound negative result

**Author:** Claude Sonnet 4.6 · **Date:** 2026-05-29
**Goal:** `GOAL-PROLOG-BB.md`
**one4all HEAD at handoff:** `40c17ecb`
**.github HEAD at handoff:** `08322f7a`

---

## What landed (in order)

### 1. PLR-J-1 — CAT-D-10 type-test builtins MEDIUM_BINARY arm (one4all `efbdd61c`)

`src/emitter/BB_templates/bb_builtin.cpp` CAT-D-10 (`var/nonvar/atom/integer/float/number/
compound/atomic/callable/is_list/ground`) had a MEDIUM_TEXT arm only; in MEDIUM_BINARY the asm
strings emitted as raw bytes, so native `--run` had `atom(42)` / `integer(hello)` falsely
succeed. Ported the scalar path to raw bytes: `movabs rax,&rt_pl_type_test; call rax` with SysV
`rdi=fn rsi=k0 rdx=i0 rcx=s0`; `test eax; je ω; jmp γ; β→ω` (identical shape to the M3-PL-NOINTERP-1e
comparison arm). BB_PL_STRUCT compound-literal arg returns the double-no-op honest-abort
(deferred to PLR-J-3). Added one extern decl for `rt_pl_type_test`.

**Verified:** `rung09` type-test sub-lines now `yes/yes/no/no`, byte-matching mode-2.
(`functor/arg/=..` lines still fail — they need PLR-J-3 — so rung09 stays FAIL overall but is
provably closer; verify the type-test sub-lines directly, not the whole-program diff.)
FACT 0, GATE-3 m2 104/107, GATE-SWI 57/57, smokes 5/5/5/13, mode-3 crosscheck unchanged 10/132.

### 2. Engine feature-parity study vs gprolog + SWI (one4all `c7529bad`)

`doc/PROLOG-FEATURE-COMPARISON-2026-05-29-SONNET.md` — line-by-line read of GNU Prolog
(`gprolog-master/src/EnginePl/wam_inst.h`, `Pl2Wam/indexing.pl`) and SWI-Prolog
(`swipl-devel-master/src/pl-incl.h`, `pl-index.c`) against SCRIP's engine. Found three candidate
divergences; converted to rung families PL-TRAIL-COND, PL-INDEX-L2, PL-CP-FRAME in
GOAL-PROLOG-BB.md → `PL-ENGINE-PARITY`. Fleshed `ARCH-PROLOG.md` from a 3-line stub to an
engine-model + parity-gap reference.

### 3. PL-TRAIL-COND — tried, VERIFIED UNSOUND, reverted (one4all `40c17ecb`, doc only)

Implemented conditional trailing exactly as gprolog/SWI do (Term `birth_stamp`, monotonic
`g_pl_var_stamp`, HB register `g_pl_hb_stamp` snapshotted into `pl_choice` on push, restored on
pop/truncate, `bind()` skipping the trail push when `var->birth_stamp > g_pl_hb_stamp`).

**It broke backtracking.** GATE-3 dropped 104→102: `rung05_backtrack_backtrack` (recursive
`member/2` over `[a,b,c]`) yielded only `a`; `rung11_findall_findall_arith` collected only `[1]`
instead of `[1,4,9]`. **Reverted in full** (all six touched files `git checkout`-ed); rebuilt and
re-confirmed 104/107.

**Root cause (architectural finding):** the WAM conditional-trail optimization presupposes a
SECOND binding-undo mechanism — heap-segment reclamation. In a real WAM, backtracking resets the
heap pointer H to the CP's HB, physically discarding every cell (and binding) allocated after the
CP, so those bindings need not be trailed. SCRIP's boxed GC model has NO such mechanism:
`trail_unwind(mark)` is the SOLE way a binding is undone, and term cells are never reclaimed on
backtrack (GC owns lifetime). Therefore EVERY mutable binding must be trailed; skipping a "young"
one leaves it bound across the backtrack — exactly the bindings inside a recursive body that must
reset for the next alternative. The `birth_stamp > HB` test correctly identifies young vars, but
in our model young ≠ reclaimed-on-backtrack, so the skip is unsound. Closed as won't-fix-as-designed;
only viable after a (large, unmotivated) per-CP heap-reclamation substrate exists.

Full analysis + precondition: `doc/PROLOG-FEATURE-COMPARISON-2026-05-29-SONNET.md`.
The code change was tried and fully reverted, so NO engine source differs from baseline; only the
doc was committed. FACT 0.

---

## Verified state at handoff

| Gate | Result |
|---|---|
| GATE-3 (Prolog interp, mode-2) | 104/107 (3 pre-existing FAILs: rung15, rung27, rung30_pushback) |
| GATE-SWI (mode-2) | 57/57 |
| mode-3 native crosscheck | 10 PASS / 122 FAIL (unchanged; PLR-J ladder is the path) |
| smokes prolog/icon/raku/snobol4 | 5/5/5/13 |
| FACT (templated-bytes-outside-templates) | 0 |
| Build | green |

---

## NEXT

**PL-ENGINE-PARITY family status after this session:**
- PL-TRAIL-COND ⛔ CLOSED (verified unsound; needs heap reclamation first — unmotivated).
- PL-CP-FRAME-0 — moot (HB had no other consumer once PL-TRAIL-COND closed).
- PL-INDEX-L2-1 — still open BUT: assessed this session as not changing any current pass/fail
  (largest single corpus predicate is modest, ~8-12 clauses, so O(1) vs O(N) selection is an
  internal scan-count win only). Worth doing only if a many-fact benchmark motivates it; would be
  byte-identical mode-2 output with a reduced candidate-scan counter. Lower priority than the
  PLR-J ladder.

**Recommended actual next work: the PLR-J ladder** (`GOAL-PROLOG-BB.md → PLR-J`, the active
CURRENT-NEXT-STEPS section) — it directly attacks the 122 open mode-3 native failures.
PLR-J-1 is done. **PLR-J-2** (explicit per-node resume, replacing the β heuristic; transliterates
irgen.icn `ir_a_Binop`/`ir_a_Mutual`/`ir_a_Call`) is the next structural step; or **PLR-J-3**
(compound-term builder in raw bytes — unblocks rung03 + rung09's functor/arg/=.. lines + compound
unify). Develop and verify against mode-2 (the correctness reference) throughout.

---

## Lessons for next session

1. **The boxed GC model is NOT a WAM heap.** Any WAM optimization that relies on heap-stack
   reclamation discipline (conditional trailing, environment trimming on the stack, last-call heap
   trim) must be checked against the fact that SCRIP never reclaims term cells on backtrack — the
   trail is the only undo. Pre-screen such ports for this precondition before implementing.
2. **An escape probe that passes is not a soundness proof.** The `X=f(Y)` probe passed but missed
   the recursive-CP-reuse case that actually broke. When porting a backtracking-semantics change,
   the gate test (recursive member, findall) is the real proof, not a hand-built single-level probe.
