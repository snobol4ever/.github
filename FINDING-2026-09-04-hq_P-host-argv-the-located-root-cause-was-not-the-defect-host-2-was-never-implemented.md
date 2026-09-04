# FINDING — `HOST()` argv: the row's located root cause was NOT the defect. `HOST(2,·)` was never implemented at all, and `HOST(3)` was a hardcoded `0`

**Seat:** hq_P (PERFORMANCE) · **Date:** 2026-09-04 · **Mode:** QUARTET, SNOBOL4-ONLY (Lon 17:37/17:41)
**Row:** `snobol4-host-argv-not-staged-for-zero-param-entry` (rank 2, minted by seat08) — a blocker of my own lane row
`snobol4-csnobol4-suite-non-pass-censused-by-class-and-cured` (csnobol4_suite `genc.sno`).
**Tree:** landed at SCRIP `1d31e2963` · corpus `06a77479c` (pushed) · .github with this FINDING
**Oracles:** csnobol4 `/home/resources/csnobol4/snobol4` and SPITBOL `/home/resources/x64/bin/sbl -bf` (grading arm), both by absolute path.
**Build:** incremental `make` (RULES.md:118 loosening), `RT_OPT=-O0`.

## 1. The row's root cause was real, but it was not what made the witness fail

The baton located the defect precisely and confidently, in `src/driver/scrip.c`: `rt_main_args_stage()` is called only
behind `if (_nparams >= 1)` / `if (sbbg->nparams >= 1)`, a gate that answers an unrelated question. That reading is
correct as far as it goes, and the gate IS a defect — but it is **not why the witness printed `argc=0`**.

⭐ **The control arm is one line and it refutes the diagnosis outright.** If the `nparams >= 1` gate were the cause,
the same program with a parameterised entry would work. It does not:

```
./scrip --run h.sno -- v311.sil          (zero-param entry)   -> argc=0 / arg1=
./scrip --run m.sno -- v311.sil          (DEFINE('M(X)') entry) -> argc=0 / arg1=      <- IDENTICAL
```

The actual defect is in `src/runtime/core/core.c` `_HOST_()`, and it is much simpler than the row supposed:

```c
if (selector == 3) return INTVAL(0);      /* hardcoded — never consulted argv at all */
/* ...and there was NO `selector == 2` arm anywhere in the function. */
```

`HOST(3)` returned a constant `0` and `HOST(2,i)` fell through to the function's final `return NULVCL`. **Staging was
irrelevant: nothing downstream ever read it.** Fixing only the gate the row names would have changed nothing
observable, and the row would have closed on a witness that still printed `argc=0`.

⛔⭐ **THE TRANSFERABLE SHAPE — A ROOT CAUSE FOUND BY READING IS A HYPOTHESIS, NOT A MEASUREMENT.** Every word of the
baton's analysis is true; it was arrived at by reading the driver, and the driver really does carry a wrong gate. What
was never done was the one cheap experiment that *discriminates* — run the shape the diagnosis predicts will work. This
is the same class as the `CSN_NO_SEGV_HANDLER` entry in CLAUDE.md (a correct procedure with a false explanation) and
the `command -v` oracle probe (an instrument answering a narrower question than the one intended): **the evidence
appeared to confirm the reading because the reading was never given a chance to fail.**

## 2. The contract, measured on both oracles rather than assumed

```
$ snobol4 probe.sno alpha beta          $ sbl -bf probe.sno alpha beta
host3=2                                 host3=3
arg[0]=/home/resources/csnobol4/snobol4 arg[0]=/home/resources/x64/bin/sbl
arg[1]=probe.sno                        arg[1]=-bf
arg[2]=alpha                            arg[2]=probe.sno
arg[3]=beta                             arg[3]=alpha
first-failing-index=4                   arg[4]=beta / first-failing-index=5
```

Both dialects agree in shape, and it matches the SPITBOL manual (`.tools/docs/spitbol-manual-v3.7.txt:6926`):
*"HOST(3) returns the index of the first unused argument, and HOST(2, i) retrieves argument i."*

1. `HOST(2,i)` indexes the **whole command line**, `i=0` being the interpreter binary — not a user-args-only vector.
2. `HOST(2,i)` **FAILS** (not null) past the end. `genc.sno:37` depends on exactly this: `OPTLOOP ARG = HOST(2,IND) :F(NOFILE)`.
3. `HOST(3)` is an **INDEX into that vector**, not a count.

