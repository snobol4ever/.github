# FINDING-2026-08-08-CLAUDE-SN46-ZK2-VAR-REF-TWO-BLOCKERS-UNPINNED-LEA-AND-LVALUE-RVALUE-SPLIT.md

**Session:** s221 — Claude Sonnet 4.6
**Goal:** GOAL-ICN-ZETA-CELLS, rung ZK-2
**Status:** Attempted IR_VAR_REF cells-arm admission; two independent blockers measured; both edits reverted; tree clean at HEAD f41f21b7.

---

## BLOCKER 1 — UNPINNED GRAPH LEA DRIFT

**Symptom:** `rung23_table_table_basic` (unpinned flat main proc) silently produced no output (rc=0) with VAR_REF admitted on the cells arm, despite census showing `armed=13 declined_nodes=0`.

**Root cause:** `bb_var_ref`'s ZD arm emits `lea rdx, FRQ(op_sa)`. For unpinned graphs (`x86_fb()` = rsp), `FRQ(op_sa)` resolves to `[rsp + op_sa + op_zdepth]` — an RSP-relative address baked at VAR_REF's alpha carve depth. Each subsequent `sub rsp, 16` carve moves RSP further down, so by the time a second VAR_REF(t) fires (at `n8` in the table test), the `lea rdx, [rsp+288]` instruction encodes a different absolute machine address than the first `lea rdx, [rsp+288]` at `n3` — because RSP has moved 80B between them (5 × K=16 carves). Both compute `[rsp+288]` but reach different absolute bytes; neither points to `t`'s frame slot.

