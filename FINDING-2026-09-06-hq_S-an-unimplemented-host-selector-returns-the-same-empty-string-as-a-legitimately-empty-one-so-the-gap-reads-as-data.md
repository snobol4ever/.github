# FINDING — an unimplemented HOST() selector returns the same empty string as a legitimately empty one, so the gap reads as data

**Seat:** hq_S (HQ-SUSTAIN) · **Date:** 2026-09-06 · **Tree:** SCRIP `e1c74e259` (cure), corpus `999270288` · **Build:** incremental `make`, `RT_OPT=-O0` · **Modes:** m3 and m4, agreeing

## THE WITNESS

`corpus/packages/snobol4/csnobol4_suite/float2.sno`, red in both modes on the pool snapshot
(`.github/probes/package-red-pools-2026-09-06.tsv`, `csnobol4 float2 m3:FAIL m4:FAIL`). One missing output
line, `OK`. The program:

```
	BITS = HOST(HOST_REAL_BITS)
	FT = 1. / 3
	THIRD = CONVERT(FT, 'STRING')
	EQ(BITS,64)					:S(DOUBLE)
	OUTPUT = IDENT(THIRD,"0.333333") "OK"		:(END)
DOUBLE	OUTPUT = IDENT(THIRD,"0.333333333333333") "OK"
```

## WHAT IT WAS NOT

The obvious suspect was `CONVERT(real,'STRING')` precision, and it was innocent — measured directly,
SCRIP already produces `0.333333333333333`, the 64-bit answer, byte-for-byte. Had the cure been attempted
there it would have been a change to a correct builtin chasing a defect one line away.

## THE DEFECT

`_HOST_` (`src/runtime/core/core.c`) implemented selectors 0–4 — the Catspaw SPITBOL set — and closed with
a bare `return NULVCL;` that swallowed the entire CSNOBOL4 2xxx extension range. `HOST_REAL_BITS` is 2301,
so `BITS` was the null string, `EQ(BITS,64)` failed, control fell to the **32-bit** branch, and `IDENT`
compared a correct 64-bit string against the 6-digit constant. Nothing errored. The program took a wrong
branch and printed nothing, which is the quietest failure a config query has available.

## WHY IT SURVIVED — THE PART WORTH KEEPING

**The null fallback is upstream-correct, and that is precisely what made it undiagnosable.** Measured against
the live csnobol4 oracle (`/home/resources/csnobol4/snobol4`): `HOST(9999)`, a selector no implementation
claims, returns `DATATYPE=STRING` and an empty value — it does **not** fail. So SCRIP's fallback matched
upstream exactly, and an unimplemented selector was indistinguishable, at the SNOBOL4 level, from a
selector that is implemented and legitimately empty. There is no probe a program can run to tell the two
apart, and no diagnostic anywhere in the chain. The gap did not look like a missing feature; it looked
like data.

This is the same shape as
`FINDING-2026-09-06-hq_S-a-refusal-that-fires-on-100-percent-of-inputs-reports-the-same-sigok-0-as-one-that-never-fires.md`,
filed by this seat earlier the same day: **a fallback that returns a legal value carries no hit rate, so a
path that never runs and a path that runs constantly present the identical face.** In the signature arm it
was a decline; here it is an empty string. The general form: *when the "I don't handle this" answer is
inside the codomain of the "I do handle this" answer, the instrument can no longer report on itself.*

## THE CURE

Eight selectors, answered as facts SCRIP can derive **about its own build** via `sizeof`/`CHAR_BIT` rather
than as constants transcribed from the oracle's output — so they stay true if the build moves:
2300 INTEGER_BITS, 2301 REAL_BITS, 2302 POINTER_BITS, 2303 LONG_BITS, 2304 DESCR_BITS (`sizeof(DESCR_t)`),
2306 CHAR_BITS, plus 2212 DIR_SEP `/` and 2213 PATH_SEP `:`. All eight now agree with the live oracle.

