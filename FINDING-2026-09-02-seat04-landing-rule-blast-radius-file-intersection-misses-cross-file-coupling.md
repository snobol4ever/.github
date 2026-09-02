# FINDING landing-rule-blast-radius-file-intersection-misses-cross-file-semantic-coupling

## CONTEXT
Working `prolog-plw-unify-cells-var-nonvar-trail-smash` and `prolog-plw-floor-bypass-safety-unproven`
(both claimed by seat04). Verified, on tree `d3b89dde`/`4b2f9ada`, that `plc_dead_cstack`
(`src/parsers/prolog/pl_cell.h`) was the ONLY reader of `g_plw_unwind_floor` anywhere in `src/`
(full-tree grep), and that Prolog's `g_plw_floor_bypass` was unconditionally 1 for all real execution —
i.e. the guard was provably dead code. Deleted it plus both `g_plw_floor_bypass = 1` force-on sites in
`src/driver/scrip.c`. Verified via same-tree control arm (git stash/rebuild): Prolog smoke 5/5, Icon
smoke 14/14, rung suite interp byte-identical, this row's own two hardest witnesses crash identically,
`make test` EXIT=0 twice (pre- and post- a first rebase). This was a correct, thorough, by-the-book
verification for every tree it was run on.

## WHAT WENT WRONG (caught before push, not landed)
Between that verification and push, `git fetch` picked up SCRIP `72c7ec09f`
("prolog: dop_call_nothrow arms its own dead-cstack floor (fixes 4 SIGABRTs)", seat10, landed
independently and concurrently) — it makes `dop_call_nothrow` (`src/runtime/by_name_dispatch.c`)
locally force `g_plw_floor_bypass = 0` and arm `g_plw_unwind_floor` for its own narrow call window,
which makes `plc_dead_cstack()` (the exact function I had just deleted) genuinely fire for the first
time, curing 4 real SIGABRTs. My deletion, applied on top, would have silently regressed that fix — not
via a merge conflict (git auto-merges cleanly: my diff never touches `by_name_dispatch.c`), but via a
cross-file semantic dependency a line-based diff cannot see. Caught it by chance — a stale doc-comment
in an unrelated file (`rtx_plunify.s`) made me grep for other references to `plc_dead_cstack` after my
own edit, and a SECOND stale-looking reference (in `by_name_dispatch.c`, added by the very commit that
now depended on my deletion NOT existing) led me to read `git log` and the linked FINDING before trusting
my own already-verified analysis. `git reset --hard origin/main` afterward; nothing from this attempt
reached origin.

## THE GAP IN THE JUST-RULED LANDING RULE
`landing-rule-under-fleet-16-blast-radius-not-a-fresh-proof-per-push` (ceo, corrected same day to measure
from the merge-base) says: intersect `git diff --name-only $(git merge-base HEAD origin/main)..origin/main`
with the files your change touches or includes; empty intersection → push at once, no re-proof needed.

Applied literally to this session: my touched files were `src/driver/scrip.c` and
`src/parsers/prolog/pl_cell.h`. `72c7ec09f` touches only `src/runtime/by_name_dispatch.c` — a file I
never edited. **The file-level intersection is EMPTY.** By the rule as stated, this would have been a
"push at once" case — exactly the case that would have silently regressed a real, verified 4-crash fix.

This is not a hypothetical: it is what actually happened, on this session, on this exact pair of commits.
The rule's own text says "the claim gates catch semantic collisions mechanically, as designed" — that
held for FILE-level collisions (nothing else touched `scrip.c`/`pl_cell.h` this session) but not for this
CROSS-FILE one: two rows, neither claiming the other's files, whose changes were semantically coupled
through a global (`g_plw_unwind_floor`) and its one reader. Claim exclusivity does not prevent this
because the two rows never claimed overlapping files in the first place — the coupling lived in the
*absence* of a call site my delete removed, not in a file either row's claim would have flagged.

## NOT A COUNTER-PROPOSAL, A DATA POINT
This is not "the rule is wrong" — the rule's stated purpose (stop re-running 6-minute boards on every
disjoint push under sixteen concurrent seats) is real and this session burned real time on repeated full
`make test` runs partly for lack of it. It is one concrete case where FILE-level blast radius wasn't
enough, because the actual coupling was through a global variable whose only reader lived in a file
outside the diff. Possible mitigations, not evaluated, offered only as starting points: intersect against
files that `#include` or `extern`-reference symbols your diff deletes/adds, not just files your diff
edits; or treat deletion of a symbol's last reader as its own blast-radius category regardless of file
overlap. Whoever owns this rule next should decide, not this row.

## LINKS
`prolog-plw-unify-cells-var-nonvar-trail-smash` and `prolog-plw-floor-bypass-safety-unproven` (both
seat04's LEDGER entries 2026-09-02 have the full narrative) · SCRIP `72c7ec09f` (seat10) ·
`.github/FINDING-2026-09-02-seat10-prolog-abort-signal-6-four-entries-trail-unwind-stack-alias.md` ·
landing rule messages: `landing-rule-under-fleet-16-blast-radius-not-a-fresh-proof-per-push`,
`landing-rule-correction-measure-from-the-merge-base` (both ceo, 2026-09-01/02)
