# An if-then-else whose condition binds a fresh variable that the then-branch uses loses the redo of a generator before it

hq_packages, 2026-10-25, ceo CEO-1959. For the cto and the cfo (the placement programme, CEO-1895). NOT cured: the cause is in the planner's discard of the spine at the commit, not in any library. Found by SWI library/test_csv.pl (8 cases, all HANG: csv_read_file_row's driver is exactly this shape).

## The minimal witness (no I/O, no library; SCRIP 67d64782c, swipl 9.0.4 and 10.1.5 agree)

    q1(X) :- X = [a,b].
    r1(L, R) :- between(1, 3, L), ( q1(R0) -> R = R0 ; fail ).
    main :- forall(r1(L, R), (write(L-R), nl)).

swipl: 1-[a,b]  2-[a,b]  3-[a,b].   SCRIP (m3): 1-[a,b]  then  `_G0-[a,b]`  then ends -- L is UNBOUND in the second answer and there is no third.

The IPC monitor trace (monitor_run.sh min2.pl --trace) shows why: after the first answer, the backtrack runs `L3 q1/1() ... RETURN r1/2` (events 11-16), re-entering the if-then-else DIRECTLY; between's second answer is never stored where L lives, and between's third answer is never asked for. The redo reaches the right continuation with the generator's state gone or its output cell elsewhere.

## The class (all measured, m3, m4 equal where graded; SCRIP_OPT=0 changes nothing, so it is the base lowering/emission, not an optimizer pass)

FAILS (L list = [1] where swipl has [1,2,3]): the condition CALLS A USER PREDICATE (or a prelude Prolog predicate: length/2, read_line_to_codes/2, read_line_to_string/2) with a FIRST-OCCURRENCE variable R0, and the then-branch uses R0: `( q(R0) -> R = R0 ; fail )`, `( q(R0) -> R0 = R ; fail )`, `( q(R0) -> R = x(R0) ; fail )`, `( q(R0) -> R0 = R0 ; fail )`, `( q(R0) -> R = R0 ; R = none )`; also with member/2 as the generator instead of between/3.
PASSES: the same with an anonymous variable `( q(_) -> R = a ; fail )`; R0 used AFTER the if-then-else (`( q(R0) -> true ; fail ), R = R0`); no if-then-else (`q(R0), R = R0`); a leaf builtin as the condition (`atom_codes(abc,R0)`, `functor(T,f,2)`); a CALL in the then-branch (`-> length(R0, R)`).
So the trigger is: a retained generator (between/member) + a condition that is a real call + a fresh variable in the condition that crosses into the then-branch. Plausibly the commit's discard (the unmark/cut of the condition's spine) takes the fresh variable's cell with it OR the then-branch's general-unify temporary (`sub rsp, 32` of the rtx_pl_unify leaf) lands on the generator's retained state; the emitted code of the failing and passing siblings (e4/e5 of the probe) is byte-identical up to the then-branch, where the failing one calls the general `rtx_pl_unify` on two variable refs and the passing one inlines unify_const.

## Age and weight
Present in every build I could run: SCRIP b444ca747 and c9a13b8fc (10-21), 642a6c837 and bbd09778f (10-23), 336a29fcd, 02de2f8e8, 01964419b (10-24), and 67d64782c. Not a regression of the 10-24 landings. csv_read_file_row/3 is built on it (library(csv): `between(1, infinite, Line), ( csv_read_row(Stream, Row0, Opts), Row0 \== end_of_file -> Row = Row0 ; !, fail )`), so test_csv's 8 cases hang (each case's findall never ends because the stream is read once and the redo spins); the SAME pattern is a common way to write a loop in user code, so a real program is exposed wherever a generator, an if-then-else on a called predicate and a fresh variable meet.
Not GC: identical with -d2097152k and -s65536k. Not the cut-across-shift divergence of the continuations page (no shift here).

## Next
The owner decides the cure. I have NOT touched the planner, the discard law or the unify leaf. Witness gate to cut once cured: the 4-line program above with its swipl-cut ref through test_witness_both_modes.sh (I will write it the moment an owner names the landing, or the owner takes it), and test_csv's 8 cases are the downstream proof.
