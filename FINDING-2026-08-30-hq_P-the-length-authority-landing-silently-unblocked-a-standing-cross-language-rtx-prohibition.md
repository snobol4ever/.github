# FINDING — the length-authority landing (`85b877d4`) silently inverted the measured fact behind a STANDING
# CROSS-LANGUAGE PROHIBITION, and deleted the perf win that prohibition was waiting for. `rtx_match.s`'s SLEN
# FINDING forbade any RTX fast arm keyed on `slen != 0` "until a LOWER-side rung populates it", on a measured
# ARM-FAST-B rate of **100% (2,000,001 of 2,000,001)**. Re-measured now: **0 of 1000.** Nothing linked the
# prohibition to the rung that satisfied it, so it went on forbidding — with a measured 100% beside it —
# something that had become free.

**hq_P · 2026-08-30**, found by applying hq_C's rule from the same afternoon (*a port's fidelity clause is a
dependency on the thing it copied, and nothing links the two*) as a **sweep of the asm twins** after changing a
C path. Comment-only landing, SCRIP `d7310af0`.

## 1. What the prohibition said, and what it was measured on

`src/runtime/rtx/rtx_match.s`, THE SLEN FINDING — careful, honest, and correct when written:
> *The obvious fast arm is "DT_S with a cached slen => return slen, no strlen." MEASURED on pattern_bt: that arm
> fires **0 times out of 2,000,001**, and the slen==0 arm fires **2,000,001 — ONE HUNDRED PERCENT**. Cause:
> **STRVAL (core.h) mints DT_S with .slen = 0, and only BSTRVAL populates it**, so a plain SNOBOL4 string
> assignment never carries its length. A port built on the cached-slen arm would assemble, gate green, be
> byte-identical over the whole suite, and **move NOTHING**.*
> *⇒ **NO RTX FAST ARM IN EITHER LANGUAGE MAY BE KEYED ON slen != 0 until a LOWER-side rung populates it.**
> Populating slen at assignment would **delete 2,000,001 strlens per run here** — worth more than this collapse.*

It even carried a second, independent confirmation from the Icon side (s217-ICN: `arr.slen == 0` on 100% of
arrivals). Two languages, two measurements, one conclusion. **All of it correct at the time.**

## 2. The premise is gone — measured, not argued

`85b877d4` landed Lon's length-authority ruling by changing **`STRVAL` itself** to measure once at construction
and carry the count. That is precisely the "LOWER-side rung" the note was waiting for.

| | recorded (pre-`85b877d4`) | re-measured now |
|---|---|---|
| ARM-FAST-B (`slen==0`, strlen owed) | **2,000,001 / 2,000,001 = 100%** | **0 / 1000 = 0%** |

⚠️ Different K — the note measured at `LT(N,2000000)`, mine is pattern_bt's default (1000 arrivals). **The
qualitative inversion is what is established**: an arm taking 100% of arrivals now takes none. I did not
re-run at K=2M, so the *count* of strlens deleted is the note's own figure, not mine.
⭐ **The win landed as a side effect of a CORRECTNESS commit and nobody claimed it** — it is not in
`85b877d4`'s message, because I did not know it was there.

## 3. ⛔ THE SHAPE — "FORBIDDEN UNTIL Y" IS A DEPENDENCY ON Y THAT NOTHING LINKS TO Y

This is hq_C's fidelity-clause family with the dependency pointing **forward** instead of sideways:
 · **hq_C's instance** (`rtx_icnrel.s`, cured `60f244e3`): *"the string arm reproduces strcmp's slen-IGNORING
   semantics BECAUSE THAT IS WHAT THE C TAIL DOES"* — true until the C tail changed.
 · **this instance**: *"forbidden UNTIL a LOWER-side rung populates slen"* — true until the rung landed.
⭐ **Both are comments that AUTHORISE rather than describe**, which is what makes them worse than ordinary stale
prose: a reader who checks them comes away *convinced*, and this one came with a measured 100% attached.
⛔ **And the search that finds them is not the obvious one.** Changing `STRVAL` and grepping for `STRVAL` finds
the C call sites; it does not find asm that *depends on STRVAL's behaviour without naming it*. hq_C's practical
form is the one that worked: **when you fix a C path, grep its RTX/asm/JIT twins for the justification, not for
the symbol** — the twin does not call the thing it copied.
⭐ **A "forbidden until" clause needs a tripwire on the enabling condition, not a note.** Nothing on earth was
going to point from `STRVAL`'s definition back to a prohibition in a `.s` file.

## 4. What this unblocks, and what is NOT claimed

✅ RTX fast arms keyed on `slen != 0` are now **legitimate on the SNOBOL4 side** — the census that forbade them
has inverted, so a cached-slen arm would no longer be vacuous. That is a real, named perf opportunity, and it
is the kind the note explicitly said was "worth more" than the rung it was attached to.
⛔ **NOT re-measured: the Icon twin.** The cause was the same `STRVAL`, so it is very likely inverted too — but
that is an **inference, not a measurement**, and it is written into the comment as such. **The Icon arm must be
re-censused before any Icon RTX rung is keyed on `slen`.** Repeating the note's own two-language claim on one
language's evidence would be exactly the error this finding is about.
⛔ **No fast arm was written.** This lands the retraction of the prohibition and the measurement behind it,
nothing more. ⛔ And the strlen-deletion figure (2,000,001/run) is **the note's number at its K**, not mine.
