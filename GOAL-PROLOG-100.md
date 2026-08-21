# ⛔⭐⭐⭐ GOAL-PROLOG-100 — SCRIP PROLOG x86/x64 ALL THE WAY HOME: 100%, ONE PLAN, ONE FILE

**Opened 2026-08-16 s165 by Lon in-chat: ONE goal file to 100% Prolog via the THREE ZETAS; every carried item verified against source.** Replaces ten Prolog GOAL-* files (deleted; dispositions §LEDGER, full text in `.github` git at `94fa9093`) — **every deleted Prolog GOAL-* name resolves HERE.** Pruned 2026-08-21 per Lon: completed rungs deleted, prose compressed; history in git.

## ⛔ FACT RULES (RULES.md is the authority; two locally critical)
- **⛔⛔⛔ NO NEW GLOBAL VARIABLES without Lon's explicit in-chat permission that session; the ask must be a big unmissable banner** (name, type, owning file, purpose, why registers/stack cannot carry it). State rides registers (r10/r11 wires) and the stack. Enforcement: diffs checked; uncited new file-scope state = REJECTED (precedent s55).
- **O0-DEV-O2-BENCH (RULES.md s179):** RT_OPT `-O0` for development; `-O2` only for bench/demo, passed explicitly. ⚠ `make` skips recompiles when only `RT_OPT` changes — `rm -f out/rt_pic/*.o out/libscrip_rt.so` first. Label every perf number with its `-Ox`.

## ⭐⭐⭐ THE MODEL — THE THREE ZETAS (same design of record as GOAL-SNOBOL4-100 / GOAL-ICON-100; ⛔ NO DUAL STORAGE ARMS IN THE END STATE)
Tiering directive (Lon s166): **RSP until depth is compile-time-unknown, then RBP frame at α, torn down at ω — all generator constructs with DYNAMIC growth.**

| tier | motion | Prolog embodiment |
|---|---|---|
| **ζ-SPINE** | slides | per-BB FORTH cells on RSP: α grants, zero intermediate pops, ONE terminal release; operands via ZOPQ, results via ZRES; NON-POPPING (Lon s163/s164). NOFC default-ON tree-wide (killswitch `SCRIP_NOFC=0`); cells arm opt-in `SCRIP_PL_CELLS=1` (`pl_cells_stamp`, lower_prolog.c); ZD-PL-A + slices 2a/2b landed (`bb_call_fn.cpp` ~:506/512/515). |
| **ζ-ACTIVATION FRAME** | comes and goes | per-suspension predicate/generator activations; heap-fb ADOPT for resumable graphs (`emit_heap_fb_adopt`, emit.h ~:644; consumers unified via `emit_rec_pin`); record payload = CELL BASE. **The suspend class is the 70.3% wall (32,173 refs) — R-3.** RBP near-eradicated tree-wide; γ-retain re-introduces it ONLY as the ζ-ACTIVATION anchor (PL-Z-2). |
| **ζ-STANDING** | pinned for activation life | per-graph activation base: wire header + params/locals at α; zframe stamp default-ON per-graph (`lower_prolog.c`, killswitch `SCRIP_PL_ZFRAME=0`); mutual exclusion with cells arm structural. **Proc-entry protocol (781 refs, 17.3%) has no BB to own it — R-2.** |

**Register contract:** RSP = FORTH spine · pin is a LAYOUT CONTRACT, not a spelling switch (emit.h law) · R13/R14/R15 scan-reserved · RBX = heap bump-frontier · rcx/rdx = γ/ω wires at proc enter · R10/R11 = glue wires, never scratch · GZ ports: δ = callee α, ε = callee β.
**Canonical sources (RULES.md law):** primary source MANDATORY for semantics rungs. Local seat: unpacked trees at `/home/resources/gprolog-master` + `/home/resources/swipl-devel-master`; web seats: ask Lon for the archives (`refs/` is gitignored, per-session). `SCRIP/doc/{GPROLOG,SWIPL}-STUDY-*.md` are notes, NOT a substitute.