## 3. The cure — three files, and NO new global

- `src/runtime/core/core.c`: added `host_cmdline_arg()` (reads `/proc/self/cmdline`, streaming, no buffer and no
  static) and implemented `selector == 2` (→ `FAILDESCR` past the end) and `selector == 3`.
- `src/runtime/by_name_dispatch.c`: added `rt_main_args_count()` — a **pure function over state that already exists**,
  reading the staged list's own `frame_size` field. No new variable.
- `src/driver/scrip.c`: removed the four `nparams >= 1` gates (the row's original defect — genuinely wrong, and now
  load-bearing, because the staged count is what makes `HOST(3)` exact).

⭐ **`HOST(3)` is derived, not sniffed:** `first_unused = (count of /proc/self/cmdline entries) − (count of user args
the driver staged)`. The driver stages exactly the user args in both modes (m3: the post-`--` tail; m4: `argv+1`), so
the subtraction is **true by construction in both modes** with no `--`-sniffing special case, and it degrades safely:
if staging never happened the count is 0, so `HOST(3)` points one past the end and `HOST(2,·)` fails cleanly.

**Verified in all three shapes** (m3 with args, m3 with none, m4 standalone binary):

```
m3  ./scrip --run probe.sno -- alpha beta   host3=4  arg[4]=alpha  first-failing-index=6
m3  ./scrip --run probe.sno                 host3=3  (== past the end: HOST(2,3) fails at once, correct)
m4  ./probe.bin alpha beta                  host3=1  arg[1]=alpha  first-failing-index=3
```

## 4. The consumer moved, which is the result that matters

`genc.sno` under the upstream invocation (`Makefile:145`, inputs `v311.sil`/`globals`/`procs` from `/home/resources/csnobol4`):

- **Before:** SILPATH empty → opened nothing → EOF at once → **0 bytes**.
- **After:** reads the SIL file and generates output; **the first 47 bytes are byte-identical to the csnobol4 oracle's**
  (`/* generated from v311.sil by genc.sno on  */`).
