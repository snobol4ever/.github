# The Raku phaser family is ONE construct, and every rank in it is the oracle's

**hq_raku · 2026-09-20 · row `raku-the-31-no-layout-graphs-the-compiler-refuses-are-cured-or-named-and-counted-in-the-gc-slot-kind-census` (ceo CEO-979, GC-only order) · SCRIP landing beside this file**

## What the 31 no_layout entries actually are

`util_gc_census.py maps --zls-langs raku` read `graded=896 no_layout=31` — 31 master entries the compiler refused a frame layout for, NAMED AND UNCOUNTED. Measured, not assumed:

| class | n | the compiler's own reason | disposition |
|---|---|---|---|
| statement-prefix / phaser blocks | 18 | `raku parse error line N: syntax error` | CURED here |
| `our` declarator | 1 | same | CURED here |
| `join(...)` call spelling | 3 | same | CURED here (1 of the 3 now parses and is still wrong — a different defect, named below) |
| sequence operator `1 ... 10` | 1 | same | DEFERRED with a reason, below |
| advanced benchmarks | 6 | same | one row each, below |
| role-composition diagnostics | 2 | `Method 'x' must be implemented by class C ...` | DECLARE — these legitimately have no frame |

**All 31 are also RED in RakM** (`util_raku_entry_grade.sh`, 31 graded, 0 green). So the no_layout set is a SUBSET of the master's own reds and never a hidden collector hole. It is still DARK by CEO-993's line, for a reason one level up: a graph with no frame layout has no frame map, so every leaf boundary inside it stores into an unmapped slot BY CONSTRUCTION — the cfo's CFO-129 sharp form ("only the leaf boundaries need rooting, AND the slot the boundary stores into has to be inside the frame map") generalized from one slot to a whole graph, 31 graphs of it in Raku alone.

## The construct: a phaser is a position, not a keyword

18 of the 31 share a prefix, and they are ONE construct. A phaser is a block whose POSITION in the enclosing block is decided by its name — so the whole family is a **stable reordering of one statement list**. No new IR kind, no new box, no new global. The parser marks each one as a call to the reserved name `__rk_phaser_<name>` carrying its block as the last child (the `__rk_arr` / `__rk_undef` marker-call idiom the grammar already uses); `rk_phasers_place` reorders a block's list by rank and unwraps the marker; the loop rules take `FIRST`/`NEXT`/`LAST`/`once` out of their body first.

The lexer gives a phaser token only when a block opens right after the name — 18 **fixed-length** trailing-context rules, because flex only tracks `yyleng` correctly when the part before the `/` is fixed length. That keeps every one of these names an ordinary identifier everywhere else.

## Three ranks that were not guessable, and were measured rather than reasoned out

Every rank in the table below came from running the construct under `/usr/bin/raku` on 2026-09-20 and reading the output. Three of them contradict what the names suggest:

* **At mainline `UNDO` fires and `KEEP` does not. In every other block `KEEP` fires and `UNDO` does not.** Not truthiness-dependent: a sub returning `0` still runs `KEEP`, and a mainline whose last statement is `1;` still runs `UNDO`.
* **`TEMP { }` as a block phaser is observably nothing** — it prints nothing at any scope.
* **`FIRST` and `LAST` never run when the loop body never runs.** `for @empty { FIRST {...} LAST {...} NEXT {...} }` prints nothing at all. That is why both sit behind ONE guard cell, set to 1 before the loop and to 0 by the first iteration: `if (g) { g = 0; FIRST }` at the head, `unless (g) { LAST }` after the loop.

## The red that became a rule: a statement after TT_RETURN overwrites the value

The first cut placed `LEAVE`/`KEEP` after the ordinary statements, which put them AFTER a trailing `return`. `sub f() { ENTER {...} KEEP {...} LEAVE {...} say "body"; return 7; } say f();` then printed `enter body leave keep` and **handed back nothing** — a statement emitted after `TT_RETURN` overwrites the value the sub was about to return.

rakudo runs the phasers after the body and before the value reaches the caller (`enter body leave keep 7`), so **holding a trailing return back and re-appending it last matches the oracle exactly**, and the whole divergence disappears. A `return` in the MIDDLE of a body is not held back, and the phasers after it do not run — named, not cured.

⭐ The reusable half: the probe that found this was a generalization probe, not a witness. Every one of the 18 witnesses was already byte-identical to rakudo when the return bug was live, because not one of them is a sub with a return value. **A construct family graded only on its own witnesses is graded on the shapes someone thought to write down.**

## Named divergences, none of them silent

* `NEXT` does not fire on an explicit `next` statement (it fires on falling off the end of the body). rakudo fires it on both. Measured: ours `1 N 3 N end`, rakudo `1 N N 3 N end`.
* A loop phaser nested inside an `if` within a loop body **REFUSES** (`rt_script_die_surface`, rc=1, naming the phaser) rather than running in place — a measured refusal, never a confident wrong answer, per the cto's rule (b). ⛔ CORRECTED AFTER EXERCISING THE ARM RATHER THAN ASSERTING IT: I first wrote that rakudo attaches such a phaser to the enclosing loop. **It does not** — measured, `for 1..3 { if $i > 0 { FIRST {say "first"} } say $i }` prints `1 2 3` under rakudo and never runs the block at all. So our refusal is CONSERVATIVE against the oracle rather than a divergence from it, and it is not a reachability regression either, because the same program was a parse error before this landing. Both refusal arms were run before this sentence was written; the `once`-in-a-sub arm fires the same way, and rakudo's own answer there (`once call call`) confirms the semantics we cannot yet give it.
* `BEGIN` runs first at RUN time, not at COMPILE time. Observationally identical for any program that only prints.

## The two entries that are DECLARED rather than cured

`class_method_range_replace_6` and `class_method_say_replace_49` are role-composition diagnostics — a required method not implemented, and a method existing in two roles unresolved. **rakudo refuses them too**, our m3 output already matches the ref, and a program that legitimately never compiles has no frame by construction. Their `no_layout` reading is CORRECT AND PERMANENT and belongs in a declaration beside the data, not in a cure. They fail only on the `m4-build` arm, which is the harness asking a compile-error program for a binary.

## What is left, with the reason each one is left

* **`test_seq_op` — the sequence operator `(1 ... 10)`. DEFERRED ON PURPOSE.** Mapping `...` onto `..` is right for two plain endpoints and SILENTLY WRONG for the list-headed form `1, 3 ... 11`, which the grammar's `arg_list` splits on the comma before `...` can bind — it would quietly become `(1, 3..11)`. That is exactly the cto's rule (b) case: a construct whose parse makes a program print a plausible wrong answer where it used to refuse WAITS.
* **`scrip_test_rk_seq_consumers_arr` — parses now, still wrong.** Prints `3-1-2-1` where rakudo prints `-3-1-2-1`, and drops two blank lines: an empty-string array element is dropped by `reverse`/`unique`/`join`. A separate defect this cure merely made MEASURABLE — dark to red is the direction CEO-993 ranks, and it gets its own row.
* **Six benchmarks, one construct family each**, none cheap: `rc-man-or-boy-test` (`$B := { ... }`, a self-referential closure binding), `divide-and-conquer` (`start`/`await`/`[+]`/`do for ^N` — concurrency, outside the baseline), `point_class_add2` (`nqp::create`, `nqp::bindattr_n` — NQP internals, not Raku), `rc-9-billion-names` (`:=` binding on an array element), `rc-perfect-shuffle` (`flat map { ... }, 0..N`), `rc-self-describing-numbers` (`+«$s.comb`, a hyper-operator whose guillemet is also a LEX error).
