# FINDING 2026-08-27 (seat04) — row `perf-call-by-name-census-and-rank`: census built, ranked, one new gap found, cure work NOT attempted here

**Date:** 2026-08-27 · **Seat:** seat04 (FLEET-16) · **Row:** `perf-call-by-name-census-and-rank` (hq_P mint, rank 1) · **Build:** SCRIP HEAD at time of measurement (post `git pull --rebase`, working tree clean) · **RT_OPT=-O0** (mandatory, s262 FACT RULE) · **Instrument:** callgrind Ir only (`SIMS=0`), via `scripts/profile_box_histogram.sh` · **Witness:** `corpus/benchmarks/snobol4/roman.sno`, `bench_wrap.sh --mode=iter --n=20000`, output verified `check: 1102`. **Tool this row also delivers:** `SCRIP/scripts/util_call_by_name_census.sh` — re-run it for a fresh number; do not carry today's Ir figures forward as if pinned.

## What this row is, and what it deliberately is not

The disease: a runtime mechanism reached through a generic string-keyed lookup (hash/strcmp/table scan) on every use, where a direct or cached reference would do. It was measured three unrelated times in one day before this row existed (seat05's `$`-indirection probe, seat01's `nv-set-fn` memo A/B, and the already-closed `perf-nv-set-capture-pump`) — hence a class row, not three findings (row-factory discipline, RULES.md § NO-PER-OP-FILTER). This row's own charter is **census and rank, not cure** — it must not become an umbrella that can never close (the `perf-roman-8x`/`perf-string-runtime`/`sweep-free-rows-are-real` shape the row's own brief explicitly warns against). Zero cures attempted or landed in this session.

## Headline: this disease class is far more worked than the minting brief suggested

Before measuring anything fresh, tracing the task-file graph (`tasks/*.task.md`, several NOT present in `QUEUE.tsv` at all — see Queue-hygiene note at the end) found that the general builtin-by-name dispatch chain (`try_call_builtin_by_name_bl` → `rt_call_arr_impl` → `rt_call_arr_bl`) already has **three sibling rows, all CLOSED**, with real measured wins:

- `perf-by-name-builtin-dispatch` (umbrella) — CLOSED 2026-08-24. One safe cure landed directly (SNO$NOFAIL second-character guard, −1.39%).
- `perf-dispatch-callsite-cache` — CLOSED. STEP2 (redundant memcmp skip on the bid-keyed array-cache path, −2.41%) + STEP3 (C-only fast path for 14 niladic bid-keyed builtins, −4.264% on top) = **1.070x combined** vs the pre-STEP2 baseline on `string_manip.sno`. STEP1 (the full emit-time persistent-cell cure) was **withdrawn**, not deferred — hq_C ruled it unsafe as designed (setjmp/longjmp retargeting + DT_DATA field-precedence hazards, both verified, neither a plumbing gap). One optional follow-up flagged there and not re-minted here: extending STEP3's shape to the RELOP family (EQ/NE/LT/…) — blocked on those builtins having no `BID_*` entry at all, a different blocker than this row's own new finding below.
- `perf-dispatch-gc-safepoint-necessity` — CLOSED. Inlined the cheap `g_gc_pending` check ahead of the safepoint veneer (−3.99% on `string_manip.sno`), mirroring an existing precedent in `rtx_plunify.S`. The harder register-parking-necessity question was left open **by explicit HQ-only-mints ruling** (its own NEXT: "mint is HQ's call, not a seat's") — flagged again below, not minted by this row either.

The variable-by-name cluster (`NV_GET_fn`/`NV_SET_fn` + `_var_hash`/`_var_bucket_find`) is **partially closed**: the read side (`defer-nv-read-by-pointer-not-name`) and the write side's dominant caller (`perf-nv-set-capture-pump`, the capture-pump call site) are both CLOSED. `NV_SET_fn`'s own remaining cost is `perf-nv-set-fn-o0-overhead` (still open, PARKED) — and as of TODAY, separately, its item-1 accounting gap was closed by seat07 (`FINDING-2026-08-27-seat07-nv-set-fn-accounting-gap-CLOSED-inlined-var-find-cached.md`, pulled fresh this session): **100% of the function's 50,492,413 Ir is now named**, and item 3 (a cure for the fast-path-hit line, 13,403,067 Ir / ≈3.7% of that session's kernel) is **now unblocked**, not attempted by anyone yet.

## This census's own fresh measurement (via the new script, pristine build, current HEAD)

```
$ make pristine && bash scripts/util_call_by_name_census.sh
```

