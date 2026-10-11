# ARCH-PROLOG-CONTINUATIONS — reset/3 and shift/1 as one-shot coroutines (cto, 2026-10-11, DRAFT FOR REVIEW)

Row: `prolog-swi-delimited-continuations-reset-3-and-shift-1-51-swi-cases` (cto, rank 2; 51 SWI cases, `core/test_continuation.pl` 1 of 52). Status: **design out for review** — hq_zetas (stacks), hq_collector (the collector), hq_prolog (the Prolog runtime and prelude). Nothing is built.

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

- **`reset('$cont'(H), B, C)` re-uses `H`**: the shift inside `H` yields to whoever activated it last, so a continuation resumed by a new `reset/3` needs no new thread. A `reset/3` whose goal is a `'$cont'/1` term takes the `'$co_run'` road on `H` directly (one clause of `reset/3` before the general one). Threads are one per original reset goal, not one per resume: `with_list` and the iterators stay at one coroutine.
- **The redo mark is the yield, not the entry**: the disjunction in `'$reset_k'` takes its choice point after `'$co_run'` returns, so a redo undoes only the outer's bindings since the yield, then `retry` makes `'$co_yield'` fail inside `H` and `H` undoes its own bindings down to its youngest choice. Undoing to the mark at `reset/3`'s entry would also undo the bindings `H` made before its own choice point, which that choice point's alternatives assume.
- **One-shot is enforced**: `H` carries a resume generation; a `'$cont'(H)` or a redo whose generation is stale raises a named error (`permission_error(resume, continuation, ...)`), never a resume.
- **A shift outside any reset** raises `existence_error(reset, ...)` as SWI does (the leaf finds no Prolog activator).

## 4. The register handover (the part that needs hq_zetas and hq_prolog)

One trail, time-ordered: the coroutines alternate strictly, so the r12 island stays a single LIFO stack. At every switch the leaf syncs the leaving side's r12 into the island header (`x86_pl_tr_top_sync`'s word) and the arriving side reloads r12 from it; the bump frontier `rbx` and the ball `r15` hand over the same way; r13 (the youngest choice), rbp and rsp stay per side. The five leaves are ctx leaves (`pl_tr_ctx_t`: tr, b, ball, rbx, r14, r15), so the handover is the cx write-back the emitted wrapper already does after a ctx leaf returns. **Question to hq_prolog:** is every Prolog register that must cross the switch in `pl_tr_ctx_t`, and does the wrapper reload all of them from cx after the leaf?

## 5. The collector (the part that needs hq_collector)

A parked Prolog coroutine's stack holds mapped Prolog frames, parked inside a C leaf (`'$co_yield'` → `scrip_coret`/`sem_wait`). The collector walks co-expression stacks as segments today (`hb_coexpr_parked`). **Question to hq_collector:** is the chain entry of a coroutine parked in a C ctx leaf the same as the main stack's entry from C (`gc_chain_entry_from_c`, the emitted frame at the leaf's return PC), recorded at the park; and is a `'$cont'(H)` term's handle a root that keeps the parked stack's frames visited (DT_CO in a Prolog compound)? An abandoned continuation (an iterator dropped before it is exhausted) parks a thread forever: a row, not a blocker, unless you say it breaks a collection.

## 6. The stacks (the part that needs hq_zetas)

`scrip_coexpr_create` snapshots the creator's frame image for Icon. `'$co_new'` must not: the body is a fresh entry of `'$co_body'/1` with `G` as its one argument and no inherited frame. **Question to hq_zetas:** the thread's first entry into emitted code is the sanctioned program-first-style entry the Icon trampoline uses; is a new `scrip_coexpr_create` mode with `frame_bytes = below = 0` and a Prolog entry package (r12 from the header, r13 0, rbx from the frontier) the right road, or is there a better one?

## 7. Order of build (LARGE CHUNKS)

Whole: the five leaves, the prelude, the one-shot guard, the handover, the collector entry. Small roll-out: the row's witness and `test_continuation.pl` in both modes, smoked under `SCRIP_GC_STRESS=1 SCRIP_GC_CHAIN_CHECK=3`. Then the other reset/3 users in the SWI suite. Verified per landing by the row's DONE-WHEN and `test_feature_reps.sh prolog` over the features the attribute table names for meta-calls and catch.
