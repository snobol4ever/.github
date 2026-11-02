---
name: speed-measurement
description: How speed is measured and when it may be worked: a benchmark is an instruction count, never a wall clock (CEO-1912); speed opens only for SNOBOL4 and Icon (CEO-2035) after completeness and correctness (CEO-1886); util_instr_count.sh's OVERHEAD and WORK, the benchmark oracle, callgrind and perf as profilers, the quiet slice for the rare clock, the bench_* scripts, the kernel convention and the README tables. Load it before a speed row, a benchmark landing, a profile, or any number that claims one engine is faster.
---

# Speed measurement

Detail is in `reference.md` beside this file.

## 1. The rulings

- **The order of work** (CEO-1886): completeness, then correctness, then speed. Placement is correctness (CEO-1895).
- **Speed only for SNOBOL4 and Icon, by instruction count** (CEO-2035; Lon 2026-10-30: "Yes, let's move on to performance for SNOBOL4 and Icon."). Prolog, Pascal and Raku have no speed rows until Lon opens them. The ports' speed rows rest under Lon's hold (CEO-2049).
- **A benchmark is an instruction count, never a wall clock** (CEO-1912; Lon 2026-10-22: "Forget about benchmarking based on wall clock; instead use instruction counts from calgrind and other techniques."). A count does not move with the box's load, so it runs at any time. A clock is taken only inside `util_quiet_slice.sh` (a reserved slice), and is never the basis of a row.
- **A benchmark is a test**: every kernel has a ref and its answer is diffed before its count means anything; a fast wrong answer is a defect. The kernel is a pristine source; the harness generates the wrapping around it.
- **No `-O2`**: the runtime builds at `RT_OPT=-O0`; a speed claim never rides a compiler flag.

## 2. The instrument

```bash
bash ../harness/scripts/util_instr_count.sh [-n N] [--vs sbl] <engine> <program.sno> [< input]
#   engine: sbl (the benchmark oracle, /home/resources/spitbol-bench-oracle/sbl -bf), scrip (mode 3), scrip4 (mode 4, compile not counted), dotnet, jvm
```

It counts `instructions:u` with perf stat for the process and every thread it starts, prints two numbers, OVERHEAD (the engine on an empty program) and WORK (the program less OVERHEAD), each the median of N runs with its spread, and with `--vs sbl` the multiple of WORK against SPITBOL (2.000x means half of sbl's count). Each engine runs at the program's declared sizes and oracle arguments, so a count is never taken from an oracle that died of a size error.

## 3. Profiling (to find the cost, not to grade it)

- Do the analysis in mode 4 (a real ELF); mode 3's slab shows as unknown to the tools.
- SCRIP is not a call and return machine: ports are wired into jumps, so a flame graph of the slab is flat. Edge profiling is the model: `callgrind --collect-jumps=yes`, joined to `--dump-bb`'s box graph.
- `harness/scripts/profile_callgrind.sh`; perf is `/usr/lib/linux-tools-6.8.0-138/perf` (never `/usr/bin/perf`, a dispatching shim that refuses on this kernel).
- Field facts: callgrind counts `rep movsq` as one Ir per quad moved; `--main-stacksize=2000000000` on deep recursive demos or a crashed run writes a plausible partial profile; `--branch-sim` cannot see return-stack mispredicts.
