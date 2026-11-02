# Building SCRIP: the reference

Verified 2026-11-01 against `SCRIP/Makefile`, `out/` and the harness. Consolidated from ARCH-HEADER-SPLIT, ARCH-BUILD-SYSTEM-DRAFT (2026-08-23) and ARCH-SRC-LAYOUT-DRAFT-hq_C (s269), retired (`.github/RETIRED-ARCH-PAGES.tsv`). The two drafts are history: the source reorganisation they argued landed (`src/{driver,parsers,ir,lower,optimizer,planner,emitter,templates,runtime,tools}`), and their measurements predate it.

## 1. The Makefile's targets

`all build-all pristine pristine-all buildinfo libscrip_rt libscrip_rt_static scrip parsers parsers-sc scrip-monitor monitor-ipc hooks setup run test test-sequential test-arena test-boards test-postoffice preflight fleet-smoke clean distclean` (and `run-jvm`, `run-net`, relics of the deleted non-x86 targets). `make -n` relinking the runtime builds the stage-0 runtime first. A Makefile edit after a verdict build stales every gate started after it.

## 2. The header-split plan (DESIGN-PLAN header-split, CEO-2032; every step DONE by 2026-10-31)

1a the fan-in instrument and the stripped-object identity script; 1b the small split (`core.h` stops including `g_runtime.h` and `descr.h`); 2 `x86_asm.h` became `x86_asm.cpp` compiled once behind `x86_ops.h` and the family pairs; 2b the four over-ceiling family headers cut; 3 `emit.h` un-concatenated into `emit_state.h`, `bb_label.h`, `emit_medium.h` and the rest; 4 `IR.h` split into `ir_node.h`, `ir_graph.h`, `ir_construct.h`, `ir_fwd.h`; 5 the runtime's families cut out of `core.h`, `rt.h`, `gc_heap.h`; 6 the layers' interface headers, data headers renamed `.inc`, every include by its path from `src/`, the `-I` list cut to `-I src`; 7 the gate blocking. The base set (read by neither rule) includes `ir/ir_fwd.h`; the base set does not grow and the ceiling is not raised without a ruling. Forbidden: a move that also changes text; a new umbrella; a large step outside a quiet window or without a last-minute rebase.

## 3. Facts for a header landing

- A data `.inc` (an initializer, a table, an embedded source) is spliced text, not declarations a unit names; the unused-include arm leaves it alone.
- A header-split fixer adds includes to units only; a C-linkage conflict names an unwrapped C header or a tail outside its guard; `bb_templates.h` prototypes are C++ linkage, so a definition must not add `extern "C"`.
- A passenger split exposes carried declarations: run the implicit-declaration pass over the rewritten units (`-Werror=implicit-function-declaration`), since the build's `-w` hides an unprototyped call (the five-units row, `scrip-five-units-call-a-function-no-included-header-declares-...`, FREE).
- A header move has readers in the harness: grep it for the old file name before landing.
