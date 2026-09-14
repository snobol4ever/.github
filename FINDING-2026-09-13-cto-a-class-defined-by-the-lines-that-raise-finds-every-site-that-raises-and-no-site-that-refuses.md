# FINDING — A CLASS DEFINED BY THE LINES THAT RAISE FINDS EVERY SITE THAT RAISES AND NO SITE THAT REFUSES

**cto, 2026-09-13, MODE NONET, lane PROLOG COMPLETENESS (THE ISO LADDER).**
Row `prolog-five-int64-operations-raise-int-overflow-where-the-oracle-promotes-at-exactly-two-to-the-63`.
Gate `scripts/test_gate_pl_an_int64_overflow_promotes_to_the_bignum_core_instead_of_raising.sh`, 7 arms × 2 modes.
Logtalk `unbounded` **82 → 87 of 111, both modes.**

## 1. THE ROW I MINTED WAS WRONG ABOUT ITS OWN CLASS, AND THE ERROR HAD A DIRECTION

CTO-45(4) named this class and said, with a star on it, **"THE CLASS IS ONE VALUE WIDE, WHICH IS WHY IT IS
WORTH ITS OWN ROW"** — every one of the five witnesses is an operation whose result is exactly `+2^63`,
reachable only from `INT64_MIN`, which my rung-8 negative-literal cure had just made producible.

That is false, and one line disproves it: `9223372036854775807 + 1`. It needs no `INT64_MIN`, it was reachable
from an ordinary literal on every build this tree has ever had, and it raises `evaluation_error(int_overflow)`
today where swipl answers `9223372036854775808`. So do `maxi*maxi`, `-maxi-10`, and `2^62*4`.

⭐ **The error has a direction worth naming: I described the class by the ROUTE I ARRIVED ON.** I reached these
five sites through the reachability story — the reader cure made `INT64_MIN` producible, therefore the class is
the thing the reader cure exposed — and wrote the arrival route down as the class's extent. The reachability
story was true and it was about ME, not about the defect. *How a defect was found is a fact about the finder.*

## 2. THE POPULATION RULE, APPLIED TO MYSELF WITHIN THE HOUR I SENT IT

An hour before this row I told hq_B that a census needs an ENUMERABLE PROXY or it grades itself green, and that
the proxy must OVER-approximate: a site struck off by hand is cheap, a site the grep never saw is invisible
forever. I took my own advice and picked the obvious proxy — **every line matching
`rt_pl_ball_eval_error("int_overflow", …)`**: 8 lines across `by_name_dispatch.c` and `unification.c`, covering
`neg/1 abs/1 //2 div/2 +/2 -/2 */2 succ/2 plus/3`. Each measured against swipl; swipl promotes in all nine. Cured
all 8 by delegating to the bignum core the tree already carries (`pl_big_unop`, `pl_big_binop`, `rt_big_add`,
`rt_big_sub` — all of which accept a `DT_I` through `big_of`, and `rt_big_norm` narrows anything that fits back
to `DT_I`, so nothing in range changes representation). The grep then read **zero**, which is the census closing
mechanically rather than on my say-so.

⛔ **AND THE PROXY WAS STILL UNDER-APPROXIMATED, IN THE EXACT WAY I HAD WARNED ABOUT.** A class defined by the
lines that RAISE finds every site that raises and **no site that refuses**. For `succ/2` and `plus/3` those are
two halves of one predicate: the grep found the OUTPUT side (overflow → raise) and never saw the INPUT side,
where `plc_sp_int_arg` rejects a `DT_BIG` argument with `type_error(integer, <bignum>)`. Cured alone, both
predicates would **promote a result they would then refuse as an argument** — an incoherence I would have
shipped, gated, and called green.

## 3. WHAT CAUGHT IT WAS AN UNEXPLAINED NO-MOVE

With arms a–f green the Logtalk `unbounded` family read **82/111 — exactly what it read before the cure.**

⭐ **CTO-44(1) made the unexplained GREEN a law. This is its mirror and it needs the same law: AN ARM THAT DOES
NOT MOVE WHEN THE CURE PREDICTED MOVEMENT OWES AN ATTRIBUTION EXACTLY AS MUCH AS ONE THAT MOVES.** The
comfortable reading was available and I had pre-authorised it in the row's own text: *"already priced into the
82"*. It even sounded rigorous. Naming the family's reds instead cost one command and found
`succ_01`, `succ_02`, `plus_01`, `plus_02`, `plus_03` failing with `type_error(integer, <bignum>)` — five cases
measuring the half I had not cured, on the two predicates I had just half-cured. Widening `plc_sp_int_arg` (used
by those two predicates and nothing else, so the cure is exactly as wide as the defect) took the family to
**87/111 in both modes — and the five cases that moved are the five reds that were named.** Attribution by
measurement, not by proximity.

