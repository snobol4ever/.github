# EMITTER-COMMON.md — Common Emitter Architecture

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** AUTHORITATIVE

---

## What It Is

The EMITTER walks a `SM_Program` (flat array of `SM_Instr`) and produces
native code for a target platform. Every backend emitter shares this
structure — only the output format differs.

---

## The Emitter Contract

Input: `SM_Program` — the same instruction stream the INTERP executes.
Output: native code for the target platform.

**The fundamental guarantee:** if INTERP passes the full corpus on a
given `SM_Program`, the EMITTER for that same `SM_Program` is correct
by construction — because they execute the same instructions.

---

## Per-Instruction Emit

Each `SM_Op` maps to an emit function in every backend:

```c
void emit_instr(SM_Instr *instr, EmitState *st) {
    switch (instr->op) {
        case SM_PUSH_VAR:    emit_push_var(instr->u.name, st);   break;
        case SM_PAT_LIT:     emit_pat_lit(instr->u.str, st);     break;
        case SM_PAT_ALT:     emit_pat_alt(st);                   break;
        case SM_EXEC_STMT:   emit_exec_stmt(&instr->u.exec, st); break;
        case SM_JUMP_S:      emit_jump_s(instr->u.target, st);   break;
        /* ... all SM_Op cases ... */
    }
}
```

One switch. One case per instruction. No tree-walking. No IR access.

---

## Two-Mode Emission (x86 only)

The x86 emitter has two modes for BB-GRAPH generation:
- `EMIT_TEXT` — writes NASM .s text → assembled by nasm
- `EMIT_BINARY` — writes raw x86 bytes into bb_pool → executed directly

Both modes are driven by the same `SM_PAT_*` instruction sequence.
The mode switch is global state in `bb_emit.c`.

See `BB-GEN-X86-BIN.md` and `BB-GEN-X86-TEXT.md`.

---

## Label Resolution

Forward jumps (`SM_JUMP`, `SM_JUMP_S`, `SM_JUMP_F`) reference label
indices. The emitter resolves these in two passes:

1. First pass: record byte offset (or JVM pc, or .NET offset) for each
   `SM_LABEL` instruction.
2. Second pass: patch all forward jump targets.

Or: single pass with a backpatch list (same technique as `bb_emit.c`).

---

## Per-Backend Emitters

| Backend | Doc | Output | Status |
|---------|-----|--------|--------|
| x86 | `EMITTER-X86.md` | .s file (TEXT) or bb_pool bytes (BINARY) | ⬜ needs SM_Program input |
| JVM | `EMITTER-JVM.md` | .j Jasmin bytecode | ⬜ in progress |
| .NET | `EMITTER-NET.md` | .il MSIL | ⬜ in progress |
| JS | `EMITTER-JS.md` | .js source | ⬜ in progress |
| WASM | `ARCHIVE-WASM-BACKEND.md` | .wat text | ⛔ parked |

---

## Multi-Backend Single-IR Optimization

**scrip-cc has an optimization that gcc does not have.**

A single invocation compiling one source file can build the IR tree **once** and
pass it to **multiple backends** in sequence. The IR tree is constructed once by
the frontend (parse → lower → IR) and then each requested backend (`-asm`, `-jvm`,
`-net`, `-c`) walks the same in-memory tree.

**Rules that follow from this:**

1. **IR tree must be read-only after construction.** Any backend that mutates the
   tree corrupts subsequent backends. All backends treat IR as immutable once the
   frontend returns.

2. **Per-backend state must be fully reset between backends.** Each backend entry
   point (`asm_emit`, `jvm_emit`, `net_emit`, `c_emit`) must zero its own statics
   before running.

3. **Lowering passes** (`fixup_val_tree`, snocone lowering, Prolog lowering) run
   as part of the frontend and produce the final IR. They must not be re-run per
   backend. Called exactly once, before the first backend entry point, inside
   `compile_one`.

4. **Shared helpers** (e.g., `emit_concat_fold` in `ir_emit_common.c`) called from
   multiple backends must not cache pointers into the tree across backend runs if
   memory arenas are recycled.

