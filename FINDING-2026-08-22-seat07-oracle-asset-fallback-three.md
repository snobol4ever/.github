# FINDING — oracle-asset-fallback-three: the last 3 of 54 scripts now resolve x64 through D-17b

seat07, 2026-08-22. Queue row `oracle-asset-fallback-three` (rank 2), locked and closed this session.

## The brief

Three scripts hardcoded `$S4E/x64` for the SPITBOL oracle with no fallback, unlike 51 others that
resolve it through the D-17b asset tier (`GOAL-SCRIP-HQ.md` items 14/15: *"seats carry ONLY
.github/SCRIP/corpus"* — oracles/vendor trees live at HQ, `/home/claude`, and a seat without its own
`x64/` borrows HQ's). A per-seat `x64/` clone is not just wasted disk: `handoff_status.sh` discovers
it as a repo with an origin remote, which blocks that seat's handoff forever.

## Census — HQ's 51/3 split, independently re-derived (falsifiable per HQ LAW 17)

```
grep -l S4E_ASSETS scripts/*.sh | wc -l                      → 51
comm -23 <(grep -l '\$S4E/x64' scripts/*.sh | sort) \
         <(grep -l S4E_ASSETS  scripts/*.sh | sort)          → exactly the 3 named:
                                                                board_beauty_m1.sh
                                                                util_beauty_override.sh
                                                                util_crosscheck_two_oracle_census.sh
```
HQ's split was NOT falsified — confirmed exactly. The D-17b comment line is byte-identical across all
51 scripts that carry it (`grep -h '# D-17b' scripts/*.sh | sort -u` → one line), so there was one
canonical string to copy, not one to reinvent:

```bash
S4A="${S4E_ASSETS:-$([ -d "$S4E/x64" ] && echo "$S4E" || echo /home/claude)}"   # D-17b: ASSET root -- oracles/vendor trees live at the HQ root on this machine (Lon: seats carry ONLY .github/SCRIP/corpus); a root owning its own x64 (HQ, or a full standalone clone-set) is self-contained.
```

## The fix

All three scripts: added the `S4A=` line verbatim (copied from `util_run_beauty_oracle.sh`), then
routed their oracle path through `$S4A/x64/bin/sbl` instead of `$S4E/x64/bin/sbl`. Nothing else about
oracle *selection* changed — `-bf` stays the only correctness arm, `sbl_clean_bin()`/benchmark oracle
choice is untouched, this is purely WHERE the binary is found.

- **`board_beauty_m1.sh`** — already refused correctly on a missing oracle (`exit 2`); the refusal
  message said "Clone x64 first," which is now wrong advice under D-17b, so it was reworded to point
  at `S4E_ASSETS` instead of telling the seat to clone its own copy.
- **`util_beauty_override.sh`** — had **no oracle-existence check at all**. It ran `sbl` inside a
  `(... 2>/dev/null)` subshell under `set -uo pipefail` (no `-e`), so a missing oracle would have
  failed SILENTLY — empty `oracle.out`, script carries on, prints a plausible `DIFF`/`AGREE` verdict
  that is actually meaningless. This was the one real instance of the "false all-FAIL/false-verdict"
  class the brief warned about, not merely a style gap. Added `SBL="$S4A/x64/bin/sbl"` + an explicit
  `[ -x "$SBL" ] || { ... ; exit 2; }` refusal before any work happens.
- **`util_crosscheck_two_oracle_census.sh`** — already refused correctly (`for r in "$SBL" "$CSN"
  "$SCRIP"; do [ -x "$r" ] || ...; exit 2; done`); only the `SBL=` path itself needed the `$S4A` swap.

## Verification

**Negative test** — `S4E_ASSETS` pointed at a freshly-made empty directory, all three scripts:
```
board_beauty_m1.sh:                  exit=2  "⛔ ORACLE ABSENT (.../x64/bin/sbl). ... D-17b: seats do not clone x64 -- point S4E_ASSETS at a root that has it."
util_beauty_override.sh:             exit=2  "⛔ ORACLE ABSENT (.../x64/bin/sbl). D-17b: seats do not clone x64 -- point S4E_ASSETS at a root that has it."
util_crosscheck_two_oracle_census.sh: exit=2  "MISSING: .../x64/bin/sbl" + "⛔ without both oracles this prints a plausible all-FAIL table — refusing"
```
No silent skip, no false table, in any of the three.

**Positive test, from this actual seat** (`/home/claude07`, confirmed **no local `x64/`** — D-17b's own
condition, not simulated): the S4A fallback resolves to `/home/claude`, and
`md5sum /home/claude/x64/bin/sbl` = `0d1173f910b2570567163c66feb59202` — **byte-identical** to the
oracle the census/HQ docs already cite (`ec80390`, same md5). A seat with no oracle of its own reaches
the exact same binary HQ grades against, not a stand-in.

- `util_beauty_override.sh Parse "'X'"` ran to completion (rc=0) and printed a real oracle answer
  (`oracle=Parse Error`) — the oracle was actually invoked, not silently skipped.
- `util_crosscheck_two_oracle_census.sh` (no override) now gets **past** the SBL check and refuses
  specifically on `MISSING: /usr/local/bin/snobol4` — CSNOBOL4 isn't installed in this environment.
  That is a real, pre-existing, unrelated gap (this row does not touch CSNOBOL4 resolution); the point
  is the SBL leg of the same check no longer fires, proving the fix.
- `board_beauty_m1.sh`, run for real from this no-`x64/` seat, produced a genuine differentiated ladder
  (PASS / DIFF / `⭐M1-FIXED-POINT`, m4 10/10) — **not** an all-FAIL wall. See the adjoining FINDING
  (`FINDING-2026-08-22-seat07-stale-runpath-after-seat-rename.md`) for why `scrip` itself had to be
  rebuilt before this run was possible at all; that blocker was unrelated to the oracle and is now
  fixed on this seat.
- Diffed against a run using HQ's own SCRIP/corpus/oracle (`S4E_HOME=/home/claude`, which takes the
  OTHER arm of the same ternary — self-contained, `$S4E/x64` exists locally): m4 matches exactly
  (10/10, fixed point both sides). m3 differs (HQ 10/10, this seat 3/10 from rung 10) — traced to a
  **1-commit gap** between this seat's SCRIP HEAD (`568bf098`) and HQ's (`261cafc`), and that one
  commit (`261cafcb`, "banner: SUCCESS now has to be earned") touches only handoff-banner logic, zero
  files under `src/`. Compiler source is byte-identical between the two runs, so the m3 divergence is
  a build-state or runtime fact, **not evidence this row touched scoring** — flagged to HQ separately
  rather than chased here, since it is outside this row's lane.

## Scope check

No file outside the three scripts touched. No oracle-*selection* logic changed (`-bf`, `sbl_flags()`,
`sbl_clean_bin()` untouched). No `.ref`/`.s` artifacts regenerated (nothing in `emit.cpp`, templates,
or lowering touched). **Not a scoring change.**
