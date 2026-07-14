# FINDING 2026-07-14 — NCB-3: TEST 140 IS NOT A FRAME-LOCATION BUG. IT IS A COMPUTED-NAME CONDITIONAL-ASSIGNMENT-TARGET INVOCATION BUG.

AUTHORS: Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
GOAL: `GOAL-SNOBOL4-BB.md` PHASE 1 → RUNG NCB-3 ("EVAL/CODE ζ onto rsp; unblocks test 140"). Base: SCRIP `c22ae61c` (ZB-ITER-1a landed; ZC_PORT default CSTACK→FORTH).
STATUS: **ROOT CAUSE, gdb-CONFIRMED — NO CODE MOVED.** Correcting the rung's own framing before anything is touched. Oracles (x64 SPITBOL + csnobol4) were built and used; MONITOR-FIRST was attempted and found DARK for this bug class (see §4). The reproduction, the two distinct failure modes, and the fix surface are below.

---

## 0. TL;DR — THE RUNG'S PREMISE IS PARTLY WRONG

The rung says: move the EVAL/CODE **invoke** out of C onto an rsp-bumped ζ frame, and that "unblocks test 140." Investigation says: **the `eval_frame[512]` C-local is NOT what breaks test 140.** During EVAL *construction* the frame path (`eval_chain_run_capture` → `rt_eval_run`) runs cleanly and `rbx == g_gva_base` is correct there (gdb-verified). Test 140 breaks at **match-commit time**, in the deferred conditional-assignment pump, because the `.`-assignment **target** `*inner('c1')` is a deferred CALL-WITH-ARGUMENT that lowers to a synthetic `EXPR$N` thunk which **is not invocable** from the pump. The rsp-frame refactor is still worth doing, but it is neither necessary nor sufficient for 140. **Do not expect the rsp move alone to turn 140 green.**

---

## 1. THE TARGET, EXACTLY

`corpus/crosscheck/patterns/140_pat_eval_double_fn_trick.sno` (.ref: `stk=B`). The beauty.sno "double-function trick":

```
inner   stk    = c stk
        inner  = .stk                                :(NRETURN)     ; returns the NAME .stk
outer   outer  = EVAL('LEN(1) . *inner(' cs ')')     :(RETURN)      ; EVAL compiles a pattern
...
        pat    = outer('c1') outer('c2')                             ; two EVAL'd patterns concatenated
        s POS(0) pat RPOS(0)                          :S(YES)F(NO)
```

Both oracles (SPITBOL, csnobol4) → `stk=B`. **SCRIP `--run` → `stk=` (empty).** SCRIP `--compile` also fails 140. The initialized value of `stk` is `''`; the empty output means **the conditional assignments never fired** — `stk` is untouched from init.

Semantics (manual Ch.6 + Ch.9, NRETURN p.133, deferred `*` p.85): `LEN(1) . *inner('c1')` matches one char; on whole-match success the target `*inner('c1')` is evaluated — `inner` pushes onto `stk` and NRETURNs the name `.stk` — and the matched char is assigned to that name. Correct trace: match 'A' → inner pushes 'c1', returns .stk, assign 'A'→stk; match 'B' → inner pushes 'c2', returns .stk, assign 'B'→stk. Final `stk='B'`.

---

## 2. ROOT CAUSE — gdb-CONFIRMED (EVAL PATH, test 140)

The deferred-conditional-assignment ("dcap") machinery lives in `src/runtime/pattern_match.c`. Pends are recorded by the capture box as `rt_dcap_e { varname, saved_delta, len }` (:555); commit is BOX-DRIVEN (NCB-1c M3): `bb_match_release.cpp` → `rt_dcap_end_ok_open` (:608) → `rt_dcap_step` (:617) → `rt_dcap_end_ok_close` (:630). The sweep is `rt_dcap_pump` (:576).

`SCRIP_DCAP_TRACE=1` on 140 → `[DCAP] end_ok n=2`. **The two pends ARE recorded and the pump DOES run.** So this is not a missing-pend bug.

The pump body (:589–596):
```c
if (e->varname && e->varname[0] == '*') {
    rt_g_want_name = 1;
    long fb = rt_proc_call_open(e->varname + 1, 0);   // <-- 0 args
    if (!fb) { rt_g_want_name = 0; continue; }         // <-- SILENTLY skips on failure
    c->pending = d;
    return fb;                                          // proc runs as a box; rt_dcap_step finishes the assign
}
if (e->varname && e->varname[0]) NV_SET_fn(e->varname, d);   // plain-name path
```

