# GOAL-MODE4-SN4-SNOCONE.md — Mode-4 x86 Full Test Suite: SNOBOL4 + Snocone

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

⛔ **Read before any source file:** `ARCH-x86.md` then `ARCH-SCRIP.md` then `ARCH-EMITTER.md`.

**Repo:** one4all+corpus+.github.
**Done when:** every SNOBOL4 and Snocone test that passes under `--sm-run` also passes under `--jit-emit --x64` (linked binary via libscrip_rt.so). Zero regressions vs the `--sm-run` baseline.

**Mode-4 pipeline recap:** `scrip --jit-emit --x64 file.sno` → `.s` → `gcc -c` → `gcc link -lscrip_rt` → ELF binary → run. All test harness scripts use this pipeline with the working dir set to `/home/claude/one4all` (for macro includes).

---

## Baselines (one4all `3cfbfae0`, 2026-05-15)

| Suite | Script | Mode-4 now | Target |
|---|---|---|---|
| smoke_snobol4 | `test_smoke_snobol4.sh` | 7/7 ✅ | 7/7 |
| beauty subsystems mode-4 | `test_gate_em_beauty_subsystems_mode4.sh` | 15/17 | 17/17 |
| crosscheck_snobol4 | `test_crosscheck_snobol4.sh` | 6/6 ✅ | 6/6 |
| crosscheck_snocone | `test_crosscheck_snocone.sh` | 8/8 ✅ | 8/8 |
| gate_em8_snocone | `test_gate_em8_snocone_jit_emit.sh` | 5/5 ✅ | 5/5 |
| broad corpus SNOBOL4 | `test_mode4_broad_corpus_snobol4.sh` | 240/280 | ≥250 |
| beauty self-host | `test_gate_sn7_beauty_self_host.sh` | — | PASS |

---

## Steps

(M4SN-0 through M4SN-3 ✅ completed. M4SN-4a ✅ completed: `test_mode4_broad_corpus_snobol4.sh` exists in `scripts/`. Currently active: **M4SN-4b**.)

### M4SN-4 — Broad corpus SNOBOL4: sm-run parity in mode-4

- [ ] **M4SN-4b** — Run and triage failures by category. Fix mode-4-specific failures only. Current: 240/280 (target ≥250). Live diagnostics for the next two fixes in the **Watermark** section below (1016_eval EVAL segfault; 1114_item ITEM_SET routing via `_usercall_hook` + `rt_chunk_lookup` export).
- [ ] **M4SN-4c** — Target: mode-4 broad corpus PASS ≥ sm-run PASS. No regression vs sm-run.

### M4SN-5 — Full regression: test_regression_full_corpus.sh MODE=x64 with libscrip_rt pipeline

The existing `test_regression_full_corpus.sh MODE=x64` uses the old mock-include pipeline (13/430). Rewrite or add a new script using the libscrip_rt.so pipeline.

- [ ] **M4SN-5a** — Write `test_mode4_full_regression.sh`: iterate all crosscheck .sno files, emit→link→run via libscrip_rt.so, compare vs .ref. Report PASS/FAIL/SKIP.
- [ ] **M4SN-5b** — Run and establish true mode-4 baseline count.
- [ ] **M4SN-5c** — Fix mode-4-specific failures. Target: PASS count ≥ sm-run PASS count on same corpus.

### M4SN-6 — beauty self-host in mode-4

- [ ] **M4SN-6** — Run `test_gate_sn7_beauty_self_host.sh` with mode-4. beauty.sno parsed and run as mode-4 binary should produce byte-identical output to SPITBOL oracle. Gates: beauty_self_host PASS, smoke 7/7, beauty 17/17.

---

## Session Setup

```bash
git config --global user.name "LCherryholmes"
git config --global user.email "lcherryh@yahoo.com"
# repos already cloned: one4all, corpus, .github, x64
bash /home/claude/one4all/scripts/build_scrip.sh
make -C /home/claude/one4all libscrip_rt
make -C /home/claude/one4all out/sm_codegen_x64_emit_test
make -C /home/claude/one4all out/sm_phase2_sim_test
make -C /home/claude/one4all out/bb_flat_text_test
# Confirm HEAD
cd /home/claude/one4all && git log --oneline -1  # expect 4f0e2996 or later
```

**Mode-4 compile+link helper** (use this inline in scripts):
```bash
compile_mode4() {
  local sno="$1" out="$2"
  local tmp=$(mktemp -d)
  /home/claude/one4all/scrip --jit-emit --x64 "$sno" > "$tmp/p.s" 2>/dev/null || { rm -rf "$tmp"; return 1; }
  (cd /home/claude/one4all && gcc -c "$tmp/p.s" -o "$tmp/p.o" 2>/dev/null) || { rm -rf "$tmp"; return 1; }
  gcc "$tmp/p.o" -L/home/claude/one4all/out -lscrip_rt -lgc -lm \
      -Wl,-rpath,/home/claude/one4all/out -o "$out" 2>/dev/null || { rm -rf "$tmp"; return 1; }
  rm -rf "$tmp"
}
```

