# HANDOFF 2026-05-27 — Sonnet — PROLOG-BB: AGW-9 CLOSED (GATE-4 2/4 → 4/4)

**Goal:** GOAL-PROLOG-BB.md — V-3 / AGW-9B-2 + AGW-9B-3 (multi-clause choice + `;` disjunction).
**Result:** ✅ **GATE-4 4/4. AGW-9 STRUCTURAL TEMPLATES CLOSED.** All five Prolog four-port templates
now FILLED; mode-4 standalone x86 executes `p(a). p(b). main :- p(X), write(X), nl.` and prints `a`,
and `main :- ( true ; true ), write(ok), nl.` and prints `ok`. Three latent pre-existing bugs found
and fixed in passing. No regressions in GATE-1/2/3 or any cross-language smoke gate.

## Gate ledger (clean rebuild, this session)
- GATE-1 smoke prolog: **5/5** ✅
- GATE-2 crosscheck:    **132/0** ✅ (ORACLE_MISS 5 unchanged)
- GATE-3 rung interp:   **88/107** ✅ (UNCHANGED — mode-2 transparent)
- GATE-4 mode-4 rung:   **4/4** ✅ (m4-seq + m4-call + m4-choice + m4-alt all PASS)
- Emptiness audit:      **EMPTY=0 / FILLED=5** ✅ ("AUDIT GREEN — AGW-9 closed")
- Cross-lang smoke:     icon 5/5, snocone 5/5, rebus 4/4, raku 5/5 ✅

## What landed (template-pure throughout — every emitted byte from a `bb_*` / `sm_*` template)

### Templates filled (V-3 closure)
- **`bb_pl_choice.cpp`** (was EMPTY → FILLED): dispatcher for BB_CHOICE. At `_.lbl_α` emits
  `jmp .Lplch<id>_c0_pre`, then each `.Lplch<id>_c<i>_pre:` block: clause 0 emits
  `call rt_pl_trail_mark_push@PLT`; clauses 1..n-1 emit `call rt_pl_trail_unwind_top@PLT`
  (rewind to the entry checkpoint); both then `jmp .Lplch<id>_c<i>_body`. β (redo) routes to ω
  for now (deterministic first-solution; stateful resumable choice is a later rung). Labels are
  reconstructed at template time via `pl_choice_clause_label(_.pl_choice_id, i, "pre"/"body")`,
  matching the driver's mint scheme.
- **`bb_pl_alt.cpp`** (was EMPTY → FILLED): identical dispatcher, n=2 (BB_PL_ALT.α/β are the two
  branch entry nodes; their γ/ω are pre-wired by lower_pl so the bodies self-chain).
- **`bb_succeed.cpp`** (NEW): minimal leaf template emitting `α: # BOX SUCCEED() ; jmp γ ; β: jmp ω`.
  Replaces the fall-through to `bb_limit` for `BB_SUCCEED` (which is what `true`/`otherwise` lower
  to). Routed via `emit_core.c` (was `case BB_SUCCEED: ... fall to bb_limit`; now `bb_succeed(nd)`).

### Byte-free drivers (`emit_bb.c`)
- `pl_choice_bodies_em(nd, out, max)` — emit-time accessor that walks `bb_pl_choice_state_t->bodies[]`
  and returns each clause's `BB_graph_t->entry`. Mirrors `pl_seq_goals_em`.
- `pl_choice_clause_label(dst, dsz, id, ci, suffix)` — shared `.Lplch<id>_c<i>_<suffix>` label
  scheme used by both the driver (label minting) and templates (label reconstruction).
- `flat_drive_pl_choice(nd, γ, ω, β)` — mints per-clause `pre/body/beta` labels, stashes
  `id` + `n` in `g_emit.pl_choice_id` / `pl_choice_n`, calls `EP_FILL` (which dispatches to the
  template, emitting the dispatcher), then lays each clause's body via `walk_bb_flat` with
  `γ=γ_in` (shared success), `ω=next_pre` (or `ω_in` for the last), `β=cβ[i]`.
