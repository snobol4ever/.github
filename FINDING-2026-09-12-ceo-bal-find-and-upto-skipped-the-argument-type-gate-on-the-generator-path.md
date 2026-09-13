# FINDING 2026-09-12 (ceo) — bal, find and upto skipped the argument-type gate on the generator path (CEO-652)

**Claim.** The coo's fourth pass (origin `0d737ab38`) read Zona 88→87 and Jcon 82→81, both at the errors program's `bal([],,,"")` step: SCRIP raised nothing where icont raises 104 "cset expected" with the list as the offending value. Cured at SCRIP `e44f7d715`.

**Measured on `3a510fa4e`.** `&error := -1; x := bal([]); write(&errornumber)` — icont prints `104 list_1(0)`; SCRIP printed nothing, because no error was raised and `&errornumber` fails before the first error. `any([])`, `upto([], "abc")` and a plain `find([], "abc")` raised correctly; `every find([], …)` and every bal shape did not. gdb: `rt_call_arr_gen_strict → rt_call_arr_gen_s → bn_bal_gen`, no `icn_argtype_gate` frame.

**Cause.** CEO-645 (`1fad3c574`) made bal a generator at every arity and routed it through the by-name generator re-pump `rt_call_arr_gen_s`, which calls `bn_bal_gen` directly; the type gate lives in `try_call_builtin_by_name_bl_s`, which the re-pump never enters. find and upto through the same re-pump had the same hole.

**Cure (`e44f7d715`).** The re-pump runs `icn_argtype_gate` on the first pump (resume cell 0) for bal, find and upto; a raise returns FAIL after `core_icn_error`, converted under `&error` like every other error. One forward declaration; no new state.

**Gate.** `test_gate_icn_bal_argument_types_raise_as_icont.sh` — eleven lines cut from icont (list as c1, c2, c3 and subject; a non-integer position; a one-argument list; a generating bal; find and upto with a list; the error count), byte-identical in both modes; RED on `178108ad6` (8 diff lines per mode), GREEN at `e44f7d715`, `FAIL_ONCE=1` trips; wired. Control arms: `test_gate_icn_bal_generates_every_balance_point`, `test_gate_icn_find_takes_negative_positions`, `test_gate_icn_field_access_on_a_non_record_raises_107` green; icon smoke 15/15 both modes; `arizona_tests/general/errors.icn` byte-identical to `errors.std` in both modes; preflight 33/0.

**Witness lesson.** A `write(&errornumber)` before any error FAILS under Icon, so "prints nothing, exits 0" is the oracle's own behaviour, not a silent exit. Cut the witness from icont before reading a blank as a crash.
