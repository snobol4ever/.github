# HANDOFF — 2026-06-01 — OPUS48 — PROLOG-BB — PLG-5 (`\=`, `\+`, safety) + IR_DISJ var-binding (in progress)

Model: Claude Opus 4.8. Continues the GOAL-PROLOG-BB ladder. Focus this session: PLG-5
(multi-goal body backtracking, the rung10 puzzle pattern). Three fixes LANDED in the working
tree (not yet committed); one bug (IR_DISJ cross-arm variable binding) DIAGNOSED to the exact
line, fix in progress.

--------------------------------------------------------------------------------------------------
## BASELINE AT HANDOFF (verified, working tree, NOT committed)
--------------------------------------------------------------------------------------------------
- `bash scripts/prove_lower2.sh`  -> 64 PASS / 0 FAIL   (topology gate green)
- `bash scripts/test_smoke_prolog.sh` (GATE-1):
    - mode-2 (--interp):  PASS=5 FAIL=0  / 5   (HARD GATE — green)
    - mode-3 (--run):     PASS=5 FAIL=0 EXCISED=0 / 5
    - mode-4 (--compile): PASS=3 FAIL=0 EXCISED=2 / 5  (clause+recursion still EXCISED — unchanged)
- Anchor programs (mode-2) all correct:
    - rung05_backtrack -> `a b c`
    - rung08_recursion -> `8 6`
    - rung10 puzzle_01 -> `Cashier=smith Manager=brown Teller=jones`
- rung10 puzzles producing non-empty output: 8/20 at a 12s timeout (was 6/20 before this session;
  one extra puzzle lands between 10-12s, so the count is timeout-sensitive, not a hard 8).

Build: `make -j4 scrip && make libscrip_rt`. (Standard. `scripts/install_system_packages.sh` first
on a fresh container.) Git identity already set; clone creds per the operator's standing note.

Working tree: ONLY `src/lower/bb_exec.c` and `src/lower/lower.c` are modified. All debug hooks
(`SCRIP_BIND_DBG`, `SCRIP_DISJ_DBG`) have been REMOVED. Nothing committed — review before commit.

--------------------------------------------------------------------------------------------------
## FIX 1 (LANDED, verified) — `\=` not-unifiable was completely missing
--------------------------------------------------------------------------------------------------
Symptom: `carpenter \= painter` returned FALSE (should be TRUE). `lower.c`'s GOAL arm handled
`=\=` (arith not-equal) and `\==` (structural not-identical) but had NO arm for `\=` (the
negation-as-failure of `=/2`), so it fell through to the default and misbehaved.

Authoritative semantics consulted (4-swipl-devel): ISO 7.4.1, SWI `\=(X,Y) :- \+(X=Y)`.
Succeeds iff A and B are NOT unifiable; makes no binding either way; semidet.

Implementation: new helper `g_not_unify` in `lower.c` (around line 1820). Builds the
negation-as-failure ITE directly at IR level (no synthetic tree nodes): Else = IR_SUCCEED,
Then = IR_FAIL, condition = `g_unify(A,B)`. Mirrors the existing `g_ite` topology / the
`bb_ite_state_t` sidecar. Wired in the TT_FNC arm:
    lower.c:2005  `if (tm_g(e, TT_FNC, "\\=", 2, &A, &B)) return g_not_unify(...)`

--------------------------------------------------------------------------------------------------
## FIX 2 (LANDED, verified) — `\+` / `not` negation-as-failure was missing
--------------------------------------------------------------------------------------------------
Same root shape as Fix 1. Parser already produces `TT_FNC("\\+",[Goal])` / `TT_FNC("not",[Goal])`
(prolog_parse.c lines ~265, ~566, ~841). No GOAL arm consumed them.

Authoritative semantics (4-swipl-devel): ISO 7.8.6, SWI boot/init.pl
`\+(Goal) :- (Goal -> fail ; true)`. Run Goal once; if it SUCCEEDS the whole goal FAILS; if Goal
FAILS the whole goal SUCCEEDS. Semidet.

Implementation: new helper `g_neg_goal` in `lower.c` (around line 1800). Same IR-level ITE as
`g_not_unify` but the condition is an arbitrary lowered goal (`lower_goal(cx, goal_t, ...)`)
rather than `g_unify`. Wired:
    lower.c:2007  `if (tm_g(e, TT_FNC, "\\+", 1, &arg)) return g_neg_goal(cx, e->c[0], ...)`
    lower.c:2008  `if (tm_g(e, TT_FNC, "not", 1, &arg)) return g_neg_goal(cx, e->c[0], ...)`

Verified: `\+(fail)` succeeds, `\+(true)` fails, `\+(X=bar)` with X=foo succeeds, etc.

