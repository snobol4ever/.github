# FINDING 2026-09-13 coo -- an array-of-integer field inside a pointer record clamps every element to a byte, and an array element store mints an 8 KB immortal block

**Tree**: SCRIP `0a6e5520a` (origin HEAD when measured) and the coo's cure worktree; oracle `/usr/bin/fpc 3.2.2 -Miso`; `RT_OPT=-O0`; both modes.

## 1. `array [1..n] of integer` inside a `^record` clamps to 0..255

Witness (`p: ^node` where `node = record id: integer; pay: array [1..128] of integer end`):

```pascal
new(p); p^.pay[1] := 300; p^.pay[128] := 1000;
writeln(p^.pay[1]:1, ' ', p^.pay[128]:1)
```

`fpc -Miso` prints `300 1000`. SCRIP prints `255 255`, in mode 3 and mode 4, at every width tried
(100, 128, 200, 255, 256, 300) and with both a literal and a variable index.

**Cause, read from the source**: a field of a heap record is one SOH-delimited segment of the record's
joined string, and an indexed store into such a field lowers to `__pas_field_idx_set`
(`src/runtime/by_name_dispatch.c`). That builtin is the PACKED-ARRAY-OF-CHAR path: it writes ONE BYTE at
the element position, clamping an integer value to `0..255` (`if (cv > 255) cv = 255`). There is no
integer-element path for an array field inside a pointer record. A record field that is an
`array of integer` therefore stores one character per element and reads back a character's ordinal.

**Why it matters now**: this is what the P4 interpreter's byte-addressed `store` hits, so it stands
between the P4 self-host milestone and generation 2 even after the heap row lands. It is NOT caused by
the movable-root cure and it reproduces on origin HEAD without it.

## 2. An array element store mints an 8 KB immortal block, one per store

Profiled with `SCRIP_ALLOC_HIST=1` on the P4 interpreter (`int.pas`): a single dominant callsite,
`arr_set` in `src/runtime/by_name_dispatch.c`, type `HB_WS` (203), 3725 allocations totalling 30.8 MB --
about 8 KB each, one whole rebuilt copy of the array's joined string per element assignment. `HB_WS` is
one of the four block types CEO-648 retired the exemption for, so every one of those copies is currently
immortal: the P4 interpreter exhausts the 512 MB arena after 32860 such blocks.

`arr_set` is a SHARED-NODE builtin (every frontend's array store goes through it), so it is outside the
coo's Pascal lane and is reported here rather than cured. Two separable defects live in it: the
allocation class (cured for Pascal records by the movable-root row, still pinned here) and the cost
class (a whole-array copy per element store, which is quadratic in the array's length).

## What is NOT claimed

Neither of these is a regression. Both reproduce on a clean origin HEAD. Neither is graded by any
current suite row, so no number moved because of them.

## Suggested rows (the ceo mints, not the coo)

1. `pascal-an-integer-array-field-of-a-record-stores-integers-not-bytes` -- Pascal-own, the coo's lane,
   and the next thing P4 generation 2 needs.
2. `arrays-store-one-element-without-rebuilding-the-whole-array` -- shared node, not the coo's lane;
   ranks with `gc-retire-the-four-immortal-block-types-every-block-slides`.
