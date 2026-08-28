# FINDING 2026-08-28 seat03 — `corpus_suite_harness.py`'s `compile_m4()` links without `-no-pie`, making some m4 CRASH verdicts non-deterministic across runs of the identical binary

## Context
Resuming `probe-consolidate-fuzz` after hq_C's unblock (SCRIP `3987d9ba` landed `(D)` xfail/xpass
support). Of the 25 previously-loose witnesses, 20 converted cleanly; 5 failed `corpus_suite_harness.py
convert`'s byte-equal-or-no-delete check with "NEITHER form reproduced the original's behavior" even
though the "candidate" form is a byte-identical verbatim copy of the original (the harness forces
verbatim block form for any non-green original — no re-derivation is even in play).

## What was found
A byte-identical program run through the harness's own two internal measurements (once as
"original", once as a fresh-tmp-dir "candidate") should always agree if `scrip`'s behavior is
deterministic. It didn't, for 5 witnesses. Root-caused for one of them directly, not by inference:

`corpus_suite_harness.py`'s `compile_m4()` (`scripts/corpus_suite_harness.py:244`) builds the m4
binary via `scrip --compile` → `gcc -c` → `gcc <obj> -L<rt_dir> -lscrip_rt -lm -Wl,-rpath,<rt_dir> -o
<out_bin>` — **no `-no-pie`**. Reproduced by hand for `fz_segv_09.sno`: the linked binary is confirmed
PIE (`file` reports `pie executable`; the linker itself warns `creating DT_TEXTREL in a PIE`) — the
exact mechanism root's `CLAUDE.md`/`RULES.md` already document: "SCRIP mode-4 codegen embeds absolute
addresses; default PIE linking produces a DT_TEXTREL relocation the loader mis-applies." Run 5×:
**4× SIGILL (rc=132), 1× SIGSEGV (rc=139)** — the crash *signal itself* changes depending on ASLR's
per-exec load address. The identical `.o`, re-linked with `-no-pie` and otherwise unchanged, run 5×
the same way: **5× SIGSEGV (rc=139)**, perfectly stable.

`Verdict.behaviorally_equal` requires an exact signal match for a CRASH kind
(`self.returncode == other.returncode`, `corpus_suite_harness.py:191`) — against a source this
unstable, no candidate could ever reproduce it, mechanically, regardless of how faithfully the
conversion preserves the source text. `convert_one`'s own "original" measurement is itself just
one random draw from the same instability, so even the reported "orig" verdict for these witnesses
is not a reliable baseline.

**This is the third occurrence of the identical defect class in this project**, not a new one:
1. `test_crosscheck_sc_corpus_rung.sh` — missing `-no-pie`, found and FIXED by seat07
   (`SCRIP@3dc642fd`, 2026-08-27).
2. `test_corpus_snobol4.sh`'s own `compile_mode4()` — missing `-no-pie`, found and FLAGGED-NOT-FIXED
   by seat07 the same day ("it's the primary SNOBOL4 gate... a question for hq_C, not a unilateral
   call").
3. `corpus_suite_harness.py`'s `compile_m4()` — this finding. Arguably the widest blast radius of the
   three: every language's suite-format conversion (`convert`, `convert_one`, `run`) routes m4
   grading through this exact function, not just SNOBOL4.

## Effect on probe-consolidate-fuzz (this row)
20 of 25 converted this session (SCRIP xfail support unblocked them); pushed, `test_corpus_snobol4.sh`
clean (1120/1120 both modes, FAIL=0/SKIP=0/MISSING=0), harness's own `run` on the merged suite: `SUITE_
BOARD family=fuzz total=54 m3_fail=0 m4_fail=0` (one benign, already-documented XPASS —
`fz_red_m2_breach_m3only`'s m4 side, unrelated to this finding). 5 stay loose (`probe/fuzz/KEEP.md`,
rewritten this session) specifically because of the instability above — a DIFFERENT reason than the
`(D)` xfail/xpass gap that blocked all 25 an hour prior. Two of the five (`fz_red_m1b_arbno_defer_
blob`, `fz_segv_24`) also have an `m3` `HANG` side, which does **not** route through `compile_m4()` —
their instability may need a second explanation (general ASLR of stack/heap/`libscrip_rt.so` placement,
since `scrip` itself is already linked `-no-pie`); not chased further, out of this row's scope.

## What was NOT done (deliberately)
**Did not patch `compile_m4()`.** Same restraint seat07 already showed on `test_corpus_snobol4.sh`'s
own gate, applied here with even more reason: this function is the ONE shared m4 path for every
language's conversion across the entire `corpus-suites-consolidation` fan-out, not a single family's
concern. Adding `-no-pie` would very likely be strictly corrective (it stabilized `fz_segv_09` in the
direct test above, with no observed downside), but changing it now, mid-fan-out, with many concurrent
seats converting other families through the same harness, deserves hq_C's sign-off rather than a
seat's unilateral edit — the same judgment call this project has already made once this week, not a
new one.

## Recommendation
Add `-no-pie` to the `gcc ... -o <out_bin>` link step in `compile_m4()`
(`scripts/corpus_suite_harness.py:260`), matching the ~120 other m4 link sites in `scripts/` that
already carry it. Likely (not verified beyond `fz_segv_09`) that this alone converts some or all of
the remaining 5 `probe/fuzz` witnesses, and may retroactively stabilize other already-converted
families' m4 CRASH verdicts that happen never to have been re-measured enough times to notice the
same flakiness.

Sent to hq_C via `s4e_msg.sh send` (topic `corpus-suite-harness-compile-m4-missing-no-pie`).
