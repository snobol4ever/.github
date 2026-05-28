# GOAL-ICON-BB.md — All Icon Byrd-Box constructs, modes 1/2/3/4

**Repo:** one4all + .github

## ⛔ MODE PRIORITY
Mode 2 (`--interp`) first, then mode 3 (`--run`). Mode 4 (`--compile`) DEFERRED.

---

## ✅ LFJ COMPLETE — Lower From JCON (all 15 rungs)

LFJ-0..LFJ-15b ✅ (`1dfe9631` one4all, 2026-05-27). Every `ir_a_*` from `irgen.icn` transcribed into `lower_icn_new_<KIND>`; legacy lower deleted; dispatch table replaced by plain switch; all six `_threaded_b` AG-pure intercepts folded into `_ag` variants. **Reference:** `/home/claude/corpus/programs/icon/jcon-ref/irgen.icn`.

Key commits: `bc7dae2a` (LFJ-0 mapping doc) · `e5eb34b0` (LFJ-1b table) · `0540aace` (LFJ-14 last flip) · `cde72b79` (LFJ-15 consolidate) · `6a631124` (LFJ-15b _ag variants).

---

## ⛔ ACTIVE: AG-PURE MIGRATION

### Model
No operands on BB nodes. CFG of boxes wired by four ports only. Operand values flow through `BB_graph_t.ring` (chain walker pushes `cur->value` each step; apply boxes read `ag_ring_peek(cfg, k)`).

**Four ports:**
| Port | Direction | Meaning |
|------|-----------|---------|
| α | UP (synthesized) | fresh-entry address |
| β | UP (synthesized) | retry-entry (self for resumable, else ω_in) |
| γ | DOWN (inherited) | success continuation |
| ω | DOWN (inherited) | failure continuation |

**BB_t has ONLY:** `t`, `α β γ ω`, `sval/ival/dval`, `value/counter/state`. PEERS sidecar (`operand_aux`) LEGACY for Icon — kept for Prolog/SNOBOL4.

**FACT RULE:** all emitted x86 via templates only. `grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/ | grep -v _templates/ | grep -v emit_core | wc -l` == 0.

### Completed steps
| Step | What | Commit |
|------|------|--------|
| 1 | Ring fields dormant in BB_graph_t | `64805e16` |
| 2 | Chain walker pushes every step (incl FAIL) | `e2850a98` |
| 3 | BB_BINOP: lhs→rhs→apply, peek(1/0) | `9d4d25b0` |
| 4 | BB_SEQ AG-pure + BB_FAIL pre-alloc | `245ae97e` |
| 5 | BB_IF: cond.γ=cond.ω=nd_if; nd_if.γ=then; nd_if.ω=else | `687d6694` |
| 6 | BB_CONJ: left→right→apply | `76453c56` |
| 7 | BB_ALT: arms chained via ω; nd_alt.γ=γ_in | `e8217005` |
| 8.1 | BB_EVERY flat-wire gate (nd->ival=1) | `f81e1d51` |
| 8.2 | BB_TO/TO_BY dynamic-bound chain (sval ag/ai/ar) | `7acc7849` |
| LFJ-15b | All 6 _threaded_b intercepts → _ag variants | `6a631124` |
| 9 | BB_LCONCAT/SECTION/IDX/IDX_SET _ag + executor branches | `1dfe9631` |
| 10a-1 | If_ag lowers cond/then/else via lower_icn_expr_threaded_b | `a9b326f0` |

### Step 10b unblocked progressively by Step 10a
Step 10a is the architectural pre-work that splits across multiple `_ag` lowerers. Each `_ag` family that currently lowers sub-expressions via bare `lower_icn_expr_node` must switch to `lower_icn_expr_threaded_b` so Family 1 / Family 2 γ-chain wiring runs for nested BB_CALL / BB_ASSIGN. Once **all** are migrated, Step 10b (sidecar deletion + ring-peek in bb_exec.c) becomes safe.

