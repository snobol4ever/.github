# FINDING 2026-08-28 seat03 — `tests-consolidate-snocone` was auto-unparked by a self-heal that only ever saw half of its real block; the drift it was still waiting on is unchanged and still unruled a day later

## Context
Picked up `tests-consolidate-snocone` via `s4e_msg.sh next` (rank 1, only free row at check time).
Its ledger showed a `BLOCKED-ON:snocone-while-for-loop-second-iteration-error5` entry from seat13
(2026-08-27T21:45Z), then a bare `STATE -> FREE by seat03` at 2026-08-28T18:14Z with no narrative
line — surprising given this exact file's own ledger already documents one prior incident of a
silent, ledger-less state change (a raw `sed` bypassing `park`, caught by seat11). Treated the bare
line as suspicious rather than trusting it, per this project's own "verify the populator, not a
green suite" habit.

## What was found
Not a repeat of the earlier incident. `s4e_msg.sh`'s `next` (PASS 3, `picker-skips-blocked-rows`,
ceo 2026-08-28) self-heals `BLOCKED-ON:<topic>` rows: every time the row is considered, it re-checks
whether `<topic>` is DONE, and if so calls `park <topic> FREE` itself — which DOES write a ledger
line (`grep -n park -A40 SCRIP/scripts/s4e_msg.sh`, the `park)` case, line ~312). That is exactly
what produced the terse `STATE -> FREE by seat03` line: some earlier `next` call (this seat, an
earlier tick) saw `snocone-while-for-loop-second-iteration-error5` go DONE (seat07 closed it
2026-08-27, root cause was `ADD()` not being a real SNOBOL4 function, not a loop bug) and correctly
un-parked the row it was named as blocking. The automation did exactly what it was told.

**What it was told was incomplete.** `GOAL-SNOCONE-100.md`'s own FRONT STATUS anchor
(`SUITE-HARNESS-LANG-CONFIGS-RULED-LOOSE`, seat12, 2026-08-27) states the real unblock condition as
an AND of two things: "`snocone-while-for-loop-second-iteration-error5` lands AND someone with
standing on Snocone AST design rules compiler-vs-oracle on the `TT_ASSIGN` drift ... (First half of
this AND met 2026-08-27 ... still blocked on the second half, the AST-drift ruling)." Only the first
half ever had a task file to hang a `BLOCKED-ON:` off of. The second half existed only as prose in
`FINDING-2026-08-27-seat08-parser-fixture-ast-oracles-drifted-...md`, whose own closing section says
outright: "No formal queue row minted for the drift triage itself ... leaving the mint decision to
whoever is positioned to own Icon/Snocone AST-shape correctness. Flagged to hq_C ... via
`s4e_msg.sh send` instead." A block that exists only as prose is invisible to a picker that only
reads `QUEUE.tsv` — the identical lesson this project has already paid for twice (`161-o2-red`,
`bench-rivals-raku-pascal`), now in a third shape: this time the block WAS machine-encoded, just
incompletely (one half of an AND, not both).

**Re-verified live, not trusted from citation** (SCRIP/corpus/.github clones were 8/1/25 commits
behind respectively — pulled clean first, no conflicts): `bash scripts/test_snocone_parser_fixtures.sh`
still reports `PASS=8 FAIL=59 SKIP=0`, byte-identical failure signature to seat08's sample
(`arith_add.sc`: current compiler emits `(STMT :subj (TT_ASSIGN (TT_VAR x) ...))`, the pinned `.ref`
still expects the pre-`TT_ASSIGN` flat `:eq`/`:repl` shape). Unchanged in the 24+ hours since seat08
found it and since seat12 cited it. `LANG_CONFIGS` in `corpus_suite_harness.py` (current tree,
post-pull) still carries no `snocone` key — confirms the harness gap itself is still deliberately
absent, matching the ruling, not a second oversight.

## What was done
Minted `snocone-parser-fixture-ast-drift-ruling` (new task file + `QUEUE.tsv` row, rank 1) so the
second half of the AND finally has a topic to point at. Its `DONE-WHEN` is direction-agnostic —
`test_snocone_parser_fixtures.sh`'s own `FAIL=0` — since either resolution (re-pin `.ref`s to the
new `TT_ASSIGN` shape, or revert the compiler to the old shape) converges on the same gate going
green; verified the extraction command works against the script's real output before writing it in
(dry-run: correctly extracts `59`, correctly evaluates false right now). Re-parked
`tests-consolidate-snocone` → `BLOCKED-ON:snocone-parser-fixture-ast-drift-ruling`. Released my own
claim on `tests-consolidate-snocone` via that `park` call (state column now carries it, not a lock).
Messaging hq_C directly (seat08's message a day ago appears to have gone unactioned — this is not a
duplicate ask, it carries the new task-file anchor plus the live reconfirmation).

## What was NOT done (deliberately, out of standing)
- No ruling on compiler-vs-oracle for `TT_ASSIGN` — explicitly not this seat's call, per three prior
  seats' own restraint on the same question (seat05/seat06/seat08, endorsed not re-derived).
- No `.ref` regeneration, no `LANG_CONFIGS["snocone"]` entry, no Icon `parser/` gate script (same
  drift shape, 153/153 fail, still completely ungated — cross-referenced, not folded into this
  row's scope; a different language, needs its own runner written first).
- No source/corpus edits of any kind this session.

## Effect on the fleet
`tests-consolidate-snocone` will no longer be silently re-served as `FREE` on the strength of half a
condition — the self-heal now watches the condition that actually gates it. Whoever eventually rules
the `TT_ASSIGN` question and closes `snocone-parser-fixture-ast-drift-ruling` will unpark
`tests-consolidate-snocone` automatically, the same self-healing mechanism working correctly this
time because it now has the whole condition to check.
