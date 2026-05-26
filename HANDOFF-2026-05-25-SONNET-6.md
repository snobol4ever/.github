# HANDOFF — 2026-05-25 — Claude Sonnet 4.6 Session (sixth)

**one4all HEAD:** `bcbfde24`
**.github HEAD:** this file
**Gates:** smoke_prolog 0/5 (pre-existing) · smoke_icon 5/5 ✅ · GATE-PK 496/0/602 ✅

---

## FREE-2 — Status

**Architecture:** correct and intact.

**Sequence in Mode 3 (`scrip.c`):**
1. `sm_preamble` → builds SM instrs + BB graphs
2. `exec_stmt_pat_table_build(sm, &n)` — called **before** `ast_tree_free`; calls `bb_build_brokered(bb_table[bi]->entry)` for each `SM_EXEC_STMT` with BB pattern; copies `subj_name`, `has_repl`, `sm_pc` into flat `ExecStmtPat_t` table
3. `ast_tree_free` — AST gone
4. `stage2_free_bb_only(s2)` — all BB graphs freed, zero residue
5. `sm_image_init()` — JIT segment `mmap`'d
6. `SM_codegen(sm, pat_tbl, n)` — emits blobs; for `SM_EXEC_STMT` with pattern, calls `emit_exec_stmt_pat_blob(fn, subj_name, has_repl)` which bakes all args as immediates
7. `free(pat_tbl)` — table gone
8. `sm_run_with_recovery` — runs blobs. No BB, no BB table referenced
9. `stage2_free_sm_bb(s2)` — SM instrs freed

**`goto --run`:** PASSES ✅
**`pattern_replace --run`:** BROKEN — result `Xabc` instead of `aXc`

---

## Root cause of `pattern_replace --run` being broken

**The `bb_box_fn` returned by `bb_build_brokered` is non-functional.**

Confirmed by direct test: calling `exec_stmt_blob` with the built `bb_box_fn`
directly (before any free, before `sm_image_init`) causes exit code 2 (crash).
The blob itself is broken, not the argument passing.

**Hypothesis (not yet confirmed):** `bb_build_brokered` uses `bb_alloc` which
returns `mmap(PROT_READ|PROT_WRITE)` memory. `bb_seal` adds `PROT_EXEC` via
`mprotect`. But calling the blob (a function pointer into that memory) may crash
if `mprotect` has not yet fired, or if the memory is not properly executable on
this kernel without `WX` permissions. Check whether `bb_seal` is working.

**Alternative hypothesis:** `bb_build_brokered` sets up some global emitter state
(`g_flat_slot_count`, `g_flat_node_id`, `g_child_cache`) that conflicts with
state expected by `SM_codegen` which also uses the emitter. When `exec_stmt_pat_table_build`
calls `bb_build_brokered` before `SM_codegen`, it may corrupt state that
`SM_codegen` needs. Check whether calling `bb_build_brokered` AFTER `SM_codegen`
(but still before freeing BB) fixes the issue.

**What next session must investigate:**

1. Read `bb_alloc` and `bb_seal` in `src/emitter/emit_bb.c` — confirm `mprotect`
   with `PROT_EXEC` fires correctly and that the returned `bb_box_fn` is executable
2. Test: call `bb_build_brokered` AFTER `SM_codegen` (move step 2 to after step 6)
   — does `pattern_replace --run` work then?
3. If neither helps: read what `sm_image_init` sets up that `bb_build_brokered` needs
4. The table can be built after `SM_codegen` if SM instrs are still alive at that point
   (they are — freed by `stage2_free_sm_bb` after run)

**Correct order to try:**
```
sm_preamble
ast_tree_free
stage2_free_bb_only   ← BB graphs freed
sm_image_init
SM_codegen(sm, NULL, 0)   ← emit blobs for non-pattern instrs
exec_stmt_pat_table_build  ← build table (BB already freed? NO — can't)
```
Wait — BB is freed before table build. That can't work.

**The real constraint:** `bb_build_brokered` needs BB graphs alive. BB graphs must
be freed before run. So `bb_build_brokered` MUST run before `stage2_free_bb_only`.
The question is whether it can run before or after `SM_codegen`.

Try: move `exec_stmt_pat_table_build` to AFTER `SM_codegen` but BEFORE
`stage2_free_bb_only`. This keeps BB alive through codegen, then frees after:

```c
sm_image_init()
SM_codegen(sm, NULL, 0)          // no pat table yet
pat_tbl = exec_stmt_pat_table_build(sm, &n)  // BB still alive
stage2_free_bb_only(s2)          // now free BB
// patch the already-emitted SM_EXEC_STMT blobs? No — can't patch after emit
```

Problem: `SM_codegen` emits blobs. If we call it without the table, `SM_EXEC_STMT`
falls through to `emit_standard_blob(h_exec_stmt)` which reads `bb_table` at
runtime — but BB is freed. So table must be built BEFORE `SM_codegen`.

**The real fix to investigate:** why does `bb_build_brokered` produce a broken blob
before `sm_image_init`? Read `bb_alloc`:

```c
grep -n "bb_alloc\b" src/emitter/emit_bb.c
```

If `bb_alloc` uses `GC_MALLOC` (not `mmap`), the returned memory may not be
executable. `bb_seal` may do `mprotect` on it which would fail silently on
non-`mmap`'d memory. If so, fix: call `sm_image_init` BEFORE
`exec_stmt_pat_table_build`, then call `bb_build_brokered`.

**Proposed new sequence:**
```c
sm_preamble
ast_tree_free
sm_image_init()                     ← move BEFORE table build
pat_tbl = exec_stmt_pat_table_build  ← bb_alloc now has executable memory
stage2_free_bb_only                  ← BB freed
SM_codegen(sm, pat_tbl, n)
free(pat_tbl)
sm_run_with_recovery
stage2_free_sm_bb
```

This is the most likely fix. Try it first.

---

## Files changed since last handoff (one4all `bcbfde24`)

- `src/driver/scrip.c` — Mode 3 sequence: table before ast_tree_free, free BB before codegen
- (all other changes from `7b087f0f` still in place)

## Watermark
```
one4all: bcbfde24
.github: this file
GOAL: FREE-2 pattern_replace --run
NEXT: move sm_image_init before exec_stmt_pat_table_build in scrip.c Mode 3
      then test pattern_replace --run → aXc
```
