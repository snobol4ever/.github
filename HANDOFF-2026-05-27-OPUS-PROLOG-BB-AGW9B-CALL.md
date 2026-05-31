# HANDOFF 2026-05-27 — Opus — PROLOG-BB: AGW-9B-call (GATE-4 1/4 → 2/4)

**Goal:** GOAL-PROLOG-BB.md — V-3 / AGW-9B-1 (deterministic predicate call) + write(atom) fix.
**Result:** ✅ **GATE-4 1/4 → 2/4.** `greet :- write(hi), nl.` / `main :- greet.` compiles to
standalone x86 and prints `hi`. First mode-4 Prolog predicate-to-predicate call. SCRIP `449f4ca3`.

## Gate ledger (clean rebuild, this session)
- GATE-1 smoke: 5/5 ✅
- GATE-2 crosscheck: 132/0 (ORACLE_MISS 5) ✅
- GATE-3 rung interp: 88/107 ✅ (UNCHANGED — mode-2 transparent)
- GATE-4 mode-4: **2/4** ✅ (m4-seq + m4-call PASS; m4-choice/alt still FAIL — empty templates)
- Emptiness audit: EMPTY 3→2 (`bb_pl_call` FILLED; choice/alt remain)
- SNOBOL4 mode-4 compile sanity ✅

## What landed (template-pure: every emitted byte from a template; emit_bb.c stays byte-free)

### bb_pl_call.cpp — FILLED (the call SITE)
Emits `call .Lplpred_<name>_<arity>`, then `call rt_last_ok` + `test eax,eax` → `jne γ` / `jmp ω`;
β→ω (deterministic: a single-solution callee has nothing to redo). Reads callee name + arity
DIRECTLY off the emit-time BB node (`pBB->sval`, `pBB->ival→arity`) — the `bb_pl_ls` intern channel
is clobbered across multi-pass emit (same loss noted for write(atom)).

### sm_bb_switch.cpp PL_ENTRY — callee-block emission (the call TARGET)
After inlining the entry predicate's flat graph, emits EVERY OTHER predicate as a callable flat block
under stable `.Lplpred_<sanitized-name>_<arity>`: env-push, flat body via `pl_emit_callee_block_body`,
then `γ:`→last_ok=1+`ret` / `ω:`→last_ok=0+`ret`. A skip-jump (`.Lplcallees<id>_end`) hops over the
blocks so control never falls into one. This begins retiring V-4 (rt_pl_b_* runtime graph-rebuild) for
*called* predicates — they now exist as native x86, not a runtime-reconstructed graph.

### emit_bb.c — byte-free helpers + walk_bb_flat case
- `walk_bb_flat`: added `case BB_PL_CALL: FILL(...)` (it was falling to `default:` → `emit_jmp_label`
  in text mode → `bb_emit_byte` 0xe9 abort — that was the WHOLE m4-call failure, not "empty template").
- `pl_call_block_label`: builds `.Lplpred_<name>_<arity>`, sanitizes non-`[A-Za-z0-9_]`, strips any
  `/arity` suffix (table stores `"greet/0"`, call node stores `"greet"` — both must derive one label).
- `pl_emit_callee_block_body`: byte-free; drives `walk_bb_flat` on one predicate's entry node.

### pl_runtime.c/h — byte-free predicate enumeration
`pl_bb_pred_count` / `pl_bb_pred_name_at` / `pl_bb_pred_arity_at` (graph-less slots return NULL/0).

### write(atom) mode-4 bug — FIXED (handoff track 1)
Root cause: the flat intern-str hook (`g_flat_intern_str`) was wired ONLY inside the pattern-window
path (gated on `n_invariant`), so a Prolog-only compile left it NULL → `emit_intern_str` returned NULL
→ `bb_prepare_pl` set `bb_pl_ls=NULL` → write arm emitted `xor edi,edi` (NULL atom). ALSO: even with the
hook set, `emit_intern_str` only resolves under `g_is_text`, and the PL_ENTRY flat walk runs
`bb_prepare_pl` during a NON-text pass (probed: `g_is_text=0`). Fix (two parts):
1. `emit_sm.c`: wire `lower_flat_set_intern_str(codegen_intern_str)` unconditionally after
   `strtab_collect`/`pl_pre_intern_pred_names` (the strtab already holds every atom).
2. `emit_bb.c bb_pl_intern_into`: when `emit_intern_str` returns NULL, fall back to mode-independent
   `strtab_label` (the atom WAS collected; the label `.S<idx>` is a pure function of the string).
`write(hi)` now emits `lea rcx,[rip+.S3]` with `.S3: .string "hi"` in rodata.

## NEXT SESSION — AGW-9B-2/3 (the other two GATE-4 rows)

m4-choice/alt FAIL with `bb_emit_byte: non-BINARY-mode reach (0xe9)` — `BB_CHOICE`/`BB_PL_ALT` have
NO `walk_bb_flat` case yet, so they fall to `default:` (same shape the call bug had). Order per goal file:

### (1) bb_pl_choice.cpp — multi-clause predicate (`p(a). p(b).`)
STATEFUL — the hard one. Needs inline `trail_mark`/`trail_unwind` (permitted effect helpers) emitted as
x86. clause[i].ω→clause[i+1].α; last ω→ω_in. Mirror `bb_exec.c` BB_CHOICE. Add `case BB_CHOICE` to
walk_bb_flat (likely a `flat_drive_pl_choice` driver mirroring `flat_drive_alt`, since it has N child
clause bodies to recurse + wire). The callee-block infra from this session already emits each predicate
as a block, so a multi-clause predicate's BB_CHOICE will be walked inside its block.

### (2) bb_pl_alt.cpp — `;` disjunction (`( true ; true )`)
Same trail discipline, two branches. Add `case BB_PL_ALT`. Mirror `flat_drive_alt`.

Gate each: emptiness EMPTY drops by 1; matching m4-* row PASSes; GATE-1/2/3 unchanged.

## PL-DEBT-1 ledger update
`rung-call mode-4 ✅ 2026-05-27 (m4-call, greet/0 det call)`. write/1 mode-4: var-arg ✅ AND atom-arg ✅
now (track 1 closed). Deterministic 0-arity call ✅. Multi-clause (choice) + disjunction (alt) ⏳.

## Notes for the choice/alt session
- The callee-block label scheme is stable: any predicate is reachable via `call .Lplpred_<name>_<arity>`.
  When choice/alt land, a predicate whose body contains a call to a multi-clause predicate will Just Work
  because that callee is already emitted as its own block.
- V-4 (rt_pl_b_* runtime rebuild) is NOT yet deleted — it still emits alongside the new flat blocks.
  Once choice/alt land and every construct flat-emits, delete `codegen_pl_predicate_registry` /
  `XA_PL_BUILDER` + the `rt_pl_b_*` family (V-4 gate: `grep rt_pl_b_ out.s == 0`).
- β-port for BB_PL_CALL is currently β→ω (deterministic). A call to a multi-solution predicate will need
  β to re-enter the callee for the next solution — defer until choice lands and a backtracking call is testable.
