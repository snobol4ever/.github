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
| broad corpus SNOBOL4 | `test_mode4_broad_corpus_snobol4.sh` | 242/280 | ≥250 |
| beauty self-host | `test_gate_sn7_beauty_self_host.sh` | — | PASS |

---

## Steps

(M4SN-0 through M4SN-3 ✅ completed. M4SN-4a ✅ completed: `test_mode4_broad_corpus_snobol4.sh` exists in `scripts/`. Currently active: **M4SN-4b**.)

### M4SN-4 — Broad corpus SNOBOL4: sm-run parity in mode-4

- [ ] **M4SN-4b** — Run and triage failures by category. Fix mode-4-specific failures only. Current: 242/280 (target ≥250). Sess 2026-05-15h closed 1016_eval EVAL fnptr scheme (see Watermark). Next: `*Fn(args)` deferred-call-capture family (`expr_eval`, `140_pat_eval_double_fn_trick`, `141_pat_eval_double_fn_arbno`) — different mechanism (`pat_assign_callcap` / `XCALLCAP` BBs), not PUSH_EXPRESSION.
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

**HEAD** one4all `d30949cb` · Baselines: smoke 7/7 ✅, crosscheck_sn4 6/6 ✅, crosscheck_sc 8/8 ✅, gate_em8 5/5 ✅, beauty 15/17, mode-4 broad corpus **242/280**.

Sess 2026-05-15h (Claude Opus 4.7): M4SN-4b — **1016_eval PASS** (`+1`, 241→242/280). Implemented Option A (fnptr scheme) from prior watermark, with the rsp-alignment refinement noted below.

Changes:
1. `sm_macros.s` `PUSH_EXPRESSION` macro: `movabs rdi, \entry` → `lea rdi, [rip + .L\entry]`, and `mov esi, \arity` → `mov esi, 2` (hardcode the slen=2 fnptr sentinel — arity is unused upstream and the only way DT_E can arrive at EXPVAL_fn under this new shape is via this macro).
2. `src/emitter/emit_sm.c` (`SM_TPL_PUSH_EXPRESSION` macro-definition emit, lines ~745-753): updated to match the new `lea`/hardcoded-`2` shape so mode-4 text output uses the same expansion as the in-place `sm_macros.s`. The args-column emitter (`build_args_col`) was unchanged — the bare integer is still emitted; the `.L` prefix is supplied by the macro template.
3. `src/runtime/rt/rt.c`: exported two new helpers, `int rt_vstack_depth(void)` and `DESCR_t rt_vstack_pop(void)`, used only by the slen==2 dispatch below. The existing module-static `vstack_pop`/`vstack_depth` (which thread through `g_ops->`) are kept private; the new exports trivially wrap them.
4. `src/runtime/snobol4/eval_code.c` `EXPVAL_fn` (line 401): new `slen == 2` branch. Calls the thunk through a small inline-asm trampoline: `mov rsp→rbx ; and rsp,-16 ; sub rsp,8 ; call *fn ; mov rbx→rsp`. The `sub rsp,8` step is required: the thunk does NOT establish a C frame (it's just `PUSH_*`/`CALL_FN`/`RETURN(=ret)`), and its nested `call rt_*@PLT` invocations expect the thunk's entry rsp to be 16-aligned (so the nested callee sees rsp ≡ 8 mod 16 on entry, per System V ABI). Without the `sub rsp,8`, the thunk's nested SSE-using helpers (`snprintf` inside `VARVAL_fn(DT_I)`) crash on `MOVAPS`/`__printf_buffer_init`.

**Important alignment lesson**: an `and rsp,-16` alone is not enough; the thunk acts as a callee that itself does further calls, so it must receive a 16-aligned rsp at entry, which means the trampoline's `call *fn` site must satisfy `(rsp + 8) ≡ 0 mod 16` — i.e. rsp ≡ 8 mod 16 at the `call` instruction. `and -16` puts rsp at 0; the additional `sub rsp,8` moves it to 8. After the call's push of 8 bytes, the thunk sees rsp ≡ 0 mod 16, which is what it needs for its nested ABI-compliant calls.

Verified all three EVAL assertions in 1016_eval (`*('abc' 'def')`, `*q`, `*IDENT(1, 2)` deferral that fails) execute correctly via the fnptr path. Mode-1 (`--ir-run`) and mode-2 (`--sm-run`) untouched and still PASS.

Gates: smoke 7/7 ✅, beauty 15/17 unchanged (ShiftReduce_driver/counter_driver still diff, pre-existing), crosscheck_sn4 6/6 ✅, crosscheck_sc 8/8 ✅, gate_em8 5/5 ✅, broad corpus **241→242**/280. Zero regressions.

**Live diagnostics for next session** (not yet fixed):

1. **expr_eval, 140_pat_eval_double_fn_trick, 141_pat_eval_double_fn_arbno**: these involve `*Fn(args)` deferred-call captures inside patterns, NOT plain `PUSH_EXPRESSION`. 140/141 do not emit any `PUSH_EXPRESSION` instructions — they go through `pat_assign_callcap` / `bb_callcap_emit_binary` (cf. SL-13c in GOAL-SNOCONE-SM-LOWER) — different mechanism, different fix. `expr_eval` still segfaults under mode-4 even after this session's fix; it heavily uses `*Push()` deferred calls inside patterns plus EVAL, so likely the same `pat_callcap` family bug. Triage these together next session.

2. (Closed) `_usercall_hook` mode-4 routing — was a misdiagnosis in prior watermarks; struck.

**Strategy for next session:** investigate the `*Fn(args)` deferred-call-capture path under mode-4. The SL-13c fix in `eval_code.c` (`TT_CAPT_COND_ASGN`/`TT_CAPT_IMMED_ASGN` → `pat_assign_callcap`) and the `bb_flat.c` `flat_is_eligible` XCALLCAP exclusion both already exist; the mode-4 specific issue may be in how `XCALLCAP` BBs are emitted as native code vs. SM. Expected gain: +3 to +5 (`expr_eval`, `140_pat_eval_double_fn_trick`, `141_pat_eval_double_fn_arbno`, and probably one or two of the `word*` / `cross` failures that exercise similar mechanisms).
