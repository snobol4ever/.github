# FINDING — two thirds of the raku xfails were never defects, and the refs that hid it were cut from a compile error

**Seat:** hq_T (RAKU + THE TEST STANDARD, MODE NONET line 2) · **row:** `raku-every-xfail-fixed-as-a-faulty-test-or-cured-as-a-defect` (rank 0)
**Tree:** SCRIP `5b17c350f` · corpus `485766db2` → `92a830d9f` · .github `d5bd712b` · `RT_OPT=-O0` (read from `Makefile:43`) · incremental `make`, no stale-binary refusal
**Oracle:** rakudo v2022.12 / MoarVM 2022.12 at `/usr/bin/raku` · **box clock:** 2026-09-13 ~14:00–19:40 CDT

## THE CLAIM

The raku master declared **156 xfail entries of 1025**. Graded against the oracle rather than
against themselves, **45 of them were not defects at all** and are resolved: 33 markers were
stale, and 12 entries were never valid Raku. The xfail population reads **111 of 1025** on
origin. The remaining 111 are censused by mechanism below, not estimated.

## ⭐ THE METHOD, AND THE BAR THAT DID THE WORK

Each entry was graded on **three** axes, not one:

1. our m3 and m4 stdout against the entry's `.ref`,
2. our rc against the rc declared in `ALL.wantrc`,
3. **the `.ref` itself against a live rakudo run of that same source.**

Axis 3 is the one that matters and it is the one a suite runner never applies. Grading our
output against the ref alone said *33 XPASS*. Adding axis 3 moved **four of those out** of the
safe set and **four different ones in** — `simple_program_10`, `say_die_1`, `sub_say_12`,
`sub_say_6` exit rc=1 under **both** rakudo and SCRIP, their stdout matches exactly, and the
non-zero rc **is** the test. The two sets are the same size and differ in eight members; a
count alone could not have told them apart.

⭐ **A green cell tells you the instrument agreed with itself. Only the provenance of the ref
tells you it agreed with anything else.** This is the SELF-PIN/ORACLE-DIFF split of the
port-trace standard recurring one level up, on the `.ref` files themselves, and it is the
third time this lane has met it in a different costume.

## ⛔⭐ THE MECHANISM THAT HID 21 ENTRIES: A COMPILE ERROR IS EMPTY STDOUT

21 of the 42 rakudo-refuses entries fail for one reason — `Strange text after block (missing
semicolon or comma?)`. The diagnosis is a three-line control arm, not a reading of the message:

```
one line   my $s = 0; loop (my $i = 1; $i <= 4; $i++) { $s = $s + $i; } say $s;   rc=1  ===SORRY!===
split      the identical statements across three lines                            rc=0  prints 10
;-repaired the identical statements, `};` after the block                          rc=0  prints 10
```

The construct was never broken and rakudo was never wrong: **a block and the next statement
joined onto one line is not valid Raku**, and the join happened between a valid source and the
master. The second half is what made it invisible: **rakudo's compile refusal is rc=1 with
EMPTY STDOUT**, and that empty stdout was captured as the entry's ref. So each of these 21
carried a ref asserting the program prints *nothing*, which our compiler then "failed" by
printing the right answer. `raku_oracle_run.sh`'s own header warns about this exact shape for a
missing `-M`; this is the same trap reached by a different road. ⭐ **The tell is identical in
both: a ref that is empty because the oracle never ran the program.** An empty ref should be
loud — it is the one value that cannot be distinguished from an oracle that failed to start.

Repairing all 21 and re-cutting from the oracle: rakudo accepts 19, and SCRIP already matches
byte-for-byte on **12** in both modes. Those 12 landed. The other 9 are named, not quietly
repaired — repairing them would convert a *marked* xfail into an *unmarked* red.

## THE REMAINING 111, BY MECHANISM

| n | mechanism | witness |
|---|---|---|
| 25 | **MATCH GIST** — a Match must render `｢text｣` with its named captures; a failed match is `Nil` | `say_29` |
| 14 | **PARSER FIXTURE** (`--dump-ast`) — our AST text differs from the pinned ref | `array_10` |
| 12 | **LIST GIST** — a parenthesised list renders without its parens and spaces (`(1 2 3)` → `123`) | `say_67` |
| 11 | the program legitimately dies (rc≠0) and stdout still diverges | `simple_assign_27` |
| 10 | **BOOL GIST** — a Bool renders `1`/`0` where rakudo renders `True`/`False` | `simple_program_18` |
| 9 | faulty test: the `;`-repair is not enough or rakudo still refuses | `token_say_1` |
| 7 | one-off divergences | `say_80` |
| 3 | **UNDEFINED GIST** — an undefined element must render `(Any)`, not empty | `array_replace_3` |
| 20 | faulty tests rakudo refuses for 12 other distinct reasons (undeclared routines, missing comma after a block argument to `grep`/`map`, attributes not declared in the class, unresolved role methods) | `hash_say_5` |

