# GOAL-RAKU-BB.md — Raku: goal-directed ~20% onto shared BB generators

**Repo:** one4all + corpus + .github
**Sister:** GOAL-ICON-BB.md (kinds REUSED) · GOAL-RAKU-FRONTEND.md
**Prereq:** HEADQUARTERS PP-1..6 ✅. BB-TEMPLATE-LADDER invariants 0..9 apply.

## Two IRs

- **SM** — flat stack-machine spine (`src/include/SM.h`).
- **BB** — four-port Byrd-box graph (`src/include/BB.h`). Kinds are **language-agnostic**. `BB_graph_t.lang` tags origin (`BB_LANG_RKU=6`); node kinds are reused.

SM emits `SM_BB_SWITCH` with `a[2].i` tag handing control to a BB graph. Tags: `SM_BBSW_ICN_GEN` (0x49434E47), `SM_BBSW_PL_ENTRY` (0x504C454E), `SM_BBSW_RK_GEN` (0x524B474E "RKGN"). Raku reuses the ICN_GEN emit-time contract verbatim — `sm_bb_switch.cpp` / `emit_sm.c` / `sm_interp.c` arms accept both tags.

**Where Raku sits:** Icon/Prolog are ~100% BB. SNOBOL4/Snocone/Rebus are mixed. Raku today is ~100% eager SM in practice; the goal-directed ~20% is what this goal moves onto shared BB kinds.

**Rules (RULES.md):** no C Byrd boxes; no SM/BB walking at runtime in modes 3/4; ports are α/β/γ/ω; no `rt_*`/`raku_*` *port-logic* helpers (conversion/effect helpers via `@PLT` are fine). X86 arms only.

## The insight (validated by RK-BB-1)

Per docs.raku.org: almost everything generative in Raku produces a **`Seq`**. `gather`/`take`, `…`, lazy ranges, `map`, `grep` — all "generate a Seq" on demand. ONE four-port pull protocol (yield-one-at-β = Icon `BB_SUSPEND`/`BB_EVERY` PUMP) suffices; every generative construct is a PRODUCER or CONSUMER of it. A would-be 10-kind ladder collapses to ~3 rungs on already-templated shared kinds.

## Port semantics (identical to Icon generators)

| Port | Direction | Raku meaning |
|---|---|---|
| γ | inherited DOWN | `take` yield / next Seq element |
| ω | inherited DOWN | exhaustion (Seq drained; junction collapsed; grep all-false) |
| α | synthesized UP | fresh-pull entry (first `.pull-one`) |
| β | synthesized UP | resume entry (next `.pull-one` after a yield) |

Driver = **`BB_PUMP`**. NOT Prolog's `BB_ONCE`.

## Pipeline

```
Raku source → frontend (raku.y/.l)
  → SM spine: scalar/eager → SM_CALL_FN
             generative   → lower_raku_* → BB_graph(lang=BB_LANG_RKU)
                          → SM_emit_sii(SM_BB_SWITCH, NULL, bb_idx, SM_BBSW_RK_GEN)
  → SHARED templates (already filled): bb_to_by.cpp, bb_upto.cpp,
                                       bb_iterate.cpp, bb_gen_alt.cpp
  → emitted x86 (Mode 4)
```

## Moves to BB vs stays SM

**MOVES (goal-directed, REUSE shared kinds):**

| Raku construct | shared BB kind | rung |
|---|---|---|
| lazy range `$a..$b`, `$a,$b ... $c` | `BB_TO_BY` | RK-BB-1 ✅ |
| `gather { … take … }`, `…` operator | `BB_SUSPEND` + `BB_EVERY` PUMP | RK-BB-2 ✅ |
| lazy `map` / `grep` | `BB_ITERATE` consumer (γ predicate for grep) | RK-BB-3 ✅ |
| junctions `any`/`all`/`one`/`none`, infix `\|`/`&` | `BB_ALTERNATE` + Bool-collapse on ω/γ | RK-BB-4 |

**STAYS eager SM:** scalar builtins (`uc`/`lc`/`substr`/`trim`/`index`/`rindex`), `say`/`print`, arithmetic, hash/array element ops, class/method dispatch, `sort` (whole-list), `try`/`CATCH` (existing inline `raku_exc_*` SM is the right shape).

