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

- [ ] **RK-BB-2** ⛔ STEPS 1-5 LANDED, STEP 6 PARTIAL — KEYSTONE lazy `Seq` box. `gather`/`take` + `…`
  → `BB_SUSPEND`+`BB_EVERY` PUMP. Retarget `lower_gather_hoist_pass` so `take`
  becomes γ-yield in the Seq box (lower-risk than full replacement). REUSE
  `bb_upto.cpp`. Verify `test/raku/rk_gather.raku` under `--compile`.
  - Step 1 ✅ (one4all `2f2aed25`) — `lower_icn_proc_body` accepts TT_SUB_DECL;
    hoist registers `__gather_N` in proc_table.
  - Step 2 ✅ (one4all `340b804d`) — `TT_SUSPEND` case in `lower_icn_expr_node`
    emits `BB_SUSPEND` node (Raku-gated via `cfg->lang`).
  - Step 3 ✅ (one4all `8a046af1`) — `lower_every`/`lower_iterate` accept
    LANG_RAKU; have_switch guard prevents PUSH_VAR a[0] clobber.
  - Step 4 ✅ (one4all `e8568ee4`) — `bb_suspend.cpp` template authored:
    literal-int fast-path pushes DESCR_t{DT_I, val_i} onto r12 via
    `rt_push_int@PLT` (TEXT) or inline 16-byte stack push (BINARY). α→push+γ,
    β→ω. Dynamic operand passthrough mirrors bb_to_by H-3 TODO.
  - Step 5 ✅ (one4all `e8568ee4`) — `emit_core.c` walk_bb_node: BB_SUSPEND
    peeled off bb_stub group → routes to `bb_suspend(nd)`.
  - Step 6 ⛔ PARTIAL (one4all `6ea3637d`) — three downstream pieces authored,
    blocked by upstream. (a) `bb_seq.cpp` NEW: multi-yield driver using
    .data resume_addr slot + indirect-jmp on β. (b) emit_core: BB_SEQ peeled
    off bb_stub → routes to `bb_seq(nd)`. (c) `lower_fnc` detects `__gather_*`
    is_generator calls and emits `SM_BB_SWITCH(SM_BBSW_RK_GEN)` in place of
    `SM_CALL_FN`. BLOCKER: `lower_icn_proc_body` returns NULL for EVERY Raku
    TT_SUB_DECL (both `main` and synthesized `__gather_N`) — TT_SUSPEND lowering
    never reached. Need `lower_raku_proc_body()` parallel to `lower_pl_predicate`,
    handling the strict gather-body shape (BB_SUSPEND chain). See
    HANDOFF-2026-05-27-OPUS-RK-BB-2-STEPS-4-6-PARTIAL.md for the diagnostic.

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
one4all: 6ea3637d (RK-BB-2 step 6 PARTIAL — bb_seq + dispatch peel + lower_fnc routing; blocked by lower_icn_proc_body NULL on Raku)
.github: HEAD (this update)
corpus:  unchanged

Gates at 6ea3637d (2026-05-27, Opus 4.7, RK-BB-2 steps 4-5 ✅ + step 6 PARTIAL):
  GATE-RK mode-2:  8/30   HOLD
  GATE-RK4 mode-4: 8/30   HOLD
  Smoke raku:      5/0    HOLD
  Smoke icon:      5/5    HOLD
  Smoke prolog:    5/5    HOLD
  Icon all rungs:  198/34/36 HOLD
  Prolog mode-4:   1/4    HOLD (carried)
  GATE-PK: ⛔ harness segfault — INHERITED FROM upstream 6deb9f71 (SBL-ANY-1
           + flat-driver α-label fix). Pre-6deb9f71 baseline was 455/64/590/6.
           Owed: SBL-ANY session.
  FACT RULE grep:  0
  Build:           clean

⛔ RK-BB-2 STEPS 4-5 ✅ DONE (2026-05-27, Opus 4.7, commit e8568ee4):

Step 4 (bb_suspend.cpp): four-port template. α reads pBB->α->ival (literal-int
  fast-path), pushes DESCR_t{DT_I, val_i} via rt_push_int@PLT (TEXT) or inline
  16-byte r12 push (BINARY), jmp γ. β: jmp ω. Dynamic operand passthrough mirrors
  bb_to_by H-3 TODO. FACT RULE clean; PEERS RULE clean.
Step 5 (emit_core.c): BB_SUSPEND peeled off bb_stub group → bb_suspend(nd).

⛔ RK-BB-2 STEP 6 PARTIAL (2026-05-27, Opus 4.7, commit 6ea3637d):

  (a) bb_seq.cpp NEW: multi-yield driver. .data resume_addr quad; outer α jmps
      child0_α; outer β load+indirect-jmp resume_addr. Per-child γ fixup writes
      resume_addr := next-child-α (or done-trampoline for last) then jmps outer γ.
      Each child's ω points at next child's α (substituted via emit_child_box_seq's
      lbl_ω repointing). n==0 guard preserves passthrough for non-gather BB_SEQ.
      MEDIUM_TEXT only; MEDIUM_BINARY stubbed.
  (b) emit_core.c: BB_SEQ peeled off bb_stub group → bb_seq(nd).
  (c) lower_fnc: detects Raku `__gather_*` is_generator proc calls, emits
      SM_BB_SWITCH(SM_BBSW_RK_GEN, bb_idx) in place of SM_CALL_FN. Mirrors
      lower_for_range's RK-BB-1 pattern.

  ⛔ BLOCKER: lower_icn_proc_body returns NULL for EVERY Raku TT_SUB_DECL.
  [DBG-procbody] proves both `main` AND `__gather_0` get body_irb=(nil).
  [DBG-tt_suspend] probe in lower_icn_expr_node's TT_SUSPEND case never fires —
  so the TT_SUSPEND lowering Step 2 added is currently UNREACHABLE. proc_table[].
  bb_idx stays -1 → lower_fnc routing falls through to default SM_CALL_FN →
  bb_seq.cpp and bb_suspend.cpp unreached.

  ROOT CAUSE LIKELY: lower_icn_expr_threaded_b (or an inner check) rejects Raku
  stmt shapes before reaching lower_icn_expr_node. For `__gather_0` body =
  3× TT_SUSPEND(TT_ILIT) — the simplest possible BB graph — yet still NULL.

  FIX (recommended next session): author lower_raku_proc_body() parallel to
  lower_pl_predicate, handling only the strict gather-body shape (BB_SUSPEND
  chain on simple operands). Gate at lower.c:2083 on
  proc->t==TT_SUB_DECL && name prefix "__gather_". See HANDOFF doc.

NEXT: RK-BB-2 step 6.1 (diagnose) → 6.2 (lower_raku_proc_body) → 6.3 (verify 9/30).
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
