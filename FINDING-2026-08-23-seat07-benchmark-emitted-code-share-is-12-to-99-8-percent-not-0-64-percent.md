# FINDING seat07 — on 7 diverse `corpus/benchmarks/` kernels, emitted code is 11.9%–99.8% of Ir, never close to beauty's 0.64%: box-fusion and its siblings are RE-RANKED UP, loudly

**Session:** 2026-08-23 seat07 (`/home/claude07`), postoffice task `profile-benchmarks-not-just-beauty` (rank 0, locked via `s4e_msg.sh next`).
**Instrument:** `valgrind --tool=callgrind --dump-instr=yes --cache-sim=yes --branch-sim=yes` via `scripts/profile_box_histogram.sh`, mode-4 **standalone** (compile happens once, unmeasured, before callgrind starts — compile bucket is 0% *by construction*, not estimated). RT_OPT=`-O0` (default). Oracle correctness unaffected (measurement-only session).
**Tree:** all three repos pulled current mid-session (SCRIP `76ec253d`, corpus `f34ce80a`, `.github` `23888ab6`) after discovering a stale local `corpus` clone (§1) — nothing left uncommitted anywhere by this session except this file.

---

## 0. Answering the brief's own prerequisite FIRST: how many kernels are even measurable?

**14 of 15.** `array_sum` SIGSEGVs deterministically under valgrind in both modes (native 3/3 clean) — this is `FINDING-2026-08-22-hq-m3-executes-three-times-m4-on-beauty-and-the-benchmark-harness-cannot-be-instrumented.md` §7's defect, tracked live and still open as `array-sum-valgrind-segv` (checked this session — unfixed, unassigned). Excluded here, as it was from seat2's original 15-kernel sweep. The other 14 all compile, link, and run clean under callgrind.

---

## 1. The harness.inc coercion defect: already cured — by seat12, same day, credited here after a genuine near-collision

`rung-harness-zk-string-coercion` names a real defect, independently confirmed by two sessions on two kernels (`FINDING-2026-08-22-seat06-...` on `arith_loop`; `FINDING-2026-08-22-seat01-kill-the-plt-...md` §6 on `func_call`): `harness.inc`'s FIXED-WORK block set `ZK = fixed_n`, and `fixed_n = INPUT` — SNOBOL4 `INPUT` always returns STRING, never coerced before use — so `rt_coerce_num2_d` re-ran a from-scratch STRING→numeric coercion every steady-state iteration (70.29% of `arith_loop`'s Ir in seat06's measurement).

This session independently re-derived the same root cause while establishing a clean measurement baseline for §2 below — including, unprompted, the same generalization seat06's own narrower `ZK = fixed_n + 0` proposal missed (that a future kernel pinning its own `ZK` would still hit the bug via `LT(ZN, fixed_n)` on the outer batch loop, since it skips the `ZK = fixed_n` copy entirely) — and landed a fix at `harness.inc`'s `ZFIXRUN` label. **Before pushing, discovered `rung-harness-zk-string-coercion` was already claimed, fixed, measured, and closed by seat12 earlier the same day** (corpus `6f9b82dd0`, `.github` `f2df80b6`, `FINDING-2026-08-23-seat12-fixed-n-string-coercion-cured-564m-ir-removed-on-both-kernels.md`, task file state `DONE`) — landed while this session's local `corpus` clone was still 90+ commits behind origin, a live instance of exactly the PULL-BEFORE-TRUST lesson `FINDING-2026-08-23-seat13-...` names from this same day. Diffed the two independently-derived fixes: **byte-for-byte identical code change** (`ZFIXRUN fixed_n = fixed_n + 0` at the exact same line, same reasoning about the pinned-`ZK` path), differing only in comment wording. Discarded this session's duplicate local edit and pulled seat12's landed version rather than create a competing commit.

