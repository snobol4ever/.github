# DESIGN — Byrd Boxes for ALL of Prolog (Proebsting-pure)

Four ports. Closure resume. No fifth/sixth port. No WAM, no bytecode, no C control engine.
The boxes **are** the engine. SWI/GNU is out of our head.

Canon: Proebsting, *Simple Translation of Goal-Directed Evaluation* (`SCRIP/bench/...pdf`).
Reference implementation: JCON `tran/irgen.icn` (the `ir_a_*` four-port wiring) + `jcon/vClosure.java`.

---

## 0. The only primitives

Every construct compiles to **four code chunks** — Proebsting's ports, our Greek names:

| port | Proebsting | direction | meaning |
|------|-----------|-----------|---------|
| **α** | start   | synthesized (up)   | fresh-solve entry: produce the FIRST solution |
| **β** | resume  | synthesized (up)   | redo entry: produce the NEXT solution |
| **γ** | succeed | inherited (down)   | success continuation (where to go on a solution) |
| **ω** | fail    | inherited (down)   | failure continuation (where to go when exhausted) |

Control threading is **`goto`/`call` connecting a node's own four ports and its children's
own four ports** — and nothing else. A parent never grows a port to name a child's entry; it
branches to the child's existing α/β. (This is the whole content of the four-ports FACT RULE.)

### Five laws that fall out of the model

1. **Determinacy is first-class (`bounded`).** A box that cannot offer a second solution emits
   **no β chunk** — no redo entry, no choice point, no retained state. β exists *only* for
   genuine generators. (JCON F1: every `ir_a_*` guards its resume with `/bounded`.) This is the
   single highest-leverage idea and the thing the WAM "always push a CP" mindset hides.

2. **Callee resumability is a CLOSURE VALUE, never a port.** Entering a predicate is a **call**
   that yields a closure `(value, Resume)`; re-driving it is **resuming that closure** — a runtime
   value operation, dispatched from the *caller's own β chunk*. The closure in SCRIP **is the
   callee's frame** (the `rt_enter` cell block) plus its trail/CP marks. (JCON `ir_a_Call` +
   `vClosure`.) There is no "callee-entry port" and no "callee-resume port"; one is a call opcode's
   target, the other is `closure.Resume()`.

