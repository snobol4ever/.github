---
name: byrd-boxes
description: The Byrd box model itself: the four ports α β γ ω, Proebsting's four-chunk translation, the α β γ ω layout of every Prolog construct, what is a box and what is only a value service, the literature from Byrd 1980 to Danvy 2001, and Lon's seed programs. Load before designing or building any box, lowering a control construct, or touching the Prolog engine.
---

# Byrd boxes

SCRIP is one machine: every pattern, generator and goal of every language is a four-port box wired at compile time. This page is the model itself. The templates' coding rules are skill `box-templates`; where a box's cells live is skill `scrip-memory-model`; how compiled Prolog runs today is skill `prolog-engine`. The sources, quoted by file and line, are `reference.md` beside this file.

## 0. Why this page exists (Lon, 2026-11-13, in the cto's window, verbatim)

"What are going to do about Prolog not using Bryd boxes instead of C code in general? What are we going to do about Prolog not using BB's for ALL its GOAL DIRECTED EVAL?" / "does their exist a SKILL for byrd boxes? If not collect a plethora of documents and combine them into a SKILL or add to existing SKILL." / "See all the white papers written starting with Mr. Larry Byrd and associates." / "Certainly inlcude the main paper by Todd Proebsting." / "We want the byrd box layouts for ALL Prolog constructs. What I call alpha, beta, gamma, and omega." / "You can also digest my seeds: test*icon*.c and test*sno*.c programs which implement BB's." / "So it is up to you to create a wonderful SKILL or multiple SKILLS for all you have learned here today and now."

No skill held the model before this one: sixteen skill files named a Byrd box once or twice each, and the literature (about fifty documents, `/home/resources/manuals/byrd-boxes/`) and the seeds (`/home/resources/ByrdBox/`) were read by none of them.

## 1. The model

**The four ports.** Lon's names, used in every template, plan row and seed: **α proceed** (Byrd's call, Proebsting's start), **β recede** (redo, resume), **γ succeed** (exit, succeed), **ω concede** (fail, fail).

**Byrd 1980** drew the box around a procedure to explain Prolog's control flow to the user of an interpreter's debugger: "I have drawn a box around the whole procedure and added some labelled arrows which indicate the control flow in and out of the box." The call port is entered "with the intention of matching a component clause and then satisfying any subgoals in the body of that clause"; the exit port is "a successful return"; the redo port means "a subsequent goal has failed and that the system is backtracking in an attempt to find alternatives to previous solutions"; the fail port is "a failure of the initial goal". "When we redo ... we are in exactly the same place as when we left except for the direction of movement." His box is per invocation, hides the clauses ("we are not concerned with which clause matches"), and gives the control constructs `,` `;` `->` no box at all: in his diagrams a conjunction is the wiring between two goal boxes.

**Proebsting 1997** made the box a compiler: "In the Byrd Box, ports are locations, whereas here they are pieces of code." For each operator of the syntax tree the translation produces "four labeled chunks of code", one for each of Byrd's ports, plus one temporary for the operator's value. "The start and resume chunks are synthesized attributes. The fail and succeed chunks are inherited attributes": an operator writes its own α and β, and writes the γ and ω of each of its operands. Some resumptions are known only at run time (which branch of an `if` ran), so a port may be a jump through a cell, his `gate`. The scheme "requires nothing more powerful than conditional, direct, and indirect jumps", and after copy propagation and branch chaining the four-chunk code of `5 > ((1 to 2) * (3 to 4))` is two plain nested loops. Lon's seed `test_icon.c` is that example written out as labeled gotos, both passes; his `test_sno_*.c` do the same for SNOBOL4 patterns, with the names α β γ ω and the frame record ζ that the whole machine now carries.

