# HANDOFF-2026-06-12-SONNET46-ICON-FULL-PASS-GENARG-POW-M3EXCISE.md

## Session Summary

**Goal:** GOAL-ICON-FULL-PASS — push m2/m3/m4 Icon pass counts; eliminate EXCISED.
**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6

---

## Watermark

**HEAD (SCRIP) = `3e08aaa`** (unchanged — changes NOT yet committed, see below)
**Baseline:** m2=194 · m3=29 (184 EXCISED) · m4=32 (142 EXCISED)
**With WIP applied:** m2=199 · m3=38 (115 EXCISED) · m4=38 (115 EXCISED)
**Gain:** m2 +5 · m3 +9 (EXCISED −69) · m4 +6 (EXCISED −27)

**HEAD (.github) = this file**

---

## Changes In-Flight (NOT YET COMMITTED — apply with git stash pop or verify diff)

Four files modified from `3e08aaa`:

### 1. `src/runtime/arithmetic.c` — POWER_fn always-real (FULL-19 extension)
**What:** Removed the integer fast-path from `POWER_fn`. Icon spec: `^` always returns real regardless of operand types.
**Why:** `2^10` was returning integer `1024` instead of real `1024.0`.
**Tests fixed (m2):** rung19 (+2), rung26 (+3) — total +5 m2.
```c
DESCR_t POWER_fn(DESCR_t a, DESCR_t b) {
    if (IS_FAIL(a) || IS_FAIL(b)) return FAILDESCR;
    double r = pow(to_real(a), to_real(b));
    if (isinf(r) || isnan(r)) { core_runtime_error(2, NULL); return FAILDESCR; }
    return REALVAL(r);
}
```

### 2. `src/lower/lower_icon.c` — generator-in-call-arg (FULL-18-resid partial)
**What:** `lower_call()` now detects resumable (generator) args via `is_resumable()` and uses the inline chains path instead of isolated subgraph blocks.
**Why:** `every write(tag("a"|"b"|"c"))` — the ALT inside `tag(...)` was put in an isolated subgraph, making it invisible to the flat chain's resume pumping. Chains mode inlines the ALT directly into the flat chain so EVERY can drive it.
**Guard:** `[]` and `MAKELIST` are excluded from the chain-upgrade (they stay subgraph for both simple and generator args). Generator args to `[]` get `cx->beta = call` (not ω) so EVERY can re-enter the subscript.
**Tests fixed (m2):** rung32 (+1). rung16 still broken (see NEXT STEPS).

### 3. `src/interp/IR_interp.c` — stateful `[]` subscript with generator index
**What:** Added special-case handler for `IR_CALL` with `dval==2.0` (subgraph mode), `sval="[]"`, `nargs==2`. On state==0 (fresh): evaluates both arg subgraphs and caches obj in `susp_gen_cache`. On state==2 (resume): re-uses cached obj and re-evaluates the index subgraph only (not fresh-starting it).
**Why:** `every write(s[1 to 3])` — each EVERY resume was re-evaluating `s` (correct) but also re-entering `1 to 3` from scratch (wrong — TO would restart from 1 every time). The special case holds `s` across resumes and pumps TO through.
**Status:** Partial — `s[1 to 3]` still outputs only `3` (not `a b c`). The state machine is close but the TO resume cycle isn't fully threaded (see NEXT STEPS).

### 4. `src/driver/scrip.c` — Remove over-conservative m3 excision guards
**What (a):** Removed 5 `return 0` guards from `icn_graph_native_emittable_mode()`:
- `icn_kind_native_stub(nd->op)` — blocked IR_GEN_ALT, IR_KEYWORD, IR_SUSPEND, IR_BINOP_GEN etc.
- `has_lassign && !icn_assign_safe_kind(nd->op)` — blocked local vars with most node types
- `has_lassign && BINOP non-arith` — blocked pow, concat, relop in local-var procs
- `has_lassign && has_binop && LIT_F/LIT_NUL` — blocked float literals in local-var procs
- `has_lassign && CALL != write/writes` — blocked any proc call in progs with local vars
- `for_run && CALL dval==3.0` — blocked ALL user-proc calls in m3
**What (b):** Moved `rt_proc_reset()` + first proc-registration loop to run **before** `icn_graph_native_emittable_mode()`. Previously, proc names were not yet registered when the emittability check ran, so `rt_proc_is_registered()` always returned false for user procs, causing the `bb_call.cpp` dispatch to fall through to the wrong template.
**Effect:** m3/m4 EXCISED count drops 69 in m3, 27 in m4. Programs that previously bailed with `[SMX]` now either PASS or FAIL.

