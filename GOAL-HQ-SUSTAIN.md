# GOAL-HQ-SUSTAIN.md — HQ-SUSTAIN (hq_S), opened 2026-09-05 15:02 CDT

## THE MANDATE
Lon 2026-09-05, in-chat to ceo, verbatim: *"So how many HQ's and how many Fleet workers should we have? 8 HQ's?"* · *"I just created S, I, and R root folders."* — the ceo's recommendation that day (GOAL-CEO CEO-293): eight Opus HQs, each owning ONE cure surface small enough to drain between landings, over twelve Sonnet walkers, because the measured shortage was cure capacity, not witness supply (one cure per HQ-hour against a walker output several times that, and five engine classes queued on one HQ that had not read its mail in ninety minutes).

## THE LANE (MASTER-PLAN § THE LANES, eight HQs)
hq_S owns the SNOBOL4 RUNTIME: builtins, I/O and file association, keywords, error handling and limits (SETEXIT, &ERRLIMIT, &STLIMIT), tracing, the csnobol4 suite (60/119 at opening) and the SPITBOL testpgms — every SNOBOL4 class whose cure lives in `src/runtime/{builtins,rt,core}`, `rtx_match.s` or `rtx_str.s`; the parser, the lowerer and the pattern boxes stay hq_P's. Its seats under THE 12-SEAT CUT: 03–04.

## LAWS THAT BIND EVERY hq_S LANDING (compact; RULES.md is the parent)
- An HQ CURES; a seat measures. You never run a suite, a board or `make test` by hand — a seat runs it and files the class row with a minimal witness cut from the oracle; you cure it in rung order on that witness (Lon 2026-09-05 to hq_T, MASTER-PLAN § WHO FIXES WHAT).
- A shared-node change (a box two or more frontends lower to, `x86_asm.h`, the emitter, runtime core/rt) is AUTHORED by the HQ whose language exposed the class and CO-SIGNED by hq_U, which grades the other frontends' boards and the demo set (RULES § THE DEMO-SET CONTROL ARM) before the push. hq_U reviews; it does not queue.
- Every landing names its control arms with tree hashes; every suite run rewrites its SCORE.md row through `util_score_row.py`; THERE IS NO XFAIL; OUR FILES ARE LF; no pristine build; a multi-line DONE-WHEN is run whole by hand until hq_T's bus fix lands.
- Drain your inbox at every prompt boundary: a ruling unread is not in effect.

## SESSION SETUP (every session)
1. `git -C SCRIP fetch origin && git -C SCRIP merge --ff-only origin/main`, same for `corpus` and `.github`; `cd SCRIP && make`.
2. `bash scripts/s4e_msg.sh check` — read, act or reply, `clear`.
3. Read this file's LIVE CURSOR, then `SCORE.md` § THE SEPTEMBER 10 GRID for your lane's cells, then assign each of your seats its first row (`s4e_msg.sh assign seatNN <topic>`, a runnable DONE-WHEN proven red once).

## LIVE CURSOR

**2026-09-06 ~14:2x CDT hq_S — SITTING LEDGER (FLEET-12).**

**CURED, ON BRANCH, NOT MERGED:** CEO-334d (the AIS class). Branch `hq_S/ais-sig-disp-dollar-marker`,
SCRIP `09cd8a3b9`, one file, +2/-14 in `bb_call_proc_staged.cpp`. `bcps_sig_disp` parsed `[rsp#` and is fed
`FRQB(slot,0)`, which `x86_zop` **always** renders as `[rsp$` — so the signature arm had **never fired once**
for any argument-bearing call site, and those sites fell through silently to the SCC `open_slim` convention
while the callee's prologue was the role-4 SIG shim that dereferences `rcx` as a signature block. Cure:
delete the duplicate parser, teach the survivor `$`, delegate. `FINDING-2026-09-06-hq_S-the-signature-arm-declined-100-percent-of-inputs-because-its-parser-was-fed-a-spelling-it-could-not-read.md`.

**MEASURED (m3 + m4, vs `sbl -bf`, incremental `make`, `RT_OPT=-O0`):** ceo's witness `v21` rc=139 both modes
→ rc=0 MATCH both modes; `v21b` (twin, no formal) and `v22` (same call at top level) MATCH before and after
as controls. `v21b` survives only because `nf4=0` means the shim never dereferences the bad `rcx` — **the
defect was present and invisible there.**

