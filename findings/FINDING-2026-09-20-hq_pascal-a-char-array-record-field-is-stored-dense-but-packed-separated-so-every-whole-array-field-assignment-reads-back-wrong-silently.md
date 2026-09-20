# FINDING 2026-09-20 hq_pascal — a char-array record field is STORED DENSE but PACKED SEPARATED, so every whole-array field assignment reads back wrong, silently, exit 0

**Seat:** hq_pascal · **Tree:** SCRIP `5418432bb`, corpus `8486bb1e2` · **Oracle:** `/usr/bin/fpc -Miso` (FPC 3.2.2) · **Graded by ORACLE DIFF, never by rc.**

⛔ **THIS IS NOT A GC DEFECT AND THE DISTINCTION IS THE POINT.** It reproduces at the SHIPPED arena with `SCRIP_GC_STRESS` unset, with no collection anywhere near it. It was found while probing for one, and a witness that used this construct would have read as GC corruption at the tiny arena. Any seat grading a GC witness that stores a whole array into a record field is grading THIS instead.

## The witness, and it exits 0 with no diagnostic

```pascal
type str = packed array [1..8] of char;
     rec = record name: str end;
     link = ^rec;
var p: link; r: rec; a, t: str; j: integer;
...
for j := 1 to 8 do t[j] := chr(ord('a') + j);
a := t;                                   (* plainarray *)
r.name := t;                              (* localrec   *)
new(p); p^.name := t;                     (* ptrrec     *)
for j := 1 to 8 do p^.name[j] := t[j];    (* ptrperchar *)
```

| form | `fpc -Miso` | SCRIP m3 | SCRIP m4 |
|---|---|---|---|
| `plainarray` — `a := t` | `bcdefghi` | `bcdefghi` ✅ | `bcdefghi` ✅ |
| `localrec` — `r.name := t` | `bcdefghi` | **`09899`** ⛔ | **`09899`** ⛔ |
| `ptrrec` — `p^.name := t` | `bcdefghi` | **`09899`** ⛔ | **`09899`** ⛔ |
| `ptrperchar` — per element into `p^` | `bcdefghi` | `bcdefghi` ✅ | `bcdefghi` ✅ |

A second witness isolates the local record further — per-element write into a LOCAL record, then read back:

| form | `fpc -Miso` | SCRIP m3 |
|---|---|---|
| `r.name[j] := t[j]` then read | `bcdefghi` | **`0`** ⛔ |
| `write(r.name)` whole field | `bcdefghi` | **`` (empty)** ⛔ |
| `a := r.name` field to array | `bcdefghi` | **`0`** ⛔ |

**Both modes fail identically, so this is lowering/runtime and not mode-conditional codegen.**

## The mechanism, read out of the code

A Pascal array value is a **SOH-separated** string: `--dump-ast` shows `t` initialized to `"0\x010\x010\x01…"`. A record is also a SOH-separated string, one segment per field. A char array nested in a record would therefore collide with the record's own separators, and the parser handles that by wrapping the RHS at `pascal.y:1008` in `__pas_ca_pack`:

```
(TT_FNC (TT_VAR __pas_field_set) (TT_VAR p) (TT_ILIT 0)
        (TT_FNC (TT_VAR __pas_ca_pack) (TT_VAR t)))
```

`__pas_ca_pack` (`by_name_dispatch.c:3403`) maps SOH → `\x1e` and **keeps the separators**, so it yields `b\x1ec\x1ed\x1e…` — a SEPARATED string of length 15 for an 8-element array.

⛔ **But the field interior is DENSE, and the per-element writer proves it.** `__pas_field_idx_set` (`by_name_dispatch.c:3442`) locates field `fidx` with `pas_seg_span` and then writes element `eidx` at **byte offset `pre + eidx - 1`**, one byte per element, no separators:

```c
o[pre + (size_t)eidx - 1] = (char)ch;
```

So the per-element writer stores `bcdefghi` densely and the reader indexes densely — which is exactly why `ptrperchar` is the one pointer form that works — while `__pas_ca_pack` stores a separated string that the same dense reader then mis-indexes. **Two writers disagree about the representation of the same field, and the reader agrees with only one of them.**

## Why no instrument caught it

- The Pascal master is **246/246** and does not contain this construct, so the denominator never covered it.
- It **exits 0** and prints a plausible string, so every rc-shaped check reads green — CEO-556's class, and the same quiet-wrong-answer shape the GC road has been chasing all week.
- `__pas_ca_unpack` exists and is emitted only at `pascal.y:1121` for a whole-field READ, so the pack/unpack pair is self-consistent **with each other** and inconsistent with the dense per-element writer. A round-trip test of pack→unpack alone would pass.

## What is NOT claimed

The graded reach is **small, and measured rather than guessed**: only one PAT file carries both `record` and `array [`. This is a real silent wrong answer, not a large slice of the FPC 88/181 or PAT 297/427 pile. Do not cite it as either.

## The cure is a REPRESENTATION RULING and is deliberately NOT landed here

There are at least three broken paths and they do not share one line: (a) `__pas_ca_pack`/`__pas_ca_unpack` encode separated where the field interior is dense; (b) a LOCAL record's nested-index store `r.name[j]` fails even per element, and the local record is initialized to the single-segment literal `"0"` with no room for an 8-element field at all; (c) the whole-field read path depends on whichever representation (a) settles on. **Picking dense-vs-separated is one decision that all three must then obey**, and landing (a) alone would leave (b) wrong while making the suite look better. Routed rather than half-cured.
