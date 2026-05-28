# HANDOFF 2026-05-27 — Opus 4.7 — PROLOG-BB: CAT-A-3 (b) Step A + full B–D design

**Goal:** GOAL-PROLOG-BB.md — CAT-A-3, the largest single mode-4 unlock
(estimated +15–25 corpus PASS). Lon chose **option (b): resumable-call
protocol** over (a) inline-on-demand, to preserve single-emit.

**This session landed Step A only** (runtime substrate, behavior-neutral) and
the complete B–D design below. one4all `58142007`. All gates hold at watermark.

Why stop after Step A: Steps B–D are ~150 LOC across 4 files (two BB templates,
emit_bb.c, the PL_ENTRY arm in sm_bb_switch.cpp) plus a full 107-fixture corpus
run. That deserves a fresh-context session. Landing a half-wired multi-template
ABI change under context pressure is the worst possible handoff. Step A is the
self-contained, fully-green foundation; B–D build on it from a known-good base.

## Watermark / gate ledger (unchanged this session — Step A is additive)

| Gate | Count |
|---|---|
| GATE-1 smoke | 5/5 |
| GATE-2 crosscheck | 132/0 (5 ORACLE_MISS) |
| GATE-3 mode-2 | 91/107 |
| GATE-4 mode-4 minimal | 4/4 |
| Full mode-4 corpus | 28/107 |
| FACT RULE | 0 |

one4all HEAD: `58142007` (Step A). Prior: `66d283ad` (rung25-TERM-STRING).

## The problem (grounded in rung02)

```prolog
person(brown). person(jones). person(smith).
main :- person(X), write(X), nl, fail ; true.
```
Mode-2: `brown\njones\nsmith`. Mode-4: `brown` ONLY.

`, fail` should backtrack into `person(X)` to enumerate all three. It doesn't
because:
- `bb_pl_call.cpp:97` — `β: jmp ω` (call site never re-enters callee on redo)
- `bb_pl_choice.cpp:58` — `β: jmp ω` (choice never advances to next clause on redo)

`person(X)` is a BB_PL_CALL whose callee body is a 3-clause BB_CHOICE. So redo
must: call-site β → resume callee → callee's BB_CHOICE advances cursor → next
clause. The two are coupled; they ship together (Steps C+D).

## The design — caller-allocated continuation state (WAM-style, single-emit-safe)

Mode-2 keeps continuation in BB_t.state + aux (zc->cur, zc->cs, cs->act
snapshots) — see bb_exec.c BB_CHOICE arm (2921–2976) and BB_PL_CALL arm
(2977–3076); these are the semantic reference. Mode-4 can't (no BB_t at
runtime). Instead: **the cursor lives in CALLER-allocated stack slots.** The
callee block stays emitted exactly once; each call site allocates its own
resume state. Single-emit preserved at the byte level.

### Step A (DONE, `58142007`) — substrate

- Trail checkpoint/rewind by explicit mark: **reused existing**
  `rt_pl_trail_mark()` / `rt_pl_trail_unwind(int)` (rt.c 996–1005). They take a
  caller-supplied mark value, so each call site owns its checkpoint — no
  aliasing across nested activations (unlike the depth-32 g_pl_mark_stack LIFO
  the static cascade uses). NO new trail helper (first draft added a redundant
  pair; removed).
- **Added** `Term **pl_bb_env_install(Term **env)` (rt.c, declared
  pl_runtime.h): sets g_pl_env without freeing previous, returns previous in
  rax. The non-freeing counterpart to pl_bb_env_pop (which frees). The
  resumable path must keep the callee env alive across redo — goal file:
  "callee block must NOT pop saved env on γ." Exported (nm -D confirms).

### Step B — BB_CHOICE β as stack-resident cursor (`bb_pl_choice.cpp`)

Current template (68 lines): entry → jmp pre[0]; pre[0] pushes a trail mark via
rt_pl_trail_mark_push, jmps body[0]; pre[i>0] unwinds-top + jmps body[i]; clause
bodies wired by the driver so γ=γ_in, ω=next-pre (static cascade); β:jmp ω.

