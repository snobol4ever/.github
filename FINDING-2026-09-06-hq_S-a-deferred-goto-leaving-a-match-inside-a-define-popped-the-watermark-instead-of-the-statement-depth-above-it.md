# A deferred goto leaving a match inside a DEFINE popped the watermark instead of the statement depth above it

**hq_S, 2026-09-06, MODE OCTET.** Row `snobol4-aisnobol-wang-sigsegv-both-modes`. Cure in `src/emitter/emit.cpp`
(`zd_exit_pop_s`), gate `scripts/test_gate_sno_deferred_goto_from_match_inside_define.sh`, killswitch
`SCRIP_ZD_DEFER_EXIT=0`. Payload: aisnobol `WANG.sno`, which now matches `sbl -bf` in both modes.

## The defect

A SNOBOL4 goto whose target is COMPUTED (`:S($('L.' OP))`), taken from the SUCCESS branch of a pattern match, in
a statement inside a DEFINE body, left the statement at the wrong stack depth. The transfer landed on a label in
that same body, whose `:(RETURN)` then popped a data word as its return address and jumped to it — SIGSEGV 139 in
BOTH modes, at an address like `0x300000002`, which is a value, not a code pointer.

`rt_goto_resolve` was NOT at fault and this is worth stating because it is the obvious suspect: under gdb it
returns the CORRECT address (`LBL__L.A`). The target was always right; the stack under it was not.

## Three factors, each one measured by removing it

Every control below was green before the cure and after it:

| removed factor | witness | result |
|---|---|---|
| computed target → plain label | `:F(FR)S(L.A)` | green |
| conditional → unconditional goto | `:($('L.' OP))` | green |
| inside a DEFINE → main level | same shape, no DEFINE | green |
| match → assignment | `X = X :F(FR)S($(...))` | green |
| success branch → failed match's F branch | `X 'zz' = '' :F($(...))` | green |

## The arithmetic, and why one witness was not enough

`zd_exit_pop` returns a POP COUNT. For a plain `IR_STATEMENT_END` the count and the intended residual coincide
whenever `full == 2*wm`, which is true of every witness the watermark rule was originally written against — so
the ambiguity never showed. An `IR_GOTO_DEFERRED` chain breaks the tie, because it pushes its own resolve frame
on top of the statement.

Two witnesses differing ONLY in whether the match replaces:

| | statement depth | full (at the goto) | watermark | correct pop | residual |
|---|---|---|---|---|---|
| `X 'a' = ''` | 32 | 80 | 16 | 64 | 16 |
| `X 'a'` (bare) | 16 | 64 | 16 | 64 | 0 |

The correct pop is **64 in both**, while `full` differs by exactly the replacement's 16. The arrival depth was
measured directly, not inferred: `rbp-rsp` at the target label against `rbp-rsp` at a normally-reached statement
in the same body, in the same binary — 65856 correct, 65872 on the crashing path.

**Two formulas were written, built and REFUTED on this pair before the third stood.** `full - wm` fixes the
replacing arm and leaves the bare one dead; plain `full` does exactly the reverse. Only
`full - (stmt - wm)` — leave the statement's depth above the watermark — satisfies both. Both refuted arms
were tested off ONE build behind the same env switch, so the refutation cost two runs, not two rebuilds.

⭐ **The reusable part: a formula fitted to one witness of a family is a coincidence with a build number.** The
two arms here differ by three characters of SNOBOL4 source. Had only one been minted, either wrong formula would
have shipped green, with a gate to prove it.

## Scope, and why the boards cannot see it

