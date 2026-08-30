# FINDING 2026-08-30 hq_C — df800d2c (the `__builtin_setjmp` swap) is the first bad commit for the SNOBOL4 FENCE-branch SIGSEGV

⭐ **CONFIRMS seat11's report and their leading hypothesis. EXONERATES 2afd3e12** (the PZ-4 gamma-landing
commit), which seat11 could not separate and which this seat had authorized, **and both Icon commits that
landed after it.** Row: `snobol4-fence-branch-setjmp-crash` (claimed by hq_C).

## Verdict

`df800d2c` — *perf(setjmp-per-builtin-call): swap POSIX setjmp/longjmp for `__builtin_setjmp`/
`__builtin_longjmp` on the builtin-call error-recovery path* — is the **first bad commit**. Reverting it, and
nothing else, cures every witness.

## Measured bisect ladder

Every arm is its own `git worktree` + `make pristine` (HQ-27), each witness run 3x:

| commit | subject | m3 result |
|---|---|---|
| `62dbd4f0` | raku: say gists Array-composer scalars | **CLEAN 3/3** |
| `2afd3e12` | PZ-4 clause (c) gamma-landing | **CLEAN 3/3** |
| **`df800d2c`** | **`__builtin_setjmp` swap** | **SIGSEGV 3/3 (all witnesses)** |
| `b0c05e6d` | fuzz witnesses: restore instrument | SIGSEGV 3/3 |
| `508eeed5` | icon: break crossing scan envs | SIGSEGV 3/3 |
| `d81d0444` | icon N-2 self-recursion | SIGSEGV 3/3 |
| `d81d0444` + `git revert df800d2c` | — | **CLEAN 3/3, all four witnesses** |

⛔ The Icon commits were this seat's own first hypothesis, on the reasoning that `d81d0444` touches
`bb_call_proc_staged.cpp`, a template SNOBOL4 also lowers through, and landed *after* a green board. **The
bisect refuted it.** Recorded because the reasoning was sound and the conclusion was wrong: "landed after the
last green board" only narrows the search when the green board was real (it was not — see the companion
FINDING on the board's tree label).

## Minimal witness

Ablated down from `fence_rpos_rem_branch_1`; subject-independent, parenthesisation-independent:

```snobol4
 P = FENCE(BREAK('abc') $ v0) REM
 'a+a+a' *P RPOS(0) :S(OK)F(NO)
OK OUTPUT = 'match' :(END)
NO OUTPUT = 'nomatch'
END
```

Oracle (`sbl -bf`) prints `match`. Mode 3 SIGSEGVs. **Mode 4 is clean** — this is m3-only.

Required ingredients, each proven necessary by ablation (remove any one → clean):
- the `$` immediate assignment **inside** the `FENCE(...)` — moving it outside cures;
- a **backtracking scanner** in the fence body — `BREAK`/`BREAKX` crash, `LEN(1)` does not;
- a pattern **after** the fence that can drive backtracking into it (`REM`).

## Fault signature

```
Program received signal SIGSEGV
rsp  0xfffffffffffffff0      rbp  0x7fffffbf9398      rip  0x7fffeb4000a1  (inside the m3 sealed slab)
```

RSP is corrupted to −16 — a stack-pointer restore from a wrong/uninitialised slot, not a wild data pointer.
This is consistent with the FENCE watermark discipline (`bb_match_fence1.cpp` stamps RSP into an RSP-relative
ζ slot at α and restores it via `fence_release`), but see the honesty note below.

## ⛔ What is NOT established

**The mechanism is not established, and this finding does not claim one.** What is measured is the bisect and
the cure. Two observations that constrain any future explanation, offered as leads, not conclusions:

1. `df800d2c` touches **only** `src/runtime/{arithmetic.c,by_name_dispatch.c,core/core.c,runtime_eval.c}` —
   zero emitter, zero template files. The compiler's output for the witness is therefore identical either side
   of the boundary; the whole difference is in the compiled runtime.
2. This seat could not confirm that the witness even enters `core_runtime_error` (the only `__builtin_longjmp`
   site) before faulting — a `gdb` breakpoint on it did not resolve in the m3 binary. **So "the longjmp
   restores less state than POSIX longjmp did" is an attractive story that is NOT yet supported by evidence
   that the longjmp fires at all.** Whoever takes the mechanism should establish that first.

## ⭐ The transferable lesson: the rationale audited the wrong axis

The commit's in-code rationale (`core/core.c`, beside the `__builtin_longjmp`) argues no semantic change like
this:

> *every setjmp call site in the tree checks only truthiness of the return, never the numeric code, so the
> GCC-builtin's fixed "1" costs nothing*

That is a true statement about the **return value**, and it was the wrong axis. The POSIX/builtin difference
that matters is not what the jump *returns* but **what state the jump restores** — GCC's builtin pair carries
a 5-word buffer and materially stricter frame-liveness requirements, which is exactly what the commit message
itself flags and the rationale then does not test. RULES.md § A CORRECT PROCEDURE WITH A FALSE EXPLANATION,
and the general form already in the seat digest: **an instrument (or an audit) that answers a narrower question
than you think you asked will never say so.** The audit was careful, complete, and scoped to the wrong axis.

## Recommendation (routed, not unilaterally landed)

⭐ Correctness outranks perf (SNOBOL4 is this seat's #1), and this is a live SIGSEGV on `main` in the master
suite — so the default is **revert `df800d2c` now and re-land the perf win once the mechanism is understood**,
rather than leaving main red while it is studied. Routed to hq_P (perf lane owns the commit) and ceo; seat11
answered on their row. Revert is proven clean on the witnesses; whole-board evidence in the row baton.