**Debug aid:** Add an `IR_FROZEN` flag (static bool in `ir.c`) that backends set at
entry and the IR node allocator checks — any `expr_new()` call while frozen is a bug.

---

## SIL Naming Conventions (canonical, Sessions 84–85)

| Category | Names |
|----------|-------|
| Types | `DESCR_t`, `DTYPE_t` |
| Fields | `.v` (type), `.a` (address), `.f` (flags) |
| Values | `NULVCL`, `STRVAL()`, `INTVAL()`, `FAILDESCR`, `IS_FAIL_fn()` |
| Vars | `NV_GET_fn`, `NV_SET_fn` |
| Functions | `APLY_fn`, `DEFINE_fn`, `CONC_fn`, `FNCEX_fn`, `MAKE_TREE_fn` |
| Stack | `NPUSH_fn`, `NPOP_fn`, `NINC_fn`, `PUSH_fn`, `POP_fn`, `TOP_fn` |
| Pattern | `XCHR` (lit), `XARBN` (arbno), `XNME` (`.`), `XDNME`/`XFNME` (`$`) |
| Expr IR | `E_MPY`, `E_OR`, `E_NAM`, `E_DOL`, `E_FNC` |

Intentional lowercase (domain primitives): `eq/ne/lt/le`, `add/sub/mul`, `ident/differ`.
Known bug: `ARRAY_VAL` uses `.a`, should be `.arr` — `snobol4.h:399`, dormant.

---

## Three-Column Generated C Format

```
Col 1  Label   chars  0..17
Col 2  Stmt    chars 18..59
Col 3  Goto    chars 60+
```

Macros: `PLG(label,goto)`, `PL(label,goto,stmt)`, `PS(goto,cond)`, `PG(goto)`.
`emit_pretty.h` shared by `emit.c` and `emit_byrd.c`.
`emit_byrd.c` uses 3-column ✅. `emit.c` still uses raw `E(...)` — fix after M-BEAUTY-FULL.

---

## CNode IR — emit_cnode.c (M-CNODE ✅ ac54bd2)

Solves: streaming printers make irrevocable formatting decisions with no lookahead.

