# Four of the five Jcon A–I reds were real; the fifth was a semicolon we added ourselves

**Seat:** hq_C · **2026-09-09** · CEO-445 (Lon: *"Switch to Icon completely… Icon only; no SNOBOL4 nor Prolog"*)
**Trees:** SCRIP `b87234ec3` · corpus `af179eebd` · RT_OPT=-O0 · oracle Arizona `icont`/`iconx`
**Board:** Icon master 707/707 (entries 860) → **709/726 (entries 879)**, per-entry identity **0 regressions · 0 vanished** over 1557 examined.

## WHAT THE CRITERION CHANGE ACTUALLY BOUGHT

The A–I half of hq_I's twelve genuine Jcon reds is now IN the Icon master denominator instead of behind `.xfail` markers. Four are red in the fraction (`errors` `evalx` `fncs` `gener`); **`image` passes both modes**, and it is a real cure rather than a re-labelling.

⛔ **`rung36_jcon_image` WAS NEVER A SCRIP DEFECT.** Our copy carried **one semicolon** the upstream `jcon_tests/image.icn` does not — line 66, terminating the `then` branch of an `if/then/else` — which makes **`icont` itself refuse the program**: `Line 67 # "else": invalid expression`. Upstream compiles clean. The semicolon was added for SCRIP's semicolon-required frontend, and **the adaptation had silently become part of the oracle's input**. A corpus fixture bug sat behind an `.xfail` marker reading as a compiler defect.

⭐ **A concurrent seat found the same class from the other end in the same hour** (`1409e998b`: a `;` after a *case clause* breaks `icont`; 5 of 20 fail to compile as ours, all 5 compile clean upstream) and resolved it by compiling the UPSTREAM source for the oracle. Two independent discoveries of one class, from a syntax we introduced. The general form is worth more than either instance: **when a corpus is adapted for the tool under test, the adaptation silently becomes part of what the oracle is asked to answer, and every ref cut afterwards is cut from a different program than the one on disk.**

## THE MARKER WAS DOING DOUBLE DUTY AS EVIDENCE AND AS EXCUSE

`KEEP.md`'s keeper reason for these read *"permanently `.xfail`-marked, genuinely fails today"*. hq_I measured on 2026-09-08 that the marker set and the master denominator are **two disjoint sets**. So a red held out of every denominator is invisible to every board **by construction**, and "genuinely fails today" could stay true indefinitely with nobody accountable. **The evidence for holding them out was the fact of their being held out.** Retiring the marker is what made `image`'s fixture bug findable at all: nobody re-examines a program that no board grades.

## ⚠ THE NUMBER MOVED IN A WAY THAT READS AS A REGRESSION AND IS NOT

707/707 → 709/726. **A reader comparing fractions concludes Icon got worse.** The pass SET grew; the denominator grew faster, because it now states reds it used to hold out of sight. This is the shape every honest criterion change makes, and it is why the floor (a ratchet over the pass set) rose 707 → 709 in the same commit that added 17 visible reds. ⛔ A fraction is not comparable across a criterion change; only the per-entry identity is, and it says 0 regressions.

## WHAT IS NOT CLAIMED, AND ONE THING NAMED FOR ITS OWNER

- **`rung36_jcon_io` is NOT absorbed** and is not counted: the icon master format cannot yet carry a stdin sidecar, AND its `.expected` is a **STARVED cut** — 50 diff lines against a fed oracle run, missing the eight stdin echo lines entirely. Its ref was wrong in a way no board could see, because the board never ran it. Two independent blockers, either sufficient.
- The four remaining reds are **not diagnosed here** — this landing is the criterion change CEO-445 asked for, and the cures are one at a time after it.
- ⚠️ **Two entries graded non-deterministically across runs minutes apart on one tree** (`procedure_every_alt_replace_4`, origin `rung36_jcon_kwds`, red in one run and absent from the next; `procedure_write_265` likewise). Not mine by origin, named rather than absorbed into a count: a board that reports a different red set on the same tree is a measurement problem before it is a compiler problem.
- ⛔ **LANE COLLISION, for the ceo:** MODE line 2 gives hq_C the Jcon A–I half and hq_I J–Z, but `errors` (A–I) was being cured by another seat while I absorbed it (`f7e1e3017`), and my landing collided on the generated master **twice**, once losing a full rebuild. Two seats absorbing into one generated `ALL.icn`/`ALL.ref`/`ALL.csv` cannot merge — the files are built, not edited — so the split needs to be by *suite file*, not by program name, or absorptions need serialising.