gdb breakpoint at `pattern_match.c:589` prints the recorded pend varnames:
```
PEND: varname='*EXPR$0'  saved_delta=0  len=1
PEND: varname='*EXPR$1'  saved_delta=1  len=1
```

**They are `*EXPR$0` / `*EXPR$1`, NOT `*inner`.** Because `*inner('c1')` is a deferred call WITH an argument, the lowerer mints a synthetic thunk for it: `sno_expr_collect` at `src/lower/lower_snobol4.c:69–75` (`snprintf(buf, "EXPR$%d", g_sno_nexpr)`; stored in `g_sno_exprs[]`; emitted as a mini-chain `EXPR$N = <deferred expr>` at :1734–1742). The pend therefore carries the thunk name.

gdb at `rt_proc_call_open` filtered to EXPR:
```
rt_proc_call_open('EXPR$0', 0): registered=0   ...   Value returned is $1 = 0
```

**`rt_proc_is_registered("EXPR$0") == 0` and the call returns 0.** The EVAL runtime-compile path (`runtime_eval.c: eval_build_chain` → `lower_snobol4` + `emit_chain(...,"pat_flat")`) emits the EXPR$N sub-chain into the graph but **never registers it as a callable proc**, so `rt_proc_call_open` cannot find it. `fb==0` → the `*` arm hits `continue` → **the assignment is skipped** → `stk` stays `''`. QED.

Corollary defect: the `if (!fb) { … continue; }` is a SILENT drop. Even once the invocation is fixed, this line should not swallow a genuine call failure without a trace — it masks exactly this class of bug.

### What is NOT the bug (ruled out, so the next session doesn't re-chase them)
- **GVA index mismatch — RULED OUT.** `gva_index_of` (`src/optimizer/gva_collect.c:20`) is a PERSISTENT global map; `eval_build_chain` does not reset it or re-run the optimizer, so the EVAL fragment reuses the main program's map. `SCRIP_M3_GVA_TRACE=1` → `active=1 n_gva=7`, one canonical slot for `stk`.
- **`stk` accessed by name — RULED OUT.** Breakpoints on `NV_SET_fn`/`NV_GET_fn` filtered to `name=="stk"` NEVER fire. All `stk` access is via the fast GVA slot `[rbx+k*16]`. (The commit assignment goes through `rt_assign_var`, not `NV_SET_fn` — see §3.)
- **`rt_eval_run` / `eval_frame[512]` stale-frame — RULED OUT for 140.** `EXPVAL_fn` (the DT_E slen==3 `eval_frame[512]` path, `runtime_eval.c:268`) NEVER fires during the 140 match. The frame path runs only at EVAL CONSTRUCTION (twice, once per `outer()`), where `rbx==g_gva_base` is correct.

---

## 3. A SECOND, DISTINCT FAILURE MODE — THE PLAIN (NON-EVAL) PATH

