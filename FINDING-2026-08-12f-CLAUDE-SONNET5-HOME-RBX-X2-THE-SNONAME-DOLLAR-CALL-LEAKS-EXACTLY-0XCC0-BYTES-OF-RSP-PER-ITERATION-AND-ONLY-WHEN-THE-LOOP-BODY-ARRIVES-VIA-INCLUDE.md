# FINDING 2026-08-12f — CLAUDE SONNET5 — HOME-RBX X-2: RTX-FUNC-11 IS NOT A CAPACITY DEFECT. THE `SNO$NAME` DISPATCH LEAKS EXACTLY `0xCC0` (3264) BYTES OF RSP ON EVERY LOOP ITERATION, ONLY WHEN THE LOOP BODY ARRIVES VIA `-INCLUDE`. LIVE RSP TRACING AND CORE-DUMP DISASSEMBLY AGREE ON THE SAME CONSTANT, INDEPENDENTLY.

**Fingerprint at measurement:** SCRIP `51934a9f` + uncommitted instrumentation (this session, see §4) · corpus `14dc06bd` · `.github` `4a292e25` · `RT_OPT` default (`-O0 -g`, not directed otherwise) · built AFTER `install_system_packages.sh` per the load-bearing order warning (FINDING-2026-08-12d).

**Orientation:** read `PLAN.md` → `RULES.md` → `GOAL-SN4-HOME.md` → `GOAL-SN4-HOME-RBX.md` LIVE CURSOR (s33, X-2 open, no blockers) → per RULES "CONSULT CANONICAL SOURCES" read the two existing FUNC-11 FINDINGs in full before touching anything (2026-08-11 "PRODUCT-LAW", 2026-08-11 "INCLUDE-SCOPED-CAPACITY") rather than re-sweeping thresholds a fourth time — both explicitly instruct the next session to instrument, not sweep.

---

## 1. BASELINE RE-PROVEN

`rtx11_dynvar_include.sno` (the existing two-sided witness, `probe/rtx11_dynvar_{include,inline}.sno`): include arm `rc=139` SIGSEGV, inline arm `rc=0` prints `done`. Matches the prior FINDING exactly. Nothing landed between s33 and now changed this class.

## 2. THREE MORE CAPACITY HYPOTHESES KILLED BY INSPECTION, NOT ASSUMPTION

Before instrumenting, checked every fixed-size table reachable from `NV_SET_fn`'s creation path:

- **`_var_reg[VAR_REG_MAX=1024]`** (`core.c:2136`) — **DEAD CODE.** `_var_reg_n` is initialized to 0 and never incremented anywhere in the file; every loop that reads it runs zero iterations, always. Three seats' "falsified threshold constants" line up with this being a red herring someone likely already bumped without effect.
- **`rt_ws_alloc`/`rt_ws_strdup`'s workspace island** (`gc_heap.c:273-308`) — bounded at `ZC_WSI_MB=1024` (1GB, `zeta_choices.h:224`), but **guarded**: exhaustion prints `[WSI] workspace island exhausted` and calls `abort()` (SIGABRT), not a silent SIGSEGV. Also nowhere near hit — creating 16-60 `NV_t` entries is a few KB against a 1GB budget.
- **`global_names[GLOBAL_MAX]`** (`name_binding.c:6-19`) and **`Scope.e[FRAME_SLOT_MAX]`** (`scope_add`, same file) — both bounds-checked (abort / return -1, no corruption), and both populated **only from compile-time syntactic variable names** (`sno_reg_var`, called from `TT_VAR`/`TT_NAME` lowering). A runtime `$`-computed name is invisible to both tables by construction.

None of these can produce a silent SIGSEGV at this scale. Recorded so nobody re-spends the time re-checking them.

## 3. `g_core_errjmp_n` FALSIFIED AS THE MECHANISM

`rt_call_arr` wraps every dispatch in a `setjmp`/`longjmp` nesting counter (`g_core_errjmp_stk[64]`, `by_name_dispatch.c:4645-4658`) — a fixed-size array was a live suspect. Instrumented (`SCRIP_CALLARR_TRACE=1`, prints `fn`, call count, `g_core_errjmp_n` per call) and measured: **`errjmp_n` stays flat at `1` across every call, on both the crashing and clean witnesses.** Killed in one measurement.

## 4. INSTRUMENTATION ADDED (uncommitted in the working tree at fingerprint time; recommend committing alongside this FINDING)

Three env-gated counters, matching the existing `SCRIP_ALLOC_HIST`/`rt_alloc_hist_on()` idiom but **not reusing it**, because `SCRIP_ALLOC_HIST` reports via `atexit()`, which never fires on a raw SIGSEGV — useless for the crashing arm, only usable as an inline-arm control.

