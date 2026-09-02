# FINDING — first-solution-only: full causal trace on `between/3`, plus a concrete codegen lead for the cure

**seat10 · 2026-09-01 · FLEET-16 · row `prolog-backtracking-yields-first-solution-only` · SCRIP HEAD `2a140b90`**

## What this adds to the existing chain

`FINDING-2026-08-29-hq_P-prolog-generator-resume-cell-lives-inside-lexprep2-cleared-frame-region.md`
established the mechanism via a one-shot manual gdb patch (preserve the resume cell across one clobber →
`1,3` instead of `1`) and named the open question: *"which slots in `[fb, fb+region_bytes)` are live across
a retry."* This FINDING re-derives the failure with an unpatched binary, end to end, with every value
traced (not inferred), and narrows the open question to one gating condition in the emitter.

## Repro (swipl-graded, both harness shapes the row's DONE-WHEN asks for)

```prolog
main :- ( between(1,3,X), write(X), nl, fail ; true ).       % oracle: 1\n2\n3\n  -- scrip m3+m4: 1\n only
main :- findall(X, between(1,3,X), L), write(L), nl.         % oracle: [1,2,3]    -- scrip m3: [1] only
```
Both harness shapes collapse to the same one-solution answer, confirming one shared mechanism, not two.

## Full causal trace (gdb, unpatched HEAD `2a140b90`, `--run`)

Breakpoints on `rt_jmp_frame_lexprep2` and `rt_pl_between_gen`, printing `fb`/`region_bytes` and
`args`/`resume`/`*resume` at every hit, no source or memory edits:
```
LEXPREP2      fb=...9080 region=592                 -- $disj0's own frame prep
LEXPREP2      fb=...8f60 region=224                  -- between$2F3's frame prep, FIRST entry
BETWEEN_GEN   args=...8fb0 nargs=3 resume=...8fe0 *resume=0     -- fresh: allocates plc_between_t, cur:1->2, returns X=1
"1" printed
LEXPREP2      fb=...8f60 region=224                  -- SAME fb AGAIN, on the retry after `fail`
BETWEEN_GEN   args=...8fb0 nargs=3 resume=...8fe0 *resume=0     -- resume cell reads back 0: the wipe won
BETWEEN_GEN   args=...8fb0 nargs=3 resume=...8fe0 *resume=-1    -- a SECOND call, immediately, resume now -1
[exits, rc=0, no further output]
```
The offsets match `hq_P`'s reading exactly (resume cell at fb+128 of the 224-byte region — confirmed
directly against the emitted `.s`: `between_repro.s:63,72` zeros `[rsp+128]` and passes `lea rcx,[rsp+128]`
as `rt_call_arr_gen`'s 4th arg).

**New here: the wipe does not just lose the iterator, it manufactures a phantom second success.**
`rt_pl_between_gen`'s `*resume==0` branch has a fast path for an *already-bound* `X` (line
`by_name_dispatch.c:4661`): if `args[2]` derefs to an in-range integer, it treats the call as already
satisfied and returns success with `*resume=-1`, **without consuming the iterator**. On the wiped retry,
`X` is still bound to `1` (nothing unwound it — the real unwind lives inside the lost `plc_between_t.mark`,
never reached), so this branch fires, silently declares victory a second time, and sets `*resume=-1`. The
very next call then hits `if (*resume==-1) return FAILDESCR` immediately. So the natural (unpatched)
sequence is: real success (prints 1) → wipe → phantom success (reuses stale binding, prints nothing new,
plausibly swallowed by however the box wiring treats a resume that emits no fresh unification) → immediate
hard fail. This is a different, and more precise, story than "loses the resume, stops" — it explains why
retrying even manually-patched runs can misbehave in more than one way depending on exactly when the wipe
lands relative to which branch is live.

## The codegen lead: `pl_zf_resume` is gated by name, and by-name generators are not in the table

Both `between$2F3`'s box (`n3_call_builtin_gen`/`rt_call_arr_gen`) and the SUSPEND-node protection machinery
(`g_pl_zf_pending_cursor` / `rt_pl_zf_resume_set` / `rt_pl_zf_resume_clear`) are emitted from the **same**
template, `src/templates/bb/bb_call_proc_staged.cpp`. That file computes, per call site:
```cpp
int  zf_cont_off  = (g_emit.zframe_graph && _.op_sval) ? zls_g_resume_by_name(_.op_sval) : -1;
bool pl_zf_resume = g_emit.zframe_graph && (zf_cont_off >= 0);
```
and only when `pl_zf_resume` is true does the β (retry) path call `rt_pl_zf_resume_set` (comment on site:
*"PL-FR-4 zframe β: pop triple, set pending resume, re-enter callee α"*) — the exact protected path that
would keep a resume cell alive across `rt_jmp_frame_lexprep2`'s selective restore. The disassembled
`between$2F3_β` path (`between_repro.s:127-128`) goes straight to `n3_call_builtin_gen_β` with **no**
`rt_pl_zf_resume_set` call anywhere on it — consistent with `zls_g_resume_by_name("$between")` returning
`-1` for this call site. Did not chase `zls_g_resume_by_name`'s registry itself (where names get
registered, and whether any by-name generator is ever in it) — that is the concrete next step, not
something to guess at from one call site.

**Not claiming this is the whole fix.** Registering `$between`/`$for`/`$dyn_iter`/etc. into whatever backs
`zls_g_resume_by_name` might be exactly right, or might just move the symptom (the phantom-success branch
above is a second, independent hazard even with a protected resume cell — a stale still-bound `X` at retry
time is itself worth a second look regardless of where `*resume` lives). And this touches a template shared
with `icn_gen_regime()` call sites in the same file — any change here needs Icon control-arm regression, not
just the Prolog corpus, per this row's own DONE-WHEN.

## Second sub-bug (m3 silently drops remaining conjunction goals): NOT reproduced with the shape tried

Tried the obvious shape —
`main :- ( between(1,3,X), write(X), nl, fail ; true ), write(after), nl.` — both m3 and m4 print
`1\nafter\n` identically, no divergence. Whatever witness seat14/seat06 used to observe m3 going fully
silent (rc=0, remaining conjunction dropped) has a different shape than a `;true`-guarded disjunction
followed by a same-clause tail goal. Not chased further this sitting — recording the negative result so the
next attempt doesn't re-try the same shape and can start from a real prior witness file instead of guessing.

## Disposition

Not landing a codegen/runtime change this sitting: the resume-protection lead is concrete but unverified
past one call site, the phantom-success hazard is a second open question, and this template is shared with
Icon. Landing something here without both of those closed is exactly the "witness prints the right sequence
for the wrong reason" trap hq_P already flagged for this row. Wrote a real, runnable (partial) DONE-WHEN
check for the `between/3` sub-case into the baton — the row's DONE-WHEN line had never been made executable
at all before this. `for/3`, `current_stream/1` enum (both need `gprolog`, not `swipl` — see the row's own
oracle-discipline warning), the assertz-user-predicate receipt, and the m3-silent-drop remain open.
