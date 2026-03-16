# DOTNET.md — SNOBOL4-dotnet (L2)

.NET/C# backend: SNOBOL4 → MSIL via GOTO-driven threaded bytecode runtime.

→ Backend reference: [BACKEND-NET.md](BACKEND-NET.md)
→ Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)

---

## NOW

**Sprint:** `net-delegates`
**HEAD:** `63bd297`
**Milestone:** M-NET-DELEGATES

**Next action:** Implement `net-delegates` in `ThreadedCodeCompiler.cs` — replace
`Instruction[]` storage with direct `Func<Executive, int>[]`. No intermediate objects.

---

## Session Start

```bash
cd SNOBOL4-dotnet
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
export PATH=$PATH:/usr/local/dotnet
git log --oneline -3   # verify HEAD
dotnet build Snobol4.sln -c Release -p:EnableWindowsTargeting=true
dotnet test TestSnobol4/TestSnobol4.csproj -c Release   # confirm 1607/0
```

**CRITICAL:** Always pass `-p:EnableWindowsTargeting=true` on Linux builds.

---

## Milestones

| ID | Trigger | Status |
|----|---------|--------|
| **M-NET-DELEGATES** | Instruction[] eliminated — pure Func<Executive,int>[] dispatch | ❌ |
| M-NET-SNOCONE | Snocone self-test: compile snocone.sc, diff oracle | ❌ |
| **M-NET-POLISH** | 106/106 corpus rungs pass · diag1 35/35 · benchmark grid published | ❌ |
| M-NET-BOOTSTRAP | snobol4-dotnet compiles itself | ❌ |

---

## Sprint Map

### Active → M-NET-DELEGATES

| Sprint | Status |
|--------|--------|
| `net-msil-scaffold` | ✅ |
| `net-msil-operators` | ✅ |
| `net-msil-gotos` | ✅ |
| `net-msil-collapse` | ✅ |
| **`net-delegates`** | ← active |

### → M-NET-SNOCONE

| Sprint | Status |
|--------|--------|
| `net-snocone-corpus` | ✅ `ab5f629` |
| `net-snocone-lexer` | ✅ `dfa0e5b` |
| `net-snocone-expr` | ✅ `63bd297` |
| `net-snocone-control` | ❌ |
| `net-snocone-selftest` | ❌ |

### → M-NET-POLISH (tested · full-featured · benchmarked)

Three tracks run in sequence: corpus coverage first, feature gaps second, benchmarks last.

| Sprint | What | Trigger |
|--------|------|---------|
| `net-corpus-rungs` | Run 106/106 crosscheck rungs 1–11 against DOTNET; fix all failures | 106/106 green |
| `net-diag1` | Run diag1 35-test suite (from SNOBOL4-corpus) against DOTNET; fix all failures | 35/35 green |
| `net-feature-audit` | Compare DOTNET feature coverage vs CSNOBOL4 ref: keywords, data types, built-ins, I/O, CODE()/EVAL() stubs | zero open gaps |
| `net-feature-fill` | Implement any missing features identified by audit (one sub-sprint per gap) | audit clean |
| `net-benchmark-scaffold` | Wire DOTNET into harness benchmark pipeline; collect DOTNET timing column | pipeline green |
| `net-benchmark-publish` | Run full benchmark grid (DOTNET vs CSNOBOL4 vs SPITBOL vs TINY); publish results in HARNESS.md | grid published |

**M-NET-POLISH fires when:** `net-corpus-rungs` ✅ + `net-diag1` ✅ + `net-feature-fill` ✅ + `net-benchmark-publish` ✅

---

## Pivot Log

| Date | What | Why |
|------|------|-----|
| 2026-03-10 | `net-delegates` declared active | Steps 1–13 complete, Step 14 next |
| 2026-03-16 | M-NET-POLISH added: 6 sprints (corpus → diag1 → feature-audit → feature-fill → benchmark-scaffold → benchmark-publish) | Explicit milestone to get DOTNET fully tested, full-featured, and benchmarked before bootstrap |
