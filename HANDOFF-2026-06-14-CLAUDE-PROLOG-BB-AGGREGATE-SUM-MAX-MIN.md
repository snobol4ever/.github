# HANDOFF — 2026-06-14 · Claude · Prolog BB — PL-BB-5 aggregate sum/max/min (m3/m4 91→93)

## Watermark
SCRIP `7561e59` (pushed; rebased onto `edba4d9` which arrived mid-session, no conflict) · .github `(this commit)`.
**m2 114/115 · m3 93/115 · m4 93/115.** GATE-1 5/5/5 HARD. NO-NEW-GLOBAL floor 15 (unchanged). m3≡m4 by construction.

## Gates (verified before push AND re-verified post-rebase)
GATE-1 `test_smoke_prolog.sh` 5/5/5 ✓. GATE-3 `test_prolog_rung_suite.sh` m2=114 / m3=93 / m4=93 ✓.
`test_gate_pl_no_new_global.sh` green at floor 15 ✓. rung27 5/5 ✓.
Cross-lang HARD: SNOBOL4 m4 7/7 ✓, Icon 12/12/12 ✓, Raku 35/35/35 ✓ (unification.c is in the shared libscrip_rt.so).
`bb_one_box` findings unchanged at 56 (pre-existing SNOBOL4/Icon files, proven by git-stash A/B: 56 before == 56 after).

---

## What landed — ONE commit (`7561e59`), the cleanest green-mover off 91

**`aggregate_all(sum(X)/max(X)/min(X))` as new REDUCE-MODES on the existing `IR_CELL_FINDALL` box.**
No new box, no new global, no new IR kind. This is the PL-BB-5 "same box + reduce-finishes" win the prior
handoff flagged as the cleanest ratchet-mover, and because m3≡m4 are byte-identical it moved BOTH modes 91→93.

Three files:
1. **`scrip.c`** (`pl_gz_build_goal`, the `aggregate_all` arm ~line 1535): now detects a `sum(X)`/`max(X)`/`min(X)`
   compound template (op `IR_STRUCT` or `IR_ARITH`, arity 1, inner arg an `IR_LOGICVAR`), sets `agg_mode` 2/3/4,
   and passes the INNER arg `X` as `fst->tmpl`. The existing collect loop (`gzu_build(tmpl)` →
   `rt_pl_findall_collect`) then conses `X`'s numeric VALUE per solution — identical mechanism to count's
   `agg_mode=1`. The admission gate (`pl_gz_count_synth_goal`) already passed `aggregate_all` through (it
   falls to the generic `IR_BUILTIN`→return-1 arm); the real decision is this build arm, which `count` already
   proved works for top-level `main` bodies.
