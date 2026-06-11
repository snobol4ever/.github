# HANDOFF 2026-06-10 OPUS48 — PROLOG-BB ARITY-3 / rung06

**Goal:** GOAL-PROLOG-BB.md · PL-GZ-9 corpus reconquest.
**Watermark:** SCRIP `1a1eeb6` · .github `8af9d78a` (both pushed, battery green).

## Landed

**rung06 (`append/3`, `length/2`, `reverse/2`) admitted onto the native m3 (`--run`) path.**
GATE-3 m3 ratchet **27 → 28**. No regressions: m2=114, m4=51. GATE-1 5/5/5.
Structural gates green: one-box, no-vstack, pl-no-value-stack, no bytes outside templates.

### Mechanism — lift the arity-2 ceiling to arity-3
The GZ call path was hard-capped at arity 2 (only `rsi`/`rdx` arg registers, `[2]`-wide
state arrays, `ar > 2` admission guards). Widened to arity-3:

- `src/interp/IR_interp_state.h`: `pl_gz_choice_state_t` `args[2]→[8]`, `consts[4][2]→[4][8]`;
  `pl_gz_call_state_t` `args[2]→[8]`.
- `src/emitter/BB_templates/bb_cell_call.cpp`: `bcc_areg` 3rd register `rcx` (`rsi`/`rdx`/`rcx`);
  `bcc_sh()` nargs limit `<= 2 → <= 3`; `bcc_ar()` extended to check `op_parts_ival[5]`; arg-load
  `FOR` loop cap `< 2 → < 3`. NOTE: this file was rebased onto a concurrent session's
  `op_parts_ival` refactor (see below) — it now reads `op_parts_ival[]`, not the `bcc_st()` struct.
- `src/emitter/emit_bb.c`: added `op_parts_ival[5]` fill for arg-2 in the `IR_CELL_CALL` case
  (mirrors the `[3]`/`[4]` fills for args 0/1).
- `src/emitter/BB_templates/bb_callee_frame.cpp`: `bcf_areg` 3rd register `rcx`; arity guard `> 2 → > 3`.
- `src/emitter/BB_templates/bb_cell_choice.cpp`: arity guard `bcch_A() > 2 → > 3`.
- `src/driver/scrip.c`: six `ar > 2 → ar > 3` admission guards
  (`pl_gz_choice_inline`, `pl_gz_choice_rule_clauses`, `pl_gz_rule_body_goal_ok`,
  `pl_gz_rule_inline_check`, `pl_gz_rule_callee_body`, choice call-site); and the two synth-arg
  counting caps `ai < 2 → ai < 3` (`pl_gz_clause_nsynth`, `pl_gz_count_synth_goal`) that size the
  callee frame — without these a non-logicvar 3rd arg gets no synth slot and the frame is undersized.

Admission was set to `ar > 3` (not unbounded) so it matches the 3-register emitter; arity-4+
hits the loud `x86_bomb` stub rather than mis-emitting.

### Rebase event
Pushed into a conflict: a concurrent session (`f5072d0`) had refactored `bb_cell_call.cpp`'s data
contract from the `pl_gz_call_state_t` struct to `g_emit.op_parts_ival[]`, and removed the
`IF(MEDIUM_TEXT, …)` head-wrapper per the new RULES.md "NO MEDIUM_* IN TEMPLATES" FACT RULE.
Resolution **ported arity-3 onto their new contract** rather than clobbering either side — kept
their hygiene refactor + MEDIUM_* removal, layered the 3rd register / lifted limits / added the
`op_parts_ival[5]` fill on top. Re-verified green after the merge (commit `1a1eeb6`).

## Open / next

- **rung09 is next** on the PL-GZ-9 ladder: `functor/3`, `arg/3`, `=../2` — IR_BUILTIN
  term-inspection builtins not yet in `pl_gz_rule_body_goal_ok`. Self-contained next piece.
- **m4 rung06 still prints `[]`** — the legacy `pl_rich_body_root` rich-tier mishandles arity-3.
  Per M34-5 this is an admission-gap item to close on the GZ path, **NOT** to patch in the m4
  fallback. Left as-is; recorded in the goal STATE block.
- **Lowerer deletion question UNRESOLVED (Lon to decide).** Lon asked to "delete the old"
  Prolog lower stage, naming `lower_prolog_nl.c` as the new one. Investigation found the roles
  reversed: `lower_prolog.c` (619 lines, exports `lower_goal_entry`/`lower_clause_body_entry`) is
  the **live** m2/m3/m4 path (feeds `lower_program.c:320` + the `prove_lower2.sh` topology gate);
  `lower_prolog_nl.c` (179 lines, exports `lower_prolog(prog)`) is wired **only** to the
  `--dump-bb2` diagnostic. Deleting `lower_prolog.c` breaks the build; deleting `lower_prolog_nl.c`
  contradicts the "keep the new one" instruction. **Both left in place pending one word from Lon:**
  (1) delete the dead-end `lower_prolog_nl.c` + repoint `--dump-bb2`, or (2) finish the NL migration
  (grow `lower_clause_body_entry`/`lower_goal_entry` into the NL file, or repoint `lower_program.c`
  + `prove_lower.c` to the whole-program `lower_prolog()` entry) before retiring the old file.

## Notes
- Uploaded gprolog/swipl reference zips did not mount this session (uploads dir empty at tool time).
  Prolog authority used: corpus `.expected` files + m2 interpreter as oracle (per RULES — Proebsting
  is canon; gprolog/SWI are observable-semantics oracles only).
