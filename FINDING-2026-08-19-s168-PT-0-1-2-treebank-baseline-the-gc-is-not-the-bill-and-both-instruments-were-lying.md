# FINDING s168 (PT front, rungs PT-0..PT-2) — THE GC IS NOT THE BILL ON PURE MATCHING, AND BOTH SANCTIONED INSTRUMENTS WERE PRINTING FICTION

**Seat:** queue row `pt-baseline` (rank 3), brief = `GOAL-SNOBOL4-100.md` s166 §PT, rungs **PT-0..PT-2 ONLY** (instrument-only, no fixes).
**Tree:** SCRIP `25d8970c` for §2/§3, re-proved for §1 at post-`a78b39fb` (FZ-3) HEAD after a mid-seat rebase — see §1 · corpus `f5538e01` (the three workload files — `treebank-match.sno`, `treebank-match-fence.sno`, `VBGinTASA.dat` — verified byte-unchanged at the newer corpus HEAD pulled at handoff, so corpus drift does not touch these numbers) · oracle `x64` cloned this seat.
**Build:** `make pristine` (HQ-27), driver + `out/libscrip_rt.so` from ONE build, same second (19:30:02) — the s149/HQ-27 ABI-mix and stale-`.so` classes are both excluded by construction.
**⛔ RT_OPT = `-O0` on every number below** (FACT RULE O0-DEV; 260 × `-O0`, zero `-O1/-O2` in the build log). O2-DIRECTED-ONLY binds — Lon did not direct `-O2` this seat. **§7 states which conclusions are RT_OPT-sensitive and which are not.**

---

## 0. THE HEADLINE

On `treebank-match`, the workhorse the PT brief names, **SCRIP is 1.20× the oracle's wall (0.83× speedup) — the TOP of the stated 0.28–0.95× band, not the bottom — and the GC contributes EXACTLY ZERO to that deficit.** The match loop allocates nothing: 3 blocks / 4,194,416 bytes total, byte-identical at 100 and at 2000 match iterations, 0 storage regenerations at every arena size from 8 MB to 4096 MB. **H1 ("the GC tax follows the match") is FALSIFIED for pure matching.** The whole deficit is engine, and 59.4 % of all cycles sit in ONE construct: the deferred-pattern dereference `*group`.

Two prerequisites had to be repaired before any of that could be measured, and **both sanctioned instruments were emitting plausible, entirely false output** — the "non-empty is not alive" class again, twice in one seat (§5).

---

## 1. PT-0 — THE 3-WAY BASELINE (sbl / m3 / m4)

Protocol: same-moment interleaved, one iteration runs all three engines back to back, 7 samples, median-of-7, identity-gated (all three must print byte-equal stdout or the row is a bug report, not a timing). **Ratios only — absolute ms are not comparable across runs (LAW 2).** Instrument: `SCRIP/scripts/bench_pt0_3way.sh` (new, §5b).

| program | sbl | m3 | m4 | m3/sbl | m4/sbl | m3 speedup | m4 speedup | identity |
|---|---|---|---|---|---|---|---|---|
| `treebank-match` | 778 ms | 888 ms | 933 ms | **1.14×** | **1.20×** | 0.88× | **0.83×** | OK (3-way) |
| `treebank-match-fence` | 882 ms | 904 ms | 957 ms | **1.02×** | **1.09×** | 0.98× | 0.92× | OK (3-way) |

*reps=2000 counter tape on the 100 KB `VBGinTASA.dat`; scrip compile-only = 8 ms, i.e. <1 % of the m3 window.*

**RE-PROVED AFTER A MID-SEAT REBASE (RULES: re-prove the gate after a rebase).** `a78b39fb` **FZ-3** — which touches FENCE0 codegen (`emit.cpp`, `bb_match_fence0.cpp`) — landed while this seat was measuring, and this seat has a fence row. The table was therefore re-measured on a second `make pristine` at the post-FZ-3 HEAD, twice more at `--samples 15`:

| run | HEAD | `treebank-match` m3/sbl · m4/sbl | `treebank-match-fence` m3/sbl · m4/sbl |
|---|---|---|---|
| 1 (7 samples) | `25d8970c` pre-FZ-3 | 1.14× · **1.20×** | 1.02× · 1.09× |
| 2 (7 samples) | post-FZ-3 | 1.17× · **1.19×** | 0.91× · 0.93× |
| 3 (15 samples) | post-FZ-3 | 1.15× · **1.19×** | 0.97× · 1.01× |
| 4 (15 samples) | post-FZ-3 | 1.13× · **1.19×** | 1.00× · 1.03× |

