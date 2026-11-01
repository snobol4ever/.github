---
name: icon
description: SCRIP's Icon (Arizona Icon 9.5.25a is the oracle; semicolons required): src/parsers/icon, lower_icon.c, the Icon rtx leaves, the IPL, Arizona, Jcon and IcnRungs suites and refs, generators, scanning, co-expressions. REQUIRED by the skill gate before editing the Icon parser, lowerer or prelude.
---

# SCRIP Icon

The record is GOAL-ICON-100.md (LIVE CURSOR, newest first); a page beats this skill. Icon is the SNOBOL4 machine with a second syntax; the Unicon superset (CEO-2072, ARCH-UNICON.md) extends it with no switch. Suite tables, file maps and receipts in full are in `reference.md` beside this file.

## 1. The oracle

- **One oracle: Arizona `icont`/`iconx` 9.5.25a** under `/home/resources/icon-master/bin/`, through `icont_bin()`, `iconx_bin()` in `harness/scripts/lib_oracle_flags.sh`, never `command -v`. No dialect marker, no jcon arm (CEO-390).
- **Semicolon-required, newlines are whitespace** (CEO-495/544, settled): `;` separates statements; none before `end`. Every shipped `.icn` carries them.
- A ref is cut from the oracle; no XFAIL. A ref the oracle cannot produce (it does not terminate, or its own defect) comes from the second implementation and is NAMED in `OUTSIDE_ARIZONA_BASELINE.tsv` (CEO-491). Refusal, crash or hang is `NO_ORACLE_ANSWER` (CEO-1696).
- Runtime errors are iconx's numbers and texts; the traceback names every frame as iconx does.

## 2. The manuals

`/home/resources/manuals/icon/icon-book-3rd-edition.txt`, `icon-doc-*.txt`, `goal-directed-evaluation-simple-translation.txt` (Proebsting), the Unicon reports and book; the oracle's sources `/home/resources/icon-master/src/runtime/`; `/home/resources/manuals/byrd-boxes/`. Before ruling on a builtin: grep the book, then `icont`/`iconx` on a five-line probe.

## 3. The source map

- Parser `src/parsers/icon/` (hand-written `icon_lex.c`, `icon_parse.c`, `icon_driver.c`, `icon_runtime.c`); the bootstrap `parser_icon.sc`.
- Lowering `src/lower/lower_icon.c`: every expression a four-port box; generators, `every`, `suspend`, alternation, scanning (`s ? e` as ENTER/LEAVE), tables and sets, the block protocol (an Icon call crosses no C helper).
- Runtime: `src/runtime/rtx/rtx_icn{agg,call,gen,num,rel,sub,var}.s`, `rt/rt_coexpr.c` (co-expressions), `rt_sg_scan.S`, `keywords.c` (`&subject` and `&pos` derived from r13/r14/r15 at the read), `aggregates.c`, `string_ops.c`.
- `./scrip --dump-ast|--dump-ir|--dump-plan prog.icn`; mode 3 `--run`, mode 4 `--compile`.

## 4. The ARCH pages

ARCH-ICON-RTX.md (leaves, register contract, § 9 the activation record as frame, § 10 the scanning environment in three registers); ARCH-SNOBOL4-RTX.md, ARCH-THREE-ZETAS-EMISSION.md, ARCH-ZETA-ONE-COORDINATE.md; ARCH-ENGINE.md (co-expressions); ARCH-GC-COMPILE-TIME-FRAME-MAPS.md; ARCH-CALL-FORMS.md, ARCH-BUILTIN-TABLE.md; ARCH-UNICON.md.

## 5. The suites

- Keys and runners in `harness/scripts/`: `icn-rungs` (`test_icon_ladder.sh`), `arizona` (`test_icon_arizona_suite.sh`), `ipl` (`test_icon_ipl_suite.sh`), `jcon` (`test_icon_jcon_suite.sh`), `icon-bench-ref`, `icon-demos`.
- One program: `corpus_suite_harness.py run ../corpus/tests/icon/ALL.icn ../corpus/tests/icon/ALL.ref --lang icon --modes m3,m4 --partition entry:<name>`; a package program by its runner with `S4E_CHUNK=entry:<name>`.
- Per landing: the DONE-WHEN, `test_feature_reps.sh icon <feature>`, `test_smoke_icon.sh`; then `s4e_test_request.sh` for the coo. Speed is open for Icon by instruction count, behind correctness (CEO-1886/2035).

## 6. Debugging a red

1. `bash ../harness/scripts/monitor_run.sh prog.icn --oracle` (the instrumented iconx fork); `--modes` for mode 3 against mode 4.
2. Asm-diff the smallest repro beside a passing sibling within one mode.
3. Placement: `util_bb_placement_census.py --lang icon`, `SCRIP_ZD_CHECK=1`.
4. gdb last, with a breakpoint and a hit count (hardware watchpoints are unreliable here).

## 7. Rulings a landing must not break

- No software value stack; the activation record IS the frame (ARCH-ICON-RTX § 9, CEO-1542).
- The scanning environment is (r13, r14, r15) at every instruction of an Icon graph: `&subject` is `{DT_S, r15d, r13}`, `&pos` is `r14 + 1`, derived at the read; no `scan_subj`, `scan_pos` or `in_scan` returns.
- A co-expression runs on the pthread's own mmap'd stack: never a heap block, never pinned.
- An Icon call crosses no C helper (CEO-1488/1491); `main` is an ordinary procedure; no C function enters a box (CEO-1576).
- Semicolons are settled law; one oracle; an outside-baseline ref is named or it is not a ref.
- The three zetas: every operand starts on the RSP spine; the planner alone decides; a retry never restores RSP.
- **The length is carried, never measured** (2026-11-01 IPL cures): a slice of a scanned subject (`tab`, `move`, `=`, a section of `&subject`) is `{DT_S, slen, ptr into the subject}` and is NOT NUL-terminated. Never feed `.s` to `strcmp`, `strlen` or a C-string table; use `slen` or `rt_cstr_d`. A synthesized `TT_QLIT` needs its `slen` (mode 4 reads a zero length literally). When a library procedure is red, ask what differs between a `tab()` slice and a literal.
- A cure that trades one program for another never lands (CEO-589); an Icon emitter or lowerer change regenerates the Icon benchmark `.s` in the coo's pass.
