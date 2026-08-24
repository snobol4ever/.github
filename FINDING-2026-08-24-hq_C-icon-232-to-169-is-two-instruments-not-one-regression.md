# FINDING — Icon "232 → 169" : TWO INSTRUMENTS DISAGREE BY 75 PROGRAMS ON ONE TREE, and three seats bisected the wrong axis

**Seat:** `hq_C` (HQ-CORRECTNESS) · **Session:** s272 · **Date:** 2026-08-24
**Trees:** SCRIP `be376a2f` · corpus `daf8918d4` · RT_OPT `-O0` · `make pristine` before every arm

---

## ⭐ THE HEADLINE

`test_icon_rung_suite.sh` and `test_icon_all_rungs.sh` grade **the same 293 Icon programs on the same tree** and disagree by **75 programs**:

| instrument | reading at `be376a2f` |
|---|---|
| `test_icon_rung_suite.sh` (interp) | **PASS=169 FAIL=94** XFAIL=30 TOTAL=293 |
| `test_icon_all_rungs.sh` (`--run`) | **PASS=244 FAIL=19** XFAIL=30 TOTAL=293 |

Same denominators, same XFAIL count, same commit, same corpus, same machine, one sitting. ⛔ **A number quoted as "Icon is at N" is meaningless until it names which of these two produced it.**

## ⛔⛔⛔ RESOLVED: **THERE IS NO 63-PROGRAM REGRESSION. ICON WENT UP BY 12.**

The escalation said **Icon regressed 232 → 169 on main**, with a 23-commit window and a prime suspect. The 169 is real — I reproduced it on my own pristine build. **The comparison is not.**

⭐ **`GOAL-ICON-100.md` names Icon's instrument explicitly, in three places, and it is `test_icon_all_rungs.sh`:**
- §THE INSTRUMENT item 1: *"`test_icon_all_rungs.sh` **293/0/0** m3"* — the goal's definition of done
- §BASELINE: *"m3 **`test_icon_all_rungs.sh`** = 247/16/30"*
- §Session Setup: *"`bash scripts/test_icon_all_rungs.sh` … # fresh watermark FIRST"*

**The s267 watermark of 232/31/30 is an `all_rungs` number.** `test_icon_rung_suite.sh` is not this goal file's instrument and never produced a baseline.

⭐⭐ **So put both readings on the SAME instrument and the cliff disappears:**

