# FINDING 2026-07-25 — PL RUNTIME RESIDENCY IS **NINE** FUNCTIONS, NOT 132

**Session:** s149 (orientation + measurement). **Goal:** GOAL-PROLOG-BB — "rewrite Prolog to Byrd Boxes,
move 99% out of the runtime" (Lon directive).

## THE HEADLINE

**"99% out of the runtime" is a NINE-FUNCTION job, not a 132-function job.** Measured, exact, not estimated.

| rank | function | dynamic calls | cum % |
|------|----------|--------------:|------:|
| 1 | `rt_pl_dop_unify`          | 80,993 | 37.38 |
| 2 | `rt_pl_dop_ax_sub`         | 48,595 | 59.80 |
| 3 | `rt_pl_dop_is_v`           | 48,518 | 82.19 |
| 4 | `rt_pl_dop_unwind_nothrow` | 16,490 | 89.80 |
| 5 | `rt_pl_dop_cmp_gt`         | 15,932 | **97.15** |
| 6 | `rt_proc_call_open_det`    |  1,460 | 97.82 |
| 7 | `rt_jmp_frame_lexprep2`    |  1,460 | **98.50** |
| 8 | `rt_pl_dop_trail_unwind`   |  1,301 | 99.10 |
| 9 | `rt_gen_spine_resume_enter`|    732 | **99.44** |
| — | remaining 12 reached syms |  1,219 | 100.00 |

TOTAL = 216,700 runtime entries over 5 benchmarks (nrev, qsort, queens_8, tak, deriv), mode-4, RT `-O0`.

**The 132 `rt_pl_*` definitions and the 257 predicate arms in `by_name_dispatch.c` (6,967 lines) are almost
entirely COLD on this corpus — only 23 rt_ symbols are reached via PLT at all, and 9 carry 99.44%.**

## METHOD (reproducible, no perf/gdb needed)

Container has **NO `perf`, NO `gdb`, NO `valgrind`, NO `ltrace`** (re-confirmed s149; consistent with s148).
Instrument = **LD_PRELOAD PLT interposition**, auto-generated from the binary's own PLT:

```
objdump -d prog_bin | grep -oE '<[a-z_][a-z0-9_]*@plt>' | ... > syms_rt.txt   # 23 syms
python3 gen -> plcount.c  (one counting trampoline per sym) -> plcount.so
PLCOUNT_OUT=... LD_PRELOAD=./plcount.so ./prog_bin
```
Exact (not sampled), no rebuild of SCRIP, outputs verified unchanged under interposition.
Artifacts: `/home/claude/meas/{plcount.c,plcount.so,syms_rt.txt}`.

## ⚠ LIMITATION — THIS IS A **FREQUENCY** RANKING, NOT A **COST** RANKING. DO NOT SUM IT WITH s141/s148 TIME NUMBERS.

Call count != cycles. A `rt_proc_call_open_det` entry may cost far more than an `ax_sub` entry, so the
frequency table above **does not by itself demote the REGAIN-1 spine rung** (cursor: ~36%) or the lexprep2
sink (~20%) — those are TIME claims and this is a COUNT claim. They measure different things.

**A cost-weighted version was ATTEMPTED AND FAILED.** An `__rdtsc` inclusive/exclusive-cycle interposer
(`/home/claude/meas/pltime.c`) **segfaults on this engine**: Prolog backtracking is longjmp-based, so when
`unwind_nothrow`/trail unwind fires, the trampoline's post-call epilogue never executes — depth bookkeeping
corrupts and the stack is unwound past the interposer frames. **Any future timing interposer here must be
longjmp-aware (sigsetjmp checkpoint or depth resync on unwind), or it will crash the same way.** Recording
this so the next session does not re-derive it.

## WHAT IT MEANS FOR THE REWRITE

1. **The target set is small and nameable.** Nine boxes gets 99.44% by frequency. This makes
   "rewrite Prolog to Byrd Boxes" tractable as a bounded ladder rather than an open-ended port.
2. **Ranks 6 and 7 are on the BLOCKED path.** `rt_proc_call_open_det` + `rt_jmp_frame_lexprep2` are the
   proc-call/frame spine emitted by `xa_flat.cpp` — **independently re-confirmed s149 as the SOLE remaining
   `test_gate_template_medium_invisible.sh --strict` violator, 128 raw-byte sites, dual BINARY(:169)/TEXT(:289)
   arms.** So **XA-FLAT-CONVERT is genuinely on the critical path for 2 of the 9**, exactly as the s148 cursor said.
