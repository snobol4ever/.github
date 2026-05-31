# SESSION HANDOFF — 2026-05-27 (Opus 4.7) — RK-BB-SEGFAULT-CLUSTER bugs 2+3 ✅

**SCRIP HEAD:** `2a70abed` ✅ all gates HOLD or improve
**.github HEAD:** this commit (PLAN.md + GOAL-RAKU-BB.md pruned, watermark updated)

Prior session: `HANDOFF-2026-05-27-OPUS-RK-BB-SEGFAULT-CLUSTER-BUG-1.md`.

---

## What landed this session

ONE commit on SCRIP (`2a70abed`), ONE file changed (`src/lower/lower.c`, +56/-8).

Three structural edits restoring multi-sub Raku programs to a working SM shape.
Bug 1 (segfault elimination) had cleared the runtime crash; bugs 2 and 3 — the
architectural issues underneath — were documented but unfixed. This session
landed both.

### Edit 1 — `lower_stmt` ~L1987 (bug 2a: top-level inline gate)

Prior code inlined EVERY non-gather Raku sub's body at top level. For multi-sub
programs this ran `double`, `greet`, `add`, `classify` bodies sequentially at
startup against an empty stack; the first `return` halted before reaching
`main`'s body. Single-sub programs (`sub main()` only) worked by accident.

Fix: gate the inline emission on `_is_main` so only `sub main()` inlines at
top level (top-level IS main in Raku convention). Other subs emit no body at
top level; they're reached via `SM_CALL_FN` to the named LABEL skeleton.
`__gather_*` still skips per RK-BB-2 (body lives in the BB graph).

### Edit 2 — `lower_proc_skeletons` ~L2370 (bug 2b: skeleton body extraction)

Prior code extracted body via `bnd = (proc->t == TT_PROC_DECL && proc->n >= 3) ? proc->c[2] : NULL`.
For TT_SUB_DECL (Raku) this is NULL → skeleton emitted as just LABEL + RETURN
with no body. Also `g_lang = LANG_ICN` unconditionally during body lowering —
Raku expressions would lower with Icon semantics.

Fix: branch on `proc->t == TT_SUB_DECL`:
- Body at `proc->c[nparams+1..]` as flat children (no enclosing TT_VLIST).
- `g_lang = LANG_RAKU` during lowering.
- Skip emitting body for `main` (already inlined at top level via Edit 1) and
  for `__gather_*` (BB graph routes via SM_BB_SWITCH).
- For TT_PROC_DECL, behavior bit-identical to before.

### Edit 3 — `build_proc_scope` ~L2288 (bug 3: param→slot binding)

Prior code read `plist = (proc->t == TT_PROC_DECL && proc->n >= 2) ? proc->c[1] : NULL`
where `plist` is a TT_VLIST of TT_VARs. Raku TT_SUB_DECL has no TT_VLIST —
params are flat TT_VAR children at `proc->c[1..proc->v.ival]`. plist NULL →
scope empty → body's `$param` reads miss the frame slot and read from global
where the param is unset.

Fix: TT_SUB_DECL branch at top of `build_proc_scope`:
- Walk `proc->c[1..proc->v.ival]` adding each TT_VAR sval to scope.
- Walk `proc->c[nparams+1..]` via `expression_scope_walk` for body-local slots.
- `scope_add` is idempotent by name (slot reuse for duplicates).

## Gates

```
GATE-RK mode-2:  14/33 → 16/33  (+rk_interp, +rk_map_grep_sort24)
GATE-RK4 mode-4: 15/33 HOLD
Smoke raku:      5/0    HOLD
Smoke icon:      5/5    HOLD
Smoke prolog:    5/5    HOLD
Smoke snobol4:   13/0   HOLD
Broker Icon:     198    HOLD
GATE-PK: ⛔ harness segfault — INHERITED. Owed: SBL-ANY session.
FACT RULE grep:  0
Build:           clean
```

## SM dump evidence (rk_subs after edits)

```
   1  SM_LABEL             s="double"
   2  SM_LOAD_FRAME        ← param $n bound (bug 3 fix)
   3  SM_COERCE_NUM
   4  SM_PUSH_LIT_I        i=2
   5  SM_COERCE_NUM
   6  SM_MUL
   7  SM_VOID_POP          ← BUG 4 (next session): discards result
   8  SM_RETURN

  70  SM_LABEL             s="main"
  71  SM_RETURN            ← correctly empty (bug 2b: main skipped)

  73+ STNO labels…
  78  SM_PUSH_LIT_I        i=7
  79  SM_CALL_FN           s="double" nargs=1   ← top-level main inlined (bug 2a)
  80  SM_CALL_FN           s="write" nargs=1
  ...
```

Multi-sub structure now correct. SM_CALL_FN dispatches by name to the LABEL
skeleton. Params bind via LOAD_FRAME. Main runs at top level.

## ⛔ NEXT — RK-BB-SEGFAULT-CLUSTER bug 4 (lower_return)

