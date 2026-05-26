# GOAL-ICON-BB.md — All Icon Byrd-Box constructs in modes 1/2/3 (then 4)

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ NO AST WALKING IN MODES 2/3/4 — see RULES.md § "NO AST WALKING IN MODES 2, 3, OR 4"         ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  Sess 2026-05-15g removed all tree_t* dereferences from sm_interp.c (mode 2) and                ║
║  sm_jit_interp.c (mode 3). Stubs print [NO-AST] <opcode> on stderr.                              ║
║                                                                                                  ║
║  If a gate breaks with [NO-AST] FOO — write fresh SM/BB lowering for FOO.                       ║
║  Do NOT restore the AST-walking call.  Do NOT route through proc_table_call or any              ║
║  other back-door that hands a tree_t* to mode-2/3/4 code.                                       ║
║                                                                                                  ║
║  Mode 1 (`--interp` standalone AST interp) is unchanged and remains the reference path.        ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝


╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — CONSULT irgen.icn BEFORE IMPLEMENTING ANY BB KIND — NO EXCEPTIONS           ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  JCON's irgen.icn is the authoritative reference for every Icon BB (Byrd-box) construct.        ║
║  It contains ir_a_<Construct> procedures that show exactly what ports fire, what state is       ║
║  needed, and how generators compose. READ IT FIRST for every new BB kind.                       ║
║                                                                                                  ║
║  Location: /home/claude/corpus/programs/icon/jcon-ref/irgen.icn                                ║
║                                                                                                  ║
║  For TT_ITERATE (!E): ir_a_Unop with closure — the collection is evaluated once on α,          ║
║  then each element is yielded in order on β. Exhaustion → ω.                                   ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — NO NEW FUNCTIONS IN icon_box_rt.c / RT — NO EXCEPTIONS                      ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  Do NOT write rt_list_bang(), rt_iterate_something(), or any other C helper in                  ║
║  icon_box_rt.c, rt.c, or any runtime file to support a BB template.                             ║
║                                                                                                  ║
║  ALL logic for a BB kind must live in its BB_templates/bb_*.cpp file, emitted as inline x86.   ║
║  If the operation requires runtime state (counter, cached collection), store it in pBB->counter ║
║  and pBB->opaque — both are valid at JIT-emitter time and addressable via movabs.               ║
║                                                                                                  ║
║  The only permitted RT calls from a BB template are pre-existing PLT symbols                    ║
║  (subscript_get, rt_push_str, rt_push_int, GC_malloc, etc.) — not new functions you write.     ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** one4all + .github
**Sister docs:** `GOAL-CHUNKS.md`, `GOAL-CHUNKS-STEP17.md`, `GOAL-LANG-ICON.md`
**Carved:** 2026-05-10

**Done when:**
1. Every AST kind reachable from a `--interp` PASS Icon program lowers via `lower.c` to pure SM — no `emit_push_expr + SM_BB_PUMP` legacy fallthrough fires. Legacy block physically deleted.
2. `--ir-emit` byte-identical to pre-rung baseline for every corpus program.
3. `SCRIP_NO_AST_WALK=1 ./scrip --interp` == `./scrip --interp` for every program in the `--interp` PASS set (the *honest* gate).
4. Every SM opcode emitted by Icon lowering has a `sm_codegen_x64` mirror.
5. `is_suspendable` / `coro_eval` not reachable from SM dispatch under `SCRIP_NO_AST_WALK=1`.

⛔ **"Cheating":** `--interp` silently calls `coro_eval` for un-migrated kinds. `SCRIP_NO_AST_WALK=1` aborts on this. Output equality alone is not sufficient.

---

## Architecture

```
.icn → icon_parse() → AST_t*
  --ir-emit  → ir_print_program()                        Mode 1
  --interp   → execute_program() → interp_eval()         Mode 2  (AST walker)
  --interp   → lower() → SM_Program → sm_interp_run()   Mode 3
  --run  → lower() → sm_codegen_x64() → run         Mode 3.5
  --compile → lower() → sm_codegen_x64() → binary      Mode 4
```

Proebsting four-port template (start/resume/succeed/fail) → `SM_SUSPEND_VALUE` + goto wiring.
JCON gold: `/home/claude/jcon-extract/jcon-master/tran/irgen.icn` (69 `ir_a_<Construct>` procedures).

---

## Session Setup

```bash
cd /home/claude/one4all
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
bash scripts/build_spitbol_oracle.sh
```

Baseline gates (all green before picking up next rung):
```bash
bash scripts/test_smoke_icon.sh                 # PASS=5
bash scripts/test_smoke_unified_broker.sh       # PASS=17
bash scripts/test_icon_all_rungs.sh             # PASS=153 (regression recovers at G-4)
```

---

## ⚡ CURRENT WORK — Phase G: Eradicate BB_t.c[]/n

### GOLDEN BB RULE (established 2026-05-25, session with Lon)
BB_t is SCRIP's **IR node** — equivalent to JCON's `ir_*` instruction records (ir_IntLit, ir_Var, ir_Field, ...).
JCON has ONE IR. SCRIP has ONE IR: BB_t. The SM is NOT the IR — it is a 3-instruction bootstrap only.
JCON's four label ports → BB_t's four pointer ports (α/β/γ/ω).
JCON's per-record payload fields (val, name, field, op) → BB_t's `sval`/`ival`/`dval`.
Multi-scalar opcodes (e.g. BB_TO_BY with lo/hi/step) decompose into a chain of BB nodes.
BB_t must NOT have: `c[]`, `n`, `lhs`, `rhs`, `operand`, `opaque`, `sval2`, `ival2`, `ival3`.
BB_t DOES have: `sval`, `ival`, `dval` (IR payload) + `value`/`counter`/`state` (interpreter runtime).

