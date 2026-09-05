# FINDING — SNOBOL4 pattern operands are stashed in ONE GLOBAL PER SYNTACTIC SITE, so an operand whose evaluation recurses back through the same statement silently rewrites the enclosing activation's pattern

**Seat:** hq_C (HQ-CORRECTNESS) · **Date:** 2026-09-05 · **Row:** `snobol4-gimpel-hyphenat-and-line-error-246-is-a-third-mechanism-not-the-capture-class`
**Tree:** SCRIP `47f99b0c9` + the cure below · corpus `94585e051` · RT_OPT `-O0` · incremental `make` · oracle `/home/resources/x64/bin/sbl -bf`

## THE CLAIM, MEASURED

`P = A | B` lowers to a `SNO$MKPAT` call whose operands are first assigned to **globals named after the syntactic site** — `PAT$0$V0`, `PAT$0$V1`, … — which `rt_patv_freeze()` then reads back and snapshots into the pattern instance. The site name is fixed at compile time, so **all activations of that statement share one set of globals**. If evaluating operand *j* re-enters the same statement (directly or through any call chain), it overwrites operand *i<j* of the enclosing activation *before* `MKPAT` ever reads it.

```
IR for  AA = AA | BB(N)
    ASSIGN PAT$0$V0 <- VAR "AA"        <- left operand parked in a site-named GLOBAL
    ASSIGN PAT$0$V1 <- CALL "BB"(N)    <- this call recurses into AA, re-entering THIS statement
    CALL   SNO$MKPAT("PAT$0", "2")     <- freeze reads PAT$0$V0 -- now the INNER activation's value
```

**Minimal witness (16 lines, no includes).** The inner invocation only has to *reach and fail* the same alternation statement; it never has to complete it:

```snobol
        DEFINE('AA(N)')                 :(AA_END)
AA      AA = 'y' N
        AA = AA | BB(N)                 :S(RETURN)F(RETURN)
AA_END
        DEFINE('BB(N)')                 :(BB_END)
BB      EQ(N,0)                         :S(FRETURN)
        BB = AA(0)                      :(RETURN)
BB_END
```
`AA(1)` must be `'y1' | 'y0'`. SPITBOL full-matches `y1` **and** `y0`; SCRIP before the cure matched **only `y0`** — the outer's left alternative had become the inner's value.

## WHY IT MATTERED FAR FROM THE WITNESS — A WRONG ANSWER WEARING A STACK OVERFLOW'S CLOTHES

gimpel's `OR.sno` accumulates alternatives with exactly this shape, `OR = OR | OR_EXTRACT()`, and `OR_EXTRACT` recursively calls `OR`. The inner call reached that statement, failed it, and left `OR` null — so `OR(',AB,CD')` built **`NULL | 'CD'`** where SPITBOL builds `'AB' | 'CD'`:

```
fullmatch []    SCRIP YES / SPITBOL no        <- a null alternative that should not exist
fullmatch [AB]  SCRIP no  / SPITBOL YES       <- the real first alternative, lost
```
A pattern that matches null is what `HYPHENAT.sno` then fed to its self-recursive `HYPH_PAT = … | NEUT_SUFF FENCE *HYPH_PAT`. `NEUT_SUFF` matching null means the recursion never advances the cursor, so `HYPHENAT_driver` and `LINE_driver` died with **`ERROR 246 -- stack overflow`** and zero output. ⭐ **The overflow was a symptom of a wrong answer, three files and two levels of recursion away from its cause.** Sizing the stack would have "fixed" nothing; the row that finally caught it was minted precisely because two earlier rows had named these two programs and been refuted.

## THE ABLATION THAT DECIDED IT — AND THE CONTROL THAT LIED FIRST

⛔ **My first control arm passed while the bug was live, and it passed for a reason worth writing down.** I tested `K = K | K(0)` with the inner and outer holding **the same value** `'AB'`. A clobber is invisible when the clobbering value equals the clobbered one: the test could not have failed whether or not the defect existed. Re-run with distinguishable values (`'y1'` vs `'y0'`) it fails immediately. **A control whose two arms are observationally identical is not a control** — this is the same family as the project's standing lesson that an ablation set which never removes the true cause names whatever is left standing.

The factorial that actually decided the cure:

| variation | result | what it exonerates / implicates |
|---|---|---|
| recursion removed from `OR_EXTRACT` entirely | **CURED** | the recursion is the ingredient |
| recursion hoisted out of the concatenation, still called | still red | *not* the concatenation's operand order |
| recursion lands on a **cloned** statement site | **CURED** | it is the SITE that is shared, not the function |
| same shape with **concatenation** instead of `\|` | correct both | eager operators were never affected |
| left value from a literal / a function return / a nested call | correct both | operand provenance is irrelevant |
| plain clobber of the left variable by a non-recursive call | correct both | a write alone is harmless; **re-entering the site** is the defect |