3. **Ranks 1–5 are NOT blocked by xa_flat.** `unify`/`ax_sub`/`is_v`/`unwind_nothrow`/`cmp_gt` are reached from
   `bb_call_fn.cpp` / `bb_call.cpp`, already-converted template files. **97.15% is reachable without touching
   the forbidden-shape file at all.** This is the cheap half of the ladder and it is unblocked TODAY.
4. **Per-program variance is extreme — do not tune on one benchmark.** `tak` = 206,735 entries with **ZERO**
   spine calls (pure unify/is_v/ax_sub). `nrev` = 1,401 entries, **75.4% spine**. `deriv` = 131 entries total.
   A rung validated only on nrev optimizes a workload shape that tak does not have, and vice versa.
   **Every rung in this ladder must report the full 5-program table, not a single number.**

## PROPOSED LADDER (supersedes nothing until Lon rules)

- **PLBB-1** `unify` family inline as an emitted box (37.4% of entries, unblocked) — biggest single win.
- **PLBB-2** `is_v` + `ax_sub` + `cmp_gt` (arith/compare device-ops, 52.4% combined, unblocked).
- **PLBB-3** `unwind_nothrow` + `trail_unwind` (backtracking edge — the longjmp spine; design care).
- **XA-FLAT-CONVERT** (rules-mandated prerequisite) then **PLBB-4** spine: `call_open_det` + `lexprep2`.

## GATES RUN THIS SESSION

- `make scrip` rc=0; `make libscrip_rt` rc=0; mode-3 `--run nrev.pl` correct; mode-4 via
  `run_prolog_via_x86_backend.sh` correct.
- `test_gate_template_medium_invisible.sh --strict` → `REMAINING: xa_flat.cpp(128)`, GATE FAIL — **verified
  pre-existing on the clean tree, not introduced here.**
- No source file modified this session. Measurement only.

---

# ⭐ SUPERSEDING SECTION (same session, later) — **THE SINK ALREADY WORKS; THE RESIDUAL IS ONE NAMED ARM: VVB**

## CORRECTION TO THE HEADLINE ABOVE — READ THIS FIRST

The table at the top counts **runtime ENTRIES**, which is **NOT** total device-op work, because PL-SINK-1
already absorbs a large share of `$unify` inline and never enters the runtime at all. **The top table's
denominator is wrong for answering "what fraction is out of the runtime."** Corrected by A/B:

```
tak, $unify attempts:   SCRIP_NO_SINK=1 -> 365,751 runtime entries
                        sink enabled    ->  79,512 runtime entries
  => inline absorbs 286,239 = 78.3% of unify traffic ALREADY OUT of the runtime.
```
**So Prolog `$unify` is already ~78% out of the runtime, not ~0%. The job is the last ~22%, not the whole thing.**

## THE RESIDUAL IS ONE SHAPE

Pre-deref arg tags at the slow path: **100% `DT_N`/`DT_N` (80,980/80,980)** — uninformative, that is just the
call ABI. **Post-deref cell tags are the real discriminator:**

| post-deref pair | count | share of residual |
|---|---:|---:|
| `DT_SNUL` × `DT_SNUL` (**both unbound = VVB**) | 61,438 | **75.9%** |
| `DT_T`(5) × `DT_SNUL` | 19,509 | 24.1% |
| `DT_I` × `DT_SNUL` | 2 | ~0% |

⚠ **Trust the first row, treat the second with suspicion.** The `DT_T`(table) reading is almost certainly an
artifact of my interposer **re-implementing** the deref chase (`/home/claude/meas/deref_hist.c`) instead of
calling the engine's own `plw_cell_deref`; a table tag is not a plausible `tak` value. **Next session: redo
this histogram by dlsym-ing the real deref, do not reuse my replica.** The VVB row is corroborated
independently (below) and is safe.

## INDEPENDENT CORROBORATION — THE TEMPLATE SAYS SO ITSELF

`bb_call_fn.cpp:23` names its own deferrals: *"...(DT_N entry forms, **both-unbound join/VVB**, compound
recursion, floats/NaN, non-identical atoms → rt_descr_equal, trail uninitialized/full → area grow) falls into
the UNTOUCHED C leaf."* The emitted asm agrees: after deref, `cmp r8,r9; je <identity>` then both-unbound
routes to the slow label. **The measurement and the source independently name the same gap. This is the rung.**