BB.h has been updated to the correct struct. Build currently fails at emit_core.c:913 (`nd->c[]`/`nd->n`) — all `c[]`/`n`/`sval2`/`ival2`/`ival3`/`opaque` references across emitter + lower files must be migrated.

**NEXT STEP: G-1** — migrate all `c[]`/`n` references out of BB_t callers.

`BB_t` is a node in a **wired directed graph**. It is NOT a tree. `BB_t **c` and `int n` smuggle tree-child semantics into graph nodes. Every `nd->c[i]` on a `BB_t` is wrong.

**Architecture:**
```
tree_t         — produced by parser. Has c[]/n. Correct there.
  ↓ lower()
SM_sequence_t  — flat array of SM instructions (primary output of lower)
BB_graph_t     — wired directed graph of Byrd boxes, in sm.bb_table[]
```

Labels in JCON irgen.icn = pointers in SCRIP BB graphs. α/β/γ/ω are pointers.
- **γ/ω** inherited — caller sets where box jumps out on succeed/fail
- **α/β** synthesized — box's own entry points exposed to callers
- **lhs/rhs/operand** — operand sub-boxes the box evaluates; NOT control flow

**Baseline:** smoke 5/5, broker 17, rungs 153 (G-4 recovers to ≥169).

#### G-0 — Commit 2026-05-25 session work ✅ `bd6b0917`
SM_UNUSED_1..5 rename + F-6d partial (BB_BINOP/BINOP_GEN/LCONCAT/ARITH/UNIFY/BUILTIN/PL_ALT → α/β). Done. one4all `bd6b0917`, .github `213c9370`.

#### G-1 — Migrate all c[]/n/ival2/ival3/sval2/opaque out of BB_t callers ⏳
DONE (e099fdae): emit_core.c, lower_pl.c, lower_icn.c, icon_box_rt.c, scrip_ir.c,
  bb_builtin.cpp, bb_unify.cpp, bb_arith.cpp, bb_binop_gen.cpp, bb_pat_pos.cpp,
  bb_pat_tab.cpp, bb_to_by.cpp, bb_upto.cpp, bb_iterate.cpp, bb_pl_var.cpp.
REMAINING: bb_exec.c — 294 violations. Build fails at bb_exec.c:57.
Mapping used: c[0]→α, c[1]→β, c[2]→γ; ival2→ival or state (is_relop); ival3→state (has-run);
  sval2→dropped (runtime data); opaque→counter (ptr cast); nd->n→ival (arity) or dropped.

⚠️  STRUCTURAL GAP — γ/ω NOT FULLY WIRED:
The lowerer currently wires operands into α/β but does NOT thread γ (success) and ω (failure)
continuations through the graph. BB_node_alloc initialises α=nd (self), β=nd (self), γ=NULL, ω=NULL.
Most nodes exit with γ=NULL → executor crashes on success.
JCON solution: IR code-gen passes four label continuations DOWN into each recursive call so every
ir_* instruction is born with all four ports filled. SCRIP must do the same: lower_icn_expr_node
and lower_pl_stmt_node must accept (succ, fail) BB_t* arguments and wire them into every node
they create. This is the real G-1 gap — field renaming alone is not enough.
G-2 (bb_exec.c cleanup) can proceed mechanically, but the graph is not semantically correct
until continuation threading is added to the lowerer.

- [x] emit_core.c, all BB_templates, lower_pl.c, lower_icn.c, icon_box_rt.c, scrip_ir.c
- [ ] bb_exec.c (294 hits) — NEXT SESSION
- [ ] Thread γ/ω continuations through lowerer (lower_icn_expr_node, lower_pl_stmt_node)
- [ ] Gate: clean build, smoke 5/5, broker ≥17, rungs ≥153.

---

## ⚡ Phase H — The Attribute Grammar (decided with Lon, 2026-05-26)

**Decision: pointers, no label IR.** BB_t is the IR for ALL modes (2/3/4). Labels are a pure
emit-time artifact produced by walking the pointer graph; they are never stored in BB_t.
JCON's two labels per box → one SCRIP pointer per port + the *target node's* door selector.

### The four attributes
BB_t's four ports are an attribute grammar over the lowering traversal:

| Port | AG kind | Direction | Meaning |
|------|---------|-----------|---------|
| **γ** (gamma) | **inherited** | passed DOWN into a node | where to go on SUCCESS (the "after" box) |
| **ω** (omega) | **inherited** | passed DOWN into a node | where to go on FAILURE (the "before"/backtrack box) |
| **α** (alpha) | **synthesized** | passed UP from a node | the node's FRESH-entry address |
| **β** (beta)  | **synthesized** | passed UP from a node | the node's RETRY-entry address |

Lowering signature becomes:  `lower(cfg, tree, γ_in, ω_in, &α_out, &β_out)`.
γ/ω are values handed down; α/β are written back up through out-params.

