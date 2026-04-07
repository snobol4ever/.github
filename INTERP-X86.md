# INTERP-X86.md — x86 Interpreter (C)

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** AUTHORITATIVE

---

## What It Is

The x86 interpreter executes `SM_Program` instructions in C. It is the
primary development and testing vehicle for the SCRIP stack machine.

When the interpreter passes the full corpus, the x86 emitter can emit
the same SM_Program as native x86 code with confidence — because they
execute the same instruction stream.

**Binary name:** `scrip`
**Language:** C
**Contains:** SM dispatch loop + BB-DRIVER + all 25 bb_*.c boxes

---

## Architecture

```
scrip
  ├── SM dispatch loop      (src/runtime/sm/sm_interp.c)  ← TO BE WRITTEN
  ├── SM-LOWER              (src/runtime/sm/sm_lower.c)   ← TO BE WRITTEN
  ├── BB-DRIVER             (src/runtime/dyn/stmt_exec.c) ✅
  ├── 25 bb_*.c boxes       (src/runtime/boxes/*/bb_*.c)  ✅
  ├── bb_pool               (src/runtime/asm/bb_pool.c)   ✅
  ├── bb_emit               (src/runtime/asm/bb_emit.c)   ✅ (TEXT mode)
  └── NV store / runtime    (src/runtime/snobol4/)        ✅
```

---

## Current State (2026-04-04)

`scrip` currently exists but tree-walks the IR (`EXPR_t`/`STMT_t`)
directly instead of executing `SM_Program` instructions. This is wrong.

What needs to change:
1. Write `SM-LOWER`: `Program*` → `SM_Program` (IR → instruction stream)
2. Write `sm_interp.c`: dispatch loop over `SM_Program`
3. `scrip.c` driver calls SM-LOWER then sm_interp, not the tree-walker

The BB-DRIVER, bb_*.c boxes, and bb_pool are correct and reusable as-is.

---

## Corpus Status

With the tree-walking `scrip --ir-run` (wrong architecture, but same runtime):
- Broad corpus: **177p/1f** (DYN-81, 2026-04-04)

This number proves the BB-DRIVER and boxes are correct.
It will be the baseline for the SM_Program-based interpreter.

---

## Build

```bash
cd /home/claude/one4all
ROOT=$(pwd); RT="$ROOT/src/runtime"
gcc -O0 -g -I src -I "$RT/snobol4" -I "$RT" -I "$RT/boxes/shared" \
    src/driver/scrip.c \
    src/frontend/snobol4/lex.c src/frontend/snobol4/parse.c \
    src/runtime/snobol4/snobol4.c src/runtime/snobol4/snobol4_pattern.c \
    src/runtime/dyn/stmt_exec.c src/runtime/dyn/eval_code.c \
    $(find src/runtime/boxes -name "bb_*.c") \
    -lgc -lm -o scrip
```

---

## Test

```bash
INTERP=/tmp/dyn_run_s.sh
CORPUS=/home/claude/corpus
TIMEOUT=10
bash test/run_interp_broad.sh
```

---

---

## M-DYN-S1 Implementation Plan — emit_pat_to_descr

### Key Finding

There is NO `emit_pat_expr` in `emit_x64.c`. The emitter goes straight from
the pattern AST to `emit_pat_node()` (inline NASM). There is no path that
compiles a pattern expression to a `DT_P` DESCR_t at runtime.

`snobol4_pattern.c` already has all the constructors:
`pat_lit`, `pat_cat`, `pat_alt`, `pat_arbno`, `pat_span`, `pat_break_`,
`pat_any_cs`, `pat_notany`, `pat_len`, `pat_pos`, `pat_rpos`, `pat_tab`,
`pat_rtab`, `pat_arb`, `pat_rem`, `pat_fence`, `pat_fence_p`, `pat_fail`,
`pat_abort`, `pat_succeed`, `pat_bal`, `pat_ref`, `pat_assign_imm`,
`pat_assign_cond`. All return `DESCR_t` (DT_P).

These are in `eval_code.c`'s `eval_node()` and `snobol4_pattern.c`'s
`snopat_eval()`. Already in the linked runtime.

### The New Function: emit_pat_to_descr

```c
/* Walk pattern AST, emit NASM to call snobol4_pattern.c constructors,
 * leave DT_P DESCR_t in [rbp-32]/[rbp-24]. */
static void emit_pat_to_descr(EXPR_t *pat, int slot);
```

Pattern node → NASM emission mapping:
- `E_QLIT`  → `lea rdi, [rel S_literal]` + `call pat_lit`
- `E_CONCAT`→ emit left, emit right, `call pat_cat`
- `E_ALT`   → same as concat but `call pat_alt`
- `E_ARBNO` → emit child, `call pat_arbno`
- `E_FNC("SPAN",arg)` → emit arg, strval, `call pat_span`
- `E_FNC("BREAK",arg)` → `call pat_break_`
- `E_FNC("ANY",arg)` → `call pat_any_cs`
- `E_FNC("LEN",arg)` → intval, `call pat_len`
- `E_FNC("POS",arg)` → `call pat_pos`
- `E_FNC("RPOS",arg)` → `call pat_rpos`
- `E_FNC("ARB")` → `call pat_arb` (no args)
- `E_FNC("FAIL")` → `call pat_fail`
- `E_FNC("FENCE",0)` → `call pat_fence`
- `E_FNC("FENCE",1)` → emit arg, `call pat_fence_p`
- `E_VAR` → `call pat_ref` with variable name
- `E_CAPT_IMM` ($) → emit child, `call pat_assign_imm`
- `E_CAPT_COND` (.) → `call pat_assign_cond`
- `E_INDR` (*VAR) → emit var name, `call pat_ref_val`

