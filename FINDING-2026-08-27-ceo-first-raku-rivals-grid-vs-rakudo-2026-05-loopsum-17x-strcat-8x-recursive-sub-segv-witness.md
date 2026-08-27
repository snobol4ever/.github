# FINDING 2026-08-27 (ceo): first Raku rivals grid vs Rakudo 2026.05 — loopsum 17.4x, strcat 8.3x (TOTAL basis); recursive-sub SEGFAULT witness banked

**Context:** Lon's build-and-benchmark order. Rakudo v2026.05 on MoarVM 2026.05 built sudo-free at /home/resources/rakudo-local (release tarball + --gen-moar; the GitHub zip drops lack the nqp-configure submodule — two failed attempts recorded so nobody retries). `rakudo_bin()` prefers it. SCRIP at -O0 per law; Rakudo at its released defaults. Single-run wall clock, work-scaled kernels, both arms same basis.

**Shared axes: wall clock · TOTAL (startup included, both arms) · m3 --run · × vs Rakudo 2026.05**
| kernel | scrip | rakudo | × |
|---|---|---|---|
| loopsum (3M-iter integer while) | 27ms | 471ms | **17.4x** |
| strcat2 (200k string concat) | 20ms | 165ms | **8.3x** |
| startup (say 1) | 7ms | 118ms | (context, not a kernel) |

Outputs AGREE on both kernels (loopsum 4499998500000; strcat2 200000). SLOPE view (startup subtracted, NEVER to share a column with the totals above): loopsum ≈17.6x, strcat2 ≈3.6x — the strcat TOTAL multiple is startup-flattered; the slope is the honest per-work number there.

**⛔ WITNESS: recursive Raku sub SEGFAULTS m3 (rc=139)** — `sub fib($n) { if $n < 2 { return $n; }; return fib($n-1) + fib($n-2); } say fib(24);` dumps core; Rakudo prints 46368. Non-recursive subs pass (the RK-ZC-2 class is cured); RECURSION is a distinct open shape — consistent with the C-made-frame archaeology (per-activation frames not yet carried). Row `raku-recursive-sub-segv` minted with this witness inline.

**Caveats per FACT RULE:** two kernels is a smoke-grid, not the campaign; the three-angle harness owns quotable README numbers; Rakudo arm labeled 2026.05 (rakudo-local), never the apt 2022.12.
