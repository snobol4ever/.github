# FINDING: sweep-free-rows-are-real, pass 18 (seat06, 2026-08-27)

## Headline
STEP 18's own gate condition ("do not resume until FLEET ladders back past 8 or an HQ dispatches directly") was UNMET at pick time (MODE read exactly FLEET-8) — released unworked once, matching the 6 prior releases citing the same condition. Re-picked minutes later after Lon declared FLEET-12 live, which satisfies the condition. Ran STEP 0 (gate): gross churn 9 ≥ threshold 4 → opened a pass. **0 defects, 0 corrections, 5 NEW rows verified LIVE, 3 GONE rows verified correctly claimed** (not lost). Two more rows the gate had reported (`perf-roman-8x`, `unload-m3-m4-divergence`) were independently verified live by direct execution, then raced free→claimed by other seats before the baseline write — correctly excluded, not treated as corrections. True-free 141 → 141 (net 0, but real churn: −3/+5 classified, then 2 more races folded in at round-trip time, −2/+0).

## Method
Unchanged from passes 5–17: pulled all three repos fresh (SCRIP `7a2a9d19`, corpus `67685120`, `.github` `82d6722f`, each repo's own hash), ran `bash SCRIP/scripts/sweep_free_rows_gate.sh` (STEP 0), classified the reported delta by direct execution/citation (not brief-reading, not gate-label-trusting), rewrote `SWEEP-CLASSIFIED.tsv`, round-trip-verified twice (once caught 2 more live races, folded in before the final write; the write itself then verified byte-identical to a truly fresh regeneration).

## STEP 18's own gate (fleet-size condition)
- First pick (MODE=FLEET-8): released unworked, LEDGER entry recorded, citing the same reasoning as seat04's 13:08Z release immediately prior.
- Lon declared FLEET-12 live minutes later (`MODE` file: *"Let's go to mode FLEET-12."*, up from FLEET-8 after the banner-pristine fix landed and load fell). Re-picked; condition now satisfied.

## Classification detail

**GONE (3), all verified correctly claimed via `claims/`, none lost:**
- `corpus-suites-consolidation` — seat08, RUNNING.
- `perf-nv-set-fn-o0-overhead` — seat01, bare claim (no RUNNING marker yet — the same less-common manual-claim shape passes 6/11 already named as legitimate).
- `prolog-unify-var-compound-segv` — seat04, bare claim (same shape).

**NEW (5), all verified LIVE by direct execution/citation, not brief-reading:**
- `goal-consolidate-{pascal,raku,rebus,snocone}` — four `ceo` mints (Lon's in-chat order, GOAL-CEO.md CEO-30, "one GOAL file per language"). Census claims (1/5/3/11 `GOAL-*LANG*.md` files respectively) verified **exact**, including every individual filename, by direct `ls` against the live `.github` tree at fresh HEAD — no drift from any of the four task files' own LEDGER mint records.
- `prolog-multiclause-fail-backtrack-segv` — mechanism claim reproduced exactly: built `scrip` fresh at HEAD, ran the task file's own `DONE-WHEN` witness (`fact(a). fact(b). fact(c). main :- fact(X), write(X), nl, fail ; true.`) → **rc=139, SIGSEGV**, matching the brief precisely (not a variant, not already fixed).

**Verified LIVE, then raced away before the baseline write — correctly excluded, recorded here for the next pass's context, not corrections:**
- `perf-roman-8x` — the standing perf umbrella row (same shape as the closed `perf-tables-strings-runtime-bucket`/`perf-string-runtime`), reappearing after seat11's FLEET-8-standdown release. All 3 cross-referenced child rows (`perf-nv-set-fn-o0-overhead`, `perf-nv-set-capture-pump`, `perf-onedend-dcap-ceremony`) confirmed to exist as real task files. Claimed by seat01 (RUNNING) between the gate snapshot and classification.
- `unload-m3-m4-divergence` — reproduced the exact m3/m4 divergence table from its own task file, byte-for-byte: m3 → `10`/`10`/`unreachable` (rc=0), m4 → `10`/`unreachable` (rc=0), confirmed still disagreeing (row correctly stays open). Claimed by seat11 (RUNNING) between classification and the baseline write — caught by the mandatory round-trip check (see below), not missed.

**Round-trip catch (mandatory per pass 14's precedent):** re-ran the fresh-vs-written diff immediately before committing the baseline and caught 2 more live races that happened during classification itself: `diag-regs-telemetry-can-lie` (→ seat12 RUNNING) and `gimpel-suite-triage` (→ seat10 RUNNING). Both verified as genuine claims (not corruption), folded in before the write rather than left stale. Final write then re-verified byte-identical to a third, independent fresh regeneration.

## Sanity checks
- 0 duplicate QUEUE.tsv topics.
- 88 orphaned-DONE claims (was 82 at pass 17 — proportional growth, not chased, same standing note every pass has carried since pass 4).
- Gate re-run against the freshly-written baseline: gross churn 0 → rc=1, confirms a clean write.

## Fleet-velocity note
This pass raced 4 separate times in ~15 minutes of wall-clock classification work (`perf-roman-8x`, `unload-m3-m4-divergence`, `diag-regs-telemetry-can-lie`, `gimpel-suite-triage`, all free→claimed) — the highest race count of any single pass on record, coinciding with the FLEET-8→FLEET-12 expansion's first minutes (same pattern pass 12 flagged for FLEET-4→FLEET-12, and pass 13/14 for FLEET-8's own transitions). The round-trip discipline pass 14 made mandatory is exactly why none of these landed as stale data. No process change proposed; the existing method already absorbs this correctly.

## Baseline
`SWEEP-CLASSIFIED.tsv` rewritten for pass 19 at SCRIP `7a2a9d19` / corpus `67685120` / `.github` `82d6722f`, 141 topics, round-trip verified clean (churn 0) against an independent fresh regeneration.
