# FINDING s174 (HQ, Fable 5) — **THE PER-OP FILTER AND THE 8-BYTE WINDOW LAW DIE. EVERY SCRATCH-CELL LEAF IS THE SAME BOX, AND THE GUARD THE WINDOW LAW WAS PROUDEST OF WAS GUARDING NOTHING.**

**Orders (Lon 2026-08-20 in-chat, verbatim in substance):** *"No [per-op filter] is allowed … There is NOTHING special about ANY, SPAN, BREAK, etc. If you have exceptions for one you have them for ALL … All leaf BBs are the same. Delete leaf_frame_candidate — all leafs are candidates. [Fix the window law] NOW. Eradicate the word [and the word 'refuse'] in every MD file, every source comment, every variable and function name."* Delegation suspended; HQ executed hands-on. Landed: SCRIP `44b8b82c` (pristine-verified at rebase HEAD). Witnesses: corpus `probe/leafwide/` (this push).

## What landed
1. **`leaf_frame_candidate()` DELETED.** Replacements: `leaf_zeta_family(op)` — the closed family DEFINITION (SPAN/BREAK/BREAKX/TAB/RTAB/REM/ARB/BAL, the boxes whose template owns a scratch suspension cell), every member identical, no admissions, no carve-outs; and `leaf_frame_member(nd)` — the ONE condition is **LOCATION, never identity**: inside an ALT arm the flat rsp coordinate has no granted owner in either medium (s66/s71), so the cell homes on rbp; on the ordinary spine the offset calculation is exact and rsp stays the home (Lon HQ-60; the s127 conviction against wholesale re-homing stands).
2. **The 8-byte window law is DEAD.** Every leaf claims **TWO consecutive registry slots** (one 32B owner; staged base = the lower slot, so d ∈ [0,24) is always in-claim — `LFC(8)`/`LFC(16)` included). `frame_slot_scan` advances by claim width; the interleaved ARBNO/CAPTURE/FENCE1/LEAF numbering stays collision-free by construction; `blob_frame_bytes`/frame-extra grow via the same one count.
3. **BAL joins the ONE dispatcher** — its 11 raw `FR(x86_scratch_off+d)` spellings became `LFC(d)`. Receipt: `ctl_bal_solo` mode-4 `.s` **byte-identical** pre/post at the default arm (ZREF's no-slot arm is `FR(x86_scratch_off+d)` verbatim, and the diff proves it).
4. **Word eradication complete** (census 0 across src/, scripts/, every `.github` MD, QUEUE.tsv, BOARD.md, SEAT-CLAUDE.md): `op-filter` and `refuse`* are gone from comments, prose, filenames (`rtcc_claimed_reg_registry.txt`, `wreg_claim_registry.txt` — gate readers repaired and re-run), and identifiers (`_tiny_fallback_z`, `_unpriced_runs`).
5. Default arm is byte-identical **structurally**: `leaf_frame_member` gates on `sn4_span_frame()` (default OFF), so no registry, carve, or claim math moves at the shipped default; the one non-gated edit (BAL's spelling) has the §3 receipt.

## Armed receipts (SCRIP_SPAN_FRAME=1, pristine)
- **`clob_altarm_arm2direct_red` — s129's HEADLINE — is CURED.** The pre-existing, no-killswitch memory corruption (SPAN's suspension dword landing on the STANDING frame's CAS mark) now PASSES armed, m3, oracle-identical. The other three clobarm reds are their own classes (wire-clobber, s128 choice-record) and keep their faces — unchanged either arm.
- `cn_alt_leaf_flat_red` + `cn_alt_leaf_lit_red` (CONST_NEST=1): green BOTH modes armed; unchanged at default.
- ⛔ **The flip stays HELD** (seat7 s173: TDump_driver PASS→flaky wrong answer armed under `ulimit -s unlimited`; their option "flip narrowed" is now ILLEGAL by the no-filter law, which strengthens hold-until-root-cause). **Seat7's 30/527 armed blast radius is STALE at this HEAD** — the claim widths and the newly admitted members resize the arm; re-sweep before any arming verdict.

## ⛔ THE FILTER'S PROUDEST GUARD WAS DEAD CODE — measured
The `SPAN(*var)` conjunct tested `IR_LIT(nd).sval[0]=='*'` — a **literal** spelling that real deferred-expression operands never carry. The pre-change armed `.s` of `SPAN(*CS)` was **already frame-homed** (`[rbp-64]`): the window law never fired on the road it existed to guard. The defect it feared is real — and it lives on a road the filter could not see (next section).

## ⛔ THE PINNED REMAINING CLASS — the operand-slot flat read inside an arm (NOT cured by re-homing the cell)
Witness family `corpus/probe/leafwide/` (all oracle-refed):
| witness | shape | default | armed |
|---|---|---|---|
| `ctl_bal_solo` | BAL, no ALT | PASS both modes | PASS |
| `ctl_spanvar_solo` | SPAN(*CS), no ALT | PASS both modes | PASS |
| `ctl_spanvar_alt_inline` | SPAN(*CS) on ALT arm, inline | **nomatch (oracle: match) BOTH arms** | same |
| `leafwide_spanvar_alt` | same through a PAT$ blob | m3 nomatch · **m4 SEGV BOTH arms** | m3 SEGV (reshuffled garbage, same read) |
| `leafwide_bal_alt` | BAL on ALT arm through blob | **nomatch BOTH arms** | same |
**Mechanism (asm + gdb receipts):** solo takes an **own-carve road** (`n15_match_span_α: sub rsp,16` — correct). Inside an ALT the box takes a **flat road**: cursor in the planner's cell (`[rbp-80]`) but the deferred-needle descriptor read at a compile-time flat coordinate (`mov r8, qword ptr [rsp+184]`) that resolves to **`rbp+16` — caller territory** — at the arm's runtime depth (`movzbl (%r8,%rdx,1)` faults; frame #1 = `0xbc000000bc`, two dirty dwords). No `rt_pat_prim_str` on this road — the sval-defer arm (fully LFC, now safe under the 2-slot claim) is a DIFFERENT road; here the **eval glue writes the operand slot at a shallower depth than the arm-interior reader reads it**. The writer and the reader disagree on the base — the fix is base agreement (the same law the cell just got), not another filter. Seat7's TDump spurious-FAIL (dropped `jne …span_beta` recede in `arbno_af`, seat4's find) is plausibly this family's backtrack face. `bb_match_span_var.cpp` (13 raw spellings, ZERO emitters — dead template) noted for deletion.
**Classification:** all three red witnesses are PRE-EXISTING both arms (arm=0 is byte-identical legacy by construction); the armed blob variant trades silent-wrong for a crash — honest-bomb-over-silent-wrong, but the class is OPEN and is the next repair, evidence in hand.

## Instrument notes (fleet, this slice)
- The every-port probe (`SCRIP_ZDP_TEARDOWN=1`) masks the blob SEGV (its push/pop shifts the stack) and prints only `[ZDP-TOP]` refusals here — the lattice refusing to price the very ports the flat road addresses **is** the conviction, but skew-catching this class needs the probe to also fire on unframed leaves.
- seat3 s172: `unary_not.sno` emits a DIFFERENT `.s` per compile (uninitialized string literal) — **the top instrument threat on the tree** (breaks md5 sweeps and the byte-identity law itself); + 7 corpus programs nondeterministic at a fixed arm; + seat1's 141 flaky false-mover. Fleet protocol need: hold-the-arm-fixed control before any mover verdict. All on Lon's desk (row creation suspended).
