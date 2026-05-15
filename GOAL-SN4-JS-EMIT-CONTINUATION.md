# SJ4-JS-3/4 Continuation Guide — Scalar IR Emission for JavaScript

**Status:** SJ4-JS-1 ✅ (19 BB emitters complete) + SJ4-JS-2 ✅ (SM API complete)  
**Blocked:** SJ4-JS-3/4 pending scalar IR emission  
**Estimated effort:** 2–3 sessions (complex codegen task)

---

## What SJ4-JS-3/4 Need

### SJ4-JS-3 — Smoke 7/7
Write test script: `scripts/test_smoke_snobol4_js.sh`
- Run 7 SNOBOL4 smoke programs via `scrip --sm-emit --target=js file.sno`
- Execute JS output with `node`
- Compare to oracle

**Blocker:** scalar IR nodes don't emit; currently only generators work

### SJ4-JS-4 — Beauty Self-Host
Run `beauty.sno` under JS emission and verify byte-identical output to SPITBOL oracle

---

## Architecture: Scalar IR Emission

The switch/dispatch loop is required because SNOBOL4 can GOTO backward, which forbids straight-line code.

### Model

```js
'use strict';
const rt = require('./sno_runtime.js');
rt._init();

// String table (literals)
const _S0 = "hello";
const _S1 = "OUTPUT";

// Pattern factories
function wire_pat_0(ms) { ... }
function wire_pat_1(ms) { ... }

// Main execution loop — MANDATORY for GOTO support
let _pc = 0;
loop: while (true) {
    switch (_pc) {
    case 0:  // statement 0 (first label)
        rt.push_str(_S0, 5);
        rt.store_var(_S1);
        _pc = 1;
        continue;
    case 1:  // statement 1
        rt.halt_tos();
        break loop;
    default:
        break loop;
    }
}
rt._finalize();
```

### Statement Numbering

- Each IR statement (scalar sequence in a statement boundary) gets a unique case number
- Wired in lower; available as IR node metadata
- GOTO(label) → jump to label's statement number

### Three Phases

1. **Prologue** (emit_js_prologue) — done ✅
   - `'use strict';`
   - `const rt = require('./sno_runtime.js');`
   - `rt._init();`

2. **Scalar Walk** (emit_js_scalar) — **NOT YET IMPLEMENTED**
   - Visit each IR_t node via ir_walk (DFS)
   - Emit stack operations for scalar nodes
   - Emit pattern factory calls and result handling
   - Track PC assignments

3. **Epilogue** (emit_js_epilogue) — done ✅
   - `rt._finalize();`

---

## Scalar Node Kinds (SNOBOL4 subset)

### Literals

| IR_kind | Emit as | Example |
|---------|---------|---------|
| IR_LIT_I | `rt.push_int(nd->ival);` | Push 42 |
| IR_LIT_S | `rt.push_str(_S<N>, len);` where _S<N> = nd->sval | Push "hello" |
| IR_LIT_F | `rt.push_real_bits(nd->dval);` | Push 3.14 |
| IR_LIT_NUL | `rt.push_null();` | Push null |

### Variables & Storage

| IR_kind | Emit as | Example |
|---------|---------|---------|
| IR_VAR | `rt.push_var("VARNAME");` where VARNAME from nd->sval | Load X |
| IR_ASSIGN | `rt.store_var("VARNAME");` | X = ... |

### Operations

| IR_kind | Emit as |
|---------|---------|
| IR_UNOP(NEG) | `rt.neg();` |
| IR_UNOP(NOT) | ??? (boolean complement) |
| IR_BINOP(+) | `rt.arith('add');` |
| IR_BINOP(-) | `rt.arith('sub');` |
| IR_BINOP(*) | `rt.arith('mul');` |
| IR_BINOP(/) | `rt.arith('div');` |
| IR_BINOP(\|\|) | `rt.concat();` (string concatenation) |
| IR_BINOP(EQ) | `rt.acomp('eq');` (arithmetic) or `rt.lcomp('eq');` (string) |

### Function Calls

| IR_kind | Emit as |
|---------|---------|
| IR_CALL | `rt.call("FUNCNAME", nargs);` |

### Pattern Matching

| IR_kind | Emit as |
|---------|---------|
| IR_SCAN | Create pattern via factories; call rt.set_scan(ms, pat) |
| IR_GOTO | `_pc = stmt_number; continue;` |
| IR_FAIL | `_last_ok = false; _pc = fail_label; continue;` |
| IR_SUCCEED | `_last_ok = true; _pc = next_label; continue;` |
| IR_RETURN | `do_return(kind, cond);` (stub for now) |

---

## Implementation Roadmap

### Phase 1: Scalar Foundation (SJ4-JS-3a)

Enhance emit_js_scalar to:

```c
int emit_js_scalar(IR_t * nd, FILE * out) {
    switch (nd->t) {
    case IR_LIT_I:
        fprintf(out, "rt.push_int(%lld);", nd->ival);
        break;
    case IR_LIT_S:
        fprintf(out, "rt.push_str(");
        js_escape_string(out, nd->sval);
        fprintf(out, ", %d);", (int)strlen(nd->sval));
        break;
    case IR_VAR:
        fprintf(out, "rt.push_var(\"");
        fprintf(out, "%s", nd->sval);  // uppercase already
        fprintf(out, "\");");
        break;
    case IR_ASSIGN:
        fprintf(out, "rt.store_var(\"");
        fprintf(out, "%s", nd->sval);
        fprintf(out, "\");");
        break;
    case IR_UNOP:
        if (nd->ival == NEG_OP) fprintf(out, "rt.neg();");
        else fprintf(out, "/* unop stub %lld */", nd->ival);
        break;
    case IR_BINOP:
        // Handle binary ops (add, sub, mul, div, concat, comparisons)
        break;
    case IR_CALL:
        fprintf(out, "rt.call(\"%s\", %d);", nd->sval, nd->ival);
        break;
    default:
        fprintf(out, "/* scalar stub: kind %d */", nd->t);
    }
    return 0;
}
```

**Gate:** Compile without error; hello.sno scalar operations emit (even if not yet executed correctly).

### Phase 2: Switch/Dispatch Loop (SJ4-JS-3b)

Enhance emit_js_prologue to emit the switch statement structure:

```c
static int g_next_case = 0;

int emit_js_prologue(IR_block_t * cfg, FILE * out) {
    fprintf(out, "'use strict';\n");
    fprintf(out, "const rt = require('./sno_runtime.js');\n");
    fprintf(out, "rt._init();\n");
    fprintf(out, "let _pc = 0;\n");
    fprintf(out, "loop: while (true) { switch (_pc) {\n");
    g_next_case = 0;
    return 0;
}

int emit_js_epilogue(IR_block_t * cfg, FILE * out) {
    fprintf(out, "default: break loop;\n");
    fprintf(out, "}} rt._finalize();\n");
    return 0;
}
```

**Gate:** Valid JS with switch loop structure; doesn't execute yet but parses.

### Phase 3: Statement Boundaries (SJ4-JS-3c)

Wire statement case numbers via IR metadata or visitor context:

```c
typedef struct {
    IR_emit_vtable_t * vt;
    FILE * out;
    int stmt_id;
    int case_num;
} emit_js_context_t;
```

Each statement's entry IR_t node gets a case label.

**Gate:** test_smoke_snobol4_js.sh produces executable JS for hello.sno.

### Phase 4: Pattern Matching Integration (SJ4-JS-4a)

Wire pattern factories into scalar execution:

```c
case N:
    // Execute pattern matching if IR_SCAN present
    const ms = rt.MatchState("subject string");
    const pat = wire_pat_5(ms);
    const result = pat.alpha();
    if (result !== null) {
        _pc = success_label;
    } else {
        _pc = fail_label;
    }
    continue;
```

**Gate:** hello.sno with pattern matching runs correctly.

### Phase 5: Full Beauty (SJ4-JS-4b)

Run beauty.sno and fix remaining issues (DEFINE, indirect patterns, &STCOUNT, etc.).

**Gate:** md5sum beauty_js.out = abfd19a7a834484a96e824851caee159.

---

## Key Files to Modify

| File | Changes |
|------|---------|
| `src/emitter/emit_js.c` | Expand emit_js_scalar with all IR_* cases |
| `src/runtime/js/sno_runtime.js` | Add missing stack operations (already mostly done) |
| `scripts/test_smoke_snobol4_js.sh` | NEW — test harness |

## Reference Materials

- `src/lower/ir_exec.c` — IR interpreter (definitive semantics for each node kind)
- `src/emitter/emit_ir.c` — IR walk and visitor pattern
- `archive/backend/emit_emitters/emit_js.c` — legacy JS emitter (1126 lines) — patterns for scalar walk
- `src/runtime/boxes/bb_*.js` — already in use, no changes needed
- GOAL-SN4-JS-EMIT.md — this goal

## Session Notes

**Completed (2026-05-15, Claude Sonnet 4.6):**
- SJ4-JS-1: 19 BB emitters + dispatch table (emit_js.c)
- SJ4-JS-2: SM API + MatchState factory (sno_runtime.js)
- Build: clean, all tests pass

**Context consumed:** ~52% (99k of 190k tokens)  
**Remaining:** Sufficient for SJ4-JS-3a-3b in next session  
**Recommendation:** Fresh session for SJ4-JS-3 full implementation

---

## Quick Start for Next Session

```bash
cd /home/claude/one4all
git log --oneline -3  # Verify a72c9b6d HEAD
git checkout -b sj4-js-3-scalar
# Edit src/emitter/emit_js.c: expand emit_js_scalar()
# Edit src/runtime/js/sno_runtime.js: ensure all ops present
# Edit src/emitter/emit_js.c: enhance emit_js_prologue/epilogue for switch
# Create scripts/test_smoke_snobol4_js.sh
make scrip
bash scripts/test_smoke_snobol4_js.sh
```

---

**End handoff document.**
