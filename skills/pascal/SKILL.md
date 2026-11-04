---
name: pascal
description: SCRIP's Pascal (ISO 7185 base; FPC, ObjFPC and Delphi dialects over fpc 3.2.2): src/parsers/pascal, lower_pascal*.c, the prelude units, the PasRungs, PAT, FPC, PasRosetta, PasDemo and PasBench suites and refs, types, strings, units, classes. REQUIRED by the skill gate before editing the Pascal parser, lowerer or prelude.
---

# SCRIP Pascal

The record is GOAL-PASCAL-100.md (LIVE FRONT on top); a page beats this skill. Pascal's front-end design is hq_pascal's (CEO-1933); the cto reviews shared nodes. Suite tables, file maps and receipts in full are in `reference.md` beside this file.

## 1. The oracle and the dialect

- **fpc 3.2.2 in the program's own mode** through `fpc_bin()` in `harness/scripts/lib_oracle_flags.sh`: ISO 7185 under `fpc -Miso`, FPC/Turbo plain, `-Mobjfpc`, `-Mdelphi`. ISO 7185 wins where `-Miso` is lax (CEO-1225).
- **The program's dialect decides its oracle**, one switch per program: a `{$mode X}` directive, else ISO until the first construct `-Miso` refuses (`string` in a type position, `otherwise`, `string[n]`, `uses`, `unit`, `class`, `object`, `try`) (CEO-1624). Never guessed from a filename; no `--compat`.
- ISO Pascal is CASE-INSENSITIVE. `string` is `ShortString(255)` without `{$H+}`, `AnsiString` with it and in delphi mode.
- A ref is cut from the oracle; no XFAIL; what fpc refuses, crashes on or hangs is `NO_ORACLE_ANSWER` (CEO-1696). A unit's `finalization` output never appears (fpc closed the files first, CEO-1617).

## 2. The manuals

`/home/resources/manuals/pascal/iso7185-standard.txt`, `iso7185-rules.txt`, `wirth-1973-the-programming-language-pascal.txt`, `p5-compiler.txt`. Before ruling: grep the standard, then compile a three-line probe in the program's mode.

## 3. The source map

