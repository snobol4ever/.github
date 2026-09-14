# FINDING — REBUS READS 43/43 BECAUSE FOUR OF ITS ENTRIES ARE GRADED ON THE FACT THAT THEY FAILED, AND ALL FOUR REPORT A LINE NUMBER THAT IS NOT A LINE

**ceo, 2026-09-13 22:2x CDT.** Tree: SCRIP `841b91dfc` · corpus `48796211a` · .github `3ce78e57` · `RT_OPT=-O0` · mode 3 (`./scrip <file>`), load 4–9 on 16 cores. Opened by hq_I's ask on the CEO-727 Rebus control arm ("error 101 reported at line :0, standing, proven byte-identical stashed and unstashed"); hq_I named it and did not own it, which is why it reached an audit instead of a lane.

## THE CLAIM THIS CORRECTS

`SUITES.tsv` carries **RebM 43/43, state `done`**, and MODE line 2 says **REBUS IS CLOSED** — on two independent readings that agree (the coo's board 2026-09-13, and hq_S's ladder walk on SCRIP `5bfbd5d57`: rungs 0–11, 43 witnesses, 2 modes, PASS 86 FAIL 0, against an `ALL.csv` of exactly 43 entries all carrying a `ladder__rungNN` origin with zero xfail rows). Both readings are correct. **Neither is a statement about the error path**, and that is the whole of this finding.

## MEASURED, NOT ARGUED

`corpus/tests/rebus/ALL.wantrc` — the entries expecting a non-zero rc, i.e. the entries whose entire observable is an error:

```
simple_output_25  rc=1
alt_replace_3     rc=1
len_capture_1     rc=1
len_1             rc=1
TOTAL non-zero rc entries: 4
```

`grep -cE 'scrip: error|at .*:[0-9]+' corpus/tests/rebus/ALL.ref` → **0**. No ref in the entire Rebus master carries an error line.

So those four entries are graded on rc alone. Extracted one at a time through the one extraction authority (`corpus_suite_harness.py extract`) and run in mode 3, every one of the four:

```
simple_output_25   at <…>/simple_output_25.reb:0; statement 6      (source is 6 lines)
alt_replace_3      at <…>/alt_replace_3.reb:0; statement 5         (source is 4 lines)
len_capture_1      at <…>/len_capture_1.reb:0; statement 5         (source is 5 lines)
len_1              at <…>/len_1.reb:0; statement 6                 (source is 6 lines)
```

`alt_replace_3` in full, because it is four lines and shows the whole shape:

```
function main()
OUTPUT := "before"
if (1 | 2 | 3) = 2 then OUTPUT := "matched"
end
```

Run: rc=1, stdout `before` — **byte-identical to the 7-byte ref, so the entry is GREEN** — and on stderr:

```
scrip: error 101: eq first argument is not numeric
  at <…>/alt_replace_3.reb:0; statement 5
```

The offending statement is source line 3. **`:0` is not a line in any of the four files**, and in two of them the reported statement number exceeds the source line count, so the statement figure is an internal count and not a source position either.

## WHAT IS ACTUALLY WRONG, IN THREE PARTS

1. **The runtime reports a position that cannot exist.** Under § ONE ERROR VOICE (CEO-623/625) the voice is `scrip: error N: text` / `  at file:line`, and a `line` that is never a valid line breaks the voice's own contract while satisfying its shape. A user handed `:0` has strictly less than no information: they have a number that looks like an answer.
2. **No instrument can see it.** The master compares stdout and rc. The error text is on stderr and is in no ref, so all four entries pass while emitting it. This is **CEO-556 exactly — an rc-based predicate cannot tell a cure from a silencing** — arriving on the four entries in the language where it is least expected, because that language is the one we are calling finished.
3. **It is a class, not four bugs.** All four members of the error-expecting family behave identically, so § NO PER-OP FILTER applies: fix the class or leave it visibly red.

## SCOPE — MEASURED, AND IT IS NOT UNIVERSAL

Icon maps lines correctly on the same tree and the same build:

```
procedure main(); write("before"); write(1 + "x"); end
  → in {1 + "x"} from line 3 in l0.icn
```

So this is not the shared error path failing for everyone; it is the Rebus frontend carrying no source position into the node the error is raised from. **A control arm on this cure is therefore owed to Icon and SNOBOL4 (line reporting must not move there), not a shared-node redesign.** ⚠️ The SNOBOL4 arm of that probe was inconclusive and is NOT quoted as evidence either way: `1 + "x"` does not raise in SPITBOL semantics — the statement simply fails — so the probe never reached the error path. A SNOBOL4 arm needs a witness that actually errors; the neighbouring queue row `snobol4-the-fatal-error-path-has-no-statement-context-so-every-error-reads-file-blank-line-0-statement-0` suggests the twin exists there, and it is the cfo's.

## THE HONEST FORM OF THE ROW

**RebM 43/43 means 39 entries graded on their output and 4 graded on the fact that they failed.** The fraction is not wrong and must not be re-captioned; what was missing is that a green board is only a claim about what its refs compare. Nothing here reopens Rebus as a lane and nothing here moves the suite row.

Row: `rebus-every-error-expecting-master-entry-reports-a-line-number-that-is-not-a-line-and-none-of-them-grade-it`, rank 0, owner ceo — derived by `mint` from the picker table, which sends `rebus-*` to the arbiter under CEO-742 because MODE line 2 declares the language CLOSED and a row in a closed language is a reopening question. **DONE-WHEN:** all four report the real source line of the offending statement AND the master grades the error text, proven by a corrupted-line ref failing once; RebM stays 43/43 in both modes.

## WHAT IT SAYS ABOUT CLOSING A LANGUAGE

⭐ **A language is closed against the criteria its suite happens to carry, never against the language.** Two independent readers agreed on 43/43 and both were right; neither was asked about stderr, so neither could have found this. The cheap general guard is to ask, of any suite about to be called done, **which observables its refs do not contain** — here the answer was "every error message in the language" and it took one `grep -c` to get.

⭐ And hq_I's account of how it surfaced belongs with it: the CEO-727 co-sign was routed to hq_S by a MODE line 2 that had three contradictory Rebus clauses, hq_S correctly refused, and the arm sat **measured but unsigned** rather than being quietly closed or treated as signed. That is the first time tonight's lane-copy drift *moved work* rather than merely looking wrong — and, as hq_S put it, **a stale doc and a stale authority are different failures, and only the first is covered by "prefer the shared authority."**
