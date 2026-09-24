# FINDING 2026-09-24 hq_icon: the cset registry goes weak, so a dead computed cset leaves the collector

Row `icon-deal-the-shuffle-and-random-path-is-twenty-times-slower-than-iconx-in-both-modes` (hq_icon, MODE DECTET).
Base SCRIP `8b6cb3607`, the cure on `300e59ca3` plus the patch below. RT_OPT `-O0`, incremental `make`. The box sat at
load 15 to 47 all sitting, so CPU figures are quoted as ratios between runs made back to back, never as absolute times.
The measured claims are folded into the row's baton ledger and NEXT in the same landing.

## 1. THE OWNER, MEASURED

deal `-h 1000` in mode 4 at the shipped 128 KB window read **1248 ms CPU against iconx's 38 ms** (the row's own DONE-WHEN,
5-run medians) on `8b6cb3607`, with **3020 collections** and 172,464 live bytes at exit (the `[GC-EXERCISE]` line).

`perf` works on this box without valgrind. The default `/usr/bin/perf` wrapper refuses for want of the oem kernel's
tools package, but the generic-kernel binary `/usr/lib/linux-tools-6.8.0-138/perf` records user-space call graphs fine.
Its profile at the shipped window: `gc_blk_of` 50.5% self, `gc_collect_ex` 16.4%, and **`kw_cset_gc_roots` 20.5%
inclusive, plus most of the 8.7% of `gc_blk_of` called directly from the slot fix-up loop**. About 40% of the run is the
collector visiting the cset registry.

The cause: `keywords.c` keeps each cset's length and 256-bit membership keyed by its pointer, and `kw_cset_intern`
appends every DISTINCT computed cset. `kw_cset_gc_roots` rooted every entry, so no computed cset ever died. deal
computes a few thousand distinct suit-subsets, and every collection visited, marked, slot-registered, forwarded and slid
every one of them.

## 2. TWO CURES TRIED AND REFUSED, SO NOBODY REPEATS THEM

- **Not registering computed csets that carry no NUL** (their length is `strlen`). deal fell to about 72 ms, but a
  cset-scanning microbenchmark (`upto`/`many` over two computed csets, 40 passes over a 12 KB subject) went
  **951,383,962 → 1,465,670,508 Ir, +54%**. `rt_scan_needle` calls `kw_cset_len` once per character, and an
  unregistered pointer falls through to the content hash plus `strlen`. `rt_icn_cset_member` also loses the bit table.
  REVERTED.
- **Moving the registry's strings to the compile-time arena** (immortal, invisible to the collector). Ruled out without
  building it: runtime use of the compile-time arena is the `arena_in_runtime` debt the allocator ratchet
  (`scripts/c_allocator_baseline.tsv`) is driving down.

## 3. THE CURE: THE UNNAMED ENTRIES ARE WEAK

A cset is a value. An unnamed interned result that no root reaches is unobservable, and the next intern of the same
content makes a fresh block holding the same value. The cto ruled this CEO-812-compatible (no conservative visit) on the ASK.

- `kw_cset_gc_roots` roots only named keyword csets (`&lcase` … `&cset`, and their names). A plant,
  `SCRIP_GC_PLANT_CSET_STRONG=1`, restores the strong rooting and prints a once-per-process proof line.
- `gc_collect_ex` calls `kw_cset_gc_weak()` **once, after the mark drain and before forwarding**. For each unnamed
  entry it asks the new `rt_gc_weak_keep(&ptr)` (seven lines in `gc_heap.c`): if the block is outside the heap, keep it;
  if it is marked, slot-register it so forwarding slides it; otherwise tombstone it (`ptr = NULL`, `len = -1`). Any drop
  also clears the 64-entry `rt_icn_cset_register` pointer memo, so a stale address can never short-circuit a registration.
- The registry compacts and re-indexes on its next lookup. `kw_cset_hindex_refresh` already rebuilt the pointer index
  once per collection generation; it now first calls `kw_cset_compact`, which removes tombstones and rebuilds the content
  index only when something was removed. Named entries always precede unnamed ones (`kw_cset_prime` runs before the
  first unnamed append), so the two cached keyword indices (`&ascii`, `&cset`) never shift. No new global: an earlier
  cut's file-static dead flag was removed in favour of the unconditional compaction pass.

## 4. EVIDENCE

**deal itself.** `-h 1000` m4 at the shipped window: **3020 → 434 collections**, **172,464 → 49,856 live bytes at exit**, CPU
about **15x lower** in back-to-back pairs (2789 → 179 ms at load 17; 1698 → 127 ms at load 24). Answers are byte-identical
to iconx 9.5.25a in both modes. The row's DONE-WHEN is still RED after the cure: about 150 ms against iconx's 50, measured
at load 17.

**Instruction counts with no collection** (`SCRIP_HEAP_KB=262144`, callgrind, one witness binary run against two equal-length
library copies, so the library is the only difference): the scanning microbenchmark reads **951,383,962 → 951,382,967 Ir**,
and deal 258,734,977 → 258,829,630 Ir (+0.04%). An intermediate cut had put the compaction's locals inside
`kw_cset_hindex_refresh`, which cost one instruction per registry lookup (+3.84M Ir on the microbenchmark). Moving
compaction into its own `noinline` function removed that.

