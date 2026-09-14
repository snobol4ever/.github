# FINDING 2026-09-13 hq_R — the findall/4 tail divergence is the DYNAMIC meta-call, not the static one; a static-only gate is a false green for it, and my first gate was exactly that

**Row:** `prolog-a-construct-has-two-lowerings-and-the-meta-call-path-stages-arguments-differently` (owner cto, dispatched to hq_R).
**Tree:** cut on SCRIP `0f7e2b8df` and RE-PROVEN in full on the merged tree `c4e64b21f` after origin moved under it; landed as SCRIP `301440bbb`, corpus `89d25a4c3`. Incremental `make`, `RT_OPT` as the Makefile carries it (`-O0`).

## THE ROW NAMED A REAL DIVERGENCE AND POINTED AT THE WRONG HALF OF `call/1`

The row's witness pair is `static.pl` (fourth argument `T`, a variable) against `meta.pl`
(`call((findall(X,(X=1;X=2),S,[3]), write(s(S)), nl))`). It attributes the whole difference to the meta path. The first
thing to measure is whether that witness pair can carry the claim, and it cannot:

```
--dump-ir meta.pl,   term_e vs term_lval_e ...... BYTE-IDENTICAL (diff -q, 2618 lines)
--dump-ir static.pl, term_e vs term_lval_e ......  1 line of 2639:
    47c47
    <   23   24   45@  VAR       [] var="G3"
    ---
    >   23   24   45@  VAR_REF   []
```

`term_lval_e` (`src/lower/lower_prolog.c:174`) is `term_e` plus ONE arm: `if (t->t == TT_VAR) return IR_VAR_REF`. The
meta witness's fourth argument is `[3]`, a list literal, so the flip cannot reach it. **`call/1` on a LITERAL goal is
not a second machine at all** — `lower_prolog.c:1104-1123` collects the conjunction and lowers it through the same
`pl_lower_conj` a clause body uses, which is why the IR is identical to the byte.

⭐ But the symptom the row reported — a tail that spells itself `nl`, the last goal of the conjunction — **is real, and
I reproduced it.** It needs the goal to be meta-called **through a VARIABLE**, the `pl_meta_call_dyn` path
(`lower_prolog.c:1108`), which the row's witness never exercised:

```prolog
run(G) :- call(G).                     U = [9], run((findall(Y,(Y=1;Y=2),S,U), write(dyn_call(S)), nl))
runc(G) :- catch(G,_,true).            ... runc((findall(...S,U), write(dyn_catch(S)), nl))
                                       ... G4 = (findall(...S,U), write(dyn_var(S)), nl), call(G4)
```

All three print `[1,2|nl]` for the oracle's `[1,2,9]`. Every static shape — direct, `call((literal))`, `->`, `catch` on
a literal, a clause argument — prints the correct answer on the same tree. **So the row's sentence is right and its
witness is wrong: there ARE two lowerings, and they are STATIC vs DYNAMIC meta-call, not static vs `call((...))`.**

## THE AXIS IS BOUND-VS-UNBOUND, AND EACH OPERAND KIND SERVES ONE HALF

`findall/4`'s fourth argument is read as an input and bound as an output:

| 4th arg at call time | `term_e` (IR_VAR, on origin) | `term_lval_e` (IR_VAR_REF) |
|---|---|---|
| unbound var `T` | `t(_G0)` **RED** — a value read of an unbound var is detached from the slot, so the unification that should bind `T` binds a copy | `t([3])` green |
| **bound** var, statically called | `a([1,2,9])` green | `a([1,2,9])` green — slot not yet reused |
| **bound** var, **dynamically meta-called** | green | `[1,2\|nl]` **RED** |
| literal `[3]` | green | green (same node) |

⭐ The `|nl` tail is a **dangling frame reference**, not a lowering choice: the raw `IR_VAR_REF` descriptor is
`{DT_N, slen=1, p=&frame_slot}`, and consing it as a list tail keeps a pointer into the activation frame. Under the
dynamic meta-call the slot is reused before the list is printed, so the tail reads back as whatever goal now occupies
it. **The symptom renames itself per program** — which is why it reads as "the tail resolves to the continuation" and
would be re-diagnosed from scratch every time it surfaced.

## THE CURE IS THE REFERENCE PLUS ONE DEREF, IN THE RUNTIME, AND THE OBVIOUS DEREF IS WRONG

`rt_pl_all_solutions_tail_cell` (`src/runtime/by_name_dispatch.c:2344`) took the tail as `DESCR_t lst = args[2];` —
raw, never dereferenced. The lowering must pass a REFERENCE (an unbound tail has to stay bindable), so the runtime is
the layer that owes the deref.

⛔ **A plain `rt_pl_deref_val(args[2])` is the wrong deref — measured, not reasoned.** It returns `*cell` **by value**,
and an unbound cell's descriptor (`DT_SNUL`/`DT_FAIL`, or a self-referential `DT_PLVAR`) carries no pointer back to the
cell, so the copy is bindable and the variable is not: the static arm regressed straight back to `t(_G0)` with the
lowering flip still in place. Deref **only when the cell is bound**:

