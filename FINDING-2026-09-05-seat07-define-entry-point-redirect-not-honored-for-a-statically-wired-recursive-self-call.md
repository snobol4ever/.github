# FINDING — `DEFINE(name, altlabel)`'s explicit entry-point redirect is not honored when a function calls itself by name from its own body

**Seat:** seat07 · **Date:** 2026-09-05 · **Row:** `snobol4-error-5-is-a-catch-all-for-three-spitbol-outcomes`
**Tree:** SCRIP `1d7ec5246`+local · corpus `a6e836ea6`+local · oracle `/home/resources/x64/bin/sbl -bf`

## 1. Where this came from

Chasing this row's "loud member" (`gimpel-linked-list-functions.sno`: a VALID program — oracle runs it
clean — that SCRIP refuses with a bogus ERROR 5) led to a real, upstream field-shift bug in the parser
(fixed by this row, see the task LEDGER: an omitted LEADING call argument, `F(, 'y')`, shifted the
remaining arguments left instead of leaving the omitted slot's own position null). Fixing that let the
fixture run six of its eight expected output lines further — into `COPYL.INC`'s recursive list-copy —
before hitting **`ERROR 246 -- stack overflow`** instead of the earlier bogus ERROR 5. This FINDING is
the newly-exposed, separate defect underneath that overflow.

## 2. The mechanism, isolated

`COPYL.INC` uses a classic SNOBOL4/SPITBOL idiom: a function redirects its OWN future (including
recursive) calls to a different label mid-execution, via `DEFINE`'s optional second argument:

```
COPYL   DEFINE('COPYL(L)', 'COPYL_1')   * from now on, calls to COPYL(...) should enter at COPYL_1
        T = TABLE(100)                  * one-time setup (memo table for circular-list safety)
        COPYL = COPYL(L)                * recursive call -- MEANT to land at COPYL_1, not re-run setup
        DEFINE('COPYL(L)T')             :(RETURN)   * restore the original entry point before returning
COPYL_1 ...                             * the real copying logic
```

Minimal witness (no lists, no DATA type, nothing but the redirect itself), `SCRIP_DEBUG_APPLY` unset:

```
        DEFINE('FOO(L)')                :(FOO_END)
FOO     OUTPUT = 'in-setup-FOO'
        DEFINE('FOO(L)', 'FOO_1')
        OUTPUT = FOO(L)
        DEFINE('FOO(L)')                :(RETURN)
FOO_1   OUTPUT = 'in-FOO_1'
        FOO = 'done'                    :(RETURN)
FOO_END
        OUTPUT = FOO('x')
END
```

**Expected** (and what real SPITBOL does): `in-setup-FOO`, then ONE recursive entry at `FOO_1`
(`in-FOO_1`), then it returns. **SCRIP: `in-setup-FOO` repeats forever** (stack overflow) — the
recursive `FOO(L)` call keeps re-entering label `FOO` (the setup arm), never `FOO_1`, so the
redirect never takes effect and the "one-time setup" runs on every recursive call, unbounded.

## 3. Root cause, as far as traced

The RUNTIME side of this looks correct: `_DEFINE_` (`core.c:3024`) calls `DEFINE_fn_entry()` when a
second argument is given, which correctly updates the registered `FNCBLK_t.entry_label` for the name
(`core.c:2852`); `FUNC_ENTRY_fn()` (`core.c:3109`) reads that field fresh on every lookup, not cached.
**But `driver_call.c`'s dynamic-call resolver (`call_user_function`, the one that consults
`FUNC_ENTRY_fn`) is not what a same-file self-call goes through.** SCRIP's whole design compiles
statement-to-statement control transfer as compile-time-wired jumps (CLAUDE.md Architecture: "Ports
are wired at compile time... the wiring IS the execution, no runtime dispatch") — a call to a name
that is ALSO a label visible in the same translation unit is the textbook case for that static wiring,
and the evidence above is consistent with the recursive `FOO(L)`/`COPYL(L)` call sites being wired
directly to label `FOO`/`COPYL` at compile time, never touching the dynamic `FUNC_ENTRY_fn` path that
`DEFINE`'s redirect actually updates. **Not yet confirmed at the codegen/BB level** — this FINDING
stops at the black-box behavior plus the two runtime functions read above; nobody has yet traced which
BB template or lowering decision picks the static-wire path over the dynamic one for this shape.

## 4. Why this is a separate row, not a same-sitting patch

- It is a different subsystem (function-entry compilation / static box-wiring vs. the parser argument-
  list bug this row actually owns) with its own investigation still to do at the codegen level.
- It is already a KNOWN, independently-catalogued defect *class*, not a one-off: `corpus/tests/snobol4/
  ALL.csv`/`ALL.xfail` carry **`user_function_replace_4`** and **`user_function_replace_7`** (rows 1816–
  1817, class `define-redefinition-ordering`, re-verified 2026-09-04 by seat15) for a *related but
  distinct* symptom — a SECOND `DEFINE` retroactively changes what an ALREADY-EXECUTED FIRST call
  printed (hoisted/declarative resolution). This FINDING's shape (a redirect not taking effect on a
  *future*, same-name recursive call) is the mirror-image gap in the same general area: `DEFINE`'s
  redefinition semantics are under-specified end-to-end in SCRIP, and unifying the fix for both shapes
  wants one deliberate design pass, not a patch bolted onto an unrelated error-numbering row.
  `gimpel-linked-list-functions.sno` stays red (stack overflow) until this lands.

**Routed, not silently absorbed:** flagging to hq_P (this row's lane) to mint as its own row — same
discipline seat08 used for the `core_err_msgs` table finding this row built on.
