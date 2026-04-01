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

## §NOW — SJ-4

**HEAD:** one4all `4b5e682`
**Next milestone: M-SJ-A03** (still in progress)

M-SJ-A01 + M-SJ-A02 + block-grouping rewrite (SJ-3) done.
Emit-diff 1286/0. Node v22 IIFE bug is the only blocker.

First actions (mandatory order):
1. `git log --oneline -3`  # confirm 4b5e682
2. `CORPUS=/home/claude/corpus bash test/run_emit_check.sh`  # expect 1286/0
3. **Fix Node v22 var/IIFE bug** in `js_emit()` forward-decl section:
   - Emit bare `var goto_vX;` only in forward section
   - Remove `var goto_v_END = function() { return null; };` from forward section
   - Block section already assigns goto_v_END correctly
   - Test: `node compiled_hello.js` must print `HELLO WORLD` with no error
4. Run full corpus baseline (hello, rung2/3/4/8): measure pass/fail
5. Fix `remdr` missing in sno_runtime.js
6. Fix float format: `1.` → `1` in `_to_str()`
7. Fix n-ary SEQ: right-fold children in js_emit_pat()
8. Fix ARBNO zero-advance guard (see ARCH-spipat-js.md)
9. Wire `run_snobol4_js()` into `run_invariants.sh`
10. Gate: emit-diff 1286/0, first snobol4_js invariants green → commit M-SJ-A03

---

*SESSION-snobol4-js.md — updated SJ-3 final, 2026-04-01, Claude Sonnet 4.6.*
