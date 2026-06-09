# HANDOFF — PLG-8-native: Prolog mode-3 (`--run`) hello-world emits in the boxes, no ring

**Author:** Claude Opus 4.8 · **Date:** 2026-05-31 · **SCRIP HEAD (pre-commit):** `5c97162`
**Goal:** GOAL-PROLOG-BB.md
**Directive (Lon):** "Ensure your mode 3 is emitting code and data in the BB's and that all
return values go up the BB graph chain. Notice how there is no RINGS needed in the test\*.c
code. Use your RINGS for mode 2 interp. Wrong for mode 3."

## The correction this implements

PLG-8 (`0c29950`) un-EXCISED Prolog mode-3 by routing `--run` through `bb_exec_once` — the
**mode-2 interpreter**, which threads values between nodes via the **AG ring**
(`IR_graph_t.ring[AG_RING]` + `ag_ring_push`, pushed in `bb_exec_once`'s loop at
`bb_exec.c:4506`). Output was correct and byte-identical to mode-2, but it is the **ring path**.
Per the uploaded canonical target shapes (`test_sno_1.c`, `test_icon.c`): in mode-3 every value
lives in a **per-box slot** (`POS0`, `BIRD`, `mult_V`, `x5_V`) and the consumer reads its
producer's slot directly — there is **no ring and no value stack**. Rings are the mode-2-interp
idiom; mode-3 must EMIT code+data inside the boxes with success/failure flowing up the BB graph
chain through the `γ`/`ω` ports.

## What landed (`src/driver/scrip.c`, Prolog-only, additive, +53/−0)

A native mode-3 path for the **proven hello-world tier**, mirroring exactly how Icon and
SNOBOL4 mode-3 already work (`bb_build_flat` + the `g_frame_active` ζ-frame, `(void)fn(rt_frame(),0)`):

1. **`pl_flat_body_root(g)`** — the Prolog sibling of `sno_ring_to_tree`. Returns the flat-walk
   ROOT (the principal `IR_GCONJ` in the main graph) iff the body is a conjunction of
   constant-arg builtins (`write`/`writeln`/`print`/`nl`/`halt`) and/or `IR_SUCCEED`/`IR_CUT`/
   `IR_ATOM`, with **`nslots==0`** (no logic-variable slots) and no user-proc call / choice /
   disjunction / ITE / unify / arith goal. Returns `NULL` for every richer shape. The GCONJ is
   found by scanning `g->all[]`; its goal entries are read from the `bb_conj_state_t` sidecar
   (`node->ival`). A bare 0-arg fact (`g->entry` is `IR_SUCCEED`, no GCONJ) is also accepted.

2. **Prolog `mode_run` arm** — if `pl_flat_body_root` returns a root: `g_frame_active=1;
   bb_build_flat(root); pfn(rt_frame(),0); goto run_done`. The flat walk
   (`walk_bb_flat → flat_drive_pl_seq → bb_builtin`) emits the write boxes; **`bb_builtin` reads
   each argument from the goal's own `α` at emit time** — `write` of an `IR_ATOM` becomes
   `mov rdi, imm64(atom); call rt_pl_write_atom`, a sealed read-only constant read directly by
   its consumer, **no `rt_pl_atom_push` ring push**. `nl` → `mov edi,10; call putchar`. If
   `bb_build_flat` returns NULL (template gap) or the shape isn't recognized, the arm keeps the
   **interim `bb_exec_once` route** → zero regression. Widen-as-you-go gate, identical in spirit
   to `sno_ring_to_tree`.

`mode_interp` (mode-2) is **untouched** — it keeps `bb_exec_once` + the ring, exactly as the
directive requires ("use your RINGS for mode 2 interp").

## Verified

With temporary `[TRACE-NATIVE-FLAT]` / `[TRACE-INTERIM-RING]` markers (since removed, tree clean):

- `hello.pl` mode-3 → **`[TRACE-NATIVE-FLAT]`** → prints `Hello, World!` ✅ (native, no ring).
  The `write_atom` smoke (`main :- write(hello), nl.`) is the same shape → native.
- `queens.pl` / `palindrome.pl` mode-3 → `[TRACE-INTERIM-RING]` (correct fallback; need slots/choice).

## Gates (all green, no regression)

| Gate | Before | After |
|---|---|---|
| GATE-1 smoke m2 | 5/5 | 5/5 |
| GATE-1 smoke m3 | 5/5 (ring) | **5/5** (hello-tier native, rest interim) |
| GATE-1 smoke m4 | 5/5 EXCISED | 5/5 EXCISED |
| GATE-3 rung m2 | 109/111 | 109/111 |
| GATE-3 rung m3 | 109/111 | 109/111 |
| prove_lower2 | 51/51 | 51/51 |
| FACT | 0 | 0 |

The 2 GATE-3 fails are unchanged and unrelated to this work: `rung15_abolish_abolish_then_reassert`
(re-assert after abolish — stale CHOICE graph) and `rung30_dcg_pushback_rest` (`{ Goal }` DCG
extra-goal not lowered). Both are mode-agnostic `lower.c` recognition gaps.

## NEXT (widen native mode-3 rung by rung)

1. **`unify` / `arith` smoke tier** — `X = world, write(X)` and `X is 2+3, write(X)` have
   `nslots>0` (one logicvar slot). The slot must live in the **ζ-frame** (`[r12+off]`), not the
   ring. Extend `pl_flat_body_root` to accept `IR_UNIFY` (var=const) and `IR_ARITH`/`is` goals,
   confirm `bb_unify`/`bb_arith`/`bb_builtin`'s `is` arm write/read the slot via the per-sequence
   frame (not `g_resolve_env`), and that `rt_pl_write_var(slot)` reads from the same frame. This is
   the next native rung and the first one that exercises per-box RW slots.
2. **`clause` tier (multi-clause facts + `fail`/`;`)** — needs `flat_drive_pl_choice` proven
   through `bb_build_flat` (the `IR_CHOICE` bodies are separate sub-graphs; register them and
   verify backtracking enumerates via the ζ-frame, not the ring).
3. **`recursion` tier** — needs `flat_drive_call_userproc` + `rt_proc_register` of the user
   predicates (mirror the Icon proc-registration loop already in the Icon mode-3 arm).
4. Each rung: verify the program goes `[TRACE-NATIVE-FLAT]` (re-add the marker locally) AND the
   full GATE-1/GATE-3 m3 counts hold. Mode-2 must stay byte-identical throughout.

## Files

- `src/driver/scrip.c` — `pl_flat_goal_is_simple` + `pl_flat_body_root` recognizer; native
  `bb_build_flat` branch in the Prolog `mode_run` arm with interim `bb_exec_once` fallback.
- `.github/GOAL-PROLOG-BB.md` — PLG-8-native live-state entry + gate table refresh.
