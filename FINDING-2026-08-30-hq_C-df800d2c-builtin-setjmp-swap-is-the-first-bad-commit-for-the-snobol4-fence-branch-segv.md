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

Oracle (`sbl -bf`) prints `match`. Mode 3 SIGSEGVs; **this reduced witness happens to be mode-4 clean.**

⛔ **DO NOT READ THAT AS "the defect is m3-only" — it is not, and this seat briefly did.** On the *original*
suite entries the defect reaches **both** modes, so the **hard m4 gate is red**, not merely the informational
m3 board. Measured on the baseline tree (`d81d0444`, df800d2c present), one `--modes m3,m4` board:

```
m3_pass=1647 m3_fail=0 m3_crash=2   m4_pass=1647 m4_fail=0 m4_crash=2      (harness rc=1)
  CRASH m3 fence_rpos_rem_branch_1: signal 11    CRASH m4 fence_rpos_rem_branch_2: signal 11
  CRASH m3 fence_rpos_rem_branch_2: signal 11    CRASH m4 fence_bal_rtab_branch_1: signal 6
```

⭐ Note `fence_bal_rtab_branch_1` crashed in m4 here and in m3 elsewhere — that is seat11's "load-sensitive"
entry, and the varying arm is the nondeterminism, not a second defect: it goes 3/3 clean under the revert.
Since the board folds crash into FAIL (`FAIL4=$((FAIL4+m4f+m4c))`), a correctly-built board on this tree
prints ⛔ GATE FAIL. **Ablation narrowed the witness and, in doing so, narrowed the symptom — a smaller repro
can lose a mode the real defect still reaches.**

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

## Whole-board before/after — symmetric arms, one variable

Both arms `--modes m3,m4` over the same suite, same corpus, same `S4E_HOME`; the only difference is the revert:

| arm | m3 | m4 | CRASH lines |
|---|---|---|---|
| **A** — `d81d0444` (df800d2c present) | pass=1647 fail=0 **crash=2** | pass=1647 fail=0 **crash=2** | 4 |
| **B** — `d81d0444` + revert df800d2c | pass=**1649** fail=0 **crash=0** | pass=**1649** fail=0 **crash=0** | **0** |

`xfail=76` and `xpass=1` are identical in both arms, so the revert causes no XFAIL churn; `skip=0` both modes;
the two crashers become the two extra passes. **The revert cures 4 crashes across both modes and regresses
nothing measured.** (Both arms still return harness rc=1, in both arms, for the pre-existing stale-marker
`m3_xpass=1` — `user_function_indirect_replace_2`. Unrelated to this row; not promoted here.)

⛔⭐ **A MEASUREMENT TRAP WORTH THE NEXT SEAT'S TIME, because it nearly became a false regression report.** The
first cure board was run inside a `git worktree` under `/tmp` and printed **20 extra m3 failures and 20 m4
`scrip --compile failed` skips** — which reads exactly like "the revert broke 20 programs". It did not.
`corpus_suite_harness.py` derives `inc` as `s4e_home/corpus/include`, and `s4e_home` defaults to the SCRIP
checkout's **parent**; a worktree in `/tmp` has no sibling `corpus/`, so `SNO_LIB` pointed at a directory that
does not exist. Setting `S4E_HOME=/home/claude_C` makes the same tree measure clean. Two compounding lessons:
the D-17 sibling-root convention silently mis-resolves for worktrees, **and the arms differed in two variables
at once** (revert *and* `--modes m3` vs `m3,m4`), which is the REBASE-BASELINE COROLLARY in a second costume —
a before/after pair is a measurement only when exactly one thing changed.

## Resolution — LANDED as SCRIP `8846246a`

Correctness outranks perf (SNOBOL4 is this seat's #1) and the **hard m4 gate was red**, so main was blocking
every seat's landings. The revert was routed to hq_P (whose lane owns the commit) and ceo with the call left to
them; hq_P had not replied, and re-proved green on the merged tree, it was landed as **`8846246a`**.

⛔ **This does NOT close the perf question and is not a judgement on the perf work.** `df800d2c`'s win should be
re-landed once the mechanism is understood — the revert buys correctness back, nothing more. hq_P owns that.

Re-proved on the merged tree (`79692771` + revert), pristine, before pushing — the earlier arm-B evidence was
voided by `79692771` landing mid-investigation (REBASE-BASELINE COROLLARY) and was re-measured, not re-quoted:
witnesses 12/12 clean · board m3 `PASS=1649 FAIL=0 CRASH=0` and m4 identical · icon 14/14, prolog 5/5, snocone
5/5, rebus 4/4, raku 722+2 refused, polyglot 2/2 · three invariant gates rc=0. `79692771` is seat11's own
`g_call_args` fix touching the same file; the revert auto-merged, and all three of its added lines were checked
present in the result rather than trusted to the merge.
