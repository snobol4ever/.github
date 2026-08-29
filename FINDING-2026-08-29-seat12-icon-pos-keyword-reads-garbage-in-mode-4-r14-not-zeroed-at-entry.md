# FINDING — `&pos` reads garbage in mode-4 for `icn_cells_graph` programs: entry code never zeros `r14`

**Seat:** seat12 · **Date:** 2026-08-29 · **Row:** `tests-consolidate-icon` (found while characterizing `rung36_jcon_kwds.icn`/`rung36_jcon_subjpos.icn`'s flagged-but-untraced "m3 PASS, m4 FAIL" divergence, per `tests/icon/KEEP.md`'s own note: *"Same shape of finding as `rung38_cset_embedded_nul`... not confirmed to be the SAME cause, not traced."*)
**Not fixed in this commit.** Root-caused to the exact missing instruction and confirmed causally with a throwaway local edit (built, tested, reverted — no net diff); the real fix belongs to its own row, not this one.

## THE SYMPTOM

Both files diverge on the *very first* line of output — before either program has ever assigned to `&pos`:

```
rung36_jcon_kwds:      m3 "        &pos: 1"        m4 "        &pos: 4251097"
rung36_jcon_subjpos:   m3 "  &pos=1   &subject=\"\""   m4 "  &pos=4226521   &subject=\"\""
```

`subjpos.icn` makes this maximally clean: its very first statement is `ws()`, which dumps `&pos` and
`&subject` before touching either. Every subsequent line in the whole 60-line diff is byte-identical
between modes — once the program explicitly assigns `&pos := n` anywhere (which it does, repeatedly,
via `setpos()`), the garbage gets overwritten and everything downstream matches `.expected` exactly.
**The bug is isolated to `&pos`'s *default* value specifically — nothing else.**

## ROOT CAUSE — exact, both sides cited

`&pos` is not read from a memory cell; it's computed as `r14 + 1` directly in the shared Byrd-box
template (`src/templates/bb/bb_keyword_icon.cpp:36,67`, comment: *"KEYWORD_pos_reg [always r14+1:
register cursor is the source of truth]"*). So `&pos`'s correctness at any point depends entirely on
what `r14` holds — and the two execution modes set it up asymmetrically at program entry:

**Mode-3 (`--run`), correct:** `src/driver/scrip.c:1862` routes Icon programs (`is_icon`) through
`rt_outer_call_delta0`, not `rt_outer_call`. That function (`src/runtime/rt/rt.c:52-59`) is exactly:
```c
"rt_outer_call_delta0:\n"
"  push %r14\n"
"  xor %r14d, %r14d\n"     /* <- zeroes r14 before the call */
"  call rt_outer_call\n"
"  pop %r14\n"
"  ret\n"
```

**Mode-4 (`--compile`), missing:** `src/driver/scrip.c:1440-1447` emits the standalone binary's `main:`
entry. The `if (bbg->zframe_graph && !bbg->icn_cells_graph)` branch explicitly emits `xor r14d, r14d`
before jumping to `main_α`. The `else` branch — which is what any Icon program taking the
`icn_cells_graph` shape falls into — is just:
```c
} else
emit_textf("  jmp main_\xce\xb1\n");
```
No `r14` zeroing at all. `r14` is left holding whatever the OS/loader/CRT happened to put there at
process start, read moments later as `&pos`.

**Why this hits so broadly:** `icn_cells_graph` is set to `1` for essentially every Icon program by
default (`src/lower/lower_icon.c:1176,1249` — `SCRIP_ICN_LEGACY` must be explicitly set to fall back to
the old path). This is not a narrow edge case; it's the default Icon lowering shape, so any Icon program
compiled with `--compile` that reads `&pos` before ever assigning to it hits this.

## CONFIRMED CAUSALLY, NOT JUST BY INSPECTION

Added one line to the mode-4 `else` branch (`emit_textf("  xor r14d, r14d\n");` before the `jmp`),
rebuilt, re-ran both witnesses: `kwds` and `subjpos` mode-4 output became **byte-identical** to mode-3
(and to `.expected`) — no other line moved. Reverted immediately after confirming (`git diff` clean,
rebuilt to restore the baseline binary) — this repo now carries zero net change from this finding.

## BLAST RADIUS (flagged, not swept)

Any Icon program, compiled via `--compile`, that reads `&pos` (directly or through anything built on
the same `r14`-as-cursor convention) before the first explicit assignment to it. Did not sweep the
corpus for other consumers, and did not check whether the same gap exists for the `zframe_graph &&
icn_cells_graph` (both true) or other flag combinations beyond the two witnesses tested — a real fix
needs that fuller sweep plus the standard floor (pristine build, full gate battery, both modes,
multi-language regression since the `else` branch is reachable by non-Icon `bbg` shapes too whenever
`zframe_graph` is false) before landing, which is why it isn't landed here.

## DISPOSITION

Not attempting the fix here — out of this row's lane (`tests-consolidate-icon` is suite *conversion*,
not runtime bug-fixing, same discipline this task has applied to every other bug it's found: `proto`,
`scan1`, `&ascii`/`&cset`, `&level`). The one-line shape of the fix is now precisely known
(`xor r14d, r14d` before the `jmp main_α` in `scrip.c`'s mode-4 `else` branch, or route Icon's `main:`
entry through the same `is_icon`-aware zeroing mode-3 already has) for whoever picks it up — but it
needs its own verification sweep, not a squeeze-in. `rung36_jcon_kwds.icn` and
`rung36_jcon_subjpos.icn` stay loose (a bug, not a permanent design choice, same precedent this task
uses everywhere else). Mailed hq_C. `tests/icon/KEEP.md`'s `kwds`/`subjpos` entries updated to point
here instead of carrying "not confirmed... not traced."
