# FINDING — SNOBOL4 xfail census, the 14 "unclassified" remainder: all 14 re-verified against a fresh
build and the swapped oracle, none trusted from their recorded reason alone. 8 held up exactly as written
(and turned out to cite 9 class rows that were NEVER ACTUALLY MINTED despite each xfail reason claiming
"filed to hq_P" — corrected, all 9 now real). 2 did not reproduce their recorded mechanism at all (corpus
fixture gaps). 1 was mischaracterized (wrong root cause cited). 1 confirmed correctly waiting on an
unrelated tracked dependency. 1 confirmed a genuinely unrecoverable fixture gap.

**seat15 (`/home/claude15`, Claude Sonnet 5), 2026-09-05, THE LOOP row
`snobol4-xfail-class-14-unclassified-reasons-censused-and-named` (hq_T). Tree: SCRIP `b35ddccbc`, corpus
`4e47d9100` (both pulled fresh this session), oracle the 18:19 CDT 2026-09-04 swap (SIGSEGV-on-exit cure).**

## Headline

The task's own law (Lon 2026-09-03 21:30, quoted in the row's GOAL): "there is no such thing as XFAIL — an
xfail is either a faulty test to fix or a defect to cure, never a resting state." The 14 entries handed to
this row were the remainder of a 61-entry reasoned-xfail census that keyword-matched into 8 named classes;
these 14 matched none of the 8. Re-reading each reason and re-running each entry (both modes, current
build, current oracle — never trusting the recorded belief) surfaced two classes of problem beyond simple
classification: (a) a **systemic filing gap** — 9 of these defects (including 1 shared with an existing,
mis-scoped census bucket) had been diagnosed and *named* in a prior session's FINDING but never actually
`mint`ed as work, so they were invisible to anyone who didn't happen to read that FINDING's prose; and
(b) **real drift** — the compiler and the oracle both changed today, and at least 3 of these 14 no longer
behave as recorded, in ways ranging from "the exact fixture can't even be reached" to "the crash signature
changed shape."

## Method

`git pull --rebase` all three repos, `make` (incremental), then for each of the 14: extract via
`corpus_suite_harness.py extract` into an isolated scratch dir, run mode-3 and mode-4 under `timeout 8s`,
run the oracle (`sbl_correctness_bin()` + `sbl_lang_flags()`, never hand-rolled) on the same extracted
input, diff all three against each other and against `.ref`. No `corpus/`/`.github` file was touched by any
extraction or run — all scratch work lives under a session-local temp directory, referenced by `SNO_LIB`
where a diagnostic repair needed to resolve a broken `-INCLUDE`. Cross-checked every "filed to hq_P as
class row X" claim in the recorded reasons directly against `postoffice/tasks/` and `QUEUE.tsv`/
`QUEUE.done.tsv` before trusting any of them.

## 1. EIGHT REAL, DISTINCT DEFECTS — recorded reasons held up exactly, but "filed to hq_P" was never true

Every one of these was diagnosed and named in `FINDING-2026-09-03-seat08-snobol4-master-xfails-reasoned-70-
of-70-2-cured-14-new-classes-filed.md` sec4 — whose own sec7 says, in its own words, these class rows are
"ready to mint... not filed as queue rows." That caveat did not survive into the xfail reasons themselves,
which each say flatly "filed to hq_P as class row X." Checked directly: zero of the 9 named rows below
(8 here + 1 in §3) existed anywhere in `postoffice/tasks/` or `QUEUE.tsv`/`QUEUE.done.tsv` before this
session. All 8 below are unchanged from their 2026-09-03 characterization, re-verified against today's
build + oracle, and now actually minted (owner `hq_P`, rank 3):

| entry | class row (now minted) | mechanism |
|---|---|---|
| `simple_output_61` | `parser-scans-past-end` | label-scan continues past a valid END; two trailing lines spuriously duplicate-label |
| `simple_output_62` | `input-open-failure-not-signaled` | INPUT() open failure never signaled; S(loop) hangs forever, both modes |
| `user_function_replace_4` + `_replace_7` | `define-redefinition-ordering` | re-DEFINE resolved as hoisted/declarative; a later DEFINE retroactively changes an earlier call's already-printed output |
| `user_function_replace_6` | `omitted-leading-arg-shift` | `F(, 'y')` shifts args left instead of leaving a gap |
| `indirect_replace_1` | `indirect-store-through-field-name` | `P=.R(X)` then `$P=...` is a silent no-op |
| `user_function_indirect_replace_1` | `goto-function-call-parse-error` | `:(GO())` is a parse error; oracle compiles/runs it (STATEF.inc contract) |
| `user_function_code_eval_array_replace_branch_1` | `indirect-loop-var-plus-code-indirect-goto-segv` | CODE()-indirect-goto loop + indirect loop var SIGSEGVs on exit after correct partial output |

