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

**Step 2 — Gate (emit sessions ONLY — interpreter sessions skip this step entirely):**

⛔ **DYN- and one4all-SNOBOL4-NET sessions: SKIP Step 2. Do NOT run run_invariants.sh or run_emit_check.sh. Go straight to Step 3.**

Emit sessions only:
```bash
cd /home/claude/one4all
CORPUS=/home/claude/corpus bash test/run_invariants.sh snobol4_x86
# Target: 142/142. Currently: 137p/5f (word1-4, cross). All other sessions FROZEN.
```

**Step 3 — Read in order:**
```
tail -120 /home/claude/.github/SESSIONS_ARCHIVE.md   # last handoff — FIRST
grep "^## " /home/claude/.github/RULES.md            # scan headers, cat only relevant sections
cat /home/claude/.github/PLAN.md
```
Then read your SESSION-*.md (see Routing table below).

**⛔ ROUTING: frontend × backend → `SESSION-<frontend>-<backend>.md`. That is all.**

⛔ **DISAMBIGUATION — "dynamic Byrd boxes" is an ARCHITECTURE TERM, not a session name.**
Both the JVM session (J-) and the x86 interpreter session (DYN-) use dynamic Byrd boxes.
The user saying "dynamic Byrd boxes written in Jasmin" → **JVM session** (`SESSION-snobol4-jvm.md`).
The user saying "dynamic Byrd boxes written in C / .s / NASM" → **DYN- session** (`SESSION-dynamic-byrd-box.md`).
Backend keyword is the tie-breaker: `Jasmin` / `JVM` / `.jasmin` → J- session. `NASM` / `x86` / `.s` → DYN- session.

**Snocone × x86 additionally read:**
```
cat /home/claude/.github/SESSION-snocone-x64.md
```

**Dynamic Byrd Box (x86 interpreter) additionally read:**
```
cat /home/claude/.github/SESSION-dynamic-byrd-box.md
# Do NOT cat ARCH-byrd-dynamic.md in full — grep only the section you need
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
| **⭐ DYNAMIC BYRD BOX** | DYN-72 | one4all `bf4de1d` · corpus `8d5cc6a` | **175p/3f** · **DYN-73**: fix 1013 (NAMEVAL/NAMEPTR union confusion → use STRVAL or fix NAME_DEREF) + 1016/003 (test g_eval_pat_hook) + expr_eval (add E_ALT to interp_eval_pat default) → **178p/0f → M-DYN-INTERP-FULL** |
| **Snocone x86** | SC-14 | `05a50e8` one4all · `7729763` corpus | M-SC-B10/B11/B12 done · snocone_x86 160/160 · **SC-15**: fix do-while nested-paren hang → M-SC-SELFTEST · **SCB-1**: BEAUTY ramp — see SESSION-snocone-beauty.md |
| ~~**SNOBOL4 WASM**~~ | ⛔ PARKED SW-17 | `fdcd636` one4all | WASM suspended — see MILESTONE_ARCHIVE.md |
| ~~**ICON WASM**~~ | ⛔ PARKED IW-17 | `4d6cb2d` one4all | WASM suspended — see MILESTONE_ARCHIVE.md |
| ~~**Prolog WASM**~~ | ⛔ PARKED PW-17 | `48461c7` one4all | WASM suspended — see MILESTONE_ARCHIVE.md |
| **SNOBOL4 JS** | SJ-17 | one4all `ec6c0b3` · .github this | **SJ-18**: fix cross + expr_eval + 1015_opsyn → ≥170p · M-SJ-INTERP |
| **⭐ TINY JVM** | J-233 | one4all `b8560bb` | **J-234**: 1011_func_redefine frame-scoping + 1017_arg_local → ≥165p |
| **SNOBOL4 JS** | SJ-24 | one4all `77b1a73` · .github this | **SJ-25**: fix test_stack (TABLE/ARRAY indexing) + test_case icase no-match → ≥175p → M-SJ-INTERP+2 |
| **⭐ TINY JVM** | J-229 | one4all `4ceba85` · .github `bd9fb05` | **J-230**: fix bb_arbno VerifyError + bb_any/rpos regression → ≥136p → ARRAY/TABLE → ≥155p |
| **ICON JS** | IJJ-1 | — | **M-IJJ-A01** (after M-SJ-A01): emit_js_icon.c scaffold. Oracle: Proebsting paper + emit_jvm_icon.c. See MILESTONE-JS-ICON.md |
| **Prolog JS** | PJJ-1 | — | **M-PJJ-A01** (after M-SJ-A01): emit_js_prolog.c scaffold. Trail+unify runtime. Oracle: emit_jvm_prolog.c. See MILESTONE-JS-PROLOG.md |
| **⭐ one4all-SNOBOL4-NET** | D-181 | one4all `e1a66fb` (WIP) · .github this | **166p/12f** · icase root-cause complete (str write-back bug + pattern-return infra in WIP) · **D-182**: fix str splice write-back → commit WIP → test_case/math/stack/string ≥170p → NRETURN → ≥175p |
| **DOTNET** | D-166 | `e1e4d9e` snobol4dotnet | **M-NET-P35-FIX**: @N Phase 3/5 fix → 80/80 crosscheck. FROZEN until M-DYN-S1. |
| **Icon JVM** IJ-58 · **Prolog JVM** PJ-84a · **Prolog x64** PX-1 · **ICON x64** IX-18 · **⭐ Scrip Demo** SD-37 · **🌳 Parser pair** PP-1 · **TINY backend** B-292 · **TINY NET** N-253 · **TINY JVM** J-217 · **TINY frontend** F-223 · **README** R-2 · **🔗 LINKER** LP-6 · **🔗 LINKER JVM** LP-JVM-3 | ← resume per session | see SESSIONS_ARCHIVE | read own SESSION-*.md ||

**Invariants (DYN-20 baseline): x86: SNOBOL4 `142/142` · Snocone `160/160` · Icon `95p/163f` · Prolog `13p/94f` | JVM: SNOBOL4 `94p/32f` · Icon `173p/44f` · Prolog `106p/1f` | .NET: `108p/2f` | WASM: SNOBOL4 `28p/1f`

**Gate:** Emit sessions — runtime invariants only (`snobol4_x86`), emit-diff retired until post M-DYN-S1. Interpreter sessions (DYN-, one4all-SNOBOL4-NET) — broad corpus pass count only; do NOT run run_invariants.sh or run_emit_check.sh.

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
| Snocone BEAUTY | `SESSION-snocone-beauty.md` | — | — |
| SNOBOL4 (WASM) | ⛔ PARKED | — | — |
| SNOBOL4 (JS) | `SESSION-snobol4-js.md` | `BACKEND-JS.md` | — |
| Icon (JS) | `SESSION-icon-js.md` | `BACKEND-JS.md` | — |
| Prolog (JS) | `SESSION-prolog-js.md` | `BACKEND-JS.md` | — |
| Rebus | `FRONTEND-REBUS.md` | — | — |

Special: `SCRIP_DEMOS.md` · `ARCH-scrip-abi.md` · `SESSION-linker-sprint1.md` · `SESSION-linker-net.md` · `MILESTONE-JVM-SNOBOL4.md`

**3. Deep reference → ARCH-*.md** (open only when needed — catalog in `ARCH-index.md`)

---

*PLAN.md = routing + NOW only. 3KB max. No sprint content. No completed milestones.*
