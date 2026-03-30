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
| **GRAND MASTER REORG** | G-9 s27 | one4all `29c836f` · corpus `7d3cfa2` · .github this session | **M-G5-LOWER-ICON-FIX** G2/G1/G7 emitter cases remaining → then **M-G9-ICON-IR-WIRE** |
| **Snocone x86** | SC-2 | `3f5da0f` one4all · `080d51a` corpus | M-SC-A10: rungA10 capture (goto-free) |
| **SNOBOL4 WASM** | SW-1 | `36af87e` one4all · `62f2d8f` corpus | M-SW-A01: HELLO (3/4 — literals str→int coerce needed) |
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

**Invariants (post-reorg baseline, G-9 s22):** x86: SNOBOL4 `106/106` · Icon `94p/164f` · Prolog `13p/94f` | JVM: SNOBOL4 `94p/32f` · Icon `173p/44f` · Prolog `106p/1f` | .NET: `108p/2f`

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