- **`SCRIP_NV_TRACE=1`** — one line per new-variable creation, at both `NV_SET_fn`'s and `NV_PTR_fn`'s allocation sites (two distinct creation paths, both covered), immediately `fflush`ed so lines survive a subsequent crash.
- **`SCRIP_CALLARR_TRACE=1`** — one line per `rt_call_arr`/`rt_call_arr_impl` entry: call number, `fn`, `nargs`, `errjmp_n`, and (added second) the live `rsp` value read via inline asm at the true JIT call-site boundary (top of `rt_call_arr`, before its own C prologue's fixed offset).

## 5. ⭐ TOTAL CREATION-EVENT COUNT CLUSTERS AT 35-38 (NEW — NOBODY HAD COUNTED THIS BEFORE)

`SCRIP_NV_TRACE=1` on the include witness: **24 fixed startup keyword registrations** (`ALPHABET`, `tab`...`SUCCEED` — universal, present in every SNOBOL4 program) **+ 3 source variables** (`T`,`A`,`i`, via `NV_PTR_fn`) **+ only 8-11 of the intended 40 `DYNVAR*` names** before the crash. Repeated 6 times: total creation-event count at crash lands in **[35,38]** — a narrow band, not the wide coin-flip zones (88-112, 16-20) prior seats measured on *distinct-name* or *assignment* counts alone. This is the first time startup-keyword creations were counted as sharing the same budget as user/dynamic creations.

⚠ At this point the natural read is "some ~37-slot table," matching the goal file's own manual-level framing (Ch.19 note 7, variable blocks are permanent/unbounded). **This reading turned out to be wrong — see §7.**

## 6. A CONFOUNDED TEST, CAUGHT AND FIXED BEFORE BEING TRUSTED

First attempt at decoupling call-count from creation-count: a `V=1,R=50` probe (one dynamic name, 50 repeated `$`-assigns via the proven `$A[i,2]=A[i,1]` idiom). Built the backing table with 50 literal `T['kN']='FOO'` statements. **Result: clean, rc=0.** Before trusting this, noticed the probe's own construction accidentally supplies 50 statements' worth of the exact "padding raises the threshold" effect the 2026-08-11 FINDING §6 already established (0 pad→16 safe, 10→20, 30→30, 60→60, roughly linear) — so the "no crash" reading was confounded by self-supplied headroom, not informative about R alone.

**Fixed:** rebuilt with the table populated by a 6-line loop (`GT(j,50):F(L1)`) instead of 50 literal statements — 14 total source lines regardless of R. **Verified against the SPITBOL oracle first** (`x64/bin/sbl`, cloned this session) — prints `done`, confirming the probe is valid before trusting SCRIP's behavior on it. Result: **still clean, rc=0, confirmed across 5 runs**, 29 total creation events (24 startup + 4 source vars `T,j,A,i` + 1 `FOO`), 53 total dispatcher calls.

This is worth recording as a caught mistake, not edited away, per this project's own norm.

## 7. ⭐⭐ THE BREAKTHROUGH: LIVE RSP TRACING NAMES THE MECHANISM

The §6 result (53 calls, 1 creation, clean) against the §5 result (~11 calls, ~36 creations, crash) already favored creation-count over call-count as a *symptom* — but neither explained the *mechanism*, and a core dump taken on the crashing witness (`ulimit -c unlimited`; no `gdb` in this container, matching a prior seat's note, so **hand-wrote a `struct.unpack`-based `NT_PRSTATUS` parser** — walked the core's own `PT_NOTE` program header, no `pyelftools` needed) gave real crash registers: `si_signo=11` (SIGSEGV confirmed), `r9=0x70001000` exactly matching `RT_PIN_BASE+RT_PIN_BYTES` = `RT_GVA_VA` (`pin_va.h`) — correct, not corruption — and `rip` resolving to a small (24KB) executable page that is **not** `libscrip_rt.so` (whose own `.text` is 4.3MB) — the anonymous JIT slab that mode-3 executes emitted code from directly, independently corroborating the 2026-08-11 FINDING's own "rip in anon JIT slab" read on a different crash instance.

Extracted the raw bytes at `rip` from the core file and disassembled with `objdump -b binary -m i386:x86-64`: the faulting instruction is `mov QWORD PTR [rsp],rax`, immediately after `sub rsp,0x10`. A few instructions away in the same window: `add rsp,0x10` immediately followed by `add rsp,0xcc0` — a release with **no matching carve visible in that 96-byte window**.

**Added `rsp` capture to `SCRIP_CALLARR_TRACE`** (inline asm `mov %%rsp,%0` at the top of `rt_call_arr`, before its own prologue) and re-ran both witnesses:

| witness | rsp deltas across successive calls |
|---|---|
| **crashing** (`rtx11_dynvar_include.sno`, all-distinct names via `-INCLUDE`) | `-0xcb0, -0xb0, +0xcc0, +0xcc0, +0xcc0, +0xcc0, +0xcc0, +0xcc0, +0xcc0, +0xcc0, +0xcc0, +0xcc0` |
| **clean** (`v1r_decoupled.sno`, same idiom, written inline, no `-INCLUDE`) | `..., 0, 0, 0, 0` — **byte-identical rsp across all 53 calls, zero drift** |

**Repeated 3 more times on the crashing witness — deterministic every time**: same `-0xcb0, -0xb0`, then unbroken `+0xcc0` every call thereafter, varying only in how many calls complete before the fatal one (11-13 across the 3 runs — consistent with the §5 clustering, now explained rather than merely measured: the *rate* is fixed, only the *point of fatality* has run-to-run jitter, plausibly ASLR-dependent on what sits above the frame).

**`0xCC0` (3264 decimal) is the exact same constant independently found in the core-dump disassembly (§ above).** Two independent instruments — live register tracing and post-mortem disassembly of an unrelated crash instance — converged on the identical number.

⇒ **MECHANISM, NAMED (first time in this investigation's history across three prior sessions):** the emitted code for a `$A[i,2]=A[i,1]`-style indirect-assignment loop, when the loop body arrives through `-INCLUDE`, over-releases stack by a fixed 3264 bytes on every iteration — `rsp` walks *upward* (toward the caller's frame, not away from it) instead of returning to its pre-call value. After ~8-11 iterations (~26-36KB of drift) it walks into something that faults. **This is not a table-capacity defect.** The goal file's Ch.19-note-7 framing ("a fixed capacity for an unbounded population is wrong by construction") is a true semantic point in general, but it is not what is happening here — the crash is reproducible with a *single* dynamically-created name repeated, with essentially no distinct-name growth at all, provided the release imbalance is present; §6's clean 51-repeat result on the non-`-INCLUDE` idiom shows the imbalance is specifically tied to how an included loop body's frame is torn down, not to variable population size.

**This is also the first mechanical explanation for why every red witness in this entire investigation requires `-INCLUDE` and every inline control is clean** — a fact every prior session measured and none explained.

## 8. WHAT IS **NOT** DONE

- **The exact emitter/lowering site producing the mismatched `add rsp,0xcc0` is not identified.** I have the constant and the trigger condition (`-INCLUDE`d loop body), not the template/codegen line. Most likely candidate class: a per-block frame-cleanup sized for the *whole* included block's carve, incorrectly scoped to run on *every loop iteration* inside it rather than once — but this is a hypothesis from the shape of the evidence, not yet convicted by reading the emitter with the fix in mind.
- **No fix attempted.** This FINDING is instrumentation + mechanism, not a patch.
- **Not checked:** whether other `-INCLUDE`d loop constructs besides the `$`-indirect-assignment idiom show the same `0xCC0`-per-iteration signature (would confirm the "whole-block cleanup misplaced inside the loop" theory generally rather than as a `SNO$NAME`-specific artifact) — the `fence_driver.sno` 17/17 beauty_suite drivers are the natural broader corpus to re-check with `SCRIP_CALLARR_TRACE` once a candidate fix exists.
- **`161_capture_in_arbno`** (pre-existing `crosscheck/capture` failure noted at s33) untouched, unrelated.
- No `.s` regen — no templates/emitter code touched this session (RULES step-4 not triggered).
- Uncommitted: `src/runtime/core/core.c`, `src/runtime/by_name_dispatch.c` (the three instruments, §4). Recommend committing as diagnostic infrastructure (matches the standing `SCRIP_ALLOC_HIST`/`SCRIP_GC_STRESS` idiom of permanent env-gated instruments) alongside this FINDING.

## 9. NEXT, IN ORDER

1. Find the emitter/lowering site emitting the per-included-block `add rsp,0xcc0` cleanup and determine why it fires per-iteration instead of per-block (likely `lower_snobol4.c`'s `-INCLUDE` handling or the enclosing statement-frame emitter in `emit.cpp`).
2. Once a fix lands, re-run `SCRIP_CALLARR_TRACE`'s rsp column on the witness to confirm zero drift, matching §7's clean control.
3. Re-run `probe/rtx_func_11_{inline,include}.sno` and the 34-file `beauty_suite` (X-2's stated acceptance criterion) both modes.
4. Sweep other `-INCLUDE`d looping constructs for the same signature before assuming this is `SNO$NAME`-specific.

## 10. ADDENDUM (same session, immediately after §9) — THE DIVERGENCE IS NOT A LITERAL `-INCLUDE` BRANCH

Quick, bounded check before opening a wider search: `grep -n "INCLUDE" src/emitter/emit.cpp src/lower/lower_snobol4.c` → **zero hits in either file.** Neither the lowering pass nor the emitter special-cases `-INCLUDE` at all. This means `-INCLUDE` is almost certainly handled upstream (parser/preprocessor splicing text or AST nodes before LOWER sees a unified tree), and the `0xCC0`-per-iteration divergence between the include and inline arms is **structural** — something about the resulting AST/IR shape or statement/label numbering differs between spliced-in and directly-written code — **not** a codegen path that explicitly asks "did this come from `-INCLUDE`?". Recorded so the next session doesn't re-run this exact grep expecting a hit. Next session's search should start at how `-INCLUDE` is expanded (parser stage) and compare the resulting AST/IR shape for the two arms directly (e.g. `--dump-ir` on both witnesses, diffed), rather than searching emitter/lowering source for the string `INCLUDE`.

**Not continued further this session** — context budget spent; see next-session handoff.

**`handoff_status.sh` is the push truth — NOT this document.**

