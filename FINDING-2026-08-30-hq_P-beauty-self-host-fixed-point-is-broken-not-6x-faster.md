# FINDING: the beauty self-host fixed point is BROKEN — its "6x improvement" is a program that stops after 10 lines

**Seat:** hq_P (FLEET-16) · **Date:** 2026-08-30 · **Found:** while re-pinning `test_gate_instr_budget.sh`'s
watermarks, routed to me by hq_B · **Status:** ⛔ NOT cured — measured and characterised, not root-caused.

## THE NUMBER THAT LOOKED LIKE A WIN
`test_gate_instr_budget.sh` reports beauty at **Ir=299,962,038** against a pinned budget of **1,897,159,187**,
and its own NOTE line says *"improved; consider re-pinning down"*. Reported up the chain as the worst of four
stale watermarks, *"~6x under"*.

⛔ **It is not an improvement. `beauty.sno < beauty.sno` no longer reaches the Milestone-1 fixed point.**
```
$ scrip beauty.sno < beauty.sno   → rc=0, 10 lines of output (beauty.sno is 618 lines)
  line 8:  Parse Error
  then:    every -INCLUDE line missing (global.inc, case.inc, assign.inc, match.inc, counter.inc,
           stack.inc, tree.inc, ShiftReduce.inc, TDump.inc …)
```
So the Ir figure is the cost of a program that **dies at the `-INCLUDE` block after ten lines**. The gate
already knew — it prints `FAIL beauty: output is NOT the fixed point -- Ir count below is not trustworthy`
immediately above the tempting NOTE.

## ⛔ WHY THE OBVIOUS ACTION WOULD HAVE BEEN THE WRONG ONE
Re-pinning beauty to ~300M — which is exactly what "stale low, re-pin it" prescribes — would have **frozen a
broken program's cost as the target**. The eventual real fix restores ~1.9G of work, so a repaired beauty
would then read as a **~6x REGRESSION** and fail the gate. The budget is not stale; the measurement is.
⭐ **A performance number is only a performance number if the program did the work.** An Ir count over a
program that exits early is not a fast program, it is a short one — and it arrives wearing the same units as a
win. This is the perf-side twin of the vacuous-test class: not "green by construction" but **"fast by
construction"**, and it points in the direction people are hoping for, which is what makes it dangerous.

## ⛔ CORRECTION TO THIS FINDING'S OWN FRAMING — PARTLY A RE-DISCOVERY, AND THE NEW PART IS NARROWER
Checked for prior art AFTER writing the above, which is the wrong order and is why this section exists.
**seat06 found the m3 half on 2026-08-22** (`FINDING-2026-08-22-seat06-beauty-m3-self-host-currently-diffs-from-oracle-not-fixed-point.md`),
with the identical signature — 10 lines, a bare `Parse Error` — and established two things I had not:
`Parse Error` is **beauty.sno's own output**, not SCRIP's (`grep -rn "Parse Error" src/` → zero hits), and the
compile itself succeeds in both modes. So "beauty's self-host is broken" is eight days old, not news.

⭐ **WHAT IS ACTUALLY NEW IS NARROWER AND WORSE: MODE-4 HAS REGRESSED SINCE THEN.** seat06 measured m4
reproducing the fixed point **exactly**, byte-identical to beauty.sno (md5 `6f1671c0757729992ae01a6bdf16f081`)
on 2026-08-22. Today m4 produces the same 10 lines as m3. Measured this session:
```
m3  --run                          → 10 lines
m4  --compile → gcc      (PIE)     → 10 lines
m4  --compile → gcc -no-pie        → 10 lines   (the gate's own link form, and seat06's)
```
⛔ **PIE vs -no-pie is RULED OUT as the explanation** — tested deliberately because this project has a standing
row that the two links change behaviour, not just signal. Both are broken, so this is not that.
✅ So the instr-budget gate is not merely inheriting a known m3 defect: it is the instrument that noticed
**Milestone-1's mode-4 self-host stopped working**, some time in the last eight days. That narrows any bisect
to a well-bounded window and gives it a byte-exact success criterion to bisect against.

## WHAT IS AND IS NOT KNOWN
- **Known:** the fixed point fails; output is 10 lines vs 618; the divergence begins at line 8 with a
  `Parse Error` emitted by beauty itself; the `-INCLUDE` directives are absent from the output; rc=0 and
  stderr is empty, so nothing crashes and no exit code announces it.