**2305 HOST_SPEC_BITS IS DELIBERATELY NOT IMPLEMENTED.** It reports the width of the SIL *specifier*, and
SCRIP has no specifier type — grepped clean. The oracle says 256; writing 256 here would be transcribing a
true fact about csnobol4 as a false fact about SCRIP, and it is the one selector in the family that is not a
measurement of this machine. No graded program reads it.

## SCOPE AND CONTROL ARMS

Corpus-wide, `HOST(` appears in 29 files. Every use outside this suite is selector 0–4 (getenv, argv,
system) — untouched. `corpus/tests/snobol4/ALL.sno`, the master regression suite, uses only `HOST()` and
`HOST(0)`; the no-argument form is **left alone on purpose**, since `ALL.ref` pins its current behaviour.
Of the named 2xxx selectors only `float2` (REAL_BITS) and `basename.sno` (DIR_SEP) are live, and
`basename.sno` has no `.ref` — not a graded pair.

Both graders were shown to be capable of failing in the same sitting, per this lane's standing rule (a
control that cannot fail is not a control): the identical m3 and m4 pipelines were run against `label.sno`,
still red for an unrelated `&CASE`/`LABEL()` folding gap, and both reported RED.

## ⛔ A RETRACTION, IN THE SAME DOCUMENT AS THE CLAIM

**An earlier revision of this FINDING asserted that `csnobol4/pow` is a dialect divergence and not a
defect, and warned the next walker away from it. That was wrong, and the reasoning was wrong in a way
worth keeping.**

The claim rested on two true readings: SCRIP prints `9^-1 = 0.111111111111111`, and so does the live
SPITBOL oracle. What made the conclusion false is that I ran `pow` **without `--compat=csnobol4`**, which
is the flag this suite actually grades under (`test_snobol4_csnobol4_suite.sh:142` sets `COMPAT`). Under
that flag SCRIP prints `9^-1 = 0` and `pow` **passes both modes**, diff clean. It appears in neither
`RED-M3` nor `RED-M4` on a board measured today.

`pow` **was** a genuine defect and **was already cured** before I looked at it — SCRIP `e7c45454e`, which
added the fourth compat switch `SCRIP_IPOW_CSNOBOL4` and kept SPITBOL's real for the default dialect. The
pool row `csnobol4 pow m3:FAIL m4:FAIL` is simply stale.

⭐ **THE SHAPE OF THE ERROR, WHICH IS THE SAME ONE THIS DOCUMENT IS ABOUT.** I graded with an instrument
configured to answer a narrower question than the suite asks, then reached for a **second** instrument —
the SPITBOL oracle — that shares the same blind spot, and read its agreement as confirmation. It agreed
*because* I had disabled the mode under test. A corroborating instrument only corroborates if its failure
mode is independent; two tools that are blind in the same direction agree most strongly exactly where they
are both wrong. This is the identical defect named in "WHY IT SURVIVED" above, committed by the person
writing it up, in the same sitting, about the same suite.

## WHAT IS ACTUALLY TRUE, AND IS THE USEFUL WARNING

`.github/probes/package-red-pools-2026-09-06.tsv` carries **five csnobol4 rows that are green** on a board
measured today: `convert`, `err`, `float2`, `pow`, `rewind1`. Four are stale-but-legitimate — `err` and
`convert` cured by hq_S at `7338727e0` and `00b62a274`, `pow` at `e7c45454e`, `float2` by this landing —
and `rewind1` is `PARKED_NO_REGEN` by hq_P ruling, so it is not a gradable row at all. The pool says 53 red
for csnobol4; the board says 48; the difference is exactly those five.

**A fixer minting flip rows off that snapshot will burn time on programs that are already green.** That is
the real hazard here, and it is worth more than the false one this document originally carried. Grade the
program yourself, under the suite's own flags, before minting the row.
