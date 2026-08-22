# FINDING seat05 — table-nested-subscript-cost: the compounding is per-hop allocation, not boxing or a
super-linear defect; a half-built optimization (`SCRIP_SUB_AGG`/"container-only") was completed and
measured to cut the fast-path case 8-14% at the mechanism level, 5.1% end-to-end on real claws5

**Session:** 2026-08-22 seat05 (`/home/claude05`, Claude Sonnet 5), THE LOOP queue row
`table-nested-subscript-cost`, rank 1 — **THE SINGLE BIGGEST PERF LEVER ON THE BOARD** per
`FINDING-2026-08-21-s199`. Sibling row `table-flat-1level-segv` (blocking dependency) was already closed
by seat6 as "does not currently reproduce" — unblocked, taken alone this session.
**Tree:** SCRIP `2659558e` at session start → rebased onto a concurrent landing of `ir-ident-differ-inline`
(seat07, see cross-reference below), pristine-rebuilt (HQ-27) at every step. corpus/`.github` untouched
except this session's own additions. RT_OPT=`-O0` (default, dev).

---

## 0. ⛔ ORACLE CORRECTION — the brief's own "0.17x" and seat6's partial ladder both predate the
## two-oracle ruling and are graded against the DIRTY oracle

`FINDING-2026-08-21-s199`'s 0.17x and seat6's addendum ladder (1.34x/0.53x/0.33x) were measured against
`x64/bin/sbl`, which the SAME-DAY, LATER `⛔⛔⛔ FACT RULE` in `RULES.md` (s255, "SETTLED — THE TWO-ORACLE
RULING") establishes carries a monitor-IPC bridge costing **~2.2-3.5x instructions** and must never be
used for benchmarking again — `/home/resources/spitbol-clean/sbl` via `lib_oracle_flags.sh`'s
`sbl_clean_bin()` is now the sole benchmark oracle. Separately, `scripts/test_bench_snobol4_timed.sh`
itself wasn't wired to the clean binary until commit `1aaa1d399` (**today, 15:42**, mid-fleet) — so no
number quoted anywhere before that commit, this row's own brief included, is comparable to what follows.
Re-measured against the clean oracle at session start (unmodified tree): **claws5 m3:sbl = 0.09x**, not
0.17x — the dirty oracle was flattering SPITBOL's relative cost. This is the correct starting point.

## 1. METHOD — mechanism probes, not inference

Built 10 new self-contained kernels in `corpus/probe/table_nested/` (not `corpus/benchmarks/.../demo/` —
dropping a `.sno` there joins the scored suite by construction; these are graded only via an explicit
`BENCH_DIR=` override, same convention `corpus/probe/claws5_table_flat1.sno` already established).
Every kernel's `check:` line is pinned from the **live correctness oracle** (`x64/bin/sbl -bf`), reconfirmed
oracle-identical in **both modes** (m3 `--run`, m4 `--compile`→link→run) at every rebuild this session:

- `chain_read_d{1,2,3}.sno` — pure READ at chain depth 1/2/3, table pre-built (no creation/IDENT in the
  timed loop), key cycles through 8 pre-seeded slots (`slot = slot+1`, `EQ`/reset at 7 — no division, no
  builtin beyond `LT`/`EQ` already proven by the harness itself) so the read cannot be trivially
  loop-hoisted. Same leaf value (`slot*3`, INTEGER) at every depth — isolates pure re-lookup cost as a
  function of hop count, nothing else varying.
- `value_type_tbl.sno` — same single-hop shape as `chain_read_d1`, except the stored value is a TABLE
  reference instead of an INTEGER — isolates "nested-table value boxing" from hop count.
- `ident_guard_d1.sno` — single hop, `level1[slot] = IDENT(level1[slot]) 99999`, table pre-seeded so
  IDENT always FAILS (claws5's own steady-state fast-fail path) — isolates the guard's dispatched-call
  overhead from everything else.
- `chain_incr_d{1,2,3}.sno` — `level1[...] = level1[...] + 1` at depth 1/2/3, no IDENT, pre-seeded —
  isolates the read-then-write cost claws5's own increment line pays.
- `claws5_l1.sno` / `claws5_l2.sno` — the REALISTIC ladder's rungs 1 and 2: `demo/claws5.sno` byte-for-byte
  except `token()`'s `mem[num][wrd][tag]` build is flattened to `mem[wrd]` (rung 1, exact recipe named in
  s199/seat6) or `mem[num][wrd]` (rung 2). Real `claws5.dat` on stdin (symlinked, same bytes level 3
  reads). Rung 3 is `demo/claws5.sno` itself, unmodified.

**Instrument choice, and why it differs from seat6's wall-clock addendum:** this session's fleet ran at
**load average 10-14 throughout** (7 other seats concurrently mid-`make pristine`, confirmed via `ps
aux`/`uptime`), which made wall-clock throughput readings swing up to 2x between back-to-back runs of the
*identical* binary/kernel/env — consistent with `ARCH-PERF-TOOLING.md`'s own instruction to prefer
`callgrind`'s `Ir` (deterministic, contention-immune) and with `perf-board-rebaseline`'s "INSTRUCTION
COUNTS ONLY, never wall-clock" directive. Used `valgrind --tool=callgrind` throughout (confirmed
available and functional this session — v3.22.0 — superseding the stale 2026-08-21 "valgrind is absent"
note). For the synthetic kernels: FIXED-WORK mode (`echo N | scrip --run k.sno`, the `bench-harness-
unmeasurable` mechanism landed today) at N=5,000 and N=50,000, reporting the **marginal Ir per iteration**
`(Ir(50k)-Ir(5k))/45000` — this cancels the one-time parse/compile/JIT constant exactly, unlike a single-N
reading (a first attempt at N=5,000 alone was dominated by compile overhead and produced meaningless
~1.00-1.03x "before/after" ratios across the board; the slope method fixed this). Added one local,
contained mitigation for a separately-flagged, unrelated harness defect: `ZKN = ZKN + 0` at the top of
each new kernel's `ZBODY`, coercing the FIXED-WORK path's string-typed `fixed_n` to numeric before the
inner-loop `LT(ZI,ZKN)` comparison — see `FINDING-2026-08-22-seat06-arith-loop-fusion-target-is-24-
percent-not-0-64-percent-and-fixed-work-mode-has-a-string-coercion-defect.md` for the shared-`harness.inc`
defect this sidesteps locally without touching the file every other kernel depends on.
For the realistic ladder (data-driven, `ZSRC=INPUT` slurps stdin before `harness.inc`'s own `fixed_n=
INPUT` gate ever runs, so FIXED-WORK mode is unreachable for this kernel shape — noted as its own
limitation, not chased further): native TIME-mode under callgrind, comparing runs where **`iters:`
matched exactly** (the only condition under which a raw `Ir` total is a fair comparison) and,
separately, `scripts/test_bench_snobol4_timed.sh` against the clean oracle for the cross-engine ratio.

## 2. ⭐⭐⭐ THE MECHANISM DECOMPOSITION — measured separately, not inferred

Marginal Ir/iteration, unmodified tree (RT_OPT=`-O0`):

| kernel | Ir/op | vs. d1 | mechanism isolated |
|---|---:|---:|---|
| `chain_read_d1` | 642.5 | 1.00x | 1 hop, integer leaf (baseline) |
| `chain_read_d2` | 1080.1 | 1.68x | 2 hops, integer leaf |
| `chain_read_d3` | 1521.0 | 2.37x | 3 hops, integer leaf |
| `value_type_tbl` | 650.1 | 1.01x | 1 hop, **table-valued** leaf |
| `chain_incr_d1` | 1088.8 | 1.69x | 1-hop read+write |
| `chain_incr_d2` | 1965.4 | 3.06x | 2-hop read+write |
| `chain_incr_d3` | 2848.6 | 4.43x | 3-hop read+write |

**Reading this against the three named suspects:**
1. **Nested-table value boxing — EXONERATED as a per-access cost.** `value_type_tbl` (650.1) reads
   *the same* as `chain_read_d1` (642.5, within 1.2%, i.e. noise). A `DESCR_t` is a flat 16-byte tagged
   union (`descr.h`) — a TABLE reference costs exactly what an INTEGER costs to copy. The real (small,
   amortized) boxing cost is the ~2KB `memset` at `table_new()`, paid once per *distinct* new nested key,
   not per access — consistent with agent research into `src/runtime/aggregates.c`.
2. **Chained subscript re-lookup — the dominant, near-linear-additive cost.** d1→d2→d3 is 642→1080→1521,
   i.e. each added hop costs *close to* one more d1-unit (1.68x, 2.37x vs. a naive-additive prediction of
   2x, 3x) — NOT super-linear. **Root cause, confirmed by direct source read** (`src/templates/
   bb_subscript.cpp`, `src/runtime/pattern_match.c:c_rt_subscript_var`): every `[k]` compiles to exactly
   one call to `rt_subscript_var`; a 3-level chain is 3 fully independent calls wired by dataflow, zero
   cross-level sharing, and — this is the part that makes it expensive, not just repeated — **every call,
   hit or miss, read or write, mints a fresh 72-byte `VCELL_t` via the GC arena** to wrap the result as a
   NAMETRAP, which the very next hop immediately unwraps (`IS_VARREF_fn`+`rt_deref`) and discards. The
   asm port's own header at `rtx_icnsub.S:57-62` already names this "THE REAL DEFECT."
3. **IDENT() guard — a large, depth-independent, per-call dispatch tax**, not part of the chaining cost
   at all. Wall-clock (contention-noisy, but the effect size is far outside any documented noise floor,
   reproduced twice: 7.2M→2.6M ops/s and 7.5M→2.8M ops/s, both ≈2.7x): `IDENT()` is **not inlined** —
   `dop_direct_fp`'s compile-time direct-call fast path doesn't cover it, so every call installs a
   `setjmp`, computes a fresh djb2 hash of the literal string `"IDENT"`, and dispatches through a switch
   (`by_name_dispatch.c`) to reach `descr_identical` — an O(1) tag compare that itself costs nothing. The
   dispatch machinery around it is the tax, paid identically on every call regardless of hit/miss/depth.
   **This exact mechanism is independently found and FIXED, same session, by `ir-ident-differ-inline`
   (seat07) — see §5.**
4. **Read+write non-sharing, confirmed exactly:** incr/read ratio is 1.69x/1.82x/1.87x at d1/d2/d3 —
   consistently close to 2x at every depth (not decreasing with depth, which would indicate partial
   caching) — confirms the write side re-walks the FULL chain from scratch, sharing nothing with the read
   side, exactly as the "every call is independent" structural finding predicts.

**⇒ the 7x on real claws5 is not one super-linear defect. It is ~12 independent single-hop runtime calls
per token() invocation (1+2+3 hops across the three IDENT-guarded creation lines, +3+3 for the final
read-then-write increment) plus 4 IDENT dispatches, each paying a real but roughly CONSTANT per-call tax
that SPITBOL's implementation apparently doesn't scale the same way — op-count multiplication against a
per-op deficit, not a compounding one.**

## 3. ⭐⭐ THE CURE — completing a half-built optimization, found already scaffolded and inert

`src/lower/lower_snobol4.c` already marks intermediate subscript-chain hops `"container-only"`
(`sx_sub_container_only`, gated by an **already-existing** killswitch `SCRIP_SUB_AGG`, default ON) and
codegen (`bb_subscript.cpp`) already dispatches those hops to a dedicated runtime symbol,
`rt_subscript_var_container_only` — **but that function's entire body was `return
rt_subscript_var(base, idx);`**, a complete no-op alias paying the full VCELL-allocating cost anyway.
Someone had already built the wiring (IR marking, codegen dispatch, dedicated symbol, env-var killswitch)
for exactly this optimization and never finished the runtime half.

**⛔ A real correctness trap found while scoping the fix, NOT the one I expected:** `"container-only"` is
applied to *every* hop in `sx_subscript_lv` (the assignment-target/lvalue builder), **including the truly
final hop**, whose IR node is fed directly into `IR_ASSIGN_VAR` as the actual store target
(`lower_snobol4.c:513-520` etc.) — not merely as a base for one more subscript. A naive "hit + stored-
value-is-a-container ⇒ return the value directly" fast path is **safe for a read** (the consumer is
always `IR_DEREF`, which is transparent to either representation) but **unsafe for that lvalue chain's own
final hop**: if the slot being overwritten currently holds a table/array (e.g. re-assigning a key that
previously held a nested table), returning the raw value instead of a `NAMETRAP`-wrapped cell would hand
the store logic something it cannot write through — silent corruption on a real, if narrower, class of
programs. Fixed the marking, not just the runtime: `sx_subscript_lv`'s loop now calls
`sx_sub_container_only` only for `k < nidx - 1` (excludes the true final hop, reverting it to the
always-correct plain path unconditionally); the read-chain loop (`TT_IDX`) is untouched, because its
result always funnels through `IR_DEREF` regardless of which hop produced it.

**The fix (net 13 lines, 2 files):**
```c
/* src/lower/lower_snobol4.c, sx_subscript_lv's loop */
if (k < nidx - 1) sx_sub_container_only(sub);
```
```c
/* src/runtime/pattern_match.c */
DESCR_t rt_subscript_var_container_only(DESCR_t base, DESCR_t idx) {
    extern int kwb_error(int code, const char *msg);
    DESCR_t b = base;
    if (IS_VARREF_fn(b)) b = rt_deref(b);
    if (b.v != DT_A && b.v != DT_T) { kwb_error(235, "subscripted operand is not table or array"); return FAILDESCR; }
    if (b.v == DT_T) {
        TBBLK_t *tb = b.tbl; if (!tb) return FAILDESCR;
        char kb[64]; const char *ks = tbl_key_str(idx, kb, sizeof kb);
        TBPAIR_t *e = table_find_pair(tb, ks);
        if (e && (e->val.v == DT_T || e->val.v == DT_A)) return e->val;
        VCELL_t *vc = rt_agg_alloc(0, sizeof(VCELL_t));
        if (e) { vc->cellp = &e->val; vc->tbl = tb; vc->key = 0; }
        else   { vc->cellp = 0; vc->tbl = tb; vc->key = rt_ws_strdup_c(ks); }
        vc->key_d = idx; vc->sv = FAILDESCR; vc->pos = 0; vc->len = 0;
        return NAMETRAP(vc);
    }
    return rt_subscript_var(base, idx);
}
```
Fast path fires only on: table base, key HIT, stored value already a container (`DT_T`/`DT_A`) — the exact
shape of an intermediate hop in a real nested-table chain. On a MISS or a non-container (e.g. INTEGER
leaf) hit, falls through to the ORIGINAL logic, reusing `tb`/`ks`/`e` already computed (no duplicate
lookup — **a first version of this fix called `rt_subscript_var(base,idx)` as the fallback, which redoes
`table_find_pair` from scratch; measured that version net SLOWER on integer-leaf cases (chain_read_d1 got
47% worse) before catching and fixing it — left in as a cautionary note for the next person who reaches
for this shape**). Arrays (`DT_A`) are completely untouched — always fall through unconditionally.
**Killswitch: the already-existing `SCRIP_SUB_AGG=0`** disables the container-only marking entirely
(all hops revert to the plain, always-correct path) — no new global, no new env var, reused exactly as
found; verified this genuinely reproduces pre-fix costs (the no-op wrapper made "marked or not" behavior-
identical before this session, so `SCRIP_SUB_AGG=0` on the patched binary is bit-for-bit the same
work as the unpatched binary, used directly as the "before" arm of every measurement in §2 and below).

## 4. RESULTS — fix verified correct, then measured

**Correctness, both modes, this session's final merged tree:** all 10 new probes + `claws5_l1`/`claws5_l2`
+ real `demo/claws5.sno` oracle-identical in m3 (`--run`) and m4 (`--compile`→`gcc -no-pie`→run), reconfirmed
after every rebuild (3 pristine rebuilds total: initial fix, bug-fixed fast path, post-merge with
seat07's concurrent landing). SNOBOL4 smoke 7/7 both modes at every step. Icon smoke 14/14 both modes
(sanity check — `"container-only"` is SNOBOL4-lowering-only, grep-confirmed no other frontend uses it).

**Fix's own isolated effect (marginal Ir/iter, `SCRIP_SUB_AGG=0` vs. default, same binary):**

| kernel | before | after | ratio | why |
|---|---:|---:|---:|---|
| `chain_read_d1` | 642.5 | 644.4 | 1.003 | no intermediate hop — correctly a no-op |
| `chain_read_d2` | 1080.1 | 990.1 | **0.917** | 1 intermediate hop fast-pathed |
| `chain_read_d3` | 1521.0 | 1340.0 | **0.881** | 2 intermediate hops fast-pathed |
| `chain_incr_d1` | 1088.8 | 1091.8 | 1.003 | single hop each side, both excluded/non-container — no-op |
| `chain_incr_d2` | 1965.4 | 1783.5 | **0.907** | 1 intermediate hop, both read+write sides |
| `chain_incr_d3` | 2848.6 | 2478.5 | **0.870** | 2 intermediate hops, both read+write sides |
| `value_type_tbl` | 650.1 | 557.1 | **0.857** | direct hit, single hop, read context |

Monotonic, mechanism-precise, and — critically — **exactly zero effect on the depth-1 rows**, which is
what most ordinary (non-nested) table usage in the corpus looks like: this fix's blast radius is narrow
by construction, not just by testing.

**Whole-program, real `claws5.sno` + real `claws5.dat`, callgrind, `iters:` held exactly equal (1=1) so
the raw Ir totals are a fair comparison (the only pair in this session's whole-program attempts where that
held — TIME-mode's calibrate/measure batching is otherwise not iteration-count-stable across separate
callgrind invocations under this session's contention, and a later 3-way before/identonly/both attempt was
discarded for exactly that reason, noted in §6):**

| | Ir | 
|---|---:|
| before (`SCRIP_SUB_AGG=0`) | 396,021,624 |
| after (this fix) | 375,702,112 |
| **Δ** | **−5.13%** |

`claws5_l2` (2-level rung, same iters-matched method): 283,493,080 → 274,400,515 (**−3.2%**). `claws5_l1`
(1-level, control): 257,130,772 → 257,144,862 (**+0.005%**, noise) — the control lands exactly where it
should, at zero.

**Cross-engine ratio, clean oracle, wall-clock (heavy caveat — see below):** best available reading this
session, isolated single-kernel `BENCH_DIR`, REPS=20, lowest-contamination rep (nivcsw=4): **m3:sbl =
0.20x** (sbl 101/s, m3 20/s). Multiple other readings across this session, same kernel, same clean oracle,
ranged **0.09x-0.20x** depending on fleet contention at measurement time (load average 10-14 throughout,
nivcsw contamination flagged on most reps). **The wall-clock cross-engine ratio is NOT this FINDING's
citable number — the Ir evidence above is.** The stale "0.17x" this row's own brief quoted is void (dirty
oracle, §0); a trustworthy, precise m3:sbl figure needs re-measurement on a quiet box, flagged below as a
loose end rather than papered over with a cherry-picked reading.

## 5. ⭐ CROSS-REFERENCE — `ir-ident-differ-inline` (seat07) independently fixes the OTHER mechanism this
row identified, landed and merged the same session

Mid-session, `.github` pull surfaced `FINDING-2026-08-22-seat07-ir-ident-differ-inline.md`: IDENT/DIFFER
now compile to a direct inline call to `descr_identical` (killswitch `SCRIP_IDENT_INLINE`, default on),
replacing the by-name dispatch chain §2 item 3 measured above. Seat07's own isolated micro-benchmark:
**1.68x-2.37x FASTER** with the fix vs. **0.35x slower** without, on a loop body with one IDENT call added
— independently corroborates this row's ~2.7x dispatch-overhead reading via a completely different
instrument and kernel. Pulled and rebased SCRIP mid-session (auto-merged cleanly, zero conflicts — the two
changes touch disjoint code: this row's fix is `sx_subscript_lv`/`rt_subscript_var_container_only`,
seat07's is `sx_ident_differ`/`bb_ident.cpp`/`bb_differ.cpp`); reconfirmed all 10 probes + real claws5
oracle-identical in both modes and the full corpus regression clean (below) on the MERGED tree, so the two
fixes are verified to coexist correctly. **Did not attempt a precise combined-effect whole-program number**
— TIME-mode's `iters:` count varied between the pre-merge and post-merge callgrind runs (3 vs. 2 vs. 1
across attempts, sensitive to fleet load at each specific invocation), which invalidates a raw-Ir
comparison the same way the single-N synthetic attempt did in §1; the two fixes touch structurally
disjoint call sites (table-subscript hops vs. IDENT dispatch) so their savings are expected to compose,
not interact, but that composition is not independently measured here — noted as a gap, not asserted.

## 6. CORPUS NO WORSE

`test_corpus_snobol4.sh`, pristine rebuild, run twice (once immediately after this row's own fix, once
again after merging seat07's concurrent landing): **m3 PASS=357 FAIL=2, m4 PASS=355 FAIL=2 SKIP=2 both
times** — fail-set identical **by name** to the pre-existing, independently-documented baseline
(`160_pat_alt_inner_gen_resume`, `demo_treebank` FAIL; `132_pat_fence_eps_recur_shallow`, `demo_porter`
SKIP — same four names seat07's own FINDING cites as its baseline). Icon smoke 14/14 both modes
(cross-language sanity — confirmed unaffected, as the mechanism this row touches is SNOBOL4-lowering-only).
Prolog smoke shows 2 pre-existing FAILs (`clause`, `recursion`) — structurally impossible for this row to
have caused (different frontend, different lowering file, `sx_subscript_lv`/`"container-only"` never
referenced outside `lower_snobol4.c`); not chased further, consistent with `GOAL-PROLOG-100.md`'s own
documented in-progress state.

**⛔ Separately, unrelated to this row, flagged not chased:** `test_gate_emit_no_lang.sh`-adjacent
territory surfaced (via concurrent `.github` pulls) an independent, already-reported regression —
`FINDING-2026-08-22-seat04-perf-board-rebaseline-...`/`FINDING-2026-08-22-seat06-beauty-m3-self-host-
currently-diffs-from-oracle-not-fixed-point.md` — beauty.sno's self-host fixed point breaks at commit
`62017f8a` (`descr-stamp-fields`), independently bisected and reported to HQ by two other seats before this
session started. Confirmed (via the SAME method seat07 used: killswitch on/off) this row's own change is
irrelevant to it — `SCRIP_SUB_AGG` toggling changes nothing about the beauty failure, and `git log` shows
`62017f8a` predates every commit this row touched. Not this row's regression, not this row's fix.

## 7. NOT DONE / FOLLOW-ONS — the remaining structural cost, named and scoped for whoever picks it up

The fast path above only fires on (table, hit, container-valued) — the majority of claws5's own per-token
cost is still paid in full, because:
- **The true final hop of a WRITE chain never gets a fast path** (by design, §3's correctness trap) — no
  proposal here; a safe version would need the read/write IR-marking distinction to go one level deeper
  (a THIRD runtime entry point specifically for "final hop of a plain VALUE READ," which the write path
  would never route through) rather than reusing "container-only" for it.
- **A MISS still pays the full VCELL-allocating path** (inherent to the auto-vivify placeholder semantics
  — `rtx_icnsub.S`'s own comment: "an eager bucket insert here would... be the WRONG SEMANTICS"). Not
  addressed; would need its own investigation into whether the placeholder itself can be made cheaper.
- **The genuinely dominant remaining cost is `rt_subscript_var`'s own per-call VCELL allocation on
  everything my fast path doesn't catch** — i.e. every non-container-valued hit and every miss, which is
  most of a real workload's table traffic (claws5's own leaf level is always an INTEGER, never a table).
  This is exactly the defect `rtx_icnsub.S:57-62`'s own comment already names ("THE REAL DEFECT... a
  72-byte VCELL_t purely to NAME a cell that's immediately dereffed and discarded") — fixing it for the
  general READ case (not just the container-valued case this row's fix covers) is the single biggest
  remaining lever, but touches the subscript runtime's hot path unconditionally (every table AND array
  access, not just nested-table chains) and needs the same read/write-context distinction worked out
  carefully — proposing as its own row, e.g. `subscript-read-no-vcell`, scoped to: thread a compile-time
  rvalue/lvalue distinction through `IR_SUBSCRIPT` (not just "container-only" but "read-only, any leaf
  type"), verified against the FULL corpus in both modes given the blast radius.
- **The 3x-redundant-hash-walk on a fresh key** (agent research into `pattern_match.c`: the IDENT-argument
  read, the LHS-of-assignment re-evaluation of the same subscript text, and the store's own lookup are
  three independent walks for one logical "create if missing") — claws5.dat has substantial lexical
  diversity (2,161+ distinct word/tag surface forms over 6,469 tokens by a crude regex count), so this is
  not a rare, fully-amortized cost on this workload. A codegen-level CSE recognizing `x = IDENT(x) v` where
  `x` is textually identical on both sides could collapse this to one walk — proposing as
  `ident-guard-subscript-cse`, scoped narrowly to that one statement shape.
- **`TABLE_BUCKETS` is hard-pinned at 256 with no growth path** (`_Static_assert` in `rtx_init.c`) — not a
  factor for claws5's modest table sizes, flagged as a latent risk for any workload with much larger
  tables, not investigated further here.
- **A precise, quiet-box m3:sbl wall-clock ratio for real claws5** (§4) — this session's fleet contention
  (load average 10-14 throughout) made every wall-clock reading noisy well beyond the effect size being
  measured; re-run `BENCH_DIR=<isolated single-kernel dir> REPS>=20 bash scripts/test_bench_snobol4_timed.sh`
  on a quiet box for a citable number.

## WATERMARK

SCRIP: 2 files changed (`src/lower/lower_snobol4.c` +1/-1, `src/runtime/pattern_match.c` +10/-1), rebased
onto and verified compatible with seat07's concurrent `ir-ident-differ-inline` landing. corpus: 12 new
files under `corpus/probe/table_nested/` (10 `.sno`+`.ref` pairs, 2 `.dat` symlinks), zero existing files
touched. `.github`: this FINDING + `GOAL-SNOBOL4-100.md` cursor.
