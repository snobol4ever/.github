# FINDING-2026-08-08-CLAUDE-SN4-RTX-140-141-EXPR-THUNK-WANTNM-AND-DCAP-INNER-CALL-CRASH.md

## Programs

`140_pat_eval_double_fn_trick` · `141_pat_eval_double_fn_arbno`
Gate programs for the deferred-NRETURN capture rung. Both remain red at session close; the session landed **Defect 1** and fully characterized **Defect 2**.

---

## Defect 1 — LANDED (`d5da671a`) — NRETURN DT_N dereferenced before reaching EXPR$N global

### Symptom

`*inner(c1)` as a conditional-assignment capture target (`.`) inside an EVAL-compiled pattern — `EVAL('LEN(1) . *inner(' cs ')')` — produced the wrong variable assignment at match time. `inner` uses NRETURN to return `.stk` (the name of `stk`), so the capture should write the matched character to `stk`. Instead the runtime wrote to a variable named by `stk`'s current value (a string), which was the wrong location.

### Root cause — three-level trace

**Level 1 — capture target lowering.** `TT_CAPT_COND_ASGN` / `TT_CAPT_IMMED_ASGN` in `lower_snobol4.c` handle `*func(args)` capture targets by calling `sno_expr_collect(di)` which mints an `EXPR$N` thunk proc. The varname stored in the capture record is `"*EXPR$N"`. At match time `rt_dcap_pump` calls `rt_proc_call_open("EXPR$N", 0)` with `rt_g_want_name=1`.

**Level 2 — thunk call chain and wn propagation.** `rt_proc_call_open` captures `wn = rt_g_want_name = 1` into `c->wn`. The EXPR$N thunk runs and internally calls `inner(c1)`. **The problem**: the thunk's IR was emitted by `sno_expr_thunks_build` without any `SNO$WANTNM` prefix. The IR for `inner(c1)` inside the thunk therefore runs its open with `rt_g_want_name = 0` at that moment (it was consumed by the EXPR$N open). So `inner`'s call captures `c->wn = 0`.

**Level 3 — rt_nret_fix with wn=0.** `inner` does NRETURN: sets `rt_g_ret_by_name = 1` and returns `DT_N(.stk)` as `frame0`. `rt_proc_epilogue_body` for `inner`: `rt_nret_fix(DT_N(.stk), wn=0)`. With `wn=0` and `rt_g_ret_by_name=1`, `rt_nret_fix` **dereferences** the name — returning the current VALUE of `stk` (a `DT_S` string) and clearing the flag. The EXPR$N global receives `DT_S` instead of `DT_N`. The thunk's epilogue (wn=1) returns that `DT_S` to `rt_dcap_step`. `rt_dcap_step` does `NV_SET_fn(nm.s, pending)` — assigns the captured character to a variable named by the string content of `stk`, not to `stk` itself.

### Fix — `src/lower/lower_snobol4.c`

Three changes:

1. Added `int want_name` field to the anonymous `g_sno_exprs[]` struct (zero-initialized by default in `sno_expr_collect`).

2. Added `sno_expr_collect_wn(expr)`: calls `sno_expr_collect`, finds the new entry, sets `want_name=1`. Called from `TT_CAPT_COND_ASGN` and `TT_CAPT_IMMED_ASGN` when `di->t == TT_FNC && di->n > 0` (FNC with args — the case where a bare name `di->v.sval` cannot be used directly). Zero-arg case (`di->n == 0`) unchanged — it uses the bare fn name and the direct `rt_proc_call_open(name, 0)` path, which already carries `wn=1` from `rt_cap_open`.

3. `sno_expr_thunks_build`: when `g_sno_exprs[xi].want_name`, prepend `IR_LIT_STRING("") → IR_CALL("SNO$WANTNM")` before the expression's IR entry, following the identical pattern at `lower_snobol4.c:2112` (the `subj->t == TT_FNC` WANT-NAME arm for assignment statements). This sets `rt_g_want_name=1` before the inner `inner(c1)` open captures it, so `inner`'s epilogue preserves `DT_N`.

### Watermark

N=1, `setarch -R`: m3 **292/25/0** · m4 **274/42/1** · DIVERGE **19**. Exact hold vs session-open baseline. Zero regression.

---

## Defect 2 — PRE-EXISTING, LON ROUTING — DCAP inner call crashes via jmp-0

### Symptom

