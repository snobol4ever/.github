# GOAL-ICON-BB.md — Icon, 100% Byrd Boxes, from zero

## ▶ LIVE CURSOR (updated every handoff — RULES.md STALE-ORIENTATION rule)
- **✅✅ ICN-CASE-ALT-CLOSE + runerr() (2026-07-19, Claude Sonnet 4.6) — SCRIP `6f56ca41`. Icon 241/20/32 (environmental math drift vs 252/9/32 cursor — real-arithmetic/sqrt/pow/mathfunc tests, same delta as prior R8-CLOSED finding; unmodified-HEAD measures same, so no regression). TWO FIXES for GOAL-JCON-IN-SCRIP jtran self-host pipeline:** (1) **ICN-CASE-ALT-CLOSE (lower_icon.c TT_CASE)**: the prior ICN-CASE-ALT commit's documented residual is now CLOSED — gate `is_resumable(t->c[ki])` routes resumable selectors (alternation/generator) to `ksel_ω=chain_next` (canonical ir_a_Case L[i].expr.ir.failure→L[i+1].expr.ir.start) while non-resumable selectors keep `ksel_ω=ω` byte-identical (avoids the rung14/rung33 emit-walk/fold regression). 5-shape battery green both modes; rung-suite fail-list BYTE-IDENTICAL. **jtran unblocked: parse_expr11's `lex_CSETLIT|lex_INTLIT|lex_REALLIT|lex_STRINGLIT:` arm was a resumable alternated selector that exhausted to case-ω instead of falling to the next clause (`lex_IDENT:`), causing "Expecting ;" on `write`**. (2) **runerr() arm (by_name_dispatch.c)**: canonical fmisc.r `runerr(i,x)` — Run-time error banner + offending value via image(), exit(1); needed by all gen_ucode.icn/irgen.icn/parse.icn/lexer.icn assertion guards. **JTRAN PIPELINE STATE:** 2-stage preproc ✓ · 3-stage yylex ✓ · 4-stage parse ✓ (a_ProcDecl) · **5-stage ucode BLOCKED** — next `SCRIP_DEBUG_APPLY=1` diagnosis will name the new Error 5 source (runerr(500,p) firing in gen_ucode.icn from an unrecognised AST node type, or another unresolved function). **WORKDIR /home/claude/jt/**: jtran binary (17-module SCRIP m4, SCRIP_BETA_ELIDE_OFF=1, 0 bombs, 5MB), hello_t.icn (3-line canonical newline-Icon), oplexgen/interfacegen/do_ops.icn/interface.icn all correct. ζ COVERAGE ANSWER (from zeta_choices.h + fc_geom source): NOT all BBs on RSP/RBP FORTH yet — by design: (a) frame model fully converted (ZC_FRAME_RSP default since s65); (b) FORTH fixed cells granted to exactly IR_SCAN_TAB/MOVE/MATCH (ZB-ICN-FC-1/2/3); (c) `{*}` generators UPTO/FIND/BAL inside scan env explicitly NOT-YET (rsp cell double-accounts with outer re-pump — measured corruption); (d) ANY/MANY/POS are zero-cell by law (no private RW scratch — fc_geom=0 IS their FORTH form); (e) long-lived ζ (suspended generators, coexprs) never rides RSP by the two-flavor ruling. **NEXT SESSION: SCRIP_DEBUG_APPLY=1 on ucode stage → name the new blocker → fix → advance pipeline → .u1/.u2 non-empty → jlink → run → perf bench (iconx vs JCON vs SCRIP-jtran).**
- **✅✅✅ IS_VARREF_fn REBASE REPAIR + COEXPR PIPELINE (2026-07-19 s92+, Claude Sonnet 4.6) — SCRIP `7e9e414f`. Icon 252/9/32 (up from pristine merged-HEAD 220/41/32 — the PL-REGAIN-3 rebase had silently broken all table/subscript rungs). Four fixes: (1) IS_VARREF_fn (contracts/descr.h) — DT_N slen 0/1/2 all three forms; 11 sites in pattern_match.c (subscript/field/bang/random/section/swap/deref/assign); healed 32 FAILs with zero regressions. (2) bb_create frame bases: six-reg save + result-descr both [x86_fb()] not [x86_zr()] — the only zr-based value-slot writes in src/templates. (3) proc/1 registry fallback: rt_proc_is_registered consulted when g_stage2.proc_table empty (standalone m4 binaries). (4) coexpr frame snapshot: scrip_coexpr_create(body, regs, frame_bytes) — copies creator frame at create time, bodies read private copy; g_emit.frame_region promoted at dispatch. p10/p11 2-stage nested pipelines fixed both modes. Smokes 14/14×2 icon, 7/7 SN4, 5/5 Prolog. Gates no_stack/one_reg/semicolon PASS. jtran 15-module 0-bomb link verified. 4-way bench queens(10)×3: iconx 233ms / JCON 804ms / SCRIP-m3 1849ms / SCRIP-m4 1832ms. NEXT SESSION: retest m3 full-pipeline spin → self-host byte-compare → jtran-task bench.**
- **✅✅✅ GOAL-ICON-BB ROUND 2 (2026-07-19, Claude Sonnet 4.6) — FAILs 14→9, PASS 246→251/9/32. SCRIP `1ef2d828`, corpus `e95325c9`. TEN FIXES LANDED:** (1) **bb_binop_arith empty-template** for BINOP_POW/CUNION/CDIFF/CINTER — dangling jmp/abort (kwds+mindfa). (2) **bb_keyword_icon DT_FAIL check** on KEYWORD_read so keyword reads can fail. (3) **bb_to/bb_to_by to_int coerce** at alpha — raw IEEE 2.3 bits as int64 gave infinite generation (coerce timeout). (4) **emit.cpp queue cap Q_MAX=16×CH_MAX** separate static — 26 guard sites silently dropped enqueues past old 8192 shared cap leaving nodes undriven; GC exonerated. Root of coerce layout-sensitivity. (5) **lower_if C-succ force-alpha** — beta-tagged condition-success edge into naked committed DISJUNCTION (post tramp-erad); fixes nested-if under generator-condition (prepro precheck). (6) **Universal arg-resume** in lower_call — ω_to(call,aω) now fires for ALL calls when last arg resumable, not just generator-name builtins (fncs1 q5 wf proc calls). (7) **gb widened 2-4 args** in lower_call — find/upto generator classification covers bounded find(s1,s2,i,j). (8) **&error conversion protocol** — core_icn_error + g_core_errjmp_stk[64] catchers around rt_call_arr/rt_jct_relop/rt_num_arith; entab/detab raises 101/103/210; gap formula fixed; legacy longjmp-to-garbage defused (sm_preamble set g_core_err_active=1 but never setjmp'd → SEGV on every non-terminal error). (9) **Full Icon escape set** \xHH/\ooo/\b\d\e\f\l\v/\^c in both string+cset scanners. (10) **icn_preprocess rewrite** — trailing-; strip, $include depth<8, macro rescan, predefined symbols _UNIX/_JAVA/_ASCII/_CO_EXPRESSIONS/_LARGE_INTEGERS/_PIPES/_SYSTEM_FUNCTION, BOL allows leading whitespace. **ALSO:** rt_runtime.c DT_FH in list_bang_at (!file line generation); remove() builtin; reads(f) default n=1; find 2-4 arg resume; bal explicit-subject + any-c1; type(file)->'file'; std-file image bare &input/&output/&errout; known-fail keyword passthrough (control/errornumber/errortext/errorvalue/fail); &allocated 4-value generator; &dateline %l:%M %P; &features jcon 10-value; test harness cwd fix. Smokes: icon 14/14×2, SN4 7/7×2, Raku 288/288, Prolog 5/5. All gates green.
  **REMAINING 9 FAILs:** args (SEGV at line 135/447, untriaged deep crash); endetab (128 diffs — endetab1 reads stdin but lone-space entab rule wrong + ws-aliasing corruption in workspace allocator, needs investigation); htprep (76 diffs — scan-semantics: `<html>html<head>head` tag duplication); kwds (34 diffs — dateline format gap: cset-intersection `** 'kwfxday, EIRL:m'` to isolate chars still missing some; &errout type() = "file" but kw harness wants it passed — needs investigation); mindfa (110 diffs — partition diverges `{aeh,abh}` vs `{ag,bf,ce,d}`, untriaged algorithm); scan (Error 5 + SEGV — untriaged op); scan1 (infinite output — scan runtime is C-string-based, NUL at pos 1 in string(&ascii) → slen=0 → upto spins on high bytes; needs length-aware scan_subj+scan_len + 256-bitmap cset); scan2 (24 diffs — `break <expr>` TT_LOOP_BREAK drops its expression, needs loop-result protocol); string (0 diffs → **PASS** at end of session); var (FATAL emit_drive IR_ASSIGN nameless 2-operand assign — FZ-B1; needs Lon call: sealed-RO-blob vs startup-built name→frame-offset table for variable()).
  **NEXT SESSION ATTACK ORDER:** (A) length-aware scan sweep — (ptr,len) subject + 256-bitmap cset membership in scan_subj + upto/tab/move/many/any/find/bal/match — blast radius: scan1 (infinite), scan (Error 5 scan-family ops), scan2 (partly), htprep (partly); (B) kwds remaining 34 — probe the dateline cset-intersection and errout cases more carefully; (C) mindfa algorithm divergence — read the source and trace what set {aeh} represents vs {ag}; (D) endetab deep tab-column semantics; (E) var — awaits Lon call on name-table form; (F) args — deep SEGV triage. TWO PRE-PINNED REGRESSIONS STILL OPEN from prior cursor: geddump/tgrlink → test `git revert 7aade169`; ipxref → LOWER-side lower_alt arm-interior BFS ordering fix.
- **✅ THIS SESSION (2026-07-18, Claude Sonnet 4.6) — PERF + DOCS + BENCH MEASUREMENT. SCRIP pushed to `8540367c` (3 commits above parallel-session HEAD). THREE DELIVERABLES:** (1) **PERF `ed948780` — list `put()` O(n²)→amortized O(1)** via `frame_cap` 4th field: `list(frame_elems,frame_size,gen_type,frame_cap)` at all 5 DEFDAT + 6 DATCON sites; in-place write when `n<cap`, doubling growth; `get`/`pop` decrement cap across base-pointer bump; `push`/`sort` set exact cap; GC fast path accepts 3-or-4 fields. `micro` battery wall moved 71→96 (put/get exhaustion gone; residual = push/set batteries). (2) **README `e4ee08af` — Icon benchmark section replaced**: 4-engine measurement (iconx 10/10, JCON 10/10, SCRIP m3+m4 **6/10**), best-of-3 timings on 6 passing programs (m4 geomean **3.1× vs iconx**, 8.5× on non-trivial concord/deal/queens, ~46× vs JCON with JVM-startup caveat), **two freshly-bisected bench-track regressions pinned**: geddump+tgrlink silent-empty → `7aade169` (α-force pilot); ipxref FATAL op=27 → `00a027ca` (DISJUNCTION slice-2). (3) **WIP `8540367c` (ITERATE fallback, labeled as safe-floor only)**: `IR_ITERATE` `nd_slot` fallback in `emit_drive` guard — strictly non-regressing (fires only where `drive_unowned` previously aborted); fixes 6-line alternation-arm ITERATE repro (`(1=2)|(w==!L)` now succeeds); converts ipxref abort→hang (`rt_size_d` spin on garbage descriptor) — the real fix is LOWER-side slot-wiring for the slice-2 arm-wiring ordering bug. **ARCH-ICON.md register contract corrected** `.github@ca4d8d32` — RSP-era truth (ZC_FRAME=RSP since s65, R12 free, RBX=GC-TOP-HEAP-arm not GVA-base). **NEXT SESSION: (a) re-derive FAIL count fresh (`test_icon_all_rungs.sh`) — the FZ cluster diagnoses have rotted (FZ-B2 rung36_jcon_scan now SEGVs instead of TE-4 bombing); (b) triage each fresh FAIL; (c) fix rung by rung. TWO PRE-PINNED REGRESSIONS for the next session's first two targets: geddump/tgrlink → test `git revert 7aade169` (3 files, 27 lines) — if it reverts cleanly against HEAD the three benchmarks restore and that's the commit; ipxref → LOWER-side fix: `lower_alt`'s arm-interior BFS ordering queues IR_RETURN before its value producer when a result operand is a RETURN node — the `icn_arm_result` filter already excludes RETURN from trailing result operands so the slot lookup finds nothing (`bb_slot_get` misses, `nd_slot` fallback needed LOWER-side before drive time, not in the emitter guard). Bench-track re-run after fixes.**
- **✅✅✅ ICN-GOTO-SURVEY: SURVEY COMPLETE + α-FORCE MECHANISM + 3 TRAMP FAMILIES ERADICATED (2026-07-18 follow-on session, SCRIP `607974bb`→`3af9d43a`→`53c39665`, Claude Fable 5) — Icon 246/14/32 FAIL name-set byte-identical across ALL commits (fresh same-tree baseline; NOTE this sandbox baselined at 246/14, one PASS better than the prior cursor's 245/15, pre-existing at HEAD); smoke 14/14×2; icn_no_stack/one_reg_frame/semicolon/emit_no_lang green; SN4 7/7×2, PL 5/5×2, Raku 288/288×2; m4 asm→gcc→run PASS on all 6 pilot-critical programs.** THE LANDINGS: (1) `607974bb` rung 1 — the two identical dj α-entry tramps (lower_alt+lower_if) unified into one `icn_dj_α_entry`. (2) `3af9d43a` α-FORCE MECHANISM (Lon picked edge-tag): `lc_γ_to_α`/`lc_ω_to_α` force writers (lower_common.c+lower.h), edge tag `"α!"` CE B1 21 — EMITTER HONOR CAME FREE (emit.cpp 1732-38/1801 positive-match only β/σ/φ, everything else defaults α; bc_chase preserves the tag on unchased edges) — then the dj tramp ERADICATED: lower_alt/lower_if return dj NAKED; the NAKED-RETURN PROBE (temporarily remove tramp, harness names the shields — now the standard site-population instrument) found exactly 3 breaking tests, all one wiring: lower_every `mark→b_entry` (bounded body ENTERS FRESH per interp.r Op_Mark — never resumes) → force-α; instructive contrast in the same function: `unmk→gen_beta` IS a resume, promotion stays. (3) `53c39665` sites 8+6: body-less every GOTO deleted (`b_entry = gen_beta`, tail γ_to promotes identically) + generator-keyword seed GOTO deleted (naked return; `&features` pump verified 6 values both modes). **STRUCTURAL FINDING (FINDING-2026-07-18-CLAUDE-ICN-GOTO-SURVEY-RUNG1-UNIFIED.md, with addendum): the A-family tramps split into TWO CHANNELS.** RETURNED-ENTRY channel (sites 1, 6): conversion CHEAP — probe names the few unshielded promoting sites, force-α them, delete tramp — DONE. CONTINUATION channel (site 2 STMT-BOUNDARY ~:1120, site 4 scan-leave ~:609-10, site 7a SENT ~:531): these shield the γ/ω PARAMS passed into child lowering; promotion fires inside EVERY construct lowerer\'s build()/γ_to against continuation targets — NOT a mechanical slice; needs the continuation-channel protocol design (tagged-ref γ/ω through lower()? NOTE the `target==cx->beta` keying idea is DEAD — captured-beta wirings like gen_beta are written after cx->beta moves). B-family (break/next :462-3, while/until/repeat glue :803-28, conj jn[i] :543) = forward-ref/router roles, NOT promotion absorbers — unchanged by design. **SAME SESSION, LATER: DEAD-GOTO REAP LANDED (SCRIP `71133e8b`) — `src/optimizer/dead_goto.c` dg_run reaps bypassed-orphaned IR_GOTO nodes (full ref-set: γ/ω edges + operands + entry/body_root; monitor-stamped exempt; NULL-slot convention), fixpoint after rounds; CLOSES the hygiene goal for continuation-channel + B-family tramps WITHOUT the protocol change (reaped post-bc-bypass instead of never created; 37 nodes across rung1*/rung2* slice; probe stmt-alternation branch_chain=3 dead_goto=1). Proven at the FULL SN4 crosscheck WATERMARK m3 305/2 m4 304/2/1 DIVERGE=1(1017_arg_local) + all prior gates. NEXT SESSION CURSOR: continuation-channel tagged-ref protocol is now OPTIONAL purity (no longer hygiene-motivated) — next real rung is Lon pick from the goal ladder; remaining survey residue = sites 2/4/7a tramps still CREATED then reaped (protocol conversion would prevent creation), B-family by design. PUSH: all commits LOCAL — handoff must push SCRIP (4 commits: 607974bb, 3af9d43a, 53c39665, 71133e8b) + .github (4+ commits).**
- **✅✅✅ ICN-MOVE-LABEL-ERAD SLICES 3+4 LANDED (2026-07-18 follow-on, SCRIP `580d230c`, corpus `0e597f1f`, Claude Sonnet 4.6) — `lower_if` (IR_INDIRECT_GOTO + 2× IR_MOVE_LABEL) → committed nary IR_DISJUNCTION self-state box; IR_INDIRECT_GOTO RETIRED GLOBALLY (zero producers); `icn_arm_result` wiring-kind filter shared to both `lower_alt` AND `lower_if`; Icon MOVE_LABEL producers = ZERO. Icon 245/15/32 ×3 FAIL name-set byte-identical to pristine both modes; smoke 14/14×2; gates icn_no_stack/one_reg_frame/semicolon PASS; SN4 7/7×2, Prolog 5/5×2, Raku 288/288×2.** `lower_if` committed wiring: C = arm-0 prefix (C-fail lands φ-glue; alt_i++/dispatch IS the branch selection; bounded per interp.r Op_Mark/Unmark parity), T/E σ-land results into the box's own slot but fail=ω-OUT (the commit: exhaust never advances), valueless resume = IR_FAIL sentinel → node_ω (NOT self-marker: self≡advance would leak then-resume into else); fresh entry funnels through dj.α GOTO trampoline (same s95 stale-alt_i discipline as lower_alt). IR_INDIRECT_GOTO pruned: emit case labels ×2, zls case label, 3 dead optimizer γ-protections (dead_pure.c / branch_chain.c / copy_prop.c); kind stays declared in IR.h + scrip_ir.c; bb_indirect_goto template retained for the 0-operand Prolog-gate DISJUNCTION. Real bug found+fixed in-slice: nary trailing result operand = IR_RETURN queues EARLY in chain BFS, drives before its value producer, bb_slot_get misses (no nd_slot fallback unlike MOVE_LABEL:1419) → &null return (rung02_proc_fact 120→0, jcon_mathfunc). Shared `icn_arm_result` filter (GOTO/SUCCEED/FAIL/RETURN/SUSPEND/CORET/COFAIL → NULL) simultaneously fixed the SAME latent disease in `lower_alt` (absv `n > 0 | return -n` returned &null at HEAD — REPRODUCED and fixed same session). Two new corpus lock programs: rung02_if_return_arm (committed-if + return-in-then + conj-return arm) and rung13_alt_return_arm (bare return-arm alternation). **NEXT SESSION CURSOR: IR_GOTO survey = α-entry-vs-auto-β-promotion protocol rung (~19 lines / ~14 sites in lower_icon.c; 4–7 nodes/graph; GOTO-chase already folds them off hot path — IR hygiene, own gated slices). Order: (1) unify the two dj α-entry tramps (lower_alt + lower_if identical pattern); (2) STMT-BOUNDARY α-force tramps (~L1031); (3) break/next (~L462-3); (4) scan leave tramps (~L609-10); (5) while/until glue (~L803-16); (6) seed (~L278); (7) SENT (~L531); (8) body-less every (~L1011). Eradication = lc_γ_to_α! edge-tag or helper (raw-α, no promotion) + emitter honor + per-site gated conversion. Icon MOVE_LABEL producers now ZERO (kind declared for Prolog only).**