- **The unfenced row is rock stable: m4/sbl = 1.19–1.20× in all four runs**, across two pristine builds and two HEADs. That is the number to carry forward, and FZ-3 does not move it.
- **The fenced row is NOT clean and its run-2 reading of 0.93× is an OUTLIER that must not be quoted.** The oracle is a fixed prebuilt binary running unchanged work, yet its own fenced median swung 882 / 1082 / 952 / 915 ms (±11 %) across the four runs while SCRIP's moved only 957 / 1011 / 959 / 941 ms (±3.5 %). The instability is on the ORACLE side — the s141/s108 bimodality LAW 2 exists for. Best post-FZ-3 estimate from the two 15-sample runs: **m4/sbl ≈ 1.01–1.03×, m3/sbl ≈ 0.97–1.00× (parity)**, improved from 1.09×/1.02×, **but a 1.09→1.02 delta is not cleanly separable from ±11 % oracle noise and this seat does NOT claim FZ-3 caused it.** A seat wanting that claim needs many more samples, or a fenced witness whose oracle timing is stable.
- **What IS robust across all four runs: FENCE costs the ORACLE and is inert on SCRIP.** sbl unfenced 778–835 ms vs fenced 882–1082 ms (always slower, +13 % to +30 %); SCRIP m4 unfenced 933–993 ms vs fenced 941–1011 ms (+1 %, i.e. within noise). One data point for H4; not this seat's rung.

**⛔ THE 1× WINDOW IS NOT MEASURABLE AND MUST NOT BE QUOTED.** One pass over the 100 KB input is 4–10 ms, of which scrip's own compile is ~7 ms: a 1× m3 number times the COMPILER, not the pattern engine. Measured at 1×, the same programs read m3/sbl 2.50× and m4/sbl 2.00× — pure startup artifact, ~2× worse than the truth. The brief's "at 1x" cannot be taken literally; the honest reading is "one pass of the input per iteration, mounted on a tape long enough to see."

**FENCE, post-FENCE-SPLIT (`bd3f02ef`) — one data point for H4, NOT this seat's rung.** Fencing is still ~inert on SCRIP (m3 +1.8 %, m4 +2.6 %) while it now **COSTS the oracle 13.4 %** (778→882 ms) on this pure-match workload. Direction stated explicitly because the goal file records the oracle "moving 1.14×–2.3×" without a sign: here the fence makes SPITBOL *slower*, and the fenced row is where SCRIP looks best (0.92×) precisely because the oracle got worse, not because SCRIP got better.

**⛔ ROW THAT CANNOT BE RUN — the workhorse trio is a DUO.** `treebank.sno`, the deserializing sibling named in the brief, is dead on BOTH sides at this HEAD: the oracle rejects it (`ERROR 217 -- syntax error: duplicate label`, ×5, at lines 70/75/80/83/86) and SCRIP m3 answers `** Error 5 in statement 0 / Undefined function or operation`. It is therefore neither oracle-gradeable nor self-consistent, and no PT-0 row exists for it. Note this is the ONLY member of the trio that allocates (it builds lists), so **the allocating half of the workhorse is exactly the half that does not run** — see §4.

---

## 2. PT-1 — THE PER-BOX HISTOGRAM

`profile_box_histogram.sh` on `treebank-match` @100 reps, callgrind `--dump-instr` + cache-sim + branch-sim, ranked by cyc-proxy per the TWO LAWS (rank by cyc-proxy, never bare Ir; ranks not absolutes). **Method guide `ARCH-PROFILE-BOX-HISTOGRAM.md` obeyed; its trap 4 is what the tool itself was violating (§5a).**

```
cyc-proxy split: emitted boxes 52.4%  |  runtime+libc 47.6%
```

### Category rollup (200 rows)

| category | cyc% | rows |
|---|---|---|
| emitted boxes | **52.4 %** | 23 |
| runtime `.so`: pattern engine | **45.3 %** | 12 |
| libc / loader (one-time startup) | 2.0 % | 37 |
| runtime `.so`: string ops | 0.3 % | 32 |
| runtime `.so`: other | 0.1 % | 93 |
| **runtime `.so`: GC** | **0.0 %** | 3 |

