# FINDING — gimpel-suite-triage: 144 drivers re-graded, 8 symptom classes, one minimal witness each

**Session:** 2026-08-27, seat10 · postoffice task `gimpel-suite-triage` (rank 1, minted hq_C s266)
**Scope, per the task's own GOAL:** DISCOVERY, not cure. Nothing in `SCRIP/src` was touched. This is a
fresh re-triage against current HEAD, not a continuation of the 2026-08-20 s183–s194 gimpel batch
sessions (whose FINDINGs classified the same suite by *construct*, e.g. "X = SPAN(X) self-rebind" —
see `FINDING-2026-08-20-s186-gimpel-batch-a-*.md` and its five siblings). This row asks for coarser
*symptom* buckets (compile-err/link/crash/DIFF/timeout) with one witness per bucket, so it re-measures
rather than assumes those classes still hold — several do not (§5).

**Trees graded:** SCRIP `f7af8606` (bin md5 `3c97fca1c34d`, `make pristine` at `-O0`, built
2026-08-27T08:43:28), corpus `9068fdd4`. ⛔ Origin moved twice more under SCRIP during this session
(to `e637707d`, then `1f79ed2f` ahead of that) from unrelated concurrent activity (Icon N-2 zeta-frame
work, a `.ref`-comment fix) — per REBASE-BASELINE COROLLARY, this row's build was never re-pulled or
rebuilt mid-measurement, so every number below is one consistent tree throughout, named here rather
than chased.
**Oracle:** `/home/resources/x64/bin/sbl -bf` only, live (not pinned) for every verdict and every witness
`.ref` in this row, minted fresh this session.
**Harness:** `SCRIP/scripts/scorecard_snobol4.sh run --suites gimpel`, the suite's own registered row
(`-name *_driver.sno`, so all 445 files in `corpus/packages/snobol4/gimpel/` are correctly narrowed to
the 144 real driver programs before grading — see that directory's own `README.md`; the 301 `NAME.sno`
library modules are not programs and are not counted).

## 1. THE BOARD — 144 drivers, current state

```
SUITE      W    N  M3ok  M4ok   m3%   m4%  SCORE  UNSCR
gimpel     5  126    53    53  42.1  42.1   42.1     18
```
144 total − 18 UNSCR (oracle cannot run them, no pin — excluded from every percentage; unchanged
mechanism from `FINDING-2026-08-20-s191-the-gimpel-suite-scored-145-library-modules-*.md`, still the
`INPUT`-third-argument dialect trap and a few genuine SPITBOL-protected-name collisions) = 126 scoreable,
53 PASS both modes = **42.1%**. The task brief's own s264 census read 40.5% — consistent drift, not a
contradiction; three days of unrelated compiler work moved it 1.6 points.

## 2. THE 8 SYMPTOM CLASSES — every (m3,m4) status pair observed among the 73 real failures

