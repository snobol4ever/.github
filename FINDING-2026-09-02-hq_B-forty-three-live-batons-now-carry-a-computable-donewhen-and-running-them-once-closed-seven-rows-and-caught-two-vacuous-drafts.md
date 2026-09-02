# FINDING 2026-09-02 (hq_B) — forty-three live batons now carry a computable DONE-WHEN; running each cheap one once on the uncured tree closed seven rows that were already done and caught two vacuous drafts of my own

**Tree:** SCRIP `862c51cb` · corpus `d0351a54` · MODE `TRIO` (file read). Row `live-batons-all-carry-a-computable-donewhen` (ceo mint via hq_P, ladder I rank 1; ruling option (b)): each LIVE row gets a criterion `s4e_msg.sh done` can execute, or a supersede with a reason. Gate `test_gate_baton_donewhen_runnable_live.sh`: **LIVE=43 at claim → LIVE=0 at close**; riders 1 (11 already-DONE rows, audit) and 2 (14 orphan batons) are ceo's and untouched.

## What was written

43 criteria, each authored from its row's GOAL, one line, `${S4E_HOME:?}`-anchored, parseable, first word a command, no no-op form. 13 replaced the untouched mint placeholder, 24 replaced prose, 6 replaced commands that spilled over several lines or carried a prose tail (`— PLUS …`). The text each replaced is kept on a `DONE-WHEN-WAS` line in its baton, and every baton got a ledger line saying the criterion is not a verdict.

⭐ **Where the witness had moved, the criterion follows the origin, not the path.** The corpus re-grid absorbed `probe/icn` into `tests/icon` (`probe_witness__*`), `probe/vlist_select` and `probe/fuzz` into `tests/snobol4` (`probe_vlist_select__*`, `probe_fuzz__*`), `crosscheck/snocone/rungXNN` into `tests/snocone` (`crosscheck_rungXNN`), `pb30.pas` into `tests/pascal`, `demo/` into `demos/`. Nine batons still named the dead paths. Their criteria extract by ORIGIN through `lib_master_extract.sh` or the harness's `extract-family`.

## ⭐ Running them once is what made the sweep worth anything

| result | rows |
|---|---|
| red on the uncured tree, as a criterion should be | 22 |
| green — checked a second, independent way, row genuinely done, **CLOSED by computed `done`** | 7: `probe-icn-glob-invisible` (11 origins in the Icon master, graded by `board_icon_master.sh`), `polyglot-demo05-compile-time-sigabrt` and `polyglot-demo10-tan-nat-wrong-answer` (`test_gate_polyglot_demos.sh` m3 10/10 m4 10/10), `prolog-call-n-multiarg-target-wrong` (prints 6 and 5), `icon-rung10-augop-two-entries-named-break-…` (0 break-named entries remain), `suite-harness-xfail-extract-round-trip` (an XFAIL entry re-converts with ON-DISK RE-VALIDATION PASSED), `vlist-v05-m4-sigsegv-m3-m4-divergence` (the family 8/8 in both modes) |
| green, NOT closed | 1: `pascal-m4-intermittent-segv-pb30-sieve` — 100 fresh m4 runs of each witness all correct; the crash is not reproducible here, and the baton's own prose says a re-run-N pass proves absence of the symptom, not a fix. Noted on its baton for its owner. |
| **vacuous first draft, caught by the run, fixed** | 2: the fuzz criterion matched no origin (the prefix is `probe_fuzz__`, not `fuzz__`) and passed over an empty loop — now guarded `n>0`, 58 entries examined, `probe_fuzz__fz_abort_05` still nondeterministic, red; the perf-sweep criterion ended in `; true` — a no-op tail that made the whole line green — now a subshell that exits 1 without the audit FINDING, red |
| expensive (`make pristine` + a board / Icon all-rungs), checked statically only | 13 |

**The lesson the two vacuous drafts teach, in one sentence:** a criterion that parses and resolves is not yet a criterion — the gate was right to refuse to execute them, and the author has to. The first draft of the fuzz line would have closed a row with a live nondeterminism in it.

**Receipts:** the batons (43 `DONE-WHEN-WAS` lines + ledger lines); QUEUE.done.tsv (7 closures + this row); the gate line `uncloseable batons: 25 total -- LIVE=0 · already-DONE=11 · ORPHAN=14`.