- `flat_drive_pl_alt(nd, γ, ω, β)` — same pattern, n=2, branches are `nd->α` + `nd->β`.
- `walk_bb_flat` switch: new `case BB_CHOICE:` / `case BB_PL_ALT:` route to the drivers;
  new `case BB_SUCCEED:` populates `xa_bb_ep_*` with a single `EP_JMP(γ)` and falls through
  via `EP_FILL` to `bb_succeed.cpp`; `case BB_FAIL:` routes to existing `bb_fail.cpp`.

### Effect helpers (rt.c — KEEP side, no port logic)
- `rt_pl_trail_mark` / `rt_pl_trail_unwind` (int return / int arg) — simple wrappers over the
  trail. Not used by the dispatchers but added for completeness.
- `rt_pl_trail_mark_push` / `rt_pl_trail_unwind_top` / `rt_pl_trail_mark_pop` — saved-mark stack
  (depth 32). The dispatcher pushes a fresh mark at entry; each `pre[i>0]` unwinds to the top
  mark so failed clause bindings are undone before the next attempt. Pop is unused on the
  first-solution path (success exits via γ; final fail exits via ω); resumable choice will pop
  when the choice exhausts. Pure side effect — no γ/ω decision lives here.
- `pl_bb_env_save_push(nslots)` (in `pl_runtime.c`) — returns the caller's previous `g_pl_env`
  so the BB_PL_CALL site can restore it after the callee returns. The existing `pl_bb_env_push`
  is fire-and-forget (caller leaks); this variant is the disciplined replacement for call sites.
- `pl_bb_bind_arg(slot, caller_term)` (in `pl_runtime.c`) — in the CURRENT (callee) env, create
  `term_new_var(slot)`, store at `g_pl_env[slot]`, and `unify` it with the caller-supplied Term*.
  The unify records on the trail so the binding is visible to the caller via TERM_REF aliasing
  AND undoable on failure. Pure effect.

### Three latent pre-existing bugs fixed (exposed by m4-choice — the first GATE-4 row to bind+read a variable across a call)

#### Bug A — `BB_PL_CALL` had no arg-passing prologue
`bb_pl_call.cpp` only emitted `call <block>` + last_ok test. m4-call (`greet/0`) didn't notice because
no args. m4-choice (`p(X)`) needs the caller's `X` bound to whatever the callee unifies. **FIX:**
the template now emits a full prologue:
1. For each arg in `zc->args[]`: build a caller-side `Term*` via `rt_pl_node_to_term(kind, ival, sval, dval)`,
   push on stack.
2. `mov edi, arity+16; call pl_bb_env_save_push@PLT; push rax` — saved caller env on stack, fresh callee env installed.
3. Stack-alignment pad (`sub rsp, 8`) if (n_args + 1) is odd.
4. For each arg in reverse: `mov rsi, [rsp + offset]` (caller-Term), `mov edi, slot`, `call pl_bb_bind_arg@PLT`.
5. `call <callee_block>`.
6. Unwind pad, `pop rdi; call pl_bb_env_pop@PLT`, drop arg-Term stack, then test last_ok → γ/ω.

The callee block in `sm_bb_switch.cpp` PL_ENTRY no longer emits its own `pl_bb_env_push` (the call
site handles env switching). Replaced with a comment marking that responsibility moved.

