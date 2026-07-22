# FINDING-2026-07-22-CLAUDE-ICN-CASE-ALT-SELECTOR-ALPHA-FORCE

**Status:** FIXED (lower_icon.c, TT_CASE) — Icon rung suite PASS=241 FAIL=20 XFAIL=32 (no regression).

## Symptom

SCRIP-jtran on any `.icn` file containing `if` or integer/real/string literals in multi-procedure
programs reported `File …; Line N # Expecting parse_expression` immediately after the first
operator token in a boolean expression (e.g. after `<` in `if n < 2 then`).

## Root Cause

A `case` expression whose **selector arm is a resumable alternation** (`case v of { a | b | c : body }`)
was being β-stamped (entered in *resume* mode) when the `case` was nested inside any enclosing
generator context (e.g. `every v := gen do case v of { … }`).  β-stamping means the alternation
generator is entered already-exhausted, so it immediately falls through to `default` — even the
first alternand never matches.

Minimal standalone repro (no jtran):
```icon
every v := 1 to 3 do
    case v of { 1 | 2 | 3 : write(v," MATCH") ; default : write(v," NOMATCH") }
```
Oracle → `1 MATCH 2 MATCH 3 MATCH`.  Pre-fix SCRIP → `1 NOMATCH 2 NOMATCH 3 NOMATCH`.

jtran's parser (`parse.icn`) dispatches primary expressions via exactly this pattern throughout:
```icon
case parse_tok_rec of {
    lex_INTLIT | lex_REALLIT | lex_STRINGLIT : return a_Intlit(…)   # line 217
    lex_IF : return parse_do_if()                                    # line 225
    …
```
8 such alternation arms in parse.icn alone.  Single-value arms (`lex_IF :`) always worked; only
alternation arms (`a | b | c :`) were broken when inside a generator context.

## Fix

`src/lower/lower_icon.c`, `TT_CASE` lowering (~line 546).  When the selector is resumable
(alternation), interpose an **α-forced `IR_GOTO` trampoline** so the selector enters fresh on each
case-evaluation.  Mirrors the body-α-FORCE at :541 and the `IR_GOTO` trampoline idiom at :842/:1128.
The mismatch-resume path (stepping through alternands via `kβ` at :545) is unchanged.

```c
// Before (one line):
chain_next = ke ? ke : idc;

// After (α-force trampoline for resumable selectors):
IR_t * ke_target = ke ? ke : idc;
if (ke && is_resumable(t->c[ki])) {  /* ICN-CASE-ALT SELECTOR α-FORCE */
    IR_t * KENT = build(cx, IR_GOTO, NULL, NULL);
    lc_γ_to_α(KENT, ke); lc_ω_to_α(KENT, ke);
    ke_target = KENT;
}
chain_next = ke_target;
```

**Both `make scrip` and `make libscrip_rt` must be rebuilt after this change.**

## Investigation Path (MONITOR-FIRST)

1. Reproduced blocker: SCRIP-jtran on `tA.icn` (`if 1<2 then write(1)`) → parse error.
2. Token-stream diff (instrumented yylex): oracle emits 14 tokens; SCRIP-jtran stops at token 8 (`2`).
3. Draining yylex *directly* (`: yylex`, no parser) → full 14-token stream.  ∴ lexer is correct;
   bug is in parser↔lexer interaction.
4. Instrumented `parse_eat_token` + `default` arm: at the error, `parse_tok_rec === lex_INTLIT` is
   TRUE, yet the case-alternation arm containing `lex_INTLIT` didn't fire.
5. Minimal probe without jtran/coexpr/scanning confirmed: alternation arms NOMATCH for all types
   (int, string, record) in generator context; single-value arms always correct.
6. Fixed value (`v := 2; case v of {1|2|3:…}`) → MATCH.  ∴ trigger is generator context, not
   alternation dispatch per se.  → β-stamp hypothesis → α-force fix → verified.

## Ruled Out

- Identity across coexpr boundary (probe: MATCH in both).
- Scan-env (`&subject`/`&pos`) corruption across coexpr (probe: MATCH in both, even with consumer
  scanning between resumes and with created-coexpr chains).
- Set/table membership of mutated records (probe: MATCH in both).

## Effect on Self-Host

Post-fix SCRIP-jtran **parses tA.icn and fib.icn without error** (`: yylex : parse` clean).
Frontier advances to **ast2ir**: `Illegal data type` appears when jtran's IR-generation stage
processes the parsed AST for `if`/multi-statement constructs.  Oracle does ast2ir cleanly.
This is the next blocker (JTRAN-ASTIR-ILLEGALTYPE).

## Cursor Update (GOAL-ICON-BB)

- Previous HEAD: `14d7c265` (name() builtin).
- This commit: ICN-CASE-ALT selector α-force fix.
- Icon rung suite: **241/20/32** (unchanged — zero regression).
- JTRAN-PARSE-MULTISTMT: **CLOSED** (this fix).
- JTRAN-ASTIR-ILLEGALTYPE: **OPEN** — new frontier, localized to `: yylex : parse : ast2ir`
  stage on `if`/compound-statement inputs.  Approach: MONITOR-FIRST, compare irgen execution
  between SCRIP-jtran and oracle on tA.icn.
