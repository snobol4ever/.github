# FINDING 2026-08-24 seat01 — `perf-string-runtime` STEP 1: fresh -O0 attribution, string_manip vs string_concat. Two existing child rows fed fresh evidence, one new row minted.

**Row:** `perf-string-runtime` (rank 0, dispatch-locked via `s4e_msg.sh next`). Task text is explicit: **"⛔ ROW FACTORY: rank, mint rows, do not cure."** This FINDING is investigation output, not a cure.

## Pinned measurement conditions (apples-to-apples)
SCRIP `69449f94` (post strip-wave 3b, `make pristine`, clean tree) · corpus `35b7d034` (clean tree) · **RT_OPT = `-O0`** (Lon s262 FACT RULE — no `-O2` builds, ever) · mode-4 (`--compile` + `gcc -no-pie ... -lscrip_rt`) · instrument `valgrind --tool=callgrind` (Ir) · fixed-work mode via `scripts/bench_wrap.sh <k>.sno --mode=iter --n=20000` (N baked in, no wall-clock deadline anywhere in the run — the correct arm for callgrind per `FINDING-2026-08-22-bench-harness-unmeasurable.md`). Both kernels are now standalone applications (s265 revamp); the harness is inlined by `bench_wrap.sh`, not `-INCLUDE`d.

⛔ **THE OLD `58.6%` / `42,754,772` Ir FIGURES (hq_P s259, `FINDING-2026-08-22-hq_P-three-losing-kernels-three-root-causes-two-are-by-name.md`) ARE `-O2` AND ARE NOT COMPARABLE TO ANYTHING BELOW.** `RT_OPT=-O2` is retired by Lon's s262 FACT RULE; this session's numbers are the current, citable state. Re-baselined, not subtracted-across-arms.

## Correctness (verified, not assumed)
Both kernels: `check: 43` (string_manip) / `check: 1000` (string_concat), m3 (`--run`) ≡ m4 (native `.bin`) byte-for-byte on stdout, matching the pre-existing `.ref`-equivalent baseline (hq_P s259's `check: 43` citation for string_manip).

## Headline totals (N=20000, whole-program Ir including the phase-1 CHECK call)
| kernel | total Ir | Ir/iter (N=20000) |
|---|---|---|
| string_manip | 50,956,778 | 2,547.8 |
| string_concat | 28,239,769 | 1,412.0 |

⛔ **SPITBOL-side `842 Ir/iter` / `3.7x` is NOT RE-MEASURED THIS PASS** — carrying it into a ratio with today's SCRIP number would violate the apples-to-apples FACT RULE (old orientation, different RT_OPT context on the SCRIP side even if SPITBOL is unaffected by SCRIP's RT_OPT). This FINDING supplies fresh SCRIP-side attribution only, per the row's own STEP 1 ask; a fresh oracle-side run is a separate, small, un-minted step if anyone wants the ratio re-stated.

## Methodology trap found and falsified by injection: dynamic-linker relocation cost is FIXED, not per-iteration
`_dl_relocate_object` / `do_lookup_x` / `_dl_lookup_symbol_x` appear high in both profiles (~3.36M Ir combined in string_manip, 6.6% of its total). Hypothesis: one-time ELF lazy-PLT-binding cost proportional to the *set* of distinct external symbols referenced, not to iteration count. **Falsified by injection**, not assumed: re-ran string_manip at N=2000 (10x fewer iterations) — `_dl_relocate_object` **1,176,238 Ir at both N=2000 and N=20000, byte-identical**; same for `do_lookup_x` (862,025) and `dl-new-hash.h:_dl_lookup_symbol_x` (539,200). Confirmed fixed. **Consequence for this and future callgrind kernels: do not divide this cost by N and call it per-op — it is a process-startup tax that shrinks as a fraction of total the larger N gets, and inflates a small kernel's overhead-looking percentage.** Not a SCRIP defect, not minting a row for it — flagging so nobody double-counts it against a code cure.

## The contrast the task asked for: string_concat pays ZERO by-name dispatch
string_concat's top-10 Ir list (`rt_sxt_extend` 23.11%, `c_str_concat_d` 16.21%, `descr_to_str`/`rt_sxt_note`/`descr_slen` coercion+bookkeeping ~13%, `IS_{NULL,STR,INT,REAL}_fn` type tags ~9% combined, GC safepoints ~3%) contains **no `try_call_builtin_by_name`, no `rt_call_arr_*`, no `bn_*`, anywhere in the profile.** `S = S 'x'` lowers to a BINOP-CONCAT template (`bb_binop_concat_slot.cpp`) that calls `str_concat_d`/`c_str_concat_d` directly — the compiler already knows which runtime entry point CONCAT is and bakes a direct call. string_manip's `REPLACE(S,...)`/`SIZE(S)` are ordinary function-call-syntax builtins, resolved by **runtime string-name lookup on every single call** even though `REPLACE`/`SIZE` are spelled in the source and never vary. **This is the isolating contrast: it is not "strings" that are slow, it is specifically function-call-syntax builtins going through by-name dispatch — exactly the `name-lookup-strcmp` CLASS row's thesis, now confirmed on a second, independent kernel with a clean same-session control.**

## string_manip's attribution, and where each piece already has (or now gets) a queue row

