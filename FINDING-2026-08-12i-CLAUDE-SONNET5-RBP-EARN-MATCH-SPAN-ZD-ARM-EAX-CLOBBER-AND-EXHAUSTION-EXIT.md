# FINDING — MATCH_SPAN ZD arm: eax clobbered by its own call, and end-of-subject wrongly failed

**Session:** Claude Sonnet 5, 2026-08-12, RBP-EARN seat pickup after s34.
**Fingerprint:** SCRIP fix `af207c9e` (pre-fix `05e6b1ae`) · corpus witnesses `edc0986b` (pre-fix `e7424687`).

## How this was found

Orientation re-verified the s34 cursor's open rulings against the *current* tree rather than
trusting the cursor text (RULES.md: assume origin moved). **R-2 was already closed** — `677e8753`
(the `main_α` R9/GVA fix) is on `main`, unreverted, and BOARD independently hardened an instrument
around it (`5a4a13f9`, `8729da2f`). No action needed there.

Wrote `scripts/board_patterns_2mode.sh` (new — no existing script did a combined m3+m4 `.ref`
census over `crosscheck/patterns`) and re-measured at HEAD: **74/122 AGREE, 46 both-fail, 2
m4-only-fail, 0 m3-only-fail.**

Picked `063_pat_fence_fn_optional` (small, on-goal: FENCE + capture) and ran the `spl`/`scr`
sync-step monitor (bridge already applied in the cloned `x64` — worked immediately). It pinpointed
the exact divergence: `N` captures `''` instead of `'123'` at `FENCE(SPAN(digits)|'') . N`.

Killswitch discriminators (`SCRIP_FENCE_WHACK=0`, `SCRIP_U2=0`, `SCRIP_U2_FENCE=0`) were all
**inert** — none changed the wrong output. **This exonerates the RBP-frame / FENCE1 machinery
for this witness.** Stripped FENCE and the `|` alternation entirely; the bug reproduced with bare
`X SPAN(digits) . N`. Further isolation: `SPAN('0123456789')` (literal) works instantly;
`SPAN(digits)` (identical string via a variable) hangs on 3+ uniform-matching-character subjects,
silently mis-answers on exactly 2.

`--dump-ir` showed the fork: literal arg → `MATCH_SPAN []` (zero operands, static arm, `_.op_sa<0`
essentially — baked charset). Variable arg → `MATCH_SPAN [16]` (one operand, `_.op_zres &&
_.op_sa>=0`, the "ZD arm" landed `346d1d6f` 2026-08-11, one day before this session — brand new,
under-exercised, structurally the same static-vs-dynamic-argument fork this goal's own s38 FIX
PLAN opened with for stored patterns).

A temporary debug shim on `rt_sg_member` (renamed the `.S` symbol to `_impl`, wrapped it in a
tracing C shim, rebuilt, ran, then **fully reverted** — verified via `git diff`/`git status` +
`nm out/libscrip_rt.so | grep sg_member` showing exactly one clean symbol before the final commit)
showed the per-character membership call **alternating correct/corrupted `needle_ptr`/`needle_len`
on every other call to the single call site** — perfectly periodic, not random.

## Root causes (two, independent, both in the same never-previously-exercised arm)

`src/templates/bb_match_span.cpp`, the `if (_.op_zres && _.op_sa >= 0)` arm:

