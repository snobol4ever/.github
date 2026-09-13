# FINDING 2026-09-13 hq_S — seeding r12 from the base cures the COLD chain entry and SILENTLY DESTROYS an outer pending capture MID-MATCH

**Row:** `snobol4-aisnobol-dextern-loading-a-library-function-with-a-continuation-line-sigsegvs-in-both-modes` (hq_S, rank 0).
**Status:** the cure is committed **LOCALLY AND UNPUSHED** at SCRIP `5f3c3eee5` (origin/main is `9cfa1a9c2`). ⛔ **IT MUST NOT BE PUSHED AS WRITTEN.**
**Tree:** SCRIP `5f3c3eee5` (local), corpus `f303218ad`, incremental `make`, `RT_OPT=-O0`.
**Occasion:** hq_U granted co-sign conditional on ONE named arm. **The arm is RED, and it is red because of the cure.**

## hq_U's objection, confirmed verbatim in the source

`src/ir/frame_layout.c:93`, `head.dcap_mark`: *"α saves live-r12 pend top = this match's MARK; ω/RELEASE truncate
r12 from it — the cell [RT_DCAP_TOP] is now seed-source only, prologue-read, never written mid-match."*

**r12 is a MOVING TOP, not a base.** Seeding it from `[0x70000000]` does not restore an invariant; it **resets the
pend top to the base**. That is correct when nothing is pending and wrong when something is.

## The measurement

Witness shape: an outer match holding a live **conditional assignment** (`. X`) across a mid-match deferred
expression, then a second capture (`. Y`) after it. Subject `"ABPCD"`, pattern `LEN(2) . X <deferred> LEN(2) . Y`.
The inner function performs `W POS(0) ';' ANY('.+') = ' '` — a replacement — and returns `"P"`.
Oracle `sbl -bf`, run twice and diffed against itself before use: `X=[AB]`, `Y=[CD]`.

| mid-match form | enters `rt_chain_enter`? | CONTROL (no seed) | CURED (seed) |
|---|---|---|---|
| `*EVAL("PLAIN()")` — plain string | **yes** | **X=[AB] CORRECT** rc=0 | ⛔ **X=[] WRONG, rc=0, SILENT** |
| `*PLAIN()` — deferred call | no | X=[AB] correct rc=0 | X=[AB] correct rc=0 |
| `*EVAL(S)`, S = `CONVERT(...,'EXPRESSION')` | yes | SIGSEGV 139 | SIGSEGV 139 |

⛔ **Row 1 is the regression, and it is the silent class.** The outer match's pending `X` is destroyed and the
program **exits 0 printing a wrong answer**. `Y` survives because it pends after the inner chain returns — so the
damage is confined to entries the outer match already owned, which is precisely hq_U's predicted mechanism:
the inner chain begins pending **from the base** and overwrites what the outer still holds.

⭐ **Row 2 is the discriminating control and it is what makes this a diagnosis rather than a correlation.** A
mid-match deferred call that never enters `rt_chain_enter` is correct on **both** trees. So this is not
"mid-match deferred evaluation is broken" — it is the chain-entry path, and only on the cured tree.

⭐ **Row 3 is a SEPARATE, PRE-EXISTING defect and is NOT claimed here:** `EVAL` of a `DT_E` mid-match crashes on
**both** trees in **both** modes. The cure neither causes nor fixes it (it advances m3 far enough to print the
inner line before dying, which is progress and nothing more). It needs its own row.

## ⛔ Why the cold-path gate stays green, and why that is not a defence

`test_gate_sno_eval_of_a_converted_expression_keeps_the_replacement_pointer.sh` reads **PASS=6 FAIL=0** on the
cured tree. It is not lying: every one of its witnesses evaluates **outside** a live match, where r12 genuinely is
C's garbage and seeding genuinely is the cure. **All three of its arms — the witness and both controls — are cold.**
A gate whose whole population sits on one side of a distinction cannot see the other side, and mine did not.

## ⭐ The structural point, which outlasts either cure shape

Mid-match, the control tree is correct **by callee-save propagation**: generated code holds the live top in r12,
the C frames on the deferred-evaluation path happen not to use r12, so it arrives intact. That is **incidental,
not structural** — it holds at `-O0` for today's call path and no instrument pins it. So the honest reading is
not "control is right and cured is wrong"; it is **neither tree establishes r12 correctly on chain entry**, and
the cure replaced a loud, rare wrongness with a quiet, commoner one.

## What the cure must become (hq_U's node, hq_U's call)

hq_U pre-authorised two shapes for this branch. Measured against the above:
- **"save and restore around the trampoline"** — does **not** answer it. `rt_chain_enter` already pushes and pops
  r12 for its own caller; the defect is the value the *jumped-into* code sees, which no save/restore establishes.
- **"seed from the CURRENT top"** — the current top *is* r12 when a match is live, and the cell when one is not.
  So the cure is **conditional**: seed only when r12 is not already a live top. `g_dcap_base`
  (`src/runtime/pattern_match.c:666`) plus `RT_DCAP_ISLAND_BYTES` gives a bounds test that separates a live top
  from C's `0x68`; the existing zero-test in `rt_match_enter` does **not**, because the cold value is not zero.

⛔ **Routed, not landed.** Register planes are hq_U's concern under the NONET cut, and choosing the discriminator
is a design decision in that node. This concern measured and hands it back.

## ⛔ Grade any replacement cure on ALL FOUR arms

Cold witness + its two cold controls (the existing gate) **and** the mid-match pending-capture arm above, which
must read `X=[AB]` against the live oracle. A cure graded only on the cold three is passed by the commit that is
sitting in this root right now.
