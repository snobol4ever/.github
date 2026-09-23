# FINDING — ERROR 242 "function return from level zero" fires after a SETEXIT-trapped retry then FRETURN; both standing SnoM master reds are this one bug (hq_snobol4, 2026-09-23)

## Symptom

Both of the SnoM master's two standing (pre-existing, non-xfail) reds — `dupl_size_replace_branch_1`
and `size_keyword_replace_branch_1` (both in the `beauty_suite_ReadWrite_driver` / `ReadWrite.inc`
family, `corpus/include/ReadWrite.inc`) — fail identically:

```
scrip: error 242: function return from level zero
```

Both are the SAME root cause, not two bugs. Tree: SCRIP `3312ba787`, corpus `39ca43e26`.

## Minimal reproduction (8 lines, no -INCLUDE needed to see the shape, but using the real library to
## keep the exact trap sequence)

```
-INCLUDE 'global.inc'
-INCLUDE 'ReadWrite.inc'
        Read('/nonexistent/directory/nope.txt')                           :S(T3BAD)
        OUTPUT = 'T3 PASS: Read FRETURN on inaccessible path'
        :(DONE)
T3BAD   OUTPUT = 'T3 FAIL: Read should have FRETURNed on inaccessible path'
DONE
END
```
(run from `corpus/include` so `-INCLUDE` resolves). Oracle (`sbl -bf`): `T3 PASS: Read FRETURN on
inaccessible path`, rc=0. SCRIP: `error 242: function return from level zero`, rc=1.

## Mechanism

`ReadWrite.inc`'s `Read()` (lines ~14-26):
```
Read           rdPrevXit      =    SETEXIT(.ReadSpit)
               rdPrevLim      =    &ERRLIMIT
               &ERRLIMIT      =    1
               INPUT(.rdInput, 8, , fileName)                                        :F(ReadNo)
               SETEXIT(rdPrevXit)
               &ERRLIMIT      =    rdPrevLim                                         :(ReadGo)
ReadSpit       SETEXIT(rdPrevXit)
               &ERRLIMIT      =    rdPrevLim
               INPUT(.rdInput, 8, fileName '[-l131072]')                             :F(FRETURN)
```
CSNOBOL4's 4-arg `INPUT()` form is tried first under `&ERRLIMIT=1` with a `SETEXIT(.ReadSpit)` trap
armed (SPITBOL raises a FATAL error on the 4-arg form rather than an ordinary match failure, so a
plain `:F()` branch can't catch it — the trap is required). On a genuinely inaccessible path, the
FATAL fires, the trap resumes execution at `ReadSpit` (a label INSIDE `Read()`, reached via the
runtime's error-trap dispatch rather than by falling through the preceding statement), which retries
with SPITBOL's own 3-arg form. That ALSO fails (ordinary match failure this time, no trap needed) and
hits `:F(FRETURN)` — an ordinary function-failure-return. This is where SCRIP raises ERROR 242
instead of correctly returning FAILURE from `Read()` to its caller.

**Reading of the cause:** `rt_kw_return_level_zero()` (`src/runtime/core/core.c:2820`) is the runtime's
"tried to pop below the outermost call frame" guard — `rt_chain_enter`'s prologue
(`src/runtime/runtime_eval.c` asm, `rt_chain_enter`/`rt_chain_enter_v`) seeds it as the sentinel γ/ω
continuation pair for the OUTERMOST frame. `FRETURN`'s runtime implementation must be walking/popping
some call-level counter or continuation chain to find "the enclosing function's failure
continuation," and the SETEXIT-trap resume (jumping into `ReadSpit` via the trap dispatcher rather
than via an ordinary call/return sequence) appears not to correctly preserve or restore whatever level
marker `FRETURN` later reads — so by the time `:F(FRETURN)` executes, the runtime believes it is
already at the outermost frame (level zero) even though we are still lexically and dynamically inside
`Read()`.

**Not confirmed further than this** — I did not trace the exact call-level counter/data structure or
prove definitively where it goes wrong; this is as far as ASM-diff/read-only investigation got before
stopping to route it, per the ownership boundary below.

## Ownership — NOT mine to land

`rt_kw_return_level_zero`, `rt_chain_enter`/`rt_chain_enter_v` (`runtime_eval.c`), and the call-level
bookkeeping they guard are core runtime plumbing — the `icn_zf_*` naming on the adjacent driver-side
continuation (`icn_zf_exit_γ`, `src/driver/scrip.c:102`) that shares this same sentinel pattern is one
signal this machinery is not SNOBOL4-exclusive. This matches this row's own **prior** cursor entry
(2026-09-22, topic `snobol4-c2bb-regression-58-code-eval-indirect-entries-broken-since-your-14-commit-landing`):
ERROR 242 in this exact shape (`by_name_dispatch.c`/`runtime_eval.c`/`rt.c`) was already named there as
a shared-node regression, not landable directly. That regression has since been LARGELY cured by the
officers (SnoM m3 FAIL dropped 58 → 2, m4 44 → 7 across intervening landings) — these two entries are
the last SnoM-master remnant of it, now localized to the specific SETEXIT-trap-resume-then-FRETURN
shape above, which is more specific than the original report.

## Ask

Routed to `cfo` (topic `snobol4-error-242-setexit-trap-resume-then-freturn`) same sitting, per RULES.md
ASK/FLIP protocol — not blocking, recorded and moving on.
