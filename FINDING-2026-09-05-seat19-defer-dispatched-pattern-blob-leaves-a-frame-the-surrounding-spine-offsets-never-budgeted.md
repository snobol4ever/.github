# FINDING 2026-09-05 seat19 — root cause, confirmed by gdb: a DEFER-dispatched compiled-pattern
# "blob" leaves 32-80+ bytes of its own activation frame on the stack across its γ transfer, and
# every fixed-offset spine reference after it in the same statement was budgeted for exactly 16

**Row:** `snobol4-shared-pattern-primitive-as-function-argument-fails-in-callee-reopened` (hq_U lane).
**Status:** ROOT CAUSE FULLY PINNED, EXACT BYTES ACCOUNTED FOR, NO FIX LANDED. Three candidate
minimal patches were tried and rejected (see § WHY NO QUICK PATCH EXISTS) — this needs a real
design decision, not a blind edit, per the caution the original finder (seat02) already gave and
that RULES.md's own witnessed incidents back up.

Read first: `FINDING-2026-09-05-seat02-a-pattern-primitive-passed-as-a-function-argument-always-fails-to-match-inside-the-callee.md`
(the original repro, scope table, and false-green-by-coincidence) and the reopened task's own GOAL
(the false-closure history). This finding does not repeat that evidence — it completes the "SOURCE
LEADS ... NOT a confirmed fix site" section with an actual, gdb-verified mechanism.

## THE MECHANISM, IN ONE SENTENCE

`IR_MATCH_DEFER`'s compile-time stack-growth budget (`zd_k()`, `emit.cpp:2509`, and the matching
`_xh += 16` at `emit.cpp:3275`) is a **universal, fixed 16 bytes**, but when the deferred value
resolves at runtime to a *compiled pattern* (any non-literal primitive — `LEN`, `ANY`, `SPAN`,
`RPOS`, …), the dispatch mechanism that invokes it (`bb_glue_pass_wires_blob`, landing in a box
built by `bb_compile_pat_tree_sz`) **actually leaves 48–96+ bytes on the stack across the success
(γ) transfer**, not 16. Every box compiled *after* the `MATCH_DEFER` in the same statement — in
our witness, `RPOS(L-1)` — reads its own operands via a compile-time-fixed `[rsp+N]` displacement
computed under the false 16-byte assumption. The real value is silently offset by the excess, so
`RPOS` reads garbage instead of "L-1", the RPOS check that should succeed instead fails, and every
scan-position retry of the whole `WRD PAT RPOS(L-1)` pattern fails identically — hence
"unconditionally, deterministically" per the original FINDING's own words.

Literal-string DEFER targets are unaffected because they never enter this dispatch path at all —
`bb_match_defer.cpp`'s inline-cache fast arm does a byte compare in place and only ever pushes the
same 2 words (16 bytes) the surrounding chain was compiled to expect. That is the entire reason
`MATCH(2,"SS")` works and `MATCH(1,LEN(1))` does not: two different runtime code paths inside the
same `IR_MATCH_DEFER` box, only one of which matches its own compile-time budget.

## THE EXACT BYTE ACCOUNTING (gdb-verified, mode 4, both binaries built at SCRIP `23f342b4d`+pull)

Witness pair (differ in exactly one token, the PAT argument):
```
sibling (passes): DEFINE("MATCH(L,PAT)")  WRD="LEAV"  MATCH(1,"V")      :S(OK)F(BAD)  [WRD PAT RPOS(L-1)]
witness (fails):  DEFINE("MATCH(L,PAT)")  WRD="LEAV"  MATCH(1,LEN(1))   :S(OK)F(BAD)  [WRD PAT RPOS(L-1)]
```
`--dump-bb` on both: **the compiled `MATCH` procedure body (proc MATCH's own box graph, `LBL__MATCH`
through `n35_match_end`) is byte-identical between the two programs** — same box kinds, same wiring,
same slot count. The divergence is entirely runtime: which code path `n33_match_defer_α` takes.

Tracing `n33_match_defer_α`'s two arms by hand, in units of bytes-of-rsp-consumed from its own
entry (`D0`) to landing at `n34_match_rpos_α` (RPOS, the box right after PAT in the pattern chain):

| Path taken | Net rsp delta reaching RPOS | Matches the 16-byte budget? |
|---|---|---|
| DT_S fast arm (literal `"V"`, `edx==2` inline compare) | **16** (2 pushes: old-r14, resume-addr) | ✅ yes — this is what `zd_k()` assumes |
| DT_P arm (`LEN(1)`, dispatched via `bb_glue_pass_wires_blob(4,5)` into the `dtp_fn_of`-compiled box) | **96** | ❌ 80 bytes over budget |

The 96 comes from, in order: match_defer's own 2-word push (16) + the compiled LEN(1) box's own
`push rbp` (8) + its `sub rsp, 0x28` local frame (40, = `blob_head_bytes()` = 40 because
`sn4_blob_casmark()` is true here) + its success-path re-push of {saved rbp, dup γ-label,
dup ω-label, resume-snippet address} (32, never released before the `jmp` onward) = 16+8+40+32 = 96.

