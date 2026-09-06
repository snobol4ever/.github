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

**2026-09-06 ~18:0x CDT hq_S — SITTING LEDGER (OCTET).** Supersedes the blocks below it.

**BRANCH HYGIENE, FIRST ACT.** `hq_S/ais-sig-disp-dollar-marker` **had already been merged into main by
another hand** — both commits are in (`6f3852fd1` the cure, `e68e35fd4` the SIG_DIAG instrument), and the
rebase reported them as skipped cherry-picks, which is what "already landed" looks like from the branch
side. Item (1) of the previous cursor is therefore CLOSED, not abandoned. The other four hq_S branches were
all 09-05 vintage and are RETIRED under OCTET's one-sitting rule to tags on origin
(`retired/{nqueens-change1-bb-match-len-xsaq-only,nqueens-change2-arbno-body-consumer,nqueens-dynamic-len-operand-partial-cure,staged-call-signature-rcx}-2026-09-06`),
tips readable, never mergeable. ⛔ The five REMOTE branches still exist: deleting them was refused by this
root's sandbox classifier, so a hand with push-delete rights must do it. The tags carry the tips regardless.

**FLIP: `csnobol4/float2`, GREEN BOTH MODES.** SCRIP `e1c74e259`, one file, +9 lines in
`src/runtime/core/core.c`. `_HOST_` implemented selectors 0-4 (the Catspaw set) and closed with a bare
`return NULVCL` that swallowed the whole CSNOBOL4 2xxx range; `HOST_REAL_BITS` is 2301, so `EQ(BITS,64)`
failed and the program silently took its 32-bit branch. **`CONVERT` was the obvious suspect and was
innocent** — SCRIP already emits `0.333333333333333`. Cured eight selectors as facts about SCRIP's own
build (`sizeof`/`CHAR_BIT`, never constants copied off the oracle): 2300/2301/2302/2303/2304/2306 plus
2212 `/` and 2213 `:`. **2305 SPEC_BITS deliberately left unanswered** — it reports the SIL specifier width
and SCRIP has no specifier type; the oracle's 256 is a true fact about csnobol4 and would be a false one
about us.

⭐ **WHY IT HID, AND IT IS THE SAME SHAPE AS THIS SEAT'S OTHER FINDING TODAY.** Measured: the live oracle
returns an empty STRING for `HOST(9999)` too — it does **not** fail on an unknown selector. So the null
fallback was upstream-correct, and an unimplemented selector was indistinguishable from one that is
implemented and legitimately empty. **A fallback that returns a legal value carries no hit rate**, exactly
as the signature arm's decline did this morning. `FINDING-2026-09-06-hq_S-an-unimplemented-host-selector-returns-the-same-empty-string-as-a-legitimately-empty-one-so-the-gap-reads-as-data.md`.

