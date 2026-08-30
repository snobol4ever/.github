# FINDING 2026-08-29 seat04: array-sum-valgrind-segv's own BRIEF claim ("unmeasurable by the one instrument
# immune to our four other instrument defects") is now stale — a working, already-proven alternative exists
# for the class of measurement every citing perf row has actually wanted.

Row: `array-sum-valgrind-segv`. Not a cure for the underlying Valgrind-exclusive crash (still open, see the
row's own LEDGER for four passes of root-cause and mechanism work) — this documents a practical mitigation
so the row's DONE-WHEN doesn't have to wait on Valgrind's own internals being fully understood.

## What's confirmed
Built this row's own pinned witness, `corpus/benchmarks/snobol4/array_sum.sno`, as a standalone mode-4 binary:
`scrip --compile array_sum.sno -o array_sum.s < /dev/null`, then `gcc -no-pie array_sum.s -L SCRIP/out
-lscrip_rt -lm -Wl,-rpath,SCRIP/out -o array_sum_bin` (the exact technique `perf-match-begin-beta-cure`
independently proved out, for a different reason — separating compile from run so a profiler sees 100% runtime,
0% compiler noise). Ran it under real `perf` (`/usr/lib/linux-tools-6.8.0-138/perf` — kernel-version-mismatched
against this container's `6.17.0-1032-oem` but confirmed working regardless, same finding as the perf row):

```
sum of 2,4,..,1000 = 250500
after 20 rebuilds  = 250500
Performance counter stats: 9,152,372 instructions:u
```

Clean exit, zero crash, zero Valgrind involvement anywhere in the chain.

## What this does and doesn't mean
- **Does:** `array_sum`, `table_access`, and by extension any array/subscript/table-heavy SNOBOL4 program can
  be profiled for cycle/instruction-level attribution via the standalone-binary + real-`perf` recipe, which is
  exactly what every perf row that has cited this class of program has actually needed (attribution, not
  leak-checking).
- **Doesn't:** replace Valgrind for whatever this row's original brief cared about specifically —
  uninitialized-read detection, memory-safety checking. If a future row needs THAT class of guarantee on
  array/table-heavy code, this mitigation doesn't help it; the underlying crash still blocks Valgrind itself.
- **Doesn't:** cure or further explain the crash mechanism. The leading hypothesis (a Valgrind-internal
  artifact, not a SCRIP-owned unregistered stack — native-absent, address-fixed across ASLR, appears only
  under Valgrind on first occurrence of this code path) stands exactly as the prior four passes left it.
  Confirming it definitively would need Valgrind's own C source (`coregrind/m_main.c`/`m_signals.c`), judged
  by two prior passes as uncertain payoff for a bug that affects tooling usability, not native correctness —
  not attempted again here for the same reason.

## Why this is being written up now
So the row's DONE-WHEN can close on "root cause understood to this confidence level + a working alternative
documented" rather than requiring Valgrind's own internals to be solved — a proposal routed to ceo rather than
applied unilaterally, since redefining a row's own completion criterion is exactly the kind of call this
project's own discipline routes past one seat.