⛔ **CAUGHT AND CORRECTED IN-SESSION, kept here rather than silently fixed — exactly the trap HQ-27's "gate verdicts require `make pristine`" discipline exists for.** A first run of this script, against the `scrip`/`libscrip_rt.so` binaries already sitting in `out/` at session start (built 15:11 by a prior session, before this row was claimed), reported `NV_SET_fn` at **52,328,457 Ir**. After `make pristine` (full rebuild against current HEAD, forced by this same discipline before trusting any gate as a verdict), the identical script against the identical witness reports **26,073,364 Ir** — essentially half. Every OTHER site's absolute Ir was unchanged to the instruction between the two runs (`rt_call_arr_impl` 8,725,254 both times, `try_call_builtin_by_name_bl` 7,096,635 both times), which rules out a witness/tooling difference and confirms the two runs used genuinely different binaries. **The table below is the pristine-verified number at HEAD `fddbbd02`; the 52.3M figure is void, not a second data point to average.**

**A plausible, evidence-based (not proven — no isolated A/B run) explanation for the direction, not just the staleness:** seat07's own 50,492,413 Ir citation was measured at SCRIP `89c8c654`. `git log --oneline 89c8c654..HEAD -- src/runtime/core/core.c src/runtime/by_name_dispatch.c src/runtime/rt/rt_protected.*` shows 36 commits landed since, including `264f8226 perf-nv-set-capture-pump: eliminate by-name NV_SET_fn calls from rt_dcap_pump's write arm` — and `rt_dcap_pump` was `NV_SET_fn`'s single largest caller context in every prior citation (23,317,465 of the 46,453,125 combined, ≈50%). A commit that specifically removes NV_SET_fn calls from that exact caller landing in this window is directionally consistent with the total dropping by roughly half. **Not verified by a controlled before/after on this specific commit this session** — reported as the likely explanation, not a proven cause, per this project's own control-arm discipline (a plausible mechanism is not the same evidence class as a measured A/B).

| rt:function | Ir (pristine, this run) | Ir% | Status |
|---|---:|---:|---|
| `NV_SET_fn` | 26,073,364 | 7.7% | OPEN — item 3 (fast-path-hit cure), see above, PARKED/unclaimed |
| `rt_call_arr_impl` | 8,725,254 | 2.6% | CLOSED — `perf-dispatch-gc-safepoint-necessity` |
| `rt_call_arr_bl` | 7,504,214 | 2.2% | OPEN — `setjmp-per-builtin-call`, unclaimed |
| `try_call_builtin_by_name_bl` | 7,096,635 | 2.1% | CLOSED — `perf-dispatch-callsite-cache` |
| `_var_hash` | 4,201 | 0.0% | MITIGATED — `SCRIP_NV_MEMO` cache (default on) starves the slow path almost entirely on this witness |
| `_var_bucket_find` | 315 | 0.0% | MITIGATED — same cache |

**Methodology note, not a discrepancy to chase:** `util_call_by_name_census.sh` reports whole-function self-cost with no `--separate-callers` split (profile_box_histogram.sh doesn't expose that flag), so this isn't directly diff-able against seat07's `--separate-callers=2`-derived 50,492,413 (measured at SCRIP `89c8c654`, likely also a different exact tree — this run's own HEAD is whatever `git log -1` reads at execution time). The ranking conclusion is unaffected either way: `NV_SET_fn` is this disease class's single largest remaining item on this witness, bigger than the entire builtin-dispatch-chain trio combined (23.3M vs 26.1M) even at the corrected, lower figure.

`_var_hash`/`_var_bucket_find` reading near-zero is the **expected, correct** signature of the memo cache doing its job (matches seat01's A/B: these costs "do not exist at all when the cache is populated") — not a sign the census missed something.

## The one genuinely NEW item this census found: `SNO$NAME` is fast-path-eligible but not fast-pathed

`$`-indirection (`$nm`) lowers to `IR_CALL "SNO$NAME"` (confirmed via `--dump-ir-verbose` in seat05's finding) and dispatches through the exact same `try_call_builtin_by_name_bl` chain as any other by-name call. Checked directly against source this session:

- `SNO$NAME` **has** a stable `BID_*` entry (`builtin_ids.h:241`, id 53) — structurally eligible for the same bid-keyed array-cache path STEP2's cure already covers, and it already reaches a cheap post-resolution jump via the pre-existing `g_bidjmp_on` switch (default on, `by_name_dispatch.c:5256`, confirmed `case BID_SNOx24NAME: goto L_bidjmp_6468`).
- `SNO$NAME` is **not** among STEP3's 14-name C-only fast-path list (SIZE/TIME/TRIM/DATE/DUPL/LPAD/RPAD/REMDR/SUBSTR/REPLACE/REVERSE/INTEGER/IDENT/DIFFER) — all 14 are **niladic**; `SNO$NAME` takes one argument (the name to resolve), so whether STEP3's exact mechanism (a switch gated on `rt_dtax_gen==0`, placed after the DT_DATA check, inside the setjmp scope) transfers cleanly to a monadic builtin is **unverified, not assumed** — that verification is exactly what a child row should do, not something this census claims to have proven.
- **Why this matters more than it looks:** per `FINDING-2026-08-27-seat05-nd2-subscript-narrowed-and-name-indirection-measured.md` (same day, cited not reproduced here — re-running that isolated probe would be pure duplication of a fresh, properly-labeled, same-tool measurement), `SNO$NAME`'s own dispatch is the **single largest contributor** in an isolated `$`-indirection-vs-direct-access probe: **≈2.06M Ir, ≈42%** of that workload's indirection overhead — larger than the entire `NV_GET_fn`/`NV_SET_fn`/`_var_hash`/`_var_bucket_find`/`VARVAL_d_fn` layer beneath it (≈36%). `roman.sno` (this census's own witness) doesn't isolate this cost the way seat05's dedicated probe does, which is why it doesn't show up as a distinct line in the ranked table above — it's already inside `try_call_builtin_by_name_bl`'s aggregate self-cost, not separable without a dedicated `$`-heavy witness or per-bid instrumentation.

**Child row minted for this:** `perf-dispatch-fastpath-name-indirect` (see below) — scoped to *investigate and, if safe, extend* STEP3's shape to `SNO$NAME`, explicitly not pre-judged as safe.

## A deliberate non-finding, worth recording so nobody re-walks this path

Prolog's own by-(name,arity) predicate resolution (`resolve_bb_lookup`, `resolve_pred_hash`, `resolve_pred_table_lookup` in `src/runtime/builtins/resolution.c`) is **not** a runtime dispatch site: grepped every caller and all of them are in `src/lower/lower_prolog.c` and `src/driver/driver_hooks.c` — compile-time (lowering-phase) resolution only, consistent with "language identity stops at lower" and the BB architecture's own invariant that ports are wired at compile time. **Out of scope for this disease class by construction**, not by oversight.

Two smaller candidates identified but **not measured** (no Ir number to rank by, so no child row minted — would violate this row's own "rank by attributable Ir" discipline to mint on a guess): `rt_builtin_is_known`'s linear `strcmp` scan over a ~90-name static table (`by_name_dispatch.c`), and `keywords.c`'s `kwb_find` (small fixed `&`-keyword table). Both are bounded, small-N linear scans, not obviously hot-path; flagged here for whoever runs this census next rather than guessed at.

## Recommendation, ranked, for whoever picks up next (this row does not cure any of it)

1. **`perf-nv-set-fn-o0-overhead` item 3** (unclaimed, PARKED) — highest measured Ir of anything in this whole class on the standard witness, even after this session's own correction (26.1M Ir whole-function, this row's pristine measurement at HEAD `fddbbd02`; 13.4M Ir was the more precisely isolated fast-path-hit line per seat07 at the older `89c8c654`, itself likely now smaller too given the intervening capture-pump landing — whoever picks this up next should re-isolate the line fresh rather than trust either older figure). Now fully unblocked (accounting gap closed).
2. **`perf-dispatch-fastpath-name-indirect`** (new, minted by this row) — smaller in this census's own witness, but seat05's isolated measurement suggests high relative value for any workload that leans on `$`-indirection; also directly informs the open "does `.NAME`'s representation need a semantics ruling" question already deferred to Lon.
3. **`setjmp-per-builtin-call`** (existing, unclaimed) — the setjmp/longjmp scope wrapping the whole by-name dispatch chain; 7.5M Ir self-cost on `rt_call_arr_bl` this run, unknown how much is the setjmp mechanism itself vs. other work in that function — not decomposed by this census.
4. **Register-parking necessity inside the GC safepoint** — real, larger-upside, harder question; per `perf-dispatch-gc-safepoint-necessity`'s own explicit ruling, minting this is HQ's call, not a worker seat's. Flagging it here for hq_P rather than minting it.

## Queue-hygiene note (adjacent, fixed in passing, not this row's main scope)

Two task files central to this exact disease class — `perf-by-name-builtin-dispatch.task.md` and `perf-dispatch-callsite-cache.task.md`, both CLOSED — are **not present in `QUEUE.tsv` at all** (confirmed: `grep` for either topic string returns nothing in the index). Since both are closed this is inert today, but it means a future `next` picker can never surface them and nobody auditing `QUEUE.tsv` alone would know this cluster existed. Not fixed in this session (out of this row's scope, and the two rows are already closed so there's no dispatch-eligibility bug to fix the way `tests-consolidate-prolog`'s stale `FREE` state was earlier this session) — flagged here as a receipt in case a future queue-hygiene pass wants a starting list.

## Reproduction

```bash
cd SCRIP
make            # if not already built
bash scripts/util_call_by_name_census.sh
```
Refuses (rc=2) if the compiler isn't built, the witness is missing, valgrind isn't on `PATH`, or a cited symbol has been renamed/removed from the source since this census was written — proven live this session (`WITNESS=/nonexistent/path.sno bash scripts/util_call_by_name_census.sh` → rc=2, before ever attempting a real (successful) run).
