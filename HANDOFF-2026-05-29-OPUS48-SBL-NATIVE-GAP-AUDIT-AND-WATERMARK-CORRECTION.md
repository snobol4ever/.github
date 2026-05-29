# HANDOFF — SBL native-gap audit + watermark correction (analysis only, no code commit)

**Goal:** GOAL-SNOBOL4-BB.md
**Author:** Claude Opus 4.8 · 2026-05-29
**HEAD measured:** one4all `b408b086`
**Type:** Investigation / diagnosis. NO source changed, NO commit. Hand-off trigger not given; this file documents verified findings for the next session.

---

## TL;DR

1. The GOAL watermark's claim that **the Raku sibling commit `30e7c0a1` regressed SNOBOL4 mode-2 252→223 via shared `bb_exec.c`/coerce is WRONG.** Bisection proves the Raku commit did not regress SNOBOL4 (its `bb_exec.c` change is `BB_LANG_RKU`-gated; its parent already scored 223). Please correct the watermark.

2. The corpus harness `test_interp_broad_corpus_and_beauty.sh` runs **bare `scrip file.sno`, which is mode-3 NATIVE by default** (`scrip.c:135-136` → `mode_run=1`; `--run` is the documented default). It is NOT mode-2. That is why the "mode-2" and "native" failure sets are byte-identical — they are the same execution path.

3. The real 252→243 story: commit **`0f4fcfde` ("Remove all mode fallback paths")** removed the `mode_run`→`sm_interp_run` fallback per Lon's no-fallback directive. That **honestly exposed 9 native-arm gaps** previously masked by the interpreter fallback. This is the no-fallback rule working as intended, NOT a regression to "recover" by restoring fallback (doing so would violate RULES.md MODE PURITY).

4. The "fence/capture regression" (061/063/064/065/Qize_driver/test_string) is a **mirage**: those pass under native already. They only fail explicit brokered `--interp`, which is a different engine and not the default harness path. Caused by `0e926c16` but irrelevant to the default-harness score.

---

## Three execution paths (the source of all prior confusion)

| Path | Engine | Today's corpus score | Notes |
|------|--------|----------------------|-------|
| bare `scrip f.sno` (default = `mode_run`) | **native** (`sm_run_native`) | **243/280** | the harness's actual path |
| `mode_run` + wired-BB + `sm_interp_run` fallback | interp | (was 252) | **removed** by `0f4fcfde` per no-fallback directive |
| `scrip --interp f.sno` | brokered-BB + `sm_interp_run` | 246/280 | different engine; NOT the default |

The "252" baseline (`baf8397d`) was path #2, which no longer exists. It is not recoverable without re-introducing a forbidden fallback.

---

## Verification trail (all via per-commit worktree builds, today's corpus)

