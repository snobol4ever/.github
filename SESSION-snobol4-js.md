# SESSION-snobol4-js.md — SNOBOL4 × JavaScript (one4all)

**Repo:** one4all · **Frontend:** SNOBOL4 · **Backend:** JavaScript
**Session prefix:** `SJ` · **Trigger:** "playing with SNOBOL4 JavaScript" / "SNOBOL4 JS"
**Replaces:** SESSION-snobol4-wasm.md (⛔ PARKED)

---

## §SUBSYSTEMS

| Subsystem | Doc |
|-----------|-----|
| SNOBOL4 language / IR | `FRONTEND-SNOBOL4.md` |
| JS backend patterns | `BACKEND-JS.md` |
| Milestone ladder | `MILESTONE-JS-SNOBOL4.md` |

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
CORPUS=/home/claude/corpus bash test/run_emit_check.sh           # always 981/4
CORPUS=/home/claude/corpus bash test/run_invariants.sh snobol4_js
```

---

## §KEY FILES

| File | Role |
|------|------|
| `src/backend/emit_js.c` | JS emitter — main work file (to create) |
| `src/runtime/js/sno_runtime.js` | JS runtime stub (to create) |
| `test/js/run_js.js` | Node runner shim (to create) |
| `src/backend/c/emit_byrd_c.c` | **Oracle** — copy EKind switch, adapt syntax |
| `src/backend/c/trampoline.h` | **Oracle** — trampoline model |

---

## §ORACLE READ ORDER (before writing any code)

```bash
cat src/backend/c/trampoline.h              # trampoline engine
sed -n '1,100p' src/backend/c/emit_byrd_c.c # output macro, uid counter
grep -n "^static void emit_\|case E_" src/backend/c/emit_byrd_c.c | head -40
```

---

## §DISPATCH ENCODING (decided SJ-1 — do not re-debate)

Pattern statements emit a `for(;;) switch(_pc)` loop.
`_pc` is an integer: `(node_uid << 2) | signal`.

```js
const PROCEED = 0, SUCCEED = 1, CONCEDE = 2, RECEDE = 3;
// emit_js.c:  J("case %d: ", uid << 2 | PROCEED)
// uid from next_uid() — same counter as x64/C emitters
```

**Oracle:** `src/runtime/engine/engine.c` — `t << 2 | a` dispatch.
**Do NOT use string case labels** — integer switch → JS JIT jump table.

emitted shape:
```js
let _pc = (N_SEQ<<2|PROCEED);
dispatch: for(;;) switch(_pc) {
  case (1<<2|0): ...  // SEQ  PROCEED
  case (1<<2|2): ...  // SEQ  CONCEDE  (β — advance scan)
  case (1<<2|3): return block_END;  // SEQ RECEDE (ω — total fail)
  case (2<<2|0): ...  // ALT1 PROCEED  (α — try first arm)
  case (2<<2|2): ...  // ALT1 CONCEDE  (β — try second arm)
  case (2<<2|3): _pc=(1<<2|2); break;  // ALT1 RECEDE (ω → SEQ β)
}
```

## §OUTPUT HANDLING (decided SJ-1)

```js
const _vars = new Proxy({}, {
    set(o,k,v) { o[k]=v; if(k==="OUTPUT") process.stdout.write(String(v)+"\n"); return true; }
});
```

## §NOW — SJ-3

**HEAD:** one4all `f9499d8`
**Next milestone: M-SJ-A02 — Byrd-box pattern dispatch**

M-SJ-A01 delivered: emit_js.c + sno_runtime.js + run_js.js + Makefile/-js wire.
Hello passes. emit-diff 981/4.

First actions (mandatory order):
1. `git log --oneline -3`  # confirm f9499d8
2. `CORPUS=/home/claude/corpus bash test/run_emit_check.sh`  # confirm 981/4
3. Read `src/backend/c/emit_byrd_c.c` emit_pat_node() (E_SEQ, E_ALT, emit_lit,
   emit_pos, emit_len, emit_any, emit_arb) — oracle for JS port.
4. In `src/backend/emit_js.c`: replace `_match()` stub in js_emit_stmt()
   with full `for(;;) switch(_pc)` Byrd-box dispatch (see §DISPATCH).
   Port emit_pat_node() as js_emit_pat_node() using J() macro.
5. In `src/runtime/js/sno_runtime.js`: promote `_match` from stub to full
   dispatcher that invokes the compiled pattern function.
6. Wire `CORPUS=/home/claude/corpus bash test/run_invariants.sh snobol4_js`.
7. Gate: emit-diff 981/4 · invariants moving toward green.

---

*SESSION-snobol4-js.md — updated SJ-2→SJ-3, 2026-04-01, Claude Sonnet 4.6.*
