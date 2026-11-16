---
name: scrip-architecture
description: The map of SCRIP: the one pipeline (driver, parser, lower, optimizer, planner, emitter, runtime), modes 3 and 4, the IR types, the cross-layer rulings, which skill owns which layer. Load first when a task crosses layers or routes a red.
---

# SCRIP's architecture

One `scrip` binary compiles SNOBOL4, Snocone, Rebus, Icon (and its Unicon superset), Prolog, Raku and Pascal to x86-64. Every pattern, generator and goal is a four-port Byrd box (α proceed, β recede, γ succeed, ω concede) wired at compile time into straight-line jumps: SNOBOL4 patterns, Icon generators and Prolog backtracking are three syntaxes over one machine. The law is `/home/.github/RULES.md`; this skill is the map. Detail and the retired-name table are in `reference.md` beside this file.

## 1. The pipeline (each stage hands the next exactly one thing)

1. **Driver** `src/driver/scrip.c`: the extension picks the frontend from `scrip_exts[]` (an unknown extension refuses, it never guesses). `.scrip` and `.md` are polyglot: fenced blocks tagged SNOBOL4, Icon, Prolog, Raku, Rebus (`src/driver/polyglot.c`). The law since CTO-511 (Lon 2026-11-04; again 2026-11-16) is that every fenced section runs in document order like Jupyter's Run All, sharing the registry, the globals and the heap, and that a notebook is a second reader of the same runner printing the same; what the tree does of it is section 7, THE DOCUMENT ROAD.
2. **Parser** `src/parsers/<lang>/`: C front ends (bison and flex for SNOBOL4, Rebus, Pascal, Snocone; hand-written for Icon, Prolog, Raku). Output: the pruned parse tree `tree_t` (`src/ir/ast.h`). Only `tree_t` crosses to lower (CEO-1322/1369/1371/1377/1378). The seven Snocone parsers in `$S4E_SCRIP/bootstrap/parser_<lang>.sc` are the bootstrap: built as `out/parser_<lang>` by `make parsers-sc`, graded tree for tree against the C parsers (skill `snocone-parser-patterns`).
3. **Lower** `src/lower/lower_<lang>*.c`: `tree_t` in, `IR_graph_t` population out, registered in `g_stage2.bbp` by `bb_program_add`. The driver runs each segment's lowerer (`lower_sno_stage2`, `lower_icon_stage2`, `lower_pl_stage2`, ...) inside `sm_preamble` (`src/driver/scrip_sm.c`). Every runtime table is built here; every builtin is resolved here (skill `lowering`).
4. **Optimizer** `src/optimizer/optimizer.c`: `optimizer_run(g)` per graph (constant and arithmetic folding, copy propagation, dead code, branch chains).
5. **Planner** `src/planner/`: `planner_stage_procs`, `planner_stage_main`, `planner_stage_proc`. Placement of every cell on the three zetas is decided once, here, into the plan table (CEO-1895; skill `scrip-memory-model`).
6. **Emitter** `src/emitter/emit.cpp`: `walk_bb_node_inner` binds each IR kind to its box template through `bb_emit_x86(bb_*())`; it reads the IR and the plan and decides nothing. Templates `src/templates/bb/`, helpers `xa/`, the one encoder `x86/` (skill `box-templates`).
7. **Runtime** `src/runtime/`: `rt/` (C: call protocol, collector, slabs, co-expressions, the Prolog engine), `rtx/` (hand-written asm leaves on the rtcc ABI), `core/`, `builtins/`; linked as `out/libscrip_rt.so`.

## 2. The two modes (modes 1 and 2 are deleted; each mode is graded against the oracle)

- **Mode 3, `--run` (default):** the emitter writes machine code into a sealed slab (`src/runtime/rt/rt_slab.c`) and jumps in. Sizing switches go before the file.
- **Mode 4, `--compile --out=prog.s`:** the emitter writes x86-64 assembly; the harness links it PIE against `out/libscrip_rt.so`. A bare `-o FILE` is refused.
- Run-time compilation (EVAL, CODE, Prolog `call/N`, asserted clauses) goes through the same pipeline from the runtime: `src/runtime/runtime_eval.c` re-enters the planner and emitter. There is no interpreter.
- `--target=` accepts only `x86`; the other names the usage text lists refuse ("Stack-Machine codegen removed"). Future targets are skill `scrip-backends`.

