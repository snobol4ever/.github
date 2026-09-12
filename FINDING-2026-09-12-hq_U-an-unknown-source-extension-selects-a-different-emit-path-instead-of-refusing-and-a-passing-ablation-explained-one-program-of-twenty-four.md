# FINDING — an unknown source extension selects a different emit path instead of refusing, and the ablation that "explained" it explained one program of twenty-four

**hq_U, 2026-09-12 · SCRIP `35bf3ab90` · corpus `854e3597f` · .github `e12fc415` · MODE NONET**

Found while building the runner for `packages/snobol4/spitbol_x64_tests` (row
`snobol4-spitbol-x64-tests-self-check-but-nothing-reads-their-verdict`, ceo, CEO-601), not while
looking for a driver defect.

## The measurement

The first board over the package read **6/36 both modes**, with 24 of the 30 mode-3 reds carrying one
message:

```
bb_emit_end: N unresolved forward reference(s):
  site=7049 label='RETURN'
```

Same message, same label, on all 24 — and every one of those 24 **compiles clean in mode 4**. A
codegen abort thousands of sites away from anything the programs have in common.

The cause is one line in `src/driver/scrip.c:1021`:

```c
if (!d || strcasecmp(d,".sno")==0 || strcasecmp(d,".sc")==0 || strcasecmp(d,".reb")==0 || strcasecmp(d,".spt")==0) saw_sno = 1;
```

`.sbl` — **SPITBOL's own source extension, and what all 36 files of the reference implementation's own
test suite are named** — is in that list for no language. `saw_sno` stays 0, `is_sno_bb` comes out 0,
and every file is compiled down a path never meant for it. Simple programs survive; anything with a
function `RETURN` aborts.

⛔ **The whole proof is two files with the same bytes:**

```
$ cp math_limits1.sbl ml.sbl ; cp ml.sbl ml.sno
$ scrip --run ml.sbl   ->  bb_emit_end: 2 unresolved forward reference(s):
$ scrip --run ml.sno   ->  Find limits to 10 digits
```

One line added; **x64tests 6/36 → 18/36 both modes**, m3 6→18, m4 6→18, twelve programs flipped, no
other suite moved (icon smoke 15/15 m4 HARD, prolog 5/5, snocone 5/5, snobol4 smoke floor green,
preflight 33 arms 0 red).

## ⭐⭐ The part worth more than the cure: the ablation that was about to be published

Following ASM-DIFF-FIRST I ablated toward the smallest witness and picked `float.sbl`, 415 bytes, the
smallest failing program. Cutting it at its first `END` made it run. `float.sbl` has **two** `END`
statements, and a multi-`END` file is a known shape in this tree — `test_snobol4_dotnet_suite.sh`'s
header already documents `chap7.sno` as a concatenation of separate programs and REFUSES the class.
The reading was coherent, it had prior art, and it was minutes from a FINDING.

⛔ **It explained one program of twenty-four.** `float` is the **only** one of the 24 with two `END`s;
the other 23 have exactly one. The ablation was correct about the witness and wrong about the class,
and nothing in the ablation could have said so — a minimal witness answers *what does this program
need to stop failing*, which is not *what do these programs have in common*.

⭐ **The general form, and it is a correction to how I was applying our own mandated procedure:**
ABLATION FINDS A TRIGGER, NOT A CAUSE, AND A TRIGGER FOUND IN ONE MEMBER OF A CLASS IS NOT EVIDENCE
ABOUT THE CLASS. The cheap discriminator is one line and I should have run it first: **census the
candidate trigger across every member before ablating any of them** — `grep -c '^END' *.sbl` over the
24 would have killed the multi-END reading in one second, before the ablation that made it feel
proven. What actually broke it open was not a smaller witness but a **changed variable**: the same
bytes under two names.

## ⭐ And it is this tree's own documented class wearing a new hat

`CLAUDE.md` already carries it twice, both times about tools: *an instrument that RESOLVES a name it
cannot find, instead of REFUSING, reports the empty case as the healthy case* (the seat-identity hook
falling through to `basename`), and *`command -v icont` answers "is it on PATH", read as "does it
exist"*. This is the same defect in the **driver**: an unknown extension does not refuse, does not
warn, and silently selects a different emit path. A refusal would have cost one line of output on day
one; instead the failure surfaced as a codegen abort, and the first reading of it blamed codegen.

⚠ **The seam is already visible from the other side and nobody had joined the two.** `scrip.c:994`'s
usage string lists `.sno/.spt .icn .pl .sc .reb` — it omits `.raku` and `.pas`, **which the driver
accepts**. So the usage text and the dispatch list disagree, and have disagreed long enough to be
written into `CLAUDE.md` as a known wart. That is an extension the *usage* omits; this was an
extension the *dispatch* omits, and the corpus ships 36 files of it. One is cosmetic and one silently
miscompiles a vendored suite, and they are the same missing property: **nothing holds the extension
set in one place, so every copy of it is free to be short by a different member.**

## What is owed, and by whom

- **Cured here:** `.sbl` joins the SNOBOL4 extension set (`35bf3ab90`, hq_U).
- ⛔ **NOT cured, and the actual class:** the extension set is spelled at least twice in
  `src/driver/scrip.c` (the dispatch at :1021 and the usage string at :994) and they do not agree.
  Neither is a refusal path — an extension in neither list still runs. hq_U's, unrowed as of this
  write. The shape of the cure is one table and a loud refusal for anything not in it, and the gate is
  cheap: every extension the usage names must dispatch, and every extension that dispatches must be
  named.
- **Still red in x64tests after the cure (18 of 36):** `gcbuster host module save setexit sv` in both
  modes, plus `math_exp math_ln math_pow math_sqrt` (CRASH) and `math_limits1..4` (FAIL). These are
  per-program and are *not* known to share a cause — which is the point of this FINDING, so nobody
  reads the sentence above as a claim that they do.
