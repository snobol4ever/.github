# FINDING — an exception granted for one reason is inherited by every mechanical pass that follows; an exception list is a set of files that quietly stop receiving corrections

**Who/when:** hq_C, 2026-08-28, discharging rank-0 row `pascal-refs-regen-refs-half`. Fix: corpus `16e2677c9`.

## Setting

`358179bb` moved SCRIP's default Pascal integer write width 10 → 11 to match `fpc -Miso`, and seat04
regenerated the `.ref` corpus against the oracle. My caveat on the row was that a blanket regen could bake
in a second defect hiding behind the same symptom, so the close required classifying rather than trusting.

**I validated the regen against `fpc -Miso` directly — never against SCRIP**, because a SCRIP-vs-ref
comparison cannot distinguish a correct ref from one pinned to SCRIP's own output. Each `.pas` copied out
first (fpc writes artifacts next to source), each `.in` used where present.

**Result over the 58 loose pairs: MATCH=56 · MISMATCH=1 · FPC-WON'T-COMPILE=1.** seat04's regen is
genuinely oracle-correct. The caveat's own question — *is a second defect hiding behind the width?* —
answers **no**: `read3` was the only stale-width ref, and every remaining failure differs beyond whitespace.

## The one mismatch, and why it is not a miss

`read3.ref` carried width 10 while every other ref moved to 11. **The regen could not reach it because
fpc cannot run the program at all.** Given its own `read3.in` (`1 2 3 4 5`), `fpc -Miso` dies with
**Runtime error 106** on the ISO `while not eof do read(i)` idiom.

So `read3` sits on the row's exception list for an entirely legitimate reason — *the oracle cannot produce
this ref* — and was therefore **also, silently, excluded from the width correction**, which is an unrelated
concern that happened to run through the same mechanism.

⭐ **The exception was granted for one reason and inherited by another.** Nobody decided that; nothing
recorded it; no instrument could report it, because from the outside an exempted file and a correct file
look identical — both are simply *not in the diff*. **An exception list is a set of files that quietly stop
receiving corrections**, and it keeps that property for every pass that comes after, indefinitely, long
after the reason for the exemption is forgotten.

This is the same family as the moved-basis defect from the same row's parent (a board whose basis moved
reported 82 compiler failures instead of refusing) and as the ROWD coverage claim cured the same session
(green *because* nobody could ever close the row). In each, a mechanism that is correct for its own purpose
silently answers a question it was never asked.

## The fix, and why each half comes from where it does

Widen `read3.ref` 10 → 11, preserving the value.

- The **value** (15 = 1+2+3+4+5) comes from the pre-existing ref: semantically right, and unreproducible by
  fpc, which is why the file is exempted in the first place.
- The **width** comes from the oracle, verified 56 times over in the same measurement.
- **Neither half is taken from SCRIP.** SCRIP is used only to *check* the result, which now matches
  byte-for-byte.

Measured after: m4 loose PASS 141 → **143**, FAIL 13 → **11**; suites **96 pass / 0 fail** both modes;
m3 loose PASS=154 FAIL=9; benchmarks EXAMINED=10 PASS=9 FAIL=0.

## ⭐ A second result, from the classification itself: an aggregate failure count hides structure

Classifying all m4 loose failures by *signature* rather than counting them turned `FAIL=13` into:
**one** whitespace artefact (`read3`, now fixed), **one cluster of seven**, and four singletons.

The cluster: `boolarg boolassign boolchain boolidx boolmix boolnot boolptr` — SCRIP emits **truncated**
output (`boolnot` nothing at all; `boolassign` 1 of 3 lines) and the values it *does* emit are **correct**.
That is early termination — **one shared defect, not seven independent reds** — and the correctness of the
first emitted value is evidence *against* reading it as a boolean-arithmetic bug.

**`FAIL=13` invites thirteen investigations.** The classification cost minutes and is the difference
between one row and seven. Row minted: `pascal-bool-family-truncated-output-one-defect-not-seven`, carrying
an explicit do-not-file-as-seven-rows instruction and the do-not-re-derive note that the width issue is
already ruled out.

## The rules

1. **When exempting a file, record what it is exempt FROM.** "Excluded from the oracle regen" and
   "excluded from all corrections" are different lists that look the same from outside.
2. **Validate a regenerated oracle corpus against the oracle, not against the tool under test** — the
   check that feels natural is the one that cannot fail informatively.
3. **Classify a failure count before investigating it.** The aggregate is not the work list.
