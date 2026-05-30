# GOAL-RAKU-BB.md — Raku goal-directed ~20% onto shared BB generators

## ⏸ ON HOLD — 2026-05-30

**Lon directive (2026-05-30): Raku development paused indefinitely. Raku BB is no longer top
priority. Do not resume without explicit re-prioritization from Lon.**

Gates at hold: GATE-RK m2 45/46, GATE-RK4 m4 46/46 PERFECT, GATE-RK3 m3 45/46 CRASH 0,
smoke 5/5/5/13/5, SNOBOL4 iso M2 19/0 M4 18/1. one4all HEAD `290af6b9`. Build clean.

Next work when resumed: SM-2 `when`-arm reroute (diagnose BB_ITERATE/SM_CALL_FN mode-4 crash
via gdb on rk_given18 in_loop; see watermark for full diagnosis). Then SM-3 frontend (own session).

---

**Repo:** one4all + corpus + .github
**Sister:** GOAL-ICON-BB.md (kinds REUSED) · GOAL-RAKU-FRONTEND.md
**Prereq:** HEADQUARTERS PP-1..6 ✅. BB-TEMPLATE-LADDER invariants 0..9 apply.

## Two IRs

- **SM** — flat stack-machine spine (`src/include/SM.h`).
- **BB** — four-port Byrd-box graph (`src/include/BB.h`). Kinds are **language-agnostic**. `BB_graph_t.lang` tags origin (`BB_LANG_RKU=6`); node kinds are reused.

SM emits `SM_BB_INVOKE` (language-ignorant BB jump-in/jump-out; split out of the old SM_BB_SWITCH per LANG-IGNORANT-SM-TEMPLATES, 2026-05-28). Raku reuses the ICN_GEN emit-time contract verbatim. Icon/Prolog are ~100% BB. SNOBOL4/Snocone/Rebus are mixed. Raku today is ~100% eager SM in practice; the goal-directed ~20% is what this ladder moves onto shared BB kinds.

## The insight

Per docs.raku.org: almost everything generative in Raku produces a **`Seq`**. `gather`/`take`, `…`, lazy ranges, `map`, `grep` — all "generate a Seq" on demand. ONE four-port pull protocol (yield-one-at-β = Icon `BB_SUSPEND`/`BB_EVERY` PUMP) suffices; every generative construct is a PRODUCER or CONSUMER of it. A 10-kind ladder collapses to ~3 rungs on shared kinds.

## Port semantics (identical to Icon generators)

| Port | Direction | Raku meaning |
|---|---|---|
| γ | inherited DOWN | `take` yield / next Seq element |
| ω | inherited DOWN | exhaustion (Seq drained; junction collapsed; grep all-false) |
| α | synthesized UP | fresh-pull entry (first `.pull-one`) |
| β | synthesized UP | resume entry (next `.pull-one` after a yield) |

Driver = **`BB_PUMP`**. NOT Prolog's `BB_ONCE`.

## Moves to BB vs stays SM

**MOVES (goal-directed, REUSE shared kinds):**

| Raku construct | shared BB kind | rung |
|---|---|---|
| lazy range `$a..$b`, `$a,$b ... $c` | `BB_TO_BY` | RK-BB-1 ✅ |
| `gather { … take … }`, `…` operator | `BB_SUSPEND` + `BB_EVERY` PUMP | RK-BB-2 ✅ |
| lazy `map` / `grep` | `BB_ITERATE` consumer | RK-BB-3 ✅ |
| junctions `any`/`all`/`one`/`none`, infix `\|`/`&` | `BB_ALTERNATE` + Bool-collapse | RK-BB-4 (blocked Q9-Q12) |

**STAYS eager SM:** scalar builtins, `say`/`print`, arithmetic, hash/array element ops, class/method dispatch, `sort` (whole-list), `try`/`CATCH`.

**REGEX / GRAMMAR (RK-NFA rungs, this file):** regex backtracking onto an isolated `BB_NFA_*` family. Grammar/LTM deferred (Phase 2). See the RK-NFA rungs in Open rungs below.

## ⛔ Rules

- No C Byrd boxes; no SM/BB walking at runtime in modes 3/4; ports are α/β/γ/ω; X86 arms only.
- No `rt_*`/`raku_*` port-logic helpers. Conversion/effect helpers via `@PLT` (mode-4) or absolute `movabs+call` (mode-3) are fine.
- **No language sniffing in SM/BB/XA templates.** Per-language behavior lives in lowering.

## Completed rungs

- **RK-BB-1 ✅** `for $a..$b -> $i` → `BB_TO_BY`.
- **RK-BB-2 ✅** KEYSTONE lazy Seq. `gather`/`take`+`…` → `BB_SUSPEND`+`BB_EVERY` PUMP. REUSE `bb_upto.cpp`.
- **RK-BB-3 ✅** lazy `map`/`grep` as Seq CONSUMERS (eager-drain). Sub-steps 3.0/3a/3b/3c/3d green.
- **RK-BB-SEGFAULT-CLUSTER ✅** 4 bugs: polyglot union-clobber, multi-sub structure for TT_SUB_DECL, lower_return value preservation.
- **RK-BB-SM-FRAME-MODE4 ✅** Mode-4 named-sub frame slots: `rt_frame_enter/leave/load/store` + SM_LOAD/STORE_FRAME x86 templates.
- **RK-GIVEN-MODE4 ✅** `given`/`when` as if-chain (no SM_PUMP_CASE, no thunks).
- **RK-HASH ✅** hash builtins (set/get/exists/keys/values/pairs/delete), SOH/STX encoding.
- **RK-IO ✅** `rk_fileio38`+`rk_stdio39` mode-4. `TT_ITERATE(TT_FNC)` arm in `lower_every`; `raku_capture` returns FHVAL; setvbuf line-buffer stdout.
- **RK-EXCEPTIONS ✅** try/CATCH/die mode-4. SSE-safe `raku_die`; exc_clear/check/get; guard hash-builtin on DT_S.
- **RK-CLASS ✅** `rk_class26` modes 2 and 4. `lower_class_decl` emits `RECORD_REGISTER` before `RECORD_MAKE`; handler delegates to idempotent `icn_record_register`.
- **MODE3-NO-INTERP-3 ✅** SM_NAMED_CALL absolute-target patching in sm_run_native Pass 3 closed Cluster 2.
- **M3-RK-NOINTERP-1a ✅** `bb_to_by.cpp` MEDIUM_BINARY r12→rt_push_int (Sonnet 4.6, `55d03444`).
- **M3-RK-NOINTERP-1b ✅** SM_BB_INVOKE MEDIUM_BINARY arm — scratch-buffer-flush w/ sink save/restore, `walk_bb_node` integration, ascending-sites fix in `bb_to_by.cpp:142` (Opus 4.7, `48ca4e21`).
- **M3-RK-NOINTERP-1c ✅** `bb_iterate.cpp` Raku MEDIUM_BINARY arm wired (Opus 4.7, 2026-05-29, one4all `8d3a8cdf`). Mirrored the existing MEDIUM_TEXT arm in raw x86: α zeroes `&pBB->counter`, β-define falls into `NV_GET_fn(name)`, unpacks `rax:rdx` (low32=v, hi32=slen; rdx=base ptr), strlen-fallback when slen=0, bounds-check `jge lω`, scan for SOH separator, `GC_malloc(seg_len+1)` + `rep movsb` + NUL-term, `rt_push_str(ptr,len)` + `jmp lγ`. All four helper calls use absolute `movabs rax,&fn; call rax` (no PLT in mode-3). bin.sites ascending: `{beta_off, fail_off+2, succ_off+1}` paired with `{lβ_p define, lω_p, lγ_p}`. **Mode-3 native: 19→25 PASS** (+6: rk_fileio38, rk_for_array{,_simple,_underscore}, rk_given18, rk_map_grep_sort24 all CRASH→PASS).
- **RK-M2-GATHER ✅** mode-2 gather multi-yield (Opus 4.8, 2026-05-29, one4all `30e7c0a1`). `rk_gather` FAILed mode-2: `bb_exec.c` `BB_SEQ` was an AG-PURE passthrough that never drove the gather body's `BB_SEQ→SUSPEND·SUSPEND·SUSPEND·FAIL` chain (SUSPEND hit `default:`→FAIL, and `bb_exec_once/resume` walk to `next==NULL` with no pause-at-yield). Added a gather driver INSIDE `case BB_SEQ`, gated `g_current_cfg->lang==BB_LANG_RKU && bb->α->t==BB_SUSPEND`: yields ONE take per (re)entry using `bb->counter` as the resume cursor (reset to 0 by `bb_exec_once`, preserved by `bb_exec_resume`); the counter-th SUSPEND's `α` is evaluated and returned as `bb->value` via terminal `NULL`; walking past the last SUSPEND onto `BB_FAIL` → `FAILDESCR`. Mirrors mode-3 `bb_seq_gather_binary` (resume_slot ≡ counter, per-child γ-yield ≡ the NULL return through the driver loop). GATE-RK m2 23→24. Ordinary proc-body SEQs (α not a SUSPEND) untouched.
- **RK-M2-ACOMP ✅** `SM_ACOMP` string→numeric coercion (Opus 4.8, 2026-05-29, one4all `30e7c0a1`). `rk_given18` FAILed mode-2: `given` on a `for`-loop variable missed every `when` arm. Array elements pulled via `BB_ITERATE` arrive as `DT_S`; `sm_interp.c` `SM_ACOMP` treated any non-`DT_I`/`DT_R` operand as `0`, so topic `"1"` compared as `0==1`→false→default. Fix mirrors `SM_ADD`: `if (l.v==DT_S) lv=to_real(l)` (and r). GATE-RK m2 24→25. Shared across all languages; verified zero regression (SNOBOL4 crosscheck unchanged via before/after stash, Icon relop direct, broad broker 6/6).
- **RK-BB-4a ✅** constructor junctions any/all/one/none mode-2 (Opus 4.8, 2026-05-29, one4all `30e7c0a1`). Per Q9/Q12. `lower.c` `lower_fnc` intercepts Raku lowercase any/all/one/none (NOT the SNOBOL4/Icon `ANY` pattern path) → `SM_CALL_FN __rk_jct_<flavor>` with the RK-BB-3.0a dup-name first arg skipped. `raku_builtins_byname.c` packs a tagged-string junction VALUE (Q12): `ETX(0x03) + flavor('a'/'l'/'o'/'n') + SOH-separated members` (ETX is free of the SOH/STX array/hash bytes). `rk_junction_is` + `rk_junction_collapse` (recursive on junction members) thread the relop per flavor: any=OR, all=AND, one=exactly-one, none=NONE. `sm_interp.c` `SM_ACOMP`(numeric)/`SM_LCOMP`(string) gain a junction guard (`DT_S && s[0]==0x03`, never fires for normal values) routing to the collapse. GATE-RK m2 25→26.
- **RK-BB-4b ✅** infix `|`/`&` junctions mode-2 (Opus 4.8, 2026-05-29, one4all `30e7c0a1`). Per Q10 (BB-ALT-class substrate is the model, but mode-2 uses the same tagged-string value as 4a — no new opcode per Q9). `raku.l` adds single-char `|`/`&` (flex longest-match keeps `||`/`&&`; no code-sigil conflict). `raku.y` `mk_junction` builds `l|r`→`any(l,r)`, `l&r`→`all(l,r)` as the SAME `TT_FNC` node make_call produces, so infix + constructor share one lowering + collapse; same-flavor chains FLATTEN at parse time (`(3&3)&3`→`all(3,3,3)`), sidestepping the nested-`\x01` leak in the flat rep. `%left '|' '&'`; parser/lexer regenerated, zero grammar conflicts. **Full `rk_junctions` probe PASS mode-2.** GATE-RK m2 26 (rk_junctions FAIL→PASS; net session 23→26).
- **M3-RK-NOINTERP-1d ✅** `rk_gather` closed (Opus 4.8, 2026-05-29, one4all `a894af4a`). Last Cluster-1 native test. The gather body BB graph is `BB_SEQ(n=4) → SUSPEND·SUSPEND·SUSPEND·FAIL` (NOT the bb_upto path the prior handoff guessed). Three coordinated fixes: **(1) `bb_seq.cpp`** new raw-x86 gather-driver `bb_seq_gather_binary` — the MEDIUM_BINARY arm only walked the `xa_bb_emit_pair_*[]` passthrough, which is UNPOPULATED on the SM_BB_INVOKE → `walk_bb_node` path (no `flat_drive_seq` ran), so outer β (`.Lbbinv%d_β`) was never defined → `bb_emit_end` abort. New driver mirrors the MEDIUM_TEXT gather-driver in raw bytes: α fan-out `jmp s0_α`; define outer β = `movabs rax,&resume_slot; mov rax,[rax]; jmp rax`; per-child: define Lα[k], `walk_bb_node(child,NULL)`, define Lγ[k] fixup (`movabs rax,&resume_slot; lea rcx,[rip+nxt]; mov [rax],rcx; jmp outer_γ`); done trampoline `jmp outer_ω`. resume_slot is a malloc'd quad (scratch page has no .data); intermediate labels malloc'd so pointers survive into the wrapper's `bb_emit_end` (runs after bb_seq returns); rip-relative `lea` patches via standard `bb_emit_patch_rel32` (site+4 = rip). **(2) `bb_suspend.cpp`** MEDIUM_BINARY arm now pushes via `rt_push_int` (movabs+call) not raw `mov [r12]` — `sm_run_native` doesn't init r12 as a value-stack pointer (the SM value stack is the `g_vstack` C global), so the old r12 stores segfaulted; same fix bb_to_by took in 1a; bin sites reordered ascending per 1b. **(3) `lower.c` `lower_every`** new branch for `for gather{} -> $v` (`TT_EVERY(TT_ITERATE(v, TT_FNC(__gather_N)))`) — the generic scaffold routed through `lower_iterate` which emits `SM_BB_INVOKE; STORE_VAR v` BEFORE the scaffold's `JUMP_F`, storing the loop var from an empty value-stack on the exhaustion pull → underflow; new branch mirrors the iterate-array branches (JUMP_F gates the store). **Mode-3 native: 25→26 PASS, CRASH 7→6** (rk_gather CRASH→PASS).

## Open rungs

- [ ] **M3-RK-NOINTERP-1e (regex cluster) → SUPERSEDED by the RK-NFA rungs below.** `rk_re32/33/34/35/37`, `rk_regex23` (6 tests). NOTE: these FAIL in mode-2 too (not only mode-3 CRASH) — see RK-NFA-1 dispatch-gap finding.

### RK-NFA — Raku regex onto an ISOLATED `BB_NFA_*` family

