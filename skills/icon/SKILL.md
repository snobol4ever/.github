---
name: icon
description: SCRIP's Icon (Arizona Icon 9.5.25a the oracle): src/parsers/icon, lower_icon.c, the IconProgLibrary, IconArizona, IconJconTests and IconRungs suites, generators, scanning, co-expressions. REQUIRED by the skill gate before editing the Icon parser, lowerer or prelude.
---

# SCRIP Icon

The record is GOAL-ICON-100.md (LIVE CURSOR, newest first); a page beats this skill. Icon is the SNOBOL4 machine with a second syntax; the Unicon superset (CEO-2072; skill `unicon`) extends it with no switch. Suite tables, file maps and receipts in full are in `reference.md` beside this file.

## 1. The oracle

- **One oracle: Arizona `icont`/`iconx` 9.5.25a** under `/home/resources/icon-master/bin/`, through `icont_bin()`, `iconx_bin()` in `/home/harness/scripts/lib_oracle_flags.sh`, never `command -v`. No dialect marker, no jcon arm (CEO-390).
- **Semicolon-required, newlines are whitespace** (CEO-495/544, settled): `;` ends every statement of a procedure body, the last one before `end` too (MEASURED 2026-11-13 on `scrip --dump-ast`: `return 1`, a bare `return`, `fail` and an expression statement directly before `end` are each refused with expected ';', and `return 1;` parses; the parser is `stmt_end` in icon_parse.c), and separates the statements of a `{ }` block, whose last expression is bare. Every shipped `.icn` carries them.
- **`&progname` is the stem** (the coo 2026-11-13, on junior_08's measurement of gate_cases_icon pinwitness): SCRIP runs a program as `icont` then `iconx` does, and its driver cuts the extension on purpose (src/driver/scrip.c), so a ref that prints `&progname` is cut by the built convention (`run_icon_built_oracle`, iconx on the stem), as arizona's and jcon's `kwds` refs are, never by the one-step `icon` driver, which keeps the `.icn`.
- **THE GRAPHICS ORACLE'S LIBRARY IS COMPILED BY ITS OWN TRANSLATOR** (the cto 2026-11-16 16:2x CST: the oracle stands for Arizona Icon with graphics, and an accident of our build is not Arizona's behaviour; built by officer_02): `/home/resources/icon-master-x/lib` is the plain build's library copied beside it (2026-11-14), whose `$ifdef _X_WINDOW_SYSTEM` arms are the plain ones (viface's vidget font, vtext's arrow keys); `/home/resources/icon-master-x/libx` is the stock `ipl/Makefile` recipe (`icont -usc`) run with the X oracle's icont, which defines `_X_WINDOW_SYSTEM` and `_GRAPHICS`, on corpus's semicolon text, made again by `/home/resources/progress/icon-graphics-2026-11-16/oracle-lib-officer_02/make_libx.sh`. Every graphics oracle cut links it: `IPATH="$GRAPHICS_ICON_ORACLE_LIB"` (`lib_oracle_flags.sh`; the shared staging `ipl_graphics_stage.py` sets it for the one prover and the launcher). icont with no IPATH links its tree's own `lib`, so a hand cut names the variable. MEASURED at the switch: 383 of 392 modules byte equal; one answer of every graphics entry read moved, fontpick's.
- **A PERSON SEES A GRADED GRAPHICS ENTRY THROUGH ONE LAUNCHER** (the cto 2026-11-16 15:2x CST, built by officer_02): `python3 /home/harness/scripts/icon_demo.py NAME` runs the entry NAME of ipl_gprogs, ipl_gpacks or ipl_gprocs on SCRIP in mode 3 on the caller's DISPLAY, staged as the one prover stages it (`ipl_graphics_stage.py`, which `prove_ipl_gprogs_entry.py` imports: arguments, stdin, fixtures, companions), SCRIP named by `S4E_SCRIP` or `--scrip DIR`; `--oracle` runs it on the graphics oracle beside it; `--list` names every entry with its Subject line; `--keys NAME` prints the program's header on how it is driven; `--probe` is its proof on the screen road.
- **A SEAT NEVER RUNS THE LAUNCHER ON DISPLAY 0**, which is Lon's screen: with `S4E_SEAT` set it refuses `:0` rc 2, and with no DISPLAY it refuses rc 2; a seat's run of a graphics program is the road's, on a display of its own.
- A ref is cut from the oracle; no XFAIL. A ref the oracle cannot produce (it does not terminate, or its own defect) comes from the second implementation and is NAMED in `OUTSIDE_ARIZONA_BASELINE.tsv` (CEO-491). Refusal, crash or hang is `NO_ORACLE_ANSWER` (CEO-1696), and so is an oracle that answers differently on two runs (the cto 2026-11-14, row ipl-red-progs-csgen, on senior_01's measurement: four runs of `progs/csgen`, which calls `randomize()`, gave four md5s; the oracle is run twice through the one-step driver before the row is written, and a validator is never a ref).
- Runtime errors are iconx's numbers and texts; the traceback names every frame as iconx does.
- **GRAPHICS IS IN: X-Windows programs are graded off-line, under a virtual display** (Lon 2026-11-14 15:4x CST, in the grader's window, verbatim: "We are absolutely DOING GRAPHICS, X-windows. Yes? We should be able to do off-line (i.e. without physical window in which a human user is required) GUI tests. Yes?"; it REVERSES his word of 2026-09-27, "Place the graphics programs on the exclude list.", so the class `NEEDS_GRAPHICS_FACILITY` written on that word is a debt from now, never a closed fact). MEASURED that hour by the grader: the two oracles the fleet grades by have no graphics (the `&features` of `/home/resources/icon-master/bin/iconx` and of unicon 13.3 carry no graphics line); `Xvfb`, `xvfb-run` and `xwd` are installed with the X development libraries; two graphics builds of Arizona Icon 9.5.25a now stand beside the plain oracle, which is unchanged: `/home/resources/icon-stock-x` (the pristine source, newline insertion, with its own 793-file library and the tools `colrbook`, `vib` and kin) and `/home/resources/icon-master-x` (the fleet's semicolon-required translator, the plain oracle's library copied beside it); a drawing program run twice under `xvfb-run` gave the same text and the same GIF, byte for byte, and with no display it answers `no window` (`/home/resources/progress/handoffs/grader-2026-11-14/gfx_census.py` is the census of the library's 177 graphics programs on that road). THE ACCESSORS (officer_06 2026-11-16, harness 3eea3a22f and 8b0b9e4ea): `graphics_icont_bin`, `graphics_iconx_bin` (this build, `/home/resources/icon-master-x`) and `graphics_unicon_bin` (skill `unicon` R2) in `lib_oracle_flags.sh`, never a bare path; `graphics_display_run CMD` runs CMD under an Xvfb of its own (`-displayfd`, so two callers never race) with the caller's `DISPLAY` removed, since a seat's session may carry the desktop's `:0` and a window opened there is on Lon's screen (MEASURED that day); `util_graphics_oracles_check.sh` proves both oracles draw one probe twice alike and print the same pixels. WHAT IS OWED: SCRIP has no graphics built-in (no `WOpen` in any source file of SCRIP), which is the cto's design, ruled 2026-11-16 to stand as designed on 2026-11-10 and written in `reference.md` section 9, THE WINDOW FACILITY (the oracle's own window source translated by a script, its memory converted to the collected heap and the stack, the 48 functions entered through the loaded-function adapter; steps W1 to W7); then the 183 ipl, 43 unicon_uni and 5 unitests rows excluded `NEEDS_GRAPHICS_FACILITY` are cut again. THE HARNESS'S GRAPHICS ROAD IS BUILT (skill `suites-and-grading` section 4, THE SCREEN ROAD): a run under a virtual display, the answer its text and its window's pixels, and a program that waits for a mouse or a key is given scripted events from `NAME.events` beside its entry (W7, the cqo 2026-11-16, harness d54306e6).