**SPLIT OUT to GOAL-RAKU-PAT-BB:** regex / grammar backtracking. Defer until SNOBOL4-BB and PROLOG-BB land more rungs.

## ⛔ No `rt_*`/`raku_*` port-logic helpers

Never add `raku_seq_pull` / `rk_take_yield` / `raku_grep_step` / junction dispatch helpers. Port logic (α/β/γ/ω) lives in the shared `bb_*.cpp` templates, emitted inline as x86. If a rung "needs" a new `raku_*` helper, the lowering is wrong — fix the BB graph, not the runtime.

## Ladder steps

- [x] **RK-BB-1** ✅ (Opus, one4all `13cef01a`) — `for $a..$b -> $i` → shared `BB_TO_BY`. `lower_raku_range` synthesizes `TT_TO_BY`, reuses `lower_icn_expr_top`, retags `BB_LANG_RKU`. `lower_for_range` gated `LANG_RAKU && !exclusive`. Arms widened in `sm_bb_switch.cpp` / `emit_sm.c` / `sm_interp.c`. Shared runtime fix: `rt_nv_set` made non-consuming (peek). Follow-on (RK-BB-1b): exclusive `..^` + non-literal-bound ranges fall through to eager SM.

- [x] **RK-BB-2** ✅ (Opus 4.7, one4all `d08237e0`) — KEYSTONE lazy `Seq` box. `gather`/`take` + `…` → `BB_SUSPEND`+`BB_EVERY` PUMP. REUSE `bb_upto.cpp`. `bb_suspend.cpp` authored (`e8568ee4`). `lower_icn_proc_body` accepts TT_SUB_DECL. `bb_seq.cpp` multi-yield driver via `.data resume_addr` slot. `rk_gather.raku` PASSES `--compile` byte-exact `10\n20\n30\ndone\n`. Open follow-on (RK-BB-2b): mode-2 BB_SUSPEND executor missing — Icon-shared cross-language session.

- [x] **RK-BB-3** ✅ (Opus 4.7) — lazy `map`/`grep` as Seq CONSUMERS. Decomposed into:
  - **3.0+3d infra** (`fcac4ab3`) — `raku_try_call_builtin_by_name` + `raku_try_mutating_builtin_by_name` dispatchers chained into `sm_interp.c` SM_CALL_FN + `rt.c` rt_call. Handlers for elems/arr_get/substr/index/rindex/uc/lc/chars/length/trim/sort + push/pop/arr_set.
  - **3.0a** (`ba481112`) — (1) `lower_fnc` c[0]-dup suppression for LANG_RAKU (raku.y vestigial duplicate). (2) `rt_set_lang(int)` + XA_FILE_HEADER prologue emits `mov edi, <g_lang>; call rt_set_lang@PLT` so mode-4 libscrip_rt.so stamps g_lang before any rt_call. (3) `trim` aliased to `raku_trim`. 8→9 mode-2, 9→10 mode-4.
  - **3.0b** (`7a60d30e`) — mutators wired: `lower_fnc` push/pop prepends `SM_PUSH_LIT_S vname` when first real arg is TT_VAR; nargs+1. TT_ARR_SET same prepend, nargs 3→4. SM_CALL_FN + rt_call peel args[0].s as vname when fn ∈ {push, pop, arr_set} AND args[0].v == DT_S. 9→10 mode-2, 10→11 mode-4 (+rk_arrays).
  - **3a** (`706e2828` mode-2/3 + `cc6c1a06` mode-4) — `for @arr -> $v` polymorphism for `BB_ITERATE`. `lower_raku_iterate_arr` builds 1-node BB graph (`sval=intern(arr_vname)`, `cfg->lang=BB_LANG_RKU`, α/β self-loop). `lower_every` pattern-matches `TT_EVERY(TT_ITERATE(TT_VAR(arr), sval=$v), body)`. Discriminator: `BB_t.sval` presence (no new fields per PEERS RULE). Mode-2 `bb_exec.c`: sval-polymorphic branch, fetches via `NV_GET_fn` every call, scans `\x01`-bytes, yields GC-allocated substring. Mode-4 `bb_iterate.cpp` Raku MEDIUM_TEXT arm: `.data` slots (name asciz + counter quad), NV_GET_fn@PLT call, **slen-fallback strlen@PLT** (STRVAL hardcodes `.slen=0`), GC_malloc fresh NUL-terminated segment copy (rt_push_str needs ptr to NUL not (ptr,len) — downstream fputs reads to NUL).
  - **3b/c** (`42d2a367` + binding-fix `af0df613`) — pure lowering transform `lower_raku_map_or_grep`. Eager-drain materialization: synthesizes `__map_acc_N`/`__grep_acc_N`, builds BB graph via `lower_raku_iterate_arr`, γ-body stores yielded elem → `_` then for map lowers body + 3-arg push; for grep JUMP_F-gates the push (pushes `_`, not pred). ZERO new BB kinds, ZERO new runtime helpers, 100% template emission. Binding-fix: `strip_sigil` rewrites VAR_SCALAR pre-AST so body's `$_ * 2` parses to `TT_BINOP(TT_VAR("_"), …)`. Hardcoded `"$_"` at γ-store and grep push arg → bare `"_"`. `rk_for_array_underscore.raku` added as permanent regression probe.

