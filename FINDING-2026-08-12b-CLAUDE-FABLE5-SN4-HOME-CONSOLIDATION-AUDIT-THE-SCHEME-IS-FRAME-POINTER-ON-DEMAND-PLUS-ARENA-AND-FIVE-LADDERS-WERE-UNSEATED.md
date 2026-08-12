# FINDING 2026-08-12b (Fable 5, s31) — SN4 HOME CONSOLIDATION AUDIT: THE SCHEME IS FRAME-POINTER-ON-DEMAND PLUS ARENA, AND FIVE LADDERS WERE UNSEATED

**Session shape:** all parallel sessions stopped; ONE consolidated seat owns RBP-EARN + SNOBOL4-BB + SNOBOL4-RTX + RTCC + ZETA-MECH + ZETA-CLIMB + the HOME seat files. Lon's question, verbatim in substance: *"We now think we know MAYBE how to handle unbounded, i.e. unknown at compile time, RSP stack growth which disallows a known RSP relative offset for operands. Are we right? Will this work … will the new RSP, RBP, RBX, R12, R11, R10, R13-R15 scheme work and solve EVERYTHING? … Are the new GOAL files missing anything from the previous set?"* **ZERO compiler bytes this session; no gates run; no watermark moved. Analysis + `.github` amendments only.**

## 1 · VERDICT: YES ON THE CORE CLAIM

**The LAW ("frame iff the cell↔RSP byte distance is not a compile-time constant at some site that reads it") is isomorphic to a solved problem.** It is exactly the condition under which every production C compiler abandons frame-pointer omission: `alloca`/VLA places dynamically-sized material between locals and RSP, RSP-relative offsets die, RBP is established once at entry. OPAQUE (`*P` defer of unknown growth) and UNBOUNDED (ARBNO instance stack) are the pattern-matching instantiations of `alloca`. Ruling (2)'s self-contained argument is the crux: *the commit must restore a watermark whose distance from current rsp is exactly P's growth — you cannot address the watermark with the quantity it stores. Hence rbp.*

**The tree's own commit history already ran the controlled experiments, both directions:**
- `5caf44a9` MV-BASE: forced-rsp consumer read `[rsp+slot]` *"diverges inside ARBNO bodies (SAME OFFSET ≠ SAME OBJECT)"* — the LAW violated, gdb-bracketed.
- s26 (FINDING-2026-08-11e): ARBNO's 32-bit cursor at `[rsp+4]` overwrites the UPPER HALF of a 64-bit resume address; `rip` tracks the cursor value — the UNBOUNDED hazard photographed.
- CLIMB s41: correct `end` at `[rsp+88−16N]` for N carving primitives while the template read `[rsp+88]` — non-constant distance, measured linear.
- `7c903000`: *"Wire save is per-activation ON THE SPINE, so nested deferred re-entry survives where a flat global cell cannot"* — the cure direction, HANG 12→6.
- Flat-single-cell convictions: `g_blob_ctx` (twice), `g_star_peek`, `g_rtcc_block` scan gap. M-1b's phrasing generalizes it: *"one register claimed globally: same hack, different spelling."*

**The taxonomy is TOTAL, proven not assumed.** Two hazard classes; the hypothesized third (unequal ALT arm depth) FALSIFIED BY DESIGN (arms carve nothing — ruling 3/4, one grep). Every lifetime class has exactly one home: constant-LIFO→RSP · non-constant per-activation→RBP earned `[rbp+K]` · dynamic-multiplicity match-scoped→R12 arena (mark restored at β) · heap→RBX frontier · continuations→R10/R11 per-activation spine saves · globals→R9 GVA + rip-rel RO · match state Σ/δ/Δ→R13/R14/R15. Only non-LIFO lifetime in SPITBOL semantics = co-expressions; ruling (0) handles it (own thread, ZETA-FRAMES prior art). The reading-edge sharpening (success-edge reads earn; failure-edge reads do not because LIFO restored rsp before β) is what keeps ALT/CAT frameless with `*P` operands — frames MANY and TINY, not everywhere.

## 2 · "SOLVE EVERYTHING" — THE THREE CONDITIONS (attached to existing rungs, no new rungs)

1. **Reads-based census incl. GLUE reads** (EARN-2): `frame_need_of` reconciles with `emit_graph_has_deep_arrival` (one authority, s27); never consumes `IR_t.pat_static` blindly (BINOP operand dropped pre-evaluation, s29); the ALT/CAT sharpening is PROVED by the census over glue reads, never asserted (ZTOS: the arming frontier is the READERS).
2. **The closed re-entry edge inventory** (EARN-3 deliverable; HOME GATE line 7, minted s31): backtrack β per choice class (arena pin W5) · ω unwind · FENCE whack · scanfail · ABORT drain · unanchored retry bump · **NRETURN · direct Goto `:<C>`/CODE() · SETEXIT** (Ch.9/19 non-local transfers — named in no seat file before s31). One missed edge = the FF-0 class.
3. **GC coverage** (RBX X-1 / RC-8a): arena records hold DESCR refs; the RTCC block is scanned by nothing at HEAD; latent now, LIVE on arg-tier claim.

