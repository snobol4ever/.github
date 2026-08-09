# FINDING 2026-08-09 (s14, Claude Opus) — PL-ZK-5B OPTION A AS IMPLEMENTED IS A 6→0 REGRESSION, AND THE TREE ARRIVED PRE-STAGED

**Goal:** `GOAL-PL-ZETA-CELLS.md` · **SCRIP HEAD:** `ada979eb` · **Build:** -O0, TIMEOUT=6s, bench-22 board (`scripts/test_bench_prolog_modes.sh`)

## 0. THE LAND MINE FIRST — THE WORKING TREE WAS NOT CLEAN AT SESSION OPEN AND I DID NOT WRITE ITS CONTENTS

`/home/claude/SCRIP` existed in the container before this session cloned anything. It sat at `ada979eb` with **three uncommitted modified files**: `src/emitter/emit.cpp`, `src/runtime/rt/rt.c`, `src/templates/bb_var_ref.cpp`. The diff was a complete implementation of PL-ZK-5B **Option A**, with comments already self-labelled `PL-ZK-5B OPTION A (s14)` — i.e. attributed to the session that had not yet run.

**I did not author those edits.** I found them, built them, and measured them. Recording this plainly because this repo has been bitten by exactly this class before (`FINDING-2026-07-29-CLAUDE-SN4-RTX-8-SLICE4-S217-...-I-TWICE-READ-A-WORKING-TREE-AS-ORIGIN.md`). A pre-staged tree that names itself after the current session is the strongest possible invitation to report someone else's uncommitted code as this session's landing.

**Procedural correction for the session-start checklist:** `git status --short` on every repo BEFORE the first build, and treat a dirty tree at open as an unattributed artifact — measure it, never adopt it. `PLAN.md` step 8 sends you straight to the goal file's setup scripts; it never tells you to check whether the tree you inherited is clean.

## 1. THE MEASUREMENT — CLEAN HEAD IS PARITY; THE PATCH IS A CRATER

All four runs at `ada979eb`, -O0, TIMEOUT=6s, `green` = m3 AND m4 both correct out of 22.

| tree | arm | green | broken |
|---|---|---|---|
| **clean `ada979eb`** | `SCRIP_PL_CELLS=0` | **6** | 16 |
| **clean `ada979eb`** | `SCRIP_PL_CELLS=1` | **6** | 16 |
| + Option A patch | `SCRIP_PL_CELLS=1` | **0** | 22 |
| + Option A patch | `SCRIP_PL_CELLS=1 SCRIP_ZD_PL_VR=0` | **5** | 17 |

**Two independent facts fall out:**

**(a) s13's parity claim is CONFIRMED at this HEAD.** cells=1 == cells=0 == green=6. The s13 cursor said "bench-22 cells=1 == cells=0 baseline green=6" and it reproduces exactly. s13's separate note that a parallel session's `qsort/m4` regression had knocked cells=1 to green=5 no longer reproduces — that has been repaired by a parallel seat between `069c2fd8` and `ada979eb`.

**(b) The patch is falsified twice over.** With VAR_REF admitted: **green 6 → 0**, every program on the board. With the documented killswitch `SCRIP_ZD_PL_VR=0` thrown: **green 6 → 5**, still down one.

## 2. ⛔ KILLSWITCH-COMPLETENESS DEFECT — THE RUNTIME HALF IS NOT COVERED BY THE KILLSWITCH

Fact (b) is the more important half. `SCRIP_ZD_PL_VR=0` disables VAR_REF **admission** in `zd_wl_kind` — an emitter-side gate. But Option A's third edit is in `rt_jmp_frame_lexprep2` (`src/runtime/rt/rt.c`), and that loop fires **unconditionally on every Prolog lex frame**, killswitch or no killswitch. So the rung's `=0` byte-identity obligation (RUNGS preamble: *"each: own commit, killswitch, `=0` byte-identity"*) is **not satisfiable as written** — there is no `=0` position from which the runtime seeding disappears.

**RULE CANDIDATE for `GOAL-PL-ZETA-CELLS.md` COORDINATION:** a rung that lands both an emitter arm and a runtime arm needs the killswitch read at the **runtime** site too, or one env var that both sites consult. An emitter-only killswitch silently under-covers any rung with a runtime half — and every future `=0` byte-identity proof for that rung is vacuous.

