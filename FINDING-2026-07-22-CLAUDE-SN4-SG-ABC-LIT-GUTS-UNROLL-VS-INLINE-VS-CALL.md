# FINDING 2026-07-22 (s128, Claude) — SG-ABC: LITERAL-NEEDLE GUTS 3-WAY — 100% UNROLL vs INLINE vs CALL on the match-only pair, vs SPITBOL

**Lon directive (s128):** "Let's get CLAWS5 and TREEBANK pattern MATCH only programs working. Let's see 100% loop un-rolling versus INLINE versus CALL. Each respects the R13, R14, and R15 contract and are optimized to use these three registers. Also show compared to SPITBOL."

## WHAT LANDED (SCRIP, uncommitted at time of writing → see session commit)

**`ZC_LIT_GUTS ∈ {UNROLL, INLINE, CALL}`** (zeta_choices.h, default UNROLL = byte-identical to s127 HEAD, corpus-wide — verified by .s diff on the pair, crosscheck watermark, AND all three regen scripts reporting zero changed artifacts). The switch forks the **LITERAL-needle (`op_sa < 0`) arm** of `bb_match_{span,break,any,notany}.cpp`:
- **UNROLL** — the s125/s127 machinery unchanged: ≤`ZC_CSET_CHAIN_MAX` compare-chain, else 256B membership table, char-steps unrolled ×`ZC_UNROLL_FACTOR`.
- **INLINE** — the *same emitted inner needle-loop body as the `ZC_SPAN_GUTS` INLINE arm*, shared verbatim via per-template `*_ndl_r8()` needle-load helpers: variable needles load `FRQ(op_sa+8)`/`FR(op_sa+4)`; literal needles load `lea r8,[rip+.Sn]` (TEXT, strtab RO) / movabs sval (BINARY) + `mov32 r9d, len` (imm32, byte-identical both media per R10).
- **CALL** — same sharing via `*_ndl_rsi()`, invoking the s126 `rt_sg_scan.S` lean leafs (R13/R15-aware, explicit lengths, NUL-safe).

All three flavors ride **R13=Σ / R14=δ / R15=Δ**; the INLINE/CALL bodies are *the same instructions* for literal and variable needles by construction (only the two needle-load instructions differ), so the flavor comparison isolates exactly the guts mechanism. `bb_match_breakx` stays UNROLL-only this rung (β-extension arm doubles the surface; neither match-only program uses BREAKX) — noted in the switch comment.

**BINARY needle-pointer lifetime:** frozen trees' `IR_LIT.sval` points into the pattern header's `rcp` strings (pattern_match.c `dtp_rcp_tree`), which live as long as the cached blob `h->fn` — movabs of sval is blob-lifetime-safe. (Same standing GC-W caveat as every baked pointer if the workspace ever slides.)

## ROUTING DISCOVERY THAT SHAPED THE DESIGN

Both match-only programs **store** their patterns in variables → compiled by the RUNTIME freeze (`bb_compile_pat_tree` → `sno_pat_tree_graph_rt`), whose **B-RE contract forbids runtime-operand pre-chains** (`npre > 0` is fatal). Pattern build evaluates needles to concrete strings → **100% of both programs' needle sites are frozen-LITERAL** (corroborated by corpus `d6b4bc24`'s own verification note). So the A/B/C fork had to live **in the templates**, not the lowerer — for a literal needle, INLINE/CALL need only pointer+length, both known at emit time. Zero lowerer changes, zero recipe-contract violation.

## ONE BUG CAUGHT AND FIXED IN-SESSION

First B/C build: claws5 **m4-only** FAIL — `lea r8, [rip + ]` (empty label) at the static ANY(&UCASE) site → as rejects. Cause: the `strtab_label` fill line was added to span/break/notany but missed in `bb_match_any`. m3 masked it (BINARY ignores the label); treebank masked it (no static ANY site). Fixed; full matrix green after.

## CORRECTNESS (all ref-identical: `matched bytes=65768` / `100155`)

3 flavors × 2 programs × 2 modes = **12/12 OK**. K-loop bench wrappers (N repeated matches in-program, zero side effects) also ref-identical on SCRIP and SPITBOL at K∈{1,5,50,200}.

## BENCHMARK — per-match ms, slope (t_KXL − t_K1)/(N−1), median of 5 interleaved reps