⭐ The cloned-site arm is the one that named the mechanism. Everything else only said "recursion is involved"; only the clone separated *the function recursing* from *the syntactic site being re-entered*, and those two had been indistinguishable in every witness up to that point.

## THE CURE I BUILT — AND THE CONTROL ARM THAT REFUTED IT ⛔

Carry the operand values to `SNO$MKPAT` **as call arguments** (per-activation IR slots) and freeze from those instead of re-reading the site-named globals. It is the obvious fix, it is wrong, and it is worth recording precisely because it *looks* right:

| arm | result |
|---|---|
| the 16-line witness above | **cured** |
| `OR(',AB,CD')` → `'AB'\|'CD'` | **cured** |
| `HYPHENAT_driver` | ERROR 246 gone, 4 of 6 lines correct |
| Icon smoke both modes · Snocone smoke | 15/15 · 5/5 |
| **`demo_porter`** | ⛔ **REGRESSED** — the stemmer silently under-stems (`abatement` stays whole) |

A diagnostic build printing both candidate sources at freeze time named the cause on the first run, at a 19-operand site:
```
[PATV-DIAG] PAT$6$V4 glob(v=2 slen=0 s=)  arg(v=86 slen=32766 s=-)
```
**A value node's slot is not live for a second consumer.** The assignment already consumed it; reading it again at the call yields whatever now occupies the slot, so the pattern froze junk. Reverted whole rather than landed.

⭐ **What actually caught it.** `demo_porter` is in no gate this row holds — not in the DONE-WHEN, not in gimpel, not in the smoke suites. Every arm I would have called "the control" passed. It surfaced only because the SNOBOL4 demo set was run and then **attributed by stash-rebuild A/B** rather than eyeballed: `porter` MATCH without the change, DIFF with it, while `json` and `treebank` failed identically both ways and were therefore never mine. ⛔ Three programs failed; exactly one was caused by me, and nothing but the A/B could tell them apart.

**Still open.** The untried candidate is `sno_prologue_add()` — make the `$V` temps locals of the enclosing DEFINE so the existing per-activation save/restore covers them. A runtime stack would need a new global and therefore Lon's explicit permission.

## THE SECOND DEFECT, FOUND UNDERNEATH THE FIRST — `SPAN(X)` BINDS BY NAME (CURED, LANDED)

With defect 1 cured in the scratch build, `HYPHENAT_driver` still got two lines wrong (`computer min=2 -> 3`, want `5`). Reducing that gave a **separate** defect with a 4-line witness and no recursion at all:

```snobol
        X = 'AEIOU'
        X = SPAN(X)
        S = 'ABCDE'
        S X =            ;* SPITBOL: S -> 'BCDE'   SCRIP: no match
```

`sno_pat_node()`'s `TT_SPAN` case carried a `TT_VAR` arm — **the only occurrence of that arm in the entire file** — which stored the variable's NAME and resolved it at MATCH time. `ANY`, `NOTANY`, `BREAK` and `BREAKX` all fall through to `sno_pre_req()` and snapshot at construction time, which is SPITBOL's semantics; `SPAN(*X)` is the spelling for a deferred charset and its `TT_DEFER` arm is correct and untouched. By match time the name resolved to the pattern itself, so the match failed.

gimpel `DIFF.sno` is literally `S2 = SPAN(S2)`, so `DIFF()` returned its first argument undiminished, so `HYPHENAT`'s digram table was built from the **whole alphabet** instead of each letter's complement set — a wrong table that still looked like a table.

⭐ **Why it survived so long:** binding by name agrees with snapshotting for every subject that never reassigns the variable, which is nearly all of them. The defect is invisible until a program assigns the pattern back to its own charset variable — and then it fails by returning a plausible answer, not by erroring.

**Cure:** delete the arm. **Measured on the merged tree** (SCRIP `3461226bd` + this cure, corpus at the ALL.ref desync fix, RT_OPT `-O0`, oracle `sbl -bf`): gimpel **81 → 85** both modes, Icon smoke 15/15 both modes, Snocone 5/5, `demo_porter` MATCH.

## WHAT IS STILL RED, NAMED RATHER THAN HIDDEN

This row's own DONE-WHEN is **still RED** and the row stays open: defect 1 is reverted, so `HYPHENAT_driver` and `LINE_driver` are not yet green. What is now known, and was not before, is that they need BOTH cures — the two lines that survived defect 1's cure were defect 2:
```
hyphenation min=6 -> 7   want: no hyphenation point
computer    min=2 -> 3   want: 5
```
Reduced to `'retupmoc' HYPH_PAT` with `MIN=2` → SCRIP `K=3`, SPITBOL `K=5`. ⚠ A synthetic witness over `ARB LEN(1) $ C @K *GT(K,MIN) *T<C>` **agrees with the oracle**, so the residual is *not* simply the deferred table subscript; the minimal ablation is still owed and the next actor should not inherit that guess.
