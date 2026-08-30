# FINDING 2026-08-30 hq_B — the raku-bench row is no longer a syntax row: 5 of 12 failures are parse errors

**Tree:** SCRIP `8640e02b` · corpus `6a8e86d8` · measured 2026-08-30, seat `hq_B`, pass 32 of
`raku-frontend-real-world-syntax-gaps`. Baseline unchanged at **ok=4 bad=12**.

## The claim

The row's GOAL says *"16 of the 17 `corpus/benchmarks/raku/*.raku` kernels fail to PARSE under SCRIP."*
That was true when written. **It is now 5 of 16.** Seven of the twelve remaining failures are past the
parser entirely, and they belong to three different owners.

Every one of the twelve, classified by its own measured mode-3 diagnostic:

| class | n | kernels |
|---|---|---|
| **PARSE ERROR** | 5 | divide-and-conquer · rc-9-billion-names · rc-man-or-boy-test · rc-perfect-shuffle · rc-self-describing-numbers |
| **EMITTER — `[SMX] mode-3 does not cover this program`** | 4 | merge-sort · rc-dragon-curve · rc-forest-fire-stringify · rc-mandelbrot |
| **NO DIAGNOSTIC — ran clean, wrong answer, rc=0** | 2 | insertion-sort (`224` vs ref `0`) · pi-sequential-iteration |
| **SIGSEGV rc=139** | 1 | spinner |

The four `[SMX]` kernels also fail to compile/link in **mode 4**, so that is genuine emitter coverage in
both modes, not a mode-3-only gap.

⭐ **Why this matters more than the count:** 31 passes have hunted grammar constructs, correctly and
productively, on a population that has since shifted underneath the row title. A seat picking this row up
reads "syntax gaps", greps the kernels for exotic syntax, and finds plenty — because the kernels *do*
contain it. What the grep cannot tell them is that for seven of the twelve, the parser is no longer the
thing standing in the way.

## Per-construct ablation — the grep over-counts the gaps, badly

`divide-and-conquer` contains `\SCALE` sigilless terms, a hyphenated sub name, string interpolation, a
statement-modifier `if`, `?? !!`, `[+]`, `do for`, `await` and `start`. A static grep reports nine
candidate gaps. **Six of the nine already work:**

```
✅ my \SCALE = 10; say SCALE;              10        (both)
✅ sub foo-bar($n) {...}                    2        (both)
✅ say "v: $x";                             v: 5     (both)
✅ say $x if 0;                             done     (both)
✅ say $d <= 0 ?? "y" !! "n";               y        (both)
✅ say [+] (1,2,3);                         6        (both)
⛔ my @r = do for ^3 { $_ * 2 };            oracle [0 2 4]   scrip: parse error
⛔ start { 42 }                             oracle 42        scrip: parse error
⛔ await                                    scrip: Undefined function
```

So the real blocker set for that kernel is **three** constructs, not nine. `await`/`start` have zero
occurrences anywhere in `src/parsers/raku/` — genuinely absent from the grammar, not mis-parsed.

## ⛔⭐⭐ Three of these are SILENT WRONG ANSWERS at rc=0, not parse gaps

From `rc-9-billion-names`, isolated one construct per file:

```
my @t = $[1]; say @t;          oracle [[1]]     scrip prints 1     rc=0, lex error on stderr, RUNS ON
my $r = []; $r.push(7); say $r; oracle [7]       scrip prints ""    rc=0, NO diagnostic at all
my @a=(1,2,3); say @a.shift;   oracle 1         scrip prints ""    rc=0, NO diagnostic at all
my @a=(1,2,3); say @a.elems;   oracle 3         scrip 3            ✅ AGREE
```

`.elems` works, so this is not "array methods are unimplemented" wholesale — **`push` and `shift` are
no-ops that return nothing and say nothing.** The itemization case is the same shape pass 31 measured for
hyperoperators: a lex error is printed, execution *continues*, and a plausible wrong value is produced
under exit code 0.

⛔ **The consequence for sequencing:** fixing this kernel's four parse errors would make it parse and then
compute a wrong answer, because its inner loop is `.push`/`.shift`. Grammar work alone cannot flip it.

