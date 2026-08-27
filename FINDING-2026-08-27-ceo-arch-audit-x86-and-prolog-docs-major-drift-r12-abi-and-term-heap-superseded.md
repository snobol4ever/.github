# FINDING 2026-08-27 (ceo): ARCH audit 2 of 3 — ARCH-x86.md and ARCH-PROLOG.md are MAJOR DRIFT; both teach superseded substrate models as current

**Context:** same audit wave as the zeta/IR FINDING (Lon's read-the-ARCH-docs order makes doc drift actively harmful). Verified at current HEAD; templates are FLAT in `src/templates/` (no BB_templates/, no XA_templates/, no xa/ subdir); no `src/machine/`.

## ARCH-x86.md — MAJOR DRIFT

- **The load-bearing drift: the box model.** ":Boxes are stackless / have no stack" + an r12 ζ-frame ABI (`mov r12,rdi`, RW locals `[r12+off]`, "r12 callee-saved and survives"). Reality: three zetas ON the stack — ζ-SPINE=RSP (`x86_alpha_carve` = `sub rsp,K`, x86_asm.h:1752; `x86_zref`), ζ-ACTIVATION/STANDING=RBP (`zone_ref`, x86_asm.h:937/962/888); r12 is just register #12 in the encoder tables. Superseded by RULES.md § BB FRAME-PLACEMENT CRITERION and Lon 2026-08-27 (all three zetas are on the stack).
- **Self-contradiction:** the :3 prune banner lists `bb_pool` as "DELETED — none of it exists" while `src/ir/bb_pool.{c,h}` is live, referenced tree-wide, and used by the doc's own body three lines later.
- Dead paths/names: `BB_templates/`/`XA_templates/` dirs (flat now); `bb_flat.c` → `bb_glue_flat.cpp`/`xa_flat.cpp`; `SCRIP/archive/frontend/prolog/prolog_emit.c` → `one4all/archive/...`; three cross-refs to `GOAL-SNOBOL4-BB.md` (absent) → `GOAL-SNOBOL4-100.md`.
- Verified correct: one-driver emit.cpp/emit.h; flat templates + x86_asm.h encoder discipline; `--run`/`--compile` (+`--target`); `xa_dispatch`/`XA_op_t`; `bb_snapshot_state`/`bb_restore_state`; the mprotect RW→RX I-cache fence (exact, bb_pool.c:45); the corpus probe refs.

## ARCH-PROLOG.md — MAJOR DRIFT

- **The central substrate section is REVERSED by ruling:** :27-34 declares tagged heap `Term*` a "deliberate substrate choice" that "survives." Lon's s273 ruling (GOAL-PROLOG-100 head): Prolog uses **DESCR, not Term**; allocations ride SPINE→ACTIVATION→STANDING; the heap arm is struck. The doc accurately describes CURRENT code (426 `Term` refs; only pl_cell.h touches DESCR) — but presents pre-ruling code as settled design instead of as the thing being excised.
- VOID "stackless" as the model name (:5) — content survives as no-separate-operand-value-stack.
- Dead paths/symbols: `src/runtime/interp/pl_runtime.{c,h}` (dir gone; no `pl_choice` struct — only `lower_pl_choice_graph()` at lower_prolog.c:859); `g_pl_cut_barrier`/`pl_cp_truncate` zero hits (cut is TAG-2 watermark restore per PZ-3); unify/trail live in `src/runtime/unification.c` as `pl_unify`/`pl_trail_unwind`, not `prolog_unify.c:bind/trail_unwind`; `SCRIP/archive/...` → `one4all/archive/...`; five refs to absent `GOAL-PROLOG-BB.md` → `GOAL-PROLOG-100.md`.
- Verified correct: term.h path and its TermTag family (accurate to source, pending excision); bb_node_state_t snapshot/restore; four Greek ports; δ/ε abolition.

## Two premise corrections beyond the docs

- **`bb_pl_*.cpp` do not exist yet** (Prolog lowers through shared templates — consistent with GOAL-PROLOG-100's PZ-1(b) being the first code rung).
- **`sm_interp_run` does not exist in src/** — the CEO-root CLAUDE.md digest cited it as the Prolog `--run` exception; the real fallback is the mode-3 native-emitter coverage guard at `src/driver/scrip.c:1641`. Digest corrected this date. Also GOAL-PROLOG-100.md:11 cites `src/parser/prolog/term.h`; truth is `src/frontend/prolog/term.h`.

**Disposition:** worklist folded into repair row `arch-doc-repair-bundle` (rank 1); "stackless" rewording rides `stackless-eradication`.