---

## NEXT STEPS (Ordered by Impact)

### BLOCKER: `bb_return.cpp` writes result then jumps to proc ω — ω overwrites result with FAIL

**Root cause:** `bb_return_str()` emits:
```
mov [r12+0], rax   ; write return value
mov [r12+8], rdx
jmp ω              ; ← jumps to proc_ω
```
The proc's `ω` block (`icn_proc_X_ω`) immediately does:
```
mov dword ptr [r12+0], 99   ; OVERWRITES return value with DT_FAIL!
```
So `rt_call_proc_descr` reads back FAIL from `[r12+0]`, sees `eax==99`, returns FAILDESCR. All user-proc calls in m3 and m4 silently fail — `write(answer())` outputs nothing.

**Fix:** `bb_return.cpp` must NOT jump to `ω`. It should jump to a dedicated "proc return success" label that goes straight to the ABI exit (`mov eax,1; xor edx,edx; pop r12; ret`) without passing through the `ω` FAIL-write block. Options:
- Add a `γ` label alias for the proc success exit and emit `jmp γ` from RETURN.
- Emit inline `mov eax,1; xor edx,edx; pop r12; ret` from the RETURN template directly.
- Add a new `PORT_PROC_γ` marker that resolves to the proc's γ label.

The m4 text emitter has the same bug structurally (RETURN → jmp ω → ω writes FAIL) but m4 still shows correct output for simple proc tests — likely because `main_ω` has the FAIL-write block and when RETURN is in a sub-proc, the sub-proc's ω writes FAIL then the call site sees FAIL and doesn't write. Verify this on the linked binary.

### FULL-18-resid: `s[1 to 3]` still gives `3` only (rung16)
The IR_interp.c special case for `[]` stateful subscript is in place but the TO generator isn't correctly being pumped. In the IR_interp `dval==2.0, sval="[]"` handler: on state==2 (resume), `IR_interp_once(ab1)` re-runs the TO subgraph. But `IR_interp_once` evaluates `ab1` fresh (calls `bb_reset(ab1)` first?). Check whether `ab1`'s state is preserved between resumes — `bb_reset` must NOT be called on resume path. The `every write(s[1 to 3])` chain: EVERY → write → `[]` call → TO. EVERY's β should pump write's β → `[]`'s β → TO's β. Currently `[]` in state==2 re-enters TO from state==0 (fresh).

Fix: on state==2, do NOT call `bb_reset(ab1)` — just call `IR_interp_once(ab1)` with its existing state. Then if `ab1` returns FAIL (TO exhausted), reset state to 0, return FAIL to pump EVERY.

### FULL-12: `integer(x)` / `real(x)` coercion
All type combos. `integer("3")` → 3, `real(7)` → 7.0. Currently outputs wrong. Consult `refs/icon-master/src/runtime/oarith.r` — `i_to_proc` and `r_to_proc`. Add to `by_name_dispatch.c`. Affects rung36 (+5), rung37.

### FULL-13-resid: keywords rung37 residuals
Three residuals: `&lcase`, `&ucase` (string constant keywords), `&pos` write-back on scan exit, `&error` write-back, `&random`, `&dump`/`&trace`. `&lcase`/`&ucase` are read-only string constants — add to `keywords.c`. `&pos` write-back: after scan stmt exits, set `&pos` to final position.

