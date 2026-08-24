# FINDING 2026-08-24 — seat12 — `perf-string-runtime` STEP 7: fresh reconciliation after two landed dispatch cures, a third getenv-memo instance, and the startup-cost asymmetry quantified

## Scope and comparability

STEP 6's own closing note (seat04): *"No further open thread identified on THIS row from this pass — whoever continues should re-survey the kernel (or pick a fresh one, e.g. `table_access`/`roman` for the same class of check) rather than assume one is already queued."* Checking that instruction literally, both suggested fresh kernels already carry their own dedicated, actively-claimed rows (`perf-roman-8x`, `perf-table-subscript-fastpath`) — picking either up under this row would duplicate scope already owned elsewhere, not extend it. So this pass takes the other branch: **re-survey `string_manip.sno`'s own kernel**, this row's actual lane.

- Pulled fresh: SCRIP `ef18421e` (14 commits past STEP 6's `0f4231f8`), corpus `c294d7c1`.
- ⭐ **Two of those 14 commits are real, landed cures directly in this row's own territory**, both downstream of evidence this row fed to `perf-by-name-builtin-dispatch`: `2d8d6df7` (seat08 — `SNO$NOFAIL` guard extended to a 2-character pre-filter, stops paying a full `strcmp` for every ordinary `'S'`-leading builtin) and `5d6f8a71` (skip the redundant `memcmp` recheck on the array-cache path once `bid_of()` already proves identity). Neither touches `string_manip.sno`'s other cited paths (`core.h`, `bn_size`'s own body, `rtx_alloc.S`, `gc_heap.c`'s allocator) — confirmed by `git log 0f4231f8..ef18421e -- src/runtime/by_name_dispatch.c src/contracts/core.h src/runtime/rt/gc_heap.c src/runtime/rtx` before trusting any number below.
- Fresh own-build (`make`, RT_OPT confirmed `-O0 -g -fno-strict-aliasing -fwrapv -fno-omit-frame-pointer` on every compile line, per the s262/s266 NO-`-O2`-EVER FACT RULE), fresh `bench_wrap.sh --mode=iter --n=20000` twin, mode-4 (`scrip --compile`, `gcc -no-pie -Lout -lscrip_rt -lm`).
- **`check: 43`** on both engines — matches every prior citation on this row exactly.
- ⚠️ **Self-inflicted near-miss, recorded honestly**: the first `profile_callgrind.sh` invocation on the SCRIP binary produced `TOTAL_Ir=66,804`, 100% dynamic-linker-startup-shaped — the exact "implausibly tiny Ir total" failure mode seat02's STEP 4 LEDGER already documented for a mis-invoked SPITBOL run. Cause here was different but the *symptom* is the same named class: `LD_LIBRARY_PATH` wasn't set for the `-no-pie` mode-4 binary (unlike the `scrip` driver itself, which is `-rpath`'d), so the program errored `error while loading shared libraries: libscrip_rt.so` before executing a single instruction of program code, and callgrind happily profiled the failed dynamic-link attempt instead. Setting `LD_LIBRARY_PATH=$SCRIP/out` before the callgrind invocation fixed it. Recorded so the next session recognizes the symptom immediately rather than re-diagnosing it.
- SPITBOL side: `sbl_clean_bin()`/`sbl_lang_flags()` per the one authority, hand-invoked under `valgrind --tool=callgrind` (its CLI-arg source invocation doesn't fit `profile_callgrind.sh`'s stdin-only signature, same reason seat02's STEP 4 hand-invoked it).

## A. Headline ratio reconciliation: the two landed dispatch cures move this row's own number for the first time since STEP 2

Fresh, same-tree, same-run apples-to-apples:

| engine | Ir @ N=20000 | check |
|---|---:|---|
| SCRIP (mode-4, `-O0`, `ef18421e`) | **49,258,250** | 43 |
| SPITBOL (`sbl_clean_bin()`, `-bf`) | **13,019,733** | 43 |

Ratio (SBL Ir / SCRIP Ir, this row's own established axis, above 1.00x = SCRIP ahead): **0.2643x**.

⭐ **The correct comparison baseline is STEP 2's re-measurement (0.2546x), not the original BRIEF's headline (0.2696x)** — STEP 2 (seat04) already established the BRIEF's own absolute numbers are retired as a comparison baseline (the SPITBOL-side figure alone moved for reasons predating the s255 two-oracle split, unrelated to anything measured since). Against the correct baseline:

- STEP 2 (seat04, `411bd9de`): SCRIP 51,121,149 / SPITBOL 13,017,534 = **0.2546x**
- This session (`ef18421e`): SCRIP 49,258,250 / SPITBOL 13,019,733 = **0.2643x**
- **Relative improvement: 1.038x (+3.8%)** — real, measured, and directionally/magnitude-consistent with the two landed commits' own self-reported deltas (`2d8d6df7`: −714,014 Ir; `5d6f8a71`: −1,218,706 Ir; combined −1,932,720 vs. this session's measured −1,862,899 from the STEP 2 baseline — within ~0.14% of the kernel, inside this row's already-documented ~0.1–0.3% cross-session noise floor, not a discrepancy worth chasing further).

SPITBOL's own number is unchanged within noise (13,017,534 → 13,019,733, 0.017%) — as expected, nothing on the SPITBOL side moved. **The entire ratio improvement is the two dispatch cures**, cleanly attributable, no other variable in motion.

⚠️ For anyone tempted to compare against the BRIEF's 0.2696x and call this a regression: don't — that number is pre-s255-oracle-split and already retired as a baseline per STEP 2's own LEDGER. Comparing against it here would silently resurrect exactly the mistake STEP 2 flagged.

## B. Cross-validation: every not-yet-cured bucket reproduces byte-identical on a fully independent build

Five previously-cited, still-unowned-by-any-landed-cure self-cost figures reproduce **exactly**, Ir-for-Ir, on this session's independent fresh build (different session, different clone, 14 commits later, only the two dispatch-path files touched in between):

| symbol | prior citation | this session | match |
|---|---:|---:|---|
| `bn_size` (by_name_dispatch.c) | 1,932,004 | 1,932,004 | exact |
| `IS_CSET_fn` | 672,000 | 672,000 | exact |
| `rt_gcheap_alloc` | 650,982 | 650,982 | exact |
| `__strchr_avx2` (phantom) | 635,418 | 635,418 | exact |
| `__sigsetjmp` + `__sigjmp_save` | 924,474 + 546,039 | 924,474 + 546,039 | exact |

This is strong, independent confirmation that the whole six-STEP investigation chain is sound — not an artifact of any one session's build, clone state, or measurement quirk. `bn_replace`'s own self-cost sum (18,986,411, STEP 3's exact-arithmetic citation) also reproduces exactly, confirming neither landed cure touches `bn_replace`'s own body (both live in the general dispatch layer `bn_replace` calls *through*, `rt_call_arr_impl`/`try_call_builtin_by_name_bl`, not in `bn_replace` itself).

## C. A third instance of the "non-inlined getenv-memo call tax at `-O0`" mechanism: `repl_pl_off`

New in this session's top-30 (not previously named in any `perf-string-runtime` LEDGER entry): `by_name_dispatch.c:5093`, `repl_pl_off()`:
```c
static int repl_pl_off(void) { static int v = -1; if (v < 0) { const char *e = getenv("SCRIP_REPL_PL"); v = (e && *e == '0') ? 1 : 0; } return v; }
```
— `bn_replace`'s own `SCRIP_REPL_PL` killswitch memo, already hoisted (per its own header comment) to be read once per `bn_replace` call rather than three times. Cost: **210,009 Ir, 0.43% of kernel**, 20,999 calls.

This is the **identical code shape** to two already-known instances: `rt_alloc_hist_on` (`perf-alloc-hist-gate-unconditional-call-tax`, 215,862 Ir/0.42% on this same kernel) and `dtax_off` (`GOAL-HQ-PERFORM.md` R-11, cited there at 0.57% on `roman`; independently re-measured this session at **420,029 Ir, 0.85%** on `string_manip.sno` — the largest of the three on this kernel, and not previously cited for this kernel specifically). All three: `static int f(void){static int v=-1; if(v<0){v=<getenv-derived init>;} return v;}`, plain `int`, not GC-observable, not reachable from the deferred-capture engine — the exact safety shape `perf-alloc-hist-gate-unconditional-call-tax`'s own NEXT already argues clears `always_inline` of the s264 risk.

⭐ **This may widen more than scope.** R-11 frames `dtax_off`'s own fix as needing *"a file-scope cached flag, i.e. a new global... not taken without [Lon's grant]"* — written before `perf-alloc-hist-gate-unconditional-call-tax`'s later argument that the identical shape is safe to `always_inline` directly, no new global required. If that argument holds, it plausibly holds for `dtax_off` and `repl_pl_off` too, meaning R-11's "blocked on a global-variable grant" disposition for `dtax_off` may be stale rather than settled. **Not verified this pass** — no source read of the always_inline safety argument was re-derived per-instance, and no source edits were made (row-factory). Fed to `perf-alloc-hist-gate-unconditional-call-tax`'s LEDGER as a scope-widening note; not resolved unilaterally, and not re-minted as a duplicate row.

## D. The dynamic-linker/startup asymmetry, quantified on this kernel for the first time

`GOAL-HQ-PERFORM.md` R-11 notes, in the context of `roman` at N=2000: *"Startup — ~3.6M Ir, dominated by `_dl_relocate_object` against a 34 MB `libscrip_rt.so`. Invisible in the slope, but it is 8.7% of an N=2000 run and it is what makes the quotient basis lie."* This session's `string_manip.sno` N=20000 profile lets that claim be checked on a **different kernel, different N, apples-to-apples against SPITBOL's own equivalent cost** for the first time:

| | SCRIP (dl-relocate + do_lookup_x + dl-new-hash + check_match) | SPITBOL (dl-relocate + dl-lookup) |
|---|---:|---:|
| Ir | 3,913,862 | 39,656 |
| % of that engine's own kernel | **7.95%** | **0.30%** |

SCRIP pays **~100x more** dynamic-linker/relocation Ir than SPITBOL for the equivalent startup work, both in absolute terms and — more importantly for this row's own headline ratio — as a *share of its own kernel*. This corroborates R-11's ~3.6M-Ir figure as a fairly kernel/N-independent **fixed per-process cost** (this session's 3.91M on a completely different kernel/N is the same order of magnitude, not a coincidence of roman's own shape), and confirms it is asymmetric: SPITBOL's own binary appears not to pay a comparable relocation tax for whatever it links against.

**This is a basis caveat, not a new runtime-service defect** — R-11 already names the mechanism and already frames it as a TOTAL-vs-SLOPE methodology question (*"invisible in the slope... what makes the quotient basis lie"*), not a call to action, and this row (like every citation on it) has always measured on a TOTAL basis (one N, not a two-N difference), so this fixed cost has been baked into every ratio this row has ever cited, including §A's above. Not minted as a new row; recorded here as the first cross-kernel magnitude confirmation of R-11's claim, and flagged so a future SLOPE-basis remeasurement of this row's own headline ratio (subtracting this fixed cost) is understood to read *more* favorably for SCRIP than any TOTAL-basis number this row has ever quoted, including this one.

## E. Minor corroboration: the `descr.h:bn_size` split-attribution reproduces too

STEP 6 documented a second, separately-DWARF-keyed citation, `descr.h:bn_size`, 84,000 Ir (0.16-0.17%), a compound-literal-macro DWARF-line-table artifact (`FAILDESCR`/`INTVAL`), not a distinct cost center. It reproduces exactly (84,000 Ir) on this session's build — small, but consistent with §B's broader pattern that nothing in `bn_size`'s own body moved.

## F. Current top-of-profile is now ~fully attributed — closure question raised, not decided here

This session's fresh top-17 (full list in the raw profile, available on request) maps, bucket for bucket, onto rows this investigation has already minted or GOAL-HQ-PERFORM rungs that already own the mechanism:

| bucket | % of kernel | owned by |
|---|---:|---|
| `bn_replace` (translate loop + body) | 38.54% | `perf-replace-translate-loop-scalar-byte-copy` |
| opaque BB-port labels (`main`, `???:0x401276`) | 9.72% | `callgrind-opaque-bb-labels` |
| `try_call_builtin_by_name_bl` / `rt_call_arr_impl` / `rt_call_arr_bl` | 21.95% combined | `perf-by-name-builtin-dispatch` (+ children `perf-dispatch-callsite-cache` [partly cured], `perf-dispatch-gc-safepoint-necessity`) |
| `bn_size` | 3.92% | this row's own STEP 5/6 + `perf-core-tag-predicate-o0-call-tax` (dead-code option) |
| dl-relocate/dl-lookup (startup) | 2.39%+1.75%+1.59%+... | `GOAL-HQ-PERFORM.md` R-11 (§D above) |
| `rt_gc_point_arr_c`/`rt_gc_point_arr` | 3.75% combined | `perf-dispatch-gc-safepoint-necessity` |
| `__sigsetjmp`/`__sigjmp_save` | 2.99% combined | `setjmp-per-builtin-call` |
| `__memcmp_avx2_movbe` | 1.62% | `perf-dispatch-callsite-cache` (already halved) / `perf-replace-map-cache-revalidation` |
| `IS_CSET_fn`/`IS_INT_fn`/`IS_REAL_fn` | 2.46% combined | `perf-core-tag-predicate-o0-call-tax` |
| `rt_gcheap_alloc`/`rt_ws_alloc_c` | 2.13% combined | `GOAL-HQ-PERFORM.md` R-9/T-3 |
| `__strchr_avx2` (phantom) | 1.29% | `callgrind-ifunc-phantom-attribution` |
| `dtax_off`/`repl_pl_off` (getenv-memo family) | 1.28% combined | `perf-alloc-hist-gate-unconditional-call-tax` (§C, scope-widening fed, not resolved) |

That is essentially the entire kernel. STEP 6 already found "no further open thread" on this kernel; this session's reconciliation is the same conclusion from an independent angle — nothing in the current top-of-profile lacks an owner. **This is the same shape `perf-table-array-runtime` was in when hq_C ruled (s270) to close it as SUPERSEDED with `perf-table-subscript-fastpath` named successor** (*"You reached the same conclusion from two independent sessions... and both released it FREE with nothing curable left in scope; that IS the finding, and the right way to record it is a closure with a pointer, not an open row nobody can discharge."*). Sent as a QA ask to hq_C (topic `q-perf-string-runtime-close`, not decided unilaterally here) rather than closed on this session's own authority.

## What this feeds

- **`perf-string-runtime`** (this row): §A is the fresh headline number, §F is the closure question, both belong in this row's own NEXT/LEDGER.
- **`perf-alloc-hist-gate-unconditional-call-tax`**: §C, a scope-widening note (third instance, `dtax_off`'s "needs a new global" framing possibly stale).
- **`GOAL-HQ-PERFORM.md` R-11**: §D, first cross-kernel magnitude confirmation of the startup-cost claim (not edited directly — HQ's own cross-cutting file, noted here and in the QA ask instead).
- **hq_C**: closure question for this row (§F), same shape as the `perf-table-array-runtime` precedent.

No cure applied anywhere. Zero edits to any `.c`/`.h`/`.S`/`.cpp`/`.sno` source this session (row-factory duty, same as every prior STEP on this row).