### TOP-10 COST ROWS

| # | cyc% | row | kind | note |
|---|---|---|---|---|
| 1 | 19.9 % | `rt:patv_slot` | rt: pattern engine | **D1m 3.52 M = 68.4 % of ALL D1 read misses** — cache-bound snapshot read |
| 2 | 15.2 % | `rt:rt_patv_defer_get_pat_dtp` | rt: pattern engine | calls `patv_slot` AGAIN with the same args, then `dtp_fn_of` |
| 3 | 14.1 % | `match_defer_α` | emitted box | the `*group` dereference box itself |
| 4 | 10.2 % | `rt:dtp_fn_of` | rt: pattern engine | 83 M Ir with ~0 cache and ~0 branch misses = pure call/prologue cost |
| 5 | 9.6 % | `PAT$_α_body` | emitted box | frozen pattern blob activation |
| 6 | 9.4 % | `match_break_α` | emitted box | **Bcm+Bim 1.92 M** — the per-character mispredict row |
| 7 | 7.6 % | `match_lit_α` | emitted box | Bcm+Bim 1.17 M |
| 8 | 6.9 % | `PAT$_γ` | emitted box | Bcm+Bim 1.44 M — success-edge record machinery |
| 9 | 1.4 % | `match_alternate_α` | emitted box | |
| 10 | 1.2 % | `rt:_dl_relocate_object` | libc/loader | one-time startup, shrinks with reps — ignore |

### What the table says

- **`*group` deferred dereference = 59.4 % of ALL cycles** (rows 1+2+3+4). Per dereference SCRIP pays a 3-call C round trip — `patv_slot` (twice: `rt_patv_defer_get_pat_dtp` re-reads the identical slot its caller already read) plus `dtp_fn_of` — on top of the emitted `match_defer_α` box. SPITBOL resolves the same recursion by cursor arithmetic and a table dispatch. **This is the single named target the PT front was looking for.**
- **Branch mispredicts live in the EMITTED code, not the runtime**: the emitted blob carries 93.7 % of all Bcm and 99.9 % of all Bim, concentrated in `match_break_α` / `match_lit_α` / `PAT$_γ`. That is **direct support for H2** (per-character box-transition control flow instead of a byte loop inside the box).
- **H3 (string materialization) is NOT the bill here**: runtime string ops total 0.3 %. `string_manip 0.28×` must come from a different workload class; on pure matching, strings are noise.

---

## 3. PT-2 — THE GC/ENGINE SPLIT

| arena (`SCRIP_HEAP_MB`) | 8 | 16 | 64 | 512 (default `ZC_HEAP_MB`) | 4096 |
|---|---|---|---|---|---|
| storage regenerations | **0** | **0** | **0** | **0** | **0** |

**Allocation is independent of the number of matches** — the decisive measurement:

| reps | blocks | bytes |
|---|---|---|
| 100 | 3 | 4,194,416 |
| 2000 | 3 | 4,194,416 |

20× the matching work allocates **the identical 3 blocks and the identical 4,194,416 bytes** (that is the 4 MB `-r4194304` input buffer plus two blocks — i.e. the *input read*, not the match). The match loop allocates **nothing**, so sizing the arena past the window changes nothing because there was never anything to collect.

**⛔ NON-VACUITY CONTROL (this is why the zero is trustworthy).** A zero from a counter that never prints is worthless. `SCRIP_GC_STRESS=1000` also printed 0 regenerations — *not* because telemetry is dead but because the stress trigger fires per ALLOCATION and the program performs only 3. Forcing `SCRIP_GC_STRESS=1` prints `[ZGC] regeneration #1 (LG): blocks 1->1 (pinned 1, fill 0) bytes 4194336->4194336 reclaimed 0`. **The counter and the telemetry path are live; the 0 is a true zero.**

### THE SPLIT

| component | share of the treebank-match deficit |
|---|---|
| **GC / storage regeneration** | **0.0 %** |
| **Engine (emitted boxes + pattern-engine runtime)** | **100 %** — of which 52.4 % emitted, 45.3 % runtime `.so` |