## 2. The manuals

`/home/resources/manuals/icon/icon-book-3rd-edition.txt`, `icon-doc-*.txt`, `goal-directed-evaluation-simple-translation.txt` (Proebsting), the Unicon reports and book; the oracle's sources `/home/resources/icon-master/src/runtime/`; `/home/resources/manuals/byrd-boxes/`. Before ruling on a builtin: grep the book, then `icont`/`iconx` on a five-line probe.

## 3. The source map

- Parser `src/parsers/icon/` (hand-written `icon_lex.c`, `icon_parse.c`, `icon_driver.c`, `icon_runtime.c`); the bootstrap `parser_icon.sc`.
- Lowering `src/lower/lower_icon.c`: every expression a four-port box; generators, `every`, `suspend`, alternation, scanning (`s ? e` as ENTER/LEAVE), tables and sets, the block protocol (an Icon call crosses no C helper).
- Runtime: `src/runtime/rtx/rtx_icn{agg,call,gen,num,rel,sub,var}.s`, `rt/rt_coexpr.c` (co-expressions), `rt_sg_scan.S`, `keywords.c` (`&subject` and `&pos` derived from r13/r14/r15 at the read), `aggregates.c`, `string_ops.c`.
- `./scrip --dump-ast|--dump-ir|--dump-plan prog.icn`; mode 3 `--run`, mode 4 `--compile`.

