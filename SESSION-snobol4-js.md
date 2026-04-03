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

⛔ **INTERPRETER SESSION — do NOT build scrip-cc, do NOT run make, do NOT touch C sources.**
Per RULES.md §68–70: interpreter sessions never invoke scrip-cc or the emitter pipeline.

Setup (installs node only — gcc/make are irrelevant here):
```bash
FRONTEND=snobol4 BACKEND=js TOKEN=TOKEN_SEE_LON bash /home/claude/.github/SESSION_SETUP.sh
```

Skips: `nasm wabt wat2wasm java javac mono ilasm icont swipl gcc make`

---

## §TEST

⛔ **Do NOT run `run_emit_check.sh` or `run_invariants.sh`** — those test the scrip-cc emitter pipeline. This is an interpreter session.

Run the broad interpreter test instead:
```bash
cd /home/claude/one4all
CORPUS=/home/claude/corpus node test/js/run_broad.js
```

---

## §KEY FILES

| File | Role |
|------|------|
| `src/backend/emit_js.c` | JS emitter — main work file |
| `src/runtime/js/sno_engine.js` | **5-phase executor** (port of `stmt_exec.c`) |
| `src/runtime/js/sno_runtime.js` | Value types, builtins, I/O |
| `test/js/run_js.js` | Node runner shim |
| `src/backend/c/emit_byrd_c.c` | **Oracle** — copy EKind switch, adapt syntax |
| `src/backend/c/trampoline.h` | **Oracle** — trampoline model |
| `src/runtime/dyn/stmt_exec.c` | **Oracle** — 5-phase executor (sno_engine.js model) |

---

## §ORACLE READ ORDER (before writing any pattern code)

```bash
cat src/backend/c/trampoline.h                       # trampoline engine
sed -n '1,50p' src/runtime/dyn/stmt_exec.c           # 5-phase spec header
sed -n '1,100p' src/backend/c/emit_byrd_c.c          # output macro, uid counter
grep -n "^static void emit_\|case E_" src/backend/c/emit_byrd_c.c | head -40
```

The two oracles are complementary:
- `stmt_exec.c` → oracle for `sno_engine.js` (runtime executor, 5-phase logic)
- `emit_byrd_c.c` → oracle for `emit_js.c` (emitter, EKind switch)

---

## §5-PHASE EXECUTOR (the architectural spine)

Every SNOBOL4 pattern-match statement is:
```
Phase 1: build_subject  — resolve subject variable or evaluate expression
Phase 2: build_pattern  — pattern AST → {α, β} JS Byrd box graph
Phase 3: run_match      — drive root.α() via trampoline, collect captures
Phase 4: build_repl     — replacement expression already evaluated
Phase 5: perform_repl   — splice into subject, assign, :S/:F branch
```

`sno_engine.js` exports:
```js
function exec_stmt(subj_name, subj_val, pat, repl, has_repl) {
    // Phase 1: resolve subject
    // Phase 2: build_pattern(pat) → {α, β} root box
    // Phase 3: scan loop + trampoline
    // Phase 4: repl already in hand
    // Phase 5: splice + assign + return 1/:S or 0/:F
}
```

For pattern-free statements, Phases 2+3 are skipped and Phase 5 is just
a variable assignment. The executor handles both paths.

---

## §DISPATCH ENCODING (decided SJ-1 — do not re-debate)

Pattern statements emit a `for(;;) switch(_pc)` loop.
`_pc` is an integer: `(node_uid << 2) | signal`.

```js
const PROCEED = 0, SUCCEED = 1, CONCEDE = 2, RECEDE = 3;
// emit_js.c:  J("case %d: ", uid << 2 | PROCEED)
// uid from next_uid() — same counter as x64/C emitters
```

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

## §NOW — SJ-4 → SJ-5

**HEAD:** one4all `4b5e682`
**Next milestone: M-SJ-A03**

**Architecture pivot (SJ-4):** Milestones reorganized around the 5-phase
executor model from `stmt_exec.c`.  `sno_engine.js` is the new key file —
a direct JS port of the x86 5-phase executor.  See MILESTONE-JS-SNOBOL4.md.

Current state: M-SJ-A01 + M-SJ-A02 + block-grouping rewrite (SJ-3) done.
Emit-diff 1286/0. Node v22 IIFE bug is the only blocker for M-SJ-A03.

**SJ-5 first actions (mandatory order):**
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
8. Wire `run_snobol4_js()` into `run_invariants.sh`
9. Gate: emit-diff 1286/0, first snobol4_js invariants green → commit M-SJ-A03
10. **Begin `sno_engine.js` Phase 5 stub** (no-pattern path: var assign + :S/:F)
    Oracle: `stmt_exec.c` lines 877–end (Phase 5 `perform_repl`)

---

*SESSION-snobol4-js.md — updated SJ-4 pivot, 2026-04-02, Claude Sonnet 4.6.*
*Added 5-phase executor spine. sno_engine.js is now the architectural center.*