**H1 is FALSIFIED for pure matching.** The s154 fact base (collector O(garbage) vs oracle O(survivors), 65–70 % of wall at every heap size) is not contradicted — it is *localized*: that bill is charged by programs that ALLOCATE (captures, list building, concatenation, json), not by pattern matching as such. On a capture-free match SCRIP never enters the collector, and it still runs 1.20× the oracle. **Any repair rung aimed at the collector cannot move this row.**

---

## 4. SCOPE — WHAT THIS FINDING DOES *NOT* COVER

- Only `treebank-match` and `treebank-match-fence` (both **capture-free, side-effect-free**). The allocating member of the trio does not run (§1), so **the GC share of an allocating match is still unmeasured** — the 0 % above must not be generalized to matching with captures. That is the first thing the next seat should mount, and it needs `treebank.sno` repaired or an allocating witness minted.
- PT-3 (construct attribution), PT-J (json characterization) and PT-4 (decomposition + repair rungs) were **not** run — out of brief (PT-0..PT-2 ONLY). The `*group` mechanism named in §2 is offered as PT-3's entry point, not as PT-3's answer.
- json (631 KB) and claws5 untouched, per brief.

---

## 5. ⛔ BOTH SANCTIONED INSTRUMENTS WERE PRINTING FICTION — READ BEFORE TRUSTING ANY EARLIER PT-SHAPED NUMBER

### 5a. `profile_box_histogram.sh` attributed the program's own cycles to the dynamic loader

Unrepaired, on this workload it printed:

```
cyc-proxy split: emitted boxes 0.0%  |  runtime+libc 100.0%
   380,066,511  46.5   rt:lookup_malloc_symbol      <-- ld.so, and it never runs hot here
   245,776,841  30.1   rt:dtp_wrap_fn_sz            <-- wrong function
   123,869,580  15.2   rt:rt_patv_freeze            <-- wrong function
```

Every one of those rows is false. **Root cause: callgrind name compression, which is trap 4 in `ARCH-PROFILE-BOX-HISTOGRAM.md` — documented, never implemented.** callgrind names an object/function once and then back-references it as a bare `(id)`. In this profile **11 of 13 `ob=` lines and 336 of 659 `fn=` lines are bare back-refs**, and — decisively — **the program's own object is named only on a `cob=` line**, never on an `ob=` line. The parser tested `bname in l` against the raw `ob=` text, so `in_prog` was false for 100 % of the emitted blob's cost (→ "0.0 %"), and each bare `fn=(id)` silently inherited the previously named function, pinning the blob's cycles on `lookup_malloc_symbol` (a `ld-linux-x86-64.so.2` symbol, object id 1).

**Fix landed:** one id→name table populated from `ob=`/`cob=` and `fn=`/`cfn=` alike; family rollup extended for the `n<K>_<box>_<port>` symbol shape this corpus emits.

**Verification — the repaired tool now agrees EXACTLY with the official `callgrind_annotate` from the valgrind package**, which was used as an independent oracle throughout:

| row | fixed tool (Ir) | `callgrind_annotate` (Ir) |
|---|---|---|
| `patv_slot` | 120,835,200 (18.1 %) | 120,835,200 (18.10 %) |
| `rt_patv_defer_get_pat_dtp` | 105,730,800 (15.8 %) | 105,730,800 (15.84 %) |
| `dtp_fn_of` | 83,076,400 (12.4 %) | 83,076,400 (12.45 %) |
| emitted blob | 52.4 % cyc | 52.28 % Ir |

⛔ **Consequence for the record: any earlier histogram whose top rows are libc/loader names, or which reports a near-0 % emitted-box share, was produced by the broken parser and should be re-run before it is cited.** The s143 provenance case study is not impugned (its output shows a plausible 55.1 % emitted share), but nothing downstream of it should be trusted on sight.

### 5b. `bench_sno_match4.sh` — the PT-0 instrument named in the brief — cannot run at all

It dies on **every** program with `NameError: name 'ind' is not defined` → `claws5-match BUILD FAIL`. Its `mkrep` regex is `^(\s*)src\s+(\S+)\s+:F\((\w+)\)$`, which predates the `src ? pattern :F(label)` line shape that every `*-match.sno` in the corpus carries today; no line ever matches, so `mkrep` falls through with its locals unbound. Its tape is also capped at 52 reps (`LEN(N)` over `&LCASE &UCASE`) — far too short for this workload, where 52 reps is still ~25 ms against a ~4 ms startup.

