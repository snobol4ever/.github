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

  - **bug 4: lower_return discards Raku return value** ⛔ NEXT SESSION. SM dump of rk_subs shows correctly-shaped skeleton at PC 1-8: `LABEL "double"; LOAD_FRAME; COERCE_NUM; PUSH_LIT_I 2; COERCE_NUM; MUL; VOID_POP; RETURN`. The **VOID_POP before RETURN** discards the multiply result. `lower_return` (lower.c:1240) for the bare branch (no `g_sc_func_name`) emits `lower_expr; SM_VOID_POP; SM_RETURN`. SM_RETURN handler at sm_interp.c:1432 reads `st->stack[st->sp - 1]` as retval when `fr->retval_name` NULL — i.e., expects stack-top to be retval. **Fix:** add `LANG_RAKU` branch in `lower_return` that emits `lower_expr(t->c[0]); SM_RETURN` with NO VOID_POP. Without this, `return $n * 2` discards result; `say(double(7))` prints nothing, `add(3,4)` returns 0, `classify` returns garbage. Expected uplift: rk_subs + rk_try_catch25 flip green in mode-2; mode-4 follows (mode-4 also blocked on SM_LOAD_FRAME template missing — separate concern).

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
one4all: 2a70abed (RK-BB-SEGFAULT-CLUSTER bug 2+3 — TT_SUB_DECL skeleton + scope)
.github: HEAD (handoff — bugs 2+3 closed; bug 4 (lower_return) documented for next session)
corpus:  unchanged

Gates at RK-BB-SEGFAULT-CLUSTER bug 2+3 (2026-05-27, Opus 4.7):
  GATE-RK mode-2:  16/33  (+rk_interp, +rk_map_grep_sort24)
  GATE-RK4 mode-4: 15/33  HOLD
  Smoke raku:      5/0    HOLD
  Smoke icon:      5/5    HOLD
  Smoke prolog:    5/5    HOLD
  Smoke snobol4:   13/0   HOLD
  Broker Icon:     198    HOLD
  GATE-PK: ⛔ harness segfault — INHERITED. Owed: SBL-ANY session.
  FACT RULE grep:  0
  Build:           clean

rk_subs / rk_try_catch25 still fail (wrong output, not segfault):
  rk_subs:        prints only "hello raku" — bug 4 (lower_return VOID_POPs retval).
  rk_try_catch25: "Error 5 Undefined function" — try/CATCH-specific, separate.
  rk_interp:      now PASSES.
```

⛔ NEXT SESSION — RK-BB-SEGFAULT-CLUSTER bug 4 (lower_return Raku return-value):

ONE FILE TO TOUCH: src/lower/lower.c, function `lower_return` at L1240.

PROBLEM:
`return $n * 2` in a Raku sub produces SM `lower_expr(n*2); SM_VOID_POP; SM_RETURN`. The VOID_POP discards the multiply result. SM_RETURN handler at sm_interp.c:1432 reads `st->stack[st->sp - 1]` as retval when `fr->retval_name` is NULL — expects stack-top to be retval. So result is lost.

FIX SHAPE:
```c
static void lower_return(const tree_t *t)
{
    if (t->n > 0 && t->c[0] && g_sc_func_name) {
        lower_expr(t->c[0]);
        SM_emit_s(g_p, SM_STORE_VAR, g_sc_func_name);
        SM_emit(g_p, SM_VOID_POP);
    } else if (t->n > 0 && t->c[0] && g_lang == LANG_RAKU) {
        /* Raku: leave result on stack-top; SM_RETURN reads stack[sp-1]. */
        lower_expr(t->c[0]);
    } else if (t->n > 0 && t->c[0]) {
        lower_expr(t->c[0]); SM_emit(g_p, SM_VOID_POP);
    }
    SM_emit(g_p, SM_RETURN);
}
```

EXPECTED UPLIFT (mode-2): rk_subs flips (14→17 expected). rk_try_catch25 may flip too if its Error 5 is downstream of return-value loss; otherwise it's a separate try/CATCH issue.

MODE-4 BLOCKER (separate, also needs attention next session):
After bug 4, mode-4 rk_subs hits `as: Error: no such instruction: 'unhandled SM_LOAD_FRAME'` at multiple sites. The frame-slot read/write isn't emitted in mode-4 for Raku. SM_LOAD_FRAME / SM_STORE_FRAME templates either don't exist or aren't routed for LANG_RAKU. Search `sm_load_frame.cpp` / `walk_sm_instr` LOAD_FRAME branch in `emit_sm.c` — likely needs Raku-arm or polymorphic dispatch. Same shape as SM_LOAD_VAR but indexed via slot not name.

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
