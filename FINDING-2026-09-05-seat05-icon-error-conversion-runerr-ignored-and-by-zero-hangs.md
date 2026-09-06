# FINDING 2026-09-05 — seat05 — `&error` conversion has two gaps: `runerr()` ignores it, `to...by 0` hangs under it

Context: FLEET-12, seat05, hq_B lane. Surfaced as a side effect of strengthening the isolation-ladder
witnesses named in the companion FINDING (`icon-witness-audit-passes-for-the-wrong-reason`) — the
strengthening recipe there wraps a refusal-triggering call in `&error := 1` so the specific error code
becomes observable on stdout. Two of the fifteen candidates broke that recipe outright, in two different
ways, both confirmed against the real oracle. Not cured here (out of this row's lane — walking finds it,
hq_B cures it, per the FLEET-12 split); routed via message the same session. Tree: SCRIP `75e5b6f5f`.

## Gap 1 — `runerr()` does not honor `&error`

`runerr(N, V)` is Icon's own "raise runtime error N with offending value V" builtin — its entire purpose
is to produce a catchable runtime error. Real Icon lets `&error` convert it to a failure like any other
runtime error:
```
procedure main()
  &error := 1;
  runerr(205, "bogus");
  write("num=", &errornumber, " text=", &errortext);
end
```
- **icont/iconx (oracle):** prints `num=205 text=invalid value`, rc=0 (the error was converted to a
  failure; execution continued to the `write`).
- **SCRIP:** prints nothing on stdout, `Run-time error 205 / offending value: "bogus"` on stderr, **rc=1**
  — `&error := 1` was set but had no effect on this specific call; the program aborted exactly as if
  `&error` had never been assigned.

Every OTHER runtime error probed this session (any/many/upto/find/match/move/tab wrong-type refusals,
`insert` on a non-set, `bal` wrong-type) is correctly converted by `&error` in SCRIP — this is specific to
`runerr()` itself, not a general `&error` failure. Likely site: wherever `runerr()`'s C implementation
raises its error, it is probably calling a lower-level abort path directly rather than going through the
same "check `&error` first" gate the other runtime-error sites share.

**Consequence for the isolation ladder:** `ladder_rung41_rt_runerr` cannot be strengthened with the
recipe in the companion FINDING until this is fixed — wrapping it in `&error` currently turns a
vacuous-but-harmless PASS into a hard crash. Left un-strengthened deliberately; ready-to-use oracle-cut
content (`num=205 text=invalid value`) is in the companion FINDING for whoever lands this cure.

## Gap 2 — `to X by 0` loops forever under `&error`, instead of failing or aborting

```
procedure main()
  &error := 1;
  every write(1 to 5 by 0);
  write("num=", &errornumber, " text=", &errortext);
end
```
- **Without `&error`** (the ladder's existing `ladder_rung01_paper_by_zero` witness): SCRIP correctly
  raises `ERROR 211 -- by value equal to zero` and aborts, rc=1 — this is the CORRECT, already-passing
  behavior and is not in question.
- **With `&error := 1`:** SCRIP does not fail gracefully and does not abort — it **spins forever**,
  printing `1` in an unbroken stream (confirmed reproducing twice, once caught live via `ps` at 99.7% CPU
  for 2+ minutes before being killed, once reproduced on purpose under `timeout 5` to confirm it is not a
  one-off). The by-zero check that normally raises error 211 appears to be reachable only through the
  same abort path Gap 1 describes; with that path suppressed by `&error`, the underlying `to...by`
  generator falls through to ordinary generation with a step that never advances past its start value.

**Severity note:** this is a hang, not a wrong answer — worse than the vacuous-witness class this
session was chartered to find, since it makes the interpreter unresponsive rather than merely
unconvincing. Any real Icon program that sets `&error` (a normal, documented way to make error handling
local rather than fatal) and separately has a live-computed step that can be zero would hang instead of
either failing gracefully (oracle behavior once `&error` is honored) or aborting (current no-`&error`
behavior). Recommend prioritizing over Gap 1 for exactly this reason.

**Consequence for the isolation ladder:** `ladder_rung01_paper_by_zero` is left un-strengthened and
un-touched — the existing (vacuous but non-hanging) witness stays as the safe, currently-committed state.
Do NOT apply the companion FINDING's `&error`-wrap recipe to this witness until the hang is fixed; a
land of this specific witness's strengthening without the underlying fix would introduce a multi-second
(or worse) hang into every future full-ladder run.

## Suggested root-cause direction (not verified against source — a hint, not a diagnosis)

Both gaps are consistent with a single shared cause: the by-zero check and `runerr()` may both raise
their error through a path that unconditionally aborts (bypassing whatever gate the other runtime-error
sites use to check `&error` first), and for the by-zero case specifically, whatever guards the abort call
also appears to gate the loop-termination logic itself — so suppressing the abort (by having `&error` set)
doesn't just skip the error, it skips the termination check too. This is a hint for wherever hq_B starts
looking, not a location in `src/` — not traced to a specific file or function this session.
