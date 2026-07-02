# GOAL-IR-IMMUTABLE-EMIT.md — The emitter READS IR. It NEVER mutates it. (Ground Zero #5)

## ⛔⛔ HARD RULE — ICON ONLY. IGNORE EVERY `lower_*.c` WHERE `* != icon` (Lon, 2026-06-30)
**This goal touches `src/lower/lower_icon.c` and Icon-reachable code ONLY. Do NOT read, open, grep into,
reason about, "clean up," or edit `lower_snobol4.c`, `lower_raku.c`, `lower_prolog.c`, `lower_common.c`'s
per-language arms, or ANY non-Icon frontend/lowerer. They are PARKED — already broken pending their own
GZ#5 rebuilds (not started), by directive — and they reference a wholesale-dead pre-GZ#5 IR vocabulary
(`IR_SEQ`, `IR_PATTERN_*`, `IR_DTP_ASSIGN`, `IR_ALT`, … — none in the current `IR_e`). They are NOT in the
Makefile build. Their stale enum references are INERT and are NOT this goal's concern; "fixing" or even
auditing them is wasted effort and a scope violation.**
- **The ONLY files in scope:** `src/lower/lower_icon.c`, `src/emitter/emit.cpp` (+ `emit.h`, Icon-reachable
  templates `src/templates/bb_*.cpp`), `src/contracts/IR.h`/`scrip_ir.c`, `src/opt/ir_query.c`, the Makefile
  template list, and the Icon corpus/smoke. Nothing else.
- **If a dead enum member (e.g. `IR_ALT`) lingers in a parked non-Icon file, LEAVE IT.** It compiles nowhere,
  ships nowhere, and singling it out is theater. Purge such names ONLY from LIVE, build-included, Icon-reachable
  code (e.g. the `emit.cpp` chain-BFS) — which is done.
- **When in doubt whether a file is in scope:** if its name is not `lower_icon.c` and it is not reached when
  compiling an Icon program through `emit.cpp`, it is OUT. Move on.

## ⛔⛔ HARD RULE — ICON-ONLY TEST EXECUTION. DO NOT RUN ANY NON-ICON LANGUAGE TEST (Lon, 2026-06-30)
**Do not run, invoke, or cite any non-Icon test/smoke/gate — not as setup, not as a sanity check.** Stricter than the scope rule above: don't *execute* another language's test at all. Those frontends are PARKED; their FAILs are pre-existing noise this goal does not pay for.
- **FORBIDDEN:** `test_smoke_prolog.sh`, `test_smoke_snobol4*.sh`, `test_smoke_raku*.sh`, `test_smoke_unified_broker.sh` (cross-language), any `scripts/test_*` whose name contains `prolog`/`snobol4`/`raku`/`rebus`/`snocone`/`pascal`, and any other-language line inherited from another doc's Session Setup (GOAL-ICON-BB.md's `test_smoke_prolog.sh` line does not apply to this goal).
- **PERMITTED (shared build steps, not tests):** `make scrip` / `make libscrip_rt`, cloning the SPITBOL `x64` oracle, and anything named `test_*icon*` / `test_gate_icn_*` / `test_smoke_icon.sh`.
- **THE ONLY GREEN SIGNALS THIS GOAL READS:** `scripts/test_smoke_icon.sh` (12 programs ×2 modes) · `scripts/test_icon_all_rungs.sh` (289-program corpus) · the four `test_gate_icn_*.sh` discipline gates · `scripts/test_gate_emit_no_ir_mutation.sh` · `scripts/audit_jcon_wholesale.sh` (66 probes, icont-oracle 4-way — the per-rung instrument).
- **COMPLETION TEST:** zero non-Icon test invocations in the session's tool-call history; if one ran anyway, its output is not cited as evidence.
## ⛔⛔ STANDING DIRECTIVE (Lon, 2026-06-28) — WHOLESALE JCON-IN-SCRIP, ICON-ONLY
We are doing a complete wholesale rewrite of the Icon LOWER + EMITTER to mirror JCON
(`refs/jcon-master/tran/`) construct-by-construct, because JCON has it CORRECT. Same IR as JCON's `ir.icn`
EXCEPT SCRIP keeps fine-grained `IR_BINOP`/`IR_UNOP` instead of one `ir_OpFunction`. **EVERYTHING ELSE IS
DEFERRED** (old TRACK A/B/C ladder, IRM numbering, the pre-pivot opcode-collapse plan) — go straight to the
JCON spine, one TT at a time, per the CONVERSION PLAYBOOK below.
- **`.s` byte-identity is NOT a gate, ever** (Lon, repeated 4×). The `.s` is the honest current output and
  will keep changing drastically. Never wire it into a gate.
