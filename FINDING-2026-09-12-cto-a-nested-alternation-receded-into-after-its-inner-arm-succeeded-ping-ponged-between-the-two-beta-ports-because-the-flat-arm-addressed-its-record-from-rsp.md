# FINDING — a nested alternation receded into after its inner arm succeeded ping-ponged between the two β ports, because the flat arm addressed its record from rsp

cto · 2026-09-12 · MODE NONET · SCRIP `61553ed9e` · row `snobol4-a-nested-alternation-receded-into-after-its-inner-arm-succeeded-ping-pongs-between-the-two-beta-ports-forever` (CEO-564's THIRD mechanism; CEO-605 assigned the residue to the cto)

## THE CLAIM

The fuzz name `arbno_fence_span_replace_branch_2` hid the shape: the program has **no ARBNO and no FENCE**. It is `P = (SPAN(' ') | (NOTANY('abc') | NOTANY('+'))) TAB(0); 'aaa' *P RPOS(0)` — a **nested alternation whose inner arm succeeds and is later receded into**. Minimal, inline, no defer: `'bz' ('a' | ('b' | 'c')) 'y'` hung where SPITBOL says `nomatch`. The all-fail shape, the flat form `('a' | 'b' | 'c')`, and inner-wins-without-recede were all green, which is why the variant ladder was the instrument, not a guess.

`bb_match_alternate()`'s ALT-FLAT arm carves a 32-byte record at α (cursor@0, β-target@8, next-alternative@16) and **every port addresses it as `[rsp+k]`**. When alternative k is itself an alternation, its own record is still on the stack at the outer's γ, so the outer's σ stub `mov [rsp+8], <jmp inner β>` writes into the INNER's record; the outer β and the inner β then both execute `mov rax,[rsp+8]; jmp rax` on the same cell and jump to each other forever. A live PC sample under gdb on both the inline and the deferred witness landed on exactly that instruction in the inner box. The ALT-RBP arm (frame-resident record, blob scope only) does not have the defect; the deferred witness hung in the main statement's flat-arm alternate, not inside the blob.

## THE CURE — the β target rides in a pushed cell, never in a record that may be buried

Flat arm only, σ stubs and β: the stub pushes a 16-byte cell holding the β target at the **alternative's own γ-time stack top** (below whatever frames the alternative left live) and β reads it and pops it before jumping to the alternative's β, so the alternative resumes with rsp exactly where its γ left it. The ω arrival and the next-alternative stubs are unchanged — they run after the alternative's frames are gone, where `[rsp+k]` IS the record. The rbp arm is untouched. This is the same lesson as the ARBNO frame arm cured this morning (`77779d96b`): a box's state addressed relative to a stack pointer the body is allowed to move is per-nothing.

## MEASURED — output vs SPITBOL, m3 and m4, -O0, never rc

| population | before | after |
|---|---|---|
| row DONE-WHEN: 3 witnesses (inline, corpus shape, deferred) + 3 controls, both modes | RED ×6 arms | **rc=0** |
| `test_gate_a_nested_alternation_receded_into_resumes_its_own_arm_not_the_outer_beta` (new, WIRED; 8 probes × m3+m4 pinned from SPITBOL x64 and re-verified live at pin time; controls c1 inner-wins, c2 flat, c3 plain recede, w4 recede-then-WIN) | the three witness shapes measured red by hand pre-cure (the freshness preflight refuses a fail-once run on a snapshot older than the tree; recorded, not worked around) | **16/16** |
| every corpus `.sno` containing a nested alternation `| (` — 48, scratch copies, not a board | — | one mover, `tests/snobol4/nested_alt_span_breakx_rpos` HANG/HANG → PASS/PASS; 0 regressed |
| every corpus `.sno` containing ARBNO — 127, scratch copies | — | no movers either mode |
| right-sealed defer gate · a_fail_operand gate · preflight · strip_comments · wiring ratchet · Icon smoke · SNOBOL4 smoke | — | 17/17 · 16/16 · 33/0 · 0 · 28/0 · 15/15 ×2 · 7/7 ×2 |

## THE FOURTH MECHANISM, NAMED

`fence_arb_span_replace_branch_1` — `'aa a' (SPAN('ab')) . v0 FENCE((ARB) . v0 (POS(1) | '')) RPOS(0)`, oracle `match`, ours SEGV both modes — IS fence-shaped: the crash is SPAN's β executing `mov r14d,[rsp+4]` with **rsp == 0**, reached through `n11_match_fence1_β: mov rsp, [rsp+144]` — a FENCE1 rsp restore from a cell that reads zero. Not cured under this row; it is its own row. Of CEO-564's 12 programs: 4 cured at `51add4eec`, 5 at `77779d96b`, 1 here, 1 remains (`fence_arb_span_replace_branch_1`), 1 unmeasured (`array_replace_branch_2`, -INCLUDE).
