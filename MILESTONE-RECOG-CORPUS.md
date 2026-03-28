# MILESTONE-RECOG-CORPUS.md — M-RECOG-CORPUS

**Sprint:** PP-1 extension  
**Owner:** PP-1 session (Claude Sonnet 4.6)  
**Created:** 2026-03-27  
**Status:** DONE — 2026-03-27 (Claude Sonnet 4.6) — commit 4b4d71a snobol4x

---

## Goal

Run all four SCRIP recognizer/parser tools against the full program corpora and
establish a baseline pass/crash count. Zero crashes required; pass rate tracked
for trend.

**Tools under test:**
- `demo/scrip/icon_parser.icn` — full Icon parser (combinator, AST output)
- `demo/scrip/icon_recognizer.icn` — Icon wholesale recognizer (BEAUTY paradigm)
- `demo/scrip/prolog_parser.pro` — full Prolog DCG parser
- `demo/scrip/prolog_recognizer.pro` — Prolog wholesale recognizer (BEAUTY paradigm)

**Input corpora:**
| Corpus | Files | Notes |
|--------|-------|-------|
| `corpus/programs/icon/**/*.icn` | ~851 | IPL + misc Icon programs |
| `snobol4x/test/frontend/icon/**/*.icn` | ~258 | Compiler test suite |
| `snobol4x/test/frontend/prolog/**/*.pro` | ~130 | Compiler test suite |
| `snobol4x/test/frontend/prolog/**/*.pl`  | included above | Same dir |

---

## Pass/Fail Criteria

**PASS** (milestone complete):
- Zero crashes (exit non-zero or timeout at 10s) on any input file
- Parser pass rate ≥ 85% on Icon corpus (baseline: 29/30 sample = 97%)
- Recognizer pass rate ≥ 30% on Icon corpus (baseline: 13/30 sample = 43%;
  many files use `$include`/`link` which are legitimately skipped)
- Prolog parser pass rate ≥ 80% on prolog test corpus
- Prolog recognizer pass rate ≥ 50% on prolog test corpus

**Empty output** (not a crash) — acceptable for files that use preprocessor
directives (`$include`, `$define`, `link`) or are pure library include files
with no top-level procedures.

---

## Harness

Two scripts added to `snobol4x/test/scrip/`:

```bash
# Icon (both parser and recognizer)
bash test/scrip/run_corpus_icon.sh \
  corpus/programs/icon \
  test/frontend/icon

# Prolog (both parser and recognizer)
bash test/scrip/run_corpus_prolog.sh \
  test/frontend/prolog
```

Both scripts:
- Compile tools from source before running
- Emit `pass / empty / crash` counts per tool
- Exit 1 if crash count > 5% of total files
- Print `RESULT: PASS` or `RESULT: FAIL`

Override timeout: `TIMEOUT=30 bash run_corpus_icon.sh`

---

## Baseline (2026-03-27 sample run, 30 files)

| Tool | Pass | Empty | Crash |
|------|------|-------|-------|
| icon_parser     | 29/30 (97%) | 1 | 0 |
| icon_recognizer | 13/30 (43%) | 17 | 0 |

Prolog baseline: not yet run (tools just created).

---

## Session instructions

1. `git pull --rebase` in both `snobol4x` and `corpus`
2. Run `bash test/scrip/run_corpus_icon.sh` — record counts
3. Run `bash test/scrip/run_corpus_prolog.sh` — record counts
4. If crashes > 0: triage top-5 crash inputs, fix tool, re-run
5. If pass rate below threshold: improve tool, re-run
6. When all thresholds met: commit results table to this file, mark `Status: DONE`
7. Update PLAN.md row + push

**Read only:** `PLAN.md` PP-1 section + this milestone file.

---

## Results (fill in when run)

| Tool | Total | Pass | Empty | Crash | Pass% |
|------|-------|------|-------|-------|-------|
| icon_parser | | | | | |
| icon_recognizer | | | | | |
| prolog_parser | | | | | |
| prolog_recognizer | | | | | |


## Results (2026-03-27, Claude Sonnet 4.6, commit 4b4d71a snobol4x)

| Tool | Total | Pass | Empty | Crash | Pass% |
|------|-------|------|-------|-------|-------|
| icon_parser | 1109 | 1090 | 19 | 0 | 98.3% ✅ |
| icon_recognizer | 1109 | 576 | 533 | 0 | 51.9% ✅ |
| prolog_parser | 130 | 130 | 0 | 0 | 100% ✅ |
| prolog_recognizer | 130 | 130 | 0 | 0 | 100% ✅ |

**icon_parser fix:** right-recursive p_exprlist (eliminates eval stack overflow on large files); flat trees for associative ops (|, ||, ++, --, **, +, -, *, /, %, //).
