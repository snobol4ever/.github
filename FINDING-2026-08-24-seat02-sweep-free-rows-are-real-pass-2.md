# FINDING — sweep-free-rows-are-real, pass 2: 134 true-free (was 89), 28 new rows classified, both STEP-2 loose ends resolved

**Session:** 2026-08-24 seat02, THE LOOP row `sweep-free-rows-are-real`, executing STEP 2 of the prior pass's own instructions (`.github/FINDING-2026-08-23-seat02-sweep-free-rows-are-real-89-classified.md`): re-run the cross-reference against current HEAD, chase the 2 named loose ends. Snapshot: SCRIP `69449f94`, corpus/`.github` `35b7d034` (fresh `git pull --rebase` all three).

## HEADLINE

- **True-free count now: 134** (state==FREE, no `claims/*.claim`), up from **89** at the 2026-08-23T20:57Z snapshot — growth continues to outpace consumption (+50% in about a day), exactly as the prior pass's caveat predicted.
- **28 of the 134 are new** since the prior snapshot (diffed against `QUEUE.tsv.bak.seat02-sweep-20260823T212807Z`, the prior pass's own pre-edit backup). 2 were self-minted by the prior pass (already known-good, not re-checked). 9 are other well-formed HQ mints (icon/process/correctness, read directly, all LIVE). **19 are a `conform-*` family from a systematic SNOBOL4 conformance-vs-oracle sweep — classified via 4 parallel read-only forks, cross-checked directly by this session on anything that looked off.**
- **Result: 19/19 `conform-*` rows are genuinely LIVE** (every defect independently reproduced against a fresh oracle-differential run) — but **4 needed a correction** the DONE-WHEN/brief itself couldn't surface, and one split into two rows. Verifying rather than trusting a green or a plausible-sounding claim caught all four.
- **Both STEP-2 loose ends from the prior pass resolved** (see dedicated sections below): the `kw-missing-4`/`conform-line-lastline-crash` overlap, and the `lib_gate.sh` CWD-sourcing bug's real fleet-wide scope.
- **One brand-new class-defect row minted** (`lib-gate-cd-order-silent-skip`), sized by direct measurement, not estimation.

## METHOD

1. Recomputed true-free the same way as pass 1: `QUEUE.tsv` state==FREE minus `claims/*.claim`, both freshly read (134 topics; separately confirmed the 43 claim files with no matching FREE row are all `DONE`-terminated and already correctly swept, not an anomaly).
2. Diffed against the prior pass's pre-edit snapshot backup to isolate genuinely new candidates rather than re-classifying rows the prior pass already resolved (28 topics).
3. Read the 9 non-`conform-*` new rows directly — all freshly minted by hq_C/hq_P s269, well-formed with real evidence, no fork needed. One (`icon-sweep-scratch-hardening`) turned out to have a DONE-WHEN targeting the wrong file (see below).
4. Batched the 19 `conform-*` rows into 4 parallel read-only forks (5/5/5/4): run each DONE-WHEN fresh, reproduce directly if it refuses, verdict + receipt required, no writes. This session performed all write-back centrally. On anything a fork flagged as off-narrative, this session independently re-verified directly before writing a permanent record — caught one case (`conform-setexit-noop`) where a broader cross-check against `GOAL-SNOBOL4-100.md` itself (not just the fork) was needed to get the framing right.

## THE 28 NEW ROWS

### Non-conform (9, read directly)
| topic | verdict | note |
|---|---|---|
| `icon-deal-runaway-output` | LIVE | real, well-formed (hq_P→hq_C s267, the s267 disk-full outage's correctness half). **Flagged overlap** with `icon-runaway-output-class` — both target `deal.icn`, minted independently one day apart without cross-referencing each other. Cross-reference note added to both, not merged (not identical scope: the class row also covers `jcon_record`/`jcon_substring`). |
| `icon-runaway-output-class` | LIVE | real, well-formed (hq_C s266, merges 3 witnesses incl. `deal.icn`). See overlap note above. |
| `icon-247-to-232-fifteen-program-gap` | LIVE | real, well-formed, hq_C s269, strong evidence (two independent baseline re-confirmations). |
| `icon-sweep-scratch-hardening` | **DONE-WHEN wrong-target — fixed in place** | DONE-WHEN checked `scripts/scorecard_icon.sh`, which has zero `mktemp`/`/tmp` references and was never the offending file. The row's own progress log shows the real class-defect work landed and gated elsewhere (`honest_icon_correctness.sh`, `honest_icon_bench.sh`, `test_monitor_3way_sync_step_auto.sh`, all fixed; `test_gate_scratch_is_bounded.sh` the resulting gate). Verified fresh this session: `GATE PASS(0)... examined 475`. Retargeted DONE-WHEN to the real gate; re-ranked 0→5 (danger neutralized+gated per the row's own repeated framing, remainder is hygiene: 23 bounded leakers need traps, cache eviction addition 6). Not retired — hygiene work genuinely remains. |
| `handoff-status-three-state-push-check` | LIVE | real, well-formed, hq_P s269, minted at CEO's instruction. |
| `sm-eval-subexpr-weak-abort-landmine` | LIVE | real, well-formed, hq_C s269, from an existing adversarial-verification FINDING. |
| `zd-wants-is-a-per-op-filter` | LIVE | real, well-formed, hq_C s269, explicitly sequenced after the CEO-11 strip (intentional, not a defect). |
| `perf-by-name-builtin-dispatch` | LIVE | self-minted by this row's own prior pass — already fully understood, no re-check needed. |
| `sweep-zero-length-refs` | LIVE | self-minted by this row's own prior pass — already fully understood, no re-check needed. |

### `conform-*` family (19, forked + directly cross-checked)

**15/19 confirmed LIVE exactly as briefed, no rewrite needed:** `conform-clear-exclusion-ignored`, `conform-collect-huge-not-failing`, `conform-copy-table-aliases`, `conform-dupl-pattern-overload-fails`, `conform-exit-savefile-unimplemented`, `conform-field-never-succeeds`, `conform-io-four-functions-unimplemented`, `conform-io-write-read-same-run-empty`, `conform-load-missing-error-validation`, `conform-output-1arg-noop`, `conform-rsort-sort-array-noop`, `conform-table-default-arg-ignored`, `conform-trace-stoptr-inert`, `conform-trim-tabs-not-stripped`, `conform-unload-noop`.

**4 needed a correction (all real, all still LIVE, all rewritten in place — not retired, not dead):**

| topic | what was wrong | fix |
|---|---|---|
| `conform-date-format-wrong-length` | DONE-WHEN reads **green right now** despite the defect being fully present (`SIZE(DATE())=19` confirmed fresh). The witness's SNOBOL4 pattern has no `RPOS(0)` anchor, so a fixed-width 17-char field pattern is satisfied by the first 17 characters of a 19-char value — it never validates total length. | Flagged prominently in GOAL with a ⛔⛔ banner + LEDGER entry so nobody retires this row on the false green; did not edit the witness `.sno` myself (that's this row's own cure, not bookkeeping). |
| `conform-dump-function-noop` | Brief claims "zero output... complete no-op." No longer true — DUMP now emits a `[DUMP start]`/`[DUMP end]` stub block (built-ins listed as `DT_DATA`, user vars as generic `STR()` placeholders, no `&KEYWORD` section). Defect still real, DONE-WHEN still correctly fails, but the fix target changed from "unimplemented" to "implemented wrong." | Rewrote GOAL/STEP1/STEP2 with current output captured verbatim; flagged that something changed DUMP's behavior since 2026-08-23 without this row being updated. |
| `conform-local-opsyn-m4-empty` | Bundled LOCAL + OPSYN on a "same symptom" hypothesis the row's own STEP 2 flagged as unconfirmed. `f13_local` matches (m3 correct, m4 silently empty). `f14_opsyn` does NOT — current behavior is `FATAL lower_snobol4 (GZ#5 subset)` in BOTH modes (m3 never reaches "prints 42"; m4 is EMITFAIL, not silent-drop). Confirmed independently twice (direct + fork) before acting. | Rescoped this row to LOCAL only; split OPSYN out to new row `conform-opsyn-operator-rebind-gz5-fatal`, cross-referenced to the existing `conform-unary-interrog-gz5-gap` (same GZ#5-subset family, different trigger construct). |
| `conform-setexit-noop` | GOAL claims SETEXIT's trap mechanism is a "complete no-op." **False** — `GOAL-SNOBOL4-100.md`'s own s249 record (2 days *older* than this row) landed the trap for undefined-function-call errors, independently re-confirmed still working (`se_trap_undef.sno` → `HANDLER`, byte-matches `.ref`). The real, narrower gap: undefined-*label*-transfer errors (error 38) specifically bypass the trap — a different, more primitive code path. | Rewrote GOAL to the precise narrower framing; flagged an unresolved ambiguity (whether `GOAL-SNOBOL4-100.md`'s standing "Lon prices SETEXIT+&ERRTYPE before code" note, written *before* s249's landing, still gates this narrower remainder or was satisfied/superseded) rather than guessing either way. |

**Net: 19/19 real, 0 dead, 1 new row minted from a split.** This is a strong hit rate for the family, but the 4 corrections all came from independent verification catching something a plausible-sounding fork report or a green DONE-WHEN would have missed — the discipline mattered even at a 100% LIVE base rate.

## LOOSE END (ii) RESOLVED — kw-missing-4 / conform-line-lastline-crash

Direct repro, fresh HEAD: `timeout 8 ./scrip --run corpus/probe/conformance/k14_stno_line.sno < /dev/null` →
```
stno=1
stno-next=2

** Error 342 in statement 0
   &constant read before its one-time assignment: &LINE
rc=1
```
This is precisely the Error 342 the prior pass's batch-H fork cited as `kw-missing-4`'s evidence that &LINE/&LASTLINE/&FILE/&LASTFILE are unimplemented — so `conform-line-lastline-crash`'s "truncated output + nonzero exit" symptom and `kw-missing-4`'s "Error 342" evidence are the same event seen two ways, not two defects. `conform-line-lastline-crash` has real witnesses and a computable DONE-WHEN; `kw-missing-4` did not. **Rescoped `kw-missing-4` to &FILE only** — the one keyword of the original four with no witness anywhere — and cross-linked both task files so neither effort duplicates the other. Verified this rescoping doesn't conflict with `GOAL-SNOBOL4-100.md`'s own SEAT-KW-3 text (line 1301), which names the same four keywords as one unit but doesn't preclude splitting tracking across rows.

## LOOSE END (iii) RESOLVED — lib_gate.sh CWD-relative-sourcing bug, sized

Prior pass found this incidentally on 2/89 gates and explicitly deferred sizing it ("scope beyond that unknown... mint a row sized to the real count, don't fix ad hoc"). Measured this session:
- **23 scripts** fleet-wide match `$(dirname "$0")/lib_gate.sh` sourcing (`grep -lE '\$\(dirname "\$0"\)/lib_gate\.sh' test_gate_*.sh board_*.sh bench_*.sh`).
- A static heuristic (does a `cd` line appear before the source line) shortlisted 4 candidates — **but empirically running all 23** from the seat root (the DONE-WHEN-sanctioned invocation shape, `bash SCRIP/scripts/X.sh`) found **5 actually break**, catching one (`test_gate_no_c_to_bb.sh`) the static heuristic missed because its `cd` isn't a simple top-level line. Measuring beat guessing, again — same lesson as the false-positive DONE-WHEN catches above.
- Each broken script's OWN substantive check still runs and reports a real verdict — confirmed directly (`test_gate_no_vstack.sh` still printed a correct `FAIL (--strict)`). What silently breaks is `gate_floor`, the exact empty-glob/empty-dir guard that the false-green-gate-script family (`rbx-quarantine-missing-src-false-pass` et al., already well-populated in the queue) exists to police — so this bug removes that specific protection on 5 gates, without currently flipping any of their verdicts.
- Minted `lib-gate-cd-order-silent-skip`, rank 2 (same tier as its sibling false-green family), with a DONE-WHEN that re-runs this exact census — verified to currently read false (bug not yet fixed).
- The 5: `test_gate_no_c_to_bb.sh`, `test_gate_bb_emit_blind.sh`, `test_gate_emit_no_slot_alloc.sh`, `test_gate_no_vstack.sh`, `test_gate_rtcc_claimed_regs.sh`.

## OTHER HOUSEKEEPING

- Confirmed 43 `claims/*.claim` files with no matching FREE `QUEUE.tsv` row are all `DONE`-terminated and correctly swept already — not a defect, not chased further (row-factory discipline: don't chase what isn't real).
- QUEUE.tsv net change this pass: +2 rows minted (`lib-gate-cd-order-silent-skip`, `conform-opsyn-operator-rebind-gz5-fatal`), 1 rank change (`icon-sweep-scratch-hardening` 0→5), 0 retirements (unlike pass 1, nothing in this batch was ALREADY-FIXED).

## CAVEAT — STILL A SNAPSHOT

Same caveat as pass 1, sharper this time: the free-row count grew 89→134 (+50%) in roughly one day despite this row itself retiring/rewriting rows each pass. **This row is confirmed as a standing process, not a one-shot** — STEP 2(a)'s own instruction to future sessions ("re-run the same cross-reference against CURRENT HEAD") should be repeated again, and probably needs to happen more than once per day at the current mint rate. **A secondary lesson from this pass specifically:** even a family that classifies 100% LIVE (the `conform-*` sweep) still hid 4 real corrections behind plausible-looking briefs and one outright false-positive DONE-WHEN — a future sweep should keep independently re-verifying rather than trusting either a green exit code or a fork's first-pass narrative, especially when a claim ("complete no-op", "identical symptom") is strong and easy to check directly.
