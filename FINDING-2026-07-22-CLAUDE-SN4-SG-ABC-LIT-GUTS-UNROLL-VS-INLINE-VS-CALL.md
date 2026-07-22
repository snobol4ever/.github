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