- **No full regression required per rung.** Icon regression may go to zero and grow back; breaking other
  languages mid-ladder is authorized (they are already broken pending their own GZ#5 rebuild — not started).
- **No micro "baseline gate."** The old two-snippet sanity gate (`write("hello world")` + `write(1+1)`,
  both modes) is RETIRED (Lon, 2026-06-30) — it tested almost nothing and was never a script, only this line.
  The honest per-rung signal is `bash scripts/test_smoke_icon.sh` (12 programs, both modes) plus the corpus
  stash/rebuild/FAIL-set diff for the rung you touched; each TT is its own honest pass/fail — land it,
  document it precisely, move on. **Icon-only, full stop — see the ICON-ONLY TEST EXECUTION hard rule at the
  top of this file; do not run a non-Icon smoke to "double-check" anything.**
- **`IR_t.tmp` IS the temporary slot** (not `lhs`; no `IR_TMP` opcode — see CONVERSION PLAYBOOK). Only
  value-producers carry one (`ir_node_produces_value`); control/effect ops don't.

## ⛔⛔ ORIENTATION SYNOPSIS — read this instead of the six docs PLAN.md's session-start sends you to
**Everything load-bearing from `ARCH-ICON.md`, `ARCH-x86.md`, `REGISTER-LAYOUT.md`, `ARCH-SCRIP.md`,
`REPO-SCRIP.md`, and `CORPUS-LOCATIONS.md`, distilled in one place by someone who already read all six this
session — so the next session doesn't have to.** Skip those six for routine work on this goal; open one only
if a specific question genuinely isn't answered here.

**The four-port model (Byrd box).** Every construct = α(start, fresh entry) β(resume, ask for next value)
γ(success, value ready) ω(fail, exhausted). A relop is a 0-or-1-result generator, not a boolean (canonical
Icon `cmplte`: `return y` / `fail`). γ/ω are `IR_t` edges; α/β are positions the chain-BFS discovers from
edges pointing AT a node (see CONVERSION PLAYBOOK above for the full isomorphism). Resumability is ω-wiring
only — see DIVISION RULE below; never a stored flag.

**Stackless boxes.** No value stack, no `r12`-as-TOS, no `rt_push/pop`. RW state lives in the ONE per-glob ζ
frame `[r12+off]` (established once by the glob preamble, `mov r12, rdi`). RO compile-time constants (cset
literals, baked pointers) sealed adjacent, reached `[rip+disp]`. Recursion/re-entry = a fresh per-α-entry
DATA linkage, never a stack push — CODE is shared and reusable, DATA is per-invocation. Never jump into the
middle of a blob from outside; every cross-blob entry lands on the α-preamble.

**Register contract — LIVE table (ignore the SM-era/r10 history in REGISTER-LAYOUT.md; the doc says itself
it's superseded, twice over, and `bb_regs.h` — its other source of truth — is deleted):**

| Reg | Role |
|---|---|
| r12 | ζ — BB-local RW frame `[r12+off]`. **NOT** a value stack. |
| r13 | Σ — subject base pointer |
| r14 | δ — cursor (0-based; `&pos = δ+1`) |
| r15 | Δ — subject length/end |
| rbx | GVA slot-array base — globals at `[rbx+gva_k*16]`, 16-byte DESCR stride (verified vs live templates 2026-06-30) |
| rbp | NV/variable-name hash table base (reserved; GET/SET still plain C calls) |
| r10 | **RETIRED** — no data-block register; `bb_regs.h` (which defined this contract) no longer exists |

**Flat-BB ABI.** A glob = N concatenated boxes' code + one sealed RO region at the end. Entry = jump to the
glob's first byte (no `esi` port-test — that's the legacy dispatched/`--bb-brokered` form only). Both
intra- and extra-blob transitions are plain `jmp rel32` (`r12` is callee-saved, survives either way). Two
block kinds: BB (`bb_*.cpp`, does WORK) vs XA (`xa_*.cpp`, wraps/stitches — prologue/epilogue/data-section/
entry-dispatch; builds no operands).

**Execution modes — current reality (REPO-SCRIP.md; `ARCH-SCRIP.md` is stale here, still describing a
since-deleted mode 2).** Exactly two: `scrip --run f` = mode 3, native x86 BINARY in-process. `scrip
--compile f` = mode 4, x86 TEXT asm → `gcc -no-pie` + `libscrip_rt.so`. Both must produce identical results;
that's the whole isolation invariant — no mode-3/4 code path walks the AST or interprets SM/BB at runtime,
the emitter walks the graph only at EMIT TIME then frees it.

**Build/run.** `cd /home/claude/SCRIP && make scrip && make libscrip_rt`. Oracle: SPITBOL x64 at
`/home/claude/x64/bin/sbl -b file.sno` (clone `snobol4ever/x64` if absent). **Fresh sandbox:** `apt-get install -y libgc-dev gdb` first; the audit oracle = icont/iconx built from the icon-master upload (`make Configure name=linux && make`, never X-Configure), auto-probed via `SCRIP/refs/` symlinks (RULES.md CONSULT CANONICAL SOURCES recipe).

**Corpus.** Icon programs: `/home/claude/corpus/programs/icon/rung<NN>_*.icn` (263, each with a sibling
`.expected`) — **not** `/home/claude/SCRIP/test/icon/` (only 8 smoke files). Full suite:
`bash scripts/test_icon_all_rungs.sh`. Fast smoke (12 programs, both modes): `bash scripts/test_smoke_icon.sh`.

**Concurrency discipline (GOAL-ICON-BB.md, condensed).** One dispatch case per IR kind; one template file
per box; edit only your own language's arms/boxes, never a peer's; a kind with no case ABORTS loud, never
silently declines. Patch-offset bookkeeping is abolished — `bb_bin_t`/hand-counted byte offsets don't exist;
patch metadata travels in-band as tagged records inside a template's returned string, walked once by
`bb_emit_x86`.

## ⛔⛔ IR-LAYOUT JCON-ALIGNMENT DIRECTIVE (Lon, 2026-07-02) — make Icon's IR match JCON's layout
**Principle (Lon verbatim-in-spirit):** match JCON's IR record set as closely as possible. THE ONE EXCEPTION is
`ir_Goto`/labels — SCRIP BBs carry the four ports INSIDE the box template, so instead of varying code output
with labels, SCRIP has varying `IR_*` opcodes that CLASSIFY each form BY NAME, one template each. SNOBOL4 was
done very differently; Icon shall be the JCON-faithful one. All BBs done = Icon at 100%.

**LANDED (`65f8c32e`):** `IR_FIELD`→`IR_FIELD_GET` · `IR_ENTER_INIT`→`IR_INITIAL` (mechanical, FAIL set byte-identical).

**DERIVED ANSWERS (fresh from refs/jcon-master/tran, 2026-07-02):**
- **while/until:** JCON emits PURE `ir_Goto` chunk wiring — `ir_Conj` does not exist ANYWHERE in JCON (0 hits
  in ir.icn/irgen.icn/gen_bc.icn). SCRIP's `IR_CONJ` is our MATERIALIZED Goto: the chain-BFS discards a
  sentinel's edges, so where JCON writes a bare Goto chunk, SCRIP needs a real node to carry the jump
  (while's exit sentinel W, repeat's header H, break/next). Same wiring, one SCRIP-ism justified by the
  ports-in-the-box exception.
- **to / to-by:** JCON has NO `ir_To` at all — `ir_a_ToBy` defaults `/p.byexpr := a_Intlit(1)` and always emits
  ONE `ir_opfn(operator("...",3))`. JCON collapses because its product is a generic opfn dispatch; per the
  classification principle SCRIP splits BY NAME instead.
- **subscript:** canonical subscript yields a VARIABLE (`oref.r` subsc/trapped vars) — lvalue AND rvalue
  through one node is CORRECT. Current `TT_IDX → lower_call("[]")` is the misfit.

**RUNG LADDER (Lon directives, in order):**
- ~~TO-SPLIT~~ **LANDED (SCRIP `7dd2baf7`, 2026-07-02):** `IR_TO` (2-operand, implicit by=1) + `IR_TO_BY` (3-operand,
  runtime by; `lower_to` picks by TT arity) — mirrored at every spec'd IR_TO site plus three the spec didn't name
  (`scrip.c rhs_kind_ok` pre-emission gate, `bb_call_write_route` wintexpr/route-3, `descr_chain_arity`=3).
  `bb_to.cpp`'s static constant-by helper was DEAD on the live path (walk stages `op_node_kind=nd->op`, never
  IR_OP_COUNT, so it always returned 1) — by=1 baked, byte-identical; `bb_to_by.cpp` carries the runtime-by
  four-port arm verbatim. **IR_RESUME_VALUE was NOT needed** (see reserved table). Probes 34/35 hold; negative-by
  hand-checked m3==m4; audit 68/68; corpus 194/59/36 FAIL set byte-identical (stash `comm` diff empty).
- ~~IR_MAKE_LIST~~ **LANDED (SCRIP `138c64dc`, 2026-07-02):** TT_MAKELIST/TT_VLIST → `lower_make_list` →
  `IR_MAKE_LIST` (N operands), retiring the `lower_call("MAKELIST")` by-name string route for Icon; element
  chaining is JCON `ir_a_ListConstructor` verbatim-in-shape. Variable slot grant (k += 1+n_operands: result
  DESCR at tmp, contiguous argv scratch at tmp+16); `bb_make_list.cpp` marshals slots → ONE `rt_make_list`
  call (extracted from the by-name arm, which now delegates — write-once); >16-element literal falls LOUD.
  Probe 50 OK 4-way; audit 68/68; corpus FAIL set byte-identical; empty `[]` + inline `[5,6,7][3]` hand-checked m3==m4.
- [ ] **IDX-UNIFY:** route `TT_IDX` → `IR_SUBSCRIPT` (2-operand base+index form beside the 3-operand section
  form), lvalue+rvalue; retire `lower_call("[]")`. Unblocks the `arr[i] <- v` punch item (subscript-lvalue
  revassign). Probe 63 + 53/54 must hold.
  **SURVEY (2026-07-02, pre-implementation — verified against canonical + live tree):** (a) canonical `subsc`
  is `operator{0,1} [] subsc(underef x -> dx, y)` (oref.r:581, `use_trap` machinery) — takes x UNDEREFERENCED,
  yields a trapped VARIABLE, fails on out-of-range; (b) JCON's rval partner is `ir_Deref(lhs value)`
  (gen_bc.icn:124) — tmp-holding-variable → tmp-holding-value, exactly the KEEP-reserved `IR_DEREF`'s job;
  (c) **BIGGER THAN SPEC'D: `x[i] := v` is TODAY an `IR_FAIL` placeholder** (lower_icon.c TT_ASSIGN's TT_IDX
  arm builds `IR_FAIL` and pushes operands onto it — the chain-BFS threads it to ω, so subscript-ASSIGNMENT
  silently fails); IDX-UNIFY replaces that placeholder, not just the `<-` shape; (d) today's rvalue route is
  `lower_call("[]")` → by-name `subscript_get(l,r)` — a value COPY, no variable semantics; (e) discriminate
  the two IR_SUBSCRIPT arms by n_operands (2 vs 3; section variants already ride op_ival). PHASING
  RECOMMENDATION: structure (list/table) cell-pointer variable first + IR_DEREF for rval consumers + the
  assign-through write path; STRING subscript keeps the value path this rung (probe 63 protected; canonical
  `tvsubs` string trapped-vars = its own later rung).
