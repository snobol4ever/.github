# HANDOFF 2026-06-15 — Icon native real-POW — ✅ LANDED (Claude)

**Goal:** GOAL-ICON-FULL-PASS — the watermark's explicit "NEXT real-arith" call-out: native real-POW.
**Result:** LANDED & PUSHED. `rung19_pow_toby_pow_var` (`x:=3.0; write(x^2)` → `9.0`) is **PASS in m3 AND m4** (was EXCISED). SCRIP commit = **`fe80ecf`** (on origin/main; rebased clean over concurrent Prolog landing `cedad93`, re-gated identical).

## Tally
m3 **132 → 133** · m4 **132 → 133** (+1 each). FAIL **23** unchanged (the move is EXCISED→PASS). EXCISED **92 → 91**. XFAIL 36. Total 283.

## The four edits (2 files)
1. **`emit_bb.c` `binop_slot_kind`** — `BINOP_POW` now returns `IR_BINOP_ARITH` (was falling through to generic `IR_BINOP` → the `walk_bb_node: kind=7 unhandled` garbage).
2. **`emit_bb.c` `binop_is_num_real`** — `if (op == BINOP_POW) return 1;` BEFORE the operand-real scan. Icon's `^` is ALWAYS real (even `3^2` = `9.0`), and `rt_num_arith` already returns `REALVAL(pow(ld,rd))` unconditionally for POW. So POW must set `op_num_real=1` regardless of operand types.
3. **`emit_bb.c` `walk_bb_flat` IR_CALL→descr binop branch (~line 3049)** — added `|| op_is_pow` so a POW operand of a CALL (`write(x^2)`) takes the SAME validated `descr_binop_set_slots` fast path the real-arith ops use (instead of the generic `flat_drive_binop_tree` fallback). The fast path's `needs_walk` check treats LIT_I/already-slotted operands as pre-produced, so `x` (slotted via its varslot) + `2` (LIT_I chain node) → `descr_binop_set_slots` → `op_num_real=1` → `bb_binop_arith` real arm.
4. **`scrip.c` `local_assign_rhs_ok_g`** — the LIT_F-assign branch is now `return 1` (was `return !graph_has_pow(g)`), and the now-dead `graph_has_pow` (decl + def) is deleted.

## Why deleting `graph_has_pow` is correct, not a regression of `c26f89f` Fix 1
`c26f89f` Fix 1 added `graph_has_pow` to keep a graph with a LIT_F local-assign (`x := 3.0`) EXCISED whenever it ALSO contained a POW — *specifically because POW routed to generic `IR_BINOP` and produced garbage.* That guard was a placeholder pending a real POW arm, not a permanent invariant. Edits 1–3 give POW a correct real arm, so the reason for the guard is gone and the LIT_F-assign is now always admissible. Confirmed by analysis + the empirical gate diff that this flips ONLY the target:
- `rung37_augop_pow` (`i ^:= 3`) has a POW-binop RHS that hits `rhs_kind_ok` (returns 0, NOT the LIT_F branch) → stays EXCISED.
- Constant-fold pow tests (`2^10`, `2.0^0.5`, `5^0`, `2^3+1`, …) fold POW→`IR_LIT_F` before emission, so no live POW binop reaches the arm → stay PASS.
- The `rung36_jcon_*` programs stay EXCISED on their other unsupported constructs (image/coexpr/map/bigint).

The `flat_drive_binop_tree` fallback also calls `descr_binop_set_slots` + `binop_slot_kind` (lines ~1557-1562), so even a POW that takes the tree path (e.g. a LIT_F operand) is real-correct — no latent garbage path admitted by Edit 4.

## Verification
Both modes verified by explicit FAIL-name AND EXCISED-name diffs vs baseline: the ONLY line that moved is the target's EXCISED entry. Zero new FAIL, zero EXCISE→FAIL. Target prints `9.0` in m3 (`--run`) and m4 (standalone `--compile`→`as`→`gcc`→run). Gates: icon smoke 12/12 m3+m4 · prolog 5/5 m3+m4 · no-stack 0 · one-reg-frame 0 · FACT 0 · g_vstack 0 · bb_bin_t 0 · template-medium-invisible 0. Diff adds zero byte-producers; touches no template files.

## Key intel (reusable)
- Icon `^` (`BINOP_POW` = 18) is ALWAYS real. `rt_num_arith(a,b,BINOP_POW)` → `REALVAL(pow(to_real(a),to_real(b)))` (arithmetic.c) regardless of operand tags.
- A CALL-arg subexpression like `x^2` flows through `walk_bb_flat`'s IR_CALL→IR_BINOP descr-chain branch; the operands are chain nodes emitted (and slotted) BEFORE the binop in γ-edge order, so the binop fast path finds them already slotted.

**Author:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
