# GOAL-PROLOG-BB.md — Prolog: GDE inside Byrd-Box machine code (PL-GZ track)

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

Landed-rung history DELETED (git holds it). FACT-RULE bodies kept VERBATIM (md5-locked across sibling GOAL-*-BB files).

**<= LIVE CURSOR (2026-07-22, s126): display/1 + display/2 + print/2 LANDED (PL-ISO-9). DONE 115->118, core-open 123->120. Rung suite 153->154/154 x3 modes. SCRIP <local> / corpus <local>. DETAILS: (1) display/1,/2 (ISO core): NEW rt_pl_display_cell (unification.c) = pl_write_term_opts(t, quoted=0, ignore_ops=1) -- mirrors gprolog Pl_Display_1 WRITE_IGNORE_OP mask (ignore_ops, UNQUOTED), distinct from write_canonical WRITE_IGNORE_OP|WRITE_QUOTED. Wired 3 sites in by_name_dispatch.c (is_known gate + $display/$display2 handlers + det name/arity table). (2) print/1 + print/2 CORRECTED to plain-write (rt_pl_write_cell) per gprolog Pl_Print_1 mask WRITE_NUMBER_VARS|WRITE_NAME_VARS|WRITE_PORTRAYED (= write, NOT writeq); SCRIP prior print/1->writeq was a latent oracle-divergence (verified NO corpus dep, safe). (3) DOT-FUNCTOR FIX (prolog_builtin.c pl_wt generic-compound branch): emit '.' literally for the cons functor under ignore_ops, because atom_needs_quoting('.')=0 (all-graphic) so pl_wt_atom will not quote it even at quoted=1 -- matches gprolog display([a,b])->'.'(a,'.'(b,[])) AND fixes write_term(L,[ignore_ops(true)]) to match gprolog (bonus). Only ignore_ops callers reach that branch (write_canonical uses a SEPARATE writer pl_write_canonical_term), so surgical, zero regression. BOTH .so and scrip rebuilt (by_name_dispatch.c compiles into separate object dirs). m3==m4 byte-exact vs gprolog 1.4.5 across rung73 (18 lines: operators-functional, lists, quoted-atoms-unquoted, standalone-dot, numbervars/$VAR-literal, stream forms via user_output). Rung suite 154/154 x3; smoke 5/5 x3; no_value_stack PASS; no_new_global unchanged (ONLY pre-existing g_pl_disj_ctr FAIL, floor 14 -- ZERO globals added). corpus rung73_display. BANKED FOLLOW-ONS (each its own rung): (a) display_to_atom/chars/codes still route through wk=3 (=write_canonical, QUOTED) which is WRONG vs gprolog display (UNQUOTED) -- needs a distinct display writer-kind + rewire; (b) print portray hook absent (SCRIP print=write, no user:portray/1 callback) -- matches gprolog output for all non-portray terms. NEXT: write.pl now 0-open; remaining PL-ISO-9 = pretty.pl (bind_variables/2, name_query_vars/2, name_singleton_vars/1) + print.pl get_print_stream/1; OR atom.pl cluster (number_atom/2 trivial, then current_atom/1 + atom_property/2 = atom-table enum); OR DEC-10 char-I/O (get0/1=get_code + put/1=put_code aliases, get/1/skip/1 loops). >>> DEC-10 CHAR-I/O NOW ALSO LANDED THIS SESSION (dec10io.pl): get0/1->$get_code + put/1->$put_code (pure table aliases, zero new code), get/1 (new $get1: skip codes<=32, return first >32, -1 at EOF) + skip/1 (new $skip1: read codes until ==arg or EOF; type_error(integer) on non-int). EOF-guarded to avoid gprolog get/1|skip/1 infinite-loop-at-EOF quirk (normal cases byte-exact). corpus rung74_dec10_io (self-contained: put to stdout, then open+set_input a temp file for get0/get/skip). SESSION TOTALS: DONE 115->122 (+7), core-open 123->116 (-7), rung suite 153->155/155 x3 modes. m3==m4 byte-exact vs gprolog 1.4.5 for both rungs. no_value_stack PASS; no_new_global floor 14 unchanged (ZERO globals). dec10io.pl remaining 7 = see/seen/tell/told/seeing/telling/append (stream-switching via $dec10_stream dynamic pred - own rung, heavier).**

**<= PRIOR CURSOR (2026-07-22, s125): name/2 + byte-io + unget LANDED (PL-ISO-4 / PL-ISO-7). ISO DONE 102->115, core-open 136->123. Rung suite 150->153/153 x3 modes. DETAILS: (1) name/2 (atom.pl, rung70): decompose atom/int/float->codes; construct via number-parse-first (strtoll/strtod), atom fallback — mirrors gprolog Pl_Name_2. Wired at 3 by_name_dispatch.c sites (is_known + handler + det-table) + g_pl_nl_builtins[] in lower_prolog.c (LESSON: list edit was likely redundant — det-target block at lower_prolog.c:596 fires BEFORE is_builtin_exec gate:611, so det-table entry alone routes I/O-class builtins without a list entry; confirmed by byte-io and unget needing NO list edit). (2) get_byte/put_byte/peek_byte /1,/2 (char_io.pl, rung71): mirrors get_code/put_code; EOF->-1; put_byte range-checks 0-255 type_error(byte,...). by_name_dispatch.c only. (3) unget_char/unget_code/unget_byte /1,/2 (char_io.pl, rung72): single C ungetc; char=single-char-atom, code=int(-1=no-op), byte=int-0-255(-1=no-op). by_name_dispatch.c only. ALL: both .so and scrip must be rebuilt when editing by_name_dispatch.c or lower_prolog.c (compile into SEPARATE object dirs). m3==m4 byte-exact vs gprolog 1.4.5 across all 3 rungs. no_value_stack PASS; no_new_global 14/floor 14 (zero new globals). SCRIP ef726064 / corpus dc5e84a6 / .github 3b8884a8. OPEN ITEMS BANKED (each its own rung): (a) float-print: SCRIP write(3.14)->3.14 vs gprolog 3.1400000000000001 (pre-existing, affects any float in a corpus rung); (b) put_*/unget_* permission-error-before-type-error ordering (two-error-conflated case only); (c) unget multi-pushback (C ungetc single-item only). NEXT candidates: char_io open items (put_char/2 remaining, get_key family), or atom.pl cluster (current_atom/1, atom_property/2), or sort/4 (SWI-only so needs swipl as oracle).**

