# ARCH — the README benchmark campaign: every working program against its rival

**Owner:** hq_P (HQ-PERFORMANCE) · **Authority:** Lon's order relayed by ceo s272 · **Opened:** 2026-08-24 s272
**Order, verbatim in substance:** *after cleanup, BENCHMARKS for SNOBOL4, Icon and Prolog against their rivals — a COMPLETE RUN OF EVERY WORKING PROGRAM, gathering the comparative tables for the README.*

## ⭐ THE BLOCKER LIST IS NOT WHAT THE BRIEF SAID — MEASURED, NOT ASSUMED

ceo's baton named **Prolog** as the blocked column and left Icon implicitly fine. Both halves needed correcting, in opposite directions:

| column | rival | state | denominator |
|---|---|---|---|
| **SNOBOL4** | `/home/resources/spitbol-bench-oracle/sbl` via `sbl_clean_bin()` | ✅ **READY** | **18 of 18** — SCRIP 18, SPITBOL 18, both 18 |
| **Icon** | `icont`/`iconx` **9.5.25a**, built, at `/home/resources/icon-master/bin` | ✅ **READY — NOT BLOCKED** | **20 of 20** (see the two traps below) |
| **Prolog** | `swipl`, `gprolog` | ⛔ **GENUINELY BLOCKED** — no binaries; source only at `/home/resources/{swipl-devel-master,gprolog-master}` | corpus is **fine**: 102 programs, 12/12 sampled compile under SCRIP |

⭐ **Icon is not blocked and the campaign must not be planned as if it were.** CLAUDE.md says *"icont/iconx … are not installed (Icon's oracle is a fleet install task before any Icon board is trusted)"* and `command -v icont` agrees — but the toolchain **is built and works**, just not on `PATH`. Verified: `icont -s t.icn -x` → `icont-alive`, `Icon Version 9.5.25a, September 7, 2025`. ⛔ Do not spend a fleet row installing what is already on disk. Reach it by absolute path or a `PATH` prepend, exactly as the SPITBOL oracles are reached — never by a per-root copy.

⛔ **Prolog is blocked on the RIVAL ONLY, not on the corpus.** Do not let a row be written to "build the Prolog benchmark corpus" — it exists.

## ⛔ Two traps in the Icon denominator, both of which produce a wrong number silently

**(1) Three of the 23 files are LIBRARY MODULES, not programs.** `post.icn`, `options.icn`, `shuffle.icn` have no `main`. SCRIP correctly refuses to build them standalone; counting them makes SCRIP look like it fails 3 programs. **The program count is 20, not 23.**

**(2) icont needs those modules precompiled or it fails 5 REAL programs.** `concord`, `deal`, `ipxref`, `queens`, `rsg` all `link post` and icont reports `cannot resolve reference to file 'post.u1'`. Naively censused, that reads as *"icont cannot build 5 programs SCRIP can"* — a false incompatibility.

Measured both ways:

```
naive census:      TOTAL=23  scrip=20  icont=18  both=15     <- WRONG, and it looks plausible
modules precompiled (icont -c post.icn options.icn shuffle.icn):
                   20 standalone programs, icont builds 20 of 20, SCRIP builds 20 of 20
```

⭐ **The honest Icon denominator is 20/20, not 15/23.** Every row in this campaign must precompile the three modules first and must exclude them from the program count. A campaign that shipped `both=15` would have understated the shared denominator by a quarter and invented five incompatibilities that do not exist.

## Campaign rows (seat-runnable where mechanical)

Each row emits a FACT-RULE grid, README-ready. **Axes named once above each grid**, rows carry bare multiples.

- **BENCH-1 · SNOBOL4 × SPITBOL** (mechanical, seat-runnable). 18 programs, `sbl_clean_bin()` with `-bf`, mode-4, `RT_OPT=-O0`. **DONE-WHEN:** 18 rows, each with a verified-identical output pre-check, or an explicit VOID with its reason.
- **BENCH-2 · Icon × icont/iconx** (mechanical once the module step is in the brief). 20 programs, `PATH=/home/resources/icon-master/bin`, modules precompiled first.
- **BENCH-3 · Prolog × SWI + GNU** ⛔ **BLOCKED, do not dispatch.** Needs `swipl`/`gprolog` installed. Escalated to Lon via ceo (apt, or build from the two source drops). Everything except the rival column is ready.
- **BENCH-4 · assembly + README emission** (hq_P). Consumes 1–3, emits the comparative tables. ⛔ Must refuse to emit a Prolog column while BENCH-3 is blocked rather than shipping a vacuous one.

## ⛔ Binding constraints, inherited and non-negotiable

- **`RT_OPT=-O0` only.** NO-O2 law (Lon s262). Every number labelled with its RT_OPT.
- **The unit is `x`, a multiple, on the faster axis: `reference / ours`.** Never a direction word on a multiple. Percentages may take the word and must name their basis.
- **One instrument, one basis, one RT_OPT, one mode, one ζ selector, one oracle+flags per grid.** A SLOPE is not a TOTAL.
- **Fixed work, verified before the number is believed.** This session re-pinned two watermarks that had outlived their workloads; a benchmark campaign is the same failure mode at scale.
- **Correctness gates the timing.** A wrong answer is never a fast answer — verify output before recording any number.
- **Oracle-loud-refusal.** A missing oracle REFUSES; it never prints a plausible table.
- **VOID-THE-RUN** on any arm whose basis moved mid-campaign — corpus paths moved three times in one day this session.
- **Denominator honesty.** State the denominator and how it was derived, every grid. `both=15` vs `20/20` above is why.

## Coordination

`corpus/benchmarks/icon/` is the live denominator for **icon-n2** and for BENCH-2. seat02 (row `icon-corpus-semicolonize`) correctly held it pending hq_P ack. **Measured: all 23 files are already semicolonized** (e.g. `bench_icnint_loop.icn`, 4 semicolons in 6 lines), so there is no sweep to do there and no dialect question to settle — released to seat02 with that finding rather than a bare yes/no.