#### Bug B — `bb_prepare_pl` swapped channel for (VAR, ATOM) unify
For `BB_UNIFY` with α=BB_PL_VAR, β=BB_ATOM, the code set `bb_pl_ls = β->sval` (atom's name) but
left `bb_pl_rs = NULL`. The unify template reads `_.bb_pl_ls` for the LHS operand and `_.bb_pl_rs`
for the RHS, so the atom's `.S<n>` label was attached to the LHS (a BB_PL_VAR, which ignores sval)
and the RHS BB_ATOM was emitted with NULL sval → `prolog_atom_intern(NULL)` defaulted to `"[]"`.
**Result:** unifying `X = a` was binding X to `"[]"` instead of `"a"`. **FIX:** change the assignment
to `bb_pl_rs = β->sval` (correct channel for the RHS). One-line fix, big impact.

#### Bug C — `rt.c` lacked `prolog_atom.h` include + `rt_init` didn't initialize the atom table
Two latent issues compounding:
1. `rt.c` did not `#include "prolog_atom.h"`, so calls like `const char *nm = prolog_atom_name(t->atom_id)`
   compiled against an implicit declaration `int prolog_atom_name(int)`. The 64-bit pointer return
   was truncated to a sign-extended 32-bit value (e.g., `0x7ffff750f800` → `0xfffffffff750f800`),
   then `fputs` segfaulted on the garbage address. **Symptom:** `write(atom)` mode-4 segfault.
2. `rt_init` didn't call `prolog_atom_init()`, so the canonical reserved atoms (`.`, `[]`, `true`,
   `fail`, `!`) weren't pre-loaded. The first user atom interned (whatever it happened to be) got
   id 0. **Symptom:** atom ids leaked across runs and shifted by the order of interning.
**FIX:** include `prolog_atom.h` in rt.c; add `prolog_atom_init()` to `rt_init` right after
`trail_init`. These were lurking under m4-call success (no atom output).

### Globals + headers
- `sm_emit_t.pl_choice_id` / `pl_choice_n` — int fields stashed by the choice/alt drivers,
  read by the templates to reconstruct the per-clause label scheme.
- `pl_choice_clause_label` declared in `emit_bb.h`; `bb_succeed` declared in `bb_templates.h`.
- New `bb_succeed.cpp` added to the Makefile (both the source list and per-file compile rules).

## Open work

### V-4 — retire `rt_pl_b_*` runtime BB-rebuild path
`xa_pl_builder.cpp` still emits the `rt_pl_b_begin/_node/_kids/_entry/_end_register` runtime reconstruction
of the BB graph at standalone-binary startup (RULES.md "no runtime BB walk", AGW-1c exception). Every
predicate is now flat-emitted as a callable block under `.Lplpred_<name>_<arity>` (call sites
`call` directly, never through the registry). The graph reconstruction is dead code; delete:
- `codegen_pl_predicate_registry` (emit_sm.c) — emits `XA_PL_BUILDER` + `XA_PL_REGISTRY_TABLE`
- the `rt_register_predicates_pl` call from emitted `main`
- the `rt_pl_b_*` family from `rt.c` / `rt.h`
- the `XA_PL_BUILDER` / `XA_PL_REGISTRY_TABLE` / `XA_PL_SUB_BUILDER` / `XA_PL_KIDS_RODATA` opcodes
  + their templates

**Gate:** `grep rt_pl_b_ out.s == 0` and `grep rt_register_predicates_pl out.s == 0`; GATE-4 still 4/4.

### V-5 — Prolog `--run` flat-emit path
`scrip.c:432/441/446` route Prolog `--run` (mode 3) through `sm_run_with_recovery(&s2->sm, sm_interp_run)`
→ the C BB walker. RULES.md AGW-1c sanctions this *until the bb_pl_*.cpp templates land*. They've now
landed (V-3 closed). Route `--run` through `sm_emit_linear`→`sm_run_linear` flat-blob path (in-proc
PROT_EXEC buffer); delete the Prolog branch at scrip.c:423-446; remove the AGW-1c exception text
from RULES.md.

### V-6 — confirm `pl_bb_dcg` / `bb_exec_*` are mode-2-only
After V-4/V-5, `pl_bb_dcg` (C Byrd box; the mode-2 reference walker) must be reachable ONLY from
`sm_interp_run` dispatch. Audit + document in the watermark; do NOT delete `bb_exec_*` (mode 2
needs it).

