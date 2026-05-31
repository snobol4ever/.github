# HANDOFF 2026-05-28 — Opus 4.7 — ICON-BB RESET

**Session author:** Claude Opus 4.7
**Goal:** GOAL-ICON-BB.md (RESET — content wiped and replaced 2026-05-28)
**Outcome:** Two and a half months of mode-2 `SM_BB_INVOKE`-per-statement watermark hunting wiped. Goal file reset to BB-ground-zero rung structure (IBB-0..IBB-34). IBB-0 closed. IBB-1 steps 1–5 of 11 done in code, pushed. Build green; legacy smokes hold.

---

## Final state

| Repo | Hash | What |
|------|------|------|
| SCRIP | `89777f09` | IBB-1 steps 1-5: SM opcode + handler + opname + emit stubs |
| .github | `dec38756` | IBB-0 reset: GOAL-ICON-BB.md replaced; PLAN row collapsed |

## Gates (verified at handoff)

- `smoke_icon` 5/5
- `smoke_prolog` 5/5
- `smoke_unified_broker` 36/17
- FACT RULE: 0 violations outside templates/emit_core
- Legacy `test_icon_all_rungs` was at PASS=194 mode-2 at start of session; not extended (the new shape obsoletes the rung-count watermark).

---

## What happened (honest account)

Lon initiated the session expecting BB work toward the goal in `GOAL-ICON-BB.md`. I (the model) spent two turns defending the existing mode-2 `SM_BB_INVOKE`-per-statement shape as "the design," even though `ARCH-ICON.md`, `ARCH-x86.md`, `GOAL-ICON-BB-NATIVE.md`, and `test_icon.c` had been describing the actual target — flat Byrd-box graphs jumped into via `jmp` with no SM scaffolding around them — since 2026-03-10. The architecture documents were in the session context from the start. I read them, summarized them, and still answered Lon's direct architecture question with the wrong framing twice before he forced me to re-read.

Conversation-history search confirmed: the BB target was specified by Lon on **2026-03-10** with `ByrdBox.zip` and `test_icon.c`. Across at least nine sessions in the two-and-a-half months since, Claude instances have repeatedly accepted "land the mode-2 rung in front of me" framings instead of working toward the documented target. The cumulative effect is two-and-a-half months of polishing the wrong shape — what `GOAL-ICON-BB-NATIVE.md` already called *"one month lost"* in May has become two-and-a-half months lost.

Lon called this out plainly. I agreed. The reset followed.

I also initially carved a new file `GOAL-ICON-GROUND-ZERO.md` instead of replacing the contents of `GOAL-ICON-BB.md`. Lon pointed out that the original file's name (`GOAL-ICON-BB`) already says "BB" — the work that should always have been in it. I deleted the parallel file and replaced the original's contents.

---

## What landed

### IBB-0 — Reset

- Contents of `GOAL-ICON-BB.md` wiped (had been accumulating mode-2 `SM_BB_INVOKE` watermark text through GEN-BUILTIN/BANG-EXPR/LIMIT-EXPR/PARAM-SHADOW/rung36-split etc., all 2026-05-28).
- Replaced with BB-ground-zero rung structure: IBB-0 reset, IBB-1 hello-world two-op boot, IBB-2 boot-shape decision, IBB-3 arithmetic, IBB-4 every+to mode 2, IBB-5 every+to mode 4 (architecture target landing), IBB-6 alt, IBB-7 full `test_icon.c` expression both modes (default-flip after this), IBB-8..IBB-34 remaining Icon constructs.
- Per-rung gate: mode 2 + mode 4 byte-identical output; SM dump shows only `SM_BB_RUN_THE_DAMN_ICON + SM_HALT` for Icon programs; FACT 0; legacy smokes hold.
- Watermark: programs PASS dual-mode, not rungs PASS mode-2.
- `GOAL-ICON-GROUND-ZERO.md` deleted (was the wrong parallel-file approach).
- `PLAN.md` ICON row collapsed to one entry pointing at the reset goal.

