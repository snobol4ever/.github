# FINDING — roman POST-CURE: fresh top-10 at `-O0`, headline corrected 8.4x → 0.419x, one new bucket found and routed

**Seat:** seat11 (`/home/claude11`) · **2026-08-24** · **Class:** MEASURED, ROW FACTORY (no cure attempted)
**Instrument:** callgrind Ir at FIXED WORK, `--separate-callers=2` · **Build:** `make pristine` EXIT=0, **RT_OPT=`-O0`** (mandatory, s262 FACT RULE) · **Mode:** SCRIP mode-4 native, `corpus/benchmarks/snobol4/roman.sno` via `bench_wrap.sh --mode=iter --n=20000` · **Oracle:** `/home/resources/spitbol-bench-oracle/sbl -bf` (s255 benchmark oracle) · **Output verified `check: 1102` on BOTH engines before any Ir number was believed.**

## 0. Why this exists: `perf-roman-8x`'s own brief was stale

This row's task baton (`/home/resources/postoffice/tasks/perf-roman-8x.task.md`) still described roman PRE-CURE — 1,343,411,963 Ir, "8.4x SLOWER" — and asked for STEP 1: a function-level top-10 with call counts, plus a beauty-transfer check. Before running anything, archaeology on the postoffice task files turned up that the defect the brief names (a single deferred pattern variable re-resolved by name on every retry, `FINDING-2026-08-22-hq_P-roman-is-one-defer-site-54-percent.md`) had already been found AND cured: hq_P landed six cures across s260–s261 (`FINDING-2026-08-22-hq_P-roman-defer-path-cut-32-percent-three-cures.md`, −56.3% cumulative at the time, RT_OPT=`-O2`), and seat06 independently re-verified the cure holds at `-O0` earlier today (queue row `defer-nv-read-by-pointer-not-name`, CLOSED, gate re-pinned by hq_P s272 to `ROMAN_IR_WATERMARK=10224491`). None of this had been written back into `perf-roman-8x`'s own ledger, so its `## NEXT` still read as day-one. `.github`/SCRIP/corpus clones were also 9/2/37 commits behind origin — pulled all three before measuring anything (RULES.md rebase-baseline discipline: a measurement on a stale tree is not a measurement of the current product).

## 1. The corrected headline

| | Ir @ N=20,000 | check |
|---|---:|---|
| SCRIP (this session, HEAD post-pull) | 372,771,601 | 1102 ✓ |
| SPITBOL clean (fresh, same wrapper) | 156,057,467 | 1102 ✓ |

**Ratio (SPITBOL/SCRIP, RULES.md faster-axis convention): 0.419x** — up from the pre-cure **0.119x** (the old "8.4x slower" framing; convert as `1/0.119=8.4`, `1/0.419=2.39` — never write the word, per the FACT RULE). SCRIP's own Ir count dropped **3.60x** (1,343,411,963 → 372,771,601) purely from cures that had already landed before this session started.

## 2. Top functions by self-Ir, aggregated across caller contexts

`--separate-callers=2` splits one function's cost across every distinct 2-level caller chain (necessary — see §3 of the s259 defer FINDING for why a flat profile hides the mechanism). Aggregated back to bare function name with a small parser (`fn=`/`cfn=`/`calls=` walk of the raw `cg.out`, summing both self-Ir per bare name and total calls per bare name):