Minimal non-EVAL repro (`pat = LEN(1) . *inner('c1') LEN(1) . *inner('c2')`, `inner` DEFINE'd normally, NRETURN `.stk`): oracles → `stk=B`; **SCRIP → aborts**:
```
[IDX] BOMB rt_assign_var: lvalue is not a variable (dtype=1) — string/record subscript assignment is the tvsubs rung (GOAL-IR-IMMUTABLE-EMIT IDX-UNIFY)
```
Same for a NULLARY deferred call (`. *grab()`, the shape `expr_eval.sno` uses). Here the proc IS reached and called; the failure is downstream in `rt_dcap_step` (:617) → `rt_assign_var(nm, c->pending)` (:626): the value flowing back as the "name" has **dtype=1 (a string), not a NAME descriptor**. So the NRETURN name (`inner = .stk`) is **degrading to a string** somewhere between the thunk return and `rt_assign_var` — the epilogue (`rt_proc_call_epilogue`) or the thunk's `EXPR$N = <expr>` store is not preserving name-ness.

So the two failing modes are:
1. **EVAL path (140/141):** thunk not registered → call fails → assign skipped (silent). `stk=''`.
2. **Plain path (expr_eval's main-program `. *Push()` shapes):** thunk called → NRETURN name degrades to string → `rt_assign_var` bombs.

`expr_eval.sno` (3rd failing crosscheck) exercises BOTH — it has `. *Push()`/`. *Unary()`/`. *Binary()` in the main program AND `EVAL(...)` inside the callees — so it needs both modes fixed.

---

## 4. THE MONITOR IS DARK FOR THIS BUG CLASS (a real MON-RE precondition)

Per RULES.md, MONITOR-FIRST is mandatory and a dark monitor must be reinstated first. It IS dark here. `PARTICIPANTS="csn scr"` and `"spl scr"` on 140 both diverge at **step 2** with the oracle emitting a statement `LABEL stno=N` event while SCRIP emits a `CALL outer` / `@1 CALL EXPR$0` event. Proven to be a **trace-vocabulary mismatch, not the bug**, by running the monitor on **PASSING test 161** (`161_pat_defer_fn_nested_match`) — it trips the identical false CALL divergence. Cause: `scripts/monitor/tracepoints_bin.conf` does `INCLUDE .*`, so SCRIP's `mon_emit_call_bin()` (`rt.c:795`, `rt.c:991`) emits CALL events for user functions AND for compiler-internal thunks (`EXPR$N`) that the oracle bridges structurally cannot emit (they don't compile deferred exprs into named functions). Aligning this (suppress synthetic/`EXPR$`/builtin CALL events in SCRIP under the monitor, or teach the bridges) is a genuine **MON-RE rung** and is the proper prerequisite to bracketing 140 mechanically. This session used gdb-direct as the pre-committed contingency.

---

## 5. FIX SURFACE (for the next session — this is "its own session, NOT localized", as the rung warned)

A correct fix spans, at minimum:
1. **The EVAL runtime-compile path** (`runtime_eval.c: eval_build_chain`): make the `EXPR$N` thunks it emits **invocable** by the dcap pump. Either register each as a callable proc (mirror whatever `lower_sno_stage2` / the main-program emit does to make `*Push()` callable), or expose their per-label entry points so the pump can reach them.
2. **The dcap pump** (`pattern_match.c: rt_dcap_pump` :589): when the `*` target is a DT_E/`EXPR$N` thunk rather than a registered proc, invoke it via the DT_E/eval mechanism (this is where the rung's "invoke on an rsp-bumped ζ frame" belongs — the thunk invocation is the thing that should move onto rsp and be box-driven). Also make the `if(!fb) continue` non-silent.
3. **NRETURN name-descriptor flow** (plain path, §3): `rt_proc_call_epilogue` / the `EXPR$N = <expr>` store must preserve the NAME descriptor so `rt_assign_var` (`:626`) receives a variable, not a string (dtype=1).
4. **The `esi` audit still owed** (NCB-2a) intersects (1): the EVAL chain entry ABI (`rt_eval_run` sets `esi=0`) and the thunk-call ABI must agree.

**Validation bar:** all 305 crosscheck tests (m3 303/3, m4 302/3/1 at this base; ~35s) must not regress; 140/141/expr_eval must go green in BOTH modes; smoke 7/7 both modes. Do NOT commit on low context — a partial fix here silently corrupts a passing baseline.

### Candidate approaches (unranked; next session picks)
- (A) Register `EXPR$N` thunks as callable procs during EVAL compile; the pump's existing `*NAME` arm then just works — but the thunk ABI must return a NAME (fixes §3 too if unified).
- (B) Teach the pump to invoke DT_E thunks via `EXPVAL_fn`/eval on an rsp frame (ties directly to the rung's rsp goal), keeping proc-calls and thunk-calls as two arms.
- (C) Replicate exactly what the working main-program `. *Push()` path does — but note §3 shows that path is ALSO broken (name→string), so (C) alone is insufficient.

---

## 6. GROUND TRUTH ARTEFACTS (this session)
- Baseline reproduced EXACTLY at `c22ae61c`: m3 `PASS=303 FAIL=3` (`expr_eval 140 141`), m4 `PASS=302 FAIL=3 SKIP=1` (`expr_eval 140 1017_arg_local`), DIVERGE=1 (`1017_arg_local`). Smoke 7/7 both modes.
- gdb scripts + outputs, `SCRIP_DCAP_TRACE`/`SCRIP_M3_GVA_TRACE` traces, and monitor runs are in the session transcript.
- Manual sections read: EVAL (p.130–132, ref p.221), CODE (p.132–133, ref p.215), NRETURN (p.133), deferred `*` (p.85–86).

---

## ✅ RESOLVED — s56 (2026-07-14, Claude). SCRIP `9f24d954`. Test 140 green in BOTH modes.

This finding's mechanism was right and its fix surface was right. The *root* was one layer deeper than
"the EVAL compile emits the sub-chain but never registers it", and the correction is worth recording
because it explains why a register-only patch would have looked correct and still failed:

**The thunk proc was never BUILT, so there was nothing to register.** `lower_snobol4()` — the entry
`eval_build_chain` calls — is a one-line wrapper for `sno_lower_fragment_at()`. The `EXPR$N` thunk
GRAPHS are built by a loop that lives exclusively in `lower_sno_stage2()`, the whole-program entry. A
runtime EVAL therefore ran `sno_expr_collect` (minting the NAME `EXPR$0`, recording the pend as
`*EXPR$0`) and then built no graph, filed no `ProcEntry`, and emitted nothing. `rt_proc_call_open`
returning 0 was not a registration bug; it was a truthful answer about a proc that did not exist.

**What landed:**
1. `sno_expr_thunks_build(mark)` — the thunk-graph loop, lifted out of `lower_sno_stage2` (which now
   calls it with mark 0; whole-program behaviour is bit-identical) and made callable from a mark, so
   the fragment path can build exactly the thunks IT minted.
2. `eval_thunks_emit_from(pc0)` (runtime_eval.c) — the driver's own walk, over just the procs the
   fragment added: `rt_proc_register` → set generator/variadic/dyn_scope/result_name →
   `ir_drive_slot_assign` → `emit_chain(…, "proc_flat")` → `rt_proc_set_fn`. The slot pass is NOT
   optional: without it the emitted thunk aborts with *"frame-active graph with no zeta_mark slot"*.
3. **Name salting.** `lower_sno_stage2` resets `g_sno_nexpr = 0` per compile, so every runtime EVAL
   re-minted `EXPR$0`. Fragment compiles now salt (`EXPR$0F1`, `EXPR$1F2`, …); the main program keeps
   plain `EXPR$N`, so its artifacts are byte-identical. In mode 4 this matters more than in mode 3:
   main's `EXPR$0` is registered at startup by the emitted binary, and the first runtime EVAL would
   otherwise overwrite that registration.
4. **The NAME survives.** `rt_dcap_pump` re-arms `rt_g_want_name` after opening an `EXPR$` thunk, so
   the NRETURN'd `DT_N` is not deref'd to a string by `rt_nret_fix` at the thunk's tail call (this
   finding's SECOND failure mode). `rt_dcap_step` additionally honours a string-valued target by name
   indirection (manual p.85 / p.192). The silent `!fb continue` now warns.

**Latent heap bug found en route (independent of EVAL, hit by any virgin `stage2_t`):**
`stage2_proc_grow` / `stage2_label_grow` doubled a zero cap — `s2->proc_cap *= 2` with cap 0 stays 0 —
so the first grow `realloc`'d to ZERO bytes and then `memset` a whole `ProcEntry` past the end. The
whole-program path never arrives with a virgin table, so this had slept forever; the mode-4 runtime
`.so` DOES (its `g_stage2` is untouched until an EVAL compiles something), which is precisely why 140
passed mode 3 and SIGSEGV'd mode 4 for one build. Seeded to 16, matching `bb_program_add` — which had
the guard all along. gdb: `__memset_evex_unaligned_erms` ← `stage2_proc_grow` ← `sno_expr_thunks_build`
← `eval_build_chain("LEN(1) . *inner(c2)")`, i.e. the SECOND EVAL, as the cap-0 arithmetic predicts.

**MONITOR-DARK verdict upheld.** No monitor work was possible for this class; gdb-direct was used as
this finding sanctioned. A MON-RE trace-vocab align remains the true MONITOR-FIRST prerequisite.

**Still open, and explicitly NOT this class** (so the next session does not re-chase them through EVAL):
141 bombs in the LOWERER (`tree kind 25` in ARBNO-body position) at COMPILE time in both modes, and
expr_eval hits the `[B-RE]` opaque-DT_P refusal. Both are pattern-composition-over-a-runtime-pattern
problems (SZ-4 / SZ-5), not deferred-thunk problems.

**Known hazards documented, NOT fixed:** (1) an over-budget `bb_pool_release` in the eval cache can free
emitted thunk code while the proc registry still points at it; (2) a deferred call whose ARGUMENTS
contain another user-proc call will mis-consume the re-armed `want_name` flag; (3) `code()` does not
salt, so a CODE fragment carrying `*expr` can still collide with main's `EXPR$N`.