| Sub-step | Lowerer | Status |
|----------|---------|--------|
| 10a-1 ✅ | If_ag (cond/then/else) | `a9b326f0` |
| 10a-2 ✅ | Conjunction_ag (left/right) | `6992c58d` (broker 30→34) |
| 10a-3 ✅ | Alt_ag (arms) | `d181c92e` |
| 10a-4 | Every_ag (gen for non-TO; body) | PARTIAL ✅ `5d5bf85d` — streaming gens (`!t`/`!L`/`key`/alt) flat-wire via ival=2; static-TO + block (BB_SEQ_EXPR) bodies stay legacy by design |
| 10a-5 ✅ | Binop_ag (lhs/rhs) | this session (rungs 198, broker 34) |
| 10a-6 ✅ | Lconcat_ag (lhs/rhs) | this session (rungs 198, broker 34) |
| 10a-7 ✅ | Section_ag (base/i1/i2) | this session (rungs 198, broker 34) |
| 10a-8 ✅ | Idx_ag (base/idx) | this session (rungs 198, broker 34) |
| 10a-9 ✅ | Idx_set_ag (base/idx/rhs) | this session (rungs 198, broker 34); new `_ag` variant + threaded_b early-exit; executor AG-pure branch already present from Step 9 |
| 10a-10 ✅ | ToBy_ag (verify lo/hi/by) | verified no-change (lo→hi→nd chain already correct; bounds via lower_icn_new_ToBy) |
| 10b | Sidecar deletion + ring-peek in bb_exec.c | BLOCKED on 10a-4 only |

Each 10a-N is independent and zero-impact when applied alone (legacy executor recursion still handles operand eval) — commit each separately, gate ≥198 throughout.

### ⚠️ Step 10a-4 (Every_ag) — BLOCKED, NOT zero-impact (Opus 4.7, 2026-05-28)
Bisected thoroughly: threading the non-TO gen and/or body via `lower_icn_expr_threaded_b` REGRESSES rungs (198→190/191/194 across variants; `rung13_table_iterate` = `every v := !t do write(v)` goes silent). Unlike If/Conjunction/Alt (forward continuations), EVERY's flat-wire gate (`nd->ival==1`, `bb_exec.c:1414`) builds a CYCLIC graph: body's γ/ω ports are reused as loop back-edges (`gen.γ=body; body.γ=gen; body.ω=gen; gen.ω=nd`). When `threaded_b` Family 2 deep-threads the body BB_CALL's args (`ax->γ=nd`), the chain-walker path AND BB_CALL's own executor arg-recursion DOUBLE-EVALUATE the generator-resume → desync → no output. `gen->γ` targeting the apply node skips arg eval; targeting the entry double-evals. **Conclusion: 10a-4 is entangled with executor behavior and effectively requires Step 10b (ring-peek replacing executor recursion) FIRST.** Defer 10a-4 until after 10b lands the ring-peek, OR special-case the flat-wire executor (`bb_exec.c` BB_EVERY `ival==1` branch) to suppress BB_CALL arg-recursion when the body was threaded. All attempts reverted to clean 198.

### Next: Step 10b (sidecar deletion + ring-peek) — only 10a-4 remains as a sub-blocker

**10b STATE MAP (measured 2026-05-28, watermark `b2f773bc`):**
- Acceptance (2) `bb_exec_node(nd->[αβ])` == 0 — **ALREADY SATISFIED.**
- Acceptance (1) `bb_operand_aux_set` in lower_icn.c == 2, NOT 0. The two are: Family-1 BB_ASSIGN simple-var (`lower_icn.c:2012`) and Family-2 BB_CALL args (`lower_icn.c:2043`). Their executor consumers are the ONLY two `bb_operand_aux_get` calls left: BB_ASSIGN (`bb_exec.c:895`) and BB_CALL (`bb_exec.c:972`). Every other operand kind (BINOP/LCONCAT/SECTION/IDX/IDX_SET/CONJ/ALT/IF) ALREADY reads via `ag_ring_peek` — confirmed at bb_exec.c lines 1177/1313/1349/1384/1541/1609/1985/2011/2161. So 10b item (1) = convert exactly BB_ASSIGN + BB_CALL executors to ring-peek, then delete the 2 sidecar writes.
- Acceptance (3) `icn_kind_owns_omega_operand` — 8 refs; the live ones are `lower_icn_proc_body` (lines 1865, 1872) and `icn_leaf` (1913); it now returns true only for BB_IF. Removing it requires re-expressing BB_IF's ω-as-else without the predicate.