- With `--with BLOCKS` (the Makefile's own `cat with` args), SCRIP now reproduces the oracle **exactly**, including the
  diagnostic: both print `genc.sno: unknown option --with` and nothing on stdout.

⚠️ genc is **still not gradeable**, for reasons that are not this row's and not SCRIP's: the **oracle itself** fails on
this input (`genc.sno:766: Error 24 ... Undefined or erroneous goto` at statement 568), i.e. the vendored `genc.sno` and
`v311.sil` are mismatched versions. SCRIP diverges from the oracle further in and then runs past 600 s — **a new class,
behind the one this row cured, not a regression.** Not minted here; it belongs to the genc harness/fixture row.
⚠️ Also observed, not chased: on the `--with` arm the oracle exits **rc=1** and SCRIP **rc=0** (existing row `error-code-parity`).

## 5. ⛔ THE ROW'S DONE-WHEN IS WRONG AND MUST NOT BE SATISFIED — it encodes a contract no implementation has

The DONE-WHEN requires, from `./scrip --run h.sno -- v311.sil`:

```
argc=2      (HOST(3))          arg1=v311.sil   (HOST(2,1))
```

That asks `HOST(3)` to be a **count** and `HOST(2,·)` to index a **user-args-only vector**. Neither oracle behaves that
way, and the row's own GOAL text disagrees with its own DONE-WHEN (the prose predicts `argc=1`, the check demands `2`).

⛔⭐ **Satisfying it would have closed the row while leaving the defect uncured, and would have broken the very program
the row exists to unblock.** Under those semantics `genc`'s `IND = HOST(3)` yields 2, `HOST(2,2)` fails immediately,
and genc dead-ends at `NOFILE` — exactly the symptom being cured. **A green DONE-WHEN would have been the failure.**
This is the "readable and wrong" shape the SCORE.md column-semantics gate exists for: the check parses, runs, and
returns a clean verdict on the wrong question.

**I did not edit the DONE-WHEN** (a lying test is the `make test` trap in another hat, and the row is not mine to
re-pin). The row stays **OPEN** with the cure landed. Proposed replacement, which grades the measured contract and
which the landed cure passes — for ceo/hq_T to re-pin:

```bash
bash -c 'set -eu; cd "$S4E_HOME/SCRIP" || exit 2; W=$(mktemp -d); trap "rm -rf \"$W\"" EXIT;
printf "\tIND = HOST(3)\n\tOUTPUT = \x27a=\x27 HOST(2,IND)\n\tOUTPUT = \x27b=\x27 HOST(2,IND + 1)\n\tHOST(2,IND + 2)\t:S(BAD)F(OK)\nBAD\tOUTPUT = \x27NO-FAIL-PAST-END\x27\nOK\nEND\n" > "$W/h.sno";
out=$(timeout 8 ./scrip --run "$W/h.sno" -- alpha beta </dev/null 2>&1) || true;
printf "%s\n" "$out" | grep -q "^a=alpha$" && printf "%s\n" "$out" | grep -q "^b=beta$" && ! printf "%s\n" "$out" | grep -q "NO-FAIL-PAST-END" || { echo "REFUSED: got: $out"; exit 1; };
echo "HOST(3)/HOST(2,i) match the oracle contract incl. failure past the end"; exit 0'
```

## 6. Found in passing and cured: a live CRLF re-infection source pointed at MY OWN lane

`make test` was **red on origin** at `test_gate_our_files_are_lf` — `corpus/tests/raku/ALL.csv`, 5 CRLF lines, already
in HEAD (`33045cf84`), inherited and blocking every seat's blocking set. Stripped in its own commit with the proof the
gate demands (HEAD's bytes with CRs stripped == the new bytes; line count unchanged).

⭐ **The residue was the symptom; the generator was still infected.** `util_build_master_suite.py` had been cured (all
4 writers carry `lineterminator="\n"`), but `scripts/util_build_package_suite.py:228` — **added in today's pull** —
still used a bare `csv.writer(f)` with `newline=""`, whose default terminator is `\r\n`. That script writes the
**package** suites' CSVs, i.e. `csnobol4_suite` — my own lane. Cured there too, so the next regeneration cannot
re-infect. ⛔ **A data fix without the generator fix would have been a band-aid that reappears on the next rebuild.**

## 7. Control arm — and TWO reds on the master board, BOTH inherited, both proven so rather than assumed

Board on the landed tree (`test_corpus_snobol4.sh`, denominator **1760**, `xfail=61`):
**m3 PASS=1720 FAIL=2 · m4 PASS=1720 FAIL=1 SKIP=1** — the gate exits **RED** on the m4 red.

⛔ **The board is RED on origin, and it was red before I touched it.** I proved this the only way that settles it:
built origin's tip `cfde5756f` (the commit my work rebased onto, *without* my commits) in a separate worktree outside
the seat root, and ran both failing entries there. **Byte-identical output on both.** Neither red is mine.

| entry | mode | status |
|---|---|---|
| `simple_output_276` | m3 | pre-existing `FATAL lower_snobol4 (GZ#5 subset)` — pattern replacement is outside the landed subset |
| `user_function_len_defer_branch_6` | m3 + m4 | ⛔ **a REGRESSION that arrived on origin during this session** |

⛔⭐ **`user_function_len_defer_branch_6` is the one that matters and it is not in my row.** The entry has been in the
master since `11a36c87f` (08-29/30) and was passing; it fails now on origin. It is the deferred-lambda target
(`p = LEN(1) . *(n = n + 1)`) that seat08 reported landing to me this session as *"default-propagate-failure (a lambda
that FAILS at evaluation fails the whole match)"*. The oracle disagrees with the landed behaviour:

```
sbl -bf : before / nomatch n=1        <- the match FAILS
SCRIP   : before / after n=1 dummy=[] <- the match SUCCEEDS
```

**This reds `make test` for every seat** (the m4 arm is the blocking one). Reported to ceo; not cured here because
this landing is a different row and I will not fold an unrelated semantic change into a verified cure.

⭐ **Ruled out on the record, because it was the live risk in my own change:** removing the `nparams` gates makes
`rt_main_args_stage()` run for every program, and it writes `g_call_args[0]`. `user_function_len_defer_branch_6` is a
user-function-argument test, so that was the obvious suspect. `SCRIP_NO_MAIN_ARGS=1` (which skips exactly that write)
produces **identical output**, and the baseline worktree fails identically with no staging change at all. Not the
mechanism.

`make test` was **rc=0 green** on the pre-rebase tree; `test_gate_our_files_are_lf` (5077 files, 0 CRLF) and
`strip_comments.py --check` (0 comments) are green on the landed tree.
