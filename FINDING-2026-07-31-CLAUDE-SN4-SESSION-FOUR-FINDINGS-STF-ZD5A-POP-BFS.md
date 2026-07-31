# FINDING-2026-07-31-CLAUDE-SN4-SESSION-FOUR-FINDINGS-STF-ZD5A-POP-BFS

Session s21x-z (2026-07-31, Claude Sonnet 4.6). Baseline: SCRIP `6e45fb6d` (s21x-y HEAD).
Watermark confirmed: crosscheck m3 231/86 · m4 229/86/2 · DIV=1 {W04_arbno_basic}.

---

## FINDING 1 — STF-FLIP IS PURE CEREMONY; HKQ NEVER FIRES

**Measured corpus-wide (318 crosscheck programs, `SCRIP_STF_DEBUG=1`):**
- 31 programs arm (`live=1`): all arithmetic / assign / concat / goto / output shapes.
- 0 armed programs have ANY `ptr [rbp` data reference.
- 0 armed programs have ANY HKQ (`[rbp + -N]`) reference.
- `IF(stfh(), x86_zclaim(48))` in `bb_match_head` fires in **0/318 programs**.

**Root cause:** arming predicate at `emit.cpp:2633` requires `!flat_pat && !flat_gen`.
`bb_match_head` — the ONLY template using HKQ — lives exclusively in `flat_pat` graphs.
The two sets are **disjoint by construction**. The bracket arms only on graphs that cannot
contain its only customer.

**Consequence for ZD-5:** the goal file states *"with the rbp bracket now default-on,
the depth-immune base the family needs EXISTS."* It does not exist for that family.
ZD-5a-PRE is vacuous (the 48B carve never fires). ZD-5's stated premise is false.

**The bracket IS correct for variable-length statements** (ARBNO, FENCE1, recursion)
where ΣK is not static. It is pure ceremony for all 31 currently-armed programs.

**No code changed for this finding. No commit.**

---

## FINDING 2 — ZD-5a-PRE IS VACUOUS BY CONSTRUCTION

`bb_match_head:32` `IF(stfh(), x86_zclaim(48))` fires **zero times** over the full
crosscheck corpus (318 programs, both modes). The "unledgered second allocation authority"
named in the s21x-y cursor never allocates.

Measurement: `grep -A3 'match_head_α' <compiled.s> | grep 'sub rsp, 48'` → 0 matches
across all 318 programs. The `stfh()` predicate is always false in match-bearing graphs
because `flat_stmt_frame` is gated `!flat_pat` at `emit.cpp:2633`.

**Do not spend a rung on ZD-5a-PRE as written. Re-derive ZD-5 entry conditions.**

---

## FINDING 3 — CONSUMER POPS IN bb_assign_global ARE COUNTERFEIT FINAL SUCCESS

**Law violated (ZD-1, s21x-v, port discipline):** γ SUSPEND. ω own-K. The consumer
does not release the producer's cell. `test_icon.c` embodiment: `to1_I = x1_V` — reads
the producer's named cell, never frees it, because `x2_fail: goto x1_resume` re-enters
x1 at β and x1 must still have its state.

**The two illegal sites in `bb_assign_global.cpp`:**
```
line 48:  IF(vfc(), ... + IF(!stf(), x86_zrelease(16)))   // value path
line 60:  IF(vfc(), ... + IF(!stf(), x86_zrelease(16)))   // name path
```
Both pop the **producer's** 16B cell, not the assign box's own storage (assign carves
nothing at α — there is no `sub rsp,K` in bb_assign_global).

**Deletion tested:** removing both `IF(!stf(), x86_zrelease(16))` clauses rebuilds
clean but produces m4 222/93/2, DIV=7 — seven new failures, all and only transfer
programs (214_indirect_goto, 215_indirect_goto_cond, 1020_code_label_transfer,
1021_code_direct_goto, 082_keyword_stcount, test_stack, W04_arbno_basic), all `armed=0`.

**Root cause of regression:** the pop was standing in for a FINAL SUCCESS release.
In armed graphs the statement bracket (`mov rsp,rbp`) provides it; in unarmed graphs
the pop WAS the release, counterfeit as it is. Deletion is correct but incomplete.

