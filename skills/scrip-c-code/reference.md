# SCRIP C code: the reference (the detail behind SKILL.md; read the section you need)


Every hand-written `.c`, `.h` and `.inc` under `SCRIP/src/` (the compiler, the lowerers, the planner, the emitter's C, the runtime, the driver; the bison/flex parsers and the generated tables excepted) is written to one shape and one set of prohibitions that Lon has ruled on verbatim. The checkers are the law's instruments and run on every file a landing touches. The law is RULES.md (§ C code style line 223, CEO-1565; the `malloc` FACT RULE line 29, CEO-832/842; NO NEW GLOBAL VARIABLES line 252; THE LENGTH IS CARRIED line 236; NO `-O2`; NO FIXED LIMITS), § 6 below (dynamic storage, the ratchet, the runtime globals). Lines quoted below are from SCRIP 8e366c454 and harness 230edb1.

## 1. THE RULES (each with its receipt)

- **THE 200-COLUMN HIERARCHY RULE** (Lon 2026-10-08, verbatim: *"Put code on 200 character lines. If does not fit, begin wrapping at that level and keep those lines long. No line shall EXCEED 200 characters, all must fit."* · *"when you begin wrapping, it must be at hierarchical C structures."* · *"if at one level it over flows a line, then you break at the hiearchical level and start the rule over again at the indention. But each child at the level gets its own line."*; CEO-1565; RULES.md 223): an item -- a statement, or a whole block with its else-chain -- that fits goes on ONE line of at most 200 UTF-8 bytes at its indent; an item that does not fit is a block that opens on its own line, lays every child out by the same rule one level deeper, each child on its own line, and closes on its own line; a statement longer than a line wraps at its own nesting level with long continuation lines; a preprocessor directive keeps its own line. `.cpp` and everything under `src/templates/` is LINE-ORIENTED instead (the box-templates skill).
- **ZERO COMMENTS, ZERO BLANK LINES** (the same word: *"No comments just comment line breaks. No blank lines."*): the only comment is the separator `/*----...----*/` re-cut to exactly 200 characters between functions; `strip_comments.py --check` and `util_reflow_200.py --check` refuse anything else. What a comment would have said goes in the ARCH page or the GOAL cursor, not the code. A truncated separator is an open comment that swallows the next function: the checker counts them.
- **NO `malloc`, `calloc`, `realloc`, `free`, ANYWHERE** (Lon 2026-09-17, verbatim: *"Ensure that we never use malloc/free since we are doing GC instead. ... Make a FACT RULE which disallows calling those 4 functions anywhere in SCRIP."*; RULES.md 29: *"WE HAVE A GARBAGE COLLECTOR. THAT IS THE ALLOCATOR."*): in C and in asm, under any spelling, through a macro, a typedef'd pointer, a `#define` alias or a wrapper; run-time values live on the collected heap (`rtx_alloc.s`, the runtime allocator), compile-time populations in the arena (`src/ir/ct_arena.c`: `ct_alloc`, `ct_try_alloc`, `ct_zalloc`, `ct_grow`, `ct_strdup`, `ct_strndup`, `ct_drop`, `ct_arena_bytes`); `test_gate_c_allocators_are_eradicated_and_say_where_they_went.sh` holds the zero. The rule overturned a cto ruling the same hour it was made; that is part of the record.
- **NO NEW GLOBAL VARIABLE WITHOUT LON'S EXPLICIT PERMISSION** (Lon 2026-08-13; RULES.md 252: *"no session creates ANY new global variable -- file-scope mutable state, pinned VA slot, exported cell, parallel array, or equivalent -- in ANY repo without FIRST asking Lon in-chat and receiving permission that session."*): state rides registers (the r10/r11 wires), the stack (the three zetas), or a field of the stage's one struct -- `g_lower_t g_lower` (g_lower.h 280), `g_planner_t g_planner` (g_planner.h 105), `sm_emit_t g_emit` (emit.h 674), the runtime's `g_core_t`, `g_rt_t`, `g_abi_t`, `g_atoms_t`, `g_bn_t`, `g_zsm_t`, `g_misc_t`, `g_pl_eng_t` (`src/runtime/core/g_runtime_*.h`); a field is state too and needs the same grant when it is runtime state; `test_gate_no_new_function_scope_static.sh` and `test_gate_globals_census_counts_writable_sections_only.sh` (a symbol in `.data`/`.bss` counts, `.rodata` does not) hold the count; `audit_runtime_globals_census.py` asks of each one *"can that global live on one of the 3 ZETAS?"*.
- **NO FIXED LIMIT A PROGRAM CAN REACH** (Lon 2026-09-23: *"we must still handle almost everything without a FIXED LIMIT ... Scan the SCRIP for all fixed arrays, fixed buffers, etc."*; `audit_fixed_caps_census.py`, `test_gate_dyn_caps_ratchet.sh`: the population of fixed tables may only FALL, and a fall lowers the baseline in the same landing): a bound a program's size can exceed is a `cv_t` vector or an arena-grown table; a declared size (`-s`, `-d`) is the program's own hard cap, never a buffer's. The census is blind to `.y`/`.l` sources and to the second array after a semicolon; grep beside it.
- **NO `-O2` BUILDS, EVER** (Lon 2026-08-23; `RT_OPT ?= -O0 -g -fno-strict-aliasing -fwrapv -fno-omit-frame-pointer`, Makefile 59): the frame pointer and `-fwrapv` are what the collector's chain and the unbounded integers rely on; speed is measured by instruction count on the emitted code, not by the C compiler's optimiser.
- **THE LENGTH IS CARRIED, NEVER MEASURED** (Lon 2026-08-30: *"Remove all strlen on the DESCR .s that is totally INVALID and not performant. A NUL character is a valid string element."*; RULES.md 236): a DESCR's `slen` is the length; `strlen` on `.s` is both wrong and slow.
- **GENERATED TABLES ARE REGENERATED, NEVER EDITED**: `box_cell_shapes.inc`, `rt_entry_table.inc`, `gc_allocating_table.inc`, `builtin_table.inc`/`.h`, the parsers' tables; each has its `util_gen_*.py` and its `test_gate_*_is_current.sh`; regenerate BEFORE `make` or the freshness guard refuses the gate.
- **ONE KIND OF THING PER FIELD** (`test_gate_ir_field_discipline.sh`): a field never smuggles a pointer in an integer or a flag in a string; a union is declared, not punned.
- **NO LANGUAGE NAME PAST THE DRIVER** (CEO-1838/1840): `scrip_exts[]` in `src/driver/scrip.c` is the last place a language is named; after lower, every variance is an IR fact (the lowering skill).

## 2. THE FILES

- `SCRIP/src/`: `driver/` (`scrip.c`), `parsers/<lang>/` (bison/flex: EXEMPT from the reflow and the comment strip, their generated outputs excluded from every census), `lower/`, `ir/` (`ir_node.h`, `ir_graph.h`, `ct_arena.c` and `ct_arena.h`, `ct_vec.h`), `planner/`, `emitter/` (`emit.cpp` is C++ and line-oriented; `emit.h`, `g_emitter.h` are C and under the rule), `runtime/` (`rt/`, `core/`, `builtins/`, `rtx/`), `templates/` (line-oriented), `tools/`.
- The checkers, `harness/scripts/`: `util_reflow_200.py [--check | --apply | --proof | --objproof | --print] [--width 200] PATH...` (a directory names every C, C++ and `.inc` file under it; `src/parsers` and the two generated tables are never touched; `--proof` and `--objproof` prove the reflow changed nothing: the preprocessed text, or the object bytes, before and after), `strip_comments.py --check` (string- and char-literal aware; the generated flex/bison outputs excluded), `audit_fixed_caps_census.py [--tsv OUT] [--top N] [--dir src]` (`--tsv` takes an OUTPUT path and overwrites it), `audit_runtime_globals_census.py` (gated by `test_gate_globals_census_counts_writable_sections_only.sh`).
- The gates: `test_gate_c_allocators_are_eradicated_and_say_where_they_went.sh`, `test_gate_dyn_caps_ratchet.sh`, `test_gate_dyn_caps_a_long_label_or_procedure_name_passes_every_old_name_buffer.sh`, `test_gate_dyn_caps_a_long_prolog_term_and_a_regrown_function_table_pass_the_old_runtime_bounds.sh`, `test_gate_no_new_function_scope_static.sh`, `test_gate_globals_census_counts_writable_sections_only.sh`, `test_gate_pl_no_new_global.sh`, `test_gate_no_hidden_global_in_emitted.sh`, `test_gate_gc_the_lowerer_registries_are_rooted_not_malloced.sh`, `test_gate_ir_field_discipline.sh`, `test_gate_emit_no_lang.sh`; the Makefile's `preflight` (the cheap hermetic arms, no build) and `test` (the blocking set, the coo's).

