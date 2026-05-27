# GOAL-RAKU-BB.md — Raku: goal-directed ~20% onto shared BB generators

**Repo:** one4all + corpus + .github
**Sister:** GOAL-ICON-BB.md (kinds REUSED) · GOAL-RAKU-FRONTEND.md.
**Prereq:** HEADQUARTERS PP-1..6 ✅. BB-TEMPLATE-LADDER invariants 0..9 apply.

## Two IRs

- **SM** — flat stack-machine spine (`src/include/SM.h`).
- **BB** — four-port Byrd-box graph (`src/include/BB.h`). Kinds are **language-agnostic**.
  `BB_graph_t.lang` tags origin (`BB_LANG_RKU=6`); node kinds are reused.

SM emits `SM_BB_SWITCH` with `a[2].i` tag handing control to a BB graph.
Tags: `SM_BBSW_ICN_GEN` (0x49434E47), `SM_BBSW_PL_ENTRY` (0x504C454E),
`SM_BBSW_RK_GEN` (0x524B474E "RKGN"). Raku reuses the ICN_GEN emit-time
contract verbatim — `sm_bb_switch.cpp` / `emit_sm.c` / `sm_interp.c` arms
accept both tags.

**Where Raku sits:** Icon/Prolog are ~100% BB. SNOBOL4/Snocone/Rebus are mixed.
Raku today is ~100% eager SM in practice; the goal-directed ~20% is what
this goal moves onto shared BB kinds.

**Rules (RULES.md):** no C Byrd boxes; no SM/BB walking at runtime in modes 3/4;
ports are α/β/γ/ω; no `rt_*`/`raku_*` *port-logic* helpers (conversion/effect
helpers via `@PLT` are fine). X86 arms only.

## The insight (validated by RK-BB-1)

Per docs.raku.org: almost everything generative in Raku produces a **`Seq`**.
`gather`/`take`, `…`, lazy ranges, `map`, `grep` — all "generate a Seq" on demand.
ONE four-port pull protocol (yield-one-at-β = Icon `BB_SUSPEND`/`BB_EVERY` PUMP)
suffices; every generative construct is a PRODUCER or CONSUMER of it. A would-be
10-kind ladder collapses to ~3 rungs on already-templated shared kinds.

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
| `gather { … take … }`, `…` operator | `BB_SUSPEND` + `BB_EVERY` PUMP | RK-BB-2 |
| lazy `map` / `grep` | `BB_ITERATE` consumer (γ predicate for grep) | RK-BB-3 |
| junctions `any`/`all`/`one`/`none`, infix `\|`/`&` | `BB_ALTERNATE` + Bool-collapse on ω/γ | RK-BB-4 |

**STAYS eager SM:** scalar builtins (`uc`/`lc`/`substr`/`trim`/`index`/`rindex`),
`say`/`print`, arithmetic, hash/array element ops, class/method dispatch,
`sort` (whole-list), `try`/`CATCH` (the existing inline `raku_exc_*` SM is the
right shape).

**SPLIT OUT to GOAL-RAKU-PAT-BB:** regex / grammar backtracking. SNOBOL4 pattern
axis (`BB_SCAN`+`BB_PAT_*`) plus Prolog `BB_ONCE`+OR-retry for rule selection.
Heaviest lift; defer until SNOBOL4-BB and PROLOG-BB land more rungs. Today's
eager `raku_nfa_exec` stays.

## ⛔ No `rt_*`/`raku_*` port-logic helpers

Never add `raku_seq_pull` / `rk_take_yield` / `raku_grep_step` / junction
dispatch helpers. Port logic (α/β/γ/ω) lives in the shared `bb_*.cpp` templates,
emitted inline as x86. If a rung "needs" a new `raku_*` helper, the lowering is
wrong — fix the BB graph, not the runtime.

## Ladder steps

