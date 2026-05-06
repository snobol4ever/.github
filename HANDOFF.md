# HANDOFF — session 2026-05-05 (CHUNKS Steps 1, 2, 3-prep) → next session

## Context-window saturation

This session ended at ~85% context after landing three commits on the
GOAL-CHUNKS axis:

  1. **CHUNKS Step 1 LANDED** — one4all `a79b09f0`.  Scaffolding:
     `SmChunk_t` struct, `SM_PUSH_CHUNK` and `SM_CALL_CHUNK` opcodes,
     FATAL stubs, full 7-site audit in `docs/CHUNKS-step01-audit.md`.

  2. **CHUNKS Step 2 LANDED** — one4all `1b42498f`.  Migrated
     `sm_lower.c:573` (E_DEFER `*expr`).  `SM_CALL_CHUNK` opcode
     implemented in interp + codegen with minimal SmCallFrame
     (`retval_name=NULL`).  `SM_RETURN` patched in both runners to read
     top-of-stack when `retval_name == NULL`.  `EVAL(*expr)`
     special-cased in E_FNC lowering — emits chunk body inline +
     `SM_CALL_CHUNK` directly, bypassing `SM_CALL "EVAL"` and keeping
     execution on the same SM stack (per Lon's principle: "code is
     code; one push and pop is as good as another").

  3. **CHUNKS Step 3 prep LANDED** — one4all `55eb4e03`.  Fix for
     pre-existing latent bug in `sm_label_pc_lookup` exposed by chunk
     emission.  Stored-chunk path now works: `E = *X; OUTPUT = EVAL(E)`
     prints `WORLD` on `--sm-run` and `--jit-run`.  Step 3 producer
     migration (`sm_lower.c:470`) NOT yet done — consumer infra ready.

All gates green at every commit.  Three one4all commits, one .github
commit, all pushed.

  * one4all `a79b09f0` — CHUNKS Step 1 (scaffolding + audit)
  * one4all `1b42498f` — CHUNKS Step 2 (E_DEFER `*expr`; SM_CALL_CHUNK)
  * one4all `55eb4e03` — CHUNKS Step 3 prep (sm_label layout fix +
                         consumer infra: sm_call_chunk, EXPVAL_fn, pat_to_patnd)
  * .github  `d0a5bae`  — Steps 1+2 marked closed; PLAN updated to CH-3

---

## What was done

### Step 1 — scaffolding (commit `a79b09f0`)

Pure addition.  No behavior change.

- `sm_prog.h` — `SmChunk_t` struct (`entry_pc`, `arity`); `SM_PUSH_CHUNK`
  and `SM_CALL_CHUNK` opcodes added after `SM_PUSH_EXPR`.
- `sm_interp.c` / `sm_codegen.c` — `fprintf+abort` stubs.
- `sm_prog.c` — opcode names in name table.
- `docs/CHUNKS-step01-audit.md` — 7 sites classified by E_kind +
  consumer + migration step.  Lon's optimization observation noted:
  for `*P` where P is already a compiled pattern/BB chunk,
  `SM_PUSH_CHUNK` could bake in the existing `entry_pc` with no fresh
  body — recorded for a later optimization pass; Step 2 emits the
  general form for correctness first.

### Step 2 — E_DEFER `*expr` in value context (commit `1b42498f`)

The E_DEFER lowering at sm_lower.c:573 now emits:

    SM_JUMP skip
    SM_LABEL entry_pc        <- chunk entry
    lower_expr(child)
    SM_RETURN
    SM_LABEL skip
    SM_PUSH_CHUNK entry_pc, 0

The DT_E descriptor carries `slen=1, i=entry_pc` (slen=0 = legacy
EXPR_t* path; both paths coexist while migration completes).

`SM_CALL_CHUNK` handler in `sm_interp.c` and `sm_codegen.c`: pushes a
minimal `SmCallFrame` (caller's stack saved, `ret_pc=st->pc`,
`retval_name=NULL`, `nsaved=0`), sets `pc=entry_pc`, lets `SM_RETURN`
unwind naturally.

`SM_RETURN` and `h_return_impl` patched: when `fr->retval_name == NULL`
(chunk thunk), read result from top of chunk's value stack instead of
`NV_GET_fn(retval_name)`.  Same patch applied to the `is_nret` branch
(NAMEVAL push).

`EVAL(*expr)` in E_FNC case at sm_lower.c — when sole arg is E_DEFER,
emit chunk body inline + `SM_CALL_CHUNK` directly.  No `SM_CALL "EVAL"`,
no `EXPVAL_fn` C dispatch.  Lon's inline case: code is code; running it
via SM_CALL_CHUNK is no different than any other call.

### Step 3 prep — `sm_label` layout fix + stored-chunk path (commit `55eb4e03`)

Stored-chunk crash root cause (latent for years, exposed by Step 2):

`sm_label_pc_lookup` (sm_prog.c:126) walks all `SM_LABEL` instructions
calling `strcmp(p->instrs[i].a[0].s, name)` for named-function dispatch.
Two emitters use SM_LABEL with **incompatible operand layouts**:

    sm_label():        a[0].i = target_pc           /* unnamed */
    sm_label_named():  a[0].s = name; a[1].i = pc   /* named */

The lookup's `a[0].s &&` guard didn't help: when `sm_label()` set
`a[0].i = 5` (entry_pc), the union aliased `a[0].s` to
`(const char *)5` — non-null garbage, segfault on `strcmp`.

Pre-CHUNKS, unnamed labels never sat between an `SM_CALL` and the
lookup walk — they were always behind forward jumps for if/while.
Step 2's chunk bodies put unnamed labels right in program flow,
scanned on every named-fn dispatch.

**Fix:** `sm_label()` now stores PC in `a[1].i` (matching named-label
layout) and leaves `a[0]` zeroed (via `_grow`'s memset).  Verified by
grep: no other reader of unnamed-label `a[0].i` exists; only
`sm_patch_jump` touches the JUMP's `a[0].i`, not the LABEL's.

Consumer infrastructure for stored chunks now works:

- `sm_call_chunk(int entry_pc)` — runs a chunk on a heap-allocated
  nested `SM_State` (own value stack, shared NV table — `SM_State` is
  ~512KB due to embedded 256-frame call array; can't go on the C
  stack).  `setjmp`/`memcpy` of `g_sno_err_jmp` gives local error
  isolation so chunk errors don't longjmp into outer dispatch's
  jmp_buf.
- `EXPVAL_fn` for chunk DT_E (slen==1) — routes via `sm_call_chunk`.
- `pat_to_patnd` for chunk DT_E — dispatches via `EXPVAL_fn` through a
  new `coerce:` label (skips the EXPR_t IR walk).

Inline case (Step 2): `EVAL(*X)` → `WORLD` ✓ (`sm-run`, `jit-run`).
Stored case (Step 3 prep): `E=*X; OUTPUT=EVAL(E)` → `WORLD` ✓
(`sm-run`, `jit-run`, `ir-run` all match).

---

## Where this leaves the goal

GOAL-CHUNKS — Eliminate SM_PUSH_EXPR

  - [x] Step 1 — Survey + scaffolding
  - [x] Step 2 — Migrate sm_lower.c:573 (E_DEFER `*expr`)
  - [ ] **Step 3** — Migrate sm_lower.c:470 (pattern non-QLIT arg, SM_PAT_USERCALL_ARGS)
  - [ ] Step 4 — Migrate sm_lower.c:326/345/386 (E_FNC sub-args, SM_PAT_CAPTURE_FN_ARGS)
  - [ ] Step 5 — DT_E carrier validation (instrumented build + assertions)
  - [ ] Step 6 — SNOBOL4 isolation gate strengthening
  - [ ] Step 7 — M1 milestone close

Step 3 is now a small lowerer edit at sm_lower.c:470:

    /* before */
    emit_push_expr(p, arg);
    /* after */
    {
        int skip = sm_emit_i(p, SM_JUMP, 0);
        int entry = sm_label(p);
        lower_expr(p, lt, arg);
        sm_emit(p, SM_RETURN);
        int after = sm_label(p);
        sm_patch_jump(p, skip, after);
        sm_emit_ii(p, SM_PUSH_CHUNK, (int64_t)entry, 0);
    }

The consumer (`bb_usercall` thawing each DT_E via `EVAL_fn` → `EXPVAL_fn`)
already routes chunks via `sm_call_chunk`.  Verify no regression in
Snocone pattern smoke (`*upr(tx)` user-pattern call arg deferral) and
in the `beauty.sno` 2-way harness if you want maximal coverage.

Step 4 is the same pattern at three sites (326/345/386) — all use the
SM_PAT_CAPTURE_FN_ARGS consumer which similarly thaws each DT_E via
EVAL_fn.

---

## Architectural decisions worth carrying forward

1. **Code is code.**  A chunk is just instructions in `prog->instrs[]`.
   No special "lazy IR" storage, no carrier-fiction, no parallel
   evaluator.  When you need to evaluate a chunk, you point `pc` at it
   and run the dispatcher.

2. **Same stack vs nested stack:** Lon's correction.  For inline cases
   (`EVAL(*expr)` lowered all in one place), use `SM_CALL_CHUNK` and the
   live SM stack — one push and pop is as good as another.  For C-call
   dispatch (`EXPVAL_fn` from `EVAL_fn` thaw), heap-allocated nested
   `SM_State` is fine *because*: the value stack is a heap buffer,
   not a "stack" in any meaningful sense; running the dispatcher on a
   different DESCR_t array is the same operation.  Don't conflate
   "nested SM_State" with "wrong" — the original crash was a label
   layout collision, not a state-isolation problem.

3. **DT_E discriminator: `slen` field.**  `slen == 0` ⇒ legacy
   `EXPR_t* ptr`.  `slen == 1` ⇒ chunk descriptor with `i = entry_pc`.
   This lets old and new paths coexist during migration.  Once Steps
   3–5 land and no producer emits `SM_PUSH_EXPR` anymore, the legacy
   branches in `EXPVAL_fn` and `pat_to_patnd` can be deleted.

4. **`SM_LABEL` operand layout is now uniform.**  Both `sm_label()` and
   `sm_label_named()` store PC in `a[1].i` and use `a[0].s` for name (or
   NULL).  This cleanup is general, not CHUNKS-specific.

---

## Open question for next session

The optimization Lon raised in the first message: when `*P` and P is
already a bound pattern variable (DT_P holding a compiled BB), the
chunk descriptor could just reference the existing BB's entry point
with no fresh body emitted.  This requires:

- Tracking which DT_P values have stable entry_pcs (do they?).
- Detecting at lower time when E_DEFER's child is provably an existing
  pattern (E_VAR resolving to a DT_P).

A clean optimization but not a correctness requirement.  Worth a
sketch session before diving in — the BB system's relationship to
SM `entry_pc`s isn't immediately obvious from the code alone.

---

## What's NOT done

- Step 3 producer migration (the actual `sm_lower.c:470` edit).
  Consumer infra ready; should be ~10 lines of code + a smoke run.
- Steps 4–7 (rest of M1).
- M2–M6 entirely.

---

## Repos / commits at session end

- one4all `55eb4e03` (main, pushed)
- .github  `d0a5bae`  (main, pushed)
- corpus   unchanged this session

All gates green at session end:
- smoke ×6: snobol4 7/7, snocone 5/5, icon 5/5, prolog 5/5, raku 5/5, rebus 4/4
- isolation gate (test_isolation_ir_sm.sh): PASS
- `scrip_all_modes`: PASS=2, SKIP=3
- Build: green at -O0 with all warnings.

End of handoff.
