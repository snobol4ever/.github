# FINDING seat09 — the compiler's own 13.4G Ir, bucketed and named: emitter (59%) and ζ-storage layout (17%) dominate; two existing rows get fresh evidence, two gaps get proposed

**Session:** 2026-08-23 seat09, THE LOOP row `profile-the-compiler-1426x` (rank 0, resumed claim — a prior sitting started this same callgrind run and did not finish it; its `/tmp` output was already gone by this sitting, no state lost, re-run from scratch).
**Instrument:** `valgrind --tool=callgrind --dump-instr=yes --collect-jumps=yes --smc-check=all-non-file`. **RT_OPT=-O0** (default, `make pristine` immediately before the run — HQ-27). Mode 3 (`--run`, default). Ir only, never wall clock (callgrind counts are deterministic, per ARCH-PERF-TOOLING.md and the s250/s253 precedent).
**Workload:** `./scrip corpus/programs/snobol4/demo/beauty/beauty.sno < /dev/null` — **compile + init ALONE, nothing executes** (this is the row's whole point: the compiler itself has never been profiled in isolation; every prior perf FINDING profiled either emitted code or a full self-host run where runtime execution swamps compile cost).
**Receipts:** SCRIP HEAD `6e4951c5`, corpus HEAD `f34ce80a` (`beauty.sno` last touched `336f49d2`, the BEAUTY-CN fixed-point rewrite). `beauty.sno`: 41,492 bytes, md5 `006850eb4e1ff2d0f7afc1aac2671b65`. Beauty self-host fixed point independently reverified this session (`diff <(./scrip beauty.sno < beauty.sno) beauty.sno` → empty, exit 0) — confirms the regression seat04/seat06 chased on 2026-08-22 is fixed at current HEAD, third independent confirmation after seat15's.

## 1. The headline number

**Total Ir, compile+init only: 13,422,044,716.**

⛔ **This does NOT update the old "1,426x" ratio in this row's own brief — that ratio is retired, not recomputed.** The brief's `12,995,512,724 Ir vs SPITBOL 9,113,074 Ir = 1,426x` was measured against a *different, now-obsolete* `beauty.sno` (40,971 bytes, pre-BEAUTY-CN). The current file is a different program by content (41,492 bytes) even though it serves the same role. Worse: **no SPITBOL oracle on this box can run the current file at all** — `/home/resources/x64/bin/sbl -bf beauty.sno < /dev/null` dies at line 10, `ERROR 251 -- keyword operand is not name of defined keyword`, independently reproduced this session. This matches `reprofile-after-byname-bake`'s (seat15) finding verbatim: *"beauty.sno's BEAUTY-CN conversion means no SPITBOL oracle on this box can run it any more... the SCRIP-vs-SPITBOL beauty ratio is currently undefined, not just unmeasured."* Third confirmation of that gap (seat15, then me). **The SCRIP-side number above is real and MEASURED; the ratio against SPITBOL is UNDEFINED until GOAL-SCRIP-HQ.md D-12/D-13 (a BEAUTY-CN-capable oracle) lands. Do not compute or cite a ratio from this FINDING.**

## 2. Bucket ranking (self-Ir; 99.90% of total covered, 0.10% long tail honestly unitemized)

| self-Ir | % of total | bucket | source dirs |
|---|---|---|---|
| 7,933,333,571 | **59.11%** | **emitter** | `src/emitter/{emit.cpp,emit_str.cpp}` |
| 2,310,418,111 | **17.21%** | **contracts (ζ-storage layout + allocators)** | `src/contracts/zeta_storage.c` |
| 1,695,118,675 | **12.63%** | **libc/system** | glibc: strcmp, msort, memcpy, etc. |
| 618,824,100 | **4.61%** | **templates** | `src/templates/x86_asm.h` + `bb_*.cpp` |
| 485,940,440 | **3.62%** | **lower** | `src/lower/lower_common.c` (mostly one function) |
| 180,128,698 | 1.34% | libstdc++ (std::string/STL internals) | inlined STL, mostly called *from* templates/emitter |
| 78,565,295 | 0.59% | **optimizer_run** | `src/optimizer/{gva_collect.c,ir_index.h,...}` |
| 61,313,486 | 0.46% | runtime (rt/core/builtins) | `src/runtime/name_binding.c:is_global` etc. |
| 27,161,718 | 0.20% | **parser** | `src/parser/snobol4/{snobol4.tab.c,snobol4.lex.c}` |
| 14,883,673 | 0.11% | **machine/slab** (JIT-executed anon blob) | the tiny bit of beauty's own compiled code that runs before hitting EOF on `/dev/null` and exiting |
| 3,001,046 | 0.02% | driver | `src/driver/*` |

**The gap nobody expected: parser (0.20%) and optimizer_run (0.59%) are rounding errors. `machine/slab` — actual execution of the JIT-compiled program — is 0.11%, confirming the `/dev/null` isolation worked as intended: essentially nothing of beauty *runs*.** The entire 13.4G Ir is compilation, and compilation is emitter + ζ-storage-layout + the libc calls those two issue, full stop. This directly answers the brief's own question ("is compile now the #1 bucket, now that by-name-bake removed the runtime dispatch cost") — yes, overwhelmingly, and not close.

## 3. Top 15 functions by self-Ir, with call counts (raw `cg.out` parsed for `calls=` edges; self-Ir cross-checked against `callgrind_annotate`'s flat table)

| self-Ir | %tot | calls | self-Ir/call | bucket | function |
|---|---|---|---|---|---|
| 3,410,501,922 | 25.41% | 468 | 7,287,397 | emitter | `emit.cpp:codegen_flat_chain_body` |
| 1,609,614,746 | 11.99% | 468 | 3,439,348 | emitter | `emit.cpp:zd_plan` |
| 1,063,462,569 | 7.92% | 9,330 | 113,983 | contracts | `zeta_storage.c:zls_node_bytes` |
| 972,294,373 | 7.24% | 44,829,486 | 22 | libc | `__strcmp_avx2` |
| 645,316,674 | 4.81% | 468 | 1,378,882 | contracts | `zeta_storage.c:zls_mark_value_refs` |
| 574,170,354 | 4.28% | 286 | 2,007,589 | emitter | `emit.cpp:cap_in_repeat_body` |
| 524,029,142 | 3.90% | 16,855 | 31,090 | emitter | `emit.cpp:bb_slot_get` |
| 473,182,476 | 3.53% | 1,222 | 387,220 | emitter | `emit.cpp:emit_label_intern` |
| 438,643,357 | 3.27% | 15,125,633 | 29 | contracts | `zeta_storage.c:zx_cmp` |
| 415,978,433 | 3.10% | 34,532 | 12,046 | lower | `lower_common.c:bb_src_of` |
| 319,315,404 | 2.38% | 2,356,965 | 135 | libc | `msort_with_tmp.part.0` (glibc qsort) |
| 300,892,002 | 2.24% | 2,167 | 138,852 | emitter | `emit.cpp:frame_need_of` (2nd cost-center) |
| 255,801,603 | 1.91% | 1,041 | 245,727 | emitter | `emit.cpp:emit_label_lookup_offset` |
| 226,704,715 | 1.69% | 29,129 | 7,783 | templates | `x86_asm.h:bb_emit_x86(std::string const&)` |
| 173,581,338 | 1.29% | 1,922 | 90,313 | emitter | `emit.cpp:alt_arm_member` |

**Call counts are from a direct parse of `cg.out`'s `calls=` edges (script kept, not checked in — scratch), cross-validated three ways: `codegen_flat_chain_body` 468×10,966,180,008 incl-Ir matches the `callgrind_annotate --auto` source view's own `=> ... (468x)` annotation exactly; leaf functions' (`zx_cmp`, `__strcmp_avx2`, `bb_src_of`) inclusive-Ir matches their self-Ir table entry to the instruction (confirms they call nothing further); `qsort(zx, zx_n, sizeof(zls_entry_t*), zx_cmp)` at `zeta_storage.c:492` confirmed by direct source read, explaining `zx_cmp`'s 15.1M-call count as a sort comparator, not 15.1M independent lookups.**

⛔ **Inclusive-Ir is unreliable for the recursive entries (`codegen_flat_chain_body`, `zd_plan`, `frame_need_of`) — same caveat the original HQ FINDING already named ("deep recursive cycles... figures up to 98,938% of total").** The `self-Ir/call` column above is safe regardless of recursion (self-cost is never double-counted); the table deliberately reports that, not inclusive/call.

## 4. What each bucket actually is, and the two shapes worth naming

**Shape A — quadratic/superlinear over the whole graph, no string compare involved.** `codegen_flat_chain_body` + `zd_plan` (37.4% combined) are called exactly 468 times each — once per "chain" — and `compiler-quadratic-residue`'s own brief already names both as two of its three remaining sites (*"the floater double-loop over `g_emit_cfg->n` inside `codegen_flat_chain_body`"* and `zd_plan` directly), alongside `emit.cpp:flat_beta_used_scan` (not in my top 15, below threshold individually — worth checking directly against this row, not re-derived here). **This FINDING is exactly the re-profile that row's own FIRST STEP asks for**, now done in isolation (no runtime noise) rather than on the row's original N=400 synthetic. See §6.

**Shape B — linear scan / membership test that should be O(1).** `emit_label_intern` (387,220 Ir/call, only 1,222 calls) and `emit_label_lookup_offset` (245,727 Ir/call, only 1,041 calls) are the *exact* pathology the now-fixed `bb_ab_slot_for` was caught by (FINDING-2026-08-22-hq, item #4, "label-pool linear scans... same pathology as #1, same cure") — **and it is still there**: 729M Ir combined (5.43% of this run's total), matching that old FINDING's 5.4%-of-total figure for the same two functions almost to the decimal, even though the two runs have very different denominators (this run is compile-only; that one was compile+init+full-execute) — a strong cross-validation that the mechanism, not the workload, drives this cost. `bb_slot_get` (31,090 Ir/call × 16,855 calls) and `bb_src_of` (12,046 Ir/call × 34,532 calls, this row already tracked under `name-lookup-strcmp`, see §6) have the same *shape* (moderate call count × suspiciously high per-call cost for what should be a cheap accessor) but are not confirmed as scans — flagging the shape, not the diagnosis.

**Shape C — a large sort with an unexplained N.** `zeta_storage.c:492`: `qsort(zx, zx_n, sizeof(zls_entry_t*), zx_cmp)`. 15,125,633 comparator calls implies (`n·log₂n`) **zx_n on the order of 700,000–800,000 entries** for a 41KB source file — two orders of magnitude more than the source's own line/token count suggests it should need. Not root-caused here (out of this row's scope, "row factory, do not stop to optimize") — flagged as the single most concrete open question in the whole profile: **is `zx_n` proportional to program size, or is something appending duplicates / not deduplicating before the sort?** `zls_build` itself (the driver of `zls_node_bytes`/`zls_mark_value_refs`/the qsort) has only 1,876 Ir of self-cost and is called a handful of times — it is a thin driver over genuinely large collections, not a hot loop itself.

**Shape D — codegen is string-based.** `templates` (4.61%) is dominated by `x86_asm.h:bb_emit_x86(std::string const&)`, `x86_parse`, `x86_core_[abi:cxx11]`, `x86_port_hook`, `x86_rnum` — all of which build or parse `std::string` representations of x86 mnemonics/operands. This is very likely why `libstdc++ (std::string/STL internals)` shows up as its own 1.34%/180M-Ir bucket (basic_string `operator+=`, `_M_append`, `_M_mutate`, ctor/dtor churn) almost entirely reachable *from* templates/emitter call sites, not from anywhere else in the compiler. Not one of the six buckets the brief named, but real and directly caused by bucket D's own encoding strategy — folding it into "templates" for the >2% threshold below.

## 5. Row disposition — existing rows get evidence, two gaps get proposed (not minted — see §7)

Per §7 of PROTOCOL.md, minting new QUEUE.tsv rows is the HQ MINT step, not a seat's; seat04's own `perf-board-rebaseline` FINDING set the precedent of naming candidate rows for HQ rather than self-minting (*"Suggest minting `fixed-work-zk-string-coercion` as its own row"*, never created directly). Following that precedent:

| bucket | % | existing row? | disposition |
|---|---|---|---|
| emitter | 59.11% | **YES — `compiler-quadratic-residue`** | Evidence appended to that row's LEDGER (see below). Not a new row. |
| contracts (ζ-storage) | 17.21% | none found | **NEW candidate proposed**, see §7. |
| libc/system | 12.63% | **YES — `name-lookup-strcmp`** (covers the `__strcmp_avx2`/`bb_src_of` majority of this bucket) | Evidence appended to that row's LEDGER. `msort_with_tmp`'s share (2.38%) belongs with the new ζ-storage candidate instead (its comparator is `zx_cmp`, not a name lookup). |
| templates | 4.61% | none found (`rationale-x86-asm-h` is a COMMENT-recovery row, unrelated to perf — checked, confirmed out of scope) | **NEW candidate proposed**, see §7. |
| lower | 3.62% | covered by `name-lookup-strcmp` (85.6% of this bucket is `bb_src_of`, named in that row's own brief text) | No new row. |

## 6. Fresh evidence added to `compiler-quadratic-residue` and `name-lookup-strcmp`

`compiler-quadratic-residue`'s FIRST STEP literally asks: *"re-profile before assuming the s251 ranking still holds... confirm the three sites are still the top compile-side costs."* Answer, isolated and precise for the first time: **yes — `codegen_flat_chain_body` (25.41%) and `zd_plan` (11.99%) are #1 and #2 of the ENTIRE compile-only profile, 37.4% combined**, up from that row's own qualitative "still climbing 2.36→2.58→2.89→3.23" growth-ratio evidence. `flat_beta_used_scan` did not surface in my top 15 — worth a direct name-check by whoever holds that row, not re-derived here.

`name-lookup-strcmp`'s own DONE-WHEN is *"`__strcmp_avx2` falls out of the compile-side top ten."* Answer: **not done — `__strcmp_avx2` is #4 in this isolated compile-only top ten at 7.24% (44,829,486 calls), and `bb_src_of` is #10 at 3.10%.** This is a REAL workload (beauty.sno), not that row's N=400 synthetic — stronger evidence, same verdict (open).

Both LEDGER entries appended verbatim to those two task files this session, citing this FINDING.

## 7. Two new candidate rows proposed for HQ to mint (not minted by this seat — see §5's reasoning)

**Candidate A — `zeta-storage-sort-and-node-bytes-cost`.** Target: `src/contracts/zeta_storage.c` — `zls_node_bytes` (113,983 Ir/call × 9,330 calls, 7.92%), `zls_mark_value_refs` (1,378,882 Ir/call × 468 calls, 4.81%), `zx_cmp`+`qsort` (15.1M comparator calls, 3.27%+2.38% libc). Combined 17.21%+2.38% = **19.6% of total compile-only Ir**, the single largest bucket with no current owner. First step: confirm whether `zx_n` (§4 Shape C) is genuinely proportional to program size or a dedup/accumulation defect — that answer alone could reclassify a third of this bucket. Draft DONE-WHEN (HQ to refine): a FINDING records `zx_n`'s relationship to source size on 2+ programs of different sizes, and either explains the ~800K-entry count as correct or files the defect it reveals.

**Candidate B — `x86-asm-h-string-based-encoding-cost`.** Target: `src/templates/x86_asm.h`'s `std::string`-based instruction builders (`bb_emit_x86`, `x86_parse`, `x86_core_[abi:cxx11]`, `x86_port_hook`, `x86_rnum`, ...) plus the libstdc++ bucket they drive (4.61%+1.34% = **5.95% combined**). First step: confirm the libstdc++ std::string calls are in fact reachable only from these encoders (not independently caused elsewhere) via one caller-tree check, then assess whether a fixed-size stack buffer / small-string-optimization-friendly builder removes the heap churn without touching the `x86(...)` encoder contract (RULES.md TEMPLATE-ONLY EMISSION still applies — this is an *internal representation* change inside the encoder, not a new emission path). Draft DONE-WHEN (HQ to refine): the libstdc++ bucket's Ir share on this same workload drops, beauty fixed point holds, corpus holds at standing reds.

## 8. Items for HQ (hq_P — this is a PERFORMANCE row, doorbell sent)

1. Mint Candidates A and B above if the ranking merits it (§7) — both currently un-owned, both individually larger than several existing rank-1 rows.
2. `compiler-quadratic-residue` and `name-lookup-strcmp` both got fresh, precise, isolated-compile evidence this session (§6) — still open, still valid, now with real-workload numbers instead of synthetic/full-run ones.
3. **The SCRIP-vs-SPITBOL ratio for beauty is UNDEFINED, not just unmeasured** (§1) — third session to hit this (seat15, then this one). `GOAL-SCRIP-HQ.md` D-12/D-13 (BEAUTY-CN-capable oracle) blocks every future beauty-workload ratio, not just this row's.
4. `zx_n`'s ~800K-entry magnitude (§4 Shape C) is the single most concrete unanswered question in this profile — small follow-up, potentially large payoff either way (confirms the sort is legitimate, or finds a second `bb_ab_slot_for`-class defect).
5. Zero code changes this session. FINDING carries the numbers; task files carry the receipts.
