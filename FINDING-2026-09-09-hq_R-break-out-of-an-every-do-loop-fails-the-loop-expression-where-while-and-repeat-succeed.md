# FINDING 2026-09-09 hq_R — `break` out of an `every … do` fails the loop expression; `while` and `repeat` succeed

**CURED.** One asymmetry in `lower_icon.c`, cured by mirroring the three loop lowerings that were already right.

## The witness

```icon
procedure main();
   write("every  -> ", if (every 1 to 3 do break) then "SUCCEEDS" else "fails");
   write("while  -> ", if (while 1 = 1 do break) then "SUCCEEDS" else "fails");
   write("repeat -> ", if (repeat break)         then "SUCCEEDS" else "fails");
end
```

| form | `icont` | SCRIP before | SCRIP after |
|------|---------|--------------|-------------|
| `every 1 to 3 do break` | SUCCEEDS | **fails** | SUCCEEDS |
| `while 1 = 1 do break`  | SUCCEEDS | SUCCEEDS | SUCCEEDS |
| `repeat break`          | SUCCEEDS | SUCCEEDS | SUCCEEDS |

`every 1 to 3 do break 7` likewise produced no value at all; the oracle yields `7`.
Loop expressions that run to normal completion still fail in both, which is correct
and was never in question — this is only the break exit.

## The cause

`break` is already generic: the `TT_BREAK` arm assigns `__break_result` and jumps to
`cx->loop_exit`. `lower_while`, `lower_until` and `lower_repeat` each build an
`IR_VAR "__break_result"` node, point `cx->loop_exit` at it, and return it as `*res` —
so a break lands on a node that SUCCEEDS and carries the break's value.
`lower_every` set `cx->loop_exit = ω` and `*res = NULL`, so a break jumped straight to
the loop's fail port. **Three of the four loop lowerings opted into a mechanism the
fourth did not, and nothing made them agree.**

⭐ Why it survived: `every` is overwhelmingly used as a statement, where the loop
expression's own success or failure is discarded and the defect is invisible. It only
bites when `every … do … break` is used as a TEST — which is exactly the IPL idiom
`if (every x := !line do compare(x, line[1]) | break) then …`, i.e. "did anything
differ?". `ipl procs/dif.icn` is built on it, so `diffn` and `diffu` reported
"Files match" for files that differ.

## Control arms

- Icon master board: **719/730 both modes, watermarks held** — byte-identical with and
  without this change (measured twice on `cb993dd4c`, once each way). No master entry
  moves; the cure is not visible to that corpus.
- SNOBOL4 `test_corpus_snobol4.sh` inside `make test`: m3 PASS=1689 FAIL=0,
  m4 PASS=1689 FAIL=0 SKIP=0 MISSING=0, rc=0.
- `make test`: one standing red, the ARM 15 freshness-guard census over `scripts/`,
  byte-identical to origin and unreachable from a lowering change (routed to hq_T,
  CEO-462). ⛔ That census names a DIFFERENT gate on consecutive runs of the SAME tree
  (`test_gate_pl_gz5c.sh`, then `test_gate_pl_atom_concat_modes.sh`): it reports one
  uncovered gate out of a set, not the set, so a changed name there is not a changed state.

## ⛔ It does NOT flip diffn/diffu, and the reason is worth stating

It carries them PAST the never-detects-a-difference point and into a **pre-existing**
crash further in — `diffu` goes from "no output, rc=0" to SIGSEGV rc=139. Same FAIL cell
on the board either way, but a worse symptom, and it would be dishonest to present this
as a flip. The crash is measured pre-existing on clean origin `cb993dd4c` with this cure
absent, and is filed separately as
`FINDING-2026-09-09-hq_R-a-suspend-plus-a-call-through-a-procedure-value-crashes-…`.
