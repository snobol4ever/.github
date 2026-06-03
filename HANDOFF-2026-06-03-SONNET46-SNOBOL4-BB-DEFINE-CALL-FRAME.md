# HANDOFF 2026-06-03 (Sonnet 4.6) — SNOBOL4 `define` mode-3: call frame + RETURN routing land; no-arg user calls GREEN

## Summary

Continued the `define` frontier (SNOBOL4 mode-3, the last failing smoke). **No-argument user-proc
calls now run end-to-end in mode-3, matching the SPITBOL oracle.** DEFINE registration, the
name-save call frame, and RETURN/FRETURN routing all work. The full `define` smoke
(`DOUBLE(21)` → `42`) is **not yet green** — it is blocked on two precisely-diagnosed issues
(string-arg `slen`, and param-to-param arithmetic), documented below.

**All HARD gates hold; this is a safe incremental landing (m3 unchanged at 5/6, m2 7/7).**

## Gate state (verified this session, clean rebuild of `scrip` + `libscrip_rt`)

- SNOBOL4 m2 **7/7 HARD** · m3 **5/6** (only `define`) · m4 0/6
- Icon m2 **12/12 HARD** · m3 4/12 · m4 4/12 (NOT regressed by the shared-file touches)
- `prove_lower2` PASS · `no_bb_bin_t` 0 · LI-FENCE OK · concurrency invariants OK
- ENV: `apt-get install -y libgc-dev`

## What landed (SCRIP — 7 files, +158/−8; NOT a fresh feature, an incremental step)

The 4 HANDOFF wiring steps for `define` were implemented; 3 real bugs found + fixed en route.

1. **Driver registration (`scrip.c`, SNOBOL mode-3 `--run` block).** Before building `main`, the
   loop now `rt_proc_reset()`s, and for each non-`main` proc: `rt_proc_register(name, entry,
   pnames, nparams)` + `gvar_flat_chain_build(proc_graph)` + `rt_proc_set_fn(name, fn)`. Mirrors
   the Icon mode-3 loop. (Proc graphs are VIEWs over the one landing-node graph with their own
   entry; building each is byte-safe and does not corrupt `main`'s later fold — verified.)

2. **`bb_call` DEFINE arm (`bb_call.cpp`, `bb_call_gvar_define_str`).** `g_gvar_flat_chain &&
   dval==2.0 && fn=="DEFINE"` → load spec (RO) → `call rt_proc_define` → single-shot `jmp γ / def
   β / jmp ω`. BINARY + TEXT. (`rt_proc_define` stays a no-op success in mode-3 — registration is
   done by the driver; the call is emitted for correctness.)

3. **`bb_call` user-proc arm (`bb_call.cpp`, `bb_call_gvar_userproc_str`).** `g_gvar_flat_chain &&
   dval==2.0 && rt_proc_is_registered(fn)` → marshal args to a ζ-frame DESCR array (reusing
   `marshal_call_arg`) → `call rt_call_named_proc(fn, &frame[argbase], narg)` → store result DESCR
   → `cmp eax, 99 / je ω / jmp γ` (DT_FAIL=99 → ω, i.e. FRETURN fails the call). Routed the gvar
   `dval==2.0` IR_CALL straight to FILL in `walk_bb_flat` (args live in `counter` sub-graphs, so
   the legacy `α->γ` arg-walkers must be bypassed).

4. **IR_ASSIGN(call-result) arm (`bb_gvar_assign.cpp`) + RETURN/FRETURN routing.**
   - New 5th arm in `bb_gvar_assign`: `op_a_node_kind==IR_CALL` reads the call's result DESCR from
     its ζ-slot (`op_a_slot` lo/hi) and stores it into the named global via the **new runtime
     helper `rt_gvar_assign_descr(name, lo, hi)`** (added to `rt.c`, reconstructs the DESCR from
     two qwords). Wired `IR_CALL` into both IR_ASSIGN dispatch points (`emit_core.c` walk_bb_node +
     `emit_bb.c` walk_bb_flat).
   - **`flat_drive_return` rewritten:** it was `EMIT_PAIR_FILL`-ing IR_RETURN, but `walk_bb_node`
     has **no IR_RETURN template** → the box emitted nothing and the chain fell through (segfault).
     Now emits a direct `emit_jmp_label` to the slab **success** exit (`flat_succ_p`), with FRETURN
     (`dval==2.0`) routing to the slab **failure** exit (`flat_fail_p`). This is HANDOFF step 4 and
     also the fix for the IR_RETURN crash.

### 3 real bugs found + fixed (these are the reason it took the whole session)

- **`x86("mov", reg, (uint64_t)ptr)` is a TRAP.** That overload — `x86(mnem, sym, uint64_t)` —
  **ignores the mnemonic and always emits `movabs rax,imm; call rax`** (it routes to
  `x86_call_ro`). So `x86("mov","rdi",ptr)` *calls* the pointer instead of loading it → segfault.
  Compounding it, **`x86_movimm` silently truncates imm64 to 32 bits** (`u64le((uint64_t)(uint32_t)imm)`).
  **RULE for the next session: to load a pointer / full imm64 into a register in BINARY mode, use
  `x86_load_ro(reg, "??", ptr)`** (full 64-bit movabs in BINARY, `lea [rip+label]` in TEXT). Fixed
  in the DEFINE arm, the user-proc arm, and the shared `marshal_call_arg` IR_LIT_I branch.
  ⚠ The SAME buggy `x86("mov","rdi",(uint64_t)fn)` still exists in `bb_call_rk_arr_str` and the
  nested-call branch of `marshal_call_arg` (the Raku `g_descr_flat_chain` path) — LEFT ALONE
  (out of the SNOBOL lane; not exercised by SNOBOL; "fixing" risks changing Raku bytes). If Raku
  `rt_call_arr` mode-3 is ever exercised it will hit this same trap — flagged here.
- **args-array address vs contents.** The user-proc arm needs `rsi = &frame[argbase]` (the array
  address), but `x86_frame_load64` *loads the contents*. Added a new encoder **`x86_frame_lea(reg,
  off)`** (`lea reg,[r12+off]`) to `x86_asm.h` (additive, byte-neutral to other langs) and used it.
- IR_RETURN crash (see step 4 above).

## REMAINING — two issues block `DOUBLE(21)`→`42` (next session starts here)

1. **String args lose their length (the `slen` bug).** `marshal_call_arg`'s IR_LIT_S BINARY branch
   writes `mov qword [aoff], 1` (tag=DT_S in the low 4 bytes) but leaves **`slen`=0** in the high 4
   bytes of that same low qword. So a string parameter reads back as a **zero-length** DT_S string
   (`OUTPUT = Y` for `G('AB')` prints empty, not `AB`). DESCR layout is `{DTYPE_t v (4B); uint32_t
   slen (4B); union payload (8B)}` — the low qword packs `v | (slen<<32)`. **FIX:** write `v |
   ((uint64_t)strlen(s) << 32)` into the tag qword for the IR_LIT_S case. ⚠ `marshal_call_arg` is
   SHARED with the Raku path — do it in a way that's byte-neutral to Raku (or, cleaner: have
   `rt_call_named_proc` normalize DT_S args by recomputing `slen` from the C string — keeps the
   emitter untouched, but is a runtime hack; prefer the emitter fix if it can be made lane-safe).
   VERIFIED ROOT CAUSE via a debug build: arg entry kind=1 (IR_LIT_S) sval="AB" marshalled to the
   right slot; the body runs; only the length is wrong.