**Delivered instead:** `SCRIP/scripts/bench_pt0_3way.sh` — 3-way (sbl/m3/m4), identity-gated, same-moment interleaved, median-of-N, counter tape (uncapped), `--compile-cost` to bound the m3/sbl compile-in-window asymmetry, and a hard refusal to print any ratio when the oracle is absent. The 2-way `bench_sno_match4.sh` is left in place and still broken; repairing or retiring it is a queue row someone should own.

---

## 6. ENVIRONMENT — THE ORACLE AND THE PROFILER WERE BOTH MISSING

- **`x64/` was ABSENT at seat start.** Every SNOBOL4 board script diffs against `x64/bin/sbl`; absent, they print a full, plausible, entirely false all-FAIL table. Cloned per PLAN.md §1b and verified alive (`m1_alt_arm2_cap.sno` → `b`) before any ratio was computed. **The three-sessions-running trap is still armed for the next seat: it is not in the image.**
- **This container is non-root (uid 1000, no passwordless sudo), so `install_system_packages.sh` cannot install anything** — it exits 0 having installed nothing but the packages already present. valgrind (PT-1's engine) and gawk (the scorecard's) were both missing. Worked around WITHOUT root: `apt-get download` + `dpkg -x` into a scratch prefix, then `PATH`/`VALGRIND_LIB`/`LD_LIBRARY_PATH`. valgrind 3.22.0 and gawk 5.2.1 both run. **`install_system_packages.sh` should either detect non-root and say so loudly, or grow a userspace fallback — silently succeeding while installing nothing is how a seat concludes "valgrind is unavailable in this container" and writes it into a goal file** (precisely the gdb-404 / VERIFY-INHERITED-BLOCKERS pattern that cost s33–s39).

---

## 7. RT_OPT SENSITIVITY — WHAT `-O2` WOULD AND WOULD NOT CHANGE

Stated because the brief demands every number carry its RT_OPT level, and because one conclusion here is genuinely level-sensitive:

- **SENSITIVE — the 52.4 / 45.3 split between emitted boxes and runtime `.so`.** `dtp_fn_of` (10.2 %, 83 M Ir, ~0 cache misses, ~0 branch misses) and `patv_slot` are small leaf functions whose cost at `-O0` is substantially call overhead and unelided prologue/epilogue. `-O2` would inline much of that. **The runtime share is an upper bound; do not quote 45.3 % as an `-O2` number.**
- **NOT SENSITIVE — the three load-bearing conclusions.** (a) GC share is 0 % because *nothing is allocated*, which no optimization level changes. (b) The 3.52 M D1 read misses in `patv_slot` are a memory-access-pattern property, not a codegen property. (c) The 1.92 M mispredicts in `match_break_α` are emitted-code control flow, and `-O2` does not recompile the emitted blob — it only rebuilds the `.so`.
- The oracle is a fixed prebuilt binary, so an `-O2` SCRIP would only improve the SCRIP side of every ratio in §1. **The 1.20× is therefore a worst case for SCRIP, and the "0.83× speedup" should be read as a floor.**

---

## 8. REPRODUCE

```bash
git clone https://github.com/snobol4ever/x64 $S4E_HOME/x64          # ⛔ not optional
cd SCRIP && make pristine                                            # HQ-27; RT_OPT defaults to -O0
bash scripts/bench_pt0_3way.sh --reps 2000 --compile-cost            # PT-0 (§1)
bash scripts/profile_box_histogram.sh <tape>.sno <corpus>/programs/snobol4/demo/VBGinTASA.dat 20   # PT-1 (§2)
SCRIP_HEAP_MB=4096 SCRIP_ZETA_TELEM=1 ./tape.m4 < VBGinTASA.dat 2>&1 >/dev/null | grep -c ZGC      # PT-2 (§3)
SCRIP_GC_STRESS=1  SCRIP_ZETA_TELEM=1 ./tape.m4 < VBGinTASA.dat 2>&1 >/dev/null | grep    ZGC      # the non-vacuity control
```
valgrind userspace prefix (non-root containers): `apt-get download valgrind libsigsegv2 gawk && dpkg -x *.deb $PREFIX`, then `VALGRIND_LIB=$PREFIX/usr/libexec/valgrind`.