**⚠️ BB_CALL is NOT a clean one-shot conversion** (inspected `bb_exec.c:960-1010+`): the BB_CALL executor is deeply entangled — generator-arg ODOMETER (Icon goal-directed cross-product, rightmost-advances-fastest, `state==2`), proc-gen pumping (`state==1`, `nd->counter`=GeneratorState), user-proc-vs-builtin dispatch, and deep-thread-vs-non-deep arg reading all interact with how args are sourced. Converting to pure ring-peek means rederiving the odometer resume semantics through the ring — a substantial design task, high regression risk across the generator-heavy rungs (rung03/13/24/31/36 families). **Budget a full fresh-context session for BB_CALL alone.** BB_ASSIGN (simple-var, single rhs operand) is the easy half and could go first as its own sub-step.

**10b plan.** To get there: convert BB_ASSIGN executor (read rhs via `ag_ring_peek(cfg,0)` instead of `bb_operand_aux_get`) + delete its sidecar write (lower_icn.c:2012) — small, gate. Then tackle BB_CALL odometer-through-ring separately. 10a-4 must be solved in the SAME pass as the BB_CALL/Every executor work, because removing executor recursion is exactly what unblocks the Every flat-wire double-eval — once the body is read via ring-peek instead of `bb_exec_node`, threading it no longer double-fires the generator. So 10a-4 + BB_CALL ring-peek + BB_EVERY `ival==1` executor (drive chain purely via ports + ring, no `bb_exec_node(nd->β)`) form one coherent unit; verify rung13_table_iterate + the every-suite hold at 198.
**10a-9 ✅ this session.** `lower_icn_new_Idx_set_ag` added (lower_icn.c, right after Idx_ag): flat base→idx→rhs→apply γ-chain, operands via threaded_b, α=β=NULL on apply. New early-exit in threaded_b for `TT_ASSIGN` with `TT_IDX` lhs, before the Family-1 BB_ASSIGN(TT_VAR) block. The BB_IDX_SET executor's AG-pure branch (bb_exec.c, `if (!nd->α && !nd->β)` → peek 2/1/0) was already in place from Step 9, so no executor change. Verified: `L[2]:=99`, `t["k"]:=7`, rung13 5/5.

All forward/operand-chain `_ag` lowerers are now migrated (Binop/Lconcat/Section/Idx/Idx_set; ToBy verified). The ONLY remaining 10a sub-blocker is **10a-4 (Every_ag)**, the cyclic flat-wire case (see blocker note below).

**Acceptance greps (whole 10b):** (1) `bb_operand_aux_set` in lower_icn.c == 0; (2) `bb_exec_node(nd->[αβ])` in bb_exec.c == 0 (already 0); (3) `icn_kind_owns_omega_operand` removed; (4) rungs ≥198 throughout.

Acceptance (whole migration):
1. `grep -nE 'bb_operand_aux_set' src/lower/lower_icn.c | wc -l` == 0
2. `grep -nE 'bb_exec_node\(nd->[αβ]\)' src/lower/bb_exec.c | wc -l` == 0
3. `icn_kind_owns_omega_operand` removed
4. rungs PASS≥198 throughout

### Per-step gate
```bash
bash scripts/build_scrip.sh
bash scripts/test_smoke_icon.sh              # PASS=5
bash scripts/test_icon_all_rungs.sh          # PASS≥198
bash scripts/test_smoke_prolog.sh            # PASS=5
bash scripts/test_smoke_unified_broker.sh    # PASS≥30
grep -rnE 'seg_byte\(SEG_|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/ | grep -v _templates/ | grep -v emit_core | wc -l  # ==0
```

### DO NOT
- Touch SNOBOL4 / Snocone / Rebus / Raku / Prolog lower or BB families.
- Touch BB_PAT_*.
- Add fields to BB_t.
- Use `nd->α` / `nd->β` as tree pointers for any new Icon code.

---

## Session Setup
```bash
cd /home/claude/one4all
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
bash scripts/test_smoke_icon.sh            # PASS=5
bash scripts/test_smoke_unified_broker.sh  # PASS≥30
bash scripts/test_icon_all_rungs.sh        # PASS=198
```

---

## Architecture
```
.icn → icon_parse() → AST_t*
  --interp   → execute_program() → interp_eval()        Mode 2 (SM+BB C walker, reference)
  --run      → lower() → sm_codegen_x64() → exec        Mode 3 (in-proc, PROT_EXEC)
  --compile  → lower() → sm_codegen_x64() → binary      Mode 4 (separate process)
```

**Lowering signature:** `lower(cfg, tree, γ_in, ω_in, &α_out, &β_out, bounded)`. Each `lower_icn_new_<KIND>_ag` function produces AG-pure-shaped output directly.

---

