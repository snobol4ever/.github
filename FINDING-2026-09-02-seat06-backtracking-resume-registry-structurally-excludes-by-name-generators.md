# FINDING 2026-09-02 (seat06) — both of seat10's open sub-questions closed by reading, not guessing; the codegen lead needs a re-think, not just a registration fix

Row: `prolog-backtracking-yields-first-solution-only`. Tree: SCRIP `9d086c5ef`. No source changed this
session — root-caused further only, matching this row's own established discipline (hq_P, seat10, seat05
all declined to land a codegen change without closing every open question first; this finding closes two of
them and opens a more precise one).

## Sub-question (a), from seat10's NEXT: "does `zls_g_resume_by_name`'s registry ever contain a by-name
## generator, or is this class structurally never covered" — ANSWER: structurally, categorically never.

`zls_g_resume_by_name` (`src/ir/zeta_storage.c:746`) linear-scans a table (`zg[]`, `zls_graph_t` entries)
whose only writer is `zls_graph_name()` (`zeta_storage.c:54`). Every call site of `zls_graph_name` (grepped
across `src/`, all eight are in `src/driver/scrip.c`) registers a name from `s2->proc_table[_pi2].name` —
i.e. a **user-defined, source-compiled procedure/predicate**, keyed by its own emitted `IR_graph_t*`. A
by-name generator like `"$between"` is never a `proc_table` entry: it is a native C function
(`rt_pl_between_gen`, `by_name_dispatch.c:4692`) reached via a fixed dispatch string inside
`rt_call_arr_gen`, with no `IR_graph_t` of its own to register. There is no code path, past or future-proof,
by which `zls_g_resume_by_name("$between")` could return anything but `-1` **as this registry is currently
designed** — this is not a gap in coverage, it is an exclusion built into what the table is *for* (naming
compiled call graphs, not runtime dispatch strings).

## Sub-question (b), from seat10's NEXT: "`rt_pl_between_gen`'s already-bound-X fast path... needs its own
## fix or guard" — CONFIRMED, exact mechanism, current line numbers.

`by_name_dispatch.c:4695-4704`:
```c
if (*resume == 0) {
    ...
    DESCR_t x = rt_pl_deref_val(args[2]);
    if (!plc_is_unbound(x)) { long long i = 0; if (!plc_int_check(x, &i)) return FAILDESCR;
        if (i >= lo && i <= hi) { ...; *resume = -1; return r; } return FAILDESCR; }
    plc_between_t *it = (plc_between_t *)rt_ws_alloc(sizeof *it);
    it->cur = lo; it->hi = hi; it->mark = pl_trail_mark(&g_pl_trail);
    *resume = (int64_t)(intptr_t)it;
}
```
This fast path exists for a legitimate case (`between(1,3,2)` called with X pre-bound: a deterministic
membership check, no iterator needed) and is correct for it. On the wiped retry this row is about, `*resume`
reads back `0` (indistinguishable from a fresh call) while `X` is *still* bound to the prior solution
(nothing unwound it — the unwind lives inside `it->mark`, and `it` itself is the lost pointer). The fast path
cannot tell "genuine fresh call, caller pre-bound X" from "corrupted retry, X is a leftover" — both look
identical at this check. It fires, phantom-succeeds, sets `*resume=-1`; the next call hard-fails immediately
at line 4705. This matches seat10's trace exactly, confirmed by direct read rather than re-run.

## The more precise question this raises, which neither sub-answer alone poses cleanly

The `zf_cont_off`/`rt_pl_zf_resume_set` apparatus (`bb_call_proc_staged.cpp:690-691` gate, `:814-846` the
retry emission, consumed via `g_pl_zf_pending_cursor` in `rt_jmp_frame_lexprep2`, `rt/rt.c:1698-1721`) is
designed to let a retry **jump back into the callee's own resume continuation** — `zf_cont_off` is an offset
*into a specific compiled callee's emitted code* (that is what `zls_g_resume_by_name` returns: `resume_off`
on a `zls_graph_t`, i.e. a label offset inside *that graph's* machine code). A native by-name generator has
no such continuation to jump back into — `rt_pl_between_gen` is one C function with an internal `switch`-free
loop; its "resume" is entirely the opaque `int64_t *resume` handle, not a machine-code label. **Wiring
by-name generators into this registry, even if a registration site were invented for them, would be pointing
`zf_cont_off` at nothing meaningful** — there is no callee-owned label for it to name. This is a different,
sharper claim than "not yet registered": the apparatus's *design*, not just its current population, assumes
a compiled-graph callee.

Confirmed this isn't moot by checking the gating gets past it: `emit_pl_gamma_retain()`
(`emit.h:545`) reads `getenv("SCRIP_PL_GAMMA_RETAIN")`, default 0 — so the landing-side
`x86_bomb("...PZ-4 clause (c) LANDING...")` at `bb_call_proc_staged.cpp:774` (gated on
`pl_zf_resume && emit_pl_gamma_retain()`) is **not** reached in the default build even if `pl_zf_resume`
became true by some other means; only the pre-existing β/retry branch (`:814-846`, itself "pre-existing
mailbox code, unchanged" per seat05's 2026-08-30 comment on that exact span) would run, and *that* is a
straight call to `rt_pl_zf_resume_set` with `zf_cont_off` — the value with nothing meaningful to point at
for a native generator, per the paragraph above. So even bypassing the bomb doesn't lead anywhere useful
without inventing what `zf_cont_off` should mean for a callee that has no compiled continuation.

## The only existing selective-preservation mechanism is this same apparatus — there is no simpler adjacent hook

`rt_jmp_frame_lexprep2` (`rt/rt.c:1698`) does an unconditional `memset(fb, 0, region_bytes)`, then restores
exactly one thing: `g_pl_zf_pending_cursor` (+ its paired trail-mark), **if and only if** that global is
currently non-null — and the only writer of that global is `rt_pl_zf_resume_set`, called from the same
`pl_zf_resume`-gated branch discussed above. There is no separate, lighter-weight "preserve these specific
bytes across a retry" list to extend for native generators; the one that exists is the compiled-graph
apparatus, end to end. A fix for by-name generators needs either (i) a genuinely new, purpose-built
preservation path (its own global-mailbox-shaped mechanism, populated by `rt_call_arr_gen`'s call sites
directly rather than by a graph-name lookup, since there is no graph), or (ii) something else neither this
nor any prior finding on this row has proposed. Recording this as the fork in the road rather than picking
one — designing (i) means inventing new plumbing in a file already carrying multiple "not landed, deliberately"
scaffolds and shared with Icon; I did not attempt it this sitting.

## Disposition

Not landing a codegen or runtime change this sitting. Both of seat10's open sub-questions are now closed
with direct evidence (not inference), and the codegen lead ("register by-name generators into
`zls_g_resume_by_name`") is now understood to be a **structurally unreachable dead end**, not an unfinished
wiring task — the next real step is designing a new, purpose-built preservation mechanism for native
generators' resume cells, decoupled from the compiled-graph-continuation apparatus, which is a genuine
design task (not a registration fix) and needs its own careful scoping before any code is written, plus
Icon control-arm verification once it is. Leaving that scoping to whoever picks this up next, with this
finding as the reason not to re-chase the registration lead.
