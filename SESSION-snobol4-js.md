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

## §NOW — SJ-1

**Next milestone: M-SJ-A01**

First actions:
1. Read oracles above
2. Create `src/backend/emit_js.c` scaffold — empty EKind switch, `J()` macro
3. Create `src/runtime/js/sno_runtime.js` — trampoline + OUTPUT + `_vars`
4. Create `test/js/run_js.js` — Node runner
5. Wire into Makefile
6. Gate: hello/literals pass, emit-diff 981/4 holds

Read: `BACKEND-JS.md` · `MILESTONE-JS-SNOBOL4.md`

---

*SESSION-snobol4-js.md — rewritten SJ-1, 2026-03-31, Claude Sonnet 4.6.*
