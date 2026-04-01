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
grep "^## " /home/claude/.github/RULES.md            # scan headers, cat only relevant sections
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
| **GRAND MASTER REORG** | G-10 s1 | .github `f14c42a` | GRAND_MASTER_REORG_2.md committed — plan official. G-11: wait for all sessions to land current milestone (Phase 0 gate), then call freeze. |
| **⭐ DYNAMIC BYRD BOX** | DYN-7 partial — M-DYN-6 🔧 | one4all `c4bc4ba` DYN-7 | **M-DYN-6** (next): wire CODE builtin + EVAL_fn arithmetic path + f13 corpus gate. eval_code.c done, rung7 8/8. See SESSIONS_ARCHIVE DYN-7. |
| **Snocone x86** | SC-11 | `dbad62b` one4all · `327ed02` corpus | M-SC-B07 done · compound-assign fix in snocone_parse.c · rungB07 7/7 · **SC-12**: identify next unimplemented construct |
| ~~**SNOBOL4 WASM**~~ | ⛔ PARKED SW-17 | `fdcd636` one4all | WASM suspended — see MILESTONE_ARCHIVE.md |
| ~~**ICON WASM**~~ | ⛔ PARKED IW-17 | `4d6cb2d` one4all | WASM suspended — see MILESTONE_ARCHIVE.md |
| ~~**Prolog WASM**~~ | ⛔ PARKED PW-17 | `48461c7` one4all | WASM suspended — see MILESTONE_ARCHIVE.md |
| **SNOBOL4 JS** | SJ-2 | — | **M-SJ-A01**: emit_js.c + sno_runtime.js + run_js.js + Makefile wire. Dispatch: `(uid<<2)|signal` integer switch (engine.c oracle). OUTPUT via Proxy. See SESSION-snobol4-js.md §DISPATCH. |
| **ICON JS** | IJJ-1 | — | **M-IJJ-A01** (after M-SJ-A01): emit_js_icon.c scaffold. Oracle: Proebsting paper + emit_jvm_icon.c. See MILESTONE-JS-ICON.md |
| **Prolog JS** | PJJ-1 | — | **M-PJJ-A01** (after M-SJ-A01): emit_js_prolog.c scaffold. Trail+unify runtime. Oracle: emit_jvm_prolog.c. See MILESTONE-JS-PROLOG.md || **Icon JVM** IJ-58 · **Prolog JVM** PJ-84a · **Prolog x64** PX-1 · **ICON x64** IX-18 · **⭐ Scrip Demo** SD-37 · **🌳 Parser pair** PP-1 · **TINY backend** B-292 · **TINY NET** N-253 · **TINY JVM** J-216 · **TINY frontend** F-223 · **DOTNET** D-164 · **README** R-2 · **🔗 LINKER** LP-6 · **🔗 LINKER JVM** LP-JVM-3 | ← all unfrozen, resume | see SESSIONS_ARCHIVE for HEAD per session | read own SESSION-*.md for next action |

**Invariants (SC-9 baseline):** x86: SNOBOL4 `106/106` · Snocone `126p/0f` · Icon `95p/163f` · Prolog `13p/94f` | JVM: SNOBOL4 `94p/32f` · Icon `173p/44f` · Prolog `106p/1f` | .NET: `108p/2f` | WASM: SNOBOL4 `28p/1f`

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
| SNOBOL4 (WASM) | ⛔ PARKED | — | — |
| SNOBOL4 (JS) | `SESSION-snobol4-js.md` | `BACKEND-JS.md` | — |
| Icon (JS) | `SESSION-icon-js.md` | `BACKEND-JS.md` | — |
| Prolog (JS) | `SESSION-prolog-js.md` | `BACKEND-JS.md` | — |
| Rebus | `FRONTEND-REBUS.md` | — | — |

Special: `SCRIP_DEMOS.md` · `ARCH-scrip-abi.md` · `SESSION-linker-sprint1.md` · `SESSION-linker-net.md`

**3. Deep reference → ARCH-*.md** (open only when needed — catalog in `ARCH-index.md`)

---

*PLAN.md = routing + NOW only. 3KB max. No sprint content. No completed milestones.*
