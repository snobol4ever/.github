# HANDOFF — 2026-05-28 Opus 4.7 — Prolog BB — SWI-NEXT step 2 + bb_exec_node stack reduction

## Summary

Two independent, atomic changes; both green on all gates.

### Change A — SWI-NEXT step 2: once/1 intercept (mechanical, ~10 lines)

**File:** `SCRIP/src/lower/bb_exec.c` ~line 3270 (BB_PL_CALL handler)

**Diff:** Extended the existing call/N meta-fallback intercept from
```c
if (carity >= 1 && strcmp(callee, "call") == 0) { … }
```
to
```c
if ((carity >= 1 && strcmp(callee, "call") == 0) ||
    (carity == 1 && strcmp(callee, "once") == 0)) { … }
```

**Rationale:** `pl_call_term` (the carity==1 arm) commits to one solution via
`pl_invoke_var_goal` — no resume CP — so `once(G) ≡ call(G)` under this BB-graph
dispatch path. Standard Prolog semantics.

**Preserved invariant:** `call/N` for N>1 keeps its existing `carity >= 1` clause via
the OR-form. The prior session warned that accidentally narrowing this to
`carity == 1` would break SWI-2d/2e; the OR form does not.

### Change B — WAM-CP-6-prelude: bb_exec_node stack frame reduction

**File:** `SCRIP/src/lower/bb_exec.c` ~lines 3455, 4066, 4075

**Diff:** Three large stack arrays moved to `GC_MALLOC` heap:
- `Term *acc[4096]` (32 KB) — findall arm  → `Term **acc = GC_MALLOC(4096*8)`
- `Term *elems[4096]` (32 KB) — sort/msort arm  → `Term **elems = GC_MALLOC(...)`
- `int out_idx[4096]` (16 KB) — sort/msort arm  → `int *out_idx = GC_MALLOC(...)`

