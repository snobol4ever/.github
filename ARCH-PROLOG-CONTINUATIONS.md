# ARCH-PROLOG-CONTINUATIONS — reset/3 and shift/1 as one-shot coroutines (cto, 2026-10-11, DRAFT FOR REVIEW)

Row: `prolog-swi-delimited-continuations-reset-3-and-shift-1-51-swi-cases` (cto, rank 2; 51 SWI cases, `core/test_continuation.pl` 1 of 52). Status: **design out for review** — hq_prolog answered § 3 and § 4, hq_collector § 5 (2026-10-11, folded in below); hq_zetas (§ 6) outstanding, queued behind its CEO-1682 class-one measurement and free to veto at review. Nothing is built.

## 1. What SWI means, and what the corpus asks for

`reset(Goal, Ball, Cont)` calls `Goal`. If `Goal` calls `shift(B)` and `B` unifies with `Ball`, `reset/3` returns with `Cont` a callable term that, when called, resumes `Goal` after the `shift/1`. If `Goal` ends without a shift, `Cont = 0`. `reset/3` is transparent to backtracking: a redo backtracks into the choice points `Goal` left before the shift.

Every use in `test_continuation.pl` is **one-shot**: each continuation is called once, usually as the goal of the next `reset/3` (iterators `init_iterator/next`, `with_list`, `play/2`, transducers, `reset_in_cond`, `call(shift, a)`, `tassert` with an assert after the shift). No case calls one continuation twice, and none backtracks into a `reset/3` after its continuation ran.

## 2. Why a coroutine, and not the frames in place or a copied stack

