# FINDING — RUNG 2 LANDS: MULTI-CLAUSE CHOICE, THE CLAUSE STEP ON β, AND γ-RETAIN

**hq_C, 2026-09-02, TRIO.** Row `prolog-rung-2-multi-clause-choice-and-the-clause-step-on-beta`.
Law: `RULES.md` § THE PROLOG REBUILD GATE. Sovereign: `ARCH-PROLOG-BYRD-BOX-TRANSLATION.md` § B.3, § A.1, § E row 2.
Tree: SCRIP `2fc5ce73` · corpus `100db9e3`. Start point SCRIP `7d0ed0f8` (rung 1).

## 1. What landed

**One graph per predicate, carrying every clause.** `lower_pl_pred_graph` refused `nc != 1`; it now builds a single
`IR_graph_t` whose `alt_entry[k] / alt_ret[k] / alt_redo[k] / alt_fail / n_alts` table names each clause's head-unify
entry, its success node, its rightmost resumable goal, and the one node every clause fails into. Params are shared,
`nlocals` is the max over clauses, `deterministic` is `nc == 1`.

**F.CUR holds an ADDRESS, not an index.** This is Jcon's `ir_MoveLabel` with the temporary promoted into the frame
(§ B.3 (ii)). The pinned prologue seeds `F.CUR` at `[H+8]` with the address of alternative 1; each alternative's
trampoline advances it to the next, or zeroes it on the last. **So there is no clause table and no index compare
chain anywhere** — the step is `mov rax,[H+8]; test; jz ω; jmp rax`. Indexing (rung 12, hq_P) cuts the same cursor
statically without changing this shape.

**The graph β IS the predicate box's Byrd redo port.** In order: `test r15,r15; jnz ω` (review C9 — SCRIP wires box
N+1's ω to box N's β, so without this a ball would be run as a redo); then consume `F.RES` at `[H+16]` **zeroing it as
it is read**, and jump it; else the clause step. The zero-on-read is what makes a clause that is redone and then fails
fall through to the step without any separate reset: a clause that succeeds again re-banks F.RES at its own success
trampoline.

**The clause step** (`<graph>_step`): unwind `r12` to `F.TRMARK` at `[H+0]` through the named rtx helper, re-seed
`F.G[*]` unbound over `[rbp+16+np*16, +nl*16)` (`rep stosb`, the LCL-SEED precedent — those cells are younger than the
choice, so the log never recorded them), drop stale `F.RES`, follow `F.CUR`.

**γ-RETAIN (the PZ-4 keystone).** A pinned graph's γ compares `r13` against `F.B0` at `[H+24]`. Equal: no live choice,
release exactly off the pin and hand `rax = 0`. Unequal: a choice younger than this frame is live and is carved
*below* it, so releasing would let the caller carve straight over a live choice point — keep the frame, hand
`rax` = our own base and `rdx` = our graph β, restore only the caller's pin. ω restores `r13 = F.B0` and always
releases. **The root graph never retains** (PZ-4 clause (f)): it is entered from the driver, whose wires `call exit`,
so no landing exists to consume the token.

**The call site** (`bb_call_proc_staged`, pinned arm): the γ landing banks `rax`/`rdx` into `FRQ(act)`/`FRQ(act+8)`
and pops the wire pair plus the PL-CALL-ALIGN pad **only on the released arm**; β tests `r15`, then re-enters the
retained frame with `mov rbp, token; jmp resume` and **deliberately does not move rsp** — it still sits below the
retained frame, exactly where the retaining γ left it, which is what keeps the retained frame safe from the caller's
own later calls. ω clears the token so a later β cannot re-enter a dead frame.

## 2. ⭐⭐ THE SHARED EPILOGUE READS ITS OWN γ WIRE THROUGH rsp, WHICH IS ONLY THE PIN WHILE NOTHING IS RETAINED

Measured, not reasoned: with the root graph routed to the pre-existing ICN-FR-2 zframe epilogue, all three witnesses
printed the RIGHT ANSWER and then SIGSEGV'd (rc=139). The arm spells its wire load `[rsp# + kt-24]`. Under the pin that
spelling has always resolved to the same address as `[rbp + kt-24]` **because rsp happened to equal rbp at γ** — true
for every graph that never retained anything. The instant a callee is retained, rsp sits below a live frame, the load
returns garbage, and `jmp rcx` leaves the program. Every read in the new pinned arms goes through the pin.

⭐ The general form: **a spelling that is only accidentally equivalent is indistinguishable from a correct one until
the accident stops holding** — and the failure arrived *after* the correct output, which is exactly the shape that
reads as "works, with a crash at the end" rather than "wrong address".

## 3. ⭐ TWO REACHABILITY WALKS, AND ONLY ONE OF THEM WAS THE ONE I FIXED