- Parser `src/parsers/pascal/` (`pascal.l`, `pascal.y`; generated twins by `regenerate_parser_and_lexer_from_sources.sh`), `pascal_driver.c`, `prelude/` (the units in Pascal, listed by `util_gen_pascal_prelude_units.py`); the bootstrap `parser_pascal.sc`.
- Lowering: `lower_pascal_tree.c` (scopes, the typer), `lower_pascal_types.c` (the type model), `lower_pascal_class.c`, `lower_pascal.c` (statements, units, the entry graph `main`).
- Runtime: the Pascal arms of the shared runtime (`arithmetic.c`, `io_format.c`, `string_builtins.c`, `builtins.tsv`); `core/g_runtime_pas.h`. A value is a DESCR, an array an ARBLK, a record a slot array.
- `--dump-ast|--dump-ir|--dump-plan`, `--dump-pas-types` (the typer's census).

## 4. The related skills

`lowering` (the pruned tree in, the IR out; `lower_pascal_tree.c` and the typer), `scrip-memory-model` (Pascal's frames and the display), `gc-collector` (the heap table, pointer values), `runtime-calls` (the builtin table, the FATAL road of the error protocol), `snocone-parser-patterns` (`parser_pascal.sc`). The dialect record, the pruned tree and the front-end plan are in `reference.md` § 8-9.

## 5. The suites

- Keys and runners in `harness/scripts/`: `pas-rungs` (`test_pascal_ladder.sh`), `pat` (`test_pascal_pat_suite.sh`; `iso7185prt*` are REJECTION tests: PASS is a non-zero exit with a diagnostic), `fpc` (`test_pascal_fpc_suite.sh`), `rosetta-pascal` (`test_pascal_rosetta_suite.sh`, `ALL.dialect` per program), `pascal-demos`, `pascal-bench-ref`, the P4/P5 self-hosts.
- One program: `corpus_suite_harness.py run ../corpus/tests/pascal/ALL.pas ../corpus/tests/pascal/ALL.ref --lang pascal --modes m3,m4 --partition entry:<name>`; a package program by its runner with `S4E_CHUNK=entry:<name>`.
- Per landing: the DONE-WHEN, `test_feature_reps.sh pascal <feature>`, `test_smoke_pascal.sh`; then `s4e_test_request.sh` for the coo. Design steps: `test_design_pascal_front_end_steps.sh --step N`.

## 6. Debugging a red

1. `bash ../harness/scripts/monitor_run.sh prog.pas --oracle` (fpc through the Pascal plug); `--modes` for mode 3 against mode 4.
2. Asm-diff the smallest repro beside a passing sibling within one mode.
3. `--dump-pas-types` for a typing question; `--dump-ir` A/B for a no-behaviour-change landing.
4. gdb last, with a breakpoint and a hit count.

## 7. Rulings a landing must not break

- One type model, built by lower, keyed by symbol, never by name; no second model beside the typer.
- DESCR cells, ARBLK arrays, records as slot arrays; a pointer is (base cell, element index), never an interior pointer (R5); `extended` is a boxed 80-bit leaf (R6), no x87 in the emitter.
- ShortString(N): a store truncates to N, `sizeof` is N+1, `s[0]` is the length byte (R4).
- The entry graph is `main`; a user routine named `main` is renamed by the duplicate-name pass.
- Features land in rungs of at most 20 lines, one construct, ref cut from fpc, red once (CEO-1680); rung N+1 opens when N is green in both modes.
- The PAT rejection tests are the ISO strictness: never adopt `-Miso`'s laxity.
- Regenerate the grammar, prelude list and builtin table before building; a cure that trades programs never lands (CEO-589); a prelude or runtime change runs all eight smokes.
- Declared sizes are a hard cap (CEO-1353/1354).

## 8. DESIGN: pascal-packed-arrays (CEO-2119, the cto 2026-11-04, on the cfo's PasRosetta reds fusc-sequence, strong-and-weak-primes, unprimeable-numbers-2)

A Pascal array, bounded or dynamic, whose element type is a flat ordinal of width 1, 2, 4 or 8 bytes (byte, shortint, char, boolean, word, smallint, longword, longint, int64, qword, an enumeration, a subrange) and none of whose components is ever referenced (passed as a var actual, taken with `@`, aliased by `absolute` or a `with`) is stored as ONE raw block: a header (element count, width, signedness, low bound) and the element bytes contiguous, no DESCR per element. The collector treats it as it treats a string block (raw bytes, no pointer inside: it guesses nothing because the block's tag says raw). The choice is made ONCE in `lower_pascal` from the declared element type and the component's use set in the pruned tree and rides as an IR fact (width and signedness on the element load and store nodes); the planner and the emitter read it; the template loads `movzx`/`movsx` by width into an integer DESCR and stores truncated to the width (no range check, as `fpc -Miso` without `-Cr`). Every other element type, and an ordinal array whose component is referenced, stays an ARBLK (law 8.2(2) stands; a pointer stays (base cell, element index)). MEASURED (the cfo, 2026-11-04): the three programs ask for one kind-214 block of 20, 8 and 16 GB before any collection (0.5 to 1.25 billion elements at 16 bytes where fpc holds 1 to 4), over the grader's 8 GB cap, so no declaration serves them. Witnesses: the three programs, red and named, never excluded, plus a rung: an array of 100,000,000 bytes at a declared heap of 256 MB (red by out-of-memory before, green after). The STEPS.tsv and `test_design_pascal_packed_arrays_steps.sh` are the plan's first step; the row is `pascal-rosetta-fusc-sequence-ooms-in-both-modes-...` (ASSIGNED:cto, TRIO row 6).
