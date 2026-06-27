<!-- GOAL-SNOBOL4-BB · SCRIP native pattern-match ladder for modes 3/4 (--run/--compile) -->

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  ▶▶▶▶▶  TOP PRIORITY — SEEN FIRST, DONE FIRST — MONITORED LADDER CLIMB  ◀◀◀◀◀  ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

**THIS SECTION IS THE WHOLE JOB. Everything below it (DEMO-PAT, NRG, GVA, PERF-CALL, …) is a SOURCE OF FAILING PROGRAMS to feed THIS ladder — not a separate track.** The method (Lon directive 2026-06-27 — **lightened from strict MONITOR-FIRST now that the monitor is proven**): **STATIC-FIRST → ONE STAB → THEN MONITOR.** For each failing program: (1) **STATIC ANALYSIS** — read the program's `.ref`, run SCRIP `--run`/`--compile`, read the divergent output, then reason from the generated `.s` + the IR + the BB templates straight to the land mine. (2) **ONE STAB** — make a single targeted fix and rebuild. (3) **VERIFY against the program's `.ref`** — both `--run` AND `--compile` must match it; the `.ref` is ground truth, **no live oracle needed**. If the stab FAILS or the bug resists static reasoning, **ESCALATE** to the 2-way IPC sync-step monitor: bracket between the first divergent trace event and the previous (last-agreeing) event, pin a gdb spin/ignore-counter breakpoint at that bracket, and walk C-step-by-step until the LAND MINE (the instruction that writes the wrong value) is under the cursor — fix, re-verify. The monitor is the **heavy instrument reserved for hard-to-find bugs**; it (and the x64 SPITBOL oracle + the extra monitor build targets it needs) is **NOT built or run until a stab has failed**. NO scattershot prints. The regression gate stays the `.ref`-based crosscheck (fast, not the monitor). Documented prior art (monitor escalation): `GOAL-MONITOR-REINSTATE.md`, `MONITOR-BINARY-DESIGN.md`, `GOAL-TWO-STEP-HUNT.md`, and the gdb-hit-count diagnoses in `GOAL-LANG-SNOBOL4.md` / `GOAL-CSN-FENCE-FIX.md` / `GOAL-PROLOG-BB.md` and `archive/ARCHIVE-LANG-SNOBOL4-HISTORY.md`.

## ⛔ FACT RULE — SCRIP SNOBOL4 IS CASE-SENSITIVE; ALL RESERVED NAMES MUST BE UPPERCASE (Lon directive, 2026-06-26)
**SCRIP SNOBOL4 operates in case-sensitive mode ONLY. This is non-negotiable and permanent.**
- All reserved/builtin symbols MUST be UPPERCASE in SCRIP source: `DEFINE`, `OUTPUT`, `INPUT`, `END`, `RETURN`, `FRETURN`, `NRETURN`, `EQ`, `NE`, `LT`, `LE`, `GT`, `GE`, `LGT`, `IDENT`, `DIFFER`, `INTEGER`, `REAL`, `SIZE`, `TRIM`, `DUPL`, `REVERSE`, `REPLACE`, `SPAN`, `BREAK`, `ANY`, `NOTANY`, `LEN`, `POS`, `RPOS`, `TAB`, `RTAB`, `ARB`, `ARBNO`, `REM`, `FAIL`, `SUCCEED`, `FENCE`, `ABORT`, `BAL`, `OPSYN`, `EVAL`, `CODE`, `APPLY`, `ARRAY`, `TABLE`, `DATA`, `ITEM`, `CONVERT`, `CHAR`, `LPAD`, `RPAD`, `SUBSTR`, `SORT`, `COLLECT`, `COPY`, `DATE`, `TIME`, `PROTOTYPE`, `ARG`, `LOCAL`, `FIELD`, and all keywords (`&LCASE`, `&UCASE`, `&ALPHABET`, `&ANCHOR`, `&TRIM`, etc.).
- **SPITBOL oracle must ALWAYS be invoked with `-bf` flag** (binary, no case-folding): `/home/claude/x64/bin/sbl -bf file.sno`. Never invoke without `-bf` as it will silently fold case and produce misleading oracle results.
- The crosscheck corpus (`corpus/crosscheck/`) and all reference test programs already use uppercase. If a test program has lowercase builtins, it is a bug in the test program, not a SCRIP limitation.
- This rule was established because the SCRIP parser is case-preserving (`intern = strdup`, no folding) and the runtime registers all builtins in `_func_buckets` under their uppercase names (`"DEFINE"`, `"EQ"`, etc.). A lowercase call `define(...)` will never find the builtin and will silently fail with Error 5.



## THE LADDER (do strictly in this order)

- **RUNG 0 — GET THE MONITOR LIT FOR MODES 3/4.** The monitor is currently DARK for native modes (the per-statement taps lived only in the deleted mode-2 path). Until it emits `LABEL/VALUE/CALL/RETURN` per statement from `--run`/`--compile`, no climb is possible. This is the **MON-RE rung immediately below** (MON-RE-1 … MON-RE-6). Reinstating it is the prerequisite to every subsequent rung and therefore comes FIRST. Acceptance: `PARTICIPANTS="spl scr" SCRIP_RUN_FLAG=--run bash scripts/test_monitor_3way_sync_step_auto.sh /tmp/mdiv.sno` reports the first divergence at the `$nm = vl` statement (a real semantic divergence), with matching LABEL/VALUE granularity up to that point.
- **RUNG 1 — CLIMB THE CROSSCHECK FAIL SET.** Walk `test_crosscheck_snobol4.sh`'s FAIL set one program at a time, **STATIC-FIRST**: read its `.ref` + the divergent SCRIP output + the generated `.s`, take ONE targeted stab, rebuild, and verify `--run`/`--compile` against the `.ref`. Escalate to the monitor (bracket → gdb spin-break → land mine) ONLY if the stab fails. Each fix drops the fail count by one; the next program's divergence is the next sub-rung. The fail set is the rung supply.
- **RUNG 2 — CLIMB THE DEMO HANGS (claws5, treebank).** Same loop on the pattern-heavy demos (the DEMO-PAT material below): monitor localizes the hang to the first statement where SCRIP's wire diverges from the oracle (GAP-1's deferred-call-in-capture will surface as the trace event where the side-effect counter fails to advance), bracket it, walk to the land mine in the lower/emit/runtime path, fix. The GAP-1…GAP-7 diagnosis below is the MAP of expected land mines, not a substitute for the monitor finding them.
- **RUNG 3+ — anything else that diverges** (NRG correctness regressions, new feature gaps) climbs the same ladder.

**Build + monitor invocation (every session):**
```bash
apt-get install -y libgc-dev && cd /home/claude/SCRIP && make && make libscrip_rt
git clone https://github.com/snobol4ever/x64 /home/claude/x64   # SPITBOL oracle (spl)
# 2-way monitor (the bug finder):
PARTICIPANTS="spl scr" SCRIP_RUN_FLAG=--run bash scripts/test_monitor_3way_sync_step_auto.sh <file.sno>  # SCRIP under test
# then gdb at the bracket with a spin counter:
#   break <file>:<line>;  ignore <bp> <N-1>   (stop on the first DIVERGENT iteration)
#   step / next / finish  until the land-mine instruction is under the cursor
```

---

<!-- GOAL-MONITOR-REINSTATE · IPC sync-step binary monitor, re-homed onto native modes 3/4 -->

# RUNG 0 DETAIL — GOAL-MONITOR-REINSTATE.md — reinstate the binary sync-step IPC monitor

## ▶▶▶ NEXT SESSION — START HERE

**Why this goal exists.** The binary sync-step IPC monitor (controller `scripts/monitor/monitor_sync_bin.py`, harness `scripts/test_monitor_3way_sync_step_auto.sh`, wire format `scripts/monitor/monitor_wire.h`) compares SCRIP against SPITBOL **event-by-event over a synchronous binary wire** and reports the FIRST divergence with a source-line table. It made bug-finding near-instant. It went dark when **mode-2 (`--interp`) was deleted**: the per-statement trace taps (`mon_emit_label_bin`, the VALUE/CALL/RETURN emitters) are called ONLY from `src/driver/driver_call.c` → `exec_stmt`, the dead mode-2 SM-interpreter path. Modes 3 (`--run`) / 4 (`--compile`) are native x86 and never call them per-statement, so SCRIP's wire stream leads straight to `END` while SPITBOL leads with `LABEL stno=1`.

**GROUND TRUTH (session, verified by live run — NOT inferred):**
- Framework WORKS: with the harness defaulting to `--run`, a 2-way `PARTICIPANTS="spl scr"` run connects both participants, steps the barrier, and prints a DIVERGE table. The controller, FIFO barrier, byte-compare, and first-divergence reporter are all intact.
- SCRIP-side binary protocol is INTACT in `src/runtime/core/core.c`: `mon_send_bin`, streaming `MWK_NAME_DEF` intern, `MWK_VALUE/CALL/RETURN/LABEL/END`, the go-pipe barrier (`MONITOR_READY_PIPE`/`MONITOR_GO_PIPE`), and the LOAD-able `_b_MON_PUT_*` builtins. Verified: scrip emits 27 wire bytes when env vars are set.
- SPITBOL `/home/claude/x64/bin/sbl` has the bridge compiled in (`MONITOR_READY_PIPE` present in the binary); x64 carries `monitor_ipc_spitbol.so` + `osint/monitor_ipc_runtime.c`.
- The CURRENT divergence on any program is the instrumentation-granularity gap (SPITBOL `LABEL stno=1` vs SCRIP `END`), NOT a semantic bug. Fixing that gap = this goal.
- `mon_emit_label_bin` is reachable ONLY from `driver_call.c:161` (mode-2). The IR does NOT carry a statement number (`lower_snobol4.c` drops `:stno`; the AST attr is read at `driver_call.c:153`). The IR node struct (`src/contracts/IR.h`) has `ival`/`dval`/`counter`/`state` per-opcode fields but no dedicated stno slot.