**Why:** `bb_exec_node` is a giant switch; under `-O0` (the project's default) GCC
reserves the per-case-block locals as separate stack slots rather than reusing
the same slab, giving the function a ~111 KB stack frame measured via gdb. With
an 8 MB stack that caps `bb_exec_once` mutual-recursion depth at ~72 frames.
Moving the three giant arrays off-stack drops the frame to ~30 KB, roughly
tripling effective recursion depth before stack overflow.

**Effect:** Closes one variety of the SEGFAULT-CLUSTER for plunit. A minimal
reproducer (4 FAIL tests, then a 2-element split_string pair) previously
segfaulted on the second split_string; now passes cleanly.

**Not a full WAM-CP-6.** This is a stack-pressure reduction, not LCO. Deep tail
recursion still grows the stack linearly; the proper fix remains the
`bb_exec_once` non-recursive refactor sketched in
HANDOFF-2026-05-28-SONNET-PROLOG-BB-WAM-CP-6-ANALYSIS.md. This prelude buys
roughly 3× headroom for the same number of activations.

## Honest .ref re-baseline

Three SWI .ref files updated to reflect honest output now that test bodies
actually run:

| File | Was | Now |
|---|---|---|
| `corpus/programs/prolog/swi_tests/test_exception.ref` | `EMPTY throw / EMPTY ex_coroutining` | `FAIL throw / FAIL ex_coroutining` |
| `corpus/programs/prolog/swi_tests/test_list.ref` | `EMPTY memberchk` | `FAIL memberchk` |
| `corpus/programs/prolog/swi_tests/test_misc.ref` | `EMPTY misc` | `FAIL misc` |

`test_string.ref` **left unchanged** at `EMPTY string / EMPTY string_bytes` — that
suite still segfaults mid-execution (see `Remaining bug` below), so a clean
verdict line never reaches the matcher. The 2-line miss is honest under the
matcher's current semantics.

## Gates (post-change)

| Gate | Score | Δ |
|---|---|---|
| GATE-1 smoke prolog | 5/5 ✅ | — |
| GATE-2 crosscheck | 132/0 (5 ORACLE_MISS) ✅ | — |
| GATE-3 mode-2 rung | 104/107 ✅ | byte-identical |
| GATE-3 mode-3 rung | 104/107 ✅ | byte-identical |
| GATE-4 mode-4 minimal | 4/4 ✅ | — |
| **GATE-SWI mode-2** | **55/57 (96%)** ✅ | **57/57 EMPTY → 55/57 honest** |
| **GATE-SWI mode-3** | **55/57 (96%)** ✅ | byte-identical to mode-2 |
| FACT RULE grep | 0 ✅ | — |
| smoke_icon / smoke_raku / smoke_snobol4 | 5/5 / 5/5 / 13/13 ✅ | — |

## Remaining bug surfaced — `bb=0x3` in `pl_node_to_term` (for next session)

After landing Change A + Change B, `test_string.pl` still segfaults after
running 8 tests. Root cause is **not** Change A or B — it is a pre-existing
type-confusion / memory-corruption bug exposed (not introduced) by the once/1
intercept making real test bodies execute. Confirmed by re-running at HEAD
baseline with both changes reverted: test_string then runs to completion as
EMPTY (no test bodies execute), so the bug was always there but masked.

### Diagnostic detail

`gdb` backtrace at crash:
```
#0 pl_node_to_term (bb=0x3) at bb_exec.c:122
#1 bb_exec_node (bb=0xe699d0) at bb_exec.c:3323
       pl_node_to_term(zc->args[ai])  /* ai==0 */
```

`zc` inspection at frame 1:
```
zc = { args=0x7ffff7ede540, nargs=3, callee="pj_rev", arity=3, cs=0x0 }
zc->args[0] = 0x3        ← bogus (small int — likely TERM_INT value)
zc->args[1] = 0x61       ← bogus (0x61 = 97 = 'a' ASCII)
zc->args[2] = 0x0
```

`zc->args` itself sits in a libgc anonymous-mapping rw-p region (heap), so the
array container is intact. Its **contents** have been overwritten by values
that look like small Prolog integers or atom codes.

### Hypothesis

`pj_rev/3` is deeply recursive:
```prolog
pj_reverse(L, R) :- pj_rev(L, [], R).
pj_rev([], R, R).
pj_rev([H|T], A, R) :- pj_rev(T, [H|A], R).
```

The recursive call must build a fresh `[H|A]` compound for arg 2 each time.
plunit calls `pj_reverse` on the suite list, which can be 8-10 entries. Each
recursion shares the same BB_PL_CALL node (same `zc`) but has its own
activation env.

Two leads worth investigating in order of likelihood:

1. **`zc->args[]` re-population on recursive entry.** `lower_pl_new_Call` allocates
   `zc->args` once at lower time. But under the new once-intercept code path,
   the synth-tree round-trip (`pl_term_to_synth_expr` → `interp_exec_pl_builtin`
   → `bb_exec_once` for user predicate) may go through a code path that
   incorrectly writes into `zc->args` instead of into `callee_env`. Search
   for any write `zc->args[i] = ...` outside `lower_pl_new_Call`.

2. **GC sweep collecting unreferenced compound args.** The intermediate `[H|A]`
   compounds built by `pl_node_to_term`/`term_new_compound` during recursive
   args evaluation may only be reachable through the C stack temporaries at
   line 3323 (`Term *caller_term = ...`) and the `callee_env` array
   (which is `calloc`'d at line 3317 — **not** `GC_MALLOC`'d). Under deep
   recursion, libgc may sweep them. If a freed Term* slot in callee_env is
   reused as a small-integer ALLOC for the next activation's TERM_INT, the
   subsequent zc->args[ai] reload through `pl_node_to_term` could see garbage.

The `calloc` at line 3317 is suspicious — it's the only non-GC allocation in
the BB_PL_CALL path. Suggest first experiment: change `calloc` to `GC_MALLOC`
and `free` to no-op (or `GC_free` if libgc has it), and verify whether the bb=0x3
crash disappears.

### Reproducer

```bash
cd /home/claude/SCRIP
cat > /tmp/test_string_var.pl << 'EOF'
:- use_module(library(plunit)).
:- begin_tests(string).
test(noop_1, fail) :- true.
test(noop_2, fail) :- true.
test(noop_3, fail) :- true.
test(noop_4, fail) :- true.
test(split_string, L == ["a", "b", "c", "d"]) :-
    split_string("a.b.c.d", ".", "", L).
test(split_string, L == ["SWI-Prolog", "7.0"]) :-
    split_string("SWI-Prolog, 7.0", ",", " ", L).
:- end_tests(string).
:- initialization(main).
main :- run_tests([string]).
EOF
# After Change B: above passes cleanly (was segfault).
# Full test_string.pl still crashes — that's the bb=0x3 bug.
PLUNIT=/home/claude/corpus/programs/prolog/plunit.pl; WRAP=/tmp/swi_wrap.pl
printf 'main :- run_tests.\n:- initialization(main).\n' > $WRAP
timeout 30 ./scrip --run $PLUNIT \
    /home/claude/corpus/programs/prolog/swi_tests/test_string.pl $WRAP
# Expect: 8 tests print, then "Segmentation fault"
```

For gdb session:
```bash
ulimit -c unlimited
timeout 30 gdb --batch \
  -ex "run --run $PLUNIT \
        /home/claude/corpus/programs/prolog/swi_tests/test_string.pl $WRAP" \
  -ex "frame 1" -ex "p *zc" -ex "p ai" \
  -ex "x/8gx zc->args" -ex "bt" \
  ./scrip
```

## NEXT recommended

In order of leverage and difficulty:

(a) **`bb=0x3` corruption fix** — start with the `calloc` → `GC_MALLOC`
    experiment described above (one-line change). If that resolves it, the
    root cause is GC reachability. If not, instrument `zc->args[ai] = X`
    writes with an assert that X looks like a valid BB_t* (e.g. low 12 bits
    of the pointer are within a small range from the bbg base). High leverage:
    unblocks test_string.ref + sets up a wider class of deep-recursion fixes.

(b) **WAM-CP-6 LCO proper** — the bb_exec_once non-recursive refactor (the
    sketch is in HANDOFF-2026-05-28-SONNET-PROLOG-BB-WAM-CP-6-ANALYSIS.md).
    Larger work (multiple sessions). Change B is the lightweight prelude.

(c) **WAM-CP-13** — mode-4 parity for 9/10/11. Long arc.

(d) **PL-RT-ASSERTZ** — dynamic clause support. Medium.

## Files touched this session

`SCRIP/`:
- `src/lower/bb_exec.c` — both changes (once intercept + 3 array migrations)

`corpus/`:
- `programs/prolog/swi_tests/test_exception.ref`
- `programs/prolog/swi_tests/test_list.ref`
- `programs/prolog/swi_tests/test_misc.ref`

`.github/`:
- `HANDOFF-2026-05-28-OPUS-PROLOG-BB-SWI-NEXT-STEP2-AND-STACK-REDUX.md` (this)
- `PLAN.md` (Prolog row update)
- `GOAL-PROLOG-BB.md` (state-at-HEAD update + SWI-2 step boxes)

## Critical warnings for next session

1. **`make libscrip_rt` is essential** after touching `bb_exec.c` — the script
   `scripts/test_prolog_mode4_rung.sh` and any mode-3 tests link against
   `out/libscrip_rt.so`. The handoff for SWI-NEXT step 1 already flagged this;
   it remains true.

2. **GC_MALLOC vs calloc semantics.** When attempting the calloc→GC_MALLOC
   experiment in `pl_invoke_var_goal` (pl_runtime.c:955) and `bb_exec.c:3317`,
   remember `GC_free` is a no-op-equivalent in libgc; the `free` calls at
   pl_runtime.c:968 and bb_exec.c:3334 must either be deleted or left as-is
   (GC tolerates `free` on its memory but it's a memory leak — small, since
   the env survives only briefly).

3. **The `bb=0x3` crash is NOT a regression** of the once/1 or stack-redux
   changes. Reverting Change A masks it (test_string runs as EMPTY); reverting
   Change B moves the segfault earlier (to stack-overflow). The bug is
   intrinsic to deep pj_rev recursion through the user-pred dispatch path.

## Three-Milestone authorship contribution

This session: Milestone 2 — incremental progress (BB executor stability under
deep recursion, plunit/SWI honest baseline).