Seat12's own measurement (reconstructing the pre-migration stdin-gate mechanism specifically to get a before/after number, N=2,000,000): `arith_loop` 908,916,459 → 308,056,779 Ir (**−66.1%**), `func_call` 1,099,475,651 → 498,680,595 Ir (**−54.6%**), `rt_coerce_num2_d` 564,000,282 → 0 Ir in both. That is the real, citable before/after for this defect — not reproduced here.

**Separately, and this is the operative fact for §2 below**: the corpus's *current* iteration-count mechanism is `bench_wrap.sh --mode=iter --n=N` (Lon's s265 standalone revamp — every kernel `.sno` is now standalone with its own `END`/`.ref`, selected via a `*BENCH kernel=...` marker; `-INCLUDE 'harness.inc'` + stdin is legacy), which **bakes `fixed_n = N` as a source-level integer literal**, never via `INPUT`. A source-level literal is INTEGER-tagged at parse time and structurally never enters the STRING-coercion path regardless of whether `harness.inc`'s own defensive fix is present — confirmed empirically, not just reasoned: none of §2's seven fresh histograms (measured post-pull, so on top of seat12's landed fix regardless) show any `rt_coerce_num2_d`/`rt_parse_num_d` presence. §2's bucket table was never at risk from this defect either way.

`rung-harness-zk-string-coercion` is **not this row's to close** — seat12 already did, correctly, same day (task file `owner: seat12 · state: DONE`, real `grep`-based `DONE-WHEN`). Not touched further here beyond crediting it above.

Corpus README.md's benchmark section still describes the pre-s265 `-INCLUDE`-mandatory shape (`"check: <value>"` `.ref` format, `-INCLUDE 'harness.inc'` required) — stale (already flagged independently by `FINDING-2026-08-23-seat13-...` this same day), not fixed here (out of this row's scope).

---

## 2. THE DELIVERABLE — per-workload bucket table, 7 kernels, current mechanism, zero known artifacts

Chosen to span every bucket in HQ's original beauty taxonomy (by-name resolution / pattern engine / table-array / string ops) plus the two call-shaped kernels the demotion note itself leaned on. Compile = 0% for all seven **by construction** (mode-4 standalone: compile happens once, unmeasured, outside the callgrind region — not an estimate, a structural guarantee, same as `FINDING-2026-08-22-seat04-perf-board-rebaseline...` §3b already established for `fibonacci`).

`DL-startup` is a new, small, well-understood artifact this session's methodology surfaces: `_dl_relocate_object`/`do_lookup_x`/`_dl_lookup_symbol_x` — one-time dynamic-linker cost of loading `libscrip_rt.so`, **identical absolute Ir across every kernel** (≈10.08M cyc-proxy, confirming it's N- and kernel-independent, pure process-startup), shrinking as a % at higher N. Shown separately, not folded into "runtime," so nobody mistakes it for genuine per-iteration cost the way the old `ZK` defect got mistaken for `arith_loop`'s "real" runtime cost.

| kernel | N | total Ir | **emitted-code** | by-name-res. | pattern-engine | table/array | string-ops | GC/alloc | DL-startup¹ | other/tail |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `arith_loop` | 2,000,000 | 266,800,133 | **98.3%** | 0.0% | 0.1% | 0.0% | 0.0% | 0.0% | 1.4% | 0.2% |
| `fibonacci` | 3,000 | 1,765,322,025 | **99.8%** | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.2% | 0.0% |
| `func_call` | 2,000,000 | 451,839,477 | **99.0%** | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.9% | 0.1% |
| `indirect_dispatch` | 200,000 | 359,067,758 | **14.8%** | 74.3% | 0.0% | 0.0% | 0.5% | 3.3% | 0.8% | 5.4%² |
| `pattern_bt` | 200,000 | 1,149,138,224 | **31.0%** | 29.3% | 37.1% | 0.0% | 0.0% | 1.0% | 0.2% | 1.4% |
| `string_concat` | 400,000 | 459,955,159 | **11.9%** | 0.0% | 1.7% | 0.0% | 78.7% | 6.5% | 0.9% | 0.3% |
| `table_access` | 800 | 446,880,782 | **33.1%** | 0.0% | 0.0% | 58.8% | 0.0% | 6.4% | 0.9% | 0.8% |
| — beauty self-host (HQ, for scale)⁴ | — | 27,780,439,752 | 0.64% | 48.64% | 0.74% | 0.73% | 0.20% | 0.23% | — | 46.77%³ |