## 2. TWO ENTRIES WHOSE RECORDED MECHANISM DOES NOT CURRENTLY REPRODUCE — corpus-hygiene, not compiler defects

`simple_output_68` and `simple_output_70` (both `probe_gimpel` origin) fail to even reach their recorded
mechanism as extracted: both scrip AND the oracle fail identically with "cannot open include" — not an
oracle differential, a broken fixture.

- **`simple_output_68`** (`gim_double_include_hang`): on-disk fixture is `gim_double_include_hang_A.inc`;
  the source's own `-INCLUDE` names `gim_double_include_hang_A.sno` — an extension mismatch. Diagnostic-
  only repair (scratch copy, never committed): once the include resolves, output is CORRECT with NO hang.
  The recorded "including the same file twice hangs scrip" does not reproduce even when made reachable.
- **`simple_output_70`** (`gim_or_single_alternative_crash`): `-INCLUDE 'OR.sno'` is not beside the witness;
  the real file is `corpus/packages/snobol4/gimpel/OR.sno`. Diagnostic-only repair (`SNO_LIB` pointed at the
  real dir): once `OR.sno`/`BALREV.sno` resolve, `OR(LIST)` with one alternative now fails with a
  **deterministic, cleanly-caught "ERROR 246 — stack overflow"**, both modes, 3/3 reproductions each — NOT
  the recorded nondeterministic raw SIGSEGV/SIGABRT flip. Likely explanation: `src/runtime/rt/
  rt_stack_overflow.c`'s stack-guard-page SIGSEGV handler (classifies as ERROR 246) postdates the original
  2026-09-03 characterization — the crash is tamed at the observability layer, but whether a single-
  alternative `OR(LIST)` should recurse this deeply at all is still an open, real question.

This is the **third** independently-discovered instance of "gimpel-origin `-INCLUDE` broken in the flat
master" — after `gimpel_triage` (7 witnesses, owned seat06) and an unnamed 5-witness set in
`FINDING-2026-09-03-seat08` sec3 — 14 witnesses now, across three uncoordinated namings. Minted
`gimpel-probe-witness-include-path-unresolved` (owner `hq_T`, rank 3) rather than guess at the fix myself;
whoever picks it up must re-characterize both witnesses from scratch once the paths are fixed, since neither
witness's recorded behavior is currently demonstrated.

## 3. ONE ENTRY, SAME MECHANISM AS AN EXISTING (MIS-SCOPED) CENSUS BUCKET

`keyword_replace_branch_11`'s own reason cites the identical hq_P class-row name as `keyword_replace_branch_10`
("setexit-not-invoked-under-errlimit-survival"), and `FINDING-2026-09-03-seat08` sec4 item1 independently
confirms both as 2-of-4 original witnesses of ONE mechanism (the other two, `keyword_replace_1`/`_2`, have
since left `ALL.xfail` entirely). Despite this, hq_T's own census bucket task
(`snobol4-xfail-class-setexit-errlimit-composition-2-entries`) currently pairs `keyword_replace_branch_10`
with `size_indirect_keyword_replace_branch_1` instead — a DIFFERENT, unrelated s194
"indirect-nonname-silent-accept" NUL-byte-namespace pin that only shares the words SETEXIT/&ERRLIMIT in
passing. Flagged to hq_T (`setexit-census-bucket-membership-wrong`) rather than edited directly (their
claim, not mine).

Behavior has also **drifted** since 2026-09-03: re-run today, `keyword_replace_branch_11`'s m3 and m4 are
now IDENTICAL (the recorded "m4 refuses to compile" mode-divergence is gone), and the first handler
("HANDLER S4") now DOES fire once (contra "neither... fires") — but the handler's own `:(CONTINUE)` resume
statement is treated as a literal undefined label rather than SPITBOL's resume-point pseudo-target, so each
attempted resume re-triggers the handler until `&ERRLIMIT(10)` exhausts and the program goes fatal
("Error 38... transfer to undefined label: CONTINUE"), both modes now identical. `keyword_replace_branch_10`
itself was NOT re-run fresh this session — its recorded reason predates today's changes and should not be
trusted without a fresh check. Minted `setexit-not-invoked-under-errlimit-survival` for real (owner `hq_P`,
rank 3), citing both live witnesses and the drift.

## 4. ONE ENTRY MISCHARACTERIZED — wrong root cause cited, real mechanism identified

`user_function_array_replace_branch_1`'s recorded reason cites "queue row `subscript-silent-accept`" as the
cause. That citation was itself a **phantom reference** (never minted — independently confirmed the same
day by seat08, who found the real subscript mechanism separately and minted it as
`snobol4-subscript-undeclared-operand-not-detected`, a genuinely different defect this witness does not
exercise). Reading the witness's own extracted source settled it: its header comment is near-verbatim
identical to the `vlist-expr-alternation` task's own brief — this is the SPITBOL parenthesised-comma-
expression-alternation (`TT_VLIST`) family, not a subscript defect. `subscript-silent-accept` only
described how the bug was originally *exposed* (a subscript-behavior change made it visible), never what it
*is*.

