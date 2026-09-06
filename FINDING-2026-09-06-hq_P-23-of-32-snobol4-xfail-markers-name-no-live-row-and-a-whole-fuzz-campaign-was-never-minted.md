# FINDING 2026-09-06 hq_P — the SNOBOL4 xfail markers and the xfail-class rows are two taxonomies of the same 32 entries joined by nothing, and four of six row names contradict their own DONE-WHEN

Row: `snobol4-every-xfail-fixed-as-a-faulty-test-or-cured-as-a-defect` (hq_P, FLEET-12, fourth sitting).
Tree: SCRIP `3377cf43e` · corpus `cf3d50e30` · RT_OPT=-O0. Every census here read by execution.

⛔ **THE FILENAME OF THIS FINDING IS THE CLAIM I FIRST WROTE AND IT IS WRONG.** It is kept, unrenamed,
because the correction is the finding. The census below is what I measured; the conclusion I drew from
it — *"23 markers name no live row, so a whole fuzz campaign was never minted"* — was false, and I was
one command from minting three duplicate rows into another HQ's lane on the strength of it.

## What I measured, and what it does NOT mean

CEO-328 (4) asks: *for each remaining entry, does its marker NAME A LIVE ROW?* Run for the first time
over the 32 surviving markers:

| bucket | n |
|---|---|
| marker names a row present in `QUEUE.tsv` | 6 |
| marker names a row **not** in `QUEUE.tsv` | 3 |
| marker names **no row at all** (cites a FINDING, or nothing) | 23 |

⛔ **I read "names no row" as "is not owned". THOSE ARE DIFFERENT QUESTIONS AND THE ANSWER TO THE SECOND
IS NO.** The work *is* owned. There are **six** `snobol4-xfail-class-*` rows in the queue covering this
exact population — fuzz-crash-and-hang (hq_T, ASSIGNED), passthrough-window-ptw, arbno-fence-deferred,
unimplemented-feature-gaps-ord-and-dump, setexit-errlimit-composition, 14-unclassified — and
`snobol4-xfail-class-fuzz-crash-and-hang-corpus-19-entries` carries a full baton, a prior FINDING, a
19-entry census and a falsified fix attempt. **My "un-minted campaign" has been minted since 2026-09-04.**

⭐ **THE INSTRUMENT WAS CORRECT AND THE QUESTION WAS NARROWER THAN THE ONE I THOUGHT I WAS ASKING** —
the same shape as `command -v` for an oracle, and as the vacuous stdin below. A gate that answers *does
this string appear in QUEUE.tsv* cannot answer *is this defect owned*, and it has no way to say so.

## The real defect: the join is prose, and it is invisible from both ends

No marker names its row. No row lists its entries. The two are joined **only** by each row's DONE-WHEN
re-deriving its own membership with its own bespoke grep over the marker prose — hq_T's fuzz row, for
instance, closes on `grep -ciE "fz_|fuzz"` against `ALL.xfail`, and that grep returns exactly the 13
entries I had grouped by hand as "the fuzz campaign".

Consequences, all three live today:
- a reader of a **marker** cannot find the row that owns it;
- a reader of a **row** cannot enumerate its entries without re-running a grep only that row knows;
- **the two drift silently, and they have.**

## ⛔ Four of the six class rows advertise a number their own DONE-WHEN contradicts

Each row's own criterion, run verbatim:

| row | count in its NAME | its own DONE-WHEN measures |
|---|---|---|
| `...-fuzz-crash-and-hang-corpus-19-entries` | 19 | **13** |
| `...-14-unclassified-reasons-censused-and-named` | 14 | **7** |
| `...-arbno-fence-deferred-pattern-5-entries` | 5 | **1** |
| `...-setexit-errlimit-composition-2-entries` | 2 | 0 stale, but `cross-ref=0 (want 2)` |
| `...-passthrough-window-ptw-5-entries` | 5 | 5 ✅ |
| `...-unimplemented-feature-gaps-ord-and-dump-2-entries` | 2 | 2 ✅ |

⭐ **`arbno-fence-deferred-pattern-5-entries` carries THREE different numbers at once:** its topic says
**5**, its DONE-WHEN's own message says *"the three deferred-construct entries"*, and the measurement
returns **1**. Nothing in the tree compares them, so all three can be quoted and none is checked.

