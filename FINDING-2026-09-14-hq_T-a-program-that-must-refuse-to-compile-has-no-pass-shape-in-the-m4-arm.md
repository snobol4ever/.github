# FINDING 2026-09-14 hq_T — a program that MUST refuse to compile has no PASS shape in the m4 arm

**Measured** on SCRIP `a1df8eed8` + corpus `f52809f05`, RT_OPT `-O0`, incremental `make`, box clock
2026-09-14 ~03:0x UTC. Found while executing CEO-740 (promote the raku XPASSes).

## THE CLAIM

`corpus_suite_harness.py`'s mode-4 arm classifies a non-zero `scrip --compile` as
`Verdict("SKIP", detail="scrip --compile failed")` (`corpus_suite_harness.py:784`). That is right for a
program that *should* compile and doesn't. It is **wrong for a program whose correct behaviour is to be
rejected at compile time** — and the arm cannot tell the two apart, because the only thing it looks at is
whether the compile succeeded.

So a compile-time-die test is **structurally unpassable in m4**: permanently in the denominator, never in
the numerator, and reported as SKIP rather than as a red — which is why nobody has been looking at it.

## THE WITNESSES

The two entries that CEO-740 asked me to promote and I did **not**, because promoting them would have
moved the row backwards. Both are role-composition errors, both marked XFAIL in `corpus/tests/raku`:

| entry | source | m3 | m4 | rakudo v2022.12 |
|---|---|---|---|---|
| `class_method_range_replace_6` | `role R { method needed() {...} }` / `class C does R { }` | rc=1, stdout empty → **PASS** | `--compile` rc=1, stdout empty, stderr `Method 'needed' must be implemented by class C because it is required by role R`, no `.s` → **SKIP** | rc=1, stdout empty |
| `class_method_say_replace_49` | `role A { method m() {…"a"} }` / `role B { method m() {…"b"} }` / `class C does A does B { }` | rc=1, stdout empty → **PASS** | `--compile` rc=1, stdout empty, stderr `Method 'm' must be resolved by class C because it exists in multiple roles (A, B)` → **SKIP** | rc=1, stdout empty |

Both declare `wantrc=1` in `ALL.wantrc` and both have an empty ref. **SCRIP is correct in both modes and
agrees with the oracle in both.** The compiler is not the defect here; the grading is.

These two are exactly the gap between the board's `m3 xpass=19` and `m4 xpass=17`.

## SIZE, MEASURED RATHER THAN GUESSED

Of raku's 16 `ALL.wantrc` entries, **2 are compile-time-die (m4 SKIP) and 14 are runtime-die (m4 grades
them fine)** — so the class is small today, and 7 of the 17 entries I promoted this sitting were
runtime-die, which is why they promoted cleanly. Corpus-wide the nonzero-`wantrc` population is raku 16,
icon 8, rebus 4, prolog 1, snocone 1; snobol4 and pascal carry none. The class is small **now** and will
not stay small: every language's ladder eventually reaches constructs whose only correct behaviour is a
compile-time rejection, and Pascal's oracle (`fpc -Miso`) rejects at compile time by design.

## WHY THIS IS AN ASK AND NOT A LANDING

`corpus_suite_harness.py` is a shared node serving all seven masters. Teaching the m4 arm a
compile-time-die shape changes the denominator arithmetic of every board, so under the NONET guardrails
("a change to a node another concern owns is an ASK to your HQ with the measurement, never a landing")
it goes up rather than in. Raised to the ceo this sitting.

**The shape I would propose, for the ceo to rule on, not to be read as a decision:** an entry whose
declared `wantrc` is non-zero and whose ref is empty is *asserting a rejection*; for such an entry, an
m4 compile that exits with exactly that rc and writes nothing to stdout is a **PASS**, and a compile that
SUCCEEDS is the **red**. That inverts the arm only for entries that have explicitly declared it, so no
existing entry changes verdict — which is the property that makes it gradable as a control arm.

## ⭐ THE REUSABLE PART

`SKIP` is the third thing a verdict can be, and it is the one that does not argue with you. A red gets
looked at and a pass gets counted; a skip is *absence*, and absence reads as "not my problem yet" no
matter how long it sits. These two entries have been correct in both modes and invisible in one of them,
carrying an XFAIL marker that said the opposite, for as long as they have existed.

The narrower lesson, and the one that generalises past this harness: **an instrument that classifies by
MECHANISM ("the compile failed") cannot express INTENT ("the compile was supposed to fail"), and it will
never say so** — it reports a real-looking verdict in the vocabulary it has. Same family as
`command -v` answering "is it on PATH" when asked "does it exist", and as the `$?`-after-a-pipeline
reporting the last command's status. The tell is the same every time: the instrument is answering a
narrower question than the one you asked, and it is answering it correctly.

## SEE ALSO

- `corpus_suite_harness.py:784` — the classification.
- `scripts/util_raku_entry_grade.sh` — the per-entry grader; its header already records the neighbouring
  trap (grading a die test on stdout alone scores four entries XPASS that are not). This finding is that
  same trap one level further out: grading on *build success* alone scores a correctly-refusing compile
  as unmeasurable.
- `FINDING-2026-09-05-hq_T-every-xfail-promotion-leaves-the-master-unsorted-and-the-csv-stale.md`.
