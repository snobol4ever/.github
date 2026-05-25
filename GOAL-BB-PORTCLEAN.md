# GOAL-BB-PORTCLEAN.md — Eradicate BB_t.c[] / BB_t.n: replace with named fields

**Repo:** one4all + .github
**Carved:** 2026-05-25 (session with Lon, Claude Sonnet 4.6)
**Sister docs:** `GOAL-ICON-BB.md`, `GOAL-BB-TEMPLATE-LADDER.md`

---

## Why

`BB_t` is a node in a **wired directed graph** (Byrd boxes connected by four ports:
α β γ ω). It is NOT a tree. The fields `BB_t **c` and `int n` smuggle
AST-tree-child semantics into graph nodes, which is wrong in design and causes
bugs. Every `nd->c[i]` access on a `BB_t` is an offence.

The architecture:

```
tree_t   — produced by parser, consumed by lower
           ↓ lower()
SM_sequence_t  — flat array of stack-machine instructions (primary output)
BB_graph_t     — wired directed graph of Byrd boxes, stored in sm.bb_table[]
                 and referenced from SM instructions by index
```

`BB_graph_t` nodes (`BB_t`) must use only:
- **α, β** — this box's own entry points (callers jump IN here)
- **γ, ω** — successor boxes this box jumps OUT to on succeed/fail
- **lhs, rhs, operand** — named sub-box pointers for operand sub-expressions
- **ival, ival2, ival3, sval, sval2, dval** — compile-time scalar data
- **opaque** — runtime state struct pointer
- **value, counter, state** — per-execution mutable state (pending deletion per F-6g)

Labels in JCON irgen.icn = pointers in SCRIP BB graphs. α/β/γ/ω are pointers,
not indices.

**Operands (lhs/rhs) vs control (γ/ω):**
- γ/ω are **inherited** — set by the caller/context, tell the box where to jump
- α/β are **synthesized** — exposed by the box as its own entry points
- lhs/rhs/operand are **operand sub-boxes** — driven by this box evaluating them;
  NOT the same as γ/ω which are control-flow successors

---

## Baseline (session 2026-05-25, one4all pre-commit)

Gates before any work in this goal:
```
smoke icon:    PASS=5  FAIL=0
broker:        PASS=17 FAIL=32
icon rungs:    PASS=153 FAIL=78 XFAIL=35
```

Uncommitted at session start: SM_UNUSED_1..5 rename + partial F-6d
(BB_BINOP/BINOP_GEN/LCONCAT/ARITH/UNIFY/BUILTIN/PL_ALT migrated to α/β).
**Commit these first before any new work.**

---

## Session Setup

```bash
cd /home/claude/one4all
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
```

Gates:
```bash
bash scripts/test_smoke_icon.sh              # PASS=5
bash scripts/test_smoke_unified_broker.sh   # PASS=17
bash scripts/test_icon_all_rungs.sh         # PASS=153
```

---

## Step 0 — Commit session work ⏳

Commit the uncommitted changes from the 2026-05-25 session:
- SM_UNUSED_1..5 opcode rename (SM.h + sm_prog.c)
- F-6d partial: BB_BINOP, BB_BINOP_GEN, BB_LCONCAT, BB_ARITH, BB_UNIFY,
  BB_BUILTIN, BB_PL_ALT migrated from c[]/n to α/β in:
  lower_icn.c, lower_pl.c, bb_exec.c, emit_bb.c, bb_arith.cpp, bb_unify.cpp,
  emit_per_kind_audit.c

```bash
cd /home/claude/one4all
git add -A
git commit -m "F-6d partial + SM_UNUSED_1..5: BB_BINOP/ARITH/UNIFY/BUILTIN/PL_ALT use α/β not c[]. smoke 5/5 broker 17."
```

---

## Step 1 — Add lhs/rhs/operand fields to BB_t ⏳

**File:** `src/include/BB.h`

Add three named sub-box pointer fields to `struct BB_t`, just after the port fields:

