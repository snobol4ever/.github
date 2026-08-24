# FINDING 2026-08-24 seat15 — `sweep-free-rows-are-real` PASS 11

Same method as passes 5-10 (exact-diff against `/home/resources/postoffice/SWEEP-CLASSIFIED.tsv`, all three repos pulled fresh first). Re-snapshotted `QUEUE.tsv`+`claims/` together a second time before classifying (pass 9's race lesson) and re-verified the round-trip a second time after rewriting the baseline (pass 10's method, applied again below) — both came back clean.

## Provenance
SCRIP `ef18421e` / corpus `89eda383c` / `.github` `d1347490` — each repo's own hash, pulled fresh this session via plain fast-forward `git pull --rebase` (all three had substantial drift since the last session's HEAD, no conflicts). SCRIP was also rebuilt (`make`, incremental, RT_OPT confirmed `-O0`) before trusting any direct repro — the checked-in `scrip` binary predated yesterday's pull.

## Method, exactly as pass 5-10 left it
```
awk -F'\t' 'NF>=4 && $4=="FREE"{print $2}' QUEUE.tsv | sort > a
ls claims/ | sed 's/\.claim$//' | sort > b
comm -23 a b                              # true-free now
comm -23 true-free-now SWEEP-CLASSIFIED-topics   # NEW
comm -13 true-free-now SWEEP-CLASSIFIED-topics   # GONE (comm -23 the other direction)
```
No tooling snags this pass — pass 10's header-line exclusion (`$1!="TOPIC"`) held up cleanly.

True-free: **145 → 143** (net **-2**, gross churn **4** — 1 new / 3 gone, tied with pass 9 for the smallest gross churn on record). ⚠️ First draft of this FINDING mis-arithmetic'd this as "145 → 142 / net -3" — caught by the round-trip verification below disagreeing with the hand count (143 vs 142) before it was committed anywhere. Corrected here and in `SWEEP-CLASSIFIED.tsv`'s own header comment; flagging the near-miss explicitly since this exact class of error (trusting a computed count without re-deriving it) is the row's own founding lesson.

## Delta: 1 new, 3 gone, net -2 — all 4 classified, 0 defects

**GONE (verified correctly claimed, not lost — checked `claims/<topic>.claim` directly for all 3):**
- `perf-string-runtime` — held by `seat12`, `RUNNING`. Cross-checked against a live `BOARD.md` snapshot: seat12's most recent banner line reads `row OPEN perf-string-runtime` — matches.
- `banner-attributes-wrong-row-on-unclaim` — held by `seat04` (single-line claim, owner only, no `RUNNING` marker — a manual `claim`, not yet promoted by `next`). Corroborated by reading the task file's own LEDGER tail: real in-progress work recorded this session (a RED/GREEN gate-script rewrite with receipts), not a stray or stale claim.
- `handoff-status-three-state-push-check` — held by `seat04` (same single-line claim shape). Corroborated the same way: LEDGER shows a minted-then-worked row with a QA entry recording an independently-confirmed verdict this session.

Both `seat04` claims lack the `RUNNING` second line that `next`-dispatched claims carry (that marker is written by the picker's ASSIGNED→RUNNING promotion; a manual `claim <topic>` writes only the owner line). Neither is DONE. Per the row's own operational definition of true-free (state==FREE AND no claim file, LEDGER `[seat02·2026-08-23T20:58Z]`), presence of a non-DONE claim file — regardless of whether it carries an explicit RUNNING marker — is sufficient to correctly exclude a row; this is not a new class of claim, just a less common one, and both were corroborated past the claim file alone.

**NEW — 1 fresh mint, verified LIVE by direct repro (not by reading the brief):**
- `snocone-returns-codegen` — minted by `hq_C` 2026-08-24 s272 per CEO-21, Lon's direct instruction ("get that bug in the queue"). Rank 1, top of the Snocone restoration tier, gates `beauty.sc` running beside `beauty.sno`. The brief cites three one-line witnesses; verified witness 1 directly against the fresh build: `function f(x) { f = 1; nreturn; } OUTPUT = f(0);` run under `./scrip` (mode 3, default) reproduces the exact cited failure verbatim — `bb_emit_end: 1 unresolved forward reference(s): site=256 label='RETURN'`, then aborts (rc=134, core dump). Also ran the same witness under `--compile` (mode 4): emission succeeds (rc=0) but the emitted asm's `NRETURN:` block ends in `jmp RETURN` where no `RETURN:` label is ever defined anywhere in the output — the same missing-port defect surfaces in both mediums, consistent with the brief's own Byrd-box framing (STEP 3: an unwired ω/γ return port) and with the ARCH invariant that m3 and m4 share one codegen path. Did not attempt witnesses 2/3 or any cure — row-factory rule; one clean exact-match repro of the row's central claim is enough for classification, and STEP 1/2/3 in the task's own `## NEXT` are for whoever picks up the cure.

## Sanity checks (same as every prior pass)
- Duplicate QUEUE.tsv topics: **0**.
- Orphaned-DONE claims (`grep -l "^DONE$" claims/*.claim`): **58** (was 56 at pass 10 — proportional growth, not chased, same disposition as every prior pass).

## Round-trip verification
After rewriting `SWEEP-CLASSIFIED.tsv` (145 → 143 topics: 3 removed, 1 added, canonically sorted, pass-11 header block appended above the existing pass 4-10 history rather than replacing it), diffed its data section against a fresh independent regeneration of the true-free set, snapshotted a second time (not reusing the snapshot the classification itself was based on): **byte-identical**. This second, independent snapshot is also what caught the -3/-2 arithmetic error above — the regeneration returned 143 lines against a hand-count that said 142, and the mismatch was chased down rather than overridden.

## Cadence note (continuing the flag passes 4-10 have all raised, still not this row's call)
Smallest gross churn tied with pass 9 (4, vs pass 10's 11). Of the 4 changed rows, 0 were independent grassroots discovery: 1 new row is a direct HQ/Lon dispatch (`snocone-returns-codegen`, CEO-21) and all 3 gone rows are ordinary claim/release cycling on rows already fully characterized in prior passes (`perf-string-runtime` — the standing umbrella, previously noted reappearing in passes 6/8/9/10 too; the other two are first-time claims on pass-4/INHERITED mints, not repeat churn). Consistent with the pattern passes 8-10 already flagged: a meaningful share of this queue's remaining churn is structural rather than novel discovery. Not this row's call to make.

No cure attempted (row-factory rule — zero edits to any `.c`/`.h`/`.S`/`.cpp`/task-file source this session beyond `SWEEP-CLASSIFIED.tsv` itself and this row's own task-file `## NEXT`/LEDGER). `SWEEP-CLASSIFIED.tsv` rewritten for pass 12 (143 topics, canonically sorted).
