# HANDOFF 2026-06-15 — Icon native `IR_CASE` (case-of) — ✅ **LANDED** (Claude)

**Goal:** GOAL-ICON-FULL-PASS — native `case` expression for `rung33_case_*` (the watermark's named priority: "rc=139 IR_CASE native template").
**Result:** **LANDED & PUSHED.** `rung33` is **5/5 in m3 AND m4** (was 0 PASS / 5 EXCISED). SCRIP HEAD = **`176ecda`** (rebased clean over a concurrent landing `476af37` and re-gated).

This supersedes `HANDOFF-2026-06-15-CLAUDE-ICON-BB-CASE-NATIVE-WIP.md` (the prior WIP patch). The WIP's empty-output bug is fully resolved; its "two `walk_bb_node`" theory was a red herring — the real causes are below. The `wip-icon-case-native.patch` was applied via `git apply --3way` onto current HEAD as the starting scaffold, then fixed.

---

## Tally

m3 **122 → 127** (+5) · m4 **122 → 127** (+5) · FAIL **25** (unchanged, identical m3/m4) · XFAIL 36 · EXCISED 100 → 95. The five `rung33_case_*` moved EXCISED → PASS; the 25-program FAIL set is byte-identical to baseline (verified by explicit FAIL-list diff — PASS +5, EXCISED −5, FAIL +0). icon smoke 12/12 m3+m4 · prolog smoke 5/5 m3+m4 · no-stack 0 · one-reg-frame 0 · FACT 0.

---

## The six coordinated fixes (10 files)

The prior WIP built and ran but printed **empty values**, and several bugs only surfaced in m4 (the binary m3 emitter silently tolerates duplicate labels — last-wins; GAS `as` rejects them). Each fix below was confirmed empirically by IR/asm inspection, not from the stale handoff.

1. **`descr_chain_arity` (emit_bb.c)** — added `case IR_CASE: return 0;`. Without it `IR_CASE` fell to `default:-1`, so when `write(case…)` adopted operands, the consumer CALL hit `if (ar < 0) { sp = 0; continue; }` and **reset its operand stack** → `write` got `n_operands=0` → empty output. Exact same bug class as the prior SECTION/LIST_BANG fix. This alone made the literal-valued cases (`int`/`str`/`in_proc`) PASS.

2. **`lower_icon.c` `TT_CASE`** — the arm builds pushed the **entry** node (`ve`/`ke`/`de`, the value returned by `lower()`), but the slot read needs the **result** node (`*res` = `vn`/`kn`/`dr`). For a literal entry==result so it worked; for `1*10` the entry is the *left literal* `1` (head of the eval chain) while the result is the `BINOP`. Changed all three pushes (default value, key, arm value) to the result — mirroring how the **selector** already used `sr` on the line above. Fixed `1*10` storing `1`.

3. **`case_slot_binop_operands()` (emit_bb.c, new static helper)** — a binop's operands live in the **`operand_aux` sidecar** (PEERS rule; `lower_icon.c` line ~134 `bb_operand_aux_set`), NOT in `operands[]`. `descr_chain_operand_refs` only binds `operands[]` for binops that sit in the *main* producer chain; an isolated arm-value binop is reached via `operands[]` of the arm (not γ/ω), so it's never visited → `operands[]` empty → `bb_child0/1` NULL. The helper (a) hydrates `operands[]` from `operand_aux` exactly like the gvar path at emit_bb.c ~2835, then (b) pre-walks the operands so they emit as slotted producer boxes (mirroring `flat_drive_section`). Then `walk_bb_flat(binop)`'s descr arm finds both operand slots ≥0 and allocates its result slot. Called before key/value/default walks in `flat_drive_case`. Fixed `1*10` → bomb → `10`.

4. **`scrip.c` `rhs_kind_ok`** — added `if (r->op == IR_CASE) return 1;`. `write(case…)` works (CASE as a CALL arg) but `x := case…` declined because `IR_CASE` wasn't an admissible **local-assign RHS** kind. Fixed `rung33_case_case_no_default` (EXCISE → PASS). (Mirrors IR_FIELD_GET/IR_GATHER entries.)

5. **`bb_case_arm.cpp`** — removed the redundant `x86("label", _.lbl_α)` from **both** arms. The arm node is filled twice (compare box + take box), and `bb_fill_alpha` derives the α label from the node id → the same `bb<id>_α` label emitted twice → m4 `as` "symbol already defined". The boxes are entered via the driver's explicit labels (`key_done` / `take` / `val_done` fall-through), never via their own α, so the label was pure decoration.

6. **`flat_drive_case` (emit_bb.c)** — two structural fixes:
   - **Stop re-walking the selector.** The selector is the chain node *immediately preceding* the CASE (it's the chain entry; selector.γ → CASE), already emitted & slotted by `codegen_flat_chain_body`. `flat_drive_case` was re-walking it → the selector box emitted **twice** with identical labels (`bb<id>_α`, etc.). Now it just reads `sel_slot = descr_binop_opnd_slot(sel)`.
   - **Unique β per take box.** Each take box's `def β` used the shared CASE `lbl_β` (= `xchainN_nK_β`, which the chain *also* defines), and with N arms that's N+1 definitions → duplicate. Case is deterministic (no resume into arms), so each take box now gets its own `xcase%d_take%d_β` / `xcase%d_deftake_β` (defined, never targeted, fails to ω). Killed the duplicate `xchainN_nK_β` in m4.

Plus the patch's scaffold (kept from WIP): `IR_CASE_ARM` kind (IR.h / scrip_ir.c), `bb_case_arm` dispatch (emit_core.c), `rt_case_eq` re-landed from `src/attic` into live `rt.c` + libscrip_rt (`nm -D` confirmed it was missing), the Makefile source/compile lines, and the `IR_CASE` wrapper-shape admissibility check in scrip.c.

---

## DEBUG LESSON (logged)

m3 (in-process binary) **tolerates duplicate labels** (label-define records the current position, last-wins; jumps resolve to the last). m4 (`--compile` → GAS → `as`) **rejects** them. So a box can be 5/5 in m3 and 0/5 in m4 purely from label collisions. **Always `as` the m4 `.s` when a kind passes m3 but not m4** — the error line names the colliding symbol and points straight at the double-emit. The duplicate-label trail here was: (a) arm-node α (template label), (b) selector re-walk, (c) shared CASE β across take boxes — three distinct collisions, fixed in order.

---

## Hard-won facts (do-not-re-derive)

- Binop operands are in **`operand_aux`**, not `operands[]`, until `descr_chain_operand_refs` binds them — and it only binds nodes on the **main γ/ω chain**. Any isolated sub-expression walk (case arm, and likely future constructs) must hydrate from `operand_aux` first (helper pattern in `case_slot_binop_operands`).
- `lower()` returns **entry**; `*res` is the **result**. For anything that will be slot-read, push `*res`, not the return value. The selector already did this; the arms didn't.
- `bb_binop_arith` reads operand **slots** (`FRQ(op_sa+8)`) and is gated on `op_off ≥ 0`; it never embeds literals inline. A two-literal binop in isolation therefore needs its literals pre-emitted as producers (the helper) or it produces a no-op with no result slot.
- The two emitter dispatchers are **`walk_bb_flat`** (emit_bb.c, the flat-chain dispatcher with `flat_drive_*`) and **`walk_bb_node`** (emit_core.c, single-box, where `IR_CASE_ARM` lives). `EMIT_PAIR_FILL` → `walk_bb_node`. The arm IS correctly routed through `walk_bb_node`; `walk_bb_node` copies `IR_LIT(nd).ival` → `g_emit.op_ival` (emit_core.c:328), which bridges the driver's `IR_LIT(arm).ival = 0/1` to the template's `_.op_ival` compare/take role flag.

---

## Possible follow-up (not blocking)

- `flat_drive_binop_tree`'s early-return for `LIT op LIT` (emit_bb.c ~1431) does **not** allocate `op_off` and assumes caller-set operand slots — it is incomplete/likely-dead for producing a value in isolation. Not touched (risk to SNOBOL/gvar paths); the case helper sidesteps it. Worth an audit if another caller relies on it.
- Computed **selectors** (`case 1+1 of …`) and **computed keys** are handled by the helper (it's wired for key + value + default), but only depth-1 binops are exercised by the corpus; nested arm expressions are untested.

---

## Gate (all green this session)

`test_icon_rung_suite.sh` m3=m4=**127/283** FAIL 25 XFAIL 36 EXCISED 95 (FAIL-list-diff vs baseline = only the 5 rung33 flipped EXCISED→PASS, zero regressions) · `test_smoke_icon.sh` 12/12 m3+m4 · `test_smoke_prolog.sh` 5/5 m3+m4 · `test_gate_icn_no_stack.sh` 0 · `test_gate_icn_one_reg_frame.sh` 0 · FACT grep 0. Style: my new lines all ≤200 cols; `bb_case_arm.cpp` template-pure (0 raw-byte producers, 0 `bb_bin_t`, 0 blank lines).

## Provenance
Single Claude session: orientation → applied & fixed the WIP CASE patch → landed. Canonical sources consulted: `refs/jcon-master/tran/irgen.icn` (`ir_a_Case`), `refs/icon-master/src/runtime/{oarith,ocomp}.r` (=== coercion). SCRIP `176ecda`. HEAD (.github) = this file.
