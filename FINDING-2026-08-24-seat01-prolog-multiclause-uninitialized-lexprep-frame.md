# FINDING 2026-08-24 seat01 — the assertz/retract/abolish "class defect" is not a dynamic-database bug: EVERY 2+-clause Prolog predicate crashes, root-caused to `rt_jmp_frame_lexprep2` being an empty stub

**Row:** `prolog-assertz-retract-abolish-unmasked` (minted hq_C s272 from seat04's incidental finding). **SCRIP** `ab9c087c` · **corpus** `fea43840`, both pristine-built at `-O0`. **Not fixed** — this finding explains why the row's DONE-WHEN cannot be met by a scoped fix, and routes the real bug to where it belongs.

## What the task asked, and what's actually true

The task frames rung13/14/15 (0/5, 2/5, 1/5) as "assertz / retract / abolish semantics — the dynamic-database predicates... a class defect, not three bugs," and STEP 4 asks: is the cure confined to the dynamic-database builtins, or does it reach below the Prolog lowerer?

**It reaches below the lowerer, and it has nothing to do with assertz specifically.** Every one of the 12 failing cases (STEP 1 reproduced the board first: rung13 0/5, rung14 2/5, rung15 1/5, rungs 12/16-21 stay 5/5 — 12 failures measured, not the brief's 13; corrected number per THE LOOP's own rule) is a **SIGSEGV**, not a logic mismatch:

```
$ ./scrip --run rung13_assertz_assertz_unify.pl < /dev/null
Segmentation fault
```

STEP 2 said "read the failures before theorizing" — diffing actual vs `.expected` for all 12 showed **zero wrong-answer cases**; all 12 are crashes. That alone should have been the first tell: assertz/retract/abolish have *distinct* failure semantics (clause-ordering, logical-update-view, indexing, live-choicepoint abolish) — they do not all crash identically. A single shared crash across three unrelated predicate families is a sign the predicate identity is irrelevant.

## Minimal repro, ablated down from the corpus witnesses

```prolog
:- assertz(foo(1)).
:- assertz(foo(2)).
main :- foo(X), write(X), nl.
```
crashes. But so does the assertz-free control:
```prolog
foo(1).
foo(2).
main :- foo(X), write(X), nl.
```
**`--dump-ir` on both programs emits the byte-identical IR graph for `foo/1`.** assertz was never involved in the crash; `pld_mark_scan`/`pl_dyn_mark` in `prolog_lower.c` only affects call-site dispatch bookkeeping, and the compiled shape for a 2-clause predicate is the same whether the clauses came from source or got flagged dynamic. Further bisection:

| program | clauses | shape | result |
|---|---|---|---|
| `foo(1). main :- foo(X), write(X), nl.` | 1 fact | plain | PASS, prints `1` |
| `foo(1). foo(2). main :- foo(X), write(X), nl.` | 2 facts | plain | **SIGSEGV (nondeterministic)** |
| `bar(x). bar(y). bar(z). main :- bar(z), ...` | 3 facts | plain | **SIGSEGV** |
| `count(0). count(N) :- N > 0. main :- count(0), ...` | 2 clauses, 1 a rule | plain | **SIGSEGV** |
| `len([],0). len([H\|T],N):-len(T,N0),N is N0+1.` | 2 clauses, recursive | textbook list recursion | **SIGSEGV** |
| `corpus/tests/prolog/queens.pl` | real corpus program | N-queens | **SIGSEGV** (after printing its header) |

This is not an edge case. **Any user-defined predicate with 2 or more clauses crashes mode-3 execution.** It is not new, either: this repo's own `scripts/test_smoke_prolog.sh` already has two permanently-red rows for exactly this shape —
```
fact(a). fact(b). fact(c).                    main :- fact(X), write(X), nl, fail ; true.   → "clause"    FAIL (m2/m3/m4)
count(0) :- !.  count(N) :- N>0, ..., count(N1).  main :- count(3).                          → "recursion" FAIL (m2/m3/m4)
```
five lines above `write_atom`/`unify`/`arith`, which pass. Nobody had connected "two of five Prolog smoke tests are red" to "multi-clause predicates are broken" before now.

**It's nondeterministic**, which is why it reads as three separate semantic bugs rather than one crash: five consecutive runs of the identical `foo(1). foo(2).` program gave SIGSEGV, clean-exit-no-output, clean-exit-no-output, SIGSEGV, SIGSEGV. gdb with ASLR left enabled (gdb disables it by default — that's why the first two attempts showed "exited normally") caught a crash at PC `0x0000000000000011` — a small-integer value used as a jump target, not a real code address. Mode-4 (`--compile`, real ELF via gcc) does **not** crash on the same program, but also does not print the expected `1` — silent empty output, exit 0. That's the same "m3≢m4 divergence AND a silent wrong answer" class GOAL-PROLOG-100.md's PZ-0 section already names for a different witness (`plz_p8`); this is a second, more severe instance of it.

