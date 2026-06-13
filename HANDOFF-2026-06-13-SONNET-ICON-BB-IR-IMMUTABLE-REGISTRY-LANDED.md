# HANDOFF 2026-06-13 — ICON-BB: IR-IMMUTABLE enforced — IR pointer removed from the mode-3/4 runtime proc registry

**Goal:** GOAL-ICON-FULL-PASS / GOAL-ICON-BB. This is the IR-IMMUTABLE "ACTUAL task"
(execution-time IR-access audit) from HANDOFF-2026-06-13-IR-IMMUTABLE-MODE34.md — LANDED.
**Result:** the runtime proc registry no longer holds an `IR_t *`, and the IR-walking builder
hook is physically gone. m2 unchanged, zero regressions.
**HEAD (SCRIP) = `ae008c6`** (was 76639bd at session start). HEAD (.github) = this file.

## The rule (restated, since e50b089 misread it)
Mode 3 (`--run`) and mode 4 (`--compile`) each require **exactly ONE full read of the IR at
EMISSION time** to build their artifact (mode 3 → in-process image via `bb_build_flat`; mode 4 →
`.s` via `descr_flat_chain_build_proc_text`). That emission read is REQUIRED and CORRECT. What the
rule forbids is the IR being touched **DURING EXECUTION** of the emitted artifact — a `libscrip_rt`
helper dereferencing an `IR_t *` at run time, or an `IR_t *` baked into the generated code and
chased while it runs. The emitter is NOT bombed (that was the reverted e50b089 mistake).

## Audit finding
The **active** Icon/SNOBOL execution path was already IR-free: `rt_call_proc_descr` /
`rt_call_named_proc` / `rt_call_named_proc_sl` dispatch through `p->fn` (an emitted code pointer);
no runtime-helper TU derefs an `IR_t *`. The violation was dormant-but-forbidden **wiring**:

1. `rt_proc_t` carried a `void *entry`, and all four mode-3/4 driver blocks did
   `rt_proc_register(pname, s2->bbp.table[idx]->entry, …)` — pushing a live `IR_graph_t::entry`
   (`IR_t *`) into the runtime registry for every proc.
2. `bb_build_flat` (an IR walker, `emit_bb.c`) was installed as `g_rt_gen_proc_builder` via
   `rt_proc_set_builder` — an IR-walker aimed at those stored pointers.

Both dormant (dispatch uses `p->fn`; the builder is never invoked) → a loaded gun, not a live
deref. So there was **no live runtime IR-deref call site to stub with `(*(char*)NULL)`**. Used
enforcement-by-deletion instead — strictly stronger (the symbol/field cease to exist, so the
compiler forbids re-introduction), exactly the `bb_bin_t`-ABOLISHED philosophy already canon in the
GOAL files.

## What landed (3 files, −26/+15)
- `src/runtime/rt/rt.c`: removed `void *entry` from `rt_proc_t` and every write to it; deleted
  `g_rt_gen_proc_builder` + `rt_proc_set_builder`; dropped the `entry` param from
  `rt_proc_register`.
- `src/runtime/rt/rt.h`: removed the `rt_proc_set_builder` decl; updated `rt_proc_register` decl.
- `src/driver/scrip.c`: all four driver blocks (mode-4 Icon/Raku, mode-4 Prolog, mode-3 Icon/Raku,
  mode-3 Prolog) — `rt_proc_register(pname, pn, np)` (no `->entry`); deleted the two
  `rt_proc_set_builder(bb_build_flat)` installs + their externs + the now-unused `bb_build_flat`
  externs. The surviving `bb_build_flat(icn_root)` at the mode-3 main-graph site is the SANCTIONED
  emission read (declared via `emit_bb.h`), kept intact.

## Remaining IR reads — all sanctioned, none during mode-3/4 execution
- **Mode-2 interpreter** (`IR_interp.c` via `bb_graph_of_proc`) — reads IR by design; mode 2 ≠ 3/4.
- **Emission** (`emit_bb.c` `resolve_bb_entry_node`/`bb_build_flat`, templates) — the one emission read.
- **Prolog `sm_interp_run` clause solver** (`resolution.c` TT_FNC / `bb_graph_of_pred`) — the explicit
  RULES.md carve-out, out of Icon scope.

