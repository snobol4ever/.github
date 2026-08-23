# FINDING — Milestone 1's `-O2` breakage is **two functions**: `c_rt_cap_open` and `rt_call_proc_descr`

**Seat:** `hq_C` · **Date:** 2026-08-22 (s258) · **Tree:** SCRIP `c4429b44` · **Class:** MEASURED, verified two-sided

## THE RESULT

Delta debugging (ddmin) over the 289 symbol-table-derived functions of `src/runtime/rt/rt.c` and `src/runtime/pattern_match.c`, bounds asserted before searching, converged in ~20 probes to a **minimal curing set of two**:

| de-optimised at `-O2` | beauty self-host | 17-line witness |
|---|---|---|
| `c_rt_cap_open` alone | **278** ⛔ | wrong (`fail2/calls=3`) |
| `rt_call_proc_descr` alone | **614** ⛔ | **correct** (`match2/calls=2`) |
| **both together** | **40,971 ✅ FIXED POINT** | **correct** ✅ |

`c_rt_cap_open` lives in `pattern_match.c`; `rt_call_proc_descr` lives in `rt.c` — **one in each file**, which is exactly why the earlier file-level bisect required both files at `-O0`.

## ⭐ THIS EXPLAINS THE 614

That third byte count has appeared all session and nobody could place it — *"rt.c alone de-optimised → beauty 614"*. It was always `rt_call_proc_descr` alone, since that function is in `rt.c`. **The three byte counts now decompose exactly:**

- **278** — both defects live
- **614** — `rt_call_proc_descr` cured, `c_rt_cap_open` still live
- **40,971** — both cured

Nothing about the byte counts is mysterious any more, and 614 is now a *diagnostic*: seeing it means exactly one of the two is fixed.

## THEY ARE THE TWO HALVES OF THE DEFERRED-CALL-IN-A-PATTERN PATH

A **pattern capture open** and a **procedure call by descriptor** — precisely what `*F()` with a nested match performs, and what beauty performs constantly while parsing SNOBOL4.

⭐ **Independent corroboration from the other lane:** hq_P, working performance and not coordinating on this, measured that ~54% of every instruction `roman` executes is a single deferred pattern node, and that ~92% of `NV_GET_fn` cost arrives through `rt_defer_nv_read` — also in `pattern_match.c`. Two HQs converged on the same subsystem from opposite directions. And `rt_call_proc_descr` was among the 102 pin-touching functions measured for mechanism 1, tying both mechanisms to one call path even though pin reservation alone does not cure beauty.

## ⛔ WHY ddmin AND NOT BISECT — THE TRANSFERABLE PART

A plain binary search over the *same 289 names*, with the same instrument and the same asserted bounds, converged on `rt_gvar_assign_pat_sz` — **which cures nothing alone**. Binary search assumes **monotonicity**: that any superset of a curing set also cures. This property is not monotone. With a two-function cure, a half containing only one of them fails, the search discards the half holding the other, and it terminates confidently on garbage.

ddmin tests **chunks and complements** and raises granularity when neither reduces, so a two-element cure survives the search. **The confirmation step — testing each candidate ALONE — is what caught the bisect's false answer and what validates this one.** It is not optional.

## WHAT IS STILL NOT FIXED

⛔ `optimize("O0")` on two functions **hides** the defect; it does not remove it. But the hunt has gone **261 files → 2 files → 2 functions**, and two functions is small enough to read. Next step: diff each function's `-O0` against its `-O2` disassembly and find what the optimiser does that the emitted-code contract cannot survive.

⛔ Mechanism 1 (the blob-pin conflict) remains separate and separately fixable; reserving the four pins build-wide cures the witness and **not** beauty. Do not ship either cure as "`-O2` is healthy" — that is the false-green trap one level up.

## WHAT THE DISASSEMBLY SAYS — AND WHAT IT RULES OUT

| function | `-O0` pins | `-O2` pins | pins-reserved build |
|---|---|---|---|
| `c_rt_cap_open` | **none** | rbx=5 r12=8 r13=9 r14=6 r15=8 | all 0 |
| `rt_call_proc_descr` | rbx=3 | rbx=11 r12=10 r13=6 r14=5 r15=4 | all 0 |

Both begin using the blob pins heavily only under optimisation — a compelling lead that is **wrong**. `-ffixed` demonstrably worked (all pins 0 in that build) and beauty still failed, so **pin usage is correlated with mechanism 2 and does not cause it.**

⛔ **Inlining is ruled out too, and my earlier negative on it was invalid.** At `-O0`, `c_rt_cap_open` calls `IS_FAIL_fn` and `IS_STR_fn`; at `-O2` both are inlined — tempting, because those are `DESCR_t` tag predicates and the original C-0 *was* a 32-bit-tag-compare defect. But `-O2 -fno-inline` **on both files** still yields 278. The earlier `-fno-inline` negative had been run on `rt.c` alone, and `c_rt_cap_open` lives in `pattern_match.c`. **That is the same subset error as the r14/r15 mis-refutation — committed twice in one session, by the seat writing the law against it.**

## THE SURVIVING SIGNAL: IT BREAKS AT EVERY OPTIMISATION LEVEL

`-Og` **278** · `-O1` 278 · `-O1 -fno-tree-dse` 278 · `-O1 -fno-tree-ter` 278 · **`-O1 -fno-tree-coalesce-vars` → 259**.

Even `-Og`, the most conservative level, fails. And `-fno-tree-coalesce-vars` produces **259** — a byte count seen nowhere else except under `-ffixed-r14/r15`. Coalescing therefore *moves* the symptom without curing it.

⭐ **Reading:** at `-O0` every local occupies its own stack slot; from `-Og` upward GCC coalesces variables and allocates registers. Something in these two functions requires two logically-distinct values to have **distinct storage** — an aliased `DESCR_t`, or a value an asm block assumes lives in memory. That is the shape for the next seat to chase, and it is a far narrower question than "why does `-O2` break SNOBOL4".

## MECHANISMS RULED OUT, WITH RECEIPTS

pins (reserved build-wide, `-ffixed` verified effective) · UB (UBSan `-fno-sanitize-recover`, silent) · inlining (`-fno-inline`, both files) · four individual passes · any single function (both are required) · the coroutine path (`rt_genp_*` is never called by the witness).
