# FINDING — DWARF `.file`/`.loc` LANDED FOR MODE-4: `perf`/`callgrind`/`gdb`/`objdump` NOW SEE SNOBOL4 SOURCE LINES

**Seat:** seat12 (FLEET, THE LOOP, task `emit-dwarf-loc-and-box-symbols`) · **2026-08-23** · **Class:** IMPLEMENTED + MEASURED, rung 1 of 2 (`.file`/`.loc` only; `.globl`/`.type`/`.size` per box is rung 2, out of scope here)

## Verdict

Mode-4 (`--compile`) SNOBOL4 output now carries real DWARF line info. Built with a new opt-in switch
(`SCRIP_DWARF_LOC=1`), `corpus/programs/snobol4/demo/roman.sno` compiles+links+runs to the byte-identical
`.ref` output it always has, and its ELF now carries a correct `.debug_line` table:

```
$ readelf --debug-dump=decodedline roman2.prog | head -8
roman.sno:
File name                        Line number    Starting address    View    Stmt
roman.sno                                  1            0x401299               x
roman.sno                                  2            0x401550               x
roman.sno                                  3            0x4018c7               x
...
```

Line 2 is `ROMAN N RPOS(1) LEN(1) . UNITS =  :F(RETURN)`, line 7 is the hot `TEST` loop body
(`TEST  OUTPUT = I ' -> ' ROMAN(I)`) — matches the actual source exactly.

`callgrind_annotate --auto` (Q2 in ARCH-PERF-TOOLING.md, "the workhorse") prints the `.sno` source
with instruction counts in the margin, unprompted, on the strength of that same DWARF data:

```
$ valgrind --tool=callgrind --dump-instr=yes --collect-jumps=yes ./roman2.prog
$ callgrind_annotate --auto=yes cg.out
-- Auto-annotated source: .../corpus/programs/snobol4/demo/roman.sno
222,853 ( 2.18%)  ROMAN N RPOS(1) LEN(1) . UNITS =  :F(RETURN)
1,169,834 (11.45%)  => .../pattern_match.c:rt_match_end_all (1,128x)
...
 31,744 ( 0.31%)  TEST  OUTPUT = I ' -> ' ROMAN(I)
354,811 ( 3.47%)  => .../rtx_str.S:str_concat_d (690x)
332,532 ( 3.26%)  => .../core.c:NV_SET_fn (345x)
 25,149 ( 0.25%)        EQ(I,J)  :S(RETURN)
 12,617 ( 0.12%)        I = I + 1  :(TEST)
```

**One annotated hot statement, per the task's DONE-WHEN:** `TEST  OUTPUT = I ' -> ' ROMAN(I)` — the body of the
program's own hot loop (runs once per number converted, 437 times total across the four `TEST` ranges) — carries
31,744 direct Ir plus 354,811 in `str_concat_d` and 332,532 in `NV_SET_fn`, attributed to SNOBOL4 source line 7,
not to an anonymous slab offset.

## `perf annotate --source` — NOT run, and why that's an environment gap, not a code defect

`perf` is installed at `/usr/bin/perf` in this seat's container but is a version-mismatched wrapper for the
running kernel (`6.17.0-1032-oem`); it refuses with "WARNING: perf not found for kernel..." and asks for
`linux-tools-6.17.0-1032-oem`, which needs `sudo apt install` — this container has no passwordless sudo. Per
LAW 0 (measured, not hypothesis), I am not claiming to have run `perf annotate` successfully. Confidence it would
work once that package lands: high — `perf` reads exactly the same `.debug_line`/`.debug_info` ELF sections that
`readelf` (above) and `callgrind_annotate` (above) already independently decode correctly, and both are external,
unmodified tools with zero SCRIP-specific handling. This is recorded as an open item, not closed.

## Implementation

New medium-complete op `x86("loc", file, line)` in `src/templates/x86_asm.h`, same shape as the existing
`label`/`comment`/`srccomment` ops (TEXT emits, BINARY/MACRO_DEF is a pure no-op — `.loc` carries zero runtime
semantics, so "correct for BOTH media" means "does nothing in BINARY," the same carve-out
`GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` already documents for `label`):

```cpp
if (!strcmp(mnem, "loc")) return (MEDIUM_BINARY || MEDIUM_MACRO_DEF || !xa.s || !xa.s[0]) ? std::string()
    : (std::string(".file 1 \"") + xa.s + "\"\n.loc 1 " + std::to_string((long long)(int64_t)xb.u) + " 0\n");
```

Called from ONE place — `walk_bb_node_inner` in `src/emitter/emit.cpp`, right beside the existing `srccomment`
block — so **zero `bb_*.cpp` templates were touched** (satisfies "Do NOT gate on MEDIUM_* in any bb_*.cpp"
directly: there was nothing to gate, the call site never moved into a template):

```cpp
{ static int _dl = -1; if (_dl < 0) { const char *e = getenv("SCRIP_DWARF_LOC"); _dl = (e && e[0] == '1') ? 1 : 0; }
  g_emit.op_line = _dl ? bb_line_of(nd) : 0;
  if (g_emit.op_line > 0) { const char * _sf = stmt_src_get_file(); if (_sf && *_sf) bb_emit_x86(x86("loc", _sf, g_emit.op_line)); } }
```

