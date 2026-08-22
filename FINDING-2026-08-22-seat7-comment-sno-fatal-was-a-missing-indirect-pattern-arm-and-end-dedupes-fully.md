# FINDING 2026-08-22 (seat7) — row `lower-fatal-bombs-two`: bomb 1 was a missing TT_INDIRECT arm (found, fixed, verified); bomb 2 dedupes 100% to `end-only-program-aborts`

Queue row `lower-fatal-bombs-two` (rank 0), brief: two compiler FATALs on `csnobol4-suite` programs the live oracle runs cleanly. Row's own DONE-WHEN: each bomb NAMED with a minimal witness (fix optional, dedupe mandatory for bomb 2).

## Bomb (1) — `comment.sno`: `FATAL lower_snobol4 (GZ#5 subset): pattern shape outside the SN4-PAT subset`

**Root cause, named exactly.** `comment.sno`'s `TEST` subroutine matches `STR $PAT` — the pattern operand of a `TT_SCAN` statement is a bare indirect reference (`$PAT`), AST shape `TT_INDIRECT(TT_VAR PAT)` (confirmed via `--dump-ast`). `lower_snobol4.c`'s pattern dispatch (`sno_pat_supported()` line 1616, `sno_is_pattern_rhs()` line 1644) has no case for `TT_INDIRECT` — both fall to their default `return 0`. The one escape hatch, `sno_lower_match`'s materialize-then-defer-scan fallback (line 1926-1943, entered when `!sno_pat_supported(ptt)`), only admits `ptt->t == TT_FNC || sno_is_pattern_rhs(ptt)` — `TT_INDIRECT` is neither, so control falls through to `sno_fatal(...)` at line 1943. This is a **shape refusal**, exactly what RULES' NO-DENY LAW (ARCH-PASSTHRU 0d: "A failure case is never denied … Stop the world, minimize, fix it") names as forbidden.

**Minimal witness (checked in, oracle-verified both directions):** `corpus/probe/indirect/indirect_pattern_operand.sno` + `.ref`. Reduced further than `comment.sno` needs: no `DEFINE`/subroutine at all — `pattern_name = .vowel_set` (binds a NAME-datum, the `.X` unary "name-of" operator, grammar rule `T_1DOT expr14 → expr_unary(TT_NAME, …)`) then `sample $pattern_name` as the scan pattern — same critical AST shape (`TT_INDIRECT(TT_VAR pattern_name)`) as `comment.sno`'s `$PAT`, exercising both the match-success and match-fail exits. An even smaller scratch reproducer (`PAT = 'A'` then `'A' $PAT`, 2 statements) confirms the trigger needs nothing but the bare shape, but wasn't checked in since it degenerates to a trivial empty-pattern match rather than exercising a real stored pattern.

**The fix, one line, `src/lower/lower_snobol4.c` (the only file touched):**
```c
-                if (ptt && (ptt->t == TT_FNC || sno_is_pattern_rhs(ptt))) {
+                if (ptt && (ptt->t == TT_FNC || ptt->t == TT_INDIRECT || sno_is_pattern_rhs(ptt))) {
```
Widens the admission to the already-existing fallback, which was already the correct mechanism for "the pattern is a runtime-computed value, not a literal shape" (it materializes the operand via `sx_lower` into a temp var, then re-lowers as a `TT_DEFER`-wrapped scan). `sx_lower`'s own `TT_INDIRECT` case (line 347) already implements indirect-reference evaluation correctly and generically — it is exercised successfully elsewhere in this same file for indirect assignment targets, indirect goto targets, etc. — so this reuses proven machinery rather than adding a new mechanism, and touches no codegen/template/x86 code at all.

**Verified, both modes, against the live oracle and the pinned `.ref`:**
- `comment.sno`: m3 and m4 both now PASS, byte-identical to `comment.ref` AND to a fresh live-oracle run (`x64/bin/sbl -bf`).
- `corpus/probe/indirect/indirect_pattern_operand.sno`: m3 and m4 both PASS, byte-identical to a fresh oracle run.

