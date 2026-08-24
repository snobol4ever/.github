# FINDING 2026-08-24 (seat03) — row `vlist-v05-m4-sigsegv-m3-m4-divergence`: the m3≢m4 crash is NOT the disjunction's spine cell — it's a genuine memory-safety bug in EVAL's runtime indirect-call path, valgrind-localized

## HEADLINE

The task brief's own hypothesis ("suspect the m4 medium's spine depth around the new disjunction flat-cell")
is **exonerated by direct measurement**: `v01_select_min.sno`, which uses the exact same `IR_DISJUNCTION`
construct as `v05`, runs **100% valgrind-clean** under mode 4. `v05`'s crash is a real memory-safety defect —
valgrind catches an **invalid read of an unmapped address (`0x1F00000000`) inside libc's `getenv()`**, reached
via an `atexit` handler, meaning something earlier in execution performed a wild write that corrupted process
state (most likely `environ` or an adjacent glibc global). Every "uninitialised value" warning valgrind flags
along the way — including inside `rt_define_tiny_ok` (`rt.c:1785`) — is **not disjunction/zeta-storage code at
all**; all of it sits inside **EVAL's runtime code-generation path for an indirect procedure call**
(`*push_list(...)`, `*pop_final(...)` — the classic SPITBOL `epsilon . *Foo(...)` trampoline idiom, here built
from a dynamically-constructed `EVAL()` string, not a literal source pattern) or the deferred pattern-capture
pump. ⛔ The `rt_define_tiny_ok` lead was tested this session with a one-line kill-switch (`SCRIP_NO_TINY=1`)
and **did not fix the crash** — read the "RECOMMENDED NEXT STEP" section below before chasing it further; the
exoneration of the disjunction construct is solid, but which specific EVAL/capture site is the true root cause
is still open.

## WHAT'S CONFIRMED, MEASURED THIS SESSION

- **m3/m4 split reconfirmed** on current tree (SCRIP `1a9cc1bc`, post `0e57de3b` + `9df28b03`): `v05` mode 3
  prints `MATCH size=1` correctly, rc=0. Mode 4 (`--compile` + `gcc -no-pie` + `libscrip_rt.so`): **no stdout at
  all**, rc=139 (SIGSEGV, core dumped).
- **`v01` is valgrind-clean under mode 4** (`valgrind -q ./v01_bin`, zero output, rc=0) — same
  `IR_DISJUNCTION`/`disj_sigma_copy`/`fc_geom` flat-cell path the task brief suspected, minimal witness,
  completely exercised, zero corruption signal. This rules out the disjunction's own codegen as the culprit for
  `v05`'s crash; whatever's wrong is specific to something `v05` does that `v01`–`v04` don't.
- **`v05` under `valgrind -q` (no `--main-stacksize` override, default 60s timeout)**: several "Conditional
  jump or move depends on uninitialised value(s)" warnings preceding the fatal one, most specifically —
  ```
  ==PID== Conditional jump or move depends on uninitialised value(s)
  ==PID==    at 0x4B95240: rt_define_tiny_ok (rt.c:1785)
  ==PID==    by 0x4DDFF40: bb_tiny_shim_ok (bb_call_proc_staged.cpp:204)
  ==PID==    by 0x4DE5BB6: bcps_det_arm()::{lambda()#1}::operator()() const (bb_call_proc_staged.cpp:266)
  ==PID==    by 0x4DF9B59: bcps_det_arm() (bb_call_proc_staged.cpp:263)
  ==PID==    by 0x4E0F0F0: bb_call_proc_staged_str[abi:cxx11](IR_t*) (bb_call_proc_staged.cpp:859)
  ==PID==    by 0x4DDAA6A: bb_call[abi:cxx11](IR_t*) (bb_call.cpp:510)
  ==PID==    by 0x4BE1531: walk_bb_node_inner (emit.cpp:1254)
  ==PID==    by 0x4BDA8A3: walk_bb_node (emit.cpp:975)
  ==PID==    by 0x4BE807A: emit_drive (emit.cpp:1520)
  ==PID==    by 0x4C12DCE: codegen_flat_chain_body (emit.cpp:3086)
  ==PID==    by 0x4C1BB17: emit_chain (emit.cpp:3421)
  ==PID==    by 0x4BB6102: eval_thunks_emit_from (runtime_eval.c:188)
  ```
  **This is the emitter running AT RUNTIME, inside the compiled `v05_bin` process itself** — `eval_thunks_emit_from`
  is EVAL's mechanism for JIT-compiling a dynamically-built string (`EVAL("epsilon . *push_list(" vs ")")`,
  line 65 of the witness) into a fresh Byrd-box chain and executing it, by calling back into the SAME
  `emit_chain`/`codegen_flat_chain_body`/`walk_bb_node` machinery that `scrip --compile` itself uses at
  ahead-of-time compile time. `bb_call_proc_staged_str` → `bcps_det_arm` → `bb_tiny_shim_ok` is a call-site
  optimization deciding whether an indirect call (`*push_list(...)`) can use a cheaper "tiny shim" ABI —
  `rt_define_tiny_ok` (rt.c:1782-1786) makes that decision by reading `p->dyn_scope`, `p->is_generator`,
  `p->is_variadic`, `p->redefined` off the `rt_proc_t` registry entry for `"push_list"`, and valgrind says one
  of those fields is uninitialized memory at the time of the read.