- [x] **RK-BB-1** ✅ (2026-05-27, Opus, one4all `13cef01a`) — lazy inclusive range
  `for $a..$b -> $i` → shared `BB_TO_BY`. `lower_raku_range` synthesizes
  `TT_TO_BY`, reuses `lower_icn_expr_top`, retags `BB_LANG_RKU`. `lower_for_range`
  gated `LANG_RAKU && !exclusive`. Arms widened in `sm_bb_switch.cpp` /
  `emit_sm.c` / `sm_interp.c`. `bb_to_by.cpp` REUSED unchanged. GATE-RK4 +
  `run_raku_via_x86_backend.sh` + `rk_range_for` test added. Shared runtime fix:
  `rt_nv_set` made non-consuming (peek) so mode-4 STORE_VAR matches mode-2.
  Open follow-on (RK-BB-1b): exclusive `..^` + non-literal-bound ranges
  (currently fall through to eager SM).

- [x] **RK-BB-2** ✅ (2026-05-27, Opus 4.7, one4all `d08237e0`) — KEYSTONE lazy `Seq` box.
  `gather`/`take` + `…` → `BB_SUSPEND`+`BB_EVERY` PUMP. REUSE `bb_upto.cpp`.
  `test/raku/rk_gather.raku` PASSES `--compile` (mode-4): byte-exact `10\n20\n30\ndone\n`.
  - Step 1 ✅ (one4all `2f2aed25`) — `lower_icn_proc_body` accepts TT_SUB_DECL;
    hoist registers `__gather_N` in proc_table.
  - Step 2 ✅ (one4all `340b804d`) — `TT_SUSPEND` case in `lower_icn_expr_node`
    emits `BB_SUSPEND` node (Raku-gated via `cfg->lang`).
  - Step 3 ✅ (one4all `8a046af1`) — `lower_every`/`lower_iterate` accept
    LANG_RAKU; have_switch guard prevents PUSH_VAR a[0] clobber.
  - Step 4 ✅ (one4all `e8568ee4`) — `bb_suspend.cpp` template authored:
    literal-int fast-path pushes DESCR_t{DT_I, val_i} onto r12 via
    `rt_push_int@PLT` (TEXT) or inline 16-byte stack push (BINARY).
  - Step 5 ✅ (one4all `e8568ee4`) — `emit_core.c` walk_bb_node: BB_SUSPEND
    peeled off bb_stub group → routes to `bb_suspend(nd)`.
  - Step 6 ✅ (one4all `d08237e0`) — UNBLOCKED. Three-edit patch in lower.c:
    (a) `lower_hoist_gather_in_expr`: `def->v.sval = intern(gname)` →
        `def->v.ival = 0`. The v.sval/v.ival union-clobber was causing
        `lower_icn_proc_body` to read garbage as nparams (Open Q5).
    (b) `lower_stmt` RAKU+TT_SUB_DECL branch: skip body emission when the
        proc name starts with `__gather_`. Body lives in the BB graph;
        emitting at top-level orphans it (stack underflow on startup).
    (c) `lower_expr_inner` TT_SUB_DECL case: same defensive skip; keeps
        `SM_PUSH_NULL` contract intact.
    lower_icn_proc_body builds the BB graph (BB_SEQ→3×BB_SUSPEND); lower_fnc
    routing emits `SM_BB_SWITCH(SM_BBSW_RK_GEN, bb_idx)` at every call site;
    sm_bb_switch.cpp dispatches via bb_seq → bb_suspend (template emission).
    NOT needed: the separate `lower_raku_proc_body()` the handoff anticipated.
    The existing path works once nparams is correct. Open follow-on
    (RK-BB-2b): mode-2 still stack-underflows on `rk_gather` (bb_exec.c has
    no executor for BB_SUSPEND) — a separate Icon-shared goal per the
    handoff's gating comment in TT_SUSPEND.