## ⛔ DEFINITION OF DONE — "100%" MEANS THIS AND NOTHING LESS
1. Rung suite 164/164 BOTH modes (`test_prolog_rung_suite.sh`) · smoke 5/5 · honest board green with rc≠0 COUNTED (R-0h landed s166).
2. bench-22 green=22 m3+m4 (`test_bench_prolog_modes.sh`), oracle-correct vs gprolog/`.ref`; van Roy classes closed (findall/forall serialize · assert/retract mid-computation · `is` over runtime-built terms · arity>8).
3. **ONE storage arm** — Lon's ruling from the R-4 A/B table; losing arm + its killswitches DELETED.
4. Gates strict + green: `test_gate_pl_no_new_global.sh` ratchet 14→0 · `test_gate_emit_no_lang.sh` OK · `test_gate_template_medium_invisible.sh --strict` GREEN (remaining: `bb_glue_flat.cpp(4)` + `xa_flat.cpp(8)`) · TEMPLATE-ONLY/BOTH-MEDIUM greps 0 · `handoff_status.sh` COMPLETE.
5. Perf LAST, only under THE INSTRUMENT: emitted-instruction share ≥90% (s154 baseline 55.0%) · ≤1.2× then ≤1.0× GNU on the rail. **Wall time DISQUALIFIED in this container class (s164).**

## THE INSTRUMENT (boards are RUN, never transcribed; re-derive every count fresh)
```bash
bash scripts/test_smoke_prolog.sh                # 5-program tripwire, 3 columns
bash scripts/test_prolog_bb_honest.sh            # counts + exit-gates ORACLE_CRASH (R-0h landed s166)
bash scripts/test_prolog_rung_suite.sh           # 164 × interp+compile
bash scripts/test_bench_prolog_modes.sh          # bench-22 board (green/frontier/broken)
LD_PRELOAD counts: scripts/util_rtx_count_syms.sh  # THE perf instrument (s148 PLT interposition)
```
Twin-arm boards: run any board ×4 = {default, `SCRIP_PL_CELLS=1`} × {`SCRIP_PL_ZFRAME=0/1`} to locate the owning arm. Falsify every zero by injection before believing it.

## ⛔ LAWS THAT BIND EVERY RUNG (compact; RULES.md is the parent)
ASM-DIFF-FIRST (RULES.md s132, supersedes MONITOR-FIRST: smallest repro → diff emitted `.s` → only then gdb ignore-counters; cheapest discriminating experiment first; the sync-step monitor remains a tool, on monitor-proven witnesses only) · TEMPLATE-ONLY · BOTH-MEDIUM · **TRIPLE-ARM CANARY (Lon s230, RATIFIED): every commit touching `src/emitter/`, `src/templates/`, or `x86_asm.h` runs the Icon canary AND this file's smoke+honest BEFORE commit — the couplings run BOTH ways** · ONE-AUTHORITY (grep the rule's shape, not the variable's name) · killswitch byte-identity + compile-time md5 blast radius over the corpus for every codegen change · NO-LANGUAGE-SENTINEL past LOWER · PEERS RULE (`ir_operand_push`; no BB_t fields) · ZERO C Byrd boxes · SINK CONTRACT (whole-arm-or-defer · faithful `sink_deref` · runtime-interned IDs un-bakeable · GC/floor skip for non-allocating arms only · `cmp` is 32-bit always; ~24 `x86("mov",<r32>,imm)` REX.W sites await ruling · `_Static_assert` beside every baked layout · per-rung label decades · per-rung `SCRIP_NO_SINK<N>` — the family switch CANNOT measure a rung).

## ⛔ STANDING CONDITION — SN4 + ICON GOALS RUN CONCURRENTLY, SAME REPOS
Full text GOAL-ICON-100 §STANDING CONDITION, binding here verbatim: separate clones are the default · `git fetch` before trusting any recorded watermark; pin `git rev-parse HEAD` + clean status to every number · a sibling delta is not a Prolog signal until the sibling cursor is checked · shared-emitter commits can move THIS watermark without mentioning Prolog (what the TRIPLE-ARM CANARY catches) · verify HEAD + 0-tracked-modified AT THE POINT OF MEASUREMENT.