### Stateful resumable choice/alt
The dispatchers currently route β (redo) to ω (`jmp .Lplent0_ω` shape). The mode-2 `BB_CHOICE` case
in `bb_exec.c` is heavily stateful (zc->cur cursor, last_body resume via `bb_exec_resume` of inner
live choice points). Mode-4 β path: walk forward from `zc->cur` to the next un-tried clause, unwind
trail, retry. This is the "advance cursor" path; the harder "resume inner choice" path is the
recursive `bb_body_has_live_choice` discipline mirrored as emitted x86. Needed for rungs that
backtrack into multi-clause predicates (e.g., `member/2`-style enumeration).

### Builtin rungs (mode-2 ladder)
`rung18` plus/3 bidirectional, `rung25` term_to_atom operator-notation writer, `rung28` catch/throw,
AGW-5 stateful committed-ITE, runtime assertz-in-body. None blocked by AGW-9.

## Files touched

```
Makefile                                         (+2)   bb_succeed.cpp added
src/emitter/BB_templates/bb_pl_alt.cpp           (~)    EMPTY → FILLED (dispatcher)
src/emitter/BB_templates/bb_pl_call.cpp          (~)    full arg-passing prologue/epilogue
src/emitter/BB_templates/bb_pl_choice.cpp        (~)    EMPTY → FILLED (dispatcher)
src/emitter/BB_templates/bb_succeed.cpp          (NEW)  leaf template for Prolog `true`
src/emitter/BB_templates/bb_templates.h          (+1)   bb_succeed decl
src/emitter/SM_templates/sm_bb_switch.cpp        (~)    callee block: remove env_push (moved to call site)
src/emitter/emit_bb.c                            (+~)   flat_drive_pl_choice / _alt, pl_choice_bodies_em,
                                                       pl_choice_clause_label, walk_bb_flat cases,
                                                       bb_prepare_pl (VAR,ATOM) channel fix
src/emitter/emit_bb.h                            (+1)   pl_choice_clause_label decl
src/emitter/emit_core.c                          (~)    BB_SUCCEED → bb_succeed (was bb_limit)
src/emitter/emit_globals.h                       (+2)   pl_choice_id / pl_choice_n fields
src/runtime/interp/pl_runtime.c                  (+~)   pl_bb_env_save_push / pl_bb_bind_arg
src/runtime/interp/pl_runtime.h                  (+2)   decls
src/runtime/rt/rt.c                              (+~)   rt_pl_trail_{mark,unwind,mark_push,
                                                       unwind_top,mark_pop}; prolog_atom.h include;
                                                       prolog_atom_init() in rt_init
src/runtime/rt/rt.h                              (+8)   decls
```

## Architectural notes

The "every byte from a template" discipline held throughout. Drivers stay byte-free:
- `flat_drive_pl_choice` / `flat_drive_pl_alt` mint labels (`emit_label_initf`), call
  `emit_label_define_bb` (label-def is structure, not bytes), recurse via `walk_bb_flat`,
  and stash `id` + `n` in `g_emit` for the template. Zero `bb_emit_byte`, zero `s_2asm`,
  zero raw opcodes in the driver.
- Templates `bb_pl_choice.cpp` / `bb_pl_alt.cpp` are the sole emitters of the per-clause
  trail `call`s + dispatcher `jmp`s. They reconstruct labels via the shared
  `pl_choice_clause_label` helper.
- The new effect helpers (`rt_pl_trail_*`, `pl_bb_env_save_push`, `pl_bb_bind_arg`) are pure
  side-effect / conversion routines — no `DESCR_t` returns, no `entry` selector, no port
  decisions. The emitted x86 owns γ/ω via `rt_last_ok` (call template) or per-clause `jmp`
  chains (choice/alt template).
