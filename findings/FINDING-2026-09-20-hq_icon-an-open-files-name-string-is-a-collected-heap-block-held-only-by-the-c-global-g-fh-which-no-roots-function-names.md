# FINDING 2026-09-20 hq_icon — an open file's NAME is a collected-heap block held only by `g_fh[]`, and no `*_gc_roots` function names `g_fh`

**Seat** hq_icon · **Mode** TENET · **Row** `icon-gc-the-icon-share-of-the-unmapped-slot-population-censused-by-name-and-the-master-clean-at-one-megabyte`
**Tree** SCRIP `5418432bb` (the two new witness files are the only additions), corpus `8486bb1e2`, RT_OPT `-O0`, load ~2 · **Oracle** `/home/resources/icon-master/bin/icont` + `iconx` 9.5.25a

## THE MEASUREMENT FIRST

`src/runtime/by_name_dispatch.c:7798` — `if (idx >= 0 && idx < FH_MAX) g_fh[idx].name = rt_heap_strdup_c(path);`

`rt_heap_strdup_c` (`src/runtime/rt/gc_heap.c:353`) allocates in the **collected heap**. `g_fh` is a plain C global
(`src/driver/driver_private.h:42`, `fh_slot_t g_fh[FH_MAX]`). **`g_fh` is named in ZERO GC visit or root calls** —
measured, not asserted:

```
grep -rn '<sym>' src/ --include=*.c --include=*.cpp | grep -cE 'rt_gc_visit|rt_gc_root_range_add'
  g_fh          0        _io_chan      0        g_sno_errtext 0        gram_reg 0        g_lbl_tab 2
```

`g_lbl_tab` reading **2** is what makes the zeroes a measurement rather than a broken grep: the same instrument
finds the one global of this shape that IS rooted.

So the name string is unreachable from every root the collector walks. One collection reclaims it, the arena
re-issues its bytes to the next allocation, and `image(f)` prints whatever landed there.

## THE WITNESS, LANDED AND ORACLE-CUT