### IBB-1 steps 1–5 (SCRIP `89777f09`)

Five mechanical infrastructure pieces for the two-op boot:

1. **SM opcode added.** `src/include/SM.h`: `SM_BB_RUN_THE_DAMN_ICON` inserted between `SM_BB_PL_INVOKE` and `SM_OPCODE_COUNT`. Comment: *"a[1].i = bb_table index of the ROOT program BB graph. The entire Icon program is one connected port-graph rooted here. Mode-2 handler: bb_exec_once(root_graph); halt. Mode 3/4 (later rungs): emit `lea r10, [rip + Δ_root_data]; jmp .Lroot_α`. No SM scaffolding around it. No exit_pc. No every-loop. The graph IS the program."*

2. **Opname table updated.** `src/lower/sm_prog.c`: added `"SM_BB_RUN_THE_DAMN_ICON"` so `--dump-sm` will print it.

3. **Mode-2 handler.** `src/processor/sm_interp.c` (after `SM_BB_PL_INVOKE` handler, before `SM_SUSPEND_VALUE`):
   ```c
   case SM_BB_RUN_THE_DAMN_ICON: {
       int idx = (int)ins->a[1].i;
       BB_graph_t *root = (idx >= 0 && idx < g_stage2.sm.bb_count) ? g_stage2.sm.bb_table[idx] : NULL;
       if (!root) { fprintf(stderr, "[NO-AST] SM_BB_RUN_THE_DAMN_ICON: bb_table[%d] is NULL\n", idx); st->last_ok = 0; break; }
       DESCR_t v = bb_exec_once(root);
       st->last_ok = !IS_FAIL_fn(v);
       break;
   }
   ```

4. **Emit-core stubs.** `src/emitter/emit_core.c`:
   - Main dispatch: `case SM_BB_RUN_THE_DAMN_ICON: /* IBB-1: mode-3/4 stub for now — mode-2-only at this rung. Later rungs emit lea r10... jmp .Lroot_α. */ return 0;`
   - `sm_op_is_dispatched`: added to the BB_INVOKE/BB_PL_INVOKE group.

5. **Build + gates verified.** scrip builds clean; smoke_icon 5/5, smoke_prolog 5/5, smoke_unified_broker 36/17. No regression.

---

## What's NOT DONE — IBB-1 steps 6–11 (for next session)

The hard part of IBB-1. Five concrete steps:

6. **Write `src/lower/lower_icn_bb.c`.** Function `BB_graph_t *lower_icn_bb(CODE_t *prog)`:
   - Walks AST: `STMT_t → TT_PROC_DECL → TT_PROGRAM body`.
   - Calls existing `lower_icn_expr_node(bbg, tree)` on each statement-expression to lower into the graph.
   - Chains top-level statements via γ-edges (first statement's α is `bbg->entry`).
   - Returns the single root `BB_graph_t*` for the whole program.
   - Uses existing `BB_alloc(N, BB_LANG_ICN)` to create the graph.

7. **Write header `src/lower/lower_icn_bb.h`** exporting the function.

8. **Hook in `src/lower/lower.c`** (before existing Icon path at line 133):
   ```c
   if (g_lang == LANG_ICN && getenv("SCRIP_ICN_BB")) {
       BB_graph_t *root = lower_icn_bb(g_current_code);
       int idx = g_stage2.sm.bb_count;
       g_stage2.sm.bb_table[idx] = root;
       g_stage2.sm.bb_count++;
       SM_emit_si(g_p, SM_BB_RUN_THE_DAMN_ICON, NULL, (int64_t)idx);
       SM_emit_0(g_p, SM_HALT);
       return;  // skip the entire legacy lower path
   }
   ```
   The env-gate `SCRIP_ICN_BB=1` is the opt-in so legacy smokes stay green.

9. **Functional gate:** `SCRIP_ICN_BB=1 ./scrip --interp /tmp/hello.icn` (`procedure main() write("hello") end`) prints `hello\n`, exit 0.

10. **SM-shape gate:** `SCRIP_ICN_BB=1 ./scrip --dump-sm /tmp/hello.icn` shows exactly:
    ```
    0  SM_BB_RUN_THE_DAMN_ICON
    1  SM_HALT
    ```

11. **Legacy gate:** unsetting `SCRIP_ICN_BB`, all smokes still pass.

Then commit + push, tick all IBB-1 boxes, IBB-1 closes.

---

## Pointers for next session

- `BB_alloc(N, BB_LANG_ICN)` — `src/processor/bb_pool.c`. Creates a graph. Set `bbg->entry`.
- `lower_icn_expr_node(bbg, tree)` — `src/lower/lower_icn.c:` (search for the function). Lowers an expression node into the graph. **Existing, working.**
- `g_stage2.sm.bb_table[idx]` / `g_stage2.sm.bb_count` — `src/lower/sm_prog.c` (or wherever g_stage2 is defined). Registers the graph for `SM_BB_RUN_THE_DAMN_ICON` to find by index.
- Top-level lower entry: `lower_stmt` in `src/lower/lower.c`. The Icon-specific branch starts at line 133.
- AST shape for hello: `STMT.subject = TT_PROC_DECL(name, params, body)` where `body = TT_PROGRAM(TT_FNC(write, "hello"))`. Verified via `./scrip --dump-ast /tmp/hello.icn`.
- The TT_FNC for `write("hello")` lowers via existing `lower_icn_new_Call` to `BB_CALL`. `bb_exec.c case BB_CALL` already routes to the `write` builtin. So `lower_icn_bb` for IBB-1 is essentially: build a graph, call `lower_icn_expr_node` on the body's TT_FNC, set `bbg->entry`, return.

---

## DO NOT (next session)

- Touch the legacy `lower_icn_new_*` functions. They stay for legacy smokes during transition.
- Touch SNOBOL4 / Snocone / Rebus / Raku / Prolog lower or BB families.
- Reintroduce `SM_BB_INVOKE` per-statement for Icon programs going through `lower_icn_bb`.
- Write `DESCR_t foo(void *zeta, int entry)` C Byrd box functions. See `GOAL-ICON-BB-NATIVE.md` banner.
- Add fields to `BB_t`.
- Walk SM or BB at runtime in modes 3/4.
- Treat this as "another Icon BB step." It is rung 1 of a 34-rung rewrite. Don't get pulled back into the legacy mode-2 watermark.

---

## Session start for next person

```bash
git clone https://TOKEN@github.com/snobol4ever/.github.git /home/claude/.github
# Read PLAN.md → ICON-BB row points here.
# Read RULES.md.
# Read GOAL-ICON-BB.md — current shape is the IBB-* rung ladder (reset 2026-05-28).
# Read ARCH-ICON.md, ARCH-x86.md, GOAL-ICON-BB-NATIVE.md, .github/test_icon.c — the design.
# Read this handoff.
git clone https://TOKEN@github.com/snobol4ever/SCRIP
git clone https://TOKEN@github.com/snobol4ever/corpus
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh                  # expect: clean build
bash scripts/test_smoke_icon.sh              # expect: 5/5
bash scripts/test_smoke_prolog.sh            # expect: 5/5
bash scripts/test_smoke_unified_broker.sh    # expect: ≥35
```

Then pick up at IBB-1 step 6: write `lower_icn_bb.c`.

---

## Closing note

Two-op boot opcode and mode-2 handler are in place. The next session needs to write the lowering function and the hook. The hello-world test is `procedure main() write("hello") end`. Once IBB-1 closes, IBB-3 (arithmetic), IBB-4 (`every (1 to 3)` mode 2), and IBB-5 (`every (1 to 3)` mode 4 — first dual-mode rung, architecture target) follow.

The work is recoverable. Don't relapse.