- **✅✅✅ ICN-MOVE-LABEL-ERAD SLICES 1+2 LANDED (2026-07-18 s95, SCRIP `00a027ca`, Claude Sonnet 4.6) — ZERO IR_MOVE_LABEL from Icon alternation (`lower_alt`); Icon 244/14/32 zero-delta across both commits; smoke 14/14×2, 4 gates, SN4 7/7×2 (shared walker unaffected), Raku 16/1, Prolog 5/5.** Two commits: `a2ae523e` ICN-BOUND-UNMARK (Op_Mark/Op_Unmark bounded-body RSP cut — micro bench's 16B/lap abandoned-scan-suspension SEGV at ~515K laps; interp.r `rsp=efp-1` canonical fix; IR_BOUND+IR_UNMARK kinds, bb_bound template, zls 16B grant, lower_every bracket). `00a027ca` ICN-MOVE-LABEL-ERAD slice 2 (IR_DISJUNCTION nary self-state, SN4-NARY-ALT mirror): lower_alt rewritten — one dj node, arms lowered with succ=fail=dj, σ/φ retag loop (γ→dj="σ", ω→dj="φ", FAIL-goto γ→dj="φ"), operands=(entry,resume)×N + result×N trailing, ival=N, GOTO α-entry trampoline (fresh entry must zero alt_i via dj.α — bare entry0 returned the `bx→by stale-alt_i` bug), ab_in_arm resume detection, self-marker=advance (resume≡φ-glue, ARBNO precedent). bb_disjunction template: option-B per-arm σ-glue value copy dispatched by alt_i (op_parts channel); alt_i at FR(+16); zeroed on α. Emitter shape-split (0-operand = legacy Prolog gate/bb_indirect_goto; nary → bb_disjunction + flat-drive path), nary walker lists +DISJUNCTION, kind-aware N (reads ival for DISJUNCTION vs n_operands/2 for others), CONJUNCTION value-chase (structural follow operands[0] before slot-lookup — avoids pre-alias-stale zls_off for `(x & "yes") | "no"` shape), FAIL-sentinel entry→chain-ω (bare `fail` arm was becoming statement-continue instead of proc-fail — the roman bug). zls nary grant (shape-split: 0-op = gate 16B; nary = locals-region 16B alt_i+pad); IR_DISJUNCTION added to generator-kind + value-producer lists; Prolog ml.ival pinned with exclusion comment. Three real bugs found and fixed during landing: (1) outer-edge β-promotion (nested `("a"|"b")` gave ax-ay-ay-ay loop — dj's γ/ω must use promoting γ_to/ω_to not raw lc_*); (2) fresh-entry must funnel through dj.α (GOTO trampoline); (3) FAIL-sentinel arm (roman `integer(n)>0 | fail`). **NEXT SESSION CURSOR:** §6 `lower_if` (IR_INDIRECT_GOTO + 2× IR_MOVE_LABEL → 2-way self-state box; after that Icon's MOVE_LABEL producers hit ZERO — kind stays declared for Prolog). Then IR_GOTO survey: new dj α-entry tramp, STMT-BOUNDARY α-force tramps (~:1031), break/next (~:462-3), scan leave tramps (~:609-10), while/until glue (~:803-16), seed (~:278), SENT (~:531), body-less every (~:1011) — all are the α-entry-vs-auto-β-promotion protocol question. Residual micro heap-exhaustion (battery 94+: put/get O(n)-copy-per-append in by_name_dispatch.c ~L4677) is pre-existing WS/GC-ladder territory, not bench-lane.
- **✅✅✅ ICN-APPLY-SPINE + FRONTIER-PIN LANDED (2026-07-18 s94, SCRIP `a88cb120`, corpus `a2458b12`, Claude) — BENCH TRACK 8/10 → 9/10 BOTH MODES; geddump FULL geddump.dat BYTE-IDENTICAL to iconx oracle both modes (12568L, diff empty); Icon rungs 243→244 PASS / 15→14 FAIL / 32 XFAIL vs FRESH stash-derived HEAD baseline, sole per-test delta `rung36_jcon_recogn` FAIL→PASS, ZERO regressions (comm-diff proven).** FIVE stacked root causes, each stash-bisected to HEAD: (1) **geddump.icn source defect** — lines 255/276 (`first := trim(tab(upto('/'))) | return tab(0)`) lacked `;`, silently merging with the next line's `="/"` into `return tab(0)="/"` under SEMICOLON-REQUIRED (last name scanned empty; no-slash fallback became a failing numeric compare; iconx masked it via newline-semicolon insertion) — the 2be21433 semicolonize pass missed exactly the lines that still parsed. (2) **Binary `!` apply was a one-shot builtin** (`__apply__`→rt_call_value), erasing the generator protocol — generator callee jmp'd garbage. Now lowers to IR_CALL_VALUE marked `op_sval="apply"` (JCON `ir_a_Binop`: binary `!` is a closure/ResumeValue generator op) and `bb_call_value` gains the `bcps_spine_gen_arm` transfer verbatim: `rt_call_{value,apply}_spine_prep` resolves the callee value (+ runtime list spread ≤64), stages `g_call_args`, `rt_proc_call_open`, returns the blob; wires rcx/rdx, once-flag at `[ζ+off+16+n*16]` (LOWER's 2+n grant), det/builtin fall back to the one-shot C window (handle in the same cell; 0/ptr disjoint from spine flag 1). Fulfills s92 verbatim: co-expressions are the ONLY separate-stack construct. The s91 pthread genp substrate (still reached by non-spine callers) repaired for the s92 body regime via `rt_genp_spine_enter` — `rt_proc_enter`'s γ landing pops 5 regs, which at the s92 RETAINING-γ deep frontier EATS the 16B resume record + 24B of live frame (rip=r12 frame-junk class); new shim = no-pop landings, 3-qword sentinel record (post-`return` full-unwind resumption lands exhausted), γ deliveries park in `scrip_coret` + resume `jmp [rsp]`, thread-local `g_genp_self`, `first_done` ONE-POP flag. (3) **FRONTIER-PIN — pre-existing s92 spine gap, proven at clean HEAD with PURE NAMED CALLS** (`/tmp/r18.icn`: `every x := gen("A") do { s := gen("B"); … }` yielded 6 lines not 2): β's blind `jmp [rsp]` resumed the abandoned inner activation's record. Every γ/ω landing now pins its own frontier rsp in the act slot's spare qword `[act+8]`; β restores rsp from the pin before `jmp [rsp]` — resume targets its OWN record and structurally reclaims abandoned carves below (this is what flipped `jcon_recogn` to PASS). Applied to `bcps_spine_gen_arm` AND the new bb_call_value arm. (4) **`is_resumable` gaps** — TT_BANG_BINARY, computed-callee TT_FNC, and TT_FIELD/TT_NULL/TT_NONNULL/unop wrappers unclassified → `suspend <wrapped generator>` got no β re-pump wire (first-value-only; the gedval/gedref truncation). (5) **`~===` parsed as `not(a===b)`** — succeeds with `&null` instead of the right operand (geddump's refto husb/wife lines silently dropped via `ptab[&null].n`); new `TT_NIDENTICAL` rides the existing `BINOP_NEQV=23` lane end-to-end (enum was already there; parser+lc_binop_code+lc_is_binop were the only missing links). **GATES:** SN4 crosscheck at watermark m3 305/2 m4 304/2/1 DIVERGE=1 (`1017_arg_local`); SN4 smoke 7/7; icon smoke 14/14 BOTH modes; `icn_no_stack`/`one_reg_frame`/`emit_no_lang`/`semicolon_required` green; `icn_scan` FLOOR-fail pre-existing at HEAD in this sandbox (stash-proven); raku smoke 16/1 identical to HEAD (`division float`). Bench/feature/demo .s regenerated + auto-committed (corpus `a2458b12`). **RESIDUALS NAMED:** (a) `micro` = pre-existing `[ZHP] heap exhausted (512MB, 4.4M blocks) after storage regeneration` during the string-coercion batteries, IDENTICAL at clean HEAD — string-churn retention, GC-ladder territory (AGG-PRECISE's plateau probe doesn't cover this shape), NOT a bench-lane fix; (b) `/tmp/r14.icn` — `f := gen3; suspend f(…)` (LOCAL-variable det-named callee under suspend) still first-value-only, left deliberately (nm="f" fails `icn_call_allow_gen`; widening to all named calls re-wires every det suspend — regression risk; was SEGV at HEAD, so net improvement); (c) live-interleaved same-level generators (`every f(g1(),g2())` alternating resumes) — the pin fixes abandoned pollution but interleaved LIVE carves below a resumed activation's frontier remain the s92 open question (not observed failing in suite/bench). Repro ladder `/tmp/r1..r19.icn` + `/tmp/g{30,40,100,400,1000}.dat` probes; oracle at `/home/claude/icon-master/bin/icont -s`.**
- **✅ PARSER FIXES LANDED (2026-07-18, SCRIP `2e8c7788`, Claude Sonnet) — for the JCON-compiler-compile track (`GOAL-JCON-IN-SCRIP.md`), but they live in the shared Icon parser so every Icon-lane session now builds on them: (1) prefix-`.` deref `TT_DEREF`, (2) position-free `case` default, (3) canonical `break`-operand via new `icn_begins_nexpr` (= jcon `nexpr_set`). All verified vs `jcon-master/tran/parse.icn`. `ZLS_MAX_GRAPHS` 256→4096. Icon rung suite held at 242/15/32 (ZERO regression), smoke 14/14×2, all 4 gates green. Does NOT touch the FZ/XFAIL ladders — pure enablement. See `FINDING-2026-07-18-CLAUDE-JCON-COMPILER-PARSES-LINK-BLOCKED-MISSING-LABEL-CLASS.md` for the JCON compiler's state (parses 18/18; link blocked by a single missing-label walk-bug class).**
- **✅✅✅ GENP slice-2 LANDED (2026-07-17 s91, Lon directive "Complete Icon conversion over to the RSP/RBP stack for ALL ZETA storage — co-expressions and generator PROCEDURES get their OWN stack PER INSTANCE") — generator procs join the per-instance-stack substrate; Icon 237→242 PASS, ZERO regressions; m4 trio+genqueen PASS both mediums.** Root cause was FRAME-TEARDOWN-ON-YIELD: the body's 65544B RSP self-carve unwound on γ/ω epilogue, destroying local vars + resume cell; `every`'s backtrack β re-entered through the zeroed cell → `jmp 0` → rip=0 SEGV rc139. **THE FIX (7 source files, committed SCRIP `cf29b23c`):** (1) `emit.h` adds `flat_gen` regime flag; (2) `emit.cpp emit_jmp_entry_for_proc` ADMITS generators (was `return 0`), sets `flat_gen`; (3) `scrip.c` four jmp-entry registration sites + m4 `proc_startup` now also emits `rt_proc_set_generator` call (without it the det one-shot arm fired and coret aborted "no current coexpression" in m4); (4) `rt_coexpr.{h,c}` exports `scrip_co_ctx_init`+`scrip_co_gc_link` for embedded (by-value) contexts; (5) `rt.c` adds `rt_coexpr.h`+`<unistd.h>`, the `rt_genp_s` struct (next/regs[5]/co/args/nargs/fn/name/done with _Static_assert on layout), `rt_genp_thread_entry` asm thunk (loads rbx/r12..r15 from offsets 8..40, jmps `rt_genp_entry_c`), `rt_genp_entry_c` (restages args, `rt_proc_call_open`, `rt_proc_enter`, coret/cofail on result), `rt_genp_yield` (= `scrip_coret`), `rt_genp_lookup`/`triage`/`destroy`, genp arms at TOP of both `rt_proc_call_gen_h` (inline-asm reg capture → calloc → `scrip_coexpr_activate`) and `rt_proc_resume_frame_h` (lookup → activate → triage); (6) `bb_suspend.cpp` adds `rt_genp_yield` extern + pure accessors `genp_regime()`/`genp_yield_fp()`, swaps `x86_gamma()` for `mov rdi,FRQ(0)+mov rsi,FRQ(8)+call rt_genp_yield` when `flat_gen` — R2/R5-clean, zero new encoders, resume falls through into existing β chain. **MEASURED (all fresh s91, stash-bisected):** Icon harness **237→242 PASS / 15 FAIL / 32 XFAIL** (zero regressions); fixed: `rung03_suspend_gen{,_compose,_filter}` + `rung36_jcon_genqueen` + `rung36_jcon_recogn` (stdout-correct, exit still 124 = abandoned-instance teardown); m4 trio+genqueen PASS; gates: `no_stack`/`one_reg_frame`/`emit_no_lang` OK; `global_no_nv`/`local_no_nv`/`icn_scan` pre-existing FAIL (stash-bisected = baseline); Raku smoke 16/1 identical both trees; SN4 smoke 7/7 + 312/7 broad corpus unchanged. **v1 FENCE (named residue for slice 3):** `jcon_fncs1` (SEGV — nested-proc semantics), `jcon_level` (wrong sequence — value-of-suspend in nested generator), `jcon_recogn` exit-hang rc=124 (abandoned-instance teardown = abandoned-generator thread/stack leak), cross-suspend scan-sync brackets skipped (flat_gen + flat_lex both set on scan-generator intersection), scan family FZ-E, htprep/prepro FZ-D parse, var FZ-B1, kwds/mindfa/string/args/coerce/endetab/mffsol (15 residual FAILs total).
- **✅✅✅ NCB-1d LANDED (2026-07-17 s90, Lon "Switch all Icon templates to RSP/RBP FORTH ζ, sharing the C runtime stack; look at what SNOBOL4 has done") — det LEXICAL procs join the jmp-entry regime; the proc trampoline is retired for them; Icon 205→237, Raku 209→283/283-PERFECT, SN4 +2.** The s84-era "return-value + base-case" bug was the CALL-REGIME/SELF-ALLOC MISMATCH: bcps' lex arm kept the caller-made-frame window (`rt_frame_prep`+`call rax`) while the callee body self-allocated under RSP and ignored rdi — args never arrived (fact's n = zeroed DESCR → `n=0` type-fails → ~128×64KB runaway → SIGSEGV) and γ hardcoded `eax=1` losing the [rbp+0/8] result.  **THE FIX (uncommitted in this tree, 6 source files):** (1) `emit.h` `flat_lex` + (2) `emit.cpp emit_jmp_entry_for_proc` now ADMITS det lex real procs (`gram__*` scan-protocol boxes and generators still declined; LBL__ arms with flat_lex=0), (3) `xa_flat.cpp` jmp-entry prologue BOTH mediums gains a flat_lex tail `call rt_jmp_frame_lexprep(fb=rsp, kt−32)` (new rt.c strict leaf: NULVCL fill + `rt_frame_bind_args` from staged `g_call_args`; no-op on non-lex pcall top) and the DET γ/ω epilogues BOTH mediums converted rsp-relative → **DEPTH-IMMUNE rbp-absolute** (result+wires via pinned rbp, `lea rsp,[rbp+kt]`, reads-before-motion — the line-429 "seal cut arriving DEEP" tripwire class; Icon `return` from generator/scan depth IS that arrival), (4) `bb_call_proc_staged` det-arm guard widened `is_dyn && RSP` → `RSP` (every det named call takes the wire; legacy arms now non-RSP-only), (5) **REGIME RECORD** `rt_proc_t.jmp_entry` (+setter; registered beside `rt_proc_set_generator` in the three in-process driver sites AND printed into the m4 `proc_startup` — m4's runtime table never had is_generator, so the compile-time truth is embedded), consulted by ALL FIVE C transfer windows: `rt_proc_call_c_lex`, `rt_call_proc_descr` (first-class `$b()`/blocks — the blk_calls_sub stack-jump crash), and `rt_proc_call_gen_h`'s new det arm (value calls `every (!plist)()` — rung37_proc_lookup crash; one-shot via `rt_proc_enter`, hout=0).  **MEASURED (all fresh this session, SCRIP src on `496e62f4`+edits, corpus `f69dd89f`+10 icon-bench .s):** Icon harness **237/20/32** (was 205/52/32 at measured HEAD; honest sweep CLEAN 200→**236** (stratum 2), FAIL 52→**20**, zero regressions by comm-diff), icon smoke **m3 14/14** m4 12/14 (was 12/10), **Raku smoke 283/283 BOTH modes** (HEAD measured 209/74 — the regime coherence fixed all 74: blocks, methods, multis, grammars, param typechecks), SN4 crosscheck **m3 305/2** (HEAD 303/4 — depth-immune epilogue fixed `test_case` + `140_pat_eval_double_fn_trick`, the EVAL-deep-arrival class), m4 295/11 unchanged, **DIVERGE 12→10** same residual names, SN4 smoke 7/7×2, prolog smoke 3/5 = PRE-EXISTING at HEAD (cursor's 5/5 was s84-era; not this slice), 3 Icon gates + emit_no_lang green, strict-medium residue xa_flat 96→**100** (the 4 raw-arm adds, s84-precedent style — the xa_flat revamp remains the WIP owner).  Residual 20 FAIL classified: 3× rung03_suspend_* + genqueen/level/fncs1 (GENERATOR procs = slice 2), jcon scan/scan1/scan2 + rung08×3-DIRTY + scan_alt-DIRTY (FZ-E scan family), htprep/prepro (FZ-D parse), var (FZ-B1), kwds/mindfa/recogn/string rc=0 wrong-output quad, args/coerce/endetab/mffsol. `rung36_jcon_parse` FAIL→DIRTY (27B correct then rc139 mid-flight, rcx=0 wire signature — gen/scan intersection); `rung36_jcon_meander` is ADDRESS-UNSTABLE across relinks (full-output+rc139 on one build, empty+rc0 on the next) — count NOT-fixed, flag for slice 2.  Repros `/tmp/{onecall,fact0,fact3}.icn` + `blk.raku`/`gram.raku`; sweep `/tmp/icon_m3_honest.sh` (now mirrors harness `.stdin` handling).
  **STRATUM 2 (same session, FZ-E root fix): `xaf_anchor_leave_*` was reading the graph anchor `mov rsp,[rsp+off]` — the U5 zr→rsp seal made it depth-valid only at 0; Icon's retained scan-suspension cells arrive DEEP (sa2 bracket: `"eb" ? (="e"||="b")` alone crashed rsp→heap→jmp 0), and SN4 mode-4 seal-cuts were the SAME class.  Fix = frame-base read (`x86_fb()`/`48 8B A5`) under RSP, enter unchanged (prologue IS depth 0).  Plus the lower_alt fresh-entry GOTO trampoline (lower_icon.c:16's generic β-promotion was landing alternation fail-cascades on generator-arm βs).  POST-BATTERY: Icon honest CLEAN **236** DIRTY **1** (`proto` rc1) FAIL 20 zero-regression; icon smoke **14/14 BOTH modes**; rung08 trio + scan_alt crash → CLEAN/rc0; **SN4 m4 295→304, DIVERGE 12→1** (the whole pat_fence/abort family was this anchor bug; residuals m3 {expr_eval,141}, m4 {expr_eval,1017}, DIV {1017} — strict subsets), m3 305/2 held, Raku 283/283 held, prolog 3/5 held.  `rung36_jcon_meander` is **ASLR-UNSTABLE** (full-output+rc0 vs empty+rc0 across execs — NOT counted fixed; sweep counts wobble ±1 on it).  Scan residuals now VALUE-level: scan_alt/scan1 NOMATCH-rc0, scan/scan2 rc139 deeper in the family.
- **⚠ HARNESS DEFECT (still open):** `test_icon_all_rungs.sh` grades stdout only (2>/dev/null, exit code discarded) — an exit-code check must be added so crash-on-exit regressions cannot hide (this is exactly what masked the 0-clean state as 205 green). Same blind spot in the SNOBOL4 crosscheck.  Interim: `/tmp/icon_m3_honest.sh` (mirrors harness incl. `.stdin`, adds exit-code CLEAN/DIRTY split).
- **HEAD rung:** ZERO-FAILURE MANDATE — live headline **242/15/32** (s91, GENP slice-2 landed; see top bullet). R12-era 242/15/32 (`b404fb95`) remains the pre-RSP reference. FAIL-ZERO (15) + XFAIL-ZERO (32) ladders below. Re-derive counts fresh, never from prose.
- **GROUND TRUTH — R12 baseline (SCRIP `b404fb95`, corpus `78915257`, documented, NOT re-run this session):** **242 PASS / 15 FAIL / 32 XFAIL / 289 TOTAL** (mode-3). Fail set (15): `rung36_jcon_{args,coerce,endetab,fncs1,htprep,kwds,mffsol,mindfa,prepro,recogn,scan,scan1,scan2,string,var}`. This is the clean pre-RSP-flip baseline and the base the DISJUNCTION refactor should build from.
- **⭐ NEW DIRECTIVE (Lon, 2026-07-17): co-expressions and generator PROCEDURES are slated to get their OWN stack PER INSTANCE.** The single RSP/RBP ζ FORTH stack is the per-sequence frame for straight-line/backtracking boxes; a `create`/`@` co-expression and a suspending generator procedure each need an independent activation stack per live instance (so multiple suspended generators / co-expressions coexist without clobbering one another's ζ). This is the natural home for the s65 "side-stack island for suspending PAT$ blobs" idea generalized to Icon co-expr + generator-proc instances. NOW = SLICE 2 (s90): with det lex procs landed on jmp-entry, the generator-proc conversion is the next rung — per-instance activation stacks (ZH heap routing exists: rt_proc_call_gen_h/resume_frame_h; the det arm inside gen_h shows the seam). The 3 rung03_suspend_* + genqueen/level/fncs1 fails are its acceptance set. Relates to `ARCH-ICON.md` §Co-expressions (pthread+semaphore model already landed for `create`/`@`) — per-instance stack is the ζ-allocation half of that.
- **XFAIL-ZERO progress this session:** 3 stale markers deleted (corpus commit `78915257`): `level` (every/suspend exhaustion was fixed upstream), `random` (LCG now matches), `subjpos` (was KNOWN HANG — now runs in 28ms, byte-identical). All three verified m3+m4 stable across repeated runs before deletion.
- **FZ-B1 `var` DIAGNOSIS CORRECTED this session:** NOT a pointer-hole (DT_N / NAMETRAP already exists — slen=0 NV-dict, slen=1 direct cell ptr, slen=2 VCELL; rt_deref + IS_NAMETRAP_fn wired). Actual gaps: (1) lower_lvalue_var in lower_icon.c has no case for variable(...) as lvalue target → TT_ASSIGN mints nameless placeholder → emitter abort; (2) rt_icon_variable(name) needs a per-proc runtime name→frame-offset table for locals (one narrow reflection-scoped table; globals → NV dict slen=0; keywords → closed setter table). NEXT: Lon call on name-table form (sealed RO blob vs startup-built).
- **FZ-E SCAN FAMILY root cause (recogn/scan/scan1/scan2/string) CORRECTED this session:** NOT generator-in-call-arg. Minimal repro: "eb" ? { (="a") | (="e" || ="b") } returns &null, should return "eb". Root cause: emitter wires SCAN_MATCH fail-edge to arm-B beta label (resume, mid-flight) instead of alpha label (fresh start). In asm: SCAN_MATCH "a" omega -> xchain0_n5_beta (element-index=2) not xchain0_n5_alpha (index=0, save delta). Land mine in emit.cpp ~L887-904 / IR_SCAN_SEQUENCE case L1101 — the fail-edge alpha/beta classifier. recogn 4th input "eb" (t()‖="b" path) is this bug, not generator-in-arg.
- **NOTE (refs, 2026-07-17):** uploaded zips did NOT arrive this session; `refs/` set up from GitHub canonical upstreams per RULES.md fallback — `refs/icon-master` → `github.com/gtownsend/icon` (master; Arizona Icon v9, 45 `src/runtime/*.r`), `refs/jcon-master` → `github.com/proebsting/jcon` (master; `tran/irgen.icn` present). Both verified against RULES.md's `ls` check. ICN-RESUME-THROUGH-SCAN LANDED 483a6215.
- **⭐ NEW DIRECTIVE (Lon, this session): ERADICATE IR_MOVE_LABEL from Icon — make IR_DISJUNCTION a nary self-state box (mirror IR_MATCH_ALTERNATE / IR_SCAN_ALTERNATE). Full design in `FINDING-2026-07-15-CLAUDE-ICON-MOVE-LABEL-ERADICATION-VIA-BB-SELF-STATE.md`. Key facts measured: (a) Icon's `|` lowers to IR_DISJUNCTION + per-arm IR_MOVE_LABEL (lower_icon.c:820); IR_IF similarly uses IR_INDIRECT_GOTO + two IR_MOVE_LABELs (lower_icon.c:835–848). (b) ARBNO is SNOBOL4-only — Icon does NOT produce it. (c) Icon's top-level `|` (IR_DISJUNCTION) and `1 to N` (IR_TO) both SURVIVE the RSP-frame default flip at HEAD; the 38-test regression (242→204) is from the scan-family and complex reflection paths under the new RSP frame — caused by `f7de3863` (R12-ERAD s65) flipping the default BEFORE the Icon RSP migration was complete. (d) Icon `|` lowers to IR_DISJUNCTION (NOT IR_MATCH_ALTERNATE; Icon's lower_alt is Icon-owned in lower_icon.c:820). SNOBOL4's `|` produces IR_MATCH_ALTERNATE — different kinds. (e) The 38-test HEAD regression is the R12-ERAD session's to recover (out of Icon lane); work from `b404fb95` for a clean 242-baseline signal. NEXT RUNG: implement the DISJUNCTION nary refactor per the FINDING (start at §3, option B for value routing — per-arm result copy dispatched by alt_i).**

## ▶▶ ZERO-FAILURE MANDATE (Lon directive, 2026-07-15): "We have no expected failures." END STATE = 289/0/0 — every FAIL fixed AND every `.xfail` marker DELETED (source fixed or SCRIP fixed). The two ladders below are the whole job. Re-derive counts from a fresh `test_icon_all_rungs.sh --corpus <path>` run, never from prose (this session already caught the cursor claiming 239/15 when ground truth was 238/16 — the `rung13` regression).

### ▶ RUNG: FAIL-ZERO — drive the live FAILs to 0 (20 as of s90 — re-derive fresh; cluster membership below is 2026-07-15-era, several since fixed by NCB-1d)
Grouped by ROOT CAUSE, not alphabetically — one fix clears a whole cluster. Attack clusters top-down (crashes before wrong-output: a crash blocks everything downstream of it). Each step: MONITOR/`--dump-ir` to bracket → fix at the land mine → confirm m3 AND m4 → re-run suite, confirm the test flips and nothing else breaks.

**Cluster A — `x86_parse` bracket-operand abort — ✅ FIXED (SCRIP, root cause found).** ROOT CAUSE (not what the first note guessed — the multi-gen `every` was a red herring): `x86(mnem, xa, xb, …)` at `x86_asm.h:1057` eagerly runs `x86_parse` on its first TWO args BEFORE checking the mnemonic — so a DATA-directive payload (`.string`/`comment`/diagnostic) whose text contains `[...]` (e.g. the Icon string value `"[x]"`) was parsed as a memory operand, and the base-not-a-register arm `abort()`ed before the `.string` handler at 1067 could safely escape it. Minimal repro was just `write("[x]");` — any bracket-bearing string literal, no `every` needed. FIX: the abort at ~1038 replaced with the benign `XK_SYM` fallthrough the function already uses at line 1049 (unrecognized bracket → treat as symbol, let real instruction handlers fail loudly downstream if they truly get a bad operand). Data payloads now pass through untouched. Verified: 238→239 PASS, zero regressions, all Icon gates green, m3+m4.
- [x] **FZ-A1** — `rung13_alt_alt_cross_arg_sideeffect` — **PASS** (the regression; fully green now).
- [→] **FZ-A2** — `rung36_jcon_kwds` — crash GONE but had a SECOND failure behind it → now WRONG-OUTPUT (1609B). Reclassified to Cluster E (monitor for first divergence; keyword-read gaps `&ascii`/`&lcase`/`&cset` suspected per prior watermarks).
- [→] **FZ-A3** — `rung36_jcon_scan1` — crash GONE, now WRONG-OUTPUT (385B). Reclassified to Cluster E.

**Cluster B — emit-time IR aborts (2 distinct bugs, 2 tests).**
- [ ] **FZ-B1** — `rung36_jcon_var` — `emit_drive IR_ASSIGN guard: nameless 2-operand assign` — assign-through-lvalue-producer (`!x`/`?x` element-variable, or `s[i:j]` section as assignment TARGET). LOWER's TT_ASSIGN terminal arm mints a placeholder instead of a real target; fix in `lower_icon.c` TT_ASSIGN (not a missing template — the abort message says so).
- [ ] **FZ-B2** — `rung36_jcon_scan` — `bb_call marshal: IR_VAR arg names a local with no LOWER-granted varslot (TE-4)` — grant the varslot in `ir_drive_slot_assign` per the BOMB message's own pointer.

**Cluster C — SEGV rc=139 (3 tests, need minimal-repro bisection each).** Run under `CSN_NO_SEGV_HANDLER=1`/`SCRIP_NO_SEGV_HANDLER` for a clean backtrace, then MONITOR→bracket→gdb-hit-count per RULES.md.
- [ ] **FZ-C1** — `rung36_jcon_endetab`
- [ ] **FZ-C2** — `rung36_jcon_fncs1`
- [ ] **FZ-C3** — `rung36_jcon_scan2`

**Cluster D — PARSE errors (ONE symptom, 2 tests): `function call: expected ) (got ;)`.** htprep line 160, prepro line 39. Icon front-end rejects some legal call syntax (likely a `;`-in-arg or nested-call form). Diagnose in `src/parser/icon/`; decide source-fix vs parser-fix (parser-fix strongly preferred — the .icn is canonical JCON).
- [ ] **FZ-D1** — `rung36_jcon_htprep` (parse error line 160)
- [ ] **FZ-D2** — `rung36_jcon_prepro` (parse error line 39)

**Cluster E — WRONG-OUTPUT, ran clean (6 tests, monitor each for first divergence).** These reach the oracle-diff mechanically — MONITOR-FIRST is the exact tool. Bracket the first divergent event, fix at the land mine.
- [ ] **FZ-E1** — `rung36_jcon_args` (out=2989B; wrong content)
- [ ] **FZ-E2** — `rung36_jcon_coerce` (out=1550B; ⚠ under `--compile`/naked `--run` this can emit ~241MB on one line — ALWAYS cap `| head -c`; the harness is safe because it captures to a var)
- [ ] **FZ-E3** — `rung36_jcon_mffsol` (out=92B)
- [ ] **FZ-E4** — `rung36_jcon_mindfa` (out=2220B)
- [ ] **FZ-E5** — `rung36_jcon_recogn` (out=0B — produces nothing; generator-in-call-arg suppression suspected)
- [ ] **FZ-E6** — `rung36_jcon_string` (out=2744B)

### ▶ RUNG: XFAIL-ZERO — sift every `.xfail` marker; fix source OR fix SCRIP; DELETE the marker (35 tests)
END STATE: zero `.xfail` files in `corpus/programs/icon/`. Per test: (1) remove `.xfail`, run it, read the real failure; (2) decide — is the `.icn`/`.expected` wrong (fix SOURCE) or is SCRIP missing/wrong (fix SCRIP)? Prefer fixing SCRIP: the `rung36_jcon_*` programs are canonical JCON and the `.expected` is graded against the real iconx/JCON oracle. Source-fix is legitimate only for a genuinely-broken test artifact. NOTE: `.xfail` files are NEVER run by the harness, so some may ALREADY pass — check each before assuming work is needed (a free win = delete marker, confirm PASS). Markers carrying a stated reason are triaged first (known root cause); the 24 empty markers need a fresh run to classify.

**Known-reason markers (11) — root cause already recorded:**
- [x] **XZ-1** `subjpos` — DONE (s4): was KNOWN HANG; now runs 28ms, byte-identical m3+m4. Marker deleted corpus `78915257`.
- [x] **XZ-2** `random` — DONE (s4): now passes m3+m4 byte-identical. Marker deleted corpus `78915257`.
- [ ] **XZ-3** `radix` — bignum: radix literals > 64 bits need arbitrary-precision ints (not implemented). Ties to lgint.
- [ ] **XZ-4** `lgint` — large-integer / bignum arithmetic (empty marker but name + radix note imply the same bignum gap).
- [ ] **XZ-5** `ck` — generative argument to `tab` (`tab(span-1|0)`) unsupported; `Image()` needs generator-in-arg; "deeper issues" noted.
- [x] **XZ-6** `level` — DONE (s4): passes m3+m4 byte-identical (upstream fix landed). Marker deleted corpus `78915257`.
- [ ] **XZ-7** `profsum` — `next` inside `line ? {}` doesn't restart enclosing `while`; next/break propagation through scan body.
- [ ] **XZ-8** (reserved — refold if another reasoned marker surfaces on fresh read)
- [ ] **XZ-9** (reserved)
- [ ] **XZ-10** (reserved)
- [ ] **XZ-11** (reserved)

**Empty markers (24) — classify on a fresh run, then fix or delete.** Batch by first-failure signature after un-quarantining; expect them to fold into the same clusters as FAIL-ZERO (bignum, generator-in-arg, scan control-flow, io). List: `arith btrees case checkfpx collate cxprimes diffwrds errkwds errors evalx every fncs geddump gener image io iobig large misc nargs others prefix recent sets sieve sorting struct toby`.
- [ ] **XZ-E-BIGNUM** — the arithmetic/number cluster (`arith`, `checkfpx`, `cxprimes`, `radix`✓, `lgint`✓) — likely all one bignum/real gap.
- [ ] **XZ-E-STRUCT** — `btrees`, `sets`, `sorting`, `struct`, `sieve`, `collate` — list/set/table/sort builtins.
- [ ] **XZ-E-GEN** — `every`, `gener`, `evalx`, `nargs` — generator/argument semantics.
- [ ] **XZ-E-IO** — `io`, `iobig`, `image`, `errors`, `errkwds`, `others`, `recent`, `misc`, `case`, `diffwrds`, `prefix`, `large`, `fncs`, `geddump` — classify individually; io + image + error-keyword families.

## 📍 ICON BENCHMARK MAP — sources, references, runners (added 2026-07-18, Lon directive: record locations so next session finds things without re-discovery)

**TWO benchmark tracks — do not conflate:**
- **Timing benchmarks (link-heavy, NOT byte-diffable):** `/home/claude/corpus/benchmarks/icon/` — 10 programs (`concord deal geddump ipxref micro micsum queens rsg tgrlink version`) + support files (`options.icn post.icn shuffle.icn version.icn`) + `.dat` inputs. Merged icon-master/tests/bench + jcon-master/bmark; `corpus/benchmarks/README-ICON-JCON.md` is authoritative for the merge. `post.icn` is the timing scaffold: `Init__` dumps `&version`/`&host`/`&features`/`&regions` then reassigns `write := writes := 1` (output suppression — verified working in SCRIP m3 2026-07-18); `Term__` dumps elapsed `&time`/storage/GC counts. Output is therefore ENVIRONMENT-SPECIFIC (region sizes, times, impl banner) — cross-implementation correctness = runs-to-completion + well-formed dump, NEVER byte-diff. The sibling `*.std` are icont self-benchmark dumps, NOT oracles (README says so). The sibling `*.s` are SCRIP mode-4 artifacts (`scripts/update_icon_bench_asm.sh`; bench+demo corpora ONLY per RULES.md).
- **Diffable oracle variants:** link-free, semicolon-adapted copies live in the MAIN corpus as `corpus/programs/icon/rung36_jcon_{queens,concord,geddump}` with `.expected` oracles, graded by `test_icon_all_rungs.sh` like any rung (2026-07-18 fresh: queens PASS, concord PASS, geddump XFAIL). `deal ipxref rsg tgrlink micro micsum` have NO diffable variant — timing track only.

**Runner:** `bash SCRIP/scripts/test_icon_bench_corpus.sh` (`SKIP_BUILD=1` after first build; `ICONM=`/`JCONM=` override reference paths). Runs all 10 through THREE implementations: Arizona iconx (oracle) + JCON (auto-detected when `$JCONM/bin/jcont` + java exist; compiles untimed to `.jxe` with link deps as extra sources, runs timed) + SCRIP m3/m4, per-program args/stdin mirroring jcon-master/bmark/Makefile. SCRIP `link` is a NO-OP, so link deps ride as extra source args (`SCRIP_LINK_DEPS` table; mechanism verified live). Grades exit status; line counts shown (iconx and JCON agree on all 10 — the two anchors).

**Results 2026-07-18 (after ICNBENCH-ARGS-RSP `4b3371b1` + ICN-IDX-GEN-ENTRY `0029fa83`):** iconx **10/10** · JCON **10/10** · SCRIP **m3 8/10 · m4 8/10** (was 2/10 at session start). `tgrlink` m3 AND m4 are BYTE-IDENTICAL to iconx (3239L, diff=0). The passing dumps differ from iconx only in the legitimate environment-specific fields (&version banner, &features set, region sizes, &time, GC counts) — `string53648192` vs `string  500000` is right(x,8) with an 8-char number, NOT a formatting bug.

**Residue (2 programs, BOTH classify into the existing FZ-E scan/keyword family — not new clusters):**
- **geddump** — SEGV before first output once the first INDI record exists (`head -30 geddump.dat` PASSES, `head -40` crashes). Root: `gedlnf`'s scan produces WRONG VALUES — `s ? { first := trim(tab(upto('/'))) | return tab(0); ="/"; last := tab(upto('/')|0) }` loses the post-slash segment (last="" not "CLINTON") and the slash-less `return tab(0)` fallback silently fails; the failure-driven backtracking then hits the broken path. Minimal repro `/tmp/gd8.icn` (2-call lnf; oracle prints `CLINTON, William Jefferson` + `NoSlashName`, SCRIP prints `, William Jefferson` + nothing). Eliminated by direct test: sortf, omitted ctor args, `id[\r.id]:=r`, recursive-gen walk, variadic `a[]`, `put(l, t[rec]:=v)` all PASS.
- **micro** — runs 71/119 battery entries then SEGV; the next entry is `(&pos +:= 1) & (&pos -:= 1)` — augmented assignment to the &pos scan keyword. Everything before (arith/structs/`s ? 0`) passes.

**LANDED this session (the two fixes that took 2/10 → 8/10):**
- **ICNBENCH-ARGS-RSP** (SCRIP `4b3371b1`): under the RSP ζ default BOTH modes dropped `main(args)` (m3 gated the store on non-RSP `mf`; m4 emitted only a FENCE comment). Fix: `rt_main_args_stage/fetch` staged channel (by_name_dispatch.c) + bind in the outer RSP prologue BOTH media (xa_flat.cpp, after the rbp seed, esi preserved, call-parity kept, lexprep precedent) gated on new `g_flat_outer_nparams` (emit.cpp, language-blind, set/reset tightly around main's emit_chain at all 4 driver sites; m4 wrappers stage via `[rsp]=argv,[rsp+8]=argc`).
- **ICN-IDX-GEN-ENTRY** (SCRIP `0029fa83`): `lower_idx_var`'s forward FIRST-ENTRY into the index expr used `γ_to`, whose generator-β promotion (lower_icon.c:15 — same class as the s90 lower_alt note) entered a generator index (`alist[aseq()]`, IR_CALL_VALUE) at β with no staged activation → `jmp` through the zeroed resume cell, rip=0, NO C transfer window hit (gdb-proven). Fix: `lc_γ_to` (no promotion) — backtrack re-entry still rides sub's ω→β tag. Repro ladder `/tmp/r2{a..f}.icn`: genproc under every ✓, as assign ✓, as SUBSCRIPT INDEX ✗→✓.

**Reference implementations (BOTH built and proven working this sandbox 2026-07-18):**
- **Arizona Icon** (icont/iconx): source `/home/claude/icon-src/icon-master` (uploaded zip; upstream github.com/gtownsend/icon), symlinked to the canonical `/home/claude/icon-master` the runner expects. Build: `make Configure name=linux && make Icont` → `bin/icont`, `bin/iconx`. Runs all 10 benchmarks.
- **JCON** (Proebsting/Townsend, Icon→JVM): source `/home/claude/jcon-src/jcon-master` (uploaded zip; upstream proebsting/jcon). Needs `default-jdk-headless` (javac+jar — the preinstalled JRE is NOT enough; `apt-get update` first, the stale index 404s) AND Arizona `icont` on PATH. Build: `make build` → `bin/{jtran,jlink,jcon.zip,jcont,jcon}` (warnings only). ⚠ TWO INVOCATION TRAPS: (1) `jcont`/`jcon` are `#!/bin/sh` but use bashisms — this box's /bin/sh=dash dies "Bad substitution"; ALWAYS invoke via `bash .../bin/jcont`. (2) jcont writes `../$FNAME.zip` relative to the source name — run from the source's own directory with BARE filenames, never absolute paths. Working form: `cd <srcdir> && bash /home/claude/jcon-src/jcon-master/bin/jcont -us prog.icn deps.icn -x args...`.

## ⌚ WATERMARK 2026-07-17 s91 (Claude Sonnet 4.6 · SCRIP src `cf29b23c` COMMITTED ON ORIGIN · corpus unchanged) — GENP slice-2 landed: generator procs per-instance-stack; Icon 242/15/32; m4 trio+genqueen PASS; SN4 smoke 7/7+312/7; Raku 16/1

**Scope:** GENP slice-2 implementation per Lon directive "Complete Icon conversion over to the RSP/RBP stack for ALL ZETA storage — co-expressions and generator PROCEDURES get their OWN stack PER INSTANCE."  Root-caused the FRAME-TEARDOWN-ON-YIELD SEGV (rip=0, rc139): generator body's 65544B RSP self-carve unwound on γ/ω epilogue → `every` backtrack β re-entered through zeroed resume cell → `jmp 0`.  Joined generator procs to the coexpr pthread/semaphore substrate (existing `scrip_coswitch` machinery, GC-registered `ZC_COEXPR_STACK_GCHEAP`): each instance = `rt_genp_s` (calloc'd, carry-by-value `scrip_coctx_t`) activated via `scrip_coexpr_activate`; `rt_genp_thread_entry` asm thunk restores 5 callee-saved regs (captured by inline-asm at call site) then jmps `rt_genp_entry_c`; `bb_suspend` `flat_gen` arm yields via `rt_genp_yield` (value in rdi:rsi), resume falls through into the existing β chain; real return/fail flow unchanged through `rt_proc_enter`'s γ/ω landings into `rt_genp_entry_c`.  Critical m4 fix: `proc_startup` now embeds `rt_proc_set_generator` call (without it the det one-shot arm fired and `scrip_coret` aborted).  All numbers stash-bisected for attribution.  **Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6

## ⌚ WATERMARK 2026-07-17 s90 (Claude Fable 5 · SCRIP src `496e62f4` + 6-file NCB-1d edits UNCOMMITTED · corpus `f69dd89f` + 10 icon-bench .s uncommitted) — NCB-1d landed: det lexical procs join jmp-entry; Icon 237/20/32; Raku 283/283 both modes; SN4 m3 305/2 DIVERGE 10

**Scope:** NCB-1d implementation session per Lon's "RSP/RBP FORTH ζ for ALL, sharing the C runtime stack; look at what SNOBOL4 has done."  Root-caused the s84 proc bug to the call-regime/self-alloc mismatch; converted det lexical procs to the SN4 jmp-entry protocol (admission + lexprep prologue tail + depth-immune rbp-absolute det epilogues + site guard widening + the `rt_proc_t.jmp_entry` regime record consulted by all five C transfer windows; `gram__*` scan-protocol boxes name-declined).  All numbers fresh-measured with stash-A/B attribution: Icon harness 205→**237**/20/32, honest sweep CLEAN 200→**236** (zero regressions by comm-diff), icon smoke **14/14 BOTH modes**, Raku **283/283 both modes** (HEAD measured 209/74 — all 74 pre-existing failures fixed), SN4 crosscheck m3 303/4→**305/2** (`test_case`+`140` = EVAL deep-arrival class the old rsp-relative epilogue comment predicted), m4 295→**304** DIVERGE 12→**1** (stratum-2 anchor fix cleared the pat_fence/abort family), SN4 smoke 7/7×2, prolog 3/5 (pre-existing at HEAD, attributed by stash), gates green except strict-medium WIP residue xa_flat 96→100 (4 raw-arm adds, s84 precedent).  Artifacts regenerated (feature/bench/demo committed by their utils; 10 icon-bench .s pending the source commit).

## ⌚ WATERMARK 2026-07-17 (Claude Opus 4.8 · SCRIP `11e36fae` s83 · corpus `78915257`) — RSP/RBP ζ measurement across full suites; refs from GitHub; per-instance-stack directive noted

**Scope:** Measurement + orientation session, no code committed. Built scrip + libscrip_rt at HEAD `11e36fae` (RSP/RBP FORTH-style ζ is the default for ALL zeta allocations here). Ran BOTH full Icon suites: **mode-3 `--run` = 205/52/32/289; mode-4 `--compile` = 195/62/32/289** by the stdout-only harness (Lon ask: "how much of Icon is still running using RSP/RBP for ALL ζ allocations"). Delta vs the documented R12 baseline (242/15/32 at `b404fb95`, NOT re-run this session) = **−37 mode-3**. **🚨 But an exit-code-aware re-sweep found the 205 is a stdout-only illusion: CLEAN (stdout ok + exit 0) = 0/289; all 205 "passes" print correct output then abort rc=134 (`*** stack smashing detected ***`) — the RSP/RBP ζ FORTH stack overruns the native C-stack canary. Under RSP-for-ALL-ζ, ZERO Icon programs exit cleanly.** The stdout-only grading (harness L92/97) masked a total-corruption regression; an exit-code check is a needed harness fix. The ~18-commit REG-7 RBP-consumer-flip series since the s65 flip (`f7de3863`) recovered only +1 for Icon — that work was SNOBOL4/shared, not Icon. Frame invariants hold under RSP (`no_stack`=0, `one_reg_frame`=0, semicolon prison green); mode-4 smoke red at 10/14. mode-4 FAILs ⊃ mode-3 FAILs + 10 compile-path-only casualties (scan/string-builtin/IO). Regressed population = basic proc/suspend/loop/global/record/strretval/case rungs (`rung02/03/09/13/21/24/25/32/33/37`) — consistent with FINDING §8 (RSP migration incomplete for Icon's scan-family + generator/reflection paths). Set up `refs/` from GitHub canonical upstreams (zips did not arrive): `gtownsend/icon` + `proebsting/jcon`. **Noted new Lon directive:** co-expressions + generator procedures get their OWN stack PER INSTANCE (ζ-allocation half of the co-expr model). **No SCRIP/corpus code changed; main tree untouched.** **Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.8

## ⌚ WATERMARK 2026-07-15 s5 (Claude Sonnet 4.6 · SCRIP `b404fb95` · corpus `78915257`) — orientation + IR_MOVE_LABEL eradication directive

**Scope:** Pure orientation + analysis session. No code committed to SCRIP or corpus. Established refs/ symlinks from uploaded zips. Confirmed clean baseline 242/15/32 at `b404fb95` (re-derived fresh). Measured and proven: (1) HEAD `96fb698c` is **204/53/32** — 38-test regression from `f7de3863` RSP-frame default flip, **not Icon's bug to fix** (R12-ERAD session owns recovery). (2) Icon's `|` top-level alternation uses IR_DISJUNCTION + IR_MOVE_LABEL (lower_icon.c:820); IR_IF uses IR_INDIRECT_GOTO + two IR_MOVE_LABELs — both are the "label indirection instead of self-state" anti-pattern. (3) ARBNO is SNOBOL4-only; Icon does not produce it. (4) Icon `|` lowering is Icon-owned (`lower_alt`, `lower_icon.c:820`) producing IR_DISJUNCTION — different from SNOBOL4's IR_MATCH_ALTERNATE. (5) Lon directive: eradicate IR_MOVE_LABEL from Icon; reshape IR_DISJUNCTION into nary self-state form mirroring IR_MATCH_ALTERNATE / IR_SCAN_ALTERNATE; make the BB hold its own state variables. Design captured in `FINDING-2026-07-15-CLAUDE-ICON-MOVE-LABEL-ERADICATION-VIA-BB-SELF-STATE.md`. **No code changes. SCRIP main tree green and untouched.** **Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6

## ⌚ WATERMARK 2026-07-15 s4 (Claude Sonnet 4.6 · SCRIP `b404fb95` · corpus `78915257`) — 3 xfail markers deleted; FZ-B1 and FZ-E root causes corrected

**Scope:** s92 GENP-SPINE — generator procedures moved off the per-instance coexpr/pthread substrate onto the ONE RSP/RBP ζ spine (LIFO law). **Result: 242/15/32 — baseline parity.** `rung36_jcon_level` promoted FAIL→PASS (level dance); `rung36_jcon_recogn` rc=124 hang eliminated (rc=0, content still FAIL — scan-family root cause). New acceptance rung `rung03_suspend_return` added (suspend-then-return poison, confirmed PASS). All smokes green: Icon 14/14 m3+m4, SN4 7/7, Raku 283/283. All gates green: icn_no_stack, icn_one_reg_frame, emit_no_lang. Prolog clause 4/5 pre-existing. **Grant repair landed:** `IR_PROC_GEN/IR_CALL_VALUE` zls_grant returned -1+n (bug exposed by 0-operand generator `return` test) → fixed to 2+n; offset arithmetic `off*j` → `off+16*j` aligned to emitter formula. **Residue:** recogn content (scan-family root: disjunction fail-edge at emit.cpp ~L887-904); C-window value-called generators remain pthread; cross-suspend scan-sync unfenced. **FZ-E scan root** (from prior cursor, still open): disjunction fail-edge wired to arm-B β instead of α in emit.cpp IR_SCAN_SEQUENCE case (~L887-904, L1101); recogn/scan/scan1/scan2/string share this. **Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6

## ⌚ WATERMARK 2026-07-15 s3 (Claude Sonnet 4.6 · SCRIP `b24c63c7` · corpus unchanged) — orientation only; 239/15/35 independently verified; refs/ symlinks established from uploaded zips

**Scope:** Pure orientation session. No code changes. Built scrip from HEAD `b24c63c7` (6 commits ahead of s2 cursor — all Raku/Pascal, zero Icon). Independently re-ran full Icon suite: **239/15/35 confirmed byte-identical to cursor**. All 4 Icon gates green, smoke 14/14 m3+m4. Set up `refs/jcon-master` + `refs/icon-master` symlinks from user-uploaded zip archives (RULES.md CONSULT CANONICAL SOURCES setup). Read `ir_a_Scan` from canonical `irgen.icn` as first look at Cluster B/scan territory. Next session: begin FAIL-ZERO work at first open rung (FZ-B1 or FZ-B2 per Lon direction). **Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6

## ⌚ WATERMARK 2026-07-15 s2 (Claude Sonnet 4.6 · SCRIP `50249fd5` · corpus unchanged) — control-in-value fix landed; cluster diagnoses corrected; 239/15/35 maintained

**Scope:** Full session-setup baseline confirmed (239/15/35 byte-identical to cursor). Investigated all 15 FAILs; corrected cluster descriptions — every cursor claim was measured against a minimal repro, not trusted from prose. **LANDED `50249fd5` — control-in-value fix:** `while`/`until`/`repeat`/`every` were setting `*res` to a control `IR_GOTO` and routing loop-exit to γ (success). Icon semantics: these produce no value and fail as expressions. Fixed all four in `lower_icon.c`: route exit to ω, `*res = NULL`. Safe for statement context (succ==fail in `lower_proc_body`). `image(while write(move(1)))` now correctly reaches `| "none"`. `scan` advanced past its TE-4 bomb. **Verified:** 239/15/35 zero-regression, all 4 Icon gates PASS, smoke 14/14 m3+m4, Prolog 5/5, m4 compiles. **Diagnoses:** FZ-B1 `var` blocked on pointer-hole arch (Lon). FZ-B2 `scan` new blocker: bare scan functions outside `s ? …` read uninit Σ/δ/Δ. FZ-D1/D2 `htprep`/`prepro`: Icon preprocessor (unbuilt). FZ-E cluster: generator-argument-to-procedure, distinct second root cause. **Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6

## ⌚ WATERMARK 2026-07-15 (Claude Opus 4.8 · SCRIP `e18b038a` · corpus unchanged) — ZERO-FAILURE MANDATE opened; FZ-A1 landed (238→239/15/35); goal file pruned

**Scope:** fresh full Icon suite run corrected the cursor (claimed 239/15, reality was 238/16 — `rung13_alt_alt_cross_arg_sideeffect` regression, HEAD newer than s5). Authored FAIL-ZERO (16 steps, 5 clusters) + XFAIL-ZERO (35 markers) ladders. **FZ-A1 LANDED (SCRIP `c822995a`→`e18b038a`):** `x86_parse` eager pre-parse (`x86_asm.h:1057`) aborted on bracket-bearing string literals (`.string`/comment payloads containing `[...]`, e.g. `write("[x]")`); abort replaced with the benign `XK_SYM` fallthrough the fn already uses. rung13 PASS; kwds/scan1 crash lifted → wrong-output (Cluster E). Zero regressions, all Icon gates green, m3+m4. Then pruned this goal file (watermarks → last 3; stale scan-design cursor bullets removed).

## ⛔ FACT RULE — LANGUAGE-BLIND BB/XA TEMPLATES (Lon, 2026-06-03)
No language-specific logic in any BB/XA template: templates dispatch on IR shape + representation flags only. FORBIDDEN inside `src/emitter/{BB,XA}_templates/`: `IR_LANG_*`/`LANG_*`/`is_<lang>` guards, language-named template fns/files/dispatch arms, hardcoded language-builtin names. Per-language behavior lives in the runtime (by-name dispatch) or in LOWER (different IR shape → its own BB) — never in a template arm. Inventory: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md`; fix ladder LB-* in GOAL-PASCAL-BB.md. COMPLETION TEST: the audit's Tier-1 grep over both template dirs == 0.

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
FORM:** a box's leading `α:` label (`s_1asm(std::string(_.lbl_α)+":")`) and comments (`s_comment(...)`) exist only
in the GAS arm, so `IF(MEDIUM_TEXT, <comment-or-label>)` with NO matching `IF(MEDIUM_BINARY, <bytes>)` is fine; an
`IF(MEDIUM_TEXT,<gas-instruction>) + IF(MEDIUM_BINARY,<bytes>)` PAIR is the violation. Non-x86 platform arms
(JVM/JS/NET/WASM) are out of scope (X86 ONLY for now) and keep their `s_*asm` text.


**CORRECTION RECORD (Lon 2026-06-06):** RULES.md TEMPLATE-ONLY EMISSION is now corrected to MATCH this rule; its former
"duplicate the byte-producing code into each template file" clause (515aa7d6, 2026-05-28) is DEAD — it predated the
2026-06-02 directive and said the opposite. Restated plainly: ZERO BINARY emission anywhere in a `bb_*.cpp` — not in the
top-level `*_str`, not in any helper it calls (a static helper in the template file is INSIDE the fence; relocating bytes
into helpers changes nothing). `x86()` internals (`x86_asm.h`) are the ONLY place BINARY and TEXT are emitted, side-by-side.

**ENFORCEMENT:** gate `scripts/test_gate_template_medium_invisible.sh` (comments stripped): in `BB_templates/*.cpp`,
the raw-byte producers + `IF(MEDIUM_BINARY`/`IF(MEDIUM_MACRO_DEF` count == 0 (informational WIP baseline; `--strict`
enforces zero). **COMPLETION TEST:** (a) zero raw-byte producers and zero `IF(MEDIUM_BINARY,…)`/`IF(MEDIUM_MACRO_DEF,…)`
in any `BB_templates/*.cpp`; (b) every instruction emitted via an `x86(...)` call; (c) the gate green under `--strict`
and in the Session-Setup gate list; (d) this FACT RULE body byte-identical across the four GOAL-*-BB files.

**THREE FACES OF ONE END STATE.** This rule, the `bb_bin_t`-ABOLISHED rule above, and the no-`pBB`/`_.node` rule are
three faces of ONE converted box: pure `x86()` concatenation reading only `_`. A box that still hand-encodes bytes
ALSO still carries `bb_bin_t` and ALSO branches on the medium; converting it to `x86()` clears all three at once. The
three gates therefore reach zero TOGETHER, box-by-box, as the revamp completes — the prison is escaped only by
finishing the conversion.

## ⛔ NO C BYRD-BOX FUNCTIONS — A BOX IS ENTERED BY JUMPING TO ITS α/β LABELS, NEVER A `(ζ, int entry)` C CALL (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**There is NO such thing as a C byrd-box function. The "brokered BB" concept is ABOLISHED.** A byrd box is
EMITTED machine code. It has exactly TWO entry points, and they are **LABELS** — α (fresh entry) and β
(resume). Control reaches a box by **JUMPING to one of those labels**. A box is NEVER a C function, is NEVER
reached by a C call, and NEVER takes an integer `entry` argument to select α vs β. The C signature
`DESCR_t NAME(void *ζ, int entry)` — a ζ-state pointer plus an `int entry` α/β selector — is **FORBIDDEN**.
It was the discredited brokered-BB calling convention (an "entry kludge"); it is gone. The ONLY driver is the
**mode-2 BB-graph interpreter** (`bb_exec.c`), which walks the IR graph directly and IS the broker/driver;
**modes 3 and 4 are native code in which boxes thread control by jumping between α/β labels** (RULES X86-64
register / subject-model convention) — never through a function pointer plus an `entry` integer. There is no
`bb_broker` driver and no `(ζ, int entry)` box anywhere.

**HISTORY — READ THIS, because it is why the rule now exists in this strongest form.** This prohibition has
stood for **AT LEAST TWO MONTHS**. Lon ordered these C `(ζ, int entry)` byrd boxes DELETED at least **THREE
separate times**, and each time a session either declined, re-introduced them, or held/reverted the deletion
"to keep the build green." A prior plain rule (RULES.md "NO C BYRD-BOX FUNCTIONS") did **not** hold. They
were finally deleted **2026-06-01** — the `pl_*_fn` family (all of `pl_broker.c`), `gen_bb_dcg`,
`gen_bb_oneshot`, `resolve_bb_dcg`, `bb_deferred_var`/`_exported`, `fail_box`, the dead `bb_cap`/`bb_atp`
declarations, **and the `bb_broker` driver itself** (`bb_broker.c`). **KEEPING THE BUILD GREEN IS NOT A
LICENSE TO PRESERVE A FORBIDDEN BOX.** When this signature and a green build conflict, the **signature
loses**: delete the box and tear out its callers (the brokered execution path — Prolog `--run`, brokered
pattern scan, brokered generators — is removed, not preserved). A broken build pending the caller teardown is
acceptable; a surviving `(ζ, int entry)` box is not.

**COMPLETION TEST:** (a) `grep -rnE 'DESCR_t[[:space:]]+[A-Za-z_]+[[:space:]]*\([[:space:]]*void[[:space:]]*\*[[:space:]]*[a-z]*[[:space:]]*,[[:space:]]*int[[:space:]]+entry' src/ --include=*.c --include=*.cpp --include=*.h | grep -v typedef` == 0 (no C byrd-box definition or declaration with the `(ζ, int entry)` signature); (b) no `bb_broker` driver function exists; (c) every emitted box is entered by a jump to an α or β label, never a C call with an `entry` int; (d) this FACT RULE body is byte-identical across the five GOAL-*-BB files.

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
under a different name (`*_vstack[]`, `value_stack`, `g_estack`, a hand-rolled `WamWord[]`/`DESCR_t[]`
push/pop arena used to pass values between boxes, etc.). FORBIDDEN to (re)introduce: a global/static array
whose purpose is to push a box's value and pop it in a consumer; `rt_push_*`/`rt_pop_*`/`vstack_*` value
traffic; any `*_push`/`*_pop` helper that moves an *intermediate* value between boxes. (KEEP, NOT a value
stack: the Prolog trail `g_resolve_trail`/`rt_pl_trail_*` — a binding-undo ledger; the choice-point ledger
`g_resolve_bfr`/`resolve_choice` — the irreducible cross-node resume spine; the C call stack used for
genuine recursion; an ARBNO-style explicit indexed per-activation frame array. None of these is a value
stack.) The residual `vstack_*`/`rt_vstack_ops_t` SCAFFOLDING left in `src/runtime/rt/rt.c` is dead/aborting
(`g_ops` only ever points at `g_default_ops`, whose push/pop/peek `abort()`); it is being removed rung by
rung (the VSX ladder) and must NOT be wired up to anything — adding a real backing store to it = creating a
value stack = a violation.

**GUARD:** `scripts/test_gate_no_vstack.sh` (informational baseline now; flips to a HARD `--strict`
zero-check at VSX-8). It greps (comments stripped) ACROSS ALL `src/` for `g_vstack`/`vstack_push`/
`vstack_pop`/`vstack_peek`/`rt_vstack_*`. The `g_vstack` token is already at ZERO and must STAY at zero;
the rest trend to zero as the scaffolding is deleted. Any session that makes the `g_vstack` count non-zero,
or that adds a new value-stack array under any name, has violated this rule. **COMPLETION TEST:** (a)
`grep -rn 'g_vstack' src/` == 0 (code AND comments); (b) no new global/static push/pop value arena exists;
(c) `scripts/test_gate_no_vstack.sh` `g_vstack` line reads 0; (d) the FACT RULE body is byte-identical
across all five GOAL-*-BB files.

> **⚠️ `wire_seq`/`wire_alt` (lower.c)** were strictly generalized 2026-05-31 (fail-chain walks past bounded
> elements; alt arms lower right-to-left), re-proven non-regressive for Icon — relevant only if you edit them.

## ⛔ SHARED-LOWERER ONE-FILE CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The AST→IR lowerer's SHARED SPINE is **ONE file** — `src/lower/lower.c` — with **ONE entry** (`lower2`, role-seeded via `lower2_{value,pattern,goal}_entry`) and **ONE big switch over the shared `tree_e`** for the co-located languages. **AMENDED (Lon 2026-06-04): the shared IR graph is the LANGUAGE-INDEPENDENT contract — LOWER splits per language.** Prolog's goal-role family now lives in `src/lower/lower_prolog.c` (`d6d93c6`; shared helpers de-static'd into `lower_internal.h`); remaining languages stay co-located in `lower.c` until Lon splits them out. The discipline below keeps concurrent sessions **conflict-free and mutually beneficial**:

1. **ONE CASE PER KIND.** Each `TT_*` is at most ONE `case` label per role switch. If your language needs a kind with no case yet → ADD the case. If the case exists → ADD YOUR ARM to it. **NEVER duplicate the label.** (Win-win: SNOBOL4 adding `case TT_ASSIGN` hands Icon/Prolog a ready slot.)

2. **LANGUAGE VARIATION LIVES INSIDE THE CASE — NEVER A PER-LANGUAGE FORK.** When a kind behaves differently per language, branch on `cx.lang` (or role) WITHIN the one case (`switch (cx.lang) { case IR_LANG_SNO: …; case IR_LANG_PL: …; }`, or if/else). One kind → one case → language arms inside. A language graduates to its OWN `lower_<lang>.c` ONLY by Lon's directive (Prolog: 2026-06-04), taking its whole role-family with it — never an ad-hoc fork.

3. **EDIT ONLY YOUR OWN LANGUAGE'S ARM.** A session may ADD or MODIFY the `cx.lang` arm for its OWN language inside any case. It must **NEVER modify, reorder, or delete another language's arm.** A language owning its own `lower_<lang>.c` edits ONLY that file (plus lockstep scaffolding per rule 5) and never a peer's. This is what makes concurrent sessions' diffs non-overlapping → git auto-merges with **zero conflicts**.

4. **A MISSING LANGUAGE ARM FALLS LOUD, NEVER SILENT.** Inside a case, a language with no arm yet routes to `lower_unhandled` (loud stderr + NULL) — never a silent or wrong default. A half-built arm fails LOUDLY so it can never corrupt a peer's proven path.

5. **SHARED SCAFFOLDING IS ADDITIVE; SIGNATURE/SEMANTIC CHANGES ARE LOCKSTEP.** The cursor (`lcx_t`), the port primitives (`nalloc`/`set_succ_fail`/`ret`/`emit_leaf`), and the match-collect library (`tm`/`tm_g`) are SHARED (declared in `lower_internal.h`, defined in `lower.c`). ADDING a helper or a case label is free (no conflict). CHANGING the signature/semantics of an existing shared helper or of `lcx_t` affects all three cats → it MUST update all three GOAL files' FACT RULE in the SAME commit and re-prove all three.

6. **THE TOPOLOGY PROOF GATE IS THE SHARED GREEN SIGNAL.** `scripts/prove_lower2.sh` must stay green before every commit (it compiles `lower.c` + `lower_prolog.c` + the harness). Each cat's proof cases are ADDITIVE (append your own; never delete a peer's). Green = your arm wired right AND you didn't disturb a peer.

**COMPLETION TEST:** (a) no duplicated `case TT_` label within any one switch in `lower.c` (nor within any per-language lowerer file); (b) every case's language branches end in a real arm or `lower_unhandled` (no silent default); (c) the FACT RULE body is byte-identical across the three GOAL files (`awk '/SHARED-LOWERER ONE-FILE/{p=1} p{print} /prove_lower2.sh green/{if(p)exit}'` md5 matches — first-match, not greedy `sed`); (d) `scripts/prove_lower2.sh` green.

## ⛔ TEMPLATE-ONLY EMISSION — ONE-DISPATCH CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The unified IR→x86 emitter is **ONE dispatch** — `src/emitter/emit_core.c`'s `switch (nd->t)` over the shared `IR_e` — fanning out to **per-box template functions** under `src/emitter/{BB,SM,XA}_templates/`. Every byte of emitted machine code lives INSIDE a template fn reached ONLY via this dispatch (RULES.md TEMPLATE-ONLY). SNOBOL4, Icon, and Prolog fill emitter boxes CONCURRENTLY in SEPARATE sessions, all writing into this one dispatch + this one template tree. The discipline below makes the three sessions **conflict-free and mutually beneficial** (one session's dispatch case + template file is the next session's ready slot), exactly mirroring the SHARED-LOWERER rule:

1. **ONE DISPATCH CASE PER IR KIND.** Each `IR_*` is at most ONE `case` label in `emit_core.c`. If your language's kind has no case → ADD it (one line: `case IR_FOO: bb_foo(nd); return 0;`). If it exists → it already calls the right template; do not duplicate. **NEVER duplicate the label.** Append new cases at the END of the language's contiguous block (SNOBOL `IR_PAT_*` block, Prolog `IR_GOAL/ARITH/BUILTIN/LOGICVAR/ATOM/STRUCT/UNIFY/CUT/DISJ/GCONJ` block, Icon `IR_EVERY/ALT/LIMIT/SCAN/TO/…` block) so the three sessions' inserts land in different hunks → git auto-merges.

2. **ONE TEMPLATE FILE PER BOX — NEVER A SHARED MEGA-FILE.** Each box's bytes live in its OWN `.cpp` (e.g. `bb_pat_len.cpp`, `bb_unify.cpp`, `bb_every.cpp`). A session creating a new box CREATES a new file; it never appends a second box's body into a peer's file. Per-box files = per-session non-overlapping edits. Duplicating a byte pattern INTO each template is REQUIRED (duplication is the point — RULES.md); never factor shared bytes into a common emitter helper that two languages edit.

3. **EDIT ONLY YOUR OWN LANGUAGE'S BOXES.** A session may ADD or MODIFY template files for ITS OWN language's kinds and the ONE dispatch line that reaches each. It must **NEVER modify another language's template body or dispatch line.** (SNOBOL touches `bb_pat_*`; Prolog touches `bb_goal/arith/unify/cut/disj/conj/atom/struct/logicvar`; Icon touches `bb_every/alt/limit/scan/to/iterate/…`.)

4. **BYTES LIVE ONLY IN TEMPLATES — A MISSING BOX FALLS LOUD.** FORBIDDEN outside a template fn: `seg_byte(SEG_CODE`, `SL_B(`, `sl_emit_one`, `emit_standard_blob`, and the raw byte-producers `bytes()/u8()/u32le()/u64le()` (allowed only in `bomb_bytes`/`bb_emit_asm_result` of `emit_str.cpp`). A kind with no template yet must hit the dispatch's loud default (assert/abort), never silently emit nothing or fall through. `scripts/util_template_purity_audit.sh` is the standing guard.

5. **THE SHARED SOURCE LIST IS ADDITIVE; BUILD/ABI CHANGES ARE LOCKSTEP.** The Makefile `RT_PIC_SRCS` template list is APPEND-ONLY — add your new `.cpp` on its own line at the end of the language's group (one line = one hunk, no conflict). ADDING a template + its source line + its dispatch case is free. CHANGING a shared emitter primitive (`emit_core` dispatch signature, `BB_t`/`IR_t` layout, the `operand_aux` sidecar API, register-frame ABI) affects all three → it MUST update all three GOAL files' FACT RULE in the SAME commit and re-prove all three.

6. **THE EMITTER GATES ARE THE SHARED GREEN SIGNAL.** Before every commit: `scripts/util_template_purity_audit.sh` (no bytes outside templates), `scripts/test_gate_em_template_byte_identity.sh` + `scripts/test_gate_em_template_matrix.sh` (templates emit the sanctioned bytes), and the per-language no-stack/one-reg gates (`test_gate_icn_no_stack.sh`, `test_gate_icn_one_reg_frame.sh`) must stay green. Green = your box emits right AND you didn't disturb a peer.

**COMPLETION TEST:** (a) no duplicated `case IR_` label in `emit_core.c` (`grep -oE 'case IR_[A-Z_]+' src/emitter/emit_core.c | sort | uniq -d` empty); (b) every `IR_*` kind a language emits has exactly one dispatch case reaching one template fn, unmatched kinds hit the loud default; (c) zero forbidden byte-emitters outside templates (`util_template_purity_audit.sh` clean); (d) the FACT RULE body is byte-identical across the three GOAL files (`awk '/TEMPLATE-ONLY EMISSION — ONE-DISPATCH/{p=1} p{print} /util_template_purity_audit.sh clean/{if(p)exit}'` md5 matches); (e) the emitter gates above are green.

## ⛔ NO DUPLICATED LOGIC — WRITE EACH PIECE OF LOGIC ONCE (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

**This is a LOGIC problem, not a formatting problem.** (Lon, 2026-06-01.) The template tree is BAD CODE: the same logic is written over and over. `bb_builtin.cpp`
is 2,427 lines because of duplication, not because the work is big. Fix the duplication; the line count
collapses on its own.

**THE ONE LAW: each piece of logic is written ONCE.** A box does PORT work (α/β/γ/ω wiring). The runtime does
VALUE work (build a term, compare, arithmetic, concat). When a box reimplements VALUE work inline, you get
duplication — and duplication is the disease in every form below.

**DUP FORM 1 — THE SAME ALGORITHM IN TWO MEDIA (worst, the bulk of the bloat).** `emit_build_compound_term`
(92 lines, emits GAS text) and `emit_build_compound_term_bin` (94 lines, emits raw bytes) are the SAME
post-order Term-builder written TWICE. A bug must be fixed in both or they drift. THE FIX IS NOT TO MERGE THE
TWO WALKERS — it is to DELETE BOTH. Building a Term is a RUNTIME job; `rt_pl_compound_build_n` and
`rt_pl_node_to_term` already do it. The box marshals operand slots into registers and `call`s the helper.
Once it is one `rt_*` call there is NOTHING to duplicate: TEXT emits `call foo@PLT`, BINARY emits
`movabs rax,&foo; call rax` — two trivial encodings of ONE logical call, which is the sanctioned per-medium
difference (NOT duplicated logic). ~18 builtin families currently each call BOTH walkers; killing the walkers
sheds >1,000 lines.

**DUP FORM 2 — EMIT-TIME LOGIC THAT IS A RUNTIME JOB.** Root cause of FORM 1. Any time a template grows a
recursive walker, an arithmetic evaluator, a comparator, a term constructor — that is VALUE work in the wrong
place. It belongs behind ONE `rt_*` call. (Guard, GOAL-BB-TEMPLATE-LADDER invariant 9: never add an
`rt_*_exec` that does α/β/γ/ω PORT logic — that is a C byrd box. The split is clean: RT = value, BOX = ports.
If you are emitting more than "marshal args, call helper, wire the 4 ports," you are duplicating runtime logic
into the emitter.)

**DUP FORM 3 — AN OPERAND BOX REIMPLEMENTED INSIDE ITS CONSUMER (fusion).** `bb_binop` reads
`pBB->α->t == IR_LIT_I` and seals the operand's VALUE (`pBB->α->ival`) in its own blob — reimplementing what
`bb_lit_scalar` already does (put a literal where a consumer can read it). Two pieces of code, one job. The
consumer must READ the operand's slot (`bb_slot_get(pBB->α)`); the operand's own box fills it. DELETE the
operand-kind arm. (PREREQ, proven 2026-06-01: deleting GZ-3/GZ-4 today breaks `write(2+3)` because the lowerer
does not yet chain literal operands as producer boxes in that shape — so the de-fuse step is first a LOWERER
fix that makes both operands producers, THEN the deletion.) Any `pBB->α->ival/sval/dval` or `->α->t==IR_LIT_*`
read inside a consumer box = fusion = duplicated operand logic.

**DUP FORM 4 — N DIFFERENT BOXES IN ONE FILE (cram).** `bb_binop.cpp` held 7 unrelated four-port shapes
selected by `op`/operand-kind/`g_*_flat_chain`. Each distinct shape is its own box; a `_str()` returning
several different complete four-port byte sequences is N boxes in one filename. This is the LEAST harmful dup
(it is co-location, not copied algorithm) but it hides the others. De-cram by splitting distinct shapes behind
a thin router (`bb_foo.cpp` keeps the `extern "C" void bb_foo(IR_t*)` so `emit_core.c` is untouched; each shape
is `bb_foo_<shape>_str(...)` returning its bytes or `""`; router calls each in order). Worked example DONE:
`bb_binop_*.cpp` + 38-line `bb_binop.cpp`.

**NOT DUPLICATION — DO NOT "FIX" THESE.** (a) The same byte pattern hand-copied INTO each per-box template is
REQUIRED (RULES.md — duplication of bytes across boxes is the point; never factor into a shared emitter helper
two languages edit). (b) Per-file op-classifier tables (`gen_is_numrel`, `gen_rel_to_tt`) copied per file —
acceptable, per-file, no shared edit. (c) Boxes 95%+ identical SHARE one file parameterized by an immediate /
opcode / register (`bb_lit_scalar` groups IR_LIT_I/S/F/NUL; `bb_binop_arith` groups ADD/SUB/MUL/DIV/MOD) —
grouping near-identical SHAPES is correct; splitting them is over-splitting. (d) The two ARMS of one box
(`IF(BINARY)`/`IF(TEXT)`) are two encodings of one logic — NOT duplication. The line is always: copied
*algorithm* = bad; copied *bytes/encoding* of one logic = fine.

**THE TEST:** could a bug in this code require fixing the same logic in two places? If yes → duplication →
collapse it (delete the emit-time copy in favor of one `rt_*` call; delete the fused operand arm in favor of
the slot read; delete the second-medium walker).

**COMPLETION TEST (per file):** (a) no algorithm (walker / evaluator / comparator / term-builder) appears in
both a TEXT arm and a BINARY arm — value work is ONE `rt_*` call; (b) no emit-time reimplementation of runtime
value work; (c) no operand-kind read (`pBB->α->ival/sval/dval`, `->α->t==IR_LIT_*`) inside a consumer box;
(d) one four-port shape per `_str()` (or a pure router); (e) the FACT RULE body is byte-identical across all
four GOAL files.

## ⛔ X86-64 REGISTER / SUBJECT-MODEL CONVENTION (FACT — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

Locked callee-saved layout the three concurrent BB sessions MUST share (canonical origin: GOAL-ICON-BB "Subject model — four names, zero redundancy"; casing inherited from the snobol4jvm Clojure SNOBOL4). **Casing carries meaning: UPPERCASE = the fixed whole/bound; lowercase = the moving position.**

| Reg | Class | Name | Role |
|-----|-------|------|------|
| **R13** | callee-saved | **Σ** (UPPER) | subject BASE ptr — the fixed whole string |
| **R14** | callee-saved | **δ** (lower) | CURSOR — the moving scan position |
| **R15** | callee-saved | **Δ** (UPPER) | subject LENGTH/END — the fixed bound |
| (scratch) | — | **σ** (lower) | TRANSIENT current-char ptr `Σ+δ`, computed at deref, NOT durable |
| **R12** | callee-saved | **ζ** (zeta) | BB-local RW FRAME base; every box-local is `[r12+off]` (RATIFIED 2026-05-30) |
| **R10** | caller-saved | (retired) | RW box-locals → `[r12+off]` (ζ frame); RO → `[rip+disp]`. r10 RETIRED (R10-OUT) |
| **rbx** | callee-saved | — | FREE / callee-saved scratch (preserved across the box chain) |
| **rbp** | callee-saved | — | DEFINE'd / brokered function frame ptr when active (`push rbp;mov rbp,rsp`); else callee-saved scratch |

**DUAL ROLE — R13/R14/R15 ALSO CARRY THE PROLOG TRAIL (RATIFIED Lon 2026-06-13).** Prolog has no subject string, so the subject trio Σ/δ/Δ is idle and instead carries the TRAIL — Prolog's one main attraction (its single shared binding-undo spine) — in the SAME base/cursor/end shape, casing preserved (UPPER = fixed, lower = moving):

| Reg | subject (SNOBOL4/Icon) | Prolog TRAIL — `Trail{stack;top;capacity}` |
|-----|------------------------|---------------------------------------------|
| **R13 = Σ** (UPPER, fixed) | subject BASE ptr | trail `stack` — base of the `Term*` array |
| **R14 = δ** (lower, moving) | CURSOR | trail `top` — the mark; "push" = ++, "unwind" = set back |
| **R15 = Δ** (UPPER, fixed) | subject LENGTH/END | trail `capacity` — the fixed bound |

The physical registers are SHARED — never live in two languages at once. A cross-language BB jump save/restores the trio (DEFERRED — its own later rung; not yet wired). The trail in registers replaces the `g_resolve_trail` symbol load with pure register traffic. **RBP stays RESERVED** (its brokered-frame role is dead under NO C BYRD-BOX; held for a future use TBD — Lon). This DUAL-ROLE addition is byte-identical across all three GOAL files; the subject rows above remain each file's own.

**γ-success return packing:** `rax = σ ptr`, `rdx = δ int` (spec_t).

**RETIREMENT (all three sessions must honor):** the old **`Ω`** (omega — mode-2 `refs/bb/test_*.c` oracle) and **`Σlen`** (mode-3/4 `bb_pat_*.cpp` templates) are ONE quantity under two names → **both fold into `Δ`**; always moved in lockstep. Rename sweep: `Δ(old cursor)→δ`, `Ω→Δ`, `Σlen→Δ`. Substring nesting is held on the C stack (`save_Σ`/`save_Σlen`), so ONE length register suffices. **Pre-flight gate before deleting a name:** grep that no path ever sets `Σlen ≠ Ω`. Changing any assignment in this table is LOCKSTEP — update all three GOAL files in the SAME commit (mirrors the SHARED-LOWERER / EMITTER FACT RULES).


## ⛔⛔ GROUND ZERO 3 — STACKLESS (Reset 2026-05-30) ⛔⛔

Values live in flat per-box slots at emit-time offsets; consumer reads producer's slots directly. Unbounded backtrack = per-box arena indexed by depth, never push/pop. Inter-box transitions are `jmp rel32`. **References:** `test_icon.c` (flat goto target) · `test_sno_1/2/3.c`.

**GATE:** `grep -rnoE 'rt_(push|pop)_[a-z_]+' src/emitter/BB_templates/ src/emitter/emit_bb.c | grep -v _pl_ | wc -l` == 0.

### ⛔ ALWAYS TEST BOTH NATIVE MODES (m2/--run DELETED)

Every test runs `--run`/`--compile` on the SAME source. Done = m3+m4 PASS or LOUDLY EXCISE. HARNESS: `scripts/test_icon_rung_suite.sh [--rung R] [--mode all|run|compile]`. Stubbed kind → `[SMX] EXCISED` (exit 0). m4 needs `make libscrip_rt` + gcc.

### Rung ladder

- [x] **ICN-STORAGE** — GST-1/2 + GVA-1/2 + LVA-1 LANDED (globals `[rbx+k*16]` mode-4; locals locked ζ-frame, gate `test_gate_icn_local_no_nv.sh`). Open remainder: **GVA-M3** (mode-3 in-process globals still NV; optional) → `GOAL-ICN-GVA-M3.md`. Analysis: `ICON-AUDIT-2026-06-24.md` §C. Unblocks `initial`/`static` (the `.bss __gva` arena is their persistent-writable-static region).
- [ ] **GZ-DEFER** — EVAL / CODE / `*P` deferred patterns.
- [ ] **GZ-11+** — `not`/`size`/`nonnull` `bb_unop` · relop remainder · generator-operand binops (Fig-1) · `rt_call_builtin` · lists/tables/records/csets/sort.

## ⛔ PER-BOX LOCAL STORAGE — ALL STATE LIVES INSIDE THE BOXES (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

**ONLY local BB allocation variables are used; NOTHING is stored outside the boxes.** Every value a
SNOBOL4 (or Icon / Prolog) BB graph computes or holds at run time lives in storage that belongs to a
box — never in any external/global side channel. There is NO AG ring at run time (the ring is the
MODE-2 ORACLE's idiom ONLY — `bb_exec_once`), NO value stack (`g_vstack`/`rt_push_*`/`rt_pop_*`), and
intermediate values are NOT threaded through the global name table (`NV_GET`/`NV_SET`) — name-table
stores are reserved for genuine SNOBOL4 *variables* on assignment, not for passing a value from a
producer box to its consumer.

**Each box owns exactly two kinds of local allocation, both INSIDE the box (not outside):**
- **READ-ONLY data (RO)** — compile-time constants for that box (literal int/real/string/cset values,
  the box's name string, fixed bounds, op codes). Placed in the SEALED segment adjacent to the box's
  BLOB and reached by IP-relative addressing (`lea/mov reg,[rip+disp]`, `disp` an emit-time constant in
  the BINARY arm; a `.L`-label in the TEXT arm). RO data is NEVER threaded on a stack and NEVER reached
  by an absolute `movabs … &slot` immediate.
- **READ-WRITE data (RW)** — the box's mutable runtime storage (its result value/DESCR slot, counters,
  cursors, per-box backtrack arenas, generator state). Lives in the per-sequence ONE-REGISTER FRAME and
  is reached register-relative `[ζ=r12 + emit_time_offset]`. A consumer reads a producer box's result by
  that producer's frame offset (`bb_slot_get`/`bb_slot_alloc`); a SNOBOL4/Icon *variable* is ONE
  name-keyed frame slot (`bb_varslot`) shared by its IR_ASSIGN(name) writer and IR_VAR(name) readers.

So every box value reference is exactly one of: **(RO)** `[rip+disp]` into sealed data, or **(RW)**
`[ζ+off]` into the per-sequence frame. Never a ring, never a value stack, never a name-table round-trip
for an intermediate. This is the `test_sno_1.c` / `test_icon.c` named-slot law the GZ-7 Icon and PLG-8
Prolog siblings already follow (`febef10`: `x:=42;write(x)` → m2==m3==m4, all slot-based, no ring).

**COMPLETION TEST (per box family):** (a) no `bb_exec_once`/AG-ring read or write on the mode-3/4 run
path; (b) no `g_vstack`/`rt_push_*`/`rt_pop_*`; (c) no `NV_GET`/`NV_SET` used to carry an *intermediate*
producer→consumer value (only true variable assignment); (d) every box-local read is `[rip+disp]` (RO)
or `[ζ+off]` (RW) — no `movabs … &pBB->slot` absolute slot address; (e) mode-3 BINARY arm and mode-4
TEXT arm of the SAME box do the SAME processing (the only diff is BINARY-bytes vs GAS-text).

---

## Premise

Icon IS a Byrd-Box port-graph; every construct is a box; no SM, no value stack. Modes 3/4: `push r12; mov r12,rdi; jmp .Lroot_α`; boxes in `bb_pool`/linked binary; transitions are `jmp rel32` — no call/ret/dispatch/broker/walker/push-pop. Target shape: `test_icon.c` (flat goto, named slots, three-column LABEL/ACTION/GOTO).

## ⛔ GOAL RULE (Icon SM streams)

**ZERO SM opcodes for an Icon program.** Completion: `./scrip --dump-sm prog.icn` → `; SM_sequence_t  count=0`.

## ⛔ ICON SEMICOLON-REQUIRED — NO NEWLINE PROCESSING, EVER (FACT RULE — Icon, Lon directive 2026-06-23)

**SCRIP Icon REQUIRES an explicit `;` between bare statements. The Icon front-end does ABSOLUTELY NO
newline processing — a newline is plain whitespace and NEVER becomes a statement separator.** The
canonical `icont` "optional semicolon" mechanism (newline → `;` insertion when the previous token is an
Ender and the next is a Beginner — `refs/icon-master/src/common/tokens.txt`, `src/h/lexdef.h`) is
**FORBIDDEN in this codebase.** SCRIP is its own dialect: statements are `;`-terminated, full stop. A
program with bare statements separated only by newlines is a PARSE ERROR, by design, and that is correct.

**WHY THIS RULE EXISTS IN ITS PRISON FORM.** A session ADDED newline-to-`;` insertion to the Icon lexer
(the Beginner/Ender table + newline-crossing `TK_SEMICOL` synthesis) — exactly the thing forbidden here —
to make canonical newline-style benchmark sources parse. It was reverted byte-for-byte, but a plain rule
("Icon requires semicolons") did not prevent it. The rule now has STRUCTURAL + BEHAVIORAL ENFORCEMENT so
it cannot recur. Canonical newline-style sources are adapted by ADDING `;` to the SOURCE (a corpus matter),
NEVER by teaching the compiler newline processing. KEEPING A BENCHMARK PARSING IS NOT A LICENSE to insert
newline handling — when a benchmark and this rule conflict, the **rule wins**: the source gets semicolons.

**FORBIDDEN inside `src/parser/icon/`:** any Beginner/Ender token classification used for separator
insertion (`tok_is_beginner`/`tok_is_ender`/`Beginner`/`Ender` flags), any newline-crossing detection that
synthesizes a separator (`prev_line` comparison driving a `TK_SEMICOL`), any one-token buffering whose
purpose is to inject a separator (`have_pending` + synthetic `TK_SEMICOL`), and minting `TK_SEMICOL` from
anything other than the literal `;` character. The lexer treats `'\n'` as whitespace (the `isspace` path in
`skip_ws`) and emits `TK_SEMICOL` ONLY from `case ';'`.

**ENFORCEMENT — THE PRISON (`scripts/test_gate_icn_semicolon_required.sh`), three independent locks, ALL
must hold:** LOCK 1 (negative grep, comments stripped) — zero newline-insertion machinery in
`src/parser/icon/*.c|*.h`. LOCK 2 (mint-site) — exactly ONE `make_tok(TK_SEMICOL,...)` site in
`icon_lex.c` (the `';'` case). LOCK 3 (behavioral canary, identifier-name-independent) — a two-bare-
statement program separated by a NEWLINE MUST be rejected with a parse error, and the same program with an
explicit `;` MUST parse. Reintroducing insertion must defeat all three; LOCK 3 pins the actual behavior so
a rename cannot evade it. **COMPLETION TEST:** (a) `scripts/test_gate_icn_semicolon_required.sh` exits 0;
(b) it is in the Session-Setup gate list; (c) the newline canary parse-errors and the semicolon canary
parses; (d) `src/parser/icon/icon_lex.c` mints `TK_SEMICOL` only from the literal `;`.

## ⛔ CONSULT CANONICAL SOURCES (JCON + Icon)

Every port-topology / resume-wiring / builtin-semantics question: read canonical FIRST — `refs/jcon-master/tran/irgen.icn` and `refs/icon-master/src/runtime/*.r` (`fstranl.r`, `ocomp.r`, `fscan.r`). The m2 oracle is a transcription; canonical wins. Extract uploaded zips into `refs/` at session start if absent.

## Per-rung gate

```bash
bash scripts/build_scrip.sh
./scrip --run     /tmp/rung_NN.icn  > out_m3.txt
./scrip --compile /tmp/rung_NN.icn  > out_m4.s

bash scripts/test_icon_rung_suite.sh --rung rungNN
make libscrip_rt

bash scripts/test_gate_icn_no_stack.sh
bash scripts/test_gate_icn_one_reg_frame.sh
bash scripts/test_gate_icn_semicolon_required.sh
bash scripts/test_gate_icn_local_no_nv.sh
bash scripts/test_smoke_icon.sh
bash scripts/test_smoke_prolog.sh
```

---

## DO NOT

- Touch SNOBOL4 / Snocone / Rebus / Raku / Prolog lower or BB families.
- Use `SM_BB_INVOKE` for Icon programs going through `lower_icn_bb`.
- Write `DESCR_t foo(void *zeta, int entry)` C Byrd box functions.
- Add fields to `BB_t`.
- Walk SM or BB at runtime in modes 3/4.
- Reintroduce the value stack for Icon in any form.

---

## Session Setup

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
bash scripts/test_smoke_icon.sh                   # m3 12/12 · m4 12/12
bash scripts/test_smoke_prolog.sh                 # PASS=5
bash scripts/test_gate_icn_semicolon_required.sh  # PASS (PRISON)
```

---

## Watermark

**2026-07-01 measured (this sandbox, SCRIP `6a509382`, local):** `test_icon_all_rungs.sh` PASS=190 FAIL=63 XFAIL=36 /289 · icon smoke 12/12 m3+m4 · no_stack 0 · one_reg 0 · semicolon prison green · local_no_nv PASS · `audit_jcon_wholesale.sh` 64/66. Older per-session tallies (a different harness era) and the 2026-06-2x session logs were DELETED 2026-07-01 per RULES.md "DELETE completed steps" — full narratives in git + `.github/HANDOFF-*.md`.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
**Architecture:** `ARCH-ICON.md` · `ARCH-x86.md` · `GOAL-ICON-BB-NATIVE.md` · `.github/test_icon.c`

## Session-close / push protocol
See RULES.md — the computed-status FACT RULE (`scripts/handoff_status.sh` verbatim stdout is the ONLY sanctioned completion claim) and the companion rule forbidding the word "HANDOFF" in assistant-authored prose at close. The two rule bodies formerly duplicated here were deleted 2026-07-01; RULES.md is the single home.
