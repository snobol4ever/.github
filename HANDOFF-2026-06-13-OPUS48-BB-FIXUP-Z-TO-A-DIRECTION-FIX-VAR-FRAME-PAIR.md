# HANDOFF — 2026-06-13 (Opus 4.8) — GOAL-BB-FIXUP-Z-to-A

## STATE (verified at handoff)
- **SCRIP @ `fa4cb1d`** (working tree clean) · **.github @ `cf253549`** (clean)
- **CURSOR: `bb_resolve.cpp`** (tracker `# CURSOR:` line — the ONE source of truth)
- Tree builds (`make -j4 scrip` + `make libscrip_rt` rc=0). Gate battery green vs baseline.
- **Pre-existing reds (NOT introduced, do not chase under this goal):** (1) `test_smoke_compile_hello_all_langs` 5/6 — failing row = `rebus` ROW-DRIFT FAIL-compile (on-hold per PLAN; entered in a prior concurrent window). (2) `util_template_purity_audit.sh` rc=1 = single `bb_call_write_slot.cpp:71` fprintf side-effect.

## WHAT THIS SESSION DID
1. **DIRECTION CORRECTION (the headline).** Lon corrected ×3: Z→A means the cursor moves DOWN the alphabet (toward A, to names sorting EARLIER), continuing from the cursor — NOT "jump to the nearest-Z dirty file," NOT "easiest/cheapest file first" (both are A→Z = backward). Encoded as a loud **READ THIS FIRST** banner at the top of `GOAL-BB-FIXUP-Z-to-A.md` (commit `cf253549`) with the exact resume procedure + the three forbidden moves + "cursor line beats watermark" + "dirty-behind-the-cursor files wait for the lap-wrap." A pointer was added at `## THE CURSOR`. **Next session: read that banner before touching anything.**
2. **Landed 2 files (valid CLEAN+gated, but BEHIND the cursor — out of strict order, kept because they harmlessly pre-clean the var-frame region for the next Z-start lap; NOT reverted):**
   - `bb_var_frame_ref` 5→0 CLEAN — `e56caf7`
   - `bb_var_frame` 4→0 CLEAN — `fa4cb1d`
   - Both: **CV7** `x86_reg_disp32_load64(D,B,O)` → `x86("mov", D, RDQ(B,O))` + **rp** lambda `[](int)` → `[&](int h) { (void) h; … }`. Byte-identical in BOTH mediums **by construction**: `RDQ` (x86_asm.h:354) emits `"qword ptr [B + O]"` → operand parser (x86_asm.h:477) yields base=B/off=O → `mov` dispatch (x86_asm.h:575) calls the SAME `x86_reg_disp32_load64`. Both Pascal-only (`lower_pascal.c:84`/`:92`), no firing corpus → C2-by-construction (assign_frame-family precedent). The `[&](int h){(void)h;…}` form is the blessed FOR-lambda from CLEAN `bb_assign_frame.cpp`; the audit's `ret_lam` excluder requires a `&`/`=` capture (empty `[]` gets its return counted → rp).
