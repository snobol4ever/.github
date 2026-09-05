# FINDING 2026-09-05 seat18 — `core_runtime_error`'s terminal print is a CLASS-WIDE monolingual + double-print defect, not a single division bug

**Seat:** seat18 (hq_U) · **Mode:** FLEET-20 · **Tree:** SCRIP `bc4fe8423` · corpus `31cced3fe`
**Found while:** walking task `core-runtime-error-prints-one-spitbol-diagnostic-to-both-streams-for-every-language` (minted by hq_B).

## 0. Scope correction: this is bigger than the minted DONE-WHEN measures

The task's DONE-WHEN only exercises `rt_div`'s divide-by-zero path. The census in §3 shows the same pattern — a shared, language-blind runtime function calling `core_runtime_error()` with a hardcoded SNOBOL4-numbered code/message — at 6 sites in `src/runtime/arithmetic.c` alone, plus more in `pattern_match.c`, `by_name_dispatch.c`, `aggregates.c`, `keywords.c`, `runtime_eval.c`. Curing `rt_div`/`rt_mod` alone would leave the class red everywhere else an Icon (or Prolog) program hits an uncaught error through shared runtime.

## 1. Defect 1 (double print) — root cause confirmed, fix is one line

Regression commit: SCRIP `1d7ec52469067894808de6d0901beb06dd945a7d` ("snobol4: DATA() now honors system-function protection (ERROR 248)"), 2026-09-05 10:33:12 -0500. It replaced the old single-stream print with today's core.c:2206-2210:

```c
fprintf(stdout, "%s(%ld) : ERROR %03d -- %s\nin statement %ld\n", g_file ? g_file : "", g_line, code, msg ? msg : "", g_stno);
fprintf(stderr, "%s(%ld) : ERROR %03d -- %s\nin statement %ld\n", g_file ? g_file : "", g_line, code, msg ? msg : "", g_stno);
```

Both fire unconditionally — the stdout call is new, the stderr call is the pre-existing line reformatted into the new SPITBOL shape. Every runner that captures `2>&1` (`test_snoflake_suite.sh:162-175`, named in the task) grades the diagnostic twice where the oracle prints it once. **Recommended fix:** delete the `stdout` fprintf (core.c:2207-2208), keep `stderr` only — restores pre-regression single-print behavior while keeping the SPITBOL-format string 1d7ec5246 actually intended to add. No other caller changes for this half.

## 2. Defect 2 (monolingual format) — root cause is architectural, not a call-site bug

Measured: `write(1 / "abc")` in Icon prints (x2, per defect 1) `(0) : ERROR 002 -- division caused integer overflow`; iconx prints `Run-time error 102 / numeric expected / offending value: "abc"` with a traceback. (Second-order divergence, not chased further here: SCRIP's message text is *also* wrong for this input — "division caused integer overflow" is `rt_div`'s fixed string for `b.i==0`, but `1/"abc"` should fail on operand type, not divide-by-zero.)

`core_runtime_error`'s **entry** half (core.c:2171-2180) already dispatches correctly for Icon: when `\&error` traps (`g_error != 0`), it publishes `g_icn_errnumber`/`g_icn_errtext`/`g_icn_errvalue` and longjmps, regardless of which language compiled the program — this works because `g_error` is real language-blind *runtime state* (an error-trap counter), not a language-identity flag. Its value already means "the running graph wants Icon-shaped error info," independent of source language.

The **terminal** half (core.c:2206-2213, reached only when `g_error == 0`, no trap installed) has no equivalent signal to consult. I looked for one and did not find one:
- `is_icon` (`src/driver/scrip.c:918`) is a local in the driver's compile function, computed from file extension for pipeline orchestration only (gates `g_postfix_resume`, `optimizer_run`, etc.). It never reaches `src/runtime/*` and does not exist at run time.
- `grep -rn 'g_icn_mode\|g_lang\|g_dialect\|g_source_lang\|g_output_style'` over `src/runtime/` and `src/runtime/core/`: zero hits.
- No runtime-visible dial currently distinguishes "this executing program was compiled from a `.icn` file" from "…a `.sno` file" — consistent with the stated law (language identity stops at lower — no language globals past the parser/lower boundary), but it means the terminal print has nothing behavioral to branch on today.

**Open question for whoever cures this:** `core_runtime_error` can't pick Icon's vs. SNOBOL4's uncaught-diagnostic shape without *some* runtime-visible signal, and every candidate I can see is new state set once at program start by the driver and read only by this one terminal print. That is a new global by the letter of the no-new-globals rule ("File-scope mutable state, pinned VA slot, exported cell… all of it") even though its shape is a single dial, not a parked value — flagging so the cure carries its own ⛔ ask-Lon banner rather than skip it because the state looks small. I have no design opinion on the right shape (a register wired through box entry vs. a genuine global vs. something already in the ζ machinery I haven't found) — that's hq_U's call.

## 3. Census — every `core_runtime_error` call site outside `core.c` itself carrying a fixed SNOBOL4-flavored code/message

(file:line — code — message; **not** all confirmed reachable from non-SNOBOL4 frontends — see caveat below)

- `arithmetic.c:99,103,113,119` — code 2, NULL (default msg "Error in arithmetic operation")
- `arithmetic.c:254` — code 2, "division caused integer overflow" (`rt_div` — the minted witness)
- `arithmetic.c:255` — code 2, NULL (`rt_mod`)
- `pattern_match.c:280,346` — code 3, NULL ("Erroneous array or table reference")
- `pattern_match.c:429` — code 103, "eval argument is not expression"
- `by_name_dispatch.c:3690,6050` — code 29, "undefined operator referenced"
- `by_name_dispatch.c:4164` — code 312, "remdr caused real overflow"
- `by_name_dispatch.c:6000` — code 103, "eval argument is not expression"
- `aggregates.c:115` — code 164, "prototype argument is not valid object"
- `keywords.c:211-214,447,449,512` — code from caller / 251 / 342
- `runtime_eval.c:354` — code 38, "transfer to undefined label: %s"

All of these live in shared, language-blind files (pattern matching and the box machine are shared across SNOBOL4/Icon/Prolog per the architecture doc). The `arithmetic.c` sites are confirmed reachable from Icon (measured above); the rest are census only — I have not traced whether Icon/Prolog source can actually reach each one. Whoever cures this should verify reachability per site before spending fix effort where nothing outside SNOBOL4 can land.

## 4. DONE-WHEN measured today (both RED, as the task said)

```
=== SNOBOL4 witness ===
(0) : ERROR 248 -- attempted redefinition of system function      [stdout]
in statement 0
(0) : ERROR 248 -- attempted redefinition of system function      [stderr]
in statement 0
=== Icon witness ===
(0) : ERROR 002 -- division caused integer overflow               [stdout]
in statement 0
(0) : ERROR 002 -- division caused integer overflow               [stderr]
in statement 0
```

`k=2` (oracle 1); `icon_terminus_first_line="(0) : ERROR 002 -- division caused integer overflow"` (oracle starts `Run-time error 102`).

## 5. What I did not do

Per FLEET-20 mode (Sonnet seats walk/witness, Opus HQs cure) and the SHARED-NODE VERDICT SCOPE control-arm requirement on any `src/runtime/core` change, I did not patch `core.c`/`arithmetic.c`. Defect 1's fix is unambiguous and one line; I left it for the cure pass anyway so both defects land together under one control-arm run instead of two.

WITNESS COMPLETE, HANDING TO hq_U TO CURE.
