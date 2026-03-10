# SNOBOL4-plus — Organization Plan & Handoff Document

> **For a new Claude session**: Read this file first to understand the full
> organization. Then read the PLAN.md in the specific repo you are working on.
> This file tracks cross-repo state, decisions, and outstanding work.

---

## What This Organization Is

Two people building SNOBOL4 for every platform:

**Lon Jones Cherryholmes** (LCherryholmes) — software developer
- SNOBOL4-jvm: full SNOBOL4/SPITBOL compiler + runtime → JVM bytecode (Clojure)
- SNOBOL4-python: SNOBOL4 pattern matching library for Python (PyPI: `SNOBOL4python`)
- SNOBOL4-csharp: SNOBOL4 pattern matching library for C#
- SNOBOL4: shared corpus — programs, libraries, grammars

**Jeffrey Cooper, M.D.** (jcooper0) — medical doctor
- SNOBOL4-dotnet: full SNOBOL4/SPITBOL compiler + runtime → .NET/MSIL (C#)

Mission: **SNOBOL4 everywhere. SNOBOL4 now.**

---

## Repository Index

| Repo | Language | Status | Branch | Tests |
|------|----------|--------|--------|-------|
| [SNOBOL4-dotnet](https://github.com/SNOBOL4-plus/SNOBOL4-dotnet) | C# / .NET | Active | `main` | 1,484 passing |
| [SNOBOL4-jvm](https://github.com/SNOBOL4-plus/SNOBOL4-jvm) | Clojure / JVM | Active | `main` | 2,033 / 4,417 assertions / 0 failures |
| [SNOBOL4-python](https://github.com/SNOBOL4-plus/SNOBOL4-python) | Python + C | Active | `main` | — |
| [SNOBOL4-csharp](https://github.com/SNOBOL4-plus/SNOBOL4-csharp) | C# | Active | `main` | 263 passing |
| [SNOBOL4](https://github.com/SNOBOL4-plus/SNOBOL4) | SNOBOL4 | Corpus | `main` | — |

---

## Quick Start — Each Repo

### SNOBOL4-dotnet
```bash
git clone https://github.com/SNOBOL4-plus/SNOBOL4-dotnet.git
cd SNOBOL4-dotnet
export PATH=$PATH:/usr/local/dotnet
dotnet build -c Release
dotnet test TestSnobol4/TestSnobol4.csproj -c Release
```

### SNOBOL4-jvm
```bash
git clone --recurse-submodules https://github.com/SNOBOL4-plus/SNOBOL4-jvm.git
cd SNOBOL4-jvm
# Install Leiningen if needed
lein test
```
Reference oracles (build from source — see SNOBOL4-jvm PLAN.md for instructions):
- `/usr/local/bin/spitbol` — SPITBOL v4.0f
- `/usr/local/bin/snobol4` — CSNOBOL4 2.3.3

### SNOBOL4-python
```bash
git clone https://github.com/SNOBOL4-plus/SNOBOL4-python.git
cd SNOBOL4-python
pip install -e ".[dev]"
pytest tests/
```
PyPI package: `pip install SNOBOL4python`

### SNOBOL4-csharp
```bash
git clone https://github.com/SNOBOL4-plus/SNOBOL4-csharp.git
cd SNOBOL4-csharp
dotnet build -c Debug src/SNOBOL4
dotnet test tests/SNOBOL4.Tests
```

### SNOBOL4 (corpus)
```bash
git clone https://github.com/SNOBOL4-plus/SNOBOL4.git
# Used as submodule in SNOBOL4-jvm at corpus/lon/
```

---

## Organization Setup Log

| Date | What Happened |
|------|---------------|
| 2026-03-09 | GitHub org `SNOBOL4-plus` created. Jeffrey (jcooper0) invited as member — **PENDING: must accept invitation and be promoted to Owner**. |
| 2026-03-09 | `SNOBOL4-plus/SNOBOL4-dotnet` created. All 6 branches mirrored from `jcooper0/Snobol4.Net`. Jeffrey's 3 post-branch commits cherry-picked onto `feature/msil-trace`. PAT token scrubbed from `MSIL_EMITTER_PLAN.md` via `git filter-repo`. Merged to `main` (193 commits). Default branch set to `main`. |
| 2026-03-10 | `SNOBOL4-plus/SNOBOL4` created and mirrored from `LCherryholmes/SNOBOL4`. |
| 2026-03-10 | `SNOBOL4-plus/SNOBOL4-jvm` created and mirrored from `LCherryholmes/SNOBOL4clojure`. Submodule URL updated from `LCherryholmes/SNOBOL4` → `SNOBOL4-plus/SNOBOL4`. |
| 2026-03-10 | `SNOBOL4-plus/SNOBOL4-python` created and mirrored. PyPI project URLs updated to org. Version bumped to 0.5.1. Trusted Publisher configured on PyPI for both old and new repo. |
| 2026-03-10 | `SNOBOL4-plus/SNOBOL4-csharp` created and mirrored. |
| 2026-03-10 | Personal repos `LCherryholmes/SNOBOL4`, `LCherryholmes/SNOBOL4python`, `LCherryholmes/SNOBOL4csharp`, `LCherryholmes/SNOBOL4clojure` **archived** (read-only). To be deleted in ~1 month. |
| 2026-03-10 | Org profile README written and published via `SNOBOL4-plus/.github`. |

---

## Outstanding Items

### Must Do
- [ ] Jeffrey accepts GitHub org invitation → Lon promotes jcooper0 to Owner at https://github.com/orgs/SNOBOL4-plus/people
- [ ] Verify SNOBOL4python 0.5.1 published successfully to PyPI (check Actions tab — wheels workflow)
- [ ] Remove old PyPI Trusted Publisher (`LCherryholmes/SNOBOL4python`) once 0.5.1 is confirmed live
- [ ] Write individual repo READMEs for all five repos
- [ ] Delete four archived personal repos in ~1 month (after April 10, 2026)

### Next Development Work
- [ ] SNOBOL4-jvm Sprint 23E: inline EVAL! in JVM codegen to eliminate arithmetic bottleneck
- [ ] SNOBOL4-dotnet: production-readiness pass, remaining known failures
- [ ] SNOBOL4-python / SNOBOL4-csharp: cross-validate pattern semantics against JVM implementation
- [ ] Build unified cross-platform test corpus (see ASSESSMENTS.md)

---

## Key Decisions (Permanent)

1. **Canonical repos are in the org.** Personal repos are archived and will be deleted.
2. **All default branches are `main`.**
3. **SNOBOL4-jvm submodule** points to `SNOBOL4-plus/SNOBOL4` (not the personal repo).
4. **PyPI publishes from `SNOBOL4-plus/SNOBOL4-python`** via Trusted Publisher (OIDC, no token).
5. **Jeffrey's authorship is preserved.** His commit history is intact throughout.
6. **PLAN.md files stay in individual repos** for repo-specific operational detail. This file tracks org-level state only.

---

## Git Identity
```
user.name  = LCherryholmes
user.email = lcherryh@yahoo.com
```
Token: stored securely — do not commit. Request from user at session start if needed.
