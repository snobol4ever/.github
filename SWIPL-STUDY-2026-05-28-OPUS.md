# SWIPL Architecture Study — Prolog Done Right (2026-05-28, Opus 4.7)

Study of SWI-Prolog `swipl-devel-master` (`src/pl-data.h`, `pl-vmi.c`, `pl-wam.c`,
`pl-incl.h`, `pl-index.c`) vs our SCRIP Prolog implementation. Purpose: learn the
real WAM model so our BB/SM/XA emission converges on it instead of reinventing it
badly. **This is a learning/orientation doc — no code changed.** CAT-A-3 B–C work
stashed (`git stash@{0}`) pending decision on whether to land it or pivot to the
model below.

---

## The seven load-bearing ideas in SWIPL (and where we are)

### 1. Tagged words, not boxed pointers  (`pl-data.h`)

SWIPL: every Prolog value is ONE machine `word`. Low 3 bits = tag
(`TAG_VAR=0, ATTVAR, FLOAT, INTEGER, STRING, ATOM, COMPOUND, REFERENCE`); next 2
bits = storage class (`STG_STATIC/GLOBAL/LOCAL` — where the payload lives); 2 bits
GC mark. Small ints live inline (`valInt(w) = (sword)w >> 7`); atoms are an index;
compounds/bignums/floats/strings are a *tagged pointer* into the global stack.

Ours: `struct Term { TermTag tag; int saved_slot; union { ... } }` — a heap-allocated,
GC_malloc'd box per value, reached by `Term*`. A small integer is a whole struct.
A variable is a whole struct.

**Cost of the gap:** every `term_new_int`, every var, every list cell is a GC
allocation + pointer-chase. SWIPL puts a small int in a register. This is the
single biggest performance and memory divergence. **It also makes idea #3
(instant backtrack reclamation) impossible for us** — we have no stack to truncate.

**Verdict:** a tagged-word representation is the correct long-term target for the
runtime term type. Huge change (touches term.h, unify, all of bb_exec, every
builtin). Not a this-week move, but everything else should be designed knowing
this is the destination.

### 2. In-place binding + dereference chains  (`deRef`, `bindConst`)

SWIPL: binding a variable = overwrite the variable cell in place with a
`TAG_REFERENCE` word pointing at the value. Reading = `deRef` chases the ref chain.
Unbound var = a cell holding `(word)0` / a self-ref.

Ours: same *shape* — `bind()` sets `var->ref = val; var->tag = TERM_REF;` and
`term_deref` chases. **We already got this right.** The difference is only that our
cell is a malloc'd box and SWIPL's is a stack slot.

### 3. The mark is THREE pointers; Undo truncates the stack  (`struct mark`, `Undo`)

SWIPL `struct mark = { trailtop, globaltop, saved_bar }`. `Undo(m)`:
1. walk trail back to `m.trailtop`, calling `setVar(*entry)` to unbind each var;
2. **`gTop = m.globaltop`** — instantly frees every term allocated since the mark.

Ours: `trail_unwind(t, mark)` does step 1 only. We have NO step 2 because terms are
GC-malloc'd individually — there is no "top" to reset. We rely on Boehm GC to
eventually collect. So a deep failed search balloons the heap until GC runs;
SWIPL reclaims it the instant it backtracks.

**Verdict:** step 2 is a *free* consequence of idea #1 (stack-allocated terms). It
is not separately implementable without the global stack. Another vote for #1.

### 4. Choice points are a linked list of stack records  (`struct choice`, `newChoice`, `BFR`)

