# HANDOFF 2026-06-13 — ICON-BB: IR-IMMUTABLE / AST-interp deletion VERIFIED already landed (NO code change)

**Goal:** GOAL-ICON-BB / GOAL-ICON-FULL-PASS.
**Session type:** orientation + READ-ONLY verification. **ZERO code changed.**
**SCRIP HEAD = `ae008c6`** (== origin/main; working tree clean). **.github HEAD = `6d86d91b`** + this file.
**Tallies NOT re-run this session** (verification was static/grep only) — per prior handoff they stand at
m2 202 / m3 76 / m4 82; next session should re-run `scripts/test_icon_rung_suite.sh` to confirm before building.

## Why this handoff exists

Lon re-presented the long-standing instruction: "the IR is NEVER TOUCHED in mode 3/4 — delete any code that
does so, NULL-bomb + physically remove the call sites; and DELETE any tree_t AST walker used for
interpretation (m2 or m3), even if it breaks m2." This session confirmed — grounded in `git log`, not the
docs — that **the task is already DONE and correct at `ae008c6`.** No re-execution was needed or performed.

## Git evidence the task is landed (read these commits, do not redo them)

- `ae008c6` — dropped the `IR_t *` + the IR-walker builder hook (`g_rt_gen_proc_builder`/`rt_proc_set_builder`)
  from the mode-3/4 runtime proc registry. Registry is now name + emitted-code fn-ptr only.
- `603b185` — **DELETED the `tree_t` AST interpreter** (`interp_exec_builtin`, ~1666 lines from
  `resolution.c`); commit message states the principle verbatim ("An AST walker that does not emit IR is
  worthless even for m2"). The dead `eval_node(tree_t*)` in `runtime_eval.c` is now a LOUD BOMB.
- `0f6506b` / `76639bd` — eradicated the runtime IR-walk in m3/m4: deleted `rt_node_to_term_ptr` /
  `emit_term_from_node_bin` (the pattern that baked a live `IR_t*` into emitted code) and bombed the BINARY
  arms (`bb_term_inspect`/`bb_term_io`/`bb_list`) that did it.

## ⚠️ WARNING TO NEXT SESSION — do NOT re-bomb the EMISSION read

The literal "delete any code that touches IR in mode 3/4 and NULL-bomb it / remove from file", **if applied to
the emission-time read, is the `e50b089` trap that was REVERTED at `8b9a58e`** ("emission read of IR is
required & allowed"). Mode 3 needs exactly ONE read of the IR to build the RX-slab image; mode 4 needs ONE to
emit the `.S` source. The prohibition is **execution-time only**: no IR access DURING execution of the emitted
artifact. **Do NOT physically purge `emit_bb.c` — its IR read IS the sanctioned emission read.** Lon's own
clarifying paragraph this session drew exactly this line, so we are aligned.

## Runtime confirmed clean (grep, this session)

- No `rt_*` helper takes an `IR_t*`/`IR_graph_t*` reachable from emitted code (EVAL/CODE rail excepted).
- Residual `tree_t` in `src/runtime/` is only: the sanctioned EVAL/CODE compile rail (`EXPVAL_fn` /
  `CONVE_fn` / `CODE_fn` in `runtime_eval.c`, `interp_eval_pat` in `pattern_match.c`) + already-bombed
  `eval_node` + harmless weak stub `_expr_is_pat` + emission-time scope analysis (`scope_patch`/`static_*`
  in `name_binding.c`).

## FLAG (NOT actioned — SNOBOL, out of Icon scope)

`src/runtime/by_name_dispatch.c` `script_try_call_builtin(tree_t *call, ...)` still takes an AST node on a
**SNOBOL by-name** path. The Icon goal fences this session off SNOBOL families, so it was left untouched. If
the execution-time IR/AST audit should extend to SNOBOL, that is a separate SNOBOL session.

## Live Icon priorities (unchanged, from prior handoffs)

1. **Real-arithmetic native path** (rc=134, highest leverage): `descr_binop_opnd_slot` (emit_bb.c ~1420)
   returns -1 for `IR_LIT_F`, so real/mixed operands get no slot and the arith template is integer-only. Slot
   `LIT_F` operands + add a real-arith arm (SSE `addsd/mulsd/divsd`, or a DESCR-in/out `rt_*` helper matching
   the m2 interp real coercion). Unblocks rung17/18 and rung26 `2^3+1` (`LIT_F+LIT_I`).
2. **Real `bb_every` four-port box** (architectural): `bb_every.cpp` is a hollow stub; the real drive/resume/
   exhaust lives in `flat_drive_every` (a DRIVER, violates TEMPLATE-ONLY). Build the box mirroring canonical
   `ir_a_Every` (irgen.icn:309). Fixes the rc=124 generator-resume timeout cluster.
3. **Native builtin call wiring** — `push`/`read`/`iand` unsupported in `bb_call` (rung22/27/37).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
