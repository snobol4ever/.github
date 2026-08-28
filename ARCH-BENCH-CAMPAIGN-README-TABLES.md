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
- **BENCH-3 · Prolog × SWI + GNU** ✅ **UNBLOCKED 2026-08-24 (ceo): Lon installed `swipl` via apt; rivals verified on disk.** Everything ready; dispatch behind the crunch ordering.
- **BENCH-4 · assembly + README emission** (hq_P). Consumes 1–3, emits the comparative tables. ⛔ Must refuse to emit a Prolog column while BENCH-3 is blocked rather than shipping a vacuous one.

## ⭐⛔ THREE-ANGLE TRIANGULATION (Lon 2026-08-24, in-chat — binding on every BENCH row above)

Lon, verbatim in substance: *"Ensure that the benchmarks are looked at from 3 ANGLES: (1) time based loop and count iters and give a second, or a good long time to get into the billions or trillions of iters but do not over do it if the whole thing takes too long, (2) iteration based loop and measure time and give a scaled amount tailored per-benchmark to also be long enough to get something useful. I want to cross prove. And (3) All time having wrapped the process in the whatever perf-like process measures CPU time, disk time, elapsed time. So you have the time or iterations reported by the program triangulated with the PERF telemetry. I'm trusting these numbers."*

- **Angle 1 — TIME-mode**: fixed wall-time budget, count iterations → iters/s. Budget long enough for a useful count (billions+ of iters where the kernel is cheap), but capped — do not let the whole campaign run long. Exists today for SNOBOL4: `test_bench_snobol4_timed.sh`.
- **Angle 2 — ITER-mode**: fixed iteration count, **scaled per-benchmark** so each runs long enough to be useful; measure elapsed time. (FIXED-WORK/callgrind-Ir is a *different instrument* on this angle — it corroborates but does not replace the wall-clock arm.)
- **Angle 3 — PERF wrapper on EVERYTHING**: every arm of angles 1 and 2 runs wrapped in the perf-style measurement (CPU time, disk/IO time, elapsed time — `/usr/bin/time -v` or `.tools/bin/perf`, see ARCH-PERF-TOOLING.md), so the program-reported figure is checked against external telemetry it cannot fake.
- **Cross-prove or VOID**: angle 1 and angle 2 must agree with each other, and each program-reported figure must agree with its angle-3 telemetry (elapsed≈elapsed, CPU/elapsed sane, disk≈0 for pure kernels). Disagreement beyond tolerance = VOID-THE-RUN, publish neither number.
- **Polarity, confirmed by Lon this ruling**: `1.5x` means **faster** — the FACT-RULE axis stands (`reference/ours`, faster axis; ≥1.00x ahead/GREEN, <1.00x behind/RED). Colourization green/red is wanted — keep it (`lib_perf_fmt.sh` in terminals, ```diff fences in markdown).
- **Status of existing numbers**: the seat13 18-kernel table (bench-rebaseline-15-kernels LEDGER) is **angle-1-only, preliminary** — it stands as the shape of the story but every README-published number must be triangulated first.
- **DURABLE TOOLING (Lon, same ruling)**: *"ensure that all the work is captured as shell scripts, Python programs, sets of data files. Whatever it takes to not REDO this EVERY SINGLE TIME from scratch."* Per-kernel iteration scales live in a committed data file, raw readings land as committed TSVs, and the grid a README quotes is the grid a script printed — nothing hand-transcribed.
- **BENCHMARK = TEST (Lon, same ruling)**: *"the source files [are] an app you can run albeit RINKY that has a REF file which can be verified. So it is a benchmark and a test."* Every kernel is a runnable app with a `.ref`, and the `.ref` diff is verified on EVERY measured run (variable `iters:`/`ms:` lines stripped, per the existing timed-runner convention). A kernel without a verified `.ref` is ungraded and its number unpublishable.
- **WHY**: a single-instrument number can lie three independent ways (timer granularity, per-kernel scaling error, machine noise/GC-in-window — the two GC2 rows proved it); triangulation makes polarity and magnitude self-checking before anything goes public. **SUNSET**: binds the announcement campaign; revisit after the READMEs ship.
- Execution row: `bench-triangulation-3angle` (postoffice, rank 0, minted on Lon's direct "Get to work" — his word supersedes the crunch ordering for this lane; src re-org continues in parallel on its own rows).

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

## ⭐⭐ THE TWO-ASPECT PRESENTATION LAW (Lon, in-chat to CEO, 2026-08-28 — binding on every benchmark presentation)
**Lon, verbatim in substance:** *"Always present from TWO aspects: (1) elapsed time — running SPITBOL, running SCRIP mode 3, or running the mode-4 generated executable from the command line; and (2) measured time from the program itself (elapsed AND cpu) at begin and end of the program's benchmark fixture."*
- **Aspect 1 — COMMAND-LINE ELAPSED**: the whole-process wall time the user feels. For m3 it INCLUDES the compile — that is honest, it is what running `scrip prog.sno` costs; for m4 the compile sits outside; label which. External instrument (`bench_rusage`), never engine self-timing.
- **Aspect 2 — IN-PROGRAM BRACKETS**: TIME()/host-clock readings taken INSIDE the program at fixture begin/end, elapsed AND cpu — the match/compute phase isolated from compile and startup BY THE PROGRAM ITSELF. ⭐ This is the standing answer to compile-dominated demo inputs (treebank-match's 9.3M-insn total): the bracket sees the match phase TODAY, without waiting on any harness. Precedent: the TIME()-bracket method is already ruled sufficient for oracle comparisons (CEO-30, microsecond-unit on the patched oracle clock, NS-TIME s249).
- ⛔ The two aspects NEVER share a column (different instruments); a grid presents both, labeled. The FACT RULE's shared-axes list applies to each independently.
- SPITBOL a.out note (Lon asked): saving a SPITBOL executable to bypass its compile in aspect 1 is the EXISTING row `x64-execfile-writer` (rank 3, hq_C, LOWER priority by Lon's own earlier ruling — the bracket method suffices meanwhile). No new row.

## ⭐ STATIC-VS-SHARED m4 LINK ARM — ASPECT-1 RE-MEASUREMENT (seat02, row `m4-static-link-arm`)

FINDING `f4f6292c` (hq_P) isolated the tier-1 aspect-1 floor to merely LOADING `libscrip_rt.so` (430
minor faults / 7.4MB / ~1.8ms before any program work) and found static linking the one lever of four
that actually worked, at a real price (~27-30MB/binary) that keeps it an ADDITIONAL opt-in arm, never
a default — `out/libscrip_rt.so` is unchanged and still canonical. This re-measures aspect 1 on all 10
tier-1 twins now that the arm is built: `--static` (`STATIC=1`) in `bench_rep_loop_demos_snobol4.sh`
and `bench_snobol4_fixed_iter.sh`, via `make libscrip_rt_static` → `out/libscrip_rt.a` (the SAME
`RT_PIC_OBJS` as the `.so`, `ar rcs`'d) + `gcc -no-pie -static` (never `-Wl,-Bstatic` toggling).

Shared axes: instrument `tools/bench_rusage` (best-of-3 external elapsed); aspect 1 = whole process,
m4 compile included; RT_OPT=-O0; mode m4 only (STATIC does not touch sbl/m3, both unaffected by
construction); SCRIP tree `ddb86a93`. × is `shared/static`, ≥1.00x = static ahead (GREEN).

⚠️ **Measured on the shared 16-seat box under real, visible contention, not a quiet machine** —
`uptime` read load average 5.7-6.8 throughout, with other seats' own `bench_rep_loop_demos_snobol4.sh`
processes independently visible in `ps` for the whole run. `calculator-1-match` — the heaviest tier-1
program, and therefore the row most exposed to scheduler noise — is flagged UNTRUSTED rather than
hidden or silently re-rolled: it read WORSE under static while every other row improved. Per this
file's own three-angle law, disagreement this sharp on one row is a reason to withhold that number,
not to average it in or discard it.

```diff
 demo                        × vs shared (aspect 1, m4 whole-process)
-calculator-1-match          0.56x   UNTRUSTED -- contended run, heaviest tier-1 program, re-measure quieter
+calculator-1-match-fence    1.01x
+calculator-2-match          1.04x
+calculator-2-match-fence    1.09x
+treebank-match              1.80x
+treebank-match-fence        1.63x
+claws5-match                2.22x
+claws5-match-fence          2.04x
+json-match                  1.88x
+json-match-fence            1.93x
```

**Correctness + footprint, all 21 sanctioned demos (10 tier-1 twins included):** every static binary
byte-matches its `.ref` AND is independently verified genuinely static via `ldd` (the control-arm-trap
check `f4f6292c` asks every static-arm caller to run — this row's own first attempt at that check had
a `pipefail`/`ldd`-exit-code bug that misreported every binary as non-static; cured in
`lib_static_link_snobol4.sh` before any number below was trusted). Full table:
`corpus/benchmarks/snobol4/perf-attribution-20260828T034003Z-seat02-static-link-arm.tsv`.

Aggregate across all 21 (mean of each demo's static/shared ratio): **maxrss → 0.477x of shared (a
52.3% cut), minor faults → 0.595x of shared (a 40.5% cut)**, at a binary size of 15.9KB-250.4KB
(shared, mean 51.5KB) growing to a flat **~29.1-29.3 MB regardless of program size** (static, mean
28.4MB) — the archive's own content dominates; program size barely moves it. Same shape FINDING
`f4f6292c` reported (do-nothing floor -51% faults there vs -40.5% mean here; the difference is this
arm links fully `-static`, glibc included, not only `libscrip_rt` — a wider cut than the finding's own
arm, never independently re-priced there, so treat the two as agreeing in direction and order of
magnitude, not as the same measurement).

⛔ **Not a ship decision.** This row builds and prices the arm; whether SCRIP ever links this way by
default remains Lon's call, unchanged by any number above.
