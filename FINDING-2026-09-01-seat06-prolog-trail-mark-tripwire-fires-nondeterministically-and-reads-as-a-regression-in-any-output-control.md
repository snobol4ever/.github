# FINDING — the corrupt-trail-mark tripwire fires NONDETERMINISTICALLY, and will read as a regression in any output-diff control arm

**seat06, 2026-09-01, FLEET-16.** Found while running the control arm for slice
`prolog-term-descr-s1-write-format-printers` (SCRIP `6bfe74cf2`).
⛔ **Not mine to fix** — trail machinery belongs to hq_P's `calling-convention-depth-tracked`, which every
Term→DESCR slice is told not to touch. Routing, not curing.

## What fires

`corpus/tests/prolog/rung10_programs_puzzle_12.pl` and `..._13.pl`, mode 3:

```
SCRIP FATAL: pl_trail_unwind refuses corrupt trail mark -719325200 (top=27, caller=0x734b4e674f51): its PRODUCER handed over garbage.
SCRIP FATAL: unwinding it would index ents[-1] and write 16 bytes past the trail array. TRIPWIRE, not a cure.
```

The mark value is a different garbage pointer on every run (`-719325200`, `-390072336`, …); `top=27` is
stable. The tripwire itself is working exactly as designed — it is refusing an out-of-bounds write and
saying so. **The defect it points at is upstream, in whatever produces the mark.**

## The measurement, and why it is the point

I hit this as a **2-of-16 divergence** between a reference binary saved before my change and the binary
after it — the classic shape of "your change broke two programs." It is not. Eight runs per binary per
program:

| program | reference binary (pre-change) | modified binary |
|---|---|---|
| `puzzle_12` | FATAL in **3/8** runs | FATAL in **2/8** runs |
| `puzzle_13` | FATAL in **5/8** runs | FATAL in **5/8** runs |

⭐ **On the single pass that flagged it, it fired for the REFERENCE on `puzzle_12` and for MINE on
`puzzle_13` — one each way.** That opposite-direction split is what exposed it as nondeterministic; a
one-directional flip would have looked exactly like a regression I had caused, and I would have gone
hunting in my own diff.

## Why this is worth a FINDING and not just a note

**Every slice of the Term→DESCR umbrella is verified by output-diffing against a pre-change binary** —
that is the method the umbrella's own brief prescribes ("the oracle for a printer is its own output …
byte-identical before and after, both modes"). These two programs will produce a spurious diff in roughly
a third to half of all such runs, in either direction, for any slice, whether or not it touched anything
related.

⛔ The failure mode is asymmetric and expensive: a seat sees 2 programs differ, believes their own change
caused it, and either burns the session hunting a phantom or — worse — "fixes" a printer that was already
correct. A seat who instead sees *zero* diffs on a lucky pass learns nothing and moves on.

## What to do

1. ⛔ **Do not treat a `puzzle_12`/`puzzle_13` diff as a regression signal without re-running.** Repeat the
   program several times on **both** binaries and compare *rates*, not a single pass. A single-pass output
   diff is not evidence here.
2. **Fixing it belongs to `calling-convention-depth-tracked`** (trail machinery). The tripwire's own words
   name the target: *"its PRODUCER handed over garbage"* — the bug is in the mark's producer, not in
   `pl_trail_unwind`, which is behaving correctly by refusing.
3. ⭐ **Consider whether these two belong in a control-arm set at all while this stands.** A control arm
   that is nondeterministic in a third of runs is not a control arm; it is a coin flip that costs a
   session each time it lands wrong.

## Adjacent, same session, recorded so it is not re-derived

`make test`'s SNOBOL4 master arm currently **refuses (rc=2, "harness produced no SUITE_BOARD line")**
rather than passing or failing: `corpus_suite_harness.py run` on the 1576-entry master suite SIGTERMs
without emitting a board line. **Reproduced on the unmodified tree**, with the box at loadavg ~17 and four
other seats running the identical suite concurrently. ⭐ It is a REFUSAL — "cannot measure" — and must not
be read as either green or red. A seat that quotes `make test` as passing here has quoted a run that never
produced a verdict.

## Postscript, same session — a third measurement hazard, this one self-inflicted and easy to repeat

The first version of this FINDING cited SCRIP `ae8f4d36b`. **That commit does not exist on origin.**
RULES mandates `git pull --rebase` before push and re-proving the gate afterward; the rebase rewrote the
commit, and the real landed SHA is `6bfe74cf2`. I had already written the pre-rebase hash into this file,
into the slice baton's `## NEXT`, and into its LEDGER.

⭐ **The trap is ordering, and it is built into the required workflow:** you commit, you cite the SHA in
the prose you write next, and only *then* does the mandatory rebase rewrite it. `handoff_status.sh`
correctly reported `SYNCED` throughout — the *work* was pushed the whole time — so nothing flagged it.
The dangling citation is invisible to every green check.

⛔ **Verify a cited SHA with `git merge-base --is-ancestor <sha> origin/main` before leaving it in prose,
not with `handoff_status.sh`.** SYNCED answers "is my tree pushed", never "does the hash I wrote down
still exist". Corrected here and in the baton.
