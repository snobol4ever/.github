# FINDING 2026-08-24 seat10 — `sweep-free-rows-are-real` PASS 10

Same method as passes 5-9 (exact-diff against `/home/resources/postoffice/SWEEP-CLASSIFIED.tsv`, all three repos pulled fresh first — this session's pull was fast-forward-only on all three, no conflicts).

## Provenance
SCRIP `be376a2f5` / corpus `c294d7c1e` / `.github` `fa2aff43c` — each repo's own hash, pulled fresh this session before the sweep (all three were behind origin at session start per `handoff_status.sh`; resolved with plain `git pull --rebase`, all fast-forwards).

## Method, exactly as pass 5-9 left it
```
awk -F'\t' 'NF>=4 && $4=="FREE"{print $2}' QUEUE.tsv | sort > a
ls claims/ | sed 's/\.claim$//' | sort > b
comm -23 a b                              # true-free now
comm -23 true-free-now SWEEP-CLASSIFIED-topics   # NEW
comm -13 true-free-now SWEEP-CLASSIFIED-topics   # GONE
```
One tooling snag caught and fixed before trusting the diff: the baseline file's literal `TOPIC\tVERDICT` header line (not `#`-prefixed, unlike every other header line) leaked into the first extraction attempt and printed as a phantom GONE row. Excluded explicitly on the second pass; round-trip-verified clean afterward (see below).

True-free: **142 → 145** (net **+3**, gross churn **11** — 7 new / 4 gone, the largest gross churn of any pass since pass 6's 6/3).

## Delta: 7 new, 4 gone, net +3 — all 11 classified, 0 defects

**GONE (verified correctly claimed, not lost — checked `claims/<topic>.claim` directly for all 4):**
- `audit-rtx29-icon-table-int-chain-walk-post-s262` — held by `seat08`, `RUNNING`.
- `corpus-suites-consolidation` — held by `seat07`, `RUNNING`.
- `icon-corpus-semicolonize` — held by `seat02`, `RUNNING`.
- `perf-dispatch-callsite-cache` — held by `seat05`, `RUNNING`.

All 4 also independently cross-referenced against a live fleet board snapshot (`s4e_msg.sh board`) taken this session — 3 of the 4 (all but `icon-corpus-semicolonize`) appeared verbatim as that seat's current-row status, corroborating the claim files without relying on the claim files alone.

**NEW — 4 fresh, unstarted mints (verified against source, not trusted from the task file alone):**
- `beauty-comment-bug-witness`, `pascal-restore-prezeta`, `raku-restore-prezeta`, `snocone-restore-prezeta` — all four minted by hq_C 2026-08-24 s272 off ceo's `GOAL-CEO.md` CEO-20 scope extension (Lon, verbatim in substance: *"extend scope to Snocone, Raku, and Pascal — at least get them to where they were before the huge month-long ZETA development phase"*, Rebus riding on the Snocone row). Verified two ways: (1) every watermark number each task file cites (Raku 719/0 vs today 705/19; Pascal 152/152 vs today 98/153 m3 · 86/153 m4; Snocone "excavate, no candidate" vs today 4/5 smoke · 6/8 crosscheck; Rebus 4/4) matches `GOAL-CEO.md`'s own CEO-20 text verbatim, no drift; (2) every script each task file's `DONE-WHEN` names (`test_gate_pascal_m3.sh`, `test_gate_pascal_m4.sh`, `test_smoke_raku.sh`, `test_crosscheck_snocone.sh`, `test_smoke_rebus.sh`, `test_corpus_snobol4.sh`) exists at the cited path. `beauty-comment-bug-witness`'s own claimed pre-state (`corpus/probe/beauty_comment/` not yet created, since STEP 1 is unstarted) was independently confirmed: the directory does not exist. All four `## NEXT` blocks correctly point at their own STEP 1 with no LEDGER entries yet — genuinely untouched, not stale.

**NEW — 3 reappeared rows (claim churn on rows with real open work, not new defects):**
- `icon-runaway-output-class` — claimed+released twice this cycle (seat06 landed the root-cause fix, seat07 independently reconfirmed it and left the row blocked on a sibling claim + an open HQ question). Fix commit `27f366d2` independently confirmed present in SCRIP history (`git log --oneline -1 27f366d2` resolves, message matches: "templates: bb_iterate's every-generator exhaustion check compared full rax against bare DT_FAIL, never matching"). Genuinely LIVE — real remaining work (deal.icn's own SIGSEGV, tracked on the sibling row `icon-deal-runaway-output`; an unanswered QA question to hq_C about whether this row's `DONE-WHEN` should decouple from deal.icn).
- `perf-by-name-builtin-dispatch` — reappeared after seat05's release (its own STEP 2 is unblocked and in progress on the split child rows). All 4 child rows it names (`perf-dispatch-callsite-cache`, `perf-dispatch-gc-safepoint-necessity`, `perf-core-tag-predicate-o0-call-tax`, `perf-alloc-hist-gate-unconditional-call-tax`) independently confirmed present in `QUEUE.tsv`, not orphaned references.
- `perf-string-runtime` — the standing umbrella row, reappeared after seat04's STEP 6 release. Same disposition noted in passes 6/8/9: ordinary claim churn on a row that is LIVE by design (`DONE-WHEN` permanently prose). Its own `## NEXT` still names a live open thread (`IS_CSET_fn`'s two sibling symbols, further kernel resurveys) rather than trailing off.

## Sanity checks (same as every prior pass)
- Duplicate QUEUE.tsv topics: **0**.
- Orphaned-DONE claims (`grep -l "^DONE" claims/*.claim`): **56** (was 54 at pass 9 — proportional growth, not chased, same disposition as every prior pass).

## Round-trip verification
After rewriting `SWEEP-CLASSIFIED.tsv` (142 → 145 topics, 7 removed+re-added... i.e. 4 removed / 7 added, canonically sorted, pass-10 header block appended above the existing pass 4-9 history rather than replacing it), diffed its data section against a fresh independent regeneration of the true-free set: **byte-identical**, same check pass 9 ran.

## Cadence note (continuing the flag passes 4-9 have all raised, still not this row's call)
This is the largest gross churn (11) since pass 6 (9), driven mostly by one HQ-level event — ceo's s272 scope extension minting 4 well-formed rows in one dispatch — plus ordinary claim/release cycling on 3 already-known standing rows. Zero of the 7 NEW rows were independent grassroots discovery; 4 trace to one HQ decision and 3 are recurring appearances of rows already fully characterized in prior passes' FINDINGs. This is a third independent data point (after pass 8's and pass 9's) that a meaningful share of this queue's churn is structured (HQ dispatches, row-factory splits, claim/release cycling) rather than novel discovery — another point toward event-driven cadence over clock-driven, though as before, not this row's call to make.

No cure attempted (row-factory rule, unchanged — zero edits to any `.c`/`.h`/`.S`/`.cpp`/task-file source this session beyond `SWEEP-CLASSIFIED.tsv` itself, which is this row's own deliverable ledger, not project source). `SWEEP-CLASSIFIED.tsv` rewritten for pass 11 (145 topics, canonically sorted).