- `baf8397d` default(path#2) = 252; the 9 below all PASS there.
- 9-test bisect over `baf8397d..94bbd9eb`: clean at `855cbee2`, broken at **`0f4fcfde`** (the no-fallback commit). Endpoints 9/0 → 0/9.
- Raku commit `30e7c0a1` `bb_exec.c` diff = BB_SEQ gather driver, **gated `g_current_cfg->lang == BB_LANG_RKU`** → cannot touch SNOBOL4. Its `sm_interp.c` change is `SM_ACOMP`/`SM_LCOMP` (numeric/string compare), unrelated to these failures.
- True `--interp` (path #3) = 246. Diff vs native(243): native LOSES 9 (below), WINS 6 (061/063/064/065/Qize_driver/test_string). 246 − 9 + 6 = 243. ✓

---

## The 9 addressable native gaps (pass oracle, fail native) — the real work

Reproduce any: `SNO_LIB=corpus/programs/snobol4/demo/inc ./scrip <file>` (native) vs `./scrip --interp <file>` (passes).

### Cluster A — native user-function call/return machinery (7 tests, DOMINANT)
SM-native function/return, not BB pattern templates. Likely in `sm_native.c` / `SM_templates` (CALL/RETURN/NRETURN/local-frame/DATA-accessor emission).
- `1010_func_recursion`  — **SIGSEGV** (recursion frame).
- `1016_eval`            — **SIGSEGV** (EVAL of code string).
- `213_indirect_name`    — wrong-output; only assertion 5 fails = **NRETURN returning a NAME (`.A`) then read-deref**. Assertions 1-4 ($X indirect, $NM deref, $X lvalue, $.A literal) PASS natively.
- `1013_func_nreturn`    — wrong-output (NRETURN).
- `1011_func_redefine`   — wrong-output (function redefinition).
- `1017_arg_local`       — wrong-output (local/arg binding).
- `094_data_define_access` — wrong-output: `DATA('complex(real,imag)')` then `real(X)`/`imag(X)`; native emits only ONE field line (expected `3` then `-2`, native prints just `-2`). Auto-generated DATA field-accessor codegen.

NRETURN appears in both 213#5 and 1013 → **start there**; it is the smallest reproducer (213 isolates exactly one failing assertion).

### Cluster B — BREAKX flat-wiring + BINARY arm (2 tests) = the pending SBL-BREAKX-2 rung
- `W05_breakx` — **abort**: `bb_emit_end: unresolved forward reference site=19 label=''`.
- `word4`      — **abort**: `bb_emit_end: unresolved forward reference site=23 label='pat_brok_β'`.

Root: BREAKX lowers to `BB_PAT_BREAK` with `ival=1`, `β=bb` (self-loop) (`lower_pat_dcg.c:64`). In `bb_pat_break.cpp`:
- plain-BREAK MEDIUM_BINARY arm is COMPLETE (lines 92-126).
- **BREAKX MEDIUM_BINARY arm is a 2-jump stub** (lines 90-91, sites `{1,2}`) — α-port jmps straight to ω (always fails). The stub's second site is also mis-numbered (says 2, the rel32 begins at byte 6).
- BREAKX TEXT arm (lines 164-195) is fully implemented and is the spec to mirror, BUT it uses TWO `.data` slots (z, z_orig); the BINARY form has only the single `g_emit.bb_cs_zeta` `delta@+8` slot. Need a second persistent int (deque-int slot per `bb_capture.cpp` pattern) OR derive z_orig from `[r10]` as plain-BREAK does.
- The `site=…label=''`/`pat_brok_β` aborts indicate the **β-self-loop flat-wiring** (β=bb) leaves a label unresolved BEFORE bytes matter. Fix wiring first, then the BINARY β-rescan bytes.

SBL-BREAKX-2 is therefore genuinely two-part (wiring + bytes); budget a full session and verify with `objdump`-level byte checks.

### Cluster C — beauty drivers (3 tests, derivative)
- `assign_driver`, `fence_driver`, `match_driver` — wrong-output. Almost certainly fall out once Cluster A (user-function/return) lands, since the beauty library is function-heavy. Re-measure after A.

---

## Recommended next rung

**SBL-NATIVE-FN-1 (NRETURN read-deref) — LANDED this session ✅.** 4-line fix in `rt_call` (rt.c:~1555): the `INVOKE_fn` fallthrough now derefs NRETURN results (guarded `kw_rtntype=="NRETURN"` + `IS_NAMEPTR/IS_NAMEVAL`), mirroring the `if(cfn)` branch. Native 243→245 (+213_indirect_name, +assign_driver); --interp 246 unchanged; smoke 13/13; FACT 0; audit OK; zero regressions.

**SBL-NATIVE-FN-2 (NRETURN as lvalue) — NEXT, already isolated.** `1013_func_nreturn` now passes assertion 1 but fails assertion 2: *assigning through* an NRETURN function result (`fn() = val`) — the returned NAME must be used as an lvalue, not read-deref'd. Distinct from FN-1 (read side). Then the SEGV pair (`1010_func_recursion`, `1016_eval` — native recursion frame / EVAL dispatch), `1011_func_redefine`, `1017_arg_local`, `094_data_define_access` (DATA field-accessor codegen), and finally Cluster B SBL-BREAKX-2 (wiring + BINARY arm).

## Watermark edits requested
- Strike the "SIBLING Raku commit … regressed 252→223 via shared bb_exec.c/coerce" sentence in the GATE-4/NATIVE lines.
- Replace with: "Default harness path is mode-3 native (no fallback since `0f4fcfde`). 243/280 = honest native; 9 oracle-passing programs lack complete native arms (Cluster A native user-functions ×7, Cluster B BREAKX wiring+arm ×2, +3 derivative drivers). True `--interp` = 246. See HANDOFF-2026-05-29-OPUS48-SBL-NATIVE-GAP-AUDIT."

## Gate state at audit (unchanged — no code touched)
```
HEAD one4all        = b408b086
GATE-1 smoke        = 13/13
native broad        = 243/280
true --interp broad = 246/280
FACT RULE           = 0
audit_m3_native     = GATE OK
```
