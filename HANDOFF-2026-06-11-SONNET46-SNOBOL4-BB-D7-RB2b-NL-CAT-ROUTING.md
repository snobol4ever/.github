# HANDOFF — 2026-06-11 · Sonnet 4.6 · SNOBOL4-BB · D7-RB-2b NL CAT ROUTING LANDED

**SCRIP commit: `906adfe` (pushed).**

## What landed (+87 lines, 1 file: `src/lower/lower_snobol4.c`)

Four new static helpers + one new block in `lower_assign`:

**Helpers (added between `sno_has_idx` and the separator):**
- `sno_leaf_buildable(t)` — 1 if leaf is QLIT, TT_VAR predefined-name (REM/ARB/FAIL/SUCCEED/FENCE/ABORT + lowercase), unary-s(QLIT) (SPAN/ANY/NOTANY/BREAK/BREAKX), or unary-i(ILIT) (LEN/POS/RPOS/TAB/RTAB)
- `sno_seq_buildable(t)` — recursive: TT_SEQ iff c[0] buildable AND c[1] leaf-buildable; non-SEQ iff leaf-buildable
- `sno_seq_has_pat_leaf(t)` — 1 if SEQ contains ≥1 non-QLIT leaf; guards all-QLIT concat from misrouting
- `sno_build_leaf_ir(cx, t, g, w)` — builds the appropriate IR_PATTERN_* node for a leaf

**New block in `lower_assign` (before the `sno_has_pat` orphan arm):**
If `rhs->t == TT_SEQ && sno_seq_buildable(rhs) && sno_seq_has_pat_leaf(rhs)`:
1. Flatten the left-assoc binary SEQ tree into `leaves[]` array (iterative stack, right-first push = left-first pop)
2. Build pats[0..nl-1] via `sno_build_leaf_ir`
3. Pairwise left-assoc IR_PATTERN_CAT chain (mirrors TT_ALT all-QLIT arm): build order leaf0→leaf1→CAT01→leaf2→CAT012→...→DTP_ASSIGN
4. `ir_operand_push(dtp, final_cat)`, return `pats[0]`

## Verification

**Probes (m2==m3==m4==sbl PASS):**
- LIT-LIT: `P='a' 'b'` / 'ab' → matched ✓
- SPAN-LIT: `P=SPAN('a') 'b'` / 'aabb' → matched aab ✓
- LEN-LIT: `P=LEN(1) 'a'` / 'xabc' → matched xa ✓
- BREAKX-LIT: `P=BREAKX('X') 'X'` / 'abcXdef' → matched abcX ✓
- ANY-LEN: `P=ANY('xyz') LEN(2)` / 'xyzabc' → matched xyz ✓
- SPAN-LIT-SPAN: `P=SPAN('helo') ' ' SPAN('world')` → matched hello world ✓
- POS-LIT: `P=POS(0) 'a'` / 'abc' → matched a ✓
- CONCAT-nonreg: `X='foo' 'bar'` → foobar (guard correct; all-QLIT stays on ASSIGN_CONCAT) ✓
- FAIL-lone: `P=FAIL` → failed ✓

**Gates:** smoke 7/7/7 HARD · pat-rung M2 19/19 · M3 19/19 · M4 16/19 (050/051/054 pre-existing b11a963, floor held) · corpus BYTE-IDENTICAL 172/156/144 both sides, FAIL-set diff EMPTY · fence HARD

## Key finding / B10 landmine

`P='A' ARB 'C'` on 'XABYC': the IR graph is CORRECT (PATTERN_LIT('A') → PATTERN_ARB → PATTERN_CAT → PATTERN_LIT('C') → PATTERN_CAT → DTP_ASSIGN). But the match side uses `PAT_DEFER("P")` → `rt_defer_match` → `rt_dtp_run` which is ONE-SHOT: returns the first δ result, no backtrack re-entry. ARB needs β-regen (extend by 1 each retry) which requires the caller to drive β. The B10 DEFER-IN-BUILD rung is needed to give the match engine full re-entry into the built pattern.

## Facts for next session

- `sno_seq_has_pat_leaf` is required; without it `X='foo' 'bar'` routes to PATTERN_LIT instead of ASSIGN_CONCAT (smoke concat regression)
- The left-assoc binary SEQ tree flattens to left-to-right order via right-first-push / left-pop
- All the IR nodes (PATTERN_LIT/ARB/CAT etc.) and their slot/emit_bb/descr_chain_arity entries were already wired from D7-RB-2; no changes needed there
- D7-RB-3 next: `P=LEN(3)` value-assign — TT_LEN with ILIT arg ALREADY in sno_leaf_buildable (unary-i arm), but `P=LEN(3)` alone (not in a SEQ) falls to the existing unary-i ILIT single-node block at lower_assign — check if that block already emits IR_PATTERN_LEN + DTP_ASSIGN or still orphans
