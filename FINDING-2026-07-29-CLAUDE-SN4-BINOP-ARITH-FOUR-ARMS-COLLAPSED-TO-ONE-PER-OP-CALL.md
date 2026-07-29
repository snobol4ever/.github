# FINDING-2026-07-29-CLAUDE-SN4-BINOP-ARITH-FOUR-ARMS-COLLAPSED-TO-ONE-PER-OP-CALL

**Session:** s207 · **Repo:** SCRIP @ `ec307c3c` (base, clean main) · **Status:** IMPLEMENTED + GATED + MEASURED. Local only, NOT pushed.
**Directive of record (Lon, s207):** *"for now all these should be ONE CALL into the runtime. We'll optimize the inline later. Let's just reduce these to proper ADD calls if it +, and a SUB call if it -, etc."*

---

## ⭐ WHAT WAS THERE — THE SHAPE LON FLAGGED

`corpus/programs/snobol4/demo/arithmetic.s`, box `n7_binop_α`, from a four-line program. **44 instructions
for one `A + B`**, including a literally duplicated pair of loads:

```
mov eax, [rsp+16]   ; tag a
cmp eax, 100        ; DT_DATA
mov eax, [rsp+0]    ; tag b
cmp eax, 100
mov eax, [rsp+16]   ; tag a AGAIN — same address, same register, nothing written in between
cmp eax, 6          ; DT_I
mov eax, [rsp+0]    ; tag b AGAIN
cmp eax, 6
```

Four loads where two suffice, two call sites (`rt_binop_overload`, `rt_num_arith`), three labels, and
`mov r8d, <op>` shipping a **compile-time constant** to a callee that re-derived it by `switch`.

`bb_binop_arith.cpp` had **four arms**, each hand-rolling its own tag ladder:

| Arm | Guard | Was |
|---|---|---|
| 1 | `vfcb()` value-spine | inline int-int ADD/SUB/MUL + 2 call sites |
| 2 | `op_num_real` | bare `call rt_num_arith` |
| 3 | `!op_num_real` ∧ ADD..MOD | inline int-int + immediate elision + 2 call sites |
| 4 | POW/CUNION/CDIFF/CINTER | bare `call rt_num_arith` (⚠ **guard omitted `!vfcb()`** — for a vfcb POW graph arms 1 *and* 4 both emitted) |

## ✅ WHAT IT IS NOW

**Runtime** (`src/runtime/arithmetic.c`, +12): nine per-op entries via one `RT_BINOP_ENTRY` macro —
`rt_add` `rt_sub` `rt_mul` `rt_div` `rt_mod` `rt_pow` `rt_cunion` `rt_cdiff` `rt_cinter`. Each absorbs the
`DT_DATA` → `rt_binop_overload` dispatch, so **operator overloading survives with one call at the site**.
⭐ **Each entry carries its OWN body** — own `setjmp` bracket + its one int-int case — rather than delegating
to `rt_num_arith`. Two intermediate shapes were built and measured before this one: a `rt_binop_1(a,b,op)`
helper (**two** extra `-O0` frames) and a delegating macro (**one**). At `-O0` nothing inlines, so each hop
is a real frame; deleting the last one recovered `arith_mixed` from 0.783× to 0.938× (see the board).
`rt_num_arith` itself is UNCHANGED and still live — `by_name_dispatch.c:994` calls it, and it remains the
template's fallback for any op without a per-op entry.

**Template** (`src/templates/bb_binop_arith.cpp`, 166 → 94 lines): four arms → **two**, differing only in
addressing (value-spine `rspq` vs frame `FRQ`), identical in shape:

```
mov rdi/rsi/rdx/rcx <- a.tag a.val b.tag b.val
call rt_<op>@PLT
cmp eax, 99 ; DT_FAIL -> ω
store result
```