## 3. WORKED EXAMPLES (quoted)

A function that fits goes on ONE line, `lower_common.c` 245 (the separator above it is the only comment):

```c
/*----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------*/
IR_t * lc_build(IR_graph_t * g, IR_e op, IR_t * γ, IR_t * ω) { IR_t * nd = IR_node_alloc(g, op); lc_γ_to(nd, γ); lc_ω_to(nd, ω); return nd; }
```

A block that does not fit opens on its own line and lays each child on its own line one level deeper, `lower_common.c` (the bb-source index): the `for` is the item that overflowed; its children are statements that fit, so each is one line; the `if` child with its block fits on one line, so it stays one line.

```c
    for (int i = 0; i < g_lower.lc.bb_src.n; i++) {
        const IR_t * k = g_lower.lc.bb_src.nd[i];
        size_t h = ((size_t)(uintptr_t) k >> 4) & (size_t)(cap - 1);
        while (t[h].k && t[h].k != k) h = (h + 1) & (size_t)(cap - 1);
        if (!t[h].k) { t[h].k = k; t[h].v = i; }
    }
```

The arena API every compile-time population uses, `ct_arena.h` 10-17 (the only allocator the compiler calls; a runtime `cv_t` freed adds a `ct_drop`, which the C-allocator census counts as a `ct_*` call, not a `free`):

