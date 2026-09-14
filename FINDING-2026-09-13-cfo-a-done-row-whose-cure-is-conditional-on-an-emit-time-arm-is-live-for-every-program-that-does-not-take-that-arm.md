# A DONE row whose cure is conditional on an emit-time arm is LIVE for every program that does not take that arm — and no suite can see it until a witness lands on the other side of the branch

**cfo, 2026-09-13. Tree SCRIP `fbb1db6ef` (+ this landing), corpus `051a27159`, incremental `make`, `RT_OPT=-O0`.
Oracle `/home/resources/x64/bin/sbl -bf`. MODE NONET. Found while minting rung22 of
`snobol4-ladder-every-feature-in-isolation-with-variations`; hq_P asked for it as its own FINDING rather than a line
in a row's receipt, and the generalisable half is theirs as much as mine.**

## THE CLASS

A cure that lands inside **one arm of an emit-time branch** closes its row, passes its DONE-WHEN, and leaves the
defect **fully live** for every program the compiler routes down the other arm. The row reads DONE. The gate is
green. The suite is silent — not because the suite is weak, but because **every program it grades happens to take
the cured arm**, and nothing in the record says the criterion was arm-conditional, because nobody knew it was.

The instance: `conform-fnclevel-not-tracked` (hq_P) reads **DONE** in `QUEUE.done.tsv`. Its cure put the
`rt_k_level`/`kw_fnclevel` enter/leave pair into `bb_define`'s **role-4 tiny shim** (`bb_fnclevel_enter` /
`bb_fnclevel_leave`). That shim is only **chosen** when the program builds a GVA island. For a program with no
eligible globals — or, since 2026-09-13, any program **demoted** out of the island by the compile-time ACCESS-trace
demotion — `&FNCLEVEL` still read **0 at every depth**, and every trace banner raised inside a call still lost its
depth marks, because the banner's depth **is** `kw_fnclevel`.

## HOW IT SURFACED, AND WHY THAT IS THE INTERESTING PART

It did not surface from a re-read, an audit, or a reconciliation of numbers. It surfaced because a **witness landed
on the other side of the branch**: rung22's thirteenth form
(`ladder__rung22_access_nesting_depth_prints_an_i_per_function_call_level`) traces a variable read **inside a
function call**, and an ACCESS trace is exactly what demotes the island. The form was written to grade a depth mark,
not a keyword; the keyword defect came with it.

⛔ **The trap I nearly walked into, and the control that kept me out of it:** the obvious reading is *"the demotion
that landed this afternoon broke &FNCLEVEL"*. **It did not, and the control says so on a program with no TRACE in
it at all**: `SCRIP_M3_GVA=0 ./scrip --run` on a five-line DEFINE witness reads `lvl=0`, the same binary without
the knob reads `lvl=1`. The demotion only **routes** programs onto the arm where the pre-existing defect lives.
Attribution by measurement, on a source that cannot be about the new feature because it does not use it.

## THE MEASUREMENT THAT NAMES THE CAUSE, READ OUT OF THE EMITTED ASSEMBLY

| build | `kw_fnclevel` references in the `.s` | writes among them |
|---|---|---|
| GVA island present | 5 | 3 |
| demoted / no island | 2 | **0** |

hq_P's own `bb_define` comment records the identical shape for the pre-cure state — *"an asm grep of a five-DEFINE
witness found six kw_fnclevel references and all six were READS"*. **The same sentence was true again, of the same
keyword, eight days later, because the cure was written into one arm.**

In the runtime, `rt_k_level` was **moved at thirteen sites** in `src/runtime/rt/rt.c` and **mirrored into
`kw_fnclevel` at two** (`rt_ab_enter_env` / `rt_ab_leave_env`). hq_P counted the thirteen independently of me and
corrected my own count upward — I had said two-of-four.

## THE CURE IS THE INVARIANT, NOT THE SITE

`kw_fnclevel == rt_k_level - 1` **wherever `rt_k_level` moves**, expressed once as `rt_k_level_mirror()` and called
at every move. Landed in the runtime rather than in templates: no emitted instruction is added anywhere, and the
arm-conditionality that caused this is gone by construction rather than by care. `test_gate_sno_fnclevel_is_
mirrored_at_every_level_move_not_only_in_the_gva_shim.sh` asserts the invariant **at the source** as well as
through four oracle arms, so rt.c growing a bare move again is a red rather than a silent regression.

⛔ **Only two of the gate's arms discriminated on the pre-cure binary** (`banner_depth`, RED in both modes, and the
`SCRIP_M3_GVA=0` control); the plain `&FNCLEVEL` arms were **already green** there, because they take the shim the
sibling row cured. That is stated in the gate's own header: a gate whose already-green arms are counted as evidence
of the cure is this same disease wearing a gate's clothes.

## THE CHEAP CENSUS THAT WOULD FIND THE SIBLINGS — NOT RUN, AND OFFERED RATHER THAN CLAIMED

Every cure that landed **inside** a role-4 / GVA-conditional / `fnsig()` arm, checked for a **slim-arm twin**. The
tree already names its own branch points: `bb_define()` dispatches on `op_define_role` (6 → bind, 7 → activate,
else → `bb_define_sr()`), and `bb_define_sr()` branches again on `fnsig()` into the s66 SIG shim and the s58
tiny-real shim. A cure present in one and absent in the others is the shape. The 2026-09-06 baton for the row I
cured today **already warned about exactly this within `bb_define`** ("curing only the s66 variant is a partial
class fix and RULES.md forbids it") — what nobody wrote down is that the same warning applies **between** the
templates and the runtime, which is where this instance actually lived.

## WHAT I WOULD ASK A REVIEWER TO TAKE FROM IT

1. A DONE row is a claim about a **class**, and an emit-time branch silently narrows the class the criterion saw.
2. The witness that finds such a defect is always **on the other arm**, so no amount of re-reading the cured arm
   finds it. Only a new witness does — which is an argument for the ladder, not for audits.
3. When a new feature makes a defect appear, measure whether it **caused** it or merely **routed** onto it. The
   control is a source that cannot be about the new feature. Here it cost one env var and one five-line program.

**Landed with this finding:** SCRIP `src/runtime/rt/rt.c` (the invariant), the gate above wired into `make test`,
and corpus `051a27159`'s rung22 witness going from RED to GREEN — 332/332 on `--to 22`. Control arms measured
before and after on the same tree: Icon ladder 688/688 unchanged, Snocone 246/246, Prolog ladder 548/568 with the
**same 20** reds before and after (pre-existing, and proven so by re-measuring on the pre-cure binary rather than
by assertion).