2. **`unification.c`** (after `rt_pl_agg_count_finish`): three new reduce-finishes over the `pl_findall_acc`
   `Term*` number list. `rt_pl_agg_sum_finish` (start 0, int/float-aware accumulate; empty⇒0).
   `rt_pl_agg_minmax_finish(acc,res,want_max)` + thin `_max_finish`/`_min_finish` wrappers (fold;
   **fail on empty goal** per SWI's `nonvar(Max)` discipline — see library/aggregate.pl lines 204-225).
   A small `agg_num(t,&iv,&dv,&isf)` helper reads INT/FLOAT, rejects non-numbers.
3. **`bb_cell_findall.cpp`** (`bcfa_finish`): new `bcfa_finish_call()` switches the finish `rt_*` on
   `bcfa_agg()` (=`op_parts_ival[10]`): 1→count, 2→sum, 3→max, 4→min, default→`rt_pl_findall_finish` (list).

### Correctness note worth carrying forward (latent m2 divergence)
On an EMPTY goal, the new m3/m4 path is MORE correct than m2: SWI `aggregate_all(max(X),Goal,_)` FAILS when
Goal has no solutions (the `nonvar` check); my reduce-finishes reproduce that (max/min return 0=fail on n==0).
The m2 interpreter currently returns `max=0` for an empty goal — the SWI-incorrect behavior. No gate exercises
empty-goal aggregate so GATE-3 is unaffected, but if someone aligns m2 later, match the fail-on-empty semantics.

---

## The 22 remaining m3/m4 failures — PRE-TRACED map for the next session

All 22 fail identically in m3 and m4 (parity holds). Enumerated by name this session:

### rung11 findall ×2 — same box I just worked in, but two DISTINCT root causes (both traced)
- **`findall_arith`**: `findall(Y, (num(X), Y is X*X), Ys)` → m3 gives `[_G-1,_G-1,_G-1]` (WRONG, counted FAIL).
  ROOT CAUSE: the findall GOAL is a CONJUNCTION. `lower_prolog` threads `t->c[1]` so `fs->gcfg->entry` is the
  FIRST goal's α (`num(X)`), an `IR_GOAL` — so the `groot->op==IR_GOAL` admission passes treating the goal as
  just `num(X)`, and the conjunction TAIL (`Y is X*X`) is silently dropped. Y stays unbound → collected as a
  fresh var 3×. FIX OPTIONS: (a) lambda-lift the conjunction into a synthetic helper predicate
  `'$fa0'(X,Y) :- num(X), Y is X*X.` at lower time, then the existing single-callee drive works (standard
  Prolog technique, cleanest); (b) teach the findall box to drive a conjunction inner goal (bigger).
- **`findall_filter`**: `findall(X, even(X), Xs)`, `even(X) :- num(X), 0 is X mod 2.` → m3 `[PL-GZ FENCE]`.
  ROOT CAUSE: the callee `even`'s body contains `0 is X mod 2` — an `is/2` with a LITERAL (non-logicvar) LHS.
  Both `pl_gz_rule_body_goal_ok` (~line 550) and `pl_gz_rule_clause`'s `is` arm require LHS `op==IR_LOGICVAR`,
  so `even` is rejected from inline admission → the whole findall fences.
  KEY FINDING: the RUNTIME needs NO change — `rt_pl_is_cell_int/arith/bivar` (IR_interp.c ~1704-1850) all
  `unify(term_deref(lhs), vt, …)`, so a bound/literal LHS already compares correctly (unifies `0` with the
  result of `X mod 2`). The fix is ADMISSION + EMISSION only: allow a literal LHS by synthesizing a fresh
  logicvar slot, bind it to the literal, then `is` against it (the `pl_gz_lv(kk)` synth pattern the aggregate
  inner-arg + struct-unify paths already use). CAVEAT: this `is` is inside a CALLEE rule body, emitted by the
  rule-clause codegen — NOT `pl_gz_build_goal` — so the synth must reach the rule-body path (or be a lower-time
  `Const is Expr` → `Fresh is Expr, Fresh == Const` rewrite, which also touches m2; verify m2 stays 114).

### rung14 retract ×5 (B3) — NEW generator box
A DB-cursor generator (semidet→nondet, HAS a β). DESIGN-PROLOG-BB-ALL §3: `ret.α` = first matching clause,
bind+mark→γ; `ret.β` = unwind(mark), next matching clause. `cursor` is the frame value.

### rung15 abolish ×5 (B4) — NEW bounded box
Bulk removal, bounded (no β). DESIGN §3. `rt_pl_abolish_*` removes clause records.

### rung28 catch/throw ×5 (B2) — NEW control box (the one genuinely Prolog-specific control box)
DESIGN §4: `catch.α` pushes a catch-frame cell (catcher + &Recovery.α + trail/CP marks), runs Goal as a
closure; matching `throw` is a non-local ω lands at Recovery.α. ⚠ The catch RESIDUE globals
(`g_resolve_catch_top/stack`, `rt_catch_native`) are still live and reached by m2's catch path — do NOT delete
them as part of DEMOLITION until this box lands (the prior handoff's "PROBE FIRST" warning).

### rung30 DCG ×5 (B5) — pure LOWERING, no new box
DESIGN §5: `H --> B` becomes an ordinary clause of arity+2 threading a difference list `(S0,S)`; `phrase/2,3`
is then a plain predicate call. `lower_prolog` already has a `phrase` arm (line ~242) but the `-->` rule
translation / generate-mode is incomplete.

---

## Recommended next pick (by leverage, given the above traces)
1. **rung11 `findall_filter`** — smallest, fully traced, runtime already correct; only admission+synth. +1 both modes.
2. **rung11 `findall_arith`** via lambda-lifting the conjunction goal — generalizes findall, +1 both modes, and
   the same lambda-lift unblocks any compound findall/aggregate goal (high downstream value).
3. **rung30 DCG** — 5 tests, pure lowering (no new box, no new global), lower-risk than the new control boxes.
4. retract/abolish/catch are each a NEW box (5 each) — larger lifts; catch is gated by the m2-catch-residue probe.

## Discipline followed
One code commit to SCRIP, gated before push (GATE-1 5/5/5 HARD, GATE-3 114/93/93, no-new-global floor 15) AND
re-verified after the mid-session rebase onto `edba4d9`. Touched only the Prolog GZ findall path + the shared
`unification.c` (cross-lang smokes confirmed unaffected). No FACT RULE edited. No new global, no new box, no new
IR kind. PLAN.md goals table NOT touched (routine handoff). Goal-file STATE block updated with the 93/93 watermark.
