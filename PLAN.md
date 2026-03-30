# PLAN.md — snobol4ever HQ Plan

SNOBOL4/SPITBOL compilers targeting JVM, .NET, and native C.
**Team:** Lon Jones Cherryholmes (arch, MSIL), Jeffrey Cooper M.D. (DOTNET), Claude Sonnet 4.6 (TINY co-author, third developer).

---

## ⛔ SESSION START — Run these two commands first, every session, no exceptions

**Step 1 — Setup (tools + repos + build). Run once per fresh environment:**
```bash
TOKEN=ghp_xxx bash /home/claude/.github/SESSION_SETUP.sh
```
Clones repos, installs ALL tools via apt (nasm, gcc, libgc, java, mono, swipl, icont),
builds from source (CSNOBOL4, SPITBOL, scrip-cc), sets git identity. No tests run.

**Step 2 — Gate (emit-diff only). Run every session after setup:**
```bash
cd /home/claude/one4all
CORPUS=/home/claude/corpus bash test/run_emit_check.sh
```

**⚠ `run_invariants.sh` is RETIRED as a session gate.** Last full run: G-9 s18. Final counts recorded in `GRAND_MASTER_REORG.md` (M-G-INV-FAST-X86-FIX ✅). Do not run invariants at session start — emit-diff only going forward.

**Never pre-check or pre-install tools manually.** SESSION_SETUP.sh handles everything.
The test scripts verify tools are present but do NOT install — if they report a missing
tool, re-run SESSION_SETUP.sh.

**Gate run time:**
- `run_emit_check.sh` — emit-diff 493 files × 3 backends: **~8–12s**

After setup + gate, read in order:
```
tail -120 /home/claude/.github/SESSIONS_ARCHIVE.md   # last handoff — FIRST
cat /home/claude/.github/RULES.md                    # mandatory rules
cat /home/claude/.github/PLAN.md                     # NOW table + next milestone
cat /home/claude/.github/GRAND_MASTER_REORG.md       # phase detail
```

## 9 Repos under github.com/snobol4ever

| Repo | Role | Clone path |
|------|------|------------|
| `.github` | HQ — PLAN, ARCH, SESSION, FRONTEND docs | `/home/claude/.github/` |
| `one4all` | Main compiler/runtime — 6 frontends × 4 backends, C | `/home/claude/one4all/` |
| `snobol4jvm` | SNOBOL4 → JVM, Clojure | `/home/claude/snobol4jvm/` |
| `snobol4dotnet` → `snobol4net` | SNOBOL4 → .NET, C# (rename pending M-G9) | `/home/claude/snobol4dotnet/` |
| `corpus` | Test corpus — .sno/.icn/.pl + .ref oracle output | `/home/claude/corpus/` |
| `harness` | Test infrastructure — corpus runners | `/home/claude/harness/` |
| `snobol4python` | SNOBOL4 pattern library for Python | clone if needed |
| `snobol4csharp` | SNOBOL4 pattern library for C# | clone if needed |
| `snobol4artifact` | CPython extension | clone if needed |

---

## ⚡ NOW

Each concurrent session owns exactly one row. Update only your row. `git pull --rebase` before every push.

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **⚠ GRAND MASTER REORG** | G-9 s23 | `.github` pending | **M-G7-UNFREEZE** (execute this session — all NAME-* done) |
| **Snocone x86** | SC-1 design complete | `e874660` .github | M-SC-CONSOLIDATE: merge snocone_lower+cf → emit_x64_snocone.c; then add goto/break/continue; then corpus rungs A01–A05 |
| **⭐ Scrip Demo** | SD-37 `795c2ff` | — | resume — unfrozen |
| **🌳 Parser pair** | PP-1 `4b4d71a` | — | resume — unfrozen |
| **TINY backend** | B-292 `acbc71e` | — | resume — unfrozen |
| **TINY NET** | N-253 `e7dc859` | — | resume — unfrozen |
| **TINY JVM** | J-216 `a74ccd8` | — | resume — unfrozen |
| **TINY frontend** | F-223 `b4507dc` | — | resume — unfrozen |
| **DOTNET** | D-164 `e1e4d9e` | — | resume — unfrozen |
| **README** | R-2 `00846d3` | — | resume — unfrozen |
| **ICON x64** | IX-18 `c648df5` | — | resume — unfrozen |
| **Prolog JVM** | PJ-84a `a79906e` | — | resume — unfrozen |
| **Prolog x64** | PX-1 `a051367` | — | resume — unfrozen |
| **Icon JVM** | IJ-58 `5b32daa` | — | resume — unfrozen |
| **🔗 LINKER** | LP-6 `e7dc859` | — | resume — unfrozen |
| **🔗 LINKER JVM** | LP-JVM-3 `55d8655` | — | resume — unfrozen |

**Invariants (post-reorg baseline, G-9 s22):** x86: SNOBOL4 `106/106` · Icon `94p/164f` · Prolog `13p/94f` | JVM: SNOBOL4 `94p/32f` · Icon `173p/44f` · Prolog `106p/1f` | .NET: SNOBOL4 `108p/2f` — all failures pre-existing non-regressions.

**Gate:** emit-diff + targeted invariants — see RULES.md gate section. Emit-diff expects **738/0**.

---

## Routing: pick three → read three docs

**1. Repo**

| Repo | Doc |
|------|-----|
| one4all | `REPO-one4all.md` |
| snobol4jvm | `REPO-snobol4jvm.md` |
| snobol4dotnet | `REPO-snobol4dotnet.md` |

**2. Frontend × Backend → Session doc**

| | x86 | JVM | .NET |
|--|:-------:|:---:|:----:|
| SNOBOL4 | `SESSION-snobol4-x64.md` | `SESSION-snobol4-jvm.md` | `SESSION-snobol4-net.md` |
| Icon | `SESSION-icon-x64.md` | `SESSION-icon-jvm.md` | — |
| Prolog | `SESSION-prolog-x64.md` | `SESSION-prolog-jvm.md` | — |
| Snocone | `FRONTEND-SNOCONE.md` | — | — |
| Rebus | `FRONTEND-REBUS.md` | — | — |

Special: `SCRIP_DEMOS.md` (SD sessions) · `ARCH-snobol4-beauty-testing.md` (beauty sprint) · `ARCH-scrip-abi.md` + `SESSION-linker-sprint1.md` (LP-2 JVM) + `SESSION-linker-net.md` (LP-4 .NET)

**3. Deep reference → ARCH-*.md** (open only when needed — full catalog in `ARCH-index.md`)

---

*PLAN.md = routing + NOW only. 3KB max. No sprint content. No completed milestones.*

---

## G-9 Session 23 — Start (2026-03-30, Claude Sonnet 4.6)

**one4all** `b41dc8d` · **corpus** `8db2d44` · **.github** this session

### Agenda this session
- M-G7-UNFREEZE — tag post-reorg-baseline-2, unfreeze all sessions
- M-G3-ALIAS-CLEANUP — replace all compat alias names in backend switch cases with canonical EKind names
- M-G2-BACKEND-FLATTEN — remove one4all/src/backend/{x64,jvm,net,wasm} subfolders; all emit_*.c files live directly in src/backend/
- RULES.md updated — invariants reinstated with targeted-regression rule (per-backend column only mid-session; full suite at start/end)

**Do not add content to PLAN.md beyond this section. Handoffs → SESSIONS_ARCHIVE.**
