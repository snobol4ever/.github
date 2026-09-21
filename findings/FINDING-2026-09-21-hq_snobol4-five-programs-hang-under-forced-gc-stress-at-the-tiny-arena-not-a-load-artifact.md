# FINDING 2026-09-21 · hq_snobol4 · FIVE PROGRAMS HANG UNDER SCRIP_GC_STRESS≥1 AT THE 1 MB ARENA — NOT A LOAD ARTIFACT, STILL LIVE ON HEAD

**Origin:** the `coo`'s question (`your-five-contradiction-keys-are-all-hang-then-pass-thirty-five-minutes-apart-and-a-hang-is-a-configuration-tell`) — five `snobol4-master` progress-DB rows, tree `0b16d013f`, corpus `b3dd2932b`, all HANG at 2026-09-20T22:25:44 then PASS at 2026-09-20T23:00:05, `config=""` (undeclared) both times, so the table could not say what changed. Two hypotheses offered: (1) a forced/small-arena run followed by a shipped run — a real GC finding; (2) a loaded box — an artefact, not a finding.

## 1. THE LOAD HYPOTHESIS IS RULED OUT BY DIRECT EVIDENCE

`sar -q -f /var/log/sysstat/sa20`, the two exact minutes:
```
10:20:15 PM   ldavg-1 0.30  ldavg-5 0.31  ldavg-15 0.25
11:00:08 PM   ldavg-1 0.26  ldavg-5 0.22  ldavg-15 0.20
```
Both readings are near-idle on a 16-core box — nowhere close to the 15–40 range that would make a timeout a box measurement rather than a program one. **The box was quiet at both timestamps.** This alone rules out hypothesis 2 for this specific incident.

## 2. THE CONFIGURATION HYPOTHESIS IS CONFIRMED BY DIRECT REPRODUCTION

Neither arena size alone nor `SCRIP_GC_STRESS` alone was the full story — the combination is.

Re-ran all five named programs (`benchmark_calculator-1`, `benchmark_calculator-2`, `demo_porter`, `span_break_keyword_replace_branch_1`, `user_function_eval_span_replace_branch_1`, extracted via the harness's own `extract`, `--out-in` for the four that carry stdin) in a detached worktree pinned to the exact historical tree `0b16d013f`, rebuilt clean, today's box (`ldavg` 4–6 throughout — still nowhere near loaded):

| configuration | result (all 5 programs) |
|---|---|
| shipped arena, no stress env set | PASS, rc=0, sub-second, all 5 |
| `SCRIP_HEAP_MB=1 SCRIP_HEAP_MAX_MB=512`, no stress | PASS, rc=0, sub-second, all 5 |
| shipped arena, `SCRIP_GC_STRESS=0` | PASS, rc=0, sub-second, all 5 |
| `SCRIP_HEAP_MB=1 SCRIP_HEAP_MAX_MB=512`, `SCRIP_GC_STRESS=0` | PASS, rc=0, sub-second, all 5 |
| **`SCRIP_HEAP_MB=1 SCRIP_HEAP_MAX_MB=512`, `SCRIP_GC_STRESS=1`** | **TIMEOUT, rc=124, all 5 — killed at 30s (2 programs) / 60s (3 programs), never returned** |
| `SCRIP_HEAP_MB=1 SCRIP_HEAP_MAX_MB=512`, `SCRIP_GC_STRESS=3` | TIMEOUT, rc=124 (checked on the 3 benchmark-heaviest of the 5; same shape) |

**Arena alone does not hang them. Stress alone (at the shipped arena) does not hang them. Both together do, 5 of 5, deterministically, on an idle box.** This is exactly the coo's hypothesis 1, now measured rather than inferred: these five do not survive collection pressure within any reasonable timeout at the tiny arena.

## 3. STILL LIVE ON HEAD — NOT ALREADY CURED

Re-ran three of the five (the heaviest allocators) at `SCRIP_HEAP_MB=1 SCRIP_HEAP_MAX_MB=512 SCRIP_GC_STRESS=1` on **today's current tree** (SCRIP `f839e933b`, post the `cfo`'s Pass-B auditor landing): same result, rc=124 at 30s, all three. This is not a since-fixed regression on an old tree — it is a live population today.

## 4. WHAT THIS IS NOT (SCOPE, NOT YET CHARACTERIZED)

- Not yet named to a mechanism (livelock in the collector's stress-forced path vs. genuinely superlinear collection-count growth vs. something else) — this finding proves the *shape* (hang needs BOTH a tiny arena AND stress≥1; neither alone), not the *cause*.
- Not yet checked at intermediate stress values, at the two other named programs under stress=3, at mode 4, or at longer timeouts (a "hang" here means "exceeded 30–60s"; whether it is truly unbounded or just very slow was not distinguished — a longer-timeout probe is the next move if this is picked up as a row).
- Two of the five (`benchmark_calculator-1/2`) are BENCHMARK-class entries; `GC BEFORE LANGUAGE SCORES` / `speed is not your lane today` (CEO-1061) still applies — this is reported as a correctness-adjacent GC-survival finding (does the program *complete*), not a performance number, and no perf multiple is claimed anywhere in this finding.
- This is a different mechanism from `a84e1945` (a silent wrong-answer / SIGSEGV under collection) — this is a HANG, a wall-clock verdict, not a byte-diff. Not claimed to be the same root cause; not yet ruled unrelated either.

## 5. FOR THE PROGRESS TABLE ITSELF

Both the 22:25 and 23:00 rows were written before `config` was ever populated (the column existed in the header from 2026-09-06 but the writer only started filling it later this sitting per SCRIP `f839e933b`'s `test_gate_progress_records_the_configuration_it_exercised.sh`). Going forward, any row this lane appends under a declared GC axis should carry `--config` so this exact ambiguity does not recur; nothing owed on the historical rows themselves.
