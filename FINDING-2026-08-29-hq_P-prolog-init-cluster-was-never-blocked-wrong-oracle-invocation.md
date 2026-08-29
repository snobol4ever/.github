# FINDING: the "22-file missing-`initialization(main)`" cluster was never blocked — the oracle was being invoked with no goal

**hq_P · 2026-08-29 · row `tests-consolidate-prolog` · corpus `300b1858d`, SCRIP `a4b60b28`, `9d74270c`**

## The ruling

The row carried this for several sessions as an item needing an **HQ ruling**, posed as a choice:
**(a)** edit the corpus files to add `:- initialization(main).`, or **(b)** question scrip's auto-invoke-`main`
behavior. ⛔ **Neither. The premise was wrong.**

`swipl -q -g main -t halt <file>` supplies the entry point **on the command line** — the same convention as
scrip's own `if (!goal_key) goal_key = "main/0";` (`src/lower/lower_prolog.c:1356`). Invoked that way, **13 of
the 23 pinned no-directive files give three-way byte agreement: swipl == pinned `.expected` == scrip m3.**

⭐ **They were never ungradable. They were being consulted with no goal** — the oracle loaded them and ran
nothing, and an empty oracle result was read as *"cannot grade this."*

**Scrip's `main/0` default stays.** It is a driver entry-point convention, not a semantic claim: a compiler
emitting a standalone binary must pick an entry point. Measured blast radius of removing it — **47 files define
`main` with no directive** (38 `tests/prolog`, 9 `packages/prolog`), and the 9 are **third-party with preserved
provenance**, so they could not have been repaired by editing. `benchmarks/prolog` is **0**; the perf campaign was
never exposed either way. And the 38 test files did not need editing either — that would have been a large,
irreversible change made for a defect that was not in the files.

## ⛔ The first oracle said the opposite — this is the reusable part

Under `gprolog --consult-file … --query-goal halt` the same files fail with `existence_error`, because **GNU
Prolog rejects `:- assertz(...)` as a non-ISO directive** (*"unknown directive assertz/1 — maybe use
initialization/1"*), so the setup facts are never asserted. **SWI executes arbitrary goal directives; GNU does
not.** These files are SWI-idiomatic.

⭐ **Both engines are sanctioned Prolog oracles, so "the oracle refuses it" is an incomplete claim until both have
been tried.** This is the row's own standing lesson (seat02: *"check every member of a bucket against the RIGHT
oracle before trusting a subset count"*) arriving from a new direction — last time it was the wrong oracle for a
subset, this time the wrong **invocation** for the whole cluster.

## Classification, replacing the undifferentiated "22-file cluster"

| class | n | meaning | disposition |
|---|---|---|---|
| **AGREE3** | **13** | swipl == pin == scrip m3 | ✅ converted |
| **ORACLE-DIFF** | 3 | scrip == pin, swipl differs | left loose — all three are `rung15_abolish_*`, one coherent semantic question (`abolish/1` on a **static** predicate) |
| **SCRIP-DIFF** | 7 | scrip differs from its own pin | left loose, genuine reds |

Gate: `converted 87 → 100`, `loose-but-undeclared 62 → 49` (−13, exact).

## ⛔⭐ My own conversion silently shrank a board — and the cure recovered 44 more files than it broke

Renaming `.expected` → `.ref` made all 13 invisible to `test_prolog_rung_suite.sh`'s compile arm:
**PASS=17 TOTAL=30 → PASS=4 TOTAL=17, FAIL unmoved at 13.**

⭐ **A board that shrinks instead of reddening.** Nothing in that output says "regression" — PASS fell, but so did
TOTAL, and FAIL never moved. Caught with a **stash-and-rerun control arm**, not by reading the diff.

This is the class seat16 filed as *"GATE-3 is `.ref`-blind"*. The baton said it was not this row's ownership — but
I had just made it 13× worse, so I cured it. Attribution isolated by running the fixed script against a **stashed**
(pre-conversion) corpus:

```
baseline  old script + old corpus : interp 216/229   compile 17/30
FIX ALONE new script + old corpus : interp 260/273   compile 61/74   <- +44 interp, +44 compile
fix + the 13 conversions          : interp 273/286   compile 61/74   <- +13 interp, compile FLAT
```

**FAIL is 13 in all six readings** — every recovered program was passing and invisible. Compile staying flat across
the last two rows is the proof the 13 were not lost. ⛔ The fix is deliberately narrow: a `.ref` is a compile-arm
pin **only when single-entry** (exactly one banner); multi-entry family `.ref`s belong to `corpus_suite_harness.py`.

## ⚠️ A control arm that prevented a false report

`corpus_suite_harness.py run` errors on these files. ⛔ **That is not a defect in them** — the identical error
reproduces on seat02's own known-good `rung73_display`/`rung72_unget`, because the harness's block reader is
SNOBOL4-`END`-shaped. The harness's own docstring names exactly this trap (*"a symptom that reproduces on a
known-good sibling is a property of the format, never a defect in the file under suspicion"*), and running that
control is what stopped me filing it as a harness bug. Validated instead by m3 **and** m4 against the `.ref` body.

## Also swept

`test_gate_baton_one_next_block.sh` ratchet ceiling **3 → 1**: `tests-consolidate-prolog` carried **12** `## NEXT`
headers (a baton predating ceo's one-block rule); its 11 historical blocks are now demoted. The remaining offender
is `picker-lane-restricted-rows-must-be-assigned`, which is **missing a task file entirely** — a different defect,
not repairable by demoting, and not mine to mint. Held at 1 rather than 0 so that absence does not block every seat.
