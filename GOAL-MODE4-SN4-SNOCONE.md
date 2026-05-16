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

## Baselines (one4all `937cd31c`, 2026-05-15)

| Suite | Script | Mode-4 now | Target |
|---|---|---|---|
| smoke_snobol4 | `test_smoke_snobol4.sh` | 7/7 ✅ | 7/7 |
| beauty subsystems mode-4 | `test_gate_em_beauty_subsystems_mode4.sh` | 15/17 | 17/17 |
| crosscheck_snobol4 | `test_crosscheck_snobol4.sh` | 6/6 ✅ | 6/6 |
| crosscheck_snocone | `test_crosscheck_snocone.sh` | 8/8 ✅ | 8/8 |
| gate_em8_snocone | `test_gate_em8_snocone_jit_emit.sh` | 5/5 ✅ | 5/5 |
| broad corpus SNOBOL4 | `test_mode4_broad_corpus_snobol4.sh` | 245/280 | ≥250 |
| beauty self-host | `test_gate_sn7_beauty_self_host.sh` | — | PASS |

---

## Steps

(M4SN-0 through M4SN-3 ✅ completed. M4SN-4a ✅ completed: `test_mode4_broad_corpus_snobol4.sh` exists in `scripts/`. Currently active: **M4SN-4b**.)

### M4SN-4 — Broad corpus SNOBOL4: sm-run parity in mode-4

- [ ] **M4SN-4b** — Run and triage failures by category. Fix mode-4-specific failures only. Current: 245/280 (target ≥250). Sess 2026-05-15i closed numeric-coercion bug family: `2 ** 3` (int^int) now returns INTVAL for SNOBOL4 via `shared_arith` + `rt_exp`; `5 + ''` (null arith coerce) now returns INTVAL via fixed `SM_COERCE_NUM`/`rt_coerce_num`/`h_coerce_num` (scan string for `.eEdD` instead of fragile `iv != 0 || v.s[0] == '0'` heuristic). Net +3: `027_arith_exponent`, `410_arith_int`, `literals`. Sess 2026-05-15h closed 1016_eval EVAL fnptr scheme. Next candidates: ARG()/LOCAL() family (`1017_arg_local`), DIFFER+error-continuation (`911_datatype`), or the deferred-call-capture family (`expr_eval`, `140`, `141`).
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

**HEAD** one4all `937cd31c` · Baselines: smoke 7/7 ✅, crosscheck_sn4 6/6 ✅, crosscheck_sc 8/8 ✅, gate_em8 5/5 ✅, beauty 15/17, mode-4 broad corpus **245/280**.

Sess 2026-05-15i (Claude Opus 4.7): M4SN-4b — **027_arith_exponent + 410_arith_int + literals PASS** (`+3`, 242→245/280). Two numeric-coercion bugs fixed; both also restored sm-run correctness (the bugs were upstream of mode-4, but mode-4 inherited them).

Changes:

1. **`src/runtime/snobol4/coerce.c` `shared_arith` SM_EXP** (line 45-53): integer^non-negative-integer was returning REAL for SNOBOL4. Old gating `g_icn_jcon ? INTVAL : REALVAL` only returned INT under Icon-JCON dialect; SNOBOL4 fell into REAL. SPITBOL oracle: `2 ** 8 = 256` (integer, no dot). The corresponding mode-1 path in `interp_eval.c:2973` already uses `g_lang != 1 && ...` (1 = LANG_ICN) — copied that gate plus the JCON exception: `(g_lang != 1 || g_icn_jcon) ? INTVAL(res) : REALVAL((double)res)`. Plain Icon stays real (correct per `rung26_pow_int_pow.expected = 1024.0`); JCON-Icon stays integer; SNOBOL4 now correctly integer. Also fixed the negative-exponent fallback from `INTVAL((int64_t)pow(...))` to `REALVAL(pow(...))` — `2**-1` should be `0.5`, not truncated `0`.

2. **`src/runtime/rt/rt.c` `rt_exp`** (line 718-735): mode-4 emitter calls `rt_exp` for SM_EXP, but `rt_exp` always returned REAL and didn't coerce strings/nulls. Rewrote it to mirror `rt_arith`'s shape: pop, DT_FAIL check, DT_S→INTVAL(to_int), DT_SNUL→INTVAL(0), then delegate to `shared_arith(l, r, SM_EXP)`. Required new include `#include "../../include/sm_prog.h"` for `SM_EXP` enum visibility.

