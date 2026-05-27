# HANDOFF 2026-05-27d (Opus 4.7) — ICN-Z-2b LANDED

**Goal:** GOAL-ICON-BB · **Rung:** ICN-Z-2b (leaf + BB_SEQ explicit ω-advance port slice)

## What landed

The one safely-sliceable piece of the ICN-Z 4-port AG zipper: the explicit `stmt[i].ω →
stmt[i+1].α` advance edge for the statement chain, plus a BB_SEQ port-follower in `bb_exec.c`.
Behaviour is byte-identical to baseline (verified by `git stash` diff) — this is an additive,
mode-2-safe wiring change that prepares the SEQ level for the full atomic pass.

### lower_icn.c — `lower_icn_proc_body`
Post-build pass after the back-to-front zipper: forces `stmt[i]->ω = stmt[i+1]` (next stmt's α)
for every intermediate statement, mirroring irgen `ir_a_ProcBody`/`ir_a_Compound` where BOTH the
success and failure of an intermediate stmt advance to the next stmt's start (compound advance, NOT
backtrack). Guarded by `icn_kind_owns_omega_operand(prev->t)` so a stmt that uses ω as an operand
slot (BB_IF else-branch) keeps its operand. Last stmt keeps ω==NULL — that NULL IS the proc terminal
(BB_SEQ falls off end → FAILDESCR). Added a forward declaration of `icn_kind_owns_omega_operand`
(defined later in the file).

### bb_exec.c — `case BB_SEQ`
Re-expressed the walk as a port-follower: advances via `st->ω` (the explicit edge stamped above);
for an ω-operand kind (BB_IF) advances via `st->γ` instead; stops when the port is NULL (proc
terminal). Replaces the purely-structural `st = st->γ` loop. BB_SEQ_EXPR (value-of-last / pump-last)
left untouched — it is a different construct.

## Gates (all held, non-regressing)
- smoke_icon 5/5
- smoke_prolog 5/5
- icon_all_rungs PASS=198 FAIL=34 XFAIL=36
- broker 23
- FACT grep 0

## Known limitation (NOT a regression — pre-existing, out of scope)
A multi-statement side-effect chain such as `write("a"); write("b")` still prints only the first
statement, in BOTH baseline and this build. Each `write(...)` lowers to a BB_CALL composite whose own
γ/ω are not yet port-followed; control does not hand back along the explicit ω edge to the next stmt.
This unblocks only with the **full atomic ICN-Z pass** (BB_CALL + the other operand-bearing
composites converted to 4-port threaded form, with `bb_exec.c` re-expressed as a pure port-follower).
CALL was explicitly excluded from Z-2b.

## Next session
Full atomic ICN-Z pass. Entry-point line map (68 `lower_icn_expr_node` sites + the `bb_exec.c`
composite cases) is in GOAL-ICON-BB.md immediately below the START-HERE block. Read each construct's
`ir_a_*` in `corpus/programs/icon/jcon-ref/irgen.icn` before wiring it. ONE pass, mode-2 green per
construct group; cannot half-zip (shared `bb_exec_node` driver recurses α/β as children for every
composite).
