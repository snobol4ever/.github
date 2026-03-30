# PLAN.md — snobol4ever HQ Plan

SNOBOL4/SPITBOL compilers targeting JVM, .NET, and native C.
**Team:** Lon Jones Cherryholmes (arch, MSIL), Jeffrey Cooper M.D. (DOTNET), Claude Sonnet 4.6 (co-author).

---

## ⛔ SESSION START — every session, no exceptions

**Step 1 — Setup (once per fresh environment):**
```bash
FRONTEND=x BACKEND=y TOKEN=ghp_xxx bash /home/claude/.github/SESSION_SETUP.sh
```
See `SETUP-tools.md` for FRONTEND/BACKEND values. Installs only needed tools.

**Step 2 — Gate:**
```bash
cd /home/claude/one4all
CORPUS=/home/claude/corpus bash test/run_emit_check.sh                   # expect 738/0+
CORPUS=/home/claude/corpus bash test/run_invariants.sh <your_cells>     # own backend only — see RULES.md
```

**Step 3 — Read in order:**
```
tail -120 /home/claude/.github/SESSIONS_ARCHIVE.md   # last handoff — FIRST
cat /home/claude/.github/RULES.md
cat /home/claude/.github/PLAN.md
```
Then read your SESSION-*.md (see Routing table below).

**Snocone × x86 additionally read:**
```
cat /home/claude/.github/SESSION-snocone-x64.md
```

---

## 9 Repos under github.com/snobol4ever

| Repo | Role | Clone path |
|------|------|------------|
| `.github` | HQ — PLAN, ARCH, SESSION, FRONTEND docs | `/home/claude/.github/` |
| `one4all` | Main compiler/runtime — 6 frontends × 4 backends, C | `/home/claude/one4all/` |
| `snobol4jvm` | SNOBOL4 → JVM, Clojure | `/home/claude/snobol4jvm/` |
| `snobol4dotnet` | SNOBOL4 → .NET, C# | `/home/claude/snobol4dotnet/` |
| `corpus` | Test corpus — .sno/.icn/.pl + .ref oracle output | `/home/claude/corpus/` |
| `harness` | Test infrastructure — corpus runners | `/home/claude/harness/` |

---

## ⚡ NOW

Each session owns exactly one row. Update only your row. `git pull --rebase` before every push.

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **GRAND MASTER REORG** | G-9 s28 | one4all `9b2fa58` · corpus `224d3d4` · .github this session | **M-G9-ICON-IR-WIRE** |
| **Snocone x86** | SC-2 | `95b2617` one4all · `5f5206d` corpus | M-SC-A14: rungA14 arith loops (2 tests) |
| **SNOBOL4 WASM** | SW-2 | `44ac687` one4all | **M-SW-A02: ARITHMETIC** rung4/ 5 tests — dispatch-loop block nesting fix needed |
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

**Invariants (post-reorg baseline, G-9 s22):** x86: SNOBOL4 `106/106` · Icon `94p/164f` · Prolog `13p/94f` | JVM: SNOBOL4 `94p/32f` · Icon `173p/44f` · Prolog `106p/1f` | .NET: `108p/2f` | WASM: SNOBOL4 `4/4`

**Gate:** Emit-diff **738/0**. Targeted invariants per RULES.md gate section.

---

## Routing: pick three → read three docs

**1. Repo** → `REPO-one4all.md` / `REPO-snobol4jvm.md` / `REPO-snobol4dotnet.md`

**2. Frontend × Backend → Session doc**

| | x86 | JVM | .NET |
|--|:---:|:---:|:----:|
| SNOBOL4 | `SESSION-snobol4-x64.md` | `SESSION-snobol4-jvm.md` | `SESSION-snobol4-net.md` |
| Icon | `SESSION-icon-x64.md` | `SESSION-icon-jvm.md` | — |
| Prolog | `SESSION-prolog-x64.md` | `SESSION-prolog-jvm.md` | — |
| Snocone | `SESSION-snocone-x64.md` | — | — |
| SNOBOL4 (WASM) | `SESSION-snobol4-wasm.md` | `BACKEND-WASM.md` | — |
| Rebus | `FRONTEND-REBUS.md` | — | — |

Special: `SCRIP_DEMOS.md` · `ARCH-scrip-abi.md` · `SESSION-linker-sprint1.md` · `SESSION-linker-net.md`

**3. Deep reference → ARCH-*.md** (open only when needed — catalog in `ARCH-index.md`)

---

*PLAN.md = routing + NOW only. 3KB max. No sprint content. No completed milestones.*

---

## G-9 Session 24 — Completed (2026-03-30, Claude Sonnet 4.6)

**one4all** `acda30b` · **corpus** `8db2d44` · **.github** this session

### Completed
- M-G7-UNFREEZE ✅ — `post-reorg-baseline-2` tagged + pushed
- M-G9-ALIAS-CLEANUP ✅ — all 13 IR_COMPAT_ALIASES replaced with canonical EKind; `#define IR_COMPAT_ALIASES` removed from scrip_cc.h; grep src/backend/ = 0 hits; 738/0; baseline invariants confirmed

**Do not add content to PLAN.md beyond this section. Handoffs → SESSIONS_ARCHIVE.**

## G-9 Session 27 — Completed (2026-03-30, Claude Sonnet 4.6)

**one4all** `29c836f` · **corpus** `7d3cfa2` · **.github** this session

### Completed
- Corpus icon `.s` baselines updated (stale from G3–G6 cset externs) — gate 738/0 ✅
- `icn_random(long n)` added to `icon_runtime.c` — G2 runtime prerequisite ✅
- Invariants confirmed: x86 SNOBOL4 `106/106` ✅ · Icon `94p/164f` · Prolog `13p/94f`

**Do not add content to PLAN.md beyond this section. Handoffs → SESSIONS_ARCHIVE.**

## G-9 Session 28 — Completed (2026-03-30, Claude Sonnet 4.6)

**one4all** `9b2fa58` · **corpus** `224d3d4` · **.github** this session

### Completed
- **icn_random no-libc fix** ✅ — replaced `rand()`/`srand()`/`time()` (broken under `-nostdlib`) with pure LCG seeded from stack pointer. Restored icon_x86 invariants 23p/235f → 94p/164f.
- **M-G5-LOWER-ICON-FIX G1** ✅ — `ICN_POS`: identity passthrough both backends
- **M-G5-LOWER-ICON-FIX G2** ✅ — `ICN_RANDOM`: `emit_random()` x64 + `emit_jvm_icon_random()` + `icn_builtin_random(J)J` Jasmin method JVM
- **M-G5-LOWER-ICON-FIX G7** ✅ — `ICN_SCAN_AUGOP`: explicit stub-fail both backends
- **M-G5-LOWER-ICON-FIX complete** ✅ — all G1–G7 cases done
- **bison/flex purged** ✅ — SESSION_SETUP.sh, RULES.md, SETUP-tools.md, SESSION-snocone-x64.md updated; rebus Makefile guarded; generated files freshened and committed
- Gate: **738/0** ✅ · Invariants: SNOBOL4 `106/106` ✅ · Icon `94p/164f` · Prolog `13p/94f`

**Do not add content to PLAN.md beyond this section. Handoffs → SESSIONS_ARCHIVE.**
