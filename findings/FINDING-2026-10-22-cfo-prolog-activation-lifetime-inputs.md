# FINDING 2026-10-22 cfo -- the inputs of ARCH-PROLOG-ACTIVATION-LIFETIME.md, measured, and two defects found on the way

These are the cto's asks of 2026-10-22 13:0x CDT, on the Prolog switch row (CEO-1895 programme item 6): when a frame is released at a last call, what the trail keeps when a clause choice is popped, which variable stays representative, what the allocator does at the hard cap, and the chain across segments.

How it was read:
- SCRIP origin bcd2ef252 (binary built 12:53), mode 3 `./scrip p.pl` and mode 4 `--compile` + gcc + run;
- the shipped defaults (`-d128m -s4m`), stdin `/dev/null`;
- every reading set against `/usr/bin/swipl` 9.0.4 `-q`, the harness's own oracle invocation.
Mailed to the cto at 13:3x and 13:4x.

## (A) Last call -- when the frame is released

`bcps_block_tail_arm` (src/templates/bb/bb_call_proc_staged.cpp) releases the frame only when all three hold:
- the site is armed: seal 1 or IR_SEAL_TAIL_POP, and not the root graph;
- `r13` equals the frame's saved choice, so no choice point is younger than the frame;
- every argument cell passes the per-cell check. A link into this frame is followed (at most 4 hops). An unbound cell of this frame DECLINES.

Run 1,000,000 deep at 4 MB, both modes, swipl-equal:
- `count(N) :- N1 is N - 1, count(N1).`
- `mk(N, [N|T]) :- N1 is N - 1, mk(N1, T).`
- an accumulator, then `app/3` over the result

| shape (each `X(0) :- !.` plus) | deepest at 4 MB, m3 / m4 | bytes a level | swipl |
|---|---|---|---|
| non-tail `len([_|T], N) :- len(T, N0), N is N0 + 1.` | 10,439 / 10,957 | ~400 / 381 | 1e6 |
| last call after a live choice `cp(N) :- member(_, [a, b]), N1 is N - 1, cp(N1).` | 4,653 / 4,887 | ~897 / 854 | 1e6 |
| **last call passing a fresh unbound local** `lv(N, _) :- N1 is N - 1, lv(N1, _).` | 9,336 / 9,765 | ~447 / 427 | 1e6 |

Controls that run 1e6 deep:
- the head variable `lv(N1, Y)`, `lv(N1, f(_))` and `lv(N1, a)`;
- the choice removed by `once/1` or by a cut before the call;
- `X = _, lv(N1, X)` still declines.

**The WAM unsafe variable is never globalized**, so this tail arm declines forever.

## (B) The trail when a choice is popped

Trailing is conditional (`PL_U_TRAIL`, rtx_plunify.s):
- no entry when no choice point is live;
- a stack cell is trailed only if it is older than the choice's stack mark;
- a heap cell is trailed only if it is below the choice's heap mark.

**A cut never tidies.** No tidy code exists in `src/`, and `bb_cut` never touches `r12`. Witness:

```prolog
loop(0) :- !.
loop(N) :- member(_, [a, b]), !, N1 is N - 1, loop(N1).
main :- loop(NN), write(done), nl.
```

It leaves exactly 3 entries per cut. Read under gdb at `exit`: the trail top is 6,000,003 entries past the header at NN = 2,000,000, with the header word equal to `r12`. No older choice point exists to unwind them. Both gdb interrupts of a running loop landed in `rt_gc_trail_run` / `rt_gc_trail_roots_run`.

| NN | SCRIP m3 | swipl |
|---|---|---|
| 1,000,000 | 1.3 s, 157 MB | 0.4 s, 8 MB |
| 3,000,000 | 10.2 s, 392 MB | 0.4 s |
| 4,000,000 | 17.0 s, 509 MB | 0.6 s |
| 5,000,000 | 32.3 s, 626 MB | 0.6 s |
| 6,000,000 | **REFUSE rc 2** "trail arena exhausted after 16777215 conditional bindings (PL_TR_ARENA_LG2=29, 512 MB)", 43 s, 695 MB | 0.96 s, 8 MB |

The 3-a-cut slope predicts exhaustion at 5.59M. The same leak appears with:
- `( member(_, [a, b]) -> true ; true )`;
- `once(q(_))` over a two-clause `q/1`;
- `call(member(_, [a, b])), !`.

