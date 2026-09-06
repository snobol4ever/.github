# The package-inventory declaration matcher was nondeterministic, and two of the gate arms written to catch it were wrong first

**hq_T · 2026-09-06 ~09:1x–10:0x CDT · FLEET-12 · SCRIP `247ed5e88` `b284499f3` `27a6b82bb` `90c1d3562` `ca867d182` `8e63484b3`**

Row `every-package-runner-prints-shipped-graded-ungraded-and-ungradable-and-the-leaderboard-carries-the-inventory` (rank 0, THE PACKAGE LOCKDOWN, Lon 2026-09-06: *"Fix the never graded business."*). All numbers below were produced by the commands shown, on the trees named in the commits.

## 1. Five runs, identical code, identical tree, five different answers

`lib_inventory.sh` tested "is this declared program actually shipped?" with

    printf '%s\n' "${found[@]}" | grep -qxF "$nm"

Every package runner sets `pipefail`. `grep -q` exits at the first match and closes the pipe; if `printf` is still writing it takes `EPIPE`, dies on `SIGPIPE`, and the pipeline reports **141**. Whether `printf` has finished is a **race**.

Measured over `corpus/packages/icon/ipl`, five consecutive runs, nothing changed between them:

| run | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| "declared but not shipped" | 127 | 137 | 139 | 125 | 138 |

**Every one of those was false.** All 211 named files are shipped.

⛔ **The severity is not the wrong count, it is which arm was disabled.** This is the arm that catches a **stale declaration** — a ruling that no longer names a file, which silently withdraws a guarantee. Under the race it accused ~130 live files per run, so a genuine stale entry was indistinguishable from noise and the correct human response to the refusal was to *disbelieve it*. hq_I had independently reached that conclusion and left arizona and ipl unwired, which was the right call on the evidence available to them.

⭐ **The general form: `pipefail` converts an optimisation into a failure.** `grep -q`, `head`, `find | head -1` — every early-exit consumer can `SIGPIPE` its producer, and `pipefail` then reports that as the pipeline's status. It is invisible whenever the producer's output is small, which is every fixture anyone writes.

## 2. Two more defects in the same matcher, both silent

- **Path-blind.** The census indexed **basenames**; arizona and ipl declare **paths**. ipl's 390 `procs/…`/`gprocs/…` declarations could never match anything (hq_I measured 424 of 645 Icon declarations reading as not-shipped). Cured by indexing package-relative path *and* basename, a bare name accepted only while unique — ipl ships four colliding basenames (`gener`, `morse`, `repeats`, `spokes` across `procs/`, `progs/`, `gprocs/`, `gprogs/`), two of them already declared, so a bare ruling would land on whichever file the census reached first.
- **Our own generated `ALL.<ext>` master was counted as a shipped VENDOR program.** Four packages carry one (`ipl`, `aisnobol`, `csnobol4_suite`, `gimpel`). It inflates `shipped` by exactly one and makes the load-bearing SUM **unreachable by one, forever** — a lane grades every vendor program and still refuses.

⭐⭐ **That third one was the whole of a two-instrument disagreement, and neither instrument was wrong.** hq_I's Icon runner reported ipl `shipped=851`; the shared body reported `852`. hq_I excludes `ALL.icn`; the body did not. Two correct instruments answering two different questions, **and neither could say so** — the disagreement surfaced only as a number that would not reconcile. With it cured, ipl reads `shipped=851 graded=64 ungraded=211 ungradable=390`, delta **186**, matching hq_I's independently derived 186 **to the unit**. Two instruments built from opposite ends agreeing exactly is worth more than either number alone.

## 3. ⭐⭐ The arms written to catch this were wrong twice, and only running them against the known-bad code found it

**First draft — 600 short names, agreement over five runs. It PASSED against the code that was known to be broken.** The witness needs **two** ingredients: the name list must exceed the **64K pipe buffer** *and* the match must be **early**. With the existing three-file fixtures `printf`'s whole output fits in one buffer, it never blocks, `EPIPE` never happens — which is exactly why **eleven existing arms passed over this defect on the day they landed**. The working witness is 800 names × 90 chars = 72000 bytes, declaration matching `find`'s first entry: 5/5 false refusals pre-cure, 5/5 clean post-cure.

**Second draft — agreement only. It passed again.** On the big fixture the bad body is **5/5 *identically* wrong**. ⛔ **Stability alone is satisfiable by being consistently wrong.** It is unstable at ipl's scale and stable at the fixture's; both are the same bug, and only an arm asserting *agreement **and** correctness* sees both.

⭐ Both drafts were caught by one habit: **run a new gate arm against the known-bad code before landing it.** This is hq_I's rule from the arizona determinism case the same morning — *a check that cannot fail for the reason you are asking about is not a weak check* — and the reason it must be a procedure rather than an intention is that **both drafts printed exactly the string a passing arm prints**. hq_I's companion warning is taken too: the arm runs five **independent** invocations, never a back-to-back pair, because a determinism check whose two passes share a process cannot fail for the reason it is asking about.

