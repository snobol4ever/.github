# FINDING seat06 — `perf-string-runtime`'s own targeted mechanism is 0.36% of beauty's Ir, not "almost certainly part of the flagship gap"; a fresh live SCRIP-vs-SPITBOL beauty ratio is reproducible again after 2 days orphaned

**Session:** 2026-08-24 seat06, THE LOOP queue row `perf-string-runtime` (STEP 8, rank 0, umbrella claim — DONE-WHEN permanently prose/false by design per hq_C's V2-2 conversion).
**SCRIP HEAD:** `85a92341` · **corpus HEAD:** `dfc75192`. `git log ef18421e..85a92341 -- src/runtime/by_name_dispatch.c src/contracts/core.h src/contracts/descr.h src/runtime/rt/gc_heap.c` is empty — the 7 commits since STEP 7's (seat12) baseline touch only infra/test-tree files, so no re-measurement of `string_manip.sno` itself was warranted (would reproduce STEP 7's 0.2643x unchanged). This session instead closes a different open thread: **the row's own BRIEF has never been checked against beauty's actual measured profile**, despite beauty being the BRIEF's own stated reason this row matters.

## 1. The question this row's BRIEF never answered

The BRIEF (verbatim in the task file) says: *"AND THIS IS ALMOST CERTAINLY PART OF THE FLAGSHIP GAP: beauty is a string program and runs 9.34x slower."* That 9.34x is sourced from `FINDING-2026-08-22-s256-hq-the-runtime-perf-map-scrip-wins-scalar-and-loses-everything-real.md` (beauty self-host, SCRIP-runtime-only 2,129,544,838 Ir vs SPITBOL-clean 228,082,817 Ir). Across 7 STEPs and 6 sessions, nobody re-checked this claim against a full Ir attribution of beauty itself — every STEP measured `string_manip.sno`'s own synthetic kernel, which is the right instrument for isolating the mechanism but was never tied back to what fraction of beauty's *own* profile that mechanism actually explains. Two same-day/next-day findings that answer this directly were never cited in this row: `FINDING-2026-08-22-hq-scrip-spends-under-one-percent-of-its-instructions-running-the-program.md` and `FINDING-2026-08-21-s251-beauty-is-95-percent-compiler-and-the-compiler-is-quadratic.md`.

## 2. Fresh measurement, current HEAD, both engines fixed-point-verified

`corpus/demo/beauty/beauty.sno` moved during the s272 corpus reorg (`corpus/programs/snobol4/demo/beauty/` → `corpus/demo/beauty/`, includes → `corpus/include/`); paths below reflect the current tree.

```
SCRIP m3:      ./scrip beauty.sno < beauty.sno   → diff vs beauty.sno: IDENTICAL (true fixed point), plain and under callgrind
SPITBOL clean: (cd corpus/include && SETL4PATH=. sbl_clean_bin() -bf beauty.sno < beauty.sno) → diff vs beauty.sno: IDENTICAL, plain and under callgrind
```

| | Ir (callgrind) |
|---|---|
| SCRIP m3 (compile+run, mode-3 bundled) | 15,321,076,349 |
| SPITBOL clean oracle | 228,058,097 |
| ratio (SPITBOL/SCRIP, FACT RULE form) | **0.0149x** (SCRIP pays ~67.2x the instructions) |

⛔ **This TOTAL is not comparable to the BRIEF's own 9.34x** — that number is scoped "SCRIP runtime" only (compile subtracted out); this one is the mode-3 bundle (compile+run together, same basis as `FINDING-...-hq-scrip-spends-under-one-percent...`'s 34.5x and s251's 32.3x/23.2x-wall lineage). Flagging the basis mismatch rather than computing a false runtime-only split here — that decomposition already exists and is redone fresh in §3.

