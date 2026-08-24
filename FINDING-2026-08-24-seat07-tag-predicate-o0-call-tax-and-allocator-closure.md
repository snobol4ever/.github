# FINDING 2026-08-24 seat07 — `perf-string-runtime` STEP 5: the `IS_CSET_fn`/`rt_gcheap_alloc`/`rt_ws_alloc_c` chase

**Task:** `perf-string-runtime` (FLEET-4, picked via `s4e_msg.sh next`). STEP 4 (seat02) named these three symbols
"the ONE candidate direction from the original STEP-4 fork that's now unambiguously the ONLY one left untried."
This session chased all three, fresh, on `string_manip.sno`'s own kernel (not borrowed from `roman.sno`).
Row-factory pass: **measure, mint, no cure attempted — zero edits to any `.c`/`.h`/`.S`/`.cpp` source.**

## Provenance
SCRIP HEAD `447faf10` (3 commits past seat04's `411bd9de`; `git log 411bd9de..447faf10 -- src/runtime/by_name_dispatch.c src/runtime/rt/gc_heap.c src/runtime/core/core.h` empty — directly comparable). corpus/`.github` pulled current. Build: plain `make`, `RT_OPT=-O0` (the only legal arm, FACT RULE s262). `bench_wrap.sh --mode=iter --n=20000` on `corpus/benchmarks/snobol4/string_manip.sno`, compiled mode-4 (`--compile` → `gcc -no-pie *.s -Lout -lscrip_rt -lm -Wl,-rpath,out`), profiled via `scripts/profile_callgrind.sh`.

**Correctness + cross-validation:** `check: 43` (matches every prior session's citation). `TOTAL_Ir=51,186,375` vs seat04's `51,121,149` at `411bd9de` — 0.13% drift, noise not regression, same figure seat04 already certified. The three target symbols' **self-cost Ir is byte-identical** to seat04's own citation in `FINDING-2026-08-24-seat04-string-manip-spitbol-remeasure-and-bb-label-blindspot.md` (672,000 / 650,982 / 399,004) — independent confirmation the numbers are stable, not measurement noise.

| Ir | % of kernel | symbol |
|---:|---:|---|
| 672,000 | 1.31% | `IS_CSET_fn` |
| 650,982 | 1.27% | `rt_gcheap_alloc` |
| 399,004 | 0.78% | `rt_ws_alloc_c` |

## 1. `IS_CSET_fn` — REAL, not phantom, and it generalizes to a whole family. NEW ROW MINTED.

`IS_CSET_fn` is one of six `static inline` one-liners in `src/runtime/core/core.h:28-33` (`IS_NULL_fn`, `IS_STR_fn`, `IS_INT_fn`, `IS_REAL_fn`, `IS_CSET_fn`, `IS_DATA_fn`), each a single boolean expression over a 16-byte-by-value `DESCR_t`. **At `-O0`, `static inline` is not honored** — confirmed at the object-code level, not inferred:

- `nm out/libscrip_rt.so`: `IS_CSET_fn` **7** separate compiled instances (one per translation unit, internal linkage), `IS_INT_fn` **8**, `IS_REAL_fn` **9**, `IS_STR_fn` **6**, `IS_NULL_fn` **3**.
- `objdump` on one instance (`33307b <IS_CSET_fn>`): a full 19-instruction function body — `push rbp; mov rbp,rsp; ` two register-to-stack spills, compare, branch, `pop rbp; ret` — for what is logically `v.v==DT_S && v.slen==0xFFFFFFFFu`.
- **20 real `call` instructions** project-wide target an `IS_CSET_fn` instance (verified via full disassembly, not sampling). Callers mapped by address include `bn_size` (×2 — **string_manip.sno's own SIZE builtin**), `try_call_builtin_by_name_bl` (×4 — the by-name dispatch machinery this whole umbrella row is about), `c_rt_size_d`, `rt_num_arith_impl`, `bn_type_datatype`, `cset_resolve`, `binop_apply`, and others.
- **Control, same file, same one-line shape:** `rt_plain_int_str` (`core.h:59`) carries `__attribute__((always_inline))`. `nm`: **zero** instances. `grep -c "call.*rt_plain_int_str"` over the same disassembly: **zero**. Forcing inlining works when asked; plain `static inline` at `-O0` does not.
- Own-kernel magnitude (fresh, this session): `IS_CSET_fn` 672,000 Ir (1.31%, ~21,000 calls per the raw `.callgrind` `cfn=`/`calls=` record, ≈32 Ir/call) + `IS_INT_fn` 273,104 (0.53%) + `IS_REAL_fn` 273,065 (0.53%) = **1,218,169 Ir, 2.38% of the whole kernel**, all of it call/ret/frame-setup ceremony around one-line boolean checks.

⛔ **THE OBVIOUS CURE IS A KNOWN, ALREADY-TRIED, ALREADY-REVERTED DEAD END — DO NOT REPEAT IT.** `GOAL-HQ-PERFORM.md:157`, verbatim: *"DO NOT CURE ANYTHING HERE WITH `always_inline`. TESTED AND REVERTED s264. Adding it to the 14 `core/core.h` tag predicates + `dtax_off` bought claws5 −0.42% / json −0.17% and BROKE THREE DEFERRED-CAPTURE TESTS (`058_capture_dot_immediate`, `059_capture_dollar_deferred`, `060_capture_multiple`), m3 wall time 4s → 402s."* Mechanism: forcing inlining moves the `DESCR_t` out of memory into a register across a call boundary the GC's conservative stack scanner depends on — `pattern_match.c` is the deferred-capture engine and cannot tolerate it.

⭐ **BUT A SAFE, ALREADY-SHIPPED ALTERNATIVE EXISTS IN THIS CODEBASE FOR THE IDENTICAL SHAPE.** `FINDING-2026-08-23-hq_P-claws5-1.36x-json-2.37x-four-per-call-resolutions-the-compiler-already-knew.md:63`, on hoisting a `patv_slot` tag check into its three callers as literal duplicated C rather than an attribute: *"Written out rather than made `always_inline` on purpose: s264 measured that `always_inline` on the descr.h/core.h tag predicates broke three deferred-capture tests... Three lines of stated duplication is the cheaper risk."* That cure landed and gated green (`make pristine`, corpus m3 359/1 m4 359/1). **Duplicating the one-line check literally at a specific hot call site does not touch the shared `core.h` declaration and does not risk the s264 regression** — at `-O0` the duplicated expression gets the same spill-after-every-statement treatment as any other straight-line code, it never becomes a register-resident value living across a call boundary the way a forced-inline substitution does.

**Minted `perf-core-tag-predicate-o0-call-tax`** — scoped narrowly to the `by_name_dispatch.c` call sites this kernel actually exercises (`bn_size`, `try_call_builtin_by_name_bl`), explicitly citing the s264 landmine so nobody re-attempts `always_inline`, and explicitly flagging that `try_call_builtin_by_name_bl` is general dispatch machinery that needs checking against deferred-capture reachability before landing (unlike `patv_slot`, which lives inside the capture engine itself and was fixed with full knowledge of that context).

## 2. `rt_gcheap_alloc` / `rt_ws_alloc_c` — REAL, genuine, and ALREADY OWNED. No new row.

Both are real, substantial, hand-written-asm-backed allocator work (`rt_gcheap_alloc` in `rtx_alloc.S`, the project's SIL bump allocator; `rt_ws_alloc_c` in `gc_heap.c:256` is a thin wrapper calling `rt_gcheap_alloc(HB_WSC, n)`) — not an `-O0`/inlining artifact, not a phantom. `bn_replace` (string_manip's REPLACE call) allocates its output buffer through exactly this path.

This is not new territory: `GOAL-HQ-PERFORM.md` already scopes it twice.
- **R-9** (`:492`, verbatim): *"DO NOT 'FIX' THE ALLOCATOR AS PART OF IT: `rt_ws_alloc_c` (workspace island, never freed, 60 Ir) vs `rt_str_alloc` (GC heap, ASM fast path, 38 Ir) — `bn_dupl` and `bn_trim` use the workspace too, so it is the family convention, and changing it is an allocation-policy decision with GC consequences."*
- **RUNG T-3** (`:628-824`) already has a fully-scoped three-part redesign (route `HB_WS`/`HB_WSS` through the GC heap with pinning, per Lon's own question *"Is the TABLE algorithm using GC HEAP? Or malloc/free?"*) — currently measured against `table_access`'s table-key leak specifically.

**What this session adds:** confirmation that T-3's mechanism is not table-key-specific — `bn_replace`'s output buffer (string_manip.sno, a program with zero `TABLE` usage) leaks into the same never-collected workspace island via the identical `rt_ws_alloc_c → rt_gcheap_alloc(HB_WSC,...)` path, on a second, unrelated kernel. **T-3's scope should read as "the whole `rt_ws_alloc_c`-calling family" (REPLACE/DUPL/TRIM/DATE-format buffers, `by_name_dispatch.c:5062,5070,5080,5111`), not just table keys** — worth a note for whoever next picks up T-3, not a new row. STEP 5's chase of these two symbols is closed: genuine cost, already owned, not a fresh defect.

## 3. Incidental find, same call path: `rt_alloc_hist_on` pays a real call on every allocation, always, even when the feature is off. NEW ROW MINTED.

Sitting directly on `rt_gcheap_alloc`'s own call path (`gc_heap.c:204,229,248,258,264,271` — the same allocator wrapper functions `rt_ws_alloc_c` belongs to) is `rt_alloc_hist_on()`, showing separately in the profile at 215,862 Ir / 0.42%. Its body (`gc_heap.c:155-159`):
```c
int rt_alloc_hist_on(void) {
    if (g_ah_on < 0) { const char *e = getenv("SCRIP_ALLOC_HIST"); g_ah_on = (e && *e && *e != '0') ? 1 : 0; ... }
    return g_ah_on;
}
```
`g_ah_on` is resolved **once**, before `main()` even runs, via `__attribute__((constructor)) static void rt_alloc_hist_init(void) { (void)rt_alloc_hist_on(); }` (`:161`). So for the entire steady-state run of every benchmark, this is a real function call — full call/ret, not `static inline` this time but an ordinary externally-linked function, called from **7 sites** covering every allocation type (`DT_S`, `HB_WS`, `HB_WSS`, `HB_WSC`, `HB_PLJ`, generic) — that does nothing but `return` an already-known global int. The lazy-init branch is provably dead code at steady state.

**This one carries none of the s264 risk**: `g_ah_on` is a plain `int`, not a `DESCR_t`, not GC-observable state, not reachable from the deferred-capture engine. `always_inline` (or simply reading `g_ah_on` directly, guarding the rare lazy-init separately) is a plain, low-risk fix by the same reasoning that already clears `rt_plain_int_str`. **Minted `perf-alloc-hist-gate-unconditional-call-tax`.**

## Housekeeping
- **QA flag resolved:** seat02's STEP 4 flagged `FINDING-2026-08-24-seat04-bn-replace-translate-loop-and-strchr-phantom-attribution.md` as absent from `.github` git history despite being cited pushed. It is present now (`git log` shows it landed at `458c4bb2`, `git ls-files` confirms tracked) — most likely seat02 checked before that commit had propagated to the clone in use. No action needed; noting for the record so nobody re-flags it.
- **Not chased, honest boundary:** `bn_size`'s own remaining breakdown (1,932,004 Ir / 3.77% of kernel, minus the ~2-call IS_CSET_fn share now attributed above) has no dedicated attribution yet. Candidate for whoever continues; out of this session's three-symbol brief.
- No cure attempted anywhere in this pass (row-factory), zero edits to any SCRIP source file. Releasing `perf-string-runtime` via `unclaim`.
