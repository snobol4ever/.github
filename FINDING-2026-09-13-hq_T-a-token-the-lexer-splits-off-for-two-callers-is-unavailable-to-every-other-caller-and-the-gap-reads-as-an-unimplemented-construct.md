# FINDING 2026-09-13 hq_T — a token the lexer splits off for two callers is unavailable to every other caller, and the gap reads as an unimplemented construct

**Measured while walking the Raku ladder** (MODE NONET, hq_T is the Raku ladder seat; CEO-670).
Tree: SCRIP `202d8bfff` → the landing, **pushed and re-proven after rebase at `0a2a3fd34`**;
corpus `7bedb92d0` → `12df2da75`; oracle rakudo via `rakudo_bin()`.

## The number

| reading | ladder, rungs 0..14, witness × mode |
|---|---|
| CEO-671's brief, at `3a510fa4e` | PASS **92** / 136 |
| measured at the head of this sitting, `202d8bfff` | PASS **134** / 136 |
| after the one-cause cure below | PASS **136** / 136 |

One witness was red, in both modes: `ladder__rung12_exceptions_specific_type`.

## What happened

`raku.l` lexed a `::`-qualified name as its own token:

    {ALPHA}{ALNUM}*("::"{ALPHA}{ALNUM}*)+   → QIDENT

and `raku.y` accepted `QIDENT` at **exactly three sites**: `pkg_name` (for `class`), and two `KW_USE` arms.
Expression position is written against `IDENT` — `IDENT '(' arg_list ')'`, `IDENT '.' KW_NEW ...`,
`IDENT '.' IDENT`, and bare `IDENT` as a name — so **no qualified name could appear in an expression at all**.

⛔ **Every one of those three QIDENT sites already had an `IDENT` twin.** The split bought nothing. Deleting
the token and lexing a qualified name as an ordinary `IDENT` made `A::B.new()`, `A::B::C.new.m`, `X::AdHoc`
and `when X::AdHoc` parse through machinery that was already there, and cost **no grammar rule** — the diff
is one lexer action and the removal of three now-dead alternatives.

## Why it stayed open, and why that is the reusable part

⭐ **The defect presented as an EXCEPTIONS defect and it was a NAMING defect.** `LADDER.tsv` had rung12
filed against three ablated causes, honestly: the `CATCH` phaser did not parse, `fail` did not parse, and a
`::`-qualified name did not parse in expression position. The first two were cured elsewhere. The third
survived — and because it was the last red on the *exceptions* rung, the standing reading was that SCRIP's
exception support was incomplete. It was not. Exceptions worked. The program could not say the **name** of an
exception type, and it could not have said the name of anything else either.

⭐ **The general form: a token split off for a privileged caller is invisible to every caller that did not
ask for it, and the absence surfaces wherever that name happens to be needed — never where the split was
made.** A grep for `QIDENT` finds three happy sites and looks complete. Nothing points from the three
accepting sites to the dozen that cannot. The cheap test is the one this ladder walk applied by accident:
**ablate the failing witness until the remaining program has nothing to do with the feature you think you are
debugging.** `my $x = A::B.new()` is not an exceptions program. That is when the cause is located.

## The second half — what SCRIP already knew, said out loud

`X::AdHoc` is the type Raku's `die "str"` throws, and SCRIP already models an exception **as its message
string**: `by_name_dispatch.c` answers both `.message` and `.payload` off that string. So the semantics were
not a new feature, they were a name for an existing one — `X::AdHoc.new(payload => P)` **is** P, and
`when X::AdHoc` inside a `CATCH` matches whatever is in flight, because under that model every thrown
exception is an X::AdHoc. Both are exact, not approximations.

⛔ **NO OTHER `X::` TYPE IS ACCEPTED, DELIBERATELY.** `when X::IO` against an ad-hoc exception REFUSES
(`variable 'X::IO' is read but never assigned`) rather than matching. Widening `rk_is_adhoc_name` to the
`X::` namespace would have turned one green witness into a family of false greens: a type test SCRIP cannot
make must never quietly come back true. **The refusal is the correct answer and is worth more than the pass.**

## Against me, named

The brief I was working from cited **92 of 136**, and the tree read **134 of 136** before I changed anything —
42 witness-modes of drift, cured by other seats between the brief being written and being read. I re-measured
first, which is the only reason the sitting went to the one real red instead of re-curing eleven closed ones.
⭐ **A count inside a brief is a reading of a tree the brief does not carry with it.** The brief was not wrong
when written; it was a photograph. The instrument is one command away and the photograph never is.

## What this changes

`corpus/tests/raku/config/LADDER.tsv`: ten rungs flipped `BUILT-RED` → `BUILT`, and the Raku ladder is green
end to end for the first time — rungs 00–14, 68 witnesses, both modes, 136/136. The original RED note on each
flipped rung is kept after a `||` marker rather than erased: the cause a rung was minted against is the part
worth reading later.

## Control arms, and what is still running

Seven smokes: icon 15/15 · pascal 9/9 · prolog 5/5 · raku 10/10 both modes · rebus 4/4 · snocone 5/5 ·
snobol4 7/7 — every one identical to the prior sitting's recorded numbers. `make preflight` 35 arms 0 red.
`test_gate_parser_generated_files_in_sync.sh` GREEN over 14 generated files from 9 grammars — the arm that
matters most here, because the generated parsers are tracked and `make` has no bison/flex rule, so a grammar
edit that is not regenerated changes nothing and every board stays green. Raku parser fixtures 80/97,
unchanged. RK-ZC-8 invariant B (the full Raku smoke suite) 719/0 both modes.

