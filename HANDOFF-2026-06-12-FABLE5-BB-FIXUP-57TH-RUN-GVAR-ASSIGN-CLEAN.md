# HANDOFF — 2026-06-12 · 57th attended run (Fable 5) · Sonnet 4.6

## What landed
**FIXUP bb_gvar_assign.cpp: 66→0 CLEAN — SCRIP @ 8dc0032**

Three-file edit (bb_gvar_assign.cpp + emit_core.c + emit_bb.c):

**Deleted (dead code):**
- `g_descr_flat_chain` arm in bb_gvar_assign — proven dead: emit_core.c routes flat_chain to bb_assign_local, never bb_gvar_assign; arm contained x86_begin + x86_ro_load_q + x86_ro_seal_str + x86_frame_load64 + x86_frame_store64
- IR_SEQ/IR_UNOP/IR_SEQ_EXPR from emit_core.c IR_ASSIGN admission — no working template arms for these shapes

**emit_core.c:** Added `bb_prepare(nd)` call for IR_ASSIGN dispatch (CV9)

**emit_bb.c:** Added IR_ASSIGN bb_prepare block:
```c
if (nd->op == IR_ASSIGN) {
    IR_t *oa = (nd->n_operands > 0) ? nd->operands[0] : NULL;
    g_emit.bb_ls = bb_intern_into(g_emit.bb_ls_buf, IR_LIT(nd).sval ? IR_LIT(nd).sval : "");
    g_emit.bb_rs = oa ? bb_intern_into(g_emit.bb_rs_buf, IR_LIT(oa).sval) : NULL;
    return;
}
```
Null-guard on oa->sval prevents strtab pollution for BINOP/CALL arms.

**bb_gvar_assign.cpp:** Full regeneration:
- Zero statics (16→0): all helpers inlined as direct expressions; labels via `_.bb_ls`/`_.bb_rs`, fn ptrs via direct casts
- Zero MEDIUM_TEXT: dead arm + Lon directive (m3=m4 identical)
- Zero bypass: `x86_movabs_r64` → `x86("movabs", ...)`; frame/ro bypasses gone with dead arm
- ONE return per PLATFORM: ternary chain over 5 arms (LIT_S/LIT_I/VAR/BINOP/CALL)
- Bombs for slot==-1 guards inline in ternary (BINOP/CALL arms)

## Proof
**A/B normalized asm-diff:**
- kw_i (LIT_I arm): EMPTY
- ca (CALL arm): EMPTY
- kw_v (VAR arm): R1-comment-only (`# BOX IR_ASSIGN(var)…` → `# IR_ASSIGN`)
- bi (BINOP arm): R1-comment-only (spurious `.S2: .string ""` strtab entry corrected by null-guard fix)
- kw_s (LIT_S arm): label-renumbering-only — rdi←ANCHOR, rsi←"1" correct in both; .S0/.S1 swap is cosmetic intern-order change from bb_prepare computing bb_ls before bb_rs

**Behavior: m2=m3=m4 identical ×5, ALL ARMS LIVE**
- LIT_S: `&ANCHOR="1"` → 1 ✅
- LIT_I: `TRIM=1` → 1 ✅
- VAR: `&ANCHOR=X` → 5 ✅
- BINOP: `N=3+4` → 7 ✅
- CALL: `N=SIZE("hello")` → 5 ✅

## Rank delta
125 total / **107 dirty** / **18 clean** / **GRAND 1948** (was 17 clean / 2014 — −66 exact, sole mover)

## Gates at floors (all verified post-commit)
sno m4 7/7 HARD · pat M2 19 M4 18/0 skip-1 (pre-existing) · icon m2 12/12 HARD m3=m4 10/2 · prolog smoke 5/5 ×3 · prove 0P+0F rc=0 VACUOUS · purity 1 · bin_t 0 · vstack 3 · handencoded 0 · med_inv 102 · emit_blind 0 · sno_pat_reg HARD

## Inherited reds (pre-existing, NOT regressions from this run)
1. **pl_gz2 gate FAIL**: "neg m3 did NOT show the loud fallback (GZ wrongly admitted?)" — non-admitted Prolog `main :- X = f(a), write(X), nl.` being admitted to GZ fast path. Pre-dates this run.
2. **053_pat_alt_commit M4 SKIP**: duplicate `.Lpb0_s`/`.Lpb0_desc` labels from `bb_pattern_lit.cpp` `pb_bump()` never called — pre-existing from STRIP-WRAPPER commit a1a2191.

## Next session
**Cursor: `bb_gvar_assign_concat.cpp`**

Arrival state: TOTAL=27 (mt=2 lv=6 rp=11 hc=6 sd=2)

Key issues to resolve:
- `IF(MEDIUM_TEXT)` split in concat arm — binary uses `x86_load_ro` with graph pointers (m3 in-process); TEXT uses parts array (m4). Same class as the now-deleted bb_gvar_assign SEQ arm. Resolution: delete BINARY path entirely OR prove it dead too (check flat_drive_gvar_assign sets op_parts_n for IR_ASSIGN_CONCAT in TEXT mode only via `if (MEDIUM_TEXT && ...)`).
- `static char b[64]` local inside template function body (lv=6) — needs bb_prepare to pre-intern part labels OR global buffer (file-level static, not lv violation)
- `bb_slot_claim` in template body → move to bb_prepare if we add a bb_prepare call for IR_ASSIGN_CONCAT
- `x86_load_ro` bypass calls → delete with BINARY path
- Helpers (hc=6): dst_name/dst_addr/dst_label/lhs_graph/rhs_graph/fn_* — inline via bb_ls/bb_rs after adding bb_prepare, same recipe as bb_gvar_assign

Note: bb_prepare for IR_ASSIGN_CONCAT would need to set bb_ls (dst label), op_parts_n (already set by flat_drive_gvar_assign for TEXT mode — verify it's available at bb_prepare time), and op_off (= bb_slot_claim(16*op_parts_n)).

## SCRIP state
SCRIP @ 8dc0032 · .github @ (this commit)
