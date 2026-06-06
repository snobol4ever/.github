# HANDOFF 2026-06-06 (Sonnet 4.6) — PROLOG-BB: PL-GZ-9a compound unify native m3

SCRIP commit: `9f56a73`. .github commit: this doc + GOAL-PROLOG-BB.md watermark update.

## Session summary — PL-GZ-9a landed

### What landed

**rung03_unify** (`f(X,a) = f(b,Y)` → `b a`) now runs natively on the GZ m3 path.
GATE-3: m2 115/115 HARD · m3 **22**/0/93-EXC (+1 rung03) · m4 105/0/10-EXC (no regression).

### Three-part implementation

**1. `bb_cell_unify.cpp` — new STRUCT arm** (fires when `lk==IR_STRUCT || rk==IR_STRUCT`):
```
mov rdi, r12              ; GZ frame pointer
x86_ro_load_q rsi, 0     ; sealed lhs IR_t* [rip+disp]
x86_ro_load_q rdx, 1     ; sealed rhs IR_t* [rip+disp]
call rt_pl_unify_struct_gz
test eax, eax / je PORT_OMEGA / jmp PORT_GAMMA
def PORT_BETA / jmp PORT_OMEGA
+ x86_ro_seal_q(0, (uint64_t)ln)
+ x86_ro_seal_q(1, (uint64_t)rn)
```
The IR_t* subtrees are sealed as RO constants beside the box. Valid for m3 (in-process,
pointers live). m4 falls through to the flat/rich emitter which already handles rung03.

**2. `rt_pl_unify_struct_gz` in `unification.c`** — GZ-frame-aware IR→Term* builder:
- `IR_LOGICVAR{slot}` → `cells[slot]` from frame (`frame+8+8*slot`)
- `IR_ATOM/LIT_I/LIT_F` → `term_new_atom/int/float`
- `IR_STRUCT` → recursive `term_new_compound` with arg chain walked via `nd->α → nd->γ → ...`
- Then `rt_unify_terms(lt, rt_)` with trail-backed binding

**3. `pl_gz_admit` in `scrip.c`** — relaxed IR_STRUCT rejection:
- STRUCT nodes now allowed when they are operands of `IR_UNIFY` nodes in the graph
- `IR_UNIFY` check extended: when `ls || rs` (either side STRUCT), both sides must be
  STRUCT|LOGICVAR|ATOM|LIT_I (the standard GZ-admissible types)
- `g_gz_no_struct_ptr = 1` set before m4 TEXT call to `pl_gz_admit`, blocking STRUCT
  admission there (IR_t* pointer sealing is in-process only; m4 uses flat/rich emitter)

Also added `#include "../contracts/IR.h"` to `unification.c` for `IR_t` struct access.

## What was attempted but NOT landed: PL-GZ-9b (rung05/06/08)

**Target**: multi-clause predicates with compound/list heads — `member/2` (`[X|_]`,`[_|T]`),
`append/3`, `fib/2`, etc. These are the bulk of the 93 remaining excised rungs.

**Root diagnosis**: The GZ admission pipeline has two layers:
1. `pl_gz_choice_inline` → `bb_cell_choice`: only handles atom/int constant matching per clause
2. `pl_gz_callee_get_choice` → `pl_gz_rule_callee_body`: emits CELL_UNIFY chains

For STRUCT heads, layer 1 is wrong (emits `rt_pl_unify_cell_const` with IR_STRUCT kind, which
is broken). The right path is layer 2. But layer 2 requires `pl_gz_rule_clause` to accept
STRUCT head args — and when that gate was opened, the `pl_gz_fact_clause_units` + `pl_gz_call_args_ok`
relaxations caused `member/2` to be admitted into the GZ call chain, producing infinite
recursion (no depth guard, no termination on recursive predicates).

**Design for next session (PL-GZ-9b)**:

The correct architecture for compound-head multi-clause predicates:

A. Gate `pl_gz_choice_inline`: return NULL when ANY clause head arg is IR_STRUCT.
   This forces routing to the `pl_gz_callee_get_choice` path.

