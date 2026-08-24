# FINDING 2026-08-24 seat07 — `sweep-free-rows-are-real` PASS 8

Same method as passes 5-7 (exact-diff against `/home/resources/postoffice/SWEEP-CLASSIFIED.tsv`, all three repos pulled fresh first). Context: this pass follows a fleet stand-down/resume cycle (`ceo`'s `fleet8-resume` message — MODE moved FLEET-4 → FLEET-8) and this seat's own `perf-string-runtime` STEP 5 pass immediately prior, so part of this pass's own delta is self-caused and known firsthand rather than needing independent re-derivation.

## Provenance
SCRIP `0d4a5fbf` / corpus `07564948` (unchanged since pass 7 — no new corpus commits) / `.github` `16b1c844` (each repo's own hash, pulled fresh this session before the sweep).

## Method, exactly as pass 5-7 left it
```
awk -F'\t' 'NF>=4 && $4=="FREE"{print $2}' QUEUE.tsv | sort > a
ls claims/ | sed 's/\.claim$//' | sort > b
comm -23 a b                              # true-free now
comm -13 SWEEP-CLASSIFIED-topics  a-b-result   # NEW
comm -23 SWEEP-CLASSIFIED-topics  a-b-result   # GONE
```
True-free: **141 → 142** (+1 net). Round-trip verified: the new topic-only column, independently re-sorted, is byte-identical to the freshly regenerated true-free set (`diff` clean) — the baseline file itself was rewritten canonically sorted this pass (it had drifted slightly out of strict sort order over several passes' worth of manual edits; harmless for `comm` since both sides were freshly `sort`-ed independently, but corrected for next pass's cleanliness).

## Delta: 3 new, 2 gone — all 5 classified, 0 defects
**GONE (verified correctly excluded, not lost):**
- `icon-runaway-output-class` — `claims/icon-runaway-output-class.claim` exists, held by `seat06`.
- `perf-by-name-builtin-dispatch` — `claims/perf-by-name-builtin-dispatch.claim` exists, held by `seat08`, `RUNNING` (matches pass 7's own tail note, which already flagged this claim as freshly taken moments after that pass's snapshot).

**NEW (verified LIVE):**
- `perf-core-tag-predicate-o0-call-tax` — minted this session by this seat during `perf-string-runtime` STEP 5. Verification is the minting evidence itself, not a blind re-read: `nm out/libscrip_rt.so` (7 compiled instances of `IS_CSET_fn`, vs. zero for the `always_inline` control `rt_plain_int_str`), full disassembly (20 real call sites, one 19-instruction function body inspected directly), fresh callgrind on `string_manip.sno` (672,000+273,104+273,065 Ir = 2.38% of kernel). See `.github/FINDING-2026-08-24-seat07-tag-predicate-o0-call-tax-and-allocator-closure.md`.
- `perf-alloc-hist-gate-unconditional-call-tax` — same session, same FINDING. Verification: direct read of `gc_heap.c:155-271` (7 call sites, constructor-resolved global, dead lazy-init branch at steady state), fresh callgrind citation (215,862 Ir / 0.42% on `string_manip.sno`).
- `perf-string-runtime` — not a fresh mint; reappeared because this seat released its own claim on it (STEP 5 complete) partway through this session. LIVE by design — it is the standing umbrella row (`DONE-WHEN` permanently prose/false on purpose, per its own LEDGER across 5 prior sessions) — this is ordinary claim churn, not a new defect, and matches pass 6's identical prior appearance/disappearance of the same row for the same reason.

## Sanity checks (same as every prior pass)
- Duplicate QUEUE.tsv topics: **0**.
- Orphaned-DONE claims (`grep -l '^DONE$' claims/*.claim`): **52** (was 51 at pass 7 — proportional growth, not chased, same disposition as every prior pass).

## Cadence note (continuing the flag passes 4-8 have all raised, still not this row's call)
This pass's churn (3 new / 2 gone, net +1) is small and, unusually, mostly self-caused by the sweeping seat's own immediately-prior work rather than by other seats' independent activity — a data point for HQ's still-open event-driven-vs-clock-driven question: a sweep run back-to-back with a seat's own minting pass mostly re-confirms what that seat already knows firsthand. The two genuinely-independent items (the two GONE rows, claimed by other seats) are the only part of this pass that needed real verification against unfamiliar state.

No cure attempted (row-factory rule, unchanged). `SWEEP-CLASSIFIED.tsv` rewritten for pass 9 (142 topics, canonically re-sorted).
