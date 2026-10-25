# A cut inside a resumed continuation tidies the trail across the park gap -- the pl_floor fence refuses a SUCCESSFUL continuation

hq_packages, 2026-10-25, ceo CEO-1959/1964. For the cto (ARCH-PROLOG-CONTINUATIONS.md § divergence line, the trail rule of ARCH-PROLOG-RTX). NOT cured: the cure is in the shared emitted tidy or in the park-gap design.

## The witness
SWI core/test_continuation.pl `continuation:ifthen#1` is the last graded red of that file (9 of 10 in both modes; the other 42 cases are EXCLUDED SCRIP_EXCEEDS_ORACLE):

    shift_in_cond(R) :- ( shift(hello(X)) -> format(atom(R), 'Hello ~w', [X]) ; true ).
    reset_in_cond(R) :- reset(shift_in_cond(R), hello(X), Cont), X = world, call(Cont).

swipl answers R = 'Hello world'; SCRIP raises `permission_error(backtrack, continuation, done)`. The minimal form, no binding, no format:

    a2(R) :- once(shift(hello(_))), R = after.
    main  :- reset(a2(R), hello(_), Cont), call(Cont), print(R), nl.     % swipl: after; SCRIP: the permission_error

It fails for every cut that is LOCAL to the shifted goal -- once/1, the condition of ->, a disjunction's inner cut (`( shift(h), ! ; true )`) -- and passes when the cut is the clause-level `!` after the shift (`p :- shift(h), !, q.`), and when there is no cut (`p :- shift(h), q.`). The error says "backtrack" but nothing backtracks: the continuation SUCCEEDS.

## The measurement (gdb, rt_plco_park / rt_plco_resume, SCRIP 367370215, -O0)

    PARK   kind=2 (shift)  *tr=...e0  floor=...a0  base=...a0
    RESUME cmd=1           *tr=...160                 (the MAIN side grew the shared trail e0 -> 160 while the coroutine was parked)
    PARK   kind=2 (done)   *tr=...120  floor=...160   -> rt_plco_park: *tr < pl_floor -> returns -1 -> permission_error

rt_plco_resume sets pl_floor = the trail top at the resume; the next park refuses when the top has fallen below it (rt.c, rt_plco_park). Between the two parks the only thing that lowers r12 without a backtrack is x86_pl_tr_tidy (x86_asm.h), which every commit/cut emits: "above the mark of r13, the choice this commit leaves, every entry the trail test would not record under r13 is dropped". The cut of once/-> returns r13 to the barrier saved at the construct's entry, BEFORE the park, whose mark (a0) is below the park gap; the walk therefore compacts the gap [e0,160), which holds the main side's entries, judged against the COROUTINE's barrier (its HB), not the main's. A main-side variable newer than the coroutine barrier's HB but older than a main choice point made after the park is a variable the main side must still undo, and the tidy drops its entry. So the fence is right to refuse a continuation whose tidy crossed the gap (the divergence line says "cuts across its shift and then fails"); it is wrong in saying so only for failure -- it fires for success too, and no wrong answer is yet shown without it, only a possible one.

## Options (the cto's to choose)
1. The tidy stops at the resume floor: start the walk at max(mark of r13, pl_floor of the running coroutine). Costs a load and a compare in every tidy with r13 != 0 -- a template change to the shared hot path (every Prolog .s changes; the identity proof is by outcome, not bytes).
2. A fence entry: at resume the coroutine side pushes a pad-bearing (PL_TR_PAD_KEEP) entry and the walk, on meeting one, keeps everything below it. Needs the walk to start AT the fence or skip the gap by a jump word in the fence, otherwise it examines the gap first.
3. A per-coroutine trail (as engines have, rt_pl_tr_new_arena) for reset/shift: the gap vanishes, the time-ordered undo the doc wants ("a reset goal that binds a variable of the caller and fails back into a caller choice point must see the binding undone") needs a splice at the switch instead.
4. Relax the fence only (accept the tidy), which trades the refusal for the possible unsoundness above. I recommend against it.

Measured cost of leaving it: ONE graded case of the SWI suite (ifthen#1); any real program that cuts inside a shifted goal (tabling's delimited control uses shift/reset through call/1) is exposed to the same refusal.
