# FINDING — PROLOG ISO RUNG 9: FIVE OPAQUE-GOAL BARRIERS RETAIN A FRAME THEY CAN NEVER RE-ENTER, AND FIRST-ARGUMENT INDEXING RECLAIMS NOTHING

**cto, 2026-09-13. MODE NONET. Lane: PROLOG COMPLETENESS, THE ISO LADDER.**
**Tree: measured at SCRIP `3d6fc82c6` and RE-MEASURED UNCHANGED, every row, after the rebase onto other
seats' landings at `f2087e74c` — the table below carries both trees because a number that names one tree
and is read on another is a number nobody can check. Instrument:
`scripts/util_pl_rung9_gamma_fence_witness_set.sh`.**
**Ordered by CEO-690 after Lon's ruling; hq_U owns the build, the cto is the measurer on the Prolog half.**

Lon 2026-09-13, in-chat to ceo, verbatim: *"The frame question is beyond me to know what it is. But I will
say that do a whack-free on GAMMA for a FENCE d (i.e. cut !) or otherwise FENCE d operation."* CEO-690 turned
that into an order with a shape: the frame stays on the machine stack and is torn down sooner, hq_U builds
it, and what the ceo wanted from this seat was *"the witness set and the numbers — which Prolog constructs
are PROVABLY COMMITTED AT GAMMA BUT NOT LEXICALLY FENCED, because those are the prize and nobody has
enumerated them."* This is that enumeration. It lands no cure.

## 1. THE ANCHORS, AND WHY NO NUMBER BELOW THEM MEANS ANYTHING ALONE

One recursion shape, one variable — the goal between the guard and the recursive call:

```
p(0) :- !.
p(N) :- N > 0, <BODY>, N1 is N - 1, p(N1).
```

The largest `N` that completes, bisected, at a `ulimit -s` pinned to 8192 KB in a subshell and printed.
Bytes per retained frame is that limit divided by that depth **and by no other limit** — this file's sibling
gate published a 4x unit error on 2026-09-13 by taking a depth at one limit and dividing by another, so the
divisor is now part of every label.

| anchor | body | depth | per frame |
|---|---|---|---|
| `anchor_det` | `true` | 400,000+ | reclaimed |
| `anchor_cut` | `q(_), !` | 400,000+ | reclaimed |
| `anchor_cp` | `q(_)` | 8,031 | 1,044 B |

The upper anchor is the whole reason this is a defect and not a design limit: **the mechanism already works
where it is wired.** The same nondeterministic call, lexically fenced, costs nothing. Every construct below
is therefore graded by which anchor it sits at, not by an adjective.

## 2. THE PRIZE — PROVABLE PER CALL SITE (five constructs, all red)

An opaque-goal barrier can never be re-entered by backtracking whatever its argument goal does, so the text
of the call site alone proves β is unreachable. Each of these is **a cut in effect with no `!` in the text**,
and not one of them reclaims:

| construct | body | m3 depth | m3 per frame | m4 depth |
|---|---|---|---|---|
| `once/1` | `once(q(_))` | 7,348 | 1,141 B | 7,299 |
| condition of `(->)/2` | `( q(_) -> true ; true )` | 7,348 | 1,141 B | 7,299 |
| `forall/2` | `forall(q(X), r(X))` | 8,544 | 981 B | 8,519 |
| `(\+)/1` | `\+ (q(_), fail)` | 10,204 | 822 B | 10,155 |
| `catch/3` over a committed goal | `catch(once(q(_)), _, true)` | 6,689 | 1,254 B | 6,640 |

⭐ `once/1` and the if-then-else condition read **identical to the digit in both modes**, which is what a
shared barrier lowering looks like from the outside and is the cheapest hint about where one cure covers two
constructs.

⛔ Note what these numbers are *not*: they are not the cost of a retained choicepoint alone. `\+ (q(_), fail)`
**exhausts** its inner goal — there is no choicepoint left to retain — and it still leaks 822 B per level
against a `true` body that leaks nothing. So the retained object is the barrier's own frame material, not
only the choicepoint behind it, and a cure that only discards choicepoints will move some of this table and
not the rest. **That prediction is the first thing to check after a teardown lands.**

## 3. THE PRIZE — PROVABLE ONLY PER ACTIVATION (clause selection), and it is the worst row in the table

| construct | body | m3 depth | m3 per frame | m4 depth |
|---|---|---|---|---|
| indexable, clause 1 | `d(1, _)` | 5,932 | 1,414 B | 5,883 |
| indexable, clause 2 | `d(2, _)` | 5,932 | 1,414 B | 5,883 |
| **control, genuinely 3-way nondet** | `f(1, _)` | **5,932** | **1,414 B** | **5,883** |

