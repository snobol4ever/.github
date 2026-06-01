# HANDOFF 2026-06-01 (Opus 4.8) — SNOBOL4-BB CALLER TEARDOWN (build restored)

**Repos touched:** SCRIP (`646a543`, pushed) · .github (this commit, pushed last)
**Goal:** GOAL-SNOBOL4-BB.md (SESSION RUNG #0 SBL-PAT-BB → PB-RB ladder)

---

## What this session did

The prior session (`cc23c9f`) deleted every C byrd-box function with the forbidden
`DESCR_t f(void *ζ, int entry)` signature **and** the `bb_broker` driver, on Lon's emphatic
directive — and **accepted a broken build** ("makes NO DIFFERENCE what breaks"). This session
performed the **CALLER TEARDOWN** that was the explicit `NEXT (#1)`: gut the dangling brokered
callers so the build is green again, with the brokered execution path **removed, not preserved**.

### The 7 dangling files (all repaired) + 2 orphan headers (deleted)

| File | Dangling symbol(s) | Fix |
|------|--------------------|-----|
| `gen.h` | `FAIL_GEN_NODE = {fail_box,…}`; `#include "bb_broker.h"` | `{NULL,NULL,0}` sentinel; include `bb_box.h` |
| `gen_runtime.c` | `gen_bb_pump_proc_by_name` (built `gen_bb_dcg`/`gen_bb_oneshot`) | abort stub; include `bb_box.h` |
| `gen_runtime.h` | `#include "bb_broker.h"` | include `bb_box.h` |
| `resolve_runtime.c` | `resolve_bb_once_proc_by_name` (`resolve_bb_dcg`) + 3 brokered Prolog `--run` sites (`pl_box_choice*`/`pl_box_goal_from_ir` + `bb_broker`: user-pred ×2, findall, aggregate_all) | abort stubs; drop `pl_broker.h`+`bb_broker.h`, add `bb_box.h` |
| `resolve_runtime.h` | `#include "bb_broker.h"` | include `bb_box.h` |
| `interp_hooks.c` | brokered Prolog call (`pl_box_choice*`+`bb_broker`) | abort stub |
| `stmt_exec.c` | `exec_stmt_blob` brokered pattern scan (`bb_broker bb_scan`) | abort stub; drop `bb_broker.h` |
| `scrip.c`, `interp_private.h` | `#include …/pl_broker.h` | dropped |
| **`src/frontend/prolog/pl_broker.h`**, **`src/processor/bb_broker.h`** | orphaned (their `.c` gone in cc23c9f) | `git rm` |

**Key correctness point — `bb_node_t` is KEPT.** The struct `{ bb_box_fn fn; void *ζ; size_t ζ_size; }`
(its real home is `bb_box.h`) is NOT the forbidden thing — only the `(ζ,int entry)` box **functions**
and the `bb_broker` **driver** were abolished. Removing `bb_broker.h` had been pulling in `bb_box.h`
transitively; repointing the includes directly at `bb_box.h` restores the `bb_node_t` type the
(now-dead, aborting) interpreter state structs still mention. Those 38 remaining `bb_node_t`
references compile but are unreachable on the live mode-2/3 paths and fall away with the dead
interpreter paths later.

### Gates (all green; matching/exceeding the watermark)

```
make scrip                  rc=0
make libscrip_rt            rc=0
test_smoke_snobol4.sh       m2 7/7 HARD · m3 5/6 · m4 0/6   (m4 0/6 = PRE-EXISTING by-design
                                                             sno_ring_to_tree-removed abort,
                                                             NOT this teardown)
test_smoke_icon.sh          m2 11/11 HARD · m3 11/11 · m4 9/11  (proc_* m4 fails pre-existing)
prove_lower2.sh             64/0 topology
test_gate_sm_dead.sh        0  (≤1)
g_vstack                    0
audit_concurrency_invariants.sh  OK
```

COMPLETION TEST (a) of the NO-C-BYRD-BOX FACT RULE re-verified: the `(ζ,int entry)` box grep
returns **zero**. Byte-neutral to Icon (only the brokered path + its includes were touched).

---

## NEXT (#1): PB-RB-1 EMIT ARM

**The LOWERING is already done** (`6343198`): `lower2_pat_build_entry` (lower.c:2183) lowers a
`TT_QLIT` pattern → ONE `IR_REF_INVARIANT` box over a sealed `IR_PAT_LIT` element (sealed element
carried in `operand_aux` per PEERS RULE, referenced not threaded; bounded single-shot β=ω_in).
prove_lower2 64/0 already covers its 2-node REFINV topology.

**What remains = the emit arm + a mode-3 probe:**

1. **`bb_ref_invariant.cpp`** — replace the dormant fail-loud stub (TEXT `bomb_text` / BINARY
   `abort`) with real BINARY + TEXT arms: load the sealed `IR_PAT_LIT` `bb_box_fn` **head** (the
   child-cache fn ptr — an **emit-time constant**: `movabs` imm64 in BINARY / `[rip+disp]` `lea`
   in TEXT, RO, never on a stack) into a ζ-frame RW slot `[ζ=r12+off]`, then `jmp γ`; β = `jmp ω`
   (bounded single-shot, Fork A/E — **no runtime construction**). Model: `bb_sno_subject.cpp`.
2. **`emit_bb.c`** — add `flat_drive_sno_ref_invariant`: pre-build the sealed `IR_PAT_LIT` child
   via `bb_build_brokered(ch)` (resolve `ch` from `bb_operand_aux_get`, **not** `bb_pat_kid`),
   `child_cache_put` its head (+ `child_cache_set_lbl` for TEXT), set `g_emit.bb_child_*`, alloc
   the ζ-slot via `bb_slot_alloc(nd)`, emit the box. Add the `walk_bb_flat` `IR_REF_INVARIANT`
   case + `pre_build_children` / `pre_build_children_text` recognition (mirror the
   `IR_PAT_ARBNO`/`ASSIGN_COND`/`ASSIGN_IMM` arm).
3. **`emit_core.c`** — dispatch **already wired** (emit_core.c:415 `IR_REF_INVARIANT` →
   `bb_ref_invariant`).
4. **mode-3 `S 'b'` probe** — JIT a `SUBJECT('abc')` → `REF_INVARIANT('b')` → `SUCCEED` chain
   (model the PB-0/PB-1 `sno_flat_chain_build` probes), run with `rt_frame`, disasm-confirm the
   `'b'` literal-matcher head lands in the ζ-slot, stackless (ζ=r12), no value stack.

**Precedent:** ARBNO/capture child-emit at `emit_bb.c:1787-1815` (`bb_build_brokered(ch)` →
`child_cache_put`). The sealed element is the EXISTING `bb_lit.cpp` four-port matcher
(emit_core.c:384 `IR_PAT_LIT` → `bb_lit`; reads `[r10]`=δ, compares lit bytes vs Σ+δ, advances δ
→ γ else ω).

**Do NOT regress mode-2** — the `IR_SCAN` super-node stays intact (native chain is modes-3/4);
`IR_SCAN` retirement is the later PB-RB-CONV step.

Then the rest of the PB-RB ladder: PB-RB-2 (matcher four-port ABI) → PB-RB-3 (BB_MATCH driver) →
PB-RB-4 (STITCH_SEQ/STITCH_ALT) → PB-RB-5/6 (variant elements + structural BB_PAT_BUILD) →
PB-RB-7 (replacement/substitution) → PB-RB-CONV/8/OPT.

---

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