Frame-arm guard set to `!vfcb() && _.op_off >= 0` — exactly arm 3's coverage, subsuming 2 and 4 and
**closing arm 4's missing `!vfcb()`** (double emission).
⛔ **NO `x86_asm.h` CHANGE, NO NEW ENCODERS — TEMPLATE-ONLY.** This is the axis on which s206's SSE rung
was blocked: it needed `addsd`/`movsd` memory forms and therefore collided with the RTX-11/12 concurrency
warning. This rung does not touch that file at all.

**Result at the flagged site:** 44 → 13 instructions · `arithmetic.s` 404 → 271 lines · `mov r8d` op-shipping
sites **0** · one `call rt_add` / `rt_sub` / `rt_mul` / `rt_div`, one per operator in the program.

## ✅ GATES — WATERMARK RE-PROVEN LIVE BEFORE ANY EDIT, AND AFTER

```
BASELINE  m3 PASS=280 FAIL=54 · m4 PASS=276 FAIL=50 SKIP=8   (334)
AFTER     m3 PASS=280 FAIL=54 · m4 PASS=276 FAIL=50 SKIP=8   (334)
```

⭐ **Failure sets diffed line-by-line, not just counted: IDENTICAL. Zero movers in either direction.**
(Counts alone can mask an equal-size swap; the set diff cannot.) Baseline matches s206's record on this box.

**Cross-language (this edit is in SHARED `arithmetic.c` AND a SHARED template):** Icon 4/0 · Prolog 189/0.
⭐ **And these are real evidence here, not the §7 step-2b unmoved-battery FALSE CLAIM** — `bb_binop_arith`
is language-agnostic by the NO-LANGUAGE-PAST-LOWER rule, and `corpus/programs/icon/generators.icn --compile`
emits `call rt_add` ×2 / `call rt_sub` ×1. **Verified that the changed code is reached, rather than assumed.**
⚠ Snocone battery NOT run — `./beauty_full_bin` absent from the clone (environmental, not a regression).

## ⭐⭐ COLLATERAL DEFECT REMOVED — THE INLINE `idiv` HAD NO ZERO-DIVISOR TEST

Old arm 3 inlined DIV/MOD as `cqo ; idiv rcx` guarded **only** by `cmp eax, 6` (DT_I) tag checks. A zero
divisor therefore reached `idiv` and raised **SIGFPE — a hardware trap, not SNOBOL4 statement failure**
(`arithmetic.c:239` returns `FAILDESCR` for `ri == 0`; manual p.20 makes `1/0` an error, not a crash).
Present in **5 committed artifacts**: `arithmetic.s`, `calculator-1.s`, `calculator-2.s`, `json.s`,
`op_dispatch.s`. `INT64_MIN / -1` is the same hole (`#DE` overflow).
⚠ **EVIDENCE BOUNDARY, STATED PLAINLY:** the missing zero-test is proven **statically** from the committed
artifacts; the fix is proven **dynamically** (`X = 1 / 0` now fails the statement, rc=0). **The old binary was
not re-run to watch it trap.** Claiming a demonstrated crash would overstate what was measured.

## ✅ FALSIFICATION — TWO-SIDED, AND AIMED AT THIS RUNG'S *DISTINCTIVE* COMPUTATION

⭐ **s204's rule applied deliberately: the probe targets the thing this change INVENTED — the op→symbol
routing — not merely "does arithmetic still run."** RTX-5b's lesson was that a rung can pass every battery
while its own distinctive field stays unverified. Here the distinctive claim is *"`-` reaches `rt_sub`, `+`
reaches `rt_add`"*, so the probe corrupts `rt_sub` to compute `a.i + b.i`.

```
PROBE ON   m3 PASS=268 FAIL=66 · m4 PASS=264 FAIL=62      (12 movers EACH mode)
           demo arithmetic.sno -> 13 / 13 / 30 / 3        (subtraction returning addition)
RESTORED   m3 PASS=280 FAIL=54 · m4 PASS=276 FAIL=50      failure set byte-identical to baseline
           demo arithmetic.sno -> 13 / 7 / 30 / 3
```

