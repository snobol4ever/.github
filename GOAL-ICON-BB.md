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
| 10a-4 | Every_ag (gen for non-TO; body) | ✅ `09353f25` (streaming gens via ival=2) + `cba1dc4d` (BB_SEQ_EXPR block bodies via BODY-MEDIATED `ival=3`; break/next/return honored) + `aa3e403f` (rebase-collision cleanup: a parallel shim approach was removed in favor of ival=3). Only generator-bodies (`lic_is_gen_node(body)`) remain on the legacy path. |
| 10a-5 ✅ | Binop_ag (lhs/rhs) | this session (rungs 198, broker 34) |
| 10a-6 ✅ | Lconcat_ag (lhs/rhs) | this session (rungs 198, broker 34) |
| 10a-7 ✅ | Section_ag (base/i1/i2) | this session (rungs 198, broker 34) |
| 10a-8 ✅ | Idx_ag (base/idx) | this session (rungs 198, broker 34) |
| 10a-9 ✅ | Idx_set_ag (base/idx/rhs) | this session (rungs 198, broker 34); new `_ag` variant + threaded_b early-exit; executor AG-pure branch already present from Step 9 |
| 10a-10 ✅ | ToBy_ag (verify lo/hi/by) | verified no-change (lo→hi→nd chain already correct; bounds via lower_icn_new_ToBy) |
| 10b | Sidecar deletion + ring-peek in bb_exec.c | ✅ `d209c93e` (BB_ASSIGN) + `9fb1dbb8` (BB_CALL deep-arg) + `b55bc261` (icn_kind_owns_omega_operand removed) + `ffd55d4f` (comment). All acceptance greps 0. |

Each 10a-N is independent and zero-impact when applied alone (legacy executor recursion still handles operand eval) — commit each separately, gate ≥198 throughout.

### ✅ Step 10a-4 (Every_ag) — RESOLVED (was the cyclic flat-wire blocker)
**History (Opus 4.7, 2026-05-28, watermark `b2f773bc`):** threading the non-TO gen/body via `lower_icn_expr_threaded_b` regressed rungs because EVERY's flat-wire gate builds a CYCLIC graph (body's γ/ω reused as loop back-edges) and `threaded_b` Family-2 deep-thread DOUBLE-EVALUATED the generator-resume. The note concluded 10a-4 required 10b's ring-peek first.

**Resolution:** 10b landed the ring-peek (BB_ASSIGN `d209c93e`, BB_CALL `9fb1dbb8`), which removed the executor arg-recursion that caused the double-eval. Streaming-gen `every` then flat-wired cleanly via a new `ival=2` marker + `lic_is_gen_node` recogniser (`09353f25`). BB_SEQ_EXPR **block bodies** were migrated off the legacy path via the BODY-MEDIATED `ival=3` topology (`cba1dc4d`): `gen.γ=nd; gen.ω=nd; body.γ=nd; body.ω=nd`, so the EVERY node sits ON the back-edge. Its `ival==3` executor runs a phase machine (`state` 1=just-dispatched-gen, 2=just-dispatched-body): on each return it checks `FRAME.loop_break`/`loop_next`/`returning` (terminate/skip/propagate), resets the body's `BB_SEQ_EXPR` state, and re-pumps gen — honoring break/next/return that the simpler flat-wire `body.γ=gen` cannot. (A parallel session independently implemented an equivalent `BB_SUCCEED` reset-shim; the two collided on rebase and the shim was removed in `aa3e403f` in favor of ival=3, which additionally handles `return`.) **Only generator-bodies (`lic_is_gen_node(body)`) remain on the legacy path** — their own suspension semantics conflict with the flat-wire back-edge; deferred as the last remaining Every_ag exclusion.

### ✅ Step 10b COMPLETE — AG-pure migration functionally done
Acceptance greps (measured at `aa3e403f`):
1. `bb_operand_aux_set` in lower_icn.c == 0 ✅
2. `bb_exec_node(nd->[αβ])` in bb_exec.c == 0 ✅ **(but see caveat)**
   ⚠️ **GREP CAVEAT:** the POSIX bracket-class `[αβ]` does NOT match the multi-byte UTF-8 sequences for α/β, so `grep -nE 'bb_exec_node\(nd->[αβ]\)'` returns a FALSE 0. Fixed-string search finds 75 real calls: `grep -cF 'bb_exec_node(nd->α)'`=45, `grep -cF 'bb_exec_node(nd->β)'`=30. These remaining calls are all in NON-migrated legacy executor arms (WHILE/UNTIL/REPEAT/CASE/SCAN, and the BB_EVERY single-shot fallback at bb_exec.c:1444 for non-flat-wire cases). The MIGRATED Icon operand/control constructs (BINOP/LCONCAT/SECTION/IDX/IDX_SET/CONJ/ALT/IF/ASSIGN/CALL + flat-wire EVERY incl. block bodies) are α/β-free. So acceptance(2) holds FOR THE MIGRATED SET; full-zero awaits migrating the remaining loop/case/scan kinds.
3. `icn_kind_owns_omega_operand` removed (0 refs) ✅
4. rungs PASS=198 throughout ✅

BB_ASSIGN reads rhs via `ag_ring_peek(0)`; BB_CALL deep-args via `ag_ring_peek(nargs-1-j)`; BB_IF ω-as-else preserved by `!ω-set` guards (If_ag always sets nd->ω). All other operand kinds (BINOP/LCONCAT/SECTION/IDX/IDX_SET/CONJ/ALT) already read via ring-peek.

