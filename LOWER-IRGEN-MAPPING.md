# LOWER-IRGEN-MAPPING.md — JCON `irgen.icn` → SCRIP `lower_icn_new.c`

**Authoritative contract for LFJ rungs.** Every `ir_a_*` transcription consults this
document. Drift from this mapping is the failure mode that killed the previous four
attempts. If a transcription cannot be expressed via the mappings below, STOP and
extend this document first — then transcribe.

**JCON sources:** `/tmp/jcon-master/tran/ir.icn` (record definitions) and
`/home/claude/corpus/programs/icon/jcon-ref/irgen.icn` (procedures).

**SCRIP targets:** `src/lower/lower_icn_new.c` + `src/include/BB.h` (read-only here).

---

## 1. The shape mismatch

JCON's IR is a **flat chunk graph**: labeled blocks of straight-line instructions
connected by explicit `ir_Goto(coord, targetLabel)` jumps. Labels are first-class
records (`ir_Label(value)` / `ir_TmpLabel(name)`). Each AST node carries an `ir_info`
record with four labels (start, resume, failure, success) representing its four
entry/exit points. The translator `suspend`s `ir_chunk(label, [insns...])` records
into a global stream which the linker concatenates.

SCRIP's IR is a **port graph**: `BB_t` nodes connected by direct pointers in the four
port fields (α, β, γ, ω). No labels at the lowering layer. No flat instruction stream.
A lowerer returns a single `BB_t *` (the apply node) whose ports point at peer nodes.