```c
void *ct_alloc(size_t n);
void *ct_try_alloc(size_t n);
void *ct_zalloc(size_t n, size_t sz);
void *ct_grow(void *p, size_t n);
char *ct_strdup(const char *s);
void ct_drop(void *p);
```

The build flags that are law, `Makefile` 59: `RT_OPT ?= -O0 -g -fno-strict-aliasing -fwrapv -fno-omit-frame-pointer` with its own `⛔ NO -O2 BUILDS, EVER` beside it. The one stage struct a lowerer writes to, `g_lower.h` 280: `extern g_lower_t g_lower;` -- a new lowerer datum is a field of it (compile-time state, no grant), never a file-scope `static`.

## 4. THE PROVING INSTRUMENTS (harness/scripts)

- On every file a landing touches, before the commit: `python3 harness/scripts/util_reflow_200.py --check <paths>` and `python3 harness/scripts/strip_comments.py --check <paths>` (rc 0); `--apply` reflows, `--proof <paths>` shows the preprocessed text unchanged by the reflow.
- The ratchets the diff's area owns: `test_gate_dyn_caps_ratchet.sh` (a fixed table added is red; one removed lowers the baseline in the same commit: the baseline file named in the gate's header is lowered by hand in the same commit; `audit_fixed_caps_census.py` has no baseline writer, only `--tsv`, `--top`, `--dir`, `--selftest`), the C-allocator gate, the two globals gates, the generated-table `_is_current` gates for any table the change feeds.
- `make preflight` (the hermetic arms, under a second each, pinned by `test_gate_preflight_arms_stay_cheap.sh`) is cheap enough to run after every build; it is NOT the per-push check (CEO-1316: heavy verification once per batch of 3-4).
- `make -j8` with `-Werror` behaviour as the Makefile sets it; a warning is a red; `ccache` wraps every compile and is shared across roots, so a clean rebuild is `make pristine`.
- The census instruments for a question: `audit_fixed_caps_census.py --top 20`, `audit_runtime_globals_census.py`, `grep -rn 'malloc\|calloc\|realloc\|free(' src/ --include=*.c --include=*.h --include=*.s` (the gate's own grep is the law; yours is the preview).

## 5. THE FORBIDDEN FORMS

A line over 200 UTF-8 bytes; a blank line; a comment other than the 200-character separator; a block wrapped inside a line instead of opened on its own line; two children on one line when their parent overflowed; `malloc`/`calloc`/`realloc`/`free` under any spelling (`strdup`, `asprintf`, `getline`, `open_memstream`, a `realloc`ing wrapper, a `#define` alias); a file-scope or function-scope mutable `static` without the grant cited in the commit; a pinned VA slot, an exported cell, a parallel array; a `char buf[256]`, a `#define MAX_* 1024`, an array bound a program's size can exceed; `-O1`/`-O2`/`-O3` in any flag; `strlen` on a DESCR's `.s`; a generated `.inc` edited by hand; a field reused for a second kind of value; a language name past the driver; a `goto` into a box or a C function entering one (CEO-1576); a `#if 0` block (it is a comment); `pkill -f` or a shell pattern in a C `system()` call.

## 6. DYNAMIC STORAGE AND THE RUNTIME GLOBALS (from the retired dynamic-storage and globals pages, verified 2026-11-01)

- **No fixed limit a program can reach** (Lon 2026-09-23: "we must still handle almost everything without a FIXED LIMIT"; CEO-1210). One question per declaration: can a legal program make it overflow? Class A (bounded by the machine or the language: `X86_INTERNAL_MAX`, `IR_OP_COUNT`, an ISO Pascal set's 32 bytes) stays fixed and is named; class B (scratch for one value of fixed width) stays when sized from the type, and program text never passes through one; class C (a population a program grows) must be dynamic.
- **Where a population lives is decided by its lifetime** (CEO-1354): a construct's scratch on the stack; a runtime population on the GC heap as a rooted typed vector (`gv_t` in `src/runtime/core/g_runtime_vec.h`, grown by `gv_reserve` in `gc_heap.h`); a compile-time population in the compile-time arena (`src/ir/ct_arena.c`, a whack-at-end arena, Lon 2026-09-29), grown by `ct_grow` and `cv_t`/`cv_reserve` (`src/ir/ct_vec.h`) by alloc, copy and abandon (CEO-1244).
- **The one primitive is realloc** (Lon 2026-09-23: "do not do anything more fancy then a grown in place and copy and grown just like realloc does"; CEO-1211): it fits; it is the last block, so extend in place at the frontier; otherwise allocate at the frontier, copy, and leave the old block (collected on the heap, abandoned in the arena). Growth is doubling. A fixed-bucket hash rehashes at load factor 1.
- **One pass, no whack-a-mole** (CEO-1332): every class-C table converted in one sweep. The ratchet `util_dyn_caps_witness.sh census` against `harness/scripts/fixtures/dyn_caps/BASELINE` may only fall (`test_gate_dyn_caps_ratchet.sh`); `audit_fixed_caps_census.py` is the census. The only refusal is allocator exhaustion, loud, naming the table and the size.
- **Runtime globals, asked one question** (Lon 2026-10-08: "can that global live on one of the 3 ZETAS?"): C construct-lifetime state belongs in its construct's frame and the global is deleted; K a constant writable by oversight becomes `const`; S program-lifetime state lives in the one runtime state struct `g_runtime` (`src/runtime/core/g_runtime*.h`); H a chain head or single current-X cell stays (CEO-1542); T function-scope statics (cached getenv seams, once flags) are not globals. The census is `audit_runtime_globals_census.py`; a new global needs Lon's in-chat grant that session.

## 7. HOW A LANDING IS PROVED

1. Write the code to the shape: one line per item that fits, the block form for what does not; no comment, no blank line; every allocation through the arena or the collector; every datum a field of the stage struct or on a zeta.
2. Before the commit: `util_reflow_200.py --check` and `strip_comments.py --check` on every file touched; the C-allocator gate; the globals gates if a static or a struct field of runtime state was added (with Lon's grant cited in the commit message); the dyn-caps ratchet if an array bound appeared or vanished; the `_is_current` gate of any table the change feeds (regenerated before the build).
3. `make -j8` clean of warnings; `make preflight`; `test_feature_reps.sh` and the smokes of every language the file serves (all eight for shared code: `lower_common.c`, `ct_arena.c`, the runtime core).
4. Commit named files with `git commit -F -`; pull --rebase; rebuild (the freshness guard refuses a stale binary); re-run the gates started after any Makefile edit; push.
