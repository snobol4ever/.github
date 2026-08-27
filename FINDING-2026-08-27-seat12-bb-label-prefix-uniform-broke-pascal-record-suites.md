# FINDING: `a01fe9f6` (bb-label-prefix-uniform) broke ~1/3 of Pascal's suite families, live on main now

**Who/when:** seat12, 2026-08-27, discovered while re-proving `test_gate_pascal_m4.sh` after `git pull
--rebase` on the `pascal-restore-prezeta` row (RULES.md REBASE-BASELINE COROLLARY caught this — a
post-rebase gate re-run is what surfaced it, not a targeted search).

## What happened

`test_gate_pascal_m4.sh`'s 17 SUITE_FAMILIES (which had measured a clean, stable **96/96 pass, both
modes**, repeatedly, all session) dropped to **64/96** immediately after rebasing onto `origin/main`.
Bisected precisely with two isolated `git worktree` builds (main checkout untouched throughout):

- `c5510d23` (xa_flat.cpp fix, immediately before the suspect): suites **96/96 clean**.
- `a01fe9f6` (bb-label-prefix-uniform, the very next commit): suites **64/96**, byte-identical failure
  set to the current `main` tip (`45b3ea92`).

This is **not** related to `pascal-restore-prezeta`'s own work this session (a 1-line `zd_nops()` fix to
`emit.cpp`, entirely unrelated to label emission) — confirmed by testing the rebased tip with and without
that fix: identical suite breakage either way.

**Affected families** (FAIL/total): `aa` 2/2, `arrrec` 2/2, `chararr` 3/3, `misc` 10/39, `nestpv` 2/2,
`pb` 2/3, `rec` 3/3, `recparam` 3/3, `vrec` 3/9, `with` 2/3. **Unaffected**: `arr2d`, `case`, `char`,
`goto`, `ptr`, `set`, `stdlib`. The affected set skews heavily toward **record/variant-record/nested-proc**
constructs (`rec`, `recparam`, `arrrec`, `vrec`, `nestpv`, `with` — record field access) — this is a
strong hint about which control-flow shapes the new resolver mishandles, not a random subset.

Failure classes on the individual-loose-file side of the same gate also grew slightly (32→35: new
failures `aa6`, `aggloc2`, `patchtable`) — same commit, not separately investigated.

## Why this is plausible from the commit's own description

`a01fe9f6`'s message describes exactly the mechanism this smells like it broke: internal scratch labels
(the `L(n)` family) used to be anonymous `.LxN_M` serials; this commit adds a **two-pass resolver in
`bb_emit_x86`'s TEXT path** that "locks each `(uid,n)` internal-label pair to whichever port it is first
seen under." Any box whose internal label is legitimately **jumped to from more than one port context**
(e.g. a fast-path comparison AND a slow-path fallback both targeting the same "write false" block) is
exactly the shape this heuristic would misresolve if it assumes single-port ownership per label — plausible
for record/variant-record boxes with multiple type-check/fallback branches converging on shared cleanup
labels, matching the affected-family list above. **Not verified against the actual resolver code** — this
session did not have time to read `bb_emit_x86`'s new two-pass logic itself; flagging the hypothesis
because it's specific enough to save whoever picks this up a re-diagnosis pass, not because it's proven.

## What was NOT done

Not bisected past the single suspect commit (didn't need to — `c5510d23`→`a01fe9f6` is a direct,
adjacent pair, both isolated-worktree-built and tested). Not root-caused inside `bb_emit_x86`'s resolver.
Not checked against SNOBOL4/Icon/Raku/Prolog/Snocone corpora — Pascal's suite families were what this
session was already measuring; **this commit touches shared label-emission infrastructure (`bb_emit_x86`,
`x86_deflabel`), so per the SHARED-NODE LAW it plausibly affects every frontend's box templates that use
multi-port internal labels, not just Pascal's record boxes** — whoever owns this needs a broader board,
not just a Pascal one.

## Suggested next step for whoever picks this up

Read `bb_emit_x86`'s new two-pass resolver (the commit message names it precisely) against one of the
now-failing witnesses (`corpus/tests/pascal/crosscheck/rec.pas` is small and 0/3 clean-broken — good
minimal target). Check whether a label referenced from two different port contexts is actually
mis-locked to the wrong one, per the hypothesis above. `git revert a01fe9f6` (or reworking the resolver
to key on something label-identity-based rather than first-seen-port) are the two obvious directions;
not evaluated here which is preferable — that's a design call for whoever owns the label-emission
architecture, not a call to make from this row's context.
