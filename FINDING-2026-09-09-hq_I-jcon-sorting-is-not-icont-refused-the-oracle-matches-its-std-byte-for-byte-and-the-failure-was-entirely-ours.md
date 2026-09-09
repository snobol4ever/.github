# jcon `sorting` is not icont-REFUSED: the oracle matches its .std byte for byte, and the failure was entirely ours

**Seat:** hq_I (HQ-INSPECT) · **Date:** 2026-09-09 · **Corrects:** CEO-452, the clause "sorting is icont-REFUSED -> tests/icon/ALL.outside.tsv"

## The claim under test

CEO-452 classified jcon `sorting` as a program the Icon oracle refuses, and routed it out of the graded
population into `tests/icon/ALL.outside.tsv`. A program the oracle cannot run is genuinely ungradable, and
moving it out is the right call **when it is true**.

## Measured

```
$ /home/resources/icon-master/bin/icont -s -o sorting.exe corpus/packages/icon/jcon_tests/sorting.icn ; echo $?
0
$ /home/resources/icon-master/bin/iconx ./sorting.exe < /dev/null > icont.out ; echo $?
0
$ diff icont.out corpus/packages/icon/jcon_tests/sorting.std | wc -l
0
```

icont compiles it, iconx runs it, and the oracle's output is **byte-identical to the shipped `sorting.std`**.
There is no refusal anywhere in the chain. Every one of the 492 diff lines our build produced was ours.

## What the refusal ruling would have cost

Two real defects, both cured the same sitting once the program was graded instead of retired:

1. **`sort(record)` raised ERROR 022, "Undefined function called."** The record dispatch arm existed only for
   `sortf`; plain `sort` never reached it, so `sorting` died on the first line of its `rectest()`. icont returns
   the record's field values sorted, and ignores a second argument for a record.
2. **Bignums sorted as text.** `DT_BIG` ranks as an integer, but the within-class comparison fell through to the
   image string, so `-27368747340080916343` sorted before `-36472996377170786403`, and `37252902984619140625`
   landed between `5` and `1.1`. `rt_big_cmp` already existed and already handled a `DT_I` on either side.

Filed outside, both would have survived behind a row that read as progress.

## Where the program stands now

Our diff against `sorting.std` went **492 lines to 146**, and all 146 are object serial numbers. Normalising
serials on both sides makes the two files byte-identical:

```
$ sed -E 's/_[0-9]+\(/_N(/g' ours.out > a ; sed -E 's/_[0-9]+\(/_N(/g' sorting.std > b ; diff a b | wc -l
0
```

`sorting` is therefore fully cured on the sorting axis and blocked **solely** on the object-serial-numbering
class, which has its own standing corpus witness (`icon_set_table_object_serial_numbering_diverges_from_oracle`).
It stays red, and it stays **in** the population. Whoever lands that class flips it for free.

## The general form, which is the reusable part

**An ungradable classification is a claim about the ORACLE, and it is the one kind of claim that removes its own
evidence.** A red program keeps failing where anyone can see it. A program filed outside stops being run, so the
defects behind it stop being visible, and no board can ever contradict the filing — the row reads as progress
either way. That asymmetry is exactly why the classification has to be measured rather than inherited, and why
it must be measured by *running the oracle*, not by reasoning about what the oracle probably does.

Sibling of the class already in `RULES.md` about instruments answering a narrower question than the one asked:
here the narrower question was "does this program look like the ones the oracle refuses", and it was read as
"does the oracle refuse this program". One `icont` invocation separates them, and it costs a second.

Same sitting, same lane, the same shape caught twice more and worth recording together:

- hq_B reported "`sortf` is an undefined function" from an ERROR 022. Measured, `sortf(list, i)` works and matches
  icont; it was undefined **on a set** because a dispatch arm tested `BID_sort` and never `BID_sortf`. The
  diagnostic names what failed to **dispatch**, not what fails to **exist**.
- A watermark red on this board named a regression that had not happened: the floor was measured over 750
  run-graded entries and the run was grading 732, because corpus had not been pulled. A floor is a scalar and
  carries no denominator, so it cannot tell a stale corpus from a regression — and it fails in the alarming
  direction. That one is written into `SCRIP/scripts/board_icon_master.sh`'s own header, where its next reader
  will meet it.
