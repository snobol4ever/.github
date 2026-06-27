# ARCH-IR.md — Intermediate Representation

The shared IR produced by all frontends. Every frontend compiles to this.
SM-LOWER compiles the IR to `SM_sequence_t` instructions (IR-RN-0, 2026-05-20).

## tree_t — the expression node

Current names (post IR-RN-0). Source of truth: `src/include/ast.h`.

```c
/* tree_t — AST node for expressions (was EXPR_t pre IR-RN-0) */
struct tree_t {
    tree_e   t;          /* node kind (was EKind/e_kind) */
    char    *v.sval;     /* string: TT_QLIT text, TT_VAR/TT_FNC/TT_IDX name */
    long     v.ival;     /* integer: TT_ILIT value */
    double   v.dval;     /* float: TT_FLIT value */
    tree_t **c;          /* children array */
    int      n;          /* child count */
};
// Accessors: ast_left(e), ast_right(e), ast_arg(e,i), ast_nargs(e)
// Builder:   ast_node_new(kind), ast_push(parent, child)
```

## tree_e — node kinds

**Leaves:** TT_QLIT, TT_ILIT, TT_FLIT, TT_NUL, TT_VAR, TT_KEYWORD
**Unary:** TT_MNS, TT_NOT, TT_IND (indirect $), TT_NAME (.), TT_ATP (@), TT_STR (*), TT_TILDE
**Binary:** TT_ADD, TT_SUB, TT_MUL, TT_DIV, TT_EXP, TT_SEQ, TT_CAT, TT_ALT, TT_CAPT_COND_ASGN, TT_CAPT_IMM_ASGN, TT_IDX, TT_CHOICE (Icon/Prolog), TT_CLAUSE (Prolog), TT_UNIFY (Prolog), TT_CUT (Prolog)
**N-ary:** TT_FNC (function call), TT_CONCAT (string concat chain), TT_LIST, TT_APPLY
**Pattern:** TT_ARBNO, TT_ARBN, TT_SCAN, TT_POS, TT_RPOS, TT_LEN, TT_RLEN, TT_REM, TT_ARB, TT_FENCE, TT_FAIL, TT_SUCCEED, TT_ABORT, TT_BAL

## STMT_t — the statement

Source of truth: `src/frontend/snobol4/scrip_cc.h`.

```c
struct STMT_t {
    char    *label;
    tree_t  *subject;
    tree_t  *pattern;
    tree_t  *replacement;   /* NULL if no replacement */
    tree_t  *goto_s_expr;   /* :S(label) */
    tree_t  *goto_f_expr;   /* :F(label) */
    tree_t  *goto_u_expr;   /* unconditional goto */
    int      lineno, stno, is_end, has_eq, lang;
    STMT_t  *next;
};
```

## Five phases of a SNOBOL4 statement

```
Label:  Subject  Pattern  =Replacement  :S(goto)  :F(goto)
```

| Phase | Name | Can Fail | Backtracks |
|-------|------|----------|------------|
| 1 | Subject eval | yes | no |
| 2 | Pattern build | yes | no |
| 3 | Match | yes | YES — BB-DRIVER → BB-GRAPH |
| 4 | Replacement eval | yes | no |
| 5 | Assign | no | no |

Phases 1,2,4,5: straight-line stack machine. Phase 3: Byrd box graph.

> ⛔ **CORRECTION (2026-05-30, GROUND ZERO 3).** Icon does not use the stack
> machine / SM value stack at all. An Icon program is one connected Byrd box
> graph, stackless: values in flat per-box DATA slots, inter-box transitions by
> direct `jmp`, zero SM opcodes emitted. The "stack machine" phases above describe
> the SNOBOL4 SM path, not Icon. See `GOAL-ICON-BB.md` → "GROUND ZERO 3" and
> `ARCH-x86.md` §"Boxes are stackless".

---

## Polyglot CODE_t* (U-12 through U-19)

A single `CODE_t*` may contain statements from multiple source languages.
`parse_scrip_polyglot()` in `scrip.c` parses a `.scrip` fenced-block file,
compiling each block with its own frontend, and appends all `STMT_t` chains
in source order into one `CODE_t*`.

Fence syntax:

````
```SNOBOL4
  ... snobol4 source ...
```
```Icon
  ... icon source ...
```
```Prolog
  ... prolog source ...
```
````

Tags are matched case-insensitively: `SNOBOL4`, `Icon`, `Prolog`.
Unknown tags are skipped. Each block is compiled independently by its
frontend; the resulting `STMT_t` chains are linked together in order.

### STMT_t.lang — language tag (U-12)

`STMT_t` carries an `int lang` field (defined in `scrip_cc.h`):

```c
#define LANG_SNO  0   /* SNOBOL4 (default — zero from calloc) */
#define LANG_ICN  1   /* Icon */
#define LANG_PL   2   /* Prolog */
```

