# FINDING: `@arr[$x OP @arr]` inside 2+ nested `for` loops SIGSEGVs — pre-existing, unrelated to string interpolation, likely the same class as the known closure/frame-resolution gap

Row: `raku-frontend-real-world-syntax-gaps` (construct f, string interpolation). Discovered while implementing
`@arr[expr]` interpolation inside `"..."` strings (needed by `spinner`, the corpus's only kernel using this
shape — confirmed by grep across all 17 `corpus/benchmarks/raku/*.raku`).

## Measured, not inferred

Minimal repro, 8 lines, **no string interpolation at all**:
```raku
sub MAIN(Int $h = 2, Int $w = 2) {
  my @arr = (10,20,30);
  for ^$h {
    for ^$w {
      print @arr[$_ % @arr];
    }
  }
}
```
`./scrip --run` → SIGSEGV (rc=139). `gdb bt`: `#0 0x0000000000000011 in ?? ()` — a jump to a tiny integer
address, the same signature class this rung's own icon-bench task file documents for generator-frame
corruption ("`ret` then jumps to the integer that overwrote γ").

**Isolated to exactly two ingredients, both required:**
- **2+ levels of `for` nesting.** Single loop (`for 0..1 { print @arr[$_ % @arr]; }`), or nested loops with
  no subscript, or nested loops with a plain-index subscript (`@arr[$_]`, no operator) — all run clean.
- **An operator (`%` tested; likely any binary op) whose subscript expression references the SAME array
  being subscripted** (`@arr[... @arr]`) — a plain named-scalar index inside the identical nested-loop
  shape does not crash.

Neither ingredient alone reproduces it; both together do, regardless of whether the index variable is
`$_` or a named scalar (`$i` crashes identically), and regardless of whether it's reached via string
interpolation or plain code — **confirmed identical crash from direct, non-interpolated code**
(`print @arr[$_ % @arr];`), which is what rules out the interpolation feature as the cause.

## Not chased further — out of this row's lane

This is real design work belonging to whatever rung owns generator/frame-chain codegen (the same
"anonymous `IR_graph_t` per loop body, resolved-elsewhere variable reads" mechanism already root-caused
for `rc-mandelbrot`/`rc-dragon-curve`/`merge-sort`'s shared blocker — not re-derived here, just flagging
the resemblance since a second array reference inside the loop body is exactly the kind of "reads a name
whose home graph differs" case that mechanism is built around). Not bisected into the emitter; not
attempted. Whoever next works the closure/frame-resolution item may find this a useful second, simpler
repro (no `for ... -> $var`, no closures, just nested bare loops) to validate a fix against.

## Consequence for the interpolation construct (unaffected — landed separately)

`spinner.raku` is the only kernel needing `@arr[expr]`-in-string interpolation, and it also happens to hit
this exact crash shape (`@spinner[$_ % @spinner]`, self-referencing, inside `for ^$h { for ^$w { for
^$spins { ... } } }`, 3 levels deep). The interpolation feature itself works correctly and is verified
independently (see task NEXT block) — `spinner` now parses and runs instead of failing to parse, advancing
to this separate, deeper, pre-existing blocker. Raw 17-kernel count unchanged at 3/17, same normal shape
as nearly every prior pass on this row.