**ONE FILE TO TOUCH:** `src/lower/lower.c`, function `lower_return` ~L1240.

`rk_subs` still fails mode-2 with output `hello raku\n` (only). Diagnostic:

`return $n * 2` in `double($n)` produces SM:
```
  LOAD_FRAME ; COERCE ; PUSH_LIT_I 2 ; COERCE ; MUL ; VOID_POP ; RETURN
                                                       ↑↑↑↑↑↑↑↑
                                                       discards result
```

`lower_return` (lower.c:1240) for the bare branch (no `g_sc_func_name`)
emits `lower_expr; SM_VOID_POP; SM_RETURN`. The VOID_POP kills the result.

SM_RETURN handler at `sm_interp.c:1432`:
```c
DESCR_t retval = (fr->retval_name)
    ? NV_GET_fn(fr->retval_name)
    : ((st->sp > 0) ? st->stack[st->sp - 1]
       : (g_lang == LANG_ICN ? NULVCL : FAILDESCR));
```

When `fr->retval_name` is NULL (the common case), retval comes from
**stack-top** (`st->stack[st->sp - 1]`). So the convention is: leave the value
on stack, RETURN grabs it. The VOID_POP in `lower_return` violates that.

For Snocone with `g_sc_func_name` set, the path stores by name (works).
For Icon, procedures use BB_RETURN via the BB graph — this code path is never
reached. For Raku, this code path is the active one and it's broken.

**FIX SHAPE:**

```c
static void lower_return(const tree_t *t)
{
    if (t->n > 0 && t->c[0] && g_sc_func_name) {
        lower_expr(t->c[0]);
        SM_emit_s(g_p, SM_STORE_VAR, g_sc_func_name);
        SM_emit(g_p, SM_VOID_POP);
    } else if (t->n > 0 && t->c[0] && g_lang == LANG_RAKU) {
        /* Raku: leave result on stack-top; SM_RETURN reads stack[sp-1]. */
        lower_expr(t->c[0]);
    } else if (t->n > 0 && t->c[0]) {
        lower_expr(t->c[0]); SM_emit(g_p, SM_VOID_POP);
    }
    SM_emit(g_p, SM_RETURN);
}
```

**EXPECTED UPLIFT (mode-2):** rk_subs flips (16 → 17). rk_try_catch25 may
flip too if its `Error 5 Undefined function` is downstream of return-value
loss; otherwise it's a separate try/CATCH issue requiring its own diagnostic.

## ⛔ MODE-4 BLOCKER (separate, surfaces after bug 4)

After bug 4 lands, mode-4 `rk_subs` will hit:

```
as: Error: no such instruction: `unhandled SM_LOAD_FRAME'
```

at multiple sites. The frame-slot read isn't emitted in mode-4 for Raku.
Either `sm_load_frame.cpp` doesn't exist, or `walk_sm_instr`'s LOAD_FRAME
branch in `emit_sm.c` routes to a stub for non-Icon. Same shape will exist
for SM_STORE_FRAME.

**Triage path:**
1. `grep -n "SM_LOAD_FRAME\|SM_STORE_FRAME" src/emitter/` to find templates.
2. `grep -n "LOAD_FRAME\|STORE_FRAME" src/processor/emit_sm.c` for dispatch.
3. The Icon path likely emits via SM_templates/sm_load_frame.cpp; check
   whether it has a Raku-arm or whether it gates on language.
4. The slot index is in the SM instruction's `a[0].i` (frame-relative).
5. Pattern: same as SM_LOAD_VAR but indexed via slot not name. Should
   be a small template if SM_LOAD_VAR has one already.

After mode-4 LOAD_FRAME / STORE_FRAME work, mode-4 rk_subs follows mode-2
green for free (assuming the value-flow through SM_CALL_FN's rt.c path is
already symmetric — RK-BB-3.0a's `rt_set_lang` prologue ensured the dispatch
chain runs in mode-4).

## Tests still failing in mode-2

```
rk_subs           → "hello raku" — bug 4 (return value lost)
rk_try_catch25    → "Error 5 Undefined function" — likely try/CATCH-specific
rk_re32, rk_gather, rk_combinator, rk_given18, rk_hash17, rk_hashes,
rk_class26, rk_fileio38, rk_junctions — various (regex, hash, class,
                                                  fileio, junctions not in scope)
```

The 17 remaining mode-2 fails are mix of: future ladder rungs (junctions,
regex), substrate gaps (hashes, classes, fileio), and downstream effects
of bug 4. Bug 4 alone is the cheapest single uplift available.

## Doctrinal status

- ZERO new BB kinds.
- ZERO new runtime helpers.
- ZERO new emit_textf / seg_byte sites.
- 100% template/lowering emission preserved.
- FACT RULE grep: 0 (no seg_byte / SL_B / sl_emit_one / emit_standard_blob).
- PEERS RULE clean (no BB_t fields added).
- Touched ONE file: `src/lower/lower.c` (+56/-8).

⛔ END HANDOFF
