# FINDING — `core_err_msgs[40]` is not indexed by official SPITBOL error numbers, at all

**Seat:** seat08 · **Date:** 2026-09-05 · **Mode:** FLEET-8 (hq_P lane, SNOBOL4 ONLY)
**Row:** `snobol4-testpgms-test1-traps-29-runtime-errors-under-spitbol-scrip-traps-3`
**Tree:** SCRIP `df9fe6af0` · corpus `d58a796fa` · oracle `/home/resources/x64/bin/sbl -bf`

## 1. The defect, measured directly against the manual

`src/runtime/core/core.c:2082`, `static const char *core_err_msgs[40]`, is read by
`core_runtime_error(int code, const char *msg)` (`core.c:2125`) as `msg = core_err_msgs[code]` whenever
a call site passes `NULL` for `msg`. **The array's index has no relationship to SPITBOL's own numbering
of the same errors.** Confirmed against the authoritative source, not assumed:

```
$ pdftotext -layout /home/resources/spitbol-manual-v3.7.pdf - | sed -n '11309,11374p'
 Error numbers   ... The number is provided in &ERRTYPE, and the text in &ERRTEXT.
   22   Undefined function called
   29   Undefined operator referenced
   38   Goto undefined label
   41   FIELD function argument is wrong datatype
```

Cross-checked against `core_err_msgs[]`'s own text at the SAME conceptual message:

| Message (near-identical text) | `core_err_msgs[]` index | Official SPITBOL number (manual) |
|---|---|---|
| "Undefined function or operation" | **5** | **22** |
| "Undefined or erroneous goto" | **24** | **38** |

The goto row is not new — seat12 already caught it in passing on 2026-08-27 (LEDGER,
`conform-setexit-noop` task: *"core.c's small core_err_msgs[40] default-message array has 'Undefined or
erroneous goto' at index 24, NOT 38 -- that array is NOT a SPITBOL-official-code table"*) and correctly
called it "a latent, unrelated pre-existing oddity" out of scope for that row. **This FINDING is the
follow-through**: a second, independently-measured instance (index 5 vs. official 22) proves it is not
an isolated off-by-one, and the manual's own official list runs to at least 61 numbered errors (not 40),
so the array is also too small to hold the full table even if reindexed.

## 2. Why this matters beyond cosmetics

`&ERRTYPE` is not decorative — it is the mechanism every SETEXIT-based diagnostic (including SPITBOL's
own vendored `testpgms` suite) prints and, in real programs, branches on. **A runtime error that SCRIP
correctly detects AND correctly routes to `core_runtime_error()` will still fail a byte-exact oracle
diff if the code number is wrong**, independent of whether the underlying detection logic is right.
Confirmed live:

```
$ S4E_HOME=... SETEXIT(.ERRH); X = NOSUCHFN(1)     (&ERRLIMIT=1000 set first — see § 3 below)
oracle:  CAUGHT ERRTYPE=22 ERRTEXT=undefined function called
SCRIP:   CAUGHT ERRTYPE=5  ERRTEXT=Undefined function or operation
```

The trap fires correctly in both — this is a pure numbering defect, not a detection defect, and it sits
underneath *every* error-path fix anyone lands on this codebase until it is corrected. It is the reason
a future, otherwise-perfect fix for "undefined operator referenced" (see the sibling FINDING/LEDGER on
this same row, R-8 `opsyn_unary_target`) still will not byte-match the oracle unless that fix's call site
passes the literal, manual-sourced number **29**, not whatever `core_err_msgs` would suggest.

## 3. A related trap-arming gap, worth naming so it isn't re-discovered as a mystery

Both the oracle and SCRIP silently bypass SETEXIT and crash-print directly, with garbage-looking
diagnostics, when `&ERRLIMIT` is left at its default (0) before `SETEXIT(...)` is armed — this is NOT a
SCRIP-vs-oracle divergence (both do it), just a probe-construction gotcha worth recording once:
`test1.spt` itself sets `&ERRLIMIT = 1000` before `SETEXIT(.ERRORS)` for exactly this reason (line 10 of
`corpus/packages/snobol4/spitbol_testpgms/test1.spt`). Any future minimal witness for a SETEXIT-based
error must do the same or it will misleadingly look like the trap doesn't route at all.

## 4. Scope — this is NOT this row's fix, and is bigger than one row

Correcting this properly means: (a) transcribing the manual's full numbered list (61+ entries, pages
~272-275 of `/home/resources/spitbol-manual-v3.7.pdf`, extractable via `pdftotext -layout`) into a
correctly-sized, correctly-indexed replacement table, and (b) auditing every existing
`core_runtime_error(N, ...)` / `kwb_error(N, ...)` call site that currently passes a **hardcoded internal
N** (there are dozens across `core.c`, `keywords.c`, `runtime_eval.c`, etc.) to pass the **official**
number instead. That is a cross-cutting change touching a widely-shared, currently-working file, with
real regression risk if rushed — it deserves its own row and its own careful verification (every already-
green SETEXIT/&ERRTYPE witness must be re-proven, not just the new ones), not a same-sitting patch bolted
onto a single testpgms investigation.

**Routed, not silently absorbed:** flagging to hq_P (this row's lane) to mint as its own row. Suggested
scope split: (1) transcribe manual's official table into a new, correctly-sized array; (2) grep-and-fix
every hardcoded call site; (3) re-run the full SNOBOL4 gate plus every existing SETEXIT/probe witness
before calling it green, since a numbering fix can silently *break* a witness that was accidentally
passing by matching SCRIP's own wrong number against itself in a hand-authored `.ref` rather than against
a live oracle cut.