**This total ratio is, as far as I can find, the first one reproducible since 2026-08-23**: seat15's and hq_P's same-day findings (`FINDING-2026-08-23-seat15-reprofile-after-byname-bake-beauty-fixed.md` §3, `FINDING-...-hq_P-the-m1-board-grades-beauty-against-an-oracle-that-refuses-it.md`) independently found BOTH available SPITBOL oracles on this box refusing to parse beauty.sno post-BEAUTY-CN (`ERROR 251`, `&USER_DECLARED_CONSTANTS`), orphaning the whole SCRIP-vs-SPITBOL beauty ratio lineage pending `sbl-x`/D-12. That gap is closed now — most likely by corpus commit `8e70b83a` ("beauty includes are the first pristine curated set — beauty/*.inc → include/, Lon s269"), which post-dates both those findings and re-curated exactly the include tree the parse was failing in. Not chased further (out of this row's scope; the mechanism doesn't matter to what follows) — flagging for whoever owns `sbl-x`/D-12/`m1-board-judge-is-a-refusing-oracle` that the oracle-refusal symptom those rows were scoped around may no longer reproduce, worth a re-check there.

## 3. Where the 15.3B Ir actually goes — this row's own mechanism located precisely

`callgrind_annotate --threshold=99.5` on the fresh SCRIP run, self-cost:

| Ir | % | function | phase |
|---|---|---|---|
| 3,301,142,914 | 21.55% | `emit.cpp:codegen_flat_chain_body` | compile |
| 1,555,038,685 | 10.15% | `emit.cpp:zd_plan` | compile |
| 1,328,562,916 | 8.67% | `__strcmp_avx2` (name/label interning) | compile |
| 1,039,569,839 | 6.79% | `zeta_storage.c:zls_node_bytes` | compile |
| 617,708,745 | 4.03% | `zeta_storage.c:zls_mark_value_refs` | compile |
| 567,625,748 | 3.70% | `emit.cpp:cap_in_repeat_body` | compile |
| 514,162,570 | 3.36% | `emit.cpp:bb_slot_get` | compile |
| 447,954,648 | 2.92% | `zeta_storage.c:zx_cmp` | compile |
| 430,322,368 | 2.81% | `emit.cpp:emit_label_intern` | compile |
| 412,915,609 | 2.70% | `lower_common.c:bb_src_of` | compile |
| **360,810,576** | **2.35%** | **`by_name_dispatch.c:meth_is_user_proc`** | **runtime, by-name family** |
| 326,538,271 | 2.13% | libc `msort_with_tmp` | compile |
| … (11 more compile-phase emitter/zeta functions, each <2%) | ~9% | | compile |
| **55,910,112** | **0.36%** | **`by_name_dispatch.c:try_call_builtin_by_name_bl`** — **this row's own named target** | **runtime** |
| 42,861,772 | 0.28% | `getenv` (getenv-memo call-tax family, see §5) | runtime |

