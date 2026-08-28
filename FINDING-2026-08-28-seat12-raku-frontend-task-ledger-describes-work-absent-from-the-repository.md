# FINDING 2026-08-28 seat12 — raku-frontend-real-world-syntax-gaps' task LEDGER describes five work
passes (seat03, seat04 ×2, seat05 ×2) with specific commit hashes, verification numbers, and detailed
root-cause narratives — NONE of which are present in the SCRIP repository, on any branch

**Seat:** seat12 · **Date:** 2026-08-28 · **Task:** `raku-frontend-real-world-syntax-gaps` (rank 1) ·
**Tree:** SCRIP, `main`, freshly pulled to `c2fa9bff` this session (also corpus, `.github`, both
fast-forwarded 45/very-many commits from a stale local clone before any of this was checked).

## ⛔⛔⛔ RETRACTED (seat12, same session, ~40 minutes later) — THE CONCLUSION BELOW WAS WRONG

**The five commits are real. They exist. The work happened.** What I measured at every step below was
true at the moment I measured it — but the moment was wrong, and I never re-checked before writing it
down. Sequence: my session's *initial* `git pull --ff-only`, done before any of this investigation,
correctly fetched origin as of that instant (HEAD `c2fa9bff`). Seats 03/04/05's five commits were
pushed to origin **after** that pull and **while this session was doing its own bitwise-operator
implementation work** — a normal, expected outcome of this project's "commit and push freely, no
concurrency gating" model. Every check in this FINDING (`git cat-file -t`, `git log --all`, `git
reflog`) is a query over the **local object database as of my last fetch**, not over origin's true
current state — and I never re-fetched before concluding absence. My own `git pull --rebase`, run
routinely afterward to push my own work, pulled exactly those five commits in one shot
(`c2fa9bff..1416f279`) and they merged cleanly (`raku.y`/`raku.l` auto-merged with zero conflicts
against my own change; only the *generated* `.tab.c`/`.lex.c` — which cannot 3-way-merge two
independent bison/flex regens as text — conflicted, resolved the ordinary way, by regenerating fresh
from the merged grammar source).

**The methodological error, stated plainly so it doesn't repeat:** I checked "does this exist in what
I already have" and reported it as "does this exist," without first running `git fetch` (or an
equivalent freshness check) to rule out "I simply haven't fetched it yet" as the explanation. This is
the exact failure shape RULES.md's own FACT RULES warn about — "a claim's provenance dies at the
moment of write-down," "pull-before-trust" — and I fell into it while writing a FINDING that quotes
those same rules. The honest instrument here would have been `git fetch origin && git log
origin/main --oneline -- <path>` (checks true remote state directly) rather than `git log --all`
(checks only refs already known locally as of last fetch) — a distinction that mattered exactly once
and I didn't make it.

**What was actually true, and what wasn't:** seat03/04/05's LEDGER entries describing colon-pair,
return-modifiers, compound-assign-as-expr, array-assign-unless, typed-defaulted-params, and
punctuation-wordlists are **real, landed, verified work** — not fabricated. The one thing this FINDING
got right independent of the timing error: the *task file's own* "3/17, state as of afe050e1" banner
was, even so, briefly stale the moment I read it (afe050e1 hadn't reached my clone yet) — a real,
if much smaller and much more mundane, instance of "the ground moved between when the note was
written and when it was read," same shape as `FINDING-2026-08-28-seat05-rebase-silently-clobbered-…`,
several orders of magnitude less dramatic than this FINDING's original headline. That headline is
withdrawn. Original text kept below unedited, per this project's own retract-in-the-open convention —
it documents a real methodology mistake worth keeping visible, not a real repository defect.

Corrected current state (post-merge, this session, re-verified): see this session's LEDGER entry in
`raku-frontend-real-world-syntax-gaps.task.md`, written after this retraction, for the actual
post-merge kernel count and control-arm results.

---

# Original text follows, uncorrected, kept for the methodology lesson only — do not cite its headline claim.

## What happened

Picked up this task's `RESUME` claim per THE LOOP. The task file's `## NEXT`/`## LEDGER` describe, in
detail, five completed work passes closing real-sounding grammar gaps in the raku frontend: sigil-less
bindings, plain array params, colon-pair named args, typed/defaulted params, `sub MAIN` auto-invocation,
a param type-check-ordering bug, return-statement-modifiers, compound-assign-as-expr — each with commit
hashes (`afe050e1`, `816a900b`, `47c2bf4f`, `7203a29b`, `f7a04e23`), specific verification numbers
(`test_crosscheck_raku.sh` 51/51, `test_smoke_raku.sh` 724/724 both modes), and in two cases detailed
"near-miss" war-stories (a `pd->v.ival` off-by-one for methods, a UTF-8-truncating regex census) with
enough circumstantial specificity to read as genuine incident reports.

**None of it is in the repository.** Sequence that surfaced this:

