# HANDOFF — 2026-06-06 — Opus 4.8 — PASCAL-BB session 22

Three deliverables, all landed + pushed. Gate at close: **m2 49/1, m3 49/1, m4 49/1 — UNIFORM** over
50 probes (sole fail = recursion.pas, 16-bit maxint pin); SNOBOL smoke 19/0.

## 1. PB-10d — boolean assignment residue shapes (SCRIP `2419bb8`, corpus `92b2b88`)

Measured BEFORE fixing: `a[i] := relop` and `p^.f := relop` ALREADY GREEN all modes — the LOWER call
rewrites (arr_set_pure / __pas_field_set) put the pas_bool diamond in call-arg position, covered by
PB-10b's marshal arm; the s20/s21 residue claim was stale. Pinned by boolidx.pas + boolptr.pas. The
live bug was `funcname := relop` only: lower.c:754 normalizes a bare-funcname selector (TT_FNC, n==1)
to IR_ASSIGN(name) with the RHS lowered INLINE — same IR as `var := relop`, so it missed PB-10c's
parser rewrite; m3/m4 emitted whichever single literal the assign's α pointed at (boolfn `0 0` vs
oracle `1 0`), m2 correct. Fix (pascal.y only + direct bison regen): the `assignment:` statement-IF
rewrite accepts the bare-funcname selector alongside TT_VAR; else-arm rebuilds a fresh TT_FNC(name)
node (never reuse $1 twice). Zero lower/emitter changes. Byte-identity 4/4 incl. recursion.s (proves
the non-relop funcname path untouched).

## 2. GOAL prune — Lon directive (.github `81d9be09`)

GOAL-PASCAL-BB.md **25.7KB → 8.5KB (−66%)**: completed rungs PB-0..10d, session 20/21 watermark
essays, and the closed LB ladder DELETED — git history + prior handoffs hold them. Kept terse: FACT
RULE, current state/NEXT/residues, mechanism inventory ("how it works NOW"), P4 dialect bounds,
provenance guardrail, invariants, paths, executable Session Setup + gate shape, the six landmines.
PLAN.md Pascal row → one-line pointer (house style). NOT touched, flagged for grand master reorg:
RULES.md (FACT RULES carry exact completion-test greps other sessions enforce), GOAL-ICON-BB.md +
REPO-SCRIP.md (owned by concurrently active sessions).

## 3. PB-11 — case statement (SCRIP `046bfe1`, corpus `24babd7`)

Sources read first: pascalp.y `case_statement` production; pcom.pas casestatement (labels → xjp jump
table; in-range gaps → `ujc`); oracle probe confirmed pint HALTS "value out of range" on no-match.
Mechanism: parse-time desugar, ZERO new IR — `case e of …` → TT_SEQ_EXPR(`__pctN := e`, if-chain),
arms `TT_IF(pas_cond(or-chain of __pctN = const), stmt)` folded right-to-left into else slots;
multi-label = TT_ADD of EQ diamonds (the boolchain-proven shape, all modes); depth-8 temp stack for
nested cases, strdup'd temp names per leaf (leaf_s does NOT copy), counter reset per parse; labels =
folded integer constants only (true/false/char labels out of v1 scope — scalar_constant folds them to
0). Probes case1 (loop-driven, multi-label) + case2 (case in function, expression selector, funcname
arms). NEW RESIDUE: no-match silently continues vs pint's halt — an error trap is runtime work,
outside parser scope; in the goal RESIDUES list.

## Gotchas (carry forward)

1. Concurrent-push tax confirmed ×2 this session (BB-FIXUP bb_retract_throw, bb_succ_plus): every
   `git pull --rebase` → `rm -f scrip && make` → FULL 3-mode gate re-run. Both held.
2. All six standing landmines re-confirmed; they live in the pruned goal file's Landmines section.
3. Suite runner still has no checked-in script — the exact shape is in the goal's Session Setup.

## Next (Lon picks)

(a) `goto` — the last TT_SUCCEED stub; needs IR landing pads (SNOBOL-label style), a real rung.
(b) the 16-bit maxint rung for recursion.pas. (c) documented residues (operand-order under side
effects; `__pbt`/`__pct` recursion clobber; case no-match trap) if a probe ever forces them.
