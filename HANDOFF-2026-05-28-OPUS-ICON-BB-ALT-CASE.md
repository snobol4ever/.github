# HANDOFF 2026-05-28 — Opus 4.7 — ICON-BB ALT-EXPR + CASE-EXPR

**Session author:** Claude Opus 4.7
**Goal:** GOAL-ICON-BB.md
**Outcome:** rungs **161 → 170** (+9) across four steps, smokes green throughout, FACT 0, zero regressions.

---

## Final state

| Repo | Hash | What |
|------|------|------|
| one4all | `d1031b0c` | CASE-EXPR (tip) |
| .github | `f78c0071` | session goal/plan updates (tip) |

## Gates

- `smoke_icon` 5/5
- `smoke_prolog` 5/5
- `smoke_unified_broker` 35/18 (broker 35 — pre-existing 18 FAILs unchanged)
- `test_icon_all_rungs` PASS=**170** FAIL=63 XFAIL=36 TOTAL=269
- FACT RULE: 0 violations outside templates and emit_core

---

## Steps landed this session

### 1. MAIN-BOOT — `80d0d5ee`
Recovered Icon from 0/5 smoke after `08e05f68` whacked `SM_BB_PUMP_PROC`.
Four coordinated fixes:
1. Main bootstrap as ordinary `SM_CALL_FN "main" nargs=0` + `SM_VOID_POP` at lower epilogue.
2. Every-loop `exit_pc` moved from `SM_BB_INVOKE.a[0]` → `a[2]` (a[0] is the α/β state flag — silent slot collision masked for years by PUMP_PROC bypass). Matching FAIL-jump added in interp + template.
3. `lower_return` Icon arm aligned with Raku (no VOID_POP — retval reaches `sm_eval_subexpr`'s nested-stack read).
4. `every E` with no `SM_BB_INVOKE` in `gen_expr` AND no body lowers as one-shot (was infinite-looping on non-gen E like `every write(sum_to(5))`; previously masked by `icn_bb_pump_proc_by_name`'s `icn_bb_oneshot` wrapper).

**Result:** smoke_icon 0/5 → 5/5, rungs 1 → 161.

### 2. ALT-EXPR — `8b0ad2ba`
`lower.c case TT_ALTERNATE` (lines 2354–2358 pre-rename) was half-finished: built a `BB_graph_t *` via `lower_icn_expr_top()` then **immediately freed it and called `lower_unhandled()`** (which emits `SM_PUSH_NULL`). So every `1|2|3`-style alternation reaching `lower_expr` (call-arg, `:=` RHS, bare stmt) collapsed to a single null push.

**Fix** matches the `lower_to` / `lower_to_by` shape already in the file: build CFG, `SM_seq_bb_add()`, emit `SM_BB_INVOKE`. The runtime side (`BB_ALT` mode-2 exec at `bb_exec.c:1702`, `SM_BB_INVOKE` dispatch at `sm_interp.c:677`) was already complete. Pure lowering hookup, 8 lines added, 2 deleted.

**Recovered (+4):** `rung08_strbuiltins_match`, `rung13_alt_alt_int`, `rung13_alt_alt_every_write`, `rung32_strretval_strret_every`.

### 3. RENAME — `b84153c3`
Pure rename in `src/lower/` only:
- `BB_graph_t *cfg` → `BB_graph_t *bbg` (~735 sites)
- `BB_t *nd` → `BB_t *bb` (~2030 sites)

Strict word-boundary `sed`. Did NOT touch: `cfg_alt`, `_cfg`, `_bcfg`, `gcfg`, `g_current_cfg`, `bb_idx`, `BB_t`, `BB_graph_t`, `bb_exec_*`, `BB_node_alloc`, `bb_pl_*`, `pat_bb`, `arm`, `choice_nd`, etc. — all are different identifiers.

**One collision fixed:** `Pl_PredEntry_BB *bb` at `bb_exec.c:3196` lived inside a function whose outer `BB_t *nd` parameter renamed to `bb`; the inner shadow caused `bb->value`/`bb->ω`/`bb->state` to resolve to the wrong type. Renamed Prolog-entry local to `*pe` (Predicate Entry). Twin at `lower.c:2550` had no surrounding `BB_t *nd`, no change needed.

**10 files changed, 2603 insertions, 2603 deletions** — perfect symmetry confirming pure rename. Gates identical to pre-rename (rungs **165**, smokes unchanged).

### 4. CASE-EXPR — `d1031b0c`
Icon `TT_CASE` was misrouted through Snocone-shaped branches in `lower_case` (two bugs):

1. **Misclassification.** Icon's trailing default body `default: "other"` is a `TT_QLIT` literal. The legacy-Snocone branch at `lower.c:1315` was gated on `g_lang != LANG_RAKU` plus the QLIT-trailing test — which Icon trees with QLIT defaults matched. That branch *interprets* the trailing QLIT as an end-label name and silently drops it.
2. **Expression-vs-statement.** The "modern Snocone" branch at line 1361 also caught Icon and emitted `lower_expr(body); SM_VOID_POP` per arm followed by an unconditional final `SM_PUSH_NULL` — fine for case-as-statement, destroys the value when used as `write(case x of {...})` or `x := case ...`.

**Fix** is two-character: change both branch gates from `g_lang != LANG_RAKU` to `g_lang == LANG_SNO`. Icon then falls through to the existing `!is_raku` branch at `lower.c:1419`, which already handles `has_def = (t->n - 1) % 2` and preserves arm values (`lower_expr(body)` with no trailing VOID_POP). The expression-correct lowering was already there — Icon just wasn't reaching it.

**Recovered (+5):** all five rung33 case rungs — `case_int`, `case_str`, `case_arith`, `case_no_default`, `case_in_proc`.

Pre-existing Snocone `semantic` test failures (3) confirmed unrelated via stash-and-test.

---

## NOT-DONE — work for future sessions

**Clusters still failing (63 rungs):**

1. **rung13 cartesian-product** (4 rungs: `alt_alt_nested`, `alt_alt_cross_arg`, `alt_alt_cross_arg_sideeffect`, `alt_alt_augconcat`). The post-ALT-EXPR remainder. `every write((a|b) || (x|y))` needs cartesian product over multiple generators in one expression — the ICN-Z zipper / BB-port-graph mode-4 path. Goal file already calls this out: *"Filter/binop-generator cases need the BB-port-graph mode-4 path."* The flat SM scaffold cannot interleave operand re-evaluation with mid-sequence β-resume.

2. **`every <var> ||:= <gen>`** (rung13_alt_alt_augconcat surface). Pre-existing stack underflow — verified independent of ALT-EXPR by reproducing with `every s ||:= (1 to 3)`. Augmented-assign bookkeeping doesn't survive the generator's β-resume back-edge.

3. **Generator-proc semantics on `SM_CALL_FN` path** (~30 rungs: rung03 suspend_gen family, rung22 list_bang, rung23 table_key, rung30 misc_seq, rung31 sort, etc.). `sm_eval_subexpr` is a one-shot run with no `g_current_generator_state`, so `SM_SUSPEND` inside a user proc silently fails. Needs GeneratorState wiring on the SM call side (or a distinct route for generator procs). Pre-MAIN-BOOT watermark `64ca51b7` had 199 rungs — 38 of those gen-proc rungs depended on `icn_bb_pump_proc_by_name`'s GeneratorState path, which PUMP_PROC has removed.

4. **rung36 jcon** (~26 rungs). jcon reference programs — generally larger, exercise more semantics. Most are blocked by category-3 (gen-proc) or specific builtins (`upto`, `sort`, etc.). Lower priority.

5. **Smaller singletons** (rung10 augop_break_repeat, rung11 bang_augconcat, rung15 iterate_string, rung16 subscript_sub_every, rung35 block_body_every_gen_block) — each could be individually investigable; may surface novel bugs or land in one of the four clusters above.

**Watermark recovery target:** pre-MAIN-BOOT was 199. Current is 170. The 29-rung gap is the gen-proc path (category 3) plus the rung13 zipper deferral.

---

## Acceptance greps (per GOAL-ICON-BB.md)

```bash
grep -nE 'bb_operand_aux_set' src/lower/lower_icn.c | wc -l   # == 0 ✅
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/ | grep -v _templates/ | grep -v emit_core | wc -l   # == 0 ✅
```

Note the FACT-grep extensions in PLAN's gate list — confirmed clean.

---

## Session start for next person

```bash
git clone https://TOKEN@github.com/snobol4ever/.github.git /home/claude/.github
# read PLAN.md, find ICON-BB row, then read GOAL-ICON-BB.md
# read RULES.md
git clone https://TOKEN@github.com/snobol4ever/one4all /home/claude/one4all
git clone https://TOKEN@github.com/snobol4ever/corpus /home/claude/corpus
cd /home/claude/one4all
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
bash scripts/test_smoke_icon.sh              # expect 5/5
bash scripts/test_smoke_prolog.sh            # expect 5/5
bash scripts/test_smoke_unified_broker.sh    # expect ≥35
bash scripts/test_icon_all_rungs.sh          # expect 170/269
```

Then pick a NOT-DONE cluster. My recommendation: **gen-proc GeneratorState wiring** has the most leverage (~30 rungs gated on it). If a smaller win is preferred, look at rung15/rung16/rung35 singletons.
