# FINDING — slice-captures LANDED: string_pattern m4 +110% and **crosses SPITBOL, 0.52x → 1.09x**. The GC never needed changing — it already marks and relocates interior pointers. The blocker this file was first pushed to report has been FOUND AND CLEARED.

⚠️ **THIS FILE WAS RENAMED, and the rename is the point.** It was first pushed as `…-slice-captures-price-at-1.63x-…-and-are-blocked-by-one-named-defect-the-builtin-arg-path-drops-slen.md`. That claim was true when written and is now **superseded**: the blocker was traced, cured, and the cure landed (SCRIP `89571dd7`) in the same session. The filename is the claim in this corpus, so a filename still saying BLOCKED would have read as open work in `ls`. The original claim is preserved in §5 rather than deleted.

**Seat:** hq_C · **Date:** 2026-08-28 · **Row:** `perf-pattern-defer-capture-layer-cure`, slice **(b)** (DUO split: ceo staged it, Lon declared DUO in-chat to hq_C and hq_P) · **Trees:** measured on SCRIP `34aea2db` pristine `-O0`; correctness landed at `e5edc4a5` (rebased onto hq_P's `9688e110`/`c233a56f`/`53ddfa1d`, gate re-proven after the rebase) · **Instrument:** `bench_snobol4_fixed_iter.sh` (angle 2 — N fixed per kernel from committed `SCALE.tsv`, external `user+sys` via `tools/bench_rusage`, best of REPS=3), `NOHUGE=1 HEAP_MB=4096`, oracle `sbl_clean_bin()` `-bf -s16m`.

⛔ **INSTRUMENT NOTE, so no column is misread:** these are **iterations/second from external CPU time**, NOT the wall-clock best-of that `FINDING-…-ceo-patmatch-gap-answered…` reports. On the same tree the two instruments disagree in level (m4 pattern_bt reads 0.79x here vs 1.23x there). Both are true of their own instrument. **Only the A/B delta below, measured on one instrument, is claimed.**

## 1. THE RESULT (A/B on the landed tree, slice arm off vs on, same binary otherwise)

Instrument: `bench_snobol4_fixed_iter.sh` (angle 2 — N fixed from committed `SCALE.tsv`, external `user+sys` via `tools/bench_rusage`, **best of 5**), `NOHUGE=1 HEAP_MB=4096`, pristine `-O0`, oracle `sbl_clean_bin()` `-bf -s16m`. **The oracle arm held steady across both arms (13.8M/s string_pattern, 3.9–4.0M/s pattern_bt), which is what makes the multiples comparable.**

```diff
  kernel          mode   slices OFF    slices ON     delta     vs clean SPITBOL
+ string_pattern  m4       7.2M/s       15.1M/s      +110%     0.52x -> 1.09x   <- CROSSES 1.0x
+ string_pattern  m3       7.1M/s       14.6M/s      +106%     0.52x -> 1.06x
+ pattern_bt      m4       5.0M/s        5.6M/s       +12%     1.28x -> 1.40x
```

`pattern_bt` moves least **by construction, and that is the confirmation not the disappointment**: it carries one capture per iteration and its remainder is the defer/NV layer — hq_P's slice (a). The two halves of the DUO split were disjoint, exactly as ceo predicted when assigning them.

⭐ **Session arc on string_pattern m4, for scale:** 0.46x at session start (`34aea2db`) → 0.52x after hq_P's slice (a) and the defer-collapse promotion landed → **1.09x** with slice (b). The row's stated goal was "string_pattern's lever to cross 1.0x". It crossed.

⛔ **INSTRUMENT NOTE, so no column is misread:** these are **iterations/second from external CPU time**, NOT the wall-clock best-of that `FINDING-…-ceo-patmatch-gap-answered…` reports. The two instruments disagree in level on the same tree. Only the A/B delta, measured on one instrument with a stable oracle arm, is claimed here.

⚠️ An earlier ceiling probe on `34aea2db` priced this at +63%; the landed figure is +110% because the baseline moved underneath (slice (a) removed the defer cost that was masking the capture cost). **The +63% number is retired — do not quote it.**

## 2. THE GC WAS NEVER THE OBSTACLE — MEASURED, NOT ASSUMED

The row was framed as "capture slices must survive subject mutation." Reading the collector says the hard half is already built:

* `rt_gc_visit_descr` (`gc_heap.c:438-444`) maps an interior `DT_S` pointer to its block through `gc_blk_of`, marks the **whole parent** (so slicing a subject keeps the subject alive), counts `g_gc_interior++`, and registers the slot.
* The compactor's fixup preserves interior offsets exactly: `*loc = (new payload base) + (*loc - old payload base)` (`gc_heap.c:~672`). Every live block relocates since Lon's s262 pin removal, and interior pointers already relocate correctly with it.

**So lifetime and relocation are solved for slice-backed captures today.** The obstacle is entirely in the string-consumer contract.

⛔ Two real hazards found by reading, both cheap and both cured in the design:
1. **`.slen == 0` can never be a slice.** `descr_slen` reads slen 0 as "ask strlen", so a zero-length slice would report the whole rest of the subject. Slices are minted only for `len > 0`.
2. **`str_concat`'s sxt arm.** `rt_sxt_match` keys on exact base-pointer equality, so a delta-0 slice whose base is the extend-owner inherits the **owner's** length (`alc = g_sxt_len`), and `rt_sxt_extend` then appends at the wrong offset — a wrong answer, not a crash. Cure is one call: break the sxt owner when minting a slice.

## 3. THE CONSUMER CLASS, NAMED BY AN INSTRUMENT RATHER THAN A GREP

`SCRIP_CAP_POISON=1` (landed, default off) writes a non-NUL byte where a capture's terminator goes, so any consumer reading past `.slen` yields a wrong answer instead of a silently-correct one. **"Is `DT_S` length-authoritative" is a question about every consumer a value can reach; no grep of `.s` uses can answer it — the 890-program board answers it in one run.**

```diff
  poison board   FAILs      what it named
- first cut         16      10 were the INSTRUMENT'S OWN ARTIFACT (see §4a)
- bounded len>0      6      the numeric validators: is_numeric_like, to_int_slow, to_real, coerce_numeric
- after cure 1       1      the survivor: the coercion family reached from EMITTED code (§5)
+ after cure 2       0      GREEN 891/891 both modes -- and still green with slices ON
```

**Cure (landed `e5edc4a5`):** `rt_cstr_d()` in `core/core.h` — the C-string boundary. The test is structural and needs no flag bit and no spare `DESCR_t` field (there is none; 16 bytes is a SysV register-pair by `static_assert`): `.s[.slen]` is **always** in bounds, being either the value's own terminator or a byte of the parent it slices. An already-terminated value costs one load and one branch and is returned unchanged, so the ordinary path pays nothing.

## 4. ⭐ TWO LESSONS THAT COST REAL VERDICTS, BOTH THE SAME SHAPE

**(a) The instrument answered a narrower question than I asked.** Poisoning byte 0 of a zero-length capture turned `""` into `"Z"` and manufactured **10 of the original 16 failures** — failures of the instrument, not of the tree. A board that is wrong is indistinguishable from a board that is right until you ask what it actually measured. Bounding poison to `len > 0` is load-bearing, not tidying.

**(b) ⛔ THE SHARED-NODE CONTROL ARM CAUGHT A REGRESSION IN MY OWN CURE.** `core.c`/`core.h`/`arithmetic.c` are nodes every frontend lowers to, so every frontend was graded **with a control arm re-run at HEAD**. First cut: **Icon 251 → 250, `rung36_jcon_coerce` SIGSEGV.** Cause: `descr_slen` treats `0xFFFFFFFF` as a **third** spelling of "ask strlen" and `rt_cstr_d` did not, so it indexed `d.s[0xFFFFFFFF]`. **A change whose every witness was SNOBOL4, breaking an Icon program — and the SNOBOL4 board stayed 891/891 green through it.** The general form: *any predicate over `.slen` must answer for all three spellings (0, 0xFFFFFFFF, a real count) or it is not a predicate over `.slen` at all.* Fixed; watermark restored to 251 = control.

## 5. ✅ THE BLOCKER, FOUND AND CLEARED (this section is what the rename is about)

The last poison survivor was `XDump_driver`, via `XDump.sno:29` `LT(i, iMax)` where `iMax` is a `SPAN(digits) . iMax` capture. Five-line witness:

```
        digits = '0123456789'
        P = '1:10'
        P POS(0) SPAN(digits) . a ':' SPAN(digits) . b RPOS(0)
        OUTPUT = 'direct  : ' LT(1, b) 'yes'
END
```
`OUTPUT` printed `b` correctly while `LT(1, b)` raised **Error 148, "lt second argument is not numeric"**.

⭐ **My first hypothesis was wrong and ASM-DIFF-FIRST is what corrected it.** I assumed `STRVAL` minting `.slen = 0` had discarded the length somewhere in the builtin-argument path — plausible, and it would have sent me auditing `STRVAL` call sites. Reading the emitted `.s` instead showed the call is not to the guard I had already fixed: it is `call rt_coerce_num2_d@PLT`. **The value never lost its length; a different consumer family was reading it.** That family is `rt_parse_num_d`, `rt_coerce_int_d` and `rt_pat_prim_int` in `runtime/rt/rt.c` — all reading `.s` as a C string, none consulting `.slen`. Routed through `rt_cstr_d`; poison board went to **0**.

⛔ **Worth keeping for the RTX lane:** `rt_coerce_num2_d` is hand-written ASM (`rtx_icnnum.S`) whose whole design is *decide the easy case or bail to C*, and "trailing junk after the digits → bail" meant the ASM was already handing the slice case to C correctly. **No ASM change was needed** — and this is a concrete example of a `c_*` body that is NOT duplicate documentation but the hard-case handler the ASM depends on, which is the ordering constraint on Lon's delete-the-C-twins ruling.

## 5b. ⛔ THE LIFETIME AXIS WAS TESTED, AND MY FIRST READING OF THE TEST WAS WRONG

`SCRIP_GC_STRESS=64` forces a collection every 64 allocations — the instrument that would expose a dangling slice. First comparison read as *slices add a `demo_calculator_2` m4 failure*. **It did not.** The stress arm is **nondeterministic**, oscillating 2↔3 FAILs on an unchanged binary. Across 4 slice runs and 4 control runs the failure set is **identical** — `{demo_porter, demo_calculator_1, demo_calculator_2}` — and the control fails `calculator_2` m4 in **3 of 3** later runs. **The run that suggested a regression was the CONTROL being flaky, not the slice arm.**

Two things fall out, both worth rows that are not mine:
* **Three pre-existing GC-stress failures** (`demo_porter`, `demo_calculator_1`, `demo_calculator_2`) — real collector fragility, present with slices off.
* **The stress arm's own nondeterminism.** An arm that returns different failure sets for identical inputs cannot discriminate, and if it had been run once and trusted it would have blocked a correct change (or passed a broken one). ⭐ *Same family as §4a: an instrument that answers a different question than you asked never says so.*

## 6. COMPLETENESS (Lon, in-chat 2026-08-28: make COMPLETE the programs CEO and HQ-PERFORM are tuning)

Census of `corpus/demo/snobol4`: **27 demo programs on disk, 22 graded** by `test_corpus_snobol4.sh`. The five ungraded:

| program | state |
|---|---|
| `calculator-2.sno` | ✅ **now graded** — passed both modes unmodified; board 890 → **891** |
| `claws5.sc` | ⛔ runs rc=0 but prints only `Pattern match failed` — Snocone defect on a tier-3 target |
| `porter.sc` | ⛔ **parse error** `porter.sc:15` — Snocone grammar has no locals-list production (`func_head`, `snocone_parse.y:297`) cannot parse `function cons(i) (c) {` |
| `beauty.sc`, `beauty.sno` | ungraded, no `.ref` on disk |

⭐ `calculator-2` is the sharpest of these: a **tier-3 campaign target** whose `-match` and `-match-fence` twins were both graded while the program itself never was — and `calculator-2.ref` (5,878 bytes) had been sitting on disk the whole time. Not a hard problem, a **missing row**: the denominator was quietly one smaller than it looked on a program the campaign is actively tuning.

## 7. VERDICT SET (pristine `-O0`, HQ-27; re-proven after EACH rebase onto hq_P's landings; control arm at HEAD for every non-zero rc)

```
SNOBOL4 board          m3 PASS=891 FAIL=0 · m4 PASS=891 FAIL=0 SKIP=0 MISSING=0
poison board           m3 PASS=891 FAIL=0 · m4 PASS=891 FAIL=0      <- with slices ON
test_gate_emit_no_lang                 rc=0
test_gate_template_medium_invisible    rc=0
Icon rungs             PASS=251 FAIL=15 BADEXIT=1 XFAIL=30 / 297   == control, watermark held
smoke icon/snocone/rebus/raku          rc=0
smoke prolog                           rc=1 (`clause`) -- IDENTICAL to control, pre-existing
```

⛔ **`.s` artifacts are stale in the tree and it is NOT from this row.** The benchmark `.s` now differs from committed output, and the diff is exactly hq_P's resolved-fn inline cache (`g_sno_defer_cells`, emitted from `bb_match_defer.cpp`, slice (a) `9688e110`). This row's changes are runtime-only and emit nothing; flagged here so the next regen is attributed correctly rather than read as drift from slice (b).

**Landed:** SCRIP `e5edc4a5` (length authority + calculator-2 board row) and `89571dd7` (slice-captures).