`SCRIP/scripts/gc_witnesses/hb_file_name_unrooted.icn` + `.ref` (ref cut from `icont`/`iconx` 9.5.25a, per Lon's REF order).

```icon
procedure main()
   local f, s, i;
   f := open("tmp3", "wt") | stop("cannot open");
   write("A ", image(f));
   every i := 1 to 8 do s := repl("a", 65536);
   write("B ", image(f));
   close(f)
end
```

Oracle: `A file(tmp3)` / `B file(tmp3)`. SCRIP prints `B file(aaaaaa…)` — the `repl("a",65536)` block re-issued
in place. **Graded by oracle diff, never by rc: rc stays 0 on every wrong run.**

| arm | stress 0 1 2 3 4 5 8 |
|---|---|
| m3, `SCRIP_HEAP_MB=1` | `X X X X X X X` |
| m3, shipped arena (control) | `. X X X X X X` |
| m4, `SCRIP_HEAP_MB=1` | `X` (same corruption) |

Deterministic — 5 of 5 runs identical. It is not a rate.

## A / B / A, AND THE CURE IS ONE LOOP

**B arm** — added to `bnd_gc_roots()` (`src/runtime/by_name_dispatch.c:833`, already called from `gc_heap.c:1085`):

```c
{ extern void rt_gc_visit_raw(const char **);
  for (int fi = 0; fi < FH_MAX; fi++) {
      if (g_fh[fi].name)  rt_gc_visit_raw((const char **)&g_fh[fi].name);
      if (g_fh[fi].alias) rt_gc_visit_raw((const char **)&g_fh[fi].alias);
      if (g_fh[fi].enc)   rt_gc_visit_raw((const char **)&g_fh[fi].enc); } }
```

| arm | tree | witness band at `SCRIP_HEAP_MB=1` |
|---|---|---|
| A | origin, clean | `NOMATCH × 7` |
| B | + the loop above | **`MATCH × 7`** |
| A' | reverted, rebuilt | `NOMATCH × 7` |

⛔ **THE LOOP WAS REVERTED AND IS NOT LANDED.** `g_fh` is a node SNOBOL4, Icon, Prolog and Pascal all reach, so
this is an ASK to an officer and never an HQ's landing (ASK PATH; ceo CEO-1016: *"YOUR JOB ON THIS ROW IS TO NAME
THEM AND HAND THEM OVER"*). Whoever lands it grades every frontend, not just Icon.

## THE CLASS, NAMED AND NEVER COUNTED

A collected-heap pointer parked in a **C global** that no root call names. Every member found, with its line:

| target | site | rooted? |
|---|---|---|
| `g_fh[idx].name` | `src/runtime/by_name_dispatch.c:7798` (Icon/SNOBOL4 `open`) | **no** — the proven witness |
| `g_fh[idx].name` | `src/runtime/by_name_dispatch.c:2346` (Prolog `open`) | **no** |
| `g_fh[idx].alias` | `src/driver/driver_globals.c:22` | **no** |
| `g_fh[idx].enc` | `src/driver/driver_globals.c:23` | **no** |
| `_io_chan[c].varname` | `src/runtime/core/core.c:4171` | **no** |
| `_io_chan[ch].varname` | `src/runtime/core/core.c:4187` | **no** |
| `_io_chan[c].varname` | `src/runtime/core/core.c:4213` | **no** |
| `g_sno_errtext` | `src/runtime/keywords.c:311` | **no** |
| `g_sno_errtext` | `src/runtime/keywords.c:341` | **no** |
| `g_sno_errtext` | `src/runtime/runtime_eval.c:255` | **no** |
| `g_sno_errtext` | `src/runtime/runtime_eval.c:489` | **no** |
| `gram_reg[i].body` | `src/runtime/by_name_dispatch.c:454` | **no** |
| `gram_reg[gram_n].qname` | `src/runtime/by_name_dispatch.c:455` | **no** |
| `gram_reg[gram_n].body` | `src/runtime/by_name_dispatch.c:455` | **no** |
| `g_lbl_tab[g_lbl_n].key` | `src/runtime/runtime_eval.c:380` | yes — the control |

⛔ **WHAT THIS LIST CANNOT SEE, SO NOBODY READS IT AS COVERAGE.** It was produced by a scratch reader over the
allocator call sites (`rt_heap_strdup_c`, `rt_gcheap_alloc`, `rt_pvec_alloc`, `rt_ws_alloc_descr`) whose
assignment target resolves to a file-scope object. It **under-reports by construction** in three known ways, each
found by hand after the reader had already printed its answer: a ternary RHS (`x = c ? alloc() : 0`) is missed —
that is how `driver_globals.c:22/23`, `keywords.c:311` and `core.c:4187` were found; a function-level `static`
aggregate is missed — that is `gram_reg`; and a pointer stored through a helper rather than assigned in place is
invisible to it entirely. **This is a floor, not a population.** Making it a real instrument is the coo's lane and
is recommended, not done here.

⭐ **This is NOT class 2 of ARCH-GC section 3c.** Icon's class 2 is measured EMPTY:
`util_zls_frame_map_census.py --lang icon` reads `graphs=1261 words=164358 unkinded=0 holes=0 graded=826
no_layout=0`, and the unmapped-store census over the 17 Icon GC witnesses reads `shielded_stores=392 members=0
undecidable=10`. It is not classes 1/3/4 either: no frame slot is involved. **It is a root-set gap on the C side**
— a fifth storage class the four in section 3c do not cover, and one the frame-map work cannot reach.

## THE TEN UNDECIDABLE ICON SITES, NAMED (the census's own honest hole)

`util_gc_unmapped_store_census.py scripts/gc_witnesses/*.icn` → `witnesses=17 graphs=27 shielded_stores=392
members=0 undecidable=10`, every one `NO-ANCHOR-REACHES-SITE`, and **all ten are co-expression witnesses**:

- `hb_coexpr_genp_scan.icn` `.Lcall_value_β_23_8` line 250 — `[rbp+216]`, `[rbp+208]`
- `hb_coexpr_parked.icn` `.Llit_integer_α_53_0` line 342 — `[rbp-616]`, `[rbp-624]`; line 370 — `[rbp-600]`, `[rbp-608]`
- `hb_coexpr_refresh.icn` `.Llit_integer_α_164_0` line 1030 — `[rbp+1048]`, `[rbp+1040]`; line 1058 — `[rbp+1064]`, `[rbp+1056]`

Icon reads `members=0` **with 10 sites unmeasured**, which the census itself refuses to call clean. Icon's share of
the undecidable population is exactly the co-expression family, which is where Icon's own regime enters a box
through an indirect jump.

## THE ICON MASTER AT THE TINY ARENA

`SCRIP_HEAP_MB=1`, harness, both modes, my own run on a clean tree:

```
SUITE_BOARD family=ALL total=826 m3_n=826 m3_pass=824 m3_fail=2 m3_crash=0 m3_hang=0
                        m4_n=826 m4_pass=825 m4_fail=1  all_pass=824 all_n=826 arena_mb=1
```

826/826 at the shipped arena. Confirms CEO-935's reading independently.

## TWO FURTHER DEFECTS, UNDERNEATH THE FIRST — NAMED, NOT MINIMIZED

With the B-arm root in place both named entries still fail, so the file-name gap is **not** the whole of either:

- **`procedure_coexpr_suspend_replace_3`** — the `tmp3`/`textgen` arm goes green; the `tmp4`/`bingen` arm then
  reports `mismatch on item 1` (binary I/O, `reads`/`writes`, `repl("\^@",1037)`). Deterministic, 5/5.
- **`procedure_every_scan_replace_16`** — `wordcount` loses exactly two table increments: `letters` reads 3 where
  the oracle says 4, and `many 1` is absent entirely. No garbage key is printed. Deterministic, 5/5.

⛔ **NEITHER MINIMIZES BY SOURCE ABLATION** and I am saying so rather than leaving a gap. For entry 16 I cut a
standalone `wordcount` (MATCH), one with `static letters` plus 60 × `repl("q",16384)` of pressure (MATCH), and
four variants keeping exactly one predecessor of `main` — `spellw(1 to 25)`, `sieve()`, `spellw(10000000 to
10000500 by 7)`, `spellw(945123342)` — **all four MATCH**. The defect needs the full heap history of all five
predecessors; it is heap-state dependent, not construct dependent, so the ablation ladder this tree normally
climbs does not reach it. Cost: ~25 minutes of ablation for a negative result, reported as a negative result.

## ROUTING

The cure for the named class is a root-set registration — the cfo's file and lane. The two residual defects are
emitter/planner-shaped and go to the cto. Both sent this sitting under Lon's escalation order.
