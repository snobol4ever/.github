# SESSION HANDOFF — 2026-05-27 (Opus 4.7) — RK-BB-2 steps 4-5 ✅ + step 6 PARTIAL

**SCRIP HEAD: `6ea3637d`** ✅ all gates HOLD
**.github HEAD: pending — this file + PLAN.md + GOAL-RAKU-BB.md watermark**

---

## What landed this session

Two commits on SCRIP. Step 4-5 are clean and ready. Step 6 is partial — the
three downstream pieces are authored and build-clean, but a step-1-era upstream
bug, discovered via debug probes this session, blocks the counter from moving.

### Commit `e8568ee4` — RK-BB-2 steps 4-5 ✅

**Step 4: `src/emitter/BB_templates/bb_suspend.cpp`** — NEW four-port x86
template for BB_SUSPEND (Raku `take(E)` yield-one). One file per BB kind per
RULES.md.

- Literal-int fast-path: `pBB->α->t == BB_LIT_I` → read `pBB->α->ival` at
  emit time, push DESCR_t{DT_I, val_i} onto r12 value-stack.
- MEDIUM_TEXT: `mov rdi, val_i ; call rt_push_int@PLT ; jmp γ` for α; `jmp ω`
  for β. (TEXT path runs in mode-4 — r12 isn't set up there.)
- MEDIUM_BINARY: inline 16-byte DESCR_t push to r12 via four mov + add r12,16,
  then jmp γ rel32. β: jmp ω rel32. (BINARY path is brokered — r12 IS set up.)
- Dynamic operand (non-BB_LIT_I) falls through with port-passthrough (α→γ,
  β→ω), mirror of bb_to_by's H-3 TODO.
- No `rt_*` port-logic helpers; only `rt_push_int@PLT` (value-effect helper,
  permitted by RULES.md §"No rt_*/raku_* port-logic helpers").
- FACT RULE clean: all bytes via s_* / bytes() / u32le / u64le.
- PEERS RULE clean: no BB_t field added.

**Step 5: emit_core.c walk_bb_node dispatch** — peeled BB_SUSPEND off the
bb_stub group; now routes to `bb_suspend(nd)`. bb_templates.h gets the extern.
BB_PROC / BB_SCAN / BB_NONNULL / BB_INTERROGATE / BB_NOT / BB_PAT_CALLOUT stay
on bb_stub.

**Makefile**: bb_suspend.cpp added to both SCRIP_SRCS and the scrip target's
explicit per-file compile rules.

**Hazard found and fixed during step 4 authoring**: my opening block comment
included the string `s_*/bytes()` which contains a literal `*/` — closing the
comment prematurely and dumping the next 10 lines into the toplevel translation
unit. The em-dash `—` past the false comment-close then triggered an
extended-identifier error. Reworded to `s_* / bytes()`. Reproducible trap for
future template authors; consider adding a lint or banning `*/` from
single-line in-comment uses.

### Commit `6ea3637d` — RK-BB-2 step 6 (PARTIAL)

**(a) `src/emitter/BB_templates/bb_seq.cpp`** — NEW multi-yield driver for
Raku gather bodies (and any future BB_SEQ-of-yielders).

Design rationale: a single SM_BB_SWITCH β-entry label has to know which child
yielded last. We carry a `.data` quad slot per BB_SEQ — `resume_addr` — that
holds the address to jmp to on next β. Init=0; the SM_BB_SWITCH's own .byte
flag gates fresh-vs-resume entry above us, so we only see β after α has run
once and a child has populated resume_addr.

Per-child wiring (k in [0, n-1], last = n-1):
```
seq.α       :  .L<seq-id>_α      → jmp .L<seq-id>_s0_α
seq.β       :  .L<seq-id>_β      → load resume_addr, indirect jmp
stmt_k.α    :  .L<seq-id>_s<k>_α  (child's first-entry label)
stmt_k.γ    :  .L<seq-id>_s<k>_γ  (child's yield label — fixup defines here)
stmt_k.ω    :  if k<last → .L<seq-id>_s<k+1>_α (via emit_child_box_seq's lbl_ω repoint)
              if k==last → outer ω (passes through)
stmt_k.β    :  .L<seq-id>_s<k>_β  (currently unused — β re-entries flow via
                                   resume_addr, not via the child's own β label)
```

Per-child γ fixup (emitted by bb_seq between child texts):
```
.L<seq-id>_s<k>_γ:
    lea rax, [rip + resume_slot]
    lea rcx, [rip + <next-stmt-α-or-done>]
    mov [rax], rcx
    jmp <outer γ>
```

Done trampoline at the very end: `jmp <outer ω>`.

Reuses bb_binop_gen's `emit_child_box` pattern: repoint g_emit.lbl_*, then
`walk_bb_node_str_c(child)` to get the child's x86 as std::string, concatenate.

`n == 0` guard preserves the passthrough shape for non-gather BB_SEQ uses
(Icon/Snocone proc bodies traverse this template after the dispatch peel —
they have BB_SEQ-rooted bodies too, but their children aren't BB_SUSPEND, and
they're driven via SM_BB_PUMP_PROC, not SM_BB_SWITCH).

MEDIUM_TEXT only; MEDIUM_BINARY stubbed as passthrough (brokered binary
emitter doesn't exercise Raku today).

**(b) emit_core.c walk_bb_node dispatch** — peeled BB_SEQ off the bb_stub
group; routes to `bb_seq(nd)`. bb_templates.h gets the extern.

**(c) `src/lower/lower.c` lower_fnc** — at the top, detect Raku is_generator
proc calls by name prefix `__gather_` and emit
`SM_BB_SWITCH(SM_BBSW_RK_GEN, bb_idx)` in place of SM_CALL_FN. Mirrors
`lower_for_range`'s RK-BB-1 SWITCH-emission pattern. Falls through to default
lowering when `proc_table[pi].bb_idx == -1` (the proc body didn't successfully
lower to a BB graph). **The fallthrough fires every single call today** — see
blocker.

Makefile: bb_seq.cpp added to both SCRIP_SRCS and the scrip-target per-file
rules.

---

## ⛔ BLOCKER (discovered this session via debug probes)

`lower_icn_proc_body` returns NULL for EVERY Raku TT_SUB_DECL — both
top-level `main` AND the synthesized `__gather_N`. Confirmed via a `[DBG-procbody]`
fprintf at `lower.c:2084` immediately after the call: both procs print
`body_irb=(nil)`.

Crucially, a parallel `[DBG-tt_suspend]` probe placed at the top of
`lower_icn_expr_node`'s `TT_SUSPEND` case **never fires**. So Step 2's
`TT_SUSPEND → BB_SUSPEND` lowering is unreachable: something upstream rejects
the proc body before any TT_SUSPEND statement is visited.

The proc-body lowerer loops back-to-front calling
`lower_icn_expr_threaded_b(cfg, st, ...)` for each statement. A single NULL
return aborts the whole proc body (line 1088 in lower_icn.c). For `__gather_0`,
the body shape is:
```
TT_SUSPEND (TT_ILIT 10)     ← stmt 0
TT_SUSPEND (TT_ILIT 20)     ← stmt 1
TT_SUSPEND (TT_ILIT 30)     ← stmt 2
```
Every stmt is a TT_SUSPEND with a literal int operand — about as simple as a
BB graph can get. Yet not one of them reaches the TT_SUSPEND case in
`lower_icn_expr_node`. The only way that's possible is if
`lower_icn_expr_threaded_b` rejects before it calls `lower_icn_expr_node` —
or `lower_icn_expr_node` has a case that matches TT_SUSPEND-like input ABOVE
the TT_SUSPEND case in the switch and returns NULL there. But TT_SUSPEND is
the only case for that node kind; no earlier case can match it.

A second possibility: `BB_alloc(4096, BB_LANG_RKU)` at lower_icn.c:1061 itself
returns NULL when the lang tag is BB_LANG_RKU (=6). Worth a 30-second test.

A third possibility: `lower_icn_expr_threaded_b` performs structural checks
on the AST node (`is_leaf`, `is_suspendable`) and one of those returns NULL
on TT_SUSPEND, bypassing the inner `lower_icn_expr_node` call. Verify by
adding a `[DBG-thread] e->t=%d` probe at the top of
`lower_icn_expr_threaded_b`.

For `main`, the body shape is:
```
TT_EVERY (TT_ITERATE v <gather-call>) <body>
TT_SAY  (TT_QLIT "done")
```
Different shape than __gather_0's all-TT_SUSPEND, but ALSO returns NULL.
Likely culprit: `TT_EVERY` has no case in `lower_icn_expr_node`. The Icon
mode-2 path for TT_EVERY is in lower.c's `lower_every`, not in lower_icn.c.
So `lower_icn_proc_body` was already failing on Icon procs whenever their
body contained certain Icon-specific stmt kinds — but for Icon those failures
were tolerated because the fallback SM path handled everything. For Raku
this becomes load-bearing.

**Easiest path forward** (recommended): skip the Icon-centric
`lower_icn_proc_body` for Raku entirely. Write a `lower_raku_proc_body()`
that handles only the shapes Raku gather bodies need (initially: a sequence
of TT_SUSPEND with simple operands). The TT_SUB_DECL "main" doesn't need a
BB graph — it stays on the inline-stmt SM path. Only the hoisted
`__gather_N` procs need BB graphs, and their bodies are by construction
strictly TT_SUSPEND-statements (per `lower_hoist_gather_in_expr` at
lower.c:2152).

In lower_proc_skeletons (lower.c:2083), gate on `proc->t == TT_SUB_DECL &&
name starts with "__gather_"` → use the dedicated Raku lowerer. All other
TT_SUB_DECL keep returning NULL from `lower_icn_proc_body` (today's behavior).

---

## What HOLDS at this HEAD

```
GATE-RK   mode-2:           8/30   HOLD
GATE-RK4  mode-4:           8/30   HOLD
Smoke raku:                 5/0    HOLD
Smoke icon:                 5/5    HOLD
Smoke prolog:               5/5    HOLD
Icon all rungs:             198/34/36 HOLD
FACT RULE grep:             0
Build:                      clean
```

No counter movement — the rung still needs the blocker fix.

---

## NEXT SESSION

**Fresh context required (~80%+).** The work below is contained but needs
patience and methodical probing.

### Step 6.1 — Diagnose the blocker

Re-introduce two short-lived debug probes (REMOVE before commit):

```c
/* At lower_icn.c top of lower_icn_expr_threaded_b: */
fprintf(stderr, "[DBG-thread] e->t=%d cfg->lang=%d\n", (int)e->t, (int)cfg->lang);

/* At lower_icn.c top of lower_icn_expr_node: */
fprintf(stderr, "[DBG-node] e->t=%d cfg->lang=%d\n", (int)e->t, (int)cfg->lang);
```

Run `./scrip --dump-sm --interp test/raku/rk_gather.raku 2>&1 | grep DBG`.
If `[DBG-thread]` fires with `e->t=131` (TT_SUSPEND? — actually wait, 131 is
TT_SUB_DECL, TT_SUSPEND is in the high TT_* range) and `[DBG-node]` never
fires with TT_SUSPEND, the gap is in `lower_icn_expr_threaded_b`'s pre-call
guards. If `[DBG-node]` fires with a kind we DON'T handle, we know which
case is missing.

Cross-reference numeric tt values with `src/include/ast.h:25-` to translate
`e->t=N` to the kind name.

### Step 6.2 — Author `lower_raku_proc_body`

In `src/lower/lower_icn.c` (or a new `src/lower/lower_raku.c` parallel to
`lower_pl.c`), write:

```c
BB_graph_t *lower_raku_proc_body(tree_t *proc) {
    /* Strictly for hoisted __gather_N procs: a sequence of TT_SUSPEND stmts
       whose operand is a simple literal or var. No control flow inside the
       gather body — that's enforced by lower_hoist_gather_in_expr.
       Returns NULL on any shape outside that envelope. */
    if (!proc || proc->t != TT_SUB_DECL) return NULL;
    int nparams = (int)proc->v.ival;
    int body_off = nparams + 1;
    int n_stmts = proc->n - body_off;
    if (n_stmts <= 0) return NULL;
    BB_graph_t *cfg = BB_alloc(4096, BB_LANG_RKU);
    if (!cfg) return NULL;
    /* Build the BB_SUSPEND chain. Each stmt becomes a BB_SUSPEND whose α is
       a BB_LIT_I (or BB_LIT_S / BB_VAR for dynamic operands — fall-through
       to bb_suspend.cpp's dynamic-passthrough). Wire stmt_k.γ → next stmt's
       BB_SUSPEND head; stmt_k.ω → terminal BB_FAIL. */
    BB_t *fail_term = BB_node_alloc(cfg, BB_FAIL);
    if (!fail_term) { BB_free(cfg); return NULL; }
    BB_t **stmt_nodes = calloc((size_t)n_stmts, sizeof(BB_t *));
    if (!stmt_nodes) { BB_free(cfg); return NULL; }
    for (int i = 0; i < n_stmts; i++) {
        tree_t *st = proc->c[body_off + i];
        if (!st || st->t != TT_SUSPEND) { free(stmt_nodes); BB_free(cfg); return NULL; }
        BB_t *susp = BB_node_alloc(cfg, BB_SUSPEND);
        if (!susp) { free(stmt_nodes); BB_free(cfg); return NULL; }
        if (st->n >= 1 && st->c[0]) {
            BB_t *val = lower_icn_expr_node(cfg, st->c[0]);  /* handles TT_ILIT/QLIT/VAR */
            if (!val) { free(stmt_nodes); BB_free(cfg); return NULL; }
            susp->α = val;
        }
        stmt_nodes[i] = susp;
    }
    /* γ-chain: stmt[i].γ = stmt[i+1] (or NULL for last so bb_seq's fixup
       resume_addr points at done-trampoline). ω: all stmts → fail_term. */
    for (int i = 0; i < n_stmts; i++) {
        if (i + 1 < n_stmts) stmt_nodes[i]->γ = stmt_nodes[i + 1];
        stmt_nodes[i]->ω = fail_term;
    }
    BB_t *seq = BB_node_alloc(cfg, BB_SEQ);
    if (!seq) { free(stmt_nodes); BB_free(cfg); return NULL; }
    seq->α = stmt_nodes[0];
    seq->ival = n_stmts;
    cfg->entry = seq;
    free(stmt_nodes);
    return cfg;
}
```

Gate it at the call site in lower.c:2083:
```c
BB_graph_t *_irb = NULL;
if (proc->t == TT_SUB_DECL && nm && strncmp(nm, "__gather_", 9) == 0) {
    _irb = lower_raku_proc_body(proc);
} else {
    _irb = lower_icn_proc_body(proc);
}
```

### Step 6.3 — verify rung 9/30

Once `__gather_0` has bb_idx >= 0, `lower_fnc`'s call-site routing fires →
`SM_BB_SWITCH(SM_BBSW_RK_GEN)` lands in the SM → sm_bb_switch.cpp walks the
BB graph → bb_seq.cpp drives the multi-yield → bb_suspend.cpp pushes 10,
20, 30.

Expected gates:
- GATE-RK mode-2: 8/30 → 9/30 (`rk_gather` flips PASS)
- GATE-RK4 mode-4: 8/30 → 9/30
- Smoke raku, icon, prolog, Icon all rungs: HOLD
- FACT RULE grep: 0

If rk_gather still fails:
1. Check `./scrip --dump-sm --interp` shows `SM_BB_SWITCH RK_GEN` at line 11
   instead of `SM_CALL_FN __gather_0`.
2. Check the assembly emission with `./scrip --dump-asm` or equivalent —
   look for `.Lseq<id>_α`, the three `.Lseq<id>_s<k>_α` labels, and the
   `rt_push_int@PLT` calls.
3. Verify the resume_addr indirect-jmp wiring (the trickiest bit).

### Hazards / unknowns

- **lower_iterate's Raku branch (Step 3) wires PUSH_VAR + STORE_VAR around
  the call site.** The dump-sm at HEAD shows lines 10-12 are PUSH_VAR
  __gather_0, CALL_FN __gather_0, STORE_VAR v. When lower_fnc emits
  SM_BB_SWITCH instead of PUSH_VAR + CALL_FN, the `STORE_VAR v` at line 12
  still expects a value on the stack from γ — sm_bb_switch.cpp's γ-arm does
  push (via the inline bb_suspend → rt_push_int) so this should work. But
  verify: in lower_iterate at lower.c:1602, the Raku branch is
  `lower_expr(t->c[0])` which is the gather call → SWITCH; then
  `emit_var_store(t->v.sval)` which is STORE_VAR. The PUSH_VAR at line 10
  is the AST's TT_VAR(__gather_0) child of the TT_FNC — currently the
  default lower_fnc path emits it before SM_CALL_FN. When the routing
  fires, that PUSH_VAR DOESN'T get emitted (the routing returns early), so
  the SM dump should drop that line. Confirm.

- **bb_seq's resume_addr slot is per-emission, not per-BB-node.** A second
  `for gather { }` in the same program creates a SECOND BB_SEQ — but
  `id = bb_node_id(pBB)` is unique per node, so labels collide-safely. ✓

- **bb_suspend.cpp does NOT define `_.lbl_β`.** When bb_seq passes
  `Lβ[k]` as the child's β label, the child only emits `Lβ[k]: jmp ω`.
  Nothing else references `Lβ[k]` — by design, β-flow goes through bb_seq's
  outer β + resume_addr. The unused label-def is harmless.

- **The "main" TT_SUB_DECL still NULL-returns from lower_icn_proc_body.**
  After step 6.2 gates it on `__gather_*` prefix, main keeps its NULL
  return and the SM inline-stmt path drives it (the lower_proc_skeletons
  body-emit at lower.c:2113 reads c[2] for TT_PROC_DECL only — Raku
  TT_SUB_DECL gets bnd=NULL, no inline body emission, leaving the SM
  inline-at-stmt-level shortcut to do its job, per Step 1's note).

### DO NOT, next session

- Do NOT touch SNOBOL4 / Snocone / Rebus / Icon / Prolog BB families.
- Do NOT add fields to BB_t (PEERS RULE / HQ Invariant 17).
- Do NOT add `rt_*` / `raku_*` port-logic helpers (RULES.md).
- Do NOT regenerate `raku.tab.c` from `raku.y` — the makefile has no
  bison rule and the committed .tab.c is the source of truth.
- Do NOT ungate the TT_SUSPEND case in lower_icn_expr_node for Icon
  (would regress rung03_suspend_gen 198→195 per Step 2's note).
- Do NOT remove the bb_seq.cpp `n==0` passthrough guard — Icon/Snocone
  proc bodies also route here after the dispatch peel.

### Recommended order

```
Step 6.1: re-introduce DBG probes               → identify failing tt-kind
Step 6.2: write lower_raku_proc_body            → smoke + Icon all rungs HOLD
Step 6.3: verify rk_gather PASS                 → GATE-RK + GATE-RK4 9/30
```

---

## Session start for next session

```bash
git clone https://TOKEN@github.com/snobol4ever/.github  /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/SCRIP  /home/claude/SCRIP
git clone https://TOKEN@github.com/snobol4ever/corpus   /home/claude/corpus
cat /home/claude/.github/PLAN.md
cat /home/claude/.github/GOAL-RAKU-BB.md
cat /home/claude/.github/HANDOFF-2026-05-27-OPUS-RK-BB-2-STEPS-4-6-PARTIAL.md  # this file
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && make -j4 scrip libscrip_rt
bash scripts/test_raku_ir_rungs.sh     # Expect 8/30
bash scripts/test_raku_mode4_rung.sh   # Expect 8/30
bash scripts/test_smoke_raku.sh        # Expect 5/0
bash scripts/test_smoke_icon.sh        # Expect 5/5
bash scripts/test_smoke_prolog.sh      # Expect 5/5
bash scripts/test_icon_all_rungs.sh    # Expect 198/34/36
```

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7