**The weak path is exercised, not just present.** A witness keeps some computed csets live in a list and a table, lets
the rest die, and holds a NUL-carrying complement (`~'abc'`, 253 characters) whose length only the registry knows. It
matches iconx in both modes at stress 0, 1, 3 and 5 on both trees. Under gdb it made 50 real compactions over 50
collections at stress 0, and 1700 over 44,916 at stress 1.

**The tombstone is never read** (the cto's first condition). The witness runs under `SCRIP_GC_PLANT_FLIP=1`, which copies
every live block to disjoint ground and makes all old ground `PROT_NONE`, so a dangling entry would fault where it is used.
At stress 1 and 3, in both modes, it matched iconx, the flip plant's proof line printed, and no `[ZGC-STALE]` report
appeared. deal `-h 30` m4 under f1 is also identical to iconx, over 7788 collections.

**The gate.** `test_gate_icn_the_cset_registry_is_weak_so_a_dead_computed_cset_leaves_the_collector.sh` is wired into the
blocking set and `gate_wiring.tsv`. Its six arms: deal `-h 1000` matches iconx in both modes; the strong-rooting plant
applies and still matches; its collection count is at least 3x; its live bytes are higher; its CPU is at least 2x; and a
120-iteration flip witness (529 compactions) matches iconx in both modes under f1 with no stale read. It reads **PASS 6/6 on
the cure, in about 7 s**. A copy run against the control tree `8b6cb3607` read **RED on arms 2–5**: no plant there, and
3020 collections in both runs.

**The population machine** (`util_gc_population_machine.py icon`, control worktree `8b6cb3607` versus the cure; only
`src/parsers/pascal` differs between that control and the cure's parent `300e59ca3`, so for Icon it is the parent). Arms
nogc, s0, s1 and f1, both modes, 826 entries:

| arm | mode | control PASS | cure PASS | non-green only on the cure / only on the control | identical stdout | identical collections |
|---|---|---|---|---|---|---|
| nogc | m3 / m4 | 826 / 826 | 826 / 826 | 0/0 · 0/0 | 826/826 · 826/826 | 826/826 · 826/826 |
| s0 | m3 / m4 | 825 / 825 | 825 / 825 | 0/0 · 0/0 | 826/826 · 826/826 | 826/826 · 826/826 |
| s1 | m3 / m4 | 824 / 824 | 824 / 824 | 0/0 · 0/0 | 826/826 · 826/826 | 820/826 · 820/826 |
| f1 | m3 / m4 | 823 / 822 | 823 / 822 | 0/0 · 0/0 | 826/826 · 826/826 | 820/826 · 820/826 |

The non-green entries are the same names on both trees and all predate this landing: `procedure_every_alt_replace_4`
(s1/f1 FAIL), `procedure_every_suspend_replace_10` (OOM at 128 KB; its ALL.csv declares 16 MB, which the machine's fixed
window overrides), `procedure_record_every_replace_12` (f1), and `procedure_record_scan_replace_2` (f1, m4). The collector
is attributable on only one side for 0 entries in each direction. The six entries whose collection counts move at s1/f1
are the cure's intended effect: fewer live csets means different collection timing, with identical output.
(An earlier run of the machine was killed at 12:52Z by the cto's name-pattern sweep, and the cto apologised. This table
is from the complete re-run.)

**Icon's other suites on the cure** (dirty tree, so the runners wrote no SCORE row): IPL 194/194, Arizona 88/88 and
IcnBench 26/26, all in both modes; Jcon 81/82, whose one red is htprep in m3, the cto's stale-subject defect and the
same as the published row. Jcon's first run REFUSED rc=2 because the corpus changed under it: the four suites ran
concurrently and one of them wrote a scratch file into the corpus. Run alone, it read as above.

**The gates that read `gc_heap.c` or the registry** (58 found by grep): 45 green on the cure. Eight read red IDENTICALLY
on the control worktree (scripts byte-identical), so they are tolerated and named: `conservative_auditor` (e1: 5
undeclared), `emitted_safe_point_matches_its_contract` (1/7), the `spill_record` gate, `frame_map_anchor`,
`a_safe_point_stores_into_a_mapped_slot` (2/10, reported not blocking), `visited_set_key_spaces` (arm b, the same arm on
both trees), `stack_is_completely_accounted` (1 frame) and `rtcc_block_coverage`. The cto claimed the row curing the GC
gate reds at 13:07Z. `test_gate_gc_the_plant_says_whether_it_applied.sh` read RED on arms 3 and 4 BECAUSE OF THIS PATCH
(a new plant knob, and a new reader of the flip plant, missing from its knob table). It reads PASS 5/5 once both are
declared in the table, as the gate itself directs. The grep also swept up Prolog, Raku and Snocone gates; under
CEO-1232 those are their HQs' to read and form no part of this verdict. `make preflight`: 61 arms, 0 red.

**The patch** is branch `hq_icon/weak-cset-registry` at SCRIP `560c5cd90` (one commit on `300e59ca3`), for the cto's review
before it goes to main.

## 5. WHAT IS LEFT OF deal, AND WHOSE

perf on the cure: the collector is still **45% inclusive** (434 collections at the 128 KB window). **`gc_blk_of` is
13.6% self**: its page-map hit walks forward block by block inside a 512-byte granule, which is long when the granule is
full of small string blocks. That walk is the cto's, named on the ASK and not taken here; so is the window policy
(CEO-1225). The Icon-own and shared residual is by-name builtin dispatch (`try_call_builtin_by_name_bl_s` 4.2% self), the
swap (`rt_swap_var` 1.1%) and `rt_random_var_body` (0.8%).
