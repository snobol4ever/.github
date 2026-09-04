# FINDING 2026-09-03 seat09 — csnobol4_suite reconciled; prior classes re-verified; two new classes found

## Context
Task `snobol4-csnobol4-suite-non-pass-censused-by-class-and-cured` (SNO1, postoffice, minted ceo CEO-175, hq_P lane, FLEET-16 re-start). GOAL: reconcile SCORE.md's two disagreeing `csnobol4_suite` readings, then census the non-pass entries BY CLASS. This FINDING covers both halves. Cure is hq_P's (Opus); this pass is discovery + witness only, same division of labor as `FINDING-2026-08-27-seat06-csnobol4_suite-triage-eight-classes-three-are-not-scrip-bugs.md` (hereafter "the Aug 27 FINDING"), which this pass builds on rather than repeats.

## Part 1 — Reconciliation (already landed, `.github` `a9e0d686`)
SCORE.md carried a grid cell reading `58/58` at commit `4118b58f` and a detail-table reading `52/118` at `d24e99d8`. `4118b58f` does not resolve as an object anywhere in this repo (`git merge-base --is-ancestor` errors "Not a valid object name"), and 58 cannot be this suite's total under the runner's own "every `.sno` with a sibling `.ref`, no hand-curated exclusions" rule — 118 is the real, structurally-fixed population (confirmed independently: `118 of 124 vendored programs have a gradable .ref`). Fresh run on SCRIP `ce199b05`/corpus `ce673206b` (9 SCRIP commits after `d24e99d8`) reproduces the `52/118` reading exactly: `total=118 m3_PASS=52 m3_FAIL=25 m3_REJECT=40 m3_CRASH=1 m3_HANG=0 m4_PASS=52 m4_FAIL=24 m4_REJECT=41 m4_CRASH=1 m4_HANG=0`, triangulation `PASS=83 FAIL=35`, `REGEN-CANDIDATE=35`. `58/58` is retired — most likely the pre-fix, symlink-corrupted first cut the runner's own header comment documents (a same-session bug that skewed pass/fail by exactly 1 per mode; nobody re-ran the grid cell after the fix landed). SCORE.md updated in three places (both grids + the detail table) and pushed.

## Part 2 — Census: re-verifying the Aug 27 classes under the CURRENT runner
The Aug 27 FINDING used a different harness (`scorecard_snobol4.sh`, STATUS ∈ {PASS,DIFF,TIMEOUT,SIGn,RCn,COMPILE_FAIL,ASM_FAIL,ORACLE_FAIL}) against N=122. The current runner (`test_snobol4_csnobol4_suite.sh`) uses a different, simpler taxonomy (PASS/FAIL/REJECT/CRASH/HANG by rc+output-match) against N=118. Re-verified by cross-referencing all 66 current RED-M3 names against the Aug 27 class membership (mechanical checks: lowercase terminal `end`, `-INCLUDE` target existence/trailing-space, known-extension keyword grep) plus direct re-runs where the automated check was ambiguous.

