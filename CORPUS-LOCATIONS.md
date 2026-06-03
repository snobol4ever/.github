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
| Icon     | `/home/claude/corpus/programs/icon/`     | `rung<NN>_<topic>_<variant>.icn`   | 263 |
| SNOBOL4  | `/home/claude/corpus/programs/snobol4/`  | varies (see snobol4corpus subdir)  | many |
| Snocone  | `/home/claude/corpus/programs/snocone/`  | varies                             | many |
| Prolog   | `/home/claude/corpus/programs/prolog/`   | varies                             | — |
| Raku     | `/home/claude/corpus/programs/raku/`     | varies                             | — |
| Rebus    | `/home/claude/corpus/programs/rebus/`    | varies                             | — |
| Pascal   | `/home/claude/corpus/programs/pascal/`   | our `.pas` probes + README (reference oracle fetched separately, not bundled; no suite yet) | — |

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

**Icon corpus (`--interp`):**
```bash
bash /home/claude/SCRIP/scripts/test_icon_all_rungs.sh
# Defaults: SCRIP=/home/claude/SCRIP/scrip
#           CORPUS=/home/claude/corpus/programs/icon
# Reports: PASS=N FAIL=N XFAIL=N TOTAL=263
# As of 2026-05-09: 177 / 56 / 30
```

The runner is **hardcoded to `--interp`** (line 58 / 60 of the
script).  There is no `--interp` flag.  To run the corpus in
mode 3 today, copy or wrap the runner — see "Per-mode runner"
below.

**Per-rung subset:**
```bash
bash /home/claude/SCRIP/scripts/test_icon_ir_rung_NN.sh
```
where `NN` is 01..36.  These exist for many but not all rungs;
see `scripts/test_icon_ir_rung_*.sh`.

**Per-program manual:**
```bash
cd /home/claude/SCRIP
./scrip --interp /home/claude/corpus/programs/icon/rung01_paper_mult.icn
```

## Per-mode runner — write one, do not embed paths

A goal that needs `--interp` and `--run` results across the
corpus should add a sibling script (e.g.
`scripts/test_icon_sm_all_rungs.sh`) that copies
`test_icon_all_rungs.sh` and changes the mode flag.  Do **not**
write per-rung mode probes that embed `/home/claude/corpus/...`
paths — read from `$CORPUS` with this file's default.

---

## What "modes work" means — the cheat-detection rules

(Borrowed from the framing in `GOAL-CHUNKS.md` and made explicit
here so corpus runners and goal probes apply it consistently.)

A program "works in mode 3" iff:
1. `./scrip --interp <prog>` exits 0
2. Output is byte-identical to `--interp` (the oracle)
3. **No AST walker is reached during SM dispatch.**  Specifically:
   - `coro_eval` not called from `sm_interp_run`'s call graph
   - `interp_eval` / `interp_eval_pat` / `interp_eval_ref` /
     `call_user_function` / `execute_program` not reachable from
     the SM dispatch loop
   - `SM_PUSH_EXPR` (the legacy AST-pointer-on-stack opcode) not
     fired by any SM_Program produced by `sm_lower`
   - `proc_table[i].proc` (raw `AST_t*` field) not dereferenced
     during call dispatch — `proc_table[i].entry_pc` is the
     correct field

(1) and (2) are necessary; (3) is what distinguishes "mode 3
honest" from "mode 3 with mode 2 fallback under the hood."  The
isolation gate (`scripts/test_isolation_ir_sm.sh`) and the
SCRIP_EXPRS_AUDIT counter together witness (3).

A program "works in mode 2 honestly" iff `--interp` walks the
AST tree without secretly delegating to SM dispatch.  Less
contested than mode 3 today, but worth naming so goal files
don't accidentally ship a "mode 2 = mode 3 in disguise" cheat
in the other direction.

A program "works in mode 4" iff its emitted standalone binary
runs to completion linking only against `libscrip_rt.so` —
no AST walker can possibly be reached because the emitted
artifact is a separate process.  This is the structural property
that makes mode 4 the closure witness for the whole stack.

---

## When to update this file

- New corpus directory added → add a row to the table.
- Path moves → update the row, do not leave stale paths.
- New runner script → add to "Runners".
- New language → new row.

This file is **navigation** like PLAN.md, not authoritative
content — the corpus repo's own `LAYOUT.md` and `README.md` are
the source of truth for file naming inside the corpus.  This
file just says where it is.
