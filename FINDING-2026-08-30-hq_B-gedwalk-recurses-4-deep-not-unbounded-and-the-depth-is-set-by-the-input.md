# FINDING 2026-08-30 hq_B — gedwalk recurses 4 deep, not unbounded; and the depth is set by the input file

**Tree:** SCRIP `759efa86`+ · corpus `6d8a364c` · measured 2026-08-30, seat `hq_B`, on row
`icon-n2-recursive-generator-per-activation-storage`.

## What this answers

The row's GOAL closes with an instruction that no pass has carried out across at least five sessions:

> *"Characterize first: how deep does gedwalk actually recurse on geddump.dat (measured, not assumed) — a
> small bounded depth may admit a simpler answer than the general case."*

Every pass since has gone straight to the crash mechanism — productively, and with two real corrections
along the way — while the opening question stayed open. **The answer is 4.**

## Measured

`gedwalk` instrumented with a depth parameter and a histogram, compiled and run under the **Icon oracle**
(`/home/resources/icon-master/bin/icont -s`), on the benchmark's own `geddump.dat` (24,431 lines, 389 KB):

```
GEDWALK-MAX-DEPTH=4
GEDWALK-TOTAL-ACTIVATIONS=48833
  depth 1:  3188 activation(s)
  depth 2: 18956
  depth 3: 21223
  depth 4:  5466
```

⭐⭐ **48,833 activations in total; at most 4 alive at any moment.** That distinction is the whole point for
this row. Per-activation storage has to survive *suspension*, so what must be live is the suspended chain —
**four records** — not the 48,833 the program creates over its run. The GOAL cites jcon's precedent of
materializing a `vClosure` per activation; on this benchmark the live set that design would hold is four.

## ⛔ But the depth is a property of the INPUT, not of the program

The obvious next move — "so bound it at 4" — is wrong, and it is cheap to show why. Synthetic GEDCOM files
of increasing nesting, same binary:

```
max GEDCOM level 2  ->  GEDWALK-MAX-DEPTH=4      <- this is geddump.dat
max GEDCOM level 4  ->  GEDWALK-MAX-DEPTH=6
max GEDCOM level 6  ->  GEDWALK-MAX-DEPTH=8
```

`depth = max GEDCOM level + 2`, linear, with no ceiling in the format. So 4 is a fact about *this file*.

⚠️ **I predicted 3 from the data and measured 4.** Levels 0/1/2 are the only ones present
(`awk '{print $1}' geddump.dat | sort -n | uniq -c` → 3190 / 15775 / 5466), and reasoning from the GEDCOM
level structure gives a depth of 3; the record roots add one more activation. The instruction in the GOAL
said "measured, not assumed" and it was right to: the inference was off by one, in the direction that would
have made a fixed-N design one frame too small.

## What this does and does not license

✅ **It reshapes the design question, which is what the GOAL wanted it for.** "A recursive suspended chain's
lifetime is not stack-shaped" is true in general; on this benchmark the chain is four deep and its shape is
known before execution. A bounded activation stack **with an explicit overflow refusal** would run
`geddump.icn` honestly and be gradeable — and unlike the general case it needs no ruling about where
per-activation records live, because they would live where the row's own storage doctrine already says.

⛔ **It does not license a fixed depth of 4, and it does not license silence on overflow.** N is chosen by
whoever supplies the `.dat`. A build that assumes 4 would produce a wrong answer on a deeper file with no
diagnostic — the same class as the `[SMX]` refusal exiting 0 and the `.push`/`.shift` no-ops filed today.
The refusal is the load-bearing half of that design, not a nicety.

⛔ **It says nothing about mutual recursion**, which the GOAL lists separately and which no measurement here
touches. `gedwalk` is self-recursive only.

## Method note

The measurement used the ORACLE, not SCRIP, deliberately: SCRIP cannot run this program at all — that is
the row. Asking the reference implementation what the program *does* is independent of every open question
about what SCRIP does with it, and it cost one instrumented copy and two compiles.

⭐ It is the same move as asking the oracle to run a sequential rewrite of the raku `start`/`await` kernel
earlier today: **ask what the program actually DEPENDS on before designing machinery for what it might
contain.** Five passes of gdb on the crash site were all correct work; none of them could have produced
this number, and this number changes what the cure has to be.
