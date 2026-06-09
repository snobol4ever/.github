# SESSION HANDOFF — 2026-05-27 (Opus 4.7) — RK-BB-2 PREREQ + scope-discovery deepening

**SCRIP HEAD: `50370f5a`** ✅ all gates HOLD
**.github HEAD: pending watermark update for GOAL-RAKU-BB**

---

## What was accomplished this session

Scope-discovery for RK-BB-2 went one level deeper than the prior Sonnet
handoff (HANDOFF-2026-05-27-RK-BB-2-SCOPE.md). The "five-step surface area
A–E" in that doc was correct as far as it went, but missed a foundation
issue that gates ALL of A–E: **Raku procs were absent from `proc_table`
entirely**, so even the existing SM-generator machinery had no entry to
dispatch to.

### Foundation bug — TT_SUB_DECL.sval was being clobbered (LANDED, `50370f5a`)

Traced inside the raku parser action for `sub IDENT '(' ')' block`:

```
DBG-SUBD57: ident=helper            ← yyvsp[-3].sval is "helper"
DBG-SUBD57: e.sval=(null)           ← AFTER leaf_sval, sval is null
DBG-ADDPROC: e.t=131 e.sval=(null)  ← propagated to add_proc, then polyglot
```

Root cause: `tree_t.v` is a `union { char *sval; long long ival; double dval; }`.
The Raku parser (raku.tab.c case 56/57) does:

```c
tree_t *e = leaf_sval(TT_SUB_DECL, ident);  // sets e->v.sval = ident
e->v.ival = (long long)nparams;              // OVERWRITES union — sval gone
```

The hoist pass at `lower.c:2132` escapes this only because it doesn't write
`v.ival` after `def->v.sval = intern(gname)`.

Workaround (committed): `polyglot.c` now falls back to `proc->c[0]->v.sval`
(the TT_VAR child the parser adds right after `leaf_sval`) when
`proc->v.sval` is NULL. One file, ~12 lines, fully documented inline.

Proper fix (deferred): move `nparams` off `v.ival` to a side-channel — either
an extra child node, or grow `tree_t` with a separate `int` field. Restoring
the single-meaning of `v.sval = name` cleans up many downstream paths and
removes the workaround at polyglot.c lines 116-138.

### Effect

`proc_count` is now > 0 for every Raku program. `proc_skeletons` produces real
`SM_LABEL helper` / `SM_LABEL main` entries. Existing Raku tests still pass
because the inlined-at-top-level body (the legacy `lower_stmt` LANG_RAKU
TT_SUB_DECL branch) still runs as before — the new proc skeletons are
empty stubs (`LABEL → RETURN`) because `lower_proc_skeletons` at lower.c:2088
looks for `TT_PROC_DECL && n >= 3`, which doesn't match TT_SUB_DECL.

### Gates (end of session)

```
GATE-RK   mode-2:           8/30   HOLD
GATE-RK4  mode-4:           8/30   HOLD
Smoke raku:                 5/0    HOLD
Smoke icon:                 5/5    HOLD
Smoke prolog:               5/5    HOLD
Icon all rungs:             198/34/36 HOLD
FACT RULE grep:             0
```

No counter movement; foundation in place for it.

---

## NEXT SESSION — RK-BB-2 proper. (added 2026-05-27, Opus 4.7)

**Fresh context required (~80%+).** With `proc_count > 0` for Raku, the
remaining work is mechanical — straight implementation of the BB_SUSPEND
template + lowering wiring per the directive "100% template emission via
BB/SM/XA templates."

### Direction confirmed by Lon (2026-05-27)

> "I'm with you on 100% code emission via ONLY BB/SM/XA templates despite the cost."

That settles all four open questions from GOAL-RAKU-BB.md:

1. **Path β** (direct BB_SUSPEND lowering, cleaner BB graph). Retargeting
   the hoist pass to feed an SM-shaped Seq box preserves an eager-SM
   intermediate that would need unwinding later.
2. **(b)** Write a new `src/emitter/BB_templates/bb_suspend.cpp`, using
   `bb_upto.cpp`'s loop+yield structure as the reference skeleton.
3. **Shared `BB_ALTERNATE` with `lang==BB_LANG_RKU` guard** for junctions
   (RK-BB-4 — port logic belongs in the template, not in an SM wrapper).