**Concrete measurement (text asm, rung23_table_table_basic SCRIP_ICN_CELLS=1):**
- `n3_var_ref_α` (RSP = entry−32): `sub rsp,16` → RSP = entry−48; `lea rdx,[rsp+288]` → absolute entry+240 ✓
- `n8_var_ref_α` (RSP = entry−128 after n3+n4+n5+n6+n7 carves): `lea rdx,[rsp+288]` → absolute entry+160 ✗ (t's slot is at entry+240)

**Fix direction:** `x86_fb_pinned()` guard on admission — pinned graphs set `mov rbp,rsp` at proc entry so `lea rdx,[rbp+op_sa]` is depth-immune and correct at any subsequent carve depth. Added pin guard; rung23_table_basic then correctly declined VAR_REF (no pinned graphs in that proc) and output `42` correctly on the cells arm fallback.

---

## BLOCKER 2 — LVALUE/RVALUE CONSUMER SPLIT (measured in pinned graphs)

**Symptom:** `jcon_kross` (`xprint` proc, pinned `flat_gen` graph, n=28) armed 13/28 nodes with VAR_REF admitted under the pin guard, but produced truncated output — `every write(right(s2[1 to k-1], j))` generated fewer iterations than expected.

**Root cause:** `rt_subscript_var` always returns a NAMETRAP `{DT_N, slen=2, VCELL_t*}` — it is an lvalue producer by design. When the NAMETRAP lands in a ZRES cell on the FORTH spine:
- **Lvalue consumers** (`rt_assign_var` via IR_ASSIGN_VAR): handle NAMETRAP correctly via `vc->cellp` write.
- **Rvalue consumers** (`right()`, `write()` via IR_CALL_BUILTIN_ICON): expect a plain value DESCR `{DT_S, ...}`; a NAMETRAP in ZRES causes `right()` to receive the wrong type, misbehave silently.

The rvalue-extraction step is `IR_DEREF` — the node that calls `rt_deref()` to convert a NAMETRAP/VAR_REF to its value. `IR_DEREF` is **not yet admitted** on the cells arm (`zd_wl_kind` has no `icn_cells_graph` arm for it).

**All-or-nothing gate implication:** A run containing `IR_VAR_REF → IR_SUBSCRIPT → IR_DEREF` must arm atomically or decline atomically. With only IR_VAR_REF + IR_SUBSCRIPT admitted, a run that also contains IR_DEREF declines as a unit (correct — but why did 13/28 arm in xprint?). The armed 13 nodes were in runs that did NOT include IR_DEREF — e.g. pure literal+builtin chains. But those armed runs' ZRES geometry now shares the spine with the declined subscript+deref runs, and the interaction caused the output truncation. The exact mechanism: the generator `IR_TO` (armed, K=32) re-enters β non-popping; each iteration its counter cell is stable. But a declined subscript run's fc_geom slot may alias or conflict with the TO cell layout at certain graph depths — MONITOR-FIRST would be needed to pinpoint, but the fix is clear.

**Verification:** With `SCRIP_ZD_ICN_VR=0` (VAR_REF admission killswitch OFF), `jcon_kross` produces correct output. With VAR_REF admitted (pinned guard only), `jcon_kross` produces truncated output. Delta = VAR_REF admission on xprint's pinned graph.

---

## OBSERVATIONS ABOUT s220's STATED DIAGNOSIS

The s220 finding stated: "bb_subscript's ZD arm reads `ZOPQ(0, 0/8)` as `{DT_TABLE, table_ptr}` directly, but VAR_REF produces `{DT_N=1, &slot}` — the subscript template must dereference operand-0 through the DT_N indirection before calling `rt_subscript`."

This diagnosis was **incorrect about the consumer**. Verified this session:
- `c_rt_subscript_var` (pattern_match.c:1032): calls `IS_VARREF_fn(base)` + `rt_deref(base)` for any DT_N base — correct.
- `c_rt_assign_var` (pattern_match.c:1229-1230): dispatches on `DT_N, slen==1` via direct ptr-write — correct.
- `rtx_icnsub.S` (lines 200-215): gates on `DT_N && slen==1 && ptr!=0`, calls `rt_deref` — correct.

No consumer template changes are required. The actual blockers are structural (RSP-relative addressing + DEREF not armed).

---

## CORRECT NEXT STEPS FOR ZK-2

**Step 1:** Arm `IR_DEREF` on the cells arm in `zd_wl_kind`. `bb_deref.cpp` already has a complete ZD arm (reads ZOPQ(0,0/8), calls `rt_deref`, writes ZRES(0/8)). Only missing: one admission line in `zd_wl_kind` with `icn_cells_graph` guard + killswitch `SCRIP_ZD_ICN_DEREF`. K=16 default; nops=1 (already in the 1-operand arm).

**Step 2:** Re-admit `IR_VAR_REF` with BOTH guards: `x86_fb_pinned()` (prevents RSP-drift LEA) AND `icn_cells_graph`. Once IR_DEREF is in the whitelist, the run gate ensures `VAR_REF → SUBSCRIPT → DEREF` arms atomically — the partial-arm NAMETRAP hazard cannot occur.

**Step 3:** Witness suite: `rung23_table_table_basic` (lvalue path: VAR_REF→SUBSCRIPT→ASSIGN_VAR), `rung36_jcon_kross` (rvalue path: VAR_REF→SUBSCRIPT→DEREF→right()), plus fib(10) ZK-4 retention and SN4 byte-identity.

**Step 4:** Alternatively, if pinned-only VAR_REF coverage is too narrow for the census impact Lon wants from ZK-2, consider admitting `IR_DEREF` first as a standalone rung-let (its bb_deref ZD arm already exists; it unblocks `write(x)` rvalue reads for all pinned local-ref chains), then tackle VAR_REF as a second rung-let.

---

## TREE STATE AT HANDOFF

- HEAD: `f41f21b7` (ZK-2 s220 parallel walker: IR_KEYWORD_ICON admission) — unchanged.
- No new commits this session (all edits reverted; net-zero codegen delta).
- `zd_wl_kind` comment block updated: two-blocker finding documented in-source.
- `bb_var_ref.cpp`: deferred comment added in place of the reverted ZD arm.
- Build: clean. ZK-5 gate: 3/3 green. SN4 crosscheck: byte-identical. Icon suite watermarks: not re-derived (no codegen landed; prior cursor watermarks apply: baseline m3 218/45/30, CELLS=1 m3 184/79/30 with ±1 flake on rung09_loops_repeat_counter per s219 instability finding).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6
