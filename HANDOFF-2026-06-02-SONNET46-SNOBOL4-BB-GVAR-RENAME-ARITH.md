# HANDOFF — SNOBOL4 BB: gvar rename + `OUTPUT = 2 + 3` in mode-3

**Author:** Sonnet 4.6 (third developer). **Date:** 2026-06-02.
**SCRIP tips:** `03995b7` (rename) → `707b284` (arith). `.github` = this commit.

---

## 1. PIVOT rename: `bb_nv_assign` → `bb_gvar_assign`

Lon directive mid-session: `NV` is opaque jargon. The prior session renamed `bb_sno_assign`→`bb_nv_assign`
but `NV` (Name-Value) is still meaningless. The concept is **global variables** — what the user manual
calls them. The runtime is language-independent; Icon, Prolog, Raku, and SNOBOL4 all use `NV_GET_fn` /
`NV_SET_fn` for named global variables. So `gvar` is the correct concept.

**Mapping (SCRIP `03995b7`, 9 files, 42+/42-, symmetric rename-only):**
- `bb_nv_assign.cpp` → `bb_gvar_assign.cpp` (git mv)
- `bb_nv_assign` / `bb_nv_assign_str` → `bb_gvar_assign` / `bb_gvar_assign_str`
- `rt_nv_assign_str` / `_int` / `_var` / `_concat` → `rt_gvar_assign_str` / `_int` / `_var` / `_concat`
- `g_nv_flat_chain` → `g_gvar_flat_chain`
- `flat_drive_nv_assign` / `flat_drive_nv_assign_binop` → `flat_drive_gvar_assign` / `flat_drive_gvar_assign_binop`
- Makefile source list + per-object rules + `.o` names updated

Zero orphan `nv_assign` / `g_nv_flat` references in any `.c/.cpp/.h` after rename (grep verified).
Gates green throughout (rename-only, behavior unchanged by construction).

---

## 2. `OUTPUT = 2 + 3` in mode-3 (SCRIP `707b284`)

**Result:** `5` — byte-identical to SPITBOL oracle for `+`, `-`, `*`, `/`.
`m3 smoke: 1/6 → 2/6` (output + arith both pass). MODE3_MIN floor corrected 5→2.

### IR structure (from `--dump-bb`)
```
IR_graph_t lang=SNO n=11 entry=4
  [6] IR_ASSIGN  α=.  γ=5  ω=5  sval="OUTPUT"
  [7] IR_BINOP   α=.  γ=6  ω=5  ival=BINOP_ADD
  [8] IR_LIT_I   α=.  γ=9  ω=5  ival=2
  [9] IR_LIT_I   α=.  γ=7  ω=5  ival=3
```
`flat_drive_gvar_assign_binop` walks `ASSIGN->α=BINOP` via `walk_bb_flat`, which hits the new gvar branch
in the `IR_BINOP` dispatch.

### Three pieces landed

**(a) `op_a_slot` promotion — `emit_globals.h` + `emit_core.c`:**
- Added `int op_a_slot` to `sm_emit_t` (after `op_a_node_kind`)
- `walk_bb_node` now sets `g_emit.op_a_slot = nd->α ? bb_slot_get(nd->α) : -1` (plus `extern int bb_slot_get(IR_t*)`)
- This is the no-neighbor FACT RULE: the dispatcher marshals the α-operand's ζ-slot offset onto `_`;
  the box reads only `_`, never calls `bb_slot_get` itself

**(b) `bb_binop_gvar_arith.cpp` — new file:**
- Guard: `g_gvar_flat_chain && op_off >= 0 && op is arith`
- `op_sa` = LHS literal ival (int, deposited by driver)
- `op_sb` = RHS literal ival (int, deposited by driver)
- `op_off` = 8-byte ζ-slot (allocated via `bb_slot_alloc(nd)`, node-keyed so `bb_slot_get` finds it)
- Emits: `mov rax, lhs_imm; mov rcx, rhs_imm; <op>; mov [r12+off], rax; jmp γ; def β; jmp ω`
- Uses `x86("mov", "rax", (long)lhs)` — immediate move, NOT a frame slot read
- Result is raw int64, NOT a 16-byte DESCR (the consuming `bb_gvar_assign` builds the DESCR via `rt_gvar_assign_int`)

