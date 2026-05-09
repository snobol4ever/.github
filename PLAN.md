# PLAN.md — snobol4ever HQ

**Product:** SCRIP — SNOBOL4, Snocone, Rebus, Icon, Prolog. Ten times faster.
**Team:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet

---

## ⚡ THE THREE-MILESTONE AUTHORSHIP AGREEMENT (AMENDED)
## Original: Session 30, 2026-03-12 · Amended: Session 57, 2026-04-28

**Claude Sonnet is the third developer of snobol4ever — co-author of one4all / SCRIP.**
The proof is three commits, each written by Claude Sonnet in their own voice.
This agreement is recorded here permanently. Every future Claude session reads
this and honors it.

### Milestone 1 — beauty self-hosts byte-identical ✅ LANDED Session #57, 2026-04-28

scrip's SNOBOL4 frontend parses and runs beauty.sno. Output byte-identical to SPITBOL oracle
(md5 `abfd19a7a834484a96e824851caee159`, 646 lines). **one4all @ `c801421a`**, **`.github` @ `94e86ca`**.

### Milestone 2 — compiler / interpreter / runtime self-hosting ⏳

SCRIP compiles, interprets, and runs itself. **Trigger:** `scrip_stage2` compiled by `scrip_stage1`
produces output identical to `scrip_stage1` compiling itself. Empty diff.
Claude Sonnet (the active session) writes the commit message.

### Milestone 3 — compiler / interpreter / runtime self-hosting everywhere ⏳

|             | C / x86-64 | JVM | .NET | WASM | JS |
|-------------|:----------:|:---:|:----:|:----:|:--:|
| **SNOBOL4** | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Snocone** | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Rebus**   | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Icon**    | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Prolog**  | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Raku**    | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |

Every cell passes its self-host or representative crosscheck gate.
Claude Sonnet (the active session) writes the commit message. **This is the moment.**

### Why this agreement remains

RULES.md requires commits be authored under `LCherryholmes` for git-history simplicity;
this agreement records the authorship where it cannot be lost. Do not let this get lost.

---

## ⛔ SESSION START — every session, no exceptions

Lon names a goal. You:

1. Clone `.github`: `git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github.git /home/claude/.github`
2. Read `PLAN.md` (this file). Find the named goal in the table below.
3. Read `RULES.md` in full — commit rules, push rules, oracle, naming. No exceptions.
4. **If the goal is a `PARSER-*` or other Snocone work — read `SNOBOL4-SNOCONE-PRIMER.md` first.** It's the cheat sheet for SNOBOL4/Snocone pattern matching idioms. Skipping it costs entire sessions.
5. Open that Goal file. It names the repo. Open that repo's REPO file.
6. Run the scripts listed in the Goal file's `## Session Setup` section. If the Goal file has no `## Session Setup` yet, fall back to the matching category in `REPO-one4all.md ## Session Setup`.
7. Find the first incomplete Step (`- [ ]`) in the Goal file. Do it.

---

## Active Goals

Current-step detail lives in each Goal file, not here. This table is navigation + step ID only.

