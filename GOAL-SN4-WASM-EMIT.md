# GOAL-SN4-WASM-EMIT.md — SNOBOL4 → WebAssembly Emitter (IR_t-based, beauty self-host)

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ NO AST WALKING IN MODES 2/3/4 — see RULES.md § "NO AST WALKING IN MODES 2, 3, OR 4"         ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  Sess 2026-05-15g removed all tree_t* dereferences from sm_interp.c (mode 2) and                ║
║  sm_jit_interp.c (mode 3). Stubs print [NO-AST] <opcode> on stderr.                              ║
║                                                                                                  ║
║  If a gate breaks with [NO-AST] FOO — write fresh SM/BB lowering for FOO.                       ║
║  Do NOT restore the AST-walking call.  Do NOT route through proc_table_call or any              ║
║  other back-door that hands a tree_t* to mode-2/3/4 code.                                       ║
║                                                                                                  ║
║  Mode 1 (`--ir-run` standalone AST interp) is unchanged and remains the reference path.        ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝


╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  A C Byrd box (C BB) is ANY C function with signature: DESCR_t foo(void *zeta, int entry)      ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                             ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

⛔ **Read before any source file:** ARCH-IR.md then ARCH-WASM.md then ARCH-EMITTER.md.
⛔ **Prereq:** GOAL-IR-EMITTER-PREREQ.md must be complete (IEP-1 through IEP-6 all ✅).

**Repo:** one4all + .github
**Goal:** scrip --sm-emit --target=wasm file.sno emits a .wat file; wat2wasm + node host runs it correctly.
**Done when:** `bash scripts/test_sn4_wasm_ladder_safe.sh` runs the ~157-program corpus ladder
(csnobol4-suite + snobol4/demo + snobol4/feat) over `scrip --sm-emit --target=wasm` + wat2wasm
+ node host, and reports **PASS ≥ 100** with no segfaults during emission. Beauty self-host
remains a downstream goal (tracked separately) but is no longer the closing gate here.

Why this scope change: beauty.sno requires DEFINE/RETURN, full pattern matching, and EVAL
host fallback — each its own multi-session lift — while the smaller corpus programs each
exercise one or two features at a time, giving a measurable per-feature progress signal.
The ladder is also the same gating model used by GOAL-SN4-JS-EMIT (currently 10/129 PASS).

---

## Pipeline

The stages pass exactly ONE structure between them:

```
tree_t  →  lower  →  IR_t  →  THIS EMITTER  →  .wat file
```

This emitter reads IR_t only. It does not read SM_Program. It produces both:
- SM-equivalent WAT function bodies for scalar IR_t nodes (push, store, call, jump, return) inside a `block`/`br_table` dispatch loop in a single `$main` function
- BB WAT function pairs (`$bb_NAME_a` / `$bb_NAME_b`) for generator IR_t nodes (pattern boxes returning matched length ≥0 or -1 on failure)

---

## Reference implementations — all BB work is already done

Every SNOBOL4 BB is already implemented in WAT. Before writing any BB emitter template for a node kind, read the corresponding function pair in `src/runtime/wasm/bb_boxes.wat`. The mapping is one-to-one:

