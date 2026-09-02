# FINDING — the Term path ordered unbound variables by FIRST-ENCOUNTER POSITION, not by the address of
# the variable cell. Every `prolog-term-to-descr-eradication` slice that rewrites a comparison, a sort or
# a canonicaliser onto DESCR cells will silently reorder variables unless it reproduces that, and the
# corpus does NOT catch it: ALL.pl stays byte-identical while `X @< Y` flips.

**seat13 · 2026-09-01 · row `prolog-term-descr-s2-compare-sort-pairs`** (slice s2 of the umbrella;
applies equally to s1–s5, which edit the same `unification.c` converter surface).

**Cured in the slice that found it, not just diagnosed** — SCRIP `17d2eddd`: `rt_pl_atop_cell` is on cells and
byte-identical, umbrella 490 -> 487, SNOBOL4 control arm green (m3 and m4 PASS=1669 FAIL=0). This FINDING exists because the trap is INVISIBLE to the obvious rewrite and to the
obvious test, and four sibling slices are walking toward it right now.

## 0. Answer

`rt_pl_term_compare` ordered two distinct unbound variables with a raw pointer test:

    case TERM_VAR: return (a == b) ? 0 : (a < b ? -1 : 1);

Those are pointers to Terms that `pl_cell_copy_walk` had just MINTED, one per distinct unbound cell,
from `rt_pl_cterm_alloc` — a strict bump allocator (`g_pl_cterm_cur += need`, `src/runtime/rt/rt_arena.c`).
So the pointer test was never about the variable's identity or storage: monotonic bump addresses made
`a < b` mean **"a was encountered before b"**, over the walk of ALL of the first argument and then ALL of
the second. The natural cell-native rewrite —

    case var: return (a == b) ? 0 : (a < b ? -1 : 1);   /* a, b now pl_cell_t * */

— compiles, passes the corpus, and is WRONG: it orders by where the variable cells happen to sit in the
frame, which has no relation to encounter order.

## 1. Why the corpus does not catch it

⚠ STATED AS MEASURED vs INFERRED, because the difference matters here.

**MEASURED — the corpus has no executed var-vs-var ordering coverage at all.** `corpus/tests/prolog/ALL.pl`
holds 26 lines carrying an ordering or collation goal (`grep -nE "@<|@>|@=<|@>=|compare\(|msort\(|sort\(|keysort\("`).
Every one that actually RUNS compares ground terms: atoms at lines 681-701 and 815-818, atom lists through
`msort`/`sort` at 705-723 and 1043, and ground pairs through `keysort` at 1883. The only four that mention two
variables — lines 4, 6, 70 and 72, `foo(X,Y) :- X @>= Y.` and its siblings — are CLAUSE-ONLY entries with no
`main` and no directive, i.e. exactly the driver class the MASTER-PLAN records as the 139 m3 crashes
(`[IBB] FATAL: mode-3 driver: main BB graph not found`, whose named witness is literally `foo(X,Y) :- X @>= Y.`).
They die in the driver and never reach a comparison. So the corpus contains the SHAPE of the coverage and
none of the substance: **zero var-vs-var comparisons are ever executed.**

**MEASURED — the correct rewrite changes nothing.** Byte-identical on three witnesses, both modes, against a
real pre-change binary (stash, rebuild, capture, restore, rebuild, capture): ALL.pl 357 lines, a
compare/sort/pairs witness, and the 10-goal crux witness below. Prolog smoke 5/5 both modes,
`test_gate_pl_coupling` PASS, `test_corpus_prolog_parser` PASS.

**INFERRED, NOT MEASURED — say so out loud:** that the WRONG rewrite (comparing `pl_cell_t *` addresses)
would leave all of that green. I did not build the wrong variant, so I have not watched the corpus fail to
notice it. The inference now rests on something checkable rather than on impression — there is no executed
var-vs-var comparison for it to fail — but it is still an inference. The experiment that would settle it is
one line: replace the `cla == 0` arm of `rt_pl_cell_compare` with `return (a == b) ? 0 : (a < b ? -1 : 1);`,
rebuild, and re-run ALL.pl plus the crux witness. Predicted: ALL.pl identical, crux witness flips.

The defect surfaces only on goals like `X @< Y`, `f(X,Y) @< f(Y,X)`, `compare(O, k(P,Q), k(Q,P))`, or an
`msort` of a list containing free variables — none of which the corpus exercises today.

