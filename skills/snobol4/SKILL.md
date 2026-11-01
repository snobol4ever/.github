---
name: snobol4
description: SCRIP's SNOBOL4, Snocone and Rebus (SPITBOL semantics; the oracle is sbl -bf): their parsers, lowerers, pattern runtime and match leaves, the SnoRungs, Gimpel, Budne, Flake, AIS, TPgm, X64T, X32T, SnoBench, SnoDemo, Snocone and Rebus suites and refs. REQUIRED by the skill gate before editing those parsers, lowerers or preludes.
---

# SCRIP SNOBOL4, Snocone and Rebus

The record is GOAL-SNOBOL4-100.md, GOAL-SNOCONE-100.md and GOAL-REBUS-100.md (LIVE CURSOR on top); a page beats this skill. SNOBOL4 is THE MODEL the other languages adopt, and a shared-machine change rolls out here first (CEO-1478..1484). Full suite tables, file maps and receipts are in `reference.md` beside this file.

## 1. The oracle

- **One oracle: SPITBOL `sbl -bf`**, through `sbl_correctness_bin()` in `harness/scripts/lib_oracle_flags.sh` (the benchmark oracle through `sbl_clean_bin()`). `-bf` always; `--compat` and `-F` are refused: SNOBOL4 and Snocone are CASE-SENSITIVE. CSNOBOL4 (Budne) is a population, never a second oracle.
- Snocone: `scrip --transpile prog.sc` gives portable SNOBOL4 that runs on `sbl -bf` first; its output is the ref. Rebus the same road; its spec is TR84-9.
- A ref is cut from the oracle; no XFAIL. What SPITBOL refuses, crashes on or hangs is `NO_ORACLE_ANSWER` (CEO-1696). SPITBOL's exit codes and fatal line are part of the ref.
- Shipped sizes `-d128m -i1m -s4m -m16m` (CEO-1261); declared sizes are a hard cap (CEO-1353). Keywords answer as SPITBOL answers.

## 2. The manuals

`/home/resources/manuals/snobol4/spitbol-manual-v3.7.txt` (every primitive, keyword, exit code, error), `green-book.txt`, `discrete-patterns-theory-snobol4.txt`, `/home/resources/manuals/rebus/rebus-tr84-9.txt`, `/home/resources/manuals/byrd-boxes/`; Snocone's paper `corpus/tests/snocone/report.md` (the census standard, not the syntax spec). Before ruling: grep the manual, then run a five-line probe on `sbl -bf`.

## 3. The source map

- Parsers: `src/parsers/snobol4/` (`snobol4.l`, `snobol4.y`; generated twins by `regenerate_parser_and_lexer_from_sources.sh`), `src/parsers/snocone/`, `src/parsers/rebus/`; the bootstrap parsers `SCRIP/bootstrap/parser_<lang>.sc` (never rewritten).
- Lowering: `src/lower/lower_snobol4.c`, `lower_snocone.c`, `lower_rebus.c`, `tree_to_sno.c` (`--transpile`).
- Runtime: `pattern_match.c`, `runtime_eval.c` (CODE/EVAL; the one granted global `g_sno_stmt_compiled`, CEO-1271), `string_ops.c`, `aggregates.c`, `keywords.c`, `io_format.c`; the leaves `rtx_match.s`, `rtx_str.s`, `rtx_table.s`; boxes `bb_match_*.cpp`.
- `./scrip --dump-ast|--dump-ir|--dump-plan prog.sno`; mode 3 `--run`, mode 4 `--compile --out=prog.s`.

## 4. The ARCH pages

ARCH-SNOBOL4-RTX.md (leaves, the register contract: r12 the conditional-assignment stack, r13 Σ, r14 δ, r15 Δ); ARCH-THREE-ZETAS-EMISSION.md and ARCH-ZETA-ONE-COORDINATE.md; ARCH-ZD-DEPTH-PLANNER.md; ARCH-ZETA-LAYOUT-ONE-SOURCE-OF-TRUTH.md (§ 9 the frame whack); ARCH-RT-CALL-PROTOCOL.md; ARCH-BUILTIN-TABLE.md; ARCH-LANGUAGES.md (Snocone's spellings).

## 5. The suites

- Keys: `sno-rungs`, `gimpel`, `csnobol4` (Budne), `snoflake`, `aisnobol`, `dotnet`, `testpgms`, `x64tests`, `x32tests`, `snobol4-bench-ref`, `snobol4-demos`, `snc-rungs`, `snocone-bench-ref`, `snocone-demos`, `reb-rungs`, `rebus-bench-ref`. Runners `harness/scripts/test_snobol4_*_suite.sh`, `test_snobol4_ladder.sh`, `test_snocone_*`, `test_rebus_*`.
- One program: `corpus_suite_harness.py run ../corpus/tests/snobol4/ALL.sno ../corpus/tests/snobol4/ALL.ref --lang snobol4 --modes m3,m4 --partition entry:<name>`. A master is a container, never run whole.
- Per landing: the DONE-WHEN, `test_feature_reps.sh snobol4 <feature>`, `test_smoke_snobol4.sh` (plus snocone and rebus smokes for their lowerers); then `s4e_test_request.sh <key> <entry>...` for the coo.
- Speed is open for SNOBOL4 by instruction count (`util_instr_count.sh`, `bench_snobol4_bar.sh`), behind correctness (CEO-1886/2035).

## 6. Debugging a red

1. Snocone first: transpile, make the `.sno` run on `sbl -bf`, then `bash ../harness/scripts/monitor_run.sh prog.sno --oracle`: the bug lies between the last agreeing and first diverging event.
2. Asm-diff the smallest repro beside a passing sibling within one mode.
3. `--dump-plan`, `SCRIP_ZD_CHECK=1` for placement; `SCRIP_GC_STRESS=1` for a collector suspicion.
4. gdb last, with a breakpoint and a hit count.

## 7. Rulings a landing must not break

- SPITBOL semantics, case-sensitive, `-bf` always.
- The three zetas are the model: a pattern box's cells default to the RSP spine; the match frame is set once at `S ? P`; the conditional-assignment stack is the r12 island; a retry never restores RSP.
- Every pattern node is a four-port box; a defect in one member of a box family is a class defect; no C function enters a box (CEO-1576).
- The `.sc` parsers are never rewritten (Lon 2026-09-24); the method is transpile, SPITBOL, monitor.
- Snocone is C surface over SPITBOL: `#` an OPSYN operator, `//` and `/* */` comments, `a[i,j]`, `|` alternation, `&&` concatenation; a census names both spellings of what Snocone spells twice.
- CODE/EVAL under the one granted global; LOAD/UNLOAD/SAVE/EXEC are a feature, not an error path.
- Beauty is its own oracle (`beauty.sno < beauty.sno` is the identity); no md5 pinned.
- A grammar edit needs `regenerate_parser_and_lexer_from_sources.sh`; a cure that trades one program for another never lands (CEO-589).
