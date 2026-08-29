# FINDING 2026-08-29 (seat04) — `rt_gcheap_carve`/`c_rt_gcheap_alloc`/`gc_collect_ex` now attributable at all (crash-free), but sampled percentages are unstable under current FLEET-16 load

**Context:** `perf-match-begin-beta-cure`, GC+alloc thread. Prior sittings could not attribute `rt_gcheap_carve`/`c_rt_gcheap_alloc` because the only tool that could see inside a real GC-triggering workload (callgrind, on `table_access.sno --n=15000`) segfaults — that crash is the already-tracked, unrelated `array-sum-valgrind-segv` defect (see `.github/FINDING-2026-08-29-seat04-array-sum-segv-generalizes-again-seam-stack-traced-to-missing-gnu-stack-note.md`, this same day). This FINDING sidesteps that crash entirely by using real `perf` sampling (not callgrind/valgrind) on this row's own already-validated mode-4-standalone-binary recipe (proven crash-free and clean for the `NV_SET_fn` work). **No cure attempted, zero source edits.**

Trees: SCRIP `2bae6ff5`, corpus `8938ce076`, `.github` `16ddfd46` at session start. Toolchain: real `perf` at `/usr/lib/linux-tools-6.8.0-138/perf` (kernel-mismatch warning is cosmetic, per this row's own prior finding). Build: `./scrip --compile table_access_n15000.sno > p.s && gcc -no-pie p.s -L out -lscrip_rt -lm -Wl,-rpath,out -o bin` (mirrors `bench_sno_match4.sh`). Workload: `table_access.sno` via `bench_wrap.sh --mode=iter --n=15000` — the vehicle this row already established as the one that reliably triggers a real `gc_collect_ex` collection (porter never does, at any N tried).

## Result 1 — the method works: all four targets are visible, zero crashes, two independent trials

Both trials: native-correct (`check: 250500`, `iters: 15000`), `perf record -F max`, zero lost samples, no crash (contrast with callgrind/memcheck on the identical binary, which segfaults every time). `gc_collect_ex`, `rt_gcheap_alloc`, `rt_gcheap_carve`, and `c_rt_gcheap_alloc` all show up cleanly in both:

| symbol | run 1 (738ms, 21,671 samples) | run 2 (2,886ms, 82,654 samples) |
|---|---:|---:|
| `gc_collect_ex` | 19.35% (4,377) | 6.09% (5,429) |
| `table_set_descr_d` | 15.24% (3,239) | 6.83% (5,722) |
| `table_find_pair_d` | 3.62% (770) | 1.74% (1,458) |
| `_tbl_grow` | 2.66% (563) | 1.25% (1,042) |
| `rt_gcheap_alloc` | 1.34% (284) | 0.59% (490) |
| `rt_gcheap_carve` | 1.25% (282) | 0.54% (461) |
| `c_rt_gcheap_alloc` | 0.76% (173) | 0.35% (298) |

## Result 2 — but the exact percentages are NOT reproducible under this container's current load, and no single number here should be cited as precise

The two trials are back-to-back runs of the byte-identical binary against the byte-identical, deterministic workload (`check: 250500` both times) — yet total wall-clock differs **3.9x** (738ms vs 2,886ms) and total sample count differs **3.8x** (21,671 vs 82,654), and `gc_collect_ex`'s own percentage share swings from the single hottest symbol in the program (19.35%) to roughly a third of that (6.09%). This is the same FLEET-16 PMU-contention hazard this row already logged once for `perf stat -r N`'s aggregate mode (load average ~14-15/16 cores under concurrent seats) — now confirmed on `perf record`'s frequency-based sampling too, and at a much larger magnitude (3x on a headline number, not a small-effect noise floor).

**What is more robust:** the *raw sample counts* for these specific hot symbols grew far less between runs (`gc_collect_ex` 4,377→5,429, +24%) than the *total* sample count did (+282%) — the extra samples in run 2 are concentrated somewhere else, not spread proportionally across the whole profile. And the *relative ranking* among `table_find_pair_d`/`_tbl_grow`/`rt_gcheap_alloc`/`rt_gcheap_carve`/`c_rt_gcheap_alloc` is identical in both runs — only `gc_collect_ex` vs. `table_set_descr_d`'s rank-1/rank-2 order swaps. Neither of these secondary observations is chased to a mechanism here (plausible candidates: cache/memory-bus contention from sibling seats affecting the table/GC linear-walk code disproportionately, or scheduling-induced dilution elsewhere in the profile) — flagged as the natural next question, not answered.

**Cross-check against this row's own prior, differently-sourced measurement:** the earlier `SCRIP_ZETA_TELEM` phase-telemetry reading (a prior sitting, same workload) found `gc_collect_ex`'s internal cost is 66% `index` + 31% `fwd` (both full-arena linear walks) + 2.7% `mark`, with `rt_gcheap_verify()` dead at 0.002%. `perf annotate` on `gc_collect_ex` in run 1 shows sample density concentrated in exactly two large, separate address ranges within the function — consistent with two dominant loop bodies, matching the two-phase picture — but this binary carries no debug info (`addr2line` resolves nothing), so the two clusters could not be mapped to specific source lines/phase names this session; treat as corroborating shape, not a re-confirmation of the exact percentages.

## Disposition

**Genuinely new for this row:** `rt_gcheap_carve`/`c_rt_gcheap_alloc` are attributable at all for the first time (previously blocked by the crash) — both land in the low single digits (0.3-1.3%) across two trials, meaningfully smaller than `gc_collect_ex`/`table_set_descr_d` regardless of which trial's exact numbers are trusted. **Not established:** a precise, citable percentage for any of these symbols under current conditions — this needs either a lower-contention measurement window, many more trials averaged, or (this row's own proven fallback when sampling gets unreliable) a static/deterministic instruction-count technique in place of frequency sampling. Not attempted this session (time-boxed). No cure attempted; zero source edits anywhere.
