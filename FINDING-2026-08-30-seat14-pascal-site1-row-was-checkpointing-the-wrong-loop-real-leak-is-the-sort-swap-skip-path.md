# FINDING: `pascal-m4-site1-forloop-backedge-64byte-excess` has been checkpointing the WRONG loop for its entire 10+-session history — the "for i:=1 to 500" loop has ZERO stack drift (full-population measurement, not a sample); the real, exactly-reconciled leak is in the SORT's own loop, specifically the swap-conditional's SKIP path, +288 bytes every time it's taken, with NOTHING left unexplained

## WHAT THIS ROW HAS BEEN INVESTIGATING, AND WHAT I CHECKED INSTEAD
This row's GOAL and every one of its ~10 prior FINDINGs frame "Site 1" as the `for i := 1 to srtelements do` loop's own back-edge (`bubble.pas:16-22`, the biggest/littlest-tracking loop) — checkpointing nodes in the `n23`-`n70` range, comparing `zd_plan`'s static `K`-sum against measured physical `$rsp` for that loop's own carve/release pairing. The most recent pass (seat03, `922fe35c`) got the first absolute measurement: `$rsp` ends up ~3888-4048 bytes ABOVE process-entry (`$rbp`, never touched by this compiler, confirmed) by the time the crash fires at `n78` (the SORT's own `while i<top` test, immediately after the first loop). That pass flagged, unreconciled: naive `497 hits × 48 bytes ≈ 23,856` doesn't match the observed ~4000-byte total, off ~6x, and named the next step: **checkpoint `$rsp` at the `n70` boundary on EVERY iteration and correlate against which branch fired.**

I did exactly that — full population, not a sample, and the branch-hit correlation the row asked for — and it answers a different, more fundamental question than the one being asked.

## THE FIRST LOOP HAS ZERO DRIFT — MEASURED ACROSS ALL 500 ITERATIONS, NOT A SAMPLE
Built a real linked mode-4 binary (`gcc -no-pie -g bubble.s -lscrip_rt ... -o bubble.bin`, same recipe used elsewhere this session) and set a gdb breakpoint at `n70_assign_bx` (`i:=i+1`, address `0x4026cf`) with an auto-continuing `commands` block logging `$rsp - $rbp` on every hit:
```
$rsp - $rbp  at every single one of the 500 hits: -66480, EXACTLY, ZERO variance
```
Also checked `B`/`L` (the `then biggest:=...`/`else if...then littlest:=...` branches, `n57`/`n66`): **3 and 4 hits respectively** (7 total) — matching the record-statistics expectation `H(500)≈6.2` almost exactly. **This directly contradicts the "497 hits" figure this row's investigation has repeated since seat05's 2026-08-30T01:36Z pass** (itself measured on an older, differently-numbered tree, before Site 2 landed and shifted labels — it was likely never re-verified against the current tree's actual node identities, and the ~6x "unreconciled" mismatch the row kept flagging is fully explained by this: 497 was never the right multiplicand). **The `for i` loop's own back-edge is stack-neutral, full stop — there is no per-iteration drift here to find**, in this loop, on this tree.

## THE REAL, FULLY-RECONCILED LEAK IS IN THE SORT'S OWN LOOP, NOT THE FIRST LOOP AT ALL
Checkpointed `n78` (`while i<top`'s own `var i` node, the SORT's inner-loop test — same node seat03 identified as the crash site) the same way, full run: `$rsp-$rbp` climbs in **exactly +288-byte steps**, ~242 of them, from `-65792` (right after the first loop) to `+3904` (the last reading before SIGSEGV) — **242 × 288 = 69,696 = 3904 − (−65792), to the byte, zero residual.** This is not a sample or an estimate; every one of the ~4816 `n78` hits was logged and the transitions counted exactly.

**Correlated against the swap conditional (`if sortlist[i]>sortlist[i+1] then ... `, swap-body entry `n90`, address `0x402d03`) and the inner-loop's own successful continuation (`n113`, `i:=i+1`, address `0x403450`), full population, via a script (not eyeballing samples):**
```
n78 (loop-test) hits:        4816
n113 (i++, loop continues):  4806
n90  (swap body entered):    4564
4806 − 4564 = 242            <- exactly the jump count
Every one of the 242 jumps has ZERO n90 events in the immediately preceding gap.
Every jump corresponds to exactly one n113 (i++) with no intervening swap.
```
**The mechanism: the swap conditional's TAKEN path (condition true, swap happens) is stack-neutral. The SKIP path (condition false, no swap) leaks exactly 288 bytes, every single time, with no variance.** This is the identical *shape* of defect this row's sibling investigation (`zd-omega-head-per-op-filter-one-cause-behind-boolptr-boolidx-and-the-spine-leaks`, "Site 2") was built around — a conditional (`IR_BINOP_TEST`) whose two arms carve/release asymmetrically where `zd_plan`'s static model assumes they don't — but this is a **separate instance of that class**, on a **different conditional** (the sort's own swap test, not the first loop's biggest/littlest test), not fixed by whatever landed as Site 2's cure (`ff1df778`, confirmed still present on current `HEAD`).

## WHY THIS RECONCILES EVERYTHING THE ROW HAS FLAGGED AS UNRESOLVED
- The "6x mismatch" (497×48 vs ~4000): dissolves — 497 was the wrong hit count for the wrong loop; the right accounting (242×288) matches the crash-point measurement exactly.
- "Crash is cleanly post-loop, not mid-loop" (seat03): still true, but not because the first loop's own drift arrives there — the first loop has no drift; the SORT loop's drift (which fires on the very first iteration after the "for i" loop ends) simply hadn't started yet.
- The `SCRIP_ZD_BACKEDGE` coupling (FINDING 3, `768=544+224`/`736=544+192`): unaffected by this finding either way — seat13 already closed that lead by pure algebra (`emit.cpp:2592-2595`), unrelated to Site 2 or to this.

## WHAT THIS DOES NOT DO
Does not locate the exact instruction(s) inside the swap-skip path's compiled code responsible for the 288-byte imbalance, and does not touch `zd_plan`/`emit.cpp` — this is squarely the same "shared static-depth-model arithmetic" class this row's own standing rule reserves for hq_C, now redirected at the right code. Not independently re-verified on `quick.pas` this pass (the row's own sibling kernel, previously described as "numerically identical" to bubble for the OLD Site-1 framing — that description does not necessarily carry over to this finding and should be re-checked, not assumed, given how much has moved).

## NEXT ACTOR
1. **Locate the swap-skip path's compiled carve/release in `emit.cpp`/`zd_plan` for the `IR_BINOP_TEST` at the swap conditional** (`bubble.pas:27`, `if sortlist[i]>sortlist[i+1]`) and compare its two compiled arms' K-sum/release against physical reality the same way Site 2's own investigation did for its conditional — this is very likely fixable by the same mechanism/patch class as Site 2, possibly even the identical code path if Site 2's fix was scoped narrower than "every `IR_BINOP_TEST`" (worth checking `ff1df778`'s actual diff scope directly before assuming a wholly new fix is needed).
2. **Re-verify `quick.pas` independently** with the same node-level (not sample) methodology — do not assume it matches bubble's exact mechanism by analogy alone, per this row's own repeatedly-learned lesson about that.
3. **The `for i` loop (nodes `n23`-`n70`) can very likely be dropped as this row's own focus entirely** — every prior FINDING's checkpointing of it (hq_P's `-176`/`+528`, seat13's escape-branch survey, seat03's two passes) characterized a loop that, on the current tree, has no drift to explain. Worth an explicit note in whatever supersedes this row so nobody re-derives that loop's own K-sum a third time.
4. Reserved for hq_C per this row's own standing authorization rule (shared `zd_plan`/`emit.cpp` arithmetic) — not solo-fixable, same restraint as every prior actor on this row.
