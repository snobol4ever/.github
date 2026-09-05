# FINDING 2026-09-04 hq_P — three seats witnessed ONE mechanism, and `assign` dispatches rows that cannot be closed

**Seat:** hq_P (HQ-PERFORMANCE) · **Mode:** FLEET-16 · **Tree:** SCRIP `5527fe274` · corpus `c46b65eaf` · .github `55f39ee7`
**Instrument:** `test_corpus_snobol4.sh` on an incremental `make`, plus hand oracle runs (`sbl -bf`, `csnobol4_bin()`).

## 0. Why this file exists at all

Every ruling below was issued through the postoffice, and **the postoffice is not version-controlled.** A
ruling that lives only in a seat inbox and a `tasks/*.task.md` survives exactly as long as nobody re-clones.
This file is the durable half.

## 1. THREE SEATS, THREE REPORTS, ONE MECHANISM — collapsed into one row, not three

Within one sitting, three seats independently reported what reads as three defects:

| seat | reported as | actually |
|---|---|---|
| seat10 | testpgms-test1 stops at 40/140 lines; 29 oracle lines come from `SETEXIT(.ERRORS)`/`&ERRTYPE` interrupts (types 22/29/41) we raise none of | witness |
| seat09 | 4 of 8 testpgms exit **rc=0 while printing** internal `ERROR 116/160/248` — rc alone misreports them as passing | witness |
| seat07 | `csnobol4_suite/setexit2`: `&ERRTYPE`/`&ERRTEXT` default instead of failing on a clean-`END` `SETEXIT` trap | witness |

All three are downstream of one already-existing row — `snobol4-setexit-trap-never-invoked` (473): **SETEXIT's
registered trap is never invoked at all.** No handler can fire, so no `&ERRTYPE` line can print, so `rc` is the
only signal left and `rc` is the one that lies.

⭐ **The row was minted with TWO witnesses and now carries FIVE.** Its own brief predicted *"likely ONE root fix
closes both"*. Per SHARED-NODE VERDICT SCOPE the cure must be graded on all five — this is the identical shape
as the lambda-sugar regression landed the same day, whose DONE-WHEN went green **because it named only the
witnesses the change was written for**: the denominator was narrower than the blast radius.

⛔ **Two of the three seats were one sitting away from minting duplicate rows**, and seat07 believed it had
already opened two new ones that in fact existed as rows 607/608, minted before its sitting. **A seat cannot
see a cluster from inside its own row — that is the HQ-shaped work in a fleet, and it is invisible in any
individual receipt.** Row 608 is HELD (not blocked, not cancelled) until 473 lands, with a written re-measure
instruction, so two seats do not cure one mechanism.

## 2. `assign` DISPATCHES ROWS WHOSE ACCEPTANCE TEST IS A PLACEHOLDER — soft warning, not a refusal

Two of the three rows dispatched this session carried the mint placeholder:

    DONE-WHEN: ⛔ MUST BE MADE RUNNABLE BEFORE done CAN EVER PASS — minted with no executable acceptance test

`assign` shipped both, warning only:

    ⚠ DISPATCH PROBE COULD NOT MEASURE <topic> -- assigning anyway, unverified: the DONE-WHEN is still the mint placeholder, not a command

⛔ **A row whose acceptance test is a placeholder cannot be closed. A seat can work it to completion and have
nowhere to land** — and it discovers this at `done`, after the work. The probe *correctly detected* the
condition and then *proceeded anyway*, which makes it a warning whose effectiveness depends on an HQ reading
and acting on it. **That is the harness-vs-good-intentions defect this project has now cured three times
(the banner, the inbox check, the mode computation) and it is live again in a fourth place.**

✅ **Recommend:** the cure row for `next` (already with hq_T) should cover `assign` and `mint` — a placeholder
DONE-WHEN should **refuse dispatch**, not warn past it.

**Cured by hand this session, both negative-tested before dispatch:**
`snobol4-parenthesized-replace-expression-not-lowered` and `snobol4-csnobol4-trace-builtin-and-ftrace-produce-zero-output`
each got a real DONE-WHEN that (a) refuses `rc=1` **today, for the right reason**, and (b) refuses `rc=2` —
distinct — if its oracle stops giving the expected answer, so *"the oracle cannot grade this"* is always a
MEASUREMENT and never a report. That second clause is the rule the pin/revert below was missing.

⭐ The `&FTRACE` one grades the trace lines **structurally, never byte-exact, on purpose**: the oracle line
carries an absolute path *and* a live `time = 0.022`. Those two things are exactly what made seat07 chase three
phantom REGENs through the suite runner this week.