| IR_t node kind | Reference functions in bb_boxes.wat | Notes |
|---|---|---|
| IR_PAT_LIT | `$bb_lit_new` / `$bb_lit_a` / `$bb_lit_b` | param: lit_ptr i32, lit_len i32 |
| IR_PAT_SPAN | `$bb_span_new` / `$bb_span_a` / `$bb_span_b` | param: chars_ptr i32 |
| IR_PAT_BREAK | `$bb_brk_new` / `$bb_brk_a` / `$bb_brk_b` | param: chars_ptr i32 |
| IR_PAT_ANY | `$bb_any_new` / `$bb_any_a` / `$bb_any_b` | param: chars_ptr i32 |
| IR_PAT_NOTANY | `$bb_notany_new` / `$bb_notany_a` / `$bb_notany_b` | param: chars_ptr i32 |
| IR_PAT_LEN | `$bb_len_new` / `$bb_len_a` / `$bb_len_b` | param: n i32 |
| IR_PAT_POS (rpos=0) | `$bb_pos_new` / `$bb_pos_a` / `$bb_pos_b` | param: n i32 |
| IR_PAT_POS (rpos=1) | `$bb_rpos_new` / `$bb_rpos_a` / `$bb_rpos_b` | param: n i32 |
| IR_PAT_TAB (rtab=0) | `$bb_tab_new` / `$bb_tab_a` / `$bb_tab_b` | param: n i32 |
| IR_PAT_TAB (rtab=1) | `$bb_rtab_new` / `$bb_rtab_a` / `$bb_rtab_b` | param: n i32 |
| IR_PAT_REM | `$bb_rem_new` / `$bb_rem_a` / `$bb_rem_b` | no payload |
| IR_PAT_ARB | `$bb_arb_new` / `$bb_arb_a` / `$bb_arb_b` | mutable state in arena |
| IR_PAT_ARBNO | `$bb_arbno_new` / `$bb_arbno_a` / `$bb_arbno_b` | param: child_handle i32 |
| IR_PAT_CAT | `$bb_seq_new` / `$bb_seq_a` / `$bb_seq_b` | params: left_h i32, right_h i32 |
| IR_PAT_ALT | `$bb_alt_new` / `$bb_alt_a` / `$bb_alt_b` | params: child_a_h i32, child_b_h i32 |
| IR_PAT_ASSIGN_IMM | `$bb_capture_new_imm` / `$bb_capture_a` / `$bb_capture_b` | param: varname_ptr i32, child_h i32 |
| IR_PAT_ASSIGN_COND | `$bb_capture_new_cond` / `$bb_capture_a` / `$bb_capture_b` | param: varname_ptr i32, child_h i32 |
| IR_PAT_FENCE | `$bb_fence_new` / `$bb_fence_a` / `$bb_fence_b` | no payload |
| IR_PAT_ABORT | `$bb_abort_new` / `$bb_abort_a` / `$bb_abort_b` | no payload |

The emitter's task for each node kind: write a C function `emit_wasm_bb_NODE(IR_t *nd, FILE *out, int stmt_id, int node_id)` that generates a `$bb_stmt_node_new` WAT function (allocates a 32-byte arena slot via `$arena_alloc`, writes the node's payload into the slot, returns the handle i32) plus wired calls to the pre-existing `$bb_NAME_a` and `$bb_NAME_b` function bodies from bb_boxes.wat. The emitter does NOT re-emit the α/β logic — it emits only the `_new` constructor and wiring glue; the α/β functions from bb_boxes.wat are included verbatim via `(include ...)` or concatenated at the top of the output .wat file.

Also read: `src/lower/ir_exec.c` IR_exec_node() — the interpreter for IR_t. Each case is the authoritative semantics for its node kind.

---

## WASM emission model

**Box state model:** Per ARCH-WASM.md, each box occupies a 32-byte slot in the arena at `BOX_ARENA_BASE = 0x50000`. Fields: `+0` type tag, `+4` param0, `+8` param1, `+12` param2, `+16..+28` mutable state. Box functions receive the arena offset (handle) as their sole parameter.

**Match state globals:** `$sigma` (i32 ptr), `$delta` (i32 cursor), `$omega` (i32 length) — mutable globals imported from the host environment. These mirror the C globals Σ/Δ/Ω.

**Failure sentinel:** Return `i32.const -1` for ω (failure). Return matched length ≥ 0 for γ (success). The host scan loop advances `$delta` by the returned length on success.

**Scalar nodes** emit into a single `$main` WAT function using `br_table` for SNOBOL4 GOTO dispatch (WASM has no `goto`; use `block`/`br_table` on a mutable `$pc` local):

