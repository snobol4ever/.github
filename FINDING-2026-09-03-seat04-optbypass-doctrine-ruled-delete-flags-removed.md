# FINDING 2026-09-03 seat04 — Optbypass doctrine question RULED (delete) and implemented: SCRIP_OPT/SCRIP_ZD are gone, not merely retired

**Row:** `optimizer-off-path-segvs-so-the-emergency-bypass-is-not-a-correct-path` (rank 1, picked up via `next`) · **Mode:** FLEET-16
**Trees:** SCRIP (this session's deletion, pending push) · .github (this FINDING)
**Class:** a standing cross-cutting doctrine question, blocking three prior seats (seat10, hq_B, seat06), each of whom independently measured the same unchanged result and released the row back to the queue rather than decide it themselves.

## Summary

`SCRIP_OPT=0`/`SCRIP_ZD=0` (the "emergency optimizer bypass") had been measured, over several sessions, to SIGSEGV or give wrong output on 11.6%–18.4% of the graded SNOBOL4 corpus — not a safe-but-slow fallback, a broken one, from an architectural cause (a fixed-offset depth-tracking convention that cannot represent a node reachable at two different runtime depths; hq_C's structural diagnosis). Lon's 2026-08-30 ruling ("make the convention safe") was implemented (`f9a90958`) and landed, but measured afterward to move neither bypass arm's regression rate at all (OPT0 11.49%→11.59%, ZD0 18.32%→18.42% — both up, not down). Three fleet seats independently re-verified this exact unchanged state across today's session and released the row each time, each noting explicitly that curing the arms (site-by-site patching) was foreclosed by Lon's own prior ruling, and deleting the flags was not a fleet seat's call to make — this had become a pure doctrine question sitting on the queue, unowned, with ceo's DELETE recommendation on file since CEO-156 and no ruling from Lon.

**This session, asked Lon directly** (this session has a live channel to Lon that routine fleet dispatch does not) rather than re-measuring an unchanged result a fourth time. **Lon ruled: delete the flags.**

## What was deleted

Per the ζ-storage flag precedent (`--zeta-storage=`/`SCRIP_ZETA_STORAGE` — "the flags are GONE, not merely retired"), the `getenv()` calls that gave these two env vars their bypass effect are removed from `src/`, not merely neutralized behind a dead branch:

- `src/optimizer/optimizer.c`: `optimizer_run()` no longer reads `SCRIP_OPT` at all — the early `if (e && *e=='0') return;` (which skipped every optimization pass: const-fold, copy-prop, pattern-fold, dead-pure, branch-chain, dead-goto) is gone. The optimizer runs unconditionally, matching what CLAUDE.md already claimed ("always on").
- `src/emitter/emit.cpp`: `zd_plan()` no longer reads `SCRIP_ZD` — the `_zd` variable and its `if (!_zd || n<=0) return;` early-exit are gone (kept the `n<=0` guard, an unrelated legitimate safety check). The depth-tracking planner runs unconditionally.
- Untouched, deliberately: the *other*, narrower `SCRIP_OPT_*` sub-flags (`SCRIP_OPT_NULLCAT`, `SCRIP_OPT_TRACE`, `SCRIP_OPT_BINIMM`, `SCRIP_OPT_STATS`, `SCRIP_OPT_CMPINT`) and the `SCRIP_ZD_*` diagnostic sub-flags (`SCRIP_ZD_DIAG`, `SCRIP_ZD_ONLY`, `SCRIP_ZD_SKIP`, `SCRIP_ZD_TESTFAM`, `SCRIP_ZD_OMEGA_HEAD`, `SCRIP_ZD_BACKEDGE`, `SCRIP_ZD_VALDIAMOND`, `SCRIP_ZDLOCAL`). These are per-pass debugging knobs, not the broad on/off bypass this row and Lon's ruling were about — a different mechanism, out of scope, not measured broken.
- `Makefile`: `test_gate_optbypass_watermark.sh` removed from `make test`'s recipe — it gated a bypass that no longer exists.
- `scripts/test_gate_optbypass_watermark.sh` and `scripts/util_census_optimizer_bypass.py` left on disk (not deleted) — historical/reference value documenting the investigation; no longer wired into anything that runs automatically.

## Verification

`python3 scripts/util_census_optimizer_bypass.py --only array_defer_indirect_replace_branch_1` (the row's own witness, previously `default PASS | SCRIP_OPT CRASH rc=-11 | SCRIP_ZD CRASH rc=-11` since the row was minted): now `default PASS rc=0 | SCRIP_OPT PASS rc=0 | SCRIP_ZD PASS rc=0` — all three arms identical, confirming the flags are genuinely inert, not just less-broken. Full `make test` (SNOBOL4 board, all gates) and the Icon watermark run this session since this touches the shared optimizer pipeline reachable from every language — see the task file's LEDGER for the exact numbers.

## Why this was asked rather than decided

RULES.md's own standing rule (§ THE PROLOG REBUILD GATE and elsewhere) reserves architecture/doctrine calls with fleet-wide reach for Lon, and this row's own history is the textbook case: three separate seats over two days each did the diligence (re-measure, confirm nothing changed, recognize it's not theirs to decide) and correctly declined to rule on cure-vs-delete themselves. Nothing new needed measuring; what was missing was Lon's answer, and this session could get it directly.
