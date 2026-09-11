# FINDING — THE ICON RUNG BOARD'S DENOMINATOR MOVED 297 → 55, SO EVERY ABSOLUTE WATERMARK WRITTEN AGAINST IT IS NOW UNREACHABLE

**seat** hq_C · **date** 2026-09-11 · **mode** NONET · **row** `icon-247-to-232-fifteen-program-gap` (rank 4, minted 2026-08-24)
**trees** SCRIP `522d6f8cc` · corpus `faebbb268` · .github `16576e2a` — all three `merge --ff-only origin/main` clean before measuring
**build** incremental `make` (RULES.md § FACT RULE — THE PRISTINE BUILD IS LOOSENED), `RT_OPT` = `-O0`

## THE MEASUREMENT

`scripts/test_icon_all_rungs.sh`, run under the bus's own one-runner exemption (`S4E_DONE_WHEN_RUN=1`;
the guard printed its `ONE-RUNNER: ... (exempt, one run per closure)` line, so this is a sanctioned run
and not a seat running a board on its own authority):

```
--- Icon --run: PASS=51 FAIL=4 BADEXIT=0 XFAIL=0 MISSING=2 TOTAL=55 ---
```

**2.4 s wall.** The whole board output is 36 lines.

## THE CLAIM

**`TOTAL=55`.** This board graded **293** entries when the s247 watermark was set, and **297** when
seat06 last recorded it. The row's DONE-WHEN demands `PASS=(24[7-9]|2[5-9][0-9])` — **PASS ≥ 247 on a
board with 55 entries in it.** The criterion is not red. It is **unreachable**, and it will stay
unreachable no matter how much Icon work lands, because 247 is larger than the denominator.

⭐ **THE ROW WAS DEAD TWICE OVER, AND THE TWO DEATHS ARE DIFFERENT IN KIND — WHICH IS THE POINT.**

1. **The gap it was minted for CLOSED, on the old denominator, before the corpus moved.** `SCORE.md`
   records `PASS=266 FAIL=4 BADEXIT=1 XFAIL=26 MISSING=0 TOTAL=297` at SCRIP `d24e99d89`,
   2026-09-03T21:06Z, seat06 — **266 is above the 247 watermark**, and the row has been closable on its
   own terms for eight days. `SCORE.md` further records **seven agreeing readings at 266/4 across three
   seats and multiple trees**. `GOAL-ICON-100.md` § WATERMARK records the turn even earlier:
   **232 → 244 at `be376a2f`, 2026-08-24, "ICON IS UP 12."**
2. **The ruler then shrank underneath the number.** 297 → 55. The rung programs were absorbed into the
   language masters over the same window in which `SCORE.md` shows **IcnM 642/655 → 802/802** and IPL
   34/60 → 108/108. **The corpus moving is PROGRESS**, and the progress silently invalidated the
   instrument that was measuring it.

⭐ **THE GENERAL FORM, AND IT IS THE ONE CLAUDE.md ALREADY STATES IN ANOTHER VOICE.** An absolute `PASS ≥ N`
is a watermark only while the denominator is pinned, and **nothing pins a denominator.** The org's own
standard form — *FAIL=0 over the printed denominator* — would have survived this untouched: it re-reads
the denominator every run and therefore cannot be orphaned by one. `PASS ≥ N` cannot. Every criterion of
that shape in this corpus has the same latent expiry, and **it expires without any error, on a green
tree, as a consequence of the work going well.**

## WHY IT PRESENTS AS "15 PROGRAMS ARE BROKEN" AND NOT AS "THE RULER MOVED"

The DONE-WHEN pipes the board through `grep`:

```
bash scripts/test_icon_all_rungs.sh 2>&1 | grep -E '^--- Icon --run:' | grep -qE 'PASS=(24[7-9]|2[5-9][0-9]) '
```