```wat
(func $main (export "main")
  (local $pc i32)
  (local $tmp i32)
  (block $done
    (loop $dispatch
      ;; switch ($pc)
      (block $L3 (block $L2 (block $L1 (block $L0
        (local.get $pc)
        (br_table $L0 $L1 $L2 $L3)
      )
      ;; case 0: set_stno(1); $pc=1; continue
      (i32.const 1)  (call $sno_set_stno)
      (i32.const 1)  (local.set $pc)
      (br $dispatch))
      ;; case 1: push_str("hello",5); $pc=2; continue
      (i32.const 0x1000)  (i32.const 5)  (call $sno_push_str)
      (i32.const 2)  (local.set $pc)
      (br $dispatch))
      ;; case 2: store_var("OUTPUT"); $pc=3; continue
      (i32.const 0x1010)  (call $sno_store_var)
      (i32.const 3)  (local.set $pc)
      (br $dispatch))
      ;; case 3: halt_tos()
      (call $sno_halt_tos)
      (br $done))
  ))
)
```

String literals are written into a WASM `(data ...)` segment at compile time. Each unique string gets a fixed linear-memory address (starting at `0x1000`, growing upward). The emitter tracks a string table mapping sval → i32 address, deduplicating identical strings.

**Generator nodes** (all IR_PAT_* kinds) emit as calls to `$bb_NAME_new` constructors (from bb_boxes.wat) within a `$wire_pat_N` helper function, which allocates all nodes, writes their cross-handles into the arena slots, and returns the entry node handle. This wiring function is called once at SM_EXEC_GEN sites inside `$main`.

```wat
;; Emitted for a stmt-5 pattern: IR_PAT_LIT("hello") → entry
(func $wire_pat_5 (result i32)
  (local $n3 i32) (local $n4 i32)
  ;; allocate lit node: $bb_lit_new(ptr_hello, 5)
  (i32.const 0x1000)  (i32.const 5)  (call $bb_lit_new)
  (local.set $n3)
  ;; allocate term-success node (provided by runtime)
  (call $bb_term_succ_new)
  (local.set $n4)
  ;; wire n3.succ = n4, n3.fail = $g_term_fail
  (local.get $n3)  (local.get $n4)   (call $bb_set_succ)
  (local.get $n3)  (global.get $g_term_fail)  (call $bb_set_fail)
  ;; return entry handle
  (local.get $n3)
)
```

---

## sno_runtime.wat — scalar runtime functions

All SM-level operations called from `$main` live in `src/runtime/wasm/sno_runtime.wat` as exported WAT functions. This mirrors the architecture of SnoRt.j (JVM) and sno_runtime.js (JS). The value stack is a separate region of linear memory (`STACK_BASE = 0x60000`); each slot is 16 bytes (8 bytes value, 4 bytes type tag, 4 bytes padding).

| Function | WAT signature |
|---|---|
| `$sno_push_int` | (param i32) |
| `$sno_push_str` | (param $ptr i32) (param $len i32) |
| `$sno_push_real` | (param f64) |
| `$sno_push_null` | (no params) |
| `$sno_push_var` | (param $varname_ptr i32) |
| `$sno_store_var` | (param $varname_ptr i32) |
| `$sno_pop_void` | (no params) |
| `$sno_concat` | (no params) |
| `$sno_neg` | (no params) |
| `$sno_exp_op` | (no params) |
| `$sno_coerce_num` | (no params) |
| `$sno_arith` | (param $op i32) |
| `$sno_acomp` | (param $op i32) |
| `$sno_lcomp` | (param $op i32) |
| `$sno_last_ok` | (result i32) |
| `$sno_set_last_ok` | (param i32) |
| `$sno_set_stno` | (param i32) |
| `$sno_halt_tos` | (no params) |
| `$sno_call` | (param $name_ptr i32) (param $nargs i32) |
| `$sno_do_return` | (param $kind i32) (param $cond i32) |
| `$sno_init` | (no params) |
| `$sno_finalize` | (no params) |

INPUT/OUTPUT: the WASM module imports `host.read_line` and `host.write_line` from the JS host. The `$sno_store_var` function checks if the varname is "OUTPUT" (by pointer comparison against the string table) and calls `host.write_line`. The `$sno_push_var` function checks for "INPUT" and calls `host.read_line`.

⚠️ **EVAL/CODE limitation (per ARCH-WASM.md):** WASM cannot do EVAL or CODE natively. Beauty.sno uses `EVAL()` heavily. Strategy: emit a `host.eval_fallback` import; the JS host runs a sub-scrip process for EVAL expressions. This is acceptable for beauty self-host correctness; performance is a later concern.

