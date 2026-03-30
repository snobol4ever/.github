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

**🔒 ALL SESSIONS FROZEN except Snocone x86 — Phase 3 naming (M-G3-NAME-*) still in progress. Do not unfreeze until all NAME-* milestones complete and invariants confirm clean.**

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **⚠ GRAND MASTER REORG** | G-9 s21 — Greek ports swept all emitters + generated output ✅; CSV reporting added ✅; invariant regression unresolved; M-G3-NAME-* scope = FULL identifier rename per ARCH-reorg-design.md §THE LAW | `d0e5ea1` one4all · `f8d139f` corpus · `.github` pending | **NEXT: run invariants → read `test-results/invariants_latest.csv` → separate pre-existing vs Greek regressions → M-G3-NAME-NET full pass (ALL identifiers, locals, labels, comments — not just ports)** |
| **Snocone x86** | SC-1 (new — unlocked) | — | first milestone — see `FRONTEND-SNOCONE.md` |
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

**Invariants (post-reorg baseline):** x86: SNOBOL4 `106/106` · Icon `38-rung` · Snocone `10/10` · Rebus `3/3` · Prolog per-rung PASS | JVM: SNOBOL4 `106/106` · Icon `38-rung` · Prolog `31/31` | .NET: SNOBOL4 `110/110` | DOTNET repo: `TBD — retest required` | snobol4jvm repo: `TBD — retest required`

**Gate:** emit-diff only — `CORPUS=/home/claude/corpus bash test/run_emit_check.sh` → expect **738/0**. Invariant suite retired as session gate (G-9 s18).

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

## G-9 Session 20 — Final state (2026-03-30, Claude Sonnet 4.6)

**one4all** `83fed63` · **.github** pending · **corpus** `8e8c134`

**⚠ SESSION HAD ERRORS — see SESSIONS_ARCHIVE correction entry.**

### Completed correctly this session
- SESSION_SETUP.sh bison/flex fix — `.github` `63a0894`
- JVM harness fix (`run_crosscheck_jvm_rung.sh` stdout→`-o`)
- JVM float format (`sno_fmt_double`), CONVERT integer/real/string, E_NAM value-context
- 33 JVM baselines regenerated. Gate: **738/0** ✅
- M-G7-STYLE-DOC ✅ — `doc/STYLE.md`
- M-G7-STYLE-BACKENDS/FRONTENDS/IR ✅ — `//` comments fixed

### Errors made this session
- Fired M-G7-UNFREEZE prematurely — Phase 3 (M-G3-NAME-*) not done
- Unfroze all sessions (re-frozen in correction commit `ce06593`)
- M-G7-UNFREEZE reverted in GRAND_MASTER_REORG.md

### Next session — read SESSIONS_ARCHIVE last entry only

**Do not add content to PLAN.md beyond this section. Handoffs → SESSIONS_ARCHIVE.**