--------------------------------------------------------------------------------------------------
## FIX 3 (LANDED, verified) — safety-counter truncation silently killed deep backtracking
--------------------------------------------------------------------------------------------------
THIS WAS THE BIG ONE for PLG-5. `bb_exec_once` / `bb_exec_resume` guarded their port-follower
loop with `safety = bbg->n * 64 + 256`. For the main graph (~20-30 nodes) that is ~2000 steps.
A program that backtracks N^k times through k nested generators traverses far more node-steps
than that, so the loop hit the safety cap and returned FAILDESCR MID-RUN — no error, just
truncated/empty output. This is why 6-generator `fail`-loops and most rung10 puzzles "hung"
(they were actually being silently cut off, or running just under the cap and producing nothing).

Minimal reproducer that nailed it: 5 nested `age/1` + `fail ; true` -> `done`; SIX nested ->
empty. The boundary was the step budget, not arity.

Fix (4 sites, all in bb_exec.c): raise the multiplier/floor to `n * 65536 + 1048576`.
    bb_exec.c:4780  bb_exec_once initial
    bb_exec.c:4791  bb_exec_once LCO-redirect reset
    bb_exec.c:4817  bb_exec_resume initial
    bb_exec.c:4828  bb_exec_resume LCO-redirect reset
The counter is purely an anti-infinite-loop dev guard; enlarging it changes no semantics.
After this fix the 6-generator loop, `differ6/6`, and the basic-constraint phase of the puzzles
all complete. NOTE: this is a band-aid sized for the corpus; a principled version would budget by
choice-point depth, or drop the guard now that the engine is trusted. Flag for a future cleanup.

--------------------------------------------------------------------------------------------------
## BUG 4 (DIAGNOSED to the exact line; fix IN PROGRESS) — IR_DISJ cross-arm variable binding
--------------------------------------------------------------------------------------------------
This is the remaining blocker for the empty rung10 puzzles. All of them funnel through a
disjunction whose arms bind a variable that the continuation then reads
(`( ... , V=name1 ; ... , V=name2 ), write(V)`), so this one bug accounts for the bulk of the
remaining empties.

### Reduced reproducer (THE test to fix against)
    main :- ( X = a ; X = b ), write(X), nl, fail ; true.
    EXPECT: a / b      GOT: a / a

Control flow is CORRECT — both arms run and the `; true` tail fires (verified with a `seen(X)`
+ `end` variant: prints `seen(a) seen(a) end`, i.e. two iterations + tail). The defect is purely
that arm-1's binding does not take effect: X is still bound to `a` when arm 1 runs.

### What I changed in IR_DISJ this session (the rewrite so far)
The ORIGINAL IR_DISJ exec was deeper-broken than the binding bug: it did
`bb_exec_node(bb->α)` INLINE and read only that one node's value — but DISJ's `bb->α`/`bb->β`
were never set by `wire_alt` (arms live in the `operand_aux` sidecar, not the node ports), and a
multi-node arm (a conjunction) only had its FIRST node executed. So the old code returned
FAILDESCR for any non-trivial arm; top-level `member(...);true` only worked because that arm is a
single resumable GOAL node.

I rewrote it to a PURE-JUMP model (bb_exec.c:3677, marked "Pure-jump model"):
  - state=0: save trail mark in `bb->ival`, `bb->counter=0`, `return arms[0]` (jump into arm 0;
    the OUTER port-follower then drives the arm sub-chain — no inline execution).
  - resume (backtrack re-enters via DISJ.β = DISJ itself): `trail_unwind(to bb->ival)`,
    `bb->counter++`, if exhausted -> ω; else save fresh mark, `return arms[counter]`.
And in `wire_alt` (lower.c:178-201), FOR IR_DISJ ONLY:
  - store ENTRY nodes (not apply nodes) in operand_aux  (lower.c:194) — Prolog jumps to entries;
    Icon IR_ALT / SNOBOL IR_PAT_ALT still store apply nodes (their collector advances via ->ω).
  - wire each arm's success edge straight to the continuation `γ_in` (lower.c:181 `arm_succ`,
    used at :186 and :188) rather than back to the DISJ node. DISJ is re-entered ONLY on
    backtrack (its `ret(..., node)` resume), so the continuation's ω-edge (patched by
    lower2_clause_body_entry / wire_seq to DISJ's resume) brings control back to advance arms.
  - also set `node->α = entry[0]` (lower.c:201) — harmless; Icon ignores it.

These changes are SOUND for control flow (rung05/rung08/puzzle_01 and the `;true` tail all hold,
gates green). The binding bug is the one thing left.

### The exact defect (traced with the now-removed SCRIP_BIND_DBG / SCRIP_DISJ_DBG hooks)
`bind()` in src/frontend/prolog/prolog_unify.c only trails when `var->var_slot != -1`, fine.
Trace of the reproducer:
  - `X=a` calls bind exactly ONCE: var_slot=0, trail_before=0  (binding lands at trail index 0)
  - `X=b` NEVER calls bind at all
  - at DISJ resume: saved mark `bb->ival = 1`, live trail top = 1
