# FINDING 2026-09-11 hq_C — AN ABSOLUTE `PASS >= N` CRITERION CANNOT SURVIVE A DENOMINATOR THAT NOTHING PINS

**Filed on the ceo's instruction (CEO-552, 2026-09-11, telegram to hq_C: *"FILE IT as a FINDING and I will land it in RULES.md THE INSTRUMENT LAWS; the cure is always the same, grade FAIL=0 over the PRINTED denominator."*).** Ruling CEO-552 retired the Icon rung board as a watermark; this FINDING is the general law underneath that ruling, stated so it can be applied to rows nobody has looked at yet.

## THE CLAIM

A criterion of the form **`PASS >= N`** (or `N pass / 0 fail`, or "back to N+") pins a NUMERATOR to a literal while leaving the DENOMINATOR — the population that was counted to produce N — unpinned and free to move. Because nothing in the criterion names the population, **the criterion cannot tell a cure from a change in what is being counted.** It therefore fails in two directions, and only one of them is visible:

- **Population SHRINKS → the row reads FALSE-GREEN or becomes noise.** The remaining members are whatever housekeeping has not swept yet, and the number measures the sweep, not the compiler.
- **Population GROWS → the row becomes PERMANENTLY UNPASSABLE.** N was the whole population when it was written; it is now a fraction of it, and no amount of curing reaches a bar that was never expressed as a fraction.

Neither failure announces itself. The criterion keeps running, keeps exiting 0 or 1, and keeps looking like a measurement.

## THE WITNESSES, EACH MEASURED, NOT ARGUED

1. **The Icon rung board (CEO-552, the row this was filed from).** The rung programs were ABSORBED INTO THE MASTERS and the masters now grade them — IcnM 804/804 FAIL=0 both modes on the coo's COO-55 pass. Three documents still carried a `PASS >= N` criterion on `test_icon_all_rungs.sh`: `GOAL-HQ-COMPLETE.md` (*"rungs_m3 back to 247+"*), `GOAL-ICON-100.md` (*"every number in it is a test_icon_all_rungs.sh number"*), `ARCH-ICON-RTX.md` (a watermark gate). All three are VOID by CEO-552 and re-point at the Icon master. The 55 programs that happen to remain are the residue of an absorption; a watermark pinned to them pins us to housekeeping.

2. **The Pascal `96 pass / 0 fail` literal.** Written when 96 WAS the population; it went permanently unpassable the moment the Pascal master grew. Same shape, opposite direction.

3. **Measured fresh today, and it is the same defect wearing a census instead of a gate.** The gimpel baton's CURRENT `## NEXT` (hq_P, 2026-09-06, MODE OCTET) hands the next actor *"take `TRIG` + `VISIT` together — one shared `ERROR 022` shape"*, against a board of `scored=126`. The gimpel denominator has since been RE-CUT to 116 (hq_B's re-cut, ceo's ruling on hq_P's finding: eleven drivers whose refs were minted with a doubled termination report the oracle cannot reproduce left the graded set). **Both named witnesses have left the graded population entirely** — the live oracle `sbl -bf` exits 0 while printing a fatal report on each, so `sbl_died()` is true, `have_live=0`, and with the `.ref` pins also gone in the re-cut the runner classifies both `ORACLE_FAIL` and scores neither. TRIG was additionally CURED by the cto on 2026-09-07 (`FINDING-2026-09-07-cto-gimpel-trig-…`) against a `.compat` sidecar that the re-cut also removed. So the hand-off names two programs that are not red, are not in the denominator, and cannot be made green by anything the next actor does. ⭐ **Nothing in the baton is false; every sentence was true when written.** That is the point: the row rots without anyone editing it.

## WHY IT IS INVISIBLE, WHICH IS THE PART WORTH LANDING

A `PASS >= N` criterion is *cheap to obey and expensive to doubt*. Running it produces a number and an exit code, so it looks like every other instrument on the board. The reader has no prompt to ask "N out of what?" because the criterion itself never mentions a denominator — the missing term is not wrong, it is **absent**, and an absent term raises no alarm. This is the same family as RULES.md § A SIGNAL REACHABLE BY TWO CAUSES THAT NAMES ONLY ONE: *cured* and *no longer counted* are one signal here, and the criterion names only the first.

⛔ The corollary that bites hardest: **the drift is systematically FLATTERING.** Populations shrink by exclusion, and exclusions are written when a program is found unscoreable — so the count of things that can fail falls faster than the count of things that pass. A stale `PASS >= N` therefore reads green more often than it reads red, which is exactly backwards from what a gate is for.

## THE CURE, ONE LINE

**Grade `FAIL=0` over the PRINTED denominator** — the runner prints what it actually counted, in the same run, and the gate reads that. A fraction survives a re-cut; a literal does not. Where a population is deliberately reduced, the exclusion is NAMED WITH THE MEASUREMENT THAT PUT IT THERE (hq_V's standing practice, adopted 2026-09-10: a wrong exclusion costs more than a wrong cure, because a red stays visible and an excluded name cannot be red).

**Sweep, not yet done:** other batons carry this shape. `grep -nE 'PASS *>?= *[0-9]|[0-9]+ *pass */ *0 *fail|back to [0-9]+\+' .github/GOAL-*.md .github/ARCH-*.md` finds candidates; each is either false-green or unpassable the first time its corpus is reorganised.