## Root cause

`lower_prolog.c:798` (`lower_pl_pred_graph_new`) compiles any 2+-clause predicate with `suspend_deliver=1`: clauses chain via `IR_SUSPEND` boxes (so backtracking can resume into the next clause), not the single-shot path a 1-clause predicate takes. A SUSPEND-capable graph needs a bigger, generator-shaped stack frame.

That frame's prologue is built in `src/templates/xa_flat.cpp:253` (`xa_flat_zframe_prologue_str`). It branches on `g_flat_dc_np`:
- `>= 0`: zero the frame region with an explicit `rep stosb`, then call `rt_icn_zframe_args_install` (a real init function, `rt.c:1209`) — **this is the path a 1-clause predicate takes.**
- `< 0` (the generator/SUSPEND path, `xa_flat.cpp:281-291`): **no zeroing at all** — it calls `rt_jmp_frame_lexprep2` instead.

`rt_jmp_frame_lexprep2` (`src/runtime/rt/rt.c:1612-1615`):
```c
void rt_jmp_frame_lexprep2(void *fb, long suffix_off, long region_bytes)
{
    (void)fb; (void)suffix_off; (void)region_bytes;
}
```
It is a complete no-op. Confirmed against the emitted `.s`: the 1-clause case emits `xor eax,eax; mov ecx,224; rep stosb` before its install call; the 2-clause case allocates a 608-byte frame and initializes **none** of it before `call rt_jmp_frame_lexprep2@PLT`. Whatever was previously on the stack at those addresses — the retry/resume continuation the SUSPEND box's second operand (`ab`, wired in `lower_pl_pred_graph_new:824-828`) depends on — is read as-is. That explains every symptom: nondeterminism (stack garbage varies run to run), the bogus small-integer jump target, why only 2+-clause predicates are hit (1-clause predicates take the zeroing path and never reach `rt_gen_save_wires`/lexprep2), and why it reproduces identically for assertz-derived and plain-source clauses alike (the IR and the frame-prep branch don't know or care where the clauses came from).

This is not a fresh discovery of the *stub* — GOAL-PROLOG-100.md's WORKLIST §0 already lists `rt_jmp_frame_lexprep2` as "an empty stub still called from every prologue." What's new here is the causal chain from that stub to a concrete, reproducible, nondeterministic SIGSEGV in ordinary multi-clause Prolog, independent of assertz/retract/abolish, plus confirmation it already shows up (unconnected) in this repo's own smoke suite.

## Why this finding does not include a fix

