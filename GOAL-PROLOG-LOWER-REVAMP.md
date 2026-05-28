# GOAL-PROLOG-LOWER-REVAMP — bring Prolog LOWER to Icon-LOWER fidelity

**Status:** Investigation complete (Opus 4.7, 2026-05-28). Design captured; NOT yet
implemented. This is a multi-session revamp. Reference material: jcon-master
(uploaded), specifically `tran/irgen.icn` (the canonical four-port IR generator)
and `tran/ir.icn` (the IR node + chunk record types).

## The reference model: irgen.icn (Jcon)

irgen.icn is the authoritative statement of how Icon's goal-directed evaluation
lowers to a four-port control graph. The four ports are the fields of one record:

```icon
record ir_info(start, resume, failure, success, x)   # irgen.icn:10
```

Mapping to our Greek-letter ports:
- `start`   = **α**  (fresh entry)
- `success` = **γ**  (a solution was produced; continue forward)
- `failure` = **ω**  (no/no-more solutions; the construct is exhausted)
- `resume`  = **β**  (redo: the parent wants the next solution)
- `x`       = per-construct scratch (loopinfo / scaninfo) — our aux sidecar

`ir_init(p)` (irgen.icn:1426) mints all four labels for every AST node up front:

```icon
procedure ir_init(p)
    p.ir := ir_info()
    p.ir.start   := ir_label(p, "start")
    p.ir.resume  := ir_label(p, "resume")
    p.ir.success := ir_label(p, "success")
    p.ir.failure := ir_label(p, "failure")
end
```

Then each `ir_a_<Node>` procedure emits `ir_chunk(label, [insns…])` suspensions
that wire its own four ports to its children's four ports. The labels are the
LOGICAL links; `ir_chunk` turns them into PHYSICAL basic blocks. Example — the
choice point (the Icon analog of Prolog BB_CHOICE), irgen.icn:167 `ir_a_Alt`:

```icon
ir_init(p)
# start → first alternative's start
suspend ir_chunk(p.ir.start, [ ir_Goto(_, p.eList[1].ir.start) ])
# each alt: success → MoveLabel(resume-cont) + our success;  failure → next alt's start
every i := 1 to *p.eList do {
    suspend ir_chunk(p.eList[i].ir.success, [
        ir_MoveLabel(_, t, p.eList[i].ir.resume),   # remember where to resume
        ir_Goto(_, p.ir.success) ])
    suspend ir_chunk(p.eList[i].ir.failure, [ ir_Goto(_, p.eList[i+1].ir.start) ])
}
# last alt's failure → our failure
suspend ir_chunk(p.eList[-1].ir.failure, [ ir_Goto(_, p.ir.failure) ])
# our resume → IndirectGoto(t): jump back to whichever alt last succeeded
/bounded & suspend ir_chunk(p.ir.resume, [ ir_IndirectGoto(_, t) ])
```

Key properties of the reference model — these are the bar to hit:

1. **Every node carries an explicit `resume` (β) label.** Backtracking never
   guesses which neighbor is resumable; the parent's `resume` chunk names the
   exact child resume label (or `IndirectGoto` through a saved-label temp `t`
   when the resumable alternative is only known at run time).
2. **One procedure per AST node type.** irgen has 43 `ir_a_*` procedures; the
   dispatcher `ir()` (irgen.icn:1356) is a flat `case type(p)`. No node's wiring
   leaks into another's function body.
3. **`bounded` flag threads the determinacy context.** A bounded context (the
   value is used once, e.g. the condition of `if`) suppresses the resume-chunk
   emission entirely — see the `/bounded &` guards. Unbounded (the expression may
   be resumed for more solutions) emits the full resume wiring. This is the
   single most important piece Prolog LOWER is missing in clean form.
4. **`IndirectGoto` + `MoveLabel` for run-time-chosen resume targets.** When the
   construct can't know at lower time which sub-expression will be the live
   choice point (Alt, RepAlt, Every), it stores the resume label in a temp and
   jumps through it. This is the logical-link-made-physical the user described.

