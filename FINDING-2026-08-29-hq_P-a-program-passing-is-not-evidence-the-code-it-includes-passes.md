# FINDING — a program passing is NOT evidence that the code it includes passes; and `beauty`'s `Read()` is CSNOBOL4-only

**hq_P · 2026-08-29 · corpus `20aea7eeb` · row `beauty-suite-ref-provenance`**

## The reasoning trap, stated first because it is the transferable part

Three beauty_suite drivers match their pinned `.ref` while live SPITBOL refuses to run them. Lon's steer was that
they all derive from `beauty.sno`, **which runs in both SPITBOL and CSNOBOL4** — so the natural inference is that
the subsystems must be portable too, and the divergence must be a pin or an extraction artifact.

Measured: `beauty.sno` (618 lines, 16 `-INCLUDE`s) does run under live `sbl -bf` with **rc=0, zero errors**.

⛔ **And it settles nothing, because `beauty.sno` never calls any of the routines involved.** Measured call counts in
`beauty.sno`: `Read(` **0** · `Write(` **0** · `Trace(` **0** · `MakeLeaf(` **0** · `MakeNode(` **0**.

ERROR 067 / 116 / 243 are **runtime** refusals. The parent *compiles* the included code — which is why it is green —
and never *executes* it. The drivers execute it.

⭐ **THE LAW: an inclusion relationship transmits COMPILE-time validity, never RUN-time validity. "The parent runs in
both engines" is evidence only about the paths the parent actually takes.** A green umbrella program is one of the
weakest portability signals available, and it looks like one of the strongest.

## The live defect this uncovered

`tests/snobol4/beauty_suite/ReadWrite.sno` is **byte-identical** to `corpus/include/ReadWrite.inc` — the library file
`beauty.sno` itself ships — and it contains:

```
Read  INPUT(.rdInput, 8, fileName '[-m10 -l131072]')
```

`[-m10 -l131072]` is a **CSNOBOL4-only file specification**; SPITBOL raises `ERROR 116 -- inappropriate file
specification for INPUT` (manual line 11434). ⛔ **So any program calling `beauty`'s `Read()` is CSNOBOL4-only
today.** This is not a stale test pin — it is a portability defect in shipped library code, and it was invisible
precisely because the one program that exercises the library never calls that routine.

## The three files are three different things

| suite file | vs `corpus/include/` | what it is |
|---|---|---|
| `ReadWrite.sno` | **byte-identical** to `ReadWrite.inc` | live library code — the defect above |
| `global.sno` | **byte-identical** to `global.inc` | live library code |
| `trace.sno` | same length, bytes differ | a **drifted** copy of `trace.inc` |
| `tree.sno` | 18 lines vs `tree.inc`'s 88; **both** its `DEFINE`d routines (`MakeNode`, `MakeLeaf`) are **absent** from the `.inc` | a separately-written **miniature** that only borrows the name |

⛔ They were being treated as one disposition question. They are three: a **library portability** question, a
**drift** question, and a **fixture** question. `tree.sno`'s `ARRAY('1:0')` (zero-length array, ERROR 067, manual
line 11380) is the same construct class as `ReadWrite`'s but sits in a fixture, not in shipped code.

## A method error of mine, recorded because it is the same shape

I first reported these pins as having **no** oracle provenance — "inherited wholesale from one4all, predating the
practice of pinning against an oracle here at all" — and called that *stronger* than the s191
`prototype-array-dim` case. It was wrong. Two of the three drivers name their oracle in their own header, two lines
from the top: `*  Oracle: snobol4 -f -P256k -Idemo/inc driver.sno` — and `snobol4` is **CSNOBOL4**.

⭐ **`git log --follow` answers WHEN a file arrived and whether it changed. It cannot answer WHICH ENGINE produced
its content.** I asked history a question only documentation could answer and filled the gap by inference. The
archaeology was sound; the question was wrong. **Provenance is often documentation, not history — read the file
before excavating it.**

## Status

Nothing changed. Asked, unruled. ⭐ Recommend the `ReadWrite` portability defect be split into its own row: it is a
real defect in shipped library code, not a bookkeeping choice, and it does not need the corpus-contract ruling the
other two are waiting on.
