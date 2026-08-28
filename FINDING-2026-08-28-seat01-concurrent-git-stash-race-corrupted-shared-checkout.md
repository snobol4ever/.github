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

## Open, for whoever has context on the IR_MATCH_TAB/defer work or owns fleet git-safety infra

- `/home/claude01/SCRIP` currently has 6 files with live conflict markers (`git status` shows
  them `UU`), uncommitted, unpushed — inspect before anyone runs a destructive git command there.
- Consider whether a background Agent spawned against a seat's own checkout should be barred from
  running `git stash`/`pull --rebase`/`make pristine` against that SAME working directory while
  the spawning foreground session may still be active in it — two independent-but-related actors
  sharing one non-locking working tree is exactly the shape that produced this.
