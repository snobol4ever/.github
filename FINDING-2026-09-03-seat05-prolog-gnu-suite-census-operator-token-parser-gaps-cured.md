# FINDING prolog-gnu-suite-census: operator-token parser gaps found and CURED (two classes)

## TASK
`prolog-gnu-suite-censused-by-refusal-rung-and-builtin-gap-non-ladder-gaps-cured` (FLEET-8, ceo
dispatch, seat05). GOAL: census `corpus/packages/prolog/gnu_prolog` (62 `.pl` files -- GNU Prolog's
own vendored compiler/library source) via `scripts/test_prolog_gnu_suite.sh` into two populations --
(a) ladder refusals (counted by rung, left alone -- rungs are the HQs') and (b) non-ladder gaps (mine),
mint `prolog-gnu-class-<slug>` rows for the latter, cure the largest. Measured on pristine SCRIP
`a3faade17` / corpus `534773170` (post the rung-0..7 construct-ladder rebuild).

## INSTRUMENT FIX FIRST
`test_prolog_gnu_suite.sh` predates the whole construct-ladder rebuild (authored by seat05,
2026-08-30, before rung 0's cut) and had no notion of a ladder refusal (`lower_prolog.c`'s
`pl_refuse()`, rc=2, stderr `"... is not on the ladder yet -- rung N lands it"`): every such refusal
fell into the script's `UNEXPECTED` bucket, which both fails the gate and buries any real non-ladder
gap in noise indistinguishable from expected, already-known ladder gaps. Added a `LADDER` bucket:
rc=2 with that exact stderr shape is tallied by rung (`grep -oP`) and named, counted separately from
`UNEXPECTED`/`OK_FAIL`, sums into the total/`TOTAL` invariant the script already refuses on a
mismatch of. This is the two-population split the task's own GOAL asks for, made structural instead
of manual.

## CENSUS RESULT (post-rebase tree SCRIP `e5c313f7a`, re-measured -- see REBASE note)
```
GNU_SUITE_BOARD total=62 lib=51 ok=1 ok_pass=1/1 ok_fail=0 reject=1 ladder=9 unexpected=0
```
- LADDER=9, never cured here (rungs are the HQs'): rung 7: 2 (`Pl2Wam/ciaolib.pl`
  `Pl2Wam/sicslib.pl`); rung 9: 7 (`BipsPl/all_pl_bips.pl` `Pl2Wam/first_arg.pl`
  `Pl2Wam/indexing.pl` `Pl2Wam/inst_codif.pl` `Pl2Wam/reg_alloc.pl` `Pl2Wam/swilib.pl`
  `Pl2Wam/yaplib.pl`).
  ⭐ **REBASE NOTE**: the census was first measured on `a3faade17` (rung 5: 2, rung 7: 2, rung 9: 5)
  while this row was in flight; mid-session, 10 more commits landed on origin/main including rung 5
  (if-then-else/negation/once/forall/plain-directives, `54536fbf6`) and rung 8
  (findall/bagof/setof, `59bae15c5`). Per this project's own REBASE-BASELINE rule, re-measured on
  the merged tree rather than trusting the pre-rebase numbers: the two former rung-5 files
  (`indexing.pl`, `reg_alloc.pl`) now compile past rung 5 and land on rung 9 instead -- LADDER total
  is unchanged at 9 (same 9 files), only their rung tags moved, which is exactly the expected,
  correct behavior of a live-derived instrument (never a hardcoded list) tracking real upstream
  progress.
- REJECT=1 (`Pl2Wam/compat.pl`): the pre-existing, already-tracked `misc-single-witness-parser-crashes`
  hang-after-parse-error class. NOT re-rowed. `BipsPl/debugger.pl` independently hit the identical
  symptom during the manual LIB compile-probe below (a second witness of the same class) -- noted,
  not re-rowed.
- LIB=51: correctly excluded per the standing hq_C ruling (row
  `prolog-gnu-conformance-ok-fail-print-zero-bytes-both-modes`) -- these are GNU Prolog's own internal
  bootstrap-only library source, not standalone programs with their own oracle. But the harness's
  `is_bootstrap_only()` check never invokes SCRIP on them at all (pure content grep, before any
  compile), so they carry zero coverage from the official board by construction. Manually
  compile-probed all 51 (`--compile`, 10s timeout, same as the harness's own classify step) purely to
  check for front-end crashes the board structurally cannot see -- this is where the two cured classes
  below were found.
- OK=1, OK_PASS=1/1, OK_FAIL=0, UNEXPECTED=0: the one gradeable file passes clean; zero fresh gaps in
  the officially-graded population itself.

## ROOT CAUSE -- two classes minted, both cured in one commit
Compile-probing the 51 never-graded LIB files surfaced 4 files with a genuine
`parse error: expected . at end of fact/clause` (neither the LIB signal nor a ladder refusal):
`BipsPl/consult.pl:333`, `BipsPl/src_rdr.pl:288`, `Pl2Wam/code_gen.pl:686` (reported line; actual
fault one clause earlier, at `685`), `Pl2Wam/read_file.pl:489` (then, once fixed, `:1381`, then
`:1395` -- three further instances of the same family behind the first, all in the same file). All
four trace to `src/parsers/prolog/prolog_parse.c`'s `pt_primary()`: a reserved/symbolic operator token
used somewhere OTHER than its usual operator position has no bare-atom fallback, or a hardcoded
prefix case commits to prefix-application before checking a valid operand actually follows.

- **`prolog-gnu-class-directive-term-as-nested-expression`**: `pt_primary()` had no `case TK_NECK` at
  all. `:-` is lexed as a dedicated `TK_NECK` token (`prolog_lex.c:247`), wired ONLY for the two
  top-level shapes (`:- Goal.` as a whole directive clause, `Head :- Body` infix, both in
  `parse_clause()`). A nested `(:- X)` used as an ORDINARY TERM -- exactly what GNU Prolog's own file
  loader does when reading a directive as DATA, e.g. `Term = (:- Directive)`, or
  `'$treat_term'((:- Directive), OpenFileStack) :- ...` as a clause-head argument -- fell through to
  `default: return NULL`. Standard/ISO Prolog declares `:-` as BOTH `op(1200,xfx,:-)` (infix, already
  handled) AND `op(1200,fx,:-)` (prefix, MISSING). Fix: added the missing case, building a `:-`/1
  prefix compound at precedence 1199 (`fx`, matching the `prec-1` formula every other non-associative
  prefix case in the file already uses), guarded by the pre-existing `prefix_arg_starts()` helper so a
  bare `:-` used as a plain atom (`suspicious_predicate(:-, 1)`) still falls back to `TT_QLIT` instead
  of wrongly consuming a following `,` as its operand.
- **`prolog-gnu-class-symbolic-token-bare-atom-no-fallback`**: two related but mechanistically
  distinct gaps in the same function, found chasing `read_file.pl`'s and `code_gen.pl`'s remaining
  failures after the `:-` fix. (a) The hardcoded `TK_OP` prefix cases for `\+`/`not`/`\` committed to
  prefix-application UNCONDITIONALLY -- unlike the `-`/`+` cases two lines below them, which already
  peek the next token before committing -- so `fast_exp_functor_name(\, 1, 'Pl_Fct_Fast_Not')` wrongly
  consumed its own argument-list comma as `\`'s operand. (b) `TK_COMMA`/`TK_SEMI` (`,`/`;`) had no
  bare-atom fallback path at all -- only the explicit functor-call form `;(A,B)` was handled, so
  `suspicious_predicate(;, 2)` had nowhere to go but `NULL`. Fix: added the same `prefix_arg_starts()`
  guard used for `:-` to (a) (falls through cleanly to the pre-existing generic `TT_QLIT` tail already
  shared by every other `TK_OP` case, once ungated); added an explicit `TT_QLIT` fallback to (b) (no
  generic tail existed to fall through to there).

## FIX
SCRIP `fd3ec8108`, `src/parsers/prolog/prolog_parse.c` (+ the LADDER-bucket instrument addition in
`scripts/test_prolog_gnu_suite.sh`), four call sites in `pt_primary()`, all additive: one new `switch`
case, a boolean guard added to two pre-existing `if` conditions, one new fallback statement. No
existing passing behavior touched by construction (every change either adds a case that did not exist
or narrows an unconditional branch with a check that was already used elsewhere in the same function)
-- confirmed empirically below.

## VERIFICATION
- All four originally-failing files individually re-compiled before/after each incremental change:
  each moves from `parse error` to a legitimate downstream ladder refusal (rung 5, 7, or 9 depending
  on the file) -- never silently "passes" grading, since LIB-classified files stay excluded from
  PASS/FAIL by the pre-existing, unrelated ruling. Minimal repros built and verified for both classes
  independently (a standalone `(:- Directive)`-as-argument witness; a standalone
  `a(\,1,d). a(;,2,e). a(:-,1,f).` witness) before touching the real corpus files, and after, as the
  two rows' own DONE-WHENs (both re-run clean post-fix).
- `test_prolog_ladder.sh --to 4`: 14/14 PASS. `--only 6`: 20/20 PASS. `--only 7`: 4/4 PASS (all three
  required by this task's hard-arms list) -- re-proven on the post-rebase tree.
- `make test`'s full recipe (all 9 arms, each independently re-run on pristine `e5c313f7a` after the
  mid-session rebase -- see ENVIRONMENTAL ANOMALY below for why individually rather than as one
  monolithic invocation): `strip_comments.py --check` 0 violations · `test_gate_capture_stdin_and_red_exit.sh`
  OK · `test_gate_term_wordref_ratchet.sh` OK (0/0) · `test_corpus_snobol4.sh` (run sharded `--shard
  1/8`..`8/8` + `--combine 8`) m3 PASS=1679 FAIL=0, m4 PASS=1679 FAIL=0 SKIP=0, MISSING=0 ·
  `test_gate_emit_no_lang.sh` OK · `test_gate_template_medium_invisible.sh` OK (0 raw-byte producers,
  0 BOTH-MEDIUM sites) · `test_gate_corpus_coverage_classified.sh` OK (every live subtree classified)
  · `test_gate_optbypass_watermark.sh` OK (DEFAULT 0/1656, SCRIP_OPT=0 192/1656 <= watermark 192,
  SCRIP_ZD=0 305/1656 <= watermark 308) · `test_gate_pl_quad_regs.sh` PASS(0) (0 unenrolled r12-r15
  writes, 107 compiled witnesses -- up from 78 pre-rebase, consistent with rung 5/8 adding more
  Prolog witnesses to the ladder tree). Every arm green; no arm skipped or assumed.
- Prolog smoke: `test_smoke_prolog.sh` PASS=5/5 all three modes (m2/m3/m4). Icon smoke:
  `test_smoke_icon.sh` PASS=14/14 both modes (m3/m4) -- change is 100% confined to
  `src/parsers/prolog/`, cannot reach Icon by construction (`parser/` is per-language, downstream
  code never branches on language identity past lower); verified empirically anyway per the
  shared-node discipline.
- `strip_comments.py --check`: rc=0, 0 violations across 384 files (0 comments/blank lines added,
  matches house style).
- `nm -D`: 0 Prolog-only data symbols (`g_pl_*`/`g_plw_*`/`g_resolve_*`/`g_rt_pl_*`/`pl_wot_*`),
  re-checked post-rebase -- the fix is pure control-flow inside two pre-existing functions
  (`pt_primary`, via its already-declared `Token`/`tree_t` locals), zero new file-scope declarations.

## ENVIRONMENTAL ANOMALY -- `make test` (the monolithic target) killed twice, not a verdict either way
Two separate invocations of the monolithic `make test` (one harness-backgrounded, one `nohup`+
`disown`-detached) were externally `Terminated` mid-run, both times inside `test_corpus_snobol4.sh`,
under heavy fleet-wide CPU contention (load average 13-20 on a 16-core box, ~8-10 other seats
building/testing simultaneously post the FLEET-8 mode switch). Per this project's own INSTRUMENT LAW
("an instrument must distinguish MEASURED AND CLEAN from NEVER RAN"), a killed run is NEITHER a pass
NOR a fail -- it is discarded, not counted either way. Worked around by running every one of the 9
constituent arms individually (the SNOBOL4 corpus arm via its own `--shard`/`--combine` mechanism,
built for exactly this), each completing cleanly within a single bounded invocation. All 9 are
independently green, reported above. Recorded here rather than silently omitted.

## NEXT ACTOR
- `Pl2Wam/compat.pl` and now-also-observed `BipsPl/debugger.pl` (hang after parse error, an
  error-recovery defect) stay under the existing `misc-single-witness-parser-crashes` class -- not
  rowed here; second witness noted for whoever owns that row.
- The 9 LADDER refusals are the HQs' (rungs 5, 7, 9) -- not touched, per the fleet's own lane rule.
- One rung-labeling oddity observed in passing, NOT rowed (too minor on its own, flagged for whoever
  owns rungs 7/10 to reconcile): `Pl2Wam/pl2wam.pl`'s refusal reads `"builtin current_prolog_flag is
  not on the ladder yet -- rung 7 lands it"`, but `ARCH-PROLOG-BYRD-BOX-TRANSLATION.md` sec E places
  flags at rung 10 ("the flags ... land HERE with the DB, not as leaves"). Possibly a stale/wrong
  literal rung argument at that one `pl_refuse()` call site in `lower_prolog.c` -- not verified
  further here, out of this row's lane.

## A NAMED DEVIATION
Both fleet task GOALs (this row and its SWI sibling) prescribe curing the largest non-ladder class "as
det leaves in the rung-6 shape" (`PL_CTX_LEAF`/`dop_direct_fp`/the quad scanner's allow-list) -- the
mechanism for wiring a missing or wrong RUNTIME BUILTIN. The largest (only) non-ladder class actually
found in the GNU suite was a PARSER gap, not a builtin-dispatch gap, so that mechanism does not apply;
the cure here is a parser fix instead. Named explicitly rather than silently substituted, per this
project's own rule that an unqualified correction should not quietly inherit a template that does not
fit it.

## LINKS
Task `/home/resources/postoffice/tasks/prolog-gnu-suite-censused-by-refusal-rung-and-builtin-gap-non-ladder-gaps-cured.task.md`
· rows `prolog-gnu-class-directive-term-as-nested-expression`,
`prolog-gnu-class-symbolic-token-bare-atom-no-fallback` (both minted and cured this session) · sibling
row (SWI suite, seat04) `prolog-swi-suite-censused-by-refusal-rung-and-builtin-gap-non-ladder-gaps-cured`
· `ARCH-PROLOG-BYRD-BOX-TRANSLATION.md` sec E (ladder rung table) · `scripts/test_prolog_gnu_suite.sh`
(instrument, this session's LADDER-bucket addition).
