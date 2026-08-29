# FINDING — `upto(!x)` (a scanning function whose argument is itself a generator) infinite-loops instead of advancing the argument and terminating

**seat06 · 2026-08-29 · row `tests-consolidate-icon` (rung36 `scan` characterization) · SCRIP HEAD `32a2d9df`**

## The question this started from

`rung36_jcon_scan.icn`'s KEEP.md entry read "under-produces vs `.expected`, untraced" — the one remaining
genuinely-open rung36 thread per the current baton (seat12's `## NEXT`, priority 2). Traced it.

## Minimal repro (3 lines, reproducible standalone)

```icon
procedure main()
   &subject := "badc";
   every write(upto(!&lcase))
end
```
Arizona `icont` (oracle): `2`, `1`, `4`, `3` — four lines, then stops (rc=0). SCRIP `--run`: `2`, `2`, `2`,
`2`, `2`, ... **forever** (killed by `timeout`; produced 13.4MB of `"2\n"` in under 10s before being
killed). **This is a hang, not a wrong-output bug** — worse than the class every other rung36 finding on
this row has characterized so far (all of those are wrong-output or crash, all bounded).

## Not cset-specific

`every write(upto(!"abcd"))` (a literal string generator via `!`, no `&lcase` keyword involved) reproduces
the identical shape: oracle `2 1 4 3`, SCRIP stuck repeating `2` forever. Rules out anything specific to
`&lcase`/keyword-cset handling — the defect is in how `upto()` (and structurally, per the code below,
plausibly any scanning function of the same shape — **not verified for `find`/`match`/`any`/`tab`, flagging
as an untested but plausible blast radius, not a confirmed one**) handles a GENERATOR argument in general.

## Isolation: not the outer `?`-scan either

The witness's actual line (`("badc" | "edgf" | "x") ? write(upto(!&lcase))`) also under-produces, but
`("badc" | "edgf") ? write("hit")` alone (alternation + scan + `every`, no `upto`/generator-argument
involved) matches the oracle exactly (`hit` x4, both sides). The `?`-scan/alternation/`every` machinery
itself is not implicated — isolating strengthens that the defect is specifically in the generator-typed
argument to `upto`, not the surrounding scan construct (which merely changes the failure mode from
"infinite loop" to "wrong output, terminates" when wrapping the same `upto(!x)` shape — not investigated
further why wrapping changes the failure mode, flagged for whoever picks this up).

## The mechanism, verified in the template, not the full causal chain

`src/templates/bb/bb_scan_upto.cpp`'s "var cset" arm (lines 12-41, taken whenever the cset argument is not
a compile-time literal — i.e. exactly the `upto(!x)` shape, `_.op_sa` slot-based) has ONE β (resume) entry
point shared by two logically different callers:
```
+ x86_beta()
+ x86("inc",     FRQ(_.op_off + 16))
+ x86("jmp",     L(0))
```
This is **identical** to what `L(1)` (an ordinary "this position didn't match, try the next one" failure)
does. β just increments the position cursor and re-loops, reading the SAME cset value already sitting in
`FRQ(_.op_sa + 8)` — it never re-reads `_.op_sa` for a fresh value and never resets the cursor to the
subject start. That is *correct* for "give me the next position for the SAME cset" (continuing a single
`upto('a')` call's own position search) — but **`upto(!x)` needs two structurally different kinds of
resume**: (1) same argument, next position (what β does, correctly) — and (2) argument generator has a NEW
value, start a FRESH position scan from the subject start with the new cset (what β does NOT do — there is
no code path in this file that resets the cursor or re-fetches `_.op_sa` on resume). Confirmed by the
witness's own required semantics: oracle's `2, 1, 4, 3` for "badc" is not monotonic (2→1 goes backward),
which is only possible if the position scan restarts from 1 for each new letter — proving case (2) is a
real, exercised code path in Arizona Icon, not a corner case.

⛔ **NOT ROOT-CAUSED PAST THIS POINT, flagged not guessed at:** this file alone doesn't show WHERE the
argument generator (`!&lcase`/`!"abcd"`) advancing is supposed to route back into `upto`'s α (fresh call,
which WOULD reset the cursor and pick up a freshly-stored `_.op_sa`) instead of its β. That's graph-wiring
(how a call/function node whose argument is itself a generator gets compiled — the argument-generator's own
box and its backtrack target), not this template, and finding it needs tracing the wiring for a generator
argument specifically, which this session did not do (out of this row's lane, and a materially bigger dig
than the template-level read above).

## Not attempted here

This row (`tests-consolidate-icon`) is suite conversion, not runtime bug-fixing — same discipline every
prior session on this row has applied to every bug it found (`proto`, `scan1`, ascii/cset, `&level`,
r14-not-zeroed). No fix attempted. `rung36_jcon_scan.icn` stays loose, not KEEP.md'd (it's a bug, not a
permanent design exclusion — same convention this row has used throughout: KEEP.md is for "will never
convert by design," not "currently buggy").

## Severity note, why this is flagged more urgently than a same-shape "characterized, not fixed" finding

Every other open rung36 thread produces wrong output or a bounded crash. This one hangs. Existing harnesses
on this row (`test_icon_rung_suite.sh` and siblings) appear to consistently wrap Icon runs in `timeout`, so
this is very unlikely to already be causing a silent CI hang — not verified exhaustively, flagging as a
reasonable inference, not a swept claim. Worth hq_C's attention promptly regardless, since `upto(!x)` (or
the same shape on another scanning function) is not an exotic construct.

Mailed `hq_C` (`icon-upto-generator-arg-infinite-loop`) with this finding and the two minimal repros.
`tests/icon/KEEP.md`'s `scan` entry updated to point here instead of "under-produces, untraced" (corpus,
see task ledger for the commit hash).
