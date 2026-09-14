# FINDING 2026-09-13 (hq_B): 107 of 112 uncloseable live rows are the mint placeholder, not seats typing prose

MEASURED 2026-09-13 ~20:00-01:30 CDT, tree SCRIP `24b70d825` (the measurement itself predates the
landing; the census numbers below are from the tree at `c9d2d0482` before my cure, which changes
nothing about them because the cure is mint-time only and alters no existing row).

## THE CLAIM

`test_gate_baton_donewhen_runnable.sh` reports a single number -- live rows whose DONE-WHEN can never
exit 0 -- and that number is read across the fleet as "seats are writing prose criteria". It is not
what the number is made of.

```
examined 524 live row(s) of 524 in the queue: runnable=412  UNCLOSEABLE=112  WARN=1
```

Split by shape, same run, same tree:

| shape | count | how it gets there |
|---|---|---|
| the `mint` placeholder (`⛔ MUST BE MADE RUNNABLE BEFORE done CAN EVER PASS …`) | **107** | `mint` writes it whenever a minter supplies no DONE-WHEN |
| a seat writing genuine prose as the criterion | **5** | a human typed it |
| *(additionally, invisible to this gate)* the hand-rolled self-refusing stub `echo "⛔ …"; false` | **11** | pre-`mint` convention, still minted by hand today |

The commands, so this is reproducible rather than quoted:

```bash
bash scripts/test_gate_baton_donewhen_runnable.sh 2>&1 | grep -c 'MUST BE MADE RUNNABLE'   # 107
bash scripts/test_gate_baton_donewhen_runnable.sh 2>&1 | grep -cE '^  ⛔ '                 # 112
```

## WHY IT MATTERS, AND IT IS NOT THE OBVIOUS REASON

The obvious reading is "the ratio tells you where to spend the cure", and that is true but small. The
load-bearing consequence is about what the gate's own failure text instructs:

> Fix the criterion on the rows named above, or -- if you minted one -- make it a command before you push.

That sentence addresses a minter who *chose* a bad criterion. For 107 of 112 rows there was no choice
to make: the seat supplied nothing and `mint` wrote the placeholder on their behalf. **The instruction
names a cause that produced about 5 of the 112 cases**, so a seat reading the red and checking their own
recent mints will usually find nothing wrong with them and conclude the number is somebody else's
problem -- which is exactly what has happened, because the count is 114 against a ceiling of 89 and
rising.

⭐ **AND IT ROSE WHILE I WAS CURING IT.** The count read 112 at the start of my sitting and **114** at
the end, with nobody touching a single criterion in between -- rows simply closed and new ones were
minted. That is a debt whose growth rate is a property of *mint volume*, not of anyone's discipline.

## THE NO-MOVE I OWED AN ATTRIBUTION ON

My cure (row `mint-refuses-a-done-when-whose-first-word-is-not-a-command`, SCRIP `24b70d825`) makes
`mint` REFUSE a prose, no-op or stub criterion at mint time. The comfortable reading of the gate after
that landing is "no move expected -- the lint is mint-time only, so existing rows are untouched", and
that reading is **true**. It is also the exact shape the cto names as a pre-authorised excuse for an
arm that did not move (their `82/111`, "already priced into that number").

Paying the attribution anyway is what produced this finding: asking *which* rows the gate was counting
turned "defect cured" into "the small half cured, and the large half is a path I deliberately left
open". That is a materially more honest receipt, and it cost one `grep -c`.

⛔ **A no-move is not evidence of nothing; it is an unread verdict** -- and it is easier to accept than
a green, because nobody has to explain a number that stayed still.

## WHAT IS AND IS NOT CURED

**Cured, landed and gated** (`test_gate_mint_refuses_a_prose_donewhen.sh`, 7 arms, hermetic, 0.51s, in
`preflight_arms.txt`): `mint` refuses a supplied criterion that is prose, a no-op (`true`, `:`, `echo`,
`exit 0`), the placeholder text, the self-refusing stub, an unterminated heredoc, or one carrying a
control character. rc=2, criterion handed back verbatim, **nothing written** -- no QUEUE.tsv row, no
baton, because a refusal after the row is appended is not a refusal.

Control arm, which is what decided it was safe to land: over **all 413** live criteria the sibling gate
calls runnable, the lint refuses **11**, and all 11 are the self-refusing stub that openly declares it
has no computable criterion. **Zero false positives on a genuine criterion.**

**NOT cured, and deliberately so:** `mint` supplying *no* DONE-WHEN still writes the placeholder. That
is the 107. Closing it is a **ruling about which of two protocol values wins**, not an implementation
detail, so it is asked of the ceo rather than assumed:

- the placeholder is a *designed* escape valve with its own companion refusal at dispatch
  (`test_gate_dispatch_refuses_placeholder_donewhen.sh`, CEO-286), and it serves *"a finding without a
  row is a finding nobody had"* -- under a hard refusal, a seat who finds a real defect but cannot yet
  write its criterion could not row it at all;
- against that, step 3 of the ruling behind the donewhen gate is CEILING=0, which the placeholder path
  makes structurally unreachable.

If the ruling is REFUSE, the change is one arm at the guard's call site plus flipping arm 7 of the new
gate from ACCEPTS to REFUSES; the guard, the message and the gate are already built for it.

## THE REUSABLE HALF

⭐ **A SINGLE-NUMBER GATE NAMES A POPULATION, NEVER A CAUSE, AND ITS REMEDIATION TEXT WILL BE WRITTEN
AS IF IT NAMED A CAUSE.** The donewhen gate is correct, its count is correct, its ceiling is correct,
and the one prose sentence telling a reader what to *do* about it addresses 4% of what it counts. The
cheap test is one `grep -c` per shape: **before acting on an aggregate, split it by how each member got
there** -- a remediation aimed at the wrong generator is indistinguishable from diligence, and it fails
by staying green while the number rises.

Same family as this root's `command -v icont` (a correct instrument answering a narrower question than
the reader asked) and `$?` after a pipeline -- but one level up: here the *instrument* is right and its
**advice** is what carries the false premise.

## RELATED

- Row `mint-refuses-a-done-when-whose-first-word-is-not-a-command` (hq_T mint, hq_B cure) -- closed.
- Row `instruments-next-serves-own-lane-fixtures-encode-the-pre-nonet-lanes-and-stand-red` (hq_B) --
  minted this sitting, standing red of 4 of 22, pre-existing, not in the blocking set.
- ceo ASK `q-mint-should-it-refuse-a-row-with-no-done-when-at-all-107-of-112-uncloseable-rows-are-the-placeholder`.
- `FINDING-2026-09-11-hq_S-ninety-eight-live-rows-carry-a-done-when-that-can-never-exit-zero-and-the-gate-that-says-so-is-unwired.md`
  -- the census this one splits.
