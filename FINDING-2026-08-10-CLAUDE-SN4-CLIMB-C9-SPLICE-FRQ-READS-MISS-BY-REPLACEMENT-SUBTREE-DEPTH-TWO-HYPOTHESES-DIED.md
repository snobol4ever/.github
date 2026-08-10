# FINDING 2026-08-10 — SN4 ζ-CLIMB C-9: SPLICE FRQ READS MISS BY REPLACEMENT SUBTREE DEPTH; TWO HYPOTHESES DIED ON THE WAY

**Session:** CLIMB s36 (Sonnet 4.6). **Repos at open:** SCRIP `c7e085fd` · corpus `9fb2e019`.
**Fix:** ALREADY LANDED by s35 (Opus 5) as `942ef1b1` (`C-9 REPL-ZDEPTH`). This finding documents the independent root-cause derivation from this session, two falsified hypotheses, and a confirmed independent path to the same diagnosis.

---

## THE DEFECT (observed at SCRIP `c7e085fd`, BEFORE `942ef1b1`)

`SUBJECT ? PATTERN = REPLACEMENT` overwrites the entire subject with the replacement string instead of splicing only `[match_start, match_end)`. Both modes m3 ≡ m4 (glue stubs exonerated per METHOD §6).

**MONITOR-FIRST bracket** (`PARTICIPANTS="spl scr"`, `062_capture_replacement.sno`):
```
DIVERGE step 4, stno=2,  X 'world' = 'there'
  last agree: step 3   LABEL stno=2
  spl: VALUE X = STRING(11)='hello there'
  scr: VALUE X = STRING(5) ='there'
```
`STRING(5)` = replacement's own length — verbatim write, no splice.

**In-tree tracer** (`SCRIP_REPL_TRACE=1`):
```
[REPL] name=X slen=0 start=0 end=0 rs="XY" rlen=2
```
`slen=0, start=0, end=0` → `nlen = rlen` → whole-subject overwrite. The C of record `c_rt_match_replace` is **correct** (three-memcpy splice, matches manual Ch.6 p.72-73). The defect is in the arguments.

---

## TWO HYPOTHESES DIED (before any code was read)

### Hypothesis 1: "Prefix dropped, suffix retained"

062 and 063 both produced the replacement alone. Both have empty suffixes, so the symptom looked like a prefix bug. **Falsified** by probes with non-empty suffix:

```
P1: X = 'abc DEF ghi';  X 'DEF' = 'XY'  →  got [XY],  expected [abc XY ghi]
```

The suffix is also gone — the whole subject is overwritten.

### Hypothesis 2: "Constant +16 compensation"

A throwaway probe adding 16 to all four flat reads in `bb_match_replace.cpp` (`op_sa`, `op_sa+8`, `op_off`, `op_off+24`) made the literal-replacement cases oracle-exact. **Falsified** by replacement SHAPE:

```
R2: X 'DEF' = A B      (concat)   → still slen=0 start=0 end=0
R4: X 'DEF' = N + 1   (arith)    → still slen=0 start=0 end=0
```

Literal (`'XY'`) and bare-variable (`Y`) replacements passed; concat and arith still failed because those chains carve more than one cell. **The delta is the live ζ-footprint of the replacement subtree, not a constant.** Probe reverted immediately; tree clean throughout.

---

## ROOT CAUSE (independently confirmed; matches `942ef1b1` diagnosis)

The replacement travels by ζ-cell address (`ZOPQ(1,0)` / `op_zres` — ZD-5 MATCH-SPINE) so it is depth-immune. The subject (`FRQ(op_sa)`, `FRQ(op_sa+8)`) and span (`FR(op_off)`, `FRQ(op_off+24)`) are flat reads. `IR_MATCH_REPLACE` is K=0 (the splice owns no result cell), so `zd_k()` returns 0, and `op_zdepth=0`. But by the time `bb_match_replace_α` executes, the replacement expression has already carved its own ζ-cells and left them **live** (r9 points into them). Every flat read is short by that subtree's carve. Emitted asm at the ctx_restore-to-splice window shows the miss directly:

```asm
mov  r13, [rsp + 48]     # outer_Σ  — written by head at this RSP
call rt_match_ctx_restore
n11_lit_string_α:
sub  rsp, 16             # replacement mints its ζ-cell; RSP drops by 16
n12_match_replace_α:
mov  ecx, [rsp + 48]     # "start"  — same offset, now 16B past outer_Σ → zero
```

**This is also a REGRESSION.** Committed artifact `062_capture_replacement.s` carried `[rsp+176/184/64/88]`; HEAD `c7e085fd` emitted `[rsp+160/168/48/72]` for the same program — exactly 16 short for a literal replacement. The same-program A/B between committed artifact and current compiler exonerates the C of record and names the emitter as the regression site without gdb or code reading.

Commit `1351d299` (M-3 UCLAIM physical deletion) removed the owner-table term `delta_out(reader) − delta_out(owner)` that had provided the cross-box compensation. `15d2af87` (M-3 FIX) restored the intra-box depth accumulator but not the cross-box term. The residual casualties are flat readers whose slot owner is a different box — exactly the splice reading head slots across the replacement chain's carve.

---

## THE FIX (s35, `942ef1b1`, not this session)

`g_zd_zunder` staged for `IR_MATCH_REPLACE` only, consumed at the choke as an `op_zdepth` addend; mirrors the `g_zd_ztail`/`IR_TO` precedent. 3 insertions / 3 deletions. Gate: crosscheck m3 239/78 → 242/75, exactly 3 status changes, all fail→pass (062 · 063 · 064_replace_multi_arm), zero pass→fail.

---

## SELECTIVITY — THE FINGERPRINT

| arg | source | at `c7e085fd` |
|---|---|---|
| `rdi` name | `ROQ(0)` — rip-relative, RSP-immune | ✅ correct |
| `r9` replacement | `ZOPQ(1,0)` — ζ-cell by address, RSP-relative to current top | ✅ correct |
| `rsi/rdx` subject | `FRQ(op_sa)`, `FRQ(op_sa+8)` — flat | ❌ zero |
| `ecx/r8` start,end | `FR(op_off)`, `FRQ(op_off+24)` — flat | ❌ zero |

The depth-immune paths survive; the flat paths miss. That selectivity pattern is the fingerprint: anything on `ROQ`/`ZOPQ` is right; anything on `FRQ`/`FR` is short by the preceding carve.

---

## SEPARATE CLASS (do not fold into this rung)

- **061** fails the match outright (`POS(N)` with a variable argument) — not a splice defect, not C-9.
- **065** pre-existing CRASH (rc=139) — separate class.
- **D12/D13/H31** — inherited regressions, introduced between `6ffa57fe` and `c7e085fd` by a parallel seat, not yet diagnosed. Not C-9.