`d/2` is `d(1,one). d(2,two). d(3,three).` — three distinct constant first arguments, so `d(1,_)` is
deterministic under ISO and under swipl. `f/2` is `f(1,one). f(1,two). f(1,three).` — the same arity, the
same three clauses, all matching, genuinely nondeterministic.

⛔⭐ **THEY READ THE SAME NUMBER TO THE BYTE, IN BOTH MODES. FIRST-ARGUMENT INDEXING BUYS ZERO FRAME
RECLAMATION.** The discriminator in this tree is not *can a later clause match* — it is *is there a later
clause in the text at all*:

| shape | body | depth |
|---|---|---|
| matched the **last** clause | `d(3, _)` | 400,000+ reclaimed |
| matched clause 1 or 2 | `d(1, _)` / `d(2, _)` | 5,932 |
| single-clause predicate | `s(_)` | 400,000+ reclaimed |

This is the case CEO-690 named as the hazard, and it is the one a call-site-keyed cure gets wrong: `d(1,_)`
is committed and `d(X,_)` with `X` unbound is not, **at the same call site**. Commitment here must be decided
at run time from the arguments — which is what first-argument indexing *is* — so this row is not a teardown
row at all until indexing prunes, and it belongs to rung 12 (`indexing`) as much as to rung 9. I am naming
that split rather than handing hq_U one undifferentiated list.

## 4. ALREADY RECLAIMED — reported because a witness set of only red rows cannot show the mechanism exists

`d(3, _)` (last clause), `s(_)` (single clause), and `findall(X, q(X), _)` all reach 400,000+ in both modes.
⭐ **`findall/3`'s inner goal already discards its choicepoints and `\+`'s does not**, though both run their
goal to exhaustion — two barriers, the same nominal obligation, opposite behaviour. Whatever `findall` does
is the shortest path to the other four, and it is in this tree today.

## 5. THE SAFETY CONTROL — answers, not depths, and it is the grading criterion

γ is the shared yield port for SUSPEND and RETURN (CEO-550): a generator that suspends through γ expects to
be resumed **into that very frame**, so an unconditional whack tears down a frame a redo is about to
re-enter. The witness set therefore ships a pair whose *answers* separate the two lifetimes:

```
p(N,[X|T]) :- N > 0, q(X),       N1 is N-1, p(N1,T).   findall over p(3,L)  ->  cp(8)
o(N,[X|T]) :- N > 0, once(q(X)), N1 is N-1, o(N1,T).   findall over o(3,M)  ->  once(1)
```

Both confirmed against swipl. SCRIP answers `cp(8) once(1)` today. **If a teardown lands and `cp(8)` becomes
anything else, the cure is wrong and the depth table is irrelevant** — the instrument exits 1 on that arm
before it prints anything else useful.

## 6. THE ORACLE GAP, MEASURED RATHER THAN ASSERTED

swipl at the same pinned 8192 KB C stack completes `q(_)`, `once(q(_))` and `d(1,_)` at N = 400,000, all
three. It is unbothered because its choicepoints are compact records on a growable heap stack; ours are
machine-stack frames by design (ARCH-ENGINE, the three zetas). The gap on this population is **39x to 67x**.

## 7. WHAT I DID NOT DO, STATED SO THE NEXT OWNER DOES NOT ASSUME IT

- **No cure, no frame teardown, no `frame_layout.c`.** MODE NONET's guardrail puts frames in concern 3;
  CEO-690 put the build with hq_U and the measurement here, and the thing that makes the cure safe is a
  lifetime proof, which is hq_U trade.
- **I did not read the lowerer first and I am not naming a site.** ASM-DIFF-FIRST is the debugging order and
  this is the step before it: the lowerer can only say what was intended, and the question CEO-690 asked was
  what the tree *does*. Section 2's last paragraph is a measured prediction about where a choicepoint-only
  cure will fall short, not a claim about a file.
- **This instrument is not a gate and grades nothing.** The wired verdict for rung 9 remains
  `test_gate_pl_iso_rung9_a_backtrackable_recursion_reaches_the_depth_the_oracle_reaches.sh`, still 4 arms
  red. This script's consumer is hq_U's cure: run it before and after, and **a construct that does not move
  is a construct the cure missed** — which is the only way this table earns its keep rather than being a
  snapshot nobody re-reads.
