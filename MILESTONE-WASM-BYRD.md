# MILESTONE: M-SW-BYRD — SNOBOL4 WASM Full Byrd-Box Rewrite

## Summary

Replace `emit_wasm.c`'s PC-loop + `emit_pattern_node` scaffold with a
full Byrd-box emitter using `return_call` tail-call WAT functions for
every statement phase and every pattern node — exactly mirroring the
x64 (`emit_byrd_asm.c`) and JVM (`emit_jvm.c`) backends.

The current PC-loop model handles statement-level goto correctly but
is architecturally wrong for pattern matching: it cannot backtrack,
cannot handle multi-position alternation, and cannot support
user-defined pattern functions.

## Statement-Level Byrd-Box Model (from x64/JVM reference)

Each SNOBOL4 statement has three phases, each of which can fail:

```
  subject eval  ──γ──▶  pattern match  ──γ──▶  replacement eval
       │                      │                       │
       ω                      ω                       γ → :S(target)
       │                      │
       ▼                      ▼
    :F(target)            advance scan cursor → retry α
                          (exhausted → :F(target))
```

**The fence between subject and pattern is the most important boundary:**
- Subject eval γ → pattern α  (subject succeeded, start matching)
- Subject eval ω → statement :F  (subject itself failed — e.g. undefined var)
- Pattern γ → replacement α  (match succeeded, apply replacement)
- Pattern ω → scan-advance or :F  (no match at this cursor, try next position)
- Replacement γ → :S target
- Replacement ω → :F target  (replacement can fail e.g. undefined rhs)

WAT encoding — each phase is a WAT `(func ...)`, transitions are `return_call`:

```wat
;; Statement N subject eval
(func $sN_subj_α (result i32)
  ;; eval subject expression → (off len) globals
  ;; if subject fails: return_call $sN_stmt_ω
  return_call $sN_scan_α)

;; Scan loop: try pattern at positions 0..subj_len
(func $sN_scan_α (result i32)
  ;; set cursor = scan_pos
  return_call $sN_pat_α)   ;; enter pattern tree

(func $sN_scan_ω (result i32)   ;; pattern failed at this position
  ;; increment scan_pos; if scan_pos > subj_len: return_call $sN_stmt_ω
  return_call $sN_scan_α)       ;; retry

;; Pattern tree: N nodes, each with α and β ports
;; (see Pattern Node Encoding below)

(func $sN_pat_γ (result i32)    ;; pattern matched
  ;; eval replacement (if any)
  return_call $sN_repl_α)

(func $sN_repl_γ (result i32)   ;; replacement succeeded
  return_call $goto_S_target)

(func $sN_stmt_ω (result i32)   ;; whole statement failed
  return_call $goto_F_target)
```

## Pattern Node Encoding (per EKind)

Each pattern node gets two WAT functions: α (try) and β (backtrack).
Mirrors x64 `emit_pat_node` and JVM `emit_jvm_pat_node`.

```
E_QLIT  literal string:
  α: sno_lit_match(subj, cursor, off, len) → if match: cursor+=len, return_call γ
                                            → else: return_call β
  β: return_call outer_β  (no internal backtrack)

E_SEQ  sequential:
  α: return_call left_α
  left_γ  = right_α
  right_β = left_β   (backtrack left)
  right_γ = outer_γ

E_ALT  alternation:
  α: save cursor; return_call left_α
  left_β: restore cursor; return_call right_α
  right_β = outer_β
  left_γ = right_γ = outer_γ

E_ARBNO  zero-or-more:
  α: save cursor; try inner_α  (zero = return_call outer_γ)
  inner_γ: if cursor==saved: return_call outer_γ (zero-advance guard)
           else save cursor; try inner_α again
  inner_β: restore cursor; return_call outer_γ  (backtrack to zero)

E_ARB:
  α: return_call outer_γ  (match empty)
  β: try next longer match up to subj_len

E_CAPT_COND (.var):
  α: save before-cursor; return_call child_α
  child_γ: store subj[before..cursor] in var; return_call outer_γ
  child_β: return_call outer_β
```

## What to Rewrite

1. **New file: `src/backend/emit_wasm_sno.c`** — SNOBOL4 Byrd-box WASM emitter.
   Replaces `emit_wasm.c`'s `emit_main_body` + `emit_pattern_node`.
   Uses `emit_wasm.h` shared API (strlit, data_segment, runtime_imports).

   OR: rename/refactor `emit_wasm.c` in-place, replacing `emit_main_body`
   and `emit_pattern_node` with Byrd-box functions.

2. **Keep from `emit_wasm.c`:**
   - String literal table (strlit_intern/abs/len/reset — shared API)
   - `emit_wasm_expr` (inline value expression — used by subject/replacement eval)
   - `emit_runtime_imports` / `emit_wasm_runtime_imports_sno_base`
   - Variable globals table

3. **Replace in `emit_wasm.c`:**
   - `emit_main_body` — PC-loop → per-statement Byrd-box function emitter
   - `emit_pattern_node` — cursor-local structured → α/β tail-call functions

4. **Counter:** `static int wasm_sno_ctr` — monotonic, never resets.
   Label format: `$sN_phase_port` e.g. `$s42_scan_α`, `$s42_pat7_α`.

## Reference Files

| Backend | Statement wiring | Pattern nodes |
|---------|-----------------|---------------|
| x64 | `emit_x64.c` lines 5033–5200 | `emit_x64.c:emit_pat_node` |
| JVM | `emit_jvm.c` lines 2990–3100 | `emit_jvm.c:emit_jvm_pat_node` |
| Icon WASM | `emit_wasm_icon.c:emit_expr_wasm` | α/β tail-call per node |

## Gate

- All existing snobol4_wasm invariants pass (55p/1f baseline)
- Emit-diff 981/4 holds
- rung2/3/4/8/9/rungW01-W07/rung11 all pass after rewrite

## Session prefix: SW (continues SW-18+)
## Status: OPEN — not yet started
