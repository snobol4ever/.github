# FINDING 2026-09-06 hq_U — Icon reversible assignment to a GLOBAL aborted the compiler, and the diagnostic sent every reader to the wrong file

Row `flip-ipl-scramble-rev-assign-to-a-global-aborts-the-compiler` (rank 0, hq_U). **Five IPL package
programs flip to PASS against their own `.std`: scramble, deal, conman, isrcline, itrcsum.**

## The bug, in one discriminating pair

```icon
global g                     local g                    <- the only difference
procedure main()
  g := 1;
  every (g <- 2) & write(g);
  write(g);
end
```

`local` compiles and prints `2` then `1`, matching `icont`/`iconx`. `global` **aborted the compiler**,
rc=134. Six lines, oracle-verified, and the pair is the whole diagnosis.

## Root cause

`emit.cpp`'s `IR_ASSIGN` arm tests `is_global(vn) && !graph_has_local(...)` **first** and takes a global
path carrying `op_sval`/`op_gva_k`. `IR_REV_ASSIGN` had **no such arm**: it went straight to
`bb_varslot_peek(vn)`, which resolves locals only, got `-1` for a global, and `abort()`ed. Two members
of one assignment family treating the same lvalue class differently — the NO-PER-OP-FILTER shape.

⛔ **THE DIAGNOSTIC IS WHY THIS SAT UNCHASED, AND IT IS THE REAL FINDING.** It printed:

> `[TE-4] IR_REV_ASSIGN local 'l_POS' has no LOWER-granted varslot — grant it in ir_drive_slot_assign (scrip_ir.c), never allocate in the emitter`

`l_POS` is **not a local** — `corpus/packages/icon/ipl/procs/lists.icn:365` declares `global l_POS` — and
`ir_drive_slot_assign` is **not where the fix belongs**. The message names a file, a variable class and a
remedy, and all three are wrong; following it means adding a slot grant that must never exist for a
global. It is the third instance this day of the same organism (the artifact verifier that said it built
nothing, `scrip`'s md5 that cannot move): **an instrument that states the wrong thing confidently, where
the confidence is the active ingredient** — a vague message gets investigated, a precise wrong one gets
obeyed. The message is corrected in the same commit.

## The cure

A `bb_rev_assign_global` sibling, following the engine's own per-storage-class convention
(`bb_assign_local` vs `bb_assign_global`). Save slot (`op_sc`), rhs slot (`op_a_slot`) and own slot
(`op_off`) stay frame-relative; only the **variable's** accesses become global. Both arms implemented,
because `g_gva_active` is genuinely 0 sometimes (`scrip.c:1477`, and whenever `n_gva == 0`):

- **GVA arm** — `GVARQ(op_gva_k, w)` / `ABSQ(RT_GVA_VA + op_gva_k*16 + w)`.
- **by-name arm** — `NV_GET_fn` to save, `NV_SET_fn` to store, `NV_SET_fn` again on β to restore.

The β arm restores the global from the save slot in both, because **that restore is the reversibility** —
it is the whole semantic, not a cleanup.

⭐ **BOTH ARMS ARE EXERCISED BY THE TWO MODES, WHICH I CHECKED RATHER THAN ASSUMED.** m3 takes the
by-name arm and m4 takes the GVA arm on the same witness — verified by counting `NV_GET_fn` in the
emitted `.s` (m3 non-zero, m4 zero) and reading the m4 block, which saves `[r9+0]/[r9+8]` into the frame
and restores it on β. Had I only run one mode I would have shipped half a template unexecuted.

## The trap that cost the most, and it was not in the compiler

`g_emit.op_sval` and `op_gva_k` set in the *prepare* arm **do not survive to the template**:
`walk_bb_node_inner` (`emit.cpp:1089`, `:1097`) **recomputes both** from a node-kind whitelist, using
`IR_LIT(nd).sval` — which is NULL for `IR_REV_ASSIGN`, whose lvalue name lives in `operands[1]`. So the
prepare arm's values were silently replaced with empty/-1 between being set and being read.

The symptom was not a crash in the compiler but a **SIGSEGV in the compiled program**: the by-name arm
emitted `.string ""` and no `.quad`, so `rdi` loaded garbage into `NV_GET_fn`. ⭐ The general shape:
**a field set in one pass and re-derived in a later one is not a field, it is a suggestion** — and a
whitelist keyed on node kind silently excludes every kind nobody added. Fixed by setting both at the
dispatch, after the recompute, which is where the other operand-named nodes already do it (`:1152`).

## Measured

- Row DONE-WHEN: **GATE OK** — both modes print `2/1` matching the oracle, and scramble no longer hits TE-4.
- IPL: **scramble, deal, conman, isrcline, itrcsum PASS** against their own `.std`. `makepuzz` clears TE-4
  and now reaches its real output before diverging later — **a different cause, not this class, and not
  claimed as a flip.**
- Shared-node scope: `grep -c IR_REV_ASSIGN src/lower/lower_*.c` → **icon 4, every other frontend 0**, so
  Icon is the only board this node owes; the SNOBOL4 master rides as the standard codegen control arm.
- `strip_comments.py --check` 0 files; `test_gate_template_medium_invisible` and `test_gate_emit_no_lang`
  both rc=0.
- Boards and both tree hashes are named in the landing commit.
