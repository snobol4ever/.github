# GOAL-DATATYPE-PORTABLE-TESTS — Fix all DATATYPE case-hardcoded tests in corpus

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** corpus
**Done when:** No corpus `.sno` or `.inc` file contains `IDENT(DATATYPE(...), 'PATTERN')` or
any other hardcoded uppercase or lowercase DATATYPE string comparison.

## Why

RULES.md: "Any test that checks a DATATYPE result must be portable across case.
Do NOT hardcode IDENT(DATATYPE(x), 'string') or IDENT(DATATYPE(x), 'STRING')."

Session 4 found that `beauty_omega_driver.sno` and likely `beauty_semantic_driver.sno`
hardcode `'PATTERN'` (uppercase) in IDENT(DATATYPE(...)) checks. This makes them fail
on snobol4dotnet (lowercase) and would fail on SCRIP (uppercase — same issue, opposite case).
The `.ref` files baked from those broken drivers are also wrong and must be rebaked.

## Pattern for portable DATATYPE comparison

```snobol4
*  Derive type tokens once at program start — never hardcode case:
        dSTRING  = REPLACE(DATATYPE(''),        &LCASE, &UCASE)
        dINTEGER = REPLACE(DATATYPE(0),         &LCASE, &UCASE)
        dPATTERN = REPLACE(DATATYPE(LEN(1)),    &LCASE, &UCASE)
        dARRAY   = REPLACE(DATATYPE(ARRAY(1)),  &LCASE, &UCASE)
        dTABLE   = REPLACE(DATATYPE(TABLE()),   &LCASE, &UCASE)
        dNAME    = REPLACE(DATATYPE(.x),        &LCASE, &UCASE)

*  Then compare uppercased:
        IDENT(REPLACE(DATATYPE(p1), &LCASE, &UCASE), dPATTERN)  :S(ok)F(fail)
```

## Steps

- [ ] **S-1** — Audit all corpus `.sno` and `.inc` files for hardcoded DATATYPE string
      comparisons. Command: `grep -rn "IDENT.*DATATYPE\|DATATYPE.*IDENT" corpus/programs/`
      Gate: list of all violating files produced.

- [ ] **S-2** — Fix `beauty_omega_driver.sno`: rewrite all IDENT(DATATYPE(x), 'PATTERN')
      checks to use case-portable form. Rebake `beauty_omega_driver.ref` by running under
      snobol4dotnet after the *LEQ dispatch bug (BEAUTY-19 S-8B) is fixed.
      Gate: omega driver passes on snobol4dotnet.

- [ ] **S-3** — Fix `beauty_semantic_driver.sno` if it has the same issue.
      Rebake `.ref`. Gate: semantic driver passes.

- [ ] **S-4** — Fix any remaining corpus files found in S-1.
      Gate: `grep -rn "IDENT.*DATATYPE\|DATATYPE.*IDENT" corpus/programs/` finds only
      portable comparisons (no bare string literals like `'PATTERN'`, `'string'`, etc.).
