# Speed measurement: the reference

Verified 2026-11-07 against the harness and the box. Consolidated from ARCH-PERF-TOOLING (2026-08-28) and ARCH-BENCH-CAMPAIGN-README-TABLES, retired (`.github/RETIRED-ARCH-PAGES.tsv`); both predate CEO-1912, so their wall-clock and three-angle method is history: the count of § 2 of .github/skills/speed-measurement/SKILL.md replaced it.

## 1. The instruments by question

| question | instrument |
|---|---|
| how many instructions does the program's work cost, against SPITBOL | `util_instr_count.sh --vs sbl` |
| how does a count grow with input size | `bench_ir_slope.sh`, `bench_prolog_ir_slope.sh`, `bench_parser_ir_slope.sh` |
| a language's bar against its rival | `bench_snobol4_bar.sh`, `bench_icon_bar.sh`, `bench_icon_ir_bar.sh`, `bench_prolog_bar.sh`, `bench_prolog_ir_bar.sh`, `bench_pascal_bar.sh`, `bench_raku_bar.sh` |
| where the time goes inside the collector | `util_gc_share_callgrind.sh`, `util_collection_asm_share.sh` |
| how many calls from emitted Prolog reach a C family | `bench_prolog_call_census.sh REGEX` |
| a budget a landing may not exceed | `test_gate_instr_budget.sh`, the gc instruction-budget gate |
| a process's own resource use | `SCRIP/out/bench_rusage` |

## 2. The benchmark populations

`corpus/benchmarks/<lang>/` (the only tree beside the demos with committed `.s`), each kernel with its ref; the Icon set's library modules (`post.icn`, `options.icn`, `shuffle.icn`) are not programs and must be precompiled for icont, or five real programs falsely read as icont failures; the Icon program count excludes them. The README tables of the repos are rendered from the measurements, never typed.

## 3. History that still explains an old number

- The 2026-08-28 two-aspect law (command-line elapsed beside in-program brackets, never in one column) and the three-angle method (fixed time, fixed iterations, a process wrapper) were the presentation rules for wall-clock numbers; a number taken that way is a clock reading and cannot be compared with a count.
- `SCRIP_BBPROF` was a dead instrument in mode 4 (2026-08-28).
