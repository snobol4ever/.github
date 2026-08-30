# FINDING: the shared "45-script" dead-path repro command has three bugs of its own, and crosscheck/ is confirmed converted, not lost

## Context
Row `dead-suite-path-consumer-sweep` (ceo direct assignment), continuing hq_P's
`FINDING-2026-08-30-hq_P-dead-corpus-paths-leave-45-scripts-green-over-nothing.md` and seat12's
partial 18-script handoff (SCRIP `f1d32342`). Re-ran hq_P's own repro command fresh before trusting
its count, per this project's own standing FACT RULE culture — and it does not hold up as-is.

## THREE BUGS IN THE REPRO COMMAND ITSELF, found in order, each corrected before trusting the next number
1. **Double-prefix false positive.** The regex `\$(CORPUS|S4E[A-Z_]*)/...` — with `S4E[A-Z_]*`'s `*`
   meaning zero-or-more — also matches bare `$S4E` (not just `$S4E_SOMETHING`). The command's own
   `sed 's/\$[A-Za-z_]*\///'` then strips only that one `$S4E/` prefix, leaving the REST of the
   captured path (which may already read `corpus/benchmarks/snobol4` verbatim, if the script wrote
   `$S4E/corpus/...`) — and the existence check re-prepends `/home/claude_P/corpus/` on top of that,
   producing `.../corpus/corpus/benchmarks/snobol4`, which of course never exists. Confirmed on
   `test_3way_snobol4.sh`'s `$S4E/corpus/benchmarks/snobol4`: the real directory exists; the check as
   written cannot see that.
2. **Digit-excluding character class.** An intermediate fix attempt used `[A-Za-z_]+` to pull the
   variable name back out of a captured match — which does not match `S4E` (it contains a literal
   `4`) at all, so every `$S4E.../` match silently fell through to "unresolvable" until corrected to
   `[A-Za-z0-9_]+`.
3. **`$CORPUS` is not a universal alias for `$S4E/corpus`.** Several scripts locally redefine it —
   e.g. `test_gate_pascal_m3.sh`: `CORPUS="${CORPUS:-$S4E/corpus/tests/pascal}"`. A checker that
   assumes `$CORPUS/X` always means `$S4E/corpus/X` will misjudge every script that redefines it.
   Confirmed: `test_gate_pascal_m3.sh`'s actual resolved path (`corpus/tests/pascal/ALL.pas`) exists
   and is fine; a blind assumption reported it as dead. **This bug is NOT fully correctable by
   smarter regex** — it needs either per-script sourcing of the real definition or dynamic
   verification (actually running the script), not a second static heuristic layered on the first
   two. Comment-embedded example text is a fourth, smaller trap (`test_gate_suite_conversion_
   complete.sh` line 184 has `"$CORPUS/tests/prolog/..."` inside a `#`-comment, matched by the raw
   regex, not real code) — filtered by excluding matches after an unescaped `#`.

## MEASURED, after all three corrections
79 distinct scripts / 141 references to a `$CORPUS` or `$S4E`/`$S4E_HOME` path currently resolve to
nothing. This splits into two **unrelated** root causes the raw grep conflates:

**(A) 38 reference `$S4E/x64` directly.** Investigated fully, not assumed: **zero of the 38 have an
actual bug.** Every occurrence is either the safe, already-correct `[ -d "$S4E/x64" ] && ... ||
echo /home/resources` fallback idiom (harmless dead branch now that per-seat x64 is permanently gone
per Lon s261 — the OR-branch always fires and resolves correctly), or a comment mentioning `x64` by
name while the actual code already calls `sbl_clean_bin()`/`sbl_correctness_bin()` correctly. Ran
all 38 end-to-end (not just grepped) to confirm before writing this down — real failures exist in
several of them, but every one traced to something else entirely (the already-known demo/demos
rename, missing `beauty.sno`, etc.), never to the x64 reference itself.

