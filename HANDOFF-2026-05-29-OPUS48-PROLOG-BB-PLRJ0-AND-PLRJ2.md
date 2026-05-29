# HANDOFF — Prolog BB: PLR-J-0 + PLR-J-2 (Opus 4.8, 2026-05-29)

**Author:** Claude Opus 4.8
**Goal:** GOAL-PROLOG-BB.md (PLR-J JCON/ICON four-port transliteration ladder)
**Repos pushed:** one4all `751c5f10`, .github `8206c250`
**Net:** two ladder rungs closed (PLR-J-0 → PLR-J-2), both `lower_pl.c`-only,
lower-time-only, **byte-identical output**, FACT 0. No emitter/template/runtime change.

---

## What landed

### PLR-J-0 — `bounded`/determinacy flag at lower time (one4all `e2d99c3d`)

Added the pure classifier `pl_goal_is_bounded(const tree_t *e)` in `src/lower/lower_pl.c`
(immediately above `lower_pl_goal`, with a forward decl in the static block). Transliterates
JCON irgen.icn **F1**: every `ir_a_*` proc guards its resume chunk with
`/bounded & suspend ir_chunk(p.ir.resume, …)`; a *bounded* construct (≤1 solution) emits no
resume wiring at all. The classifier answers "does this goal offer ≤1 solution?" as a pure
function of the parse tree — computed inline as JCON does, so **no `BB_t` field (PEERS RULE
clean) and no sidecar**.

- **Bounded** (β/resume port is dead): cut, `true`/`fail`/`otherwise`/`nl`, unification,
  arithmetic comparison (`> < >= <= =:= =\=`), every `pl_builtin_style` table builtin
  (write/is/type-test/atom-string/sort/format/…), and a conjunction or ITE all of whose
  components are bounded.
- **NOT bounded**: disjunction `;`, user-predicate calls (multi-clause can re-satisfy),
  bare-var meta-calls, anything unrecognized. **Conservative by construction** — a wrong
  answer only ever keeps today's unconditional-β behaviour.

**POPULATED-BUT-UNUSED this rung** (read later by PLR-J-2 / WAM-CP-12), so output is
byte-identical. Populated + provable via env-gated trace `SCRIP_PL_BOUNDED_TRACE=1`
(default OFF, stderr only, no emitted bytes — same pattern as `SCRIP_LCO_TRACE` /
`SCRIP_IDX_TRACE`). Verified: `main :- X is 2+3, X>4, write(X), nl, (X=:=5;X=:=6), foo(X).
foo(Y):-Y>0.` traces `is/write/nl/>/=:= → bounded=1`, `foo (user call) → 0`, `; → 0`;
program output `5` unchanged.

### PLR-J-2 — explicit per-node resume predicate (one4all `751c5f10`)

Replaced the inline `(t==BB_PL_CALL||t==BB_CHOICE||t==BB_PL_ALT)` resumable tests scattered
in `lower_pl_new_Conj` (the `gβ[]` redo wiring, two loops) and `lower_pl_clause_body` (the
body backtrack chain) with one named predicate `pl_node_is_resumable(const BB_t *)`,
transliterating JCON irgen.icn **F2/F3**: the resume/redo edge is wired by name, never by a
runtime nearest-resumable-predecessor search. It is the **dual of PLR-J-0's
`pl_goal_is_bounded`** — a bounded goal's β port is dead → non-resumable; an unbounded goal
(user call, clause choice, inline disjunction) is resumable → the conjunction threads a redo
edge into it.

Resumable set = `{BB_PL_CALL, BB_CHOICE, BB_PL_ALT}` — **BYTE-IDENTICAL** to the structural
test it replaces for every node kind the lowerer emits today. `BB_PL_ITE` stays
non-resumable to the enclosing SEQ (it owns its own internal β), exactly as before. Closes
**PL-LOWER-REVAMP gap (2)**.

**Redo edge verified directly:** `pick(1).pick(2).pick(3). main :- pick(X), X>=2, write(X), nl.`
prints `2` (the failing `X>=2` redrives `pick/1` past `X=1`); the `…,fail. main.` backtrack-all
variant enumerates `2` then `3`.

---

## Why these two together, in this order

The PLR-J ladder dependency order is `PLR-J-0 → {PLR-J-1 done} → PLR-J-2 → PLR-J-3 done →
PLR-J-4 → PLR-J-5`. PLR-J-0 is the prerequisite the PL-LOWER-REVAMP note called "no
`bounded`/determinacy flag"; PLR-J-2 is the structural fix it called gap (2). Both are
lower-time-only and byte-identical, which is the safest possible pair to land before the
heavy binary-emission rung (PLR-J-4). PLR-J-0 establishes the *concept* (bounded ⇔ ≤1
solution); PLR-J-2 makes the *consumer* (the redo-edge decision) explicit and names the seam.
Today they agree with the prior structural heuristic on every node kind, so nothing moves —
the value is structural clarity plus a single extension point for negation / findall-goal /
CP-elision.

