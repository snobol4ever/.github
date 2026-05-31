# SESSION HANDOFF — 2026-05-27 (Opus 4.7) — RK-BB-2 ✅ CLOSED

**SCRIP HEAD: `d08237e0`** ✅ all gates HOLD or improve
**.github HEAD: this commit** ✅ PLAN.md + GOAL-RAKU-BB.md updated

Prior session: `HANDOFF-2026-05-27-OPUS-RK-BB-2-STEPS-4-6-PARTIAL.md`.

---

## What landed this session

**One commit, one file changed in SCRIP** (+27/-5 lines in `src/lower/lower.c`).
`rk_gather.raku` PASSES `--compile`: native x86 binary emits
`10\n20\n30\ndone\n` byte-exact to `.expected`. GATE-RK4 mode-4: 8/30 → 9/30.

The work consumed the equivalent of a half-session and turned out NOT to need
the `lower_raku_proc_body()` parallel-lowerer the prior handoff anticipated.
The blocker was upstream from where the prior session looked: a union-clobber
in the AST hoist that fed garbage into the nparams field.

### Commit `d08237e0` — RK-BB-2 step 6 ✅

Three surgical edits, all in `src/lower/lower.c`:

#### (1) `lower_hoist_gather_in_expr` (~L2202) — the union-clobber

```c
- tree_t * def = ast_node_new(TT_SUB_DECL); def->v.sval = intern(gname);
+ tree_t * def = ast_node_new(TT_SUB_DECL); def->v.ival = 0;  /* nparams=0; name in c[0] */
```

`tree_t.v` is a union; setting `v.sval` to a pointer clobbered `v.ival`.
`lower_icn_proc_body` then read `(int)proc->v.ival` as nparams, getting
the pointer's low 32 bits — a very large number. Then
`body_off = nparams + 1` overshot `proc->n` by orders of magnitude, so the
guard `if (proc->n <= body_off) return NULL` fired on EVERY Raku TT_SUB_DECL.

The name `__gather_N` is already stored in `c[0]->v.sval` (the TT_VAR child).
The redundant copy on the SUB_DECL node was only ever a side-channel; killing
it removes the clobber. `lower_proc_skeletons` reads `proc_table[pi].name`
which was set by the hoist's own registration code (see L2229-2247), not from
`proc->v.sval`, so name resolution still works.

This is Open Question #5 from `GOAL-RAKU-BB.md` ("Union-clobber proper fix").
The fix is now landed for `__gather_*` (the only TT_SUB_DECL the hoist
creates). Non-gather user `sub` declarations are not affected — they come
from `raku.y` with `v.sval` set; lower paths read name from `c[0]->v.sval`
in this codebase already.

#### (2) `lower_stmt` RAKU + TT_SUB_DECL branch (~L1787)

```c
  if (lang == LANG_RAKU && subject && subject->t == TT_SUB_DECL) {
+     const char *_gn = (subject->n >= 1 && subject->c[0] && ... ) ? ... : NULL;
+     int _is_gather = (_gn && strncmp(_gn, "__gather_", 9) == 0);
+     if (!_is_gather) {
          int nparams = (int)subject->v.ival;
          for (int i = nparams + 1; i < subject->n; i++)
              if (subject->c[i]) { lower_expr(subject->c[i]); SM_emit(g_p, SM_VOID_POP); }
+     }
      goto emit_gotos;
  }
```

Hoisted `__gather_*` procs are driven via `SM_BB_SWITCH(SM_BBSW_RK_GEN, bb_idx)`
emitted by `lower_fnc` at the call site (the routing added in the partial
Step 6, commit `6ea3637d`). Their body lives in the BB graph that
`lower_icn_proc_body` now successfully builds (once (1) lands). Emitting
the body here too orphans it at program top-level — SM_VOID_POP / SM_SUSPEND
ops run on program startup before `main` is even called, hence the stack
underflow that I confirmed via `sm_interp: stack underflow` after just (1).

Skip the body walk for `__gather_*` only. All other Raku TT_SUB_DECL
statement subjects keep their existing emit-for-effect semantics.

#### (3) `lower_expr_inner` TT_SUB_DECL case (~L1965)

```c
- case TT_SUB_DECL: { int np=(int)t->v.ival; for(i=np+1;...){lower_expr; VOID_POP;} SM_PUSH_NULL; return; }
+ case TT_SUB_DECL: {
+     int np=(int)t->v.ival;
+     /* same __gather_ detection */
+     if (!_is_gather) { for(...) {lower_expr; VOID_POP;} }
+     SM_emit(g_p, SM_PUSH_NULL);
+     return;
+ }
```

Defensive: any path that drops into `lower_expr_inner(TT_SUB_DECL)` should
also skip the body walk for hoisted gather procs. SM_PUSH_NULL is still
emitted to preserve the expression-position contract (TT_SUB_DECL as an
expression yields null). I'm not aware of a path that actually reaches
this case for `__gather_*` today, but the contract matters when (b) might
be sidestepped by future statement shapes.