| Class | Aug 27 verdict | Still reproducing? | Notes this pass |
|---|---|---|---|
| #1 lowercase keyword (14: `8bit2 breakline conv2 diag1 diag2 func2 hide k noexec space space2 setexit setexit5 setexit6`) | NOT a SCRIP defect | ✅ all 14 reconfirmed (lowercase terminal `end` detected in every member) | Unchanged. Cure tool still `util_uppercase_keywords.py`, still unrun against this suite. |
| #2 missing `-INCLUDE` target (10: `base float2 include2 include3 include4 json1 ndbm random sleep time`) | NOT a SCRIP defect | ⚠️ partially reconfirmed | `sleep` mechanically confirmed (`../modules/time/time.sno` absent). Several members (`base include2 include3 include4 ndbm random time`) ALSO carry a lowercase terminal `end`, so which defect actually fires first (parse rejects on the keyword before ever reaching `-INCLUDE` resolution) is unverified per-file — flagged, not re-traced this pass. |
| #3 DIFF / `&DUMP` etc. (16, only `a dump popen popen2 loaderr` named) | mixed: `a`/`dump` confirmed SCRIP defect, `popen*`/`loaderr` likely out-of-scope extensions | ✅ `a`/`dump` reconfirmed (`&DUMP=1` still a silent no-op, rc=0, no dump report) | See NEW-A below — `&DUMP` turns out to be one instance of a broader "diagnostic-keyword output silently dropped" shape shared with `&TRACE`/`&FTRACE`/`TRACE()`. |
| #4 content-after-`END` (12, only `sudoku atn crlf trim0 trim1 uneval2` named as plausible) | confirmed SCRIP defect (traced only on `sudoku`) | 🟢 **mostly fixed** — 4 of 6 named members (`sudoku trim0 trim1 uneval2`) are no longer in RED-M3 at all. Only `atn`/`crlf` remain, and both now carry OTHER classes' signatures (`atn`: uses `ORD`, class #5's family; `crlf`: lowercase terminal `end`, class #1) — both show `(CC)` in RED-M4, the same early-parse-rejection shape class #1/#5 members show, not a runs-to-completion-then-differs shape. Plausible reading: class #4 is now FULLY cured, and its two apparent survivors are mis-attributed (actually class #1 and #5 members) — not proven by ablation this pass, flagged for whoever cures #1/#5 to confirm as a side effect. |
| #5 RC1 CSNOBOL4-extension (8 named: `ord labelcode maxint rewind1 file intval keytrace update`) | not verified uniform; `ord` traced, `labelcode`/`maxint` independently known, `rewind1` separate (stdin-routing) | ✅ `ord`/`labelcode`/`maxint` reconfirmed (all three still invoke their respective unimplemented builtin); `rewind1` reconfirmed as a stdin-routing case. `file intval keytrace update` **still individually unchecked** — same open item Aug 27 left. |
| #6 TIMEOUT/EOF hang (2, `openo2` + 1 unnamed) | confirmed SCRIP defect, most severe class found | ✅ reconfirmed directly: `SNO_LIB=$SUITE timeout 8 ./scrip --run openo2.sno` → rc=124, 1.77MB and still growing when killed. **But this pass's full-suite run scored `m3_HANG=0`** — openo2 is red (FAIL or REJECT, not HANG) in the aggregate board. Read: this is a **timeout-boundary flake**, same load-dependent class SCORE.md already documents for `nqueens` (this box runs 16 concurrent FLEET-16 seats; whether the unbounded-output loop crosses the 8s wall before or after some other resource limit trips depends on available CPU at the moment). The underlying defect (INPUT() never signals EOF failure) is unchanged and still the most severe class here regardless of which specific status label a given run happens to land on. |
| #7 `-INCLUDE` trailing space (2: `line include`) | confirmed SCRIP defect | ✅ reconfirmed (`line.sno`'s target `'line2.sno '` still carries the trailing space, still unresolved) | Unchanged. |
| #8 link-only failure, `setexit7` (RC1/ASM_FAIL) | confirmed SCRIP defect | ✅ reconfirmed (`setexit7` still `(CC)`-tagged in RED-M4 only, not RED-M3) | Unchanged. |
| #9 `nqueens` SIG11 flake | noted, not re-witnessed | ✅ still present | Unchanged; same flake family as #6's timeout-boundary behavior. |
| #10 `scanerr` (RC1/COMPILE_FAIL, "harness bug") | scorecard classification gap, not a SCRIP behavior difference | 🔁 **reclassify, don't re-mint** | Under the CURRENT runner this isn't a harness bug at all: m3 direct run gives `FATAL lower_snobol4 (GZ#5 subset): pattern shape outside the SN4-PAT subset... EVAL and CODE are outside the landed subset`, rc=1 — the identical, already-tracked (`GOAL-SNOBOL4-BB.md`) pattern-matching-subset limitation, and m4's `(CC)` tag is now produced directly from `--compile` failing (no fragile stderr-regex matching in this runner, unlike the old scorecard). Nothing to cure or re-mint; the old "harness gap" framing is moot under the new runner. |

