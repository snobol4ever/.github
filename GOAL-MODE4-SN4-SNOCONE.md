# GOAL-MODE4-SN4-SNOCONE.md — Mode-4 x86 Full Test Suite: SNOBOL4 + Snocone

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ NO AST WALKING IN MODES 2/3/4 — see RULES.md § "NO AST WALKING IN MODES 2, 3, OR 4"         ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  Sess 2026-05-15g removed all tree_t* dereferences from sm_interp.c (mode 2) and                ║
║  sm_jit_interp.c (mode 3). Stubs print [NO-AST] <opcode> on stderr.                              ║
║                                                                                                  ║
║  If a gate breaks with [NO-AST] FOO — write fresh SM/BB lowering for FOO.                       ║
║  Do NOT restore the AST-walking call.  Do NOT route through proc_table_call or any              ║
║  other back-door that hands a tree_t* to mode-2/3/4 code.                                       ║
║                                                                                                  ║
║  Mode 1 (`--ir-run` standalone AST interp) is unchanged and remains the reference path.        ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝


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

## Baselines (one4all `5edb6b1e`, 2026-05-15)

| Suite | Script | Mode-4 now | Target |
|---|---|---|---|
| smoke_snobol4 | `test_smoke_snobol4.sh` | 7/7 ✅ | 7/7 |
| beauty subsystems mode-4 | `test_gate_em_beauty_subsystems_mode4.sh` | 15/17 | 17/17 |
| crosscheck_snobol4 | `test_crosscheck_snobol4.sh` | 6/6 ✅ | 6/6 |
| crosscheck_snocone | `test_crosscheck_snocone.sh` | 8/8 ✅ | 8/8 |
| gate_em8_snocone | `test_gate_em8_snocone_jit_emit.sh` | 5/5 ✅ | 5/5 |
| broad corpus SNOBOL4 | `test_mode4_broad_corpus_snobol4.sh` | 241/280 | ≥250 |
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

**HEAD** one4all `5edb6b1e` · Baselines: smoke 7/7 ✅, crosscheck_sn4 6/6 ✅, crosscheck_sc 8/8 ✅, gate_em8 5/5 ✅, beauty 15/17, mode-4 broad corpus **241/280**.

Sess 2026-05-15f (Claude Opus 4.7): M4SN-4b — **1114_item PASS** (`+1`, 240→241/280). Root cause: `rt_call()` in `src/runtime/rt/rt.c` had branches for `"IDX_SET"` but not `"ITEM_SET"`. The lowerer (`lower.c:461`) emits `SM_CALL_FN "ITEM_SET"` for `ITEM(arr,idx) = val`, not `"IDX_SET"`. In mode-4, that became `call rt_call@PLT` with name=`"ITEM_SET"`, fell past the existing branches to `INVOKE_fn("ITEM_SET",...)` which has no registered handler → `Error 5: Undefined function or operation`. Fix: added `"ITEM_SET"` branch mirroring `"IDX_SET"` (nargs==3 → `subscript_set`; nargs>=4 → `subscript_set2`). Also widened the existing `"IDX_SET"` branch's `nargs == 4` → `nargs >= 4` for the 4D-bracket case (`ama<2,1,2,1> = 2121`). The runtime only has 1D/2D subscript primitives; multi-dim writes degenerate to first-two-indices, matching `_usercall_hook` (interp_hooks.c:38-39) and `_ITEM_` builtin (snobol4.c) — same semantics sm-run uses.

**Previous-session watermark note about exposing `rt_chunk_lookup` for `_usercall_hook` was a misdiagnosis** — `_usercall_hook` (interp_hooks.c) is never installed in mode-4. `rt_init()` sets `g_user_call_hook = _rt_usercall` (rt.c:323). The actual gap was the missing `"ITEM_SET"` arm in `rt_call`'s big strcmp ladder. Fix lives in rt.c.

Gates: smoke 7/7 ✅, beauty 15/17 unchanged (ShiftReduce_driver/counter_driver still diff, pre-existing), crosscheck_sn4 6/6 ✅, crosscheck_sc 8/8 ✅, gate_em8 5/5 ✅, broad corpus **240→241**/280. Zero regressions.

**Live diagnostics for next session** (not yet fixed):

1. **1016_eval EVAL segfault.** Unchanged from prior watermark. Mode-4 emits `PUSH_EXPRESSION entry, 0` where `entry` is an integer label index → stored as `d.i` with `d.slen=0` → `EXPVAL_fn` falls into `slen==0` branch and calls `eval_node((tree_t*)expr_d.ptr)` → segfault. Plan (option A — fnptr scheme): (a) change `sm_macros.s`'s PUSH_EXPRESSION macro from `movabs rdi, \entry` to `lea rdi, [rip + \entry]`; (b) change `emit_sm_push_expression()` in `src/emitter/emit_sm.c:337` to emit the lea form (currently calls `emit_seq_movabs_rdi`); (c) add new `slen==2` branch to `EXPVAL_fn` (`src/runtime/snobol4/eval_code.c:401`) that invokes the fnptr; (d) the thunk bodies emitted in mode-4 lack a C prologue (no `push rbp`) so their inner `call rt_*@PLT` will misalign rsp — wrap the call through a small inline-asm trampoline in eval_code.c that does `push rbp; mov rbp,rsp; and rsp,-16; call *fn; mov rsp,rbp; pop rbp` before invoking. Expected +1 to +2 (1016_eval and probably one or two related EVAL/CODE tests).

2. **`_usercall_hook` mode-4 routing.** Previously believed needed for 1114_item — actually NOT NEEDED. `_usercall_hook` is only installed in the interp/sm code paths; mode-4 uses `_rt_usercall` set in `rt_init()`. The 1114_item failure was unrelated. Strike this from the active diagnostic list. If a future bug DOES require `rt_chunk_lookup` to be public, the exposure work is still valid plumbing, but no test currently demands it.

**Strategy for next session:** tackle (1) only. Expected gain: +1 to +2. Combined with this session's +1, that brings broad corpus into the 242–243 zone, still 7-8 below the ≥250 target — additional triage work needed on the remaining 34 fails after that.
