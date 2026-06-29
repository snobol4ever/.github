# HANDOFF — 2026-06-29 — Sonnet 4.6 — GZ#5 enum-amputation prep + ONE-EMITTER-DRIVER roadmap

## SCRIP HEAD: 8f3e4b23 (committed locally; **PUSH PENDING — credential needed, handoff INCOMPLETE until pushed**)

Lon's directive this session (escalated across three turns):
1. Drop the redundant manual "heartbeat" step (hello-world + 1+2 by hand). The Icon rung smoke
   suite (`scripts/test_icon_ir_rung_*.sh`, 41 rungs) already covers it. Heartbeat was never a
   script — only a workflow habit recorded in handoffs. STOP reciting it; smoke suite is the gate.
2. Remove all IR_* enums not used by the new `emit_drive`.
3. Mechanism correction: do NOT delete/edit BB template files. Use **remove-from-build +
   keep-intact-on-disk** for any source in the way (same pattern as `lower_noicon_stubs`).
4. Remove all non-Icon language EMITTER code; consolidate `emit_bb.c` + `emit_core.c` into
   `emit_drive.c` — the ONE EMITTER DRIVER. Consolidate the headers. Other languages HIBERNATE
   (intact on disk, out of build) while Icon works.

## What LANDED this session (1 commit, green + smoke-verified)

