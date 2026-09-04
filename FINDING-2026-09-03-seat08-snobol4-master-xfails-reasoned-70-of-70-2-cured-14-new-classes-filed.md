# FINDING — SNOBOL4 master xfails: every entry reasoned, 2 fixture bugs cured, 14 new defect classes filed, 1 gap in the list itself closed

**Date:** 2026-09-03 (~19:30-20:20 CDT) · **Seat:** seat08 (FLEET-16, hq_P lane) · **Row:** `snobol4-master-xfails-reasoned-or-cured` (SNO4, minted CEO-175)

## Headline

Every xfail entry in `corpus/tests/snobol4/ALL.xfail` now carries a real reason. Task's own DONE-WHEN
(no "not further diagnosed"/TODO/unknown-reason text anywhere, every XFAIL banner immediately followed
by content) passes, exit 0. Along the way: **the list itself was short one entry** — `simple_output_63`
(seq 1670) carried an XFAIL banner in `ALL.sno`/`ALL.ref` with **no corresponding line in `ALL.xfail` at
all** (silently legal per the sidecar's own "absent = no reason, never an error" rule, but it meant the
task's stated "70 entries" was actually 69 measurable + 1 invisible — now 70 total, all reasoned). Two
entries were **cured outright** (fixture bug, not a SCRIP defect) and promoted out of the list entirely.

## Method

Re-ran every one of the 69 named `ALL.xfail` entries in both modes via `corpus_suite_harness.py`'s own
`run_m3`/`run_m4` (the harness's ONE AUTHORITY, not a hand-rolled compile/link recipe), against a fresh
incremental build (`make`, RT_OPT=-O0, per the pristine-loosening ruling) after `git pull --rebase` on
all three repos (SCRIP 7 commits behind, corpus 7, .github 19). Grouped by `(m3_kind, m4_kind)` verdict
pair, then by the master CSV's own `origin`/`family` columns, which cleanly separated the 69 into real
families (`gimpel_triage_*`, `probe_gimpel`, `probe_csnobol4_triage`, `probe_setexit2`, `probe_fuzz`/
`probe_loose_fuzz`, `probe_passthru`, and singletons) — most of which turned out to already carry
extremely precise, pre-written root-cause comments in their own source (a previous session's diagnostic
work, never transcribed into `ALL.xfail`'s reason sidecar).

## 1. TWO FIXTURE BUGS CURED — entries left the list

**`tab_trim_size_replace_1` / `tab_trim_size_replace_2`** (KW-1/KW-5b `&TRIM` witnesses): both read via
`INPUT` in a loop; both header comments name an exact required input (`"hello   "` then `"world<TAB>"`).
The master's `ALL.in` stdin sidecar had **no entry for either** — they were silently running on empty
stdin, producing `[]`/`size=0` instead of the documented behavior. Added the two missing stdin blocks to
`ALL.in` (exact content from the witnesses' own comments); both now **PASS m3 AND m4, and PASS all three
optimizer-bypass arms** (default, `SCRIP_OPT`, `SCRIP_ZD` — `util_census_optimizer_bypass.py --only`).
Promoted per the INTERIM PROMOTION PROTOCOL (`lib_master_extract.sh`): ` XFAIL` removed from the matching
banner in **both** `ALL.sno` and `ALL.ref` in the same commit as the `ALL.in` fix, reason lines removed
from `ALL.xfail`, `corpus_suite_harness.py list` re-run on the result (1736 entries, rc=0) to prove the
master still reads cleanly. This was a fixture-level absorption gap (loose-file `.dat` companions never
carried into the flat master's `.in` sidecar), not a SCRIP defect — exactly the class of red hq_P's brief
authorized this row to cure directly.

**Related, NOT cured:** `user_function_eval_span_replace_branch_1` (perf-characterization witness,
FINDING-2026-08-22-m3-run-only-is-alpha-cell-scan-pollution.md) has the identical shape (reads `INPUT` in
a loop, no stdin in `ALL.in`) but its cited source (`crosscheck/control/expr_eval.sno`) no longer exists
at that path, so the exact original multi-line input isn't recoverable from the witness alone — flagged
in its reason line, not guessed.

## 2. THE LIST'S OWN GAP — `simple_output_63`

XFAIL-flagged in `ALL.sno`/`ALL.ref` (seq 1670) but **absent from `ALL.xfail` entirely** — not even a bad
placeholder line, just missing. This is the exact witness named in `corpus_suite_harness.py`'s own
`classify()` comment (the "positive rc without declared `want_rc`" bug: a program that cannot compile was
scoring PASS on empty==empty text match). Its own header comment is already excellent: lowercase `end`
(SCRIP requires uppercase, RULES.md) is rejected identically by scrip AND the `sbl -bf` oracle — corpus
dialect, not a SCRIP-only defect; `util_uppercase_keywords.py` already exists to normalize this
corpus-wide but has not been run. Added the missing banner+reason block to `ALL.xfail` at its correct
sorted position (between seq 1669 and 1671).

## 3. CORPUS-HYGIENE GAPS (not SCRIP defects) — stale paths masking already-known bugs

Three `gimpel_triage_*` entries' absorption into the flat master carries their ORIGINAL `-INCLUDE` text
verbatim, but the referenced companion files were renamed (prefixed `gimpel_triage_`) during the
tests/snobol4 flatten — the includes now resolve to nothing, so these entries fail at "file not found"
instead of reaching the mechanism `FINDING-2026-08-27-seat10-gimpel-triage-eight-symptom-classes-ranked.md`
already root-caused:

| entry | class | masked mechanism (already known, FINDING rank) |
|---|---|---|
| `simple_output_93` | class1 | duplicate-label parse error, no include-guard (rank1) |
| `array_replace_2` | class5 | `CODE()`+indirect-goto SIGSEGV (rank5) |
| `array_replace_branch_2` | class8 | workspace-heap exhaustion, self-`DEFINE` recursion (rank8, two-level include) |

Two more one-off fixture issues, same flavor:
- `simple_output_186` (rtx_func_11): `-INCLUDE 'rtx11_dynvar.inc'` names a file absent from the **entire**
  corpus tree (not just renamed — genuinely gone).
- `arbno_span_len_replace_branch_1` (gim_fortput_m4_only_segv): `-INCLUDE` hardcodes a **seat-specific
  absolute path** (`/home/claude4/corpus/programs/gimpel/FORTPUT.sno`) — a D-17 PORTABLE-HOME violation.
  The real file lives at `corpus/packages/snobol4/gimpel/FORTPUT.sno` on every seat. This witness's own
  header says the SIGSEGV it guards against is **already fixed** (SPAN-FRAME, s188/d3251f23) — so the
  regression guard currently can't fire either way, for a reason unrelated to the bug it exists to catch.

None of these five were fixed this session (portable include-path resolution for a witness absorbed into
the flat master needs more care than a one-line rename — same root tension the KEEP.md doc already
documents for the gimpel_triage family generally). Flagged precisely rather than guessed at.

## 4. REAL DEFECTS, NEWLY CHARACTERIZED — 14 class rows for hq_P

Ablated witnesses already sit at their named entry in `ALL.sno` (extract via `lib_master_extract.sh
master_extract_name <name> <out.sno>`); none required more than reading source + re-running both modes.
No `src/` edits made (per brief: cure only fixture/xfail/instrument-level reds; hand the rest to hq_P).

1. **`setexit-not-invoked-under-errlimit-survival`** — witnesses `keyword_replace_1`, `keyword_replace_2`,
   `keyword_replace_branch_10`, `keyword_replace_branch_11` (ONE mechanism, 4 witnesses): when `&ERRLIMIT`
   is set nonzero and survives an arithmetic runtime error (division by zero), an armed `SETEXIT(.H)`
   handler is **never invoked** — execution silently falls through past the failing statement instead of
   routing to `H`. `keyword_replace_branch_10`/`_11` additionally show an m3/m4 divergence (m4 refuses to
   compile the shape at all).
2. **`errlimit-alone-does-not-survive-undefined-function`** — `keyword_replace_branch_9`: distinct from
   (1) — `&ERRLIMIT` with no `SETEXIT` anywhere does not make an "undefined function called" error
   survivable at all (whole program aborts instead of taking the statement's own `:F` branch).
3. **`define-redefinition-ordering`** — `user_function_replace_4`, `user_function_replace_7`: re-`DEFINE`
   is resolved as if declarative/hoisted rather than an ordered runtime statement — a LATER `DEFINE`
   retroactively changes what an EARLIER (already-executed) call printed.
4. **`parser-scans-past-end`** — `simple_output_61`: SCRIP keeps label-scanning text physically after a
   valid `END`; two identical trailing data lines trigger a spurious duplicate-label error. Root cause of
   `csnobol4_suite/sudoku.sno`.
5. **`input-open-failure-not-signaled`** — `simple_output_62`: `INPUT()` on a file it cannot open never
   signals failure; the `S(loop)` branch keeps succeeding forever (infinite loop). Root cause of two real
   suite timeouts (`openi`/`openo2`).
6. **`omitted-leading-arg-shift`** — `user_function_replace_6`: an omitted LEADING call argument,
   `F(, 'y')`, shifts remaining arguments left instead of leaving a gap (`'y'` lands in the first param).
7. **`indirect-store-through-field-name`** — `indirect_replace_1`: `P=.R(X)` then `$P=...` (indirect store
   through the name of a DATA field) is a silent no-op; the same idiom over a plain variable works.
8. **`goto-function-call-parse-error`** — `user_function_indirect_replace_1`: `:(GO())` (a goto whose
   operand is a function call) is a parse error; ordinary direct and indirect gotos both work fine.
9. **`deferred-array-element-capture-target`** — `break_len_array_replace_1`: a conditional assignment
   whose target is a deferred array element (`*A<I>`) captures nothing, no diagnostic, rc=0.
10. **`indirect-loop-var-plus-code-indirect-goto-segv`** — `user_function_code_eval_array_replace_branch_1`:
    a `DEFINE`d function reaching its loop variable indirectly through a name argument, combined with a
    `CODE()`-compiled indirect-goto loop, SIGSEGVs on the way out — each ingredient alone is correct
    (both siblings proven green in the same witness file).
11. **`opsyn-missing-hash-operator-char`** — `opsyn_replace_branch_1`: `OPSYN('#','DIFFER',2)` (manual
    p.116 worked example) fails to parse at all — `#` isn't in scrip's recognized operator-character set.
12. **`opsyn-unary-dispatch-wrong-char`** — `opsyn_any_capture_replace_1`: an OPSYN'd unary operator
    (`!X` as `ANY(X)`) matches the wrong character when scanning (`'ABC321' ? !'3C'` should land on `'C'`
    at position 3, returns `'3'` instead).
13. **`eval-chained-defer-no-expression-datatype`** — `eval_defer_3`: `a=*(1+2); b=*a; EVAL(b)` doesn't
    reach the `EXPRESSION`-datatype answer the oracle gives.
14. **`arbno-rpos-keyword-pattern-parse-error`** — `user_function_arbno_rpos_1`: genuine parse error
    ("missing END statement") on a deferred pattern assignment to a keyword-shaped variable containing a
    function call inside `ARBNO(*subject)`. Symptom confirmed only; grammar-level root cause not bottomed
    out this session.

## 5. ALREADY KNOWN, RE-CONFIRMED, NOT RE-DIAGNOSED

- `span_replace_1`, `span_replace_2`, `simple_output_67` — `X=SPAN(X)` self-rebind, still open
  (FINDING-2026-08-20-s186 §1).
- `user_function_table_datatype_branch_1` (COPYL, rank4), `user_function_convert_indirect_branch_1` (ONCE,
  rank6 — **m3 matches the FINDING exactly; m4 has apparently drifted from SIGSEGV to a compile refusal
  since 2026-08-27, worth a re-triage note**), `user_function_code_eval_bal_branch_1` (DEXP, declared GZ#5
  scope) — all `FINDING-2026-08-27-seat10-gimpel-triage-eight-symptom-classes-ranked.md`.
- `user_function_6`, `user_function_len_capture_1`, `user_function_len_capture_replace_1`,
  `user_function_len_capture_branch_2` — declared GZ#5-subset boundaries, compiler's own FATAL message
  (non-literal `DEFINE` prototype; capture target in a runtime-built pattern not a simple variable).
- `keyword_replace_3` — SETEXIT FACE 9, already-named s194 defect (`g_core_err_stmt` never advances).
- `user_function_array_replace_branch_1` — "RED ON ARRIVAL" per its own header, tracked under queue row
  `subscript-silent-accept`.
- `size_indirect_keyword_replace_branch_1` — deliberate pin, s194 row `indirect-nonname-silent-accept`.
- `trim_alt_keyword_replace_branch_1` — deliberate instrument for an unbuilt LAMBDA feature (RULES.md
  THE INSTRUMENT LAWS clause 3), self-pinned, never graded against the oracle.
- `simple_output_64` (ORD unimplemented, both tools lack it), `keyword_19` (&DUMP unimplemented, real but
  large SCRIP-only gap, deferred), `simple_program_1` (deliberately-missing include, mirrors the
  lon_cherryholmes gap).
- 16 `probe_fuzz`/`probe_loose_fuzz` entries — the extensively multi-session-tracked fuzzer crash/hang
  corpus (`FINDING-2026-08-20-s188` eleven-SEGVs/four-mechanisms, `s189` diff-batch/hang-batch, and
  `FINDING-2026-08-29-hq_C`/`seat09` successors). Spot-verified 4 of the 16 against their own header
  comments or matching `fz_*` names in those FINDINGs; the remaining 12 cited by name/class without
  individual re-derivation — this is pre-existing, already-tracked territory, not a fresh discovery, and
  re-deriving each individually would duplicate weeks of prior HQ investigation.
- 5 `probe_passthru` (`ptw_*`) entries — the active, documented nested-pattern-variable correctness
  campaign (`ARCH-PASSTHRU.md`, `board_passthru_combo.sh`); deliberately red per that campaign's own xfail
  law ("a red row is never denied"). One (`fence_pos_rpos_replace_branch_3`) directly reproduces `beauty`'s
  own `Commands` grammar shape verbatim.

## 6. CONTROL ARM

`make` (incremental, RT_OPT=-O0, per the pristine-loosening ruling) after `git pull --rebase` on all three
repos. `TIMEOUT=120 bash scripts/test_corpus_snobol4.sh` run as the landing control arm — see task LEDGER
for the resulting SUITE_BOARD line (this FINDING was written while that run was still in flight; do not
trust a number here over the LEDGER's own receipt).

## 7. SUGGESTED NEXT (naming for whoever picks these up, not filed as queue rows)

- 14 class rows above are ready to mint as rungs the moment hq_P ranks them; witnesses are one
  `lib_master_extract.sh` call away, no re-ablation needed.
- The 5 corpus-hygiene include-path gaps (§3) are a plausible single small row: "portable-ize the
  gimpel_triage/-rtx/-FORTPUT `-INCLUDE` paths absorbed into the flat SNOBOL4 master."
- `user_function_convert_indirect_branch_1`'s m3≡m4 drift (§5) is worth a one-line note to whoever owns
  that invariant's gate, independent of ONCE's actual bug.
