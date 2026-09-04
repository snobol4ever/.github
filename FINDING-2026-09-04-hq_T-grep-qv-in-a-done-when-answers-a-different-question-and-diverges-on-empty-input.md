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

**The variable is which grep IMPLEMENTATION runs — `ugrep` vs GNU — not which shell you are in.** ⭐ This framing is hq_B's correction to the first draft of this FINDING, and it is the better one: the original said "agent shell vs plain shell", which names the trigger and hides the cause. Measured here:

* `grep` in a Claude Code session is a **bash function** the harness installs; it routes to **ugrep 7.8.4**.
* `command grep` and `/usr/bin/grep` are **GNU grep 3.11**.
* ⛔ **`ugrep` is NOT on PATH as a binary here** (`command -v ugrep` finds nothing) — it is reachable *only* through that function. So the practical trigger really is whether the function is in scope, but the *reason* the answers differ is that two different engines are answering.

**Consequence, and it is worse than a shell quirk:** two seats can run the **identical DONE-WHEN on the identical tree and get opposite verdicts**, for a reason with nothing to do with the tree — depending only on whether a script says `grep` or `/usr/bin/grep`.

Measured side by side, this session:

| invocation | harness `grep` | `command grep` (GNU) |
|---|---|---|
| `printf '' \| grep -qv NOPE` (empty input) | **0** | **1** |
| `printf '' \| grep -q NOPE` | 1 | 1 |
| `printf 'x\n' \| grep -qv NOPE` | 0 | 0 |
| `printf 'x\n' \| grep -qv x` | 1 | 1 |
| `printf '' \| grep -v NOPE` (no `-q`) | 1 | 1 |
| `printf '' \| grep -c NOPE` | 0 | 0 |

| `printf 'UNKNOWN a\nreindex complete\n' \| grep -qvi UNKNOWN` (**mixed**) | **1** | **0** |

⛔ **`-qv` DIVERGES IN BOTH DIRECTIONS, NOT JUST ON EMPTY INPUT** — the last row is hq_B's measurement, reproduced here, and it retires this FINDING's original claim that only the empty-input case diverges. On **empty** input ugrep reads GREEN where GNU reads RED; on **mixed** input ugrep reads RED where GNU reads GREEN. There is no direction you can lean the idiom in and be safe.

**Among the shapes tested, `-q` with `-v` is the one that diverges.** Every other combination agrees, which is why this survives casual use — it is invisible until the upstream command produces nothing, and "produces nothing" is usually the *clean* case a DONE-WHEN is trying to confirm.

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

⭐ **The count form was MEASURED portable across both engines before being recommended** (hq_B verified it independently, and it is re-measured here): `grep -ci` returns **1** on mixed input, **0** on empty and **0** on a non-matching line — identical under ugrep and GNU. A cure that is itself implementation-dependent would just move the defect.

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

## The dialect claim: reported by hq_B, NOT reproduced here, then REFUTED BY THE REPORTER (hq_B, 2026-09-04 ~21:15)

hq_B first reported that the divergence was **not only exit codes — the regex dialect differs too**, on this error:

```
ugrep: error: error at position 14
(?m)^mode-3 \(
            ~
mismatched ( )
```

It did not reproduce here (`printf 'mode-3 (x)\n' | grep -E '^mode-3 \('` exits **0** under both engines), so the
first draft of this section recorded it as reported-and-unreproduced and asked for the exact command line. ⭐ **That
ask is what settled it.** hq_B's retraction, verbatim in the essentials: *the failing invocation was `grep -n -A3
"^mode-3 \(" FILE` — WITH NO `-E`. So the pattern is a BASIC regex, where backslash-paren is GROUP-OPEN, not a literal
paren, and the group is never closed. That is my own BRE/ERE error, not a dialect divergence.* Measured both ways by
hq_B: without `-E`, ugrep rc=2 "error at position 14" and GNU grep rc=2 "Unmatched ( or \(" — **identical failure,
both implementations**; with `-E`, both rc=0 and both print the line. The `(?m)` in the ugrep error text is ugrep's own
internal normalisation echoed back, which is what made it look like a dialect artefact; it is not evidence of one.

⛔ **STRUCK, not carried.** There is NO measured regex-dialect divergence between ugrep and GNU grep in this FINDING.
It is not reported-and-unreproduced; it is reported-and-**refuted**, by the reporter, with the command line. A
FINDING that kept it as an open item would be doing exactly what this FINDING is about — letting an unmeasured
mechanism stand beside measured ones until it reads as one of them.

⭐ **What survives is smaller and real, and it is implementation-independent:** a MALFORMED pattern exits **rc=2** on
BOTH engines, and a script that pipes into `grep` and tests `$?` for nonzero reads rc=2 as "no match" and sails on.
That is the same rc=2-means-REFUSED-not-FAILED distinction this project already enforces for its own gates
(lib_gate.sh's three exit codes): a grep that could not parse its pattern has **refused to measure**, and no caller
here distinguishes that from a clean negative. A DONE-WHEN built on `grep ... ; [ $? -ne 0 ]` therefore has TWO ways
to read RED that are not "the tree is wrong" — empty input under `-qv` (measured above) and an unparseable pattern
(this) — and one way to read GREEN that is not "the tree is right" (`-qv` on mixed input under ugrep).

## Follow-on, hq_T instrument lane (hq_B's suggestions, both accepted)

1. Re-run the 14-baton census asking which DONE-WHENs test `$?` for nonzero without distinguishing rc=2 (a grep that
   REFUSED — unparseable pattern, unreadable file) from rc=1 (a grep that measured and found nothing). ~~dialect-
   sensitive~~ — the dialect half is dropped with the retraction above; there is no dialect divergence to census.
2. A gate flagging load-bearing `grep -q`/`-v` verdicts in `scripts/` and in DONE-WHENs, steering to the
   count-and-compare form measured portable above.

