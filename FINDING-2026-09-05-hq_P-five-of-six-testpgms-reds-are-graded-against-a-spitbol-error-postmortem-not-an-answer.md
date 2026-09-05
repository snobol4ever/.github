# FINDING — five of six scored `spitbol_testpgms` reds are graded against a SPITBOL ERROR POST-MORTEM, not an answer

**Seat:** hq_P · **Date:** 2026-09-05 · **Row:** `snobol4-spitbol-testpgms-four-programs-to-100-percent-both-modes`
**Tree:** SCRIP `df9fe6af0` · corpus `d58a796fa` · RT_OPT=`-O0` · oracle `/home/resources/x64/bin/sbl -bf` · modes m3+m4

## The board line (FIRST EVER LIVE RUN of this row's re-pinned DONE-WHEN)

```
SPITBOL_TESTPGMS_BOARD total=8 scored=7 unscored=1 m3_pass=1 m3_fail=6 m4_pass=1 m4_fail=6   rc=1
```

⭐ The baton predicted this run would `REFUSE(2)` on `total<8`. It did not: hq_T's vendoring row landed all
eight programs, so the criterion graded instead of refusing. **The prediction in the baton was stale, not wrong
when written** — recorded here so the next reader does not re-derive it.

## What the six reds actually are

| prog | oracle rc | oracle output | what the runner did | what is true |
|---|---|---|---|---|
| test1 | 0 | 140 clean lines | scored, RED | ⭐ **genuine SCRIP red** (seat08's row, CLAIMED) |
| test2 | 231 | — | UNSCORED, named | correct |
| test3 | 0 | 47 clean lines | scored, PASS | correct |
| test4 | **0** | `ERROR 116 -- inappropriate file specification for input` | scored, RED | ⛔ graded against a non-answer |
| test5 | **0** | `ERROR 116` | scored, RED | ⛔ graded against a non-answer |
| test6 | **0** | `ERROR 248 -- attempted redefinition of system function` | scored, RED | ⛔ graded against a non-answer |
| test7 | **0** | `ERROR 248` | scored, RED | ⛔ graded against a non-answer |
| test8 | **0** | `ERROR 160 -- inappropriate file specification for output` | scored, RED | ⛔ graded against a non-answer |

⛔⭐ **THE INSTRUMENT HOLE, AND IT IS THE RUNNER'S OWN DOCTRINE ONE TURN SHORT.** The runner's header states the
law correctly — *"AN ORACLE THAT DIES IS UNSCORED AND COUNTED AS SUCH … the run STATUS decides, never the byte
count"* — and implements it as `orc != 0`. **SPITBOL reports a FATAL ERROR and exits `rc=0`.** So a run that
produced no answer at all passes the status test, and a "ref" is cut LIVE from an error dump. The guard is not
absent; it tests the one thing that does not discriminate here.

## Why these five can never be diffed against this oracle

The oracle's entire "answer" for a refused program is an error banner plus a post-mortem:

```
test5.spt(6) : ERROR 116 -- inappropriate file specification for input
in file              test5.spt
in line              6
stmts executed       4
execution time msec  0
memory used (bytes)  15408
memory left (bytes)  1033160
```

⛔ `memory used (bytes)`, `memory left (bytes)` and `execution time msec` are implementation-specific and
nondeterministic. **No second implementation can ever byte-match this**, so these five are structurally
unscorable against `sbl` — the same category as test2, reached by a different route. ⭐ Verified the post-mortem
is ERROR-PATH ONLY: test3 completes and its 47 lines carry no dump, which is why test3 can and does pass.

## The constructs, ablated to witnesses, with a CONTROL ARM

Four minimal witnesses, each graded on **two independent SPITBOL builds** plus CSNOBOL4 and SCRIP:

| witness | construct | x64 grading oracle | clean bench oracle (control) | CSNOBOL4 | SCRIP m3 |
|---|---|---|---|---|---|
| w1 | `INPUT(.INPUT,,72)` | ERROR 116 | ERROR 116 | runs | **runs** |
| w2 | `OUTPUT('TITLE',6,'(14H…,110A1)')` | ERROR 160 | ERROR 160 | runs | **runs** |
| w3 | `DATA('SYMB(CHAR,LINK)')` | ERROR 248 | ERROR 248 | runs | **runs** |
| w4 | `DEFINE('INDEX(TAU)')` | ok | ok | runs | runs |

⭐ **BOTH SPITBOL BUILDS AGREE EXACTLY**, so this is SPITBOL SEMANTICS, not a broken or mis-flagged oracle —
which was my own first reading of it, and it was wrong. The manual is the authority and confirms the shape:
`INPUT(.Variable, Channel, "filename[options]")` (v3.7 §1929) — when the 3-argument form is used the channel
must be a valid integer, and `INPUT(.INPUT,,72)` passes a null channel.
⛔ w4 is the negative control that keeps the claim honest: `DEFINE('INDEX(TAU)')` is NOT the 248 trigger.
test6's 248 is `test6.spt(16)`, `DATA('ITEM(COUNT,TOP)')` — a DATA field name colliding with a system function.

## SCRIP's side: not a plain bug, a DIALECT divergence

`src/runtime/core/core.c:3212` `_INPUT_` computes `int ch = (n >= 2 && IS_INT(a[1])) ? (int)a[1].i : -1;` and,
when the channel is null, falls into the stdin re-association branch and returns `NULVCL` (success) instead of
raising. `_OUTPUT_` (`:3247`) has the same shape. ⭐ **SCRIP's acceptance matches CSNOBOL4 exactly** (verified,
table above) — so the accurate statement is that SCRIP speaks the CSNOBOL4 dialect here while its DEFAULT
dialect is SPITBOL, not that it is simply too permissive.

