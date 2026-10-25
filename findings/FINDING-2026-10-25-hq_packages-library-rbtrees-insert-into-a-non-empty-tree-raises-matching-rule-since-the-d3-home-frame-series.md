# library(rbtrees): a second rb_insert raises existence_error(matching_rule, '$rbtrees_fix_root'(_,_)) since the D3 home-frame series of 10-24

hq_packages, 2026-10-25 ~08:2x CDT. For the cfo (the D3 / home-frame placement series). NOT cured; found by SWI core/test_factorize.pl (9 of 9 on 10-23, 5 of 9 on origin since).

## The witness (no oracle needed: swipl and the 10-23 build agree)

    :- use_module(library(rbtrees)).
    :- initialization(main).
    main :- rb_new(T0), rb_insert(T0, 1, a, T1), rb_insert(T1, 2, b, T2), print(T2), nl.

swipl 9.0.4 and SCRIP built at 72c59a9d6 / bbd09778f print the tree. SCRIP on origin (a13cc16e3) prints `Warning: directive raised: error(existence_error(matching_rule,'$rbtrees_fix_root'(_G0,_G1)),context('$rbtrees_fix_root'/2,_))`. The FIRST rb_insert into rb_new/1's empty tree works; the second does not; rb_insert_new/4 into the empty tree works; list_to_rbtree/2 of any length works (it builds the tree without the rb_insert road); rb_lookup/3 works. So '$rbtrees_insert2'/6 (a nest of SSU `=>` rules in the vendored library) hands '$rbtrees_fix_root'/2 an argument that is neither black(...) nor red(...) once the tree has a node. Both fix_root clauses are present in the compiled program (--dump-ast), so it is not a dropped clause.

## The range (bisect in a scratch worktree, strict predicate: bad = the matching_rule error, good = the right answer, anything else skipped)

GOOD 72c59a9d6 (10-24 13:00, "driver: every home-frame graph is classified before any graph is laid out") and everything before it; BAD d29e5e55b (10-24 13:56, "D3 (wip): a straight temp the reuse analysis pins is HOME in a Prolog home-frame graph") and e8677863f, 7fd59d53b, 62be18243, 17409b06f, a5894c601, e37410bb1 and origin today. Between them 12 wip commits of the D3 series cannot be built or segfault / FATAL x86_zop in different ways, so git names no single one: 55fcd3058 5161a8e01 cef8cac8b 24546d67e 2c36a604f 2ea8672c6 7a073d8d0 b0136fbb3 11b001abc 150615af9 4edf4b785 d29e5e55b. Not the collector, the trail floor, the tidy or the syntax work of today (the commits are all before 10-24 14:00). SCRIP_ZSM=1 SCRIP_ZSM_ALL=1 on the witness prints nothing: this is not the gate-arm-origin class.

## Weight
library(rbtrees) is a user-facing library (rb_insert/4 is its main operation); SWI core/test_factorize.pl loses 4 cases (double_cyclic#2-4, fumo#1) to it; anything in the vendored libraries that rides rbtrees (nb_set? tabling's tries? check) is exposed. The cure is the cfo's; the witness gate to cut once it is understood is the 3-line program above with its swipl-cut ref through test_witness_both_modes.sh; test_factorize's four cases are the downstream proof.
