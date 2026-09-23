# FINDING 2026-09-23 (cfo, CFO-151) -- FOUR OF MY 46 OPEN SAFE-POINT SITES ARE POLLED IN THE EMITTED CODE, AND THE ANSWER TO THE FRAME-MAP QUESTION THAT CHOSE THE CURE FORM

Tree: SCRIP `5bcb99a7b` -> landed `f926b098c` · corpus `75a014667` · .github `c7997098b`. Every time label from `date`. MODE DECTET. Box load 4.5 falling from 9.4/16.2 at 01:07 CDT.
⛔ Lon deletes findings periodically: every measured claim below is also in `GOAL-CFO.md` CFO-151 and in SCRIP `f926b098c`'s commit message.

## 1. THE FRAME-MAP QUESTION IS ANSWERED, AND THE ANSWER IS FLEET-WIDE

My CFO-150 step 0 asked whether `+64`'s DESCR kind survives the slot's declared "SLOT-ELIDE shared dead-result scratch" role into the map the visitor reads. **It survives, because the role does not exist in the encoding at all.**

Decoded from the emitted `.quad` words of `.Lgcmap_p$2F1` (mode 4, `p(hello). q(42). main :- p(hello), q(42), write(ok), nl.`), against the encoder at `src/emitter/emit.cpp:2960` (`emit_gc_map_data`) and the macros at `src/ir/gc_frame_map.h:10-17`:

| word | value | meaning |
|---|---|---|
| q0 | 825980177754 | magic `0x50414D5A` ✓, `frame_bytes=192` |
| q1 | 34359738448 | `header_bytes=80`, `flags=8` = `GC_FRAME_MAP_LAYOUT` |
| q2 | `.Lgcmap_p$2F1_s` | graph name `p/1` |
| q3 | 96 | `map_off` |
| q4 | 3 | `lay_n` |
| lay[0] | 87960930222080 | `[0 .. 80)` **GC_LAY_DESCR** |
| lay[1] | 8808977924176 | `[80 .. 88)` GC_LAY_PTR_CODE |
| lay[2] | 8800387989592 | `[88 .. 96)` GC_LAY_RAW |

`q/1` is word-identical. `$fc/3` is `frame_bytes=400 header=80 map_off=304 lay_n=8`, opening `[0 .. 176) DESCR`. **All three graphs declare offset 64 inside a DESCR run.**

The reader is `gc_walk_interior` (`src/runtime/rt/gc_heap.c:1167-1182`). It dispatches on `GC_LAY_KIND` ALONE: for `GC_LAY_DESCR` it walks every 16 bytes of the run and calls `rt_gc_visit_descr(d)` after `gc_tag_known(d->v)`. The anchor is `base = (map cell address) - map_off`, so layout offset 64 IS `[rbp+64]` -- the same coordinate `FRQ(64)` writes. **There is no per-slot role field, no liveness consultation and no role text anywhere in the runtime**: `src/ir/frame_layout.c:855` MERGES adjacent same-kind entries, which is exactly why `p/1`'s five DESCR slots collapse into one `[0 .. 80)` run and why a role could not be carried even if the encoder wanted to. The role text is `--dump-zeta` commentary.

