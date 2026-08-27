# FINDING 2026-08-27 seat07 — `table_set_descr_d`: the one available `rt_sxt_break_fast` lever landed but is INERT on `table_access.sno`; the remaining 25.90% is -O0 call tax plus an already-tuned allocator, not a hash/probing defect

**Date:** 2026-08-27 · **Seat:** seat07 (FLEET-16) · **Row:** `perf-table-set-descr-hash-bucket-cost` (rank 1, claimed via `s4e_msg.sh next`, first session on this row) · **Build:** `make` EXIT=0 at SCRIP HEAD `f928c8ca` (post 3-repo pull) · **RT_OPT=-O0** (mandatory) · **Instrument:** `valgrind --tool=callgrind` + `callgrind_annotate`, plain (no `--separate-callers`, matching `test_gate_instr_budget.sh`'s own `measure_ir`) · **Oracle/mode:** SCRIP mode-4 native binary, `corpus/benchmarks/snobol4/table_access.sno` standalone (no wrapper — same recipe the gate uses) · **Output verified byte-identical before/after** (`sum of T[1..500] = 250500` / `after 20 rebuilds = 250500`).

## ⭐ HEADLINE

There is exactly one live, unconverted `rt_sxt_break` call site left inside this row's own named target function, `table_set_descr_d` (`src/runtime/aggregates.c:425`) — the sibling row `perf-sxt-break-unconditional-call-tax` (seat04, 2026-08-27, LANDED) explicitly named it as one of six remaining call sites and its own QA invited exactly this follow-up. **Landed the identical, already-safety-derived `always_inline` substitution** (`rt_sxt_break` → `rt_sxt_break_fast`) at that one site. ASM-diff confirms it inlined cleanly (zero `call` instructions, direct `g_sxt_owner` RIP-relative access — the same signature the precedent's own proof used). **But it measures as a genuine no-op on `table_access.sno` specifically: 12,997,937 → 12,997,923 Ir (14 Ir, noise-level, not attributable to the guarded branch at all)** — because `table_access.sno`'s write path (`T[I] = I * 2`) stores only `DT_I` (integer) values, and the `rt_sxt_break*` call is gated behind `val.v == DT_S`, so the branch this fix speeds up is never taken by this benchmark's workload. The fix is real, correct, and a genuine system-wide win for any table whose *values* are strings — it just isn't the lever this row's own DONE-WHEN measures.

Went on to profile `table_set_descr_d`'s own line-level cost on the integer-only workload it actually runs (see table below) and did not find a second safe lever: the two largest remaining costs are -O0's inherent call/prologue/epilogue ceremony (immovable without a hand-asm port, a materially bigger undertaking than this row's "smallest repro" scope) and `_tbl_grow`'s allocation cost, which is already the subject of extensive prior measurement-driven tuning against CLAWS5 (floor=1-vs-4, chain-vs-vector) that this row's own GOAL explicitly forbids re-deriving from scratch.

## ⚠ RE-PROVEN POST-REBASE (RULES.md: a baseline measured before a rebase is void after one)

Between this session's claim and push, this session's second `git pull --rebase` (pre-push, required
after the first rebase touched `pattern_match.c`/`core.c`) picked up `d7ce4556` (a DIFFERENT seat,
`perf-table-subscript-fastpath` lever 2 landing/pushing mid-session, confirmed via
`git merge-base --is-ancestor d7ce4556 <this session's first-pull tip>` = not-an-ancestor, i.e.
genuinely new) which re-pinned
`TABLE_ACCESS_IR_WATERMARK` 12,986,443 → **11,879,659** — a genuine ~8.6% win, UNRELATED to this row's
own mechanism (lever 2 fuses the CALL SITE that invokes `table_set_descr_d`, not the function's own
body). All numbers below are the ORIGINAL pre-rebase measurement, kept for the methodology and the
line-level breakdown (still structurally accurate — lever 2 doesn't touch anything inside
`table_set_descr_d`). **Re-measured fresh on the final, pushed tree:** total **11,875,402 Ir**;
`table_set_descr_d` **1,903,579 Ir**, now **16.03%** of the (smaller) total, up from 14.97% — its
absolute cost is essentially unchanged (as expected: this row's fix is inert on this workload either
way, and lever 2 doesn't touch this function's internals), so it is now a LARGER share of what
remains, which if anything strengthens the case for the hand-asm-port candidate flagged below.
Corpus (366/366 both modes) and `test_gate_instr_budget.sh` (GATE OK, all four workloads, on the
pushed watermark) both re-run clean on this final tree — see task LEDGER for the exact re-proof.

## Baseline, re-derived fresh (same discipline as this row's own NEXT block demands) — PRE-REBASE, superseded numbers, methodology intact

Standalone `table_access.sno` (mode-4, no wrapper, matching `test_gate_instr_budget.sh`'s own `measure_ir`): **12,997,937 Ir** before any change — 11,494 Ir (0.09%) above the pinned `TABLE_ACCESS_IR_WATERMARK=12986443`, well inside the ±2% band (this is incidental drift from the 27-file `SCRIP` pull this session picked up before claiming the row — unrelated files: `rt.c`, `core.c`, `gc_heap.c/h`, etc. — not chased, not this row's business). Per-function breakdown at this scale (`callgrind_annotate`, no separate-callers): `table_set_descr_d` **1,945,579 Ir (14.97%)**, the single largest NAMED function in the run (ahead of the dynamic loader's own relocation cost and `table_find_pair_d`'s 4.97%). This is a smaller, higher-fixed-cost workload than the row's own posted `bench_wrap.sh --n=2000` profile (722.6M Ir total, `table_set_descr_d` at 25.90%) — both numbers are honest, correctly different measurements at different scale, not a contradiction (same caveat this row's own NEXT block already states for roman/beauty).

