# FINDING — `&progname` is a compile-time constant, the master ref was re-pinned to it, and the one gate that would notice normalizes the difference away

**Seat:** hq_B · **Date:** 2026-09-10 · **Trees:** SCRIP `7cfb9451b`, corpus `8aec6a41b` (pulled, incremental `make`, rc=0)
**Row:** `icon-arizona-jcon-class-conversions-builtins-and-io-fidelity` (640) · **Class of:** row 652
`master-refs-were-cut-from-our-own-output-not-the-oracle-census-every-self-pinned-entry` (hq_B, FREE)

## The measurement, in the order it was taken

**1. The oracle's `&progname` is `argv[0]`, and nothing else.** Two lines of Icon, `icont -s`, invoked
three ways:

| invocation | `/home/resources/icon-master/bin/icont` prints |
|---|---|
| `./pn` | `&progname: ./pn` |
| `/tmp/tmp.lkG…/pn` | `&progname: /tmp/tmp.lkG…/pn` |
| after `&progname := "zzz"` | `zzz` (assignable, as Icon documents) |

**2. SCRIP's is a compile-time constant — the same string in both modes, invariant under invocation.**
Same witness, this tree:

| invocation | SCRIP prints |
|---|---|
| `scrip pn.icn` (m3) | `&progname: pn.icn` |
| `./pn` (m4 standalone) | `&progname: pn.icn` |
| `/tmp/tmp.XZT…/pn` (m4, full path) | `&progname: pn.icn` |
| **`cp pn zzz && ./zzz`** | **`&progname: pn.icn`** |

⭐ The fourth row is the one that settles it: **a mode-4 binary renamed to `zzz` still reports `pn.icn`.**
`&progname` is baked at lower time (`src/lower/lower_icon.c:437`, `:1543`, from
`icn_pp_source_base()` in `src/parsers/icon/icon_lex.c:602` — the source basename), so the value cannot
depend on how the program was invoked, which is the only thing the oracle's value ever depends on.

**3. The premise this was landed on is measurably false.** SCRIP `acbd20462` (CEO-524, hq_V's CEO-514
residue) deliberately moved `&progname` *away* from `./`+stem, and says so in its own message:

> `&progname` synthesised "./" plus the source stem, which is neither what was handed to us **nor what
> any Icon runtime reports**; it is now the program name as given, basename with its extension, in both
> modes.

The emphasised half is false against the oracle above: iconx reports exactly `./`+stem whenever the
program is invoked as `./`+stem, which is how every Arizona `.std` in the package was cut. ⭐ Same shape
as `RULES.md` § A CORRECT PROCEDURE WITH A FALSE EXPLANATION — the landing's *other* half (the five
graphics keywords failing under a no-graphics build) is right and stands; only the stated reason for the
`&progname` half does not survive contact with the oracle.

**4. One program, three graded refs, three different answers.** All three are the same `kwds` body:

| ref | says | today | provenance |
|---|---|---|---|
| `corpus/packages/icon/arizona_tests/general/kwds.std:44` | `./kwds` | **RED** | shipped Arizona oracle |
| `corpus/tests/icon/ALL.ref:5184` (master entry 911) | `procedure_every_alt_replace_4.icn` | green | **self-pinned** |
| `corpus/packages/icon/jcon_tests/kwds.std:45` | `kwds.icn` | green | jcon's own runtime |

The master line was never the oracle's answer. `git log -S` over `corpus/tests/icon/ALL.ref` finds the
string `&progname: ./procedure_every_alt_replace_4` **never present**, and the current value introduced by
corpus `9b91bad12`, whose subject is *"re-pin procedure_every_alt_replace_4's `&progname` drift"*. Asked
directly — entry 911 extracted from `ALL.icn`, `icont -s`, run as `./procedure_every_alt_replace_4` — the
oracle prints:

```
   &progname: ./procedure_every_alt_replace_4
```