2. **`X + X` (param-to-param arith) bombs `bb_binop_arith`** ("shape mismatch (dispatch chose this
   arm but predicate failed)"). The `define` smoke's `DOUBLE = X + X` is a binop of two VAR (param)
   operands, not the literal-literal `IR_BINOP_GVAR_ARITH` shape the gvar arith arm currently
   bakes. This is the same fusion limitation the goal file's BB-HYGIENE / de-fuse notes describe:
   the gvar binop arm needs operands read from ζ-slots (producer boxes) rather than baked
   immediates. **This is the larger of the two remaining pieces** and likely wants the de-fuse
   (make both binop operands producer boxes whose values land in ζ-slots the arith box reads),
   coordinated with the REG / BB-HYGIENE ladders.

A no-arg proc returning a literal, and a no-arg proc reading a GLOBAL, both work — so once (1)+(2)
land, the smoke should pass. Suggested ladder: fix (1) first (1-arg string call → `hello`), then
(2) (the `X+X` body) → `DOUBLE(21)` → `42`, raise MODE3_MIN 5→6.

## Build / verify recipe (next session)

```bash
cd /home/claude/SCRIP
bash scripts/build_scrip.sh && make libscrip_rt   # BOTH — emit path lives in scrip AND libscrip_rt
bash scripts/test_smoke_snobol4.sh                # m2 7/7 HARD; m3 5/6 (target 6/6)
bash scripts/test_smoke_icon.sh                   # m2 12/12 HARD (shared-file regression check)
bash scripts/prove_lower2.sh ; bash scripts/test_gate_no_bb_bin_t.sh
bash scripts/test_gate_no_lang_names.sh ; bash scripts/audit_concurrency_invariants.sh
```

Repro files used this session (recreate as needed):
`DEFINE('DOUBLE(X)') / OUTPUT = DOUBLE(21) / :(END) / DOUBLE DOUBLE = X + X / :(RETURN) / END`
(oracle `42`); a 1-arg string variant `G(Y) { G = Y }` over `G('AB')` (oracle `AB`, currently
empty — the slen bug).

## Watermark

SCRIP tip = this commit (define call-frame + RETURN routing + movabs/lea fixes; m3 5/6, define
still blocked on string-slen + param-binop). .github tip = this commit. Detail: this file.
