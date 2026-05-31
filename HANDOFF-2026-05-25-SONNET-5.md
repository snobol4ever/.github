# HANDOFF — 2026-05-25 — Claude Sonnet 4.6 Session (fifth)

**SCRIP HEAD:** `5ea638d3`
**.github HEAD:** (this file + RULES + GOAL-BB-TEMPLATE-LADDER updates)
**Gates:** smoke_prolog 5/5 ✅ · smoke_icon 5/5 ✅ · GATE-PK 496/0/602 ✅

---

## New RULE added

`RULES.md`: BB/SM deletion is total — zero residue. No shadow copies. No partial
frees. No stale indices. One free point after the last consumer. ASAN verify required.

---

## FREE-2 — Work in progress (SCRIP `5ea638d3`)

**Goal:** Delete BB and SM completely before Mode 3 execution. Blobs are self-contained.

**Architecture (correct):**
1. `exec_stmt_pat_table_build(sm, &n)` — walks SM instrs before any free.
   For each `SM_EXEC_STMT` with `a[2].i >= 0` (has BB pattern): calls
   `bb_build_brokered(bb_table[bi]->entry)` → compiles BB pattern to `bb_box_fn`.
   Copies `subj_name` (from `a[0].s`), `has_repl` (from `a[1].i`), `sm_pc` into
   flat `ExecStmtPat_t` table. Returns malloc'd array.
2. `stage2_free_bb_only(s2)` — frees all `BB_graph_t` objects. Zero residue.
3. `SM_codegen(sm, pat_tbl, pat_tbl_n)` — reads from table (NOT from BB).
   For each `SM_EXEC_STMT`: emits `emit_exec_stmt_pat_blob(fn, subj_name, has_repl)`
   — self-contained x86 blob with all args baked as immediates. Calls `exec_stmt_blob`.
4. `free(pat_tbl)` — table gone.
5. `stage2_free_sm_bb(s2)` — wait, SM instrs still needed by other blob handlers
   via `CUR_INS` at runtime... actually `stage2_free_sm_bb` called AFTER run. See below.
6. `sm_run_with_recovery` — runs blobs. No BB, no BB table referenced.
7. `stage2_free_sm_bb(s2)` — frees SM instrs after run.

**goto --run:** PASSES ✅

**pattern_replace --run:** SEGFAULTS — root cause identified:

`bb_build_brokered` calls `codegen_flat_body` which reads `pBB->sval` (the literal
string, e.g. `"b"` for pattern `'b'`) and bakes it as a raw `imm64` pointer into
the blob's machine code.

`BB_lower_pat` (called from `lower.c`) sets `nd->sval = t->v.sval` — this aliases
the **AST** string, NOT the SM instrs string. `SM_emit_s` does `strdup` so
`sm->instrs[i].a[0].s` is independent. But `nd->sval` is not.

`ast_tree_free(ast_prog)` is called at the top of Mode 3, BEFORE
`exec_stmt_pat_table_build`. So when `bb_build_brokered` reads `pBB->sval`,
the AST string is already freed → dangling pointer baked as imm64 → segfault
at runtime when the blob tries to dereference `"b"`.

**The one-line fix:**

In `bb_build_brokered` (`src/emitter/emit_bb.c`), before calling
`codegen_flat_body`, walk all nodes in the graph and `GC_strdup` any `sval`
string. OR: patch `BB_lower_pat` to `GC_strdup` strings at construction time.
Either approach makes `sval` independent of the AST.

Alternatively: move `exec_stmt_pat_table_build` to before `ast_tree_free` in
`scrip.c` — but the baked pointer still becomes dangling after `ast_tree_free`.
So the `GC_strdup` fix in `bb_build_brokered` (or `BB_lower_pat`) is required
regardless.

**Files changed (SCRIP `5ea638d3`):**
- `src/processor/sm_jit_interp.c` — `ExecStmtPat_t` struct, `exec_stmt_pat_table_build`,
  `emit_exec_stmt_pat_blob`, `SM_codegen` updated to take table
- `src/processor/sm_jit_interp.h` — updated `SM_codegen` sig, exports table type/fn
- `src/driver/scrip.c` — Mode 3: build table → free BB → codegen → free table → run → free SM
- `src/driver/scrip_sm.c` — `stage2_free_bb_only` restored (frees all BB)
- `src/driver/scrip_sm.h` — `stage2_free_bb_only` declared
- `src/driver/sync_monitor.c` — `SM_codegen(sm, NULL, 0)` call updated
- `src/runtime/rt/rt.c` — `rt_exec_stmt_pat` added (unused now but harmless)
- `src/runtime/rt/rt.h` — `rt_exec_stmt_pat` declared

**What next session must do:**

1. Fix `sval` dangling pointer — one of:
   - In `BB_lower_pat` (`src/lower/lower_pat_dcg.c`): change `nd->sval = t->v.sval`
     to `nd->sval = GC_strdup(t->v.sval ? t->v.sval : "")` everywhere.
   - Or in `bb_build_brokered` (`src/emitter/emit_bb.c`): walk `nd->all[]` before
     `codegen_flat_body` and `GC_strdup` any `sval`.
2. Verify `pattern_replace --run` → `aXc` ✅
3. Run `bash scripts/test_crosscheck_snobol4.sh` → `pattern_replace` and `goto` PASS
4. FREE-3: `SM_BB_ONCE_PROC` — same pattern (Prolog predicate BB graphs freed before run)
5. FREE-4: SM instrs freed before run (requires all blobs to not use `CUR_INS`)
6. FREE-5: ASAN clean

## Session setup for next session

```bash
cd /home/claude/SCRIP && bash scripts/build_scrip.sh
bash scripts/test_per_kind_diff.sh   # PASS=496
bash scripts/test_smoke_prolog.sh    # PASS=5
bash scripts/test_smoke_icon.sh      # PASS=5
```

## Watermark

```
SCRIP: 5ea638d3
.github: this file
GOAL: GOAL-BB-TEMPLATE-LADDER.md FREE-2
STATUS: 🔄 WIP — goto PASS, pattern_replace BROKEN (sval dangling ptr)
NEXT STEP: GC_strdup sval in BB_lower_pat or bb_build_brokered
```
