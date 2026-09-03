# FINDING 2026-09-03 seat07 — Raku `reverse` cured; full-suite re-point now measures, revealing 32 pre-existing AST mismatches

**Tree:** SCRIP (pristine `-O0` rebuild on top of the two commits landed elsewhere during this session) ·
corpus (unchanged) · measured 2026-09-03, seat `seat07`. FLEET-16, baton
`raku-smoke-two-refusals-cured-and-the-full-suite-runner-repointed`.

## Part 1 — the two smoke REFUSED entries: both were `reverse`, both cured

`test_smoke_raku.sh` named the two refusals as `array_reverse` and `str_reverse` (both `[m3 EXCS] [m4 EXCS]`).
Both trace to the same line: `src/lower/lower_raku.c` lowered `TT_REVERSE` — Raku's `reverse(...)` — via
`rk_excise()` unconditionally, bucketed with the still-pending lazy-Seq constructs (`TT_GATHER`, `TT_MAP`,
`TT_GREP`, `TT_SUSPEND`). Unlike those, `reverse` needs no generator/Seq machinery for the eager case these
smokes exercise — the runtime already carried a working `bn_reverse`/`REVERS_fn` (SNOBOL4's string `REVERSE`)
and a structured `ARBLK_t` array representation with an established generic-dispatch precedent one case away:
`TT_SORT: lower_rcall(cx, t, "array_sort", 0, γ, ω, res)`, whose `array_sort` handler (by_name_dispatch.c)
treats its argument as either a real `DT_A`/`.arr` array or an SOH-joined pseudo-array string.

**Cure**, mirroring that exact precedent:
- `lower_raku.c`: `case TT_REVERSE: return lower_rcall(cx, t, "array_reverse", 0, γ, ω, res);`
- `by_name_dispatch.c`: new `array_reverse` dispatch entry (added beside `array_sort`), added to the
  `rt_builtin_is_known()` name registry (load-bearing: `lower_raku.c:590` and `emit.cpp`'s call-route
  selection both gate on it, matching `array_sort`'s registration). Branches three ways: a real `ARBLK_t`
  array (element-order reverse, mirroring `arr_get`'s array unwrap), an SOH-joined string-as-array (element
  reverse, mirroring `array_sort`'s split/rejoin), else a plain string (`REVERS_fn`, character reverse).

**Verified** (pristine `-O0` build, sequential, no concurrent build activity):
```
mode-3 (--run):      PASS=724 FAIL=0 REFUSED=0  / 724
mode-4 (--compile):  PASS=724 FAIL=0 REFUSED=0  / 724
```
`my @r = reverse((1,2,3))` and `reverse('abc')` both verified correct by direct repro in addition to the smoke.
Icon smoke re-verified 14/0 both modes (unaffected — see the false-alarm note below).

## Part 2 — `test_raku_ir_full_suite.sh` re-pointed, not deleted

Old script targeted `$REPO/test/raku` (retired under the one-flat-suite corpus reorg — see
FINDING-2026-08-30-hq_B) and printed `SKIP ... rc=0` when that directory was absent, which it always was: a
never-ran reading as green (named in GOAL-CEO.md CEO-20 and row
`test-raku-ir-full-suite-skips-rc-0-when-its-population-directory-is-absent`). It is **re-pointed, not
deleted**: `test_smoke_raku.sh` and this suite are not the same population — the master pair
`corpus/tests/raku/ALL.raku`/`ALL.ref` (129 entries) is a separate, richer AST-parity corpus
(`LANG_CONFIGS["raku"]["modes"]="ast"`) with no overlap in what it exercises.

New script: checks the master pair exists (else `REFUSING (rc=2)`, never SKIP), runs
`corpus_suite_harness.py run ALL.raku ALL.ref --lang raku`, translates its `SUITE_BOARD ast_pass=/ast_fail=`
fields into the repo's conventional `PASS=N FAIL=N` line, and relays the harness's own rc.

**Measured against current SCRIP:**
```
SUITE_BOARD family=ALL total=129 ast_pass=83 ast_fail=32 ast_crash=0 ast_hang=0 ast_unproven=0 ast_skip=0 ast_xfail=14 ast_xpass=0
PASS=83 FAIL=32
rc=1
```
The re-point is mechanically correct and gate-honest (confirmed: absent-population path REFUSES rc=2; the
present-population path never prints a `SKIP` line; rc tracks the harness truthfully) — but the DONE-WHEN's
`[ rc -eq 0 ]` clause is **not met**, because the suite was never run before and is not clean. **32 real,
pre-existing AST-parity mismatches**, unrelated to `reverse` (none of the 12 `reverse` occurrences in
`ALL.raku` fall inside a failing entry; the 32 names cluster thematically around `replace`/`smartmatch`/
`junction`/`when`/`for` — e.g. `sub_junction_smartmatch_1`, `sub_for_range_replace_2`,
`sub_when_junction_replace_1`). This population was last rebuilt 2026-08-29 (corpus `237eb0900` et al.,
predating this session) and has evidently never been run to completion before this row — the SKIP bug hid it
from every prior read. **Left as a separate, unscoped body of work** — not attempted here: 32 potential
frontend defects in `replace`/`smartmatch`/`junction`/`for` is a different lane than this row's two named
refusals, and each needs its own measurement the way `reverse` got one, not a bundled guess. Recommend a new
row (or GOAL-RAKU-100 ladder entry) scoped to this specific class list, owned separately.

## False alarm, logged so it doesn't cost the next reader a diagnosis

Mid-session, `test_smoke_icon.sh` briefly reported `[m3 FAIL] write_int`, `[m3 FAIL] arith`,
`[m4 FAIL] write_int` (12/2 m3, 13/1 m4) on an **incremental** (non-pristine) `make`. Root cause, confirmed by
reproduction and clean re-run: two concurrent `make`/`make test` invocations (one launched in the background,
one in a foreground `git stash`/rebuild cycle used to isolate the reverse change) raced on the same
`scrip`/`out/libscrip_rt.so` output — the same background `make test` run later crashed outright with
`PermissionError: ... '/home/claude07/SCRIP/scrip'`, confirming a build-race rather than a logic defect.
A subsequent **pristine** rebuild, with every gate run sequentially and nothing else touching the build
directory, reproduced 14/0 both modes cleanly, twice. Filed here per RULES.md's culture of naming a
false-positive rather than letting it recur unexplained: **never run two `make`/`make test` invocations
against the same seat's build directory concurrently** — incremental `make` here is not safe against that,
and `make pristine` is the documented (and now doubly-confirmed) requirement before trusting any gate verdict,
including a red one.

## Gate status at push (pristine `-O0`, sequential, nothing concurrent)

- SNOBOL4 `make test`: ✅ GATE OK — m3 PASS=1679 FAIL=0 · m4 PASS=1679 FAIL=0 SKIP=0 · MISSING=0; full
  `make test` rc=0 (capture-oracle-refs gate, term-wordref ratchet, pl_quad_regs gate all green too).
- Icon watermark: 14/0 both modes — unaffected (see false-alarm note above).
- Raku smoke: 724/0/0 both modes — both named refusals cured.
- `strip_comments.py --check`: 384 files scanned, 0 offenders.
- No new globals: both C edits are local-scope additions inside existing functions/arrays; no file-scope
  state added.
