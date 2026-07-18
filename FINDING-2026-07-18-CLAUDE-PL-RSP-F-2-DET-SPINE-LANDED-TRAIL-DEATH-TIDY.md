# FINDING 2026-07-18 — RSP-F-2 LANDED: DET preds join the rsp spine; the trail death-tidy; guard-complementarity widening; the crypt/deriv regime tradeoff banked

Session s97 (Claude Fable 5). SCRIP `d52fdaac`, corpus `8d2fb9db` (hashes are POST-REBASE onto the parallel
ICN-MOVE-LABEL-ERAD slice `2b774ff5`, which retired IR_INDIRECT_GOTO globally but preserved the 0-op
Prolog-gate DISJUNCTION — the rebased combination re-ran green: rung 138/138 x3 + all three det reproducers;
that session also measured Raku 288/288 and Icon 243/15 in ITS container, reinforcing that this container's
raku-63/icon-244 numbers are environmental). Follows RSP-F-1 (`16064867`).

## 1. What landed — the whole rung is a LOWER-side regime flip

RSP-F-2's spec said "emit rsp-carved frames for classified-DET jmp_entry procs, direct call, bypass the
trampoline; its consumers are exactly the marks RSP-F-1 writes." The realization required **zero emitter,
template, or emit-regime changes**: a classified-DET pred IS a plain procedure, so `lower_pl_register_all_preds`
now lowers it with `suspend_deliver=0` (the MOVE_LABEL delivery main/0 has always used) and registers
`is_generator=0`. Everything downstream follows from the two existing markers:

- `emit_jmp_entry_for_proc` arms `flat_gen=0` → the det epilogue (full LIFO rsp unwind, no retaining
  suspend record) — exactly the Icon/Raku det proc regime, proven machinery.
- `bb_call_proc_staged_str` dispatches on `rt_proc_is_generator` → `bcps_det_arm`'s jmp-entry wire:
  no once-flag, no retention, β routes to the fail continuation (verified in emitted .s — the redo of a
  det call fails without re-entering the callee; the callee is never re-executed on redo).
- The runtime record (`jmp_entry=1, is_generator=0`) routes value/computed calls through
  `rt_proc_call_gen_h`'s det one-shot arm.

`pl_det_compute()` (the RSP-F-1 fixpoint, split out of `pl_det_classify_all`) now runs BEFORE registration;
the marking/report pass is unchanged. `SCRIP_PL_DET=0` is an emergency-only escape (the `SCRIP_OPT=0`
shape) forcing every pred back to the suspend/gen regime for bug isolation.

## 2. The land mine stepped on and defused: trail entries outlive rsp frames

First fail-loop run died `*** stack smashing detected ***` in `rt_call_arr` under `$trail_unwind`
(gdb bracket). Mechanism, pinned not guessed: the value trail records `{addr, old}` unconditionally; a det
callee's frame cells are bound and trailed during its run; the det exit fully unwinds the rsp frame; a later
unwind to an older mark then RESTORES through those addresses into whatever reoccupies the memory — reused C
helper frames (the measured canary smash) or, worse, a live later activation carved over the same region
(silent corruption). **Unwind-time filtering is unsound against that reuse-aliasing** — a stale entry can
alias a LIVE re-carved frame and the filter cannot tell. The only sound moment is FRAME DEATH:

- `rt_pcall_t.vtmark` records the value-trail top at `rt_proc_call_open` (both prologues).
- `rt_proc_call_epilogue_γ/ω` compact the segment pushed since, dropping entries whose address lies in the
  just-vacated stack window: floor = the tidy leaf's own C frame (deepest live stack byte; the (floor,upper)
  span is inside the stack VMA so no heap cell can alias it), upper = the landing rsp
  (`__builtin_frame_address(0)+16` in the epilogue). Entries at/above upper are the caller's live cells
  (head-unification bindings backtracking must later undo) — kept, order preserved (same-address restore
  pairs are either both dead or both kept, so value-restore commutation is untouched).
- **Generator first deliveries land on the same epilogue (ONE-POP law) with their activation RETAINED and
  its cells LIVE below the landing** — `!c.p->is_generator` gates them out. Behavioral condition, no
  language identity; a program that never pushes the value trail gets a zero-iteration walk.

New leaves `rt_value_trail_mark` / `rt_value_trail_tidy_dead_below` live beside `g_pl_trail` in
`resolution.c`. Measured NOT to be a hot cost (crypt identical iters with the walk disabled during triage).

## 3. Guard-complementarity widening (the tak class)

