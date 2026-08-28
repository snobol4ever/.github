# FINDING — slice-captures are PRICED (m4 string_pattern 1.63x, 0.46x→0.75x vs clean SPITBOL) and BLOCKED BY ONE NAMED DEFECT: the builtin-argument path drops `.slen`. The GC was never the obstacle — it already fixes interior pointers.

**Seat:** hq_C · **Date:** 2026-08-28 · **Row:** `perf-pattern-defer-capture-layer-cure`, slice **(b)** (DUO split: ceo staged it, Lon declared DUO in-chat to hq_C and hq_P) · **Trees:** measured on SCRIP `34aea2db` pristine `-O0`; correctness landed at `e5edc4a5` (rebased onto hq_P's `9688e110`/`c233a56f`/`53ddfa1d`, gate re-proven after the rebase) · **Instrument:** `bench_snobol4_fixed_iter.sh` (angle 2 — N fixed per kernel from committed `SCALE.tsv`, external `user+sys` via `tools/bench_rusage`, best of REPS=3), `NOHUGE=1 HEAP_MB=4096`, oracle `sbl_clean_bin()` `-bf -s16m`.

⛔ **INSTRUMENT NOTE, so no column is misread:** these are **iterations/second from external CPU time**, NOT the wall-clock best-of that `FINDING-…-ceo-patmatch-gap-answered…` reports. On the same tree the two instruments disagree in level (m4 pattern_bt reads 0.79x here vs 1.23x there). Both are true of their own instrument. **Only the A/B delta below, measured on one instrument, is claimed.**

## 1. THE PRICE (why this cure is worth its correctness surface)

Ceiling probe: `rt_dcap_pump` hands out a descriptor pointing INTO the subject (`.s = subj + delta`, `.slen = len`) instead of `rt_str_alloc` + `memcpy`. Deliberately unsound — its only job is to price the cure before the consumer surface is paid for.

```diff
  kernel          engine   baseline      slice-probe    delta      vs clean SPITBOL
+ string_pattern  m4        6.2M/s        10.1M/s       +63%       0.46x -> 0.75x
+ string_pattern  m3        6.7M/s        11.7M/s       +75%       0.49x -> 0.87x
  pattern_bt      m4        3.1M/s         3.1M/s        flat      unchanged
```

`pattern_bt` is flat **and that is the expected result, not a null**: it carries one capture, and its remainder is the defer/NV layer — hq_P's slice (a), which landed at `9688e110` for −40.6% instructions. The two slices are disjoint by construction, which is why the split was correct.

⚠️ **Oracle variance caveat, stated because it bounds the claim:** `sbl` re-measured 3.9M/s then 3.4M/s on pattern_bt across the two runs (13%), while string_pattern's oracle held (13.6M → 13.5M). The string_pattern multiples above rest on a stable oracle arm; a pattern_bt multiple from this pair would not.
⚠️ **The baseline has since moved.** The price was taken on `34aea2db`. Slice (a), the per-pump monitor read, and the PT-3 defer-collapse promotion all landed underneath afterwards. **Re-price on the current base before quoting 1.63x as current state.**

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
- first cut         16      10 were the INSTRUMENT'S OWN ARTIFACT (see below)
- bounded len>0      6      the numeric validators: is_numeric_like, to_int_slow, to_real, coerce_numeric
+ after cure         1      the one real survivor, named in §5
```

**Cure (landed `e5edc4a5`):** `rt_cstr_d()` in `core/core.h` — the C-string boundary. The test is structural and needs no flag bit and no spare `DESCR_t` field (there is none; 16 bytes is a SysV register-pair by `static_assert`): `.s[.slen]` is **always** in bounds, being either the value's own terminator or a byte of the parent it slices. An already-terminated value costs one load and one branch and is returned unchanged, so the ordinary path pays nothing.

## 4. ⭐ TWO LESSONS THAT COST REAL VERDICTS, BOTH THE SAME SHAPE

**(a) The instrument answered a narrower question than I asked.** Poisoning byte 0 of a zero-length capture turned `""` into `"Z"` and manufactured **10 of the original 16 failures** — failures of the instrument, not of the tree. A board that is wrong is indistinguishable from a board that is right until you ask what it actually measured. Bounding poison to `len > 0` is load-bearing, not tidying.

**(b) ⛔ THE SHARED-NODE CONTROL ARM CAUGHT A REGRESSION IN MY OWN CURE.** `core.c`/`core.h`/`arithmetic.c` are nodes every frontend lowers to, so every frontend was graded **with a control arm re-run at HEAD**. First cut: **Icon 251 → 250, `rung36_jcon_coerce` SIGSEGV.** Cause: `descr_slen` treats `0xFFFFFFFF` as a **third** spelling of "ask strlen" and `rt_cstr_d` did not, so it indexed `d.s[0xFFFFFFFF]`. **A change whose every witness was SNOBOL4, breaking an Icon program — and the SNOBOL4 board stayed 891/891 green through it.** The general form: *any predicate over `.slen` must answer for all three spellings (0, 0xFFFFFFFF, a real count) or it is not a predicate over `.slen` at all.* Fixed; watermark restored to 251 = control.

## 5. ⛔ THE ONE REMAINING BLOCKER — SLICES CANNOT SHIP UNTIL THIS IS CURED

**The builtin-argument path does not preserve `.slen`.** Witness, 5 lines, reproduces under `SCRIP_CAP_POISON=1` on the current tree:

```
        digits = '0123456789'
        P = '1:10'
        P POS(0) SPAN(digits) . a ':' SPAN(digits) . b RPOS(0)
        OUTPUT = 'direct  : ' LT(1, b) 'yes'
END
```
`OUTPUT` prints `b` correctly (the output path IS length-aware), but `LT(1, b)` raises **Error 148, "lt second argument is not numeric"** — the value reaches `is_numeric_like` having lost its length, so the boundary in §3 cannot see that it is slice-backed. Board witness: `XDump_driver` (`corpus/tests/snobol4/beauty_suite`), via `XDump.sno:29` `LT(i, iMax)` where `iMax` is a `SPAN(digits) . iMax` capture. **Suspected mechanism, NOT yet proven:** `STRVAL(s_)` mints `.slen = 0`, so any rebuild of a descriptor through it discards length authority. **Next step is to prove the exact site, not to assume this one.**

⛔ **Do not enable slice-captures before this is closed.** With `.slen` lost, a slice degrades to a read past the value — a wrong answer, silently.

## 6. COMPLETENESS (Lon, in-chat 2026-08-28: make COMPLETE the programs CEO and HQ-PERFORM are tuning)

Census of `corpus/demo/snobol4`: **27 demo programs on disk, 22 graded** by `test_corpus_snobol4.sh`. The five ungraded:

| program | state |
|---|---|
| `calculator-2.sno` | ✅ **now graded** — passed both modes unmodified; board 890 → **891** |
| `claws5.sc` | ⛔ runs rc=0 but prints only `Pattern match failed` — Snocone defect on a tier-3 target |
| `porter.sc` | ⛔ **parse error** `porter.sc:15` — Snocone grammar has no locals-list production (`func_head`, `snocone_parse.y:297`) cannot parse `function cons(i) (c) {` |
| `beauty.sc`, `beauty.sno` | ungraded, no `.ref` on disk |

⭐ `calculator-2` is the sharpest of these: a **tier-3 campaign target** whose `-match` and `-match-fence` twins were both graded while the program itself never was — and `calculator-2.ref` (5,878 bytes) had been sitting on disk the whole time. Not a hard problem, a **missing row**: the denominator was quietly one smaller than it looked on a program the campaign is actively tuning.

## 7. VERDICT SET (pristine `-O0`, HQ-27; re-proven AFTER the rebase onto hq_P's landings)

```
SNOBOL4 board          m3 PASS=891 FAIL=0 · m4 PASS=891 FAIL=0 SKIP=0 MISSING=0
test_gate_emit_no_lang                 rc=0
test_gate_template_medium_invisible    rc=0
Icon rungs             PASS=251 FAIL=15 BADEXIT=1 XFAIL=30 / 297   == control, watermark held
smoke icon/snocone/rebus/raku          rc=0
smoke prolog                           rc=1 (`clause`) -- IDENTICAL to control at HEAD, pre-existing
emitted .s, both pattern kernels       byte-identical -> runtime-only, no artifact regen
```
Every non-zero rc above was re-run as a control arm at HEAD before being called pre-existing.