**Explicitly NOT solved by the scheme** (so nobody bills these to it): LOWER Defects A/B, C-9 `start` displacement + POS/RPOS anchor, 061, capture-after-variable-length (all seated in HOME-LOWER); FUNC-11 include-scoped CAPACITY (RBX X-2 — allocation, not addressing); unbounded growth itself is BOUNDED, not eliminated (p.123 stack-overflow class stays oracle-parity xfail; the arena needs X-0's overflow/growth story); the parked RTX perf ladders.

**R13–R15 note:** δ(r14) restoration at backtrack rides the choice record by design; Σ(r13)/Δ(r15) save-restore across a NESTED match is a crossing row EARN-0b verified only for rsp/rbp — one-measurement addendum minted (re-run `161_pat_defer_fn_nested_match` watching r13/r15).

## 3 · RECONCILIATION: FIVE UNSEATED ITEMS (now assigned) + TWO DOC DEBTS

Accounted correctly at s30 mint: LADDER W→EARN · AB→P3 · RTX-FUNC≈AB · FUNC-11→X-2 · RC-8a→X-1 · MON-CAP→B-5 (verbatim incl. the table-assign VALUE event) · C-9/061/test_string→L-3/4/5 · m4-dark harness→B-0 · D12/D13→W-2 · demo 2/15→P2 meter (FF-0 prediction) · M-1..M-7 spirit→EARN-7/10/11 + GATE 3/4 · **LADDER PB CLOSED pre-consolidation** (all `[x]`, BB 07e; PLAN row stale by design — do not reopen).

**Unseated, now assigned (master ledger minted in GOAL-SN4-HOME.md):**
1. **LADDER KW** (BB KW-0..6) → ADOPTED P3.5; acceptance = xc318 keywords-12 green both modes.
2. **DEFER LATCH** (`g_star_peek` per-site; RTX row) → ADOPTED P1-concurrent (pattern_match.c only); witnesses 140/141 (RED m3 rc=139 / m4 PASS) promoted to named-witness layer (B-7(iv)). Manual-proven structurally wrong (Ch.7 p.86 + Ch.9 pp.122–3).
3. **MECH S-LADDER** (M-SLEN S0–S5) → RIDES EARN-6; S4's register-only MATCH_BEGIN α is EARN-6's implementation arm.
4. **CLIMB C-10/C-11** → ADOPTED P3.5; C-11 doubles as the EARN reentrancy stress suite (EVAL/CODE re-entry).
5. **RTCC residue** → RC-8b/8c ADOPTED at RBX X-5 (gated on X-1); RC-5/RC-7 PARKED pending Lon + X-1. RTX instrument debts → BOARD B-8; BREAKX witness mint → B-7(iv).

**Doc debts closed s31:** R13/R14/R15 added to the HOME register contract (+ nested-match verify obligation); REGISTER-LAYOUT.md bannered (r12=ζ row STALE — r12 is the pending-arena TOP; full 16-row map = X-0's deliverable); `g_blob_ctx`/`rt_blob_ctx_ptr` grep==0 added to HOME GATE 4 (largely discharged by `0970838f` g_zctx base stack — gate verifies); collision pin extended to the ZCTX/guard pair (emit.cpp:2373/2806); Milestone-2 explicitly out of HOME scope.

## 4 · PLAN SCRUTINY — WHAT TO PRESERVE, WHAT TO WATCH

**Preserve:** BOARD's zero-compiler-bytes referee separation · census-before-frame-moving standing law + instrument-expiry rules · the ordering laws (W-5 flip gated on EARN-1+3 — the old 19-SEGV+7-HANG correctly reframed as MISSING FRAMES, measured never assumed; P3 serialized full-runway) · collision pins named in advance with the arena layout given ONE owner (CAP-SYM lesson) · **the five oracle pins landed in corpus BEFORE implementation** (the single best methodological feature of the plan).

**Watch:** (a) floors drift mid-P1 — a seat landing a floor-moving repair should post the BY-SET delta to BOARD's file in the same push; (b) every number states its RTCC arm until W-6 seals default-ON; (c) EARN-8 (STATEMENT losing its license) is the scariest single change — M-1b-class statement-scope state (δ0, flag) must be re-homed before the frame is refused; correctly parked to P3 with EARN-7 measurements in hand.

## 5 · SESSION NOTES

Repos at audit: SCRIP `fc5b0754` (3180 commits) · corpus `ff51ccbe` · `.github` `58150792` · x64 not cloned (not needed — zero code). SPITBOL manual v3.7 (spitbol/spitbol-docs) fetched to `/home/claude/refs/`; Ch.6/9/18/19 read for every construct cited. First clone attempt of SCRIP/corpus raced-empty in background; foreground re-clone clean — do not background parallel clones. Context budget: audit consumed ~70% of one Fable-5 window; the six goal files total ~450KB — future consolidated seats should extract cursors + open rungs, never read bodies whole.
