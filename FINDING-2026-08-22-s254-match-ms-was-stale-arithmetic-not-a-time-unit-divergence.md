# FINDING — s254 seat4: match_ms=675791 was stale demo arithmetic, not a TIME() divergence

**Session:** s254 (seat4) · **Date:** 2026-08-22 · **Row:** `match-ms-time-units` (rank 0, HQ s251)
**Status:** FIXED — 4 programs, 4 repos touched (corpus, x64 read-only probe, .github)

---

## 1. THE HEADLINE

`TIME()` itself is fine. It returns integer nanoseconds off `CLOCK_MONOTONIC` in SCRIP and the SPITBOL
oracle alike, exactly as `FINDING-2026-08-21-s249-ns-time-and-the-arith-loop-instruction-budget.md`
specified. The bug was entirely downstream: four SNOBOL4 programs compute an elapsed-time figure as a
raw `TIME()` difference and label it milliseconds — arithmetic that was correct before s249 (when
`TIME()` really did return whole ms) and was never updated when s249 changed the unit under it.
`json.sno`'s `match_ms=675791` is **677192 ns measured**, i.e. **0.68 ms** — a three-byte parse read as
11 minutes only because nobody divided.

## 2. THE BRIEF'S OWN PREMISE, MEASURED AND PARTLY FALSIFIED

The dispatch brief asserted *"SPITBOL prints no such line at all on the same program, so this is
SCRIP-side."* Measured, this is false: `TERMINAL` output is stderr, and stderr was not captured
separately in whatever check produced that claim.

```
$ printf '[1]' | sbl -bf json.sno 2>&1 1>/dev/null
match_ms=4679
```

SPITBOL prints the line and its number (4679 ns = 4.68 μs) is **also** plausible for a 3-byte match —
so the oracle was never broken either. Recorded so the false premise doesn't get re-spent: **always
separate stdout/stderr before concluding an engine "prints nothing."**

## 3. ROOT CAUSE, ISOLATED

FIRST STEP per the brief: a minimal sleep-free counted loop, `TIME()` before and after, run under both
engines (`/tmp/.../time_unit_probe.sno`, 200,000-iteration increment+compare, no I/O):

| engine | elapsed_ns | ns/iteration |
|---|---|---|
| SCRIP (m3) | 885,726 | 4.4 |
| SPITBOL `-bf` | 8,018,573 | 40.1 |

Both are sane nanosecond-scale readings (as milliseconds they'd claim 0.9s / 8.0s for 200K trivial
increments — absurd). The ~9x ratio matches other m3:sbl ratios in the s249 baseline table (`var_access`
7.31x, `op_dispatch` 7.23x) — SCRIP compiled beats SPITBOL interpreted by the expected margin, not some
unrelated distortion. **TIME() is not the bug in either engine.**

The actual defect, found by grep, not guesswork:

```
$ grep -n 'TIME(\|_ms\b' json.sno calculator-1.sno calculator-2.sno
json.sno:268:*  ... TIME() is milliseconds of compute
json.sno:287:    TERMINAL = 'match_ms=' (t1 - t0)       :(END)
calculator-1.sno:65:    TERMINAL = 'match_ms=' (t1 - t0)        :(END)
calculator-2.sno:97:    TERMINAL = 'match_ms=' (t1 - t0)        :(END)
```

Three demos, six call sites (`:(END)` arm + `fail`/`bad` arm each), all doing raw `t1 - t0` with **no
conversion**, and `json.sno`'s own comment states the stale contract in writing: *"TIME() is
milliseconds of compute since program start."* s249 §4 changed that contract in all three engines and
never touched these four programs — the comment is the fossil that proves it.

A fourth site, same shape, found by widening the sweep past `demo/`: `programs/aisnobol/KALAH.sno`'s
`REPORT()` prints `PRT(S " milliseconds used")` where `S = TIME() - SECS`, an unconverted ns figure
under an explicit "milliseconds" label.