## A separate stringification gap, and one that is NOT one

```
                        oracle      scrip
say @a;                 [1 2 3]     1 2 3      Array -> SQUARE brackets
say (1,2,3);            (1 2 3)     123        List  -> ROUND brackets, and see below
say [1,2,3];            [1 2 3]     1 2 3
my $l=(1,2,3); say $l;  (1 2 3)     1 2 3
print @a;               1 2 3       1 2 3      ✅ AGREE — the .Str path is already correct
```

⛔ **I first wrote this up as a small, high-leverage fix, then measured it. It is not small.** The bracket
*shape* depends on Array vs List, and `rt_make_flat_agg` does not distinguish them — a blanket `[...]`
would be wrong for every List. The cure needs a type distinction the runtime does not have.

⭐ The mechanism is otherwise well-placed, which is worth recording so the eventual fix is not built in the
wrong layer: `by_name_dispatch.c:5668` already passes the say-vs-print flag **as** the `use_gist` flag —
Raku-correct by construction — and gist reaches `rk_obj_stringify` only for `DT_DATA`. A flat aggregate
falls through to `VARVAL_fn` and joins bare. So the fix belongs on the aggregate's own **type**, and does
**not** require branching on language identity (which `RULES.md` forbids past lower anyway). It requires
the type to exist.

⛔⭐ **A separate and probably larger defect fell out of the same probe: `say (1,2,3)` prints `123`.** No
separators at all, where `say @a` at least prints `1 2 3`. A parenthesised list literal is being taken as
*multiple arguments* to `say` and concatenated, rather than as one List. `say (...)` is an extremely
common form and it appears on no prior pass's list.

⭐ **But float stringification is already correct, and it is worth recording as a NEGATIVE result** so
nobody re-derives it: `0.1e0+0.2e0`, `1e0/3e0`, `2e0**0.5e0`, `1e0/7e0`, `100e0/3e0` all print
byte-identically to the oracle (shortest round-trip, not `%.17g`). So
`pi-sequential-iteration`'s `3.1415926535897643` vs ref `3.141592653589764` is **not** a formatting nit —
the two are **distinct doubles exactly 1 ULP apart** (`0x1.921fb54442cd7p+1` vs `0x1.921fb54442cd6p+1`).
The kernel accumulates a million terms of `1.0 / (1.0 + $x*$x)`, and in Raku `1.0` and `0.5` are **Rat**,
not Num. This is a numeric-semantics difference, not rounding, and it is not a cheap win — which is
exactly what a glance at "one digit off" would have suggested.

## Retired: the row's standing "waiting on a PRNG ruling" item

NEXT-ACTOR item 5 has read *"checked inbox again this pass, still no reply"* for three passes. It is dead
twice over: hq_P **did** rule (`ruling-prng-refs-are-ungradeable-by-construction`), and the cure already
shipped — corpus `2f552159` rewrote insertion-sort/merge-sort to generate input from a fixed-seed LCG
in-program instead of `rand()/srand()`. Verified: both `.ref`s are `0` and live `/usr/bin/raku` gives `0`
on three consecutive runs for both.

⭐⭐ **A RULING THAT ARRIVES AS A COMMIT IS INVISIBLE TO A SEAT WATCHING AN INBOX.** Two compounding
misses, neither careless: seat14 asked **hq_P**, so successive passes were checking **hq_B**'s inbox for a
reply that was never coming there — a question's answer goes to the asker, but the *waiting* is done by
whoever holds the row next. And even in the right inbox there was nothing to find, because the ruling's
payload was a corpus commit. The baton said "check the inbox again"; the answer was in the tree.
**When a baton item is "waiting on a ruling", the re-check must be RE-MEASURE THE THING, not re-read the
mailbox** — a landed cure and an unanswered question look identical from an inbox, and only one is still
true.

## What the next actor should do differently

Split the row, or at minimum stop treating the twelve as one population. The four `[SMX]` kernels are
emitter coverage, `spinner` is a crash, `insertion-sort` and `pi` are runtime semantics — three owners who
are not the frontend. The genuine frontend residue is five kernels, and within them the blocking
constructs are far fewer than a grep suggests.
