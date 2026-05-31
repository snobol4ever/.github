# HANDOFF — 2026-05-28 — Opus 4.7 — Prolog BB — SWI-NEXT step 1: TT_VAR-as-goal

**Repos:** SCRIP only (single file: `src/lower/lower_pl.c`).
**Predecessor:** `6c3d8703` (Opus 4.7, SWI-5 EMPTY verdict scripts).
**Successor target:** `a21dc32b` (post-rebase landing point for this commit).
**Type:** Partial fix + diagnostic. Step 1 of 2 needed to unblock real SWI test execution.

---

## TL;DR

`lower_pl.c` returned NULL whenever it was asked to lower a bare `TT_VAR` as a goal.
That silently wiped out the body of any user predicate that meta-called one of its
own arguments, including `foo(G) :- catch(G, _, _)`. The empty body produced a
one-RETURN BB graph; the call site appeared to be a no-op, masquerading as
"predicate not found" in failure traces.

**Fixed in this session.** Added a `TT_VAR` arm in `lower_pl_goal` that synthesizes
a `BB_PL_CALL(callee="call", arity=1)` so the existing SWI-2d intercept in
`bb_exec.c BB_PL_CALL` handles the meta-dispatch. Mirrors standard Prolog
semantics: `?- X.` ≡ `?- call(X).`

**Still broken (step 2, next session).** The same bug pattern exists for `once/1`
in the BB-graph dispatch path. `bb_exec.c BB_PL_CALL` intercepts `callee=="call"`
(SWI-2d) but not `callee=="once"`. So `once(G)` falls through to a non-existent
`once/1` user-predicate lookup and silently fails. plunit's `pj_run_tests` uses
`once(pj_run_one(...))` heavily, so until once/1 is intercepted, no plunit
test body ever returns from `pj_run_one`, and all 9 SWI suites stay EMPTY.

GATE-SWI remains at 57/57 EMPTY (honest baseline from SWI-5). All other gates
byte-identical: GATE-1 5/5, GATE-2 132/0, GATE-3 m2 104/107, GATE-4 4/4,
BB-honest 128/0, FACT 0, smokes all green.

---

## How the bug was found

Following PL-RT-USER-FROM-SYNTH-2 (`61187cc7`) and SWI-5 (`bafe415`/`6c3d8703`),
the obvious follow-up was: real test execution. The SWI-5 handoff already
flagged `pj_do_succeed(s, n, true)` returning false for some reason.

Bisection in `/tmp/bisect*.pl`:

1. `catch(true, _, R), !, ...` standalone → works
2. `pj_do_succeed/3` standalone → fails
3. `foo(A, B, G) :- catch(G, _, R)` → fails
4. `foo(G) :- catch(G, _, R)` → fails — minimal repro
5. `foo(G) :- call(G)` → works (the contrast)
6. `foo(G) :- catch(call(G), _, R)` → works (workaround)

The contrast between (4) and (6) localized the bug to catch's lowering. Reading
`src/lower/lower_pl.c:502+` (the `catch/3` arm) showed that catch lowers its
first arg (Goal) through `lower_pl_goal(gcfg, e->c[0], ...)` into a self-contained
sub-graph. When `e->c[0]` is a TT_VAR, `lower_pl_goal` returns NULL because the
case-match ladder ends with:

```c
if (e->t != TT_FNC || !e->v.sval) return NULL;
```

at line 445 (pre-fix). TT_VAR doesn't match TT_FNC, so it returns NULL. The
catch arm propagates: `if (!g) return NULL;`. The clause body becomes NULL. The
predicate's whole body ends up an empty BB graph.

SM dump for the broken case showed:
```
   0  SM_JUMP        -> 3
   1  SM_LABEL       s="foo/1"
   2  SM_RETURN       ← empty body!
   3  SM_LABEL
   ...
```

versus a working case where the body had actual BB_INVOKE / BB_PL_CALL.

---

## The fix

`src/lower/lower_pl.c`, inserted between the 0-arity-call arm and the existing
TT_FNC guard:

```c
if (e->t == TT_VAR) {
    BB_t *bb = BB_node_alloc(bbg, BB_PL_CALL); if (!bb) return NULL;
    bb_pl_call_state_t *zc = (bb_pl_call_state_t *)GC_MALLOC(sizeof *zc);
    zc->callee = "call"; zc->arity = 1; zc->cs = NULL;
    zc->args = (BB_t **)GC_MALLOC(sizeof(BB_t *)); zc->nargs = 0;
    BB_t *aα = NULL, *aβ = NULL;
    BB_t *a = lower_pl_term(bbg, e, γ_in, ω_in, &aα, &aβ); if (!a) return NULL;
    zc->args[zc->nargs++] = aα;
    bb->sval = "call"; bb->ival = (int64_t)(intptr_t)zc;
    bb->α = zc->args[0];
    bb->γ = γ_in; bb->ω = ω_in;
    if (α_out) *α_out = bb;
    if (β_out) *β_out = bb;
    return bb;
}
```

The TT_VAR itself lowers through `lower_pl_term` into a `BB_PL_VAR` node (an
env-indexed Term ref). The synthesized `BB_PL_CALL` with `callee="call"` and
`args[0]=<that BB_PL_VAR>` is what BB_PL_CALL's SWI-2d intercept already knows
how to dispatch:

```c
// bb_exec.c:3270-3290
if (carity >= 1 && strcmp(callee, "call") == 0) {
    ...
    Term *gt = pl_node_to_term(zc->args[0]);
    gt = term_deref(gt);
    ok = pl_call_term(gt);
    ...
}
```

Zero new infrastructure. Zero template changes. Zero changes outside lower_pl.c.
Behavior-neutral for every existing gate because none of them exercise the
TT_VAR-in-goal-position pattern (the corpus deliberately avoids it, since it
was known to be broken).

---

## What still needs to land (step 2)

`once/1` has the same shape of missing intercept in BB_PL_CALL. The fix is
mechanical: add an `||` to the existing call intercept guard, dispatch through
the same `pl_call_term`:

```c
// bb_exec.c:3270 — REPLACE existing line:
if (carity >= 1 && strcmp(callee, "call") == 0) {
// WITH this (preserves call/N for N>1, adds once/1):
if ((carity >= 1 && strcmp(callee, "call") == 0) ||
    (carity == 1 && strcmp(callee, "once") == 0)) {
```

`once(G)` semantically equals `call(G), !`. The current `pl_call_term`
already commits to one solution via `pl_invoke_var_goal` (no resume), so
treating `once(G)` identically to `call(G)` is semantically equivalent in
this BB-graph path. The AST-runtime path in `pl_runtime.c` has had this branch
at line 1108 since long ago — the BB-graph path just never gained the
companion intercept.

**Warning for the next session:** my first attempt this session narrowed
`carity >= 1` to `carity == 1` accidentally, which would have broken
SWI-2d/2e `call/N` for N>1. The correct shape is either the OR form above
or two separate guard arms. Test with rung33 mode-2 (`rung33_bridge_callN`
should remain 5/5 — that gate confirms call/N for N>1 works) after the edit.

**Combined effect of step 1 + step 2:** plunit's `pj_run_tests` body
`once(pj_run_one(Suite,N,O,G))` will:

1. `once(...)` — intercept fires, calls pl_call_term with `pj_run_one(...)` (step 2)
2. `pj_run_one(Suite,N,O,G)` runs — its `Goal` arg flows through
   `pj_do_succeed(Suite,Name,Goal) :- catch(Goal, _, _), !, ...`
3. `catch(Goal, _, _)` — Goal is a TT_VAR, lower_pl_goal builds a call(Goal)
   sub-graph (step 1), bb_exec.c dispatches via pl_call_term, test body
   actually runs

After both steps land, expect:
- All 9 SWI suites switch from EMPTY → real PASS/FAIL distribution
- .ref files need re-baselining accordingly
- New SWI-PASS counts probably drop somewhat from 57/57 (some tests will
  legitimately FAIL — we have known gaps in arithmetic, string ops, DCG, etc.)