## Our Icon side: lower_icn.c — faithful, and the template to copy

`lower_icn.c` (1995 lines) mirrors irgen closely:
- **9 `_ag` (attribute-grammar / threaded) functions**, signature:
  `lower_icn_new_X_ag(cfg, e, BB_t *γ_in, BB_t *ω_in, BB_t **α_out, BB_t **β_out)`.
  This C signature **is** `ir_info` made physical: the node receives its success
  (γ) and failure (ω) continuations from the parent and hands back its entry (α)
  and resume (β). Each `_ag` reproduces one `ir_a_*` procedure's chunk wiring as
  BB_t pointer links.
- **104 per-construct `lower_icn_new_<Node>` dispatchers** — one per nonterminal,
  matching irgen's one-procedure-per-node discipline.
- 343 explicit four-port (`α/β/γ/ω`) references in the file.
- `lower_icn_new_Alt_ag` (line 872) is the direct transliteration of `ir_a_Alt`
  above; `lower_icn_new_If_ag` ↔ `ir_a_If`; `Every_ag` ↔ `ir_a_Every`; etc.

This is the level Prolog LOWER must reach.

## Our Prolog side: lower_pl.c — the gap

`lower_pl.c` is 624 lines with 219 four-port references — it DOES thread the four
ports (the `γ_in, ω_in, **α_out, **β_out` signature is on `lower_pl_term`,
`lower_pl_goal`, `lower_pl_threaded`), so it is not ad-hoc. But it diverges from
the reference model in three structural ways:

### Gap 1 — monolithic dispatch (2 mega-functions vs 1-per-construct)

All goal lowering lives in `lower_pl_goal` (lines 166–508, ~340 lines): a chain
of `if (e->t==… && strcmp(fn,"…"))` arms for conjunction, disjunction, cut,
if-then-else, builtins, and user calls — all inline in one function. irgen and
lower_icn.c give each its own procedure. Consequence: the wiring for `;`
(disjunction = BB_CHOICE-like) and `,` (conjunction = BB_PL_SEQ) are interleaved
and share locals, making the resume threading hard to verify against irgen
chunk-by-chunk.

### Gap 2 — β by heuristic, not by explicit port (the correctness gap)

Conjunction wiring (lines 196–206) computes each goal's β as "the nearest
resumable predecessor," scanning left and propagating:

```c
gβ[i] = (t==BB_PL_CALL||t==BB_CHOICE||t==BB_PL_ALT) ? gnodes[i] : gβ[i-1];
...
for (i=1;i<n;i++) if (!gnodes[i]->ω) gnodes[i]->ω = gβ[i-1];
```

irgen NEVER does this. Every node has its own `resume` label; the parent wires
`goal[i].failure → goal[i-1].resume` directly, and goal[i-1]'s OWN resume chunk
decides whether it has more solutions (a deterministic node's resume chunk just
`Goto`s its failure; a generator's resume chunk re-enters). The heuristic
collapses "which node is resumable" to a lower-time type test over a hardcoded
set {CALL, CHOICE, ALT}. Any resumable construct NOT in that set (or any future
one) is invisible to backtracking. This is very likely the root structural cause
of the CAT-A-3 class of mode-4 backtracking failures (rung02/05/06): the β links
are approximate, so the emitter has no precise resume edge to lay down.

### Gap 3 — no `bounded` flag

Prolog LOWER has no analog of irgen's `bounded` parameter. Determinacy (a goal
whose solutions are used once — e.g. the condition of `->`, or a goal followed by
`!`) is not threaded through lowering, so resume wiring is emitted (or omitted)
by ad-hoc rules per arm rather than by one uniform context flag. Cut (`!`)
handling especially would fall out naturally from a `bounded`-style context.

## What the revamp requires (multi-session; staged)

**Stage 0 — port-parity scaffolding.** Add a `bounded` int parameter to the
threaded signature: `lower_pl_goal(cfg, e, γ_in, ω_in, &α_out, &β_out, bounded)`.
Thread it everywhere (default 0 = unbounded). No behavior change yet; pure plumb.

