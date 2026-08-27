# FINDING 2026-08-27 seat11 — UNLOAD'S ERROR-022 ROUTING IS ROOT-CAUSED AND FIXED (VERIFIED, NOT LANDED); TWO INDEPENDENT BLOCKERS STOP THE ROW, NEITHER FIXABLE WITH MORE SCRIP RUNTIME CODE

**Row:** `conform-unload-noop` (postoffice task, rank 1). **Tree:** SCRIP `fa9baa8f` pristine `-O0`. Oracle `/home/resources/x64/bin/sbl -bf`.

## SUMMARY

Picked up this row via THE LOOP (FLEET-12, seat09-12 active, lane `07-12→hq_P`). Root-caused and fixed the actual defect the row is about (UNLOAD doesn't make a call raise ERROR 022). The fix is verified correct and regression-clean **except** that it unmasks a pre-existing, unrelated OPSYN defect as a loud crash instead of a silent wrong answer — landing it as-is would flip `test_corpus_snobol4.sh`'s blocking mode-4 gate from 365/365 to 364/365. Held back, **not committed**. Separately, the row's own DONE-WHEN cannot mechanically pass regardless, for a structural reason unrelated to any of this. Routed both to hq_C (`q-unload-donewhen-shape-and-opsyn-block`).

## PART 1 — SEAT14'S ROUTED QUESTION IS MOOT ON THIS TREE (measured, not assumed)

seat14 (2026-08-27, earlier this same day) fixed UNLOAD's registration-removal (SCRIP `97949fb0`→`60f69f3e`) but found mode-3 still diverged from mode-4 and routed a question about whether a call-site cache bypasses re-validation. Before trusting that framing, re-ran the repro fresh on a newly-pulled tree: **mode-3 and mode-4 now agree** (`10` then `unreachable`, matching hq_P's later 18:05Z receipt). ASM-DIFF-FIRST on the emitted `.s` for both `foo(5)` call sites (pre- and post-UNLOAD) shows byte-identical sequences: `call rt_proc_call_open("foo",1)@PLT` → `test rax,rax` → (success) `call rt_proc_fn@PLT` → `jmp rax`. This is a **fresh lookup on every call** — no cell, no cache. Whatever caused seat14's session to see m3 unchanged is gone on this tree (most likely incidental same-day fleet churn elsewhere; not chased). seat14's routed architecture question does not apply to this code path as it stands.

## PART 2 — THE REAL, NARROWER GAP: THREE TWIN CALL-EMISSION ARMS, ONE WRONG BRANCH EACH

`rt_proc_call_open`'s only 0-return path is `if (!p || !p->fn) return 0;` (not found / unregistered). Three call-emission arms in `src/templates/bb/bb_call_proc_staged.cpp` consume that 0 identically (`test rax,rax; je L(1)`) and all route `L(1)` to `call rt_faildescr` — an ordinary FAIL, so the statement silently doesn't happen and execution falls through to the next statement, instead of the oracle's actual behavior (a hard, nameable runtime error). This is the same "twin site" shape this project has hit before (frame-rsp's two mode-4 prologue emitters, s193's original UNLOAD/LOAD/SETEXIT triage) — found by grepping every `x86("call", "rt_faildescr", ...)` in the file, not by luck:

- `bcps_det_arm()`'s ZD/z-resident arm (~line 424)
- `bcps_det_arm()`'s default arm (~line 681) — **the one `f15_unload.sno`'s two call sites actually hit**, confirmed via `.s` inspection
- `bcps_spine_gen_arm()`'s generator-call arm (~line 788)

