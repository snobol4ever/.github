# FINDING 2026-08-17 s131 — THE LEAF-SUSPENSION WIDENING IS NOT MECHANICAL: SIX ADMITTED ON MEASURED GREENS, TWO DECLINED ON MEASURED LAW

**Seat:** Claude Opus 5. **Watermark:** SCRIP `41a0e324` (rebased onto concurrent Icon push `48201b2f`; gate re-proven there), corpus `05ef7042`.
**Predecessor:** `FINDING-2026-08-16-s130-leaf-cell-is-unconverted-flat-coordinate.md`.

## The claim under test

s130 cured `IR_MATCH_SPAN`'s raw-flat suspension cell by re-homing it into the
ONE activation-frame slot registry, and named the next rung:

> **(a) WIDEN TO THE SEVEN SIBLINGS** — BREAK/BREAKX/TAB/RTAB/REM/ARB/BAL carry
> the identical unsound `FR(x86_scratch_off)` spelling and are UNTOUCHED; the
> widening is **mechanical** (same accessor pair, same predicate, add the ops to
> `leaf_frame_candidate`'s whitelist) but earns its own blast radius.

The spelling premise is TRUE — verified by grep, all seven carry it. **The
"mechanical" conclusion is FALSE**, and taking the instruction literally would
have landed a fresh instance of the very defect s130 cured.

## What measuring first bought

Minted `corpus/probe/leafsib/` — eight witnesses, one per family member, each
modelled exactly on the cured `clobarm/clob_altarm_arm2direct_red` so the only
variable is the leaf op, each oracle-pinned by live `sbl` to `id=iffoo`.

| arm | m3 | m4 |
|---|---|---|
| default (OFF) | **0/8** | **0/8** |
| `SCRIP_SPAN_FRAME=1` (slice 2) | **6/8** | **6/8** |

Baseline detail: SPAN/TAB/RTAB/REM/BREAK/BREAKX `rc=139` in BOTH media;
ARB/BAL `rc=0` with a **silent wrong answer** (`parse fail`) — worse than a
crash, since nothing announces it. **m3 ≡ m4 in every row**, so the defect is
medium-independent, exactly as SPAN's was.

## ⛔ DECLINE 1 — BAL, AND WHY A GREEN WITNESS WOULD HAVE LIED

Per-template measurement of the offsets each sibling actually spends in its
scratch cell:

| op | offsets used | verdict |
|---|---|---|
| BREAK, TAB, RTAB, REM | `+0` | fits the window |
| BREAKX, ARB | `+0, +4` | fits the window |
| **BAL** | **`+0, +4, +8`** | **⛔ EXCEEDS** |

s130 measured the registry as tiling ONE 16B granule per slot with the base 8
bytes above the granule floor, so **a slot offers `d ∈ {0,4}` and nothing more —
`d=8` is the neighbour's cell.** BAL spends 12 bytes.

Admitting BAL would have handed a neighbouring ARBNO/CAPTURE-SAVE/FENCE1 cell
to BAL's third word: **the same cross-owner overwrite this rung exists to kill,
moved indoors.** The trap is that `leafsib_bal` would have gone **GREEN** while
silently corrupting a sibling class — the defect would have been invisible in
its own witness and would have surfaced sessions later as an unrelated ARBNO or
capture bug. This is the identical failure mode s130 already declined
`SPAN(*var)` for; BAL joins it in the 12B/16B wide class.

**The generalisable lesson:** in this registry, *a witness going green is not
sufficient evidence that an admission is safe*, because the damage lands in a
neighbour that the witness never exercises. Admission requires the offset audit,
not just the green.

## ⛔ DECLINE 2 — ARB IS A DIFFERENT DEFECT, AND THE MONITOR IS WHY WE KNOW

ARB was initially admitted (it fits the window) and stayed RED. MONITOR-FIRST
settled it — with one correction worth recording, because it is a reusable trap:

**The first monitor run was `csn spl` — two ORACLES and no SCRIP.** It reported
a step-8 divergence between csnobol4 and SPITBOL and said NOTHING about our
compiler. A conclusion was drawn from it and had to be withdrawn. ⛔ **Always
confirm SCRIP is a participant (`PARTICIPANTS="spl scr"`) before reading a
monitor verdict as a verdict on SCRIP.**

The correct run convicts cleanly:

```
DIVERGE step 6   (PARTICIPANTS="spl scr", leafsib_arb, SPAN_FRAME=1)
  5 | 3 | LABEL stno=INT=3              | LABEL stno=INT=3   <- last agreed
> 6 | 3 | @3 VALUE I = STRING(5)='iffoo' | LABEL stno=INT=5
```

The oracle assigns `I`; SCRIP branches to statement 5 — **the match fails
outright.** ARB never resumes into the arm interior to extend from null, so
**its suspension cell is never re-entered.** Re-homing an address that is never
reached is an unproven admission that widens every frame for no measured green.
ARB belongs to the **s120/s122/s123 arm-interior RESUME class** and waits for
that rung; its template already routes through `LFC`/`LFCQ`, which on the
declined arm returns the legacy spelling byte-identically, so that rung inherits
the plumbing and changes one word in the whitelist.

## ONE AUTHORITY — the accessor moved out of the template

s130 sited `spf`/`SPC`/`SPCQ` as file-statics in `bb_match_span.cpp`. The family
is **eight boxes in eight files**; spelling that fact eight times is the s68/s70
spelled-twice disease with seven chances to drift, and **one file left on the
legacy arm is a HALF-HOMED family** — precisely the cross-owner overwrite the
rung exists to kill. The accessor is therefore sited ONCE in `x86_asm.h` as
`LFC`/`LFCQ`, beside `FR`/`FRQ`/`RDD`/`RDQ` whose class it shares, and
`bb_match_span.cpp` is migrated onto it (26 refs, the exact count s130 claimed).

## Gates

* **Default arm byte-identical: 969/970** over 970 programs; the single mover is
  `parser/unary_not.sno` — the **known noise floor** s130 routed.
* **THE NULL IS NON-VACUOUS:** the baseline pair recorded against ITSELF returns
  the SAME single mover, so the instrument is honest and the 969 is real.
* ON-arm blast radius **50** (s130's SPAN-only was 36; six ops, so wider).
* **Scorecard IDENTICAL on both arms** — META 67.9, `beauty_suite` 41.2,
  `patterns` 82.4, `crosscheck` 93.3, **zero row movers ⇒ zero regressions.**
* Both declines **PROVEN INERT**: `--compile` byte-identical across both arms.
* Template-only + both-medium greps **0** on every touched file.
* Pre-existing, NOT this rung: `test_gate_template_medium_invisible.sh --strict`
  fails on `bb_glue_flat.cpp(4)` + `xa_flat.cpp(8)`, both untouched here.

## ⛔ What this rung does NOT do

**It does not move M1/beauty.** `beauty_suite` is 41.2 on both arms. The blocker
remains the `Command` non-leaf ALT-carrier class (s127/s128). This rung is a
prerequisite for it, not a cure of it — stated plainly so no later seat reads
6/8 as progress toward Milestone 1 that it is not.

## Next, in order

1. **Corpus-wide ON sweep, then Lon's flip grant** — the killswitch is still
   default OFF. Everything above is measured; the flip is a decision, not a
   measurement, and it is Lon's.
2. **The 12B/16B wide class** — two consecutive slots (or a widened granule) for
   BAL and `SPAN(*var)`. Moves ARBNO/CAPTURE/FENCE1 offsets, so its own rung and
   its own blast radius.
3. **The ARB arm-interior resume class** — s120/s122/s123 lineage; `leafsib_arb`
   is its ready-made witness and the monitor already names its first divergence.
4. **`unary_not.sno`** — initialise the assign-name string for the `~` unary arm;
   gate on three runs producing one md5, then re-measure the noise floor to ZERO.
   Until then every byte-identity claim over this corpus must exclude it or
   measure the null against itself, as this rung did.
