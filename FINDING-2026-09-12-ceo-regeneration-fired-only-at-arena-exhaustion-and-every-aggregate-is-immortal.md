# FINDING 2026-09-12 17:46 CDT (ceo) — regeneration fired only at arena exhaustion, and every aggregate is immortal

**Tree:** measured on SCRIP `f8421f4bd`, cured (pacing) `bebf6df1a` · seat ceo (Icon lane, row `icon-every-image-call-leaks-a-pinned-block…`, CEO-605's micro.icn abort) · cursor CEO-639.

## Measurement

`every 1 to 3000000 do image("ab\tcd")` read 564 MB RSS in both modes though image's 256-byte result is collectable (type 205 in
`SCRIP_ALLOC_HIST`; the cto's cure is on main). Telemetry: ONE regeneration, at 536 MB — arena exhaustion. The seam-side line
(`g_hp_gcline`) sat at half the arena and is consulted only at gateway seams a builtin-call loop never reaches; the assembly fast
path (`rtx_alloc.s`) carved inline against the arena END. Separately, `every 1 to N do []` retains 96 bytes per iteration
(HB_DINST 32 + HB_WS fields 64), `table()`/`set()` ~250, `list(3)` ~190, while `"x" || "y"` retains nothing: `hb_pinned()`
force-marks every pinned block live at every regeneration and slides none, so aggregates are immortal (the GC-5 row in
`ARCH-ENGINE.md`, listed "open"); 3M `image([])` times out at 120 s with 122 regenerations, each walking millions of immortal blocks.

## Cure (SCRIP `bebf6df1a`) — pacing, GC-7

The collection line sits min(128 MB, half of the remainder) past the top; the fast region carries it as `g_hp_fr.line` at offset 48
(struct 56 bytes, static-asserted, `rtx_alloc_test.c` mirrored) and the inline carve compares against it; `c_rt_gcheap_alloc` collects
at the line through the same conservative path exhaustion already used, then re-arms past the new top. `SCRIP_GC_LINE_MB` overrides;
0 restores the old policy and is the control arm. Measured: string and integer loops 150 / 146 MB RSS (m3 / m4), 12–14 regenerations;
control 564 MB. The line is 128 and not 64 because `bench_icnstr_concat_int_dispatch` read 0.21 s at 64 against 0.13 s at 128 and under
the old policy (wall, three runs each — a scouting datum, not a grid). Gate `test_gate_gc_pacing_bounds_a_churning_program.sh`, wired.
Control arms: four smokes green both modes; the rtx inventory gate green; the coo's next pass on every language.

## Not cured here — named as the rank-0 blocker

`icon-aggregate-blocks-are-immortal-pinned-so-every-list-table-and-record-is-retained-until-the-arena-fills`: take HB_DINST and HB_ARR
out of `hb_pinned()`, mark them only when reached (the DT_DATA case already traces fields and registers the `.u` and `fields` slots; it
must also mark the instance, its fields block and its element array and register the element-array slot), keep raw C-stack references
conservative. Until it lands the image row's list arm stays red. Also named: `image("q\"x\\y")` differs from iconx by one backslash.
