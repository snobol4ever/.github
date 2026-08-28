# FINDING — the Pascal ref corpus is ONE COLUMN off, not 52 defects; and the self-referential oracle was hiding a single unimplemented rung behind 15 crashes

**Seat:** hq_C · **Date:** 2026-08-28 · **Row:** `pascal-refs-regen-from-fpc-oracle` (parked awaiting my ruling; now RULED and UNPARKED) · **Tree:** SCRIP `104ca904`, corpus `49adbb852` · **Instrument:** all 58 graded `corpus/tests/pascal/*.pas`+`.ref` pairs, `< /dev/null`, oracle `fpc 3.2.2` via `lib_oracle_flags.sh fpc_bin()` = `/usr/bin/fpc`.

## THE MEASUREMENT (three legs, whole corpus, not a sample)

```diff
  leg                          identical   whitespace-only   substantive   fails
  fpc -Miso   vs committed        5             48               4         1 compile-fail
  scrip       vs committed       30              -               4        24 crash / rc!=0
```

## 1. THE PARKED PREMISE DOES NOT SURVIVE MEASUREMENT

seat13 parked this row correctly — a one-way regeneration against a 90% mismatch deserved a ruling, and refusing to guess was the right failure direction. But the premise the park rested on was *"the refs look like they were captured from SCRIP's own output, so regenerating from fpc will make SCRIP's Pascal board regress hard."*

⭐ **The refs are not SCRIP's output today: 28 of 58 (48%) do not reproduce their own committed ref under `scrip`.** Whatever was true when they were captured, regenerating from the ruled oracle **cannot cause** a SCRIP regression — the divergence is already there, and is invisible only because `do-not-score-Pascal` is still in force. Meanwhile `fpc -Miso` agrees with the refs on **content** for 53 of 58.

The risk the park was protecting against has inverted: the dangerous state is the one we are in, not the one the regen would create.

## 2. THE 90% MISMATCH IS ONE COLUMN — ONE CONSTANT, NOT 52 DEFECTS

```
committed ref : "........11"    <- 10-column field
fpc -Miso     : ".........11"   <- 11-column field
```
Every one of the 48 disagreements is this. 11 is the width of the widest signed 32-bit integer (`-2147483648`), which is why fpc chose it; ISO 7185 leaves the default implementation-defined, so neither is wrong in the abstract — but the CEO ruling makes fpc the oracle, so **SCRIP's default integer field width moves 10 → 11.** One constant plus a regen.

⛔ **The mode matters and the wrong one manufactures a corpus-wide phantom.** Measured across every mode on a three-line program:
```
default / -Mtp / -Mdelphi / -Mobjfpc :  "42"          <- no padding at all
-Miso / -Mextendedpascal             :  ".........42" <- right-justified, width 11
```
Grading against an unpadded mode would produce a diff on essentially every file that says nothing whatever about correctness. **The ruling is `fpc -Miso`.**

## 3. ⛔ THE REAL FINDING: A SELF-REFERENTIAL ORACLE HID ONE RUNG BEHIND 15 CRASHES

The 24 SCRIP failures are **not 24 defects**. Clustered by first-line signature:

| count | signature |
|---|---|
| **15** | `[IDX] BOMB rt_assign_var: lvalue is not a variable (dtype=0) — string/record subscript assignment is the tvsubs rung` |
| 1 | `libscrip_rt: BOMB — bb_var_frame: PAS-DISPLAY L>=N fallback unimplemented` |

**One unimplemented rung — `tvsubs` — is the single largest cause of Pascal corpus failure.** Minted as `pascal-tvsubs-subscript-assign-rung`.

⭐ **And the reason it stayed invisible is the lesson, not the bug.** The ref corpus was captured self-referentially and Pascal is not scored, so nothing ever graded these programs against anything capable of disagreeing. **An oracle that is a copy of the thing it grades cannot fail.** These defects were not hidden by difficulty; they were hidden by the grading — the same family as the session's other silent-success defects (a cure compiled out by a flag, a regen that regenerated nothing, a reps=0 grid that agreed 7/7 because nothing ran, `OUTPUT` to an fd discarding every write).

## 4. THE RULING, AND ITS SEQUENCING

1. **Invocation: `fpc -Miso`.** (This is what the row was parked for.)
2. **Regeneration APPROVED**, with the width move 10 → 11 in the **same attributed commit** — either alone makes the board worse, so they are one change.
3. **Exception list is already sized:** 4 substantive `fpc`-vs-ref disagreements + 1 that will not compile under `-Miso` = 5 files needing a per-file reason. Never silent drops.
4. ⛔ **Lift `do-not-score-Pascal` only AFTER `pascal-tvsubs-subscript-assign-rung` lands.** Lifting it first puts ~24 known reds straight onto the announcement board.

## 5. ONE HAZARD MET WHILE MEASURING, WORTH THE LINE

`fpc` writes its output **next to the source**, not into the working directory — so a naive sweep over `corpus/tests/pascal/*.pas` litters the corpus with `.o` and binaries. Mine did, on the first pass; caught by `git status` and removed with `git clean` before anything was committed. Anyone re-running this measurement should copy the `.pas` files out first, as the final sweep here does.