- [x] **RK-BB-SEGFAULT-CLUSTER** ✅ ALL THREE BUGS — Opus 4.7, 2026-05-27:

  - **bug 1** (`0f3561c0`) — union-clobber dereference in `polyglot_init`. `proc->v.sval && *proc->v.sval` UNSAFE for TT_SUB_DECL because raku.y:340 clobbers v.sval via `v.ival=np` union write. np>0 → union reads as 0x1, 0x2 → passes NULL check, segfaults at `*v.sval`. Fix: for TT_SUB_DECL, never trust v.sval — always use `c[0]->v.sval`. polyglot.c +20/-3.

  - **bug 2+3** (`2a70abed`, Opus 4.7) — multi-sub Raku now structurally correct. Three surgical edits in `src/lower/lower.c` (+56/-8):
    - **2a (`lower_stmt` ~L1987):** RAKU+TT_SUB_DECL inline emission gated on `_is_main` only. Other subs emit no top-level body; reached via SM_CALL_FN to named LABEL skeleton. `__gather_*` still skips per RK-BB-2.
    - **2b (`lower_proc_skeletons` ~L2370):** TT_SUB_DECL body extraction from `proc->c[nparams+1..]` (not `c[2]`). `g_lang=LANG_RAKU` during body lowering (was unconditional LANG_ICN). Skip `main` and `__gather_*` from skeleton-body emission (main is inlined at top level; __gather_* lives in BB graph).
    - **3 (`build_proc_scope` ~L2288):** TT_SUB_DECL branch — params at `proc->c[1..v.ival]` as flat TT_VAR children, body walk at `proc->c[nparams+1..]` for local-var slots. scope_add idempotent by name.
    
    Gates: GATE-RK mode-2 14 → **16** (+rk_interp, +rk_map_grep_sort24), GATE-RK4 15 HOLD, smokes 5/5/5/13 HOLD, broker Icon 198 HOLD, FACT RULE 0.

  - **bug 4 ✅** (Opus 4.7, 2026-05-27, one4all `ecd561b1`) — `lower_return` Raku return-value preservation. One-file change to `src/lower/lower.c` `lower_return` (+2 -0): added `else if (t->n > 0 && t->c[0] && g_lang == LANG_RAKU) { lower_expr(t->c[0]); }` branch between the `g_sc_func_name` (Snocone) branch and the generic VOID_POP branch. Leaves the result on stack-top where `SM_RETURN` (sm_interp.c:1432) expects it — no VOID_POP. Gates: GATE-RK mode-2 **16 → 18** (+rk_subs, +rk_combinator). GATE-RK4 mode-4 **15 HOLD** (still blocked on SM_LOAD_FRAME template absence). Smokes raku/icon/prolog/snobol4 **5/5/5/13 HOLD**. Broker Icon **198 HOLD**. FACT RULE 0. Build clean. `rk_try_catch25` is a separate try/CATCH issue, not return-value-related.

