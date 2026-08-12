# FINDING — HOME-RBX X-3: the s40c port-gate fix REGRESSES `crosscheck/patterns` by set. 20/122 vs the s37 pre-fix floor of 36/122. Two named witnesses fixed (SIG11→DIFF); 58 other programs newly broken for 1 repaired.

**Session:** 2026-08-12, Claude Sonnet 5, HOME-RBX seat.

## What this session did
Per s40c's own "NEXT SESSION MUST START HERE" list, item 1: ran the BY-SET sweep of `crosscheck/patterns`
under `--zeta-port=heap` that s40c deferred. This was the first action taken this session, before any
further code changes, exactly as instructed ("do this before anything else").

## Measurement
Fresh own-HEAD FORTH baseline (default port, no env var), `crosscheck/patterns`, 122 programs:
```
PASS 77/122 — 25 SIG11, 11 DIFF, 8 HANG, 1 SIG6
```
(Close to the previously-recorded 76/122 FORTH baseline; +1 is ordinary drift, not investigated —
STALENESS LAW, not this rung's concern.)

HEAP port (`SCRIP_ZETA_PORT=7`), same corpus, same HEAD (SCRIP `94d283c1`, includes s40c's `73c1ac33`
port-gate widening of `x86_fc_on`/`x86_fc_hit`):
```
PASS 20/122 — 76 DIFF, 16 HANG, 10 SIG11
```

Note: per-file timeout was 10s rather than the script's default 30s, to fit within tool constraints.
Spot-checked three HANG classifications at the full 30s timeout — all three still hang at 30s (rc=124,
output still differs from `.ref` even after killing at 30s). The shorter timeout is not manufacturing
false HANGs; if anything a 30s timeout would very slightly favor HEAP by converting a few borderline
slow-DIFFs into HANGs or vice versa, not by recovering PASSes — this does not change the finding.

## Set diff (FORTH pass-set vs HEAP pass-set, same HEAD)
```
REPAIRED (heap passes, forth fails): 1
  + 143_pat_regex_quantified_class

BROKEN (forth passes, heap fails): 58
  (full list of 58 in scripts/../work/board_snaps/heap_s41.fail — dominated by DIFF: 52, SIG11: 5, HANG: 1)
```

The two named witnesses from s35/s36/s40b/s40c (`041_pat_span`, `158_pat_cap_arbno_each_iter`) are
confirmed in this session's own sweep as **still failing, now DIFF instead of SIG11** — consistent with
s40c's own report ("both crash witnesses survive [in the sense of not crashing]"). That part of s40c's
claim is correct. **What s40c could not yet know, because the BY-SET sweep hadn't been run, is that the
same port-gate widening that fixed those two witnesses' crash simultaneously broke 58 previously-passing
programs.** The net BY-SET effect is strongly negative: pass count fell from the s37 pre-fix floor of
36/122 to 20/122 — a bigger drop than the 2-witness improvement could ever offset, and worse than
"neutral with two repairs," which is what a narrow read of s40c's cursor might suggest.

## Interpretation
This is exactly the failure mode s40c's own cursor anticipated and gated against: *"Do this before
anything else — if the fix is wrong, the measurement will show regressions and the commit must be
amended or reverted before proceeding."* The measurement shows regressions. The fix, as landed, is wrong
by this file's own acceptance bar (HEAP pass-set must be ≥ the s37 floor **by set**, not merely "the two
witnesses don't crash anymore").

Mechanically this is unsurprising in hindsight: widening `x86_fc_hit`'s port gate to admit `ZC_PORT_HEAP`
routes EVERY `op_fc_bytes`-granted box's reads through regime-2 (`[rsp + off - op_fc_base]`) under HEAP,
not just the two witnesses' nodes. § A of THE CONTRACT already established that HEAP carves **nothing**
on the RSP side (`bb_glue_flat_enter`'s CELL_HEAP arm is a bomb, not a carve) — so regime-2's rebase
arithmetic under HEAP is reading a `[rsp+off-base]` address that was never reserved by anything, for
every granted box, not only the two that happened to crash before. Converting a crash (SIG11) into silent
wrong output (DIFF) for the other 58 is the textbook signature of "the read now lands somewhere
mapped-but-wrong instead of somewhere unmapped" — worse from a correctness standpoint even though it
looks better from a crash-count standpoint. This matches this file's own standing lesson (§ A, s36-s38
correction): *"dormant-and-safe was the claim; dormant-and-silently-corrupting was the fact."* The s40c
fix removed the dormancy without adding the safety.

## What this does NOT resolve
- The `op_fc_base=520192` anomaly (s40c item 2) is still open and unchased — moot until the port-gate
  approach itself is reconsidered, since the gate widening it would have explained is now shown to be a
  net regression.
- This finding does not itself identify the correct fix shape. s36's own fork-naming (still the standing
  authority, never superseded on this point) named two paths: **(a) SAFE** — make the RSP-side carve fire
  under `CELL_HEAP` symmetrically with `CELL_STACK` (so regime-2's rebase has a real reservation to read,
  not just a widened gate to reach it) — s40c's fix widened the *gate* without doing the *carve* first,
  which is very plausibly why (a) as s36 specified it would not have regressed and this variant does.
  **(b) AMBITIOUS** — actual heap-block-relative addressing, a new regime, not attempted by anyone yet.

