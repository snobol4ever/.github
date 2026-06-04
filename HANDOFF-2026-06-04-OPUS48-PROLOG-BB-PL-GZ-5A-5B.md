# HANDOFF — PROLOG-BB · PL-GZ-5a + PL-GZ-5b (calls, ζ-tree, recursion) — 2026-06-04, Opus 4.8

**SCRIP commits:** `da9228d` (5a calls via δ/ε) → `9cba9ab` (5b-i ζ-tree substrate) → `c285ea1` (5b-ii recursion).
**.github commits:** `bb0bfe38` (GOAL prune + 5a watermark) → `05095ed1` (5b watermark) → this handoff.
**Watermark at close:** GATE-1 m2 5/5 HARD · m3 4/0/1-EXC (`recursion` only — multi-clause, flips at 5c) · m4 5/5;
GATE-3 m2 115/115 HARD · m3 18/0/97-EXC · m4 105/0/10-EXC; gz2/3/4/5a/5b PASS all corrupt-proven; coupling
ceilings 19/10/0/39 (every new-path box emits ZERO control calls; `rt_enter`/`rt_pl_cells_init`/`rt_trail_*` are
VALUE-class); one-box PASS; g_vstack 0; SNOBOL4 19/19; Icon 5/7 standing.

## What landed

**5a — user-predicate CALLS (`da9228d`).** The call IS a port edge to another box's α: two new port fills
**δ = callee α / ε = callee β** beside γ/ω/β (`PORT_DELTA`=4/`PORT_EPSILON`=5; `X86_INTERNAL_BASE` 4→6,
single-sited symmetric — grep-verified no hardcoded base anywhere); call encoder `x86("call",port)` =
`Lrec(0xE8)+Jrec(port)` / ` call name`. New boxes `bb_cell_call.cpp` (arg CELL-POINTER marshal → call δ →
verdict-in-rax λ-test jne-γ/jmp-ω; β re-enters via ε) and `bb_callee_frame.cpp`. Admit (scrip.c beside
`pl_gz_admit`): single-clause rule callees ar≤2, head goals `UNIFY(LV i, LV|const)` (self folds at rewrite;
cross-var/const heads = CELL_UNIFY vs arg cells), det body class; caller const args = synthetic query cells
(PASS-A prescan; `cells_init` covers ncells = nslots+nsynth); callee bodies REBUILT FRESH (shared m2 graphs never
mutated); callees memoized per clause graph. 5a's one-frame interim + its stale-mark soundness argument are
HISTORY — superseded by 5b, recorded in the GOAL's 5a entry.

**5b-i — ζ-TREE substrate (`9cba9ab`).** Each call SITE owns a child-frame POINTER slot in the caller's frame
(the seed's `&ζ->p2_ζ`); `rt_enter(void **slot, int nslots)` (src/runtime/unification.c) = reuse-or-alloc.
Register protocol = the seed's print form `path(&ζ->p2_ζ,α,a0,a1)`: call δ with **rdi=child, rsi/rdx=arg cell
ptrs**; call ε with **rdi=child ONLY** (args already live in the child frame); callee α/β: push caller ζ (saves
r12 AND restores SysV alignment), `mov r12,rdi`. Callee slots = clause slots DIRECT (args 0..ar-1, locals after;
mark at [ζ+0] mirroring bb_query_frame). Emitted callee blocks are REENTRANT. All 5a probes stayed byte-identical
across the swap — the substrate landed green before recursion touched it.

**5b-ii — recursion (`c285ea1`).** IR_GOAL admitted in rule bodies (per-goal structural check + deep admission
at build); `pl_gz_callee_get` = memo with **SHELL-FIRST insertion** (self/mutual recursion finds the shell at
admit; call_states hold only the pointer; fields finalized before the drive reads them). Body builder reworked:
nested-call const args = synthetic cells **APPENDED TO THE CALLEE'S LOCALS** (covered by its per-activation
cells_init); child slots placed AFTER locals+synths, OUTSIDE the init range. `bb_cell_call` sizes rt_enter as
arity+nlocals+**nchild**. Drive = WORKLIST: `gz_callee_labels` allocs `gzp%d_α/β` once; `gz_emit_callee` first
scans its body for CELL_CALL → labels+appends nested callees; the emission loop re-reads ncallees.

## Load-bearing invariants (do not regress)

1. **rt_enter reads the child slot BEFORE anything writes it** — child slots must stay OUTSIDE every
   cells_init range (query: after ncells; callee: after locals+synths). Fresh frames are zeroed by GC_malloc;
   the query frame by `rt_frame`'s static BSS. Violating this hands rt_enter a Term* as a "frame".
2. **Arg-save BEFORE `rt_trail_mark`** in bb_callee_frame α — rt calls clobber rdi/rsi/rdx.
3. **Callee bodies are rebuilt fresh at admit** — the shared m2 clause graphs are never mutated.
4. Recursion depth is sound because every activation has its own frame, hence its own child slots; the C call
   stack is the sanctioned recursion spine.

## Gate ratchets applied (the pattern: a stale "not yet implemented" negative becomes a capability → flip it
to a positive and keep the decline family alive with a still-over-the-watermark negative)

- gz3 neg2 (const-head rule) → `consthead` positive (`side\na\n`) + arith-body negative.
- gz5a neg2 (nested call) → moved to gz5b positive; replaced by compound-body negative `q(X) :- X = f(a).`
- gz5b negatives: 2-clause rule pred (5c territory) + arith-behind-nested-call. Corrupt-proofs must run from
  `scripts/` (the harness `cd "$(dirname $0)/.."` breaks from /tmp) and measure `$?` WITHOUT a pipe (a pipe
  makes `$?` report `tail`'s rc).

## Session craft kept

`str_replace` on big blocks can eat the ADJACENT function header — verify `grep -n "static .* pl_gz_admit"`
after any large replace (it bit once this session, repaired immediately). New template files go in the Makefile
in TWO places (sources list ~L169 + compile rule ~L383). m4 test recipe:
`./scrip --compile --target=x86 f.pl > f.s && as -o f.o f.s && gcc -no-pie f.o -L out -lscrip_rt -Wl,-rpath,$PWD/out -o f.bin`.

## Next opener: PL-GZ-5c — multi-clause RULE predicates (full `path/2`)

Callee-level choice over rule clauses: cursor + mark in the callee's OWN frame row (the bb_cell_choice shape,
which is already the seed's edge/2 transcription), per-clause body chains, β dispatch = cmp-chain to clause-k's
redo entry; head-unify per clause as in 5a. This flips the GATE-1 `recursion` smoke probe (path/2 is two-clause)
and is the last structural rung before GZ-6 cut. Also open: GZ-1b(e) fence (delete the m3 fallback),
CORPUS-S-HYGIENE(b) (needs Lon's demo keep-list), and the 5c-adjacent general 2-arm disjunction deferred at 4b.