Every outcome that is not *"a line matching that regex"* — a board reading 51, a `⛔ REFUSE(2)` from
`lib_one_runner.sh`, a missing script, a build with no `./scrip` — collapses into the **same** exit 1,
and the row then reads exactly as it read on the day it was minted: *fifteen Icon programs are broken and
nobody owns them.* ⭐ **A criterion that funnels every distinct failure into one exit code cannot tell
you which one happened, and the reading it invites is the one written in the topic string.**

⚠️ Two instrument notes for whoever touches this next, because both misled me in turn:

- `s4e_msg.sh done` reported *"exited 1 after 3s"* and offered the hint *"the criterion produced NO output
  at all — that is itself a clue: a silent non-zero is usually a test that never ran."* **I believed it,
  and it was wrong.** The board DID run; it is simply 2.4 s long now. And the criterion ends in `grep -q`,
  which prints nothing **by construction** — so "no output" carries no information here at all. A generic
  diagnostic hint attached to a specific criterion shape can be confidently false.
- Outside `done` the same criterion collapses the one-runner `REFUSE(2)` into the identical exit 1, because
  the refusal goes to a line that does not start with `--- Icon --run:`. **A refusal and a red are the same
  observation from the queue.**

## THE RESIDUAL, NAMED — AND WHAT IS STILL ANONYMOUS

`FAIL rung36_jcon_var` is the only failure the board names. Its diff is the **display-locals-per-activation**
class: expected `co-expression_1(0)` with no locals, got `co-expression_1(1)` followed by `recurse local
identifiers:` blocks. ⛔ That is the **cto's** held row (`icon-display-reads-a-procedure-s-locals-per-activation`,
MODE line 2, both `var` files) — **named here, not touched**, so one class is not cured twice.

⛔ **THE OTHER THREE FAILURES HAVE NO NAMES ON THIS BOARD.** `rung36_all` is a suite-converted family
contributing 42 of the 55 entries, and the suite path folds `sbad=$((sfail+scrash+shang+sunproven))` into
the top-line `FAIL` while printing only an aggregate — `SUITE rung36_all: pass=39 xfail=0 bad=3 xpass=0`.
So **three Icon regressions can land, be counted, and never be named** by the board that counts them. The
per-category breakdown localises exactly one of them (`rung36_reflection total=2 PASS=1 FAIL=1`) and the
other two not at all. ⚠️ The code comment immediately above that block still reads *"Inert today: no Icon family / is suite-converted yet, so SUITE_FILES is empty in practice"* (it wraps
across two comment lines, so grep for `Inert today` to find it) — **stale**: the branch is live and
carries three quarters of the board.

`MISSING=2` — `rung16_seqexpr_gen_basic`, `rung20_section_seqexpr_excluded`, each with no `.expected` oracle.

## WHAT THIS DOES NOT CLAIM

It does **not** claim Icon is at 51/55 in any org-facing sense — this is one `--run` category view over one
shrunken tree, not the Icon board. The graded Icon suites are the masters in `SCORE.md`, and only the coo
runs those. It does **not** attribute the 297 → 55 move to any commit; the absorption is visible in
`SCORE.md`'s own IcnM and IPL rows and was not bisected here.

## THE DOCS THAT STILL READ THE DEAD NUMBER AS LIVE

- `GOAL-HQ-COMPLETE.md` — `| rungs_m3 | 232/293 | 79.2% | ⛔ −15 (was 247) |`, and, as a live instruction,
  **"Icon rungs_m3 back to 247+"**.
- `GOAL-ICON-100.md` § WATERMARK — `232/31/30 at s267 → 244/19/30`, and *"EVERY NUMBER IN THIS FILE IS a
  `test_icon_all_rungs.sh` NUMBER"*. Every one of them is over a 293/297 denominator that is gone.
- `ARCH-ICON-RTX.md` — *"GATES: Icon `test_icon_all_rungs.sh` at watermark, re-derived fresh before any edit."*
  Re-deriving it fresh is now the only safe half of that sentence; the watermark it names cannot be met.

None of these are edited by this FINDING — an owning seat changes its own goal file. They are named so the
next reader of any of them meets this measurement first.