```c
struct BB_t {
    BB_op_t           t;
    BB_t         * α;        /* this box's start-fresh entry point */
    BB_t         * β;        /* this box's resume/backtrack entry  */
    BB_t         * γ;        /* successor on succeed               */
    BB_t         * ω;        /* successor on fail                  */
    /* Named operand sub-box pointers — replace c[]/n for binary/unary kinds */
    BB_t         * lhs;      /* left operand sub-box  (binary kinds) */
    BB_t         * rhs;      /* right operand sub-box (binary kinds) */
    BB_t         * operand;  /* single operand sub-box (unary kinds) */
    BB_t        ** c;        /* DEPRECATED — being removed; see GOAL-BB-PORTCLEAN */
    int            n;        /* DEPRECATED — being removed; see GOAL-BB-PORTCLEAN */
    ...
```

Also update the comment on `BB_ARITH`, `BB_UNIFY`, `BB_BINOP_GEN` in the enum
to say `lhs/rhs` not `c[0]/c[1]`.

Gate: build only — `bash scripts/build_scrip.sh`. No behaviour change.

---

## Step 2 — Delete rt_binop_gen (dead C Byrd box) ⏳

**File:** `src/runtime/interp/icon_box_rt.c` and `.h`

`rt_binop_gen(BB_t *nd, int entry)` is a C Byrd box function — exactly what the
GOAL-ICON-BB absolute rule forbids. It duplicates the BB_BINOP_GEN logic that
now lives in `bb_exec.c` using α/β. It is called only from
`bb_binop_gen.cpp` (the x86 emitter template). Since the executor path is
`bb_exec.c`, this function is dead for the interp path, and the emitter template
needs to be rewired to not call it.

Sub-steps:
- a) Remove `rt_binop_gen` from `icon_box_rt.c` and `icon_box_rt.h`
- b) Update `bb_binop_gen.cpp` to emit inline x86 instead of calling
  `rt_binop_gen@PLT`, reading `pBB->lhs` and `pBB->rhs` (after Step 1)
- c) Build + gates

`icn_every_box` in the same file: check callers — if called only from dead paths,
delete. If still live (e.g. SM_BB_PUMP_PROC path), leave but mark for F-2.

---

## Step 3 — Migrate unary BB kinds (operand field) ⏳

All these use `nd->c[0] = inner` in `lower_icn.c` and `nd->c[0]` in `bb_exec.c`.
Replace with `nd->operand = inner` / `nd->operand`.

Kinds (all single-operand):
`BB_SIZE`, `BB_NOT`, `BB_NONNULL`, `BB_NULL_TEST`, `BB_RANDOM`,
`BB_NEG`, `BB_POS`, `BB_CSET_COMPL`, `BB_CALL` (inner expr),
`BB_RETURN` (retval), `BB_REPEAT` (body), `BB_INITIAL` (body),
`BB_KEY_GEN` (table expr).

**Files to touch per kind (always both together):**
- `src/lower/lower_icn.c` — builder side
- `src/lower/bb_exec.c` — executor side

Do all unary kinds in one commit. Gate: smoke 5/5, rungs PASS≥153.

---

## Step 4 — Migrate binary BB kinds (lhs/rhs fields) ⏳

All use `nd->c[0]=lhs; nd->c[1]=rhs` in `lower_icn.c` and reads in `bb_exec.c`.
Replace with `nd->lhs = lhs; nd->rhs = rhs`.

Kinds:
`BB_ASSIGN`, `BB_SWAP`, `BB_IDENTICAL`, `BB_IDX`, `BB_FIELD_GET`,
`BB_FIELD_SET` (obj+rhs; sval=fieldname), `BB_CSET_UNION`,
`BB_CSET_DIFF`, `BB_CSET_INTER`, `BB_GEN_SCAN` (subj+body),
`BB_LIMIT` (gen+lim), `BB_EVERY` (gen+body),
`BB_WHILE`/`BB_UNTIL` (cond+body),
`BB_IF` (cond; then/else via γ/ω wiring — see Step 4b),
`BB_BINOP` (lhs+rhs; op in ival — already done in F-6d but aug-op
builder in lower_icn.c still uses c[]).

