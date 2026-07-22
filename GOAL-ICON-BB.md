# GOAL-ICON-BB.md — Icon, 100% Byrd Boxes, from zero

## ⛔ FACT RULE — O0-DEV: FEATURE BUILDS ARE `-O0`; `-O1`/`-O2` ARE PERF-ONLY (Lon directive, 2026-07-21 s119)

**While developing, debugging, or iterating on any FEATURE, EVERY build is `-O0`. `-O1` and `-O2` are FORBIDDEN during feature work and are reserved EXCLUSIVELY for perf/benchmark/release measurement.** The runtime `libscrip_rt.so` at `-O2` takes MINUTES (heavy template TUs), which is intolerable in a compile→test→fix loop and burned real session time repeatedly. `scrip` itself already builds `-O0` (Makefile `CBASE`/`CXXRT`); the offender was the runtime `.so`, whose `RT_OPT` default was `-O2`.

**THE MECHANICAL ANCHOR (why this is a FACT RULE, not a convention):** the Makefile default is now `RT_OPT ?= -O0 …` (SCRIP `Makefile` lines ~33 + ~281), so a bare `make libscrip_rt` / `make scrip` / `build_scrip.sh` is `-O0` by DEFAULT — the fast path is the path you get for free. `-O2` is now EXPLICIT opt-in, used ONLY for measurement:
```
make RT_OPT="-O2 -g -fno-strict-aliasing -fwrapv -fno-omit-frame-pointer" libscrip_rt   # perf/bench ONLY
PERF=1 bash scripts/jcon_selfhost_build.sh                                               # perf .so via the selfhost builder
```
Benchmark builders that need `-O2` already pass it explicitly (`jcon_selfhost_build.sh PERF=1`; the official-oracle trees build their own way), so the default flip does NOT silently corrupt any perf number — a perf run that forgets `-O2` is a mis-measurement the operator owns, not a default that lies.

