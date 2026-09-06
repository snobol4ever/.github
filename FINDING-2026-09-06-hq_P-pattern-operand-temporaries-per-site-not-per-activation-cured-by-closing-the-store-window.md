# FINDING — pattern operand temporaries were per-SITE, not per-ACTIVATION; cured by closing the store window

**hq_P · 2026-09-06 · row `snobol4-pattern-operand-temporaries-are-per-site-globals-clobbered-by-reentry`
(minted hq_C, censused seat01, addressed to an Opus HQ by name) · MODE OCTET · SCRIP `99200db5b` + this cure,
corpus `7fba27c82`**

## The defect, in one sentence

A pattern-valued assignment stages its operands into **per-SITE global variables** (`<bn>$V0..$Vn` for the
snapg / `MATCH_DEFER` arm, `<bn>$A0..` for the coerce arm), and the lowerer chained them
`eval0 → store0 → eval1 → store1 → … → MKPAT`; any user code inside operand 1 that **re-enters the same
source site** overwrites the outer activation's already-stored operand 0, and `SNO$MKPAT` then freezes the
**inner** activation's operands into the **outer** pattern.

## Why it is worth a FINDING rather than a line in the ledger

⭐ **The trigger is SITE RE-ENTRY, not recursion — and the two are easy to confuse because every witness of
the bug is recursive.** The control arm that separates them is the useful artifact:

```
A: recursive, alternation site executed only at the OUTERMOST level   -> GREEN before the cure
B: recursive, alternation site RE-ENTERED by the inner call           -> RED   before the cure
```

Same recursion depth, same function, same pattern shape. Only B re-enters the staging site. A reader who
tests "does recursion work?" gets a green answer and stops — plain recursion, and even a pattern accumulator
across a *non*-recursive call, were correct the whole time.

## Cure

