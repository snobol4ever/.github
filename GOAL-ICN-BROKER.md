# GOAL-ICN-BROKER.md — Icon Value-Generator Byrd Box Broker

**Repo:** one4all
**Done when:** All Icon goal-directed backtracking (generators, scan, suspend) routes
through a brokered Byrd-box driver mirroring SNOBOL4's interp_eval_pat + exec_stmt +
bb_build architecture, at the IR interpreter level.

---

## Motivation

SNOBOL4 at the IR level:
  1. `interp_eval_pat(e)` — walks IR tree, builds PATND_t via pat_cat/pat_alt/pat_lit
  2. `exec_stmt(subj, pat, ...)` — calls bb_build(PATND_t*) → root bb_box_fn
  3. Phase 3 broker loop: root.fn(ζ, α) → β re-entries → ω (string-cursor typed)

Icon generators are the same four-signal model (α/β/γ/ω) but value-typed (DESCR_t)
rather than string-cursor typed (spec_t). The architecture must be identical:
  1. `icn_eval_gen(e)` — walks IR tree, builds icn_gen_t (DESCR_t-typed Byrd box)
  2. `icn_exec_gen(subj, gen, body_fn)` — drives broker loop
  3. Broker loop: gen.fn(ζ, α) → β re-entries → ω (value typed)

Current scrip.c uses ad-hoc icn_drive/icn_gen_stack/icn_coro_table instead.
This goal replaces all of it with the brokered architecture.

---

## Steps

- [ ] **B-1** — Define icn_box_fn type and icn_gen_t struct.
  `typedef DESCR_t (*icn_box_fn)(void *zeta, int entry);`
  `typedef struct { icn_box_fn fn; void *zeta; } icn_gen_t;`
  Mirrors bb_box_fn / bb_node_t in bb_box.h.
  Place in new file: src/frontend/icon/icon_gen.h
  Gate: header compiles cleanly.

- [ ] **B-2** — Implement icn_broker loop.
  `int icn_broker(icn_gen_t gen, void (*body_fn)(DESCR_t, void*), void *arg);`
  Loop: gen.fn(ζ, α) → if not FAIL: body_fn(val, arg), then gen.fn(ζ, β) → repeat → ω.
  Returns tick count (number of values produced).
  Mirrors Phase 3 of exec_stmt. Place in src/frontend/icon/icon_gen.c
  Gate: compiles; unit test with a hand-built constant box.

- [ ] **B-3** — Implement icn_bb_to: E_TO Byrd box.
  State: lo, hi, cur. α: init cur=lo; if cur>hi → ω; push cur, γ.
  β: cur++; if cur>hi → ω; push cur, γ.
  Replaces icn_drive E_TO + icn_gen_stack.
  Gate: every (1 to 5) via broker → 5 ticks.

- [ ] **B-4** — Implement icn_bb_to_by: E_TO_BY Byrd box.
  State: lo, hi, step, cur. α/β: same as B-3 with step.
  Gate: every (1 to 10 by 2) → 1,3,5,7,9.

- [ ] **B-5** — Implement icn_bb_iterate: E_ITERATE (!str) Byrd box.
  State: str, pos, len. α: pos=0; β: pos++. γ: return char at pos.
  Replaces icn_drive E_ITERATE.
  Gate: every !("abc") → a, b, c.

- [ ] **B-6** — Implement icn_bb_suspend: E_SUSPEND Byrd box (coroutine).
  Wraps the ucontext coroutine machinery already in icn_coro_table.
  α: start coroutine (fresh call). β: swapcontext resume.
  ω: coroutine exhausted.
  Replaces icn_coro_table direct use.
  Gate: rung03 5/5 via broker.

- [ ] **B-7** — Implement icn_bb_find: find() generator Byrd box.
  State: needle, haystack, pos. α: first match. β: next match.
  Replaces icn_drive E_FNC("find") special case.
  Gate: rung08 find_gen via broker.

- [ ] **B-8** — Implement icn_eval_gen(e) → icn_gen_t.
  Mirrors interp_eval_pat: walks EXPR_t tree, returns icn_gen_t.
  Dispatch: E_TO→icn_bb_to, E_TO_BY→icn_bb_to_by, E_ITERATE→icn_bb_iterate,
  E_SUSPEND→icn_bb_suspend, E_FNC(find)→icn_bb_find,
  E_FNC(user-gen-proc)→icn_bb_proc_call.
  Non-generators: wrap interp_eval result as a one-shot box.
  Gate: icn_eval_gen covers all nodes hit by rung01-11.

- [ ] **B-9** — Wire E_EVERY in interp_eval through icn_broker.
  Replace icn_drive(gen,gen) and icn_has_suspend_call path with:
    icn_gen_t g = icn_eval_gen(gen); icn_broker(g, body_cb, body_node);
  Remove icn_drive, icn_gen_stack, icn_gen_push/pop, icn_gen_active.
  Gate: rung01-11 59/59 PASS via broker; no icn_drive remaining.

- [ ] **B-10** — Remove all ad-hoc backtracking machinery from scrip.c.
  Delete: icn_drive, icn_gen_stack/depth/push/pop/active/lookup,
          icn_has_suspend_call, icn_coro_table direct dispatch in E_FNC.
  Gate: make scrip clean; 59/59 PASS; SNOBOL4 regression unchanged.

- [ ] **B-11** — Update PLAN.md and GOAL-ICON-IR-RUN.md done.

---

## Key files
| File | Role |
|------|------|
| `src/frontend/icon/icon_gen.h` | icn_box_fn, icn_gen_t, icn_broker — new |
| `src/frontend/icon/icon_gen.c` | Box implementations + broker loop — new |
| `src/runtime/x86/bb_box.h` | Model: bb_box_fn, bb_node_t, α/β ports |
| `src/runtime/x86/stmt_exec.c` | Model: exec_stmt Phase 3 broker loop |
| `src/driver/scrip.c` | Wire icn_eval_gen + icn_broker into E_EVERY |

---

## Rules
- No push until "perform hand off".
- Commit identity: LCherryholmes / lcherryh@yahoo.com.
- Build gate: make scrip clean + rung01-11 score non-regressing after every step.
- Mirror bb_box.h / exec_stmt architecture exactly — same four signals, same loop.
- One box per step. Gate on its rung. Do not batch.