### JCON irgen.icn is the per-construct wiring spec (NOT a mechanical graft)
JCON's IR (tran/ir.icn) is a flat instruction-list-with-labels (`ir_chunk(label, insnList)`,
`ir_Goto`, `failLabel` fields, named temps) — a DIFFERENT topology from BB_t's wired graph.
It CANNOT be transcribed. BUT every AST node `p` in irgen carries `p.ir` with exactly four labels
that map 1:1 onto our four ports:

| JCON `p.ir.<label>` | SCRIP port | AG kind |
|---------------------|-----------|---------|
| `p.ir.start`   | `nd->α` | synthesized (up) |
| `p.ir.resume`  | `nd->β` | synthesized (up) |
| `p.ir.success` | `nd->γ` | inherited (down) |
| `p.ir.failure` | `nd->ω` | inherited (down) |

Translation rules (verified against `ir_a_ToBy`, irgen.icn:1168):
- JCON `ir_Goto(X)` (jump to label) → SCRIP set a port pointer to node X.
- JCON `suspend ir_chunk(p.child.ir.success,[ir_Goto(p.other.ir.start)])` → SCRIP `child->γ = other` (synthesized α of `other` wired into inherited γ of `child`).
- JCON named temp (`closure`,`fv`,`tv`) → SCRIP child node's `value` field, read UP after the child runs.
- Generator backtracking (`by.failure→to.resume`, `to.failure→from.resume`) → SCRIP ω ports chaining back to predecessor β ports.

The 43 `ir_a_<Construct>` procedures map ~1:1 onto SCRIP BB kinds. For each H-3/H-4 kind:
READ its `ir_a_` proc, transliterate the 4-label wiring into 4-pointer wiring. JCON has already
solved door/resume/eval-order; we copy the topology, not the text.
Reference extracted to: `/home/claude/jcon-extract/jcon-master/tran/{ir,irgen}.icn`.

### Why one pointer per port suffices (the door question — resolved)
A pointer names the BOX, not the door. The door (fresh vs retry) lives in the **target node's
`state`** field, stamped by the transferer immediately before control passes (`X->state=0; goto X`
= fresh; `X->state=1` = resume). This is ALREADY the house style in bb_exec.c (171 `->state`
uses; lines 314-315 stamp `nd->α->state=0; nd->β->state=0` before entry). The trampoline returns
the next BB_t* and the top loop dispatches on `->t`. No code-address label is needed because we
never jmp to code in modes 2/3 — we hand a struct to a switch.

