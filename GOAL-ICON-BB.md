# GOAL-ICON-BB.md — All Icon Byrd-Box constructs, modes 1/2/3/4

**Repo:** one4all + .github
**Mode priority:** Mode 2 (`--interp`) first, then Mode 3 (`--run`). Mode 4 deferred.

---

## Model

No operands on BB nodes. CFG of boxes wired by **four ports**. Operand values flow through `BB_graph_t.ring`.

| Port | Direction | Meaning |
|------|-----------|---------|
| α | UP (synthesized) | fresh-entry |
| β | UP (synthesized) | retry-entry (self for resumable, else ω_in) |
| γ | DOWN (inherited) | success continuation |
| ω | DOWN (inherited) | failure continuation |

**BB_t has ONLY:** `t`, `α β γ ω`, `sval/ival/dval`, `value/counter/state`. PEERS sidecar `operand_aux` LEGACY for Icon (kept for Prolog/SNOBOL4).

**Lowering signature:** `lower(cfg, tree, γ_in, ω_in, &α_out, &β_out, bounded)`. Each `lower_icn_new_<KIND>_ag` produces AG-pure output directly.

**FACT RULE:** all emitted x86 via templates only. `grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/ | grep -v _templates/ | grep -v emit_core | wc -l` == 0.

---

## ✅ DONE

