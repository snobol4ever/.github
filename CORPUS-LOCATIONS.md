# CORPUS-LOCATIONS.md — where the test programs live

**Read this before assuming a corpus path.**  Test program paths
were rediscovered three times across recent sessions because no
single doc names them.  This is that doc.

PLAN.md links here.  Goal files that reference corpus programs
should point at this file rather than embed paths inline.

---

## Per-language corpus paths

All paths are absolute, rooted at the standard checkout layout
(`/home/claude/<repo>/...`).

| Language | Corpus root | Typical filename pattern | Count |
|----------|-------------|--------------------------|-------|
| Icon     | `/home/claude/corpus/programs/icon/`     | `rung<NN>_<topic>_<variant>.icn` | 263 rung files (suite TOTAL=289 incl. subdirs) |
| SNOBOL4  | `/home/claude/corpus/programs/snobol4/`  | varies (see snobol4corpus subdir)  | many |
| Snocone  | `/home/claude/corpus/programs/snocone/`  | varies                             | many |
| Prolog   | `/home/claude/corpus/programs/prolog/`   | varies                             | — |
| Raku     | `/home/claude/corpus/programs/raku/`     | varies                             | — |
| Rebus    | `/home/claude/corpus/programs/rebus/`    | varies                             | — |
| Pascal   | `/home/claude/corpus/programs/pascal/`   | reference compiler (pcom.pas/pint.pas) + `.pas` probes; no suite yet | ref |
| Icon TIMING benchmarks | `/home/claude/corpus/benchmarks/icon/` | 10 link-heavy programs + support + `.dat`; NOT byte-diffable (timing scaffold output) — full map, reference-impl build recipes, and runner traps: `GOAL-ICON-BB.md` §ICON BENCHMARK MAP | 10 |
| **SNOBOL4 TIMED benchmarks** ⬅ s149, PROMOTED s155 (BM-ONE) | `/home/claude/corpus/benchmarks/snobol4/` | `<kernel>.sno` (body-only) + `.ref` (check line only) + `harness.inc` + `NOISE-FLOOR.tsv`; TIME-based (fixed ms budget, iterations counted). ⛔ NOT generated — `harness.inc` is the ONE driver and the bodies are HAND-EDITABLE. `gen_timed_bench_snobol4.sh` is DELETED. `timed/` subdir is RETIRED. Runner `test_bench_snobol4_timed.sh` (grades only files that include `harness.inc`) | 12 |
| **Gimpel SNOBOL4 function library** ⬅ s191 | `/home/claude/corpus/programs/gimpel/` | ⛔ **TWO KINDS OF FILE.** `NAME_driver.sno` = a runnable test (`-INCLUDE "NAME.sno"` + body + `END`) and **is** the scorecard row; `NAME.sno` = a LIBRARY MODULE (a `DEFINE` and a `:(NAME_END)` label — no `END`, no output) and is **not a program**. The scorecard enumerates `-name *_driver.sno`, so **a test whose name does not end in `_driver.sno` is silently never scored**. Full conventions + the SNOBOL4+/Catspaw `INPUT` dialect trap: `programs/gimpel/README.md` | 124 drivers + 145 modules |
| **BB reference embodiments** ⬅ SINGLE COPY (2026-08-04) | `/home/claude/corpus/probe/bb/` | `test_sno_*.c` · `test_icon*.c` · `test_sno_cell_*.s` · `test_sno_stmt_frame_*.{s,sno}` · `test_sno_call2bb_*.sno` · the 141-probe suite | one home |
| **Bench-harness procedure-boundary witnesses** ⬅ s252 | `/home/claude/corpus/probe/benchharness/` | `probe_toplevel.sno` / `probe_defwrap.sno` / `probe_deflocal.sno` — same loop body at top level, `DEFINE`-wrapped, and `DEFINE`-wrapped with true locals; receipts for `FINDING-2026-08-22-s252-the-define-boundary-moves-one-slot-offset-and-nothing-else.md` | 3 |