3. **`src/processor/sm_interp.c` `SM_COERCE_NUM`** (line 448-462): old code coerced empty string `""` to REAL 0.0 because `to_int("")==0` and `v.s[0]=='\0'` (not `'0'`), so it fell into the `else` REAL branch. Correct SPITBOL semantics: any string lacking `.`/`e`/`E`/`d`/`D` is integer; only then is it real. Rewrote: scan string for those chars; if present → REALVAL(to_real); else → INTVAL(to_int). Also handles DT_SNUL identically. This unblocks `5 + ''` returning `5` (int) rather than `5.` (real). Fixed `410/009` (`null addend is zero`) and `literals` test as side-effect.

4. **`src/runtime/rt/rt.c` `rt_coerce_num`** (line 672-690): same fix as (3) for mode-4 path.

5. **`src/processor/sm_jit_interp.c` `h_coerce_num`** (line 460-475): same fix for mode-3 (JIT) path. Maintains three-mode parity.

**Verified passing in both sm-run and mode-4:**
- `027_arith_exponent`: `OUTPUT = 2 ** 8` → `256` (was `256.`)
- `410_arith_int`: full 9/9 assertions including `2**3=8`, `'1'+'0'=1`, `5+''=5`
- `412_arith_real`: still 6/6 (no regression on the real path)
- `literals` test: now also passes (string-arith coercion in test body)

Gates: smoke_sn4 7/7 ✅, crosscheck_sn4 6/6 ✅, crosscheck_sc 8/8 ✅, gate_em8 5/5 ✅, smoke_snocone 5/5 ✅, smoke_rebus 4/4 ✅, beauty_mode4 15/17 unchanged (ShiftReduce_driver/counter_driver still diff, pre-existing), broad corpus **242→245**/280. Icon smoke 3/5, Prolog smoke 0/5 — both unchanged from pre-session baseline (verified via `git stash` before-and-after run); my coerce.c change uses `g_lang != LANG_ICN` so Icon's real-result semantics are preserved.

**Live diagnostics for next session** (not yet fixed, carried from prior watermark):

1. **expr_eval, 140_pat_eval_double_fn_trick, 141_pat_eval_double_fn_arbno**: `*Fn(args)` deferred-call captures inside patterns. 140/141 fail in `--ir-run` too — root cause is deeper than mode-4; SL-13c fix in `eval_code.c` may need a similar pass over `bb_callcap_emit_binary` / `XCALLCAP` BB native emission. Different mechanism from PUSH_EXPRESSION (the 1016_eval fix).

2. **910/1011_func_redefine class**: mid-recursion DEFINE redefinition. ir-run passes (3/3) but sm-run fails at assertion 003 — `myfunc` is being called recursively while being redefined, and the SM call frame doesn't reload the new binding. Mode-3/4 inherits the sm-run bug.

3. **Custom DATA type drivers (ShiftReduce_driver, Gen_driver, Qize_driver, TDump_driver, ReadWrite_driver, counter_driver, stack_driver, test_stack)**: user-defined `DATA('Node(t,v,c,n)')` types with field accessors. All pass in ir-run; all fail in sm-run. Not mode-4-specific.

4. **word1/word2/word3/word4, cross**: complex driver programs using `STAR` patterns and runtime-built grammars. Fail in ir-run too — frontend/lower issue, not mode-4.

**Strategy for next session:** the +3 win shows that "fix the upstream sm-run bug, mode-4 inherits the fix for free" is a viable path. Eight failures (`027`, `410`, `911`, `literals`, `1017_arg_local`, `139_pat_calc_paren_deep`, `114_pat_fence_via_var_in_paren_alt`, ...) used to be the same numeric-coercion bug class — that vein is exhausted, but other classes (DATA-type accessors, ARG()/LOCAL(), redefine-mid-recursion) each offer 1-3 tests if patched. Pick by tractability: ARG()/LOCAL() and 911 (DATATYPE+DIFFER+error-continuation) look smaller than the DATA-type or redefine-recursion problems. Target ≥250 still in reach with two more sessions.