## THE FIX: `aggregates.c:425`, one line, the exact precedented substitution

```c
// before
{ extern void rt_sxt_break(const char *); if (val.v == DT_S) rt_sxt_break(val.s); }
// after
if (val.v == DT_S) rt_sxt_break_fast(val.s);
```

`rt_sxt_break_fast` (`gc_heap.h:43`) already existed, `always_inline`, safety-derived by seat04 on the sibling row (same `g_sxt_owner` plain global, zero GC-triggering points inside the body) — re-verifying that safety case was NOT redone from scratch here; the ASM-diff below is the same class of proof the precedent itself required ("re-derive, don't assume the safety case transfers automatically" — QA note on the sibling row), applied at this call site specifically.

**ASM-diff (the load-bearing proof, ASM-DIFF-FIRST per RULES.md):** `objdump -d out/libscrip_rt.so --disassemble=table_set_descr_d` shows, immediately after the `!tbl` guard: `movzx eax,[rbp-0x210]` (reload `val.v`) → `cmp al,0x2` (`DT_S`) → `jne` around → direct `lea rax,[rip+...] # <g_sxt_fr>` / compare / conditional `mov QWORD PTR [rax],0x0`. **Zero `call` instructions** for this logic anywhere in the function — the identical shape (RIP-relative global, no PLT, more conservative stack spilling than a register-only value) the precedent's own objdump proof found for `NV_SET_fn`.

## Correctness (all re-run fresh, not assumed from the sibling row)

- `bash scripts/test_corpus_snobol4.sh`: **366/366 both modes, FAIL=0 SKIP=0 MISSING=0.**
- `bash scripts/test_gate_instr_budget.sh`: **GATE OK, all four workloads.** `table_access: Ir=12998563 within budget 12986443 ±2%`; `array_sum`/`roman` OK (untouched by this change); `beauty` NOTE-improved (pre-existing drift from concurrent unrelated work this session's pull picked up, not this row's business, not re-pinned here).
- GC-stress spot check on the one witness suite the sibling row used, run through the correct non-container harness (`corpus_suite_harness.py run gc.sno gc.ref --modes m3,m4` — running the `.sno` directly is the documented category error, 41 false "duplicate label" parse errors, not attempted twice): plain **15/15 both modes**; `SCRIP_GC_STRESS=7` **m3 13/15 (2 HANG), m4 15/15** — the HANGs are `213_gc_exhaustion_churn`/`214_gc_exhaustion_live_set` by name, the *exact same two* deliberately-named exhaustion tortures the sibling row's own LEDGER documents as pre-existing and unrelated at this same stress level. Reproduces the precedent's documented baseline exactly; no new GC hazard from this call site.
- `test_gc_stress_suite.sh` itself SKIPs (`no gc corpus at /home/claude07/corpus/crosscheck/gc`) — a stale hardcoded path from before the corpus reorg (real location: `corpus/tests/snobol4/crosscheck/gc.sno`). Pre-existing infra staleness, not caused by and out of scope for this row; flagged here rather than silently worked around a second time, not fixed (scope discipline).

## Line-level profile of `table_set_descr_d` on the workload it actually runs (post-fix, `callgrind_annotate` against source)

`table_access.sno`'s write path (`T[I] = I * 2`, `TABLE(512)` ⇒ 256 buckets, ~500 keys, both DT_I keys and DT_I values) exercises the integer hash arm only (`_tbl_h_int`, one `imul`) and the linear-scan arm of `_tbl_lower` (nbuck avg load ≈1.95, well under `TBL_LINEAR_MAX=12`) — both already the cheapest arms available per the file's own extensive prior tuning. Per-line self cost (10,500 calls):

