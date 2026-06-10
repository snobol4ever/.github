# HANDOFF — BB-FIXUP 44th attended run (2026-06-10, Fable 5)

## What landed
- **SCRIP 3cfd576** — bb_callee_frame.cpp lap-2 regeneration 20→2 (CV10 prep relocation: own bb_prepare IR_CALLEE_FRAME block, op_parts ival[0..2]=arity/nlocals/NC; R2 inlines; mt 3→0; CV8 fence; R1 terse; one lazy-IF return). Proof: instruction-stream byte-identity ×4 prolog probes (sole delta = R1 comment), sa=0/1/2/4 LIVE, m2=m3=m4 ×4. GRAND 2249→2231 exact closure.

## Inherited red (NEW Lon verdict item, owner SNOBOL4-NL)
- pat rung M4 16/3 under NL=1 (alternation trio 050/051/054); SCRIP_NL=0 → 19/0 exact. Cause b11a963 (sno NL default flip). Third NL silent-empty-alternation instance. Gate-gap: the flip's evidence bar lacked the pat-rung M4 leg. This run certified everything on both legs.

## Deferred / routed
- **bb_call.cpp** (cursor passed, [S] sharpened): FIX-3-i is the next-session entry at full headroom. Key scoping: write lowering now in nl/lower_icon_nl.c chains arm (dval=1.0); slot-vs-expr classification is an EMIT-time fact → likely bb_prepare (CV10) with LOWER carving kinds only — state-or-pin at execution; kind-admission census in tracker; write("lit") silent-decline shape needs an A/B probe.
- **bb_call family ×4**: FIX-7d-excluded, fresh counts noted (fn=4, proc_staged=25, userproc=6, write_slot=32).
- **bb_catch.cpp**: UN-TICKED, conversion-gated on FIX-9 Cat-B XK_RIPLBL + the unpinned term-delivery design (shared bb_resolve). MEDIUM_TEXT admission is LOAD-BEARING pre-R3. FINDING: mode-3 catch native is TEXT-only today, ungated (bb_pattern_* sibling).

## State
- Cursor: `# CURSOR: bb_cell_call.cpp` (a bb_zn reader — likely the bb_callee_frame recipe applies).
- Ceiling: 115/108/7/GRAND 2231. Floors unchanged otherwise.
- SCRIP @ 3cfd576 · .github @ watermark commit. Session-env replay: apt libgc-dev + build_scrip.sh + make libscrip_rt confirmed again.