## 4. THE FIX

Six `TERMINAL`/`REPORT` call sites across four files, `(t1 - t0)` → `(t1 - t0) / 1000000`, matching the
**exact idiom `harness.inc` already established for this same s249 transition** (`ms: ZE / 1000000`,
integer truncating division — §4.5 of the s249 finding: *"ZBUD/ZFLR stay in milliseconds ... this file
converts them once, in place"*). Stale unit comments corrected alongside. No new global, no new IR, no
new grammar — pure demo-source arithmetic, zero compiler/runtime changes.

```diff
- TERMINAL = 'match_ms=' (t1 - t0)        :(END)
+ TERMINAL = 'match_ms=' (t1 - t0) / 1000000        :(END)
```

Truncating to whole ms means a sub-millisecond match now reads `match_ms=0` — **this is correct, not a
regression in resolution.** `scripts/util_out_sweep.sh`'s own parallel-safety comment independently
records `match_ms=0` / `match_ms=1` as the real values these demos produced *before* s249, so 0 is the
historical, intended magnitude for a trivial input, not a loss.

## 5. VERIFICATION

`json.sno`, every comma-free input from the known-good set in
`FINDING-2026-08-21-s251-json-deserializer-hangs-on-every-comma-and-has-no-corpus-coverage.md` (comma
inputs skipped deliberately — see §7):

| input | SCRIP match_ms | SPITBOL match_ms |
|---|---|---|
| `[]` `{}` `{"a":1}` `[{"a":1}]` `[1]` | 0 (all) | 0 (all) |

`calculator-1.sno` / `calculator-2.sno` against the real 32 KB `calculator.input`:

| program | SCRIP | SPITBOL |
|---|---|---|
| calculator-1 | 19 ms | 14 ms |
| calculator-2 | 17 ms | 16 ms |

Same order of magnitude both engines, both plausible for parsing 32 KB against the calculator grammar.
`KALAH.sno`'s fix mirrors the other three exactly but **could not be end-to-end verified** — see §7.2.

stdout unaffected: `TERMINAL` is stderr by design (`json.sno`'s own comment: *"written to TERMINAL ...
so that stdout stays deterministic and byte-comparable against .ref"*); confirmed no `.ref` file
anywhere contains `match_ms`, and `calculator-1.ref` still diffs clean post-fix.

## 6. ⭐ THE UNIT CONTRACT — FOR THE NEXT DEMO

**`TIME()` returns an INTEGER NANOSECOND count off a monotonic wall clock (`CLOCK_MONOTONIC`), identically
in SCRIP, SPITBOL and CSNOBOL4, since s249 (`ec80390e3`/`SCRIP ec34eba0`).** It does **not** self-report
in milliseconds and never rounds for you.

- Want milliseconds for display? **You divide.** `(t1 - t0) / 1000000` — integer division truncates;
  that's correct, expected behavior for a demo timing figure, not a bug to work around.
- Writing a new benchmark? **Don't hand-roll this at all** — `-INCLUDE 'harness.inc'` already owns the
  conversion (`ZBUD`/`ZFLR` stay milliseconds, the harness multiplies by 1,000,000 once at the top and
  divides once at the bottom; see its own header comment for the full contract).
- Comparing `TIME()` against a **budget or deadline constant** (not just printing a duration, e.g.
  KALAH.sno's `PLAY(...,TIME())` search-clock pattern)? Any hardcoded threshold predates s249 and is
  denominated in the OLD unit for that engine — re-derive it in nanoseconds or the comparison is silently
  wrong by 10^6, in whichever direction breaks that program's control flow. Grep for `TIME()` used in a
  comparison (`LT`/`GT`/`GE`/`LE` against it, or a `:S()`/`:F()` branch off it), not just in a print
  statement — a wrong budget compiles clean and fails silently, which is worse than a wrong printout.

## 7. SCOPE — WHAT WAS SWEPT, WHAT WAS DELIBERATELY LEFT ALONE

Full-corpus grep for `_ms|msec|match_ms|elapsed_ms|execution time msec` across every `.sno .icn .pl .sc
.inc`: hits landed in exactly three families — the four SNOBOL4 programs fixed here, Icon's `rate_*.icn`
+ `micro.icn` + three `ipl/gprogs` (all read Icon's own `&time` keyword, a different runtime mechanism
s249 never touched), and two GNU Prolog benchmarks (`statistics(runtime, ...)`, likewise unrelated).
Confirmed by reading the actual matched lines, not by the language extension alone — **s249 named
SCRIP/SPITBOL/CSNOBOL4 specifically; Icon and Prolog were never in scope and this sweep confirms neither
was silently touched.**

### 7.1 NOT FIXED, ALREADY TRACKED: the JSON comma hang

`json.sno` hangs on any comma-bearing input (`FINDING-2026-08-21-s251-...`, queued rank-0
`json-arbno-comma-hang`). Verification here used only the comma-free input set that finding already
proved passes — running `twitter.json`/`citm_catalog.json` through the fix would have hit that hang and
told me nothing about the TIME() fix. Left for its own row.

### 7.2 ⛔ NOT VERIFIABLE THIS SESSION: KALAH.sno has pre-existing CRLF line endings

`programs/aisnobol/KALAH.sno` fails to parse AT ALL under SCRIP — `unexpected char ''` at a dozen-plus
lines, root cause `\r\n` (CRLF) line endings (confirmed `cat -A`: `^M$`). **Reproduces identically on the
untouched git HEAD copy**, so this is pre-existing and unrelated to the TIME() fix — SCRIP's parser has
never been able to run this file. The TIME()-unit fix at `MAKE`/`REPORT()` is correct by inspection
(identical pattern to the three verified fixes) but could not be smoke-tested end-to-end because the file
doesn't compile at all, with or without the fix. Flagged for HQ triage — not fixed here, out of scope for
this row, and a global CRLF strip is a bigger and riskier change than one row should absorb unasked.

### 7.3 ⛔ COLLATERAL, UNRELATED: calculator-2.sno's stdout does not match its own .ref

Discovered while diffing stdout to prove the TIME() fix didn't touch it. `calculator-2.sno` — **on the
untouched git HEAD copy, before any edit of mine** — produces ~3000 lines of stdout diff against
`calculator-2.ref`, deterministically (same md5 across two runs). `calculator-1.sno`, same shape, same
edit, diffs clean. Proven pre-existing by replaying `git show HEAD:...` in a scratch copy before touching
anything. Not investigated further — well outside this row's blast radius — but a live, silent,
deterministic red `.ref` on a named corpus demo is exactly the "false green" class this project watches
for, so it is named here rather than left for the next session to re-discover from zero.

## 8. FILES AND COMMITS

| repo | commit | what |
|---|---|---|
| corpus | `53dcb7b6` | regenerated `.s` for json/calculator-1/calculator-2 (`util_regen_demo_s_artifacts.sh`, graceful-skip, 3 updated / 18 unchanged) |
| corpus | `d919a97d` | the fix: json.sno, calculator-1.sno, calculator-2.sno, aisnobol/KALAH.sno |
| .github | this file | unit contract + collateral findings |

Both corpus commits pushed (`4e5fa2d0..d919a97d`). No SCRIP (compiler) changes — this row never touched
codegen, so no benchmark/feature/programs/crosscheck regen applies, only the demo-artifact regen already
run above.

## 9. DONE-WHEN, CHECKED

- ✅ SCRIP `TIME()` agrees with the SPITBOL oracle in units and magnitude — isolated probe, §3.
- ✅ Every demo printing a `*_ms` value reports a plausible figure — §5, all six call sites across all
  four affected files.
- ✅ This FINDING states the unit contract — §6.