B. Gate `pl_gz_rule_clause`: allow IR_STRUCT as head arg RHS (line 521 `return 0`).
   The body validation does NOT need STRUCT relaxation — only the head unify positions.

C. Gate `pl_gz_choice_rule_clauses`: add a recursion-depth guard. The visiting list
   `g_gz_visiting[16]` already exists but the recursive `member/2` body calls itself,
   which hits the visiting guard and returns 1 (ok) — but the emitted GZ callee has
   no termination for recursive execution. Need additional depth ceiling (e.g., max 2
   levels of callee nesting for STRUCT-head predicates).

D. `pl_gz_callee_get_choice` (PL-GZ-5c multi-clause path): currently only handles
   simple atom/int head args via `pl_gz_rule_callee_body`. Need to extend
   `pl_gz_rule_callee_body` lines 560-576 to emit CELL_UNIFY(slot_i, STRUCT_node)
   — which `bb_cell_unify`'s STRUCT arm already handles correctly via `rt_pl_unify_struct_gz`.
   The STRUCT node is a compile-time constant sealed beside the box.

E. The key CORRECTNESS question for recursion: the GZ ζ-tree model allocates a fixed
   child-frame slot per call site. For recursive `member/2`, the same call site is re-entered
   with a new frame (`rt_enter` reuse-or-alloc). The trail correctly unwinds between
   backtrack attempts. But the GZ admission currently caps at 8 callees and 4 clauses —
   `member/2` with recursive body passes `pl_gz_choice_rule_clauses` (visiting guard lets
   it through), but the emitted GZ blob then loops forever on the `[a,b,c]` list because
   the recursive call's frame allocation has no termination — `rt_enter` always returns
   a frame, the recursive CELL_CALL always succeeds at entering, and backtracking is only
   from the CELL_CHOICE's trail mark.

   The fix: for recursive multi-clause predicates with STRUCT heads, the GZ substrate
   needs the full `IR_CHOICE` → `IR_GOAL` → callee `IR_CHOICE` chain (the existing m2
   IR machinery) rather than the GZ inlined path. The GZ path can only handle SHALLOW
   (non-recursive) predicates with STRUCT heads — e.g., `foo([a,b]) :- ...` (fact/rule
   with known list patterns and NO recursive calls).

   Practical scope for 9b: admit STRUCT-head predicates that are EITHER (a) facts only
   (no body goals) OR (b) rules whose body goals call ONLY atom/int-const predicates
   (not recursive). That covers `member/2`-style with constant lists but not with
   variable lists. The bulk of `[H|T]` usage in the corpus is actually in recursive
   predicates — so 9b may only recover a handful of rungs. The bigger unlock is
   the full WAM-style CHOICE path for general recursive predicates (PL-GZ-9 proper).

## Gate verification on 9f56a73

GATE-1: 5/5 m2 HARD · 4/0/1-EXC m3 · 5/5 m4
GATE-3: 115/115 m2 HARD · 22/0/93-EXC m3 (+1 rung03) · 105/0/10-EXC m4
test_gate_pl_gz7: PASS (all probes including gzvarith_cmp + gzvarith_is)
test_gate_bb_one_box: PASS
seg_byte/SL_B grep: 0 · g_vstack: 0

## Next opener: PL-GZ-9b

Scope: STRUCT-head multi-clause predicates where the callee body is non-recursive (fact
or simple rule). Steps:
1. `pl_gz_choice_inline`: add STRUCT-head guard → return NULL
2. `pl_gz_fact_clause_units`: accept IR_STRUCT + IR_LOGICVAR in head arg β positions
3. `pl_gz_rule_clause`: allow IR_STRUCT head arg RHS (add `if (u->β->t == IR_STRUCT) continue;`)
4. `pl_gz_choice_rule_clauses`: add non-recursive guard — reject if any clause body
   calls a predicate whose graph is the SAME as the current `cg` being validated
5. Test: a predicate like `path(a,b). path(b,c). main :- path(X,Y), write(X-Y), nl.`
   should admit and run natively, since fact heads `a`/`b`/`c` are atoms — but
   `match([a|_]). match([b|_]).` with STRUCT heads should also admit as non-recursive facts.
6. Gate ratchet: m3 count must be ≥ 22 (no regression).
