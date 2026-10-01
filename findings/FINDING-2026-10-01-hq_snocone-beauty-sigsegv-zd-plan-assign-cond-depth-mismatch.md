# FINDING-2026-10-01-hq_snocone-beauty-sigsegv-zd-plan-assign-cond-depth-mismatch

## Supersedes
FINDING-2026-10-01-hq_snocone-beauty-sigsegv-break-12char-threshold.md. That finding's localization (the quoted-string
alternation `String = *SQ | *DQ` inside `Expr17`) is WRONG -- it was a plausible but unproven guess from the 12-char
threshold alone. This finding root-causes the actual crash site with exact byte-level proof, fully independent of
`String`/`Expr17`/DEFER/alternation: it is a stack-depth miscalculation in `GenTab()` (`corpus/library/Gen.sc`), a
tiny pretty-printer helper with no pattern alternation in its body at all.

## Context
Task `snocone-every-suite-to-100-under-tenet-ceo-1383`. SncDemo 22/23 -- the one red is the Snocone self-host beauty
demo, SIGSEGV rc=139 in both modes, confirmed on the current tree (SCRIP `eeaebd765`, corpus `1587f21e0`) with the
prior finding's exact repro (concatenate `beauty.chain`'s 16 library files + `beauty.sc`, feed it only line 3 of
`beauty.in`).

## The crash site (proven with real ELF symbols, mode 4)
```
0x42e2b7 <RETURN_GenTab+92>:  mov  rcx, qword ptr [rcx+8]   <- SIGSEGV, rcx=0, fault addr 0x8
```
`RETURN_GenTab` is the compiled exit code for `corpus/library/Gen.sc`'s `GenTab(pos)` function -- confirmed by gdb
symbol resolution on a `cc`-linked mode-4 binary, not inferred from stack-offset pattern-matching. Its last five
instructions, decoded against `xa_flat_chain_epilogue_sig_str()` (`src/templates/xa/xa_flat.cpp:422`), are a
byte-exact match of that function's "CLASS-C chain epilogue-gamma, det-arm signature form" template: restore the
parked `rt_g_want_name` ("name request... HQV-12 protocol"), reload the caller's continuation pointer from
`[rsp + kt-24]` (kt=496 here), follow it to `[ptr+8]` (the gamma continuation), release the frame, jump.

## Proof the bug is INSIDE GenTab's body, not at any call site
Breakpointing `GenTab_alpha` (function entry, address 0x42d925) and the crash instruction (0x42e2b7) together, over
the one crashing run:
```
ENTRY rcx=0x459a66 rdx=0x12 ...     CRASH-SITE rcx=0x459a66   <- call #1: PRESERVED, correct, continues fine
ENTRY rcx=0x45a617 rdx=0x21 ...     CRASH-SITE rcx=0          <- call #2: CORRUPTED -> SIGSEGV
```
Call #2 enters with a perfectly valid signature pointer (0x45a617, a real code address) and reaches the shared exit
with that slot reading 0. The call site is not at fault; the corruption happens during GenTab's own execution.
`SCRIP_SIG_DIAG=1` confirms all 13 static call sites of `GenTab` in `beauty.sc` (8 zero-arg, 5 one-arg) are uniformly
"verdict=SIG why=eligible" -- no caller/callee convention mismatch, no DECLINE.