---

## Watermark

**HEAD** one4all `3cfbfae0` · Baselines: smoke 7/7 ✅, crosscheck_sn4 6/6 ✅, crosscheck_sc 8/8 ✅, gate_em8 5/5 ✅, beauty 15/17, mode-4 broad corpus 240/280.

Sess 2026-05-15e (Claude Opus 4.7): M4SN-4b — `rt_set_stno` → `comm_stno` wiring. Mode-4 binaries were reporting `** Error N in statement 0` for every runtime error because `rt_set_stno()` only set `kw_stno` but never invoked `comm_stno()` (which is what `g_sno_err_stmt` tracks for the error printer). sm-run/jit-interp paths reach `comm_stno()` via `sm_jit_interp.c:182`; mode-4 emits direct `call rt_set_stno@PLT` and bypasses it. Fix: `rt_set_stno()` now also calls `comm_stno((int)stno)`. Observable: error in `x=1; ITEM(.x,1)=5` now prints `statement 2` instead of `statement 0`. Gates unchanged from baseline (error-reporting fix only, no test went PASS→FAIL or FAIL→PASS).

**Live diagnostics for next session** (not yet fixed — two independent issues, each prototyped and reverted this session):

1. **1016_eval EVAL segfault.** Mode-4 emits `SM_PUSH_EXPRESSION entry, 0` where `entry` is a label index. The macro stores this as `d.i` with `d.slen=0`. `EXPVAL_fn` (eval_code.c:401) then falls into the `slen==0` branch and calls `eval_node((tree_t*)expr_d.ptr)` — `.ptr` is the integer label, not a tree pointer → segfault at addr 0x2 / 0x1c / 0x31. Two fix options:
   - **(A)** Emit thunks as RIP-relative function pointers. Requires new `rt_push_expression_fnptr(void*)` + new `EXPVAL_fn` branch (`slen==2` → call fnptr) + emitter macro change to `lea rdi,[rip+.L\entry]`. **ABI subtlety:** thunks have no C prologue (no `push rbp`); they execute body then `ret`. Their internal `call`s see whatever rsp the caller set. So at the call-site for the thunk, rsp must already be 16-aligned MINUS 8 (so that the call's return-push lands at 16-aligned, which is what thunk's internal `call`s require). Use a naked asm wrapper: `pushq rbp; mov rsp,rbp; and -16,rsp; sub 8,rsp; call *rdi; mov rbp,rsp; pop rbp; ret`. Working scaffolding for (A) was prototyped this session and reverted only because issue (2) needs solving first to avoid a beauty regression.
   - **(B)** Pre-emit thunks as proper C-callable functions with prologue/epilogue. Smaller alignment surface but changes the `RETURN` macro semantics — thunks would need `push rbp; mov rbp,rsp` prologue and a `pop rbp; ret` epilogue. Affects any code path that already assumes thunks are bare-ret labels.

2. **`_usercall_hook` regression in mode-4.** Tried installing `_usercall_hook` (interp_hooks.c) as `g_user_call_hook` from `rt_init()` to fix **1114_item** ITEM_SET routing. ITEM_SET passes; **but regresses beauty subsystems 15/17 → 13/17** (omega_driver and semantic_driver segfault). Root cause: `_usercall_hook` (interp_hooks.c:60) checks `g_current_sm_prog` to dispatch user-defined functions; mode-4 has `g_current_sm_prog == NULL`, so it falls through to `call_user_function()` (interp_call.c:68) which does `NO_AST_WALK_GUARD` and AST-walks — but mode-4 has no AST. Need to insert `chunk_reg_lookup`+`call_native_chunk` fallback ahead of `call_user_function` for the mode-4 case. **Blocker:** `chunk_reg_lookup` is `static` in rt.c. Expose it (e.g. `rt_chunk_lookup`, also `rt_call_native_chunk`) or move the hook dispatch into rt.c. Once exposed, the hook fix unblocks 1114_item (+1) without regressing beauty.

**Strategy for next session:** address (2) first by exposing `rt_chunk_lookup` from rt.c, fix `_usercall_hook` to use it when `g_current_sm_prog==NULL`. That alone gives +1 (1114_item) cleanly. Then tackle (1) for 1016_eval — expected +1 to +2. Combined +2 to +3 toward target ≥250.