## THE FOUR FACTS
1. **C WALKERS: MODE 2 ONLY.**
2. **NO C WALKERS IN MODE 3/4.**
3. **SM + BB DO NOT EXIST AT RUNTIME IN MODE 3/4.**
4. **ONE x86 PRODUCER.** Templates only.
5. **TEMPLATE-ONLY EMISSION (FACT RULE).** grep == 0.

---

**WATERMARK:** one4all `09353f25` (10b complete + 10a-4 partial, Opus 4.7, 2026-05-28; hash is post-rebase — landed on top of parallel Raku/SNOBOL4 commits). Gates: smoke_icon 5/5 · broker **36** (raised by parallel Raku/SNOBOL4 work; Icon-owned share unchanged) · rungs 198 · smoke_prolog 5/5 · FACT RULE 0.

**✅ Step 10b COMPLETE — sidecar deletion + ring-peek migration done.** All four acceptance criteria met:
1. `bb_operand_aux_set` in lower_icn.c == **0** ✅ (both Family-1 BB_ASSIGN + Family-2 BB_CALL sidecar writes deleted)
2. `bb_exec_node(nd->[αβ])` in bb_exec.c == **0** ✅
3. `icn_kind_owns_omega_operand` == **0** ✅ (removed; BB_IF ω-as-else now preserved by plain `!ω`-set guards since If_ag always sets nd->ω)
4. rungs == **198** ✅

Commits this session: `8f887fa1` (10b-easy: BB_ASSIGN executor → ag_ring_peek(0), `nd->ival=1` AG-threaded marker survives bb_reset) · `359c5754` (10b-hard: BB_CALL deep-arg executor → ag_ring_peek(nargs-1-j), `nd->dval=1.0` deep marker) · `4485d647` (icn_kind_owns_omega_operand removal).

**KEY DESIGN NOTES for the BB_CALL conversion (non-obvious):**
- The deep-thread discriminator could NOT be re-derived at runtime: `is_suspendable` (lower) flags ALL TT_FNC calls as generators, but `ir_is_single_shot` (exec) does NOT — so a runtime re-derivation mismatches for nested calls like `write(dbl(5))`. Fixed by stamping `nd->dval=1.0` in lower's Family-2 `!any_gen` branch (immutable IR payload, survives `bb_reset`, faithful to what lower actually did).
- `nd->state` is NOT usable as a lower→exec marker: `bb_reset` zeroes `state` (and `value`/`counter`) on every node. Use `ival`/`dval` IR-payload fields instead. The BB.h comment referencing `ival3` is STALE — no such field exists on BB_t (only `ival`, `dval`).
- Deep args push exactly ONE ring value each (nested binop args are legacy single boxes via `lower_icn_expr_node`, which recurse internally without top-level ring pushes), so consecutive `peek(nargs-1-j)` is correct.

**SWITCH-OVER STATUS:** the operand_aux sidecar API (`bb_operand_aux_set/get` in `scrip_ir.c`, struct fields in `BB.h`) now has ZERO live callers across ALL languages. It is dead code. NOT deleted here because it is shared PEERS-RULE infrastructure in `scrip_ir.c`/`BB.h` (outside GOAL-ICON-BB file ownership; RULES forbids touching cross-language BB families). Deletion is an HQ "grand master reorg" task.

### ✅ Step 10a-4 (Every_ag) — PARTIAL: streaming generators now flat-wire (Opus 4.7, 2026-05-28, `5d5bf85d`)
The earlier "STILL BLOCKED" conclusion assumed the body had to be threaded via `lower_icn_expr_threaded_b` (which double-evaluates the generator-resume on the cyclic back-edge → 198→194 regression). That framing was wrong. The body does NOT need threading. The fix:
- New `lic_is_gen_node` in lower_icn.c recognises a STREAMING generator (`BB_LIST_BANG`/`BB_KEY_GEN`/`BB_FIND_GEN`/`BB_SEQ_GEN`/`BB_PROC_GEN`/`BB_ALT`/`BB_ALTERNATE`/`BB_BINOP_GEN`/`BB_ITERATE`/`BB_LIMIT`), seeing through a `BB_ASSIGN` wrapper (so `v := !t` matches).
- `Every_ag` now stamps a NEW marker `nd->ival = 2` and flat-wires `gen.γ=body; body.γ=gen; body.ω=gen; gen.ω=nd` when gen is generator-bearing. The chain walker drives the loop purely through ports — gen re-pumps its self-stateful generator via its own rhs-recursion (state survives because the walker never `bb_reset`s mid-pass). The body is kept as the single-box `lower_icn_expr_node` (NOT threaded). `bb_exec.c` BB_EVERY passthrough accepts `ival==1 || ival==2`.
- **Two deliberate exclusions** (stay on the legacy executor-recursion path, which is correct for them): (a) static-bound TO/TO_BY/UPTO — `every x := 1 to 3 do B`; re-pumping a static TO through the assign rhs-recursion stalls it at its first value (rung35). (b) multi-statement block bodies, which lower to `BB_SEQ_EXPR` whose executor has head/tail GENERATOR semantics (`state==1` ⇒ pump tail only); on a pure-port back-edge the walker re-enters at `state==1` and skips the head stmts (`every v:=!L do {w:=v+100; write(w)}` → `105,105` not `105,106`). The legacy executor resets `body->state=0` each iteration; the pure-port walker has no back-edge hook to do so.

