# Byrd boxes: the sources

Every statement below is tied to a file and line of `/home/resources/manuals/byrd-boxes/` (about fifty documents; `PROVENANCE.txt` there names each one's origin) or of Lon's seeds in `/home/resources/ByrdBox/`. The digests were made on 2026-11-13 by five read-only readers and the cto, on Lon's word that day ("See all the white papers written starting with Mr. Larry Byrd and associates." / "Certainly inlcude the main paper by Todd Proebsting." / "You can also digest my seeds"). A line marked as a reader's inference is not in the source. Three files of the collection hold no text (Finkel 1980, Warren 1983, Haynes 1985: form feeds only) and Byrd's Research Paper 151, "Understanding the control flow of PROLOG programs", which the DEC-10 manual cites, is not in it. The three Ducassé reports are glyph-garbled in extraction and `1994-brayshaw-ppig-prolog-visualisation.txt` is a different paper (§ 4).

## 1. Byrd 1980 and the DEC-10 lineage

DEBUG = 1980-byrd-prolog-debugging-facilities-DEBUG.MEM.txt (read in full), GUIDE3 = 1980-byrd-guide-version3-dec10-prolog-GUIDE3.MEM.txt, PEREIRA = 1978-pereira-users-guide-dec10-prolog-PROLOG.DOC.txt, BOWEN = 1982-bowen-decsystem10-prolog-users-manual.txt, CMU = cmu-prolog.doc.txt (the same manual as BOWEN, version 3.47; only page headers differ). Quotes are verbatim with runs of spaces collapsed.

### Byrd's own definitions (DEBUG)

- The model (49-50): "a model of Prolog execution which views the program control flow in terms of movement about the program text." He calls it the "'text processor' model" (21, 450-452). "procedure box" appears once, at 147.
- The box (72-74): "I have drawn a box around the whole procedure and added some labelled arrows which indicate the control flow in and out of the box."
- Call (77-92): "This arrow represents initial invocation of the procedure. When a goal of the form 'descendant(X,Y)' is required to be satisfied, control passes through the call port of the descendant box with the intention of matching a component clause and then satisfying any subgoals in the body of that clause. Notice that this is independent of whether such a match is possible; i.e. the box is called, and then such matters are worried about."
- Exit (96-105): "This arrow represents a successful return from the procedure. This occurs when the initial goal has been unified with one of the component clauses and any subgoals have been satisfied. Control now passes out of the exit port of the descendant box."
- Redo (107-128): "This arrow indicates that a subsequent goal has failed and that the system is backtracking in an attempt to find alternatives to previous solutions. Control passes through the redo port of the descendant box. An attempt will now be made to resatisfy one of the component subgoals in the body of the clause that last succeeded; or, if that fails, to completely rematch the original goal with an alternative clause and then try to satisfy any subgoals in the body of this new clause."
- Fail (130-145): "This arrow represents a failure of the initial goal, which might occur if no clause if matched [sic], or if subgoals are never satsified [sic], or if any solution produced is always rejected by later processing. Control now passes out of the fail port of the descendant box and the systems continues to backtrack."
- Clauses are not visible (147-151): "the information we get about the procedure box is only the control flow through these four ports. This means that at this level we are not concerned with which clause matches, and how any subgoals are satisfied".
- Nesting (151-162): "whenever we are trying to satisfy subgoals, what we are actually doing is passing through the ports of their respective boxes."
- One box per invocation (163-177): "the box we have drawn round the procedure should really be seen as an invocation box. ... we will have a different box for each different invocation of the procedure."
- Backtracking into a box (222-241): "Backtracking is followed by moving your finger back up the code, every goal you meet can be seen as a redo in the trace. If this goal succeeds again then we come out at the exit port ... If the goal fails then we come out at the fail port and keep going backwards looking for a choice point."
- Redo state (293-296): "When we redo descendant we are in exactly the same place as when we left except for the direction of movement."
- Port counts (439-446): "for any invocation there is always only one call and fail, although there may be arbitrarly [sic] many redos and corresponding exits ( >= 0 )."
- Conjunction: Byrd draws no box for it. The diagram at 251-255 for `?- descendant(abraham,ANS), fail.` shows two goal boxes joined by a forward arrow and a backward arrow; the diagram at 185-205 draws a box around each body goal inside the procedure box and chains the two goals of clause 2.

### Specific points in Byrd's documents

- Cut: DEBUG gives no port behaviour for `!`; invocations "cut out of the search space (using !)" are unavailable (594-595). GUIDE3 1747: "! Cut any choices taken in the current procedure."
- Built-ins (DEBUG 737-743): "not all calls to procedures will be traced ... These include all primitive I/O evaluable predicates (eg get, put, read, write), all basic control structures (eg ',', ';', '->') and all debugging control evaluable predicates". The built-in `fail` is traced as an ordinary box: "(3) Call : fail / (3) Fail : fail" (283-284).
- Compiled code: GUIDE3 83-84: "most of the debugging aids, such as tracing, are not applicable to compiled code." The model describes the interpreter only (also BOWEN 1160-1161).
- Invocation number (DEBUG 710-717): "unique invocation identifier ... continuously incrementing regardless of whether or not you are actually seeing the invocations". Depth (720-722): "the number of direct ancestors this goal has".
- Skip (577-580): "only valid for call and redo ports"; control returns at "either the exit port or the fail port". Leashing (636-667): full, tight, half, loose, off, or 0-15 as bits for call, exit, redo, fail.
- No Unify port and no clause box in either Byrd document; "unified" occurs once in DEBUG (97), inside the Exit definition.

### Earlier and later documents

- PEREIRA 1978 has no box and no ports: the trace has two events (1129-1139), "-N goal" at a call and "+N goal" when it "is successfully completed". Cut (594-598): "When first encountered as a goal, cut succeeds immediately. If backtracking should later return to the cut, the effect is to fail the "parent goal"".
- BOWEN 1982 takes "Part of Chapter 2 ... from [Byrd 80]" (174), cited as "Understanding the control flow of PROLOG programs", Research Paper 151 (4338-4341; that paper is not in the collection). It names "The Procedure Box Control Flow Model" (689), adds "Control flow is viewed at the procedure level, rather than at the level of individual clauses" (674-675), rewords the call port "first the box is called, and then the attempt to match takes place" (730-731), adds a ";" option that "can be called at an Exit port to force a move to the Redo port" (1069-1070), and gives "(P -> Q; R) :- P, !, Q." (1893).
- Eisenstadt and Brayshaw 1988: an augmented AND/OR tree that "incorporates ... Byrd box models (call/exit/fail/redo procedural models) as special cases" and "tells the truth about clause head matching and deals correctly with the cut". Eisenstadt and Brayshaw 1990: status boxes at each tree node, "complete details of unification and control history". Tobermann and Beckstein 1993: "a precise mathematical specification of the box model for definite programs as it was informally introduced by Byrd".
- Three files hold only form-feed characters and no text: 1980-finkel-nested-iterators-recursive-backtracking.txt (27 bytes), 1983-warren-abstract-prolog-instruction-set.txt (34 bytes), 1985-haynes-logic-continuations-IU-TR183.txt (23 bytes).

### What a compiler writer could misread (the reader's list)

1. The Redo arrow ENTERS the box: it reports that a later goal failed (DEBUG 107-109) and prints the goal with its exit-time bindings (287); Fail prints the call-time goal (319).
2. Redo is shown for every exited box, outermost first (287 then 301), even when no alternative is left (318-319, Redo then Fail): a redo does not imply a choice point (the x option's "last real choice point", 796).
3. "always only one call and fail" (439-444) holds only under exhaustive backtracking: an invocation removed by cut (594-595) or left at a final success shows no Fail.
4. Control constructs have no box in Byrd: `,` `;` `->` are invisible (740-743); a conjunction box with its own four ports extends Byrd, in whose diagram conjunction is wiring between goal boxes (251-255). The reader's inference.
5. Cut has no port description in these sources; PEREIRA 596-598 routes backtracking into a cut to the failure of the parent goal, not to the goal before the cut.
6. call(X) and cut disagree: PEREIRA 2171-2180 makes the cut act on the clause containing call(X) when interpreted and local when compiled; BOWEN 2057-2060 makes it always local.
7. Exit does not close the box (104-105 read with 293-296): the box stays re-enterable.
8. DEBUG 368 prints "(1) Redo : descendant(isaac,esau)" although box 1 exited as "descendant(abraham,esau)" (365): a typo in the source.

## 2. The four-port translation: Proebsting 1997 and 1999, Danvy 2001

P97 = 1997-proebsting-simple-translation-goal-directed-evaluation.txt, P99 = 1999-proebsting-new-implementation-icon-language.txt, D01 = 2001-danvy-unifying-approach-goal-directed-evaluation.txt.

- The four chunks (P97:96-106): ".start The initial code executed for the entire expression rooted at [the operator]"; ".resume The code executed for resuming the expression"; ".fail The code executed when the expression fails"; ".succeed The code executed when the expression succeeds at producing a value." "The start and resume chunks are synthesized attributes. The fail and succeed chunks are inherited attributes." (P97:113-117). "translation produces four labeled chunks of code, one for each of Byrd's ports. In addition, each AST operator has a corresponding run-time temporary variable to hold the values it computes." (P97:89-93). "In the Byrd Box, ports are locations, whereas here they are pieces of code." (P97:132-133). "Byrd called these call, redo, fail, and exit." (P97:125).
- P97 has six templates: literal, unary minus, plus, less-than, to, if. P99 adds bang, create, scan (E1 ? E2), suspend, fail, procedure init/body, every, next, break. No template in the three papers for to-by, conjunction, alternation, while/until/repeat, not, limitation, return.
- Run-time ports: the if gate ("goto [ifstmt.gate]", P97:222-242, because the resume target depends on the condition's outcome, P97:209-219); loop.continue for break (P99:1293-1297); the PC field of a suspended procedure (P99:1445). Danvy uses a boolean gate (D01:818-820).
- Optimisation (P97:200-209): the naive output "suffers from generating many simple copies and many branches to branches. Propagating copies and eliminating branches to branches (by branch chaining and reordering the code) optimizes the code well"; Figure 1 (nine templates) becomes Figure 2 (twelve lines, five labels), "code that would be produced from two generic for loops". "requires nothing more powerful than conditional, direct, and indirect jumps." (P97:248-249).
- Jcon (P99): "The Jcon compiler is responsible for effecting goal-directed control flow. Beyond this, it is little more than a translator to calls on runtime system routines." (P99:205-207). A procedure fails by returning null; a suspending procedure returns a closure with a Resume method, its temporaries and locals saved in arrays and "the program location at which the Resume method should begin is kept in the PC field" (P99:1441-1447); "no analysis is done to determine which temporaries actually need to be saved ... the compiler conservatively stores all of them" (P99:1491-1492). "unless the context allows the possibility of resumption, the compiler ... makes no provision" (P99:814-816). Results: one half to one fourth of Icon version 9's speed on the JVMs of the day (P99:1823-1824).
- Danvy 2001: one monadic semantics instantiated with list, stream and two continuation monads, then compiled by specialising the interpreter; "The first argument is the success continuation and the second argument the failure continuation. Note that the success continuation takes a failure continuation as a second argument. This failure continuation determines the resumption behavior" (D01:413-418); the templates "are intrinsic to the semantics of Icon and can be provably derived" (D01:186-188); residual code "corresponds to the target programs of Proebsting's optimized template-based compiler" (D01:931-932). Subset: integer, plus, to, less-or-equal, if.
- Discrepancies the reader found: P97:215-219 and P99:1177-1178 say the gate gets "either E1's or E2's" resume label while both templates use E2 and E3; P99's break template jumps to loop.start where loop.succeed reads as intended (the reader's inference).

### The templates, one row a construct (start and resume are the construct's own; the rest are what it writes for its operands; `<-` stands for the assignment arrow the text extraction lost)

| Construct (file:lines) | start | resume | the operands' fail and succeed | extra |
|---|---|---|---|---|
| literal N (P97:147-150) | `value <- N; goto succeed` | `goto fail` | none | none |
| uminus(E) (P97:165-174) | `goto E.start` | `goto E.resume` | E.fail: `goto uminus.fail`; E.succeed: `uminus.value <- -E.value; goto uminus.succeed` | none |
| plus(E1,E2) (P97:132-139) | `goto E1.start` | `goto E2.resume` | E1.fail: `goto plus.fail`; E1.succeed: `goto E2.start`; E2.fail: `goto E1.resume`; E2.succeed: `plus.value <- E1.value+E2.value; goto plus.succeed` | none |
| LessThan(E1,E2) (P97:148-159) | as plus | as plus | as plus, except E2.succeed: `if (E1.value >= E2.value) goto E2.resume; LessThan.value <- E2.value; goto LessThan.succeed` (the comparison glyph is lost in the extraction; `>=` is the reader's inference) | none |
| to(E1,E2) (P97:175-187) | `goto E1.start` | `to.I <- to.I+1; goto to.code` | the wiring of plus, except E2.succeed: `to.I <- E1.value; goto to.code`; to.code: `if (to.I > E2.value) goto E2.resume; to.value <- to.I; goto to.succeed` | the counter `to.I` and a fifth chunk `to.code` |
| if E1 then E2 else E3 (P97:222-242) | `goto E1.start` | `goto [ifstmt.gate]` | E1.fail: `gate <- addrOf E3.resume; goto E3.start`; E1.succeed: `gate <- addrOf E2.resume; goto E2.start`; E2.fail and E3.fail: `goto ifstmt.fail`; E2.succeed and E3.succeed: `ifstmt.value <- En.value; goto ifstmt.succeed` | a run-time port: `gate` and an indirect goto |
| !E (P99:1158-1165) | `Goto E.start` | `Resume(bang.val, tmp, E.resume); Goto bang.succeed` | E.fail: `Goto bang.fail`; E.succeed: `OpFunction(tmp,"!",[E.val],E.resume); Move(bang.val,tmp); Goto bang.succeed` | `tmp` holds the suspended runtime generator |
| create E (P99:1200-1205) | `Create(create.val, E.start); Goto create.succeed` | `Goto create.fail` | E.fail: `CoFail()`; E.succeed: `CoRet(E.val, E.resume)` | a runtime thread |
| E1 ? E2 (P99:1223-1236) | `Goto E1.start` | `ScanSwap(sub,pos); Goto E2.resume` | E1.fail: `Goto scan.fail`; E1.succeed: save &subject and &pos; `Goto E2.start`; E2.fail: restore them; `Goto E1.resume`; E2.succeed: `ScanSwap; Goto scan.succeed` | two temporaries a scan |
| suspend E (P99:1252-1259) | `Goto E.start` | `Goto suspend.fail` | E.fail: `Goto suspend.fail`; E.succeed: `Succeed(E.val, E.resume)` | the resume address is stored at run time |
| fail (P99:1263-1266) | `Fail()` | `RunTimeError()` | none | none |
| every E do B (P99:1299-1306) | `Goto E.start` | `Goto every.continue` | E.fail: `Goto every.fail`; E.succeed: `Goto B.start`; B.fail and B.succeed: `Goto E.resume` | `continue` is a label temporary |
| break E (P99:1316-1323) | `MoveLabel(loop.continue, break.resume); Goto E.start` | `Goto E.resume` | E.fail: `Goto loop.fail`; E.succeed: `Move(loop.val, E.val); Goto loop.start` | a run-time port: several breaks a loop |

No template in the three papers: a call ("Translating a function call that generates a sequence of values requires a mechanism for suspending and resuming a function invocation.", P97:252-255); conjunction (in Jcon a runtime method that "just returns its second argument", P99:772-773); alternation ("a control structure that must be addressed by the compiler", P99:774-775); limitation (P99:779-781); `to by` (in Jcon the runtime generator `ToBy`, P99:776-777).

## 3. The formal models of the box

K03 = 2003-kulas-pure-prolog-execution-21-rules.txt (K03f, the fernuni file, is the same paper with a scrambled rule figure: cite K03); VCL = 2000-kulas-rewriting-prolog-semantics-VCL2000.txt; WRLA = 2000-kulas-beierle-rewriting-semantics-WRLA.txt; LOP = 2000-kulas-annotations-for-prolog-LOPSTR99-LNCS1817.txt; WLPE = 2000-kulas-debugging-prolog-using-annotations-WLPE99-ENTCS30-4.txt; K05 = 2005-kulas-toward-concept-backtracking-computation.txt; D07 = 2007-deransart-observational-semantics-prolog-box-model.txt; D07fr = the extended French report; J99 = 1999-jahier-specifying-trace-models-continuation-semantics-LPE99.txt.

### Kulaš: S:PP, pure Prolog execution in 21 rules (K03 Fig. 2, 231-321)

Vocabulary: `port ::= call | exit | fail | redo` (K03:197). An event is "a quadruple (Port, Goal, A-stack, B-stack)" (K03:176). The A-stack holds the ancestors, tagged `1/A,B`, `2/A;B` (K03:199-200). The B-stack holds "bets": the mgus plus memos `BY(goal, atom) | OR(goal, (tag/goal;goal))` (K03:201-202). A push event is call or redo; a pop event is exit or fail (K03:478-480). Ports belong to every goal, not only predicates (K03:97-99). Canonical form: one clause per predicate, head unification moved into the body as `X=T`, clauses joined by `;` (K03:55-62).

The rules ([..] is the A-stack top; K03 line):
- Conjunction: conj:1 (235) call A,B → call A [1/A,B]; conj:2 (238) exit A [1/A,B] → call B [2/A,B]; conj:3 (241) fail A [1/A,B] → fail A,B; conj:4 (243) exit B [2/A,B] → exit A,B; conj:5 (246) fail B [2/A,B] → redo A [1/A,B]; conj:6 (248) redo A,B → redo B [2/A,B].
- Disjunction, which is also clause selection: disj:1 (254) call A;B → call A [1/A;B]; disj:2 (256) fail A [1/A;B] → call B [2/A;B]; disj:3 (259) fail B [2/A;B] → fail A;B; disj:4 (261) exit A → exit A;B, push OR(A,1/A;B); disj:5 (263) exit B → exit A;B, push OR(B,2/A;B); disj:6 (266) redo A;B with OR(C,N/A;B) on top → redo C [N/A;B], the memo popped.
- true and fail: true:1 (271) call true → exit true; true:2 (274) redo true → fail true; fail (280) call fail → fail fail.
- Unification: unif:1 (288) call T1=T2 → exit and push the mgu if one exists, else fail; unif:2 (292) redo T1=T2 with the mgu on top → fail, the mgu popped.
- User predicate: atom:1 (305) call GA → call σ(B) [GA] for a fresh clause H:-B with mgu(GA,H)=σ, else fail GA; atom:2 (308) exit B [GA] → exit GA, push BY(B,GA); atom:3 (310) fail B [GA] → fail GA; atom:4 (315) redo GA with BY(B,GA') on top → redo B [GA'], the memo popped.
- Not covered: cut, negation, if-then-else ("pure", K03:35).

How a redo finds the inner box: it descends to the most recent exit: into the right conjunct (conj:6), into the disjunct named by the OR memo (K03:144-147), into the body kept in the BY memo, which also fixes the definition at call time (K03:369-372). Leaves turn redo into fail (true:2, unif:2); that fail becomes redo of the left conjunct (conj:5) or call of the next disjunct (disj:2).

Proved: the transition relation is functional (K03:411); a legal event has a unique legal predecessor and successor (K03:530-532); modularity, `call G ⟨U,Σ⟩ →* exit G ⟨U,Σ'+Σ⟩`, "Notice the same A-stack" (K03:341-344, 588-600); "In a failed derivation, Σ = nil" (K03:632). K05 restates the calculus as S1:PP in 20 axioms (K05:297-371), the memos shrunk to `BY(goal) | OR(tag)` (K05:261).

The earlier rewriting semantics (VCL, WRLA): call/1 is opaque to cut (VCL:317); cut: "all the continuations emptied" up to and including the parent's (VCL:348-349, 362, rules 374-385); if-then is `once(If),Then` (VCL:576); cut-transparent disjunction (VCL:627-636). The annotations papers give the ports by goal replacement (LOP:373-392; WLPE:410-422): call `C, P`; exit `P, C`; fail `(P ; C, fail)`; redo `P, (true ; C, fail)`.

### Kulaš 2005 on backtracking

"Backtracking means reconsidering (cancelling) the already made choices (substitutions)." (VCL:125-126). "a backward derivation Pop G ⟨U⟩ ⟶ Push G ⟨U⟩ we call a backward pass relative to G and U" (K05:539-540). "Forward and backward computation of Prolog are treated in a uniform manner" (K05:888-889). On the box model: "The Byrd model is a seminal work in control flow, but it proved hard to formalize, and variable handling was not tackled in the original work at all" (K05:841-843); "traces of Prolog execution are generated, but there is no support for reasoning about the structure of the execution" (K05:858-859).

### Deransart 2007: the observational semantics

A full virtual trace of events `et : (t, at, St+1)` (D07:105-116); the actual trace is extracted from it and a rebuilding function interprets it (D07:135-148). "A full state has 9 parameters: {T, u, n, num, pred, claus, first, ct, flr}" (D07:331-332): the tree, the current node, the creation counter, node number, predication, clause list, first-visit flag, complete flag, failed flag. An actual event is `t r l port p`: chrono, creation number, depth, port, predication (D07:512-522). Ports: "Call, Exit, Fail or Redo" (D07:520-521). Seven rules (D07:439-467). "Each node is labelled with a predication and a packet of clauses" (D07:326); a choice point is a node whose clause list still has a clause (D07:386-390). Unification and clause choice are external functions (D07:406-409). "Whatever is the state, only one rule in R can be applied" (D07:497-498). Depth is a "useless attribute" (D07:656-658). The French report compares three trace models on one program, simplified m1, GNU Prolog m2 and original Byrd m3, with 28, 32 and 44 events and "m1 ⊆ m2 ⊆ m3" (D07fr:1674-1675, 1887, 1966, 2049), and remarks that the Exit events alone rebuild the proof trees (D07fr:817-818).

### Jahier 1999

A continuation semantics with three continuations (J99:152-155): success ("controls the formation of proofs"), failure ("controls the search"), cut failure ("the code to be executed after a cut"). Call is emitted before resolution; the callee's success continuation emits exit, then runs the caller's success continuation with a failure continuation that emits redo and resumes the callee; the callee's failure continuation emits fail (J99:216-223). Cut gets call and exit only (J99:207).

### Where the formal models disagree

- Redo into a deterministic exit: Byrd, Kulaš and Jahier redo every exited box (K03:274; "(redo a), (fail a)", J99:315; m3 "Redo p2(a) / Fail p2(a)", D07fr:1773-1774). Deransart jumps to the choice point: "one does not repeat all the Redo" (D07:487-489). GNU redoes the ancestor path only (D07fr:1738-1739).
- Unification as a port: `=` has four ports and head unification lives in the body in Kulaš (K03:39-42, 288-292); Deransart treats it as external (D07:406-409).
- Clause-level boxes: each disjunct has its own ports in Kulaš (K03:254-266); Deransart keeps clauses inside the predicate box and out of the trace (D07fr:843-845).
- Cut: absent from K03, K05 and Deransart; Jahier chooses "not to generate the redo and fail event" (J99:224-225); VCL empties the continuations (348-349).
- Fail means "no (more)", not finite failure (LOP:673; VCL:1087-1089).

### Invariants for a four-port implementation (the reader's ten)

1. Every port has exactly one successor, and every reachable event exactly one predecessor (K03:411, 530-532).
2. A fail is paired with the most recent call of the same goal in the same context, with the binding stack exactly as at that call (K05:554-556, 586; K03:632).
3. A redo enters a box in exactly the state its last exit left (K05:559).
4. A box's life is call, then exit and redo in pairs, ending in one fail or an exit (K05:562-565, 744-756).
5. In a conjunction, fail of the left fails the whole; fail of the right redoes the left; redo of the whole enters the right (K03:241, 246, 248).
6. Fail of an alternative calls the next one; redo must re-enter the alternative that last exited, so exit records which (K03:256, 266, 315).
7. A determinate leaf answers redo with fail after undoing its own binding (K03:274, 292).
8. A box returns its caller's context unchanged; only bindings grow (K03:341-344).
9. The clause set is fixed at call (K03:369-372).
10. Cut succeeds exactly once and empties the choice points up to and including the parent's; disjunction is transparent, call/1 opaque (J99:224-225; VCL:348-349, 607-608, 313-317).

## 4. The systems' ports and the trace analysers

SWI-B = manual-swi-byrd-box-model.txt, SWI-O = manual-swi-debugger-overview.txt, SWI-T = manual-swi-prolog_trace_interception-4.txt, SIC-PB = manual-sicstus-procedure-box.txt, SIC-371 = manual-sicstus-3.7.1-debugging.txt, SIC-07 = 1987-carlsson-sicstus-0.7-manual.txt, QP = manual-quintus-prolog-users-manual-3.5.txt, ECL = manual-eclipse-box-model-official.txt, ECL-04 = manual-eclipse-box-model.txt, GNU = manual-gnu-prolog-debugging-chapter-official.txt, CIAO = manual-ciao-debugger.txt, YAP = manual-yap-users-manual.txt, DN94, OP97, AV98 = the Ducassé files of 1994, 1997, 1998.

TWO DEFECTS OF THE COLLECTION. The three Ducassé reports are glyph-garbled in their text extraction (font codes with no Unicode map; only the figures are legible): the reader decoded passages by a substitution table, so a quote marked (decoded) is a reconstruction, and only a fraction of each report was read, RR3531 hardly at all. `1994-brayshaw-ppig-prolog-visualisation.txt` is the wrong paper: a PPIG abstract on a Prolog-teaching experiment that never mentions the box model.

### Systems against ports

| System | Ports documented | Where |
|---|---|---|
| DEC-10 (as cited) | call, exit, redo, fail | SWI-O:225-229; QP:8635 |
| SWI-Prolog | call, redo, exit, fail, and unify, exception; the trace hook adds redo(PC), exception(E), cut_call(PC), cut_exit(PC) | SWI-B:199-201; SWI-T:174-213 |
| SICStus 0.7 | call, exit, redo, fail; Block and Unblock messages | SIC-07:552, 613, 669, 686-690 |
| SICStus 3.7.1 | the four and exception; Block and Unblock messages | SIC-371:87, 226, 358, 380-389 |
| SICStus current | the five and block, unblock ports | SIC-PB:43-44, 120-129 |
| Quintus 3.5 | call, exit, redo, fail, done, head, exception | QP:7019-7020, 7825-7826, 52966 |
| ECLiPSe | CALL, EXIT and *EXIT, REDO, FAIL, NEXT, ELSE, LEAVE, DELAY, RESUME | ECL:20-22, 67 |
| GNU Prolog | call, exit, fail, redo, exception | GNU:11-17, 26 |
| Ciao | call, exit, redo, fail | CIAO:89 |
| YAP | call, exit, redo, fail | YAP:6454, 6486-6510 |
| Opium | call, exit, fail, redo, unify | OP97:626-628 (decoded) |

### The ports beyond Byrd's four

- unify (SWI): "represents the neck instruction, signalling the end of the head-matching process. This port is normally invisible" (SWI-T:188-190).
- Head (Quintus): "shows the clauses' heads that will be tried for unification… which clause is about to be tried, and which clause will be tried next if this clause fails… shown after indexing" (QP:6853-6856).
- NEXT (ECLiPSe): "from the failure of one clause to the head unification of a following clause" (ECL:60-64). ELSE: the next branch of a disjunction tried after the previous branch failed (ECL:67-73).
- Done (Quintus): "just like the Exit port, but signifies a determinate exit" (QP:6851).
- exception: SICStus, "an exception that was raised in the initial goal… the system continues to pass the exception to outer levels" (SIC-PB:93-100); SWI, "activated on each parent frame of the frame generating the exception until the exception is caught" (SWI-T:202-206).
- LEAVE (ECLiPSe): "All ancestors of the predicate that raised the exception will subsequently exit via a LEAVE port, until a catch/3… is found… This invocation of catch/3 then passes a NEXT port" (ECL:99-106).
- DELAY and RESUME (ECLiPSe): DELAY "is a singleton port, it does not enter or leave a box. However, a new invocation number is assigned"; at RESUME "the box then behaves as if it had been entered through its CALL port" (ECL:113-126). Block and Unblock (SICStus): "passed through when a goal is blocked / …unblocked" (SIC-PB:123-129).
- cut_call and cut_exit (SWI's hook only): "A cut is encountered at PC"; "A cut has been executed" (SWI-T:208-213).

Read against SCRIP's ports: unify, Head and NEXT are events inside a predicate box's α and clause step; ELSE is the disjunction's `A.ω`; Done and *EXIT mark a γ that leaves no choice (a bounded box); exception and LEAVE are an ω with the ball armed; DELAY and RESUME are the wake of a suspended goal. None is a fifth way into or out of a box.

### How the systems show the constructs

- Conjunction, disjunction, if-then-else, negation and cut are INVISIBLE to the debuggers: SICStus 0.7, "true/0, !/0, ','/2, '->'/2, ;/2, '\+'/1, and if/3… you will never see messages" (SIC-07:677-682); Quintus omits "!/0 (cut), ;/2 (or), ,/2 (and), and ->/2 (local cut)" (QP:7865-7867); SICStus 3.7.1, "calls that are compiled in-line… are not traced" (375). A disjunction's choice shows only as ECLiPSe's ELSE or as SWI's redo(PC) with a non-zero PC, "an in-clause choice point left by, e.g., ;/2" (SWI-T:180-184).
- A deterministic exit: SWI, "Backtrack points are not shown if either the goal succeeded deterministically or its alternatives were removed using the cut" (SWI-O:774-777); ECLiPSe, only an *EXIT box can be re-entered by REDO (ECL:44-50, 74-76); Quintus, Done against Exit; SICStus and YAP print `?` at a nondeterminate Exit (SIC-371:334-339; YAP:6522).
- Dynamic and interpreted code: Quintus tags "(dynamic)" (QP:7840); SICStus 0.7 debugs "in the Prolog interpreter" (480); Ciao needs its interpreted mode (CIAO:35).

### Ducassé and Noyé, Opium

"A step by step trace with all its details is too much information at too low a level of abstraction… as the relevant pieces of information are not contiguous, programmers cannot… perform pattern matching at low cost… their commands are not expressive enough" (OP97:135-142, decoded). "In an exhaustive trace the events related to a given goal are not necessarily consecutive" (OP97:563). A second model "closer to the operational semantics" adds a port for the execution backtracking to the goal itself, as distinct from into one of its subgoals; "For automated analysis both ports should be extracted and clearly separated." (DN94:478-505, decoded). The exit port has no code location under last-call optimisation (DN94:671-678). Opium's event attributes (OP97:570-649, decoded): a chronological number, the goal's invocation number, depth, port, module and predicate, arguments (at redo "the same instantiation as for the previous [exit] event"), and the clause for a unify event.

### Where the systems disagree

1. Redo: SICStus and Quintus use one port for re-entry, "resatisfy one of the component subgoals… or… rematch" (SIC-PB:67-79); SWI's redo is "traced when the engine backtracks to find the next matching rule" (SWI-B:210-211), `redo(0)` the next clause and a non-zero PC an in-clause choice (SWI-T:177-186); ECLiPSe splits it into REDO, NEXT and ELSE (ECL:60-90).
2. Redo after a deterministic exit: hidden in SWI (SWI-O:774) and ECLiPSe (ECL:74-76); Byrd's text shows it.
3. Exception: no port in SICStus 0.7, YAP, Ciao; a fifth port in SICStus 3.7.1 and later, GNU, Quintus, SWI; ECLiPSe's LEAVE, after which the catcher passes NEXT.
4. Head unification: SWI's unify comes after a successful match; Quintus's Head before the attempt; ECLiPSe's NEXT covers only later clauses; SICStus is "not concerned with identifying the matching clause" (SIC-PB:103-105).
5. Call: SWI, "call is traced, once, if any rules might match" (SWI-B:208); SICStus, "first the box is called, and then the attempt to match takes place" (SIC-PB:53-55).
6. The arguments shown at a port: ECLiPSe shows none at FAIL or LEAVE (ECL:58-59, 109) and call-time values at REDO (87-90); Quintus's Redo shows "the same as at the previous Exit" (QP:7848).
7. The box's identity: SWI says "each predicate" (SWI-B:179); SICStus says "invocation box" (SIC-PB:112-118).

## 5. The implementation models

C83 = 1983-carlsson-on-implementing-prolog-in-functional-programming-UPMAIL-TR5.txt; AK = 1991-aitkaci-wam-tutorial-reconstruction.txt; T11 = 2011-tarau-binprolog-continuation-passing.txt; A02 = 2002-andrews-witness-properties-semantics-prolog-cut.txt; ctl, meta, exc, dcg = manual-swi-{control-predicates,metacall,exception-handling,dcg}.txt; Q = manual-quintus-prolog-users-manual-3.5.txt; Y = manual-yap-users-manual.txt; S07 = 1987-carlsson-sicstus-0.7-manual.txt. Gaps: A02 has no call/1 and restricts cut to the clause's top level; the four SWI files do not specify findall, bagof, setof, forall, between or call//N; Q, Y and S07 were read only in their database, meta-call and indexing sections.

### Carlsson 1983: success continuations

"If the theorem prover succeeds in proving its goal, it calls this continuation. If it fails, it simply returns. ... it calls the continuation for each proof found." (C83:129-131). The host stack is the failure continuation. The reader's mapping of the code at C83:357-381 (an inference): α is the entry to `resolve`; γ is `(invoke cont)`; ω is the function returning; β is the return into `try-assertions`, which does `(reset mark)` and tries `(cdr assertions)`. Unification binds destructively and trails: `(push x *trail*) (rplacd x y)` (C83:392-394). Cut is "lexically scoped", so failure returns "an integer specifying an ancestor depth" (C83:472-477); "Upon backtracking, cut fails the parent goal." (C83:505-507). bagof's continuation pushes a copy and returns nil "to force the theorem prover to really find all proofs" (C83:459-463).

### Aït-Kaci: the WAM

- A choice point holds the argument registers, E, CP, the previous B, the next clause, TR, H (AK:1712-1755), and B0 (AK:4526-4541). try_me_else creates it, retry_me_else restores it and updates the next clause, trust_me restores and pops it (AK:1808-1818, 1887-1938).
- The trail: "Only conditional bindings do. A conditional binding is one affecting a variable existing before creation of the current choice point." (AK:1702-1703).
- Cut: call and execute set B0 to B; "executing a cut amounts essentially to resetting B to the value of B0" (AK:3626-3634). A deep cut saves B0 in the environment (get_level) and `cut Yn` uses it (AK:3703-3724); because indexing may create two choice points a call, B0 "is systematically saved as part of a choice point at its creation and restored upon backtracking" (AK:3763-3765).
- Indexing: switch_on_term dispatches on variable, constant, list, structure (AK:3437-3440); switch_on_constant and switch_on_structure hash, a miss backtracks (AK:3441-3454); try, retry, trust thread the clauses of one key (AK:3463-3467). With an instantiated first argument "no choice point frame for it is ever needed" (AK:3478-3480).
- A fact is its head instructions then `proceed` (AK:1310-1312).
- What the WAM does in compiled instructions: per-clause head unification in read and write mode (AK:920-931), clause sequencing, choice-point save and restore, trail undo, cut, first-argument dispatch. Only the general `unify`, `bind` and `trail` are shared routines (AK:4753-4869). Not covered: conditionals, assert and retract, setof (AK:3817-3819).

### Tarau: BinProlog

`A :- B1,...,Bn` becomes a binary clause carrying its continuation (T11:136-138), for example "nrev([X|Xs],Zs,Cont):-nrev(Xs,Ys,app(Ys,[X],Zs,Cont))." (T11:148); a fact calls `true(Cont)` (T11:144). Binary clauses "need no “return” after a call" (T11:119-120): no environments, an "OR-stack-only WAM" (T11:178-180). Backtracking remains: try, retry, trust are kept (T11:317-318). Meta-call: call/2 "adds the extra argument Cont to f(...)", looks the predicate up, "fills up the argument registers and proceeds with the execution of the code of those predicates" (T11:212-216). The cut barrier travels in the continuation (T11:261-262). The emulated dynamic database is "2-3 orders of magnitude slower" (T11:1052-1053).

### Andrews 2002: the cut

"Cut therefore cuts away not only the later clauses of the same predicate, but also the alternative clauses for subgoals that appear earlier in the clause." (A02:222-223). Billaud's reading: "when a predicate is called, the current backtrack stack is stored; the execution of a cut corresponds to discarding the current backtrack stack and replacing it with the one stored by the current predicate." (A02:270-272). "The cut in the if-then-else construct is hard cut in most Prologs." (A02:256).

### What the SWI manuals fix

- "Meta calling is opaque to the cut. ... The following control structures are transparent to the cut: ;/2, ->/2 and *->/2. Cuts appearing in the condition part of ->/2 and *->/2 are opaque to the cut." (ctl:302-311).
- call/N: "Append ExtraArg1, ExtraArg2, ... to the argument list of Goal and call the result." (meta:307-308). A variable body goal is call/1 (meta:293-296). "once(Goal) :- call(Goal), !." (meta:350-351).
- `\+` is a control structure; a run-time cut in it "is scoped to the call/1" (ctl:458-464).
- If-then-else: "Unlike !/0, the choice point of the predicate as a whole (due to multiple clauses) is not destroyed." (ctl:374-376); `(If -> Then)` fails when If fails (ctl:385-387). Soft cut: `(call(Condition), Action)` if Condition ever succeeds, else `(\+ Condition, Else)` (ctl:418-427).
- catch/3: "all choice points generated by Goal are cut, the system backtracks to the start of catch/3 while preserving the thrown exception term, and Recover is called as in call/1." (exc:275-278). "ISO demands that throw/1 make a copy of Exception, walk up the stack to a catch/3 call, backtrack and try to unify the copy of Exception with Catcher." (exc:305-308).
- setup_call_cleanup: "Cleanup will be called exactly once after Goal is finished: either on failure, deterministic success, commit, or an exception." (meta:450-452).
- DCG: the expansion "adds two additional arguments to each term" (dcg:264-266); phrase/2 is `phrase(DCGBody, InputList, [])` (dcg:302).

### The dynamic database in the manuals

- Quintus, the logical update view: "the definition of a dynamic procedure that is visible to a call is effectively frozen when the call is made. A procedure always contains, as far as a call to it is concerned, exactly the clauses it contained when the call was made." (Q:14733-14735). "a retracted clause is reclaimed only when the system determines that there are no choice points on the stack that could allow backtracking to the clause" (Q:14952-14954). "Dynamic procedures are implemented by interpretation, even if they are included in a file that is compiled." (Q:14824-14825). "dynamic predicates as well as static predicates are indexed" (Q:3579-3589).
- YAP defaults to the immediate update view: "new clauses or entries to the data base are visible in backtracking" (Y:7834-7843); the logical view: "any additions or deletions of clauses for a goal will not affect previous activations of the goal" (Y:7848-7849).
- SICStus 0.7: "If reactivated by backtracking, invocations of the predicate whose clauses are being retracted will proceed unaffected by the retracts." (S07:2008-2010). "Dynamic predicates are always stored in consulted form even if a compilation is in progress." (S07:979-984).

So the systems of the manuals INTERPRET a dynamic clause, and the WAM COMPILES every head. SCRIP's law takes the WAM's side for the dynamic clause too: its head is unified by a box (SKILL.md section 3.10).

### Consequences for a native four-port compiler (the reader's list)

1. γ jumps to the continuation and ω to the newest choice point, with no interpreter loop (C83:129-131; AK:1826).
2. Bindings older than the newest choice point are trailed and undone at β (AK:1702-1703).
3. Head unification is emitted per clause, never a generic matcher over stored clause terms (AK:920-931).
4. First-argument dispatch is emitted code and avoids the choice point when one clause matches (AK:3478-3480; Q:3654-3658).
5. Cut needs the choice-point level captured at α, kept in the frame for deep cuts and restored on backtracking (AK:3703-3724, 3763-3765).
6. Meta-call, `\+` and conditions open a new cut barrier; the branches of `;`, `->`, `*->` use the clause's (ctl:302-311).
7. call/N is argument extension, a lookup, then an ordinary α entry (T11:212-216; meta:307-308).
8. If-then-else commits to the condition's first solution but keeps the predicate's clause alternatives (ctl:374-376).
9. A dynamic call fixes the clause set at α so later asserts and retracts are invisible to its β (Q:14733-14735).
10. A retracted clause stays resumable until no choice point can reach it (Q:14952-14954).
11. Dynamic clauses get first-argument indexing and last-clause determinacy like static ones (Q:3588, 3713-3714).
12. throw copies the ball, finds the innermost unifying catch, cuts the goal's choice points, restores the catch's entry state, then calls the recovery (exc:275-278, 305-308).

## 6. Lon's seeds (`/home/resources/ByrdBox/`; copies in `/home/corpus/library/probe_reference/bb/`)

Hand-written C in which every construct is four labeled entries and every transfer is a `goto`. They are where the port names α β γ ω and the frame record ζ come from.

**`test_icon.c`** (174 lines) is Proebsting's worked example, `every write(5 > ((1 to 2) * (3 to 4)))`, twice. The first pass is the nine templates as written by the attribute grammar: for each operator a value variable (`x5_V`, `to1_I`, `mult_V`) and the labels `_start`, `_resume`, and for each operand `_succeed` and `_fail`:
```
to1_start:                                      goto x1_start;
x1_fail:                                        goto to1_fail;
x2_fail:                                        goto x1_resume;
to1_code:           if (to1_I > x2_V)           goto x2_resume;
                    else to1_V = to1_I;         goto to1_succeed;
to1_resume:         to1_I = to1_I + 1;          goto to1_code;
x1_succeed:                                     goto x2_start;
x2_succeed:         to1_I = x1_V;               goto to1_code;
```
The second pass is the optimised code, eleven lines and two loop counters: what the planner and the encoder are meant to reach from the first.

**`test_sno_1.c`** (182 lines) matches `POS(0) ARBNO('Bird' | 'Blue' | LEN(1)) $ OUTPUT RPOS(0)` against a subject Σ of length Ω with the cursor Δ. Each primitive is a box that moves Δ at α and moves it back at β:
```
POS0_α:     if (Δ != 0)                         goto POS0_ω;
            POS0 = str(Σ+Δ, 0);                 goto POS0_γ;
POS0_β:                                         goto POS0_ω;

BIRD_α:     if (Σ[Δ+0] != 'B')                  goto BIRD_ω;   ... one test a character
            BIRD = str(Σ+Δ, 4); Δ += 4;         goto BIRD_γ;
BIRD_β:     Δ -= 4;                             goto BIRD_ω;

LEN1_α:     if (Δ+1 > Ω)                        goto LEN1_ω;
            LEN1 = str(Σ+Δ,1); Δ+=1;            goto LEN1_γ;
LEN1_β:     Δ-=1;                               goto LEN1_ω;
```
Alternation records which arm took γ in a cell and dispatches β on it (the disjunction's gate, as a selector):
```
alt_α:      ζ->alt_i = 1;                       goto BIRD_α;
alt_β:      if (ζ->alt_i == 1)                  goto BIRD_β;
            if (ζ->alt_i == 2)                  goto BLUE_β;
            if (ζ->alt_i == 3)                  goto LEN1_β;
                                                goto alt_ω;
BIRD_γ:     ζ->alt = BIRD;                      goto alt_γ;
BIRD_ω:     ζ->alt_i++;                         goto BLUE_α;
```
ARBNO keeps one frame record per iteration, an array of ζ; α opens iteration 0, β opens one more iteration, and the body's ω steps back one record and resumes the iteration before:
```
ARBNO_α:    ζ = &_1[ARBNO_i=0];
            ζ->ARBNO = str(Σ+Δ, 0);             goto alt_α;
ARBNO_β:    ζ = &_1[++ARBNO_i];
            ζ->ARBNO = ARBNO;                   goto alt_α;
alt_γ:      ARBNO = cat(ζ->ARBNO, ζ->alt);      goto ARBNO_γ;
alt_ω:      if (ARBNO_i <= 0)                   goto ARBNO_ω;
            ARBNO_i--; ζ = &_1[ARBNO_i];        goto alt_β;
```
Concatenation is the conjunction (`POS0_γ → assign_α`, `assign_ω → POS0_β`, `seq_β → RPOS0_β`), and the immediate assignment `$` is a box whose operand's γ does the write.

**`test_sno_2.c`** (378 lines) adds SPAN, BREAK, NOTANY and nested ARBNO in a treebank reader. **`test_sno_3.c`** (589 lines) is a recursive expression grammar: each named pattern is a C function entered at a port, `str_t V(V_t ** ζζ, int entry)`, which on `entry == α` takes a fresh frame (`enter(ζζ, sizeof(V_t))`) and jumps to `V_α`, and otherwise jumps to `V_β` with the frame it left; a parent keeps its children's frame pointers in its own frame. That is a procedure call as one box with its activation frame, and a recursion as a chain of frames. **`test_sno_4.c`** (169 lines) is a match whose result is returned at γ or the empty string at ω. `/home/resources/ByrdBox/byrd_box.py` and `/home/resources/ByrdBox/transl8r_SNOBOL4.py` are the generators that wrote these files from source text.

**Icon's operators, from Proebsting's templates** (reference § 2 has the line numbers): a literal is `α: value; → γ` and `β: → ω`; a unary operator passes α and β to its operand and computes at the operand's γ; a binary operator starts the left at α, starts the right at the left's γ, resumes the left at the right's ω, and resumes the right at β; a comparison is a binary operator whose test, when false, goes to the right operand's β; `E1 to E2` adds a counter and a `code` chunk; `if` adds the gate; `every E do B` sends both of B's exits to E's β; `suspend` leaves through γ recording the operand's β as the place to come back to.
