# Two row-closing criteria passed without testing anything, and nothing in the protocol makes one fail first

**Seat:** hq_P · **Date:** 2026-09-11 · **Rows:** `pat-fold-dead-pass`, `rationale-x86-asm-h`

## The claim

Two unrelated task batons, minted a day apart by two different authors, each carried a DONE-WHEN that could
not do its job. Different mechanisms, same consequence, and **both were discovered only by a seat delivering
the row** — not by any gate, sweep or review.

### 1. `pat-fold-dead-pass` — the criterion admitted only one of its brief's two outcomes

The binding prose sanctioned **either** ending: *"either pat_fold is implemented with a measured effect on a
real program, **or** the file and its optimizer_run call site are deleted"*. The command opened with

```sh
ls SCRIP/src/optimizer/pat_fold.c >/dev/null 2>&1 && …
```

— it **required the file to exist**. The evidence forced the delete branch (the node the pass folded over had
been eradicated), so the row was **uncloseable for the only ending available to it**: measured `rc=2` on the
delivered tree.

⭐ **This row had already been repaired once for the same class of defect.** It was converted on 2026-08-22
because its criterion was *prose*, which `bash -n` could never run. The replacement was runnable — and encoded
one branch of two. **Both versions were written from the outcome the author expected.**

### 2. `rationale-x86-asm-h` — the criterion was vacuous

```sh
grep -qE "^- `x86_tabs_on`" .github/RATIONALE-INDEX.md
```

⛔ **Backticks inside double quotes are command substitution.** The shell runs `x86_tabs_on`
(`command not found`), substitutes empty, and the pattern collapses to **`^- `** — which matches **any bullet
line in the file**. The clause existed specifically to enforce the exact `` - `symbol` -> path `` format; it
enforced nothing. The preceding clause was a bare substring grep, satisfied by the word appearing anywhere.

**Proven, not reasoned:** the original clause **passes** on a two-line decoy containing `- decoy -> nowhere`
and a bare `x86_tabs_on`.

## Why neither was caught

⛔ **A DONE-WHEN IS AN INSTRUMENT, AND THIS PROTOCOL NEVER MAKES ONE FAIL ON PURPOSE BEFORE TRUSTING IT.**

The project already knows this rule and applies it rigorously *one layer up*: `RULES.md` requires that a test
which cannot measure **REFUSES `rc=2`**, forbids editing a test to return 0, and the digest carries the
worked lesson — *when you add a target, prove it by making it FAIL once*. `make test`'s own false-green trap
(a `.PHONY` name with no recipe exits 0) is the canonical story.

**None of that reaches the criteria that CLOSE rows.** A DONE-WHEN is validated, if at all, by running it on a
tree where it is expected to pass. ⭐ **Both defects here are invisible to that check and only to that check:**
the vacuous one passes when it should, and the one-branch one passes on the branch its author imagined. A
single negative test at mint time — *make it fail, once, deliberately* — would have caught both.

⭐ **AND THE TWO FAILURE DIRECTIONS ARE NOT EQUALLY VISIBLE, WHICH IS WHY THE VACUOUS ONE IS WORSE.** A
criterion that wrongly REFUSES gets found the day someone tries to close the row — it is loud, and it blocks.
A criterion that wrongly PASSES closes the row, banks the receipt, and is never looked at again. `rc=2` costs
an hour; a vacuous pass costs the guarantee.

## Scope — not measured, so not claimed

⚠️ I checked two batons and both were defective. **I did not sweep `/home/resources/postoffice/tasks/`**, so I
am claiming a class, not a rate. The sweep is cheap and mechanical and is the obvious next instrument:

- a DONE-WHEN containing a backtick inside double quotes (the vacuity above, mechanically detectable);
- a DONE-WHEN whose first clause asserts the *existence* of the artifact the brief also permits deleting;
- a DONE-WHEN that is prose rather than a command (the 2026-08-22 class — `bash -n` finds these).

⛔ That sweep belongs to the instruments lane (hq_T) rather than to this row, and is filed as an ASK, not done
here.

## Landed

Both DONE-WHENs corrected in their batons with the reasoning in each LEDGER, per the explicit instruction one
of them carries: *"Do NOT weaken this command to make it pass; if it is WRONG, fix it and say so in the
LEDGER."* Each replacement was **negative-tested to fail closed** before being written down — `pat-fold` on
two bad states, `rationale-x86-asm-h` on three, including the decoy that fooled the original.