## Part 3 — two NEW classes, not in the Aug 27 FINDING

**NEW-A: `&TRACE` / `&FTRACE` / `TRACE()` diagnostic output is silently a no-op — same shape as the already-known `&DUMP` gap.** Confirmed by direct diff against `.ref` for 5 members: `trace1 t trfunc ftrace trace2`. In every case SCRIP exits rc=0 with **zero bytes of output** where the `.ref` expects several lines of `stmt N: ..., time = xxx`-shaped trace text (the runner's own `normalize()` already masks the nondeterministic `time=` field — these are real content mismatches, not noise). Minimal witness (`trace1.sno`, 7 lines):
```
        &TRACE = 10
        TRACE('foo')
        foo = 1
        foo = 2
END
```
expects 2 lines naming each assignment; SCRIP prints nothing. Same root shape as class #3's `&DUMP`: a keyword/builtin that's accepted (no parse error, rc=0) but whose entire diagnostic-output side effect is unimplemented. A shared-mechanism cure (wherever `&DUMP`'s termination-report hook lives, `&TRACE`/`&FTRACE`/`TRACE()`'s per-statement hook is presumably a sibling gap in the same family) is worth checking before treating these as unrelated.

**NEW-B: `LABEL()` output is duplicated within each statement, and a trailing case is dropped.** `label.sno` (24 lines, uses `LABEL()` combined with a `-CASE 0` directive) — SCRIP prints:
```
foofoo
TESTTEST
ENDEND
BARBAR
```
against expected:
```
foo
TEST
END
BAR
bar
```
Every SCRIP-produced line is the expected line **concatenated with itself** (`foofoo` = `foo`+`foo`, etc.), and the final `bar` entry is missing entirely (4 lines vs. 5). Single witness so far; root cause not traced past the symptom (candidate: `LABEL()`'s result is being written to the output buffer twice, or a concatenation step is applied twice — not investigated further this pass).

**OPEN, not yet classified: `case1.sno`.** Source confirms it explicitly exercises a `-CASE` directive (`-case 1` for case-insensitive mode, later a bare `-case` to switch back) — CSNOBOL4-specific case-folding pragma, distinct from class #1 (SCRIP's fixed uppercase-only `END` recognition) since this is a program-issued MODE TOGGLE rather than a bare lowercase keyword. `label.sno` above also opens with `-CASE 0` — worth checking together, but not run/diffed this pass (viewed source only).

## Part 4 — 21 RED-M3 names not covered by the Aug 27 FINDING at all
`alis case1 convert err float function genc label len repl setexit2 setexit4 spit tab trace1 trace2 trfunc t words1 words` (21). Of these, **6 resolved above** (`trace1 trace2 trfunc t ftrace` → NEW-A; `label` → NEW-B). **15 remain untraced**: `alis case1 convert err float function genc len repl setexit2 setexit4 spit tab words1 words`. Quick source-level notes for whoever picks these up next (sizes/first lines only, no execution yet): `err` (7 lines, `&ERRLIMIT`/`&ERRTYPE`/`&ERRTEXT`) and `float` (6 lines, floating-point `OUTPUT` formatting) are the smallest and likely fastest to ablate; `genc` (1729 lines, "genc.sno from snobol4-1.4.1") is a large multi-feature self-test, not a minimal case, and should probably be triaged last or skipped in favor of the corpus's own smaller programs; `setexit2`/`setexit4` are further `SETEXIT` variants (trap-on-END, `&ERRLIMIT` interaction) distinct from the already-diagnosed class #8 link failure; `words1`/`words` are two variants of the same "word counting" sample program and likely share one root cause.

## Disposition
Reconciliation landed (`.github` `a9e0d686`). Seven classes are well-evidenced enough to file as SNOBOL4 ladder rungs this session (below). Remaining open items — class #2's lowercase/include confound, class #5's four untraced members, class #4's not-yet-ablated hypothesis, `case1`/`-CASE`, and the 15 untraced names in Part 4 — are left for the next walk of this row (task SNO1 `## NEXT`), not guessed at here.