---

## JS host wrapper

The emitted .wat file is not self-contained — it requires a JS host to supply I/O and string services. The emitter also generates a companion `prog.mjs` host file (or the smoke script supplies a generic one):

```js
// Generic WASM host for emitted SNOBOL4 .wasm files
import { readFileSync } from 'fs';
import { createInterface } from 'readline';

const rl = createInterface({ input: process.stdin });
const lines = [];
rl.on('line', l => lines.push(l));

const wasmBytes = readFileSync(process.argv[2]);
const { instance } = await WebAssembly.instantiate(wasmBytes, {
  env: { memory: new WebAssembly.Memory({ initial: 8 }) },
  host: {
    write_line: (ptr, len) => { /* decode from linear memory, print */ },
    read_line:  (ptr_out)  => { /* write next line from `lines` into memory, return len */ },
    eval_fallback: (expr_ptr, expr_len, out_ptr) => { /* shell out to scrip --eval */ },
  }
});
instance.exports.main();
```

A generic host script lives at `src/runtime/wasm/sno_host.mjs` and is reused by all emitted programs.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
apt-get install -y wabt 2>/dev/null || true    # provides wat2wasm, wasm-validate
bash /home/claude/one4all/scripts/build_scrip.sh
wat2wasm --version
node --version
```

---

## Steps

All steps here build on top of GOAL-IR-EMITTER-PREREQ (IEP-1..6). The visitor infrastructure, wiring phase, and scalar node emission are already done for x86/JVM/JS. This GOAL adds WASM-specific completeness and drives to beauty self-host.

### SN4-WASM-1 — sno_runtime.wat: complete WASM scalar runtime

- [x] **SN4-WASM-1 ✅** — Create `src/runtime/wasm/sno_runtime.wat`. All exported functions listed in the table above. The value stack lives at `STACK_BASE = 0x60000`; each slot is 16 bytes. Type tag constants: 0=integer, 1=string, 2=real, 3=null. Variables are stored in a hash table region starting at `VAR_BASE = 0x80000`. OUTPUT: when `store_var` is called with the "OUTPUT" varname pointer, call imported `host.write_line`. INPUT: when `push_var` is called with "INPUT", call imported `host.read_line`.

  **Closed:** prior session 2026-05-15 commit `468910b0`. Implementation actually lays out memory as: stack 0x00000, var table 0x10000 (was 0xA0000 — fixed this session), runtime keywords 0x31xxx, BB arena 0x50000, dynamic str heap 0x80000 (was 0x60000 — fixed this session, collided with arena). 475-line runtime; smoke gate passes.

  **Gate:** Hand-written test .wat file calling `$sno_push_str` + `$sno_halt_tos` assembles with wat2wasm and runs under the generic host, printing the string. ✅

### SN4-WASM-2 — Complete all 19 BB constructor emitters for WASM

- [x] **SN4-WASM-2 ✅** — For each IR_PAT_* kind in the table above, implement `emit_wasm_bb_NODE(IR_t *nd, FILE *out, int stmt_id, int node_id)`. The emitter writes a `$bb_stmt_node_new` WAT function that: (1) calls `$arena_alloc`, (2) writes the node's payload into the returned arena slot via `i32.store`, (3) returns the handle.

  **Closed:** prior session 2026-05-15 commit `685183c1`. 19 BB constructor emitters present in `src/emitter/emit_wasm.c` (functions `emit_wasm_bb_lit` through `emit_wasm_bb_callout`).

  **Gate:** All 19 constructor functions emit valid WAT. ✅

### SN4-WASM-3 — Scalar emitter (SM_Program walker) + wire into scrip.c

- [x] **SN4-WASM-3 ✅** — Create `src/emitter/emit_wasm.c` with `emit_wasm_from_sm(SM_Program *prog, FILE *out)` and `emit_wasm_program(tree_t *tree, FILE *out)` entry point. The SM walker converts SM opcodes to `call $sno_NAME` WAT instructions, wrapped in a `$main` function using `block`/`br_table` dispatch (actually implemented as nested if-else dispatch — same semantics, simpler to emit). Prepend bb_boxes.wat and sno_runtime.wat content (or reference them via WAT module linking). Wire `--sm-emit --target=wasm` in `scrip.c`.

  **Closed:** prior session 2026-05-15 commit `685183c1` for emit_wasm.c.  scrip.c `--target=wasm` dispatch wiring was missing from that commit (target was falling through to the IR-block stub, producing empty output) — **wired up this session**: extern declaration + dispatch branch in scrip.c + Makefile entry + duplicate `g_emit_vtable_wasm` removed from emit_wasm.c (it lives in emit_ir_targets.c).

  **Gate:** `scrip --sm-emit --target=wasm hello.sno > hello.wat && wat2wasm hello.wat -o hello.wasm && node sno_host.mjs hello.wasm` prints `Hello World`. ✅

### SN4-WASM-4 — Smoke 7/7

- [x] **SN4-WASM-4 ✅** — Write `scripts/test_smoke_snobol4_wasm.sh`. Run all 7 SNOBOL4 smoke programs via `scrip --sm-emit --target=wasm`, assemble with wat2wasm, run with node + sno_host.mjs, compare output to oracle `.ref` files.

  **Closed:** prior session 2026-05-15 commit `685183c1`. Verified holding this session after memory-layout repairs: PASS=7 FAIL=0.

  **Gate:** 7/7 PASS. ✅

### SN4-WASM-5 — Corpus ladder coverage (PASS ≥ 100 / ~157)

- [ ] **SN4-WASM-5** — Achieve PASS ≥ 100 on `scripts/test_sn4_wasm_ladder_safe.sh`, the per-program corpus ladder over csnobol4-suite, snobol4/demo, and snobol4/feat. Each `.sno` is emitted via `scrip --sm-emit --target=wasm`, assembled with wat2wasm, run under `node sno_host.mjs`, and its stdout diffed against the co-located `.ref` oracle. Fresh process per program (so one bad program can't take the batch down).

  **Gate:** ladder reports PASS ≥ 100 with no scrip segfaults during emission. (Beauty self-host is no longer the closing gate; deferred to a later goal.)

  **Status (sess 2026-05-15, Claude Opus 4.7, one4all `9c2c26a5`):** ladder baseline PASS=11 FAIL=118 of 129 programs (8.5%). Currently passing: `cat`, `collect`, `end`, `hello`, `loop`, `noexec`, `openo`, `punch`, `sleep`, `space2`, `str`. One emission-time scrip segfault observed during the batch — fix is in 5d-pre.

#### Sub-steps for SN4-WASM-5

- [x] **SN4-WASM-5a ✅** — Wire scrip.c `--target=wasm` dispatch. Beauty was producing empty `.wat` output before this. (See SN4-WASM-3 note above for the actual fix.)

- [x] **SN4-WASM-5b ✅** — Fix memory-layout collisions: dynamic str heap was at 0x60000 colliding with BB arena at 0x50000; var table was at 0xA0000 with no clear separation. Moved var table to 0x10000, dynamic str heap to 0x80000, emitter literal data to 0x100000 (1MB), grew emitter memory import from 8 → 32 pages to match runtime. `$sno_init` now zeros the var table. (Layout comment in sno_runtime.wat updated to reflect actual code.)

- [x] **SN4-WASM-5c ✅** — Implement basic builtins in `$sno_call`: LT, GT, EQ, NE, GE, LE, IDENT, DIFFER. Previously the entire function was a stub returning null with `last_ok` unchanged; every conditional fell through erroneously, causing infinite loops on simple while-style tests. Loop test now correctly prints 1..N then exits when LT(N,N) fails.

- [x] **SN4-WASM-5-LADDER ✅** — Add `scripts/test_sn4_wasm_ladder_safe.sh` mirroring the JS ladder structure. Baseline PASS=11/129.

- [ ] **SN4-WASM-5d** — Fix or skip the scrip emission-time segfault on `corpus/programs/csnobol4-suite/scanerr.sno`. This is a **pre-existing scrip frontend bug** — confirmed against the JS ladder which segfaults on the same program (SESSION-2026-05-15-HANDOFF.md, sec 2). Not WASM-specific. Two options: (a) fix the upstream frontend bug, (b) skip `scanerr.sno` in the ladder script with a documented one-line guard until upstream is fixed.

- [ ] **SN4-WASM-5e** — Implement remaining single-arg / 2-arg scalar builtins in `$sno_call`: SIZE, INTEGER, STRING, CONVERT, DATATYPE, TRIM, DUPL, SUBSTR, REPLACE, REVERSE, ITEM. Each adds a `(data ...)` name segment and a dispatch branch. Should unlock ~20-40 ladder programs.

- [ ] **SN4-WASM-5f** — Implement user-defined functions: SM_DEFINE (build name→PC table), SM_CALL_FN for user procs (push return-PC, jump), SM_DO_RETURN (pop return-PC, jump). Needs a return-PC stack in linear memory and the `$main` dispatch loop to accept indirect PC writes (it already does, since the loop reads `$pc` mutably each iteration). Should unlock another large batch of programs that use DEFINE.

- [ ] **SN4-WASM-5g** — Wire pattern matching: route SM_EXEC_GEN sites through the BB arena (handles already created via `emit_wasm_bb_NEW` constructors per SN4-WASM-2), allocate match state, drive scan loop, capture results. The α/β bodies in `bb_boxes.wat` are pre-written; this step is just plumbing `$main` to call them.

- [ ] **SN4-WASM-5h** — (Optional, downstream of 5g) EVAL fallback in `sno_host.mjs`: import `host.eval_fallback`, spawn `scrip --eval` as child process, marshal result back. Required only for the few corpus programs that use EVAL().

---

## Key invariants

- **Reads IR_t only.** This emitter never reads SM_Program. IR_t is the sole input.
- **19 BB kinds, all pre-implemented.** Every α/β body is already written in bb_boxes.wat. The emitter writes only `_new` constructors and wiring; it does NOT re-emit α/β logic.
- **WASM has no goto.** All backward jumps must use `block`/`loop`/`br_table`. The SM dispatch loop uses `loop $dispatch` + `br_table` over a mutable `$pc` local.
- **Failure sentinel is `i32.const -1`.** All box α/β functions return i32. Success returns matched length ≥ 0; failure returns -1.
- **All strings in linear memory data segments.** The emitter maintains a string table; identical strings share one `(data ...)` entry. String base address: `0x1000`, growing upward.
- **Arena base: `0x50000`.** Each box slot: 32 bytes. Arena grows upward from base. Never overwrite the bb_boxes.wat arena layout.
- **EVAL/CODE limitation acknowledged.** Use `host.eval_fallback` import for beauty self-host. Not a blocker; fallback is correct, just slow.
- **Flag:** `--sm-emit --target=wasm` (not `--jit-emit --wasm`).
- **Build tool:** `wat2wasm` from wabt. Validate with `wasm-validate` before running.

---

## State

```
watermark: SN4-WASM-5d NEXT (5a/5b/5c/5-LADDER ✅ this session; 1-4 ✅ prior sessions)
head: one4all <to-be-set-by-handoff>; .github <to-be-set-by-handoff>
session: 2026-05-15 (Claude Opus 4.7) — SN4-WASM-5 partial progress; goal pivot beauty → ladder
progress: prereqs (IEP-1..6) ✅; SN4-WASM-1 ✅; SN4-WASM-2 ✅; SN4-WASM-3 ✅ (scrip.c dispatch wired);
          SN4-WASM-4 ✅ (smoke 7/7 holding); SN4-WASM-5a/5b/5c ✅; SN4-WASM-5-LADDER ✅ (baseline 11/129);
          SN4-WASM-5d-h remaining.
gate this session: ladder PASS=11 FAIL=118 / 129; smoke_snobol4_wasm 7/7 holding;
                   smoke_snobol4 7/7, smoke_snocone 5/5,
                   crosscheck_snobol4 6/6, crosscheck_snocone 8/8,
                   broker 23/49 (unchanged baseline).
goal pivot: closing gate is ladder PASS ≥ 100, not beauty self-host.
            beauty deferred to a later goal that depends on the full ladder + EVAL fallback.
```