Ranked by member count. `status pair` is the harness's own per-mode verdict (`PASS DIFF TIMEOUT SIG<n>
RC<n> COMPILE_FAIL ASM_FAIL ORACLE_FAIL`); a divergent pair (m3 ≠ m4) is itself a finding, since
`m3 ≡ m4` is this compiler's own stated design invariant (CLAUDE.md, Architecture) — 24 of the 73
failures (33%) violate it.

| rank | class (status pair) | n | witness | line count | what it shows |
|---|---|---|---|---|---|
| 1 | `COMPILE_FAIL`/`COMPILE_FAIL` | 18 | `class1_dup_label_*.sno` (2 files) | 4+3 | **isolated sub-mechanism, not the whole bucket** — see §3 |
| 1 | `RC1`/`COMPILE_FAIL` | 18 | `class2_rc1_compile_fail_dexp.sno` | 9 | honest unlanded-subset refusal (runtime-`DEFINE`), m3 and m4 print the identical FATAL and both exit rc=1, m4 just never emits a binary |
| 3 | `DIFF`/`DIFF` | 15 | `class3_diff_span_self_rebind.sno` | 14 | silent wrong answer: `X = SPAN(X)` self-rebind is an inert pattern (both modes agree with each other, disagree with oracle) |
| 4 | `RC1`/`RC1` | 8 | `class4_rc1_rc1_copyl.sno` | 12 | runtime self-`DEFINE` recursion overflows SCRIP's stack (`ERROR 246`) on a 2-node case the oracle finishes instantly — see §4 |
| 5 | `SIG11`/`SIG11` | 7 | `class5_sig11_seq_*.sno` (2 files) | 16+5 | `CODE()`-compiled string + indirect goto `:<ARG_S>` SIGSEGVs both modes after printing partial output |
| 6 | `RC1`/`SIG11` | 4 | `class6_rc1_sig11_once.sno` | 13 | **mode-divergent crash**: m3 fails soft (`Error 22 — undefined function called`, rc=1), m4 SIGSEGVs, same self-modifying `CONVERT(...,'EXPRESSION')`-built pattern |
| 7 | `SIG6`/`COMPILE_FAIL` | 2 | `class7_sig6_compile_fail_ip.sno` | 9 | unary `~` (NOT) lowers to IR op=3, which has no emitter template — `emit_drive`'s universal driver aborts (`SIGABRT`) the instant it sees the op, at compile time, in *both* modes (m4's abort happens during `--compile` itself, hence COMPILE_FAIL there and SIG6 in m3) |
| 8 | `SIG6`/`SIG6` | 1 | `class8_sig6_perm_*.sno` (3 files, see note) | 9+29+9 | same self-`DEFINE` recursion family as rank 4, this time exhausting the *workspace heap* (`[WSI] workspace island exhausted, 1024 MB`) instead of the C stack — ~30–40s wall clock to manifest, oracle answers in a fraction of a second |

No `ASM_FAIL` (link failure) and no `TIMEOUT` occurred anywhere in the 144-driver run — both of the
task's five suggested buckets are legitimately *empty* right now, not merely unwitnessed.

All 8 `.ref` files are fresh live-oracle output minted this session (`sbl -bf`, redirected `< /dev/null`),
none hand-authored, none copied from an old pin.

## 3. ⭐ THE #1 BUCKET IS AT LEAST TWO UNRELATED DEFECTS, AND ONE IS FULLY ISOLATED

`grep`-ing every `COMPILE_FAIL`/`COMPILE_FAIL` driver's own error line splits it cleanly:
- **4 of 18** (`HYPHENAT`, `LINE`, `L_TWO`, `MINP`) say `error: duplicate label 'NAME'` — every one of
  these drivers `-INCLUDE`s a small helper (`SPACING.sno`, `COUNT.sno`, etc.) that is ALSO
  `-INCLUDE`d, transitively, by a second helper the same driver pulls in — a diamond. **SCRIP's
  `-INCLUDE` has no include-guard**: the shared file's labels land in the flattened unit twice.
  Verified in isolation as the whole mechanism, independent of any real gimpel content:
  `class1_dup_label_driver.sno` `-INCLUDE`s the same 3-line helper twice, nothing else, and gets the
  identical `duplicate label` shape SCRIP gives on the real 4 drivers. The oracle handles the diamond
  with no complaint (`sbl -bf` answer: `1`), so this is a real SCRIP-side gap, not a dialect issue.
- **14 of 18** say `error: parse error: syntax error` at a driver-specific line — genuinely
  unclassified; each may be its own construct (unsupported syntax) rather than one mechanism. Not
  ablated this session (time-boxed) — a natural next queue row, and the include-guard fix above will
  shrink this bucket to 14 the moment it lands, which is itself a useful predicted-effect note for
  whoever mints that cure row.

## 4. ⭐⭐ THE SELF-`DEFINE` RECURSION IDIOM IS ONE ROOT CAUSE BEHIND TWO SEPARATE SYMPTOM CLASSES

`COPYL` (rank 4, `RC1/RC1`) and `PERM` (rank 8, `SIG6/SIG6`) are unrelated gimpel functions — one copies
a linked list, one runs Trotter's permutation algorithm — but both are written in the same classic
SNOBOL4 idiom: `DEFINE('F(...)','OTHER_ENTRY')` called *at runtime, from inside F itself*, to swap the
function's own entry point after a one-time setup (so the caller-visible signature stays `F(...)` while
the hot path skips re-initializing). Both idioms recurse in SCRIP without ever terminating — COPYL hits
the C call-stack guard first (`ERROR 246`, fast), PERM hits the workspace heap ceiling first (`[WSI]
exhausted`, slow, ~30–40s) — while the **live oracle finishes both instantly** on the same inputs
(`class4`: `done`; `class8`: `3 permutations`, the mathematically correct 3! − 1 = wait, 2-element case,
2 permutations plus the initializing call = `3 permutations`, matching `PERM_driver`'s own header
comment about the off-by-one-by-design first call). One shared mechanism, two different resource
ceilings hit first — a single cure candidate (something about how SCRIP compiles a function that
re-`DEFINE`s itself mid-call is not actually shrinking/terminating its own activation the way the
oracle's implementation does) plausibly closes both rows at once. Flagging the link; not diagnosing
the mechanism further (out of scope — DISCOVERY, not cure).

## 5. DRIFT SINCE THE s183–s194 BATCH FINDINGS — do not carry those classes forward uncritically

Re-ran every witness already committed under `corpus/probe/gimpel/` (the s186-era batch-A/B/etc.
minimal witnesses) against the current build before writing anything new, per this row's own caution
about the compiler having moved. Result: **at least 6 of the 9 original s186 "nine defect classes" no
longer reproduce as originally described** — `gim_span_param_pattern_wrong`, `gim_tab_defer_no_template`,
`gim_defer_pred_in_pattern_segv`, `gim_real_print_precision`, `gim_defer_cassign_indirect` and
`gim_eval_silent_success`'s narrow case now all match the live oracle (fixed, presumably by the
FENCE/choice-record/frame-rsp work landed 2026-08-23, though this session did not bisect which commit).
`gim_span_self_rebind_wrong` (class 1, `X = SPAN(X)`) and the `~`-operator no-template class (class 4,
now `SIG6` instead of a clean FATAL exit) still reproduce and are reused/promoted above as `class3` and
`class7` respectively. Not a regression audit — just the reason this row re-measured instead of
reusing the old table wholesale, and a useful "already fixed, don't re-open" list for whoever triages
the old batch FINDINGs' remaining open items.

## 6. DELIVERABLES

- `corpus/probe/gimpel_triage/class{1..8}_*.sno` + matching `.ref` (12 `.sno`, 8 `.ref` — classes 1, 5
  and 8 are 2–3 files each since their mechanism is inherently a shared-helper `-INCLUDE`).
- This FINDING.
- Task file `## LEDGER` appended, `## NEXT` written, at `/home/resources/postoffice/tasks/gimpel-suite-triage.task.md`.

## 7. SUGGESTED NEXT ROWS (not filed as queue rows — DISCOVERY scope; naming them for whoever mints cures)

1. `-INCLUDE` diamond de-duplication (include-guard) — closes 4 of 18 in the top bucket, isolated and
   reproduced in 7 lines total (§3).
2. Root-cause the shared self-`DEFINE`-recursion non-termination — plausibly closes rank-4 and rank-8
   together (§4).
3. Classify the remaining 14 ungrouped `parse error: syntax error` members of the top bucket — will
   shrink once (1) lands; re-measure after, don't assume all 14 survive it.
4. The `RC1`/`SIG11` mode-divergence (rank 6) is an `m3 ≡ m4` invariant violation on its own, independent
   of whatever ONCE's actual bug is — worth a note to whoever owns that invariant's gate.
