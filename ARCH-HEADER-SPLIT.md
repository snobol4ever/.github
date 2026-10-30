# ARCH-HEADER-SPLIT.md — ONE HEADER PER STRUCTURE AND ITS DEFINITIONS, NO UMBRELLA HEADERS, AND A ONE-HEADER EDIT RECOMPILES ONLY THE UNITS THAT USE THAT STRUCTURE (the cto; DESIGN-PLAN written 2026-10-30 11:4x-12:3x CDT on Lon's word, in-chat to the ceo, verbatim: *"how about re-design our header files and split them out properly focusing on individual structures and their related definitions."* · *"I want the header files designed properly NOT to cause total re-builds."*; CEO-2032; the frozen snapshot of 171 headers and .inc files at origin 2ecf50e7f)

DESIGN-PLAN: header-split

## 0. The measurement (the ceo's inventory at 2ecf50e7f over 1,122 build units per root; the cto's census of this root's 296 source units and 285 dependency files, 2026-10-30 11:4x)

| what | reading |
|---|---|
| headers and .inc in the snapshot | 171 (156 headers, 15 .inc) under src/, in 12 directories |
| translation units | 296 under src/ (templates 144, runtime 60, parsers 30, lower 14, driver 13, optimizer 11, planner 10, ir 6, tools 5, emitter 3), built 3 to 4 ways each (the compiler, the runtime PIC, stage 0, the parser modules) into the 1,122 of the ceo's count |
| a unit's dependency list | median 46 headers per unit (from the .d files) |
| the widest headers (units reaching them, ceo / this root) | ct_arena.h 476 / 261; g_runtime.h 405 / 215 and each of its nineteen parts 215; descr.h 377 / 224; core.h 217 / 203; IR.h 206 / 209; bb_box.h 192; SM.h 191; bb_program.h 187; stage2.h 186; rt_slab.h 185; rt_arena.h 183; call_forms.h 168; bb_pool.h 164; emit.h 156 / 159; XA.h, stno_map.h 159; rt_pl_trail.h 151; pin_va.h 150; rtcc.h 148; x86_arg_roles.h 146; x86_asm.h 144 / 145 |
| the units that actually NAME each structure | DESCR_t 109; g_runtime 57 (g_runtime.abi 35, .misc 16, .eval 9, .atoms 4, every other part 3 or fewer); tree_t 51; IR_t 49; IR_graph_t 37; g_emit 23 of the non-template units and 122 of the 143 templates (`_.`); ARBLK_t 11; VCELL_t 10; TBBLK_t, DATBLK_t, DATINST_t, zeta_plan_t 8; g_planner 7; bb_label_t 5; NV_t, FNCBLK_t, x86_rsp_st_t, gc_site_t 1 |
| x86_asm.h | 3,310 lines, 256 KB, 466 inline functions in 40 families (31 rsp, 19 frame, 18 reg, 18 jmp, 16 rtcc, 15 gc polls, 12 zdp, 11 jcc, 10 fc, 9 pl, 9 align, 8 zref, 8 zop ...), 35 const_ tables, the tracker x86_rsp_st_t (lines 199-262), 40-odd extern "C" runtime prototypes; the 143 templates name 116 distinct helpers of the 466, a median of 6 each; at -O0 nothing is inlined, so each of the 145 units carries its own compiled copy of the encoder |
| emit.h | 870 lines, 28 structs, 169 prototypes, eight former headers pasted end to end (include blocks at lines 9, 80, 106, 179, 215, 248, 276, 728, 742, 795, 815, 828); 143 of its 159 units are templates that read three things from it: the g_emit struct, bb_label_t and the medium enums |
| core.h | 382 lines, 12 structs, 266 prototypes of a dozen families; it includes g_runtime.h, which is how the nineteen runtime parts reach 215 units that never name them |
| IR.h | 370 lines, 13 structs, 28 inline bodies; directly included by 15 units, reached by 209 through emit.h and x86_asm.h |
| g_runtime.h | 51 lines: eighteen includes and one struct of nineteen parts BY VALUE (the asm reads fixed offsets from g_runtime) |
| include paths | -I src -I src/ir -I src/lower -I src/emitter -I src/runtime/core -I src/runtime (+ templates and parsers for the runtime): any header is includable by bare name from anywhere, so a header's directory says nothing about who may reach it |
| dead headers (no includer at the census) | g_runtime_entry.h (0 lines), gc_slot_table.h (0 lines), sync_monitor.h, cset_block.h, box_rt.h, bb_common.h, pl_cell.h, unicode_alpha_ranges.h, emit_per_kind_audit.h |
| data wearing a .h | rk_core_names.h 51,439 lines (2.3 MB), rk_case_table.h 700 lines |

**Read honestly:** the recompiles today are not caused by big headers but by UMBRELLAS: core.h carries g_runtime.h into 215 units of which 57 use it; emit.h carries IR.h, rt_arena.h, bb_box.h, call_forms.h, bb_pool.h, stno_map.h and XA.h into 159 units of which the templates need three small things; x86_asm.h carries rtcc.h, pin_va.h, rt_pl_trail.h, stage2.h and x86_arg_roles.h into 145. A one-line edit to g_runtime_gc.h (3 users) recompiles 405 of 1,122 units. The cure is not to shrink the big headers first; it is to cut the umbrellas and make every unit include what it uses.

## 1. THE RULE (written so a gate can check it)

**R1, ONE HEADER, ONE STRUCTURE.** A header is one of exactly two kinds. A TYPE HEADER declares ONE structure (or one closely bound family: a struct with its entry and bucket records, an enum with its name table) together with its fields, enums, constants, macros, one-line accessors and the prototypes of the functions that take or return that type. An INTERFACE HEADER `foo.h` declares the functions that `foo.c` (or `foo.cpp`) defines and nothing else. There is no third kind: no header that only includes other headers (an umbrella), no header that collects the prototypes of several files (a grab-bag), no header that holds data tables (data is a `.inc` included by one unit).

**R2, INCLUDE WHAT YOU USE, AND ONLY THAT.** A unit includes DIRECTLY every header whose declarations it names, and no header whose declarations it does not name. A header includes only what its own declarations need to compile; a pointer or reference to a struct needs a forward declaration (`struct IR_graph_t;`), not the struct's header. Includes are written by their path from `src/` (`#include "ir/ir_node.h"`), and the one `-I src` is the include path, so a header's directory is its layer.

**R3, NO INLINE BODIES BUT ONE-LINERS.** A function body in a header is at most one expression (an accessor, a predicate, a tag test) over the header's own type, or an `always_inline` the hot path has been measured to need (descr.h's predicates, the asm leaves' twins). Every other body is compiled once in a `.c`/`.cpp`. At -O0 (the fleet's build) an inline body is not inlined anyway: it is a static copy per unit, which costs compile time and buys nothing.

