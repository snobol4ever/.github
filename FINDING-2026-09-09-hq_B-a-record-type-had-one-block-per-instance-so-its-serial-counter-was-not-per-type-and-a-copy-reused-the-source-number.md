# A record type had one block per INSTANCE, so its serial counter was not per-type, and a copy reused the source's number

**Seat:** hq_B · **Date:** 2026-09-09 · **Row:** CEO-476
`icon-record-serial-allocation-runs-through-three-constructors-and-a-per-instance-datblk-so-a-copy-cannot-get-a-fresh-number`
RT_OPT=-O0, incremental `make` · **Lane:** MODE NONET, Icon only

## The claim

`copy()` of a record imaged as the source's serial, and the counter then stayed one behind forever.
Oracle `r_1 r_2 r_3`; SCRIP `r_1 r_1 r_2`. Cured — three defects, one per layer.

## The measurement

```icon
record r(a,b)
procedure main()
   local x, y, z;
   x := r(1,2); y := copy(x); z := r(3,4);
   write(image(x)); write(image(y)); write(image(z));
end
```

| | m3 | m4 |
|---|---|---|
| `icont`/`iconx` | `r_1 r_2 r_3` | `r_1 r_2 r_3` |
| SCRIP before | `r_1 r_1 r_2` | `r_1 r_1 r_2` |
| SCRIP after | `r_1 r_2 r_3` ✅ | `r_1 r_2 r_3` ✅ |

## ⭐ Why the visible defect could not be fixed on its own

The obvious one-line fix — make `copy` mint a serial instead of reusing `src.u->id` — reads
`src.u->type->serial_next`. Two layers underneath made that read wrong:

1. **`dat_alloc_fill` gave every INSTANCE its own `DATBLK_t`**, rebuilt field-by-field from the `DatType`
   on every construction. The "per-type" block was per-instance, so a counter on it counted to 1 forever.
2. **That block's `serial_next` was never initialised.** `rt_ws_alloc` hands back uninitialised memory and
   nothing wrote the field. Nothing *read* it either — which is the only reason this had not already
   produced a garbage serial. It was a loaded gun, and the obvious fix is what pulls the trigger.
3. **`by_name_dispatch.c` copy did `nu->id = src.u->id`** — the visible defect.

So the cure is structural: a `DatType` caches **one** `DATBLK_t`, every instance of that type shares it,
`serial_next` is initialised at that single point, and the constructor and the copy both take their number
from it. One type, one block, one counter, one allocation site.

`DatType.serial_next` (the old counter) is **removed**, not left in place: nothing else read it, and a
field that looks like the authority but is not is exactly the decoy this codebase keeps re-learning.

## Two constraints checked rather than assumed

⛔ **No new globals** (CLAUDE.md hard rule). The counter lives on the existing `DATBLK_t`; the cache is a
struct member on the existing `DatType`. A name-keyed serial service — the shape the row's GOAL proposed —
would have needed a new global, so it was not taken.

⛔ **The cached pointer is collector-safe by construction.** `rt_ws_alloc` bumps the workspace island and
**never frees and never moves** (`rt_ws_alloc_core`, `gc_heap.c`); the compacting slide operates on the
separate `rt_gcheap` arena. Verified before caching a pointer in a static table, not after.

⛔ **The second `DatType` is a prefix truncation.** `rt_runtime.c:35` redeclares
`{ char name[64]; int nfields; char fields[64][64]; }` and never reads past it, so appending a member and
dropping a later one leaves its layout intact.

## Control arms — both arms with the two binaries side by side

| arm | before | after |
|---|---|---|
| Icon master (both-modes) | 740/754 | **741/754** |
| Icon master m3 · m4 | 740 · 740 | **742 · 741** |
| Icon master per-entry identity | — | examined=1557 **regressions=0 vanished=0** |
| Arizona | m3 76/90 · m4 76/90 | m3 76/90 · m4 76/90, identical red set |
| SNOBOL4 master | — | m3 1893 FAIL=0 · m4 1893 FAIL=0 SKIP=0 · ast 28 FAIL=0 OK |

⭐ **The flips are NAMED, by diffing the two FAIL lists — not inferred from the totals**, because a total
that moves by one cannot tell you whether one entry flipped or two flipped and one regressed:

- `procedure_write_257` — **m3**
- `procedure_record_every_replace_16` — **m3 and m4**
- newly red: **none**

## ⛔ Two things this row named did NOT flip, and neither is this defect

- **`procedure_write_257` m4.** Its record half is now byte-exact (`A:record array_1(3)` /
  `B:record array_2(3)`). What remains is `copy()` **of a function value**: `image(copy(copy))` gives
  `&null` in m4 where m3 *and* iconx both give `function copy`. That is the m4 function-value path — a
  separate defect, filed here by name rather than absorbed into this row's receipt.
- **`procedure_record_every_replace_14`** (Arizona `fncs`). A 187-line omnibus over dozens of builtins;
  the serial is one line of it. The row's GOAL expected this to move and it does not, which is worth
  recording: `fncs`'s 446 differing lines were never mostly serial numbering.
