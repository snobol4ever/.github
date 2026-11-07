---
name: scrip-architecture
description: The map of SCRIP: the one pipeline (driver, parser, lower, optimizer, planner, emitter, runtime), modes 3 and 4, the IR types, the cross-layer rulings, which skill owns which layer. Load first when a task crosses layers or routes a red.
---

# SCRIP's architecture

One `scrip` binary compiles SNOBOL4, Snocone, Rebus, Icon (and its Unicon superset), Prolog, Raku and Pascal to x86-64. Every pattern, generator and goal is a four-port Byrd box (α proceed, β recede, γ succeed, ω concede) wired at compile time into straight-line jumps: SNOBOL4 patterns, Icon generators and Prolog backtracking are three syntaxes over one machine. The law is `.github/RULES.md`; this skill is the map. Detail and the retired-name table are in `reference.md` beside this file.

## 1. The pipeline (each stage hands the next exactly one thing)

1. **Driver** `src/driver/scrip.c`: the extension picks the frontend from `scrip_exts[]` (an unknown extension refuses, it never guesses). `.scrip` and `.md` are polyglot: fenced blocks tagged SNOBOL4, Icon, Prolog, Raku, Rebus (`src/driver/polyglot.c`). Since CTO-511 (Lon 2026-11-04) every fenced section runs in document order like Jupyter's Run All, sharing the registry, the globals and the heap; the Jupyter notebook is a second reader of the same runner (cells are sections, `metadata.scrip.language` is the fence name) and the two must print the same.
2. **Parser** `src/parsers/<lang>/`: C front ends (bison and flex for SNOBOL4, Rebus, Pascal, Snocone; hand-written for Icon, Prolog, Raku). Output: the pruned parse tree `tree_t` (`src/ir/ast.h`). Only `tree_t` crosses to lower (CEO-1322/1369/1371/1377/1378). The seven Snocone parsers in `SCRIP/bootstrap/parser_<lang>.sc` are the bootstrap: built as `out/parser_<lang>` by `make parsers-sc`, graded tree for tree against the C parsers (skill `snocone-parser-patterns`).
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

`IR.h` (now `src/ir/ir_node.h`, `ir_graph.h`, `ir_fwd.h`); `MOD_OP` trace tags (deleted, the tag-ceiling rule is void); `IR_INDIRECT_GOTO` and `IR_MOVE_LABEL` (now `IR_GATE`, `IR_GATE_ARM`); `bb_broker`, `emit_core.c`, `SM_templates/`, `BB_templates/`, `emit_jvm.c`, `emit_js.c`, `emit_wasm.c`; `STMT_t.lang`, `LANG_*`, `g_lang`; modes 1 and 2. The full table is `reference.md` § 4. A retired ARCH page is read with the command in `.github/RETIRED-ARCH-PAGES.tsv`.

## THE TWO MODES AND THE EXTENSIONS (moved from CLAUDE.md 2026-11-05)

Mode 3 (`./scrip prog.<ext> < /dev/null`, the default `--run`) builds the x86-64 blobs in a sealed slab and jumps in, in-process; mode 4 (`./scrip --compile --out=prog.s prog.<ext> && gcc prog.s -L$PWD/out -lscrip_rt -lm -Wl,-rpath,$PWD/out -o prog`) assembles the same emitted text against `out/libscrip_rt.so`; the two must agree on every program, and a program is graded in both (`--modes m3,m4`). Switches `-d<kb>k -s<kb>k` (the declared heap cap and stack) go before the file, the program's own arguments after `--`; `--dump-ast --dump-ir --dump-bb --dump-zeta --dump-plan` show each stage. The driver picks the language by extension: `.sno .spt .sbl` SNOBOL4, `.sc` Snocone, `.reb` Rebus, `.icn` Icon and Unicon (`--dialect=unicon` or the program's own markers), `.pl .pro .prolog .plt` Prolog, `.pas .dpr` Pascal, `.raku` Raku, `.md .scrip` polyglot; no language flag passes the driver.