### FULL-17: `sort(L)` / `sort(T,i)` 
`rt_list_sort` in `aggregates.c`. Consult `refs/icon-master/src/runtime/fstranl.r`. Affects rung31 (+5).

### FULL-14: scan-alt `s ? (e1|e2)` resume
`IR_GEN_SCAN` resume re-enters across alt. Rung37 (+2).

### FULL-15: remaining str-relop cases
`ac == 'ca'` → string comparison (lexicographic). `by_name_dispatch.c`. Rung37 (+1).

### FULL-16: mutual recursion forward refs
`rt_call_named_proc` for procs referenced before definition. Rung37 (+1).

### m3/m4 remaining excisions
115 still EXCISED in both modes. Most are from `icn_kind_native_stub` (IR_GEN_ALT, IR_SUSPEND, IR_BINOP_GEN, IR_KEYWORD, IR_PROC_GEN — Icon generators, scan, cset) and complex assign shapes (`icn_local_assign_rhs_ok` returns 0 for CALL-on-RHS). Each needs corresponding native templates or the emittability check relaxed further with crash-safe fallback.

---

## Key Architecture Notes (do not re-derive)

**Excision flow (m3):** `scrip.c --run` → `icn_graph_native_emittable_mode(s2, for_run=1)` → if returns 0 → prints `[SMX]` and exits 0. The test runner counts `[SMX]` stderr as EXCISED (not FAIL). User directive: no EXCISED ever.

**Proc registration order (CRITICAL — already fixed):** `rt_proc_register` (name→entry, fn=NULL) must run BEFORE `icn_graph_native_emittable_mode` so `rt_proc_is_registered()` works. `rt_proc_set_fn` (name→bb_box_fn) runs AFTER, in the second loop.

**dval conventions for IR_CALL:**
- `dval=1.0` — chains (inline flat chain, write/writes or gen-arg detected)
- `dval=2.0` — subgraph, `[]`/MAKELIST style (args in blks[])
- `dval=3.0` — subgraph, user-proc/builtin style (args in blks[])

**`is_resumable(t)`:** checks if a tree node is a generator (ALT, TO, TO_BY, EVERY, WHILE, etc., or a call to a known generator builtin). Used by `lower_call` to decide chains vs subgraph.

**Slot map:** `g_bb_slotmap` is per-build-session. `descr_flat_chain_build_proc` resets it (`g_bb_slotmap_n=0`) before building each proc binary. After the proc is built, the slotmap contains ONLY that proc's nodes. When main binary is built next, `bb_call_proc_staged_str`'s `bb_slot_get(arg_terminal)` looks up an arg node from a sub-proc's subgraph — that node's slot was in a PREVIOUS slotmap session and returns -1. This is why proc calls with args fail silently (slot -1 → fallback to 0 → reads wrong frame slot). Fix by emitting arg subgraphs inline in the main binary frame via `flat_emit_arg_subchain` (already done for `ival>0` in `flat_drive_userproc`) — but the `bcps_bin_arm` slot lookup happens after emission, so it should find the slot. Investigate whether the slot is actually allocated during `flat_emit_arg_subchain` for BINARY medium (it should be — `walk_bb_flat` → `walk_bb_node` → `bb_slot_alloc16`).

---

## Session Setup

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
bash scripts/test_icon_rung_suite.sh   # expect m2=199 m3=38 m4=38 with WIP
bash scripts/test_smoke_icon.sh
bash scripts/test_smoke_prolog.sh
```

## Gate After Every Step

```bash
bash scripts/build_scrip.sh && make libscrip_rt
bash scripts/test_icon_rung_suite.sh   # m2 >= 199; m3 >= 38; m4 >= 38
bash scripts/test_smoke_prolog.sh
bash scripts/test_gate_bb_one_box.sh
```

## Canonical Source Rule

Before ANY construct: grep canonical FIRST.
- Port topology → `refs/jcon-master/tran/irgen.icn`
- Runtime → `refs/icon-master/src/runtime/*.r` (`fstranl.r`, `oarith.r`, `oref.r`, `ocomp.r`)
