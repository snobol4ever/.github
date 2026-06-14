# HANDOFF — 2026-06-13 OPUS48 — Icon m3/m4: IR_SWAP + real-arith constant-fold

**Goal:** GOAL-ICON-FULL-PASS (Icon m2 frozen as HARD oracle; close the m3/m4 native gap).
**Result:** two complete units landed & pushed. Icon **m3/m4 82→87 (+5)**, m2 **202** unchanged, FAIL 63→59, ZERO regressions.

## Verified state at handoff
- **SCRIP HEAD = `1b71e43`** (local == origin/main, clean).
- **.github HEAD = `586d787b`** (local == origin/main, clean).
- Icon rung tally: **m2 202 · m3 87 · m4 87** (XFAIL 36). m2 is the HARD gate (unchanged).
- icon smoke 12/12/12 (all three modes) · prolog smoke 5/5 · `test_gate_icn_no_stack`=0 ·
  `test_gate_icn_one_reg_frame`=0 · FACT gate (byte-emitters outside templates)=0.
- The 45 `test_gate_bb_one_box` FAILs remain PRE-EXISTING (emitter entry-count gate, untouched).

## What landed this session (two units)

### 1. Native `IR_SWAP` for `x:=:y` (SCRIP `a06554a`)
New four-port box **`src/emitter/BB_templates/bb_swap.cpp`** — pure `x86()` (0 byte-producers; not in the
medium-invisible remaining list). Reads both var slots into `rax:rdx`/`rcx:rsi`, cross-stores (left←rv,
right←lv), writes result `rv`→own slot, `jmp γ`/`def β`/`jmp ω`. Both operands read BEFORE either store
(classic swap); the producer-chain VAR reads are harmless (reads don't mutate). Wiring:
- `flat_drive_swap` (emit_bb.c) resolves `op_sa`/`op_sb` via `bb_varslot_peek` + `op_off` via
  `bb_slot_alloc16` before the fill.
- `walk_bb_node` (emit_core.c): `case IR_SWAP: bb_emit_x86(bb_swap());`.
- `icn_graph_native_emittable_mode` (scrip.c) admits IR_SWAP ONLY when both operands are `IR_VAR` w/ sval
  (non-VAR-operand swaps like `a[i]:=:a[j]` clean-`[SMX]` decline, never abort).
- Makefile: `bb_swap.cpp` in RT_PIC_SRCS + the `scrip:` target compile line (BOTH are required — the `scrip:`
  link globs `$(OBJ)/*.o`, so the `.o` must exist or the symbol is undefined at link).
- Verified: rung15 swap_basic (`2\n1`) + swap_str (`world\nhello`) PASS all 3 modes. m3/m4 82→84.

### 2. Real-arith constant-fold + guarded LIT_F local-assign (SCRIP `1b71e43`)
Lowering-only fold (mirrors the proven pow `^` fold), `src/lower/lower_icon.c`:
- `icn_const_step` now folds constant binary arith **ADD/SUB/MUL/DIV/MOD** (int-or-real, recursive — so
  `2^3+1` evaluates whole: `2^3`=8.0 real, `+1`=9.0 real).
- The `lower` fold trigger fires for ANY all-constant arith binop whose result is **real** → builds `IR_LIT_F`.
  Pure-int constants stay on the existing native int path (no behavior change); relops/concat return 0 from
  `icn_const_step` → never folded.
Plus a small emitter/gate enablement:
- `emit_core.c:392` now gives `IR_LIT_F` operands a slot (`op_a_slot`) — purely additive (every `op_a_slot`
  consumer bombs on <0, so a LIT_F operand previously always bombed/excised; nothing working relied on -1).
- `icn_local_assign_rhs_ok_g` (scrip.c) admits a `LIT_F` local-assign RHS **ONLY when the graph has no binop**
  (`!icn_graph_has_binop`; needs a forward-decl of `icn_graph_has_binop` since it's defined later in the file).
- Verified: rung17 `2.0*3.5`→7.0, rung26 `x:=2^3+1`→9.0 PASS all 3 modes. m3/m4 84→87.

## ⚠️ DEBUG LESSON (binding — added to the goal watermark)
The FIRST attempt admitted `LIT_F` local-assign **unconditionally** in `icn_rhs_kind_ok`. The native gate is
whole-graph (emit only if EVERY node is emittable). Admitting the LIT_F assign flipped the gate decline→admit
for three real-**VARIABLE** programs — `x:=1.5;write(x+y)`, `x:=3.0;if x=3.0`, `x:=3.0;write(x^2)` — which
then hit their non-existent real-binop/relop/pow boxes → **3 EXCISE→FAIL regressions**. The `--mode interp`
PASS count and even the m3 PASS count both went UP, hiding it. Caught only by an explicit FAIL-LIST DIFF vs the
pristine baseline (`comm -13 pristine_fail now_fail`). Contained with the `!has_binop` guard: rung26's `2^3+1`
folds to a binop-free graph (admit), while every real-VAR case keeps a runtime binop (clean `[SMX]` decline).
**RULE: always diff the FAIL list vs pristine, never trust a +PASS count alone — a net +PASS can hide
EXCISE→FAIL.** EXCISE is sanctioned (m2 is the oracle); a non-`[SMX]` FAIL is not.

## NEXT — prioritized, scoped

1. **Real-arithmetic RUNTIME path (now isolated).** The 3 EXCISED real-VAR programs above + rung17_real_add
   (`x+y`) + rung18 real relops (real_gt/mixed/real_eq) + rung19 real-var pow need a NATIVE real binop/relop
   arm. `rt_arith` (arithmetic.c) is INTEGER-ONLY (returns `long`); there is NO DESCR-in/out real helper.
   Cleanest per the RT=value / BOX=ports FACT rule: add an `rt_*` taking two `DESCR_t` + an op code, doing Icon
   numeric coercion (int/real/mixed, matching the m2 interp — NOT `POWER_fn`), returning a `DESCR_t`; then a
   real-arith template arm marshals the two operand slots → regs → `call` → stores the result DESCR to its own
   slot. This is a SHARED-dispatch change (SNOBOL4/Prolog also use the binop dispatch) → gate the full suite +
   an explicit FAIL-diff vs pristine. (`descr_binop_opnd_slot` at emit_bb.c:1451 still returns -1 for LIT_F —
   the binop operand-slot path also needs LIT_F enablement for the var-real case, same additive pattern.)
2. **`bb_every` four-port rebuild** — rc=124 generator-resume timeout cluster (~12: rung01/02/03/14/19).
   `bb_every.cpp` is a hollow stub; the real EVERY drive/resume/exhaust lives in `flat_drive_every` (DRIVER,
   violates TEMPLATE-ONLY). Build a real box mirroring canonical `ir_a_Every` (irgen.icn:309): start→expr;
   expr.success→body; body.success/fail→expr.resume (the loop); expr.failure→ir.failure.
3. **List builtins** (rung22 — push/put/get/pull/bang; incl. 2 rc=139 SEGFAULTS on get/pull).
4. **Subscript `s[i]`** (rung16, 5 progs) — lowered as `IR_CALL dval=2` → hits `LANGUAGE-BLIND rule` abort in
   the descr-chain arm; tangled with the call path, not a clean standalone box. `flat_drive_idx_get` exists
   (emit_bb.c:3012) but the lowering shape differs.

## Discipline (binding)
m2 (`--interp`) is the HARD oracle — never let `--mode interp` PASS drop below 202; verify with an explicit
before/after `bash scripts/test_icon_rung_suite.sh --mode interp` diff. ALWAYS gate all three modes; a native
shape with no template must LOUDLY `[SMX]` decline (→ EXCISED, sanctioned) — NOT abort or silently FAIL. After
EVERY emitter/gate change, diff the FAIL list vs pristine (not just the PASS count). Templates are
`x86()`-pure (no raw byte-producers, no `MEDIUM_*` branch in `bb_*.cpp`). Build:
`bash scripts/build_scrip.sh && make libscrip_rt`. Concurrent remote is fast-moving — `git pull --rebase`,
then REBUILD + re-verify (m2 HARD + spot-checks) before push, since peers touch shared files
(emit_bb.c/emit_core.c/scrip.c/Makefile). Commit per repo; push code repos first, `.github` last.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