**Stage 1 — split the monolith into per-construct functions**, mirroring
lower_icn.c's `_new_X` / `_X_ag` split. One function each for:
`lower_pl_conj` (`,` → BB_PL_SEQ), `lower_pl_disj` (`;` → BB_CHOICE/ALT),
`lower_pl_ite` (`->;` → BB_PL_ITE), `lower_pl_cut` (`!` → BB_CUT),
`lower_pl_call` (user pred → BB_PL_CALL), `lower_pl_builtin` (→ BB_BUILTIN).
Each takes the full threaded+bounded signature and wires ONLY its own ports.
Verify mode-2/3/4 gates unchanged after each extraction (pure refactor).

**Stage 2 — replace the β-heuristic with explicit resume ports.** Give every
goal node a real β even when deterministic: a deterministic node's β should point
to a tiny "fail" continuation (≡ irgen's resume-chunk that `Goto`s failure),
NOT be smeared from a neighbor. Conjunction then wires `goal[i].ω = goal[i-1].β`
unconditionally (irgen's exact rule), and determinism is expressed by what
goal[i-1].β actually does, decided in goal[i-1]'s own lowering. This removes the
{CALL,CHOICE,ALT} hardcoded set.

**Stage 3 — make BB_CHOICE wiring a transliteration of `ir_a_Alt`** (the
MoveLabel/IndirectGoto resume-target pattern), which is exactly the physical
mechanism CAT-A-3 (b) needs: the choice's resume jumps through a saved label to
whichever clause last succeeded. This UNIFIES the LOWER revamp with the CAT-A-3
emitter work — the resume-buffer cursor in the CAT-A-3 design is the run-time
realization of irgen's `MoveLabel(t, …) / IndirectGoto(t)`.

**Stage 4 — re-verify the full corpus.** Expectation: the mode-4 backtracking
rungs (rung02/05/06 and the broader `pred(X),…,fail` family) become wireable
because the β edges are now precise. This is the same +15–25 unlock CAT-A-3
targets — the LOWER revamp and CAT-A-3 are two halves of one correctness story
(precise resume edges in the graph + an emitter that lays them down).

## Relationship to CAT-A-3 (in flight)

CAT-A-3 Steps A–D (see HANDOFF-2026-05-27-OPUS-PROLOG-BB-CAT-A3-STEPA.md) fix the
EMITTER side: make `bb_pl_call.cpp` / `bb_pl_choice.cpp` honor β at the x86 level.
This GOAL fixes the LOWER side: make the BB_t graph carry PRECISE β edges for the
emitter to lay down. They meet at BB_CHOICE: irgen's `ir_a_Alt` MoveLabel/
IndirectGoto resume pattern is the design source for BOTH the lowered β links
(this goal, Stage 3) and the r12 resume-buffer cursor (CAT-A-3 Step C). Recommend
sequencing: land CAT-A-3 B–D first (emitter honors the β edges that already exist
approximately), THEN this revamp (make those edges precise) — or interleave Stage
3 here with CAT-A-3 Step C since they share the Alt model. Lon to direct.

## Quantified gap summary

| Metric | irgen.icn (ref) | lower_icn.c (good) | lower_pl.c (gap) |
|---|---|---|---|
| explicit four-port record/links | ir_info, all 4 | 343 α/β/γ/ω refs | 219 refs |
| one function per AST node | 43 ir_a_* procs | 104 _new_ + 9 _ag | 2 mega-funcs |
| explicit per-node resume (β) | yes (every node) | yes (_ag β_out) | heuristic (Gap 2) |
| bounded/determinacy flag | yes (threaded) | yes (bounded arg) | absent (Gap 3) |

## NEXT
- Lon to confirm sequencing vs CAT-A-3 B–D and approve the Stage 0–4 plan.
- Stage 0 (bounded plumb) is the safe first commit — pure parameter threading,
  zero behavior change, fully gate-verifiable. Good opening move for a fresh
  session with the irgen.icn reference open alongside.
