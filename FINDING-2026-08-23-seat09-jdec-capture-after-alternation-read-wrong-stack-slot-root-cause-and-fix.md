# FINDING — seat09: root cause and fix for the jdec()/dcap reentrancy corruption

**Date:** 2026-08-23 · **Seat:** seat09 (`/home/claude09`) · **Row:** `jstring-escape-dcap-pump-segv` (assigned by hq_C) · **Supersedes the hypothesis in, but does not replace:** `FINDING-2026-08-22-seat09-jstring-capture-with-any-escape-segvs-rt-dcap-pump.md` (§3's `g_dcf_top` stack-bookkeeping hypothesis was the right shape — reentrancy — but the wrong mechanism; see §2 below for what it actually is).
**Status:** ROOT-CAUSED AND FIXED. `src/emitter/emit.cpp` patched, `make pristine` rebuilt, corpus/broad-corpus/crosscheck/instr_budget(beauty self-host) gates all green with zero new regressions (§4).

## 0. WHAT CHANGED SINCE THE ORIGINAL FINDING

Between the original finding (2026-08-22) and this session, someone (commit `53c1323a`, 2026-08-23 00:09:45, message "jstring capture: refuse a capture entry that cannot lie inside the subject") landed a **defense-in-depth guard** in `rt_dcap_pump()` (`pattern_match.c:647-663`): before trusting a capture entry's `len`/`saved_delta`, it now bounds-checks them against the subject length and, if they don't fit, prints `CORRUPT CAPTURE ENTRY refused` and skips the entry (`rc=1`, match fails cleanly) instead of reading out of bounds. **This guard is correct, valuable, and should stay** — it is what turned the original SIGSEGV/SIGABRT into a clean, bounded refusal, and it is a legitimate last-line-of-defense against any *other* class of stale-entry bug that might exist or reappear. But it is a symptom guard, not a fix: with only the guard in place, `jdec()` reentered via a deferred `*estr` capture target still silently produces a **wrong** decode (the escape is dropped) even though the program no longer crashes. This finding root-causes and fixes the actual defect so the guard goes back to being dormant (never fires) on this witness.

## 1. ROOT CAUSE, CONFIRMED BY DIRECT MEASUREMENT (RULES.md ASM-DIFF-FIRST §3, gdb with hit-context, no watchpoints)

**It is not a `g_dcf_top`/stack-of-frames bug.** `g_dcf[]` LIFO reuse across the reentrant `jdec()` call is correct: traced every push/pop (`c_rt_dcap_end_ok_open`/`rt_match_end_all`) across the outer json-string match → `rt_call_proc_descr(name=estr)` → `jdec`'s fast-path check → `jdec_lp`, and every `mark`/`top` pointer pair is exactly self-consistent with the entry counts actually written. `g_dcf_top` depth-2 at the crash site is expected, correct reentrant nesting, not corruption.

**It is a stack-pointer imbalance in the compiled capture-commit code**, specific to a `.` (immediate) capture whose pattern immediately follows a `MATCH_ALTERNATE` (SNOBOL4 `(A | B)`), when that capture is classified as using **"spine" storage** (`havehome()`/`_.op_frame_need==0`, `src/templates/bb_match_capture.cpp`'s phase0/phase1 "ordinary, unchanged mechanism" branches, `readhome()`/`writehome()` = `FR(_.op_off)`, i.e. an RSP-relative slot). Measured directly in a symbol-ful mode-4 binary (`gcc -g` on the emitted `.s`, breakpoints on the actual emitted labels — no source-level breakpoint could reach JIT'd mode-3 code, so mode-4 was built specifically for this):

```
n652_match_assign_save_α  (phase0 SAVE, "seg"):  rsp=0x7fffffffd550, writes [rsp+0]=r14d=0   (position 0, correct)
n653_match_alternate_α    (the alternation):     rsp=0x7fffffffd540  (sub rsp,16 from n652, never popped on the success path)
n654_match_assign_cond_α  (phase1 COND, "seg"):  rsp=0x7fffffffd510, reads eax=[rsp+0]

0x7fffffffd550 - 0x7fffffffd510 = 0x40 = 64 bytes.
```

The alternation (`bb_match_alternate.cpp`, `sub rsp,32` on entry) plus its winning arm's own transient stack use (`BREAK(bslash)`, `bb_match_break.cpp`) together grow `rsp` by 64 bytes on the way through, and **the success path never restores it** before falling through into the capture's COND code. The COND code, unaware the alternation moved rsp, reads `[rsp+0]` at the *new*, 64-bytes-deeper rsp — memory it never wrote, containing whatever the intervening call frames left there. In the reentrant case that memory holds fragments of the C call chain's own addresses (`saved_delta` decoded as the low 32 bits of a `0x7ffff25ff060`-shaped stack address — exactly the "huge garbage" the original finding's crash showed), which is what trips the `CORRUPT CAPTURE ENTRY` guard (or, pre-guard, the SIGSEGV/heap-exhaustion). **This is not reentrancy-specific in principle** — any `.` capture positioned right after an alternation, spine-classified, will read a wrong (if less dramatically wrong) position; reentrancy just supplies memory content bad enough to be visibly, deterministically bad.

The classifier that decides spine-vs-activation-frame storage, `frame_need_of()` (`src/emitter/emit.cpp:746`), already has a purpose-built escape hatch for exactly this class of hazard — `cap_in_alt_arm()` flags a capture *nested inside* an alternation's own arm, `cap_in_repeat_body()` flags one inside an ARBNO/FENCE body, and a `SCRIP_CAP_NEST` scan flags a capture followed by an ARBNO/dynamic-DEFER/VALUE later in the same statement. **None of them cover "my SAVE and COND straddle an alternation that isn't containing me, it's immediately before me"** — `(BREAK(bslash) | '') . seg` is not a capture *inside* an arm, it is a capture *of* the alternation's own result, and every existing check misses that shape.