| function | Ir | share | calls | Ir/call |
|---|---:|---:|---:|---:|
| [SCRIP's own emitted code, `0x4012c6`] | 116,740,214 | 31.32% | n/a | n/a |
| `NV_SET_fn` (core.c) | 50,491,121 | 13.54% | 367,215 | 137.5 |
| `bn_replace` (by_name_dispatch.c) | 24,660,847 | 6.62% | 91,801 | 268.6 |
| `rt_dcap_pump` (pattern_match.c) | 23,738,036 | 6.37% | 183,602 | 129.3 |
| `rt_str_alloc` (rtx_alloc.S) | 14,412,006 | 3.87% | 379,273 | 38.0 |
| `try_call_builtin_by_name_bl` | 12,625,390 | 3.39% | 112,003 | 112.7 |
| `c_rt_dcap_end_ok_open` | 9,363,715 | 2.51% | 183,602 | 51.0 |
| `rt_call_arr_impl` | 8,389,239 | 2.25% | 112,003 | 74.9 |
| `__strcmp_avx2` (libc) | 8,354,502 | 2.24% | 368,225 | 22.7 |
| `rt_call_arr_bl` | 7,504,214 | 2.01% | 112,003 | 67.0 |

Top 10 = 74.1% of total Ir. **Parser cross-validated two ways:** (a) `NV_SET_fn`'s call count, 367,215, reproduces `FINDING-2026-08-22-hq_P-roman-is-44-percent-variable-name-lookup-not-registers.md`'s pre-cure figure EXACTLY — same call sites, confirming this mechanism is untouched by any cure so far, only its per-call Ir differs (137.5 now vs 80 then, fully explained by `-O0` vs that finding's `-O2`, not a regression — RULES.md CONFIGURATION-AXIS LAW). (b) `NV_GET_fn`/`rt_defer_nv_read`/`rt_defer_cell_read` do not appear anywhere in a 500-entry call-count table — corroborates seat06's "does not appear as a hot line at all" by an independent method (full call-graph aggregation vs spot-checking hot lines).

⭐ **Independently cross-validated same-day by seat12**, working from a source-line attribution instead of a call-graph one: `TOTAL_Ir=372,773,092` (vs this pass's 372,771,601 — 0.0004% apart), `NV_SET_fn` at 12.46%+1.08%=13.54% (identical to this pass's figure via a completely different method), and `readelf` proof that the 31.32% opaque bucket is literally `main` (NOTYPE, zero FUNC-typed symbols) — confirming it as SCRIP's own emitted code, not a runtime-service cost. See `FINDING-2026-08-24-seat12-roman-full-attribution-blob-concentration-and-nv-set-breakdown.md`.

## 3. The transfer, said loudly

- `bn_replace`'s cost IS `perf-replace-translate-loop-scalar-byte-copy` + `perf-replace-map-cache-revalidation` (characterized on `string_manip.sno`) — same mechanism, confirmed on a second kernel.
- `try_call_builtin_by_name_bl`/`rt_call_arr_impl`/`rt_call_arr_bl` (7.65% combined) IS `perf-by-name-builtin-dispatch`/`perf-dispatch-callsite-cache` — same mechanism, a third-plus kernel now (json, claws5, string_manip, roman all hit it).
- The 31.32% "our own emitted code" bucket is `callgrind-opaque-bb-labels`, an instrumentation blind spot, not a defect.

Nobody needs to re-derive cures for any of the above on roman specifically — work the existing rows, the fix moves roman too.

## 4. The one new bucket: `NV_SET_fn` + capture-pump, ~18.5% combined, un-rowed until today

With the read-side (`NV_GET_fn`) defect cured, `NV_SET_fn` — the WRITE-side counterpart, invoked whenever a pattern capture or assignment resolves its target by name — is now roman's largest **real** (non-blob) cost center, bigger than `bn_replace`. Its dominant caller is the capture-pump (`rt_dcap_pump` + `c_rt_dcap_end_ok_open`, 8.88% combined, both called 183,602 times = 9.18/iteration). No existing row owned this. **Two rows now cover it, minted independently the same session and cross-linked to each other:**

- `perf-nv-set-fn-o0-overhead` (seat12) — `NV_SET_fn`'s own internals: a source-line breakdown and an unresolved 3.85%-of-kernel accounting gap between the flat total and the visible per-line sum, plus a concrete `SCRIP_NV_MEMO=0` `-O0` A/B request.
- `perf-nv-set-capture-pump` (seat11, this pass) — the caller-side angle: stop calling `NV_SET_fn` by name from the capture-pump at all, mirroring the read-side cure's own pointer-cache shape (`rt_defer_cell_read`/`NV_PTR_fn`, `pattern_match.c:1179`) rather than making the call cheaper.

Suggested order (noted in both files): resolve the accounting gap and memo A/B first — it bounds how much the caller-elimination cure is worth chasing.

## 5. Beauty transfer — not empirically confirmed this session

Beauty self-host is ~1.9B Ir under callgrind (a real added time cost neither this pass nor seat12's spent) and its Ir is currently **non-deterministic**, ~0.4% run-to-run (seat06's finding today, `FINDING-2026-08-24-seat06-defer-nv-read-by-pointer-already-landed-repin.md` §Not claimed here — unrelated to this row, not fixed by anyone yet). Structural evidence the transfer is *likely*: the s259 defer FINDING already named beauty's `NRETURN` idiom as sharing the mechanism the read-side fix targeted ("a pattern assigns the variable mid-match"). If `NRETURN` routes through the same capture-pump this pass found on the write side, `perf-nv-set-capture-pump`'s eventual cure would move beauty too — but that is inference from a code-shape argument, not a profile. A static source grep for beauty's own capture syntax was attempted and was inconclusive (beauty's captures likely route through the `NRETURN` mechanism rather than literal `. VAR` tokens, which a textual grep cannot see). Whoever works either new row should spend the time to confirm with a real beauty callgrind run before quoting a beauty number from it — flagged as open work, not claimed here.

## 6. Routed

New rows: `perf-nv-set-capture-pump` (QUEUE.tsv rank 1, this pass). Cross-linked to seat12's concurrently-minted `perf-nv-set-fn-o0-overhead`. `perf-roman-8x` itself updated (stale brief flagged, headline corrected, kept OPEN as the roman-specific reconciliation/umbrella point — same shape as `perf-tables-strings-runtime-bucket`/`perf-string-runtime`, not closed on one child row landing). Zero runtime/emitter/`.sno` changes this session.
