# HANDOFF 2026-06-03 (Opus 4.8) — Prolog-BB: PT-2b-simple findall + literal-int-LHS is (m4 91→95)

## TL;DR

Two gated landings. **(1) `ea9e5ea` PT-2b-simple:** `findall/3` over **nondeterministic SIMPLE
goals** (a single predicate call) now emits and runs natively in mode-4 through the PT meta rail
(`rt_call_term`/`rt_redo_meta`/`rt_findall_term`, all landed in `62426a6`). **(2) `c8063ec`
literal-int-LHS `is/2`** (`0 is X mod 2`), the separable blocker for the filter rung. m4
**91 → 95 / 0 / 20**; GATE-3 m2/m3 **115/115 held**; **zero FAILs** — every widened admission
either passes or cleanly EXCISES. New m4 passes: `rung11_findall_findall_{basic,template,filter}`
+ `rung30_dcg_generate` (the `phrase` goal rode along free — DCG translation yields a single
IR_GOAL). All 20 remaining EXCISED sit squarely on PT-1b / PT-3 / PT-4.

## Landing 1 — PT-2b-simple (`ea9e5ea`, 3 files)

1. **`src/emitter/BB_templates/bb_builtin.cpp`** — `emit_build_compound_term` gains an
   **IR_GOAL arm**: builds the goal Term from `bb_goal_state_t` (functor = `zc->callee`, args
   from `zc->args[i]`, post-order via the same walker); **arity-0 builds an ATOM** term so
   `rt_call_term`'s `TERM_ATOM` branch fires. Fully relocatable (literal immediates +
   `[rip+strlabel]` only) — same law as the IR_STRUCT/IR_ARITH arms. The findall TEXT arm's
   existing `else emit_build_compound_term(fs->goal_node)` branch needed no change.

2. **`src/driver/scrip.c`** — admission (RICH gate only → m4 only):
   - `pl_findall_term_buildable` — recursive mirror of the encoder's coverage
     (ATOM/LIT_I/LIT_F/LOGICVAR leaves; STRUCT γ-chain; ARITH α/β). Applied to goal args AND
     tmpl AND result.
   - `pl_findall_goal_graph_simple` — **THE TRAP THIS SESSION HIT AND FIXED:**
     `fs->goal_node = gα` is the goal graph's ENTRY, which for a conjunction
     `(num(X), Y is X*X)` is the FIRST goal's α — a registered `IR_GOAL` that masquerades as a
     complete simple goal. Admitting it emitted a findall that called only `num(X)`, dropping
     the `is` — wrong answer `[_G-…]`, a FAIL (worse than EXCISE). And `γ==NULL` alone is NOT a
     sufficient guard (a disjunction's first branch also has `γ==NULL`). The honest check: the
     goal graph (`fs->gcfg`) contains **exactly ONE control-position node**
     (GOAL/GCONJ/DISJ/ITE/CHOICE/CUT/BUILTIN/UNIFY/FAIL/SUCCEED), and it is `fs->goal_node`.
     Term-operand kinds don't count. This is the admission to widen when PT-1b lands.
   - `pl_findall_goal_admissible` — goal ∈ {IR_FAIL, IR_SUCCEED, true/fail/false atom} or
     IR_GOAL whose **callee exists in the compile-time pred registry**. NOTE: registry names
     carry the arity suffix (`"color/1"`); compare suffix-stripped (`strrchr('/')`), exactly as
     `codegen_pl_pred_table` already does when emitting `.Lpl_pname_*`. Unknown callee →
     EXCISE, never a wrong-answer `[]` (rt_call_term would stderr-and-fail → findall would
     "succeed" with `[]`).

3. **`src/interp/IR_interp.c`** — **bug fix in `rt_findall_term`**: after redo-exhaustion the
   machine was left with `g_resolve_env` pointing at the CALLEE env (`rt_redo_meta` installs
   `cp->env` before each redo; the final failing redo never restores), so a following
   `write(Xs)` resolved Xs in the wrong env and printed `_`. Now saves/restores
   `g_resolve_env` + `g_resolve_cut_flag` + `g_resolve_cut_barrier` around the drive,
   mirroring `rt_findall`'s outer-state discipline (the gcfg-driver sibling directly above it).

## Landing 2 — literal-int-LHS `is/2` (`c8063ec`, 4 files)

**Canonical grounding** (RULES "CONSULT CANONICAL SOURCES"): gprolog `BipsPl/arith_inl.wam`
compiles `is/2` as `math_load_value(x(1),1)` + **`get_value(x(0),1)`** — evaluate RHS, then
**general-unify** with the LHS term, whatever it is. LHS need NOT be a var. For a LIT_I LHS
this is **type-sensitive unify, NOT `=:=` value-compare** (`0 is 0.0` is FALSE; `0 =:= 0.0` is
TRUE) — which is why this is its own runtime entry and not a rewrite to the cmp family.

- **`src/interp/IR_interp.c`** — `rt_is_lint(lval, op, lk, li, rk, ri)`: one `rt_arith` eval +
  one `unify` against `term_new_int(lval)`. Mirrors `rt_is`'s flow exactly (NO-DUP: the ONE
  evaluator, the ONE unify).