## 2. THE FIX

`src/emitter/emit.cpp`, one new classifier predicate plus one wire-in, matching the existing `cap_in_alt_arm`/`cap_in_repeat_body` style exactly:

```c
static int cap_save_cond_gap_has_alt(const IR_t * nd) {
    if (!nd || nd->n_operands < 1 || !nd->operands[0]) return 0;
    return nd->operands[0]->op == IR_MATCH_ALTERNATE;
}
```

Wired in to `frame_need_of()`'s `IR_MATCH_ASSIGN_IMM`/`IR_MATCH_ASSIGN_COND` case, after the existing `cap_in_alt_arm`/`cap_in_repeat_body` checks: `if (!h) h = cap_save_cond_gap_has_alt(nd);`

`--dump-ir` on a minimal `jdec`-shaped repro confirms `operands[0]` of a `MATCH_ASSIGN_COND`/`_IMM` node is that capture's **immediate predecessor pattern element** (verified on the sibling `ec` capture too: its `operands[0]` is the preceding `MATCH_LEN` node, not an alternate) — a direct, single-hop structural link, not an index-range heuristic, so this is exact rather than approximate. When the predecessor is `IR_MATCH_ALTERNATE`, `frame_need_of` now returns 1, routing the capture through the already-correct, already-proven activation-frame (`CFC(0)`, RBP-relative, per-invocation-fresh) mechanism instead of the imbalanced spine path — the same mechanism `IR_MATCH_ARBNO`/`FENCE0`/`FENCE1` already always use for the identical reason.

An index-range-scan version of this same check (walk `g_emit_cfg->all[min(si,ni)+1 .. max(si,ni))` looking for `IR_MATCH_ALTERNATE`) was tried first and **did not work** — it never found the alternate. Left as a note for whoever next touches this area: `g_emit_cfg->all[]`'s array order does not reliably reflect program order for SAVE-vs-COND index comparison the way `cap_in_repeat_body`'s ARBNO/FENCE-span check gets away with (that check bounds a *span containing* the capture, not a *gap between* two specific other nodes, which is a different and apparently less order-sensitive query). The direct `operands[0]` link avoided the whole question.

## 3. VERIFIED CORRECT, NOT JUST CRASH-FREE

Direct entry inspection (gdb, `pattern_match.c:697`, dumping the pushed `rt_dcap_e` records before `rt_dcap_pump` touches them) on the exact 4-byte witness `"\t"` (`printf '"\\t"'`), post-fix:

```
entry0: varname=seg saved_delta=0 len=0     # BREAK(bslash) at position 0, first char IS backslash → correct empty capture
entry1: varname=ec  saved_delta=1 len=1     # the char right after the backslash ('t') → correct
```

Both byte-exact correct (previously: `saved_delta=4066373728 len=228593568`, guard-refused). `CORRUPT CAPTURE ENTRY` no longer fires on this witness, in either mode-3 or mode-4.

## 4. REGRESSION VALIDATION

`make pristine` rebuild, then, all on the fixed tree vs. the same suites re-run on the pre-fix tree via `git stash`/`git stash pop` for direct A/B:

- `test_corpus_snobol4.sh`: 358/359 pass both m3 and m4 — the one failure (`demo_treebank`, "Error 235 subscripted operand is not table or array") reproduces **identically on the pre-fix baseline**, unrelated (table/array subscripting, not captures).
- `test_broad_corpus_snobol4.sh`: 343/344 both modes, same single pre-existing `demo_treebank` failure, no others.
- `test_crosscheck_snobol4.sh`: 323/323 both modes, **zero** m3-vs-m4 divergence.
- `test_gate_instr_budget.sh`: PASS — beauty.sno self-hosts to its byte-identical fixed point and stays within its pinned `-O0` instruction budget (no measurable perf regression from the narrow classifier addition).
- `.s` artifact regen (RULES.md handoff order, all six scripts) surfaced a handful of pre-existing `EMIT-FAIL`/`AS-FAIL` entries (Icon `rung36_jcon_*`, Prolog `coverage_pl_nodes`/`rung10_programs_puzzles`, Rebus, Snocone `rungB05_alt_*`/coverage) — every one spot-checked (Icon `IR_ASSIGN` guard, Prolog duplicate-symbol assembler error, Snocone `GZ#5 subset` lowering gap) reproduces **identically on the pre-fix baseline**; none are new, and none are related to `IR_MATCH_ASSIGN_COND`/`ALTERNATE` classification. The regen diffs themselves are large (this tree was well behind origin at session start — see the seat's own banner/handoff — so most of the size is unrelated drift catching up in one shot, not this fix).

## 5. WHAT'S STILL OPEN

- The guard added in `53c1323a` is now expected to be permanently dormant on this witness but is left in place deliberately (§0) — it is real, independent insurance, not redundant scaffolding to strip out.
- This finding does not touch `json-alternate-af-spin` (the comma-spin defect) — per the task baton's own QA note, the two are independent blockers on `citm_catalog.json` and this row's closure does not unblock that one.
- `jdec()`'s escape-table decode logic itself (`esc[ec]`, `\uXXXX` via `jutf8`) was not exercised end-to-end against a real oracle diff in this session — the capture-position defect was upstream of and masked correctness-testing that logic; now that positions are right, that's newly possible but out of this row's scope.
- The general shape "a `.` capture's immediate predecessor is a stack-shifting construct the classifier doesn't know about" may have siblings beyond `MATCH_ALTERNATE` (e.g. could `MATCH_DEFER` or `MATCH_VALUE` in predecessor position hit the same imbalance?) — not measured; flagging for whoever next works this classifier, not claiming it here.
