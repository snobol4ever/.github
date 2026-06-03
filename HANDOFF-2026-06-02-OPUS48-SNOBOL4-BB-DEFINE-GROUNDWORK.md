# HANDOFF — SNOBOL4 BB: `define` runtime groundwork + LI-FENCE repair

**Author:** Claude Opus 4.8 (third developer). **Date:** 2026-06-02.
**Repo tips after this session:** SCRIP `a9e1ff1` (two commits: `76ff512` LI-FENCE repair → `a9e1ff1` define
groundwork); `.github` = the commit carrying this file.

This session oriented from the SPITBOL manual (ch.8 "Program-Defined Functions"; ch.3 concat/coercion),
verified the live state, repaired a pre-existing LI-FENCE false positive, and landed the **runtime call-frame
foundation** for the `define` smoke (the lone remaining SNOBOL4 mode-3 failure). It deliberately STOPPED before
the byte-producing emit + driver wiring so that work lands as one finished, gated unit in a focused continuation
(per RULES "never start a split you cannot finish+gate+commit").

---

## 1. LI-FENCE repair (commit `76ff512`)

`scripts/test_gate_no_lang_names.sh` was **FAILING** at session start (4 hits). Cause: the gate's tag regex
`(...|pl_|_pl|...)` matches `_pl` as a substring, and the `__pas_writeln` Pascal helper in
`src/runtime/builtins/gen_runtime.c` used a local `int _pl = snprintf(...)` — a field-width / print-length
scratch, NOT a Prolog (`pl`) language tag. Renamed `_pl` → `_pfmtlen` (no `_pl` substring). Rename-only,
behaviorally byte-identical; LI-FENCE now holds without needing an allowlist entry.

## 2. `define` runtime groundwork (commit `a9e1ff1`, ADDITIVE / byte-neutral)

Added to `src/runtime/rt/rt.c` + decl in `rt.h`:

- **`DESCR_t rt_call_named_proc(const char *name, DESCR_t *args, int nargs)`** — the SNOBOL4 call frame, modeled
  on the proven mode-2 `IR_interp.c` `IR_CALL dval==2.0` user-proc path. SPITBOL Manual ch.8 p.106 semantics:
  on call, the dummy args + locals (the proc's `pnames[0..nparams]`) AND the function-named binding are saved on
  a pushdown stack (`g_name_save` via `NV_GET_fn`), the actuals are installed into the params / null into the rest
  via `NV_SET_fn`, control runs the proc's BB-graph `fn` on a **per-activation frame** sliced from a dedicated
  recursion-safe arena (`g_proc_frame_nest_arena`), the function-named variable is read back as the result
  (`NV_GET_fn(name)`), FRETURN (the `fn` returning FAIL) yields FAILDESCR, and the saved bindings are restored
  LIFO. This is the global-variable / name model, NOT Icon's frame-slot model — correct for SNOBOL4 whose IR_VAR
  reads and IR_ASSIGN writes go by name through the NV table.
- **`DESCR_t rt_proc_define(const char *spec)`** — the mode-3 DEFINE entry. A success no-op (returns NULVCL):
  the driver pre-registers procs at compile time from `proc_table`, so DEFINE at runtime need only succeed for
  statically-known prototypes. (A runtime-computed prototype string — SPITBOL's fully-dynamic DEFINE — would
  need this to actually register; out of scope for the smoke, flag if a corpus test needs it.)

**Naming (LI rung):** named by the CS concept, NOT the language. The mechanism is a *name-save call frame*
(`rt_call_named_proc`), the globals are `g_name_save` / `NAME_SAVE_MAX` / `g_proc_frame_nest_*`. An earlier draft
used `rt_sno_*` / `g_sno_*` / `SNO_*` and tripped LI-FENCE (26 hits) — corrected before commit.

**Why this is safe to land alone:** pure C, no emit/byte risk, and **not yet called by any emit path**, so all
program output is unchanged (m3 stays 5/6). It is the linchpin every remaining step calls.

## 3. The `define` IR shape (verified this session)

A temporary `bb_print` extension (IR_CALL/IR_RETURN/IR_BINOP detail, reverted) confirmed: `main` and `DOUBLE`
are two VIEWS over ONE shared 16-node graph (main entry node 4, DOUBLE entry node 7). Key nodes:
- `[9] IR_CALL fn="DEFINE" narg=1 dval=2` — DEFINE call
- `[11] IR_CALL fn="DOUBLE" narg=1 dval=2` — DOUBLE call (γ→[10] IR_ASSIGN OUTPUT)
- `[12] IR_ASSIGN name="DOUBLE" dval=0` ← `[13] IR_BINOP op_ival=0` (ADD) ← `[14]/[15] IR_VAR X` — the body
- `[2] IR_RETURN dval=1` (RETURN), `[3] IR_RETURN dval=2` (FRETURN)
Both calls are `IR_CALL dval==2.0`; arg sub-graphs ride on `counter` (as the mode-2 path + `bb_call` dval==2 arm
already assume).

## 4. REMAINING — byte-producing emit + driver (the focused continuation)

Do these together as one gated unit; gate target = `define` smoke → `42`, m3 5/6 → 6/6, raise MODE3_MIN 5→6.
Build BOTH `scrip` + `libscrip_rt` after any `src/emitter/**` edit. Byte-verify any new encoder vs `as`.

1. **Driver proc-registration** (`src/driver/scrip.c`, the SNOBOL `else {}` mode-3 block that today only builds
   `main` via `gvar_flat_chain_build`): `rt_proc_reset()`; for each non-`main` proc in `s2->proc_table[]`, build
   its chain (a `gvar_flat_chain_build`-style builder over the proc's entry — i.e. a `gvar_flat_chain_build_proc`
   that seeds the slab from the proc's entry node, sibling of `descr_flat_chain_build_proc`) and
   `rt_proc_register(name, entry, pnames, nparams)` + `rt_proc_set_fn(name, fn)`. The entry, `nparams`, and
   `lower_sc` param names are all in `proc_table`. Model: the Icon mode-3 loop at `scrip.c:~887`. NOTE the proc
   `fn` is invoked by `rt_call_named_proc` as `fn(frame, 0)` where `frame` is its own arena slice — the proc's
   gvar chain uses ζ=r12 for its scratch, so the frame must be a valid writable buffer (the arena provides it).
2. **`bb_call` DEFINE arm** (gvar path, guard `g_gvar_flat_chain`, `fn=="DEFINE"`): RO-load the spec string,
   `call rt_proc_define`, then `jmp γ` / `def β` / `jmp ω` (single-shot). (Or, since registration is done by the
   driver, simply succeed — but calling `rt_proc_define` keeps the door open for dynamic prototypes.)
3. **`bb_call` user-proc arm** (gvar path, `rt_proc_is_registered(fn)`): evaluate each arg sub-graph to its
   value (into the call's ζ-slots or a staged DESCR array), `call rt_call_named_proc(fn, args, narg)`, store the
   returned DESCR into this IR_CALL's own ζ-slot (the consuming IR_ASSIGN reads it via its `α` operand-ref),
   `test`/`je ω`/`jmp γ`. The arg-marshalling can reuse the `marshal_call_arg` / `rt_arg_stage` pattern, but the
   call itself is `rt_call_named_proc` (name model), not `rt_call_proc_descr` (Icon frame-slot model).
4. **RETURN/FRETURN** in the gvar chain: `flat_drive_return` already jumps to the slab SUCCESS exit
   (`flat_succ_p`) — correct for return-by-value (the function-named var already holds the result; the slab exit
   returns control to `rt_call_named_proc`, which reads it). Add a `dval==2.0` (FRETURN) arm that jumps to the
   slab FAILURE exit (`flat_fail_p`) instead.

## 5. Gate state (GREEN; baseline for the continuation)

SNOBOL4 m2 **7/7 HARD** / m3 **5/6** / m4 0/6 · Icon m2 **12/12 HARD** · `prove_lower2` PASS · `no_bb_bin_t` 0 ·
**LI-FENCE OK** (was failing at session start) · `audit_concurrency_invariants` OK · `test_gate_sm_dead` OK.
ENV: `apt-get install -y libgc-dev` (`core.h` / `raku_nfa_bb.c` include `<gc/gc.h>`).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
