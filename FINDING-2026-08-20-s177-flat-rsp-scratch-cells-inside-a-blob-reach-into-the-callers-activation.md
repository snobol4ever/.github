# FINDING s177 (HQ, Fable 5) — **THE POINT WHERE UNBOUNDED/UNKNOWN STACK REACH MUST BE DEALT WITH: A SCRATCH-CELL LEAF INSIDE A SEAM-ENTERABLE GRAPH PRICES ITS CELL AS A FLAT RSP OFFSET, AND THAT OFFSET WALKS ACROSS THE SEAM INTO THE CALLER'S ACTIVATION. AT DEPTH 1 IT LANDS IN SLACK (PASSES BY COINCIDENCE); AT DEPTH 2 IT LANDS ON THE BANKED γ WIRE AND THE MACHINE JUMPS THROUGH A CURSOR.**

**Front:** ARCH-PASSTHRU (Lon's escalation-ladder law 0c) · witnesses `corpus/probe/passthru/ptw_min_segv.sno` (+ the PT-COMBO `ptc1b/2b_*3` class) · SCRIP `bac98d58`, both modes, m3 ≡ m4.

## The reproducer (4 lines, oracle `match`, SCRIP rc139 both modes)
```
$('Z' 'Z') = 1                      (fz poison: forces the live seam road)
P1 = TAB(4) | TAB(3)
P2 = LEN(1) *P1 LEN(1)
'abcdef' POS(0) *P2 'ef' RPOS(0)
```
Same P1 behind ONE seam (`ptc1b_var2`) PASSES — by coincidence, see below.

## The frame arithmetic (from the emitted `.s`, hand-verified)
PAT$1 (`LEN(1) *P1 LEN(1)`) frames: `push rbp; sub rsp,24` → banked γ wire r10 at **rbp−8**, ω at rbp−16, rdx at rbp−24; its DEFER carves 16 → rsp = rbp−40. It enters PAT$0 (`TAB(4)|TAB(3)`, FRAMELESS — `blob_frame_bytes()==0` legacy shape), which carves its 32B choice record → rsp = rbp−72. The two TAB boxes then store their β-restore cursor at zd_plan's FLAT coordinates: `n2: mov [rsp+48], r14d` → **rbp−24** (caller's rdx bank) · `n1: mov [rsp+64], r14d` → **rbp−8** (caller's banked γ CONTINUATION). n1 is TAB(3), the second alternative — reached ONLY on β-retreat, which is why the forward road never bleeds.

## The runtime proof (gdb, m4 binary, breakpoint at n1_match_tab_α)
```
writes [rsp+64] = 0x7fffffffe030 = rbp-8        (the banked γ-wire cell, exactly)
[rbp-8] BEFORE store: 0x0000000000401970        (a real code pointer)
SIGSEGV at pc=0x1, r10=0x0000000000000001       (low dword overwritten with cursor r14d=1)
```
PAT$1_γ's `mov r10,[rbp−8]; jmp r10` executed address 1. The crash is not "a SEGV": it is the flat coordinate crossing the seam, measured to the byte.

## THE DEAL-WITH RULE (Lon's ladder 0c, mechanized — the escalation trigger is COMPILE-TIME DECIDABLE)
A box's ζ cell may ride RSP fixed offsets ONLY while every byte between its cell and its RSP at access time was carved by boxes of ITS OWN graph — known count, known type, priced by zd_plan's execution-sequence walk. The moment the box lives in a graph that can be ENTERED THROUGH A SEAM (a blob/EXPR/CODE graph: no MATCH_BEGIN of its own), what sits above it is the CALLER'S ACTIVATION — unknown number and type of frames the planner never walked — and tier 1 fails STRUCTURALLY, not probabilistically. Escalate: the cell homes in the graph's OWN RBP activation frame (tier 2). Trigger predicate, already in the lattice: `zdp_scratch_cell(nd) && graph-is-seam-enterable` ⇒ RBP slot. PAT$0's defect is exactly that it stays FRAMELESS (its TAB cells are not registry candidates, so `blob_frame_bytes()` reads 0) while its cells reach outward.
**Face A is the same wound wearing the filter:** s127's `sn4_alt_carrier` all-leaf admission exists BECAUSE arm-interior carves make the flat coordinates wrong; single-leaf arms were admitted because their flat cells "only" reach caller slack (the s130 "passes by coincidence" conviction, verbatim). The PT-COMBO board measured the filter's exact perimeter: any ALT arm > one leaf behind a seam = silent `nomatch` (`ptw_min_refusal`: `P1 = LEN(3) | LEN(2) LEN(2)`, pure LEN). Fix direction per NO-DENY + the ladder: FRAME the seam-enterable graph, home every scratch cell + the choice record in that frame, DELETE the admission.

## Measured state (PT-COMBO, corpus pushed)
55 combinatorial witnesses (classes 0–8 × var/fn road × 2–3 levels × fwd/retreat, all oracle-refed, all fz-poisoned — the un-poisoned control INLINES and tests nothing): **40/55 both modes, m3 ≡ m4 every row.** 15 reds = the two faces above, both minimized. ⚠ `ptc5b` FENCE greens are suspect (nomatch-for-the-wrong-reason possible) — re-grade after face A falls.
