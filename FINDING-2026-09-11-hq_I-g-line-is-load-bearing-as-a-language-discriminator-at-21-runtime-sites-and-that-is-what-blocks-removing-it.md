# FINDING 2026-09-11 hq_I — `g_line` is load-bearing as a LANGUAGE DISCRIMINATOR at 21 runtime sites, and that is what blocks removing it

**Measured on** SCRIP `0e4539a65` · corpus `3708c8ab9` · `RT_OPT=-O0` · measurer hq_I,
2026-09-11 ~21:1x UTC. Census run per **CEO-405** ("ask what STATE you are moving and grep its
carriers"), against **CEO-551** (Lon's order: get rid of the global; r10 does not reach it).

## The blocker, in one line

```c
int core_icn_active(void) { extern long g_stno; extern long g_line; return g_stno == 0 && g_line > 0; }
```
`src/runtime/core/core.c:343`

`g_line` is not only the diagnostic cursor. Together with `g_stno` it **is** the runtime's answer to
*am I running Icon?*, and **21 call sites across five runtime files** branch on it:
`arithmetic.c` (2), `pattern_match.c` (7), `core.c` (4), `builtins/gen_runtime.c` (3),
`by_name_dispatch.c` (3), plus the declaration and definition.

Those sites are not cosmetic. They gate whether an **Icon run-time error is raised at all** —
201/202 (division by zero, mod), 204, 101/103 (integer/numeric expected), 110, 113, 114. Verified
live: `write(1 / 0)` reports `Run-time error 201 / File dz.icn; Line 2 / division by zero`, and that
raise is `arithmetic.c:255` guarded by `core_icn_active()`.

**So a change that lets `g_line` read 0 in Icon does not merely blank a line number in a report — it
silently stops raising a family of Icon run-time errors.** Failure mode: programs that should abort
with error 201/101/113 instead return `&fail` or a wrong value and keep running. That is the worst
possible shape for a regression, because every board still prints and nothing crashes.

## Why no existing gate sees this

`test_gate_emit_no_lang.sh` **passes**, and correctly:

```
OK: LANG-BLIND — no language-identity identifier in src/emitter or src/templates.
```

It is blind here twice over, and both are structural, not oversights:

1. **Scope.** It examines `src/emitter` and `src/templates`. This discriminator lives in
   `src/runtime/`, which the gate never looks at.
2. **Shape.** It greps for language-identity *identifiers* — a `LANG_*` enum, a `:lang` attr, a
   language name. `core_icn_active` encodes language identity in the **values of two unrelated
   globals**. There is no name to find. A grep-for-names gate cannot see a fact encoded in a
   predicate over data.

⭐ **The general form, which is the reusable part:** a rule enforced by grepping for names is only as
good as the assumption that the thing being banned has a name. Language identity smuggled through
`g_stno == 0 && g_line > 0` is exactly as much a violation of *language identity stops at lower* as a
`LANG_ICON` enum would be, and it is invisible to the instrument written to prevent it. When a gate
reports OK, ask what shape of violation it is capable of detecting.

## Full census of the state being moved

**46 `g_line` references** (excluding generated `.tab.c`/`.lex.c`). Four distinct carriers of "the
current source line", which is the real answer to CEO-405's question:

| carrier | where | role |
|---|---|---|
| `g_line` | `keywords.c:28` | the global cursor, stamped per statement |
| `g_icn_act[lv].line` | `core.c:339` | per-activation: the line its frame was CALLED from |
| `co_t.create_line` / `cur_line` | `rt_coexpr.c:233,260,264` | per co-expression, saved and restored across activation |
| `g_lastline` | `keywords.c:524` | SNOBOL4's previous-statement line |

Readers, classified by whether the line is a compile-time constant where it is needed:

- **Icon trace — mostly converted already.** `bb_suspend.cpp:33` passes the suspend's own line as
  ARG 4, a compile-time constant (the `cc3f4e817`/`a1db51e6b` work). Remaining readers:
  `trace_print_icon` (`core.c:199`, the CALL/RETURN/RESUME events) and `rt_icn_trace_coexpr`
  (`core.c:229`), which today get correct values by *runtime reconstruction* via
  `icn_act_restore_call_line` rather than by carriage.
- **Icon run-time error and traceback** — `core.c:398,426,433,2622-2627`. Raised from inside runtime
  helpers, where the line is NOT a compile-time constant; it IS one at the emitted call site.
- **`&line`** — ⭐ **already done for Icon, and this corrects the ceo's reason (2) as it applies to
  my lane.** `lower_icon.c:439` lowers `&line` to an `IR_LIT_INTEGER`; Icon never reads `g_line` for
  it. The by-address exposure the ceo flagged — `keywords.c:214` `(int64_t *)&g_line` and the
  by-name write at `by_name_dispatch.c:6955` — is the **SNOBOL4** `&LINE` route, not Icon's. It still
  has to be answered, but it is hq_P/hq_S's keyword machinery, not Icon lowering.
- **The language discriminator** — the 21 sites above. **This is the one that blocks removal.**
- **SNOBOL4 statement machinery** — `rt_stmt_enter` (`keywords.c:521-525`) writes `g_stno`,
  `g_line`, `g_lastline` together as the SPITBOL termination-report context.

## What this means for the order

"Get rid of the global" stays right, and the trace half is already most of the way there. But the
ordering is now forced, and it is not the order the reference count suggests:

1. **Replace the discriminator first.** `core_icn_active()` must answer *which frontend produced this
   program* from something that is not a line number. Until it does, every later step risks silently
   disabling Icon error raising. This is also a standing violation of *language identity stops at
   lower* that should be cured on its own merits, with its own gate — one that looks in
   `src/runtime/` and can see a predicate, not just a name.
2. Then finish carriage for the trace CALL/RETURN/RESUME events and the error/traceback path,
   replacing reconstruction with the compile-time constant.
3. The SNOBOL4 `&LINE`-by-address and `rt_stmt_enter` routes are a separate lane's work and should
   not be bundled.

⛔ Step 1 is a shared-node change touching five runtime files and the semantics of seven Icon error
numbers. It wants hq_U's co-sign (confirmed, CEO-551) and a control arm on every frontend, and it is
emphatically not a one-sitting flip row.
