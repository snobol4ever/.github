# FINDING 2026-09-13 hq_S — seeding r12 from the base cures the COLD chain entry and SILENTLY DESTROYS an outer pending capture MID-MATCH

**Row:** `snobol4-aisnobol-dextern-loading-a-library-function-with-a-continuation-line-sigsegvs-in-both-modes` (hq_S, rank 0).
**Status:** the cure is committed **LOCALLY AND UNPUSHED** at SCRIP `caf7f39e6` (was `5f3c3eee5` before a rebase onto origin) (origin/main is `a732fc08c`). ⛔ **IT MUST NOT BE PUSHED AS WRITTEN.**
**Tree:** SCRIP `caf7f39e6` (was `5f3c3eee5` before a rebase onto origin) (local), corpus `f303218ad`, incremental `make`, `RT_OPT=-O0`.
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

---

## ⛔⭐ ADDENDUM — THE MISSING STOP BANNER WAS A STALE CHECKOUT, AND I CAUSED IT BY SKIPPING ONE FETCH

Lon, in-chat: *"where is the banner with success and failure?"* then *"go figure how it failed and fix that
instead of running on the side."* Both were right, and the answer is not a defect in the instrument.

`s4e_msg.sh banner` in this root emitted **0 bytes on stdout** and exited 1. The Stop hook wraps
`$(... banner ...)` in `{"systemMessage": ...}`, so it filed an **empty message on every stop** — the seat ends
silently. I traced it, found the `banner)` case had **no stdout write anywhere** in its ~300 lines, and wrote a
`printf '%s\n' "$line"` cure.

⛔ **The cure was already on origin and my insert refused itself.** Re-applying the identical patch against a
clean `origin/main` base asserted `already patched`: **`b643ea097`, landed the same day — "banner: print the
computed verdict again -- it stopped, and thirteen seats were cleared without one."** My local SCRIP was **11
commits behind** it. On the current tree the banner prints 1514 bytes and the correct ⛔ FAILURE verdict.

⭐ **The cause is this root's own PULL-BEFORE-TRUST rule, and I broke it in the first command of the session.**
I ran `git merge --ff-only origin/main` on SCRIP **without a preceding `git fetch`** (I did fetch `.github` and
`corpus` — SCRIP alone got none). It answered **"Already up to date"**, which was *true against a stale remote
ref* and which I read as *the tree is current*. FETCH-IS-NOT-CHECKOUT is written in this root's digest; the trap
is that the wrong reading produces the **reassuring** output, so nothing prompts a second look.

⭐⭐ **The general form, and it is this project's `command -v` lesson in a new costume:** an instrument answered a
narrower question than I thought I asked — `merge --ff-only` answers *"is my local ref behind the ref I last
fetched"*, never *"is my tree current"* — and it will never say so. **The tell I had and ignored:** the banner
itself printed `SCRIP: DIVERGED from origin/main` in the very trace I was reading to debug it. I was looking
past the verdict at the machinery. A blind instrument was not the problem; a stale one was, and it was saying so.

⛔ **What I nearly did, which is worse than the bug:** landed a duplicate `printf` into `s4e_msg.sh` — hq_B's
node under the NONET cut — reinventing a cure that already existed, on a stale base, and calling it a fix. The
branch was deleted unpushed. **Before diagnosing any instrument as broken, bring its repo current first**; a
stale checkout and a real defect present identically, and only one of them is yours to fix.