| Ir | % of total | source | disposition |
|---|---|---|---|
| ~18,986,411 | 37.26% | `bn_replace` (own body — includes real translate work AND its own dispatch-like ceremony, see below) | split below |
| ~11,676,856 | 22.92% | outer by-name dispatch chain: `try_call_builtin_by_name_bl` 5,166,515 + `rt_call_arr_impl` 3,276,165 + `rt_call_arr_bl` 2,814,147 + `dtax_off` 420,029 | **fed to `perf-by-name-builtin-dispatch`** (existing row, unblocks its STEP 1) |
| ~1,932,004 | 3.79% | `bn_size` (SIZE's own by-name-dispatched call, same outer chain cost not double-counted here — this is its body) | same class as above, smaller instance |
| ~1,470,000 (est.) | ~2.9% | `__sigsetjmp` 924,474 + `__sigjmp_save` 546,039 | **fed to `setjmp-per-builtin-call`** (existing row, confirms still-live at current HEAD) |
| ~3.36M+ | ~6.6%+ | `_dl_relocate_object`/`do_lookup_x`/`_dl_lookup_symbol_x` | fixed one-time cost, not a code defect (see above) |
| ~1,596,991 | 3.13% | `memcmp` (`__memcmp_avx2_movbe`) | **split ~50/50, see below** |
| remainder | ~23% | `rt_gc_point_arr_c`/`rt_gc_point_arr` (GC safepoints), `IS_CSET_fn`, `rt_gcheap_alloc`, `strchr`/`strcmp`, `rt_ws_alloc_c` | genuine per-call runtime cost, not attributed to a ceremony class here |

### The `memcmp` split, and the new finding it exposes
Two, and only two, call sites in `by_name_dispatch.c` invoke `memcmp` on the hot path: **(a)** `by_name_dispatch.c:5287`, the OUTER dtax name-cache hit-check (`_dx->gen==rt_dtax_gen && _dx->len==_dxl && !memcmp(_dx->nm, fn, _dxl)`) — one call per by-name dispatch attempt, i.e. once per `REPLACE`/`SIZE` call-site invocation; **(b)** `by_name_dispatch.c:5107`, **`bn_replace`'s OWN internal 4-slot translation-map cache** (`!memcmp(g_rm[s].f,fv,fl) && !memcmp(g_rm[s].t,tv,fl)`) — up to two calls per `bn_replace` invocation, checking whether the cached FROM/TO map still matches THIS call's arguments.
Call-count cross-check (not just self-cost location): total calls into `REPLACE`+`SIZE` across the whole run = 1,000 (CHECK phase) + 20,000×2 (MEASURE phase, one REPLACE + one SIZE per ZBL iteration) = 21,000 REPLACE + 21,000 SIZE = 42,000 outer dispatch attempts → 42,000 outer memcmp calls (site a). `bn_replace` runs 21,000 times → up to 42,000 inner memcmp calls (site b, 2/call on a cache hit). **Sum = 84,000, matching the measured caller-tree count of 83,997 (+49 noise) almost exactly** — the two sites split the 1,596,991 Ir roughly 50/50, ≈798K Ir (1.57%) each.
**Site (a) is already `perf-by-name-builtin-dispatch`'s business** (it's part of the outer name→pointer resolution). **Site (b) is a DIFFERENT, more specific defect: `REPLACE`'s own map-cache re-validates via hash+2×memcmp on every single call, even though `string_manip.sno`'s FROM (`'aeiou'`) and TO (`'*****'`) arguments are compile-time string literals that never change across all 21,000 calls in this program.** Per the pre-existing inline measurement note at `by_name_dispatch.c:5085` (hq_P s262, on a different kernel, `roman.sno`), this cache-check (hash + 2 memcmp PLT hops) is ~101 of `bn_replace`'s ~480 Ir/call — roughly 21% of the function's own cost, ≈4% of a REPLACE-heavy kernel's total. **This is a THIRD, distinct sub-defect, not covered by either existing child row** (the outer-dispatch row is about reaching `bn_replace`'s pointer; this is about what `bn_replace` does AFTER it's been reached). New row minted: `perf-replace-map-cache-revalidation` (see below).

## Actions taken on the row graph (row-factory duty, not a cure)
1. **`perf-by-name-builtin-dispatch`** (existing, unassigned, rank 0) — LEDGER updated with this session's fresh -O0 numbers, directly answering its own blocking STEP 1 ("confirm current cost at HEAD... re-state it here before proceeding"). Confirmed: still the dominant cost class, ≈22.9%+ of string_manip's total at current HEAD, shape unchanged from the s259 diagnosis even though the absolute Ir moved with RT_OPT. Not claimed/cured here.
2. **`setjmp-per-builtin-call`** (existing, unassigned, rank 2) — LEDGER updated with fresh evidence (~2.9% at -O0/current HEAD, same shape as the s259 citation). Does not answer its own open design question (what does the setjmp actually guard); left as-is.
3. **`perf-replace-map-cache-revalidation`** (NEW, rank 2) — minted for the site-(b) finding above, with a citation of both this FINDING and the pre-existing `by_name_dispatch.c:5085`/`:5264` inline notes (hq_P s262) that had already partially characterized the shape on a different kernel without their own queue row.

## Files/commands for reproduction
`bash scripts/bench_wrap.sh corpus/benchmarks/snobol4/string_{manip,concat}.sno -o <out>.sno --mode=iter --n=20000` → `./scrip --compile -o <out>.s <out>.sno </dev/null` → `gcc -no-pie <out>.s -Lout -lscrip_rt -Wl,-rpath,out -o <out>.bin` → `valgrind --tool=callgrind --callgrind-out-file=<out>.callgrind ./<out>.bin </dev/null` → `callgrind_annotate --threshold=95 <out>.callgrind`. Raw `.callgrind` files kept in this session's scratchpad only (not committed — regenerate via the above; `.s`/binary artifacts are honest current output, never pinned goldens, per RULES.md).