`xa_flat.cpp` is shared flat-frame machinery (its sibling function on the same branch is `rt_icn_zframe_args_install` — Icon-named), and GOAL-PROLOG-100.md is explicit and repeated that changes to this exact subsystem — generator/retained-frame handling for Prolog's multi-clause dispatch — are gated behind a hand-written, oracle-verified seed and **Lon's ruling before any lowering change** (PZ-1(c)/PZ-4, "SEED FIRST (C5 discipline)... LON RULES THE SEED BEFORE ANY LOWERING CHANGE"). A "just zero the frame like the other branch does" patch would very likely convert crashes into deterministic-but-still-wrong behavior rather than correctness (the retained state that needs real values — the resume continuation, the trail mark — needs *correct* initialization, not merely *defined* initialization), and it touches code the PZ ladder is actively, deliberately sequencing. That call belongs to whoever owns PZ-4, not to a row scoped as an assertz/retract/abolish bugfix.

## What this changes about the row's numbers

Prolog's "rung interp 110/164" watermark (GOAL-PROLOG-100.md s248 cursor) almost certainly already contains this bug's nondeterminism — some fraction of "passing" multi-clause-predicate programs are passing by luck of stack layout, not correctness, and re-running the same corpus could shift that number in either direction without any code change. Anyone re-deriving that watermark should know it's not as stable as a single number implies until this lands.

## Disposition

- The unmasking half of this row (corpus paths repointed post-re-grid to `corpus/tests/prolog/`, missing-corpus guard converted from silent SKIP to REFUSE rc=2 per the row's own ⛔ instruction) is done and pushed — see the task file LEDGER.
- The cure half is **not attempted**: DONE-WHEN (rung13/14/15 → 5/5) cannot be reached without the `xa_flat.cpp`/`rt_jmp_frame_lexprep2` fix, which is PZ-4/PZ-1(c) territory. Recommend HQ route this FINDING to whoever owns that rung, or mint it as its own dedicated rung given it blocks far more than three test files — it blocks correct execution of any multi-clause Prolog predicate, which is most of them.

## Addendum — oracle re-grading (per hq_C's task-file note: swipl/gprolog are now installed, re-grade before curing)

Ran all 12 failing `.pl` sources through the real oracle (`swipl -q -g main -t halt file.pl`, verified against a passing case first) and diffed against each `.expected` file — not against SCRIP's crashing output, which tells us nothing:

- **8 of 12 `.expected` files are byte-identical to SWI-Prolog 9.0.4**: all 5 of rung13, `retract_all`/`retract_basic`/`retract_mixed` (rung14), `abolish_then_reassert` (rung15).
- **3 of 4 rung15 (abolish) `.expected` files disagree with SWI's default behavior**: `abolish_existing`, `abolish_one_of_two`, `abolish_then_query_fail` all expect a post-abolish query to **silently fail** (`gone` / `cat_gone` / `no`), but SWI-Prolog 9.0.4 with default flags raises `error(existence_error(procedure, fact/1), main/0)` instead — `abolish/1` fully de-registers the predicate rather than leaving it dynamic-and-empty, so calling it is an undefined-procedure error, not a failure. This is ISO-standard behavior (`unknown` flag defaults to `error`), not a SWI quirk.
- GNU Prolog was **not cleanly measured** for these three: `gprolog --consult-file f.pl --entry-goal main --entry-goal halt` printed `warning: unknown directive assertz/1 ... directive ignored` for every `:- assertz(...)` line, meaning the facts were never asserted at all before the existence_error fired — an invocation-methodology confound (this form of top-level directive needs `:- initialization(main).` or an interactive `consult`, not the flags used here), not a trustworthy second oracle reading. Do not cite a gprolog number for these three from this session.

**This is a second, independent, smaller issue from the crash — it does not block or get blocked by the frame-init root cause above, but it does mean three of the twelve `.expected` files should not be treated as ground truth as-is.** Whoever owns the eventual cure should decide (or route to Lon) whether SCRIP's `abolish/1` should match ISO/SWI's existence_error semantics — in which case these three `.expected` files are the corpus defect and need correcting — or deliberately diverge, in which case the divergence should be stated, not silently encoded in three `.expected` files that look like ordinary fixtures. Not resolved here; STEP 3 was "grade against the oracle," not "rule on dialect," and the row's own STEP 4 discipline (read the diffs, don't guess) applies here too.