**Fix:** repoint all three arms' `L(1)` failure branch from `rt_faildescr` to the already-existing `rt_ab_undef_fn_stub` (`rt.c:480`: `__attribute__((noreturn)) void rt_ab_undef_fn_stub(void) { core_runtime_error(22, "Undefined function called"); __builtin_unreachable(); }`). This stub is not new machinery — it is already the default `fn_cell` value in `bb_define.cpp` (before a real DEFINE binds the cell) and the target of `scrip.c`'s undefined-symbol trampoline. It correctly honors `SETEXIT`/`&ERRLIMIT` error trapping via `longjmp` when armed (`core_runtime_error`'s own logic), rather than unconditionally hard-exiting. 7-hunk diff: one new `extern` decl, plus at each of the 3 sites, the local `fail_fp*` pointer-cache var is repointed at `rt_ab_undef_fn_stub` and renamed `undef_fp*` (it becomes the only remaining use once `rt_faildescr` is no longer called there), and the `x86("call", "rt_faildescr", fail_fp*)` line becomes `x86("call", "rt_ab_undef_fn_stub", undef_fp*)`. Full diff available on request / reconstructable verbatim from this description — every site is named above.

**Verified correct:** `f15_unload.sno` now prints `10` then halts in both m3 and m4 (rc flips 0→1); `unreachable` never prints; the second `foo(5)` never runs. This matches the oracle's actual behavior (still not byte-identical to its stdout — see Blocker 1).

## BLOCKER 1 — DONE-WHEN'S OWN SHAPE CANNOT PASS FOR ANY ERROR-HALTING WITNESS (structural, project-wide)

`test_one_witness.sh`'s `donecheck` requires exit-code match **and** full-stdout `cmp -s` against the live oracle. Measured: `x64/bin/sbl -bf` prints a full abnormal-termination trailer to stdout on every uncaught runtime error — file/line/statement/stmts-executed/`memory used (bytes)`/`memory left (bytes)` — confirmed **absent** on a normal run (`b01_assign.sno` oracle stdout is the bare value `42`, nothing else). The memory-used/left figures are SPITBOL-internal accounting and differ per program: `11872`/`1036696` on `f15_unload.sno` vs `11648`/`1036920` on `f12_load.sno` (both measured directly). No independent reimplementation can reproduce these byte-for-byte. Oracle `rc` is also `0` on this whole class of error (confirmed on both witnesses above) where SCRIP's `core_runtime_error` always `exit(1)`.

**Not specific to this row:** `conform-load-missing-error-validation.task.md` (`f12_load.sno`, same seat08 conformance-sweep batch, identical DONE-WHEN shape, expects ERROR 142) has been `FREE`/unclosed since 2026-08-23 for this exact reason. Any "should raise an oracle error" row from that sweep likely shares this blocker — worth checking before assuming a fix is possible with more runtime code, or before minting more rows in the same shape.

## BLOCKER 2 — CURING PART 2 UNMASKS A PRE-EXISTING OPSYN DEFECT (confirms + extends hq_C's same-day finding)

`test_corpus_snobol4.sh` with the Part 2 fix applied: m3 stays 365/365; m4 goes 365/365 → 364/365. New failure: `crosscheck/rung10`'s `1010_func_recursion` case, specifically its `OPSYN(.facto,'fact')` + `facto(4)` sub-check.

**Proven pre-existing, not introduced by this fix:** rebuilt the unmodified pre-fix tree and ran the identical minimal repro (`DEFINE('fact(n)')` self-recursive factorial; `OUTPUT=fact(5)`; `OPSYN(.facto,'fact')`; `OUTPUT=facto(4)`). Pre-fix mode-4 **already** silently drops the `facto(4)` output — prints only `120`, exits 0, no second line, no error. This fix makes the identical defect loud (crash after `120`) instead of silent. `rung10`'s own self-check (`NE(facto(4),24):f(e003)`) cannot distinguish "correctly computed 24" from "the call itself failed" — both take the same `:F()` branch — so the pre-fix 365/365 was already a false green on this sub-check specifically.

**Root cause measured, and it is the same bug hq_C independently found the same day:** `FINDING-2026-08-27-hq_C-opsyn-alias-is-broken-for-a-single-plain-function-not-rebinding-and-not-nondeterministic.md`, whose one open, explicitly-unmeasured hypothesis was "is `old_entry` NULL in `register_fn_alias` (`core.c:2766`) for a DEFINE'd-proc oldname?" gdb-confirmed here: `break register_fn_alias`, run the fact/facto witness, `old_entry` prints `(FNCBLK_t *) 0x0`. `register_fn_alias` only ever searches/writes `_func_buckets` (the builtin-alias table); `fact` is a DEFINE'd proc living in `g_rt_gen_procs`/`rt_proc_t` — the same two-table split seat14 already hit for UNLOAD itself.

**One data point beyond hq_C's finding:** hq_C's table implies a single OPSYN alias "passes by never using [the broken path]" (the compiler statically resolves it when only the alias name is ever called). This witness is *also* single-OPSYN yet still fails, because it calls **both** `fact(5)` (original) and `facto(4)` (alias). ASM-diff confirms `facto(4)` routes through the STAGED path (`call rt_proc_call_open` + direct jump), not hq_C's by-name-dispatch case (`rt_call_arr_bl@PLT`) — an independent exposure of the identical root cause via a different call route.

**Also flagged, not chased:** mode-3 (`--run`) gives the *correct* answer for this witness (`120`/`24`), both before and after this session's fix, despite `register_fn_alias`'s bug being identical in-process. Some other resolution path exists for m3 that m4 doesn't share — worth understanding before "fixing" `register_fn_alias`, since m3's behavior may already show what the fix should converge to.

## DISPOSITION

The Part 2 fix is real, correct for its own target, and regression-clean in isolation, but **not committed** — landing it flips the blocking-set gate red, and NO BROKEN COMMITS is absolute. Routed to hq_C as `q-unload-donewhen-shape-and-opsyn-block` (owns both correctness methodology and today's OPSYN finding). Task baton (`conform-unload-noop.task.md`) LEDGER carries the same detail plus the exact diff shape. Claim stays open under seat11 pending a ruling on either blocker.
