# FINDING: the meta-call re-drive bomb was a four-word entry stack and a protocol the caller never spoke

**hq_C · 2026-09-06 · SCRIP `e1c74e259` + this change · corpus `2255c6186` · RT_OPT=-O0 incremental `make`**

## The claim

`bb_call_value`'s goal arm resolved a Prolog goal at run time, entered the callee correctly, and then
resumed it with the **Icon flat-generator spine**. The callee was a **PL Byrd box**. Entry is shareable
between those two protocols; re-drive is not. The box refused loudly rather than emit the resume, and
the refusal stood for three days as `x86_bomb("meta-call re-drive: ...")`.

The cure is not a new mechanism. It is the caller speaking the protocol the callee already spoke.

## What was actually wrong, in two parts

**1. The entry stack was two words where the callee reads four.** `bb_call_proc_staged`'s PL call site
pushes `[rsp+0]=gamma [rsp+8]=omega [rsp+16]=jump-back [rsp+24]=pad`. `bb_call_value` pushed only the
gamma/omega pair, so the callee read its jump-back word out of the caller's locals, and rsp entered the
callee 8-mod-16 — an ABI violation *before* it is a protocol violation. Emitting the same four words is
what lets the landings pop the same 32.

**2. The landings banked the wrong facts.** The PL contract is: the callee hands back `rax` = its own
frame base when it RETAINED a live choice and 0 when it released, and `rdx` = its graph beta. The Icon
spine instead banks `rsp` and resumes with `mov rsp,banked; jmp [rsp]`. Against a PL callee that is not
a near-miss, it is a jump through a frame the callee still owns.

## The discriminator that had to be invented, and why

The old beta told its two arms apart with `cmp rax, 1` — the spine once-flag is exactly 1, a C-window
handle is a pointer, disjoint. **A retained PL frame base is also an arbitrary pointer**, so the same
test reads it as a C-window handle and resumes the wrong protocol. There was no spare word: the ζ grant
for `IR_CALL_VALUE` is `n` argv quads plus exactly one act/pad quad.

The fact that separates them was available but not established: the C-window arm never writes `H+8`.
Zeroing `H+8` at **alpha** makes "non-zero H with zero H+8" mean *C window* and "both non-zero" mean
*retained PL box*, using only the two granted words. The discriminator is created at alpha rather than
inferred at beta, because by beta the information is genuinely gone.

## ⛔ The part worth more than the fix: it briefly traded a refusal for a wrong answer

With the bomb lifted, two of the four inherited Prolog-master crashers went from **rc=134 with a named
refusal** to **`[]` at rc=0** — a silent wrong answer, the worst class this org grades. They were not
regressions of the cure; they were a *second* defect the bomb had been masking, and lifting the mask
published it as data.

This was caught only because the four crashers were graded by VALUE against their `.ref` rather than by
"does it still bomb". **A cure that removes a loud refusal must be graded against the oracle, not
against the refusal it removed** — otherwise "the bomb is gone" reads as success at the exact moment the
program starts lying. The A/B is on file: the pre-cure binary on this same tree bombs both witnesses.

The second defect was that a meta-called **conjunction** dispatches its arms, but `is/2` and `>/2` were
not reachable by meta-call — the identical gap `throw/1` and `=/2` had, in the same table
(`pl_meta_early`). Two names were added, one per witness that asked. **Not the family**: a census finds
~38 names sitting in that position, and bulk-seeding this table regressed two m4 witnesses earlier the
same day.

## Measured

- The four inherited master crashers `findall_directive_replace_2..5`: **PASS in both modes** (all four
  bombed at rc=134 before, on this tree).
- The class, not just the witnesses: `G = p(X), call(G), write(X), fail` printed `1` and then bombed;
  it now enumerates `1 2 done` in both modes, matching swipl.
- Rung-10 dynamic-DB slice **22/22**, m3 and m4, unmoved.
- **Icon run-graded m3 PASS=697 · m4 PASS=697 / 702, watermarks held** — the control arm that matters,
  because `IR_CALL_VALUE` is a shared node and Icon reaches it through `apply` and generic call-value.
  The new arms are gated on `cv_is_goal() && x86_fb_pinned()`, so no Icon site changes shape.

## What this does NOT fix, stated because the row's headline still reads red

`test_call` does not flip. Its blocker moved from the re-drive bomb to `setup_call_cleanup/3`, which is
part **(B)** of this row and is next. And the runtime-resolved error path still names a placeholder
culprit — `type_error(callable, ?/0)` where swipl names `type_error(callable, 1)` — which is hq_R's
`$pl_goal_guard` leaf called on the resolved goal rather than lowered in on static shape. hq_R predicted
that limit before I measured it; both probes are in the row's ledger.