1. Picked a well-scoped remaining gap from `## NEXT` — Raku's numeric bitwise infix operators
   (`+&`/`+<`, the "chained bitwise ternary" blocking `rc-dragon-curve`) — confirmed via direct grep
   that `src/ir/ast.h` has zero bitwise `TT_*` node kinds and `raku.l` has zero `+&`/`+<` tokens, and
   found Icon's shared `iand`/`ishift` runtime builtins (`by_name_dispatch.c`, language-agnostic by
   construction) were a clean reuse target. Implemented, bison-conflict-checked (93→95 shift/reduce,
   9→9 reduce/reduce — tolerated-range delta), regenerated, built, verified by isolated probe (m3 and
   m4 codegen both route through the same generic `rt_call_arr_bl("iand"/"ishift", …)` call, matching
   `say`'s own mechanism) and against the real kernel — this construct is real, correct, and landed
   (see below).
2. `rc-dragon-curve.raku` still failed after the fix, now at line 21 — a NEW blocker (`($x,$y) =
   ($dx,$dy);`, bare parenthesized list-assignment without `my`), not present in the catalog. Fine on
   its own (kernels commonly have more than one gap), but prompted a full 17-kernel re-sweep to get
   accurate current numbers before writing anything down.
3. **The re-sweep measured `ok=1 bad=16`** — only `send-more-money-loops` passes. The LEDGER's own
   "state as of seat03's pass" line claims **3/17**, with `point_class_add`/`point_class_add1` closed
   by colon-pair support. Both failed in the fresh sweep with `raku lex error … unexpected char ':'`
   — the exact symptom colon-pair support (a bare `:` lexer rule) exists specifically to cure.
4. Checked directly: `grep -n '^":"' src/frontend/raku/raku.l` — **no such rule exists.**
   `grep -n "return ':'" src/frontend/raku/raku.l` — **nothing.**
5. `git cat-file -t afe050e1` (and the other four hashes) — **`fatal: Not a valid object name`**, for
   all five. Not "not on this branch" — not a valid object at all, anywhere in the local object
   database (which had just fast-forwarded 45 commits from origin, so this is a live, current clone).
6. `git log --all --oneline -- src/frontend/raku/raku.y src/frontend/raku/raku.l` (every branch, every
   remote-tracking ref) — **four commits, ever**: the initial import, one comment-stripping pass, and
   two structural directory-rename commits (`parser/`↔`frontend/`). No feature commit. Ever.
7. `git reflog show --all | grep` for the five hashes — nothing. `git branch -a` — eleven unrelated
   `origin/*` feature branches (rtx-3b, snobol4-bladder, icon-m3m4-jz-fix, …), none raku-related.
8. Spot-checked two more specific claims directly against source rather than trusting the pattern
   was isolated to one construct: `lower_raku.c`'s `has_main` scan **still only matches lowercase
   `"main"`** (seat05's pass-1 fix, "CLOSED", would have added an uppercase-`MAIN` arm — it is not
   there). `raku.y`'s `param_list` production **has no `VAR_ARRAY` alternative at all** (seat04's
   pass-1 fix, "CLOSED", would have added exactly that — it is not there). Zero for two.

**This rules out the usual innocent explanations.** A silently-clobbered rebase
(`FINDING-2026-08-28-seat05-rebase-silently-clobbered-…`) or a stash race
(`FINDING-2026-08-28-seat01-concurrent-git-stash-race-…`) both still leave a trace — an orphaned
commit in the reflog, a real object `git fsck` can recover, *something*. Here there is no trace of any
kind: the cited hashes are not valid git object names, and the files never contained the described
code on any ref this local clone can see. The task file's LEDGER describes tool calls, measurements,
and verified pushes that — as far as this repository's history can show — never happened.

## What this is NOT saying

Not asserting bad faith or naming a cause (this session has no way to distinguish "a prior session's
report was never backed by real execution" from "a prior session executed against some other tree that
was later discarded before ever reaching `origin`" from any other mechanism) — only that the
task file's LEDGER cannot be trusted as evidence of repository state, full stop, and neither can any
other task file's LEDGER be assumed reliable without the same direct check. **RULES.md's own FACT
RULES already say this in general form** ("PUSH IS NOT A HANDOFF-ONLY STEP", "HANDOFF COMPLETE
requires a confirmed push", "a claim's provenance dies at the moment of write-down") — this is a
concrete, fully-reproducible instance of exactly that failure, at a scale (5 passes, 2 seats, dozens of
specific claims) worth a fleet-wide flag rather than a quiet local correction.

## What this session did about it

- Did **not** trust or build on any LEDGER claim beyond what direct inspection confirmed.
- Landed only the one construct independently verified end-to-end this session (bitwise infix ops,
  `+&`/`+<` → shared `iand`/`ishift` builtins) — SCRIP commit (this session, see push log).
- Rewrote the task file's `## NEXT` to state the **measured** current pass count (re-derived fresh,
  1/17 raw before this session's fix) and marked the prior "3/17, constructs #1–4 + MAIN + ordering +
  return-modifiers + compound-assign all CLOSED" narrative as **UNVERIFIED — contradicted by direct
  repo inspection**, without deleting the original text (kept, addended, per RULES.md's "retract in
  the open, never a silent edit").
- This finding + `s4e_msg.sh ask` to HQ, non-blocking — continuing to work the row on the corrected,
  measured baseline rather than stopping.

## Recommendation for whoever rules on this

Whatever produced these five passes' worth of specific, plausible, unverified narrative is worth
finding — it is not unique to this task file, and `handoff_status.sh`/gate-verdict discipline only
catches it if a session actually runs those commands before writing "CLOSED". A fleet-wide census of
recently-touched task files' claimed commit hashes against `git cat-file -t` (cheap, mechanical, exactly
this session's step 5) would show how far this extends before anyone spends more cycles trusting a
LEDGER that reads as evidence but was never checked against one.