---

## Gates (byte-identical across both rungs, verified on pushed HEAD `751c5f10`)

| Gate | Result |
|---|---|
| GATE-1 smoke | 5/5 |
| GATE-2 crosscheck | 11 PASS / 121 (5 ORACLE_MISS=0) |
| GATE-3 rung suite (mode-2) | 104/107 |
| GATE-4 mode-4 minimal | 4/4 |
| GATE-SWI plunit | 57/57 (100%) |
| FACT grep | 0 |
| siblings icon/raku/snobol4 | 5/5/13 |

---

## NEXT — PLR-J-4 (largest single win)

Callee-block sweep in the `SM_BB_PL_INVOKE` **MEDIUM_BINARY** arm
(`src/emitter/SM_templates/sm_bb_switch.cpp`) **in lockstep with** the
`bb_pl_call.cpp` **MEDIUM_BINARY** call protocol. Current state confirmed this session:

- The `bb_pl_call.cpp` MEDIUM_BINARY arm (lines ~39–43) is a **double-jump stub**
  (`jmp ω; jmp ω`); the full call protocol (build args, `pl_bb_env_save_push`,
  `pl_bb_bind_arg`, `call .Lplpred_<name>_<arity>`, `rt_last_ok` test, caller-env
  save/restore, `_redo` β path) exists **only in the MEDIUM_TEXT arm** (lines ~44–119).
- The `SM_BB_PL_INVOKE` BINARY arm has a **DEFER GUARD** (`sm_bb_switch.cpp` ~line 264–278):
  if the program defines >1 user predicate it sets `g_sm_native_unsupported` and stubs, so
  `--run` aborts honestly. The TEXT arm's callee-block loop (`pl_emit_callee_block_body`,
  lines ~376–418) must be ported into the BINARY arm so all callee blocks emit into the
  **same scratch buffer** as the entry, letting `bb_emit_end()` resolve the cross-block
  `call .Lplpred_*` and `_redo → β` rel32 patches.

**Label contract** (both sides already agree, via `pl_call_block_label` in
`src/emitter/emit_bb.c:565`): `.Lplpred_<sanitized-name>_<arity>` and `<…>_redo`. In TEXT the
assembler resolves these; in BINARY the call site must emit `E8 + rel32` patched against a
`bb_label_t` that the callee-block loop `bb_label_define`s in the same scratch session — so
**4a (port the call protocol) and 4b (callee sweep + drop the guard) are coupled** and must
land together (or 4a leaves dangling patches). The goal file authorizes splitting only if a
session can't hold both; if split, land 4a's call-site bytes guarded so they're never reached
until 4b defines the labels.

**Helpers are all real C symbols** (verified): `pl_bb_env_save_push`, `pl_bb_bind_arg`,
`pl_bb_env_install`, `pl_bb_env_pop`, `rt_pl_cp_save_caller_env`, `rt_last_ok`,
`pl_cp_current`. In BINARY use `movabs rax,&helper; call rax` (no PLT). **`pl_choice` offsets
confirmed:** `env` at +24, `saved_args` (caller_env) at +40 — matching the TEXT arm's
`[rax+24]` / `[rax+40]`. The PLR-J-3 `emit_build_compound_term_bin` in `bb_builtin.cpp` is the
reference for the byte idioms (movabs for interned strings + helpers, aligned slot frames).

**Gate for PLR-J-4:** `rung02_facts` + `rung08_recursion` mode-3 byte-match mode-2; the 11
existing crosscheck PASS unaffected; FACT 0. This unblocks the 121 open mode-3 crosscheck
failures (all multi-predicate programs).

Alternative if PLR-J-4 is deferred: **PLR-J-5** (BB_CHOICE as `ir_a_Alt` transliteration +
gprolog untrail-before-retry / trust ordering) — but it depends on PLR-J-4 (callee blocks to
backtrack into), so PLR-J-4 should go first.

---

## Files touched

- `src/lower/lower_pl.c` — `pl_goal_is_bounded` (+ fwd decl + env-gated trace in
  `lower_pl_goal`), `pl_node_is_resumable` (+ two call-site swaps in `lower_pl_new_Conj` and
  `lower_pl_clause_body`). ~74 lines total across both rungs, lower-time only.
- `.github/GOAL-PROLOG-BB.md`, `.github/PLAN.md` — watermarks + step checkboxes + NEXT
  pointers.

Develop and verify against mode-2 (`--interp`, the correctness reference) throughout, per the
goal file's mandate.