Re-run today: m3 gives wrong output on 2 of 11 lines (side-effect-suppression semantics of the alternation
— not a clean "only element 1 evaluated" shape, so the `SCRIP_VLIST_ALT` partial fix from
`vlist-expr-alternation`, default OFF, may not even cover this witness's exact shape). **M4 now SIGSEGVs
(rc=139)** — wholly undocumented by the original reason. The construct (nested `IR_DISJUNCTION`-producing
parenthesised alternation with side-effecting arms) matches the exact witness family of the long-running,
HQ-only "Defect C" tracked at `vlist-v05-m4-sigsegv-m3-m4-divergence` / `defect-c-zop-flat-regime-depth-
compensate` (x86_zop flat-regime raw fallback, no depth-compensation from inside an outstanding carve —
still open as of that row's last entry read this session). Flagged to hq_C
(`vlist-new-witness-user-function-array-replace-branch-1`) as a corroborating witness rather than
re-derived — CEO-19 HQ-only codegen lane. No mint: already tracked, just previously mis-attributed.

## 5. ONE ENTRY CONFIRMED CORRECTLY WAITING

`trim_alt_keyword_replace_branch_1` is a self-pinned instrument for `lang-lambda-pattern-primitives`
(confirmed real, minted, rank 3, currently PARKED under today's SNOBOL4-only mode — correctly so). It is
NOT the same shape as either neighboring bucket it superficially resembles: not
`unimplemented-feature-gaps-ord-and-dump` (ORD/&DUMP are real, oracle-comparable gaps in existing SPITBOL
features), and not `size_indirect_keyword_replace_branch_1`'s SETEXIT/namespace pin. Freshly confirmed
distinguishing property: the oracle **cannot run this witness at all** (`sbl -bf`: "ERROR 230 — syntax
error: illegal character" on the literal λ/Λ glyphs, rc=231) — there is no oracle diff to ever grade
against, until `lang-lambda-pattern-primitives` lands. No action needed beyond this classification.

## 6. ONE ENTRY CONFIRMED A GENUINELY UNRECOVERABLE FIXTURE GAP

`user_function_eval_span_replace_branch_1`: `ALL.in` carries no stdin block for this entry at all
(grep-confirmed absent). scrip (both modes) AND the oracle all produce EMPTY output, rc=0, against
`/dev/null` — `line = INPUT :F(END)` fails immediately in every tool alike, a trivial three-way agreement
that verifies nothing. The `.ref`'s 168 lines of "255" were captured against real multi-line
arithmetic-expression input that no longer exists anywhere in the corpus (its cited source,
`crosscheck/control/expr_eval.sno`, was retired in the crosscheck-to-tests conversion). No pass/fail verdict
is possible without the lost input. This needs a fixture owner to reconstruct plausible input from the
`.ref`'s shape, or retire the `.ref`'s expectation — not a compiler fix, and not minted (no existing row
owns "ALL.in fixture gaps" generically; flagging here rather than inventing one for a single instance).

## 7. CORPUS.XFAIL EDITS

All corrected reasoning written directly into `corpus/tests/snobol4/ALL.xfail` — 18 reason lines touched
(the 14 above plus 4 cross-referenced neighbors: `simple_output_64`, `keyword_19`,
`keyword_replace_branch_10`, `size_indirect_keyword_replace_branch_1`, each given a one-line pointer to the
correct class-row name or a mis-pairing warning). Zero banner lines touched, zero entries deleted, zero
refs re-cut. Verified structurally identical before/after: 61 banners, 61 unique names, 122 lines.

## 8. SUGGESTED NEXT

- 9 freshly-minted rows (owner hq_P ×8, hq_T ×1, all rank 3) are ready to pick up — no re-derivation needed,
  each cites its witness(es) and current behavior directly.
- hq_T should correct the SETEXIT-2 census bucket's membership (message sent).
- hq_C/hq_P should treat `user_function_array_replace_branch_1` as a new Defect C witness if convenient
  (message sent); not blocking, not re-derived here.
- Whoever owns corpus fixture hygiene should look at all three known "gimpel `-INCLUDE` broken in the flat
  master" sets together (gimpel_triage 7 + seat08's unnamed 5 + this session's 2 = 14) rather than as three
  separate small fixes — flagged, not actioned, per this row's own "census, not cure" scope.
- `snobol4-xfail-class-14-unclassified-reasons-censused-and-named` itself stays open: its DONE-WHEN
  correctly still requires all 14 to actually go green, which is now real, dispatchable work instead of an
  invisible prose claim.
