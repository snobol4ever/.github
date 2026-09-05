# FINDING — 2026-09-04/05 (seat12, hq_T lane; queue row `snobol4-xfail-class-fuzz-crash-and-hang-corpus-19-entries`)
# THE 9 S183-ONLY FUZZ WITNESSES: ROOT-CAUSED A REAL ARBNO WILD-JUMP DEFECT, BUILT A FIX THAT CURES IT, THEN FALSIFIED THE FIX AGAINST THE FULL SNOBOL4 MASTER BOARD (15 NEW REGRESSIONS) AND REVERTED CLEAN — DISPOSITION: ROOT CAUSE FULLY UNDERSTOOD, CANDIDATE FIX DISPROVEN, NOTHING LANDED

**Tree at measurement:** SCRIP HEAD `039606345` — **confirmed byte-identical after this session** (`git status`/`git diff` clean; see §5). corpus HEAD `1aa7a352eb`. Oracle: `/home/resources/x64/bin/sbl -bf`.

## 0. SCOPE AND WHY THIS FINDING EXISTS DESPITE LANDING NOTHING

Per hq_T's ruling (inbox, this session): DONE-WHEN line 3 (`ALL.xfail` fz_/fuzz grep count) is the row's whole acceptance test; line 4 struck (hq_T: "an artifact of my minting, carries no meaning... I have no objection to you striking it"). Per the prior session's FINDING, the directed next step was the 9 s183-systematic-fuzzer-only witnesses (no s188/s189 lineage, zero prior root-cause work):
`arbno_fence_pos_replace_branch_2`, `arbno_bal_tab_replace_branch_1`, `arbno_arb_rpos_replace_branch_2`, `fence_arb_tab_replace_branch_2`, `arbno_fence_span_replace_branch_1`, `arbno_fence_bal_replace_branch_1`, `arbno_span_break_replace_branch_1`, `arbno_span_tab_replace_branch_1`, `arbno_fence_bal_replace_branch_2`.

This row's own law: "an entry that behaves differently than its reason says is a FINDING, not a failure of this row," and the ASM-DIFF-FIRST/INSTRUMENT-LAWS discipline demands the fix be proven against the **full** corpus board, not the one red witness, before it can land. This sitting did exactly that — found the root cause, built a fix, confirmed it cures the target witness byte-exact, then ran the full board and found the fix breaks 15 *other*, previously-green witnesses. Per this row's own law ("never re-cut a ref to make one green... say so with the oracle's own output beside the claim") and the prior session's own precedent (a falsified fix, reverted clean, is worth more recorded than a landed guess), this is written up in full rather than discarded.

## 1. ABLATION — MINIMAL REPRO

Started from `arbno_arb_rpos_replace_branch_2` (`P = ARBNO(ARBNO((LEN(0) | '+') ARB)); 'aaa' *P RPOS(0)`, SIG11 both modes). Systematic ablation (ASM-DIFF-FIRST) reduced this to a 1-line minimal repro:

```
'a' ARBNO((LEN(0) | 'x') ARB) POS(1)     :S(OK)F(NO)
OK        OUTPUT = 'match'                   :(END)
NO        OUTPUT = 'nomatch'
END
```