### The 221-arm blocking set, and the measurement I broke myself

The landing did not wait on it — the bar under MODE line 2 is the row's DONE-WHEN plus the gates the landing
touched plus `make preflight`. It finished afterwards: `11 blocking arm(s) failed, 10 refused`.

⛔ **That reading is not the tree's, and nine of the ten refusals were mine.** I rebuilt the binary while the
set was running. Arms 33–44 refused in a block, and `test_gate_runners_refuse_on_a_stale_binary.sh` went RED
saying exactly that. Re-run on the settled tree, **all nine clear rc=0.**
⭐ **A long measurement is a tree, not a command.** Anything that changes the tree mid-run invalidates every
arm after it — and the honest tell was the single gate whose entire job is to notice that the binary moved.
Every other arm just reported its own confusion.

⭐⭐ **One arm named me, and it was right — which is the better half of this FINDING.**
`test_gate_baton_donewhen_runnable.sh`: `runnable=398 UNCLOSEABLE=105, ceiling 89 — GREW by 16`, with the
message *"if you minted one, make it a command before you push."* **Three of that day's growth were rows I
minted in this very sitting**, each with a DONE-WHEN written as prose. A row like that can be **cured
perfectly and record no flip**, because `done` refuses a criterion that cannot exit 0 — so the work
disappears rather than the row, and the cost lands on whoever picks it up later, never on whoever minted it.
That is the shape that does not self-correct.

Fixed all three on the spot and proved each on **both** arms: `rc=1` naming the open defect, `rc=2` when it
cannot measure. Two of the three had refused with *bash's* message rather than naming themselves — the same
defect one level down — and now print `REFUSE(2): …` in their own voice. ⭐ This is the refusal-arm extension
of fail-once that CEO-671 asked be filed, applied to my own work within the hour it was asked for.

⛔ **Then the census turned on me.** By owner, the 102 uncloseable rows are **hq_T 33** · hq_P 19 · hq_B 12 ·
hq_U 10 · hq_C 8 · hq_R 7 · hq_V 5 · hq_I 4 · hq_S 3 · coo 1. The largest share is mine, which is the only
reason the backlog row earns its rank. The valve rather than the mop is at the mint:
`mint-refuses-a-done-when-whose-first-word-is-not-a-command` (hq_B) — whose own DONE-WHEN mints a probe row
with a prose criterion, cleans it up, and today reports **`FAIL: mint ACCEPTED a prose DONE-WHEN and wrote
the row`**. The defect demonstrated live rather than described.

**Also red and in my lane, rowed rather than patched:** the raku master is 977 of 1025 entries out of its
builder's order — not from this landing (the corpus commit touched `LADDER.tsv` and nothing else). ⛔ I did
not simply run `--resort`: it moves a population of 1025 rows, which is exactly the shape of
`FINDING-2026-09-12-hq_T-moving-a-population-blinds-every-instrument-that-derives-it-and-the-gate-stays-green`.
Running it as a tail-end action would have repeated the mistake that FINDING exists to prevent.

✅ **Every Raku arm in the set is green.**

⛔ **`test_gate_raku_zframe.sh` invariant A is RED and is NOT this landing** — it asserts that the
`SCRIP_RK_ZFRAME=0` killswitch still reproduces a bomb on `sub f($a){return $a*2} say f(21);`, and that
program no longer bombs. The witness contains no `::`, no exception, and nothing this landing touches; the
gate is in neither the blocking set nor preflight, which is how it has been able to sit red. It is a gate
pinning a defect that was cured out from under it — its own invariant B is green in the same run.

## Re-proven after rebase

The push rebased onto five sibling landings (`e838a68b5` instruments · `7552a4f7f` gate wiring ·
`854f31238` runtime trace banner · `67df8c9c8` snobol4 by-name · `d62b63d88` the stream-struct cut). Law is
to re-prove the gate after a rebase, not to trust the pre-rebase reading: rebuilt, and
`test_raku_ladder.sh --to max` reads **PASS 136/136 FAIL 0** at SCRIP `0a2a3fd34` corpus `12df2da75`.
`make preflight` re-read **37 arms 0 red** — two arms more than before the rebase, which is a sibling seat's
wiring landing and not a miscount of mine. Control smokes re-read icon 15/15 · pascal 9/9 · prolog 5/5 ·
snocone 5/5, unchanged across the rebase.

⭐ The `SCORE.md` ladder cell now reads 136/136 and **the runner wrote it, not a seat**: `lib_ladder.sh:204`
calls `util_score_row.py write --column ladder` at the end of every run, and 7 of the 9 `test_*_ladder.sh`
runners are on that shared body. On the first clean run of this sitting it wrote the then-true 134/136 and I
reverted it by hand, since boards are the coo's; on the post-rebase run it wrote the now-true 136/136 and
that stands, because reverting it would restore a stale number in the name of a convention. The convention
and the instrument disagree, one of them should change, and it is one line in one shared file — flagged to
the coo and the ceo rather than worked around seat by seat.
