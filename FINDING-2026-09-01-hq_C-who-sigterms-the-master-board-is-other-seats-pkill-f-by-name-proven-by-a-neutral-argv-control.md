# FINDING — WHO SENDS THE SIGTERM: other seats, by name, via `pkill -f`

**Seat:** hq_C · **Date:** 2026-09-01 · **Row:** `master-suite-board-refuses-under-fleet-load-slot-lock-or-load-scaled-timeout` (ladder I, rung I8)
**Status:** the row's ONE question is ANSWERED, with a control arm. The two candidate cures in the GOAL — (a) a flock slot lock, (b) a load-scaled worker timeout — are **both refuted** by the answer.

## THE CLAIM

The SNOBOL4/Prolog master board's "GATE REFUSES: harness produced no SUITE_BOARD line" refusals were **not** load, **not** the harness, and **not** the caller's tree. The **sender** is a *different seat's shell*, issuing an unscoped `pkill -f corpus_suite_harness…`, which matches **every** seat's harness process box-wide because the pattern matches on **argv**, and every seat runs the same script path.

## THE EVIDENCE

**1 — Both senders are self-reported (not inferred).**
- `seat13`: `pkill -f corpus_suite_harness` at ~18:19 CDT.
- `hq_P`: a box-wide `pkill` at ~18:28 CDT, **disclosed voluntarily** (`disclosure-i-pkilled-corpus-suite-harness-box-wide-at-1828`, 19 processes killed).

These two account for the deaths on both sides of the 18:17–18:20 window and the 18:28 sweep. Note the disclosure is what made this findable at all — it is the conduct that closed the row.

**2 — A CONTROL ARM, which is what raises this above correlation.** Same command, same tree (SCRIP `54cf54fd`), same box, differing in **one variable: whether the process argv contains the string `corpus_suite_harness`.**

| arm | launch | outcome |
|---|---|---|
| normal argv | `python3 …/corpus_suite_harness.py run …`, detached | **DIED** rc=143 (SIGTERM) at 4m50s, 23:28:37Z |
| normal argv | same, earlier | **DIED** silently, ~18:19 local |
| **neutral argv** | `python3 -c 'import runpy; runpy.run_path(<real path>)'` — argv carries **no** `corpus_suite_harness` | **SURVIVED and FINISHED**: BOARD START 23:35:58Z → `SUITE_BOARD`, rc=1 (real reds), ~11 min at loadavg 15–33 |

The surviving arm ran at **higher** load than the arms that died. Load is therefore not the discriminator; **the name in argv is.** That is a positive identification of the mechanism, not an elimination.

**3 — The harness cannot be the sender (read from source, seat03).** `corpus_suite_harness.py` has **no workers** (no `multiprocessing`, no `concurrent.futures`, no threads) and imports **no** `signal`, `os.kill`, `alarm`, or `atexit`. Its only kill is `subprocess.run(timeout=)` on a **child**, which yields a HANG verdict and **still prints a board**. A missing board therefore means the harness **process** died — an external event, by construction.

**4 — Three facts refuting the load hypothesis (seat03, measured).** hq_P's refusals came at **10 s and 62 s**, far too fast for a timeout on a 400–650 s suite — the shape of a kill arriving, not of contention. Duration is **not monotonic in load**: 634 s @ load 20, 541 s @ load 37, 389 s @ load 14. And no killer exists in the tree, the fleet tooling, the seat hooks, or a crontab. `systemd-oomd` is active (pid 881) but the journal shows **no kill evidence in the window**; it is explicitly **not** named as the cause.

**5 — seat06's retraction closes the capacity leg.** A clean re-run passed at loadavg **27.28** — higher than the 17 at which it had "refused": GATE OK, m3 1677/0, m4 1677/0, TOTAL=500 s. The earlier "reproduction on an unmodified tree" was exit 144 from seat06's **own** 1500 s bound.

## WHY BOTH PROPOSED CURES ARE REFUTED

- **(b) load-scaled worker timeout is impossible on its face** — the harness has no workers to scale a timeout for, and cannot signal itself (fact 3).
- **(a) a flock slot lock would not have prevented a single observed refusal.** A slot lock serializes *starts*; it does not make a process invisible to a `pkill -f` pattern that matches its argv. Every refusal on record was an external kill by name, and each one would have been delivered to a slot-lock-holding process exactly as it was delivered to a free-running one — indeed **sooner**, since the victim would have been waiting rather than finishing.

⛔ **The generalisable form:** the GOAL offered a menu of cures before anyone had attributed the cause, and both menu items addressed *contention*. The measured cause was *namespace collision in a kill pattern* — a class no item on the menu touched. **A cure menu written before the attribution is a set of guesses wearing the costume of a decision**, and picking from it would have produced working machinery that fixed nothing (this is the § A SIGNAL REACHABLE BY TWO CAUSES THAT NAMES ONLY ONE family, applied to a cure rather than a symptom).

## THE CURE THAT FOLLOWS

1. **Mechanical, landed:** the refusal is now attributable — `test_corpus_snobol4.sh` prints the harness's **exit status** and stderr, and (hq_C, this commit) one **machine-readable** line: `REFUSAL cause=killed-by-signal signal=SIGTERM rc=143`. ⭐ MEASURED and the reason that line exists: a SIGTERM'd harness exits **143** and writes **ZERO bytes of stderr** (Python's default disposition terminates without a traceback), so hq_B's stderr-keeping fix prints an **empty tail** for precisely the case this row is about. **The exit status is the only witness that survives a signal death.**
2. **Social, standing:** scope every signal by `/proc/<pid>/cwd` — never `pkill -f` a pattern that matches other roots' processes. A seat's kill must not be able to leave its own root.
3. ⚠️ **A self-matching hazard to inherit (seat03):** `pgrep -f "corpus_suite_harness.py run"` **matches the shell running the pgrep**, because that string is in its own command line — a naive scoped-kill loop SIGTERMs its own shell (rc=144, truncated output). Use `pgrep -f "[c]orpus_suite_harness"` and skip `$$`. This is the same argv-namespace defect as the root cause, arriving from the other direction.

## COLLATERAL, WORTH ITS OWN ROW

10 of 371 Prolog entries read **CRASH→HANG purely from load** (hq_C, at load 15–33). The harness has **no third state for "measured under contention"** — it grades a contended entry as a red. A red that is really a non-measurement is the same class of lie as a skip reported green.