**The missing half:** a statement-completion release on transfer edges for unarmed graphs.
SNOBOL4's goto field `:(LABEL)` IS the statement's final success — that edge is where
the accumulated ΣK must be released as `add rsp, ΣK`. ΣK is statically known (BFS
interleave doesn't affect this — it's the sum of producer K's in scope at the transfer).

**Other templates with same defect (consumer pops):**
- `bb_binop_arith.cpp` lines 66, 107: `x86_zrelease(16)` in consumer position
- `bb_binop_concat_slot.cpp` line 40: `x86_zrelease(16)` in consumer position
- `bb_match_head.cpp` line 34: `x86_zrelease(16)` — subject cell pop (different
  authority: subject is a dedicated producer whose sole consumer IS match_head,
  and the match statement's γ is final success — may be legitimate; needs ruling)

**bb_save_restore.cpp** and **bb_match_defer.cpp** zrelease calls are own-K at ω —
those are correct.

**Tree reverted to green before handoff. No commit.**

---

## FINDING 4 — .s SCRAMBLE IS BFS FILL IN emit.cpp:1988, NOT THE EMITTER

**Observed:** statement boxes interleave in emitted `.s`. arithmetic.sno example:
stmt `OUTPUT = A + B` emits n4(var), n5(var), then n7(binop) and n10(assign) are
separated by n6(var)/n8(var)/n11(binop)/n9(var)/n12(var) from stmts 4 and 5.
Source comments are therefore misaligned — `# OUTPUT = A + B` sits above n4/n5
but n7 (its binop) sits under `# OUTPUT = A - B`.

**Root cause:** `nodes[]` is filled by a BFS queue (FIFO) at `emit.cpp:1988`.
BFS interleaves sibling subtrees by design — stmt 3's γ successor is stmt 4's head,
so both enter the queue at the same level. This is not an emitter defect; it is the
fill discipline. The repo law "emission order is not a contract (BFS interleaves)"
(s21x-g) documents this knowingly.

**Your directive makes emission order a contract.** Fix is in the fill, not the emitter.

**Correct approach (ruling on SRC-ORDER-LAYOUT option B):**
Reorder `nodes[]` by statement membership after BFS fill, before the labeling loop
(`g_flat_node_id` assignments at `emit.cpp:2071`). Statement membership derives from
the γ-wire walk that `zd_plan` already performs (`bb_src_of` identifies heads; γ wires
+ operand edges reach all members). That walk must be replayed as a sort key before
the `_uid` counter runs, or the prefix-sum `op_flat_disp` ordering breaks.

**op_flat_disp hazard:** `op_flat_disp` is a prefix sum over fc_geom-granted suspended
cells, computed in `zd_plan` which walks `nodes[]`. If `nodes[]` order changes,
`op_flat_disp` must be recomputed on the new order — not just the labels reordered.
This is the "emit-side stno sort" hazard the goal file names under option (A); option (B)
avoids it by fixing order at the source, before any prefix sum runs.

**`bb_src_of` is a head-only marker** (registry lookup; non-null only for statement heads).
It cannot be used as a per-node group key. Membership must be walked from each head.

**No code changed for this finding. No commit.**

---

## NEXT SESSION ORDERED

1. **Transfer-edge FINAL SUCCESS release for unarmed graphs** — prerequisite to the
   bb_assign_global pop deletion (Finding 3). Read seed `.s` embodiments first:
   `SCRIP/seed/test_sno_stmt_frame_1.s` and `_2.s`. Emit `add rsp, ΣK` on the
   goto/transfer edge for unarmed graphs; ΣK = sum of producer K's in scope.
   Then delete the four consumer pops (assign × 2, binop_arith × 2, concat_slot × 1).
   Gate: m4 229/86/2, DIV=1 must hold after both changes together.

2. **SRC-ORDER-LAYOUT (B) — lower-side id assignment fix** — reorder `nodes[]` fill
   so ids run consecutively within a statement. `zd_plan`'s γ-wire walk is the
   membership oracle. Must recompute `op_flat_disp` on new order. Gate: watermark
   neutral + `.s` regen × 5 + source comments correctly aligned with their boxes.

3. **STF-FLIP audit** — measure whether the bracket should be default-OFF (revert
   STF-FLIP) or whether the arming predicate should admit `flat_pat` graphs so the
   match family actually gets the depth-immune base ZD-5 needs.

**CARRY UNCHANGED:** test_string m3 flake (nondeterministic, both regimes). 130/131
clean-HEAD segv (deterministic, unchased). COMPARE m4, NEVER m3, when gating.
