# FINDING-2026-08-17-s140 — THE STATIC-OFFSET DEFER β WIDENING IS FALSIFIED; THE FIX IS U-2, NOT A NEW STACK SLOT

**Seat:** Claude Sonnet 5. **Trees:** SCRIP `0887f44c` (reverted to clean — no landed template change), corpus `f8a40d63`+ (ablation table only).
**All rungs DEFAULT-INERT — no source change survives this session; the tree matches s139 HEAD byte-for-byte.**

---

## 1 ⭐⭐⭐⭐⭐ ABLATION TABLE MINTED — FINDING-2026-08-17-s139 sec.2 TABLE NOW LIVES IN corpus/probe/m1/

Five witnesses (`m1_defer_ALT`, `m1_defer_SPAN`, `m1_defer_LEN0`, `m1_inline_ALT`, `m1_nodefer_ALT`), every arm oracle-`ok`
(x64 sbl -b, re-verified this seat), reproduce the s139 table's verdicts exactly on HEAD `0887f44c` in BOTH media:
`defer_ALT`/`defer_SPAN` FAIL, the other three PASS. `probe/m1/README.md` documents the set and the invalidation rule
(any defer-record change must flip the first two to ok/ok without moving the other three off ok/ok). Committed, corpus
`f8a40d63` — NOT YET PUSHED (needs credential, see end of session).

## 2 ⛔⭐⭐⭐⭐⭐ FIRST HYPOTHESIS FALSIFIED IMMEDIATELY, BY THE NET IT WAS BUILT TO SERVE

Attempted: widen the sn4_alt_carrier and non-carrier γ records from 16B to 24B by pushing `rbp` as a 3rd quad (pushed
FIRST so existing `[rsp+0]`/`[rsp+8]` consumers — ARBNO's af edge, this box's own exhaust stub — are undisturbed), then
have β read the frame-base with a literal `RDQ("rsp", 16)` before resuming.

**Measured, one build cycle:** default-off byte-identical (confirmed against all 5 witnesses, m3). `SCRIP_DEFER_CARVE_RBP=1`:
**every one of the 5 witnesses SEGVs**, including the three standing-green counter-witnesses that pass today. Root cause,
found by comparing the emitted `.s` for two different defer nodes in the same program: `n5_match_defer_β` baked
`[rsp+32]` while `n10_match_defer_β` baked `[rsp+16]` for the nominally-same record shape — **a static rsp-relative
displacement at β is unsound because β is reached from call sites at different, dynamically-varying stack depths.**
This is not a new discovery — `x86_asm.h`'s own `x86_frame_off` comment already states the general law ("no
compile-time-constant RSP distance ... across ANY defer", emit.cpp:690) and I re-derived the SAME law by breaking it.

**Reverted clean** (`git checkout -- src/templates/bb_match_defer.cpp`); rebuilt; re-confirmed byte-identity with the
s139 baseline before doing anything else. The ablation net caught this on the FIRST build, before any beauty.sno
attempt — it did exactly the job it was minted for.

## 3 ⭐⭐⭐ gdb CENSUS: β's CALL-SITE VARIETY IS REAL BUT NARROWER THAN FEARED, AND THE ACTUAL CRASH SITE WAS MISDIAGNOSED MID-SESSION

Traced `m1_defer_ALT` under gdb (unicode label names don't resolve in this gdb build — use `nm`-derived numeric
addresses, `break *0xADDR`, not `break label_β`). Findings:

- Box-to-box β chaining (`n6`'s exhaust: `add rsp,16; jmp n5_match_defer_β`) is SAFE under the current ambient-rbp
  design — the chaining box always does its OWN `mov rsp,rbp; pop rbp` before handing off, so rbp is already correctly
  re-established for the box it jumps into. This is not the hazard.
- ARBNO's `as`/`af` sites (`cmp r14d,eax; je/jne nNN_match_defer_β`) DO jump directly into a defer's β with no
  intervening unwind — this IS the external, unprotected resume path the s139 residue names.
- **However**, on `m1_defer_ALT`, the actual SEGV (`rip=8`, confirmed under gdb, reproducible) fires at `n55_match_defer_β`
  — a THIRD, previously-unexamined defer node, reached via a completely different statement's own MATCH_BEGIN
  (`n53_match_begin_α` / `rt_match_enter`), not through the `n11/n12/n16`+ARBNO chain this seat spent most of its
  tracing on. `rbp` at `n55`'s α (`0x...e958`) vs its β (`0x...ea30`) differ by 0xd8 (216) bytes — consistent with
  SOME other activation's frame having been established and torn down in between, exactly the cross-activation clobber
  s139 named, but on a node this seat had not identified as relevant. **This seat ran out of budget before finishing
  the trace of WHY `n55` specifically is the first node to observe the clobber** (whether it's the textually-first
  unsealed carve-defer the program executes, or something more specific to its position). Re-verify which node is
  live-first before trusting any per-node reasoning here — this seat's early assumption ("the crash is in n11/n12/n16")
  was wrong and cost real time; confirm the failing node under gdb BEFORE reasoning about its source, every time.

## 4 ⭐⭐⭐⭐⭐ THE RIGHT FIX SHAPE IS ALREADY NAMED IN THIS CODEBASE — U-2, NOT A NEW MECHANISM

`ZREFS`'s own comment (x86_asm.h:1197, s139's own landed code) names this exact defect class in passing and says who
owns the fix: *"U-2 adds the RECORD-FIELD tier that ends per-template record layout assumptions (the s132 deferclob
corpse: IR_MATCH_DEFER β = bare `jmp [rsp]` three lines from IR_MATCH_ALTERNATE β = `[rsp+8]`, two private layouts on
one shared region)."* **U-2 has not landed.** The existing model for the correct shape is `sn4_choice_rbp_off()`
(emit.cpp:2411) + `zone_ref()`/`ZREFS` (x86_asm.h:1184/1197): a small per-node authority function that returns EITHER
`-1`/`0` (no rbp home, stay on the depth-tracked ζ-SPINE via `FR`/`FRQ`) OR a NEGATIVE RBP-RELATIVE OFFSET into the
node's ALREADY-EXISTING enclosing activation frame (the same registry ARBNO/CAPTURE/FENCE already use via
`frame_need_of()`/`arbno_frame_candidate()`, sized at the enclosing MATCH_BEGIN's own frame-extra allocation).

**Why this sidesteps the whole class of bug this seat hit twice:** an rbp-relative activation-frame slot is
addressed IDENTICALLY regardless of how deep rsp happens to be at the moment β fires or which call path reached it —
it is depth-immune by construction, the same property `FRQ`'s `op_zdepth` compensation exists to approximate for the
rsp arm and that a raw stack-pushed record can never have. **This is category-different from both of this seat's
attempts** (a bare stack slot at a baked displacement; ambient rbp trusted with no home at all) — it is a THIRD
option this seat did not try: give the frame-base a NAMED HOME the way CHOICE/ARBNO/CAPTURE/FENCE already have one,
sized by the enclosing MATCH_BEGIN, instead of trying to make it travel on the suspending stack.

## 5 NEXT SEAT, PICK UP EXACTLY HERE

1. **Do not repeat either falsified shape.** No baked `RDQ("rsp", N)` at β (falsified sec.2). No bare ambient-rbp
   trust with no home (the current s139 default, known broken — the reason this rung exists).
2. **Design a `sn4_defer_frame_rbp_off()`-shaped authority**, modeled EXACTLY on `sn4_choice_rbp_off()`: registers a
   slot in the enclosing MATCH_BEGIN's frame extra (same mechanism `arbno_frame_slot_assign()` uses to widen
   `emit_match_begin_frame_extra()` by 16B/site) for an unsealed carve-defer's OWN frame-base snapshot. α writes rbp
   there via the ONE dispatcher (`zone_ref`/a new `ZREFS` customer, not a hand-rolled RDQ); β reads it back the same
   way, unconditionally correct regardless of call-site depth.
3. **Before writing template code, confirm under gdb which node fires first and why**, per sec.3's caution — this
   seat's assumption cost real time twice. `nm the linked binary; break *0xADDR` (unicode labels don't resolve).
4. **Test against `corpus/probe/m1/{m1_defer_ALT,m1_defer_SPAN,m1_defer_LEN0,m1_inline_ALT,m1_nodefer_ALT}` after
   EVERY build**, before touching beauty.sno. Do not land on fewer than all 5 agreeing.
5. Push `corpus` (`f8a40d63`, the ablation table) — credential needed, not yet asked this session at time of writing.

## 6 OWED AND PAID
Ablation table: 5/5 witnesses reproduce the s139 table's verdicts on HEAD, both media, oracle-verified. Reverted
template edit: byte-identical to s139 HEAD, confirmed via full 5-witness default-arm re-run post-revert. No gate run
(no template change survives to gate). beauty unmoved (not attempted this session — the record-layout question had
to be resolved first; attempting beauty against either falsified shape would have wasted the run).