Sub-step **4b — BB_IF special case:**
BB_IF has three children (cond, then, else). cond → `nd->operand`.
Then and else branches are control-flow successors — wire them as
`nd->γ = then_nd; nd->ω = else_nd;` with the cond result driving the jump.
The executor evaluates `nd->operand`, then follows γ on success or ω on fail.

Sub-step **4c — BB_IDX_SET and BB_SECTION (ternary):**
These have three operands (base, idx, rhs) or (base, i1, i2).
Use `nd->lhs = base; nd->rhs = idx; nd->operand = rhs_or_i2` and store
the third value in whichever named field fits. For BB_SECTION the section
kind is already in `nd->ival`.

Gate after each sub-step: smoke 5/5, rungs PASS≥153.

---

## Step 5 — Migrate Prolog BB kinds ⏳

**File:** `src/lower/lower_pl.c` and `bb_exec.c`

Remaining `c[]` uses in `lower_pl.c`:

- `BB_PL_SEQ` — N-statement conjunction. Wire as γ-chain:
  `seq[0].γ → seq[1]; seq[1].γ → seq[2]; ... seq[N-1].γ → outer_γ`.
  No array needed. The BB_PL_SEQ node just holds `nd->operand = first_stmt`
  and each stmt chains via γ to the next.

- `BB_PL_CALL` with args — args already in `g_pl_env[]` slots set by caller;
  the arg BB_t nodes from `lower_pl_term_node` are only needed to evaluate
  the arg expressions. Chain them as a γ-sequence feeding into the call.
  `nd->lhs` = first arg node chain, `nd->sval` = predicate name, `nd->ival2` = arity.

- Clause-body `BB_UNIFY(slot_var, head_ir)` — already migrated to α/β in F-6d
  (Step 0 commit). Verify.

- `nd->c[nd->n++] = blk` in choice builder — each clause body is a `BB_graph_t`
  stored in `blk->opaque`. Chain them: `blk[i].ω → blk[i+1].α`.
  The `BB_CHOICE` node holds `nd->operand = first_clause_bb`.

Gate: Prolog smoke via `test_smoke_unified_broker.sh` PASS≥17.

---

## Step 6 — Migrate emit_bb.c and emit_sm.c ⏳

**File:** `src/emitter/emit_bb.c`

`walk_bb_flat` and `pre_build_children` still use `nd->c[0]`/`nd->c[i]` for:
- `BB_PAT_ARBNO`, `BB_PAT_ASSIGN_IMM`, `BB_PAT_ASSIGN_COND` — pattern nodes.
  These are pre-DCG scratch; after `BB_lower_pat()` converts them to a wired
  graph the `c[]` array is not traversed. Replace `nd->c[0]` with `nd->operand`.
- The SNOBOL4 pattern sequence walk in `pre_build_children` iterates `nd->c[i]`.
  Replace with γ-chain traversal following `nd->γ`.

**File:** `src/emitter/emit_sm.c`

`nd->c[k]` used in BB_CHOICE/PL_SEQ serialiser. Replace with γ-chain walk.

**File:** `src/emitter/BB_templates/bb_builtin.cpp`

`pBB->c[0]` → `pBB->operand` (the single arg node for BB_BUILTIN).

Gate: smoke 5/5, broker PASS≥17, rungs PASS≥153.

---

## Step 7 — Delete c[]/n from BB_t struct ⏳

Only when zero remaining `->c[` references exist on `BB_t` variables (not
`tree_t` variables — those are correct and untouched).

Check:
```bash
grep -rn "nd->c\[\|pBB->c\[\|->c\[" src/lower/bb_exec.c src/lower/lower_icn.c \
  src/lower/lower_pl.c src/emitter/emit_bb.c src/emitter/emit_sm.c \
  src/emitter/emit_core.c src/emitter/BB_templates/ \
  src/runtime/interp/icon_box_rt.c src/lower/scrip_ir.c
# Must be empty (or only tree_t variables)
```

Then remove from `BB.h`:
```c
BB_t        ** c;   /* DELETE */
int            n;   /* DELETE */
```

