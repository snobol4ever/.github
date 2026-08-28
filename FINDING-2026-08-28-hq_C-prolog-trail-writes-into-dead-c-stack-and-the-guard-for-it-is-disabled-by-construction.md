# FINDING — the Prolog trail writes into DEAD C-STACK, and the guard that exists to stop it is disabled by construction for exactly the programs that hit it

**Seat:** hq_C · **Date:** 2026-08-28 · **Row:** `polyglot-demo-empty-output-rc0`
**No code changed.** Tree byte-identical to `origin/main` (a temporary env-gated probe was installed for one A/B and fully reverted).

## MINIMAL WITNESS — 2 elements, deterministic, BOTH modes

```prolog
:- initialization(main, main).
whites(S0,S) :- S0=S.
whites(S0,S) :- S0=[C|S1], char_type(C,space), whites(S1,S).
word([C|Cs],S0,S) :- S0=[C|S1], char_type(C,alpha), word(Cs,S1,S).
word([],S0,S) :- S0=S.
words([],S0,S) :- whites(S0,S).
words([W|Ws],S0,S) :- whites(S0,S1), word(W,S1,S2), W \= [], words(Ws,S2,S).
main :- words(Ws,[' ',h],[]), write(Ws), nl.
```

| arm | result |
|---|---|
| `swipl` (oracle) | `[[h]]` |
| SCRIP m3 | **rc=134, `*** stack smashing detected ***`** — 6/6 runs |
| SCRIP m4 | **rc=134, same** |

⭐ **Input length is the whole ladder**, and it is sharp: `[]`, `[h]`, `[h,i]`, `[' ']`, `[h,' ']` all produce the **correct** answer. `[' ',h]` smashes the stack. `[h,' ',t]` and longer give `rt_pl_cterm: island exhausted (16777216 used)`. The trigger is a second word — i.e. the first genuine backtrack over a consumed prefix.

## ⭐⭐ TWO SUSPECTS THE ROW WAS POINTED AT ARE EXONERATED — BY MEASUREMENT, NOT BY READING

The baton's ordered step 2 was *"trace `phrase/3`'s compiled call path (`lower_prolog.c:607-620`)"*, and the prior FINDING left the DCG translator *"not ruled out by measurement, only by reading."* **Both are now ruled out by measurement.** Hand-expanding the DCG — no `-->`, no `phrase/3`, plain clauses with explicit `S0`/`S` threading — **reproduces the identical abort**:

```prolog
whites(S0,S) :- S0=S.                                      % ... etc, as above
main :- string_chars("hi there",Chars), words(Ws,Chars,[]), write(Ws), nl.
```

So the defect is in **plain clause resolution / backtracking**, reachable with no DCG machinery in the picture at all. Do not spend a session on `phrase/3` or `dcg_expand_*`.

⛔ **Also stale: seat09's `length/2` lead.** `main :- length([a,b,c], N), write(N), nl.` was reported as SIGSEGV under `--run`, correct under `--compile`. At current HEAD it prints `3`, rc=0, in **both** modes. Re-measured before use; that data point no longer reproduces and should not be chased.

## ROOT CAUSE — valgrind names it exactly

```
Invalid write of size 8
   at  pl_trail_unwind (pl_cell.h:81)
   by  dop_trail_unwind (by_name_dispatch.c:1459)
   by  dop_call_nothrow (by_name_dispatch.c:1488)
   by  rt_pl_dop_trail_unwind (by_name_dispatch.c:1564)
   by  n167_call_prolog_bx
 Address 0x1ffefef0b8 is on thread 1's stack
 1376 bytes below stack pointer
```

`pl_trail_unwind` restores `*ents[i].addr = ents[i].old` for each trail entry. **Those addresses point into C stack frames that have already been popped** — the write lands 1160–1376 bytes *below* the current `RSP`, which is why the canary in `dop_call_nothrow` dies. The trail outlives the frames whose cells it records.

## ⛔⛔ THE GUARD FOR THIS ALREADY EXISTS — AND IS TURNED OFF FOR EXACTLY THESE PROGRAMS

`pl_cell.h` has `plc_dead_cstack(p)`, whose entire purpose is *"this trail entry points into a dead C-stack frame — skip the write-back"*, and `pl_trail_unwind` consults it. Its first line is:

```c
if (!g_plw_unwind_floor) return 0;   /* -> "not dead" */
```

`g_plw_unwind_floor` is set by `dop_call*` **only when `g_plw_floor_bypass` is 0**. And the driver sets that bypass to **1** for precisely this program class — `src/driver/scrip.c:1811` (m3) and `:1386` (m4, emitting `call rt_plw_floor_bypass_on@PLT`), both gated on `is_prolog && bbg->zframe_graph && !bbg->icn_cells_graph`.