**(c) `bb_gvar_assign` int-binop arm (was x86_bomb stub):**
- Guard: `op_a_node_kind == IR_BINOP`
- Reads `_.op_a_slot` (promoted by `walk_bb_node`)
- Emits: `lea rdi [rip+dst_name]; mov rsi [r12+op_a_slot]; call rt_gvar_assign_int; jmp γ; def β; jmp ω`
- `FRQ(slot)` = 64-bit load from `[r12+slot]` into `rsi` (int64 argument)

**Driver change (`emit_bb.c` IR_BINOP walk_bb_flat branch):**
```c
if (g_gvar_flat_chain && op_is_arith && nd->α && nd->β
    && nd->α->t == IR_LIT_I && nd->β->t == IR_LIT_I) {
    g_emit.op_sa  = (int)nd->α->ival;   // literal value, not slot offset
    g_emit.op_sb  = (int)nd->β->ival;   // literal value, not slot offset
    g_emit.op_off = bb_slot_alloc(nd);  // 8-byte slot, node-keyed
    EMIT_PAIR_RESET();
    EMIT_PAIR_DEF_JMP(lbl_β, lbl_ω);
    EMIT_PAIR_FILL(nd, lbl_γ, lbl_ω, lbl_β);
}
```
Key correctness fact: `bb_slot_alloc(nd)` registers the slot under the BINOP node in `g_bb_slotmap`.
When `walk_bb_node` later runs for IR_ASSIGN, `bb_slot_get(ASSIGN->α = BINOP)` finds the slot. ✓
(Using `bb_slot_claim(8)` would NOT register in slotmap → `bb_slot_get` returns -1 → bomb. Caught in testing.)

**Also wired:** `bb_binop_gvar_arith_str()` added to `bb_binop.cpp` router (before the fallback bomb).
**Makefile:** `bb_binop_gvar_arith.cpp` added to `RT_PIC_SRCS` list + per-object compile rule.

### Gates (final state)
```
make scrip           rc=0
make libscrip_rt     rc=0
test_smoke_snobol4   m2 7/7 HARD · m3 2/6 · m4 0/6
no_bb_bin_t          0
sm_dead              0
concurrency          OK (FACT RULES byte-identical x3)
prove_lower2         PASS
g_vstack             0
medium_invisible     61 informational (bb_call 60 + bb_unop 1, pre-existing)
```

---

## 3. NEXT (SNOBOL4)

**`bb_subject` + `bb_match` together — the `pattern` smoke: `S 'b' = 'X'` → `aXc`.**

The pattern smoke requires:
1. SUBJECT box: `bb_subject` loads `Σ` (base) + `Δ` (length) into `g_subject_slot` (a ζ-frame slot).
   Already landed (`bb_subject.cpp`), but needs to run in the same flat chain as MATCH.
2. MATCH box: `bb_match` α reads `g_subject_slot` to get the subject, establishes the ch.18 outer
   start-loop, and inline-emits the element (`IR_PAT_LIT` for `'b'`).
3. Replacement: `S 'b' = 'X'` also needs the replacement spliced in (`bb_scan_stmt` or the SUBJECT/MATCH/REPL chain).

The flat chain must emit SUBJECT → (element graph) → MATCH in sequence. `flat_drive_scan_stmt` is the
entry point for `IR_SCAN`; it currently uses `rt_scan_exec` (the mode-2 bridge). The native path goes
through `flat_drive_subject` + `flat_drive_match`.

**After pattern smoke:** `bb_capture` and `bb_arbno` (the brokered-call arms need BROK-1/BROK-2 conversion,
but the data they capture — cursor snapshots — is already in ζ-slots via the REG ladder).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
