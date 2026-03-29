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
| `corpus` | Test corpus — .sno/.icn/.pl + .ref oracle output | `/home/claude/corpus/` |
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
| **⚠ GRAND MASTER REORG** | G-9 s1 — M-G2-ICN-X64-GAP-FILL ✅ · M-G-EMIT-COVERAGE ✅ · emit-diff 493/0 | `6d8dd4b` one4all · .github pending | **run 7 invariants → M-G4-SHARED-OR → M-G2-MOVE-PROLOG-ASM-a/b → corpus migration** |
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

## G-9 Session 2 — Final state (2026-03-29, Claude Sonnet 4.6)

**one4all** `6d8dd4b` (no new commits — infrastructure session) · **.github** pending push

### Completed this session
- All oracles installed: CSNOBOL4 2.3.3, SPITBOL/x64, Icon 9.5.25a, SWI-Prolog 9.0.4, scrip-cc ✅
- M-G-INV-FAST ✅ — harness rewritten: persistent archive cache, batch jasmin, single SnoHarness JVM, parallel nasm. Harness now returns results within 240s.
- M-G-INV-TIMEOUT ✅ — five-layer timeout defence: per-binary (5s), SnoHarness per-class (3s), jasmin batch (60s), SnoHarness suite (120s), watchdog (300s). All 38 icon rung runners patched. START/FINISH/ELAPSED on all scripts.
- Emit-diff: **493/0** ✅ unchanged.

### Next session — read SESSIONS_ARCHIVE last entry only

1. **M-G-INV-FAST-X86-FIX** — fix snobol4_x86 LINK_FAIL (xargs subshell can't see exported bash function — rewrite dispatch to per-test mini-scripts). Do first, before any other work.
2. **Run 7 runtime invariants** gate checkpoint: `x86 106/106 · JVM 106/106 · .NET 110/110 · Icon x64 38-rung · Icon JVM 38-rung · Prolog x64 per-rung · Prolog JVM 31/31`
3. **M-G4-SHARED-OR** — E_OR wiring extractability audit (2-vs-3 backend)
4. **M-G2-MOVE-PROLOG-ASM-a/b** — split Prolog ASM out of emit_x64.c → emit_x64_prolog.c
5. **M-G0-CORPUS-AUDIT execution** — Icon rung migration one4all/test/ → corpus/

**Do not add content to PLAN.md beyond this section. Handoffs → SESSIONS_ARCHIVE.**