- [ ] **RK-BB-3** — lazy `map`/`grep` as Seq CONSUMERS. REUSE `bb_iterate.cpp`;
  grep adds γ-port predicate test (loop on false, γ on true, ω on source ω).
  Migrate `lower.c:1872-1881` off eager `SM_CALL_FN raku_map`/`raku_grep` for
  the lazy path. `rk_map_grep_sort24.raku` under `--compile` (sort stays eager).

- [ ] **RK-BB-4** — junctions + infix `|`/`&` → `BB_ALTERNATE` with Bool-collapse
  policy on ω/γ. REUSE `bb_gen_alt.cpp`/`bb_alt.cpp`. Add junction test.

- [ ] **RK-BB-5..N** — `reverse`/`tail`/`from-loop` as Seq consumers, one rung
  each. `zip`/`cross` = multi-Seq drivers (later).

## Rung methodology (mostly REUSE)

Per rung: (1) lower the Raku construct to the shared BB kind via
`lower_raku_*` (parallel `lower_icn_*`); (2) confirm existing `bb_<kind>.cpp`
covers it (Icon proved most cases); (3) only if Raku semantics differ, extend
the shared template behind a `lang==BB_LANG_RKU` guard (last resort — prefer
making the lowering match the template); (4) run GATE-RK4 + GATE-PK + GATE-RK
(mode-2) + smoke. Commit when the Mode-4 golden matches and nothing regresses.

## Test corpus — REUSE

`test/raku/*.{raku,expected}` (30 cases). The job is mode-4 conformance to
those goldens (the Prolog GATE-4 pattern), not correctness-from-zero — mode-2
already runs them. Add NEW flat files only for laziness probes the eager suite
can't express (e.g. `(1..Inf)[4]` that must terminate).

## Mode-3 (`--run`) — needs a Lon directive

RULES.md sanctions exactly one temporary SM-walk exception (Prolog `--run`,
AGW-1c). Do NOT route Raku `--run` through `sm_interp_run` without a Lon
directive. Mode-4 is this ladder's target; Mode-3 follows for free when the
templates land (same `bb_*.cpp` serves both per ARCH-SCRIP §"Mode 4").

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
GATE-PK    test_per_kind_diff.sh        # currently segfaults (NOT this goal — see watermark)
GATE-RK    test_raku_ir_rungs.sh        # mode-2, must hold/improve
GATE-RK4   test_raku_mode4_rung.sh      # mode-4 vs .expected, must hold/improve
GATE-RK-SM test_smoke_raku.sh           # smoke must hold
```

## Watermark

```
one4all: d08237e0 (RK-BB-2 step 6 ✅ — three-edit unblock: union-clobber fix + body-orphan suppress)
.github: HEAD (this update)
corpus:  unchanged

Gates at d08237e0 (2026-05-27, Opus 4.7, RK-BB-2 ✅ rk_gather PASSES mode-4):
  GATE-RK mode-2:  8/30   HOLD  (BB_SUSPEND has no bb_exec.c executor — separate Icon goal)
  GATE-RK4 mode-4: 9/30   ✅ rk_gather flipped 8→9
  Smoke raku:      5/0    HOLD
  Smoke icon:      5/5    HOLD
  Smoke prolog:    5/5    HOLD
  Icon all rungs:  198/34/36 HOLD
  Prolog mode-4:   4/4    (was carried 1/4; unrelated upstream improvement)
  GATE-PK: ⛔ harness segfault — INHERITED FROM upstream 6deb9f71 (SBL-ANY-1
           + flat-driver α-label fix). Pre-6deb9f71 baseline was 455/64/590/6.
           Owed: SBL-ANY session.
  FACT RULE grep:  0
  Build:           clean

⛔ RK-BB-2 STEP 6 ✅ COMPLETE (2026-05-27, Opus 4.7, commit d08237e0):

Three surgical edits in src/lower/lower.c (only file touched, +27/-5):

(1) lower_hoist_gather_in_expr (~L2202): the Open Q5 union-clobber.
    `def->v.sval = intern(gname)` clobbered v.ival (same union), so
    lower_icn_proc_body read garbage as nparams → body_off overshot
    proc->n → NULL return on every Raku TT_SUB_DECL. Fix: v.ival = 0
    (nparams=0). Name lives in c[0]->v.sval (TT_VAR), already correct.

