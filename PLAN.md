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
CORPUS=/home/claude/corpus bash test/run_emit_check.sh                   # expect 981/4+
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
| **GRAND MASTER REORG** | G-9 s35 | one4all `388140a` · corpus `caa3903` | rung09 loops: icon_x86 103p/155f → next milestone |
| **Snocone x86** | SC-5 | `994a482` one4all · `bb835ca` corpus | M-SC-B05: `||` alternation (5 tests) |
| **SNOBOL4 WASM** | SW-10 | `8072122` one4all · `8c755d4` corpus | **M-SW-B06: POS/RPOS/LEN/TAB** rungW06/ 4 tests |
| **ICON WASM** | IW-9 | `2bc7a93` one4all | **M-IW-R01**: activation frame stack → rung02_proc_fact (120) |
| **Prolog WASM** | PW-12 | `8869d47` one4all | **M-PW-B01**: γ body-goal fns + GTSiteData done; β1 re-call needs secondary scratch cell for recursive list arg — see SESSIONS_ARCHIVE PW-12 |
| **Icon JVM** IJ-58 · **Prolog JVM** PJ-84a · **Prolog x64** PX-1 · **ICON x64** IX-18 · **⭐ Scrip Demo** SD-37 · **🌳 Parser pair** PP-1 · **TINY backend** B-292 · **TINY NET** N-253 · **TINY JVM** J-216 · **TINY frontend** F-223 · **DOTNET** D-164 · **README** R-2 · **🔗 LINKER** LP-6 · **🔗 LINKER JVM** LP-JVM-3 | ← all unfrozen, resume | see SESSIONS_ARCHIVE for HEAD per session | read own SESSION-*.md for next action |

**Invariants (G-9 s33 baseline):** x86: SNOBOL4 `106/106` · Snocone `116p/0f` · Icon `95p/163f` · Prolog `13p/94f` | JVM: SNOBOL4 `94p/32f` · Icon `173p/44f` · Prolog `106p/1f` | .NET: `108p/2f` | WASM: SNOBOL4 `28p/1f`

**Gate:** Emit-diff **981/4**. Targeted invariants per RULES.md gate section.

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
