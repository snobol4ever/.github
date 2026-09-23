# FINDING 2026-09-22 hq_raku — `__rk_arr_sort`'s block-comparator scratch lived on the GC heap across the callback

**Row:** `raku-silent-wrong-answers` (claimed by hq_raku under MODE DECTET, CEO-1129: "the rows in your lane
that say the collector DOES NOT WORK ... wrong answers under collection, silent segvs, crashes at the tiny
arena" — component 4 of the GC acceptance bar, WORKING, previously frozen at the 2026-09-20 stand-down
reading and un-refreshed since the collector's frame-map/safe-point work moved).

## Measured, not assumed

`test_gate_raku_master_is_clean_at_the_tiny_arena.sh` (`SCRIP_HEAP_MB=1`, band `1 3 5 8 16`), tree
SCRIP `4336cb8ee` / corpus `b3dd2932b` / binary `84d80bfb4f63`: three (entry, mode) pairs diverged
PASS(control) -> CRASH(stress N) against the control arm, both modes, at stress 1/3/5/8 (not 16 -- a
band, never a point):

- `ladder__rung18_two_arg_block` — `my @n=(3,1,2); say @n.sort({ $^b <=> $^a });`
- `ladder__rung18_two_arg_block_sort_string` — `my @w=("pear","fig","kiwi"); say @w.sort({ $^b leg $^a });`
- `ladder__rung19_block_methcall_sort_by_key` — `my @w=<aa b ccc>; say @w.sort({ $^a.chars <=> $^b.chars });`

All three are `.sort({ two-arg block })` — the class is the mechanism, not any one program (RULES.md
§ ACT ON ABLATION). Extracted standalone and reproduced directly:
`SCRIP_HEAP_MB=1 SCRIP_GC_STRESS=1 ./scrip --run ladder__rung18_two_arg_block.raku` → SIGSEGV rc=139,
both m3 and m4. gdb backtrace: SIGSEGV inside `__GI_____strtol_l_internal`, called from
`rk_elem_descr` (`by_name_dispatch.c:331`), called from `rk_block_cmp` (`:337`) with
`x` pointing at `\333`-filled (0xDB poison) memory and `y == NULL` with a stale `yl=50`.

## Root cause

`__rk_arr_sort`'s two-arg-block path built its element scratch (`els`/`lens`, plus each element's
null-terminated copy) via `rt_pvec_alloc`/`rt_wsb_alloc` — both GC-heap allocators (`HB_PVEC`/`HB_WSB`,
confirmed at `gc_heap.c:304,333`) — then held those raw C pointers across `rk_block_cmp`'s call into
`rt_call_proc_descr`, which re-enters EMITTED Raku code (the sort block) and can itself allocate. Nothing
roots a GC-heap block reachable only from a C local on the runtime's own (unmapped) C stack frame — the
same class already named for `__rk_arr_map`'s accumulator (row
`raku-gc-thirty-six-programs-return-a-silently-wrong-answer-under-forced-collection...`, cured at SCRIP
`a7ba722b3`), recurring here in a different builtin. Under `SCRIP_GC_STRESS`, the collector reclaimed the
scratch mid-sort (nothing else referenced it), so the next comparison read vacated/poisoned or reused
memory.

**Ruled out, measured rather than assumed:** the block-LESS numeric/string sort path (same file, `nargs>=1`
handler) does the identical scratch-allocation shape but never re-enters emitted code during the sort
(pure `strtoll`/`strcmp`), so nothing it does can trigger a collection mid-sort. Tested a 12-element string
array across the full declared stress band (0/1/3/5/8/16) — clean at every point. Left untouched: the cure
form follows the box (CEO-1129), and this box does not exhibit the defect.

## Cure

Moved the two-arg-block path's scratch (`els`, `lens`, each element's copy) off the GC heap entirely —
plain `malloc`, freed once the final `rt_wsb_alloc`'d result string is built (that last allocation happens
after the sort loop, with no further re-entry into emitted code, matching the pattern every other safe
caller in this file already uses). `SCRIP/src/runtime/by_name_dispatch.c`, one function, no new globals, no
change to the collector's root-scan or the shared spine — a LOCAL, one-builtin cure (PACE RULES rule 7).

## Verification

- All three witnesses PASS, both modes, across control/arena/stress 1/3/5/8/16.
- Raku master board unchanged: `853/929` m3, `853/929` m4 of 929, `arena_mb=1` — identical to the
  pre-fix reading, confirming the control arm (and the block-less sort path) was never in question.
- `test_smoke_raku.sh` 10/10 both modes; `test_smoke_snobol4.sh` 7/7; `test_smoke_icon.sh` 15/15 both
  modes (checked since `by_name_dispatch.c` is shared across languages).
- Full `test_gate_raku_master_is_clean_at_the_tiny_arena.sh` re-run post-fix, tree `d9c66f2c6`: all six
  axes (arena, stress 1/3/5/8/16) vs control, 1858 pairs each — `divergent=0 inconclusive=0 vanished=0`
  on every one. "Raku's master does not change its answer under collection." `.github/SCORE.md`'s
  `raku-master` row rewritten from this reading (`.github` `feee008d`).

## Not attempted / named as unmeasured

- The `nargs>=1` (block-less) sort path is UNCHANGED — measured clean at the one shape tried (a
  12-element string array); a larger or differently-shaped input is not ruled out and is not this
  finding's population.
- Other `by_name_dispatch.c` builtins that re-enter emitted code via `rt_call_proc_descr` while holding
  C-local scratch (e.g. `__rk_arr_reduce`, immediately below this handler in the file) were NOT audited
  for the same class in this pass — named as a candidate for the shared pass-B conservative auditor
  rather than assumed clean.
