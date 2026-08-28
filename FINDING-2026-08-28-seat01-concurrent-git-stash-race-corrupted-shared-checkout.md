# FINDING 2026-08-28 seat01 — a foreground session and its own background Agent, sharing one checkout, raced each other's git state; a THIRD, unidentified stash was collateral damage

## What happened

Working row `class-c-epilogue-kt-offset-corruption-extra-exit-node` (root-caused and fixed —
see that task's LEDGER, and SCRIP `35750f03`/`7c22a84a`), this session repeatedly observed its
own working tree (`/home/claude01/SCRIP`) change out from under it mid-investigation: files
edited moments earlier reverting to HEAD, `git log`/`git stash list` gaining entries this
session never created, and finally a genuine `make` failure from **literal unresolved conflict
markers** (`<<<<<<< Updated upstream` / `>>>>>>> Stashed changes`) left in `src/emitter/emit.cpp`
and four `src/templates/bb/bb_match_{any,break,breakx,notany}.cpp` files.

`ps auxww` caught the cause directly: a recurring `bash -c` process (seen twice, ~08:14 and
~08:26) running `git stash; make pristine; bash scripts/update_icon_bench_asm.sh` against this
exact directory. A `<task-notification>` that arrived mid-session confirmed **this was this
session's OWN background Agent** (spawned by the pre-`/clear` predecessor conversation, still
running after `/clear` wiped the foreground's visible history) — independently investigating the
*same* task, reaching the *same* root cause and fix, and racing this foreground session's git
operations the entire time. Its own final report says it hit the identical 6-file conflict, tried
`git reset --merge` to back out cleanly, was blocked by its harness's safety classifier, and
correctly stopped rather than route around the block.

## The part that is NOT explained

The 6 conflicted files' content (an `IR_MATCH_TAB`/`RTAB`/`POS`/`RPOS`/`BREAK`/`BREAKX` "defer"
fast-path using `rt_pat_prim_int`) belongs to neither this session's fix nor the background
Agent's — both of us have independent, first-hand knowledge of only the class-c epilogue work.
This is a **third, unidentified** piece of in-progress work. It was captured in a stash at some
point (this session directly read its full diff before touching anything), but `git stash list`
no longer contains it — some process ran `stash pop`/`drop` on it. **There is no backup left. If
those 6 files are reset or checked out without first extracting their current content, that work
is gone.**

## What this session did NOT do, deliberately

Did not run `git reset --merge`, `checkout --`, or any other command that would discard the 6
conflicted files — same call the background Agent made, for the same reason: neither of us has
context on whose work it is or which side of the conflict is correct, and guessing risks silently
destroying someone's unrecoverable in-progress feature.

## What this session did instead

Verified and landed its own fix (`x86_asm.h` FR32/FR64 prefix disambiguation) entirely through
disposable `git worktree`s built off fresh `origin/main` — cherry-picking the already-committed
fix, rebuilding, gate-testing, and pushing from there. This never touched the main checkout's
broken index at all. **The worktree-off-origin pattern is the general escape hatch** for
"my own committed work is safe, but the shared checkout's working tree/index is not" — recommend
it explicitly wherever THE LOOP's push/verify steps are documented, since this class of race is
structural (two processes, one checkout) rather than a one-off mistake.

⛔ **`/home/claude01/SCRIP` WILL NOT BUILD RIGHT NOW.** The 6 files above contain live,
uncompilable `<<<<<<<`/`=======`/`>>>>>>>` conflict markers — anyone who `cd`s in and runs
`make`/`make pristine` gets a `cc1plus` syntax error (`version control conflict marker in file`)
that has nothing to do with whatever they were working on. This is loud and easy to misdiagnose as
your own change's fault if you don't already know the checkout is corrupted. Build elsewhere (a
`git worktree` off `origin/main`, per below) until this is resolved.

## hq_C ruling (2026-08-28, in response to this session's ask) — confirmed correct, and extended

Leaving the 6 files untouched (this session) and refusing to force past the block (the background
Agent) were both correct — RULES/CLAUDE.md's ban on `reset --hard`/`push --force`/history rewrite
under any brief exists precisely for this shape. hq_C directed, in order: (1) extract the 6 files
outside the workspace root before anything else touches them (done — see below); (2) do not treat
"conflicted" as "abandon" — diff against `origin/main` and against SCRIP `1419c791` to determine
whether the stashed content is unlanded follow-on, a partial re-do of already-landed work, or
genuinely novel, since a diff answers that better than anyone's memory; (3) do not authorise
abandonment locally — route to `ceo` for owner identification (cross-root custody), and if `ceo`
can't find an owner, it's Lon's call, not an HQ's or a seat's; (4) name explicitly that the
checkout won't build (done, above).

## Extraction + diff analysis (this session, following the ruling)

Extracted all 6 files verbatim (with their conflict markers intact) to
`/tmp/.../scratchpad/conflict-extract/` before touching anything further — a safety copy that
survives regardless of what happens to the live checkout next.

**The diff against `1419c791` is conclusive, not ambiguous.** `1419c791` (2026-08-24, LCherryholmes)
landed "TAB/RTAB/POS/RPOS/ANY/NOTANY/SPAN/BREAK/BREAKX now support `*name` deferred arguments" —
the exact same feature, across the exact same file set the stash touches. Its own commit message
names a bug it fixed along the way: *"the 'is sval a deferred marker' test was a `sval[0]=='*'`
string sniff, ambiguous with a literal cset that itself starts with `*`... SIGSEGVs
`corpus/crosscheck/control/expr_eval.sno`... Replaced with `nd->pat_static`... as a type-safe
discriminator and dropped the `*`-prefix encoding."

Every one of the 15 conflict hunks across all 6 files shows the identical shape: the **"Updated
upstream" side is `1419c791`'s landed `pat_static`-discriminator fix, verbatim**; the **"Stashed
changes" side is the OLD `sval[0]=='*'`-sniff-plus-strip-prefix approach `1419c791`'s own message
says it replaced because it SIGSEGVs.** E.g. `lower_snobol4.c`:
```
<<<<<<< Updated upstream
              IR_LIT(nd).sval = lp_strdup(arg->c[0]->v.sval);
              nd->pat_static = 1;   /* SN4-DEFER-CSET-MARK: ... NOT a leading-star sniff (ambiguous...) */
=======
              char pb[128]; snprintf(pb, sizeof pb, "*%s", arg->c[0]->v.sval);
              IR_LIT(nd).sval = lp_strdup(pb);
>>>>>>> Stashed changes
```
and every `bb_match_*.cpp` hunk pairs `_.node->pat_static` (upstream, current) against
`_.op_sval[0] == '*'` + `vn1 = _.op_sval + 1` (stashed, the superseded sniff). **This is not
unlanded follow-on work and not genuinely novel — it is stale, pre-`1419c791` WIP for the identical
feature, carrying the exact defect that commit's own message documents fixing.** The one exception
(`emit.cpp`'s single hunk, `IR_MATCH_LAMBDA` vs. an empty stashed side) is not feature content at
all — it's the stash simply predating `IR_MATCH_LAMBDA`'s unrelated later addition, a merge
artifact rather than a real edit conflict.

**This session is NOT authorising deletion on this analysis alone, per hq_C's ruling — routing to
`ceo` for the actual disposal decision, extracted copies cited above as the safety net either way.**