4. **Defer `GOAL-RAKU-PAT-BB`** — it reuses `BB_SCAN`/`BB_ONCE` from
   SNOBOL4-BB and PROLOG-BB; build on those after they mature.

### Concrete step list (in order, gate after each)

1. **Loosen `lower_icn_proc_body` (lower_icn.c:996)** to accept TT_SUB_DECL
   with body in `c[1..n-1]` (current code requires TT_PROC_DECL with
   `c[2]=TT_PROGRAM`). Two early-bail conditions to adjust:
   - `if (!proc || proc->t != TT_PROC_DECL) return NULL;` → also accept
     TT_SUB_DECL
   - body shape: `body_node = proc->n >= 3 ? proc->c[2] : NULL` (Icon) vs.
     for Raku, statements start at `c[1]` after the TT_VAR name child and
     run to `c[n-1]`. Build a synthetic body view (don't mutate the AST).

   Acceptance: `lower_icn_proc_body` called on a `__gather_N` TT_SUB_DECL
   returns a non-NULL `BB_graph_t*`. Verify via `--dump-sm` on
   rk_gather.raku showing `bb_idx` ≥ 0 in the SM_LABEL preamble.

2. **Add TT_SUSPEND case to `lower_icn_expr_node` (lower_icn.c)** that
   produces a `BB_SUSPEND` BB node with the expression as a child. Wire it
   into `lower_icn_expr_threaded_b` so its ports are stamped. Threading
   shape: the suspend's γ = ω_in (next-stmt entry — yielding-and-resuming
   the body's β re-fires the next stmt; for a bounded stmt-context suspend
   the protocol matches BB_TO_BY: α evaluates expr → yield via γ → on β
   advance to next-stmt).

   Note: `lower.c:2069` already detects BB_SUSPEND in the lowered body and
   sets `is_generator=1`. Once the BB graph emits these nodes, the existing
   generator-proc dispatch handles it for SM mode-2.

3. **Widen `lower_every` (lower.c:1461) and `lower_iterate` (lower.c:1557)**
   from `g_lang != LANG_ICN` to also accept LANG_RAKU. For the gather case,
   `lower_every`'s SM scaffold (SM_BB_SWITCH + JUMP back-edge) is the right
   shape — it just needs to fire for Raku. Acceptance: GATE-RK mode-2
   moves 8/30 → 9/30 (rk_gather passes).

4. **Write `src/emitter/BB_templates/bb_suspend.cpp`** with the four-port
   pull protocol for proc-body suspends:
   - **α (fresh):** evaluate expr operand via PEERS RULE
     (`bb_operand_aux_get`), push DESCR_t result onto value stack (r12
     convention or rt_push_*), jmp γ.
   - **β (resume):** caller's `every` re-entry. Resume = "advance to next
     stmt"; in a BB_SEQ body the SEQ's port-follower already handles this,
     so β = ω_in (the suspend node has no per-node retry — successive
     yields come from re-entering the SEQ, which finds the next BB_SUSPEND
     by following γ-chain).
   - **γ:** consumer takes value, will re-enter via β.
   - **ω:** unreachable in a body context; the BB_SEQ ω-edge carries
     exhaustion. Stub as `jmp lbl_γ` or fall-through.

   Use `bb_upto.cpp` lines 12-71 as the structural reference (TEXT mode
   with .data state slot, MEDIUM_TEXT + MEDIUM_BINARY arms).

5. **Wire `emit_core.c:532`** from `bb_stub` → `bb_suspend`. Add the
   `extern void bb_suspend(BB_t *);` declaration in `bb_templates.h`.

6. **Verify `sm_bb_switch.cpp` handles BB_SEQ-rooted graphs**
   (sm_bb_switch.cpp line 49 expects `g_stage2.sm.bb_table[idx]->entry`
   which for a proc body is `BB_SEQ`, not a leaf generator). The current
   ICN_GEN form calls `walk_bb_node_str_c(gen)` — for BB_SEQ this routes
   to `bb_stub` (line 517). Either:
   - Wire BB_SEQ to a new `bb_seq` template that walks γ-chain emitting
     each child inline, OR
   - Extend sm_bb_switch.cpp to detect BB_SEQ-rooted graphs and walk the
     chain explicitly before/after the four-port label dance.

   The first is cleaner per the directive (template-only emission, no
   walking outside templates) but is broader scope. The second is a
   one-template extension within sm_bb_switch.cpp's existing closure.

   **Lon decision needed** if scope explodes: extend sm_bb_switch.cpp
   inline (faster, contained) vs. write bb_seq.cpp (cleaner, more files
   touched). Recommendation: write bb_seq.cpp — it's the next natural
   ladder rung anyway (BB_SEQ comes up in every multi-stmt proc body)
   and matches the "100% template emission" directive.