## Note (honesty)
The registry IR-pointer storage is a SHARED `rt.c` mechanism, so this also removed the IR pointer
from the **Prolog** registry blocks (mechanical, behavior-neutral; Prolog smoke 5/5+5/5 confirms).
If Lon wants this scoped strictly Icon-only, say so and it can be narrowed — but the rule is
byte-identical across all GOAL-*-BB files, so removing IR from the registry for every language is
strictly correct.

## Verification (explicit before/after)
- m2 interp `--mode interp`: PASS=202 → **202** (HARD floor held; diff empty, zero regressions).
- Icon smoke: m2 12/12 (HARD), m3 12/12, m4 12/12.
- Prolog smoke: m3 5/5, m4 5/5.
- `test_gate_icn_no_stack`=0, `test_gate_icn_one_reg_frame`=0.
- `test_gate_bb_one_box`: the 45 FAILs remain PRE-EXISTING (zero template files touched).
- Post-change greps: `rt_proc_set_builder`/`g_rt_gen_proc_builder` == 0 anywhere;
  `rt_proc_register(... ->entry ...)` == 0; zero `IR_t`/`IR_graph_t` in the Icon/SNOBOL execution
  helpers.

## Intel produced this session (no code) — global-variable phase split for Icon
For future register/runtime work, the Icon globals partition cleanly (derived from a call-target
trace of mode-4 `.s` over a broad rung+smoke spread, plus the scan/keyword/var/call templates):
- **Mode-3 RUN (runtime lib):** `g_names` (NV table); `global_names`/`global_count`;
  `g_root_ctx`/`g_ctx_current`; `g_rt_gen_procs`/`g_rt_gen_proc_count`; `g_call_args`;
  `g_proc_arena`/`g_proc_depth`; `g_proc_frame_nest_arena`/`g_proc_frame_nest_depth`;
  `g_name_save`/`g_name_save_top`; `g_frame_buf` (root frame); `g_rt_frames`/`g_rt_frame_depth`;
  `g_native_chunk_depth`; `g_last_ok`; `scan_subj`/`scan_pos`/`scan_stack`/`scan_depth`;
  `g_error`/`g_trace`/`g_dump`/`g_random`/`g_jcon`; `bb_rnd_seed`; `g_lang`;
  `g_halt_rc`/`g_halt_set`.
- **Mode-4 EMIT (emitter/lowering):** `g_emit_cfg`; `g_emit` (sm_emit_t op_* neighbor slots);
  `g_flat_node_id`; `g_flat_chain_set`/`g_flat_chain_set_n`; `g_descr_flat_chain`; `g_bb_alpha_seq`;
  `g_text_child_counter`/`g_in_prebuild`; `g_flat_slot_count`/`g_bb_slotmap_n`/`g_bb_varslot_n`;
  `g_subject_slot`; `g_frame_active`; `g_emit_frame_caller_dl`; `g_icn_scan_regs_live`;
  `g_flat_data_*` (sealed `[rip+disp]` RO block); `g_gvar_flat_chain`/`g_gvar_callarg_live`;
  `g_icn_postfix_resume`; `g_icn_globals_nv`.
The two sets are DISJOINT — the IR-immutability boundary made concrete: emitter state is consumed
at emission and never read by the running image.

## NEXT (unchanged priorities from the Sonnet session handoff)
1. REAL ARITHMETIC native path (rc=134) — `descr_binop_opnd_slot` (emit_bb.c ~1420) returns -1 for
   `IR_LIT_F`; slot LIT_F + real-arith template arm (SSE addsd/mulsd/divsd or a DESCR-in/out rt_*).
2. Native builtin call wiring — `push`/`read`/`iand` in `bb_call`.
3. Real `bb_every` four-port box (rc=124 cluster) — see HANDOFF-…-EVERY-BOX-MISSING.md.
4. Global var native reads (`bb_var` arm; rung21/25) — `g_icn_globals_nv` model, consult GOAL-ICN-GLOBAL-NV.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