- [~] **RK-BB-4 substrate audit** — Opus 4.7, 2026-05-27. Probe-based audit found goal text's "REUSE bb_gen_alt.cpp/bb_alt.cpp" is unfounded. SEVEN GAPS verified by inspection:
  1. raku.l no KW_ANY/KW_ALL/KW_ONE/KW_NONE; no single-char `|`/`&` (only `||`/`&&`).
  2. TT_ALT overloaded — Raku `||` reuses SNOBOL4 pattern-alt AST kind (raku.y:426). Works by coincidence on truthiness via lower_pat_expr → SM_PAT_ALT. Out of scope but flagged.
  3. bb_exec.c:1618-1620 BB_ALTERNATE mode-2 executor is a no-op: `nd->value = FAILDESCR; return nd->ω;`.
  4. bb_alternate.cpp mode-4 template DOES NOT EXIST. Would fall through default stub.
  5. bb_alt.cpp mode-4 template IS A STUB (37 lines, α→γ/β→ω passthrough only).
  6. bb_gen_alt.cpp IS A STUB (11 lines, returns empty string).
  7. Icon's TT_ALTERNATE lowers to BB_ALT (not BB_ALTERNATE) per lower_icn.c:1095. **BB_ALTERNATE is orphan.** Reusable substrate is BB_ALT — but mode-4 is a stub.
  
  `test/raku/rk_junctions.raku` + .expected committed as target probe (`4ee45eb7`). Fails at lex today (expected).

  **Open questions for Lon (Q9–Q12, gating any work):**
  - Q9: Introduce NEW TT kinds (TT_LOR/TT_LAND) for Raku `||`/`&&` to disentangle from SNOBOL4 patterns? Or defer.
  - Q10: BB_ALT (existing n-ary substrate, mode-4 stub) or finish orphan BB_ALTERNATE? Recommend BB_ALT.
  - Q11: Substrate-first (author BB_ALT mode-2 + mode-4, benefits Icon too) vs frontend-first eager (lex/parse + eager SM_CALL_FN, defer substrate)? Recommend (b) frontend-first.
  - Q12: Junction value representation. (i) tagged `\x02any\x02 1\x01 2\x01 3` string mirroring \x01-arrays, (ii) DT_JUNCT type tag, (iii) DT_DATA icn_type="junct". Recommend (i).

- [ ] **RK-BB-4-frontend** — pending Lon directive on Q9–Q12. Best case (path b): lexer + grammar + new TT_JUNCT_* kinds + `lower_raku_junction` eager SM mirror of RK-BB-3.0+3d. Worst case (path a): substrate-first — BB_ALT mode-2 executor + bb_alt.cpp mode-4 template + then frontend.

- [x] **RK-BB-SM-FRAME-MODE4** ✅ — Opus 4.7, 2026-05-28. Mode-4 named-sub dispatch+return. Pieces 4a (rt_frame_enter/leave/load/store in libscrip_rt, `d6fe17e2`), 4b (SM_LOAD/STORE_FRAME x86 templates, `7c9d4570`), 1-scaffold (rk_sub_lookup/rk_sub_label helpers, `3eece6a3`), and **1-WIRING** (`18c4820f`): sm_label_str emits `.Lrksub_<name>:`; sm_call_str emits `mov edi,np; call rt_frame_enter@PLT; call .Lrksub_<name>; call rt_frame_leave@PLT` for Raku user-subs (builtins fall through to CALL_FN/rt_call); void subs push SM_PUSH_NULL before trailing SM_RETURN for callsite VOID_POP balance. rk_subs == .expected. Recursion fact(5)=120, nested outer(4)=50. GATE-RK4 15→18 (+rk_subs/rk_combinator/rk_interp). All other gates HOLD. FACT RULE 0.