### Acceptance for the rung

- GATE-RK mode-2: 8/30 → 9/30 (rk_gather)
- GATE-RK4 mode-4: 8/30 → 9/30 (rk_gather under `--compile`)
- Smoke raku: 5/0 HOLD
- Smoke icon: 5/5 HOLD; Icon all rungs: ≥ 198 HOLD
- Smoke prolog: 5/5 HOLD
- FACT RULE grep == 0

### Recommended order for the next session

```
Step 1 (lower_icn_proc_body TT_SUB_DECL)  → verify bb_idx ≥ 0 in dump-sm
Step 2 (TT_SUSPEND case)                   → verify BB_SUSPEND in graph
Step 3 (lower_every widen)                 → verify SM_BB_SWITCH emitted
Step 4 (bb_suspend.cpp)                    → verify text-mode x86 output
Step 5 (emit_core.c wire)                  → verify mode-2 → 9/30
Step 6 (sm_bb_switch BB_SEQ)               → verify mode-4 → 9/30
```

Each step independently verifiable. Commit after every step (or at every
gate-green checkpoint).

### Hazards / unknowns

- `lower_proc_skeletons` at lower.c:2088 reads `proc->c[2]` for Icon body;
  for Raku TT_SUB_DECL the body lives at `c[1..n-1]`. Will need a similar
  treatment to step 1 (synthetic view, or per-lang body indexing). The
  Raku case will require setting `g_lang = LANG_RAKU` instead of the
  hardcoded `LANG_ICN` at line 2086 — but this may interact with
  `lower_icn_proc_body` which expects Icon AST semantics. Test carefully.

- Existing Raku tests pass because of the inlined-at-top-level shortcut.
  Once `lower_proc_skeletons` actually lowers the body, that inlining
  becomes a duplicate emission. `lower.c:1739` (LANG_RAKU TT_SUB_DECL stmt
  branch) may need to early-exit when the proc is in `proc_table`. Mirror
  what Icon does at line 1719ish for TT_PROC_DECL stmts.

### DO NOT, this rung

- Do NOT touch SNOBOL4 / Snocone / Rebus / Icon / Prolog BB families.
- Do NOT add fields to BB_t (PEERS RULE / HQ Invariant 17).
- Do NOT add `rt_*` / `raku_*` port-logic helpers (RULES.md).
- Do NOT regenerate raku.tab.c from raku.y — the makefile has no bison
  rule and committed .tab.c is the source of truth; raku.y is documentation.

### Proper fix for the union-clobber (defer to a separate goal/session)

The polyglot.c workaround should be retired by:
1. Move `nparams` storage off `v.ival` (e.g., to a leading TT_VLIST child,
   or extend `tree_t` with a separate `int ival2` field — the latter
   doubles every node's size, so prefer (1) or a TT_ATTR side-channel).
2. Restore `v.sval = name` semantics on TT_SUB_DECL.
3. Revert the polyglot.c c[0] fallback.

This is mechanical but touches every TT_SUB_DECL reader (lower.c, polyglot.c,
ast_print.c, possibly more) — not a one-session task. Track separately if
desired.

---

## Session start for next session

```bash
git clone https://TOKEN@github.com/snobol4ever/.github /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/SCRIP /home/claude/SCRIP
git clone https://TOKEN@github.com/snobol4ever/corpus  /home/claude/corpus
cat /home/claude/.github/PLAN.md
cat /home/claude/.github/GOAL-RAKU-BB.md
cat /home/claude/SCRIP/SESSION-2026-05-27-OPUS-RK-BB-2-PREREQ.md  # this file
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && make -j4 scrip
bash /home/claude/SCRIP/scripts/test_raku_ir_rungs.sh     # Expect 8/30
bash /home/claude/SCRIP/scripts/test_raku_mode4_rung.sh   # Expect 8/30
bash /home/claude/SCRIP/scripts/test_smoke_raku.sh        # Expect 5/0
bash /home/claude/SCRIP/scripts/test_smoke_icon.sh        # Expect 5/5
bash /home/claude/SCRIP/scripts/test_smoke_prolog.sh      # Expect 5/5
```
