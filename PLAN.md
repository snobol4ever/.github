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
| **Snocone x86** | SC-9 | `086d340` one4all · `4a70276` corpus | M-SC-B08 ✅ · FOR step fix (depth-aware lexer) · snocone_x86 126/126 · **SC-10**: next unimplemented construct |
| **SNOBOL4 WASM** | SW-17 | `fdcd636` one4all | **M-SW-BYRD-A**: per-stmt skeleton (no pattern), gate rung2/3/4. Then B(E_QLIT)→C(E_SEQ)→D(E_ALT)→E(ARBNO)→F(captures)→G(DEFINE). See MILESTONE-WASM-BYRD.md |
| **ICON WASM** | IW-16 | `48be4dd` one4all | **M-IW-G02**: rung03_suspend_gen_compose — implement E_ALT for generator composition |
| **Prolog WASM** | PW-16 | `1a46b53` one4all (pw-15-wip) | **PW-17 first**: fix rung07 multi-clause body call arity mismatch (`_call` needs 6 args, emitter passes 3) — see PW-16 handoff |
| **Icon JVM** IJ-58 · **Prolog JVM** PJ-84a · **Prolog x64** PX-1 · **ICON x64** IX-18 · **⭐ Scrip Demo** SD-37 · **🌳 Parser pair** PP-1 · **TINY backend** B-292 · **TINY NET** N-253 · **TINY JVM** J-216 · **TINY frontend** F-223 · **DOTNET** D-164 · **README** R-2 · **🔗 LINKER** LP-6 · **🔗 LINKER JVM** LP-JVM-3 | ← all unfrozen, resume | see SESSIONS_ARCHIVE for HEAD per session | read own SESSION-*.md for next action |

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
| SNOBOL4 (WASM) | `SESSION-snobol4-wasm.md` | `BACKEND-WASM.md` | — |
| Rebus | `FRONTEND-REBUS.md` | — | — |

Special: `SCRIP_DEMOS.md` · `ARCH-scrip-abi.md` · `SESSION-linker-sprint1.md` · `SESSION-linker-net.md`

**3. Deep reference → ARCH-*.md** (open only when needed — catalog in `ARCH-index.md`)

---

*PLAN.md = routing + NOW only. 3KB max. No sprint content. No completed milestones.*
