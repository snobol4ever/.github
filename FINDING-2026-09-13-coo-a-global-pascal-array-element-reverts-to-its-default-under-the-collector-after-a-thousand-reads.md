# FINDING 2026-09-13 coo -- a correctly assigned element of a global Pascal array reverts to its default under the collector, and it is what now blocks Pascal-P4 generation 2

**Trees**: SCRIP `1d0a3d3d4` (origin), corpus `c0cdcd113`; oracle `/usr/bin/fpc 3.2.2 -Miso` where one exists;
`RT_OPT=-O0`; mode 3. Package `corpus/packages/pascal/p4`.

## What moved

After three Pascal landings today -- the movable heap root (`f0d0adf5b`), array fields keeping their
declared element type (`bcf75511a`) and record-variable scoping (`2bef12615`) -- Pascal-P4's second
generation changed failure entirely:

| reading | before today | now |
| --- | --- | --- |
| generation 1 (SCRIP-built P4 compiles its own source) | rc 0, 18911 P-code lines, 0 errors | unchanged |
| generation 2 (SCRIP-built P4 interpreter runs that P-code) | `[ZHP] heap exhausted (512 MB)` after ~2.9 s | runs to completion, rc 0 |
| generation 2's verdict | BLOCKED on the heap | BLOCKED on one named defect below |

Generation 2 now prints exactly one line, P4's own diagnostic ` illegeal instruction`, and stops.
The self-host script still reads `SELFHOST BLOCKED`, which is honest, but the blocker is no longer
the collector.

## The defect, measured

`int.pas` holds `instr: array [bit6] of alfa`, a 128-entry table of ten-character mnemonics, filled
by a nested procedure `init` and searched by a sibling nested procedure `assemble` through
`while instr[op] <> name do op := op + 1`.

Instrumenting a scratch copy of the vendored source (never the vendored file), printing ONE array
element per `writeln` so the reading cannot be blamed on the print:

| where | `instr[23]` |
| --- | --- |
| in `load`, immediately after `init` returns | `ujp       ` |
| in `generate`, at the top of its loop | `ujp       ` |
| in `assemble`, at each of its first five statements, for 1079 consecutive instructions | `ujp       ` |
| in `assemble`, after the search loop on instruction 1080 | corrupt |

**The 1080th instruction is where it breaks, not the first.** Dumping character codes at that point
settles what "corrupt" means:

```
name       117 106 112  32  32  32  32  32  32  32     ("ujp" + seven blanks, ten components, correct)
instr[23]   48                                          (ONE component, the character '0')
```

The table entry has been replaced by a single `'0'`, which is the default fill this runtime writes
into an unassigned aggregate component. So a correctly assigned element of a global Pascal array
REVERTS TO ITS DEFAULT after roughly a thousand iterations of a loop that only reads it.

## It is the collector

The failure mode changes with every collector setting, on the same tree, same input, same binary:

| setting | outcome |
| --- | --- |
| default | deterministic across three runs: the corrupt read above, P4 prints ` illegeal instruction` |
| `SCRIP_GC_LINE_MB=0` (pacing off) | SIGSEGV |
| `SCRIP_GC_LINE_MB=1` | exits 1 with no P-code written |
| `SCRIP_GC_STRESS=500` | `[ZHP] heap exhausted (512 MB, 179 blocks) on a pinned allocation` |

Four different failures from four collector settings is not a frontend defect. Note the last row's
arithmetic: 179 blocks filling 512 MB is about 3 MB per block, which is the array's whole backing
store copied per element store -- the same `arr_set` site already filed on 2026-09-13 in the
finding on integer array fields, still allocating `HB_WS` and therefore still unreclaimable.

Under MODE NONET (CEO-669) GC heap storage across all seven languages is hq_V's concern and this is
handed to them; the Pascal frontend half is the coo's and nothing here points at it.

## Not claimed

Generation 1 is unchanged and still clean. Nothing here is a regression: the P-code that generation
2 loads is the same 18911 lines generation 1 has produced all along, and re-reading it shows it
well-formed (a label definition per line from `writeln(prr,'l',labname:4)`, an instruction per line,
and the apparent double records such as ` ent   1   l   4` are a single `writeln` at comp.pas:2063
carrying a label OPERAND, not two merged lines).

## Suggested next step

Narrow the table read by bisecting `int.pas` itself rather than by building witnesses: the shape is
inside that file and six plausible reductions of it are already ruled out. The cheapest cut is to
print `instr[23]` after each statement of `assemble` in a scratch copy until it goes empty.