⭐ **THE MACHINERY FOR THE CURE ALREADY EXISTS AND LANDED TODAY:** `--compat=spitbol|csnobol4` (ceo RULING R1,
SCRIP `f3f4870d7`, `src/driver/scrip.c:847`). It is **not yet wired to file-association acceptance** — `grep
compat src/runtime/core/core.c` returns nothing.

## Precedent already in this corpus — this class was met and settled once before

⭐ The gimpel suite hit the identical class and resolved it by ORACLE CHOICE, and wrote down why:
- `packages/snobol4/gimpel/ASM_driver.sno:16` — *"This .ref comes from CSNOBOL4 (snobol4 -b), not from
  x64/bin/sbl. ASM.sno opens its work file with `OUTPUT(.DISK,10,,'ASMTEMP')` -- a four-argument form Spitbol
  does not accept -- and sbl stops with ERROR 160 … before assembling anything. CSNOBOL4 is the other
  sanctioned SNOBOL4 oracle and runs it."*
- `packages/snobol4/gimpel/POKER_driver.sno:6` — same class, ERROR 116 AND 248, documented as unrunnable by
  either oracle.

⛔ The class is not confined to testpgms: **50 sites** corpus-wide use an empty-channel `INPUT`/`OUTPUT`
association, 7 in testpgms and the rest largely in gimpel.

## Consequence for the row

⛔ The row's DONE-WHEN requires `unscored=0` AND `m3_fail=0 m4_fail=0`. As long as these five are graded by
byte-diff against `sbl`, **it is unsatisfiable by any amount of compiler work** — the ground truth is a memory
dump. This is a ruling question (asked of ceo, this session), not a defect to code around, and it is NOT a
reason to loosen the criterion: `unscored=0` is doing exactly the job it was added for.

## Recommended resolution (for the ceo's ruling — not applied)

1. **Runner (hq_T's lane, messaged):** treat an oracle run whose output carries a SPITBOL fatal-error
   post-mortem as UNSCORED-and-named, exactly like `rc!=0`. Status alone cannot see this class.
2. **Oracle choice (precedented):** grade test4/5/6/7/8 against CSNOBOL4 as gimpel's ASM already does, or under
   `--compat=csnobol4`. ⚠️ `csnobol4/` is ABSENT from this root; the working binary is `/home/claude/csnobol4/snobol4`.
3. **SCRIP conformance (hq_P's lane, rowed):** wire `--compat` to file-association acceptance so the SPITBOL
   default raises 116/160. ⛔ Wide blast radius (50 sites) — it needs its own board, not a drive-by edit.

⛔ **NOT CURED THIS SITTING, AND DELIBERATELY SO:** the 248 class is `snobol4-data-of-a-system-function-name-is-error-248`,
CLAIMED and RUNNING by **seat04**; test1's genuine red is CLAIMED and RUNNING by **seat08**. Under `FLEET-8`
curing either bypasses a live claim lock. Only the 116/160 class was unrowed, and it is rowed by this finding.
