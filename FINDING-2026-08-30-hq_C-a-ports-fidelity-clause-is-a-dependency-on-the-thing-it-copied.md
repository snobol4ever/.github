# FINDING 2026-08-30 hq_C — a port's fidelity clause is a dependency on the thing it copied

**Tree:** SCRIP `b54c1c95` → cured `60f244e3` · measured 2026-08-30, seat `hq_C`. Closes the gap hq_P
flagged honestly on their own landing: *"the Icon pair was fixed by argument and symmetry and is NOT
graded against the Icon oracle — no witness there exercises a NUL-leading string."*

## The claim

Icon string comparison stopped at the first NUL. Witness, scrip vs `icont`+`iconx`, one file:

| | `*x` | `x == ""` | scrip | oracle |
|---|---|---|---|---|
| `x := char(0) \|\| "abc"` | 4 | | **TRUE** | differs |
| `y := char(0)` | 1 | | **TRUE** | differs |
| `x == y` | | | **TRUE** | differs |

Three sinks carried it. All three are fixed in `60f244e3`.

## ⛔ Two of the three fixes changed NOTHING observable

`by_name_dispatch.c`'s relop tail and `lower_common.c`'s `BINOP_S*` arm both did `strcmp` on values.
Both are genuinely wrong, genuinely on the path, and **the witness printed the identical wrong answer
after each was fixed.** I only found the real site because I re-ran the witness rather than trusting
the edit — the trap hq_P had described to me hours earlier, hit from the other side.

The reason is in the third file's own header: **59.8% of arrivals are string relationals and never
reach C at all.** `rt_jct_relop` is hand-written assembly (`src/runtime/rtx/rtx_icnrel.s`), an
Icon-exclusive RTX fast path that bails to C only for shapes it declines.

## ⭐⭐ Why it survived three separate C fixes — the generalizable part

The asm carried this comment, and **it was correct when written**:

> *PORT != FIX: the string arm reproduces strcmp's NUL-terminated, slen-IGNORING semantics exactly,
> **because that is what the C tail does**. Making it slen-aware would be a behaviour change wearing a
> port's clothes.*

That is good engineering — a port must not silently change semantics. But the C tail has since been
made length-aware three times over (`values.c` `descr_identical`, `core.c` `is_numeric_like` and its
siblings, and the two sinks above), so this arm became **the only code still preserving the retired
semantics, defended by a justification that had evaporated.**

**THE RULE: A PORT'S FIDELITY CLAUSE IS A DEPENDENCY ON THE THING IT COPIED, AND NOTHING LINKS THE
TWO.** "Because that is what X does" is true only until X changes. It is strictly worse than ordinary
stale prose, because it does not merely *describe* the code — it *authorises* it, so a reader who
checks the comment comes away convinced the divergence is deliberate and correct.

**Practical form:** when you fix a C path, grep its RTX/asm/JIT twins for a comment that justifies
itself by reference to that path. The search target is the phrase *"because that is what … does"*, not
the symbol you changed — the twin does not call the thing it copied, which is exactly why no
call-graph search finds it.

This is the third member of a family now: hq_B's `rung34_bridge_setof` comment describing the false
green it was written to cure; hq_P's `flat_gen` comment whose "only Icon generator graphs carry the
term" *was* the bug; and this. In all three the code and its justification were separated by an edit
nobody could have known to make.

## Verdict scope

`lower_common.c` and `by_name_dispatch.c` are shared sinks, so every frontend was graded. Pristine:
SNOBOL4 m3 1672/0 · m4 1672/0 · icon 14/0 both · prolog 5/0 both · snocone 5/0 · rebus 4/0 · raku
722/0 REFUSED=2 of 724 · `make test` rc=0. Because the change is in Icon's hottest comparison path,
the Icon vendor suites were run as an extra control arm — both rc=0 at their published floor:
Arizona 89 total, m3 38 pass / 0 REJECT, m4 39 / 0 REJECT; JCON 81 total, m3 40, m4 38.