SWIPL: `struct choice { type; parent; mark; frame; value }`. `BFR` ("backtrack
frame register") points at the most recent choice. `newChoice` pushes one onto the
local stack and links `parent = old BFR`. Backtracking = take `BFR`, `Undo(BFR->mark)`,
resume at `BFR->value.pc` / next clause, set `BFR = BFR->parent`. Cut = set
`BFR = FR->parent_choice` (discard all choices newer than the cut barrier).

Ours: we have NO first-class choice point. Mode-2 `bb_exec` fakes it with
`nd->state>0` "is this node a live choice" flags walked at runtime (the
`bb_active_choice` scan at bb_exec.c:849). Mode-4 (the stashed CAT-A-3 work) tries
to rebuild it as an r12 "resume buffer" with a hand-rolled 5-qword layout and a
64-deep pool. **That r12 buffer is a from-scratch reinvention of `struct choice`.**

**Verdict:** the resume-buffer instinct in CAT-A-3 is *correct in spirit* but it's
modelling one choice point in isolation. The real model is a **choice-point stack**
with parent links, shared by ALL constructs (clause selection, `;`, retry). If we're
going to build the machinery, build the linked CP stack once — then `;`, multi-clause
choice, and `findall` re-solve all use the same primitive, and **cut becomes trivial**
(truncate the CP list to a saved barrier) instead of the ad-hoc `g_pl_cut_flag` we
have now.

### 5. Read/write-mode head matching — one pass, no build-then-unify  (`H_FUNCTOR`/`UMODE`)

SWIPL compiles each clause head into `H_*` instructions that walk the incoming
argument *in lockstep* with the head structure. At each functor: if the incoming
arg is unbound → **write mode** (build the structure, bind); if it's already a
compound → **read mode** (match field-by-field, recurse). No intermediate term is
built when matching. `H_FIRSTVAR` special-cases the first occurrence of a clause
variable (just capture the pointer, no unify).

Ours: `lower_pl` builds a full `Term` for the head pattern, then calls generic
`unify()` against the goal. We always allocate the pattern even when matching an
existing structure.

**Verdict:** the `B_UNIFY_{FF,VF,FV,VV,FC,VC}` specialization family (first-var/var/
const pair combinations) is where SWIPL gets its unification speed. Our single
`BB_UNIFY` + generic `unify()` is the correctness-complete but slow version. A
medium-term win: specialize the common unify shapes in lower_pl (var-against-const,
first-occurrence-var) into distinct BB nodes with tiny templates, instead of routing
all through `unify()`.

### 6. Last-Call Optimization — tail recursion in constant space  (`I_DEPART`)

SWIPL: when the *last* goal of a clause body is a call AND no choice point was
created in this frame (`BFR <= FR`), it **reuses the current frame** rather than
pushing a new one (`copyFrameArguments(lTop, FR, arity); VMH_GOTO(depart_continue)`).
Tail-recursive predicates (`count(N):- N>0, N1 is N-1, count(N1)`) run forever in
O(1) local stack.

Ours: every `BB_PL_CALL` is a fresh `call` with its own env push. Deep recursion =
deep C stack = eventual segfault (we've seen this — the SEGFAULT-CLUSTER rungs).

**Verdict:** LCO requires the frame/CP-stack model (#4) to even express "no choice
point since this frame." Once we have a CP stack, LCO is "if BFR <= current frame at
the last call, reuse the frame." This is the principled fix for the segfault cluster,
replacing per-call C recursion.

### 7. JIT first-argument clause indexing  (`pl-index.c`)

SWIPL: on first call to a multi-clause predicate, it builds a hash index on the
first argument's key (deepens to multi-arg / sub-arg indexes if that's not
discriminating). `p(a):-... p(b):-... p(c):-...` called as `p(b)` jumps straight to
clause 2 — **no choice point, no backtracking through a/c.** `MAX_VAR_FRAC`,
`MIN_SPEEDUP` heuristics decide when an index is worth it.

Ours: `BB_CHOICE` tries clauses in source order, each pushing/popping the trail,
backtracking on mismatch. O(clauses) per call, always, with a choice point even
when the call is semidet.

**Verdict:** indexing is the determinism detector. It's also what makes most "choice
points" disappear — and a choice point we never create is one we never have to
implement backtracking for. Big correctness *and* speed lever, but it sits on top of
#1+#4 (need keys on tagged words + a CP model to know when we elided one).

---

## The dependency order (what unlocks what)

```
#1 tagged-word terms (global stack)
   ├── enables #3 instant backtrack reclamation (free once #1 exists)
   ├── enables #7 cheap first-arg keys
   └── prerequisite for a real local/global/trail stack triple
#4 choice-point stack (parent-linked records)   ← can start on TOP of current Term* boxes
   ├── makes CUT trivial (truncate CP list to barrier)
   ├── unifies ;  / multi-clause / retry under one primitive
   ├── prerequisite for #6 LCO ("no CP since frame?")
   └── this is what CAT-A-3's r12 buffer is groping toward
#5 read/write head matching + B_UNIFY_* specialization (independent; speed)
#6 LCO (needs #4)
#7 JIT indexing (needs #1 keys + #4 to elide CPs)
```

**Two independent entry points that DON'T need the big #1 rewrite:**
- **#4 choice-point stack** can be prototyped with our existing `Term*` boxes: a
  `struct pl_choice { type; parent; int trail_mark; Term **env; BB_t *resume; }`
  linked list with a `g_pl_bfr` register. This *generalizes* the stashed r12 buffer
  into the real model and makes cut/`;`/multi-clause one mechanism. **Recommended
  next move** — it's the smallest step that replaces a reinvention with the genuine
  article, and it's the foundation everything else needs.
- **#5 unify specialization** is pure speed, fully independent, low risk.

---

## Direct implications for the stashed CAT-A-3 B–C work

The r12 resume-buffer (5 qwords: state/cursor/trail_mark/callee_env/saved_r12) is a
**single-choice-point record without the parent link.** It works for one resumable
call at a time but:
- the "γ-leak" problem (resumable call that succeeds and is never backtracked leaves
  r12 dangling) is *exactly* the problem `struct choice` solves with `DiscardMark`
  and the CP being on a stack that the frame teardown truncates;
- cut across a resumable call has no story in the buffer model; in the CP-stack model
  it's `BFR = barrier`.

**Recommendation to Lon:** rather than finish the buffer-in-isolation model and then
re-do it as a CP stack later, promote the buffer to a real parent-linked choice-point
record now (idea #4), with `g_pl_bfr` as the single backtrack register. Same emit
effort, but it's the model we keep. The cursor-dispatcher in `bb_pl_choice.cpp`
(WAM-style `cmp cursor / cascade`) is already the right shape for "next clause" — it
just needs to read/write the CP record instead of a bare r12 buffer, and the CALL
site pushes/pops CP records instead of pool buffers.

---

## What we already do right (don't churn these)

- deref + in-place ref binding (idea #2) — matches SWIPL.
- trail as an array of bound-var pointers, unwind-to-mark (idea #3 step 1).
- atoms as interned ids.
- four-port (α/β/γ/ω) AG lowering — this is our own structure; SWIPL uses a flat
  VM + CP stack instead, but our port model is a legitimate alternative as long as
  β (redo) is backed by a real CP record.

---

## Files read for this study
SWIPL: `src/pl-data.h` (tags/storage/deref), `src/pl-incl.h` (struct choice / mark /
localFrame / queryFrame, Mark/Undo/Trail macros), `src/pl-vmi.c` (H_*/B_*/C_*/I_*
opcodes; H_FIRSTVAR, H_RFUNCTOR read/write mode, I_DEPART LCO), `src/pl-wam.c`
(newChoice, discardChoicesAfter, BODY/CLAUSE/FRAME_FAILED backtrack), `src/pl-index.c`
(JIT first-arg/deep indexing).
Ours: `src/frontend/prolog/term.h`, `prolog_unify.c` (unify/trail/bind),
`src/lower/lower_pl.c`, `src/lower/bb_exec.c`, `src/emitter/BB_templates/bb_pl_*.cpp`.
