# snobol4ever — HQ

SNOBOL4/SPITBOL compilers targeting JVM, .NET, and native C.
**Team:** Lon Jones Cherryholmes (arch, MSIL), Jeffrey Cooper M.D. (DOTNET), Claude Sonnet 4.6 (TINY co-author, third developer).

---

## ⚡ NOW

Each concurrent session owns exactly one row. Update only your row. `git pull --rebase` before every push.

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
<<<<<<< HEAD
| **⚠ GRAND MASTER REORG** | G-7 — FRONTEND-PROLOG-JVM.md trimmed 12KB→4.6KB; §NOW bloat + Roadmap removed | `eb9f2ec` G-7 | M-G0-FREEZE (Lon schedules) |
| **⭐ Scrip Demo** | SD-26: M-SD-2 ✅ wordcount — SNO2C-JVM + ICON-JVM + PROLOG-JVM PASS | `de04f48` SD-26 | M-SD-3 |
| **TINY backend** | `main` B-292 — 106/106 | `acbc71e` B-292 | M-BEAUTIFY-BOOTSTRAP-ASM-MONITOR |
| **TINY NET** | `net-t2` N-248 — 110/110 | `425921a` N-248 | M-T2-FULL |
| **TINY JVM** | `main` J-216 — STLIMIT/STCOUNT ✅ | `a74ccd8` J-216 | M-JVM-STLIMIT-STCOUNT |
| **TINY frontend** | `main` F-223 — see TINY.md | `b4507dc` F-223 | M-PROLOG-CORPUS |
| **DOTNET** | `main` D-164 — 1903/1903 | `e1e4d9e` D-164 | TBD |
| **README** | `main` R-2 | `00846d3` | M-README-DEEP-SCAN |
| **ICON frontend** | `main` I-11 — rung03 ✅ | `bab5664` I-11 | M-ICON-STRING |
| **Prolog JVM** | `main` PJ-76 — 8 plunit bugs fixed; SWI baseline partial | `d6c63ad` PJ-76 | M-PJ-SWI-BASELINE |
| **Icon JVM** | `main` IJ-57 — M-IJ-JCON-HARNESS 🔄 rung36 0/51 pass; 0 CE; all compile+reach JVM; VerifyError from missing emit stubs | `14400a9` IJ-57 | M-IJ-JCON-HARNESS |
=======
| **⚠ GRAND MASTER REORG** | G-7 — FRONTEND-PROLOG-JVM.md trimmed | `eb9f2ec` G-7 | M-G0-FREEZE (Lon schedules) |
| **⭐ Scrip Demo** | SD-27: M-SD-3 🔄 roman — 5/6 PASS; ICON-JVM list subscript VerifyError | `51e38fc` SD-27 | M-SD-3 |
| **TINY backend** | B-292 — 106/106 | `acbc71e` B-292 | M-BEAUTIFY-BOOTSTRAP-ASM-MONITOR |
| **TINY NET** | N-248 — 110/110 | `425921a` N-248 | M-T2-FULL |
| **TINY JVM** | J-216 — STLIMIT/STCOUNT ✅ | `a74ccd8` J-216 | M-JVM-STLIMIT-STCOUNT |
| **TINY frontend** | F-223 — see REPO-snobol4x.md | `b4507dc` F-223 | M-PROLOG-CORPUS |
| **DOTNET** | D-164 — 1903/1903 | `e1e4d9e` D-164 | TBD |
| **README** | R-2 | `00846d3` R-2 | M-README-DEEP-SCAN |
| **ICON x64** | I-11 — rung03 ✅ | `bab5664` I-11 | M-ICON-STRING |
| **Prolog JVM** | PJ-77a — corpus 30/30 | `b7b7aa7` PJ-76 | M-PJ-SWI-BASELINE |
| **Icon JVM** | IJ-56 — rung36 0/51; 38 CE | `52e575c` IJ-56 | M-IJ-JCON-HARNESS |
>>>>>>> ad7a4abb3dc12790abbb08ff7386c5c42d9567cf

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

Special: `SCRIP_DEMOS.md` (SD sessions) · `BEAUTY.md` (beauty sprint)

**3. Deep reference → ARCH-*.md** (open only when you hit something you don't understand)

---

*PLAN.md = routing + NOW only. 3KB max. No sprint content. No completed milestones.*