## 2. The witness

`w_vord.pl` (10 goals, all of them flip if encounter order is lost) is reproduced at the end of this file.
Its answers are confirmed three ways at 14f384ed: pre-change SCRIP, post-change SCRIP, and SWI-Prolog
(`/usr/bin/swipl`) all agree line for line, both modes. SWI agreeing matters — it shows first-encounter
order is not a SCRIP quirk to be preserved grudgingly but the ISO-conformant reading: in every case the
FIRST-MENTIONED variable is the smaller one.

## 3. The shape that is correct

Record the encounter position explicitly and compare positions, never addresses. In s2 that is `pl_vord_t`
(`src/runtime/unification.c`): a stack-resident 256-entry map, walked over a then b before the comparison
begins, handing out increasing indices on first sight of each distinct unbound cell. It rides the spine,
allocates nothing, and adds no global — the pre-walk costs exactly the traversal `pl_cell_copy_walk`
was already doing, minus the allocation.

⛔ Two degenerate behaviours of the old path are deliberately NOT reproduced, and any slice inheriting this
shape should make the same call knowingly: (1) past 256 distinct variables in ONE comparison the old code
stopped memoising and minted a fresh Term per later occurrence, so a variable stopped comparing equal to
ITSELF; (2) an unrecognised DESCR tag fell through to `term_new_var(-1)`, a distinct fresh variable per
occurrence, so two reads of the same opaque cell compared unequal. Both are defects, neither is reachable
from the corpus, and preserving them bug-for-bug would be preserving a defect. Raised in the s2 baton QA.

## 4. Chain of custody

- Scope measured at claim: DONE-WHEN failed naming all 17 s2 functions, 65 Term lines, at 14f384ed.
- ⚠ The baton's per-function counts were minted at bcb0ec1e, 80 commits earlier, and have DRIFTED
  (`pb_canon_walk` 2 to 1, `rt_pl_pairs_keys_values_cell` 13 to 10, `resolve_term_compare` 3 to 1). The
  function LIST is unchanged, so the row is still correctly aimed; a slice quoting the counts as current
  state would be quoting a stale measurement.
- Umbrella ratchet: 490 to 487 at this rung.
- ⚠ Unrelated pre-existing crash met while building the witness, NOT filed as new: a collection goal
  (`findall/3`, `bagof/3`, `setof/3`) with any BOUND argument and two or more solutions is rc=139, while
  the same goal with all arguments free is rc=0. That is the already-owned `rt_call_arr_gen` /
  `rt_jmp_frame_lexprep2` resume-cell defect (first-solution-only signature), root-caused by hq_P and
  parked under `prolog-pz4-gamma-retain-activation-frames`; `corpus/tests/prolog/PENDING.md` already
  carries two of its witnesses. Recorded here only because the bound-vs-free discriminator is sharper
  than the text in PENDING.md and may save the cure owner an ablation.

## 5. The witness, verbatim

    :- initialization(main).
    show(L) :- write(L), nl.
    main :-
        ( f(X1,Y1) @< f(Y1,X1) -> show(a_xy_lt_yx) ; show(a_xy_ge_yx) ),
        ( f(Y2,X2) @< f(X2,Y2) -> show(b_yx_lt_xy) ; show(b_yx_ge_xy) ),
        ( g(A,A) @< g(A,B) -> show(c_aa_lt_ab) ; show(c_aa_ge_ab) ),
        ( h(C,d(E)) @< h(E,d(C)) -> show(d_nest_lt) ; show(d_nest_ge) ),
        compare(O1, k(P,Q), k(Q,P)), show(O1),
        compare(O2, P2, f(P2)), show(O2),
        msort([Z,f(Z),a,Z,1], M1), show_len(M1),
        msort([f(V,W), f(W,V), f(V,V)], M2), show_len(M2),
        ( t(R,S,R) @< t(S,R,S) -> show(e_rsr_lt) ; show(e_rsr_ge) ),
        ( u(G,H,I) @< u(I,H,G) -> show(f_ghi_lt) ; show(f_ghi_ge) ).
    show_len(L) :- length(L,N), write(len(N)), nl.

Expected (SCRIP both modes, and SWI-Prolog):
`a_xy_lt_yx` `b_yx_lt_xy` `c_aa_lt_ab` `d_nest_lt` `<` `<` `len(5)` `len(3)` `e_rsr_lt` `f_ghi_lt`
