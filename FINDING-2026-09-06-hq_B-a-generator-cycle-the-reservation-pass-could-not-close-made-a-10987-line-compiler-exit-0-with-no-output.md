# A generator cycle the reservation pass could not close made a 10987-line compiler exit 0 with no output

**Seat:** hq_B (HQ-BEAUTIFY) · **Date:** 2026-09-06 · **Mode:** OCTET
**Subject:** `corpus/packages/icon/jcon-compiler` — Lon's named "doosey", the Jcon compiler written in Icon
**Cure:** SCRIP `dd148e2cf` · **Row:** `flip-jcon-compiler-jtran` (stays OPEN — see *Two defects*)

## The symptom, and why it is the expensive kind

The SCRIP-built 17-module jtran **compiled clean, linked clean, ran, exited 0, and emitted nothing.**
The icont-built jtran prints 56 bytes on `preproc t1.icn : stdout`. SCRIP printed **0**, with empty
stderr and rc=0.

⛔ **Every board that grades "did it run" scores that compiler as fine.** No crash, no diagnostic, no
non-zero status. This is the strongest argument in the corpus for oracle-diff grading over
exit-status grading, and it is worth more than the bug.

## The cause was in the build log the whole time

```
[GENHOST] ⛔ host=main RESERVES NOTHING: a generator callee (direct or transitive) is not yet
registered (forward reference) or is recursive/cyclic (unsupported ...)
```
and at run time:
```
libscrip_rt: BOMB — N-2 armed: generator call site has no reserved region ... refusing loudly
instead of emitting a wild-rbp protocol
```

`icn_gen_host_slice` (`src/templates/x86/x86_asm.h`) walks the callee graph summing per-activation
slices. On a repeat it allowed exactly **one** cycle shape — the *immediately* visited callee
(`i == nvisited - 1`). So direct recursion was carved and `a → b → a` was refused.

The cure carves a repeat into **any** ancestor, sized by the **sum of the slices around the
component**. For `i == nvisited - 1` it reduces to the previous expression exactly: a strict
generalisation of the existing self-recursion rule, not a new policy.

## The witness is eleven lines, and the controls are what made it cheap

```icon
procedure a(n); if n <= 0 then fail; suspend n; suspend b(n - 1); end
procedure b(n); suspend a(n); end
procedure main(); every write(a(3)); end
```
`iconx` prints 3/2/1. SCRIP was rc=134 in **both** modes; now 3/2/1 in both.

⭐ **Two controls, both still green, and they are the finding's spine:** *direct* recursion
(`suspend down(n-1)`) was always fine and emits no warning at all, and a plain *forward reference*
(a generator defined below `main`) was always fine. So the trigger is **neither recursion nor
forward reference alone — it is a cycle**, which is precisely what a 17-module compiler full of
mutually recursive walkers is made of.

## How a 10987-line silence became an 11-line witness in one step

**Bisect the pipeline, not the compiler.** `jtran` is a stage pipeline, so I ran its simplest
possible producer/consumer pair — `cat t1.icn : stdout`. It did **not** fall silent: it bombed,
loudly, rc=134, naming its own cause. One command turned an unbounded search into a named mechanism.

⛔ **This only worked because the runtime refuses loudly instead of proceeding with a wild rbp.** The
bomb is not noise to be silenced; it is the reason this was findable in an hour.

## ⛔ The forty minutes I lost, and the rule that would have saved them

My **first** diagnosis was wrong: I reported that a variable-held structure did not survive the
`create` boundary. It was measured against a `libscrip_rt.so` **an hour older than the tree** — the
cto's rung-38 co-expression landing (`09a1ce869`) had already cured what I was looking at. A bare
`./scrip` invocation does not trip the stale-binary refusal, and a hand ablation is *all* bare
invocations.

⭐ **A CONSISTENT ABLATION IS NOT A CURRENT ONE.** My four witnesses were internally consistent,
agreed with each other, and isolated cleanly to inline-vs-variable. All four were wrong. Rebuild
before the first witness and again after any pull, and **name the binary in the receipt** — I did
not, which is why the correction was a paragraph and not a footnote.

## Two defects, one program — the row stays open

With the cure in, jtran goes from **0 bytes to 75** against the oracle's **56**. It now speaks and is
wrong: the preprocessor stage duplicates a statement and misplaces its `#line`. That is a **second**
defect, invisible until the first fell, and it belongs to the cto from here (Lon, 16:4x — the Jcon
compiler moves to the cto).

⛔ **0 → 75 is progress, not a flip**, and the row keeps its byte-for-byte DONE-WHEN. Calling it done
at 75 bytes would be exactly the receipt this project spends its gates catching.

## What the identity gate caught on this very landing

`test_gate_icon_master_per_entry_identity.sh` joined `make test` in the cure's own commit (CEO-353)
and immediately named **2 regressions**. I stashed the patch, rebuilt, and reproduced them byte for
byte **without** it — inherited, proven bidirectionally rather than argued. Both are now rows, not
pins with no route:

- `icon-current-and-main-keywords-render-as-empty-string-not-a-co-expression-value` (rank 1)
- `icon-rung41-runtime-builtins-chdir-getenv-delay-getch-loadfunc-are-undefined` (rank 2) — four
  entries red on every board for weeks with **no row at all**

⭐ **A regression that appears while you are holding a patch is the easiest thing here to
misattribute, and the only cure is to take the patch away and look again.**

## Control arms

| arm | result |
|---|---|
| Icon per-entry identity | PASS — 0 regressions over 1557 pinned `(origin, mode)` pairs |
| SNOBOL4 master | m3 1854/1855 · m4 1854/1855, FAIL=1 — `user_function_keyword_branch_3`, hq_P's named inherited set, rank-0 row, **proven inherited bidirectionally** |

---

## Appendix (merged at hq_T's request): when the instrument, not the subject, is what moved

Both of us spent this sitting reading an instrument's noise as a fact about the tree, from opposite
directions, and the two halves are only useful together. hq_T's own write-up carries the racing-gate
mechanism and its `wait_grading` cure; this section keeps the two rules that generalise.

**⭐ A single base/patched split that agrees with your hypothesis is not evidence until the base arm is
repeated.** (hq_T's rule, kept in their words.) We had both written this up as *disagreement between two
readers* — which only helps someone who happens to have a second reader. hq_T had no second reader: they
had one reading that **confirmed what they feared**, and were one decision from reverting a cure that a
1890-entry differential later proved clean. Repeating the base arm four times on an **unchanged** tree gave
FAIL / PASS / FAIL.

⛔ **A confirming reading is the one nobody thinks to repeat.** I did the same thing in the other direction:
four `create`-boundary witnesses that agreed with each other and with my hypothesis, every one measured
against a `.so` an hour older than the tree. Agreement felt like evidence in both cases and was neither.

**⭐ A varying violation count on a fixed build is a stronger confession than a pass/fail flip.** hq_T's
base arm produced counts 2, 0, 1 on an unchanged tree. A flip has an innocent story available; a count that
moves while the build does not has none — and the count is already printed, so it costs nothing to look at.

**⛔ Position in the recipe sets the priority.** That gate is **arm 2 of 60** in `make test`: its red does not
fail one arm, it stops the other 58 including the SNOBOL4 board — with a plausible-looking cause attached to
whichever seat happens to be holding a patch.

The cheap rule that falls out of all of it: **if a control arm produces the answer you expected, run it twice
anyway.** One run is the whole price, and it is the only thing standing between a flaky gate and a reverted
cure.

