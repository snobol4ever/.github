# FINDING 2026-09-23 hq_prolog: assert/retract-triggered runtime recompilation of a dynamic predicate corrupts its OWN box's next trace CALL/STMT literals — root cause narrowed, not yet fixed

## UPDATE 2026-09-23 later (same day, second sitting): the prior hypothesis is DISPROVEN; root narrowed to runtime JIT recompilation

The original write-up below (first sitting) hypothesized a "ζ-SPINE depth/slot mismatch around the
`$db_erase`/`$db_assertz_r`-family `IR_CALL` nodes," blamed the CALLING clause's own depth bookkeeping, and
required BOTH `retract` and `assertz` present. This sitting's ASM-diff-first work (SCRIP tree `b7b923d1c`,
unchanged this sitting — no code was edited) DISPROVES that shape on four counts, each measured:

1. **`assertz` ALONE reproduces it — `retract` is not required.** `main :- assertz(counter(1)), counter(C),
   write(C), nl.` corrupts identically to the original retract+assertz witness.
2. **`retract` ALONE (when it leaves the predicate re-callable) also reproduces it** on the same shape.
3. **Asserting into a DIFFERENT predicate, then calling an UNRELATED (never-recompiled) predicate, is clean** —
   `main :- assertz(other(1)), counter(C), write(C), nl.` traces `counter/1` correctly. This rules out any
   global/shared table getting corrupted for ALL subsequent calls; only the JUST-RECOMPILED predicate's OWN
   next call is affected.
4. **A plain generator (`between(1,1,_)`) before the same call does NOT reproduce it.** This rules out "any
   choice-point/generator nesting before a staged call" as the shape; the trigger is specifically DYNAMIC
   PREDICATE RECOMPILATION, not backtracking machinery in general.

**The real trigger, isolated to a 3-line repro:**
```prolog
:- dynamic(counter/1).
counter(0).
main :- assertz(counter(1)), counter(C), write(C), nl.
:- initialization(main).
```
`assertz` on `counter/1` triggers a RUNTIME JIT RECOMPILATION of `counter/1`'s own compiled box (every
assert/retract fully recompiles the predicate: `pl_db_store` → `rt_pl_db_recompile` (`unification.c:2297`) →
`pl_runtime_define_pred` → `pl_runtime_define_pred_g` (`lower_prolog.c:1747`), confirmed as the same path
already named by the sibling row `prolog-assertz-beyond-64-clauses-is-invisible-and-each-assertz-recompiles-the-predicate-...`).
The VERY NEXT CALL to that freshly-recompiled predicate, in the same clause body, has its OWN
`__trace_call`/`__trace_stmt` literal arguments corrupted — not the caller's, the CALLEE's, baked into the
box that was JUST re-emitted.

**Direct evidence (gdb, `SCRIP_TRACE=2000000000`, mode-4 standalone binary, breakpoints on `rt_trace_call` /
`rt_trace_stmt`):**
```
=== rt_trace_call name=main/0 (ptr=0x405a61) nargs=0 ...     <- correct: static .rodata address
--- rt_trace_stmt line=3 ... (x4, all correct)
=== rt_trace_call name= (ptr=0x7ffffffed990) nargs=0 ...     <- CORRUPT: this is a STACK address, not rodata
--- rt_trace_stmt line=1 ...                                  <- CORRUPT: L1 (or L209, or other garbage — varies run to run)
```
The corrupted `name` pointer is a live STACK address, not the static string address `counter/1`'s own literal
should carry — i.e. this is reading an uninitialized or stale stack slot, not a bad string, and the actual
value is non-deterministic across runs (`L209` first sitting, `L1` this sitting), consistent with reading
whatever happened to be on the stack rather than a fixed wrong-but-repeatable offset.

**What was ruled out this sitting, with the exoneration named:**
- **The `CALL_PROC_STAGED` emission template itself (`bb_call_proc_staged.cpp`, `n*_call_proc_staged` in the
  `.s`)**: byte-structurally identical between the working (`probe_direct.pl`, no assert/retract) and broken
  (`probe_after_assert.pl`) compiles — same `rt_arg_stage` / `g_call_args` / `rt_proc_call_open_det` /
  `rt_gen_spine_pass_γ/ω` / `rt_pl_exist_key_raise` sequence, same landing-word push/jmp shape (the CFO-36 /
  CEO-483 non-generator padding comment is present verbatim in both, unchanged). Per ASM-DIFF-FIRST, an
  instruction sequence identical across both is exonerated — this template is not the defect.
- **Generator-flag mismatch between static and runtime-recompiled registration**: `lower_prolog.c:1635`
  (static/load-time path) and `lower_prolog.c:1773` (`pl_runtime_define_pred_g`, runtime-recompile path) BOTH
  unconditionally set `rt_proc_set_generator(key, 1)` — every Prolog predicate is always registered as a
  generator, both before and after any recompilation. No mismatch here; ruled out.
- **`bb_pool_init()` resetting shared JIT scratch memory**: read in full (`src/ir/bb_pool.c`). It is a
  lazily-initialized, idempotent, monotonic bump allocator (`if (pool_base) return;` guards re-init as a
  no-op); calling it again from `pl_runtime_define_pred_g` does not rewind or clobber `pool_top`. Ruled out.
