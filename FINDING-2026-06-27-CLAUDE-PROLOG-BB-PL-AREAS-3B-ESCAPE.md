# FINDING — PL-AREAS-3b deterministic-pop is unsound before PL-AREAS-4 (the escape problem)

**Session:** 2026-06-27 · Claude (3rd dev) · GOAL-PROLOG-BB · PL-AREAS-3b attempt
**Outcome:** implemented det-pop for bounded calls → passed fib + 115 rungs + 21/22 bench → **deriv corrupted** → root-caused to the escape problem → **reverted to green baseline. Nothing committed.**

---

## 1. What was attempted

PL-AREAS-3b as the goal file scopes it: the live E-area switch, deterministic-POP for bounded calls.
The mechanism (saved at `/home/claude/.github/pl-areas-3b-detpop-WIP.patch`, 3 files, +37/-5):

- **`src/runtime/unification.c`** — new `void *rt_e_enter(int nslots)`: bumps `8 + 16*(nslots>0?nslots:1)` off `g_pl_env_area` (the same size formula as `rt_enter`) and returns it. **No caller slot, no `if(!*slot)` cache** — a bounded call has its resume β elided (PL-BB-1), so the frame is never re-read; the cache only ever skipped the GC_malloc cost and would dangle a stale pointer once E is reset (the documented #1 corruption trap).
- **`src/runtime/rt/rt.h`** — declared `rt_e_enter`.
- **`src/emitter/BB_templates/bb_cell_call.cpp`** — split the α body on `_.op_bounded`:
  - **bounded:** `rt_e_mark` → stash mark in the (now-unused) call-slot cell `FR(GZ_CELL_OFF(ival[0]))` → `mov edi,nslots; rt_e_enter` (note: `rt_e_enter`/`rt_e_reset` take the int arg in **edi**, unlike `rt_enter` which takes nslots in **esi**) → shared arg setup → call → `def L(0)`; then **reset E on both return edges** after consuming `eax`: `test eax; je L(1); <reset>; jmp γ; def L(1); <reset>; jmp ω`. Uses label `L(1)` (free for the call box; only `L(0)` was used).
  - **non-bounded:** unchanged (`rt_enter` + GC cache + `jne γ/jmp ω` + `def β` resume).

This is the documented design (STATE "Next" + line 47/48 touch points). The mechanism itself is correct; the problem is the layer beneath it.

---

## 2. What passed

- Clean build (scrip + libscrip_rt). `g_pl_env_area` already allowlisted (PL-AREAS-3a).
- **smoke 5/5** m2+m3+m4.
- **rung suite 115/115** m2+m3+m4 — the full soundness suite did **not** catch this.
- **bench 21/22** green.
- fib: all 3 call sites became bounded (`rt_enter@PLT` → 0, replaced by `rt_e_*`), output **10946** correct (m3 + m4). fib is the deterministic-pop target and it worked.

## 3. What broke

**`deriv`** (symbolic differentiation, every clause cut → det → bounded). m3 + m4 FAIL, interp (m2) **ok**. Output:
```
(_G2+_G3)*((x^2+2)*(x^3+3))+(x+1)*((_G2+_G3)...   <- unbound vars where bound values belong
```
The m2-vs-m3/m4 split isolates the cause to the E-area det-pop (interp uses no E-area).

---

## 4. Root cause — the escape problem (confirmed, minimal repro)

> Det-pop reclaims a bounded callee's frame at γ, but **output terms carry logic vars resident in that frame**. When sibling/subsequent bounded calls **reuse** the popped memory, the escaped vars are corrupted.

deriv's recursive clause is `d(U+V,X,DU+DV) :- !, d(U,X,DU), d(V,X,DV)`. The head builds the output compound `DU+DV` with `DU,DV` as **frame-resident** head vars. `d(U,X,DU)` binds `DU` (escaping into the caller's result), its frames pop, then `d(V,X,DV)` **reuses that popped memory** while `DU` is still referenced → `DU`'s subtree corrupts to unbound vars.

Minimal repro (`/tmp/escape2.pl`, reproducible):
```prolog
:- initialization(main).
main :- d(t(t(l,l),t(l,l)), R), write(R), nl.
d(t(A,B), p(DA,DB)) :- !, d(A,DA), d(B,DB).
d(l, leaf) :- !.
```
m3 + m4 both print `p(p(_G2,_G3),p(leaf,leaf))` (expected `p(p(leaf,leaf),p(leaf,leaf))`). The **first** subtree (`DA`) is corrupted — its frames were popped then reused by `d(B,DB)`; the **last-computed** subtree (`DB`) is intact (no subsequent reuse). Same `_G2/_G3` signature as deriv.

### Why the floor's other programs passed (the three cases)
- **fib** — output is a **ground scalar** (`F is F1+F2`). Nothing escapes the frame. Safe.
- **queens** — its only bounded predicate is `range/3`, which **escapes** a list whose tail vars live in range's frames — but `range` runs to completion *before* the search, and the search (`sel/3`, `queens/3`, `not_attack`) is **non-bounded → GC frames**, so range's popped E-area memory is **never reused**. The dangling refs read intact memory. Accidentally correct.
- **deriv** — **escapes AND reuses** (all-bounded binary recursion). Corruption.

The hazard requires *escape* (a frame-resident var referenced by the caller's result) **and** *reuse* of the popped memory before the result is read. The 115-rung suite happens to contain neither in combination; deriv does.

---

## 5. Consequence for the ladder

**A general det-pop is unsound before the heap-area + globalization of PL-AREAS-4.** This reorders the goal file's sequencing (which lists 3b det-pop ahead of 4). Two viable paths:

1. **PL-AREAS-4 first** (heap area / R13 + escape-copy or globalization): output structure cells and escaping vars live on the H-area, not the frame, so frame reclamation is safe. Then revive the WIP patch as-is. *(Preferred — this is the WAM-correct foundation; it also unblocks queens' real win, since the search frames could then be E-area + backtrack-reset.)*
2. **Gated det-pop**: introduce a flag **separate from `op_bounded`** (e.g. `op_pop_safe`) that is set only when the predicate's output is provably ground (no head-output position carries a var bound in the body to non-ground structure). Pop only when `op_pop_safe`. Keeps the fib-class win; skips deriv. **Must be a distinct flag** — `op_bounded` also drives the shipped β-elision (PL-BB-1), which must not change. The ground-output analysis is essentially a slice of PL-AREAS-4's escape analysis, so path 1 likely subsumes it.

Note also the **trail-coupling** sub-finding (analysed but *not* the cause here): a succeeded bounded call popped while an **outer choice** is live leaves dangling trail entries; this is memory-safe only if every spanning choice also resets E (backtrack-reset). The floor didn't exercise it (the escape problem fired first), but it is a second prerequisite for det-pop nested inside choices, and reinforces that det-pop and backtrack-reset are correctness-coupled.

---

## 6. Tree state

- **Reverted** `bb_cell_call.cpp`, `rt.h`, `unification.c` via `git checkout` → clean working tree.
- Rebuilt; **floor green: smoke 5/5, rung 115/115, bench 22/0/0** (all m2+m3+m4).
- **Nothing committed.** WIP mechanism preserved at `pl-areas-3b-detpop-WIP.patch` for revival after PL-AREAS-4 (or behind an `op_pop_safe` gate).
- No structural-gate regressions (the revert removed all new wiring; `g_pl_env_area` allowlist is pre-existing PL-AREAS-3a).
