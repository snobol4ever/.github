# HANDOFF — 2026-05-17b — GOAL-ICON-BB-JCON — IJ-IRALLOC-OVERFLOW

## Commit
one4all `6ddb9584` pushed to main.

## What landed
**IJ-IRALLOC-OVERFLOW** — single construct, clean gates.

Root cause: `lower_icn_proc_body` called `IR_alloc(128, IR_LANG_ICN)`. Programs with complex
lowered IR (e.g. `every write(3.0 < (2.5 | 3.5 | 4.5))`) need more than 128 IR nodes. The
unbounded `cfg->all[cfg->n++] = nd` write in `IR_node_alloc` stomped adjacent heap, corrupting
sibling IR_t nodes' `c`/`n` fields. Manifested as infinite loops under `--ir-run` and `--sm-run`.

Four changes in one commit:
| File | Change |
|---|---|
| `src/include/IR.h` | Added `int max` field to `IR_block_t` |
| `src/lower/scrip_ir.c` | Set `cfg->max = max_nodes` in `IR_alloc`; `if (cfg->n >= cfg->max) return NULL` in `IR_node_alloc` |
| `src/lower/lower_icn.c` | `IR_alloc(128 → 4096)` in `lower_icn_proc_body` |
| `src/lower/ir_exec.c` | Missing `return nd->ω` in `IR_ICN_BINOP` β outer loop when `right.α` also fails after `left` advances |

## Gates
```
ir-run:  126/265   (unchanged — rung18/rung36 exit cleanly now, still xfail for output mismatch)
honest:  276/0/0   (+4 from 272)
smoke:   5/5
broker:  19/49     (+2 from 17)
```

## NEXT step
**IR_BINOP_GEN real-typed arithmetic** — rung18/rung36 now exit without hanging; they produce
empty output instead of correct output. `binop_map[]` in `IR_BINOP_GEN` executor handles
int+int but the relop retry for real-typed operands needs `icn_binop_apply` wired through
correctly. Should flip rung18_real_relop_real_relop_goal and several rung36 reals.

Also candidate: re-test `rung36_jcon_*` family now that alloc overflow is fixed — some may
pass without further code changes.

## Session notes
- Diagnosis took most of the session: initial hypothesis (SM recursion via proc_table_call)
  was wrong; ir_body WAS populated. Debug prints changed heap layout and masked the bug.
  Confirmed via IR_SEQ debug print that forced a dereference, changing behavior. Classic
  heap-corruption-via-overflow pattern.
- The `ir_exec.c` beta-outer missing return was a separate latent bug found during analysis,
  bundled into the same commit since it's in the same area and was confirmed safe.
- Context at handoff: ~75%. One construct landed. No corpus changes.

## Addendum — post-push finding

rung18 (`every write(3.0 < (2.5 | 3.5 | 4.5))`) still hangs under `--ir-run` after the IJ-IRALLOC-OVERFLOW commit. The 4096 alloc is in place and verified. During session the hang disappeared only when a debug `fprintf` was present in IR_SEQ — classic heap-corruption-masked-by-debug. Another `IR_alloc(N)` call with a small cap is overflowing during lowering of the real-typed alternate/relop subtree and corrupting the IR_EVERY node. Not yet identified.

**Next session start:** add overflow debug to `IR_node_alloc` (print when `cfg->n >= cfg->max`), run rung18, find which cfg overflows, fix that caller. Then proceed to IR_BINOP_GEN real-typed arithmetic. Must land ≥2 constructs.