- [ ] **CONJ-RENAME (Lon raised 2026-07-02, name = Lon's call):** `IR_CONJ` is named for Icon's `&`
  (goal-directed sequential conjunction — e2's value, e2-failure backtracks into e1; not boolean AND), but its
  DOMINANT role today is the MATERIALIZED GOTO the IR-LAYOUT directive's ONE EXCEPTION describes: repeat's
  header H, break/next jumps, the case-result collector, `;` sequencing, every-no-body placeholder (JCON has
  no ir_Conj — 0 hits — it writes bare Goto chunks; SCRIP needs a real node because the chain-BFS discards
  sentinels' edges). The name under-describes the node. Options for Lon: (a) ONE new name for the junction
  role (IR_JOIN / IR_JUNCTION / IR_LINK …) or (b) SPLIT — keep IR_CONJ for genuine `&`, new opcode for the
  pure-jump role (classify-by-name principle). Mechanical pass mirrors the `65f8c32e` rename precedent.
- [ ] **RESERVED-SET RECONCILE — census DONE (2026-07-02, whole-src grep excluding decl/name-table), Lon decides delete-vs-implement per enum:**
  | enum | live refs | JCON record | verdict input |
  |---|---|---|---|
  | ~~`IR_EXEC`~~ | **DELETED (`7138de96`)** — was a payload MACRO (IR.h:109), not an enum member (census miscount corrected) | none | — |
  | ~~`IR_UNREACHABLE`~~ | **DELETED (`7138de96`)** | ir_Unreachable | role served by `x86_bomb` — divergence ratified |
  | ~~`IR_SCAN_SWAP`~~ | **DELETED (`7138de96`)** | ir_ScanSwap | save/restore lives inside IR_SCAN_ENTER — divergence ratified |
  | `IR_DEREF` | 0 | ir_Deref (gen_bc:125) | **KEEP-reserved (Lon Q&A 2026-07-02):** IR_VAR fuses read+deref (value copy) and lvalues are dedicated WRITE opcodes today — but IDX-UNIFY makes IR_SUBSCRIPT variable-producing, and its rval consumers then need the explicit deref, JCON-style (gen_bc:125). IR_DEREF is the IDX-UNIFY partner. |
  | `IR_MOVE` | 1 (copy_prop.c, unexercised pass) | ir_Move (gen_bc:220) | absorbed by the tmp doctrine DELIBERATELY (producers write own slot; zero construction sites) — delete = ratify the divergence; implement = feed copy_prop |
  | ~~`IR_RESUME_VALUE`~~ | **DELETED (`ed0ac777`, Lon directive 2026-07-02)** — reservation spent: TO-SPLIT (`7dd2baf7`) landed ToBy resume as durable ζ-frame arithmetic (counter at tmp+16, β = plain add), so JCON's resume-value INSTRUCTION dissolves into SCRIP's frame LAYOUT | ir_ResumeValue (gen_bc:551) | — |
  | `IR_MAKE_LIST` | 0 | ir_MakeList (irgen:1346) | **IMPLEMENT** — already this ladder's rung above |

  **CORRECTION (2026-07-02):** `IR_OP_COUNT` was wrongly listed in the earlier 7 — it is the enum COUNT
  SENTINEL (277 structural uses as array bound/name-table size), not an opcode; NOT deletable.

## ⛔ FACT RULE — THE EMITTER NEVER MUTATES AN IR NODE
The emitter (`src/emitter/**`) dispatches on `nd->op` and reads `nd`'s fields. It does **NOT** write
`nd->op`, does **NOT** write `IR_LIT(nd).*`/`IR_EXEC(nd).*` on an input node, does **NOT** synthesize IR
nodes, and does **NOT** consult `rt_*` to decide IR shape. Every specialization decision is made in LOWER
(per-language) and baked into the IR shape the emitter receives.
**GATE:** `scripts/test_gate_emit_no_ir_mutation.sh` — `[-]>op[[:space:]]*=` (op-writes) + `IR_LIT(...).x =`
on an input node (field-writes) == 0. **Current: HARD=4** (all pre-existing, in code paths the GZ#5 rewrite
hasn't reached yet — not regressed by Icon LOWER work, which the gate doesn't scan).

## ⛔ DIVISION RULE (Lon, 2026-06-27) — RESUMABILITY IS ω-WIRING, NOT A STORED FLAG
"Generator vs coercive vs plain" is not three operators — it's the OPERATION (an immediate on one node) plus
**resumability, which costs ZERO template logic**: a resumable node is reached by routing a consumer's
backtrack edge AT the producer node; the chain-BFS (`codegen_flat_chain_body`) resolves that edge to the
producer's **β** (not its α) whenever `ir_is_generator_kind(producer)` and the consumer sits later in chain
order. **PROVEN (B3, 2026-06-27):** live four-port chains correctly enumerate `(1 to 3)+10`→`11 12 13` and
Cartesian `(1 to 3)+(1 to 2)`→`2 3 3 4 4 5` with **zero dedicated generator-tree walker** — `bb_conj`'s entire
body is `x86_pair_loop()` (pure in-band β-define + γ/ω jumps from the DRIVE_PAIR table). Never store a
generator/resumable flag on the node (`dval=1.0` tags are the violation pattern — remove on sight).

## DO NOT
- Re-introduce ANY `->op =` write in `src/emitter/**`.
- Decide a call kind from `rt_*` runtime state at emit time — proc/builtin tables are compile-time.
- Encode operand-source in an IR opcode — operand-source lives on the OPERAND node (a producer box).
- Add a per-language function to the emitter/templates — language lives in parser + LOWER only.
- Build a separate "generator" opcode/template family — see DIVISION RULE; it's ω-wiring, not a template.

## ⛔⛔ CONVERSION PLAYBOOK — JCON → SCRIP, ONE TT AT A TIME (Claude Sonnet 4.6, 2026-06-30)
**The mechanical recipe for converting any Icon construct from JCON into LOWER + the EMITTER DRIVER +
TEMPLATES. Read once; each TT is then fill-in-the-blanks. This is the head-start for the SNOBOL4/Snocone/
Rebus/Prolog/Pascal sessions doing the same to their own lowers later.**

### THE CENTRAL ISOMORPHISM — 4 JCON labels ⇄ (2 node positions + 2 IR_ref_t edges)
JCON's `ir_info(start, resume, failure, success)` (`irgen.icn` `ir_init`) ⇄ SCRIP's `IR_t.γ`/`IR_t.ω`
(`src/contracts/IR.h`):

| JCON label | SCRIP realization | Set/read by |
|---|---|---|
| `p.ir.start`   | the node's own **α position** in the flat chain | a predecessor's γ/ω points here |
| `p.ir.resume`  | the node's own **β position** | BFS routes a consumer's edge here iff `ir_is_generator_kind` |
| `p.ir.success` | `nd->γ.node` | LOWER: `γ_to(nd, target)` |
| `p.ir.failure` | `nd->ω.node` | LOWER: `ω_to(nd, target)` |

`start`/`resume` are **not stored** — they're positions the BFS discovers from edges pointing AT the node.
You never "set start/resume"; you set OTHER nodes' γ/ω to point here, and the generator-kind check picks
α-vs-β. This is why JCON's four labeled chunks collapse to two edges. `p.ir.x` (loopinfo/scaninfo) has no
struct field — it's carried in `icx_t` (`cx->loop_exit`, `cx->loop_next`, `cx->beta`) during lowering.
JCON's `ir_tmploc`/`ir_MoveLabel`/`ir_IndirectGoto` (unbounded-resume "label variable") usually maps to
**plain β-wiring** — wire ω at the right node and delete the indirection.

**⚙ IR_ref_t CARRIES ITS OWN α/β PORT IN `.sz` — LOWER STAMPS IT, EMITTER READS IT (LANDED 2026-06-30, `bb70a841`).**
`IR_ref_t` = `{IR_t* node; char sz[4];}`. The `sz` field is the **α/β discriminant of the edge**, written by
LOWER at construction and read by the emitter — NOT recomputed downstream. The rule LOWER applies: an edge whose
TARGET is `ir_is_generator_kind` is a RESUME edge → stamp `"β"` (`lc_γ_to_β`/`lc_ω_to_β`); every other edge →
`"α"` (`lc_γ_to`/`lc_ω_to`). The Icon `γ_to`/`ω_to`/`build` wrappers (`lower_icon.c`) do this automatically by
checking `ir_is_generator_kind(target)`. The emitter (`emit.cpp` chain-BFS) reads the stamp:
`node_γ = (γ.sz=="β") ? betas[k] : lbls[k]` (UTF-8 `β` = `CE B2`). **PROVEN equivalent to the old positional
`i > k && ir_is_generator_kind` guess:** with the positional fallback DELETED (pure-stamp routing), icon smoke
stays 11/12 and the full corpus stays 82/289 — zero divergence. The fallback is RETAINED for now only to protect
un-stamped edges during the ongoing GZ#5 rollout; the end state deletes it. **WHY THIS MATTERS (Lon, 2026-06-30):**
the graph must be CORRECT AT CONSTRUCTION — an edge has to say whether it means "enter fresh (α)" or "resume (β)"
or no optimization pass can even know what an edge *means*. Recomputing α/β positionally in the emitter made the
graph incomplete; stamping it on the ref makes the graph self-describing, which is the precondition for sound
optimization. **The remaining un-stamped resume sites** (SEQ/CONJ backtrack chaining `ω_to(val[i],val[lr])`,
`cx->loop_next` loop-backs, `lβ`/`mβ` operand resumes) currently rely on the positional fallback; stamping them
explicitly (so the fallback can be deleted) is the follow-up rung. **NOTE:** a stamp names ONE static target; a DATA-dependent resume (whichever arm last fired) is the label variable — LANDED `dc45d9e2` (`IR_MOVE_LABEL` + `IR_INDIRECT_GOTO`; see Watermark).

### lhs ⇄ tmp
JCON's `lhs`→`ir_Tmp` node ⇄ SCRIP's `int IR_t.tmp` FIELD on the producing node (one node = one value = one
slot — why the `IR_TMP` opcode is dead). LOWER assigns it; `drive_value_slot()` (`emit.cpp`) reads `nd->tmp`
first, falls back to legacy slot-alloc only for unconverted nodes. A consumer reads an operand's value via
`operand->tmp` (see `IR_CALL`'s arm: `a->tmp`).

### THE FOUR CONVERSION SHAPES (classify the JCON `ir_a_X`'s `ir_chunk` list)
1. **Pure edge-threading** (only `ir_Goto` chunks) → LOWER wires γ/ω among sub-exprs; **no opcode, no
   template, no driver case.** Landed: `TT_IF` (`lower_if`, JCON `ir_a_If`). Also this shape: `ir_a_Compound`,
   `ir_a_NoOp`, `ir_conjunction` (→ `IR_CONJ`/`bb_conj`, whose template is pure pair-table threading — the
   zero-template limit case of this shape).
2. **Value-producer + runtime call** (`ir_opfn`/`ir_Call`/lits) → ONE `IR_*` node, operand `tmp`s pushed, the
   TEMPLATE marshals slots into args and `call`s an `rt_*` helper (value work NEVER reimplemented inline —
   that's DUP FORM 1/2 in GOAL-ICON-BB.md). Operation rides as an immediate, not opcode identity. Landed:
   literals, `IR_VAR`, `IR_BINOP`/`_RELOP`, `IR_UNOP`, `IR_CALL*`, `IR_KEYWORD`, `IR_RETURN`.
3. **Resumable generator** (success loops back via resume) → per the DIVISION RULE, make the node
   `ir_is_generator_kind` and point the consumer's backtrack edge at it; the BFS does the rest. Landed:
   `IR_TO` (`bb_to.cpp`). Also landed: `TT_EVERY`, `IR_REPALT`, `IR_LIMIT`, `IR_ITERATE`.
4. **Control/effect** (`ir_Succeed`/`ir_Fail`/`ir_Assign`) → `IR_SUCCEED`/`IR_FAIL`/`IR_ASSIGN`, no tmp.
   JCON's `ir_Move` (copy closure result into target) is usually absorbed — the producer writes its own tmp.

### THE LOOP-BACK & UNCONDITIONAL-JUMP IDIOM (loops, break, next, goto — Claude Sonnet 4.6, 2026-06-30)
**THE TRAP (cost an entire prior session a "diagnosed, not fixed" entry):** an `IR_FAIL` or `IR_SUCCEED` node is
NOT a general "jump-to-my-γ-target" node — it is a CHAIN TERMINATOR. The chain-BFS (`codegen_flat_chain_body`,
`emit.cpp`) does two things that discard a sentinel's edges: (i) it *threads through / skips* `IR_SUCCEED` and
`IR_FAIL` nodes (they're never added to `nodes[]`, lines ~950/955/970), and (ii) when ANOTHER node's γ (or ω)
points AT a sentinel, it resolves that edge to the **chain's** `lbl_γ`/`lbl_ω` exit (lines ~1001-1002:
`γ.node->op == IR_FAIL → node_γ = &lbl_ω`; `== IR_SUCCEED → &lbl_γ`). So a sentinel's *own* γ-target (e.g. the
post-loop continuation you wired into a `break`) is **silently thrown away** — control goes to the enclosing
chain's exit, not your target. This is why `repeat`-via-`IR_FAIL`-loopback ran the body once then left, and why
`break`-as-`IR_FAIL` skipped its post-loop code.

**THE FIX — to jump unconditionally to an arbitrary real target T (and have T's subgraph emitted), use an
`IR_CONJ` node with γ=ω=T, never a sentinel.** `IR_CONJ`'s driver (`emit.cpp` ~line 910) is pure
`DRIVE_PAIR_JMP(lbl_γ)` + `DRIVE_PAIR_DEF_JMP(lbl_β,lbl_ω)` — i.e. "jump to my γ-target," nothing else — and
`IR_CONJ` IS a real chain node, so (a) it is added to `nodes[]`, (b) the BFS *follows* its γ edge (queuing T and
everything reachable from T), and (c) an edge pointing at the `IR_CONJ` resolves to the `IR_CONJ`'s own α label —
a real `jmp`, forward or backward. `IR_CONJ` carries no value and needs no tmp; pushing its jump-target as
operand[0] (as `lower_repeat` does) keeps slot-registration uniform with the value-producing CONJ used for `;`.

**APPLYING IT — the loop family (JCON `ir_a_Repeat`/`ir_a_While`/`ir_a_Until`, decoded to 2-edge form):**
- `while C do B`: sentinel `W=IR_FAIL` with `ω→γ_post`; `C.success→B.start`, `C.failure→W`(=exit),
  `B.success→C.start`, `B.failure→C.start`. (Works because a `while` *does* exit via C's failure — the
  `IR_FAIL` exit semantics align. **Do not "fix" `while`'s `IR_FAIL` — it is the genuine loop exit.**)
- `until C do B`: mirror — `C.success→W`(=exit), `C.failure→B.start`, body loops to `C.start`.
- `repeat B`: **no condition, no failure exit.** Header `H=IR_CONJ`, `γ=ω→B.start`; body lowered with
  `γ=ω→H` (both body success AND body failure loop back); construct entry = `H`; `cx->beta=γ_post`. The loop
  leaves ONLY via `break`/`return`/`fail`. (JCON: `expr.success→ir.start`, `expr.failure→ir.start`,
  `ir.start→expr.start`; the `ir.start` Goto collapses into `H`.)
- `break` (JCON `ir_a_Break`: `expr.success→curloop.success`, `expr.failure→curloop.failure`): jump to
  `cx->loop_exit` (the loop construct's γ = its post-loop continuation) via `IR_CONJ`, γ=ω=`loop_exit`.
- `next` (JCON `ir_a_Next`: `Goto curloop.nextlabel`): jump to `cx->loop_next` (the loop header) via `IR_CONJ`.
  For `repeat`, `cx->loop_next = H`; for `while`/`until`, set it to the condition entry so `next` re-tests.
- **`cx->loop_exit`/`cx->loop_next` save/restore is MANDATORY** around the body lower (nested loops) — already
  done by all three; copy the pattern.

### EXPORTABLE WIRING RULES (proven across LIMIT/REPALT/ALT/IF — apply to every future junction construct, any language)
- **Edge ROLE beats target KIND.** `build()`/`γ_to` auto-stamp β whenever the TARGET is generator-kind — trustworthy ONLY for backtrack edges. A producer's SUCCESS edge into a generator-kind junction (LIMIT gate, REPALT, …) is α (enter fresh); LOWER must α-restamp it (`lc_γ_to`). Enforced at 7 sites: statement spine (guarded — `every` re-aims its own γ), TT_REPALT's γ, TT_LIMIT count→entry, TT_SEQ/SEQ_EXPR, and (2026-07-02, `b3d41c74`) the loop family's body entries — lower_while C.γ→B, lower_until C.ω→B, lower_repeat H→B.
- **A synthesized `*res` junction's γ is the construct's PUBLIC success label.** Wire-later callers re-point only `*res` — internal success paths (each arm's ml) must resolve through the junction's γ at EMIT time (a READ of the finished graph, never a write).

### THE 3-FILE EDIT RECIPE (shapes 2 & 3; shape 1 is LOWER-only)
- **(a) LOWER** (`src/lower/lower_icon.c`): build the node (`build(cx,IR_X,γ,ω)`); recurse sub-exprs
  capturing `*res` + `cx->beta`; wire γ/ω per the JCON chunk list (`γ_to`/`ω_to`); push operands
  (`ir_operand_push`/`bb_operand_aux_set`); set `cx->beta` to this node if it's the resumable thing the
  consumer should target. Return the entry node; set `*res` to the value node.
- **(b) DRIVER** (`src/emitter/emit.cpp`, `emit_drive`): add `case IR_X:` — read operand slots
  (`bb_child0/1`, `ir_call_arg(nd,i)`, `→tmp`), set `g_emit.op_*`, set DRIVE_PAIR if the box jumps via the
  pair loop, `DRIVE_FILL(nd, lbl_γ, lbl_ω, lbl_β)`. **Read-only — never write `nd->op`/`IR_LIT(nd).field`.**
- **(c) TEMPLATE**: `case IR_X: bb_emit_x86(bb_x()); return 0;` in `walk_bb_node`; create
  `src/templates/bb_x.cpp` (`x86(...)` only, both BINARY+TEXT via the same calls); add to Makefile + gate
  scans. Mirror an existing same-shape template (generator→`bb_to.cpp`; pure-thread→`bb_conj.cpp`).
- **(d) BFS REACH:** confirm `codegen_flat_chain_body`'s queue-feeding follows the node's ω where needed
  (generator exhaust, relop fail) — **the single most common silent bug** (sank `until` until `59dafbc0`).
- **(e) VERIFY both modes, then commit:** `SCRIP_ICN_BB=1 ./scrip --run` AND `./scrip --compile` →
  `gcc -no-pie -x assembler X.s -Lout -lscrip_rt -lgc -lm -Wl,-rpath,out` → run. Mutation gate ≤ baseline. If
  a generator diverges/hangs: **MONITOR-FIRST** (RULES.md) — bracket with the monitor, then gdb
  breakpoint-hit-count to the land mine. Do not guess.

### CANONICAL SOURCE PAIRING
Port topology ← `refs/jcon-master/tran/irgen.icn` `ir_a_X` (the `suspend ir_chunk` list IS the γ/ω wiring).
Emission ← `refs/jcon-master/tran/gen_bc.icn` `bc_gen_ir_Y` for each `ir_Y` in the chunk (JVM bytecode → x86
by analogy). Value semantics ← `refs/icon-master/src/runtime/*.r` (`oarith.r`/`ocomp.r`/`ocat.r`/`oasgn.r`/
`fscan.r`/`fstranl.r`/`invoke.r`). The m2 oracle is a transcription, not truth.

### ⚠ FILE-LAYOUT NOTE (2026-06-30 consolidation — several older docs/PLAN.md are stale on this)
`src/emitter/{emit_bb.c, emit_core.c, emit_drive.c, BB_templates/, XA_templates/, bb_regs.h}` **no longer
exist.** Current: `src/emitter/emit.cpp` + `emit.h` (the ONE driver, `emit_drive`, + dispatch) + `emit_io.c`
+ `emit_str.cpp` + `sil_macros.h`; templates flattened to `src/templates/*.cpp` (161 files, no subdirs). The
register contract is hardcoded as `"r12"`/`"r13"` string literals in templates — no macro header. Use these
paths; ignore any doc still citing the old ones (this file now does, throughout).

## ⛔ TT_* COVERAGE PUNCH LIST (Icon ladder — climb this, not an opcode ladder)
**Ground truth = `bash scripts/audit_jcon_wholesale.sh` — run it fresh; never trust this prose (TECHNIQUE Step 4).** Snapshot 2026-07-01: **64/66 both modes.**

**✅ COVERED (audit-verified OK):** literals I/R/S/CSET · ident/global/invocable · `initial` (once-per-DEPTH caveat below) · binop arith/divmod/relop/concat · unop −/+/*x/\x//x (IR_UNOP + IR_UNOP_TEST) · `not` (via `&null` IR_VAR; IR_NOT deleted) · assign/augop/swap · **if** — statement AND value-context, then+else (value convergence via the ig shared cell, JCON `ir_a_If` :583-610, landed 2026-07-01) · while/until/repeat/break/next · every (postfix, assign, assign+body, noassign-after) · to / to-by · alternation bounded + unbounded (label variable) · repalt · limit · compound · call (builtin/arglist/params/recurse/mutual) · proc fail/suspend/return · list-ctor / `|||` lconcat · record field · section `s[i:j]` + string subscript · scan (move/tab-upto/many/match/cset-arg) · create / `@` activate / exhaust · seq-expr · `&line` / `&pos`-in-scan · case + case-default.

**🔴 OPEN — the audit ladder: EMPTY (66/66 as of SCRIP `a3de01d2`, 2026-07-01).**
- ~~`22_revassign`~~ **LANDED (SCRIP `a3de01d2`):** `IR_REV_ASSIGN` (generator-kind, k+=2 grant, save DESCR at off+16) per canonical `rasgn` (oasgn.r:142-162), reusing the pre-existing orphaned `bb_rasgn.cpp` verbatim. The historic BENCH-F2 op_a_slot collision is defeated by OPERAND ORDER (operands[0]=rhs so walk's clobber-pattern re-derivation lands correctly; [1]=lhs name carrier, IR_SWAP idiom). Root cause of the probe failure: `is_resumable()` (the AST-side conj fail-chain predicate) lacked TT_REVASSIGN — one token. Subscript lvalue `arr[i] <- v` stays an honest IR_FAIL placeholder (own rung).
- **Same commit (Lon directive):** `bb_operand_aux_set/get` DELETED — it was a thin DESTRUCTIVE veneer over `IR_t.operands/n_operands` itself (no side table); 12 setters → `ir_operand_push`, 6 tautological fallback readers collapsed, API gone from IR.h/scrip_ir.c/lower.h. RULES.md PEERS RULE corrected in place. Renames: `IR_RASGN→IR_REV_ASSIGN`, `IR_SECTION→IR_SUBSCRIPT` (Griswold-book naming; dead-name reuse, the IR_UNOP_TEST precedent).
- ~~`54_section_plus`~~ **LANDED (SCRIP `c0e74d52`, 2026-07-01):** `s[i+:n]`/`s[i-:n]` desugared in LOWER per canonical icont (tcode.c:591-600 — dup i; eval n; plus/minus; sect): synthetic IR_BINOP(ADD/SUB) as operand[2], IR_SECTION always plain; driver operands moved to `drive_value_slot` (tmp doctrine); `subscript_get2` reversed positions now SWAP per canonical sect (oref.r:509-513) — also fixes plain reversed `s[4:2]`, previously empty. Audit 65/66.

**🟡 OPEN — beyond the probe set:**
- ~~corpus rung03 suspend shapes~~ **LANDED (SCRIP `a0b3f410`, 2026-07-02):** not a suspend bug — a UNIVERSAL proc-local varslot/tmp collision (`bb_varslot` cursor after param interning == `ir_drive_slot_assign`'s base; the relop's return-y result-write clobbered the first local). Fix: proc builders jump the varslot cursor to `jcon_value_region` so locals sit above tmps. Corpus 190→194 (+rung03_suspend_{gen,compose,filter}, +rung36_jcon_statics), zero regressions.
- `TT_CSET_COMPL` (`~e`) — silent no-op stub (falls to default → IR_SUCCEED); `TT_RANDOM` (`?e`) + dead `TT_INTERROGATE` — unresolved silent no-ops, deliberately unreclassified (flagged 2026-07-01).
- coexpr unary prefixes `.e` / `^e` absent from `parse_unary` (`^` lexes only as binary POW).
- `IR_SCAN_TAB` absent from `ir_is_generator_kind` (UPTO/FIND/MANY/BAL present) — the scan family's "reverses effects if resumed" contract (canonical `tabmat`, `omisc.r:84`) is unverified; own rung.
- ~~limit-of-RepAlt `(|1) \ 3`~~ **STALE — re-tested 2026-07-02, PASSES** (fixed by the intervening repalt/limit rungs); deleted per re-derive-don't-trust-prose.
- ~~`while … do write(|1)` unclassified data point~~ **CLASSIFIED + LANDED (SCRIP `b3d41c74`, 2026-07-02):** loop-family PRODUCE edges into generator-kind bodies were auto-stamped β (asm-verified `jmp …β` skipping REPALT's α flag-clear). lower_while/until/repeat body-entry edges → unconditional α-stamp (EXPORTABLE RULE sites 5-7; bodies are bounded, JCON 'always bounded'). Probe `68_loop_genkind_body` pins all three — **audit 68/68**. SIBLING FLAGGED (no repro yet): the body→condition LOOP-BACK edges have the same latent shape if a loop CONDITION's entry is generator-kind; conditions are bounded too, α when a repro lands.
- ~~unary-test-op failing-`if` else-routing~~ **LANDED (SCRIP `ca31f6e2`, 2026-07-02):** BFS ω-following whitelist lacked IR_UNOP/IR_UNOP_TEST (both loops) — else subgraph never discovered, edge resolution degraded to chain lbl_ω, whole if-else silently vanished. Mirror of the BINOP pair added; probe `67_unop_test_else` pins it — **audit now 67/67**.

**⚠ STANDING AUDIT TARGETS (systemic, not constructs):**
- **THE CLOBBER PATTERN** (see WHOLESALE section below) — diff every `g_emit.op_{sval,ival,dval,stno}` staged in `emit_drive` against `walk_bb_node`'s re-derivation lists; each mismatch is a live/latent bug (two found so far: CHARSET sval, LIMIT ival).
- **x86() silent-drop** — the dispatcher returns EMPTY for an unrecognized arg shape (sank `bb_enter_init`'s 4-arg cmp/mov; kept `flat_drive_repalt`'s absence invisible). A default-bomb retrofit at 147-template scale is its own carefully-gated rung, not a drive-by.
- `initial` is once-per-DEPTH, not once-per-procedure (ζ frames = static `g_rt_frames[depth]`, reused) — canonical once-ever needs writable static storage; own rung (the GVA `.bss` arena is the named candidate, GOAL-ICON-BB §ICN-STORAGE).
- Emitted proc preamble still carries `lea r10,[rip+Δ]` — r10 is RETIRED in the register contract; reconcile the preamble with REGISTER-LAYOUT's table.
- `SCRIP_OPT=1` `branch_chain` crash (optimizer ships OFF by default). Whoever fixes it must defer-protect captured labels: coret β-edges, `g_create_body_entry` targets, every `IR_MOVE_LABEL.operand[0]` target, every `IR_INDIRECT_GOTO` γ-target (JCON `optim_goto_chain_defer` discipline). `copy_prop` has zero live material (no IR_MOVE construction sites — unexercised) and its unconditional-elimination divergence from JCON's `defs==1 & uses==1` is unverified; `arith_fold.c` is unlinked.
## ⛔⛔ MECHANICAL JCON→SCRIP CONVERSION TECHNIQUE (Claude Sonnet 4.6, 2026-06-30) — read before starting any new TT
**This is the by-eye/by-hand recipe used this session, written up so the next session (Icon or, later, any
other language doing the same JCON-mirroring exercise) doesn't have to re-derive it.** It is a refinement of
the CONVERSION PLAYBOOK above with the actual workflow steps that playbook assumes but doesn't spell out.

### Step 0 — find the JCON procedure, read it as a literal wiring diagram
`refs/jcon-master/tran/irgen.icn` has one `ir_a_X` procedure per AST node kind (`grep '^procedure ir_a_'`
gives the full list — **43** of them, one-to-one with JCON's `a_X` AST records; **the "47" this line previously claimed is WRONG — fresh `grep -c '^procedure ir_a_' refs/jcon-master/tran/irgen.icn` = 43, re-verified 2026-07-01**). Each is a `suspend
ir_chunk(LABEL, [INSN, INSN, ...])` sequence. Read it as exactly what it says: a chunk named `p.ir.start` (or
`.resume`/`.success`/`.failure`) containing a list of instructions ending in a `ir_Goto`/`ir_IndirectGoto` to
another chunk's label. **Draw the graph on paper or in your head before writing any C** — nodes = chunks,
edges = the Goto targets. This graph IS the lowering; everything downstream is mechanical translation of it.

### Step 1 — classify by the FOUR CONVERSION SHAPES (already in the playbook above)
Count how many `ir_opfn`/`ir_Call`/value-instructions appear outside pure `ir_Goto` threading. Zero ⇒ shape 1
(pure edge-threading, LOWER-only, no opcode/template). One ⇒ shape 2 or 4 depending on whether a value is
produced (`lhs`/`target` set) or not. A success-chunk that loops back to a `.start`/`.resume` ⇒ shape 3
(resumable generator) — **check this FIRST**, because shape-3 constructs disguise themselves as shape 1 if you
only look at instruction count; the tell is a `Goto` whose target is upstream of the current chunk in the
threading order (a back-edge), not just any `Goto`.

### Step 2 — find the `bounded`/`unbounded` fork, if any
Many `ir_a_X` procedures branch on `/bounded` (Icon: `if bounded is null then ... else ...`). **This single
flag is the entire difference between "this construct needs a label variable" and "this construct doesn't."**
`ir_a_Alt`/`ir_a_RepAlt`/`ir_a_ListConstructor` all do this — the unbounded arm allocates `t := ir_tmploc(...)`
and emits `ir_MoveLabel`/`ir_IndirectGoto`; the bounded arm never does. **Do not implement both arms in one
pass.** Land the bounded arm first (it is always simpler and is what 90% of real call-sites exercise — `write(x)`,
`if`, a plain consumer), prove it, commit it, THEN come back for the unbounded/label-variable arm as its own
rung. This is exactly why `TT_ALTERNATE`'s bounded case (`write(1|2)`) is done and its unbounded case
(`every write(1|2|3)`) is correctly deferred — don't fuse them.

### Step 3 — runtime semantics: which `.r` file, and what to actually extract
`refs/icon-master/src/runtime/*.r` is C, not Icon — it's the OPERATIONAL ground truth for what a value
operation actually computes (overflow rules, type coercion order, fail conditions), which JCON's `irgen.icn`
deliberately doesn't encode (JCON just emits a generic `ir_opfn`/`ir_Call` and defers semantics to its own
runtime, exactly as SCRIP's templates defer to `rt_*` helpers — **never reimplement value semantics inline in
a template; call/mirror the existing `rt_*` helper, or if none exists, the `.r` file tells you what that
helper needs to do**). The useful extraction from a `.r` file is almost never the whole function — it's the
ONE structural fact that disambiguates an implementation choice: this session's two uses were (a) `oasgn.r`'s
`GeneralAsgn` `default:` arm showing assignment is type-uniform once the destination's *address* is resolved
(`Asgn(x,y)` = `*VarLoc(dest)+Offset(dest) = src`, no type-casing at the store), which told us the global-vs-
local distinction must live in ADDRESS RESOLUTION (a template/driver concern), not in assignment semantics
(never needs its own per-kind logic); (b) `rmacros.h`'s `VarLoc`/`Offset` macros confirming a Icon "variable"
descriptor is self-locating regardless of storage class, which is the running theory for why SCRIP's existing
`bb_var_global.cpp`/`bb_gvar_assign*.cpp` family (12 templates, pre-existing, NOT new) already has the right
shape — it just isn't reachable from the new flat-chain driver yet (see GVA-FLAT rung below). Match the genre
of fact you need (control-flow shape vs. value semantics vs. storage-class resolution) to the genre of source
(`irgen.icn` vs `gen_bc.icn` vs `*.r`) — don't read all three cover-to-cover for every TT; **read the chunk
list first, and reach for the `.r` file only when a *specific* implementation choice is actually ambiguous.**

### Step 4 — BEFORE writing LOWER code, grep the CURRENT SCRIP state for the TT
`grep -n "case TT_X:" src/lower/lower_icon.c` and `grep -n "case IR_X" src/emitter/emit.cpp` (note: TWO
`emit.cpp` switches exist — `walk_bb_node`'s TEMPLATE SELECTOR switch and `emit_drive`'s DRIVER switch; a TT
can be live in one and stubbed/missing in the other, which is exactly what the global-assign bug turned out to
be). **Do not assume the punch list's prose is the ground truth for what's broken — it can be stale, and was
this session** (see CORRECTIONS below). Always re-derive from a fresh `gdb` repro + the actual switch
statements before designing a fix. The RULES.md MONITOR-FIRST methodology (bracket via a real crash/gdb
trace, not by reading code and guessing) is not optional even for "obviously" missing cases — this session's
global-assign investigation found a SECOND, upstream, more severe bug (a universal segfault, not the
documented "abort") purely because the repro was run before the fix was designed, not after.

### Step 5 — the 3-FILE EDIT RECIPE (already in the playbook above) applies; ADD: check for PRE-EXISTING
**infrastructure under a different driver mode before writing a new template from scratch.** This session
found `bb_gvar_assign.cpp` (legacy `!g_descr_flat_chain` driver, fully built, untested-but-presumably-working)
and `bb_var_global.cpp` (the flat-chain-NATIVE read-side counterpart, already correctly shaped). The
write-side flat-chain-native template does NOT exist and should be a fresh file MIRRORING `bb_var_global.cpp`'s
shape (dual-path: `[rbx+gva_k*16]` fast path when slot-allocated, `NV_SET_fn(name, DESCR_t)` runtime-call
fallback otherwise) rather than either (a) trying to reuse `bb_gvar_assign.cpp` as-is (wrong shape — it expects
raw `op_a_node_kind` node-shape introspection, the OLD driver's idiom; the flat-chain driver instead
pre-resolves every operand to a `tmp`-backed slot via `IR_t.tmp`/`drive_value_slot`, so the new template should
consume `op_a_slot`, not re-derive the producer's shape) or (b) writing global-assign from a blank page (most of
the addressing logic — `RDQ("rbx", k*16)` vs `FRQ(slot)`, the `g_gva_active`/`op_gva_k` gating — already exists
correctly in sibling templates and should be copied, not reinvented).

## Watermark
**2026-07-02 SESSION CLOSE — SCRIP `ed0ac777`: four commits this session — TO-SPLIT `7dd2baf7` (IR_TO/IR_TO_BY, JCON-ALIGNMENT rung 1) · IR_MAKE_LIST `138c64dc` (rung 2, by-name MAKELIST route retired for Icon) · IR_RESUME_VALUE DELETED `ed0ac777` (Lon directive; reservation spent) · IDX-UNIFY SURVEY recorded (rung open; FINDING: x[i]:=v is today an IR_FAIL placeholder). Every rung: audit 68/68 both modes · corpus 194/59/36 FAIL set byte-identical (stash comm) · smoke 12/12×2 · no_stack 0 · one_reg 0 · semicolon prison green · local_no_nv PASS · mutation HARD=4 baseline · bench-asm 13/0/1/12 unchanged. CONJ-RENAME rung opened (Lon names it). Next implementation rung: IDX-UNIFY.** Prior same day: IR_MAKE_LIST LANDED (JCON-ALIGNMENT rung 2) — dedicated opcode replaces the by-name MAKELIST string route for Icon; JCON ListConstructor chaining; variable slot grant (result + contiguous argv scratch); `rt_make_list` extracted, by-name arm delegates. Probe 50 OK 4-way · audit 68/68 both modes · corpus 194/59/36 FAIL set byte-identical · smoke 12/12×2 · all gates green · mutation HARD=4 baseline · bench-asm unchanged. Next ladder rung: IDX-UNIFY (route TT_IDX → IR_SUBSCRIPT 2-operand, lvalue+rvalue, retire lower_call("[]"); unblocks arr[i] <- v; the IR_DEREF partner).** Prior same day: TO-SPLIT LANDED (IR-LAYOUT JCON-ALIGNMENT rung 1) — `IR_TO`/`IR_TO_BY` split per spec + 3 unspec'd mirror sites (rhs_kind_ok, write_route, chain_arity); bb_to constant-by helper proven DEAD and by=1 baked byte-identical; IR_RESUME_VALUE NOT needed (reservation spent, back to Lon). Audit 68/68 both modes (34/35 hold, negative-by hand-checked m3==m4) · corpus 194/59/36 FAIL set byte-identical (stash `comm` diff empty) · smoke 12/12×2 · no_stack 0 · one_reg 0 · semicolon prison green · local_no_nv PASS · mutation HARD=4 baseline · bench-asm 13/0/1/12 unchanged (updated=0). Next ladder rung: IR_MAKE_LIST.** Prior: **2026-07-02 SESSION CLOSE — SCRIP `65f8c32e` (push pending): five rungs this session (slot-collision a0b3f410 · unop-else ca31f6e2 · loop-α-restamps b3d41c74 · renames 65f8c32e) + probes 67/68 · audit 68/68 · corpus 194/59/36 · bench-asm re-verified post-rename 13/0/1/12 · reserved-set reconcile EXECUTED: IR_SCAN_SWAP + IR_UNREACHABLE + IR_EXEC-macro DELETED (`7138de96`), IR_DEREF kept as the IDX-UNIFY partner, IR_MOVE/IR_RESUME_VALUE pending Lon. Opening rung next session: TO-SPLIT. IR_FIELD_GET + IR_INITIAL renames (JCON-alignment directive opened — see its section). Prior `b3d41c74`: loop-family PRODUCE-edge α-restamps LANDED (EXPORTABLE RULE sites 5-7; probe 68 — audit **68/68 both modes**). Prior rung `ca31f6e2`: failing unary-test-op else-routing (BFS ω-following UNOP pair; probe 67). Prior rung same session `a0b3f410`: proc-local varslot/tmp SLOT COLLISION fixed (universal — every proc with `local` had its first locals aliasing the first value-producer tmps; relop return-y writes clobbered them). Corpus 190→194/59/36 of 289** — stash/rebuild `comm` diff = exactly +4 FAIL→PASS (rung03_suspend_{gen,gen_compose,gen_filter}, rung36_jcon_statics), ZERO PASS→FAIL · audit 66→**67/67 both modes** (probe 67 added) · smoke 12/12×2 · no_stack 0 · one_reg 0 · semicolon prison green · local_no_nv PASS · mutation gate **HARD=4** (pre-existing baseline) · icont/iconx oracle live · bench-asm baseline 13/0/1/12. Prior rungs same day: `a3de01d2` (`22_revassign`, AUDIT LADDER COMPLETE + operand_aux API deleted + IR_REV_ASSIGN/IR_SUBSCRIPT renames), `c0e74d52` (`54_section_plus`).

### Landed history (compressed 2026-07-01 per RULES.md "DELETE completed steps" — full narratives in `git log` + `.github/HANDOFF-2026-0*.md`)
- **Foundations (06-30):** CONVERSION PLAYBOOK + `TT_EVERY` keystone · IR_ref_t α/β edge-stamp (`bb70a841`) · ICON-ONLY hard rules · `IR_ALT` deleted repo-wide (alternation = pure threading) · repeat/break/next via the IR_CONJ loop-back idiom · unop operand-push fix (`2d2b1ec8`) · universal `op_sval`/`gva_index_of` segfault fixed (`baa3a592`) · GVA-FLAT global assign (`feab99c7`) + slot-collision fixes (`024abd2f`, `d225d4a2`) · the every/TO/TO_BY regression cycle — fixed at HEAD, oracle-confirmed · scan-builtin opcodes TAB/MOVE/UPTO/ANY/MANY/FIND/MATCH/POS/BAL · IR_FIELD_SET / IR_PROC_GEN / IR_SUSPEND incl. binary-mode resume slots (`44c0da…`) · TT_IDX/MAKELIST union-clobber fixed (`8e296381`).
- **Opcode hygiene (07-01):** IR_TERNOP→IR_SECTION · IR_SUBSCRIPT / IR_GOTO / IR_NOT / IR_*_GENERIC deleted · four-opcode can-fail grid (IR_UNOP / IR_UNOP_TEST / IR_BINOP / IR_BINOP_TEST; the `_GEN` axis REJECTED per the DIVISION RULE) · `=s` desugared to `tab(match(s))` per `omisc.r:84` · prove_lower retired.
- **OPTIMIZER stage (07-01, `18a3440e`):** `src/optimizer/` between LOWER and EMITTER, `SCRIP_OPT`-gated OFF; branch_chain + copy_prop built (open items → PUNCH LIST standing targets).
- **Co-expressions (07-01, RUNGs 1-5):** create/coret/cofail pthread+semaphore model (`rt_coexpr.c`), `@` activation end-to-end both modes; three bring-up bugs gdb-bracketed (uninitialized create fields, bb_create k=5 clobber of the staged body-entry, coret γ→chain-default).
- **Label-variable infra (07-01, `dc45d9e2`):** IR_INDIRECT_GOTO re-added + IR_MOVE_LABEL; ig-owned shared 32-byte cell (value + `t`), t0-port sibling-label LEA; unbounded alternation `every write(1|2|3)` → `1 2 3`; corpus exactly +9; also fixed literal-arm ω-cascade discoverability and runtime-failing-arm0 value convergence.
- **Wholesale audit (07-01):** 66-probe icont-oracle instrument built · csetlit/&line/&pos/LIMIT (9 root causes) → 60/66 · initial + lconcat → 62/66 · repalt (`7edb9b9a`: `flat_drive_repalt` built — the phantom exorcised — + three β-mis-stamp PRODUCE-edge fixes + IR_REPALT `k+=2` grant) → 63/66 · if_value_else → **64/66** (SCRIP `6a509382`).
## ⛔⛔ WHOLESALE FROM-SCRATCH VERIFICATION — the executable audit + first fix ladder (Claude Sonnet, 2026-07-01, continuation session)

**Lon's directive verbatim-in-spirit: "do not trust any of it. We need to start the list from scratch and run through a one by one verification step. We are missing and are doing some thing wrong."** This session built the from-scratch list as an EXECUTABLE instrument, ran it, and fixed the first 4 construct families it caught (9 distinct root causes). The instrument is the head start for every future rung AND for the other-language LOWER/EMITTER rewrites.

### THE TECHNIQUE — what, where, when, why, how
- **WHERE:** `SCRIP/scripts/audit_jcon_wholesale.sh` + `SCRIP/test/icon/jcon_audit/NN_name.{icn,.expected}` (66 probes).
- **WHAT:** one minimal probe per JCON `ir_a_*` (all 43 — count re-derived fresh by `grep '^procedure ir_a_' refs/jcon-master/tran/irgen.icn`, matching the prior session's corrected 43; CoexpList excluded, JCON itself punts) plus SCRIP-specific TT extras (swap, revassign, augop, lconcat, scan suite, seq_expr, &pos, string subscript). Each probe runs **4-way**: canonical **icont/iconx ORACLE** vs hand-derived **EXPECTED** vs **MODE-3** vs **MODE-4**. Truth = oracle output when the oracle compiles the probe, else expected; oracle≠expected ⇒ **PROBE-BAD** (the probe is wrong, not SCRIP).
- **WHY the oracle:** hand-expected values drift and encode the author's misconceptions. The oracle caught TWO probe-suite bugs before they could masquerade as SCRIP bugs: (a) declarations joined with `;` — declarations are not statements, rejected by SCRIP AND standard Icon; use a NEWLINE between `end`/`global`/`record`/`invocable` and the next declaration (statements inside bodies stay `;`-separated for SCRIP); (b) icont flag order is `icont -s -o OUT FILE`.
- **HOW to build the oracle:** `cd <icon-master> && make Configure name=linux && make` → `bin/icont`,`bin/iconx` (this session: the uploaded `2-icon-master.zip`, extracted at `/home/claude/workspace/refs-src/icon-master`; a backgrounded make stalled at src/common — foreground retry completed in ~2 min). Harness auto-probes that path + `SCRIP/refs/icon-master/bin/icont`; override with `ICONT=`.
- **HOW to run/extend:** `bash scripts/audit_jcon_wholesale.sh [name-filter]`. To extend: drop `NN_name.icn` + `NN_name.expected` in the audit dir. Verdicts: OK / M3-or-M4 BAD / HANG / CRASH / NOASM (--compile aborted) / NOCC (gcc failed) / PROBE-BAD.
- **WHEN:** per-rung, before AND after — it is cheap (~40s), per-construct, and oracle-anchored, unlike the corpus (feature-rung-organized) and smoke (12 fixtures) suites.

### THE CLOBBER PATTERN — systemic, now named (audit target for next session)
`DRIVE_FILL` order is: emit_drive stages `g_emit.*` → `walk_bb_node` RE-DERIVES `op_sval`/`op_ival`/`op_stno`/`op_dval` from the node → template reads. **Any emit_drive staging of those four fields for an opcode outside walk's derivation lists is silently discarded.** Two instances found this session (CHARSET sval, LIMIT ival). NEXT-SESSION AUDIT: diff every `g_emit.op_{sval,ival,dval}` assignment inside emit_drive cases against walk_bb_node's preamble lists; each mismatch is a live or latent bug of this class.


**Status + remaining ladder: single source = the Watermark and the PUNCH LIST above; ground truth = the harness itself.**
