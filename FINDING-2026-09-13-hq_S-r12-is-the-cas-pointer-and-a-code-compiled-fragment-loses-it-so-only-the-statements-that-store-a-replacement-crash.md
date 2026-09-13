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


---

# ⛔⭐⭐ CURED, AND THE DIAGNOSIS ABOVE IS SUPERSEDED ON ITS CAUSE (hq_S, same day, SCRIP after the cure)

Everything above is kept because its MEASUREMENTS are correct and its refusals were right. Its **cause** is not.
Read this section as the finding; read the one above as the trail that led here.

## What it actually is, in one sentence

**r12 is a machine-wide invariant in generated code and an ordinary callee-saved register inside the C
runtime.** Generated code establishes the CAS pointer exactly once, in the program's own prologue, and every
box from then on assumes r12 holds it. But C is free to keep its own value there — it only owes its own caller
a restore. So a compiled chain entered **from C** runs with **C's r12**, and the first
`subject pattern = replacement` inside that chain stores through it and dies.

The two trampolines that enter a chain from C — `rt_chain_enter` and `rt_chain_enter_v`,
`src/runtime/runtime_eval.c` — push and pop r12 correctly for their own caller and jumped into generated code
**without re-establishing it**. The cure is one instruction in each, seeding r12 from the same absolute slot
`main`'s prologue reads. It is safe on the cold path by construction: `rt_match_enter` already tests r12 for
zero and calls `rt_dcap_lazy_init`, so seeding an uninitialised slot takes the designed cold route.

## ⛔ What I got wrong above, and the shape of the error

The section above says the trigger is a DEXTERN library load with a **continuation line**, reached through
`EVALCODE`. **None of that is the class.** Ablated to **nine lines** with no `CODE()`, no library file, no
DEXTERN, no continuation line and no vendor package at all:

```
	DEFINE("PLAIN()W")
	S = CONVERT("PLAIN()","EXPRESSION")
	OUTPUT = "ev=" EVAL(S)
	OUTPUT = "done"				:(END)
PLAIN	W = ";+ tail"
	W POS(0) ';'  ANY('.+') = ' '
	...
```

Crashes in both modes, `n40_match_end_bx`, r12 = 0x68 — the identical signature. The oracle runs it clean.

⭐ **The ablation matrix is the part worth copying**, because each row removes exactly one ingredient and two
of them acquitted the whole story I had built: `EVAL` of a plain **string** instead of a converted expression —
**passes**. The same function called **directly** — **passes**. Dropping the `CODE()` layer entirely — still
**crashes**. Dropping the outer wrapper — still **crashes**. So the load, the library, the nesting and the
continuation line were all scenery, and the two survivors, `EVAL` of a `DT_E` and a replacement, were the whole
thing.

**What does survive from the old story, and it is the useful half:** the corrupt pointer is carried by *every*
chain entered from C, and only a statement that performs a **replacement** ever dereferences it. That is why
the class hid inside one vendor program for months — the two aisnobol entries that crashed were simply the only
ones whose loaded body reached a successful replacement. **A defect that every caller carries and one caller in
a hundred dereferences will always be found wearing that one caller's costume**, and the costume is what I
wrote down the first time.

## The gate, and why it has two control arms

`scripts/test_gate_sno_eval_of_a_converted_expression_keeps_the_replacement_pointer.sh` — **6 witness-modes
PASS=6 FAIL=0**, and **PASS=4 FAIL=2** with the cure stashed and the tree rebuilt, both reds on the witness.
The two control arms are the two ingredients removed one at a time (`EVAL` of a plain string; the same function
called directly). Both were green **before** the cure and stay green after: a cure that seeded r12 wrongly, or
that seeded it unconditionally where it must not be, reds them while the witness goes green. One arm alone is
passed by over-correcting.

## The remainder, named rather than claimed

aisnobol `TEST.sno` and `SIR.sno` **still crash**, and they are now a **different defect**: r12 reads a valid
pointer at the fault and the crash is stack exhaustion inside libc's `snprintf` under deep recursion — the
error-246 guard class. Not folded in, not claimed, and those two programs are not counted as flipped.
