# SCRIP Icon: the reference (the detail behind SKILL.md; read the section you need)

The record is `.github/GOAL-ICON-100.md` (LIVE CURSOR entries, newest first). Verified 2026-11-01 against SCRIP 9cb24d2ca; the Icon and Unicon ARCH pages are retired into this skill (`.github/RETIRED-ARCH-PAGES.tsv`).

## 1. The oracle and the dialect rule (CEO-390, CEO-491, CEO-495, CEO-544)

- **ONE ORACLE, ONE FEATURE SET: Arizona `icont`/`iconx` v9.5.25a**, the SCRIP-dialect build under `/home/resources/icon-master/bin/`, reached through `icont_bin()`, `iconx_bin()` and `icon_bin()` in `harness/scripts/lib_oracle_flags.sh`, never `command -v` (a seat once wrote "no Icon oracle exists" from a PATH miss). The source-keyed dialect switch is RETIRED: `#SRC: JCON` is upstream Arizona content, so no marker in a program names a dialect, and `g_jcon` is deleted (CEO-390).
- **SCRIP Icon is SEMICOLON-REQUIRED and newlines are whitespace** (Lon 2026-09-10, CEO-495; settled law, never raised again, CEO-544): `;` is a SEPARATOR between statements, so the last statement before `end` needs none; every shipped `.icn` carries a semicolon terminating every statement AND none where Icon forbids one (`icont -s -c` accepts it). A corpus file that satisfies one side and not the other is red (`util_icon_semicolons.py`, `util_icon_semicolon_class_classifier.py`).
- **A ref is cut from the oracle, never from our output; there is no XFAIL.** A ref the oracle CANNOT produce -- it does not terminate (lgint) or its own defect (toby: `to` wraps past maxint) -- is taken from the second implementation's shipped output and NAMED in `OUTSIDE_ARIZONA_BASELINE.tsv` with its provenance (CEO-491): a named exception class, not a second oracle. The Jcon suite keeps its own `.std` oracle, but a `.std` line stating a jcon-implementation fact (the `&features` list) is not an Icon fact. What the oracle refuses, crashes on or hangs is `NO_ORACLE_ANSWER` (CEO-1696).
- Runtime errors are iconx's numbers and texts (`error 103`, `error 205`: `test_gate_icn_a_trapped_substring_past_its_shrunk_subject_raises_205.sh`); the traceback names every frame as iconx does, a generator frame and a co-expression activation included (the `corpus/tests/icon/*traceback*` witnesses).

## 2. The manuals (text, grep them)

- `/home/resources/manuals/icon/icon-book-3rd-edition.txt` (The Icon Programming Language, 3rd edition: the language), `icon-doc-*.txt` (the implementation docs: `cfuncs`, `extlvals`, `files`, `relnotes`, `faq`, `build`, `port`), `goal-directed-evaluation-simple-translation.txt` (Proebsting's translation of goal-directed evaluation, the model every generator compiles to), `unicon-utr{2,3,5,8}.txt` (Unicon technical reports) and `unicon-book-*.txt` (the Unicon book, 31 chapters, CEO-2072). `PROVENANCE.txt` names each source.
- The oracle's own sources and tests: `/home/resources/icon-master/` (`src/runtime/` for a builtin's exact behaviour, `tests/` the Arizona suite as shipped); the IPL as shipped under `corpus/packages/icon/ipl/`; Jcon under `/home/resources/jcon-master` and `corpus/packages/icon/jcon-ref/`.
- The Byrd-box literature: `/home/resources/manuals/byrd-boxes/` (`1999-proebsting-new-implementation-icon-language.txt`, `2001-danvy-unifying-approach-goal-directed-evaluation.txt`).
- Before ruling what a builtin does: `grep -n -A8 'bal(' /home/resources/manuals/icon/icon-book-3rd-edition.txt`, then `icont` and `iconx` on a five-line probe (`write` each result). The book says what; the oracle's output is the ref.

## 3. The source map

