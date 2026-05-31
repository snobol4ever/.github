# GOAL-LOWER-MERGE.md — Unify lower/*.c into one lower.c

**Repo:** one4all + .github
**Sister:** GOAL-LANG-INDEPENDENT-RENAME.md · GOAL-SNOBOL4-BB.md
**Carved:** 2026-05-30 (Lon directive)

---

## The directive

Merge all `src/lower/*.c` source files into a single consolidated `lower.c`. No scattered split files. One file, consolidated functions, logical ordering. The current split (`lower_graph.c` / `lower_clause.c` / `lower_ctx.c` / `lower_pat_dcg.c`) is historical artifact — collapse it.

**Files to merge into `lower.c`:**

| File | Lines | Content |
|------|-------|---------|
| `lower.c` | 371 | Entry point `lower()`, proc-skeleton dispatch, Raku prescan helpers |
| `lower_graph.c` | 2153 | Icon/generator BB lowering — `lower_gen_proc_body`, all `gen_bb_*` builders |
| `lower_clause.c` | 793 | Prolog predicate BB lowering — `resolve_*` functions |
| `lower_ctx.c` | 37 | `expression_scope_walk`, `kw_canonicalize` |
| `lower_pat_dcg.c` | 821 | SNOBOL4 pattern DCG lowering — `BB_lower_pat`, `build_node`, `build_patnd` |
| **Total** | **~4175** | All lowering logic in one file |

**NOT merged (keep as separate files):**
- `lower_sno.c` — SNOBOL4→SNOBOL4 source transpiler (`--dump-sno`), SCT goal, different concern
- `bb_exec.c` — oracle/interpreter, not a lowering pass
- `scrip_ir.c` — IR allocation helpers, keep as support module
- `sm_prog.c` — stage2 lifecycle, keep as support module
- `ast_clone.c` — AST utility, keep separate

**Header consolidation:** `lower_graph.h`, `lower_clause.h`, `lower_ctx.h`, `lower_pat_dcg.h` — their public declarations fold into `lower.h`. Delete the individual headers after merge; update all `#include` sites.

---

## Rules during merge

1. **No behavioral change.** This is a pure structural consolidation — no logic edits, no renames, no algorithm changes. If a function is wrong before the merge, it stays wrong after. Fix bugs in separate commits.
2. **One `#include` set at the top of `lower.c`.** Merge all `#include` directives from all files; deduplicate. No per-section `#include` blocks.
3. **Section separators.** Use `/*===*/` (200 chars) between major logical sections (one per merged file). Use `/*---*/` between functions within a section.
4. **Logical ordering:** entry point first, then: Icon lowering, Prolog lowering, SNOBOL4 pattern lowering, shared context helpers.
5. **200-char line max, no blank lines** (RULES.md).
6. **Gate after each file merged** — build green + Icon m2 hello passes before merging the next file.

---

## Steps

- [ ] **LM-1 — merge `lower_ctx.c` (37 lines, smallest first).**
  Append `lower_ctx.c` body into `lower.c` under a `/*===*/` separator.
  Move `lower_ctx.h` public decls into `lower.h`. Delete `lower_ctx.h` and `lower_ctx.c`.
  Update `#include "lower_ctx.h"` → `#include "lower.h"` at every site.
  Update Makefile and `build_scrip.sh` source lists.
  Gate: `make scrip` rc=0, `make libscrip_rt` rc=0, Icon m2 hello ✅.

- [ ] **LM-2 — merge `lower_clause.c` (793 lines — Prolog).**
  Same pattern: append body, fold header, delete files, update includes + Makefile.
  Gate as above.

- [ ] **LM-3 — merge `lower_pat_dcg.c` (821 lines — SNOBOL4 pattern).**
  Same pattern.
  Gate as above.

- [ ] **LM-4 — merge `lower_graph.c` (2153 lines — Icon/generator, largest).**
  Same pattern.
  Gate: `make scrip` rc=0, `make libscrip_rt` rc=0, Icon m2 hello ✅, sm_dead 1/1, FACT 0.

- [ ] **LM-5 — final cleanup.**
  Verify no stale `lower_graph.h`, `lower_clause.h`, `lower_ctx.h`, `lower_pat_dcg.h` remain anywhere.
  Verify `lower.h` has all needed declarations.
  Run full gate: make scrip + libscrip_rt + sm_dead + audit GATE OK + Icon m2 hello.
  Commit: `LOWER-MERGE: all lower/*.c consolidated into lower.c`.

---

## Session State

```
HEAD one4all  = df3551a7
Status        = NOT STARTED
Gate          = make scrip rc=0, make libscrip_rt rc=0, Icon m2 hello ✅, sm_dead 1/1, FACT 0, audit GATE OK
```
