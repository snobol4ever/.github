# FINDING seat04 (IN PROGRESS) — perf-board-rebaseline: a live DESCR_t regression breaks beauty at HEAD (bisected, pristine-confirmed), and the pre-regression Ir count shows the workload is now compile-dominated, not runtime-dominated

**Session:** 2026-08-22 seat04 (`/home/claude04`, Claude Sonnet 5), THE LOOP queue row `perf-board-rebaseline`, rank 0 (resumed claim).
**Status:** IN PROGRESS — this is the FIRST STEP deliverable plus an unplanned blocking discovery, not the full DONE-WHEN. Posted now per "commit what you have," not held for the full row.
**SCRIP tree:** unchanged, HEAD `568bf098` (main, clean working tree). No code touched, no killswitch, no `.s` regen owed.

---

## 0. ⛔ BLOCKING DISCOVERY: beauty self-host is BROKEN at current HEAD — already sent to HQ (`q-beauty-regression-descr-tag-split`)

Attempting this row's FIRST STEP (`make pristine` at HEAD, callgrind beauty self-host, compare to seat1's 27,760M/15,870M) surfaced that **HEAD `568bf098` cannot reproduce the beauty.sno fixed point at all.**

- `scrip beauty.sno < beauty.sno` (pristine build at HEAD) prints beauty's own `mainErr1` label — the string `Parse Error` — instead of echoing its input. Output md5 `1c75f97d1907f92f4c0a8a3ef49eb9ee`, expected `6f1671c0757729992ae01a6bdf16f081`.
- **This is not a SCRIP compile error.** `grep -rn '"Parse Error"' src/` returns nothing — `Parse Error` is beauty.sno's *own* source-level error message (`beauty.sno:617`, label `mainErr1`), printed when beauty's hand-written grammar-checker decides its input doesn't parse. beauty is being fed itself, which does parse (it's beauty's own already-beautified source) — so this means some runtime value SCRIP computes for beauty's own logic is now wrong, and beauty's grammar-checker is (correctly, per its own logic) rejecting corrupted input. SCRIP's parser is not at fault; a runtime descriptor/value is.
- **Not a general break:** `test_smoke_snobol4.sh` is 7/7 both modes at HEAD, and trivial one-liner programs run correctly. Only beauty — a large, real program exercising far more of the language — trips it.

**Bisected, both boundary commits confirmed with a full `make pristine` (not incremental) per HQ-27:**

| commit | result | md5 |
|---|---|---|
| `0ff71be8` (free-r10: eradicate dead WREG fallback) | **GOOD** | `6f1671c0757729992ae01a6bdf16f081` |
| `62017f8a` (descr-stamp-fields: split DESCR_t tag into v/mod_op/src_node/slen, pin sizeof==16) | **BAD** | `1c75f97d1907f92f4c0a8a3ef49eb9ee` |

`62017f8a` is a direct parent-child pair with `0ff71be8` — no other commit sits between them. The break is this commit, full stop. Its own message says "Compare-site width conversion and stamping logic follow" — i.e. it knowingly landed the struct-layout half of a two-part migration before the call-site half. The promised follow-up, `0f17fbf4` ("convert all 171 asm+template DT_x tag compares to 8-bit"), does **not** fix it — tested directly, still `BAD`, identical failure md5. Every commit from `62017f8a` through HEAD (9 commits, including `0f17fbf4`) reproduces the identical `1c75f97d…` output. This has been broken, undetected, since `62017f8a` landed — the project's own gates (smoke, corpus) don't exercise beauty's fixed point, only `test_gate_sn7_beauty_self_host.sh`/`test_gate_em_beauty_subsystems_mode4.sh` do, and neither is in this row's path (not run this session — flagging that they should be, as a cheap next check for whoever owns the fix).