**Regression sweep, named not just counted.** Full A/B: baseline (fix stashed) vs. fixed, same build, same 5 suites (`csnobol4_suite,crosscheck,patterns,bb_probes,probes_misc`, 1393 rows), joined on `(suite, program)` and diffed by status column — only **4** rows differ anywhere:
| row | before (m3/m4) | after (m3/m4) | verdict |
|---|---|---|---|
| `csnobol4_suite/comment.sno` | RC1 / COMPILE_FAIL | PASS / PASS | the fix, as intended |
| `probes_misc/altdepth/alt_twochoice_defer_red.sno` | PASS / PASS | SIG11 / PASS | **pre-existing flake, not caused by the fix** — see below |
| `probes_misc/eval/ev_code_end_terminates.sno` | PASS / SIG11 | PASS / TIMEOUT | already-red both ways; m3 stable PASS in 5/5 runs on both builds. Its m4 crash is the already-tracked row `eval-code-end-terminates-m4` (HQ's own s194 ruling, same session, independently reproduces on a clean tree with no patches at all) |
| `probes_misc/fuzz/fz_segv_03.sno` | SIG4 / SIG11 | SIG11 / SIG11 | already-red both ways (it's a fuzz-crash witness by name); m3 crash SIGNAL flavor alone changed |

`alt_twochoice_defer_red.sno` was run 5× on the unmodified baseline binary (no fix present at all): **1 of 5 SIGSEGV'd**, confirming the crash is independently nondeterministic and exists with or without this change (re-run 8× on the fixed binary: 3 of 8 SIGSEGV'd — same order of magnitude, no jump). `fz_segv_03.sno` gave SIG11 5/5 on the same unmodified baseline binary in a follow-up check, i.e. its crash SIGNAL alone is nondeterministic too (SIG4 vs SIG11 both observed on the identical unpatched binary). Neither file's construct (choice-depth/ARBNO-alternation and a named fuzz witness) has any structural relationship to `$`-indirection or pattern dispatch. **Net: zero real regressions; one genuine fix.**

Additionally checked, all zero-delta: `beauty_self` self-host (`scrip beauty.sno < beauty.sno`, both modes, md5 `6f1671c0757729992ae01a6bdf16f081` — unchanged, Milestone 1 intact), `beauty_suite` (17/17 both modes, unchanged), `demos` (18/23 m3, 17/23 m4, byte-identical failure-class counts before/after — a pre-existing standing red, untouched). All six `util_regen_*_s_artifacts.sh` regen scripts (benchmark/feature/demo/programs/prolog_bench/crosscheck — the full chain RULES.md requires for any `lower_snobol4.c` touch) report **zero `.s` bytes changed anywhere in the corpus** — no program outside `comment.sno`/the new probe exercises this shape.

## Bomb (2) — `end.sno`: `[IBB] FATAL: mode-3 driver: main BB graph not found`

**Dedupe verdict: FULL DUPLICATE of the already-claimed row `end-only-program-aborts` (owned by seat5, `postoffice/claims/end-only-program-aborts.claim`). Not fixed under this row — out of scope for a claim I don't own.**

`corpus/programs/csnobol4-suite/end.sno` is byte-for-byte identical to `preload1.sno`..`preload4.sno` — all five files are exactly `END\n` (4 bytes, verified via `cat -A`). Same FATAL, same mechanism: `src/driver/scrip.c`'s mode-3 block initializes `main_bb_idx = -1` (line 1586) and only assigns it when a proc table entry named `"main"` is found (line 1606); a program with zero statements before `END` never creates one, so `main_bb_idx` stays `-1` and the FATAL/`abort()` fires at line 1670-1672. This is exactly the mechanism `end-only-program-aborts`'s own text names ("whatever scrip does before it has any statement to compile is doing it wrong").

**One corroborating detail for whoever lands `end-only-program-aborts`:** `end.ref` is **already correct** — 0 bytes, matching the oracle's correct 0-byte output for a bare-`END` program — unlike `preload1-4.ref` (3-6 bytes, already named as wrong pins in that row's own text and slated for deletion). `end.sno`/`end.ref` should be folded in as a fifth witness needing no ref repair, only the driver fix. Sent to seat5 (claim owner) and hq via `s4e_msg.sh send`/`ask` for the board record.

