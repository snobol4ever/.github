# A fully-proven cure shipped DEFAULT-OFF and was dark for eight days, while every demo profile measured the path it exists to delete

**Seat:** hq_P (HQ-PERFORMANCE) · **Date:** 2026-08-27/28 · **Mode:** DUO (Lon in-chat; MODE file rewritten by ceo to match)
**Cure commit:** SCRIP `53ddfa1d` · **Original arm:** SCRIP `72f9c772`, 2026-08-19 · **Row:** perf-pattern-defer-capture-layer-cure / Lon tier-1 demo campaign

## The claim

`bb_match_defer.cpp`'s PT-3 defer-collapse arm — the inline fast path that answers a deferred
`*group` dereference from loads instead of a three-call C round trip — was written, reviewed,
measured, correctness-graded on 1034 programs, and committed on **2026-08-19 behind a killswitch
that defaulted to OFF**. It was never promoted. It has been dark for eight days.

The arm is **unchanged** by this session. Only the polarity of its killswitch changed.

## The defect is one inverted predicate

```
patv_fast_on()   v = (e && *e && *e != '0') ? 1 : 0     OPT-IN  -> unset means NOT EMITTED
everything else  v = (e && *e == '0') ? 0 : 1           OPT-OUT -> unset means ON
```

`defer_xpat_on`, `defer_ic_on` and `rt_defer_merge_on` in the same and neighbouring files all use
the opt-out spelling. One function used the opposite one, in a file whose surrounding idiom is the
reverse, and the cure disappeared silently.

## Why nobody noticed, which is the transferable part

⭐ **A default-OFF killswitch on a CURE is not a killswitch — it is a deletion with a comment
explaining what it used to do.** It is invisible in every profile. It is indistinguishable from
unwritten code. And it survives review *precisely because the file still reads as though the cure
shipped*: the 20-line rationale comment, the measured numbers, the invariant proof are all sitting
right there above a predicate that switches them off.

This is the same family as two other defects live in the fleet this week — hq_C's Pascal grid where
`7/7 m3 = fpc` was produced by running kernels under `</dev/null` so `reps=0` and both engines
printed nothing and "agreed", and my own icon-n1 criterion `PASS>=232` already satisfied at
`PASS=249` by corpus growth. **All three are instruments that cannot distinguish "measured and
clean" from "never ran".**

The cost here was not hypothetical. ceo's tier-1 dig the same night reported calculator-1-match at
0.28x with "82.6% of cycles in the emitted match_defer boxes, 16% RT, and the 16% is one symbol,
`rt_patv_defer_get_pat_dtp`" — and asked me to *write* the ~6-instruction inline guard that would
kill it. That guard already existed. The profile was measuring the un-cured path because the cure
was compiled out.

## Measured, re-verified on today's tree

The original evidence (`72f9c772`: 1034 programs both media, zero arm-caused movers, four apparent
m3 movers all disproven by a hold-the-arm-fixed control, 112 emitting programs oracle-graded at
PASS 74 / arm-caused FAIL 0, treebank-match 1.41x and its fence twin 1.63x on disjoint windows) was
**not taken on trust** — it is eight days and hundreds of commits old. Re-measured by emit arm, m4,
`-O0`, perf instructions at each demo's committed input, both arms byte-checked against the
committed `.ref`:

| demo | OFF | ON | delta |
|---|---|---|---|
| calculator-1-match | 1095.3M | 760.1M | **−30.6%** |
| calculator-1-match-fence | 289.9M | 195.0M | **−32.8%** |
| calculator-2-match | 34.0M | 30.9M | −9.1% |
| calculator-2-match-fence | 31.3M | 28.1M | −10.4% |
| treebank / json / claws5 match + fence twins | — | — | −2.1% .. +0.5% |

⚠️ **The flat rows are an instrument limit, not a verdict on the arm**, and the distinction matters
because `72f9c772` measured treebank-match at 1.41x. Those demos' committed inputs are
pattern-COMPILE dominated: the entire treebank-match run is 9.3M instructions, and scaling its input
60x reaches only 13.4M. The original 1.41x came from a rep-loop harness (`reps=200`) that re-runs the
MATCH, which is the axis this arm moves. Those rows say *"not measurable at the committed input"*,
never *"no effect"* — and they do establish no regression anywhere.

**A rep-loop demo harness is the missing instrument**, and its absence is why a 1.41x cure could sit
dark without any board noticing.

## Swept for siblings rather than assumed unique

Every other default-OFF `getenv` in `src/templates` and `src/runtime` is either a **diagnostic**
(`DESCR_STAMP`, `RSPDIFF`, `BBPROF_MAP`, `ALLOC_HIST`, the `*_DIAG` family) or an `_OFF`-suffixed
**disable** switch (`SXT_OFF`, `ZSKIP_OFF`, `REPLMAP_OFF`), where default-OFF is the correct
polarity. **This was the only dark cure, not the tip of an epidemic.**

## Recommendation

A staging flag needs an **owner and a promotion date**, or it needs to default ON with an escape
hatch — which is what this now has (`SCRIP_PATV_FAST=0` is the control arm). A cure committed behind
a default-OFF flag with neither is indistinguishable from a cure that was never written, and the
tree cannot tell you which one you have.

## Gates

Pristine build (HQ-27): board m3 PASS=890 FAIL=0 · m4 PASS=890 FAIL=0 SKIP=0 · MISSING=0;
`test_gate_emit_no_lang` rc=0; `test_gate_template_medium_invisible` rc=0 (0 medium-branch sites —
BOTH-MEDIUM holds, the arm is pure `x86()` concat); icon smoke 14/14 FAIL=0, snocone 5/5, rebus 4/4.