## 3. WITNESS — `app/3` REGRESSES, AND IT ALREADY PASSED WITHOUT THE RUNG

```prolog
app([],L,L).
app([H|T],L,[H|R]) :- app(T,L,R).
main :- app([a,b],[c],R), write(R), nl.
```

| tree | cells=0 | cells=1 |
|---|---|---|
| clean `ada979eb` | `[a,b,c]` | `[a,b,c]` |
| + Option A patch | `[a,b,c]` | *(empty output)* |

⭐ **CORRECTION OF RECORD FOR THE s13 CURSOR.** s13's NEXT SESSION PROTOCOL step (4) reads: *"Verify `app([a,b],[c],R)→[a,b,c]`, `nrev`, `fib` with VR enabled."* **`app/3` already passes on the cells arm at clean HEAD with VR disabled.** It therefore cannot discriminate the VAR_REF work in either direction — it is green before the rung starts and it is the first casualty when the rung lands. It is a **regression detector**, not an acceptance witness. The rung still has no witness that goes red-without / green-with; ZK-5B needs one before any further attempt, or the next session will again be unable to tell progress from parity.

`two.pl` (two-clause `foo(0)`/`foo(X):-X>0`) prints `pos` correctly on all four configurations and discriminates nothing.

## 4. ROOT-CAUSE HYPOTHESIS — NOT PROVEN, STATED AS A HYPOTHESIS

The runtime edit promotes a param slot to a fresh self-referential `DT_PLVAR` heap cell **when `_s->v == DT_SNUL`**:

```c
if (_s->v == DT_SNUL) { ... _s->v = DT_PLVAR; _s->slen = 0; _s->p = (void *)_j; }
```

`src/contracts/descr.h` pins `DT_SNUL == 0` and says so in block capitals: *"DT_SNUL == 0 IS PINNED AND LOAD-BEARING. Zeroed memory is a valid null string."* So `v == DT_SNUL` **cannot distinguish "slot never bound" from "slot legitimately holds the null string / a zeroed descriptor."** The loop runs over `[0, nparams)` unconditionally, not over `[nargs, nparams)`, so a slot that `rt_frame_bind_args` has just filled with a real argument whose descriptor reads zero is clobbered into a fresh unbound variable.

That is the shape that produces `app([a,b],[c],R)` → empty: the list argument is replaced by an unbound var, `$ix_g` then selects the wrong clause, and the recursion yields nothing. **This was not confirmed under gdb — no monitor run, no single-step.** Per `RULES.md` MONITOR-FIRST, the next session must not act on this paragraph as if it were a diagnosis; it is a reading of the source and it names where to point the 2-way sync-step monitor first.

**If the hypothesis holds, the minimal repair is the bound, not the tag:** seed only `[nargs, nparams)` — the slots `rt_frame_bind_args` provably did not write — and never test `DT_SNUL` as an "unset" sentinel anywhere, because `descr.h` forbids that reading globally.

## 5. WHAT WAS AND WAS NOT LANDED

- **SCRIP: nothing committed. Tree returned to clean `ada979eb`.** Publishing a green→0 board as a rung landing would violate `RULES.md` ("Run goal's gate before every commit. No broken commits.").
- The falsified diff is preserved verbatim at `.github/WIP-2026-08-09-PL-ZK-5B-option-A-FALSIFIED.patch` so the next session can re-apply, instrument, and repair it rather than re-derive it.
- Option A **as a design** is not disproven by this session. What is disproven is **this implementation** of it: one seeding site, one tag test, one uncovered killswitch. The design question Lon was asked to rule on (A vs B) remains open and the ruling is unchanged by this result.

## 6. UNRELATED-BUT-MEASURED

`gprolog-master`'s engine is WAM-compiled-to-C with no readable choice-point/trail header; it is a poor canonical reference for this ladder. `swipl-devel-master` is the better one: `src/pl-incl.h:1657` `struct mark { trailtop; globaltop; saved_bar; }` and `src/pl-wam.c:1540 __do_undo(const mark *m)` confirm that a trail mark is a **trail-stack-top snapshot** and that undo is a pointer-walk back to it — which is precisely the contract `$trail_mark` / `pl_trail_unwind` implement, and it validates the ZK-4 decision to keep the mark frame-independent.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