⛔ **THE BB EMBODIMENTS HAVE EXACTLY ONE HOME: `corpus/probe/bb/` (Lon directive 2026-08-04).** They
previously existed as 2–4 divergent copies across `SCRIP/seed/`, `SCRIP/bench/`, and `.github/`, and the
ARCH docs pointed at three different ones — so a session reading "the golden design" got whichever copy its
doc happened to name. `SCRIP/seed/` and `SCRIP/bench/` no longer contain any `test_sno_*`/`test_icon*`.
Anything that consumes them takes a path into `corpus/probe/bb/` (see `scripts/test_gate_call2bb_stub_regime.sh`,
which reads `$PROBE` with that default). **Do not re-create a second copy for convenience.**

**Each `.icn` (or `.sno`, etc.) program has a sibling `.expected`
file** with the canonical SPITBOL/oracle output.  The corpus runner
diffs against that file.  Some programs have `.xfail` markers
indicating known-unimplemented territory (counted XFAIL, not FAIL).

**Some programs have sibling `.j` and `.s` files** — these are
JCON (.j) and SPITBOL (.s) artifacts, not source.  Source is `.icn`.

## NOT the corpus

- `/home/claude/SCRIP/test/icon/` — only **8** programs total
  (hello, queens, sieve, palindrome, generators, meander, roman,
  plus a coverage subdir).  These are smoke-test files, not the
  full corpus.  The smoke tests reference these.
- `/home/claude/SCRIP/bench/` — benchmarks, not correctness corpus.

---

## Runners

**Icon corpus:**
```bash
bash /home/claude/SCRIP/scripts/test_icon_all_rungs.sh
# Defaults: SCRIP=/home/claude/SCRIP/scrip  CORPUS=/home/claude/corpus/programs/icon
# Reports: PASS=N FAIL=N XFAIL=N TOTAL=289   (2026-07-01: 190/63/36)
# Per-construct, oracle-anchored: bash SCRIP/scripts/audit_jcon_wholesale.sh (66 probes)
```

**Icon timing benchmarks (iconx oracle + SCRIP m3/m4):**
```bash
SKIP_BUILD=1 bash /home/claude/SCRIP/scripts/test_icon_bench_corpus.sh
# First run without SKIP_BUILD=1 (auto-builds icon-master at /home/claude/icon-master).
# Full map + Arizona/JCON build recipes + invocation traps: GOAL-ICON-BB.md §ICON BENCHMARK MAP
```

**Per-rung subset:**
```bash
bash /home/claude/SCRIP/scripts/test_icon_ir_rung_NN.sh
```
where `NN` is 01..36.  These exist for many but not all rungs;
see `scripts/test_icon_ir_rung_*.sh`.

**Per-program manual:**
```bash
cd /home/claude/SCRIP
./scrip --run /home/claude/corpus/programs/icon/rung01_paper_mult.icn
```

## Per-mode runner — write one, do not embed paths

A goal that needs `--run` and `--run` results across the
corpus should add a sibling script (e.g.
`scripts/test_icon_sm_all_rungs.sh`) that copies
`test_icon_all_rungs.sh` and changes the mode flag.  Do **not**
write per-rung mode probes that embed `/home/claude/corpus/...`
paths — read from `$CORPUS` with this file's default.

---

## What "modes work" means (2026-07-01)
Modes 1/2 are DELETED. "Works" = `--run` (mode 3) and `--compile` (mode 4) both exit 0 with output matching the sibling `.expected`/oracle, byte-identical to each other; no AST/IR is walked at runtime (emit-time only — GOAL-IR-IMMUTABLE-EMIT.md, GOAL-MODE34-IDENTICAL.md). The former SM-era cheat-detection symbol list was deleted (all symbols dead).

## When to update this file

- New corpus directory added → add a row to the table.
- Path moves → update the row, do not leave stale paths.
- New runner script → add to "Runners".
- New language → new row.

This file is **navigation** like PLAN.md, not authoritative
content — the corpus repo's own `LAYOUT.md` and `README.md` are
the source of truth for file naming inside the corpus.  This
file just says where it is.
