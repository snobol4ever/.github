# FINDING 2026-09-23 hq_prolog: assert/retract-triggered runtime recompilation of a dynamic predicate corrupts its OWN box's next trace CALL/STMT literals — ROOT CAUSE CONFIRMED AND CURED

## UPDATE 2026-09-23 latest (third sitting): ROOT CAUSE CONFIRMED BY GDB, CURED — a dangling-stack-pointer bug in `pl_pred_graph`, Prolog-owned, NOT the shared `src/ir/` candidates

CEO-1208 authorized landing this wherever it fell (permission step retired, CEO-801); the two shared-code
candidates named in the update below (`zls_forget_graph_nodes`, the JIT literal-pool addressing) were BOTH
directly investigated with gdb and BOTH EXONERATED — the real defect is neither, and is entirely inside
Prolog's own `src/lower/lower_prolog.c`.

**GDB EVIDENCE (SCRIP tree at the start of this sitting, `9f5233f70`, 3-line repro
`:- dynamic(counter/1). counter(0). main :- assertz(counter(1)), counter(C), write(C), nl. :- initialization(main).`,
mode-4, breakpoint on `rt_trace_call`, walking the caller frames):** `args[0]` (the DESCR_t staged for
`__trace_call`'s name argument) printed as `{v = 2, slen = 9, s = 0x7ffffffedb30}` — the TAG (`v=2`, a string)
and LENGTH (`slen=9`, exactly `strlen("counter/1")`) are CORRECT, but the DATA POINTER `s` is
`0x7ffffffedb30` — **the EXACT stack address that held the `key` PARAMETER of the earlier
`pl_runtime_define_pred_g(key="counter/1", ...)` call**, confirmed by comparing against that function's own
breakpoint hit moments earlier in the SAME gdb session. By the time the recompiled box executes (on a LATER
call, after `pl_runtime_define_pred_g`'s stack frame has long since been popped and reused by intervening
calls), that address holds whatever garbage the stack currently contains — hence "a live stack address,"
non-deterministic across runs, exactly as originally observed.

**ROOT CAUSE, `src/lower/lower_prolog.c:1691`, inside `pl_pred_graph` (shared by BOTH the offline/static
compile path and the runtime-JIT recompile path):**
```c
const char * trace_key = key;   // BEFORE — a bare alias to the CALLER's string
```
For OFFLINE/static compilation this is harmless: the `.s` emitter dereferences `trace_key` SYNCHRONOUSLY,
copying its bytes into `.rodata` text before `key`'s owning frame is ever popped. For a RUNTIME-JIT-compiled
box (assertz/retract recompilation always goes through this same function via
`pl_runtime_define_pred_g` → `lower_pl_pred_graph` → `pl_pred_graph`), the box instead EMBEDS THE RAW POINTER
VALUE for later use, and "later" means "on a SUBSEQUENT call, after this function has returned and its frame
is gone" — a dangling pointer by construction, not a race, not table staleness, not a frame-layout offset bug.
**This is why my prior static-reading hypotheses about `zls_forget_graph_nodes` and the fc-family tables in
`src/ir/frame_layout.c` were both wrong**: those tables were confirmed via gdb to be entirely EMPTY
(`zf_n=0`, `zx_n=0`) at the point of this process's one-and-only runtime recompile — there was no prior
compile in this process to be stale against. The bug needed no shared-node fix at all.

**CURE, one line, Prolog-owned, no shared code touched:**
```c
const char * trace_key = key ? ct_strdup(key) : NULL;   // AFTER — a durable arena copy (ct_alloc-backed, never freed)
```
`ct_strdup` (`src/ir/ct_arena.c:109`) is the project's sanctioned arena string-duplication helper (already used
two lines later in `pl_runtime_define_pred_g` for the SAME `key` string, for predicate registration) — this is
the correct, already-established idiom for exactly this situation (a string VALUE that must outlive its
caller's frame; CLAUDE.md's "only string values belong on the heap" rule).

**VERIFIED:** the 3-line repro, previously printing `****1 <garbage>()` / `****2 L1` (or `L209`, varying by
run) / `****3 RETURN ( = ''`, now prints `****1 counter/1()` / `****2 L1` / `****3 RETURN counter/1 = ''`
cleanly and DETERMINISTICALLY in BOTH modes (mode-4 `--compile`+assemble+link, and mode-3 `--run`, the latter
additionally showing `main/0`'s own correctly-named call/return around it). `make preflight`: 59/60 arms
green, the one red is the pre-existing, unrelated allocator-eradication gate (cfo's cure row, CEO-1208).

**NOT cured by this fix, confirmed still open and unrelated:** monitor witness 4
(`scripts/monitor/witnesses/sync_step_prolog_4.pl`) still DIVERGEs at step 35 after this cure — but the
DIVERGENCE ITSELF shows no corrupted text at all: `gpx` emits `LABEL stno=INT=12` where `scr` emits
`@12 CALL counter/1`, an EVENT-KIND/sequencing mismatch, not a garbled name. This was never claimed to be the
SAME bug — the original discovery of the trace-literal corruption was via plain `--trace`, independent of the
monitor, and this cure closes that independently-reproducible defect; witness 4's own divergence needs its
own separate investigation, unstarted here. Row `prolog-assertz-beyond-64-clauses-...` (clause invisibility
past 64 asserts, ZLS entry-table overflow under repeated recompiles) was checked and is ALSO NOT reached or
narrowed by this cure — a different defect on the same recompile path, still fully open.

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