**(B) The remaining 52 (103 references, after excluding the false positives above) are genuine.**
`corpus/crosscheck/` is the largest single cluster (11+ scripts). Traced with `git log
--diff-filter=D`, not assumed: **deliberately converted, not lost** — `da0987478`/`d55137833`/
`69c43155e`/`710f2562c` show it absorbed into `corpus/tests/<lang>/ALL.{sno,ref,csv}` masters over
2026-08-28's "total conversion." Confirms hq_P's own warning exactly: the cure is `lib_master_
extract.sh` extraction by origin, never re-pointing at a surviving directory (would grade a
different population and look green either way).

## ONE WORKED EXAMPLE, fully verified
`test_gate_out_sweep_flaky.sh` referenced 3 named `crosscheck/patterns/*.sno` files directly (with
an existing, correct `[ -f ... ] || exit 1` guard — this script was never silently green, it was
loudly red, exactly RULES.md's own preferred failure shape). Found each file's origin in `ALL.csv`
(`crosscheck_patterns__<name>`, cross-checked against a near-duplicate-looking but wrong origin from
an unrelated `scrip_test_snobol4_patterns_038_pat_literal` family before picking the right one),
extracted via `master_extract_origin` into the script's own `mktemp -d` work directory, ran the gate
end-to-end: **GATE GREEN**, and the extracted flaky witness's md5 (`027851e5bcd8152...`) matches the
exact value this script's own header comment cites from the original 2026-06 finding — direct proof
the extraction preserved byte-identical content, not a different population. Landed SCRIP `a14a60d8`.

## NOT DONE — scope remaining, organized by shape, for whoever continues
- **crosscheck cluster (10+ scripts still)**: `test_crosscheck_all_backends.sh`, `test_csnobol4_
  budne_suite.sh`, `test_emit_diff_invariant_check.sh`, `test_gate_omega_own_k.sh`, `test_interp_
  broad_corpus_and_beauty.sh`, `test_invariants_3x3_harness.sh`, `test_smoke_snobol4_run.sh`,
  `test_wasm_corpus_rung.sh`, `board_denominators.sh`, `test_corpus_snobol4.sh` (this last one also
  needs the separate, already-known `demos`-vs-`demo` fix). Same technique as the worked example —
  find each file's origin in the relevant language's `ALL.csv`, extract, never re-point.
- **`test_lower_byte_identical.sh`**: 16 references alone (individual fixture files across
  snocone/icon/prolog/raku/snobol4) — likely needs a per-language audit of where each specific
  fixture landed, not one mechanical pattern; its own row, not a quick pass.
- **`beauty`/`beauty_suite` cluster**: already flagged by seat12 as NOT a mechanical repoint — Lon's
  s271 ruling deliberately deleted the live `beauty.sno` and named `beauty_classic.sno` (now in
  `demo/`) as canonical instead. Needs re-scoping by whoever owns Milestone 1, not this row.
- **`demos/csn_bridge_*`/`label_flow`/`spl_bridge` cluster**: these already SKIP gracefully
  ("corpus checkout incomplete") rather than false-greening — lower priority, may be genuinely
  not-yet-built features rather than drift.
- **Pascal (`test_gate_pascal_m3/m4.sh`)**: false positive, already correct (see bug 3 above) —
  remove from any future list built off the raw grep.
- **Misc singletons**: `test_gate_pl_coupling.sh`, `test_gate_udc.sh` (has its own separate `tests/
  snobol4/tests/snobol4/` double-nesting typo, worth a second look), `test_icon_bench_corpus.sh`
  (also has an unrelated `ICONM: unbound variable` bug), `test_prolog_parser_fixtures.sh`,
  `test_parser_snocone.sh` — not triaged individually this pass.

## The generalizable lesson
A shared repro command handed between sessions is itself an instrument, and this project's own FACT
RULES say to verify an instrument before trusting its count — that applied here to the measurement
tool as much as to any gate script. All three bugs were silent: none of them crashed the command,
they just mis-classified real paths as dead or vice versa, and the wrong number would have looked
exactly as authoritative as the right one.