- **`src/emitter/BB_templates/bb_builtin_is_cmp.cpp`** — TEXT-only arm, sibling of the V-2
  binary var-LHS arm (same marshal shape, `mov rdi,<lval>` instead of `mov edi,<dst_slot>`).
  `_.bb_op_lbl` was already deposited unconditionally on LHS kind by `bb_prepare`.
- **`src/emitter/BB_templates/bb_builtin_common.h`** — `rt_is_lint` extern (additive).
- **`src/driver/scrip.c`** — `pl_rich_is_lint_simple` (LIT_I LHS + non-floaty binary ARITH RHS
  with simple int leaves), OR-ed into the RICH gate's `is` arm only. **The FLAT gate is
  deliberately untouched** — per the float-unify precedent
  (HANDOFF-…-FLOAT-UNIFY-M4), admitting new shapes to the flat gate makes m3 build them as
  in-process blobs, which is the undebugged hazard. m4-native, m3-interpreted.

## Gate state (HEAD `c8063ec`, all re-verified)

| Gate | Before | After |
|---|---|---|
| GATE-1 smoke | m2 5/5 · m3 4/5 · m4 5/5 | unchanged |
| GATE-3 rung suite | m2 115 · m3 115 · m4 91/0/24 | m2 **115** · m3 **115** · m4 **95/0/20** |
| FAILs (m4) | 0 | **0** |
| PL-HY-FENCE one-box | PASS | PASS |
| pl-no-value-stack | PASS | PASS |
| medium-invisible | 343 | 343 (new is arm is pure `s_2asm` TEXT) |
| no_bb_bin_t / b.size() / seg_byte / SL_B / g_vstack | all 0 | all 0 |
| siblings | Icon = `991a26b` re-baseline · SNOBOL4 pat 1/2·1/19 | **identical** (Icon verbatim; SNOBOL4 stash-A/B-verified) |

Remaining m4 EXCISED-20: `findall_arith` (conjunction goal → **PT-1b**) · 5 retract · 5
abolish (**PT-4**) · 4 aggregate/nb (**PT-4**) · 5 catch/throw (**PT-3**).

## Hazards / notes for the next session

- **PT-1b admission point is ready:** when the term-level control resolver lands, widen
  `pl_findall_goal_graph_simple` (or replace it with "goal graph serializable as a control
  TERM") — that single gate is what keeps conjunction/disjunction goals EXCISED today.
- **Nested meta-calls:** `g_pl_meta_redo` is a single static — fine for findall's single-level
  drive; PT-1b's nested meta-call stack must replace it (already called out in GOAL PT-1).
- **Corpus `.s` artifacts are stale** (SM-era macro preambles incl. `rt_push_null` value-stack
  residue). Recent sessions re-cleaned (`git checkout HEAD -- 'programs/prolog/*.s'`) rather
  than regen-committing; last regen commit was PLR-K-9 era (`5354a66`). A fresh
  "Regenerate Prolog rung .s artifacts: post-PT-2b" commit would purge the residue —
  **Lon's call**, not taken unilaterally. `rung42/43*.s` remain untracked from the prior
  session.
- **Compound-nested float** latent gap in `emit_build_compound_term` (IR_LIT_F arm drops dval)
  unchanged from the float-unify handoff; now also reachable via findall goal/tmpl args. No
  corpus test yet.

## Build / verify

```bash
cd /home/claude/SCRIP && make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_prolog.sh          # m2 5/5
bash scripts/test_prolog_rung_suite.sh     # m2 115 · m3 115 · m4 95/0/20
# probes:
printf ':- initialization(main).\ncolor(red). color(green). color(blue).\nmain :- findall(X, color(X), Xs), write(Xs), nl.\n' > /tmp/fa.pl
bash scripts/run_prolog_via_x86_backend.sh /tmp/fa.pl        # [red,green,blue]
printf ':- initialization(main).\nmain :- X = 4, 0 is X mod 2, write(ok), nl.\n' > /tmp/il.pl
bash scripts/run_prolog_via_x86_backend.sh /tmp/il.pl        # ok
```
The suite regenerates `corpus/programs/prolog/*.s`; `git checkout HEAD -- 'programs/prolog/*.s'` to re-clean.

Authors: LCherryholmes · Claude Opus 4.8