3. **Cursor corrected** `bb_unop` (my wrong backward setting) → **`bb_resolve`** (the next dirty file going Z→A-DOWN from the tracker's prior `bb_return`: return 0 → retract_throw 0 → resolve 18). Watermark appended to the goal file.

## NEXT — open at `bb_resolve.cpp` (but it is a BLOCKED dispatcher)
`bb_resolve` is the `IR_BUILTIN` meta-resolver dispatcher (`bdisp(IR_t*pBB)` + `std::string bb_resolve(IR_t*pBB)`). Its **18** violations CANNOT reach `audit_bb_fixup_file.sh` rc=0 in isolation:
- `bdisp(pBB)` + `bb_resolve(pBB)` carry `IR_t*` → **CV9/CV10**
- the dispatch chain still calls PARAMETERIZED sub-handlers: `bb_is_cmp_str` · `bb_type_test_str` · `bb_term_inspect_str` · `bb_term_io_str` · `bb_findall_str` · `bb_list_str` (each `(pBB, fn, hdr)`) → **CV9**
- `fn` / `hdr` / `r` locals → **CV6**
- raw-byte BINARY fallback arm `bytes(1,"\xE9") + u32le(0) + bytes(1,"\xE9") + u32le(0)` → **CV5/R3** (it is the BINARY twin of the TEXT `jmp γ; def β; jmp γ` stub — decompose to `x86("jmp", …)` forms)
- many dispatch returns → **rp**

**Dropping `pBB` is impossible until EVERY sub-handler is parameterless.** Sanctioned path = the **IR_DET_\* per-builtin migration already begun**: `bb_det_succ_plus` + `bb_det_type_test` exist and are dispatched directly from `emit_core.c:526`/`:531` via `IR_DET_TYPE_TEST`/`IR_DET_SUCC_PLUS` (IR kinds in `IR.h:106`/`:111`). Pattern per remaining builtin: mint an `IR_DET_*` kind (`IR.h` + `scrip_ir.c` name table) → lower to it (`lower_*.c`) → `bb_prepare` delivers its fields (`emit_bb.c` + `sm_emit_t`) → add `bb_det_X()` template (parameterless, reads `_.op_parts_*`) → dispatch it from `emit_core.c` → retire that builtin's strcmp arm from `bdisp`. When `bdisp` empties, `bb_resolve` dissolves to parameterless.

**Z→A order AMONG the resolver-family files** (these ARE the `bb_resolve` stop; sort across the alphabet but are all worked here, ordered Z→A among themselves): `bb_type_test`(58) → `bb_term_io`(62) → `bb_term_inspect`(97) → `bb_list` → `bb_is_cmp`(110) → `bb_findall`(10) → then `bb_det_type_test`(2)/`bb_det_succ_plus`(2) `lv` cleanup. (`bb_succ_plus` 99abc83 and `bb_retract_throw` already 0.)

**SHARP FIRST CHECK (possible quick win):** since `IR_DET_TYPE_TEST`/`IR_DET_SUCC_PLUS` already dispatch via `bb_det_type_test`/`bb_det_succ_plus`, verify whether `bb_type_test_str`/`bb_succ_plus` in `bdisp` are now DEAD legacy paths (no builtin still routes through the strcmp arm). If dead → remove the arm + retire the file = cheap `bdisp` shrink toward dropping `pBB`. If still-live → full per-builtin IR_DET_* mint as above. Check what each `bdisp` arm matches (`_.op_sval` / `fn` strcmp) vs what `lower_*.c` now lowers to an `IR_DET_*` kind.

## FLAGS FOR LON (genuine, non-blocking — resolve before/at next session)
1. **Shared cursor.** The tracker holds ONE `# CURSOR:` line, but ≥2 goals commit to this tree (this Z→A goal + GOAL-BB-FIXUP gvar-arith/Pascal family; `532bc79` Pascal forward-decl driver landed concurrently THIS session). Setting the cursor to `bb_resolve` assumes the cursor belongs to Z→A (per the goal's own 2026-06-12 reset note). If the other goal shares it, say so / split it.
2. **No-skip vs. blocked dispatcher.** `bb_resolve` (dirty) cannot hit rc=0 until its sub-handlers are parameterless, and three of them (`type_test`/`term_io`/`term_inspect`) are FILE-NAME-nearer-Z than the cursor's prior spot — "behind" a strict file-name sweep. Working resolution applied: treat the resolver family as ONE stop at `bb_resolve`, sub-handlers ordered Z→A among themselves. Confirm that's how you want the no-skip SOP to apply to a dispatcher-with-components.

## INHERITED, STILL UNADDRESSED
`audit_bb_fixup_file.sh` checks NEITHER **CV9** (`_str` suffix / parameter presence) NOR **CV10** (IR-graph access) — flagged since the 5th-session watermark. The spec is therefore unenforced for the two CONVERSIONS most central to the `bb_resolve` family. Adding those greps would make the family's progress measurable.