- **LFJ-0..15b** (`1dfe9631`/`6a631124`): all `ir_a_*` from `irgen.icn` transcribed to `lower_icn_new_<KIND>`; legacy lower deleted; six `_threaded_b` AG-pure intercepts folded into `_ag` variants. Reference: `corpus/programs/icon/jcon-ref/irgen.icn`.
- **Steps 1–9** (ring fields, chain walker, BINOP, SEQ+FAIL, IF, CONJ, ALT, EVERY flat-wire `ival=1`, TO/TO_BY, LCONCAT/SECTION/IDX/IDX_SET).
- **Step 10a-1..10** — all `_ag` lowerers thread sub-expressions via `lower_icn_expr_threaded_b`.
- **Step 10a-4 (Every_ag)** — streaming gens flat-wire via `ival=2`+`lic_is_gen_node` (`09353f25`/`5d5bf85d`); block bodies via BODY-MEDIATED `ival=3` w/ phase machine honoring break/next/return (`cba1dc4d`/`aa3e403f`); gen-bearing single-node body corner fixed (`64ca51b7`). **Exclusions stay on legacy (correct, not bugs):** static-bound TO bodies, suspending generator bodies.
- **Step 10b — sidecar deletion + ring-peek** (`d209c93e`/`9fb1dbb8`/`b55bc261`/`ffd55d4f`/`8f887fa1`/`359c5754`/`4485d647`): BB_ASSIGN reads rhs via `ag_ring_peek(0)`; BB_CALL deep-args via `ag_ring_peek(nargs-1-j)` w/ `nd->dval=1.0` deep marker; `icn_kind_owns_omega_operand` removed.
- **MAIN-BOOT** (this session, Opus 4.7, 2026-05-28): restored Icon top-level execution after `08e05f68` whacked `SM_BB_PUMP_PROC`. Two coordinated fixes: (a) lower epilogue emits `SM_CALL_FN "main" nargs=0; SM_VOID_POP` (per `08e05f68` handoff guidance); (b) every-loop `exit_pc` moved from `BB_INVOKE.a[0]` → `a[2]` because `a[0]` was the α/β state flag and collided silently; mode-2 interp now honors `a[2].i` exit-jump on FAIL. Sites: 4 lower stamps + `sm_bb_switch.cpp` template + interp handler.
- **ALT-EXPR** (Opus 4.7, 2026-05-28, `8b0ad2ba`): `lower.c case TT_ALTERNATE` was half-finished — built CFG via `lower_icn_expr_top` then immediately freed it and called `lower_unhandled` (`SM_PUSH_NULL`). So `1|2|3` reaching `lower_expr` (call-arg, `:=` RHS, bare stmt) collapsed to a single null. Fixed by matching `lower_to` shape: build CFG, `SM_seq_bb_add`, emit `SM_BB_INVOKE`. `BB_ALT` mode-2 exec already handled the first-success-arm semantics and β-resume; the surrounding `lower_every` scans for `SM_BB_INVOKE` to wire its loop. Recovered 4 rungs: `rung08_strbuiltins_match`, `rung13_alt_alt_int`, `rung13_alt_alt_every_write`, `rung32_strretval_strret_every`. Watermark 161 → **165**, zero regressions.
- **RENAME** (Opus 4.7, 2026-05-28, `b84153c3`): `src/lower/` only — `BB_graph_t *cfg` → `*bbg`, `BB_t *nd` → `*bb` via strict-word-boundary sed. ~2765 sites across 10 files. One collision: `Pl_PredEntry_BB *bb` at `bb_exec.c:3196` (inside a function whose `BB_t *nd` parameter also renamed to `bb`) → renamed Prolog-entry local to `*pe`. Pure rename — gates identical to pre-rename.
- **CASE-EXPR** (Opus 4.7, 2026-05-28, `d1031b0c`): Icon `TT_CASE` was misrouted through Snocone-shaped branches in `lower_case`. Two bugs: (a) when Icon's trailing default body was `TT_QLIT` (e.g. `default: "other"`), the legacy-Snocone branch interpreted it as an end-label name and silently dropped it; (b) modern-Snocone branch did `lower_expr(body); SM_VOID_POP` per arm then final `SM_PUSH_NULL`, destroying case-as-expression value. Fix: gate both branches on `g_lang == LANG_SNO`. Icon now falls through to the `!is_raku` branch (line ~1419), which already handles `has_def = (t->n - 1) % 2` and preserves arm values. Recovered all 5 rung33 cases. Watermark 165 → **170**, zero regressions. Pre-existing Snocone `semantic` failures (3) confirmed unrelated via stash-and-test.
- **PARAM-SHADOW** (Opus 4.7, 2026-05-28, `4d5fe69e`): applied the diagnosis from CASE-EXPR session. In `src/lower/lower.c::emit_var_load`, the LANG_ICN proc-as-value fallback fired BEFORE `scope_get(g_proc_scope, vn)`. Any parameter whose name happened to satisfy the proc-table walk or `icn_proc_as_value(vn).v == DT_S` was emitted as `SM_PUSH_VAR` instead of `SM_LOAD_FRAME` — parameters were not shadowing proc names. Symmetric with `emit_var_store` (line 153) which already checked scope first. Fix: reorder. Recovered `rung32_strretval_basic_strret` (was printing `hello name` instead of `hello world`). Watermark 170 → **171**. NOT a 20+ pickup as the diagnosis estimated — `rung36_jcon_*` family still FAILs on `** Error 5` (different code path).
- **LIMIT-EXPR + rung37 runner glob** (Opus 4.7, 2026-05-28, `471ac1c9`): two fixes. (a) `src/lower/lower.c::lower_limit` was `lower_unhandled` stub, so TT_LIMIT in lower_expr context (`every write((1 to 5) \ 3)`, call-arg, `:=` RHS, bare stmt) emitted SM_PUSH_NULL and the every-loop scanned no SM_BB_INVOKE — entire rung14 dark. Fix mirrors `lower_to` / ALT-EXPR (`8b0ad2ba`) / CASE-EXPR (`d1031b0c`): build BB CFG, SM_seq_bb_add, SM_BB_INVOKE. `lower_icn_new_Limitation` + `bb_exec.c::BB_LIMIT` were already present. Recovered 5/5 rung14 + bonus `rung30_builtins_misc_seq`. (b) `scripts/test_icon_all_rungs.sh` runner glob covered `rung0[1-9]/rung1[0-9]/rung2[0-9]/rung3[0-5]` + explicit `rung36_*`, but `rung37` was silently absent — added `rung37_*` loop, 14 tests now visible (6 PASS / 8 FAIL). TOTAL 269 → 283.
- **BANG-EXPR** (Opus 4.7, 2026-05-28, `381df169`): `src/lower/lower.c::lower_iterate` for LANG_ICN was the SAME anti-pattern as pre-fix `lower_alt` and pre-fix `lower_limit` — building bbg via `lower_icn_expr_top` then immediately `BB_free(bbg)` and calling `lower_unhandled(t)`. So TT_ITERATE in lower_expr context (`every write(!L)`, call-arg, `:=` RHS, bare stmt) emitted SM_PUSH_NULL — entire rung22 bang_list/put_bang + entire rung31 sort/sortf dark because the enclosing every-loop scanned no SM_BB_INVOKE. The path that worked all along: when TT_ITERATE is a child of TT_EVERY the every-loop wrapper rebuilds it via `lower_icn_expr_top`, which is why rung15/16 partially worked. Plain bare-arg path was broken. Fix mirrors `lower_to` / `lower_limit`. Recovered 10 rungs across 5 rung-files: rung11_bang_augconcat_bang_str, rung13_table_iterate, rung15_iterate_string, rung22 (2), rung31 (5).
- **GEN-BUILTIN find()/key()** (Opus 4.7, 2026-05-28, `8cc487e9`): `src/lower/lower.c::lower_fnc` shape-2 dispatch (`t->v.sval == NULL`, name in `t->c[0]->v.sval`) emitted SM_CALL_FN for every function call, including Icon TRUE generators like `find()` and `key()` that already had BB_FIND_GEN / BB_KEY_GEN infrastructure in `lower_icn.c::lower_icn_new_Call` + bb_exec executors. Without SM_BB_INVOKE in the SM stream, enclosing every-loop saw no generator switch and pumped only the first value (`every write(find('a','banana'))` → `2` instead of `2 4 6`). Fix: in the shape-2 branch, if `g_lang==LANG_ICN` and call target is `find` or `key`, build BB CFG via `lower_icn_expr_top` and emit SM_BB_INVOKE instead. Recovered `rung08_strbuiltins_find_gen`. `key(t)` as standalone generator works now (`every write(key(t))` emits 3 keys); `rung23_table_table_key` still FAILs because `key(t)` is now generating but the result feeds `t[key(t)]` subscript and hits a SEPARATE stack-underflow (same family as `rung16 s[1 to 3]`). Different failure mode, not a regression.
- **rung36 category sidecar + per-category runner subtotals** (Opus 4.7, 2026-05-28, corpus `e89681b` + one4all `64c7530c`): the 75-test rung36 JCON pool was a single opaque bucket. Sidecar `corpus/programs/icon/rung36_categories.txt` maps each test to one of 8 intent categories (control 13, gens 12, strings 11, scan 9, reflection 9, numbers 8, structures 7, io 6, sum=75). Runner reads sidecar and emits per-category subtotals between rung body and overall total. Triage now visible by area: `rung36_strings` already moving (5 PASS), `rung36_scan` is best signal/noise pure-FAIL pool (6 FAIL, 3 XFAIL), `rung36_gens` needs mode-4 zipper. Zero file renames, zero git history disturbance, JCON provenance preserved.

