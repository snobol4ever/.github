# FINDING 2026-08-30 seat14 — Raku `xx` (list-repeat) evaluates its LHS ONCE and replicates the value; real Raku re-evaluates it per repetition. New bug class, root-caused, NOT fixed — needs new box-IR lowering infrastructure.

## CONTEXT
Found while working `raku-frontend-real-world-syntax-gaps` (postoffice task, locked via `next`'s dependency-inversion promotion this session). Not one of the 9 catalogued syntax gaps in that task's own `## NEXT` — this is a POST-parse runtime-semantics bug, orthogonal to everything that row has tracked so far (which has been grammar/parse gaps exclusively). Confirmed via the LEDGER (line 979, pass 19 "closed xx-at-expr-level") that prior work on `xx` was purely grammatical — promoting it from two narrow statement-level productions to a general `repl_expr` alternative (`raku.y:1584`) so it can appear anywhere an expression can. Every verification example across passes 17-19 uses a literal LHS (`1 xx 3`, `[1,2] xx 3`) — none exercise a side-effecting LHS, so this bug was never observed.

## ROOT CAUSE, ISOLATED CLEANLY
`X OP_REP_XX N` lowers directly in the grammar action (`raku.y:1584`) to `make_call("__rk_arr_xx", X, N)` — a plain function call, so `X` is evaluated exactly once, as a normal eager call argument, before `__rk_arr_xx` ever runs. The runtime implementation (`src/runtime/by_name_dispatch.c:3020-3038`) receives that single already-computed value in `args[0]`, splits it into elements (its own array representation is a SOH-separated string), and just **copies those same elements `cnt` times** into the output buffer (`by_name_dispatch.c:3035-3036`). There is no way for a plain eager-argument runtime call to re-invoke the expression that produced `args[0]` — the bug is structural, not a small logic error.

Real Raku semantics: `EXPR xx N` re-evaluates `EXPR` fresh for each of the `N` repetitions UNLESS `EXPR` is itself a literal list/Parcel (e.g. `(1,2,3) xx 2` → `1,2,3,1,2,3`, no re-evaluation of each element) — that literal-list case is what SCRIP's current implementation actually models correctly.

**Isolating repro (confirmed against `/usr/bin/raku` v6.d on this box, and against SCRIP, side-by-side, no RNG involved to rule out any PRNG confound):**
```raku
my $n = 0;
my @b = ($n++) xx 5;
say @b;
```
- real raku: `[0 1 2 3 4]` (re-evaluates `$n++` each time)
- SCRIP `--run`: `0 0 0 0 0` (evaluates `$n++` once, replicates `0` five times)

This is what actually broke `corpus/benchmarks/raku/insertion-sort.raku` (and would identically affect `merge-sort.raku`, same pattern, line 34): `@ints = (SCALE.rand).Int xx SCALE;` draws `.rand` exactly once and replicates that single integer 500 times, instead of drawing 500 independent values.

## WHY THE OBVIOUS SHORTCUT (reuse gather/take) DOES NOT WORK
`gather for N { take EXPR }` looked like a free reuse of already-landed, working machinery (pass 20 landed bare `for`-loops inside `gather`). Tested directly:
```raku
my $n = 0;
my @b = gather for 1..5 -> $i { take ($n++); };
```
`./scrip --run`: `[SMX] --run: mode-3 native emitter does not yet cover this program (a box has no MEDIUM_BINARY arm — Raku map/grep). REJECTED — native BB emission pending (no interpreter fallback).` — the SAME native-BB-emission/generator-eligibility gate that blocks `merge-sort`/`rc-dragon-curve`/`rc-forest-fire-stringify`/`rc-mandelbrot` in this row's own current DONE-WHEN sweep, and the same gate this task's LEDGER has recorded as declined 11+ times pending an explicit ARCH ruling. So desugaring `xx` into `gather`/`take` is a dead end in mode-3 (the mode DONE-WHEN grades) until that separate, already-flagged architecture gap is resolved — it is NOT a shortcut around it.

## WHY THIS WASN'T ATTEMPTED THIS PASS
A correct general fix needs to lower `X xx N` (when `X` is not a literal list) into an actual counted loop that re-lowers `X` fresh each iteration and accumulates results — e.g. a synthesized temp accumulator + a counted loop + per-iteration string-concat-with-SOH-separator (matching `__rk_arr_xx`'s own output encoding), keeping the existing literal-list-repeat behavior untouched (detectable at lowering time by checking whether `X`'s root node is a call to `__rk_arr`, `raku.y:497` etc.). This is a **statement-level lowering addition, zero grammar changes needed** (good — no bison-conflict risk, the dominant risk class in this row's whole history) — but `lower_raku.c`'s expression lowering (`lower_rv`, `raku.y`-driven box IR with explicit γ/ω continuation wiring, i.e. this project's Byrd-box α/β/γ/ω port model) has **no existing precedent for synthesizing a loop-with-accumulator during lowering** (checked: no gensym/temp-var helper, no statement-splicing helper anywhere in the file). Building that safely — without silently breaking box-wiring invariants elsewhere — is real, new infrastructure, not a mechanical mirror of an existing pattern (unlike, e.g., pass 25's `^@grid` fix, which reused an existing sigil-table pattern). Naming the fix site precisely rather than landing an unverified box-IR change, consistent with this row's own established practice (see e.g. the standing closure/frame-resolution gap, declined 11+ passes for the same class of reason).

## BLAST RADIUS / REGRESSION RISK — CONFIRMED ZERO FOR EXISTING TESTS
`grep -rn " xx " corpus/ scripts/test_smoke_raku.sh` — every existing usage (corpus and all ~8 smoke-test call sites) uses a literal LHS (`"x"`, `"ab"`, `0`, `"yo"`, `"z"`, `5`, or a literal list composer). "Evaluate once vs. evaluate N times" is unobservable for a literal, so a correct fix changes zero existing outputs. The two random-content kernels this bug actually affects are covered separately below (they have their own, likely-fatal, separate problem).

## SEPARATE, RELATED FINDING FILED
`insertion-sort.raku`'s and `merge-sort.raku`'s `.ref` files cannot be matched even with `xx` fixed, for an unrelated reason (SCRIP's `rand`/`srand` is glibc's PRNG, not Raku's) — see `FINDING-2026-08-30-seat14-raku-benchmark-refs-depend-on-prng-algorithm-match.md`. Fixing `xx` alone will not flip either kernel's DONE-WHEN status; it is still worth fixing on its own correctness merits (a real, generalizable Raku-semantics gap) whenever someone builds the loop/accumulator lowering infrastructure this needs.

## NEXT ACTOR
1. Do not re-attempt the gather/take shortcut — measured, dead end, same declined gate.
2. Real fix site: `lower_raku.c`, statement-level special case for `VAR '=' X xx N` (and the `my` form) when `X`'s root is not a `__rk_arr` call — needs a loop+accumulator lowering pattern that does not exist yet in this file. Scope to the assignment-statement shape actually used everywhere in the corpus/smoke suite (no usage nests `xx` deeper than a direct assignment RHS) rather than solving fully general expression-position re-evaluation.
3. Even once implemented, re-verify against the PRNG finding above before expecting `insertion-sort`/`merge-sort` to flip to PASS — they likely still won't, for the separate reason.