**Decision (locked w/ Lon, 2026-05-29):** build a NEW isolated `BB_NFA_*` opcode family, do NOT reuse SNOBOL4's shared pattern opcodes. Reasons: (1) isolation removes the chief regression risk (shared templates would let a Raku bug hit SNOBOL4's hot path); (2) NFA kinds are the more-generic basis (SNOBOL4's `SPAN`/`BREAK` derive from `CLASS+`); (3) captures genuinely diverge — SNOBOL4 `$`/`.` write GLOBALS, Raku `$0`/`$<n>` are scoped match-object captures, var model not unified; (4) the mode-2 SNOBOL4 matcher (`snobol4_pattern.c`) is SNOBOL4-runtime-bound. Convergence into language-agnostic `BB_MATCH_*` is DEFERRED (RK-NFA-CONV) only where byte+semantics identical; `SPLIT` + captures stay separate.

**Raku semantics (verified docs.raku.org + S05):** HYBRID — quantifiers/`||`(ordered)/`regex`-decl/subrule-retry = backtracking (→`BB_NFA_*`); `|` = declarative LONGEST-TOKEN + proto = parallel/forward (→Phase 2). Grammars are the SAME engine (namespace of `token`/`rule`/`regex`; subrule `<name>` = backtrackable method call). The 6 tests are PLAIN regex (only single-char `a|b` where LTM≡ordered) → Phase 1 needs no LTM machinery.

**Family 1:1 from `Nfa_kind`:** `BB_NFA_{CHAR,ANY,CLASS,SPLIT,EPS,BOL,EOL,CAP_OPEN,CAP_CLOSE,ACCEPT}` (Phase 1); `{ASSERT,PRED,SUBCALL,LTM}` (Phase 2). Driver `BB_PUMP`, β = next-state/backtrack edge.

## ⛔ DECISION (Lon + Claude, 2026-05-29) — LEAF BB EMISSION SHELVED; PIVOT TO THE SEAM

**Status: RK-NFA-4 / RK-NFA-5 / G1-1 / G1-2 / G1-3 are SHELVED (not deleted, not pursued).** After working the SPLIT design end-to-end, Lon and Claude concluded the leaf single-pattern emission path is **ceremony, not value**, and the BB effort should move one tier up to the subrule seam.

**The reasoning (recorded so a future session does not re-open the leaf push):**

1. **The leaf matcher already works in all three modes via the C path.** `~~` lowers to `SM_CALL_FN raku_match` → the byname dispatcher → the isolated `raku_nfa_*` backtracking matcher (`nfa_bt`, ~35 lines). GATE-RK m2 41/42, GATE-RK4 m4 42/42, GATE-RK3 m3-native 41/42 CRASH 0. The BB leaf-emission path fixes **nothing that is broken**; default `~~` is the C matcher (`RK_NFA_BB` OFF) and stays that way.
2. **Nine of the ten `BB_NFA_*` kinds do not backtrack.** CHAR/CLASS/ANY/BOL/EOL/CAP_*/EPS/ACCEPT are SINGLE-SHOT leaves: they advance (γ) or fail (ω), and their β just forwards to ω — they have no second solution to yield. For those nine the four-port box is a **costume** over "test a char, advance or fail." Only **SPLIT** uses the structure (it is the one choice point), and SPLIT is "try arm 1 else arm 2" — a two-line C conditional vs a byte-exact crash-on-wrong-byte x86 template with the loop-back-edge `counter` subtlety. Not worth a hard session to reproduce a verdict the C matcher already returns.
3. **BB backtracking relocates the control stack; it does not abolish backtracking state.** The ω→β wiring + per-box `counter` removes the explicit *control* choice-point stack for FLAT patterns (one stack collapses into graph edges). But RECURSION (subrule calling subrule) still needs a stack of resume *cursors* somewhere — the interpreter's C stack / the compiled WAM-CP frames — because one node's single `counter` cannot hold N depths at once. So the BB win is real but **narrow**: it is load-bearing only where there is resume-across-recursion. Flat leaf regex has none → no win there.

**WHERE BBs DO EARN THEIR KEEP (what we keep + pursue):**
- **The subrule seam (G3).** `<name>` is a backtrackable METHOD CALL: on outer failure the subrule must yield its NEXT match, recursively, while building the Match tree. That is exactly resume-and-yield-next across a call boundary = the job four-port generators (`BB_SUSPEND`/`BB_ALT`/`BB_PUMP`, all of which ALREADY EXIST) are good at. This is the real BB destination and it is the #1 grammar goal anyway.
- **Uniform kind-set for the five backends** (the goal's stated instrumental rationale). Caveat we go in clear-eyed about: if regex does not naturally want BBs, the nine leaf "kinds" we already flushed out may be the *wrong* (leaf-costume) kinds — the seam generators are the kinds that matter.

**KEPT (cheap, may serve the seam):** the isolated `BB_NFA_*` enum (`src/include/BB.h`) and the `raku_nfa_to_bb` graph builder (RK-NFA-1b ✅). The already-landed leaf templates in `bb_nfa.cpp` stay DORMANT behind `RK_NFA_BB` (OFF) — not deleted (removal risks the green gates for zero functional gain), not extended. `bb_nfa_split` is **NOT** to be written.

**ISOLATION DECISION (2026-05-29, locked) STILL HOLDS** — the `BB_NFA_*` family is isolated from SNOBOL4's pattern opcodes for the four reasons recorded below. Shelving leaf *emission* does not reopen that; it only stops grinding the leaf x86 templates.

- [ ] **RK-NFA-1 — wire family + mode-2 backtracking walk.** 1a/1b/1c/1d/1e ✅; remaining: gate the BB graph into mode-4 (RK-NFA-4 below).
  - [x] 1a. `BB_NFA_*` enum block in `src/include/BB.h` (isolated; SNOBOL4's pattern opcodes untouched).
  - [x] 1b. **DONE (RK-NFA-1b ✅, Opus 4.8, 2026-05-29, one4all `6b593da8`).** `raku_nfa_to_bb(Raku_nfa*) → BB_graph_t*` state→node walk in `raku_nfa_bb.c` (isolated; zero `snobol4_pattern.c` contact). `nfa_kind_to_bb` 1:1 `Nfa_kind`→`BB_NFA_*`; one `BB_t` per NFA state; ports γ=out1-node (advance), β=out2-node (SPLIT backtrack), ω=NULL for the consumer scaffold; payload CHAR ival=char, CLASS sval=32-byte cset blob, CAP_OPEN/CLOSE ival=group idx; `bbg->entry`=start node; returns NULL on Phase-2 kinds (NK_CODE/NK_SUB_CALL) so callers fall back. Verified standalone: graph faithfully mirrors the NFA across the full L1-L15 pattern set (node count == state count, ports wired, entry correct, csets/chars/caps carried). Pure graph construction, NO x86, dead-code-until-RK-NFA-4. Gates unchanged.
  - [x] 1c. Isolated mode-2 backtracking matcher `raku_nfa_bb_match` (`src/frontend/raku/raku_nfa_bb.c`, `nfa_bt` depth-first, β=`SPLIT.out2`); `raku_nfa_start/accept` accessors + `raku_nfa_states` defined; Makefile wired; `RK_NFA_BB=1` gate in tree-walk handler.
  - [x] 1d. Standalone oracle: backtracking BB verdict == parallel NFA verdict on **L1-L12, 12/12, zero mismatches.** Thesis proven.
  - [x] 1e. **CLOSED (RK-NFA-1e ✅, Opus 4.8, 2026-05-29, one4all `0d94e255`).** SM dispatch gap closed and the WHOLE mode-2/mode-4 regex cluster lit up (went past option-A name-registration). `~~` lowered to `SM_CALL_FN raku_match` but the only handler `raku_try_call_builtin(tree_t*)` was the legacy tree-walk; `--interp` (`sm_interp.c:1387`) and `rt_call` (`rt.c:1598`) reach `raku_try_call_builtin_by_name`, which never knew the name → all 6 regex tests failed BOTH modes. **(1)** `raku_builtins_byname.c`: by-name twins using pre-eval'd `args[]` — `raku_match`, `raku_match_global`, `raku_subst`, `raku_nfa_compile`, `raku_re_capture`, `raku_named_capture`; all route through the ISOLATED `raku_nfa_*` matcher (`raku_re.c`/`raku_nfa_bb.c`), zero SNOBOL4-pattern-opcode contact. **(2)** Capture name-collision: the lexer mapped BOTH `$*STDOUT`/`$*STDERR` (FH) and `$0`/`$1` (regex) to `VAR_CAPTURE→TT_CAPTURE→raku_capture`, and the RK-IO `FHVAL` handler shadowed the regex slice. Split at the lexer: `$*STD*`→new `VAR_FH`→`TT_FH_CAPTURE`→`raku_capture` (FH, byte-identical); `$0`/`$1`→`VAR_CAPTURE`→`TT_CAPTURE`→new `raku_re_capture` (group slice). Net-zero new grammar conflicts (still 30). **(3)** Subst write-back: `s/pat/repl/` mutates its subject; by-name args are pre-eval'd values (var identity erased, unlike the AST handler's frame inspection). When the smatch-subst LHS is a plain `TT_VAR`, `lower_expr` emits `STORE_VAR`+re-`PUSH_VAR` after the call → subject rebound, statement still yields a value. **GATE-RK m2 35→41/42** (only rk_stdio39 fidelity non-bug remains), **GATE-RK4 m4 36→42/42 PERFECT**. Smoke 5/5/5/13/5 HOLD; SNOBOL4 pattern-rung suite BYTE-IDENTICAL M2 19/0 M4 18/1 (isolation proven); FACT 0 (mode-2/4-dispatch rung, no emitter/template bytes). This subsumes the mode-2/mode-4 verdict+capture+global+subst goals of RK-NFA-2/RK-NFA-3 as well; what remains for those rungs is the BB_NFA_* emission path (RK-NFA-1b → RK-NFA-4/5).
- [ ] **RK-NFA-2 — mode-2: csets + anchors + ordered alt** (rk_re32/33, L4-L12). Verdict logic already oracled; needs RK-NFA-1e plumbing.
- [ ] **RK-NFA-3 — mode-2: captures** `$0`/`$1`/`$<name>` → `BB_NFA_CAP_*` (rk_re34/35, L13-L15).
- [ ] **RK-NFA-4 — mode-4 emission. ⏸ SHELVED 2026-05-29 (see DECISION block above).** Leaf-emission ceremony; default `~~` stays on the C matcher. The 9 landed leaf templates stay dormant behind `RK_NFA_BB`; `bb_nfa_split` is NOT to be written. NEW `src/emitter/BB_templates/bb_nfa_*.cpp` (FACT-pure, four-port, isolated). GATE: rk_re33/34/35 mode-4; SNOBOL4 pattern-rung suite byte-unchanged. **SCAFFOLD LANDED (Opus 4.8, 2026-05-29, one4all `ac1bc66b`):** `bb_nfa.cpp` with the trivial passthrough nodes `bb_nfa_eps`/`bb_nfa_cap_open`/`bb_nfa_cap_close` (pure `jmp γ`, byte-identical to `bb_eps`); all 10 `BB_NFA_*` opcodes wired into the `emit_core.c` dispatch (3 → templates, 7 consuming/branching → `bb_stub` placeholder); prototypes in `bb_templates.h`; Makefile RT_PIC_SRCS + explicit `bb_nfa.o` scrip rule. Dead-code-until-`~~`-rewiring (nothing builds a `BB_NFA_*` graph yet); gates unchanged, FACT 0. REMAINING: the 7 consuming/branching templates (CHAR/ANY/CLASS/SPLIT/BOL/EOL/ACCEPT) with the pos/subject/slen register model + char/cset/backtrack bytes + capture block, then the `~~`→`SM_BB_INVOKE` rewiring (behind `RK_NFA_BB=1`). See DESIGN below.
  - **Graph is ready.** `raku_nfa_to_bb` (RK-NFA-1b ✅) already emits the isolated `BB_NFA_*` graph: one `BB_t`/state, γ=out1-node (advance), β=out2-node (SPLIT backtrack only), payload CHAR ival=char / CLASS sval=32-byte cset / CAP ival=group-idx. The 10 templates consume THIS graph.
  - **Spec to reproduce in x86 = `nfa_bt` (raku_nfa_bb.c).** Depth-first backtracker: ACCEPT→return pos; EPS/CAP_*→tail to out1; BOL/EOL→guard pos==0 / pos==slen then out1; CHAR/ANY/CLASS→if `pos<slen && test(subj[pos])` advance pos+1 →out1 else fail; SPLIT→try out1 (γ), on fail try out2 (β). This is EXACTLY the four-port BB model: γ=success-continue, ω=fail/backtrack, β=SPLIT's second arm. Same shape as `BB_ALT`/`BB_PUMP` which already have real MEDIUM_BINARY counter-state dispatch.
  - **Template contract (model on `bb_eps.cpp`, the minimal four-port):** each `bb_nfa_X_str(BB_t*pBB, bb_bin_t&bin)` returns x86 via `IF(MEDIUM_MACRO_DEF/BINARY/TEXT, …)`; `bin = {{site_offsets},{_.lbl_γ_p,_.lbl_β_p,_.lbl_ω_p},{is_rel…}}` declares the port relocation sites; `extern "C" void bb_nfa_X(BB_t*)` calls `bb_emit_asm_result`. Register model (proposed): a callee-saved reg holds `pos` (e.g. r13), another the subject base ptr (r14), another slen (r15d) — set once by the driver α; capture array a malloc'd quad block reached via movabs (mode-3) / @PLT helper (mode-4), NOT a BB_t field (PEERS RULE). char test via `cmp byte [r14+r13], ival`; cset test via `bt`/table lookup against the 32-byte sval blob emitted into rodata (xa_strtab_rodata or a movabs'd const).
  - **Per-opcode byte sketch:** `bb_nfa_char` cmp+je→γ(pos++) / fallthrough→ω; `bb_nfa_any` cmp `\n` + bounds→γ/ω; `bb_nfa_class` 32-byte bitset `bt`→γ/ω; `bb_nfa_eps` `jmp γ` (clone bb_eps); `bb_nfa_bol`/`eol` `test pos`/`cmp pos,slen`→γ/ω; `bb_nfa_cap_open/close` `mov [cap+idx*8], pos` then `jmp γ`; `bb_nfa_split` try γ then β (the existing BB_ALT counter-state slab is the live model); `bb_nfa_accept` set match-end + `jmp` graph-γ.
  - **Driver + entry:** leftmost-unanchored sweep (try each start pos) lives in the α-side of the entry node OR a small `bb_nfa` graph wrapper; mirror `raku_nfa_bb_match`'s `for sp in 0..slen` loop. `BB_PUMP` is the driver kind per the goal's port table.
  - **Dispatch wiring (emit_core.c ~599):** add `case BB_NFA_CHAR: bb_nfa_char(nd); return 0;` … for all 10 (today they hit `default:` "unhandled"). Add the 10 prototypes; add the 10 `.cpp` to the Makefile object list (alongside the other `BB_templates/*.cpp`).
  - **`~~` rewiring:** today `~~` lowers to `SM_CALL_FN raku_match` (C matcher, all 3 modes green via byname). RK-NFA-4 adds an ALTERNATE lowering path: build the graph via `raku_nfa_to_bb` and emit `SM_BB_INVOKE` over it (mirror `lower_raku_iterate_arr` + the `SM_BB_INVOKE` site in `lower_every`). Gate behind a flag first (e.g. reuse `RK_NFA_BB=1`) so default stays on the proven C matcher until all 10 templates are green; flip default last.
  - **Isolation gate every step:** `bash scripts/test_snobol4_pat_rung_suite.sh` must stay M2 19/0 M4 18/1 (no SNOBOL4 pattern template touched), FACT grep 0, GATE-RK4 must not regress from 42/42, GATE-RK3 from 41/42.
  - **Standalone oracle:** the L1-L15 verdicts + captures are already proven by the C matcher (mode-2/3/4 41/41/42); RK-NFA-4's job is byte-for-byte parity of the EMITTED path against those goldens, not new semantics.
- [ ] **RK-NFA-5 — mode-3 native. ⏸ SHELVED 2026-05-29 (see DECISION block above).** `SCRIP_M3_NATIVE=1`; mode-3 already PASSES regex 41/42 CRASH 0 through the C matcher + byname dispatch, so this MOVES `~~` onto the emitted isolated `BB_NFA_*` slab (architectural ladder completion, not a crash-fix); flip default `~~`→BB.
- [ ] **RK-NFA-6..9 → SUPERSEDED by the RK-GRAM ladder below.** The old plan routed subrules `<rule>`→`BB_NFA_SUBCALL` (an NFA-internal opcode). DROPPED per the 2026-05-29 tier-seam decision (locked w/ Lon): keep the NFA slab **leaf-only**; route subrule/rule/grammar backtracking through the **EXISTING** four-port generators (`BB_SUSPEND`/`BB_ALT`/`BB_PUMP`), NOT a new NFA opcode — a `BB_NFA_SUBCALL` would re-implement the backtracking + recursion + Match-tree build the generators already do. `{m,n}`/frugal → RK-GRAM-2; LTM `|`→`BB_NFA_LTM` STAYS Tier-A (declarative/DFA, not backtracking); subrules/grammar/proto/actions → RK-GRAM-3..6. See **Full grammar-feature ladder — RK-GRAM** below.
- [ ] **RK-NFA-CONV (DEFERRED):** collapse `BB_NFA_CHAR/CLASS/ANY/BOL/EOL` ↔ SNOBOL4's `LIT/ANY/LEN/POS/RPOS` pattern opcodes into `BB_MATCH_*` where byte+semantics identical; `SPLIT`+captures stay separate. (Now also tracked as RK-GRAM-6 G6-1.)

## Full grammar-feature ladder — RK-GRAM (the ENTIRE Raku regex + grammar surface)

**⭐ TOP PRIORITY (Lon, 2026-05-29).** Getting the full grammar feature working is the #1 goal now. **Reason:** the grammar surface FLUSHES OUT all the BB kinds. The SM spine is ~99% complete; what's missing for a full all-language back-end development cycle is a COMPLETE collection of BB kinds. Raku grammars exercise the generator/backtracking BBs the hardest (subrule recursion, LTM, choice points), so finishing this ladder gives every back-end (x86/JVM/.NET/JS/WASM) the full BB template set to emit against. Drive RK-GRAM to completion ahead of the other Raku rungs.

**Decision (locked w/ Lon, 2026-05-29): TWO TIERS, ONE SEAM.**

- **Tier A — NFA leaf (single pattern).** One named regex's *body*: literals, classes, anchors, quantifiers, `|` LTM, `||` ordered, in-pattern captures/assertions/adverbs/backrefs. Rides the ISOLATED `BB_NFA_*` family (`nfa_bt` depth-first; `SPLIT.out2` = β backtrack edge). Covers `token` (`:ratchet`, pure forward scan = what an NFA does best), `rule` (`:ratchet` + `:sigspace`), AND the leaf level of `regex` (backtracks via SPLIT). This is the DFA-convertible part and the target of the `BB_MATCH_*` convergence.
- **Tier B — BB-generator grammar structure.** The seam is the **subrule call `<name>`** — per docs.raku.org subrules ARE backtrackable *method calls*. When an outer match fails, the subrule must yield its NEXT match = the four-port β-pump protocol. So subrule / rule-composition / grammar backtracking rides the **EXISTING** generators (`BB_SUSPEND`/`BB_ALT`/`BB_PUMP` — the live Icon substrate; recursive across subrules like Prolog WAM-CP choice points). **A grammar = a namespace of generators; `token TOP` is the entry.**

**Declarator semantics (the whole distinction is two adverbs):** `regex` = `:ratchet` OFF (backtracks) + `:sigspace` OFF · `token` = `:ratchet` ON + `:sigspace` OFF · `rule` = `:ratchet` ON + `:sigspace` ON. `:sigspace` turns significant whitespace into a `<.ws>` subrule call.

**`|` vs `||`:** `|` = declarative **longest-token-match** (parallel, order-independent, picks longest declarative prefix; a `{}` code block terminates a prefix) → Tier-A `BB_NFA_LTM`. `||` = **ordered** (textual order, backtracking) → Tier-B generator alternation. Only `||` and subrule-retry are backtracking; `|` is DFA.

**Isolation gate EVERY rung (unchanged invariant):** `scripts/test_snobol4_pat_rung_suite.sh` stays M2 19/0 M4 18/1 (no SNOBOL4 pattern template touched); FACT grep 0; GATE-RK4 no regress; GATE-RK3 no regress; smoke 5/5/5/13/5 HOLD.

**Test corpus note:** the corpus has NO grammar/subrule tests today (the 6 regex tests are PLAIN single-pattern). Each RK-GRAM rung adds `test/raku/*.{raku,expected}` probes; mode-2 (GATE-RK) and mode-4 (GATE-RK4) byte-identical is the per-rung gate (Prolog GATE-4 pattern).

### Phase 1 — NFA leaf, core single-pattern (RK-NFA-1..5) — ⏸ SHELVED 2026-05-29 (leaf emission; see DECISION block)
Tracked in the RK-NFA rungs above (1a–1e ✅, 4 SCAFFOLD ✅). **The mode-2/3/4 leaf MATCHER is GREEN via the C path** (41/42, 42/42, 41/42); only the BB *emission* (G1-1..3) is shelved as ceremony. Restated here as the ladder's first phase:
- [ ] **G1-1** RK-NFA-4 — **S1✅ + S2✅ + S3 (L1 atom)✅ — `/x/` GREEN in mode-4** (Opus 4.8, 2026-05-29). **S1** (one4all `c8aeb90d`): gated `~~`→`SM_BB_INVOKE` over the isolated BB_NFA_* graph, default OFF (`RK_NFA_BB`). **S2+S3** (one4all `57ec5cea`): first runnable atom L1 `/x/`~"x" green in mode-4 (MEDIUM_TEXT) via the EMITTED isolated slab — byte-identical to the C matcher (match / miss / leftmost-offset `"abcx"`→pos 3). The contract's `walk_bb_flat` S2 was WRONG; the node-keyed NFA walker lives in the **`sm_bb_switch.cpp` SM_BB_INVOKE MEDIUM_TEXT arm** (subject-pop-from-vstack + leftmost sweep + r12/r13/r14/r15 save/restore, per-node label wiring), with leaf bytes in `bb_nfa.cpp`. Default gates HOLD (m2 41/42, m4 42/42, m3 41/42 CRASH 0, smoke 5/5/5/13/5, SNOBOL4 iso M2 19/0 M4 18/1, FACT 0). LEAVES LANDED: `bb_nfa_char`/`accept` (`57ec5cea`), `bb_nfa_any`/`bol`/`eol` (`a0346ec5`), **`bb_nfa_class` 32-byte cset bitset (`037be2ce`, Opus 4.8, 2026-05-29 — rodata-embedded blob, `bt edx,eax` mirroring raku_cc_test; verified byte-identical to C-matcher on `[a-z]`/`[A-Z]`/`\d`/`\s` incl. leftmost sweep + class-miss)**. REMAINING for G1-1: **`bb_nfa_split`** (the `*`/`+`/`?`/`||` fork). ⚠️ **ARCHITECTURE CORRECTION (Lon, 2026-05-29):** do NOT add a backtrack stack — BBs ALREADY backtrack, structurally, through the four-port wiring. The earlier \"explicit backtrack-stack\" note (and the `nfa_text_box` linear walker it implied) was WRONG and a foreign pattern. The correct model: SPLIT is a CHOICE POINT exactly like `BB_PAT_ALT` / `BB_CHOICE` / `BB_PL_ALT`, and the NFA graph should be driven by the canonical **`walk_bb_flat` + `flat_drive_*`** machinery (`emit_bb.c`), NOT the bespoke `nfa_text_box` walker in `sm_bb_invoke.cpp`. In that machinery, backtracking IS the port wiring: a downstream leaf's ω is wired to the β (retry) of the nearest upstream choice point; that choice point's β advances to its next alternative; its last alternative's ω propagates to the outer ω. The chain of ω→β edges through the graph *is* the choice-point stack, realized as wiring (see `flat_drive_alt`: arm.γ→outer-γ, arm[i].ω→arm[i+1] via the alt's β; and `flat_drive_pl_seq`: \"fail → redo predecessor\"). Each box also holds its own resume cursor (`pBB->counter`) for α/β re-entry — that per-box state replaces any global stack (see `bb_alt.cpp` MEDIUM_BINARY). PLAN for the redesign: (1) a `flat_drive_nfa_split` in `emit_bb.c` that mints labels and wires out1's ω → SPLIT's β, SPLIT's β → out2, out2's ω → outer ω; (2) route the leaf NFA kinds (CHAR/CLASS/ANY/BOL/EOL/CAP_*/EPS/ACCEPT) through `walk_bb_flat`'s `FILL` path (their existing four-port `bb_nfa_*` templates already emit γ/ω/β bodies); (3) drive the whole NFA graph (incl. the leftmost-unanchored sweep) via `walk_bb_flat` instead of `nfa_text_box`. The already-green leaves keep their template bytes; only the WALKER changes from linear to structural. Byte-exact x86 against the C-matcher oracle, crash-on-wrong-byte → fresh full session. Then captures (RK-NFA-3, L13-L15), mode-3 BINARY (RK-NFA-5), flip default (G1-3). Repro: `RK_NFA_BB=1 bash scripts/run_raku_via_x86_backend.sh FILE.raku`.
- [ ] **G1-2** RK-NFA-5 — `~~` onto the emitted slab in mode-3 native. ⏸ SHELVED 2026-05-29.
- [ ] **G1-3** mode-4 `~~` default flip to BB once G1-1+G1-2 green (retire the C-matcher fallback behind `RK_NFA_BB`). ⏸ SHELVED 2026-05-29.

### Phase 2 — NFA leaf, FULL single-pattern surface (RK-GRAM-2, Tier A)
All lower to the `BB_NFA_*` slab; most are compile-time cset/loop shaping, NOT new opcodes.
- [ ] **G2-1 quantifiers** — `**{m,n}`, `**{m..n}`, `**{m..*}`, `**N`; greedy default.
  - [ ] a. counted SPLIT loop with counter-state (model on `bb_pump` MEDIUM_BINARY).
  - [ ] b. separator quantifier `<thing>+ % <sep>` / `%%` (loop modifier).
- [ ] **G2-2 frugal** — `*?` `+?` `??` `**{m,n}?` (SPLIT preference flips: try-fewer-first).
- [ ] **G2-3 grouping** — `[ … ]` non-capturing bracket (structural EPS); `( … )` capturing already at NFA CAP_OPEN/CLOSE.
- [ ] **G2-4 anchors + boundaries** — `^^`/`$$` (line), `<<`/`>>` (= `«`/`»`, word), `<|w>`/`<?wb>`. (`^`/`$` already BOL/EOL.)
- [ ] **G2-5 predefined classes** — `\d \w \s \h \v \t \n \r` + negations `\D \W \S \H \V` → CLASS csets at compile (no new opcode).
- [ ] **G2-6 enumerated classes** — `<[a..z]>`, `<-[ … ]>` negated, `<[…]+[…]>` / `<+[…]-[…]>` set algebra → cset at compile; unicode props (`<:Letter>`) → G6-4.
- [ ] **G2-7 lookahead** — `<?before p>` `<!before p>` `<?after p>` `<!after p>`: zero-width sub-match (run sub-NFA, restore pos, verdict only) → NEW `BB_NFA_ASSERT`.
- [ ] **G2-8 boolean / code assertions** — `<?{ code }>` `<!{ code }>` zero-width predicate (lowered Raku expr → call into value layer; mode-4 @PLT) → NEW `BB_NFA_PRED`; `<?>`/`<!>` constants.
- [ ] **G2-9 conjunction** — `&`/`&&` (all alternatives match the same span; longest governs). Leaf form.
- [ ] **G2-10 in-pattern adverbs** — `:i`/`:ignorecase` (cset case-fold at compile), scoped `:s`/`:sigspace`, scoped `:r`/`:ratchet`; `:m`/`:ignoremark` → G6-4. Scope = remainder of the group.
- [ ] **G2-11 backrefs (in-pattern)** — `$0`/`$1`/`$<name>` USED inside the pattern (re-match captured text) → NEW `BB_NFA_BACKREF` (read cap slot, literal-compare run).
- [ ] **G2-12 interpolation** — `$var` (literal), `<$var>` / `<{ code }>` dynamic subpattern, `@array` (LTM over elements). Dynamic/`@array` build the NFA at match time → later sub-rung.
- [ ] **G2-13 capture markers** — `<( … )>` keep-delimiters (set match start/end within a larger pattern).

### Phase 3 — BB-generator grammar STRUCTURE (RK-GRAM-3, Tier B) — THE SEAM
- [ ] **G3-1 named-regex decl** — `my regex/token/rule name { … }` lowers each to a four-port BB **generator** (NOT a free fn) whose body is the Tier-A NFA slab. `token` = ratchet generator (β never re-pumps past first match); `regex` = backtracking generator (β re-pumps); `rule` = token + `:sigspace`. **⏳ FIRST MILESTONE DONE (one4all `dd52b2bf`): `Grammar.parse($s)` runs TOP, mode-2/3/4 green (see top watermark). NOT yet on a BB generator — rides the C `raku_nfa_*` engine; the BB-generator form (sub-steps a/b) + subrule composition is G3-2.**
  - [ ] a. `lower_raku_named_regex` → `SM_BB_INVOKE` over the generator graph.
  - [ ] b. `:sigspace` rewrite: insert a `<.ws>` generator at each significant boundary (rule only).
  - **G3-1 EXECUTION PLAN (measured 2026-05-29, Opus 4.8, one4all `76719461` — facts so the next session executes, not explores).** The PARSE layer is done (TT_GRAMMAR_DECL{ TT_REGEX_DECL(v.ival 0/1/2)... }, bodies as opaque LIT_REGEX child c[1]). Today `lower.c` reports `unhandled AST kinds: TT_GRAMMAR_DECL` and skips it (graceful, exit 0; a grammar coexists with runnable code — verified `say;grammar;say` prints both lines mode-2 + mode-4). MODEL = `lower_class_decl` (`src/lower/lower.c:1987`) + `lower_class_prescan` (`:2952`, walks top-level stmts for TT_CLASS_DECL, registers each method via `lower_raku_meth_register` BEFORE skeletons) + dispatch (`:2641 case TT_CLASS_DECL`). A grammar is the same shape: a namespace whose members are named generators instead of methods. REUSE ALREADY-LANDED: `raku_nfa_build(const char*pattern)` (`raku_re.c:299`, decl in `raku_re.h:46`) parses a body string → `Raku_nfa*`; `raku_nfa_to_bb(Raku_nfa*)` (`raku_nfa_bb.c:90`, RK-NFA-1b ✅) → isolated `BB_NFA_*` `BB_graph_t*`. So a TT_REGEX_DECL body → generator graph is a two-call pipeline that EXISTS. STEPS: (1) `lower_grammar_prescan` mirroring `lower_class_prescan` — register each `Grammar::rule` name (rename c[0]->v.sval to `Grammar__rule` like methods) into a grammar-rule table keyed for subrule resolution at G3-2. (2) `lower_grammar_decl` mirroring `lower_class_decl` — for each TT_REGEX_DECL: `raku_nfa_build(c[1]->v.sval)` then `raku_nfa_to_bb`; register the graph at runtime via an SM-level call (model the `RECORD_REGISTER` idempotent-handler pattern at `:2025` so BOTH mode-2 sm_interp and mode-4 rt_call register before any invocation — a lower-time-only registry is empty in the mode-4 child process, see the RK-CLASS comment). flavor (v.ival): token=ratchet (β no re-pump), regex=backtrack (β re-pumps), rule=token+`:sigspace`. (3) dispatch `case TT_GRAMMAR_DECL: lower_grammar_decl(t); SM_emit(g_p, SM_PUSH_NULL); return;` next to `:2641`; add `if (has_raku) lower_grammar_prescan(prog)` next to `:3005`. ⚠️ TESTABILITY COUPLING (the reason this is not independently shippable): a lowered generator is only OBSERVABLE once something INVOKES it. The smallest end-to-end test needs an invocation path — either G3-5 `Grammar.parse($s)` entering `TOP`, or a `~~`/`&name` reference. So G3-1 must land WITH a minimal invocation (recommend the `TOP` entry: `G.parse("...")` → enter the TOP generator → return Match/Nil), and the first `test/raku/*.{raku,expected}` grammar probe attaches there (Prolog GATE-4 pattern, mode-2 + mode-4 byte-identical). Until then the parse fixture `test/raku/rk_grammar_parse.raku` stays `.expected`-less (run-gates SKIP). CAVEAT (from the shelving decision): re-confirm at the seam that the leaf `BB_NFA_*` graph is the right substrate before relying on it — the GENERATORS (`BB_SUSPEND`/`BB_ALT`/`BB_PUMP`) are the load-bearing kinds, the leaf graph may be leaf-costume.
- [ ] **G3-2 subrule call** — `<name>` inside a pattern → β-pumpable generator invocation (**THE SEAM**). Forms: `<name>` (capturing), `<.name>` (suppress), `<&name>` (lexical), `<name=other>` (alias), `<Pkg::name>` (qualified). **⏳ FIRST MILESTONE DONE (one4all `aa58850a`): bare `<name>` composes via non-recursive registry expansion, mode-2/3/4 green (see top watermark). NOT yet on BB generators; non-recursive only; capturing-group wrap; no Match tree. The BB-generator form (recursion + backtrack-across-calls) is the load-bearing tier still to do.**
  - [ ] a. plain `<name>` — invoke + capture-by-name into the Match tree (G5).
  - [ ] b. `<.name>` — structure only, no capture.
  - [ ] c. retry — outer fail re-enters the subrule's β for its next match (recursive choice point; mirror the Prolog WAM-CP frame-reuse model).

  **⛔ DESIGN NOTE — how Rakudo/NQP actually does it (read 2026-05-29 from `Raku/nqp` `src/QRegex/P6Regex/` + the cursor mechanics in Raku old-issue-tracker #6120; recorded so the BB tier is not designed blind).** Rakudo compiles every `regex`/`token`/`rule` to a **regexsub** — a method on a **`Cursor`** object. A Cursor holds `pos`, the captures, and a **backtrack stack (`bstack`)**. A subrule call `<foo>` invokes foo's regexsub, which returns a Cursor; on success the outer continues from the sub-Cursor's `pos`. On BACKTRACK the engine **unwinds via the Cursor's `$!restart` function pointer** and the bstack — `cursor_more`/`cursor_next` re-enter a regexsub to yield its **NEXT** match (NQP issue #6120: "skip calling regex_mast … only unwind the cursor stack based on the backtrack stack"; `cursor_more` "calls `$!regexsub` with … a new cursor"). **THIS IS THE FOUR-PORT GENERATOR, 1:1:** Cursor ≡ (pos + captures) match state; regexsub ≡ a generator; `cursor_more`/`$!restart` ≡ the **β (retry) port** ("give me your next match"); first call ≡ **α**; a yielded match ≡ **γ**; exhaustion ≡ **ω**. So the SEAM (`<name>`) = invoke a generator, and outer failure pumps its β — precisely `BB_SUSPEND`/`BB_ALT`/`BB_PUMP`. This CONFIRMS the watermark's "BBs relocate the control stack" thesis: NQP keeps an explicit bstack + restart pointers; the BB model turns the choice-point chain into ω→β WIRING + per-box resume cursors — BUT recursion (foo calls foo) still needs a STACK of Cursors (resume cursors), because one box's single `counter` cannot hold N call depths. That is the one piece registry-expansion (G3-2 milestone) cannot do and the BB generator must: a per-invocation Cursor frame (mirror Prolog WAM-CP frame reuse). **Declarator semantics confirmed from the NQP grammar:** `token` = `:ratchet` (commit, no intra-token backtrack), `regex` = full backtrack, `rule` = token + `:sigspace`; `:sigspace` inserts `<.ws>` at significant boundaries where `token ws { [ \s | '#' \N* ]* }` (optional whitespace/comments). `|` = LTM (separate NFA, longest declarative prefix); `||` = ordered/bstack backtrack. **BB-TIER PLAN (informed):** (1) one four-port generator per registered rule (the regexsub); α = fresh Cursor at pos, γ = yield a match (advance outer pos), β = `cursor_more` (next match), ω = exhausted. (2) `<name>` lowers to invoking that generator and wiring its ω→ the enclosing choice point's β (the relocation). (3) a Cursor-frame stack (heap, per invocation) carries pos+captures across recursive calls — the BB analog of NQP's Cursor chain / Prolog's WAM-CP frames. (4) the C-engine milestones (G3-1/G3-2) are the GOLDEN ORACLE the emitted BB form is diffed against. Build it as a fresh full-budget session; the leaf `BB_NFA_*` slab stays the char-level tier, the generators are the rule/subrule tier.
- [ ] **G3-3 subrule args** — `<name(expr, …)>` (e.g. `token start($c) { $c+ }`); thread args through the generator's α as bound params.
- [ ] **G3-4 grammar decl** — `grammar G { … }` = namespace of named-regex generators (subclass of `Grammar is Match`); resolve `<name>` against the method table.
  - [ ] a. inheritance `grammar G is Base` / roles `does` — MRO over generator tables.
- [ ] **G3-5 entry points** — `G.parse($s)` enters `TOP` (anchored whole-string); `G.subparse` (unanchored prefix); `:rule`/`:pos`/`:args` named args. Top driver = anchored variant of the NFA leftmost sweep.
- [ ] **G3-6 default `<ws>`** — built-in whitespace token, grammar-overridable `token ws { … }`; wire `rule` sigspace to the in-scope `ws`.

### Phase 4 — LTM + proto dispatch (RK-GRAM-4)
- [ ] **G4-1 grammar-level LTM** — `|` across subrule alternatives picks the longest declarative prefix (NOT ordered). LTM dispatcher over the generator set; `BB_NFA_LTM` builds the prefix DFA, the winning branch then runs as a generator.
- [ ] **G4-2 proto / multi** — `proto token X {*}` + `multi token X:sym<foo> { … }`; `<sym>` literal; dispatch by LTM over the `:sym` prefixes.
- [ ] **G4-3 `||` at grammar level** — ordered alternation across subrules (textual order, full backtrack across the generator tree).

### Phase 5 — actions + Match tree + captures (RK-GRAM-5)
- [ ] **G5-1 Match object** — `$/` as the match TREE built post-order as generators succeed; positional `$0/$1` (= `$/[0]`) and named `$<name>` (= `$/<name>`) slices. (RK-NFA-3 captured FLAT; this builds the tree.)
- [ ] **G5-2 action methods** — `:actions` object; per successful named match call `method <name>($/)` in post-order (sub-match actions fire before the caller's).
- [ ] **G5-3 make / made** — `make X` stashes `$/.made`; outer action reads `.made`; `TOP` action returns the built AST.
- [ ] **G5-4 aliased captures** — `<key=identifier>` / numbered alias capture into the tree.

### Phase 6 — convergence + control + adverbs (RK-GRAM-6, DEFERRED)
- [ ] **G6-1 `BB_MATCH_*` convergence** — = RK-NFA-CONV. Collapse `BB_NFA_{CHAR,CLASS,ANY,BOL,EOL}` ↔ SNOBOL4 `LIT/ANY/LEN/POS/RPOS` where byte+semantics identical; SPLIT + captures stay separate.
- [ ] **G6-2 backtrack control** — `:` (ratchet point), `::` (fail group), `:::` (fail rule), `<commit>`, `<cut>`.
- [ ] **G6-3 match adverbs** — `:g`/`:global` (partial via `raku_match_global`), `:ov`/`:overlap`, `:ex`/`:exhaustive`, `:nth`, `:x`, `:c`/`:continue` on `~~`/`.match`.
- [ ] **G6-4 unicode props** — `<:Letter>`, `<:Nd>`, `:ignoremark`/`:m`; full property tables.
- [ ] **G6-5 `:Perl5`/`:P5`** — Perl5-compat regex mode (separate compile path; very deferred).

**Test ladder L1-L15** (GATE-NFA-O = mode-2 `raku_nfa_bb_match` verdict == `raku_nfa_exec` verdict, then `.expected`): L1 `/x/`~"x"; L2 `/.*/`~""; L3 `/.*/`~"xyz"; L4 `/[a-z]+/`~"hello"; L5 `/[a-z]+/`~"123"(no); L6 `/\d+/`~"abc123"; L7 `/\d+/`~"abc"(no); L8 `/a||b/`~"cat"; L9 `/a||b/`~"dog"(no); L10 `/^x$/`~"x"; L11 `/^x$/`~"xy"(no); L12 `/^x$/`~""(no); L13 `/([A-Za-z]+)/`→$0; L14 two caps; L15 `<word>(...)`. **L1-L12 verdict-green standalone; L13-L15 at RK-NFA-3.** Isolation guard every rung — run the SNOBOL4 cross-language regression suite (`scripts/test_snobol4_pat_rung_suite.sh`, a SNOBOL4-owned artifact; the only place a SNOBOL4 `pat` name appears, intentionally, as the thing this Raku ladder must NOT perturb) — it must stay M2 19/0 M4 18/1.
- [x] **RK-BB-4 mode-2 ✅** (4a constructors + 4b infix, see completed rungs). **Full `rk_junctions` probe PASS mode-2.** Q9-Q12 ANSWERED by Lon (2026-05-29): **Q9** reuse existing kinds; break out new SM/BB opcodes ONLY if language-specific behavior diverges. **Q10** build on `BB_ALT` (live substrate Icon uses); split later if needed. **Q11** substrate-first. **Q12** tagged-string rep. Substrate proven: `BB_ALT` mode-2 is a complete n-ary alternation engine (empirically `x=(1|2|3)`→hit, `x=(7|8|9)`→miss, `every write(10|20|30)`→10/20/30); `BB_ALT` mode-4 `MEDIUM_BINARY` is a real counter-state dispatch slab (NOT a stub — the probe header's stale assumptions #3/#4 refer to the orphan `BB_ALTERNATE`, and only the `MEDIUM_TEXT` arm is a passthrough). Junction VALUE rep is the tagged string; the boolean collapse currently lives in mode-2 `SM_ACOMP`/`SM_LCOMP` (NOT yet on `BB_ALT`).
- [x] **RK-BB-4c (mode-4 junctions) ✅** (Opus 4.8, 2026-05-29, one4all `216f22cd`). Route (i): junction collapse added to shared `rt_acomp`/`rt_lcomp` (`src/runtime/rt/rt.c`), mirroring the mode-2 `SM_ACOMP`/`SM_LCOMP` interpreter cases. The `SM_ACOMP`/`SM_LCOMP` x86 templates already emit `mov edi,<op>; call rt_acomp`/`rt_lcomp` — the work lives in those runtime helpers, so this is FACT-clean (no template byte change). When a popped operand is `rk_junction_is()` true → `rk_junction_collapse(scalar,jct,op,numeric)` (1 acomp / 0 lcomp); push scalar+`LAST_OK=1` on hit else FAIL. `rk_junctions` mode-4 GREEN. Mode-3 junctions correct too (same helpers) but dormant (MODE3-DISPATCH-GAP).
- [x] **RK-BB-4d edges — precedence + nesting ✅** (Opus 4.8, 2026-05-29, one4all `0a5352e3`+`1652aeb9`). (2) PRECEDENCE: new `jct_expr` grammar tier (`raku.y`) makes infix `|`/`&` bind tighter than comparison (real Raku); `$x == 1|2|5` → `$x == any(1,2,5)`. Comparisons take `jct_expr` operands; parser regenerated, net-zero new conflicts. (1) NESTED MIXED-FLAVOR: SOH-leak fixed via EOT(`\x04`)-terminated junction rep — builder appends `\x04`; `rk_junction_collapse` scans scalars to SOH-or-EOT and skips nested `\x03…\x04` spans by depth count, recursing on the opaque span. `50&(50|60)` etc. now correct. Probes `rk_junction_prec`, `rk_junction_nest` added. (3) var round-trip + string-relop collapse already worked. REMAINING sliver: `^`(one) infix not lexed; only `one(...)` constructor.
- [x] **RK-BB-5.0..5.3 ✅** (Opus 4.8, 2026-05-29, one4all `36e41ed6`). List/array Seq consumers landed as pure value helpers in `raku_builtins_byname.c` (flatten SOH-array args into segments; no emitted x86, FACT-clean; reachable mode-2 `sm_interp` + mode-4 `rt_call`; byte-identical across modes). **5.0 `reverse`** (`a4bc02d4`) eager-drain reorderer; `for reverse(...)` rides the existing `for CALL(...)→$v` materialization branch. **5.1 `unique`+`sum`** (`8b10f978`) dedup-first-occurrence + numeric fold (INTVAL all-integral else REALVAL). **5.2 `join`** (`ed321adc`) `join(SEP,LIST)` fold-to-string; composes with reverse. **5.x array-arg coverage** (`f9425b68`, test-only) — confirmed reverse/unique/sum/join all work on push-built `@arrays`. **5.3 comma-list array initializer `my @a = e1,e2,...`** (`36e41ed6`) — the REAL gap behind `my @a=1,2,3` parse errors (NOT @-args, which already worked). Two `raku.y` productions (untyped+typed) build `ASSIGN(@a, __rk_arr(...))`; lookahead `;`(single-expr) vs `,`(comma-list) is a clean LALR split → **net-zero new conflicts (still 30 s/r)**; parser regenerated via `scripts/regenerate_parser_and_lexer_from_sources.sh` recipe (bison 3.8.2). New `__rk_arr` builtin packs args into an in-order SOH-array. Probes: rk_reverse, rk_unique_sum, rk_join, rk_seq_consumers_arr, rk_array_literal. **GATE-RK mode-2 28→33/40, GATE-RK4 mode-4 29→34/40; smoke 5/5, siblings icon/prolog/snobol4/snocone 5/5/13/5, FACT 0, all commits, no regressions.** DEFERRED: parenthesized `my @a=(1,2,3)` (list-atom, conflict-prone); `.method(N)` forms (`.tail`/`.head`/`.reverse`) need method-call-with-args parsing; `zip`/`cross` multi-Seq drivers need a nested-tuple representation.
- [x] **RK-BB-5.4a (`.method` list-method forms) ✅** (Opus 4.8, 2026-05-29). `.reverse`/`.unique`/`.sum`/`.elems`/`.head(N)`/`.tail(N)` routed from `TT_METHCALL` (after class static-resolution miss) and `TT_FIELD` (bare postfix) to the list-context value helpers, ahead of the class-oriented `raku_mcall`/`FIELD_GET` fallbacks (`raku_is_listmeth` whitelist, gated `g_lang==LANG_RAKU`). New `head`/`tail` value builtins in `raku_builtins_byname.c` (trailing arg = count N; bare form defaults N=1) modelled on `reverse`. Also widened the `for`-CALL materialise guard (`lower_every`) to accept `TT_METHCALL`/`TT_FIELD` list-method invocants (`raku_methform_listmeth`), so `for @a.reverse -> $x`/`for @a.head(N) -> $x` materialise-then-iterate (previously ran away — guard keyed only on `TT_FNC`). Pure value helpers, no emitted x86 (FACT-clean); byte-identical mode-2/mode-4. Class methods/fields untouched (rk_class26 unchanged). Probe `rk_listmeth`. Commits `dbb3d15f` (postfix) + `91bfae91` (for-form). DEFERRED: `.join` (invocant/arg order swapped vs free-fn `join`, which already works).
- [x] **RK-BB-5.4b (parenthesized array literal) ✅** (Opus 4.8, 2026-05-29, `56a30122`). `my @a = (e1, e2, ...)` via two initializer-only `raku.y` productions (untyped + typed) mirroring the 5.3 bare comma-list: `KW_MY [IDENT] VAR_ARRAY '=' '(' expr ',' arg_list ')' ';'` → `ASSIGN(@a, __rk_arr(...))`. Restricting the paren-list to the **initializer RHS** (NOT a general atom) keeps it **NET-ZERO new conflicts (still 30 s/r)** — a general-atom `'(' expr ',' arg_list ')'` form added +2 (method-chain/hash-subscript interactions) and was reverted. Single-element paren `(7)` stays scalar via the unchanged `'(' expr ')'`; bare comma-list + scalar paren coexist. Parser regenerated (bison 3.8.2). Probe `rk_paren_array`.
- [ ] **RK-BB-5.4c (`zip`/`cross`) — DEFERRED, own session** — multi-Seq drivers where each output element is itself a list, so it needs a **nested-tuple representation** (STX-within-SOH or similar) that `for`/`say`/`.elems` consumers must understand. NOT a pure value helper (broad blast radius); the goal groups these as "(later)". Recommend a fresh session with full budget.

## RK-SMARTMATCH — unify `when` + `~~` onto ONE `ACCEPTS` seam

**Idea (Claude Opus 4.8, 2026-05-29).** In real Raku `when X` ≡ `if $_ ~~ X`, and `~~` is the
`Mu.ACCEPTS` protocol (corroborated in `rakudo-main/src/core.c/{Junction,Match}.rakumod` +
`src/Raku/Grammar.nqp`). SCRIP today has them as **two divergent narrow paths and no `ACCEPTS`
seam**: `~~` (`lower.c` `TT_SMATCH` ~2528) is hardwired to `raku_match`/`raku_match_global`/
`raku_subst` (regex only); `when` (the RK-GIVEN if-chain, `lower.c` ~1499-1536) tests each arm with
`SM_ACOMP`(EQ, numeric) / `SM_LCOMP`(LEQ, string-literal). One `ACCEPTS` dispatch routing BOTH would
light up a whole family at once: `when /re/`, `when 1..10`, `when Int`, `when *.even`, `when any(...)`,
and the matching `$x ~~ …` forms. FACT-clean (value helper, no template bytes; behavior in lowering).

### ⛔ MEASURED 2026-05-29 (Opus 4.8, one4all `a062f28b`) — facts so the next session executes

Probed mode-2 to find the REAL starting rung (do not re-discover):

- `when any(1,2,3)` **ALREADY WORKS** — `say` prints `in-set`. The RK-BB-4a/4c junction guard in
  `SM_ACOMP`/`rt_acomp` fires when the arm pushes the junction value; `topic == any-member` collapses
  correctly as a side-effect. **Junction arms are DONE; do not touch them.**
- `when /ell/` → **PARSE ERROR** (line of the `when`). The lexer does NOT lex `/…/` as a regex after
  `when` (the `raku_after_smatch` regex-lex flag is set by `~~`, not by `when`/`given`). So
  `when /re/` is a **FRONTEND gap, not a lowering gap.**
- `$x ~~ 5` → **PARSE ERROR**. The `~~` lexer path forces a regex RHS, so a non-regex RHS (`5`,
  `1..10`, `Int`) won't parse. `~~`-with-general-RHS is **also a FRONTEND gap.**

**Conclusion:** the lowering reroute is the EASY half; the gating work is the lexer/parser. Stage it
so each rung is independently green (no broken commits). `~~`-regex and `when`-literal/junction paths
must stay byte-identical until the very last flip.

### Incremental rungs (each independently green; gate ladder below every rung)

- [x] **SM-0 runtime seam (DEAD CODE, cannot regress) ✅** (Opus 4.8, 2026-05-30, one4all `e6f8b532`). Added `raku_accepts(topic, matcher)` to
      `raku_builtins_byname.c` (reachable all 3 modes via the existing `raku_try_call_builtin_by_name`
      table — same seam RK-NFA-1e used). Dispatch by matcher representation, REUSING proven helpers:
      Junction tagged-string (`s[0]==0x03`) → `rk_junction_collapse(topic,jct,EQ)` (numeric mode keyed
      on topic-is-number); else the `when`-literal base case — numeric eq when BOTH topic+matcher are
      numbers (`to_real`), else string eq (`strcmp==0`, the SNOBOL4-LEQ semantics the `when` string-arm
      uses). Hit→`INTVAL(1)`, miss→`FAILDESCR` (the verdict convention `raku_match` uses, so the SM-2
      `JUMP_F` arm guard consumes it unchanged). Regex arm stays on the SM-1 direct `raku_match` path
      (a bare `/re/` RHS never reaches here per the SM-1 plan); Range/Type/Callable DEFERRED to SM-4.
      NOT wired to any lowering (grep-verified zero callers outside its own file) → zero behavior change.
      ALL GATES BYTE-IDENTICAL to baseline: GATE-RK m2 45/46, GATE-RK4 m4 46/46, GATE-RK3 m3 45/46
      CRASH 0, smoke 5/5/5/13/5, SNOBOL4 iso M2 19/0 M4 18/1, FACT 0, build clean.
- [ ] **SM-1 `~~` reroute, regex-preserving.** In `TT_SMATCH` `match` flavor: keep `raku_match` DIRECT
      when `c[1]` is a bare regex literal (zero regex regression — verify `--dump-sm` unchanged for
      `rk_re*`/`rk_regex23`); only a NON-regex RHS routes to `raku_accepts`. NOTE: today no non-regex
      RHS can even reach here (SM-3 frontend unblocks that), so SM-1 is an inert-but-correct reroute
      landed ahead of the frontend — keeps the two rungs separable.
- [x] **SM-1 `~~` reroute, regex-preserving ✅** (Opus 4.8, 2026-05-30, one4all `7bb603a8`). In
      `TT_SMATCH` `match` flavor, added `rhs_non_regex` gate before the `const char *fn` dispatch:
      if `strcmp(flavor,"match")==0 && c[1]->t != TT_QLIT` → lower topic + arm + emit
      `SM_CALL_FN raku_accepts, 2; return`. A regex-literal RHS is always `TT_QLIT` (from the
      `LIT_REGEX → leaf_sval(TT_QLIT,pat)` parser action, line 505 `raku.y`), so the intercept
      is inert today — the lexer still forces `LIT_REGEX` for every `~~` RHS, `rhs_non_regex`
      is always 0, and `--dump-sm` is byte-identical for all 6 regex/smatch corpus files
      (verified grep: zero `raku_accepts` in any SM dump). Becomes live when SM-3 adds a
      general-expression `~~` RHS production. subst/match_global stay on direct helpers
      unconditionally. ALL GATES BYTE-IDENTICAL to baseline: GATE-RK m2 45/46, GATE-RK4 m4
      46/46, GATE-RK3 m3 45/46 CRASH 0, smoke 5/5/5/13/5, SNOBOL4 iso M2 19/0 M4 18/1, FACT 0.
- [ ] **SM-2 `when` reroute, literal+junction-preserving.** Replace the per-arm `SM_ACOMP`/`SM_LCOMP`
      with `PUSH topic; lower(arm); SM_CALL_FN raku_accepts,2; JUMP_F`. The literal base case must
      stay byte-equivalent in OUTPUT (eq), and the junction case must still collapse (now via
      `raku_accepts` instead of the ACOMP guard — re-verify `rk_given`/`rk_given18`/`rk_junctions`).
      Gate: GATE-RK + GATE-RK4 + GATE-RK3 hold; no new probe yet (behavior identical on existing corpus).
- [ ] **SM-3 FRONTEND — own session, regen required.** (a) lexer: arm the regex-lex flag after
      `when`/`given`-`when` so `when /re/` lexes a `LIT_REGEX` arm; (b) `~~`: allow a general expression
      RHS (only force regex-lex when the next non-space char is `/`). Regenerate parser+lexer
      (`scripts/regenerate_parser_and_lexer_from_sources.sh`, bison 3.8.2); **bison s/r conflict count
      must not rise** (currently 30). This is the high-risk rung — budget a full session; do NOT
      combine with SM-0..2.
- [ ] **SM-4 widen `raku_accepts`: Range / Type / Callable arms.** PREREQ CHECK FIRST: does SCRIP have
      a Range VALUE (vs the `BB_TO_BY` generator) and a Type/Callable value kind? If not, add the
      minimal value tag(s) before wiring. Range → min≤topic≤max (reuse BB_TO_BY bound logic);
      Type → isa/type-name compare; Callable → call matcher(topic) + `.Bool`.
- [ ] **SM-5 probes + flip.** Add `rk_smartmatch_when.{raku,expected}` (when over regex/range/type/
      junction/callable + literal default) and `rk_smartmatch_op.{raku,expected}` (`$x ~~` each form),
      mode-2 == mode-4 byte-identical (Prolog GATE-4 pattern). This is the rung that proves the feature.

**Gate ladder (every rung):** GATE-RK + GATE-RK4 + GATE-RK3 hold/improve; smoke 5/5/5/13/5;
SNOBOL4 iso M2 19/0 M4 18/1; FACT 0; bison conflicts unchanged (until SM-3, which must stay 30).

**Risk register:** (1) SM-3 lexer flag interaction with the existing `~~` regex path is the chief
regression vector — test `$x ~~ /re/` still lexes as regex after the change. (2) `raku_accepts` arg
order must match the byname pre-eval convention (args[] pre-evaluated, var identity gone — see the
RK-NFA-1e subst write-back note for the same gotcha). (3) Keep the ACOMP junction guard until SM-2 is
proven, then decide whether to retire it (it also serves bare `$x == any(...)`, so likely KEEP).

## mode-2 fixes (non-ladder, this session)

- **gather mode-2** (RK-M2-GATHER ✅) and **`SM_ACOMP` string coercion** (RK-M2-ACOMP ✅) — see completed rungs. Net with junctions: GATE-RK mode-2 **23→26/33**.
- **`rk_stdio39` mode-2 FAIL is a test-fidelity issue, NOT a bug** — the `--interp` harness captures stdout only, but `rk_stdio39.expected` lists `stderr ok` as line 3, encoding `$*STDERR→fd 1`. Mode-2 correctly routes `$*STDERR` to fd 2 (real Raku); mode-4 only "passes" by mis-routing stderr to stdout. Lon's call whether to fix the golden or accept the mode-2/mode-4 divergence.

## Rung methodology

Per rung: (1) lower the Raku construct to the shared BB kind via `lower_raku_*` (parallel `lower_icn_*`); (2) confirm existing `bb_<kind>.cpp` covers it; (3) only if semantics differ, **extend the lowering** — never the template; (4) run GATE-RK4 + GATE-RK + GATE-RK3 + smoke. Commit when goldens match and nothing regresses.

## Test corpus — REUSE

`test/raku/*.{raku,expected}` (33 cases). Job is mode-4 conformance (Prolog GATE-4 pattern). Add NEW flat files only for laziness probes the eager suite can't express.

## Mode-3 (`--run`)

**2026-05-28 Lon directive (3× this session, BINDING):** mode-3 = flat-wired x86 SM AND BB. Interpreters reserved for mode-2. `--run` MUST NOT invoke `sm_interp_run`. Honest mode-3 = `SCRIP_M3_NATIVE=1 ./scrip --run`. Today's default `--run` for Raku silently falls through to `sm_interp_run` (empirically traced); ladder work to flip default tracked in `MODE3-DISPATCH-GAP.md`.

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
cd /home/claude/one4all && make -j4 scrip libscrip_rt > /tmp/build.log 2>&1
[ -x scrip ] || { grep -E "error:" /tmp/build.log | head -5; exit 1; }
for r in /home/claude/one4all /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done
bash scripts/test_raku_ir_rungs.sh    # GATE-RK mode-2 baseline
bash scripts/test_raku_mode4_rung.sh  # GATE-RK4 mode-4 baseline
bash scripts/test_smoke_raku.sh       # smoke baseline
bash scripts/test_raku_mode3_native.sh  # GATE-RK3 mode-3 native (SCRIP_M3_NATIVE=1 --run)
```

## Gates

```
GATE-RK    test_raku_ir_rungs.sh        # mode-2, must hold/improve
GATE-RK4   test_raku_mode4_rung.sh      # mode-4 vs .expected, must hold/improve
GATE-RK3   test_raku_mode3_native.sh    # mode-3 native (SCRIP_M3_NATIVE=1 --run), must hold/improve
GATE-RK-SM test_smoke_raku.sh           # smoke must hold
```

## Watermark

```
RAKU ON HOLD (Lon directive, 2026-05-30). Raku development paused indefinitely; no longer top
  priority. Resume only on explicit re-prioritization. State at hold: one4all `290af6b9`, all
  gates at documented baseline above. SM-0 + SM-1 clean and pushed. SM-2 diagnosed but not
  committed. Grammar G3-1/G3-2 (C oracle) green; BB-generator tier (recursion + backtrack-across-
  calls) not yet built. See the watermark entries below for full session history.

SM-0 + SM-1 LANDED; SM-2 ATTEMPTED + REVERTED (Sonnet 4.6, 2026-05-30, one4all HEAD `7bb603a8`,
  .github clean). Two clean rungs, one diagnosed regression, no broken commits.

  SM-0 (e6f8b532): `raku_accepts(topic,matcher)` dead-code seam in `raku_builtins_byname.c`.
  Two live arms reusing proven helpers: junction (rk_junction_is → rk_junction_collapse EQ,
  numeric=topic-is-num); literal eq (both numeric → to_real eq, else strcmp==0 = SNOBOL4-LEQ
  semantics). Hit→INTVAL(1), miss→FAILDESCR (raku_match verdict convention). Regex stays on
  the direct SM-1 path. DEAD CODE: grep-verified zero callers outside own file. All gates
  byte-identical to baseline.

  SM-1 (7bb603a8): `rhs_non_regex` gate in `lower.c TT_SMATCH` match flavor. `c[1]->t != TT_QLIT`
  (a LIT_REGEX → TT_QLIT always) routes to `SM_CALL_FN raku_accepts,2`; today the lexer forces
  LIT_REGEX for all ~~ RHS so rhs_non_regex is always 0, intercept is inert. --dump-sm verified
  byte-identical for all 6 regex corpus files (zero raku_accepts appearances). All gates
  byte-identical.

  SM-2 ATTEMPTED + REVERTED: replaced the per-arm `SM_ACOMP`/`SM_LCOMP` in the `when`-chain
  loop with `SM_CALL_FN raku_accepts, 2`. Mode-2 passed (45/46) — rk_given/rk_given18/rk_junctions
  all byte-identical. Mode-4 FAILED rk_given18 (FAIL), mode-3 CRASHED rk_given18 (SIGSEGV rc=139).
  The crash was in `in_loop()` — the `for @vals -> $v { given $v { when 1 ... } }` construct.
  The `classify`/`grade`/`nested` sub calls (same given/when arms) ran correctly; only the
  `BB_ITERATE for-loop body` context crashed. Root cause diagnosed: SM_CALL_FN emitted inside a
  BB_ITERATE body calls `rt_call@PLT` from within the compiled loop frame. The System V ABI
  callee-save contract should protect r12-r15 (used by the iterator), but the interaction between
  the BB_ITERATE x86 frame and the rt_call → raku_try_call_builtin_by_name → raku_accepts call
  chain produces a SIGSEGV. This needs a dedicated session: either (a) diagnose the exact
  alignment/register clobber via gdb on the mode-3 binary, or (b) emit SM-2 as mode-2-only
  (guard with `!g_emitting_native`) first, confirming mode-4 stays on ACOMP/LCOMP until the
  BB_ITERATE interaction is resolved. SM-2 WAS NEVER COMMITTED; the revert restored the working
  tree to the SM-1 clean state. All gates: GATE-RK m2 45/46, GATE-RK4 m4 46/46 PERFECT,
  GATE-RK3 m3 45/46 CRASH 0, smoke 5/5/5/13/5, SNOBOL4 iso M2 19/0 M4 18/1, FACT 0, build clean.

  NEXT CODE RUNG: SM-2 — but diagnose the BB_ITERATE/SM_CALL_FN crash first (gdb mode-3 binary,
  rk_given18 in_loop, find the exact faulting instruction). Option B (mode-2-only guard) is the
  safe fallback if gdb session is expensive. Then SM-3 (frontend lexer/parser, own full-budget
  session, bison conflict count must stay 30).

RK-SMARTMATCH SM-0 LANDED — dead-code raku_accepts ACCEPTS seam (Claude, Opus 4.8, 2026-05-30,
  one4all `e6f8b532`). First code rung of the RK-SMARTMATCH ladder. `raku_accepts(topic, matcher)`
  added to raku_builtins_byname.c, reachable in all 3 modes via the raku_try_call_builtin_by_name
  byname table (the RK-NFA-1e seam). Two live arms reusing proven helpers: (1) junction matcher
  (s[0]==0x03) → rk_junction_collapse(topic, jct, EQ), numeric mode when topic is a number; (2)
  literal base case → numeric eq when both topic+matcher are numbers (to_real), else string eq
  (strcmp==0, the SNOBOL4-LEQ semantics the `when` string-literal arm uses via SM_LCOMP TT_LEQ).
  Hit→INTVAL(1), miss→FAILDESCR (matches raku_match's verdict convention so the SM-2 JUMP_F arm
  guard consumes it). Regex arm intentionally NOT in the helper — it stays on the SM-1 direct
  raku_match path (a bare /re/ RHS never reaches accepts per the measured SM-1 plan); Range/Type/
  Callable deferred to SM-4. PURE VALUE HELPER, no emitted x86 (FACT 0). Confirmed DEAD CODE: grep
  shows zero `raku_accepts` references outside its own file → no lowering emits it → cannot regress.
  ALL GATES BYTE-IDENTICAL to baseline: GATE-RK m2 45/46, GATE-RK4 m4 46/46 PERFECT, GATE-RK3 m3
  45/46 CRASH 0, smoke raku/icon/prolog/snobol4/snocone 5/5/5/13/5, SNOBOL4 iso M2 19/0 M4 18/1,
  build clean. (Session started from one4all HEAD 9eed4fa1 — an interleaved Prolog session had
  advanced past the prior watermark's a062f28b; Raku gates re-verified at baseline before the rung.)
  NEXT CODE RUNG: SM-1 (`~~` reroute, regex-preserving — keep raku_match DIRECT for a bare regex
  literal RHS, route only a NON-regex RHS to raku_accepts; verify `--dump-sm` unchanged for rk_re*/
  rk_regex23) then SM-2 (`when` reroute, literal+junction-preserving). SM-3 (frontend lexer/parser:
  regex-lex after when, general RHS after ~~) is its own full-budget session with the bison conflict-
  count gate (must stay 30). Risk register unchanged (see the RK-SMARTMATCH rung block).

RK-SMARTMATCH RUNG AUTHORED — planning landing, .github only, NO code change (Claude, Opus 4.8,
  2026-05-29; one4all UNCHANGED clean at `a062f28b`, gates at baseline below). Audited the current
  Raku feature set against the uploaded rakudo-main + roast-master sources. Two outcomes recorded in
  this file: (1) the RK-SMARTMATCH rung above — unify `when` + `~~` onto one `raku_accepts`/ACCEPTS
  seam, staged SM-0..SM-5 so each increment is independently green. KEY measured findings (mode-2
  probes this session): `when any(1,2,3)` ALREADY WORKS (ACOMP junction guard side-effect — leave it);
  `when /re/` and `$x ~~ 5` are PARSE ERRORS → the blocker is the LEXER/PARSER (regex-only RHS after
  `~~`; no regex-lex after `when`), NOT lowering. So the lowering reroute (SM-1/SM-2) is easy and can
  land ahead of the frontend (SM-3, own session, regen + conflict-count gate). (2) ROAST is NOT used —
  it is a doc reference only (`test_raku_ir_rungs.sh:11`, `GOAL-RAKU-FRONTEND.md:425`); gates run 46
  hand-written `test/raku/*` probes. Recommendation logged for a future GATE-RK-ROAST scoped to the
  Tiny-Raku subset (cherry-picked in-subset assertions + a minimal Test.rakumod shim) as a conformance
  oracle. Highest-leverage corrections found in the audit (for future rungs, ranked): junction
  AUTOTHREADING through arbitrary calls (currently collapse-at-comparison only — `Junction.rakumod`
  AUTOTHREAD/CALL-ME; roast `S03-junctions/autothreading.t` calls a user sub 42×); the subrule-recursion
  BB-generator tier (already the documented NEXT, G3-2c); a Match-object `$/` tree (blocks all
  action-based grammar tests, G5); laziness for map/grep/range (eager-drain contradicts the pull
  protocol, breaks on `1..*`); `|` LTM vs ordered (untested — corpus uses single-char alts only).
  NEXT CODE RUNG: RK-SMARTMATCH SM-0 (dead-code `raku_accepts` helper) then SM-1/SM-2 reroutes, then
  SM-3 frontend in its own full-budget session. Gates at this landing (one4all clean `a062f28b`):
  GATE-RK m2 45/46, GATE-RK4 m4 46/46, smoke raku 5/5. Build clean.

G3-2 rule :sigspace LANDED (Claude, Opus 4.8, 2026-05-29, one4all `a062f28b`). Per the Rakudo reading
  (token=:sigspace OFF, rule=ON, ws between atoms -> <.ws>). The registry now carries each rule's FLAVOR
  (0=token/1=rule/2=regex), threaded via a 3rd raku_grammar_register arg + lower_grammar_decl. rk_gram_expand
  is now FLAVOR-AWARE and absorbed the old strip_ws (quote/escape-aware): token/regex strip insignificant
  whitespace, rule turns each ws RUN into optional `\s*`; subrules recurse in THEIR own flavor. So
  `rule TOP { <a> <b> }` matches "foo bar"/"foobar"/"foo   bar" while token subrules stay strict.
  test/raku/rk_grammar_rule_sigspace.{raku,expected}, mode-2==mode-4. GATES: GATE-RK m2 44/45->45/46,
  GATE-RK4 m4 45/45->46/46 PERFECT, GATE-RK3 m3 44/45->45/46 CRASH 0; smoke 5/5/5/13/5, SNOBOL4 iso M2 19/0
  M4 18/1, FACT 0, no regression. SESSION TALLY (Opus 4.8 2026-05-29): G3 parse-only (76719461) -> G3-1
  Grammar.parse (dd52b2bf) -> G3-2 subrule (aa58850a) -> <.name> (75294cbb) -> rule sigspace (a062f28b),
  plus the Rakudo-grounded BB DESIGN NOTE. GATE-RK m2 41/42->45/46, GATE-RK4 m4 42/42->46/46 PERFECT,
  GATE-RK3 m3 41/42->45/46. The whole grammar surface now runs on the C raku_nfa_* engine + registry
  expansion; these are the GOLDEN ORACLE for the BB-generator tier. NEXT: the BB-generator tier (recursion
  + backtrack-across-calls onto BB_SUSPEND/BB_ALT/BB_PUMP per the DESIGN NOTE — needs a per-call Cursor
  frame stack, the one thing registry expansion can't do); and/or G5 Match tree (return a Match obj, not the
  matched string); and/or G3-3 subrule args / G3-4 grammar inheritance. Registry expansion remains
  NON-RECURSIVE (depth-cap 16).

G3-2 <.name> NON-CAPTURING SUBRULE LANDED (Claude, Opus 4.8, 2026-05-29, one4all `75294cbb`). Small
  grounded increment after reading the NQP grammar (where `<.ws>`/`<.ident>` are pervasive): rk_gram_expand
  now recognizes `<.name>` (dot-prefixed) as a subrule call, not only `<name>`. No Match tree yet, so
  `<.name>` expands identically to `<name>` (the capture-suppression difference is invisible until G5) —
  the value is syntax coverage: `token TOP { <a> <.ws> <b> }` with a user `token ws { \s }` matches
  "foo bar", misses "foobar". Stepping stone to `rule` `:sigspace` (which auto-inserts `<.ws>` at atom
  boundaries). test/raku/rk_grammar_dotws.{raku,expected}, mode-2==mode-4. GATES: GATE-RK m2 43/44->44/45,
  GATE-RK4 m4 44/44->45/45 PERFECT, GATE-RK3 m3 43/44->44/45 CRASH 0; smoke 5/5/5/13/5, SNOBOL4 iso M2 19/0
  M4 18/1, FACT 0. NEXT bounded rung: `rule` `:sigspace` — register the per-rule flavor (token/rule/regex,
  already in the AST as v.ival 0/1/2 but NOT yet carried into the registry) and, for a `rule`, convert
  inter-atom insignificant whitespace to an optional-ws matcher (`\s*` / the in-scope `<.ws>`) instead of
  stripping it. Then the real BB-generator tier (see the DESIGN NOTE under the G3-2 rung — Rakudo cursor model).

G3-2 FIRST MILESTONE LANDED — <subrule> composition, mode-2/3/4 green (Claude, Opus 4.8, 2026-05-29,
  one4all `aa58850a`). The subrule SEAM, first increment. A rule body's `<name>` references now resolve
  and compose: `token TOP { <a> <b> }` matches the concatenation, `token TOP { <x> s }` with
  `token x { cat | dog }` matches `(cat|dog)s` with correct grouping. Built on G3-1; PURE RUNTIME
  (raku_builtins_byname.c), no parser/lowering change — the parse-only rung already captures `<name>`
  inside the opaque rule body, so the seam is resolved at match time. Same C-engine pragmatism as G3-1
  (the four-port BB-generator form is the later tier). THREE additions:
  (1) `rk_gram_expand` — recursively substitute each bare `<name>` with `( <expanded-body> )` resolved
      against the `Grammar::rule` registry. Only a bare `<ident>` NOT followed by `(` is a subrule call;
      `<name>(...)` captures / `<[...]>` classes / `<?...>` assertions pass through. Wraps in CAPTURING
      `(...)` — this engine reads `[...]` as a char class and rejects `(?:...)`; the extra captures don't
      affect the `.parse` whole-string verdict; MAX_GROUPS=16 bounds milestone-depth grammars. Depth-cap 16.
  (2) `rk_gram_strip_ws` — strip insignificant whitespace (Raku token `:sigspace`-OFF: literal pattern
      whitespace is ignored), quote- and escape-aware (`'...'`/`\<sp>` preserved). This was the real bug
      behind `<a> <b>` / `foo | bar` failing to match space-free input — the engine treated pattern spaces
      as literal. (`rule` `:sigspace`-ON -> `<.ws>` is a later rung.)
  (3) `raku_grammar_parse` flow: expand -> strip-ws -> raku_nfa_build -> match (was trim-only of one literal).
  TEST `test/raku/rk_grammar_subrule.{raku,expected}` (single subrule, concat, alternation-grouping),
  mode-2==mode-4 bytes. GATES ADVANCE: GATE-RK m2 42/43->43/44, GATE-RK4 m4 43/43->44/44 PERFECT, GATE-RK3
  m3-native 42/43->43/44 CRASH 0. smoke 5/5/5/13/5, SNOBOL4 iso M2 19/0 M4 18/1, FACT 0, no regression.
  SCOPE / NOT yet: registry expansion is NON-RECURSIVE (depth-cap 16; a self/mutually-recursive grammar
  would hit the cap, not loop — but also would not match correctly; recursion needs the BB generator that
  keeps a per-call resume cursor). Still the C `raku_nfa_*` engine, not BB. `.parse` returns matched STRING,
  not a Match tree. Only `TOP` is the entry. NEXT CODE RUNG: move the seam onto the four-port generators
  (BB_SUSPEND/BB_ALT/BB_PUMP) for true backtrack-across-calls + recursion (the load-bearing BB tier the goal
  is really after), and/or G5 Match-tree. The C-engine milestones (G3-1, G3-2) prove the SEMANTICS the BB
  form must reproduce — they are the golden oracle, exactly as the leaf C-matcher is for the leaf BB slab.

G3-1 FIRST MILESTONE LANDED — Grammar.parse($s) runs the TOP rule, mode-2/3/4 green (Claude, Opus 4.8,
  2026-05-29, one4all `dd52b2bf`). The first END-TO-END grammar feature: a `token TOP { ... }` is matched
  against input via `G.parse("...")`, returning the matched text on success / Nil on failure, whole-string
  anchored. Built directly on the parse-only rung from earlier this session. THREE pieces:
  (1) RUNTIME (`raku_builtins_byname.c`): a file-static grammar-rule registry (`Grammar::rule -> body`) +
      `raku_grammar_register(qname,body)` (idempotent; emitted at the decl site so it runs in BOTH mode-2
      sm_interp and the mode-4 compiled binary — same RECORD_REGISTER cross-mode pattern lower_class_decl
      uses) + `raku_grammar_parse(gname,subject)` (looks up `gname::TOP`, trims token-insignificant
      surrounding whitespace, matches leftmost via the EXISTING isolated `raku_nfa_build`/`raku_nfa_exec`
      engine, succeeds only on full-string match `full_start==0 && full_end==len`, returns matched text or
      FAILDESCR).
  (2) LOWERING (`lower.c`): `lower_grammar_decl` emits one `raku_grammar_register` per token/rule/regex
      member (model lower_class_decl's SM-level RECORD_REGISTER loop); `lower_grammar_prescan` collects
      grammar names into `g_rk_grammar_names[]`; `case TT_GRAMMAR_DECL` dispatch; prescan hook next to
      lower_class_prescan; and a TT_METHCALL interception — when the invocant bareword is a declared
      grammar and the method is `parse` with one arg, route to `raku_grammar_parse("G", $s)` instead of the
      generic `raku_mcall`.
  (3) PARSER (`raku.y`): the missing bareword method-call productions `IDENT '.' IDENT '(' [args] ')'`.
      Literal invocants already worked (`"abc".chars` via `atom '.' IDENT`), but a bareword `G` could not
      reduce to `atom` before the `.` (LALR held it expecting `IDENT '.' KW_NEW`), so `G.parse(...)` was a
      parse error. The new productions are parallel to the `.new` ones; NET-ZERO new conflicts (still 30
      s/r). Parser regenerated (only raku.tab.c changed — no new tokens/lexer rules).
  TEST: `test/raku/rk_grammar_parse.{raku,expected}` upgraded from the parse-only fixture (now that a run
  path exists, per the file's own gating rule) to a runnable gated test — match success->text, failure->Nil,
  a `\d+` class rule, whole-string anchoring; mode-2 == mode-4 bytes. GATES ADVANCE: GATE-RK m2 41/42->42/43,
  GATE-RK4 m4 42/42->43/43 PERFECT, GATE-RK3 m3-native 41/42->42/43 CRASH 0. smoke 5/5/5/13/5, SNOBOL4 iso
  M2 19/0 M4 18/1, FACT 0, build clean, zero regression. SCOPE / HONESTY about what this is NOT yet: the
  matcher still rides the C `raku_nfa_*` engine (NOT a four-port BB generator — that is G3-2's job, the
  load-bearing seam); only `TOP` is invocable; bodies are single patterns (no `<subrule>` yet); `.parse`
  returns the matched STRING, not a real Match tree (G5). NEXT CODE RUNG: G3-2 — the subrule seam `<name>`
  (resume-and-yield-next across a call boundary = the four-port generators BB_SUSPEND/BB_ALT/BB_PUMP), and
  generalize `.parse` to compose rules. That is where BBs finally earn their keep per the shelving decision.

G3 PARSE-ONLY RUNG LANDED — and the prior session's "flex bug" was a MISDIAGNOSIS (Claude, Opus 4.8,
  2026-05-29, one4all `4d0c69aa`). The parse-only G3 frontend rung (grammar/token/rule/regex) that the
  immediately-prior session built-then-REVERTED is now GREEN and committed. The blocker that session
  spent itself on — "token works, rule/regex SEGFAULT, crash is LEXER-INTERNAL (flex)" — was WRONG.
  The crash is NOT in flex at all. gdb backtrace put it in src/ast/ast_print.c:67 flat_length ->
  __strlen, during --dump-ast. ROOT CAUSE: TT_REGEX_DECL carries its flavor in v.ival (token=0,
  rule=1, regex=2), and v is a UNION (ival/sval share storage — exactly like TT_SUB_DECL's nparams).
  The AST printer's default-kind path reads v.sval and strlen's it; ival=0 (token) reads as a NULL
  sval -> guard skips it -> safe; ival=1/2 (rule/regex) reads as pointer 0x1/0x2 -> strlen(garbage)
  -> SEGV. That is the WHOLE bug. "token only works because it was added first" (the prior watermark's
  own parenthetical hunch) was the tell — token's flavor is 0, the others' aren't. NO flex start-state
  / longest-match / rule-ordering artifact was ever involved; the lexer the prior session reverted was
  essentially fine. FIX (1 logical line, 3 identical sites): add TT_REGEX_DECL to the v.sval-read
  exclusion guards in flat_length + the two print_node paths, exactly mirroring the pre-existing
  TT_SUB_DECL/TT_PROC_DECL entries (same union-aliasing reason). LESSON for future sessions: when a
  new node stores data in v.ival, it MUST join that exclusion list, or any --dump-ast of it crashes.
  WHAT LANDED (3 files + probe): ast.h TT_GRAMMAR_DECL+TT_REGEX_DECL (enum + tt_e_name). raku.l —
  grammar/token/rule/regex keywords (token/rule/regex set raku_expect_rebody=1); new STR_REBODY
  start-state opened by the next `{` when armed, brace-depth-counted, EVERY char class handled
  ({,},\\.,\\n,.) and bounds-guarded against the 64KB raku_strbuf, returns the whole body as
  LIT_REGEX. raku.y — grammar_decl (mirrors class_decl) + grammar_body_list (KW_TOKEN/RULE/REGEX
  IDENT LIT_REGEX -> TT_REGEX_DECL, v.ival 0/1/2 = flavor); wired into stmt next to class_decl.
  Net-zero new conflicts (still 30 s/r); parser+lexer regenerated (bison 3.8.2). VERIFIED --dump-ast
  clean for all three flavors, mixed multi-member grammars, empty grammar, nested-brace quantifier
  bodies (a**{2,3}), and full subrule/class bodies (<ws> \\d+ [ 'x' | 'y' ]) — i.e. the brace counter
  + opaque-body capture are robust well past the trivial probe. test/raku/rk_grammar_parse.raku added
  as a parse-only fixture; it has NO .expected so the run-gates SKIP it (PASS/FAIL counts untouched) —
  honoring the rule that a run-path test waits for lowering (G3-1). Gates HOLD at baseline: GATE-RK m2
  41/42, GATE-RK4 m4 42/42, GATE-RK3 m3-native 41/42 CRASH 0, smoke 5/5/5/13/5, SNOBOL4 iso M2 19/0
  M4 18/1, FACT 0, build clean. Keyword-collision check: grammar/token/rule/regex appear in the corpus
  only inside # comments (rk_combinator, rk_regex23) -> stripped before keyword match -> no breakage.
  NEXT CODE RUNG: G3-1 (named-regex decl -> four-port generator lowering) then G3-2 (subrule seam <name>).
  The parse layer is now in place; lowering is the next tier. ALTERNATIVE (own session): RK-BB-5.4c
  (zip/cross, nested-tuple rep).

G3 PARSE-ONLY RUNG ATTEMPTED + REVERTED (Claude, 2026-05-29; one4all REVERTED to clean 8be5f202,
  .github committed). Tried the parse-only G3 frontend rung (grammar/token/rule/regex keywords +
  grammar_decl). Got the AST STRUCTURE working but hit a lexer crash; reverted one4all clean per
  the no-broken-commits rule. The investigation (so the next session starts from facts, not zero):
  WHAT WAS BUILT (all reverted): (1) ast.h — TT_GRAMMAR_DECL + TT_REGEX_DECL enum + name-table.
  (2) raku.l — `grammar`/`token`/`rule`/`regex` keyword rules; token/rule/regex set a new
  `raku_after_tokenkw` flag; a new `STR_REBODY` start-state that the next `{` opens, depth-counting
  braces and returning the body as LIT_REGEX (reusing the whole existing regex-literal path).
  (3) raku.y — grammar_decl (mirrors class_decl) + grammar_body_list with 3 productions
  (KW_TOKEN/KW_RULE/KW_REGEX IDENT LIT_REGEX → TT_REGEX_DECL, ival 0/1/2 = flavor). Wired into stmt.
  WHAT WORKED: bison regen NET-ZERO new conflicts (still 30 s/r); build clean; `grammar G { token T
  { 'a' } }` PARSES + `--dump-ast` PERFECT: (TT_GRAMMAR_DECL (TT_VAR G) (TT_REGEX_DECL (TT_VAR T)
  (TT_QLIT " 'a' "))). Multiple `token` members fine.
  THE BUG (unfixed, the next session's starting point): `token` works; `rule` and `regex` SEGFAULT.
  Bisected hard: the crash fires right after the lexer returns KW_RULE/KW_REGEX + the following
  IDENT, BEFORE the body `{` is lexed (no LIT_REGEX emitted). `grammar G { rule` + EOF gives a CLEAN
  syntax error (no crash) — so the KW_RULE token itself is fine; the crash needs `KW_RULE IDENT`
  then continued lexing. THE PARSER IS NOT THE PROBLEM: bison --report=all shows states 294/295/296
  (after KW_TOKEN/KW_RULE/KW_REGEX) are PERFECTLY SYMMETRIC — each `shift IDENT, go to 329/330/331`,
  each then expects LIT_REGEX. So three structurally identical productions, identical parser tables,
  yet only token survives. ⇒ The crash is LEXER-INTERNAL (flex), triggered after IDENT following
  rule/regex but not token — likely a flex start-state / longest-match / rule-ordering artifact
  specific to the strings `rule`/`regex` (note `regex` shares a prefix with nothing, but `rule` and
  the existing `repeat`/`return` are near; and `regex` vs the regex-literal machinery). NEXT SESSION:
  re-apply the 3 files (they're documented above), then debug the flex scanner directly — generate
  raku.lex.c, find the rule/regex actions and the STR_REBODY transitions, and check whether
  returning KW_RULE/KW_REGEX leaves yy_start or the after_tokenkw flag in a state that corrupts the
  next match. A standalone flex probe (scan "grammar G { rule r { z }") printing the token stream +
  yy_start after each token will localize it fast. Consider: does `token` only work because it was
  added FIRST / is shorter? Try making rule/regex behave byte-identically to token (same flag, same
  return) and bisect by swapping which keyword is listed first. Gates after revert (one4all clean
  8be5f202): GATE-RK m2 41/42, GATE-RK4 m4 42/42, smoke raku 5/5. Build clean.


  change, one4all clean at 8be5f202, all gates baseline). This session was an architecture review,
  not a code rung. Walked the bb_nfa_split design end-to-end with Lon and concluded the leaf
  single-pattern BB EMISSION path is ceremony, not value, and SHELVED RK-NFA-4/5 + G1-1..3. The
  reasoning (full version in the DECISION block near the top of this file):
    (1) The leaf MATCHER already works in all 3 modes via the C path (raku_match → nfa_bt, ~35
        lines): GATE-RK m2 41/42, GATE-RK4 m4 42/42, GATE-RK3 m3-native 41/42 CRASH 0. The BB
        leaf-emission path fixes nothing broken; default ~~ is the C matcher (RK_NFA_BB OFF).
    (2) 9 of the 10 BB_NFA_* kinds are SINGLE-SHOT leaves that do NOT backtrack (their β forwards
        to ω) — for them the four-port box is a costume over "test a char, advance or fail." Only
        SPLIT uses the structure, and SPLIT is a 2-line C conditional vs a byte-exact crash-on-
        wrong-byte x86 template with the loop-back-edge counter subtlety.
    (3) BB backtracking RELOCATES the control stack, it does not abolish backtracking state: the
        ω→β wiring + per-box counter collapse the explicit choice-point stack for FLAT patterns,
        but RECURSION (subrule→subrule) still needs a stack of resume cursors (interp C stack /
        WAM-CP frames) because one node's single counter can't hold N depths. So the BB win is
        narrow — load-bearing only where there is resume-across-recursion. Flat leaf regex has none.
  WHERE BBs EARN THEIR KEEP (kept + pursued): the SUBRULE SEAM (G3) — <name> = backtrackable method
  call = resume-and-yield-next across a call boundary = the four-port generator job (BB_SUSPEND/
  BB_ALT/BB_PUMP, already existing); and the uniform kind-set for the 5 backends (instrumental).
  KEPT: BB_NFA_* enum + raku_nfa_to_bb builder (cheap). Landed leaf templates in bb_nfa.cpp stay
  DORMANT behind RK_NFA_BB (not deleted — removal risks green gates for zero gain; not extended).
  bb_nfa_split NOT to be written. NEXT CODE RUNG: G3 — scope the Raku frontend for grammar/token/
  rule/<subrule> support, author the first grammar/subrule probe (corpus has none today), then
  G3-1/G3-2. ISOLATION DECISION still holds. Gates at this landing (one4all 8be5f202, unchanged):
  GATE-RK m2 41/42, GATE-RK4 m4 42/42, GATE-RK3 m3-native 41/42 CRASH 0, smoke 5/5/5/13/5,
  SNOBOL4 iso M2 19/0 M4 18/1, FACT 0, build clean.


  past peer Prolog commit 123878af, conflict-free). The 32-byte cset-bitset leaf for the
  isolated BB_NFA_* family, MEDIUM_TEXT. KEY correctness point: the cset travels as 32 inline
  `.byte` rodata (`.LnfaccN: .byte 0x..`×32), NOT a movabs of pBB->sval — mode-4 TEXT assembles
  a SEPARATE native binary (scrip --compile → .s → as → gcc → run, see run_raku_via_x86_backend.sh),
  so a compiler-process pointer would dangle. Membership test mirrors raku_cc_test exactly:
  byte=bits[c>>3], bit=c&7 → `mov ecx,eax; shr ecx,3; lea rdx,[rip+cs]; movzx edx,[rdx+rcx];
  and eax,7; bt edx,eax; jnc ω`. Bounds `cmp r13d,r15d; jae ω`; hit `inc r13; jmp γ`. Scratch
  eax/ecx/edx only — walker r12-r15 and callee-saved rbx untouched. Label id = bb_node_id(pBB)
  (unique per node). Routed in emit_core.c (split BB_NFA_CLASS off bb_stub; only BB_NFA_SPLIT
  remains stubbed). Prototype in bb_templates.h. Verified byte-identical to the C-matcher oracle
  on bare classes: [a-z] hit 'h'/miss '5', \d hit '5'/miss 'x', [A-Z] on 'XYZ', \s in 'hello
  world', and leftmost sweep (\d found at pos 3 in 'abc5', no \d in '___'). Default OFF
  (RK_NFA_BB); proven C-matcher path untouched all 3 modes. Gates HOLD (below); FACT 0.
  NEXT CODE RUNG: bb_nfa_split — see the ARCHITECTURE CORRECTION watermark entry below
  (structural port-wiring via walk_bb_flat; NOT a backtrack stack).

RK-NFA-4 / G1-1 SPLIT — ARCHITECTURE CORRECTION (Lon, 2026-05-29; .github only, NO code change,
  one4all clean at 037be2ce). I (Opus 4.8) started implementing bb_nfa_split with an explicit
  bss backtrack stack (rbx stack pointer, push {out2-label,pos} on SPLIT, pop on leaf ω). Lon
  stopped it: \"Does not seem right having a backtrack stack and BBs at the same time. BBs
  backtrack already — it's built into the box structure.\" CORRECT. The four-port Byrd box IS the
  backtracking mechanism: β is the retry port, and failure propagates STRUCTURALLY through the
  port wiring (a downstream box's ω wires to the β of the nearest upstream choice point). A side
  stack is a foreign pattern. I REVERTED the stack work (never committed — tree stayed clean at
  the bb_nfa_class commit, no broken commit). The correct design, confirmed by reading the live
  machinery in emit_bb.c:
    - walk_bb_flat is THE structural driver. Leaf kinds route through FILL (set four port labels,
      call the four-port template); composite/choice kinds route through flat_drive_* which mints
      labels and wires ω→upstream-β by recursion.
    - flat_drive_alt: each arm.γ→outer-γ (success exits the alt); arm[i].ω chains so the alt's β
      advances to the next arm; last arm's ω→outer ω. The chain of ω→β edges IS the choice-point
      stack, realized as wiring — no global stack.
    - flat_drive_pl_seq: \"goal[i] fail → nearest left resumable β (redo predecessor).\" Same idea.
    - bb_alt.cpp MEDIUM_BINARY: each box holds its own resume cursor pBB->counter (α resets to 0,
      β increments, dispatch jumps to arm[counter], counter==n → ω). Per-box state, not a stack.
  SO: SPLIT is a CHOICE POINT like BB_PAT_ALT/BB_CHOICE/BB_PL_ALT. The NFA graph should be DRIVEN
  BY walk_bb_flat + a new flat_drive_nfa_split (in emit_bb.c), NOT the bespoke nfa_text_box linear
  walker in sm_bb_invoke.cpp. flat_drive_nfa_split wires out1.ω→SPLIT.β, SPLIT.β→out2, out2.ω→
  outer ω. The leaf NFA kinds (CHAR/CLASS/ANY/BOL/EOL/CAP_*/EPS/ACCEPT) route through walk_bb_flat's
  FILL path — their existing four-port bb_nfa_* templates already emit γ/ω/β bodies, so the
  template bytes are REUSED; only the WALKER changes from linear to structural. The leftmost-
  unanchored sweep also moves into the flat driver (or a small wrapper). This is the documented
  S2-contract direction the prior watermark mis-recorded as \"WRONG\"; it was right — the
  single-node walk_bb_node path was wrong, but walk_bb_flat (the MULTI-node structural driver) is
  the correct home. Byte-exact x86 vs the C-matcher oracle, crash-on-wrong-byte → fresh full
  session. NEXT CODE RUNG: G1-1 = flat_drive_nfa_split + route NFA leaves through walk_bb_flat.

HYGIENE: template files renamed to match contained opcode/function (Opus 4.8, 2026-05-29,
  one4all 8e59f6b2). NOTE for RK-NFA-4 work: the NFA walker now lives in
  SM_templates/sm_bb_invoke.cpp (was sm_bb_switch.cpp — the pre-split SM_BB_SWITCH opcode is
  gone; file holds sm_bb_invoke_str + sm_bb_pl_invoke_str). Also the four mislabeled Prolog
  templates bb_arith/atom/builtin/unify.cpp → bb_pl_*.cpp (their fns were already bb_pl_* and
  the Makefile already emitted bb_pl_*.o). The 5 remaining flagged files (sm_jumps, sm_expr_incr,
  sm_push_pop_lits, sm_pat_anchors, sm_pat_combine) are intentional multi-opcode CATEGORY files,
  left as-is. Pure rename, no behavior change; all gates baseline, RK-NFA-4 L1 still green.

RK-NFA-4 / G1-1 — bb_nfa_any/bol/eol leaves landed (Opus 4.8, 2026-05-29, one4all a0346ec5).
  Three more isolated BB_NFA_* leaves up the ladder, reusing the L1 walker register model
  (r13=pos r14=base r15d=slen) with NO walker change (γ/ω wired per node): bb_nfa_any (`.`,
  match any non-\n, advance), bb_nfa_bol (`^`, zero-width pos==0), bb_nfa_eol (`$`, zero-width
  pos==slen). MEDIUM_TEXT only; emit_core.c routes ANY/BOL/EOL; CLASS/SPLIT still bb_stub.
  The leftmost sweep handles anchors naturally (^ fails for sp>0; $ fails unless pos==slen) —
  no explicit anchored-break needed. Verified mode-4 byte-identical to the C matcher 8/8:
  . on "a"→hit / ""→miss; ^x on "x"→hit / "ax"→miss; x$ on "x"→hit / "xy"→miss; ^x$ on "x"→hit
  / "xx"→miss. Default OFF; gates baseline (below); FACT 0. NEXT: bb_nfa_class (32-byte cset
  bitset in pBB->sval → \d \w \s + [...]; test bit pos, advance) + bb_nfa_split (the */+/||/?
  fork — needs the SPLIT β=out2 label threaded into nfa_text_box: currently the walker wires
  γ=successor and ω=sweep-next per node, but SPLIT also needs β→out2-node-label and the
  backtracking on the verdict-only sweep). Then RK-NFA-3 captures, RK-NFA-5 mode-3 BINARY,
  G1-3 flip default.

RK-NFA-4 / G1-1 S2+S3 — L1 /x/ GREEN in mode-4 via the emitted isolated BB_NFA_* slab
  (Opus 4.8, 2026-05-29, one4all 57ec5cea). FIRST RUNNABLE ATOM of the BB_NFA_* emission
  ladder. /x/~"x" now matches through EMITTED four-port templates (not the C matcher) in
  mode-4 (--compile x86), byte-identical to the C-matcher verdict: match / miss / leftmost-
  offset ("abcx"→pos 3, sweep proven). Default OFF (RK_NFA_BB) so the proven path + all gates
  are untouched.
  S2 (sm_bb_switch.cpp): node-keyed NFA walker in the SM_BB_INVOKE MEDIUM_TEXT arm, gated on
  gen->t∈BB_NFA_*. The CORRECTED design from the prior watermark, now PROVEN: the multi-node
  NFA graph can't ride the single-node walk_bb_node path (bb_to_by/bb_iterate are self-contained
  one-node leaves); the walker owns the subject preamble (pop subject DESCR off the SM value
  stack — rax{v|slen}:rdx{ptr}, strlen fallback), the leftmost sweep (r12d=sp 0..slen), the
  callee-saved reg save/restore (push/pop r12-r15), and per-node label wiring (set g_emit.lbl_*
  per node, walk_bb_node_str_c each). Match pushes an int verdict (1/0) so the `if` branch's
  SM_VOID_POP balances; last_ok (caller γ/ω postamble) drives JUMP_F. β resume handler defined
  (never taken for verdict ~~). Register model: r13=pos, r14=base, r15d=slen, r12d=sp.
  S3 (bb_nfa.cpp): bb_nfa_char (cmp r13d,r15d; jae ω; movzx [r14+r13]; cmp imm; jne ω; inc r13;
  jmp γ) + bb_nfa_accept (jmp γ→matched), MEDIUM_TEXT only; mode-3 BINARY deferred to RK-NFA-5.
  emit_core.c routes BB_NFA_CHAR/ACCEPT to them; ANY/CLASS/SPLIT/BOL/EOL stay on bb_stub.
  All emission in *_templates/ (FACT 0). Default gates HOLD (below). Repro:
  RK_NFA_BB=1 bash scripts/run_raku_via_x86_backend.sh FILE.raku
  NEXT CODE RUNG: extend the leaf set up the L2-L12 ladder — bb_nfa_any (`.`), bb_nfa_class
  (32-byte cset bitset → \d \w \s + [...]), bb_nfa_bol/eol (^/$), bb_nfa_split (the * / + / ||
  fork — model the backtrack on the verdict-only sweep; SPLIT's β=out2 is the second arm). Each
  is a new MEDIUM_TEXT arm in bb_nfa.cpp + an emit_core.c route off bb_stub; the walker already
  wires γ/ω/β per node (SPLIT will need its β=out2 label threaded — add to nfa_text_box). Then
  RK-NFA-3 captures ($0/$1 → GC_malloc cap block in the walker preamble), then RK-NFA-5 mode-3
  BINARY (byte twins of the TEXT arms), then G1-3 flip default ~~→BB. The C matcher stays the
  default + the golden oracle the emitted path is diffed against (L1-L15 already pass via C in
  all 3 modes).

RK-NFA-4 / G1-1 S1 LANDED + S2 CONTRACT CORRECTED (Opus 4.8, 2026-05-29, one4all c8aeb90d).
  FIRST CODE RUNG of the BB_NFA_* emission ladder. S1 = the gated `~~` lowering rewiring in
  lower.c TT_SMATCH (real case ~line 2492, NOT 2488): getenv("RK_NFA_BB") && flavor==match →
  raku_nfa_build(t->c[1]->v.sval) [compile fn is raku_nfa_build, NOT raku_nfa_compile] →
  raku_nfa_to_bb (RK-NFA-1b graph) → lower_expr(c[0]) pushes subject → SM_seq_bb_add +
  SM_BB_INVOKE; raku_nfa_free after (builder copies CHAR ival / CLASS cset / CAP idx / ports
  out — graph independent of the malloc'd nfa). Phase-2 kinds → raku_nfa_to_bb NULL → fall
  through to the proven C matcher. subst/match_global stay on the C matcher. Default OFF so the
  SM_CALL_FN raku_match path is untouched. Added #include raku_re.h to lower.c. +22 lines,
  FACT 0 (no emitted bytes). VERIFIED via --dump-sm: flag OFF → SM_CALL_FN raku_match; flag ON
  → SM_BB_INVOKE. All gates at baseline (see below), all five smokes green, SNOBOL4 iso intact.

  ⛔ KEY FINDING — the RK-NFA-4-CONTRACT.md S2 plan was WRONG and is now corrected (see the
  ⚠️ UPDATE block at the TOP of that file). The contract said "add flat_drive_nfa to
  walk_bb_flat." But the live mode-4 Raku ~~ path is: SM_BB_INVOKE → emit_core.c:858
  sm_bb_invoke → SM_templates/sm_bb_switch.cpp MEDIUM_BINARY arm → entry-flag dispatch +
  walk_bb_node(gen,NULL) [emit_core.c:528, a SINGLE-NODE dispatcher] + γ/ω postamble (rt_set_
  last_ok). walk_bb_flat/flat_drive_* is the ICON flat-codegen path, never hit by Raku ~~.
  walk_bb_node emits ONLY the entry node; bb_to_by/bb_iterate work as one node because each is
  SELF-CONTAINED (bounds compile-time-baked, or read from a named var via NV_GET_fn, state in
  &pBB->counter). The NFA graph is genuinely MULTI-NODE (CHAR→ACCEPT, SPLIT) → one walk_bb_node
  cannot traverse it. CORRECTED S2: a NEW node-keyed NFA walker INSIDE the sm_bb_switch.cpp
  MEDIUM_BINARY arm, gated on gen->t∈BB_NFA_*: (1) subject preamble — pop the subject DESCR off
  the SM value stack (pushed by S1's lower_expr c[0]); unpack base+slen (model bb_iterate's
  DESCR unpack, but source is the vstack not NV_GET); pos/base/slen in callee-saved regs; (2)
  leftmost sweep wrapping the walk (mirror raku_nfa_bb_match for sp in 0..slen); (3) node-keyed
  walk minting a label per node (mirror flat_drive_seq's node→label table, emit_bb.c:745),
  emit each leaf via bb_nfa_* template, wire γ→next-node, β→SPLIT-out2; cap block (GC_malloc)
  lands with RK-NFA-3 (L1 needs none). This is a NEW walker, NOT pure transcription — budget a
  fresh session. NEXT CODE RUNG: G1-1 S2 = the node-keyed NFA walker in sm_bb_switch.cpp's
  BINARY arm, then S3 bb_nfa_char+bb_nfa_accept, proving L1 /x/~"x" under RK_NFA_BB=1.
  DELIBERATELY did NOT write S2's byte-exact walker this session: it's a brand-new vstack→cursor
  calling convention as byte-exact x86 (crash-on-wrong-byte), and committing it untested would
  be a broken commit (RULES). S1 is the clean, verified, gated foundation it builds on.

RK-NFA-4 / G1-1 ENTRY CONTRACT RESOLVED (Opus 4.8, 2026-05-29, .github only — NO code change,
  NO regression). Planning landing, not a code rung. one4all + corpus UNTOUCHED (both clean;
  one4all HEAD 28a720f2, advanced past this file's older code-rung hashes by an interleaved
  SNOBOL4 session — built that HEAD, Raku gates held at the documented numbers below). Wrote
  RK-NFA-4-CONTRACT.md (this repo). KEY FINDING: the 7 consuming/branching templates were NOT
  the right first sub-step. walk_bb_flat (emit_bb.c) has NO flat_drive_nfa arm → BB_NFA_* kinds
  hit default: (define β; jmp ω; jmp ω); the flat slab is entered via `call fn(NULL,0)`
  (xa_flat.cpp prologue: sub rsp,8; cmp esi,0; je α_body; jmp β) with NO subject/pos/slen args,
  only g_vstack + the SIGMA return slot — so the "proposed" r13/r14/r15 model had no setup and
  the templates had no driver. The driver/ABI is the prerequisite. CONTRACT now pinned to real
  code (not guessed): (1) pattern is COMPILE-TIME — raku.y:468 TT_SMATCH c[1]=leaf_sval(TT_QLIT,
  LIT_REGEX), available at lower time as t->c[1]->v.sval → lowering can raku_nfa_compile it;
  (2) graph builder ready — raku_nfa_to_bb (RK-NFA-1b ✅); (3) registration = SM_seq_bb_add →
  SM_BB_INVOKE (lower.c:245-246 model); (4) relocation = bin{{sites},{labels},{is_def}} (bb_eps/
  bb_alt); (5) SPLIT live model = bb_alt.cpp counter-state slab. ABI grounded in the prologue:
  driver pops subject→r14(base)/r15d(slen), owns r13=pos, GC_malloc cap block via movabs/@PLT
  (PEERS-clean); all three callee-saved, untouched by flat prologue/epilogue. SUB-STEP ORDER
  (all behind getenv("RK_NFA_BB"), default OFF so the proven C-matcher path + all gates stay
  green): S1 lowering rewiring (lower.c TT_SMATCH ~2488) → S2 flat_drive_nfa arm in walk_bb_flat
  (preamble: pop subject, GC_malloc caps, leftmost-sweep loop wrapping the γ-chain; leaf ω→sweep-
  continue, ACCEPT γ→outer γ; sweep exhausted→outer ω) → S3 leaf templates bb_nfa_char/accept/
  any/class/bol/eol + bb_nfa_split (bb_alt model) → S4 gate ladder L1..L15 under RK_NFA_BB=1,
  flip default last (G1-3). FIRST RUNNABLE ATOM: L1 /x/~"x" = S1 + S2 + bb_nfa_char + bb_nfa_accept.
  DELIBERATELY did NOT emit the raw x86 this session: it is a brand-new vstack→cursor calling
  convention as byte-exact bytes (crash-on-wrong-byte, byte-exact golden test), and committing it
  untested would be a broken commit (RULES) — the watermark's own "fresh full-budget session"
  guidance. The contract note converts that session from reverse-engineering to transcription.
  NEXT CODE RUNG UNCHANGED: G1-1 = RK-NFA-4 (now: start at S1 with RK-NFA-4-CONTRACT.md in hand).
  Gates at session start (built one4all HEAD 28a720f2; code unchanged this session):
  GATE-RK m2 41/42, GATE-RK4 m4 42/42, GATE-RK3 m3-native 41/42 CRASH 0, smoke raku 5/5. FACT 0.

RK-GRAM LADDER AUTHORED (Opus 4.8, 2026-05-29, .github only — NO code change, NO regression).
  Planning landing, not a code rung. Wrote the full Raku grammar-feature ladder into this
  goal file: TWO-TIER decision (Tier A NFA leaf / Tier B BB-generator structure), ONE SEAM
  (subrule call <name> = β-pumpable generator invocation). SUPERSEDED the old RK-NFA-6..9
  <rule>→BB_NFA_SUBCALL plan — keep the NFA slab leaf-only; subrule/rule/grammar backtracking
  rides the EXISTING four-port generators (BB_SUSPEND/BB_ALT/BB_PUMP). Six phases, every rung
  with `- [ ]` steps: P1 NFA core (=RK-NFA-1..5, in flight); P2 full single-pattern surface
  (G2-1..13: quantifiers/frugal/grouping/anchors/classes/lookahead/assertions/conjunction/
  adverbs/backrefs/interp/markers); P3 grammar STRUCTURE (G3-1..6: named-regex-as-generator,
  subrule forms, args, grammar decl, entry points, default ws); P4 LTM+proto (G4-1..3);
  P5 actions+Match-tree (G5-1..4); P6 convergence/control/adverbs (G6-1..5, deferred).
  STRATEGIC PRIORITY recorded (Lon): RK-GRAM is #1 — the grammar surface flushes out the full
  BB-kind collection; SM spine ~99% done; a complete BB set is the prereq for the all-language
  back-end cycle (x86/JVM/.NET/JS/WASM). NEXT CODE RUNG UNCHANGED: G1-1 = RK-NFA-4's 7
  consuming/branching templates (CHAR/ANY/CLASS/SPLIT/BOL/EOL/ACCEPT), per the RK-NFA-4 DESIGN
  block. Gates at this landing (code unchanged from ac1bc66b): m2 41/42, m3-native 41/42 CRASH 0,
  m4 42/42, smoke 5/5/5/13/5, SNOBOL4 iso M2 19/0 M4 18/1, FACT 0.

RK-NFA-4 SCAFFOLD LANDED (Opus 4.8, 2026-05-29, one4all `ac1bc66b`). Begins the
  mode-4 emission rung for the ISOLATED BB_NFA_* family. NEW bb_nfa.cpp: trivial
  passthrough templates bb_nfa_eps/cap_open/cap_close (pure jmp γ, clone of bb_eps).
  All 10 BB_NFA_* opcodes wired into emit_core.c dispatch (3→templates, 7 consuming/
  branching CHAR/ANY/CLASS/SPLIT/BOL/EOL/ACCEPT→bb_stub placeholder). Prototypes in
  bb_templates.h; Makefile RT_PIC_SRCS + explicit bb_nfa.o scrip rule (BOTH build
  mechanisms — scrip links $(OBJ)/*.o from per-file -c rules, libscrip_rt from the
  RT_PIC_SRCS var; missing the explicit rule was the link-fail gotcha). Dead-code-
  until-~~-rewiring; nothing builds a BB_NFA_* graph yet, so zero regression. Gates:
  m2 41/42, m3-native 41/42 CRASH 0, m4 42/42, smoke 5/5/5/13/5, SNOBOL4 iso M2 19/0
  M4 18/1, FACT 0 (byte emitters only in bb_nfa.cpp, a BB_templates/ file). NEXT: the
  7 consuming/branching templates (pos/subject/slen register model + char/cset/
  backtrack bytes + capture block) per the RK-NFA-4 DESIGN block in this file, then
  ~~→SM_BB_INVOKE behind RK_NFA_BB=1. Best as a fresh full-budget session (byte-writing
  under FACT). raku_nfa_to_bb (RK-NFA-1b) already produces the graph these consume.

[Prior] RK-NFA-1b DONE (Opus 4.8, 2026-05-29, one4all `6b593da8`). raku_nfa_to_bb — NFA →
  ISOLATED BB_NFA_* graph builder (BB_LANG_RKU), the prereq for mode-4 emission. In
  raku_nfa_bb.c: nfa_kind_to_bb 1:1 Nfa_kind→BB_NFA_* (CHAR/ANY/CLASS/SPLIT/EPS/BOL/
  EOL/CAP_OPEN/CAP_CLOSE/ACCEPT), one BB_t per state, γ=out1-node β=out2-node(SPLIT)
  ω=NULL, payload CHAR ival=char / CLASS sval=32-byte cset / CAP ival=group-idx,
  entry=start node; NULL on Phase-2 kinds. raku_re.h fwd-decls it (no BB.h pull-in).
  Verified standalone: graph faithfully mirrors the NFA across L1-L15 (node count ==
  state count, ports wired, entry correct, csets/chars/caps carried). Pure graph
  construction, NO x86, dead-code-until-RK-NFA-4 (no caller yet) → can't regress.
  Gates unchanged: m2 41/42, m3-native 41/42 (CRASH 0), m4 42/42, smoke 5/5, SNOBOL4 iso M2 19/0 M4 18/1, FACT 0.
  NEXT: RK-NFA-4 — NEW src/emitter/BB_templates/bb_nfa_*.cpp (FACT-pure, four-port,
  isolated; opcode names from Nfa_kind) + SM_BB_INVOKE over the raku_nfa_to_bb graph
  on the ~~ path; GATE rk_re33/34/35 mode-4 via BB, SNOBOL4 pattern-rung suite
  byte-unchanged. Then RK-NFA-5 (mode-3 native via emitted BB templates; mode-3 already PASSES regex 41/42 CRASH 0 through the C matcher, so this MOVES it onto the isolated BB_NFA_* slab — architectural, not a crash-fix).

[Prior] RK-NFA-1e CLOSED (Opus 4.8, 2026-05-29, one4all `0d94e255`). Whole mode-2/mode-4
  Raku regex cluster lit up. ~~ lowered to SM_CALL_FN raku_match but the only handler
  was the legacy tree-walk raku_try_call_builtin(tree_t*); the SM byname dispatcher
  raku_try_call_builtin_by_name (sm_interp.c:1387 mode-2 + rt.c:1598 mode-4) never knew
  the name → all 6 regex tests failed BOTH modes. Closed past option-A: (1) by-name twins
  of raku_match/_global/raku_subst/raku_nfa_compile/raku_re_capture/raku_named_capture in
  raku_builtins_byname.c, all via the ISOLATED raku_nfa_* matcher (no SNOBOL4-pattern-opcode contact);
  (2) capture name-collision fix — lexer split $*STD* (→VAR_FH→TT_FH_CAPTURE→raku_capture,
  FH byte-identical) from $0/$1 (→VAR_CAPTURE→TT_CAPTURE→new raku_re_capture, group slice),
  net-zero new grammar conflicts (still 30); (3) subst write-back — lower_expr emits
  STORE_VAR+PUSH_VAR after raku_subst when the LHS is a plain TT_VAR (by-name args are
  pre-eval'd, var identity gone). GATE-RK m2 35→41/42 (only rk_stdio39 fidelity non-bug
  left); GATE-RK4 m4 36→42/42 PERFECT. Smoke 5/5/5/13/5 HOLD; SNOBOL4 pattern-rung suite
  BYTE-IDENTICAL M2 19/0 M4 18/1 (isolation proven); FACT 0 (no emitter/template bytes).
  Parser/lexer regenerated (bison 3.8.2). NEXT: BB_NFA_* emission path — RK-NFA-1b
  (raku_nfa_to_bb state→node walk) then RK-NFA-4 (bb_nfa_*.cpp mode-4 templates) /
  RK-NFA-5 (mode-3 native), the real BB ladder destination; OR RK-BB-5.4c (zip/cross,
  needs nested-tuple rep, own session).

[Prior] RK-BB-5.4a + 5.4b COMPLETE (Opus 4.8, 2026-05-29, one4all `56a30122`).
  GATE-RK mode-2 33→35/42, GATE-RK4 mode-4 34→36/42. Three commits, all green/regression-free.
  5.4a `.method` list-method forms (`dbb3d15f` postfix + `91bfae91` for-form): .reverse/.unique/
  .sum/.elems/.head(N)/.tail(N) routed from TT_METHCALL (post class-resolution-miss) + TT_FIELD
  (bare) to the list-context value helpers via the raku_is_listmeth whitelist, ahead of the
  class raku_mcall/FIELD_GET fallbacks; new head/tail value builtins (trailing arg=N, bare N=1);
  for-CALL materialise guard widened (raku_methform_listmeth) so `for @a.reverse -> $x` iterates.
  5.4b parenthesized array literal `my @a=(1,2,3)` (`56a30122`): two initializer-only raku.y
  productions mirroring 5.3 bare comma-list → NET-ZERO new conflicts.

.github: GOAL-RAKU-BB.md — 5.4a/5.4b marked ✅ in open rungs; 5.4c (zip/cross) deferred to own
  session (needs nested-tuple rep). Watermark + gates + NEXT updated. PLAN.md row updated.
  HANDOFF-2026-05-29-OPUS48-RAKU-BB-5-4-METHODS-AND-PAREN.md added.

corpus:  unchanged

GATE-RK   mode-2 (--interp):     41/42  (+all 6 regex; only rk_stdio39 fidelity non-bug left)
GATE-RK4  mode-4 (--compile x86): 42/42  PERFECT (all regex + rk_stdio39 pass on the byname path)
GATE-RK3  mode-3 native (--run):  41/42  CRASH 0 (only rk_stdio39; verified honest native — see below)
Smoke raku/icon/prolog/snobol4/snocone: 5/5/5/13/5  HOLD
SNOBOL4 pattern-rung suite:               BYTE-IDENTICAL M2 19/0 M4 18/1 (isolation proven)
bison s/r conflicts: 30 (unchanged — VAR_FH split + FH/regex production added zero)
FACT RULE grep:   0
Build:            clean
```

## Mode-3 native is HONEST and 41/42 — MODE3-DISPATCH-GAP / "CRASH 6" claims were STALE

Re-measured 2026-05-29 (Opus 4.8) with `scripts/test_raku_mode3_native.sh` (= `SCRIP_M3_NATIVE=1 ./scrip --run`
over the corpus). Result: **mode-3 native 41/42, CRASH 0** — the regex cluster (rk_re32/33/34/35/37, rk_regex23)
PASSES natively too, not just mode-2/mode-4. The prior watermark's "Raku --run emits no output for ANY program
(MODE3-DISPATCH-GAP)" and "CRASH 6" were stale: that dispatch betrayal was RETIRED. `scrip.c` lines 554-567 —
for non-Icon `--run`, the driver calls `sm_run_native(&s2->sm)` with NO interpreter fallback (abort-on-failure;
`SCRIP_M3_NATIVE` isn't even consulted — `--run` is always native for Raku). Honesty verified: `sm_native.c`
has ZERO `sm_interp_run` references; the `SM_CALL_FN` template emits `call rt_call` (mode-3 absolute movabs+call /
mode-4 @PLT) → `rt_call` (rt.c:1705) → `raku_try_call_builtin_by_name` (the SAME byname table RK-NFA-1e extended).
So all three modes share one dispatcher; the mode-3 regex passes are genuine (rk_re34 emits the real multi-line
capture output, not a silent empty pass). Only rk_stdio39 fails (the known stderr→fd-1 fidelity non-bug, all modes).

## NEXT — G3 subrule seam (the load-bearing BB tier); leaf BB emission SHELVED

**DIRECTION CHANGE (Lon + Claude, 2026-05-29).** Stop the leaf-emission push (`bb_nfa_split` /
RK-NFA-4/5 / G1-1..3 are SHELVED — see the DECISION block near the top). The leaf single-pattern
MATCHER is already green in all three modes via the C path (`raku_match` → `nfa_bt`), and 9 of the
10 `BB_NFA_*` kinds are single-shot leaves that don't backtrack, so emitting them as four-port x86
templates is ceremony, not value. Default `~~` stays on the C matcher (`RK_NFA_BB` OFF). The landed
leaf templates stay dormant; `bb_nfa_split` is NOT to be written.

**IMMEDIATE WORK: G3 — the subrule seam.** This is where BBs are actually load-bearing: `<name>` in
a pattern is a backtrackable method call that must resume-and-yield-next across a call boundary while
building the Match tree — exactly the four-port generator job (`BB_SUSPEND`/`BB_ALT`/`BB_PUMP`, all
already existing). It is also the #1 grammar goal (the grammar surface flushes out the full BB
generator kind-set the five backends emit against).

**HONEST FIRST STEP (not lowering): scope the FRONTEND.** The corpus has NO grammar/subrule tests
today (the 6 regex tests are plain single patterns), and it is unverified whether the Raku
lexer/parser even accepts `grammar` / `token` / `rule` / `<subrule>` syntax. So G3 begins with:
1. Probe the current Raku frontend (lexer keywords + `raku.y` productions) for `grammar`/`token`/
   `rule`/`<name>` support. Determine the real starting rung (parser work vs lowering work).
2. Author the first `test/raku/*.{raku,expected}` grammar/subrule probe (mode-2 GATE-RK + mode-4
   GATE-RK4 byte-identical, Prolog GATE-4 pattern).
3. Then G3-1 (named-regex decl → generator) and G3-2 (subrule call = THE SEAM).

**KEEP (cheap, may serve the seam):** the isolated `BB_NFA_*` enum + `raku_nfa_to_bb` graph builder
(RK-NFA-1b ✅). **CAVEAT, eyes open:** since leaf regex did not want BBs, the 9 leaf "kinds" may be
the wrong (leaf-costume) kinds; the seam GENERATORS are the kinds that matter. Re-evaluate whether
the leaf graph is even needed at the seam before relying on it.

ALTERNATIVE (deferred, own session): **RK-BB-5.4c** (`zip`/`cross`) — multi-Seq drivers, each output
element a list → needs a nested-tuple rep (STX-within-SOH); broad blast radius.

### G3 FRONTEND SCOPING (measured 2026-05-29, one4all 8be5f202 — facts for the next session)

Probed the Raku frontend to find G3's real starting rung. Findings:
- **NO `grammar`/`token`/`rule` keyword exists** in `raku.l` or `raku.y`. There is no `KW_GRAMMAR`/
  `KW_TOKEN`/`KW_RULE` token, no `grammar_decl` production, no `<subrule>` syntax. G3 is genuinely a
  FRONTEND build-out, not a lowering tweak.
- **Regex exists ONLY as a literal.** `raku.l` lexes `/.../` into `LIT_REGEX` via the `STR_RE` start
  state (gated by `raku_after_smatch`, set by the `~~` operator); `m:g/.../`→`LIT_MATCH_GLOBAL`,
  `s/.../.../`→`LIT_SUBST`. The grammar uses it at exactly one site: `raku.y:467
  jct_expr OP_SMATCH LIT_REGEX`. So a regex body is today an opaque string handed to `raku_nfa_build`
  at match time — there is no named/declared regex.
- **The model to mirror for a grammar is `class_decl`** (`raku.y:385`): `KW_CLASS IDENT '{'
  class_body_list '}'` with `KW_METHOD IDENT '(' param_list ')' block` members. A `grammar` is the
  same shape — a named namespace whose members are `token`/`rule`/`regex` declarations instead of
  methods. The `KW_CLASS KW_METHOD KW_HAS KW_NEW` token block (`raku.y:166`) is where `KW_GRAMMAR
  KW_TOKEN KW_RULE KW_REGEX` would be added.
- **The regex parser `raku_re.c` is REUSABLE for token bodies.** It already parses the full single-
  pattern surface into an NFA; a `token NAME { <body> }` body is the same pattern grammar plus
  subrule calls `<name>`. The NEW frontend work is: (a) lex `grammar`/`token`/`rule` as keywords and
  a `{ ... }` regex-body start-state (distinct from the `/.../` `STR_RE` state — body uses `{}`
  delimiters and allows whitespace/comments under `:sigspace`); (b) a `grammar_decl` production
  modelled on `class_decl`; (c) extend `raku_re.c` (or a sibling) to recognize `<name>` subrule
  calls → `NK_SUB_CALL` (already in `Nfa_kind`, currently makes `raku_nfa_to_bb` return NULL).

PROPOSED G3 START (next session, fresh budget): a PARSE-ONLY rung — add the keywords + `grammar_decl`
+ `{}`-body lexing, get a `grammar G { token TOP { 'a' } }` probe to `--dump-ast` cleanly (no
lowering, no x86, no gate movement). That isolates the pure-frontend risk before any BB/generator
lowering. Then G3-1 (named-regex → four-port generator) and G3-2 (subrule seam). Authoring the first
`test/raku/*.{raku,expected}` probe waits until at least parse + a minimal run path exists.

**✅ PARSE-ONLY RUNG DONE (Opus 4.8, 2026-05-29, one4all `4d0c69aa`).** All of the above landed and is
green — see the top watermark entry. The reverted-session's "flex bug" was a misdiagnosis (an
`ast_print.c` union misread of `v.ival` as `v.sval`, fixed by adding `TT_REGEX_DECL` to the printer's
exclusion guards). `grammar`/`token`/`rule`/`regex` parse to `TT_GRAMMAR_DECL`/`TT_REGEX_DECL` with
opaque `LIT_REGEX` bodies, `--dump-ast` clean (incl. nested `**{m,n}` + subrule/class bodies). NEXT is
G3-1 (named-regex → generator lowering), then G3-2 (subrule seam).


## Open questions for Lon

Resolved (2026-05-27): 100% template emission via BB/SM/XA only.

Pending:
- **Q5.** Union-clobber proper fix. TT_SUB_DECL uses `v.ival` for nparams AND wants `v.sval` for name. Move nparams to a side-channel so `v.sval = name` semantics is restored.
- **Q9-Q12.** RK-BB-4 directives — see substrate audit above.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