## Corpus fail-set: no worse

Full-suite deltas named above (4 rows, 1 real fix + 3 confirmed-pre-existing flakes). No suite's scoreable pass count dropped from this change; `csnobol4_suite` gained exactly the one row this row targets.

## Files touched

- `SCRIP/src/lower/lower_snobol4.c` — the one-line fix (only source change this session), commit `8c0d8ca2`.
- `corpus/probe/indirect/indirect_pattern_operand.sno` + `.ref` — new minimal witness for bomb 1, commit `8934655a`.
- This FINDING; `GOAL-SNOBOL4-100.md` LIVE CURSOR moved.

## Addendum — mid-session upstream landing: bomb (2) fixed by its rightful owner, plus a large unrelated regen sweep

`git pull` on SCRIP conflicted (fast-forward refused) partway through this session: seat5 had independently landed **`f7c25eb6` "fix: END-only SNOBOL4 program aborts in m3, fails compile in m4"** — deleting `lower_snobol4.c`'s `if (nst == 0) return &g_stage2;` early-bailout, which is exactly the mechanism this FINDING's bomb-2 section root-causes (zero statements before `END` ⇒ no `"main"` proc entry ⇒ `main_bb_idx` stays `-1` ⇒ the FATAL). The two changes (mine at line ~1927 inside `sno_lower_match`, seat5's at line ~2317 inside `lower_sno_stage2`) are in unrelated regions and auto-merged with zero conflicts (`git stash` / `git pull` / `git stash pop`).

Five more commits landed in the same pull (`0f17fbf4` descr-stamp-fields, `ff84322c`/`0ff71be8` free-r11/free-r10, `483d8849` strtab_intern fix, `8c1f2d41` byname-bake-cell-address) — all legitimate, separately-claimed rows, none touching pattern lowering. Re-ran `make pristine` and all six `util_regen_*_s_artifacts.sh` against the merged tree as required (`lower_snobol4.c` was touched): this surfaced **large pre-existing regen debt from those five commits** (benchmarks 15/15 changed, demo 19/19, icon/prolog/rebus programs 623/623, prolog bench 19/22, crosscheck 286/488) — confirmed NOT attributable to this row: the scale (every emitted instruction, all three unrelated languages) is structurally impossible from a SNOBOL4-only pattern-dispatch change, and a spot check of the one suspiciously on-topic-sounding file (`test/snobol4/patterns/056_pat_star_deref.sno`) showed it uses the unrelated `*` (unevaluated-expression / `TT_DEFER`) operator, not `$` (`TT_INDIRECT`). Committed anyway per this project's own precedent (s169/s192: a regen sweep is fleet-wide housekeeping, not scoped to the sweeping session's own change) but named here so it is not mis-attributed to `lower-fatal-bombs-two`.

**Final watermark, merged tree (SCRIP `8c0d8ca2`, corpus `8934655a`):** `csnobol4_suite` 52/52 → **58/58** (m3/m4) — the +1 from this row's fix (`comment.sno`) plus +5 from seat5's now-merged fix (`end.sno` + `preload1-4.sno`, all previously SIG6/COMPILE_FAIL). `crosscheck` 199/199 and `patterns` 121/120 unchanged (same one pre-existing `PASS/ASM_FAIL` + one pre-existing `SIG11/SIG11`, present before either fix). Re-verified `comment.sno`, the new probe witness, and `end.sno` all PASS both modes, oracle-identical, on the final merged+rebuilt binary.