The transcription rule is: **a JCON label becomes a `BB_t *`. A JCON `ir_Goto(_, L)`
becomes a port assignment that points at the node corresponding to L.** Instructions
inside a chunk become fields on the `BB_t` (for the apply box's payload) or peer
`BB_t` nodes wired into the chunk's CFG (for sub-operations).

---

## 2. The four labels ↔ four ports

JCON `ir_info` record:
```icon
record ir_info(start, resume, failure, success, x)
```

| JCON label | SCRIP port | Direction | Meaning |
|---|---|---|---|
| `start`   | **α** | synthesized UP   | fresh-entry of this node's subgraph |
| `resume`  | **β** | synthesized UP   | retry-entry (self if resumable, else = `ω_in`) |
| `success` | **γ** | inherited DOWN   | success continuation (where to go on yield) |
| `failure` | **ω** | inherited DOWN   | failure continuation (backtrack / outer fail) |

**Read this carefully.** JCON uses these names as *labels you jump to*. SCRIP uses
them as *pointers you store in the node*. The semantic correspondence is exact, but
the directionality matters:

- In JCON, `p.ir.start` is the label you `Goto` to enter `p`. After lowering, the
  apply node has been written to chunk `p.ir.start`'s label, so jumping there enters
  the construct. In SCRIP, the lowerer's return value IS the address of the apply
  node — that pointer is α (a pointer the caller stores to its own γ to enter `p`).
- In JCON, `p.ir.failure` is a label provided by the caller (the loop, the `if`,
  the conjunction sibling — whoever is consuming `p`'s failure). The caller passes
  it as the `failLabel` argument to `ir_opfn`, etc. In SCRIP, that same address is
  the `ω` port passed down through the lowerer's signature (`ω_in`).

The lowering signature in SCRIP is therefore:
```c
BB_t *lower_icn_new_<Kind>(BB_graph_t *cfg, tree_t *e,
                           BB_t *γ_in, BB_t *ω_in,
                           BB_t **α_out, BB_t **β_out, int bounded);
```

| Param | JCON correspondent |
|---|---|
| `cfg`      | implicit (chunks emitted into global stream)        |
| `e`        | `p` (the AST node)                                  |
| `γ_in`     | `p.ir.success` (a label provided by caller)         |
| `ω_in`     | `p.ir.failure` (a label provided by caller)         |
| `α_out`    | `p.ir.start` (lowerer reports back its entry)       |
| `β_out`    | `p.ir.resume` (lowerer reports back its retry)      |
| `bounded`  | `bounded` (literally the same argument)             |

`α_out` / `β_out` are out-parameters because in JCON the labels exist *before* the
chunks are emitted (created by `ir_init(p)` at the top of every `ir_a_*`); in SCRIP
the `BB_t *` exists *after* the apply node is allocated. The lowerer therefore
returns its own α/β via out-params, and (per the existing `lower_icn_expr_threaded_b`
convention) returns the apply node directly as the function's return value (which the
caller assigns to its own γ when wiring its predecessor).

`bounded == 1` means the consumer of this expression cannot resume it (statement
position, `if` condition, etc.). When `bounded == 1`, β_out = ω_in (no retry —
failure directly resumes the outer ω). When `bounded == 0`, the kind decides:
generators set β_out = self (the apply node), non-generators set β_out = ω_in.
See `icn_kind_is_resumable` in `bb_exec.c` for the current SCRIP table.

---

## 3. The ir_info other field

```icon
record ir_info(start, resume, failure, success, x)
                                                ^
                                          construct-specific
```

The `x` field holds construct-specific state. For loops it's an `ir_loopinfo`
(scan level, next-label, continue-label, etc.). For scan it's an `ir_scaninfo`. In
SCRIP these are folded into BB_t's payload fields:

| JCON `x` field      | SCRIP `BB_t` field                                       |
|---|---|
| loop counter        | `nd->counter` (int64)                                    |
| loop-state flag     | `nd->state` (int)                                        |
| stored value        | `nd->value` (DESCR_t)                                    |
| literal int payload | `nd->ival`                                               |
| literal real payload| `nd->dval`                                               |
| string payload      | `nd->sval`                                               |
| break/next labels   | walker-side via `FRAME.loop_break` / `FRAME.loop_next`   |
| scan save/restore   | walker-side via `FRAME.scan_*` (existing scaffolding)    |

**Do NOT add fields to `BB_t`.** PEERS rule, HQ Invariant 17. Anything that doesn't
fit must use the sidecar `BB_graph_t.operand_aux` keyed by `BB_t *`.

---

## 4. JCON record → SCRIP `BB_op_t`

Each JCON instruction record maps to one SCRIP `BB_op_t` enum value (or, for compound
instructions, decomposes into a chain of SCRIP boxes).

| JCON record | SCRIP `BB_op_t` | Notes |
|---|---|---|
| `ir_chunk(label, insnList)`     | (no direct mapping — chunks are JCON-only artifact of flat stream)   | A chunk is just the body reachable from `label`. In SCRIP that body is the BB subgraph hung off the corresponding `BB_t *`. |
| `ir_Label(value)`               | (no direct mapping — labels are pointers in SCRIP)                   | When JCON allocates a label via `ir_label(p, suffix)`, SCRIP allocates a `BB_t` (or uses an existing one as the target). |
| `ir_TmpLabel(name)`             | (no direct mapping)                                                  | Temporary labels become fresh `BB_t *` allocations. |
| `ir_Goto(coord, targetLabel)`   | (no direct mapping — port assignment)                                | `chunk(L) → Goto(M)` ≡ `node_at_L->γ = node_at_M` (or `->ω`, depending on which port the goto represents in context). |
| `ir_IndirectGoto(_, tmpLabel)`  | `BB_GOTO_INDIRECT` (does this exist? if not, defer)                  | TmpLabels are runtime-loaded. Used by `next` / `break` to return through a stored continuation. Existing SCRIP scaffolding uses `FRAME` flags — keep that until a real test forces the issue. |
| `ir_IntLit(coord, lhs, val)`    | `BB_LIT` (existing kind)                                             | `nd->ival = val`. `lhs` ≡ the `nd->value` slot. |
| `ir_RealLit(coord, lhs, val)`   | `BB_LIT_R` (or `BB_LIT` with real marker — verify in bb_exec.c)      | `nd->dval = val`. |
| `ir_StrLit(coord, lhs, len, val)`| `BB_LIT_S`                                                          | `nd->sval = val`, `nd->ival = len`. |
| `ir_CsetLit(coord, lhs, len, val)`| `BB_LIT_C`                                                         | Cset payload. |
| `ir_Var(coord, lhs, name)`      | `BB_VAR`                                                             | `nd->sval = name`. |
| `ir_Key(coord, lhs, name, failLabel)` | `BB_KEYWORD`                                                   | Icon keywords (&pos, &subject, ...). `nd->sval = name`. `failLabel` = ω_in. |
| `ir_Move(coord, lhs, rhs)`      | `BB_ASSIGN`                                                          | lhs is a `BB_VAR` peer; value source is whoever's `nd->value` last on the chain. |
| `ir_MoveLabel(coord, lhs, label)` | (rare — defer until needed)                                        | Stores a continuation pointer. Used in loops with `break` targets. |
| `ir_Deref(coord, lhs, value)`   | `BB_DEREF` (or inline — verify)                                     | Force-evaluate a variable reference into its value. |
| `ir_Assign(coord, target, value)` | `BB_ASSIGN_LV`                                                      | Icon `:=` where target is an lvalue, not just a name. |
| `ir_MakeList(coord, lhs, valueList)` | `BB_LIST_NEW` / `BB_MAKE_LIST`                                  | List constructor `[...]`. |
| `ir_Field(coord, lhs, expr, field, failLabel)` | `BB_FIELD`                                              | `obj.field` access. `failLabel` = ω_in. |
| `ir_OpFunction(coord, lhs, fn, argList, failLabel)` | `BB_CALL` (with builtin fn) or `BB_BINOP`                | The workhorse. For unary `!` (generators), the call enters via α and resumes via β. For binops, it's a single-shot apply. The lowerer decides based on `fn`'s arity and resumability. |
| `ir_Call(coord, lhs, fn, argList, failLabel)` | `BB_CALL`                                                 | User-defined procedure call. |
| `ir_ResumeValue(coord, lhs, value, failLabel)` | `BB_RESUME`                                              | Tell a generator to produce its next value. |
| `ir_EnterInit(coord, startLabel)` | (procedure-prologue only)                                          | Wires the procedure's initial entry. Built by `lower_icn_proc_body`, not by `ir_a_*` procedures. |
| `ir_Succeed(coord, expr, resumeLabel)` | (procedure-epilogue only)                                     | `return expr` from a procedure. Maps to `BB_RETURN`. |
| `ir_Fail(coord)`                | `BB_FAIL` (existing kind)                                            | Unconditional failure. |
| `ir_Create(coord, lhs, coexpLabel)` | `BB_COEXP_CREATE`                                                | Co-expression creation. |
| `ir_CoRet(coord, value, resumeLabel)` | `BB_COEXP_RETURN`                                              | Yield from a co-expression. |
| `ir_CoFail(coord)`              | `BB_COEXP_FAIL`                                                      | Co-expression failure. |
| `ir_ScanSwap(coord, subject, pos)` | `BB_SCAN_SWAP`                                                    | Push/pop &subject / &pos around a `?` scan. |
| `ir_Unreachable(coord)`         | (assertion-only — no SCRIP equivalent needed; assert(0) in walker)   | JCON emits these to mark dead code that the optimizer should never reach. |

**Validation requirement before any LFJ rung touches a record above:** confirm the
`BB_op_t` enum entry exists in `src/include/BB.h` *and* has an executor case in
`src/lower/bb_exec.c`. If not, that's a deferred kind — its rung is blocked until
the BB family lands. Do not invent new `BB_op_t` values mid-LFJ.

---

## 5. Helper procedures (irgen.icn) → C helpers

JCON uses small helper procedures repeatedly. Each is a single C function:

| JCON | Purpose | SCRIP C |
|---|---|---|
| `ir_init(p)`              | allocates the four labels on `p.ir`              | (no direct equivalent — the lowerer is itself the "init") |
| `ir_init_loop(p, ...)`    | `ir_init` + allocates `ir_loopinfo`              | Stack-allocated locals in the lowerer; nothing on `BB_t` |
| `ir_label(p, suffix)`     | allocates a labeled `ir_Label`                    | `BB_node_alloc(cfg, BB_NOOP)` for control-only junctions |
| `ir_tmp(st, _)`           | allocates a unique tmp name `tmp1`, `tmp2`, ...   | Not needed — SCRIP uses `nd->value` directly |
| `ir_tmploc(st, _)`        | allocates a unique label name `loc1`, `loc2`, ... | Not needed |
| `ir_chunk(L, insns)`      | emit a labeled chunk                              | Build the BB subgraph; `L` is the BB_t at the entry |
| `ir_coord(\p.coord)`      | extracts source coord                             | Currently unused in SCRIP (no debug info pass yet) |
| `ir_coordinate("",0,0)`   | placeholder coord                                 | Same — ignore |
| `ir_binary(...)`          | shared binary-op skeleton                         | Helper C function `static BB_t *lower_binary_skel(cfg, e, ...)` |
| `ir_unary(...)`           | shared unary-op skeleton                          | Helper C function `static BB_t *lower_unary_skel(cfg, e, ...)` |
| `ir_conjunction(...)`     | `&` conjunction lowering                          | This IS `ir_a_Conj` essentially — keep as helper if used elsewhere too |
| `ir_value(...)`           | lower an rval expression to a value-producing chunk | Helper C function — every `ir_a_*` that needs a value calls this |
| `ir_rval(...)`            | adjust an operator for rval/lval context          | Inline into call site — small enough |
| `ir_opfn(...)`            | emit an `ir_OpFunction` with failLabel            | Inline — it's just `BB_CALL` allocation + arg wiring |
| `ir_traverse(...)`        | walk operand subgraphs                            | The chain-walking is now the BB executor's job, not the lowerer's |

---

## 6. The `inuse`, `target`, `rval` arguments

Every `ir_a_*` takes `(p, st, inuse, target, bounded, rval)`. SCRIP's lowering
signature does not carry `inuse`, `target`, or `rval`. Why:

- **`inuse`** is JCON's set of currently-live temporary names. SCRIP doesn't allocate
  named temps — values live in `nd->value` on the producing node, read via the
  cfg ring (`ag_ring_peek`) by the consumer. No `inuse` needed.
- **`target`** is JCON's destination for the produced value — a tmp name. The
  caller hands it down; the lowerer writes the value there. SCRIP's equivalent:
  the chain walker pushes `nd->value` to the ring after success; the consumer
  reads from the ring. The "target" is implicit in the chain ordering. The
  legacy `lower_icn_expr_node` uses `nd->α` / `nd->β` as operand pointers; the
  AG-PURE work moved that to the ring. **LFJ uses the ring exclusively** — no
  operand pointers on `BB_t`.
- **`rval`** tells the lowerer to dereference (force) the result. SCRIP currently
  handles this at `BB_VAR` execution time (frame-slot lookup is implicit deref).
  When LFJ encounters a JCON `ir_rval` call, it is either a no-op for SCRIP or
  emits a `BB_DEREF` peer — decide per-construct, document the decision in this
  file when it arises.

**Net effect:** SCRIP's lowering signature is simpler than JCON's. The mechanical
arguments JCON carries to manage its flat stream are unnecessary in port-graph land.

---

## 7. Dispatch (the LFJ machinery)

`src/lower/lower_icn_new.h` declares:
```c
typedef BB_t *(*lower_icn_kind_fn_t)(BB_graph_t *cfg, tree_t *e,
                                     BB_t *γ_in, BB_t *ω_in,
                                     BB_t **α_out, BB_t **β_out, int bounded);
extern lower_icn_kind_fn_t lower_kind_table[TT_MAX];
void lower_kind_table_init(void);
```

`lower_icn_expr_node(cfg, e)` (in `lower_icn.c`) becomes:
```c
BB_t *lower_icn_expr_node(BB_graph_t *cfg, tree_t *e) {
    if (!cfg || !e || e->t < 0 || e->t >= TT_MAX) return NULL;
    lower_icn_kind_fn_t fn = lower_kind_table[e->t];
    if (!fn) return NULL;
    BB_t *αo = NULL, *βo = NULL;
    return fn(cfg, e, NULL, NULL, &αo, &βo, 0);
}
```

`lower_icn_expr_threaded_b` similarly thins to dispatch + the existing AG-PURE
intercepts (preserved until LFJ-15 sweeps them out). LFJ-1a/1b/1c get this all in
place before any `ir_a_*` is transcribed.

Each LFJ rung adds a new `lower_icn_new_<Kind>(...)` and overrides the table slot
in `lower_kind_table_init()` to point at it instead of `lower_icn_legacy_<Kind>`.
The legacy function stays compiled (unused) until LFJ-15.

---

## 8. Validation per rung

The contract is: **rungs 198 PASS, before and after each table flip.** No comparator.
No shadow graph. The 198 rungs are the spec.

If a rung's table flip drops the count, options are:
1. Revert the table flip (one-line change), diagnose, retry.
2. The legacy function and the new function are not behaviourally equivalent — the
   new one is wrong. Re-read the `ir_a_*` procedure. Re-read this mapping doc.
   Fix the new function. Flip again.

**Drift detection:** the moment a transcription produces something that doesn't fit
sections 2–6 above (e.g., wants to add a new `BB_op_t`, or store something
discriminator-shaped on `BB_t`), STOP. Update this document with the missing case
first, get sign-off, then proceed. Discriminator markers in `nd->ival` (the
"deep-threaded" flag from 2026-05-27, the "ag"/"ai"/"ar" sval tags from AG-PURE 8.2,
the `nd->ival = 1` BB_EVERY passthrough flag from AG-PURE 8.1) are the **anti-pattern
this doc exists to prevent.**

---

## 9. Open questions (resolve before the rung that needs them)

These are deliberately unresolved here. The first LFJ rung that touches each item
must consult and update this section.

- **Q1 (LFJ-3, literals):** Is `BB_LIT` polymorphic over int/real/string/cset, or
  are there separate `BB_LIT_R` / `BB_LIT_S` / `BB_LIT_C` kinds? Read `BB.h`.
- **Q2 (LFJ-5, binop):** Where does `BB_BINOP` get its op-code today (TT_ADD vs
  TT_SUB, etc.)? Currently `nd->sval` carries it. Is that a discriminator violation?
  Probably yes — sval is supposed to be IR payload, but op-code on a generic BB_BINOP
  *is* discriminator-shaped. LFJ-5 may need separate `BB_ADD`/`BB_SUB`/... kinds.
- **Q3 (LFJ-7, ToBy):** The AG-PURE 8.2 work added sval `"ag"`/`"ai"`/`"ar"` markers
  for dynamic vs static, int vs real. LFJ replaces this with clean per-kind dispatch.
  The new `lower_icn_new_ToBy` should produce a clean `BB_TO_BY` whose mode is
  encoded structurally, not via sval. Verify how the executor reads mode — adjust
  if needed.
- **Q4 (LFJ-8, Every):** The AG-PURE 8.1 work uses `nd->ival = 1` as the "passthrough"
  marker. LFJ removes this. The new `lower_icn_new_Every` builds a clean BB_EVERY
  whose executor branch is selected structurally (e.g., presence/absence of α/β/γ).
- **Q5 (LFJ-9, Compound):** JCON's `ir_a_Compound` and `ir_a_ProcBody` set up the
  proc frame and the stmt chain. SCRIP currently does this in `lower_icn_proc_body`.
  Does that function get rewritten too, or does it stay legacy and just call into
  `lower_icn_new_<Kind>` per stmt? The latter is simpler — proc_body is plumbing,
  not an `ir_a_*` procedure. Leave proc_body alone; LFJ-9 may be a no-op if Compound
  itself is just a stmt-chain wrapper.

---

## 10. References

- `irgen.icn` — the procedures to transcribe (1559 lines, in `corpus/programs/icon/jcon-ref/`).
- `ir.icn` — the record definitions (`/tmp/jcon-master/tran/ir.icn`).
- `LOWER-REWRITE-FROM-JCON.md` — the directive document (this file's parent).
- `GOAL-ICON-BB.md` — the LFJ staircase (this file's caller).
- `RULES.md` — TEMPLATE-ONLY EMISSION, NO C BYRD-BOX FUNCTIONS, FOUR GREEK PORTS, PEERS RULE.

---

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7