---

## Watermarks

- **Pre-MAIN-BOOT:** `64ca51b7` — smoke_icon 5/5 · broker 36 · rungs 199 · smoke_prolog 5/5 · FACT 0.
- **Post-SNOBOL4 LANG-IGNORANT** (`08e05f68`): smoke_icon **0/5** (PUMP_PROC whacked).
- **MAIN-BOOT** (Opus 4.7, 2026-05-28, `80d0d5ee`): smoke_icon **5/5** · smoke_prolog 5/5 · broker 35 · rungs **161** · FACT 0.
- **ALT-EXPR** (Opus 4.7, 2026-05-28, `8b0ad2ba`): rungs **165** · broker 35 · FACT 0.
- **CASE-EXPR** (Opus 4.7, 2026-05-28, `d1031b0c`): rungs **170** · broker 35 · FACT 0.
- **PARAM-SHADOW** (Opus 4.7, 2026-05-28, `4d5fe69e`): rungs **171** · broker 35 · FACT 0.
- **LIMIT-EXPR + rung37 glob** (Opus 4.7, 2026-05-28, `471ac1c9`): rungs **183** PASS / TOTAL 283 · broker 35 · FACT 0.
- **BANG-EXPR** (Opus 4.7, 2026-05-28, `381df169`): rungs **193** PASS / TOTAL 283 · broker **36** (+1) · FACT 0.
- **GEN-BUILTIN** (Opus 4.7, 2026-05-28, `8cc487e9`): rungs **194** PASS / FAIL 53 / XFAIL 36 / TOTAL 283 · broker 36 · FACT 0.
- **rung36 category split** (Opus 4.7, 2026-05-28, one4all `64c7530c` + corpus `e89681b`): runner-only change, outcomes unchanged. Per-category snapshot at this watermark:
  ```
  rung36_control       total=13  PASS= 0  FAIL= 4  XFAIL= 9
  rung36_gens          total=12  PASS= 0  FAIL= 6  XFAIL= 6
  rung36_io            total= 6  PASS= 0  FAIL= 3  XFAIL= 3
  rung36_numbers       total= 8  PASS= 0  FAIL= 3  XFAIL= 5
  rung36_reflection    total= 9  PASS= 1  FAIL= 4  XFAIL= 4
  rung36_scan          total= 9  PASS= 0  FAIL= 6  XFAIL= 3
  rung36_strings       total=11  PASS= 5  FAIL= 4  XFAIL= 2
  rung36_structures    total= 7  PASS= 0  FAIL= 3  XFAIL= 4
  ```