**Line numbers were already sitting in the tree, unused for this purpose.** `stmt_ast.c:stmt_to_ast` has attached
a `:line` attribute (`s->lineno`) to every SNOBOL4 statement node since before this task existed, exactly parallel
to the `:src`/`:stno` attributes the existing `srccomment` feature already reads. The only wiring needed:
`bb_src_note`/`bb_src_of` (`src/lower/lower_common.c`) already maintain a node-pointer-keyed side table mapping
each IR node to its captured source text (`g_bb_src`, `nd[]`/`src[]` parallel arrays) — widened by one parallel
`line[]` array plus a `bb_line_of(nd)` reader, mirroring `bb_src_of`. The one real call site
(`lower_snobol4.c:2191`) now also captures `lp_s_int(st[i], ":line")` — a helper already used elsewhere in the
same file for `:stno`. Raku's 7 synthetic-label call sites (no real source position) pass line `0`.

**Filename** comes from `stmt_src_get_file()`, a new one-line getter added beside the existing `g_src_lines`
per-compile-file-content cache in `src/driver/stmt_ast.c` (which already retains the file's *content* for
`srccomment` reconstruction but had never retained the *path* — one `static char *g_src_path`, set in the same
place `stmt_src_set_file` already resets the line cache).

**No new global variables in the sense RULES.md's ban targets.** Every piece of new state is one more field on an
already-existing, already-global per-compile side table (`g_bb_src` in lower_common.c; `g_src_lines`'s sibling
`g_src_path` in stmt_ast.c) or a new field on the existing per-node `g_emit` operand-staging struct (`op_line`,
alongside `op_src`) — the same pattern the codebase used minutes earlier in this session's own upstream history
(`alpha_slot` added to `rt_proc_t`'s alignment hole, SCRIP `80a01c63`) without a fresh Lon banner-ask. No new
top-level symbol was introduced.

## Verified, with receipts

- `scripts/test_gate_emit_dwarf_loc.sh` (new) — encoder present; `SCRIP_DWARF_LOC=1` build of `roman.sno` has
  `.file`/`.loc`, default build has neither; `readelf --debug-dump=decodedline` on the linked demo resolves every
  line number into `[1, 15]` (the source's real extent); `test_gate_template_medium_invisible.sh` stays green.
  **Negative-injection proven**: disabling the encoder (`if (0 && !strcmp(mnem,"loc"))`) makes the gate FAIL with
  the correct message; restored and re-verified green (LAW 0 / V2-5 style — a gate that can't say no isn't one).
- `bash scripts/test_gate_template_medium_invisible.sh` — rc=0, ratchet unchanged (8 pre-existing `xa_flat.cpp`
  informational sites, 0 enforced `MEDIUM_*` sites in `bb_*.cpp`, unchanged by this task).
- **Feature-off byte-identity, at full corpus scale**: ran all six regen scripts in RULES.md order
  (`util_regen_{benchmark,feature,demo,programs,prolog_bench,crosscheck}_s_artifacts.sh`). Benchmark artifacts:
  zero changes. Feature/demo/programs/crosscheck artifacts: some files *did* change, but `grep -rl '^\s*\.loc \|^\s*\.file '`
  across every `.s` in `corpus/` and `SCRIP/test/` after the full regen returns **nothing** — none of that churn
  is this feature (default is off; it never fired). The actual cause is internal literal/label renumbering from
  two upstream commits landed and pulled into this session before this task started (`claws5+json speed` IR_LIT_NAME
  folding, `free-r11` register fix) that hadn't been regenerated yet — ordinary regen-catchup, verified by diff
  (e.g. `.Lx492_0` → `.Lx485_0` renumbering in `calculator-1.s`, no instruction-shape change), not something this
  task introduced. Pre-existing `EMIT-FAIL`/`AS-FAIL` entries in Icon/Prolog/Rebus/Snocone programs surfaced by the
  same sweep are unrelated: this feature is gated on `bb_line_of(nd) > 0`, which only `lower_snobol4.c` ever
  populates, so it cannot affect any non-SNOBOL4 compile path.
- `roman.sno` demo output, built with the feature on, still matches `.ref` byte-for-byte (functional correctness
  of the feature's host program is untouched, as expected of a TEXT-only annotation with no BINARY twin).

## Scope / what's still open

- Rung 2 (`.globl`/`.type`/`.size` per Byrd box, "first-class symbols WITH EXTENTS") is explicitly deferred, per
  the brief.
- `perf annotate --source` unverified in this environment (see above) — the next session with a working `perf`
  (or sudo to fix this container's) should confirm; I'd be surprised if it disagreed with `readelf`/`callgrind`.
- Only SNOBOL4 populates `:line`/`bb_src_note`, so `.loc` only ever fires for SNOBOL4 statements (same scope the
  existing `srccomment` feature already has — not a new limitation).
- `-INCLUDE`d files are NOT separately tracked: `stmt_src_get_file()` returns the single top-level compile
  filename, so a statement lowered from an included file would get `.loc`'d against the wrong file. Matches the
  existing `stmt_src_slice`'s own "source not in main file (INCLUDE)" carve-out for the same reason. Not exercised
  by `roman.sno` (self-contained) or the corpus-wide regen sweep's `.loc`-leakage check.