- [x] **RK-GIVEN-MODE4** ✅ — Opus 4.7, 2026-05-28 (one4all `5950356f`). Raku `given`/`when` mode-4. Was emitting `SM_PUMP_CASE` + `emit_thunk` subexprs — no x86 arm, and driving it would need runtime `sm_eval_subexpr` SM-walking (forbidden mode-4). Rewrote `lower_case` `is_raku` branch to a straight if-chain over already-templated opcodes (mirrors the non-raku CASE branch): topic → per-site-unique `__rk_case_topic_<seq>__` (nesting-safe); per arm PUSH topic; lower wval; `SM_ACOMP TT_EQ` (numeric) or `SM_LCOMP TT_LEQ` (string literal); `JUMP_F`; body (TT_PROGRAM walk); `JUMP end`; default last; trailing `PUSH_NULL` for callsite VOID_POP balance. SM_PUMP_CASE now has zero emit sites. rk_given == .expected. rk_given18 still FAILs but on a pre-existing for-over-pushed-array segfault (test_case fails identically on clean baseline; verified via stash-rebuild) — orthogonal. GATE-RK4 18→19 (+rk_given). All other gates HOLD. FACT RULE 0.

- [ ] **RK-BB-5..N** — `reverse`/`tail`/`from-loop` as Seq consumers, one rung each. `zip`/`cross` = multi-Seq drivers (later).

## Rung methodology (mostly REUSE)

Per rung: (1) lower the Raku construct to the shared BB kind via `lower_raku_*` (parallel `lower_icn_*`); (2) confirm existing `bb_<kind>.cpp` covers it (Icon proved most cases); (3) only if Raku semantics differ, extend the shared template behind a `lang==BB_LANG_RKU` guard (last resort — prefer making the lowering match the template); (4) run GATE-RK4 + GATE-PK + GATE-RK (mode-2) + smoke. Commit when the Mode-4 golden matches and nothing regresses.

## Test corpus — REUSE

`test/raku/*.{raku,expected}` (33 cases). The job is mode-4 conformance to those goldens (the Prolog GATE-4 pattern), not correctness-from-zero — mode-2 already runs them. Add NEW flat files only for laziness probes the eager suite can't express (e.g. `(1..Inf)[4]` that must terminate).

## Mode-3 (`--run`) — needs a Lon directive

RULES.md sanctions exactly one temporary SM-walk exception (Prolog `--run`, AGW-1c). Do NOT route Raku `--run` through `sm_interp_run` without a Lon directive. Mode-4 is this ladder's target; Mode-3 follows for free when the templates land.

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
# GATE-PK currently SEGFAULTS — see watermark; do not block on it.
```

## Gates

```
GATE-PK    test_per_kind_diff.sh        # currently segfaults (NOT this goal)
GATE-RK    test_raku_ir_rungs.sh        # mode-2, must hold/improve
GATE-RK4   test_raku_mode4_rung.sh      # mode-4 vs .expected, must hold/improve
GATE-RK-SM test_smoke_raku.sh           # smoke must hold
```

## Watermark

```
one4all: 5950356f (RK-GIVEN-MODE4 — Raku given/when via mode-4-safe if-chain)
.github: HEAD (handoff — given/when landed; GATE-RK4 18->19)
corpus:  unchanged

Gates at RK-GIVEN-MODE4 DONE (2026-05-28, Opus 4.7):
  GATE-RK mode-2:  18/33  HOLD
  GATE-RK4 mode-4: 19/33  +1 (rk_given; prior session +3 rk_subs/rk_combinator/rk_interp)
  Smoke raku:      5/0    HOLD
  Smoke icon:      5/5    HOLD
  Smoke prolog:    5/5    HOLD
  Smoke snobol4:   13/0   HOLD
  Broker Icon:     198    HOLD (test_icon_all_rungs PASS=198)
  Icon mode-4:     5/5    HOLD
  GATE-PK: ⛔ harness segfault — INHERITED (not this goal).
  FACT RULE grep:  0
  Build:           clean

PROGRESS THIS SESSION (1 commit, all gates HOLD/improve, no regressions):
  WIRING  18c4820f  Two template edits + one void-sub lowering fix:
    - sm_jumps.cpp sm_label_str: .Lrksub_<name>: emitted at named SM_LABEL
      site when rk_sub_lookup(name)>=0. Includes stage2.h + emit_bb.h added.
    - sm_calls.cpp sm_call_str: mov edi,np; call rt_frame_enter@PLT;
      call .Lrksub_<name>; call rt_frame_leave@PLT for Raku user-subs;
      builtins fall through to unchanged CALL_FN/rt_call path. Same includes.
    - lower.c lower_proc_skeletons: void Raku subs push SM_PUSH_NULL before
      trailing SM_RETURN (call-as-stmt VOID_POP balance). Value-returning subs
      ret early, unaffected.

