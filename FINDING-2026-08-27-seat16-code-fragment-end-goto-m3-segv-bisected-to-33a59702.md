# FINDING 2026-08-27 (seat16) — `probe/eval`'s CODE()-fragment `:(END)`-exit witnesses now SIGSEGV in mode-3 too (was mode-4-only); bisected to `33a59702`, root cause identified, not fixed here

Surfaced as a side effect of `probe-consolidate-m1-and-small` (the `probe/eval` family): the harness's byte-equal-or-no-delete convert step refuses any original that isn't fully green, which is expected for `ev_code_end_label_ctl.sno`/`ev_code_end_terminates.sno` (both are s192 NAMED RED, a documented standing mode-4 SIGSEGV — see both files' own header comments and `GOAL-SNOBOL4-100.md`). What was NOT expected: on the session's first build (07:55, stale relative to HEAD) both witnesses read `m3 PASS / m4 CRASH` as documented; after a mandatory `make pristine` rebuild to HEAD (`da035c7d`, 14:53:38 — done because the same staleness had already produced false-red verdicts elsewhere in this row, see the row's commits), both now read **`m3 CRASH / m4 CRASH`**. Mode-3 regressed.

## Repro

```
cd SCRIP && ./scrip /home/claude16/corpus/probe/eval/ev_code_end_terminates.sno < /dev/null
```
Prints the fully correct output (`before` / `in fragment`) and THEN segfaults — `rc=139`, reproducible 3/3, not flaky. Identical shape for `ev_code_end_label_ctl.sno`. The crash is on the way out, after all correct output is already flushed — consistent with a bad return address / stack imbalance hit at the fragment's own exit, not a logic error in the fragment body.

## Bisect (git bisect, `SCRIP`, both witnesses cross-checked)

- Known-good bound: `ef2e01be2` (07:55:56, matches the stale binary's build time) — both witnesses `rc=0`, correct output.
- Known-bad bound: `da035c7d` (HEAD, 14:53:38) — both witnesses `rc=139`.
- 7 bisect steps (each a plain `make` + repro, not full pristine — final result cross-checked with a full `make pristine` at both ends below), converged on a single commit with no gap:

**First bad commit: `33a59702db3acdf451d3ec7646f2d193f61cf9da`** — "emit.cpp/xa_flat.cpp: CLASS-C epilogue actually returns through the det-arm signature (snocone-returns-codegen)", 2026-08-27 08:11:56.
Immediate parent `4cb91e7ec2af2015c83d614bc293e21bce9775da` was independently, directly tested (not just inferred) during the bisect: both witnesses `rc=0`.
Cross-checked both witnesses again at both commits after a full rebuild (not just the bisect's incremental `make`): parent good/good, culprit bad/bad for both files. Gapless, both witnesses agree exactly on where the flip happens.

## Root cause (from the culprit commit's own message, which is unusually explicit about the risk it was taking)

`33a59702` changes `xa_flat_class_c`'s epilogue from a plain `add rsp,kt` + fall-through-to-ret, to reloading a parked signature pointer and `jmp`ing through it (`sig+8` for gamma, `sig+16` for omega) — needed so a Snocone `return`/`freturn` (a det-arm call site expecting a jmp-through-signature protocol) doesn't pop garbage off the stack. The commit message explicitly identifies that **not every CLASS-C-eligible caller uses that protocol**: "EVAL()'s runtime-compiled fragments (runtime_eval.c) reach the identical prologue but are invoked via a normal C call/ret... for them the OLD plain-release epilogue is correct and the new signature-following one segfaults" — and states this is "Gated on the existing `g_rt_fragment_emit` flag, already used for exactly this distinction elsewhere in `bb_call_proc_staged.cpp`," with EVAL itself re-verified fixed (`corpus/crosscheck/rung10/1019_eval_string.sno`).

**This bisect shows the `g_rt_fragment_emit` gate does not (or does not fully) cover CODE()-built fragments the same way it covers EVAL's runtime-compiled string fragments.** `CODE()` and `EVAL()` both compile a runtime string into executable SNOBOL4 at runtime and both plausibly reach the same CLASS-C-eligible prologue/epilogue pair by the same C call/ret convention `runtime_eval.c` uses — but only EVAL was named as verified in the commit message. `ev_code_end_terminates.sno`/`ev_code_end_label_ctl.sno` are both plain top-level `CODE()` fragments (no DEFINE, no Snocone, no det-arm call site involved at all in the source), so if the gate correctly excluded them, this commit should not have touched their behavior — but it demonstrably did, identically for both, and the parent commit is clean. The commit message itself names two other known-incomplete edges from the same change ("mode-3 Error 22... a separate mechanism needing its own fix", "a `return` nested inside an `if`... separate defect, not yet root-caused") — this appears to be a third, previously unlisted edge of the same change, on the CODE()-fragment side rather than the Snocone-return side.

## What this is NOT

- Not a stale-build artifact — cross-checked at both bisect ends with clean, freshly-`make`'d binaries (and the parent commit's result matches what a completely independent, later `make pristine` also produced).
- Not caused by this session's corpus consolidation work — no SCRIP source was touched by that work; this bisect only checked out and built pre-existing commits.
- Not the same defect s192 already tracks — s192 (still correctly cited as the reason these two files are excluded from the `probe/eval` suite conversion) is the pre-existing mode-4-only SIGSEGV. This is a distinct, newer regression that widens s192 from mode-4-only to both-modes, introduced same-day by a commit whose own message shows the author was actively managing exactly this class of risk and, per this bisect, didn't fully close it.

## Not fixed here

Root-causing stopped at "which commit, which mechanism, which gate is probably incomplete" — actually fixing it means reading `g_rt_fragment_emit`'s exact emission conditions against how `CODE()` fragments are lowered vs how `EVAL()` fragments are (`runtime_eval.c` vs whatever lowers `CODE()`) and is real codegen work under the ASM-DIFF-FIRST protocol, out of scope for a corpus-consolidation row. Left for whoever picks this up; `probe/eval`'s `KEEP.md`-equivalent (this family's consolidation commit message) already points here for context on why these two files stay loose.

## Verification

- Bisect cross-checked as described above: both bounds independently rebuilt and re-tested for both witnesses, not just relied on the bisect's own incremental build.
- Did not re-run the full corpus board or gates at the historical bisect commits (out of scope for a bisect); HEAD's own gates (`test_gate_udc.sh` 40/40, `test_corpus_snobol4.sh` 365/365 both modes) were verified separately, after this bisect, as part of the consolidation row's own handoff, at a fresh `make pristine` HEAD build.
