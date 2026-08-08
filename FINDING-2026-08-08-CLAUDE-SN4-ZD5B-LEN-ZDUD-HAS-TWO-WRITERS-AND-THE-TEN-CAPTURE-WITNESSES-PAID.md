# FINDING 2026-08-08 (CLIMB s14) — `zd_ud[]` HAS TWO WRITERS AND TWO MEANINGS; THE `_xh` GATE READ THE WRONG ONE

**Rung:** GOAL-SN4-ZETA-CLIMB C-6 · **Fix:** SCRIP `8970c59e` · corpus `bf8ec91e`
**Introduced by:** SCRIP `b491998e` (ZD-5b-LEN cross-head fix) · **Last good:** `01440ed4`

---

## THE LAND MINE

`b491998e` bought D07 (`LEN(*N)`) and paid ten witnesses for it:

```
A05 A06   ALT capture (=F, W unset; A05 crashed)
H08 H10 H14 H15 H23 H26 H28 H29   FENCE1 + capture (H29 crashed)
```

Both modes, so the m3 glue was exonerated at the outset (METHOD §6).
The commit message **named all ten in advance** and diagnosed them as:

> those blob contexts re-enter at variable RSP depth, so the static
> cross-head offset is wrong for them; routing those to FRAMED glue is
> the M-2(a) sequel.

**That diagnosis is wrong, and it cost the rung a MECH block it did not need.**

## WHAT THE TRACE SAID

`SCRIP_ZD_DIAG=1` on the three representative witnesses:

| probe | `[ZD-H]` run-head events |
|-------|--------------------------|
| D07 (fixed by b491998e)   | **1** — `Kc=256 hpos=4 zdh=48 nblob=0` |
| A05 / H08 / H14 (broken)  | **0** |

All three parts of `b491998e` live inside `if (Kc > 0 && hpos >= 0 && !zwr)`,
the same branch that prints `[ZD-H]`. **Zero events means none of the three
parts ever ran for the regressed witnesses.** A mechanism that never executes
cannot be the mechanism. "Blob contexts re-enter at variable RSP depth" is a
statement about a code path these programs do not take.

Selective revert confirmed the isolation — with part 3 (`_xh`) forced off,
A05/H14 return to `=S`, D07 loses its capture. A clean 1-for-10 trade, and
part 3 is the sole carrier.

## ROOT CAUSE — TWO AUTHORITIES FOR ONE SLOT

`zd_ud[]` is written from two arms of `zd_plan`, meaning two different things:

```c
/* blob-closure arm  */  zud[hi] = zdh;   /* a CROSSING DEPTH   */
/* UCLAIM mem[] arm  */  if (mem[k]) { zud[k] = K; zuh[k] = hi; }   /* a CLAIM FRAME SIZE */
```

The staging site read `zd_ud[zd_uh[i]]` and assumed the **first** meaning:

```c
int _xh_zdh = ... ? (int)zd_ud[zd_uh[i]] : -1;
int _xh = (zd_ud[i] > 0 && zd_ud[_k] == 0 && _xh_zdh >= 0 && ...) ? 1 : 0;
```

All ten regressed witnesses take the **UCLAIM arm**. So `_xh_zdh` received `K`
— a frame size, never a depth — the `>= 0` test passed on it, and `_xh` fired
on statements that have no cross-head read at all. The "corrected" offset was
then computed from an unrelated quantity and the capture operand resolved to
the wrong cell.

`zd_ud[i] > 0` reads as "this node is post-head." It actually means
"*somebody* wrote this slot." Under one writer those coincide. Under two they
do not, and nothing in the type system or the name says which arm won.

**This is the same defect class the comment on that very line already names** —
the ZD-2d/2e note about the planner and the driver holding "TWO OPINIONS" of
operand count. The line documenting a one-authority violation acquired one.

## THE FIX

`zd_zdh[]` — sole authority for the crossing depth. Written only by the
blob-closure arm, initialised to `-1` everywhere else. The `>= 0` test becomes
a genuine predicate ("this run head published a zdh") instead of an accident
of write order. Byte-identical for the D07 population; the ten come back.

## MEASURED

| | before (`31a22715`) | after (`8970c59e`) |
|---|---|---|
| m3 | 125 / 7 / 0 / **10 REGRESSION** | **135 / 7 / 0 / 0** |
| m4 | 121 / 10 / 1 / **10 REGRESSION** | **132 / 10 / 0 / 0** |

Both exceed the s13 watermark (m3 134 · m4 131) — D07 is kept, not traded.
`XFAIL.compile` D07 removed same rung. Regen: `061_capture_in_arbno.s`
`[rsp+72]` → `[rsp+312]`, verified against the SPITBOL oracle; 3 demo `.s`
regenerated, all oracle-clean.

## CONSEQUENCES

1. **C-6 was never MECH-blocked on this.** No new frame/glue/claim protocol was
   needed — de-aliasing two overloaded slots is CLIMB-local. MECH cross-request
   for D06/D07/D08 is partially void: D07 is closed. D06/D08 remain open and
   should be re-diagnosed rather than inherited.
2. **A named-in-advance regression is still a red gate.** `b491998e` correctly
   declined to XFAIL its ten (RULES: never XFAIL except a Lon-ruled park) — but
   that leaves the suite red and the rung ungateable, and the next session
   inherits a watermark that silently no longer holds. The honest commit message
   did not prevent the cost. **Surface for a Lon ruling:** a known-red landing
   needs either a park or a revert, not a message.
3. **A theory that names its own casualties still needs falsifying.** The
   author's mechanism was plausible and specific, and it was wrong. One
   `SCRIP_ZD_DIAG=1` run — thirty seconds — falsified it. MONITOR-FIRST is not
   only for the bug hunt; it applies to the *explanation* offered for a bug
   already found.

## STILL OPEN (control-built pristine HEAD — identical rc, NOT caused by this fix)

- `pb_snapshot_imm` rc=134 stack-smashing (s13's "MUST FIX FIRST"; output `S A`
  correct, canary fires post-execution)
- `pb_stitch_compose` rc=139 SIGSEGV
- `template_medium_invisible --strict` red on `bb_glue_flat.cpp(2)`,
  `xa_flat.cpp(8)` — self-labelled informational WIP baseline, untouched here