- Several more "uninitialised value" warnings follow, all inside EVAL/pattern-capture machinery
  (`eval_cache_insert_raw`/`eval_cache_get` in `runtime_eval.c`, `table_set_descr_d` in `aggregates.c` via
  `rt_assign_var`/`rt_dcap_pump`/`rt_match_end_all` — the deferred-capture-and-assign pump for the unanchored
  scan `'ab' ? p :F(NO)` at the witness's line 91) — **not reproduced or investigated in depth this session**,
  listed here so the next pass doesn't have to re-discover them.
- **The fatal error**: `Invalid read of size 1 at getenv (getenv.c:31), by zop_audit_report (zeta_storage.c:904),
  by __run_exit_handlers, by exit, by main_γ. Address 0x1F00000000 is not stack'd, malloc'd or (recently)
  free'd.` `zop_audit_report` is an `atexit`-registered diagnostic hook (registered from
  `zop_audit_graph_close`, `zeta_storage.c:894-896`) that calls `getenv("SCRIP_ZOP_AUDIT")` as its first act.
  glibc's `getenv` crashes walking `environ` — meaning `environ` (or a pointer glibc's `getenv` depends on) has
  already been corrupted to an absurd, clearly-non-pointer-shaped value (`0x1F00000000` — plausibly a
  SNOBOL4-domain integer like `31` landing in a pointer-sized slot via a tagged-value/DESCR mixup, though this
  is speculation, not verified). **Because this crash happens inside an atexit handler, it also swallows the
  program's own buffered stdout** — `v05`'s actual computed result may well be correct (mode 3 says so) and the
  crash purely destroys visibility into that fact, which is why `--run` mode's own terminal output never
  appears even though `main_γ` had already reached `exit()`.
- **EVAL itself is not broadly broken under mode 4**: `corpus/crosscheck/rung10/{1016_eval,1019_eval_string,1022_eval_fail}.sno`,
  `crosscheck/control/expr_eval.sno`, and `crosscheck/patterns/{140,141}_pat_eval_*.sno` are all part of the
  clean, fully-passing crosscheck suite (mode 4 included). The `epsilon . *Foo(...)` indirect-call idiom is
  also independently exercised (and passing) in `beauty.sno`, `json.sno`, `porter.sno`,
  `calculator-2.sno`, `include/semantic.inc` — **as a literal source pattern**, not as the return value of a
  dynamically-constructed `EVAL()` string. The narrower, untested combination appears to be: **EVAL of a
  dynamically-built string, where that string itself contains an indirect-call trampoline, invoked from inside
  real (non-tail, multi-frame) SNOBOL4 procedure recursion (`ListInsert`/`ListAppend`), running inside a
  `--compile`-built (mode 4, gcc-linked) process.**

## WHAT THIS FINDING DOES NOT ESTABLISH

- **Not proven**: that `rt_define_tiny_ok`'s uninitialized read is the actual ROOT cause of the wild write that
  later corrupts `environ`-adjacent memory, as opposed to a downstream symptom of something else already wrong,
  or a red herring that happens not to matter (an uninitialized boolean read can take a wrong branch without
  itself writing bad memory). It is the **first** point in the crash's causal chain where valgrind can name a
  concrete, file:line-precise defect, which makes it the natural next place to look — not a confirmed fix target.
- **Not investigated**: whether `rt_proc_register`'s "already exists" branch (`rt.c:448`, which deliberately
  does NOT touch `is_generator`/`dyn_scope`/`is_variadic`/`jmp_entry` — correct behavior for genuine
  redefinition, since it sets `redefined=1` and `rt_define_tiny_ok` checks `!p->redefined`) is actually what's
  firing here, versus a THIRD registration path. `rt_proc_register_rec` (`rt.c:1948-1959`) only calls
  `rt_proc_register()` (the fully-zero-initializing path) when `r->flags & 1` is set; if unset, the subsequent
  `rt_proc_set_fn`/`rt_proc_set_nparams`/`rt_proc_set_nformals` calls all silently no-op via `rt_proc_find`
  returning NULL (verified: `rt_proc_set_nparams`/`rt_proc_set_nformals`, `rt.c:561-571`, both guard on
  `if (p)`) — so THAT path looks safe on inspection, but was not traced against v05's actual DEFINE/registration
  sequence to confirm which path `"push_list"` actually goes through, nor whether some OTHER writer touches
  `g_rt_gen_procs` entries outside `rt_proc_register`'s two branches.
