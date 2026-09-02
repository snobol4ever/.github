# FINDING 2026-09-02 hq_P — `van Roy REFUSE 0` cannot serve as the Prolog redesign's program gate: it is NONDETERMINISTIC, and it is satisfied by getting WORSE

**Row:** P7 / the PROLOG REDESIGN program gate (`ARCH-PROLOG-THREE-ZETAS.md` § 6, `8426dc57`). **Tree:** SCRIP `fa12d7cb`, `-O0`, mode 3.
**Instrument landed with this finding:** `SCRIP/scripts/test_gate_vanroy_prolog_acceptance.sh`.
⚠️ **This is a finding about the GATE, not about the redesign.** The redesign's direction is not in question, the sequence is not in
question, and nothing here argues against PZ-4-first. What is in question is the one sentence that decides when the program is *done*.

## 1. The board is not reproducible — 11 of 21 kernels flip on an UNCHANGED binary

Four consecutive full passes, same binary, same inputs, nothing rebuilt between them:

| pass | CLEAN | REFUSE | CRASH | other |
|---|---|---|---|---|
| 1 | 3 | 8 | 8 | 2 |
| 2 | 4 | 4 | 11 | 2 |
| 3 | 4 | 7 | 8 | 2 |
| 4 | 4 | 5 | 10 | 2 |

Per-kernel outcome strings over four reps (`.` clean, `R` refuse, `C` crash, `o` other):

```
derive RCRC!   deriv .RRR!   divide10 RRCR!   ham RCRC!    log10 CRRC!   meta_qsort CRCR!
ops8 CCCR!     queens CRRR!  sendmore RRRC!   tak R.R.!    times10 RRCC!
cal CCCC   crypt CCCC   mu CCCC   query CCCC   zebra CCCC   nreverse oooo   qsort oooo
fib ....   nrev ....   queens_8 ....
```

⛔ **`tak` is clean on half its runs. `deriv` was clean on one.** So even the CLEAN count moves (3–4) without any change.
⭐ **A single pass over this board is therefore not a measurement**, and `REFUSE 0` read once is a coin flip, not a verdict. A seat can
reach it by chance and can read a real cure as a regression, in the same hour.

## 2. Worse: `REFUSE 0` is satisfied by the board DEGRADING

⛔⛔ **The refusal is a GUARD.** Every one of the 8 REFUSEs is the same line — `SCRIP FATAL: pl_trail_unwind refuses corrupt trail mark
… its PRODUCER handed over garbage` — i.e. `pl_trail_unwind` **caught** a corrupt mark before acting on it. So a kernel that stops
refusing has done one of two things, and the criterion cannot tell them apart:

1. it was **cured** — the mark is no longer corrupt; or
2. it now **crashes instead**, or the guard was removed.

**That is not hypothetical: it is the direction this board already moves in.** Under worst-of-3 the count reads `REFUSE=3, CRASH=13`.
⛔ **If those last three refusals became crashes, `REFUSE 0` would read GREEN with 16 of 21 kernels crashing** — a strictly worse
compiler passing the program's completion test. The cheapest path to satisfying the criterion is a regression.

⭐ **Same shape as the vacuous-test class already on the board, arriving through a new door:** a criterion whose cheapest satisfying
change is a regression is not an acceptance test, it is a target. And it would be aimed at the row Lon escalated.

## 3. The cure for the instrument — worst-of-N over three counters, not one

`test_gate_vanroy_prolog_acceptance.sh` runs each kernel `REPS` times (default 3) and classifies it by its **WORST** outcome
(`CRASH > REFUSE > other > CLEAN`). A kernel counts as CLEAN only if it is clean **every** pass, so the board stops flapping and a cure
has to hold rather than merely occur once. It prints each kernel's per-rep string and marks a flapper with `!`.

**It gates on all three at once, because any one alone is gameable:**

- `REFUSE 0` **and**
- `CRASH 0` — *a refusal converted into a crash is a regression, not progress* **and**
- `CLEAN ≥ CLEAN_FLOOR` — pinned at **3** (`fib`, `nrev`, `queens_8`: clean on every pass). Raise it **with** a cure, never lower it.

Measured now, worst-of-3: **CLEAN=3 (floor 3) · REFUSE=3 · CRASH=13 · other=2**, `rc=1`.

⛔ **Recommendation for `ARCH-PROLOG-THREE-ZETAS.md` § 6:** replace *"van Roy REFUSE 0"* with *"van Roy REFUSE 0 **and** CRASH 0 **and**
CLEAN ≥ pinned floor, worst-of-N"*. The one-counter form is not conservative — it is the only form of the three that a regression passes.

## 4. The flapping is itself evidence, and it belongs in § 3

⭐ A corrupt trail mark that **sometimes crashes and sometimes gets caught** is reading memory whose content differs between runs. That is
consistent with — and observed from the outside — the mechanism § 0 already names: the retained frame lives **below `rsp`** and is
clobbered by whatever the next call happens to write there. Whether the mark survives to be *checked* then depends on run-to-run stack
content, which is exactly what these outcome strings show. **PZ-4's clause (a) should collapse this nondeterminism, not merely reduce the
counts** — and that is a sharper, falsifiable prediction for the frame work than "the refusals go away": if the frame is genuinely
protected, the per-rep strings become CONSTANT, whatever value they take.
