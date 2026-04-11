# MILESTONE-NET-SNOBOL4.md — snobol4dotnet Milestone Ladder

**Session:** D · **Repo:** snobol4ever/snobol4dotnet
**Team:** Lon Jones Cherryholmes (arch) · Jeffrey Cooper M.D. (.NET) · Claude Sonnet 4.6 (co-author)

---

## Milestone chain

| Milestone | Description | Gate |
|-----------|-------------|------|
| **M-NET-BEAUTY-19** | ⚠️ **NOW** — All 19 beauty drivers pass. B-BEAUTY-0 (FENCE redef) → B-BEAUTY-9 (ShiftReduce). Ladder in `MILESTONE-NET-BEAUTY-19.md`. Baseline: 7/19. | 19/19 pass |
| **M-NET-BEAUTY-SELF** | **NEXT** — beauty.sno self-beautifies: reads itself as INPUT, writes itself to OUTPUT, output matches input exactly. Gates on M-NET-BEAUTY-19. | output == input |
| **M-NET-SNIPPETS** | Gimpel/corpus snippet test factory · fill all coverage gaps in `TestSnobol4/` · `CorpusRef_GimpelBits.cs` etc. | ≥ 2040 passed · 0 failed · crosscheck 80/80 |
| **M-NET-P35-FIX** | Fix @N Phase 3/5 capture clobber in `ThreadedExecuteLoop.cs` | crosscheck 80/80 · dotnet test ≥ 1911/1913 |
| **M-NET-PAT-CAPTURES** | Capture audit: `@/./$` vs SPITBOL oracle | rung9 100% vs SPITBOL |
| **M-NET-PAT-PRIMITIVES** | 16 pattern primitives vs SPITBOL oracle: LEN POS RPOS TAB RTAB REM ANY NOTANY SPAN BREAK BREAKX FENCE FAIL SUCCEED ABORT BAL | rung2–9 100% · dotnet test 1913/1913 |
| **M-NET-EVAL-COMPLETE** | EVAL/CODE edge cases: pattern context · CODE across statement boundaries · AppendCompile jump patching | rung10/1016_eval pass · CODE corpus pass |
| **M-NET-NRETURN** | NRETURN lvalue-assign | rung10/1013 pass |
| **M-NET-SNOCONE** | Snocone self-test under snobol4dotnet | Snocone self-test ✅ |
| **M-NET-BOOTSTRAP** | snobol4dotnet compiles itself | Self-hosting bootstrap ✅ |

---

## Sprint sequence

| Sprint | Milestone |
|--------|-----------|
| D-178 | M-NET-P35-FIX + M-NET-PAT-CAPTURES |
| D-179 | M-NET-PAT-PRIMITIVES |
| D-180 | M-NET-EVAL-COMPLETE + M-NET-NRETURN |
| D-215 | M-NET-BEAUTY-19 ⚠️ NOW |
| D-216 | M-NET-BEAUTY-SELF |
| D-220 | M-NET-SNOCONE + M-NET-BOOTSTRAP |

---

*MILESTONE-NET-SNOBOL4.md — rewritten D-215, 2026-04-11, Claude Sonnet 4.6.*
*Scoped to snobol4ever/snobol4dotnet only. one4all/scrip-interp.cs milestones (Phases 0/A/B01-B03) live in MILESTONE-NET-INTERP.md.*