Clauses 1..N-1 are reached only through a trampoline, so no IR edge points at them. Seeding the emitter's RPO walk
made them EMIT; the program then aborted in `drive_value_slot` because `zls_build`'s **own** reachability worklist
(`zeta_storage.c`, seeded from `g->entry` alone) had granted them no slots. Two walks, one graph, one seed each. The
tell was that the fix moved the failure rather than removing it.

⭐ And a third, smaller one of the same family: `RPO_PUSH` silently drops `IR_SUCCEED` and `IR_FAIL`, so the first
design — a clause step riding on an `IR_FAIL` node and an F.RES bank riding on `IR_SUCCEED` — could never have fired.
Both became tail-emitted LABELS with the two ports redirected at resolution time. A clause whose body is empty or is
`true` has no node at all, so the trampoline target resolver chases SUCCEED chains and lands on the clause's own
success trampoline or the graph γ.

## 4. Instruments

`rt_pl_tr_unwind` (rtx) and `rt_pl_choice_open` (rtx) are the only writers rung 2 adds, both enrolled in
`QUAD_HELPER_RX` **by exact name, never as a shape** — emitted code still writes none of `r12`–`r15`.
`rt_pl_tr_unwind_sync` (C) unwinds to the mark and republishes the arena's GC top word in one entry.

## 5. Verdicts — pristine `-O0`, DONE-WHEN as written rc=0

| arm | reading |
|---|---|
| ladder `--to 2` | PASS 6/6 (3 witnesses × 2 modes) |
| BX-0 port trace `--to 2` | PASS(0), killswitch and perturbation OK on 6 |
| quad gate | PASS(0) — writes 50, enrolled 50, violations 0; rtx-writes 10, violations 0 |
| `nm -D` Prolog-only globals | 0 |
| `strip_comments.py --check` | 0 offenders |
| SNOBOL4 blocking board | m3 1679/1679 · m4 1679/1679 FAIL=0 SKIP=0 MISSING=0 |
| Icon smoke | 14/14 both modes |
| Icon STRICT rung suite | 264/6/1/27 of 298 — UNCHANGED |
| Icon MASTER board | m3 PASS=398 · m4 PASS=398, watermarks held |
| optbypass watermark | DEFAULT 0/1656 · SCRIP_OPT=0 192/1656 · SCRIP_ZD=0 304/1656 |
| SNOBOL4 control-arm `.s` | BYTE-IDENTICAL across the whole rung |

**RE-PROVED ON THE MERGED TREE (the rebase-baseline corollary).** The push rebased three scripts-only commits
under mine — including `test_prolog_ladder.sh` itself, the runner that grades me — so the verdicts above certify a
tree that no longer exists. Re-run whole on `2fc5ce73` after `make pristine`: **DONE-WHEN rc=0**, ladder 6/6, trace
PASS(0), SNOBOL4 1679/1679 both modes, quad-scan writes 53 enrolled 53 violations 0, optbypass DEFAULT 0/1656 ·
`SCRIP_OPT=0` 192/1656 · `SCRIP_ZD=0` 303/1656 (watermark ≤ 308; the first run read 304 — a watermark, not an
equality, and it moved the safe way).

## 6. REPORTED, not gating (RULES clause 4)

Prolog master board **56/383 both modes** (rung 0 read 6, rung 1 read 50, so rung 2 adds 6).
Prolog smoke 2/5 (arith, clause, recursion want rungs 6/7/10 — not this rung's).
Quad-gate population: **compiled witnesses 1 → 10** — multi-clause predicates are what let `probe_plz` and the
swi-bench / van Roy `nreverse` programs reach the emitter at all.

## 7. Witnesses beyond the ladder

`chain2b.pl` — `p(1). p(2). p(3). q(X) :- p(X). main :- q(X), write(X), nl, fail. main :- true.` — prints `1 2 3`
rc=0 in both modes. **This is backtracking INTO a callee's callee**, the defect the PZ-4 row measured at rc=139 in
both arms and carried unfixed through twenty passes. `nested.pl` and `deep.pl` refuse at rung 6 (`<`, `is`) — ceo's
lane, not a rung-2 result.

## 8. Trace refs

`--cut --to 2` (merging), 42 blocks kept. Exactly two blocks changed, censused block-by-block:
`ladder__rung00_hello` **byte-identical**; `ladder__rung01_fact_rule` differs by **one line** (the clause γ now routes
through its success trampoline, so the port target reads `main/0_ret0`); `ladder__rung02_choice_redo` replaced whole,
168 → 48 lines — the old block was the pre-cut global-mailbox machine's port sequence. Rungs 03–05 untouched.

## 9. What rung 3 starts from

The alternative table, the trampolines, the step and the graph β are all in place and language-blind
(`zframe_pinned_base` + `n_alts`). Inline disjunction (§ B.5) is the SAME shape one level down: `bb_disjunction` with
`F.RESd` in the enclosing frame. The retain/landing/β protocol does not change. ⚠ Open and named: a predicate whose
LAST clause is entered still leaves `r13 = H` (conservative — it retains one activation longer than necessary and
costs nothing but a frame); tightening that is rung 12's static cut, not a correctness debt.
