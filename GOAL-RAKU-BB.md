# GOAL-RAKU-BB.md — Raku goal-directed ~20% onto shared BB generators

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

- [ ] **RK-NFA-1 — wire family + mode-2 backtracking walk.** 1a/1b/1c/1d/1e ✅; remaining: gate the BB graph into mode-4 (RK-NFA-4 below).
  - [x] 1a. `BB_NFA_*` enum block in `src/include/BB.h` (isolated; SNOBOL4's pattern opcodes untouched).
  - [x] 1b. **DONE (RK-NFA-1b ✅, Opus 4.8, 2026-05-29, one4all `6b593da8`).** `raku_nfa_to_bb(Raku_nfa*) → BB_graph_t*` state→node walk in `raku_nfa_bb.c` (isolated; zero `snobol4_pattern.c` contact). `nfa_kind_to_bb` 1:1 `Nfa_kind`→`BB_NFA_*`; one `BB_t` per NFA state; ports γ=out1-node (advance), β=out2-node (SPLIT backtrack), ω=NULL for the consumer scaffold; payload CHAR ival=char, CLASS sval=32-byte cset blob, CAP_OPEN/CLOSE ival=group idx; `bbg->entry`=start node; returns NULL on Phase-2 kinds (NK_CODE/NK_SUB_CALL) so callers fall back. Verified standalone: graph faithfully mirrors the NFA across the full L1-L15 pattern set (node count == state count, ports wired, entry correct, csets/chars/caps carried). Pure graph construction, NO x86, dead-code-until-RK-NFA-4. Gates unchanged.
  - [x] 1c. Isolated mode-2 backtracking matcher `raku_nfa_bb_match` (`src/frontend/raku/raku_nfa_bb.c`, `nfa_bt` depth-first, β=`SPLIT.out2`); `raku_nfa_start/accept` accessors + `raku_nfa_states` defined; Makefile wired; `RK_NFA_BB=1` gate in tree-walk handler.
  - [x] 1d. Standalone oracle: backtracking BB verdict == parallel NFA verdict on **L1-L12, 12/12, zero mismatches.** Thesis proven.
  - [x] 1e. **CLOSED (RK-NFA-1e ✅, Opus 4.8, 2026-05-29, one4all `0d94e255`).** SM dispatch gap closed and the WHOLE mode-2/mode-4 regex cluster lit up (went past option-A name-registration). `~~` lowered to `SM_CALL_FN raku_match` but the only handler `raku_try_call_builtin(tree_t*)` was the legacy tree-walk; `--interp` (`sm_interp.c:1387`) and `rt_call` (`rt.c:1598`) reach `raku_try_call_builtin_by_name`, which never knew the name → all 6 regex tests failed BOTH modes. **(1)** `raku_builtins_byname.c`: by-name twins using pre-eval'd `args[]` — `raku_match`, `raku_match_global`, `raku_subst`, `raku_nfa_compile`, `raku_re_capture`, `raku_named_capture`; all route through the ISOLATED `raku_nfa_*` matcher (`raku_re.c`/`raku_nfa_bb.c`), zero SNOBOL4-pattern-opcode contact. **(2)** Capture name-collision: the lexer mapped BOTH `$*STDOUT`/`$*STDERR` (FH) and `$0`/`$1` (regex) to `VAR_CAPTURE→TT_CAPTURE→raku_capture`, and the RK-IO `FHVAL` handler shadowed the regex slice. Split at the lexer: `$*STD*`→new `VAR_FH`→`TT_FH_CAPTURE`→`raku_capture` (FH, byte-identical); `$0`/`$1`→`VAR_CAPTURE`→`TT_CAPTURE`→new `raku_re_capture` (group slice). Net-zero new grammar conflicts (still 30). **(3)** Subst write-back: `s/pat/repl/` mutates its subject; by-name args are pre-eval'd values (var identity erased, unlike the AST handler's frame inspection). When the smatch-subst LHS is a plain `TT_VAR`, `lower_expr` emits `STORE_VAR`+re-`PUSH_VAR` after the call → subject rebound, statement still yields a value. **GATE-RK m2 35→41/42** (only rk_stdio39 fidelity non-bug remains), **GATE-RK4 m4 36→42/42 PERFECT**. Smoke 5/5/5/13/5 HOLD; SNOBOL4 pattern-rung suite BYTE-IDENTICAL M2 19/0 M4 18/1 (isolation proven); FACT 0 (mode-2/4-dispatch rung, no emitter/template bytes). This subsumes the mode-2/mode-4 verdict+capture+global+subst goals of RK-NFA-2/RK-NFA-3 as well; what remains for those rungs is the BB_NFA_* emission path (RK-NFA-1b → RK-NFA-4/5).
- [ ] **RK-NFA-2 — mode-2: csets + anchors + ordered alt** (rk_re32/33, L4-L12). Verdict logic already oracled; needs RK-NFA-1e plumbing.
- [ ] **RK-NFA-3 — mode-2: captures** `$0`/`$1`/`$<name>` → `BB_NFA_CAP_*` (rk_re34/35, L13-L15).
- [ ] **RK-NFA-4 — mode-4 emission.** NEW `src/emitter/BB_templates/bb_nfa_*.cpp` (FACT-pure, four-port, isolated). GATE: rk_re33/34/35 mode-4; SNOBOL4 pattern-rung suite byte-unchanged.
- [ ] **RK-NFA-5 — mode-3 native.** `SCRIP_M3_NATIVE=1`; closes rk_re32/33/34/35/37, rk_regex23 CRASH→PASS; default `~~`→BB; NFA→harness oracle.
- [ ] **RK-NFA-6..9 (Phase 2, DEFERRED):** `{m,n}`/`*?`; LTM `|`→`BB_NFA_LTM`; subrules `<rule>`→`BB_NFA_SUBCALL`; `:ratchet`+grammar dispatch+actions.
- [ ] **RK-NFA-CONV (DEFERRED):** collapse `BB_NFA_CHAR/CLASS/ANY/BOL/EOL` ↔ SNOBOL4's `LIT/ANY/LEN/POS/RPOS` pattern opcodes into `BB_MATCH_*` where byte+semantics identical; `SPLIT`+captures stay separate.

**Test ladder L1-L15** (GATE-NFA-O = mode-2 `raku_nfa_bb_match` verdict == `raku_nfa_exec` verdict, then `.expected`): L1 `/x/`~"x"; L2 `/.*/`~""; L3 `/.*/`~"xyz"; L4 `/[a-z]+/`~"hello"; L5 `/[a-z]+/`~"123"(no); L6 `/\d+/`~"abc123"; L7 `/\d+/`~"abc"(no); L8 `/a||b/`~"cat"; L9 `/a||b/`~"dog"(no); L10 `/^x$/`~"x"; L11 `/^x$/`~"xy"(no); L12 `/^x$/`~""(no); L13 `/([A-Za-z]+)/`→$0; L14 two caps; L15 `<word>(...)`. **L1-L12 verdict-green standalone; L13-L15 at RK-NFA-3.** Isolation guard every rung — run the SNOBOL4 cross-language regression suite (`scripts/test_snobol4_pat_rung_suite.sh`, a SNOBOL4-owned artifact; the only place a SNOBOL4 `pat` name appears, intentionally, as the thing this Raku ladder must NOT perturb) — it must stay M2 19/0 M4 18/1.
- [x] **RK-BB-4 mode-2 ✅** (4a constructors + 4b infix, see completed rungs). **Full `rk_junctions` probe PASS mode-2.** Q9-Q12 ANSWERED by Lon (2026-05-29): **Q9** reuse existing kinds; break out new SM/BB opcodes ONLY if language-specific behavior diverges. **Q10** build on `BB_ALT` (live substrate Icon uses); split later if needed. **Q11** substrate-first. **Q12** tagged-string rep. Substrate proven: `BB_ALT` mode-2 is a complete n-ary alternation engine (empirically `x=(1|2|3)`→hit, `x=(7|8|9)`→miss, `every write(10|20|30)`→10/20/30); `BB_ALT` mode-4 `MEDIUM_BINARY` is a real counter-state dispatch slab (NOT a stub — the probe header's stale assumptions #3/#4 refer to the orphan `BB_ALTERNATE`, and only the `MEDIUM_TEXT` arm is a passthrough). Junction VALUE rep is the tagged string; the boolean collapse currently lives in mode-2 `SM_ACOMP`/`SM_LCOMP` (NOT yet on `BB_ALT`).
- [x] **RK-BB-4c (mode-4 junctions) ✅** (Opus 4.8, 2026-05-29, one4all `216f22cd`). Route (i): junction collapse added to shared `rt_acomp`/`rt_lcomp` (`src/runtime/rt/rt.c`), mirroring the mode-2 `SM_ACOMP`/`SM_LCOMP` interpreter cases. The `SM_ACOMP`/`SM_LCOMP` x86 templates already emit `mov edi,<op>; call rt_acomp`/`rt_lcomp` — the work lives in those runtime helpers, so this is FACT-clean (no template byte change). When a popped operand is `rk_junction_is()` true → `rk_junction_collapse(scalar,jct,op,numeric)` (1 acomp / 0 lcomp); push scalar+`LAST_OK=1` on hit else FAIL. `rk_junctions` mode-4 GREEN. Mode-3 junctions correct too (same helpers) but dormant (MODE3-DISPATCH-GAP).
- [x] **RK-BB-4d edges — precedence + nesting ✅** (Opus 4.8, 2026-05-29, one4all `0a5352e3`+`1652aeb9`). (2) PRECEDENCE: new `jct_expr` grammar tier (`raku.y`) makes infix `|`/`&` bind tighter than comparison (real Raku); `$x == 1|2|5` → `$x == any(1,2,5)`. Comparisons take `jct_expr` operands; parser regenerated, net-zero new conflicts. (1) NESTED MIXED-FLAVOR: SOH-leak fixed via EOT(`\x04`)-terminated junction rep — builder appends `\x04`; `rk_junction_collapse` scans scalars to SOH-or-EOT and skips nested `\x03…\x04` spans by depth count, recursing on the opaque span. `50&(50|60)` etc. now correct. Probes `rk_junction_prec`, `rk_junction_nest` added. (3) var round-trip + string-relop collapse already worked. REMAINING sliver: `^`(one) infix not lexed; only `one(...)` constructor.
- [x] **RK-BB-5.0..5.3 ✅** (Opus 4.8, 2026-05-29, one4all `36e41ed6`). List/array Seq consumers landed as pure value helpers in `raku_builtins_byname.c` (flatten SOH-array args into segments; no emitted x86, FACT-clean; reachable mode-2 `sm_interp` + mode-4 `rt_call`; byte-identical across modes). **5.0 `reverse`** (`a4bc02d4`) eager-drain reorderer; `for reverse(...)` rides the existing `for CALL(...)→$v` materialization branch. **5.1 `unique`+`sum`** (`8b10f978`) dedup-first-occurrence + numeric fold (INTVAL all-integral else REALVAL). **5.2 `join`** (`ed321adc`) `join(SEP,LIST)` fold-to-string; composes with reverse. **5.x array-arg coverage** (`f9425b68`, test-only) — confirmed reverse/unique/sum/join all work on push-built `@arrays`. **5.3 comma-list array initializer `my @a = e1,e2,...`** (`36e41ed6`) — the REAL gap behind `my @a=1,2,3` parse errors (NOT @-args, which already worked). Two `raku.y` productions (untyped+typed) build `ASSIGN(@a, __rk_arr(...))`; lookahead `;`(single-expr) vs `,`(comma-list) is a clean LALR split → **net-zero new conflicts (still 30 s/r)**; parser regenerated via `scripts/regenerate_parser_and_lexer_from_sources.sh` recipe (bison 3.8.2). New `__rk_arr` builtin packs args into an in-order SOH-array. Probes: rk_reverse, rk_unique_sum, rk_join, rk_seq_consumers_arr, rk_array_literal. **GATE-RK mode-2 28→33/40, GATE-RK4 mode-4 29→34/40; smoke 5/5, siblings icon/prolog/snobol4/snocone 5/5/13/5, FACT 0, all commits, no regressions.** DEFERRED: parenthesized `my @a=(1,2,3)` (list-atom, conflict-prone); `.method(N)` forms (`.tail`/`.head`/`.reverse`) need method-call-with-args parsing; `zip`/`cross` multi-Seq drivers need a nested-tuple representation.
- [x] **RK-BB-5.4a (`.method` list-method forms) ✅** (Opus 4.8, 2026-05-29). `.reverse`/`.unique`/`.sum`/`.elems`/`.head(N)`/`.tail(N)` routed from `TT_METHCALL` (after class static-resolution miss) and `TT_FIELD` (bare postfix) to the list-context value helpers, ahead of the class-oriented `raku_mcall`/`FIELD_GET` fallbacks (`raku_is_listmeth` whitelist, gated `g_lang==LANG_RAKU`). New `head`/`tail` value builtins in `raku_builtins_byname.c` (trailing arg = count N; bare form defaults N=1) modelled on `reverse`. Also widened the `for`-CALL materialise guard (`lower_every`) to accept `TT_METHCALL`/`TT_FIELD` list-method invocants (`raku_methform_listmeth`), so `for @a.reverse -> $x`/`for @a.head(N) -> $x` materialise-then-iterate (previously ran away — guard keyed only on `TT_FNC`). Pure value helpers, no emitted x86 (FACT-clean); byte-identical mode-2/mode-4. Class methods/fields untouched (rk_class26 unchanged). Probe `rk_listmeth`. Commits `dbb3d15f` (postfix) + `91bfae91` (for-form). DEFERRED: `.join` (invocant/arg order swapped vs free-fn `join`, which already works).
- [x] **RK-BB-5.4b (parenthesized array literal) ✅** (Opus 4.8, 2026-05-29, `56a30122`). `my @a = (e1, e2, ...)` via two initializer-only `raku.y` productions (untyped + typed) mirroring the 5.3 bare comma-list: `KW_MY [IDENT] VAR_ARRAY '=' '(' expr ',' arg_list ')' ';'` → `ASSIGN(@a, __rk_arr(...))`. Restricting the paren-list to the **initializer RHS** (NOT a general atom) keeps it **NET-ZERO new conflicts (still 30 s/r)** — a general-atom `'(' expr ',' arg_list ')'` form added +2 (method-chain/hash-subscript interactions) and was reverted. Single-element paren `(7)` stays scalar via the unchanged `'(' expr ')'`; bare comma-list + scalar paren coexist. Parser regenerated (bison 3.8.2). Probe `rk_paren_array`.
- [ ] **RK-BB-5.4c (`zip`/`cross`) — DEFERRED, own session** — multi-Seq drivers where each output element is itself a list, so it needs a **nested-tuple representation** (STX-within-SOH or similar) that `for`/`say`/`.elems` consumers must understand. NOT a pure value helper (broad blast radius); the goal groups these as "(later)". Recommend a fresh session with full budget.

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
bash /tmp/gate_rk3.sh                  # GATE-RK3 mode-3 native (recreate from prior handoff if absent)
```

## Gates

```
GATE-RK    test_raku_ir_rungs.sh        # mode-2, must hold/improve
GATE-RK4   test_raku_mode4_rung.sh      # mode-4 vs .expected, must hold/improve
GATE-RK3   /tmp/gate_rk3.sh             # mode-3 native, must hold/improve
GATE-RK-SM test_smoke_raku.sh           # smoke must hold
```

## Watermark

```
RK-NFA-1b DONE (Opus 4.8, 2026-05-29, one4all `6b593da8`). raku_nfa_to_bb — NFA →
  ISOLATED BB_NFA_* graph builder (BB_LANG_RKU), the prereq for mode-4 emission. In
  raku_nfa_bb.c: nfa_kind_to_bb 1:1 Nfa_kind→BB_NFA_* (CHAR/ANY/CLASS/SPLIT/EPS/BOL/
  EOL/CAP_OPEN/CAP_CLOSE/ACCEPT), one BB_t per state, γ=out1-node β=out2-node(SPLIT)
  ω=NULL, payload CHAR ival=char / CLASS sval=32-byte cset / CAP ival=group-idx,
  entry=start node; NULL on Phase-2 kinds. raku_re.h fwd-decls it (no BB.h pull-in).
  Verified standalone: graph faithfully mirrors the NFA across L1-L15 (node count ==
  state count, ports wired, entry correct, csets/chars/caps carried). Pure graph
  construction, NO x86, dead-code-until-RK-NFA-4 (no caller yet) → can't regress.
  Gates unchanged: m2 41/42, m4 42/42, smoke 5/5, SNOBOL4 iso M2 19/0 M4 18/1, FACT 0.
  NEXT: RK-NFA-4 — NEW src/emitter/BB_templates/bb_nfa_*.cpp (FACT-pure, four-port,
  isolated; opcode names from Nfa_kind) + SM_BB_INVOKE over the raku_nfa_to_bb graph
  on the ~~ path; GATE rk_re33/34/35 mode-4 via BB, SNOBOL4 pattern-rung suite
  byte-unchanged. Then RK-NFA-5 (mode-3 native, closes the 6 CRASHes).

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

GATE-RK   mode-2:                41/42  (+all 6 regex; only rk_stdio39 fidelity non-bug left)
GATE-RK4  mode-4:                42/42  PERFECT (all regex + rk_stdio39 pass on the byname path)
GATE-RK3  mode-3 native:         not re-run (RK-NFA-1e is mode-2/4-dispatch + lowering; mode-3 regex
                                 still CRASH via MODE3-DISPATCH-GAP — closes when BB_NFA_* emission lands)
Smoke raku/icon/prolog/snobol4/snocone: 5/5/5/13/5  HOLD
SNOBOL4 pattern-rung suite:               BYTE-IDENTICAL M2 19/0 M4 18/1 (isolation proven)
bison s/r conflicts: 30 (unchanged — VAR_FH split + FH/regex production added zero)
FACT RULE grep:   0
Build:            clean
```

## Remaining mode-3 native (CRASH 6)

- CRASH `rk_re32/33/34/35/37`, `rk_regex23` — regex now PASSES mode-2 AND mode-4 (RK-NFA-1e), but
  mode-3 `--run` still CRASHes: Raku `--run` emits no output for ANY program (MODE3-DISPATCH-GAP,
  pre-existing) and the regex builtins are on the SM byname path, which the honest mode-3 native
  flow (`SCRIP_M3_NATIVE=1`) doesn't reach. Lights up when the BB_NFA_* emission path (RK-NFA-4/5)
  lands OR the dispatch gap closes.
- `rk_junctions` mode-3: junctions correct (collapse in rt_acomp/rt_lcomp) but Raku `--run` emits no
  output for ANY program (MODE3-DISPATCH-GAP, pre-existing) — lights up free when that gap closes.

## NEXT — BB_NFA_* emission path, or RK-BB-5.4c (zip/cross)

RK-NFA-1e CLOSED the whole mode-2/mode-4 regex cluster via the SM byname dispatch path (+ capture
disambiguation + subst write-back). The verdict/capture/global/subst SEMANTICS are now proven in
modes 2 and 4. What remains is the BB ladder destination — moving regex onto the ISOLATED `BB_NFA_*`
opcode family (NOT SNOBOL4's pattern opcodes), so mode-3/mode-4 run through emitted templates rather than the C
matcher:
**(a)** RK-NFA-1b — `raku_nfa_to_bb(Raku_nfa*) → BB_graph_t*` state→node walk via `Nfa_state.bb_id`.
**(b)** RK-NFA-4 — NEW `src/emitter/BB_templates/bb_nfa_*.cpp` (FACT-pure, four-port, isolated;
  derive every opcode name from `Nfa_kind`: `BB_NFA_CHAR/ANY/CLASS/SPLIT/EPS/BOL/EOL/CAP_OPEN/
  CAP_CLOSE/ACCEPT`). GATE: rk_re33/34/35 mode-4 via BB; SNOBOL4 pattern-rung suite byte-unchanged.
**(c)** RK-NFA-5 — mode-3 native, closes the 6 CRASHes; default `~~`→BB.
Or **RK-BB-5.4c** (`zip`/`cross`) — multi-Seq drivers, each output element a list → needs a
nested-tuple rep (STX-within-SOH); NOT a pure value helper, broad blast radius, own session.


## Open questions for Lon

Resolved (2026-05-27): 100% template emission via BB/SM/XA only.

Pending:
- **Q5.** Union-clobber proper fix. TT_SUB_DECL uses `v.ival` for nparams AND wants `v.sval` for name. Move nparams to a side-channel so `v.sval = name` semantics is restored.
- **Q9-Q12.** RK-BB-4 directives — see substrate audit above.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
