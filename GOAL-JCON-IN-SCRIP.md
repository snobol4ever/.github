# GOAL-JCON-IN-SCRIP.md — Re-found SCRIP's Icon pipeline on JCON's IR. (PIVOT, Lon 2026-06-27)

## ⛔ THE PIVOT — WHY THIS EXISTS

SCRIP's Icon IR/BB was built first, **without `IR_TMP`**, and deferred value-slot bookkeeping to
emit time. Every other language (SNOBOL4, Prolog, …) was then founded on that shape and inherited
its pathology: **operand-source FUSION** (`IR_*_GVAR_*`, `IR_ASSIGN_<src>`, the emit-time `->op`
swaps) — operand provenance baked into the consumer opcode, reconstructed at emit by walking the
graph. That reconstruction IS why the emitter mutates IR (Ground Zero #5's 45 sites).

**JCON has it right.** `tran/irgen.icn` lowers ALL of Icon to a small canonical IR where **every
value lives in a tmp** produced by one node and read by another. No operand-source in any opcode.
The emitter (in JCON, the Java vProc layer) only reads.

**We re-found Icon on JCON's IR**, with exactly ONE deliberate divergence: where JCON has the single
`ir_OpFunction` (operator-as-runtime-function, arity resolved dynamically), SCRIP keeps the
**fine-grained `IR_BINOP` + `IR_UNOP`** split, because SCRIP is a TEMPLATE system (one BB = one
instruction = one template emitting x86 directly) and a per-arity template is cleaner than an
arity branch inside one template. Coercion/resumability are NOT new opcodes (see §AXES).

Icon first. Then Lon spins up each other language session on this same clean, tmp-carrying spine.

---

## ⛔ FROZEN: THE LABEL MODEL (JCON 4-label ir_info ↔ SCRIP 2 x86-labels + 2 IR_ref_t)

JCON: `record ir_info(start, resume, failure, success, x)` — each AST node `p` carries `p.ir`, four
labels. Lower emits `ir_chunk(LABEL, [insns])` — a basic block keyed by one of those four labels.

SCRIP: each `IR_t` BB has FOUR PORTS, **α β γ ω** (Greek, always). TWO are local x86 labels the
template emits; TWO are `IR_ref_t` successor pointers on the node:

| JCON ir_info | SCRIP port | materialization | role |
|---|---|---|---|
| `start`   | **α** | x86 label (box entry, `bb<id>_α`)        | where this box begins |
| `resume`  | **β** | x86 label (`def β`)                       | re-enter for NEXT value |
| `success` | **γ** | `IR_ref_t nd->γ.node` → successor's α     | produced a value → go here |
| `failure` | **ω** | `IR_ref_t nd->ω.node` → successor's α     | no (more) values → go here |

**Mechanical correspondence (this is the whole recipe in three lines):**
- A JCON `ir_X(...)` instruction inside a chunk  →  a SCRIP `IR_X` node in the graph.
- A JCON chunk's LABEL  →  the **α** (or **β**) of the first node of that chunk's node-sequence.
- A JCON `ir_Goto(coord, LABEL)` ending a chunk  →  a SCRIP **γ/ω** successor pointer to LABEL's node.

JCON produces CHUNKS (label + insn list). SCRIP produces TEMPLATES (one `bb_X()` per node, emitting
the box body with α/β local and γ/ω as successor jumps). Same control graph, different surface.

---

## ⛔ FROZEN: THE IR CONTRACT — JCON's set, SCRIP names

From `refs/jcon-master/tran/ir.icn`. `H`=have today, `NEW`=mint, `SPLIT`=our divergence, `?`=decide.
Infra (`ir_chunk`, `ir_operator`, `ir_coordinate`, `ir_info`, the `*Label` value-carriers) is not
an instruction; it maps to SCRIP label/operand plumbing.

| # | JCON `ir_*` | SCRIP `IR_*` | st | note |
|---|---|---|---|---|
| 1 | IntLit | `IR_LIT_I` | H | |
| 2 | RealLit | `IR_LIT_F` | H | |
| 3 | StrLit | `IR_LIT_S` | H | |
| 4 | CsetLit | `IR_LIT_CSET` | NEW | first-class cset literal (sealed bitmap, RIP-rel) |
| 5 | Var | `IR_VAR` | H | |
| 6 | Global | `IR_GLOBAL` | NEW | JCON keeps distinct from Var; we currently fold into VAR+name |
| 7 | Field | `IR_FIELD_GET`/`_SET` | H | |
| 8 | **Tmp** | **`IR_TMP`** | **NEW — KEYSTONE** | the value carrier; every producer writes one, consumer reads it |
| 9 | Key | `IR_KEYWORD` | H | keyword fetch (&subject,&pos,…) |
| 10 | Move | `IR_MOVE` | NEW | tmp→tmp copy (distinct from Assign's lvalue store) |
| 11 | MoveLabel | `IR_MOVE_LABEL` | NEW | load a label value into a tmp (feeds IndirectGoto) |
| 12 | Deref | `IR_DEREF` | NEW | variable → value |
| 13 | Assign | `IR_ASSIGN` | H | Icon `:=` store into lvalue |
| 14 | MakeList | `IR_MAKE_LIST` | ? | `list()` works as builtin today; mint only if `[a,b,c]` needs it |
| 15 | OpFunction | **`IR_BINOP` + `IR_UNOP`** | **SPLIT** | operation = immediate on node; one template per arity |
| 16 | Call | `IR_CALL` | H | |
| 17 | ResumeValue | `IR_RESUME_VALUE` | NEW | resume a suspended closure/generator value |
| 18 | EnterInit | `IR_INITIAL` | H | |
| 19 | Goto | `IR_GOTO` | ? | confirm live; SCRIP mostly uses port jumps not explicit goto nodes |
| 20 | IndirectGoto | `IR_GOTO_DYN` | H | |
| 21 | Succeed | `IR_SUCCEED` | H | |
| 22 | Fail | `IR_FAIL` | H | |
| 23 | Create | `IR_CREATE` | NEW | co-expression create |
| 24 | CoRet | `IR_CORET` | NEW | co-expression activate/produce (`@C`) |
| 25 | CoFail | `IR_COFAIL` | NEW | co-expression fail |
| 26 | ScanSwap | `IR_SCAN_SWAP` | NEW | `?`-scan subject/pos save-restore (today internal to IR_GEN_SCAN) |
| 27 | Unreachable | `IR_UNREACHABLE` | NEW | dead-tail marker (emits ud2/bomb) |
| 28 | Record | `IR_RECORD_DEF` | H | |
| 29 | Function | `IR_PROC` | H | procedure/function def |
| 30 | Invocable | `IR_INVOCABLE` | ? | likely WONTFIX (single-unit model) unless `invocable` kw wanted |
| 31 | Link | `IR_LINK` | ? | likely WONTFIX (single-unit model) |
| 32 | Field(set form) | `IR_FIELD_SET` | H | |
| 33 | (label infra) | α/β + `IR_MOVE_LABEL`/dyn | H | ir_Label/ir_TmpLabel → SCRIP label plumbing |

**NEW to mint (9):** IR_TMP, IR_GLOBAL, IR_LIT_CSET, IR_MOVE, IR_MOVE_LABEL, IR_DEREF,
IR_RESUME_VALUE, IR_CREATE, IR_CORET, IR_COFAIL, IR_SCAN_SWAP, IR_UNREACHABLE.
**DECIDE:** IR_MAKE_LIST, IR_GOTO liveness, IR_INVOCABLE/IR_LINK (WONTFIX candidates).

---

## ⛔ THE AXES — why coercion & resumability are NOT new opcodes (settled with Lon)

- **Operation** (ADD/LT/CONCAT…) → immediate on the ONE `IR_BINOP`/`IR_UNOP` node (JCON's principle).
- **Resumability** (generator vs det) → **ω-WIRING only**. `(1 to 3)+(1 to 2)` enumerates because
  lower points `ω→right.β → (right ω)→left.β → (left ω)→binop.ω`. The template is oblivious. **Proven
  by JCON: `ir_a_Every` and generator-binop emit only `ir_Goto`.** No GEN opcode. (`IR_EVERY`,
  `IR_GEN_BINOP`, `IR_BINOP_GEN`, `flat_drive_binop_gen_tree`, `bb_every`=no-op → all DELETE.)
- **Coercion** (Icon/SNOBOL4 vs Pascal) → **operand REPRESENTATION**: boxed descriptor → coercing
  sink (`rt_num_arith`, shared by Icon+SNOBOL4); unboxed → raw `add`. If Icon/SNOBOL4 ever diverge,
  a **coercion-policy immediate** on the node, switched in the runtime sink — never a language `#ifdef`.

---

## ⛔ THE CONVERSION RECIPE (per JCON `ir_a_<AST>` procedure)

Each JCON `procedure ir_a_X(p, st, inuse, target, bounded, rval)` converts to:
1. **lower_icon arm** for the matching AST token:
   - allocate result/work tmps (`ir_tmp(st,inuse)` → an `IR_TMP` node + a slot id);
   - recursively `lower()` each sub-expression (JCON `suspend ir(p.sub, …, tmp, …)`) → producer
     boxes whose result tmp is known to this arm;
   - build THIS construct's node(s) (`ir_opfn`→`IR_BINOP`/`IR_UNOP`, `ir_Move`→`IR_MOVE`, …);
   - wire the four ports per the chunk structure: the chunk at `p.ir.start` → this box's α; the
     `ir_Goto`s ending each chunk → γ/ω successor pointers; the `p.ir.resume` chunk → β handling.
2. **bb_X templates** (one per canonical IR node touched): read operand tmps' slots
   (`FRQ(off(operand_tmp))`), emit x86 via `x86(...)`, store result to `FRQ(off(node.tmp))`,
   `jmp γ` on success / `jmp ω` on fail. NO `bb_slot_alloc16` at emit — slots come from lower.

**A lower-time TMP pass owns slot assignment** (the keystone): walk the graph, map each `IR_TMP` →
a `[r12+off]` frame offset; stamp the offset where the emitter can read it. The emitter NEVER
allocates a slot or reconstructs a producer→consumer link again. This is what kills F1/F4 → gate 0.

---

## SEQUENCING — keystone first, then the 33

- [ ] **J0 — IR_TMP + lower-time slot pass (KEYSTONE, blocks all else).**
      Mint `IR_TMP`. Add `lower_icon` tmp allocation (every value-producing node gets a result tmp;
      operands reference tmps). Add a lower-time slot-assignment pass (tmp → `[r12+off]`), stamped
      for the emitter. **Done:** `./scrip --dump-ir` shows tmps on nodes; global+global add carries
      `lhs=tmpK, operands=tmpI,tmpJ`; emitter reads `off(tmp)` and calls zero `bb_slot_alloc16`.

- [ ] **J1 — EXEMPLAR: ir_a_Binop end-to-end (proves the recipe).**
      Convert JCON `ir_a_Binop`+`ir_binary` (irgen.icn L472–540) → `lower_icon` IR_BINOP arm
      (tmps + producer boxes + γ/ω/β wiring) + `bb_binop_arith`/`_relop`/`_concat` reading tmp slots.
      **Done:** `i := 2 + 3; write(i)` and `(1 to 3) + (1 to 2)` (9 sums, Icon order) compile 0-bomb
      and run correct, with NO emit-time `->op` swap and NO GVAR opcode in the path.

### The 33 — grind after J0/J1 (each: lower arm + bb template(s) + a one-line run test)
Group A — literals & storage:
- [ ] IR_LIT_I  - [ ] IR_LIT_F  - [ ] IR_LIT_S  - [ ] IR_LIT_CSET(NEW)
- [ ] IR_VAR  - [ ] IR_GLOBAL(NEW)  - [ ] IR_FIELD_GET  - [ ] IR_FIELD_SET  - [ ] IR_KEYWORD
Group B — value movement:
- [ ] IR_TMP(J0)  - [ ] IR_MOVE(NEW)  - [ ] IR_MOVE_LABEL(NEW)  - [ ] IR_DEREF(NEW)  - [ ] IR_ASSIGN
Group C — operations & calls:
- [ ] IR_BINOP(J1)  - [ ] IR_UNOP  - [ ] IR_CALL  - [ ] IR_RESUME_VALUE(NEW)
Group D — control & goal-direction:
- [ ] IR_GOTO(?)  - [ ] IR_GOTO_DYN  - [ ] IR_SUCCEED  - [ ] IR_FAIL  - [ ] IR_UNREACHABLE(NEW)
- [ ] IR_INITIAL
Group E — structure:
- [ ] IR_MAKE_LIST(?)  - [ ] IR_RECORD_DEF  - [ ] IR_PROC  - [ ] IR_INVOCABLE(?)  - [ ] IR_LINK(?)
Group F — co-expressions & scan:
- [ ] IR_CREATE(NEW)  - [ ] IR_CORET(NEW)  - [ ] IR_COFAIL(NEW)  - [ ] IR_SCAN_SWAP(NEW)

### After the 33 are clean — demolish the old fused shapes
- [ ] DELETE wiring-as-opcode no-ops (`IR_EVERY`/`bb_every`, audit `IR_LIMIT`/`IR_REPALT`/`IR_SEQ`).
- [ ] DELETE fusion opcodes + templates (`IR_*_GVAR_*`, `IR_ASSIGN_<src>`, `IR_BINOP_ARITH/_RELOP/_CONCAT`,
      GEN-binop) once everything routes through the tmp-carrying generic nodes.
- [ ] Gate `test_gate_emit_no_ir_mutation.sh --strict` reads 0.

---

## DO NOT
- Do NOT attempt all 33 in one session — freeze the contract, grind per-rung, test each.
- Do NOT allocate slots or reconstruct producer→consumer at emit time — that is J0's whole point.
- Do NOT encode operand-source, coercion, or resumability in an opcode — node immediate / repr / ω-wiring.
- Do NOT add a per-language fn to emitter/templates — language lives in parser + lower ONLY.

## Watermark

## ⌚ 2026-07-19 (Claude Sonnet 4.6 · SCRIP `f5898e83` · corpus `fd381248`) — banggen + pos fixes; jtran 17-module 0-bomb link; ucode rc=0; one blocker left; LIVE CURSOR below
**LIVE CURSOR — NEXT SESSION START HERE.**
Two fixes landed (`f5898e83`). Board: Icon 252/9/32 (identical to cursor baseline; zero regressions). Smoke 14/14×2, SN4 7/7, Prolog 5/5. Gates no_stack/one_reg/semicolon PASS. jtran **17-module** canonical TRANSRC merge (do_ops+interface generated by SCRIP-compiled oplexgen/interfacegen): **0 bombs, links (4.97MB), ucode pipeline rc=0 (no Error 5)**. Prior item (A) m3 116M-line spin: CURED (do_ops fixed by banggen). Prior item (C) empty ucode files: PARTIALLY CURED (rc=0, no crash) but `.u1/.u2` still 0 bytes — one blocker remains. Item (B) bc_File JVM-class: WONTFIX (loadfunc / single-unit model). **ONE OPEN BLOCKER:** yylex's `@coexpr` inside a generator whose `suspend` crosses a live `s?{}` scan frame re-reads the first value forever (R8 minimal 20-line repro). Root cause confirmed read-only: `scan_subj`/`scan_pos` are globals; `rt_coexpr.c` does NOT save/restore scan state on coexpr switch; real Icon requires `&subject`/`&pos` per-co-expression. Fix: save/restore scan state in rt_coexpr.c's switch path (+ possibly ensure IR_SCAN leave runs on generator suspend-exit). Full bracket, R8/R9/R10 discriminators, and fix-shape in `FINDING-2026-07-19-CLAUDE-JCON-SELFHOST-POS-BANGGEN-FIXES-YYLEX-PUMP-BLOCKER.md`. **NEXT: fix per-coexpr scan state in rt_coexpr.c → retest R8 → retest ucode pipeline → self-host byte-compare vs iconx-jtran → 4-way bench.**

## ⌚ 2026-07-19 (Claude Fable 5 · SCRIP `b6363a50` · corpus `547d67d6` · .github `cd5280b4`+this) — jtran LINKS + RUNS; five fixes; two pipeline blockers pinned
**Practical track continued.** Merge compile now **0 bombs** and **LINKS** (4.4MB binary) under `SCRIP_BETA_ELIDE_OFF=1`. The prior finding's 183-labels + 1-bomb were ONE surface (177 `bb_assign_local` bombs, control-node rhs on `__case_result`). Five fixes in `b6363a50`: pair-array cap 32→1024+guard (17-arm DISJUNCTION SEGV); TT_CASE `icn_arm_result` filter; `emit_chain_operand_refs` stack-sim backfill no longer rides control nodes (a 45-mangle-sites specimen, gdb-caught); case return-arm keeps its exit edge (corpus lock `rung14_case_return_arm`); **proc/1** + proc() descriptor → canonical `rt_proc_value(name)` (entry_pc form misresolved to 'main' under stackless). Board: Icon rungs FAIL 9→7 (scan2+var flipped PASS, zero regressions), smokes+3 gates green. **BLOCKED on two runtime gaps, micro-repro'd in `FINDING-2026-07-19-CLAUDE-JCON-SELFHOST-FIVE-FIXES-TWO-PIPELINE-BLOCKERS.md`:** (A) β-elision scan gap (one label; hatch = sanctioned baseline); (B) coexpr pipeline — m4 create-through-proc()-descr loses the first `@` (p8 10-line repro, m3 works), m3 full pipeline spins ~116M empty lines (preprocessor proven correct in isolation). NEXT: fix B (m4 in-thread descr-call path first — the GZ-10 slab hint), then self-host byte-compare vs iconx-jtran (Arizona icont/iconx already built this sandbox), then the 4-way bench. **Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet

## ⌚ 2026-07-18 (Claude Sonnet · SCRIP `2e8c7788` · corpus `c6cd5ee9` · .github `2ef09762`+this) — the ACTUAL JCON compiler sources now parse 18/18 and near-compile; sources checked into corpus
**Scope (practical track, distinct from the J0/J1 IR-TMP pivot below — that remains a parallel session's):** got the real JCON translator (`refs/jcon-master/tran/*.icn`, 15 modules + 3 utilities, ~10K lines) parsing and compiling under SCRIP. **Landed (SCRIP `2e8c7788`):** three Icon parser fixes verified against canonical `jcon-master/tran/parse.icn` — (1) prefix-`.` dereference (`TT_DEREF` + lower arm mirroring TT_RANDOM), (2) position-free `case` default (stashed during clause loop, pushed last → preserves lower's trailing-odd-child convention; matches irgen `ir_a_Case` p.dflt), (3) canonical `break`-operand rule (new `icn_begins_nexpr` predicate = jcon `nexpr_set`/Beginner set, superseding two hand-maintained blocklists that mis-parsed `break` before `}`/`|`); plus `ZLS_MAX_GRAPHS` 256→4096 (369-proc program overflowed it). **MEASURED zero-regression:** Icon rung suite **242/15/32** (identical to baseline), Icon smoke 14/14 ×2, all 4 Icon gates green, SNOBOL4 smoke 7/7, Prolog 4/5 (≥ pre-existing). **Sources checked into corpus** (`c6cd5ee9`, `programs/icon/jcon-compiler/`): 18 semicolonized modules (semicolons added at icont's Beginner/Ender points — SCRIP requires `;`, pure Icon doesn't; one-time conversion done by our own tool) + JCON COPYRIGHT + README + NOTICE entry; preprocessor.icn's undefined `$ifdef _MACINTOSH` block dropped as JCON's build does; no `.s`/`.j` (RULES.md). **STATE:** merged 15-module compile emits ~451,520 lines asm (rc=0) with exactly **ONE** `bb_assign_local` bomb; **link BLOCKED by 183 undefined refs, ALL one class** `xchainN_nN_α` (BB alpha-labels referenced but not emitted — a single walk-bug: contiguous node span emits zero ports while neighbors emit fine; type-dispatch/disjunction arm that is also a generator-β resume target; the IR_MOVE_LABEL/DISJUNCTION "label-indirection not walked" family). **Full diagnosis + repro path in `FINDING-2026-07-18-CLAUDE-JCON-COMPILER-PARSES-LINK-BLOCKED-MISSING-LABEL-CLASS.md`.** NEXT: repro the missing-label bug from the xchain1259 shape, fix the emit walker's successor-enqueue (one fix clears all 183 → should link); then the single bb_assign_local node. **Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet

**PIVOT opened 2026-06-27.** Contract + label model + recipe FROZEN above (verified vs ir.icn,
irgen.icn, and src/contracts/IR.h `IR_t`). No code landed yet. Next rung: **J0 (IR_TMP + lower
slot pass)** — the keystone everything else blocks on. SCRIP HEAD at pivot: e2f1d61b. Gate: HARD=45.