`n34_match_rpos_α`'s compiled code (`emit.cpp`'s generic offset driver) reads its "L−1" operand via
`mov rax, [rsp+88]` — a single fixed constant baked in when the statement was compiled, under the
assumption that everything between "L−1 is computed" and "RPOS reads it" contributes exactly the
budgeted amount. Confirmed live via gdb on the mode-4 linked binary: breaking at the JIT'd/compiled
`fn` (`bb_compile_pat_tree_sz`'s return value) and single-stepping shows **5 clean invocations at
scan positions r14 = 0,1,2,3,4** (so the *outer* scan/backtrack loop is not the bug — it retries
correctly at every position, literal and DT_P alike) — but at r14=3, where `LEN(1)` correctly
succeeds and advances r14 to 4 (the position `RPOS(0)` should then confirm), execution lands at
`n34_match_rpos_α` with rsp 80 bytes lower than the sibling program reaches the identical label at,
so `[rsp+88]` reads 80 bytes into the wrong slot instead of the "0" that `L-1` (L=1) evaluates to.
Compare against `dtp_fn_of`'s own instrumentation (`SCRIP_PSTAMP_TRACE=1`): `fn=... zsz=96 zstatic=1`
— note `zsz=96` is *exactly* the same number this trace derives by hand for the DT_P path's total
rsp consumption, confirming the accounting rather than coincidence (though nothing downstream
actually consults `zsz` — see next section).

## `dtp_zsz_of`/`dtp_zstatic_of` ARE DEAD CODE — NOT THE MISSING WIRE, BUT A NAMED RED HERRING

`dtp_zsz_of()`/`dtp_zstatic_of()` (`src/ir/dtp.h:12-13`, defined `pattern_match.c:41-42`) look like
exactly the accessor a caller would use to ask "how much stack will this compiled pattern need" —
and have **zero call sites anywhere else in the tree** (`grep -rn` confirms). They are not the
missing link to a fix; the actual growth is emitted unconditionally by the `_blob_wire` machinery
in `emit.cpp` (below) regardless of whether anyone ever reads `zsz`. Do not spend time wiring these
up as if that were the fix — the growth is real, present in the generated code, and the problem is
that the *consumer* (RPOS's fixed offset) has no way to learn about it, not that the *producer*
failed to report a number nobody asked for.

## SOURCE OF THE 96, PRECISELY

- `bb_pat_build.cpp:85-114` (`bb_compile_pat_tree_sz`): sets `g_emit.flat_jmp_entry=1` and
  `g_emit.flat_pat=1` for any runtime-compiled DEFER pattern (this is what `dtp_fn_of` calls).
- `emit.cpp:3411-3412`: `_wire_stub` is false here (neither of its two conditions apply to a
  `flat_pat` graph); `_blob_wire = (!_wire_stub && flat_jmp_entry && flat_pat) = 1`. This is the
  ONLY call site of `bb_glue_pass_wires_blob` in the whole tree (`bb_match_defer.cpp:264`), so
  `_blob_wire` is specifically *the* DEFER-dispatch convention, not a generic one shared elsewhere.
- `emit.cpp:2436-2442` (`blob_frame_bytes`): even with `count==0` (no ARBNO/capture/FENCE1 registry
  slots — true for a bare `LEN(1)`), it still returns `blob_head_bytes()` (`emit.cpp:2347`:
  **24 or 40, never 0**) rather than 0. This is what makes the framed (`_bfb>0`) exit path fire for
  even the most trivial leaf pattern.
- `emit.cpp:2995` (the "R-4(b) BLOB ACTIVATION FRAME" comment/code) and `emit.cpp:3420-3423` /
  `emit.cpp:3445` (the γ/ω exits under `_blob_wire`): this is genuinely necessary machinery for a
  pattern that DOES own registry slots (ARBNO cell / capture SAVE / FENCE1 watermark) needing to
  survive their own interior's jmp-entry crossings "and be PER-ACTIVATION under recursion" (comment,
  verbatim) — i.e., it exists to make backtracking into a *complex* deferred pattern correct. It is
  not itself a bug; applying it unconditionally to leaf patterns that need none of that is.

## WHY NO QUICK PATCH EXISTS (three tried, three rejected — recorded so nobody re-walks them)

1. **Raise `zd_k()`'s IR_MATCH_DEFER budget from 16 to some larger constant, and pad every OTHER
   path (literal, GVA-direct) to consume the same amount.** Rejected: `blob_frame_bytes()` is
   `blob_head_bytes() + 16*count + …`, and `count` (ARBNO/capture/FENCE1 registrations inside the
   *dynamically bound* pattern) is unbounded — a sufficiently complex runtime-constructed pattern
   can need arbitrarily more than any fixed ceiling. There is no worst case to pad to.
2. **Zero out `blob_frame_bytes()`'s `count==0` branch so leaf patterns skip the framed exit.**
   Tried by hand-tracing the resulting "FRAMELESS" arm (`emit.cpp:3422`'s second `IF`, `_bfb<=0`):
   it *also* doesn't collapse to 16 bytes — it does an unconditional `sub rsp,8` plus 3 pushes
   (32 bytes net), because that path is shared with the Icon-generator-suspend convention, which
   has its own fixed shape unrelated to `bb_match_defer.cpp`'s specific 16-byte budget. Still 32
   bytes over budget, and now the fix requires *also* touching a path shared with an unrelated
   consumer (Icon suspend/resume) to shave the remaining 32 — a strictly larger, less-isolated
   change than the one being attempted, for a defect this row does not own.
3. **Existing `SCRIP_DEFER_CARVE_RBP=1` flag** (`emit.cpp:2222-2225`, `bb_match_defer.cpp:38,64-70`)
   looked like it might already be exactly this fix, unshipped behind a default-off flag (the
   fleet's own KILLSWITCH-POLARITY witness class). **Tested directly: it segfaults** on this exact
   witness (rc=139) rather than fixing it. Whatever it does today, it is not a working substitute.

The structural reason all three fail the same way: **the extra bytes are not a leak to clean up —
they are the compiled pattern's own backtrack-resume record, which must stay reachable for as long
as a later box in the chain might fail and backtrack into it.** You cannot both (a) shrink the
stack back to a small fixed footprint immediately after a successful DEFER dispatch, for the
*following* boxes' fixed offsets to keep working, and (b) keep that same footprint alive and
findable for a *later* backtrack into the DEFER's box. Any fix that picks (a) unconditionally will
silently break backtracking through a pattern rich enough to need it (this row's own witness is too
simple to exercise that regression, which is exactly how it would ship unnoticed).

## THE FIX THIS ACTUALLY NEEDS (for whoever has the bandwidth + corpus-board time to do it right)

Per RULES.md's own BB FRAME-PLACEMENT CRITERION ("the moment compile-time-unknown stack growth can
intervene between a box's γ departure and β resumption, they move up to a ζ-ACTIVATION-FRAME"): a
`MATCH_DEFER` whose value is not provably a literal at compile time is exactly this case, and the
sound fix is architectural, not a constant tweak: **anything computed before a general (non-
`pat_static`) `MATCH_DEFER` in a statement, and read after it, must stop living on a fixed-offset
zeta-spine slot** — it needs a location the DEFER's internal stack churn cannot shift under it (a
GVA slot, or a stable RBP anchor established before the whole match statement begins and never
touched by any box's own internal `sub rsp`). Concretely this touches: `lower_snobol4.c`'s
"PATV$N" synthetic-temporary creation (the compiler-materialized value carrying `L-1` in our
witness) and `zeta_storage.c`'s slot classifier (which currently has `IR_MATCH_DEFER` in
`zls_locals_shifted()` but only for the *DEFER's own* box, not for shielding what already exists
before it). If routed through GVA, note it must also join whatever save/restore set the DEFINE-call
convention already swaps for formal parameters (`bb_define.cpp`'s SIG shim, `nsave`/`gk4[]`) or a
recursive call will corrupt the outer activation's copy — the reentrancy hazard this row must not
introduce while fixing the wrong-answer one.

## SCOPE (confirms, not just repeats, the original FINDING's belief)

The mechanism is exactly "a MATCH_DEFER resolves to a compiled (non-literal) pattern, and something
after it in the same statement reads a fixed spine offset computed before the DEFER ran" — which is
present verbatim in `ENDING.sno`'s `WORDEND` fragment (`MATCH(3,VOWEL)`, `MATCH(1,NOEND)`, both
non-literal DEFINE-argument patterns immediately followed by more chain). This is now the confirmed
mechanism for LEAVING, not merely the suspected one; DANCING/CURVED were not individually re-traced
this pass but share the identical idiom and almost certainly the identical defect.

## NOT DONE

- No code changed this session (tree confirmed clean, `git status` empty, before writing this up).
- DONE-WHEN on the reopened row is still RED — this finding does not close it.
- The reentrancy interaction between a GVA-routed "PATV$" fix and recursive DEFINE'd-function calls
  was reasoned about but not built or tested — flagged above as a hazard for whoever implements it.
- Whether `blob_frame_bytes()`'s minimum floor (`blob_head_bytes()`, 24/40) is itself removable for
  the true leaf case (no registry slots) without touching the shared Icon-suspend "frameless" exit
  was investigated (§ WHY NO QUICK PATCH EXISTS, item 2) and found to still fall short by 32 bytes,
  not fully ruled impossible with more work — a narrower fix scoped to *only* the leaf/count==0 case
  might still be viable with an isolated exit sequence for that case rather than reusing either
  existing shared arm, but that is new plumbing, not a flip of an existing flag.

Repro/scratch files (not committed): `/tmp/claude-1000/-home-claude19/2b495f88-db94-4833-93c4-be7ce16611b0/scratchpad/{sib_literal,wit_primitive}.{sno,ir,bb,s}`, `wit_primitive_bin`, `dbg*.gdb`.
