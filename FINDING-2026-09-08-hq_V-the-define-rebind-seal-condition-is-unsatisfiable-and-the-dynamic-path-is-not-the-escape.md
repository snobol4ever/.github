# FINDING — the DEFINE re-bind seal is dead code by construction, and the dynamic path is NOT the escape hatch

**Seat:** hq_V · **Date:** 2026-09-08 22:0x CDT · **Tree:** SCRIP `60d58c05b` (measured), tree returned CLEAN — nothing landed
**Row:** `snobol4-define-is-resolved-at-compile-time-so-re-define-is-last-wins-for-the-whole-program` (rank 4)
**Continues:** `FINDING-2026-09-08-hq_V-a-redefine-with-an-alternate-entry-binds-one-entry-for-the-whole-program.md` (HQV-7)

## The witness, unchanged and still reproducing

Three `DEFINE`s of one name alternating between two entries, with a call after each:

```
        DEFINE('F()','FA')
        OUTPUT = F() ' one'
        DEFINE('F()','FB')
        OUTPUT = F() ' two'
        DEFINE('F()','FA')
        OUTPUT = F() ' three'
        :(FIN)
FA      F = 'A'
        :(RETURN)
FB      F = 'B'
        :(RETURN)
FIN
END
```

`sbl -bf` reads `A one / B two / A three`. SCRIP reads `A one / A two / A three` in **both** modes — the last `DEFINE` in program text wins for every call.

## ⛔ HQV-7's OPEN QUESTION IS ANSWERED, AND THE ANSWER IS NO

HQV-7 closed with: *"the next question is whether `LBL__F1` is simply absent from `proc_table` for a label that is only a DEFINE entry and never a branch target."* **It is not absent.** Instrumenting the `dentry` loop in `src/driver/scrip.c` (~1429) on this witness prints:

```
DBG bind fn=F own_entry=FA LBL__FA_in_proc_table=YES(with node)
DBG bind fn=F own_entry=FB LBL__FB_in_proc_table=YES(with node)
DBG bind fn=F own_entry=FA LBL__FA_in_proc_table=YES(with node)
```

Both entry labels are present **with `proc_entry_node` set**, and each bind node carries its **own correct entry** via `ir_define_bind_entry` (`FA`, `FB`, `FA`). **Every input the cure needs is already in hand at that loop.** The loop discards it: at `scrip.c:1430` it resolves each bind by `strcmp(_pr->name, IR_LIT(_c).sval)` — the *function* name — so all three binds of `F` find the same proc and take the same entry. That instrumentation was reverted; nothing landed.

## ⭐ THE NEW FACT: THE ROLE-5 BODY SEAL CAN NEVER FIRE

HQV-7 measured that *no store to `body_cell$F` is emitted at all* and attributed it to a NULL `_.lbl_t0`. The reason is stronger than a missing value — **the guard is unsatisfiable by construction.** The `dentry` loop fills its three parallel arrays in exactly two mutually exclusive arms:

| arm | `dentry_entry` | `dentry_name` |
|---|---|---|
| `IR_GOTO_DEFERRED` (`scrip.c:1439`) | `_tn`, non-NULL | **NULL** |
| fallback (`scrip.c:1441`) | **NULL** | `"<fn>_α"` |

`emit.cpp:1260` then derives both halves of the guard from those same arrays:

```
g_emit.lbl_t0 = g_emit_cfg->dentry_name[_dq];   _realstub = g_emit_cfg->dentry_entry[_dq] ? 1 : 0;
```

and the seal is emitted under `if (g_is_text && g_emit.lbl_t0 && _d1st && _realstub)`. **`lbl_t0` non-NULL implies `dentry_name` non-NULL implies `dentry_entry` NULL implies `_realstub == 0`.** The two conjuncts cannot both hold for any bind node in any program. The role-5 emission is dead code, which is why the `M4-BODY-SEAL` machinery in `bb_define.cpp` — the activation really does read `body_cell$F`, and `rt_define_site` really does rebind `p->fn` and set `p->redefined` — has never been reachable. **Fixing the entry resolution alone will not wake it; the guard has to be repaired in the same landing or the seal stays dead.**

## ⛔ A FOURTH MEASURED DEAD END — the dynamic path is not the escape hatch

The tempting small cure is to leave the emitter alone and route a multiply-bound name down the *runtime* `DEFINE` path the lowerer already has (`lower_snobol4.c` ~2251, taken when `sno_def_entry_absent`), since `rt_define_site` rebinds correctly. **Measured and reverted: it makes mode 3 SIGSEGV.** A helper computing "this fname is bound at 2+ sites with differing entries" from `st`/`nst`/`is_def` (pure, no new global) was added and both bind call sites routed through it; mode 3 then died at `0x0` with `core_runtime_error` on the stack — a call through a NULL `fn`, because the dynamic path never resolves the alternate entry label to a body in the interpreter. **Do not re-walk this.** The dynamic path works for the cases `sno_def_entry_absent` already sends it (protected system-function names, and `g_sno_uses_code` with no landing for the label); it is not a general destination for an explicit-entry `DEFINE`.

## Where the next seat should start

Not in the lowerer. **The binding is one-proc-per-name at compile time in BOTH modes** — that is why the two modes are wrong *identically*, and it is the real shape of the defect. A cure has to make the call read a binding that is a runtime value, which is precisely what the dormant `body_cell$<FN>` seal was built for. The minimum landing is therefore **two** repairs together, not one: (1) resolve each bind node through **its own** entry (`ir_define_bind_entry`) rather than by function name at `scrip.c:1430`, populating `dentry_entry` **and** `dentry_name` for that arm; and (2) repair the `lbl_t0 && _realstub` guard so the seal it gates can fire. Mode 3 needs the interpreter's equivalent of the same store; `scrip.c:687` and `:1447`, which skip a `LBL__` proc precisely when it is a DEFINE entry target, are the places that decide whether the alternate entry survives as a callable body at all.

**Row released with this recorded, not marked done.** The `gimpel-linked-list-functions` red it was minted against (via `COPYL`'s self-redefinition trick) is untouched and still red.