## 4. The related skills

`rtx-asm-leaves` (the Icon leaves `rtx_icn*.s`, the register plane: r13 Σ, r14 δ, r15 Δ inside a scan); `scrip-memory-model` (the cell frame of an Icon procedure, the spine, generators as retaining edges); `gc-collector` (co-expression segments, the allocating-box polls); `runtime-calls` (the call protocol, generator procedures, the builtin table's Icon step, `&error` and `runerr` on the error protocol); `box-templates`; `scrip-backends` (SCRIP's future targets). The Unicon superset is skill `unicon` (load it for any Unicon edit); the design plans are in `reference.md` § 9.

## 5. The suites

- Keys and runners in `/home/harness/scripts/`: `icn-rungs` (`test_icon_ladder.sh`), `arizona` (`test_icon_arizona_suite.sh`), `ipl` (`test_icon_ipl_suite.sh`), `jcon` (`test_icon_jcon_suite.sh`), `icon-bench-ref`, `icon-demos`.
- One program: `corpus_suite_harness.py run ../corpus/tests/icon/ALL.icn ../corpus/tests/icon/ALL.ref --lang icon --modes m3,m4 --partition entry:<name>`; a package program by its runner with `S4E_CHUNK=entry:<name>`.
- Per landing: the DONE-WHEN, `test_feature_reps.sh icon <feature>`, `test_smoke_icon.sh`; then `s4e_test_request.sh` for the coo. Speed is open for Icon by instruction count, behind correctness (CEO-1886/2035).

## 6. Debugging a red

1. `bash ../harness/scripts/monitor_run.sh prog.icn --oracle` (the instrumented iconx fork); `--modes` for mode 3 against mode 4.
2. Asm-diff the smallest repro beside a passing sibling within one mode.
3. Placement: `util_bb_placement_census.py --lang icon`, `SCRIP_ZD_CHECK=1`.
4. gdb last, with a breakpoint and a hit count (hardware watchpoints are unreliable here).

## 7. Rulings a landing must not break

- No software value stack; the activation record IS the frame (CEO-1542).
- The scanning environment is (r13, r14, r15) at every instruction of an Icon graph: `&subject` is `{DT_S, r15d, r13}`, `&pos` is `r14 + 1`, derived at the read; no `scan_subj`, `scan_pos` or `in_scan` returns.
- A co-expression runs on the pthread's own mmap'd stack: never a heap block, never pinned.
- An Icon call crosses no C helper (CEO-1488/1491); `main` is an ordinary procedure; no C function enters a box (CEO-1576).
- Semicolons are settled law; one oracle; an outside-baseline ref is named or it is not a ref.
- The three zetas: every operand starts on the RSP spine; the planner alone decides; a retry never restores RSP.
- **The length is carried, never measured** (2026-11-01 IPL cures): a slice of a scanned subject (`tab`, `move`, `=`, a section of `&subject`) is `{DT_S, slen, ptr into the subject}` and is NOT NUL-terminated. Never feed `.s` to `strcmp`, `strlen` or a C-string table; use `slen` or `rt_cstr_d`. A synthesized `TT_QLIT` needs its `slen` (mode 4 reads a zero length literally). When a library procedure is red, ask what differs between a `tab()` slice and a literal.
- A cure that trades one program for another never lands (CEO-589); an Icon emitter or lowerer change regenerates the Icon benchmark `.s` in the coo's pass.