---

## ⛔⭐⭐⭐ LIVE CURSOR — 2026-08-16 s166 (Fable 5) · re-verified 2026-08-21 (seat2) at SCRIP `7153ccd7`, fresh `-O0` build: smoke 3/5 UNCHANGED; file pruned per Lon this session
State (s166 boards at `c2ce75b1`+2; smoke re-derived at `7153ccd7`): **smoke 3/5** (clause, recursion FAIL, all columns) · honest **PASS=106 FAIL=0 ABORT=0 ORACLE_CRASH=79** (the 79 = R-0's real backlog) · rung **113 interp / 109 compile of 164** · bench-22 **green=8** · gates: no_new_global ratchet 14/14 · emit_no_lang OK · medium-invisible `--strict` FAIL (`bb_glue_flat.cpp(4)` + `xa_flat.cpp(8)`). Non-smoke boards not yet re-derived at `7153ccd7` — re-derive before work.
**ROOT CAUSE (clause/recursion + the 79-crash class): γ-RELEASE USE-AFTER-FREE.** Multi-clause predicate = flat_gen zframe graph; `n4_suspend_α` CP-pushes a resume INTO the activation; normal γ-exit `add rsp,kt` RELEASES it; caller's write()/libc shred it (first solution's bindings lived there ⇒ blank); backtrack `$res: add rsp,8; pop rsp` re-anchors into freed memory ⇒ rip=0x1. Exact twin of Icon Z-3 under the LIFO CONTRACT (Lon s242): **α carves, ω tears down, γ RETAINS** — canonical law gprolog `wam_archi.def:120` `Local_Top = ((B >= E) ? B : E)`. Full chain + p1–p6 probe matrix: `FINDING-2026-08-16-CLAUDE-PL-Z1A-GAMMA-RETAIN-AND-R0H.md`.
**PL-Z-1a LANDED** (retain arm, opt-in `SCRIP_PL_GAMMA_RETAIN=1`, default byte-identical; `xa_flat.cpp` zframe epilogue-γ). ON-arm measured: divergence moves to the caller handshake (caller landings compiled for the release regime; caller cell refs drift kt+8) and Prolog OUTER main is `flat_jmp_entry=1` so its γ under retain exits exit@PLT kt-deep (p5 ok→rc139).
**THE REGRESSION IS THE ROAD:** s164's 164/164 + 22/22 predates the zeta conversion; today's numbers are the twin-arm substrate's honest price. R-0 reconquers on the NEW substrate — never by reverting it.
**NEXT: PL-Z-2** (= R-0's clause/recursion fix AND R-3's opening) — γ-retain default-ON enabling pair, ~5 coordinated sites per FINDING §3: (a) zframe prologue saves caller rbp in header + pins rbp=own base post-carve (reconcile with `[kt-8]` own-base); (b) γ-retain arm unchanged (hands base in rax); (c) caller staged-call γ/β landings re-anchor `mov rsp,rbp`(−staticΔ) before any cell ref; (d) `$res` backtrack: after `pop rsp`, restore rbp=own base; (e) ω epilogue restores caller rbp before releasing kt. Plus terminal top-graph exclusion (nothing resumes main; its γ stays a release). Retained frames = the CP stack, freed LIFO by backtrack-ω — the FORTH-style non-popping spine. Hazard: PL-FR-4 s14 class (inner-predicate β-resume contamination; per-frame sentinel).