- **Frames in place** (shift leaves the frames between `reset` and `shift` retained, and a continuation call re-enters them): a continuation is called from a different stack depth than the one it was suspended at (`sum/3` calls `next/3` several frames deeper). A box addresses its ζ-SPINE storage relative to rsp at its planned depth, so a frame re-entered at another depth reads the wrong slots. Making every predicate that might shift rbp-pinned is not decidable at compile time (`shift/1` is reachable through `call/N`).
- **A copied stack segment** (SWI's way, multi-shot): re-installing frames at another address needs every intra-segment pointer relocated — rbp links, `GC_LAY_PTR_FRAME` links, return PCs keyed by site — and every heap term that references a Prolog variable cell inside the segment would dangle. The maps could relocate the first three; nothing finds the fourth.
- **A coroutine** (the reset goal runs on its own stack, the machinery Icon co-expressions already use: a pthread with its own mmap'd stack, `scrip_coexpr_*` in `rt_coexpr.c`): addresses never move, a continuation is a handle to a parked stack, and "called from a different depth" means "resumed by a different activator", which `scrip_coexpr_activate` already supports. The cost is one-shot semantics; a second resume of a spent continuation is a named refusal, never a wrong answer.

## 3. The shape

Prelude predicates (Prolog, compiled with the program) over five runtime leaves:

```
reset(G, B, C)       :- '$co_new'(G, H), '$co_run'(H, go, S, X), '$reset_k'(H, S, X, B, C).
'$reset_k'(H, shift, X, B, C) :- ( B = X, C = '$cont'(H) ; '$reset_redo'(H, B, C) ).
'$reset_k'(H, done, _, _, C)  :- ( C = 0 ; '$reset_redo'(H, _, C) ).
'$reset_k'(_, throw, E, _, _) :- throw(E).
'$reset_redo'(H, B, C) :- '$co_run'(H, retry, S, X), '$reset_k'(H, S, X, B, C).
shift(X)   :- '$co_yield'(shift, X).
'$cont'(H) :- '$co_run'(H, go, S, X), '$cont_k'(H, S, X).
'$cont_k'(_, done, _).
'$cont_k'(H, shift, X) :- shift(X), '$cont'(H).
'$cont_k'(_, throw, E) :- throw(E).
'$co_body'(G) :- catch(( call(G), '$co_yield'(done, 0), fail ; true ), E, '$co_end'(throw, E)), '$co_end'(fail, 0).
```

(The status fail ends the coroutine and makes `'$co_run'/4` fail; `reset/3` and `'$cont'/1` then fail with it.)

The prelude selector pulls the `$`-prefixed helpers (`'$co_body'/1`, `'$reset_k'/5`, `'$reset_redo'/3`, `'$cont'/1`, `'$cont_k'/3`) through `reset` and `shift` with `pl_cv_add`, as `display` and `write_canonical` pull theirs (hq_prolog's review).

- **`reset('$cont'(H), B, C)` re-uses `H`**: the shift inside `H` yields to whoever activated it last, so a continuation resumed by a new `reset/3` needs no new thread. A `reset/3` whose goal is a `'$cont'/1` term takes the `'$co_run'` road on `H` directly (one clause of `reset/3` before the general one). Threads are one per original reset goal, not one per resume: `with_list` and the iterators stay at one coroutine.
- **The redo mark is the yield, not the entry**: the disjunction in `'$reset_k'` takes its choice point after `'$co_run'` returns, so a redo undoes only the outer's bindings since the yield, then `retry` makes `'$co_yield'` fail inside `H` and `H` undoes its own bindings down to its youngest choice. Undoing to the mark at `reset/3`'s entry would also undo the bindings `H` made before its own choice point, which that choice point's alternatives assume.
- **One-shot is enforced**: `H` carries a resume generation; a `'$cont'(H)` or a redo whose generation is stale raises a named error (`permission_error(resume, continuation, ...)`), never a resume.
- **A shift outside any reset** raises `existence_error(reset, ...)` as SWI does (the leaf finds no Prolog activator).

## 4. The register handover (hq_prolog reviewed it 2026-10-11; the answer, re-measured on SCRIP 966109bb9)

One trail, time-ordered: the coroutines alternate strictly, so the r12 island stays a single LIFO stack. What crosses a switch:

- **r12 (the trail top) crosses through `cx->tr`.** The leaving leaf copies its `cx->tr` into a word of the handle `H`; the arriving side's blocked leaf (`'$co_run'` or `'$co_yield'`, returning) copies that word into its own `cx->tr`, and its wrapper reloads r12 from `[rsp + CTX_TR]`, which every ctx wrapper in `rtx_plunify.s` already does. The handle's word, not an island header word.
- **rbx crosses nothing.** Emitted Prolog never names rbx (0 of the 72,766 lines of a compiled witness's `.s`), and RULES.md's *rbx IS SCRATCH* (Lon) has the bump load the frontier into rbx with rbx dead at the end of the sequence: the frontier lives in memory and both sides read the same word. The draft's "the bump frontier rbx hands over" was wrong and is withdrawn.
- **r15 (the ball) is 0 on both sides at every switch.** `'$co_run'` and `'$co_yield'` are entered at a call port, where no ball is in flight; a throw inside `G` is caught by `'$co_body'`'s `catch/3` and crosses as the `(throw, E)` status pair, re-thrown by the prelude on the arriving side. SysV's restore of the callee-saved r15 is therefore the right value, and the island's ball slot (one island, shared) is 0 too.
- **The raising leaves take the ball road that exists.** The stale-resume `permission_error` and the shift-without-reset `existence_error` are raised by a leaf, so the five leaves are `PL_CTX_LEAF_BALL` instances (`CTX_BALL` zeroed before the call, armed from rcx after): no new wrapper, the hot generic `PL_CTX_LEAF` untouched, `rtx_plunify.s` gains five instantiation lines beside hq_runtime's veneer re-landing in the same file.
- **r13, rbp and rsp stay per side; r14 (the standing root) is the creator's on both.** The coroutine starts at r13 = 0 and `PL_U_TRAIL` trails nothing while r13 is 0, so `'$co_body'`'s first act is its barrier choice (the disjunction around `call(G)`): every binding `G` makes is made under a coroutine choice point. Measured at the build, not assumed: a reset goal that binds a variable of the reset caller's frame and then fails back into a caller choice point must see the binding undone in both modes.

hq_prolog measured the generic wrapper reloading only r12 and `CTX_BALL` left unzeroed on that road, and proposed a `PL_CTX_SWITCH_LEAF` reloading r12, rbx and r15 from cx; re-measured, rbx and r15 need no reload and the ball road is `PL_CTX_LEAF_BALL`'s.

## 5. The collector (hq_collector answered 2026-10-11, read against gc_heap.c and rt_coexpr.c on origin 0d608e9cf)

A parked Prolog coroutine's stack holds mapped Prolog frames, parked inside a C ctx leaf (`'$co_yield'` → `scrip_coret` → `sem_wait`).

- **The chain entry is recorded at the park, by the unwinder road.** Today a parked segment is `[park_sp, stack end]` entered at (pc 0, `park_sp`, `park_rbp`), and `gc_chain_find` with pc 0 follows the frame-pointer chain from `park_rbp` to the first registered site. That fails silently on one shape: a frameless rtx leaf between the emitted call and the C function, whose return address the rbp chain skips. So the park records `gc_chain_entry_from_c`'s triple (the first registered site found by CFI) in `scrip_coctx_t` as `park_site_pc`, `park_site_sp`, `park_site_rbp`, beside `park_sp`/`park_rbp`, and the parked segment starts from that record. hq_collector lands that half in `rt_coexpr.c` and `gc_heap.c`, not blocked on this build.
- **The coroutine's first frame returns into a registered start stub** (`rt_plco_start`, with a conts record `rt_plco_start_conts` in the shape of `rt_genp_n2_conts`), so the chain stops there on the sanctioned stop a parked segment may end on; a chain that climbs into the thread-start C frames reads nosite, which the collector refuses once § 13 STEP B lands.
- **r12 is in place before any poll**: the ctx wrapper reloads it before the leaf returns to emitted code (§ 4), and the chain check at a poll reads the frame, not the registers.
- **The handle is not a root and needs none.** Every live context is on `g_co_gc_head` from creation to `scrip_coexpr_destroy`, and each parked context is walked as a segment whatever the heap reaches. `H` in `'$cont'(H)` is a `DT_CO` descriptor whose pointer is the context (ct_alloc'd, outside the heap), which `gc_blk_of` skips: no new visitor.
- **An abandoned continuation is a leak, not a break**: its context stays on the list and every collection walks its frames (a per-collection cost, a thread and a stack mapping). A leak row once the build is on origin, with a loop-of-abandoned-iterators witness; hq_collector offers an end-of-collection hook over the handles if reclamation is wanted.

## 6. The stacks (the part that needs hq_zetas)

`scrip_coexpr_create` snapshots the creator's frame image for Icon. `'$co_new'` must not: the body is a fresh entry of `'$co_body'/1` with `G` as its one argument and no inherited frame. **Question to hq_zetas:** the thread's first entry into emitted code is the sanctioned program-first-style entry the Icon trampoline uses; is a new `scrip_coexpr_create` mode with `frame_bytes = below = 0` and a Prolog entry package (r12 from the header, r13 0, rbx from the frontier) the right road, or is there a better one?

## 7. Order of build (LARGE CHUNKS)

Whole: the five leaves, the prelude, the one-shot guard, the handover, the registered start stub (the collector's park record is hq_collector's half). Small roll-out: the row's witness and `test_continuation.pl` in both modes, smoked under `SCRIP_GC_STRESS=1 SCRIP_GC_CHAIN_CHECK=3`. Then the other reset/3 users in the SWI suite. Verified per landing by the row's DONE-WHEN and `test_feature_reps.sh prolog` over the features the attribute table names for meta-calls and catch.
