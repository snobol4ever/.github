# FINDING 2026-09-04 hq_T — a cure applied to one copy of a guard never reaches the others: five skip-as-success arms survived in four suite runners beside a sibling cured of the identical pair

**Row:** `harness-and-ladder-runner-refuse-on-a-stale-binary-like-the-artifact-regen-does` (ceo → hq_T, rank 1).
**Found while:** wiring the stale-binary preflight into every suite runner and writing the census arm that proves all of them carry it.

## What the row asked, and what the census turned up on the way

The row extends `gate_require_fresh` (lib_gate.sh, hq_B `4c7253e99`) — until now called by **one** production script, `test_corpus_snobol4.sh` — to the ladder body, the Python harness and the vendor-suite runners, so no board can grade a binary older than the tree whose SHA it stamps on the verdict. The witness was ceo's own pair of false-red audits in one day (a fetched-not-merged clone at 12:23; a 10:57 binary at 14:03 that read RED and then GREEN after nothing but an incremental `make`).

Wiring it needed a denominator: **which scripts grade with `$SCRIP`?** `grep -l '"$SCRIP"' scripts/test_*_suite.sh` → **20**. Reading the anchor line of each — the existing "is scrip built?" guard the preflight lands beside — found this, in non-comment code:

| runner | guard | exit |
|---|---|---|
| `test_gc_stress_suite.sh:36` | `SKIP scrip not built` | **0** |
| `test_snobol4_pat_rung_suite.sh:11` | `SKIP scrip not built at $SCRIP` | **0** |
| `test_snobol4_pat_rung_suite.sh:9` | `SKIP pattern dir not found at $PATDIR` | **0** |
| `test_prolog_rung_suite.sh:50` | `SKIP scrip binary not found at $SCRIP` | **0** |
| `test_prolog_rung_suite.sh:54` | `SKIP corpus not found at $CORPUS` | **0** |
| `test_swi_suite.sh:11` | *(no guard at all; default `SCRIP=./scrip`, cwd-relative)* | — |

Five arms in four runners that **report SUCCESS from a run that graded nothing** — the exact defect `lib_gate.sh`'s header names as the reason it exists (*"31 of 105 gates COULD NOT SAY NO"*), and that RULES.md forbids outright (*a test that cannot measure REFUSES with rc=2 — never skip-as-success*).

⭐ **The part worth a FINDING is the sibling.** `test_icon_rung_suite.sh` is `test_prolog_rung_suite.sh`'s structural twin — same two guards, same shape — and it was **already cured**, with a 5-line header explaining the ABSENT-ORACLE FALSE-GREEN class in full (*"These two arms printed SKIP and exited 0, so a box with no compiler built, or no corpus cloned, reported SUCCESS to every caller that reads $?"*). The cure was correct, well-explained, and **stopped at the file it was applied to**. The Prolog twin kept both arms.

## The class, stated once

This is the same shape as the row's own motivation, one level down. The staleness rule existed twice in bash (`gate_require_fresh`, `assert_binary_current`); ceo cured a wrong basis in one (`3d12ca54` — *"IT IS NOT A SUPERSET, IT IS WRONG"*), the cure never reached the other, and the identical defect was cured a second time nine days later (`4c7253e99`). Here: the skip-as-success guard existed in N runners; one was cured with a paragraph of rationale; four kept it.

⛔ **A cure applied to one copy STRENGTHENS everyone's belief that the class is dead while the other copies keep the bug.** The cost of a copy is never the duplicated lines. It is that the cured copy's header now reads as the org's position on the matter, and nobody greps for what the header says was fixed.

⭐ **The instrument that finds this is a census with a printed denominator, never a fix.** The cured Icon twin could not have found the Prolog twin — it does not know it has one. `grep -l '"$SCRIP"'` did, in one line, because it asked *who else grades* rather than *is this one right*. That is the whole difference between a cure and a gate.

## A second, smaller lesson: the gate arm that caught it was wrong first

The acceptance gate's ARM 11 first checked for skip-as-success **textually** — `grep 'SKIP scrip not built'`. Its only two hits were the **cure comments** this row had just written into two runners, quoting the very code they had deleted; meanwhile the live uncured arm one line above (`SKIP pattern dir not found`; `exit 0`) matched nothing and went unnamed. A textual arm cannot tell a fixed defect from a description of one. Rewritten to strip comment lines and match the behaviour (an `echo SKIP` followed by `exit 0`, same-line or multi-line), it found the live arm at once. ⭐ **An arm that greps for a string is a statement about what the file SAYS; the gate needs a statement about what the code DOES.**

## Cures landed in this row (SCRIP)

* `scripts/util_require_fresh.sh` — the one-line preflight, **zero staleness logic**, sources `gate_require_fresh`; `--gate <name>` names the caller in the refusal. Python reaches the same bash function through it, so copy number three — in a second language, invisible to any grep for the bash symbol — never exists.
* `lib_ladder.sh` (all seven ladders), `corpus_suite_harness.py` (`check_scrip` → `require_fresh`), and all **20** `$SCRIP`-grading `test_*_suite.sh` runners call it.
* The five skip-as-success arms above → `rc=2` with a named cause. `test_swi_suite.sh`'s cwd-relative default → derived from the script's own location like every sibling.
* `lib_gate.sh`: the refusal named `src/src/parsers/...` (the `<src-subdir>/` prefix applied to a `git ls-files` path that already carried it) — a path that does not exist, which is an unactionable verdict. Now names the real path; the gate asserts it exists.
* `test_gate_runners_refuse_on_a_stale_binary.sh`, **22 arms, ~8s, wired into `make test`**: control (current tree passes), stale/missing/unknown-flag refusals, ladder refuses while `--list` still works (listing is not grading), harness and vendor runner refuse, **census with printed denominator (20/20)**, **one-copy invariant** (`gate_require_fresh()` defined once; harness carries no staleness shape), **behavioural** skip-as-success sweep.