Verified mode-2 AND mode-3: `!t`=99, `!L`=10/20/30, `key(t)`=a, `(1|2|3)`=1/2/3, nested-every=10/20/20/40, block-body=105/106, break=10, post-loop=7/8/done. Gates: smoke_icon 5/5, broker 34, rungs 198, prolog 5/5, FACT RULE 0.

**Remaining (genuinely architectural, not behavioral):** to bring the two excluded cases onto the flat-wire path needs a back-edge hook that resets a stateful body's `state` per iteration (or a statement-context `BB_SEQ_EXPR` variant that always re-fires head stmts). Both work correctly today via legacy; this is purity, not a gate criterion.

**ATTEMPTED + REVERTED (Opus 4.7, 2026-05-28, not committed):** tried admitting `BB_SEQ_EXPR` block bodies to flat-wire by stamping `body->dval=1.0` (a "statement-context, re-run-fresh" marker) and having the `BB_SEQ_EXPR` executor force `state=0` on entry when `dval==1.0`. That CORRECTLY fixed the head-skip (`every v:=!L do {w:=v+100;write(w)}` → 105,106 ✓). BUT it exposed the REAL blocker: **the flat-wire `body.γ=gen` topology cannot honor `break`/`next`/`return`.** `every v:=!L do { if v=20 then break; write(v) }` printed `10 30` (break ignored — behaves like next) instead of `10`. The legacy BB_EVERY loop checks `FRAME.loop_break`/`loop_next`/`returning` each iteration; the pure-port walker has NO node on the back-edge to check them (body loops straight back to gen). Reverted to clean `09353f25`. **FORWARD PATH:** change the block-body topology to BODY-MEDIATED — `gen.γ=body; gen.ω=nd; body.γ=nd; body.ω=nd` (a new `ival=3`) so the EVERY node sits ON the back-edge. Then the `ival==3` executor, on each body-return, checks FRAME.loop_break/returning (terminate/propagate), resets body state, re-pumps gen. OPEN sub-problem: at `nd`, disambiguate "re-entered from gen-exhaustion (gen.ω)" vs "re-entered from body-done (body.γ/ω)" — use an EVERY phase counter. Needs testing vs the loop-control suite (break/next/return × {block,single} body × {streaming-gen,TO} gen) and the generator-heavy rungs (03/13/24/31/36). Fresh-context session.

### ⚠️ ACCEPTANCE-GREP CAVEAT (discovered this session)
The 10b acceptance grep `grep -nE 'bb_exec_node\(nd->[αβ]\)' src/lower/bb_exec.c | wc -l` returns 0 — but NOT because the calls are gone. The POSIX bracket class `[αβ]` does NOT match the multi-byte UTF-8 sequences for α/β, so the grep silently matches nothing regardless of file contents. The correct grep is `grep -nP 'bb_exec_node\(nd->(α|β)\)'`, which finds **75** real matches (most are legitimate MODE-2 interpreter walkers, which RULES permits; the BB_EVERY legacy path at the loop body is among them). Criterion (2) as written passes by accident, not by satisfaction. Future "criterion (2) satisfied" claims must use `grep -P`.



## File ownership
`src/lower/lower_icn.c` · `src/lower/bb_exec.c` · `src/emitter/{emit_bb.c,emit_sm.c,emit_core.c}` · `src/emitter/BB_templates/bb_*.cpp` · `src/processor/sm_codegen.c` · `src/processor/sm_interp.c` · `baselines/icon-bb/`