**<= PRIOR CURSOR (2026-07-22, s124): read_term_from_atom/chars/codes /3 LANDED (PL-ISO-7b). const_io.pl 24/30 -> 27/30. Three ISO read-with-options preds wired in by_name_dispatch.c (3 edits: is_known gate + handler block + det name/arity table): reuse the existing plc_rd_entry string reader (binds[]/bnames[]) exactly as read_from_atom does, then walk the Options list and unify variables(V) = vars in first-occurrence order, variable_names(VN) = 'Name'=Var pairs (atom-named), singletons(S) = vars occurring exactly once. Two NEW PURE helpers (no globals): pl_var_cell_ptr (deref->cell ptr) + pl_count_var_occ (tally a var cell's occurrences by walking the parsed term) for singleton detection. Sources for atom (pl_atom_str) vs chars/codes (pl_list_to_cstr) branch on src flag. Byte-exact vs gprolog 1.4.5 across m3==m4 (var-name cosmetics differ per-engine as always; rung69 uses numbervars/1 to make .expected engine-stable). Rung suite 150/150 x3 modes; smoke green x3; no-value-stack PASS; no-new-global unchanged (still ONLY the pre-existing g_pl_disj_ctr FAIL, doomed-ratchet 14/floor 14 -- I added ZERO globals). corpus rung69_read_term_from. ORACLE-VERIFIED CONTRACT NOTE (GNU/SWI split): gprolog read_term_from_atom REQUIRES a terminating '.' in the source (like read/1 from a stream) and returns first-occurrence-ordered vars with atom-named =/2 pairs; SWI does NOT require the period. SCRIP follows gprolog (primary oracle); the existing plc_rd_term already tolerates a trailing '.', so no reader change was needed. BANKED FOLLOW-ONS (honest limitations, each its own rung): (a) reader OPERATOR-WIDENING -- plc_rd_term is operator-blind so read_term_from_atom('1+2',T,[]) won't parse where gprolog would; affects ALL read-from-string forms, wants a careful pass over the shared parse routine; (b) read_token_from_{atom,chars,codes}/2 -- the other 3 const_io reads, low-value tokenizer plumbing (no exposed tokenizer entry point yet). SCRIP <local, push pending> / corpus <local, push pending>. NEXT: read_token_from_* (const_io 6->0), OR PL-ISO-9 format/write completion (~t~|~+ are SWI-only per s122 source read of gprolog format_c.c -- GNU has no column stops), OR term_inl cluster (term_variables/2, subsumes_term/2).**

**<= PRIOR CURSOR (2026-07-22, s123): numbervars/1 + const_io codes/chars family (21 preds) LANDED. LADDER A 75->97 DONE, core-open 163->141. SCRIP 6b553f96. Details: (1) numbervars/1 (PL-ISO-9): rt_pl_numbervars1_cell (From=0, discard end) + det dispatch wiring; m3==m4 byte-exact vs gprolog f(A,B,g(A,C)). (2) const_io codes/chars/atom family (PL-ISO-7b): write/writeq/write_canonical/display/print _to_ atom/chars/codes + write_term_to_* (3-ary) + format_to_chars/codes + read_from_chars/codes. Reused fh_capture_begin/end + pl_sink_build (kind 1=atom/3=codes/4=chars); new static pl_list_to_cstr for reads (placed after pl_list_to_arr to respect C ordering). const_io.pl 3/30->24/30. (3) BUGFIX: rt_pl_write_cell was writing to raw stdout bypassing output redirection -- added pl_wr_set_fp(fh_cur_out_fp()) like writeq/canonical siblings; also corrected write_to_atom which had used writeq instead of write. Rung suite 148/148 x3 modes (m3==m4); no-value-stack PASS; no-new-global unchanged (14 floor). PROLOG-ISO-TRACKER.md regenerated (was stale at 45 done, now correct at 97). NEXT: read_term_from_*/read_token_from_* (remaining const_io 6), or write.pl remaining 2 open (print/2 + get_print_stream/1), or term_inl cluster (term_variables/2, subsumes_term/2, etc.).**

**RECENT LANDINGS (git holds full cursors):** s118 open/close file streams + current_stream/1 + write_canonical GNU/ISO list dialect split (rung65/66). s117 char_io (rung64). s116 const_io write-to-atom + with_output_to + format-to-atom (open_memstream capture). s115 stream core + term-writer reroute (rung60/61/62; streams = the term $stream(N) over DT_FH/fh_table; writeq/write_canonical/write_term/format honor a redirected current-output). s114 findall/bagof/setof-over-inline-disjunction fixed + current_prolog_flag/2 + set_prolog_flag/2 (g_pl_flags). s113 ISO `/` yields float, ISO float printing, number_codes reverse, dyn-only pred registration. FEATURE PIVOT (Lon, s114): performance -> feature-complete, climb LADDER A to 100%; build -O0. Oracles gprolog 1.4.5 + swipl 9.0.4 via apt; refs/ symlinked from uploaded zips.

## 🔴🔴🔴 TOP PRIORITY — PROLOG BENCHMARK PERFORMANCE (Lon directive, 2026-07-18, verbatim: "Make Prolog benchmarks top priority ... We'll be analyzing and improving performance all around.")

## JOB #1 (perf, STANDING) - FINISH THE RBP/RSP FORTH-STYLE STACK (Lon 2026-07-18)

Main/outer spine is rsp for all languages (ZC_FRAME_RSP default since s65); SNOBOL4 runs the full CSTACK discipline; Prolog generator/resumable boxes use heap-fb-as-rbp. GAP: Prolog PROC ACTIVATIONS still cross the rt_proc_call_gen_h C trampoline (C frame + strcmp lookup) into heap-linked ZLS frames - Prolog runs BESIDE the rsp spine, not ON it. Per the s114 feature pivot this ladder is the standing background priority, resumed after LADDER A. Open rungs (RSP-F-4 open; RSP-F-1/2/3 landed):
**PL-RSP-FINISH (= SPEED-3 + SPEED-7 fused, promoted to the head; SPEED-1/2/4/5/6/8 queue BEHIND it):**
- [ ] **RSP-F-4 REGISTER RESIDENCY (= old SPEED-8).** H + TR cursors → callee-saved registers on the now-rsp substrate; LOCKSTEP convention edit across sibling GOAL-*-BB files. FINAL gate ≤1.0× — beat GNU.

**LADDER B - PL-SPEED (beat gprolog on the van Roy suite).** Baseline (2026-07-18 rail): geomean m4/GNU started ~199x; after s95-s113 speed work fib/tak sit within ~1.3-1.7x GNU and geomean vs the OLD pre-gut engine is 0.65x (NEW BEATS OLD). Full table + method in FINDING-2026-07-18-CLAUDE-PL-VANROY-RAIL-BASELINE.md. Two sub-ladders below (PL-REGAIN = recover pre-gut speed; PL-SPEED = beat GNU); work behind LADDER A per the feature pivot.

### PL-REGAIN - recover pre-gut GZ-engine speed on the new spine (fast path per construct, general fallback stays; old code is a semantics/codegen reference only, never linked). Open (slice A/B of most rungs landed s100-s106):

- [ ] **REGAIN-1 DIRECT PORT CALLS (slice C).** Emit-time-resolved `call procN_a`/`call procN_b`, arg cell-pointers in SysV regs, status in eax; DET-marked preds only (RSP-F-1 marker), NONDET keeps the gen rail. Needs a driver-minted proc-entry bb_label_t table + one new in-band 'E'/'F' record. READ BB-CODEGEN DESIGN SET (PLAN step 6). Completion: fib .s zero rt_call_arr/rt_proc_call_open on the recursion path; fib <=3x GNU.
- [ ] **REGAIN-2 DET BUILTIN OPCODES.** is/cmp/write/nl/unify each lower to ONE specialized helper (reg args, [rip+..] RO operands, je omega). Completion: grep rt_call_arr in fib .s == 0; deriv per-iter >=3x on the rail.
- [ ] **REGAIN-GATE.** A/B rail geomean vs OLD <=1.3x (parity band), then the standing gates own the finish (<=1.2x GNU RSP-F-3 ladder, <=1.0x RSP-F-4). Every rung holds the full board. Prereq: the defect-(c) SIGSEGV rung (queens_8 NEW m4 DNF blocks the rail). SPEED-5 indexing / SPEED-6 LCO stay separate.

- [ ] **PL-SPEED-1 (ii) per-call-SITE resolved-fn cache** - staged-call box gets a frame slot holding the resolved rt_proc_t* after first call. (i) O(1) FNV proc registry + the rt_call_arr $-gate DONE s98 (killed an 80M-strcmp dispatch walk, ~2.5-3x wall). Now aimed at the live arms (script_try order, pl_arith2 chains); largely absorbed by REGAIN-1/2 for DET.
- [ ] **PL-SPEED-3 DET/NONDET SPLIT** (architecture rung). Compile-time DET classification in LOWER (RSP-F-1 marker exists); DET activations = C-stack frames, NONDET = ZH. Completion: fib/tak/queens pass --zeta=zh at 64MB; deriv byte-green under poison; geomean vs GNU <=2x.
- [ ] **PL-SPEED-4 kill_since TAIL CURSOR.** Per-mark slab start pointer so kill_since walks only the tail born since the mark, not the whole heap. Completion: queens --zeta=zh within 1.5x its zls2 time.
- [ ] **PL-SPEED-5 FIRST-ARGUMENT INDEXING.** Per multi-clause pred, LOWER builds a first-arg dispatch (principal-functor/arity key -> clause-entry table); callee alpha switches on the caller arg0 tag+key and jumps to the sole candidate (no CP when unique). Source: gprolog Pl2Wam indexing.pl + WAM switch_on_term. Slice A (pre-try guards) landed s113. Completion: qsort/nrev/deriv >=25%; rung suite x3 green.
- [ ] **PL-SPEED-6 LAST-CALL OPTIMIZATION.** A DET body whose last goal is a user call reuses the caller frame (jmp to callee alpha). Completion: nrev recursion O(1) frames; geomean improves.
- [ ] **PL-SPEED-7 TRAMPOLINE RETIREMENT + RSP SPINE.** DET staged calls emit direct call proc_X_alpha (no rt_proc_call_gen_h C frame); flip the Prolog DET spine to SNOBOL4 CSTACK discipline, freeing R12. Completion: fib .s zero rt_proc_call_gen_h; frame gates green; geomean vs GNU <=1.2x.
- [ ] **PL-SPEED-8 REGISTER RESIDENCY (H/TR cursors).** With R12 freed, put the compound-build heap cursor + trail top in callee-saved registers; LOCKSTEP convention edit across sibling GOAL-*-BB files. FINAL geomean vs GNU <=1.0x (the beat-GNU milestone).

**MEASURED PERF-ADJACENT DEFECTS BANKED 2026-07-18 (each needs a rung or a monitor hunt; none fixed this session):** (a) `once/1` fence broken under external redo — correctness, reproducer in the FINDING; (b) WS accrual across fail-driven iterations → super-linear slowdown (fib ×200: 24 iters then timeout) — the queensn leak class generalized, owned by PL-WS-2 streams 2+3 / PL-SPEED-3; (c) enumeration-load SIGSEGV/SIGABRT at higher N during auto-ranging (memory exhaustion crash, not clean failure); (d) ham full-enumeration ≈4000× vs GNU (180 s/iter) — worst measured cell, structure+backtracking heavy.

## RULING (Lon, 2026-07-08): restore the old Prolog code onto the one-emitter/reduced-IR spine + new ZLS/Zeta arena with BB-managed memory lifetimes. Old algorithms + old box templates + old runtime, integrated; the old pl_gz_ scrip.c driver and emit_bb.c stay dead (one-emitter law). Supersedes the GZ#6 rebuild-from-rung01 framing and the PL-AREAS register-arena plan (zeta subsumes the E-area; the ZC two-class taxonomy covers H-class survivors; the trail is the spine; R14=TR register residency is a later perf option).

## 🎯🎯🎯 PL-100 — TWO LADDERS TO 100%: BEAT GNU AND SWI ON FEATURES *AND* SPEED (Claude, 2026-07-10 #3, Lon directive)


### LADDER A — PL-ISO (features → 100% coverage)

- [x] **PL-ISO-7 STREAM I/O.** read/1 + read_term/2 (7a), stream core + term-writer reroute + stream-form writers + const_io (s115/s116), char_io (s117), open/close file streams + write_canonical GNU/ISO list dialect split + current_stream/1 (s118), stream_property/2 (s122) ALL LANDED. PL-ISO-7b const_io codes/chars family 21 preds (s123) + read_term_from_atom/chars/codes /3 (s124) LANDED (const_io.pl 27/30; remaining 3 = read_token_from_atom/chars/codes /2).
- [ ] **PL-ISO-9 FORMAT/WRITE COMPLETION.** format directives `~p ~q ~e ~f ~g ~r ~c ~s ~t~| ~+` (column stops); write_term/2 options (quoted(true), ignore_ops, numbervars, max_depth); print_message.
- [ ] **PL-ISO-11 TERM INSPECTION + SORT VARIANTS.** term_variables/2,3, subsumes_term/2, setarg/3, acyclic_term/1, sort/4, predsort/3, msort/2 remainder. (setarg/3, `*->` soft-cut banked.)
- [~] **PL-ISO-12 FLAGS + CONTROL/CALL EXTRAS.** current_prolog_flag/2 + set_prolog_flag/2 LANDED s114 (g_pl_flags, sanctioned). between/3 + for/3 landed. OPEN: remaining flag.pl + call.pl + arith_inl.pl.
- [ ] **PL-ISO-13 CONSULT / LISTING / EXPAND.** listing/0,1, load/1, expand_term/2 (DCG term expansion), goal_expansion, pl_error remainder.
- [ ] **PL-ISO-14 VAR-GOAL GEN BRIDGE (correctness bug, not coverage).** Every GEN-rail builtin is invisible to the $call runtime bridge when the goal arg is an unbound var bound at runtime; wire the GEN builtins into the $call dispatch. Reproducer from s56.

### LADDER B - PL-SPEED: see the perf ladders at the TOP of this file (JOB #1 RSP-FINISH / PL-REGAIN / PL-SPEED). Feature pivot (Lon s114): work LADDER A to 100% first, then this ladder.

**PL-100 DONE =** ISO tracker UNASSIGNED=0 AND bridge suite 45/45 AND rung suite x3 green AND bench 22/22 AND vanroy geomean <=1.0x GNU. SWI feature-parity beyond ISO is tracked via the SWI test harness (GOAL-PROLOG-100-SWI.md).


## ⛔ FACT RULE — LANGUAGE-BLIND BB/XA TEMPLATES (Lon, 2026-06-03)
No language-specific logic in any BB/XA template: templates dispatch on IR shape + representation flags only. FORBIDDEN inside `src/emitter/{BB,XA}_templates/`: `IR_LANG_*`/`LANG_*`/`is_<lang>` guards, language-named template fns/files/dispatch arms, hardcoded language-builtin names. Per-language behavior lives in the runtime (by-name dispatch) or in LOWER (different IR shape → its own BB) — never in a template arm. Inventory: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md`; fix ladder LB-* in GOAL-PASCAL-BB.md. COMPLETION TEST: the audit's Tier-1 grep over both template dirs == 0.

## ⛔ DIRECTIVE — DYNAMIC REALLOC FOR ALL BB-LOCAL COLLECTIONS; CAP-BUMPS ARE RETIRED (Lon, 2026-06-24) — applies EVERYWHERE (all languages' BB paths)

**THE LAW: every BB-local variable that is a COLLECTION must be a dynamically-grown heap array (geometric 2× growth on overflow), NEVER a fixed-size array with an artificial `> N` ceiling.** A "cap bump" (statically raising a fixed bound, e.g. PB-NBODIES-32's `[16]`→`[32]` + `> 16`→`> 32`) is the WRONG pattern — it only moves the ceiling; the next bigger program needs another bump. The correct design has NO ceiling: start small, `realloc ×2` when full. The `alloca`-by-count arrays (`emit_bb.c` `pgl`/`pgb`/`cbody`/`cpre`/`cβ`) are the model for the per-call case where the count is known up front; **heap realloc-×2 is required where the count is not known before the loop or must persist past the call**. CONVERT, everywhere: the fixed `[N]` arrays + their `> N` guards in the GZ path (`scrip.c` `pl_gz_*` goals/args/synth/clause arrays incl. `goals_buf[64]`/`goalsB_buf[64]`/`zsk[32]`/`lbase[32]`/`callees[8]`/`claimed[8]`/`pl_claimed[16]`/`g_gz_visiting[16]`; `emit_bb.c` `gz_emit_callee_body` `nb[32]`/`cladv[32]`/`redo[32]`/`cbase[32]`; `box_state.h` `pl_gz_choice_state_t.consts[32][8]` + `pl_gz_callee_t.clause_head[32]` + the `args[8]` arg arrays; `bb_cell_choice` `> 32`), AND the analogous fixed collection arrays in every other language's BB lowering/emit path. **COMPLETION TEST:** grep finds NO fixed-size BB-local collection array gated by a `> N`/`>= N` overflow guard in any language's BB path; a `query`-style program with 25+ clauses (or 9+ goals, or 5+ args) admits with ZERO source-cap edits. **METHOD:** introduce a tiny grow helper (`ptr`+`len`+`cap`, `cap=cap?cap*2:8` on push) or reuse an existing vector; convert incrementally, floor 115/115 m3+m4 green after each conversion, `.s` byte-identical for inputs below the old cap (proves behavior-neutral).

## PB-BENCH - van Roy / Aquarius / Warren suite in corpus/benchmarks/prolog/ (src/ = swi-vanroy pristine upstream; bench/ = runnable SCRIP-dialect set with .expected oracles + honest .s). Runner scripts/bench_prolog_vanroy.sh.

## ⛔ `bb_bin_t` IS ABOLISHED — PATCH METADATA TRAVELS IN-BAND; NO FUNCTION COUNTS BYTES (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

**The `bb_bin_t { sites, labels, is_def, bytes }` struct and `bb_emit_asm_result(out, bin)` /
`bb_emit_asm_result_pairs(out)` are DELETED (Lon directive 2026-06-02). No box may name `bb_bin_t`, declare a
`bb_bin_t bin`, or call `bb_emit_asm_result`.** The struct was the carrier for a hand-counted / FUNCTION-counted
patch-offset table — the `bin.sites.push_back((int)b.size())` idiom, which is invalid: it computes a patch offset
with `b.size()` (a function of the running buffer) instead of letting the position be DISCOVERED. That idiom is the
exact nonsense the template revamp kills, and the strongest way to kill it is to remove the type so the idiom does
not COMPILE — the same enforcement-by-deletion as the no-`pBB`/`_.node` rule (a grep gate is unnecessary when the
compiler rejects it).

**THE ONE WAY: every BB template returns ONE concatenation of `x86(...)` calls and is emitted by
`bb_emit_x86(out)`.** Patch sites are TAGGED RECORDS inside that string (`L` literal bytes / `J` rel32-to-port /
`D` define-port / internal-label `L(n)` / pair-loop `E`/`F`); `bb_emit_x86` walks them and DISCOVERS each byte
position as it copies. There is NO separate offset list, so NOTHING can drift and no function ever counts bytes.
This SUPERSEDES the earlier "TWO LITERAL FORMS ONLY" framing of the BINARY arm: the hand-coded literal byte map
with a literal offset tuple was a TRANSITIONAL form; the in-band record stream is the END form, and it is what the
`b.size()` ledger was driving toward — the ledger reaches zero when the last `bb_bin_t` user is converted, not by
rewriting offset tuples by hand.

**FORBIDDEN:** `struct bb_bin_t`, `bb_bin_t bin`, `bb_emit_asm_result(...)`, `bin.sites`/`bin.labels`/`bin.is_def`,
and `(int)b.size()` (or any `.size()` of a running byte buffer used as a patch offset) anywhere in
`src/emitter/BB_templates/`, `XA_templates/`, or `emit_str.*`. The carve-out for `bb_emit_asm_result` walking a
finished string is GONE — that function no longer exists. (A box NOT YET converted is a LOUD `x86_bomb(msg)` stub
— `extern "C" void bb_foo(...) { bb_emit_x86(x86_bomb("bb_foo: …")); }` — which COMPILES + LINKS so SCRIP stays
green and ABORTS beautifully when reached; each owning session replaces its stubs with real `x86()` concatenations
as its own test reaches them.)

**ENFORCEMENT:** structural (the compiler) — `bb_bin_t` is declared nowhere, so any use fails to compile. Plus a
one-line gate `scripts/test_gate_no_bb_bin_t.sh` (comments stripped): `bb_bin_t` / `bb_emit_asm_result` live code
references == 0. **COMPLETION TEST:** (a) `emit_str.h` declares neither `bb_bin_t` nor `bb_emit_asm_result`; (b)
the gate reads zero; (c) every BB template is emitted via `bb_emit_x86`; (d) `make scrip` + `make libscrip_rt`
rc=0; (e) this FACT RULE body is byte-identical across the four GOAL-*-BB files.

## ⛔ ONE MEDIUM, INVISIBLE — NO `IF(MEDIUM_BINARY,…)` INSTRUCTION BRANCH, NO RAW-BYTE PRODUCER IN A TEMPLATE (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

**A template NEVER writes an instruction twice — once as GAS text, once as raw bytes — and NEVER branches on the
medium to pick between them (Lon directive 2026-06-02).** The forbidden shape (the exact nonsense this rule kills):
```
  + IF(MEDIUM_TEXT,  std::string(" mov rbx, rsp\n"))      // same instruction…
  + IF(MEDIUM_BINARY, x86_Lrec(x86_b3(0x48, 0x89, 0xE3))) // …written a second time as bytes
```
Every instruction goes through ONE `x86(mnem, …)` call; the encoder switches medium INTERNALLY, so the template
body is identical for BINARY and TEXT and a reader cannot tell which medium is active. If an instruction has no
`x86()` form yet, ADD an encoder + dispatch case to `x86_asm.h` (one place, byte-verified vs `as`) — NEVER
hand-encode it inline in the template. The missing encoder is the bug; the medium-branch is the symptom.

**FORBIDDEN inside `src/emitter/BB_templates/*.cpp`:** the raw-byte producers `x86_Lrec`, `x86_Jrec`, `x86_Drec`,
`x86_b1(`, `x86_b2(`, `x86_b3(`, `bytes(`, `u8(`, `u32le`, `u64le`; and any `IF(MEDIUM_BINARY, …)` or
`IF(MEDIUM_MACRO_DEF, …)` carrying instruction bytes. Those record/byte primitives are PRIVATE to `x86_asm.h` (the
encoders' implementation); a template only ever sees the `x86(...)` front-end + the markers (`L(n)`, `FR(off)`,
`FRQ(off)`, `PORT_*`) and the LOUD `x86_bomb(msg)` stub. **ALLOWED carve-out — TEXT-ONLY ANNOTATIONS WITH NO BYTE
FORM:** a box's leading `α:` label (`s_1asm(std::string(_.lbl_α)+":")`), and `IF(MEDIUM_TEXT, <comment-or-label>)` with NO matching `IF(MEDIUM_BINARY, <bytes>)` is fine.

**CORRECTION RECORD (Lon 2026-06-06):** RULES.md TEMPLATE-ONLY EMISSION corrected to match this rule; former
"duplicate the byte-producing code into each template file" clause (515aa7d6) is DEAD.

**ENFORCEMENT:** gate `scripts/test_gate_template_medium_invisible.sh` (`--strict` enforces zero). **COMPLETION TEST:** (a) zero raw-byte producers and zero `IF(MEDIUM_BINARY,…)`/`IF(MEDIUM_MACRO_DEF,…)` in any `BB_templates/*.cpp`; (b) every instruction emitted via `x86(...)`; (c) gate green under `--strict`; (d) FACT RULE body byte-identical across the four GOAL files.

**THREE FACES OF ONE END STATE.** This rule, `bb_bin_t`-ABOLISHED, and no-`pBB`/`_.node` are three faces of ONE converted box. The three gates reach zero TOGETHER, box-by-box.

## ⛔ NO C BYRD-BOX FUNCTIONS — A BOX IS ENTERED BY JUMPING TO ITS α/β LABELS, NEVER A `(ζ, int entry)` C CALL (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**There is NO such thing as a C byrd-box function. The "brokered BB" concept is ABOLISHED.** A byrd box is
EMITTED machine code. It has exactly TWO entry points, and they are **LABELS** — α (fresh entry) and β
(resume). Control reaches a box by **JUMPING to one of those labels**. A box is NEVER a C function, is NEVER
reached by a C call, and NEVER takes an integer `entry` argument to select α vs β. The C signature
`DESCR_t NAME(void *ζ, int entry)` — a ζ-state pointer plus an `int entry` α/β selector — is **FORBIDDEN**.
**ENFORCEMENT:** gate `scripts/test_gate_no_brokered.sh` reads zero; compiler rejects the signature (DESCR_t
undefined without the old header). **COMPLETION TEST:** (a) `test_gate_no_brokered.sh` green; (b) no C function
in any BB/XA template carries the `(void *ζ, int entry)` signature; (c) this FACT RULE body byte-identical
across all five GOAL files.

## ⛔ NO AST AND NO IR DURING MODE-3/MODE-4 EXECUTION (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**During the EXECUTION of a mode-3 (`--run`) or mode-4 (`--compile`) program, NOTHING reads or writes the AST (`tree_t`) or the IR (`IR_t`/`IR_graph_t`).** (Lon directive, 2026-06-13.) The compiler reads the IR exactly ONCE — before execution — to emit the mode-3 RX-slab image or the mode-4 `.S` source; thereafter the produced machine code runs with ZERO reference to either tree. A box's runtime values live INSIDE the box (RO `[rip+disp]`, RW `[ζ=r12+off]`); a runtime helper (`rt_*`) operates only on `Term*`/`DESCR_t` values, never on `IR_t*` or `tree_t*`. This subsumes the IR-NEVER-TOUCHED rule and extends it to the AST: an AST walker that does not EMIT IR is worthless — it may not exist on any run path, not even for mode 2. (The mode-2 `--run` IR-graph interpreter `IR_interp_once` is the ONLY sanctioned IR walker, and it is reachable ONLY via `--run`, never from a mode-3/4 produced binary.)

**THE ONE EXCEPTION — `EVAL()` and `CODE()`.** SNOBOL4's `EVAL` and `CODE` are dynamic-compilation builtins: by definition they compile a string into executable form AT RUNTIME (`CONVE_fn`→`EXPVAL_fn`, the `g_eval_str_hook`/`g_eval_pat_hook` rail). Reading/building an IR (or equivalent) at runtime is intrinsic to their meaning, so the prohibition does NOT apply INSIDE `EVAL()`/`CODE()` (and only there). No other construct, builtin, or runtime helper may read or write AST/IR during mode-3/4 execution.

**FORBIDDEN on the mode-3/4 run path:** any `rt_*` (or template-called) function that takes an `IR_t*`/`IR_graph_t*`/`tree_t*`, walks `->operands`/`->c[]`/`->t`/`->op`, reads `IR_LIT(...)`/`IR_EXEC(...)`, dispatches on `IR_e`/`tree_e`, or bakes a live `IR_t*`/`tree_t*` address into emitted code (the `emit_term_from_node_bin` pattern). A box NOT YET converted is a LOUD `x86_bomb(msg)`, never a silent IR/AST read.

**GUARD:** the run path's runtime objects are `Term*`/`DESCR_t` only. **COMPLETION TEST:** (a) no GZ template (`bb_cell_*`) and no mode-3/4-reachable `rt_*` reads AST/IR (grep of the run-path helpers for `IR_t*`/`tree_t*`/`IR_LIT`/`->op`/`->t` == 0, excepting `EVAL`/`CODE`'s `CONVE_fn`/`EXPVAL_fn` rail and the mode-2-only `IR_interp_once`); (b) no function bakes a live `IR_t*`/`tree_t*` into emitted bytes; (c) FACT RULE body byte-identical across all five GOAL-*-BB files.

## ⛔ NO VALUE STACK — EVER (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**SCRIP HAS NO VALUE STACK. NO SESSION, IN ANY LANGUAGE, MAY CREATE ONE.** (Lon directive, 2026-05-31.)
There is nothing like a value stack in SCRIP — every value a BB graph computes or holds at run time lives
INSIDE a box: a READ-ONLY operand constant reached `[rip+disp]` into sealed data, or a READ-WRITE slot
reached `[ζ=r12+off]` in the per-sequence one-register frame (the `test_sno_1.c`/`test_icon.c` named-slot
model). A consumer reads a producer's result directly from that producer's slot. A value is NEVER pushed
to or popped from a global stack, and intermediate producer→consumer values are NEVER threaded through a
name-table round-trip. This is the same law as the PER-BOX LOCAL STORAGE FACT RULE; this rule states the
prohibition in the strongest, language-independent form so it cannot be re-introduced from any session.

**The `g_vstack` global array is DELETED (2026-05-31) and must NEVER be resurrected** — nor any equivalent
under a different name. FORBIDDEN to (re)introduce: a global/static array whose purpose is to push a box's value and pop it in a consumer; `rt_push_*`/`rt_pop_*`/`vstack_*` value traffic; any `*_push`/`*_pop` helper that moves an *intermediate* value between boxes. (KEEP: Prolog trail `g_resolve_trail`/`rt_pl_trail_*`; choice-point ledger `g_resolve_bfr`; C call stack; ARBNO-style indexed frame array.)

**GUARD:** `scripts/test_gate_no_vstack.sh`. **COMPLETION TEST:** (a) `grep -rn 'g_vstack' src/` == 0; (b) no new global/static push/pop value arena; (c) gate `g_vstack` line reads 0; (d) FACT RULE body byte-identical across all five GOAL-*-BB files.

## ⛔ NO NEW GLOBAL FOR ANY "NOT NEEDED" STRUCTURE — THE TRAIL IS THE ONLY SPINE (FACT RULE — PROLOG-ONLY, 2026-06-13, Lon directive)

**This rule is Prolog-specific and lives ONLY in GOAL-PROLOG-BB.md** (its subject — the trail, unification, the DESIGN §10 list — is Prolog-only; it is NOT byte-identical-synced across the sibling GOAL files. The language-independent prohibition it specializes is the NO VALUE STACK rule above.)

**THE LAW: no global variable may be ADDED or USED to implement ANYTHING on the DESIGN §10 "DATA STRUCTURES NOT USED" list.** The four-port + frame-cell model means run-time Prolog state lives in exactly two places — a box's own **frame cells** `[ζ=r12+off]` and the **TRAIL** — and NOTHING ELSE. Every structure on the §10 NOT-NEEDED list (choice-point stack #1, environment stack #2, argument/value stack #3, generator-frame stack #4, **trail-MARK snapshot stack #5**, bytecode dispatch #6, setjmp/longjmp exception-frame stack #7, meta-rail engine #8, WAM register bank #9, per-engine stack set #10) is FORBIDDEN to exist as a global. The mark is an **int in the box's frame cell** (already true in `bb_cell_choice`'s `mark_slot`), the CP "ledger" is **ω-wiring + a frame cursor cell**, the catcher is a **catch-frame cell** — never a `g_*`.

**WHAT A NEW GLOBAL IS:** any new `g_*` (or file-static array/struct under any name) whose purpose is to push/pop/snapshot/iterate per-activation control or value state. If a rung "needs" one, the rung is wrong: the state belongs in a frame cell or the trail. THIS IS THE GUARANTEE Lon asked for — it is mechanically enforced, see the gate.

**THE TRACKED `g_*` ALLOWLIST (the concrete pattern list).** The gate `scripts/test_gate_pl_no_new_global.sh` carries the FROZEN allowlist and splits every `g_*` in the Prolog-owned source set into two tiers:
- **SANCTIONED (8 — legal forever):** `g_resolve_trail` (THE TRAIL — see BIG NOTE), `g_pl_pred_table`/`g_pl_pred_n` (clause DB — a heap, §10 "we need *a* clause store, not *that* one"), `g_rt_pl_nb`/`g_rt_pl_nb_n` (`nb_setval`/`nb_getval` store — a global mutable var IS the feature, by definition), `g_stage2` (the stage2 PROGRAM, compile/emit-time, freed before run by `ir_delete_all`), `g_pl_nl_arith`/`g_pl_nl_builtins` (const name tables read at LOWER time only). These are NOT runtime control/value stacks.
- **LEGACY-DOOMED (15 today — RATCHET TO ZERO; was 17, −2 via `1a1ce0f`+`7487c48`):** the resolution.c control-engine residue, each of which IS a §10 structure — `g_resolve_env` (E-stack #2), `g_resolve_bfr`+`g_resolve_cp_stamp` (CP-stack #1), `g_resolve_catch_top`/`g_resolve_catch_stack` (exception-frame stack #7), `g_resolve_mark_top`/`g_resolve_mark_stack` (trail-mark snapshot stack #5), `g_resolve_cut_flag`/`g_resolve_cut_barrier` (cut → frame gate, law 4), `g_resolve_bb_table`/`g_resolve_bb_count`+`g_meta_compat`/`g_meta_builtins` (meta-rail #8), `g_resolve_active`/`g_resolve_exception` (engine state). **DELETED this session:** `g_resolve_nb_store`/`g_resolve_nb_count` (old nb store — dead, superseded by `g_rt_pl_nb`). All remaining are UNREACHABLE from GZ dispatch but still LINK (the meta-rail + env + catch residue are still reached by m2); PL-BB-DEMOLITION deletes them. **This list is CLOSED — nothing may be added to it; the floor only ever DROPS** (delete a doomed global → lower `DOOMED_FLOOR` by one; end state 0).

**ENFORCEMENT:** `scripts/test_gate_pl_no_new_global.sh` — (1) any `g_*` not in either tier → FAIL (names it: "a new global was introduced"); (2) doomed count > floor → FAIL ("a doomed pattern re-expanded"). Verified: green at floor 17 today, and FAILS loudly when a stray `g_resolve_choicepoint_stack[256]` is injected. **COMPLETION TEST:** (a) gate green (NEW-GLOBAL check passes — zero off-allowlist `g_*`); (b) `DOOMED_FLOOR` strictly decreasing across the migration, terminating at 0 with resolution.c + the meta rail deleted; (c) the only surviving runtime spine is the trail (plus the heap stores + compile-time consts in SANCTIONED).

## 📌📌📌 BIG NOTE — THE TRAIL IS THE ONE MAIN ATTRACTION; IT WANTS A REGISTER (decision pending Lon) 📌📌📌

**Prolog's "main attraction" is the TRAIL, exactly as SNOBOL4/Icon's main attraction is the SUBJECT STRING.** DESIGN §10 names four survivors; only ONE — the trail — is a Prolog-specific runtime spine (the heap, the frame cells, and the C call stack are shared with every language). The trail is the single shared binding-undo log: a callee's bindings are undone by a caller's backtrack, so it MUST be shared across activations (DESIGN §3 law 3). It is **not** a control stack and **not** operand-passing — it is the one thing the four-port model genuinely keeps.

**Its shape is already register-perfect.** `Trail { Term **stack; int top; int capacity; }` (`src/parser/prolog/prolog_runtime.h`). The "mark" is literally `top` — an integer. That is **base / cursor / end** — the IDENTICAL three-part shape the string languages carry in registers for the subject:

| string-lang register | role | Prolog trail analogue |
|---|---|---|
| **R13 = Σ** | subject BASE ptr | trail `stack` (base of the `Term*` array) |
| **R14 = δ** | CURSOR | trail `top` (the mark; "push" = ++, "unwind" = set back) |
| **R15 = Δ** | LENGTH/END | trail `capacity` (the limit) |

**MEASURED:** R13/R14/R15 are **completely idle in Prolog mode** — 0 references across every `bb_cell_*`/`bb_det_*`/`bb_query_frame`/`bb_callee_frame` template (Prolog has no subject string, so the whole subject trio is free). RBP is likewise untouched in the Prolog GZ templates.

**RATIFIED (Lon, 2026-06-13): the trail lives in R13/R14/R15** — the very registers the string languages dedicate to their main attraction (the subject), idle in Prolog. `R13 = trail stack` (base), `R14 = trail top` (the mark/cursor), `R15 = trail capacity` (end) — base/cursor/end, the same shape as Σ/δ/Δ. This makes the parallel structural and self-documenting: *the trail is to Prolog what the subject string is to SNOBOL4/Icon, in the same three register slots*, and removes `g_resolve_trail` as a symbol load (pure register traffic; the `g_*` survives only as the init-time backing allocation, or is dropped entirely). The convention table in all three GOAL files now records this dual role (this edit). **RBP REMAINS RESERVED** (its brokered-frame role is dead under NO C BYRD-BOX; held for a future use TBD — Lon: "something lurking we have yet to see"). **DEFERRED (own later rung):** (a) the actual emitter wiring — GZ preamble loads the trail registers, `rt_trail_mark`/`rt_trail_unwind` become register ops with callee-saved discipline across `rt_*` calls; (b) the cross-language BB-jump save/restore of the trio (set on entering a Prolog box from a SNOBOL4/Icon box, restore on return).

**⚠ LOCKSTEP CONVENTION CHANGE — DONE THIS EDIT.** Per the X86-64 REGISTER / SUBJECT-MODEL CONVENTION rule, "Changing any assignment is LOCKSTEP — update all three GOAL files in the SAME commit." The R13/R14/R15 trail role is now recorded as an identical DUAL-ROLE block in the convention table of GOAL-SNOBOL4-BB.md / GOAL-ICON-BB.md / GOAL-PROLOG-BB.md (byte-identical, verified same md5). NOTE (drift flagged for Lon): the surrounding convention block was already NOT byte-identical across the three files before this edit (SNOBOL4 terser, Icon richer with casing notes, Prolog with a RETIREMENT line) — a pre-existing divergence left untouched here; only the new DUAL-ROLE addition is synced. A full re-sync of the whole block is a separate cleanup. This edit changes the convention only; the emitter wiring + cross-lang switch are the DEFERRED items noted above.

## ⛔ SHARED-LOWERER ONE-FILE CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The AST→IR lowerer's SHARED SPINE is **ONE file** — `src/lower/lower.c`. **AMENDED (Lon 2026-06-04):** Prolog's goal-role family lives in `src/lower/lower_prolog.c` (`d6d93c6`; shared helpers in `lower_internal.h`); remaining languages stay co-located in `lower.c` until Lon splits them out.

1. **ONE CASE PER KIND.** Each `TT_*` is at most ONE `case` label per role switch. **NEVER duplicate the label.**
2. **LANGUAGE VARIATION LIVES INSIDE THE CASE.** Branch on `cx.lang` within the one case. A language graduates to its OWN `lower_<lang>.c` ONLY by Lon's directive.
3. **EDIT ONLY YOUR OWN LANGUAGE'S ARM.** Never modify, reorder, or delete another language's arm.
4. **A MISSING LANGUAGE ARM FALLS LOUD.** Routes to `lower_unhandled` — never a silent default.
5. **SHARED SCAFFOLDING IS ADDITIVE; SIGNATURE/SEMANTIC CHANGES ARE LOCKSTEP.** Changing `lcx_t` or shared helpers → MUST update all three GOAL files in the SAME commit.
6. **`scripts/prove_lower2.sh` must stay green before every commit.**

**COMPLETION TEST:** (a) no duplicated `case TT_` label; (b) every case ends in a real arm or `lower_unhandled`; (c) FACT RULE body byte-identical across the three GOAL files; (d) `scripts/prove_lower2.sh` green.

## ⛔ TEMPLATE-ONLY EMISSION — ONE-DISPATCH CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The unified IR→x86 emitter is **ONE dispatch** — `src/emitter/emit_core.c`'s `switch (nd->t)` — fanning out to per-box template functions under `src/emitter/{BB,SM,XA}_templates/`.

1. **ONE DISPATCH CASE PER IR KIND.** Append new cases at the END of the language's contiguous block. **NEVER duplicate the label.**
2. **ONE TEMPLATE FILE PER BOX.** Each box's bytes live in its OWN `.cpp`. Never append a second box's body into a peer's file.
3. **EDIT ONLY YOUR OWN LANGUAGE'S BOXES.**
4. **BYTES LIVE ONLY IN TEMPLATES — A MISSING BOX FALLS LOUD.** FORBIDDEN outside template fn: `seg_byte(SEG_CODE`, `SL_B(`, `sl_emit_one`, `emit_standard_blob`, raw byte-producers. `scripts/util_template_purity_audit.sh` is the standing guard.
5. **THE SHARED SOURCE LIST IS ADDITIVE; BUILD/ABI CHANGES ARE LOCKSTEP.** Makefile `RT_PIC_SRCS` is APPEND-ONLY. Changing shared emitter primitives → MUST update all three GOAL files in the SAME commit.
6. **Before every commit:** `util_template_purity_audit.sh`, `test_gate_em_template_byte_identity.sh`, `test_gate_em_template_matrix.sh`, `test_gate_icn_no_stack.sh`, `test_gate_icn_one_reg_frame.sh` must stay green.

**COMPLETION TEST:** (a) no duplicated `case IR_` label in `emit_core.c`; (b) every `IR_*` kind has one dispatch case; (c) zero forbidden byte-emitters outside templates; (d) FACT RULE body byte-identical across the three GOAL files; (e) emitter gates green.

## ⛔ NO DUPLICATED LOGIC — WRITE EACH PIECE OF LOGIC ONCE (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

**THE ONE LAW: each piece of logic is written ONCE.** A box does PORT work (α/β/γ/ω wiring). The runtime does VALUE work. When a box reimplements VALUE work inline, you get duplication.

**DUP FORM 1 — SAME ALGORITHM IN TWO MEDIA.** Delete both media walkers; make it ONE `rt_*` call. TEXT emits `call foo@PLT`, BINARY emits `movabs rax,&foo; call rax` — two trivial encodings of ONE call.
**DUP FORM 2 — EMIT-TIME LOGIC THAT IS A RUNTIME JOB.** Any template with a recursive walker / arithmetic evaluator / term constructor = VALUE work in wrong place → move behind ONE `rt_*` call.
**DUP FORM 3 — OPERAND BOX REIMPLEMENTED INSIDE ITS CONSUMER (fusion).** Consumer reading `pBB->α->ival/sval/dval` or `->α->t==IR_LIT_*` = fusion = duplicated operand logic. Consumer must READ the operand's slot.
**DUP FORM 4 — N DIFFERENT BOXES IN ONE FILE (cram).** Split distinct shapes behind a thin router.

**NOT DUPLICATION:** (a) same byte pattern hand-copied into each per-box template (REQUIRED); (b) per-file op-classifier tables; (c) near-identical shapes grouped in one parameterized file; (d) two ARMS of one box (BINARY/TEXT) = two encodings of one logic.

**THE TEST:** could a bug require fixing the same logic in two places? If yes → duplication → collapse it.

**COMPLETION TEST:** (a) no algorithm appears in both TEXT and BINARY arm — value work is ONE `rt_*` call; (b) no emit-time reimplementation of runtime value work; (c) no `pBB->α->ival/sval/dval` / `->α->t==IR_LIT_*` in a consumer box; (d) one four-port shape per `_str()`; (e) FACT RULE body byte-identical across all four GOAL files.

## ⛔ X86-64 REGISTER / SUBJECT-MODEL CONVENTION (FACT — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

| Reg | Class | Name | Role |
|-----|-------|------|------|
| **R13** | callee-saved | **Σ** | subject BASE ptr |
| **R14** | callee-saved | **δ** | CURSOR |
| **R15** | callee-saved | **Δ** | subject LENGTH/END |
| (scratch) | — | **σ** | TRANSIENT current-char ptr `Σ+δ` |
| **R12** | callee-saved | **ζ** | BB-local RW FRAME base; every box-local is `[r12+off]` |
| **R10** | caller-saved | (retired) | RW box-locals → `[r12+off]` (ζ frame); RO → `[rip+disp]`. r10 RETIRED (R10-OUT) |
| **rbx** | callee-saved | — | FREE / callee-saved scratch |
| **rbp** | callee-saved | — | brokered function frame ptr / callee-saved scratch |

**DUAL ROLE — R13/R14/R15 ALSO CARRY THE PROLOG TRAIL (RATIFIED Lon 2026-06-13).** Prolog has no subject string, so the subject trio Σ/δ/Δ is idle and instead carries the TRAIL — Prolog's one main attraction (its single shared binding-undo spine) — in the SAME base/cursor/end shape, casing preserved (UPPER = fixed, lower = moving):

| Reg | subject (SNOBOL4/Icon) | Prolog TRAIL — `Trail{stack;top;capacity}` |
|-----|------------------------|---------------------------------------------|
| **R13 = Σ** (UPPER, fixed) | subject BASE ptr | trail `stack` — base of the `Term*` array |
| **R14 = δ** (lower, moving) | CURSOR | trail `top` — the mark; "push" = ++, "unwind" = set back |
| **R15 = Δ** (UPPER, fixed) | subject LENGTH/END | trail `capacity` — the fixed bound |

The physical registers are SHARED — never live in two languages at once. A cross-language BB jump save/restores the trio (DEFERRED — its own later rung; not yet wired). The trail in registers replaces the `g_resolve_trail` symbol load with pure register traffic. **RBP stays RESERVED** (its brokered-frame role is dead under NO C BYRD-BOX; held for a future use TBD — Lon). This DUAL-ROLE addition is byte-identical across all three GOAL files; the subject rows above remain each file's own.

**γ-success return packing:** `rax = σ ptr`, `rdx = δ int` (spec_t).

**RETIREMENT:** `Ω`→`Δ`, `Σlen`→`Δ` (both fold into `Δ`). Rename sweep done. Changing any assignment is LOCKSTEP — update all three GOAL files in the SAME commit.

## ⛔ MANDATORY READ BEFORE EVERY SESSION

**📖 REQUIRED DESIGN READING — read BOTH before touching any Prolog BB code (Lon, 2026-06-14):**
- **`ARCH-PROLOG.md`** — the Byrd-Box Prolog *design*: the ⚠️ NO-VALUE-STACK correction, the four-port (α/β/γ/ω) control model layered on the `Term*` + trail + parent-linked-CP substrate, **callee-resumability-as-a-CLOSURE-value** (δ/ε ports abolished), and `bounded`/determinacy-first-class. This is the "how a Prolog construct becomes a box" reference.
- **`DESIGN-PROLOG-BB-ALL.md`** — the plan to build BB for **ALL GDE + regular constructs**: the §A–§H coverage grid (GNU vs SWI feature frontier realized as Byrd Boxes on our trail+closure spine + GNU in-core CLP(FD)), the **merged build order** (`bounded` pass → trail-mark/conditional-trailing → `aggregate_all` → catch/throw → retract/abolish as DB-cursor generators → tabling/engines on the `Create`/`CoRet`/`CoFail` triplet), §9 the stackless re-derivation (every WAM/SWI "stack" dissolved into a pure-functional indexed frame), and **§10 the data-structures / globals NOT-USED list** — the authority on what must NEVER get a `g_*` (the `test_gate_pl_no_new_global.sh` allowlist enforces it). When unsure whether a construct needs a new structure, §10's answer is: the trail + frame cells, nothing else.

**Pipeline:** `Prolog AST → lower_prolog (four-port IR) → IR_interp.c (m2) → bb_*.cpp x86() templates (m3 BINARY / m4 TEXT)`

**⛔ PROEBSTING IS THE CANON.** gprolog/SWI-Prolog are observable-semantics oracles ONLY — never design authority.

**Three modes:** m2 `--run` (IR_interp, reference oracle) · m3 `--run` (EMIT BINARY → RX slab) · m4 `--compile --target=x86` (EMIT TEXT → as+gcc, separate process).

**⚠ m4 ATOM_* WARNING:** `ATOM_DOT`, `ATOM_NIL`, `ATOM_TRUE` etc. are initialized by `prolog_atom_init()` called from `rt_main_init()`. In m4 compiled binaries, `rt_main_init` is called by the rich-body-root preamble but NOT by the GZ preamble (which calls only `rt_trail_mark` + `rt_pl_cells_init`). Runtime helpers called from GZ templates (`unification.c`) must use `prolog_atom_intern(".")` / `prolog_atom_intern("[]")` directly — never `ATOM_DOT`/`ATOM_NIL` — or they will see `-1` in m4 GZ binaries.

**Port semantics:** γ = success continuation (inherited DOWN) · ω = failure continuation (inherited DOWN) · α = fresh-solve entry (synthesized UP) · β = redo/retry entry (synthesized UP).

**Absolute rules:** No C Byrd boxes. No SM/BB walking at runtime in Mode 3/4. Four ports = Greek letters (α/β/γ/ω) only.

## ⛔ PER-BOX LOCAL STORAGE — ALL STATE LIVES INSIDE THE BOXES (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

**ONLY local BB allocation variables are used; NOTHING is stored outside the boxes.** No AG ring, no value stack, no NV_GET/NV_SET for intermediates. Two kinds of local allocation: **RO** (`[rip+disp]`) and **RW** (`[ζ=r12+off]`).

### ⛔ NO-RESURRECT — deleted Prolog value-stack push helpers (Lon directive, 2026-05-31)
`rt_pl_atom_push` and `rt_pl_var_push` are **DELETED** and must **never be resurrected**. **GUARD:** `scripts/test_gate_pl_no_value_stack.sh`.

**COMPLETION TEST:** (a) no `bb_exec_once`/AG-ring on mode-3/4 run path; (b) no `g_vstack`/`rt_push_*`/`rt_pop_*`; (c) no `NV_GET`/`NV_SET` for intermediate values; (d) every box-local read is `[rip+disp]` (RO) or `[ζ+off]` (RW); (e) mode-3 BINARY and mode-4 TEXT of the SAME box do the SAME processing.

---

## 🔴 PL-GZ-9 — corpus reconquest

m3/m4 **115**/115 (parity). Ratchet: never regress (floor 115 both modes). The rung suite is fully green in both modes; reconquest continues beyond the rung suite (the broader corpus).

- [ ] **PL-GZ-9** — ongoing; the corpus-wide reconquest beyond the rung suite. See the rung ladder + STATE for live state.
- [ ] **PL-GZ-FENCE** — coupling gate ZERO · GATE-3 m3/m4 verdict-identical · resolution.c + meta rail DELETED · seed `.s` shape-isomorphic to `test_pl_1.c`.

## PL-BENCH - GNU/SWI van Roy benchmark reconquest (Lon 2026-06-25). Bench-1 (g_resolve_env overflow) and Bench-2 (nested-compound-head choice) landed; WS accrual closed s99. REMAINING PROGRAM CLASSES (now tracked under LADDER A features + PL-SPEED): findall+between/forall serialise (bench-3); assert/retract mid-computation (bench-4: sieve, nand); is over a runtime-built expression term (bench-5: eval); arity>8 (bench-6: unify-9, reducer-11, simple_analyzer-12, fast_mu-11/13, nand-13, chat_parser-14). Completion: all van Roy programs oracle-correct x3 modes + bench 22/22.

## Session setup

```bash
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh
make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_prolog.sh         # GATE-1
bash scripts/test_prolog_rung_suite.sh    # GATE-3
bash scripts/test_gate_bb_one_box.sh      # PL-HY-FENCE
bash scripts/test_gate_pl_no_new_global.sh  # NO-NEW-GLOBAL (allowlist + doomed-ratchet; floor 15→0)
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(' src/ --include="*.c" --include="*.cpp" | grep -v "_templates/" | grep -v emit_core.c | wc -l   # 0
grep -rn 'g_vstack' src/ | wc -l          # 0
```

## Architecture reference

Pipeline: Prolog AST → lower_prolog (four-port IR) → m2 `--run` (IR_interp) · m3 `--run` (EMIT BINARY → RX slab) · m4 `--compile` (EMIT TEXT → as+gcc).
GZ ports: δ = callee α, ε = callee β (PORT_DELTA/PORT_EPSILON beside γ/ω/β).

### Per-construct port wiring
| Construct | α | β | γ | ω |
|---|---|---|---|---|
| `IR_GCONJ` (seq) | first goal's α | last goal's β | `goal[i].γ = goal[i+1].α` | `goal[i+1].ω = goal[i].β`; first → ω_in |
| `IR_CHOICE` | first clause α | next clause α | each `.γ = γ_in` | `clause[i].ω = clause[i+1].α`; last → ω_in |
| `IR_GOAL` (call) | callee α | callee β | callee success → γ_in | callee exhausted → ω_in |
| `IR_ITE` | cond.α | ω_in (semidet) | cond.γ→Then, Then.γ→γ_in | cond.ω→Else, Else.ω→ω_in |
| `IR_UNIFY` | self | — | bind/match → γ_in | mismatch → ω_in |
| `IR_CUT` | self | — | γ_in | cut barrier → ω_in |
| leaf | self | — | γ_in | ω_in |

### Admission recipe (new deterministic builtin)
1. New `IR_DET_FOO` in `IR.h` + name table in `scrip_ir.c`.
2. `rt_pl_foo_cell(...)` in `unification.c` — cell-based, trail-mark/unwind, no `g_resolve_env`. Use `prolog_atom_intern()` not `ATOM_*` globals.
3. `bb_det_foo.cpp` — FRQ for each slot, one `call rt_pl_foo_cell`, `test eax,eax; jne γ; jmp ω; def β; jmp ω`.
4. `bb_prepare` block in `emit_bb.c` — populate `op_parts_ival/str`.
5. `emit_core.c` dispatch case.
6. Makefile: `RT_PIC_SRCS` line + explicit compile rule.
7. Four `scrip.c` sites: `pl_gz_rule_body_goal_ok`, `pl_gz_rule_clause` whitelist, `pl_gz_count_synth_goal`, `pl_gz_build_goal` (named arm BEFORE generic comparator arm — critical ordering).

**Key rule:** `ir_call_arg(nd,i)` for builtins lowered via `is_builtin_exec`; `ir_pair_arg(nd,i)` for arity-2 builtins with both args as a pair (arith cmps, succ). Named arms in `pl_gz_build_goal` must precede the generic `IR_BUILTIN && ival==2 && ir_pair_arg` arm or they are intercepted.

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