- **Not attempted**: any fix. Per this row's own repeated, hard-won lesson (this same investigation area has
  already produced multiple "confident but wrong" attempts across prior sessions — see the superseded
  `vlist-expr-alternation` FINDING's own corrections), a genuine memory-safety bug reached through a chain this
  long deserves targeted instrumentation (e.g., a temporary assert/fprintf on every write to a `push_list`
  `rt_proc_t` entry's `is_generator`/`is_variadic`/`dyn_scope` fields, or a valgrind `--track-origins=yes` run
  to get the uninitialized value's allocation site directly) before any code change, not a guess.

## RECOMMENDED NEXT STEP

1. ⛔ **TESTED THIS SESSION, NEGATIVE RESULT — do not re-propose this as the fix:** `SCRIP_NO_TINY=1
   v05_bin` (which makes `bb_tiny_shim_ok` return 0 unconditionally at its very first line, before reaching
   `rt_define_tiny_ok` at all) **still crashes rc=139, same as without it.** This means `rt_define_tiny_ok`'s
   uninitialized read, while real (valgrind still flags it independently of whether its result is later used
   for a tiny-shim decision), is **not sufficient on its own to explain the fatal crash** — either it's a
   genuinely inert red herring (an uninitialized boolean read that happens not to matter because both branches
   are otherwise safe), or the real wild write happens somewhere else in the chain regardless of which ABI path
   `bb_call_proc_staged_str` takes. **Correcting my own hypothesis in real time rather than leaving it
   standing unconfirmed.**
2. The other valgrind-flagged "uninitialised value" sites — `eval_cache_insert_raw`/`eval_cache_get`
   (`runtime_eval.c:54/47`) and `table_set_descr_d` (`aggregates.c:428`) via `rt_assign_var`/`rt_dcap_pump`/
   `rt_match_end_all` (the deferred-capture-and-assign pump servicing the witness's own `'ab' ? p :F(NO)`
   unanchored scan-with-capture at line 91) — are now the **more promising** leads, specifically because they
   involve mutable shared state (a cache, a table assignment) rather than a read-only ABI-choice flag. Neither
   was tested against a `SCRIP_NO_TINY`-style cheap kill-switch this session (none may exist) — worth checking
   for one before instrumenting by hand.
3. Re-run `valgrind --track-origins=yes` on `v05_bin` (this session used plain `-q`) targeting the
   `eval_cache_*`/`table_set_descr_d` sites specifically now that the tiny-shim lead is ruled insufficient — it
   names exactly where the uninitialized bytes were allocated/left unset, which is the fastest path to a real
   root cause from here.
4. Do not chase the `zeta_storage.c:904` `getenv()` crash site itself — it is confirmed to be a **victim**, not
   a cause (an ordinary `getenv()` call against corrupted global state), and "fixing" it (e.g., by removing the
   `atexit` audit hook) would only hide the real defect and additionally stop losing the diagnostic evidence
   this FINDING relies on.
5. Whatever the mechanism turns out to be, this session's strongest confirmed result stands regardless: it is
   **not** `zd_plan`/`emit.cpp`'s disjunction dispatch/`bb_disjunction.cpp` (v01 exonerates that construct
   directly), so the fix almost certainly belongs in the EVAL runtime path (`runtime_eval.c`) or the
   pattern-capture pump (`pattern_match.c`/`aggregates.c`), not in this row's own VLIST/disjunction code.

## RECEIPTS

SCRIP `1a9cc1bc` (post `0e57de3b` vlist cure + `9df28b03` tdump-regression fix), `make pristine` fresh build,
`RT_OPT` default `-O0`. `valgrind` (available in-container, `/usr/bin/valgrind`) with default options
(`-q`, no `--track-origins`) against both `v01_select_min.sno` and `v05_treebank_pushlist_235.sno` compiled
`--compile` + `gcc -no-pie -Wl,-rpath,out out/libscrip_rt.so`. `gdb -batch -ex run -ex bt -ex "info registers"`
under `SCRIP_NO_SEGV_HANDLER=1` gave the initial (less informative — points at the `getenv` victim site, not
the cause) backtrace; valgrind is what actually localized this. `test_gate_template_medium_invisible.sh`
checked first (0 BOTH-MEDIUM sites in `bb_*.cpp`, ruling out a literal `MEDIUM_TEXT`/`MEDIUM_BINARY` branch as
the mechanism, before reaching for valgrind).
