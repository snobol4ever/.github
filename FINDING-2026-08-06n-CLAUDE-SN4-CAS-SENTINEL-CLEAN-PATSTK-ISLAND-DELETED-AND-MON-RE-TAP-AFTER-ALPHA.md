# FINDING 2026-08-06n — CAS-SENTINEL-CLEAN: g_patstk_sp island deleted; MON-RE: monitor tap after alpha

**Session:** Sonnet, 2026-08-06n  
**SCRIP commit:** `1336ce55`  
**Status:** LANDED, gates green (118/23/0/0)

---

## FINDING 1: CAS-SENTINEL-CLEAN — g_patstk_sp pattern stack island is dead

### What existed

`g_patstk_sp` was the stack pointer for an 8MB software "pattern stack" island
(`g_patstk_base`). At each match-begin, the CAS sentinel carried a snapshot of
this pointer at `[+16]` so failure paths could restore `g_patstk_sp` without a
frame-addressed reload (the CAS-MARKER-CARRY design, s22x). The sentinel layout
was 24 bytes: `[+0]=tag0 (varname==0 discriminant), [+8]=rsp_mark, [+16]=patstk_snapshot`.

### Why it was wrong

The model is pure R12/DCAP-island — no separate pattern stack exists in the current
design. `g_patstk_sp` was a ghost from a prior era. The 8MB VAS reservation was
allocated on every process that ran a pattern match, the lazy-init ran on first match,
and the snapshot/restore cycle touched the GOT on every sentinel push and every
failure-path scan — for a variable that was never written by any pattern-matching code
path. It was a pure dead weight.

### What was removed

Six files across the compiler and runtime:

**`src/runtime/pattern_match.c`:** `RT_PATSTK_ISLAND_BYTES` define, `g_patstk_sp` global,
`g_patstk_base` static, and the entire `c_rt_patstk_lazy_init()` function body deleted.

**`src/runtime/builtins/gen_runtime.c`:** `rt_patstk_lazy_init()` call removed from
`c_rt_match_enter`. Comment records the removal.

**`src/runtime/rtx/rtx_match.S`:** The `rt_patstk_lazy_init` RTX stub (formerly RTX-8
slice 5) replaced with a `ud2` tombstone — any surviving call site will trap visibly.
The inlined lazy-init test (`mov r10,[rip+g_patstk_sp@GOTPCREL]; cmp [r10],0; je cold`)
and the `.Lme_patstk_cold` block deleted from `rt_match_enter`'s hot path.

**`src/templates/bb_match_begin.cpp`:** `extern "C" uint64_t g_patstk_sp` declaration
removed. In both the mech-2 arm (line 54) and the main arm (line 195, now 187), the
sentinel push now writes `[r12+16]=0` (dead pad, zeroed) instead of snapshotting
`g_patstk_sp`. All `g_patstk_sp` restores removed from: mech-2 fail-exit, mech-2 hfc
fail-scan, main-arm hfc fail-exit (`[r12+16]` read deleted), main-arm non-hfc ZLS
branch (`cas_patstk rdi` load deleted).

**`src/templates/bb_match_end.cpp`:** `extern "C" uint64_t g_patstk_sp` declaration
removed. Patstk restore from `[r10+16]` removed from the hfc success path and the
default success path. Both now just restore rsp from `[r10+8]` (the rsp_mark slot,
which is still correct and still there).

### Sentinel layout after the fix

The sentinel remains 24 bytes (stride must match `rt_dcap_e = {varname,saved_delta,len}`,
each 8B, total 24B, so the scan loops step by 24 correctly):

```
[+0]   tag0 (0 = sentinel; varname pointers are never 0)
[+8]   rsp_mark  (rsp at α, used by failure paths to restore the stack floor)
[+16]  0         (dead pad, was patstk_snapshot, never read)
```

### Gate result

Default probe suite: 118/23/0/0 — unchanged. No regression.

---

## FINDING 2: MON-RE — statement monitor tap must fire AFTER the alpha label

### The bug