- **`bb_pool_mark`/`bb_pool_release` rollback clobbering a live box**: Prolog's recompile path
  (`pl_runtime_define_pred_g`) does not call either — only `runtime_eval.c` (SNOBOL4's EVAL path) does. Ruled
  out as this call's own cause, though it confirms `bb_pool.c` (`src/ir/`) is genuinely shared cross-language
  JIT-emission infrastructure, which bears on where a fix would need to land.

## WORKING HYPOTHESIS, NOT YET PROVEN, NOT YET ATTEMPTED AS A CURE

`pl_runtime_define_pred_g` re-emits the predicate's box via the same `emit_chain(...)` machinery used at load
time, into the shared `bb_pool` (`src/ir/bb_pool.c`), through a path a STATICALLY-compiled box never takes
(load-time compilation for `--compile`/mode-4 writes `.s` text with `.rodata`; load-time mode-3 and ALL
runtime recompilation write directly into the JIT pool). The freshly-recompiled box's OWN `__trace_call`
literal write (the box's own `n34_lit_string`-shaped node, per the working box's disassembly) is either (a)
never executed for the recompiled box specifically, or (b) executed but the box's OWN later read of it lands
on the wrong frame offset — in either case the trace hook ends up reading a live stack slot instead of the
literal it should have just written moments earlier, in the code generated for THIS SAME (re)compilation. The
precise defective line is NOT yet identified: candidates not yet individually eliminated are (1) something in
`pl_runtime_define_pred_g`'s own state save/restore around `emit_chain` (`g_frame_active`, `g_rt_fragment_emit`,
`g_gen_proc_active`, `g_flat_frame_floor` — all saved/restored around the call, not yet each verified correct
for THIS call shape specifically), (2) `zls_forget_graph_nodes` (`src/ir/frame_layout.c:818`, shared — also
called from SNOBOL4's `runtime_eval.c:221`) mis-scoping which frame-map entries survive a recompile, and (3)
something specific to how a JIT-emitted (not statically-assembled) box addresses its own literal pool. None of
these three has been isolated with a targeted probe; this is a list of what's left to check, not a diagnosis.

**Why this was not attempted as a cure**: two of the three plausible locations (`bb_pool.c`,
`frame_layout.c`) are `src/ir/` shared machinery used by SNOBOL4's own runtime EVAL/CODE path, not
Prolog-exclusive files — CLAUDE.md's shared-node rule ("a shared box ... is an ASK to your officer with the
measurement, base-vs-head gate by gate — never a landing") applies once the defect is confirmed to live there.
`pl_runtime_define_pred_g` itself (`lower_prolog.c`, Prolog-owned) is still a live candidate and would be a
landable Prolog-lane fix if the defect turns out to be there — that is the next thing to isolate, before
touching anything in `src/ir/`.

## REPRO FILES THIS SITTING (scratchpad, not corpus)

`/tmp/claude-*/scratchpad/prolog_bug/probe_direct.pl` (correct, no assert/retract), `probe_after_assert.pl`
(original retract+assertz repro, corrupt), `probe_assertz_only.pl` (assertz alone, corrupt — the new minimal
repro), `probe_retract_only.pl` (retract alone leaving the predicate empty — corrupt differently, goal fails,
not directly comparable), `probe_between.pl` (generator, no recompilation — clean, rules out generator
nesting), `probe_other_assert.pl` (assert into an unrelated predicate — clean, rules out global corruption).
Mint as corpus witnesses only once a cure is in hand.

## STATUS

Open, escalated. Not attempted as a cure — ASM-DIFF-FIRST exonerated the one template most naturally suspected
(`CALL_PROC_STAGED`) and the remaining candidates cross into `src/ir/` shared JIT/frame-map machinery also
used by SNOBOL4, which needs an ASK before a landing per CLAUDE.md's shared-node rule. Sent to `ceo` this
sitting (topic `ask-prolog-assertz-retract-recompile-corrupts-own-trace-literal`) with this measurement.
Folded into `## NEXT` on the owning baton
(`prolog-monitor-the-instrumented-gprolog-oracle-is-completed-and-used-...`) in the same landing as this
FINDING update.

---

## ORIGINAL WRITE-UP, FIRST SITTING (2026-09-23 earlier) — SUPERSEDED BY THE UPDATE ABOVE, KEPT FOR RECORD

Found via the IPC sync-step monitor (row
`prolog-monitor-the-instrumented-gprolog-oracle-is-completed-and-used-...`), witness
`scripts/monitor/witnesses/sync_step_prolog_4.pl` DIVERGE at step 35 — but the corruption is **not** a
monitor/oracle contract artifact. It reproduces in plain `--trace` mode with no monitor involved at all, on a
4-line witness with no oracle in the loop:

```prolog
:- dynamic(counter/1).
counter(0).
bump :- retract(counter(N)), M is N + 1, assertz(counter(M)).
main :- retract(counter(N)), M is N+1, assertz(counter(M)), counter(C), write(C), nl.
:- initialization(main).
```

The working hypothesis at the time was a ζ-SPINE depth/slot mismatch around the `$db_erase`/`$db_assertz_r`
`IR_CALL` nodes, requiring both retract and assertz present. **This sitting's evidence (above) disproves the
"requires both" and "caller-depth" parts of that hypothesis** — the trigger is simpler (either builtin alone,
when it recompiles the predicate) and the corruption is in the CALLEE's own re-emitted box, not the caller's
depth bookkeeping. The repro, ruled-out list and hypothesis above supersede this section; kept only so a later
reader can see what changed and why.
