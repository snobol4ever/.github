# FINDING 2026-08-24 seat02 — `sweep-free-rows-are-real` PASS 9

Same method as passes 5-8 (exact-diff against `/home/resources/postoffice/SWEEP-CLASSIFIED.tsv`, all three repos pulled fresh first).

## Provenance
SCRIP `57d507d9` (unchanged since pass 8) / corpus `63d60ae1` (2 files updated, `library/strings.sc` + `snocone/corpus/sc4_control.sc`) / `.github` `9e75192b` (unchanged since pass 8) — each repo's own hash, pulled fresh this session before the sweep.

## Method, exactly as pass 5-8 left it
```
awk -F'\t' 'NF>=4 && $4=="FREE"{print $2}' QUEUE.tsv | sort > a
ls claims/ | sed 's/\.claim$//' | sort > b
comm -23 a b                              # true-free now
comm -23 true-free-now SWEEP-CLASSIFIED-topics   # NEW
comm -13 true-free-now SWEEP-CLASSIFIED-topics   # GONE
```
True-free: **142 → 143 → 142** (see race note below; net **0** against the pass-8 baseline once corrected).

## Live-race catch: first-pass `claims/` listing was already stale by the time it was read
The first `ls claims/` snapshot (taken immediately after the `QUEUE.tsv` snapshot) put true-free at 143 with `icon-runaway-output-class` reading as a fresh NEW mint. Re-listing `claims/` moments later (prompted by that topic's suspicious near-duplicate name against a GONE row, `icon-deal-runaway-output`) showed `icon-runaway-output-class.claim` now present, holder `seat07`, `RUNNING` — the claim was taken by another seat in the few seconds between this pass's two directory reads, not a `sed`/`comm` bug (confirmed by re-testing the `sed 's/\.claim$//'` pattern in isolation — it strips the suffix correctly). This is the 16-seat fleet's normal live churn (documented before for `QUEUE.tsv` itself, e.g. pass 1's 105→120 mid-session growth) showing up in `claims/` specifically for the first time in this task's history. **Method note for pass 10 and beyond**: when a NEW topic's name closely echoes a GONE topic's name in the same pass, re-check `claims/` for that exact topic before classifying it as a mint — it may just be a claim you read one beat too early. Re-snapshotting both `a` and `b` together (not `a` once and re-diffing `b` alone) is the safe fix and is what this pass did.

## Delta (corrected): 2 new, 2 gone, net 0 — all 4 classified, 0 defects
**GONE (verified correctly excluded, not lost):**
- `icon-deal-runaway-output` — `claims/icon-deal-runaway-output.claim` exists, held by `seat06`, `RUNNING`.
- `perf-string-runtime` — `claims/perf-string-runtime.claim` exists, held by `seat04`, `RUNNING`. Same standing-umbrella row noted appearing/disappearing in passes 6 and 8 for the same reason (claim/unclaim churn, not a defect).

**NEW (verified LIVE by direct code citation check, not a blind re-read):**
- `perf-dispatch-callsite-cache` — minted by seat08 same session as pass 8's two self-attested mints, split off `perf-by-name-builtin-dispatch`. Checked both citations directly at fresh HEAD: `g_dtax_bid[1025]` array exists at `src/runtime/by_name_dispatch.c:5171` (referenced again at line 5289 exactly as the task file describes — a `_bid`-indexed fast path guarded by `dtax_off()`). Row is correctly gated behind a blocking ask (no-new-globals rule) and not itself actionable without Lon's ruling — that gating is proof of correct row-factory discipline, not a defect.
- `perf-dispatch-gc-safepoint-necessity` — minted same session, same split. Checked all three citations directly at fresh HEAD: `rt_gc_point_arr_c` at `src/runtime/rt/gc_heap.c:319` (exact — pending/heap-top check then early-return, matches description); the asm veneer at `src/runtime/rt/rt_asm_helpers.S:100-122` (exact — six `pushq`/`popq` pairs for rbx/rbp/r12-r15 around the `_c` call, matches "parks all six callee-saved registers" claim word-for-word); the call site at `src/runtime/by_name_dispatch.c:4656` (exact — `rt_gc_point_arr(args, nargs, (const char **)0);` is that literal line). Note: the task file's own path for `by_name_dispatch.c` omits the `src/runtime/` prefix and my first lookup guessed the wrong directory (`src/runtime/rt/`, where it does not live) — a citation-format gap worth flagging (paths in this row's LEDGER are file-basename-only, unlike most other rows' full-path citations) but not a wrong citation, so not corrected in place.

## Sanity checks (same as every prior pass)
- Duplicate QUEUE.tsv topics: **0**.
- Orphaned-DONE claims (`grep -l '^DONE$' claims/*.claim`): **54** (was 52 at pass 8 — proportional growth, not chased, same disposition as every prior pass).

## Cadence note (continuing the flag passes 4-8 have all raised, still not this row's call)
Net delta 0 for the second time in 9 passes (pass 5 was the other), but — as pass 5 itself warned — a stable count is not evidence of no change: gross churn this pass was 4 (2 new/2 gone), continuing the 4-9 band pass 8 identified across the last several passes, now at its low edge. Both NEW rows this pass were mints from the *same* seat08 session that produced pass 8's two self-attested NEW rows — i.e. four of the last seven NEW rows across passes 8-9 trace to one seat's one working session on one parent row (`perf-by-name-builtin-dispatch`). That is a second independent data point (after pass 8's own note) that a meaningful share of this queue's growth is currently row-factory output from active cure sessions splitting their own parent rows, not fresh discovery — arguably a point in favor of event-driven cadence (sweep after a known minting burst) over clock-driven, since a burst from one seat's one session is exactly what a clock-driven sweep is equally likely to catch mid-burst (this pass) or miss entirely (between bursts).

No cure attempted (row-factory rule, unchanged). `SWEEP-CLASSIFIED.tsv` rewritten for pass 10 (142 topics, canonically sorted).
