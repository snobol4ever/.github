# FINDING 2026-07-19 (Claude Sonnet 4.6) — Snocone beauty suite: 0/20 → 11/20 via three LOWER-only changes

**Context.** Session picked up from the 2026-07-19 reconnect FINDING (Opus 4.8) which established
the true baseline: beauty suite 0/20 (all FATAL at GZ#5 subset boundary) and bucketed the
leverage order. This session drove three successive LOWER-only rungs in `lower_snobol4.c`,
verifying after each with build + SNOBOL4 smoke (7/7 hard gate) + Snocone smoke (5/5) + beauty
count. Nothing touched the emitter, templates, or runtime.

## Changes landed (SCRIP `f0f21b5d`)

All changes are in `src/lower/lower_snobol4.c`, Snocone-arm `sx_lower` only.
The mature SNOBOL4-arm code (and its `sno_lower_match` helper) is reused without modification.

### Rung 1 — TT_ASSIGN LHS forms (0→10 beauty)

Extended the Snocone-arm `TT_ASSIGN` case from TT_VAR-only to handle:
- `$name = e` (TT_INDIRECT) → `sx_nameval` + `IR_ASSIGN_VAR`
- `a[k] = e` (TT_IDX) → `sx_subscript_lv` + `IR_ASSIGN_VAR`
- `ITEM(a,k) = e` (TT_FNC/"ITEM") → same
- `f(o) = e` DATA-field accessor → `IR_FIELD_VAR` + `IR_ASSIGN_VAR`
- `&kw = e` (TT_KEYWORD) → `IR_CALL("SNO$KWSET")` + value
- Forward-declared `sno_lower_match` alongside existing `sx_subscript_lv` decl

Mirrors the SNOBOL4-arm constructions at lines 1638–1695 verbatim, adapted to the
Snocone arm's γ/ω/res threading.  SNOBOL4 crosscheck: 307/0/0 (unchanged).
Unblocked: ReadWrite, ShiftReduce, XDump, arith, assign, counter, global, stack, strings, tree.

### Rung 2 — TT_SCAN / subject ? pattern (10→11 beauty)

Added `case TT_SCAN:` in `sx_lower`, routing directly to `sno_lower_match(cx, t, NULL, 0, γ, ω)`.
Success threads to γ, failure to ω — exactly the right wiring for `if (subj ? pat) { ... }`.
The existing, proven SNOBOL4 pattern machinery handles all elements; zero new IR/emitter code.
Unblocked: match (the core pattern-matching subsystem, confirmed PASS).

### Rung 3 — match-replacement (no net beauty change, advanced case/Qize past old FATAL)

Added detection of `TT_ASSIGN(TT_SCAN(...), repl)` at the top of the TT_ASSIGN case.
Routes to `sno_lower_match(cx, L, R, 1, γ, ω)` (has_repl=1).
This is the `subject ? pattern = repl` form (e.g. `str ? BREAK(',') . tok ',' = ''`).
`case` and `Qize` both advanced past the TT_ASSIGN error and now hit the pattern-element
frontier (same as the 7-subsystem cluster below).

## Remaining 9 failures — precisely bucketed from measured output

### 7 subsystems: TT_FNC as a pattern element (Gen, Qize, TDump, case, fence, semantic, trace)

All hit `sno_pat_node` default FATAL with kind=45 (TT_FNC).
Root cause: a **bare function call used directly as a pattern element**, e.g. `? upr(letter)`.
SNOBOL4 eager semantics: evaluate the call, use the returned value as a pattern.

Two probes confirm the exact gap:
- `p = ('a' | upr(x)); if ('H' ? (p)) ...` → MATCH (works — pattern value stored in var, matched via IR_MATCH_DEFER)
- `if ('H' ? upr(x)) ...` → FATAL (bare TT_FNC in pattern position, no sno_pat_node case)

**Next rung:** in `sno_pat_node`, add a case for `TT_FNC` (and general value-expression)
that materializes the expression into a synthetic temp variable (`sx_lower` → `IR_ASSIGN`
on a fresh `PAT$TMP$N` name), then routes to `IR_MATCH_DEFER` on that temp name.
This reuses proven infrastructure end-to-end.  Likely flips most/all 7.

### 1 subsystem: TT_CAPT_CURSOR (omega)

Kind=44 (TT_CAPT_CURSOR, the `@` cursor-capture operator) in a pattern position.
A small separate element case in `sno_pat_node`.

### 1 subsystem: runtime divergence (roman)

No FATAL. `roman` lowers without error but produces wrong output vs the ref.
Per RULES.md: monitor-first bug-finding applies here (not a lowering add).
Has not been investigated this session.

## LIVE CURSOR

Next session: add `TT_FNC` (and general value-expr) case to `sno_pat_node` in
`lower_snobol4.c` — synthetic-temp materialization + `IR_MATCH_DEFER`. Expected to
flip Gen, Qize, TDump, case, fence, semantic, trace (7 more). Then TT_CAPT_CURSOR
(omega), then monitor-driven roman investigation.

Gate to run every step: `bash scripts/test_smoke_snobol4.sh` (7/7 hard gate) +
`bash scripts/test_smoke_snocone.sh` (5/5) + `bash scripts/test_beauty_snocone_subsystems.sh
Gen Qize ReadWrite ShiftReduce TDump XDump arith assign case counter fence global match omega
roman semantic stack strings trace tree`.