**The invariants** (Kulaš's 21 rules for pure Prolog prove them; reference.md § 3):
1. Every port has exactly one successor: nothing in a box chooses between continuations except by a test the layout names.
2. A box's life is one α, then γ and β in pairs, ending in one ω or in a γ nobody resumes.
3. A β enters the box in exactly the state its last γ left; an ω leaves the bindings exactly as they stood at the α.
4. In a conjunction the ω of the right is the β of the left and the β of the whole is the β of the right.
5. The ω of one alternative is the α of the next; a β must re-enter the alternative that last took γ, so that alternative is recorded.
6. A deterministic box answers β with ω.
7. The clauses a call sees are fixed when it is called.
8. A cut succeeds once and discards every choice up to and including its predicate's.

## 2. THE LAW: goal-directed evaluation is boxes

- **Every decision of control is a box's own code.** Which clause is tried, whether a head unifies, which alternative is next, whether a goal is redone, which of γ and ω is taken: each is an instruction of the emitted chunk (or of the one unify leaf it calls), never the return value of a C function that looked and decided.
- **C serves values.** A runtime call from a box is legal only as a value service: it computes a value from values and returns to the instruction after the call (text, a number, a copy of a term, the i-th member of a table, the candidate after this one, an I/O effect). It unifies nothing with the caller's variables, pushes nothing on the trail, and enters no box.
- **No C function enters a box** (CEO-1576; skill `runtime-calls`). MEASURED 2026-11-13 with `SCRIP_C2BB_TRACE` on eleven Prolog programs covering meta-call, findall, negation, catch, the database, tabling, sorting by a predicate and coroutines: 0 entries.
- **One unifier.** Emitted unification and the asm leaf `rtx_pl_unify` are the unifier. A builtin returns its result as a value and the box unifies it.
- **The test of a layout**: write its α and β and the γ and ω of each sub-goal in the notation of section 3. If a line needs the words "the runtime then decides", the construct is not yet a box.
- Lon's standing words: "give Prolog its activation ZETA like all the rest" (2026-09-02); "The Prolog unification needs to mirror SNOBOL4's pattern matching, using R13, R14, and R15, and also R12 as a stack." (2026-09-26, CEO-1279).

## 3. THE LAYOUTS: every Prolog construct as α, β, γ, ω

Notation (Proebsting's attribute discipline in Lon's port names). For a construct C: `C.α` and `C.β` are C's own entries (synthesized: C writes them). For each sub-goal G of C: `G.γ` and `G.ω` are what C wires G's exits to (inherited: the parent writes them). A bare `γ` or `ω` is C's own exit, which C's parent wires. `→ X` is a jump; `→ [gate]` is a jump through a cell written at run time. The state every Prolog box shares: `TR` the trail top (r12), `B` the youngest choice (the cut barrier, r13), the ball (r15). `m ← TR` marks the trail; `unwind(m)` undoes every binding pushed since. A cell named in a layout (m, b, gate, i, c, g, q) is a word of the box's own cell on the spine or in its frame.

Two rules hold in every layout. (1) A box whose γ leaves no way to produce another answer is BOUNDED: its β is `→ ω` and it leaves no choice behind. (2) Bindings are undone on the way back by the box that holds the mark: the trail is unwound to it. The formal models write the same event as a leaf popping its own binding at redo.

### 3.1 The constants
```
true        α: → γ                      β: → ω
fail        α: → ω                      β: → ω
repeat      α: → γ                      β: → γ
```

### 3.2 Conjunction and disjunction
```
(A , B)     α: → A.α                    β: → B.β
            A.γ: → B.α                  A.ω: → ω
            B.γ: → γ                    B.ω: → A.β

(A ; B)     α: m ← TR; gate ← A.β; → A.α            β: → [gate]
            A.γ: → γ                    A.ω: unwind(m); gate ← B.β; → B.α
            B.γ: → γ                    B.ω: → ω
```
Byrd's chain of boxes is the conjunction: the γ of one goal is the α of the next and the ω of a goal is the β of the one before. The disjunction's β is a run-time port, as Proebsting's `if`.

### 3.3 If-then-else, soft cut, negation, once
```
(I -> T ; E)    α: m ← TR; b ← B; → I.α             β: → [gate]
                I.γ: B ← b; gate ← T.β; → T.α       I.ω: unwind(m); gate ← E.β; → E.α
                T.γ: → γ      T.ω: → ω              E.γ: → γ      E.ω: → ω
(I -> T)        the same with E = fail:             I.ω: unwind(m); → ω

(I *-> T ; E)   α: m ← TR; seen ← 0; → I.α          β: seen ? → T.β : → E.β
                I.γ: seen ← 1; → T.α                I.ω: seen ? → ω : (unwind(m); → E.α)
                T.γ: → γ      T.ω: → I.β            E.γ: → γ      E.ω: → ω

\+ G            α: m ← TR; b ← B; → G.α             β: → ω
                G.γ: B ← b; unwind(m); → ω          G.ω: unwind(m); → γ

once(G)         α: b ← B; → G.α                     β: → ω
                G.γ: B ← b; → γ                     G.ω: → ω
ignore(G)       once(G) with                        G.ω: → γ
forall(C, A)    \+ (C, \+ A)
```
`B ← b` discards every choice the condition left: `I.β` and `G.β` are never wired. The soft cut keeps the condition's choices: `T.ω` goes back into `I.β`.

### 3.4 The cut
```
!   in a clause of P    α: B ← P.b; → γ             β: → P.ω
```
`P.b` is the barrier P saved at its α. The cut discards the clause alternatives of P and every choice left by the goals before it, so its β is P's own ω, never the β of the goal before. A cut is TRANSPARENT through `,` `;` and the then and else branches (it cuts P). It is LOCAL (opaque) inside the condition of `->` and `*->`, `\+`, `once`, `call/N`, the goal of `findall`, `bagof`, `setof`, `forall`, and the goal of `catch`: there it cuts to that construct's own `b`.

### 3.5 A predicate, its clauses, a fact
```
P(a1..an)  static, candidates C1..Ck chosen by the index over the arguments
            α: P.b ← B; m ← TR; i ← first; → C_i.α  β: → C_i.β
            C_i.γ: → γ                              C_i.ω: unwind(m); i ← next(i); i ? → C_i.α : → ω

H :- G      α: the head's unifications in order, each one's ω the clause's ω; → G.α
            β: → G.β          G.γ: → γ              G.ω: → ω
H.          α: the head's unifications; → γ         β: → ω
```
P stays resumable while the current clause's body holds a choice or a later candidate exists. The last candidate takes no mark and leaves no choice: its ω is P's ω, and when its body is bounded P's β is `→ ω`. The index (first argument or any argument, skill prolog-engine section 7) only narrows the candidates; it never changes the order of the answers.

### 3.6 Unification and the deterministic builtins
```
X = Y       α: unify, each binding pushed on the trail; equal ? → γ : → ω        β: → ω
X \= Y      \+ (X = Y)
b(args)     α: v ← the value service; unify the outputs; → γ, or → ω, or raise    β: → ω
```
`b` is any builtin with at most one answer: `is/2`, the comparisons, the type tests, `functor/3`, `arg/3` with a bound index, `=..`, `copy_term/2`, `assertz/1`, `write/1`, `atom_codes/2` in a determinate mode. The service computes a value and decides nothing; the box unifies the value and takes the exit. An error is a ball: the box arms it and takes ω (3.9).

A unification that binds a variable carrying suspended goals W (`freeze/2`, `dif/2`, `when/2`, a constraint) runs them as a conjunction after it: `X = Y` then has `γ: → W.α`, `W.γ: → γ`, `W.ω: → ω`, `β: → W.β`.

### 3.7 The generators
```
between(L, H, X)    α: i ← L; → code                β: unwind(m); i ← i + 1; → code
                    code: i > H ? → ω : (m ← TR; X = i ? → γ : → β)
```
This is Proebsting's `to`. Every builtin with several answers has this shape, a state cell stepped at β and a `code` chunk that unifies or steps again: `clause/2`, `retract/1`, `current_op/3`, `sub_atom/5`, `atom_concat/3` with an unbound prefix, `nth0/3` and `nth1/3` with an unbound index, `select/3`, `member/2` (which is two clauses and needs no template of its own). The enumeration is the box's; the runtime answers only "the i-th value".

### 3.8 Meta-call and the collectors
```
call(G, x1..xk)     α: g ← G with x1..xk appended; e ← the entry of g's functor; b ← B; → [e].α
                    β: → [e].β
                    [e].γ: → γ                      [e].ω: → ω

findall(T, G, L)    α: m ← TR; b ← B; q ← empty; → G.α                  β: → ω
                    G.γ: add a copy of T to q; → G.β
                    G.ω: unwind(m); L = the list of q ? → γ : → ω

bagof(T, G, L)      findall of Witness-T, sort by witness, then a generator over the groups:
setof(T, G, L)      β: step to the next group; setof sorts each group and drops duplicates.
aggregate_all(count, G, N)   findall's layout with a counter for q.
```
`e` is found from the functor's own identity in the procedure table; a goal that is a control term (`,` `;` `->` `\+`) is compiled once into a box of its own and then entered the same way. `[e].α` and `[e].β` are run-time ports. `findall` is Proebsting's `every`: each answer's γ goes straight back into the goal's β. Copying the template is a value service; adding to q and building L are the box's.

### 3.9 catch, throw, cleanup
```
throw(Ball)         α: ball ← a copy of Ball; → ω   β: none

catch(G, C, R)      α: m ← TR; b ← B; d ← the spine depth; gate ← G.β; → G.α     β: → [gate]
                    G.γ: → γ
                    G.ω: no ball ? → ω
                         : unwind(m); B ← b; restore d; (ball = C) ? (drop the ball; gate ← R.β; → R.α) : → ω
                    R.γ: → γ                        R.ω: → ω

setup_call_cleanup(S, G, C)   once(S), then G under a record that runs C exactly once: when G takes ω, when a ball
                              passes G's ω, when G takes γ leaving no choice, or when G's choices are cut.
```
An armed ball travels ω by ω, and while it is armed EVERY β IS ω: a conjunction's `B.ω: → A.β` hands the ball to A, whose β passes it straight on to A's ω, so a ball never resumes a goal and never re-enters a retained frame. Only a `catch` whose goal G is running tests it, at `G.ω`; a `catch` reached at its own β by a ball raised after it exited passes it on like any box. The catcher is unified after the trail is unwound to the catch's mark, so the bindings G made are gone and the ball, being a copy, is not.

### 3.10 The dynamic database
```
P(a1..an)  dynamic  α: P.b ← B; g ← the generation; c ← the first candidate of the index; → code
                    β: body live ? → c.β : (unwind(m); c ← next(c); → code)
                    code: c = none ? → ω
                          c not alive at g ? (c ← next(c); → code)
                          m ← TR;
                          c a fact ? (head(c) = (a1..an) ? → γ : → β)
                          c a rule ? → c.α              c.γ: → γ      c.ω: → β

assertz(C) asserta(C) retractall(H) abolish(PI)     deterministic builtins (3.6); each advances the generation.
retract(C)          the generator of P over the clauses that match C's head; after the unification of head and
                    body succeeds, the candidate is erased and the box takes γ; β steps on.
clause(H, B)        the same generator; γ after H and B unify with the candidate.
```
The logical update view is the cell g: a call sees the clauses alive at the generation it started in, whatever is asserted or retracted while it runs. A fact's head is unified by the same unifier every other box uses, against the stored term (a ground fact is shared, a fact with variables is renamed first). A rule is its own clause box, compiled once when it is asserted. The store answers "the next candidate after c"; it selects nothing and unifies nothing.

### 3.11 Tabling, coroutines, grammar rules
```
P tabled            α: v ← the variant of the call in the table
                       v complete ? a generator over v's answers (β: the next answer)
                       v new ?      P's own clauses run as the producer; each answer's γ adds it to v and wakes v's consumers
                       v running ?  the call is a consumer: it suspends at ω until the producer adds an answer
```
The scheduling of producers and consumers is skill prolog-tabling; what this page fixes is that an answer returned from a complete table is a generator box like `between/3`, and that a tabled clause body is the same clause box as an untabled one.

A woken goal is the conjunction of 3.6. `reset/3` and `shift/1` are coroutine switches on the generator-procedure road (skill prolog-engine section 4).

A grammar rule is no box. `H --> B` is translated to the clause `H(S0, S) :- B'` with two more arguments before lowering, and `phrase(G, L, R)` is `call(G, L, R)`.

### 3.12 What a layout never contains
A C function that picks a clause, unifies a head, walks a choice, runs a goal or decides which exit is taken. A value service returns a value to the box (text, a number, a copy, the i-th member, the next candidate) and returns to the instruction after its call; the box does the unification and takes γ or ω itself.

## 4. SCRIP's names for the parts of a layout

| In a layout | In SCRIP |
|---|---|
| α, β, γ, ω | the four ports of an IR node and of its template under `src/templates/bb/`; an edge is γ→α, ω→β, γ→β or to a parent's exit |
| a box's cells (m, b, gate, i, c) | the words of the node's cell: on the spine, or in the activation frame when no fixed distance reaches them (skill `scrip-memory-model`) |
| TR, `unwind(m)` | r12, the trail top; entries undone back to a mark (skill `prolog-engine` section 2) |
| B, `B ← b` | r13, the choice and cut barrier; a fence saves and restores it |
| the ball | r15 and the trail header's ball slot; it travels ω by ω to the innermost catch |
| conjunction | no node: the γ and ω wiring of consecutive goals |
| disjunction | `IR_DISJUNCTION` |
| if-then-else and its gate | `IR_GATE`, `IR_GATE_ARM` |
| the fence of once, `\+`, the condition, findall's goal | `IR_BOUND` at entry, `IR_UNMARK` at the commit or the discard |
| cut | `IR_CUT` |
| a predicate call | `IR_CALL_PROC_STAGED`; the clause step and its index switch are the callee's entry |
| head unification | `IR_UNIFY_CONST`, `IR_UNIFY_STRUCT`, `IR_UNIFY_VALUE`, `IR_UNIFY_FIRST` |
| a deterministic builtin | `IR_CALL` of a `$` leaf through the builtin table (`bb_call_pl_leaf.cpp`) |
| a generator | `IR_TO`, `IR_TO_BY` |
| meta-call | `IR_CALL_VALUE` (`bb_call_value.cpp`) |
| a table | `IR_TABLE_HDR` |
| cleanup | `IR_CLEANUP` |

## 5. Where SCRIP's Prolog stands against the law (MEASURED 2026-11-13, SCRIP 3eb173ee0)

Shares of user instructions in mode 4 binaries (`perf record -e instructions:u`, classed by `prof.py`; the programs, the tool and the table are `/home/resources/postoffice/escalations/prolog-boxes-not-c/`):

| The program exercises | emitted boxes | C runtime and libc | the unify leaf, the allocator, the collector |
|---|---|---|---|
| pure clauses (browse; a DCG parser) | 72 to 76 | 2 to 5 | 20 to 27 |
| negation and if-then-else | 61 | 13 | 25 |
| a `between/3` loop with global variables | 40 | 38 | 22 |
| `maplist/3` | 28 | 46 | 26 |
| `findall/3` | 27 | 39 | 33 |
| `catch/3` and `throw/1` | 27 | 56 | 17 |
| `call/N` | 20 | 66 | 14 |
| calls of asserted facts | 9 | 78 | 14 |
| tabling | 8 | 52 | 41 |
| the sieve benchmark (assert and retract) | 3 | 96 | 1 |

The skeleton is boxes and no C enters one; but outside pure clause resolution a box is a shell around C. The dynamic database is a C interpreter (the candidate is picked and its head unified by `rt_pl_db_cand_next`, `rt_pl_db_data_unify` and a second, C unifier: 5,388 instructions for one call of an indexed asserted fact). Meta-call formats a "name/arity" string and hashes it at every call. A ground literal is rebuilt at every pass. The collectors, the catcher and the tables copy and match in C. The programme that brings each to its layout of section 3, on Lon's word that day ("do all as you suggest."), is skill `prolog-engine` section 8; each step is proved by this table's instrument falling and by the answers unchanged against swipl.

## 6. The sources (reference.md)

§ 1 Byrd 1980 and the DEC-10 manuals, his definitions quoted by line. § 2 Proebsting 1997 and 1999 and Danvy 2001: the four-chunk translation, every template, the optimisation, Jcon. § 3 the formal models: Kulaš's 21 rules, Deransart's observational semantics, Jahier's continuations, and where they disagree. § 4 the systems' ports beyond four (unify, exception, the debugger manuals) and the trace analysers. § 5 the implementation models: Carlsson's continuations, the WAM, BinProlog, the semantics of cut, and what the manuals fix for call/N, catch and the database. § 6 Lon's seeds: `test_icon.c` and `test_sno_1.c` to `test_sno_4.c`, and the layouts of the SNOBOL4 pattern primitives and of Icon's operators read from them.
