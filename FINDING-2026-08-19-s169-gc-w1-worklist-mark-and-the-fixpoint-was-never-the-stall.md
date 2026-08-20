# FINDING s169 (seat2) — GC-W1: the fixpoint is gone, and it was never the stall

**Queue row 4 `gc-w1`** — *GOAL-SNOBOL4-100.md s167 D-22, rung GC-W1 ONLY. Worklist mark replaces the
fixpoint.* DONE-WHEN: killswitch rung landed · `gc_stress`+corpus green both modes · `[ZGC]` walk
collapse shown · `.s` blast 0. **All four met.** SCRIP `b7e10d3c`.

---

## 1. What was wrong, and what replaced it

s167 read the defect from source: MARK's completion was a whole-arena **fixpoint**
(`gc_collect_ex`) — `while (changed) for (i = 0; i < g_gc_nblk; i++)` — every round a full pass over
**every title in the arena** asking "marked-and-unscanned?", with the round count growing as the
reference chain is discovered depth by depth. Only five block types ever need scanning
(`HB_WS`, `HB_PLJ`, `HB_AGGV`, `HB_AGGP`, `HB_AGGT`); the pass dragged all of them past the test to
find the few.

It is now a **mark stack seeded by the root passes**: a block pushes the first time it is marked,
`scanned[]` and `changed` are deleted, and mark is O(live edges).

**The worklist is INTRUSIVE and costs zero storage.** The link rides `h->fwd`:

- the index pass at the top of every collect already sets `h->fwd = 0` for every block, and
- nothing reads `fwd` until the forwarding pass, which runs *after* mark,

so `fwd` is provably dead across the whole mark phase. Push is `h->fwd = head; head = h`; pop is
`head = h->fwd; h->fwd = 0`. **Draining therefore restores `fwd == 0` everywhere**, which is exactly
the state ADJUST expects — the data structure cleans up after itself with no reset pass.

Dedup is free: the push is guarded by `!(old & HBF_MARK)`, so a block enters the stack on the
transition into "marked" and can never be queued twice. No `queued` bit was needed.

All six mark sites — `rt_gc_pin_ptr`, `gc_cons_scan_t` (ws-only arm), `rt_gc_visit_raw`,
`gc_mark_agg`, and `rt_gc_visit_descr` at DT_S and at the DT_N fallthrough — now route through one
choke point, `gc_mark_blk(h, addf)`, which sets the bit and pushes only scannable types.

## 2. ⛔ The FACT RULE: this rung REMOVES a global

The obvious implementation wants a stack buffer, a capacity, and a top — three new file-scope
globals, which the NO-NEW-GLOBALS rule forbids without an in-chat banner from Lon.

None were added, and one was retired. `g_gc_scanbuf` and `g_gc_scap` existed *only* to serve the
fixpoint's `scanned[]` and retire with it; a single head pointer replaces both. **Net −1 file-scope
global.** The intrusive link is per-block storage that already existed, and the killswitch arm
allocates its `scanned[]` locally per collect rather than holding a buffer alive. No banner ask was
needed, and the rule's intent — state rides registers, the stack, and existing structures — is met
rather than routed around.

## 3. ⭐ The measurement that re-prices the ladder

Killswitch: `SCRIP_GC_WORKLIST=0` restores the fixpoint verbatim (draining the pushed list first so
`fwd` is clean). Default ON. New `[ZGC-MARK]` telemetry under `SCRIP_ZETA_TELEM` prints
arm · titles-walked · blocks-scanned · rounds · nblk.

**Titles walked (the s167 cost model's own unit):**

| witness | fixpoint (FX) | worklist (WL) | collapse |
|---|---|---|---|
| `table_access`, one collect, default heap | **22,057,524** | **779** | **28,315×** |
| `203_gc_table_string_keys`, `STRESS=25`, 41 collects | 241 / collect | 17.1 / collect | 14.1× |

Collect counts are identical across arms (41 = 41), so the arms agree on cadence and only the mark
work differs.

**Wall clock, same binary, best-of-3, RT_OPT `-O0` (dev default), default heap:**

| benchmark | FX | WL | gain |
|---|---|---|---|
| `table_access` | 771 ms | **729 ms** | 5.5% |
| `table_churn` | 820 ms | **739 ms** | 9.9% |
| `array_sum` | 609 ms | **608 ms** | ~0 |

### ⛔ The honest read: GC-W1 does not close s154, and now we know why

**22 million skipped title visits buy about 40 ms.** Each visit the fixpoint repeated cost only a
flags test and a `continue` — a few nanoseconds against a cache-resident index — so the fixpoint was
**~5–10% of GC wall, not the bulk of it**. s167's divergence #1 was correctly identified and is now
correctly fixed, but the sequencing note that called GC-W1 *"the s154 defect's actual owner"* is not
borne out: the 835 ms stall's mass is elsewhere.

It is in the other two divergences, which this rung does not touch:

- **#2, the walk floor** — five *unconditional* O(all-blocks) passes per collect (count walk,
  flag-clear + index + pmap rebuild, forwarding, live-array). These are unaffected by how clever
  mark is, and they are now the **largest remaining lever → GC-W2**.
- **#3, universal pinning** — every survivor pinned, slide moves nothing, full compaction
  bookkeeping paid for a non-moving result → **GC-P0/P1**.

**Recommendation to HQ: re-cut any plan that expected GC-W1 to be the s154 fix, and promote GC-W2.**
This lands next to seat1's GC-R verdict of the same day (the budget knob cannot price the cadence
hypothesis, road blocked) — with cadence blocked and mark now cheap, **the walk floor carries the
weight**, and it is the one road of the three with no known blocker in front of it.

## 4. Gates

Pristine tree (`make pristine`, SCRIP `25d8970c`) plus this change:

- **`test_gc_stress_suite.sh` — ALL GREEN.** 4 stress rungs × 2 modes × 15 tests, including
  `SCRIP_GC_STRESS=1` (collect on every allocation) — the arm that exercises the worklist hardest.
- **Corpus both modes — 307/306 PASS, 10 FAIL, 0 DIVERGE.** The 10 reds are **identical
  program-for-program with `SCRIP_GC_WORKLIST=0`**, i.e. against the pre-change algorithm in the same
  binary, so they are pre-existing and not GC-W1's: `expr_eval`, `124_pat_regex_keyword_seal`,
  `128_pat_recursive_grammar_right_rec`, `140_pat_eval_double_fn_trick`,
  `141_pat_eval_double_fn_arbno`, `145_pat_left_assoc_via_arbno_fence`,
  `160_pat_alt_inner_gen_resume`, `175_pat_bal_generator_retry`, `1110_array_1d`,
  `216_indirect_goto_computed`.
- **Shared-runtime check** (`libscrip_rt.so` is common to every frontend): Icon smoke **14/14 both
  modes**; Prolog smoke 3/5, which equals the recorded s165 watermark and is arm-independent.
- **`.s` blast 0.** 484 crosscheck artifacts re-emitted **byte-identical**, no commit produced —
  runtime-`.so` only, as D-22 requires of every rung in this ladder.

⭐ **Method note worth keeping:** the killswitch is not only a rollback lever, it is a *control*. Every
"is this red mine?" question in this rung was answered by re-running the same binary with the
killswitch off, with no rebuild and no stash — which is why the 10 corpus reds and the Prolog 3/5
could be cleared as pre-existing in seconds rather than argued about. Ladders that mandate a
killswitch per rung should say this out loud: **the OFF arm is the cheapest baseline you will ever
have, because it is the same binary.**
