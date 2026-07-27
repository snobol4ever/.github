# FINDING — s188 (2026-07-27): FLATDISP LANDED, RSP IS THE FRAME BASE; AND THE FC GATE WAS COUNTING A SUBSET

**Session:** s188 · **Goal:** `GOAL-SNOBOL4-BB.md` · **Repo:** SCRIP (`x86_asm.h`) + corpus/SCRIP `.s` artifacts
**Directive (Lon, this session):** *"Remove usage of EVERY RBP reference possible... Do ALL of them at the SAME time. It is ONE function that calculates the offsets. ALL (99.999%) of operand accesses will use RSP... It is calculated based on the known sequence of BB's."*
**Ruling (Lon, on the 3 regressions):** *"Keep you change that made RSP the default. I do not care about 3 programs failing."* — RSP default LANDED with the 3 known-bad named below.

---

## HEADLINE 1 — THE INSTRUMENT WAS MEASURING A SUBSET, WHICH IS WHY THIS NEVER CONVERGED

`test_gate_fc_no_residual_rbp.sh` reports residual-rbp **0**, and s185 recorded `FC_BASELINE 13006 -> 0`.
Direct measurement of emitted code says otherwise: **2,951 `rbp` references across the 16 SNOBOL4 benchmark
programs.**

The gap is `x86_fc_hit`'s own classification (x86_asm.h:307). It counts a miss ONLY for `OWN + full-cell`
(`defect = own && fullcell`). The other two classes it names — `CROSS` (neighbour reads) and
`OWN + window-only` (HEAD's post-unwind FLAT fields) — are scored correct-by-design and **still emit
`[rbp+N]`**. So the gate answers *"did a granted box miss its own window?"* while every session has been
reading it as *"is rbp gone?"*. Those are different questions and the second one was never being asked.

⚠ **THIS IS THE SAME SHAPE AS s184's FC-GATE DEFECT** (the gate that was measuring wall-clock patience).
Twice now the FC instrument has reported convergence that the emitted bytes contradict. **RULE OF THUMB
EARNED TWICE: when a gate says 0 and the ladder has not moved for several sessions, sweep the COMPILER
OUTPUT, not the gate.** (s184 wrote the same sentence about artifacts; it generalizes to gates.)

MEASUREMENT COMMAND (deterministic, no script needed — this is the honest number):
```
for f in corpus/benchmarks/snobol4/*.sno; do ./scrip --compile "$f" | grep -c rbp; done
```

---

## HEADLINE 2 — THE ONE OFFSET FUNCTION EXISTS; RSP IS NOW THE FRAME BASE

Lon's design was already latent in the tree and correct. The whole frame-addressing surface funnels through
exactly FOUR sites, so ONE function suffices — no per-kind whitelist, no "too far" cases:

```c
#ifndef ZC_FLATDISP
#define ZC_FLATDISP 1        /* build constant, NOT env — the compile-time-only frame law holds */
#endif
inline int x86_flatdisp_on() { return ZC_FLATDISP && ZC_FRAME == ZC_FRAME_RSP; }
inline int x86_frame_off(int off) { return x86_flatdisp_on() ? off + (int)_.op_flat_disp : off; }
```

**Sole consumers (nothing else may add a frame displacement):**
1. `x86_r12_modrm(regfield, off)` — BINARY modrm. Compensation applied **before** the mod/disp-width choice,
   or a depth-shifted ref silently picks the wrong encoding length.
2. `x86_frame_text_mem(off)` — TEXT spelling. Same function, so **R10 (BINARY agrees with TEXT) holds by
   construction** rather than by review.
3. `FR(off)` — 32-bit operand spelling, fallback path only (the `fc_hit` granted-window path already rebases
   to the *current* rsp via `off - op_fc_base` and must NOT be double-compensated).
4. `FRQ(off)` — 64-bit twin.

`x86_fb()` -> `"rsp"`, `x86_fb_num()` -> `4`, and the fr32/fr64 prefixes -> `[rsp + ` under the gate. The rbp
arm survives ONLY as the `-DZC_FLATDISP=0` A/B control.

### Why D = 0 is EXACT, not a fallback
`xa_flat.cpp` seeds the activation as `sub rsp, K_total` then `mov rbp, rsp`. **At the seed, rsp == rbp.** A
statement that pushes no FORTH cell leaves rsp there, so `[rsp+off]` and `[rbp+off]` are the same address.
That identity is what makes 89% of the conversion free.

---

## MEASURED

| build | rbp refs (16 benchmarks) | programs running clean |
|---|---|---|
| baseline (`ZC_FLATDISP=0`) | 2,951 | 15/16 |
| **RSP default (`ZC_FLATDISP=1`)** | **323 (-89%)** | 12/16 |

**The refactor is byte-neutral with the gate off** — rebuilt at `ZC_FLATDISP=0` and re-measured: 2,951 -> 2,951
exactly. So the routing itself is proven not to change codegen; only the flip does.

`.s` artifacts regenerated all three sweeps (benchmark / feature / demo). Net across demo: 41,693 insertions
vs 241,754 deletions — the rsp forms are materially shorter than the rbp forms they replace.

⚠ **BUILD TRAP THAT COST A FALSE MEASUREMENT THIS SESSION:** `make` does **NOT** track `x86_asm.h` as a
dependency. The first post-edit measurement read 2,951 (i.e. unchanged) purely because **zero** object files
had been rebuilt. Confirm with `find . -name '*.o' -newer src/templates/x86_asm.h | wc -l` — if that is not
0, you are measuring a stale binary. **Always `touch src/templates/*.cpp src/emitter/*.cpp` after editing
`x86_asm.h`.**

---

## THE REMAINING BLOCKER IS ONE LINE, AND IT IS NOT A DESIGN PROBLEM

Lon's premise — *"calculated based on the known sequence of BB's"* — is not merely right, it is **already
implemented**: `fc_leaf_walk()` (`lower_snobol4.c:1038`) is exactly that prefix sum. It walks the graph in
allocation order (== flow order on a linear spine), accumulates `pfx` per granted cell, registers each node's
static rsp->flat distance, and handles `ALTERNATE` by the S10d pad-to-max law (`fc_alt_fpmax`) so every arm
yields at a uniform depth. That machinery is correct and needs no redesign.

It is simply **called on one range only** (`lower_snobol4.c:1756`):
```c
if (fc_lin) fc_leaf_walk(g, before_pat, g->n, 32);
```
Pattern nodes inside a granted statement get a real depth; **every other node in the program gets
`op_flat_disp = 0`.** Where 0 is true (no cell pushed) the flip is exact. Where cells ARE pushed outside that
range — the ZB-VAL value-spine grants (`fc_vlit_active`: `IR_LIT_*` / `IR_VAR`) are the live example, since
`fc_geom` grants them a 16-byte cell but `fc_leaf_walk` never visits them — the address is wrong by the carve
depth. The file's own comment already conceded this: *"a declined statement has no static depth ... its
emission stays on the flat path, honestly broken under RSP."*

### KNOWN-BAD, ACCEPTED BY DIRECTIVE (do not re-litigate; fix by the rung below)
- `mixed_workload` — SIGSEGV (139) · passes at baseline
- `pattern_bt` — SIGSEGV (139) · passes at baseline
- `string_pattern` — SIGSEGV (139) · passes at baseline
- `eval_dynamic` — timeout (124) **PRE-EXISTING**, fails identically at baseline; NOT caused by this rung

---

## NEXT RUNGS (in order)

1. **FLATDISP-2 — UNIVERSAL DEPTH WALK.** Call `fc_leaf_walk` over the whole graph with a **per-statement
   reset** at the S10e unwind boundary (cells are suspended at gamma and released per statement, so a single
   running `pfx` across statements over-counts). Register it **AFTER** the existing pattern-range call:
   `fc_leaf_disp` returns the FIRST match, so the proven pattern entries win and the universal pass only
   fills gaps. This is the rung that retires the 3 known-bad above.
2. **FLATDISP-3 — DELETE THE DEAD SEED MACHINERY.** With rsp as the base, `xa_flat.cpp`'s
   `mov rbp,rsp` / `push rbp` / `mov [rsp+N],rbp` / `mov rbp,[rsp+N]` / `lea rsp,[rbp+N]` seed-save-restore
   set is pure overhead. Roughly half the 323 residue.
3. **FLATDISP-4 — FUNNEL VIOLATIONS.** The other half: hand-spelled `[rbp + N]` in templates that bypass
   `FR`/`FRQ`/`x86_frame_text_mem` (`mov rax,[rbp+N]`, `cmp qword ptr [rbp+N]`, `lea rdx,[rbp+N]`,
   `mov rbp,qword ptr [rax+N]`). Each is a TEMPLATE-ONLY-EMISSION violation in spirit — route through the
   funnel, do not re-spell.
4. **FIX THE GATE ITSELF.** `test_gate_fc_no_residual_rbp.sh` should ratchet on the *compiler-output* rbp
   count (the one-liner above), not on `x86_fc_hit`'s own-window classification. A gate that cannot see
   2,951 refs is not a gate.