## 3. The cross-layer rulings (receipts in GOAL-CEO.md under each number)

- **The tree is the pruned parse tree**; only `tree_t` crosses parser to lower; lower builds every runtime table (CEO-1322/1369/1371/1377/1378).
- **No language past the driver** (CEO-1838/1840): after lower every variance is an IR fact, a graph fact from the closed registry, a node kind or attribute, or a runtime entry named on the node. A deletion carries its re-expression.
- **Placement is decided once, in the planner** (CEO-1895).
- **No C function enters a box** (CEO-1576); logic lives in emitted boxes (CEO-2045).
- **Static wiring only, except an if-type construct** (CEO-694): only an if construct's own lowering may select a continuation at run time (`IR_GATE`, `IR_GATE_ARM`, a soft cut); a general op that selects a continuation is refused.
- **A port transfer carries no value**: rax is scratch across every port; only procedure-exit wiring promotes rax:rdx to the returned DESCR, after an explicit tagged write (audit `SCRIP_PORT_EXIT_AUDIT=1`, gate `test_gate_port_exit_value_contract.sh`, not wired in the Makefile).
- **No runtime interpreter**: a goal unknown at compile time is compiled at run time and runs as boxes (the runtime-goal ruling of 2026-09-01).
- **A co-expression is a thread**: its stack is the pthread's own mmap'd stack, never a heap block (the co-expression ruling of 2026-09-02).
- **Order of work** (CEO-1886): completeness, correctness, speed; speed only for SNOBOL4 and Icon, by instruction count (CEO-2035).

## 4. Which skill owns which layer

| you touch or debug | load |
|---|---|
| a parser, a lowerer, a prelude of language L | the language skill: `snobol4` (also Snocone, Rebus), `icon` (also Unicon), `prolog`, `pascal`, `raku` |
| Prolog's compiled machine, its tabling, its constraints | `prolog-engine`, `prolog-tabling`, `prolog-constraints` |
| `src/lower/` | `lowering` |
| `src/planner/`, `src/emitter/`, the zetas | `scrip-memory-model` |
| `src/runtime/rt/gc_*`, frame maps, polls, safe points | `gc-collector` |
| `src/templates/`, `x86_*`, `emit.cpp` | `box-templates` |
| `src/runtime/rtx/` | `rtx-asm-leaves` |
| the call protocol, the builtin table, the error protocol | `runtime-calls` |
| any `.c .h .inc` under `src/` | `scrip-c-code` |
| `bootstrap/*.sc` | `snocone-parser-patterns` |
| the Makefile, headers, the build cache | `scrip-build` |
| a gate, witness, ref, rung, DONE-WHEN | `gates-and-witnesses`; a suite or its grading: `suites-and-grading` |
| a DESIGN-PLAN and its STEPS.tsv | `design-plans` |
| instruction counts, benchmarks | `speed-measurement` |
| the bus, rows, batons, MODE | `fleet-bus`; the shared box (slices, pools, memory): `shared-box` |
| snobol4dotnet, snobol4jvm | `ports` (independent SNOBOL4 implementations, not SCRIP backends) |
| SCRIP's future JVM, .NET, JS, WASM targets | `scrip-backends` |

## 5. Routing a red to its layer

1. `bash ../harness/scripts/monitor_run.sh <prog> --oracle`: the bug lies between the last event both agree on and the first they diverge on.
2. Diverges in one mode only: the emitter or a template (asm-diff the smallest repro beside a passing sibling, `--compile` both). Both modes: lower, the runtime, or the plan.
3. `--dump-ast` wrong: the parser. `--dump-ir` wrong: lower. `--dump-plan` wrong: the planner. `--dump-bb`, `--dump-zeta`, `--dump-homes` for the box graph and placement.
4. A crash under `SCRIP_GC_STRESS=1` only: the collector or a root (skill `gc-collector`).

## 6. Names a reader of old receipts meets that are gone

`IR.h` (now `src/ir/ir_node.h`, `ir_graph.h`, `ir_fwd.h`); `MOD_OP` trace tags (deleted, the tag-ceiling rule is void); `IR_INDIRECT_GOTO` and `IR_MOVE_LABEL` (now `IR_GATE`, `IR_GATE_ARM`); `bb_broker`, `emit_core.c`, `SM_templates/`, `BB_templates/`, `emit_jvm.c`, `emit_js.c`, `emit_wasm.c`; `STMT_t.lang`, `LANG_*`, `g_lang`; modes 1 and 2. The full table is `reference.md` § 4. A retired ARCH page is read with the command in `/home/.github/RETIRED-ARCH-PAGES.tsv`.

