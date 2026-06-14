# HANDOFF 2026-06-14 — Icon m3/m4: native IR_SECTION (string `s[i:j]`) — WIP, one slot bug left (Claude)

**Goal:** GOAL-ICON-FULL-PASS — Icon `--run`/`--compile` up to m2 parity.
**State:** WIP, does NOT pass yet. Build clean. m2 untouched (lowering not modified → HARD gate intact).
**HEAD (SCRIP) before this work = `3738eac`.** Baseline captured at session start: **m2=202 (HARD) · m3=112 · m4=112**.

## Target
3 native-only FAILs, one shared root cause — string sectioning `s[i:j]` had NO native arm
(silent-empty rc=0 in m3/m4, correct in m2): `rung20_section_seqexpr_section_basic` (`s[1:4]`→hel),
`_section_var` (`s[i:j]`), `_section_full` (`s[1:6]`). Broader native-only FAIL list (30) captured in
`/tmp/m3_fail.txt` vs `/tmp/m2_fail.txt` during the session (regenerate with
`bash scripts/test_icon_rung_suite.sh --mode run|interp` then `comm -23`).

## What landed (uncommitted unless I committed below; 5 files, all ADDITIVE, mirroring `bb_field_get`)
1. `src/emitter/BB_templates/bb_section.cpp` — NEW. Loads base DESCR→rdi:rsi, i1→rdx:rcx, i2→r8:r9,
   `call subscript_get2` (exported `T` in libscrip_rt.so — mode-4 resolves), result→own slot, `β→ω`
   (one-shot, deterministic). `ival!=0` (the `s[i+:n]`/`s[i-:n]` variants) → `x86_bomb` (no test needs
   them; strictly better than today's silent-empty). r8/r9 frame loads confirmed encodable
   (`x86_reg_disp32_load64` handles `g>=8` REX).
2. `src/emitter/BB_templates/bb_templates.h` — `std::string bb_section();`.
3. `src/emitter/emit_core.c` — `case IR_SECTION` in `walk_bb_node` flat-chain path (sets
   `g_emit.op_off = bb_slot_alloc16(nd)`, calls `bb_section()`), mirroring the `IR_FIELD_GET` case at :479.
4. `src/emitter/emit_bb.c` — `flat_drive_section()` (after `flat_drive_field_get`) + `case IR_SECTION` in
   `walk_bb_flat` dispatch. Driver emits the OFF-THREAD operands i1,i2 via `walk_bb_flat`, sets
   `g_emit.op_sa=slot(i1)`, `g_emit.op_sb=slot(i2)`, then `EMIT_PAIR_FILL`. base (operand[0]) is
   ON-THREAD (lowering returns `ae`=base entry, `base.γ→SECTION`) so it is NOT re-emitted; the template
   reads base via `op_a_slot` (set by the generic head of `walk_bb_node` from operands[0]).
5. `Makefile` — 2 lines mirroring `bb_field_get.cpp` (source list ~218 + compile recipe ~472). Link globs
   `$(OBJ)/*.o`.

Lowering of IR_SECTION (`lower_icon.c:215`, unchanged): operands [base,i1,i2]; `IR_LIT(sec).ival` =
0 plain / 1 `+:` / 2 `-:`. Interp semantics (`IR_interp.c:3906`): eval 3 operands, variant math on
ival 1/2, then `subscript_get2(base,i1,i2)`, FAIL→ω else value→γ. (1-based, `s[1:4]` of "hello" = "hel".)

## THE REMAINING BUG (precise, from reading the emitted m4 asm)
The SECTION emits and runs correctly — it computes the substring and stores the result DESCR at its own
slot **`[r12+96]`** (`mov [r12+96],rax; mov [r12+104],rdx`). BUT the following `IR_CALL write(...)`
operand-marshal reads its argument from **`[r12+128]`** (`lea rsi,[r12+128]; mov edx,1; call rt_call_arr`).
**Slot 96 (section result) ≠ slot 128 (the slot write marshals from)** → write reads an uninitialised
slot → empty output. The math/call is right; only the result-slot↔CALL-arg-slot wiring is wrong.

**FIX DIRECTION (next session):** make the SECTION node deposit into the slot the CALL marshals its arg
from (the same mechanism the WORKING value boxes use — `bb_var`/`bb_to`/`bb_lit_scalar` all feed `write`
correctly). Compare how those nodes' result slot coincides with the CALL operand-marshal slot (the CALL
arg-marshal in `bb_call.cpp` / `descr_chain_operand_refs` + the arg slot base — note `lea rsi,[r12+128]`
and `descr_chain_operand_refs(entry)` at `descr_flat_chain_build:3483`). Likely either (a) the section's
`op_off` must be the operand-ref slot the CALL allocated for arg0, not a fresh `bb_slot_alloc16`, or
(b) a copy from 96→128 must be emitted, or (c) `descr_chain_operand_refs` needs to recognise IR_SECTION
as the producer for the CALL arg so the arg slot == the section slot. Inspect `descr_chain_operand_refs`
(how CALL args get their marshal slot) and how `bb_var`'s result lands in that same slot — that is the
template to copy. m2 stays at 202 throughout (no lowering change).

## VERIFICATION STILL OWED (could not run under session budget — DO THIS FIRST next session)
- Full `bash scripts/test_icon_rung_suite.sh` (all 3 modes): confirm **m2 still 202** and **m3/m4 ≥ 112**
  (no regression from the additive emit_core.c/emit_bb.c cases). Changes are reached ONLY for IR_SECTION
  so regression risk is near-zero, but it was NOT re-verified post-change. Also `test_smoke_prolog.sh`
  (5/5) since emit_bb.c is shared.
- Then iterate the slot fix until the 3 rung20 section tests PASS m3/m4 → expected m3/m4 112→115.

## Files touched (SCRIP): `bb_section.cpp` (new), `bb_templates.h`, `emit_core.c`, `emit_bb.c`, `Makefile`.
**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
