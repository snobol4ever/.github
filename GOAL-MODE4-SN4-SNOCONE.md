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
║  Mode 1 (`--interp` standalone AST interp) is unchanged and remains the reference path.        ║
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
**Done when:** every SNOBOL4 and Snocone test that passes under `--interp` also passes under `--compile` (linked binary via libscrip_rt.so). Zero regressions vs the `--interp` baseline.

**Mode-4 pipeline recap:** `scrip --compile file.sno` → `.s` → `gcc -c` → `gcc link -lscrip_rt` → ELF binary → run. All test harness scripts use this pipeline with the working dir set to `/home/claude/one4all` (for macro includes).

---

## Baselines (one4all `1ef85cdc`, 2026-05-15)

| Suite | Script | Mode-4 now | Target |
|---|---|---|---|
| smoke_snobol4 | `test_smoke_snobol4.sh` | 7/7 ✅ | 7/7 |
| beauty subsystems mode-4 | `test_gate_em_beauty_subsystems_mode4.sh` | 15/17 | 17/17 |
| crosscheck_snobol4 | `test_crosscheck_snobol4.sh` | 6/6 ✅ | 6/6 |
| crosscheck_snocone | `test_crosscheck_snocone.sh` | 8/8 ✅ | 8/8 |
| gate_em8_snocone | `test_gate_em8_snocone_jit_emit.sh` | 5/5 ✅ | 5/5 |
| broad corpus SNOBOL4 | `test_mode4_broad_corpus_snobol4.sh` | **250/280 ✅** | ≥250 |
| beauty self-host | `test_gate_sn7_beauty_self_host.sh` | — | PASS |

---

## Steps

(M4SN-0 through M4SN-3 ✅ completed. M4SN-4a ✅ completed. M4SN-4b ✅ completed sess 2026-05-15i: **250/280 ✅ target ≥250 HIT**. Currently active: **M4SN-4c**.)

### M4SN-4 — Broad corpus SNOBOL4: --interp parity in mode-4

- [x] **M4SN-4b** — Run and triage failures by category. Fix mode-4-specific failures only. **TARGET ≥250 HIT.** Final: **250/280** (was 242). Sess 2026-05-15i closed three bug classes: (a) numeric coercion (+3): `shared_arith` SM_EXP int^int → INTVAL for SNOBOL4 via fixed `g_lang != LANG_ICN || g_icn_jcon` gate, `rt_exp` rewritten to delegate to `shared_arith`, and `SM_COERCE_NUM`/`rt_coerce_num`/`h_coerce_num` (three-mode parity) now scan for `.eEdD` instead of fragile `iv != 0 || v.s[0] == '0'` heuristic. (b) REM box binary emission (+5): `emit_bb_xstar` had asm only inside `if (IS_TEXT)`; binary mode emitted nothing. Added `insn_mov_rcx_i64(TEMPLATE_ADDR_SIGLEN); insn_mov_eax_rcxmem(); emit_store_delta(); emit_jmp(s); β: emit_jmp(f);` fallthrough mirroring XLNTH/XTB. Fixed tests: `027`, `410`, `literals`, `048`, `060`, `Qize_driver`, `test_stack`, `word4`. Sess 2026-05-15h closed 1016_eval EVAL fnptr scheme.
- [x] **M4SN-4c** — ✅ **COMPLETE. Target already exceeded.** Mode-4 broad corpus 250/280 (89.3%) already ≥ --interp 223/280 (79.6%). Sess 2026-05-16 triage: 25 failures are cross-mode or pre-existing infrastructure bugs, not mode-4-specific. (a) cursor-capture bug (@var) is cross-mode (--interp+--interp+mode-4 all fail). (b) DATA-type accessors SEGFAULT in --interp (pre-existing mode-2 infrastructure violation of RULES.md NO-AST). (c) `emit_bb_xatp` has no binary-mode gap. Defer cross-mode issues to future sessions. No mode-4-specific gaps identified.

### M4SN-5 — Full regression: test_regression_full_corpus.sh MODE=x64 with libscrip_rt pipeline

The existing `test_regression_full_corpus.sh MODE=x64` uses the old mock-include pipeline (13/430). Rewrite or add a new script using the libscrip_rt.so pipeline.