Rewrite to a cursor-driven dispatcher. Stack layout at choice entry (2 qwords,
16-byte aligned — one push pair):
```
[rsp+0]  cursor      ; next clause to try, 0..N-1
[rsp+8]  trail_mark  ; entry checkpoint (rax from rt_pl_trail_mark)
```
Emit shape:
```
α:  # BOX PL_CHOICE n=N (resumable)
    call rt_pl_trail_mark@PLT     ; rax = entry mark
    push rax                      ; [rsp+8 later] trail_mark
    xor eax,eax
    push rax                      ; [rsp+0] cursor=0
    ; fall into dispatch
.Lplch<id>_dispatch:
    mov rdi,[rsp+0]               ; cursor
    cmp rdi,N
    jge .Lplch<id>_exhausted
    ; jump table / compare cascade on cursor → pre[cursor]
    ...
.Lplch<id>_c0_pre:                ; first clause: already at entry mark, no unwind
    inc qword ptr [rsp+0]         ; cursor++ (next β tries c1)
    jmp .Lplch<id>_c0_body
.Lplch<id>_c<i>_pre:              ; i>0
    mov rdi,[rsp+8]               ; trail_mark
    call rt_pl_trail_unwind@PLT
    inc qword ptr [rsp+0]
    jmp .Lplch<id>_c<i>_body
β:  jmp .Lplch<id>_dispatch       ; *** redo re-enters dispatcher; cursor persists on stack ***
.Lplch<id>_γ_local:
    add rsp,16                    ; drop cursor+mark
    jmp γ_in
.Lplch<id>_exhausted:
    mov rdi,[rsp+8]
    call rt_pl_trail_unwind@PLT   ; final unwind
    add rsp,16
    jmp ω_in
```
**Driver change (flat_drive_pl_choice in emit_bb.c):** each clause body's ω must
now wire to **β (this choice's dispatcher re-entry)**, NOT to the next clause's
pre. The cursor++ in pre is what advances. γ of each body wires to γ_local.

CAVEAT — stack discipline across clause bodies: a clause body that itself
contains a nested BB_CHOICE/BB_PL_CALL will push its own frame. The +16 drop at
γ_local/exhausted assumes the body left the stack balanced. Bodies are
port-structured (enter α, leave via γ/ω) and today leave the stack balanced;
verify with `objdump -d` on rung02 that rsp at γ_local == rsp after the entry
push pair. If a body can leave residue, the cursor/mark offsets [rsp+0]/[rsp+8]
break — in that case switch to rbp-relative addressing (set rbp at α, address
the slots off rbp, restore rsp from rbp at γ_local/exhausted).

Step B alone won't move mode-4 corpus (call sites still stub β→ω, so nothing
drives the choice's β yet). Gate expectation after B: all hold, 28/107
unchanged. Commit B separately so the choice rewrite is bisectable.

### Step C — BB_PL_CALL β as r12 resume-buffer (`bb_pl_call.cpp` + PL_ENTRY arm)

Resume buffer: caller-allocated (stack or small malloc), pointer in **r12**
(callee-saved in SysV — survives across the `call`/nested calls). Layout:
```
[r12+0]   state       ; 0=fresh, 1=resumable
[r12+8]   cursor       ; mirror of the callee's rightmost BB_CHOICE cursor
[r12+16]  trail_mark   ; callee-entry mark
[r12+24]  callee_env   ; heap env (pl_bb_env_save_push result) — kept alive across redo
```
Two callee entry labels (emitted once each per predicate — single-emit intact):
- `.Lplpred_<name>_<arity>`        — fresh entry
- `.Lplpred_<name>_<arity>_redo`   — resume entry

Call site (extends current 5-phase emit in bb_pl_call.cpp):
- Phase 0 (new): allocate resume buffer, `mov r12, <buf>`, `mov qword [r12+0],0`.
- Phases 1–3 (keep): build arg terms, env save+push, bind args. BUT use
  `pl_bb_env_save_push` and stash its return (caller env) AND the new callee env
  ptr into the buffer ([r12+24]); capture trail mark into [r12+16].
- Phase 4 fresh: `call .Lplpred_<name>_<arity>` (passes r12).
- Phase 5: test rt_last_ok → γ_in / ω_in. On γ, the buffer stays live (do NOT
  env_pop — use the non-freeing discipline; caller env restored only on
  exhaustion).
- **β (the fix):** restore r12 (it's callee-saved, still valid), reinstall callee
  env via `pl_bb_env_install([r12+24])`, then
  `call .Lplpred_<name>_<arity>_redo`; test last_ok → γ_in (next solution) /
  ω_in (exhausted → env_install back the caller env, restore).

PL_ENTRY arm (sm_bb_switch.cpp 146–190, the callee-block loop) changes:
- Emit BOTH `.Lplpred_..` and `.Lplpred_.._redo` labels.
- Fresh entry: `mov qword [r12+0],0`; body walk; γ stashes the body's rightmost
  BB_CHOICE cursor into [r12+8] + sets [r12+0]=1 + last_ok=1 + ret; ω sets
  [r12+0]=0 + last_ok=0 + ret.
- `_redo` entry: reinstall env, unwind trail to [r12+16], then
  `jmp .Lplch<choice_id>_dispatch` of the body's rightmost choice (cursor already
  in [r12+8] — Step B reads cursor from [rsp]; for the call path the choice must
  read its cursor from the buffer instead. Reconcile: simplest is to have the
  callee body's BB_CHOICE ALWAYS keep its cursor in the r12 buffer when r12 is
  live, falling back to the stack form only for choices in `main` with no r12.
  Cleaner alternative: always use r12 — top-level main also allocates a buffer.
  RECOMMEND: always-r12; main's PL_ENTRY allocates a buffer too. Removes the
  dual cursor-location problem entirely and makes Step B and C use one mechanism.)

**SCOPE for first cut:** single rightmost BB_CHOICE per callee body. Nested
choices (a clause body containing its own `;`) need a tagged cursor (which choice
+ which clause) — defer to a CAT-A-3 follow-up rung. rung02/05/06 are all
single-choice, so the common case lands first.

### Step D — verify + measure

Run rung02_facts, rung05_backtrack, rung06_lists first (the canonical targets),
then the full 107-fixture loop:
```
for f in corpus/programs/prolog/rung*.pl; do
  got=$(bash scripts/run_prolog_via_x86_backend.sh "$f" 2>/dev/null)
  [ "$got" = "$(cat ${f%.pl}.expected)" ] && echo PASS || echo FAIL
done
```
Expected +15–25. Then GATE-1/2/3/4 + sibling smokes + FACT RULE grep (must stay
0 — all new bytes are template-emitted) + `bb_emit_byte` abort check.

## Open design questions for Lon (flagged, not blocking the plan)

1. **r12 resume-buffer ABI** vs a TLS global `g_pl_resume_buf`. RECOMMEND r12
   (WAM-spirit, no global state, nesting-safe). Chosen unless Lon objects.
2. **always-r12** (main allocates a buffer too) vs dual stack/r12 cursor
   location. RECOMMEND always-r12 — unifies Step B and C, kills the
   cursor-location reconciliation. Leaning this way for the implementation.
3. **single-rightmost-choice scope** for first cut — nested choices deferred.
   RECOMMEND accept; rung02/05/06 don't need nesting.

## Files touched this session

```
src/runtime/rt/rt.c               +13  (pl_bb_env_install + comment)
src/runtime/interp/pl_runtime.h    +3  (declaration + comment)
```

## NEXT

1. **CAT-A-3 Steps B–D** (this design) — biggest mode-4 unlock. Fresh context.
2. PJ-AGW-5 (rung07 cut-barrier ω-rewiring).
3. rung18 plus/3 bidirectional (3 OPEN; investigate the claimed-complete mode-2 arm).
4. term_to_atom + term_string mode-4 emit (paired CAT-D-*).