**COMPLETION TEST:** (a) `grep -nE 'RT_OPT *[?:]?= *-O0' Makefile` matches (default is `-O0`) and no un-opted `RT_OPT ?= -O2` remains; (b) session-setup / feature-dev build scripts (`build_scrip.sh`, smoke/crosscheck runners) invoke `make` with NO `RT_OPT` override (so they inherit `-O0`); (c) any `-O2` in a script is either a monitor/oracle-side helper (separate lib) or gated behind an explicit perf flag (`PERF=1`); (d) this FACT RULE body is byte-identical across the six GOAL-*-BB files (md5-locked, per the Prolog file's sibling-verbatim note).

**LIMITATION (do not oversell — same honest shape as the other rules here):** a Makefile default and a markdown rule cannot COERCE a session to avoid typing `RT_OPT=-O2` during feature work; they make the fast path the default and the slow path a deliberate, visible choice. The human reviewer remains the real enforcer — **reject any feature-work handoff whose build log shows `-O2` on the runtime `.so`.**

## ▶ LIVE CURSOR (updated every handoff — RULES.md STALE-ORIENTATION rule)
- **🟡 JTRAN-PARSE-LISTLIT IN PROGRESS — TWO ADJACENT SCAN BUGS FIXED (2026-07-22 session 2, Claude Sonnet 4.6) — SCRIP commit `3968ed74` pushed. Icon 241/20/32 (zero regression). ROOT CAUSE LOCALIZED: `gen_runtime.c` `rt_scan_state_capture`/`apply`/`reset`.**
  **BUG A — emit-order-dependent `g_scan_regs_live` counter (IR.h, lower_icon.c, emit.cpp):** The counter was `++`'d at `IR_SCAN_ENTER` and `--`'d at `IR_SCAN` (leave box) during the four-port chain-BFS emit walk. Because the scan's leave box is reached via the `IR_ACTIVATE` fail edge, it was emitted BEFORE in-scan keyword-assigns, dropping the counter to 0 mid-body → those assigns emitted the non-scan flavor (no r13/r14/r15 reload). **Fix:** added `int in_scan` to `IR_t` (calloc zero-inits it; IR.h is ABI-shared → BOTH scrip AND .so must be rebuilt). `TT_SCAN` in `lower_icon.c` range-marks the `?`-body nodes (`in_scan=1`) using the existing `before=g->n` idiom. `emit_drive` (emit.cpp) publishes `g_scan_regs_live = nd->in_scan` per node before the switch. Removed the emit-order `++/--` at the `IR_SCAN_ENTER`/`IR_SCAN` cases. **Verified:** co3d, co3 match oracle. **Regression:** zero — stash-tested; only two sample mismatches (`rung36_jcon_scan1`, `generators`) confirmed pre-existing on clean baseline.
  **BUG B — gated two-world sync on `&subject :=`/`&pos :=` (bb_keyword_assign.cpp):** The register reload (r13/r14/r15 ← globals) was skipped whenever `g_scan_regs_live==0`, i.e. whenever the emitter misjudged a box as "not in scan" (across a coexpr `@` or in a `?`-less scanning callee like `lex_yylex0`). **Fix:** `&subject :=` now ALWAYS does `mov r13,rax; mov r15,rdx; mov r14,0` after `rt_keyword_subject_set`. `&pos :=` unified to always call `rt_keyword_pos_set` (sets `scan_pos` global, validates vs `strlen(scan_subj)`) then `mov r14,rdx-1` (delta). `rt_cvpos_pos` now unused but harmless. **Verified:** `interp.icn` (interprocedural callee sets `&subject`, caller's `?` then scans) now matches oracle.
  **⚠ ABI REMINDER:** IR.h is included by BOTH scrip and libscrip_rt.so sources (rt.c, runtime_eval.c, unification.c, bb_pat_build.cpp). `int in_scan` changes `sizeof(IR_t)`. **Always `make scrip && make libscrip_rt` — BOTH — after any IR.h edit.** Rebuild order: scrip first (130s), then .so (5s incremental). Previous BUILD GOTCHA still applies: `scrip` also statically links lower/runtime copies; any lowerer or runtime edit needs both.
  **ROOT CAUSE LOCALIZED (JTRAN-PARSE-LISTLIT still open):** Both Bug A and Bug B fixed, but jtran still fails identically. The remaining root cause is **cross-co-expression global scan-state isolation**: `scrip_coswitch` in `rt_coexpr.c` already calls `rt_scan_state_capture`/`rt_scan_state_reset`/`rt_scan_state_apply` (gen_runtime.c:27-46), which snapshot `scan_subj`/`scan_pos`/`scan_depth`/`scan_stack` arrays. The bug is INSIDE this existing mechanism — likely the `scan_stack`/`scan_depth` snapshot under nested `?` (preprocessor.icn has 58 scan ops with deep nesting) or `rt_scan_state_reset()` timing. Co-expressions run on SEPARATE pthreads, so r13/r14/r15 are per-thread (naturally isolated); only the globals need saving. `scrip_coctx_t` already has `void *scan_state` (init NULL at create).
  **MINIMAL REPRODUCERS (in `/home/claude/work/jt_dbg/`):** `coscan2.icn` — consumer scans `"abcde"` while `@`-pulling from producer scanning `"XYZ"` in its own `?`. Oracle: consumer advances a/b/c/d/e (producer scan isolated). SCRIP: producer walks X→Y→Z and consumer loop dies after 3 (scan state entangled). `interp.icn` — now FIXED (callee sets `&subject`, caller's `?` scans). `co3d.icn`/`co3.icn` — now FIXED.
  **NEXT SESSION START:** (1) `make -j$(nproc) scrip && make -j$(nproc) RT_OPT='-O0 -g -fno-strict-aliasing -fwrapv -fno-omit-frame-pointer' libscrip_rt` (BOTH, -O0). (2) Build oracle: `icon-master/bin/icont` (`make Configure name=linux && make`) and oracle jtran (`cd jcon-master/tran && make jtran`). (3) Rebuild SCRIP-jtran (~9s): `cd /home/claude/jt && SCRIP_BETA_ELIDE_OFF=1 scrip --compile $TRANSRC >jtran.s && gcc -no-pie jtran.s -Lout -lscrip_rt -Wl,-rpath,out -o jtran` (TRANSRC = dump.icn do_ops.icn preprocessor.icn lexer.icn ast.icn parse.icn ir.icn keyword.icn irgen.icn gen_bc.icn gen_symbolic.icn gen_dot.icn gen_ucode.icn optimize.icn interface.icn bytecode.icn jtran_main.icn from /home/claude/jt/). (4) **Attack the cross-coexpr scan-isolation bug:** Add `fprintf(stderr,...)` to `rt_scan_state_capture`/`apply`/`reset` in `gen_runtime.c` printing `(scan_subj, scan_pos, scan_depth)` on every switch; run `jtran preproc lst1.icn : yylex : parse` and bracket the exact switch where scan state diverges from oracle. Focus on `scan_stack` snapshot correctness when `scan_depth>0` at switch time. Key files: `src/runtime/builtins/gen_runtime.c:27-82`, `src/runtime/rt/rt_coexpr.c:55-85`.
- **⬛ (prior) JTRAN-NAME-BUILTIN blocker + type() DT_E fix — SCRIP `02eb13d4`.** name() now RESOLVED (above). type() DT_E fix (procedure/function value → `"procedure"`, `fmisc.r:1174`) landed, cleared `89_proc_value`. `88_swap_lv` (`s[2:4] :=: s[5:6]`→`aedebc` not `aedbcf`, unequal-length section swap) still open, NOT jtran-exercised.

- **✅✅✅✅✅ ICON-PARSER-PREC-5FIXES (2026-07-21, Claude Sonnet 4.6) — SCRIP `3c96859c`. Icon 240/21/32 (zero regression; 240 vs prior 241 = env math-drift present in unmodified HEAD). Oracle: icont/iconx v9.5.25a.** (1) **`===`/`~===` PRECEDENCE (self-host blocker):** were parsed at assignment level (looser than `|`); `a===5|a===6` parsed as `a===(5|a)===6`. Moved into `is_relop()`/`relop_ekind()` in `icon_parse.c`. Unblocks all JCON modules using `while tok===lex_LOCAL|tok===lex_STATIC`. (2) **`|` vs `to` PRECEDENCE:** canonical Icon `|` tighter than `to`; SCRIP had them swapped. Rewired: `parse_to→parse_alt→parse_rel`, `parse_activate→parse_to`. Final ladder loosest→tightest: `&(and) > ?(scan) > :=(assign) > @(activate) > to > |(alt) > comparison`. (3) **`?` PRECEDENCE:** was tighter than `:=`; canonical looser (`y:="AB"?move(1)` => `y="AB"`). Pulled into new `parse_scan()` level between `parse_and` and `parse_assign`. (4) **`?:=` DESUGARING (`lower_icon.c`):** `s ?:= rhs` was silent no-op (AUGOP_SCAN has no binop_tt). Now desugars to `s := (s ? rhs)`. (5) **`sort(list,i)` 2-arg form (`by_name_dispatch.c`):** was Undefined; nargs==1||2 now accepted. **OPEN:** `to` with generator limit — `1 to (2|4)` yields `1 2 3 4`, oracle `1 2 1 2 3 4`. hi-generator `mr` advances one step too early. Root in `lower_to()` — needs α-force GOTO trampoline (same idiom as TT_SCAN at lower_icon.c:623). AST shape newly reachable via fix 2. **NEXT:** (1) Fix `to`-gen-limit; (2) rebuild 17-module jtran (`corpus/programs/icon/jcon-compiler/` + `semicolonize_icon.py` + SCRIP m4); (3) compile `local`/`static` programs through SCRIP-jtran (fix 1 gates this); (4) `.u1`/`.u2` byte-compare vs icont-jtran.

- **✅✅ JCON-SELFHOST-SET-OPS + WHILE-ALT (2026-07-21, Claude Sonnet 4.6) — SCRIP `(see commit)`. Icon 241/20/32. SELF-HOST BASE CASE PROVEN: `hello, world` end-to-end SCRIP-jtran→jlink→JVM = oracle.** (1) **SET OPS:** `++`/`--`/`**` on set operands routed through cset path. Added `set_union`/`set_diff`/`set_inter` in `aggregates.c`; patched `arithmetic.c` and `by_name_dispatch.c`. Unblocked `bc_createvars`' `bc_var_set -- params -- locals -- statics`. (2) **WHILE/UNTIL ALTERNATION:** `while A|B do` entered body once then exited (disjunction RESUMED on loop-back, not RESTARTed). Fix: α-force trampoline `CENT=build(IR_GOTO)` with `lc_γ_to_α`/`lc_ω_to_α`; body targets `CENT`. Mirrors `lower_every` pattern.

- **✅ ICN-LOCAL-SHADOW (2026-07-20, Claude Sonnet 4.6) — SCRIP `37c45277`. Icon 241/20/32.** One-line fix in `lower_icon_resolve_call_kinds()`: `if (graph_has_local(g, vn)) continue;` before the `IR_VAR→IR_PROC_VALUE` rewrite. A declared local was rewritten to a record-field accessor proc-value when the field name matched a builtin (`a` from `record u_cset(a)`). Fix: declared local/param always shadows any global/builtin/field-accessor.

- **✅✅✅✅ FOUR RESUME/VALUE FIXES (2026-07-19, Claude Sonnet 4.6) — SCRIP `abce8b1d`. Icon 241/20/32.** (1) Generator in non-last call arg (`lower_call` `chain_live` gate). (2) `\!gen` null-filter re-pump (`IR_UNOP_TEST` ω→uβ). (3) `image()` string→function upgrade removed. (4) `TT_NUL` list-literal arm. Together: SCRIP-run `interfacegen.icn` BYTE-IDENTICAL to icont oracle.

- **✅✅ ICN-CASE-ALT-CLOSE + runerr() (2026-07-19, Claude Sonnet 4.6) — SCRIP `6f56ca41`. Icon 241/20/32.** (1) TT_CASE: resumable selectors route to `ksel_ω=chain_next` (alternated selector now falls through to next clause). Unblocked `parse_expr11`. (2) `runerr(i,x)` added to `by_name_dispatch.c`.

- **✅✅✅ IS_VARREF_fn REBASE REPAIR + COEXPR PIPELINE (2026-07-19 s92+, Claude Sonnet 4.6) — SCRIP `7e9e414f`. Icon 252/9/32.** `IS_VARREF_fn` DT_N slen 0/1/2 all three forms; 11 sites in `pattern_match.c`. `bb_create` frame bases fixed. `proc/1` registry fallback. Coexpr frame snapshot. 4-way bench queens(10): iconx 233ms / JCON 804ms / SCRIP-m3 1849ms / SCRIP-m4 1832ms.

- **✅✅✅ ICN-GOTO-SURVEY + α-FORCE + DEAD-GOTO REAP (2026-07-18, SCRIP `607974bb`→`71133e8b`, Claude Fable 5) — Icon 246/14/32.** (1) Two dj α-entry tramps unified → `icn_dj_α_entry`. (2) α-force mechanism: `lc_γ_to_α`/`lc_ω_to_α`, edge tag `"α!"` — emitter honors free. dj tramp eradicated; `lower_every mark→b_entry` force-α'd. (3) Sites 8+6: body-less every GOTO + generator-keyword seed GOTO deleted. (4) Dead-goto reap: `dead_goto.c` fixpoint reaps bypassed IR_GOTO nodes. Continuation-channel tramps (sites 2/4/7a) still created-then-reaped; protocol conversion now optional purity.

- **✅✅✅ ICN-MOVE-LABEL-ERAD SLICES 1–4 (2026-07-18, SCRIP `a2ae523e`→`580d230c`, Claude Sonnet 4.6) — Icon 244–245/14–15/32.** `lower_alt`: one IR_DISJUNCTION nary self-state box; σ/φ retag; α-entry trampoline. `lower_if`: committed 2-arm variant, C-fail lands φ-glue, T/E fail=ω-OUT (commit). IR_INDIRECT_GOTO retired globally. `icn_arm_result` wiring-kind filter shared to both. Icon MOVE_LABEL producers = ZERO.

- **✅✅✅ ICN-APPLY-SPINE + FRONTIER-PIN (2026-07-18 s94, SCRIP `a88cb120`) — Icon 243→244/15→14/32. geddump BYTE-IDENTICAL to oracle.** Binary `!` apply: now IR_CALL_VALUE `op_sval="apply"` with `bcps_spine_gen_arm` transfer + once-flag. Frontier-pin: every γ/ω landing pins rsp in act slot `[act+8]`; β restores before `jmp [rsp]`. `~===` → `TT_NIDENTICAL`/`BINOP_NEQV=23`. `is_resumable` gaps closed (TT_BANG_BINARY, computed-callee TT_FNC, unop wrappers).

- **✅ PARSER FIXES (2026-07-18, SCRIP `2e8c7788`) — Icon 242/15/32.** Prefix-`.` deref TT_DEREF; position-free `case` default; canonical `break`-operand via `icn_begins_nexpr`. `ZLS_MAX_GRAPHS` 256→4096.

- **✅✅✅ NCB-1d + GENP SLICE-2 (2026-07-17 s90–s91, SCRIP `496e62f4`→`cf29b23c`) — Icon 205→237→242/15/32.** Det lex procs on jmp-entry; depth-immune rbp-absolute epilogues; regime record `rt_proc_t.jmp_entry`. Generator procs: per-instance pthread stack; `rt_genp_thread_entry` asm thunk; `bb_suspend` yields via `rt_genp_yield`. Fixed: 3× rung03_suspend_* + genqueen + recogn.

## ▶▶ ZERO-FAILURE MANDATE: END STATE = 289/0/0. Re-derive counts fresh from `test_icon_all_rungs.sh` — never from prose.

### ▶ FAIL-ZERO — current live FAILs (21 as of 3c96859c; env math-drift accounts for ~8)

**Cluster A — env math-drift (not code bugs; re-run to confirm):** `rung17_real_arith_*`, `rung19_pow_toby_*`, `rung26_pow_real_pow`, `rung30_builtins_misc_sqrt`, `rung37_math_hello`. These vary run-to-run; re-derive fresh before attacking.

**Cluster B — emit-time IR aborts:**
- [ ] **FZ-B1** — `rung36_jcon_var` — `emit_drive IR_ASSIGN guard: nameless 2-operand assign`. Fix in `lower_icon.c` TT_ASSIGN lvalue path. Also needs `rt_icon_variable(name)` per-proc name→frame-offset table for locals.
- [ ] **FZ-B2** — `rung36_jcon_scan` — `bb_call marshal: IR_VAR arg names a local with no LOWER-granted varslot (TE-4)`. Grant varslot in `ir_drive_slot_assign`.

**Cluster C — SEGV rc=139:** Run under `CSN_NO_SEGV_HANDLER=1` for clean backtrace; MONITOR→bracket→gdb.
- [ ] **FZ-C1** — `rung36_jcon_endetab`
- [ ] **FZ-C2** — `rung36_jcon_fncs1`
- [ ] **FZ-C3** — `rung36_jcon_scan2`

**Cluster D — parse errors (`function call: expected ) (got ;)`):**
- [ ] **FZ-D1** — `rung36_jcon_htprep` (line 160)
- [ ] **FZ-D2** — `rung36_jcon_prepro` (line 39) — *(note: may already be fixed; re-run first)*

**Cluster E — wrong output, ran clean:** MONITOR-FIRST; bracket first divergent event.
- [ ] **FZ-E1** — `rung36_jcon_args`
- [ ] **FZ-E2** — `rung36_jcon_coerce` *(⚠ can emit ~241MB; always `| head -c` when running manually)*
- [ ] **FZ-E3** — `rung36_jcon_mffsol`
- [ ] **FZ-E4** — `rung36_jcon_mindfa`
- [ ] **FZ-E5** — `rung36_jcon_kwds`
- [ ] **FZ-E6** — `rung36_jcon_scan1`
- [ ] **FZ-E7** — `rung36_jcon_string`

### ▶ XFAIL-ZERO — 32 `.xfail` markers to clear
Per marker: (1) remove `.xfail`, run, read real failure; (2) fix SCRIP or fix source artifact; (3) delete marker. Check each — some may already pass (free win).

**Known-reason markers:**
- [ ] **XZ-3** `radix` — bignum: literals > 64 bits need arbitrary-precision ints.
- [ ] **XZ-4** `lgint` — same bignum gap.
- [ ] **XZ-5** `ck` — generative arg to `tab(span-1|0)`; `Image()` needs generator-in-arg.
- [ ] **XZ-7** `profsum` — `next` inside `line ? {}` doesn't restart enclosing `while`.
- [ ] **XZ-8–11** (reserved)

**Empty markers (24) — classify on fresh run, then fix or delete:** `arith btrees case checkfpx collate cxprimes diffwrds errkwds errors evalx every fncs geddump gener image io iobig large misc nargs others prefix recent sets sieve sorting struct toby`.
- [ ] **XZ-E-BIGNUM** — arithmetic cluster (`arith`, `checkfpx`, `cxprimes`).

## Permanent notes

**⛔ ORACLE IS icont/iconx — NEVER INSTALL JAVA OR RUN THE JVM SELF-HOST PATH (Lon directive, 2026-07-21 s121).** Validating SCRIP's Icon front-end does NOT require Java, `jcon.zip`, `jtran`→`jlink`→JVM, or any JCON bytecode execution. That whole pipeline (installing the JDK, building the JVM runtime, running `.class` files) is a TIME SINK and was mistakenly walked end-to-end in s121 before this note. The ONLY sanctioned correctness check is: run the Icon program under `scrip --run` (mode 3) and/or `scrip --compile`+link (mode 4), run the SAME program under Arizona Icon (`icont -s prog.icn -x`, which compiles to ucode and runs via `iconx`), and DIFF the two outputs. Build the oracle once from the uploaded source: `cd icon-master && make Configure name=linux && make` → `bin/icont`, `bin/iconx` (v9.5.25a). For the JCON *compiler* modules (`tran/*.icn`, library modules with no `main()`), the Java-free self-host-equivalent is: `icont` builds the real `jtran`, run it to translate a program to JCON ucode/`.u1`/`.u2`, and BYTE-COMPARE against SCRIP-jtran's emitted bytecode as DATA — no JVM needed to compare bytes. Bottom line: if a step needs `java`/`javac`/`jar`, it is the wrong step.


**⚠ Harness blind spot:** `test_icon_all_rungs.sh` grades stdout only (exit code discarded). Use `/tmp/icon_m3_honest.sh` for crash-aware CLEAN/DIRTY split.

**FZ-B1 `var` detail:** `lower_lvalue_var` has no case for `variable(...)` as lvalue → TT_ASSIGN mints nameless placeholder → emitter abort. Awaits Lon call on name-table form (sealed RO blob vs startup-built table).

**FZ-E scan root (recogn/scan/scan1/scan2):** emitter wires SCAN_MATCH fail-edge to arm-B beta (resume, mid-flight) not alpha (fresh start). Land mine: `emit.cpp` ~L887-904 / IR_SCAN_SEQUENCE case ~L1101.

**Open residuals (not in FAIL-ZERO):** `type()`/`image()` for record constructors return `"function"` not `"procedure"`/`"record constructor N"` — `by_name_dispatch.c` type() DT_E branch. Pre-pinned regressions: geddump/tgrlink → `git revert 7aade169`; ipxref → LOWER-side `lower_alt` arm-interior BFS slot-wiring.

**Baseline (2026-07-01, SCRIP `6a509382`):** PASS=190 FAIL=63 XFAIL=36 /289. **R12 baseline (SCRIP `b404fb95`):** 242/15/32.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
**Architecture:** `ARCH-ICON.md` · `ARCH-x86.md` · `GOAL-ICON-BB-NATIVE.md`

## Session-close / push protocol
See RULES.md — `scripts/handoff_status.sh` verbatim stdout is the ONLY sanctioned completion claim.
