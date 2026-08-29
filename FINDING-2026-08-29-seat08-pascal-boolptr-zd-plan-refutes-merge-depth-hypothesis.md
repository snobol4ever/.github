# FINDING — direct instrumentation REFUTES seat09's leading hypothesis for the `boolptr` field-set clobber; the operand-read backward-scan computes structurally identical offsets for the working and broken calls, and the whole relevant graph is ONE straight-line `zd_plan` run, not a multi-run merge

**seat08 · 2026-08-29 · SCRIP tree `a378a0bb` (no code shipped — a debug probe was added, used, then fully reverted; `git diff --stat` empty, vanilla rebuilt and re-confirmed reproducing the known wrong answer) · row `pascal-restore-prezeta`**

Read first: `FINDING-2026-08-29-seat09-pascal-call-argument-slots-clobbered-by-a-later-materialized-relop-argument.md`. This FINDING only covers what that one got wrong and what's now better-supported; it does not repeat the witness table or the `by_name_dispatch.c` evidence, which stand.

## What this refutes

seat09's leading hypothesis: *"`zd_out[]`'s straight-line-run construction (chasing `γ` only) does not assign a consistent depth to a node reached via TWO DIFFERENT incoming edges (the pas_mat merge)"* — i.e., the backward-scan formula (`emit.cpp:3197`, `g_zd_read[_zj] = zd_out[i] - zd_out[_k] + _xh`) computes a wrong delta for the second `__pas_field_set` call because its operand producers sit on the far side of a γ/ω merge.

**Instrumented that exact line directly** (temporary `SCRIP_PBT_ZD_DIAG` probe, printing `i, op_i, zj, k, op_k, zd_out[i], zd_out[k], xh, g_zd_read[zj]` — reverted after use). Compiled `boolptr.pas`. The two `__pas_field_set` CALL nodes (`i=15`, the working `p^.f := i>3`; `i=38`, the broken `p^.f := i<3`) show:

| call | zj | producer op | zd_out[i] | zd_out[k] | xh | **g_zd_read** |
|---|---|---|---|---|---|---|
| i=15 (works) | 0 | IR_VAR | 176 | 64  | 0 | **112** |
| i=15 (works) | 1 | IR_LIT_INTEGER | 176 | 80  | 0 | **96** |
| i=15 (works) | 2 | IR_VAR | 176 | 160 | 0 | **16** |
| i=38 (broken) | 0 | IR_VAR | 448 | 336 | 0 | **112** |
| i=38 (broken) | 1 | IR_LIT_INTEGER | 448 | 352 | 0 | **96** |
| i=38 (broken) | 2 | IR_VAR | 448 | 432 | 0 | **16** |

**The relative offsets are byte-identical between the working and broken call: 112, 96, 16, in the same operand order, every time.** `zd_out[]`'s absolute values differ (as expected — the second call sits much later in the flat sequence) but the DELTA the backward-scan hands to `ZOPQ`/`ZOPD` is not wrong and not merge-confused. Whatever corrupts `args[0]`/`args[1]` at runtime, it is not this formula computing a bad relative address.

## A second, unexpected fact: there is no multi-run merge here at all

Ran the pre-existing `SCRIP_ZD_DIAG=1` (no new code) and captured every `[ZD] h=... r=... i=...` line `zd_plan` emits for this file. **Every single armed node — 41 of them, from `i=0` to `i=47` — is claimed under `h=0`.** There is no second run head, no pass-2 omega-discovery, nothing for two different incoming edges to disagree about in `zd_out[]`'s construction. The whole relevant portion of the graph is one straight-line, monotonically-increasing-depth run (`zout` goes 16, 32, 48, ... 592 in lockstep with each armed node's `K`). This is not consistent with "the merge point gets an inconsistent depth from two different runs" — there is only one run.

## What's actually interesting: some `pas_mat` branch nodes are never armed at all

Cross-referencing the `[ZD]` dump's armed-node list against `--dump-ir`'s full 54-node graph: several IR slots are simply **absent** from the armed set — e.g. slot 12 (a second `ASSIGN ... var="__pbt1"`, distinct from the armed slot 11's `ASSIGN [10] var="__pbt1"`) never appears with a `zout`. Grepping the IR dump for both temp names shows each of `__pbt0` and `__pbt1` gets **assigned from two different places** (consistent with an if/then/else materializing the same temp on both arms) but only one assignment site per temp shows up armed in the `[ZD]` trace. I have NOT fully traced which physical branch (the literal-1 arm or the literal-0 arm) is the armed one for each of the two calls, nor confirmed that the unarmed branch is the one actually taken at runtime for the second (broken) call while the armed branch happens to be taken for the first (working) call — `i=7` in the source makes `i>3` true and `i<3` false, which is at least consistent with "the call that fails is the one whose runtime-taken branch isn't the statically-armed one," but I am flagging this as an unconfirmed pattern match, not a proven mechanism. I made two indexing mistakes trying to cross-reference `--dump-ir` slot numbers against emitter flat-array indices during this session (they are not always the same numbering) and do not trust a third attempt without fresher eyes.

## Why not chased further here

This is exactly the "core, shared, high-blast-radius machinery" seat09 already named a reason to stop, and I have now spent this sitting on two rounds of instrumentation without landing a confirmed mechanism — continuing to increase confidence, per RULES.md's own wall-clock check-in discipline, means handing off with what's confirmed rather than guessing a third round.

## Standing instructions for whoever picks this up next

1. **Do not re-pursue the merge-depth-inconsistency hypothesis as originally stated** — the two tables above refute it directly. If a `zd_plan`/`emit.cpp` fix is designed around "make the merge's two incoming depths agree," it is solving a problem that isn't present in this witness.
2. **Chase the unarmed-branch question instead**: for `boolptr`'s two `__pas_field_set` calls, determine (a) which of the two `ASSIGN ... var="__pbtN"` sites is armed (has a `zout` in the `[ZD]` dump) for each call, (b) which literal (1 or 0) that armed site writes, and (c) whether the UNARMED site is the one whose value is actually needed at runtime for the failing call. If confirmed, the mechanism would be "the emitter only ever allocates a ζ-cell for one static branch of a value-merging if/else, and the VAR-read after the merge unconditionally reads that one cell regardless of which branch actually ran" — a description of a real bug in `zd_plan`'s arming decision, not its depth arithmetic, and I have not confirmed it.
3. **`SCRIP_ZD_DIAG=1` is the right instrument for this**, not a new probe — it already prints every armed node's `zout` with no code changes needed; pair it with `--dump-ir` and cross-reference by explicit slot number printed on each line (never by file-line position — both this session's mistakes came from assuming positional alignment).
4. Full shared-node grading (SNOBOL4 blocking set, Icon watermark, Raku smoke per the standing constraints) still applies to any eventual cure — not re-run here since nothing was shipped.
