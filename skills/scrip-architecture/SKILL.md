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
- **WHAT STANDS ON ORIGIN** (mode 3; SCRIP `abc28f8b9` and `d87286b06`). For a document whose modules hold two or more mains, none of them a zframe main: the driver emits every module's main in document order and enters each through one returning trampoline, `rt_doc_call` (`src/driver/scrip.c`), which saves the callee-saved registers, pushes its own two labels as the wire pair and returns 0 or 1. The graph fact `section_main` (`ir_graph.h`) gives a SNOBOL4 family main the end `bb_glue_section`: `rt_section_end`, then a jump through the wire at rsp. A document with one main, and every program that is not a document, takes the old path and emits the same instructions as before.
- **THREE FACTS THE BUILD PAID FOR.** (1) THE WIRE IS AT RSP ONLY AT FUNCTION LEVEL ZERO: an END reached inside a function call ends the run, as in a program (`rt_section_end` tests `&FNCLEVEL`; without it the document crashed in the slab). (2) THE PROGRAM TOP IS PER SECTION: `rt_program_top_adopt` adopts once and reads the last root map, so a second section with another root frame shape was refused by the chain check under stress; the driver resets the top before each section and the trampoline adopts entry rsp plus that main's own delta (`rt_gc_root_top_delta`, read right after the main's emission). (3) AN ICON MAIN IS PER SECTION: the Icon lowerer treats the name `main` as a duplicate only inside its own module, and a later Icon section that is not adjacent inherits the global declarations of the nearest earlier one (`lower_icon_inherit_globals`); adjacent Icon sections, and adjacent Prolog sections, are merged into one module by the driver and share one main.
- **THE RULES OF A DOCUMENT** (the cao's, for Lon to overrule): an error in a section ends the document there; an Icon main that falls off its end is a normal end; an undeclared name in an Icon section stays local as Icon rules, so a SNOBOL4 variable is read from Icon by declaring it global.
- **THE STEPS LEFT**, in order (the plan and its measurements are the baton of row jupyter-step-10): C the zframe mains (`planner_tiers` makes the document's main alone a main; Raku lowers a section's top-level code only when no main exists yet; Pascal renames a second main; a Prolog section that is not first is its own root with its own world until G); D the demo refs re-cut (the ten demos print one section of three today, and ScripDemo's green was earned that way); E the notebook as a file (`scrip file.ipynb` is refused today, unknown source extension); F the kernel road (one runtime entry compiles a unit of a language into the running image; `kernel_session_snobol4.sno` names it `SCRIP.UNIT` and nothing defines it; the probe's session arm reads 1 of 8); G the Prolog world opened once (CTO-586; acceptance `cross_lang.md`). Mode 4 of a document with several mains is not in the plan yet: mode 4's start has the same one-main assumption.
- **THE WITNESS** is `/home/resources/evidence/cao/scriptix` (`run.sh` beside the documents and their refs: every document under four collector settings, two of them `SCRIP_DIAG=0`); a step adds its documents there and names the folder as its landing's gate.

## THE TWO MODES AND THE EXTENSIONS (moved from CLAUDE.md 2026-11-05)

Mode 3 (`./scrip prog.<ext> < /dev/null`, the default `--run`) builds the x86-64 blobs in a sealed slab and jumps in, in-process; mode 4 (`./scrip --compile --out=prog.s prog.<ext> && gcc prog.s -L$PWD/out -lscrip_rt -lm -Wl,-rpath,$PWD/out -o prog`) assembles the same emitted text against `out/libscrip_rt.so`; the two must agree on every program, and a program is graded in both (`--modes m3,m4`). Switches `-d<kb>k -s<kb>k` (the declared heap cap and stack) go before the file, the program's own arguments after `--`; `--dump-ast --dump-ir --dump-bb --dump-zeta --dump-plan` show each stage. The driver picks the language by extension: `.sno .spt .sbl` SNOBOL4, `.sc` Snocone, `.reb` Rebus, `.icn` Icon and Unicon (`--dialect=unicon` or the program's own markers), `.pl .pro .prolog .plt` Prolog, `.pas .dpr` Pascal, `.raku` Raku, `.md .scrip` polyglot; no language flag passes the driver.
