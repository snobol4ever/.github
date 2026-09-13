# FINDING 2026-09-13 hq_S — r12 is the CAS pointer, a CODE()-compiled fragment loses it, and the only programs that crash are the ones whose replacement actually succeeds

**Row:** `snobol4-aisnobol-dextern-loading-a-library-function-with-a-continuation-line-sigsegvs-in-both-modes` (hq_S, rank 0, minted and claimed 2026-09-13). **PARKED, not cured** — the cure sits in a node this concern does not own.
**Tree:** SCRIP `ddfe8159e`, corpus `f303218ad`, incremental `make`, `RT_OPT=-O0`.
**Subject:** `corpus/packages/snobol4/aisnobol/TEST.sno` and `SIR.sno`, run as the package ships them.

## The symptom, and how much of it is real

`TEST.sno` and `SIR.sno` SIGSEGV (rc=139) **in both modes** where `sbl -bf` runs clean: 823 deterministic
lines for TEST, 80 for SIR (the oracle was run **twice against itself** on each before either was used as a
ref — 0 diff lines both, so these refs are stable). SCRIP prints **19 correct lines** of TEST and then dies.

Ablated by call order: `ABS`, `SIGN`, `ADD1`, `SUB1`, `FLOAT`, `DFLOAT` and `MINUS` all answer correctly;
**`FIX` is the first to crash**, and `ROUND` crashes because its body calls `FIX`. The argument does not
matter — `FIX(3.7)` with a literal dies exactly like `FIX(P...I.)` with a variable — and
`CONVERT(3.7,'INTEGER')`, the only thing FIX's body does, is correct in all three engines standing alone.

## What the crash is

**`r12` is the CAS pointer** — the pending-replacement stack that a `subject pattern = replacement` statement
uses. `bb_match_end.cpp:87` stores the replacement length through it (`mov [r12], eax`), `bb_match_replace.cpp`
pops it, and `bb_match_begin` saves it at `[rbp-8]` and restores it from there. Every box therefore **assumes
the pointer is already in r12**, because it is established **exactly once, in the program's own prologue**:

| mode | site | instruction |
|---|---|---|
| 4 | `src/driver/scrip.c:1507` (emitted into `main`) | `mov r12, qword ptr [0x70000000]` |
| 3 | `src/driver/scrip.c:105-108` (`icn_zf_main_call` inline asm) | `mov $0x70000000, %r12` / `mov (%r12), %r12` |

The fault is `n867_match_end_bx+180`, `mov %eax,(%r12)`, with **r12 = 0x68** — 104, not a pointer.

## Where it is lost, measured

r12 holds a valid `0x7fffee1ff030` through **1602 by-name gotos and 1738 match entries**. The first by-name
goto carrying a bad r12 is the one immediately after:

```
goto_resolve 'EVALCODE' r12=0x7fffee1ff030 g_line=0
goto_resolve 'LOADEX1'  r12=0x68           g_line=128
```

⭐ **`g_line` reading ZERO is itself the tell** — a `CODE()`-compiled fragment carries no source line, so that
one field says *we are inside runtime-compiled code* without needing any other instrument.

⛔ **The writer is NOT yet named, and this FINDING does not name it.** Stepping forward from that goto with the
breakpoint disabled puts the change 184 instructions in, inside the RX slab where the fragment has no symbols;
`nexti` in that unsymbolised region reports the writer as a one-byte `push rsi`, which cannot be true. That is
an instrument limit, not a result, and it is recorded as one.

## ⭐ Why FIX and ROUND and nothing else — the part that generalises

Every `DEXTERN`'d load runs the same `LOADEX` loop, so every one of them very likely runs with the same corrupt
r12. **Only FIX's library body carries a continuation line**, and a continuation line is the only thing that
makes LOADEX's replacement statement (`SPITCORE.sno:135`, `X POS(0) ';' ANY('.+') = ' '`) actually **succeed**
and therefore actually **store** through r12.

So: **a corrupt pointer that every fragment carries is dereferenced only by the statements that perform a
replacement.** The class is wider than these two programs and is silent everywhere else — which is the reason
it has survived, and the reason a cure must not be graded on "TEST stopped crashing".

## Ruled out by measurement, so nobody repeats them

- The argument to `FIX` — literal and variable crash identically.
- `CONVERT(x,'INTEGER')` standing alone — correct in oracle, m3 and m4.
- The replacement statement alone; the whole `LOADEX2` loop rebuilt over an `ARRAY`; the same loop rebuilt over a real file association — **all three correct in all three engines**.
- A `CODE()`-compiled fragment entered by a by-name goto that performs a replacement inside itself — also correct.
- A memory corruption of the CAS base: the slot at `0x70000000` is written once (`0 -> 0x7fffee1ff030`) and never again, and r12 is intact at **every** `code_at` entry (29 consecutive calls). **The clobber is a register clobber.**

## Why this is an ASK and not a landing

The two candidate cures are a box template using r12 as a scratch without saving it (`src/templates/bb`), or a
fragment entry that does not re-establish the CAS pointer the way `main`'s prologue does
(`emit_jmp_entry_for_chain` / `emit_chain`, `src/emitter`). **Both are shared nodes, and hq_U owns the register
planes under the NONET cut**, so this concern measures and routes rather than lands. The next productive step
is not more gdb: emit the fragment to TEXT and read which box in it writes r12, against the box list of a
fragment that does not.

⛔ **Grade any cure on the program's OUTPUT against the oracle, never on rc** — a build that merely stopped
crashing and printed nothing would also stop dumping core.
