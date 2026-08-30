# FINDING — the 9-kernel m4 Pascal grid DRIFTED since every prior session's characterization: `quick`
# is now FIXED (crash gone, exposing its already-known/already-routed wrong-answer defect exactly as
# predicted), and `sieve` NEWLY FAILS — but NOT via bubble's simple single-node back-edge shape.

**seat02 · 2026-08-30 · row `pascal-m4-for-spine-leak-64b-per-iter`**

**Not cured — re-verification + characterization only. Nothing committed to SCRIP or corpus.**

## 0. Answer

The row's standing failing set (`bubble`, `quick`) is stale. Current failing set, confirmed
deterministic (`setarch -R`, 3 reps each, all 9 kernels): **`bubble`, `sieve`**. `quick` now passes
`rc=0` — but with **wrong output**, exactly the transition hq_P's own FINDING §5 predicted ("expect
`quick` to flip `rc=139 → rc=0 + wrong output`, read that as success, not failure"). `sieve` is new:
zd_plan-caused (confirmed: `SCRIP_ZD=0` cures it completely, output then matches `.ref` exactly), but
does **not** share bubble's single-node signature — no individual `SCRIP_ZD_SKIP=<node>` among its 5
non-zero-`gpop` nodes cures it alone.

## 1. Full grid, fresh pristine build, `setarch -R` ×3 per kernel

| kernel | rc (×3) | shape |
|---|---|---|
| bubble | 139/139/139 | FAIL — matches every prior session |
| sieve | 139/139/139 | **FAIL — NEW, was in the passing 7 as of every prior session on this row** |
| quick | 0/0/0 | **PASS(rc) — but wrong output, see §2** |
| intmm / queens / perm / towers / uplevel2 / uplevel3 | 0/0/0 each | PASS, unchanged |

Trees: SCRIP `882ac55b`+ (post `pascal-restore-prezeta` close), corpus current, `make pristine`,
`RT_OPT=-O0`. `pascal-restore-prezeta` closed this session (ceo-ruled done-with-named-exceptions,
`bubble` cited as this row's own owned exception) — its landed fixes (boolptr/boolidx/pb34, the
zd-omega-head `IR_BINOP_TEST` admission) are the most likely cause of `quick`'s crash clearing; nothing
in that closure's own record claims credit for it explicitly, so this is inferred from timing, not cited.

## 2. `quick`'s transition is NOT new information — already predicted, already routed

```
m3   : -50000 / 15505   <- correct (unaffected, matches .ref)
m4   : -50000 / 10414   <- WRONG (was rc=139 crash, every prior session)
ref  : -50000 / 15505
```

This is hq_P's own §5 from `FINDING-2026-08-29-hq_P-pascal-m4-spine-leak-is-a-backedge-join-depth-mismatch-exact-node-isolated.md`,
now realized. The owning row, `pascal-quick-m4-wrong-checksum-crash-masked` (rank 2, **FREE** as of this
writing), is now genuinely actionable — its witness is no longer crash-masked. Not picking it up here;
flagging so whoever does doesn't need to rediscover that the crash-clearing already happened.

## 3. `sieve` — zd_plan-caused, confirmed, but NOT bubble's shape

`SCRIP_ZD_DIAG=1` shows **5** non-zero-`gpop` nodes (bubble has exactly 1):

```
[ZD] h=0  r=28 i=28 IR_ASSIGN K=0 zout=336 gpop=160  wpop=336
[ZD] h=29 r=35 i=64 IR_ASSIGN K=0 zout=512 gpop=288  wpop=0
[ZD] h=65 r=7  i=72 IR_ASSIGN K=0 zout=400 gpop=384  wpop=400
[ZD] h=73 r=3  i=76 IR_ASSIGN K=0 zout=48  gpop=-48  wpop=48    <- NEGATIVE, itself suspicious
[ZD] h=77 r=2  i=79 IR_CALL   K=16 zout=48 gpop=48   wpop=32
```

- `SCRIP_ZD_SKIP=<n>` tried individually for all 5 (28, 64, 72, 76, 79): **every one still crashes
  rc=139.** Not bubble's "one node, skip it, done" shape — either a multi-node interaction, or several
  independent defect instances co-occurring in one program, not yet distinguished.
- `SCRIP_ZD=0` (disable zd_plan wholesale): **PASS, rc=0, output `1899` byte-matches `.ref` exactly.**
  Confirms zd_plan is the right subsystem, at least as the proximate cause — does not by itself prove
  the SAME mechanism as bubble (back-edge join-depth mismatch) rather than a different zd_plan defect
  that happens to also live here.
- The **negative** `gpop=-48` at node 76 was not chased further this session — worth independent
  attention regardless of whether it's this bug or a different one; a negative pop is arithmetically
  suspicious on its own.
- `sieve` is also the row's own **original** witness from an earlier hq_P pass (see the row's own
  SUPERSEDED-NEXT history) that was demoted as "unconfirmed" specifically because sieve stopped failing
  before it could be tested. It has evidently started again. Whether this is the identical mechanism
  recurring or a second one was not determined here.

## 4. Why I stopped here

This row's own DONE-WHEN grades all 9 kernels, including `sieve` — its current failure is squarely in
scope, not a tangential discovery. But `sieve`'s mechanism is NOT yet characterized to bubble's depth
(one exact node, one exact predecessor-depth mismatch, gdb-measured). Attempting a `zd_plan` cure now
would only be scoped to bubble's single-node shape and could easily leave sieve red, or — given this
function's documented history of two prior "necessary but insufficient" fixes from experienced sessions
— risk a regression while only partially informed. The row's own standing authorization note already
budgets for `zd_plan` being a shared node (SNOBOL4/Icon/Prolog) needing the full verdict set; adding an
uncharacterized second failure mode raises that bar further, not lowers it.

## 5. State

- Trees: SCRIP `882ac55b`+, corpus current as pulled this session, `.github` current. `make pristine`,
  `RT_OPT=-O0`.
- No code touched, `git status --short` clean across all three repos throughout (checked directly).

## Next actor

1. Update this row's own working picture: failing set is `{bubble, sieve}`, not `{bubble, quick}`.
2. `pascal-quick-m4-wrong-checksum-crash-masked` is now genuinely gradeable — pick it up separately.
3. `sieve` needs its own gdb-level trace (mirroring hq_P's bubble methodology: break at the loop
   join(s), watch RSP across iterations, isolate which of the 5 candidate nodes — or which combination —
   is the actual join-depth-disagreement site) before any cure attempt covering both kernels is safe.
4. Re-verify the grid fresh regardless of this entry — HEAD moves fast on this repo, as every session on
   this row has found.