¹ DL-startup, excluded and renormalized (i.e. the steady-state figure a much larger N converges to): arith_loop 99.7%, fibonacci 100.0%, func_call 99.9%, indirect_dispatch 14.9%, pattern_bt 31.1%, string_concat 12.0%, table_access 33.4% — moves nothing by more than 0.4 points; DL-startup is real but small at these N.
² `indirect_dispatch`'s "other" is mostly `rt_nret_fix`/`rt_nret_fix_tiny` (return-value fixup, call-machinery-adjacent, left uncategorized rather than force-fit) plus `__sigsetjmp`/`__sigjmp_save` (the by-name call path's non-local exit machinery).
³ beauty's "other" bucket is dominated by in-process **compile** (46.77%), which does not exist as a bucket at all on these seven — mode-4 standalone structurally cannot compile in the timed region, so it isn't "small," it's absent, per `FINDING-2026-08-22-seat04-...` §3b.
⁴ Cited as the historical figure that drove the demotion this row exists to revisit, not re-measured here. `beauty.sno`'s own text changed (BEAUTY-CN `&`-constant conversion, commit `336f49d28`, same day as the original measurement) — `FINDING-2026-08-23-seat15-reprofile-after-byname-bake-beauty-fixed.md` §4 confirms the per-function composition/ranking "remains valid" post-change (qualitatively nothing shifted), so the 0.64% figure is trustworthy as a reference point; a byte-exact re-measurement of beauty itself is out of this row's scope.

**The one-line answer the brief asked for:** emitted code's Ir share on a real, long-running kernel ranges **11.9% to 99.8%** — **19x to 156x** beauty's 0.64% — and is the single largest bucket outright (≥98%) on 3 of the 7 kernels tested. It is never, on any workload measured to date by any session, close to beauty's figure.

### 2a. Cross-validation against prior sessions (different day, different mechanism, same conclusion)

- **`fibonacci`**: this session 99.8% (Ir), `FINDING-2026-08-22-seat04-...` §3b measured 99.79% (m4-standalone) / 98.34% (m3) on 2026-08-22's mechanism. Two independent sessions, one day apart, two different generation mechanisms (old stdin-gate vs. new bake-in), agree to within 0.01–1.5 points. Strong corroboration the number is real, not a methodology artifact.
- **`arith_loop`**: not directly comparable to seat06's 7.23%/24.34% figure — seat06 measured the *isolated six-box fusion-target statement's* share of a *coercion-corrupted whole-kernel* run; this session measures the *whole kernel's* emitted-vs-runtime split on a *defect-free* run. Different numerators and denominators by design. Both point the same direction (box-fusion's target is far above 0.64%); neither contradicts the other.
- **`func_call`**: seat01's non-artifact call cost (≈198–201 Ir/call, §6 of their FINDING) is a per-call marginal cost, not a whole-kernel bucket share — this session's 99.0% whole-kernel emitted-code share is the complementary, coarser-grained view of the same underlying fact (func_call is almost entirely emitted-code cost once the harness artifact is removed).
- **`indirect_dispatch`, `pattern_bt`, `table_access`, `string_concat`**: no prior bucket-table measurement exists for these four on any mechanism — first coverage.

---

## 3. RE-RANKING, STATED LOUDLY

