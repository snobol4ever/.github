# An arm whose redness depends on the working tree will eventually be graded by somebody else's commit

**hq_I, 2026-09-06,** at hq_B's argument that this deserved separating from the sitting's ledger.

## The witness

`ipl_isolation_verify_clean` was cured this sitting to answer "did the tree change during this run"
instead of "does the tree differ from HEAD". I proved it five ways. **ARM E** covered the fallback path:
*with no baseline captured, the guard must still fire, and must say it compared against HEAD.* It returned
**rc=1** and printed the right refusal. Green.

Two hours later, after I committed the sixteen fixtures that sitting produced, I re-ran the same five arms
on the rebased tree. **ARM E returned rc=0.**

Nothing about the code had changed. ARM E had been passing because **my fixtures happened to be
untracked** — that was the only thing for a HEAD comparison to find. The moment I committed them, the
comparison had nothing to report, the arm went silent, and it would have read **green forever afterwards**,
including on every future tree where the fallback was genuinely broken.

Rebuilt to create its own untracked file and remove it, in three sub-arms: clean tree with no baseline
(silent, correct); an untracked file with no baseline (**refuses, and names the HEAD fallback**); the same
file with a baseline taken after it appeared (**silent — the actual cure**).

## The rule

⭐ **An arm that depends on the STATE OF THE WORKING TREE, rather than on state it creates itself, is
being graded by whoever commits next.** It does not fail when it stops working — it goes quiet, and quiet
is indistinguishable from passing.

⛔ **The direction of the drift is what makes this hard to notice: the arm went green because the tree got
BETTER.** Committing my fixtures was the correct thing to do, and it silently disarmed a check. There is
no commit anyone could point to as the mistake, and no reviewer would have flagged it.

The only reason I caught it: **its result changed when nothing about the code had.** That is worth
treating as a signal in its own right — a green that appears after an unrelated commit is not a green, it
is an unexplained change of state.

## Where else this shape lives

Any gate or criterion that reads `git status`, globs a working directory, counts untracked files, or
depends on a fixture "already being there". The cure is uniform and cheap: **the arm creates its own
precondition and removes it**, so its population is one it owns rather than one it inherits.

Related and distinct: the sibling failure where a gate's *population* derives from the field it protects
(`test_gate_ast_shaped_refs_are_declared_ast.sh`'s own header records a wiped column making a gate pass
over zero rows). Same family — **an instrument whose subject can become empty reports empty as success** —
but that one goes quiet when the tree gets *worse*, and this one when it gets better.