## ⭐ PLBB-1 IS THEREFORE PRECISELY DEFINED (was vague when proposed above)

**PLBB-1 = emit the VVB (both-unbound join) arm inline.** Not "inline unify" — that is already done.
Expected effect: removes ~75.9% of the unify residue; `tak` unify entries ~79,512 -> ~18,100 projected,
i.e. unify moves from 78.3% -> ~95% out of the runtime. **PROJECTION, NOT MEASURED — must be verified.**

**Design constraints (do not skip — VVB is the arm with the real correctness traps):**
1. **Bind direction is NOT free.** Binding must respect cell age/order (younger→older, WAM discipline) or
   you create dangling references that survive backtracking. Read `plw_unify_cells`' both-unbound arm in
   `by_name_dispatch.c` and mirror it EXACTLY — SINK-1's contract is "complete a whole plw arm verbatim or
   defer the whole call."
2. **Aliasing already handled** upstream (`cmp r8,r9; je identity`), so the arm sees DISTINCT cells only.
3. **Trail push required** — VVB must trail the bound cell or backtracking leaks the binding. SINK-3's
   `sink_tp_nc` carve (pre-reserved room, one check) is the pattern; trail-full still defers.
4. **Label ids:** 40..58 SINK-1, 60..77 SINK-2, 80..99 SINK-3, 100..101 SINK-8, 110..120 SINK-4.
   **VVB must claim a fresh block (suggest 121..135) or it will collide.**
5. Add its own kill switch (`SCRIP_NO_VVB=1`) — s146/s148 both noted the earlier sinks lack per-rung
   switches, so their numbers cannot be summed. **Do not repeat that mistake.**
6. Verify by **A/B byte-identity m3 vs m4** + the 5-program table, not one benchmark (tak and nrev have
   opposite shapes).

## WHY I STOPPED HERE INSTEAD OF IMPLEMENTING IT

Context budget. VVB is the arm with genuine correctness traps (bind direction + trail + backtracking); a
rushed half-edit to `bb_call_fn.cpp` would leave the tree broken and the 164-test rung red with no budget to
diagnose. **No source file was modified this session.** Tree is clean; `xa_flat.cpp(128)` gate failure is
pre-existing and untouched.

## INSTRUMENTS LEFT BEHIND (`/home/claude/meas/`, regenerate if the sandbox is gone)

| file | what | trust |
|---|---|---|
| `plcount.c/.so` | per-symbol PLT call counter, auto-generated from the binary's PLT | **exact, reliable** |
| `unifyhist.c/.so` | pre-deref arg tag histogram at `rt_pl_dop_unify` | reliable (but uninformative — ABI artifact) |
| `deref_hist.c/.so` | post-deref cell tag histogram | ⚠ **replica deref — VVB row corroborated, `DT_T` row suspect** |
| `pltime.c` | rdtsc cost interposer | ❌ **SEGFAULTS — longjmp unwinds past the trampoline epilogue. Must be longjmp-aware.** |

A/B recipe that produced the 78.3%: `SCRIP_NO_SINK=1 scrip --compile X.pl` vs default, then compare
`rt_pl_dop_unify` counts under `plcount.so`. **This is the cheapest honest way to size any future sink rung —
it measures what the sink ACTUALLY absorbs rather than what its comment claims.**

---

# ⛔⛔ THIRD AND FINAL SECTION — **I WAS WRONG TWICE. THE FULL CORPUS VINDICATES THE s148 SPINE PRIORITY. PLBB-1 (unify) IS *NOT* THE RUNG.**

## THE ERROR, NAMED

Both sections above ranked device-ops using **5 benchmarks** (nrev, qsort, queens_8, tak, deriv = 216,700
entries). That sample was **dominated by `tak`**, which is arithmetic recursion with **ZERO spine calls**.
It made `unify`/`is_v`/`ax_sub` look like the hot set and led me to recommend **PLBB-1 = inline VVB**.

**Re-measured on ALL 22 benchmarks — 13,803,839 runtime entries, 64x the sample — the ranking inverts:**

