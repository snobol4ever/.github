# HANDOFF 2026-06-06 — Opus 4.8 — SNOBOL4-BB: REG-RO + SNO-HY-1 + SNO-HY-2a

**SCRIP origin/main = `178b6e8`** (3 commits this session: `ba7622c` REG-RO, `7a24653` SNO-HY-1, `178b6e8` SNO-HY-2a). Single source of truth: GOAL-SNOBOL4-BB.md frontier + 2026-06-06 session-end watermark. This doc is the pointer + the things a cold session needs fastest.

## What landed
1. **REG-RO** — r10 eradicated from SNOBOL4 pattern family; REG-FENCE TIER2 flipped HARD r10==0. Cursor is r14d, full stop; xa_flat epilogue reads it directly (both media, same byte length, literal offsets untouched).
2. **SNO-HY-1** — IR_PAT_BREAKX split out of IR_PAT_BREAK. BREAKX β regenerated manual-faithful incl. exhaustion cursor-restore the fused arm leaked.
3. **SNO-HY-2a** — IR_PAT_RTAB split out of IR_PAT_TAB; sval=='r' sentinel-string discrimination killed.

## The 13-site IR-split recipe (now proven twice — reuse verbatim for future de-crams)
IR.h (END of SNO block) · scrip_ir.c names · lower.c kind-select (KEEP field encodings verbatim) · lower.c:145 predicate · IR_interp.c case-label SHARE (= m2 byte-identical) · emit_bb.c is_pat_chain_elem · emit_bb.c FILL · emit_core.c dispatch (NOTE: emit_core.cpp is a wrapper that #includes emit_core.c — the .c IS live) · bb_templates.h · Makefile src+rule · emit_per_kind_audit.c row+seed · prove_lower2.c kname (dump_pat asserts NODE COUNTS only — kind renames are proof-safe).

## Flagged, with proof status
- **bx2** `'a.b' (BREAKX('.') 'zz' | 'a.' . W)` → m4 NOMATCH vs m2 `a.` — PRE-EXISTING (stash-proven). Alt-driver arm-ω cursor contract; fold into SNO-HY-5.
- **SNO-HY-2b hazard** — by-var SPAN reaching bb_pat_span.cpp would cset-match the variable NAME; only upstream admission filters.
- **REG-RO residuals** — dead xa_flat prologue r10 load (BINARY twin = movabs &Δ with hardcoded out_site offsets); BINARY call fn-ptr movabs bakes (REG-RO-2 if wanted).
- **M2-ARBNO-SHY** — still awaits Lon (moves broad counts).

## Container facts (cheap to re-learn the hard way)
- GATE-3 floor THIS env = **135/280** (stash-verified twice; the 143 watermark was the prior container).
- binary-arms audit FAILs pre-existing (xa_wasm_main NO-ARM; BB-FIXUP cursor drift) — stash-proven, not a session regression.
- SPITBOL manual PDF absent from uploads + corpus this session; re-upload for deeper grounding.
- Perl batch edits: a trailing `\n` in a -pe match deletes the whole line silently; ALWAYS verify-grep counts per file afterward.
