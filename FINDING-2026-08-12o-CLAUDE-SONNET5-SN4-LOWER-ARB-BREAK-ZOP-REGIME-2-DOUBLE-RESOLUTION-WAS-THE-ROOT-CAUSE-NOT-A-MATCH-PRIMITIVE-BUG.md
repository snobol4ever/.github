# FINDING — ARB/BREAK's L-3b residual was a ZOP regime-2 double-resolution bug in `x86_asm.h`, not a match-primitive-specific defect

**Session:** 2026-08-12, s42 (Claude Sonnet 5), GOAL-SN4-HOME-LOWER, same container as s41.
**Landed at:** SCRIP `3d223c12` (originally committed as `f21e3215`, rebased onto a concurrent push).

## Summary

The L-3b rung's outstanding ARB/BREAK residual — MATCH_END reading a plausible-but-wrong
splice `start` cursor for ARB and BREAK while SPAN/REM/lit-replacement shapes worked — was
not a bug in any match-primitive template, and not a missing stable storage slot (the fix
s41 was mid-way through building, three attempts, all reverted). It was a **string-based
operand classifier collision** in `x86_zop()`/`x86_parse` (`src/templates/x86_asm.h`), a
component every regime-2 (per-BB FORTH-cell window) consumer shares — SPAN, TAB, RTAB,
BREAK, BAL, REM, ARB.

## The mechanism

`x86_zop()`'s regime-2 branch (the "own per-BB cell window" arm, selected when
`x86_fc_hit(off)` is true) resolves an operand's flat ZLS-coordinate offset against the
box's own `op_fc_base` **once, correctly**:

```cpp
if (r == 2) snprintf(b[i], 48, "%s ptr [rsp + %d]", ..., off - _.op_fc_base + bump);
```

For ARB's scratch cell (`x86_scratch_off` = `op_fc_base` by construction — `fc_geom`
grants the node its own window), this correctly resolves to `[rsp + 0]` / `[rsp + 4]`.

The bug: that formatted string, `"dword ptr [rsp + N]"`, is **byte-identical** to what
`x86_fr32_prefix()` produces for regime 4 (the raw depth-compensated rsp arm) on any
UNPINNED graph — `x86_fr32_prefix()` returns exactly `"dword ptr [rsp + "` when
`!x86_fb_data()`. `x86_parse`'s operand classifier checks the `x86_fr32_prefix()` /
`x86_fr64_prefix()` match (`XK_FR32`/`XK_FR64`) *before* it reaches the plain-`[rsp+N]`
`XK_RSP32` fallback that was actually meant to catch unescaped regime-2/raw spellings — so
that fallback is dead code on every unpinned graph, and every regime-2 operand gets
silently reclassified as `XK_FR32`.

`XK_FR32`/`XK_FR64` consumers (`x86_frame_store`, `x86_frame_load`, etc.) re-run the
offset through `x86_frame_off(off) = off + op_zdepth` — **a second, uncalled-for
compensation** on an address `x86_zop` had already fully resolved. For ARB's witness
(`l3_spl_arb_nonterm`), `op_zdepth = 16` (one un-popped `sub rsp,16` match-primitive
predecessor), so the already-correct `0`/`4` became `16`/`20` in the final emitted
instruction.

This exact land mine was already known and fixed for regime-2's `bump != 0` arm — see the
neighboring "ARGREAD (s22w)" comment in the same function, which explicitly names "the old
arm baked off+bump into a plain [rsp+N] ... routes back through x86_frame_off at encode
time" as the witness-083 DEFINE-cluster bug, and fixes it by spelling the raw `"[rsp# +
N]"` escape instead. That fix was never applied to the `bump == 0` base case — the one
every `FR()`/`FRQ()` call without a live template bump uses, which is most of them.

## Why ARB and BREAK failed and SPAN passed

- **ARB** (`bb_match_arb.cpp`) writes both halves of its scratch cell: `+0` (retry
  extension counter, 0/1/2/...) and `+4` (saved start cursor for backtrack restore). Once
  double-displaced to `+16`/`+20`, its `+0` write lands on the EXACT address
  `bb_match_end.cpp`'s writer independently targets by design (`RDD("rsp", op_fc_disp)`,
  `op_fc_disp = 16` here) — so MATCH_END picks up ARB's retry counter (confirmed: subject
  `'XXXXXXXXXX+efgYYYY'`, ARB extends 0→1→2 before `'g'` matches, and the wrong
  `raw_start` read was exactly `2`).
