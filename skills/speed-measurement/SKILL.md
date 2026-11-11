---
name: speed-measurement
description: How speed is measured: a benchmark is an instruction count, never a wall clock; util_instr_count.sh, callgrind and perf, the quiet slice, the bench_* scripts. REQUIRED by the skill gate before editing util_instr_count.sh or a bench script.
---

# Speed measurement

Detail is in `.github/skills/speed-measurement/reference.md`, beside this file.

## 1. The rulings

- **The order of work** (CEO-1886): completeness, then correctness, then speed. Placement is correctness (CEO-1895).
- **Speed only for SNOBOL4 and Icon, by instruction count** (CEO-2035; Lon 2026-10-30: "Yes, let's move on to performance for SNOBOL4 and Icon."). Prolog, Pascal and Raku have no speed rows until Lon opens them. The ports' speed rows rest under Lon's hold (CEO-2049).
- **A benchmark is an instruction count, never a wall clock** (CEO-1912; Lon 2026-10-22: "Forget about benchmarking based on wall clock; instead use instruction counts from calgrind and other techniques."). A count does not move with the box's load, so it runs at any time. A clock is taken only inside `util_quiet_slice.sh` (a reserved slice), and is never the basis of a row.
- **A benchmark is a test**: every kernel has a ref and its answer is diffed before its count means anything; a fast wrong answer is a defect. The kernel is a pristine source; the harness generates the wrapping around it.
- **No `-O2`**: the runtime builds at `RT_OPT=-O0`; a speed claim never rides a compiler flag.
- **A multiple is reference over ours, written 2.00x**, and never carries "faster" or "slower" (below 1.00x is slower; "0.666 slower" says nothing). Only a percentage takes the English word: 10% faster is 1.10x.

## 2. The instrument

```bash
bash ../harness/scripts/util_instr_count.sh [-n N] [--vs sbl] <engine> <program.sno> [< input]
#   engine: sbl (the benchmark oracle, /home/resources/spitbol-bench-oracle/sbl -bf), scrip (mode 3), scrip4 (mode 4, compile not counted), dotnet, jvm
```

It counts `instructions:u` with perf stat for the process and every thread it starts, prints two numbers, OVERHEAD (the engine on an empty program) and WORK (the program less OVERHEAD), each the median of N runs with its spread, and with `--vs sbl` the multiple of WORK against SPITBOL (2.000x means half of sbl's count). Each engine runs at the program's declared sizes and oracle arguments, so a count is never taken from an oracle that died of a size error.

## 3. Profiling (to find the cost, not to grade it)

- Do the analysis in mode 4 (a real ELF); mode 3's slab shows as unknown to the tools.
- SCRIP is not a call and return machine: ports are wired into jumps, so a flame graph of the slab is flat. Edge profiling is the model: `callgrind --collect-jumps=yes`, joined to `--dump-bb`'s box graph.
- `harness/scripts/profile_callgrind.sh`.
- PERF, MEASURED 2026-11-04 (hq_snobol4, after a wasted detour): `/usr/bin/perf` is Ubuntu's dispatching shim; it execs `/usr/lib/linux-tools/$(uname -r)/perf`, and for kernel 6.17.0-1032-oem that directory holds no perf (package `linux-oem-6.17-tools-6.17.0-1032` ships acpidbg, cpupower, rtla, turbostat and no perf). So the shim prints `WARNING: perf not found for kernel 6.17.0-1032 ... install linux-tools-6.17.0-1032-oem linux-cloud-tools-6.17.0-1032-oem` although `linux-tools-6.17.0-1032-oem` is already installed (`dpkg -l`). ⛔ DO NOT apt install anything (the binary is not in the package; nothing to install cures it) and DO NOT conclude perf is unavailable or fall back to a clock: the counter works.
- The real perf is `/usr/lib/linux-tools-6.8.0-138/perf` (perf 6.8.12): `perf stat -x, -e instructions:u CMD` counts correctly on the 6.17 kernel (`kernel.perf_event_paranoid` is 1). Since 2026-11-04 plain `perf` works for every seat too: `/home/satirical/.local/bin/perf` is a six-line sh launcher ahead of `/usr/bin` on PATH (one unix user, one PATH); it execs `/usr/lib/linux-tools/$(uname -r)/perf` if one ever exists, else the newest `/usr/lib/linux-tools-*/perf`. CHECK: `perf --version` must print `perf version 6.8.12`. If it prints the WARNING, `type -a perf` and recreate the launcher; do not install packages. The harness (`util_instr_count.sh`, the `bench_*` scripts) finds a working perf itself and needs none of this.
- WHY THIS NOTE IS NOT THE CURE: this skill already said `never /usr/bin/perf` and a seat still lost time to the shim's message, because a seat that types `perf` does not open a skill. What cures it is the launcher on PATH (plain `perf` works) and the line every seat's CLAUDE.md now carries (digest parts BUILD*.md, applied to all 19 roots 2026-11-04); this paragraph is reference for the cause.
- Field facts: callgrind counts `rep movsq` as one Ir per quad moved; `--main-stacksize=2000000000` on deep recursive demos or a crashed run writes a plausible partial profile; `--branch-sim` cannot see return-stack mispredicts.
