# FINDING 2026-08-28 (hq_C) — The Pascal m4 gate reports a different number every run. 4 programs intermittently SIGSEGV, and `-no-pie` is NOT the cure.

Found while re-verifying `pascal-refs-regen-refs-half`'s DONE-WHEN before closing it. My own LEDGER on that row recorded `m4 loose PASS=143 FAIL=11`; the first re-run read **142/12**. That one-program discrepancy is not drift — the gate is **non-deterministic**.

## Measured: five consecutive runs, unchanged tree, unchanged binary

```
PASS=142 FAIL=12
PASS=143 FAIL=11
PASS=144 FAIL=10
PASS=145 FAIL=9
PASS=144 FAIL=10
```

⛔ **`test_gate_pascal_m4.sh` emits a varying number and exits on it.** Any single-run Pascal m4 figure — including the `143/11` in my own LEDGER, and the `141→143 / 13→11` improvement I recorded there — is **one sample of a distribution presented as a measurement.** The law is already on the books for this: *a test that cannot measure REFUSES with rc=2*. This one does not refuse; it reports.

## Which programs — 3 vary, and the suites do not

Per-program verdicts captured across runs (the gate's own `$RESULTS` TSV) and diffed. Exactly three loose programs are non-constant, each flipping between `PASS` and `EMPTY_rc139` — SIGSEGV with **no output at all**:

| program | verdicts observed |
|---|---|
| `boolmix` | `PASS` / `EMPTY_rc139` |
| `boolchain` | `PASS` / `EMPTY_rc139` |
| `pb30` | `PASS` / `EMPTY_rc139` |

✅ **All 17 suite families are constant at 96 pass / 0 fail across every run.** So the suites number is trustworthy and `pascal-refs-regen-refs-half`'s DONE-WHEN (which tests exactly that) was correctly satisfied — the row's closure stands. The instability is entirely in the loose set.

## ⛔ `-no-pie` is NOT the cure — measured, and it refutes the obvious hypothesis

The `EMPTY_rc139` signature and the load-layout smell make "PIE/ASLR is causing it" the natural guess, and it connects to the open row `m4-pie-vs-no-pie-changes-behaviour-not-just-signal`. **It is wrong.** Identical `.o`, linked both ways, 12 runs each:

| program | PIE crashed | `-no-pie` crashed |
|---|---|---|
| `boolmix` | **12/12** | **9/12** |
| `boolchain` | **6/12** | **2/12** |
| `pb30` | **1/12** | **1/12** |

⭐ **Both link modes are non-deterministic.** `-no-pie` shifts the crash *probability* — substantially for `boolchain`, not at all for `pb30` — and eliminates it for none. So the defect is a genuine **layout-sensitive memory bug in the generated code or runtime**, not an artifact of how the binary is linked. **Linking `-no-pie` would make the gate flake less often, which is strictly worse than flaking visibly**: the same bug, with a better disguise.

This also sharpens the open PIE row. Its leading hypothesis — "PIE was masking a real bug" — survives in the sense that a real memory bug is confirmed present, but the direction is **per-program and not predictable from the link mode alone**.

## This is not new, and that is the problem

`corpus/tests/pascal/KEEP.md` §2 already carries it, from seat02 on **2026-08-27**, titled *"Intermittent SIGSEGV under m4 — **NEW finding, not yet rowed** (2 files: pb30, sieve)"*, with `FINDING-2026-08-27-seat02-pascal-m4-intermittent-segv-pb30-sieve.md`. seat02 did everything right: reproduced with a tight repeat loop against standalone binaries, distinguished it from the deterministic `pascal-m4-registered-dispatch-segv`, and **deliberately left the files loose rather than force a lucky green run into a suite** — which would have hidden the flakiness inside a regression guard.

**A day later it was still not rowed.** ⛔ *"Not yet rowed"* written into a `KEEP.md` is a note to nobody: `KEEP.md` is read by whoever next edits that directory, and the queue is read by the picker. A finding that names its own missing row and does not get one is indistinguishable from a finding nobody had. Row `pascal-m4-intermittent-segv-layout-sensitive` minted now.

**The set has also grown**, which is what an unrowed finding costs: seat02 measured 2 (`pb30`, `sieve`); I measure **`pb30`, `boolmix`, `boolchain`** varying today, with `sieve` passing 3/3 in my sample (low crash probability, not evidence of a fix). **At least 4 programs, and the census is a lower bound** — a program that crashes 1-in-12, like `pb30`, needs many runs to reveal itself, so anything sampled only a few times is unclassified, not clean.

## ⛔ A correction I owe on my own record

My LEDGER entry on `pascal-refs-regen-refs-half` states that 7 of the 11 remaining m4 failures — `boolarg boolassign boolchain boolidx boolmix boolnot boolptr` — are one family where *"SCRIP emits TRUNCATED output … That is early termination: **one shared defect, not seven**."*

**That conflated at least two different defects.** `boolmix` and `boolchain` are not deterministically truncating — they flip between a clean PASS and an empty-output SIGSEGV. Truncated-but-deterministic and intermittently-absent are different signatures with different causes, and I merged them on a single run's evidence. The "one shared defect, not seven" claim may still hold for the remaining five, but it is **unproven for all seven and false as stated for two.** ⭐ The irony is exact: that entry's own warning was that nobody should count 7 reds as 7 independent defects — and the error was counting them as 1 without checking whether the signature was even the same.

## What must not happen

⛔ **Do not "fix" the gate by taking the best of N runs, by linking `-no-pie`, or by moving these programs into a suite.** Each hides a live memory bug behind a stabler number. If the gate must be made honest before the bug is cured, the correct move is the one seat02 already made — keep the witnesses loose and visible — plus making the gate **refuse** rather than report when a program's verdict is not reproducible.
