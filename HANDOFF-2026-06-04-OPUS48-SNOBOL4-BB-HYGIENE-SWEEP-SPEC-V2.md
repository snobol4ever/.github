# HANDOFF — 2026-06-04 — SNOBOL4-BB — HYGIENE SWEEP + TEMPLATE SPEC v2 (Lon directive)

**Repos at handoff:** SCRIP pushed (hash in goal-file watermark); .github pushed. Trees clean.
**Gates at handoff:** sno m2 7/7 HARD · m3 6/6 · m4 6/6 — pl m2 5/5 HARD · m3 4/4+1exc · m4 5/5 — icn m2 12/12 HARD (m3/m4 5/12 pre-existing; floors MODE3_MIN=1 / MODE4_MIN=0).
**ENV:** `apt-get install -y libgc-dev`. Cold start MUST run `rm -f out/libscrip_rt.so obj/*.o && make libscrip_rt` or every mode-4 reports `<mode4-build-failed>`.

## ⛔ TEMPLATE SPEC v2 — Lon, 2026-06-04 — requirements for EVERY BB template
1. NO local variables.
2. ONE return statement per PLATFORM, returning ONE concatenated string.
3. IF() and FOR() string functions for ALL conditional and loop constructs.
4. ONE source line per ONE x86 asm line — never stack multiple asm lines on one source line.
5. NO PORT_ALPHA / PORT_BETA / PORT_GAMMA / PORT_OMEGA spellings — REAL Greek characters (α β γ ω).
6. NO MEDIUM_TEXT / MEDIUM_BINARY at template top level — make functions that hide them.
7. ERADICATE all emit_fmt() calls.
8. REMOVE ALL C source comments completely. [OPEN QUESTION for Lon: RULES.md still names the 200-char `/*---*/` separator as the ONE permitted comment — confirm whether separators survive v2.]
9. NO blank lines.

**Strategy (Lon, verbatim intent): REGENERATE each template whole from spec — do not make 100 edits to code that should have been generated in this form already.**

## Session result (spec-v1 mechanical sweep — superseded by v2, not wasted)
- Batch audit one-liner mapped all 91 BB .cpp: 54 grep-clean / 37 dirty on v1 rules (bb_bin_t, pBB->, lang guards, vstack, raw-byte producers, >200-char lines, prose comments).
- SCRIP commits: `2af3880` (prose comments stripped from bb_choice/conj/goal/ite/pat_alt/pat_cat; tracker added), `cd577ed` (all >200-char lines wrapped via adjacent-literal splits, emitted text byte-identical).
- Tracker: `SCRIP/BB-REVAMP-TRACKER.md` — RESET to v2 semantics (all `[ ]`); v1 work preserved as per-file annotations. A box is ticked ONLY when the file is regenerated to v2 and gated.

## Facts that cost time (do not re-derive)
- Mode-4 failing across the board == missing `out/libscrip_rt.so`. Build it before diagnosing anything else.
- `bb_call.cpp`: pBB refs + `a0->t ==` AST-walk chain in emitter code (RULES violation) + 3 bombs. Needs a dedicated pass.
- `bb_builtin_*` family (13 files): PBB + `bytes()`/`u32le()` raw-byte producers + prose — heaviest regeneration targets.
- PBB-flagged non-builtin files: bb_assign_frame / bb_assign_frame_ref (4 bombs each), bb_call_proc_staged, bb_call_write_slot, bb_every, bb_return.
- awk `length` counts BYTES in C locale; Greek chars inside comment strings skew counts (bb_scan_match was a true 206).
- Icon m3/m4 5/12 FAILs pre-date this session (floors set accordingly). String-literal splits cannot alter emitted bytes — sno m4 6/6 confirms.
- The v1/v2 spec gap root cause: GOAL-SNOBOL4-BB.md was read TRUNCATED (lines 90–606 elided by the viewer). Next session: read it IN FULL before touching any template.

## Next session
1. Read GOAL-SNOBOL4-BB.md IN FULL. Read this doc. Spec v2 governs.
2. Regenerate ONE template to v2 (suggest `bb_pat_break.cpp` — smallest fully-real file) as the reference form: helpers hiding MEDIUM_*, real Greek port producers, IF()/FOR() combinators, 1 src line = 1 asm line, zero locals, one return per PLATFORM. Gate sno m2 7/7 HARD, commit.
3. Regenerate down `SCRIP/BB-REVAMP-TRACKER.md`, builtin family last.