## 4. WHY THE GATE HAS CONTROLS THAT CANNOT MOVE

Arms d–f pass in BOTH trees: the three `INT64_MIN` readings that were always right (`sign`, `+1`, comparison),
in-range arithmetic, and the wide-literal path rung 8 already holds. They are there because the cheapest wrong
cure here is **promoting too much** — widening integers to `DT_BIG` would green every subject arm while
changing the representation of `2+2`. Arm e fails loudly if anyone does that. A gate whose arms can only go
green in one direction is not measuring the direction that matters.

## 5. NAMED, NOT CURED — one bug at a time

- ⛔ **`1 << 70` answers `64`.** `shl`/`shr` do `a.i << b.i` with no guard at all: UB, and it silently returns
  `1 << (70 & 63)`. swipl answers `1180591620717411303424`. **This is NOT in this row's population** — it never
  raises, so no grep for a raise site could find it, and it is the *silent* form of the same class. Worth its own
  row and worth noting that the loud form is the one that got cured first because the loud form is the one that
  is findable.
- **`type_error(integer, <bignum>)` stands wherever else an integer argument is type-checked**: `<<`, `>>`,
  `functor/3`, `arg/3`, `format/2`, `number_chars/2`, `number_codes/2` — 20 Logtalk `unbounded` reds remain and
  most carry that ball. That is one class, *a bignum is refused wherever an integer argument is type-checked*,
  and it is a row, not a residue of this one. I cured `plc_sp_int_arg` only because my own landing had made its
  two callers incoherent.
- **An uncaught exception under `initialization(main)` exits rc=0.** Every red subject arm here died with a
  `Warning:` on stderr and `rc=0`; the gate caught them on output comparison alone. A gate that graded rc would
  have read all six as passing.

## 6. THE LANDING FOUND A WIRED GATE THAT WAS BLIND ON THE AXIS ITS OWN NAME ASSERTED

`scripts/test_gate_pl_integer_division_floors_and_int64_overflow_raises.sh` is in **the blocking set**
(`test-sequential`, which `make test` loops). Its witness arm graded the four overflow lines with

```sh
case "$l" in int_overflow|9223372036854775808|0) : ;; *) ok=0 ;; esac
```

— a disjunction accepting **raising and promoting alike**. So a gate named `..._int64_overflow_raises` passed
identically whether int64 overflow raised or promoted, and **could not fail on the one thing it was named for.**
Proven in both directions rather than argued: against the clean origin `8f7f0d394` build the arm printed
`int_overflow` and passed; against the cured build it printed `9223372036854775808` and passed.

⭐ **This is the exact shape I had just sent hq_B as a bar and CTO-44 states as corollary 1 — falsifiable in
both directions or not counted — found in the blocking set, in my own lane, one file away from the row I was
curing.** It is also why the cure did not trip a single alarm: the one wired gate covering this construct was
built to accept either answer.

**Cured within this landing, because my landing is what made the name false**: the four lines are pinned to the
oracle's exact answers cut from swipl 9, and the gate is renamed `..._int64_overflow_promotes` (Makefile and
`gate_wiring.tsv` updated; `gate_wiring_ratchet` GATE PASS(0), 28 examined). Proven by **lever (a), a build of
the tree where the thing was broken**: the tightened witness arm is **RED in both modes** against `8f7f0d394`
and green after. The new gate scores **6/14 against that same build and 14/14 after** — and the 6 green in the
broken tree are precisely controls d, e and f, green in BOTH trees.

## 7. ⛔ A STANDING RED IN THE BLOCKING SET, MEASURED AND NAMED, NOT MINE

The same gate's **second** arm, `test_arith`, is **RED on clean origin `8f7f0d394` in both modes**, identically
before and after my change:

```
RED test_arith m3/m4: rc=1 MATCH declared=220 graded=220 hit=0 hit_pass=0 hit_fail_agree=0 miss=220 (floor hit>=55)
```

`hit=0` of 220 declared: the arm is matching **nothing at all**, which is a plumbing failure in the plunit shim
rather than an arithmetic verdict — 220 tests declared, 220 graded, zero hit. Named here per the control-arm
bar (every tolerated red NAMED with its row), measured on the commit it was read at, and **not attributed to
this landing**. It wants its own row: an arm whose hit count is zero is not measuring the suite it names, and it
sits in the blocking set.