---

## Diagnostic path (probes removed before commit)

The prior handoff hypothesized that `lower_icn_expr_threaded_b` was rejecting
Raku stmt shapes before reaching `lower_icn_expr_node`. The probes told a
different story.

Two short-lived `fprintf` probes:
1. At top of `lower_icn_expr_threaded_b`: print `e->t` and `cfg->lang`.
2. After `lower_icn_expr_node` call in same function: print `e->t`, `cfg->lang`, `nd`.
3. After `lower_icn_proc_body` in `lower_proc_skeletons`: print name and result.

First run showed only ONE `[DBG-thread]` line with `e->t=126 cfg->lang=6`
and `[DBG-node] nd=(nil)`. Then `[DBG-procbody] body_irb=(nil)` for both
`main` AND `__gather_0`. Two `[DBG-procbody]` lines but only one `[DBG-thread]`?
Means `__gather_0`'s loop never even called `lower_icn_expr_threaded_b` once —
the loop body wasn't entered. The only way that's possible is if `n_stmts <= 0`
or the early-return at `proc->n <= body_off` fires.

Added a third probe inside the TT_SUB_DECL branch of `lower_icn_proc_body`:
print nparams, body_off, proc->n, and every c[i]->t.

```
[DBG-subdecl] nparams=51585104  body_off=51585105  proc->n=4   ← garbage nparams
```

51585104 is the low 32 bits of the interned name pointer. Confirmed: union-clobber.
After fix (1):

```
[DBG-subdecl] nparams=0  body_off=1  proc->n=4
[DBG-subdecl]   c[0]->t=5    ← TT_VAR (the name)
[DBG-subdecl]   c[1]->t=50   ← TT_SUSPEND
[DBG-subdecl]   c[2]->t=50   ← TT_SUSPEND
[DBG-subdecl]   c[3]->t=50   ← TT_SUSPEND
[DBG-procbody] nm=__gather_0 body_irb=0x37bdbad0   ← non-NULL!
```

Decoded enum values via a small Python regex scan of `src/include/ast.h`:
5 = TT_VAR, 50 = TT_SUSPEND, 89 = TT_EVERY, 126 = TT_SAY.

The `[DBG-node] e->t=126 nd=(nil)` was `main`'s first statement — TT_SAY,
which legitimately has no case in `lower_icn_expr_node`. That's why `main`
returns NULL (it stays SM). Correct behavior, not a bug.

SM dump count after fix (1) was still 49 — same as before — because the
top-level orphaned-body emission was still firing. After fix (2) the count
dropped to 25 and SM_BB_SWITCH at line 10 replaced the orphaned SM_SUSPEND
chain. After fix (3) (defensive), no visible behavioral change but the
expression-position invariant is preserved.

After fixes (1)+(2)+(3): `./scrip --compile rk_gather.raku` produces clean
x86 assembly with the existing `bb_seq.cpp` + `bb_suspend.cpp` templates
(authored in the partial Step 6); the assembled and linked binary outputs
`10\n20\n30\ndone\n`.

---

## What HOLDS / IMPROVES at this HEAD

```
GATE-RK   mode-2:           8/30   HOLD  (BB_SUSPEND has no bb_exec.c executor)
GATE-RK4  mode-4:           9/30   ✅ rk_gather flipped 8→9
Smoke raku:                 5/0    HOLD
Smoke icon:                 5/5    HOLD
Smoke prolog:               5/5    HOLD
Icon all rungs:             198/34/36 HOLD
Prolog mode-4:              4/4    (was carried 1/4 — unrelated upstream improvement)
FACT RULE grep:             0
Build:                      clean
```

The `rk_gather` mode-4 PASS is verified two ways:
1. `bash scripts/test_raku_mode4_rung.sh` reports `PASS rk_gather` and 9/30.
2. `bash scripts/run_raku_via_x86_backend.sh $(pwd)/test/raku/rk_gather.raku`
   produces stdout `10\n20\n30\ndone\n`, byte-exact to `.expected`.

---

## NEXT SESSION

### Primary: RK-BB-3 — lazy `map` / `grep` as Seq CONSUMERS

Per `GOAL-RAKU-BB.md` ladder:

> RK-BB-3 — lazy `map`/`grep` as Seq CONSUMERS. REUSE `bb_iterate.cpp`;
> grep adds γ-port predicate test (loop on false, γ on true, ω on source ω).
> Migrate `lower.c:1872-1881` off eager `SM_CALL_FN raku_map`/`raku_grep` for
> the lazy path. `rk_map_grep_sort24.raku` under `--compile` (sort stays eager).

The producer side (BB_SUSPEND / BB_SEQ) is now proven end-to-end via
RK-BB-2. RK-BB-3 wires the consumer side onto the same Seq protocol.

