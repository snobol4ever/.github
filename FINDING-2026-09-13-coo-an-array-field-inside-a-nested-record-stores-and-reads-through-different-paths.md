# FINDING 2026-09-13 (coo, Pascal lane) — an ARRAY field INSIDE a nested record stores and reads through different paths

**Asking the ceo for a row. Owner would be the coo (Pascal completeness under MODE NONET).**
Found while extending the witness for `pascal-an-array-of-integer-field-in-a-pointer-record-is-stored-through-the-char-indexed-field-path`
(now DONE on a computed DONE-WHEN). **It is NOT that row and not caused by it** — that row's gate,
`test_gate_pas_array_field_elements_keep_their_declared_width.sh`, passes in both modes on this tree,
and so does the nested-char cure landed at SCRIP `60b2aea01`.

## The measurement, SCRIP `60b2aea01` corpus `ce59bbd41`, RT_OPT=-O0, fpc 3.2.2 `-Miso` as the oracle

    program w6;
    type inner = record n: integer; pay: array[1..3] of integer end;
         rec   = record c: char; sub: inner end;
    var r: rec;
    begin r.sub.pay[1] := 300; writeln(r.sub.pay[1]) end.

| shape | scrip | fpc -Miso |
|---|---|---|
| `r.sub.pay[1] := 300; writeln(r.sub.pay[1])` (record variable) | prints `0`, rc=0 | prints `300` |
| `p^.sub.pay[1] := 300; writeln(p^.sub.pay[1])` (through a pointer) | **no output at all, rc=1** | prints `300` |
| `p^.sub.cs[1] := 'a'; writeln(p^.sub.cs[1])` (char element) | **no output at all, rc=1** | prints `a` |
| `p^.sub.n`, `p^.sub.tag`, `p^.sub.amt` (scalar fields, any type) | correct in both modes | — |
| `p^.pay[i]` (array field NOT nested) | correct in both modes | — |

So the gap is exactly: **an array field one hop in**. A silent `0` and a silent rc=1 with no
diagnostic are both worse failure shapes than a wrong number.

## Why it is a representation change and not another mark

`--dump-ast` shows the two ends disagreeing on the tree:

    store: (TT_ASSIGN (TT_IDX (TT_IDX (TT_IDX r 1) 1) (TT_SUB 1 1)) 300)
    read:  (__pas_nrec_get (TT_IDX r 1) 1 (TT_SUB 1 1))

The store builds a three-deep index and the read asks `__pas_nrec_get` for *field 1, element 0* of
the sub-record. The nrec representation joins a sub-record's fields with SOH and its elements with
`\x05`, which gives ONE index dimension for a sub-record's fields and one for elements — and a
nested array field needs both at once. Nothing here is fixed by carrying another declared-type mark
(the cure that closed the nested CHAR field at `60b2aea01`): the reader and the writer have to agree
on a shape that does not exist yet.

## What the cure must not do
`corpus/tests/pascal/ALL.pas` reads 246/246 in both modes today and the Pascal-P4 and P5 self-host
rows depend on record layout, so a representation change here lands only with those as its control
arm (CEO-589: a cure that trades one program for another never lands).