Set by each frontend:
- SNOBOL4: `0` by default (calloc zero-initialises).
- Icon: `icon_driver.c` sets `st->lang = LANG_ICN` for every Icon statement.
- Prolog: `prolog_lower.c` sets `s->lang = LANG_PL` at both lowering sites.

The `lang` field is the sole discriminator used by `sm_lower` and
`polyglot_init` to dispatch each statement to the correct runtime.

### polyglot_init — unified initialisation (U-14)

```c
static void polyglot_init(CODE_t *prog);
```

Single walk over `prog->head`. Populates all three runtime tables at once:

| Language | What it does |
|----------|-------------|
| LANG_SNO | `label_table_build` + `prescan_defines` |
| LANG_ICN | zero icn_* state; collect `E_FNC` subjects → `icn_proc_table` |
| LANG_PL  | `prolog_atom_init`; `trail_init`; collect `E_CHOICE`/`E_CLAUSE` → `g_pl_pred_table`; set `g_pl_active=1` if any PL stmts present |

All entry points (`--run`, `--run`, `--compile`) call `polyglot_init`
via `sm_preamble`. Mode 1 (`execute_program`, `interp_eval`) is deleted
(CLI-3M-9, 2026-05-18).

### sm_lower dispatch (U-15, updated CLI-3M-9)

`sm_lower` uses `st->lang` to select lowering path per statement. The
old mode-1 `execute_program` dispatch table is gone.

---

## The Three Broker Modes — One SM (U-16)

The stack machine has three statement-level opcodes, one per broker mode:

```
SM_EXEC_STMT  →  exec_stmt()  →  bb_broker(root, BB_SCAN, ...)   SNOBOL4
SM_BB_PUMP    →  bb_broker(root, BB_PUMP, body_fn, arg)           Icon
SM_BB_ONCE    →  bb_broker(root, BB_ONCE, NULL, NULL)             Prolog
```

Defined in `src/runtime/x86/sm_prog.h`. Handled in `src/runtime/x86/sm_interp.c`.

`SM_BB_PUMP` and `SM_BB_ONCE` are stubbed in the interpreter (set `last_ok=0`)
pending full `sm_lower` support — the `--run` path is the active polyglot path.
`BB_SCAN` is already fully wired via `SM_EXEC_STMT` → `exec_stmt` → `bb_broker(BB_SCAN)`.

### BrokerMode — the three drive modes

Defined in `src/runtime/x86/bb_box.h`:

```c
typedef enum { BB_SCAN, BB_PUMP, BB_ONCE } BrokerMode;
```

| Mode | Language | Drive behaviour |
|------|----------|----------------|
| `BB_SCAN` | SNOBOL4 | Try cursor positions 0..Ω; stop on first match |
| `BB_PUMP` | Icon | Call `body_fn` for every value produced until ω |
| `BB_ONCE` | Prolog | Call α once; report γ or ω; OR-box handles retry |

All three modes share one `bb_broker()` entry point in
`src/runtime/x86/bb_broker.c` and one value type `DESCR_t` (16 bytes).

### Architectural insight

`SM_EXEC_STMT`, `SM_BB_PUMP`, and `SM_BB_ONCE` are the same machine
driven three different ways. SNOBOL4 pattern boxes, Icon generator boxes,
and Prolog clause boxes are all `bb_node_t` nodes returning `DESCR_t`.
The broker does not know or care which language built the box graph —
cross-language box composition works at the IR level without any special
casing. See `test/cross_lang.scrip` for a working end-to-end demonstration.

---

## Unified Emitter Model (EC series, 2026-05-19)

All code-generation backends share a single set of per-instruction template
functions in `emit_core.c`. There are no per-target silo files.

### Mode enum

```c
typedef enum {
    EMIT_TEXT = 0,           /* x86 GAS text (--compile) */
    EMIT_BINARY_WIRED = 1,   /* x86 binary in-memory JIT (--run) */
    EMIT_BINARY_BROKERED = 2,
    EMIT_MACRO_DEF = 3,
    EMIT_TEXT_INLINE = 4,
    EMIT_JVM  = 5,           /* JVM Jasmin text */
    EMIT_JS   = 6,           /* JavaScript */
    EMIT_NET  = 7,           /* .NET MSIL (ilasm) */
    EMIT_WASM = 8,           /* WebAssembly WAT text */
} bb_emit_mode_t;
```

Macros `IS_JVM`, `IS_JS`, `IS_NET`, `IS_WASM` (in `emit_core.h`) test the
current mode. Every template function dispatches on these macros internally.

### Entry point

```c
int emit_program(const tree_t *ast_prog, FILE *out, bb_emit_mode_t mode);
```

Single function in `emit_core.c`. Calls `sm_preamble`, `emit_mode_set`,
`emit_prologue`, the per-target walk, then `emit_epilogue`. Replaces the
former per-target `emit_jvm_program` / `emit_js_program` / `emit_net_program`
/ `emit_wasm_program` entry points (all deleted EC-2 through EC-6).

### Adding a new backend

