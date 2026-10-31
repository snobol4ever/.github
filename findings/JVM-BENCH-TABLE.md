# JVM-BENCH-TABLE -- snobol4jvm against pristine SPITBOL and CSNOBOL4, in instructions

Measured 2026-10-31 18:47 CDT by bench_snobol4_jvm_table.sh -n 3; snobol4jvm 6f91618, load 5.68 5.02 5.42; corpus 0ffb9bd12.
Basis: perf stat -e instructions:u (CEO-2035), median of 3 runs; WORK is the kernel's total less an empty program's. SPITBOL is /home/resources/spitbol-bench-oracle/sbl, CSNOBOL4 is /home/resources/csnobol4/snobol4 (output must equal the kernel's .ref).

| kernel | jar work (G) | sbl work (M) | csnobol4 work (M) | jar / sbl | jar / csnobol4 | jar overhead (G) | note |
|---|---|---|---|---|---|---|---|
| arith_loop | 1.601 | 0.232 | 1.331 | 6902.3 | 1202.1 | 16.982 | jar spread 4.02% |
| arith_loop_twin | 22.414 | 77.207 | 365.424 | 290.3 | 61.3 | 16.645 | jar spread 3.40% |
| array_sum | 6.704 | 5.128 | 32.108 | 1307.4 | 208.8 | 16.541 | jar spread 0.99% |
| eval_fixed | 6.494 | 1.238 | 4.140 | 5245.1 | 1568.6 | 16.765 | jar spread 3.50% |
| fibonacci | 16.878 | 2.602 | 11.694 | 6487.5 | 1443.3 | 16.534 | jar spread 2.77% |
| fib_recur | 272.836 | 47.008 | 208.151 | 5804.1 | 1310.8 | 16.994 | jar spread 0.35% |
| func_call | 2.970 | 0.422 | 1.976 | 7045.7 | 1503.4 | 16.770 | jar spread 2.80% |
| ident_call1 | 1.728 | 0.287 | 1.614 | 6012.6 | 1070.2 | 16.854 | jar spread 6.11% |
| ident_call2 | 1.650 | 0.284 | 1.579 | 5816.4 | 1045.3 | 16.863 | jar spread 0.15% |
| indirect_dispatch | 2.064 | 0.320 | 1.806 | 6455.2 | 1142.6 | 17.053 | jar spread 3.25% |
| mixed_workload | 3.390 | 0.375 | 1.491 | 9037.0 | 2274.4 | 16.809 | jar spread 2.36% |
| name_indirection | 5.038 | 9.024 | 50.650 | 558.2 | 99.5 | 16.905 | jar spread 0.35% |
| op_dispatch | 3.325 | 0.473 | 2.706 | 7024.3 | 1229.0 | 16.526 | jar spread 12.80% |
| pattern_bt | 4.697 | 1.681 | 7.704 | 2793.9 | 609.7 | 16.784 | jar spread 1.34% |
| roman | 5.528 | 1.210 | 8.465 | 4568.7 | 653.1 | 17.036 | jar spread 8.35% |
| string_concat | 1.297 | 0.239 | 1.813 | 5415.0 | 715.1 | 16.745 | jar spread 6.43% |
| string_concat_twin | 3.178 | 1.119 | 7.019 | 2839.8 | 452.7 | 17.033 | jar spread 3.24% |
| string_manip | 1.916 | 0.517 | 2.458 | 3705.2 | 779.4 | 16.581 | jar spread 2.49% |
| string_pattern | 3.476 | 0.754 | 3.871 | 4606.9 | 897.8 | 17.053 | jar spread 3.33% |
| table_access | 6.327 | 7.122 | 94.156 | 888.5 | 67.2 | 16.876 | jar spread 2.75% |
| table_variety | 6.370 | 4.414 | 22.284 | 1443.2 | 285.9 | 16.510 | jar spread 4.40% |
| test_icon | 2.813 | 0.251 | 0.292 | 11195.8 | 9639.0 | 17.088 | jar spread 4.43% |
| var_access | 2.710 | 0.553 | 2.953 | 4898.3 | 917.6 | 16.810 | jar spread 2.52% |
| TOTAL (counted kernels) | 385.403 | 162.460 | 835.684 | 2372.3 | 461.2 | | 23 kernels counted, 0 refused |

Empty-program overhead: jar see the column; csnobol4 0.577 M.

## How to read it

- **A multiple here is the cost of running one small program once.** Each SnoBench kernel is millisecond-sized, so the jar's WORK is mostly one-time cost (parsing the source with instaparse, compiling, class loading, the first run, the JIT), not loop iterations; a board entry pays exactly this, which is why the multiples run from the hundreds to above ten thousand. The kernels that iterate longest read lowest (arith_loop_twin, name_indirection, table_access).
- **OVERHEAD is a separate, larger number.** An empty program costs the jar about 16.5 to 17 G instructions on every run (a bare JVM is 0.06 G, a bare Clojure runtime 4.2 G, SPITBOL and CSNOBOL4 under 1 M): that fixed cost is the first target of row jvm-speed-the-fixed-start-up-of-the-jar-is-halved.
- **Steady-state speed is not in this table.** Hand-run scaled loops on 2026-10-31 (wall clock, load 10, jar 6f91618) read 12M arithmetic iterations at 170 s or more against 0.96 s on SPITBOL and 4.3 s on CSNOBOL4, 3M pattern matches at 80 s against 0.71 s and 1.7 s, 40k string concatenations at 6.7 s against 0.27 s and 1.4 s. Those are not instruction counts and not a board.
- **Noise.** The jar's total moves 0.2 to 13 percent run to run (the note column); two multiples within 15 percent of each other are not different. SPITBOL's count is stable to a few instructions; CSNOBOL4 is about five times SPITBOL's work in total.
- **Correctness first.** A kernel whose output differs from the oracle's is REFUSED, never counted; CSNOBOL4's output must equal the kernel's .ref.