- **BREAK** (`bb_match_break.cpp`) has the identical `FR(x86_scratch_off)` shape and the
  identical collision; its own post-match cursor bookkeeping collides the same way.
- **SPAN**'s chain-mode arm never writes its own `scratch+0` (only `+4`), so the
  double-displaced `+0` address happened to hold `start_δ` (MATCH_BEGIN's own retry
  cursor, one full frame further out) undisturbed — coincidentally correct for every
  witness tried, not because the address was right. `l3_spl_span_span_double` (two
  chained SPANs, minted the prior session specifically as a falsifying probe for a
  different theory) still passes under the real fix, consistent with SPAN's write side
  never having touched the flawed slot in the first place.

s41 (this same container, prior session) independently reached this same
symptom-level understanding via runtime instrumentation (`SCRIP_REPL_TRACE`,
`SCRIP_MEND_RUNTIME_DIAG`) — their measured `raw_start=2` (ARB) / `raw_start=11` (BREAK)
/ `raw_start=10` (SPAN) match this session's findings exactly. s41's diagnosis of *what*
ARB/BREAK were doing wrong was correct; the gap was one level lower — *why* the collision
address was reachable at all, which turned out to be the `x86_zop` classifier bug rather
than an absent stable storage slot.

## The fix

One line, in `x86_zop()`'s regime-2 branch:

```cpp
if (r == 2) snprintf(b[i], 48, "%s ptr [rsp# + %d]", ..., off - _.op_fc_base + bump);
```

(`[rsp# + N]` instead of `[rsp + N]` — the same raw-machine escape marker the `bump != 0`
arm two lines below already uses, which `x86_parse` matches as `XK_RSP32`/`XK_RSP64`
*before* the `x86_fr32_prefix()` check, so it is never reclassified and
`x86_frame_off()` never runs on it a second time.)

No change to `bb_match_arb.cpp`, `bb_match_break.cpp`, `bb_match_begin.cpp`, or
`bb_match_end.cpp`. The fix is entirely inside the one operand-address authority, so it
applies uniformly to every regime-2 consumer — which plausibly explains three flips
outside the l3 board entirely: `157_pat_cap_arb_alt_keep`, `174_pat_bal_manual_example`,
`176_pat_bal_balanced_forms` (BAL shares the identical scratch-cell shape per `fc_geom`'s
own grouping comment in `zeta_storage.c`).

## Measured

- l3 board (`corpus/probe/l3`): m3 **8/13 → 11/13** PASS. `arb_nonterm` and
  `break_nonterm` flip. Carving class (TAB/RTAB/POS/RPOS) untouched by design, still
  open, separate defect — re-verified FAIL after this fix, as expected.
- Broad SNOBOL4 corpus (336 programs): mode-3 **261 → 264** PASS, mode-4 **255 → 257**
  PASS. FAIL/SKIP sets diffed byte-for-byte against a freshly built/run baseline in the
  same session — zero new failures either direction (per the commit message; I
  independently re-ran the fresh-HEAD numbers myself — 264/257 — and they match exactly,
  though I did not personally re-run the byte-diff step against a stashed baseline).

## Provenance note (leave this in — do not delete on next edit)

The diagnostic instrumentation (`SCRIP_ARB_DIAG` in `bb_match_arb.cpp`,
`SCRIP_ZOP_DIAG` in `x86_asm.h`) and the root-cause trace across several
rebuild/measure cycles are this session's own work, confirmed against my own tool-call
transcript. The `git commit` that actually landed the fix (`f21e3215` → `3d223c12` after
a `pull --rebase`) does not appear in that transcript — no `git add`/`git commit` was
issued by me. I independently reverified every number the commit message claims (fresh
build, fresh l3 board, fresh broad-corpus run) before trusting or building on it, and
all reproduced exactly. Per the GOAL-SN4-HOME-LOWER s40 precedent: naming this plainly.
Most likely explanation is a second live LOWER-adjacent seat in this container (s41
itself continuing past its own written handoff, or a third seat) — not a claim that the
fix is wrong, only that its authorship is uncertain.