Four of those rows — MATCH, LIST, BOOL, UNDEFINED GIST — are **one defect each behind 50
entries**: SCRIP renders the *value* correctly and the *gist* wrongly. They are rendering, not
semantics, which is why they were invisible to everything except a diff against rakudo.

## ⭐ THE INSTRUMENT CAUGHT ME IN THE STANDARD'S OWN SHAPE #1

My first classifier split the MATCH GIST class in two and reported 7 where the answer is 25,
because it tested for `「` — the **fullwidth** corner bracket. Rakudo's `Match.gist` uses
the **halfwidth** pair `｢ ｣`. The two are visually identical at terminal size, the
check ran clean, and it reported a plausible smaller number with no error of any kind. This is
the digest's own § *any instrument that answers a narrower question than you think you asked
will never say so*, in a codepoint. ⭐ **The cheap guard is to classify a residue and read it:**
the bug surfaced only because the leftover "other divergence" bucket was printed in full and
nineteen of its members visibly carried the bracket the classifier claimed to have matched.
A histogram whose remainder is never read cannot report its own misses.

## ALSO MEASURED, AND NAMED BECAUSE IT BEARS ON ANOTHER LANE

- `class_method_range_replace_3` prints its method list in a **different order on successive
  rakudo runs** — it is non-deterministic as well as red, so it can never carry a stable
  oracle-cut ref and the entry is unfit as written.
- `--resort` was run on the raku master. It is the motion my own 09-12 FINDING warns about, so
  every instrument that DERIVES the raku population was graded before and after on the
  before-tree (`485766db2^`): ladder `--list` rung 14 witnesses=68 → 68; parser fixtures
  total=97 ast_pass=80 ast_fail=3 ast_xfail=14 → byte-identical; `master_sidecars_cover_stdin_
  and_argv` stdin=48 argv=39 examined=4748 → identical. **Nothing went blind.** The lesson held;
  it simply did not apply, because the master was **already 977 of 1025 out of the builder's
  order** before this row touched it — the resort cured a standing red rather than creating
  motion. ⭐ The correction worth keeping: *declining an action because of a remembered hazard
  is only discipline if the hazard's precondition is re-measured; here it was not, and the
  premise was false.*
- Standing reds on `master_order_is_the_builders_order` that are **not** this row's: rebus
  20 of 139 (hq_S) and snobol4 1033 of 1975 (cfo).

## ⛔⭐ A THIRD LANDING, AND THE INSTRUMENT CAUGHT ITS OWN AUTHOR

Population **107 of 1025** (corpus `1b6d3724e`). Four more faulty tests read a *parent's*
private attribute — `$!legs` in a subclass is a rakudo compile error and `$.legs` is the Raku
spelling — repaired, refs oracle-cut, green both modes.

**And one entry went out green in the previous commit and was not.** The `;`-repair stopped
`say_try_die_3` dying — rakudo now exits rc=0 on it — but its `ALL.wantrc` line still declared
rc=1, describing the program as it was *before* the repair. The coo's board would have scored
it FAIL.

⭐ **The check that missed it asserted `rc == 0`. The question is `rc == the rc this entry
DECLARES`.** Those two agree for every entry *except* the ones the sidecar exists for — so the
assertion was blind in exactly the population it was needed for, and a hardcoded constant stood
in for a lookup. `util_raku_entry_grade.sh`, written an hour later, reads the sidecar, and
found this on its first regression sweep over all 49 entries the row had landed. **An
instrument that catches its author's own defect is the only kind that has actually been shown
to be stricter than what it replaced.**

⭐ **AND ONE MORE SHAPE, FROM THE SAME SWEEP: REPAIRING A FAULTY TEST DOES NOT ALWAYS REDUCE
THE RED COUNT.** Raku requires a comma after a block argument — `grep({ $_ > 2 }, 1..5)` —
which rakudo runs and we answer with `raku parse error line 1: syntax error`. Repairing those
four entries would move the failure from the corpus to the compiler. That is the *right* place
for it, but it is not a flip, and landing the repair without the cure would convert a marked
xfail into an unmarked red. They stay marked; the frontend row carries them.
