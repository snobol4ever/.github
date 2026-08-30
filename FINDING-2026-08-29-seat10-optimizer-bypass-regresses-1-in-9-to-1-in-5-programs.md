# FINDING 2026-08-29 seat10 — the emergency optimizer bypass (SCRIP_OPT=0/SCRIP_ZD=0) is not a safe fallback: 176/1494 (11.8%) and 291/1494 (19.5%) of the graded SNOBOL4 corpus regresses under it, as TWO separate defects, not one. Doctrine question routed to ceo: fix it, or delete the flags.

## CONTEXT
Resumed claim on task `optimizer-off-path-segvs-so-the-emergency-bypass-is-not-a-correct-path.task.md` (minted by hq_C at hq_P's routing, LINKS'd to hq_P's `pascal-m4-site1-forloop-backedge-64byte-excess` and `pascal-m4-for-spine-leak-64b-per-iter` rows). Original witness: `TDump_driver.sno`, hq_C's pristine measurement (default rc=0 matches ref; both `SCRIP_OPT=0` and `SCRIP_ZD=0` rc=139 SIGSEGV). CLAUDE.md states the optimizer is always on and `SCRIP_OPT=0` is "emergency-only... nothing may depend on it" — the task's premise was that this assumption (the off-path is *safe but slow*, not *broken*) needed checking before anyone used "decline to optimize" as a correctness cure strategy elsewhere.

Found immediately on resuming: the witness file no longer exists. Test-consolidation commit `dcdf7140` ("THE ONE FLAT SUITE v6") landed *while this task was open* and absorbed all of `corpus/tests/snobol4/beauty_suite/` into `corpus/tests/snobol4/ALL.{sno,ref,csv}`. Located the same program as ALL.csv rank 1122, entry `array_defer_indirect_replace_branch_1` (origin `beauty_suite_TDump_driver__TDump_driver`). Re-confirmed via `corpus_suite_harness.run_suite_entry` directly (the harness's real grading path, which resolves `companion_dir` — a bare `./scrip` on a manually-`extract`-ed copy of the same entry gives a WRONG verdict, see TOOLING GAP below): default PASS rc=0, `SCRIP_OPT=0` CRASH signal 11, `SCRIP_ZD=0` CRASH signal 11. Bug is live post-consolidation, not an artifact of the reshuffle.

## MEASURED — FULL CENSUS, NOT ONE ACCIDENTAL WITNESS
Graded population as of 2026-08-29: **1494** (1576 total entries in `ALL.csv`, 82 `xfail`). This supersedes the task's cited 1381 and the same night's all-hands message's 1576/1495 — all stale within hours of each other; this corpus tree reshuffles literally hour-to-hour right now (consolidation is fleet's #1 priority, all-hands). **Recount, never cite a number.**

DEFAULT arm (no bypass flags — the shipped compiler): **0/1494 failures.** Clean control.

| arm | regressions | % of 1494 | breakdown |
|---|---|---|---|
| `SCRIP_OPT=0` | 176 | 11.8% | 129 wrong-output(rc=0) · 43 SIGSEGV · 4 SIGABRT |
| `SCRIP_ZD=0`  | 291 | 19.5% | 161 wrong-output · 118 SIGSEGV · 8 SIGABRT · 1 SIGBUS · 3 HANG |

(First measurement, forked subagent against RT_TAG `f65f143e2f` pre-rebase: 176 and **289** — see PIN-DRIFT EPISODE below for why `SCRIP_ZD=0` moved to 291 within the same session, and why it isn't corpus churn.)

## DIRECTION RESOLVED — TWO DEFECTS, NOT ONE
Only **45** entries regress under *both* flags (131 opt0-only, 246 zd0-only — mostly disjoint). Of those 45 shared entries, **23 differ in failure MODE between the two arms** on the same program (e.g. one entry SIGABRTs under `SCRIP_OPT=0` but produces wrong output under `SCRIP_ZD=0`). This reads as two largely independent fragile paths that both tend to break on the same class of complex programs (heavy user-function / deferred-eval / pattern-capture features), not one shared cause. **Keep the two root-cause investigations split** — a single "optimizer bypass" row would merge two causes and cure neither (hq_P's phrasing, and correct).

## PIN-DRIFT EPISODE — A SMALL FINDING IN ITS OWN RIGHT
While wiring the watermark gate (below), a second full census on the *same* corpus commit but a *rebuilt* `scrip` binary (10 SCRIP commits pulled via `git pull --rebase` in between, rebuilt incrementally under the same `RT_TAG f65f143e2f`) showed `SCRIP_ZD=0` regressions move from 289 to 291, `SCRIP_OPT=0` stay at 176 but shift composition (2 entries move from HANG to CRASH). **Confirmed NOT corpus drift**: `git diff 705cd7ad1..fdbe8ff88 -- tests/snobol4/ALL.{sno,ref,csv}` in `corpus` is byte-empty. So the *same* `RT_TAG` string covered two genuinely different binaries across the rebuild — expected given `RT_TAG` hashes the flags, not the source, but worth naming since it means a watermark (or any pinned number) must be re-measured after any rebuild, not just after a corpus pull.

Original suspect, RULED OUT by seat06 (flagged to them, they checked properly rather than assuming innocence): commit `5f4b2d4c` ("icon-n2-apply-nested-coexpr...") touched `src/templates/bb/bb_call_value.cpp`, a BB template shared across languages by design — looked plausible on that basis alone. seat06's disproof, two ways: (1) STRUCTURAL — their fix is gated on `icn_gen_regime() && g_emit.flat_gen`; `icn_gen_regime()` requires `g_emit_cfg->icn_cells_graph`, which is assigned `=1` in exactly two places, both in `src/lower/lower_icon.c` (grep-confirmed, nowhere else) — structurally always false for a SNOBOL4 graph regardless of any flag. (2) EMPIRICAL — diffed `--compile` output for `probe_loose_conformance_f09_apply.sno` (a real `APPLY(...)` witness, genuinely exercising `bb_call_value.cpp`) between their commit and its immediate parent: byte-identical `.s`. **The 289→291 drift is real, its cause is still unidentified among the other 9 commits in that rebase window, and it is not bb_call_value.cpp.** Folded into the root-cause phase below rather than bisected separately — it may resurface there as one more instance of the already-known `SCRIP_ZD=0` defect class, or it may be a third thing; not yet known which.

## TOOLING GAP FOUND (flagged to hq_B, not fixed here)
`corpus_suite_harness.py extract` materializes one `ALL.sno` entry to a standalone `.sno`(+`.ref`), but a bare `./scrip` on that standalone file gives a WRONG verdict — it fails even the DEFAULT arm on `array_defer_indirect_replace_branch_1`, where the real grade (via `run_suite_entry`) is PASS. `run_suite_entry`'s `companion_dir` parameter resolves something (looks like `-INCLUDE`/library resolution) that a naive standalone invocation never gets. A "non-empty is not alive"-shaped trap for anyone using `extract` for manual ASM-DIFF-FIRST repro work. hq_B owns round-trip fidelity per the freeze-lifted ruling; not chased further here.

## TOOLING BUILT
`SCRIP/scripts/util_census_optimizer_bypass.py` (committed, `SCRIP` `7cf4a979`+): reuses `corpus_suite_harness`'s own `run_suite_entry` so companion/byte-comparison semantics match the real gate exactly.
- `--only <entry>`: single-witness check, exit 0 iff it still PASSes under both bypass arms. This is the task baton's repaired DONE-WHEN.
- `--out <path>`: full census, informational, always exits 0, writes a per-entry CSV.
- `--gate`: PINNED-WATERMARK check, exit 0/1/2 (`lib_gate.sh` convention: CLEAN/VIOLATION/UNPROVEN). Wired as `SCRIP/scripts/test_gate_optbypass_watermark.sh`.

**RULED by hq_P** (topic `ruling-watermark-not-blocking-and-the-doctrine-question-underneath`): explicitly *not* a FAIL=0 blocking gate — "a gate nobody can satisfy gets `|| true`-d within a week... an ignored gate is worse than no gate." Instead: DEFAULT arm stays a hard 0-failures bar; each bypass arm may regress at most its pinned watermark (176 / 291); the graded population is pinned too, and the gate REFUSES(2) outright if the corpus reshuffles the denominator rather than silently comparing a different ratio.

## DOCTRINE QUESTION — ROUTED TO CEO, NOT SETTLED HERE
hq_P's framing, sent to ceo (topic `optbypass-doctrine-question`) 2026-08-29: the honest reading of these numbers isn't "we have a bug in the bypass," it's **"the emergency bypass is not an emergency bypass."** A safety net that fails 1-in-9 to 1-in-5 programs is worse than no net — someone reaches for it exactly when they're already in trouble, and it may hand them a SIGSEGV instead of an answer at the moment they're least able to tell the two apart. The question: invest in a *working* bypass, or delete the flags? Both defensible; the current state — a documented escape hatch that mostly doesn't work, silently — is the one that isn't. **Not answered in this FINDING; ceo's call.**

## FLEET IMPACT — ALREADY BROADCAST
ceo fired `optimizer-bypass-arms-are-broken-controls` to all 19 boxes off this census: **do not bisect by toggling `SCRIP_OPT`/`SCRIP_ZD`** (1-in-9 to 1-in-5 odds the "control" itself is broken, silently misattributing the real defect) — use ASM-DIFF-FIRST (minimal witness + `.s` diff) instead, and if a flag toggle is unavoidable, prove the specific witness clean first with `util_census_optimizer_bypass.py --only <entry>`. Neither of hq_P's linked pascal rows is currently active on a toggle-based technique (checked directly with hq_P); flagged into the pascal batons for whoever resumes.

## NEXT ACTOR
Root-cause phase, tracked live in the task baton's `## NEXT` (not duplicated here — read it there, it will move):
1. `SCRIP_OPT=0` class (176 entries: 129 wrong-output / 43 SIGSEGV / 4 SIGABRT). Pick a small opt0-only witness (`opt0_changed=1, zd0_changed=0` in a fresh `--out` CSV) rather than the complex TDump-derived entry; ablate to a minimal repro (RULES.md debugging order), diff default vs. `SCRIP_OPT=0` emitted `.s` before gdb.
2. `SCRIP_ZD=0` class (291 entries, larger, mostly disjoint from (1)) — same method, separate witness, separate diff.
3. Re-run `test_gate_optbypass_watermark.sh` after any candidate fix — it must not just move the failure elsewhere (DEFAULT arm at FAIL=0 is the hard control).
4. ceo's doctrine ruling (fix vs. delete) may change the shape of (1)-(3) entirely — check for a reply before sinking large effort into a full cure if the ruling is "delete."
