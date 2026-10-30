# FINDING 2026-10-29 (hq_packages, ~21:30 CDT): a retract / re-assert sequence over a ground-fact predicate SIGSEGVs in the code pool; good on 16:29, bad from 18:44

**Reproducer (10 lines, default dialect, no XSB, no library; `kp/3` is not even declared dynamic).** Save as `rep_min.pl`, run `./scrip rep_min.pl < /dev/null`:

```prolog
ins(N,K,V,I) :- ( kp(N,K,V0) -> ( V0 == V -> I = 0 ; I = -1 ) ; assertz(kp(N,K,V)), I = 1 ).
insb(N,K,V,I) :- ( kp(N,K,V0) -> ( V0 == V -> I = 0 ; I = -1 ) ; assertz(kp(N,K,V)), I = 1, ( true ; retract(kp(N,K,V)), fail ) ).
delb(N,K,D) :- ( retract(kp(N,K,V)) -> D = 1, ( true ; assertz(kp(N,K,V)), fail ) ; D = 0 ).
del(N,K,D) :- ( retract(kp(N,K,_)) -> D = 1 ; D = 0 ).
:- ins(s,111,f(a),X), write(X), nl.
:- delb(s,111,X), write(X), nl.
:- ins(s,111,f(_),Y), write(Y), nl.
:- del(s,111,X), write(X), nl.
:- insb(s,aaa,pp,_).
:- ( kp(s,aaa,X) -> writeln(found(X)) ; writeln(none) ).
```

Good (cto build fe4714842, 16:29 CDT 10-29) prints `1`, `1`, `1`, `1`, then `found(pp)`. Bad (every build from the collector's 74f759a07, 18:44, through packages b37fb09e0, runtime edf347c58, icon 2e416841f, prolog b7086cf55) dies at the 5th/6th directive:
`scrip: fatal signal 11 (SIGSEGV) at pc 0x... (in the code pool: emitted code, or a page the assertz reclaim returned -- a reclaimed run-time fragment is PROT_NONE, so a pc there was a live activation the reclaim did not see ...)`.

**Shape that matters (delta-debugged from XSB's retract_tests/backsuite.P, 24 directives down to this):** a directive leaves a pending choicepoint of the form `( true ; assertz(kp(N,K,V)), fail )` after a `retract(kp(N,K,V))`, or `( true ; retract(kp(N,K,V)), fail )` after an `assertz`; later directives assert and retract the same key's facts. Plain `assertz`/`retract` of literal facts in directives (no predicate wrapper) does NOT crash.

**Window (commits between the good and the bad build, SCRIP):** the two that change the dynamic database's fact handling are 41658f99e (17:07, "the dynamic database walks the candidates of one first-argument key -- clause/2, retract/1 and retractall visit a key's slots") and f03f48c89 (17:48, "a dynamic predicate of ground facts is DATA -- assertz compiles no code fragment for such a fact"). I did not build the commits in between, so this is a window, not a bisect.

**What it blocks:** XsbTests retract_tests_load_backsuite (39 ref lines) and retract_tests_testretract: both reach the crash once XSB's storage_* builtins and abolish/reclaim_space exist (hq_packages' landing 2026-10-30), so they cannot flip until this is cured.

**Also measured, not a regression:** any program that pulls the loader prelude (consult/load_files at run time) takes 37-62 s to compile on every build back to 16:29 (planner pf_rel -> zls_g_ptr_frame_offs scans every frame slot); hello world is 0.8 s.
