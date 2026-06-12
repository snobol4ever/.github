# HANDOFF — Pascal BB Mode 3/4 Pivot — 2026-06-12 Sonnet 4.6

## State on handoff
- **m2 gate**: PASS=103 FAIL=0 XFAIL=1 ✓ (stable throughout session)
- **m3 gate baseline**: PASS=29 FAIL=74 XFAIL=1 (NEW GOAL: bring to 103/0)
- **m4**: not yet measured systematically

## Commits this session (all pushed, rebased, green)
1. `d71ec59` — PAS_REC_MAX 64→512; pas_pend_add clears pend_ptrtarget
   - Fixed WITH-FILE-LIST hang (program t(output); begin end. was timing out)
   - Root: g_pas_ptrvars table capped at 64; pcom has 127+ ptr vars; extfp not
     registered; new(extfp) used __pas_alloc → INTVAL(0) heap slot; arr_get("0",1)
     no-SOH fast path → INTVAL(48) treated as non-nil; fextfilep loop ran forever.
2. `23a69f3` — arrrec inline field names + with-block pointer field assignment fix
   - g_pas_arrrecs now stores field names from g_pas_pend_fields on pas_arrrec_add
   - pas_arrrec_field_index(aname, fname) — lookup by arrrec's own fields
   - Grammar field-access action uses pas_arrrec_field_index as fallback (before
     nf-match-loop) — fixes display[top].fname for inline arrrec types
   - lower_assign: new case inside TT_IDX branch — when base==TT_FNC(__pas_deref,p),
     emit __pas_field_set(p, field_idx, rhs) — fixes with cp^ do field := val

## M3 failure categories (as measured)
- **30 BOMB** — bb_binop_relop: brr_ok() fails when operands aren't in integer slots
  Triggered by char-array relops (rw[i] = id in alphacmp, any alpha comparison).
  The template does cmp rax,rcx which is integer-only.

- **44 WRONG/empty** — arrays, records, with-statements, pointers produce empty output.
  Confirmed: arr_set_pure returns DESCR_t via rt_call_arr correctly; but the ASSIGN
  node that follows needs op_a_slot>=0 (slot promotion). Failure mechanism unclear —
  no BOMB, just empty stdout. Needs slot-promotion investigation or bb_gvar_assign_call.

## Root cause map for m3 failures

### BOMB fix (30 tests): lower_binop in lower_pascal.c
  When either operand of a relop is a char array (use pas_is_charexpr / pas_is_chararr
  to detect), instead of emitting IR_BINOP, emit:
    1. a call to rt_jct_relop(lv, rv, BINOP_EQ/etc.)  — returns int 0 or 1
    2. wrap in IR_IF: success → γ, failure → ω
  Signature: `int rt_jct_relop(DESCR_t lhs, DESCR_t rhs, int op)` (line ~1879 by_name_dispatch.c)
  op values from gen.h: BINOP_EQ=62, BINOP_NE=63, BINOP_LT=57, BINOP_LE=58, BINOP_GT=59, BINOP_GE=60

### WRONG fix (44 tests): slot promotion for arr_set_pure CALL result
  In bb_gvar_assign template (bb_gvar_assign.cpp line 47-56), IR_CALL case:
    `_.op_a_slot < 0` → BOMB "call-result: op_a_slot==-1 (call result slot not promoted)"
  But empirically no BOMB fires — suggests the ASSIGN node isn't even reached, OR
  a different template is selected. Next step: add stderr trace to disambiguate.
  
  Alternative diagnosis: the writeln's arg (arr_get(a, 1)) might not receive the
  updated value of `a` because the ASSIGN to `a` after arr_set_pure doesn't store
  back properly in native mode.

  Quickest experiment: try with `--trace` flag or --dump-bb and compare with a
  working integer test to see the structural difference.

## Key source files for m3/m4 work
```
src/lower/lower_pascal.c                     ← lower_binop, lower_assign
src/emitter/BB_templates/bb_binop_relop.cpp  ← BOMB target; brr_ok() predicate
src/emitter/BB_templates/bb_gvar_assign.cpp  ← IR_CALL case (slot-based assign)
src/emitter/BB_templates/bb_gvar_assign_call.cpp ← may be relevant
src/emitter/emit_core.c                      ← slot promotion pass (line ~485)
src/runtime/by_name_dispatch.c               ← rt_jct_relop (~line 1879)
src/runtime/builtins/gen.h                   ← BINOP_* enum values
```

## Gate commands
```bash
# M2 (must stay green):
bash /tmp/run_gate.sh       # PASS=103 FAIL=0 XFAIL=1

# M3 (new target: 103/0):
bash /tmp/run_gate_m3.sh    # currently PASS=29 FAIL=74

# Rebuild (always rm -f first):
cd /home/claude/SCRIP && rm -f scrip && make -j4 scrip
```

## RULES reminders
- 200-char line max, zero blank lines, one comment format only
- Pascal regen via bison only: cd src/parser/pascal && bison -d -o pascal.tab.c pascal.y
- rm -f scrip before make (no prerequisites)
- touch templates before make after template edits
- LANDMINE: do NOT re-attempt nested TT_IDX fix in mk_assign (TT_IDX inside TT_IDX)
- LANDMINE: do NOT edit libscrip_rt sources and forget to run `make libscrip_rt`
- Do NOT work on pcom entstdnames symbol-table field misregistration (lower priority)
