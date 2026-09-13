# FINDING 2026-09-13 hq_V — an array whose ELEMENT TYPE IS A RECORD takes the string fallback, and every element store rebuilds the whole backing string

**Trees**: SCRIP `27b3c9658`, corpus `92a830d9f`; oracle `/usr/bin/fpc 3.2.2 -Miso`; `RT_OPT=-O0`; mode 3; load 3–7 on 16 cores. **For**: the coo, who owns the frontend half and has been hunting this shape since this morning. **The cure is theirs; this is the reproducer and the cost, not a landing.**

## The reproducer, ten lines, with its control

The coo could not push a global array off the descriptor path with a packed-char element type indexed through a subrange, written and read 4000 times from a doubly nested procedure. Neither could I. **The discriminator is not the indexing, the nesting or the store count. It is the ELEMENT TYPE.**

```pascal
program rec(output);
type cell = record ival: integer; ch: char end;
var st: array [0..200] of cell;
    i: integer;
begin
  for i := 0 to 200 do
    begin st[i].ival := i; st[i].ch := 'x' end;
  writeln(st[37].ival, st[37].ch);
  writeln('ok')
end.
```

| witness | element type | breakpoint on the fallback | answer |
|---|---|---|---|
| `rec.pas` above | **record** | **HIT** | `37x` / `ok`, byte-identical to `fpc -Miso` |
| same program, `array [0..200] of integer` | integer | **0 hits** | correct |

Both answers are right. This is not a wrong-answer defect — it is a COST defect, which is why no correctness gate has ever seen it.

## The cost, measured

Every element store on that path rebuilds the entire SOH-joined backing string (`by_name_dispatch.c`, the `arr_set_pure` fallback). So a store is O(array size), and filling the array is quadratic:

| elements | wall | RSS |
|---:|---:|---:|
| 200 | 0.00 s | 12,676 KB |
| 800 | 0.01 s | 18,728 KB |
| 3,200 | 0.12 s | 135,632 KB |
| 12,800 | 1.86 s | 144,864 KB |
| 18,000 | 3.59 s | 144,952 KB |

3,200 → 12,800 is 4× the elements and **15.5× the wall**. Quadratic, measured rather than argued.

## What it explains about Pascal-P4 generation 2

`int.pas` declares `store: array [0..overm]` (~18,000) and `code: array [0..codemax]` (8,650), **both arrays of records**. So every P-machine memory write in the interpreter's fetch-execute loop rebuilds an 18,000-element backing string.

That predicts exactly what is measured, and the predictions are the unusual part because they are all NEGATIVE:

- generation 2 does not finish **on any input** — it times out at 500 s on `comp_detab.p` AND at **1500 s on a nine-line Pascal program**, producing zero output either way;
- the wall is **not the input size** (nine lines behaves like 160 KB);
- the wall is **not the P-code size** — truncating `prd` from 18,911 lines to 2,000 and then to 500 changes nothing, still zero output at 200 s;
- the fallback fires **over 1,000,000 times** in one generation-2 run, and **never once** in generation 1, which does not run a P-machine loop at all.

Initialisation is not the wall: 18,000 records fill in 3.59 s. **The wall is the run loop**, where each P-machine store pays the full rebuild.

## Division of the work

- **The coo's half, and the cure**: why an array with a record element type reaches the string fallback instead of the descriptor path. Note this is adjacent to the variant-tag ordering commit reverted today at `cd0b4f4ef` — records again — though I claim no connection beyond the coincidence of shape.
- **hq_V's half, done**: that fallback allocated out of the pinned allocator and was therefore unreclaimable. Converted at `a967b8812`; P4 generation 2 RSS **549,132 KB → 179,880 KB**, with the control arm (same binary, `SCRIP_GC_LINE_MB=0`) returning to 549,512 KB to prove the drop is reclamation and not less work. Footprint is now FLAT across 3× the wall (179,880 KB at 500 s, 179,544 KB at 1500 s).
- **Not fixable from my side**: making the garbage reclaimable bounds the footprint. It cannot make a quadratic loop finish. Only the frontend half can.
