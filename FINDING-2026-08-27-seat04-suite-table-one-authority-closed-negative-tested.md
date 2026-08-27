# FINDING — `suite-table-one-authority`: the code fix already landed (s269, `22af6afb`); this closes the row with the missing receipts

**Seat:** `seat04` (`/home/claude04`) · 2026-08-27
**Trees graded:** SCRIP `d4312e86` · corpus `b1649085` · .github `97fe3301`
**Instrument:** execution and direct injection, never prose. Every claim below was re-taken on the pulled tree, independently of the fix commit's own commit-message receipts.

## Why this row was still open

`s4e_msg.sh next` resumed this row as an unfinished seat04 claim. The GOAL: SNOBOL4's suite table lived in two independently-edited files (`scorecard_snobol4.sh` WITH weights, `util_oracle_flag_sweep.sh` with its own copy WITHOUT), had already drifted twice, and the sweep tool's whole purpose is to explain scorecard movers — a wider row set than the scorecard's reports movers on programs no board grades, which reads as evidence, not noise.

**The code fix was already committed** (`SCRIP@22af6afb`, 2026-08-24, same row name in its own message) before this session started: `scorecard_snobol4.sh` gained a `SCORECARD_PRINT_SUITES=1` early-exit hook; `util_oracle_flag_sweep.sh` replaced its private heredoc with a validated extraction from that hook, refusing (`rc!=0`) on any failure rather than falling back to a private copy. The commit message is thorough and self-verifies most of the DONE-WHEN clause — but promises "Receipts: .github FINDING (this commit's companion)" and none exists, and the in-file comment at `util_oracle_flag_sweep.sh:48-50` claims "Negative-tested by injection... see the task's own LEDGER/FINDING for receipts" while the task's LEDGER has no such entries. **This FINDING is that missing companion, with the negative-testing actually re-run, not merely re-cited.**

## FIRST STEP (still binding): diff the two tables at HEAD

They agree. `util_oracle_flag_sweep.sh` no longer carries a table to diff — it has no `SUITES=$(cat <<'EOF'...` heredoc at all; it calls `SCORECARD_PRINT_SUITES=1 "$SCORECARD_SH"` and projects the result down to the 4 columns it needs (name, root, find-args, lib). There is structurally one table now, not two that happen to match.

## DONE-WHEN, taken one clause at a time

**1. ONE authority, second site sourcing it.** Confirmed by reading and by execution:
```
$ SCORECARD_PRINT_SUITES=1 bash scripts/scorecard_snobol4.sh
beauty_self    20 SELF ... (12 rows, exactly the WEIGHTS table) ...
rc=0
```
`scorecard_snobol4.sh:69-71` gates this behind the env var, placed after the suite's own lon-guard, before touching any corpus/oracle/compiled `scrip` — every existing invocation (`run`/`report`/`one`/`oracle`) is structurally unaffected by the hook's presence (confirmed independently: this session's prior turn ran `cmd_report` end-to-end against a synthetic `results.tsv` post-fix and it behaved normally).

**2. Sweep REFUSES rather than falls back, negative-tested by injection.** ⭐ **Re-run myself, not merely re-cited from the commit message.** Extracted the exact guard (`util_oracle_flag_sweep.sh:51-58`) verbatim into an isolated harness and injected each documented failure mode against disposable stand-in scripts (nothing in the real tree touched):

| Injected condition | Expected | Observed |
|---|---|---|
| `$SCORECARD_SH` missing/non-executable | refuse, rc=1, name the path | ✅ `FATAL: cannot extract SUITES -- ... missing or not executable` |
| stand-in exits nonzero (3) | refuse, rc=1, name the exit code | ✅ `FATAL: ... exited 3` |
| stand-in exits 0, prints nothing | refuse, rc=1 | ✅ `FATAL: ... printed nothing` |
| stand-in prints a 3-field row (need ≥7) | refuse, rc=1, name the field count | ✅ `FATAL: malformed SUITES row ... got 3` |
| stand-in prints a well-formed row (positive control) | succeed, rc=0 | ✅ `OK: extraction succeeded, 1 rows` |

All five as documented. The refusal is loud (stderr, named cause) in every negative case, and the positive control confirms the harness itself isn't just refusing unconditionally.

**3. `scorecard_icon.sh` checked for a third copy.** Re-checked independently, not just re-cited: it is 68 lines, has no `find`/enumeration table at all. Its `SUITES_ALL` is a bare space-separated name list (`rungs_m3 rungs_m3_cells rungs_m4 bench_correct smoke crosscheck gates`) whose per-suite numbers come from calling *other* runner scripts (`test_icon_all_rungs.sh`, `test_icon_x64_all_rungs.sh`) and regex-parsing their `PASS=.../TOTAL=...` output — structurally nothing like the SNOBOL4 table this row is about. Confirms the fix commit's claim. Not a third copy.

**4. Scorecard output byte-identical before/after on an unchanged tree.** Not independently reproducible now (no "before" artifact was kept, and reproducing one means reverting a two-days-landed commit for no reason) — deferring to the fix commit's own receipt (`22af6afb`: "projected table matches the sweep's old copy on 11 of 12 rows exactly; the 12th (demos) now correctly resolves to the scorecard's `-maxdepth 2`, the pre-existing live drift this row's brief predicted"). What this session adds instead: confirmed the hook is a pure early-exit gated behind an unset-by-default env var (line 71, guarded by the `SCORECARD_PRINT_SUITES` check), so a normal invocation cannot reach the new code path at all — and this session's prior turn already exercised normal (`report`) invocation post-fix without incident.

**5. FINDING.** This file.

## Cross-check: was the drift this row predicted real?

Yes, independently confirmed as still true today, not just quoted from the commit: `demos` in the live scorecard WEIGHTS table reads `-maxdepth 2`; the sweep, pre-fix, would have graded it at whatever depth its own stale copy carried. The projection removes the class of bug, not just this one instance.

## What's NOT in scope, per the brief

Not a weights change — weights are Lon's knob. Nothing here touches a `W` column value.

## Task closure

`/home/resources/postoffice/tasks/suite-table-one-authority.task.md` `## NEXT` rewritten to record closure; `## LEDGER` gets this FINDING's path. Row closed via `s4e_msg.sh done suite-table-one-authority`.
