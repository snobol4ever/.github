# SESSION-snobol4-wasm.md — SNOBOL4 × WASM (one4all) ⛔ INACTIVE — parked 2026-03-31, see MILESTONE_ARCHIVE.md

**Repo:** one4all · **Frontend:** SNOBOL4 · **Backend:** WASM
**Session prefix:** `SW` · **Trigger:** "playing with SNOBOL4 wasm"

---

## §SUBSYSTEMS

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| SNOBOL4 language / IR | `FRONTEND-SNOBOL4.md` | pattern/AST questions |
| WASM emitter patterns | `BACKEND-WASM.md` | WAT codegen |

---

## §BUILD

```bash
FRONTEND=snobol4 BACKEND=wasm TOKEN=TOKEN_SEE_LON bash /home/claude/.github/SESSION_SETUP.sh
```

Installs: `gcc make curl unzip wabt(wat2wasm) node spitbol`
Skips: `nasm libgc-dev java javac mono ilasm icont swipl`

Note: `wabt` = `apt-get install -y wabt` · `node` = `nodejs` (pre-installed Ubuntu 24).

---

## §TEST

```bash
cd /home/claude/one4all
CORPUS=/home/claude/corpus bash test/run_emit_check.sh               # always — 981/4
CORPUS=/home/claude/corpus bash test/run_wasm_corpus_rung.sh W01     # per-rung during session
CORPUS=/home/claude/corpus bash test/run_invariants.sh snobol4_wasm  # own cell only
```

---

## §KEY FILES

| File | Role |
|------|------|
| `src/backend/emit_wasm.c` | WASM emitter — main work file |
| `src/runtime/wasm/` | WASM runtime (string heap, OUTPUT) |
| `test/wasm/run_wasm.js` | Node runner shim |
| `test/run_wasm_corpus_rung.sh` | Per-rung test runner |
| `corpus/crosscheck/rungW01/`…`rungW07/` | Pattern-test rungs — .sno .ref .s .j .il .wat |

---

## §NOW — SW-13 (→ SW-14)

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **SNOBOL4 WASM** | SW-14 WIP | `4652640` one4all | **M-SW-C02**: rung11 5/7 — fix 1115/1116 DATA typename+field accessor |

See SESSIONS_ARCHIVE SW-14 handoff for detailed task list and root-cause notes.