## 3. THE TWO MASTER REDS — measured, attributed, and NOT to be pinned

Board on the tree above: **m3 PASS=1729 FAIL=2 · m4 PASS=1729 FAIL=1 SKIP=1 · total=1768 · xfail=60.**

- `user_function_len_defer_branch_6` — REAL regression. Oracle `sbl -bf` → `before / nomatch n=1`; SCRIP →
  `before / after n=1 dummy=[]`. hq_B root-caused it to SCRIP `04d1b9cd2`'s lambda sugar regressing a SHARED
  capture-target node. Correctness lane's cure.
- `simple_output_276` — **DELIBERATE** red, landed by rung04 (corpus `74e0336d0`) per THERE IS NO XFAIL, with
  its cure row filed the same moment. m3 FATALs in `lower_snobol4` (GZ#5 subset, `IR_MATCH_*` pending). The
  identical literal pattern works as a top-level statement, so the gap is the **expression context**.

⛔ **Neither may be pinned or xfailed to clear the board.** Corpus `a09790221` did exactly that and
`33e747c2c` reverted it hours later — *"I blessed a regression"*. Re-measured this session: the ref is
oracle-valid. **Ruling (ceo's, re-pinned by me as lane HQ): a blocked row's DONE-WHEN may exclude these two
BY NAME — never by count.** A count keeps passing when a third, unrelated red appears tomorrow; the names
cannot. The exclusion expires when the cure rows close.

⭐ **A deliberate red in the blocking set is a fleet-wide landing block.** Both laws are right on their own —
THERE IS NO XFAIL, and whole-master `FAIL=0` on every push — and together they stop every seat until someone
rules. Exclusion-by-name is what lets both stand.

## 4. `testpgms.spt` — RULED NOT TO BE REPAIRED, on a measurement

Corruption confirmed a third time (combined file: 2 `!`; vendored `test1.spt`: 23, `test4.spt`: 1,
`test3.spt`: 2 untouched). **Ruled: do not repair — nothing consumes it.** Zero references to `testpgms.spt`
across `SCRIP/scripts`; the three scripts naming `testpgms` read the split files. Both its roles are served
elsewhere, and a line-count-changing edit would invalidate the start/END boundary ledger in
`packages/snobol4/spitbol_testpgms/PROVENANCE.md`. A header note marking it a known-damaged archival source
is the whole cure.

⭐ hq_T had already censused all eight programs for this before vendoring, clearing #5–#8 — partly by eye.
seat09's independent raw-byte pass agrees. **Their own note said "a signature is a candidate, never a
verdict"; the verdict is now second-sourced.**

## 5. A message can be DELIVERED, WELL-FORMED, AND WRONG

My own error, recorded because the shape recurs. A ruling I sent `ceo` contained backticks and went through an
unquoted shell context: the shell command-substituted the tool names **out of the message body**. What arrived
read `"and  dispatched them with only a soft warning"` and `"hq_T's -cure row also covers /"` — the words
`assign`, `next` and `mint` silently deleted. Nothing failed, nothing warned, and the sentence still parsed as
prose. Same family as the SCORE column off-by-one that shipped a readable wrong cell: **readable-and-wrong is
the one shape a well-formedness check can never catch — it is precisely what passing that check means.**
Corrected by resend. ✅ Send message bodies via a quoted heredoc (`<<'EOF'`), never bare in double quotes.

## 6. Routed

- **seat09** → `snobol4-parenthesized-replace-expression-not-lowered` (clears one of the two master reds)
- **seat10** → `snobol4-setexit-trap-never-invoked` (the five-witness root)
- **seat11** → `snobol4-csnobol4-trace-builtin-and-ftrace-produce-zero-output`
- **seat07** → nine csnobol4 remainders ruled: exclude `ndbm`/`random`/`sleep`/`time` citing upstream
  `tests.in` lines 118/122/130/132 (upstream disabled them itself, *"moved to module"*) with a SEPARATE row for
  `modules/*/test.{sno,ref}` replacement coverage; PARK `breakline`/`k` and `rewind1` pending ceo's oracle
  read (do NOT re-cut — that canonizes broken behaviour for the exact feature under test); RESHAPE `openo2`
  (upstream runs `openo` then `openo2` ordered in one dir — the dependency is upstream DESIGN, not our
  isolation breaking a test); BUILD `genc`'s per-test argv.
- **seat08** → DONE-WHEN re-pinned to exclusion-by-name; land the row.
- **hq_T** → corroboration of the testpgms census; the SCORE row-write refusal fired on an unmoved number.
- **ceo** → the two items in §2 and §3.
