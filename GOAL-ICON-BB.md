# GOAL-ICON-BB.md — All Icon Byrd-Box constructs in modes 1/2/3 (then 4)

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔⛔⛔  THE FOUR FACTS — Lon has said these for 2 months. They are ALL THE SAME RULE.  READ FIRST. ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  Every session re-derives these. STOP. They are stated here so you do not have to re-learn them: ║
║                                                                                                  ║
║  FACT 1 — C WALKERS LIVE IN MODE 2 ONLY.                                                         ║
║    Mode 2 (--interp, SM dispatch) is the reference path; C four-port walkers are PERMITTED here. ║
║    icn_bb_dcg / pl_bb_dcg / bb_exec_once / bb_exec_resume / bb_exec.c belong to MODE 2.          ║
║                                                                                                  ║
║  FACT 2 — NO C WALKERS IN MODE 3 OR MODE 4.  PERIOD.  NONE.                                      ║
║    Mode 3 (--run, in-process JIT) and Mode 4 (--compile) run ONLY self-contained emitted x86.   ║
║    Zero calls to icn_bb_dcg / pl_bb_dcg / bb_exec_once / bb_exec_resume reachable from --run or  ║
║    --compile. Those symbols stay DEFINED (Mode 2 needs them) but become UNREACHABLE from 3/4.    ║
║                                                                                                  ║
║  FACT 3 — IN MODE 3 / MODE 4 THE SM AND BB STRUCTURES DO NOT EXIST AT RUN TIME.                  ║
║    They exist ONLY at emit time. The emitter reads them ONCE and lays down flat-wired x86 with   ║
║    relocations baked into the BYTES (never graph pointers). scrip.c frees the SM + BB tables     ║
║    (stage2_free_bb_after_emit + stage2_free_sm_bb) BEFORE the runner executes; the runner gets   ║
║    NULL. At run time there is no SM array, no bb_table, no BB_graph_t — nothing to dereference.  ║
║    ⛔ Keeping a structure alive past the free (e.g. PJ-AGW-1c's \"skip freeing Prolog BB graphs\")  ║
║       is FORBIDDEN and was REVERTED (upstream 1af97d90). Do not re-attempt it for any language.  ║
║                                                                                                  ║
║  FACT 4 — BOTH SM AND BB ARE x86 ASM FROM THE SHARED TEMPLATE EMITTER.  ONE SOURCE, TWO CONSUMERS.║
║    The shared emitter (src/emitter/ + BB_templates/*.cpp, SM_templates/, XA_templates/) is the   ║
║    SINGLE source of x86 truth. Mode 4 writes its bytes to a binary run as a separate process;    ║
║    Mode 3 loads the SAME bytes into a PROT_EXEC buffer and calls into them in-process. They      ║
║    differ ONLY in the process boundary. A second x86 producer (e.g. replicating templates in     ║
║    the JIT's sl_* byte-emitters) is FORBIDDEN — two copies drift.                                ║
║                                                                                                  ║
║  WHY THEY ARE ONE RULE: a C walker would need the freed structures to walk (FACT 3 ⇒ FACT 2),    ║
║  and the only thing that can exist at run time in mode 3/4 is the blob + fixed PLT symbols        ║
║  (subscript_get, rt_push_*, GC_malloc, …). Run time = self-contained x86 blob + PLT. Nothing else.║
║                                                                                                  ║
║  COMPLETION TEST (verifiable, not a vibe): from any Mode-3 (--run) or Mode-4 (--compile) entry   ║
║  point, reachability to icn_bb_dcg / pl_bb_dcg / bb_exec_once / bb_exec_resume == ZERO.           ║
║                                                                                                  ║
║  CURRENT ICON VIOLATION (the exact edge to cut for Phase J):                                     ║
║    sm_jit_interp.c:2072  sl_call(rt_bb_pump_proc)             ← bakes call into mode-3 blob      ║
║    sm_jit_interp.c:1648  bake_blob_call_si(rt_bb_pump_proc..) ← same, with args                  ║
║    rt_bb_pump_proc (sm_jit_interp.c:233, JIT-local) → icn_bb_pump_proc_by_name →                 ║
║      bb_node_t{.fn=icn_bb_dcg} → bb_exec_once/resume  = the C walker. SEVER these two bake sites; ║
║      replace with the shared emitter's flat-wired BB x86 (the same x86 Mode 4 already emits).    ║
║    Symptom today: --run hello.icn → 'sm_eval_subexpr: invalid entry_pc 1' because the baked call ║
║      reads bb_table AFTER it is freed (FACT 3) → NULL → oneshot → invalid pc. --interp prints OK.║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

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
⚠ **PARTIAL (2026-05-26f + 2026-05-26k).** Sess 2026-05-26k (Opus 4.7, with Lon) landed the
attribute-grammar FOUNDATION (`45c1bde2`): added `lower_icn_expr_threaded(cfg, e, γ_in, ω_in,
&α_out, &β_out)` — the 4-attribute signature (γ/ω inherited down, α/β synthesized up). It is ADDITIVE:
it does NOT rewrite the 70 internal `lower_icn_expr_node` call sites (those still build operand
sub-graphs the old way); instead it builds the node via the existing recursive builder then STAMPS
the inherited γ/ω onto the synthesized node (filling only ports the builder left NULL), and reports
α/β up. `lower_icn_proc_body` now builds the statement spine BACK-TO-FRONT through the worker so each
statement is born with its success/failure continuation threaded (JCON ir_a_Compound: a failed stmt
still advances → both γ and ω point forward). This REPLACES the old after-the-fact γ/ω patch loop +
its BB_IF special case. Guard `icn_kind_owns_omega_operand()` prevents the worker stamping ω on kinds
that use ω as a compile-time operand (currently only BB_IF). ⚠ As H-3/H-4 migrate more operand-bearing
kinds, AUDIT whether any new kind uses ω (or γ) as an operand before the worker stamps it.
This exposed + fixed a latent γ-conflation in BB_IDX_SET/BB_SECTION (see H-4 — done this session).
rungs 189→195 (+6), smoke 5/5, broker 19, zero regressions.
The prior 2026-05-26f fixes (BB_node_alloc α/β→NULL; BB_IF else→ω) remain in place.
STILL TODO (the real remaining H-1 work): full inherited-γ/ω threading for NESTED non-leaf IF
(if-as-value: `x := if a then b else c` — then/else branches need their OWN inherited continuations,
which the additive stamp does not yet provide) and deep generator composition. That needs per-construct
threading inside the builders (passing γ/ω DOWN to recursively-lowered then/else/body), not just a
post-hoc stamp on the parent.
- [x] (2026-05-26k) `lower_icn_expr_threaded` 4-attribute signature added (additive wrapper form). `45c1bde2`.
- [x] (2026-05-26k) Leaf nodes already return `nd->γ`/`nd->ω` (executor was ready); worker stamps them. Verified leaves compose.
- [x] (2026-05-26k) `lower_icn_proc_body` seeds top γ/ω (NULL = trampoline-halt sentinel) + back-to-front spine threading.
- [x] (2026-05-26k) Gate: clean build, smoke 5/5, broker 19, rungs 189→195. No regressions.
- [ ] **REMAINING:** per-construct DOWN-threading of γ/ω into then/else/body for nested non-leaf IF + generator composition (push the full signature into the builders, not just stamp the parent).
- [x] (2026-05-26m) Conjunction `E1 & E2` split off BB_IF → own opcode BB_CONJ (generator: resume E1 across pumps, fail on E1 exhaustion). Fixes `every (gen) & body` infinite loop. rungs 195→196, smoke 5/5, broker 23, zero regress. (Part of generator-composition; BB_CONJ mode-3/4 emitter template still TODO.)
- [x] (2026-05-26f) BB_node_alloc α/β default NULL not self; BB_IF else→ω statement-context wiring. Gates green.

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
- [x] CALL args γ-chain: general call (lower_icn.c:333) + **MAKELIST (`82ec79f8`, 2026-05-26i)** build `args[0]→α`, `args[j]->γ=args[j+1]`; arity→`nd->ival`. Executor walks α→γ→γ for nd->ival args (bb_exec.c:166-178). MAKELIST had been α/β-only → `[1,2,3]` built empty list; fix recovered rungs 181→189 (all rung22 lists). BB_SEQ_GEN (≤2 args) + BB_FIND_GEN (positional α/β/γ) correct as-is.
- [x] **IDX_SET / SECTION (3 operands)** ✅ `45c1bde2` (2026-05-26k) — both packed their 3rd operand onto the γ port (BB_IDX_SET: base→α, idx→β, rhs→γ; BB_SECTION: base→α, i1→β, i2→γ). γ is the success-continuation port; the old SEQ patch loop only worked because it OVERWROTE γ after building (clobbering the operand). H-1 threading exposed the conflation — `t[k]:=v` followed by any statement dead-ended. FIX: 3rd operand moved onto the β node's γ-chain (`idx->γ=rhs` / `i1->γ=i2`), freeing each node's own γ for the inherited continuation. Executors read the operand from `nd->β->γ` and return `nd->γ`. Recovered the regression + fixed the rung13/23/35 table/subscript-assign cluster (rungs 189→195).
- [ ] Gate: clean build, smoke 5/5, broker ≥17, rungs ≥153.

#### H-5 — Sweep remaining bb_exec.c c[]/n; build green ⏳
- [ ] After H-1..H-4: `grep -n 'nd->c\[\|nd->n\b\|e->c\[\|e->n\b\|gen->c\[' src/lower/bb_exec.c` empty (cfg->n stays — legit BB_graph_t).
- [ ] Gate: clean build, smoke 5/5, broker ≥17, rungs ≥153. This closes G-1.

#### G-2 — RT-DELETE ladder: eradicate every four-port C Byrd box from the Icon RT path ⏳

**Scope (Lon, 2026-05-26j):** Delete ONLY C functions implementing four-port (α/β/γ/ω) Byrd-box
logic — `DESCR_t foo(void *zeta|BB_t *nd, int entry)` with entry==0/1 dispatch + value/FAILDESCR
return. NOT in scope (these STAY): string-conversion / value-push / subscript RT helpers a template
calls (e.g. `subscript_get`, `rt_vstack_pop`, `rt_push_*`, `icn_binop_apply`). Exempt per RULES.md:
`icn_bb_dcg`, `icn_bb_oneshot` (infrastructure DCG driver/shim, not generators). Out of scope:
Prolog `pl_*_fn` / `pl_bb_dcg` (GOAL-PROLOG-BB), SNOBOL4 `bb_deferred_var` (SN4 goal).

Defined four-port C Byrd boxes in the Icon RT path (audit @ `82ec79f8`):
`icn_to_by_rt`, `rt_binop_gen`, `icn_list_bang`, `icn_every_box` (all in icon_box_rt.c).
Dead declarations to also scrub: `rt_alt` (extern in bb_alt.cpp, defined nowhere),
`icn_bb_{to_by,iterate,binop,alternate,limit,upto_subj,to_nested,cset_compl,every}` (icon_gen.h
decls, defined nowhere).

Do ONE function per step. Each step: confirm callers, delete def + decl, rewire emitter template
to inline x86 (or confirm kind unreachable), build, gate (smoke 5/5, broker ≥17, rungs ≥153), commit.

- [x] **G-2a — `rt_alt` (dead extern)** ✅ `f0f99035` — `rt_alt` defined NOWHERE (latent mode-4 link bug); BB_ALT interp path runs via bb_exec.c:589 ω-chain walk. Removed extern decl from bb_alt.cpp; TEXT+BINARY arms rewired to port-jump (α→γ, β→ω, mirror G-2c bb_binop_gen); inline-x86 n-ary gen flagged mode-4 TODO. Binary bin-table corrected (was 3-fixup on 2-jmp body). smoke 5/5 broker 19 rungs 189.
- [x] **G-2b — dead `icn_bb_*` decls** ✅ `f0f99035` — removed 8 never-defined decls from `icon_gen.h` (to_nested, upto_subj, to_by, iterate, binop, alternate, limit, cset_compl) + 4 matching dead `extern` lines from `emit_bb.c` (to_by/iterate/alternate/limit) + 4 dead `icon_to_{make,by_make,tick,by_tick}` decls from `icon_box_rt.h`. Pure decl scrub, no logic. smoke 5/5 broker 19 rungs 189. NOTE: emit_bb.c still carries ~36 other never-called `extern DESCR_t icn_bb_*` decls (lines ~20-98) — out of this step's scope; candidate for a future broader scrub.
- [x] **G-2c — `rt_binop_gen`** ✅ `7d43dc79` — deleted `rt_binop_gen(BB_t*,int)` + IS_GEN macro + icn_binop_apply extern from icon_box_rt.c/.h. bb_binop_gen.cpp TEXT+BINARY arms rewired to port-jump (α→γ, β→ω); inline-x86 cross-product gen flagged mode-4 TODO. smoke 5/5 broker 19 rungs 189. sym gone from binary.
- [x] **G-2d — `icn_every_box`** ✅ `1101884f` — was an ORPHAN (no callers; F-2 SM_BB_SWITCH approach superseded by bb_exec.c BB_EVERY port path). Deleted fn + `icn_every_bb_state_t`; also fixed a misplaced `#endif` in icon_box_rt.h (struct sat outside the include guard). smoke 5/5 broker 19 rungs 189.
- [x] **G-2e — `icn_list_bang`** ✅ `3666025a` — deleted fn + `icn_list_bang_state_t` + snobol4.h include. `lower_iterate` (lower.c) was the LAST holdout still emitting SM_BB_SWITCH→C Byrd box; rewrote it to the sibling pattern (`lower_icn_expr_top` + `lower_unhandled`, matching lower_to/lower_to_by/lower_bang_binary) — `!E` now lowers via BB_LIST_BANG port path (lower_icn.c:935). smoke 5/5 broker 19 rungs 189 (bang rungs unaffected — BB path already carried them).
- [x] **G-2f — `icn_to_by_rt` (+ `_make`/`_make_real`)** ✅ `4da7a6b7` — deleted the four-port fn AND both state ctors (dead once the Byrd box went; nothing else used them). bb_to_by.cpp TEXT arm rewired to port-jump (was still calling icn_to_by_rt@PLT + _make despite H-3 "proof"). **icon_box_rt.c is now an EMPTY TU** (only #include + comment). `icn_to_by_rt_state_t` struct retained in header pending bb_to_by inline-x86 gen. smoke 5/5 broker 19 rungs 189. All 3 syms gone.
- [x] **G-2g — sweep + delete empty TU** ✅ `f0f99035` — grep for four-port `DESCR_t foo(void*|BB_t*,int entry)` in icon_box_rt.c empty (file deleted). Chose option (a): deleted the now-empty `icon_box_rt.c` + both Makefile lines (SRC list + compile recipe). `icon_box_rt.h` retained (`icn_to_by_rt_state_t` pending bb_to_by inline-x86 gen). Clean build, smoke 5/5, broker 19, rungs 189. **G-2 RT-DELETE ladder COMPLETE.**

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

## ⚡ Phase J — Mode 3 (`--run`) executes the SHARED emitter's flat-wired x86 (kill the JIT's C-walker bridge)

**Motto: we do things right the 10th time.** This phase is the right way, not the fast way.

### The defect (root-caused 2026-05-26, Opus 4.7, with Lon)
Mode 3 and mode 4 are meant to be the SAME flat-wired x86 BB — identical code, differing ONLY in
execution context (mode 3 = JIT executes the emitted blob in-process; mode 4 = `--compile` writes
it to a binary run as a separate process). Today they are NOT identical: they are two independent
x86 producers.
- **Mode 4** routes through the shared emitter (`src/emitter/` + `BB_templates/*.cpp`), sink =
  `g_emit_sink` (a `FILE*`, `emit_io.c:13`). `EMIT_BINARY_WIRED` (emit_core.c:31) already produces
  flat-wired binary x86 with `bb_fixup_*` relocation fixups (emit_core.c, string-concat + offset/
  length list — NO growable buffer, per Lon's 2026-05-28 ruling).
- **Mode 3** is a SEPARATE hand-written x86 generator in `sm_jit_interp.c` with its own `sl_*`
  byte-emitters, baking machine code into an `mmap` `PROT_EXEC` buffer (`label_blob_lookup`,
  `((blob_fn_t)blob)()` @ ~299). It natively compiles only the SM SPINE. For `SM_BB_PUMP_PROC` it
  bakes `mov rdi,name; mov rsi,nargs; call rt_bb_pump_proc` (sm_jit_interp.c:2069) → C path:
  `icn_bb_pump_proc_by_name` → `bb_node_t{.fn=icn_bb_dcg}` → `bb_broker(bb_pump)` → `icn_bb_dcg`
  (C four-port shim, RULES-exempt) → `bb_exec_once`/`bb_exec_resume` = the **C graph-walker**
  (`bb_exec.c`). `SM_BB_SWITCH`/`SM_BB_PUMP_SM`/`SM_BB_PUMP_CASE` are in the JIT's **no-op**
  `ignored slots` list (sm_jit_interp.c:~2086) — not handled at all on the native path.

Net: mode 3 walks the BB graph in C; only mode 4 realizes "BB = emitted x86". This violates the
design intent (mode 3 ≡ mode 4 sans process boundary) and is the last C-walker dependency on `--run`.

### The fix (one emitter, two consumers)
Make the **shared emitter the single source of x86 truth** for both modes. Mode 3 stops generating
its own BB x86 and instead consumes the emitter's `EMIT_BINARY_WIRED` output (bytes + `bb_fixup_*`),
loading it into the JIT `PROT_EXEC` buffer and `call`ing into it. Mode 4 is unchanged. No second
copy of BB x86 anywhere (option-2 "replicate templates in `sl_*`" is FORBIDDEN — it drifts).

⛔ **Invariant for the whole phase:** every closed step keeps smoke 5/5, broker ≥19, rungs ≥195,
AND mode-1/mode-4 emit byte-identical to their pre-J baselines. No broken commits.

#### J-1 — Characterize + pin the seam (no code) ✅ (2026-05-26, Opus 4.7)
**SEAM MAP (empirical, scrip @ `45c1bde2`):**
- JIT `rt_*` helpers that reach the C BB graph-walker: **ONLY `rt_bb_pump_proc`** (sm_jit_interp.c:233
  → `icn_bb_pump_proc_by_name` → `bb_node_t{.fn=icn_bb_dcg}` → `bb_broker(bb_pump)` → `bb_exec_once`/
  `bb_exec_resume`). Audited the other BB-family helpers: `rt_call_fn` (244) dispatches the NATIVE
  blob via `label_blob_lookup`+`((blob_fn_t)blob)()` (correct SM-spine path, NOT a walker) then
  builtins (IDX/etc.); `rt_suspend*`/`rt_call_expression`/`rt_exec_stmt` contain no walker refs.
  `SM_BB_SWITCH`/`SM_BB_PUMP_SM`/`SM_BB_PUMP_CASE` are in the JIT `ignored slots` NO-OP list
  (sm_jit_interp.c:~2086) — never handled natively. So the migration surface is small.
- ⚠ **NEW FINDING — mode 3 is RED for Icon TODAY, not merely C-delegated.** `./scrip --run
  /tmp/hello.icn` (the trivial `procedure main(); write("hello"); end`) prints NOTHING and errors
  `sm_eval_subexpr: invalid entry_pc 1` on stderr. `--interp` on the same file prints `hello`
  correctly. SNOBOL4 `--run` works (prints "hi"). So the JIT SM-spine is fine; the Icon
  `SM_BB_PUMP_PROC` JIT path is BROKEN, not just sub-optimal. Phase J fixes a real regression, not
  only an architectural wart. Marker frozen: `baselines/icon-bb/phase-j/mode3-icon-CURRENTLY-RED.txt`.
- ⚠ **NEW FINDING — `--ir-emit` (mode 1) is EMPTY for Icon.** md5 of `--ir-emit /tmp/hello.icn` ==
  `d41d8cd98f00b204e9800998ecf8427e` (= md5 of empty input). Mode 1 emits nothing for an Icon proc
  body; the "byte-identical mode-1" gate in later J steps is therefore trivially satisfied for Icon
  (it is the SNOBOL4 corpus that mode-1 must not perturb). Adjust J-4..J-6 gates accordingly:
  mode-1 byte-identity matters for the SNOBOL4/Snocone corpus, not Icon.
- ⚠ **NEW FINDING — mode 4 `--compile` emits `.macro NAME … call rt_*@PLT … .endm` spine.** The
  emitter's x86 is a spine of `call rt_*@PLT` into `libscrip_rt.so` PLUS wired BB — it is NOT fully
  self-contained inline x86. This is fine and expected: the "flat-wired BB" the JIT must consume is
  the same call-into-RT spine the emitter already produces; the JIT just needs those `rt_*` symbols
  resolvable in-process (they already are — same process, same RT). CLI confirms design intent:
  usage text reads "`--run` and `--compile` force wired".
- CLI flags confirmed: `--interp` (mode 2), `--run` (mode 3, DEFAULT, "x86 bytes → mmap slab → jump
  in"), `--compile` (mode 4, "emit standalone x86-64 asm to stdout, links libscrip_rt.so").
- Baselines frozen: `baselines/icon-bb/phase-j/hello.md5` (hello.ir-emit + hello.compile md5s).
- [x] Seam map produced (above). Migration surface = `rt_bb_pump_proc` + 3 no-op'd BB opcodes.
- [x] Pre-J baselines frozen under `baselines/icon-bb/phase-j/`.
- [x] Mode-3 Icon RED state captured as a regression marker (J-4 must turn it GREEN).
- [ ] STILL TODO before J-2: identify the exact emitter entry point that drives ONE proc body
  through templates in `EMIT_BINARY_WIRED` (the function the JIT will call per-proc). Candidate:
  the per-proc driver behind `--compile`; trace `SM_codegen`/`emit_*` proc loop next session.

#### J-2 — Emitter binary sink usable from the JIT (in-memory, not FILE) ⏳
**⚠ ROOT CAUSE of the mode-3 Icon RED found FIRST (2026-05-26, Opus 4.7) — reshapes J-2/J-3.**
Traced the two emit entry points: mode 4 `--compile` → `sm_codegen_text` → `codegen_sm_x86`
(shared emitter, emit_sm.c, writes text to a `FILE*`). Mode 3 `--run` → `sm_image_init` →
**`sm_emit_linear`** (defined in sm_jit_interp.c — the BESPOKE JIT generator, NOT the shared
emitter) → `sm_run_with_recovery_linear`. Confirmed: two independent x86 producers, as J-1 said.

The `--run` Icon failure `sm_eval_subexpr: invalid entry_pc 1` root-causes to a **lifetime bug**, not
a missing template:
1. scrip.c:424-444 (`mode_run`): after `sm_emit_linear`, calls `stage2_free_bb_after_emit(s2)` THEN
   `stage2_free_sm_bb(s2)` — freeing `g_stage2.sm.bb_table[]` AND the SM — **before**
   `sm_run_with_recovery_linear(NULL)` runs.
2. At runtime the JIT bakes `call rt_bb_pump_proc` (sm_jit_interp.c:2072). `rt_bb_pump_proc` →
   `icn_bb_pump_proc_by_name("main")` → `bb_graph_of_proc(e)` reads `g_stage2.sm.bb_table[e->bb_idx]`
   (icn_runtime.h:47-52) — **but bb_table was already freed in step 1** → returns NULL/garbage.
3. NULL graph → falls through to the `proc_table_call` oneshot (icn_runtime.c:380) → `sm_eval_subexpr`
   (icn_runtime.c:227) — **but the SM was also freed in step 1**, so entry_pc 1 is invalid → the error.

This is a textbook RULES.md "BB/SM deletion is total → distinct lifetimes" violation: mode 3 frees
the BB graph (consumed by the EMITTER) correctly, but the Icon path then tries to consume that graph
AGAIN at RUN time via the C walker — two consumers, one freed object, live alias in between. The
mode-2 `--interp` path works because it NEVER frees bb_table before running (scrip.c:414-423 has no
free) — the C walker reads a live graph.

**Consequence for the phase design:** the fix is NOT "give the C walker the graph back" (that
re-introduces the dual-consumer hazard and keeps the C walker on `--run`). The fix is the original
Phase-J thesis, now mandatory: mode 3 must EMIT the proc's flat x86 (so the BB graph is consumed
ONCE, by the emitter, at emit time — exactly like mode 4) and the JIT executes those bytes. After
that, `bb_table` being freed pre-run is CORRECT (nothing reads it at run time) and the lifetime
violation dissolves. So J-2/J-3 stand; J-1's "RED marker" is explained.

- [x] Decide sink mechanism: `open_memstream` as the `FILE*` for `codegen_sm_x86` so the shared
  emitter produces the SAME bytes mode 4 does, into memory (no new buffer API; honors 2026-05-28).
  Verify `EMIT_BINARY_WIRED` via memstream == file bytes for `hello.icn`'s `main`.
  ✅ **DONE 2026-05-26 (Opus 4.7), one4all `106b7c51` PUSHED.** `sm_codegen_x64_emit_test.c` gained
  a `--memcheck` mode: `emit_to_mem()` (open_memstream FILE* sink) vs `emit_to()` (file sink) for
  the canonical SM programs (EM-2 lit+halt, EM-3 arith, EM-4b loop) → **3/3 BYTE-IDENTICAL**.
  ⚠ FINDING: `codegen_sm_x86` carries PROCESS-GLOBAL accumulators (strtab/registry/macro-library)
  that are NOT reset between calls, so two emits in one process differ (+segfault). The faithful
  contract is SINGLE-SHOT-PER-PROCESS — which is exactly how mode-3/mode-4 each invoke it (once).
  The memcheck therefore fork-isolates each emission. Makefile harness target also fixed (was
  missing `-I$(SRC)/include`; SM.h lives there). Gates unchanged: smoke 5/5, broker 23, rungs 195.
- [x] Gate: `--memcheck` asserts memstream bytes == file bytes. ✅ (3/3). Built via
  `make out/sm_codegen_x64_emit_test`, run `./out/sm_codegen_x64_emit_test --memcheck`.
- [ ] ⚠ NOTE: mode 3's emit entry is `sm_emit_linear`, NOT `sm_codegen_text`. J-4 must decide:
  (a) replace `sm_emit_linear`'s per-proc BB handling with a call into `codegen_sm_x86` for proc
  bodies, or (b) longer-term, retire `sm_emit_linear` entirely in favor of the shared emitter +
  in-memory load (the true "mode 3 == mode 4 sans process" endgame, J-6). Recommend (a) incrementally
  behind `SCRIP_JIT_FLAT_BB`, converging to (b) at J-6.

#### J-3 — Load emitted bytes + apply `bb_fixup_*` into the JIT `PROT_EXEC` buffer ⏳
**⛔ DELETION SURFACE MAPPED (2026-05-26, Opus 4.7) — the exact mode-3 → C-walker edge to sever:**
- `sm_jit_interp.c:2072` — `sl_call(rt_bb_pump_proc)` (bakes the call into the mode-3 blob)
- `sm_jit_interp.c:1648` — `bake_blob_call_si(rt_bb_pump_proc, ...)` (same, with args)
- `rt_bb_pump_proc` (sm_jit_interp.c:233, JIT-local) → `icn_bb_pump_proc_by_name` →
  `bb_node_t{.fn=icn_bb_dcg}` → `bb_exec_once`/`bb_exec_resume` = THE C WALKER (FACT 2 violation).
- The C-walker symbols themselves (`icn_bb_dcg` icn_runtime.c:334, `pl_bb_dcg` pl_runtime.c:36,
  `bb_exec_once`/`resume` bb_exec.c:2021/2036) STAY DEFINED — Mode 2 needs them (FACT 1). Only the
  mode-3 CALL EDGE dies. `sm_interp.c` reaching the walker is FINE (that is mode 2).
**Sess 2026-05-26 (Sonnet 4.6, `de0f2352`):** J-3 re-scoped. Shared emitter emits TEXT asm; BB_templates
for Icon are stubs. Correct J-3: `SM_BB_PUMP_PROC` in mode-3 emits `call rel32` to proc's SM
entry_pc in the linear blob (mirrors mode-4 `CALL_EXPRESSION .L<entry_pc>`). No binary loader
needed. Also fixed `rt_call_fn` to try `icn_try_call_builtin_by_name` before INVOKE_fn.
- [x] Gate: `--run hello.icn` SCRIP_JIT_FLAT_BB=1 prints "hello". smoke 5/5 unchanged.

#### J-4 — Route `SM_BB_PUMP_PROC` JIT codegen through J-2/J-3 (behind `SCRIP_JIT_FLAT_BB=1`) ⏳
**Sess 2026-05-26 (Sonnet 4.6, `de0f2352`):** Implemented together with J-3. When `SCRIP_JIT_FLAT_BB=1`,
`sl_emit_one` SM_BB_PUMP_PROC looks up `entry_pc` from `g_stage2.proc_table` at emit time, emits
`rt_setup_icn_frame(name,nargs)` + `sub rsp,8/call rel32/add rsp,8` + `rt_teardown_icn_frame()`,
patches call target in pass 2 via `sl_add_patch`. No BB, no SM ptr, no C walker at runtime.
Flag OFF: original broken `call rt_bb_pump_proc` unchanged.
**Sess 2026-05-26 (Sonnet 4.6, `b9203411`):** Four correctness fixes:
1. `SM_VOID_POP` before `SM_RETURN*` = no-op in sl_emit_one. Root cause: mode-2 `sm_interp.c`
   has `case SM_VOID_POP:` falling through to `SM_RETURN` (no break) — never pops; return value
   stays on stack. Mode-3 was popping it via `rt_void_pop`. Peek-ahead fix in sl_emit_one.
2. `h_return_impl`: when `NV_GET_fn(retval_name)` = empty/null, use stack top (Icon proc return).
3. `SM_LOAD_FRAME`/`SM_STORE_FRAME` wired via `rt_load_frame`/`rt_store_frame` (icn_frame_env_*).
4. `rt_call_fn`: push IcnFrame from call args before native blob call; pop after.
- [x] `--run hello.icn` SCRIP_JIT_FLAT_BB=1 prints "hello" ✅
- [x] `double(21)` returns 42 under SCRIP_JIT_FLAT_BB=1 ✅
- [x] smoke 5/5 both flag states ✅; broker 23 unchanged ✅
- [x] **SM_ACOMP + SM_LCOMP wired** ✅ (`dfaf3032`, 2026-05-26 Opus 4.7). JIT-local
  `rt_acomp_op`/`rt_lcomp_op` in sm_jit_interp.c mirror rt.c rt_acomp/rt_lcomp; one int
  op-arg (TT_LE etc.) in rdi via sl_mov_rdi_i64+sl_call, same shape as SM_INCR. Was
  falling to rt_unimpl_op. `fib(7)=13` under SCRIP_JIT_FLAT_BB=1 == --interp ✅.
  SM_JUMP_S/F verified composing with new last_ok (then/else/if-as-value byte-identical
  to --interp). SM_ICMP_GT/LT confirmed DEAD (never emitted). smoke 5/5, broker 23,
  rungs01-35 189/2 — both flag states.
- [ ] **NEXT: GENERATORS.** `every`/`to`/`by` abort under --run flag-on
  (`rung01_paper_to_by` → `sm_interp: stack underflow`). Generator iteration (SM gen-tick
  / BB generator pump) not yet on flat-x86 path; substantial J-5 work, overlaps BB
  generator templates. Then J-5 ignored slots (NOTE: SM_PUMP_CASE=Raku-only,
  SM_BB_SWITCH=Prolog — neither is Icon), then J-6 flip default + delete C bridge.

#### J-5 — Migrate the rest of the J-1 seam (PUMP_SM, PUMP_CASE, BB_SWITCH, generator path) ⏳
- [ ] One opcode per sub-step, same flag, same gate each. Bring the JIT's `ignored slots` BB
  opcodes onto the emitted-x86 path so generators/case/switch run native in mode 3.
- [ ] Gate (each): smoke 5/5, broker ≥19, rungs ≥195, byte-identical mode-1/mode-4.

#### J-6 — Flip default to flat BB; delete the C bridge ⏳
- [ ] Make `SCRIP_JIT_FLAT_BB` the default (then remove the flag). Delete `rt_bb_pump_proc` and any
  now-orphaned `rt_*` BB bridges from sm_jit_interp.c. Confirm `icn_bb_dcg`/`bb_exec_once` are no
  longer reachable from `--run` (they remain the mode-2 `--interp` reference path — do NOT delete).
- [ ] Honest check: `--run` executes ZERO C-walker BB code; the ONLY BB x86 in the process is the
  shared emitter's output. grep proves no JIT-local BB x86 generation remains (`sl_*` BB arms gone).
- [ ] Gate: smoke 5/5, broker ≥19, rungs ≥195, byte-identical mode-1/mode-4, ASAN clean
  (`detect_use_after_free=1`) on all smoke gates per RULES.md deletion-total rule.

**Phase J done when:** mode 3 (`--run`) and mode 4 (`--compile`) execute the IDENTICAL emitter-
produced flat-wired x86 BB, differing only in process boundary; `rt_bb_pump_proc` + JIT-local BB
x86 deleted; `icn_bb_dcg`/`bb_exec.c` unreachable from `--run` (still live for `--interp`);
smoke 5/5, broker ≥19, rungs ≥195, mode-1/mode-4 byte-identical, ASAN clean.

---

## Honest-mode-3 protocol

Probe helpers in `scripts/icon_bb_probes.sh`: `bb_probe_detect`, `bb_probe_complete`, `bb_probe_scoreboard`.
Baseline md5: `baselines/icon-bb/--interp-honest.md5` (created sess 2026-05-11c).

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

## Active next targets (2026-05-26, build GREEN, gates GREEN) — Phase H continues.

Sess 2026-05-26m (Opus 4.7, with Lon — one4all `9be28a5d` PUSHED — H-1 GENERATOR-COMPOSITION: BB_CONJ): split Icon conjunction
`E1 & E2` off the overloaded BB_IF into its own opcode **BB_CONJ**. Root cause of rung13_alt_alt_filter
infinite loop (`every (x:=(1|2|3|4|5)) > 2 & write(x)` → `3 4 5 3 4 5…`): TT_SEQ lowered to BB_IF
(α=E1, β=E2), but BB_IF (if-then) treats cond-FAILURE as NON-FATAL — returns γ (success) with &null.
A conjunction must return ω (FAIL) when E1 is exhausted. The fake success kept the enclosing `every`
pumping, so the cond generator reset and restarted forever. Fix: new BB_CONJ kind (BB.h enum +
scrip_ir.c name table, inserted after BB_IF — positional name list updated to stay aligned); TT_SEQ →
BB_CONJ; BB_CONJ executor is a proper GENERATOR (state 0=fresh: reset+drive E1; 1=resume E1's
generator for next success; each E1-success runs E2 fresh + yields E2-value via γ; E1-exhaustion → ω).
Classifier `default` already treats BB_CONJ as gen iff E1 is gen (no change needed). **rungs 195→196
(+1: rung13_alt_alt_filter), smoke 5/5, broker 23, ZERO regressions** (only non-rung36 fail left =
rung06_cset_upto_basic, a separate scan-`?`-resume bug). bb_exec.c mode-2 only; mode-3 `--run`
`sm_eval_subexpr: invalid entry_pc 1` is the documented PRE-EXISTING Icon mode-3 emitter gap (hits even
plain hello.icn), NOT caused by BB_CONJ. BB_CONJ needs a bb_*.cpp emitter template for mode-3/4 (TODO,
flagged with Phase J emitter work).
**NEXT: rung06 scan-`?` generator resume** (`every (S ? write(upto(c)))` loops — scan subject/pos not
resuming), then the remaining H-1 work below (nested non-leaf IF DOWN-threading).

Sess 2026-05-26k cont. (Opus 4.7, with Lon — H-1 FOUNDATION LANDED, one4all `45c1bde2` PUSHED):
After closing the G-2 ladder (see below), landed the Phase H attribute-grammar foundation. Added
`lower_icn_expr_threaded(cfg, e, γ_in, ω_in, &α_out, &β_out)` (additive wrapper — does NOT touch the
70 internal lower_icn_expr_node sites; stamps inherited γ/ω onto the synthesized node, fills NULL
ports only, guards ω-operand kinds via icn_kind_owns_omega_operand=BB_IF). `lower_icn_proc_body`
rewired to thread the statement spine BACK-TO-FRONT (each stmt born with its continuation; replaces
the old patch loop + BB_IF special case). This EXPOSED a latent γ-conflation: BB_IDX_SET and
BB_SECTION packed their 3rd operand onto the γ-continuation port — worked before ONLY because the
old SEQ loop overwrote γ post-build. Fixed both (H-4 IDX_SET/SECTION done): 3rd operand → β node's
γ-chain, freeing γ for the continuation; executors read `nd->β->γ`. **rungs 189→195 (+6: rung13/23/35
table+subscript-assign cluster + rung36_jcon_trim), smoke 5/5, broker 19, ZERO regressions** (verified
comm -23 BASE vs new = empty). Honest (interp via bb_exec.c ports).
⚠ AUDIT NOTE for next session: the worker's ω-operand guard lists only BB_IF. As H-3/H-4 migrate more
operand-bearing kinds, check each for ω-as-operand (or γ-as-operand, like the IDX_SET/SECTION bug just
fixed) BEFORE the worker stamps continuations.
**NEXT: complete H-1's remaining work** — full inherited-γ/ω DOWN-threading into then/else/body for
NESTED non-leaf IF (if-as-value, where branches need their own continuations) + deep generator
composition. This means pushing the 4-attribute signature INTO the builders (recursive lowering of
then/else/body receives γ/ω), not just stamping the parent post-hoc. Then H-2 (BB_SEQ formalization),
H-3 (2-operand kinds), rest of H-4 (N-ary CALL already done 26i), H-5 (sweep bb_exec.c c[]/n).

### (prior G-2 ladder close) 2026-05-26k watermark below

Sess 2026-05-26k (Opus 4.7, with Lon): **G-2 RT-DELETE ladder CLOSED** — finished the decl-scrub
tail (G-2a/G-2b/G-2g) in one commit `f0f99035` (rebased onto upstream `38e66809`, no conflict).
G-2a: `rt_alt` was a dead extern (declared in bb_alt.cpp, `call rt_alt@PLT` in the mode-4 TEXT arm,
DEFINED NOWHERE — a latent mode-4 link bug); BB_ALT's real interp path is bb_exec.c:589 (ω-chain
walk), so nothing executed it. Removed the extern + rewired TEXT/BINARY arms to port-jump (α→γ,
β→ω; inline-x86 n-ary gen = mode-4 TODO), mirroring G-2c. Also corrected a stale BINARY bin-table
(3 fixups on a 2-jmp body → 2 fixups). G-2b: removed 8 never-defined `icn_bb_*` decls from
icon_gen.h + 4 matching dead externs from emit_bb.c + 4 dead `icon_to_*` decls from icon_box_rt.h.
G-2g: `icon_box_rt.c` was empty (all four Byrd boxes gone by G-2f) → deleted file + 2 Makefile
lines (chose option (a)); icon_box_rt.h kept for `icn_to_by_rt_state_t`. GATES green throughout:
smoke 5/5, broker 19 (×3 stable), rungs 189 — all unchanged from `8078211f` baseline.
⚠ OBSERVED (out of scope, NOT done): emit_bb.c still carries ~36 other never-called
`extern DESCR_t icn_bb_*` decls (lines ~20-98, e.g. icn_bb_every/not/while_gen/case_gen/intlit/...);
all undefined, all dead. A future broad scrub candidate — left untouched to keep G-2b's diff tight.
Also still noted from prior sessions: `SCRIP_NO_AST_WALK=1` prefix in icon_bb_probes.sh +
test_prolog_bb_honest.sh is a dead no-op (the real tripwire is the always-on NO_AST_WALK_GUARD
macro) — ~5 min cleanup, not yet done.
**NEXT: H-1** — full inherited-γ/ω threading in the lowerer (`lower_icn_expr_node` 4-attribute
signature) for nested non-leaf IF/generators; then H-2..H-5. The G-2 ladder no longer blocks it.

### (prior) 2026-05-26j watermark below

Sess 2026-05-26j (Opus, with Lon — RT-DELETE ladder): per Lon directive "remove all RT functions
that handle 4-port logic; string-conversion/value RT helpers STAY." Audited the Icon RT path and
deleted all FOUR defined C four-port Byrd boxes (`DESCR_t foo(void*|BB_t*,int entry)`), one per
commit, gates green at each: **G-2c rt_binop_gen `7d43dc79`, G-2d icn_every_box `1101884f`,
G-2e icn_list_bang `3666025a`, G-2f icn_to_by_rt+ctors `4da7a6b7`.** All four were reachable ONLY
from their mode-4 TEXT emitter templates (`call …@PLT`); the interp path (modes 2/3) already uses
bb_exec.c BB-port executors, which is WHY every gate held at smoke 5/5 / broker 19 / rungs 189
unchanged across all four deletions. Each template's TEXT+BINARY arms rewired to the port-jump form
(α→γ, β→ω, mirroring bb_alt) — the inline-x86 GENERATOR logic for each is now flagged `mode-4 TODO`
in-template (this is real future emitter work, but mode-4 to/by is already broken today: `--run`
prints `invalid entry_pc 1`, so nothing regressed). `lower_iterate` (the last SM_BB_SWITCH holdout)
rerouted to lower_icn_expr_top. **`icon_box_rt.c` is now an EMPTY translation unit.**
⚠ one4all `82ec79f8`(start) → `4da7a6b7`(end), tree CLEAN, all four pushed-pending (see handoff).
NOTE on scope: NOT touched (correctly out of scope per directive) — Prolog `pl_*_fn`/`pl_bb_dcg`
(GOAL-PROLOG-BB), SNOBOL4 `bb_deferred_var` (SN4 goal), and the EXEMPT infra shims `icn_bb_dcg`/
`icn_bb_oneshot` (RULES.md). Value/conversion helpers `rt_vstack_pop`/`subscript_get`/`icn_binop_apply`
KEPT (they are not four-port dispatchers).
REMAINING in G-2 ladder (decl-scrub only, no logic, next session ~15 min): G-2a `rt_alt` dead extern
in bb_alt.cpp (defined NOWHERE — latent mode-4 link bug; BB_ALT runs via bb_exec.c:589 interp path);
G-2b nine dead `icn_bb_*` decls in icon_gen.h + four dead `icon_to_{make,by_make,tick,by_tick}` decls
in icon_box_rt.h (all declared-never-defined-never-referenced); G-2g decision: delete the now-empty
icon_box_rt.c + its Makefile lines 179/391, or keep as empty TU (recommend delete).
NEXT after cleanup (unchanged from H plan): H-1 full inherited-γ/ω threading; then H-2..H-5.

### (prior) 2026-05-26h watermark below


Sess 2026-05-26h (Opus, EMERGENCY HANDOFF — but GREEN and committed+pushed): one bounded rung fix
landed. **one4all `3681a6a9` pushed to origin/main.** Tree CLEAN.
GATES: smoke_icon **5/5**, unified_broker **18**, icon_all_rungs **176** (was 174, +2). Honest
(NO_AST_WALK identical). Prolog smoke 0/5 unchanged (pre-existing, see 26g below).
FIX: negative literal step `by -3` in `lo to hi by step` produced EMPTY output. `-3` parses as
`(TT_MNS (TT_ILIT 3))`, NOT `TT_ILIT -3`; TT_TO_BY lowerer (lower_icn.c) read `by_n->v.ival`
directly (=0 on a TT_MNS node) → step defaulted to 1 → exhaustion check fired immediately. New
static `icn_fold_signed_lit()` folds unary TT_MNS/TT_PLS over int/float literals at lower time;
used for both is_real detection and the step value (int + real arms). Flipped `rung01_paper_to_by`
+ `rung19_pow_toby_real_toby_neg` to PASS. Only `src/lower/lower_icn.c` touched (+32/-3).
⚠ EMERGENCY NOTE — NOT a code breakage: flagged because the container FS reset mid-session; the
fix had to be re-confirmed already-committed-but-unpushed (local HEAD ahead of origin by 1) and
then pushed. Nothing is broken. Lesson for next session: commit+push immediately after a green gate;
do not leave work uncommitted across turns.
⚠ SEPARATE PRE-EXISTING ISSUE OBSERVED (out of scope, NOT regressed, NOT fixed): `--run` (Mode 3.5
JIT) on rung01 prints `sm_eval_subexpr: invalid entry_pc 1` — BB_TO_BY has no working x86 emitter
path yet. This is emitter work (G-6 / Phase H emit), independent of the interp lowering fix. The
rung gate is `--interp`-only so it is unaffected.
NEXT (unchanged from H plan): H-1 full inherited-γ/ω threading; then H-2..H-5, G-2..G-8. Prolog
counter-aliasing decision still pending Lon (see 26g + HANDOFF-2026-05-26-OPUS-PROLOG-COUNTER-ALIASING.md).

### (prior) 2026-05-26g watermark below

Sess 2026-05-26g (Opus): **DIAGNOSIS-ONLY — tree CLEAN at `319b2b6e`, nothing committed to code.**
Root-caused the Prolog `--interp` empty-output (smoke 0/5) bug. CAUSE: `bb_reset` (scrip_ir.c:58)
zeroes `nd->counter`, but option-(b) (2026-05-26d) overloaded `counter` to carry PERSISTENT
compile-time aux pointers (goal/clause/arg vectors) for BB_PL_SEQ/CHOICE/PL_CALL/PAT_ARBNO. First
`bb_exec_once`→`bb_reset` wipes the vectors → SEQ `if(!sq)` guard fires → silent empty output. This
is the field-aliasing hazard prior watermarks gestured at: `counter` carries TWO incompatible
lifetimes (transient runtime state, zeroed on reset, used by PROC_GEN/FIND_GEN; vs persistent aux
ptr, must survive). THREE fixes attempted + REVERTED: (1) preserve counter by node-type → smoke
0/5→5/5, broker 18→22, sno-JIT-interp 185→188, NO regression on icon/sno smoke or icon_all_rungs,
but rung10 crashes ~30% (parent 0/30); (2) +clear transient sub-fields → still crashes; (3) +active-
cfg-stack recursion guard w/ conditional bb_snapshot/restore on BB_PL_CALL (mirrors BB_CALL Icon
guard) → smoke 5/5, valid deep recursion (count(50)+nrev+append) 0/25, backtracking preserved
(clause smoke ok) — but rung10 STILL crashes. WHY rung10 defeats all: it PARSE-ERRORS at line 187
(truncated corpus file, present at parent too), never executes, never counted; crash is in TEARDOWN
of a partial graph — preserving counter by node-type is unsound when counter holds garbage/transient
on an aborted graph. FIX NEEDS LON'S DECISION (see HANDOFF-2026-05-26-OPUS-PROLOG-COUNTER-ALIASING.md):
disambiguate the two lifetimes — (A) bit-cast aux ptr into ival/dval (BB.h already calls these
"compile-time IR payload"; needs GOLDEN-rule ruling) [RECOMMENDED], or (B) cfg-level side table.
Then re-add the Attempt-3 recursion guard (independently correct for deep Prolog recursion).
ALSO RAISED w/ Lon: `SCRIP_NO_AST_WALK` env is DEAD (unread by any C code; grep-verified) — the
"honest gate" is now a no-op since mode-1 AST walker was physically deleted (CLI-3M-9). "Done when
#3" is tautological; candidate cleanup. (Assess g_ast_pump_active separately — live in SM_BB_PUMP_PROC.)
NOTE: baseline gates re-confirmed unchanged this session: smoke_icon 5/5, broker 18, icon_all_rungs
174, prolog smoke 0/5, prolog_bb_honest 128/0/0.

Sess 2026-05-26f (Opus): **GATES RED→GREEN, COMMITTED `319b2b6e`.** Fixed the two bb_exec.c bugs
the 2026-05-26e handoff flagged. ROOT CAUSE was systemic, deeper than described: `BB_node_alloc`
seeded `α=nd, β=nd` (self-pointers). Any lowerer that conditionally set a port left a live
self-pointer, so leaf/operand-less nodes falsely appeared to have operands. Three manifestations:
(1) body-less `every` had β=self → infinite self-recursion at the body call (the documented
"every write(1 to 3) SEGFAULT"); (2) literal `1 to 3` had α/β=self → BB_TO has_dyn=(α&&β) fired
wrongly → recursion; (3) BB_VAR leaf had α=self → ir_is_single_shot recursed forever (hit by
`every i:=1 to 3 do write(i)`). FIX: `BB_node_alloc` now inits α/β to NULL. Verified no executor
reads `α==nd` as meaningful — every site tests non-NULL as "has operand" (grep: 67, 1561, 1977);
lower_pat_dcg.c sets its self-entry explicitly so it's unaffected.
BB_IF both-branches: lowerer wired else into `nd->γ` (the success-continuation port) so cond-success
followed γ into the else box. FIX: else now on `nd->ω` (failure port); BB_IF executor runs ω only on
cond-failure, both paths return inherited γ; lower_icn_proc_body SEQ-chain no longer clobbers a
BB_IF's ω (skips ω-forward for BB_IF). lower_icn.c also: TT_TO literal-vs-dynamic split (non-literal
bounds → operand boxes in α/β), TT_EVERY/WHILE/UNTIL set β explicitly.
GATES: smoke_icon **5/5** (was 3/5), broker **18** (was 15, baseline ≥17, stable ×3), rungs **174**
(was 118, baseline 153, target ≥169 — exceeded). All verified under `SCRIP_NO_AST_WALK=1` (honest,
no AST back-doors). Prolog smoke 0/5 unchanged (pre-existing from 1c4e37c7, confirmed via git stash);
SNOBOL4 smoke 7/0 clean. Files: scrip_ir.c, lower_icn.c, bb_exec.c.
NEXT: H-1 proper inherited-γ/ω threading remains for nested non-leaf IF/generator composition (the
fixes here are correct for statement-context + leaf/last-stmt; full attribute-grammar threading per
the Phase H spec is still the larger task). Then continue H-2..H-5, G-2..G-8. Also still open from
2026-05-26e: verify multi-clause Prolog Mode-4 emission (`;/2` [NO-AST] in interp; check --compile).

### (prior) 2026-05-26e watermark below

Sess 2026-05-26e (Opus): **BUILD RESTORED RED→GREEN.** Prior "RED at emit_sm.c only" was wrong —
sm_jit_interp.c died first (broken since 7b087f0f, masked by bb_exec.c errors). Fixed sm_jit_interp.c
(CUR_INS macro missing, rt.h include collision, macro ordering, fwd decls, SM_instr_t→SM_t,
bb_exec_pat_fn→exec_stmt_blob link fix). DONE the documented emit_sm.c Prolog serializer reshape
(XA_PL_SUB_BUILDER now iterates bb_pl_choice_state_t.bodies[]; new xa_pl_sub_body_idx threaded
through both XA templates; multi-body BB_CHOICE emits N sub-builders each appending via set_opaque).
DONE the COUPLED flat-pattern pair (emit_sm.c builder + emit_bb.c walk_bb_flat) → new
bb_pat_kids_state_t GC aux (BB.h) replacing c[]/n; emit_per_kind_audit.c synthetic nodes too.
scrip links (8.8MB). See HANDOFF-2026-05-26-OPUS-BUILD-GREEN.md.
⛔ GATES RED — pre-existing Phase H bugs in bb_exec.c (NOT touched this sess): (1) BB_IF runs BOTH
branches (needs H-1 inherited-γ/ω threading; else-on-γ collides w/ success continuation), (2)
`every write(1 to 3)` SEGFAULTS (BB_EVERY+BB_TO port re-read). smoke 3/5, broker 15, rungs 118/113/35.
NEXT: fix those two bb_exec.c bugs → smoke 5/5, broker ≥17, rungs ≥153 → COMMIT. Verify multi-clause
Prolog Mode-4 emission (`;/2` directive is [NO-AST] in interp; check --compile CLI).

### (prior) 2026-05-26d watermark below

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

Sess 2026-05-26c (Opus, checkpoint — BUILD STILL RED at BB_LIMIT): continued executor port-
migration. NOW MIGRATED (read α/β, no c[]/n): BB_INITIAL (has-run flag ival3→ival since ival is
IR payload that survives bb_reset, unlike state; body c[0]→α), BB_RETURN (retval→α), BB_IF
(cond→α/then→β/else→γ; ⚠ else-on-γ collides with γ-as-success-continuation — works only for
leaf/last-statement IF, full fix needs H-1 inherited-γ/ω threading; flagged inline), BB_EVERY/
BB_WHILE/BB_UNTIL (gen|cond→α, body→β), BB_REPEAT (body→α), BB_NOT/BB_NONNULL/BB_NULL_TEST/
BB_RANDOM/BB_NEG/BB_POS/BB_CSET_COMPL (operand→α), BB_IDENTICAL (α/β). bb_exec.c c[] 229→130,
n 57→37. NEXT (the hard cluster, needs per-node state-packing design — opaque/ival2 collide with
counter where multiple live at once): BB_LIMIT (bb_exec.c:566, uses c[0]/c[1]/ival/ival2/counter/
state together), then BB_LCONCAT-adjacent generators BB_LIST_BANG/BB_KEY_GEN/BB_FIND_GEN/BB_GEN_*/
BB_BINOP_GEN/BB_ALT/BB_TO/BB_UPTO/BB_PROC_GEN, plus remaining BB_IDX/BB_SECTION/BB_FIELD_*/
BB_SIZE/BB_CASE multi-operand (c[]→α/β/γ-chain). Then emit_bb.c(20)/emit_sm.c(17). NO GATES RUN.
DECISION NEEDED for the generator cluster: BB_t has only value/counter/state as runtime-mutable
+ sval/ival/dval as reset-surviving payload. Generators caching a pointer (GeneratorState*,
TBBLK_t*, find_gen_state_t*) AND a counter AND a bound need >3 slots. Options: (a) cast pointer
into counter (works only where counter unused — BB_CALL did this), (b) allocate an aux state
struct via GC and stash its pointer in counter, freeing the other slots. (b) is the general
answer and matches JCON's per-construct state records. Recommend (b) next session.
[one4all HEAD this checkpoint: 309274c2]

Sess 2026-05-26d (Opus, EMERGENCY HANDOFF — BUILD RED at emit_sm.c only): full c[]/n/opaque/
ival2/sval2 eradication across the INTERPRETER path. DESIGN RESOLVED with Lon: BB_t needs NO new
fields. Three runtime slots (value/counter/state) + option-(b) GC aux-struct (pointer stashed in
counter, intptr cast) covers every kind; matches JCON per-construct state records. New aux structs
in BB.h: bb_arbno_state_t, bb_pl_seq_state_t, bb_pl_choice_state_t, bb_pl_call_state_t.
DONE (compiles clean): (1) ALL Icon kinds in bb_exec.c — LIMIT(c0/c1→α/β, max re-read from
β->value), ALT(walk ω-chain from α), CSET_*/GEN_SCAN/SIZE/IDX/SECTION/FIELD_GET/SET/IDX_SET
(α/β/γ per lower_icn wiring), LIST_BANG/KEY_GEN(re-read α->value, no opaque), SEQ_GEN(step
re-read from β->value), CASE(walk γ-chain sel→key→val), TO(α/β dyn or ival/dval static, no ival2),
UPTO(hay=scan_subj not sval2), ITERATE(α->value), FIND_GEN(option-b find_gen_state_t+pos in
counter), PROC_GEN(counter, matches lower_icn:95), GEN_ALT/GEN_BINOP/TO_NESTED(counter),
PAT_POS/PAT_TAB(from-end flag n→sval "r"), PAT_ARBNO(bb_arbno_state_t in counter). (2) ALL Prolog
kinds — PL_SEQ/CHOICE/PL_CALL/PL_ALT/PL_VAR + ARITH/UNIFY/BUILTIN slot reads (ival2→ival). Field
semantics STANDARDIZED: PL_VAR slot + PL_CALL arity → ival; is_relop derived in icn_binop_apply.
(3) lower_pl.c — both SEQ builders (lower_pl_seq γ-chain REVERTED to goal-array aux; clause_body
seq->c/n→aux), lower_pl_predicate (BB_CHOICE bodies→bb_pl_choice_state_t), PL_CALL N-arg vector
(was only α/β = real >2-arg bug, now full args[] in aux). +#include <gc/gc.h>. (4) rt.c — rt_pl_b_node/
sub_node (per-kind aux alloc), rt_pl_b_kids/sub_kids (route to aux goals/args or α/β), rt_pl_b_set_
opaque (append to BB_CHOICE.bodies[]). (5) lower_pat_dcg.c (ARBNO aux x2, POS/TAB sval flag). (6)
lower_icn.c TT_AUGOP (dropped dead binop->c calloc; BB_ASSIGN α/β not c/n).
⛔ REMAINING — emit_sm.c (Mode-4 Prolog serializer) ONLY. Helpers ADDED (pl_node_kids, pl_node_
ival2, pl_node_choice_body0) but NOT yet wired into the 4 read sites (~322/378/388/445 etc). NOT
mechanical: old serializer used per-BB_SUCCEED opaque clause carriers (one body each); new
bb_pl_choice_state_t holds ALL clause bodies in ONE BB_CHOICE node — the XA_PL_SUB_BUILDER loop
must be reshaped to iterate bb_pl_choice_state_t.bodies[] instead of scanning for BB_SUCCEED+opaque.
Then: full build → smoke 5/5, broker ≥17, rungs ≥153 → commit. NOTHING committed this session
beyond this handoff. BB_t struct is FINAL — do not add fields.
[one4all working tree this handoff: based on 309274c2, uncommitted interp-path migration]


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
| rung01 to-by neg-step | `3681a6a9` | rungs 174→176 | `icn_fold_signed_lit` folds (TT_MNS (TT_ILIT 3)) → -3 in TT_TO_BY lowering; was defaulting step to 1 → empty output. Also flips rung19. |
| H-1 threading + IDX_SET/SECTION | `45c1bde2` | rungs 189→195 | Attribute-grammar threaded lowerer (`lower_icn_expr_threaded`) + back-to-front spine threading in lower_icn_proc_body. Fixed BB_IDX_SET/BB_SECTION 3rd-operand-on-γ conflation (operand moved to β γ-chain). Gains: rung13_table_subscript_assign, rung23_table_table_{basic,default,key,member}, rung35_table_str_str_{default_int_key,table_read}, rung36_jcon_trim. |

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
