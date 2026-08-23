# FINDING seat15 — m1-board-judge-is-a-refusing-oracle: FIXED. `board_beauty_m1.sh` now judges the M1 milestone against the input file itself (Lon s117, no oracle) and grades prefix rungs against a frozen pre-BEAUTY-CN `beauty_classic.sno`; 10/10 green both modes on a pristine build. Follow-on sweep: `util_beauty_override.sh` confirmed broken by the identical bug (empirically reproduced); `scorecard_snobol4.sh`'s `beauty_self` suite confirmed already safe; `util_oracle_flag_sweep.sh` flagged as structurally at risk, not yet confirmed.

**Session:** 2026-08-23 seat15 (`/home/claude15`), THE LOOP queue row `m1-board-judge-is-a-refusing-oracle`, rank 0 — assigned by hq_P via the v2 ASSIGN+doorbell mechanism (cross-session message, arrived mid-way through closing `reprofile-after-byname-bake`, which independently found the same root cause from the perf-ratio angle; see that row's own FINDING for the cross-validation).
**Status:** DONE against the row's own DONE-WHEN (verified below, pristine build). Root cause is hq_P's own finding (`FINDING-2026-08-23-hq_P-the-m1-board-grades-beauty-against-an-oracle-that-refuses-it.md`) — not re-derived here, only cited.
**SCRIP tree:** HEAD `f704b1b1` at start, `make pristine` run twice this session (once before, once after the code change, per HQ-27). `scripts/board_beauty_m1.sh` modified. **corpus tree:** one new file added, `corpus/programs/snobol4/demo/beauty/beauty_classic.sno` (frozen snapshot, see §2). No other code touched.

---

## 1. The fix

`board_beauty_m1.sh`'s rung judge previously ran the SAME live oracle call for every rung, including the full-file one, against the CURRENT `beauty.sno` — which opens BEAUTY-CN's `&`-constant namespace at line 9 and is therefore no longer SPITBOL-gradable at all (hq_P's finding, root cause). Two independent judges now replace the one:

- **The full-file rung (n = TOT = 630, the actual MILESTONE 1 check):** oracle-free by design. Judge = `cmp` against the checked-in `beauty.sno` itself (Lon ruling s117 — "the checked-in file is its own oracle"). No SPITBOL involved, none needed, none possible.
- **Prefix rungs (n = 1,2,5,...,320):** still graded against the live oracle, but on a **frozen pre-BEAUTY-CN snapshot**, `corpus/programs/snobol4/demo/beauty/beauty_classic.sno` — extracted verbatim from git history at `53dd9ac0d^` (the commit immediately before the BEAUTY-CN conversion began; `84acdeb0e`, "beauty.sno repaired so it COMPILES again"), 622 lines / 40,971 bytes. **Independently verified before wiring it in** (§2): portable SPITBOL, oracle-gradable, and itself a byte-identical fixed point on BOTH engines using today's checked-in `.inc` files — a clean, working ladder target, not a hopeful guess.
- **Refusal detection, upgraded mid-fix**: my first draft sniffed the oracle's stdout for a single marker (`") : ERROR "`). Before finalizing, I found `scripts/scorecard_snobol4.sh` already carries a more rigorous two-marker check (`sbl_died()`, s191 row `ref-the-ungraded-suites`, built for a different incident — Gimpel corpus's ERROR 042/116/etc. — same underlying SPITBOL behavior: exits 0 after printing a fatal report) that requires **both** the `" : ERROR NNN -- "` line **and** the `"in statement N"` locator, "never either alone." Adopted the same two-marker check here for consistency and precision (verified both markers present in the real captured beauty.sno refusal, §4). A refusal (by exit code OR content) is tagged `ORACLE-REFUSED(...)` and excluded from both pass/fail tallies — never diffed as if it were real output.
- **V2-5 exit-code discipline wired in** (this board previously had no exit code contract at all — fell through to `echo`'s always-0 status regardless of outcome): now sources `lib_gate.sh` and uses `gate_require_exec`/`gate_require` for prerequisites, `gate_floor` to refuse (UNPROVEN, 2) if literally zero prefix rungs ever got real oracle grading (the "zero-examined looks identical to all-clean" class, same reasoning as the missing-file case `gate_floor` already covers), and `gate_verdict` for the final CLEAN(0)/VIOLATION(1) call — never fabricating a violation out of an oracle refusal.

## 2. Verifying `beauty_classic.sno` before trusting it as a ladder target

Before freezing anything, tested the candidate (git-extracted, today's `.inc` files):
```
sbl -bf beauty_classic.sno < beauty_classic.sno   → rc=0, 40,971 bytes, byte-identical to input (fixed point)
scrip   beauty_classic.sno < beauty_classic.sno   → rc=0, byte-identical to the ORACLE's output too
```
Both engines agree, both reach the fixed point, using the CURRENT `.inc` files (which have not needed to change independently of BEAUTY-CN as far as this file is concerned). This is not a guess or a "should work" — it's the same verification discipline as the milestone check itself, just applied to the frozen file once, at freeze time.

## 3. Verification of the fix itself

Full run, pristine build, default invocation (both modes, default rungs):
```
lines  m3 (--run)          m4 (--compile)
    1  PASS                PASS
    2  PASS                PASS
    5  PASS                PASS
   10  PASS                PASS
   20  PASS                PASS
   40  PASS                PASS
   80  PASS                PASS
  160  PASS                PASS
  320  PASS                PASS
  630  ⭐M1-FIXED-POINT    ⭐M1-FIXED-POINT
M3 rungs green: 10/10   first red at: none
M4 rungs green: 10/10   first red at: none
GATE PASS(0) [board_beauty_m1]: 0 rungs failed ... (examined 18)
```
`--modes m3` regression-checked separately (m4 rungs correctly show `-`, correctly excluded from the m4 tally and from the aggregate verdict rather than counted as failures — the `MODES` guard on the milestone check matters here). Task's own DONE-WHEN verified against this pristine build: `bash scripts/board_beauty_m1.sh 2>&1 | tail -6 | grep -qE "M4 rungs green: 10/10|UNPROVEN"` → **PASS**.

## 4. Negative test (V2-5 "gates can say no" discipline, per this row's own NEXT item 4)

The new risk surface is the refusal sniff — could it swallow a REAL divergence as a false "refused, not counted"? Tested directly, not assumed:
- **Real captured refusal** (`.../beauty.sno(10) : ERROR 251 -- keyword operand is not name of defined` / `in statement         2`): both markers match → correctly tagged `ORACLE-REFUSED`.
- **Synthetic plausible SNOBOL4-looking-but-wrong output** (no error citation, just ordinary statements): neither marker matches → correctly falls through to the real `cmp`/`DIFF` path, unaffected by the new gating.
- **Injected corruption attempt** (mutated `beauty_classic.sno` copy in scratch, a bad `&FULLSCAN` value): both engines rejected it outright (rc=1 each) — this landed in the pre-existing, unmodified `orc≠0` neutral bucket rather than exercising the new content-sniff path; noted as a limitation of this specific injection (too aggressive, not a subtle same-rc-different-output divergence) rather than a validated case. The two isolated-marker tests above are the actual evidence for the new code's precision.

## 5. Follow-on sweep (this row's NEXT item 5) — evidence-based, not exhaustive

Grepped every script referencing both `beauty` and `sbl`/`SBL`/`sbl_clean_bin`/`sbl_correctness_bin` (13 hits including this board). Checked the highest-risk candidates with actual runs, not just source-reading:

| script | status | evidence |
|---|---|---|
| `board_beauty_m1.sh` | **FIXED** (this row) | §3 |
| `util_beauty_override.sh` ("THE CLASS-A REPRODUCER... reach for it first") | ⛔ **CONFIRMED BROKEN, same bug, every invocation** | Ran it live: `util_beauty_override.sh '&Integer' "epsilon"` → `DIFF rc=0 ... oracle=///ovr.sno(10) : ERROR` — it `cp`s the whole beauty dir (current, BEAUTY-CN'd `beauty.sno`) into scratch and only overrides ONE named grammar line downstream of line 9, so line 9's `&USER_DECLARED_CONSTANTS` reproduces the identical refusal on literally every use. This is the tool the project's own docs say to reach for FIRST when investigating a beauty crash class — it currently cannot produce a real verdict at all. **Recommend HQ mint a dedicated follow-on row**; fixing it needs its own design call (unlike this board, its whole point is testing the CURRENT file's exact behavior, so pointing it at `beauty_classic.sno` instead would change what it's testing — not a decision to make silently in someone else's row). |
| `scorecard_snobol4.sh` (`beauty_self` suite) | ✅ **CONFIRMED ALREADY SAFE** | Ran `scorecard_snobol4.sh run --suites beauty_self` live: reports `UNSCR` (unscored, excluded from every number), not a false pass or false diff — `sbl rc=139` (a SEGV, not the rc=0-with-text shape I saw via direct invocation; the difference is unexplained and not chased here, out of scope, flagging only) plus this harness's own pre-existing `sbl_died()` two-marker check (§1's precedent) together mean it was never exposed to a false verdict here. Positive finding, not a risk. |
| `util_oracle_flag_sweep.sh` (`beauty_self` arm) | ⚠ **STRUCTURALLY AT RISK, NOT EMPIRICALLY CONFIRMED** | Reads: raw `md5sum` comparison across three `sbl` flag arms (`-b`/`-b`/`-bf`) with no content-based refusal check visible — if all three arms hit the same rc=0 error dump, it would report `tag=same` (flags don't matter) rather than "the oracle refused all three ways," a vacuous-same rather than a false-DIFF, but still not an honest verdict. Not run live this session (a heavier multi-arm sweep, out of this row's time-box); flagging for whoever picks up the util_beauty_override.sh follow-on to check in the same pass. |
| `test_corpus_snobol4.sh` (beauty_suite drivers) | ✅ Likely safe by design | Grades against pinned `.ref` files (generated offline), not a live diff — the documented safe pattern (`ARCH-SN4-CONSTANTS.md` "Oracle amplification": extension programs are oracle-fail by construction → pinned `.ref` lane). Also operates on `beauty_suite`'s small driver files, not `beauty.sno` itself. Not independently re-verified. |
| `test_gate_const_graph.sh`, `test_gate_udc.sh` | Likely safe by design | Matched the grep for UDC-related terms but showed no direct `sbl` invocation — consistent with the same pinned-`.ref` pattern these UDC gates are documented to use. Not independently re-verified. |
| `test_demo_descent_sweep.sh`, `test_rsp_descent_sweep.sh` | Lower priority, not verified | Operate on `beauty_suite` driver files via a generic descent sweep, not `beauty.sno` itself as far as read; not run. |
| `test_gate_ec_uni_complete.sh` | Different defect class, not this one | Grades `beauty.sno --compile` against a **pinned md5** (`6bf2e9daa777f54f04c8f7160da435d1`) for an unrelated internal-optimization check (PPV-2) — the *other* anti-pattern this session already caught itself doing once (see `FINDING-2026-08-23-seat15-reprofile-after-byname-bake-beauty-fixed.md` §1), not the live-oracle-diff bug this row fixes. Out of scope here; naming it so the "pinned hash goes stale" lesson isn't lost. |
| `test_snocone_beauty_self_host.sh`, `util_run_beauty_sc.sh`, `util_run_beauty_oracle.sh` | Different frontend, not verified | Snocone port (`beauty.sc`), a separate language surface from BEAUTY-CN's SNOBOL4 `&`-constant conversion; unclear without reading whether Snocone independently has an equivalent extension. Not chased — different rung's territory. |
| `test_monitor_3way_sync_step_auto.sh` | Different runtime, not verified | `GOAL-NET-BEAUTY-SELF` — a .NET port self-host check, separate concern. Not chased. |

## 6. Items for HQ (findings, not blockers — this row is DONE regardless)

1. **Mint a follow-on row for `util_beauty_override.sh`** — confirmed broken by the identical mechanism, and it's the project's own designated first-reach tool for beauty crash investigation. Needs its own design decision (see table above), not a copy-paste of this row's fix.
2. `util_oracle_flag_sweep.sh`'s `beauty_self` arm is unverified and structurally suspicious (§5) — worth checking in the same follow-on pass.
3. `scorecard_snobol4.sh`'s `beauty_self` SEGV (rc=139) vs. this row's own direct-invocation rc=0-with-error-text — same program, same oracle binary, different failure shape depending on harness (stdin handling / SETL4PATH / sizing flags?). Not chased, noted for anyone who wants to fully map SPITBOL's behavior on this input.
4. `scorecard_snobol4.sh`'s existing `sbl_died()` and this row's now-duplicated two-marker check are the same logic in two places — a small, low-priority case for extracting a shared `sbl_refused()`-style helper into `lib_oracle_flags.sh`, matching that file's own role as "the ONE authority" for other oracle questions. Not done here (would mean editing a script this row doesn't own).

## 7. DONE-WHEN

Unchanged from the baton (`R="$PWD"; cd "$R/SCRIP" && bash scripts/board_beauty_m1.sh 2>&1 | tail -6 | grep -qE "M4 rungs green: 10/10|UNPROVEN"`) — verified passing against a pristine build, §3. Handing off via `s4e_msg.sh done m1-board-judge-is-a-refusing-oracle`.
