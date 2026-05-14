# GOAL-NET-OPSYN-248 — Explore SPITBOL error 248 on OPSYN

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

**Repo:** corpus / snobol4dotnet
**Done when:** We understand exactly which OPSYN calls SPITBOL rejects with error 248,
document the rule, and ensure corpus tests cover it portably.

## Background

During NET-BEAUTY-SELF S-1 we discovered:
- `OPSYN('INPUT', 'input_')` — remapping a system I/O name → error 248 under SPITBOL (fatal)
- `OPSYN('input__', 'INPUT')` — aliasing INPUT to a new name → works under SPITBOL
- `OPSYN('INPUT', 'myInput')` in isolation → error 248 under SPITBOL
- SETEXIT does NOT trap error 248 — it is fatal regardless
- snobol4dotnet allows both forms freely

The fix applied to io.sno: guard with FENCE-as-pattern detector to skip OPSYN remap
under SPITBOL. But the general rule is not yet documented or tested.

## Questions to answer

1. Exactly which names does SPITBOL protect? INPUT, OUTPUT — what else?
   TERMINAL? ABORT? ARB? REM? LEN? SPAN? BREAK? NOTANY? ANY? TAB? RTAB? POS? RPOS?
2. Is the rule: "cannot OPSYN a name that is a keyword or system I/O variable"?
   Or: "cannot OPSYN any name whose DATATYPE is not 'undefined'"?
3. Does CSNOBOL4 have the same restriction?
4. Does snobol4dotnet need to enforce the same restriction (or stay permissive)?

## Steps

- [ ] **S-1** — Systematically test OPSYN(name, 'INPUT') and OPSYN('INPUT', name)
  for a range of system names under SPITBOL oracle. Document which succeed/fail.

- [ ] **S-2** — Test same set under snobol4dotnet and CSNOBOL4. Document differences.

- [ ] **S-3** — Add corpus crosscheck tests covering portable OPSYN usage.
  Tests must use the FENCE-guard pattern (or equivalent) to be portable.

- [ ] **S-4** — Decide: should snobol4dotnet enforce SPITBOL's error 248 restriction?
  If yes: implement. If no: document as intentional divergence in REPO file.

## Rules

- Test gate: dotnet 18/18 beauty, 79/80 crosscheck before any commit.
- Commit as `LCherryholmes` / `lcherryh@yahoo.com`.
- See RULES.md for full rules.
