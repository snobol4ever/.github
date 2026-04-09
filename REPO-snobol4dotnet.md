# REPO-snobol4dotnet.md

Jeff Cooper's complete SNOBOL4/SPITBOL runtime in C#. Compiler pipeline, threaded
execution, MSIL delegate JIT, pattern engine, plugin system. Polish → beta release.

→ Backend reference: [INTERP-NET.md](INTERP-NET.md)
→ Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `D-187` — M-NET-SNIPPET-FACTORY: systematic snippet factory — Step 0 fix GimpelBits; Steps 1–8 add Strings/Capture/Data/LibMath/LibStack/LibString/GimpelBits2/Feat → ≥2100p
**HEAD:** `bdc541f` D-185
**Invariant:** `dotnet test` → 2008 passed, 11 failed, 1 skipped before any work
**Milestone:** D-185 partial — 64 new tests added (54 pass); ASGNIC fix written but 099 still failing (DATATYPE casing)

**⚠ CRITICAL NEXT ACTION — Session D-185:**

```bash
cd /home/claude/snobol4dotnet
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git pull --rebase
git log --oneline -3   # verify HEAD = 20c34e9 D-184
apt-get install -y dotnet-sdk-10.0
dotnet build TestSnobol4/TestSnobol4.csproj -c Release -p:EnableWindowsTargeting=true
dotnet test TestSnobol4/TestSnobol4.csproj -c Release -p:EnableWindowsTargeting=true --no-build
# Expect 1954 passed, 0 failed, 2 skipped

# ASGNIC BUG (099_keyword_rw):
# &ANCHOR = '0'  →  error 208 "keyword value assigned is not integer"
# Fix: in Assign(), when leftVar.IsKeyword and rightVar is StringVar,
# attempt Convert(VarType.INTEGER) before throwing error 208.
# File: Snobol4.Common/Runtime/Functions/OperatorsBinary/AssignReplace (=).cs
# Gate: TEST_Corpus_099_keyword_rw PASS → remove [Ignore]
#       crosscheck: 80/80 → 1955 passed, 0 failed, 1 skipped

# Crosscheck:
# DOTNET_REPO=/home/claude/snobol4dotnet CORPUS=/home/claude/corpus/crosscheck \
# DOTNET_ROOT=/usr/local/dotnet10 \
# bash /home/claude/harness/adapters/dotnet/run_crosscheck_dotnet.sh
# Currently: 79/80 (1 fail: 099_keyword_rw — ASGNIC coercion)
```

**CRITICAL:** `apt-get install -y dotnet-sdk-10.0`. Always `-p:EnableWindowsTargeting=true`.

---

## Sprint: net-polish (D-164 — next)

Next sprint: 106/106 corpus crosscheck via harness, diag1 35/35, benchmark grid → M-NET-POLISH.
See TESTING.md for corpus ladder and HARNESS.md for crosscheck scripts.

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

## Active Milestones

Full ladder: `MILESTONE-NET-SNOBOL4.md` — organized around 5-phase executor model.

| ID | Status | Notes |
|----|--------|-------|
| M-NET-PERF | ✅ | Hotfixes A–D confirmed; baseline published |
| M-NET-SPITBOL-SWITCHES | ✅ | 1911/1913 D-163 |
| M-NET-SNIPPET-FACTORY | ⚠️ | **CURRENT** — Systematic snippet factory: Step 0 fix GimpelBits bugs; Steps 1–8 add Strings/Capture/Data/LibMath/LibStack/LibString/GimpelBits2/Feat · doc: MILESTONE-NET-SNIPPET-FACTORY.md |
| M-NET-P35-FIX | ❌ | Fix @N Phase 3/5 capture → 80/80 crosscheck |
| M-NET-POLISH | ❌ | 106/106 + diag1 35/35 + benchmark grid |
| M-NET-PAT-CAPTURES | ❌ | @/./$var capture audit vs stmt_exec.c |
| M-NET-PAT-PRIMITIVES | ❌ | 16 pattern primitives vs SPITBOL oracle |
| M-NET-EVAL-COMPLETE | ❌ | EVAL/CODE edge cases + rung10/1016 |
| M-NET-NRETURN | ❌ | NRETURN lvalue (follow DYN-42 fix) |
| M-NET-SNOCONE | ❌ | Snocone self-test |
| M-NET-BOOTSTRAP | ❌ | Self-hosting bootstrap |
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

SPITBOL MINIMAL is authoritative.
Key semantics: DATATYPE builtins lowercase; user DATA types `ToLowerInvariant`;
`&UCASE`/`&LCASE` = exactly 26 ASCII letters; `@N` is **0-based** cursor position.