- Parser: `SCRIP/src/parsers/icon/` -- `icon_lex.c/.h` (hand-written lexer; `icon_lex_test.c`), `icon_parse.c/.h` (hand-written recursive descent building `tree_t`; `icon_parse_test.c`), `icon_driver.c/.h` (the entry), `icon_runtime.c` (the three Icon-only runtime functions: `icon_compile`, `icon_register_program`, `icon_real_str`; everything else Icon calls is the shared runtime). The bootstrap parser is `SCRIP/bootstrap/parser_icon.sc`.
- Lowering: `SCRIP/src/lower/lower_icon.c` -- every expression a four-port box; generators, `every`, `suspend`, alternation, limitation, string scanning (`s ? e` as ENTER/LEAVE with the environment banked in the nodes' own cells), tables and sets (`key(t)` and `!t` through an Icon-order index built once per shape), `x[i] := v` as the three-operand store, `main` an ordinary procedure, the block protocol (an Icon call crosses no C helper, CEO-1488/1491).
- Runtime: the Icon rtx leaves `src/runtime/rtx/rtx_icn{agg,call,gen,num,rel,sub,var}.s` (skill `rtx-asm-leaves`), `src/runtime/rt/rt_coexpr.c` (co-expressions on the pthread's own mmap'd stack, never a heap block, Lon 2026-09-02), `rt_sg_scan.S` (cset and string-set scans), `keywords.c` (the keyword table; `&subject` and `&pos` are DERIVED from r13/r14/r15 at the read, never stored), `aggregates.c`, `string_ops.c`, `icn_extfn.c`.
- Pipeline: parser → lower → optimizer → planner → the one emitter. `./scrip --dump-ast|--dump-ir|--dump-bb|--dump-zeta|--dump-plan prog.icn`. `--run` is mode 3; `--compile --out=prog.s` mode 4, linked PIE against `out/libscrip_rt.so`.

## 4. The related skills, by question

| question | skill or section |
|---|---|
| the Icon rtx leaves and the register plane (r13 Σ, r14 δ, r15 Δ) | `rtx-asm-leaves` |
| the three zetas Icon rides: the cell frame, the spine, generators as retaining edges, the plan | `scrip-memory-model` |
| co-expressions on their own pthread stacks; the call protocol; generator procedures | `scrip-architecture` § 5, `runtime-calls` |
| the collector and Icon's frames, the co-expression segments | `gc-collector` |
| the call forms, the builtin table (its Icon step 4) | `box-templates`, `runtime-calls` |
| SCRIP's own future JVM, .NET, JS and WASM targets | `scrip-backends` |
| the Unicon superset: markers, classes, packages, the oracle | this file § 8 |
| the scanning-asm and unicon plans | this file § 9 |

## 5. The suites and how one program is graded

| suite key | runner | population |
|---|---|---|
| icn-rungs (IcnRungs) | `test_icon_ladder.sh --list | --to N | --only N`, `test_icon_all_rungs.sh`; one entry: `corpus_suite_harness.py run ../corpus/tests/icon/ALL.icn ../corpus/tests/icon/ALL.ref --lang icon --modes m3,m4 --partition entry:<name>` | `corpus/tests/icon/` (`ALL.csv` with `heap_kb`/`stack_kb`, `ALL.in`, `ALL.argv`, `ALL.rc`, `ALL.omit`, `PARTITION.tsv`, `LADDER.tsv`) |
| arizona (Zona) | `test_icon_arizona_suite.sh` | `corpus/packages/icon/arizona_tests/` (the oracle's own tests) |
| ipl (IPL) | `test_icon_ipl_suite.sh` (`lib_icon_ipl_isolation.sh`, `util_icon_package_units.py`) | `corpus/packages/icon/ipl/` (843 shipped, 644 the denominator after containers and the excluded) |
| jcon (Jcon) | `test_icon_jcon_suite.sh`, `test_demo_icon_jcon.sh`, `test_demo_icon_jcon_selfhost.sh` | `corpus/packages/icon/jcon_tests/`, `jcon-compiler/` (the self-host is the big-program GC measure) |
| icon-bench-ref, icon-demos | `test_icon_bench_suite.sh`, `bench_icon_bar.sh`, `bench_icon_ir_bar.sh` | `corpus/benchmarks/icon/` (committed `.s`), `corpus/demos/icon/` |

A package program: its runner with `S4E_CHUNK=entry:<name>`. A seat grades ONE program in both modes; the suite is the coo's (`s4e_test_request.sh <suite-key> <entry>...`, at most eight). Per landing: the DONE-WHEN, `test_feature_reps.sh icon <feature>...`, `test_smoke_icon.sh`; `test_design_icon_scanning_asm_steps.sh --list | --step N` for the scanning design. Speed is OPEN for Icon by instruction count (`util_instr_count.sh`, `bench_icon_ir_bar.sh`; a clock only in `util_quiet_slice.sh`), behind correctness (CEO-1886/2035).

## 6. Debugging an Icon red

1. `bash ../harness/scripts/monitor_run.sh prog.icn --oracle` (`icx`, the instrumented iconx fork under `/home/resources/icon-mon/`): the bug lies between the last event both agree on and the first they diverge on; `--modes` for mode 3 against mode 4; `--input FILE`.
2. ASM-DIFF-FIRST: the smallest repro beside a passing sibling, `--compile` both, diff within one mode.
3. The placement instruments: `util_bb_placement_census.py --lang icon`, `util_icn_rbp_census.py`, `util_icn_class_witness.sh`, `util_icon_disjunction_spine_witness.sh`; `SCRIP_ZD_CHECK=1` for the depth verifier.
4. Only then gdb with a breakpoint and a hit count; a hardware watchpoint is unreliable here.

## 7. Rulings an Icon landing must not break (receipts in GOAL-ICON-100.md and GOAL-CEO.md)

- **No software value stack, one-register frame** (RULES.md; "ICON STACKLESS" is a void name since all three zetas are on the stack): no `g_vstack`, no runtime-held stack; the activation record IS the frame (CEO-1542).
- **The scanning environment is (r13, r14, r15) at every instruction of an Icon graph** (§ 10.2 R1-R5): `&subject` is `{DT_S, r15d, r13}` and `&pos` is `r14 + 1`, derived at the read; the registers are live-through across every Icon-to-Icon transfer; `s ? e` is three moves each way with the banks in the ENTER and LEAVE nodes' own cells; every scan builtin is one box with every form; no `scan_subj`, `scan_pos`, `g_scan_regs_live` or `in_scan` returns.
- **A co-expression runs on the pthread's own mmap'd stack** (Lon 2026-09-02): never a heap block, never the slab, never pinned.
- **An Icon call crosses no C helper** (the block protocol, CEO-1488/1491); `main` is an ordinary procedure that returns to its caller in both modes; no C function enters a box (CEO-1576); Byrd boxes are maximally preferred (CEO-2045).
- **Semicolons are settled law** (CEO-495/544): no newline insertion, ever; the corpus carries them.
- **One oracle** (CEO-390): no dialect marker, no jcon arm, no `--compat`; an outside-baseline ref is named in `OUTSIDE_ARIZONA_BASELINE.tsv` or it is not a ref.
- **The three zetas and the placement criterion** (CEO-1750/1895): every operand and local starts on the RSP spine; the planner alone decides a home; a retry never restores RSP (`test_gate_no_rsp_reset_at_beta.sh`); the compile-time frame maps stay and the collector guesses nothing (CEO-1368/1371).
- **THE LENGTH IS CARRIED, NEVER MEASURED** (the 2026-11-01 IPL cures, SCRIP `56408ef53` `a87ccbeaf` `a66b41a27` `01933730c`; `scan-derived-strings-are-not-nul-terminated`): a string cut out of a scanned subject (`tab`, `move`, `=`, a section of `&subject`) is `{DT_S, slen, ptr into the subject}` and is NOT NUL-terminated at `slen`; a string from `string()` or a section expression is a copy and is, which is what hides the defect. Every `strcmp`, `strlen` or `char *` table lookup fed `.s` (`idx.s`, `callee.s`, `args[0].s`, a record field name, a procedure name, a keyword name for `variable()`) reads past the slice. Take the carried length (`slen`), or `rt_cstr_d` (it materializes a terminated copy only when `s[slen] != 0`, `src/ir/descr.h`). A synthesized tree node (`TT_QLIT`) needs its `slen` too: mode 3 falls back to `strlen`, mode 4 reads a zero length literally. Method: when a library procedure is red, ask what differs between a slice from `tab()` and a literal, and grep the runtime for `.s` handed to a C-string table before adding the witness.
- An Icon emitter or lowerer change regenerates the Icon benchmark `.s` (`update_icon_bench_asm.sh`) in the coo's maintenance pass; a cure that trades one program for another never lands (CEO-589); the Icon smoke runs before every push, all eight for shared code.

## 8. The Unicon superset

Moved to skill `unicon` (Lon 2026-11-04: "Does the exist a UNICON skill? If not, there should be one."): the markers, the oracle, the classes, the packages, the pattern type, threads, the UniTests package and the Unicon rungs 43 to 49. Load it with this skill for any Unicon edit.

## 9. DESIGN (the live and finished plans of this language)

- **icon-scanning-asm** (CEO-1969/1970/1998; `corpus/tests/icon/scanning_asm/STEPS.tsv`): the scanning environment is three registers and all of scan is emitted (Lon 2026-10-24: "I'm thinking that ALL of SCAN should be 100% pure ASM."). All seven steps DONE (tab and move share the subject bytes; every form is the box; the explicit-subject forms; the co-expression switch carries three words; the C-frame road carries the words explicitly; the root and the keyword assign inside a scan; the finish).
- **unicon** (skill `unicon` § 5; CEO-2072; `corpus/tests/icon/unicon/STEPS.tsv`, `test_design_unicon_steps.sh`): 1 the markers, 2 the class model, 3 packages, import and link, 4 the builtin families, 5 the finish; worked by hq_unicon under its UniTests row (CLAIMED), the posix family its next row (ASSIGNED). Read a step's state with `--step N`.
