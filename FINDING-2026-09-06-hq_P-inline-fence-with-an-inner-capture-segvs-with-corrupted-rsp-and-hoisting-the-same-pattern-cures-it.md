# FINDING — an INLINE `FENCE` with an inner capture segvs with a corrupted RSP, and HOISTING the same pattern cures it

**Seat:** hq_P · **Date:** 2026-09-06 · **Mode:** FLEET-12 · **Row:** `snobol4-every-xfail-fixed-as-a-faulty-test-or-cured-as-a-defect`
**Trees:** SCRIP `6c378cb5e` · corpus `b9f408b5e` · incremental `make`, `RT_OPT=-O0`

## THE WITNESS, AND ITS CONTROL COMES FREE

```
          'a+b' FENCE((SPAN('abc')) . v0) REM            :S(OK)F(NO)
OK        OUTPUT = 'match'                      :(END)
NO        OUTPUT = 'nomatch'
END
```

SPITBOL prints `match`. **mode 4 prints `match`, rc=0.** **mode 3 dies SIGSEGV 139.** One program, two modes,
one of them provably right — so the defect is isolated to m3's machinery before a line of source is read.

Under gdb the fault is inside the m3 RX slab and **`rsp` is `0x0`** (siblings show `0xfffffffffffffff0`, i.e.
−16). The backtrace stops immediately, because the stack pointer is not a stack address.

## ⭐ THE BOUNDARY IS NAMED IN BOTH DIRECTIONS — THIS IS THE PART THAT MAKES IT ACTIONABLE

The row's own rule (b) asks whether a red fails **for the reason you think**, and says to build the shape that
IS in scope and confirm it goes green so the red has a named boundary rather than a vibe. Both directions:

| shape | m3 |
|---|---|
| `'a+b' FENCE((SPAN('abc')) . v0) REM` — **inline**, capture **inside** | **SIGSEGV** |
| `P = FENCE((SPAN('abc')) . v0)` then `'a+b' P REM` — **hoisted**, byte-identical pattern | **`match`** |
| `'a+b' FENCE(SPAN('abc')) . v0 REM` — capture **outside** the fence | **`match`** |

## THE CLASS, MEASURED AS A LADDER AGAINST THE ORACLE

**CRASHES:** `SPAN` · `BREAK` · `BREAKX` · `ARB` · `REM` · `TAB(1)` · `RTAB(0)` · a nested `FENCE` — and it is
**contagious through composition**: `ARBNO(SPAN('abc'))` crashes, `LEN(1) SPAN('abc')` crashes.

**GREEN:** `LEN(1)` · **`LEN(N)` with a variable `N`** · `ANY` · `NOTANY` · `POS(0)` · `RPOS(0)` · `NULL` · a
string literal · `ARBNO(LEN(1))` · concatenation of fixed nodes · alternation of fixed nodes.

⭐ **`LEN(N)` is the arm that settles what the axis is.** Its length is not known until match time, and it is
**safe** — so the discriminator is **not** static-vs-dynamic length. It tracks variable **EXTENT**: nodes whose
end is found by scanning or by the cursor, not by advancing a computed amount.

## MECHANISM — THE OPERAND-FRAME ALLOCATOR IS GATED BY GRAPH NAME

`blob_frame_scope()` (`src/emitter/emit.cpp:2431`) requires `g_emit.flat_pat`. The only site that sets it for
this path is `emit_jmp_entry_for_patproc()` (`emit.cpp:3603`), which opens:

```c
if (!pname || strncmp(pname, "PAT$", 4) != 0) return 0;
g_emit.flat_pat = 1;
```

A **hoisted** pattern is emitted as a `PAT$` proc and qualifies. An **inline** pattern is emitted inside its
statement's own graph, never matches the prefix, so the FENCE's operand frame is never allocated and the
capture's saved-RSP slot holds garbage. That is exactly why hoisting cures it.

## ⛔ WHAT I DID NOT DO, AND WHY

Two rows are already **DONE** on this precise ground — `565 emit-operand-frame-allocator-is-switched-off-by-name-for-any-non-pat-dollar-graph`
(hq_U) and `551 snobol4-fence-body-consumer-never-earns-a-frame-slot-...` (hq_S). The by-name gate is still
present and this shape still dies. **I did not re-cure shared-machine code that two other HQs just closed rows
on** — that is the FLEET-mode error CLAUDE.md names. Routed to hq_U as rank 4 with a DONE-WHEN **proven red**
(3 arms: the inline witness RED, the hoisted and capture-outside controls GREEN, refusing rc=2 if it cannot
grade all three). The first question for hq_U is whether this is **in scope of 565 and regressed**, or a
sibling shape 565 deliberately left — not something I should assume in either direction.

## ⛔ THE PAYLOAD, MEASURED RATHER THAN ASSERTED

This clears **exactly two** of the 35 SNOBOL4 master xfails — `fence_arb_span_replace_branch_1` and
`fence_span_rpos_replace_branch_1` — and **ZERO package programs**: gimpel, snoflake, csnobol4_suite, aisnobol
and dotnet contain **no instance of the shape**, so **no announcement cell moves.** It does occur in three of
Lon's own programs (`rcdiff.sno`, `Listen2Facebook.sno`, `WordNet.sno`).

⛔ **AND IT IS NOT THE WHOLE SIGSEGV GROUP.** Of the nine m3 SIGSEGV xfails, only **three** show a corrupted
RSP under gdb; the other six crash with a plausible stack pointer and are not shown to be this defect.

## ⛔ THE NEAREST NEIGHBOUR, WHICH A GREP WOULD HAVE SWALLOWED

`fence_capture_imm_capture_replace_branch_1` matches a naive "capture inside FENCE" grep and is **not a member**.
It is `FENCE(('ab' . v0) $ v0)` — a **fixed**-extent body with **two stacked captures** — and it is *near-inverse*
on the body axis:

| shape | m3 |
|---|---|
| `FENCE(('ab' . v0) $ v0)` — fixed body, two captures | **CRASH** |
| `FENCE((SPAN('abc') . v0) $ v0)` — **variable** body, two captures | **`match`** |
| `FENCE(('ab' . v0))` / `FENCE(('ab') $ v0)` — one capture | `match` |

My class needs a **variable** body and **one** capture; this one needs a **fixed** body and **two**. It is
already row 643, `CLAIMED:hq_S`. ⭐ **Three greps would have called them one class; the ladder separates them,
and the cure for either would have been a no-op on the other.**
