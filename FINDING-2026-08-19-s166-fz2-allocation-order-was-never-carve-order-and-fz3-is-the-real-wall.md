# FINDING s166 — FZ-2: `all[]` WAS NEVER CARVE ORDER, AND THE RECONCILED COUNT UNCOVERED THE REAL WALL (FZ-3)

**Seat:** local `/home/claude3`, Claude Opus 5, FENCE front. **Picked up:** s154 cursor NEXT-SEAT item 1 —
*"FZ-1's ONE UNRECONCILED NUMBER, before anything else on this front."*
**SCRIP** `ce4faef7` · **corpus** `bf828a11` · **.github** this commit.

## 1. THE COUNT IS RECONCILED — AND THE CAUSE WAS NEITHER HYPOTHESIS THE CURSOR OFFERED

s154 flagged that witness `S ? SPAN('a') FENCE SPAN('b') SPAN('c')` should bill **16** and billed **32**,
and named two candidates: the `all[]` index is not the dump's slot numbering, or a node sits between them
the dump does not show. Measured with the `(ni, j, op, zd_k)` instrument the cursor asked for
(`SCRIP_FZ_DIAG`, landed and kept), the answer is a third thing:

> **`g_emit_cfg->all[]` is ALLOCATION order, not carve order.** SNOBOL4 lowering is RIGHT-FIRST, so the
> two `MATCH_SPAN`s sitting immediately left of the fence in `all[]` (indices 25, 26) are `'b'` and `'c'`
> — **both carved AFTER the cut executes** — while `'a'`, the one genuinely dead cell, sits at index **28,
> to the RIGHT**, and was never counted.

γ-chase gives the true order `BEGIN → 28 → 27(fence) → 25 → 26 → END` against ascending indices 25,26,27,28.
`fence0_release_bytes()`'s own header comment asserted "all[] order — which is carve order, so the immediate
left neighbour owns the TOPMOST cell". That premise was false; every number it produced inherited the error.

**Why it mattered, from the emitted asm (ASM-DIFF-FIRST):** the carve holds exactly one releasable 16
(`n7_match_span_α: sub rsp,16`) standing on `MATCH_BEGIN`'s **live 24-byte** cell, so `add rsp,32` popped
16 bytes of the bracket's own storage. **That is the same over-release-into-live-storage class that cored
the floor whack** — reached by a different road, and quiet only because no witness read the clobbered half
before `MATCH_END` rebuilt it.

**The fix (FZ-2):** stop guessing at order and read the one that exists. The emitter lays cells down in the
RPO `nodes[]` order `zd_plan` consumes (its own ZK-2 note: *"nodes[] is execution order"*), and that order is
recovered from the graph by chasing γ. The walk now chases γ from the enclosing `MATCH_BEGIN` through
`zd_chase()` — **the same edge-following authority the planner's run walker uses** — then steps back down the
recovered prefix. Whitelist, `ASSIGN_SAVE` exclusion, LIFO contiguity and the bracket wall are unchanged.
One rule added: the control kinds the FENCE1 siblings already exclude by name now **stop** the walk even at
K=0, because a choice/suspension record with no cell of its own still owns spine below it. No new global,
no new `IR_t` field. Witness now bills 16 and the release exactly matches the carve.

## 2. ⛔ FZ-3 — THE REAL WALL, AND WHY ARMING BY DEFAULT IS STILL REFUSED

A correct count is **necessary and not sufficient**. The release is **invisible to the ζ depth planner**:
`zd_plan`/`zvo_resolve` stage every `[rsp+off]` in the statement at a depth model computed **without** this
`add rsp,K`, so the instant K>0 every static offset to the RIGHT of the cut is stale by exactly K.

**Proof, one diff.** Armed vs disarmed on `corpus/probe/fz/fz3_capture_across_fence` case D differs in
**ONLY the two `add rsp,16` lines** — every staged offset is byte-identical while RSP moved.

**Witness.** `S ? (SPAN('a') FENCE SPAN('b')) . W`, preceded by **any** other fenced statement, prints
`abbb` against the oracle's `aaabbb` (the group's COND reads its SAVE cursor back at a stale offset), in
**both** modes. Alone it passes; the shape needs a predecessor. fz1/fz2 pass only because nothing right of
their cuts reads a cell at a staged offset.

