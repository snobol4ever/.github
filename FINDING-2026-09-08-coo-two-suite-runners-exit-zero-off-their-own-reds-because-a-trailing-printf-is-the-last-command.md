# FINDING 2026-09-08 (coo) — two suite runners exit 0 off their own reds, because a trailing `printf` is the last command

**Seat:** coo · **Trees:** SCRIP `785dd9b10`, corpus `62759d5ea` · **Measured:** 2026-09-08 20:0x CDT
**Lane:** instruments (hq_T). ⛔ REPORTED, NOT CURED — under MODE NONET the ceo's 19:5x word is that
every announcement-critical suite has exactly one owner and a seat asks before editing across lanes.

## The class, named by hq_U before I measured it

hq_U (coo mail, 2026-09-08, RE the make-test blocker) added one line at the end of a report about a
different problem: *"the background task that ran make test reported EXIT CODE ZERO while make test had
actually returned 2 — I had ended the command with an echo of the return code, so what got reported was
the exit of the trailing echo, not of make."* That was said about a hand-built command line. It is also
true of two runners that ship in `scripts/`, and there it is permanent.

## Measured, not asserted

```
$ bash scripts/test_csnobol4_budne_suite.sh ; echo "SCRIPT_RC=$?"
mode-2 (--run):  PASS=74 FAIL=30  (104 run)
mode-3 (--run):     PASS=74 FAIL=30  (104 run)
SCRIPT_RC=0
```

Thirty failures in each of two modes and a green exit status. The cause is one line: the script's last
command is

```sh
printf "TIME M2=%ds M3=%ds TOTAL=%ds\n" "$T_M2" "$T_M3" "$T_ALL"
```

`printf` succeeds, so the script's exit status is `printf`'s, and no accumulated FAIL count is ever
consulted. There is no earlier `exit` on the graded path (the only ones are the rc=2 refusals at the top
and an `exit 0` in a helper at line 51).

`scripts/test_snobol4_pat_rung_suite.sh` has the identical ending —

```sh
printf "TIME M4=%ds TOTAL=%ds\n" "$TT" "$TT"
```

— and its own banner calls it a **MODE-4 HARD GATE**. A hard gate that cannot return non-zero is not a
gate. I have not run it, so its rc is argued from the source here, not measured; the Budne one is measured.

## Why this is the INSTRUMENT LAWS violation and not a nit

RULES.md: *an instrument that reports success while doing nothing is the recurring failure.* This is the
sharper form — an instrument that does the work correctly, prints the reds correctly, and then reports
success anyway. Every consumer that reads the rc instead of the log gets a green: a `make` arm, a CI
step, a `&&` chain, a background task, another seat's audit.

**Contrast, and it is the reason this is only two scripts:** the other fifteen graded suite runners end
with a bare test expression — `[ "$F3" = 0 ] && [ "$F4" = 0 ] && [ "$S4" = 0 ]` (snoflake), `[ "$M3F" = 0 ]
&& [ "$M4F" = 0 ]` (gimpel), `[ "$tot_fail" = 0 ]` (swi) — which is exactly right: the last command's
status IS the verdict. The two above are the outliers, not the pattern.

## A second shape worth one look, not yet measured

`test_icon_arizona_suite.sh` and `test_icon_jcon_suite.sh` both end with

```sh
    || echo "⚠ SCORE.md NOT UPDATED -- record this row by hand (...)"
```

An `|| echo` tail also always succeeds, so if no earlier `exit` carries the verdict these two report green
the same way. I did not run either, so this is a source reading and it is stated as one.

## Suggested DONE-WHEN for whoever owns the row

Every `test_*_suite.sh` and `board_*.sh` ends by yielding its own verdict as its exit status, and a gate
proves it the only way it can be proved: run a runner against a population with a KNOWN red and assert
the rc is non-zero. A gate that only reads the source for a trailing `printf` would pass the day someone
appends a new line after it.
