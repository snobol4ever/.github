# HANDOFF 2026-05-27 — Opus — PROLOG-BB: GATE-4 first green (0/4 → 1/4)

**Goal:** GOAL-PROLOG-BB.md — V-1 + V-2 (first green four-port mode-4 Prolog).
**Result:** ✅ **GATE-4 0/4 → 1/4.** `main :- X is 1+2, write(X), nl.` compiles to standalone
x86 and prints `3`. This is the first time mode-4 Prolog has ever executed end-to-end.

## Gate ledger (clean rebuild, this session)
- GATE-1 smoke: 5/5 ✅
- GATE-2 crosscheck: 132/0 (ORACLE_MISS 5) ✅
- GATE-3 rung interp: 88/107 ✅ (UNCHANGED — V-1/V-2 transparent to mode-2)
- GATE-4 mode-4: **1/4** ✅ (m4-seq PASS; m4-call/choice/alt still FAIL — V-3)
- Cross-lang: icon/snocone/raku 5/5, rebus 4/4, snobol4 --interp 7/13, mode-4 SNOBOL4 `hi` ✅

## ⛔ NOT COMMITTED. 8 files dirty in one4all working tree:
`src/lower/lower_pl.c`, `src/lower/bb_exec.c`, `src/lower/bb_exec.h`,
`src/emitter/emit_bb.c`, `src/emitter/BB_templates/bb_builtin.cpp`,
`src/emitter/SM_templates/sm_bb_switch.cpp`, `src/emitter/XA_templates/xa_file_header.cpp`,
`src/runtime/rt/rt.c`. (+103 lines.) Build clean: `bash scripts/build_scrip.sh && make libscrip_rt`.

## What landed (all template-pure: every emitted byte from a template; C only for conversion/effect helpers)

### V-1 — clause body wrapped in BB_PL_SEQ (lower_pl.c)
- `lower_pl_clause_body`: after the back-to-front threading, allocate a `BB_PL_SEQ`, populate
  `bb_pl_seq_state_t->goals[] = gnodes[]`, set `seq->α = nα[0]`, `cfg->entry = seq`.
- Explicit-conjunction case (lower_pl.c ~199) was ALSO missing `goals[]` population — added it
  (BB_node_alloc does NOT allocate aux state; GC_MALLOC the `bb_pl_seq_state_t` and fill it).
- Transparent to mode-2: the interp `BB_PL_SEQ` case just returns `nd->α`, so entering the seq ==
  entering nα[0]. GATE-3 unchanged. `flat_drive_pl_seq` now recovers the chain via `pl_seq_goals_em`.

### V-2 — is/2 four-port emission (bb_builtin.cpp + bb_exec.c + emit_bb.c + bb_exec.h)
- **KEY LESSON:** do NOT pass emit-time `BB_t*` pointers into the standalone binary — they are
  scrip-process addresses, invalid at runtime (→ segfault). Pass SERIALIZABLE SCALARS only, exactly
  like the working `rt_pl_write_var(int slot)`.
- `bb_builtin.cpp` `is` arm: flattens RHS `BB_ARITH` operands at emit time into (op_lbl, lk, li, rk, ri),
  calls `rt_pl_is(dst_slot, op, lk, li, rk, ri)`, branches eax → γ/ω. Template owns all bytes incl. jmps.
- `rt_pl_is` (bb_exec.c, exported via bb_exec.h): evaluates via existing `rt_pl_arith` + unifies into
  `g_pl_env[dst_slot]`. Effect helper only. (NOTE: currently handles binary-arith RHS only; non-binary
  exprs e.g. `X is 5` or `X is Y+Z+W` will need extension.)
- `bb_prepare_pl` BB_BUILTIN branch: interns the `is` RHS op string into `bb_pl_op_lbl`.

### Two infra fixes any mode-4 Prolog needed
- **g_pl_env allocation (sm_bb_switch.cpp):** PL_ENTRY arm now emits `mov edi,64; call pl_bb_env_push@PLT`
  before `walk_bb_flat`. Top-level query has no caller env; without this any BB_PL_VAR access derefs NULL.
- **GC init (rt.c + xa_file_header.cpp):** mode-4 prologue calls `rt_register_predicates_pl`
  (→ rt_pl_b_node → GC_MALLOC) BEFORE `rt_init`. Lazy Boehm-GC auto-init deep in that chain faults in
  `pthread_getattr_np` under `-no-pie`. Fix: new `rt_gc_init()` = `GC_INIT()`, emitted as the FIRST
  instruction of every `main` (xa_file_header.cpp). Verified safe across all targets (SNOBOL4 m4 still `hi`).

## NEXT SESSION — two tracks, do in this order

### (1) write(atom) mode-4 bug — NEW, found this session, NOT fixed
`write(hello)` in mode-4 emits `xor edi, edi` (NULL atom) → prints nothing. m4-seq passes only because
its `write(X)` arg is a VAR not an atom. Diagnosis (probed, confirmed): `bb_prepare_pl` BB_BUILTIN branch
DOES intern (`nd->α->t==BB_ATOM` match=1, sval="hello", intern returns non-NULL), but `bb_pl_ls` reaches
`bb_builtin.cpp`'s write arm as NULL at TEXT-pass entry. The `BB_ATOM` branch of the same channel works
(`bb_pl_atom.cpp` lea's fine). So loss is specific to the BB_BUILTIN path — suspect a multi-pass emit
clobber between `bb_prepare_pl` and the TEXT template body. **Fix direction:** have the write arm read
`pBB->α->sval` directly and emit the string as an immediate address (mirror `bb_pl_atom.cpp` binary arm's
`u64le((uintptr_t)atom)`), bypassing the lossy `bb_pl_ls` channel. Small, self-contained.

### (2) V-3 / AGW-9B — fill empty structural templates (the other 3 GATE-4 rows)
m4-call/choice/alt FAIL with `bb_emit_byte: non-BINARY-mode reach (mode=0, b=0xe9)` — the empty
`bb_pl_call/choice/alt.cpp` stubs. Order: call → choice → alt (per GOAL-PROLOG-BB AGW-9B).
- `bb_pl_call.cpp`: predicate→predicate linkage; emit `jmp <callee entry label>`; needs stable
  per-predicate `.Lpl_<name>_<arity>_α` entry label reachable by both PL_ENTRY and BB_PL_CALL.
- `bb_pl_choice.cpp`: multi-clause; inline trail_mark/trail_unwind (effect helpers OK); clause[i].ω→[i+1].α.
- `bb_pl_alt.cpp`: `;` disjunction, same trail discipline.
Gate each: `util_prolog_template_emptiness_audit.sh` EMPTY drops by 1; the matching m4-* row PASSes.

### PL-DEBT-1 ledger update
`rung-seq mode-4 ✅ 2026-05-27 (m4-seq, X is 1+2)`. is/2 mode-2 ✅ already; mode-4 ✅ now (binary-arith RHS).
write/1 mode-4: var-arg ✅, atom-arg ⏳ (track 1 above). nl/0 mode-4 ✅.
