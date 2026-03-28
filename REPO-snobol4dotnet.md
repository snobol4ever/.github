# REPO-snobol4dotnet.md

Jeff Cooper's complete SNOBOL4/SPITBOL runtime in C#. Compiler pipeline, threaded
execution, MSIL delegate JIT, pattern engine, plugin system. Polish → beta release.

→ Backend reference: [BACKEND-NET.md](BACKEND-NET.md)
→ Testing: [ARCH-testing.md](ARCH-testing.md) · Rules: [RULES.md](RULES.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `net-polish` — fix `@N` bug → 80/80 crosscheck → diag1 35/35 → benchmark grid → M-NET-POLISH
**HEAD:** `dbdcba7` D-163
**Invariant:** `dotnet test` → 1911/1913 (2 skipped) before any work
**Milestone:** M-NET-SPITBOL-SWITCHES ✅ fired D-163

**⚠ CRITICAL NEXT ACTION — Session D-165:**

```bash
cd /home/claude/snobol4dotnet
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
export PATH=/usr/local/dotnet10:$PATH
git log --oneline -3   # verify HEAD = dbdcba7 D-163
dotnet test TestSnobol4/TestSnobol4.csproj -c Release -p:EnableWindowsTargeting=true
# Expect 1911/1913 — then fix @N bug

# @N BUG — diagnosed D-164:
# `X ? @N ANY('B')` gives N=0 when match is at cursor > 0.
# AtSign.Scan writes IdentifierTable["N"]=cursor correctly (verified by sentinel),
# but DUMP shows N=0 after statement. Something overwrites N after AtSign.Scan.
# Suspects: CheckGotoFailure opcode or statement post-match cleanup.
# Start: read ThreadedExecuteLoop.cs line 214+ (CheckGotoFailure),
#        read full opcode sequence for a pattern-match statement in Parser.cs,
#        find what writes IdentifierTable["N"]=0 after AtSign.Scan writes cursor.
# Fix → cross test PASS → 80/80 crosscheck → diag1 → benchmark → M-NET-POLISH.

# Crosscheck command:
# DOTNET_REPO=/home/claude/snobol4dotnet CORPUS=/home/claude/corpus/crosscheck \
# DOTNET_ROOT=/usr/local/dotnet10 \
# bash /home/claude/harness/adapters/dotnet/run_crosscheck_dotnet.sh
# Currently: 79/80 (1 fail: strings/cross — @N bug)
```

**CRITICAL:** .NET 10 SDK at `/usr/local/dotnet10`. Always `-p:EnableWindowsTargeting=true`.

---

## Sprint: net-polish (D-164 — next)

Next sprint: 106/106 corpus crosscheck via harness, diag1 35/35, benchmark grid → M-NET-POLISH.
See ARCH-testing.md for corpus ladder and ARCH-harness.md for crosscheck scripts.

## Completed: net-spitbol-switches (D-162)



---

## Last Session Summary

**Session D-164 — @N bug diagnosed (cross test, 79/80 crosscheck):**
- Ran crosscheck: 79/80 — only failure is `strings/cross` (`@N` cursor capture = 0 when should be > 0)
- Diagnosed: `X ? @N ANY('B')` — `AtSign.Scan` writes `IdentifierTable["N"]=cursor` correctly (write/readback verified), but `DUMP` shows N=0 after statement. Something overwrites N after `AtSign.Scan`. Suspects: `CheckGotoFailure` or statement post-match cleanup in `ThreadedExecuteLoop`. No code changes committed.

**Session D-162 — SPITBOL switches authored:**
- 11 new BuilderOptions properties; CommandLine.cs rewrite with k/m suffix parser
- `ApplyStartupOptions()` wires -e/-m; 26 unit tests in SpitbolSwitchTests.cs

---

## Active Milestones (next 5)

| ID | Status | Notes |
|----|--------|-------|
| M-NET-PERF | ✅ | Hotfixes A–D confirmed; baseline published |
| M-NET-SPITBOL-SWITCHES | ✅ | 1911/1913 D-163 |
| M-NET-POLISH | ❌ | 106/106 + diag1 35/35 + benchmark grid |
| M-NET-SNOCONE | ❌ | Snocone self-test |
| M-NET-BOOTSTRAP | ❌ | snobol4-dotnet compiles itself |

Full milestone history → [PLAN.md](PLAN.md)

---

## Performance Baseline (session159, post-hotfix A–D)

| Benchmark | Mean | Alloc/run |
|-----------|-----:|----------:|
| ArithLoop_1000 | 39.8ms | 1662 KB |
| VarAccess_2000 | 103.2ms | 6279 KB |
| Fibonacci_18 | 286.6ms | 11855 KB |
| MixedWorkload_200 | 223.2ms | 13928 KB |
| FuncCallOverhead_3000 | 40.6ms | 837 KB |

Full numbers → `perf/post_hotfix_session159.md`.

---

## SPITBOL Oracle Rule

When CSNOBOL4 and SPITBOL MINIMAL diverge: **SPITBOL MINIMAL wins.**
Key semantics: DATATYPE builtins lowercase; user DATA types `ToLowerInvariant`;
`&UCASE`/`&LCASE` = exactly 26 ASCII letters; `@N` is **0-based** cursor position.