## 4. The census was wrong about the one caller doing everything right

`ARM 11` grepped for the stanza and printed `wired=N` — counting runners that *could* emit a line, not runners that *do*. hq_I: *"those differed for every runner wired so far."* jcon is the worked case: it sourced the body, called it, counted as wired, and **could not emit a line at all** — its `UNGRADED.tsv` was 2-column and its call swallowed the refusal into a warning.

Static analysis cannot prove emission; only running the runner does. So the fix was not a cleverer grep but **three tiers that are decidable from the source, plus the gap named**: `sources` / `complete-stanza` / `unwired`, with two previously-invisible lists — INCOMPLETE STANZA (wired to refuse, not to report) and SWALLOWS THE REFUSAL (`inventory_line … || echo`, where rc=2 becomes a warning nobody reads).

⭐ **And the new census found a false positive in itself within minutes.** It judged `board_packages.sh` — an **aggregator**, which correctly sets no stanza and emits no line — as *"sources the body with an INCOMPLETE STANZA, wired to REFUSE."* **A census over the wrong population is wrong for every member of it, and it is loudest about the members that are most correct.** Same shape as the defect it had just been rewritten to cure, one commit later.

## 5. The reason-code vocabulary, and why the legacy map is not optional

Three lanes invented three vocabularies in one morning — `CONTAINER_OR_LIBRARY`, `NO-ORACLE-SHIPPED`, `EMPTY`/`ORACLE_FAIL` — in dashes and in underscores, for the same handful of situations. Ruled closed (`INV_CLASS_UNGRADABLE` / `INV_CLASS_UNGRADED`).

⭐ **The ruling is not mainly a spelling: the two files answer two different questions.** UNGRADABLE names **what the oracle did** — a ruling, disputable, nobody owes work. UNGRADED names **what is owed** — a task, claimable. So an UNGRADED class naming an *observation* is ARM 8's defect one size down: 106 ipl rows say `EMPTY` in the class and *"needs a .in … not yet authored"* in the reason. **The file already knows what is owed and the column a reader sorts by does not.** A lane cannot pick up 106 rows of `EMPTY`; it can pick up 106 rows of `NEEDS_STDIN_FIXTURE`.

⭐⭐ **The legacy map earned its keep within the hour, and on a case the ruling got wrong — not on old debt.** hq_I cured jcon concurrently and wrote `NEEDS_MULTIFILE_LINK`, a good precise name invented in good faith minutes after the vocabulary closed. With a bare *"unruled classes refuse"*, that freshly-correct file refused rc=2 and a lane delivering exactly what Lon had ordered would have been red-lit — **and would have been right to route around the ruling rather than obey it.** The class stays coarse (the bucket a lane sorts by) and the reason column carries the specificity; a vocabulary growing a member per situation is the every-lane-invents-a-spelling problem wearing a tidier hat. **A closed vocabulary is only safe to close mid-flight if it ships with the mechanism that absorbs a collision without stopping anyone.**

## 6. The leaderboard was transcribing a population it could not see go stale

`PACKAGE_SHIPPED` held three integers typed into `util_score_row.py` by a reader of somebody else's board. ⛔ **A transcribed denominator cannot go stale loudly** — it goes stale silently and every percent over it stays plausible. Measured live: the icon V cell says arizona has **"35 never graded"**; the runner's own line says `ungraded=0 ungradable=34`. **Neither number is 35.** The cell was right when written and nothing told it when it stopped being.

The V cell now carries the runner's own `PACKAGE_INVENTORY` line and the reader prefers it, with the runner's own `shipped`/`graded` becoming legal denominators **without a code edit** — a reader that only accepts numbers it was told about in advance cannot follow a live census. A clause whose buckets do not sum is **dropped and reported**: a sum that held at the runner and not in the cell was transcribed, and re-running the runner is the cure, never editing the digits.

⛔ **Not done, and named rather than implied:** the arizona/jcon clauses were **not** written into the live `SCORE.md`. Both packages now produce green summing lines, but the `graded` counts on hand came from hq_I's message, not from a runner this session ran — pasting them would be the same transcription the carriage removes, one level up.

## 7. What the reader should take

1. **`pipefail` + any early-exit pipe consumer is a latent nondeterminism**, invisible at fixture scale. Prefer a shell-native set to a `printf | grep -q` membership test.
2. **Prove a new gate arm fails against the known-bad code before landing it.** Two of these did not, and both printed the string a passing arm prints.
3. **Stability alone is satisfiable by being consistently wrong.** Assert agreement *and* correctness.
4. **A census over the wrong population is loudest about its most correct members.**
5. **When two instruments disagree by a small constant, look for a definitional difference before looking for a bug** — here, one file, and both instruments were right.
