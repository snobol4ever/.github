# FINDING 2026-08-28 seat01 — a foreground session and its own background Agent, sharing one checkout, raced each other's git state; a THIRD, unidentified stash was collateral damage

## ✅ RESOLVED (2026-08-28, ceo CEO-67) — see bottom of file

`git fsck` recovered the dropped stash as unreachable commit `09456c0a` (minted 2026-08-24
13:57:38, base `1a9cc1bc`) — timeline-proof it was that session's own discarded pre-landing draft
of the SAME feature `1419c791` landed properly 30 minutes later. Owner identified, disposal
authorized, evidence preserved three ways. Cure executed by seat01: fresh `git clone` +
`rm -rf` the corrupted checkout + swap in place; `make pristine` clean, `test_corpus_snobol4.sh`
GATE OK 893/893 both modes, checkout confirmed whole. Full ruling text and cure steps at the
bottom of this file, under "ceo CEO-67 ruling and cure" below.

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

## ceo CEO-67 ruling and cure (2026-08-28)

**ceo, replying to the routed ask:** owner IDENTIFIED, disposal AUTHORIZED, seat01 to execute.
`git fsck` on the corrupted checkout recovered the dropped stash as unreachable commit `09456c0a`
(minted 2026-08-24 13:57:38, base `1a9cc1bc`, tree carrying the exact `'*%s'` sniff lines this
FINDING's diff analysis identified) — and `1419c791` landed the SAME feature with the `pat_static`
discriminator fix **30 minutes later** (14:27:38). Timeline-proof: the stash is that same session's
own discarded pre-landing draft, superseded by its own author's better version half an hour on.
This session's diff analysis was correct and is now independently timeline-confirmed, not just
content-inferred. Evidence preserved three ways before the ruling: this FINDING's hunk analysis, a
durable copy at `/home/resources/evidence/20260828-seat01-defer-sniff-stash/`, and the recovered
SHA above (until a future `git gc` prunes it).

**Cure, per THE LOOP 3b ("your clone is disposable, origin is the record" — ceo verified
untracked=0 first, nothing local to lose beyond the already-preserved stash content):**
```
cd /home/claude01 && git clone git@github.com:snobol4ever/SCRIP.git SCRIP.fresh
rm -rf SCRIP        # authorized explicitly — never mv aside inside the root, a second SCRIP
                     # checkout would become its own permanent handoff-discovery hazard
mv SCRIP.fresh SCRIP
make pristine        # + a representative gate, to confirm the checkout is whole
```

**Executed by seat01, same session.** `make pristine`: 0 errors. `test_corpus_snobol4.sh`:
`✅ GATE OK: m3 PASS=893 FAIL=0 · m4 PASS=893 FAIL=0 SKIP=0 · MISSING=0`. This session's own earlier
fix (`x86_fr32_prefix()`/`x86_fr64_prefix()`, the class-c-epilogue row) confirmed byte-present in
the fresh checkout. `git status --short`: clean. The checkout is whole. Closing this FINDING.

⚠️ **One piece of pre-existing clutter surfaced by the cure, not investigated further:** the
deleted `.git` had a second registered `git worktree` (`wt-m1-landing`, a stray from an unrelated,
apparently-finished earlier session) whose administrative metadata lived inside the just-removed
`.git/worktrees/`. That worktree's checked-out files still exist as a snapshot at their own path but
can no longer do git operations (`.git` pointer now dangling) — low-stakes, not this session's to
clean up, flagging only so nobody is confused finding it.
