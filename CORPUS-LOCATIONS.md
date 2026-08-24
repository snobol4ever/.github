# CORPUS-LOCATIONS.md — where the test programs live

**Read this before assuming a corpus path.**  Test program paths
were rediscovered three times across recent sessions because no
single doc names them.  This is that doc.

PLAN.md links here.  Goal files that reference corpus programs
should point at this file rather than embed paths inline.

⛔ **REWRITTEN 2026-08-24 (seat04, instrument-repair-bundle PART 3) — every path below verified
directly against the tree, not carried from the previous revision.** The prior text described the
pre-flatten `/home/claude/corpus/programs/<lang>/` layout; the s269–s272 reorg removed that
`programs/` level (7,369 files moved up one directory — CEO-17/CEO-18, .github). Provenance: corpus
`741921e8`, `.github` `2bc6ce30`, both `main`, checked 2026-08-24. **This file drifts the moment the
tree moves again — trust `ls corpus/` over this table if they disagree, and fix the row rather than
trusting memory** (the exact failure this rewrite exists to correct).
⛔ **PATHS ARE REPO-RELATIVE ON PURPOSE, NEVER A HARDCODED SEAT ROOT.** This is a D-17 PORTABLE-HOME
project: every root is a sibling checkout (`corpus/`, `SCRIP/`, `.github/`, `x64/` side by side) and
the absolute prefix differs per seat (`/home/claude04`, `/home/claude_C`, `/home/claude`, …) — verify
yours with `pwd`, per `CLAUDE.md`. A path here of the form `corpus/icon/` means "under your own
sibling root," not literally the string `/home/claude/corpus/icon/`; the *previous* revision of this
file hardcoded `/home/claude/...` throughout, which is the fossil-path class this whole row exists to
retire (`scripts/test_gate_no_fossil_src_paths.sh`, same commit).

---

## Per-language corpus paths

All paths are relative to the sibling root (see banner above). Counts are a **file census taken
2026-08-24**, not a graded PASS/FAIL/XFAIL split — run the language's own board script for that.