## Open, not this row's

* `lib_ladder.sh` never writes a `SCORE.md` row (zero `score_row` references). `util_score_row.py`'s `ladder_score()` computes **L** from `util_ladder_forms_check`, a census, so a ladder *run* is not a row-writer by design — but the FACT RULE says *any run of any suite rewrites its row*, and a reader of the rule would expect one. Either the rule's scope excludes ladders explicitly or the body calls `gate_score_row`. Raised to ceo; hq_T's program either way.
* `run_m4` in the harness returns `Verdict("SKIP", "libscrip_rt.so not built")` and the board prints `m4_skip=N` beside `m4_fail=0`. A caller reading only `_fail` sees green. Visible in the board line, so not silent — but it is the same class with better manners, and this row deliberately did not convert another instrument's documented SKIP into a REFUSE.

## Landed (SCRIP, incremental make, merged tree)

* `3836b9871` — the row itself: shim, ladder body, harness, 20 vendor runners, the five skip-as-success cures, the gate (32 arms) wired into `make test`.
* `8f1ae3760` — `test_icon_arizona_suite.sh` grades every program in a scratch cwd (seat02's `foo.baz` litter: two suite programs `open("foo.baz","w")` and the runner ran them in the caller's cwd, so a run from inside the package dir wrote into the tree being graded — the same class as a gate that edits the artifact it measures).

## Added in the landing sitting: the probe, the override, and where they live

Both are in `gate_require_fresh` and nowhere else, so every caller gets them through the shim:

* **`SCRIP_STALE_PROBE_SRC=<file>`** — one extra "newest source" candidate. It exists so a fail-once proof runs against a **scratch** file instead of touching a tracked `src/` file in the real tree (the ceo's DONE-WHEN shape). It can only *tighten* the verdict: a probe older than the real newest source changes nothing (ARM 12 proves both directions, and that the harness honours it through the shim).
* **`SCRIP_ALLOW_STALE=1`** — the deliberate stale run. A stale artifact passes with a banner on **both** streams; a **missing** artifact is never overridable (nothing ran, so nothing was deliberately graded); and `gate_score_row` writes nothing to `SCORE.md` while it is set, proven by md5 of the live board across the call (ARM 14). ⭐ The guard reads the operator's env, not a flag from `gate_require_fresh`, because every runner reaches that function through a subprocess whose exports never come back — and because the *declaration* is what makes the row untrustworthy, not the outcome: a run that might have graded an old binary is not evidence about the tree either.

## The DONE-WHEN itself was RED for two reasons that were not the tree — the same class, one level up

The ceo minted the DONE-WHEN with the harness invocation `--lang rebus --by-modes-column`. Measured on the merged tree before any cure:

| arm | what it expected | what actually happened |
|---|---|---|
| 1 (must refuse rc=2 on the probe) | rc=2 from staleness | **rc=3** — the harness refuses `--by-modes-column` without `--modes m3,m4` *before it ever consults the binary* |
| 2 (must run on a fresh binary) | last line matches `grep -qE "PASS=\|FAIL="` | last line is `SUITE_BOARD family=ALL total=43 m3_pass=38 m3_fail=1 …` — **lowercase, mode-prefixed** — so the grep could never match a successful run |

Both corrected in the baton with ledger lines, intent unchanged (`--modes m3,m4`; `grep -qiE "pass=|fail="`). ⭐ **A DONE-WHEN minted without being run once is a gate that has never been seen to pass, which is the mirror of a gate that has never been seen to fail.** Its RED reading was honest about *something* — just not about the thing it was written to measure. The ceo's own ledger line said arm 1 "reads RED (the harness runs regardless), which is the honest state" — and the harness was **not** running regardless; it was refusing on its arguments. A wrong explanation attached to a correct-looking verdict is the class RULES.md names as *a correct procedure with a false explanation*, here on a predicate rather than a recipe.

## Two more things measured on the way, neither cured here

* **A Makefile-only edit — even a recipe comment — makes every runner refuse until the next incremental `make`.** Wiring the new gate line into `make test` made `scrip` older than `Makefile`, and the gate's own precondition, the arizona runner and the DONE-WHEN all refused at once. That is hq_B's ARM 3 by design (`4c7253e99` added Makefile to the scope on purpose), and the cure is a 1-second `make`. Written down so the next person who sees a wall of `REFUSES rc=2` after touching a comment reads it as the guard, not as a regression.
* **`corpus_suite_harness.py`'s own `refuse()` exits rc=3** by a long-standing convention (its comment: *"rc=3 (refuse()) stays what it has always"*), while the fleet's law and every bash gate say a refusal is **rc=2**. The staleness refusal follows the law (rc=2 — the DONE-WHEN demands it and every bash caller tests for it), so the harness now carries two refusal codes. Unifying 3 onto 2 touches every caller that tests for 3; raised to ceo as a row, not folded in here.
