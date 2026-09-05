# FINDING 2026-09-05 seat04 — DATA/DEFINE/OPSYN protection errors print `(0)` / `in statement 0`, never the real file/line

**Seat:** seat04 · **Mode:** FLEET-16 (hq_C lane) · **Tree:** SCRIP `1d7ec5246` + this row's fixes

## 1. Task and how it surfaced

Task `snobol4-data-of-a-system-function-name-is-error-248-and-the-continuing-error-line` (GOAL: match
the oracle's `test6.spt(16) : ERROR 248 -- attempted redefinition of system function` line exactly).
`core_runtime_error` (core.c:2170) was changed to print `%s(%ld) : ERROR %03d -- %s` using `g_file`,
`g_line`, `code`, `msg` -- format matches the oracle byte for byte. The VALUES don't: every protected-name
witness prints `(0) : ERROR 248 -- ...` regardless of which file or line actually called DATA/DEFINE/OPSYN.

## 2. Root cause, confirmed under gdb (not guessed)

`g_line`/`g_stno` are only ever assigned in one place: `rt_stmt_enter(stno, line)` (keywords.c:443).
Breakpointing both `rt_stmt_enter` and `core_runtime_error` and running a one-statement `DATA('ITEM(X)')`
repro: `core_runtime_error` hits first, `rt_stmt_enter` is **never called at all**. Backtrace at the error:

```
#0 core_runtime_error (code=248, msg="attempted redefinition of system function")
#1 kwb_error                                             keywords.c:214
#2 try_call_builtin_by_name_bl (fn="DATA", ...)           by_name_dispatch.c:5906
#3 rt_call_arr_impl                                       by_name_dispatch.c:3708
#4 rt_call_arr_bl                                         by_name_dispatch.c:3659
#5 0x... ?? ()   <- JIT-generated BB code, no symbol table (mode 3 sealed slab)
```

Cross-checked on mode 4's plain-text `.s` (no JIT to fight): `grep -n rt_stmt_enter` on the emitted
assembly for the same one-statement program returns **nothing** -- the call is never emitted at all for
this program, not merely skipped at runtime. DEFINE's pre-existing protection check (core.c:3032,
`_DEFINE_`) goes through the identical `kwb_error` -> `core_runtime_error` path and has the identical gap;
it was never visible before because the pre-existing format (`"** Error %d in statement %d"`, g_stno only)
was never diffed against the oracle's `file(line)` shape.

## 3. Why not fixed here

`rt_stmt_enter` is the codegen's per-statement bookkeeping hook (also drives `&STCOUNT`/`kw_stlimit`).
Whether it's conditionally emitted only for programs that reference certain keywords, or unconditionally
absent for DATA/DEFINE/OPSYN's declarative dispatch specifically (plausible: these three are meant to take
effect before normal control flow, per SNOBOL4 forward-reference semantics, and may be wired through a
separate pre-pass that never calls it) is not yet determined -- would need tracing a program that DOES emit
`rt_stmt_enter` calls to find the emission site and see why this class of statement doesn't reach it.
This is exactly what task's GOAL called "the whole error-path population" (hq_P's prior note that the
master can't carry an error-path witness because SCRIP's diagnostic format differs) -- a codegen-wide
question with performance implications (unconditional per-statement bookkeeping vs. today's apparent
opt-in), not a one-file fix, and out of scope for a DATA()-protection row.

## 4. What IS fixed and proven (this row's actual scope)

- `DATA()` now honours system-function protection like DEFINE/OPSYN (gate:
  `test_gate_sno_system_fn_protection_matches_spitbol.sh`, 95 names x 3 forms = 285 witnesses, diverge=1,
  the one remaining divergence is the pre-existing DEFINE-self case, separately findinged).
- The diagnostic CONTENT and FORMAT (`ERROR NNN -- text`) match the oracle; only the file/line VALUES are
  wrong, for the reason above.
- New gate `test_gate_sno_data_protect_mode4.sh` proves this end-to-end on mode 4 (compile, link, run):
  ERROR 248 fires at runtime (not a compile-time abort -- an earlier version of this row's fix mistakenly
  raised it from the lowering prescan, caught by this same investigation and corrected), and execution does
  not continue past the erroring statement.

## 5. Repro (for whoever picks up the location-tracking gap)

```
	DATA('ITEM(X)')
	OUTPUT = 'unreached'
END
```
Oracle (`sbl -bf`): `w.sno(1) : ERROR 248 -- attempted redefinition of system function`, exit 0.
SCRIP (mode 3 or 4): `(0) : ERROR 248 -- attempted redefinition of system function`, exit 1 (also: the exit
code itself diverges from the oracle's 0 -- core_runtime_error's fallthrough is an unconditional `exit(1)`
for any code not in `core_err_is_terminal`/`core_err_is_fatal`; whether 248-class errors should exit 0 like
the oracle is a separate policy question, not chased down here either).
