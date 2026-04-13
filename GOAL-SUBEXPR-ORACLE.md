# GOAL-SUBEXPR-ORACLE — Sub-Expression Oracle Test Suite

**Repo:** one4all + corpus
**Done when:** Generator produces ≥200 passing tests across all 18 beauty drivers under SPITBOL; suite runs under scrip --ir-run and pinpoints divergences.

## Motivation

The 19 beauty drivers are coarse — a single driver failure could have 100+ possible root causes. Sub-expression oracle tests decompose each expression bottom-up (innermost sub-expression first) and capture the oracle value at a real execution sample point. When scrip diverges, you get: exact expression, exact stlimit (execution context), expected vs actual value. Far fewer places to look.

## Technique

1. **Sample:** For each beauty driver, pick K stlimit values spread across its execution (determined by running it fully first to get &STCOUNT).
2. **Probe:** Build a program that runs the driver to stlimit=N (live context — globals, DATA structures, function definitions all established), then evaluates each sub-expression and outputs a marked result.
3. **Oracle:** Run probe under SPITBOL x64. Capture oracle values.
4. **Emit:** One .sno + .ref per (driver, stlimit, sub-expression).
5. **Regress:** Run same .sno under scrip --ir-run. PASS/FAIL vs .ref.

**Key insight:** No state restoration needed. The driver runs to stlimit=N and stops (stlimit exhausted). Probe evaluations then run with unlimited stlimit. This handles function calls, DATA structures, indirect variables, patterns — everything.

## Files

| File | Purpose |
|------|---------|
| `one4all/test/beauty_subexpr_gen.py` | Generator: probes all 18 drivers, emits .sno + .ref |
| `corpus/programs/snobol4/subexpr/` | Generated test pairs (not committed — regenerate) |

## Run commands

```bash
# Generate tests (all 18 drivers, 10 sample points, 8 sub-exprs each):
cd /home/claude/one4all
python3 test/beauty_subexpr_gen.py \
    --beauty /home/claude/corpus/programs/snobol4/beauty \
    --out /home/claude/corpus/programs/snobol4/subexpr \
    --samples 10 --subs 8 --verbose

# Run generated tests under scrip --ir-run:
python3 test/beauty_subexpr_gen.py --run \
    --beauty /home/claude/corpus/programs/snobol4/beauty \
    --out /home/claude/corpus/programs/snobol4/subexpr

# Run a single driver's subexpr tests:
python3 test/beauty_subexpr_gen.py \
    --drivers omega --samples 10 --subs 8 --run --verbose
```

## Current State (session 2026-04-12, session 5)

- one4all HEAD: `03e3b600`
- Generator written: `one4all/test/beauty_subexpr_gen.py`
- Probe mechanism verified correct (SPITBOL probe pattern works)
- Sub-expression extractor verified correct (tokenizer + recursive bottom-up)
- **Bugs to fix before generator produces valid tests** (see S-1 below)

## Steps

- [ ] **S-1** — Fix four generator bugs:
  1. `global.sno` double-include: `build_driver_source` prepends global.sno AND driver keeps its own `-INCLUDE 'global.sno'`. Deduplicate: strip explicit global.sno from driver lines since we prepend it.
  2. Single-quote in FAIL message: `OUTPUT = 'FAIL [Pop('dummy')]...'` breaks SPITBOL parser. Escape or strip quotes from subexpr text in the FAIL string.
  3. `count_driver_stmts` uses stlimit=2000000 but returns 200 (hits early stlimit from driver itself). Fix: strip `&STLIMIT` lines from driver before inserting into counter program, set outer stlimit to 10000000.
  4. Early samples fail: stlimit=33 lands inside global.sno UTF table init, before any driver functions defined. Fix: start sampling after the driver's own `&STLIMIT = 1000000` line (first ~100 stmts are global.sno setup, skip them).
  Gate: `python3 test/beauty_subexpr_gen.py --drivers counter --samples 5 --subs 6 --verbose` produces ≥20 tests, all pass under SPITBOL.

- [ ] **S-2** — Run generator on all 18 beauty drivers. Gate: ≥200 tests generated, all pass under SPITBOL (they are oracle-derived by construction).

- [ ] **S-3** — Run test suite under scrip --ir-run. Triage failures by driver. Gate: suite runs without crash; PASS/FAIL counts printed per driver.

- [ ] **S-4** — Map sub-expression failures to known bugs in GOAL-SCRIP-BEAUTY. Each FAIL should identify which of Gen/TDump/XDump/omega bugs it exercises (or reveal a new bug). Document mapping in this file.

- [ ] **S-5** — Use sub-expression failures to guide fixes in S-6..S-9 of GOAL-SCRIP-BEAUTY. Gate: fixing one scrip bug causes a cluster of sub-expression tests to flip from FAIL to PASS.

- [ ] **S-6** — Commit generator to one4all; add corpus/programs/snobol4/subexpr/.gitkeep. Gate: `make scrip` still passes; beauty suite still 14/18.

## Commit identity

Always: `LCherryholmes` / `lcherryh@yahoo.com`
