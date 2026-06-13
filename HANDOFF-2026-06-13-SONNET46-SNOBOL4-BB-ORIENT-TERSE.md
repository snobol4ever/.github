# HANDOFF 2026-06-13 · Sonnet 4.6 · SNOBOL4-BB orientation + GOAL-SNOBOL4-BB.md terse pass

**SCRIP HEAD:** ac6358e (unchanged — no code commits)
**.github HEAD:** (this commit)

---

## What this session did

**Orientation only.** Cloned repos, read PLAN/RULES/GOAL, built SCRIP, ran gates. No code committed to SCRIP.

**GOAL-SNOBOL4-BB.md:** terse pass 423→159 lines. All fact rules preserved (byte-identical obligation honored — compressed but complete). Completed items removed from watermark history. Bug ladder restructured with new M4-DCAP and M4-SMOKE-REGRESS entries.

---

## Key findings

**_wγ/_wω fix already landed** in commit `70b9977` (prior session). The Qize probe assembles, links, and runs clean. Labels `Qize_c0_wγ`/`Qize_c0_wω` are defined in the emitted asm. This was listed as open in the watermark but is closed.

**Smoke at 6/7 — two upstream regressions:**
- M3 concat: `OUTPUT = 'ab' 'cd'` gives empty output when stdin is `/dev/null`. Direct invocation (with terminal stdin) also gives empty. Pre-existing.
- M4 define: `DEFINE('DOUBLE(X)')` fails in compiled binary. Upstream regression from `14ae014` (FIXUP bb_unify.cpp — duplicate label `.Lx2_0`). Bisect to confirm; fix = eliminate duplicate label in that template.

**M4-DCAP — Qize gives correct output in --run, empty in compiled binary.** `rt_dcap_begin/end_ok/end_fail` are wired in `flat_drive_scan_native`. `--run` gives `b.c`. Compiled binary gives nothing. The deferred-capture machinery is present in the asm but the commit/assign path in the compiled binary has a gap. This is the next target.

---

## Gates at session end

- smoke: **6/7** (m3 concat + m4 define — upstream regressions)
- pat-rung: **19/19/19 no-SKIP** ✓
- fence: **HARD** ✓
- SCRIP: `ac6358e` (unchanged)

---

## Next session priority

1. Fix M4-SMOKE-REGRESS: diagnose m4 define duplicate label (trace from `14ae014`); fix `bb_unify.cpp` or the IR shape that triggers it.
2. Fix M4-DCAP: trace why compiled Qize gives empty output — compare asm from `--compile` vs what `--run` does in-process; the gap is likely in how `rt_dcap_end_ok` flushes the conditional capture assignment in the compiled path.
