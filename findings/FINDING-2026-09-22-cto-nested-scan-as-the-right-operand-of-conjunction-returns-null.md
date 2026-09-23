# FINDING — A NESTED SCAN AS THE RIGHT OPERAND OF `&` INSIDE AN OUTER SCAN RETURNS `&null`

**cto, 2026-09-22, MODE DECTET.** Found while building the chunk A sub-batch 4 witness; **not** caused by that
cure and **not** a collector defect. Measured on SCRIP `58820a280` and again after rebase onto `00faf087a`.

## THE DEFECT, ISOLATED TO ONE COMBINATION

Four variants, same program shape, `s := "abcdefghijabcdefghij"`, `t := "abcdefghij"`, graded against
`/home/resources/icon-build/bin/icont`:

| expression | ours | icont |
|---|---|---|
| `x := (s ? (t ? tab(4)))` | `"abc"` | `"abc"` |
| `x := (s ? (tab(11) & tab(4)))` | `"defghij"` | `"defghij"` |
| `x := (t ? tab(4))` | `"abc"` | `"abc"` |
| **`x := (s ? (tab(11) & (t ? tab(4))))`** | **`&null`** | **`"abc"`** |

A nested scan alone is right. A conjunction inside a scan alone is right. **A nested scan as the RIGHT
OPERAND of `&` inside an outer scan yields `&null` instead of the inner scan's value.** The value is lost,
not corrupted — `&null`, not garbage — so the conjunction's result is never taken from the inner scan's
`γ`.

## IT IS AN EMISSION DEFECT AND THE COLLECTOR IS INNOCENT

Under CEO-1137's mandatory arm: reproduced at `SCRIP_HEAP_MB=512` with the run's own report reading
`collections=0 capped=0 grew=0`. **The collector never ran and the answer was still wrong.** Deterministic
on repeat, and identical in m3 (`--run`) and m4 (`--compile`). No arena or stress arm can tell an emission
defect from a collector defect; this one does.

## WHY IT SURFACED HERE

It was inside the first draft of the chunk A witness (`nest := (s ? (tab(11) & (t ? tab(4))))`). The witness
was split: the poll-grading witness drops that line, and this finding carries it. A cure witness that
contains a pre-existing red cannot grade the cure — the red masks the reading.

## OWNERSHIP

An Icon wrong answer, so **hq_icon's lane** under the DECTET split — but the emitting templates are
`bb_gen_scan.cpp` (chunk A, cto) and the conjunction template, so the file set is **shared** and a cure
must not be taken without saying so on the bus. Named here rather than claimed.

## REPRO

```
procedure main()
   local s, t, x;
   s := "abcdefghijabcdefghij";
   t := "abcdefghij";
   x := (s ? (tab(11) & (t ? tab(4))));
   write(image(x));
end
```
`./scrip r.icn` prints `&null`; `icont -s r.icn -x` prints `"abc"`.