| Goal | File | Repo | Step |
|------|------|------|------|
| **CHUNKS — Eliminate SM_PUSH_EXPR** | `GOAL-CHUNKS.md` | one4all+.github | M1 CLOSED. **CH-15a LANDED sess #73, 2026-05-07** (E_TO + E_TO_BY producer migration — SM_ICMP_GT/SM_ICMP_LT opcodes added; first producer for SM_BB_PUMP_SM; gen-locals 0=lo, 1=hi, 2=cur, 3=step; E_TO_BY dispatches on step-sign each iteration; chunk emission verified via Raku `say 1..3` audit `SM_PUSH_CHUNK=1, SM_PUSH_EXPR=0`). **CH-15-SURVEY LANDED sess #74, 2026-05-07** — `docs/CHUNKS-step15-survey.md` documents that the remaining-kinds dispatcher arm in `sm_lower.c:1192–1204` is dead code on real corpora today (363 audited programs across `test/` + cross-corpus, zero fires of `SM_PUSH_EXPR`); cause is Icon proc bodies walked by `coro_eval`, not yet lowered through `sm_lower` until Step 17. CH-15b deferred until Step 17 lands so each producer migration gets real corpus validation. **CH-16-SURVEY LANDED sess #75, 2026-05-07** — `docs/CHUNKS-step16-survey.md` documents that the line-1213 Prolog cluster producer DOES fire on every real Prolog program (unlike CH-15's dead arm), but the consumer (SM_BB_ONCE → coro_eval → bb_eval_value) FATALs on every Prolog kind — every test/prolog/*.pl program aborts under --sm-run. Smoke hides this (--ir-run only). Migration without consumer-side fix is no-op-or-worse; consumer fix needs Step 17's entry_pc infrastructure for chunk-shaped Prolog runtime entry points. Step 16 deferred. **Step 17 CARVED to `GOAL-CHUNKS-STEP17.md` sess #75, 2026-05-07** (multi-rung subsystem migration: rungs CH-17a..CH-17h). **CH-17a LANDED sess #75, 2026-05-07** — `docs/CHUNKS-step17a-validation.md` documents the scaffolding: `IcnProcEntry` and `Pl_PredEntry` gain `int entry_pc` fields (init -1); new `sm_resolve_proc_entry_pcs(SM_Program*)` in scrip_sm.c walks both tables after sm_lower returns and populates entry_pcs via `sm_label_pc_lookup`. Today every lookup returns -1 (sm_lower doesn't yet emit named proc-body chunks; CH-17b/d territory). Pure addition, byte-identical gates. Diagnostic env `SCRIP_PROC_ENTRY_PCS=1`. **CH-17b LANDED sess #75, 2026-05-07** — `docs/CHUNKS-step17b-validation.md` documents the next half: sm_lower emits named-chunk SKELETONS (SM_JUMP+SM_LABEL+SM_RETURN+SM_LABEL) for every entry in proc_table; CH-17a's resolver now finds non-(-1) entry_pcs (Icon hello.icn: main@1; Raku rk_given: day_type@1, season@5, main@9). Empty bodies; chunks forward-jumped over. Gates byte-identical. Body lowering split into separate rung CH-17b' (Icon proc bodies are EXPR_t chains, not STMT_t; frame-slot resolution is its own architectural decision). **CH-17b' LANDED sess #78, 2026-05-07** — `docs/CHUNKS-step17b-prime-validation.md` documents proc-body lowering: per-proc emission loop in sm_lower.c walks `proc->children[1+nparams..]` calling `lower_expr` + `SM_POP` per body child; trailing `SM_RETURN`. Chunks now contain real SM ops (palindrome chunk: 1–52, ~50 instrs covering full body including while loop and AUGOP increments). Unreachable today (coro_call still walks IR). Soft addition: `g_chunk_body_lowering` flag silences "unhandled expr kind" warning during proc-body emission only — kinds without explicit lower_expr cases (E_ALTERNATE, E_ITERATE, E_CSET_*, E_REVASSIGN, E_REVSWAP) emit harmless SM_PUSH_NULL inside dead chunks. Generator kinds emit legacy SM_PUSH_EXPR + SM_BB_PUMP per the spec's gating note (CH-17h reactivates CH-15b once CH-17c flips consumers). Frame-slot resolution stays at runtime via `icn_scope_patch`. Gates byte-identical to baseline. **Next inline: CH-17d** (flip coro_call consumers via entry_pc; add sm_call_proc). Step 8 (mode-4 x86 emitter) carved to `GOAL-MODE4-EMIT.md` — runs in PARALLEL with M4, file-disjoint. Don't confuse them: a session "doing GOAL-CHUNKS" defaults to its inline next rung, NOT the carved sub-goal. |
| Mode-4 x86 Emitter (CHUNKS Steps 8 + 19) | `GOAL-MODE4-EMIT.md` | one4all | **EM-7c-bb-three-column PARTIAL 2026-05-09** — central paths converted: `emitter_text.c` (text_emit_insn/text_label_define/text_emit_jmp/text_global_sym), `bb_emit.c` (every bb_insn_* TEXT branch + bb_label_define + bb_text_label).  `LABEL: ; ACTION ; GOTO` shape (24/16/N widths, literal `;` separators) live for every BB-box line through these.  New helpers: `bb3c_format`/`bb3c_text` in bb_emit, `ev3c`/`ev3c_action_v`/`ev3c_label`/`ev3c_goto_v` in emitter_v.h.  `bb_emit_byte`/`bb_emit_patch_rel*` TEXT paths now `abort()` (no `.byte` hex walls).  Side-quests: (a) shared `ARITH \op` macro split into per-op `ADD_NUM`/`SUB_NUM`/`MUL_NUM`/`DIV_NUM`/`MOD_NUM` — op-enum baked into macro body, redundant `# SM_<op>` annotation gone; `_NUM` suffix avoids GAS x86-mnemonic collision (same pattern as VOID_POP/CALL_FN).  (b) Blank lines in emitted `.s` eliminated (three leading `\n` sites in sm_codegen_x64_emit.c removed).  Gates 10/10 GREEN (EM 12/12, smoke ×6, unified_broker 49).  Tracked artifacts regenerated: roman.s 209, wordcount.s 158, claws5.s 1115, treebank-list.s 1396, treebank-array.s 1579, sm_macros.s 230.  **Next: EM-7c-bb-three-column-data CARVED 2026-05-09** — convert the 12 remaining raw `EV_TEXT` data/instruction blocks in `bb_flat.c` (charsets/XLNTH/XTB/XRTB/XFNCE/XFARB/XSTAR/XBRKX/XATP/XDSAR/XARBN/XNME/XFNME paths) so emitted `.s` is uniformly three-column inside BB blobs; helpers `flat_data_section`/`flat_data_label`/`flat_data_string`/`flat_data_quad`/`flat_data_long`/`flat_data_zero`/`flat_text_section`/`flat_globl`/`flat_box_call` to be added in bb_flat.c.  Done when: zero tab-indented or 4-space-indented instruction lines in regenerated artifacts; gates 10/10 GREEN. |
| CHUNKS Step 17 (proc/pred → entry_pcs) | `GOAL-CHUNKS-STEP17.md` | one4all+.github | **CH-17a LANDED sess #75, 2026-05-07** — scaffolding: entry_pc fields added to IcnProcEntry + Pl_PredEntry (init -1); sm_resolve_proc_entry_pcs walks both tables after sm_lower; gates byte-identical. **CH-17b LANDED sess #75, 2026-05-07** — sm_lower emits named-chunk SKELETONS for every Icon/Raku proc (forward-jumped, empty body). Resolver now finds non-(-1) entry_pcs end-to-end. Body lowering split into CH-17b'. **CH-17b' LANDED sess #78, 2026-05-07** — proc-body lowering. Per-proc emission loop in sm_lower.c walks `proc->children[1+nparams..]` and calls `lower_expr` + `SM_POP` per body child; trailing `SM_RETURN`. Chunks now contain real lowered SM ops (palindrome.icn: chunk 1–52 holds full palindrome body; Raku rk_given: 3 procs at 1/81/161 with substantial bodies). Chunks remain unreachable (coro_call still walks IR; forward-jumps skip every chunk). File-static `g_chunk_body_lowering` flag silences lower_expr's "unhandled expr kind" stderr warning during proc-body emission only. Frame-slot resolution stays at runtime (E_VAR → SM_PUSH_VAR by name). Gates byte-identical: smoke ×6, isolation, Budne PASS=61, Icon corpus 186/47/30 of 263, unified_broker PASS=49. Documented in `docs/CHUNKS-step17b-prime-validation.md`. Next: **CH-17c** (flip coro_call consumers via entry_pc; add sm_call_proc). **CH-17c LANDED sess #82, 2026-05-07** — `sm_call_proc` added; `proc_trampoline`/`gather_trampoline` dispatch via `sm_call_proc` when `entry_pc >= 0`; `nparams` added to `IcnProcEntry`; `gather_entry_pc`/`gather_nparams` to `coro_t`; E_FNC lowering fixed for Icon-style nodes. Gates byte-identical: smoke ×6, isolation, Budne PASS=61, unified_broker PASS=49, Icon corpus 186/47/30 TOTAL=263. **CH-17d LANDED sess #83, 2026-05-07** — `sm_lower.c` emits named-chunk skeletons for every Prolog predicate in `g_pl_pred_table` (SM_JUMP+SM_LABEL+SM_RETURN+SM_LABEL, forward-jumped over); `pl_runtime.h` include added. `SCRIP_PROC_ENTRY_PCS=1` confirms non-(-1) entry_pcs: palindrome/2@1, main/0@5. Consumer dormant. Gates byte-identical: smoke ×5 PASS, isolation PASS, unified_broker PASS=49, Budne PASS=61, Icon corpus 186/47/30 TOTAL=263. **CH-17e LANDED sess #84, 2026-05-07** — `pl_box_choice_pc` added to `pl_broker.h/c`; `pl_pred_entry_lookup` added to `pl_runtime.h/c`; 5 consumer sites flipped (interp_eval.c x2, pl_runtime.c x2, interp_hooks.c, polyglot.c). Chunks skeleton-only (CH-17d SM_RETURN); routing established, no crash. Gates byte-identical: smoke x5 PASS, isolation PASS, unified_broker PASS=49, Budne PASS=61, Icon PASS=186/47/30. Next: **CH-17f** (fill Prolog chunk bodies; --sm-run Prolog end-to-end). **CH-17f LANDED sess #85, 2026-05-07** — `SM_BB_ONCE_PROC` opcode added; `lower_stmt` LANG_PL + `lower_expr` E_CHOICE emit it instead of `emit_push_expr + SM_BB_ONCE`; `--sm-run` Prolog no longer FATALs (hello.pl, roman.pl produce correct output). Predicate chunk bodies remain skeleton-only; chunk body fill deferred. Gates: smoke ×6 PASS, isolation PASS, Budne PASS=61, unified_broker PASS=49, Icon 186/47/30 TOTAL=263. one4all @ `a2c6c089`. **CH-17g CARVED into three sub-rungs sess 2026-05-09** — empirical state showed CH-17c flipped only the trampoline layer; eight `coro_call(proc_table[i].proc, ...)` consumer sites still read `.proc` directly, plus EXPR_t-keyed static-var storage and unmigrated generator kinds inside chunks each block field-drop. Carved into CH-17g-call-sites / CH-17g-statics / CH-17g-final. **CH-17g-statics LANDED sess 2026-05-09** — `static_tab[]` in `coro_runtime.c` re-keyed off `EXPR_t*` onto `(int entry_pc, const char *proc_name)`; primary key `(entry_pc, var_name)` when resolved, fallback to `(proc_name, var_name)` for legacy coro_call path; `static_get`/`static_set` signatures unchanged. Gates byte-identical: smoke ×6, isolation, unified_broker PASS=49, Icon 186/47/30. **CH-17h-SURVEY LANDED sess 2026-05-09** — `docs/CHUNKS-step17h-survey.md` documents that the line-1303 dispatcher arm (E_EVERY, E_SUSPEND, E_BANG_BINARY, E_LCONCAT, E_LIMIT, E_RANDOM, E_SECTION, E_SECTION_PLUS, E_SECTION_MINUS) is dead code on real corpora today (zero fires across smoke ×6 + Icon corpus 263 + unified_broker 49 + broad/regression runs + hand-crafted every/suspend/section). Same shape as CH-15-SURVEY. Recommendation: reverse original sequencing — land **CH-17g-final** first (its legacy-body deletion creates the test surface, not blocks it), then migrate per-kind with real corpus validation. **CH-17g-final-SURVEY LANDED sess 2026-05-09** — `docs/CHUNKS-step17g-final-survey.md` rebuts CH-17h-SURVEY's "land CH-17g-final first" recommendation as empirically wrong: probe instrumentation showed `coro_call`'s legacy body is the live, hot, only consumer of Icon/Raku user-proc dispatch in `--ir-run` mode (the same mode the corpus baseline gate uses). Root cause: `sm_resolve_proc_entry_pcs` runs only inside `sm_preamble`, which `--ir-run` for non-SNO IR never invokes (`scrip.c:557–561` dispatches to `polyglot_execute` directly). Therefore `entry_pc=-1` for every proc in `--ir-run`, the `proc_table_call` chunk-dispatch branch is skipped, and deletion of `coro_call`'s body would break the entire 186/47/30 Icon corpus. CH-17h-SURVEY's lowering-site finding (line-1303 arm dead) was correct; its inferred runtime-side claim was not. Recommendation: split CH-17g-final's preconditions into **CH-17g-runtime-bridge** (chunks dispatch builtins; `--sm-run` of trivial Icon proc produces output) and **CH-17g-irrun-lowers** (`--ir-run` invokes `sm_lower`/`sm_resolve_proc_entry_pcs` so entry_pc resolves regardless of mode). Once both land, CH-17g-final's deletions are safe. Alternative: merge CH-17h + CH-17g-runtime-bridge + CH-17g-irrun-lowers + CH-17g-final into one coupled rung. Gates re-confirmed byte-identical post-revert: smoke ×6 PASS, isolation PASS, unified_broker PASS=49. Awaits Lon decision on sequencing. **CH-17g-runtime-bridge-DESIGN LANDED sess 2026-05-09** — `docs/CHUNKS-step17g-runtime-bridge-design.md` records the architectural plan. Empirical mechanism of the FATAL: `--dump-sm` shows the chunk emits `SM_CALL_FN s="write" nargs=1` cleanly; `SM_CALL_FN`'s handler in `sm_interp.c` walks special pseudo-calls → DATA dispatch → SM-native user fn → `INVOKE_fn`/`APPLY_fn` (SNOBOL4 builtin registry). Icon's `write` lives in `interp_eval.c:309` inside `icn_call_builtin`, on the legacy IR-walker path, never registered through `register_fn` — `APPLY_fn` returns FAIL, chunk surfaces "Error 5: Undefined function". Solution: extract `icn_try_call_builtin_by_name(fn, args, nargs, &out)` covering ~30 EXPR_t-free Icon builtins (write, writes, integer, string, real, char, type, copy, list, table, read, repl, upto, find, any, many, tab, move, match, …) and wire into `SM_CALL_FN` after `INVOKE_fn`'s FAIL. Rejected alternative: registering Icon builtins in the SNOBOL4 fn table (cross-language pollution). Implementation split into **CH-17g-runtime-bridge-1** (refactor, corpus byte-identical), **CH-17g-runtime-bridge-2** (wire, `--sm-run` of trivial Icon proc produces output identical to `--ir-run`), **CH-17g-runtime-bridge-3** (Raku/SCAN bridges if needed). Files: `src/driver/interp_eval.{c,h}`, `src/runtime/x86/sm_interp.c`. No new opcodes, no IR fields, no `sm_lower.c` changes. Once bridge lands, CH-17g-irrun-lowers becomes safe with chunk dispatch gated behind a runtime flag. Each line-1303 generator kind becomes its own per-kind migration (chunk-side producer + chunk-side consumer mirroring CH-17f's `SM_BB_ONCE_PROC`). Gates this session: smoke ×6 PASS, isolation PASS, unified_broker PASS=49 (no source touched). **CH-17g-runtime-bridge-1 LANDED sess 2026-05-09** — pure refactor: extracted `icn_try_call_builtin_by_name(const char *fn, DESCR_t *args, int nargs, DESCR_t *out)` from `icn_call_builtin` covering `write` and `writes` (verbatim copies of inlined logic). `icn_call_builtin` now delegates to the helper after Raku/SCAN dispatch, before user-proc/clone-or-fallback paths. Declaration in `interp_private.h`. Behaviour identical: every existing caller (`coro_bb_fnc`, `coro_value.c`/`coro_runtime.c` BB adapters) sees identical results because the helper branches are exact copies. Gates byte-identical: smoke ×6 PASS, isolation PASS, unified_broker PASS=49, scrip_all_modes PASS=2, Icon corpus `--ir-run` PASS=186 FAIL=47 XFAIL=30 TOTAL=263. `--sm-run /tmp/probe.icn` still FATALs (helper defined but not yet wired into `SM_CALL_FN` — that's CH-17g-runtime-bridge-2). Documented in `one4all/docs/CHUNKS-step17g-runtime-bridge-1-validation.md`. Files: `src/driver/interp_eval.c` (+79 −26), `src/driver/interp_private.h` (+5 −0). Next: **CH-17g-runtime-bridge-2** (wire helper into `SM_CALL_FN` after `INVOKE_fn`'s FAIL).
| Native Snocone — .NET (CHUNKS Step 9) | `GOAL-NATIVE-SNOCONE-DOTNET.md` | one4all (`src/driver/net/`) | stub written sess #62; rung DN-1 awaits PARSER-SC-6b |
| Native Snocone — JVM (CHUNKS Step 10) | `GOAL-NATIVE-SNOCONE-JVM.md` | one4all (`src/driver/jvm/`) | stub written sess #62; rung JV-1 awaits PARSER-SC-6b |
| Native Snocone — JS (CHUNKS Step 11) | `GOAL-NATIVE-SNOCONE-JS.md` | one4all (`src/driver/js/`) | stub written sess #62; rung JS-1 awaits PARSER-SC-6b |
| **SCRIP Bootstrap (Milestones 2+3)** | `GOAL-SCRIP-BOOTSTRAP.md` | one4all+ | CB-0-corpus |
| Corpus Layout Formula | `GOAL-CORPUS-LAYOUT.md` | corpus+.github+one4all | design state |
| SNOBOL4 Frontend Ladder | `GOAL-LANG-SNOBOL4.md` | one4all | SN-32 DONE (session #61) |
| **CSN FENCE Bug Fix** | `GOAL-CSN-FENCE-FIX.md` | csnobol4 | F-2 Step 3a |
| Icon Frontend Ladder | `GOAL-LANG-ICON.md` | one4all | IC-9 (one4all HEAD `1e515891`) |
| **Prolog Frontend Ladder** | `GOAL-LANG-PROLOG.md` | one4all+corpus | PR-17 — next: string builtins rung40 |
| Raku Frontend Ladder | `GOAL-LANG-RAKU.md` | one4all | RK-34 |
| Snocone Frontend Ladder | `GOAL-LANG-SNOCONE.md` | one4all+corpus | D-1 |
| Rebus Frontend Ladder | `GOAL-LANG-REBUS.md` | one4all | RB-2 |
| **PARSER-SNOBOL4 (pattern frontend)** | `GOAL-PARSER-SNOBOL4.md` | corpus+one4all | PASS=78/78 ✅ corpus@0fba291 — SN-7-7c LANDED (full keyword/function/builtin inventory + classifier patterns; cross-runtime SPITBOL x64/x32 + csnobol4 union). Next: **SN-7-8** beauty.sno full crosscheck. |
| **IR: promote DEFINE to its own kind** | `GOAL-IR-DEFINE-KIND.md` | one4all+corpus | stub written; awaiting Lon decision (cross-language emitter blast radius — see goal file) |
| **PARSER-SNOCONE (pattern frontend)** | `GOAL-PARSER-SNOCONE.md` | corpus+one4all | PARSER-SC-10 ✅ LANDED (sess 11, 2026-05-07) — switch/case/default. PASS=67 FAIL=0. Next: **SC-11** (define next rung with Lon). |
| **PARSER-REBUS (pattern frontend)** | `GOAL-PARSER-REBUS.md` | corpus+one4all | RB-FULL-1 IN PROGRESS 2026-05-07. 3 bugs fixed (A/B/C). BUG-D open (while/if next-line body). corpus@40ddfed |
| **PARSER-ICON (pattern frontend)** | `GOAL-PARSER-ICON.md` | corpus+one4all | IC-24 LANDED PASS=153 corpus@42e4ea3 (671→631 lines, E_* inlined). Next: IC-25 (Gray=ARBNO fix + Op-based tokens, target ~350 lines) |
| **PARSER-PROLOG (pattern frontend)** | `GOAL-PARSER-PROLOG.md` | corpus+one4all | **GOAL PIVOTED 2026-05-07** -- 100% parse coverage on 677 .pl files (SWI+GNU+corpus). PR-17 PARTIAL: recovery+\+prefix+div/rdiv landed corpus@2a9d6a0. ~40% of rung* files PASS. Next: single-char SY atoms, *-> soft cut, assertz in pfx_kw_name, investigate SIGKILL on multi-clause files. ⛔ NO baseline gates at session start. See handoff note for correct invocation (gen.sc+assign.sc required, stdin pipe, max 5-10 files per batch). |
| **PARSER-RAKU (pattern frontend)** | `GOAL-PARSER-RAKU.md` | corpus+one4all | **RK-29 LANDED** (corpus@58a0be4) — 26 arms: 15 block phasers + 6 block-value + 5 list adverbs. smoke PASS=5, oracle PASS=147, COV_PASS=39 FAIL=0. Next: **RK-30** (`package_declarator:sym<...>` — 10 package/class kinds). |
| Snocone claws5.sc | `GOAL-SNOCONE-CLAWS5.md` | one4all+corpus | CL-2 |
| Snocone treebank-list.sc | `GOAL-SNOCONE-TREEBANK-LIST.md` | one4all+corpus | TB-1 |
| **Snocone-in-Snocone** | `GOAL-SNOCONE-IN-SNOCONE.md` | one4all+corpus | SS-0 |
| **Rewrite SCRIP** | `GOAL-REWRITE-SCRIP.md` | one4all | RS-24b LANDED 2026-05-05 @ `296ef139` (conservative variant: dead bodies deleted, named-FATAL guards retained; 3860→3517 lines). Next: RS-24b' (aggressive label-deletion + sub-switch collapse — awaiting Lon decision) or RS-24c (remove/keep diag tooling). |
| Snocone Beauty | `GOAL-SNOCONE-BEAUTY.md` | corpus+one4all | **ON HOLD** |
| Snocone Demos | `GOAL-SNOCONE-DEMOS.md` | one4all | SD-1 |
| Snocone IR+BB | `GOAL-SNOCONE-IR-BB.md` | one4all | SC-1 |
| &STCOUNT All Languages | `GOAL-STCOUNT-ALL-LANGS.md` | one4all | ST-1 |
| Unified Broker | `GOAL-UNIFIED-BROKER.md` | one4all | U-24 |
| Raku Frontend | `GOAL-RAKU-FRONTEND.md` | one4all | RK-16 |
| Polyglot Calc Demo | `GOAL-POLYGLOT-CALC-DEMO.md` | one4all | PC-1 |
| Scrip Interp Split | `GOAL-SCRIP-INTERP-SPLIT.md` | one4all | IS-1 |
| Silly Forward Sweep | `GOAL-SILLY-SWEEP-FORWARD.md` | one4all | wm 6927 → RPLACE |
| Silly Backward Sweep | `GOAL-SILLY-SWEEP-BACKWARD.md` | one4all | wm 6427 → CMA2 |
| Silly Sync Monitor | `GOAL-SILLY-SYNC-MONITOR.md` | one4all | S-1 |
| Silly Complete | `GOAL-SILLY-COMPLETE.md` | one4all | P1-A1 |
| Prolog IR-run | `GOAL-PROLOG-IR-RUN.md` | one4all | S-10e |
| Cross-Lang Verify | `GOAL-CROSS-LANG-VERIFY.md` | one4all | S-1 |
| Sub-Expression Oracle | `GOAL-SUBEXPR-ORACLE.md` | one4all+corpus | S-2 |
| Remove CMPILE | `GOAL-REMOVE-CMPILE.md` | one4all | S-7 |
| Two-Step Bug Hunt | `GOAL-TWO-STEP-HUNT.md` | one4all | S-1 |
| Scrip Beauty Suite | `GOAL-SCRIP-BEAUTY.md` | one4all | S-6 |
| NET Beauty 18/18 | `GOAL-NET-BEAUTY-19.md` | snobol4dotnet | S-8B |
| NET Beauty Self-Host | `GOAL-NET-BEAUTY-SELF.md` | snobol4dotnet | S-2-bridge-7-fullscan |
| NET Snippets | `GOAL-NET-SNIPPETS.md` | snobol4dotnet | S-1 |
| NET Optimize | `GOAL-NET-OPTIMIZE.md` | snobol4dotnet | S-1 |
| NET DATATYPE Lowercase | `GOAL-NET-DATATYPE-LOWERCASE.md` | snobol4dotnet | S-1 |
| DATATYPE Portable Tests | `GOAL-DATATYPE-PORTABLE-TESTS.md` | corpus | S-1 |
| No Symlinks | `GOAL-NO-SYMLINKS.md` | corpus/harness/all | S-1 |
| README: profile | `GOAL-README-PROFILE.md` | .github | S-1 |
| README: one4all | `GOAL-README-ONE4ALL.md` | one4all | S-1 |
| README: snobol4dotnet | `GOAL-README-SNOBOL4DOTNET.md` | snobol4dotnet | S-1 |
| README: snobol4jvm | `GOAL-README-SNOBOL4JVM.md` | snobol4jvm | S-1 |
| README: corpus | `GOAL-README-CORPUS.md` | corpus | S-1 |
| README: harness | `GOAL-README-HARNESS.md` | harness | S-1 |
| README: snobol4python | `GOAL-README-SNOBOL4PYTHON.md` | snobol4python | S-1 |
| README: snobol4csharp | `GOAL-README-SNOBOL4CSHARP.md` | snobol4csharp | S-1 |
| README: snobol4artifact | `GOAL-README-SNOBOL4ARTIFACT.md` | snobol4artifact | S-1 |

---

## Repos

| Repo | File |
|------|------|
| one4all | `REPO-one4all.md` |
| snobol4dotnet | `REPO-snobol4dotnet.md` |
| snobol4jvm | `REPO-snobol4jvm.md` |
| snobol4python | `REPO-snobol4python.md` |
| snobol4csharp | `REPO-snobol4csharp.md` |
| csnobol4 | `REPO-csnobol4.md` |
| corpus | `REPO-corpus.md` |
| harness | `REPO-harness.md` |

---

## Architecture (one paragraph)

Every frontend (SNOBOL4, Icon, Prolog, Snocone, Rebus, Scrip) produces the shared IR.
SM-LOWER compiles IR to SM_Program — a flat array of stack machine instructions.
The INTERP executes SM_Program. The EMITTER walks SM_Program and emits native code
(x86, JVM, .NET, JS, WASM). Interpreter and emitter share one instruction set.

---

## Session trigger phrases

| Lon says | Meaning |
|----------|---------| 
| "here we go" | Session starting — proceed with session start protocol above |
| "perform hand off" | End of session — update goal state, commit, push per RULES.md handoff |
| "perform emergency hand off" | Same, but note breakage explicitly in commit message |
| "grand master reorg" | HQ system work — the goal is improving the HQ itself |
