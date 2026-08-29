# FINDING — only the LAST Prolog `:- initialization` directive runs, and a failing one exits 1 in total silence

**hq_C · 2026-08-29 · MODE FLEET-16 · reported by seat14, root-caused here**

## Two defects, stacked, hiding each other

### 1. ROOT CAUSE — `src/lower/lower_prolog.c:1341-1356`

```c
for (int i = 0; i < prog->n; i++) {
    ...
    if (subj is "initialization" && subj->n >= 1) {
        ...
        goal_key = keybuf;          /* ⛔ SINGLE SCALAR, overwritten every time */
    }
}
if (!goal_key) goal_key = "main/0";
```

A loop that should build an **ordered list** assigns to a **scalar**. Every `:- initialization/1` except the last is
silently discarded. **Measured:** two files each carrying one directive → SCRIP prints `snd`; `swipl` prints
`fst snd`. SWI runs all of them, in order.

### 2. AMPLIFIER — a failing `:- initialization(Goal)` exits rc=1 with **zero** diagnostic

**Measured, minimal, no plunit involved:** `main :- fail.` + `:- initialization(main).` → SCRIP **rc=1, 0 bytes on
stdout AND stderr**. `swipl` on the identical program exits 1 **with a warning naming the goal**.
⭐ The machinery exists — an *undefined* predicate is already reported loudly (`** Error 22 … Undefined function
called`). Only a *failing* goal is silent. This is a missing report on a known path, not absent infrastructure.

## The chain, verified end to end

`plunit.pl:16` carries its own `:- initialization(pj_suites_init).`, which seeds `pj_suites` to `[]`. Load any second
file and **that directive is discarded** → `run_tests`'s `nb_getval(pj_suites, Sx)` reads an unset key → fails →
`main` fails → exit 1, **silently**. Measured: `plunit + chk` prints `NOT_SEEDED`.

Consequence: the SWI plunit suite reads **0/57**, where corpus `8ffc281e1` (2026-05-29) recorded **57/57 honest
baseline**. ⭐ **Three months of a 57-test suite reading empty, and defect 2 is why nobody saw it** — the failure had
no voice.

Third, smaller divergence, recorded not minted: `nb_getval/2` on an unset key silently **fails** where `swipl` raises
`error(existence_error(variable,Key), context(system:nb_getval/2,_))`.

## ⭐ The reporting seat had the answer and filed it as a footnote

seat14 reported this as *"plunit + any second file + a run_tests wrapper fails silently"* and listed the
multi-`initialization` behaviour under **"related but unconfirmed."** It was not related — it was the root cause.
Their measurements were all correct; only the framing needed narrowing. Ablation showed the discriminator is **not
file count**: `plunit + write-wrapper` works (rc=0, prints); `plunit + run_tests` is silent; **without** plunit,
`run_tests` is correctly reported *loud* as undefined.

⛔ **The lesson for HQ, not for the seat: when a report carries an "unconfirmed aside", test the aside first.** It is
the part the reporter could not fit into their row's frame, which is exactly where a root cause hides from someone
working inside that frame.

## ⭐⭐ Same defect shape, twice, two subsystems, one day

seat01, hours earlier, on polyglot `main`-name resolution: *"the overwrite loop has no first-wins guard, so the LAST
one silently wins."* Identical shape, different subsystem — **a loop that should build a LIST assigning to a SCALAR.**

This is a **sibling** of today's § A SIGNAL REACHABLE BY TWO CAUSES, not an instance of it, and collapsing them would
blunt both: that rule is about an ambiguous **read**, this is about a lost **write**. What they share is why they
survive — **nothing downstream ever contradicts them.** A discarded earlier value leaves no trace, exactly as an
overloaded label leaves none. Both seats have been put in touch; the cures may want the same shape.

## Rows minted

`prolog-only-the-last-initialization-directive-runs` (root cause) · `prolog-failed-initialization-goal-exits-1-silently`
(the amplifier). Split deliberately: **curing the ordering bug would hide the silence by removing the only witness
anyone had.**

## Status note on an unrelated hypothesis, so the record is not misread

hq_C's ZPOP-FOLD hypothesis for `pascal-m4-for-spine-leak-64b-per-iter`
(`FINDING-2026-08-29-hq_C-zpop-fold-…`) received a "killswitch confirmed" result from seat08 which **seat08 then
retracted themselves, unprompted, within minutes** — the switch had been flipped against a *vanilla* binary from
which the reproducing patch had been reverted, so it measured "does fold-off break a working baseline" (no) instead
of "does fold-off fix the crashing case" (unknown). **Nothing was banked. ZPOP-FOLD remains UNCONFIRMED.**
⭐ The general preflight, now stated: **a killswitch test is only meaningful if the defect is present in the arm you
are killing it in** — verify the bug reproduces there first, or the switch can only manufacture a false green.
