# SESSION HANDOFF — 2026-05-27 (Opus 4.7) — RK-BB-2 steps 1-3 landed

**one4all HEAD: `8a046af1`** ✅ all gates HOLD
**.github HEAD: pending — this file + PLAN.md + GOAL-RAKU-BB.md watermark**

---

## What landed this session

Three commits on one4all, each independently gated. Foundation for the
BB_SUSPEND template now in place — the AST→BB lowering and SM scaffold widen
for Raku are done; what remains (steps 4-6) is the actual x86 emission and
the BB_SEQ wiring in `sm_bb_switch.cpp`.

### Step 1 (one4all `2f2aed25`) — `lower_icn_proc_body` accepts TT_SUB_DECL

Widened from TT_PROC_DECL-only to also accept Raku's TT_SUB_DECL. Synthetic
body view via `body_arr` / `body_off` / `n_stmts` — no AST mutation. Icon
reads `body_node->c[i]` (TT_PROGRAM wrapper); Raku reads
`proc->c[nparams+1..n-1]` directly (no wrapper). `cfg->lang` now reflects
proc kind: `TT_PROC_DECL → BB_LANG_ICN`, `TT_SUB_DECL → BB_LANG_RKU`
(RK-BB-1's retag pattern, hoisted up).

Also: `lower_gather_hoist_pass` now registers `__gather_N` procs in
`proc_table` directly. `polyglot_init` runs BEFORE the hoist, so the
synthesized SUB_DECL nodes were never seen by polyglot. Same field-fill
pattern as `polyglot.c:127-137` including the `c[0]` sval fallback for the
TT_SUB_DECL union-clobber workaround.

**What was NOT done (intentional):** the handoff's plan to widen
`lower_proc_skeletons` line 2088 body-emit for TT_SUB_DECL, plus the
line 1739 inline-stmt early-exit, was attempted and reverted. Both broke
smoke raku 5/0 → 0/5 because Raku has no `SM_BB_PUMP_PROC "main"` —
top-level programs rely on the inline-at-stmt-level body emission shortcut
for TT_SUB_DECL. Until `SM_BB_PUMP_PROC` for Raku main is wired (or
hoisted `__gather_N` gains a SM call site through the BB graph), keep
both intact. Body-double-emission isn't an issue because
`lower_proc_skeletons` line 2088 still filters on TT_PROC_DECL — only
Icon's skeleton-path emits a body; Raku's stays an empty `LABEL → RETURN`
stub, and the inline shortcut carries the program.

### Step 2 (one4all `340b804d`) — TT_SUSPEND → BB_SUSPEND (Raku-gated)

Added a `TT_SUSPEND` case to `lower_icn_expr_node`. Builds a `BB_SUSPEND`
node with the yielded-value subgraph as α (operand). γ/ω stamped by the
threaded wrapper via `icn_leaf` (bounded=1 in stmt context forces β=ω_in).

**GATED on `cfg->lang == BB_LANG_RKU`.** Icon `suspend` must keep the
legacy SM path (`lower_suspend` → `SM_SUSPEND`) because mode-2 `bb_exec.c`
has no `BB_SUSPEND` executor yet — without the gate,
`rung03_suspend_gen{,_compose,_filter}` regress 198 → 195. Ungating for
Icon belongs to GOAL-ICON-BB.

### Step 3 (one4all `8a046af1`) — lower_every / lower_iterate accept LANG_RAKU

- `lower_every` gate widened ICN → ICN+RAKU. SM_BB_SWITCH scaffold is
  generator-agnostic — Icon BB_TO_BY, Raku `__gather_N` proc body, etc. all
  hand a yield value on γ.

- **Critical bug fix in `lower_every`:** the `a[0].i = exit_pc` stamp is now
  guarded on `have_switch` — the actual presence of a `SM_BB_SWITCH` in the
  emitted gen_expr stream. Without this guard, when gen_expr lowers to a
  flat shape (Raku's TT_ITERATE → `SM_PUSH_VAR` + `SM_CALL_FN` for
  `__gather_N`), the fallback `switch_pc = gen_start` clobbered the
  `SM_PUSH_VAR`'s `a[0]` (a `char *`), segfaulting `sm_seq_print` and the
  interpreter. For Icon the guard is a no-op (its BB_TO_BY scaffold always
  emits a SWITCH).

- `lower_iterate` Raku branch: emit `gen_expr` then `STORE_VAR` into the
  loop var named in `t->v.sval` (Raku parser stores the iter var name on
  TT_ITERATE's sval — see `raku.y:304`). Body re-runs on β-resume of the
  wrapping SM_BB_SWITCH.

### Effect on rk_gather

- Before this session: `TT_EVERY unhandled` warning + only "done" printed.
- After step 3 alone: same "done" — no crash, but no yields either. The
  flat fallback runs the body zero times because there's no SM_BB_SWITCH
  driving it, and `__gather_N`'s skeleton is still a `LABEL → RETURN` stub.
- Steps 4-6 will close the loop: bb_suspend emission + BB_SEQ-rooted graph
  dispatch in `sm_bb_switch.cpp` → proper pump that yields 10/20/30.

### Gates (end of session, vs 50370f5a baseline)

```
GATE-RK   mode-2:           8/30   HOLD
GATE-RK4  mode-4:           8/30   HOLD
Smoke raku:                 5/0    HOLD
Smoke icon:                 5/5    HOLD
Smoke prolog:               5/5    HOLD
Icon all rungs:             198/34/36 HOLD
FACT RULE grep:             0
```

No counter movement — steps 1-3 are foundation. The 9/30 acceptance target
requires steps 4-6.

---

## NEXT SESSION — RK-BB-2 steps 4-6

**Fresh context required (~80%+).** The mechanical bits are done. What
remains is x86 emission (a new BB template) plus a BB_SEQ-rooted-graph
dispatch case in `sm_bb_switch.cpp`.

### Step 4 — `src/emitter/BB_templates/bb_suspend.cpp`

Four-port pull protocol for proc-body suspends. Use `bb_upto.cpp` lines
12-71 as the structural reference (TEXT mode with `.data` state slot,
MEDIUM_TEXT and MEDIUM_BINARY arms).

- **α (fresh):** evaluate expr operand via PEERS RULE
  (`bb_operand_aux_get` — set up by the threaded wrapper when nd->α is
  the operand subgraph), push DESCR_t result via `rt_push_*`, jmp γ.
- **β (resume):** advance to next stmt. In a BB_SEQ body the SEQ's port-
  follower handles this — successive yields come from re-entering the
  SEQ, which finds the next BB_SUSPEND by following the γ-chain. So
  β = ω_in for the suspend node itself.
- **γ:** consumer takes value, will re-enter via β.
- **ω:** unreachable in body context (BB_SEQ ω-edge carries exhaustion).
  Stub as `jmp lbl_γ` or fall-through.

State slot in `pBB->counter` (emitter-process address, valid for native
codegen — see `bb_upto.cpp:83`).

### Step 5 — wire `emit_core.c:532` from `bb_stub` to `bb_suspend`

Add `extern void bb_suspend(BB_t *);` to `bb_templates.h`, change the
case-fallthrough at line 532. Currently `BB_SUSPEND` shares the bb_stub
arm with `BB_PROC`, `BB_SCAN`, etc. — peel `BB_SUSPEND` off and route
to `bb_suspend(nd); return 0;`.

### Step 6 — `sm_bb_switch.cpp` handles BB_SEQ-rooted graphs

A Raku proc body lowers to `cfg->entry = BB_SEQ` (the seq node holding
the stmts). Current `sm_bb_switch.cpp` calls `walk_bb_node_str_c(gen)`
which for BB_SEQ routes to `bb_stub` (`emit_core.c:517`). Two options
per the handoff:

- **(a) (cleaner, more files):** write `bb_seq.cpp` that walks the
  γ-chain emitting each child inline.
- **(b) (faster, contained):** extend sm_bb_switch.cpp to detect
  BB_SEQ-rooted graphs and walk the chain explicitly.

Lon directive: 100% template emission via BB/SM/XA only — that favors
**(a)** (`bb_seq.cpp`).

### Acceptance for the rung

- GATE-RK mode-2: 8/30 → 9/30 (rk_gather)
- GATE-RK4 mode-4: 8/30 → 9/30 (rk_gather under `--compile`)
- All other gates HOLD
- FACT RULE grep == 0

### Hazards / unknowns

- **No `SM_BB_PUMP_PROC "main"` for Raku.** The current path is: top-level
  `sub main()` stmt inlines its body at program-stmt-position via the line
  1739 shortcut. Once the gather is supposed to run through a BB pump
  (step 4-5-6), the call to `__gather_0()` needs to dispatch through
  `icn_bb_pump_proc_by_name`. Verify in dump-sm that the call site
  emerging from `lower_iterate` is wired so `is_generator=1` routes via
  pump.

- **`is_generator` detection still works.** `lower_proc_skeletons`
  line 2080's AST walk for TT_SUSPEND fires on the `__gather_N` body and
  sets `is_generator=1` regardless of whether `lower_icn_proc_body`
  produced a BB graph. Step 2's BB_SUSPEND inside the lowered graph also
  triggers the line 2069 path. Either works.

- **The unused `body` variable in `lower_every` warning.** Step 3's debug
  variable `_lang` and the inner `body` flow are fine; the build is clean.

### DO NOT, next session

- Do NOT touch SNOBOL4 / Snocone / Rebus / Icon / Prolog BB families.
- Do NOT add fields to BB_t (PEERS RULE / HQ Invariant 17).
- Do NOT add `rt_*` / `raku_*` port-logic helpers (RULES.md).
- Do NOT regenerate `raku.tab.c` from `raku.y` — the makefile has no
  bison rule and the committed .tab.c is the source of truth.

### Recommended order

```
Step 4 (bb_suspend.cpp)                    → smoke + GATE-RK still HOLD
Step 5 (emit_core.c wire)                  → verify text-mode x86 dump
Step 6 (bb_seq.cpp + sm_bb_switch)         → verify rk_gather 9/30
```

---

## Session start for next session

```bash
git clone https://TOKEN@github.com/snobol4ever/.github  /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/one4all  /home/claude/one4all
git clone https://TOKEN@github.com/snobol4ever/corpus   /home/claude/corpus
cat /home/claude/.github/PLAN.md
cat /home/claude/.github/GOAL-RAKU-BB.md
cat /home/claude/.github/HANDOFF-2026-05-27-OPUS-RK-BB-2-STEPS-1-3.md  # this file
bash /home/claude/one4all/scripts/install_system_packages.sh
cd /home/claude/one4all && make -j4 scrip libscrip_rt
bash scripts/test_raku_ir_rungs.sh     # Expect 8/30
bash scripts/test_raku_mode4_rung.sh   # Expect 8/30
bash scripts/test_smoke_raku.sh        # Expect 5/0
bash scripts/test_smoke_icon.sh        # Expect 5/5
bash scripts/test_smoke_prolog.sh      # Expect 5/5
bash scripts/test_icon_all_rungs.sh    # Expect 198/34/36
```

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7