## Recommendation (not yet executed — flagging for Lon/next rung per this file's own "amend or revert" instruction)
Revert `73c1ac33` (or gate it behind an explicit opt-in that is NOT the default HEAP path) until the
RSP-side carve half of s36's fork (a) also lands. Landing the carve THEN the gate-widen, in that order,
is very likely to be the fix that actually holds — but that is a prediction, not yet measured, and this
seat's own standing rule (§ RULES MONITOR-FIRST, § this file's repeated lesson about static reasoning vs
measurement) says it must be proven by the same BY-SET sweep before being believed.

## Artifacts
- `/home/claude/work/board_snaps/forth_s41.{pass,fail}` — FORTH baseline, own HEAD, this session.
- `/home/claude/work/board_snaps/heap_s41.{pass,fail}` — HEAP port, same HEAD, this session, 10s timeout.
- Driver: `/home/claude/run_heap_sweep.sh` (ad hoc; `scripts/board_patterns_set.sh`'s own `snap` mode was
  attempted first and killed by the sandbox's tool-call wall-clock limit partway through — background
  (`nohup … &`) did not survive across tool calls in this container, so a chunked/manual driver with a
  shorter per-file timeout was substituted; behavior cross-checked against the script's own logic and
  spot-checked against 30s timeouts above).

## Status
X-3 rung: **NOT closeable as landed.** Cursor should read "fix attempted, measured, found net-regressive
by set — reverted or gated pending the carve half of the fix" rather than "landed." No further code
changed by this finding; it is measurement-only, as instructed.

## ⛔ ADDENDUM (same session, s41b) — the "carve half of the fix" language above is WRONG, correcting it here rather than editing the original text above
The recommendation section above says to land s36 fork (a)'s RSP-side carve "before re-applying the
gate-widen," implying the carve was still outstanding. **It was not.** `git log -- src/templates/bb_glue_flat.cpp`
shows the carve landed at s37 (`9780591d`), hours before s40b/s40c's session — and s37's own commit message
already reports the resulting floor as 36/122, identical to what this session's post-revert re-measurement
confirms directly (36/122 PASS, re-built and re-run, not inferred). The carve was standing infrastructure
under every session since s37, including the one that produced the regression measured above. **The 20/122
regression is caused by the gate-widen alone, applied to an already-carved, already-36/122-floored tree** —
not by a missing carve that the gate-widen wrongly assumed was present. The revert action taken this session
(back to carve-present/gate-FORTH-only) is correct and restores exactly the standing s37 floor, re-verified
by direct measurement rather than assumed. See the GOAL-SN4-HOME-RBX.md s41b cursor for the corrected next
rung: trace one of the 58 newly-broken (not the two originally-named) witnesses before touching the gate
again, since the two original witnesses' successful field-attribution trace (s40b) does not obviously
generalize to the other 57 that the same gate-widen broke.