SCRIP runtime **`-O0`** (O2-DIRECTED-ONLY; no Lon `-O2` directive this session). SPITBOL = official optimized x64 `sbl -b -d512m -i64m [-s256m]` with `-CASE 0` prepended. claws5 N=200, treebank N=50. Harness: /tmp-only wrapper pair `claws5-matchN.sno`/`treebank-matchN.sno` (loop `mloop src pat :F(fail); n=n−1; GT(n,0):S(mloop)`) — NOT committed to corpus (Lon's call whether to adopt them as bench drivers).

| program | flavor | m3 | m4 |
|---|---|---|---|
| claws5-match | **A UNROLL** | **0.211** | **0.196** |
| claws5-match | B INLINE | 0.724 | 0.709 |
| claws5-match | C CALL | 0.739 | 0.789 |
| claws5-match | SPITBOL | 0.251 | — |
| treebank-match | **A UNROLL** | **1.918** | **2.000** |
| treebank-match | B INLINE | 2.143 | 2.633 |
| treebank-match | C CALL | 2.367 | 2.286 |
| treebank-match | SPITBOL | 0.878 | — |

**Readings:**
1. **A (100% unroll) wins BOTH workloads — and beats SPITBOL on claws5** (0.20–0.21 vs 0.25 ms/match, m3 and m4, at `-O0`). The 256B table is one load per subject char regardless of needle size.
2. **Needle length is the decider.** claws5's 10/26/36-char needles make B/C pay per needle char → 3.5–4× A. treebank's 2/4-char needles shrink the gap to +12–30%.
3. **C ≈ B throughout** — the lean-convention leaf call costs about the same as the emitted inner loop; the per-needle-char iteration is the cost, not the transfer. The s126 "no C-ABI dance" design did its job.
4. **treebank is NOT cset-guts-bound**: flavors differ mildly while SPITBOL stays 2.2× ahead — the gap lives in the recursive `*group`/ARBNO backtracking machinery (seam traffic, ζ churn: SPD-2/BP-9 territory), not in span/break/notany.
5. **Method note:** first cold runs measured 279/1041 ms (page-in + cold caches); a warm 1-rep probe even showed B/C "faster" on treebank — the 5-rep interleaved medians reversed it. The s108 interleaved-medians rule caught a would-be false conclusion again.

**Decision (Lon "all your choices"):** default stays **UNROLL**; `ZC_LIT_GUTS` retained as proving scaffold (same pattern as the ZC_PORT flavor set — Lon's keep-or-retire ruling welcome).

## EVIDENCE OF EMITTED SHAPES (static .s, claws5 SPAN 36-char site)

A: `lea rdi,[rip+.C2]` + ×4-unrolled `movzx esi,[r13+rcx]; cmpb [rdi+rsi],0; je ω̂; add ecx,1`.
B: `lea r8,[rip+.S3]; mov r9d,36` + outer subject loop (r13/r14/r15) + inner `movzx edi,[r8+rdx]; cmp esi,edi`.
C: `mov edi,r14d; lea rsi,[rip+.S3]; mov edx,36; call rt_sg_scan_nonmember@PLT`.

## GATES (final tree, default flavor)

sno smokes 7/7×2 · crosscheck m3 302/8 m4 302/6 DIVERGE=0 (fail set byte-identical to s127 watermark: 140/141 + 1020/1021 + 214/215/216) · `--compile` .s byte-identical to HEAD on the pair · regen scripts (benchmark/feature/demo): **zero changed artifacts**.

## ADDENDUM (same session, Lon follow-up): A∞ UNLIMITED CHAIN + TIME() SLURP/MATCH SPLIT + WALL

**Lon's question answered plainly: the s125-machinery "UNROLL" flavor did NOT unroll cset membership without limit** — 100% of *sites* took the literal machinery, but inside it `ZC_CSET_CHAIN_MAX=3` routed >3-char csets to the 256B table (subject step unrolled ×4). The unlimited-chain variant is a build flag away: **A∞ = `-DZC_CSET_CHAIN_MAX=256`** (zero code changes; every literal cset a full compare chain, claws5's 36-char cset = 36 inline compares per subject char-step ×4 unroll).

**Instrumentation:** TIME() split (manual p.242: ms since execution start, Unix = CPU compute time; SCRIP `bn_time` = `clock()` — same semantics, apples-to-apples). Wrappers `/tmp/bench/{claws5,treebank}-match-t.sno`: t0→slurp→t1→K-loop match→t2, print slurp/match ms. In-program CPU numbers are immune to the container's wall-clock contention (observed 2–3× wall swings between quiet and loaded windows; the in-program splits cross-validate the earlier slope method within ~10% on every cell).

**GRID (medians of 5 interleaved reps; per-match = match/K; SCRIP `-O0`; now in SCRIP README.md § SNOBOL4 Benchmark):**

| program | engine | slurp | match | per-match | wall |
|---|---|--:|--:|--:|--:|
| claws5 (K=200) | A m3 / m4 | 14/14 | 40/39 | 0.200/0.195 | 69/65 |
| claws5 | A∞ m3 / m4 | 14/14 | 65/64 | 0.325/0.320 | 96/89 |
| claws5 | B m3 / m4 | 14/14 | 143/141 | 0.715/0.705 | 172/171 |
| claws5 | C m3 / m4 | 14/14 | 149/144 | 0.745/0.720 | 180/174 |
| claws5 | sbl | 13 | 45 | 0.225 | 68 |
| treebank (K=50) | A m3 / m4 | 79/78 | 95/84 | 1.900/1.680 | 213/204 |
| treebank | A∞ m3 / m4 | 76/77 | 88/96 | 1.760/1.920 | 209/213 |
| treebank | B m3 / m4 | 78/76 | 109/95 | 2.180/1.900 | 227/211 |
| treebank | C m3 / m4 | 77/76 | 102/103 | 2.040/2.060 | 223/218 |
| treebank | sbl | 31 | 39 | 0.780 | 85 |

**Readings (extends the main finding):**
1. **The chains-beat-strchr report CONFIRMED and SUPERSEDED.** A∞ (0.32) beats B/C (0.71–0.75) — a full inline chain beats even the R13/R15-aware per-char INLINE loop and lean CALL leaf, so it certainly beat old strchr-per-char. **But the 256B table (0.195–0.200) beats the 36-compare chain by 60%** — one load per subject char vs O(cset) compares. The relationship changed exactly as suspected: our INLINE/CALL leapfrogged strchr, and the table leapfrogs the chain at long csets. Chain-≤3-then-table stands as the right ladder (s127's A/B already showed 1–3-char chains beat the table's lea+load setup).
2. **SCRIP wins claws5 at the PROCESS level too**: wall 65 vs sbl 68 ms — compile-and-run parity with optimized SPITBOL at `-O0` runtime, per-match 13% faster.
3. **treebank slurp is a real lead**: SCRIP 76–79 ms vs sbl 31 for 100 KB of `src = src line CHAR(10)`; claws5's CHAR-free slurp is at parity (14 vs 13). The delta is the per-line `CHAR(10)` builtin dispatch in concat position — s127's fold covers cset/pattern-arg position only. Folding CHAR(k) literals in general expression position would cut treebank slurp ~2.5×.
4. treebank match flavors span only 1.68–2.18 (order jitters m3 vs m4) — re-confirms the 2.2–2.6× sbl gap lives in `*group`/ARBNO backtracking machinery, not cset guts.

## ADDENDUM 2 (same session): VARIANT R — RANGE CHAINS (Lon's 4th variant)

**Design (Lon):** each literal cset coalesces into maximal contiguous byte RANGES at emit; membership = a chain of range tests. Landed as `ZC_LIT_GUTS_RANGE` (=3): same unrolled subject-step body as UNROLL, membership swapped — single-byte run `cmp esi,b; je HIT` (2 inst), multi-byte run the unsigned-sub trick `mov eax,esi; sub eax,lo; cmp eax,hi−lo; jbe HIT` (4 inst; eax verified dead at every use site in span/break/any/notany). `SPAN('0123456789' &UCASE)` = 2 range tests instead of a 36-compare chain or a 256B table load. `jbe` already wired for internal labels (x86_jcc_op + XK_ILBL dispatch — zero encoder additions). Default byte-identity re-gated (.s diff), smokes 7/7×2, crosscheck 302/8 · 302/6 DIVERGE=0, regen scripts no-op.

**GRID rows (medians of 5 interleaved reps, same harness; sbl control identical across windows at 0.780/0.230 — cross-window comparability held):**

| program | engine | slurp | match | per-match | wall |
|---|---|--:|--:|--:|--:|
| claws5 | R m3 / m4 | 13/13 | 45/44 | 0.225/0.220 | 73/69 |
| treebank | R m3 / m4 | 75/74 | 75/78 | 1.500/1.560 | 193/191 |

**THE LADDER (claws5-class csets, ≥4 chars): table 0.195 > RANGE 0.220 (≈ SPITBOL 0.230) > full chain 0.320 > INLINE 0.705 ≈ CALL 0.720.** Ranges beat the full chain by 45% and tie optimized SPITBOL — Lon's construction is real — but the L1-hot 256B table's single load-compare-branch still edges 1–2 range tests' extra branch each by ~15%. On treebank, R = 1.50–1.56, a hair under A (within noise) — guts-insensitivity re-confirmed a third time. **Default stays chain-≤3-then-table**; R retained in the scaffold (a future refinement: range-count-aware selection — 1-range csets like SPAN(&DIGITS) at 4 inst/char with zero memory traffic may win on cache-cold or SMT-contended workloads the L1-hot microbench can't see).

**TRT note (Lon's question):** x86 has no TRT; XLAT translates without testing. The table probe `movzx esi,[r13+rcx]; cmpb [rdi+rsi],0; jcc` IS a 2-instruction software TRT step. The true modern TRT is **SSE4.2 PCMPISTRI "ranges" mode** — 16 subject bytes per instruction against up to 8 range pairs — the natural next rung for SPAN/BREAK-guts (SPD-1-adjacent; candidate variant 5).
