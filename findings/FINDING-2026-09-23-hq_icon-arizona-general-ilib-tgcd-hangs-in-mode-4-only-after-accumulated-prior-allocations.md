# FINDING-2026-09-23-hq_icon-arizona-general-ilib-tgcd-hangs-in-mode-4-only-after-accumulated-prior-allocations

## What
`corpus/packages/icon/arizona_tests/general/ilib.icn`, compiled with `--compile` (mode-4), hangs (rc=124 under `timeout 15`) partway through `tgcd()`'s 9x9 `gcd()` table, at the 4th value of the `m=30` row (computing `gcd(30, 5)`). Mode-3 (`--run`) on the identical unmodified source completes correctly and matches the pristine Arizona `iconx` oracle byte-for-byte. Measured on SCRIP `d85e6186d` (the control tree, before this session's two Icon cures) and reconfirmed on `c8d96c8d8` (after) — **not caused or cured by this session's swap/reversible-assign/concat fixes**.

## Reproduction dependency (measured, the useful part)
`gcd(i,j)` uses the `i <:= -i;` idiom (Icon's `<` returns its right operand on success, so an augmented `<:=` negates `i` only when `i` is negative — an absolute-value idiom, not a bug in itself).

- Isolated single call `gcd(30, 5)`: mode-3 and mode-4 both return `5` instantly. No hang.
- Isolated `tgcd()`'s full 9x9 loop (81 `gcd()` calls, including the exact `gcd(30,5)` call) as a **standalone program** (just `main() { tgcd() }` + `gcd` + hand-written `right`/`repl` helpers, no `link`): mode-3 and mode-4 both complete correctly, matching each other line-for-line. No hang.
- The **unmodified, full** `ilib.icn` (which runs `convert:`, `datetime:`, `factors:` sections — many list/table allocations, `prime()`/`genfactors()` generator use, `squarefree()`, etc. — *before* reaching `tgcd()`): mode-4 hangs at the same `gcd(30,5)` call; mode-3 does not.

So the trigger is not `gcd`, `<:=`, or `tgcd`'s loop shape in isolation — it requires the **accumulated allocation/execution history** of the preceding ~90 lines of `main()` in the same process, and it is mode-4-only (MODES-MAY-DIVERGE territory, not a semantic bug reachable from source alone).

## Why this reads as GC-adjacent, not an Icon-frontend bug
This session also observed (unrelated, same corpus family) the IPL package suite aborting several `gprocs`/`gprogs` programs with `rc=134 [ZHP] HARD CAP REACHED: 4096 KB is committed` (the CEO-1101 hard heap cap). A hang that only appears after substantial prior allocation, in compiled code only, is the shape of a collection (or an armed-but-mishandled collection point) interacting badly with a live value across the `<:=`/`repeat` control flow — not something an isolated 9-line reproduction can be expected to trigger, since it never accumulates enough heap to reach a collection.

## What this is NOT
Not a regression from this session's landing (`c8d96c8d8`): reproduces identically on the pre-landing control tree `d85e6186d`.

## Routing
Per CLAUDE.md's THE COLLECTOR section (CEO-812) the six language HQs are paused on GC; "all the GC goes to the cto" (CEO-1181). This finding is handed to the cto rather than cured here — an Icon-lane fix would risk exactly the "landing that adds a conservative visit, a pinned block or a collection inside a runtime call" class that section says is reverted on sight. If it turns out NOT to be GC (e.g., a frame/coroutine leak from the earlier `prime()`/`genfactors()` suspend chain specifically, unrelated to heap pressure), that would be hq_icon's own to take back up.

## Repro artifacts (not committed; scratch only)
`/tmp/zona_test/ilib_ctrl.bin` (control-tree compile), `/tmp/tgcdonly.icn` (the standalone non-repro), `/tmp/gcdrepro2.icn` (the 81-call non-repro). Command that hangs: `timeout 15 ./ilib.bin < /dev/null` where `ilib.bin` is `arizona_tests/general/ilib.icn` compiled with `--compile` and linked against `out/libscrip_rt.so`.
