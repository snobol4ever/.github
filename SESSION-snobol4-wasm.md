# SESSION-snobol4-wasm.md — SNOBOL4 × WASM (one4all)

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

Installs: `gcc make curl unzip wabt(wat2wasm) node snobol4(CSNOBOL4)`
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

## §NOW — SW-11

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **SNOBOL4 WASM** | SW-11 | `2a973fe` one4all · `7c17586` corpus | **M-SW-C01: CAPTURES** rungW07/ 5 tests |

See SESSIONS_ARCHIVE SW-10 handoff for the two blockers to fix first.