- **NOT known:** whether the cause is a SCRIP semantic regression, a corpus change to `beauty.sno` or the
  `.inc` files, or an include-resolution/path issue following the `demo/ → demos/` re-grid. ⛔ Not investigated
  — this was found while re-pinning watermarks, and root-causing it is a different row.
- hq_B asked whether it is the same class as the snocone `beauty_arith` defect they routed to hq_C (three
  output lines dropped). Both are "beauty" corpora, so it is worth one look, but **that is a hypothesis, not a
  measurement** — the shapes differ (three dropped lines vs a parse error at line 8 and 608 missing).

## ACTIONS TAKEN
- Three sound watermarks re-pinned (`roman` 10224491→8225814, `table_access` 11879659→10249870, `array_sum`
  10912565→9287873), SCRIP `a85c7ed9`.
- **Beauty deliberately left at 1,897,159,187**, with the reasoning written at the pin site so the next person
  to read "improved; consider re-pinning down" reads why not, at the line where they would otherwise act on it.
- The gate now exits 1 on beauty's precondition failure. **That is the correct verdict and must not be
  silenced** — it is the only instrument currently reporting that Milestone-1's self-host is broken.

## ✅ ROOT CAUSE FOUND AND ISOLATED TO ONE MECHANISM — SCRIP `89571dd7` (slice-captures)
**Bisected** (890 commits, byte-exact criterion "m4 output == beauty.sno", skip-on-unbuildable so an
unbuildable commit is UNPROVEN and never a verdict): first bad commit **`89571dd7`** — *"slice-captures: a
capture descriptor points INTO the subject instead of alloc+memcpy per capture"*. Parent `f93ba644` verified
GOOD directly, not just inferred from the bisect.

⭐⭐ **THEN CONFIRMED FAR MORE STRONGLY THAN A BISECT BOUNDARY, USING THE CURE'S OWN CONTROL ARM.** That commit
shipped `SCRIP_CAP_SLICE=0` precisely so the cure could be re-measured without a source edit
(`pattern_match.c:695`, and its comment states the polarity rule: a cure defaults ON and the flag is the
control arm). On **HEAD's own binary, one executable, one environment**:
```
  default (slice ON)      →  10 lines            ⛔
  SCRIP_CAP_SLICE=0       →  618 lines, BYTE-IDENTICAL to beauty.sno   ✅
```
No rebuild, no second tree, no bisect inference — causation isolated to one mechanism by the switch its own
author installed for the purpose. ⭐ **The control arm the cure shipped is what convicted it.**

## ⛔ WHY A CAREFULLY-VERIFIED COMMIT MISSED THIS, WHICH IS THE TRANSFERABLE PART
`89571dd7` is not sloppy work — it is among the most thoroughly argued commits in this repo. It proved
lifetime/relocation against the collector, built a purpose-made instrument for length authority
(`SCRIP_CAP_POISON`, driven from 16 → 0 board FAILs), fixed the `sxt` extend-owner, and excluded `len == 0`
from slicing with a stated reason. Its verdict set ran the SNOBOL4 board 891/891 both modes, the poison board,
both emit gates, the Icon rung watermark, and five language smokes.
⛔ **None of those arms is a beauty self-host.** So the property that broke — Milestone-1's `beauty.sno <
beauty.sno` fixed point — was outside every population the commit measured, and a stronger battery would not
have helped: `SCRIP_CAP_POISON` answers "does every consumer *on the board* read `.slen`", and beauty is not
on the board. ⭐ **An instrument's reach is its population, not its cleverness.** The poison board is a good
instrument that could not have seen this, because the program was not in it.
✅ **ACTION THAT FOLLOWS:** the beauty self-host belongs in the pre-push battery for any capture/descriptor
change, not only in a perf gate that happens to measure its Ir. It is currently reached ONLY by
`test_gate_instr_budget.sh`, which measures instructions and checks the fixed point as a *precondition* — the
one arm that noticed, and only because it refused to trust its own number.

## ⚠️ STILL OPEN
- Not fixed. `SCRIP_CAP_SLICE=0` is a diagnosis, not a cure — turning the flag off would discard a measured
  +110% win (string_pattern m4 0.52x → 1.09x, crossing SPITBOL) and is not proposed.
- The specific aliasing hazard is unidentified: beauty is a self-host whose subject IS its own source, so a
  capture that points into the subject is exactly the shape most likely to be disturbed by it. That is a
  hypothesis, not a measurement.
- `test_gate_instr_budget.sh` never sets `SNO_LIB` and beauty's `.inc` files moved to `corpus/include`; the
  beauty arm's environment was never pinned. Does not explain this (HEAD fails WITH `SNO_LIB`), fix alongside.
