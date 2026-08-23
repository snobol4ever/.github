# FINDING 2026-08-23 (seat16) — corpus coverage census: the first real headline count, and it's smaller-but-different than it looks

**Task:** `audit-corpus-what-is-ungated` (rank 0, FLEET mode, confirmed with Lon in-chat before starting). **Status at handoff: PARTIAL, converged early** — HQ-PERFORM assigned seat16 to `icon-n3-scan-one-depth-authority` (rank 1) mid-sweep; this FINDING captures everything measured before the pivot, and the task's own NEXT block is rewritten so any seat can continue without re-deriving anything below.

## The headline number, and why the raw one is misleading

Full corpus enumeration (recursive `find`, all 7 source extensions, **`corpus/programs/lon/` excluded by construction — not walked, not counted, per the blanket ⛔ rule**): **5,144 runnable-language files.**

That number is not the right coverage denominator. **1,890 of the 5,144 are reference/witness material, not product corpus:**

| Bucket | Count | Why it's not "corpus" |
|---|---|---|
| `probe/` (68 subdirs) | 1,019 | Individual defect-witness pairs tied to specific historical debugging, not a graded suite by design |
| `programs/icon/ipl/` | 851 | Upstream Icon Program Library, copied verbatim. Its own README says outright: "canonical reference programs... oracle inputs... feature coverage targets for rung 4+ **expansion**" — it is raw material for writing future corpus, not itself the corpus. 317 of the 851 (`gprogs`+`gprocs`) are X11 graphics programs that cannot run headless regardless. |
| `programs/icon/jcon-compiler/` + `jcon-ref/` | 19 | JCON's own reference compiler source (`irgen.icn`, `linker.icn`, ...) — the canonical-source material RULES.md tells sessions to *read*, not test input |
| `programs/snobol4/oracle-unrunnable/` | 1 | Documented (own README) as having no possible ground truth — unresolved `-INCLUDE`s |

**Primary corpus (crosscheck + programs/&lt;lang&gt; + benchmarks, minus the above): 3,254 files.** This is the number a coverage policy should be computed against. Recommendation below.

## What's actually confirmed GATED (diffed against a real reference, not just executed)

- **`crosscheck/*.sno`** (325/326 have `.ref`; 1 missing — `crosscheck/coverage/coverage_sno_nodes.sno`) — confirmed covered by `test_corpus_snobol4.sh`'s recursive `find "$CORPUS/crosscheck" -name "*.sno"` loop (read directly, not via sub-agent). **This directory is fine** — contrary to the parent task's brief text (which used a bare non-recursive `ls` as an illustrative example of the failure mode), the actual runner does recurse it.
- **`crosscheck/snocone/*.sc`** (181 files, **100% have `.ref`**) — **NOT** covered by the same script (it only globs `*.sno`). Unconfirmed whether a Snocone-specific script (`test_crosscheck_beauty_snocone.sh`, `test_crosscheck_sc_corpus_rung.sh`, `test_snocone_parser_fixtures.sh` — all exist, none yet reviewed) covers it. **This is the single cheapest potential win in the whole census: the reference output already exists for all 181 files; closing this gap is pure wiring, no oracle work.**
- **`programs/snobol4/beauty_suite/*_driver.sno`** — GATED (multiple gate scripts confirmed via sub-agent read: `test_gate_sn7_beauty_self_host.sh`, `test_gate_em_beauty_subsystems_mode4.sh`).
- **`programs/snobol4/demo/`** — GATED-OR-DOCUMENTED, **already fully resolved** by the direct ancestor of this task (`demo-corpus-coverage-audit`, DONE 2026-08-22 — read `scripts/test_corpus_snobol4.sh` directly to confirm current state). 19 programs explicitly `run_test`'d; 4 documented NOT-gated with one-line reasons each inline in the script (json hang, json-match hang, json-match-fence wrong-verdict, calculator-2 wrong-answer) plus a FINDING; every one of those 4 already has its own tracked queue row (`json-alternate-af-spin`, `calculator2-wrong-output`, etc.) or is swept DONE. **This is the worked example of what "done" looks like for the rest of the corpus** — see policy recommendation below.
- **Several `probe/` subdirectories** are actively gated: `probe/bb` (`test_gate_call2bb_stub_regime.sh`), `probe/clobarm`, `probe/fz`, `probe/kw`, `probe/cn` (`test_gate_udc.sh`) — confirmed via sub-agent read of the `test_gate_*.sh` family. Most of the other 63 probe subdirectories are unconfirmed (see below).

## Icon: the 1,048-without-`.expected` number needs correcting, not just reporting

`programs/icon/` = 1,348 `.icn` files; only 300 have an `.expected` sibling. But breaking down the 1,048 without one:

| Subdir | Count | Classification |
|---|---|---|
| `ipl/` | 851 | Reference archive (see above) — **not a coverage gap** |
| `parser/` | 153 | **False alarm** — these use `.ref` siblings, not `.expected` (153/153 have one). Unconfirmed whether any script actually diffs them; NOT confirmed broken. |
| `jcon-compiler/` + `jcon-ref/` | 19 | Reference source (see above) — **not a coverage gap** |
| `samples/`, `demo/`, `repro/`, `coverage/`, + 11 top-level (`hello.icn`, `queens.icn`, `roman.icn`, ...) | ~19 | **Genuine gap candidates** — real small standalone programs, no oracle output anywhere. Smallest, cheapest, most legitimate slice of the Icon "ungated" number. |

**True Icon coverage gap, once reference/archive material is excluded: on the order of ~19-172 files (19 confirmed no-oracle-at-all; 153 more pending confirmation of whether their existing `.ref` is actually wired to a diff), not 1,048.**