Censused at the landing: Icon and Prolog emit **zero** `goto_deferred` boxes across 72 programs, and 1 of 32
sampled corpus SNOBOL4 programs reaches the arm. The change is emitted only at `IR_GOTO_DEFERRED` and only when
a match watermark and a statement depth both exist. ⛔ The byte-identity of the other frontends is therefore NOT
the claim being made — a sweep over programs with zero instances of the changed node prints exactly like proof
and is worth nothing (`RULES.md`, and hq_U's own near-miss on the same shape). The claim is the stronger one:
the node is not reached by those frontends, and the census is the evidence for it.

The sibling gate `test_gate_sno_byname_goto_zeta_unwind_in_a_loop.sh` (8 arms, 20000 iterations, pinning rsp
drift) stays GREEN under this cure — which is the arm that would have caught a residual that leaks per traversal.

## The scope proof hq_U co-signed on, which is stronger than the census above

⭐ **hq_U replaced my sampling argument with a PRODUCER census, and the difference is the whole lesson.** The
sole constructor of `IR_GOTO_DEFERRED` in the tree is `lower_snobol4.c`, five `lc_build` sites (861, 870, 882,
899, 2100); every other occurrence tree-wide — in every lowerer, driver, emitter, optimizer and runtime file —
is a read of `op ==`. **My 72-program census cannot rule out program 73; a producer census can.** It is a static
impossibility claim rather than a sampling one, and it is what belongs in a shared-node receipt.

⛔ **The law's own instrument disagrees with both of us, and that is worth recording.**
`grep -c IR_GOTO_DEFERRED src/lower/lower_*.c` returns `lower_prolog.c = 1`, so by the letter of SHARED-NODE
VERDICT SCOPE a Prolog board is owed. hq_U discharged it by looking: that hit is `lower_prolog.c:1203`, testing
`g->entry->op` — a READER of a node Prolog cannot build, structurally dead on a Prolog-only compile. **The grep
answers "does this file mention the token" and gets read as "does this frontend lower to this node"; the
denominator it prints is a CANDIDATE LIST, not the answer.** Same family as `command -v` answering "is it on
PATH" when asked "does it exist".

⛔ **The blast radius is wider than the guard, and the receipt must say which shape landed.** `zd_exit_pop` is
called UNGUARDED for every op at the gamma pop (`emit.cpp:2697`, `2717`); only the omega pop tests
`op == IR_GOTO_DEFERRED`. And `zd_stmt_exit_kind` is also true for `IR_STATEMENT` and `IR_STATEMENT_END`. So
editing the body rather than adding a function beside it moves the gamma pop for those two ops as well.
**What landed here: the body was replaced** — `zd_exit_pop` is gone and both call sites now go through
`zd_exit_pop_s`. **The behaviour for `IR_STATEMENT` and `IR_STATEMENT_END` is unchanged**: the new arm is
guarded on `op == IR_GOTO_DEFERRED`, and every other op returns `wm`, exactly as before. No second class rides
this board. (Those two ops are in any case built only by `lower_snobol4.c` — the other four lowerers never name
them — so the entire non-default branch is SNOBOL4-only by construction.)

## The board, and one number I am NOT claiming

SNOBOL4 master on the landing tree: **m3 PASS=1858 FAIL=0, m4 PASS=1858 FAIL=0 SKIP=0**. An hour earlier, on the
same corpus and the same src except this hunk, it read PASS=1857 FAIL=1 (`user_function_keyword_branch_3`,
hq_P's rank-0 row, the standing red named by CEO-359).

⛔ **I do not claim that flip.** Graded directly with the killswitch, the master reads `m3_fail=0` with the cure
ON *and* OFF — so this cure is not what changed it, and the earlier FAIL=1 does not reproduce here in either
position. Recorded as not-reproducible-on-this-tree, not as a flip and not as a standing red. The box was at
load 13–19 on 16 cores for both runs.

The one red in `make test` is `test_gate_pl_meta_call_reaches_control_constructs.sh` (Prolog `;/2` dispatch,
hq_C's lane). Proven not mine the cheap way: **identical, 3 FAIL lines, rc=1, with the killswitch on and off off
one build.** It surfaced only because the board stopped failing earlier in the recipe and let the run reach it.

## Prior art on the same node, and what it got right

`4e81927d5` introduced the watermark rule and added `IR_GOTO_DEFERRED` to `zd_stmt_exit_kind`. Its reading of the
mechanism was correct and its own gate still passes; the rule was simply degenerate on its witness. Its commit
message also called this correctly in advance: *"NOT the WANG/POKEV_driver cure ... a separate mechanism."*