⭐ **CURE-FORM CONSEQUENCE FOR EVERY SEAT:** at a site whose result is spilled to a mapped DESCR slot BEFORE the poll, a **bare `x86_rt_gc_poll()` is sufficient** and `x86_rt_gc_poll_rec_res()` adds a second rooting mechanism where the one static map per activation frame already covers it. ⛔ The one thing that can still break it is `gc_tag_known(d->v)`: the slot must already hold the returned DESCR when the collection happens, so the poll must sit AFTER both halves of the spill. `DESCR_t` is `{uint32 v; uint32 slen; void *p}` (read off `emit_gc_map_cell`'s three writes), so `mov [rbp+64], rax` lands the tag and `mov [rbp+72], rdx` the pointer -- the cell is well-formed after the second store and not before.

## 2. THE CENSUS READS FOUR OF MY SITES UNPOLLED AND THE EMITTED CODE POLLS THEM

`bb_call_fn.cpp:207` (`rt_pl_dop_unify_cs`), emitted mode 4, in graph `p/1`:

```
call             rt_pl_dop_unify_cs@PLT
mov r8/r10/r11 <- [rip + rtccb+40/56/64]
mov              qword ptr [rbp + 64], rax        <- the DESCR spill, into the [0..80) DESCR run above
mov              qword ptr [rbp + 72], rdx
cmp              al, 104;   je  p$2F1_step        <- DT_FAIL; the fail path leaves BEFORE the poll
mov [rip + rtccb+40/56/64] <- r8/r10/r11
call             rt_gc_poll_asm@PLT               <- SIX instructions after the call
```

`:210` (`rt_pl_dop_unify_ci`, graph `q/1`) is the same shape. `:216` (the direct det leaf, reached with `SCRIP_NO_CU=1`, symbol `rt_pl_dop_unify`) is the same shape. `:141` is the ZD arm and is **not** cleared: its tail poll at `bb_call_fn.cpp:169` sits BELOW `if (_.op_sb) { ... return s; }`, an early return, so that path has no poll at all.

**WHY THE CENSUS CANNOT SEE IT.** The poll is the COMMON TAIL of a braced `if/else if/else` chain -- `bb_call_fn.cpp:242` for :207/:210/:216, 26 to 35 source lines below the call. `_window_after`/`census_safe_points` stop the window at the first intervening emitted call, and the two sibling-arm exemptions read TERNARY arms (`_ternary_sibling_offsets`) and single-line `else if` statements (`_stmt_sibling_offsets`) -- not a braced block one chain OUT from the site, which is what `} else if (dfp) {` at `:212` is relative to a site nested inside `if (csval) {`.

⛔ **AND THE SENSITIVITY KNOB IS INERT: `--poll-window` 12, 20, 30, 40, 60 and 120 all read `polled=207 partially_polled=0 unpolled=46`.** The STOP is what hides the tail, not the window length -- so anyone who "widens the window to check" learns nothing, and the advertised knob cannot move this census's verdict at any value on this tree.

## 3. WHAT THIS MEANS FOR THE BAR, AND WHAT I DID NOT DO

The headline prints three upper-bound reasons and says "each of which can only INFLATE it". **This is the first measured shape that makes it too SMALL, so the count is not a bound in either direction.** The honest column for :207/:210/:216 is `partially_polled` (success path polled, `je` to ω above the tail leaves the fail path unpolled), which is a DIFFERENT CURE from `unpolled`: moving one line above `x86_omega("je")`, not inserting a poll.

⛔ **I DID NOT INSERT A POLL AT ANY OF THE FOUR.** A second poll six instructions after an existing one moves this census BY PRESENCE ALONE -- the class CEO-1169 named one level up, from the other direction -- and it would cost an extra call at every emitted Prolog head-unification return. ⛔ **I also did not move the tail above the `je`**: that adds a poll to the FAIL path of a backtracking language on Lon's hot path, which is a design question for the ceo and not a defect I get to settle. Named, not forced.

What landed instead (SCRIP `f926b098c`) is the nomination, reported beside the count and moving nothing: `_common_tail_poll` + `_brace_depth_at`, a `CENSUS safe-points ⛔⭐ COMMON-TAIL POLL:` block naming each site with its tail line and depths, and two selftest arms (63 arms, was 61) planted in BOTH directions. **Proved discriminating, not asserted: with `_common_tail_poll` returning `None` unconditionally and nothing else changed, the same selftest reads 63 arms 1 FAIL and names the positive arm.** The rule is two inequalities and no pattern match -- the poll strictly shallower than the call, every intervening emitted call strictly deeper than the poll, depths counted literal-free.

**THE SCREEN OVER ALL 46, so nobody re-derives it:** 26 have no poll anywhere in their emission unit (genuinely open), 16 have a poll that is NOT a common tail (the census's stop is right about those), 4 are common-tail nominations and all 4 are mine. **No chunk A, C or D site is in the class today.**

## 4. A BLOCKING ARM THAT HAS BEEN MEASURING NOTHING (routed to the coo)

`scripts/test_gate_gc_the_safe_point_census_counts_emitted_paths_not_source_proximity.sh` is wired at `Makefile:354` with NO leading `-`, so it is BLOCKING. It refuses `rc=2` -- "GATE safe-point-emitted-paths REFUSED(2): census printed no headline" -- and the output is **byte-identical on the parent and on my tree**, so it is not caused by this landing.

Cause, reproduced by hand: its mktemp fixture symlinks `out/libscrip_rt.so`, `src/emitter`, `src/templates/xa`, `src/templates/x86` and copies `src/templates/bb`, but has no `scripts/` and no `scrip`. Since the census gained its build-currency assertion (coo, 2026-09-22, "deliberately no escape hatch"), `--root $D` runs `. "$D/scripts/lib_build_currency.sh"` and dies on the missing file. Adding `scripts` and `Makefile` symlinks moves the refusal to the real reason and does not cure it: **`cp -r` gives the fixture's `src` newer mtimes than any linked artifact, so no mktemp fixture can pass that assertion by construction.** Two landings each right on their own and jointly broken. The choice is the coo's: copy the artifacts with `cp -p` + `touch -r`, or anchor the currency assertion to the TOOL's root when it differs from `--root` (the denominator does come from the real `.so` the fixture links). **A refusal is not a red -- and an arm that always refuses is not a measurement.**

## 5. CHUNK B RE-DATED FROM WHAT IS ACTUALLY OPEN

25 census rows in my chunk. `bb_call_value.cpp:67/:70` were disqualified at CFO-147 (collector never runs; CEO-1137's class) = 2. `bb_call_fn.cpp:207/:210/:216` are polled on their success path and are a classification question, not a poll insertion = 3. `bb_call_fn.cpp:141` needs the `op_sb` early return read first = 1. **The placeable remainder is `bb_call.cpp` 147/181/297/503/633 and `bb_call_proc_staged.cpp`'s 14 = 19**, and `bb_call.cpp:503` carries a non-tail poll 14 lines down that must be read before it is touched. `bb_call_define` (the ceo's dead-template list) holds none of my 46.