3. **Trail = ONE shared spine.** A box that may bind marks the trail at α; on backtrack (its β, or
   the enclosing choice's retry) the trail unwinds to the mark. No per-box undo logs.

4. **Cut = commit.** Prune the choice-point ledger back to a barrier captured at clause entry.
   Lexically a cut is pure **wiring** (subsequent failure bypasses the clause alternatives);
   dynamically it reads a **frame-local gate**. Never a control opcode.

5. **No value stack.** A producer's result is read by its consumer directly from the producer's
   **frame cell** `[ζ=r12+off]`; operand constants are `[rip+disp]`. Nothing is pushed/popped.

### Machine model (from the register convention)

- **r12 = ζ** = the box-local RW frame base; every box-local is `[r12+off]`, cells at
  `GZ_CELL_OFF(slot) = 8 + 8*slot`. Logic variables are cells.
- **verdict in rax**: success/fail returns in `rax` (`test eax,eax; jne γ; jmp ω`); a successful
  value is packed alongside.
- **C call stack = the sanctioned recursion spine.** A predicate call is a real subroutine call
  (args in `rsi/rdx/rcx`, frame ptr in `rdi`); recursion and the closure-resume ride the hardware
  call stack. There is no software CP-stack interpreter.
- **Terms** are built by `rt_*` value helpers into frame cells — never a WAM S-pointer
  structure-copy mode, never reading IR/AST at runtime.

---

## 1. The control boxes (four-port templates)

Notation is Proebsting's: `port : goto target`. `child.α`/`child.β` are the **child's own**
ports. "resume CLO" = resume the callee closure (re-enter the callee continuing from its last
choice point, the resume entry carried by its frame — the callee's own β).

### 1.1 Leaf goal — `true`, a fact head that matches deterministically
```
G.α : succeed once            ; goto G.γ
G.β : —                       (bounded: a matched fact offers one solution)
```
`fail/0` is the dual: `G.α : goto G.ω`.

### 1.2 Unification — `X = Y` (bounded, trailing)
```
U.α : mark ← trail_top ; if unify(X,Y) goto U.γ ; goto U.ω
U.β : —                       (deterministic: the enclosing choice unwinds `mark` on retry)
```
`unify` binds through the trail. One solution ⇒ no β; the undo happens at the nearest choice
point's retry, which unwinds the shared trail past `mark`.

### 1.3 Conjunction — `(A , B , C)`  *(JCON `ir_conjunction` / arg-sweep of `ir_a_Call`)*
```
seq.α : goto A.α
A.γ   : goto B.α              # A succeeds → start B FRESH
B.γ   : goto C.α
C.γ   : goto seq.γ
C.ω   : goto B.β              # C exhausted → REDO B (backtrack into the generator)
B.ω   : goto A.β              # B exhausted → REDO A
A.ω   : goto seq.ω            # first goal exhausted → conjunction fails
seq.β : goto C.β              # resume conjunction = resume the LAST goal
```
Pure four-port threading; every edge names a child's own port. If a goal is `bounded`, its `.β`
is dead, so the backtrack edge into it collapses to its `.ω` (straight-line — the determinacy win).

### 1.4 Clause choice — predicate with clauses `H1 ; H2 ; H3`  *(JCON `ir_a_Alt` → `IR_CHOICE`)*
```
choice.α : mark ← trail_top ; cur ← 1 ; goto H1.α
H1.γ     : goto choice.γ
H1.ω     : unwind(mark) ; cur ← 2 ; goto H2.α     # clause exhausted → next clause
H2.γ     : goto choice.γ
H2.ω     : unwind(mark) ; cur ← 3 ; goto H3.α
H3.γ     : goto choice.γ
H3.ω     : unwind(mark) ; goto choice.ω           # all clauses exhausted → fail
choice.β : goto [cur-resume]                       # resume = resume the clause that succeeded
```
`cur` is a **frame gate** (which clause are we in) because the succeeding clause isn't known at
compile time — Proebsting's indirect goto. The CP ledger records this choice so a later failure
returns to `choice.β`. A `bounded` (single-clause, or cut-committed) predicate emits no `choice.β`
and no ledger entry.

### 1.5 Predicate call — `P(args)`  *(JCON `ir_a_Call` — the closure)*
```
call.α : eval args → cells ; CLO ← enter_callee_frame ; CALL callee.α
       : if success: target ← value(CLO) ; goto call.γ
       : if fail:    goto call.ω
call.β : resume CLO                                # closure.Resume(): callee continues from its CP
       : if success: target ← value(CLO) ; goto call.γ
       : if exhausted: goto call.ω
```
`callee.α` is the **callee's own α**, reached by a call opcode. `call.β` performs a
**closure-resume** — it re-enters the callee (via the C call stack) so it resumes from its last
choice point; the resume entry is the callee's own β, carried by `CLO` (its frame). If the callee
is `bounded`, `call.β` is absent and no closure is retained — the call is a plain subroutine call.

### 1.6 Cut — `!`
```
cut.α : commit(barrier) ; goto cut.γ      # barrier = clause-entry CP marker (frame-local)
cut.β : goto cut.ω                          # redo past a cut fails — the alternatives are gone
```
`commit(barrier)` pops the CP ledger back to the barrier captured at the clause's α, so subsequent
backtracking cannot revive cut-away clauses or earlier in-body choice points. Lexically this is
**wiring** (the clause-choice `.β` becomes unreachable past the cut); the barrier value lives in a
frame cell.

### 1.7 If-then-else — `(Cond -> Then ; Else)`  *(Proebsting §4.5 `ifstmt` — the gate)*
```
ite.α  : goto Cond.α
Cond.γ : gate ← &Then.α ; commit(Cond CPs) ; goto Then.α   # Cond succeeds ONCE (soft cut) → Then
Cond.ω : gate ← &Else.α ; goto Else.α                       # Cond fails → Else
ite.β  : goto [gate]                                         # resume = whichever arm we entered
Then.γ : goto ite.γ      Then.ω : goto ite.ω
Else.γ : goto ite.γ      Else.ω : goto ite.ω
```
`gate` (a frame cell) holds the runtime resume target. `commit(Cond CPs)` at `Cond.γ` is the
`->` soft cut: the condition is solved once. `(Cond -> Then)` without else routes `Cond.ω → ite.ω`.

### 1.8 Disjunction in a body — `(A ; B)`  *(2-way `ir_a_Alt`)*
```
disj.α : mark ← trail_top ; goto A.α
A.γ    : goto disj.γ
A.ω    : unwind(mark) ; goto B.α
B.γ    : goto disj.γ
B.ω    : unwind(mark) ; goto disj.ω
disj.β : goto [gate]                # which branch succeeded (frame gate)
```

### 1.9 Negation as failure — `\+ G`  (bounded)
```
neg.α : mark ← trail_top ; CLO ← enter G ; CALL G.α
      : if G succeeds → commit(G CPs) ; unwind(mark) ; goto neg.ω    # provable → \+ fails
      : if G fails    → unwind(mark) ; goto neg.γ                    # unprovable → \+ succeeds once
neg.β : goto neg.ω                                                   # deterministic
```
Drives the G closure for its FIRST solution only, flips the verdict, discards G's bindings either
way. `once(G)` and `forall(C,A)` are the same shape (drive a closure to its first / to exhaustion).

### 1.10 findall / aggregate — `findall(Tmpl, Goal, List)`  (closure-driven, bounded)
```
fa.α  : acc ← begin()
      : CLO ← enter Goal ; CALL Goal.α
fa.L  : if Goal failed → goto fa.fin
      : collect(acc, deep_copy(Tmpl))      # VALUE work, rt_* on Term* only
      : resume CLO                          # closure.Resume(): next solution
      : goto fa.L
fa.fin: if unify(List, finish(acc)) goto fa.γ ; goto fa.ω
fa.β  : goto fa.ω                            # one List ⇒ bounded
```
This is `IR_CELL_FINDALL`, correctly understood: the loop's "next solution" is a **closure-resume**,
not a port branch. `aggregate_all/3` is the same box with a reducing `finish` (count/sum/max/min).
`bagof`/`setof` add free-variable grouping/sort on top of the same drive loop.

---

## 2. The deterministic-builtin family — ONE recipe

`is/2` · `=:= < > =< >= =\=` · `== \== @< @=< @> @>=` · `var nonvar atom number integer atomic
compound callable is_list ground` · `functor/3 arg/3 =../2 copy_term/2` · `atom_length atom_codes
atom_chars atom_concat atom_number atom_string char_type` · `write writeln print writeq
write_canonical nl format` · `succ/2 plus/3` · `msort sort` · `atomic_list_concat / concat_atom`
· `nb_setval nb_getval` · `string_*`.

All share ONE shape — a **bounded** box (no β):
```
det.α : <load operand cells> ; r ← rt_pl_<op>(cells) ; test r ; jne γ ; jmp ω
det.β : —                                            (bounded — no redo)
```
The VALUE work is a **single `rt_*` call** on `Term*`/`DESCR_t` (never IR/AST). Success/fail in
`rax`. These are the bulk of Prolog and they are the *same box* modulo the `rt_*` callee — that is
the "write each piece of logic once" rule. Admission recipe per builtin is mechanical (`IR_DET_*`
kind, name-table entry, `rt_pl_<op>_cell`, the four-port `bb_det_<op>.cpp`, dispatch + lower arms).

---

## 3. Dynamic database

- **`assert / asserta / assertz`** — bounded; `rt_pl_assert_*` adds a clause record. No β.
- **`abolish / retractall`** — bounded; bulk removal. No β.
- **`retract(Clause)`** — a **generator over the DB** (semidet→nondet); it HAS a β:
```
ret.α : cursor ← first matching clause ; if found: bind + mark ; goto γ ; else goto ω
ret.β : unwind(mark) ; cursor ← NEXT matching clause ; if found goto γ ; else goto ω
```
  `cursor` (which clause) is the frame value — the closure for the DB scan.

---

## 4. Exceptions — `catch/throw`

- **`throw(Ball)`** — unconditional: unwind trail + CP ledger up to the nearest catch frame whose
  catcher unifies with `Ball`, then enter that frame's recovery α. A **non-local ω** (failure
  direction), routed by a runtime frame search — not a port, not a control opcode.
- **`catch(Goal, Catcher, Recovery)`** — pushes a catch frame (frame cell: catcher pattern +
  `&Recovery.α` + trail/CP marks) at α; runs Goal as a closure; a matching `throw` lands at
  `Recovery.α` with bindings unwound to the catch mark.
```
catch.α  : push_catch(Catcher, &Recovery.α, marks) ; goto Goal.α
Goal.γ   : pop_catch ; goto catch.γ
Goal.ω   : pop_catch ; goto catch.ω
catch.β  : goto Goal.β                       # re-drive a nondeterministic Goal
Recovery.α (entered via throw) : … ; Recovery.γ → catch.γ ; Recovery.ω → catch.ω
```

---

## 5. DCG / `phrase`

`phrase(NT, L)` / `phrase(NT, L, R)` need **no new box**. DCG is a **lowering** step: a rule
`H --> B` becomes an ordinary clause of arity+2 threading a difference list `(S0, S)`; `phrase/2,3`
is then a plain **predicate call** (§1.5) with the list args supplied. At the BB layer it is
clause-choice + conjunction + unify. Nothing new.

---

## 6. What is EXCISED (SWI/GNU out of our head)

| WAM / bytecode mindset | Byrd-Box reality |
|---|---|
| Central choice-point **stack** + a `fail → pop CP → dispatch` engine loop | CP state lives in per-callee **closures (frames)**; the trail is the one shared spine; backtracking is the **ω/β wiring**. No engine loop. |
| **Bytecode** + fetch-decode-execute interpreter | The **boxes are the program** — direct/indirect jumps (Proebsting). No opcode dispatch. |
| C **control engine** / meta-rail (`resolution.c`, `rt_meta_solve`) | Meta-goals (findall, `\+`, once, forall, aggregate) drive a callee **closure** via the four-port wiring + `rt_*` **value** helpers. `IR_CELL_FINDALL` is the template. |
| WAM **register machine** ABI (A/X regs, S-pointer structure mode) | Terms built by `rt_*` into **frame cells**; args pass in SysV regs to callee α. |
| "Always push a choice point," determinacy discovered late | **`bounded` is first-class at lower time**: deterministic boxes have no β, no CP, no trail churn (JCON F1). |
| AST/IR walked at runtime | **Nothing** reads AST/IR during run; the compiler reads IR once to emit, then it is freed. `rt_*` see only `Term*`/`DESCR_t`. |

---

## 7. The linchpin — a `bounded` flag at lower time

Mirror JCON exactly: the lowerer tags every goal `bounded` iff it cannot offer a second solution
(deterministic builtin; single-clause head; body whose last choice is cut-committed; `\+`, `once`,
findall, `is`, comparisons, type tests, I/O). **Bounded ⇒ no β chunk, no choice point, no retained
closure.** This confines the four-port choice/closure machinery to genuine generators (multi-clause
predicates, `retract`, `member`-style recursion, `between`, findall's inner goal) and turns the rest
of Prolog into straight-line code. It is the structural fix for backtracking correctness AND the
enabler of CP elision — and it is the discipline the old SWI/GNU engine mindset obscures.

---

## 8. Build order (each rung independently gated: GATE-1 5/5/5 hard, ratchet floor)

1. **`bounded` flag in `lower_prolog.c`** — tag determinacy; bounded goals stop emitting β.
2. **Closure-resume as the call β** — `call.β` resumes the callee closure (callee's own β via the
   frame), retiring the caller-side resume-port notion entirely.
3. **Choice/conjunction/cut/ITE/disj** — the §1 control templates, gate cells for the indirect
   resumes (`cur`, `gate`), CP ledger + barrier for cut/`->`.
4. **The det-builtin family** — already largely landed; complete the recipe coverage.
5. **Meta family** — findall (landed) → aggregate sum/max/min → `\+`/once/forall, all closure-driven.
6. **Dynamic DB** (retract as a DB-cursor generator) → **catch/throw** (catch-frame search) →
   **DCG** (pure lowering).

Throughout: four ports only; callee resumability is a closure value; no fifth/sixth port; the
boxes are the engine.

---

## 9. STACKLESS — the value stack moved INTO the box (re-derivation, 2026-06-13)

SNOBOL4 and Icon are **stackless**: goal-directed control is jumps between four ports, and the
"external value stack" is placed INSIDE each Byrd Box as STATIC frame slots. **There is no control
stack and no value stack.** The single hardware stack (the C call stack) is touched only for (a)
calls into the C runtime `rt_*` helpers and (b) the predicate-call closure-resume `call δ`/`call ε`.

**Verified in-tree (not asserted):** `grep g_vstack src/ = 0`; zero `rt_push`/`rt_pop` in any
`bb_cell_*.cpp`; no choice-point-stack in the GZ runtime. State lives in `[r12+GZ_CELL_OFF(slot)]`.

**The canonical proof — the ARBNO box** (`SCRIP/bench/test_sno_1.c`). ARBNO (`*P`, match a
sub-pattern zero-or-more times) is the ONE construct that genuinely needs unbounded depth, because
each repetition backtracks independently. The naive WAM/Icon answer is a runtime stack of generator
frames (push per repetition, pop on backtrack). Here that stack is a **flat indexed frame array**:
```c
typedef struct _1 { str_t ARBNO; str_t alt; int alt_i; } _1_t;
_1_t _1[64];  _1_t *ζ = &_1[0];          /* the "stack" = box-local indexed frame + cursor */
ARBNO_α: ζ = &_1[ARBNO_i=0]; ...         /* depth 0                                        */
ARBNO_β: ζ = &_1[++ARBNO_i]; ...         /* "push" = advance index → fresh row             */
alt_ω:   ARBNO_i--; ζ = &_1[ARBNO_i]; goto alt_β;  /* "pop" = retreat index → resume row   */
```
Each depth gets its OWN row holding that repetition's value (`ARBNO`), alternative (`alt`), and
resume cursor (`alt_i`). NOTHING is destructively saved-and-restored — backtracking just moves `ζ`
back to a row that still holds its values intact. **That is the value stack turned inside-out and
frozen into the box as a PURE-FUNCTIONAL indexed frame:** control stays the four ports threaded by
`goto`; the only stack-like thing is an integer cursor (`ARBNO_i`) into a box-local array. The one
construct that *looks* like it needs a stack proves it doesn't.

### How each WAM/SWI "stack" dissolves

| WAM/SWI baggage | what it actually was | stackless replacement |
|---|---|---|
| Choice-point **stack** (B-chain) | "what to try on failure" | **ω wiring** (compile-time: clause k.ω → clause k+1.α) + a frame **cursor cell** for runtime-chosen resume |
| Environment **stack** (E-chain) | active-call locals + return | **C call** per activation; locals are **frame cells** |
| Argument/operand **value stack** | pass a computed value to consumer | producer **writes its frame cell**, consumer **reads it** — static offsets, no push/pop |
| Generator-frame **stack** (old Icon bytecode) | suspend/resume a generator | **α/β ports** + a **gate cell** (indirect goto) |
| **Trail-mark** snapshot stack | saved unwind points | an **integer in the box's own frame cell** (`mark_slot`) |
| Bytecode + fetch-decode-execute | the VM interpreter loop | **the boxes are the program** (direct/indirect jumps) |
| `setjmp`/`longjmp` exception-frame **stack** | non-local unwind to catcher | **catch-frame cells** + non-local **ω** chain search |
| meta-rail / "nearest resumable predecessor" | runtime backtrack-target search | the callee closure's **own β** via `call ε` |

---

## 10. DATA STRUCTURES NOT USED — the stacks the four-port model eliminates

Every one is a control stack or value stack wrongly imported from WAM/SWI. None survives.

| # | structure NOT used | what it was in WAM/SWI | why unnecessary |
|---|---|---|---|
| 1 | **Choice-point stack** (B-chain, parent-linked CP frames) | the backtracking control stack | failure target is the **ω port**, wired at compile time; runtime-chosen resume is a **frame cursor cell** |
| 2 | **Environment stack** (E-chain, `localFrame` chain) | active-call locals + return | **C call** per activation; locals are **frame cells** |
| 3 | **Argument/operand value stack** (A-reg save/restore; Forth-style operand stack; old SNOBOL4 value stack) | passing computed values between ops | producer **writes its cell**, consumer **reads it** — static slot offsets |
| 4 | **Generator-frame stack** (old Icon bytecode's pushed/popped generator frames) | suspend/resume generators | **α/β ports** + **gate cell** |
| 5 | **Trail-mark snapshot stack** | saved unwind points | an **integer in the box's frame cell** |
| 6 | **Bytecode + fetch-decode-execute dispatch** | the VM interpreter loop | **the boxes are the program** |
| 7 | **`setjmp`/`longjmp` exception-frame stack** (SWI `exception_frame` chain) | non-local unwind to catcher | **catch-frame cells** + non-local **ω** chain search |
| 8 | **Meta-rail engine** (`rt_meta_solve`, "nearest resumable predecessor") | runtime backtrack-target search | the callee closure's **own β** via `call ε` |
| 9 | **WAM register bank** (X/A regs, S-pointer structure-copy mode) | term build/match working store | terms built by `rt_*` into **frame cells**; args in SysV regs |
| 10 | **Per-engine duplicated stack set** (for the deferred engines feature) | isolated execution contexts | replicate trail+heap+frames; **no shared control stack to duplicate** |

**What survives is exactly four things** — and only one is Prolog-specific:
- **Trail** — the ONE shared binding-undo log (a callee's bindings are undone by a caller's
  backtrack, so it must be shared; DESIGN §3 law 3). Not a control stack, not operand-passing.
  SNOBOL4/Icon lack it (no unification); Prolog adds exactly this one spine and nothing else.
- **GC heap** — term storage (`Term*`). A heap, not a stack.
- **Frame cells** `[r12+off]` — the value stack turned inside-out: a flat per-activation array
  indexed by compile-time slots. No push/pop.
- **C call stack** — subroutine calls into `rt_*` and the closure-resume only.

**DEFERRED (optimizations, none a stack):** per-type first-arg hash index; birth-stamp/mark-bar
(conditional trailing); gprolog's double-linked clause chains (we need *a* clause store, not *that*
one). **FRONTIER (if built, heap structures with frame-cell handles, still not engine stacks):**
answer trie / worklist / SCC graph (tabling); attvar chain + wakeup queue (coroutining); constraint
store + propagation queue (CLP); continuation capture (delimited control — the one genuinely hard
case, because recursion rides the C call stack, so it needs the `Create`/`CoRet`/`CoFail`
co-expression substrate); per-engine state replication (engines).