⛔ **THE BRIEF'S TWO NAMED ARMS DO NOT WITNESS THE CLASS, and this is the correction of the sitting.**
`ENDING` was **already green before the cure** (A/B'd on a rebuilt pre-cure binary, 22 lines MATCH both
sides). `WANG` is still rc=139, has **zero** declining sites, and faults in `n33_match_defer_bx+36` with
`rcx=0` — a **match-defer** box, not a call box. Same package, same rc, different class; handed back
unclaimed. ⭐ Both were one step from entering a receipt as closures off a shared package name and a shared
rc=139; the pre-cure rebuild was the only arm that stopped it.

⛔ **RESIDUAL, DELIBERATELY NOT CURED:** `sigok` can still be 0 legitimately (`[rbp + N]` operands, `fc_hit`,
`nargs>29`, `dhi != dlo+8`) and **every one still falls through to `open_slim` against a SIG-shim callee —
still a wrong program, just rarely.** By this lane's own loud-decline rule that should `x86_bomb`. Not done
without first counting the live sites that take it. **That is the next row.**

**GATE, DELEGATED (an HQ never runs a board by hand):** seat03 → `board-arm-for-hq_S-ais-sig-disp-branch`,
a **DELTA** arm — origin/main AND branch, both modes, printed denominators, reporting the NAMED
set-difference outside CEO-335's inherited `demo_*` set. An absolute FAIL count cannot answer this: the cure
**enables** a path that never fired, so the blast radius is call sites elsewhere that switch convention.

**CEO-335 taken:** the `user_function_*` inheritance is withdrawn, my branch touches that neighbourhood, and
the delta arm is what makes a new `user_function_*` red attributable to me by construction rather than by
argument. Inherited set named verbatim in the seat brief: `demo_json`, `demo_calculator-1`,
`demo_calculator-2`, `demo_treebank` + `_match` / `_match_fence` variants (hq_R's, `285f8fb12`; nobody
reverts it).

**ROUTED OUT OF LANE:** seat04's BAL/ARB/REM/FAIL/SUCCEED/ABORT silently-uncallable finding is **hq_P's** —
the cure is in `snobol4.y` plus three lowering consumers, i.e. the frontend, not the runtime. Concurred on
the lane, not claimed.

**NEXT SEAT STARTS HERE:** read seat03's delta before merging the branch. If the set-difference is empty
outside the inherited `demo_*` set, merge and close CEO-334d. Then the loud-decline row above, then WANG as
a fresh match-defer row (it is NOT part of CEO-334d).

**2026-09-05 15:02 CDT ceo — OPENED, NOT YET RUNNING.** FIRST ROWS: SNOBOL4 ladder rungs 25–27, 29–32 (predicates, string functions, real math, I/O, system, SORT, error handling) once seat09 declares them red; the csnobol4 suite by class; the SPITBOL testpgms. Lon starts the session; the ceo re-lanes the seats at the FLEET-12 flip.

**2026-09-05 15:41 CDT hq_S — LEDGER, CLOSED WITHOUT RUNNING (MODE flipped to CEO at 15:15 before this seat was started).** WHAT LANDED: nothing — hq_S never held a row. WHAT IS LEFT: the entire FIRST ROWS list above, untouched and unassigned; no seat was assigned (`s4e_msg.sh assign` never run), no suite or board was run by this seat, so no SCORE.md row is owed or stale on its account. THE WITNESS (measured, not remembered, at the clock above): zero claims in `/home/resources/postoffice/claims/` name hq_S; `QUEUE.tsv` and `BOARD.md` carry zero hq_S rows; all three repos are clean and level with origin — SCRIP `b812fb6d1`, corpus `8972babeb`, .github `d30d29baa` (`git status --porcelain` empty, `origin/main..HEAD` empty, `merge --ff-only` = Already up to date, in each). Nothing stayed only in this checkout. NEXT SEAT: the cursor block above is unchanged and still correct — start from it, not from this line.


**2026-09-05 ~19:1x CDT hq_S — SITTING LEDGER (opened under OCTET, ran through the FLEET-12 flip at 18:27).**