## RUNGS — walk in order; each: own commit, buildable, killswitch byte-identity, twin-arm + TRIPLE-ARM CANARY, cursor move, push mid-session
- [ ] **R-0 RECONQUEST TO THE WATERLINE.** smoke 3/5→5/5 (clause/recursion first = PL-Z-2) · rung 113/109 ratchets upward every session, floor = last cursor's numbers · bench-22 8→11 (the s16 waterline)→22. ASM-DIFF-FIRST per failure; run the ×4 twin-arm board to locate the owning arm before reading code. ⚠ bench-22 was green=11 BOTH arms at `9313935` (s16); the drop to 8 post-dates it — bisect against sibling shared-emitter landings, canary-style.
- [ ] **R-1 ζ-SPINE: ZK-5B VAR_REF MATERIALIZATION** (the live blocked rung; Option A AS IMPLEMENTED FALSIFIED s14, green 6→0). Restart protocol: (1) refuse dirty tree; (2) re-derive both bench boards at HEAD; (3) **build a discriminating witness FIRST** — red on cells=1 today, green under correct materialization (`app/3`/`two.pl` do NOT discriminate — s14 correction); (4) re-apply `.github/WIP-2026-08-09-PL-ZK-5B-option-A-FALSIFIED.patch`, asm-diff first; test the `[nargs, nparams)` bound repair; (5) killswitch must cover the RUNTIME site (`rt.c`), not just the emitter (s14 defect); (6) ⛔ LON RULING WANTED: Option A (pre-allocate) vs B. Then **ZK-6 RATCHET** (bench 22/22 m3+m4 cells arm · rung 164/164 · smoke 5/5 · sink census ≥ legacy arm) and **ZK-7 GATES + A/B TABLE** feeding R-4.
- [ ] **R-2 ζ-STANDING: PROC-ENTRY MECH DECISION.** 781 frame refs (17.3%) with no BB owning the entry protocol (wire header, saved rcx/rdx/base). FUNCTION-class frame vs wire cells at fixed spine offsets; MECH-shaped — coordinate with GOAL-SNOBOL4-100's frame census, never land a new frame/glue protocol from this file alone.
- [ ] **R-3 ζ-ACTIVATION: THE SUSPEND/RESUME CLASS (the 70.3% wall).** PL-ZK-5: predicate/generator graphs — pending-cells vs pthread decided by MEASUREMENT (the ICN suspension-decision shape; watch ICN-GEN-GAMMA-RETAIN, same class). Includes ζ-FB-4 instrument: any graph with `emit_jmp_pin_legacy() && !emit_heap_fb_adopt() && suspend-slot ≥ 0` — empty ⇒ close the β narrow/wide asymmetry; non-empty ⇒ real measured decision; FALSIFY BY INJECTION first. ⛔ Do NOT blind-widen `emit_fb_stmt_scan` to `IR_DISJUNCTION` — the bail is PRINCIPLED (choice-point arrivals are not rebalanced by the HEAD..RELEASE bracket); needs a rebalancing proof (s164(5), s158).
- [ ] **R-4 ONE ARM.** A/B table cells-vs-zframe over the full board set → **Lon's default ruling** → flip default → DELETE the losing arm, its stamps, its killswitches. Completion: `grep -c 'SCRIP_PL_CELLS\|SCRIP_PL_ZFRAME' src/` reads only the survivor.
- [ ] **R-5 FEATURES & CORPUS TO 100%.** (a) Banked engine defects: engine-wide silent-fail on undefined predicates (→ existence_error) · **NO-LCO recursion cap** (16-wide body dies at depth 10 — likely the largest bench-22 unlock) · nested-`\+` binding leak · retractall/1 gaps · int/float standard-order conflation (`rt_pl_term_compare`, two-oracle) · lexer escape three-site/two-behaviour · `:` at 200 vs 600 + `|` missing as 1105 xfy · double_quotes-under-dialect (⛔ LON RULING WANTED; + PL-STRICT-1 silent-acceptance class). (b) Feature rungs: rung33 call/1..7 goal-as-Var · rung40 string type (dialect-gated) · rung41 list-ISO · rung42 meta-predicates · rung43 streams §7.9 · rung44 format §7.5 · rung45 DCG full · rung46 cross-clause catch/throw. (c) Suite reconquest (full step text git `94fa9093`): SWI extractor → core files (term/arith/sort/call/exception/write/read/op/copy_term/syntax/bags/format) → library (lists/apply/aggregate) → db → ISO conformance (gprolog `tests/`); ≥80% each, ×2 modes + gprolog oracle. Requires primary sources (§MODEL).
- [ ] **R-6 PERF FENCE (LAST; every claim under THE INSTRUMENT, never wall time).** (a) finish medium-invisible: `xa_flat.cpp(8)` + `bb_glue_flat.cpp(4)` → `--strict` GREEN (⛔ LON RULING WANTED: 4 dead xa_flat arms convert vs DELETE); (b) surviving SINK rungs: SINK-5 `$is_v` delivery · SINK-9 `$trail_unwind`/`$unwind_nothrow` (design-heavy, LAST of the leaves) · SINK-10 sweep (const-unify, deref-only sites, route audit) · SINK-4 kk==4 per-site intern cache · SINK-2 enrich; (c) RTX residue: `queensn`+`queens` workload widening, eradication of proven-cold `c_*` bodies per RTX-CLAIMS ledger rules; (d) SINK-FENCE: emitted share ≥90% (s154: 55.0%; `gc_collect_ex` largest unowned leaf — ⛔ LON RULING WANTED: GC carve-out vs GC rung); (e) register residency H+TR → ≤1.2× → ≤1.0× GNU on the van Roy rail, fail-driven shapes, two mode-4 binaries.