### Why no c[]/n/lhs/rhs/operand needed
An operand IS just another box, wired into the parent's α or β, whose result is read back UP from
that box's `value` field after it runs. Multi-operand constructs decompose into a **γ-chain** of
operand boxes (NOT child arrays). Sibling sequencing: `prev.γ ← this.α` (synthesized α bubbles up,
wired into the predecessor's inherited γ slot). N-ary (CALL args, IDX_SET/SECTION 3-operand) →
γ-chain, never packed into the 2 operand ports.

#### H-1 — Extend lowerer signature to the 4-attribute form ⏳
- [ ] `lower_icn_expr_node(cfg, e)` → `lower_icn_expr_node(cfg, e, BB_t *γ, BB_t *ω, BB_t **α_out, BB_t **β_out)`.
- [ ] Leaf nodes (LIT_I/F/S, VAR, KEYWORD): set `*α_out = *β_out = nd; nd->γ = γ; nd->ω = ω;`.
- [ ] `lower_icn_expr_top` / `lower_icn_proc_body` seed the top γ/ω (program success / program fail sentinels).
- [ ] Gate: clean build (signature compiles), no behaviour change yet on leaves.

#### H-2 — Replace BB_SEQ child-array with γ-chain ⏳
**SPEC (from JCON ir_a_Compound, irgen.icn:1231 — consulted 2026-05-26):**
- `seq.α → stmt[0]` (entry); or set `cfg->entry = stmt[0]` and drop the SEQ head node.
- Middle statements i (0..n-2): wire **BOTH** `stmt[i].γ = stmt[i+1]` **AND** `stmt[i].ω = stmt[i+1]`.
  ⚠ Icon semantic: a statement that FAILS still advances to the next statement (failure is not
  fatal in a compound). Both ports point forward. Do NOT wire ω to the body failure.
- Last statement: `stmt[n-1].γ = γ_in`, `stmt[n-1].ω = ω_in` (inherit body's continuation).
- ⚠ `FRAME.returning` early-out (current bb_exec.c:232): NOT part of sequence wiring in JCON —
  `return` is its own control construct (ir_a_Return). The γ-chain handles normal fall-through;
  `return` short-circuits via its own ω/γ to the proc exit. Verify return path before deleting the loop.
- [ ] `lower_icn_proc_body` line 920-923 (`seq->c=stmt_nodes; seq->n=built;`) → γ/ω-chain per above.
- [ ] bb_exec.c BB_SEQ case (226): walk via ports, not `nd->c[i]`; reconcile FRAME.returning.
- [ ] Gate: smoke 5/5 (proc bodies execute via chain).

#### H-3 — Port-wire 2-operand kinds via α/β + thread γ/ω ⏳
**PROOF LANDED (2026-05-26): BB_TO_BY transliterated from JCON ir_a_ToBy.** lower_icn.c TT_TO_BY
wires lo→α, hi→β (operand boxes), step→ival, sval="i"/"r". bb_exec.c BB_TO_BY reads operands UP
from α->value/β->value, walks counter, yields via γ, exhaustion→ω; door in `state`. Both regions
verified free of c[]/n/ival2/ival3. Standalone trampoline harness (/tmp/ag_proof.c) confirms:
`2 to 7 by 2`→2 4 6 ✓; `5 to 1 by -1`→5 4 3 2 1 ✓. AG design proven on a real four-port generator.
NOTE: full build still blocked by remaining ~328 c[]/n hits in bb_exec.c (other kinds) — H-1/H-2 first.
- [ ] In lower_icn.c, each binary kind: lower lhs with (γ=rhs.α, ω=node.ω, &node.α, …); lower rhs; wire node.α/β. Operand results read from `node->α->value` / `node->β->value`.
- [ ] bb_exec.c: replace surviving `nd->c[0]`/`nd->c[1]` (lines 97,122,130,133,…) with `nd->α->value`/`nd->β->value`.
- [ ] Gate: clean build, smoke 5/5, broker ≥17.

#### H-4 — N-ary kinds (CALL, IDX_SET, SECTION) via γ-chain ⏳
- [ ] CALL args (bb_exec.c line 170 `nd->c[j]`): build γ-chain of arg-eval boxes; arity → `nd->ival`.
- [ ] IDX_SET / SECTION (3 operands): γ-chain of 3 operand boxes feeding the operator node.
- [ ] Gate: clean build, smoke 5/5, broker ≥17, rungs ≥153.

#### H-5 — Sweep remaining bb_exec.c c[]/n; build green ⏳
- [ ] After H-1..H-4: `grep -n 'nd->c\[\|nd->n\b\|e->c\[\|e->n\b\|gen->c\[' src/lower/bb_exec.c` empty (cfg->n stays — legit BB_graph_t).
- [ ] Gate: clean build, smoke 5/5, broker ≥17, rungs ≥153. This closes G-1.

#### G-2 — Delete rt_binop_gen (dead C Byrd box) ⏳
- [ ] `src/runtime/interp/icon_box_rt.c` + `.h`: remove `rt_binop_gen(BB_t *nd, int entry)`. It is a C Byrd box (forbidden). Executor path is `bb_exec.c`.
- [ ] `src/emitter/BB_templates/bb_binop_gen.cpp`: remove `call rt_binop_gen@PLT`; emit inline x86 reading `pBB->lhs` / `pBB->rhs`.
- [ ] `icn_every_box`: verify callers — if only dead paths, delete too.
- [ ] Gate: smoke 5/5, broker ≥17.

#### G-3 — Migrate unary BB kinds → operand field ⏳
⛔ **SUPERSEDED by Phase H (2026-05-26).** BB.h FORBIDS `operand`/`lhs`/`rhs`. Do NOT add them.
Unary kinds get their operand wired into the **α port** (operand box); result read UP from `α->value`.
Per-kind wiring spec = the matching `ir_a_<Construct>` in irgen.icn. Kinds below still need migrating
(into ports, not fields): `BB_SIZE`, `BB_NOT`, `BB_NONNULL`, `BB_NULL_TEST`, `BB_RANDOM`, `BB_NEG`,
`BB_POS`, `BB_CSET_COMPL`, `BB_CALL` (inner expr), `BB_RETURN`, `BB_REPEAT`, `BB_INITIAL`, `BB_KEY_GEN`.
- [ ] Migrate all via α-port (builder + executor per kind). See H-3.

#### G-4 — Migrate binary BB kinds → lhs/rhs fields ⏳
⛔ **SUPERSEDED by Phase H (2026-05-26).** No `lhs`/`rhs` fields — wire operands into **α/β ports**
(2-operand) or **γ-chains** (3+ operands, e.g. IDX_SET/SECTION). Read results UP from `α->value`/
`β->value`. BB_IF: cond→α, then→γ, else→ω. Kinds still to migrate (into ports): `BB_ASSIGN`, `BB_SWAP`,
`BB_IDENTICAL`, `BB_IDX`, `BB_FIELD_GET/SET`, `BB_CSET_UNION/DIFF/INTER`, `BB_GEN_SCAN`, `BB_LIMIT`,
`BB_EVERY`, `BB_WHILE`, `BB_UNTIL`, `BB_BINOP` (incl. TT_AUGOP path), `BB_IF`, `BB_IDX_SET`, `BB_SECTION`.
- [ ] Migrate all via α/β + γ-chain. Per-kind spec = irgen.icn `ir_a_*`. See H-3/H-4.
- [ ] Gate: smoke 5/5, **rungs PASS≥169** (regression from F-6d augop recovers here).

#### G-5 — Migrate Prolog BB kinds ⏳
- [ ] `BB_PL_SEQ`: wire as γ-chain. `nd->operand = first_stmt`; each stmt `.γ → next`.
- [ ] `BB_PL_CALL` with args: γ-sequence of arg nodes; `nd->lhs = first_arg`, `nd->sval = name`, `nd->ival2 = arity`.
- [ ] `BB_CHOICE`: ω-chain. `blk[i].ω → blk[i+1].α`; `nd->operand = first_clause_bb`. Replace `nd->c[nd->n++] = blk`.
- [ ] Verify `BB_UNIFY` clause-head already migrated (F-6d); fix if not.
- [ ] Gate: broker PASS≥17.

#### G-6 — Migrate emitter files ⏳
- [ ] `src/emitter/emit_bb.c`: `nd->c[0]` → `nd->operand`; `nd->c[i]` loops → γ-chain walk (BB_PAT_ARBNO, BB_PAT_ASSIGN_IMM/COND, pre_build_children).
- [ ] `src/emitter/emit_sm.c`: `nd->c[k]` in BB_CHOICE/PL_SEQ serialiser → γ-chain walk.
- [ ] `src/emitter/BB_templates/bb_builtin.cpp`: `pBB->c[0]` → `pBB->operand`.
- [ ] `src/emitter/emit_core.c`: `bb_walk_rec` `nd->c[i]` → walk lhs/rhs/operand/γ/ω.
- [ ] Gate: smoke 5/5, broker ≥17, rungs ≥169.

#### G-7 — Verify zero c[]/n references; finalize ⏳
⚠ **CORRECTION (2026-05-26): `c` and `n` are ALREADY GONE from `struct BB_t`** (removed in
`e099fdae`; that is WHY the build is broken). There is nothing to delete from the struct or from
`BB_node_alloc` (no `c`/`n` init exists). G-7's only remaining task is verifying zero REFERENCES
remain after Phase H migrates them. Reference ledger as of `72a30688`: bb_exec.c ~312, emit_bb.c 27,
emit_sm.c 20, lower_icn.c 4 (2 = the H-2 seq->c/seq->n), lower_pl.c 4. emit_core.c/scrip_ir.c clean.
Verify zero remaining offences:
```bash
grep -rnE "(nd|pBB|gen|seq|binop|asgn|e)->(c\[|n\b)" \
  src/lower/bb_exec.c src/lower/lower_icn.c src/lower/lower_pl.c \
  src/emitter/emit_bb.c src/emitter/emit_sm.c src/emitter/emit_core.c \
  src/emitter/BB_templates/ src/runtime/interp/icon_box_rt.c src/lower/scrip_ir.c
# Must be empty (cfg->n / graph->n on BB_graph_t are legit and excluded)
```
- [ ] Confirm grep empty after H-1..H-6 + G-6 (emitter).
- [ ] Remove DEPRECATED comments from G-1.
- [ ] Gate: clean build, smoke 5/5, broker ≥17, rungs ≥169.

#### G-8 — Fix scrip_ir.c debug printer ⏳
- [ ] `src/lower/scrip_ir.c` ~line 130: prints `nd->c[j]`. Replace with lhs/rhs/operand/γ/ω walk or stub.

**Phase G done when:** `BB_t` has no `c`/`n`, zero `nd->c[` in the files above, smoke 5/5, broker ≥17, rungs ≥169.

---

---

## Honest-mode-3 protocol

Probe helpers in `scripts/icon_bb_probes.sh`: `bb_probe_detect`, `bb_probe_complete`, `bb_probe_scoreboard`.
Baseline md5: `baselines/icon-bb/sm-run-honest.md5` (created sess 2026-05-11c).

A rung is **honestly complete** iff: (a) output matches `--interp`, (b) passes under `SCRIP_NO_AST_WALK=1`, (c) audit counter zero for kind, (d) smokes unchanged, (e) ≥1 program flipped honest.

---

## Phase A — drain legacy fallthrough

`lower_bang_binary` and generative `lower_lconcat` emit `SM_BB_PUMP_AST` (bridges to `coro_eval` via `g_ast_pump_active` exemption — not caught by `SCRIP_EXPRS_AUDIT`). Phase A replaces each with a pure SM coroutine using the `emit_range_coroutine` pattern: `SM_JUMP` over body → `SM_RESUME` → loop with `SM_STORE/LOAD_GLOCAL` + `SM_SUSPEND` → `SM_PUSH_NULL + SM_RETURN` → `SM_PUSH_EXPRESSION + SM_BB_PUMP_SM`.

#### A1 — CH-17i-bang-concat-gen — `AST_BANG_BINARY` + `AST_LCONCAT` (generative)
- [ ] JCON: `ir_a_Binop` with closure / `ir_a_Unop`. Reuse `icn_bang_binary_state_t` / `icn_binop_gen_state_t`.
- [ ] Anchor: `rung15_real_swap_lconcat.icn`. Gate: smoke ×6, isolation PASS, anchor flips honest.
- [ ] Files: `sm_prog.h/c`, `sm_interp.h/c`, `sm_codegen.c`, `lower.c`

#### A2 — CH-17i-section — `AST_SECTION*`
- [ ] JCON: `ir_a_Sectionop`. State: `icn_section_state_t { subj, lo, hi, kind }`. Gate: standard + anchor honest.

#### A3 — CH-17i-limit-random — `AST_LIMIT` + `AST_RANDOM`
- [x] JCON: `ir_a_Limitation`. Gate: standard + anchor. (rung14 TT_LIMIT ✅ `554aa38f`)

#### A4 — CH-17i-iterate — `AST_ITERATE` (`!E`)
- [x] JCON: `ir_a_Unop` with closure. lower_iterate→SM_EXEC_BB via lower_icn_expr_top. SM_BB_EVAL eradicated. one4all `7af3551d`.

#### A5 — CH-17i-seqexpr-gen — `AST_SEQ_EXPR` (generative `;`-parens)
- [ ] JCON: `ir_conjunction`. Gate: standard + anchor.

#### A6 — CH-17i-fallthrough-delete
- [ ] After A1–A5: delete legacy block, replace with `abort()`. Gate: zero `SM_PUSH_EXPR` fires corpus-wide.

---

## Phase B — generative reductions

Scalar ops become generators when `is_suspendable(child)`. Extend scalar arms in `lower.c`; use existing `SM_SUSPEND_VALUE` + goto wiring.

- [ ] **B1** arith-gen — `AST_ADD/SUB/MUL/DIV/MOD/…` gen children.
- [ ] **B2** rel-gen — relops gen children.
- [ ] **B3** cat-gen — `AST_CAT`/`AST_LCONCAT` mixed.
- [ ] **B4** deref-gen — `AST_NONNULL`/`AST_NULL`/`AST_IDENTICAL` gen.
- [ ] **B5** idx-gen — `AST_IDX` gen index.
- [ ] **B6** assign-gen — `AST_ASSIGN` gen RHS + `AST_REVASSIGN`/`AST_REVSWAP`.

---

## Phase C — control-flow generator-awareness

- [ ] **C1** fnc-gen — `AST_FNC` gen arg / user proc with `suspend`.
- [ ] **C2** loop-cond-gen — `while/until/repeat` gen condition.
- [ ] **C3** if-gen — `AST_IF` gen condition (Proebsting §4.5).
- [ ] **C4** not-gen — `AST_NOT` gen subexpr.

---

## Phase D/E (owned by CHUNKS-STEP17)

CH-17g-irrun-prep → CH-17g-irrun-execution → mode3-completeness / mode4 / final-isolation. All after Phase C.

---

## Phase F — SM_BB_SWITCH: entire Icon program as composed Byrd boxes

**Architecture:** The SM is a 2-3 instruction bootstrap. Every Icon construct is a `bb_node_t { bb_box_fn fn; void *ζ }`. Boxes wire γ/ω directly to each other in C — SM never re-enters after `SM_BB_SWITCH`. `BB_graph_t` / `BB_t` / `bb_exec_node` are the OLD path and will be deleted as Phase F progresses.

**CONSULT irgen.icn before each rung.** `bb_node_t` = Byrd box. `icn_list_bang` is the model.

#### F-1 — bb_node_t for `!E` ✅ `a3505d4c`
- [x] `icn_list_bang(void *ζ, int entry)` — α pops collection from vstack, β advances counter. `lower_iterate` emits child expr + `SM_BB_SWITCH(node)`.

#### F-2 — bb_node_t for `every E do B`
- [ ] JCON: `ir_a_Every`. Box: α fires generator E (inner `bb_node_t`); on γ fires body B; on ω from E → whole every ω. β re-enters E at β. ζ holds inner box + body box.
- [ ] `lower_every` emits `SM_BB_SWITCH` into `icn_every_box`.

#### F-3 — bb_node_t for `E1 | E2` alternation
- [ ] JCON: `ir_a_Binop` alt. Box: α tries E1; on ω tries E2; β resumes last active arm. ζ holds left/right boxes + phase.
- [ ] `lower_alternate` → `icn_alt_box`.

#### F-4 — bb_node_t for `lo to hi` / `lo to hi by step`
- [ ] `icn_to_by_rt` already exists as a Byrd box fn. Wire `lower_to` / `lower_to_by` to `SM_BB_SWITCH` with `icn_to_by_rt_make` ζ. Delete `BB_TO` / `BB_TO_BY` graph nodes.

#### F-5 — bb_node_t for proc body (replace `lower_icn_proc_body` / `BB_graph_t`)
- [ ] Each Icon proc becomes one `bb_node_t`. ζ holds param slots + array of statement boxes. α sequences statements; body-falls-off → ω. Replace SM sequence emission in `lower_proc_skeletons` with single `SM_BB_SWITCH`.

#### F-6 — Make BB_t pure: remove `n`, `c`, `value`, `counter`, `state`, `opaque`

**Goal:** `BB_t` has ONLY: `t` (kind), `α β γ ω` (port pointers), `sval`/`ival`/`sval2`/`ival2`/`ival3` (compile-time data). No runtime state, no child arrays. The emitter DFS follows ports; `bb_exec_node` / `bb_exec.c` deleted.

Files using `nd->c` / `nd->n` today (must all be migrated first):
- `lower/bb_exec.c` (302 uses) — entire file deleted in F-6g
- `lower/lower_icn.c` (307 uses) — migrated to port wiring in F-6a..F-6e
- `lower/lower.c` (202 uses) — tree_t `->c`/`->n`, NOT BB_t — unaffected
- `emitter/emit_bb.c` (33 uses) — migrated to DFS port walker in F-6f
- `emitter/BB_templates/bb_*.cpp` — each migrated when its kind is ported
- `runtime/interp/icon_box_rt.c` (34 uses) — shims deleted after F-6g

#### F-6a — port-wire `BB_LIST_BANG` (replace `c[0]` child with α port to evaluator node)
- [x] `lower_icn.c` TT_ITERATE: build two nodes — BB_EVAL_CHILD (α→evaluator) + BB_LIST_BANG. Wire α/β/γ/ω. No `c[]`.

#### F-6b — port-wire `BB_TO` / `BB_TO_BY` (replace `c[0..2]` with bound data in sval/ival)
- [x] `lower_icn.c` TT_TO / TT_TO_BY: store bounds in `ival`/`dval`/`ival2`/`ival3`. No `c[]`.
- [x] `bb_to_by.cpp` template: read from `pBB->ival*` not `pBB->c[*]`.

#### F-6c — port-wire `BB_ALT` / `BB_ALTERNATE` (replace `c[0..n]` with α/β chains)
- [x] Each alt arm is a BB_t node. Wire: BB_ALT.α→arm0.α; arm0.ω→arm1.α; armN.ω→BB_ALT.ω.

#### F-6d — port-wire `BB_BINOP_GEN`, `BB_ARITH`, `BB_UNIFY` (replace `c[0..1]`)
- [ ] Operand nodes wired via α/β ports. `bb_arith.cpp`, `bb_unify.cpp` read ports not children.

#### F-6e — port-wire all remaining BB kinds in `lower_icn.c`
- [ ] BB_CALL, BB_SEQ, BB_SEQ_EXPR, BB_PROC_GEN, BB_LIMIT, BB_KEY_GEN, BB_FIND_GEN etc.

#### F-6f — replace `emit_bb.c` `walk_bb_flat` with DFS port walker
- [ ] Emitter follows `α/β/γ/ω` pointers depth-first. `walk_bb_flat(pBB->c[i]…)` → `walk_bb_port(pBB->α…)` etc.

#### F-6g — delete `bb_exec.c`, `bb_exec_node`, `bb_exec_once`, `bb_exec_resume`
- [ ] All 302 uses gone after F-6a..F-6f. Delete file. Delete `BB_graph_t` traversal machinery.
- [ ] Remove `n`, `c`, `value`, `counter`, `state`, `opaque` from `BB_t` struct.
- [ ] Delete `icn_list_bang` / `icn_every_bb_state_t` interpreter shims (replaced by emitter).
- [ ] Once F-1..F-5 land: `lower_icn_proc_body`, `lower_icn_expr_top`, `lower_icn_expr_node` deleted. `BB_graph_t` no longer built for Icon. `bb_exec_node` Icon cases removed.

---

## Active next targets (2026-05-26, `72a30688`) — Phase H (Attribute Grammar). H-3 proof landed; H-1/H-2 next.

Sess 2026-05-26 (Opus): design question RESOLVED — pointers, no label IR. Four-attribute grammar:
γ/ω inherited (down), α/β synthesized (up). Door ambiguity solved via target node's `state` (house
style, already in bb_exec.c). JCON irgen.icn is per-construct wiring spec (label↔pointer table in
Phase H), NOT a mechanical graft. H-3 PROOF: BB_TO_BY transliterated from ir_a_ToBy, harness-verified.
⛔ BUILD BROKEN: ~328 c[]/n hits remain in bb_exec.c. NEXT: H-1 (lowerer 4-attr sig, ~120 sites) +
H-2 (BB_SEQ γ-chain @ lower_icn.c:917, the literal first build break).

Sess 2026-05-26b (Opus, checkpoint — BUILD STILL BROKEN, emergency handoff): H-2 + partial H-4
landed in lower + exec for the program-spine kinds. DONE: (1) `ir_is_single_shot` classifier
walks α/β + γ-chains, no c[]/n. (2) BB_SEQ — lower_icn_proc_body now γ/ω-chains statements off
α (both γ and ω point forward per Icon compound semantics, JCON ir_a_Compound); executor walks
α→γ. seq->ival = stmt count. (3) BB_SEQ_EXPR — statement γ-chain moved from nd->γ to nd->α
(γ stays the node's own success continuation); executor finds tail by walking α→γ, head-once/
pump-tail state machine preserved. (4) BB_CALL — args now a γ-chain off α (was: only first 2
args into α/β, args 3+ DROPPED — that was a real bug); executor walks α→γ for nd->ival args;
opaque→counter (intptr cast) for the generator-state cache. (5) BB_ASSIGN, BB_SWAP execs read
α/β. bb_exec.c c[]/n: 229→187 c[], 57 n. STILL TODO (next session, all in bb_exec.c): generator
executors using opaque(32)/ival2(18)/ival3(3)/sval2(2) — NOT mechanical: several pack multiple
removed fields live simultaneously (opaque+counter+ival2), so the goal-file "opaque→counter"
map COLLIDES there; needs per-node state-packing decision. First remaining error: bb_exec.c:405
(ival3, BB_INITIAL has-run flag → map to state). Then BB_IF/BB_CASE/BB_IDX/BB_SECTION/
BB_FIELD_*/BB_LIMIT/BB_NOT/BB_SIZE/BB_REPEAT/BB_RETURN c[] reads → α/β/γ per lower_icn.c wiring
(lowerer already wires these to ports — verify each). emit_bb.c(20)/emit_sm.c(17) untouched.
NO GATES RUN (build red). one4all working tree dirty — committed as WIP.


Sess 2026-05-11h (Claude Sonnet 4.6): rung14 limit-in-generator ✅ `554aa38f`:
lower_limit_every: two SM gen slots (slot_inner=alternate coroutine, slot_limit=limit wrapper).
GLOCAL[0] holds remaining count. Outer SM_GEN_TICK drives limit coroutine; limit coroutine
drives inner alternate via nested SM_GEN_TICK, counting down from N, suspending each value.
SM_DECR 1 decrements; separate VOID_POP cleanup for FAILDESCR (done_inner) and yielded_val (done_ctr).
lower_every detects gen_expr->t == TT_LIMIT and delegates. Honest SM: 212→213.

Remaining failures — known root causes:
- Rungs regression 169→153: F-6d augop path, recovers at G-4e.
- rung15: `!E` iterate — Phase A4 AST_ITERATE.
- rung36: complex Icon features (segfaults, timeouts).
- Some IR failures: interp_eval.c slot reads still use v.ival.

---

## Invariants

1. Mode 1 (`--ir-emit`) byte-identical at every rung.
2. Icon `--interp` corpus 185/48/30 byte-identical until CH-17g-irrun-execution lands.
3. No `EXPR_t*` in SM bytecode — BB-pump opcodes take integer registry IDs.
4. Fallthrough delete (A6) is one-way: future generative kinds must add their own lowering.
5. `is_suspendable` stays in sync with lowering rungs.

---

## Closed rungs

| Rung | Commit | Honest gain | Notes |
|------|--------|-------------|-------|
| A0 — cheat-tripwire | — | — | `SCRIP_NO_AST_WALK=1` guard in `coro_eval`/`interp_eval`/etc. |
| A3-seed-fix | — | 116→117 | Unified 3 LCG seeds → `bb_icn_rnd_seed` |
| A4 — alternate | — | 117→122 | `AST_ALTERNATE` → `SM_BB_PUMP_AST` |
| CH-17g-smcall-proc | `60656fce` | 126→130 | `SM_CALL_FN` scans `proc_table` before NV dispatch |
| CH-17g-augop-inline | `bb6d4ee7` | 130→140 | `AST_AUGOP` inline read-compute-writeback |
| CH-17g-loop-stack | `864fe914` | 140→143 | `SM_VOID_POP` before `SM_PUSH_NULL` at while/until exit |
| CH-17g-scan | `d8760856` | 143→152 | `AST_CSET`→string; `AST_SCAN`→`ICN_SCAN_PUSH/POP` |
| CH-17g-builtin-batch | `c95eb2bd` | 141→167 | SIZE/NONNULL/NULL/FIELD_GET/SET/MAKELIST/RECORD_MAKE/etc. |
| CH-17g-case-swap-null | `7adfdc20` | 167→174 | `AST_CASE`; `AST_SWAP`; `AST_NULL` |
| AST_IF condition leak | `2f3dbc65` | 174→177 | `SM_VOID_POP` after `SM_JUMP_F` |
| CH-17g-scan-subject | `5f6d9d8b` | 180→185 | `NV_GET/SET_fn` for `&subject`/`&pos` |
| CH-17g-icon-conjunction | `74faf1d0` | — | `AST_SEQ` + `LANG_ICN` → `SM_JUMP_F` |
| CH-17g-initial-once | `b4d7ee18` | 172→175 | `initial {}` sentinel via NV |
| rung24 record-field-assign | `bc6357da` | 203→205 | AST_FIELD lvalue in interp_eval + icn_bb_assign_gen |
| loop_next fix | `cf389ad7` | 205→224 | `coro_bb_every`: save/clear/restore `FRAME.loop_next` around body |
| assign-cat fix | `f32e690e` | 224→226 | `icn_bb_assign_cat`: re-eval RHS each tick when AST_VAR alongside leaf gen |
| rung06 scan/any fix | `4b2a8700` | 226→227 | ICN_SCAN_PUSH/POP inline in sm_interp; Icon & conjunction SM_JUMP_F in lower_proc_skeletons |
| g_lang LANG_ICN scoped | `3648dae5` | 227→~231 | SM_BB_PUMP_PROC saves/restores g_lang; sm_preamble sets after lower(); rung28+rung24 gain |
| SI-13 union-clobber fix | `b891504a` | 0→209 honest, 1→182 IR | Four v.sval/v.ival alias bugs: nparams→_id; callee skip; slot→_id; baseline rebake |
| rung13 conjunction-in-generator | `fa8bd48f` | 208→211 honest | SM_GEN_TICK + bb_broker_drive_sm_one + IcnFrame.every_gen[]; lower_every hoists TT_ALTERNATE as inner SM coroutine; outer SM_GEN_TICK loop |
| rung14 limit-in-generator | `554aa38f` | 212→213 honest | lower_limit_every: slot_inner (TT_ALTERNATE coro) + slot_limit (limit wrapper); GLOCAL[0]=count; nested SM_GEN_TICK; SM_DECR 1; stack cleanup at each exit |

---

## File ownership

| Path | Touches? |
|------|----------|
| `src/runtime/x86/lower.c` | Yes (every rung) |
| `src/runtime/x86/sm_prog.h/c` | Yes (Phase A) |
| `src/runtime/x86/sm_interp.h/c` | Yes (Phase A) |
| `src/runtime/x86/sm_codegen.c` | Yes (Phase A JIT mirrors) |
| `src/runtime/interp/coro_runtime.c` | Fixes |
| `src/runtime/interp/interp_eval.c` | Builtin additions |
| `baselines/icon-bb/` | Baseline md5 files |