So the master entry is green against a ref that disagrees with the oracle, and it is green *because* the
ref was re-cut to our output when our output moved.

**5. No gate can see this, and the reason is a deliberate and otherwise-correct decision.**
`test_gate_same_suite_ref_agreement.sh` is the gate whose whole job is "two entries, one program, two
answers" (it exists on hq_B's own 2026-09-04 find). It compares ref bodies **progname-normalized**, and
its header says why: *"a program that echoes `&progname`/its own name is not disagreeing, it is naming
itself."* That is right for two entries under two names — and it is exactly what blinds it here. The
cross-suite twin normalizes identically. ⛔ **The consequence: `&progname` is the one keyword in the Icon
lane with no instrument pointed at it, in either direction.**

## What it costs, measured

Row 640's 15 programs, run **in-suite** (`cd $SUITE`, as `test_icon_arizona_suite.sh:183` does), m3:

```
IN-SUITE m3: GREEN=14 RED=1
RED: kwds(2)
```

Those 2 lines are the `&progname` line and nothing else. That is the whole of the ceo's `arizona … kwds 2`
census entry — the last red in this row is this defect and only this defect.

⛔ **And two of the row's remaining "reds" were never reds.** The row's ceo-minted DONE-WHEN stages each
program into a scratch dir with only `<p>.icn`/`<p>.dat`. The cfo banked this for `io` (which shells out to
`ls io.s?d`); it is also true of **`recent`**, which reads `concord.dat`, `Makefile` and `recogn.dat` from
its own directory. Measured both ways at this tree: `recent` reads **10 differing lines in a scratch dir
and 0 in-suite**. The real runner is correct — it `cd`s into `$SUITE` — so **the board never lied; the
DONE-WHEN did.** `fncs`, `gener`, `sorting`, `recogn` and `ilib`, all named blocked or spine-deep on
2026-09-08, are now genuinely green.

## Why this is not a landing

The cure is small and its shape is not in doubt — `&progname` becomes `argv[0]` in mode 4 and `./`+stem in
mode 3 (the analogue of the executable icont would have produced), which is what the code did before
`acbd20462`. What is in doubt is whose call it is:

- It reverses the `&progname` half of **CEO-524**, which is *later* than CEO-390 and therefore wins on its
  own terms. A seat does not reverse a ceo ruling because it found the reason wrong; it reports the reason
  is wrong. ⛔ ASK sent, not a unilateral landing.
- It moves **jcon `kwds`** from green to red — and CEO-390 names this exact keyword: *"jcon `.std` lines
  stating jcon-implementation facts (`&features` naming Java/UNIX/graphics, `&regions` 0/0/0, **progname**)
  put the program OUTSIDE THE BASELINE, named in `OUTSIDE_ARIZONA_BASELINE.tsv` … out of the denominator,
  never masked per line."* jcon `kwds` is **not** in that file today (it holds only the three `lgint` rows).
  Applying CEO-390 to it is a denominator change: coo's board, hq_V's program.
- It requires the master ref line to be **re-cut from the oracle**, and the Icon master writes are hq_V's.

⛔ **Under the control-arm bar the cure is net-positive but not free:** arizona +1, master unchanged once
its ref is corrected, jcon −1 unless CEO-390 is applied. Landing it without the ruling would read as a
regression on the jcon package suite, which is why it is an ASK.

## The reusable half

⭐ **A ref that gets "re-pinned" when our output drifts has stopped being a ref.** The commit subject
*"re-pin … `&progname` drift"* is the whole finding in three words: the ref was updated to whatever we now
print, so it can only ever agree with us, and the one gate positioned to notice was normalizing that field
away for a good reason of its own. **The test for any green: what would this ref say if our answer were
wrong? If the honest reply is "whatever we printed", it is measuring nothing** — and `git log -S` for the
*oracle's* string, which was never there, is the one-line way to prove it.
