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

---

## Watermarks

- **Pre-MAIN-BOOT:** `64ca51b7` — smoke_icon 5/5 · broker 36 · rungs 199 · smoke_prolog 5/5 · FACT 0.
- **Post-SNOBOL4 LANG-IGNORANT** (`08e05f68`): smoke_icon **0/5** (PUMP_PROC whacked).
- **MAIN-BOOT** (Opus 4.7, 2026-05-28, `80d0d5ee`): smoke_icon **5/5** · smoke_prolog 5/5 · broker 35 · rungs **161** · FACT 0.
- **ALT-EXPR** (Opus 4.7, 2026-05-28, `8b0ad2ba`): smoke_icon **5/5** · smoke_prolog 5/5 · broker 35 · rungs **165** · FACT 0. TT_ALTERNATE in `lower_expr` now builds-and-invokes a BB CFG instead of emitting SM_PUSH_NULL. Remaining rung13 fails (`alt_alt_nested`, `alt_alt_augconcat`, `alt_alt_cross_arg`, `alt_alt_cross_arg_sideeffect`) are downstream: cartesian product over multiple generators inside one expression needs the ICN-Z zipper / BB-port-graph mode-4 path; `every <var> ||:= <gen>` has a pre-existing stack underflow (reproducible with `1 to 3` too).

---

## Acceptance greps

Use `grep -P` or fixed-strings. POSIX `[αβ]` doesn't match UTF-8 → false 0.
1. `grep -nE 'bb_operand_aux_set' src/lower/lower_icn.c | wc -l` == 0 ✅
2. `grep -cF 'bb_exec_node(nd->α)' src/lower/bb_exec.c` + `grep -cF 'bb_exec_node(nd->β)' src/lower/bb_exec.c` — legacy-arm count; ~45+30 remain in unmigrated WHILE/UNTIL/REPEAT/CASE/SCAN/EVERY-fallback. The migrated set (BINOP/LCONCAT/SECTION/IDX/IDX_SET/CONJ/ALT/IF/ASSIGN/CALL + flat-wire EVERY incl. block bodies) is α/β-free.
3. `icn_kind_owns_omega_operand` removed ✅
4. rungs PASS at/near watermark.

---

## Next options

1. **Recover the missing 54 rungs.** Real lowering bugs in `every <expr>` as the last statement of a proc — the `SM_PUSH_NULL` (every-as-expression result) followed by stranded `SM_VOID_POP` swallows the subsequent `return total`'s value. Was masked when `SM_BB_PUMP_PROC` bypassed SM. Affects rung02/03/13/14/22/31/32/33 patterns.
2. **MODE3 (`--run`) BB_CALL/EVERY native parity** — mode-2 + mode-3 already verified for migrated constructs.
3. **Migrate remaining loop kinds** (WHILE/UNTIL/REPEAT/CASE/SCAN) — would zero out the 45+30 legacy α/β calls.
4. **Generator-body Every_ag** — last legacy-path exclusion; needs flat-wire scheme for suspending body w/o BB_SEQ_EXPR head/tail trap.
5. Take up another goal.

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
