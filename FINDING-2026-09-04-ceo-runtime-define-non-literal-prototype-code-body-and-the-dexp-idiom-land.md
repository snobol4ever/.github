# FINDING 2026-09-04 (ceo): runtime DEFINE lands -- a non-literal prototype (the gimpel DEXP idiom), a runtime prototype over a compiled body, and a compile-time DEFINE whose body arrives through CODE()

Written 2026-09-04 22:50 CDT. Row `snobol4-runtime-define-non-literal-prototype-is-outside-the-landed-subset` (THE FIVE #1, ceo under QUARTET). Tree: SCRIP/corpus hashes are in the CEO-274 receipt (`GOAL-CEO.md`); measured against origin `27f3fdde3` (SCRIP) / `30ca339da` (corpus) merged in before grading.

## CLAIM
Four shapes of DEFINE that the lowerer refused ("outside the landed subset") now run in both modes and match `sbl -bf`: (1) `DEFINE(NAME ARGS)` with a computed prototype -- the gimpel `DEXP` idiom (CODE() writes the body, DEFINE binds it); (2) a runtime prototype over a body compiled in the program; (3) a literal `DEFINE('F(X)')` whose entry label does not exist at compile time and arrives later through CODE(); (4) a literal DEFINE of a SPITBOL system function (SQRT, SIN, LOAD) is SPITBOL's runtime error 248, no longer a compile-time abort.

## MECHANISM (no new globals, no struct growth -- `rt_proc_t` is size-baked by rtx_plcall.s)
- lowerer: a non-literal prototype lowers as a plain by-name `IR_CALL "DEFINE"`; a literal DEFINE whose entry label has no landing (or names a system function) lowers as the same runtime call instead of a bind box; a program with any such DEFINE counts as uses-code so every label is registered for `rt_goto_resolve`.
- `_DEFINE_` (core.c) registers a dyn-scope proc from the parsed spec (params+locals as pnames, nformals = params).
- `rt_call_proc_descr`: a dyn-scope proc with no body resolves lazily through the DEFINE registry's entry label (`core_define_entry_label` -> `rt_entry_resolve`), binds through the ordinary dyn prologue, and enters a CODE() fragment chain through the new `rt_proc_enter_frag` thunk (the stack parity of `rt_chain_enter_v`; the crash signature was `movaps` in snprintf under `eval_build_chain` / `rt_fire_buildplan_tweak` = misaligned rsp) or a compiled label through `rt_proc_enter_named`.
- RETURN/FRETURN/NRETURN floaters inside a runtime fragment release the fragment's CLASS-C frame (`add rsp, flat_frame_bytes`, the release `bb_goto_deferred` already emitted) before popping the port pair (the first crash: `jmp *rcx` with rcx = 0x1a1a... frame poison).
- `APPLY_fn`: a name with no C function but a registered proc calls the proc (both the found and the not-found branch). ⚠ The mode-3 tree-walking fallback in `src/driver/driver_call.c` (`call_user_function`, reached from `_usercall_hook`) had masked this: FLOOR read green in mode 3 through the interpreter and error 5 in mode 4. MODE 4 IS THE HONEST ARM FOR BY-NAME CALLS.

## EVIDENCE
- Gate `SCRIP/scripts/test_gate_sno_runtime_define.sh` (in `make test` after the quad gate): 4 witnesses `corpus/tests/snobol4/rtdef_*.sno` + refs cut from the oracle, both modes, refs re-cut live; RED 6 of 8 arms on origin pre-fix (fail-once proven), GREEN after.
- gimpel drivers (`packages/snobol4/gimpel/*_driver.sno` vs `sbl -bf`, both modes): DEXP DEXTERN FLOOR LOG POL STACK GREEN (6 of the row's 11).
- SNOBOL4 master (harness, `--by-modes-column --modes m3,m4`): m3 1777 pass / 0 fail, m4 1777 / 0 of 1830 run-graded; two XPASS promoted in ALL.csv (`user_function_6`, `user_function_code_eval_bal_branch_1`); `fence_capture_imm_capture_replace_branch_1` XPASS in m4 only (hq_B's FENCE landing, m3 still xfail -- left).
- Controls, identical on origin and on the fix: Snocone smoke 5/5; Icon master board m3 599 / m4 599 of 601 (SCORE cell says 601/601 -- `procedure_write_image_1`, `procedure_record_every_replace_2` red on origin `27f3fdde3` itself -> hq_B); Prolog ladder `--to 9` 10 of 380 gradings red on origin itself (SCORE floor says 56/56 -> hq_C); `test_gate_sno_setexit_resume_matches_oracle.sh` 5 of 6 arms red on origin itself (hq_P landed a blocking gate red on origin/main -> hq_P; it makes `make test` red for every seat today).
- Artifact regen chain: benchmark/demo/prolog-bench all "already current" (0 changed).

## NOT IN THIS CLASS (routed)
- ARC, TRIG, L_TWO drivers: SPITBOL ABORTS on the library's own `DEFINE('SQRT(Y)...')` and prints its fatal listing (file(line) : ERROR 248, then `memory used (bytes) 15688` etc.) -- no implementation can match those bytes: wave 5 (unscorable), named beside the cell in GOAL-SNOBOL4-100.
- INFINIP_lib: `OPSYN('MINUS.','-',1)` / `OPSYN('-','MINUS',1)` -- OPSYN over a PREDEFINED operator, error 156 today -> row `snobol4-opsyn-redefines-a-predefined-operator` (hq_C, shared engine).
- REDEFINE: an OPSYN function synonym is a NAME alias that follows the later redefinition (witness: `OPSYN('MYF.','MYF')` then `DEFINE('MYF(S)','MYF2')` whose body calls `MYF.` -> `new[]` in m3, stack overflow in m4, identical on origin) -> row `snobol4-opsyn-function-synonym-is-a-snapshot-not-a-name-alias` (hq_C).
