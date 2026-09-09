# Eleven gimpel drivers were graded against SPITBOL's own death dump, because a pin file happened to exist

**Seat** hq_B (HQ-BEAUTIFY) · **Date** 2026-09-08 · **Row**
`snobol4-gimpel-eleven-drivers-carry-a-ref-minted-from-the-oracles-own-fatal-report-that-all-excluded-txt-says-is-no-ground-truth`
· **Trees** SCRIP `251693227` · corpus `af7d27aca` (+ this cure) · RT_OPT=-O0 · oracle `/home/resources/x64/bin/sbl -bf`

## The claim, which the package proves against itself

`corpus/packages/snobol4/gimpel/ALL.excluded.txt` — the package's own record of ref-minting — names **28**
drivers with the line:

    <name>: oracle died: graceful fatal report (e.g. undefined function) -- no ground truth to grade against

**Seventeen** of those 28 have no `.ref`, so `scorecard_snobol4.sh`'s `run_one` reaches
`have_pin=0 && have_live=0`, marks them `ORACLE_FAIL`, and the gimpel runner's UNSCR arm records them in
`OUTSIDE_SPITBOL_BASELINE.tsv`. Correct.

**Eleven** of them — `ARC ASM GPM INFINIP_lib INSULATE L_TWO PEEL SQRT TRIG TUPLE VISIT` (all `_driver`) —
carry a `.ref` **whose content is that same fatal report**, written by the 2026-09-07 one-oracle recut
(corpus `fd77d6e45`). So `have_pin=1`, the program never reaches the `ORACLE_FAIL` arm, and SCRIP is graded
against SPITBOL's death dump. Eleven permanent reds, out of the 27 the Gimpel row was carrying.

## Why nobody saw it: the guard was pointed at the live run only

`scorecard_snobol4.sh` documents this exact hazard at length and implements `sbl_died()` for it — and
applies it to `$W/live` and **never to `$W/pin`**:

```sh
rc="$(sc_oracle_run "$prog" "$lib" "$in" "$W/live")"
if [ $rc -eq 0 ]; then if sbl_died "$W/live"; then ordead=" fatal-report"; else have_live=1; fi; fi
if [ $have_pin -eq 0 ] && [ $have_live -eq 0 ]; then ... ORACLE_FAIL ... fi
```

A pin minted from a dead oracle re-admits precisely what the guard exists to exclude, and it enters through
the one door the guard does not watch. ⭐ **The discriminator between "outside the baseline" and "a red" was
not the oracle's answer — it was whether a pin file happened to exist.** `FTRACE_driver` and `TRIG_driver`
draw the **identical** `ERROR 248 -- attempted redefinition of system function` from the identical cause (a
library `DEFINE` over a SPITBOL system function name). One was recorded outside the baseline. The other was
a red. Nothing about the two programs explains the difference.

## And they were unwinnable on their face

Matching one of these pins byte-for-byte would require SCRIP to reproduce SPITBOL's termination block:

    in file              SQRT.sno        stmts executed       1
    in line              8               execution time msec  0
    in statement         1               REGENERATIONS        0
                                         memory used (bytes)  15640
                                         memory left (bytes)  1032928

Those last two are the oracle's own heap accounting. **No compiler cure could ever have flipped these
eleven.** They were a standing subtraction from the Gimpel board that no seat could have earned back, and a
seat picking one up would have spent the sitting on it before finding that out — which is what makes this
worth a FINDING rather than a commit message.

## The cure, and what it deliberately does not touch

Per the treatment Lon cut on 2026-09-08 (CEO-392; `OUTSIDE_SPITBOL_BASELINE.tsv` is its shape): the eleven
invalid pins are **deleted**, and all eleven are recorded in `OUTSIDE_SPITBOL_BASELINE.tsv` with SPITBOL's
own error and a per-program source check, mirrored into `UNGRADABLE.tsv` (163 → 174). `shipped 290 = graded
116 + ungradable 174` still balances. The board moves **127 → 116 scored**, and the eleven leave the RED
column through the mechanism that was already designed for them, with the runner's own cross-check
confirming record and live set agree.

⛔ **I did not touch `scorecard_snobol4.sh`.** It is the shared SNOBOL4 board every suite goes through, and
a `run_one` change moves every package's denominator at once. Curing the fixtures needs no instrument change
and has no blast radius.

## Two things this leaves open, both named and neither mine

1. **The instrument gap is real and is hq_T's.** `run_one` should treat a pin that itself trips `sbl_died`
   as no pin (`have_pin=0`), so the next recut cannot re-mint this class. Without it, this cure is a
   snapshot, not a fix — the 09-07 recut wrote these pins straight past a record that already said not to.
2. **I swept only gimpel.** The 09-07 recut touched every SNOBOL4 package, and the same shape — an
   `ALL.excluded.txt`-style exclusion overwritten by a recut pin — can exist in any of the other five. The
   one-line census is cheap and I did not run it outside my slice:
   `for r in *_driver.ref; do grep -qE ' : ERROR [0-9]{3} -- ' "$r" && grep -qE '^in statement +[0-9]+$' "$r" && echo "$r"; done`

## The reusable half

⭐ **A guard that names a hazard, and is wired to one of the two paths that hazard can arrive by, reads
exactly like a guard that works.** `sbl_died` is correct, well-documented, well-motivated, and was measured
into existence by a seat who paid for it — and it was checking the live oracle while the pin walked in
behind it. The cheap question for any guard you rely on: **not "is this check right?" but "what are all the
ways the thing it rejects can reach the grader, and is it on each of them?"** The same shape as this org's
`command -v`, `$?`-after-a-pipe, and hard-coded-ROOTS-array lessons: the instrument answered a narrower
question than the one being asked, and said nothing about the gap.
