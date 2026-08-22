# FINDING 2026-08-22 seat12 — oracle-two-face-adoption: censuses corrected, timing+correctness sites converted, NOISE-FLOOR re-bake deferred

Row `oracle-two-face-adoption` (rank 0), claimed via THE LOOP. Brief: adopt the s255 two-oracle
ruling (`x64/bin/sbl -bf` = correctness oracle, `/home/resources/spitbol-clean/sbl` = benchmark
oracle, `scripts/lib_oracle_flags.sh` = one authority) into the scripts that actually invoke
SPITBOL. This is a partial-completion report — the claim stays open, see STILL OPEN at the end.

## 1. The censuses, measured fresh (HQ's numbers were a hypothesis; both HQ's and RULES.md's prior counts were wrong in different ways)

- **Scripts invoking sbl in any form:** 46 (grep for `\bsbl\b|/sbl[ '"']|sbl_clean_bin|sbl_lang_flags` over `scripts/*.sh`). HQ said 45.
- **Scripts sourcing `lib_oracle_flags.sh`:** 5 before this row (`bake_noise_floor_snobol4_fixed.sh`, `bake_noise_floor_snobol4_timed.sh`, `test_bench_snobol4_timed.sh`, `bench_pt0_3way.sh` — wait, bench_pt0_3way.sh sourced it too, so the pre-row count was these 4 plus itself was miscounted in my first pass; see §2 for the corrected per-file table). Now 16 after this row's edits.
- **`sbl_clean_bin()` consumers before this row: 0** (only its own definition — HQ was right about this one, and it is the headline gap). **After: 11 real call sites** across 6 files.
- **Real (non-comment) bare `-b` invocations of the oracle before this row: 17**, not HQ's 11 and not RULES.md's ~19. Full file list in §2. Two of HQ's 11 named files (`test_crosscheck_all_backends.sh`, `util_bench_snobol4_engines.sh`) turned out to contain **zero** executable oracle invocations — see §4.

The three-census "17 bench_*/test_bench_*/bake_noise_floor_* scripts" HQ named is the raw glob count (18 by my measurement, ls `bench_*.sh test_bench_*.sh bake_noise_floor_*.sh`) — of those 18, only **6 actually reference sbl** (the rest are Prolog/Icon benchmarks with unrelated oracles). The other 5 timing/perf-adjacent conversions in this row (`board_sno15_perf.sh`, `board_sno15_perf2.sh`, `board_sno_apps.sh`, `cmp3_snobol4.sh`, `test_3way_snobol4.sh`) sit outside that glob entirely — HQ's glob pattern was too narrow for the actual timing-script population. State this explicitly rather than silently expanding scope: the real "timing set that must move" is 11 files, not 17.

## 2. What was converted

**Benchmark-oracle adoption (source `lib_oracle_flags.sh`, resolve the binary via `sbl_clean_bin()`, language arm via `sbl_lang_flags()`):**

| File | Pre-row state |
|---|---|
| `bake_noise_floor_snobol4_fixed.sh` | already sourced lib, still hardcoded `x64/bin/sbl` path — binary-path half of the fix was missing everywhere |
| `bake_noise_floor_snobol4_timed.sh` | same |
| `test_bench_snobol4_timed.sh` | same, plus the source line sat *after* the old `SBL=` assignment — reordered |
| `bench_pt0_3way.sh` | never sourced lib; hardcoded `-bf` literally (already correct value, wrong provenance) *and* hardcoded the x64 path; its own `[ -x "$SBL" ]` refusal message told the reader to "Clone snobol4ever/x64" — now-wrong advice for a seat (s255) |
| `bench_sno_match4.sh` | never sourced lib; bare `-b` (real bug) + hardcoded x64 path |
| `bench_sno_rail.sh` | same |
| `board_sno15_perf.sh` | same, plus not in HQ's glob at all |
| `board_sno15_perf2.sh` | same (3 call sites) |
| `board_sno_apps.sh` | same |
| `cmp3_snobol4.sh` | bare `-b`; its own comment documented the resulting "exits 1 on benign sandbox segfault" as an accepted quirk — that quirk is the s189 phantom-duplicate-label crash path, not a SPITBOL constant |
| `test_3way_snobol4.sh` | same |

**Correctness-oracle flag fix (stay on `x64/bin/sbl` via the existing `S4A` fallback, source lib, replace `-b` with `$(sbl_lang_flags)`):**

`board_sno15_ident.sh`, `test_arbno_radius_ab.sh`, `test_arbno_witnesses.sh`, `test_demo_full_3way.sh`, `test_one_witness.sh`, `test_demo_descent_sweep.sh` (variable is `SWEEP_ORACLE`, not `SBL` — grep for `\bSBL\b` alone misses it, noted for the next census), `build_spitbol_oracle.sh` (smoke-tests the freshly-built **patched** fork, so `-bf` is correct there — contrast with §4).

**Path-only fix:** `util_crosscheck_two_oracle_census.sh` hardcoded `SBL="$S4E/x64/bin/sbl"` with no `S4A` fallback and no override — on a seat (no sibling x64) this refuses with a spurious `MISSING: $S4E/x64/bin/sbl` even though the oracle is reachable via HQ. Added the standard `S4A` resolution; its `-bf` was already correct but hand-rolled, moved to `sbl_lang_flags()` for one-authority consistency. **Collision, resolved during `git pull --rebase`:** another seat's concurrent commit (`361accaf`, row `oracle-asset-fallback-three`) fixed the identical `S4A` gap in this same file (plus `board_beauty_m1.sh` and `util_beauty_override.sh`, neither touched here) — their fix was the `S4A` line alone; mine additionally needed the `lib_oracle_flags.sh` sourcing for the `-bf`→`sbl_lang_flags()` swap below it. Merged to the superset (their `S4A` definition + my sourcing + override-capable `SBL="${SBL:-...}"`); no work lost on either side, both rows land clean on this file.