- That's a HONEST gate number; the EMPTY-only 57/57 was a placeholder for
  "haven't started running tests yet"

---

## Empirical findings from this session worth remembering

1. **`catch(VAR, _, _)` inside a user predicate** silently wipes the predicate
   body in mode-2 — fixed in this commit.

2. **`once(USER_PRED(...))`** has the same root cause from a different angle:
   no BB-graph intercept for `once/1`. Step 2 above.

3. **Stale `libscrip_rt.so` masks fixes**: GATE-4 reported a regression
   that vanished after `make libscrip_rt`. Always run `make scrip` AND
   `make libscrip_rt` before GATE-4. (Worth adding to the goal file's
   session-setup checklist — currently it's there but easy to skip when
   only scrip code was touched.)

4. **My initial bb_exec.c edit narrowed `carity >= 1` to `carity == 1`**.
   Reverted in this session to keep gates stable. The corrected form (see
   step 2 above) preserves call/N for N>1 by combining with OR.

---

## Files touched

- `src/lower/lower_pl.c` (+23 lines, one new arm in `lower_pl_goal`)

No other files. No template changes. No FACT-RULE risk.

---

## Gates verified (post-fix, all byte-identical to predecessor `6c3d8703`)

| Gate | Count | Status |
|---|---|---|
| GATE-1 smoke | 5/5 | ✅ |
| GATE-2 crosscheck | 132/0 (5 ORACLE_MISS) | ✅ |
| GATE-3 mode-2 rung suite | 104/107 | ✅ |
| GATE-4 mode-4 minimal | 4/4 | ✅ |
| GATE-SWI plunit suite | 57/57 EMPTY (honest) | ✅ |
| BB-honest mode-3 | 128/0 | ✅ |
| FACT RULE grep | 0 violations | ✅ |
| smoke_icon | 5/5 | ✅ |
| smoke_raku | 5/5 | ✅ |
| smoke_snobol4 | 13/13 | ✅ |

GATE-SWI remains EMPTY because `once/1` step 2 hasn't landed; once it does,
the .ref files will need re-baselining.

---

## NEXT SESSION quickstart

```bash
# In bb_exec.c, around line 3270:
# Change the call/N intercept guard from:
#   if (carity >= 1 && strcmp(callee, "call") == 0) {
# to:
#   if ((carity >= 1 && strcmp(callee, "call") == 0) ||
#       (carity == 1 && strcmp(callee, "once") == 0)) {

# Then rebuild BOTH scrip and libscrip_rt:
cd /home/claude/SCRIP
make -j4 scrip && make libscrip_rt

# Verify call/N still works (this is the regression risk):
bash scripts/test_prolog_rung_suite.sh 2>&1 | grep -E 'rung33|TOTAL'
# Expect: rung33_bridge_callN_* PASS 5/5, total 104/107

# Verify once/1 fix unblocks plunit:
WRAP=$(mktemp /tmp/pl_wrap_XXXXXX.pl)
printf 'main :- run_tests.\n:- initialization(main).\n' > "$WRAP"
./scrip --interp /home/claude/corpus/programs/prolog/plunit.pl \
        /home/claude/corpus/programs/prolog/swi_tests/test_list.pl "$WRAP" \
        < /dev/null 2>/dev/null
# Expect: PASS memberchk (or FAIL memberchk with actual diagnostic),
#         NOT EMPTY memberchk

# Run full SWI suite to see new distribution:
bash scripts/test_prolog_swi_suite.sh

# Re-baseline .ref files for whatever the honest output now shows.
```

The expected real distribution depends on what our existing builtins handle.
A reasonable guess: some suites will PASS legitimately (simple cases like
test_list/memberchk, test_misc), some will FAIL (test_arith with bigints
we don't have, test_string with operators we lack), and a few might still
be EMPTY if their setup machinery hits other unimplemented features.