## The exact mechanism: measured RSP delta, not inferred
```
ENTRY rsp=0x7ffff07e7580   CRASH-SITE rsp=0x7ffff07e7390   delta=-496   (correct: matches kt=496 exactly)
ENTRY rsp=0x7ffff07e7380   CRASH-SITE rsp=0x7ffff07e7250   delta=-304   (WRONG: short by exactly 192 bytes)
```
`GenTab`'s body is one statement: `$'$B' = IDENT($'$B') $'$X'; if (~($'$B' = $'$B' ' ' DUPL(' ', pos - SIZE($'$B') -
1))) $'$B' = $'$B' ' ';` -- an assignment used as a pattern-match condition (`IR_MATCH_ASSIGN_COND`), with an
alternative statement that runs only when the assignment's pattern (built on `DUPL`, which fails on a negative
repeat count) fails. In the compiled mode-4 `.s`:
- the "success" chain (`n4173`..`n4192`: IDENT, SIZE, subtract, DUPL, concat, assign) reaches the shared merge point
  `n4197_statement_end_α` at one stack depth;
- the "alternative" chain (`n4193`..`n4196`: the plain `$'$B' = $'$B' ' ';`, far less work) reaches the SAME merge
  point at a shallower depth, because it never performed the success chain's own temp allocations;
- `n4197_statement_end_α` emits exactly ONE fixed `add rsp, 192` for both arms.
192 is precisely the measured shortfall. Whichever call takes the alternative branch (the DUPL-fails case -- i.e.
the longer quoted string, matching the prior finding's 12-char threshold, which changes `pos - SIZE($'$B') - 1`'s
sign) leaves RSP 192 bytes short of where the shared epilogue assumes it is, so `[rsp + kt-24]` -- correct for the
success path -- reads an unrelated stack slot on the alternative path. That slot happened to hold 0 for this input.

## Root cause, localized to one function and one missing case
`src/emitter/emit.cpp`'s `zd_plan()` (~line 2981), the static stack-depth planner that computes every statement's
entry/exit `sub`/`add rsp` amounts ahead of emission, walks a statement's nodes as ONE LINEAR SEQUENCE (`zd = zd + K
- REL` at line 3086) by default. It has exactly one escape hatch for "this sub-range is a mutually-exclusive
alternative, don't fold its depth into the linear sum" -- the `zarm`/"ZD-5B" mechanism (lines 3026-3041), which
walks `IR_MATCH_ALTERNATE`'s own operand pairs and marks their member nodes so they get a separate `arm_zd`
accumulator (line 3085) instead of adding into the shared `zd`. **That mechanism checks `env->op != IR_MATCH_ALTERNATE`
only (line 3029) -- `IR_MATCH_ASSIGN_COND`'s alternative-statement operand is never recognized as an arm**, so its
nodes fall through to the plain sequential accumulation as if they ran IN ADDITION TO the success chain, not INSTEAD
of it.

This is NOT a simple missing-case fix, for one concrete reason already proven the hard way in this exact file:
`ZD-5B` (the only existing precedent for "arm" handling) is **disabled by default today** (`SCRIP_ZD_5B` defaults
to 0; see `Makefile:373`'s comment on `test_gate_zd_a_back_edge_leaves_a_blob_run_and_alternation_arms_stay_unplanned.sh`,
landed by hq_snocone 2026-09-23): admitting an alternation arm into the static plan as a "spine box" was itself found
to double-release or under-release depending on the backtrack path ("unreleased it corrupted the capture after the
alternation, released it double-popped on backtrack"). `IR_MATCH_ALTERNATE`'s actual, shipping solution to
divergent-arm-depth lives elsewhere entirely -- the RUNTIME-DYNAMIC "cell" protocol in
`src/templates/bb/bb_match_alternate.cpp` (`op_alt_cell`, computed by `alt_arm_complex()`), which stores the
beta-target on the stack at gamma-time instead of relying on a single statically-computed offset. `IR_MATCH_ASSIGN_COND`
has no analogous dynamic mechanism today. Extending the already-rejected static `zarm` approach to a second IR op
risks reproducing the same double-release/under-release failure class it was disabled to fix; the durable cure is
most likely an `op_alt_cell`-equivalent for `IR_MATCH_ASSIGN_COND`'s alternative arm, which is new spine engineering,
not a one-line patch.

## Why 16 of 16 other named gaps and the whole corpus don't show this
`IR_MATCH_ASSIGN_COND` with an alternative statement is uncommon, and the two arms differ enough in temp-stack needs
for the miscount to matter even less often; this is the first witness that happens to (a) use the construct, (b) have
a much larger main arm than its alternative, and (c) immediately follow with a det-arm/signature call whose exit
epilogue reads a FIXED stack offset -- the combination that turns 192 stray bytes into a NULL-pointer jump instead
of silent, harmless slack.

## Diagnostics added this sitting (opt-in, zero default-behavior change, left in place for whoever lands the fix)
- `SCRIP_SIGEPI_DIAG=1` (`src/templates/xa/xa_flat.cpp`, `xa_flat_chain_epilogue_sig_str`): prints `fname`, `is_gamma`,
  `kt`, and the resolved signature shape for every signature-epilogue emission.
- `SCRIP_ALTC_DIAG=1` (`src/emitter/emit.cpp`, `alt_arm_complex`): prints each `IR_MATCH_ALTERNATE` arm's resolved
  node range and whether a complex (DEFER/CALL/nested-alternation/etc.) node was found in it. Not load-bearing for
  this bug (ruled out `String = *SQ | *DQ` definitively), kept because it's a genuinely useful, previously-missing
  instrument for this exact class of question and cost nothing to add.

## Reproduction (unchanged from the prior finding, re-verified on SCRIP `eeaebd765`)
Full chain + `beauty.sc`, fed only `beauty.in` line 3, both modes, rc=139, fault address 0x8. Minimal standalone
isolation (a bare `function GenTab...}` plus one or two calls, outside the full chain) was NOT attempted this sitting
-- given the root cause is now proven at the instruction level in the real repro, a minimal isolation is confirmatory
polish, not required to know what to fix or where.

## Suggested next step for whoever continues this (the spine, cto's row per MODE TENET line 2)
1. Design the `IR_MATCH_ASSIGN_COND` analogue of `op_alt_cell`: the alternative statement's depth must not be folded
   into the main chain's linear `zd` sum, and whatever reads the post-merge "caller signature"/continuation slot at a
   fixed offset must not assume a single depth.
2. Prove it against `test_gate_zd_a_back_edge_leaves_a_blob_run_and_alternation_arms_stay_unplanned.sh` (the
   authoritative zd_plan correctness gate -- extend it with a fifth witness for this shape rather than trusting the
   existing four) plus this finding's exact repro (expect rc=0, correct output, in both modes).
3. SNOBOL4 control arm required (shared `emit.cpp`/`xa_flat.cpp`, CEO's SHARED-NODE VERDICT SCOPE rule) before landing.
