# SESSION-snobol4-js.md — SNOBOL4 × JavaScript (one4all)

**Repo:** one4all · **Frontend:** SNOBOL4 · **Backend:** JavaScript
**Session prefix:** `SJ` · **Trigger:** "playing with SNOBOL4 JavaScript" / "SNOBOL4 JS"
**Replaces:** SESSION-snobol4-wasm.md (⛔ PARKED)

---

## §SUBSYSTEMS

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| SNOBOL4 language / IR | `FRONTEND-SNOBOL4.md` | pattern/AST questions |
| JS backend patterns | `BACKEND-JS.md` | JS codegen, spipatjs wiring |

---

## §BUILD

```bash
FRONTEND=snobol4 BACKEND=js TOKEN=TOKEN_SEE_LON bash /home/claude/.github/SESSION_SETUP.sh
```

Installs: `gcc make node`
Skips: `nasm wabt wat2wasm java javac mono ilasm icont swipl`

---

## §TEST

```bash
cd /home/claude/one4all
CORPUS=/home/claude/corpus bash test/run_emit_check.sh               # always — 981/4
CORPUS=/home/claude/corpus bash test/run_invariants.sh snobol4_js    # own cell only
```

---

## §KEY FILES

| File | Role |
|------|------|
| `src/backend/emit_js.c` | JS emitter — main work file (to be created) |
| `src/runtime/js/` | JS runtime (spipatjs, string ops, OUTPUT) |
| `test/js/run_js.js` | Node runner shim (to be created) |
| `corpus/crosscheck/rungJ*/` | JS-specific test rungs |

---

## §SPIPATJS INTEGRATION

Clone Phil Budne's pattern library into runtime:
```bash
cd /home/claude/one4all/src/runtime/js
git clone https://github.com/philbudne/spipatjs
```

Pattern IR nodes wire to spipatjs constructors:
- `E_QLIT` → `new Pat.Lit(str)`
- `E_SEQ`  → `Pat.and(left, right)`
- `E_ALT`  → `Pat.or(left, right)`
- `E_ARBNO`→ `Pat.Arbno(inner)`
- `E_ARB`  → `Pat.Arb`
- `E_CAPT_COND` / `E_CAPT_IMM` → cursor-function assign

---

## §EVAL / CODE

```js
// In emitted JS runtime preamble:
const _scrip = require('./scrip_mini.js');  // bundled mini-compiler

function _sno_eval(str) {
    return new Function('return ' + _scrip.compile_expr(str))();
}
function _sno_code(str) {
    const js = _scrip.compile_stmts(str);
    return new Function(js)();
}
```

This is the primary reason for the JS pivot. Design the mini-compiler
interface in M-SJ-C01 after parity is established.

---

## §MILESTONES

| ID | Scope | Gate |
|----|-------|------|
| **M-SJ-A01** | Scaffold: emit_js.c builds, hello/literals/arith pass | rung2/3/4 |
| **M-SJ-A02** | String ops: concat, SIZE, REPLACE, DUPL | rung8 |
| **M-SJ-A03** | Control flow: goto, :S/:F, labels | rung5/6 |
| **M-SJ-B01** | Pattern matching via spipatjs: E_QLIT, E_SEQ, E_ALT | rungJ01/J02 |
| **M-SJ-B02** | ARBNO, ARB, captures (.var, $var) | rungJ03/J04 |
| **M-SJ-B03** | Arrays, Tables, DATA types | rung10/11 |
| **M-SJ-C01** | EVAL() / CODE() — mini-compiler interface | rungJ05 |
| **M-SJ-C02** | DEFINE / user-defined functions | rungJ06 |
| **M-SJ-PARITY** | Full corpus parity with x64/JVM/.NET | all rungs |

---

## §NOW — SJ-1

First action:
1. `cat /home/claude/.github/BACKEND-JS.md`
2. `cat src/backend/emit_net.c | head -100` — use .NET emitter as structural template (closest to JS in simplicity)
3. Create `src/backend/emit_js.c` scaffold
4. Create `src/runtime/js/sno_runtime.js` stub
5. Gate: `run_emit_check.sh` 981/4 holds after adding emit_js.c to build

---

*SESSION-snobol4-js.md — created SJ-1, 2026-03-31, Claude Sonnet 4.6.*
