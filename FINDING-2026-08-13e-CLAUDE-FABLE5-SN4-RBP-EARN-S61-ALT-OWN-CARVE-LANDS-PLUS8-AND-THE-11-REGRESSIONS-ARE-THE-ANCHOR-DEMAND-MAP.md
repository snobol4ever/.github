# FINDING 2026-08-13e — SN4 RBP-EARN s61 — ALT OWN-CARVE LANDS (+8 NET, 12 SIG11 CURED) AND THE 11 REGRESSIONS ARE ONE CLASS: THE ANCHOR-MECHANISM DEMAND MAP

**Seat:** Claude Fable 5 · **Repo state:** SCRIP `8b97e24d` on top of `ca57c8fa` (s60) · **Directive (Lon, in-chat):** "Notice in claws5-match.s the label n5_match_alternate_α ... the ALPHA is not carving its own BB LOCAL to store the NEXT POINTER. Fix that."

## What was wrong

`bb_match_alternate` stored its state trio — saved delta dword, resume quad, next quad — through `FR(_.op_off+0)/FRQ(_.op_off+8)/FRQ(_.op_off+16)`: registered flat displacements into the residual `flat_frame_bytes` graph region, with **no `sub rsp` anywhere in the box**. `emit.cpp:2918`'s CARVE-ERAD correction already named IR_MATCH_ALTERNATE as the witness of exactly this aliasing class ("a box that carves nothing keeps living in the graph slot region"). Two structural defects follow: (a) the slots are **per-BLOB, not per-activation** — nested or re-activated alternations of one node share ONE trio (the DEL-T1 disease `bb_match_arbno`'s ROOT-SPINE note documents), so an inner group's resume/next writes clobber the outer's; (b) the displacement is only valid at one assumed frontier depth.

## What landed (SCRIP `8b97e24d`)

α now carves its own 32B record (`sub rsp,32`, 16B-quantum law): delta `[rsp+0]` (+4 dead), resume `[rsp+8]`, next `[rsp+16]`, pad `[rsp+24]`. Entry stubs, sigma stubs, β, af follow with `RDD/RSP` direct spellings (escape the FR classifier — no frame-base re-canonicalization). Release obeys the unwind law clause 2 (`emit.cpp:1937`): **the generator frees its OWN K at exhaust** — `add rsp,32` at `L(19)` before ω; β and af keep the record live (backtrack re-entry, and the next-arm entry stubs still write `[rsp+16]`). Success-side growth is NON-POPPING by THE MODEL. `zd_k(IR_MATCH_ALTERNATE)` stays 0 this rung — deliberately; see the falsification below. `claws5-match.sno` compiles to exactly the prescribed shape and is oracle-identical (it also was pre-change — NOT a mover; its historical failures were elsewhere).

## The gate (full A/B, same build box, same harness)

- **165 board:** 137→136 PASS. Sole mover 054 PASS→DIFF.
- **Corpus 1205 by-set (stash/pop A/B, `test_rsp_descent_sweep.sh`):** 530→538 PASS. 38 movers total. `0 BOMB_RETURN_BAD` both sides.
  - **19 up:** 12 SIG11→PASS (`crosscheck/patterns/061,068,100,101,102,103,106,107,157` + `probe/bb/probes/G01,H01,H04`), 3 DIFF→PASS (`063,064,065` fence-fn), 1 SIG7→PASS (`H18`), 3 TIMEOUT→PASS (`X10, test_sno_alt_d0, test_sno_alt_d5`). The cured class is fence/nested/re-activated alternation — the shared-trio aliasing (b) above.
  - **11 down (ALL stable across 2 serial single-job reruns — real, not flake):** DIFF: `054_pat_arbno_alt, probe/bb/{t1,c5}, probes/{H12,H13,N12,N15,N16}`; SIG11: `probes/{A05,X08}, 171_pat_abort_no_anchor_advance`.
  - **8 lateral** among already-failing programs (SIG11↔SIG7/SIG6/TIMEOUT — the address-sensitive-junk class reshuffling as stack geometry moved).

## The regression mechanism — one class, gdb-free (asm read + program shape suffice)

054's shape is the whole class. `X POS(0) ARBNO('a'|'b') . V RPOS(0)`: the SAVE/COND capture pair straddles the ARBNO; `n11_match_assign_cond_α` reads SAVE's parked cursor at the **static depth-difference offset** `mov eax,[rsp+16]`. Per committed ARBNO instance the flow is `arbno_β → ALT α (sub 32, record k) → arm → σ → merge γ → arbno_as → COND α`, and extension happens by backtrack THROUGH the live records — so after k commits, **k live 32B ALT records interpose** between SAVE's cell and COND's read. `[rsp+16]` reads inside record k's pad; V captures garbage/empty. Old world was accidentally net-zero (shared trio = 0 rsp delta per iteration) and accidentally LIFO-correct for *sequential self re-activation* (latest-wins == retract order) — which is why these 11 ever passed — while being wrong for *nesting* (the 12 SIG11s now cured). Every regression witness matches: `ARBNO(alt) $ OUTPUT` (t1/c5/H/N probes), one-arm capture straddle (A05), ABORT from inside an arm unwinding across the live record (171).

**FALSIFIED before spent: `zd_k(ALTERNATE)=32` cannot repair this.** The interposition is `32·k` for runtime-variable k — no static planner offset expresses it. This is verbatim the K16 prelude's outer-SAVE decline ("K16 commits would interpose between that cell and its COND static-distance read — 166 witnesses"), now reproduced by a second mechanism. The composition (record must survive success for backtrack ∧ chain/static reads need net-zero) is satisfiable only by a depth-immune read basis — **the anchor. Same mechanism, different motive, as FINDING-2026-08-13 BOARD-B12 already noted for the ARBNO cell.** These 11 + the 056 SPOT oscillator are the demand-evidence set; per the s59 cursor law: DO NOT patch ad hoc.

## Owed / open

1. **Push pending** — commits local; credential to be requested from Lon (his session-start instruction: at session end).
2. **s60's owed artifact regen** (benchmark/feature/demo) still unrun this session — two Lon pivots preempted it; it will now also capture s61's alternate shape (every alternation-bearing `.s` changes).
3. Dead zls grant: `zeta_storage.c` still grants the ALT trio nobody reads — bytes-only waste, cleanup rung.
4. The 8 lateral SIG-shuffles are unowned oscillator movement; no action.
5. Decision for Lon: whether the anchor mechanism rung opens now (11 stable witnesses + 056 + the s58 BOMB map all point at it) or the regression set rides until then.
