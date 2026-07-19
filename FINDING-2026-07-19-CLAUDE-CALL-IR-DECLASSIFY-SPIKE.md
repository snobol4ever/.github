# FINDING 2026-07-19 (Claude) — CALL-IR DECLASSIFY: the spike FIX-3 was waiting on

Origin: Lon directive this session — "break up the two IR_*CALL* opcodes into a couple/few sets or IR's to simplify." This is the fresh design spike `GOAL-BB-FIXUP-A-to-Z.md` (run #7 note) says FIX-3 needs "against the LIVE kind set before execution." Written against HEAD `a0d0c763`.

## MEASURED — the live call-IR reality (not the stale run-#7 prose)
- **8 call kinds already exist** (`IR.h:26-33`): `IR_CALL, IR_CALL_BUILTIN, _BUILTIN_GEN, _BUILTIN_ICON, _BUILTIN_SNOBOL4, _BUILTIN_PROLOG, _PROC_STAGED, _VALUE`; plus `IR_PROC_GEN` (59), `IR_PROC_VALUE`. `ir_is_call_kind` (196) groups them **by explicit list, not a numeric range**; `ir_norm_call_kind` (199) collapses any → `IR_CALL`.
- The blocker is NOT too few kinds. It is `bb_call_route_classify` (`emit.cpp:649-673`): a 24-line **runtime** classifier mapping (kind + live facts) → 14 `CALL_ROUTE_*`. Facts it re-derives at EMIT time: `rt_builtin_is_known/is_generator`, `rt_proc_is_registered/is_generator`, `icn_builtin_is_known/is_generator`, `pl_builtin_is_known`, `op_dval==2.0/3.0` (magic stage sentinel), `op_write_route` (1-5), `strcmp(fn,"__rk_bool")`, `bb_slot_get(a0)`.
- **Two FACT-RULE breaches live in that function:** it branches on per-language builtin registries (`icn_*`, `pl_*`) *inside the emitter* (language-blind FACT RULE + `test_gate_emit_no_lang.sh`), and it special-cases a runtime function by string name (`__rk_bool`).

## ROOT CAUSE (sharper than "split the opcodes")
The **generic `IR_CALL` kind is the overloaded one.** A lowerer that emits bare `IR_CALL` is punting classification to the emitter, which then does registry lookups — LOWER's job in the EMITTER (GZ#5). Fix = push classification UPSTREAM so the kind carries the full decision; the classifier degenerates to kind→route, then deletes.

Two **orthogonal axes are fused** in the one classifier and must be separated:
- **AXIS A — dispatch shape:** BYNAME | BYNAME_GEN | FN | PROC_STAGED | PROC_GEN | VALUE | RK_BOOL. Belongs in the IR KIND (decidable at lower time — `icn_builtin_is_generator(fn)` etc. are all knowable when the lowerer builds the node).
- **AXIS B — result routing:** `op_write_route` → WRITE_{SLOT,BINOP,LEGACY,EMPTY}. A SEPARATE concern (where the result lands). Must become an explicit IR field on the call node, NOT a fused route value. `bb_call_write_slot` then reads it structurally.

## PROPOSED DECOMPOSITION
1. Introduce **`IR_CALL_BYNAME`** = the deferred by-name case that bare `IR_CALL` silently stands for at emit today. **APPEND at the END of the whole `IR_e` enum** (never mid-list) so no existing enumerator renumbers. Add to `ir_is_call_kind`. ✅ PREREQ **MEASURED CLEAN this session** (grep @ `a0d0c763`): no `op >= IR_CALL && op <= …` contiguous-range assumption anywhere; no op-as-array-index / jump table keyed on op value in emitter/lower/contracts; no raw op-int `fwrite/fread` serialization; dispatch is `switch`-on-op (6 in emit.cpp) which tolerates appended enumerators. ⇒ append is renumbering-safe; only residual S1 risk is a timing collision with a parallel `IR.h` edit, not correctness.
2. **LOWER assigns the full Axis-A kind** — lowerers stop emitting bare `IR_CALL` where runtime classification would be needed; emit `_BYNAME`/`_BYNAME_GEN`/`_BUILTIN(_GEN)`/`_PROC_STAGED`/`_VALUE` directly. Generator-ness resolved at lower (it is knowable there), so the `rt_*_is_generator` branches leave the emitter.
3. **Lift Axis B out of the kind:** `op_write_route` becomes an explicit field set by lower; `bb_call_write_slot` reads the field. WRITE_* leaves the classifier.
4. **Kill the `__rk_bool` name-leak:** lower_raku emits a dedicated kind (or reuses one) for the raku-bool pattern; no `strcmp` on function names in the emitter.
5. Classifier is now **kind-only** → inline into the existing op-keyed dispatch (`emit.cpp:851/1079` style), **delete `bb_call_route_classify`**. `bb_call` (168) and `bb_call_proc_staged` (144) shed their multi-route internal branching and collapse.

## MIGRATION ORDER — each step BYTE-IDENTICAL-provable, one file per commit
Behavior is preserved at every step (same program → same route → same asm), so the 36-program A/B `.s`-delta must stay **EMPTY** through S1–S5; S6 is the payoff, everything before it is groundwork that keeps output identical.
- **S1** `IR.h`: append `IR_CALL_BYNAME`, extend `ir_is_call_kind`. [HOT — coordinate with IR-REDUCE session]
- **S2** `lower_*.c`: emit `IR_CALL_BYNAME` for the by-name-deferred case; classifier lines 670-671 go unreachable for those. [HOT]
- **S3** lift generator-ness to lower (`_GEN` kinds); delete `rt_*_is_generator` + `icn_/pl_*` branches from classifier → **language-blind gate now passes.**
- **S4** `op_write_route` → explicit IR field; `bb_call_write_slot` reads it; delete WRITE_* from classifier.
- **S5** kill `__rk_bool` strcmp (lower_raku kind).
- **S6** classifier kind-only → inline + delete; `bb_call`/`bb_call_proc_staged` collapse. Re-audit: expect large GRAND drop on both.

## RECONCILIATION with IR-REDUCE (224→33)
Net effect is SIMPLIFICATION despite +1 kind (`IR_CALL_BYNAME`): it DELETES a 24-line runtime dispatch switch, removes two FACT-RULE breaches, and collapses the two largest BB-FIXUP violators. The reduction north star targets redundant/dead opcodes and *dispatch surface*; this removes dispatch surface while making one hidden case explicit. Consistent.

## COLLISION NOTE
S1–S2 touch `IR.h` + `lower_*.c`; S3/S6 touch `emit.cpp` — the same hot files the R12/ZC_FRAME and IR-REDUCE sessions edit, under one-file-per-commit-to-main (no branches). Execute in a quiet window or coordinate; `git pull --rebase` at each commit; `handoff_status.sh` is ground truth.

## NOT DONE THIS SESSION / WHY
Spike only — no spine edits. Rationale: multi-file semantics-touching change on hot shared files with ~40% budget remaining; the goal file itself mandates spike-before-execution here. First executable slice = **S1** (append the kind, after the serialization grep-check). Ready to execute on Lon's word.