Even without NRETURN — `inner` doing a plain `:(RETURN)` — the same `EVAL('LEN(1) . *inner(c1)')` probe crashes with `SIGSEGV` at `rip=0, rbp=0`.

### Evidence of pre-existence

`git stash` on Defect 1 changes: crash reproduces identically on HEAD at `fc24965c`. Defect 2 is entirely independent of Defect 1.

### Trace

The EXPR$N thunk blob IS emitted with a valid fn pointer (`pfn=0x7ffff1606000`; `rt_proc_call_open` finds it and returns non-zero fbytes). The DCAP pump returns non-zero; the match box calls `rt_proc_open_fn` which returns `p->fn`; `jmp rax` enters the thunk blob.

Inside the blob, the sequence runs correctly through SNO$WANTNM (or the pre-fix equivalent) and into the `inner(c1)` call:

1. `rt_proc_call_open("inner", 0)` → pushes pcall, returns fbytes
2. `rt_proc_open_fn()` → reads `g_pcall[top-1].p->fn` → returns inner's fn
3. `jmp inner_fn` — inner's jmp-entry blob runs
4. `inner` executes its body; reaches γ epilogue
5. γ epilogue calls `rt_proc_call_epilogue_γ` which pops `g_pcall` (top--)
6. Blob returns via the γ wire to the EXPR$N thunk's γ landing at offset ~0x1b0

At step 6, `g_pcall_top` has been decremented by inner's epilogue. The EXPR$N thunk's pcall record is now at `g_pcall[top]` (one slot below top), but top has been decremented so it points to the EXPR$N record. This appears correct. But the thunk's `IR_ASSIGN` node follows the inner call, and its code path at `~0x19e` calls `movabs $addr, %rax; call *%rax` — identified via blob disassembly as a second `rt_proc_open_fn` call (or equivalent). At that point `g_pcall_top` is back to where EXPR$N's prologue left it, so `rt_proc_open_fn` reads the EXPR$N pcall's `p->fn`. `p->fn` IS valid (the same `0x7ffff1606000`). `jmp rax` then re-enters the EXPR$N thunk blob from the beginning — **infinite recursion / trampoline loop** — until the stack overflows and `rip` ends up at 0.

**Alternative reading (unconfirmed):** If the second call at `0x19e` is NOT `rt_proc_open_fn` but rather `rt_proc_call_open` for a *different* proc (the `IR_ASSIGN` result-commit proc), and that proc's `p->fn` is null, then `jmp 0` is the direct cause. The blob disassembly is ambiguous at this point without symbol resolution.

### What is certain

- The crash is inside the EXPR$N blob itself (not in mapped code outside the slab).
- The crash at `rip=0` is a `jmp 0` from within the blob, triggered after the inner `inner(c1)` call's γ epilogue returns.
- This is an emitter issue: the call-inside-jmp-entry-thunk protocol generates code that uses `rax` (set by an earlier call) as a jump target after a second call has clobbered it, OR `rt_proc_open_fn` is being invoked in a context where no relevant proc is on the pcall stack.
- The fix requires the emitter or the call-inside-dyn-thunk convention. **Lon's routing.**

### Probe that reproduces defect 2

```snobol4
        DEFINE('inner(c)')
        DEFINE('outer(cs)')                                   :(both_end)
inner   inner = c                                             :(RETURN)
outer   outer = EVAL('LEN(1) . *inner(' cs ')')              :(RETURN)
both_end
        s = 'A'
        pat = outer('c1')
        s POS(0) pat RPOS(0)                                  :S(YES)F(NO)
YES     OUTPUT = 'yes'                                        :(END)
NO      OUTPUT = 'no'
END
```

`scrip --run probe.sno` → SIGSEGV. `EVAL('LEN(1) . V')` (plain variable) works. `EVAL('LEN(1)')` works. Only `*func(args)` as capture target triggers the crash.

---

## Status

| Item | State |
|------|-------|
| Defect 1 NRETURN wn fix | ✅ LANDED `d5da671a` |
| Watermark exact hold | ✅ m3 292/25/0 · m4 274/42/1 · DIVERGE 19 |
| Defect 2 DCAP inner call crash | ⛔ PRE-EXISTING — Lon routing |
| 140/141 gate programs | ⛔ STILL RED (blocked on Defect 2) |
| Push | ⛔ BLOCKED — credential owed (SCRIP `d5da671a` + `.github` cursor commit) |