**`8f3e4b23` — enum-amputation prep.** Two coordinated edits, build green, broad Icon smoke green
(vars/arith/concat=30/200/foobar; user-proc f(41)=42; abs(-5)=5; hello-world + 1+2 both modes):
- **Pulled 118 non-Icon BB templates + 5 non-Icon support TUs from the Makefile** (both the `scrip`
  link and the `libscrip_rt.so` link share the `\`-continued source list, so both were trimmed).
  Files KEPT INTACT ON DISK. The 5 support TUs: `emit_term_build.cpp`, `unification.c`,
  `prolog_lower.c`, `rebus_lower.c`, `bb_pat_build.cpp`. **NOT pulled** (Icon needs them):
  `arith_fold.c` (emit_bb.c calls `gz_arith_*`), all `opt/*`.
- **Trimmed `walk_bb_node` (emit_core.c) to the 27 `emit_drive` keep-ops.** Necessary so the link
  doesn't reference the 118 pulled templates. walk_bb_node is NOT a template — it's the essential
  dispatch `DRIVE_FILL` routes through, so editing it is correct.
- Gate unchanged at **HARD=6** (the 6 `->op` writes are still in `resolve_call_kinds_descr`,
  emit_bb.c:1819-1831 — F2 call-kind classification; that is B4, a later rung).

KEEP-TEMPLATE SET (22, stay in build): bb_lit, bb_lit_scalar, bb_keyword, bb_var, bb_var_global,
bb_binop_arith, bb_binop_relop, bb_binop_concat_slot, bb_call, bb_call_fn, bb_call_proc_staged,
bb_call_bool, bb_call_write_slot, bb_to, bb_every, bb_conj, bb_succeed, bb_fail, bb_return, bb_unop,
bb_assign_local, bb_gvar_assign.

## ⛔ THE ENUM DELETE IS BLOCKED ON THE EMITTER CONSOLIDATION — measured, not guessed

Target keep-set = **37 enums**: the 27 in `emit_drive`'s switch + 3 binop discriminants
(`IR_BINOP_ARITH/RELOP/CONCAT`, used as `op_binop_kind` tags, returned by `binop_slot_kind`) + 7
pinned by KEPT templates (`IR_CALL_DEFINE`, `IR_PROC_GEN`, `IR_SEQ`, `IR_VAR_FRAME`,
`IR_VAR_FRAME_REF`, `IR_IDX`, `IR_TO_BY` — bare-code refs in bb_call/bb_to/bb_gvar_assign).

Delete-set = 185. **But only 3 are deletable RIGHT NOW.** The other 182 are pinned by essential,
non-pullable files (counts = distinct delete-set enums referenced, strings/comments stripped):
- `scrip_ir.c` = 176 — but these are JUST the metadata: `kind_names[]` (designated initializers),
  `bb_op_name`, `ir_node_produces_value`. They delete in lockstep with the enum, NO obstacle.
- `emit_bb.c` = 140 — the REAL blocker. `resolve_call_kinds_descr` + SNOBOL match-retag + the
  Prolog `gz_*` cluster + GVAR-arith cluster reference Prolog/SNOBOL enums.
- `scrip.c` = 64 — the `pl_gz_*` Prolog codegen subsystem (lines ~367–3471, ~699 lines,
  INTERLEAVED with `main()` at 2508 and the Icon dispatch — NOT cleanly contiguous).
- `lower_icon.c` = 33 — Icon lower still EMITTING ops emit_drive doesn't own yet (IF/WHILE/EVERY/
  SCAN/etc). These must be removed/redirected to JCON primitive chains as those ops get owned.
- `emit_core.c` = 3, `arithmetic.c` = 1 — trivial.

So: **the enum delete cannot complete until the non-Icon emitter code is removed from emit_bb.c +
scrip.c.** That is exactly Lon's directive #4. Do #4 first, the enum delete falls out.

## ⛔ CRITICAL FINDING — the Icon path is STILL entangled with the legacy `walk_bb_flat` fat driver

Do NOT blind-delete by name prefix. Verified call-graph facts:
- **`gvar_*` family is ICON, not Prolog.** `gvar_flat_chain_build*` / `codegen_gvar_flat_chain_body`
  / `gvar_chain_*` / `gva_collect_*` are Icon's GLOBAL-VARIABLE codegen (`g := expr`), called from
  scrip.c's Icon path (3164/3233/3308/3484/3541/3550). KEEP THEM.
- **`bb_build_flat` is ON THE LIVE ICON MODE-3 PATH.** scrip.c:3425 calls `bb_build_flat(root_node)`
  with `g_descr_flat_chain=1` whenever `root_node` is non-null (the common case).
  `bb_build_flat → codegen_flat_body → walk_bb_flat_or_inline_alt → walk_bb_flat`. So `walk_bb_flat`
  and `bb_prepare` (388 lines, emit_bb.c:575-963) are REACHED BY ICON. Removing them blind breaks
  Icon `--run`. (The CLEAN Icon path is `descr_flat_chain_build → codegen_flat_chain_body →
  emit_drive` at emit_bb.c:1552 — but it's only taken when `root_node` is NULL.)
- TRULY non-Icon (removable once disentangled): `pl_gz_build`, `pl_gz_codegen`, the `gz_*` cluster
  (emit_bb.c 312-532), and the SNOBOL pattern/scan cluster (`scan_*`, `is_pat_chain_elem`,
  `emit_cat_diamond`, `gather_lowered_cat_arms`, `repalt_*`, `case_slot_*`, `ir_alt_all_literal_arms`,
  `scan_pat_cat_concat`, `while_*`). BUT `walk_bb_flat`/`walk_bb_flat_or_inline_alt`/`codegen_flat_body`/
  `bb_build_flat` cannot go until the mode-3 dispatch (scrip.c:3424) is flipped to take the
  `descr_flat_chain_build` (emit_drive) path unconditionally.

## NEXT-SESSION RUNG ORDER (full budget; each rung Icon-smoke-green + committed separately)

**R1 — Flip Icon mode-3 off `bb_build_flat`.** In scrip.c:3424, make the `root_node` branch also use
`descr_flat_chain_build(bbg->entry)` (the emit_drive chain) instead of `bb_build_flat(root_node)`.
Verify mode-3 smoke (the 41 rungs, or at least hello/arith/vars/proc/builtin) stays green. This
severs Icon from `walk_bb_flat`/`codegen_flat_body`/`bb_build_flat`. If a construct regresses, that
construct's `walk_bb_node` arm needs porting to `emit_drive` first (grow the driver).

**R2 — Remove the SNOBOL pattern cluster + `walk_bb_flat` + `bb_build_flat`/`codegen_flat_body` from
emit_bb.c** (now dead after R1). Also `pl_gz_*`/`gz_*` (Prolog) from emit_bb.c. Build green.

**R3 — Remove the `pl_gz_*` subsystem from scrip.c.** ~699 lines, interleaved — extract or trim.
Frees scrip.c's 64 enums.

**R4 — Trim `lower_icon.c`** of emission for ops emit_drive doesn't own (33 enums) OR grow emit_drive
to own them (IF/WHILE/EVERY/TO_BY/SUSPEND/SCAN — see prior CALL-ARGS handoff "what's next" + JCON
`ir_a_If`/`ir_a_Every`/`ir_a_ToBy`). Each owned op = one freed enum + one fewer lower-emit.

**R5 — Delete the now-unreferenced enums** from IR.h + `kind_names[]`/`bb_op_name`/
`ir_node_produces_value` in scrip_ir.c (lockstep; designated initializers make it line-deletes).
Re-run the `/tmp`-style residual scan (enums with zero bare-code refs in remaining build) — target
the 37 keep-set + whatever R4 hasn't yet freed.

**R6 — Consolidate `emit_bb.c` (Icon remnant) + `emit_core.c` into `emit_drive.c`.** NOTE the C/C++
boundary: `emit_core.c` is compiled via `emit_core.cpp` (C++; templates need C++ linkage); `emit_bb.c`
and `emit_drive.c` are C. `walk_bb_node` calls C++ templates. Either compile the merged `emit_drive`
as C++ (rename to .cpp or include-pattern like emit_core.cpp), or keep the template-calling dispatch
in a .cpp TU. Plan the linkage BEFORE moving code.

**R7 — Consolidate headers** (emit_bb.h, emit_core.h → emit_drive.h or a single emit.h).

**R8 — Gate strict-0 (B7)** once resolve_call_kinds_descr moves to LOWER (B4) — the last 6 mutations.

## Files / scope reference
- emit_bb.c = 2259 lines, emit_core.c = 648, emit_core.cpp = 15 (just includes emit_core.c +
  template headers), emit_drive.c = 107.
- Checkpoint branch `enum-amputation-checkpoint` exists at the pre-session HEAD for safety.
- Keep/drop template lists + delete-set were computed mechanically; reproduce via the bare-code
  enum-reference scan (strip `//`, `/* */`, and `"..."` then grep `\bIR_X\b`).

## PUSH STATUS: **INCOMPLETE — BLOCKED ON CREDENTIAL**
SCRIP local HEAD `8f3e4b23` is committed but NOT pushed. `.github` handoff doc NOT committed/pushed.
Per RULES.md this handoff is BLOCKED until `git push` succeeds and `scripts/handoff_status.sh`
prints HANDOFF COMPLETE for both repos. Need the credential.
