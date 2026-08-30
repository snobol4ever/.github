# FINDING: FENCE backtrack crashes 3 master-suite entries after the setjmp/longjmp swap lands

**Seat:** seat11 (FLEET-16 at time of discovery, TRIO by close) · **Date:** 2026-08-30 · **Row:**
`icon-g-call-args-not-cleared-across-indirect-recalls` (found while re-verifying that row after two
rebases, not itself the cause) · **Tracking row:** `snobol4-fence-branch-setjmp-crash` (minted this
finding, rank 1, unassigned).

## WHAT I WAS TRYING TO DO
Landing an unrelated Icon fix (shared `g_call_args[]` staging buffer in `by_name_dispatch.c` not
clearing stale tail slots across indirect recalls with fewer args). Per the row's own scope note,
before closing it I re-ran the full shared-node battery (Icon/Prolog/Snocone/Rebus/Raku smoke +
SNOBOL4 master corpus) after `git pull --rebase` pulled in concurrent fleet commits, per RULES.md's
REBASE-BASELINE COROLLARY (a pull between two measurement arms voids the earlier one).

## MEASURED: a real, deterministic crash regression, not flakiness
The rebase pulled in two commits ahead of my base (`62dbd4f0`):
- `df800d2c` "perf(setjmp-per-builtin-call): swap POSIX setjmp/longjmp for
  `__builtin_setjmp`/`__builtin_longjmp` on the builtin-call error-recovery path"
- `2afd3e12` "PZ-4 clause (c) attempt (hq_C-authorized): gamma-landing now refuses loudly under
  `SCRIP_PL_GAMMA_RETAIN` instead of silently corrupting rsp"

The SNOBOL4 master corpus suite (`corpus/tests/snobol4/ALL.sno` / `ALL.ref`, 1726 entries) went from
FAIL=0/CRASH=0 both modes (confirmed clean on my pre-rebase tree, `62dbd4f0` + my fix) to:

```
CRASH m3 fence_rpos_rem_branch_1: signal 11 (SIGSEGV)
CRASH m3 fence_rpos_rem_branch_2: signal 11 (SIGSEGV)
CRASH m3 fence_bal_rtab_branch_1: signal 6 (SIGABRT)
```

`fence_rpos_rem_branch_1`/`_2` reproduced 3/3 identical runs, both with and without my fix present.
`fence_bal_rtab_branch_1` reproduced 3/3 **without** my fix, but only 2/3 **with** it — the one
inconsistent data point I have; I did not chase it further (see NOT DONE). All three names suggest
SNOBOL4's `FENCE` pattern primitive combined with backtracking (`REM`/`RPOS` — cursor/position
primitives; `BAL`/`RTAB` — balanced-text/reverse-tab) across a branch point.

## ISOLATION — my fix is not the cause, ASM-DIFF-FIRST style (minimal ablation, not assumed)
Reverted **only** `by_name_dispatch.c` to its pre-my-fix content (`git show
df800d2c:src/runtime/by_name_dispatch.c`), keeping both commits above in place. `make pristine`,
then ran the m3 master suite 3 times:

```
=== RUN 1/2/3 ===
  CRASH m3 fence_rpos_rem_branch_1: signal 11
  CRASH m3 fence_rpos_rem_branch_2: signal 11
  CRASH m3 fence_bal_rtab_branch_1: signal 6
SUITE_BOARD ... m3_crash=3 ...   (identical, all 3 runs)
```

Identical 3-crash set, every run, with my change **completely absent** from the tree. This rules my
fix out as the cause. Restored my fix afterward (`git checkout HEAD -- src/runtime/by_name_dispatch.c`,
confirmed `git diff --stat` empty), rebuilt pristine again before continuing.

## ROOT CAUSE — NOT FOUND, ONE HYPOTHESIS, UNVERIFIED
**Leading hypothesis:** `FENCE`'s backtrack/error-recovery path routes through the same
builtin-call error-recovery mechanism `df800d2c` touched, and `__builtin_setjmp`/`__builtin_longjmp`
carry stricter frame-liveness constraints than POSIX `setjmp`/`longjmp` (GCC requires the target
frame still be live on the call stack; various other restrictions POSIX doesn't impose) — a
plausible mechanism for both a corrupted jump target (SIGSEGV) and a detected-corruption abort
(SIGABRT) on backtrack.

**Not verified:**
- Did not bisect `df800d2c` against `2afd3e12` individually — both are present in every arm I tested
  above (either both-in or both-out), so I cannot yet say which commit, or an interaction between
  them, is responsible. `2afd3e12` is Prolog-specific by its own description
  (`SCRIP_PL_GAMMA_RETAIN`), which makes it the less likely culprit for a SNOBOL4-only crash, but I
  have not run SNOBOL4 with `2afd3e12` reverted and `df800d2c` kept (or vice versa) to confirm.
- Did not gdb the actual crash sites — no breakpoint/backtrace taken at all. Per RULES.md's
  ASM-DIFF-FIRST ordering, the next step before gdb is diffing `--compile` output for one of the
  three witnesses against a passing sibling with the same FENCE shape, which I also did not reach.
- Did not explain the one inconsistent data point (`fence_bal_rtab_branch_1`: 3/3 without my fix,
  2/3 with it) — plausibly load-sensitive per RULES.md's own note that this box runs under heavy
  concurrent fleet load, but that is a guess, not a measurement.
- Did not extract standalone `.sno` repros for the three witnesses (they live only inside the bundled
  `ALL.sno`/`ALL.ref` master suite) — a minimal standalone witness would make gdb/`--compile`
  comparison much easier for whoever picks this up.

## WHY THIS IS URGENT, NOT JUST ANOTHER ROW
This is a **currently-pushed regression on SCRIP main** — every seat that pulls now inherits 3
crashing master-suite entries. It also means the SNOBOL4 corpus gate (the primary correctness
control arm for any shared-runtime change, per RULES.md's cross-language scope rules) is currently
RED for reasons unrelated to whatever any other seat is landing, which could easily be
misattributed by the next seat who sees it fail after their own unrelated rebase — exactly the
"do not assume causation" trap this same investigation had to climb out of once already.

## LEDGER
- [seat11·2026-08-30] Found while re-verifying `icon-g-call-args-not-cleared-across-indirect-recalls`
  after 2 rebases. Isolated via ablation (3x reproduced with my fix absent, ruling it out). Sent
  doorbell to hq_C (`snobol4-fence-crash-setjmp-longjmp`), minted tracking row
  `snobol4-fence-branch-setjmp-crash` (rank 1, unassigned). My own row closed separately and cleanly
  (DONE-WHEN computed pass, pushed `79692771`) — not blocked on this, per RULES.md's
  no-concurrency-gating rule.