(2) lower_stmt RAKU+TT_SUB_DECL branch (~L1787): skip body emission
    when proc name starts with __gather_. Hoisted gather procs are
    driven via SM_BB_SWITCH(RK_GEN) at the call site; their body lives
    in the BB graph. Emitting at top-level orphaned it before main
    started → stack underflow on startup.

(3) lower_expr_inner TT_SUB_DECL case (~L1965): same defensive skip.
    SM_PUSH_NULL still emitted to preserve the contract.

Diagnostic path (probes removed before commit):
  [DBG-procbody] both main AND __gather_0 → body_irb=(nil) initially.
  [DBG-subdecl] __gather_0 had proc->n=4 children:
    [TT_VAR(5), TT_SUSPEND(50), TT_SUSPEND(50), TT_SUSPEND(50)] —
    BB graph should have been trivial to build.
  After v.ival=0 fix: body_irb=0x37bdbad0 — BB graph built.
  SM dump count: 49 → 25 after orphan-emit suppression.

NOT needed: the separate lower_raku_proc_body() the prior handoff
anticipated. lower_icn_proc_body widened in Step 1 already handles
TT_SUB_DECL correctly once nparams is right.

End-to-end verification via run_raku_via_x86_backend.sh:
  ./scrip --compile rk_gather.raku → .s → as → ld → ./a.out
  Output: 10\n20\n30\ndone\n — byte-exact to .expected.

OPEN: RK-BB-2b — mode-2 still stack-underflows on rk_gather. bb_exec.c
has no executor for BB_SUSPEND (TT_SUSPEND case in lower_icn.c gates on
BB_LANG_RKU specifically because Icon `suspend` would break rung03 if
BB_SUSPEND emitted with no mode-2 handler). Adding a mode-2 BB_SUSPEND
executor is a separate cross-language session (Icon-shared) — see the
gating comment in lower_icn.c TT_SUSPEND case (~L651).

NEXT: RK-BB-3 — lazy map/grep as Seq CONSUMERS. BB_ITERATE consumer +
γ-port predicate test for grep. Migrate lower.c:1872-1881 off eager
SM_CALL_FN raku_map / raku_grep for the lazy path. Reuse bb_iterate.cpp
(Icon proved most cases). Verify rk_map_grep_sort24.raku under --compile.
```

## Open questions for Lon

ALL FOUR RESOLVED (2026-05-27, Lon): 100% template emission via BB/SM/XA only.

1. ~~`lower_gather_hoist_pass` retarget (Path α) vs replace (Path β)?~~
   **→ Path β** (direct BB_SUSPEND lowering — cleaner BB graph; eager-SM
   intermediate would need unwinding later).
2. ~~`bb_upto.cpp` REUSE — literal vs structural?~~ **→ Structural.**
   Write new `bb_suspend.cpp` using `bb_upto.cpp`'s loop+yield as reference.
3. ~~Junction Boolean-collapse — shared `BB_ALTERNATE` guard vs SM wrapper?~~
   **→ Shared `BB_ALTERNATE` with `lang==BB_LANG_RKU` guard.** Port logic
   belongs in the template.
4. ~~GOAL-RAKU-PAT-BB — stub now vs defer?~~ **→ Defer.** Wait for
   SNOBOL4-BB and PROLOG-BB BB_SCAN/BB_ONCE machinery to mature.

NEW open item (deferred to a separate session):

5. **Union-clobber proper fix.** TT_SUB_DECL currently uses `v.ival` for
   nparams AND wants `v.sval` for name. Move nparams to a side-channel
   (leading TT_VLIST child, TT_ATTR, or separate tree_t field) so
   `v.sval = name` semantics is restored, and retire the polyglot.c c[0]
   fallback. Touches every TT_SUB_DECL reader.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
