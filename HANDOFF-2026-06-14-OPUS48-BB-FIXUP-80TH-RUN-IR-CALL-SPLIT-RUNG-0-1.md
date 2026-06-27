# HANDOFF — 80th attended run (Opus 4.8) — IR_CALL split Rungs 0 + 1

**Goal:** GOAL-BB-FIXUP-A-to-Z (snobol4ever/SCRIP). **Cursor:** `bb_call.cpp` (STAYS). **SCRIP origin tip:** `2fd0755`.

## Headline
The **IR_CALL split has begun** — the 79th run's "NEXT PIECE" (retiring the `dval==3.0` overload: staged-proc / by-name / userproc / builtin). Two dormant, byte-identical prep rungs landed; the producer flip is **deliberately not started** (architecture-scale, full-budget — per the 79th directive). The two unknowns that blocked the flip are now resolved with code evidence, reducing it to mechanical execution.

| commit | what |
|---|---|
| `842e22c` | **Rung 0** — four dormant IR kinds `IR_CALL_PROC_STAGED/USERPROC/BYNAME/BUILTIN` at the `IR_e` tail (after `IR_CALL_DEFINE`, before `IR_OP_COUNT` → nothing renumbers); `ir_is_call_kind()` inline beside `ir_is_scan_kind()`; `kind_names[]` (scrip_ir.c, designated-init) registers all four. Zero producers/consumers → byte-identical by construction. |
| `2fd0755` | **Rung 1** — recognition at the three primary emit-path dispatch consumers (the first to see the pass's output), as fallthrough case labels mirroring `IR_SCAN_*`: `emit_core.c` `walk_bb_node` (→ `bb_call()`), `emit_bb.c` `arg_entry_terminal`, `emit_bb.c` `walk_bb_flat` prepare. Still zero producers → dormant → byte-identical. |

Both commits rebased clean over concurrent Prolog work (`842e22c` over `ae2dd38` rung11; `2fd0755` over `89e8dd0` rung30); **each merged tree was rebuilt + re-gated GREEN** — no broken commits on origin.

## Why the flip was not started
A dormant rung's only proof is byte-identity — there is **no behavioral check until the producer flip fires**. The flip's consumer set is large and entangled (operand-position calls are in scope — see below), so hand-stamping 15+ sites in a half-spent window would be an unprovable half-state, exactly what the 79th handoff forbids. The three dispatch sites were the safe, mechanical, high-priority subset.

## Design resolved this run (the flip is now mechanical)
1. **Pass is EMIT-ONLY → interp out of scope.** The mode-2 `--run` arm (scrip.c ~2680–2737) calls `IR_interp_once` directly and **never runs `rt_proc_register`** — the proc table is empty in mode-2. So the resolve pass lives only in the mode-3/4 register sites; the mode-2 oracle keeps seeing plain `IR_CALL`, and `IR_interp.c` needs no changes. (A reduction vs. scan, which retagged at lower = all-mode.) Place the pass at the register sites, **after** the emittability guard (~2369) so the guard stays on `IR_CALL`.
2. **Scope mechanism: `dval==3.0` includes operand calls.** `lower_icon.c` (line 83–84) stages a call via `lc_call_argblks(call, …3.0…)` for any "subgraph" call (one carrying arg-blocks). Verified with `--dump-bb` on `x := f(4) + 5`: node `[6]` is the operand `f`, node `[8]` is the top-level `f`, **both** plain `CALL` at lower output. So the resolve pass **will** retag operand calls → the operand-classification consumers are in scope.
3. **Stamp strategy: keep `dval`+`sval`, change `op` only** (the scan technique). `IR_CALL_*` nodes then near-alias `IR_CALL`+`dval==3.0`; consumers need only their **op-check** widened, and their inner `dval` logic keeps working. Completeness is **gate-verified at flip time**: a missed consumer leaves a node failing its `op==IR_CALL` check → falls through dispatch → output shift → gate break (the same self-verification scan got from deleting its `emit_core` safety-net).

## The flip recipe — dedicated full-budget NEXT session
1. **One** shared `resolve_call_kinds(IR_graph_t *g)` called from the ~5 register sites (scrip.c ~2403/2593/2615/2771/2894). For each call node, stamp `op = IR_CALL_*` **only when `dval==3.0`**, using `bb_call_route_classify`'s logic restricted to `dval==3.0` + chain context. **Route alone is insufficient:** `CALL_ROUTE_BYNAME` is reached from `dval==2.0` *and* `dval==3.0`; `CALL_ROUTE_FN`/`USERPROC` aren't dval-gated. Gate on `dval==3.0`, not route.
2. **Widen/normalize the operand-classification consumers.** Cleaner to normalize call-kinds→`IR_CALL` at the **~8 set-sites** (`emit_bb.c` 1159/1160/1167/1168/2884/2885/2904/2905/3056 + `emit_core.c` 396, all `g_emit.bb_lk/bb_rk/op_a_node_kind = child->op`) than to widen the **~10 `==IR_CALL` check-sites** (`bb_binop_gvar_arith_slot`, `bb_binop_gvar_relop`, `bb_unop_gvar_slot`, `bb_gvar_assign` + `emit_bb.c` 1144/2590/2804/2912/3367).
3. **Cleanup rung** (scan RUNG-F analog): convert consumer `dval`-reads → kind-reads to actually **retire** the `dval==3.0` overload.
- **Proof obligation:** staged-proc m3/m4 programs — *exercised*, not excise-blind unlike scan — byte-identical / PASS pre + post each rung.

## Proof (both rungs, and post each rebase)
sno m4 7/7 HARD · icon m2 12/12 HARD, m3/m4 12/12 · prolog m2 5/5 HARD, m3/m4 5/5 · emit-blind 0 strict · bin_t 0 · vstack 3 · sno_pat_reg HARD.

## Verdicts
- **Resolved this run:** the 79th "NEXT PIECE" registry-timing-wall design — placement (emit-only / interp-out), scope (`dval==3.0`, operands included), stamp strategy (keep `dval`+`sval`) — all pinned with code evidence; Rungs 0 + 1 landed.
- **No LADDER rungs closed** — FIX-3 staged-half remains open at the flip.
- **Carried (standing set):** m2 disj-backtrack (PROLOG-BB) · prove_lower VACUOUS ratify (IR-REDESIGN) · pK m4 silent-empty · brokered-catch m3/m4 silent · str-relop m3-empty (ICON-BB) · gvar-relop box ungated · rank rp/cv9/cv10 · ceiling-recompute · LANGUAGE-BLIND audit · Makefile header-dep gap · scan m3/m4 84% LOUD-EXCISE (ICON-BB) · tab(nested-scan-call) coverage (ICON-BB).
- **NO-GROWTH CEILING:** not recomputed (rank audit not run; +13 lines additive across IR.h/scrip_ir.c/emit_core.c/emit_bb.c — all dormant). Recompute GRAND next session.

## Env
`install_system_packages.sh` (libgc-dev) → `make -j4 scrip` → `make libscrip_rt`. **Corpus absent by default** — clone `snobol4ever/corpus` to `/home/claude/corpus`. `make clean && make` after any header edit (IR.h; Makefile header-dep gap). Baseline GREEN before first edit.