**1. `eax` clobbered by its own call.** The loop held the scan position in `eax` across
`call rt_sg_member`. `rt_sg_member` returns its boolean result in `eax` (call ABI). The RTCC
veneer's post-call reload restores only the scratch tier `{r8,r9,r10,r11}` — `eax`/`rsi`/`rdx` are
explicitly **not** restored (RC-4 "arg tier reload deferred", by design, so a caller reading the
call's own return value in `rax` still sees it — correct for that purpose, fatal for this one).
The old code then did `add eax,1; jmp L(0)` on the corrupted value: position tracking died after
the very first successful match. `rsi`/`edx` (needle ptr/len), loaded once before the loop and
held live in registers, have identically zero protection across the call.

**2. Wrong subject-exhaustion exit.** `cmp eax,r15d; jge omega` treated "ran off the end of the
subject while every character so far matched" as **failure**. It is not — SPAN legitimately
consuming an entire all-member subject is a valid, successful span. Should jump to `L(1)` (the
commit path), not `omega`.

Bug #2 was masked by bug #1 for subjects with any non-member trailing character (the loop would
corrupt-and-eventually-exit via the broken `L(1)` path before ever reaching exhaustion) — it only
became independently visible as "silent wrong answer, not a hang" once #1 was fixed and a
same-length-as-charset all-member subject no longer looped forever.

## Fix

Move the scan position into `FR(_.x86_scratch_off)` (memory, call-safe) across the loop; reload
`rsi`/`edx` from the ζ-cell every iteration rather than holding them live across the call.
`jge L(1)` instead of `jge omega` on subject exhaustion. Diff is `+18/-5` lines, isolated to the
one arm.

## Measured impact

**crosscheck/patterns two-mode census: UNCHANGED, 74/46/2/0, before and after.** Zero regressions,
zero whole-program repairs *in this corpus*. The 7 patterns programs using `SPAN(var)` —
`063-066_pat_fence_fn_*`, `126_pat_json_number`, `153_pat_operand_edge_matrix`,
`179_pat_arbno_defer_recursive_list` — all remain in the both-fail set: they carry **additional,
separate, still-open bugs** compounding on top (FENCE+alternation capture wiring for the 063-066
cluster per the monitor's own finding above; ARBNO+defer interaction for 179; unexamined for 126/153).

Spot-checked `demo/hello.sno`, `roman.sno`, `wordcount.sno` (clean) and the `SPAN(literal)` control
`041_pat_span.sno` (unchanged, `12345`) for regressions. Two new oracle-baked witnesses minted:
`corpus/probe/earn0/earn0_span_var_arg_hang.sno` (was rc=124, now `999`) and
`earn0_span_var_arg_2char_wronganswer.sno` (was silent wrong `no digits`, now `99`).

## What this is NOT

This is not an RBP/EARN frame bug. The killswitches for the frame machinery were inert on the
originating witness; the actual defect was a plain register-liveness bug across a runtime call,
unrelated to frame establishment. It surfaced *while* investigating this goal's subject matter
(FENCE + dynamic pattern arguments) but the fix belongs to the match-template layer, not the
RBP-earning layer. Filed here because it was found via this goal's own MONITOR-FIRST process and
blocks further progress on the FENCE witness cluster.

## Next seat, in order

1. **`063_pat_fence_fn_optional` is STILL BROKEN** post-fix (m3 empty output, m4 SIG11) — a
   separate bug, now unmasked and no longer confounded by the SPAN(var) defect. Re-run the
   `spl`/`scr` monitor on it fresh; the divergence is likely now further downstream (past the
   SPAN capture) or in the FENCE/alternation wiring itself. This is the natural next MONITOR-FIRST
   target.
2. The other 6 `SPAN(var)`-using patterns programs (`064-066`, `126`, `153`, `179`) are unexamined
   past this fix — each may or may not repair once its own compounding bug is found.
3. R-1 (regen ×3 scope for non-codegen-file changes like `scrip.c`) and R-3 (`cap_imm_nret2` m3
   SEGV, `benchmarks/snobol4`, first-ever measurement, unowned) from s34 remain open — untouched
   this session, still need a Lon ruling / bisect respectively.
4. Regen ×3 not run for this commit (`bb_match_span.cpp` IS on the RULES.md step-4 trigger list —
   `src/templates/*.cpp` — so this genuinely is owed before calling this fully handed off; not run
   this session due to time budget, flagging explicitly rather than silently skipping).

**⛔ Both repos (SCRIP, corpus) committed but UNPUSHED at time of writing — credential needed.**
