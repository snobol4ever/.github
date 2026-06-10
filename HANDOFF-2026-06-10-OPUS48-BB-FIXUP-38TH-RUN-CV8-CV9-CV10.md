# HANDOFF 2026-06-10 — BB-FIXUP 38th attended run (Opus 4.8)

**SCRIP @ 7371575** (my landing; foreign 15608cf FULL-13/lower_icon above it, sanity-passed) · **.github @ the 38th-run watermark commit**.
**Cursor: bb_assign_frame.cpp (UNMOVED — this run was Lon-directed out-of-cursor bb_alt redo).**

## What happened
Lon directed a redo of the 37th-run bb_alt work and carved THREE new CONVERSIONS (verbatim rulings, now specified in GOAL-BB-FIXUP.md CONVERSIONS list):

1. **CV8 — PLATFORM IF STATEMENTS PRESERVED.** `if (PLATFORM_*)` is a separate if STATEMENT in `*_str`; one return inside it + the empty fallthrough; the platform predicate never goes inside IF() string combinators. X86 stays fenced from JVM/.NET/JS/WASM. (60a22b5 had dissolved the fence into the lazy-IF chain — corrected.)
2. **CV9 — NO PARAMETERS.** All `bb_*_str` AND the extern-C wrappers parameterless; dispatch = `bb_prepare(nd); bb_x();` (bb_arith precedent). Census: 29 template files still parameterized / 86 clean.
3. **CV10 — NO IR-GRAPH ACCESS FROM TEMPLATES.** Zero pBB / `_.node` / g_emit_cfg / bb_operand_aux_get / IR_t anywhere in a bb_*.cpp (top level or helpers). By template-call time everything is in g_emit as scalars/collections; ALL graph inspection — admission included — lives in driver-side `bb_prepare` per-kind blocks (extend sm_emit_t as needed). Zero `IR.h` include surface = completion sign. The HARD form of EMIT-BLIND.

## The landing (SCRIP 1a038c0 → 7371575)
bb_alt.cpp 11→3. bb_alt_n/bb_alt_arm DELETED; bb_prepare IR_ALT block delivers op_parts_n/tag/ival/str (NEW `int64_t op_parts_ival[16]` in sm_emit_t); emit_core IR_ALT case = prep + parameterless call; template = `_.op_*` reads behind the restored platform fence. PROOF: asm IDENTICAL ×2 LIVE probes (`every write(1|2|3)`, `every write("aa"|"bb")` — /tmp Icon shapes, recreate on arrival), diff EMPTY (comment unchanged — not even the R1 delta); m2=m3=m4 parity; full floors held; re-certified twice (concurrent 213e6cb mid-run; idle-window 15608cf at handoff).

## ⛔ KEY FINDING — CV10 changes the [S] landscape
CV10 RESOLVED bb_alt's [S] (arms[i]->op inquiry) WITHOUT the unpinned IR_ALT_LITERAL LOWER split — the inquiry relocated to the driver, where it is sanctioned. Many standing [S] eb/nw entries (bb_atom_string eb=28 · bb_is_cmp eb=34 · bb_list eb=8/nw=12 · bb_io eb=6 · bb_aggregate_nb · …) may likewise be CV10 driver-prep relocations, NOT LOWER-split waits. RE-READ each [S] on arrival. The LOWER split remains the answer only where inquiry IS lowering (shape selects a DIFFERENT four-port logic — ONE-IR-ONE-LOGIC), not mere operand delivery.

## State
- NO-GROWTH CEILING: **115 files / 108 dirty / 7 clean / GRAND 2488** (−8, sole mover bb_alt, exact arithmetic closure).
- bb_alt residue rp=3 = FOR-lambda returns + CV8 fence second return — sanctioned forms; **rp re-scope JOINS lv/nw as one counter-scope Lon verdict** (lv→top-level-only? rp→exclude lambda/platform returns? nw→widen to subscript forms?).
- Pre-existing, A/B-proven, untouched (law 5): hello-langs rebus ROW-DRIFT (not a floor gate; possibly env); smoke_compile harness make-target MISSING (37th-run flag).
- Session-env: fresh container needs `apt-get install libgc-dev` before build_scrip.sh links.
- Outstanding verdicts: standing 6 · bb_arith dead-dispatch retirement · ro_seal_q/ro_seal_str CV7 directive naming · counter-scope trio (lv/rp/nw).

## Next session
Cursor stop **bb_assign_frame.cpp** (TOTAL=66: bp=17 rp=27 hc=13 mt=1 sd=3 cl=4 ml=1). A natural CV4/CV8/CV9/CV10 showcase: baf_* parameterized helpers, an IF(MEDIUM_TEXT) head-wrapper, 17 frame/reg bypass calls — and its `_.op_a_*` operands are ALREADY driver-delivered (prep predates CV10), so the file may reach near-clean with no [S]. Apply ALL CONVERSIONS CV1–CV10 in one pass per OPERATING MODE v3.