| share | function | entries |
|------:|----------|--------:|
| 15.32% | `rt_pl_dop_trail_unwind` | 2,114,931 |
| 15.26% | `rt_gen_spine_resume_enter` | 2,106,742 |
| 14.92% | `rt_proc_call_open_det` | 2,060,043 |
| 14.92% | `rt_jmp_frame_lexprep2` | 2,060,043 |
| 8.03% | `rt_pl_dop_unify` | 1,108,786 |
| 7.38% | `rt_pl_dop_mkc` | 1,018,100 |
| 6.32% | `rt_pl_dop_unwind_nothrow` | 873,060 |
| 5.33% | `rt_pl_dop_is_v` | 735,898 |
| 5.30% | `rt_pl_dop_ax_sub` | 731,498 |
| 4.51% | `rt_pl_dop_unify_cs` | 622,812 |
| 2.09% | `rt_pl_dop_ix_g` | 289,004 |

### ⭐ **SPINE (`call_open_det` + `lexprep2` + `gen_spine_resume_enter`) = 45.11%. `unify` = 8.03%.**

**The s148 cursor was RIGHT and I was wrong.** "NEXT = REGAIN-1 slice C (THE SPINE), still the big rung
(~36%)" is corroborated by an independent instrument on the full corpus (45.1% by entry count vs its ~36% by
time — different metrics, same verdict). **Do REGAIN-1 slice C. Do not do PLBB-1 first.** My VVB analysis in
the section above is still CORRECT as far as it goes — VVB really is 75.9% of the *unify residue* — but unify
is only 8% of the problem, so VVB is worth at most ~6% of runtime entries. **It is a later rung, not the next one.**

### SECOND CASUALTY: the s148 "mkc is a POOR next target" call is ALSO sample-dependent.
s148 measured mkc at 100 vs ix_g 649 (qsort) and 30 vs 1022 (nrev) and concluded mkc is cold. **Corpus-wide,
`mkc` is 7.38% and `ix_g` is 2.09% — mkc is 3.5x HOTTER than ix_g, the opposite of the s148 conclusion.**
SINK-4 (s148's landed rung) optimized the 2.09% function. Not wasted, but not the elephant either.

## ⭐⭐ THE RULE THIS EARNS — **SAMPLE SIZE INVERTS THE RANKING, SAME AS STATIC-VS-DYNAMIC DID**

s148 earned *"static site counts invert the true ranking; use dynamic counts."* **That is necessary and NOT
sufficient.** Dynamic counts on a 5-program sample inverted the ranking a SECOND time, in the same direction
(making a locally-hot op look globally hot). The corpus has 22 programs with wildly different shapes — `tak`
is spine-free, `nrev` is 75% spine, `deriv` is 131 entries total. **Any rung ranking measured on fewer than
the full 22 is untrustworthy. Run all 22. It costs one loop and ~40 seconds.**

Recipe (exact, no perf/gdb needed, ~40s for the whole corpus):
```
for f in corpus/benchmarks/prolog/bench/*.pl; do scrip --compile $f; as; gcc -no-pie ... ; done
for b in *_bin; do PLCOUNT_OUT=/tmp/f_$p.txt LD_PRELOAD=plcount.so ./$b; done
cat /tmp/f_*.txt | awk '{a[$2]+=$1} END{...}' | sort -rn
```
22/22 compiled, linked, and ran clean. **This is now the ladder's default hotness instrument.**

## REVISED LADDER (replaces the two proposed above)

1. **REGAIN-1 slice C — THE SPINE (45.1%).** Confirmed biggest. Needs driver-minted proc-entry `bb_label_t`
   table + one in-band `E`/`F` record; **READ THE BB-CODEGEN DESIGN SET FIRST (PLAN.md step 6).**
2. **XA-FLAT-CONVERT** — rules-mandated prerequisite for the `lexprep2` half of the spine (14.9%), and clears
   the last `--strict` gate failure (`xa_flat.cpp(128)`, verified pre-existing s149).
3. **`trail_unwind` (15.3%)** — the single hottest entry and it is NOT on the s148 radar at all. Backtracking
   edge; pairs naturally with `unwind_nothrow` (6.3%) = **21.6% combined.** Strong candidate for #2.
4. **`mkc` (7.4%)** — reinstated as a real target; s148's "poor target" call was 5-program sampling.
5. **PLBB-1 / VVB (~6% ceiling)** — demoted. Design work in the section above stays valid for when it comes up.

## SESSION-END STATE
No source modified. SCRIP + corpus trees clean. This FINDING is the only new file (untracked in `.github`).
`xa_flat.cpp(128)` gate failure pre-existing and untouched. Instruments in `/home/claude/meas/`.