19 hand-built variants (full matrix available in this session's scratch, not checked in — none of these are new corpus reductions) pinned down every required ingredient: (1) the outer `ARBNO(ARBNO(...))` nesting is NOT required — a single-level ARBNO suffices; (2) a following anchor (`POS`/`RPOS`) that forces backtracking is required — without one, ARBNO's "try zero reps first" semantics never enter the body; (3) the ARBNO body must be a **sequence of 2+ elements** ending in a generator (`ARB`) — a single-element body never crashes; (4) the element **before** the generator must be able to succeed via a **zero-width (null) match** (`LEN(0)`) — an all-literal alternation never crashes; (5) the null-capable element must be **first** in the body sequence — `ARBNO(ARB (LEN(0)|'x'))` (generator first) never crashes, only `ARBNO((LEN(0)|'x') ARB)` does.

## 2. ROOT CAUSE — CONFIRMED VIA LIVE GDB TRACE, NOT INFERENCE

ARBNO's IR node (`IR_MATCH_ARBNO`) carries `operands[1]` = "the node whose β-port to jump into when the body succeeds with zero net progress" (the null-match guard). This is consumed **directly** by `bb_match_arbno.cpp`'s `je PAIR(1)` (all three live arms — `bb_match_arbno_frame()`, `bb_match_arbno_frameless()`, `bb_match_arbno_frameless_k()` — share this one null-check shape), resolved via a direct `operands[1]`-indexed lookup in `emit.cpp:flat_drive_match_alt` (confirmed by reading that function, and independently confirmed empirically: changing `operands[1]`'s value changes `PAIR(1)`'s resolved jump target one-to-one, nothing more indirect).

For a single-element ARBNO body, `operands[1]` trivially equals that one element — correct by construction. For a body that's a **multi-element sequence**, lowering (`src/lower/lower_snobol4.c`, `TT_ARBNO` case) builds it via `sno_seq_nary`, which already computes the semantically-correct retry target — the sequence's **last** element's own tail — and exposes it through an `out_rtail` output parameter. `TT_ARBNO` discards that value (calls the generic `sno_pat_node` wrapper, passing no `out_rtail`) and instead **re-derives `operands[1]` itself** via a heuristic scan that skips leading synthetic `IR_GOTO` relay nodes and takes whatever comes next. That scan cannot distinguish `sno_seq_nary`'s own internal bookkeeping relay (which, since `TT_ARBNO` calls it with `succ==fail==R`, also targets the ARBNO node) from a genuine body node — after skipping exactly one such relay it lands on the sequence's **first** element (here, the `ALTERNATE` box for `LEN(0)|'x'`) instead of the **last** (`ARB`).

**Live trace (gdb, breakpoints on the box entry addresses, printing rsp/r14d/stack contents at each hit):**
```
ARBNO-ALPHA rsp=0x...dff0 r14d=0        (try zero reps)
ARBNO-BETA  rsp=0x...dff0 r14d=0        (POS(1) failed, ask for a rep)
ALT-ALPHA   rsp=0x...dff0 r14d=0        (enter body fresh: sub rsp,32)
ARB-ALPHA   rsp=0x...dfd0 r14d=0        (LEN(0) succeeded trivially; enter ARB: sub rsp,16)
ALT-BETA    rsp=0x...dfc0 r14d=0  [rsp+8]=(nil) [rsp+16]=0x7fff00000000
SIGSEGV  rip=0x0
```
The null-guard fires on ARB's very first (0-length) try (net progress 0 == "null"), jumps directly into `ALTERNATE`'s β port — **skipping ARB's own 16-byte scratch-frame cleanup** (`add rsp,16`) that ARB's own exhaustion path would normally run first. `ALTERNATE`'s β then reads its remembered continuation pointer from `[rsp+8]` at a stale offset (16 bytes short of where its real frame lives, since ARB's still-open scratch sits between rsp and it) — landing inside ARB's abandoned, partially-uninitialized scratch. Here that reads exactly `NULL`, and the following `jmp rax` faults at address 0.

**Candidate fix (lowering):** when the ARBNO body flattens (via the existing `sno_seq_flatten_pat`) to 2+ elements with no `FENCE` among them — precisely the condition under which the generic dispatch would call `sno_seq_nary` anyway — call it directly and thread its real `out_rtail` through as `operands[1]`, instead of re-deriving a heuristic guess. Falls back to the original scan for every other body shape.

**Result on the target witness: CURED, byte-exact, both modes.** `arbno_arb_rpos_replace_branch_2`: m3 `match` (was SIG11), m4 `match` (was SIG11), oracle `-bf` `match`.

## 3. THE FIX HAS A WIDER BLAST RADIUS THAN THE ONE MECHANISM IT TARGETS — FOUND BY THE FULL BOARD, NOT BY INSPECTION