- [ ] **M4SN-5a** — Write `test_mode4_full_regression.sh`: iterate all crosscheck .sno files, emit→link→run via libscrip_rt.so, compare vs .ref. Report PASS/FAIL/SKIP.
- [ ] **M4SN-5b** — Run and establish true mode-4 baseline count.
- [ ] **M4SN-5c** — Fix mode-4-specific failures. Target: PASS count ≥ --interp PASS count on same corpus.

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
  /home/claude/one4all/scrip --compile "$sno" > "$tmp/p.s" 2>/dev/null || { rm -rf "$tmp"; return 1; }
  (cd /home/claude/one4all && gcc -c "$tmp/p.s" -o "$tmp/p.o" 2>/dev/null) || { rm -rf "$tmp"; return 1; }
  gcc "$tmp/p.o" -L/home/claude/one4all/out -lscrip_rt -lgc -lm \
      -Wl,-rpath,/home/claude/one4all/out -o "$out" 2>/dev/null || { rm -rf "$tmp"; return 1; }
  rm -rf "$tmp"
}
```

---

## Watermark

**HEAD** one4all `00731350` (Prolog session HQ) · Baselines: smoke 7/7 ✅, crosscheck_sn4 6/6 ✅, crosscheck_sc 8/8 ✅, gate_em8 5/5 ✅, beauty 15/17, mode-4 broad corpus **250/280 (89.3%) vs --interp 223/280 (79.6%) ✅ M4SN-4c complete**.

Sess 2026-05-15i (Claude Opus 4.7): M4SN-4b two-iteration push — **+8 total (242 → 250/280), zero regressions, ≥250 target met.** Three bug classes closed.

### Iteration 1 — numeric-coercion family (+3, one4all `937cd31c`)

Tests fixed: `027_arith_exponent`, `410_arith_int`, `literals`.

Changes:

1. **`src/runtime/snobol4/coerce.c` `shared_arith` SM_EXP**: integer^non-negative-integer returned REAL for SNOBOL4. Old gating `g_icn_jcon ? INTVAL : REALVAL` only returned int under Icon-JCON dialect. SPITBOL oracle: `2 ** 8 = 256` (integer, no dot). The mode-1 path in `interp_eval.c:2973` already uses `g_lang != 1 && ...` (1 = LANG_ICN) — copied that gate plus the JCON exception: `(g_lang != 1 || g_icn_jcon) ? INTVAL(res) : REALVAL((double)res)`. Plain Icon stays real (correct per `rung26_pow_int_pow.expected = 1024.0`); JCON-Icon stays integer; SNOBOL4 now correctly integer. Also fixed the negative-exponent fallback from `INTVAL((int64_t)pow(...))` to `REALVAL(pow(...))` — `2**-1` should be `0.5`, not truncated `0`.

2. **`src/runtime/rt/rt.c` `rt_exp`**: mode-4 emitter calls `rt_exp` for SM_EXP, but `rt_exp` always returned REAL and didn't coerce strings/nulls. Rewrote it to mirror `rt_arith`'s shape: pop, DT_FAIL check, DT_S→INTVAL(to_int), DT_SNUL→INTVAL(0), then delegate to `shared_arith(l, r, SM_EXP)`. Required new include `#include "../../include/sm_prog.h"` for `SM_EXP` enum visibility.

3. **`src/processor/sm_interp.c` `SM_COERCE_NUM`**: old code coerced empty string `""` to REAL 0.0 because `to_int("")==0` and `v.s[0]=='\0'` (not `'0'`), so it fell into the `else` REAL branch. Correct SPITBOL semantics: any string lacking `.`/`e`/`E`/`d`/`D` is integer; only then is it real. Rewrote: scan string for those chars; if present → REALVAL(to_real); else → INTVAL(to_int). Also handles DT_SNUL identically. This unblocks `5 + ''` returning `5` (int) rather than `5.` (real).

4. **`src/runtime/rt/rt.c` `rt_coerce_num`**: same fix as (3) for mode-4 path.

5. **`src/processor/sm_jit_interp.c` `h_coerce_num`**: same fix for mode-3 (JIT) path. Maintains three-mode parity.

### Iteration 2 — REM box binary-mode emission (+5, one4all `1ef85cdc`)

Tests fixed: `048_pat_rem`, `060_capture_multiple`, `Qize_driver`, `test_stack`, `word4`.

**Root cause:** `emit_bb_xstar` (the REM/XSTAR box) emitted asm only inside its `if (IS_TEXT)` branch. The binary-mode (EMIT_BINARY_WIRED / EMIT_BINARY_BROKERED) path was completely empty — no Δ update, no jumps, no β label. So brokered-mode REM compiled to a no-op: the BB prologue + α/β dispatch + immediately fell through to the `lbl_succ` tail without setting `Δ = Σlen`. Any capture wrapping REM (e.g. `X REM . V`) then saw `cap_start == Δ` and produced a zero-length span.

**Fix in `src/emitter/emit_bb.c` `emit_bb_xstar`:** after the `IS_TEXT` block, add the binary-mode body using existing helpers, parallel to text:

```c
insn_mov_rcx_i64(TEMPLATE_ADDR_SIGLEN);   /* rcx = &Σlen */
insn_mov_eax_rcxmem();                     /* eax = *rcx (= Σlen value) */
emit_store_delta();                        /* [r10] = eax  (= Δ) */
emit_jmp(s, JMP_JMP);                      /* → succ */
emit_label_define(b);
emit_jmp(f, JMP_JMP);                      /* β → fail */
```

This mirrors what `emit_bb_xlnth` (LEN(n)) and `emit_bb_xtb` (TAB(n)) already do: text emit + return inside `IS_TEXT`, then fall through to binary emit. XSTAR was the only mover-of-Δ that did not have the binary fallthrough.

Mode-4 ELF binaries call into the brokered BB through `libscrip_rt.so`, so the same fix unblocks them too — the asm-text expansion of `EXEC_STMT_VARIANT` ultimately invokes the same brokered XSTAR BB via `rt_match_variant` → `exec_stmt` → `bb_build_brokered`.

**Side effects beyond the five named tests:** `counter_driver`, `ShiftReduce_driver`, `ReadWrite_driver`, `TDump_driver`, `stack_driver` are unblocked at the REM step but still fail later in their DATA-type accessor logic (separate, deeper bug). `word4` now reaches end; `word1/2/3` still fail at a different grammar-driver step.

### Gates after both iterations

smoke_sn4 7/7 ✅, crosscheck_sn4 6/6 ✅, crosscheck_sc 8/8 ✅, gate_em8 5/5 ✅, smoke_snocone 5/5 ✅, smoke_rebus 4/4 ✅, smoke_icon 5/5 ✅ (was 3/5 pre-session — concurrent session improvement pulled in via rebase), beauty_mode4 15/17 unchanged (ShiftReduce_driver/counter_driver still diff, pre-existing — counter and SR fail later in DATA-type logic), **mode-4 broad corpus 242 → 250/280** ✅. Prolog smoke 0/5 unchanged from pre-session baseline.

### Live diagnostics for next session (M4SN-4c) — push 250 → ≥--interp count

Remaining 25 broad-corpus failures fall into clusters; rough tractability ordering:

1. **DATA-type accessor family** (`ShiftReduce_driver`, `Gen_driver`, `TDump_driver`, `ReadWrite_driver`, `counter_driver`, `stack_driver`): all use user-defined `DATA('Node(t,v,c,n)')` with field accessors. Pass in `--interp`, fail in `--interp`. Probably one bug — DATA-record runtime lookup not wired for SM path. Could unblock 6 tests.

2. **`*Fn(args)` deferred-call captures** (`expr_eval`, `140_pat_eval_double_fn_trick`, `141_pat_eval_double_fn_arbno`): per prior watermark, `pat_assign_callcap` / `XCALLCAP` BBs. 140/141 already fail in `--interp` too — deeper than mode-4. SL-13c in `eval_code.c` was a partial fix; XCALLCAP native emission may need similar treatment.

3. **`@var` cursor capture** (`074_pat_star_var_cursor`, `W07_capt_cur`): `@pos` should return current cursor as integer. Both empty in --interp. Probably similar binary-mode emit-gap to the REM bug — worth investigating `emit_bb_xatp` (XATP node) for the same `if (IS_TEXT)` + missing binary fallthrough pattern. Could unblock 2 tests.

4. **FENCE backtracking** (`114_pat_fence_via_var_in_paren_alt`, `124_pat_regex_keyword_seal`): csnobol4 also fails 124 per its comment — known cross-implementation issue.

5. **Recursive-pattern segfault** (`139_pat_calc_paren_deep`, `075_pat_arbno_star_backtrack`): segfault in `--interp` too. Deep pattern-engine.

6. **Test-specific** (`911_datatype` uses lowercase `lcase` not registered; `1017_arg_local` interacts with `sno_fold_on=0` default — would need a policy decision from Lon).

7. **Grammar drivers** (`word1/2/3`, `cross`): fail in `--interp` too — frontend/lower issue.

**Strategy for next session:** check `emit_bb_xatp` first — if it has the same `if (IS_TEXT)` + empty binary case as XSTAR did, that's a quick +2. After that, the DATA-type cluster (6 tests) is the biggest fish. SPITBOL manual `DATA()` semantics: each named DATA type gets generated field-access functions (e.g. `DATA('Node(t,v,c,n)')` creates accessors `t()`, `v()`, `c()`, `n()`). Likely the SM lower path doesn't invoke the generated accessor functions correctly.
