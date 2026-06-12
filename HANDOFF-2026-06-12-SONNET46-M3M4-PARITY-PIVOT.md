# HANDOFF-2026-06-12-SONNET46-M3M4-PARITY-PIVOT.md

**Session:** 2026-06-12 · Claude Sonnet 4.6
**Goal:** GOAL-ICON-FULL-PASS — M3/M4 parity pivot
**HEAD (SCRIP):** `99e96e9`
**m2:** 200/247 (unchanged) · **m3:** 39 (+1) · **m4:** 39 (+1)

---

## Pivot rationale

Lon directed: get m3/m4 at parity with m2. Starting state: m3=38, m4=38 vs m2=200. 95 m3 FAILs are not excised — they enter the native emitter and produce silent empty output.

---

## Work done

### 1. Root cause diagnosis of silent-empty m3 failures

Traced `rung01_paper_lt` (`every write(2 < (1 to 4))`):
- m3 produces empty, m2 produces "3\n4\n".
- `icn_graph_native_emittable_mode` returns 1 (IS admitted). No SMX. Program enters native path.
- `icn_ring_to_tree` returns NULL (chain has IR_BINOP, IR_LIT_I) → falls to `descr_flat_chain_build(bbg->entry)`.

**Bug 1 — flat_drive_call_intexpr** (`src/emitter/emit_bb.c`): when `dval==1.0` (single-arg write), it skipped `walk_bb_flat(a0)` entirely. So the BINOP+TO arg subtree was never walked, never got slots allocated, never got emitted. The write box then read from an uninitialized or wrong slot. **Fix:** always walk `a0` when `g_descr_flat_chain`. Introduced `need_walk = (IR_LIT(pBB).dval != 1.0) || g_descr_flat_chain`.

**Bug 2 — bb_binop_relop** (`src/emitter/BB_templates/bb_binop_relop.cpp`): relop box compared `op_sa+8` vs `op_sb+8` and jumped to γ on success — but never stored the result `y` to `op_off`. Icon relop returns `y` (right operand) per `ocomp.r` (`return C_integer y`). **Fix:** after passing the comparison, copy `op_sb` tag+value to `op_off` using rcx (not rax, to avoid clobbering the cmp result).

Both committed in `99e96e9`.

### 2. Remaining gap: rung01_paper_lt still fails after both fixes

The generated asm is now structurally correct:
- LIT_I(2) → slot 0/8; LIT_I(1) → 16/24; LIT_I(4) → 32/40
- TO: cursor@64, lo=slot16, hi=slot32, result→48/56
- BINOP relop: cmp [r12+8] vs [r12+56], on pass copies slot48→72 and slot56→80
- CALL write: reads rdi=[r12+72], rsi=[r12+80], calls `rt_write_any_nl`, jmp→TO.β retry

Yet m3/m4 produce empty output. The problem is NOT in the templates or slot wiring (verified by inspecting asm). Likely in how `descr_flat_chain_build` vs `bb_build_flat` sets up the execution context, or in the `(void)fn(rt_frame(), 0)` calling convention for this graph shape. **Not found this session.**

---

## Next session priorities

1. **Find the rung01_paper_lt silent-fail.** Add `fprintf(stderr,"[DBG]...")` to `rt_write_any_nl` or run under gdb on the --run blob to find where control is lost. Hypothesis: `bb_build_flat` path (for `icn_root != NULL`) vs `descr_flat_chain_build(bbg->entry)` — check which one actually executes and whether the binary blob encoding matches the text asm. Alternative: frame size, callee-save clobber (r12 restored at wrong point by inner call).

2. Once that class is fixed, the rc=124 timeouts (infinite retry loop) and rc=134 aborts (x86_bomb stubs) will surface as the next tier.

---

## State invariants (all hold at HEAD 99e96e9)

- m2 icon smoke 12/12 HARD ✅
- m2 prolog smoke 5/5 HARD ✅
- one-box gate PASS ✅
- No value stack, no C byrd-box functions, no bb_bin_t ✅
- Build green ✅

---

## Authors
Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