**LOUD, not silent — no escalation needed.** The emitter genuinely selects the per-op symbol; the mapping is
load-bearing, not decorative.

## ⚠ PERF — THREE-WAY BOARD; THE DELEGATION HOP WAS REAL AND IS NOW RECLAIMED

Interleaved A/B/C, all three binaries retained and alternated **within** each round, round 1 discarded,
medians of rounds 2–5. **`RT_OPT=-O0`** (O0-DEV FACT RULE; no `-O2` directed).
**NEW1** = per-op entries delegating to `rt_num_arith`. **NEW2** = per-op entries with their own body
(own `setjmp` bracket + their one int-int case), which is what is in the tree.

| program | shape | OLD | NEW1 | NEW2 | NEW1 ratio | **NEW2 ratio** |
|---|---|---|---|---|---|---|
| `arith_loop` ×60 (60M calls) | pure INTEGER — lost its inline `add` | 622 ms | 964 ms | 798.5 ms | 0.645× | **0.779×** |
| `arith_mixed` (40M calls) | REAL+REAL — was already a bare call | 1820 ms | 2325.5 ms | 1940.5 ms | 0.783× | **0.938×** |

Arms never swap rank in any round. `arith_mixed` checksum **60000001** unchanged throughout.
⭐ **BOTH NEW2 BANDS WERE PRE-STATED AND BOTH HELD** — `arith_loop` predicted 0.75–1.00× (got 0.779×),
`arith_mixed` predicted 0.90–1.05× (got 0.938×). The NEW1 boards were pre-stated too: `arith_loop` 0.4–0.7×
HELD at 0.645×, `arith_mixed` 0.9–1.0× **FALSIFIED** at 0.783× — recorded as a miss, which is what pointed
at the delegation hop and produced NEW2.

⛔ **THIS IS STILL A REGRESSION AND THAT IS THE PRICE OF THE DIRECTIVE — the inline arms were deleted on
purpose. Recorded so the later inline rung has an honest floor to beat: 0.779× / 0.938×, not 1.000×.**

⚠⚠ **AN UNEXPLAINED DISCREPANCY — DO NOT PROMOTE IT TO A LAW.** NEW1→NEW2 removes **exactly one `-O0` call
frame per operation** in both programs, yet the reclaimed time is **2.76 ns/call** on `arith_loop`
(165.5 ms / 60M) and **9.6 ns/call** on `arith_mixed` (385 ms / 40M) — a 3.5× spread for the same deleted
frame. The 9.6 ns figure corroborates the 11.3 ns estimated independently from the NEW1 board; `arith_loop`
is the outlier. **Candidate causes not tested: single-core measurement instability (this box produced the
s200 1.340/2.497/2.606/0.510 spread on one program), or operand-shape effects per s188's law that call count
does not predict benefit. NO CAUSE IS ASSERTED. "One `-O0` frame costs N ns" is NOT established by this
data and must not be quoted as if it were.**

## ⭐ CORRECTION OF RECORD — s206's DOC-ABSENCE CLAIM IS FALSE IN THIS CLONE

`FINDING-...-RTX-6-INT-INT-ARM-ALREADY-EXISTS...md` §COLLATERAL item 3 states: *"`ARCH-SNOBOL4-RTX.md` and
`RULES.md` DO NOT EXIST IN ANY CLONE"* and infers the per-rung protocol is being followed from memory.
**Both files are present at the root of a fresh `snobol4ever/.github` clone and were read in full this
session** (`RULES.md` 26,061 bytes; `ARCH-SNOBOL4-RTX.md` 25,176 bytes). The s206 session's clone was
incomplete or it searched the wrong tree. ⛔ **This is the (a)-class rot the STALE-ORIENTATION rule names,
inverted — a document asserting an ABSENCE it cannot know — and it is the more corrosive direction, because
a reader who believes it stops looking for the protocol and starts improvising one.** Verify before
inheriting: `ls .github/RULES.md .github/ARCH-SNOBOL4-RTX.md`.
