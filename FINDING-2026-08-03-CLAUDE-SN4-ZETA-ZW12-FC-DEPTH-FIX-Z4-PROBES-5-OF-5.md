# FINDING-2026-08-03-CLAUDE-SN4-ZETA-ZW12-FC-DEPTH-FIX-Z4-PROBES-5-OF-5

**Session:** s42 (2026-08-03, Sonnet 4.6)
**SCRIP commit:** `9a89ccec` · **Corpus commit:** `d871b64e`
**Gate before:** Z4 probes 3/5 (z4_span SEGV, z4_capture SEGV)
**Gate after:** Z4 probes 5/5 · crosscheck m3 281→295 · m4 274→288 · BY-SET zero regressions

---

## Root cause: two ZW-12 depth model bugs for FORTH-cell pattern boxes

### Bug 1 — MATCH_END: _fci not subtracted from zd

The ZW-12 canonical match frame depth model decremented `zd` by `ZW_FRAME_TOTAL=64` at MATCH_END.  That constant accounts for `push rbp (8) + sub rsp,ZW_FRAME_K=56 (56)`.

But FORTH-cell pattern boxes inside the run (SPAN, BREAK, TAB, RTAB, ARB, REM, BAL — each with `zd_k=16`) also emit `sub rsp,16` at alpha inside the match frame.  The `lea rsp,[rbp-8]; pop rbp` whack releases ALL of those cells along with the frame overhead.  Without accounting for them, `zd` remained inflated by their sum (`_fci`) after MATCH_END, so `gpop` at STATEMENT_END over-released by `_fci` bytes into the caller frame.

**Witnesses:**
- `z4_capture`: single SPAN inside the match frame. `_fci=16`. gpop was 160 (should be 144). Over-release of 16 bytes corrupted the COND→SAVE cross-depth read slot, causing wrong capture output and crash.
- `z4_span` single match: same shape, rc=139 (exit segfault after correct output).

**Fix:** compute `_fci = sum(zd_k for run members between hpos and END)` and subtract `ZW_FRAME_TOTAL + _fci` at MATCH_END.

### Bug 2 — MATCH_BEGIN wpop: post-ZW `zd` used instead of pre-ZW `zdh`

MATCH_BEGIN's ω exit is the pattern-exhausted fail path.  It fires AFTER the whack restores rsp to the claim base — at pre-ZW depth `zdh`, not the inflated post-ZW `zd`.  The wpop formula `zd - K + kc` ran AFTER `zd += ZW_FRAME_TOTAL`, so wpop was inflated by 64 (for the scan case: 272 instead of 208).

On each failed scan position, `add rsp, 272` released 64 extra bytes into the caller's frame.  The second scan iteration jumped to `rip=0x1` (a descriptor tag in the over-released region).

**Witnesses:**
- `z4_span` scan loop (`S BREAK SPAN =; :(SCAN)`): first iteration correct output, second iteration `rip=0x1` crash.

**Fix:** use `zdh` (saved before `zd += ZW_FRAME_TOTAL`) for head-node wpop/gpop when `zws && r == hpos`.

---

## Probe results

| Probe | Before | After |
|-------|--------|-------|
| z4_arith | OK | OK |
| z4_span | SEGV | **OK** |
| z4_arbno | OK | OK |
| z4_capture | SEGV | **OK** |
| z4_fib | OK | OK |

## Crosscheck

m3: 281P/25F/11T → **295P/22F/0T** (+14 pass, 11 timeouts resolved)
m4: 274P/32F/10T → **288P/28F/1S** (+14 pass)
BY-SET: zero regressions.  All new passes are pattern-statement programs with SPAN/BREAK/TAB inside the ZW-12 canonical frame.

## Files changed

`src/emitter/emit.cpp` — one site, two related fixes in the ZD-plan MATCH_END depth subtraction and head-node wpop assignment.