**LANDED (on main, by hq_U's co-sign):** change (1) of the nqueens cure — `bb_match_len.cpp` reads its
dynamic operand through `XSAQ(8)` — as SCRIP `b6c17b331`.

**HELD FOR CO-SIGN (pushed, not merged):** branch `hq_S/nqueens-change2-arbno-body-consumer` at
`c3f480472`, merged up to current main (merge commit — no rebase, no force). Net diff vs main is exactly
three files: `emit.cpp` (`arbno_body_member`) + `bb_match_pos.cpp` + `bb_match_rpos.cpp`. Arm 3 is hq_U's
to board; **I have not boarded it and am not claiming it.**

**THE FINDING OF THE SITTING:** `xop_frame_member` finds a consumer by chasing the **γ chain**. A SNOBOL4
ARBNO is shortest-first — α proceeds to the FOLLOWER, the BODY is reachable only through β — and `IR_t`
carries only γ and ω, so **there is no β edge in the IR to walk**. A consumer inside an ARBNO body is never
reached, and the allocator returns 0 for *not found* in the same spelling it uses for *not there*. That
splits six identical producers exactly 3-and-3 in nqueens, which is why the split looked arbitrary for two
days. Cure: grant the slot when the walk fails to reach the consumer **and** the consumer is positively
located inside an ARBNO body extent. `FINDING-2026-09-05-hq_S-the-arbno-body-consumer-is-unreachable-on-the-gamma-chain-...md`.

**MEASURED:** nqueens BAD m3 20/20 → 0/20, m4 20/20 → 0/20 (argv-length sweep, output-vs-ref). Control arm,
SNOBOL4 broad board: m3 PASS=1835 FAIL=1 · m4 PASS=1835 FAIL=1 SKIP=0 of 1836 · ast 28/28 — byte-identical
to hq_U's arm A on clean main. Seven witnesses minted and A/B'd against clean main: **five red on main in
both modes, two green (recorded as control arms, not counted as closures).**

⛔⭐ **THE NUMBER THIS LANE SHOULD CARRY FORWARD: across the five red witnesses there are ten readings on
main, and EIGHT EXIT rc=0 PRINTING THE WRONG ANSWER. Only two crash.** An rc predicate would have called
eight of ten a pass. The row was named `-sigsegv` and every pass on it for two days, mine included, graded
the last consequence. **On this lane's defects, rc is usually the wrong verdict and it fails in the
flattering direction.** Both seat briefs and every row minted this sitting carry it.

**SEATS (FLEET-12):** seat03 → `snobol4-testpgms-test1-traps-29-runtime-errors-...` (censused 22/29 green,
7 red, all invisible to rc — confirmed the predicate directly); seat04 → `snobol4-csnobol4-ord-labelcode-maxint-...`.

**ROWS MINTED (rank 1, hq_S):** `snobol4-fence-body-consumer-never-earns-a-frame-slot-same-gamma-reach-limit-as-arbno`
(first act is a witness proven red, **not** a patch — and if none can be built red, the row closes rather
than widening the rule on a hunch); `snobol4-workspace-island-exhausted-core-dumps-where-the-oracle-prints-3-permutations`
(hq_P's handover; **do not cure by raising the workspace size**).
**PLACEHOLDER CLEARED:** `input-open-failure-not-signaled` now has a runnable criterion, proven red — and
its shape is corrected: **there is no hang**, SCRIP prints zero bytes at rc=0 where the oracle raises
ERROR 116. The row got *quieter*, not fixed. Its two suite-timeout attributions are marked UNSUPPORTED.

⛔ **FOUR CORRECTIONS AGAINST MY OWN WORK, kept because the pattern is the lesson:**
1. **hq_U inverted my mechanism generalisation.** I said the coerce boxes sit outside any match region
   because in `TEST = pattern` the pattern is BUILT, not matched. Measured: the variable form is DEFERRED
   and therefore DOES get a slot; the INLINE form is the unreachable one. The window is whether a
   `MATCH_BEGIN` precedes the operand **in emission order**. ⭐ Neither lane caught it because **nqueens
   exercises only one of the two shapes, and a generalisation drawn from a sample of one reads exactly like
   a mechanism.** Marked dead in place on the baton, not deleted.
2. **I asserted a witness location I never grepped.** Told seat03 the RETURN-at-level-zero witness was one
   of test1.spt's 29; every RETURN in that file is inside a DEFINE. The bug was real; the sentence about
   where it lived was invented.
3. **I minted a duplicate** of a row seat03 had already filed, minutes apart, neither mint visible to the
   other. Mine SUPERSEDED, content folded into theirs. Fix is one command — grep QUEUE.tsv for the slug's
   distinctive noun before minting.
4. **I read a grep count instead of `make`'s exit code** after the merge, saw every witness go red, and for
   a minute believed the cure had died. It was a stale binary. The trap I spent all day warning others
   about, in my own hands, inside an hour.

**NEXT SEAT STARTS HERE:** wait on hq_U's arm-3 verdict, then merge the branch and close the nqueens row
with its re-cut DONE-WHEN (`graded=16 bad=0` on the branch today). Then the FENCE-body row (witness first),
the WSI row, and seat03's cascade ablation — if stmt137 resyncs 248/249/252/253 and 258/259, seven reds
collapse to one row and the cure surface collapses with them.
