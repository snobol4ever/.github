# FINDING — seat01: table_access ratio 0.6834x → 0.8643x (gap 1.463x → 1.157x) by closing two asm-fast-path gaps that never fired for SNOBOL4 tables

**Date:** 2026-08-24 · **Seat:** seat01 (FLEET-4) · **Row:** `perf-table-subscript-fastpath` (rank 1, dispatch-locked via direct `s4e_msg.sh claim` after releasing the row-factory row `perf-table-array-runtime` unworked — see that row's own LEDGER) · **Build:** `make pristine` EXIT=0 twice this session, RT_OPT=-O0 (default; no `-O2` anywhere, s262 FACT RULE) · **Instrument:** callgrind Ir at fixed work (`bench_wrap.sh --mode=iter`, N=2,000, mode-4 native binaries), matching FINDING-2026-08-24-seat04's exact methodology · **Oracle:** `sbl_clean_bin()` = `/home/resources/spitbol-bench-oracle/sbl -bf` (benchmark oracle, s255 two-oracle ruling).

Ratios follow the RULES.md FACT RULE (`reference/ours` = SPITBOL Ir / SCRIP Ir; above 1.00x SCRIP is faster, below 1.00x SCRIP is slower; no "faster"/"slower" words attached to a bare multiple).

## 0. Starting point (this row's own BRIEF, from seat04)

table_access N=2,000, post-algorithmic-fix (VCELL-alloc-on-read + key-stringification already cured in `perf-table-array-runtime`): SCRIP 1,051,874,749 Ir, SPITBOL 718,832,325 Ir, ratio **0.6834x**. The row's NEXT named two untried levers and said to measure each on its own: (1) thin `c_rt_subscript_var`/`c_rt_assign_var_body`'s C-side dispatch, (2) emit the subscript fast path as a `bb_*` template box. This FINDING is lever (1) — done via a different, better mechanism than "thinning" (see §1) — plus a from-scratch same-session SPITBOL re-measurement (718,846,861 Ir, 0.002% off seat04's number, confirming the workload/oracle are unchanged).

## 1. The actual defect: two existing asm fast paths never fire for a SNOBOL4 table, full stop

RULES.md's ASM-DIFF-FIRST order says read the emitted/hand-written asm before profiling deeper. `rt_subscript_var` (`src/runtime/rtx/rtx_icnsub.S`) and `rt_assign_var` (`src/runtime/rtx/rtx_icnvar.S`) are both `RTX_GATE`-fronted asm fast paths that fall back to C (`c_rt_subscript_var` / `c_rt_assign_var`) on any shape they don't recognize. Both already special-case `DT_A` (SNOBOL4 arrays arrive **already deref'd** — RTX-28's own comment: *"a SNOBOL4 array subscript arrives with the base ALREADY DEREF'D... never the DT_N varref shape"*). **Neither ever added the equivalent check for `DT_T`.** A SNOBOL4 table base arrives the same way arrays do — already deref'd, tag `DT_T`(0x18) — so it satisfies neither the `DT_A` arm nor the `DT_N`-VARREF gate every other table arm sits behind, and bails to C on cheap reject checks alone, every single time.

**Not inferred — measured**, gdb hit-count breakpoints (`break *(rt_subscript_var + N)`, `break c_rt_subscript_var`, run `table_access.sno` standalone, `commands`/`continue`/`info breakpoints`), before any fix, this tree:

| symbol | hits (of 10,500 T[I]=v writes across TABLE_ACCESS(1)+TABLE_ACCESS(20)) |
|---|---|
| `.Lsub_table_int` (RTX-29, the existing DT_N-gated integer-key table arm) | **0** |
| `c_rt_subscript_var` (C fallback) | **10,500** |
| `base.v` at C-entry (gdb, raw register read at the true entry, no prologue-skip) | **24 (DT_T) on 10,500/10,500** |

RTX-29 is not merely slow — it is provably unreachable for this traffic, because the gate above it (`cmp dil, DT_N`) already rejects `DT_T` before RTX-29's own code ever runs. Everything RTX-29 does or doesn't do correctly is moot for SNOBOL4; see §4 for why it still matters.

## 2. The fix: two new asm arms, following the exact precedent already in each file

**RTX-31 (`rtx_icnsub.S`, `rt_subscript_var`).** Added `cmp dil, DT_T` immediately after the existing `DT_A` check (same structural pattern: check tag, check subscript is `DT_I`, jump to a short direct-mint block). The mint is `c_rt_subscript_var`'s own DT_T arm, transcribed field-for-field — `vc->cellp=0; vc->tbl=tb; vc->key=0; vc->key_d=idx; vc->sv=FAILDESCR; vc->pos=0; vc->len=0`, ten instructions, one `rt_agg_alloc` call (already asm). `IS_VARREF_fn` requires `v.v==DT_N` (`descr.h:79`), so C's own `if (IS_VARREF_fn(base)) base=rt_deref(base)` is a no-op on this input — the new arm's behavior is byte-for-byte what C already does for this exact shape, not an approximation of it. `DT_S`-keyed tables are untouched (still bail, matching RTX-26's own already-standing s262 stand-down).

**RTX-NEW-ICNVAR (`rtx_icnvar.S`, `rt_assign_var`).** The write-back half of the same operation. `.Lav_nametrap` already fast-paths the `vc->cellp != 0` case (direct array/list element store); its own comment says table/tvsubs stay in C, and the file's header calls porting them *"volume, not speed"* — a judgment made for Icon's queens-board traffic (RTX-1-ICN's own stated motivation), not for SNOBOL4 tables newly made hot by RTX-31 above. Added a `vc->tbl != 0` check beside the existing `vc->cellp` check; on a table trap it calls `table_set_descr_d(tbl, key_d, val)` directly — the SAME C function `c_rt_assign_var_body` already calls, unchanged, no reimplementation of the hash/insert logic — and returns `val`. This is not "porting the insert," it is skipping the two extra C call layers and their redundant GC-safepoint/sxt-break/IS_NAMETRAP re-checks that `rt_assign_var`'s own asm entry already ran before ever reaching this arm. Register/stack discipline (5-arg SysV call, `val` parked across it via two matched pushes inside `RTX_CALL_ALIGN`/`RTX_CALL_UNALIGN`) mirrors `.Lav_sxt`'s existing pattern in the same file exactly.

Both changes: **zero new global variables** (registers + stack only, per the standing FACT RULE — no ask needed, none added). Both live entirely in `src/runtime/rtx/*.S` (hand-written runtime library asm), not `src/templates/*.cpp`/`x86_asm.h` — the TEMPLATE-REVAMP R1–R13 rules and the "x86(...)-only, no MEDIUM branch" emission-discipline rules govern *compiler-emitted* code for user programs and do not apply to this layer (confirmed by reading `ARCH-ICON.md` + `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` first, per CLAUDE.md's non-negotiable rule for BB/template work, before concluding this row's actual fix sits outside that rule's scope).

**Post-fix hit counts, same gdb methodology, all 10,500 writes:**

| symbol | before | after |
|---|---|---|
| `rt_subscript_var` asm entry | (10,500, but bails every time) | 10,500, **stays in asm every time** |
| `c_rt_subscript_var` | 10,500 | **0** |
| `rt_assign_var` asm entry | (10,500, but bails every time) | 10,500, **stays in asm every time** |
| `c_rt_assign_var` | 10,500 | **0** |
| `table_set_descr_d` (the one real insert call, unchanged) | 10,500 (via 2 extra C layers) | 10,500 (called directly) |

## 3. Measured result

| stage | SCRIP Ir (N=2,000) | SPITBOL Ir | ratio (SBL/SCRIP) |
|---|---|---|---|
| session start (seat04's post-algorithmic-fix baseline) | 1,051,874,749 | 718,832,325 (quoted) | 0.6834x |
| + RTX-31 only | 996,332,455 | — | 0.7215x |
| + RTX-31 + RTX-NEW-ICNVAR | **831,701,707** | 718,846,861 (fresh, this session) | **0.8643x** |

SPITBOL reproduced to 0.002% of seat04's quoted figure (718,846,861 vs 718,832,325) — same workload, same oracle, confirms the comparison is apples-to-apples per the FACT RULE (same instrument, same basis, same RT_OPT, same mode, same oracle+flags).

**SCRIP's own Ir dropped 1.265x this session** (1,051,874,749 → 831,701,707, a 20.9% reduction) from these two arms alone. The ratio improved from 0.6834x to 0.8643x, a **1.265x improvement in the ratio itself** (matching the SCRIP-side reduction, as expected — SPITBOL didn't move). **The gap is smaller but not closed**: SCRIP still takes **1.157x** the instructions SPITBOL does on this kernel (was 1.463x at session start, 2.773x at the original s256 measurement — three sessions, three real cuts: 2.773x → 1.463x → 1.157x). Standalone (un-wrapped, gate-style) table_access Ir also dropped, 15,267,937 → 12,986,443 — the pinned `TABLE_ACCESS_IR_WATERMARK` in `test_gate_instr_budget.sh` is re-pinned to this number below (§6). `array_sum` is untouched by design (both new arms gate on `dil==DT_T`; array_sum's kernel is `V[I]`, `dil==DT_A`, a different arm entirely) — confirmed: 10,912,565 → 10,921,313, a 0.08% noise-band move, gate reports `OK`, not `NOTE`.

## 4. ⛔ A latent hazard found and NOT fixed here, out of this row's scope — flagged and routed separately

Reading RTX-29 (`.Lsub_table_int`, the DT_N-gated integer-key table arm proven unreachable by SNOBOL4 in §1) turned up something that needs its own row, not a fix folded into this one. Its own header cites *"MEASURED s224: t[i]... It is ICON-NATIVE traffic"* — i.e., this exact arm **was** live, measured Icon traffic at least once. If it still is:

- It computes the bucket index as `hash & 0xFF` (a hardcoded single-byte mask), but the live `TBBLK_t.nbuck` is a **dynamic, per-table** power of two (`core.h:164`, "SIZED FROM THE PROGRAM'S OWN TABLE(n)"), masked as `hash & (nbuck-1)` by the real C insert/lookup. These agree only when `nbuck==256`.
- Worse: it treats `tb->buckets[h]` as a `TBPAIR_t*` chain node and reads `[r10+0]` as a `key` pointer (`.Lsub_chain`/`.Lsub_cmp`). But the live struct (`core.h:130-148`, s262) has `buckets` as `TBBUCK_t **` — pointers to `{unsigned len,cap; TBPAIR_t ent[];}` headers, **not chain nodes**, and `TBPAIR_t` itself has no `next` field any more (48 bytes: `key,key_descr,val,hkey`). Reading a bucket header's packed `{len,cap}` as a string pointer and dereferencing it is reading a near-guaranteed-unmapped low address — i.e., a plausible SIGSEGV under the right (or wrong) key/table-size combination, not a wrong-answer risk.
- `.Lsub_hit` (only reachable through this same arm) mints `cellp = &e->val` — exactly the pattern s262 banned outright *("we should never have in our code a place that depends on that pointer not moving")* — a second, independent reason this arm cannot be trusted as-is even where it doesn't crash.

Not chased further here (row-factory discipline: this row is `perf-table-subscript-fastpath`, not a correctness audit, and RTX-29 is proven dead for the one kernel this row measures). Routed: **`audit-rtx29-icon-table-int-chain-walk-post-s262`** (rank 0 — crash potential, historical evidence of real traffic, per `conform-defer-tab-span-crash`'s own rank-0 precedent for named-crash rows). Also messaged directly to hq_C given the severity class (§7).

## 5. Correctness verification (all this session, this tree, post-fix)

- `table_access.sno` / `array_sum.sno`: standalone output byte-matches `.ref` (both fixes together).
- `test_gate_instr_budget.sh`: **GATE OK** — roman (.ref match, within budget), beauty (**exact fixed point**, byte-identical self-hosted output — the strongest correctness signal available in this repo, on a large real Snocone program that exercises tables heavily), table_access (.ref match, NOTE improved), array_sum (.ref match, OK, unchanged).
- `test_smoke_icon.sh`: 14/14 PASS, both modes (m3 --run, m4 --compile) — the shared arms (`.Lav_nametrap` is Icon's own live path per RTX-1-ICN's header) show no regression on the smoke suite.
- `test_corpus_snobol4.sh`: 362/364 PASS both modes. The 2 reds (`TDump_driver`, `demo_treebank`) are **pre-existing and unrelated** — verified, not assumed: `TDump_driver` is a categorized DATA-type-accessor defect on record since `BUG_CATEGORIZATION_20260516.md` (over 3 months old, "BLOCKED for future session"); `demo_treebank` is `FINDING-2026-08-23-hq_C-treebank-is-really-the-comma-selection-expression.md`, dated the day *before* this session, root-caused to an unrelated `(A,B)` selection-expression lowering defect tracked under `vlist-expr-alternation` (assigned seat03). Zero new corpus regressions from this session's two changes.

## 6. Gate re-pin

`test_gate_instr_budget.sh`'s `TABLE_ACCESS_IR_WATERMARK` (15,267,937, pinned by seat04 same day) now reads `NOTE ... improved` at 12,986,443 — re-pinned to **12,986,443** in this commit so the gate protects the new, better baseline instead of sitting 15% loose. `ARRAY_SUM_IR_WATERMARK` unchanged (confirmed OK, not NOTE). roman/beauty watermarks untouched — already flagged loose by seat04's own session, outside this row's lane, not re-measured or re-pinned here.

## 7. Routed / open

- New row **`audit-rtx29-icon-table-int-chain-walk-post-s262`** (rank 0) — §4.
- `perf-table-subscript-fastpath` itself: **left OPEN**, not closed. Its own NEXT is explicit that the DONE-WHEN gate passing is "necessary, not sufficient" and closing requires either reaching the campaign's ratio>=2.00x target (not reached: 0.8643x) or an explicit HQ/Lon call that the residual is structurally irreducible without lever 2 (BB-template emission, `src/templates/bb_*.cpp` + `x86_asm.h`) — a materially larger, higher-blast-radius body of work (compiler-emitted-code path, full TEMPLATE-REVAMP rule set, BOTH-MEDIUM MANDATORY, no-new-globals banner-ask process) not attempted this session by design, not for lack of remaining budget. Messaged hq_C with this judgment call rather than deciding it unilaterally (see task LEDGER).
- Handoff note for whoever takes lever 2: `bb_idx_get.cpp`/`bb_idx_set.cpp` already contain an inline `DT_A`-fast/`DT_T`-falls-to-C shape (`bb_idx_set.cpp`'s own comment: *"Tables never took the fast path; arrays did"*) — same gap, different layer. **But they are dead code for SNOBOL4 today**: `IR_IDX_SET`/`IR_IDX_GET` are emitted only by `lower_snobol4.gz5-parked-41b53078.c` (a parked, non-live lowerer), not the live `lower_snobol4.c` — grepped, zero hits. Lever 2's real first step is finding what the live lowerer actually emits for `T[I]=v` (today: a plain runtime call into the very `rt_subscript_var`/`rt_assign_var` this FINDING just fast-pathed) before deciding whether to wire up the parked IR_IDX_SET path, extend it, or take a third approach.
