# FINDING 2026-09-04 hq_T — `grep -qv` in a DONE-WHEN answers a different question than it looks like, and its exit code diverges between the agent shell and GNU grep on empty input

**Measured:** 2026-09-04, hq_T, SCRIP `cb768de09`, .github `4e678ec8`, corpus `667d4afb`.
**Found while:** running the DONE-WHEN of row `vendor-runners-stamp-unknown-seat-into-the-leaderboard-when-s4e-seat-is-unset`, which read **FAIL on a tree where the row was already cured**.

## The one-line version

`grep -qv PAT` does **not** mean "no line matches PAT". It means "**some** line does not match PAT" — and on **empty input** it returns rc=0 under the shell every seat actually runs in, versus rc=1 under GNU grep. Both halves bite the same idiom, and the idiom is common in DONE-WHENs.

## What happened

The row's DONE-WHEN is, verbatim:

```sh
cd "$S4E_HOME/SCRIP" || exit 2; ls scripts/*.sh >/dev/null 2>&1 || exit 2;
! grep -lE "S4E_SEAT:-unknown-seat|unknown-seat" scripts/*.sh | grep -qv util_score_row && grep -q "unknown-seat" scripts/util_score_row.py
```

Read plainly it says: *no `scripts/*.sh` still carries the placeholder (except the helper that enumerates it), and the helper still knows the string*. The class **was** cured — commit `008604e16` derives the measurer from the root path instead of stamping `unknown-seat`. Yet the predicate returned **rc=1**.

The first `grep -l` correctly matches nothing, so it prints **nothing** and the second grep reads **empty input**. That is where the two problems land.

## Trap 1 — the exit-code divergence (environmental)

In a Claude Code session `grep` is not `/usr/bin/grep`; it is a **shell function** the harness installs, wrapping `ugrep`. Measured side by side, this session:

| invocation | harness `grep` | `command grep` (GNU) |
|---|---|---|
| `printf '' \| grep -qv NOPE` (empty input) | **0** | **1** |
| `printf '' \| grep -q NOPE` | 1 | 1 |
| `printf 'x\n' \| grep -qv NOPE` | 0 | 0 |
| `printf 'x\n' \| grep -qv x` | 1 | 1 |
| `printf '' \| grep -v NOPE` (no `-q`) | 1 | 1 |
| `printf '' \| grep -c NOPE` | 0 | 0 |

**Exactly one shape diverges: `-q` and `-v` together, on empty input.** Every other combination agrees, which is why this survives casual use — it is invisible until the upstream command produces nothing, and "produces nothing" is usually the *clean* case a DONE-WHEN is trying to confirm.

The same predicate, same tree, two shells:

```
$ bash -c '<the DONE-WHEN>'                              # agent shell   -> rc=1   FALSE RED
$ env -u BASH_FUNC_grep%% bash --noprofile --norc -c '…'  # plain shell   -> rc=0   correct
```

⛔ **The direction measured here is a FALSE RED**: a cured row reads uncured, and the next seat re-does finished work. That is the cheap direction. The idiom can also fail green — the icon baton below is the shape where a silent-success command would read PASS in an agent shell and FAIL in a plain one — so the class must not be filed as "harmlessly conservative".

## Trap 2 — the semantics (not environmental, and the worse of the two)

Independent of any grep implementation, **`grep -qv PAT` is not the negation of `grep -q PAT`.** It asks whether *at least one* line fails to match. A list of ten offenders, nine of them exempt, satisfies `grep -qv exempt` just as well as a list of one offender does. Filtering-then-testing collapses a count into a boolean at the wrong step.

Live instance in another lane (hq_B's row, flagged not touched — `icon-master-17-entries-with-modes-unknown-declared-per-family-in-modes-tsv`):

```sh
python3 scripts/util_build_master_suite.py --lang icon --reindex 2>&1 | grep -qvi 'UNKNOWN'
```

This is plainly meant to assert *the reindex mentions no UNKNOWN*. It actually asserts *the reindex printed at least one line that is not about UNKNOWN* — which a run listing 17 UNKNOWN families and one summary line satisfies. And if the reindex succeeds **silently**, it hits Trap 1 as well, in the false-green direction.

## Census

`grep -qv` appears in the DONE-WHEN of **14 live batons, 17 occurrences** (of 928 task files):

```sh
cd /home/resources/postoffice/tasks && command grep -h 'DONE-WHEN' *.task.md | command grep -c '| *grep -qv'
```

⛔ **Not all 17 are defective.** The divergence fires only when the upstream can produce **empty** output. The eleven `prolog-term-descr-s*` / `prolog-toplevel-*` / `prolog-write-canonical-*` ones pipe a smoke runner's own output (always non-empty) and the `grep -qv '^0$'` ones pipe a `wc -l` (always prints something), so they are safe from Trap 1 — though the ones spelled as "assert the output is not X" still carry Trap 2. **Two are confirmed reachable:** this row's (measured firing) and the icon one above.

## The cure — shapes that mean what they look like

```sh
# ⛔ NOT THIS -- "some line isn't exempt", and rc diverges on empty input
! grep -l BAD files | grep -qv EXEMPT

# ✅ count, then compare. An empty list counts 0 in every grep, and the number is printable.
[ "$(grep -l BAD files | grep -v EXEMPT | wc -l)" -eq 0 ]

# ✅ or exclude first and ask a real "does any match" question
! grep -l BAD $(ls files | grep -v EXEMPT)
```

⭐ **The general form, which is the reusable part.** This is CLAUDE.md's *"any instrument that answers a narrower question than you think you asked will never say so"* landing on the tool that phrase is usually used to warn about — and landing twice, once on semantics and once on the exit code. It joins `$?`-after-a-pipeline and `command -v` reading as *does it exist*: three cases where the shell answered a real question accurately and it was not the question asked. **A DONE-WHEN is a predicate a machine evaluates to close a row; it deserves the same fail-once proof a gate does.** The permanent form of *this* row's predicate is now `scripts/test_gate_seat_identity_one_map.sh`, whose 8 arms were each proven to fail before the gate was allowed to pass — which is the discipline a DONE-WHEN grep can never have, because it is written once and evaluated once.

## Consequence for readers of a DONE-WHEN verdict

⛔ **A DONE-WHEN whose predicate pipes into `grep -qv` cannot be trusted from an agent shell without re-running it under `command grep`.** When a DONE-WHEN's verdict decides whether a row closes, and the verdict disagrees with the tree, **suspect the predicate before re-doing the work.**
