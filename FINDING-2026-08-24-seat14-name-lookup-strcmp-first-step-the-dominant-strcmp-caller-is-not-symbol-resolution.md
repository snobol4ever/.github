# FINDING seat14 — `name-lookup-strcmp` FIRST STEP: `bb_src_of` confirmed a separate pointer-scan defect (not string lookup); the real `__strcmp_avx2` cost is 54.8% internal codegen-label interning (already `compiler-quadratic-residue`'s territory) + 33% x86-register-string matching, NOT SNOBOL4 symbol resolution; runtime table row does not want the same interning

**Session:** 2026-08-24 seat14, THE LOOP row `name-lookup-strcmp` (rank 1), FIRST STEP only — investigation/confirmation per the row's own text ("before designing anything"). No design or implementation done this session.
**Instrument:** `valgrind --tool=callgrind --dump-instr=yes --collect-jumps=yes --smc-check=all-non-file`, RT_OPT=-O0 (default; NO -O2 builds per s262 FACT RULE), `make pristine` immediately before the run. Mode 3 (`--run`). Ir only, never wall clock.
**Workload:** `./scrip corpus/demo/snobol4/beauty/beauty.sno < /dev/null` — compile+init only, matching `profile-the-compiler-1426x`'s (seat09) methodology. **Not the row's original "N=400 synthetic"** — that benchmark could not be located in the current tree (checked `bench_sno_rtx.sh`, `bake_noise_floor_snobol4_fixed.sh`, `test_broad_corpus_snobol4.sh`, `corpus/benchmarks/snobol4/roman.sno`; none define an "N=400" configuration). Falling back to the beauty.sno methodology is consistent with this row's own LEDGER: seat09 (2026-08-23) already did the same substitution for the same reason ("evidence only... on a REAL workload, not the N=400 synthetic").
**Receipts:** SCRIP HEAD `ab9c087c`, corpus HEAD `76940dc6`. `beauty.sno`: 40,943 bytes, md5 `f20461f9114d50414fc925df1482c9b9` — **different content from seat09's run** (their md5 `006850eb4e1ff2d0f7afc1aac2671b65`, different path pre-regrid), so this is a fresh measurement, not a citation. `git log 6e4951c5..ab9c087c -- src/lower/lower_common.c src/driver/driver_label.c src/contracts/scrip_ir.c src/optimizer/proc_collect.c src/optimizer/gva_collect.c src/emitter/emit.cpp` is empty — none of the functions discussed below changed between seat09's run and this one, so the two profiles are comparing the same mechanisms on different (but structurally similar) input.

## 1. Total Ir and top-level reproduction of seat09's numbers

**13,164,072,487 Ir total** (seat09: 13,422,044,716 — 1.9% different, consistent with different beauty.sno content, same order of magnitude). Top self-Ir entries reproduce seat09's list closely:

