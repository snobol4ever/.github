# FINDING: Pascal identifiers/keywords made case-insensitive per ISO 7185 / fpc -Miso oracle — scope established (reserved words + builtins + user identifiers, all via one lexer-level fix), landed, verified; magnitude on the vendored FPC suite corrected from the row's own framing (5-6 files, not "the majority" of 67)

## Fix
`src/parsers/pascal/pascal.l`: added `%option caseless` (makes every reserved-word/operator-keyword pattern — `program`, `begin`, `div`, `and`, etc., 34 total — match any casing) and lowercase the `IDENT` token's captured text at the lexer boundary (`pascal_lower_dup`, a new small helper; `STRINGCONST`'s own capture path is untouched, so string literal *content* is never case-folded). Canonicalizing identifiers to lowercase once, at the lexer, makes every downstream `strcmp` (builtin recognition in `pascal.y` — `writeln`/`write`/`read`/`readln`/etc. — and any user-identifier symbol-table lookup) case-insensitive for free; no other file needed to change. Regenerated `pascal.lex.c` via the project's standard flex recipe; `pascal.y`/`pascal.tab.c` untouched (grammar unaffected).

## Scope established BEFORE designing the cure, per the row's own explicit instruction
Verified all three categories in one pass, not assumed:
- **Reserved words** (`PROGRAM`/`VAR`/`BEGIN`/`END`/`IF`/`THEN`/`ELSE`, etc., any casing): correct.
- **Builtin procedures** (`writeln`/`WriteLn`/`Writeln`/`WRITELN`, the row's own DONE-WHEN witness): all four casings now `rc=0`, correct output — `ALL-CASINGS-ACCEPTED`.
- **User-defined identifiers across casings**: `MyVar`/`MYVAR2`/`myVar2` referencing the same declared variable in three different casings all resolve to one location (verified with a small witness combining declaration in one case, assignment in a second, read in a third — correct arithmetic result).

## SHARED-NODE CONTROL ARMS
Change is entirely confined to `src/parsers/pascal/pascal.l` (Pascal-frontend-only; does not even reach `lower`/IR, let alone anything shared) — `%option caseless` and the IDENT capture are pascal.l-local. Icon smoke: 14/14 both modes, unmoved. SNOBOL4 blocking set: [see task LEDGER for the fresh run — this file states the mechanism, not a moving number].

## MAGNITUDE — CORRECTED FROM THE ROW'S OWN FRAMING, MEASURED NOT ASSUMED
The row's GOAL text speculated this "single gap plausibly dominates a whole suite's red" (67 failures on the vendored FPC suite). **Measured true before/after on the identical tree** (stashed the fix, rebuilt, re-ran; popped, rebuilt, re-ran — not a comparison against an old cited baseline): **114→119 pass (m3 and m4 identically), 67→62 fail.** Diffing the exact failing-file lists (not just counts): **6 files newly pass** (`bench_shootout_src_hello`, `test_cg_tfor`, `test_testlderror`, `webtbs_tw0876`, `webtbs_tw2897`, `webtbs_tw4223` — spot-checked two of these for the expected mixed-case `WriteLn`/`Write` signature, confirmed present), **1 file newly fails** (`tbs_tb0169` — investigated fully, NOT a regression from this fix: full detail in `FINDING-2026-08-30-seat14-pascal-case-assign-inside-procedure-writes-wrong-location.md`, a separate, pre-existing, unrelated bug this fix's own progress unmasked, exactly the "a red that clears should be re-measured" pattern this project has hit repeatedly this session). Net: **+5 pass**, not "the majority of 67" — the remaining 61 failures are dominated by other causes, most visibly the already-known `-Miso`-rejects-`string`-identifier mode question this suite's own header comment names.

## NOT ATTEMPTED / OUT OF SCOPE
Did not investigate the other 61 remaining FPC-suite failures beyond confirming they are not case-signature failures by inspection of the fail list's composition (no further mixed-case builtin calls visible in a spot check of the remaining names). Did not touch `Halt` (confirmed unimplemented, see the companion FINDING) or the case-in-procedure defect (same FINDING) — both out of scope for this row.

## NEXT ACTOR
1. This row's own DONE-WHEN (the four-casing witness) passes; SHARED-NODE control arms clean. Worth a `done` once the SNOBOL4 blocking-set run is confirmed clean on this tree (fleet was mid-churn during this session's verification; re-run fresh if in doubt, per this project's own standing lesson).
2. The two newly-characterized bugs (`case`-in-procedure wrong-location write; `Halt` unimplemented) are real, separate findings with their own next-actor notes in their own FINDING file — do not conflate either with this row's own scope.
3. The remaining ~61 FPC-suite failures are NOT this row's scope (was never claimed to be) — `-Miso`/`string`-identifier mode question already named in `test_pascal_fpc_suite.sh`'s own header comment as a separate, open question.
