# PLAN.md — snobol4ever HQ Plan

SNOBOL4/SPITBOL compilers targeting JVM, .NET, and native C.
**Team:** Lon Jones Cherryholmes (arch, MSIL), Jeffrey Cooper M.D. (DOTNET), Claude Sonnet 4.6 (TINY co-author, third developer).

---

## ⛔ SESSION START — Run this first, every session

```bash
TOKEN=ghp_xxx bash /home/claude/.github/SESSION_BOOTSTRAP.sh
```

Clones repos, installs tools, sets git identity, prints current milestone, runs all three invariants.
Script is self-contained. See RULES.md for the six things it covers.

## 9 Repos under github.com/snobol4ever

| Repo | Role | Clone path |
|------|------|------------|
| `.github` | HQ — PLAN, ARCH, SESSION, FRONTEND docs | `/home/claude/.github/` |
| `one4all` | Main compiler/runtime — 6 frontends × 4 backends, C | `/home/claude/one4all/` |
| `snobol4jvm` | SNOBOL4 → JVM, Clojure | `/home/claude/snobol4jvm/` |
| `snobol4dotnet` → `snobol4net` | SNOBOL4 → .NET, C# (rename pending M-G9) | `/home/claude/snobol4dotnet/` |
| `corpus` | Test corpus — .sno/.icn/.pro + .ref oracle output | `/home/claude/corpus/` |
| `harness` | Test infrastructure — corpus runners | `/home/claude/harness/` |
| `snobol4python` | SNOBOL4 pattern library for Python | clone if needed |
| `snobol4csharp` | SNOBOL4 pattern library for C# | clone if needed |
| `snobol4artifact` | CPython extension | clone if needed |

---

## ⚡ NOW

Each concurrent session owns exactly one row. Update only your row. `git pull --rebase` before every push.

**🔒 ALL SESSIONS FROZEN — Grand Master Reorganization in progress. Resume post M-G7-UNFREEZE.**

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **⚠ GRAND MASTER REORG** | G-8 — M-G-RENAME-REBRAND ✅ (all 4 repos MD sweep clean: Tiny-Icon→Icon, Tiny-Prolog→Prolog, one4all tagline fixed) | `cd25441` one4all · `e9158e9` .github · `43473ea` corpus | **M-G-INV-EMIT-FIX: run g8_session.sh → SIGSEGV fix → emit baseline → SESSION_BOOTSTRAP → M-G4-SHARED-CONC-SEQ** |
| **⭐ Scrip Demo** | [FROZEN SD-37 `795c2ff`] | — | resume post-reorg |
| **🌳 Parser pair** | [FROZEN PP-1 `4b4d71a`] | — | resume post-reorg |
| **TINY backend** | [FROZEN B-292 `acbc71e`] | — | resume post-reorg |
| **TINY NET** | [FROZEN N-253 `e7dc859`] | — | resume post-reorg |
| **TINY JVM** | [FROZEN J-216 `a74ccd8`] | — | resume post-reorg |
| **TINY frontend** | [FROZEN F-223 `b4507dc`] | — | resume post-reorg |
| **DOTNET** | [FROZEN D-164 `e1e4d9e`] | — | resume post-reorg |
| **README** | [FROZEN R-2 `00846d3`] | — | resume post-reorg |
| **ICON x64** | [FROZEN IX-18 `c648df5`] | — | resume post-reorg |
| **Prolog JVM** | [FROZEN PJ-84a `a79906e`] | — | resume post-reorg |
| **Prolog x64** | [FROZEN PX-1 `a051367`] | — | resume post-reorg |
| **Icon JVM** | [FROZEN IJ-58 `5b32daa`] | — | resume post-reorg |
| **🔗 LINKER** | [FROZEN LP-6 `e7dc859`] | — | resume post-reorg |
| **🔗 LINKER JVM** | [FROZEN LP-JVM-3 `55d8655`] | — | resume post-reorg |

**Invariants (frozen baseline):** x86: SNOBOL4 `106/106` · Icon `38-rung` · Snocone `10/10` · Rebus `3/3` · Prolog per-rung PASS | JVM: SNOBOL4 `106/106` · Icon `38-rung` · Prolog `31/31` | .NET: SNOBOL4 `110/110` | DOTNET repo: `TBD — retest required` | snobol4jvm repo: `TBD — retest required`

**Gate invariants (SESSION_BOOTSTRAP.sh — G-sessions run all nine):** 3×3 matrix: SNOBOL4/Icon/Prolog × x86/JVM/.NET. Icon .NET and Prolog .NET not yet implemented (SKIP). Seven active checks: x86 `106/106` · JVM `106/106` · .NET `110/110` · Icon x64 `38-rung` · Icon JVM `38-rung` · Prolog x64 per-rung PASS · Prolog JVM `31/31`. Expanded from three per G-7 session (M-G2-MOVE-PROLOG-ASM-b). Rationale: reorg touches all emitters.

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


## G-8 Handoff update (2026-03-29 session 6, Claude Sonnet 4.6)

### PLAN.md bloat cleared ✅
897 lines → 92 lines. All handoff content moved to SESSIONS_ARCHIVE.md.
RULES.md rule: handoffs go to SESSIONS_ARCHIVE, not PLAN.md.

### M-G-INV-EMIT-FIX ✅ (completed session 5 + this session)
- `run_emit_check.sh`: fixed stdout capture (`-o /dev/stdout`) and `-pl` flag for `.pro` files
- Prolog baselines were silently 0 bytes (vacuous pass) — regenerated with real content
- 488/0 emit-diff (up from 484: +4 new coverage test baselines)

### M-G5-EMITTER-COVERAGE-AUDIT ✅
Gap analysis complete across SNO/PL/ICN × x64/JVM/NET:
- **SNO**: no emitter gaps (E_NUL handled inline, not via switch)
- **PL/JVM**: E_CUT, E_TRAIL_MARK, E_TRAIL_UNWIND, E_UNIFY all handled via if/else — no gaps
- **PL/NET**: arithmetic (E_ADD/SUB/MPY/DIV), E_CUT, E_TRAIL_*, E_UNIFY not handled — stub emitter by design (no backtracking yet)
- **ICN/x64**: 34 ICN_ kinds missing from switch vs JVM
- **ICN/both**: ICN_COMPLEMENT, ICN_CSET_DIFF/INTER/UNION, ICN_POS, ICN_RANDOM, ICN_RECORD missing from both backends

### Coverage tests added
- `test/icon/coverage/coverage_x64_gaps.icn` — 129-line Icon test exercising all 34 x64-missing ICN_ kinds; compiles clean to x64 (22KB) and JVM (85KB)
- `test/prolog/coverage/coverage_net_gaps.pro` — 43-line Prolog test exercising E_ADD/SUB/MPY/DIV/FLIT/CUT/TRAIL/UNIFY; compiles clean to x64 (75KB), JVM (159KB), NET (19KB)
- Baselines committed alongside sources

### Next session
**Step 1** — Wire M-G-INV-EMIT-FIX into SESSION_BOOTSTRAP.sh (emit baseline guard uses wrong dir `test/emit_baseline` — should be `test/snobol4`)
**Step 2** — Commit all of the above, update NOW table
**Step 3** — M-G4-SHARED-CONC-FOLD

**Read only:** This handoff.