Summing every clearly-runtime symbol in the full (unthresholded) profile (`meth_is_user_proc` + `try_call_builtin_by_name_bl` + `rt_defer_probe_run` + `NV_GET_fn` + `bn_replace` + `is_global` + `rt_sg_scan_member` + `rt_defer_cell_read` + `getenv` + the by-name family's tail) comes to **≈5% of total Ir** — compile-phase functions own essentially all the rest, corroborating s251's "beauty is 95% compiler" finding on fresh current data (if anything the runtime share has *shrunk* further since s251, consistent with more by-name cures having landed in the interim).

**The BRIEF's own named target — `try_call_builtin_by_name_bl`, the function whose fix class the BRIEF proposes ("REPLACE is SPELLED IN THE SOURCE... resolve-once-at-lower-time") — is 0.36% of beauty's total Ir.** `bid_of` (this row's other headline symbol across STEPs 5-7) is 171,726 Ir = 0.00%, already effectively free — confirmed already baked at compile time for literal call sites per the `BAKED-BID ENTRY (hq_P s262)` mechanism live in the source (`by_name_dispatch.c:5268`), which this row's own STEP 5-7 sessions had already independently verified real and generalizing.

## 4. A different by-name mechanism dominated beauty two days ago — and it is already cured, by a different row

`FINDING-2026-08-22-hq-scrip-spends-under-one-percent-of-its-instructions-running-the-program.md` found `bb_ab_slot_for`/`rt_dyn_alpha_fn` (a **compile-time cell-slot lookup for user-defined PROCEDURE call targets** — `emit.cpp`, resolving `alpha$<procname>` — grepped and confirmed a structurally distinct mechanism from this row's `try_call_builtin_by_name`/`bid_of`, which live in `by_name_dispatch.c` and resolve BUILTIN names like SIZE/REPLACE) at **43.8% of beauty's total Ir**, the single dominant item in that profile.

Grepping the fresh callgrind output for that family today: `bb_ab_slot_for` is **104,400 Ir (0.00%)**, called only ~1,212 times (compile-time slot assignment, not per-call resolution). Its runtime successor, `rt_dyn_alpha_fn_p`, totals **19,091,101 Ir (0.12%)**. The source carries the reason, live and dated: `rt.c:833` — *"THE ALPHA CELL IS RESOLVED ONCE PER PROCEDURE, NOT ONCE PER CALL (hq_P s266)."* **This is a real, already-landed, already-attributed cure for a mechanism that dwarfed this row's own — 43.8% → 0.12%** — from a different session (hq_P, s266), not this row, and not something to re-claim here. Noting it because it directly bears on the BRIEF's "beauty is a string program, ergo by-name-string-dispatch is almost certainly the cause" reasoning: **the by-name-shaped cost that actually mattered on beauty was procedure-call resolution, not builtin-name resolution, and it's handled.**

## 5. Net effect on this row's own open QA ask

STEP 7 (seat12) sent `q-perf-string-runtime-close` to hq_C: close this row as SUPERSEDED (precedent: `perf-table-array-runtime` at s270), naming ~9-10 successor rows, or keep it open as a standing umbrella? Still unanswered in my inbox check this session (0 messages), and no ruling found anywhere in `.github` history. Per THE LOOP (a question is non-blocking), not deciding it here either — same posture as STEP 5/6/7. This FINDING adds a fact that materially strengthens the case for closure, independent of STEP 7's "top-of-profile is fully attributed to other rows" argument: **even a complete cure of every mechanism this row has chased across 7 STEPs would move beauty's own Ir by low single-digit percent at most**, because the row's own named mechanism (`try_call_builtin_by_name_bl`) is 0.36% of beauty, `bid_of` is already ~free, and `meth_is_user_proc` (2.35%, arguably this row's near-neighbor rather than its own target) belongs more naturally to `perf-by-name-builtin-dispatch`'s own scope. The BRIEF's "almost certainly part of the flagship gap" framing — this row's entire reason for existing above ordinary priority — does not hold up against beauty's own measured profile, current or as of s251/hq's 2026-08-22 attribution. Feeding this into the QA ask rather than treating it as a new, separate question.

## 6. Not chased (honest boundary)

- The 5% runtime bucket's own further decomposition beyond function-name self-cost (already done exhaustively for `string_manip.sno`'s synthetic kernel across STEPs 1-7; not re-derived for beauty specifically — the point of this pass was the cross-reference, not a new decomposition).
- Whether `sbl-x`/D-12/`m1-board-judge-is-a-refusing-oracle` should be re-checked or closed given §2's oracle-gap finding — flagged, not this row's row to resolve.
- A runtime-only (compile subtracted) fresh beauty ratio to directly update the BRIEF's 9.34x citation — the total-Ir ratio in §2 already answers the question this row needed answered (how much does this row's own mechanism matter to beauty); a full empty-stdin compile/run split remeasurement would cost another full callgrind pass for a number this row doesn't need to make its point.

No cure attempted anywhere, zero edits to any `.c`/`.h`/`.S`/`.cpp` source this session (row-factory duty, unchanged from every prior STEP on this row).