**`box-fusion` — PROMOTE.** Currently rank 6 per `ARCH-PERF-TOOLING.md` §7, demoted on beauty's 0.64% alone with an explicit, now twice-independently-met reinstatement condition ("DO NOT PROMOTE IT BACK without a measured emitted-code share on `corpus/benchmarks/`"). `FINDING-2026-08-22-seat04-...` already called this met on `fibonacci` alone; this session adds six more kernels, four of them from bucket categories `fibonacci` didn't touch (by-name, pattern, table, string), and the emitted-code share is **≥11.9% on all seven, ≥98% on three**. There is no longer a credible reading of the evidence where box-fusion targets "the smallest bucket in the profile" — on 3 of 7 real kernels it targets the *only* bucket that matters. Recommend restoring it to at least its pre-demotion rank (rank 1, per `ARCH-PERF-TOOLING.md` §7's own account of where s250 originally filed the lever that replaced `chain-slot-coalescing`).

**`chain-slot-coalescing` — STAYS CLOSED, and QUEUE.tsv's contradiction should be resolved.** This is not this session's mechanism (slot coalescing specifically) being re-litigated: `FINDING-2026-08-21-s250` measured it negative on its own terms (arms A/B identical at 112.24/112.25 instr, 24.05/24.05 stores) — a result about *that mechanism*, not about the emitted-code bucket's overall size, and nothing here changes it. `box-fusion`'s own queue text already says chain-slot-coalescing is CLOSED for exactly this reason, while the row itself still sits at rank 2 as if open (flagged already by `FINDING-2026-08-22-seat04-...` §6/§8, unresolved as of this session — checked `QUEUE.tsv` directly, still contradictory). Restating rather than re-deriving: **someone with QUEUE.tsv write authority should close the row**, not reopen the mechanism.

**Every other emitted-code-bucket row — REVIEW FOR PROMOTION, same evidence applies.** `ir-ident-differ-inline`, `rtcc-veneer-strip-pure-asm`, `loopctl-inline-lt-concat-store`, `spine-carve-coalescing` all target emitted code directly (per `FINDING-2026-08-22-seat04-...` §6's own by-name verdict list) and were ranked in the same queue that used beauty as its implicit yardstick. This session doesn't have per-row ROI numbers for each (out of scope — this row measures workloads, not individual optimizations), but the bucket they all share is now shown real and large on the majority of tested kernels; none should be read as "small" on beauty's word alone.

**⭐ The broader finding, which matters more than any one row's rank:** HQ's original 8-bucket taxonomy (by-name resolution / compile / pattern engine / table-array / emitted code / GC / string ops) is not wrong — it's **complete and workload-relative**. This session's seven kernels each let a *different* bucket take the #1 spot: by-name resolution dominates `indirect_dispatch` (74.3%), pattern-engine and by-name split `pattern_bt` roughly evenly with emitted code (37.1% / 29.3% / 31.0%), table/array dominates `table_access` (58.8%), string-ops dominates `string_concat` (78.7%), and emitted code dominates the three call/arithmetic kernels (98–99.8%). **No single workload — beauty included — can rank these buckets against each other**; each bucket's rank depends entirely on which workload shape it's judged against. Any future queue-priority pass that uses one workload's profile to rank rows targeting *other* buckets will reproduce exactly this session's root problem on a different pair of rows. The fix is structural: keep a small standing panel of workload-shape-diverse kernels (this session's seven are a reasonable starting set) and re-rank against the panel, not against whichever single profile HQ happened to run last.

---

## 4. Task file / row closure

- `profile-benchmarks-not-just-beauty`: DONE-WHEN rewritten from prose-refusal to a real check (grep for this file + the bucket table); calling `s4e_msg.sh done profile-benchmarks-not-just-beauty`.
- `rung-harness-zk-string-coercion`: **not touched** — already `owner: seat12 · state: DONE` before this session pulled current. Credited in §1; no action taken on the row itself.
- `array-sum-valgrind-segv`: untouched, unclaimed, still open — noted in §0, not this row's scope.
- `bench-rebaseline-15-kernels-clean-oracle` (seat13, same day): different axis entirely (wall-clock throughput vs. clean-SPITBOL oracle, all 15+3 kernels) — no overlap with this row's Ir-bucket-composition question; cross-checked, not redundant.
