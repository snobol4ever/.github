# MILESTONE-NET-SNOBOL4.md — SNOBOL4 × .NET Unified Milestone Ladder

**Session:** D · **Repo:** snobol4dotnet
**Team:** Lon Jones Cherryholmes (arch) · Jeffrey Cooper M.D. (.NET) · Claude Sonnet 4.6 (co-author)

---

## Milestone chain

| Milestone | Description | Gate |
|-----------|-------------|------|
| **M-NET-BEAUTY-19** | ⚠️ **NOW** — All 19 beauty drivers pass. B-BEAUTY-0 (FENCE redef) → B-BEAUTY-9 (ShiftReduce). Ladder in `MILESTONE-NET-BEAUTY-19.md`. Baseline: 7/19. | 19/19 pass |
| **M-NET-BEAUTY-SELF** | **NEXT** — beauty.sno self-beautifies: reads itself as INPUT, writes itself to OUTPUT, output matches input exactly. Gates on M-NET-BEAUTY-19. | output == input |
| **M-NET-INTERP-B01** | Captures: `@var` / `.var` / `$var` · Phase 3/5 boundary correct by construction | rung9 capture tests 100% vs SPITBOL |
| **M-NET-INTERP-B02** | Functions: DEFINE / RETURN / NRETURN / FRETURN / call stack | rung10 function tests pass |
| **M-NET-INTERP-B03** | EVAL / CODE: self-hosted runtime compiler · `BuildEval` / `BuildCode` · no Roslyn | rung10/1016_eval pass · CODE corpus pass |
| **M-NET-SNIPPETS** | Gimpel/corpus snippet test factory · fill all coverage gaps in `TestSnobol4/` | ≥ 2040 passed · 0 failed · crosscheck 80/80 |
| **M-NET-P35-FIX** | Fix @N Phase 3/5 capture clobber in `ThreadedExecuteLoop.cs` | crosscheck 80/80 · dotnet test ≥ 1911/1913 |
| **M-NET-PAT-CAPTURES** | Capture audit: `@/./$` vs SPITBOL oracle | rung9 100% vs SPITBOL |
| **M-NET-PAT-PRIMITIVES** | 16 pattern primitives vs SPITBOL oracle: LEN POS RPOS TAB RTAB REM ANY NOTANY SPAN BREAK BREAKX FENCE FAIL SUCCEED ABORT BAL | rung2–9 100% |
| **M-NET-EVAL-COMPLETE** | EVAL/CODE edge cases: pattern context · CODE across statement boundaries | rung10/1016_eval pass |
| **M-NET-NRETURN** | NRETURN lvalue-assign | rung10/1013 pass |
| **M-NET-OPT-CACHE** | Execution cache: cache compiled pattern graphs · avoid rebuild on repeat | ≥ 2× throughput on loop-heavy corpus |
| **M-NET-OPT-EMIT** | MSIL emission: hot paths → emitted IL delegates via `BuilderEmitMsil.cs` | selected corpus tests pass via emitted IL |
| **M-NET-OPT-FULL** | Full AOT IL emission · all corpus via emitted IL | 142/142 via emitted IL |
| **M-NET-SNOCONE** | Snocone self-test under snobol4dotnet | Snocone self-test ✅ |
| **M-NET-BOOTSTRAP** | snobol4dotnet runs beauty.sno end-to-end · full self-hosting | Self-hosting bootstrap ✅ |

---

## Sprint sequence

| Sprint | Milestone |
|--------|-----------|
| D-215 | M-NET-BEAUTY-19 ⚠️ NOW |
| D-216 | M-NET-BEAUTY-SELF |
| D-217 | M-NET-INTERP-B01 |
| D-218 | M-NET-INTERP-B02 |
| D-219 | M-NET-INTERP-B03 |
| D-220 | M-NET-SNIPPETS |
| D-221 | M-NET-P35-FIX + M-NET-PAT-CAPTURES |
| D-222 | M-NET-PAT-PRIMITIVES |
| D-223 | M-NET-EVAL-COMPLETE + M-NET-NRETURN |
| D-224 | M-NET-OPT-CACHE |
| D-225 | M-NET-OPT-EMIT |
| D-226 | M-NET-OPT-FULL |
| D-227 | M-NET-SNOCONE + M-NET-BOOTSTRAP |

---

*MILESTONE-NET-SNOBOL4.md — rewritten D-215, 2026-04-11, Claude Sonnet 4.6.*
*Flat ordered milestone list. No invented phases. Scoped to snobol4dotnet only.*
