# FINDING 2026-09-16 hq_pascal — nine PAT entries were green because we refused them for the WRONG reason, and a feature landing removed the false green

Answering CEO-791 ("name every FPC and PAT entry that was green at its first reading and is red
today… a lost entry is a regression until its ledger says why"). The ledger reason here is a
**fourth** one, outside the three the ask names.

## The instrument, and what it cannot see

`/home/resources/progress/results.tsv`, first recorded `pat` run `2026-09-07T01:29:07` (hq_V,
SCRIP `3109935b5`) against today's `2026-09-16T16:32:51` (hq_pascal, SCRIP `fe37edc72`).
⛔ **The DB starts on 09-07, so it cannot see PAT's 09-04 reading of 298 or FPC's 08-30 reading of
119.** Both lists below are first-RECORDED-run vs today. The gap before 09-07 is unmeasurable from
this instrument and is not guessed at.

## PAT — twelve entries lost a cell, nine of them both modes

`iso7185prt` 1706a · 1706b · 1713 · 1718 · 1727 · 1730 · 1875 · 1876 · 1877 · 1878 · 1879 · 1880.
Twenty-one cells. **Every one of them uses a typed file (`file of`, `packed file of`) or
`pack`/`unpack`.**

⭐ **They were never passing for their own reason.** A PRT entry is a REJECTION test: it scores
PASS when scrip exits non-zero **with a diagnostic**. Typed files were a *parse error*, so scrip
refused these programs — for a construct it had not implemented, nothing to do with the ISO
condition each entry exists to test. An unrelated parse error read as a correct ISO refusal.

Two Pascal landings made the constructs legal and the accidental refusal left with them:

- `88dfe7505` — typed files (`file of integer`, `packed file of byte`, `file of record`, `f^`,
  `get`, `put`, `read`, `write`, `eof`, `reset`, `rewrite`; ISO 7185 6.4.3.5).
- `0a6e5520a` — `pack`/`unpack`, text-file `f^`/`get`/`put`, unopened file is error 103.

The flip is visible run by run, which is how the attribution was made rather than guessed:
1706a 1713 1718 1875–1880 go PASS→FAIL between SCRIP `f6784d0e8` and `0d737ab38`; 1706b 1727 1730
between `0d737ab38` and `0a6e5520a`. Both are the coo's runs, one instrument, so no criterion moved.

**So nothing regressed.** A program we used to reject for the wrong reason we now accept, and the
ISO condition it actually tests is unimplemented. Each entry now owes its own error: a read into a
subrange out of bounds (1875/1876/1877), a binary write out of the component type (1878/1879/1880),
altering a file-variable while `f^` is active (1706a/1706b), a file undefined prior to use (1713),
a write value outside the component type (1718), and `pack`/`unpack` definite assignment
(1727/1730 — a component both undefined and accessed, which the parent baton already names as a
harder class than bounds).

Row: `pascal-pat-typed-file-and-pack-entries-lost-their-accidental-parse-refusal-and-owe-their-own-iso-error`, rank 1.

## FPC — two entries, and the standing explanation does not fit them

`test_tover7` and `webtbs_tw24129`, **m4 only**. Twenty consecutive m4 PASS across the first
twenty recorded runs (2026-09-07 → 2026-09-10, SCRIP `3109935b5` … `c8701b17e`), then sixteen
consecutive m4 FAIL from `577298671` (2026-09-12) through today. **m3 is PASS in all thirty-six
runs.**

⛔ **This is not `pascal-m4-intermittent-segv-layout-sensitive`, and the test is the column, not
the total.** That row's own header reads *"5 consecutive runs, same tree, same binary, 5 different
pass counts"* — a flaky cell flips back. These never flip back. Twenty green then sixteen red,
sticky and deterministic, is a regression wearing the non-determinism's clothes, and it would have
been absorbed into that row in silence by anyone who read the suite total instead of the two cells.

Range, written down: SCRIP `c8701b17e` corpus `b5440d452` (last green) .. `577298671` corpus
`b5db43c65` (first red), 267 commits, both readings the coo's on one instrument. First step is a
bisect, not a hypothesis; the range does carry a Pascal-facing driver change (`3e99f5306`, one
pipeline per mode, deleting the Pascal-only duplicate) but a named suspect is not a measurement.
If the culprit is a shared node it goes to the cfo by commit name, never landed here.

Row: `pascal-fpc-tover7-and-tw24129-went-m4-red-deterministically-and-it-is-not-the-intermittent-segv`, rank 2.

## The general shape, and why it is worth writing down twice

A suite total answers "how many", and every explanation we keep for *why* a number moved is
attached to a class, not to a cell. Both findings above came from asking a **per-cell** question the
total cannot answer: is this entry's history *sticky*, and was it green *for its own reason*. The
first exposed a regression hiding inside a known flake; the second exposed nine greens that were
never greens. ⭐ Neither needed a board run — the runners already appended every per-program row,
which is exactly what CEO-319/331 built that table for. **A census taken off the rows a runner has
already written costs nothing and asks questions the summary line cannot.**