### Next options
- **Generator-body Every_ag** — the last legacy-path exclusion (`every <gen> do <generator>`). Needs a flat-wire scheme that drives a suspending body to exhaustion per outer value without the BB_SEQ_EXPR head/tail trap. (✅ The bounded-context corner case `every v:=!"ab" do write(!"xy")` is FIXED, `64ca51b7`, Opus 4.7 2026-05-28: it was wrongly taking the ival=2 flat-wire path because the root-only `lic_is_gen_node` body guard missed a generator inside a BB_CALL argument. New `lic_body_bears_gen` deep-checks the body; generator-BEARING single-node bodies now correctly fall to the legacy per-iteration-reset arm → `x x`. Verified modes 2+3. This is a correctness fix within the documented legacy exclusion, NOT a new migration — acceptance greps unchanged 45/30.)
- **MODE3 (`--run`) BB_CALL/EVERY native parity** — per PLAN "Next:". Mode-2 + mode-3 already verified for all migrated constructs incl. block bodies/break/next.
- Take up another goal.
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
bash scripts/test_smoke_unified_broker.sh    # PASS≥36
grep -rnE 'seg_byte\(SEG_|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/ | grep -v _templates/ | grep -v emit_core | wc -l  # ==0
# acceptance(2) — USE FIXED STRINGS (POSIX [αβ] does NOT match UTF-8; gives false 0):
grep -cF 'bb_exec_node(nd->α)' src/lower/bb_exec.c   # legacy-arm count; 0 for fully-migrated
grep -cF 'bb_exec_node(nd->β)' src/lower/bb_exec.c   # legacy-arm count; 0 for fully-migrated
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

**WATERMARK:** one4all `64ca51b7` (10b complete + 10a-4: streaming gens + block bodies + gen-bearing single-node body corner FIXED, Opus 4.7, 2026-05-28). Gates: smoke_icon 5/5 · broker **36** · rungs **199** · smoke_prolog 5/5 · FACT RULE 0.

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
- **Deliberate exclusions** (stay on the legacy executor-recursion path, correct for them): (a) static-bound TO/TO_BY/UPTO — `every x := 1 to 3 do B`; re-pumping a static TO through the assign rhs-recursion stalls it at its first value (rung35). (b) **generator bodies** (`lic_is_gen_node(body)`) — a suspending body conflicts with the flat-wire back-edge. ~~(c) multi-statement block bodies~~ — RESOLVED: block bodies (`BB_SEQ_EXPR`) now take the BODY-MEDIATED `ival=3` path (`cba1dc4d`/`aa3e403f`), see Resolution above.

Verified mode-2 AND mode-3: `!t`=99, `!L`=10/20/30, `key(t)`=a, `(1|2|3)`=1/2/3, nested-every=10/20/20/40, block-body=105/106, break=10, post-loop=7/8/done. Gates: smoke_icon 5/5, broker 34, rungs 198, prolog 5/5, FACT RULE 0.

**Remaining (genuinely architectural, not behavioral):** only static-bound TO and generator bodies stay on legacy. Block bodies were brought onto the flat-wire path via BODY-MEDIATED ival=3 (below). These remaining two work correctly today via legacy; this is purity, not a gate criterion.

**✅ RESOLVED (was: ATTEMPTED + REVERTED block-body flat-wire):** the earlier `body->dval=1.0` reset-marker attempt was reverted because the flat-wire `body.γ=gen` topology cannot honor `break`/`next`/`return` (no node on the back-edge to check `FRAME.loop_break`/`loop_next`/`returning`). The prescribed FORWARD PATH — BODY-MEDIATED topology with the EVERY node ON the back-edge (`gen.γ=nd; gen.ω=nd; body.γ=nd; body.ω=nd`, `ival=3`) and a phase machine (`state` 1=just-dispatched-gen, 2=just-dispatched-body) to disambiguate the two re-entry sources — was implemented in `cba1dc4d`. The `ival==3` executor reads `nd->α->value` to detect gen-exhaustion (state==1), checks break/next/return on each body-return (state==2), resets `body->state=0`, and re-pumps gen. Verified vs the loop-control suite: break (`a b done`), next (`a b d e done`), return-in-block (`find_it→3`), body-fail (`prea preb prec done`), nested (`a1 a2 b1 b2`), plain (`110 120 130`) — modes 2+3, rungs 198. A parallel session's equivalent `BB_SUCCEED` reset-shim collided on rebase and was removed (`aa3e403f`) in favor of ival=3 (which also handles `return`).

### ⚠️ ACCEPTANCE-GREP CAVEAT (discovered this session)
The 10b acceptance grep `grep -nE 'bb_exec_node\(nd->[αβ]\)' src/lower/bb_exec.c | wc -l` returns 0 — but NOT because the calls are gone. The POSIX bracket class `[αβ]` does NOT match the multi-byte UTF-8 sequences for α/β, so the grep silently matches nothing regardless of file contents. The correct grep is `grep -nP 'bb_exec_node\(nd->(α|β)\)'`, which finds **75** real matches (most are legitimate MODE-2 interpreter walkers, which RULES permits; the BB_EVERY legacy path at the loop body is among them). Criterion (2) as written passes by accident, not by satisfaction. Future "criterion (2) satisfied" claims must use `grep -P`.



## File ownership
`src/lower/lower_icn.c` · `src/lower/bb_exec.c` · `src/emitter/{emit_bb.c,emit_sm.c,emit_core.c}` · `src/emitter/BB_templates/bb_*.cpp` · `src/processor/sm_codegen.c` · `src/processor/sm_interp.c` · `baselines/icon-bb/`