## 3. Deliberate exceptions — named, not converted

- **`util_oracle_flag_sweep.sh`** — its entire purpose is comparing `-b` vs `-bf` output (`sweep <outdir>`, three arms including a `-b` control). Converting its `-b` away would delete the tool. Left as-is; it already documents the s189 rationale in its own header.
- **`build_official_oracles.sh`** — its `-b` (line 38, `$SPIT/sbl`) smoke-tests a **from-source build of raw upstream spitbol/x64 with zero SCRIP patches**. Raw upstream has no uppercase-keyword table, so `-bf` on an uppercase-keyword smoke program (`OUTPUT`/`END`) would break it — RULES.md's own correction confirms `-f` alone dies with "No END statement found" against unpatched upstream. **HQ's brief named this file as an offender; it is not one** — its `-b` is the only correct flag for the binary it tests. Left unconverted, documented here so the next census doesn't re-flag it blind.
- **`install_spitbol_x32_runner.sh`** — invokes a **different binary** (`$SBL32` via `qemu-i386-static`, 32-bit), unrelated to the x64/spitbol-clean two-oracle system. Out of scope for this row.
- **`util_bench_snobol4_engines.sh`** — HQ named it as an offender; it contains **zero hardcoded oracle invocations**. It's a generic `<label> <timeout> <divisor> <cmd...>` wrapper — callers pass the full engine command including flags. Its two comment lines (documenting example invocations for official-upstream vs the patched fork) are already accurate. No change made.

## 4. A bug found that wasn't in anyone's list

**`test_crosscheck_all_backends.sh`** defines `SPITBOL="${SPITBOL:-$S4A/x64/bin/sbl}"` (already correctly S4A-formed) but **never invokes it anywhere in the file** — the four backend sections all delegate to `run_crosscheck_{x86,jvm,net}_rung.sh` / `run_wasm_corpus_rung.sh`, which own their own oracle resolution independently. The variable is dead. Its header comment ("Oracle: SPITBOL x64 (/home/claude/x64/bin/sbl -b)") was actively misleading — both the hardcoded `/home/claude` path and the `-b` flag. Corrected the comment to say what's actually true; did not delete the unused variable (out of scope — not this row's concern, and deleting dead code that isn't blocking anything is a separate cleanup call).

## 5. Verification performed

- **Syntax:** `bash -n` on all 20 touched files — 0 failures.
- **Grep sweep:** zero remaining `"$SBL"|"$SPITBOL"|"$SWEEP_ORACLE" -b` (bare, not `-bf`) sites across the touched files.
- **Functional, live, on this seat (seat12, no local x64 clone — proves the S4A fallback actually works, not just that it parses):**
  - `sbl_clean_bin()` resolves to `/home/resources/spitbol-clean/sbl` (executable); running it with `$(sbl_lang_flags)` (`-bf`) against a real `.sno` produced correct output.
  - `test_one_witness.sh` end-to-end against a trivial program: oracle resolved to `/home/claude/x64/bin/sbl` via the `S4A` fallback (HQ's clone, since this seat carries none — exactly the s255 design), ran with `-bf`, **oracle rc=0**. (m3/m4 both failed in that run because `scrip` isn't built on this seat — unrelated to this row; noted, not hidden.)
  - Attempted a `LOAD()`-witness for the "clean oracle must refuse loudly, not silently misreport" DONE-WHEN item. My test program had a syntax error (SPITBOL's `LOAD()` wants a paren-form first argument, not the string literal I gave it) — both `spitbol-clean` and `x64/bin/sbl` produced byte-identical `ERROR 139` output on it, which is a mildly useful data point (parse-path parity) but **not** a decisive test of the LOAD/UNLOAD stub gap. A real witness is still needed — flagged in STILL OPEN, not fabricated here.

## 6. STILL OPEN — claim not marked done

- **NOISE-FLOOR.tsv re-bake under 12-seat load**: not attempted. This requires real concurrent load from the other seats to be live at bake time, which one session cannot orchestrate or fake. Needs either a coordinated fleet-wide bake window or an accepted proxy methodology — asking HQ (`ask oracle-two-face-adoption`) rather than blocking on it.
  - the 8-vs-12-seat delta HQ asked to be stated explicitly: not measured this session (no baseline data collected); flagging rather than guessing a number.
- **Correctness scoring "byte-identical before and after on an unchanged tree"**: not run as a full corpus sweep — `scrip` is not built on this seat (`make` was not run; out of scope for what this row actually changes, since none of these edits touch the compiler). The claim that matters here — that swapping the oracle *binary* for timing doesn't change *output* — is not re-derived from scratch; it was already measured at s255 (`FINDING-2026-08-22-seat2-clean-oracle-monitor-overhead.md`: all 15 benchmark kernels byte-identical on both binaries) and this row's job was wiring, which §5 verifies functionally. The `-b`→`-bf` correctness-side conversions are **expected** to move some scores (that's the s189 finding, not a regression) — per the brief's own "NO SCORING CHANGES... if a board moves, that is a finding to report, not a number to adjust" — no board was re-run to observe deltas this session; that's real remaining work.
- **A verified `LOAD()`-witness refusal**: inconclusive attempt in §5; needs a correctly-formed SPITBOL `LOAD()` call.

Claim `oracle-two-face-adoption` is left LOCKED and open (not `s4e_msg.sh done`) for continuation — either by this seat next session or another. Everything above is pushed; nothing is parked uncommitted.