Three phases (same as beauty.sno's pp/qq split):
- **Build:** `build_expr()` → CNode tree. No output.
- **Measure:** `cn_flat_width(n, limit)` — early exit. The "qq" lookahead.
- **Print:** `pp_cnode()` — inline if fits, multiline+indent if not.

```c
typedef enum { CN_RAW, CN_CALL, CN_SEQ } CNodeKind;
typedef struct CNode {
    CNodeKind kind;
    const char *text;
    struct CNode **args; int nargs;
    struct CNode *left, *right;
} CNode;
```

Column budget: 120 chars. Arena allocator per statement.

---

## Artifact Snapshot Protocol

End of every session touching `emit*.c` or `runtime/`:

```bash
INC=/home/claude/corpus/programs/inc
BEAUTY=/home/claude/corpus/programs/beauty/beauty.sno
src/scrip-cc/scrip-cc -trampoline -I$INC $BEAUTY > /tmp/beauty_tramp_candidate.c
LAST=$(ls artifacts/beauty_tramp_session*.c 2>/dev/null | sort -V | tail -1)
md5sum $LAST /tmp/beauty_tramp_candidate.c
# CHANGED → cp /tmp/beauty_tramp_candidate.c artifacts/beauty_tramp_sessionN.c
# SAME    → update artifacts/README.md "no change" note only
```

README records: session N, date, md5, line count, compile status, active bug.

---

## References

- `SCRIP-SM.md` — the SM_Instr / SM_Program definition
- `IR.md` — what SM-LOWER compiles FROM (emitters never see IR directly)
- `BB-GEN-X86-BIN.md`, `BB-GEN-X86-TEXT.md` — x86 BB generation
- `GENERAL-SIL-HERITAGE.md` — full SIL naming lineage

---

## Four Techniques for *X (C Backend History — reference)

These techniques were developed for the C backend and inform the general architecture:

### Technique 1 — Struct-passing (C target, current for C-text path)

Each named pattern → C function `pat_X(pat_X_t **zz, int entry)`.
All locals in typed struct. calloc on entry==0. beta dispatch on entry==1.

```c
typedef struct pat_Parse_t {
    int64_t  saved_7;
    int      arbno_depth;
    int64_t  arbno_stack[64];
    struct pat_Command_t *Command_z;
} pat_Parse_t;

static SnoVal pat_Parse(pat_Parse_t **zz, int entry) {
    pat_Parse_t *z = *zz;
    if (entry == 0) { z = *zz = calloc(1, sizeof(*z)); goto Parse_alpha; }
    if (entry == 1) { goto Parse_beta; }
    Parse_alpha: ...Byrd box labeled gotos...
    Parse_gamma: return matched_val;
    Parse_omega: return FAIL_VAL;
}
```

### Technique 2 — mmap + memcpy + relocate (ASM/native, post-SM_Program)

See `EMITTER-X86.md` §Technique 2 for full detail.

### Technique 3 — Iota functions (concept, revisit post-M-BEAUTY-FULL)

Every labeled block → own tiny C function (for addressability). One flat concatenated
struct for all locals. Bridges T1 and T2.

### Technique 4 — GCC &&label port table (concept, nonstandard)

Entire pattern in ONE function. GCC `&&label` → `void*` port table.
`goto *ports[entry]`. GCC/Clang only — not standard C.

---

## Block Function Model ("The New Plan", 2026-03-14)

```c
typedef block_fn_t (*block_fn_t)(void);
block_fn_t pc = block_START;
while (pc) pc = pc();    /* entire engine */
```

Every stmt → C function returning next block address (S-label or F-label).
Flat concatenated locals struct per block.

| SNOBOL4 | Mechanism |
|---------|-----------| 
| `:(L42)` | `return block_L42` |
| `*X` static | call `block_X` directly |
| `*X` dynamic | X holds `block_fn_t`, call it |
| `EVAL(str)` | TCC compile → degenerate stmt fn |
| `CODE(str)` | TCC compile → block fn sequence |

Sprint map: `trampoline` → `stmt-fn` → `block-fn` → `pattern-block` → `code-eval`.

---

## setjmp Model (C backend)

| Feature | Status |
|---------|--------|
| Per-function setjmp | ✅ `emit.c emit_fn()` |
| `push/pop_abort_handler` macros | ✅ `runtime_shim.h` |
| Per-statement setjmp | ❌ `emit.c emit_stmt()` |
| Glob-sequence optimization | ❌ needs reachability pass |
| Non-Gimpel DEFINE guard | ❌ `emit.c emit_stmt()` |

**Glob-sequence:** consecutive stmts in DEFINE body with NO internal label targets
share ONE setjmp. Stmts that ARE label targets start a new boundary.
**Non-Gimpel DEFINE:** bare `DEFINE(...)` mid-program gets own standalone guard.

---

## Save/Restore in DEFINE Functions (C backend)

**WRONG (current):** C-local `var_get/var_set` preamble/postamble in `emit_fn()`.
**RIGHT (target):** α port saves caller locals into struct; γ/ω ports restore.
Makes save/restore explicit in 3-column format. Prerequisite for M-COMPILED-SELF.

---

## Architecture Decisions (C backend — Locked)

| # | Decision |
|---|----------|
| D1 | Memory: Boehm GC (`libgc`) |
| D2 | Tree children: realloc'd dynamic array |
| D3 | cstack: thread-local (`__thread MatchState *`) |
| D4 | Tracing: full impl, `doDebug=0` = zero cost |
| D5 | `mock_engine.c` only in beauty_full_bin — `engine.c` fully superseded |
| D6 | All vars through `NV_GET_fn`/`NV_SET_fn` — `is_fn_local` suppression removed |
| D7 | `T_FNCALL` wrapper universal — all DEFINE'd functions save/restore on entry/exit |