**The rung this names:** thread the release into the depth model (`zd_plan`'s staging) so offsets right of
the cut are computed at the post-release depth. That is exactly the *"PLANNER fact … not a one-liner here"*
`bb_match_fence0.cpp` already predicted. **Until it lands: count right, arm wrong, DEFAULT OFF is the only
honest position.**

## 3. ⛔ THE CORPUS PROVIDES ZERO COVERAGE FOR THIS ARM — s154's CLEAN BOARD WAS NOT EVIDENCE OF SAFETY

Armed ≡ disarmed on **all 510** programs (`corpus/crosscheck` + `corpus/programs/snobol4`): the arm emits
**no release anywhere in the corpus**. Every corpus fence is `FENCE(P)`, first-position, or inside an
ARBNO/blob body with no bracket on its forward chain (treebank's two bill 0 for that reason — the same
answer as before, now for a stated reason instead of by accident). So "armed crosscheck identical to
disarmed" — true at s154 and true again here — **means no coverage, not safety.** The entire safety case
for this feature rests on minted witnesses, which is why the three in `corpus/probe/fz/` exist.

## 4. MEASUREMENTS (pristine builds both sides, HQ-27 law; baseline in its own worktree at `8fa550e4`)

| check | result |
|---|---|
| disarmed inertness, patched vs baseline **binary** | 510 programs, 509 identical + `unary_not.sno` = **0 attributable movers** |
| `unary_not.sno` | re-confirmed **pre-existing** nondeterminism: 3 md5s from one binary, one arm |
| armed vs disarmed, same binary | 510 programs, **0 movers** (zero corpus coverage, §3) |
| crosscheck | m3 **307/10** · m4 **306/10** · **DIVERGE=0**, FAIL sets identical in both arms; re-proven after rebase |
| workload family (BM-4, 15) | m3 8/7, m4 6/9 — FAIL sets **identical** in both arms |
| `treebank-match-fence` (the program the floor whack cored) | **check: 100155** both arms, both modes, still in 256 KB |
| witnesses fz1/fz2/fz3 | oracle-identical, both modes, on the shipped default |
| `scripts/test_gate_fz_release.sh` | **GREEN** here, **RED (exit 1)** on the pre-fix baseline, naming every over-release site |

The gate pins **no golden**: LOCK 2 re-derives each fence's releasable carve **from the emitted asm** by
following the α-chain and asserts the release never exceeds it. It was proven non-vacuous by running it
against the unfixed baseline before it was trusted (the first draft of it passed vacuously — it parsed only
label lines while boxes span many, so the chain never started; recorded here because a gate that cannot go
red is worse than no gate).

## 5. ⛔ TWO THINGS FOUND OUTSIDE THIS RUNG — NOT ACTED ON, LON'S CALL

1. **THE BOTH-MEDIUM GATE IS VACUOUS — ITS PATH NO LONGER EXISTS.** `RULES.md` line 19 enforces
   *"zero `MEDIUM_*` in any `bb_*.cpp`"* with `grep -rn 'MEDIUM_' src/emitter/BB_templates/`. **That
   directory does not exist** — templates live in `src/templates/`. Against the real path: **195**
   `MEDIUM_*` occurrences in `src/templates/`, **29** in `bb_*.cpp`, including genuine code gating
   (`bb_call_bool.cpp:34` `if (MEDIUM_BINARY)` / `:43` `if (MEDIUM_TEXT)`), across at least
   `bb_call_bool`, `bb_call_write_slot`, `bb_main`, `bb_key_gen`, `bb_define`, `bb_scan_stmt`,
   `bb_call_proc_staged`. Several gate scripts (`test_gate_emit_no_ir_mutation.sh`,
   `test_gate_no_handencoded_bytes.sh`, `test_gate_bb_emit_blind.sh`, `test_gate_em_template_matrix.sh`,
   `test_gate_icn_no_stack.sh`) also glob `$EMIT/BB_templates/*.cpp` and so scan **nothing**. This is a
   standing ABSOLUTE RULE whose enforcement is dead; it is a rung of its own, not a drive-by fix.
2. **THE TRACKED `.s` ARTIFACTS ARE STALE, AND NOT FROM THIS CHANGE.** Disarmed output differs from the
   checked-in `.s` on **283** of 340 comparable programs — e.g. `crosscheck/rungW02/W02_seq_basic.s`
   carries a `__gva_names` rodata section current output does not emit. This change is provably inert
   disarmed (§4), so the drift predates it. RULES step 4 would have this session run
   `util_regen_*_s_artifacts.sh`, but doing so would fold ~283 unrelated artifact updates into a fence
   commit and destroy its attributability. **Deliberately not run — flagged for Lon's ruling.**