| self-Ir | % | function | seat09's figure (different beauty.sno) |
|---|---|---|---|
| 3,299,982,934 | 25.07% | `emit.cpp:codegen_flat_chain_body` | 25.41% |
| 1,554,864,269 | 11.81% | `emit.cpp:zd_plan` | 11.99% |
| 1,039,423,793 | 7.90% | `zeta_storage.c:zls_node_bytes` | 7.92% |
| 964,021,292 | 7.32% | `__strcmp_avx2` | 7.24% |
| 412,901,191 | 3.14% | `lower_common.c:bb_src_of` | 3.10% |
| 86,446,124 | 0.66% | `__strncmp_avx2` | (not in seat09's top 15) |
| 50,457,592 | 0.38% | `name_binding.c:is_global` | 0.46% (bucket total) |
| 33,928,404 | 0.26% | `gva_collect.c:gva_index_of` | (below seat09's top-15 threshold) |

This close reproduction (all within ~0.3 percentage points despite different program content) confirms these are stable, mechanism-driven costs, not noise.

## 2. `bb_src_of` — confirmed a separate defect, NOT string-keyed name lookup

`src/lower/lower_common.c:251-300` (`bb_src_note`/`bb_src_of`): both compare **`IR_t*` pointers** (`g_bb_src.nd[i] != nd`) in a linear scan over a parallel-array side-table used for debug source-line annotation (feeds `SCRIP_SRC_COMMENT` and the emitter's zeta-domain statement-boundary scheduling, `emit.cpp` lines ~1058, 2466, 2473, 2486, 2871). `bb_src_note` additionally does a `memcmp`-based text dedup on insert. **There is no `strcmp` call anywhere in either function** — confirmed by direct source read, and confirmed empirically: `bb_src_of` does not appear anywhere in `__strcmp_avx2`'s 95-entry caller list extracted from this session's `cg.out` (§3 below). Its cost is real (3.14% self, matching seat09's 3.10%) but is a **pointer-identity linear-scan defect, structurally unrelated to string/name lookup**. The brief's framing of `bb_src_of` as evidence of "symbol/name resolution walking string comparisons" does not hold up against either the source or the profile. (seat09's own FINDING already hedged this correctly: "have the same shape... but are not confirmed as scans — flagging the shape, not the diagnosis." This session confirms: not a string scan, and not a caller of one either.)

## 3. Who actually calls `__strcmp_avx2` — full caller breakdown (964,021,292 Ir, the FIRST STEP's central question)

`callgrind_annotate --tree=caller --threshold=90` extracted the complete caller list for `__strcmp_avx2` (95 distinct call sites). Ranked:

| self-Ir via this caller | % of strcmp's 964M | calls | function | class |
|---|---|---|---|---|
| 380,016,157 | 39.4% | 16,549,883 | `emit.cpp:emit_label_intern` | internal codegen label pool |
| 148,611,425 | 15.4% | 7,149,248 | `emit.cpp:emit_label_lookup_offset` | internal codegen label pool |
| 136,344,922 | 14.1% | 6,065,362 | `x86_asm.h:x86_is_reg(char const*)` | x86 register-name string match |
| 88,980,077 | 9.2% | 4,183,935 | `x86_asm.h:x86_core_[abi:cxx11](...)` | x86 template string parsing |
| 73,428,282 | 7.6% | 3,085,354 | `x86_asm.h:x86_rnum(char const*)` | x86 operand string parsing |
| 48,871,078 | 5.1% | 2,287,897 | `name_binding.c:is_global` | SNOBOL4 global-name classification |
| 28,648,623 | 3.0% | 1,352,355 | `gva_collect.c:gva_index_of` | SNOBOL4 GVA-name lookup |
| 23,774,292 | 2.5% | 1,061,577 | `x86_asm.h:x86_parse(xop const&, opnd&)` | x86 operand parsing |
| 344,466 | 0.04% | 14,909 | `gva_collect.c:gva_name_eligible` | SNOBOL4 GVA keyword-exclusion check |
| 120,603 | 0.01% | 5,656 | `driver_data.c:dat_find_type` | DATA() field/type lookup |
| 68,834 | 0.01% | 3,130 | `proc_collect.c:scc_taint_graph` | procedure-name lookup |
| 7,661 + 1,677 | 0.001% | 432 | `driver_label.c:define_spec_from_expr`/`define_entry_from_expr` | SNOBOL4 label lookup |
| (all others) | ~1.8% | — | ~85 more sites, each <0.01% | assorted |

**This overturns the brief's central premise.** Grouping by class:

- **Internal codegen-label pool (54.8% of strcmp cost, 23.7M calls):** `emit_label_intern`/`emit_label_lookup_offset`. Read `emit_label_intern` at `emit.cpp`: `for (int i = 0; i < g_label_pool_n; i++) if (g_label_pool[i] && strcmp(g_label_pool[i]->name, name) == 0) return g_label_pool[i]; return emit_label_alloc(...)`. This is a linear scan over a **single whole-compilation label pool** (reset once per `bb_emit_begin`), not per-procedure — with only 1,222 calls to `emit_label_intern` itself (matches seat09's self-table entry) producing 16.5M strcmp comparisons, the pool must grow into the tens of thousands of entries by the time later calls scan it (consistent with this architecture's flat-wired-BB-blob design generating many internal jump labels per Byrd-box). **These are compiler-internal jump/branch labels, not SNOBOL4 identifiers.** ⛔ **This is not new territory — seat09's own FINDING already named this exact pathology** ("Shape B — linear scan / membership test that should be O(1)... the exact pathology the now-fixed `bb_ab_slot_for` was caught by [FINDING-2026-08-22-hq item #4]... and it is still there") **and assigned `emit_label_intern`/`emit_label_lookup_offset`'s own self-cost (473M+255M Ir, seat09's #8/#13) to `compiler-quadratic-residue`, not to this row.** Fixing it there (hash the label pool instead of linear-scanning it) would remove the majority of what currently shows up in `__strcmp_avx2`'s total — **as a side effect of a different row's work, not this row's design.**

- **x86 assembly string-based encoding (33.4% of strcmp cost, 14.4M calls):** `x86_is_reg`, `x86_core_`, `x86_rnum`, `x86_parse`. Read `x86_is_reg` in full: `static const char *regs[] = {"rax","rbx",...,"xmm7"};` (56 fixed strings) `for (...) if (!strcmp(s, regs[i])) return 1;`. **Genuinely and exactly the brief's own "small closed set (intern to an id)" shape** — but for x86 register/mnemonic names, not SNOBOL4 symbols. 56-entry linear strcmp scan × 6.07M calls is real, mechanical waste (a `switch` on length+first-char, a static hash set, or a compile-time perfect hash would make this O(1)). **This is a genuinely new, unowned class** — not found under any existing row title in a `grep -l "x86_is_reg\|x86_rnum\|template.*string" /home/resources/postoffice/tasks/*.task.md` sweep this session. Per this project's precedent (seat04's `perf-board-rebaseline` FINDING, seat09's own practice), **proposing this as a mint candidate for HQ, not self-minting**: working name `perf-x86-template-string-parse` — "x86_asm.h's template encoder resolves register/mnemonic names via repeated linear strcmp against small fixed string tables (x86_is_reg 56 entries, x86_core_/x86_rnum/x86_parse similar) on every operand of every emitted instruction; 33% of the compiler's own strcmp cost, ~14.4M calls on a single 41KB program."

- **Genuine SNOBOL4-identifier name lookups (the row's literal original scope): only ~8.7% of strcmp cost, ~3.66M calls, ~0.64% of the WHOLE compile.** `is_global` (5.1%), `gva_index_of`/`gva_name_eligible` (3.0%), `driver_data.c` DATA() lookups (0.01%), `proc_collect.c` (0.01%), `driver_label.c` label lookups (0.001%, essentially noise — `label_lookup` itself doesn't even surface as a caller of `__strcmp_avx2` above the display floor). These are real and match the brief's "resolve once at compile/lower time, follow a POINTER" framing structurally (`is_global`/`gva_index_of` both re-scan a linear name list on every call, called once per variable reference rather than once per distinct name) — but **numerically far too small on their own to explain the row's DONE-WHEN** ("`__strcmp_avx2` falls out of the compile-side top ten"). Fixing only these would shave ~8.7% off `__strcmp_avx2`'s cost and leave it comfortably in the top ten.

## 4. Closed vs. open set (FIRST STEP's second question, per site)

- `emit_label_intern`/`emit_label_lookup_offset`'s pool: **open, and large** — grows across the whole compilation (thousands of internal codegen labels for a 41KB program, not bounded by SNOBOL4-visible identifier count). Wants a hash table, not name interning to a small fixed enum.
- `x86_is_reg` and siblings: **closed and genuinely small** (56 fixed register-name strings, x86_core_/x86_rnum operate over a similarly small mnemonic/operand-kind vocabulary). Wants interning to an id / switch / perfect hash — this is the cleanest match to the brief's literal cure description of anything found this session.
- `is_global`: **open in principle** (global count bounded by `GLOBAL_MAX`, program-wide) but small in practice for most real programs; called once per reference, so the waste is redundant re-classification of the same name, not set size.
- `gva_index_of`/`gva_name_eligible`: same shape as `is_global` — per-program-wide list, re-scanned per reference; `gva_name_eligible`'s own 28-entry exclusion list (`INPUT`,`OUTPUT`,`TRIM`,... at `gva_collect.c:13-15`) is trivially closed and constant across all programs, a candidate for a `switch`/perfect-hash independent of interning scheme design.
- `driver_label.c:label_lookup`: closed set built once post-parse (`label_table_build`), genuinely small per program — but this session's profile shows it contributes negligibly to `__strcmp_avx2`'s cost on beauty.sno, so it is not empirically a priority regardless of its clean closed-set shape.

## 5. Runtime-side cross-check: does `table-int-keys-and-nd-subscript` want the same interning?

Read `/home/resources/postoffice/tasks/table-int-keys-and-nd-subscript.task.md` in full and verified `FINDING-2026-08-24-seat04-post-fix-table-array-callgrind-remeasurement.md` directly (not taken on faith). That row's analogous defect — `aggregates.c:tbl_key_str()` stringifying every integer table key, then hashing/strcmp-comparing the string — is **confirmed fixed** as of HEAD `eca52780`: seat04's fresh post-fix callgrind (§4 of that FINDING) states plainly "the old smoking-gun costs are gone, not just reduced... `tbl_key_str`, `_tbl_hash`, `__strcmp_avx2`, `rt_ws_strdup_c`... do not appear anywhere in the top 25" at either N=100 or N=2,000, because `table_set_descr_d`'s insert path "no longer builds `e->key` at all" — the fix was **type-tagged hashing of the runtime key VALUE directly** (hash the `DT_I` integer, compare descriptors), never touching identifier-name interning at all. **Answer: no, the runtime-side table row does not want the same interning scheme.** Its problem (hashing arbitrary runtime table-key VALUES, which can be any SNOBOL4 datatype) was already solved by a different, already-shipped mechanism, and the two problems don't share enough shape to warrant a shared design — one is runtime data-value hashing, the other (this row, narrowly) is compile-time identifier-name resolution, and the LARGEST piece of this row's own evidence (the codegen label pool) isn't identifier-name resolution either.

## 6. Recommendation for whoever picks this row up next

This row's own evidence, measured rather than assumed, does not support its literal premise as-written. Three follow-ups, not one:
1. **This row's own literal scope (SNOBOL4 identifier interning: `is_global`, `gva_index_of`, `gva_name_eligible`, `driver_label.c`, `proc_collect.c`, `scrip_ir.c`'s vslot lookups) is real but small** (~0.64% of total compile Ir on this workload) — worth doing as clean, well-scoped cleanup (each site's linear list becomes a hash map or the AST/IR gets a resolved pointer cached at first lookup instead of re-scanning per reference), but **will not by itself satisfy this row's DONE-WHEN** ("`__strcmp_avx2` falls out of the compile-side top ten") — that requires the label-pool fix, which is `compiler-quadratic-residue`'s territory, not a new design here.
2. **Coordinate with `compiler-quadratic-residue`** rather than duplicating: its own known "label-pool linear scan" pathology (`emit_label_intern`/`emit_label_lookup_offset`) is 54.8% of this row's own headline `__strcmp_avx2` evidence. Whoever closes that row's version of the defect should expect `__strcmp_avx2` to drop sharply as a side effect; whoever works this row next should re-profile AFTER that lands before designing anything for this row's own scope, to avoid solving a cost that's about to disappear regardless.
3. **A genuinely new, unowned class was found**: x86 assembly template string-parsing (`x86_is_reg`/`x86_core_`/`x86_rnum`/`x86_parse` in `src/templates/x86_asm.h`) is 33.4% of `__strcmp_avx2`'s cost and matches "small closed set, intern to an id" more cleanly than anything in this row's own original scope. Proposing as a mint candidate for HQ (not self-minted): `perf-x86-template-string-parse`.

⛔ Per this project's own culture ("A brief whose numbers turn out wrong is STILL A BRIEF — the corrected number IS a deliverable"), this FINDING is filed as a correction, not a blocker — nothing here required a STOP-and-ask; the row's FIRST STEP text itself asked exactly this question ("confirm the split is really name lookup and not incidental") and got a clear, if partly negative, answer.

## 7. Not done this session (explicitly out of scope for FIRST STEP)

No design or implementation of any interning/hashing scheme. No changes to `emit.cpp`, `x86_asm.h`, `gva_collect.c`, `name_binding.c`, `driver_label.c`, `proc_collect.c`, or `scrip_ir.c`. No new row minted (candidate proposed in prose only, per §6.3). `table-int-keys-and-nd-subscript`'s own remaining scope (N-D dispatch consolidation, `.NAME` cost) not touched — read only for the cross-check in §5.
