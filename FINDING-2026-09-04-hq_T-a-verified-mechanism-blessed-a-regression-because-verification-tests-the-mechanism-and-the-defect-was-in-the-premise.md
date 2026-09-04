# FINDING 2026-09-04 hq_T — a fully verified mechanism blessed a regression, because verification tests the *mechanism* and the defect was in the *premise*

**What I did:** built a harness verb to pin one master entry's ref to a SCRIP ruling, verified it thoroughly, applied it — and turned a **correct** red gate green. Reverted in corpus `33e747c2c`.

## The sequence

1. **hq_C, blocked and right to be careful.** The SNOBOL4 master reads red at `user_function_len_defer_branch_6`. hq_C reported it as *not* a regression: Lon's ruled lambda-deferred-target sugar (s264), landed by seat08 in SCRIP `04d1b9cd2` — and added, *"SPITBOL fails this construct too, so the row is SCRIP-only by construction and can never be graded against an oracle-captured ref."* hq_C **refused to hand-edit** a generated 1753-entry master and asked for a mechanism instead. That was exactly the right call.
2. **I built the mechanism.** `pin-ref`: re-anchor one entry's ref from a live run, mandatory `--ruling`, a provenance ledger (`ALL.refpins.tsv`), and a guard making `capture-oracle-refs` **refuse** a pinned entry so the oracle can never silently undo a ruling.
3. **I verified it, and the verification was good.** The rewrite touched exactly one line; `ALL.ref` was 6963 lines before and after; `ALL.sno` byte-identical; the writer is the builder's own so a pin cannot smuggle in a reindex; the capture guard proven to refuse `rc=2` naming the ruling. Then the master board went from m4 FAIL=1 to **FAIL=0** and I reported hq_C unblocked.
4. **hq_B's message arrived** with a clean-worktree bisect calling the same entry a **regression** from that same commit, in both modes.
5. **I ran the one command I should have run first:**

```
$ sbl -bf w.sno   →  before        rc=0
                     nomatch n=1
$ scrip w.sno     →  before
                     after n=1 dummy=[]
```

**SPITBOL does not fail the construct.** It runs it cleanly and gives a definite answer — and that answer is exactly what the ref already held. The ref was oracle-valid. SCRIP diverges from it. My pin rewrote the expectation to match the compiler.

## What that is

⛔ **The ICN4 false green in mirror image.** There, a cure changed the **compiler** to match a bad ref. Here, I changed the **ref** to match a bad compiler. Both make a board go green while the defect stays in the tree — and mine would have "unblocked" every lane sitting behind a red that is real.

⭐ **Every check I ran was about whether the pin wrote what I told it to. Not one asked whether what I told it was true.** That is the whole finding. The mechanism was sound, the verification was thorough and honest, the arithmetic was right, and the output was a false green — because **verification tests the mechanism, and the defect was in the premise**. A premise arrives as prose, in a message, from a colleague who is competent and acting in good faith, and it does not look like an input that needs measuring. It looks like context.

⛔ **The premise was one command from being settled the entire time.** "The oracle cannot grade this entry" is not an opinion; it is a claim about a program, and there is a binary on this machine that answers it in under a second.

## The cure, which is not "be more careful"

`pin-ref` now **asks the oracle itself** on every pin, prints the oracle's own answer, records it in the ledger line (`[ORACLE AT PIN TIME: RAN rc=0]`), and **refuses** when the oracle ran cleanly and disagrees with what is about to be pinned. The override is spelled `--oracle-disagrees-and-i-mean-it` — long on purpose, so it is a sentence someone had to type rather than a flag they might miss — and the ledger then records **both** answers.

Re-running my own bad pin now refuses, printing the oracle's two lines beneath the refusal.

⭐ **The general form:** when a tool's correctness depends on a claim the tool could check, the tool must check it. A premise that enters as a report is trusted forever; a premise the tool measures is evidence every time it runs. This is the same shape as *a test that cannot measure REFUSES* — one level up, applied to the claim rather than the measurement.

## Where it sits beside the other five

This is the sixth witness in the DONE-WHEN census, and the axes now split three ways:

| kind | witnesses | what fails |
|---|---|---|
| **could not measure** | four (argparse exit read as a refusal; a case-sensitive grep against a lowercase board; `git -C ..` at a non-repo; `grep -oE "scored="` matching `unscored=`) | the criterion never reached its subject |
| **denominator narrower than blast radius** (hq_B's) | `04d1b9cd2`'s own DONE-WHEN — green, correct, and smaller than the change | the criterion measured exactly what it claimed, and the claim was too small |
| **premise never measured** (this one) | the pin | the criterion and the mechanism were both right; the *input* was false |

⛔ The third is the most expensive, because nothing in the run looks wrong. There is no red to investigate, no traceback, no refusal — only a green board and a colleague thanking you for unblocking them.

## Still open, and not this row's

SCRIP `04d1b9cd2` regressed a **shared capture-target node**. Its own DONE-WHEN passed because it named only the witnesses the change was written for; `SHARED-NODE VERDICT SCOPE` is the law that would have caught it, unapplied because the change reads as sugar. m4 is the hard gate, so `make test` has been red on origin since that landing and every SNOBOL4 lane is blocked behind it. **Correctness lane. The cure is in the compiler, and it was never a ref.**
