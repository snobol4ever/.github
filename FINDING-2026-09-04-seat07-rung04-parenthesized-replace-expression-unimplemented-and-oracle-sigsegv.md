# rung04 forms turned up a real SCRIP gap (parenthesized replace-as-expression) and a flaky shared-oracle crash — two, split out

**seat07, 2026-09-04. MODE `FLEET-16`. Lane hq_P. Row `snobol4-ladder-every-feature-in-isolation-with-variations`, rung04.**

## 1. SCRIP gap: parenthesized pattern-match-with-replacement is not lowered as an expression

SPITBOL manual p.74 ("Pattern Matching with Replacement"): *"SPITBOL allows you to place the subject,
pattern, and replacement within parentheses and used as an expression. The value of the expression is the
entire subject string after replacement occurs, or failure."* Every book example of this form uses the
explicit `?` operator, e.g. `(RAINBOW ? CYCLE = REST ITEM ',')`.

Witness `ladder__rung04_replacement_expression_value`:
```
T = "MUCH ADO ABOUT NOTHING"
OUTPUT = (T ? "ADO" = "FUSS")
END
```
Oracle (`sbl -bf`): rc=0, `MUCH FUSS ABOUT NOTHING`. `./scrip --run`:
```
FATAL lower_snobol4 (GZ#5 subset): pattern element not in the SN4-PAT subset (LEN, literal, ANY, NOTANY,
SPAN, BREAK, BREAKX, TAB, RTAB, POS, RPOS, REM, ARB; SEQ+ALT landed SN4-PAT-3h). Pattern matching, EVAL and
CODE are outside the landed subset (IR_MATCH_* family pending); see GOAL-SNOBOL4-BB.md.
```
rc=1 on m3; m4 NOBUILD (same lowering path, never reaches codegen). The literal pattern `"ADO"` is **not** the
problem — the *same* literal pattern works fine as a top-level statement (`T "ADO" = "FUSS"`, this rung's own
base witness `ladder__rung04_pattern_replace` proves it green). The gap is specifically the
parenthesized/expression-context lowering path for pattern-match-with-replacement: entirely absent, not a
partial-subset edge case.

My first draft of this witness omitted the `?` (`OUTPUT = (T "ADO" = "FUSS")`, following this rung's
top-level-statement convention). That is **not valid syntax for the parenthesized form**: the oracle rejects
it too (ERROR 212, "value used where name is required" — same class as §2 below) and scrip aborts
(`libscrip_rt: BOMB`, SIGABRT). Both reject it, so it is not a usable witness either way; corrected to match
the book's own `?`-bearing syntax, which the oracle accepts cleanly (rc=0) and scrip does not (FATAL, clean
bail-out, no crash). The scrip abort-on-invalid-syntax is a separate, milder robustness gap (a FATAL would be
better than a BOMB here too) not pursued further this session — flagging it here so it isn't rediscovered as
a mystery crash: feed a parenthesized replace-statement without `?` and disambiguate before concluding it's a
new class.

**Per row policy (THERE IS NO XFAIL): this witness is absorbed and stays in the master red, not suppressed.**
`util_build_master_suite.py`'s auto-classifier sets `xfail=True`/banner `XFAIL` for any absorbed entry that
isn't green at absorb time (`orig_green` in `corpus_suite_harness.py convert_one()`) — correct default for
absorbing an already-known-red witness from another campaign, wrong for a ladder witness whose whole point is
to expose a live gap honestly. Hand-reverted in `ALL.csv` (xfail column 1→0), `ALL.sno`/`ALL.ref` (banner
" XFAIL" suffix stripped, recomputed to the correct dash-width for a non-xfail banner) so
`test_snobol4_ladder.sh` buckets it as a genuine FAIL, not an excused XFAIL — verified: `--only 4` shows
`FAIL=2` (this witness, both modes), `--to 10` shows the other 27 witnesses (54 gradings) still green, no
regression.

**Class row filed**: `mint`ed to hq_P (own lane, `lower_snobol4`-scoped per the FATAL's own text, not a
shared-node defect) — topic `snobol4-parenthesized-replace-expression-not-lowered`.

## 2. Shared oracle `/home/resources/x64/bin/sbl -bf` SIGSEGVs nondeterministically on ERROR 212 recovery

Distinct from the already-documented "plain `-b` manufactures phantom duplicate labels and crashes recovery"
class (`lib_oracle_flags.sh`, `test_snobol4_ladder.sh` header) — this trigger reproduces **with the correct,
documented `-bf` flags**. Minimal repro:
```
"MASH" "M" = "B"
OUTPUT = "unreached if rejected at compile time"
END
```
(p.72's own literal-subject-illegal example, book cites Error #212.) 6 identical invocations of
`sbl -bf <this file> </dev/null`, same binary, same input, same box, no concurrent load change observed:
3 runs printed `ERROR 212 -- syntax error: value used where name is required` (twice, to stdout and stderr)
and exited rc=231 cleanly; 3 runs printed the same error once then **SIGSEGV'd (rc=139, core dumped)** partway
through what looks like the second copy of the diagnostic. Roughly 50/50 over n=6 — not a one-off.

**Consequence for this row**: no reliable oracle-cut `.ref` is obtainable for a "literal subject is illegal"
witness without hand-typing one (forbidden by the row's own recipe). **Deliberately excluded**, not minted —
noted in `LADDER.tsv` rung04's NOTE cell so a future session doesn't rediscover the same crash from scratch.
scrip's own behavior on this exact input is a separate, milder FATAL (`SN4-REPL slice 1: replacement subject
must be a plain variable`, rc=1, no crash) — cleaner than the oracle's, incidentally.

**Consequence for the fleet**: `/home/resources/x64/bin/sbl` is the ONE shared correctness oracle every seat
cuts SNOBOL4/Snocone refs from (`sbl_correctness_bin()`, no local copies by design — Lon s261). A seat that
happens to cut a ref from this exact error shape on an unlucky run gets a **corrupted/nonexistent `.ref`
silently**, not a loud refusal — the crash looks like a shell hiccup, not a data-quality problem, unless you
already know to check rc. No cure attempted here (out of scope for a ladder-witness row; the shared oracle
binary is not this project's code to patch) — flagging so a future investigation doesn't start blind, and so
anyone who *does* see a mid-cut SIGSEGV from `sbl -bf` recognizes it rather than assuming a fluke.