**R4, THE FAN-IN CEILING.** For every header H, fan-in(H) is the number of units whose dependency file names H (directly or through another header). users(H) is the number of units that name an identifier H declares. The rule: fan-in(H) ≤ users(H) + 4 for every header; and fan-in(H) ≤ one third of the units (99 of 296; 374 of 1,122) for every header that is not in the BASE SET. THE BASE SET, each wide for a stated reason and for no other: `ir/descr_tags.h` (the value tags every language, template and asm leaf names), `ir/descr.h` (the value cell DESCR_t, the one value type of every language), `ir/ct_arena.h` and `ir/ct_vec.h` (the compile-time allocator and vector of every compile-time object: parsers, lower, optimizer, planner, emitter, driver), `ir/ast.h` (the pruned parse tree, every parser's and lowerer's), `runtime/core/name_t.h` (the name cell), `runtime/rt/rt_diag.h` (the six-line diagnostic switch), `templates/bb/bb_template_common.h`, `emitter/emit_state.h`, `emitter/bb_label.h` and `templates/x86/x86_ops.h` (what every template reads: the emitter state, the labels and the encoder's API; their fan-in is the template count by construction). Nothing is added to the base set without a ruling on this page.

**R5, THE PROOF.** A header move changes no object: every object file under the objdir and `out/` (the compiler's, the runtime's PIC and static objects, the stage-0 objects, the parser modules) is byte-identical after `objcopy --strip-debug` against the parent's, both roots built from the same `make` targets; a mismatch names the object and the landing does not push. Then the eight smokes. No identity run is needed: identical objects cannot emit different asm.

## 2. THE INSTRUMENTS AND THE GATE (hq_templates builds them first, step 1a)

- **`harness/scripts/util_header_fanin.py`** reads every `.d` file under `$OBJ` and `out/` and prints, per header: `fanin` (units reaching it), `direct` (units including it by name), `users` (units naming any identifier the header declares: typedef names, struct tags, enum members, macros, prototypes, read by a one-pass scan of the header), `includes` (its own include count), `inline_bodies` (bodies longer than one line), `lines`; `--recompiles H` prints the units a one-line edit to H recompiles (its fan-in list); `--base` reads the base set from this page's R4 list kept as `harness/scripts/header_base_set.tsv`; `--ceiling` prints every header over the ceiling and every umbrella (two or more includes and no declaration of its own); `--unused` prints, per unit, the direct includes none of whose declarations the unit names (R2's second half). It runs no build: it needs a built tree's `.d` files and refuses rc 2 without them.
- **`harness/scripts/util_objects_identical_stripped.sh <objdirA> <objdirB> [outA outB]`**: for every `.o` present in both, `objcopy --strip-debug` into a scratch dir and `cmp`; prints `objects=N identical=N differing=M` and names the differing objects; rc 1 on any difference or on an object present in one tree only. Lon's "no total rebuilds" is the thing R5 proves: the build differs in nothing but which units it recompiles.
- **`harness/scripts/test_gate_no_header_reaches_more_units_than_its_users.sh`**: arm 1 every non-base header's fan-in ≤ users + 4 and ≤ the ceiling; arm 2 no umbrella (a header with ≥ 2 includes and 0 declarations) exists; arm 3 no inline body longer than one line in a header outside the base set and the always_inline list (`harness/scripts/header_inline_allowed.tsv`); arm 4 every include names its path from src/ (no bare-name include of another directory's header); arm 5 no unit has an unused direct include (R2). Declared RULING (reporting) at step 1a, BLOCKING at step 7 when every arm reads 0. The baseline the gate ratchets from is written by `util_header_fanin.py --write-baseline` at step 1a and never raised.

## 3. THE HOT SPOTS FIRST: WHAT MOVES WHERE

**3.1 x86_asm.h (3,310 lines, 145 units).** The encoder CORE becomes compiled code: `x86_asm.cpp` holds `xop`, `x86()`, `x86_core_`, `x86_core_inner_`, the text and binary media, the record encoder (`x86_rec_*`) and the internal-label bookkeeping, compiled ONCE; `x86_ops.h` is its interface: the 116 helpers the templates name as prototypes, and the one-line port helpers (`x86_alpha`, `x86_beta`, `x86_gamma`, `x86_omega`, `x86_bomb`, `x86_begin`) kept inline. The families become type-or-interface pairs: `x86_rtcc.h/.cpp` (the 16 write-back, reload and call helpers; it includes `rtx/rtcc.h`), `x86_frame.h/.cpp` (frame, align, rsp store and load, the hb helpers), `x86_jump.h/.cpp` (jmp, jcc, deflabel, the internal labels and `X86_INTERNAL_MAX`), `x86_zeta.h/.cpp` (zop, zref, ztos, zdp, zsm: the cell forms and the verifier emitters), `x86_gc.h/.cpp` (the gate, the fifteen poll forms and the site helpers, the family zeta-layout step 6 then reduces to `x86_gc_poll()`), `x86_call.h/.cpp` (fc, pl, port and the call forms), `x86_icn.h/.cpp` (the Icon scanning helpers), `x86_consts.cpp` (the 35 const_ tables), and `x86_rsp_tracker.h/.cpp` (x86_rsp_st_t: a file of its own so that zeta-layout step 3 deletes a file, not a span). The 40-odd `extern "C"` runtime prototypes it declares (`rt_gc_poll`, `rt_gc_point_arr_c`, `rt_pl_cap_raise`, `rt_icn_*`, `zls_*`, `emit_*`, `gva_*`) go to their owners' interface headers and the encoder files include those. WHY IT RECOMPILES ONCE: an encoder edit touches `x86_asm.cpp`; a family edit touches that family's `.cpp`; a template includes `x86_ops.h` and the family headers it names (median 6 helpers; `--unused` keeps it to that). A `.cpp` edit recompiles one unit; a header edit recompiles its users.

**3.2 emit.h (870 lines, 159 units).** `emit_state.h` holds the `g_emit` struct and the `_` macro and NOTHING else (122 templates read `_.`; when a column is added they recompile, which is exactly the set that reads it). `bb_label.h` holds `bb_label_t`, `bb_patch_t`, `jmp_kind_t`, `bb_patch_kind_t` and the label and patch prototypes. `emit_medium.h` holds the medium enums and the `emitter_text_*`, `emitter_pos_*`, `emitter_end_*` prototypes. `emit_sm.h` holds the 46 `emit_sm_*` prototypes of the state machine. The per-construct walker states (`stmt_t`, `prog_t`, `bb_conj_state_t`, `bb_catch_state_t`, `bb_match_kids_state_t`) go to `bb_walk_states.h` beside emit.cpp; the Prolog call states (`pl_gz_callee_t`, `pl_gz_call_state_t`, `pl_ix_arm_t` and their vectors) to `bb_pl_call_state.h` beside the templates that read them; `emit_data_*` and `data_buf_*` to `emit_data.h`; the knobs to `emit_knobs.h`. `emit.h` then declares emit.cpp's own functions and includes nothing but forward declarations. `bb_template_common.h` is re-cut to include `emit_state.h`, `bb_label.h`, `x86_ops.h` and `ir/ir_node.h` and nothing else; `XA.h` merges into `x86_ops.h`; `emit_ir.h` into `ir_node.h`; `emit_head.h` into `g_emitter.h`.

