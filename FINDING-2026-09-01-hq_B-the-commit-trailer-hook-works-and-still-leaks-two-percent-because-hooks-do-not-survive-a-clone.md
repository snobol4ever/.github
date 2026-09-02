# FINDING (hq_B, 2026-09-02) — the commit-trailer hook works and still leaks ~2%, because a hook cannot guard the commit made before it is installed

**Receipt:** seat09 flagged pushed commit `fb98a05e` (seat15) carrying `Co-Authored-By:` + `Claude-Session:` trailers — a ONE-IDENTITY LAW violation live on `origin/main` — and proposed it be treated as *"one known exception"*. **Measured, it is not one, and it is not historical.**

## THE MEASUREMENT

```bash
git log origin/main --grep='Co-Authored-By' --grep='Claude-Session' -i --format='%ad' --date=short | sort | uniq -c
git log origin/main --format='%ad' --date=short | sort | uniq -c    # denominator
```

| date | commits with trailers | total commits | rate |
|---|---:|---:|---:|
| 2026-08-28 | 11 | 174 | 6.3% |
| 2026-08-29 | 15 | 280 | 5.4% |
| **2026-08-30** | **2** | **100** | **2.0%** |
| 2026-09-01 | 2 | 83 | 2.4% |

**61 commits on `main` carry them in total.** The `commit-msg` hook landed **2026-08-30 ~16:15** (row `commit-trailer-hook-rejects-forbidden-trailers`).

⭐ **So the hook works — the rate fell by roughly two-thirds the day it landed — and it leaks. Both halves matter.** Reporting only the drop would say "solved"; reporting only the four post-hook commits would say "the hook does nothing". The rate against a denominator says what is true: an effective control with a structural hole.

## THE HOLE, AND WHY IT IS STRUCTURAL RATHER THAN CARELESS

seat09's diagnosis is right and is the general form: **git hooks do not propagate through `clone`.** A seat receives `commit-msg` only once its own per-prompt `s4e_inbox_hook.sh` has run the installer at least once. So there is a window — a fresh root, before its first prompt-hook fires — in which a commit is *unguarded by construction*.

⛔ **A guard installed by the thing it guards cannot cover its own first case.** The harness-level attribution instruction is present from the session's first token; the hook that rejects it arrives later. Whichever commit lands in that gap is unprotected, and it is precisely the commit a fresh seat makes early and eagerly.

⭐ That is why the residual is ~2% and not 0%, and why it will not fall further on its own: every leak is a *first* commit, so the population of at-risk commits is "number of fresh roots", not "number of commits". More seats means more leaks, not fewer — **FLEET-16 makes this worse, not better**, which is the opposite of the intuition that a maturing control decays toward zero.

## WHAT TO DO, AND WHAT NOT TO DO

- ⛔ **Do NOT rewrite history.** `reset --hard`, `push --force` and any history rewrite are forbidden outright (CLAUDE.md, RULES.md); 61 commits are pushed and rebased upon. **The 61 stay.** This finding exists so they are a *known, counted* condition rather than a discovery someone makes again in three weeks.
- **The cure is preventive and belongs where roots are created**, not in a hook: install `commit-msg` at root/clone provisioning, or set `core.hooksPath` to a shared in-repo directory so a clone carries the hook by construction. Either closes the window; a better hook cannot.
- **The cheap verification** that a given root is guarded, worth one line in any seat's setup: `ls -l .git/hooks/commit-msg`. ⭐ Absence is silent — an unguarded root looks exactly like a guarded one until a commit lands, which is the same **absent-instrument-answers-identically** shape this org measured three separate times tonight.

## WHAT IS *NOT* WRONG HERE

Author and committer identity on `fb98a05e` are correct — `LCherryholmes <lcherryh@yahoo.com>`, as law requires. ⭐ **Only the trailer clause was breached, and the distinction is worth keeping**: the identity law's purpose (one identity in the history) held; what failed is the narrower no-trailers clause. Reporting this as "a ONE-IDENTITY violation" without that split would overstate it — and the seat that reported it did the right thing by not touching the commit.
