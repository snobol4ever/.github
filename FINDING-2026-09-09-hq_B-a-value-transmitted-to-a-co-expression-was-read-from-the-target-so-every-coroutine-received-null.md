# A value transmitted to a co-expression was read from the target, so every co-routine received &null

**Seat:** hq_B · **Date:** 2026-09-09 · **Tree:** SCRIP `fbda1d966` → `500401a89`, corpus `36d211ce1`,
RT_OPT=-O0, incremental `make` · **Lane:** Arizona reds M-Z (MODE NONET, Icon only)

## The claim

`expr @ C` transmitted nothing. The value was written, and then read back out of the wrong context, so
every `@&source` in every Icon co-routine yielded `&null`. Cured in `500401a89`.

## The measurement

`scrip_coexpr_activate` (`src/runtime/rt/rt_coexpr.c`) wrote the incoming value into `target->xmit` and,
after the switch, read its own result back out of `target->xmit`:

```c
target->xmit[0] = x0;                 /* value transmitted IN, stored on the target   */
scrip_coswitch(self, target, first);
out2[0] = target->xmit[0];            /* value transmitted BACK, read off the target   */
```

That pairing is correct for exactly one shape: the target returns through `scrip_coret`, which wrote its
result into its own `xmit` (`scrip_co_current->xmit`). Activate-a-generator-get-a-result therefore always
worked, and so did the whole `rt_genp` by-name generator path, which is the heaviest user of this code.

It is wrong the moment control comes back a different way. A co-expression suspended inside its own
`@&source` resumes **inside its own `activate()` frame**, whose `target` is the *source*. It reads the
source's stale `xmit` instead of the value that was just transmitted to it. Co-routines — the case `@`
exists for — never saw their argument.

⭐ **Why it hid for so long:** the defect is invisible to every one-directional use of `@`. It needs a
co-expression that is *both* activated and suspended-at-an-activate, which is the co-routine shape and
almost nothing else. The engine looked healthy because the path everything else uses was healthy.

## The cure

One context owns the value uniformly: **the value transmitted to X always lands in `X->xmit`, and a
resuming `activate` reads `self->xmit`.** `scrip_coret` now writes into `back` — the activator it is about
to switch to — rather than into itself.

For the `coret` path, `back` **is** the resuming frame's `self`, so that path is unchanged by construction.
That is not an argument, it is what the boards below measure: nothing moved.

## Witnesses (oracle: `/home/resources/icon-master/bin/icont`, both kept side by side)

| witness | oracle | SCRIP before | SCRIP after |
|---|---|---|---|
| transmit into a co-expression suspended at `@&source` | `got a` `got b` `done` | `got ` `got ` `done` | `got a` `got b` `done` ✅ |
| plain activation of a suspending generator | `1` `2` | `1` `2` | `1` `2` (unchanged) |

`arizona_tests/general/transmit.icn` now produces its **28 output words byte-exact** against
`transmit.std` — the whole three-way `reader → word → output` co-routine pipeline runs. Before the cure it
emitted 3 trace lines and a dead pipeline.

## ⛔ transmit STAYS RED, and stays this lane's

Its `.std` is 28 data lines and **76 trace lines** of 104. Two named defects remain, both `&trace`:

1. **The co-expression activation trace event is not emitted at all.** iconx prints
   `transmit.icn :   11  | main; co-expression_1 : &null @ co-expression_4` on every `@`; SCRIP prints
   nothing. That is **70 of the 104 lines** (68 transmit events + 2 `failed to` twins), counted with
   `grep -c 'co-expression_' transmit.std`. SCRIP already emits the other 6 trace lines (procedure
   entry/failed), 3 of them with the wrong line number per (2) -- so (1) is the entire remainder.
2. **The procedure-entry trace line carries the wrong line number.** For a procedure invoked through
   `create`, SCRIP attributes the *activation* site (`:11`, `:27`, `:17`) where iconx attributes the
   *create* site (`:10`, `:8`, `:9`).

## Control arms — both arms measured with the two binaries side by side

| arm | before | after |
|---|---|---|
| Arizona | m3 76/90 · m4 76/90 | m3 76/90 · m4 76/90, **identical red set** |
| Jcon | m3 66/82 · m4 66/82 | m3 66/82 · m4 66/82 |
| Icon master per-entry identity | — | examined=1557 **regressions=0 vanished=0** |
| SNOBOL4 master | — | m3 1893 FAIL=0 · m4 1893 FAIL=0 SKIP=0 · ast 28 FAIL=0 · GATE OK |

**NO BOARD MOVES.** A real oracle-proven semantic cure that flips no program, because the one program it
unblocks is red on a second, separately-named cause. Same shape as the cfo's 2026-09-08 `seq()` landing.

⛔ **The SCORE.md JCON cell reads 65 → 66 in this landing and that is NOT mine.** It is a stale cross-tree
number being re-measured on this tree; it read 66 in *both* of my arms. Named here so nobody attributes it.