The 2-way sync-step monitor (`PARTICIPANTS="spl scr" bash scripts/test_monitor_3way_sync_step_auto.sh`)
diverged at step 2–3 on every program, making it impossible to bracket any defect.

Root cause: `emit.cpp:1000` case `IR_STATEMENT_BEGIN` called `emit_mon_label_tap(stno)`
**before** calling `bb_emit_x86(bb_statement())`. The tap emitted the monitor call and
then the alpha label appeared. For statements reached by `jmp` (every statement after
the first — `jmp n4_statement_begin_α` etc.), control arrived at the alpha label directly,
bypassing the pre-label tap. Result: every jump-reached statement was invisible to the
monitor, so SCRIP's statement trace diverged from SPITBOL's immediately.

### The fix

Three edits:

1. **`src/emitter/emit.h`:** Added `int op_mon_stmt_tap` field to `g_emit` struct,
   adjacent to `op_stno`.

2. **`src/templates/bb_statement.cpp`:** Added `extern "C" void mon_emit_label_bin(int64_t stno)`
   declaration. Added `IF(_.op_mon_stmt_tap, x86("comment","MON LABEL tap") + x86("mov","rdi",(long)_.op_stno) + x86("call","mon_emit_label_bin",...))` after `x86_alpha()` in the template body. The tap now fires INSIDE the box, after the alpha label, so every arrival (including jmp-arrivals) traces correctly.

3. **`src/emitter/emit.cpp:1000`:** Rewrote the case to stage `g_emit.op_mon_stmt_tap`
   and `g_mon_max_stno` before calling `bb_emit_x86(bb_statement())`, then clears the flag
   after. The pre-label `emit_mon_label_tap()` call is gone.

### Gating effect

Gated on `MONITOR_BIN=1` environment variable — absent in normal runs, so default
codegen is byte-identical. The tap emits exactly like the existing tap in `bb_succeed.cpp`
(which already had the correct post-α placement as a reference).

Verified: `PARTICIPANTS="spl scr" ... defprobe.sno` → exit 0 (agreement).

---

## FINDING 3: HEAD-PIN bug — roman.sno wrong output, pre-existing at 590b9140

Not fixed this session; documented for the next.

In a multi-statement main graph (e.g. `roman.sno` which has stmt A = `N RPOS(1) LEN(1) .T =`
and stmt B = `'0,1I,...' T BREAK(',') .T`), the `rpin()` predicate fires for each
statement's `bb_match_begin` (`flat_deep_arrival=1, !flat_jmp_entry`). Each HEAD-PIN does
`mov rbp,rsp` to its OWN claim base. The PATCTX saves (`r13/r14/r15/capgen`) write
through `FRQ(op_off+48..72)` which with `x86_fb_data()=1` (whole-graph rbp pin) resolves
to `[rbp+48..72]` = `[stmt_claim_base+48..72]` — **correct at write time**.

The problem: when stmt A's match **fails** after stmt B has already run and pinned its own
rbp, rbp holds stmt B's claim base. Stmt A's fail-exit reads `[rbp+48..72]` → garbage →
`rt_match_ctx_restore` gets garbage → crash or wrong output.

**Confirmed pre-existing:** `git stash; make -j4 scrip; ./scrip --run roman.sno` → `result: `
(empty, wrong). Our commit did not introduce this.

**Fix direction (for next session):** Before the PATCTX restores on the fail exit of
`bb_match_begin`, reload rbp from the saved old_rbp slot:
```cpp
+ IF(rpin() && !stfh() && !_.op_stmt_pin,
    x86("note", "pin_restore") + x86("mov", "rbp", RDQ("rsp", hoff(_.op_off + 40))))
```
After the CAS rsp_mark restore puts rsp back at claim_base, `[rsp+hoff(op_off+40)]` is
the saved old_rbp written rsp-relatively at alpha before the `mov rbp,rsp` pin. Once rbp
is reloaded to stmt A's claim base, `[rbp+48..72]` addresses stmt A's own PATCTX slots
correctly. Gated `rpin() && !stfh() && !op_stmt_pin` to not fire when the STF bracket
or terminal-cut path handles the restore.
