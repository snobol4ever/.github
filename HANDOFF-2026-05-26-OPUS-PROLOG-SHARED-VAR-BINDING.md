# HANDOFF 2026-05-26 (Opus 4.7) — PJ-AGW shared-var unify binding LANDED + succ/2; main/0 auto-run gap found

**SCRIP HEAD: <this session's commit> (clean, all gates green).**
smoke_prolog 5/5 · prolog_bb_honest 128/0/0 (was 123) · smoke_icon 5/5 · smoke_snobol4 13/13 ·
GATE-3 prolog_rung_suite 20/107 (was 19) · ASAN CLEAN.

## What landed (one commit; two coordinated source changes)

### The meaty fix — BB_PL_CALL shared-var unify binding (`src/lower/bb_exec.c`)
This is the open NEXT from HANDOFF-2026-05-26-OPUS-PROLOG-DCG-PHRASE.md, done properly.
WAM model: **control state lives in bb_snapshot, ALL binding state lives in the trail.**

1. **Fresh call:** for each arg, `term_new_var(ai)` as the callee param, build the caller-arg
   TERM via `pl_node_to_term(zc->args[ai])` WHILE g_pl_env still points at the CALLER env
   (so a caller BB_PL_VAR derefs/materialises to the caller's actual cell), then
   `unify(callee_param, caller_term, &g_pl_trail)`. The unify TERM_REF aliasing makes bindings
   the callee makes propagate back to the caller automatically — INCLUDING vars nested inside
   compound args (the append/3 `[H|R]` output tail). Trail mark taken BEFORE the bind loop.
   **Both slot-copy writeback loops (fresh + resume) DELETED** — they bypassed the trail.
2. **`is` builtin:** `unify(pl_node_to_term(nd->α), result, &g_pl_trail)` instead of the raw
   `g_pl_env[slot] = vt` overwrite. The raw overwrite severed the shared-var ref link a
   unify-bound caller relies on (recursively-computed N in len/2) and bypassed the trail.
3. **Resume path:** do NOT pre-unwind the trail. The callee graph's own live choice points
   (BB_CHOICE / nested BB_PL_CALL) rewind their own bindings via their own trail marks inside
   `bb_exec_resume`. Pre-unwinding ripped them out from under the inner choice → that was the
   prior attempt's rung05 blank over-generation. Unwind to `cs->trail_mark` ONLY on call
   exhaustion (undoes arg aliasing + residue).

**Why this avoids the prior attempt's regressions:** the earlier try coupled shared-var
binding with a per-node snapshot of binding state AND pre-unwound on resume, so resumed
backtracks saw stale/over-bound vars (rung05 blanks) and aborted deep graphs deref'd bad
state (rung10 segfault). Putting ALL binding in the trail and letting inner choice points own
their own rewind removes the coupling. Verified: append([a],[b],L)=[a,b]; rung06 =
[a,b,c,d]/4/[d,c,b,a]; member(X,[a,b,c]) = a,b,c and TERMINATES; rung10 puzzle_14 no longer
segfaults (all 20 rung10 puzzles exit 0). ASAN (detect_use_after_free=1) clean on append/len/
member/rung05/rung06 + an 8-deep recursion.

### Bonus — succ/2 builtin (`src/lower/lower_pl.c` + `bb_exec.c`)
Recognized succ/2 as BB_BUILTIN in lower_pl_goal (alongside is/comparisons). Exec arm:
bidirectional, `succ(X,Y)` binds whichever of X/Y is unbound via unify (shared-var safe),
ISO non-negative-integer checks. CORRECT in isolation: succ(0,A)→1, succ(2,3)→ok,
multi-goal conjunctions print 1/5/100. **But rung18 still FAILS** — see next section.

## ⛔ KEY FINDING for next session — main/0 auto-run gap (blocks ~rung12–28)

rung18_succ_*.pl (and a whole block of rungs) have **NO `:- initialization(main).` directive**
— they just define `main :- ...` + a trailing `main.` fact, and their `.expected` files show
real output. But scrip does NOT auto-run main/0 for a directive-less file (verified:
`main :- write(hello), nl.` with no directive → empty output). The rung harness
(`scripts/test_prolog_rung_suite.sh`) just calls `scrip --interp file.pl` with no goal
injection. So these rungs can never pass until scrip auto-runs main/0.

**RULES.md forbids patching corpus to work around runtime bugs**, so the sanctioned fix is in
the DRIVER: when a Prolog program loads with no `:- initialization(_)` directive, default to
running `main/0` (standard SWI/GNU behaviour for scripts is actually the opposite — they need
initialization or an explicit goal — so this is a Lon decision: either (a) driver auto-runs
main/0 when present-and-no-directive, or (b) the corpus files are the bug and should carry the
directive, which contradicts RULES.md's no-corpus-patch rule). Start in `src/driver/scrip.c`
and `src/runtime/interp/pl_runtime.c` (the `initialization` directive handling). This single
decision likely lights up a large block of builtin-coverage rungs (rung12–28) as the builtins
themselves land.

## ⛔ NEXT candidates (in rough value order)
- **(A) main/0 auto-run decision** (above) — highest leverage, needs Lon.
- **(B) findall/3 in the live BB path** — rung11_findall_* (5) + rung30_dcg_generate. The
  AST-path impl at `pl_runtime.c:1647` uses `pl_box_goal_from_ir` = the DELETED mode-1 AST
  path (NOT usable; RULES.md NO AST WALKING). Reusable piece: `pl_copy_term` (pl_runtime.c:597,
  operates on Term*, AST-free). Plan: recognize findall/3 in lower_pl_goal (like phrase), lower
  the goal arg into a callable BB subgraph, exec arm runs it to exhaustion via bb_exec_once/
  bb_exec_resume, pl_copy_term the template (built by pl_node_to_term) on each success, build
  the list, unify into arg 3. Cross-backtrack solution collection — a real chunk.
- **(C) builtin coverage, now all shared-var-safe via the unify pattern is/succ use:**
  functor/3 + arg/3 + =.. (rung09), @</@>/@=</@>= term-ordering (rung16), sort/msort (rung17),
  atom_* (rung12), char_type (rung21). Each is a BB_BUILTIN arm; unify the output(s).

## Files touched
- `src/lower/bb_exec.c` — BB_PL_CALL shared-var binding, `is` unify, resume no-pre-unwind, succ arm.
- `src/lower/lower_pl.c` — succ/2 recognized as BB_BUILTIN.

## Gate commands (source of truth)
```bash
cd /home/claude/SCRIP && bash scripts/build_scrip.sh
bash scripts/test_smoke_prolog.sh        # 5/5
bash scripts/test_prolog_bb_honest.sh    # 128/0/0
bash scripts/test_prolog_rung_suite.sh   # 20/107
bash scripts/test_smoke_icon.sh          # 5/5  (permanent non-regression gate)
bash scripts/test_smoke_snobol4.sh       # 13/13 (permanent non-regression gate)
```