**ACCEPTANCE (the whole goal):** `PARTICIPANTS="spl scr" SCRIP_RUN_FLAG=--run bash scripts/test_monitor_3way_sync_step_auto.sh /tmp/mdiv.sno` reports the FIRST divergence at the `$nm = vl` statement — SPITBOL `a`=`hello`(STRING) vs SCRIP `a`=``(NULL) — a SEMANTIC divergence, with matching LABEL/VALUE granularity up to that point. (`/tmp/mdiv.sno`: a DEFINE'd `setit(nm,vl)` whose body is `$nm = vl`, called as `setit("a","hello")`, then `OUTPUT = "a=" a`.)

---

## ▶ RUNG: MON-RE — re-home the sync-step taps onto modes 3/4

Each step gated on `make scrip` rc=0 (never a broken commit) + the named behavioral check. The taps are `MONITOR_BIN`-guarded (read env once at startup into a global; zero emission + zero overhead when unset → crosscheck/bench unaffected). Template-only / four-Greek-port / both-medium per RULES.md. Regenerate benchmark/feature/demo `.s` only after MON-RE-3 (the first codegen-touching step) and confirm they are byte-identical with `MONITOR_BIN` unset (the guard makes the default path unchanged).

### Steps
- [x] **MON-RE-0 — harness default mode.** `scripts/test_monitor_3way_sync_step_auto.sh`: scrip participant defaulted `--interp` (deleted) → `--run`. DONE this session. (Still TODO sub-fix: the `${MONITOR_PM:+...}` `bin/sh` Bad-substitution — force `#!/usr/bin/env bash` invocation / guard the expansion.)
- [x] **MON-RE-1 — `g_monitor_bin` startup flag (runtime-only, behavior-neutral).** DONE (SCRIP `4686e00`, 2026-06-26). `g_monitor_bin` global in `core.c`; behavior byte-identical.
- [x] **MON-RE-2 — carry stno into IR.** DONE (SCRIP `4686e00`, 2026-06-26). `IR_exec_t stno` sidecar in `IR.h`; `--dump-ir` shows stno on statement-entry nodes.
- [x] **MON-RE-3 — LABEL tap in the native statement-entry box.** DONE (SCRIP c8db891, 2026-06-26). The tap is emitted in the FLATTENER (codegen_gvar_flat_chain_body in emit_bb.c), NOT the bb_succeed leaf — the flattener COALESCES IR_SUCCEED nodes (gvar_chain_resolve_stmt skips them) so bb_succeed() never fires in modes 3/4. Mechanism: a parallel nstno[] array tracks each work-box stno, populated during BFS by gvar_chain_skip_stno() (returns the stno of the IR_SUCCEED skipped past); when g_monitor_bin && nstno[i]!=0 the per-node loop calls extern-C bridge emit_mon_label_tap(stno) (bb_succeed.cpp) emitting mov rdi,stno; call mon_emit_label_bin. EMIT-TIME GATED on g_monitor_bin: the compiler core_lib_init() runs before emit in BOTH modes 3+4, so the tap is emitted ONLY when MONITOR_BIN set at compile time -> .s byte-identical with monitor off (verified arith_loop/mixed_workload/table_access md5 identical HEAD-scrip vs MON-RE-3-scrip). Gate MET: crosscheck --compile PASS=170 FAIL=85 / --run PASS=149 FAIL=112 / DIVERGE 21 — fail set BYTE-IDENTICAL to pristine HEAD (same script on /tmp/scrip_HEAD gave identical numbers+lists; zero regressions). 2-way spl-scr monitor on /tmp/mdiv.sno now ADVANCES: steps 1+2 AGREE (LABEL stno=1 DEFINE, LABEL stno=3 MAIN), step 3 DIVERGES with the bug BRACKETED — SPITBOL @3 CALL setit (enters the call) vs SCRIP LABEL stno=2 (falls through to proc-body label WITHOUT the CALL frame). .s artifacts brought current (pre-existing drift, NOT MON-RE-3 — default-path output proven identical to HEAD).
- [x] **MON-RE-4 — VALUE tap on global store.** DONE (SCRIP a136452, 2026-06-26). Added mon_emit_value_bin(name, DESCR_t) to core.c (after mon_emit_label_bin): skips kw_trace/comm_var guards, goes straight to mon_send_bin(MWK_VALUE,...) with type/payload dispatch. Wired into rt_gvar_assign_str/int/var/descr in rt.c — each calls mon_emit_value_bin(name, d) after NV_SET_fn, gated on g_monitor_bin. Runtime-only change: .s byte-identical (verified md5). Gate MET: crosscheck PASS=170/85 FAIL-set IDENTICAL to HEAD. 2-way spl-scr monitor on /tmp/simple_assign.sno: steps 1+2 AGREE (LABEL stno=1, VALUE X=STRING(5)=hello); step 3 diverges on protocol ordering (SPITBOL advances to LABEL stno=2 before SCRIP sends second VALUE) — this is expected MON-RE-4 granularity; the VALUE wire event is confirmed on both sides at step 2. mon_emit_value_bin NOT yet wired to GVA inline-store path ([rbx+k*16] direct writes bypass rt_gvar_assign_*); that tap belongs in MON-RE-4b or the NRG rung when GVA inline stores are instrumented. NOTE: rt_gvar_assign_var changed to materialize DESCR_t before NV_SET_fn so the value is available for the tap.
- [x] **MON-RE-5 — CALL/RETURN taps on function boundaries.** DONE (SCRIP `93990cc`, 2026-06-26). Added `mon_emit_call_bin(fname)` / `mon_emit_return_bin(fname, retval)` to `rt.c` (declared in `core.h`): these temporarily raise `kw_ftrace=1` to bypass `comm_call`/`comm_return`'s ftrace gate, emit the MWK_CALL/MWK_RETURN event, then restore `kw_ftrace`. Wired into `rt_call_named_proc`, `rt_call_proc_direct`, `rt_call_named_proc_sl` — all gated on `g_monitor_bin`. Gate: crosscheck `--run PASS=149 FAIL=112`, `--compile PASS=170 FAIL=85`, byte-identical to HEAD.
- [x] **MON-RE-6 — ACCEPTANCE.** DONE (SCRIP `d813b92`, 2026-06-26). 2-way `spl scr` on `/tmp/mdiv.sno` steps 1-8 now AGREE: LABEL 1, LABEL 2, LABEL 4, CALL setit, LABEL 3, VALUE a=STRING(5)=hello, RETURN setit, LABEL 5. Step 9 diverges on END-label only (SPITBOL LABEL stno=6 vs SCRIP END — benign, END not lowered to IR stno). **Semantic acceptance MET: `$nm = vl` semantic divergence (the original target bug) is GONE.** Root causes fixed this session: (1) `gvar_chain_skip_stno` took first stno in chain instead of last → fixed to collect ALL stnos via `gvar_chain_collect_stnos()`; per-node `nstno_extra[8]` array, runtime dedup prevents duplicate LABEL taps across flat bodies; (2) `$nm = vl` (TT_INDIRECT + TT_VAR repl) returned NULL from `lower_stmt_body` → proc body γ chained to next main stmt → setit executed MAIN IR_CALL instead of its own body; fixed by adding `IR_INDIRECT_ASSIGN_VAR` lowering + BB template `bb_indirect_assign_var.cpp` + runtime `rt_indirect_assign_var()` (NV_GET val_name, NV_SET target, VALUE tap); (3) `comm_call/comm_return` fprintf suppressed when `g_monitor_bin` set (monitor tap raises kw_ftrace=1 only for wire-send). Gate: crosscheck --run PASS=149 FAIL=112 / --compile PASS=170 FAIL=85 byte-identical to HEAD.

**Prereq reads (PLAN.md step 7 — touches codegen + per-statement emission):** `MONITOR-BINARY-DESIGN.md` (binary wire spec), `ARCH-SCRIP.md` §Execution modes + §Isolation invariants (no SM/BB walk at runtime — the taps are EMITTED calls, not graph walks, so they comply), `ARCH-x86.md` §Flat-BB-ABI, `src/emitter/bb_regs.h`, `src/runtime/core/core.c` (the `mon_send_bin` family + `MONITOR_READY_PIPE` block), `src/driver/driver_call.c:150-165` (the mode-2 reference tap), `scripts/monitor/monitor_wire.h` (record layout), `scripts/monitor/monitor_sync_bin.py` (the controller).

**Companion tool (harness repo):** `harness/probe/probe.py` (`&STLIMIT`+`&DUMP=2` frame replay, bisect-divergence) is the OFFLINE alternative — it needs scrip mode-3/4 to honor `&STLIMIT` (count+abort) and `&DUMP=2` (var-table dump), NEITHER of which mode-3 currently does (verified). Lower priority than MON-RE because it requires more new native code than re-homing existing taps; tracked here for when MON-RE lands and a no-barrier replay is wanted.


---

# ▶▶▶ NEXT SESSION — START HERE (session 30, next date)

**MON-RE-6 LANDED (SCRIP `d813b92`, session 29, 2026-06-26).** 2-way monitor spl vs scr on `/tmp/mdiv.sno` now agrees through 8 steps: LABEL 1/2/4, CALL setit, LABEL 3, VALUE a=hello, RETURN setit, LABEL 5. Semantic acceptance met. Root causes fixed: (1) stno-chain collection (gvar_chain_collect_stnos — ALL stnos per chain, runtime dedup); (2) `$nm = vl` was NULL-returning from lower_stmt_body → proc body executed MAIN body's IR_CALL instead of indirect assign; fixed via IR_INDIRECT_ASSIGN_VAR lowering + BB template + runtime + VALUE tap; (3) comm_call/comm_return fprintf suppressed under g_monitor_bin. Remaining gap: END-label (step 9: SPITBOL LABEL stno=6 vs SCRIP END) — benign, END not in IR stno chain.

**▶ NEXT MOVE: RUNG 1 — climb the crosscheck fail set STATIC-FIRST (read .ref + .s, one stab, verify vs .ref; monitor only on a failed stab). 410-413 (arith in call-arg) CLOSED (SCRIP `795eaef`). 310/311/312 (concat in call-arg) CLOSED (SCRIP `bc18352`) — value-concat `'a' 'b'` as a call arg lowers to an IR_SEQ node (dval=1.0, two sub-arg-blocks) that hit `flat_drive_gvar_seq_passthrough` (no-op) → varslot garbage; fixed via new `rt_concat_parts_d` (DESCR-returning concat) + IR_SEQ exclusion in `gvar_drive_call_arg_slots` + IR_SEQ concat arm in `marshal_call_arg` (flatten→parts-on-frame→call→store); also gave `gvar_seq_flatten` IR_LIT_F support and strdup'd numeric parts (strtab interns by pointer + dumps lazily, so reused static bufs corrupted earlier refs: `X=1 2;Y=3 4`→`34`/`34`). Crosscheck set-level diff: m4 FAIL 79→76 (only the 3 leave, none enter), DIVERGE 22 unchanged, run 156→159, compile 176→179, zero regressions. Next lower-risk sub-rungs: 210-213 (indirect `$X` ref/assign), 091-095 (array/table create/access). Lon pivot 2026-06-27.**

---

## ▶ PRIORITY RUNG (session 29, PRIORITY 1): DEMO-PAT — claws5 + treebank mode-4 PASS + benchmarked

**WHY (Lon):** claws5 and treebank are PATTERN-HEAVY. SPITBOL *interprets* patterns (graph-walk + backtrack history stack, manual Ch.18 "Pattern-match algorithm" — a pushdown stack remembers alternatives, cursor pops on fail). SCRIP *compiles* the backtracking into four-port native control flow (the γ/ω/β edges ARE baked jumps; no history stack at runtime). That is SCRIP's structural advantage — already visible (pattern_bt 0.77×, SCRIP beats SPITBOL). Landing these two demos + benchmarking them proves the home-field win on real corpus programs.

**GROUND-TRUTH DIAGNOSIS (session 29, scrip built + RUN — NOT inferred; oracle NOT in scope, no x64 token).** Both demos HANG in BOTH modes (mode-3 `--run` and mode-4 `--compile` share the pattern codegen; both exit 124 timeout, zero output). The OLD `GOAL-SNO-CLAWS5.md`/`GOAL-SNO-TREEBANK-*.md` "PASS" claims are STALE — they describe the now-DELETED `--interp` mode (modes 1/2, `src/driver/interp.c`, C Byrd boxes `bb_seq`/`bb_bal`); that interpreter is gone. Minimal repros (`/tmp/rep/t1`–`t9`, recreate from this list) localize the gaps:
- **t4/t5/t7/t9 = MATCH OK, NO HANG:** stored ARBNO + alternation + POS/RPOS + variable csets (SPAN/NOTANY/BREAK/ANY of DIGITS/UCASE) + `' '` separator all match correctly on real claws lines. **The pattern STRUCTURE works. The match itself does NOT hang.**
- **GAP-1 (ROOT CAUSE of the hang) — deferred-eval function calls as capture targets `(epsilon . *FN())` NEVER EXECUTE.** t6/t8/t9: the side-effect counter stays 0 — `*new_sent()`/`*add_tok()` silently no-op. Both demos build their ENTIRE data structure (`mem` table / parse stack) via these calls. They don't fire → data stays empty → the downstream pretty-printer (`pp_mem`'s `pm_cnt_loop`: `ns=ns+1; ssk[ns,1] :S(pm_cnt_loop)` over `SORT(empty)`) spins forever → THE HANG. Fix GAP-1 and the hang dissolves because the data populates.
- **GAP-2 — captures (`.`) inside an ARBNO repeated body don't COMMIT.** t7: `wrd`/`tag` come back EMPTY after a matching ARBNO. Independent of GAP-1. (D3 commit-ring must truncate-to-mark on ARBNO β-reentry and flush at overall-match γ.)
- **GAP-3 (related, lower priority — demos use STORED patterns so it doesn't block them) — inline non-literal pattern in SCAN context bombs:** t1/t2 → `BOMB bb_scan: mode-3 non-literal pattern needs native PB-RB graph (rt_scan deleted)`. Same family; fix opportunistically.
- **treebank ADDITIONAL gaps (beyond claws5):** GAP-4 recursive deferred pattern eval `*group` (a pattern var referenced via `*` inside its own def — recursive descent); GAP-5 `BAL` in built patterns; GAP-6 EVAL-built patterns (`Push_list = EVAL('epsilon . *push_list(' vs ')')` — runtime-constructed pattern spliced into the match); GAP-7 user `DATA` types (`DATA('list(head,tail)')`, M4-DATA).

**SEQUENCING:** claws5 FIRST (needs only GAP-1 + GAP-2). treebank SECOND (claws5 fixes + GAP-4..7). Each step gated on `test_crosscheck_snobol4.sh` byte-identical to HEAD (zero regressions) + the named repro/demo behavior.

### Phase A — claws5 (GAP-1 + GAP-2)
- [ ] **DP-0 — oracle + mode-4 demo harness + bench skeleton.** ✅ ORACLE IN HAND (session 29): `x64` SPITBOL cloned PUBLIC, no token (`git clone https://github.com/snobol4ever/x64`; `x64/bin/sbl -b` works for general programs — verified hello + arith). ⛔ BUT `sbl` does NOT run claws5/treebank: this `sbl` build rejects the `-P` memory flag they need AND `sbl -f` is broken on them (old goal note). **claws5/treebank oracle = SPITBOL** (`sbl -b`) on programs it accepts; `claws5.ref` (SHORT 95-line ref, sentences 1–4) remains the acceptance gate. Still TODO: `scripts/run_demo_mode4.sh` (crosscheck recipe `--compile→gcc -c→gcc -lscrip_rt -lgc -lm→run`, already prototyped at `/tmp/m4run.sh`) + `scripts/test_3way_demo_snobol4.sh` skeleton. No codegen change.
- [ ] **DP-1 — deferred-call-in-capture EXECUTION (the root-cause fix).** **EXACT DIAGNOSIS (session 29, AST-confirmed via `--dump-ast`): `(epsilon . *FN())` parses to `(TT_CAPT_COND_ASGN <pat> (TT_DEFER (TT_FNC FN)))` — the capture target `c[1]` is a `TT_DEFER` node, NOT a `TT_VAR`. BOTH lowering paths take the target as a STATIC string and DROP the deferred expr:**
  - inline scan path — `lower_snobol4.c:308` (`case TT_CAPT_COND_ASGN`): `vn = c[1]->v.sval` → `IR_LIT(nd).sval = vn`.
  - stored/freeze path (the one claws5 hits — `claws = …; src claws`) — `lower_snobol4.c:~576` (`sno_build_leaf_ir`, `IR_PATTERN_CAPTURE`): `IR_LIT(cap).sval = c[1]->v.sval`.
  When `c[1]` is `TT_DEFER`, `->v.sval` is `""`, so FN is never lowered/evaluated → side effect lost (t6/t8/t9: counter stays 0). The runtime write `rt_cap_assign_cursor(varname,sδ,cδ,is_imm)` (`bb_match_capture.cpp`) only accepts a BAKED name — **so this is NOT a 1-liner.**
  **FIX (both paths + runtime):** when `c[1]->t == TT_DEFER`, (a) lower its inner expr (`c[1]->c[0]`, the `TT_FNC`/expr) as a value-producing chain via the stamped EVAL/`run_code_chain`/`dyn-goto` rail; (b) at capture-commit (overall-match γ for `.`; submatch for `$`), RUN that chain (fires FN's side effects), take its return as the assignment NAME; (c) write the matched substring to that name. Add a runtime capture-write variant that accepts a computed name (or runs the deferred chain) — current `rt_cap_assign_cursor` is name-only. ⛔ needs **nv set** ledger STAMP (REQUESTED) for step (c). NOTE: in claws5/treebank the returned name is throwaway `dummy` (value=null) — the POINT is FN's side effect — so step (c) is harmless-but-required; the essential behavior is (a)+(b) EVALUATE the deferred target. Gate: t6/t8/t9 counters increment (`new_sent#`/`add_tok#` > 0); no crosscheck regression.
- [ ] **DP-2 — capture-commit inside ARBNO.** `.` captures in the ARBNO repeated body commit on overall success (D3 ring: SAVE records {ring-mark, δ} per iteration; WRITE appends {nv-ref, sδ, eδ} at element-γ; β-retreat truncates to mark; CAPTURE_COMMIT flushes at match-γ). Gate: t7 returns non-empty `wrd`/`tag`; no regression.
- [ ] **DP-3 — claws5 end-to-end.** mode-4 output byte-matches the DP-0 oracle ref on `claws5.input` (small), then full `CLAWS5inTASA.dat` (989 lines → 5622-line ref); NO hang (terminates < TIMEOUT). Regenerate `claws5.s` artifact (real codegen, no bomb stub). Gate: crosscheck byte-identical; claws5 diff=0.
- [ ] **DP-4 — claws5 BENCHMARK (the home-field proof).** Run claws5 mode-4 vs SPITBOL (`sbl -b`) via `test_3way_demo_snobol4.sh`; record wall-ms ratio in this goal. EXPECTATION: pattern-heavy → SCRIP competitive-or-faster (the four-port-compiles-the-backtracking thesis). Record the honest number whatever it is.

### Phase B — treebank (claws5 fixes + GAP-4..7)
- [ ] **DP-5 — user DATA types in mode-4 (M4-DATA).** `DATA('list(head,tail)')` constructor + field selectors `head(x)`/`tail(x)` + `list(a,b)`. Gate: a `list` round-trips; treebank's `stk = list(frame_id, stk)` / `head(stk)` / `tail(stk)` work.
- [ ] **DP-6 — BAL in built patterns.** The B7 BAL sub-rung: balanced-paren scan (depth counter in per-box scratch, per-char ()-balance in α, regenerating). Gate: `('(' BAL ')') . item` extracts a balanced group; `spat` in treebank matches one s-expression.
- [ ] **DP-7 — recursive deferred pattern eval `*group`.** A pattern variable referenced via `*` inside its own definition: deferred DT_P fetch + real β re-entry into the embedded sub-graph (B10 + S3 instance re-entry). ⛔ recursion guard (manual Ch.8: a pattern recursing without consuming subject overflows — match real `icont`/sbl semantics: progress before recursion). Gate: nested s-expression `((a b) c)` parses to correct depth.
- [ ] **DP-8 — EVAL-built patterns.** `Push_list = EVAL('epsilon . *push_list(' vs ')')` — runtime CODE/EVAL produces a DT_P that is spliced into the enclosing pattern at match time. Reuses the stamped EVAL rail + DP-1 deferred-call-in-capture. Gate: `Push_list('tag')`/`Pop_list()`/`Push_item('wrd')` fire during the match; stack builds.
- [ ] **DP-9 — treebank end-to-end + BENCHMARK.** mode-4 byte-matches oracle on `treebank.input` (regenerate ref against live oracle per DP-0); regenerate `treebank-array.s`; add to `test_3way_demo_snobol4.sh`; record wall-ms ratio. Gate: crosscheck byte-identical; treebank diff=0; bench number recorded.

**Prereq reads (PLAN.md step 7 — touches per-box pattern state):** `SNOBOL4-5STAGE-OWNED-BUILD.md` (D3 capture-commit ring, B7 BAL, B8 capture-in-built, B9 ARBNO, B10 DEFER-IN-BUILD — DP-1/2/6/7/8 ARE those rungs, re-sequenced demo-first); ARCH-SNOBOL4.md §Native pattern; `src/emitter/bb_regs.h`; `src/runtime/rt/bb_pat_build.cpp`; `src/emitter/emit_core.c` matcher dispatch; the permission ledger in SNOBOL4-5STAGE (DP-1 needs **nv set** STAMPED — currently REQUESTED).

---

## ▶ PRIORITY RUNG (session 29, PRIORITY 2): NRG — Native Register Codegen ("beat the interpreter on statements")

**THESIS (the reframing that makes "true compiler beats interpreter" tractable).** SPITBOL is NOT a fetch-decode-execute interpreter — for statements it is an **indirect-threaded-code VM** (manual history ch.: "compiling to an intermediate language of indirectly threaded code … a highly optimized run-time system then interprets the thread"). Threaded dispatch ≈ ONE indirect branch per op (`*next++`); no decode, no central loop; primitives are hand-tuned assembly. So SCRIP CANNOT win by "removing the dispatch loop" — threading already removed it. SCRIP currently LOSES on statements (15/16 benchmarks) because it replaced the cheap threaded NEXT (one indirect branch) with an EXPENSIVE PLT **call** per primitive (full System V convention) — *worse than threading*. NRG-A merely restores PARITY (inline → no call boundary). The ONLY way to BEAT threaded code is the one thing a threaded VM structurally cannot do: **specialize to the program** — keep a proven-typed value in a register and emit raw machine ops, with NO per-op tagged-descriptor load/store and NO per-op type re-check. (Patterns are the OTHER battleground and SCRIP already wins there — see DEMO-PAT; this rung is statements only.)

**EVIDENCE (assembly-traced, session 29).** `arith_loop.s` one iteration of `N=N+1; N=LT(N,1e6) N`: `N` is loaded from `[rbx+16/24]` and its `DT_I` tag re-checked (`cmp edx,6`) **twice** (LT box `bb13` + arith box `bb14`), plus a dead store-then-reload of slot 80 and a slot-96 round-trip — ~25 instrs where a register-resident DT_I counter needs **3** (`cmp r14,1e6; jge done; add r14,1`). `func_call.s` INC body (`INC=N+1`): **three** PLT calls — `call NV_GET_fn` (fetch N, result DEAD/unused), `call rt_gvar_get_int` (fetch N AGAIN), `call rt_gvar_assign_int` (store) — to add 1. Plus `rt_call_proc_direct`'s ~15-op save/restore protocol per call. SPITBOL threads all of this with values in registers and locals at known offsets.

**Each sub-rung independent; gate = `test_crosscheck_snobol4.sh` byte-identical (PASS=171 FAIL=84, fail SET unchanged, every stdout identical) + both-medium (mode-3==mode-4) + regenerate benchmark/feature/demo `.s` + A/B wall-ms on its target. Template-only / four-Greek-port / ledger-gated per RULES.** Order A → E → B → C → D (cheap CFG/dataflow cleanups first; they de-risk the register allocator by removing the redundancy that would confuse it; B is the lever that flips arith-class benchmarks; C/D kill the call cluster).

### NRG-A — VN: local value-numbering / redundant-load elimination (do FIRST — cheapest, broad)
- [ ] **VN-0** — within a straight-line (non-β-reentrant) box chain, value-number `[rbx+k*16]` loads + their `DT_I` tag-checks; a second identical load reuses the register. Kills arith_loop's 2nd N-load + 2nd tag-check, INC's dead `NV_GET_fn`.
- [ ] **VN-1** — drop store-then-reload of the same frame slot (`mov [r12+s],rax; … mov rax,[r12+s]`) and dead `IR_VAR` boxes whose slot is never read.
- [ ] **VN-gate** — byte-identical crosscheck; A/B arith_loop, op_dispatch, func_call.

### NRG-B — REG: register residency + static type tracking (the DEEPEST win — the only thing threading can't do)
- [ ] **REG-0** — liveness + "single-type-throughout" analysis: mark a scalar DT_I throughout a loop/body when assigned only by arithmetic, no EVAL/CODE/indirect-assign/I/O-assoc to it (reuse FZ invariance-proof + GVA DT_I guard).
- [ ] **REG-1** — allocate the proven counter to a callee-saved reg across the loop; emit `add/cmp/jcc` directly; spill to `[rbx+k*16]` only at loop exit + escape edges (spill is already-stamped GVA territory — NO new ledger). Target: arith_loop inner loop → 3 instrs.
- [ ] **REG-2** — extend to function-body locals proven DT_I (fibonacci `N`, INC `N`).
- [ ] **REG-gate** — ⛔ register value re-materializable at every β/ω edge + fallback; verify vs `sbl -b` arith_loop/fibonacci/mixed_workload. A/B arith_loop, fibonacci.

### NRG-C — INL: leaf-function inlining (eliminates the call protocol for tiny procs)
- [ ] **INL-0** — inlinability analysis in lower (≤N stmts, non-recursive, statically resolved — DCR-2 `__proc[]` already proves the static-call set).
- [ ] **INL-1** — splice callee four-port graph at the call site, param→arg substitution, return var → local temp. `R=INC(R)` → `R=R+1` inline.
- [ ] **INL-gate** — byte-identical; recursion guard; A/B func_call, func_call_overhead.

### NRG-D — PROTO: specialized call protocol (for non-inlinable/recursive calls)
- [ ] **PROTO-0** — emit per-call-site block save/restore through the known param/return cells (cells resolved at preamble à la DCR-2); no per-call loop, no fastpath re-check. ⛔ needs **nv set** ledger STAMP (currently REQUESTED).
- [ ] **PROTO-gate** — byte-identical; A/B fibonacci (recursive), roman.

### NRG-E — BOPT: branch chaining (scaffolded `src/opt/branchopt.c` `bopt_chain` — UNWIRED; Makefile compiles but does not link it)
- [ ] **BOPT-1** — wire `bopt_chain` as a LOWER→EMITTER pass + cycle guard (generator self-loops / `to.code` back-edges must not collapse). ⛔ honor the prior crash: γ-spine doubles as operand-recovery; rechain ONLY edges proven not to shorten an operand-recovery walk (gate on the deterministic chains VN proved safe).
- [ ] **BOPT-2** — dead-BB drop + fall-through layout (common path takes no branch).
- [ ] **BOPT-gate** — byte-identical; emitted-jump-count delta + A/B across all 16.

**Prereq reads:** the uploaded Proebsting four-port paper (§4 templates, §5/Figs 1–2 optimization — **persist to repo `docs/`**); ARCH-x86.md §Flat-BB-ABI + §Boxes-are-stackless; `src/lower/lower_snobol4.c`; `src/emitter/emit_bb.c` (FILL/port machinery + flattener); `src/emitter/BB_templates/x86_asm.h`.
---

## ▶ RUNG: SCAN-CLASS — specialize the cset-matching scanners (fold → table → unroll)

**GROUND TRUTH (session, emitter-verified — NOT inferred).** The literal-vs-variable dispatch and RIP-relative constant-folding ALREADY EXIST for these primitives:
- `lower_snobol4.c:522` routes SPAN/ANY/NOTANY/BREAK/BREAKX/LEN/POS/RPOS/TAB/RTAB down a LITERAL arm (arg ∈ {QLIT,ILIT,CSET}) vs a VARIABLE arm.
- POS/RPOS literal integers are ALREADY folded to immediates: `bb_match_pos.cpp:17` `cmp r14d,<imm>`; RPOS `sub ecx,<imm>; cmp r14d,ecx`; `bb_scan_pos.cpp:15` `cmp64 r14,<imm>`.
- ANY/SPAN/BREAK literal csets are ALREADY sealed RIP-relative: `bb_scan_any/many/upto` literal arms emit `ROQ(0)` + `.string`. They still `strchr` the sealed string per subject char — the inner-loop cost SCAN-TABLE/SCAN-UNROLL attack.
- NSPAN does NOT exist in `src/` (no token/IR/template) — a NEW primitive, not a folding task.

So constant-folding-into-RIP is largely DONE. Remaining: (1) a coverage AUDIT; (2) the inner-loop algorithm (table/unroll), PARKED below per Lon (2026-06-27); (3) **the VARIABLE-operand TWIN of each primitive — the SCAN-GEMINI rung below (Lon directive 2026-06-27: "every BB here should have a gemini").**

---

## ▶ RUNG: SCAN-GEMINI — every scan/match primitive gets its variable-operand TWIN (Lon 2026-06-27)

**THE GAP (session 30, RUN-confirmed — NOT inferred).** Each scanner primitive currently has a LITERAL box (operand folded: integer→immediate `cmp`, cset→`.string` sealed RIP-relative reached via `ROQ(n)`/`lea [rip+__]`). Its VARIABLE twin (operand is a `TT_VAR`/`TT_KEYWORD` resolved at runtime) is MISSING for all but SPAN — and even SPAN's twin (`IR_MATCH_SPAN_VAR` + `bb_match_span_var.cpp`) is UNREACHED in the common capture case. **Live proof:** `S ? SPAN(DIGS) . M`, `ANY(CS) . M`, `NOTANY(CS) . M`, `BREAK(CS) . M` (CS/DIGS a variable) ALL bomb `libscrip_rt: BOMB — bb_scan: mode-3 non-literal pattern needs native PB-RB graph (rt_scan deleted)`; oracle (`sbl -bf`) returns `123`/`1`/`a`/`abc` respectively.

**THE MECHANISM (emitter-traced).** Lowering ALREADY tags the variable case (`lower_snobol4.c` TT_SPAN/ANY/NOTANY/BREAK/BREAKX/POS/RPOS/TAB/RTAB/LEN arms): variable arg → `IR_LIT(nd).sval = <VARNAME>` + a marker (`dval=1.0`/`2.0`, or SPAN's `ival=1`); literal arg → `sval = <cset string>` or `ival = <int>`. Then `scan_pat_m3_native_safe()` (`emit_bb.c:2560`) returns 0 (forces the STORED/`bb_match_*` family instead of inline `bb_scan_*`) precisely when the marker is set (`dval!=0.0` for POS/LEN/TAB/RTAB/ANY/NOTANY/BREAK/BREAKX; `ival==1` for SPAN). In the match family ONLY SPAN has a `_VAR` opcode+template; the other seven fall through to their LITERAL template, which bakes the variable's NAME string as if it were the cset (cset prims) or reads a stale `ival` (int prims) → wrong result or the PB-RB bomb. **The fix is the missing twin per primitive + the routing that reaches it.**

**THE REFERENCE TWIN (the one that exists — mirror it).** `bb_match_span_var.cpp`: `lea rdi,[rip+VARNAME]` → `call rt_nv_cstr` (fetch the variable's cset string by name at runtime; `rt.c:98`) → store the `char*` to a claimed scratch slot (`bb_slot_claim(16)`) → the SAME inner `strchr` loop the literal SPAN uses, but `rdi` reloaded from the slot each char. FILL wiring at `emit_bb.c:3040` (`IR_MATCH_SPAN_VAR`: `op_name1 = sval(varname)`, `op_name2 = "bb_spanv"`, claim scratch). **Every cset twin is this shape; every int twin is the same minus the cset loop (fetch int via a numeric NV getter, then the primitive's `cmp`).**

### Sequencing (cset twins first — they unblock the pattern-heavy demos; SPAN reachability first since its template already exists)
- [ ] **GEM-0 — make the variable-cset pattern REACH the per-primitive native boxes (the prerequisite the twins sit behind).** **GROUND TRUTH (session 30, RUN-traced):** `SPAN(DIGS) . M` etc. bomb in `bb_scan_stmt.cpp:39` (`bb_scan: mode-3 non-literal pattern needs native PB-RB graph (rt_scan deleted)`), NOT in any per-primitive box. `bb_scan_stmt` is the WHOLE-STATEMENT scan box: it has a fully-literal fast path (`op_scan_pat_lit` set → one `call rt_scan_lit` with the whole pattern baked as a string) and bombs otherwise. A variable cset makes the pattern non-bakeable → `op_scan_pat_lit==NULL` → bomb. **So the pattern is NEVER decomposed into the per-primitive native match boxes where `bb_match_span_var` (and the GEM-1.. twins) live.** Therefore GEM-0 is the DECOMPOSITION/BUILD step, not a one-line op promotion: a non-literal `SUBJ ? PAT` must route to the native PB-RB built-graph path (the builder-BBs-that-build-BBs → generic `BB_MATCH` box, per ARCH-SNOBOL4.md "Native pattern architecture — modes 3 & 4") so the pattern's primitive boxes (`IR_MATCH_SPAN_VAR`, etc.) are actually emitted and run. This is the SAME root as DEMO-PAT GAP-3 ("inline non-literal pattern in SCAN context bombs"). `IR_MATCH_SPAN_VAR` being referenced-but-never-assigned in `src/` is the symptom: nothing builds the decomposed graph that would carry it. **Sub-steps:** (a) confirm/locate the native PB-RB build entry the literal path bypasses; (b) route `bb_scan_stmt`'s non-literal-pattern case into it instead of bombing; (c) ensure the marked-variable primitive (`ival==1`/`dval!=0`, `sval=varname`) lands as its `_VAR` box in the built graph. Gate: `/tmp/spanvar.sno` (`SPAN(DIGS) . M` → `123`) passes both modes; crosscheck fail set ⊆ HEAD (zero regressions); `.s` regenerated. ⛔ This is multi-file pattern-engine work (shares surface with DEMO-PAT DP-3/GAP-3) — budget a full session; do it MONITOR-first if a partial graph diverges.
- [ ] **GEM-1 — ANY_VAR twin.** New `IR_MATCH_ANY_VAR` opcode (IR.h) + `bb_match_any_var.cpp` (mirror span_var: `rt_nv_cstr` fetch → slot → ANY's single-char `strchr` test, success on match). Lowering: TT_ANY variable arm emits `IR_MATCH_ANY_VAR` (or normalize promotes `IR_MATCH_ANY` w/ `dval!=0`). FILL arm in `emit_bb.c` (claim scratch, `op_name1=varname`). Dispatch in `emit_core.c`. Gate: `ANY(CS) . M` → `1`; crosscheck ⊆ HEAD; both-medium (mode-3==mode-4); `.s` regen.
- [ ] **GEM-2 — NOTANY_VAR twin.** As GEM-1, inverted test (success when the char is NOT in the fetched cset). Gate: `NOTANY(CS) . M` → `a`; crosscheck ⊆ HEAD; both-medium; `.s` regen.
- [ ] **GEM-3 — BREAK_VAR twin.** As GEM-1, BREAK semantics (advance cursor until a char IN the fetched cset; cursor stops before it). `bb_match_break`'s literal loop, cset reloaded from slot. Gate: `BREAK(CS) . M` → `abc`; crosscheck ⊆ HEAD; both-medium; `.s` regen.
- [ ] **GEM-4 — BREAKX_VAR twin.** As GEM-3 plus BREAKX's retry-extend semantics (the two `strchr` sites in `bb_match_breakx.cpp`, both cset-reloaded). Gate: a BREAKX-of-variable program matches oracle; crosscheck ⊆ HEAD; both-medium; `.s` regen.
- [ ] **GEM-5 — POS_VAR / RPOS_VAR twins (integer).** `bb_match_pos` currently folds `op_ival`; the variable case (`POS(N)`/`RPOS(N)`, `dval=2.0`/`1.0`, `sval=varname`) needs an int-NV fetch (`rt_gvar_get_int(varname)` → register) then the SAME `cmp r14d,reg` (POS) / `mov ecx,r15d; sub ecx,reg; cmp r14d,ecx` (RPOS). One new opcode pair or a `op_name`-driven arm inside `bb_match_pos`. Gate: `POS(N)`/`RPOS(N)` with variable N match oracle; crosscheck ⊆ HEAD; both-medium; `.s` regen.
- [ ] **GEM-6 — TAB_VAR / RTAB_VAR twins (integer).** As GEM-5 for `bb_match_tab`/`bb_match_rtab` (the `cmp`/`mov32 r14d` and the RTAB `sub` use a fetched register instead of `op_ival`). Gate: `TAB(N)`/`RTAB(N)` variable match oracle; crosscheck ⊆ HEAD; both-medium; `.s` regen.
- [ ] **GEM-7 — LEN_VAR twin (integer).** `bb_match_len` variable-N twin (fetch int, `cmp`/advance by register). Gate: `LEN(N)` variable matches oracle; crosscheck ⊆ HEAD; both-medium; `.s` regen.
- [ ] **GEM-8 — scan-family variable arms (inline-context twins).** `bb_scan_many` (SPAN), `bb_scan_upto` (BREAK), `bb_scan_tab` already-slot — add the `var cset`/`var int` arm to each inline scanner the way `bb_scan_any` already carries BOTH arms (literal via `ROQ`, variable via `FRQ(op_sa+8)`/`rt_nv_cstr`), so a marked-variable primitive in an inline (non-stored) `S ? ... = ...` context need not be forced into the stored family by `scan_pat_m3_native_safe`. Then RELAX `scan_pat_m3_native_safe` to allow the now-handled variable inline shapes. Gate: a variable-cset inline replace (`S ? SPAN(var) = X`) matches oracle in both modes; crosscheck ⊆ HEAD; both-medium; `.s` regen.
- [ ] **GEM-9 — GEMINI completeness gate (audit + prison).** Grep proof every primitive has BOTH a literal box and a variable box reachable: a script `test_gate_scan_gemini.sh` that compiles one literal + one variable program per primitive and asserts (a) neither bombs, (b) both match `sbl -bf`. Wire into the SNOBOL4 gate. This is the rung's completion test.

**Prereq reads (PLAN.md step 7 — per-box pattern state + per-statement emission):** `bb_match_span_var.cpp` (the reference twin), `lower_snobol4.c` TT_SPAN/ANY/NOTANY/BREAK/BREAKX/POS/TAB/RTAB/LEN arms (the literal-vs-variable tagging), `emit_bb.c:2560` `scan_pat_m3_native_safe` + `:3035` the FILL switch, `emit_core.c:371-383` the dispatch, `rt.c:98` `rt_nv_cstr`, `bb_regs.h`. NOTE: GEM overlaps SCAN-TABLE-2 (runtime-cset table) — the table is the FAST inner loop; GEM is the CORRECT one. Do GEM first (correctness), table later (speed); the table then drops into each `_var` twin's loop.

### SCAN-FOLD — audit + close constant-folding coverage (the only ACTIVE scan-class rung)
- [ ] **SCAN-FOLD-0 — coverage audit (no code change).** For ANY/NOTANY/SPAN/BREAK/BREAKX (× `bb_scan_*` inline AND `bb_match_*` stored/native families) and POS/RPOS/LEN/TAB/RTAB: confirm the literal arm seals its constant RIP-relative (cset via ROQ/.string) or immediate (integer via `cmp imm`), with NO frame load / NO runtime arg-eval on the literal path. Deliverable: table {primitive × family → folded? Y/N/site}.
- [ ] **SCAN-FOLD-1 — close any unfolded literal arm.** Any primitive the audit marks N (literal arg still frame-loaded) → seal RIP-relative/immediate like its siblings. Gate: crosscheck byte-identical; both-medium; regenerate only the closed primitive's `.s`.
- [ ] **SCAN-FOLD-2 — NSPAN (decision, not auto).** NSPAN (nullable span, ≥0) is unimplemented; adding it is a NEW primitive (parser token + lower + `bb_*nspan`, ≥0 loop-exit vs SPAN's ≥1), its own rung — NOT a folding step. PARK until Lon requests.

### SCAN-TABLE — baked character-class classifier (PARKED — Lon: "for later")
Replace the per-char `strchr(cset,ch)` (PLT call + O(cset-len) scan) in `bb_scan_any/many/upto/bal` (+ `bb_match_*` cset loops) with a baked classifier reached RIP-relative — the real inner-loop win.
- [ ] **SCAN-TABLE-0 — pick form.** 256-byte 0/1 table (`movzx eax,[r13+rcx]; cmp byte [rip+tbl+rax],0`) vs 32-byte bitmap (`bt`). Lean: 256-byte table for streamers (single indexed load). ⛔ char UNSIGNED (movzx 0–255) — bytes ≥128 (&ALPHABET) misclassify otherwise.
- [ ] **SCAN-TABLE-1 — literal cset → bake table into RO data, sealed adjacent, RIP-relative.** Build the 256-entry table at emit time from the literal cset; emit in the sealed RO region; rewrite the literal arm's inner loop to the indexed test. Add the x86 form to x86_asm.h (both-medium). Gate: crosscheck byte-identical; A/B SPAN/BREAK on string_pattern/pattern_bt; `.s` regenerated.
- [ ] **SCAN-TABLE-2 — runtime cset → built-once table (SPITBOL parity; bulk of the win).** Represent a cset VALUE as a 256-entry table built once when its string materializes, memoized on the descriptor; the variable arm's loop uses it. Covers `BREAK(WORD) SPAN(WORD)` (wordcount/claws5/treebank). ⛔ rebuild on cset reassignment. Gate: crosscheck byte-identical; A/B wordcount.

### SCAN-UNROLL — inline-compare / unrolled small literal csets (PARKED — Lon: "for later")
Tiny literal csets (≤~10 chars): skip the table, emit direct `cmp al,cN; je` chains (`SPAN(' ')`/`BREAK(',')`/`ANY('+-')` → one compare). Faster than the table load for the common short-cset case.
- [ ] **SCAN-UNROLL-0 — threshold + dispatch.** Choose N (≤10); literal cset len ≤N → unrolled-compare arm, else → SCAN-TABLE arm, else (variable) → table/strchr. 1-char fast path first (highest frequency).
- [ ] **SCAN-UNROLL-1 — emit unrolled compares per the primitive's loop semantics** (ANY = OR-of-compares→match; NOTANY = none-match→match; SPAN/BREAK = loop-exit condition). Both-medium. Gate: crosscheck byte-identical; A/B on a single-char-cset-heavy program.

**Sequencing (Lon).** SCAN-FOLD (audit) is small — folding is already in place. SCAN-TABLE-2 (runtime-cset table) holds the bulk of the inner-loop win; SCAN-TABLE-1 + SCAN-UNROLL cover the literal cases. All gated A/B (the win is MEASURED, not assumed); template-only / four-Greek-port / both-medium; `.s` regenerated per touched primitive.


---

**RPF + TABLE-WALK-FIX LANDED (SCRIP `8ef7412`, session 27, 2026-06-25).** Two PERF-CALL wins; gate PASS=171 FAIL=84 SKIP=6 (zero regressions, fail set byte-identical to HEAD), both-medium clean, all results match .ref. Artifacts regenerated (benchmark/feature/demo .s).

(1) **RPF — relop GVA-parity** (`bb_call.cpp`): `arith_opnd_a/b` gained a `gk_lb` param (default=-1, all existing callers unchanged → byte-identical output). `bb_call_relop_inline_str` passes `gk_lb=0/2` + calls `x86_begin()`. When the operand is a GVA global (k≥0): emits `mov rdx,[rbx+k*16]; cmp edx,DT_I; jne slow; mov reg,[rbx+k*16+8]`; falls through to existing `call rt_gvar_get_int` on miss. Same DT_I-guarded pattern as `bb_binop_gvar_arith.cpp`. Fibonacci GVA-guard count unchanged (frame param, correctly untouched). **A/B (best-of-3, mode-4 native, SCRIP-vs-SCRIP):** op_dispatch 248→19ms (13.1×), arith_loop 121→13ms (9.3×), var_access 1478→238ms (6.2×), func_call 5206→4157ms (1.25×), pattern_bt 328→264ms (1.24×), table_access 3244→2758ms (1.18×). Moderate wins where the relop is not dominant; zero effect where operand is a frame param.

(2) **Table get double-walk elimination** (`aggregates.c` + `core.h` + `pattern_match.c`): added `table_get_found(tbl,key,*found)` — one chain walk, explicit found flag. `subscript_get` DT_T: was `table_has()+table_get()` (2 walks); now `table_get_found()` (1 walk). Same dflt/NULVCL branches. table_access 2758→2410ms (1.14× this change; **3244→2410 = 1.35× combined** with RPF). result: 250500 correct.

**SPITBOL re-grounding NOT done this session** — `x64` oracle token not in scope. The SCRIP-vs-SCRIP speedups are solid. Honest inference: op_dispatch/arith_loop/var_access likely flip to faster-than-SPITBOL (prior ratios were 2.29×/2.90×/1.05×; the RPF drop is ~13×/9×/6×), but that needs oracle confirmation. SPITBOL re-grounding is the first task of the next session that has the `x64` token.

**▶ NEXT MOVE (session 28): DCR-2 — codegen-side proc resolution (the named open rung in the DCR ladder).** Replace the per-call `lea rdi,name; call rt_call_named_proc` with a baked proc index/cells resolved at preamble (`__proc[]` table, GVA-analogous), so the call site does `mov rdi,[rip+__proc+k*8]; call rt_call_proc_direct` — eliminates even the cache lookup. `emit_bb.c` IR_CALL arm + `lower_snobol4.c` (mark statically-resolvable `IR_CALL`s; keep by-name fallback for `$FN`/OPSYN/runtime-DEFINE). Gate: crosscheck byte-identical; further `func_call`/`fibonacci` delta. See DCR-2 step below.

**OPT rung status (session 27 investigation):** BOPT-1 (in-place γ/ω mutation) attempted, built, wired, crashed (`flat_drive_assign FATAL` — γ-spine is overloaded as operand-recovery structure; in-place edge mutation shortens the spine the operand-recovery walks). Quantified: 34/1686=2% collapsible branches corpus-wide, 0% in hot loops; 793 dead beta-resume stubs (size/build-time, not runtime). Safe forwarder chaining already done by `gvar_chain_resolve_stmt`. Copy-prop: 23 instances corpus-wide (~1/benchmark). **OPT rung is CLOSED as a perf lever.** `src/opt/branchopt.{c,h}` retained as dead-end record. Full analysis in `docs/BOPT-DESIGN.md`.

**KEYWORD-CONCAT BOMB FIXED (SCRIP `c6d8c28`).** `X = &UCASE &LCASE` (and any concat with a `TT_KEYWORD` operand) no longer bombs `bb_gvar_assign_concat: no parts (not flattenable)`. Root cause: `sno_seq_flatten_ops` did not flag `TT_KEYWORD` as `nonleaf`, so keyword operands fell through the foldable-leaf path (which accepts only `TT_QLIT`) and dropped into the unimplemented `IR_SEQ` runtime-concat path with zero `op_parts`. Fix: one line — add `t->t == TT_KEYWORD` to the `nonleaf` trigger, routing keyword operands through the already-proven `sno_concat_chain` binary-chain path (`IR_BINOP_CONCAT`). Gate: crosscheck PASS=171 FAIL=84, fail set byte-identical to pristine HEAD (zero regressions). `wordcount.s` feature artifact updated (was bomb stub, now real codegen). 5 new demo `.s` committed (arithmetic/counter/hello/pattern_test/porter — previously never generated). Note: `wordcount` closes the codegen bomb but still **hangs** in its inner match-replace loop (`NEXTW LINE ? WPAT =`) because `WPAT = BREAK(WORD) SPAN(WORD)` with runtime-computed `WORD` cset hits the same deep pattern-engine gap as `word1`–`word4`/treebank/claws5 (crosscheck fail set, broader pattern-engine work). Benchmark timing confirmed across all 16 benchmarks: PASS=15/16 (eval_dynamic = documented OOM, correct at low N). Mode-4 native vs mode-3: arith_loop 113ms/862ms (7.6×), op_dispatch 233ms/2008ms (8.6×), table_access 3153ms/7088ms (2.2×).

**▶ NEXT MOVE (session 25): DCR-2 — codegen-side resolution (drop by-name proc call entirely). See DCR-2 step below.**

**THREE-WAY COMPARISON — RE-GROUNDED post-DCR (session 27, 2026-06-25; DCR-3).** All 16 benchmarks run SCRIP mode-4 (AOT native) vs SPITBOL (`sbl -b`). Reproducible: `scripts/test_3way_snobol4.sh` (wall-clock ratio). **Correctness: 14/14 result-bearing benchmarks byte-identical across SCRIP and SPITBOL** (`arith_loop` and `indirect_dispatch` emit no `result:` line, so they are correctness-`?` not graded). `indirect_dispatch` remains the one known DIVERGENCE (`R = $FN(X)`, `FN='ADD1'`): SPITBOL ERRORS ("undefined function called"), SCRIP returns blank `R` — the divergence is in ERROR behavior, not a printed result, so no engine emits a comparable `result:` line; nothing gates it. **Performance (wall-ms ratio = SCRIP/SPITBOL): SCRIP is SLOWER than SPITBOL on 15/16, ≈parity or faster on 1.** Re-grounded ratios: arith_loop 2.90×, op_dispatch 2.29×, string_concat 10.01×, eval_fixed 8.16×, mixed_workload 12.11×, table_access 10.86×, roman 21.80×, **fibonacci 10.50× (was 23.1× — DCR HALVED it)**, string_pattern 10.35×, string_manip 17.22×, **func_call_overhead 6.62× (was 13.3×)**, **func_call 6.65× (was 14.2×)**, eval_dynamic 165.47×. var_access 1.05× (≈parity; was 0.77× faster — slipped to parity, measurement-sensitive at `-O0` gcc of the native `.s`). **Faster than SPITBOL on 1:** pattern_bt 0.77× (FZ path). **DCR EFFECT (the headline of this re-grounding):** the function-call cluster — the whole point of the DCR ladder — dropped from ~14–23× to ~6.6–10.5×: func_call 14.2×→6.65× and func_call_overhead 13.3×→6.62× (cell-cache + memoized cells, both ~2.6×), fibonacci 23.1×→10.50× (~2.2×). The A/B numbers (DCR-1 func_call 2.61×, fibonacci 2.07×) are confirmed at the whole-benchmark level. **roman barely moved (22.7×→21.80×)** — honest: roman's per-call cost is dominated by the pattern-match + `REPLACE`, not the call save/restore protocol DCR optimized, so the protocol win is a small slice of roman's work. **The "10×" headline is STILL inverted for general workloads — DCR narrowed the call cluster by ~2× but did not close it.** Root cause unchanged (assembly-traced): native control flow but a runtime PLT call per SNOBOL primitive that SPITBOL inlines/threads. eval_dynamic COMPLETES in ~72s (NOT OOM; the bench-script "CRASH" is its 30s timeout). The remaining PERF-CALL sub-rungs (AXS done; SAB, table-probe) inline the next primitives.

**FZ-5b LANDED (SCRIP `6141434`).** Match sites referencing a once-assigned invariant pattern variable now bake the sealed matcher head directly (RIPSEAL lea) and skip the per-match `rt_defer_get_pat_fn` fetch — the hot-loop win for string_pattern/pattern_bt (500k× fetch eliminated). Three pieces: (1) FZ-5a: `fz_inlinable_head()` once-assigned-invariant analysis in `lower_snobol4.c` — conservative proof (assigns==1 AND frozen head recorded AND no indirect-assign/EVAL/CODE/CONVERT in program); behavior-neutral foundation. (2) FZ-5b: `flat_drive` IR_MATCH_DEFER case in `emit_bb.c` stages `child_cache_get`/`child_cache_get_lbl` when `fz_inlinable_head` hits; `bb_match_defer.cpp` branches on `bb_child_fn`/`bb_child_lbl` presence — inline path bakes frozen head, fetch path unchanged. Reuses RIPSEAL lea (both-medium clean). Cross-language safe (NULL for non-SNOBOL4). Gate MET: crosscheck PASS=171 FAIL=84 SKIP=6, fail set byte-identical to baseline (zero regressions). `.s` artifacts updated: string_pattern/pattern_bt/mixed_workload benchmarks now show inline marker + zero `rt_defer_get_pat_fn` calls. FZ-5b timing MEASURED (session 24, A/B = inline-on vs forced-fetch baseline, 5-trial min self-ms): string_pattern 8557→7590ms (**1.13×**), pattern_bt 1125→401ms (**2.81×**). Spread is the mechanism working — pattern_bt is one match/iter so killing the per-match `rt_defer_get_pat_fn` dominates; string_pattern also runs the INNER concat/replace loop so the fetch is a smaller slice. Verified live in codegen: 0 `rt_defer_get_pat_fn` calls, old per-shape builders absent, both outputs byte-match `.ref`.

**FZ-4 (Option B) LANDED (SCRIP `6141434`).** Bare invariant captures (`PAT = BREAK(',') . W`) now freeze to `IR_REF_INVARIANT` — the general `sno_freeze_pat_graph_entry` path — retiring `bb_build_break_capture_blob`. Full deletion set: `bb_build_break_capture_blob`, `bb_build_break_cap_lit_blob`, `sno_break_cap_lit_graph`, `sno_freeze_break_cap_lit_bin`, `sno_freeze_break_cap_lit_text` (all removed from `bb_pat_build.cpp`). `bb_pattern_cat.cpp` / `bb_pattern_capture.cpp` reduced to passthrough-only (Raku keeps passthrough; SNOBOL4 pat_via_dtp builder arm removed). `emit_core.c` dead pat_via_dtp BREAK.VAR-LIT extraction collapsed to stub. Key correction vs goal-file premise: `bb_build_break_capture_blob` was NOT dead before this rung — bare buildable captures still routed through it; FZ-4 Option B REDIRECTED that path to freeze rather than simply deleting a dead function. Gate MET: crosscheck byte-identical, build clean.

**▶ NEXT MOVE: FZ-5b timing + GVA-4 or OPSINGLE — Lon decides.**


## ▶ PRIORITY RUNG (do FIRST, session 27): OPT — IR/codegen optimizer passes (Lon pivot, Proebsting four-port)

**PIVOT (Lon, 2026-06-25):** stop hand-inlining individual hot primitives (RPF relop-prefetch and SAB self-append are HELD). Beat SPITBOL *on its own terms* by adding the GENERAL optimizer passes that Proebsting's four-port paper — "Simple Translation of Goal-Directed Evaluation" (uploaded `8_Simple_Translation_of_Goal_Directed_Evaluation.pdf`; **add to repo `docs/` for persistence**) — explicitly prescribes. SCRIP's emitter IS that four-port scheme: every operator template emits `.start/.resume/.fail/.succeed` chunks wired by gotos; in the generated `.s` these are the Greek `α`(start)/`β`(resume)/`ω`(fail)/`γ`(succeed) labels and the `snoch0_n<k>_<port>` BB labels. The paper (§5, Fig 1→Fig 2) states the naive expansion "suffers from generating many simple copies and many branches to branches," and that "propagating copies and eliminating branches to branches (by branch chaining and reordering the code)" yields code that "closely resembles … two generic `for` loops." This is a per-`.s` win on EVERY generated function — the structural complement to the PERF-CALL ladder (which attacks per-primitive call cost; OPT attacks the wiring overhead between primitives).

**EVIDENCE (assembly-traced, session 27).** `arith_loop.s` / `op_dispatch.s` are saturated with jump-to-jump chains the four-port wiring creates by construction: e.g. `snoch0_n10_β: jmp snoch0_n13_α`, the pair `jmp snoch0_n14_α … snoch0_n11_β: jmp snoch0_n10_α`, and EVERY template tail is `jmp γ; β: jmp ω`. The ports are explicit IR edges (`nd->γ.node`, `nd->ω.node`, the `EMIT_PAIR_FILL(nd, lbl_γ, lbl_ω, lbl_β)` machinery in `emit_bb.c`), so they can be re-wired at the IR level BEFORE template expansion — collapsing each chain to ONE jump rather than peephole-patching the emitted text. Three passes, independent, in pipeline order:

### BOPT — Branch optimizer (IR→IR, NEW stage AFTER lower, BEFORE emitter)
The primary/immediate pass. Re-wire the four-port edges so a port targeting an unconditional-goto BB points directly at that goto's ultimate target (Byrd chaining), then drop the emptied BBs.
- [ ] **BOPT-0 — map IR ports → Byrd ports.** Confirm which IR field is which port (`α`=start, `β`=resume, `ω`=fail, `γ`=succeed) and how `flat_drive`/`EMIT_PAIR_FILL` realize them. Read ARCH-x86.md §Flat-BB-ABI + §Boxes-are-stackless, `emit_bb.c` FILL machinery, the flattener (`x86_uid`/`g_flat_node_id` in `x86_asm.h`). Deliverable: a written port→field table; no code change.
- [ ] **BOPT-1 — transitive goto-chaining.** New `src/opt/branchopt.c` (or a `src/lower/` post-pass) over the lowered graph: for each port edge whose target BB is body-empty except `jmp X`, redirect the edge to X. Union-find / pointer-chase with a **cycle guard** — `to.code` back-edges and generator self-loops must NOT collapse into an infinite redirect. This is the "branches to branches → one jump" core.
- [ ] **BOPT-2 — dead-BB + fall-through elimination.** After rechaining: drop BBs with no predecessors; merge `A: … jmp B` into `B` when A is B's sole predecessor and B can follow A (eliminate `goto next`). Layout reorder (paper's "reordering the code") = lay succeed-chains out as straight-line fall-through so the common path has no taken branch.
- [ ] **BOPT-3 — copy propagation.** Collapse the `t<node>.value ← child.value` temp-forwarding chains the four-port templates emit (uminus/plus/relop each allocate a temp that often just forwards a child's value; cf. paper Fig 2 propagating `to1.I` directly instead of materializing `to1.value`). Propagate so the consumer reads the source temp; dead-temp elimination follows.
- [ ] **BOPT-gate.** ⛔ pure CFG/copy rewriting — semantics MUST be preserved. `test_crosscheck_snobol4.sh` result byte-identical (PASS=171 FAIL=84, fail SET unchanged, every program's stdout byte-identical). Both-medium (mode-3 == mode-4). Regenerate + commit ALL benchmark/feature/demo `.s` (they WILL change — fewer jumps; that IS the win). A/B: emitted-jump-count + wall-ms delta on arith_loop, op_dispatch, fibonacci (executed-branch reduction → a speedup that helps all 16 benchmarks, unlike a single-primitive inline).

### PEEP — Peephole / common-subexpression (post-emitter, "maybe after the emitter")
Window pass over the emitter's pre-flatten op-list (PREFERRED — structured, not regex-on-text) or the text `.s` (fallback). Cleans residue BOPT cannot see at IR level.
- [ ] **PEEP-0 — peephole window.** Kill redundant `mov A,rax; mov rax,A` spill/restore round-trips (e.g. the relop operand spill in `bb_call_relop_inline_str`), `mov reg,reg` identities, dead stores (`mov X,_; mov X,_`), and `lea`/`mov` of an already-live value. Operate on the structured op-list before flatten.
- [ ] **PEEP-1 — sub-expression elimination (CSE).** Within a BB, reuse an already-computed value instead of recomputing it (same global loaded twice; same index recomputed). This is the "SUB-EXPRESSION OPTIMIZER" half; complements BOPT-3.
- [ ] **PEEP-gate.** Crosscheck result byte-identical; both-medium; regenerate `.s`; A/B timing.

### CFOLD — General constant folding (ALL expressions, not just patterns)
Today only invariant PATTERNS fold (PB-FZ). Extend folding to every expression kind.
- [ ] **CFOLD-0 — literal-expression fold in lower (or a fold pass feeding BOPT).** Fold compile-time-literal arithmetic (`2 + 3 → 5`), literal relops used as predicates (`LT(5,10)` → always-succeed null `""`; `GE(2,9)` → always-fail — which lets BOPT delete the dead arm), literal string concat (`'a' 'b' → 'ab'`), `SIZE('abc') → 3`.
- [ ] **CFOLD-1 — wire into BOPT.** A folded always-true/false relop becomes an unconditional edge → BOPT prunes the dead branch; fewer ops reach the emitter (smaller `.s`, fewer jumps).
- [ ] **CFOLD-gate.** ⛔ correctness: fold ONLY when operands are literals AND the op is side-effect-free AND the result matches SPITBOL semantics (integer width/overflow, number↔string coercion, the null-string-identity rule from the `str_concat_d` fix). Crosscheck byte-identical; each folded form verified against `sbl -b`.

**Prereq reads:** the uploaded paper (four-port templates §4; example + optimization §5 / Figs 1–2); ARCH-x86.md §Flat-BB-ABI + §Boxes-are-stackless; ARCH-SNOBOL4.md §Native pattern architecture; `src/lower/lower_snobol4.c` (LOWER output = the graph BOPT consumes); `src/emitter/emit_bb.c` (FILL / port machinery + flattener); `src/emitter/BB_templates/x86_asm.h` (label/flatten primitives). **PLAN.md staging:** BOPT is a NEW pipeline stage between LOWER and EMITTER — register it in the driver between those two phases (the first genuinely new stage in the pipeline; PEEP hangs off the emitter, CFOLD off lower).


## ▶ PRIORITY RUNG (session 24): PERF-CALL — inline the per-primitive runtime calls

**Mandate.** The three-way comparison proves SCRIP mode-4 loses to SPITBOL on 14/16 benchmarks because every SNOBOL primitive (var get/set, operator dispatch, string concat, function call, subscript, EVAL) is a runtime PLT call. SPITBOL inlines/threads them. This ladder inlines the most-executed primitives, ranked by MEASURED cost. Each sub-rung is gated on `test_crosscheck_snobol4.sh` staying byte-identical to HEAD (zero regressions) plus a timing delta on its target benchmark(s). Sub-rungs are independent; do DCR first (biggest cluster: func_call 14×, fibonacci 23×, roman 23×).

### DCR — Direct Call protocol (the function-call cluster)

**Diagnosis (assembly + source traced, session 24).** Per call to a trivial `INC(N)`, `rt_call_named_proc` (`src/runtime/rt/rt.c:375`) runs the SNOBOL dynamic-scoping protocol as **~7 GST hash ops BY STRING NAME**: `rt_name_save_push` does `NV_GET_fn("N")`+`NV_SET_fn("N")` to save/install the param, same pair for the return-var `INC`, then `NV_GET_fn("INC")` to fetch the return, then `rt_name_restore` does two `NV_SET_fn` restores. With one proc the `strcmp` scan over `g_rt_gen_procs` is nanoseconds — the per-call HASHING is the 14×. SPITBOL saves through compile-time-known slots, no hashing.

**Fix.** Cache `name_ptr → {rt_proc_t*, ret_cell, param_cells[]}` (each cell from `NV_PTR_fn`, **proven stable**: GST entries are GC-malloc'd + chained, never moved; GVA cells live in static `__gva`; gva_register is preamble-only so cells are fixed before any call). Do save/restore via direct `*cell` ops — zero hashing after warmup. The `name` pointer is a stable `.rodata` address per call site, so a direct-mapped cache keyed by `(uintptr_t)name` is sound (collisions just re-resolve).

**⛔ HAZARD — `NV_GET_fn`/`NV_SET_fn` are NOT pure cell access (traced `core.c`).** They branch on special names with side effects a raw `*cell` would SKIP: INPUT reads stdin, OUTPUT/TERMINAL write, I/O-channel-associated vars write to files, keyword vars set `kw_*`, protected-pattern vars error. Guards (all three MANDATORY):
- (a) **Keyword fallback (free):** `NV_PTR_fn` already returns NULL for INPUT/OUTPUT/STLIMIT/ANCHOR/TRIM/… — so a NULL cell means "don't cache, fall back to by-name `NV_GET/SET`." Correct automatically.
- (b) **Protected-pattern bypass:** skip the whole fast path when `g_protected_pat_vars_armed` (`core.c:6`, cheap global).
- (c) **I/O-association disable-hook:** add a global `g_call_fastpath_off` flipped permanently true at the I/O-association sites (`core.c` ~788/2725/2753, where `_io_chan[i].varname =` is set). Once any var is I/O-associated, all calls use the correct slow path. Rare — every benchmark + most corpus never associate I/O, so the fast path applies broadly.

#### STEPS
- [x] **DCR-1 — cell-cache + cell-based save/restore (RUNTIME-ONLY, no codegen change).** ✅ DONE (session 24, SCRIP `4b663b0`). A/B: func_call 17174ms→6582ms (2.61×), fibonacci 4821ms→2324ms (2.07×).
- [x] **DCR-2a — proc-lookup cache (runtime-only).** ✅ DONE (session 25, SCRIP `3b30fbb`). Behavior-neutral; O(1) for multi-proc.
- [x] **DCR-2-cells — memoize param/return cells on rt_proc_t (runtime-only).** ✅ DONE (session 25, SCRIP `d9dc34b`). A/B func_call: ~6588ms→~6435ms (~2.5%). Cumulative: 17174ms→6435ms (~2.67×). In `rt.c`: change the `g_name_save` entry to carry `(DESCR_t *cell /*or NULL*/, const char *name, DESCR_t old)`. Add the `name_ptr→cell` cache (direct-mapped, ~2048, key compare; miss → `NV_PTR_fn`, fill). `rt_name_save_push`: resolve cell via cache; if non-NULL save `(cell, *cell)` + `*cell = arg`; else fall back to `NV_GET/SET` by name (store NULL cell + name). `rt_name_restore`: per entry `*cell = old` when cell non-NULL else `NV_SET_fn(name, old)`. In `rt_call_named_proc` (and `_sl`): return fetch via cached cell when non-NULL else `NV_GET_fn(name)`; add guards (b)+(c) to gate the cache. Both call entries benefit. **Gate:** `make libscrip_rt` (so rebuild only — this is runtime); `test_crosscheck_snobol4.sh` byte-identical to HEAD (the keyword/I/O programs in the corpus PROVE the guards); A/B `func_call`/`fibonacci` timing vs HEAD.
- [x] **DCR-2 — codegen-side resolution (drop the by-name call entirely).** ✅ DONE (session 28, 2026-06-25, SCRIP `a5ed5be`). `src/driver/scrip.c` only — activates dormant scaffolding: `proc_collect_reset/graph` over main+proc bodies, emit `__proc_names`/`__proc` bss table, `rt_proc_table_fill` in preamble, `g_proc_direct_active=1`. Call sites: `lea rdi,name; call rt_call_named_proc` → `mov rdi,[rip+__proc+k*8]; call rt_call_proc_direct`. Fallback by-name kept for `$FN`/OPSYN/runtime-DEFINE. Gate: crosscheck PASS=171 FAIL=84, fail set byte-identical (zero regressions). Both-medium clean. A/B: func_call 5208→5138ms (~1.3%), fibonacci 2040→1987ms (~2.6%) — honest small win; DCR-1/2a/2-cells already made by-name O(1); residual cost is save/restore protocol.
- [x] **DCR-3 — gate + re-ground.** ✅ DONE (session 27, 2026-06-25). `.s` confirmed byte-identical (DCR was runtime-only, idempotent regen, corpus tree clean). Re-run via `scripts/test_3way_snobol4.sh` (SCRIP/SPITBOL, wall-clock ratio). Func-call rows updated in the THREE-WAY block above: func_call 14.2×→6.65×, func_call_overhead 13.3×→6.62×, fibonacci 23.1×→10.50× (DCR ~2.2× win confirmed at benchmark level); roman 22.7×→21.80× (unchanged — pattern/REPLACE-bound, not call-bound). 14/14 result-bearing benchmarks MATCH. **The whole DCR ladder (DCR-1/2a/2-cells) is now CLOSED and re-grounded.**

### AXS — Array subscript inline (table_access 8.8×, mixed_workload 5.7×)
`subscript_get`/`subscript_set` are per-access PLT calls. For `ARRAY(...)` (NOT hashed `TABLE`) with an integer index, inline a bounds-check + direct `[base + idx*16]` load/store, exactly the shape GVA uses for scalars. Tables stay on the runtime hash path.
- [x] **AXS-0** — detect array-with-int-index access in `lower_snobol4.c` (distinct from table). ✅ DONE (session 26) — IR_IDX operand box already handles this shape; no lower-side change needed.
- [x] **AXS-1** — emit inline bounds-check + `[base+idx*16]` arm. ✅ DONE (session 26, SCRIP `e3d0ff8`). Read + write. Encoder fix (`x86_load_indexed8` REX.B/X/R) bundled.
- [x] **AXS-2** — gate: crosscheck byte-identical; out-of-range semantics match (delegate to slow path — correct by construction). ✅ DONE (session 26). PASS=171 FAIL=84, fail set byte-identical. Both-medium clean. **Note:** `table_access`/`mixed_workload` use TABLE not ARRAY — AXS DT_A guard correctly bypasses; those benchmarks need a separate table-probe inline rung.

### SAB — String self-append capacity (string_concat 8.8×, string_manip 11.3×)
`S = S X` calls `str_concat_d` → `libgc` malloc + O(n) copy every iteration = O(n²) copies + an allocation storm (the source comment confirms O(n²)). SPITBOL is O(n²) too but its per-op alloc/copy is far cheaper. Detect the compile-time self-append pattern `V = V <expr>` and back `V` with a string-builder cell tracking `(ptr,len,cap)` that doubles `cap` → amortized O(1) append (no malloc/copy while `len<cap`).
- [ ] **SAB-0** — detect self-append `V = V <expr>` in `lower_snobol4.c`.
- [ ] **SAB-1** — string-builder runtime type + emit arm.
- [ ] **SAB-2** — **⛔ correctness: preserve copy-on-assign value semantics** — any read/alias of `V` must see an immutable snapshot (else SPITBOL's value semantics break); handle `SIZE`, aliasing, GC rooting.
- [ ] **SAB-3** — gate: crosscheck byte-identical; A/B string_concat/string_manip timing.

### EVR — EVAL/CODE arena reclaim (eval_dynamic 176×)
Already diagnosed in the EVAL-OOM block below: per-EVAL re-parse + re-lower + a bump-allocated mprotect-RX code page that is NEVER reclaimed (self 1.5s vs 87.7s wall = sealing/syscall time). **CORRECTION:** eval_dynamic COMPLETES correctly in this sandbox (87.7s) — it is NOT an OOM here; the bench-script CRASH was the 30s timeout. Fix = the parked RECLAIM variant: snapshot `bb_pool` top before `eval_build_chain`, run, restore (mprotect RX→RW back), free the per-call AST/IR. Cross-ref the EVAL-OOM diagnosis. Lowest priority (one benchmark).

---



**GVA-0/1/2 LANDED (SCRIP `ef7594d`). GVA-3a/3b + str_concat_d fix LANDED (SCRIP `9222a33`). GVA-3a string-coercion fix LANDED (SCRIP `1d2c976`, rebased onto `fe2d39e`).**

Session 16 (2026-06-24): arith_loop ~870ms → ~141ms (~6×). Hot loop now branch-only: LT(N,1000000) emits cmp+jcc (GVA-3b), N=N+1 emits mov [rbx+k*16+8]+add (GVA-3a). Zero crosscheck regressions (87 fails, byte-identical set to pristine).

**CORRECTION (session 17, 2026-06-24): the session-16 line above originally claimed "Bench OK=14/16, FAIL=0" — that was WRONG. GVA-3a shipped a correctness regression: its inline-arith direct cell read `mov rax,[rbx+k*16+8]` takes the raw value field assuming DT_I, but for a DT_S/DT_R operand that field is a char*/double-bits, not an integer. So `T<IDX> = WORD + 0` (WORD a pattern capture) stored a pointer, and mixed_workload returned nondeterministic garbage instead of 550 — real state was OK=13 FAIL=1 CRASH=2. The pre-GVA path used rt_gvar_get_int (which coerces via strtoll); GVA-3a dropped that. Integer counters are always DT_I so arith_loop/fibonacci were unaffected, which is why it slipped through. The relop (GVA-3b) was already correct — it calls rt_gvar_get_int for named globals. FIX (`bb_binop_gvar_arith.cpp`, arms 2 both-names + 3 one-name): inline type-tag guard — `cmp edx,DT_I` on the cell type, fast raw read when DT_I (hot path stays call-free, branch predicts), else fall to rt_gvar_get_int slow path that coerces. arith_loop/fibonacci timings unchanged; bench now GENUINELY OK=14/16, FAIL=0, CRASH=2 (the 2 = pre-existing EVAL OOM eval_dynamic/eval_fixed, unchanged). Crosscheck still 87 fails byte-identical (zero regressions, verified before and after rebasing onto PB-NBODIES-32). All 16 benchmark + feature + demo .s artifacts regenerated side-by-side (idempotent on the combined tree).**

**EVAL OOM — DIAGNOSED (session 17, not fixed; deep + deferred).** eval_fixed (1M× `EVAL('X + 1')`) and eval_dynamic (1M× `EVAL('N + ' N)`) are the only two non-green benches (bench OK=14/16; these are CRASH, OOM-killed, NOT timeout — eval_fixed dies at ~3s). EVAL itself is CORRECT (small counts return the right value); the failure is a ~75KB/call memory leak (measured: 80MB@1k iters → 2.2GB@30k → OOM@150k, linear). Path: `EVAL_fn` (pattern_match.c) → `CONVE_fn` → `eval_build_chain` (runtime_eval.c) runs EVERY call: it re-parses the string, `lower_snobol4`s it, and `gvar_flat_chain_build` emits fresh machine code into the BB pool. The BB pool (`src/machine/bb_pool.c`) is a fixed mmap arena with a BUMP allocator (`bb_alloc` advances `pool_top`, never reclaims; `bb_pool_init` early-returns once `pool_base` set). So every EVAL bump-allocates new sealed (mprotect RX) code pages that are never freed; the per-call AST/IR (`ast_stmt_new`/`strdup`/lowered graph `g`) also leak. FIX OPTIONS for next session: (a) string→DT_E-chain CACHE — builds once, reuses; fixes eval_fixed fully (and makes it fast) but NOT eval_dynamic (1M distinct strings → cache grows + still bump-allocates per new string); (b) RECLAIM per run — snapshot `pool_top` before `eval_build_chain`, run the chain, restore `pool_top` (needs mprotect RX→RW back before reuse) + free AST/IR — fixes BOTH but is the deeper change (watch: chain must not be referenced after reset; GC interactions). Note the new cross-repo DIRECTIVE (`.github` `d26f002a`): BB-local collections use dynamic realloc-2x (cap-bumps retired) — a cache added here must follow that.

**str_concat_d correctness fix (SCRIP `9222a33`):** SPITBOL null-string-identity: `"" N` preserves N's type. Pristine returned STRING after `LT(N,5) N`; oracle expects INTEGER. GVA-3a removed the accidental `strtoll` mask that hid the bug. Fixed: `IS_NULL_fn` early-return in `str_concat_d`.

**▶ NEXT MOVE: PB-FZ** (constant-fold invariant patterns — see PRIORITY RUNG below). Then GVA-4 (indirect `$X` fast path via rbp-based GST hash index). Alternatively OPSINGLE or REC-COV — Lon decides.

---

## ▶ PRIORITY RUNG: PB-FZ — ALWAYS constant-fold invariant patterns (Lon pivot, 2026-06-24)

**PIVOT (Lon):** NO command-line switch between constant-folding and build-from-scratch. ALWAYS freeze every invariant pattern subtree at COMPILE time. `bb_pat_build.cpp` survives ONLY as the STITCH path for the case where an INVARIANT and a structurally-VARIANT pattern are combined. This promotes ARCH-SNOBOL4.md's "ALL-INVARIANT BLOB FREEZE" optimization to the ONLY path and deletes the baseline instance-wiring.

**VARIANCE TAXONOMY (the trigger is STRUCTURAL variance, not operand variance):**
- INVARIANT (→ FREEZE to one sealed `bb_box_fn` blob): literal-operand primitives (`POS(0)`, `SPAN('0-9')`, `LEN(3)`, `"abc"`), invariant combinators (SEQ/ALT/ARBNO/`.`/`$` of invariants), and `*E` (deferred-eval box has FIXED code → its graph is static; `ARBNO(*var)` is INVARIANT). **CORRECTION to ARCH-SNOBOL4.md: it lumps `*E` with the structural variants — wrong; `*E` is a fixed box doing a dynamic sub-call, so it FREEZES.**
- OPERAND-variant (→ FREEZE structure, box reads operand LATE from a slot; NO build, NO stitch): `POS(X)`, `SPAN(cvar)`, `LEN(N)`. `POS(0)` and `POS(X)` are the SAME `BB_MATCH_POS` unary matcher fed by different operand-source boxes (baked-immediate vs `[ζ+off]`/`[rbx+k·16]` load); the operand-source is polymorphic across same-arg-type matchers (one int-source feeds POS/RPOS/LEN/TAB/RTAB; one string-source feeds SPAN/BREAK/BREAKX/ANY/NOTANY). So `POS(START_LINE) SPAN(CHARS) RPOS(FINISH_LINE)` freezes WHOLE to one blob, late operand reads, ZERO runtime stitch. **GUARDRAIL:** late read is sound ONLY for IMMEDIATE matches (construct+match same statement); a STORED operand-variant pattern must SNAPSHOT operands into per-instance slots at construction (else post-construction mutation diverges from SPITBOL, which freezes operand values at the `P = …` assignment).
- STRUCTURAL-variant (→ the ONLY case needing `bb_pat_build` STITCH): a pattern-valued variable used as a sub-pattern (`var_pattern`, no `*`), `$NAME` indirect resolving to a pattern, a function call returning a pattern. These splice a runtime box-graph into the enclosing combinator.

**THE STITCH SET IS CLOSED** (SPITBOL pattern algebra — manual Ch.6 "Pattern operations" + ARBNO + immediate-assign). Exactly five combinators, so exactly these stitch boxes, and ONLY when an operand is structurally variant:
1. `STITCH_SEQ` — Subsequent (concatenation `P Q`), n-ary (assoc-flatten).
2. `STITCH_ALT` — Alternate (alternation `P | Q`), n-ary.
3. ARBNO-stitch — `ARBNO(P)` loop wrapper (variant body; `ARBNO(*P)` freezes).
4. CAPTURE-stitch `.` — conditional assignment `P . NAME` (capture-on-overall-success wrapper).
5. CAPTURE-stitch `$` — immediate assignment `P $ NAME` (capture-on-submatch wrapper).
Precedence (manual): `.`/`$` > blank(SEQ) > `|`(ALT) — fixes the stitch-tree shape. `@NAME`, `*E`, and all primitive functions are LEAVES, never combinators.

**BENCHMARK INVENTORY (verified this session — build clean, bench OK=15 FAIL=0 CRASH=1, only eval_dynamic = known throughput timeout). All three pattern benchmarks are FULLY INVARIANT → the STITCH boxes are NOT exercised by the bench corpus (they are for the wider crosscheck corpus). The bench is a pure FREEZE exercise, split immediate-vs-stored:**
- **roman** (immediate: `N RPOS(1) LEN(1).T =` and `'…' T BREAK(',').T`): ALREADY inline-frozen — emits `IR_MATCH_RPOS`/`LEN`/`CAPTURE` boxes inline; bare `T` is `IR_MATCH_DEFER` (dynamic fetch, correct). **DONE — no work.** Result-sensitive, passes .ref.
- **string_pattern** (stored: `PAT = BREAK(',').WORD ','`): built ONCE via per-shape fused runtime builder `bb_build_break_cap_lit_blob` (`src/runtime/rt/bb_pat_build.cpp:88`), matched 500k× via DEFER. Correct (result-sensitive, passes .ref). FZ replaces the fused builder with a frozen blob.
- **pattern_bt** (stored: `PAT = ('aaa'|'bbb'|'ccc'|'ddd') SPAN('abcd').W`): **stored ALT-pattern build is UNIMPLEMENTED in mode-4** — pattern literals are ABSENT from the `.s`, PAT is a no-op stub. "OK" is a FALSE PASS: result is the loop counter `N`, and a null PAT matches the null string every iteration → 500000 regardless. FZ IMPLEMENTS it. (Add a result-sensitive check — output `W` — so the freeze is actually validated.)

**SEAM (verified):** stored pattern `PAT = <invariant>` lowers (`src/lower/lower_snobol4.c`) to `IR_PATTERN_CAT` + `pat_via_dtp`; `src/emitter/BB_templates/bb_pattern_cat.cpp` emits a C-call to the per-shape `bb_build_break_cap_lit_blob`. Per-shape fused builders don't scale (no `alt4_span_cap` builder ⇒ pattern_bt stub). **`IR_REF_INVARIANT` is ALREADY a reserved opcode (`src/contracts/IR.h:174`, "REFINV" in `prove_lower.c`) but UNWIRED in the emitter — it exists for exactly this.** The immediate matchers (`bb_match_*()` dispatched in `src/emitter/emit_core.c`) ARE the frozen boxes to reuse. **FZ = redirect the existing immediate-matcher emission into a standalone sealed blob under a label + store its head as a `DT_P` via `IR_REF_INVARIANT`, replacing the `pat_via_dtp` build-call.** Match site keeps its DEFER fetch (FZ-2/3); inlining the sealed head to skip per-match DEFER is the FZ-5 perf step.

### STEPS
- [x] **FZ-2 — `IR_REF_INVARIANT` store + DEFER fetch.** ✅ LANDED (session 20, SCRIP `c3b6a83`). `PAT = BREAK(',') . W ','` lowers to a sealed matcher blob + `IR_REF_INVARIANT` storing the head as DT_P (no `bb_build_break_cap_lit_blob`). Gate MET: mode-3 AND mode-4 output == `string_pattern.ref`; builder call absent from `string_pattern.s`. See prior START-HERE header for the six pieces.
- [x] **FZ-3 — ALT-of-literals freeze.** ✅ LANDED (session 21, SCRIP `973df9e`). `PAT = ('aaa'|'bbb'|'ccc'|'ddd') SPAN('abcd').W` constant-folds to one sealed `IR_REF_INVARIANT` blob; pattern_bt mode-3 AND mode-4 output `result: 500000` + `W: ccccddddaaaa` (W hand-computed; oracle confirm pending token). Added `sno_freeze_pat_ir()` — general recursive kids-channel matcher-graph builder for invariant patterns — replacing the narrow FZ-2 per-shape constructor. Key insight: `flat_drive_cat/alt` read arms from the **kids channel** (`bb_match_kids_state_t`), not the γ/ω spine; must build in kids-channel form. `sno_has_pat()` guard prevents value-concat expressions (e.g. `42 ' items'`) from entering the freeze path. pattern_bt.sno+.ref updated (W output added). `string_pattern.s` byte-identical. Bench OK=15 FAIL=0 CRASH=1 (eval_dynamic OOM pre-existing). Crosscheck PASS=171 FAIL=84 vs pristine 168/87 — zero new failures, +3 fixed (132/133/134_pat_fence_eps_recur also freeze via the new general path).
- [x] **FZ-4 — retire dead fused builders.** Remove now-unused per-shape builders in `bb_pat_build.cpp` (keep ONLY the structural-variance STITCH path). Gate: `test_crosscheck_snobol4.sh` byte-identical (zero regressions).
- [ ] **FZ-5 (follow-on perf) — match-site direct reference.** When the compiler proves PAT holds a once-assigned invariant pattern (assigned, never reassigned), inline the sealed head at the match site and skip the per-match `rt_defer_get_pat_fn` (runs 500k× in string_pattern/pattern_bt) — the actual hot-loop win, turning stored into roman's inlined form.

**Prereq reads (PLAN.md step 7 — touches per-box state):** ARCH-SNOBOL4.md §"Native pattern architecture" + §"ALL-INVARIANT BLOB FREEZE", ARCH-x86.md §Boxes-are-stackless + §Flat-BB-ABI, `src/emitter/bb_regs.h`, `src/emitter/BB_templates/bb_pattern_cat.cpp`, `src/runtime/rt/bb_pat_build.cpp`, `src/emitter/emit_core.c` (matcher dispatch).

---

**Build:** `apt-get install -y libgc-dev && make && make libscrip_rt`. Oracle: `git clone …/x64 /home/claude/x64; sbl -b`. Tri-probe: `scrip --compile p.sno > p.s; gcc -no-pie -x assembler p.s -Lout -lscrip_rt -lgc -lm -Wl,-rpath,$PWD/out -o p.bin; ./p.bin` vs `sbl -b`. Bench/crosscheck gates: `scripts/test_bench_snobol4_modes.sh`, `scripts/test_crosscheck_snobol4.sh`.

---

## Prior context (session 13 — literal-subject native scan, now history)

roman's scan 2 (`'0,1I,…,9IX,' T BREAK(',') . T`) declined native because `flat_drive_scan_stmt` gated on a *named* subject only. Four-layer fix landed: `emit_bb.c` gate accepts `op_scan_subj_lit`; `flat_drive_scan_native` attaches an `IR_LIT_S` operand to `IR_SUBJECT`; `bb_subject.cpp` lit arm fixed (`mov→lea`, `bb_subj_litlbl()`, `rt_subject_load_lit`); `pattern_match.c` `rt_subject_load_lit` sets ζ-slot AND `Σ`/`Σlen`. Roman's earlier `MCXI` (recursive re-descent) symptom was resolved by the turn-1 local-var fix above. Roman reproduction:
```snobol4
    &TRIM = 1
    DEFINE('ROMAN(N)T')                   :(RE)
ROMAN N RPOS(1) LEN(1) . T =              :F(RETURN)
    '0,1I,2II,3III,4IV,5V,6VI,7VII,8VIII,9IX,' T BREAK(',') . T :F(FRETURN)
    ROMAN = REPLACE(ROMAN(N), 'IVXLCDM', 'XLCDM**') T :S(RETURN)F(FRETURN)
RE  R = ROMAN('176')
    OUTPUT = 'RESULT=' R
END
```

**Design note (carried):** the `walk_bb_node` preamble clobbering `op_a_sval` from `operands[0]` is the ambient-`g_emit` class flagged in session 12; the general cure (port-field reset / FILL-only / debug gen-counter assert) is still unbuilt.

---

# Open rungs (not yet started)

## PERF-GVA — Global Variable Array: eliminate GST hash lookup on hot path

### Naming

| Abbrev | Full name | What it is | Register | Access |
|--------|-----------|------------|----------|--------|
| **GST** | Global Symbol Table | Hash dictionary: name→DESCR_t. Runtime/dynamic. Currently called NV. | `rbp` (BBREG_HASH) | by name string |
| **GVA** | Global Variable Array | Flat `DESCR_t[N]` for compile-time-known globals. Static `.data`. | `rbx` (BBREG_BASE) | by integer index k |
| **LVA** | Local Variable Array | Per-call-frame `DESCR_t` slots for procedure locals/params. Already exists as ζ-frame. | `r12` (BBREG_ZETA) | by byte offset |

**The problem:** every global variable read is `call NV_GET_fn@PLT` (hash walk + string compare). Every write is `call rt_gvar_assign_*@PLT`. For `arith_loop` at 1M iterations that is ~14 PLT+hash calls per iteration. SPITBOL bakes variable addresses into code at compile time — zero calls per access.

**The fix:** at compile time, assign each program-global variable name an integer index k. Emit a flat `DESCR_t __gva[N]` array in the program's `.data` section. At preamble, call `gva_register(names, __gva, N)` which (a) populates `__gva[k]` = current GST value (null for new vars), (b) sets `GST_t.is_gva=1` and `GST_t.cell=&__gva[k]` so existing `NV_GET_fn`/`NV_SET_fn` paths transparently read/write through the GVA cell, (c) returns `__gva` base. Preamble stores that base in `rbx`. Templates then access `[rbx + k*16]` — two `mov` instructions, zero calls.

**GC safety:** `__gva` lives in `.data` (static storage, not GC heap). `DESCR_t.s` string payloads are still GC-managed heap pointers written into the cell — BDW scans `.data` as a root, so strings in GVA cells are reachable and not collected. The cell address itself never moves.

**GST forwarding invariant:** after `gva_register`, every GVA-backed variable in GST has `is_gva=1` and `cell→__gva[k]`. `NV_GET_fn` returns `*cell`; `NV_SET_fn` writes `*cell`. Dynamic paths (indirect refs `$X`, EVAL) that resolve to a GVA-backed name still work correctly at the cost of one extra pointer dereference — no correctness regression.

---

### GVA-0 — Infrastructure: GST forwarding flag + gva_register runtime  ✅ DONE (local, unpushed)

**GVA-0a — `GST_t` (rename from `NV_t`) gains `is_gva` + `cell`:**
In `src/runtime/core/core.c` (binary; edit via patch or sed):
```c
typedef struct _VarEntry {
    char              *name;
    DESCR_t            val;    /* live value when is_gva==0 */
    DESCR_t           *cell;   /* points into __gva when is_gva==1 */
    int                is_gva;
    struct _VarEntry  *next;
} GST_t;   /* was NV_t */
```
`NV_GET_fn`: `if (e->is_gva) return *e->cell;` before returning `e->val`.
`NV_SET_fn`: `if (e->is_gva) { *e->cell = val; return val; }` before writing `e->val`.
`NV_PTR_fn`: `if (e->is_gva) return e->cell;`
**Rename `NV_t` → `GST_t` throughout `core.c`.** Public API names `NV_GET_fn`/`NV_SET_fn`/`NV_PTR_fn`/`NV_CLEAR_fn` keep their names for now (rename is a separate rung, not required for correctness).

**GVA-0b — `gva_register` in `src/runtime/rt/rt.c` + `rt.h`:**
```c
/* Register N compile-time globals. Returns cells base (stored in rbx by preamble). */
DESCR_t *gva_register(const char **names, DESCR_t *cells, int n);
```
Implementation: for k in 0..n-1: find-or-create GST entry for `names[k]`; copy existing `e->val` into `cells[k]`; set `e->is_gva=1`, `e->cell=&cells[k]`.
**Exclude** names where `NV_PTR_fn` returns NULL (INPUT, OUTPUT, PUNCH, keyword `&`-prefix vars) — these stay GST-only, no GVA slot.

**GVA-0c — emitter: GVA name collection in `emit_bb.c`:**
New pass before any box emission: walk all IR nodes, collect distinct `op_sval` names for `IR_VAR`, `IR_ASSIGN`, `IR_BINOP_GVAR_ARITH`, `IR_BINOP_GVAR_ARITH_SLOT` that are non-keyword, non-`&`-prefix, non-INPUT/OUTPUT. Assign each a slot index k (stored in a new `int g_gva_slots[]` parallel to a `const char *g_gva_names[]` table, max 1024 entries). Store per-name GVA index in a lookup table `gva_index_of(name) → k` used by all templates.

**GVA-0d — emitter: emit `__gva` array + preamble call in `xa_flat.cpp` / `xa_prologue.cpp`:**
In TEXT mode, after `.section .data` banner:
```asm
  .align 16
__gva:
  .space N*16, 0
__gva_names:
  .quad .Lgvan0, .Lgvan1, ...   /* N name pointers */
  .section .rodata
.Lgvan0: .string "VARNAME0"
...
  .section .text
```
In preamble (before first user BB):
```asm
  lea rdi, [rip + __gva_names]
  lea rsi, [rip + __gva]
  mov edx, N
  call gva_register@PLT
  mov rbx, rax              /* rbx = __gva base for lifetime of program */
```
Also `push rbx` / `pop rbx` around any call that may clobber it per ABI — but since `rbx` is callee-saved in SysV ABI, callees preserve it automatically. No push/pop needed around `call` instructions in templates.

**GVA-0e — update `bb_regs.h` comment block** to document `rbx=GVA base` and `rbp=GST hash base` with new names.

**Gate GVA-0:** compile `arith_loop.sno` → verify `__gva` in `.s`; link and run → output identical to oracle; `gva_register` called once; `NV_GET_fn("N")` returns value through `e->cell`.

---

### GVA-1 — Direct load: IR_VAR global read → `[rbx + k*16]`  ✅ DONE (local, unpushed)

**Mandate:** In `bb_var.cpp` (and `bb_var_global.cpp` if separate), when `gva_index_of(_.op_sval) >= 0` (name has a GVA slot), replace `call NV_GET_fn` with inline load.

Add to `emit_globals.h` `sm_emit_t`:
```c
int op_gva_k;   /* GVA slot index for this node, -1 if GST-only */
```
Populated in `emit_bb.c` `walk_bb_node` preamble alongside existing `op_sval` fill.

Add to `x86_asm.h`:
```c
inline const char *GVAQ(int k, int hi) {
    static char b[8][40]; static int i; i=(i+1)&7;
    snprintf(b[i],40,"qword ptr [rbx + %d]", k*16+hi);
    return b[i];
}
```

`bb_var.cpp` new first arm (checked before existing `g_gvar_flat_chain` arm):
```cpp
(_.op_gva_k >= 0) ?
  x86("comment", "IR_VAR gva")
+ x86("label",   _.lbl_α)
+ x86("mov",     "rax", GVAQ(_.op_gva_k, 0))
+ x86("mov",     "rdx", GVAQ(_.op_gva_k, 8))
+ x86("mov",     FRQ(_.op_off),     "rax")
+ x86("mov",     FRQ(_.op_off + 8), "rdx")
+ x86("jmp",     "γ")
+ x86("def",     "β")
+ x86("jmp",     "ω") :
```

**Gate GVA-1:** `grep "call NV_GET_fn" arith_loop.s` == 0; full `test_crosscheck_snobol4.sh` oracle-identical.

---

### GVA-2 — Direct store: IR_ASSIGN global write → `[rbx + k*16]`  ✅ DONE (local, unpushed)

**Mandate:** Replace `call rt_gvar_assign_int` / `call rt_gvar_assign_descr` / `call rt_gvar_assign_var` / `call rt_gvar_assign_lit_i` / `call rt_gvar_assign_lit_s` with inline stores when the destination name has a GVA slot.

Integer literal store (`N = 5`), DT_I=6:
```asm
mov dword ptr [rbx + k*16],     6
mov dword ptr [rbx + k*16 + 4], 0
mov qword ptr [rbx + k*16 + 8], IMM
```

DESCR_t from frame slot (result already split lo=rax hi=rdx):
```asm
mov qword ptr [rbx + k*16],     rax
mov qword ptr [rbx + k*16 + 8], rdx
```

Steps:
- GVA-2a: `bb_gvar_assign.cpp` — integer and descr paths
- GVA-2b: `bb_gvar_assign_lit_i.cpp`, `bb_gvar_assign_lit_s.cpp`
- GVA-2c: `bb_gvar_assign_var.cpp` — var→var copy through GVA
- GVA-2d: `bb_gvar_assign_call.cpp`, `bb_gvar_assign_concat.cpp`

**Gate GVA-2:** `grep "call rt_gvar_assign" arith_loop.s` == 0; crosscheck suite green.

---

### GVA-3 — Fused integer arithmetic + relop  ✅ DONE (session 16, SCRIP `9222a33`)

**Mandate:** `N = N + 1` where both operands and destination are GVA-backed integer vars emits zero calls. Detect in `bb_binop_gvar_arith.cpp` when `op_parts` names all have GVA slots.

`N = N + 1` (add, immediate RHS):
```asm
mov rax, qword ptr [rbx + kN*16 + 8]   /* N.i */
add rax, 1
mov dword ptr [rbx + kN*16],     6      /* DT_I */
mov dword ptr [rbx + kN*16 + 4], 0
mov qword ptr [rbx + kN*16 + 8], rax
```

`LT(N, 1000000) N` (relop predicate, GVA int vs immediate):
```asm
mov rax, qword ptr [rbx + kN*16 + 8]
cmp rax, 1000000
jge β_port
/* success fall-through: value = N.i already in rax */
```

Steps:
- GVA-3a: `bb_binop_gvar_arith.cpp` fused path for GVA+GVA and GVA+IMM
- GVA-3b: new `bb_gvar_relop.cpp` for `LT`/`GT`/`LE`/`GE`/`EQ`/`NE` on GVA int operands — emits `cmp` + conditional jump, replaces `call rt_call_arr@PLT`

**Gate GVA-3:** `arith_loop.s` hot loop body (label `LOOP` to next label) contains zero `call` instructions; `fibonacci.s` same; timing run shows ≥5× improvement over baseline on `arith_loop`.

---

### GVA-4 — rbp GST hash path for runtime indirect refs (optimization, not correctness)

**Mandate:** `$X` where X's runtime string value names a GVA-backed variable: use `rbp`-based hash index to skip full GST walk.

New runtime helper `gva_lookup_by_name(const char *name) → int k` (returns -1 if not GVA-backed). Emitted in `.data` beside `__gva`:
```asm
__gst_idx:
  .space GVA_HASH_SIZE*4, 0xff   /* uint32_t[GVA_HASH_SIZE], sentinel=0xffffffff */
```
Preamble fills `__gst_idx` with (hash(name) → k) entries after `gva_register`.

Template for indirect read, fast path:
```asm
/* name string ptr in rdi */
call gva_hash_probe@PLT     /* (rbp, rdi) → k or -1 */
test eax, eax
js   .gst_slow
mov  rdx, qword ptr [rbx + rax*16 + 8]
mov  eax, dword ptr [rbx + rax*16]
jmp  γ
.gst_slow:
call NV_GET_fn@PLT
```

This is an optimization rung — correctness is guaranteed by GVA-0b's `is_gva` forwarding regardless of this rung. Do GVA-4 only after GVA-0 through GVA-3 are green and benchmarked.

**Gate GVA-4:** indirect-ref crosscheck programs (`014_assign_indirect_dollar`, `015_assign_indirect_var`) oracle-identical; `arith_loop` timing unchanged (no indirect refs in that benchmark).

---

### Expected performance impact

| Rung | Calls eliminated per `arith_loop` iteration | Estimated speedup |
|------|---------------------------------------------|-------------------|
| GVA-1 | 2 × `NV_GET_fn` | ~2× |
| GVA-2 | 2 × `rt_gvar_assign_*` | +1.5× |
| GVA-3 | `binop_apply` + both assign calls | closes to ~10× baseline |
| GVA-4 | partial `NV_GET_fn` for indirect | marginal on arith |

---

## OPSINGLE — delete operand_aux, one channel only

**Mandate:** exactly ONE operand channel: `nd->operands[]`. Delete `operand_aux` (`bb_operand_aux_set`/`bb_operand_aux_get`).

Writers still aux-only (add `ir_operand_push`, keep aux until readers flipped): `lower_snobol4.c` CALL args, `lower_icon.c:134,137,315`, `lower_raku.c:210`, `lower_pascal.c:147,162,177,340`, `lower_prolog.c:140`.

Readers to flip (`bb_operand_aux_get` → `nd->operands[]`): `BB_templates/bb_call.cpp:98`; `emit_bb.c:350,411,438,846,1072,1492,1818,2489,2957(DELETE bridge shim),3035,3240,3335,3398,3458`; `driver/scrip.c:102,245,1931`; `contracts/scrip_ir.c:355`.

Delete last (all readers flipped + all language gates green): `bb_operand_aux_set`, `bb_operand_aux_get`, struct fields, all call sites.

**Gate:** `grep operand_aux src/` (excl attic) == 0 AND all language gates green.

## REC-COV — community-recognized corpora

**Mandate:** extend coverage into community corpora. PB-GREEN stays session-first.

Inventory (pass-rates unmeasured — RC-0's job):
- `corpus/programs/gimpel/` — 145 `.sno` (no `.ref`)
- `corpus/programs/snobol4/demo/` — 18 `.sno`

Steps: RC-0 honest runner + oracle-gen refs + triage table → RC-1 gimpel → RC-2 demo → RC-3 promote counts to hard floors → RC-4 re-ground "10×" claim.

---

## BBGC — slide-compaction garbage collector for the BB code arena  ⬇ LOW PRIORITY / EXPLORATORY (Lon 2026-06-24)

**Status: design-only spike. Do NOT start ahead of GVA-4 / OPSINGLE / REC-COV.** Picked up only when the `bb_pool` bump arena's lack of compaction becomes a real ceiling (the EVAL leak fix landed a LIFO watermark — `bb_pool_mark`/`bb_pool_release` — and a 2MB retention budget, which BOUNDS but does not COMPACT: cached/retained chains pin non-top regions, so pure-LIFO leaves holes a long-running EVAL/CODE-heavy program eventually exhausts).

**Vision (Lon):** treat `bb_pool` as a GC heap of *code*. When it fills, mark live BB blobs, sweep the unreferenced, and **slide the survivors down to compact**, re-stitching ONLY the four ports (α β γ ω) and touching nothing else inside a blob body.

**Why this is viable — relocatability taxonomy (grounded in `x86_asm.h` binary encoder + `bb_regs.h`, verified 2026-06-24).** Setting the 4 ports aside, here is everything baked into a sealed blob and its behavior under a slide:
1. **Register-relative state** (`[r12+off]` ζ, `rbx` GVA, `rbp` GST, `r13/r14/r15` Σ/δ/Δ) — encodes NO code/data address → **zero fixup**. This register-centric ABI is the whole reason compaction is tractable.
2. **RIP-relative to adjacent sealed RO** (`lea reg,[rip+disp32]` to interned name/lit bytes) — disp32 = target−rip_next → **invariant IFF the RO tail moves with its blob as one indivisible unit**. ⇒ relocation unit = blob + adjacent RO, never split.
3. **Immediate data constants** (`movabs reg,<int|float-bits>`) — values, not addresses → **position-independent**.
4. **Runtime-function calls** — binary encoder ALREADY emits `movabs rax,&fn ; call rax` (`x86_asm.h:196`, abs addr) NOT `call rel32`. The runtime never moves, so the absolute target is invariant under caller movement → **zero fixup**. (Ports, by contrast, are `0xE8 rel32` / `XK_PORT` — relative, the one thing that breaks.)
5. **The four ports** — `call/jmp rel32` between boxes → break on move → **re-stitch (recompute rel32)**. Exactly the scoped work; nothing else in the body needs it.
6. **⚠ THE REAL HAZARD — stored pointers to blob ENTRY points held OUTSIDE the pool.** A moving collector must fix these: (a) the EVAL cache (`runtime_eval.c` `g_eval_cache[].fn`); (b) DT_C/DT_E descriptors on the SNOBOL heap (`code()`/`CONVE_fn` stash `d.ptr=blob_addr` into first-class values a user var can hold — `:<C>` direct-goto, `CONVERT(s,'CODE')`, retained `*expr`); (c) the runtime label→code map; (d) **live return addresses on the native C stack** pointing INTO a blob if GC can fire while a BB frame is active (the precise-moving-GC-of-JIT-code problem).

**Two design decisions that make "touch nothing else" literally true:**
- **Entry-table handle indirection.** Hand out a stable handle (index into a per-pool entry-table the collector owns) instead of a raw blob-entry address; cache/descriptors/direct-gotos store the handle, the table holds the live address, relocation updates ONLY the table. Bounds category-6 fixups to one table.
- **Compact only at a safepoint with no active BB frame** (between top-level statements / after an EVAL/CODE returns — easy to guarantee since those run synchronously to completion and the pool is touched only between statements). Eliminates category-6(d) entirely, avoiding return-address rewriting.

### STEPS
- [ ] **BBGC-0 — measure + baseline.** Add `bb_pool` occupancy/hole stats; build an EVAL/CODE-heavy stress program that pins retained chains AND keeps allocating (forces holes the 2MB-budget LIFO can't reclaim). Confirm the failure mode (NULL from `bb_alloc` while total live < pool) and document why LIFO watermark alone is insufficient. NO behavior change.
- [ ] **BBGC-1 — root enumerator.** Enumerate all live BB entry-point references: `g_eval_cache`, DT_C/DT_E descriptors reachable from GST (BDW already roots the SNOBOL heap — walk code-typed cells), the runtime label→code map, direct-goto code values. Output a `(holder, entry_addr)` root list. Read-only; no relocation yet.
- [ ] **BBGC-2 — entry-table handle indirection.** Replace raw entry addresses handed to cache/descriptors/direct-goto with handles into a collector-owned per-pool entry-table; the table holds the current address. Floor: EVAL/CODE crosscheck byte-identical (one extra deref on the slow path only).
- [ ] **BBGC-3 — mark.** From roots, mark reachable blobs; follow inter-blob refs (ports + entry-table) transitively. Verify mark set ⊇ everything the stress program calls.
- [ ] **BBGC-4 — safepoint discipline.** Define + assert the compact safepoint (no active BB frame on the C stack). Confirm EVAL/CODE return BEFORE any compaction trigger. (Closes category-6(d).)
- [ ] **BBGC-5 — sweep + slide-compact.** Slide live blobs (blob + adjacent RO, one unit) down to remove holes; update the entry-table; re-stitch the 4 ports per moved box (recompute rel32). Add a verifier that asserts NO code-internal absolute pointer exists outside the covered categories (1/3/4 must need nothing). 
- [ ] **BBGC-6 — trigger.** On `bb_alloc` overflow, run compaction (at a safepoint) and retry instead of returning NULL.
- [ ] **BBGC-7 — gate.** EVAL-heavy stress (e.g. 1M distinct EVALs) runs with BOUNDED pool, output == SPITBOL oracle, compaction firing ≥N times; full `test_crosscheck_snobol4.sh` byte-identical (zero regressions); bench unaffected.

**Prereq reads when picked up (per PLAN.md step 7 — this touches per-box state + relocation):** `ARCH-x86.md` §Boxes-are-stackless + §Flat-BB-ABI, `ARCH-ICON.md` §register-contract, `REGISTER-LAYOUT.md`, `src/emitter/bb_regs.h`, `src/emitter/XA_templates/xa_flat.cpp`, `src/machine/bb_pool.c` (the new `bb_pool_mark`/`bb_pool_release`).

---

# Completed / superseded (summary only)

Sessions 1–12 built the full SNOBOL4-BB ladder bottom-up:
- **DDS-0** (session ~8): deleted all `bb_*_proto[]` byte arrays, `DTP_t` head, `rt_dtp_run`. Ground-zero rebuild.
- **TR-1** (`7d6a9c9`): `sno_leaf_buildable` extended for `TT_CAPT_COND_ASGN`; capture patterns routed to builder, not orphaned.
- **TR-LEN** (`75f97e5`): `bb_build_len_blob` allocates `IR_MATCH_LEN` (matcher), not `IR_PATTERN_LEN` (builder). `r1`→`W=CD`.
- **Rename** (`2e5a5a3`): `IR_PAT_*` → `IR_MATCH_*` throughout.
- **TR-BREAK** (`15bda9d`): `bb_pattern_break.cpp` + `bb_build_break_blob`. First ζ-slot box; proves frame mechanism end-to-end.
- **TR-CAPTURE** (`1e962ed`): `bb_build_break_capture_blob`; `PAT=BREAK(',') . W`→`W=alpha`.
- **TR-CAT** (`5d6e7cd`): `bb_build_break_cap_lit_blob`; `PAT=BREAK(',') . W ','`→`W=alpha`.
- **splice fix** (`9ea1251`): `bb_scan_splice_empty` stripped of stale port scaffolding; string_pattern + mixed_workload GREEN.
- **literal-subject scan** (`f3f7cdb`, session 13): gate + `IR_LIT_S` operand + `bb_subj_litlbl` + `rt_subject_load_lit`. Last bomb removed.

Architecture constants (do not re-derive):
- `walk_bb_node` preamble (emit_core.c:328–333) overwrites `op_sval`/`op_ival`/`op_a_sval`/etc. from node+operands every emission — never rely on ambient values set before `FILL`.
- `rt_cap_assign_cursor` reads global `Σ` (set by `rt_subject_load_nv` and now `rt_subject_load_lit`).
- `flat_drive_cat_arms` reads the kids channel (`IR_EXEC(cat).counter`), NOT `operands[]`; a CAT with `nkids==0` emits empty.
- `bb_build_flat` entry CAT with nkids==0 emits empty — kids channel is mandatory.

## ⛔ FACT RULE — "HANDOFF COMPLETE" REQUIRES A CONFIRMED PUSH (Lon directive, 2026-06-24)
**The phrase "handoff complete" — or any terminal claim of doneness ("done", "all set", "wrapped up", "committed and clean" presented as the end state) — MUST NOT be spoken until `git push` has SUCCEEDED and `git log origin/main --oneline -1` (step 7) shows THIS SESSION'S hash on origin for EVERY touched repo.** A local commit is NOT a handoff; the bytes are on this disposable sandbox and vanish with it. "Pending push awaiting credential", "ready to push", or "the local commits are safe" is an **INCOMPLETE handoff and must be reported as INCOMPLETE — never dressed up as complete.** If a credential is missing or the push fails, the handoff is **BLOCKED**: state that plainly, say exactly what is needed, and STOP — do NOT declare completion. The push (step 6) and the `origin/main` hash confirmation (step 7) are the LAST and MANDATORY acts of every handoff; skipping either means the handoff did not happen, regardless of how green the local tree is. Verify HEAD == origin/HEAD per repo, or it is not done.

**HOW THIS WAS MISSED (root cause, 2026-06-24 — so it is not repeated):**
1. **BLOCKED was reframed as COMPLETE.** The push failed for a missing credential; instead of reporting the handoff BLOCKED, the green *local* state was reported as done with the push demoted to a suggested user follow-up. The rule's real success criterion (the session's bytes living on `origin`) was silently swapped for a weaker proxy (bytes committed to a disposable sandbox). A locally-committed handoff is the same failure as an uncommitted one, one step later.
2. **A bad precedent was inherited.** Prior HANDOFF docs in this repo literally recorded "commits pending push awaiting user token" as a handoff outcome, normalizing the incomplete pattern; it was pattern-matched instead of challenged. "Pending push" is NOT an outcome — it is an unfinished, BLOCKED handoff.
3. **The completion claim was free-authored text.** Nothing forced the status line to be checked against ground truth, so under optimism it drifted from reality. Free-text status will always drift; it must be computed.

**PROTOCOL — THE STATUS LINE IS COMPUTED, NEVER TYPED (the mechanical gate):**
The assistant MUST NOT write the string "HANDOFF COMPLETE" (or any terminal doneness claim) as its own prose. The ONLY sanctioned source of that claim is the verbatim stdout of **`bash scripts/handoff_status.sh`**, which reads ground truth (working tree clean + local HEAD == `origin/<branch>` + zero unpushed) for every git repo it AUTO-DISCOVERS under the workspace (no hardcoded repo list — it enumerates every repo with an `origin` remote, so it cannot miss a touched one and reports the count it found) and prints `HANDOFF COMPLETE` (exit 0) or `HANDOFF BLOCKED` with the reason (exit 1). Handoff step 7 is now: **run `handoff_status.sh`, paste its output verbatim, and only treat the handoff as done if that output — not the assistant — says `HANDOFF COMPLETE`.** If it says BLOCKED, the handoff is BLOCKED: fix the listed reason (commit, then `git pull --rebase && git push`) and re-run. Reading `origin` needs no credential; only the push that PRECEDES the check does. The script blocks on its own uncommitted bytes, so it cannot be satisfied by a tree that still has the rule edit unpushed — closing the loop on itself.

**LIMITATION — DO NOT OVERSELL THIS GATE.** A markdown rule CANNOT coerce the assistant to run the script; this rule has the SAME enforcement gap as the rule it replaces (the assistant must still choose to honor it — exactly what failed on 2026-06-24). The script makes the truth cheap to obtain and hard to FAKE; it does not make the lie IMPOSSIBLE. Real coercion can only live OUTSIDE the model: (a) a harness/product layer that blocks any completion claim not backed by a fresh `handoff_status.sh` run (only the platform can add this), or (b) the human reviewer, who is the enforcer that actually works — **reject any "HANDOFF COMPLETE" not accompanied by the script's verbatim stdout with hashes matching `origin`, and treat a bare completion claim as FALSE by default.**


## ⛔ FACT RULE — THE WORD "HANDOFF" IS FORBIDDEN IN THE ASSISTANT'S OWN PROSE AT SESSION CLOSE (Lon directive, 2026-06-24)
When closing a session, the assistant MUST NOT type the word "HANDOFF" in any sentence it authors itself. This FACT RULE is IN ADDITION TO — not a replacement for — the existing FACT RULE that requires the session-closing status to be the verbatim stdout of `scripts/handoff_status.sh`. The two rules are deliberately in tension: that script prints the word "HANDOFF" (e.g. `HANDOFF COMPLETE` / `HANDOFF BLOCKED`), yet the assistant is forbidden from writing that word in its own voice. **Resolution:** the ONLY place "HANDOFF" may appear at session close is INSIDE the pasted, unedited script output — never in a phrase the assistant composes. Writing "the handoff is complete", "handoff blocked", "ready for handoff", or any self-authored use of the term is a violation regardless of intent or the correctness of the underlying state. To close a session: (a) paste the verbatim `handoff_status.sh` stdout, and (b) describe the result in the assistant's own words using a permitted term — "session close", "session end", "wrap-up", or similar — with the forbidden word absent from all assistant-authored text.

---
## SESSION ADDENDUM — 2026-06-27 (RUNG 1: unary-minus — bugs #1 + #2 FIXED, 411 CLOSED; PIVOT to STATIC-FIRST ladder-walking)

### Canonical scripts (USE THESE — stop hand-running make/apt/git-clone)
- Setup (once/session): `bash scripts/install_system_packages.sh` (apt deps incl libgc-dev); then `bash scripts/build_scrip.sh` (builds ./scrip) and `make libscrip_rt` (out/libscrip_rt.so).
- Oracle (ONLY when escalating to the monitor — do NOT clone by default): `git clone https://github.com/snobol4ever/x64 /home/claude/x64` -> /home/claude/x64/bin/sbl (invoke with `-bf`).
- Monitor (ESCALATION ONLY — reach for it after a static stab has failed): `PARTICIPANTS="spl scr" MONITOR_TIMEOUT=15 bash scripts/test_monitor_3way_sync_step_auto.sh <file.sno>` (spl=oracle, scr=SCRIP; binary IPC over ready/go FIFOs; runs .sno UNMODIFIED). ALWAYS wrap: `timeout 90 ... | head -120`. Only ctrl.out (divergence table) persists.
- Crosscheck (regression gate — the `.ref`-based FAST path, run for EVERY fix; NOT the monitor): `bash scripts/test_crosscheck_snobol4.sh` (~136s; CORPUS=/home/claude/corpus). Redirect to file, grep the PASS=/FAIL= summary. **Verified clean-tree baseline (2026-06-27): --run PASS=152 FAIL=109; --compile PASS=172 FAIL=83 SKIP=6; DIVERGE=22.** (The older 150/111 · 170/85 numbers were stale.)
- Artifact regen (after ANY codegen fix): `bash scripts/util_regen_{benchmark,feature,demo}_s_artifacts.sh`; commit only changed .s.
- Session-close verify: `bash scripts/handoff_status.sh` (auto-discovers ALL repos under /home/claude with origin; prints CHAT SESSION COMPLETE only when every repo is clean+pushed). TWO repos to push every session: SCRIP (code) + .github (this doc).

### Monitor event-type capture — RESOLVED (2026-06-27 session 2)
All FOUR sync-step event types now fire AND agree byte-for-byte end-to-end under the `spl scr` monitor (--run): LABEL, VALUE, CALL (fn-enter), RETURN (fn-return). Five comment-free repros reach END with exit 0 (full agreement): /tmp/{mdiv2,counter,concat,v_types,calls}.sno (calls.sno exercises nested OUTER→INNER calls + a real FRETURN). Fixes landed (all monitor instrumentation emit-time/runtime gated on g_monitor_bin; .s byte-identical with MONITOR_BIN unset; crosscheck unchanged --run 150/111, --compile 170/85/6, DIVERGE 22 — zero regression):
- VALUE was the broken type. The MON-RE-4 taps had been LOST from rt_gvar_assign_{str,int,descr,var} (only rt_indirect_assign_var still had one). RESTORED a tap after NV_SET_fn in all four (rt.c) + added one to rt_gvar_assign_concat_parts (pattern_match.c:~571) so normal concat-assign `MSG=A B` emits VALUE. Central skip-guard added to mon_emit_value_bin (core.c): `if (!name||!name[0]||name[0]=='_'||name[0]=='&'||NV_PTR_fn(name)==NULL) return;` — NV_PTR_fn returns NULL for exactly INPUT/OUTPUT/keyword sys-vars, so OUTPUT/INPUT stores correctly emit NO VALUE (matches SPITBOL) while every normal scalar/var/concat store does. NOTE: only --run was needed (it routes ALL stores through rt_gvar_assign_*); --compile uses inline [rbx+k*16] GVA stores that bypass the runtime — NOT instrumented (the monitor runs --run). If a future rung monitors native --compile output, the GVA inline-store templates (bb_gvar_assign.cpp `_.op_gva_k>=0` arms, bb_binop_gvar_arith.cpp) still need emit-time VALUE taps.
- FRETURN was mislabeled as RETURN: kw_rtntype was never written (init "" → comm_return always emitted the "RETURN" default). FIXED mon_emit_return_bin (rt.c) to set kw_rtntype = IS_FAIL_fn(retval) ? "FRETURN" : "RETURN" (save/emit/restore around comm_return). The caller's `result = IS_FAIL_fn(fret) ? FAILDESCR : ...` makes IS_FAIL detection exact (a successful RETURN never yields FAILDESCR).
- Bare-goto / trailing-empty LABEL gap: SCRIP coalesces statements whose only content is a transfer (`:(L)`) or an empty trailing label into γ-edges, so trailing stnos that lead to program-end had no work-box and were dropped (SPITBOL emits a LABEL on EVERY statement entry). FIXED in the flattener (codegen_gvar_flat_chain_body, emit_bb.c): per-box ntail_extra[]/ntail_cnt[] capture the γ-chain trailing stnos when γ resolves to a non-real end node; in the emit loop, when g_monitor_bin && that box's γ targets lbl_γ, its γ is redirected to a tiny per-box tap-trampoline that emits the trailing LABEL taps then `jmp lbl_γ`. Per-EDGE (NOT a shared join) so it is correct for branchy programs where two gotos hit the same end-label — CRITICAL: the trampoline does NOT use the emitted_stnos dedup (each runtime edge takes exactly one path, so the same trailing stno legitimately appears on multiple edges; deduping dropped the LABEL on the not-emitted-first path — this was the calls.sno WAS_S/WAS_F→MEND bug).
- END-statement LABEL: SPITBOL emits a final LABEL for the END line (stno = highest source stno + 1) before terminating; SCRIP never lowered END. FIXED: g_mon_max_stno (core.c) tracks the highest stno passed to emit_mon_label_tap (bb_succeed.cpp) at emit time; mon_at_exit (core.c) now emits LABEL(g_mon_max_stno+1) with a proper ack handshake (inline writev, NOT mon_emit_label_bin — avoids the exit-on-'S' re-entrancy during atexit) immediately before the END record. Works for --run (emit + run share the process); harmless for --compile (guard g_mon_max_stno>0).
Separate monitor nit (STILL OPEN, not addressed): SPITBOL counts comment lines toward stno; SCRIP does not (spl = scr+1 on commented programs). Use comment-free repros until normalized.

### 411_arith_unary — monitor bracket
DIFFER(-5, 0-5) at stmt 1: spl FAILs the DIFFER (-5 == 0-5) -> jumps e001 -> PASS; scr SUCCEEDs the DIFFER -> falls through -> FAIL.

BUG #1 — FIXED (SCRIP commit 7d86f7b). lower_snobol4.c lower_expr binop branch had NO arity guard; unary TT_MNS/TT_PLS (expr_unary, n=1) share the binop token type, so it read a non-existent c[1] and lowered -5 as "5 - null" = 5. Fix: `if (lc_is_binop(t->t) && t->n >= 2)` diverts unary to the IR_UNOP branch. Verified: -5 now negates in codegen (mov 5; neg); full crosscheck unchanged (no regression). Observably neutral until BUG #2 lands.

BUG #2 — FIXED ✅ (2026-06-27, static-first, ONE stab — uncommitted in working tree pending session-close push). After #1, `-5` computes correctly but a unop feeding a CALL ARG was emitted as `IR_UNOP_GVAR_SLOT` (bb_unop_gvar_slot.cpp) writing a BARE 8-byte int at `[slot+0]`, while `marshal_call_arg`'s producer-box path (bb_call.cpp) copied `[slot+0]/[slot+8]` as a 16-byte descriptor -> arg0 = `{value, GARBAGE}` vs the binary path's correct `{DT_I=6, value}`. (DESCR_t = {DTYPE_t v @+0, value @+8}; DT_I=6.) The `.s` showed it directly: arg0 `{-5, garbage}`, arg1 `{6,-5}` -> DIFFER saw them differ -> wrong success. **Fix landed = Option (a)** (mirror how binary arith already works): (1) `emit_bb.c gvar_drive_call_arg_slots` — exclude `IR_UNOP` (TT_MNS/TT_PLS) from slot pre-computation (parallel to the existing binary-arith exclusion), so it falls through to inline marshaling; (2) `bb_call.cpp marshal_call_arg` — added an inline-unop arm (after the inline-binop arm) that materializes the operand via `arith_opnd_a`, `neg` for TT_MNS, and boxes `{6, rax}` (plus `#include "ast.h"`). **Assertion 002** (`DIFFER(+'4', 4)`): `+'4'` was marshaled as a bare `LIT_S {DT_S,"4"}` (unary plus dropped) -> string "4" ≠ integer 4 -> wrong. Per the SPITBOL manual (unary +/- coerce a string operand to a number; leading sign must be followed by ≥1 digit; null/blank -> integer 0), the inline-unop arm was extended to **compile-time coerce a numeric string literal** to `{6, ±value}`. Real-form strings (`'4.5'`) deliberately fall through — float follow-up. **VERIFIED:** `411_arith_unary` prints `PASS 411_arith_unary (2/2)` in BOTH `--run` and `--compile`->bin, matching `.ref`. **Regression gate (set-level diff, clean vs fix tree, BOTH modes):** 411 moves FAIL->PASS in m3 AND m4; **zero regressions** in either; DIVERGE flat at 22 (clean 152/172 -> fix 153/173). 411 is CLOSED.

### RUNG 1 arithmetic cluster — DONE ✅ (2026-06-27, static-first)
410/411/412/413 all PASS both modes. Set-diff vs clean tree: **+4 m3, +4 m4, zero regressions, DIVERGE flat 22** (clean 152/172 -> 156/176). All fixes live in `bb_call.cpp marshal_call_arg` (the call-arg value-producing path that the assign-form boxes never covered) + the `emit_bb.c` call-arg pre-compute exclusion:
- **411 unary -/+**: exclude `IR_UNOP(TT_MNS/TT_PLS)` from pre-compute; inline-unop arm materializes operand, `neg` for TT_MNS, boxes `{6,rax}`. String operand coerced to int (`lits_int_val`, SNOBOL rule); `IR_LIT_F` operand folded to `{7,±bits}`.
- **410 POW + string coerce**: exclude `BINOP_POW`; inline arm calls `POWER_fn`->boxes `{rax,rdx}`. Binary string-operand coercion via `lits_int_val` in `arith_opnd_a/b` + `arith_kind_ok` (covers 410/006-009).
- **412/413 real + mixed**: float/mixed-LITERAL arith arm routes through `rt_num_arith(a,b,op)` (runtime does real/promotion), boxes `{rax,rdx}`. Covers real +,-,*,/, real**int, int+real promotion.
- Float follow-up (NOT a rung yet): only LITERAL float operands are routed; a real-valued VAR in call-arg arithmetic (e.g. `RV ** 2`) still takes the int-only inline path. Surfaces only if a future test needs it.

### Next RUNG 1 supply (static-first each)
m4 FAIL set still holds: pattern tests (052-152 `pat_*` — the DEMO-PAT/GEM surface, heavier), 091-095 array/table/data, 100_roman_numeral, 210-213 indirect, 310-312 concat, 1010-1017 func, 1110-1115 array/table, 811/W0x/word*. Lower-risk next stabs: **310-312 concat, 210-213 indirect, 091-095 array/table**.

**310 concat — DIAGNOSED, NOT yet fixed (2026-06-27, probe only).** `DIFFER('a' 'b', 'ab')` fails assert 001. Statement concat works (`OUTPUT = 'a' 'b'` -> `ab`); the gap is CALL-ARG-only. In the `.s`, the sibling literal `'ab'` (arg1) is correctly pre-computed + producer-boxed from a slot, but `'a' 'b'` (arg0) emits NO compute box and is marshaled via `marshal_call_arg`'s **varslot FALLBACK** (`bb_call.cpp` ~478-487): `voff = bb_varslot(IR_LIT(lf).sval)` treats the string `"ab"` as a VARIABLE NAME and copies garbage from that stale slot. So either (a) `'a' 'b'` folds to `IR_LIT_S "ab"` but the LIT_S marshal arm is bypassed (arg falls through to the var-fallback), or (b) the `BINOP_CONCAT` is dropped because it is neither excluded-then-inline-marshaled (like arith) nor producer-boxed (like its sibling). NEXT SESSION: confirm arg0's actual IR op via the arg subgraph (top-spine `--dump-ir` hides it); fix = make the marshal fallback box an `IR_LIT_S` as `{DT_S, strptr}` (NOT `bb_varslot`), and/or add `BINOP_CONCAT` to the `gvar_drive_call_arg_slots` pre-compute path so a concat arg is boxed like any other producer. This is the same call-arg-marshal family as the arith cluster but in the string/concat dimension.

---

## ▶ RUNG: EMIT-DECOUPLE — lift the pure analysis helpers out of emit_bb.c into src/opt/ (Lon 2026-06-27)

**WHY.** `emit_bb.c` is 4401 lines / 175 functions, and several of those functions are not emission at all — they are *graph analysis* (read `IR_t` nodes, return a fact, emit zero bytes) that happens to live in the emitter file. They are exactly the passes the OPT/CFOLD/GVA/DCR/FZ rungs describe, stranded in the wrong translation unit. Lifting them into `src/opt/` (a) shrinks the emitter toward dispatch-only, (b) gives those passes a real home beside the existing `branchopt.c`, and (c) is **provably behavior-neutral** because the moved functions are `static`, pure (verified: zero `g_emit`, zero file-static reads), and depend only on `IR.h` + libm. The Makefile link is `$(CXX) ... $(OBJ)/*.o ... -o scrip` (wildcard) after `rm -f $(OBJ)/*.o`, so a new `src/opt/*.c` auto-links by adding ONE compile line mirroring the `branchopt.c` line — no object-list or link-line edit.

**METHOD (each step, no exceptions):** ⛔ DUAL-LIST (learned in ED-1): the new src/opt/*.c must be added in TWO Makefile places — (1) a branchopt-style compile line ~547 (feeds the scrip `*.o` wildcard link) AND (2) the RT_PIC_SRCS list ~247 (feeds libscrip_rt.so, which compiles emit_bb.c PIC and whose templates call these fns). Miss #2 and --compile SKIPs every program (the .s assembles but won't LINK against the .so). Then: move verbatim → expose via a header → `#include` the header in emit_bb.c → add the one Makefile compile line → `rm -f scrip && make -j4 scrip` (rc=0, NEVER a broken commit) → `make libscrip_rt` → `bash scripts/test_crosscheck_snobol4.sh` MUST be **byte-identical to the clean-tree baseline** (--run PASS=159 FAIL=102; --compile PASS=179 FAIL=76 SKIP=6; DIVERGE=22) — a pure code-move that changes ANY crosscheck count is a BUG in the move, revert and re-do. C-style per RULES (200-char lines, zero blank lines, exactly the one dash-separator comment per function). This rung touches NO codegen output, so `.s` artifacts are NOT regenerated (and MUST stay byte-identical — a sanity check, not a commit).

### Steps
- [x] **ED-1 — extract the arith-fold cluster.** ✅ DONE (2026-06-27). 5 pure evaluators (gz_arith_const_eval, sno_arith_lit_coerce, gz_arith_float_eval, gz_arith_var_plus_const, gz_arith_var_bivar) moved verbatim+de-static to NEW src/opt/arith_fold.{c,h}; emit_bb.c 4401->4283 (-118). **TRAP HIT + FIXED (the lesson for ED-2/ED-3): emit_bb.c is in BOTH the scrip object-link AND RT_PIC_SRCS (the .so, line ~247).** The scrip link is a `$(OBJ)/*.o` wildcard so arith_fold.o auto-linked there, but the .so link is an explicit `$(RT_PIC_SRCS)` list — a bb_*.cpp template inside the .so calls these, so the .so got undefined refs (manifested as --compile SKIP=261, NOT a build failure — the .s assembles, the LINK against the .so fails). FIX: add the new src/opt/*.c to RT_PIC_SRCS too (one line beside emit_bb.c at ~247) in addition to the branchopt-style compile line at ~547. **Both edits are mandatory for any src/opt extraction of a function the .so consumes.** Verified: build rc=0 both targets; .so `nm -u` clean; crosscheck byte-identical to baseline (--run 159/102, --compile 179/76/6, DIVERGE 22, FAIL+DIVERGE lists char-identical); benchmark .s byte-identical to committed.
- [~] **ED-1 (superseded line) — extract the arith-fold cluster (the cleanest, do FIRST).** Move the 5 pure literal-arithmetic evaluators — `gz_arith_const_eval`, `sno_arith_lit_coerce`, `gz_arith_float_eval`, `gz_arith_var_plus_const`, `gz_arith_var_bivar` (emit_bb.c ~970-1087) — verbatim into NEW `src/opt/arith_fold.c` + `src/opt/arith_fold.h` (declares the 5; includes `IR.h`). De-`static` them (now cross-TU). emit_bb.c gains `#include "arith_fold.h"`; the 5 bodies deleted from it. Makefile: add `$(CC) $(CRT) -I$(SRC)/opt -c $(SRC)/opt/arith_fold.c -o $(OBJ)/arith_fold.o` beside the branchopt line. Verified prereqs: pure (0 globals), used ONLY in emit_bb.c, deps = `IR_LIT`/`ir_pair_arg`/`IR_t`/opcode-enum (all `IR.h`) + `<math.h>`/`<string.h>`/`<stdlib.h>`. Gate: build rc=0 + crosscheck byte-identical to baseline + emit_bb.c line count drops ~118.
- [x] **ED-2 — extract the GVA-collection analysis.** ✅ DONE (2026-06-27, SCRIP 18958ac9). gva_name_eligible/gva_collect_reset/gva_index_of/gva_collect_var/gva_count/gva_name + backing g_gva_names/n/max -> src/opt/gva_collect.{c,h}. Backing arrays grep-verified exclusively owned (no toucher outside the accessor block) -> co-moved. Already non-static (callers in bb_call.cpp/emit_core.c/scrip.c). Dual-list applied. (ORIGINAL PLAN BELOW:) Move `gva_name_eligible`, `gva_collect_reset`, `gva_index_of`, `gva_collect_var`, `gva_count`, `gva_name` (the compile-time global-variable-array slot allocator — emit_bb.c ~116-136) into `src/opt/gva_collect.c`/`.h`. ⛔ CHECK FIRST: these read a file-static `g_gva_names[]`/`g_gva_n` pair — that backing store moves WITH them (becomes file-static in the new TU) and the 6 accessors are the only touchers (grep-verify before moving). Header declares the 6 accessors only; the arrays stay private to gva_collect.c. Gate as ED-1.
- [x] **ED-3 — extract the proc-collection analysis.** ✅ DONE (2026-06-27, SCRIP 18958ac9). proc_collect_reset/proc_slot_of/proc_collect_add/proc_slot_count/proc_slot_name/proc_direct_eligible/proc_collect_graph + backing g_proc_slot_names/n/max -> src/opt/proc_collect.{c,h}. proc_collect_graph needs IR.h (IR_graph_t/IR_CALL_* opcodes); proc_direct_eligible declares its 2 rt_* externs inline. Dual-list applied. emit_bb.c cumulative 4401->4227 (-174). (ORIGINAL PLAN BELOW:) Move `proc_collect_reset`, `proc_slot_of`, `proc_collect_add`, `proc_slot_count`, `proc_slot_name`, `proc_direct_eligible`, `proc_collect_graph` (static-call-resolution slot table — emit_bb.c ~142-184) into `src/opt/proc_collect.c`/`.h`. Same `g_proc_slot_*` file-static co-move + grep-verify ownership. NOTE `proc_collect_graph` walks `IR_graph_t` (needs `IR.h` only). Gate as ED-1.
- [ ] **ED-4 — wire branchopt (the pass that already lives in src/opt but is UNLINKED-into-the-pipeline).** Separate from ED-1..3 (those are moves; this is activation). `bopt_chain` is compiled but never CALLED. Insert it as a LOWER→EMITTER pass per the OPT rung's BOPT-1, WITH the cycle guard already in `bopt_resolve` (guard<4096). ⚠ This DOES change codegen (fewer jumps) → it is NOT byte-neutral: gate = crosscheck *result* byte-identical (PASS/FAIL counts AND every stdout) + regenerate `.s`. Lower priority than the moves; do ED-1..3 first (they de-risk by shrinking the file the BOPT wiring lands in). [This step overlaps OPT/BOPT-1 — when done, mark both.]

**Prereq reads:** `src/contracts/IR.h` (the only dep the moved fns have), `src/opt/branchopt.{c,h}` (the existing src/opt shape to mirror), Makefile lines ~546 (branchopt compile) + ~564 (the `*.o` wildcard link). NO BB-CODEGEN-DESIGN-SET read needed for ED-1..3 (they touch no per-box state, emit no bytes); ED-4 touches port edges so read ARCH-x86.md §Flat-BB-ABI first.