```c
DESCR_t t4 = args[2]; DESCR_t *c4 = plw_cell_deref(plw_entry(&t4));
... DESCR_t lst = plw_unbound_tag(c4) ? args[2] : *c4;
```

## ⛔⭐ THE PART THAT COST ME THE MOST AND IS WORTH THE MOST: MY OWN GATE WAS A FALSE GREEN FOR ITS OWN DEFECT

I wrote `test_gate_pl_findall_4_serves_a_bound_tail_and_an_unbound_one.sh` with **seven static witnesses**, ran it,
watched it go green on the cured tree, and wired it. Then I mutation-proved it — removed the runtime deref and re-ran —
and **it passed rc=0 while `a([1,2|nl])` was still printing from another witness three commands away.**

A gate that is green on the cure and green on the defect measures nothing. It would have sat in the blocking set
forever, costing 0.3s a run, protecting nothing, and reading as coverage. ⭐ **The general form: a gate is not proven
by going green on the fixed tree — it is proven by going RED on the broken one, and the mutation must be run, not
imagined.** The cure was to add the three dynamic meta-call arms; the gate is now mutation-proved BOTH ways.

⚠️ **And a second instrument error in the same sitting, from the same family as the first:** I read the mutation's
verdict as `rc=0` from `bash gate.sh 2>&1 | tail -8; echo "rc=$?"` — which reports **`tail`'s** status, not the gate's.
That is the `$?`-after-a-pipeline trap CLAUDE.md already names, hit while checking whether a test lies. Capture first
(`out=$(cmd 2>&1); rc=$?`), then read. The gate really was broken, so the wrong instrument happened to agree with the
right answer, which is the worst way to be right.

## MEASURED

```
witness                                          origin      lowering flip alone   flip + runtime deref
static  findall(X,(X=1;X=2),[A,B,3],T)           t(_G0) RED  t([3])                t([3])
static  call((findall(X,...,S,[3]),...))         green       green (same IR)       green
bound   U=[9], findall(Y,...,S,U)  statically    green       green                 green
bound   ... through run(G):-call(G) / catch/var  green       [1,2|nl] RED          [1,2,9]
row DONE-WHEN (both witnesses, m3 and m4)        RED         PASS                  PASS

--group, m3,m4, per-case, population unchanged and named on both sides:
  findall_4   14/15 -> 15/15   (+1: commons_findall_4_06)
  findall_3 14/14 · bagof_3 13/34 · setof_3 18/48 · forall_2 11/11 · call_1 20/20 · call_N 26/32 · catch_3 11/14
              — each measured on BOTH trees and identical, not assumed

test_gate_pl_findall_4_serves_a_bound_tail_and_an_unbound_one.sh   0.32s, 10 shapes x 2 modes + control arm
  cured tree                       GREEN rc=0
  runtime deref removed            RED   rc=1  (dynamic arms + control arm)
  IR_VAR_REF lowering reverted     RED   rc=1  (unbound arms)
test_gate_pl_allsol_goal_is_validated · _bagof_setof_grouping · _ctx_leaf_thunks_cannot_drop_a_ball ·
test_smoke_prolog                  all rc=0
```

⚠️ **One behaviour changes that is neither a pass nor a fail on either side, named rather than buried:**
`findall(X,(X=1;X=2),S,S)` (a tail that IS the bag — swipl builds a rational tree) prints `ERROR 246 stack overflow`
on origin and `f([2|nl])` after. Both are wrong against the oracle; no graded case covers it; it is a cyclic-term row,
left in the baton's `## NEXT` rather than taken here.

## THE TWO STANDING REDS THIS LANDING GRADED AGAINST

Both measured on a **stashed clean tree** and identical with the change, so neither is introduced by it:

`make preflight` reads **46 arms, 2 red** on both trees:

1. `util_gate_wiring.py` rc=1 — `test_gate_pl_backslash_c_layout_escape_agrees_with_the_oracle.sh` landed with SCRIP
   `0f7e2b8df` **on disk, in no recipe, in no list**. One line of Makefile owed by that landing's author. (This
   landing's own gate is wired AND adopted, so the count does not grow.)
1b. `test_gate_picker_lane_table_agrees_with_mode.sh` rc=2 — a **REFUSAL, not a red**, and the distinction is the
   point: MODE line 2 states no ownership it can parse for snocone, pascal, raku and rebus, so 4 of 7 languages
   cannot be checked in either direction and it declines to call that a pass. It reads `scripts/s4e_msg.sh` and the
   MODE file, neither touched here. ⭐ It appeared BETWEEN two of this session's control runs, on an unchanged tree,
   because MODE itself was rewritten — a reminder that a preflight baseline has the same shelf life as a MODE reading.
2. `test_gate_pl_quad_regs.sh` — **rc=1, `rtx-violations=1`**, both trees, byte-identical:
   `VIOLATION rtx_plunify.s:446  r15(BALL)  rtx=rt_pl_dop_list_guard  mov r15, rax`, with
   `files=411 writes=69783 enrolled=69783 violations=0 rtx-defined=77 rtx-reachable=30 rtx-writes=31` on both sides.