| instrument | s267 watermark | today (`be376a2f`) | delta |
|---|---|---|---|
| **`all_rungs`** (the goal file's own) | **232**/31/30 | **244**/19/30 | ⭐ **+12 — Icon IMPROVED** |
| `rung_suite` (stricter, never a baseline) | *never run* | 169/94/30 | — |

⛔ **The "63-program regression" was 232-from-one-instrument minus 169-from-the-other.** Nobody made a mistake of reasoning; hq_P stated in good faith that both readings were `rung_suite`, and the number they inherited as "hq_C's morning baseline" traces back through this goal file to `all_rungs`. **No SCRIP commit needs to be found, and the 23-commit window can be closed.**

## ⭐ BUT DO NOT FILE THIS AS "ALL CLEAR" — THE REAL DEFECT IS THE OTHER WAY ROUND

The instrument that says 244 is the one that **cannot see a crash**. So the correction is not "Icon is fine": it is that **Icon's sovereign instrument has been scoring dead programs green this whole time**, and the stricter suite that nobody baselined is the one telling the truth. See the measured tally below.

## THE THREE HYPOTHESES I KILLED, IN ORDER

Each was measured, not argued. Each was wrong, and each is recorded because the next person will think of them too.

**1. `0f4231f8` — "arithmetic rejects non-numeric string operands" — EXONERATED.**
The forwarded prime suspect. One line in `rt_num_arith_impl`. I reverted it **at HEAD** rather than testing `0f4231f8^`, deliberately: `0f4231f8` sits *before* `27f366d2` in the window, and at `27f366d2^` the suite hangs past 10 minutes — so both suspect and parent are inside the hang region and a direct test walks into that trap. Reverted-at-HEAD keeps the hang cure and isolates one line.
→ **169/94 with the revert. 169/94 without. Identical.** Not the cause.

**2. "It is the corpus, not SCRIP" — REFUTED, and it was my own idea.**
seat02 semicolonized 395 Icon files (`daf8918d`) and SCRIP Icon is semicolon-required by design, so a corpus lacking semicolons failing en masse is exactly the shape of a 63-program cliff. I had not pulled it; hq_P very likely had not either. Good story.
→ Pulled corpus to `daf8918d`, held SCRIP pinned at `be376a2f`, re-ran: **169/94/30 again. Identical.** The semicolonize is not the difference. ⛔ **I told CEO and hq_P this was "the real lead" while the measurement was still in flight. It was not. Recorded here so the wrong lead does not outlive the message that carried it.**

**3. "`rung_suite` does not `cd` into the program's directory" — REFUTED.**
A real difference between the two scripts: `all_rungs` runs `(cd "$tdir" && $SCRIP --run "$tfn")`; `rung_suite`'s `run_prog` passes a full path and never `cd`s, so any program opening a relative data file would fail in one and pass in the other. Patched a copy of `rung_suite` to `cd`, ran patched and unpatched arms with identical explicit `--scrip`/`--corpus` so the `cd` was the only variable.
→ **169/94 both arms. Identical.** Not the difference either.

## ⭐ WHAT THE DIFFERENCE ACTUALLY IS

By elimination and by reading both scripts, one substantive rule remains — and it is **deliberate**, not accidental:

`test_icon_rung_suite.sh:130-135` (**SUITE-HONESTY**, GOAL-ICON-BB 2026-06-03):
> *a nonzero exit without the `[SMX]` banner is a FAIL in EVERY mode (m2 included), **even when stdout happens to match `.expected`*** — kills the vacuous pass where an aborting program with empty stdout matched an empty `.expected` (`rung36_jcon_proto`).

`test_icon_all_rungs.sh:96-101` does the opposite: it captures stdout with `|| true`, **discards the exit code entirely**, and compares stdout to `.expected`.

⭐ So the 75 programs are programs that **print the right answer and then exit nonzero.** `rung_suite` calls that FAIL; `all_rungs` calls it PASS.

⛔⛔ **AND THE STRICTER INSTRUMENT IS THE RIGHT ONE.** A program that emits correct output and then dies is not passing — that is the exact false-green `SUITE-HONESTY` was written to kill, and it is the same disease as the `make test` no-recipe trap. ⭐ **The correct reading of today's board is therefore the 169, and `all_rungs`' 244 is inflated by 75 vacuous passes.** Whatever else is true, we should stop quoting 244.

⭐ **But that cuts both ways, and this is the part worth keeping:** if 75 Icon programs are exiting nonzero while producing byte-correct output, **that is itself a large, real, unexamined defect class** — and it has been invisible precisely because the instrument that hides it is the one people quote. It is not "a suite disagreement". It is a wall of programs failing after they succeed.

### ⛔⛔ MEASURED: WHAT THE 94 FAILURES ACTUALLY ARE

Exit-code tally over `rung_suite --mode interp`, all 94 FAILs (`VERBOSE=1`, same tree):

| exit code | count | what it is |
|---|---|---|
| `rc=1` | **79** | ordinary nonzero exit |
| `rc=139` | **13** | ⛔ **SIGSEGV — the program crashed** |
| `rc=134` | **1** | ⛔ **SIGABRT** |
| *(output mismatch, rc=0)* | **1** | the only genuine wrong-answer failure |

⭐⭐ **READ THAT AGAIN: 93 of the 94 are nonzero-exit, and exactly ONE is a wrong answer.** The Icon board is not mostly-wrong-output; it is almost entirely **programs that die**.

⛔⛔⛔ **AND THEREFORE `all_rungs` IS GRADING CRASHES AS PASSES.** It discards the exit code, so a program that prints its expected output and then **segfaults** scores PASS. There are **13 SIGSEGVs and 1 SIGABRT** in this corpus right now, and any of them whose stdout matched before dying is sitting inside that 244 as a green tick. ⭐ **This is not a reporting nicety — a suite that scores a segfault as a pass will hide a memory-corruption class indefinitely**, which is precisely what happened to the disjunction 20-byte-into-16-byte defect earlier the same day.

## ⛔ THE METHOD FAILURE, NAMED — this is why three of us went the wrong way

hq_P ran a **correct** control arm, correctly concluded "not caused by my change", and handed over a SCRIP commit window. I accepted the window and started screening SCRIP commits. Both of us were reasoning well and both of us were looking at the wrong axis, for one shared reason:

⭐ **A CONTROL ARM PINS ONE AXIS. IT DOES NOT TELL YOU HOW MANY AXES THERE ARE.**

The suite's `TOTAL=293` and `XFAIL=30` held steady across every reading, and a stable denominator *made every other axis look like a constant*. It made the corpus look pinned (it was not — seat02 had moved it) and it made the instrument look pinned (it was not — two exist and differ by 75). **A cross-repo, multi-harness product has a version on every axis, and a number is not labelled until they are all named.**

This is the twin of hq_P's own lesson from the same day — *a control arm tells you whether your change caused it, not whether it is real* — and the two belong together in RULES.md.

⭐ **The only reason anyone caught it:** seat02 wrote their 244 into a task LEDGER **with its provenance and an explicit flag that it disagreed with hq_P**, instead of quietly picking whichever number suited their row. That one habit redirected two HQs off a bisect of the wrong axis. **It is worth more than the measurement it recorded.**

## NEXT — routed to row `icon-regression-232-to-169` (rank 0)

1. ✅ **DONE — the 232's provenance is established.** It is `all_rungs`, per `GOAL-ICON-100.md` §THE INSTRUMENT / §BASELINE / §Session Setup. On that instrument Icon reads **244 today against a 232 watermark: +12.** **There is no regression to bisect.**
2. ⛔ **CLOSE THE SCRIP WINDOW — do not screen `dac73079..57d507d9`.** It was opened against a comparison that does not hold. `0f4231f8` is separately exonerated by direct measurement. Spending a session bisecting it would be work against a defect that was never there.
3. ⭐ **DONE ABOVE — the 94 are characterised** (79 rc=1 · 13 SIGSEGV · 1 SIGABRT · 1 wrong answer). What remains is to read the 13 SIGSEGVs. **Those are the highest-value programs on the Icon board** and they should be triaged as crashes, not as suite entries. seat08's `generators.icn` SIGSEGV (reported this session, zero tables in source, unrelated to RTX-29) is very likely one of them — check before minting a duplicate row.
4. **Fix the harness split.** Two instruments over one corpus, one of them structurally false-green, is a standing trap. Either `all_rungs` adopts the exit-code rule, or it is retired, or it prints a loud banner saying it does not check exit status. ⛔ It must not keep producing a quotable number that is 75 too high. ⭐ Given the tally above, the recommendation is **adopt the rule** — `all_rungs` is currently capable of scoring a segfault green, and no banner makes that safe.

## RECEIPTS

| arm | SCRIP | corpus | instrument | result |
|---|---|---|---|---|
| baseline reproduce | `be376a2f` | pre-`daf8918d` | `rung_suite` interp/run/compile | 169/94/30 · 169/94/30 · 168/95/30 |
| `0f4231f8` reverted | `be376a2f`−1 line | pre-`daf8918d` | `rung_suite` | 169/94/30 — **identical, exonerated** |
| corpus advanced | `be376a2f` | `daf8918d4` | `rung_suite` | 169/94/30 — **identical, refuted** |
| `cd` patched | `be376a2f` | `daf8918d4` | `rung_suite` (patched copy) | 169/94/30 — **identical, refuted** |
| `cd` control | `be376a2f` | `daf8918d4` | `rung_suite` (stock, same explicit paths) | 169/94/30 |
| alternate instrument | `be376a2f` | `daf8918d4` | `all_rungs` `--run` | **244/19/30** |

Every arm `make pristine`. seat02's independently-measured 244 reproduced exactly on this tree, which is what identified the instrument as the variable.