---

## Acceptance greps

Use `grep -P` or fixed-strings. POSIX `[αβ]` doesn't match UTF-8 → false 0.
1. `grep -nE 'bb_operand_aux_set' src/lower/lower_icn.c | wc -l` == 0 ✅
2. `grep -cF 'bb_exec_node(nd->α)' src/lower/bb_exec.c` + `grep -cF 'bb_exec_node(nd->β)' src/lower/bb_exec.c` — legacy-arm count; ~45+30 remain in unmigrated WHILE/UNTIL/REPEAT/CASE/SCAN/EVERY-fallback. The migrated set (BINOP/LCONCAT/SECTION/IDX/IDX_SET/CONJ/ALT/IF/ASSIGN/CALL + flat-wire EVERY incl. block bodies) is α/β-free.
3. `icn_kind_owns_omega_operand` removed ✅
4. rungs PASS at/near watermark.

---

## Next options

1. **rung36_scan cluster (6 FAIL, 3 XFAIL).** Best signal-to-noise pure-FAIL pool. Icon scanning environment (`?`, `&pos`, `&subject`, `tab`, `move`, `upto`) is a coherent feature; fixing scan plumbing could clear several together. Probes: `rung36_jcon_scan`, `scan1`, `scan2`, `concord`, `diffwrds`, `endetab`, `subjpos`, `wordcnt`, `parse`. Per-category subtotals from `test_icon_all_rungs.sh` will measure progress directly.
2. **`every <var> <augop>:= <gen>` stack underflow** — affects rung10_augop_break_repeat (`every sum +:= (1 to 5)`), rung11_bang_augconcat_bang_concat (`every result ||:= !s`). Pre-existing, reproducible with bare `every sum +:= (1 to 3)`. Symptom: `sm_interp: stack underflow`. Likely the augmented-assign SM_DUP sequence is wrong inside the every β-resume — the LHS pointer is consumed without re-pushing. Goal file flagged this for sessions. Worth a focused dig.
3. **Generator-in-subscript stack underflow** — affects rung16_subscript_sub_every (`s[1 to 3]`) and the post-GEN-BUILTIN rung23_table_table_key (`t[key(t)]`). Same family. The subscript lowering doesn't engage the generator pump on the index expression.
4. **Block-body BREAK/NEXT on the new BANG-EXPR path** — rung35_block_body_every_gen_block. The `every v := !L do { ... break/next ... }` now runs (BANG-EXPR fix), but the inner break/next don't honor the phase machine that BODY-MEDIATED `ival=3` set up in TO/TO_BY (`cba1dc4d`/`aa3e403f`). BB_LIST_BANG executor needs the same phase machine, or `lower_iterate` needs to route through the block-body-aware scaffolding when there's a do-body.
5. **rung37 newly-visible tactical fails (8).** `augop_pow`, `coerce`, `cset_ops`, `keywords`, `mutual`, `neg_pos`, `proc_lookup`, `scan_alt`. Each is a focused construct; some may be quick. Two tests have no `.expected` file (`rung37_every_do_hello`, `rung37_every_in_arg`) — could be intentional (silent-skip via runner's `[ -f "$exp" ] || return 0`).
6. **rung13 cartesian product alt** (4 FAIL) — `alt_alt_nested`, `alt_alt_augconcat`, `alt_alt_cross_arg`, `alt_alt_cross_arg_sideeffect`. Needs mode-4 ICN-Z zipper / BB-port-graph. NOT quick.
7. **rung03 suspend_gen family** (3 FAIL) — generator-proc semantics on `SM_CALL_FN` path. Needs GeneratorState wiring on the call side. NOT quick.
8. **Audit the same anti-pattern in remaining `lower_X` functions.** This session cleared LIMIT, ITERATE, find/key — same shape as ALT-EXPR and CASE-EXPR from prior sessions. Pattern: `lower_X` for LANG_ICN builds `bbg` via `lower_icn_expr_top`, immediately `BB_free(bbg)`, calls `lower_unhandled`. Still present at `lower.c:1559 lower_bang_binary` (binary `!` — proc-apply, e.g. `(!plist) ! alist` in rung36_jcon_args). The binary-bang doesn't have a `lower_icn_new_BangBinary` entry in `lower_icn.c`, so a fix here would need new BB infrastructure. Lower priority — only rung36_jcon_args and a couple others use it.
10. **Icon scanning ops have no dedicated BB templates** (raised end of 2026-05-28 session). `tab`, `move`, `match`, `any`, `many`, `bal`, `pos` are runtime-only via `SM_CALL_FN` (registered in `src/runtime/interp/icn_runtime.c:449`). They are single-shot, which is semantically correct for the ops themselves, but they don't participate in BB-graph odometer pumping when their *arguments* are generators — `tab(1 to 10)` in a scan context needs the outer every-loop to drive the `1 to 10` and re-fire `tab`. Currently the BB dispatch in `lower_fnc` only recognises a small set (find, key, list-bang); scan builtins fall through to flat `SM_CALL_FN`. Likely root cause for several `rung36_scan` and `rung37_scan_alt` FAILs. `BB_PAT_TAB`/`BB_PAT_ANY`/`BB_PAT_POS` in `BB.h` are SNOBOL4/Snocone pattern primitives — DIFFERENT family, not reusable for Icon scanning. Need either: (a) odometer support on `SM_CALL_FN` for argument generators, or (b) dedicated `BB_TAB`/`BB_MOVE`/`BB_MATCH` BB kinds with templates. Option (a) is smaller surface area.
11. Take up another goal.

---

## Per-step gate

```bash
bash scripts/build_scrip.sh
bash scripts/test_smoke_icon.sh              # PASS=5
bash scripts/test_icon_all_rungs.sh          # PASS at/near watermark
bash scripts/test_smoke_prolog.sh            # PASS=5
bash scripts/test_smoke_unified_broker.sh    # PASS≥30
grep -rnE 'seg_byte\(SEG_|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/ | grep -v _templates/ | grep -v emit_core | wc -l  # ==0
grep -cF 'bb_exec_node(nd->α)' src/lower/bb_exec.c
grep -cF 'bb_exec_node(nd->β)' src/lower/bb_exec.c
```

---

## DO NOT
- Touch SNOBOL4 / Snocone / Rebus / Raku / Prolog lower or BB families.
- Touch BB_PAT_*.
- Add fields to BB_t.
- Use `nd->α` / `nd->β` as tree pointers for new Icon code.
- Rely on POSIX `[αβ]` grep — use `grep -P` or fixed strings.
- Stamp anything on `SM_BB_INVOKE.a[0]` — it's the α/β state flag at runtime. Use `a[2]`.

---

## Session Setup

```bash
cd /home/claude/one4all
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
bash scripts/test_smoke_icon.sh
bash scripts/test_smoke_unified_broker.sh
bash scripts/test_icon_all_rungs.sh
```

---

## Architecture

```
.icn → icon_parse() → AST_t*
  --interp   → execute_program() → interp_eval()        Mode 2 (SM+BB C walker, reference)
  --run      → lower() → sm_codegen_x64() → exec        Mode 3 (in-proc, PROT_EXEC)
  --compile  → lower() → sm_codegen_x64() → binary      Mode 4 (separate process)
```

## THE FOUR FACTS
1. C WALKERS: MODE 2 ONLY.
2. NO C WALKERS IN MODE 3/4.
3. SM + BB DO NOT EXIST AT RUNTIME IN MODE 3/4.
4. ONE x86 PRODUCER — templates only (FACT RULE).

---

## File ownership
`src/lower/lower_icn.c` · `src/lower/lower.c` (epilogue/every-scaffold) · `src/lower/bb_exec.c` · `src/emitter/{emit_bb.c,emit_sm.c,emit_core.c}` · `src/emitter/BB_templates/bb_*.cpp` · `src/emitter/SM_templates/sm_bb_switch.cpp` · `src/processor/sm_codegen.c` · `src/processor/sm_interp.c` · `baselines/icon-bb/`
