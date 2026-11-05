---
name: scrip-c-code
description: Hand-written C under SCRIP/src (.c, .h, .inc): the 200-column rule, no comments or blank lines, no malloc, no new global without Lon's grant, no fixed limits, generated tables regenerated never edited. REQUIRED by the skill gate before any edit of them.
---

# SCRIP C code

Every hand-written `.c`, `.h` and `.inc` under `SCRIP/src/` (the bison/flex parsers and generated tables excepted) follows one shape and a set of prohibitions Lon ruled on verbatim. The law is RULES.md (C code style, CEO-1565; the malloc FACT RULE, CEO-832/842; NO NEW GLOBAL VARIABLES; THE LENGTH IS CARRIED; NO `-O2`; NO FIXED LIMITS) and `reference.md` § 6 (dynamic storage, the runtime globals). Lon's verbatim words, the full gate list and receipts are in `reference.md` beside this file.

## 1. THE RULES

- **The 200-column hierarchy rule** (CEO-1565): an item (a statement, or a block with its else-chain) that fits goes on ONE line of at most 200 bytes; one that does not fit opens on its own line, each child on its own line one level deeper, by the same rule. `.cpp` and `src/templates/` are line-oriented instead.
- **Zero comments, zero blank lines:** the only comment is the 200-character separator between functions. What a comment would say goes in the ARCH page or GOAL cursor. A truncated separator swallows the next function.
- **No `malloc`, `calloc`, `realloc`, `free` anywhere, under any spelling** (Lon 2026-09-17): run-time values on the collected heap (`rtx_alloc.s`), compile-time populations in the arena (`ct_alloc`, `ct_zalloc`, `ct_grow`, `ct_strdup`, `ct_drop`).
- **No new global without Lon's in-chat grant that session:** state rides registers, a zeta, or a field of the stage struct (`g_lower`, `g_planner`, `g_emit`, the runtime's `g_*`); runtime-state fields need the grant too.
- **No fixed limit a program can reach:** a growable `cv_t` or arena table; the fixed-caps population only falls (`test_gate_dyn_caps_ratchet.sh`).
- **No `-O2`, ever:** `RT_OPT ?= -O0 -g -fno-strict-aliasing -fwrapv -fno-omit-frame-pointer`.
- **The length is carried, never measured:** a DESCR's `slen`, never `strlen` on `.s` (NUL is a valid character).
- **Generated tables are regenerated, never edited** (`box_cell_shapes.inc`, `rt_entry_table.inc`, `gc_allocating_table.inc`, `builtin_table.inc`), before `make`.
- **One kind of thing per field; no language name past the driver** (CEO-1838/1840).

## 2. THE FILES

- `SCRIP/src/`: `driver/`, `parsers/` (exempt), `lower/`, `ir/` (`ct_arena.c/.h`), `planner/`, `emitter/` (`emit.cpp` line-oriented; its `.h` files under the rule), `runtime/`, `templates/` (line-oriented).
- Checkers in `harness/scripts/`: `util_reflow_200.py --check|--apply|--proof PATH...`, `strip_comments.py --check`, `audit_fixed_caps_census.py`, `audit_runtime_globals_census.py`.
- Gates: `test_gate_c_allocators_are_eradicated_and_say_where_they_went.sh`, `test_gate_dyn_caps_ratchet.sh`, `test_gate_no_new_function_scope_static.sh`, `test_gate_globals_census_counts_writable_sections_only.sh`, `test_gate_ir_field_discipline.sh`, `test_gate_emit_no_lang.sh`.

## 3. WORKED EXAMPLES

A function that fits is one line under the separator, `lower_common.c`:

```c
/*----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------*/
IR_t * lc_build(IR_graph_t * g, IR_e op, IR_t * γ, IR_t * ω) { IR_t * nd = IR_node_alloc(g, op); lc_γ_to(nd, γ); lc_ω_to(nd, ω); return nd; }
```

A block that overflowed opens on its own line; each child that fits is one line:

```c
    for (int i = 0; i < g_lower.lc.bb_src.n; i++) {
        const IR_t * k = g_lower.lc.bb_src.nd[i];
        while (t[h].k && t[h].k != k) h = (h + 1) & (size_t)(cap - 1);
        if (!t[h].k) { t[h].k = k; t[h].v = i; }
    }
```

The arena, `ct_arena.h`:

```c
void *ct_alloc(size_t n);
void *ct_zalloc(size_t n, size_t sz);
void *ct_grow(void *p, size_t n);
void ct_drop(void *p);
```

## 4. THE PROVING INSTRUMENTS

On every file touched: `python3 harness/scripts/util_reflow_200.py --check <paths>` and `strip_comments.py --check <paths>`; the ratchets the diff's area owns (dyn-caps, the C-allocator gate, the globals gates, any `_is_current` gate); `make -j8` with no warnings. `make preflight` is cheap but not the per-push check (CEO-1316).

## 5. THE FORBIDDEN FORMS

A line over 200 bytes; a blank line; any comment but the separator; two children on one line when their parent overflowed; any allocator spelling (`strdup`, `asprintf`, `getline`, a wrapper, an alias); a mutable `static` or exported cell without the grant cited in the commit; `char buf[256]` or `#define MAX_* 1024` a program can exceed; `-O1`/`-O2`/`-O3`; `strlen` on a DESCR; a hand-edited generated table; a field holding two kinds of value; a language name past the driver; a C function entering a box (CEO-1576); `#if 0`.

## 6. WHERE THE REST LIVES

RULES.md (grep: C code style, malloc FACT RULE, NO NEW GLOBAL, THE LENGTH IS CARRIED); `reference.md` § 6 (dynamic storage, the fixed-caps ratchet, the runtime globals and their classes); skill `gc-collector` (the collector's view of a root); skill `scrip-memory-model` (the lifetime rule's homes).

## 7. HOW A LANDING IS PROVED

1. Write to the shape: one line per item that fits, the block form otherwise; no comment; allocation through the arena or the collector; state in the stage struct or on a zeta.
2. Before the commit: the reflow and comment checks on every file touched; the allocator gate; the globals gates (grant cited) if a static or runtime field appeared; the dyn-caps ratchet if a bound changed; regenerate any table the change feeds.
3. `make -j8` clean; `test_feature_reps.sh` and the smokes of every language the file serves (all eight for shared code).
4. Commit named files with `git commit -F -`; pull --rebase; rebuild; push.

## THE CODE LAW IN ONE LINE (moved from CLAUDE.md 2026-11-05, Lon: all knowledge in skills)

200 columns, zero comments, zero blank lines; no symlinks, no `malloc`, no `-O2`, no fixed limits and no delimiter-joined aggregates (a list is a table, never a string with separators); declared sizes (`-d`, `-s`, `heap_kb`, `stack_kb`) are hard caps, never grown behind the user; generated tables (`gc_allocating_table.inc`, `box_cell_shapes.inc`, the rtx clobber table, the parsers) are regenerated by their generator, never edited; no new global without Lon's grant (STATE-GLOBAL, CTO-501: state lives in `g_runtime`, `g_lower`, `g_stage2`); no subagents in the repos; `util_reflow_200.py --check` and `strip_comments.py --check` per C file before a landing.
