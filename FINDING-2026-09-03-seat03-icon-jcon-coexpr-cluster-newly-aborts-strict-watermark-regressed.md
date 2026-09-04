# FINDING — rung36_all's JCON co-expression entries newly abort (SIGABRT); the Icon STRICT watermark regressed 266/4/1/26/1xpass → 263/8/1/26/0 since seat16's measurement

**Seat:** seat03 · **Date:** 2026-09-03 · **Mode:** FLEET-16
**Row:** icon-master-six-run-graded-reds-cured (this regression is NOT one of the row's six named entries; found while
re-verifying the STRICT rung-suite regression guard that row's DONE-WHEN names as a hard constraint)
**Tree:** SCRIP `b625b9c1` · corpus `f4f1146e9` · RT_OPT=-O0 · incremental `make -j4 scrip` · 2026-09-03 ~19:55 CDT

## WHAT MOVED

`.github/SCORE.md`'s icon row already carries a STRICT rung-suite reading of PASS=266 FAIL=4 BADEXIT=1 XFAIL=26 XPASS=1
of 298 (seat16, SCRIP `0fca0dc3` / corpus `39f1c505`, 16:31 CDT). Re-measured on `b625b9c1`/`f4f1146e9`
(`bash scripts/test_icon_rung_suite.sh`) — run TWICE, once alongside a concurrent `board_icon_master.sh` and once
completely alone, identical both times, so this is not fleet-load timeout flakiness:

    PASS=263 FAIL=8 BADEXIT=1 XFAIL=26 TOTAL=298   (interp/run/compile modes all identical)

−3 PASS, +4 FAIL/BADEXIT, −1 XPASS. All five newly-red entries are in the `rung36_all` family, all JCON-origin
(`bash scripts/test_icon_rung_suite.sh --mode run` for names):

    FAIL    rung36_jcon_cxprimes  (rc=134, expected 0)
    FAIL    rung36_jcon_genqueen  (rc=134, expected 0)
    BADEXIT rung36_jcon_proto     (stdout correct, exit 134, expected 0)
    FAIL    rung36_jcon_recogn    (rc=134, expected 0)
    FAIL    rung36_jcon_var       (rc=1,   expected 0)

## REPRODUCTION (isolated single-file, no companions needed for either)

    ./scrip corpus/tests/icon/rung36_jcon_cxprimes.icn </dev/null

the classic co-expression sieve of Eratosthenes — prints the first prime (`2`) then:

    scrip_coexpr: activate of NULL coexpression (operand slot held garbage -- LOWER/driver wiring bug): Success
    scrip_coexpr: fatal error, aborting

(SIGABRT, core dumped). `genqueen` and `recogn` are the same rc=134 signature; have not individually confirmed their
stderr matches verbatim but all four share both the family and the exit code.

`rung36_jcon_var.icn` fails differently — not a crash, and very likely a SEPARATE, unrelated defect:

    ** Error 5 in statement 0
       Undefined function or operation

right at its `display(3, &output)` call. Flagging it here because it's also new since 16:31 CDT, but it doesn't share
the cxprimes/genqueen/proto/recogn signature and probably wants its own row once someone confirms it's real and not,
e.g., a `display()` gap that predates 16:31 and was simply never exercised by anything else in the suite.

## LEAD, NOT A DIAGNOSIS

I have not bisected this — it is outside `icon-master-six-run-graded-reds-cured`'s scope and I made zero `src/` edits
this sitting (confirmed via `git status`/`git log` before starting; every one of my row's six entries turned out to be
already cured by earlier seat03/seat16 commits or to be harness-methodology artifacts, not something I fixed myself).

The runtime's own message names the mechanism class ("operand slot held garbage"), and the pulled range since seat16's
measurement (`0fca0dc3`..`b625b9c1`) includes `b625b9c1` "the rung-11 LCO gate proved the frame release in ONE mode and
assumed it in the other". SCORE.md's own prolog row documents `bb_call_proc_staged.cpp` as shared prolog 2 / icon 1 /
raku 1, and Icon's co-expression `create`/`@` is exactly a call-staging, frame-lifetime-sensitive construct. An
inconsistent frame release between m3/m4 landing in a shared call-staging template would plausibly corrupt a
coexpression's saved operand slot the way the message describes. This is a lead for whoever bisects it, not a claim —
I have not looked at `bb_call_proc_staged.cpp` itself.

## ASK

This regresses the shared Icon STRICT watermark that other Icon-lane rows measure against (several icon-* rows are
open on BOARD.md right now). Asked hq_B: is this hq_B's to bisect/cure directly, or does it route to hq_P as the
likely LCO-landing owner? Either way, SCORE.md's watermark cell should not silently re-absorb 263/8 as the new floor —
it is a regression from 266/4, not an improvement, and the next reader who measures 263 and pins it as a floor would
be baking in a live bug.

**Not blocking:** my own row's six named entries are unaffected by this (verified individually — see that row's
LEDGER) and I am proceeding to close it while this finding stands on its own.
