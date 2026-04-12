# GOAL-NET-DATATYPE-LOWERCASE — Enforce snobol4dotnet DATATYPE always returns lowercase

**Repo:** snobol4dotnet
**Done when:** DATATYPE() is confirmed lowercase for all builtin types; rule is tested;
no code path exists that returns uppercase from DATATYPE in snobol4dotnet.

## Why

Session 4 attempted to uppercase DATATYPE to match the SPITBOL manual ("upper-case string").
This broke 59 unit tests and was reverted. The architecture is intentional:
snobol4dotnet returns lowercase from DATATYPE() for all builtin types.
The SPITBOL manual describes SPITBOL's behavior; snobol4dotnet is a separate runtime
with its own defined behavior. See RULES.md: "snobol4dotnet DATATYPE always lowercase."

## Steps

- [ ] **S-1** — Add a unit test that explicitly asserts DATATYPE returns lowercase for every
      builtin type: string, integer, pattern, array, table, name, code, expression.
      Gate: new test passes; no existing test broken.

- [ ] **S-2** — Audit all ConversionStrategy files to confirm each `GetDataType()` returns
      a lowercase literal. Document any that use `ToLower` vs hardcoded string.
      Files to check: StringConversionStrategy, IntegerConversionStrategy,
      PatternConversionStrategy, ArrayConversionStrategy, TableConversionStrategy,
      NameConversionStrategy, CodeConversionStrategy, ExpressionConversionStrategy.
      Gate: all return lowercase literals or `.ToLowerInvariant()` — never `.ToUpperInvariant()`.

- [ ] **S-3** — Ensure DataType.cs `GetDataType()` does NOT apply any case transformation —
      it returns `arg.DataType()` directly. Gate: one-line body, no ToUpper/ToLower in DataType.cs.