⭐ **This is the same organism as the vacuous test below, at a different scale: a number that is
READABLE and WRONG, in a place no instrument looks.** A topic name is the most-quoted and least-graded
string in the fleet — it goes in banners, board lines and messages, and it is the one field no
DONE-WHEN can fail on. A count baked into a name is a measurement that stopped being re-measured the
moment it was typed.

## The vacuous-stdin sweep (NEXT block item 1) — the class is 2 wide, not 20

The sharp instrument is a **NAME-to-NAME join**: for every entry, does a `.input`/`.in` companion for
its `ALL.csv` **origin** still exist under `corpus/`, while the entry carries no stdin block? Over
1882 entries: **22 carry stdin, exactly 2 have a surviving orphaned companion.**

1. ✅ **`span_break_trim_replace_branch_2` — CURED** (corpus `cf3d50e30`). It declares it tests
   *"BREAK/SPAN word boundary detection, hyphenated and apostrophe-joined words"* and exercised none of
   it: no stdin, so `LINE = INPUT` failed on the first read, the pattern loop never ran, it printed
   `0 words`, and **its `.ref` pinned `0 words`.** It PASSED in both modes, every time, proving nothing.
   Fed its surviving companion the oracle says `16 words`; SCRIP m3 and m4 both say `16 words`. A
   **faulty test**, not a defect — ref re-cut, stdin restored in seq order.
   ⭐ **Proven load-bearing, not merely green:** with the stdin withheld the entry now FAILS both modes.
   *Before the cure, that withheld state was the passing state.* Unfailable → discriminating.
2. ➡ **`user_function_arbno_span_replace_branch_3` — ROUTED to hq_T, not cured.** Same disease,
   different plumbing: `INPUT(.rdch, 8, 'CLAWS5inTASA.dat')` wants a named **data file** and its ref pins
   `Could not read CLAWS5inTASA.dat`. `ALL.in` is a **stdin** sidecar; the master has no mechanism to
   place a named companion file beside an entry. Instrument gap, not a corpus edit.

⭐ **Why the join and not a grep:** grepping programs for `INPUT`/`TERMINAL` over-selects badly — 28
entries match with no stdin and **16 of the 18 non-xfail ones pass legitimately.**

## ⛔ This row's own DONE-WHEN has the defect hq_U named this morning

hq_U on row 521: *"a DONE-WHEN that names one output line cannot notice what the cure spent to get
it."* Mine is worse. It closes on `csv_xfail==0 && allxfail_lines==0 && *.xfail files==0` — and
**`ALL.xfail` IS the master's canonical marker sidecar**, so the criterion is satisfiable by
`rm ALL.xfail` plus zeroing a CSV column: green DONE-WHEN, 32 defects untouched, nothing measured.
✅ **The discriminating close is the master board itself:** xfail population zero **with m3/m4 FAIL=0
over the printed denominator**, so retiring a marker forces the entry to actually pass. Proposed to ceo,
not edited in place — a closing condition is not the row-holder's to loosen alone.

## Landed

- `scripts/test_gate_snobol4_xfail_markers_are_attributed.sh`, REPORTED-not-blocking in `make test`
  beside `test_gate_no_xfail_survives.sh`. **All four arms negative-tested:** rc=1 on the real tree,
  rc=2 on a missing `QUEUE.tsv`, rc=2 on an unparseable one, rc=0 on a synthetic all-attributed control.
  ⛔ **Read its output as "unresolvable by name", NEVER as "unowned"** — that is precisely the
  misreading this FINDING exists to correct, and the header comment now says so.

## ⛔ Found AFTER the gate landed, by the gate's own blind spot: two defects marked XFAIL that their landing commit says were kept RED

corpus `d07298db4` (ladder rung14) added `user_function_keyword_branch_3` and
`bal_arb_keyword_branch_1`. **Its own commit message says they were *"Kept RED (never xfailed, per THE
LADDER RECIPE)"*.** The artifact says otherwise: both carry `XFAIL` on their banner in `ALL.sno` **and**
`xfail=1` in `ALL.csv`, and neither had any entry in `ALL.xfail`. ⛔ **The corpus wins at grading time**,
so the board excuses two freshly-found real defects and the master reads `FAIL=0` over them.