### The New Case 2 in emit_x64.c

Replace the entire scan-loop + emit_pat_node() + capture block with:

```nasm
; 1. Subject name
;    If s->subject is E_VAR: lea rdi, [rel S_varname]
;    Else: xor rdi, rdi  (non-lvalue — NULL subj_name)
; 2. Pattern → DT_P descriptor via emit_pat_to_descr
;    mov rdx, [rbp-64]   ; pat.lo
;    mov rcx, [rbp-56]   ; pat.hi
; 3. Replacement
;    lea r8, [repl_slot]  or  xor r8, r8
;    mov r9d, has_repl
; 4. call stmt_exec_dyn
; 5. test eax, eax / jnz S-target / jmp F-target
```

---

## Static .s Path Must Use Five Phases

The static `.s` file (output of `scrip --jit-emit --x64`) is a valid output mode —
**but it must call `stmt_exec_dyn()` at runtime for each pattern statement.**

The pattern must NOT be baked inline as NASM Byrd box code. Instead the
compiled program must build the pattern at runtime (Phase 2) and execute
it through the 5-phase executor, exactly as `CODE()` does internally.

`CODE()` and the static compiled path are **the same thing at runtime**.

### What Changes in emit_x64.c

The current pattern statement emission block (around line 5140) emits:
- `stmt_setup_subject()` + scan loop
- Inline Byrd box NASM via `emit_pat_node()`
- Direct `jmp` to `:S`/`:F` labels

This must be replaced with the 5-step `stmt_exec_dyn` call sequence above.

### What Gets Removed

- `emit_pat_node()` — the inline NASM Byrd box emitter. Deleted.
- `stmt_setup_subject()`, `stmt_apply_replacement()` call sites in the emitter.
- The scan retry loop (scan_start/scan_retry labels) in the emitter.

### The Three Output Modes Unified

All three output modes now emit the same five-phase call structure:

- **C-text**: direct C function calls. `stmt_exec_dyn(...)` in generated C.
- **S-text**: `call stmt_exec_dyn` in generated NASM `.s`. Extern declared.
- **S-binary**: `bb_insn_mov_rax_imm64(addr_of_stmt_exec_dyn)` + `bb_insn_call_rax()` in bb_pool buffer.

### RULES.md Gate for M-DYN-S1

After the change: emit-diff baseline artifacts will change (inline Byrd box NASM
replaced by `call stmt_exec_dyn`). Run `--update` to regenerate baselines.
Then: 179/0 fail. Then run invariants — same 142/142 but now going through stmt_exec_dyn.

---

## Ground Truth: SPITBOL/CSNOBOL4 Statement Execution

From `v311.sil` (CSNOBOL4 SIL source — the canonical reference):

CSNOBOL4 is an **interpreter** — it walks compiled object code descriptors
in a loop (INTRP0: increment offset, get descriptor, invoke). SPITBOL compiles
to native code but follows the same logical structure.

**SJSR** (pattern matching with replacement) — the canonical 5-phase procedure:

- Phase 1 — Subject eval: `GETD WPTR, OCBSCL, OCICL` → get subject. Can FAIL.
- Phase 2 — Pattern eval (PATVAL): `RCALL YPTR, PATVAL,,FAIL` → DT_P. Can FAIL.
- Phase 3 — Pattern match (SCNR): drives scanner via PATBRA table. Byrd box graph.
- Phase 4 — Naming (NMD): perform captures (. and $ assignments).
- Phase 5 — Replacement (ARGVAL + RPLACE): evaluate repl, write back.

**Key:** Each phase is a separate RCALL that can FAIL. This is NOT a Byrd box graph
for phases 1/2/4/5 — it's straight-line calls with failure exits. Phase 3 (the match)
is the Byrd box graph.

**Phases 1 and 2 = stack machine assembly (straight-line, FAIL→:F, no β).**
**Phase 3 = Byrd box graph inside stmt_exec_dyn (full α/β backtracking).**
**Phase 4+5 = deterministic inside stmt_exec_dyn (no backtracking).**

---

## Milestone Chain

| ID | Deliverable | Gate |
|----|-------------|------|
| **M-DYN-S1** | `emit_x64.c`: replace inline NASM with `call stmt_exec_dyn`. Stack machine for phases 1/2/4/5. | 142/142 via stmt_exec_dyn |
| **M-DYN-S2** | Verify `CODE()` and compiled `.s` agree on all 142 tests. | 142/142 both paths |
| **M-DYN-SEQ** | Unify E_SEQ/E_CONCAT: remove `fixup_val_tree`, add `stmt_seq()` runtime dispatcher. | 179/0 + 142/142 no regression |
| **M-DYN-BENCH** | Benchmark: stack machine vs Byrd box for phases 1/2/4/5 on complex patterns. | Data collected |
| **M-DYN-BB-EVAL** | (If bench shows >20% gain) Byrd box evaluation phases. 99% stackless. | Same corpus, measurable speedup |
| **M-DYN-B1** | S-binary: `bb_emit.c` raw x86, r12=DATA, Technique 2. | LIT box binary runs |
| **M-DYN-B2** | Full corpus via binary boxes. | Same pass rate as TEXT path |

---

## References

- `SCRIP-SM.md` — the instruction set this interpreter executes
- `BB-DRIVER.md` — the Phase 3 executor inside this interpreter
- `BB-GRAPH.md` — the graph structure the driver runs
- `EMITTER-X86.md` — the emitter that produces native code from same SM_Program
- `RUNTIME.md` — unified execution model (stmt_exec_dyn, EVAL, CODE)
