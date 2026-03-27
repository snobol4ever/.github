# PLAN.md — snobol4ever HQ Plan

SNOBOL4/SPITBOL compilers targeting JVM, .NET, and native C.
**Team:** Lon Jones Cherryholmes (arch, MSIL), Jeffrey Cooper M.D. (DOTNET), Claude Sonnet 4.6 (TINY co-author, third developer).

---

## ⚡ NOW

Each concurrent session owns exactly one row. Update only your row. `git pull --rebase` before every push.

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **⚠ GRAND MASTER REORG** | G-7 — FRONTEND-PROLOG-JVM.md trimmed | `eb9f2ec` G-7 | M-G0-FREEZE (Lon schedules) |
| **⭐ Scrip Demo** | SD-37: M-SD-6 ✅ ICON-JVM sieve PASS; demos 7-10 ICON-JVM compiler gap | `795c2ff` SD-37 | M-SD-7 ICON-JVM |
| **TINY backend** | B-292 — 106/106 | `acbc71e` B-292 | M-BEAUTIFY-BOOTSTRAP-ASM-MONITOR |
| **TINY NET** | N-253 — M-LINK-NET-7 ✅ | `e7dc859` N-253 | M-LINK-NET-8 |
| **TINY JVM** | J-216 — STLIMIT/STCOUNT ✅ | `a74ccd8` J-216 | M-JVM-STLIMIT-STCOUNT |
| **TINY frontend** | F-223 | `b4507dc` F-223 | M-PROLOG-CORPUS |
| **DOTNET** | D-164 — 1903/1903 | `e1e4d9e` D-164 | TBD |
| **README** | R-2 | `00846d3` R-2 | M-README-DEEP-SCAN |
| **ICON x64** | IX-12 — rung01-03 confirmed ✅ baseline surveyed rung04-15 | `5b32daa` IX-12 | M-IX-STRING (fix `\|\|` concat segfault, rung04 100%) |
| **Prolog JVM** | PJ-84a — SWI bench 31/31 ✅ | `a79906e` PJ-84a | M-PJ-SWI-BASELINE |
| **Prolog x64** | PX-1 — probing, hello works, multi-clause broken | `a79906e` | M-PJ-X64-1 |
| **Icon JVM** | IJ-58 — snprintf→ij_gvar_field bulk ✅ list-arg obj-field ✅ bang-coerce WIP | `5b32daa` IJ-58 | M-IJ-JCON-HARNESS (VE 36→0) |
| **🔗 LINKER** | LP-6 — M-LINK-NET-7 ✅ | `e7dc859` LP-6 | M-LINK-NET-8 (ilasm/mono run) |
| **🔗 LINKER JVM** | LP-JVM-3 — demos 1-3 ✅ ICON-JVM via sno2c; M-SCRIP-DEMO WIP (family demo needs EXPORT directives + ByrdBoxLinkage.j) | `c3e3ab3` LP-JVM-3 | M-SCRIP-DEMO |

**Invariants:** TINY `106/106` · DOTNET `1903/1903`

---

## Routing: pick three → read three docs

**1. Repo**

| Repo | Doc |
|------|-----|
| snobol4x | `REPO-snobol4x.md` |
| snobol4jvm | `REPO-snobol4jvm.md` |
| snobol4dotnet | `REPO-snobol4dotnet.md` |

**2. Frontend × Backend → Session doc**

| | x64 ASM | JVM | .NET |
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