1. Add `EMIT_NEW = N` to the enum in `emit_core.h`. Add `IS_NEW` macro.
2. Add `case EMIT_NEW:` arms to `emit_prologue` and `emit_epilogue`.
3. Add `else if (IS_NEW) emit_new_from_sm(sm, out);` in `emit_program`.
4. Write `emit_new_from_sm` in `emit_core.c` (or a new `SM_templates/` file).
5. Update `scrip.c` to call `emit_program(ast_prog, out, EMIT_NEW)`.

### Adding a new SM opcode (post-INLINE-ALL)

Every SM opcode lives in exactly one `SM_templates/*.c` file. No code generation
logic exists outside these files or `BB_templates/*.c`. Steps:

1. Define the opcode in `src/lower/SM.h` (`SM_op_t` enum).
2. Add a case to `sm_op_is_dispatched()` in `src/emitter/sm_dispatch.c`.
3. Create or extend one `SM_templates/<group>.c` file. Add arms for every
   `IS_X86`, `IS_JVM`, `IS_JS`, `IS_NET`, `IS_WASM`, `IS_MACRO_DEF` — even
   if some arms are empty stubs. **No other file is touched.**
4. Add a lowering arm in `sm_lower.c` to emit the new opcode.
5. GATE-PK — baseline must not regress.

One template function per opcode (or per group where shapes are identical).
Zero per-target silo files. Zero helper wrappers outside the template.

### File map (post-EC series)

| File | Role |
|------|------|
| `src/emitter/emit_core.c` | All template functions; `emit_program`; WASM state |
| `src/emitter/emit_core.h` | Mode enum + macros; public API |
| `src/emitter/emit_sm.c` | x86 binary SM dispatch (EMIT_BINARY_WIRED) |
| `src/emitter/emit_bb.c` | x86 binary BB node emission |
| `src/emitter/BB_templates/` | One `.c` per BB box kind (JVM/JS/NET arms inline) |
| `src/emitter/SM_templates/` | Grouped SM instruction families (push/arith/control/…) |

Deleted in EC series: `emit_jvm.c`, `emit_js.c`, `emit_net.c`, `emit_ir.c`,
`emit_ir_targets.c`, `emit_wasm.c`, `emit_ir.h` (shim), `IR_emit_vtable_t`.

## IR consolidation — single-structure lowering output (IR-CONSOLIDATE-DCG, 2026-05-20)

**Invariant.** Every BB graph produced by lowering reaches engines through one
storage location: `g_stage2.sm.bb_table[bb_idx]`. The proc/predicate registry
entries (`IcnProcEntry`, `Pl_PredEntry_BB`) carry an `int bb_idx` and nothing
else for graph access — no duplicate `BB_graph_t*` pointer.

Strangler helpers `bb_graph_of_proc` and `bb_graph_of_pred` do the lookup:

```c
if (e->bb_idx >= 0 && e->bb_idx < g_stage2.sm.bb_count)
    return g_stage2.sm.bb_table[e->bb_idx];
return NULL;
```

**Producer (scrip).** `lower()` builds each BB graph, calls `SM_seq_bb_add(g_p,
cfg)` to attach it to the embedded SM sequence, and stores the returned index
into the registry entry's `bb_idx`. `g_stage2.sm` is initialized by
`stage2_reset()` at the top of every lower() pass.

**Producer (mode-4 standalone-binary).** Standalone binaries link against the
runtime but never call `lower()` — `g_stage2.sm` is left zero-initialized in
.bss. `rt_pl_b_end_register` performs the same `SM_seq_bb_add(&g_stage2.sm,
cfg)` call to obtain a `bb_idx`. `SM_seq_bb_add` lazy-allocates `bb_table`
when `bb_cap == 0`, so the standalone case needs no special init step.

This is "Option A" of the IR-CD-5 design question. The alternative ("Option
B" — permanent `ir_body` carve-out for standalone) was rejected because it
would have prevented the field deletion that the rung exists to perform.

**What this replaces.** Pre-IR-CD-5, `IcnProcEntry` and `Pl_PredEntry_BB`
each carried a `BB_graph_t *ir_body` field alongside the `bb_idx`. The
field was a duplicate pointer maintained during the migration. Consumers
went through a strangler helper that preferred `bb_idx` and fell back to
`ir_body`. The fallback covered the mode-4 standalone path until that
path was switched to use the lazy-init pathway.

## File map (post-IR-CD)

| File | Role |
|------|------|
| `src/include/stage2.h` | `stage2_t`, `IcnProcEntry`, `Pl_PredTable` typedefs; `g_stage2` decl |
| `src/lower/sm_prog.c` | `SM_seq_bb_add` (lazy-init bb_table) |
| `src/runtime/interp/icn_runtime.h` | `bb_graph_of_proc` strangler (now single-path) |
| `src/runtime/interp/pl_runtime.h` | `bb_graph_of_pred` strangler (now single-path) |
| `src/runtime/rt/rt.c` | `rt_pl_b_end_register` (standalone Prolog registration) |