## 7. DESIGN: THE DOCUMENT ROAD (the cao, 2026-11-16; Lon that day, in the coo's window: "getting SCRIPtix files, *.md, and IPYNB equivalent JSON files to run top down and accumulate the mode 3 code compiles and to share the global variables where each cell can add or reference globals from previous cells."; the cao is the one boss of Jupyter and SCRIPtix; the cto's design of 2026-11-11, CTO-586 and CTO-600, stands and is the base)

- **TWO ROADS, ONE SHARED PIECE.** A FILE (`.md`, `.scrip`) is compiled whole into one image and then its sections' mains run in document order: a forward call to a later section is the law of a file (MEASURED: `corpus/demos/scriptix/infinite_snobol4/infinite_snobol4.md`'s first section calls a procedure its second defines). A KERNEL cell cannot see a later cell, so the kernel needs a new section compiled into the running image when it arrives. Both rest on one piece: A SECTION'S MAIN RETURNS TO WHAT ENTERED IT instead of exiting.
- **WHERE A MAIN ENDS** (read 2026-11-16). An Icon cells main ends through the wire pair on the stack and a zframe main (Prolog root, Raku) through rcx and rdx, both passed by the driver; a SNOBOL4, Snocone, Rebus or Pascal main ended in a baked call of exit (`bb_glue_outer`, `bb_glue_flat.cpp`), with the driver's wire pair lying exactly at rsp there.
- **WHAT STANDS ON ORIGIN** (mode 3; SCRIP `abc28f8b9`, `d87286b06`, `1d097f5f1`, `bc81a1bee`, `72b592ba7`, all 2026-11-16). For a document whose modules hold two or more mains and no Pascal main: the driver emits every module's main in document order (clearing the emitter's per-graph frame state between two mains, `emit_jmp_entry_clear`) and enters each through one returning trampoline, `rt_doc_call` (`src/driver/scrip.c`), which saves the callee-saved registers, adopts the program top for that main and returns 0 or 1. Its four entry kinds: an outer main (SNOBOL4, Snocone, Rebus), whose graph fact `section_main` (`ir_graph.h`) gives it the end `bb_glue_section`, `rt_section_end` then a jump through the wire at rsp; an Icon cells main, which already ends through the wire pair on the stack; a zframe main (Raku), wires in rcx and rdx, rsp at its entry value at either wire; a Prolog root, the same with a pending ball reported and the run ended 2, and otherwise its trail unregistered from the root ranges (`doc_pl_end`). A document with one main, and every program that is not a document, takes the old path and emits the same instructions as before. A NOTEBOOK IS A DOCUMENT: `scrip NAME.ipynb` reads the cells with the kernel's JSON reader (`scrip_notebook_document`, `kernel.c`) into one fenced section a code cell, the cell's language by `k_cell_lang`'s rule (`metadata.scrip.language`, a `%%tag` first line, the default); it is run from the notebook's own folder, as Jupyter runs it.
- **THE FACTS THE BUILD PAID FOR.** (1) THE WIRE IS AT RSP ONLY AT FUNCTION LEVEL ZERO: an END reached inside a function call ends the run, as in a program (`rt_section_end` tests `&FNCLEVEL`). (2) THE PROGRAM TOP IS PER SECTION: `rt_program_top_adopt` adopts once and reads the last root map, so the driver resets the top before each section and the trampoline adopts entry rsp plus that main's own delta (`rt_gc_root_top_delta`). (3) A MAIN IS PER SECTION IN EVERY LOWERER: Icon treats the name `main` as a duplicate only inside its own module and a later Icon section inherits the nearest earlier one's global declarations (`lower_icon_inherit_globals`); Raku makes and counts its main inside its own module; `planner_tiers` gives every module's main the main's rule. (4) A NAME A LOWERER GENERATES IS UNIQUE IN THE DOCUMENT, NOT IN THE MODULE: the SNOBOL4 lowerer numbered its pattern and expression thunks from zero in every module (`PAT$0`, `EXPR$0`), so an earlier section matched with a later section's pattern and its conditional assignments went to the later section's variables; a module that is not the document's first takes the next salt (`sno_expr_salt_next`), the one a run-time CODE fragment takes. (5) A STRUCT BLOCK IS BORN ZERO: `rt_pl_struct_alloc` returned recycled ground as it was and `pl_db_registry` sets only some of its fields, so a Prolog root that starts after any collection crashed; found because a Prolog section may now start late. (6) A PASCAL MAIN'S FRAME IS STILL ON THE STACK AT ITS END, so the wire is not at rsp there: a document holding a Pascal main (`caller_frame`) is not run section by section yet and runs its first main.
- **THE RULES OF A DOCUMENT** (the cao's, before Lon through the coo): an error in a section ends the document there; an Icon main that falls off its end, and a Prolog root goal that fails, are normal ends; an undeclared name in an Icon section stays local as Icon rules (MEASURED: of five names a SNOBOL4 section set, an Icon section reads &null for all but one that is also an Icon built-in function), so a SNOBOL4 variable is read from Icon by declaring it global; each Prolog section that is not adjacent to another opens its own world, its dynamic database empty, while a predicate an earlier Prolog section's text defined is code and is called.
- **NOT BUILT, in the order intended** (the plan and its measurements are the baton of row jupyter-step-10): the kernel road (one runtime entry compiles a unit of a language into the running image; `kernel_session_snobol4.sno` names it `SCRIP.UNIT` and nothing defines it; the probe's session arm reads 1 of 8); ONE NAME DEFINED BY TWO SECTIONS (the Icon lowerer drops the later procedure in silence, so demos/scriptix/demo10's Icon section calls its SNOBOL4 section's function; the rule intended: a section's own definitions are bound when the section starts, on both roads); a later Raku section reading an earlier one's variable (refused today: Variable not declared); a Pascal main in the loop (its frame popped before the wire); the Prolog world opened once (CTO-586; acceptance `cross_lang.md`); a section that fails to parse is skipped today and the rest of the document runs; mode 4 of a document with several mains (mode 4's start has the same one-main assumption).
- **A DEMO'S REF IS A WHOLE ORACLE CUT OF THE DOCUMENT AS IT STANDS**: each section through its own oracle (`sbl -bf`, `icont` with `iconx`, `swipl`), in document order, twice alike (`/tmp` holds no copy: the cutter is a few lines, written again when needed). A section the oracle refuses is cured in the document, never left out of the cut (the grader's hold of 2026-11-16: five demos set `&CASE = 1` and then DEFINEd lower-case functions, which `sbl -bf` refuses with ERROR 022 at the first call; the line was removed from the documents).
- **THE WITNESS** is `/home/resources/evidence/cao/scriptix`: `run.sh` runs every document and notebook that has a ref beside it under four collector settings, two of them `SCRIP_DIAG=0`; `check_notebooks.py` runs a folder's notebooks as files against the outputs saved in their cells (corpus/notebooks: 5 of 5, 1,108 lines); `check_demo_refs.sh` grades the ten demos. A step adds its documents there and names the folder as its landing's gate.

## THE TWO MODES AND THE EXTENSIONS (moved from CLAUDE.md 2026-11-05)

Mode 3 (`./scrip prog.<ext> < /dev/null`, the default `--run`) builds the x86-64 blobs in a sealed slab and jumps in, in-process; mode 4 (`./scrip --compile --out=prog.s prog.<ext> && gcc prog.s -L$PWD/out -lscrip_rt -lm -Wl,-rpath,$PWD/out -o prog`) assembles the same emitted text against `out/libscrip_rt.so`; the two must agree on every program, and a program is graded in both (`--modes m3,m4`). Switches `-d<kb>k -s<kb>k` (the declared heap cap and stack) go before the file, the program's own arguments after `--`; `--dump-ast --dump-ir --dump-bb --dump-zeta --dump-plan` show each stage. The driver picks the language by extension: `.sno .spt .sbl` SNOBOL4, `.sc` Snocone, `.reb` Rebus, `.icn` Icon and Unicon (`--dialect=unicon` or the program's own markers), `.pl .pro .prolog .plt` Prolog, `.pas .dpr` Pascal, `.raku` Raku, `.md .scrip` polyglot; no language flag passes the driver.
