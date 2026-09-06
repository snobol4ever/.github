# FINDING 2026-09-05 seat04 — two `test_gate_sno_*` scripts execute `./scrip` with no staleness guard

**Seat:** seat04 · **Mode:** FLEET-12 (hq_S lane) · **Tree:** SCRIP `d12ece9f3` · corpus `590684477` · .github `2168508d`

## What

`make test`'s own ARM-15 census (inside the umbrella/freshness meta-gate that runs as part of the blocking
`make test` target) flags two scripts that call `./scrip` directly without the shared `gate_require_fresh()`
staleness check every other `test_gate_*` carries:

```
gate(s) that execute ./scrip with NO freshness guard: test_gate_sno_lastno_across_call_return.sh test_gate_sno_proc_own_name_byname_mid_return.sh
```

Full run: `census #2, PRINTED DENOMINATOR: gates=93 wired=91 uncovered=2` — these are the 2 uncovered.
This makes `make test` exit nonzero (`⛔ GATE FAIL: 1 of 34 check(s) failed`) even though every substantive
suite/board in the run is clean (SNOBOL4 master `m3 PASS=1689 FAIL=0 · m4 PASS=1689 FAIL=0`).

## Why this isn't mine to cure here

Found only as a side effect of running the full `make test` as extra diligence on an unrelated row
(`snobol4-csnobol4-ord-labelcode-maxint-unimplemented-builtins`, hq_S lane — ORD/LABELCODE/&MAXINT). Both
flagged scripts were last touched by hq_U at `47968068e` (2026-09-05 19:47:18 CDT), **before** my session's
starting tree (SCRIP `f3f8e252b`, 19:49:15 CDT) — pre-existing, not caused by anything in this session's
diff (`src/runtime/core/core.c`, `src/runtime/keywords.c`, `src/runtime/snobol4_system_fns.h` — no
`scripts/*.sh` touched). Retrofitting the guard into two scripts I don't otherwise own risked scope creep
on a landing that was otherwise clean and verified.

## Repro

```
cd SCRIP && make test 2>&1 | tail -60
```
(note: pipe through `tee`/`tail` masks `make`'s real exit code — check `${PIPESTATUS[0]}` or the bare
`make test` exit status, not a pipeline tail's.)
