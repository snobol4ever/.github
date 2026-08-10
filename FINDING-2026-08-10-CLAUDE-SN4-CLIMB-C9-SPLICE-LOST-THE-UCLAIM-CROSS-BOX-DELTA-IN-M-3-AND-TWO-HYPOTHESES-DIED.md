# FINDING 2026-08-10 — SN4 ζ-CLIMB C-9: THE SPLICE LOST UCLAIM'S CROSS-BOX DELTA IN M-3, AND TWO HYPOTHESES DIED ON THE WAY

**Goal:** `GOAL-SN4-ZETA-CLIMB.md` rung **C-9 REPLACEMENT + SPLICE**. Entry per s34 cursor: `062_capture_replacement`.
**Repos at open:** SCRIP `c7e085fd` · corpus `9fb2e019` (both AHEAD of the s34 cursor's `6ffa57fe`/`f46d3ebe`; capture family re-proved with **zero drift**).
**Status:** ROOT CAUSE MEASURED AND PROVEN. **No fix landed** — the fix is M-3 residual debt and belongs to MECH (cross-request below).

## THE DEFECT

`SUBJECT ? PATTERN = REPLACEMENT` overwrites the ENTIRE subject with the replacement string instead of splicing only `[match_start, match_end)`. Both modes, m3 ≡ m4 (m3 glue exonerated per METHOD §6).

MONITOR-FIRST bracket (`PARTICIPANTS="spl scr"`, 062):

```
DIVERGE step 4, stno=2, 062_capture_replacement.sno:3   X 'world' = 'there'
  last agree: step 3  LABEL stno=2
  spl: VALUE X = STRING(11)='hello there'
  scr: VALUE X = STRING(5) ='there'
```

`STRING(5)` is the replacement's own length — the write is the replacement verbatim.

## ROOT CAUSE

The C of record `c_rt_match_replace` is CORRECT (`nlen = start + rlen + (slen - end)`, three memcpys, matches manual Ch.6 p.72-73). The defect is in the ARGUMENTS. In-tree tracer `SCRIP_REPL_TRACE=1` reads the sink directly:

```
[REPL] name=X slen=0 start=0 end=0 rs="XY" rlen=2      <- ALL FOUR frame-sourced args are zero
```

`slen=0, start=0, end=0` ⇒ `nlen = rlen` ⇒ whole-subject overwrite. The selectivity names the mechanism:

| arg | source | result |
|---|---|---|
| `rdi` name | `ROQ(0)` — rip-relative | ✅ correct |
| `r9` replacement | ζ-cell `ZOPQ(1,0)` (ZD-5 MATCH-SPINE, by address) | ✅ correct |
| `rsi/rdx` subject | `FRQ(op_sa)`, `FRQ(op_sa+8)` — FLAT | ❌ zero |
| `ecx/r8` start,end | `FR(op_off)`, `FRQ(op_off+24)` — FLAT | ❌ zero |

Everything on a depth-immune path survives; everything on the flat path is short by the intervening carve. Emitted asm shows it exactly (P4, ctx_restore → splice):

```asm
mov  r13, [rsp + 48]     # outer_Σ   <- at ctx_restore, rsp+48 IS outer_Σ
call rt_match_ctx_restore
n11_lit_string_α:
sub  rsp, 16             # replacement mints its OWN ζ-cell, leaves it LIVE for the splice
n12_match_replace_α:
mov  ecx, [rsp + 48]     # start     <- same literal offset, RSP now 16 lower
```

`bb_match_replace` reuses head-relative offsets planned at the head's RSP, but executes after the replacement chain carved on the FORTH spine. By the ZTOS-2 law (`x86_asm.h:503`, *"a box compensates for exactly what IT carved"*) `op_zdepth` for the splice node is 0 — it carved nothing — so no compensation is applied.

**Why it is a REGRESSION and not a model gap.** Same-program A/B, committed artifact vs current compiler:

| arg | committed `062_capture_replacement.s` | current HEAD |
|---|---|---|
| sub_lo | `[rsp+176]` | `[rsp+160]` |
| sub_hi | `[rsp+184]` | `[rsp+168]` |
| start | `[rsp+64]` | `[rsp+48]` |
| end | `[rsp+88]` | `[rsp+72]` |

The last honest regen emitted the CORRECT offsets. The compensation was removed by **`1351d299` ZETA-MECH M-3 — UCLAIM physical deletion** (2026-08-08, own commit message records the crater: probes m3 135→0, m4 132→0). `x86_frame_off`'s surviving comment names precisely what died:

> UCLAIM (wholesale flip): on the rsp arm a flat off whose range the current run CLAIMED resolves through the owner table — **(off − claim_base) + (delta_out(reader) − delta_out(owner))** — this is the ONE execution-order offset function converting every FR/FRQ/FRQB reader at once, zero template edits.

`delta_out(reader) − delta_out(owner)` IS the cross-box term. `15d2af87` ("M-3 FIX: restore zd depth accumulator") restored the **intra-box** sliding offset and recovered the bulk of the crater (135/136). The **cross-box** term was never replaced. The residual casualties are exactly the flat readers whose slot OWNER is a DIFFERENT box — the splice reading head slots across the replacement chain's carve.

## TWO HYPOTHESES DIED

1. **"Prefix dropped, suffix kept."** 062/063 both showed the replacement alone, and both have empty suffixes — which reads as a prefix bug. FALSIFIED by probes with non-empty suffix: P1 `abc DEF ghi`/`DEF`→`XY` gave `XY`, not `XY ghi`. The suffix is dropped too.
2. **"Constant +16 compensation."** A throwaway probe adding 16 to all four reads made P1/P2/P3/062/063 oracle-exact with perfect spans (`start=4 end=7`, `start=6 end=11`, …). FALSIFIED by replacement SHAPE: bare-variable and whole-subject replacements pass, but **concatenation** (`X 'DEF' = A B`) and **arithmetic** (`X 'DEF' = N + 1`) still return `slen=0 start=0 end=0` — those chains carve more than one cell. The delta is the live carve of the replacement chain, never a constant. **Probe reverted; tree clean.**

Both falsifications came from the cheapest discriminating experiment available, before any code was read — the RULES.md §1 order paid twice here.

## CROSS-REQUEST TO MECH (blocks C-9)

The fix is a frame/claim protocol term, which this ladder does not land (COORDINATION). Restore the cross-box delta for flat readers whose slot owner is a different box, in one of two shapes:

- **(a) Restore the term in the ONE offset function.** `delta_out(reader) − delta_out(owner)` in `x86_frame_off`, sourced from whatever survives M-3's staging twins, so every FR/FRQ/FRQB reader converts at once — UCLAIM's original "zero template edits" property.
- **(b) Migrate the remaining flat readers to the ζ spine.** ZD-5 MATCH-SPINE already moved the replacement to travel BY ADDRESS through `ZOPQ`/`op_zres` because "the armed producer no longer writes the flat replp slot." Subject and span are the last flat readers in this template; the same migration makes them depth-immune.

(a) is the smaller blast radius if the staging survives M-3; (b) is template-local but only cures this one site while leaving every other cross-box flat reader latent.

**Sweep the compiler, not the artifacts:** the committed `.s` files still carry the PRE-M-3 correct offsets, so artifact inspection alone would have exonerated the compiler. They are stale honest output, not a golden — do not wire them into a gate.

## WITNESSES

Failing at HEAD, both modes: `062_capture_replacement` · `063_capture_null_replace` · probes P1/P2/P3 (mid-string, at-zero, longer-replacement) · R2 (concat replacement) · R4 (arith replacement).
Passing and must stay passing: `058` `059` `060` `064` `066` · R1 (bare-variable replacement) · R3 (whole-subject match — passes ACCIDENTALLY, since prefix and suffix are both empty there and the manual's "replacement behaves like a simple assignment" case coincides with the bug).

**SEPARATE CLASS, not C-9:** `061_capture_in_arbno` fails the MATCH outright (`POS(N)` with a variable argument, no output at all), not the splice. `065_capture_then_arbno` is rc=139. Neither is stage 4/5; do not fold them into this rung.
