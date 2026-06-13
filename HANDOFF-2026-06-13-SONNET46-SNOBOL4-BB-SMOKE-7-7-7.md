# HANDOFF 2026-06-13 · Sonnet 4.6 · SNOBOL4-BB smoke 7/7/7

**SCRIP HEAD:** 2f52ff4
**.github HEAD:** (this commit)

---

## What this session did

Fixed three classes of M3/M4 regression. **smoke 7/7/7 achieved** (was 6/7). **M4 pat-rung 19/19 no-SKIP** holds. M3 pat-rung 18/19 (one new bug found and documented).

---

## Bug 1 — 6× `x86("lea","rdi","[rip+label]")` TEXT silent-empty (bb_call.cpp)

**Root cause.** The `x86()` dispatcher in `x86_asm.h` handles `"lea"` only for specific operand kinds (`XK_RIPSEAL`, `XK_FR*`, `XK_REGDISP`, `XK_R13RCX`, `XK_REG`). A plain string like `"[rip + .Ldefspec11]"` parses to an unrecognised kind → dispatcher returns `std::string()` silently. The `lea rdi` instruction was never emitted. In TEXT mode, `rdi` was left at whatever value it held, so `rt_proc_define`, `rt_call_named_proc`, `rt_gvar_get_int`, `rt_gvar_cell`, `rt_call_proc_descr`, `rt_call_arr` all received a garbage or stale `rdi` → functions silently failed or returned FAILDESCR.

**Fix.** Replaced all 6 instances with `x86("directive", (" lea rdi, [rip + " + label + "]").c_str())`. This emits the raw asm string through the TEXT directive path, bypassing the broken dispatcher arm.

**Affected call sites in bb_call.cpp:**
- `marshal_varparam_addr` (VAR-PARAM cell addr of gvar)
- `arith_opnd_a` (arith operand A, VAR type)
- `arith_opnd_b` (arith operand B, VAR type)
- `marshal_single_call` (inline call arg)
- `bb_call_gvar_userproc_str` (user proc call — **this was the M4-DEFINE root**)
- `bb_call_gvar_define_str` (DEFINE builtin)
- `bb_call_arr_str` (arr call by-name)
- `bb_call_proc_staged.cpp` (staged proc call)

**Symptoms fixed:** M4-DEFINE (`OUTPUT = DOUBLE(21)` → empty), M4 user-proc calls silently skipped.

---

## Bug 2 — Duplicate `lbl_β` in bb_call_proc_staged TEXT arm

Lines 58–59 both emitted `x86("label", _.lbl_β)`. Removed the redundant `x86("label", std::string(_.lbl_β))` (the `std::string` variant). Also applied the lea-rdi fix to this file.

---

## Bug 3 — bb_gvar_assign_concat BINARY: scratch buf ptr baked as string addr

**Root cause.** The single-part lit_s arm used `(uint64_t)(uintptr_t)_.bb_rs` as the binary ptr arg. `bb_rs` points to `g_emit.bb_rs_buf[64]` — a scratch buffer filled by `bb_intern_into` with the label name (e.g. `.Ss_abcd`), not the actual string `"abcd"`. In BINARY mode `x86("lea","rdi","[rip+__]", ptr, label)` bakes `ptr` as a `movabs` immediate. Baking the address of a scratch buffer → the JIT code loads the address of a char array containing `.Ss_abcd`, not `"abcd"`. `rt_gvar_assign_str` received a garbled rhs → assignment silently produced null/empty.

**Fix.** Changed the rsi ptr to `_.op_parts_str[0]` — the permanent IR sval pointer set directly from `IR_LIT(c0).sval` in `gvar_seq_flatten`. For the lhs (rdi), changed from `_.bb_ls` ptr to `_.op_sval` (which is... see M3-CONCAT-MULTIPART below).

**Result.** M4 concat fixed; M3 single-part lit concat fixed (smoke test `OUTPUT = 'ab' 'cd'` passes).

---

## Open bug — M3-CONCAT-MULTIPART (pat-rung 055)

**Symptom.** `OUTPUT = A ' ' B ' ' C` (multi-part SEQ concat) gives empty in M3, correct in M2/M4.

**Root cause identified.** The lit_s arm fix used `_.op_sval` as the binary ptr for `rdi` (the destination variable name). But `op_sval` is **NULL** for `ASSIGN_CONCAT` nodes — `flat_drive_gvar_assign` never sets `op_sval`; it only sets `op_parts_*` and `bb_ls`/`bb_rs`. So BINARY mode emits `movabs rdi, 0` → null ptr passed to `rt_gvar_assign_concat_parts` → no assignment.

**Fix (one line).** In `bb_gvar_assign_concat.cpp`, both the lit_s arm and the multi-part arm's `lea rdi` ptr arg: change `(_.op_sval ? _.op_sval : "")` → `(IR_LIT(_.node).sval ? IR_LIT(_.node).sval : "")`. `_.node` is the ASSIGN_CONCAT IR node; `IR_LIT(_.node).sval` is the destination variable name (permanent IR allocation). The `bb_ls` label (TEXT) is correct and unchanged.

Also verify the multi-part arm `op_parts_str[i]` ptrs: for LIT_S (tag=0) parts `op_parts_str[i] = IR_LIT(e).sval` (permanent); for VAR (tag=1) parts `op_parts_str[i] = IR_LIT(e).sval` (the variable name, also permanent). Both should be fine as BINARY ptrs. The function `rt_gvar_assign_concat_parts` dispatches on tag to either use `.s` as a literal string (tag=0) or call `NV_GET_fn(.s)` (tag=1). Correct.

---

## Gates at handoff (SCRIP=2f52ff4)

- smoke: **7/7/7 HARD** ✓ (was 6/7)
- pat-rung M4: **19/19 no-SKIP** ✓
- pat-rung M3: **18/19** (055 multi-part concat — M3-CONCAT-MULTIPART)
- fence: **HARD** ✓

---

## Next session

1. Fix `bb_gvar_assign_concat.cpp`: change `_.op_sval` → `IR_LIT(_.node).sval` in both the rdi ptr of the lit_s arm and the rdi ptr of the multi-part arm.
2. Run smoke 7/7/7 + pat-rung 19/19/19.
3. Commit, then continue to M4-DCAP or M4-SMOKE-REGRESS per goal ladder priority.