## Confirmed-DONE row that wasn't: `ref-the-ungraded-suites`

`ref-the-ungraded-suites` (QUEUE.done.tsv, rank 6) closed with a DONE-WHEN reading "every gradeable program in feat/ and parser/ carries a live-oracle `.ref`". Measured directly: `feat/` genuinely got it (2→19 of 21). **`programs/snobol4/parser/` did not move at all — still 88 `.sno`, 0 `.ref`, 0 `.expected`, no exclusion note anywhere.** This is exactly the failure mode CEO's own AUDIT COROLLARY (ARCH-FLEET-CEO.md, s264) names: *"a recompute inherits the blindness of what it recomputes... an audit samples the instrument's ability to say NO before crediting its YES."* Nobody had re-run this row's own criterion since it closed. **New row minted: `snobol4-parser-suite-zero-ref` (rank 2).**

## Rows explicitly NOT duplicated (already tracked, confirmed by search before minting anything)

- `csnobol4-suite-triage` (rank 1, FREE) — covers `programs/csnobol4-suite/` (124 files). ⛔ Per RULES.md (s261), this suite's native oracle is `csnobol4`, NOT `sbl -bf` — grading it with SPITBOL produces false reds (30/120 measured). No `csnobol4_bin()` exists yet in `lib_oracle_flags.sh`. Did not touch.
- `gimpel-suite-triage` (rank 1, FREE) — covers `programs/gimpel/` (289 files: 124 `*_driver.sno` real tests + 145 library modules that are not programs).
- The 4 documented-not-gated `demo/` programs above.

## Not yet triaged / explicit handoff (no silent gaps)

Per RULES.md TIME-BOXED EXPLORATION and the mid-sweep HQ-PERFORM reassignment to `icon-n3-scan-one-depth-authority`, this sweep stopped here rather than push through all 5,144 files. Named explicitly, not buried:

- **Prolog** (737 files, 276 have `.ref`/`.expected`): harness-coverage cross-reference incomplete.
- **Rebus** (99, 50 have ref), **Raku** (186, 97 have ref), **Pascal** (180, 155 have ref), **Snocone `programs/snocone/`** (181, 97 have ref): file-level ratios measured directly; script-level GATED cross-reference incomplete.
- **`probe/`**: only 5 of 68 subdirectories confirmed gated (see above); the remaining 63 unconfirmed — most are plausibly inert historical witnesses (their bug already fixed and tracked elsewhere), not live gaps, but this is judgment, not yet verified per-subdirectory.
- **Methodology note for whoever continues this**: 6 parallel sub-agents were dispatched to read the 241 corpus-touching scripts in `SCRIP/scripts/` (one already-reviewed by hand: `test_corpus_snobol4.sh`). Of the 6, only 1 (`chunk_02`, the `test_gate_*.sh` family, 38 scripts) returned clean structured output. 2 more returned degenerate/off-task text unrelated to the assignment (apparent sub-agent confusion, not a data result — do not trust or cite them). 3 were still running at handoff and their results, if useful, will still arrive as task-notifications to Fleet #16 independent of what that session is doing next — worth checking before re-dispatching the same chunks. The chunk file lists survive at `/tmp/claude-1000/-home-claude16/8bf74278-e49a-45e4-b1a5-853400f2325c/scratchpad/harness_chunks/chunk_0{0,1,3}` for reuse (session-local scratch, may not survive across seats — copy out if reusing from a different session).

## Policy proposal for HQ to rule on (per the brief: propose, don't unilaterally gate 300 programs)

1. **Compute "coverage" against PRIMARY CORPUS (3,254) not raw enumeration (5,144).** Mixing `ipl/`'s upstream reference archive and `probe/`'s debugging witnesses into a correctness-coverage denominator answers a different question than "is our product corpus tested" and is the likely reason this number was never landed before now.
2. **`ipl/` needs a "mine it" policy, not a "gate it" policy** — its own README already says it's feedstock for future rungs. Gating all 851 (534 after removing the 317 X11-only ones) as a batch would trade a real coverage hole for exactly the 30-minute-gate problem the brief warns against.
3. **`probe/`'s 63 unconfirmed subdirectories need a per-subdirectory liveness check** (is there a live task row citing the underlying bug?), not blanket gating — an ungated probe file for an already-fixed bug is an inert historical witness, not a defect.
4. **For genuine remaining gaps** (Icon's ~19-172, Prolog's ~461, Rebus/Raku/Pascal/Snocone's few hundred, `probe/`'s unconfirmed slice): follow the `demo-corpus-coverage-audit` / `ref-the-ungraded-suites` three-way classify-before-committing method exactly (mint `.ref` where the live oracle can produce one under the corpus timeout; name oracle-unrunnable/needs-input programs explicitly) — it's proven and already blessed.
5. **Record exclusion reasons in a directory-local file (`EXCLUDED.md`, the pattern this session used for the parser/ row's DONE-WHEN), not only in a chat transcript or a FINDING.** `ref-the-ungraded-suites`'s parser/ half going silently unfinished — with zero trace of *why* anywhere in the tree — is the direct, mechanically-verifiable cause of the false "DONE." A future audit (or a `done`-time vacuity probe) can check an `EXCLUDED.md` exists; it cannot check a reason that only ever existed in a session transcript.
6. **Before wiring `crosscheck/snocone` or Icon `parser/` into a live gate, check runtime cost against the `timeout 30s` corpus-runner budget** — both already have their `.ref`, so this is pure wiring, but 181+153 additional file executions per run is not free.

## Row minted this session

- `snobol4-parser-suite-zero-ref` (rank 2, unassigned, FREE) — see above.
