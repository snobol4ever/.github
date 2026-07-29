# FINDING-2026-07-29-CLAUDE-SN4-RTX-ARCH-REGISTER-TABLE-STALE-R12-FREE-AND-FRAME-BASE-PER-GRAPH.md

**Session:** s205 · **Date:** 2026-07-29 · **Author:** Claude Sonnet 4.6

## THE FINDING

`ARCH-SNOBOL4-RTX.md §2` register table carried two stale entries that would
misroute any RTX asm or template work touching the frame base or r12:

| Entry in §2 | What the tree actually says |
|---|---|
| `r12 = conditional-assignment stack pointer` | **r12 is FREE.** `ZC_FRAME_R12` was DELETED outright at ZR-RSPRBP-1 (Lon directive 2026-07-27, SCRIP `da8c2347`). It had zero `#if` consumers. The ζ basis set is CLOSED at RSP and RBP. |
| `rbp = ζ frame base` | **Per-graph, not fixed.** Frame base is `x86_fb_pinned()` = `emit_rec_pin()` (ZETA-FB-2, s160): **rbp** for suspended generators / pattern blobs / deep-arrival graphs (prologue seeds `mov rbp,rsp`); **rsp** for depth-static determinate graphs (free GPR; `op_flat_disp` compensation). ONE selector, both media. |

Verified from live tree: `src/templates/x86_asm.h:347-361` (`x86_zr`, `x86_fb`,
`x86_fb_pinned`, `x86_frame_off`) and `src/contracts/zeta_choices.h:177` (ZC_FRAME_R12 deletion note).

## WHY IT MATTERS FOR RTX

Phase-1 RTX asm routines keep C signatures and rely on SysV callee-save to
preserve blob pins across the call boundary.  Any hand-written asm that references
r12 as a pin or spells a fixed frame base will encode the wrong thing silently —
the compiler does not see `.S` files.  The §2 table is the register contract every
RTX rung reads first; if it names a deleted register as a pin, the rung is mis-aimed
before it writes a line of asm.

**Correct spelling for frame-relative access in any RTX or template context:**
`FR(off)` / `FRQ(off)` via `x86_asm.h` — they resolve to `x86_fb()` which calls
`x86_fb_pinned()` and names the right base per graph.  Never hardcode `[rbp+off]`
or `[rsp+off]` directly.

## ARCH §2 CORRECTION NEEDED

The register table in `ARCH-SNOBOL4-RTX.md §2` should be updated:
- Strike `r12 = conditional-assignment stack pointer` — r12 is free (no RTX pin role).
- Replace `rbp = ζ frame base` with `rbp = ζ frame base IN PINNED GRAPHS ONLY
  (suspended generators, pattern blobs, deep-arrival); rsp arm for determinate graphs;
  one selector x86_fb_pinned() — use FR()/FRQ(), never hardcode the base`.

## THE SESSION THAT FOUND IT

s205 read `ARCH-SNOBOL4-RTX.md §2` as orientation, then read `x86_asm.h:347-361`
and `zeta_choices.h:177` to verify the register contract before writing any asm.
The discrepancy surfaced immediately on the `grep -n "inline.*x86_fb"` step that
ARCH §7 step-1 mandates.  Cost: ten seconds.  Would have cost a rung if skipped.
