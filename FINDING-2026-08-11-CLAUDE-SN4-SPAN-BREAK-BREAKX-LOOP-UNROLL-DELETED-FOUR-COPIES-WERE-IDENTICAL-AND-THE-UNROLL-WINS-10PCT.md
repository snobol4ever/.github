# FINDING 2026-08-11 — CLAUDE SN4 · SPAN/BREAK/BREAKX LOOP UNROLL DELETED; FOUR COPIES WERE TEXTUALLY IDENTICAL; THE UNROLL WINS ~10% ON CLAWS5

## Summary

The `ZC_SPAN_LIT_UNROLL`/`ZC_UNROLL_FACTOR=4` loop unroll in `bb_match_{span,break,breakx}.cpp` was deleted by Lon directive.  The four unrolled copies were **textually identical** — unlike a canonical loop unroll, no displacements were folded, no per-copy specialization was applied, no increments were hoisted.  The membership test (256-byte table lookup) was not changed.  The `ZC_UNROLL_FACTOR` constant had no recorded A/B behind it ("s125 hardcoded 4; lifted here, s125's owed switch" — `zeta_choices.h`).

## The deleted shape

Each of the four identical copies (SPAN `n12_match_span_α`, example):
```
cmp   ecx, r15d              ; bounds check (EVERY copy)
jge   .Lx35_1
movzx esi, byte ptr [r13+rcx] ; load subject byte
cmp   byte ptr [rdi+rsi], 0   ; 256B table membership test
je    .Lx35_1
add   ecx, 1                  ; advance (EVERY copy — no hoisting)
```
After the 4th copy: `jmp .Lx35_0`.  The back-edge is eliminated 3 of every 4 characters; nothing else changes.

## Why this is NOT the usual unroll benefit

A canonical unroll on a literal string comparison has a known trip count and can fold `[r13+rcx]`→`[r13+rcx+1]`→`[r13+rcx+2]`→`[r13+rcx+3]`, hoisting the `add` to `add ecx,4` once.  Here the exit is data-dependent (any copy can exit), so the trip count is unknown and the `add ecx,1` must be repeated in every copy — the loop is unrolled in shape only.  The real literal matcher (`bb_match_lit.cpp`) calls `memcmp`; it does not use this machinery at all.

## Measurement (interleaved A/B, setarch -R, RT_OPT=-O0, K=200, claws5-match.sno)

| arm | reps | ms (drop warm-up) |
|-----|------|--------------------|
| U4 (unroll=4, before) | 10 | 28, 28, 28, 29, 28, 28, 29, 29, 29, 28 — **median 28–29** |
| FIX (unroll=1, after) | 10 | 35, 31, 31, 32, 31, 31, 33, 31, 31, 31 — **median 31** |

**The unroll wins ~10% on this workload.**  Positive control: harness reproduced the README's s128 recorded `39 ms` median for flavor A before either number was quoted (pre-regen run at 39–45 ms, median 40).

The instrument was confirmed genuine: both arms verified by emission fingerprint (span char-steps = 4 vs 1); both `.so` files have distinct md5 (`rt_U4.so` 8e33e9d9, `rt_FIX.so` f7abfd69).  The earlier timing pair (reported in session before this FINDING) was made against an ambiguous `.so` and was discarded — the `scrip` binary is a thin driver, the templates live in `out/libscrip_rt.so`, and the three saved `scrip` files were byte-identical while loading different `.so` content.

## Why the win is probably not loop-back elimination

claws5's separator SPAN (`' ' CHAR(10)`) is typically 1–2 characters.  The SPAN on `'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'` runs longer on token bodies.  If the unroll wins 10%, it is more likely µop-cache / LSD effects (a 7-instruction loop streams from the loop stream detector; ~25 instructions across 3–4 fetch lines does not, and the subject-byte load and table load are independent across copies, allowing more concurrent outstanding loads in the out-of-order window).  This hypothesis is unverified — it is the most plausible mechanistic explanation given the data.

## Correctness

By-set diff across 622 programs covered by both sweeps (707 total corpus; U4 sweep terminated early): **0 regressions, 0 improvements, 0 new timeouts.**  `claws5-match` and `claws5-match-fence` both IDENT to `.ref` (mode 3).

## Code changes

- `bb_match_span.cpp`: `sp_unroll()` deleted; call site replaced with `sp_char(0) + x86("jmp", L(0))`.
- `bb_match_break.cpp`: `bk_unroll()` deleted; call site replaced with `bk_char() + x86("jmp", L(0))`.
- `bb_match_breakx.cpp`: `bx_unroll()` deleted; two call sites replaced with `bx_char(1,0) + x86("jmp", L(0))` and `bx_char(3,1) + x86("jmp", L(2))`.
- `zeta_choices.h`: `ZC_SPAN_LIT_UNROLL` and `ZC_UNROLL_FACTOR` deleted (zero remaining users verified by grep); stale header comment updated.  `ZC_LIT_GUTS_UNROLL` (the flavor name for the table/chain membership mechanism) is a distinct axis and was not changed.
- 9 insertions, 16 deletions, 4 files.

## What this does NOT fix

BREAKX was unexercised — neither `claws5-match` nor `claws5-match-fence` contains BREAKX.  The by-set sweep covered the full corpus but the correctness claim for BREAKX rests on that broader sweep only, not a targeted witness.

## Note on `ZC_LIT_GUTS_UNROLL` naming

The name is now misleading (the unroll is gone but the constant names a membership-mechanism flavor, not a loop-unroll shape).  A rename is cheap and would prevent the next reader from spending time on it.
