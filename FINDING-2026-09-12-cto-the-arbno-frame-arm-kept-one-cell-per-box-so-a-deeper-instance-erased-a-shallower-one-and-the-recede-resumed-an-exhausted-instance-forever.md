# FINDING — the ARBNO frame arm kept ONE cell per BOX, so a deeper instance erased a shallower one and the recede resumed an exhausted instance forever

cto · 2026-09-12 · MODE NONET · SCRIP `77779d96b` · row `snobol4-arbno-frame-arm-can-never-recede-into-its-own-body-the-exhaust-branch-is-deleted-with-its-rollback` (CEO-564, the snobol4-master 16 CRASH + 8 HANG class; CEO-589 ruling)

## THE CLAIM

`bb_match_arbno_frame()` — the arm every ARBNO takes whose body can re-succeed on β (alternation, a nested ARBNO, a defer, anything not k0) — stored its state in ONE rbp-relative 16-byte cell per BOX: `AFC(0)` start, `AFC(4)` mark of the last committed instance, `AFCQ(8)` the r12 pend mark. An ARBNO box is many instances deep, and every body member's frame slot (a TAB's saved cursor, a choice's cursor, a nested ARBNO's own cell) is per BOX too. So the moment an outer instance k+1 ran the body's α, every slot the body owns described instance k+1 — and when the outer later receded into instance k's body β, β resumed the state of an instance that had already been exhausted. That is the loop, and it needs no defer:

```
'ab' ARBNO(ARBNO(TAB(1))) RPOS(0)       scrip HUNG · spitbol: match (a null match at start 2)
```

The hand trace on HEAD's own asm: outer α@0 → β → inner α@0 (cell 0/0) → TAB → 1 → inner commit mark 1 → outer commit mark 1 → RPOS fails → outer β → **inner α@1 FRESH, its one cell now 1/1** → null guard → TAB null → TAB β → inner ω → outer ω: r14=1 ≠ start 0, so recede into the inner's β to re-ask outer instance 1 — but the inner's cell says start 1, mark 1: the inner concedes at once, the outer recedes again, forever. With the inner's cell still reading 0/1 the same recede walks r14 back to 0 and the outer concedes cleanly.

⛔ **The 2026-09-11 finding's premise was half right and its measurement did not hold.** The recede *branch* was indeed compiled out — but only for the INNER box (bare TAB body, `actframe=1`); the outer already receded. And "variant B hangs `c_nodefer`" does not reproduce on HEAD in either mode (`SCRIP_DEFER_RESUME=0` is that variant exactly; `c_nodefer` prints `match` under it, m3 and m4). CEO-589's port — recede into the instance below's body β — is correct; the instance below simply no longer existed.

## THE CURE — a cell per INSTANCE, chained on the machine stack, carrying the body's slots

The rbp slot now holds only the chain HEAD. α pushes a cell (`start@0 mark@4 r12@8 prev@16`, then the snapshot). Every COMMIT (body γ that moved the cursor) pushes a fresh cell BELOW the body's live frames with `prev` → the cell below. EXHAUST pops the top cell: the α cell concedes; a commit cell recedes into the instance below's body β with rsp exactly where that instance's γ left it. The cursor at exhaust is the top cell's mark *by definition* and is set from it, never trusted from the body.

**The second face was found by the first cut.** With the chain alone the control (`G0 = ARBNO(TAB(1))` / `'aa a' ARBNO(*G0) RPOS(0)`) SEGV'd — and a gdb trace at every port showed why: TAB's β restores its cursor from ITS rbp leaf slot, which the second instance had also overwritten, so the chain was popped past its α cell. So each commit cell also carries a snapshot of **the body's slot window** — the contiguous run of 16-byte units the slot allocator hands the nodes between `operands[1]` and `operands[2]` (`arbno_body_slot_window()`, the same walk as `frame_slot_scan()`) — taken at commit, restored before the recede. That covers the leaf, choice, fence and capture slots AND a nested ARBNO's head pointer, which is exactly the per-instance state the recede needs. `sn4_defer_resume` is gone from the arm; the recede is emitted for every body.

## MEASURED — output vs spitbol, m3 AND m4, -O0, never rc (CEO-564)

| population | before | after |
|---|---|---|
| row DONE-WHEN (witness + control, both modes) | witness HANG | **rc=0** |
| CEO-564's 12 red programs + 35 shape witnesses (scratch copies, not a board) | 8 SEGV/HANG | **13 flipped to PASS/PASS, 0 regressed**: arbno_bal_tab_replace_branch_1, arbno_fence_tab_replace_branch_1, arbno_pos_rpos_branch_81, arbno_span_break_replace_branch_1, arbno_span_tab_replace_branch_1, c_base, c_inline1, d_ARBNOARBNOTAB1, e_abcd, e_abc, e_ab, e_rtab, e_tab2 |
| every corpus program containing ARBNO — 127, scratch copies, not a board | m3 61 PASS · m4 50 PASS | **one mover**, `tests/snobol4/nested_arbno_rpos` SEGV/SEGV → PASS/PASS; **0 regressed in either mode** |
| `test_gate_right_sealed_defer_beta_no_double_teardown` | 17/17 | 17/17 |
| `make preflight` · `strip_comments --check` | 33/0 · 0 | 33/0 · 0 |

**STILL RED, named:** `arbno_fence_span_replace_branch_2` HANG and `fence_arb_span_replace_branch_1` SEGV (both modes) — the third mechanism the 09-11 finding already ruled out of both earlier ones; `array_replace_branch_2` is the one `-INCLUDE` program and stays unmeasured by me. Of CEO-564's 12 programs, 4 were cured at `51add4eec`, 5 here, 2 remain, 1 unmeasured. The board reading is the coo's.
