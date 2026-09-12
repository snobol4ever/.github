# FINDING 2026-09-12 (cfo) -- the driver re-set the source name from the LAST argv slot after the `--` split, so every Icon traceback with program arguments named an argument as the file

**Seat:** cfo · **Row:** `icon-runtime-error-traceback-names-the-last-argv-as-the-file` (rank 2, minted by cfo 2026-09-12 from the shootout kernels) · **SCRIP:** `0b69658d8` · **Mode:** NONET, Icon order of work.

## What was measured

`procedure main(a); write(1 + a[1]); end` run as `scrip tb.icn -- x` died `File x; Line 2`; `fannkuch.icn -- 7` died `File 7; Line 58`; iconx says `File tb.icn; Line 2`. Error number and line were right. The same witness extended with `write(&file)` printed `file=y` for `-- x y` where iconx prints `file=tb.icn`. ⭐ MODE 4 WAS NEVER WRONG, measured on the pre-cure binary: the `--compile -o tb.s tb.icn` invocation carries no `--`, so the last argv slot IS the source and the sealed name is right; the baton's "same in m4, unverified" was a guess that the control arm corrected. Only m3, where the compile and the run share one command line, was red.

## The cause, in the driver, not the runtime

`src/driver/scrip.c` walks argv, and for each input it calls `stmt_src_set_file(path)` -- the ONE store every reader of the source name draws from: the Icon lowerer's `IR_LINE_MARK` file literal (sealed read-only at compile time), the `&file` keyword, `rt_main_progname_stage`, the DWARF location, and the runtime's `core_icn_report` through `g_file`. The walk stops at `--` and records the program arguments. Then, ~130 lines later, the driver did `input_path = argv[argc - 1]` and called `stmt_src_set_file` AGAIN. With no `--` that is the input file again (harmless, a second read of the source). With program arguments it is the LAST PROGRAM ARGUMENT: the stored name becomes `7`, `fopen("7")` fails, and -- a second effect nobody had noticed -- the source-line cache that the SPITBOL termination report and the DWARF emitter read was FREED and left empty.

## The cure (3 lines)

Remember the last input path during the walk and use it after the walk; `argv[argc-1]` stays only as the fallback when no input was walked. No runtime change, no template change; a driver-only rebuild costs seconds.

## Why the graded suites never saw it

A traceback goes to stderr, error refs are cut without arguments, and every ref-graded program that takes arguments is expected to exit 0. Only a user running a program with arguments that then dies meets it. The shootout kernels (`fannkuch.icn 7`) are the first graded programs that both take an argument and, under the Unicon-only builtins, die.

## Gate

`scripts/test_gate_icn_traceback_names_the_source_file_not_the_last_argv.sh`, wired into `make test` and adopted in `gate_wiring.tsv`: one witness run with two arguments in both modes, stdout (which prints `&file`) byte-identical to iconx, and the file-bearing traceback lines (`File ...; Line N`, `from line N in FILE`) matched line for line; `GATE_FAIL_ONCE=1` rewrites our File line to the last argument so the gate is seen to say no. Measured RED on the pre-cure binary (control arm by `git stash`), green after.

## The general law

**A value that is set correctly in one place and then re-derived "for convenience" in another is two sources of truth, and the second one is the bug.** The walk already knew the input; the re-derivation from `argc - 1` was right only while the command line had one shape. When a diagnostic names the wrong THING (a file that is not a file), look for where the name is STORED, not where it is PRINTED -- the printer was right.
