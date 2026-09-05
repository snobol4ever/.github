# FINDING 2026-09-05 seat04 — `DEFINE('DEFINE(X)')` is FREE in SCRIP, PROTECTED (ERROR 248) in the oracle

**Seat:** seat04 · **Mode:** FLEET-8 (hq_C lane) · **Tree:** SCRIP `df9fe6af0` + this row's DATA()-protection cure

## 1. How it surfaced

Found while curing row `snobol4-data-of-a-system-function-name-is-error-248-and-the-continuing-error-line`
(DATA() didn't honour the protected system-function set the way DEFINE/OPSYN do). Extending
`test_gate_sno_system_fn_protection_matches_spitbol.sh` with a DATA arm and re-running it across all 95
names turned up exactly one divergence, on a name the new DATA arm doesn't even touch:

```
DIVERGE DEFINE     DEFINE: oracle=PROT scrip=FREE
```

i.e. `DEFINE('DEFINE(X)')` — DEFINE attempting to redefine itself — raises `ERROR 248 -- attempted
redefinition of system function` under `sbl -bf`, and prints `ok` (no error at all) under SCRIP.

## 2. Confirmed pre-existing, not caused by this row

This row's changes touch DATA()'s three call paths (`lower_snobol4.c`'s literal prescan,
`by_name_dispatch.c`'s `BID_DATA` case, and `core_DATA_register` in `core.c`) plus
`core_runtime_error`'s terminal print format. None of them touch DEFINE's own protection check
(`core.c:3023`, `sn4_is_system_fn(probe->name)`) or its prescan handling. The gate showed this same
single divergence before and after this row's edits.

## 3. Not chased down — flagged, not fixed here (DATA is this row's brief, not DEFINE)

DEFINE has at least four places in `lower_snobol4.c` that special-case the literal string `"DEFINE"`
as a *dispatch keyword* (lines ~55, ~164, ~439, ~899, plus the prescan at ~2434) in addition to the
runtime check at `core.c:3023`. A plausible mechanism: one of these `!strcmp(name, "DEFINE")` branches
treats a call literally named DEFINE as "the DEFINE statement itself" before ever reaching the point
where `sn4_is_system_fn` would be asked "is the name **being defined** a protected name" — i.e. the
self-referential case (`DEFINE('DEFINE(X)')`, where DEFINE is both the dispatcher and the target)
may fall through a seam between "this call IS a DEFINE" and "this call DEFINEs a function called
DEFINE". Not verified by a debugger session — this is a hypothesis for whoever picks it up, not a
diagnosis.

## 4. Repro

```
DEFINE('DEFINE(X)')
OUTPUT = 'ok'
END
```
`sbl -bf` (correctness oracle): `... : ERROR 248 -- attempted redefinition of system function`.
SCRIP (mode 3, `--run`): prints `ok`.

## 5. Evidence

`bash scripts/test_gate_sno_system_fn_protection_matches_spitbol.sh` (post this row's DATA cure):
`SNO_SYSTEM_FN_PROTECTION names=95 witnesses=285 diverge=1` — the one line quoted in §1, every other
witness (all 95 names × DEFINE/OPSYN/DATA) agrees with the oracle.