It does not appear with `\+ \+ member(...)` or with `once(true)`.

## (C) Binding direction -- which variable stays representative

There are two rules:
- **rtx_plunify.s** orders by address: a stack cell points to a heap cell, and a deeper stack cell points to a shallower one. The emitted `UNIFY_VALUE` hands two unbound cells to it.
- **`plc_unify_leaf`** (unification.c) allocates a fresh heap cell and binds BOTH variables to it.

The witness covers nine routes:
- `p1(X) :- Y = _, X = Y.`, and the same with the order reversed;
- `unify_with_occurs_check/2`;
- `call(=, X, Y)`;
- a built goal `G = (X = Y), call(G)`;
- two caller variables to one fresh local;
- a callee's local;
- `f(_)`, and `g(Y)`.

All nine agree with swipl in both modes. Each scrubs the stack (`deep(2000)`) after the call, then binds, then scrubs again before the read. No red arm shows that the scrub can catch a dangling read.

## (D) The allocator at the hard cap

`mk(N, A, L) :- N1 is N - 1, mk(N1, [N|A], L).` runs at 2,500,000 (1.3 s, 191 MB). At 5,000,000 it aborts:
- `[ZHP] heap exhausted AT THE HARD CAP ... 2794632 blocks live, cap hit 13 times, COLLECTIONS RUN 19 ... 32 payload bytes (48 with the header) of block kind 214`, then `error 204: memory overflow`, rc 1;
- this is a capacity verdict by the law's own test: collections ran;
- **a list cell costs 48 bytes** against swipl's 24;
- `-d512m` runs it.

**The same cap gives two behaviours:**
- on the emitted road it is FATAL: `catch/3` does not catch it;
- the C builtin `numlist(1, 3000000, L)` raises a CATCHABLE `error(resource_error(stack), _)` that is the heap: `-d512m` cures it and `-s64m` does not;
- swipl raises a catchable `resource_error` on both roads.

Garbage churn (50 x `numlist(1, 1000000, L)`) stays at 129 MB with and without an outer choice point.

## (E) The chain across segments

```prolog
gen(X) :- member(X, [f(a, [1, 2]), f(b, [3, 4]), f(c, [5, 6])]).
gen2(Y) :- member(Y, [g(p), g(q)]).
deep(X, Y) :- gen(X), gen2(Y).
main :- deep(X, Y), garbage(200), X = f(c, _), Y = g(q), write(X - Y), nl,
    findall(Z, (gen(Z), garbage(20)), Zs), write(Zs), nl,
    ( between(1, 3, I), garbage(50), I >= 3 -> write(i(I)) ; write(none) ), nl.
```

`garbage/1` loops over `numlist/3`, `atom_codes/2` and `atom_length/2`. It reads swipl's exact output in m3 and m4 at `SCRIP_GC_STRESS` 0, 1 and 7: 4, 76,193 and 10,887 collections (`SCRIP_GC_EXERCISE=1`), grew=0. At 100x the garbage, the stress arms exceed a 120 s ceiling, which is the cost of collecting at every safe point, not a verdict.

## Found on the way: a cut inside a disjunction arm is a silent wrong answer (the cto's row, minted)

```prolog
p(N) :- N > 0, ( member(_, [a, b]), ! ; true ), X is 1 - 1, write(X), nl.
main :- p(1), write(done), nl.
```

swipl prints `0` then `done`. SCRIP prints nothing and exits rc 0, in both modes.

`SCRIP_ZD_MAP` prints `CUT i=29 restores rsp to depth 224`, which is the arm's member exit. The DISJUNCTION's continuation (`VAR_REF X`) is planned at 80.

It needs all three of:
- a goal before the disjunction;
- a cut in an arm after a call;
- a fresh local bound after the disjunction.

Bracket: green at bc2d85fda, SIGSEGV at the spine flip e41bf8a6a, and a silent fail from 87d0c1917 through bcd2ef252.

The cto ruled it the planner's ("a cut is a DISCARD edge ... restores rsp to the ENTRY DEPTH the plan assigns to the box it continues at"). The witnesses are `directive_87`, `directive_88`, `directive_89`, `directive_90` and `cut_directive_11` in corpus tests/prolog (104fd7580, refs from swipl). The row is `prolog-a-cut-inside-a-disjunction-arm-restores-rsp-to-the-arms-exit-not-the-continuations-entry-ceo-1895` (rank 1, owner cto).