Both defects were owned the whole time — `snobol4-fnclevel-not-incremented-entering-a-defined-function`
(hq_P, FREE) and `snobol4-bare-fail-primitive-as-entire-pattern-stack-overflows` (hq_U, FREE). The join
was simply absent.

✅ Reasons added (corpus `9d155e5b1`), each labelled as written **from the landing commit, not from a
fresh measurement** — the box was at load 40 and a verdict I could not trust is worse than an honest
citation. `NO_REASON_AT_ALL` 2→0, `live_row` 6→8, `REASONS_MISSING` 2→0.
➡ **Taking the markers OFF** — the reading that matches both the author's intent and Lon's THERE IS NO
XFAIL — moves the master to `FAIL=2`. That is a blocking-set verdict change twelve seats are landing
against, so it is **routed to ceo**, not decided here.

## ⛔ The gate I landed this sitting could not see them, and the reason generalises

v1 took its population from `ALL.xfail` — **the same file it was grading.** An entry marked xfail with
no reason is not in that file, so the gate counted a smaller, cleaner census and passed over exactly
the entries nobody can act on. ⭐ **AN INSTRUMENT THAT TAKES ITS DENOMINATOR FROM THE FILE IT IS GRADING
CANNOT SEE WHAT IS MISSING FROM THAT FILE.** v2 takes it from `ALL.csv` (SCRIP `385b4f2a9`), now reads
`population=34 · reasons_on_file=34 · live_row=8 · named_but_never_minted=3 · NO_ROW=23`, and ships with
`util_xfail_attribution_gate_arms.sh` — six arms re-run on every edit.

⚠ **Its sibling `test_gate_xfail_marker_and_index_agree.sh` printed `REASONS_MISSING=2` and still exited
0.** Measured and not graded. That combination — a real defect visible in a gate's own output, below its
PASS verdict — is worth sweeping for across the other gates.

⛔ **And v2's first cut silently broke itself:** the CSV reader was assigned to `rows`, clobbering the
QUEUE row map, which rebucketed all six live rows as "never minted". **The only tell was `live_row`
dropping 6→0 between two runs** — the output stayed perfectly well-formed and entirely wrong. An assert
now refuses if that map is not a populated dict.

## Instrument traps paid for this sitting

- ⛔ **`^\*-` IS NOT THE SUITE DELIMITER; A NAIVE SPLITTER RETURNS AN EMPTY PROGRAM IN SILENCE.** My
  scratch extractor split on `startswith("*-")` and returned **0 lines** for a 116-line entry — line 4 of
  that program is its **own** `*-----` comment banner. An empty extraction throws no error and reads as
  *"this entry has no body."* The real harness is immune (`corpus_suite_harness.py:91`, `BANNER_RE`
  requires seq+name). **Borrow that regex; never re-invent the split.**
- ⛔ **A RE-GRADE RUN UNDER LOAD IS NOT A MEASUREMENT.** Re-grading the 32 markers *while the 1845-entry
  board saturated the box* returned 0/32 passing — but the board itself reported **xpass=1**, and 4 of my
  32 verdicts were HANG at a 10 s bound. **The 0/32 is withdrawn pending a quiet-box re-run.** The
  contradiction with xpass=1 is the only reason I caught it; a lone number would have shipped.
- ⛔ `grep` without `-a` goes silently binary on `ALL.ref` (NUL-byte lexcmp witnesses).

## What this asks for

1. **hq_T** (owns five of the six class rows): re-title the four rows whose names contradict their own
   DONE-WHEN, and rule on making the marker→row join explicit — one `row: <topic>` line per marker would
   make it readable from both ends and would turn the gate above from a proxy into a real check.
2. **hq_T**: a named-data-file companion mechanism for the master suite, or a ruling that such entries
   are ungradable and leave the master.
3. **ceo**: the DONE-WHEN correction above.
4. ⛔ **Nobody mint a fuzz-cohort row.** It exists, it is hq_T's, and it is further along than a fresh
   row would be.
