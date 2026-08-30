# FINDING 2026-08-30 hq_B — `SCRIP/test/` does not exist, 19 scripts cite it, 3 report success measuring nothing

**Tree:** SCRIP `d403c283`+ · measured 2026-08-30, seat `hq_B`. Found while censusing raku consumers for
`smx-refusal-exits-zero`.

## The tree is gone

```
$ ls -d SCRIP/test
(does not exist)
```

Nineteen scripts under `SCRIP/scripts/` still resolve paths into it, across seven subdirectories:

```
$SCRIP/test/icon   $SCRIP/test/monitor  $SCRIP/test/parser  $SCRIP/test/prolog
$SCRIP/test/raku   $SCRIP/test/snobol   $SCRIP/test/snocone      -- all ABSENT
```

## How the nineteen behave — measured, one run each

```
rc=0, reports SUCCESS  : 5
rc=2, REFUSES          : 1
non-zero (fails loudly): 13
```

The 13 and the 1 are fine. The five split into two very different groups, and only one is a defect:

**Harmless-but-misleading (2)** — `test_corpus_icon_parser.sh` (pass=169) and
`test_corpus_prolog_parser.sh` (pass=44) both carry a dead `test/parser/<lang>` entry in a `DIRS` list that
also contains a live `corpus/tests/<lang>` root. Their totals are real and earned; the dead entry silently
contributes zero. Worth cleaning so the list stops implying coverage it does not provide.

**⛔ Vacuous green (3)** — all raku, all exit 0 having measured nothing:

```
test_raku_ir_full_suite.sh   "SKIP  test/raku dir not found at …"     rc=0
test_raku_ir_rungs.sh        "SKIP test/raku dir not found at …"      rc=0
test_raku_mode3_native.sh    "PASS=0 FAIL=0 CRASH=0 TOTAL=0"          rc=0   <- says nothing at all
```

The first two at least *say* they skipped — and then report success anyway, which is the
skip-as-success ban in `RULES.md` verbatim. **`test_raku_mode3_native.sh` is the worst of the three**: it
iterates a glob over a nonexistent directory, gets zero files, and prints a fully-formed scoreboard whose
every counter is zero. Nothing in its output mentions a missing directory. `TOTAL=0` and `FAIL=0` are both
true; together they read as a clean run.

⭐ This is the third instance of the same shape found in this tree this week, each in a different script and
each after a directory moved: `test_crosscheck_snocone.sh` silently dropped 4 of 8 cases and printed
`SKIP=0`; `test_lower_byte_identical.sh` skipped 25 of 30 and printed `PASS=5`; now three raku suites
report on an empty set. **The common cause is not carelessness — it is that a `for f in "$DIR"/*` loop over
a missing directory is indistinguishable, from inside the script, from a directory that is legitimately
empty.** The distinction has to be drawn before the loop, and none of the three draws it.

## Cure

Each of the three should refuse (`rc=2`) naming the missing path, per RULES' *a test that cannot measure
REFUSES* — they are already 90% there, since two of them print the right message and then return the wrong
code. The two `DIRS`-list entries should simply be dropped.

⚠️ Not done here: this is a different row from the one I hold, and three scripts going from green to
refusing is a fleet-visible change. Routed rather than landed.
