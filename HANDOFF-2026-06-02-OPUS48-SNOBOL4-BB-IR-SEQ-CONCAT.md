# HANDOFF 2026-06-02 (Opus 4.8) — SNOBOL4-BB: IR_SEQ value-concat (`OUTPUT = 'ab' 'cd'` → `abcd`, mode-3 2/6 → 3/6)

## Result

The `concat` smoke is GREEN in mode-3 (`--run`) and byte-matches the SPITBOL oracle
(`/home/claude/x64/bin/sbl -b`) across every form tried:

| form | program | result |
|------|---------|--------|
| two literals     | `OUTPUT = 'ab' 'cd'`              | `abcd` |
| three literals   | `OUTPUT = 'A' 'B' 'C'`           | `ABC` |
| int coercion     | `OUTPUT = 'n=' 7`                | `n=7` |
| null-string left | `OUTPUT = '' 'xyz'`              | `xyz` |
| null-string right| `OUTPUT = 'xyz' ''`             | `xyz` |
| var concat (`;`) | `A = 'foo'; B = 'bar'; OUTPUT = A B` | `foobar` |
| var concat (lines)| three statements, `OUTPUT = A B`| `foobar` |
| var + literal    | `A = 'hi'; OUTPUT = A '!'`       | `hi!` |

Prior-passing smokes unchanged: `output` (`'hello'`) and `arith` (`2 + 3` → `5`) still green.

## Mechanism (NOT a STITCH_SEQ box)

SPITBOL manual ch.3: juxtaposition appends the right string to the end of the left; non-string
operands are coerced to string form; if either operand is the null string the other is returned
UNCHANGED (not coerced). All of this is already implemented by `binop_apply(BINOP_CONCAT, lv, rv)`.

The concat reuses the EXISTING runtime helper `rt_gvar_assign_concat(name, left_graph, right_graph)`
— **defined in `src/interp/IR_interp.c`** and exported in `libscrip_rt.so`. It `bb_reset`s and
`IR_interp_once`s each operand sub-graph, applies `binop_apply(BINOP_CONCAT, …)`, and `NV_SET_fn`s the
result into the destination variable. The operand sub-graphs for `'ab' 'cd'` are the two
`lower_value_subgraph` blocks the lowerer attaches to the `IR_SEQ` node as `counter` (left) and `ival`
(right). For var operands the sub-graph is an `IR_VAR` node whose `IR_interp_once` does `NV_GET_fn` —
the same global name table the native `bb_gvar_assign` lit_s/var arms wrote, so the value is found.

NOTE: the `rt.c` `rt_concat` (a `STACKLESS_ABORT` stub) is **unrelated dead scaffolding** and was NOT
touched. The frontier note that said "give `rt_concat` a real impl" was imprecise; the real concat
path is `rt_gvar_assign_concat`.

## The 5 edits (all gated byte-identical for the rest of the suite)

1. **`src/emitter/emit_globals.h`** — two new `sm_emit_t` fields: `int64_t op_a_counter`,
   `int64_t op_a_ival_sg`.
2. **`src/emitter/emit_core.c` `walk_bb_node`** — promote them from `nd->α` at dispatch:
   `g_emit.op_a_counter = nd->α ? nd->α->counter : 0;`
   `g_emit.op_a_ival_sg = nd->α ? nd->α->ival : 0;`
   so the box reads the concat sub-graph pointers from `_` (PEERS / no-pBB rule), never `pBB`.
3. **`src/emitter/BB_templates/bb_gvar_assign.cpp`** — replaced the concat `x86_bomb` with the IR_SEQ
   arm. Declares `int rt_gvar_assign_concat(const char*, void*, void*)` in the file's `extern "C"`
   block. BINARY arm: `lea rdi,[rip+dst]` (RO), `movabs rsi,left_graph`, `movabs rdx,right_graph`
   (the `op_a_counter`/`op_a_ival_sg` sub-graph pointers — valid in the mode-3 in-process JIT),
   `call rt_gvar_assign_concat`, `jmp γ` / `def β` / `jmp ω`. TEXT(mode-4) arm is a LOUD `x86_bomb`
   because the sub-graph addresses are not relocatable (same status as SNOBOL m4 0/6, pending the
   LOWER four-port wiring).
4. **`src/emitter/emit_bb.c`** — new `flat_drive_gvar_seq_passthrough` (`EMIT_PAIR_JMP(lbl_γ)` +
   `EMIT_PAIR_DEF_JMP(lbl_β, lbl_ω)`): the concat-descriptor IR_SEQ node emits a pure pass-through.
5. **`src/emitter/emit_bb.c` `walk_bb_flat`** — `case IR_SEQ` now branches: in the SNOBOL gvar chain
   (`g_gvar_flat_chain && nd->dval == 1.0`) it calls the pass-through; otherwise `flat_drive_seq` as
   before (Icon/value-expr unchanged).

## CRITICAL FINDING — why "skip the IR_SEQ node" was wrong

The first attempt removed the `IR_SEQ(dval==1.0)` node from the `codegen_gvar_flat_chain_body`
`nodes[]` array (it generates no standalone code). This BROKE γ/ω threading: a node that precedes the
concat statement (e.g. the `A='foo'` assignment in a multi-statement program) threads its γ *to* the
IR_SEQ node. With the IR_SEQ removed from `nodes[]`, the per-node label lookup couldn't find it and
fell back to the global success-exit label `lbl_γ` — so after `A='foo'` control jumped straight to the
function epilogue, skipping the concat entirely. Symptom: a preceding `OUTPUT='before'` printed, then
nothing (no `after`, no concat, exit 0).

The fix keeps the IR_SEQ node in `nodes[]` and gives it a pass-through emit, so its label exists and
threading resolves correctly. `gvar_chain_arity` already returns 0 for `IR_SEQ(dval==1.0)`, so
`gvar_stmt_operand_refs` (the stack-based arity pass) correctly sets the consuming `IR_ASSIGN`'s
`α = IR_SEQ`, which is what `bb_gvar_assign`'s IR_SEQ arm reads.

## ⚠ BUILD NOTE (cost a detour)

The mode-3 emit path runs the emitter compiled into the **`scrip` binary**, NOT just
`out/libscrip_rt.so`. After editing any `src/emitter/**` file you MUST rebuild BOTH:
`bash scripts/build_scrip.sh && make libscrip_rt`. Rebuilding only the `.so` leaves stale emitter
code in `scrip` and you test the wrong thing (debug traces not firing, phantom pass/fail).

## Gates (GREEN)

- SNOBOL4 m2 **7/7 HARD** / m3 **3/6** (output+arith+concat; MODE3_MIN floor raised 2→3) / m4 0/6
- Icon m2 **12/12 HARD** (byte-neutral — shared touches are SNOBOL-guarded or additive) / m3 3/12 / m4 3/12
- `test_gate_no_bb_bin_t` 0 · `test_gate_no_lang_names` (LI-FENCE) holds · `audit_concurrency_invariants` OK
  (FACT RULES byte-identical ×3 untouched) · `prove_lower2` PASS · `g_vstack` **0**

## NEXT (smallest real unit)

`pattern` (`S 'b' = 'X'` → `aXc`) → IR kind 28 = **IR_SCAN**, the ch.18 unanchored OUTER match loop
(`bb_match` + SUBJECT subject-slot wiring). Then `goto_s` (also IR_SCAN), then `define` (DEFINE
registration + SNOBOL4 call frame + RETURN). The IR_SCAN pattern engine is the LONG POLE for the
SNOBOL4 corpus.
