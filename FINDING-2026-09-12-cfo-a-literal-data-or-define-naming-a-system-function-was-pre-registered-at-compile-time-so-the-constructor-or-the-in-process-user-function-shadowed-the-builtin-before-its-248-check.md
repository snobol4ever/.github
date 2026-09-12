# FINDING 2026-09-12 cfo — a literal DATA or DEFINE naming a system function was pre-registered at COMPILE time, so the datatype constructor (both modes) or the in-process user-function entry (mode 3) shadowed the builtin before its ERROR 248 check could run

**Seat** cfo · **Mode** TRIO (CEO-619) · **Row** `snobol4-data-of-data-and-define-of-define-are-not-protected-where-spitbol-raises-248` (minted by me on the ceo's CEO-625, which found the gate red on three seats' binaries) · **Oracle** `sbl -bf`

## The claim, measured

`test_gate_sno_system_fn_protection_matches_spitbol.sh` cuts three witnesses live from the oracle for each of 95 names -- `DEFINE('NAME(X)')`, `OPSYN('NAME','SIZE')`, `DATA('NAME(X)')` -- and 283 of 285 agreed. The two that did not were the SELF-NAMED cases:

| witness | oracle | m3 before | m4 before |
|---|---|---|---|
| `DATA('DATA(X)')` | ERROR 248 | `ok` | `ok` |
| `DEFINE('DEFINE(X)')` | ERROR 248 | `ok` | ERROR 248 |
| `DEFINE('SIZE(X)')`, `DATA('SIZE(X)')` (controls) | ERROR 248 | ERROR 248 | ERROR 248 |

Neither statement even FAILED (`:F` not taken): the runtime's 248 checks -- which exist in every DATA and DEFINE entry (`core_DATA_register`, the by-name `BID_DATA` arm, `_DEFINE_`) -- were never reached. A one-line trace in `_DEFINE_` proved it: `DEFINE('SIZE(X)')` enters it in both modes, `DEFINE('DEFINE(X)')` enters it in mode 4 only.

## Two compile-time pre-registrations, one shape

1. **DATA, both modes.** `lower_snobol4.c` pre-registers every literal `DATA(...)` spec at LOWERING time (`dat_register(sp)`), so that the datatype exists for later static decisions. `DATA('DATA(X)')` therefore created a datatype named `DATA` with constructor `DATA(X)` before the program ran, and the by-name dispatcher resolves a datatype constructor BEFORE a builtin (`if (dat_find_type(name)) return 1;`). Proof: after that statement `DATATYPE(DATA('a'))` printed `DATA` and `X(...)` printed `a` -- the builtin was gone, replaced by a record constructor. Same in both media because the registration is baked into what is emitted.
2. **DEFINE, mode 3 only.** `driver_label.c: prescan_defines()` walks every statement whose subject is a literal-prototype `DEFINE(...)` and registers the spec into the runtime's user-function table (`DEFINE_fn` / `DEFINE_fn_entry`) -- in the COMPILER's process. Mode 3 runs in that same process, so the by-name call `DEFINE` found a registered "user function" named `DEFINE` (`core_call_registered_fn`, consulted before the builtin) and returned null. Mode 4 runs in a fresh process whose table holds only what the program's own DEFINE executions put there, so it reached `_DEFINE_` and raised 248. The lowerer already skips protected names at its four DEFINE sites; this fifth registrar, in the driver, did not.

## The cure (two one-liners, the same predicate the lowerer already uses)

- `lower_snobol4.c`: the DATA pre-registration is skipped when the type name is a system-function name (`sn4_sysfn_protected(nb)`), so the call reaches the runtime and raises 248 like every other protected name.
- `driver_label.c`: `prescan_defines` skips a spec whose function name is protected. The header `snobol4_system_fns.h` is included in the driver for it.

## Measured after

Gate 285/285, both modes, live oracle. `DEFINE('DEFINE(X)')`, `DATA('DATA(X)')` and the constructor probe all raise 248 in mode 3; mode 4 unchanged where it was right. Controls: all 42 gates named `sno_*`, `snobol4_*`, `*define*`, `*data*` green (145 s); both DEFINE alternate-entry gates green; `make preflight` 33/0. Blast radius is exactly the set of programs that DATA or DEFINE a protected name, which the oracle refuses with 248 -- there is no program that could have depended on the old reading except through the constructor shadow, which is itself the defect.

## What it teaches

A compile-time pre-registration that exists to let the emitter make static decisions is also a RUNTIME FACT in the mode that shares the process. Every such registrar owes the runtime's own validity checks, or the mode split appears as "mode 4 is right and mode 3 is generous" -- the reverse of the shape the previous cure had, and the same cause: state visible to one medium and not the other.