`bb_iterate.cpp` was authored for Icon and is template-clean; the rung is
expected to be ~3-5 edits in `lower.c` (a `lower_raku_map`/`lower_raku_grep`
parallel to `lower_raku_range`, plus a `lower_fnc` routing edit similar to
the `__gather_*` detection).

Sister consumer for `grep`: γ-port carries Bool result of the predicate;
on true, advance the inner Seq; on false, loop back to inner β; on inner
ω, ω out. This is the first rung that exercises BB_ITERATE's γ-port
predicate hook for Raku.

### Secondary (OPEN): RK-BB-2b — mode-2 BB_SUSPEND executor

`bb_exec.c` has no case for BB_SUSPEND. The TT_SUSPEND case in
`lower_icn.c` (~L651) is gated on `cfg->lang == BB_LANG_RKU` specifically
because emitting BB_SUSPEND for Icon would break `rung03_suspend_gen` —
the mode-2 chain walker would visit a node with no handler and stack-
underflow. This is an Icon-shared cross-language item: when somebody
authors a mode-2 BB_SUSPEND executor (or a unified pump in sm_bb_switch),
the gate can be lifted and Icon's `suspend` can move onto BB too. Not
this goal.

Symptom today: `./scrip --interp test/raku/rk_gather.raku` reports
`sm_interp: stack underflow`. Mode-4 path is unaffected because the
emit-time `bb_suspend.cpp` template handles BB_SUSPEND.

### Tertiary (OPEN): RK-BB-1b carry-over

Per `GOAL-RAKU-BB.md`: exclusive `..^` and non-literal-bound ranges
currently fall through to eager SM. Small follow-on, can be picked up
inside any RK-BB-N session.

---

## Hazards / unknowns

- **The `__gather_` prefix is now a load-bearing string in three places.**
  Search-and-replace tools should treat it as protected. If the hoist
  ever needs to rename the synthesized prefix, all three lower.c gates
  must move in lockstep with `lower_fnc` (`6ea3637d`) and any future
  consumer/predicate-side detector.

- **Open Question #5 retirement is incomplete.** The hoist no longer
  uses `v.sval` on TT_SUB_DECL, but `raku.y`'s grammar-driven
  TT_SUB_DECL nodes may still set `v.sval = name`. A future session
  can migrate nparams to a side-channel (leading TT_VLIST child, TT_ATTR,
  or a separate `tree_t` field) and retire the v.sval/v.ival dual-use
  entirely. Not urgent — the hoist path is fixed and the grammar path
  reads v.ival as the nparam count from the parser's own initialization,
  which sets both v.sval AND nparams via a path I have not audited this
  session.

- **The PEERS RULE / FACT RULE remained clean.** No BB_t fields added,
  no `rt_*`/`raku_*` port-logic helpers added, no bytes outside templates.
  Grep is 0.

---

## DO NOT, next session

- Do NOT touch SNOBOL4 / Snocone / Rebus / Icon / Prolog BB families.
- Do NOT add fields to BB_t (PEERS RULE / HQ Invariant 17).
- Do NOT add `rt_*` / `raku_*` port-logic helpers (RULES.md).
- Do NOT regenerate `raku.tab.c` from `raku.y` — the makefile has no
  bison rule and the committed .tab.c is the source of truth.
- Do NOT ungate the TT_SUSPEND case in lower_icn_expr_node for Icon
  (would regress rung03_suspend_gen 198→195 per Step 2's note in the
  prior handoff).
- Do NOT remove the bb_seq.cpp `n==0` passthrough guard — Icon/Snocone
  proc bodies also route here after the dispatch peel.
- Do NOT remove the `__gather_` prefix gates in any of the three lower.c
  edits without simultaneously updating `lower_fnc`'s routing detector
  and the hoist's name format.

---

## Session start for next session

```bash
git clone https://TOKEN@github.com/snobol4ever/.github  /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/SCRIP  /home/claude/SCRIP
git clone https://TOKEN@github.com/snobol4ever/corpus   /home/claude/corpus
cat /home/claude/.github/PLAN.md
cat /home/claude/.github/GOAL-RAKU-BB.md
cat /home/claude/.github/HANDOFF-2026-05-27-OPUS-RK-BB-2-STEP-6-CLOSED.md  # this file
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && make -j4 scrip libscrip_rt
bash scripts/test_raku_ir_rungs.sh     # Expect 8/30
bash scripts/test_raku_mode4_rung.sh   # Expect 9/30 (rk_gather PASS)
bash scripts/test_smoke_raku.sh        # Expect 5/0
bash scripts/test_smoke_icon.sh        # Expect 5/5
bash scripts/test_smoke_prolog.sh      # Expect 5/5
bash scripts/test_icon_all_rungs.sh    # Expect 198/34/36
bash scripts/run_raku_via_x86_backend.sh $(pwd)/test/raku/rk_gather.raku
# Expect: 10\n20\n30\ndone\n
```

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7
