# JVM-BENCH-TABLE -- snobol4jvm against pristine SPITBOL and CSNOBOL4, in instructions

Measured 2026-10-31 20:59 CDT by bench_snobol4_jvm_table.sh -n 3; snobol4jvm 4cd6529, load 7.92 5.08 5.41; corpus 0ffb9bd12.
Basis: perf stat -e instructions:u (CEO-2035), median of 3 runs; WORK is the kernel's total less an empty program's. SPITBOL is /home/resources/spitbol-bench-oracle/sbl, CSNOBOL4 is /home/resources/csnobol4/snobol4 (output must equal the kernel's .ref).

| kernel | jar work (G) | sbl work (M) | csnobol4 work (M) | jar / sbl | jar / csnobol4 | jar overhead (G) | note |
|---|---|---|---|---|---|---|---|
| arith_loop | 1.808 | 0.232 | 1.332 | 7795.0 | 1357.1 | 6.703 | jar spread 0.67% |
| arith_loop_twin | 21.420 | 77.207 | 365.424 | 277.4 | 58.6 | 6.680 | jar spread 1.97% |
| array_sum | 7.416 | 5.128 | 32.108 | 1446.1 | 231.0 | 6.648 | jar spread 3.01% |
| eval_fixed | 7.803 | 1.238 | 4.140 | 6302.2 | 1884.7 | 6.386 | jar spread 3.91% |
| fibonacci | 5.882 | 2.602 | 11.695 | 2260.9 | 503.0 | 6.581 | jar spread 1.36% |
| fib_recur | 17.352 | 47.008 | 208.151 | 369.1 | 83.4 | 6.718 | jar spread 2.70% |
| func_call | 2.913 | 0.422 | 1.976 | 6910.4 | 1474.4 | 6.735 | jar spread 6.08% |
| ident_call1 | 2.010 | 0.287 | 1.614 | 6996.3 | 1245.2 | 6.521 | jar spread 4.82% |
| ident_call2 | 2.092 | 0.284 | 1.579 | 7370.5 | 1324.2 | 6.707 | jar spread 4.47% |
| indirect_dispatch | 2.389 | 0.320 | 1.806 | 7473.4 | 1322.7 | 6.510 | jar spread 2.92% |
| mixed_workload | 3.060 | 0.375 | 1.491 | 8153.9 | 2052.3 | 6.620 | jar spread 4.09% |
| name_indirection | 6.306 | 9.024 | 50.650 | 698.8 | 124.5 | 6.557 | jar spread 2.49% |
| op_dispatch | 2.120 | 0.473 | 2.706 | 4478.2 | 783.5 | 6.743 | jar spread 5.05% |
| pattern_bt | 5.005 | 1.681 | 7.704 | 2976.8 | 649.6 | 6.455 | jar spread 2.42% |
| roman | 4.290 | 1.210 | 8.465 | 3545.9 | 506.8 | 6.678 | jar spread 2.04% |
| string_concat | 2.016 | 0.239 | 1.813 | 8421.0 | 1111.5 | 6.489 | jar spread 5.62% |
| string_concat_twin | 2.833 | 1.119 | 7.019 | 2531.9 | 403.6 | 6.381 | jar spread 8.36% |
| string_manip | 1.839 | 0.517 | 2.459 | 3556.3 | 748.0 | 6.806 | jar spread 1.69% |
| string_pattern | 3.457 | 0.754 | 3.871 | 4582.3 | 892.9 | 6.444 | jar spread 1.23% |
| table_access | 6.795 | 7.122 | 94.156 | 954.1 | 72.2 | 6.558 | jar spread 2.15% |
| table_variety | 6.267 | 4.414 | 22.284 | 1419.9 | 281.2 | 6.160 | jar spread 2.71% |
| test_icon | 2.787 | 0.251 | 0.292 | 11091.0 | 9544.8 | 6.700 | jar spread 5.75% |
| var_access | 3.049 | 0.553 | 2.953 | 5511.2 | 1032.3 | 6.660 | jar spread 4.66% |
| TOTAL (counted kernels) | 120.908 | 162.460 | 835.689 | 744.2 | 144.7 | | 23 kernels counted, 0 refused |

Empty-program overhead: jar see the column; csnobol4 0.577 M.

## How to read it

- **A multiple here is the cost of running one small program once.** Each SnoBench kernel is millisecond-sized, so the jar's WORK is mostly one-time cost (parsing the source with instaparse, compiling, class loading, the first run, the JIT), not loop iterations; a board entry pays exactly this. The kernels that iterate longest read lowest (arith_loop_twin, fib_recur, name_indirection, table_access).
- **OVERHEAD is a separate number.** An empty program costs the jar about 6.2 to 6.8 G instructions on every run (16.5 to 17 G before 2026-10-31's compiled grammar, the launcher's -XX:CompileThresholdScaling=4 and -XX:-DontCompileHugeMethods; a bare JVM is 0.06 G, a bare Clojure runtime 4.2 G, SPITBOL and CSNOBOL4 under 1 M). Every board entry pays it.
- **Steady-state speed is not in this table.** Scaled loops, instruction counts on 2026-10-31 (jar 4cd6529 through the launcher; sbl, csnobol4): 1.5M arithmetic iterations 117.5 G against 0.67 G and 2.73 G (176 and 43 times); 300k pattern matches 116.8 G against 1.72 G and 2.29 G (68 and 51 times); 40k string concatenations 15.9 G against 0.07 G and 0.63 G; a 40k-entry table 19.4 G against 0.04 G and 20.1 G (parity with csnobol4); fib(24), 75k calls, 24.7 G against 0.05 G and 0.21 G (525 and 118 times; 281 G before RETURN stopped reading a stack trace). Not a board.
- **Noise.** The jar's total moves 0.2 to 13 percent run to run (the note column); two multiples within 15 percent of each other are not different. SPITBOL's count is stable to a few instructions; CSNOBOL4 is about five times SPITBOL's work in total.
- **Correctness first.** A kernel whose output differs from the oracle's is REFUSED, never counted; CSNOBOL4's output must equal the kernel's .ref.