| Language | Corpus root | Typical filename pattern | Count (2026-08-24 census) |
|----------|-------------|--------------------------|-------|
| Icon     | `corpus/icon/`     | `rung<NN>_<topic>_<variant>.icn` | 295 `rung*.icn` files at the top level |
| SNOBOL4  | `corpus/snobol4/`  | varies — see subdirs below | 17 subdirs (see below) |
| Snocone  | `corpus/snocone/`  | varies                             | — |
| Prolog   | `corpus/prolog/`   | mix of `rungNN_*.pl` (some rungs flat, e.g. 12–21; others nested, e.g. 22–28 — verify per-rung before assuming either shape) + `.pl`/`.expected` or `.pl`/`.ref` pairs (BOTH extensions are live; do not assume one) | — |
| Raku     | `corpus/raku/`     | varies                             | — |
| Rebus    | `corpus/rebus/`    | varies                             | — |
| Pascal   | `corpus/pascal/`   | reference compiler (pcom.pas/pint.pas) + `.pas` probes | — |
| Icon TIMING benchmarks | `corpus/benchmarks/icon/` | link-heavy programs + support + `.dat`; NOT byte-diffable (timing scaffold output) | see `GOAL-ICON-BB.md` §ICON BENCHMARK MAP |
| SNOBOL4 TIMED benchmarks | `corpus/benchmarks/snobol4/` | `<kernel>.sno` (body-only) + `.ref` (check line only) + `harness.inc` + `NOISE-FLOOR.tsv`; TIME-based. Runner `test_bench_snobol4_timed.sh` | — |
| Pascal / Prolog benchmarks | `corpus/benchmarks/pascal/`, `corpus/benchmarks/prolog/` | present on disk 2026-08-24; not otherwise documented here yet | — |
| **SNOBOL4 include files** ⬅ corrected this pass — `PART 3` | `corpus/include/` | `<name>.inc`, flat, no subdirectory | 16. ⛔ **NOT** `corpus/demo/inc/` or `corpus/snobol4/demo/inc/` — that path never existed on this tree; it was a hardcoded default in 8+ scripts, all repointed this same commit (`test_gate_no_fossil_src_paths.sh` LEDGER). |
| **Gimpel SNOBOL4 function library** | `corpus/snobol4/gimpel/` | ⛔ **TWO KINDS OF FILE.** `NAME_driver.sno` = a runnable test and **is** the scorecard row; `NAME.sno` = a LIBRARY MODULE (no `END`) and is **not** a program. Full conventions: `corpus/snobol4/gimpel/README.md` (verify it still exists there before trusting the pointer) | 144 drivers + 145 modules |
| **BB reference embodiments** | `corpus/probe/bb/` | `test_sno_*.c` · `test_icon*.c` · `test_sno_cell_*.s` · etc. — the 141-probe suite | one home, confirmed present |
| **Bench-harness procedure-boundary witnesses** | `corpus/probe/benchharness/` | `probe_toplevel.sno` / `probe_defwrap.sno` / `probe_deflocal.sno` | confirmed present |
| **csnobol4-suite** (Phil Budne's CSNOBOL4 test suite) | `corpus/programs/csnobol4-suite/` | ⛔ the ONLY thing left under the old `programs/` prefix — every other language's `programs/<lang>/` was flattened away. Its native oracle is **csnobol4, NOT SPITBOL** — see RULES.md's FACT RULE on grading it against `sbl -bf` (30/120 false reds). A second, differently-named copy also exists at `corpus/snobol4/csnobol4_suite/` (hyphen vs underscore) — this divergence is UNRESOLVED; do not assume the two are identical without checking, and flag it if you need to rely on either. | 120 `.ref` pairs (per RULES.md) |
| Demo corpus | `corpus/demo/` | showcase programs, one subdir per demo (`arithmetic/`, `beauty/`, `calculator/`, `claws5/`, `counter/`, `hello/`, `json/`, `pattern_test/`, …) | many subdirs |
| Crosscheck corpus | `corpus/crosscheck/` | self-contained `.sno`+`.ref` pairs, the primary harness feed (SCRIP `CLAUDE.md` § Corpus layout) | — |

⛔ **THE BB EMBODIMENTS HAVE EXACTLY ONE HOME: `corpus/probe/bb/` (Lon directive 2026-08-04, unchanged
by the s269-s272 reorg — confirmed still true 2026-08-24).** Do not re-create a second copy for
convenience.

**Each `.icn` (or `.sno`, etc.) program has a sibling `.expected`
file** with the canonical SPITBOL/oracle output, OR (Prolog, some rungs) a sibling `.ref` file — the
two extensions are NOT interchangeable and NOT universal; check which one a given directory actually
uses before writing a runner (a stale `.ref`-only assumption silently zero-scores an `.expected`-only
directory, and vice versa — the exact failure class `test_gate_no_fossil_src_paths.sh` was written to
catch, in the specific case of rung12–21 Prolog tests that had been silently SKIPping for this reason).
The corpus runner diffs against that file. Some programs have `.xfail` markers indicating known-
unimplemented territory (counted XFAIL, not FAIL).

**Some programs have sibling `.j` and `.s` files** — these are
JCON (.j) and SPITBOL (.s) artifacts, not source.  Source is `.icn` (or the language's own extension).

## NOT the corpus

- `SCRIP/test/icon/` — 10 `.icn` files at the top level (hello, queens, sieve, palindrome,
  generators, meander, roman, wordcount, global_test, zk5_global_cells_zero) plus `coverage/` and
  `jcon_audit/` subdirs, confirmed present 2026-08-24. Smoke-test files, not the full corpus.
- `SCRIP/bench/` — ⛔ **REMOVED**, confirmed absent 2026-08-24 (the previous revision of this doc
  still listed it as a live "not the corpus" path; it is gone, not merely renamed).

---

## Runners

Point every runner at `$S4E/corpus/<lang>/...` (or read `$CORPUS` with the script's own default —
see `CLAUDE.md` for the `S4E`/`S4E_HOME` sibling-root convention). Do **not** hardcode an absolute
`/home/claude/...`-style prefix in a new script; that is precisely the fossil-path class this file
and `test_gate_no_fossil_src_paths.sh` exist to keep out. Per-language runner scripts live in
`SCRIP/scripts/` — grep `scripts/test_*<lang>*.sh` and `scripts/board_*.sh`/`scripts/scorecard_*.sh`
for the current entry points rather than trusting a specific script name pinned here; script names
and counts have churned repeatedly (this file's own history is the evidence) and a name pinned in
prose goes stale exactly like a path does.

## Per-mode runner — write one, do not embed paths

A goal that needs a new mode/variant across the corpus should add a sibling script that copies an
existing per-language runner and changes the mode flag. Do **not** write per-rung mode probes that
embed a literal corpus path — derive it from `$S4E`/`$CORPUS` with the script's own default, the same
convention every other runner in `SCRIP/scripts/` uses.

---

## What "modes work" means (2026-07-01, still current)
Modes 1/2 are DELETED. "Works" = `--run` (mode 3) and `--compile` (mode 4) both exit 0 with output
matching the sibling `.expected`/oracle, byte-identical to each other; no AST/IR is walked at runtime.

## When to update this file

- New corpus directory added → add a row to the table.
- Path moves → update the row, do not leave stale paths. **Say when you last verified it** — a bare
  path with no date is exactly how the previous revision went three-reorgs stale unnoticed.
- New runner script → note it in "Runners" by pattern, not by pinning one script's name.
- New language → new row.
- If you cannot fully verify a row (count, extension convention, subdir shape), say so explicitly
  ("—", "unverified") rather than carrying forward a number from the prior revision — a stale number
  with no caveat is indistinguishable from a checked one, which is the whole failure this file keeps
  having.

This file is **navigation** like PLAN.md, not authoritative
content — the corpus repo's own `LAYOUT.md` and `README.md` are
nominally the source of truth for file naming inside the corpus, though `LAYOUT.md` is itself flagged
elsewhere (SCRIP `CLAUDE.md`) as predating the per-language flatten and describing a layout that no
longer exists — treat the tree itself as the final authority over either document.
