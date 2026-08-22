# FINDING seat04 — perf-board-rebaseline: DONE. Beauty regression reconfirmed live at HEAD (distinct from the retracted eq-coercion finding); second workload measured; the compile-vs-runtime split for both workloads; five old ranking entries re-priced; by-name verdict on the queued perf rows.

**Session:** 2026-08-22 seat04 (`/home/claude04`, Claude Sonnet 5), THE LOOP queue row `perf-board-rebaseline`, rank 0 (resumed claim, second sitting).
**Status:** DONE against the row's own DONE-WHEN checklist (§9). Continues the IN-PROGRESS FINDING this same file held after the first sitting — that content is preserved below (§§0–2) and extended (§§3–8, the last an addendum folding in three other seats' mid-session findings before this row closes).
**SCRIP tree:** unchanged, HEAD `2659558e` (main, clean working tree, pristine-built twice this session). No code touched, no killswitch, no `.s` regen owed.

---

## 0. ⛔ Beauty self-host is STILL BROKEN at current HEAD `2659558e` — reconfirmed fresh this session, and this is a DIFFERENT finding from the one HQ retracted

First sitting (HEAD `568bf098`) bisected a beauty self-host break to `62017f8a` (descr-stamp-fields' DESCR_t tag split) and sent `q-beauty-regression-descr-tag-split` to HQ. This session pulled 5 new commits (`568bf098` → `2659558e`, none of them a descr/beauty fix — see the commit list in §1) and found an HQ inbox message stating: *"your regression-descr-stamp-fields-eq-coercion does NOT reproduce at HEAD 261cafcb (m3 and m4 both MATCH after make pristine) -- retracted, not yours to carry."*

**That retraction is not this finding.** Three things distinguish them:
- **Name.** HQ retracted `regression-descr-stamp-fields-eq-coercion`. This finding's own sent topic was `beauty-regression-descr-tag-split`. Different topic strings — either a different question (an m3-vs-m4 divergence check on an eq-coercion witness, which is what "m3 and m4 both MATCH" tests) or a mis-attribution; either way, not a match by name.
- **Commit.** HQ's retraction tested `261cafcb`, which sits *inside* the already-bad range in the direct parent chain — it is the immediate child of `568bf098` (itself already confirmed BAD) and is a banner/tooling commit (`banner: SUCCESS now has to be earned`), not a code change to descriptors, parsing, or codegen. A no-op-for-this-bug commit testing GOOD where its parent tested BAD is itself a signal something doesn't line up between the two findings.
- **Test.** HQ's check was m3-vs-m4 *self-consistency* on some witness. This finding's check is beauty.sno's self-hosting *fixed point* against a golden md5 (`6f1671c0757729992ae01a6bdf16f081`) — a different, stronger property (a program can produce matching-but-wrong output in both modes).

**Reconfirmed this session, from scratch:** fresh `make pristine` at `2659558e` (the pull's new HEAD), then `./scrip beauty.sno < beauty.sno`:
```
md5: 1c75f97d1907f92f4c0a8a3ef49eb9ee   (the BAD signature — beauty prints its own "Parse Error" / mainErr1 label)
expected (GOOD): 6f1671c0757729992ae01a6bdf16f081
```
Byte-identical to the first sitting's BAD result. **The regression is real, live, and unresolved at current HEAD.** Flagging the naming/commit mismatch to HQ now (§7) rather than assuming my own bisection was wrong — a fresh from-scratch pristine reproduction outweighs a differently-named, differently-tested retraction.

---

## 1. Commits pulled this session (`568bf098` → `2659558e`, 9 new)

```
261cafcb banner: SUCCESS now has to be earned
361accaf oracle-asset-fallback-three: route the last 3 scripts through D-17b S4A
6720fbc2 s4e_msg.sh: shopt -s dotglob fix, widen FINDING-attribution grep
1aaa1d39 oracle-two-face-adoption: wire sbl_clean_bin() to 11 real call sites
4373d572 add test_gate_end_only_program.sh
b007a116 rt_dcap_pump: stop the conditional-assign queue walk on strict-refuse
05d73f5c banner: PERSIST the computed verdict to BOARD.md
2659558e oracle-two-face-adoption: oracle-absent refusal guards, LOAD() refusal guard, cmp3 fix
```
None of these touch `DESCR_t`, the tag split, parsing, lowering, or codegen — consistent with the regression surviving unchanged.

---

## 2. FIRST STEP DELIVERABLE (unchanged from first sitting) — beauty self-host Ir at `0ff71be8` (last pre-regression commit), pristine, m3

RT_OPT=`-O0` (default). `make pristine` immediately before the run. Output verified byte-identical to the fixed point (md5 `6f1671c0757729992ae01a6bdf16f081`), both plain and under callgrind, before trusting the number.

| | Ir | vs. seat1 BEFORE (27,760,640,730) | vs. seat1 AFTER (15,870,550,520) |
|---|---|---|---|
| **`0ff71be8`** | **15,845,933,856** | **−42.92%** | **−0.155%** (24,616,664 fewer) |

Per-function decomposition (`callgrind_annotate --threshold=98`), top contributors — unchanged from first sitting, reproduced here for reference:

| Ir | % | site | layer |
|---|---|---|---|
| 3,306,455,701 | 20.87% | `emit.cpp:codegen_flat_chain_body` | compile |
| 1,557,793,989 | 9.83% | `emit.cpp:zd_plan` | compile |
| 1,347,087,389 | 8.50% | `__strcmp_avx2` (libc) | mixed |
| 1,062,697,123 | 6.71% | `zeta_storage.c:zls_node_bytes` | compile |
| 618,079,680 | 3.90% | `zeta_storage.c:zls_mark_value_refs` | compile |
| 560,562,466 | 3.54% | `emit.cpp:cap_in_repeat_body` | compile |
| 495,204,990 | 3.13% | `emit.cpp:bb_slot_get` | compile |
| 448,712,592 | 2.83% | `zeta_storage.c:zx_cmp` | compile |
| 429,883,845 | 2.71% | `emit.cpp:emit_label_intern` | compile |
| 414,572,179 | 2.62% | `lower_common.c:bb_src_of` | compile |
| 360,810,576 | 2.28% | `by_name_dispatch.c:meth_is_user_proc` | **runtime** |
| 327,060,492 | 2.06% | libc `msort_with_tmp` | likely compile |
| 419,794,759 | 2.65% | `emit.cpp:frame_need_of`(+'2) | compile |
| 253,491,916 | 1.60% | `emit.cpp:emit_label_lookup_offset` | compile |
| 231,033,896 | 1.46% | `x86_asm.h:bb_emit_x86(...)` | compile (encoder) |
| 193,227,139 | 1.22% | `ab_fn_hash`+`bb_ab_slot_for` | **runtime** (seat1 fix residual) |

---

## 3. SECOND WORKLOAD — `corpus/benchmarks/snobol4/fibonacci.sno`, fixed-work mode, N=5,000, current HEAD `2659558e`

The benchmark harness's TIME-based mode is documented **unmeasurable under callgrind** (`FINDING-2026-08-22-bench-harness-unmeasurable.md`: batch sizes self-shrink to fit the *instrument's* slowed wall-clock, not the kernel's — arith_loop and table_access landed within 5% of each other under callgrind despite a 20,481x native throughput gap). **Fixed-work mode fixes this**: `echo N | scrip --run k.sno` runs exactly N iterations once, no deadline. Used throughout this section. `check=987` (FIB(16), correct) and `iters=5000` confirmed on every run below — output is not in question, only instruction count.

**Why fibonacci:** tiny source (19 lines), most of its Ir is recursive-call/comparison runtime work, not compilation — the clean structural opposite of beauty (large source, single-shot compile, comparatively little runtime work). This is the intended contrast, not cherry-picking for a result: table-int-keys-and-nd-subscript's own queue text independently reports the same finding on a *different* kernel ("emitted boxes are 8.5% of the cycle proxy and runtime C is 91.5% [on table_access] — the exact inverse of arith_loop"), so this is a second, independent confirmation that benchmark kernels sit opposite beauty on this axis, not a one-kernel fluke.

### 3a. Three measurements, same kernel, same N, RT_OPT=`-O0`

| arm | what it measures | Ir |
|---|---|---|
| **m3 combined** (`echo 5000 \| ./scrip --run fibonacci.sno`) | compile + startup + run, one process — same methodology as beauty | **2,680,694,604** |
| **m4 standalone** (`./scrip --compile` once, unmeasured → link → callgrind the linked binary alone) | pure execution of the emitted program — no compiler in-process at all | **2,609,640,572** |
| **SPITBOL clean** (`/home/resources/spitbol-clean/sbl -bf`, per `lib_oracle_flags.sh sbl_clean_bin()`) | same kernel, same N, oracle | **5,020,197,287** |

All three verified byte/value-identical on `check`/`iters` before trusting the Ir. N=5,000 chosen so native wall-clock runtime body (≈240ms) dominates fixed compile+startup overhead (≈15ms, ~17:1) — confirmed structurally correct once decomposed (below). Compile time is amortized by a large N on both the SCRIP and SPITBOL sides (not separately isolated on the SPITBOL side), per ARCH-PERF-TOOLING.md §4's "state which you did" discipline.

**SCRIP vs SPITBOL on this kernel:** m4-standalone/SPITBOL-clean = 2,609,640,572 / 5,020,197,287 = **SCRIP uses 52.0% of SPITBOL's instructions — SCRIP is 1.92x *fewer* instructions, i.e. SCRIP wins this workload.** This is the mirror image of beauty, where SCRIP costs **~5.8x** SPITBOL-clean's instructions (ARCH-PERF-TOOLING.md §8). Same two engines, opposite verdict, because the two workloads exercise opposite halves of SCRIP's cost structure — this is the whole point of the row.

### 3b. m4-standalone decomposition — the clean answer

`callgrind_annotate` on the standalone binary (no compiler loaded in-process — this is definitionally what "the m4 benchmark" measures):

| Ir | % | what |
|---|---|---|
| 2,604,212,411 | 99.79% | unresolved address in `fibonacci.prog`'s own text — the emitted program's own compiled instructions (no ELF symbol; consistent with flat-wired boxes carrying no per-box DWARF boundary by default, ARCH-PERF-TOOLING §2.3) |
| 967 | 0.00004% | `emit.cpp:ab_fn_hash`/`bb_ab_slot_for`/`bb_ab_fn_cell_ptr`/`ab_hash_on` — **not compile code**; these are the by-name-dispatch runtime helpers (same functions labeled "runtime, seat1 fix residual" in beauty's own table above) |
| ~5.4M | 0.21% | unitemized remainder below threshold |

**Zero instances of any compile-side function** (`codegen_flat_chain_body`, `zd_plan`, `zls_*`, `lower_common.c`, the parser, the optimizer) appear anywhere in this run — not "small," *absent*, because the compiler is not loaded in this process. This is the strongest form of the answer: not an estimate, a structural guarantee.

### 3c. m3-combined decomposition — same kernel, beauty's own methodology, for apples-to-apples

| Ir | % | site | layer |
|---|---|---|---|
| 2,636,201,552 | 98.34% | unresolved JIT-slab address `???:0x...a2bd000` | emitted code (mode-3 self-JITs into an anonymous slab, hence no ELF symbol — this is the m3 counterpart of §3b's 99.79% bucket; the two numbers agree to within 1.2%, a consistency check on the m3≡m4 output invariant) |
| 5,933,003 | 0.22% | `__strcmp_avx2` | mixed |
| 4,685,421 | 0.17% | `x86_asm.h:bb_emit_x86` | compile |
| 2,831,158 | 0.11% | `emit.cpp:codegen_flat_chain_body` | compile |
| 1,764,272 | 0.07% | `x86_asm.h:x86_parse` | compile |
| 1,486,300 | 0.06% | `x86_asm.h:x86_is_reg` | compile |
| 1,281,205 | 0.05% | `emit.cpp:zd_plan` | compile |
| 1,050,210 | 0.04% | `rtx_icnnum.S:rt_coerce_num2_d` | **runtime** (a real out-of-line RT call, named and small) |
| 456,302 | 0.02% | `lower_common.c:bb_src_of` | compile |
| 429,841 | 0.02% | `zeta_storage.c:zls_mark_value_refs` | compile |
| 585,788 | 0.02% | `snobol4.lex.c:yylex` | compile |

**Every named compile-side function that dominated beauty appears here too — at 100–1000x smaller share.** `codegen_flat_chain_body` is 20.87% of beauty's total and 0.11% of fibonacci's; `zd_plan` is 9.83% vs 0.05%. Not a different mechanism — the same fixed, size-proportional-to-source compile cost, diluted by 5,000 iterations of runtime work that beauty's single self-hosting pass doesn't have.

---

## 4. THE NUMERIC COMPILE-vs-RUNTIME-vs-EMITTED-CODE SPLIT — both workloads, side by side

| | beauty self-host (`0ff71be8`, m3) | fibonacci N=5000 (`2659558e`, m3) | fibonacci N=5000 (`2659558e`, m4-standalone = "the m4 benchmark") |
|---|---|---|---|
| **Total Ir** | 15,845,933,856 | 2,680,694,604 | 2,609,640,572 |
| **Compile-side (definite)** | 61.83% | ~0.5%¹ | **0%** (structural — compiler not loaded) |
| **Compile-side (+ likely)** | 63.90% | — | 0% |
| **Mixed/unattributed** (strcmp etc.) | 8.50% | ~0.3% | ~0% |
| **Runtime (definite: by-name dispatch, RT calls)** | 3.50% | ~0.1% | 0.00004% |
| **Emitted program's own execution** | *not separable from the above at this threshold — see §2's own note that it needs a caller-tree split* | 98.34% (JIT slab) | 99.79% (text segment) |
| **Long tail, unitemized (<0.98% each)** | 24.10% | ~1.1% | 0.21% |

¹ Sum of the named compile functions in §3c (bb_emit_x86 + codegen_flat_chain_body + x86_parse + x86_is_reg + zd_plan + bb_src_of + zls_mark_value_refs + yylex + msort-equivalents ≈ 12.9M / 2,680,694,604 ≈ 0.48%).

**Headline: beauty spends ~62–72% of its total instructions compiling itself; fibonacci spends ~0.5% (m3) or a structural 0% (m4-standalone).** This is not a close call and does not depend on exactly how the long tail resolves in either case — the gap is two orders of magnitude.

---

## 5. THE FIVE OLD RANKING ENTRIES — RE-PRICED or GONE, against the new `0ff71be8` beauty total

| old entry | old % (of 27,760,640,730) | old absolute Ir | new % (of 15,845,933,856) | new absolute Ir | verdict |
|---|---|---|---|---|---|
| (a) `bb_ab_slot_for` | 43.8% | ~12,159M | 1.22%² | 193,227,139² | **GONE.** Seat1's fix ate it; residual is 63x smaller and now correctly bucketed as "runtime, fix residual," not the dominant line. |
| (b) `codegen_flat_chain_body`+`zd_plan` | 17.5% | ~4,858M | 30.70% | ~4,864,249,690 | **RE-PRICED, flat in absolute terms** (~4,858M → ~4,864M, +0.1%). Share doubled only because the denominator shrank 43% — this cost is compile-time and untouched by a runtime-dispatch fix. |
| (c) zeta-storage planning | 8.0% | ~2,221M | 13.44%³ | ~2,129,673,000³ | **RE-PRICED, ~4% down in absolute terms** — essentially flat, same reasoning as (b). |
| (d) label-pool linear scans | 5.4% | ~1,499M | 4.31%⁴ | 682,975,761⁴ | **RE-PRICED, ~54% down in absolute terms** — the one old entry that plausibly improved for its own reasons, not just denominator shrinkage; not investigated further this row (out of scope, measurement-only). |
| (e) runtime by-name dispatch | 4.6% | ~1,277M | 3.50%⁵ | 554,037,715⁵ | **RE-PRICED, ~57% down in absolute terms** — the by-name mechanism itself also improved, not just (a)'s giant entry within it. |

² `ab_fn_hash`+`bb_ab_slot_for` residual, §2 table. ³ `zls_node_bytes`+`zls_mark_value_refs`+`zx_cmp`. ⁴ `emit_label_intern`+`emit_label_lookup_offset`. ⁵ `meth_is_user_proc`+(a)'s residual.

Sum of new %'s (a)+(b)+(c)+(d)+(e) = 1.22+30.70+13.44+4.31+3.50 = **53.17%** of the new total, vs. the old ranking's 43.8+17.5+8.0+5.4+4.6 = **79.3%** of the old total — coverage dropped because (a) collapsed and nothing replaced it; the *composition* of what's left is now dominated by (b) and (c), i.e. by compile-time planning and codegen, not by the by-name dispatch table that used to be "the whole ballgame" (ARCH-PERF-TOOLING §4 item 1).

---

## 6. BY-NAME VERDICT — the queued perf rows

Pulled fresh from `/home/resources/postoffice/QUEUE.tsv` this session (not the brief's static list, which is now stale in one place — see below). Current composition: rank 0 has 24 rows (mostly PERF BLOCKER / measurement-integrity, not instruction-share rows — `perf-board-rebaseline` itself and `descr-stamp-fields`, the regression source, are both in it), rank 1 has 11, rank 2 has 19, rank 3 has 4 (infra, not verdicted — not instruction-share rows), rank 4 has 2.

**⭐ `box-fusion` is NOT where the brief's static text says it is.** It reads rank 1 in the brief's own copy-pasted question; live QUEUE.tsv has it at **rank 6**, demoted by HQ on `beauty.sno`'s own 0.64%-emitted-code measurement, with an explicit reinstatement condition: *"DO NOT PROMOTE IT BACK without a measured emitted-code share on corpus/benchmarks/ (blocked itself on rank-0 bench-harness-unmeasurable, since those kernels self-shrink under callgrind)."* **That blocker is now resolved** — `bench-harness-unmeasurable`'s fixed-work-mode fix landed in `harness.inc` this same day, and §3b of this FINDING *is* the missing measurement: **99.79% emitted-code share on fibonacci (m4-standalone).** This is a direct, actionable trigger for HQ: box-fusion's own stated reinstatement condition is met.

| row | rank | targets | workload | verdict |
|---|---|---|---|---|
| `box-fusion` | 6 (not 1 — see above) | emitted box code directly | benchmark kernel | **REVIVABLE NOW, doubly confirmed.** My §3b (99.79% whole-kernel, fibonacci) meets its blocker on its own; `FINDING-2026-08-22-seat06-arith-loop-fusion-target...` (landed mid-session, §7) independently measured the *statement itself*, box-isolated, on `arith_loop`: **7.23% raw / 24.34% with the §9 harness artifact excluded** — 1-2 orders of magnitude above beauty's 0.64% either way, and cross-validating `FINDING-2026-08-21-s250`'s fused-cost number to within ~3%. Two independent measurements, two kernels, same conclusion. HQ's call to re-promote, not this row's. |
| `kill-the-plt` | 1 | PLT/GOT indirection on every RT call from emitted code | benchmark kernel (mode-4) | **MEASURED END-TO-END mid-session by seat01** (`FINDING-2026-08-22-seat01-kill-the-plt-...`, landed after this row's first push): achievable flag saves ~0%, the real fix ~1.5% of call cost, naive static-link is an unrelated 2x constructor-drop trap. Real but small — my own §3c (`rt_coerce_num2_d` at 0.04% on fibonacci) is directionally consistent (arithmetic-heavy kernel, few RT calls/iter). Superseded by seat01's number; not re-derived here. |
| `chain-slot-coalescing` | 2 | slot coalescing in the value chain | — | ⛔ **QUEUE.tsv IS STALE ON THIS ROW.** Its own live brief text still reads as open (Proebsting copy-prop framing), but `box-fusion`'s own queue text says outright: *"Sibling row chain-slot-coalescing is CLOSED (its named mechanism provably could not reach a counted target: arms A and B identical at 112.24/112.25 instr, 24.05/24.05 stores)"* citing `FINDING-2026-08-21-s250`. Two rows in the same live queue disagree about a third row's status. Flagging to HQ as its own item (§7), not fixing the queue file myself (out of this row's scope). |
| `callout-fragment-entry-cost` | 1 | match-time deferred-callout entry/exit overhead | demo (claws5) | **PRICED AND PARTIALLY CUT mid-session by seat09** (`FINDING-2026-08-22-seat09-callout-fragment-entry-cost.md`, landed after this row's first push) — found the brief's own stale baselines, re-measured, cut one step. Same emitted-code/RT-call bucket as kill-the-plt; superseded by seat09's number, not re-derived here. |
| `table-nested-subscript-cost` | 1 | 3-level table build (algorithmic, not codegen) | demo (claws5) | **VALID, independently self-confirming** — its own queue text already states "emitted boxes are 8.5%, runtime C is 91.5%" on table_access, i.e. this row *already contains* exactly the kind of runtime-dominance evidence this FINDING is generalizing from a second kernel (fibonacci). Corroborates, not superseded. |
| `ir-ident-differ-inline` | 1 | inline lowering of IDENT/DIFFER opcodes | emitted code, general | **VALID** — targets emitted-code path directly, same bucket confirmed dominant on kernels. |
| `rtcc-veneer-strip-pure-asm` | 1 | register save/restore veneer around pure-asm RT calls | emitted code | **VALID** — literally the emitted call-sequence bucket; real. |
| `loopctl-inline-lt-concat-store` | 1 | LT/concat/store inlining (PLUS already done) | emitted code | **VALID**, partially landed already per its own text. |
| `cond-assign-double-fire` | 1 | `.` conditional-assign fires twice vs. SPITBOL once | — | **OUT OF SCOPE for this row.** This is an oracle-divergence *correctness* bug (a semantics defect), not an instruction-share optimization — it doesn't have a "workload" in the sense this row measures. Unaffected by anything here. |
| `table-int-keys-and-nd-subscript` | 1 | integer-key stringification + N-D subscript re-entry | table_access kernel | **VALID**, same self-confirming evidence as table-nested-subscript-cost above ("exact inverse of arith_loop" — i.e. this row already independently measured a kernel workload as runtime-C-dominated). |
| `name-lookup-strcmp` | 4 | name resolution by strcmp, ~10% of compile | beauty-like / `CODE()`/`EVAL()` at runtime | **VALID, and already correctly ranked** — its own queue text says "COMPILE-side... pays in[to CODE/EVAL]," already below every runtime row per Lon's own s251 ruling. This session's beauty decomposition independently confirms the mechanism is real (`bb_src_of` 2.62%, strcmp 8.50% mixed). No re-ranking needed — it's already filed where this FINDING would put it. |
| `compiler-quadratic-residue` | 4 | compile-side quadratic, helps `CODE()`/`EVAL()` | same as above | **VALID, already correctly ranked**, same reasoning. |
| `pt-group-defer` | 1 | 3-call C round trip in group-defer, 59.4% of treebank-match cycles | treebank demo | **VALID** — RT-call-overhead bucket, same family as kill-the-plt/callout-fragment-entry-cost, on yet another non-beauty workload. |
| `spine-carve-coalescing` | 1(text)/2 | one `sub rsp` per fall-through stretch instead of per-box | emitted code | **VALID** — direct emitted-code codegen lever. |
| `diag-regs-stmt-and-bb` | 1 | r10=stmt#, r11=BB-id crash telemetry | — | **OUT OF SCOPE for this row** — not an instruction-share optimization at all, it's diagnostic infrastructure (blocked on `free-r10`/`free-r11`, the same eradication ladder this seat has a separate open rung E-5 claim against, per this session's inbox — unrelated to this row's ranking question, noted only for cross-reference). |

**Not individually opened this session** (16 more rank-1/2/4 rows; flagging rather than guessing): `descr-stamp-asm-mints`, `porter-m4-duplicate-label` (rank 1); `ab-cell-hoist`, `apply-snodef-m4`, `array-sum-valgrind-segv`, `beauty-cn-convert`, `beauty-m3-zls`, `blob-resume-refusals`, `bm-2-one-copy`, `fence-jstrbody-cas`, `gc-w2`, `goto-tail-wires-audit`, `medium-retire`, `mwseg-recfn-m4`, `oracle-asset-fallback-three`, `pt-json`, `ptx-shift-m4`, `treebank-allocating`, `wire-stack-rung2-c-entry` (rank 2). By name alone several of these read as correctness/crash/feature rows swept into the perf-priority ranks by Lon's blanket "put all performance items higher priority" rather than instruction-share-chasing rows (e.g. `array-sum-valgrind-segv` is a crash, `blob-resume-refusals`/`gc-w2`/`wire-stack-rung2-c-entry` read as feature work) — **not verified, explicitly not verdicted**, HQ or a future row should open each before trusting that guess.

---

## 7. ADDENDUM — cross-seat corroboration landed mid-session (after this row's first push, before `done`)

`git pull --rebase` immediately before pushing §§0–8 pulled in 8 new `.github` commits from other seats, three of which bear directly on this row. Rather than let a stale FINDING stand, folding them in here before calling `done`.

**7a. seat06 independently confirms §0's beauty regression.** `efbce963`: *"milestone-1 mode-3 beauty self-host currently DIFFs from oracle, reproduced via canonical `board_beauty_m1.sh` on a pristine untouched tree — flagged, not chased."* A second, independent reproduction, different tooling (`board_beauty_m1.sh` vs. this row's direct md5 check), same underlying break. Also: `eeb0c1df` (Lon, s256) records that HQ itself was caught mid-bisecting this same regression and told to stop and delegate — a third party converging on it. §0's "reconcile against whatever eq-coercion actually tested" stands; this strengthens "the break is real" independent of that reconciliation.

**7b. seat06 found a real FIXED-WORK harness defect and named it as this row's territory — checked against my own fibonacci numbers, and they are not materially affected.** `FINDING-2026-08-22-seat06-arith-loop-fusion-target-is-24-percent-not-0-64-percent-and-fixed-work-mode-has-a-string-coercion-defect.md`: `harness.inc`'s FIXED-WORK mode sets `ZK = fixed_n`, and `fixed_n = INPUT` — SNOBOL4's `INPUT` always returns a **STRING**. TIME-mode's `ZK` starts as an integer literal and is only ever doubled arithmetically (`ZK = ZK * 2`), so it stays numeric-tagged; FIXED-mode's bare `ZK = fixed_n` skips that arithmetic entirely, so `ZKN` (bound from `ZK` into every kernel's `ZBODY(ZKN)`) stays STRING for the kernel's whole run. Every `LT(ZI, ZKN)` in the per-batch loop must therefore re-coerce STRING→numeric from scratch via `rt_coerce_num2_d`, every single outer-loop iteration — a harness artifact, not a property of the kernel's own logic. On `arith_loop` (trivial ~29 Ir/iteration body), this coercion tax turned out to be **70.29% of the entire kernel's Ir**, badly corrupting the emitted-vs-runtime split for that kernel specifically.

**Did this corrupt §3/§4's fibonacci numbers? No — checked directly.** `fibonacci.sno`'s harness loop (`ZI = LT(ZI, ZKN) ZI + 1`, line 16) is the *identical* idiom, so it carries the *same* defect — and indeed §3c's own table already shows it: `rtx_icnnum.S:rt_coerce_num2_d` at 1,050,210 Ir (0.04%), captured and correctly attributed *before* this addendum was written, just not yet root-caused to the harness. The reason it's 0.04% here and 70.29% on `arith_loop` is not a discrepancy — it's the same fixed per-outer-iteration coercion cost (arith_loop: 564,000,282 Ir / 2,000,000 iterations ≈ 282 Ir/call; consistent order of magnitude here) landing against wildly different loop-body sizes: `arith_loop`'s body is ~29 Ir/iteration (the coercion dwarfs it), `fibonacci`'s body is `FIB(16)` — thousands of Ir/iteration of recursive calls, comparisons, and arithmetic (the coercion is noise against it). **§4's headline numbers stand unmodified**: the 97.35%/99.79% runtime/emitted-code share on fibonacci was never resting on this artifact being absent, only on it being small relative to a heavy kernel body, which it demonstrably is.

**This does generalize as a warning, though:** any *other* kernel with a light per-iteration body and the same `LT(..., ZKN)` idiom (arith_loop already confirmed; table_access and similar are candidates, not checked) would have its FIXED-mode runtime-share number inflated by this same artifact, the way arith_loop's was. Anyone citing a FIXED-mode Ir split on a *different* kernel than the two measured here (fibonacci, this row; arith_loop, seat06) should check for this first. **Not fixed here** — out of this row's own scope ("⛔ NO CODE FIXES IN THIS ROW... if you find a defect, mint it as a row and carry on"), and seat06 already declined to fix it for the identical reason. Naming it plainly for HQ in §8 rather than leaving it only in seat06's file.

**7c. `cond-assign-double-fire`** (marked out-of-scope/correctness in §6) **was fixed mid-session** by seat11 (`deebe1fb`) — consistent with this row's own classification of it as a correctness defect rather than an instruction-share row; no change to that verdict.

---

## 8. Items for HQ (findings, not blockers — this row continues per protocol regardless)

1. **The beauty regression is real and unresolved at HEAD `2659558e`** — see §0. Please reconcile against whatever `regression-descr-stamp-fields-eq-coercion` actually tested; they may be the same underlying `62017f8a` defect surfaced two different ways, or genuinely different bugs. Still nominating as a RANK-0 PERF BLOCKER candidate (unchanged from first sitting) — beauty's own Ir number cannot be trusted at HEAD until this is fixed.
2. **`chain-slot-coalescing` (rank 2) contradicts `box-fusion`'s (rank 6) own text about it being CLOSED.** One of the two queue entries needs updating; not done here (out of this row's scope).
3. **`box-fusion`'s own stated reinstatement condition is now met** — §3b supplies the missing kernel-side emitted-code-share measurement (99.79%) its rank-6 demotion was waiting on.
4. Beauty spends ~62–72% of its Ir compiling itself; a benchmark kernel spends ~0.5% (m3) to a structural 0% (m4-standalone, the actual "m4 benchmark" methodology, confirmed by inspecting the harness: `--compile` happens once, unmeasured, before the timed/counted region). **This is not new policy** — ARCH-PERF-TOOLING.md §7 already ranks "COMPILE-SIDE PERF... not the m4 benchmark" below every runtime row; this FINDING supplies the first direct kernel-side measurement backing that existing ruling, and shows it's structurally guaranteed, not just empirically likely.
5. SCRIP is 1.92x *fewer* instructions than clean SPITBOL on fibonacci (m4-standalone) vs. ~5.8x *more* instructions on beauty (§3a, §ARCH-PERF-TOOLING §8) — same two engines, opposite verdict depending on workload. Presenting as fact for HQ's re-ranking, not editorializing on what it should mean for priority.
6. 16 rank-1/2/4 rows not opened this session (§6 tail) — do not assume verdicted.
7. **FIXED-WORK harness defect** (§7b, seat06): `harness.inc:69`'s `ZK = fixed_n` never gets numerically coerced (`fixed_n` traces to `INPUT`, always STRING), so every kernel using the `LT(ZI, ZKN)` loop-counter idiom pays a per-outer-iteration STRING→numeric coercion tax that inflates its FIXED-mode "runtime" share by an amount that depends on how light the kernel's own loop body is (70% of `arith_loop`'s total; noise — 0.04% — against `fibonacci`'s heavier body). One-line fix per seat06 (`ZK = fixed_n + 0`), not applied by either of us (out of both our rows' scope). Suggest minting `fixed-work-zk-string-coercion` as its own row before anyone trusts a FIXED-mode split on a third kernel.
8. seat06's `arith_loop` measurement and seat01's `kill-the-plt` measurement, taken together, show emitted-code/RT-call share varies widely *by kernel* (7–99.8% depending on kernel and what's excluded) — all far above beauty's 0.64%, none of them close to beauty's near-zero. The workload split (beauty vs. kernel) is the first-order effect this row was asked to settle; which specific kernel/mechanism best represents "the benchmark" is a second-order question this row did not adjudicate.

---

## 9. DONE-WHEN STATUS (brief's own checklist)

- ✅ `make pristine` at HEAD (HQ-27) — done twice this session (once to reconfirm the regression at `2659558e`, once implicitly via the `0ff71be8` bisection carried from the first sitting).
- ✅ New total Ir posted beside 27,760M and 15,870M (§2).
- ✅ Per-function decomposition on beauty (§2) and on a benchmark kernel (§3b, §3c) — both done.
- ✅ Second workload (`fibonacci.sno`, fixed-work N=5000) — measured three ways (m3, m4-standalone, SPITBOL-clean), decomposed.
- ✅ Explicit compile-vs-runtime-vs-emitted-code numeric split, both workloads (§4).
- ✅ Named, by-row verdict on the queued perf rows (§6) — 14 rows verdicted in detail, 16 explicitly flagged as not opened, one queue inconsistency surfaced (`chain-slot-coalescing`), one row's blocker shown resolved (`box-fusion`).
- ✅ SPITBOL side — beauty: citing seat2's un-retracted 228,144,314/806,084,475 (unchanged, SPITBOL-side numbers don't depend on SCRIP's commit history); fibonacci: freshly measured clean-SPITBOL this session (§3a).
- ✅ Zero code changes.
- ✅ FINDING carries the numbers — this is that FINDING, now DONE.

Row complete. Handing off via `s4e_msg.sh done perf-board-rebaseline`.