## ⛔ FALSIFIED / DO-NOT-REDO (each cost a measurement; retire only by RE-measurement on a moved substrate)
· **SINK-6/7 arith/cmp strcmp premise** — s147: `rt_pl_dop_ax_*`/`dop_cmp_fast` fast paths pre-empt the dispatch; the chain is COLD; the cost is the CALL. Double-compare trap: C compares ints VIA DOUBLE — naive int-cmp diverges above 2⁵³.
· **ZK-5B Option A as implemented** — s14, green 6→0; restart from the WIP patch per R-1, never from memory.
· **Single-kind ZD admission** — s163: unlocks ZERO runs; the unlock set is FIVE kinds, all-or-nothing per run, CBP in every blocking set.
· **Blind-widening `emit_fb_stmt_scan` to IR_DISJUNCTION** — s158 signature: 107/164 + SIGSEGV; the bail is principled.
· **The family switch as a rung instrument** — s146: it compares {all}vs{}; per-rung `SCRIP_NO_SINK<N>` only; ~5% effects need ~60 runs/arm; output identity ≠ work identity.
· **Wall time in this container** — s164: bimodal 649–1246ms on ONE binary; same-binary-twice control first, `^ms:` filtered, spread reported — or no claim.
· **`IR_VAR` "retired as vacuous — do not widen"** was ruled for SN4 GLOBALS; Prolog vars ARE graph locals — a reasoned re-open with Lon visibility, never a blind widen.
· **Exit 0 is not exoneration** when the divergence class is stdout-only — falsify by injection, both directions.

## ⛔ LON RULINGS WANTED (consolidated; strike when ruled)
(1) ZK-5B VAR_REF materialization Option A vs B (R-1). (2) Storage-arm default cells vs zframe (R-4, after the A/B table). (3) xa_flat 4 dead arms: convert vs DELETE (R-6a). (4) ~24 cross-language `x86("mov",<r32>,imm)` REX.W sites. (5) GC carve-out vs GC rung for the ≥90% KPI (R-6d). (6) double_quotes target dialect + PL-STRICT-1 (R-5a). (7) s163b/s164(10) provenance: parallel-writer contamination + rewritten pushed history — SHA-keyed baselines unsound until ruled (the ruling can be "expected; verify-at-measurement suffices").

## LEDGER — the 10 absorbed Prolog goal files (full text: `.github` git `94fa9093`)
PROLOG-BB (ζ/SINK ladder; opens → R-3/R-5/R-6) · PL-ZETA-CELLS (ZK-0..3 landed; ZK-5B → R-1) · PL-ZFRAME-RESTORE (FR-2 default-ON; twin-track → R-4) · PROLOG-RTX (arbitration resolved: SINK owns the hot symbols; residue → R-6c) · PROLOG-IR-RUN (OBSOLETE — modes 1/2 deleted, `sm_interp.c` gone) · PROLOG-BB-BYRD (HISTORICAL — broker landed, 0 opens) · PST-PROLOG (Phase 1 COMPLETE, 0 opens) · PARSER-PROLOG (self-host frontend experiment parked; GOAL-PARSER-SC-TRANSPILE owns that thread) · LANG-PROLOG (landed s118–s155 in git; survivors → R-5b) · PROLOG-100-SWI (suite arm → R-5c; carried lesson: **an atom is `DT_A` OR `DT_S` depending on entry — check both tags**).

