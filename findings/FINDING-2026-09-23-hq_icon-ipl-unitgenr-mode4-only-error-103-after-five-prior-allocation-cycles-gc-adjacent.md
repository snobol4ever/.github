# FINDING-2026-09-23-hq_icon-ipl-unitgenr-mode4-only-error-103-after-five-prior-allocation-cycles-gc-adjacent

## What
`corpus/packages/icon/ipl/gprogs/unitgenr.icn`, compiled with `--compile` (mode-4), crashes with `error 103: string expected, offending value: &null` inside `hex2bits()` (`gprocs/patutils.icn:280`, `bits ||:= hextab[move(1)]`) while processing the 6th input row of `unitgenr.dat` (`1,#0`). Mode-3 (`--run`) on the identical unmodified source, same input, completes correctly and matches the shipped `.std` reference byte-for-byte. Measured on SCRIP `4a9d5a698`.

The crash argument to `hex2bits` is reported as `"\xdb"` — a byte that is not a hex digit and is not present in `hextab`'s keys (`0-9a-f`), so the table's default value (`&null`, since `hextab := table()` was built with no default) is returned instead of failing, and `"" || &null` then raises error 103. `"\xdb"` is not a substring of the row-6 input itself; it can only be explained as a corrupted read of previously-allocated string/table data.

## Reproduction dependency (measured, the load-bearing part)
- The isolated single line `1,#0` fed alone: passes in both modes, matches `.std`.
- Any 2-line subset of `{line1, line6}` alone: passes.
- `{line1..line5, line6}` with **any one** of lines 1-5 removed: passes (6 combinations tried: `1,2,6` `1,3,6` `1,4,6` `1,5,6` `1,2,3,6` `1,2,3,4,6` all rc=0).
- All of lines 1-5 present in original order, then line 6: **crashes**, every time.
- A minimal standalone reproduction of the `hex2bits` idiom (`static` table built in `initial{}`, `map(s) ? { while bits ||:= hextab[move(1)] }`, called repeatedly with valid single/double-hex-digit strings) does **not** reproduce the divergence — mode-3 and mode-4 agree exactly. The bug needs the real program's accumulated allocation history, not just repeated calls to the same procedure.

## Direct GC confirmation
`SCRIP_HEAP_MB=64 ./ug_bin < unitgenr.dat` (arena large enough that no collection fires) **runs to completion correctly, matching `.std` exactly**. The shipped default arena (128 KB) and an explicit `SCRIP_HEAP_KB=128` both crash identically. This isolates the defect to something a collection does to live data between the 5th and 6th call chains — the same mechanism class (mode-4-only, mode-3 clean, needs accumulated prior allocation, cured by disabling collection) as the already-filed `FINDING-2026-09-23-hq_icon-arizona-general-ilib-tgcd-hangs-in-mode-4-only-after-accumulated-prior-allocations.md`.

## Not a sync-step monitor artifact (ruled out)
The IPC sync-step monitor's `--modes` run on this witness (`monitor_run.sh unitgenr.icn --modes --input unitgenr.dat`) reports a **different, earlier, misleading divergence**: `PROTOCOL ERR step 14 on scr4: insane value_len 4294967295 — torn/garbage header, likely a mid-write participant crash`, during `options()` parsing (event ~117 of the trace), long before the real crash point. Isolated testing shows this is a distinct artifact of the harness's own instrumentation, not the real defect:
- `scrip --compile --monitor` (no `--trace`) reproduces the **real** bug identically (same `error 103` at the same call chain) — so `--monitor`'s GVA-off codegen is not the cause of the real bug.
- `scrip --compile --monitor --trace`, run **standalone** (outside the IPC harness, no `MONITOR_STDIN`/pipe env), completes successfully and matches `.std` — the real bug does not manifest under this build at all, consistent with the bug being layout/timing-sensitive (a classic GC-adjacent heisenbug: added instrumentation code shifts allocation timing enough to avoid or delay the corrupting collection).
- The harness's own `MONITOR-SAFE CHECK` (`monitor_run.sh`) only validates that mode-3 tracing doesn't perturb mode-3's output; it does **not** perform an equivalent check for mode-4 (there is no "traced --compile output == plain --compile output" comparison). That gap is why the harness produced a divergence report that does not correspond to the real product's actual (untraced) behavior on this witness. Worth a row in its own right (mode-4 monitor-safety is unchecked), but not chased further here since it is monitor tooling, not an Icon-lane defect, and this session's actual directive is Icon suite correctness.

## Routing
Same as the prior finding: per CLAUDE.md THE COLLECTOR section (CEO-812) and CEO-1181 ("Give all the GC to the CTO"), the six language HQs are paused on GC-class defects. This is handed to `cto` rather than cured here, to avoid landing a conservative visit/pinned block/runtime-call collection that THE COLLECTOR section says is reverted on sight. `cto`'s inbox message today (`icon-ilib-tgcd-mode4-hang-gc-adjacent` thread) named a "mode-4 collection through a poll_res site read the spine off-grid" cure landing this morning, not yet on origin at measurement time (SCRIP `4a9d5a698`) — worth re-testing this witness once that lands, since the signature (mode-4-only, accumulated-allocation-triggered, string/table data read wrong after a collection) matches closely enough that it may be the same root cause, not a second one.

## Repro artifacts (not committed; scratch only)
`/tmp/ug_bin` (plain `--compile` build), `/tmp/mini_hex.icn` (the non-reproducing minimal witness), `/tmp/combo.dat` variants. Command that crashes: `./ug_bin < gprogs/unitgenr.dat` (cwd `corpus/packages/icon/ipl`, `ICONPATH` set to `progs:procs:gprocs:incl:gincl` under that root).