rk_subs mode-4: 14 / hello raku / 7 / positive / zero / negative == .expected.
RECURSION VERIFIED: fact(5)=120 (256-frame stack + call/ret nesting holds).
NESTED CALLS VERIFIED: outer(4)=inner(4)*10=50.

rk_try_catch25 still fails (separate try/CATCH issue, untouched).
```

⛔ NEXT SESSION — Remaining 14 mode-4 Raku FAILs, triaged into families (2026-05-28):
  - REGEX/NFA (6): rk_re32/33/34/35/37, rk_regex23 — DEFERRED to GOAL-RAKU-PAT-BB per goal doc.
  - HASHES (2): rk_hash17, rk_hashes — %h<k>, keys/values/exists/delete (runtime hash builtins).
  - JUNCTIONS (1): rk_junctions — BLOCKED on Lon Q9-Q12 (RK-BB-4 directives).
  - I/O (2): rk_fileio38, rk_stdio39 — file handles, $*STDOUT/STDERR.
  - EXCEPTIONS (1): rk_try_catch25 — try/CATCH/die.
  - given18 (1): rk_given18 — given/when itself WORKS; blocked on a separate
    pre-existing for-loop-over-pushed-array segfault (also kills test_case in
    the SNOBOL4 broad corpus). Best next Raku rung: fix that array/for path,
    which unblocks rk_given18 AND likely several array tests.
  HASHES or the array/for-loop fix are the best next rungs (self-contained, no
  external directive needed). Regex deferred; junctions blocked on Lon.

  (historical) Remaining mode-4 Raku FAILs to triage, likely candidates:
  - rk_try_catch25 — try/CATCH (separate exception-machinery issue, pre-existing).
  - Inspect the other failing goldens via:
      for f in test/raku/*.raku; do
        b=$(basename "$f" .raku)
        bash scripts/run_raku_via_x86_backend.sh "$f" 2>&1 \
          | diff - "test/raku/$b.expected" >/dev/null 2>&1 \
          && echo "PASS $b" || echo "FAIL $b"
      done
  - Group failures by construct; each is its own rung.

OPTIONAL HARDENING (not blocking): rt_load_frame/rt_store_frame already exist
(piece 4a) and SM_LOAD_FRAME/STORE_FRAME templates exist (piece 4b); deeper
recursion / >RT_FRAME_SLOT_MAX-param stress untested but architecturally bounded
(RT_FRAME_STACK_MAX=256, RT_FRAME_SLOT_MAX=64).

ORIGINAL FULL DESIGN (4 pieces) retained below for context.

The mode-4 x86 backend has ZERO frame-slot mechanism. `emit_sm.c:1076` emits the literal
text `"UNHANDLED SM_LOAD_FRAME"` for unrecognized opcodes — when the assembler hits this
it errors `no such instruction: 'unhandled SM_LOAD_FRAME'` (the as-error in earlier sessions).

WHY RAKU IS THE FIRST CASE TO HIT THIS:
  - Icon mode-4 corpus passes 5/5 because Icon procs route through BB graphs and
    `icn_bb_pump_proc_by_name` (bypassing SM entirely per "Icon/Prolog are ~100% BB").
  - Raku eager subs route through SM_CALL_FN → SM_LABEL → body using SM_LOAD_FRAME,
    which has no x86 dispatch arm.

THE FOUR PIECES MISSING IN MODE-4:

  1. **User-sub callsite dispatch.** Today SM_CALL_FN template emits
     `lea rdi,[name]; mov esi,nargs; call rt_call@PLT`. `rt_call` resolves
     user-subs via `chunk_reg_lookup` (SNOBOL4 `Define()` chunks) — which doesn't
     contain Raku named subs. So the call falls through to INVOKE_fn which is
     SNOBOL4 dispatch, and ends in "Undefined function". Solution: in
     `sm_calls.cpp` MEDIUM_TEXT X86 arm, look up `pSM->a[0].s` in
     `g_stage2.proc_table[]` (already visible to emitter per emit_sm.c:886);
     if found with entry_pc >= 0, emit a direct intra-binary call.

     ⚠ LABEL OFF-BY-ONE — VERIFIED THIS SESSION (do NOT use `call .L<entry_pc>`):
       `proc_table[].entry_pc` resolves to the **named SM_LABEL's own pc**
       (e.g. double=1, greet=12, add=21, classify=32 in rk_subs), via
       `sm_label_pc_lookup` returning `instrs[i].a[1].i`. BUT the named
       SM_LABEL emits NO `.L<pc>:` symbol — the `LABEL` macro expands to
       empty (sm_jumps.cpp:116). The `.L<pc>:` that DOES get emitted is at
       `entry_pc + 1` (the first body instr), because `pc_used_mark(pc+1)`
       fires for named labels (emit_sm.c:881). Empirically: `.L1` is NOT in
       the .s, but `.L2` IS. So `call .L<entry_pc>` → assembler "undefined
       label .L1" error.
     RECOMMENDED FIX (cleaner than pc-arithmetic): make the named SM_LABEL
       emit a real symbol at its own site. In `sm_jumps.cpp` sm_label_str
       MEDIUM_TEXT arm, when `pSM->a[0].s` non-empty, prepend a stable
       symbol like `.L_sub_<name>:` (or reuse `.L<entry_pc+1>`). Then the
       callsite emits `call .L_sub_<name>` — no pc arithmetic, robust against
       label renumbering. `pSM->a[0].s` is already available in that arm
       (currently unused via `(void)pSM`).

  2. **Frame push at proc entry.** Args sit on vstack at callsite; callee
     needs them in slots 0..nparams-1. Two options:
     (a) Callsite emits frame-enter helper before call: `rt_frame_enter(nparams)`
         pops nparams from vstack, copies to slot[0..nparams-1], pushes the
         frame. Then `call .L<pc>`. Cleaner separation; works.
     (b) Lowering emits `SM_FRAME_ENTER nparams` op right after SM_LABEL for
         each user sub, template emits `mov edi,nparams; call rt_frame_enter@PLT`.
         Cleaner from SM dump perspective; needs new SM opcode.
     Recommend (b) — clean SM-level visibility.

  3. **Frame pop at proc exit.** Symmetric. Either:
     (a) `lower_return` for LANG_RAKU emits `SM_FRAME_LEAVE` before `SM_RETURN`.
     (b) New combined `SM_RETURN_FRAME` op.
     Recommend (a) — keeps SM_RETURN simple, paired with (b) of #2.

     ⚠ CALL/RET CONVENTION — VERIFIED THIS SESSION:
       The `RETURN` macro (sm_returns.cpp:26) is bare x86 `ret`. SM_RETURN
       MEDIUM_TEXT (op==SM_RETURN) emits `RETURN` preceded by `pop rbp` ONLY
       when `g_in_define_body` is set (sm_returns.cpp:43). So if Raku subs
       are entered via plain x86 `call .L_sub_<name>` (recommended piece #1),
       the matching `ret` pops the call's return address and returns to the
       caller — works natively, NO setjmp/longjmp needed. TWO CONSTRAINTS:
         (i) The proc body must leave the MACHINE stack (rsp) balanced — it
             must NOT net-push anything on the x86 stack. The SM vstack is
             heap/separate so SM pushes are fine; only watch for any template
             that does raw `push` without matching `pop`.
         (ii) `g_in_define_body` MUST be false during Raku sub-skeleton
             emission, else SM_RETURN emits a spurious `pop rbp` with no
             matching `push rbp` (Raku subs entered via `call` have no
             rbp prologue) → stack corruption. VERIFY the lower_proc_skeletons
             Raku path leaves g_in_define_body unset. If it can't be guaranteed,
             gate the `pop rbp` on a new g_in_raku_sub flag instead.
       TRAILING DEAD RETURN: proc bodies emit `[explicit ret]; VOID_POP; RETURN`.
       With call/ret the explicit return's `ret` fires first; the trailing
       VOID_POP;RETURN is dead (harmless). Subs with no explicit return (e.g.
       greet) fall through to the single trailing RETURN=ret. Both correct.

  4. **`rt_load_frame` / `rt_store_frame` in libscrip_rt.** New small file
     `src/runtime/rt/rt_frame.c` mirroring the icn_runtime.c shape (a frame
     stack of small DESCR_t arrays). Functions:
       `void rt_frame_enter(int nparams)` — pops nparams from vstack into a
         new IcnFrame (or local equivalent); pushes frame.
       `void rt_frame_leave(void)` — pops frame. Return value is already on
         vstack from `lower_return` LANG_RAKU branch (bug 4 fix).
       `void rt_load_frame(int slot)` — peeks current frame, pushes slot[i]
         onto vstack.
       `void rt_store_frame(int slot)` — pops vstack into slot[i].

  5. **Templates.** New file `src/emitter/SM_templates/sm_frame_slots.cpp`
     with `sm_load_frame` / `sm_store_frame` (and optionally `sm_frame_enter`
     / `sm_frame_leave`) functions, each with MEDIUM_MACRO_DEF + MEDIUM_TEXT
     arms. Wire into `sm_op_is_dispatched` in `emit_core.c:821`. Wire into
     `codegen_sm_dispatch` in the place where existing templates are listed.

ESTIMATED SCOPE: 6-10 hours careful work. High risk of regressing Icon
mode-4 corpus (5/5) and broker Icon (198) if SM_CALL_FN template touches
arms other than the user-sub one. Must run all four smokes + GATE-RK4 +
GATE-PK4 (icon mode-4) + broker after EVERY substantive edit.

ALTERNATIVE LIGHTWEIGHT PATH (NOT recommended but documented):
Bypass slots — modify lowering to emit `SM_PUSH_VAR vname` / `SM_STORE_VAR vname`
for Raku params instead of `SM_LOAD_FRAME slot` / `SM_STORE_FRAME slot`.
Mode-4 `rt_nv_get`/`rt_nv_set` then "just works". Cost: params live in
global name table, not stack frame — broken for recursion, broken for
nested sub calls. Cheap demo win but architecturally wrong; reject.

⛔ END NEXT-SESSION GUIDANCE

## Open questions for Lon

ALL FOUR RESOLVED (Lon, 2026-05-27): 100% template emission via BB/SM/XA only.

1. ~~`lower_gather_hoist_pass` retarget vs replace?~~ **→ Path β** (direct BB_SUSPEND lowering).
2. ~~`bb_upto.cpp` REUSE — literal vs structural?~~ **→ Structural.**
3. ~~Junction Boolean-collapse — shared `BB_ALTERNATE` guard?~~ **→ Shared with `lang==BB_LANG_RKU` guard.**
4. ~~GOAL-RAKU-PAT-BB — stub now vs defer?~~ **→ Defer** until SNOBOL4-BB/PROLOG-BB mature.

NEW open items:

5. **Union-clobber proper fix.** TT_SUB_DECL uses `v.ival` for nparams AND wants `v.sval` for name. Move nparams to a side-channel (leading TT_VLIST child, TT_ATTR, or separate tree_t field) so `v.sval = name` semantics is restored. Touches every TT_SUB_DECL reader.

6. **Polymorphic BB_ITERATE or new BB_ARR_ITERATE kind?** Recommend polymorphic per "kinds are language-agnostic." (Resolved in RK-BB-3a — went polymorphic via `BB_t.sval` presence discriminator.)

7. **FIELD_GET_fn / NV_GET_fn call from inside a BB template** — fits "no port-logic helpers" rule? They're data-fetch, not α/β/γ/ω routing. Treating as allowed. (Used by RK-BB-3a.)

8. **`my @x = map { ... } @y` materialization** — eager-drain (resolved in RK-BB-3b: chose eager-drain for first cut) or stay lazy as a Seq box (future rung).

9–12. **RK-BB-4 directives** — see "RK-BB-4 substrate audit" above. Pending.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