⭐ **So the floor is never set, the guard's first line always answers "not dead", and every dead-stack write-back proceeds unchecked.** The protection and the programs that need it are mutually exclusive by construction. A reader auditing `pl_trail_unwind` sees a guarded write and moves on; the guard is real, reached, and inert.

## ⛔ AND FORCING THE FLOOR ON IS **NOT** THE CURE — MEASURED, BOTH DIRECTIONS

A/B via a temporary env-gated probe (installed, measured, reverted):

| witness | bypass ON (shipped) | floor FORCED |
|---|---|---|
| `[' ',h]` | rc=134 stack smash | **rc=1, no output** (oracle: `[[h]]`) |
| `[h,' ',t]`, 8-char, full demo | island exhausted | island exhausted, unchanged |

**Enabling the guard trades memory corruption for a WRONG ANSWER**, and does nothing for the exhaustion. That is the tell: the floor heuristic is a false dichotomy over a defect that is upstream of it. **Prolog cells reachable from the trail must not live in C stack frames that die before the choice point that references them.** Whichever way the guard is set, one of the two arms is wrong — so the fix is cell lifetime, not the predicate.

⛔ **Do not "fix" this by raising the 16MB `rt_pl_cterm` island ceiling.** The exhaustion is the same lifetime defect wearing its other face — an 8-character input cannot legitimately need 16MB.

## KIN — three seats are circling this neighbourhood from different sides
`ζ-SPINE lives on RSP`, and every symptom here is a C-stack-lifetime symptom. Worth connecting before anyone re-derives it:
- **seat07** — `pascal-m4-for-spine-leak-64b-per-iter`, 64 bytes/iteration of ζ-SPINE accounting, three mechanisms independently retired.
- **seat02** — `pascal-relop-*`, `zd_plan` walks only the γ edge so a `BINOP_TEST`'s ω arm is emitted under a *different addressing convention*; gdb-measured `zd_on=0` vs `1` and a live 272-byte `rsp` discrepancy.
- **seat10** — `m4-pie-vs-no-pie`, `RSP == 0x0` at fault under `-no-pie` at a program point where PIE has a valid stack address.

## ⭐⭐ THE PUSHING SITE IS NAMED: `plw_bind`, `by_name_dispatch.c:123` — ALL 217 OF THEM

Instrumented `pl_trail_push` to report every trail entry whose address lies on the live stack, with
`__builtin_return_address(0)` resolved through `dladdr` + `addr2line`. On the 2-element witness:
**217 stack-cell pushes, from exactly ONE return address**, `libscrip_rt.so+0x43feda` →

```
plw_bind
/home/claude_C/SCRIP/src/runtime/by_name_dispatch.c:123
```

```c
static void plw_bind(DESCR_t *cell, DESCR_t word) { pl_trail_push(&g_pl_trail, cell); *cell = word; }
```

It trails whatever cell it is handed, with no test of where that cell lives.

⭐ **AND THE DISCIPLINE THAT WOULD FIX IT ALREADY EXISTS TWO LINES BELOW, applied to only one of the
three arms.** In `plw_unify_cells` (`:126`), the **var-var** case is already stack-aware:

| arm | line | what it does | trails a doomed stack cell? |
|---|---|---|---|
| var-var, both above the current frame | `:131-137` | **VVB**: age-orders them — binds the lower-addressed (younger) at the higher (older), so the binding dies with the younger. Killswitch `SCRIP_NO_VVB`. | no — correct by construction |
| var-var, otherwise | `:137` | allocates a **heap join cell** (`rt_plj_alloc`) and points both at it | no — heap outlives both |
| **`if (av) plw_bind(A, *B)` / `if (bv) plw_bind(B, *A)`** | **`:138-139`** | **binds a variable cell to a value with no location test at all** | ⛔ **yes — this is the leak** |

So the var-**nonvar** arms are the unguarded ones, and both precedents for fixing them (age ordering,
and heap-join indirection) are already in the same function, already shipped, already killswitched.

## NEXT STEP FOR WHOEVER TAKES IT
The site is named above. The question is now a **design** one, not a search: make `plw_unify_cells`'s var-nonvar arms (`:138-139`) as location-aware as its var-var arm already is — either by refusing to trail a cell that will not outlive the choice point, or by routing the binding through a heap cell the way `:137` already does. ⛔ Whatever the shape, grade it against the **wrong-answer** arm too, not just the crash: forcing the existing floor guard on removes the smash and returns `rc=1` with no output. A cure that only stops the abort has not fixed anything.