`pl_det_pred_ok` gains: 2 clauses, all-distinct bare-var heads with identical positional slot vectors (head
unification always succeeds, selects nothing), first body goals the SAME-args arithmetic comparison under a
complementary operator pair ({>,=<} {<,>=} {=:=,=\=}) — at most one guard can succeed (both throw or both
fail on non-evaluable args, still ≤1 solution), so clause selection is determinate without a cut. Bodies
still pass the default-deny goal test, whose allowlist gains `=`/2 (≤1 solution by definition; it was the
blocker — tak's `Z = A` parses as `TT_FNC "="`), `==`, `\==`, and the `@`-compares. tak/4 now classifies
DET; qsort/nrev remain correctly det=0 (first-arg indexing class = SPEED-5, quantified follow-up).

## 4. Measured (30 s window, iterations completed, vanroy m3, stash A/B pristine vs landed)

| bench    | pristine                  | landed                          |
|----------|---------------------------|---------------------------------|
| fib      | SIGSEGV at iteration 0    | 32 iters, clean, correct 10946  |
| tak      | SIGSEGV at iteration 0    | 5 iters, clean, correct 7, default 8 MB stack |
| qsort    | 741 iters in 30 s (crawl) | 741 iters in 4.9 s (~6×), then SIGSEGV (accrual wall, same 741 boundary as pristine's crawl-stall) |
| queens_8 | 1111 iters, SIGSEGV 9.9 s | 1134 iters, SIGSEGV 5.5 s       |
| deriv    | 8160 iters, island abort  | 8004 iters, island abort, ~2× slower per iter ⚠ |
| crypt    | 130 iters / 30 s          | 65 iters / 30 s ⚠               |

Gate items: fib emitted .s has ZERO `rt_proc_call_gen_h` and zero spine-resume machinery; fib/tak run at
the DEFAULT 8 MB stack in both modes (m4 fib assembled+linked+ran: 10946). meta_qsort still SIGSEGVs — its
cause is NOT the retired C-frame/retention-on-det disease but the NONDET retained-frame accrual (`->`/`;`
bodies keep it correctly NONDET; pristine A/B: identical segv) — that is banked defect (c) of s95, owned by
the nondet reclamation story, not this rung.

## 5. ⚠ BANKED: the det-vs-gen regime tradeoff on search-heavy benches (crypt ½×, deriv ~½×)

Bracketed to the regime, not the instruction: `SCRIP_PL_DET=0` restores crypt to exactly pristine's 130
iters; the tidy walk is exonerated (disabled → still 65); the det call site's β provably does not re-execute
the callee; crypt's det set (sum/3, sum/4) is IDENTICAL to the s96 marking-only report, so the widening is
not implicated. Sum sits under crypt's heaviest redo traffic. Candidate mechanisms for the next hunt, in
order: (a) trail-shape difference — gen-regime redo ran the callee's clause-redo `$trail_unwind` promptly,
det-regime redo=ω leaves caller-visible bindings on the trail until an OLDER mark unwinds, changing
unwind-segment sizes and `pl_area_grow` realloc traffic; (b) MOVE_LABEL delivery's per-delivery slot writes
vs the retaining epilogue; (c) cache effects of carve/uncarve vs retain. The monitor + the two-step gdb spin
counter on sum's call site is the mechanical route. Do NOT chase by reading code.

## 6. Also proven this session

- Icon 244/14/32 pristine-identical (stash A/B; the s96 cursor's 243/15 is a different container's flake —
  same delta measured on pristine here).
- Raku full suite: 63 failures on BOTH pristine and landed (stash A/B identical) — pre-existing on this
  clone/environment, needs its own look; s93's 288/288 does not reproduce from fresh clone today.
- SNOBOL4 smoke 7/7; prolog smoke 5/5 ×2; `test_gate_pl_no_new_global` floor 14; rung 138/138 ×3 at every
  checkpoint (post-flip, post-widening, final).
- The `fib(20)` 4-line reproducer from the s96 cursor is retired; the vanroy fail-loop WS-accrual
  super-linear slowdown (defect (b)) remains and now DOMINATES fib's remaining wall time.

## 7. RSP-F-3 partial: bounded per-iteration table (post-landing, fixed N=1 vs N=3, default 8 MB stack)

Method: per-iter ≈ (t3 − t1)/2 (cancels startup exactly; measures EARLY iterations before the banked
WS-accrual bends the curve — the full auto-ranged rail remains RSP-F-3's deliverable). gprolog invoked
`--consult-file ... --query-goal main,halt`; its N=1→3 deltas sit inside consult-floor noise (~10–20 ms),
so GNU per-iter is low-single-digit ms except tak (≈8 ms).

| bench    | GNU/iter | SCRIP m3/iter | reading |
|----------|----------|---------------|---------|
| deriv    | ≈0.5 ms  | sub-ms (t1=t3=9 ms total) | ≈ PARITY with GNU |
| qsort    | ≈1–3 ms  | ≈5.5 ms       | single-digit × |
| nrev     | ≈1–3 ms  | ≈5.5 ms       | single-digit × |
| crypt    | ≈1–4 ms  | ≈82 ms        | ~20–80× |
| fib      | ≈2–5 ms  | ≈218 ms       | ~50–100× (was ∞ — SIGSEGV at iteration 0) |
| tak      | ≈8 ms    | ≈730 ms       | ~90× (was ∞) |
| queens_8 | ≈1–5 ms  | ≈410 ms       | ~100–400× |

Reading: the det flip removed the SIGSEGV wall and the retention; the remaining gap on the
recursion/search-heavy set is the PER-CALL CONSTANT — `rt_arg_stage` ×arity + `rt_proc_call_open`
(strcmp scan + pcall push) + `rt_jmp_frame_lexprep` (whole-frame NULVCL memset) on EVERY det call —
exactly PL-SPEED-1 (O(1) call path) and PL-SPEED-2 (frame-init elision) territory, now unblocked on a
frame regime where both directly apply. deriv/qsort/nrev being at or near parity shows the substrate
itself is sound; fib at 218 ms/iter for ~22 K calls ≈ 10 µs/call of C-leaf overhead is the whole story.