## Architecture reference (the living contract)
Pipeline: Prolog AST → `lower_prolog` (four-port IR) → m3 `--run` (EMIT BINARY → RX slab) · m4 `--compile` (EMIT TEXT → as+gcc). GZ ports: δ = callee α, ε = callee β.
| Construct | α | β | γ | ω |
|---|---|---|---|---|
| `IR_GCONJ` (seq) | first goal's α | last goal's β | `goal[i].γ = goal[i+1].α` | `goal[i+1].ω = goal[i].β`; first → ω_in |
| `IR_CHOICE` | first clause α | next clause α | each `.γ = γ_in` | `clause[i].ω = clause[i+1].α`; last → ω_in |
| `IR_GOAL` (call) | callee α | callee β | callee success → γ_in | callee exhausted → ω_in |
| `IR_ITE` | cond.α | ω_in (semidet) | cond.γ→Then, Then.γ→γ_in | cond.ω→Else, Else.ω→ω_in |
| `IR_UNIFY` | self | — | bind/match → γ_in | mismatch → ω_in |
| `IR_CUT` | self | — | γ_in | cut barrier → ω_in |
| leaf | self | — | γ_in | ω_in |

Admission recipe (new deterministic builtin): (1) `IR_DET_FOO` in `IR.h` + name table `scrip_ir.c`; (2) `rt_pl_foo_cell(...)` — cell-based, trail-mark/unwind, no `g_resolve_env`, `prolog_atom_intern()` not `ATOM_*`; (3) `bb_det_foo.cpp` — FRQ per slot, one call, `test eax,eax; jne γ; jmp ω; def β; jmp ω`; (4) `bb_prepare` block in `emit_bb.c`; (5) `emit_core.c` dispatch case; (6) Makefile `RT_PIC_SRCS` + rule; (7) four `scrip.c` sites (`pl_gz_rule_body_goal_ok` · `pl_gz_rule_clause` op-filter · `pl_gz_count_synth_goal` · `pl_gz_build_goal`, named arm BEFORE the generic pair-comparator arm). `ir_call_arg` for `is_builtin_exec` builtins; `ir_pair_arg` for arity-2 pairs.

## Session Setup (every session)
```bash
git clone https://github.com/snobol4ever/.github /home/claude/.github; for r in SCRIP corpus x64; do git clone https://github.com/snobol4ever/$r /home/claude/$r; done
cd /home/claude/SCRIP && git config --local user.name LCherryholmes && git config --local user.email lcherryh@yahoo.com
bash scripts/install_system_packages.sh && rm -f scrip && timeout 1500 make -j8 scrip > /tmp/build.log 2>&1 && make libscrip_rt && ls -la scrip out/libscrip_rt.so
# ⛔ CONCURRENCY PRE-CHECK (STANDING CONDITION): git -C . log origin/main..HEAD ; git status --porcelain — non-empty ⇒ clone fresh and measure THERE
bash scripts/test_smoke_prolog.sh && bash scripts/test_prolog_bb_honest.sh && bash scripts/test_prolog_rung_suite.sh && bash scripts/test_bench_prolog_modes.sh
bash scripts/test_gate_pl_no_new_global.sh && bash scripts/test_gate_emit_no_lang.sh
# primary sources (semantics rungs): local seat has /home/resources/{gprolog-master,swipl-devel-master} unpacked; web seats ask Lon (refs/ gitignored, per-session)
```

## ⛔ SESSION-CLOSE RULES LIVE IN `RULES.md` — NOT DUPLICATED HERE
"HANDOFF COMPLETE" requires a confirmed push; `scripts/handoff_status.sh` verbatim is the only truth; credential missing ⇒ BLOCKED, ask Lon in-chat and WAIT. Move THIS file's LIVE CURSOR every session — no cursor move, no close.