**3.3 IR.h (370 lines, 209 units) and the ir/ umbrellas.** `ir_ops.h` (the op enum and its names), `ir_node.h` (`IR_t`, `IR_ref_t`, `IR_lit_t`, the one-line `ir_is_*` predicates; the longer inline bodies to `ir_node.c`), `ir_graph.h` (`IR_graph_t`, `IR_vslot_t`), `ir_plan_facts.h` (`IR_plan_facts_t`, the CLOSED REGISTRY `pf` of CEO-1838, so that a new graph fact recompiles the planner, the emitter and the dump and not the parsers), `ir_construct.h` (`IR_construct_t`). `bb_box.h` keeps the box kinds; its 14 port records go to `bb_ports.h`. `stage2.h` keeps the driver's stage record; the per-language stage structs go beside their lowerers. `bb_program.h`, `bb_build.h` merge into their one includer's header; `SM.h`, `stno_map.h`, `bb_pool.h`, `call_forms.h`, `pin_va.h`, `gc_frame_map.h`, `dtp.h` are already one family each and are included directly by their users instead of through emit.h and x86_asm.h. After: `ir_node.h` about 50 units, `ir_graph.h` about 40, `ir_plan_facts.h` about 15.

**3.4 g_runtime.h (51 lines, 405 units) and core.h (382 lines, 217 units).** `core.h` STOPS INCLUDING `g_runtime.h` AND `descr.h`: that one edit takes the nineteen runtime parts from 215 units to the 57 that name `g_runtime`, with no other change. `core.h` splits by family: `table.h` (TBBLK_t, TBBUCK_t, TBPAIR_t, VCELL_t from descr.h, the `table_*` and `tbl_key_*` prototypes; ARCH-GC 13.14's rows read it), `array.h` (ARBLK_t, `array_*`), `datatype.h` (DATBLK_t, DATINST_t, DEFINE and DATA), `tree_blk.h` (TREEBLK_t), `nv.h` (the NV cells and macros), `trace.h` (trace_ent_t, the 26 `rt_trace_*`), `icn_builtins.h` (icn_bi_rec, the 17 `core_icn_*`), `setexit.h`, `core_error.h` (the error voice), `pat_assign.h`, `comm_var.h`; `core.h` keeps core.c's own prototypes. THE ONE STRUCTURE OF NINETEEN PARTS stays as it is under this plan (OPTION A: no new global): `g_runtime_t` holds its parts BY VALUE because the asm reads fixed offsets from `g_runtime`, so a unit that reads `g_runtime.gc.x` needs the whole layout and includes `g_runtime.h` with its nineteen part headers; an edit to any part recompiles the 57 users. OPTION B, ASKED OF LON WITH THIS DESIGN (NO NEW GLOBAL WITHOUT LON'S IN-CHAT GRANT): the nineteen parts become nineteen named globals of their part types (`g_runtime_abi`, `g_runtime_gc`, ...), the asm offsets per part, the collector's root visitor unchanged in substance; then a unit includes only the part it reads and an edit to `g_runtime_gc.h` recompiles its 3 users. The plan lands option A; option B is one landing on top of it if Lon grants it.

**3.5 descr.h (151 lines, 377 units).** `descr_tags.h` (the DT_ enum, the three bits, the stride: what templates and asm leaves name) and `descr.h` (DESCR_t with its two always_inline source-node accessors and the one-line `IS_*_fn` predicates); VCELL_t goes to `table.h`. Both are BASE and stay wide for the stated reason; what changes is that `runtime/core/descr.h` (a two-line forwarder) is deleted and every includer names `ir/descr.h` or `ir/descr_tags.h` by path.

**3.6 The rest of the wide set.** `rt_pl_trail.h` (151 units): the 26 inline bodies go to `rt_pl_trail.c`, the two layout macros the templates read become `pl_trail_layout.h`, and the header reaches its real users. `rtcc.h` (148): included by `x86_rtcc.h` and the runtime files that read slots. `rt_arena.h`, `rt_slab.h` (183, 185): included by their users, not through emit.h. `planner_head.h` (an umbrella of twelve includes) is deleted; `planner.h`'s eight structs become `zeta_plan.h` (the plan record the emitter reads as struct fields, R2 of ARCH-ZETA-LAYOUT) and `act_words.h`; `rt.h` (206 prototypes of many files) and `driver_private.h` (65) and `lower.h` (42) split into per-file interface headers. The 15 `.inc` stay `.inc`, each with one includer; `rk_core_names.h` and `rk_case_table.h` are renamed `.inc` (data); the nine dead headers are deleted after the gate's own grep proves no includer.

**3.7 Measured before, projected after (units of 1,122; this root's 296 in brackets).** ct_arena.h 476 → about 300 [80] (the compile-time units that allocate); g_runtime.h 405 → 215 [57] under option A, each part 405 → 215 [57] (option B: 3 to 35 per part); descr.h 377 → 377 (base, declared; descr_tags.h the wider of the two); core.h 217 → about 150 [40] (the runtime units that call core.c); IR.h 206 → ir_node.h about 190 [50], ir_graph.h about 150 [40], ir_plan_facts.h about 60 [15]; emit.h 156 → 12 [3] (emit.cpp and the two emitter units), emit_state.h 159 [125] (the template count, declared base); x86_asm.h 144 → x86_ops.h 150 [145] (declared base) and each family header 40 to 120 by its users, x86_asm.cpp 1; rt_pl_trail.h 151 → about 20; rtcc.h 148 → about 15; stage2.h 186 → about 25; bb_box.h 192 → about 30. The ceiling of one third (374 / 99) is then met by every non-base header with room.

## 4. THE DESTINATION OF EVERY HEADER AND .inc IN THE SNAPSHOT (171)

| header | lines | fan-in (this root) | destination | why |
|---|---|---|---|---|
| `src/driver/driver.h` | 30 | 9 | KEEP (the driver's interface) |  |
| `src/driver/driver_private.h` | 195 | 7 | SPLIT: driver_private.h keeps the driver's own records; its 65 prototypes go to the defining files (parse_stage.h, polyglot.h, planner_stage.h); it stops including sil_macros.h and SM.h wholesale |  |
| `src/driver/polyglot.h` | 13 | 3 | KEEP |  |
| `src/driver/scrip_sm.h` | 9 | 3 | KEEP |  |
| `src/driver/sync_monitor.h` | 24 | 0 | DELETE if no includer (fan-in 0), else KEEP |  |
| `src/emitter/emit.h` | 870 | 159 | SPLIT into emit_state.h (the g_emit struct and the `_` macro, nothing else), bb_label.h (bb_label_t, bb_patch_t, jmp_kind_t, the label and patch prototypes), emit_medium.h (the medium enums and emitter_text_*/emitter_pos_*/emitter_end_* prototypes), emit_sm.h (the 46 emit_sm_* prototypes of the state machine), bb_walk_states.h (stmt_t, prog_t, bb_conj_state_t, bb_catch_state_t, bb_match_kids_state_t: the walkers of emit.cpp), bb_pl_call_state.h (pl_gz_callee_t, pl_gz_call_state_t, pl_ix_arm_t and the Prolog call states, beside their templates), emit_data.h (emit_data_*, data_buf_*), emit_knobs.h; emit.h itself becomes the interface header of emit.cpp alone (its own prototypes, no includes but forward declarations) | the measured umbrella: eight former headers pasted at lines 9, 80, 106, 179, 215, 248, 276, 728, 742, 795, 815, 828; 143 of its 159 TUs are templates that need only emit_state.h, bb_label.h and x86_ops.h |
| `src/emitter/emit_decls.h` | 78 | 0 | KEEP as emit.cpp-private; its two .inc includes go with zeta-layout step 5c; bb_templates.h is included by emit.cpp directly, not through this file |  |
| `src/emitter/emit_head.h` | 49 | 1 | MERGE into g_emitter.h (fan-in 1, the same TU) |  |
| `src/emitter/g_emitter.h` | 225 | 1 | KEEP (already the emitter-private state, C++ only, fan-in 1); it stops including emit.h and includes emit_state.h and bb_label.h |  |
| `src/emitter/sil_macros.h` | 43 | 22 | KEEP (18 macros, 22 TUs: the sil instruction macros used by the driver and the text medium); it is a definitions header of one family |  |
| `src/ir/IR.h` | 370 | 209 | SPLIT into ir_ops.h (the op enum and its names), ir_node.h (IR_t, IR_ref_t, IR_lit_t and the one-line ir_is_* predicates), ir_graph.h (IR_graph_t, IR_vslot_t), ir_plan_facts.h (IR_plan_facts_t, the CLOSED REGISTRY pf), ir_construct.h (IR_construct_t and the ck enum); the 28 inline bodies longer than one expression move to ir_node.c | reaches 209 TUs (206 of 1,122 at the ceo's count) through emit.h and x86_asm.h while 49 TUs name IR_t and 37 IR_graph_t; after: ir_node.h about 50, ir_graph.h about 40, ir_plan_facts.h the planner, the emitter and the dump |
| `src/ir/SM.h` | 17 | 191 | KEEP (the state-machine enum, one family); the five TUs that name it include it directly |  |
| `src/ir/XA.h` | 7 | 159 | MERGE into x86_ops.h (one struct of the xa template road, reached by 159 through emit.h and the template commons) |  |
| `src/ir/ab_abi.h` | 20 | 3 | KEEP |  |
| `src/ir/ast.h` | 152 | 215 | KEEP: the pruned parse tree (tree_t) is one structure and this is its header; its five inline bodies longer than one line move to tree.c; it stops including ct_arena.h | declared BASE for parsers, lower and driver (51 TUs name tree_t); the emitter and the runtime never see it |
| `src/ir/bb_box.h` | 47 | 192 | SPLIT: the box kinds enum stays as bb_box.h (one family); the 14 structs are the port records and go to bb_ports.h; the 10 prototypes to the TU that defines them | reaches 192 through emit.h |
| `src/ir/bb_build.h` | 5 | 13 | MERGE into bb_box.h (5 lines) |  |
| `src/ir/bb_pool.h` | 22 | 164 | KEEP (the slab pool's interface, 14 prototypes of bb_pool.c); included by the three TUs that call it | reaches 164 through emit.h today |
| `src/ir/bb_program.h` | 9 | 187 | MERGE into stage2.h (one struct, 2 prototypes, fan-in 187 only through stage2.h) |  |
| `src/ir/call_forms.h` | 46 | 168 | KEEP (one family: the call-form records, 8 structs, 20 prototypes of call_forms.c); included directly by the planner and the emitter, no longer through emit.h |  |
| `src/ir/cset_block.h` | 26 | 0 | DELETE if no includer (fan-in 0 at the census); else KEEP |  |
| `src/ir/ct_arena.h` | 27 | 261 | KEEP, declared BASE: the compile-time arena is the allocator of every compile-time object; ast.h and ct_vec.h stop including it (a pointer to an arena is a forward declaration) | reaches 261 (476 of 1,122) today; after the split only the TUs that call ct_* include it |
| `src/ir/ct_vec.h` | 34 | 242 | KEEP, declared BASE for the compile-time layers (ir, lower, optimizer, planner, emitter, driver, parsers); its two inline bodies stay (one expression each) | reaches 242; the runtime does not use it and stops reaching it |
| `src/ir/descr.h` | 151 | 224 | SPLIT into descr_tags.h (the DT_ enum, the three bits, DT_DATA_STRIDE: what templates and asm need) and descr.h (DESCR_t with its two always_inline source-node accessors and the IS_*_fn predicates, one line each); VCELL_t moves to table.h with its table | a BASE header: DESCR_t is the value of every language; 109 TUs name it, 224 reach it today; descr_tags.h is the wide one after the split and is declared base for that reason |
| `src/ir/descr_tags.inc` | 37 | 17 | KEEP as the generated tag names (one includer) |  |
| `src/ir/dtp.h` | 66 | 18 | KEEP (the DTP record family) |  |
| `src/ir/emit_ir.h` | 9 | 132 | MERGE into ir_node.h (one prototype, no struct) |  |
| `src/ir/gc_frame_map.h` | 93 | 14 | KEEP (the frame map quad, one family; included by the planner, the emitter and the collector) |  |
| `src/ir/ir_node_index.h` | 14 | 9 | KEEP (one family) |  |
| `src/ir/pin_va.h` | 19 | 150 | KEEP (the pinned virtual addresses, 12 macros, one family: the GVA island); x86_asm.h stops including it, the two TUs that use it include it |  |
| `src/ir/rk_opname.h` | 15 | 2 | KEEP (Raku op names, 2 TUs) |  |
| `src/ir/stage2.h` | 112 | 186 | SPLIT into stage2.h (the stage record of the driver, 4 structs) and the per-language stage structs beside their lowerers (lower_<lang>_stage.h); it stops being the way the driver reaches SM.h and bb_program.h | 14 structs, reaches 186 through x86_asm.h and planner_head.h |
| `src/ir/stno_map.h` | 24 | 159 | KEEP (one structure, the statement-number map); included by the two TUs that use it, not by emit.h |  |
| `src/lower/g_lower.h` | 281 | 20 | KEEP (the lowerer's granted state, 17 structs of one family) |  |
| `src/lower/lc_vec.h` | 4 | 34 | KEEP |  |
| `src/lower/lower.h` | 62 | 23 | SPLIT: lower.h keeps the stage interface; the 42 prototypes of the per-language lowerers go to lower_<lang>.h beside each |  |
| `src/lower/lower_pascal_class.h` | 4 | 2 | MERGE into lower_pascal_types.h (4 lines) |  |
| `src/lower/lower_pascal_tree.h` | 267 | 20 | KEEP (the Pascal typer's tree records, 47 structs of one family, front-end step 3's) |  |
| `src/lower/lower_pascal_types.h` | 60 | 2 | KEEP |  |
| `src/lower/lower_rebus.h` | 8 | 11 | KEEP |  |
| `src/lower/lower_snobol4.h` | 8 | 2 | KEEP |  |
| `src/lower/pl_aggregate_names.h` | 11 | 2 | KEEP (name tables) |  |
| `src/lower/pl_arith_names.h` | 105 | 2 | KEEP |  |
| `src/lower/pl_control_names.h` | 20 | 2 | KEEP |  |
| `src/optimizer/arith_fold.h` | 10 | 0 | KEEP (one pass, one interface header; already the shape the rule asks for) |  |
| `src/optimizer/branch_chain.h` | 11 | 2 | KEEP (one pass, one interface header; already the shape the rule asks for) |  |
| `src/optimizer/const_fold.h` | 6 | 2 | KEEP (one pass, one interface header; already the shape the rule asks for) |  |
| `src/optimizer/copy_prop.h` | 6 | 2 | KEEP (one pass, one interface header; already the shape the rule asks for) |  |
| `src/optimizer/dead_goto.h` | 6 | 2 | KEEP (one pass, one interface header; already the shape the rule asks for) |  |
| `src/optimizer/dead_pure.h` | 6 | 2 | KEEP (one pass, one interface header; already the shape the rule asks for) |  |
| `src/optimizer/gva_collect.h` | 23 | 1 | KEEP (one pass, one interface header; already the shape the rule asks for) |  |
| `src/optimizer/ir_index.h` | 79 | 13 | KEEP (one pass, one interface header; already the shape the rule asks for) |  |
| `src/optimizer/ir_query.h` | 5 | 10 | KEEP (one pass, one interface header; already the shape the rule asks for) |  |
| `src/optimizer/optimizer.h` | 6 | 1 | KEEP (one pass, one interface header; already the shape the rule asks for) |  |
| `src/optimizer/proc_collect.h` | 12 | 1 | KEEP (one pass, one interface header; already the shape the rule asks for) |  |
| `src/parsers/g_parser.h` | 11 | 5 | KEEP (the parsers' granted state) |  |
| `src/parsers/icon/icon_driver.h` | 9 | 11 | KEEP (a per-language front-end header with a fan-in of 2 to 19; the bison .tab.h files are generated) |  |
| `src/parsers/icon/icon_lex.h` | 156 | 13 | KEEP (a per-language front-end header with a fan-in of 2 to 19; the bison .tab.h files are generated) |  |
| `src/parsers/icon/icon_parse.h` | 19 | 2 | KEEP (a per-language front-end header with a fan-in of 2 to 19; the bison .tab.h files are generated) |  |
| `src/parsers/pascal/pascal.tab.h` | 212 | 2 | KEEP (a per-language front-end header with a fan-in of 2 to 19; the bison .tab.h files are generated) |  |
| `src/parsers/pascal/pascal_driver.h` | 9 | 3 | KEEP (a per-language front-end header with a fan-in of 2 to 19; the bison .tab.h files are generated) |  |
| `src/parsers/pascal/pascal_prelude_units.inc` | 2158 | 1 | KEEP (generated, one includer) |  |
| `src/parsers/prolog/pl_cell.h` | 79 | 0 | DELETE if no includer (fan-in 0), else KEEP; it stops including rt_pl_trail.h and rt_arena.h |  |
| `src/parsers/prolog/prolog_driver.h` | 10 | 11 | KEEP (a per-language front-end header with a fan-in of 2 to 19; the bison .tab.h files are generated) |  |
| `src/parsers/prolog/prolog_lex.h` | 85 | 3 | KEEP (a per-language front-end header with a fan-in of 2 to 19; the bison .tab.h files are generated) |  |
| `src/parsers/prolog/prolog_lower.h` | 7 | 2 | KEEP (a per-language front-end header with a fan-in of 2 to 19; the bison .tab.h files are generated) |  |
| `src/parsers/prolog/prolog_parse.h` | 46 | 3 | KEEP (a per-language front-end header with a fan-in of 2 to 19; the bison .tab.h files are generated) |  |
| `src/parsers/prolog/prolog_prelude_libs.inc` | 34586 | 1 | KEEP (the embedded prelude, generated, one includer) |  |
| `src/parsers/raku/raku_driver.h` | 6 | 11 | KEEP (a per-language front-end header with a fan-in of 2 to 19; the bison .tab.h files are generated) |  |
| `src/parsers/raku/rk_core_names.h` | 51439 | 1 | RENAME to rk_core_names.inc (51,439 lines, 2.3 MB of embedded names: data, one includer) |  |
| `src/parsers/raku/rk_regex.h` | 5 | 2 | KEEP (a per-language front-end header with a fan-in of 2 to 19; the bison .tab.h files are generated) |  |
| `src/parsers/raku/rk_syntax.h` | 11 | 3 | KEEP (a per-language front-end header with a fan-in of 2 to 19; the bison .tab.h files are generated) |  |
| `src/parsers/raku/rk_tree.h` | 147 | 2 | KEEP (a per-language front-end header with a fan-in of 2 to 19; the bison .tab.h files are generated) |  |
| `src/parsers/rebus/rebus.h` | 40 | 15 | KEEP (a per-language front-end header with a fan-in of 2 to 19; the bison .tab.h files are generated) |  |
| `src/parsers/rebus/rebus.tab.h` | 171 | 2 | KEEP (a per-language front-end header with a fan-in of 2 to 19; the bison .tab.h files are generated) |  |
| `src/parsers/snobol4/scrip_cc.h` | 112 | 19 | KEEP (a per-language front-end header with a fan-in of 2 to 19; the bison .tab.h files are generated) |  |
| `src/parsers/snobol4/snobol4.h` | 33 | 2 | KEEP (a per-language front-end header with a fan-in of 2 to 19; the bison .tab.h files are generated) |  |
| `src/parsers/snobol4/snobol4.tab.h` | 153 | 2 | KEEP (a per-language front-end header with a fan-in of 2 to 19; the bison .tab.h files are generated) |  |
| `src/parsers/snobol4/unicode_alpha_ranges.h` | 660 | 0 | RENAME to unicode_alpha_ranges.inc if included (data), DELETE if not (fan-in 0) |  |
| `src/parsers/snocone/snocone_driver.h` | 6 | 12 | KEEP (a per-language front-end header with a fan-in of 2 to 19; the bison .tab.h files are generated) |  |
| `src/parsers/snocone/snocone_lex.h` | 16 | 2 | KEEP (a per-language front-end header with a fan-in of 2 to 19; the bison .tab.h files are generated) |  |
| `src/parsers/snocone/snocone_parse.tab.h` | 199 | 2 | KEEP (a per-language front-end header with a fan-in of 2 to 19; the bison .tab.h files are generated) |  |
| `src/planner/box_cell_shapes.inc` | 32 | 1 | KEEP (generated from box_cell_shapes.tsv, one includer) |  |
| `src/planner/frame_layout.h` | 87 | 8 | KEEP (the frame facts, one family; 76 prototypes of frame_layout.c) |  |
| `src/planner/g_planner.h` | 106 | 8 | KEEP (Lon's granted struct, one structure); it stops including stage2.h and ir_index.h and forward-declares |  |
| `src/planner/planner.h` | 248 | 7 | SPLIT: planner.h keeps the planner stage's interface; its 8 structs are the plan record and go to zeta_plan.h (zeta_plan_t and the row columns the emitter reads as struct fields, R2 of ARCH-ZETA-LAYOUT) and act_words.h; the 112 prototypes go to their defining files' headers (zeta_plan.h, plan_facts.h, act_words.h) |  |
| `src/planner/planner_head.h` | 30 | 7 | DELETE (an umbrella of twelve includes for the planner TUs; each planner TU includes what it uses) |  |
| `src/planner/zeta_depth.h` | 37 | 9 | KEEP (one family) |  |
| `src/runtime/builtin_ids.h` | 216 | 3 | KEEP (the builtin ids, one family) |  |
| `src/runtime/builtin_table.h` | 101 | 3 | KEEP (ARCH-BUILTIN-TABLE's table and header; the .inc generated) |  |
| `src/runtime/builtin_table.inc` | 591 | 1 | KEEP (generated, one includer) |  |
| `src/runtime/builtins/box_rt.h` | 8 | 0 | DELETE if no includer (fan-in 0), else KEEP |  |
| `src/runtime/builtins/gen.h` | 20 | 19 | KEEP (the generator record) |  |
| `src/runtime/builtins/gen_runtime.h` | 39 | 15 | KEEP (gen_runtime.c's interface); it stops including bb_box.h and SM.h wholesale |  |
| `src/runtime/builtins/gen_value.h` | 8 | 2 | KEEP |  |
| `src/runtime/by_name_dispatch.h` | 12 | 1 | KEEP (by_name_dispatch.c's interface) |  |
| `src/runtime/core/coerce.h` | 7 | 5 | KEEP (coerce.c's interface) |  |
| `src/runtime/core/core.h` | 382 | 203 | SPLIT into table.h (TBBLK_t, TBBUCK_t, TBPAIR_t, VCELL_t from descr.h, the table_* and tbl_key_* prototypes; the collector's gc_layout rows read it), array.h (ARBLK_t, array_*), datatype.h (DATBLK_t, DATINST_t, DEFINE_fn, DATA/FIELD_*), tree_blk.h (TREEBLK_t), nv.h (NvPair, the NV_* cells, macros and prototypes), trace.h (trace_ent_t and the 26 rt_trace_* prototypes), icn_builtins.h (icn_bi_rec and the 17 core_icn_* prototypes), setexit.h (sno_setexit_*, the g_rtccb SETEXIT slots' names), core_error.h (core_runtime_error and the error voice), pat_assign.h (pat_assign_*, pat_fence_*), comm_var.h (comm_var_*); core.h itself becomes the interface header of core.c alone and includes NEITHER g_runtime.h NOR descr.h (its prototypes forward-declare) | 266 prototypes of a dozen families; reaches 203 TUs (217 of 1,122) while TBBLK_t is named by 8, ARBLK_t by 11, DATBLK_t by 8, NV_t by 1; its include of g_runtime.h is what carries the nineteen runtime parts into 215 TUs |
| `src/runtime/core/core_errjmp.h` | 10 | 5 | DELETE with exceptions step 9 (the catchers go); KEEP until then |  |
| `src/runtime/core/descr.h` | 2 | 218 | DELETE (a two-line forwarder to ir/descr.h; every includer names ir/descr.h or descr_tags.h by its path) |  |
| `src/runtime/core/g_runtime.h` | 51 | 215 | KEEP as the one struct of nineteen parts (option A, no new global): it includes the nineteen part headers because g_runtime_t holds them BY VALUE and the asm reads fixed offsets from g_runtime; core.h stops including it, so it reaches only the 57 TUs that name g_runtime (215 today). OPTION B, FOR LON'S WORD (section 3.4): the nineteen parts become nineteen named globals of their part types and a TU includes only the part it reads; an edit to g_runtime_gc.h then recompiles its 3 users, not 57 |  |
| `src/runtime/core/g_runtime_abi.h` | 100 | 215 | KEEP (one part structure of the runtime state; included by g_runtime.h and, under option B, by its abi users alone) |  |
| `src/runtime/core/g_runtime_abi.inc` | 69 | 3 | KEEP (the ABI offsets the asm and the driver read; three includers) |  |
| `src/runtime/core/g_runtime_abi_check.inc` | 69 | 1 | KEEP (the static asserts over the ABI offsets, one includer) |  |
| `src/runtime/core/g_runtime_agg.h` | 4 | 215 | KEEP (one part structure of the runtime state; included by g_runtime.h and, under option B, by its agg users alone) |  |
| `src/runtime/core/g_runtime_atoms.h` | 33 | 215 | KEEP (one part structure of the runtime state; included by g_runtime.h and, under option B, by its atoms users alone) |  |
| `src/runtime/core/g_runtime_bbprof.h` | 25 | 215 | KEEP (one part structure of the runtime state; included by g_runtime.h and, under option B, by its bbprof users alone) |  |
| `src/runtime/core/g_runtime_bn.h` | 34 | 215 | KEEP (one part structure of the runtime state; included by g_runtime.h and, under option B, by its bn users alone) |  |
| `src/runtime/core/g_runtime_coexpr.h` | 5 | 215 | KEEP (one part structure of the runtime state; included by g_runtime.h and, under option B, by its coexpr users alone) |  |
| `src/runtime/core/g_runtime_core.h` | 64 | 215 | KEEP (one part structure of the runtime state; included by g_runtime.h and, under option B, by its core users alone) |  |
| `src/runtime/core/g_runtime_entry.h` | 0 | 0 | DELETE (0 lines) |  |
| `src/runtime/core/g_runtime_eval.h` | 17 | 215 | KEEP (one part structure of the runtime state; included by g_runtime.h and, under option B, by its eval users alone) |  |
| `src/runtime/core/g_runtime_gc.h` | 139 | 215 | KEEP (one part structure of the runtime state; included by g_runtime.h and, under option B, by its gc users alone) |  |
| `src/runtime/core/g_runtime_kw.h` | 20 | 215 | KEEP (one part structure of the runtime state; included by g_runtime.h and, under option B, by its kw users alone) |  |
| `src/runtime/core/g_runtime_misc.h` | 71 | 215 | KEEP (one part structure of the runtime state; included by g_runtime.h and, under option B, by its misc users alone) |  |
| `src/runtime/core/g_runtime_pas.h` | 8 | 215 | KEEP (one part structure of the runtime state; included by g_runtime.h and, under option B, by its pas users alone) |  |
| `src/runtime/core/g_runtime_pc.h` | 5 | 215 | KEEP (one part structure of the runtime state; included by g_runtime.h and, under option B, by its pc users alone) |  |
| `src/runtime/core/g_runtime_pleng.h` | 20 | 214 | KEEP (one part structure of the runtime state; included by g_runtime.h and, under option B, by its pleng users alone) |  |
| `src/runtime/core/g_runtime_rt.h` | 24 | 215 | KEEP (one part structure of the runtime state; included by g_runtime.h and, under option B, by its rt users alone) |  |
| `src/runtime/core/g_runtime_slab.h` | 7 | 215 | KEEP (one part structure of the runtime state; included by g_runtime.h and, under option B, by its slab users alone) |  |
| `src/runtime/core/g_runtime_tap.h` | 4 | 215 | KEEP (one part structure of the runtime state; included by g_runtime.h and, under option B, by its tap users alone) |  |
| `src/runtime/core/g_runtime_vec.h` | 5 | 215 | KEEP (one part structure of the runtime state; included by g_runtime.h and, under option B, by its vec users alone) |  |
| `src/runtime/core/g_runtime_zsm.h` | 30 | 215 | KEEP (one part structure of the runtime state; included by g_runtime.h and, under option B, by its zsm users alone) |  |
| `src/runtime/core/name_t.h` | 23 | 193 | KEEP, declared BASE for the runtime and the emitter (the name cell is one structure; 193 reach it through bb_box.h today, the users include it directly after) |  |
| `src/runtime/core/runtime_shim.h` | 64 | 10 | KEEP (the shim definitions, 10 TUs); it stops including rt_arena.h |  |
| `src/runtime/core/utf8.h` | 34 | 4 | KEEP |  |
| `src/runtime/keywords.h` | 32 | 2 | KEEP |  |
| `src/runtime/pas_bi_names.h` | 31 | 1 | KEEP |  |
| `src/runtime/pattern_match.h` | 7 | 1 | KEEP; it gains nothing (DTP_t and dtp_rcp_t move to pattern_blocks.h by ARCH-GC 13.14) |  |
| `src/runtime/pl_meta_specs.inc` | 705 | 1 | KEEP (data, one includer) |  |
| `src/runtime/pl_rat.h` | 23 | 3 | KEEP |  |
| `src/runtime/re.h` | 14 | 10 | KEEP |  |
| `src/runtime/rk_case_table.h` | 700 | 1 | RENAME to rk_case_table.inc (700 lines of table data, one includer) |  |
| `src/runtime/rk_rakudo_method_names.inc` | 51 | 1 | KEEP (generated data, one includer) |  |
| `src/runtime/rk_unicode_norm_tables.inc` | 928 | 1 | KEEP (data, one includer) |  |
| `src/runtime/rt/bbprof.h` | 14 | 1 | KEEP |  |
| `src/runtime/rt/gc_audit_b.h` | 28 | 1 | KEEP |  |
| `src/runtime/rt/gc_heap.h` | 116 | 29 | SPLIT: gc_heap.h keeps the heap block header (rt_hblk_t, the HB_ codes and HB_KIND_NAME) and the collector's interface; the 57 prototypes of other files (the slide, the chain, the roots) go to their defining files' headers (gc_chain.h, gc_roots.h); gc_layout.h (hq_collector's) stays beside |  |
| `src/runtime/rt/gc_slot_table.h` | 0 | 0 | DELETE (0 lines; the file is gc_layout.h, ARCH-GC 13.14) |  |
| `src/runtime/rt/pl_rational.h` | 76 | 2 | KEEP (one family) |  |
| `src/runtime/rt/portcount.h` | 15 | 2 | KEEP |  |
| `src/runtime/rt/prolog_atom.h` | 31 | 20 | KEEP (the atom table, one family) |  |
| `src/runtime/rt/rt.h` | 245 | 11 | SPLIT by family: rt.h keeps rt.c's own prototypes; the 206 prototypes of other files go to those files' interface headers (rt_runtime.h, rt_call.h, rt_pattern.h as the definitions fall) | 206 prototypes, 11 TUs: a grab-bag, not an umbrella |
| `src/runtime/rt/rt_arena.h` | 33 | 183 | KEEP (the run-time arena, one family; 17 prototypes); it stops being reached through emit.h (183 today) and is included by its users |  |
| `src/runtime/rt/rt_coexpr.h` | 86 | 4 | KEEP (one family) |  |
| `src/runtime/rt/rt_diag.h` | 6 | 36 | KEEP (6 lines, the diagnostic switch; declared BASE for the runtime) |  |
| `src/runtime/rt/rt_list_view.h` | 23 | 4 | KEEP |  |
| `src/runtime/rt/rt_pl_trail.h` | 113 | 151 | SPLIT: rt_pl_trail.h keeps the trail structure and its 7 prototypes; the 26 inline bodies move to rt_pl_trail.c (they are not one-line accessors) with the two macros the templates read staying as pl_trail_layout.h (offsets only) | reaches 151 TUs through x86_asm.h and pl_cell.h; 113 lines of which 26 are inline bodies |
| `src/runtime/rt/rt_protected.h` | 13 | 3 | KEEP |  |
| `src/runtime/rt/rt_sc_module.h` | 17 | 1 | KEEP |  |
| `src/runtime/rt/rt_slab.h` | 18 | 185 | KEEP (the sealed slab, one structure); included by its users, not through rt_arena.h |  |
| `src/runtime/rt/rtx_try.h` | 49 | 7 | KEEP (the try road's interface) |  |
| `src/runtime/rt_entry_table.inc` | 64 | 0 | KEEP for zeta-layout step 5 (no includer today: it is the table R4 generates) |  |
| `src/runtime/rtx/rtcc.h` | 55 | 148 | KEEP (the caller-saved spill block, one structure with its slot names and asserts); x86_asm.h stops including it, x86_rtcc.h and the runtime files that read slots include it | reaches 148 through x86_asm.h; a dozen TUs name it |
| `src/runtime/rtx/rtx_abi.inc` | 33 | 16 | KEEP (the asm ABI constants, included by the .s leaves) |  |
| `src/runtime/rx.h` | 19 | 2 | KEEP |  |
| `src/runtime/snobol4_system_fns.h` | 55 | 5 | KEEP |  |
| `src/runtime/string_ops.h` | 15 | 1 | KEEP (string_ops.c's interface) |  |
| `src/templates/bb/bb_common.h` | 55 | 0 | DELETE if no includer (fan-in 0, 44 prototypes duplicated in bb_templates.h), else MERGE |  |
| `src/templates/bb/bb_pl_cell.h` | 122 | 8 | KEEP (the Prolog cell layout the templates read); it stops including rt_pl_trail.h and stage2.h and includes pl_trail_layout.h |  |
| `src/templates/bb/bb_pl_leaf_kinds.h` | 14 | 3 | KEEP |  |
| `src/templates/bb/bb_template_common.h` | 14 | 131 | KEEP as the templates' one common header, re-cut to include emit_state.h, bb_label.h, x86_ops.h and ir_node.h only (today it includes emit.h, emit_ir.h and XA.h); the `_` macro and the three zls_ prototypes stay | 131 TUs: this is where the templates' fan-in is decided |
| `src/templates/bb/bb_templates.h` | 197 | 45 | KEEP (the 136 template entry prototypes, included by emit.cpp and the box table; a template includes it only when it calls another template) |  |
| `src/templates/x86/gc_allocating_table.inc` | 3003 | 0 | DELETE with zeta-layout step 5c (R4); KEEP until then |  |
| `src/templates/x86/rtx_clobber_table.inc` | 416 | 0 | DELETE with zeta-layout step 5c; KEEP until then |  |
| `src/templates/x86/rtx_twin_table.inc` | 49 | 0 | KEEP (generated, emit.cpp's) |  |
| `src/templates/x86/x86_arg_roles.h` | 5 | 146 | KEEP (one enum); included by the TUs that name it, not through x86_asm.h |  |
| `src/templates/x86/x86_asm.h` | 3310 | 145 | SPLIT: x86_asm.cpp (the encoder core: xop, x86(), x86_core_, x86_core_inner_, the text and binary media, the record encoder x86_rec_*, the internal label bookkeeping: lines 1-1800 and 2893 as compiled code, compiled ONCE), x86_ops.h (the API every template reads: the 116 helpers the templates name, as prototypes, plus the one-line port helpers x86_alpha/beta/gamma/omega/bomb/begin kept inline), x86_rtcc.h/.cpp (the 16 rtcc write-back, reload and call helpers), x86_frame.h/.cpp (the 19 frame, 9 align, 31 rsp and the hb helpers), x86_jump.h/.cpp (jmp, jcc, deflabel, internal labels, X86_INTERNAL_MAX), x86_zeta.h/.cpp (zop, zref, ztos, zdp, zsm: the cell forms and the verifier emitters), x86_gc.h/.cpp (the gate, the 15 poll forms and the site helpers, which zeta-layout step 6 then reduces to one), x86_call.h/.cpp (fc, pl, port and call forms), x86_icn.h/.cpp (the Icon scanning helpers), x86_consts.cpp (the 35 const_ tables), x86_rsp_tracker.h/.cpp (x86_rsp_st_t, lines 199-262, deleted by zeta-layout step 3); the 40-odd extern "C" runtime prototypes it declares go to their owners' interface headers | 3,310 lines, 466 inline functions, 145 TUs (144 of 1,122): at -O0 none of the inline bodies is inlined, so every template object today carries its own copy of the encoder; compiled once, an encoder edit recompiles one TU |
| `src/templates/xa/xa_template_common.h` | 7 | 17 | MERGE into bb_template_common.h (7 lines; the xa templates are templates) |  |
| `src/templates/xa/xa_templates.h` | 20 | 1 | KEEP (the 16 xa entry prototypes) |  |
| `src/tools/emit_per_kind_audit.h` | 5 | 0 | DELETE if no includer (fan-in 0), else KEEP |  |

## 5. THE ROLL-OUT UNDER LARGE CHUNKS (CEO-1478): ONE SMALL SPLIT WITH ITS PROOF FIRST, THEN THE REST IN FEW LARGE LANDINGS IN A QUIET WINDOW

A header move conflicts with every seat's in-flight work, so each large landing is announced by the ceo as a QUIET WINDOW (no other SCRIP landing for its hour), rebased at the last minute, proved by R5 and pushed; the step order follows the dependency of the moves and the memory-model plan (zeta-layout step 3 deletes the tracker and step 6 the poll family: the x86 split lands BEFORE them so they delete files, not spans; it waits for step 2a and 1b, which are in the templates today).

| step | what | executor (sized to the seat) | proof | DONE-WHEN token |
|---|---|---|---|---|
| 1a | the instruments and the gate (§ 2) with the baseline written; no header moves | hq_templates (Sonnet: a specified instrument) | the gate reads this page's numbers; `util_objects_identical_stripped.sh` proves itself on one no-op rebuild | the three scripts exist, the gate runs RULING and prints every header over the ceiling |
| 1b | THE SMALL SPLIT: core.h stops including g_runtime.h and descr.h; table.h, array.h and datatype.h cut out of core.h; the 57 real users include g_runtime.h directly | hq_runtime (Sonnet: mechanical, its own files) | R5 identical objects; the eight smokes | g_runtime.h fan-in ≤ 70 on this root (from 215); objects identical |
| 2 | x86_asm.h → x86_asm.cpp + x86_ops.h + the eight family pairs + x86_consts.cpp + x86_rsp_tracker; the extern "C" prototypes to their owners; bb_template_common.h re-cut | hq_templates (Sonnet; the cfo on escalation); after zeta 2a and 1b land, before zeta 3 | R5; the eight smokes; `util_emitter_memory_model_census.py` unchanged | x86_asm.h deleted; x86_asm.cpp one unit; no template includes more than x86_ops.h plus the family headers it names (`--unused` 0 over templates) |
| 3 | emit.h → emit_state.h, bb_label.h, emit_medium.h, emit_sm.h, bb_walk_states.h, bb_pl_call_state.h, emit_data.h, emit_knobs.h; XA.h, emit_ir.h, emit_head.h merged | hq_templates with the cfo (the emitter's own records need judgment) | R5; the eight smokes | emit.h fan-in ≤ 12; emit_state.h declared base |
| 4 | IR.h → ir_ops.h, ir_node.h, ir_graph.h, ir_plan_facts.h, ir_construct.h; bb_box.h/bb_ports.h; stage2.h per language; the small ir/ headers included by their users; planner_head.h deleted, planner.h → zeta_plan.h and act_words.h | the cao (Opus: the IR layer crosses parsers, lower, optimizer, planner, emitter and driver) | R5; the eight smokes; the planner gates | IR.h deleted; ir_node.h ≤ 60, ir_graph.h ≤ 50 on this root |
| 5 | the runtime's rest: core.h's remaining families (trace, nv, icn builtins, setexit, error voice, pat_assign, comm_var), rt.h and gc_heap.h per file, rt_pl_trail.h's bodies compiled, rtcc.h and rt_arena.h to their users, descr.h split and the forwarder deleted | hq_runtime (Sonnet) | R5; the eight smokes; the collector gates | core.h ≤ 45, rt_pl_trail.h ≤ 25, rtcc.h ≤ 20 on this root |
| 6 | the layers' interface headers: driver_private.h, lower.h per file; the parsers' and optimizer's already in shape; the data headers renamed .inc; the nine dead headers deleted; every include by path from src/ and the -I list cut to `-I src` | hq_snocone (Sonnet: its lane holds the parsers; mechanical) | R5; the eight smokes; `make parsers-sc` | arm 4 of the gate 0 |
| 7 | THE FINISH: the gate BLOCKING with every arm 0; the after table of § 3.7 measured and written here; option B put to Lon with the measured option-A numbers | hq_templates closes | the gate, the census | `test_gate_no_header_reaches_more_units_than_its_users.sh` green and in the blocking set |

## 6. What a builder must not do

- Move a declaration and change its text: a move is a move (R5 proves it). A fix found on the way is its own landing.
- Create a new umbrella to make a step pass (a `common.h` that includes the split headers). The gate's arm 2 reads 0.
- Add a header to the base set, or raise the ceiling, without a ruling on this page.
- Land a large step outside the ceo's quiet window, or without the last-minute rebase: a header move that conflicts is reverted, not merged by hand.
- Leave the tracker or the poll family in a header the zeta steps will delete: step 2 puts each in its own file.