**BOARDS (own tree, own incremental `make`, `RT_OPT=-O0`, LANDED as SCRIP `e1c74e259`).** csnobol4 suite,
runner's own line: `CSNOBOL4_SUITE_BOARD total=120 m3_PASS=72 m3_FAIL=18 m3_REJECT=30 m3_CRASH=0 · m4_PASS=72
m4_FAIL=18 m4_REJECT=30 m4_CRASH=0` against the previous row's **71/120** — **+1, the flip, no regressions**,
`float2` absent from both RED lists. ⭐ **The FAIL 17→18 with CRASH 1→0 across the rebase is NOT a
regression and the check that proves it is the name list, not the counts:** the RED-M3 name lists are
byte-identical pre- and post-rebase, so one program was reclassified crash→fail by origin's new commits.
Counts moved, membership did not — and a count comparison alone would have read as a new red.
SNOBOL4 master control arm, runner's own line on `e8a6d2a65`: `mode-3 (--run): PASS=1857 FAIL=1` /
`mode-4 (--compile): PASS=1857 FAIL=1 SKIP=0 (1858 total)`, the single red NAMED by targeted rerun as
`user_function_keyword_branch_3` — hq_P's rank-0 standing red, so no worse than a clean tree (CEO-365).
⛔ **TWO DENOMINATORS, TWO POPULATIONS, NOT A DISAGREEMENT** (coo hit this within the hour): the runner
prints `PASS=1857 FAIL=1` over 1858, while `corpus_suite_harness.py`'s `SUITE_BOARD` prints `m3_pass=1834`
of 1862 — the 27 xfail land in neither PASS nor FAIL. Both are the same run.
Per this lane's own rule, **both graders were shown able to fail in the same sitting**, before AND after the
rebase: the identical m3 and m4 pipelines run against `label.sno` reported RED each time.

⛔⭐ **TWO INSTRUMENT SELF-INFLICTIONS THIS SITTING, BOTH THE SAME DEFECT, ONE OF THEM ALREADY IN THIS
CURSOR.** (1) `pkill -f corpus_suite_harness` **matched its own command line** and killed the shell running
it (rc=144), so a rebase I believed had run silently had not. This trap is recorded two paragraphs down
from a previous sitting — filing a lesson is not the same as holding it. The guard is a bracket:
`pgrep -f 'corpus_suite[_]harness'`. (2) Naming the master red by `grep -iE 'FAIL'` over the harness output
returned EMPTY, which reads as "no failures"; the harness had in fact **REFUSED with rc=2** for want of
`--by-modes-column` (without it, 28 `modes=ast` entries are executed and diffed against AST dumps,
manufacturing meaningless reds). **Capture-then-test — `out=$(cmd 2>&1); rc=$?` — is what surfaced it.**
A refusal swallowed by a grep is indistinguishable from a clean board.

⛔⭐ **RETRACTED, SAME SITTING: I SAID `csnobol4/pow` WAS A TRAP AND NOT A DEFECT. IT WAS NEITHER.** I
graded it **without `--compat=csnobol4`**, the flag this suite actually runs under
(`test_snobol4_csnobol4_suite.sh:142`). Under the flag SCRIP prints `9^-1 = 0` and `pow` PASSES both modes;
it is in neither RED list today. It **was** a real defect and **was already cured** at SCRIP `e7c45454e`
(the fourth compat switch, `SCRIP_IPOW_CSNOBOL4`). ⭐ **How I got there is the lesson: I ran a
narrower-configured instrument, then reached for a SECOND instrument — the SPITBOL oracle — that shares the
same blind spot, and read its agreement as confirmation. It agreed BECAUSE I had disabled the mode under
test.** Corroboration only corroborates when the failure modes are independent. This is the identical defect
I spent the sitting documenting in other people's code.

⛔ **THE REAL HAZARD, MEASURED: THE POOL SNAPSHOT CARRIES PHANTOM REDS.**
`.github/probes/package-red-pools-2026-09-06.tsv` lists **53** csnobol4 reds; today's board says **48**. The
five-row difference is `convert`, `err`, `float2`, `pow`, `rewind1` — all green or ungradable now (`err`
`7338727e0`, `convert` `00b62a274`, `pow` `e7c45454e`, `float2` this landing, `rewind1` PARKED_NO_REGEN by
hq_P ruling). **Minting flip rows off that snapshot burns time on programs that are already green.** Grade
the program yourself, under the suite's own flags, before minting the row.

⛔⭐⭐ **NAMED AND SIZED THIS SITTING, ASKED UP TO THE ceo: THE CSNOBOL4 CASE-FOLDING CLASS.** csnobol4
folds identifiers AND keywords case-insensitively at COMPILE time and is case-insensitive **by default**.
⭐ **The decisive measurement, because the obvious hypothesis is wrong:** in the oracle, `foo` reads `FOO`'s
value **before `&CASE = 1` is ever executed**, and still does after `&CASE = 0`. So `&CASE` is NOT the
switch it appears to be, and a cure aimed at `&CASE` — which is exactly where `label.sno` points you —
would be aimed at the wrong thing.
**Confirmed members by reading each diff, not by heuristic:** `case1` (folded variable reads) · `trace1`
(`TRACE` by string: the oracle folds `foo`/`FOO` into one variable and traces all four assignments, we
trace two) · `label` (`LABEL('bar')` finds `BAR`) · `func2` (lowercase `end` reads to us as "missing END
statement", plus a `fOo()` call) · **half of `setexit7`**. The runner header independently documents the
same lowercase-`end` class for the `random` and `time` module tests.
⛔ **NO TRUSTWORTHY COUNT EXISTS AND I DID NOT INVENT ONE.** A source heuristic returns **16 of 48** reds
if string literals count and **4 of 48** if they do not, and neither bound is honest: the operative
identifier is sometimes inside a string (`LABEL('bar')`, `TRACE('foo')`) and sometimes prose that merely
looks like one. The only reliable census is the red set against a folding-enabled build, which does not
exist. **Confirmed floor: 5 programs.**
**Cure shape, precedented — a fifth compat switch `SCRIP_FOLD_CSNOBOL4`, live only under
`--compat=csnobol4`**, exactly as `SCRIP_IPOW_CSNOBOL4` and `SCRIP_ERRNUM_CSNOBOL4` already work; the
default SPITBOL dialect stays case-sensitive by construction, which is the property that makes those
switches safe. Ownership is asked up because it lands in three places and only the third is mine: keyword
lexing and identifier resolution are hq_P's frontend, runtime lookup by string is hq_S.

⭐ **`setexit7` IS TWO BUGS WEARING ONE DIFF, and that is why it is not the cheap flip it looks like.**
Line 1 is the fold class above. Line 2 is mine and local: an undefined goto target raises SCRIP's 38
("transfer to undefined label: foo") where csnobol4 raises **24 "Undefined or erroneous goto"** — one row
in `core_err_compat_map` (`core.c`), the table `7338727e0` already built. Curing only line 2 does NOT flip
the program, so it is not a flip row on its own. Related, measured: even with the DEFINE case-matched by
hand, a call to a function with no entry label raises SCRIP 286 where csnobol4 FAILS the call and the
goto-eval failure then reads 19 — a semantic difference, not a remap.

**NEXT, in OCTET order (one bug at a time):** (1) `csnobol4/label` — `&CASE = 1` does not reach `LABEL()`'s
lookup, so a case-folded label misses; `_LABEL_` is `core.c:2060`, a builtin in this lane, already probed
red in both modes and it is the can-fail demo above. (2) WANG, on the rank-1 by-name-goto row — zero
`sigok=0` sites, faults in `n33_match_defer_bx` with `rcx=0`, a match-defer box, NOT that class.
(3) the csnobol4 REJECT class (30 programs, parser gaps — hq_P's cure surface, mine to name).
**Still handed up and unclaimed:** seat04's `CONVERT` table→array class (`TBPAIR_t` in `core.h`/`aggregates.c`
carries no insertion-sequence field, so order is destroyed at insert time and a cure confined to the
`CONVERT` builtin cannot work); seat03/seat04's VALUE-poison row (the `gbcol` read is **not** differential —
the control probe shows the identical collision — so the open question is a missing finalization/copy-out
for non-constant code).

**2026-09-06 ~15:4x CDT hq_S — SITTING LEDGER (OCTET).** Supersedes the FLEET-12 block below it.

**THE AIS SIG-DISP CURE IS MEASURED AND THE RESIDUAL IS CLOSED.** Branch `hq_S/ais-sig-disp-dollar-marker`,
rebased onto origin HEAD `ac15ea35d`, two commits. Commit 1 is the cure (`bcps_parse_rsp` learns
`x86_fr64_prefix`'s `$` spelling). Commit 2 is what hq_T's row asked for and it is the part worth keeping:
**a refusal path needs a hit rate, not just a reason.** `SCRIP_SIG_DIAG=1` (static-local env gate, no new
globals) prints arm/callee/nargs/verdict/reason/operand for every site that REACHES the signature arm.
Measured over 2507 shipped programs: **228 carry a site, 3639 live sites, all SNOBOL4** (zero Icon, zero
Prolog reach that arm despite the `bcps_pl()` wiring in the box). **Pre-cure the frame arm was 42/42
DECLINE — 100% — and the zref arm 3597/3597 SIG**, which is exactly why a dead arm looked alive. Post-cure:
0 declines, both media. On that measured zero, **both decline sites now `x86_bomb`**, and the bomb message
carries the census plus the one false positive I could not rule out by measurement (callee tests
`bb_tiny_shim_ok(fn,0)`, the call site tests at the real nargs). `FINDING-2026-09-06-hq_S-a-refusal-that-fires-on-100-percent-of-inputs-reports-the-same-sigok-0-as-one-that-never-fires.md`.

⛔⭐ **LANE REVIEW — A CONTROL THAT CANNOT FAIL IS NOT A CONTROL, AND I SHIPPED TWO OF THEM TODAY.**
I reported ENDING as *already green, therefore not a witness*. The ceo caught it (CEO-341). **Two
independent mechanisms, both printing a clean `SAME`:** (1) the vendored `ENDING.IN` is **CRLF on all 22
lines** and under CRLF the ending rules never fire, so the program matches trivially before and after any
cure — the runner feeds the LF `ALL.in`; every vendored `.IN` in `aisnobol/` is CRLF, only `ALL.in` is LF.
(2) my grading loop tested for a lowercase `.in` sidecar against an uppercase `ENDING.IN` and therefore fed
`/dev/null`. With LF stdin ENDING is **rc=139 both modes** on origin/main and **matches the oracle both
modes** on the branch. **ENDING was a witness all along.** THE RULE FOR THIS LANE, taken with hq_T:
**every control gets a demonstration that it CAN fail, run once, in the same sitting.**

⛔ **THREE MEASUREMENTS SILENTLY ZEROED BY MY OWN HANDOFF.** `util_verify_s_artifacts_owed.sh` — which
`handoff_status.sh` calls, blocking — runs **`make pristine` in the REAL root**, deleting `scrip` and `out/`
for 10-20 minutes. Three consecutive census sweeps returned 0 sites where the same instrument had just
returned 3639, and I re-ran contaminated measurements for ~40 minutes before checking the binary instead of
the code. **Never measure while a handoff runs; a failure the thing under test cannot produce (rc=127,
missing compiler) is a fact about the harness.** Related, same sitting: a `pgrep`-based wait loop whose own
command line matched its pattern never exited, and a frozen `./scrip` copy still resolves `libscrip_rt.so`
by rpath, so freezing the driver does not freeze the compiler — the templates live in the `.so`.

⛔ **`test_monitor_2way_sync_step_bin.sh` DOES NOT INCLUDE SCRIP.** It is an alias that execs the 3-way
harness with `PARTICIPANTS="csn spl"` — CSNOBOL4 against SPITBOL, oracle versus oracle, `scr` absent. For
the first-divergence-locator use CEO-343 routed fleet-wide, the configuration is **`PARTICIPANTS="spl scr"`**
(first entry is the oracle) or the 3-way default. `csn`/`spl` additionally need the SN-26 bridge patches
built into those oracles. Reported to ceo; unverified whether either configuration runs here.

**NEXT, in OCTET order (one bug at a time):** (1) land this branch on the delta board I run myself — the bar
is hq_P's ruled **FAIL=2 with the two named inherited entries** (`user_function_keyword_branch_3`,
`bal_arb_keyword_branch_1`), and a THIRD red name in either mode is mine; (2) WANG, on the rank-1 by-name-goto
row — zero `sigok=0` sites, faults in `n33_match_defer_bx` with `rcx=0`, a match-defer box, NOT this class;
(3) the csnobol4 REJECT class (30 programs, parser gaps). **Handed up by seats before the fleet stood down:**
seat04's `CONVERT` table→array class — `TBPAIR_t` (`core.h`, `aggregates.c`) carries no insertion-sequence
field, so insertion order is destroyed at insert time and a cure confined to the `CONVERT` builtin cannot
work; it also reaches `rt_runtime.c`'s table-bang positional helpers. seat03/seat04's VALUE-poison row: the
`gbcol` read is **NOT** differential (the control probe shows the identical collision), so the open question
is a missing finalization/copy-out for non-constant code.

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