Remove from `BB_alloc` / `BB_node_alloc` any initialization of `c`/`n`.
Remove `DEPRECATED` comments added in Step 1.

Gate: clean build + smoke 5/5 + broker PASS≥17 + rungs PASS≥153.

---

## Step 8 — Fix augop regression in rungs ⏳

After Step 0 commit, rungs sit at PASS=153 (was 169 before F-6d partial).
The regression is in `TT_AUGOP` lowering in `lower_icn.c` which still allocates
`binop->c[0]=lhs; binop->c[1]=rhs; asgn->c[0]=lhs2; asgn->c[1]=binop` —
but `bb_exec.c` BB_BINOP now reads `nd->lhs`/`nd->rhs` (after Step 4).
Once Step 4 is done, the augop lowering will be fixed as part of BB_BINOP migration.

Verify: `bash scripts/test_icon_all_rungs.sh` should recover to ≥169 after Step 4.

---

## Step 9 — scrip_ir.c debug printer ⏳

`src/lower/scrip_ir.c` line 130 prints `nd->c[j]` child indices for debug.
After Step 7 (c[] deleted), update to walk γ/ω/lhs/rhs/operand instead.
Low priority — can be gutted to just print port addresses.

---

## Invariants throughout

1. `bash scripts/test_smoke_icon.sh` must stay PASS=5 after every step.
2. `bash scripts/test_smoke_unified_broker.sh` must stay PASS≥17.
3. No new `BB_t **c` allocations. No new `nd->n` assignments.
4. `tree_t` uses of `->c[]` and `->n` are CORRECT and UNTOUCHED.
   The grep to check BB_t offences targets only: `bb_exec.c`, `lower_icn.c`,
   `lower_pl.c`, `emit_bb.c`, `emit_sm.c`, `emit_core.c`, `BB_templates/`,
   `icon_box_rt.c`, `scrip_ir.c`.
5. After Step 7: `BB_t` has no `c` or `n` field. Any compile error = missed site.

---

## Done when

- Zero `->c[` or `->n` references on `BB_t` variables in the files listed above.
- `BB_t` struct has no `c` or `n` fields.
- `bash scripts/test_smoke_icon.sh` PASS=5.
- `bash scripts/test_smoke_unified_broker.sh` PASS≥17.
- `bash scripts/test_icon_all_rungs.sh` PASS≥169 (recovered from regression).
- Clean build, no warnings about unused fields.

---

## Notes from 2026-05-25 session (Claude Sonnet 4.6)

**Architecture clarified:**
- `lower()` builds ONE primary structure: `SM_sequence_t` (flat array).
  `BB_graph_t` sidecars hang off it via `sm.bb_table[]`, indexed by integer.
- Labels in JCON irgen.icn = pointers in SCRIP BB graphs. α/β/γ/ω are pointers.
- α/β = **synthesized** attributes (box exposes its own entry points to callers).
- γ/ω = **inherited** attributes (caller tells box where to jump on succeed/fail).
- lhs/rhs/operand = operand sub-boxes; NOT control flow; NOT α/β/γ/ω.
- `c[]`/`n` was tree-child misuse smuggled into graph nodes. Eradicate entirely.

**What was done this session:**
- SM_UNUSED_1..5 rename (was SM_BB_AVAILABLE, before that SM_SLOT_*/DELETED names).
- F-6d partial: BB_BINOP, BB_BINOP_GEN, BB_LCONCAT, BB_ARITH, BB_UNIFY,
  BB_BUILTIN, BB_PL_ALT — all migrated from c[0]/c[1]/n to α/β in
  lower_icn.c + lower_pl.c + bb_exec.c + emit_bb.c + templates.
- Rung regression: 169→153. Root cause: TT_AUGOP lower still allocates
  binop->c[], and other BB kinds not yet migrated. Recovers after Steps 3+4.

**rt_binop_gen status:** Still has 34 c[] uses in icon_box_rt.c. It is a
C Byrd box (forbidden by GOAL-ICON-BB rule). Called from bb_binop_gen.cpp
(x86 emitter template). Delete in Step 2.