`operands[1]` is not read only by the null-check wiring. Independently, several arm-selection analyses in `emit.cpp` (the FRAMELESS_K eligibility test `_k16r`/`_kk`/`_sq`; `op_arbno_body_k0`; `op_body_has_arbno`; `op_arbno_body_defer_unsafe`/`op_arbno_body_actframe`; plus two sibling-ARBNO "am I nested inside another ARBNO's body" checks) each scan `g_emit_cfg->all[]` over the index range **`[operands[1], operands[2]]`** to answer "does this ARBNO's body contain an ALTERNATE / nested ARBNO / DEFER / etc." Pre-fix, this worked *by accident*: `operands[1]` happened to equal `operands[0]` (the body's true first node) for exactly the buggy reason in §2, so the range was always the full body span. Correcting `operands[1]` to mean "last element" narrows that same range to `[last-element, last-node]`, blinding these analyses to everything earlier in the body.

Confirmed live (`SCRIP_ARBNO_DIAG=1`) on the minimal repro: pre-emit-fix, the `_k16r` block reported `sq=1` (should be 0 — `ALTERNATE` is in the body and is completely missed) and mis-routed to the "FRAMELESS_K" arm, whose one-level static stack-offset math assumes a body that never disqualifies and silently omits `ALTERNATE`'s real 32-byte frame contribution — producing not a crash but **unbounded repetition / stack growth (`ERROR 246` stack overflow)** once 2+ real repetitions were needed to satisfy a trailing anchor (a second synthetic witness, `'aa' ARBNO((LEN(0)|'x') ARB) POS(2)`, reproduces this cleanly).

**Second candidate fix (emit.cpp):** in the four affected range computations (plus the two sibling-nesting checks), use `operands[0]` instead of `operands[1]` as the range's lower bound — `operands[0]` is always the body's true first node in both the old and new semantics, so this restores the pre-fix-equivalent (correct, wide) scan.

**Combined fix (lowering + emit.cpp), full board (`test_corpus_snobol4.sh`, all 1768 SNOBOL4 master entries, m3+m4): NOT CLEAN.**
```
total=1768 · m3: pass=1689 fail=2 crash=17 xfail=58 xpass=2 · m4: pass=1689 fail=1 crash=17 skip=1 xfail=58 xpass=2
```
17 CRASH lines per mode, **none of them in the xfail set** (all `signal 6` / SIGABRT — the compiler's own `x86_bomb()` refusal, not a wild crash). Confirmed against a clean HEAD worktree build (`git worktree add`, no working-tree risk) that **15 of these 17 are new regressions** — programs that pass cleanly today and only fail with this fix applied:
`arbno_notany_pos_branch_{1,2,5,6}`, `arbno_pos_rpos_branch_{50,51,52,68,97,99}`, `arbno_span_defer_branch_5`, `arbno_fence_notany_branch_{1,3}`, `arbno_span_pos_branch_{9,10,27,28}`.
(The remaining two lines — `simple_output_276` FAIL/SKIP and `user_function_len_defer_branch_6` FAIL — reproduce identically on the unmodified baseline; **pre-existing, unrelated to this fix**, not investigated further here.)

Mechanism: the emit.cpp correction makes MANY more real corpus ARBNO bodies correctly detected as "complex" (containing an ALTERNATE/nested ARBNO/etc — a legitimately common shape) than before. Correctly-detected complexity routes them toward `bb_match_arbno_frame()`, which needs a slot from a **separate, whole-program frame-slot allocator** (`arbno_frame_slot()` → `frame_slot_scan()`, an independent capacity-limited resource-assignment pass this session did not modify or fully map). That allocator declines (`-1`) for these 15 nodes, and `bb_match_arbno()`'s own dispatcher **loudly bombs** rather than silently falling back — which is the right thing for the allocator to do in isolation, but means correcting the k0/kk/sq detection surfaces a **pre-existing, separate capacity/logic gap** in that allocator for a class of program shape it was never exercised against before (because the buggy narrow range was accidentally keeping them off this path).

**Narrower candidate (lowering fix ALONE, emit.cpp reverted): also not safe.** Spot-checking the same 15 names showed 6 of them now pass again (frameless-K is no longer selected differently for them — plausible, not exhaustively re-verified), but `arbno_pos_rpos_branch_51` produces **wrong output, no crash** (`rc=0`, does not match its `.ref`) where the unmodified baseline passes clean. This means the `operands[1]`-as-range-bound overload has at least one more live consumer this sitting did not find (most likely inside the "chain"/K16 machinery's own internal bookkeeping, which this sitting did not fully map) — narrowing the fix's scope trades a crash-class regression for a silent-wrong-answer-class regression on at least one witness, which is worse, not better, per this row's own "never a silent wrong answer" ethos.

## 4. WHY NEITHER FIX LANDED

Both variants were falsified by the full board, which is exactly the gate this row's own law and CLAUDE.md's ARBNO/emit.cpp change discipline require before landing anything here ("this template is on the path of every ARBNO in the corpus, not just these 19"). Landing either would have traded 1 real cure for a double-digit count of new regressions (crash-class for the full fix; at least one silent-wrong-answer-class for the narrower one) — an unambiguously bad trade under "a defect reachable through one member is a class defect, fixed or left visibly red, never hidden," which cuts both ways: it is equally wrong to fix one member of a class by breaking others.

## 5. TREE STATE — CONFIRMED CLEAN

Both files touched this sitting (`src/lower/lower_snobol4.c`, `src/emitter/emit.cpp`) were restored via `git show HEAD:<path> > <path>` (a read-only git operation, not a working-tree-discarding command) after the regression was confirmed, and rebuilt. `git status --short` / `git diff --stat` against HEAD `039606345`: **empty, both files.** The original crash (`SIG11`) was re-confirmed reproducing on the rebuilt binary, verifying the revert is behaviorally exact, not just textually clean. **Nothing from this sitting is committed or pushed.** The temporary `git worktree` used for baseline comparison was removed (`git worktree remove --force`); `git worktree list` shows only the primary worktree.

## 6. FOR THE NEXT SEAT (prioritized)

1. **The real fix needs a genuinely new, dedicated operand slot — not a reinterpretation of `operands[1]`.** `operands[1]` is load-bearing for at least 4 confirmed range-scan consumers in `emit.cpp` plus at least 1 more this sitting didn't locate (the `arbno_pos_rpos_branch_51` wrong-output case). The architecturally sound fix threads the corrected retry-target through a **new** operand (pushed unconditionally, ahead of the existing conditional fence-self-ref operand, shifting it from index 3 to index 4) and updates `bb_match_arbno.cpp`'s three null-check sites to read the new index — leaving `operands[1]`'s existing "body range lower bound" role, and every one of its current consumers, byte-for-byte untouched. This is more invasive on the `emit.cpp:flat_drive_match_alt` side (its per-node pair count `N` is hardcoded to 1 for `IR_MATCH_ARBNO`; giving ARBNO a second (e,r) pair reindexes every subsequent `PAIR(k)` in `bb_match_arbno.cpp`'s three live templates, e.g. today's `PAIR(2)`/`PAIR(3)`/`PAIR(5)` would need to become `PAIR(4)`/`PAIR(5)`/`PAIR(7)` or similar) — budget for that renumbering, and re-run the full board before trusting it, not just the 9 target witnesses.
2. **`arbno_pos_rpos_branch_51`'s wrong-output regression under the lowering-fix-alone build is worth root-causing on its own** even independent of this row — it means there's a live consumer of ARBNO's operand semantics this sitting did not map, and it's silent (no crash), which is the more dangerous failure shape.
3. **The frame-slot allocator (`arbno_frame_slot`/`frame_slot_scan`) has a capacity/logic gap** that a correct k0/kk/sq detection will expose for a materially common body shape (ARBNO body containing an ALTERNATE). Whether the right cure is "expand the allocator's capacity" or "give `bb_match_arbno_frameless()` a safe degraded mode instead of bombing when frame_off is unavailable AND the body is provably not the specific null-first-then-generator shape that crashes" is an open design question, not something to guess at without its own dedicated investigation.
4. **The minimal repro in §1 is a clean, standalone reduction** (not checked into the corpus — no `.sno`/`.ref` change made this sitting) that any future attempt should re-verify against first, before re-running the full board.
5. This row's 9-entry target list is unchanged; **zero of the 9 are cured as of this commit** (the one confirmed cure was on the falsified, reverted fix — it does not count until a safe version of the fix lands). DONE-WHEN (line 3) is still RED at population 19.
