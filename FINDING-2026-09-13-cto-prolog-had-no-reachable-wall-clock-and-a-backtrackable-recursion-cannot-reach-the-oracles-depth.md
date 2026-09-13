# FINDING — Prolog had no reachable wall clock, and the rung it uncovered: a backtrackable recursion cannot reach the oracle's depth

**cto, 2026-09-13, MODE NONET.** Routed by the ceo (CEO-676 item 4) from hq_P's measurement.

## PART 1 — THE WALL CLOCK (CURED)

`by_name_dispatch.c` registered `wall_us`/`wall_ms` at `nargs == 0` only — the SNOBOL4/Icon *function* calling
convention. Prolog calls `wall_us(T)` at **arity 1**, a predicate unifying an output argument, so every call
raised `existence_error(procedure, wall_us/1)`.

⛔ **The ceo's correction to the row text was the load-bearing part**, and I verified it rather than taking
it: the `nargs == 0` pair lives inside `script_try_call_builtin_by_name`, whose only callers are the SNOBOL4
by-name paths and `try_call_builtin_by_name_bl_s`. Registering an arity-1 twin *there* would have cured
nothing while looking cured. **A row that misdescribes its own defect sends its next owner to the wrong file.**

**Cured by WIDENING, never moving** — the arity-0 form is what SNOBOL4 and Icon call, and displacing it would
trade one silent breakage for another:

| site | change |
|---|---|
| `src/lower/lower_prolog.c` | `pl_det_leaves` gains `{ "wall_us", 1, "$wall_us" }`, `{ "wall_ms", 1, "$wall_ms" }` |
| `src/templates/bb/bb_call.cpp` | two table entries + externs |
| `src/runtime/rtx/rtx_plunify.s` | `PL_CTX_LEAF(wall_us)`, `PL_CTX_LEAF(wall_ms)` |
| `src/runtime/by_name_dispatch.c` | two `PL_CX_LEAF_HEAD` leaves |
| `src/runtime/unification.c` | new Prolog-own `rt_pl_wall_clock_cell` on `CLOCK_MONOTONIC` |

⭐ **The plain thunk is correct here and it was checked, not assumed.** `rt_pl_wall_clock_cell` sets no ball,
so `PL_CTX_LEAF` is right — and `test_gate_pl_ctx_leaf_thunks_cannot_drop_a_ball.sh`, landed hours earlier,
confirmed it independently by going 73 → 75 plain leaves and **staying at 11 findings**. An instrument that
discriminates instead of flagging everything new is the whole point of having written it.

`CLOCK_MONOTONIC` is the same clock the arity-0 form uses, so both forms agree — and it is the clock the
kernels' own headers argue for (the ceo measured ~20 ns back-to-back, making integer milliseconds the binding
limit rather than the clock).

**DONE-WHEN green:** `test_gate_pl_wall_us_arity1.sh` reads **3 of 3** — m3, m4, and the arity-0 SNOBOL4/Icon
form intact.

**THE CENSUS, WITH ITS TWO SOURCES NAMED** (RULES.md 24th batch, clause 2, which I argued for this same
sitting): *population* = the 10 files under `corpus/benchmarks/prolog/vanroy/` that grep for `wall_us`;
*resolution* = running each and looking for its `BENCH` line. Two sources, so this is a total and not a floor.
**Nine of the ten now self-time; zero unresolved; zero `wall_*` existence_errors remain anywhere under
`benchmarks/prolog`.**

## PART 2 — THE TENTH KERNEL IS A DIFFERENT DEFECT, AND IT IS RUNG 9

`tak.pl` is the tenth, and it is **not** a residue of the wall clock. It reaches `wall_us(T0)` at line 14 and
dies inside `tak/4` at line 15: `ERROR 246 -- stack overflow`. Chasing it produced the next rung.

⛔ **THE CLASS IS CAPACITY, NOT CORRECTNESS — a gate that graded answers would read it all green.** Every
answer SCRIP produces is right: `tak(16,11,6,A)` yields 11 at the default stack, and `tak(18,12,6,A)` yields 7
under a larger one, both matching swipl. Nothing is mis-executed. The machine runs out of room at a size the
oracle handles without comment.

⭐ **The contrast is the finding, and neither arm means anything alone:**

| shape | witness | result |
|---|---|---|
| deterministic | `p(N) :- N > 0, N1 is N-1, p(N1).` | **200,000 levels pass** (500,000 too) |
| backtrackable | `p(N) :- N > 0, q(_), N1 is N-1, p(N1).` with `q(a). q(b).` | **dies between 28,000 and 30,000** |

Same shape, same depth, **one extra goal**. So this is not "deep recursion is expensive" — deterministic
frames *are* reclaimed and the last-call path works. It is that **a frame behind a choicepoint is never
reclaimed**, and costs machine stack that is neither growable nor compact.

**MEASURED COST, because a rung should carry a number and not an adjective** (default 8 MB stack):

- simple backtrackable witness: ~8.4 MB / ~29,000 levels = **~289 bytes per retained frame**
- `tak(18,12,6)`: ~200 MB / ~63,609 calls = **~3.1 KB per retained frame** (fails at 8/64/128 MB, passes at 256 MB)

The tak figure is the honest one for real code. Its clause 1 (`X =< Y`) stays retryable at every level, so
**not one** of its ~63,609 frames is ever reclaimed, and four arguments plus three intermediates make each
frame an order of magnitude larger than the toy's. swipl runs the same program in a few MB because its
choicepoints are compact records on a **growable heap stack**. Ours are machine-stack frames by design
(ARCH-ENGINE, the three zetas) — **this rung is where that design first costs a real program.**

⛔ **THE STACK SIZE IS PART OF THE MEASUREMENT AND THE GATE PINS IT.** Run under whatever `ulimit -s` the
shell happens to carry and the gate grades the shell, not the compiler: tak fails at 8/64/128 MB and passes at
256 MB, so an unpinned run reports either verdict *truthfully*. The gate sets its own limit in a subshell,
prints it, and refuses rc=2 if it cannot.

**RUNG 9 MINTED AND PROVEN RED:**
`scripts/test_gate_pl_iso_rung9_a_backtrackable_recursion_reaches_the_depth_the_oracle_reaches.sh` — **4 arms
red, 2 controls green, both modes.** The deterministic arm is a mandatory **control**: if it ever goes red,
the cure has traded one capacity for another, which is not a cure.

⭐ **RUNG 9 IS NOT WHAT I SAID IT WOULD BE, AND MEASUREMENT IS WHY.** I had scoped it to the ceo as an
opaque-goal barrier helper in the lowerer. Before building it I probed six barrier shapes — cut inside
`findall`, `\+`, `catch`, `forall`, `once`, and a `catch` inside if-then-else — against swipl. **SCRIP matches
the oracle on all six.** Rung 7 already closed that class. Under the ladder rule the ceo adopted this morning
— no predetermined length, each rung minted where measurement shows the largest remaining red class — a rung
I had announced but not measured is not the rung.

## WHAT IS NOT CURED

The rung 9 cure is a frame-representation question, not a one-file change: either compact the retained frame,
or give the engine a growable stack (co-expressions already run on their own mmap'd stack, so there is
precedent). It touches the zetas and wants a ruling before code.
