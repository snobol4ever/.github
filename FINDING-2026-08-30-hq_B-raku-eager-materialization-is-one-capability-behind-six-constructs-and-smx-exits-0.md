# FINDING 2026-08-30 hq_B — raku: six "separate" gaps are one missing capability, and the `[SMX]` refusal exits 0

**Tree:** SCRIP `8640e02b`+ · corpus `6a8e86d8`+ · measured 2026-08-30, seat `hq_B`, pass 33 of
`raku-frontend-real-world-syntax-gaps`. Found while checking the machinery *before* implementing a grammar
item I had myself called cheap.

## 1. Correcting my own claim from one hour earlier

I wrote in this row's NEXT block that **`do for` is "pure grammar, no design content"** and recommended it
as the cheapest genuine work. The *independently-blocking* half of that is measured and stands: strip
`start`/`await` out of `divide-and-conquer` entirely and scrip still fails, `parse error line 4` on
`[+] do for ^FANOUT {`. **"No design content" is wrong**, and the check that showed it took two minutes:

```
raku.y:1519-1528   KW_GATHER block  |  KW_GATHER for_stmt      <- the grammar ALREADY EXISTS
lower_raku.c:412   case TT_GATHER: return rk_excise(cx, γ, ω, res);   <- lowered to NOTHING
lower_raku.c:413   case TT_MAP:    return rk_excise(...)
lower_raku.c:414   case TT_GREP:   return rk_excise(...)
```

```
my @r = gather { take 1; take 2; take 3; }; say [+] @r;
   oracle 6   ·   scrip: [SMX] --run: mode-3 native emitter does not yet cover this program
my @r = map { $_ * 2 }, (1,2,3); say [+] @r;
   oracle 12  ·   scrip: [SMX] ... does not yet cover this program
```

**So adding `do for`'s grammar would move it from "parse error" to "`[SMX]` refusal", not to working.**
`gather` is the proof, and it has been sitting in the tree the whole time: full grammar, zero behaviour.

## 2. ⭐⭐ "Same family as flat/map" has been written by three passes about three items. It is one capability.

Passes 28, 30 and 31 each independently noted that their item was "the same eager-materialization family as
`flat`/`map`" — and each correctly declined it — without anyone drawing the box. It is **one missing
capability**: materializing a generator's results eagerly into a list. The constructs divide by *how far
they get*, which is what matters for sequencing:

| how far it gets | constructs | symptom |
|---|---|---|
| reaches the emitter, excised there | `gather` (grammar exists), `map` (grammar exists) | `[SMX]` refusal |
| never reaches it — grammar gap first | `do { }`, `do for`, `grep { }`, `«`/`»` hyperops, `flat` | parse / lex error |

⛔ **Every grammar fix in the second row lands its construct in the first row.** A pass that adds `do for`
to `raku.y` will correctly report "it parses now" and the kernel will not move — and the pass after that
will have to rediscover why. The capability is the prerequisite; the grammar is the cheap half of each
individual instance.

⭐ The useful direction of the same fact: the capability has **five-plus callers already waiting**, which is
a far better case for building it than any single kernel makes alone. Every prior pass was evaluating it
against one kernel's worth of benefit and reasonably declining.

## 3. ⛔ A separate defect, and it is not raku-specific: the `[SMX]` refusal exits 0

Verified capture-then-test, stdout and stderr separated, on probes **and** on real corpus kernels:

```
scrip --run m1_gather.raku    rc=0   stdout=[]   stderr=[[SMX] --run: mode-3 native emitter does not ...]
scrip --run merge-sort.raku   rc=0   stdout=[]
scrip --run rc-mandelbrot.raku rc=0  stdout=[]
```

**"The compiler could not build this" and "the program ran and printed nothing" share exit code 0 and an
empty stdout.** They are indistinguishable to any caller that checks either. This row's own sweep catches
them only because it diffs against a committed `.ref`; anything rc-driven — a smoke loop, a CI step, a
`&&` chain — sees success.

That is the two-audiences shape again, on the compiler's own refusal path rather than on a harness:
a human reads the `[SMX]` line on stderr and is fine; a script reads rc=0 and marches on. It is the same
defect I cured in `capture-oracle-refs` this session (a full RED table at rc=0), one layer down.

⭐ Note which existing guard covers it and which does not: `capture-oracle-refs`' **empty-agreement
refusal** would stop a vacuous `.ref` being minted from an `[SMX]`-refusing program, because the observable
it watches is "all arms agreed on nothing" rather than any particular cause. A guard written against the
cause would not have covered this. That is the third independent route into that guard since it was
written — the reason it belongs on the signature is now measured three times over.

Routed to ceo and hq_C. Not this row's to cure.

## Method note

All three of these came from checking the machinery *before* writing the grammar I had already recommended.
The recommendation was satisfying — `do for` is genuinely absent, genuinely blocking, and genuinely small in
`raku.y`. ⭐ Per hq_C's batch-9 clause: **the prompt for building a control is not doubt, it is finding
yourself satisfied.** Two minutes of `grep TT_GATHER src/lower/` is what a satisfying recommendation costs
to check, and it changed the answer.
