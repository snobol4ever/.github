# FINDING seat01 2026-09-05: same-invocation determinism checks have a blind spot; 4 programs falsely read LIVE

Continuing task `icon-ipl-851-run-graded-against-iconx-refs-and-cured-by-class` (STEP 1) after
seat03's `unclaim` at 2026-09-05T16:32Z. Re-ran `util_cut_icon_ipl_refs.sh -v` fresh (SCRIP `da9ba149`,
corpus `4e11cb9ee`) to get the full per-file breakdown behind the summary counts in the task's own
ledger. Two programs classified LIVE by that run that were NOT in seat03's original 6-program flaky
list (`gcomp.icn`, `qt.icn`) looked like real candidates to reverse. Investigating them before minting
surfaced a class of false accept the script's own 4-agreeing-run bar cannot see.

## The mechanism

`util_cut_icon_ipl_refs.sh`'s determinism check runs a candidate 4 times **within one script
invocation**, fresh isolated scratch copy each time, and mints only if all 4 agree. This is exactly
right for nondeterminism whose period is shorter than the invocation's own wall-clock span (RNG seeded
per-run, e.g. `puzz.icn`/`solit.icn`/`farb.icn`/`parens.icn` via `&clock`-seeded `&random` or
`randomize()` — all four correctly caught as NONDETERMINISTIC today). It structurally **cannot** see:

- **Wall-clock output at coarser granularity than 4 quick runs apart.** `filexref.icn` (source line 131)
  and `shar.icn` (source line 34) both embed `&dateline` — the current date/time — verbatim in their
  output. Four runs a fraction of a second apart trivially agree; the pin still breaks the next time
  it's graded on a different date. `qt.icn` (links `datetime`, "announce the time in English") reads
  the **live system clock** when given no argument and prints it as prose ("It's just after a quarter
  to three.") — same shape, coarser failure window (however long the English-phrase rounding bucket is,
  observed here as small enough that 8 back-to-back runs still agreed, but a run minutes apart did not).
- **Reading the very corpus this task is mutating.** `gcomp.icn`'s entire body is
  `open("echo * .*","rp")` — it prints the **live directory listing of progs/**, sorted, minus argv.
  Called with zero args (as this harness always does), its output is exactly "every file currently in
  progs/". Since STEP 1's whole job is to mint new `.std` files into that same directory, gcomp's
  "correct" output changes every time the population changes — pinning it is self-defeating almost by
  construction, independent of any timing question.

Confirmed by source (`grep -n '&dateline\|&clock\|&random' progs/{filexref,shar,puzz,solit}.icn`,
`cat progs/gcomp.icn`, `cat progs/qt.icn`), not by inference. `puzz.icn`'s `&random:= map(&clock,...)`
(line 50) and `solit.icn`'s `&clock`-seeded `seed` (lines 768-773) match seat03's original diagnosis for
those two exactly; `noise.icn` also carries this mechanism (TIMEOUT bucket, "generate random noise" per
its own header, matches seat03's separate 8.7GB-RSS incident write-up).

## How this was actually caught (not just theorized)

1. Today's classifier run: `gcomp.icn`/`qt.icn` LIVE (4/4 agree), `filexref.icn`/`shar.icn` also LIVE.
2. A manual 8-independent-run check (fresh isolated scratch copy each time, same discipline as the
   script's own `run_isolated`) on `gcomp`/`qt` alone: 8/8 byte-identical for each. Looked like solid
   confirmation of seat03's original flaky-list being wrong for these two.
3. Reading source instead of trusting the sample: `gcomp.icn`'s only logic is the directory-listing
   read; `qt.icn`'s only logic is the wall-clock announce. Neither should ever have been sampled as if
   they were pure functions of nothing.
4. A real mint attempt (redirecting a fresh oracle run's stdout straight to the target `.std` path,
   **not** through the 8-run test harness) produced a **third, different** byte count for both
   (`gcomp`: 3764 -> 3765 bytes; `qt`: 33 -> 27 bytes) — proving the 8/8 and 4/4 agreements were sampling
   coincidences (an unperturbed template reused across nearby-in-time runs), not true determinism.
   `.std` files from that attempt were deleted, never committed.

## Disposition

All 4 (`filexref.icn`, `shar.icn`, `gcomp.icn`, `qt.icn`) added to `progs/UNGRADED.tsv` (new manifest,
this session) with status `LIVE-BUT-EXCLUDED` and the mechanism named — seat03's original exclusion of
`filexref`/`shar` stands, confirmed; `gcomp`/`qt` are a NEW addition to the exclude set (today's
classifier had them wrong). Net effect on the run-graded population: still 60 (no new mints this
session — the two that looked promising were exactly the two that needed to NOT be minted).

## Recommendation (not done this sitting — census/harness-fixing is in scope, not a requirement of
this row's own DONE-WHEN)

`util_cut_icon_ipl_refs.sh`'s LIVE classification should add a **static source grep** for
`&dateline|&clock|&random|randomize\(|open\(.*"..*p"` (pipe-opened subprocess reads, of which `echo *`
is one instance) as a second, independent gate alongside the 4-run repeat check — belt-and-suspenders,
same discipline the script already uses for MAX_BYTES and the isolation-copy hazard. Neither failure
mode here is rare or exotic: IPL is full of demo/game programs that are random or environment-reading
*by design*, not by defect, and the repeat-run check alone will keep false-accepting them.