=> The X=a binding sits at trail index 0, which is BELOW the saved mark 1, so
   `trail_unwind(to 1)` does NOT undo it. Arm 1 then runs `X=b` against an X still bound to `a`;
   `unify(a,b)` fails silently (atoms a != b, no bind), and `write(X)` re-emits `a`.

ROOT: the DISJ trail mark is captured at value 1 while the arm's binding goes to index 0 —
i.e. the mark was taken AFTER (or out of order with) the arm's first binding, instead of strictly
BEFORE it. Likely an execution-ordering interaction between the OUTER and INNER disjunction marks
(two DISJ nodes share the `bb->ival` convention) or eager argument/term materialization happening
before state=0 runs. The invariant we MUST establish: the mark DISJ saves before launching arm i
is <= the trail index of arm i's first bind.

### NEXT STEP (concrete)
1. Re-add the two debug hooks (trivial — one fprintf in `bind`, two in the IR_DISJ resume arm)
   and print, for arm 0's first bind, both `trail_before` and the mark DISJ saved. Confirm the
   ordering violation directly (expect saved_mark > trail_before, which is the bug).
2. Fix so the saved mark provably precedes any arm binding. Candidate approaches, cheapest first:
     (a) Ensure state=0 captures `bb->ival = trail_mark()` is the FIRST thing that runs for the
         DISJ before control ever reaches an arm — check whether something materializes the arm's
         terms (resolve_node_to_term creating/era-stamping vars) before state=0. If the inner and
         outer DISJ are both writing `bb->ival`, give the resume its mark from a per-arm saved slot
         rather than a single shared `ival` (e.g. store the pre-launch mark keyed by counter, or
         push a real RESOLVE_CP_DISJ choice point carrying trail_mark+env like the ORIGINAL code
         did, and unwind to cp->trail_mark on resume — the CP machinery already records the mark at
         the right instant).
     (b) Preferred if (a) is fiddly: on resume, unwind using a choice-point's recorded
         `trail_mark` (resolve_cp_push/cp->trail_mark, see prolog_unify.c / resolve_runtime.c)
         instead of `bb->ival`. The CP is pushed at launch time, so its mark is taken at the
         correct instant by construction. This re-introduces the CP the rewrite dropped, but only
         as the mark carrier; the jump model stays.
3. Regression set to re-run after the fix (ALL must hold):
     - rung05 -> a b c                (top-level disj + fail loop)
     - `( X=a ; X=b ),write(X),fail ; true` -> a b   (THE target)
     - p03_var: `( X=:=1,R=one ; X=:=2,R=two ; X=:=3,R=three ), write(R)` with X=3 -> three
     - rung08 -> 8 6 ; puzzle_01 -> cashier line
     - GATE-1 (m2 5/5 hard) + prove_lower2 64/64
     - full rung10 puzzle sweep (count should jump well past 8 once binding works)

--------------------------------------------------------------------------------------------------
## SCRATCH REPRODUCERS (in /tmp on the work container; recreate if gone)
--------------------------------------------------------------------------------------------------
  /tmp/test_disj_var.pl    `main :- ( X = hello ; X = world ), write(X), nl, fail ; true.`
  /tmp/t_disj_min.pl       `main :- ( X = a ; X = b ), write(X), nl, fail ; true.`
  /tmp/t_disj_diff.pl      `... write(seen(X)) ... ; write(end), nl.`  (shows 2 iters + tail)
  /tmp/p03_var.pl          disjunction arms binding R, then write(R)
  /tmp/test_arity.pl       p4/p5/p6 predicate-arity smoke (all pass — arity is NOT the issue)

--------------------------------------------------------------------------------------------------
## ORIENTATION POINTERS
--------------------------------------------------------------------------------------------------
- DISJ exec:            src/lower/bb_exec.c  case IR_DISJ (3677)
- DISJ lowering:        src/lower/lower.c    wire_alt (167) — arm_succ / operand_aux split at 181-201
- NAF helpers:          src/lower/lower.c    g_neg_goal (1800), g_not_unify (1820), wired 2005-2008
- ITE reference model:  src/lower/bb_exec.c  case IR_ITE (3638) — the clean "return bb->α" pattern
                        the DISJ rewrite is modeled on
- Icon IR_ALT (do NOT break — shares wire_alt/operand_aux): bb_exec.c case IR_ALT (2270)
- bind / trail:         src/frontend/prolog/prolog_unify.c bind (31), unify (38), trail_push (14)
- choice-point API:     src/runtime/interp/resolve_runtime.{h,c} resolve_cp_push / cp->trail_mark
- safety guard sites:   bb_exec.c 4780, 4791, 4817, 4828
- PLG ladder + gate defs: .github/GOAL-PROLOG-BB.md  (PLG-5 is the active step; PLG-6 recursion
  deep-stress + snapshot=0 is next after PLG-5 closes)