`src/lower/lower_snobol4.c` only (the row's SCOPE line, unchanged). **Evaluate every operand left-to-right
first, then write all the `$V`/`$A` slots back-to-back immediately before `MKPAT`** — the window in which a
re-entrant call can run between a store and its read no longer exists. Built by constructing the *store*
chain first and the *eval* chains last-to-first, so build order differs from execution order; evaluation
order is unchanged and no new global is introduced.

## ⛔ THE OBVIOUS-LOOKING FIX WAS ALREADY IN THE TREE AND IT IS WRONG

`SCRIP_PB_ARGORDER=0` — an env arm that predates this row — **cures the published witness**. It does so only
by storing operand 0 *last*, after the re-entrant call has returned. It moves the window; it does not close
it. The mirror witness settles it, and it is the reason this paragraph exists:

| witness | recursion in | pre-cure default | `ARGORDER=0` | after this cure |
|---|---|---|---|---|
| `p4` | **right** operand | RED | green | green |
| `p7` | **left** operand  | green | **RED** | green |

It also reverses evaluation order, which SNOBOL4 fixes as left-to-right. ⭐ **A one-witness verdict would
have shipped it**: it is green on the exact program the row was minted from. The general lesson is the
cheap one — *when a fix works, write the mirror of the witness before believing it*, because a fix that
merely relocates a window passes every test aimed at the side it moved off.

## Measured consequences

- **Flips (gimpel, graded through `scorecard_snobol4.sh`'s own conditions — `SELFDIR:include`, cwd = program
  dir, `.ref` pin verified byte-identical to the live oracle):** `OR_driver` and `ORSORT_driver` DIFF → **PASS**.
- **Advanced but not flipped, and named rather than counted:** `HYPHENAT_driver` and `LINE_driver` stop dying
  `ERROR 246 stack overflow` and now produce merely-wrong output — a second, downstream defect in the
  hyphenation/fill logic. The `ERROR 246` was this bug: `OR()` accumulates `OR = OR | OR_EXTRACT()` while
  `OR_EXTRACT` recursively calls `OR()`, re-entering that very site, so the outer left operand was clobbered
  to the inner call's null string and the resulting anchored pattern consumed nothing and recursed forever.
- **Blast radius, measured rather than assumed:** **39 of 136** gimpel drivers change emitted asm. Measured
  with a same-binary control arm — `--compile` under the default vs `SCRIP_PB_ARGORDER=1` (which reproduces
  the pre-cure lowering) — so it needed no second build and no artifact pinning.

## ⛔ A SEPARATE INSTRUMENT FAILURE FOUND ON THE WAY, WORTH MORE THAN THE CURE

Censusing the gimpel pool I built a per-program grader by copying `run_one` and **omitted one line**:
`sbl_died`, the oracle-liveness test that treats *rc=0 while printing a fatal report* as `ORACLE_FAIL`.

It promptly manufactured a **seven-program class that does not exist** — `ARC SQRT TRIG L_TWO TUPLE VISIT
INSULATE`, all "failing" `ERROR 248 — attempted redefinition of system function`. **SPITBOL raises the
identical ERROR 248 on all seven.** SCRIP was *agreeing with the oracle*. The manual settles it: *Features
Not Implemented #1* — redefining standard system functions is a deliberate SPITBOL restriction, kept
**because it permits compile-time pre-evaluation**. Those `.ref` pins were minted from CSNOBOL4 precisely
because `sbl` cannot run them, which the driver headers state in writing.

⭐ **The shape, which is the transferable part: a census harness missing an oracle-liveness check does not
under-report — it FABRICATES REDS, in a coherent cluster that reads exactly like a real class.** Seven
programs, one error number, one plausible mechanism, and it was the largest "class" on my board. Curing it
would have made SCRIP diverge from the oracle by seven programs *and* paid away the pre-evaluation this
seat's own lane exists to protect. This is the s191 conviction — *"a census is a harness; copy `run_one`,
never re-derive it"* — arriving from the other direction: **copying it and dropping one line is the same
defect as re-deriving it.**

Whether those seven should be re-pinned or marked dialect-ungradable is a ceo/Lon ruling, not a compiler
fix. Routed to ceo; not touched.

## Control arms

Row DONE-WHEN m3 + m4 green · seat01's independent `$A` witness `MATCH 111` both modes (was `MATCH 110`) ·
three new witnesses incl. both operand directions · site-re-entry discriminator (arm A) still green ·
Icon smoke 15/15 both modes · snocone 5/5 · prolog 5/5 hard gate · rebus 4/4 · `strip_comments --check` ·
`emit_no_lang` · `template_medium_invisible`.

**SNOBOL4 master, on the MERGED tree** — SCRIP `6e770a3b7` (binary built 2026-09-06T16:31Z, `scrip`
md5 `5deaf9cbfaca…`, `libscrip_rt.so` md5 `bda8b0af7623…`), corpus `7fba27c82`, `RT_OPT=-O0`, box load 12/16:

```
SUITE_BOARD family=ALL total=1862 m3_pass=1831 m3_fail=1 m3_crash=0 m3_hang=0 m3_skip=0
                                  m4_pass=1831 m4_fail=1 m4_crash=0 m4_hang=0 m4_skip=0
SUITE_BOARD_AST family=ALL total=28 ast_pass=28 ast_fail=0
```

The single FAIL, both modes, is the known inherited `user_function_keyword_branch_3` (&FNCLEVEL).

## ⛔ TWO XPASSes ON THAT BOARD AND NEITHER IS MINE — NAMED RATHER THAN ABSORBED

An XPASS is a stale xfail marker, and a landing is exactly where one gets quietly credited to whoever is
holding the pen. Both were checked against the progress database instead:

- `user_function_eval_span_replace_branch_1` — already XPASSing on **four other seats' trees** (ceo, hq_U,
  hq_S, hq_C) *before* mine. Predates this work entirely.
- `user_function_array_replace_branch_1` — ⭐ **this one is the instructive case.** On my tree carrying
  **only** my cure (`99200db5b-dirty`) it read **m3 FAIL / m4 CRASH**. It reads **m3 PASS / m4 PASS** only
  after I rebased onto `b24ec61ad` (prolog reader) and `d2209582d` (icon `system()`), *both* of which touch
  the shared `src/runtime/by_name_dispatch.c`. hq_S's `10c7978c3` already had it passing at 21:11; hq_U's
  and hq_C's trees at 21:17 and 21:26 did not. **So it belongs to one of those two commits, not to this
  cure — and an m4 CRASH was cured as a side effect, which is worth more than the marker.**

⭐ **The check that separated them cost one query and would have been invisible to any board:** my *own*
earlier board is what exonerated my own cure. Had I run only the merged-tree board — the one a landing
normally quotes — both XPASSes would have appeared beside my commit with nothing to say they weren't mine.
Routed to the marker-promotion owner; neither is claimed here.
