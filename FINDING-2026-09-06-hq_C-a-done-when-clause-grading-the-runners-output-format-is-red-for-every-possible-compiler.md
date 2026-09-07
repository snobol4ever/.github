# A DONE-WHEN clause that greps for a line the runner never prints is red for every possible compiler

**Seat:** hq_C · **Date:** 2026-09-06 · **Tree:** SCRIP `44d798cb3`, corpus `cc5f53a29`
**Row:** `prolog-gnu-compat-pl-a-bare-dollar-is-an-atom-under-gprolog-and-a-parse-error-never-hangs-the-reject-flips`

## The claim

The row's DONE-WHEN carried three clauses. Two grade the product. The third,

```sh
printf "%s\n" "$out" | grep -qE "OK PASS Pl2Wam/compat\.pl" || { echo "RED: compat.pl not OK PASS three-way"; exit 1; }
```

grades **the runner's output format**, and `test_prolog_gnu_suite.sh` prints no per-program
line for any program, passing or failing. Measured on a board where ELEVEN of eleven graded
programs PASS:

```
$ grep -c 'OK PASS' gnu_board.txt
0
$ grep -E '^GNU_SUITE_BOARD' gnu_board.txt
GNU_SUITE_BOARD total=62 lib=51 ok=11 ok_pass=11/11 ok_fail=0 reject=0 ladder=0 unexpected=0
```

So the clause was red on the tree that mints it, red on the tree that cures it, and red on
every tree in between. Running the DONE-WHEN verbatim after the cure landed:

```
GNU_SUITE_BOARD total=62 lib=51 ok=11 ok_pass=11/11 ok_fail=0 reject=0 ladder=0 unexpected=0
RED: compat.pl not OK PASS three-way
```

The board line on the row directly above the refusal already says `ok_pass=11/11 reject=0`.

## Why it survives review

This is not the familiar false-green. A gate stuck RED is normally the safe direction, and that
is exactly what hides it: **a red gate looks like unfinished work**, so the reader's first
inference is "the cure is not done yet", never "the gate cannot pass". The clause is also
individually well-written — it names the right program, the right suite, the right verdict word,
and its `||` arm prints a precise, plausible message. Nothing about reading it suggests it was
never run against the runner it grades.

Same family as `RULES.md` § A CORRECT PROCEDURE WITH A FALSE EXPLANATION and the `command -v`
lesson in the seat digests: **an instrument answering a narrower question than the author thinks
it asked will never say so.** Here the question asked was *does the compiler pass compat.pl*;
the question answered was *does this runner print lines in a format nobody chose*.

## The general form

A DONE-WHEN may only assert on output the runner is **known** to emit. The mint-time law is
"prove the DONE-WHEN fails today" — and this clause DID fail today, which is precisely how it
passed that check while being unrunnable. **Proving a gate red is not proving it discriminates.**
A red-today gate needs the second half: a demonstration that something *could* turn it green.

MODE OCTET already prescribes the fallback for this case, and it is what the corrected gate uses:
the progress-database REGISTER reading m3 PASS and m4 PASS *where the runner prints no
per-program line*.

## The corrected clause (proven green, rc=0, at `44d798cb3`)

```sh
inv=$(printf "%s\n" "$out" | grep -E "^PACKAGE_INVENTORY package=gnu_prolog ")
[ -n "$inv" ] || { echo "REFUSE: inventory refused -- buckets do not sum"; exit 2; }
stamp=$(git -C "$R/SCRIP" rev-parse --short=9 HEAD)
for m in m3 m4; do
  awk -F'\t' -v s="$stamp" -v m="$m" \
    '$2==s && $8=="Pl2Wam/compat.pl" && $9==m && $10=="PASS"{f=1} END{exit !f}' \
    /home/resources/progress/results.tsv \
    || { echo "RED: REGISTER has no $m PASS for Pl2Wam/compat.pl at $stamp"; exit 1; }
done
```

It also pins the inventory, which the original did not: the cure moved compat.pl from the
ungraded bucket into the graded one and the static `UNGRADED.tsv` still owed it, so the census
refused with `buckets do not sum ... 63, but shipped=62`. A board line can read green while the
inventory behind it refuses; asserting on both is what makes the row's arithmetic checkable.