| Line | Ir | % of fn | Note |
|---|---:|---:|---|
| function prologue (`void table_set_descr_d(...) {`) | 199,500 | 1.53% | -O0 stack-frame setup (`sub rsp,0x208`) — immovable without an ABI-level restructuring |
| `if (val.v == DT_S) rt_sxt_break_fast(val.s);` | 31,500 | 0.24% | this row's fix — cheap now, but the branch is never TAKEN here (confirms why the fix is inert for this benchmark specifically: even pre-fix, the never-taken guard's own comparison cost was already this small) |
| `h = _tbl_hkey(k)` | 10,500 | 0.08% | integer hash, already minimal |
| bucket/index housekeeping (3 lines) | 230,160 | 1.78% | `bi=...`/`b=...`/`i=_tbl_lower(...)` |
| existing-key scan loop | 61,950 | 0.48% | never hits (workload is all-fresh-insert) |
| grow check **+ `_tbl_grow` callee** | 141,456 self + **574,056 callee (6,552 calls)** | 1.09% + **4.42%** | **the single largest named cost** — `rt_gcheap_alloc`-backed bucket (re)allocation, one call per bucket's first touch (and occasionally a second, per the Poisson spread of 500 keys over 256 buckets) |
| `memmove` insert-shift | 75,604 self + 15,120 callee | 0.70% | small, `i==len` is the common case per the file's own comment |
| 4-field entry write (`key`/`key_descr`/`val`/`hkey`) | 252,000 | 1.94% | **second-largest self-cost line** — two `DESCR_t`-by-value struct copies at -O0, from already-stack-spilled parameters |
| `len++`/`size++` | 105,000 | 0.81% | |
| rehash-threshold check | 84,000 | 0.65% | never fires at this table size (500 < 256×4) |
| epilogue | 63,000 | 0.48% | stack-protector check + return |

## WHAT THIS ANSWERS FOR THE ROW, AND WHAT IT DOESN'T

- **"Is `table_set_descr_d` reducible via a known, precedented, non-hash lever?" — YES, and it is now LANDED** (the `rt_sxt_break_fast` fix), but it does not move `table_access.sno`'s own number because that benchmark's workload doesn't reach the guarded branch. The fix stands on its own merit (a real win for string-valued table writes elsewhere in the corpus/real programs) and is kept.
- **"Is there a second safe reduction inside `table_set_descr_d`'s own body, without reimplementing the hash/probing scheme?" — not found this session.** The two largest remaining costs (-O0 call ceremony, `_tbl_grow`'s allocator) are each either structurally immovable at this design layer or already the subject of prior, cross-workload-verified tuning (CLAWS5 cache-miss measurements cited in `aggregates.c`'s own comments) that this row's GOAL explicitly forbids re-deriving from scratch. Not chased further.
- **Candidate next-tier lever, NOT attempted here, flagged for whoever picks this up or a follow-up row:** `table_find_pair_d` (the READ path, `rtx_table.S`) is already a hand-written ASM port for exactly this reason (-O0's call/prologue tax dominates a small, hot, non-inlinable function). `table_set_descr_d` (the WRITE path, still C) is the natural next candidate for the same treatment — but it is materially bigger than the read port (the read path has no allocation, no insert-shift, no growth; the write path has all three), so this is a genuinely separate, larger undertaking, not a "smallest repro" fix for one sitting. Not minted as a new row here — recording the observation for whoever next profiles this function, per this row's own precedent of leaving open questions open rather than forcing either an answer or a new row that hasn't been sized yet.
- **The row's own deeper open question** ("can SCRIP beat SPITBOL's own table-write cost by 2-3x, or is parity the honest ceiling") is unchanged and still explicitly out of scope — this session did not profile SPITBOL's table implementation, per the row's own NEXT block ("neither measured nor assumed here").
- DONE-WHEN (`test_corpus_snobol4.sh` + `test_gate_instr_budget.sh`) passes, verified fresh, not assumed.

## LEDGER (raw artifacts, this session)

Scratch only, not committed: `table_access_{before,after}.{s,bin,cg.out,out}` under this session's scratchpad. Recipe fully reproducible: `./scrip --compile -o t.s /home/claude07/corpus/benchmarks/snobol4/table_access.sno`, `gcc -no-pie t.s -Lout -lscrip_rt -Wl,-rpath,$PWD/out -lm -o t.bin`, `valgrind --tool=callgrind --callgrind-out-file=t.cg.out ./t.bin < /dev/null`, `callgrind_annotate t.cg.out` (flat) / `callgrind_annotate t.cg.out src/runtime/aggregates.c` (line-level). GC-stress: `SCRIP_GC_STRESS=7 python3 scripts/corpus_suite_harness.py run corpus/tests/snobol4/crosscheck/gc.sno corpus/tests/snobol4/crosscheck/gc.ref --modes m3,m4`.

Source change: `src/runtime/aggregates.c:425` (one line), SCRIP commit `3f2d5634` (final pushed hash — rewritten twice by two pre-push `git pull --rebase` calls, `9eff9670` → `4c5113cf` → `3f2d5634`; diff itself unaffected both times, no conflicts, gates re-verified fresh after each per RULES.md).