**Sent to HQ:** `bash scripts/s4e_msg.sh ask beauty-regression-descr-tag-split "..."` (full bisection detail, same content as above). **No fix attempted** — out of this row's scope (measurement-only brief, explicit "NO CODE FIXES IN THIS ROW"). Nominating as a RANK-0 PERF BLOCKER candidate per `ARCH-PERF-TOOLING.md` §7 (beauty is MILESTONE 1 / the self-host demo) — HQ's call whether to queue a dedicated fix row.

**Consequence for this row:** current HEAD cannot supply a valid beauty-side Ir number — the broken run terminates almost immediately via beauty's own error path, so its Ir count is trivially small and not comparable to anything. The measurement below substitutes the last pre-regression commit (`0ff71be8`), clearly labeled, so the rest of this row's question (workload composition) can still be answered honestly.

---

## 1. FIRST STEP DELIVERABLE — beauty self-host Ir at `0ff71be8` (last commit before the regression), pristine, m3

RT_OPT=`-O0` (default). `make pristine` immediately before the run. Output verified byte-identical to the fixed point (md5 `6f1671c0757729992ae01a6bdf16f081`) both plain and under callgrind before trusting the number.

| | Ir | vs. seat1 BEFORE (27,760,640,730) | vs. seat1 AFTER (15,870,550,520) |
|---|---|---|---|
| **`0ff71be8`, this session** | **15,845,933,856** | **−42.92%** | **−0.155%** (24,616,664 fewer) |

The small delta from seat1's own AFTER figure is expected, not noise-worth-chasing: `0ff71be8` sits 4 commits past seat1's exact fix (`8c1f2d41`), including `0ff71be8` itself (free-r10 WREG-fallback deletion) and a strtab_intern fix — both plausibly shave a small, real amount of dead work. **Headline: seat1's fix holds, is stable, and the 27,760M baseline is confirmed dead** — this reconfirms seat1's own finding independently, on top of it now being 4 commits later.

---

## 2. THE CORE QUESTION THE ROW EXISTS TO ANSWER — per-function decomposition, same run

`callgrind_annotate --threshold=98` on the `0ff71be8` run, top contributors:

| Ir | % | site | layer |
|---|---|---|---|
| 3,306,455,701 | 20.87% | `emit.cpp:codegen_flat_chain_body` | **emitter (compile)** |
| 1,557,793,989 | 9.83% | `emit.cpp:zd_plan` | **emitter (compile)** |
| 1,347,087,389 | 8.50% | `__strcmp_avx2` (libc) | mixed, needs caller-tree to attribute |
| 1,062,697,123 | 6.71% | `zeta_storage.c:zls_node_bytes` | **ζ-storage planning (compile)** |
| 618,079,680 | 3.90% | `zeta_storage.c:zls_mark_value_refs` | **ζ-storage planning (compile)** |
| 560,562,466 | 3.54% | `emit.cpp:cap_in_repeat_body` | **emitter (compile)** |
| 495,204,990 | 3.13% | `emit.cpp:bb_slot_get` | **emitter (compile)** |
| 448,712,592 | 2.83% | `zeta_storage.c:zx_cmp` | **ζ-storage planning (compile)** |
| 429,883,845 | 2.71% | `emit.cpp:emit_label_intern` | **emitter (compile)** |
| 414,572,179 | 2.62% | `lower_common.c:bb_src_of` | **lowering (compile)** |
| 360,810,576 | 2.28% | `by_name_dispatch.c:meth_is_user_proc` | runtime (by-name dispatch residual) |
| 327,060,492 | 2.06% | libc `msort_with_tmp` | likely compile (sort of some compile-time table) |
| 284,233,224+135,561,535 | 2.65% combined | `emit.cpp:frame_need_of`(+'2) | **emitter (compile)** |
| 253,491,916 | 1.60% | `emit.cpp:emit_label_lookup_offset` | **emitter (compile)** |
| 231,033,896 | 1.46% | `x86_asm.h:bb_emit_x86(...)` | **encoder (compile)** |
| 96,657,207+96,569,932 | 1.22% combined | `ab_fn_hash`+`bb_ab_slot_for` | runtime (seat1's fix's own residual cost) |

**⭐ This directly answers the brief's central question.** Of the top ~16 entries (covering roughly 75% of all instructions), only two — `meth_is_user_proc` (2.28%) and the by-name mechanism's own residual (1.22%) — are the *generated program's runtime*. Everything else named above is the **compiler compiling beauty.sno**: emitter (`emit.cpp`), ζ-storage layout planning (`zeta_storage.c`), lowering (`lower_common.c`), and the x86 encoder itself (`x86_asm.h`). This is mode-3 (`--run`), which compiles and runs in one process, so both costs land in one Ir total — and after seat1's fix removed the dominant *runtime* defect, what's left standing is overwhelmingly **in-process compilation**, not the emitted program executing.

This matches and sharpens the s254 warning the brief itself cited (48.6% runtime by-name + 46.8% in-process compile + 0.64% emitted code, *before* seat1's fix): with the 48.6% runtime bucket now cut by seat1's own measured 42.83%-of-everything reduction, the in-process-compile share of what's left is almost certainly larger than half, likely much more — **exactly the situation the brief warned about**: box-fusion, kill-the-plt, chain-slot-coalescing, and callout-fragment-entry-cost, if aimed at the *emitted* program's execution, are optimizing a sliver of this workload's total, not its dominant cost.

**Not yet done, and needed before this becomes a number instead of a strong signal:** a clean split isolating "codegen driver overhead" (things like `codegen_flat_chain_body`/`zd_plan` that run once per compile regardless of program size) from "per-construct compile cost that would shrink on a smaller program" — beauty is a big, single-shot compile, and mode-4 timing evidence elsewhere in this project (ARCH-PERF-TOOLING §4, "compile-side perf... not the m4 benchmark") suggests this compile-dominance may be specific to *how beauty is invoked* (compile-and-run once) rather than proof that compile time matters on, e.g., a benchmark kernel invoked the same way — which is exactly why the brief demands a second workload.

---

## 3. DONE-WHEN STATUS (brief's own checklist)

- ✅ `make pristine` at (attempted) HEAD — done; HEAD is broken, substituted last-good commit, fully disclosed above, not hidden.
- ✅ New total Ir posted beside 27,760M and 15,870M, delta visible (§1).
- 🟡 Per-function decomposition on beauty — done (§2), strongly indicates compile-dominance; not yet cross-checked with a caller-tree split for the mixed `strcmp`/`msort` entries.
- ❌ Second workload (a `corpus/benchmarks/snobol4` kernel) — **not yet measured this session.**
- ❌ Explicit compile-vs-runtime-vs-emitted-code numeric split (not just qualitative) — **not yet done.**
- ❌ Named, by-row verdict on the ~20 queued perf rows (box-fusion, kill-the-plt, chain-slot-coalescing, callout-fragment-entry-cost, table-nested-subscript-cost, ir-ident-differ-inline, rtcc-veneer-strip-pure-asm, loopctl-inline-lt-concat-store, cond-assign-double-fire, table-int-keys-and-nd-subscript, name-lookup-strcmp, compiler-quadratic-residue, …) — **not yet done.**
- ✅ SPITBOL side: not re-measured this session — citing seat2's already-committed, un-retracted numbers (228,144,314 Ir clean vs. 806,084,475 instrumented on this exact workload) rather than re-deriving them; nothing about the SCRIP-side regression touches the SPITBOL denominator.
- ✅ Zero code changes.
- 🟡 FINDING carries the numbers so far — this is that FINDING, marked IN PROGRESS.

**Next, if this row continues:** measure ≥1 benchmark kernel the same way (pristine, callgrind, per-function decomposition), then work the ~20-row verdict list against both workloads' decompositions.
