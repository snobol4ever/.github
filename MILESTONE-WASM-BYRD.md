# MILESTONE-WASM-BYRD — SNOBOL4 WASM Full Byrd-Box Rewrite

**Status:** OPEN — SW-18 starts here  
**Replaces:** PC-loop + `emit_pattern_node` scaffold in `emit_wasm.c`  
**Reference oracles:** `emit_x64.c:5033–5200` (stmt wiring) · `emit_pat_node` (x64) · `emit_jvm_pat_node` (JVM)

---

## Why

`emit_wasm.c`'s `emit_pattern_node` uses structured `block`/`loop`/`if` with a
cursor local. WASM structured control flow has no `goto` — backtracking requires
jumping *backward* to a peer label, which is illegal inside a single WAT function.
The Byrd-box model escapes this by making each port a separate WAT `(func ...)`,
with `return_call` (zero-overhead tail call) between them. This is the correct
model for SNOBOL4 pattern matching. Every other backend uses it.

---

## Statement-Level Wiring

Each SNOBOL4 statement: subject · pattern · replacement · :S/:F goto.
All three phases can fail. The fence between subject and pattern is the
primary boundary.

```
subj_α  →(eval)→  subj_γ = scan_α
subj_ω  → stmt_ω  (subject itself failed)

scan_α  →(set cursor=scan_pos)→  pat_α   (enter pattern tree)
scan_ω  →(advance scan_pos; if exhausted)→  stmt_ω
        →(else)→  scan_α   (retry)

pat_tree: α/β tail-call functions per node (see below)
pat_γ   →  repl_α   (match succeeded, apply replacement)
pat_ω   →  scan_ω   (match failed at this position)

repl_α  →(eval replacement)→  repl_γ
repl_γ  →  goto :S target
repl_ω  →  stmt_ω

stmt_ω  →  goto :F target
```

WAT label format: `$sN_phase` e.g. `$s42_scan_α`, `$s42_pat7_β`  
Counter: `static int wasm_sno_ctr` — monotonic, never resets.

---

## M-SW-BYRD-A: Statement skeleton (no pattern)

**Gate:** rung2, rung3, rung4 (assignment + arithmetic — no pattern matching)

Emit per-statement WAT functions for:
- `$sN_subj_α` — eval subject via `emit_wasm_expr`, store to globals, `return_call $sN_repl_α`
- `$sN_repl_α` — eval replacement via `emit_wasm_expr`, assign, `return_call $sN_succ`
- `$sN_succ` / `$sN_fail` — `return_call` to :S/:F goto targets

Keep `emit_wasm_expr` unchanged — it is correct for subject/replacement (inline stack values).  
Keep PC-loop for statement *dispatch* (statement-level goto is fine as `br_table`).  
Replace only the per-statement body emission.

---

## M-SW-BYRD-B: E_QLIT pattern node

**Gate:** rungW01, rungW02 (literal pattern matching)

Add scan loop and first pattern node:
- `$sN_scan_α` — save scan_pos to global; set cursor = scan_pos; `return_call $sN_pat_α`
- `$sN_scan_ω` — increment scan_pos; if > subj_len: `return_call $sN_stmt_ω`; else `return_call $sN_scan_α`
- `$sN_patK_α` (E_QLIT) — `call $sno_lit_match`; success: advance cursor, `return_call` outer_γ; fail: `return_call` outer_β
- `$sN_patK_β` (E_QLIT) — `return_call` outer_β  (no internal backtrack)

---

## M-SW-BYRD-C: E_SEQ pattern node

**Gate:** rungW03, rungW04 (sequential patterns)

```
seq_α  = return_call left_α
left_γ = right_α
right_β = left_β   (backtrack into left)
right_γ = outer_γ
left_ω = right_ω = outer_β (via scan_ω)
```

---

## M-SW-BYRD-D: E_ALT pattern node

**Gate:** rungW05, rungW06 (alternation)

```
alt_α:  save cursor global; return_call left_α
left_β: restore cursor; return_call right_α
right_β = outer_β
left_γ = right_γ = outer_γ
```

---

## M-SW-BYRD-E: E_ARBNO, E_ARB pattern nodes

**Gate:** rungW07 (ARBNO, ARB)

E_ARBNO:
```
arbno_α: save cursor; return_call outer_γ   (zero match succeeds)
arbno_β: try inner_α; inner_γ → if cursor==saved: outer_γ (zero-advance guard)
                                            else: save cursor; return_call inner_α again
         inner_β → restore cursor; return_call outer_β
```

E_ARB: try empty match first (outer_γ), β tries longer.

---

## M-SW-BYRD-F: E_CAPT_COND, E_CAPT_IMM

**Gate:** rung8, rung9 (captures: `.var` and `$var`)

```
capt_α: save before-cursor; return_call child_α
child_γ: store subj[before..cursor] in var global; return_call outer_γ
child_β: return_call outer_β
```

---

## M-SW-BYRD-G: User-defined functions (DEFINE)

**Gate:** rung10 (recursion, OPSYN, alternate entry)

Prescan collects `DEFINE('fname(p1,p2,...)')` → registry.  
`E_FNC` in subject/replacement: if fname in registry → emit WAT call ABI
(save param globals, set args, `call $fname_body`, restore).  
Function body: separate WAT `(func $fname_body ...)` with RETURN/FRETURN wiring.

---

## Keep from current emit_wasm.c

- String literal table (`strlit_intern/abs/len/reset/count`) — shared API, unchanged
- `emit_wasm_expr` — inline stack-value emitter for subject/replacement expressions
- `emit_wasm_runtime_imports_sno_base` — runtime imports
- Variable globals table (`var_intern`, `var_names`)
- `emit_data_init_func` — DATA type constructor

## Replace

- `emit_main_body` — PC-loop → per-statement Byrd-box function emitter
- `emit_pattern_node` — cursor-local structured → per-node α/β WAT functions

---

## Invariant baseline (SW-17)

`snobol4_wasm`: 55p/1f (1f = pre-existing xfail `212_indirect_array`)  
Emit-diff: 981/4

Each sub-milestone must hold emit-diff 981/4 and not regress existing passes.
