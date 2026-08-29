# GOAL-NET-DATATYPE-LOWERCASE — Enforce snobol4dotnet DATATYPE always returns lowercase

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

**Repo:** snobol4dotnet
**Done when:** DATATYPE() is confirmed lowercase for all builtin types; rule is tested;
no code path exists that returns uppercase from DATATYPE in snobol4dotnet.

**Status: ✅ DONE, verified 2026-08-29 (seat16, `goal-files-major-consolidation` row).** All three gates
independently re-checked against the live `snobol4dotnet` repo (HEAD `80c828a3`), not trusted from an
earlier grading pass: S-3 confirmed by reading `Snobol4.Common/Runtime/Functions/Miscellaneous/DataType.cs`
directly — `GetDataType(Var arg) { return arg.DataType(); }`, exactly the one-line body the gate requires.
S-2 confirmed by grep — zero `ToUpper` hits across any `*ConversionStrategy.cs` file. S-1's *substance* is
met (not by one combined test, but by full per-type coverage) — `TestSnobol4/Function/Miscellaneous/
Datatype.cs` asserts a lowercase literal for every type this goal names (string/integer/pattern/array/
table/name/code/expression) plus extras (real, user-defined data); ran it for real
(`dotnet test --filter "FullyQualifiedName~Datatype"`), not just read: **29/29 PASS, 0 failed.**
⚠️ **One correction to this file's own "Why" section, found during verification:** its citation *"See
RULES.md: 'snobol4dotnet DATATYPE always lowercase.'"* does not resolve — that exact text (or any close
paraphrase) does not appear anywhere in `.github/RULES.md` today. Doesn't bear on whether the underlying
behavior is correct (independently verified above, not from that citation) — just flagging the dangling
pointer so nobody goes looking for a rule that isn't there.

## Why

Session 4 attempted to uppercase DATATYPE to match the SPITBOL manual ("upper-case string").
This broke 59 unit tests and was reverted. The architecture is intentional:
snobol4dotnet returns lowercase from DATATYPE() for all builtin types.
The SPITBOL manual describes SPITBOL's behavior; snobol4dotnet is a separate runtime
with its own defined behavior. (Citation below to RULES.md does not currently resolve — see the
verification note above; not chased further, the behavior itself is independently confirmed regardless.)
See RULES.md: "snobol4dotnet DATATYPE always lowercase."

## Steps

- [x] **S-1** — Add a unit test that explicitly asserts DATATYPE returns lowercase for every
      builtin type: string, integer, pattern, array, table, name, code, expression.
      Gate: new test passes; no existing test broken.
      **Verified 2026-08-29: `TestSnobol4/Function/Miscellaneous/Datatype.cs` covers all 8 named types
      (plus real + user-defined data); `dotnet test` run for real, 29/29 PASS.**

- [x] **S-2** — Audit all ConversionStrategy files to confirm each `GetDataType()` returns
      a lowercase literal. Document any that use `ToLower` vs hardcoded string.
      Files to check: StringConversionStrategy, IntegerConversionStrategy,
      PatternConversionStrategy, ArrayConversionStrategy, TableConversionStrategy,
      NameConversionStrategy, CodeConversionStrategy, ExpressionConversionStrategy.
      Gate: all return lowercase literals or `.ToLowerInvariant()` — never `.ToUpperInvariant()`.
      **Verified 2026-08-29: zero `ToUpper` hits across any `*ConversionStrategy.cs` file, fresh grep.**

- [x] **S-3** — Ensure DataType.cs `GetDataType()` does NOT apply any case transformation —
      it returns `arg.DataType()` directly. Gate: one-line body, no ToUpper/ToLower in DataType.cs.
      **Verified 2026-08-29: read the file directly — exactly `{ return arg.DataType(); }`.**
