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
| **GRAND MASTER REORG** | G-9 s29 | one4all `9b2fa58` · corpus `224d3d4` · .github this session | **M-G9-ICON-IR-WIRE** |
| **Snocone x86** | SC-4 | `e2f6742` one4all · `232499f` corpus | M-SC-B03 BLOCKED: fix `for`-loop compile-time hang (RBRACE not consumed at top level in sc_do_stmt) |
| **SNOBOL4 WASM** | SW-5 | `2094796` one4all | **M-SW-A05: GOTO/BUILTINS** rung8/ 3 tests — E_KW + sno_replace/size/dupl needed |
| **⭐ Scrip Demo** | SD-37 `795c2ff` | — | resume — unfrozen |
| **🌳 Parser pair** | PP-1 `4b4d71a` | — | resume — unfrozen |
| **TINY backend** | B-292 `acbc71e` | — | resume — unfrozen |
| **TINY NET** | N-253 `e7dc859` | — | resume — unfrozen |
| **TINY JVM** | J-216 `a74ccd8` | — | resume — unfrozen |
| **TINY frontend** | F-223 `b4507dc` | — | resume — unfrozen |
| **DOTNET** | D-164 `e1e4d9e` | — | resume — unfrozen |
| **README** | R-2 `00846d3` | — | resume — unfrozen |
| **ICON x64** | IX-18 `c648df5` | — | resume — unfrozen |
| **ICON WASM** | IW-7 | one4all `0f0b1eb` · `.github` this commit | **M-IW-P01**: `$icn_retcont` funcref trampoline → rung02 3/3 |
| **Prolog JVM** | PJ-84a `a79906e` | — | resume — unfrozen |
| **Prolog x64** | PX-1 `a051367` | — | resume — unfrozen |
| **Prolog WASM** | PW-7 `b053fc1` one4all | — | **M-PW-A02**: HEAD UNIF done (3p/104f) — next: rung04 is/2 + -> inline emit |
| **Icon JVM** | IJ-58 `5b32daa` | — | resume — unfrozen |
| **🔗 LINKER** | LP-6 `e7dc859` | — | resume — unfrozen |
| **🔗 LINKER JVM** | LP-JVM-3 `55d8655` | — | resume — unfrozen |

**Invariants (post-reorg baseline, G-9 s22):** x86: SNOBOL4 `106/106` · Icon `94p/164f` · Prolog `13p/94f` | JVM: SNOBOL4 `94p/32f` · Icon `173p/44f` · Prolog `106p/1f` | .NET: `108p/2f` | WASM: SNOBOL4 `12/12` (SW-3 M-SW-A03)

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
