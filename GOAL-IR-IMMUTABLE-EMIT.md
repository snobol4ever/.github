# GOAL-IR-IMMUTABLE-EMIT.md — The emitter READS IR. It NEVER mutates it. (Ground Zero #5)

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
  document it precisely, move on.
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
| rbx | DESCR base pointer (dual-width 8/16-byte) |
| rbp | NV/variable-name hash table base (reserved; GET/SET still plain C calls) |
| r10 | **RETIRED** — no data-block register; `bb_regs.h` (which defined this contract) no longer exists |

*(One stray passage in ARCH-ICON.md's old ICN-SCAN section calls rbx "NV hash base" instead — that
disagrees with REGISTER-LAYOUT.md's own GOAL-FACT-RULE table and the PLAN.md banner, which agree with each
other and with this table; treat this table as authoritative.)*

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
`/home/claude/x64/bin/sbl -b file.sno` (clone `snobol4ever/x64` if absent).

**Corpus.** Icon programs: `/home/claude/corpus/programs/icon/rung<NN>_*.icn` (263, each with a sibling
`.expected`) — **not** `/home/claude/SCRIP/test/icon/` (only 8 smoke files). Full suite:
`bash scripts/test_icon_all_rungs.sh`. Fast smoke (12 programs, both modes): `bash scripts/test_smoke_icon.sh`.

**Concurrency discipline (GOAL-ICON-BB.md, condensed).** One dispatch case per IR kind; one template file
per box; edit only your own language's arms/boxes, never a peer's; a kind with no case ABORTS loud, never
silently declines. Patch-offset bookkeeping is abolished — `bb_bin_t`/hand-counted byte offsets don't exist;
patch metadata travels in-band as tagged records inside a template's returned string, walked once by
`bb_emit_x86`.

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
   `IR_TO` (`bb_to.cpp`). Partially landed 2026-06-30: `TT_EVERY` (see PUNCH LIST).
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
Coverage measured by `SCRIP_ICN_BB=1 ./scrip --run`. `TT_*` is the shared AST enum (`ast.h`); only
Icon-reachable rows listed.

**✅ COVERED:**
- Literals (`TT_ILIT/FLIT/QLIT/CSET`), `TT_VAR`, `TT_KEYWORD` (incl. `&line`/`&file`)
- Arithmetic/relop/concat binops, unary `TT_MNS/PLS/SIZE/NONNULL/NULL`
- `TT_ASSIGN` (local var only), `TT_WHILE`/`TT_UNTIL`, `TT_FNC` (builtin + zero-arg user proc), `TT_RETURN`
- `TT_IF` (statement form — JCON `ir_a_If` edge-threading, zero opcode/template). Value-context `if`
  (`write(if c then a else b)`) still wrong: then/else write distinct slots, consumer reads only then's —
  **fix is JCON's own pattern**, a single shared `target` tmp passed to BOTH branches (`ir_a_If` passes the
  same `target` var to both `ir(thenexpr,...)` and `ir(elseexpr,...)`); SCRIP currently doesn't.
- **`TT_EVERY` — keystone case landed 2026-06-30 (`74281db6`).** `every x:=GEN do BODY` (assign-wrapped
  generator + a body that just reads the loop var, e.g. `write(x)`) verified correct both modes:
  `every x:=1 to 3 do write(x)` → `1 2 3`. Was previously a dead `IR_FAIL` stub (always empty output, for
  every shape, unconditionally) — **NOT** the "1 2 3 OK, only non-trivial bodies hang" state a stale entry
  here used to claim; that was a reverted attempt, never live. **Two narrower gaps remain, both isolated +
  reproduced, NOT fixed:**
  - body containing its own value-producer (`every x:=1 to 3 do write(x*2)`) yields only the first
    iteration (`2`, not `2 4 6`). `--dump-ir` shows the expected shape (`IR_BINOP` between assign and call,
    `ω→IR_TO`) — root cause not yet bracketed; needs MONITOR-FIRST, not guessing.
  - postfix/chained-call-wrapped generator with no assignment (`every write(1 to 3)` — **this is the
    existing Icon-smoke `"every"` fixture**) also yields only the first value. `lower_call`'s chained-arg
    path only reports `cx->beta` as resumable when a `g_postfix_resume` flag is set, which it isn't here.
  - Icon smoke: 10/12 both modes, unchanged count (`every` still FAILs — it's the postfix shape above, not
    the keystone shape; `repeat_break` is a separate pre-existing gap, see below — untouched).

- **`TT_REPEAT` + `TT_LOOP_BREAK` + `TT_LOOP_NEXT` — LANDED 2026-06-30 (Claude Sonnet 4.6).** `repeat{…}`,
  `break`, and `next` all verified both modes (mode-3 == mode-4): `repeat{write("x");break}` → `x done`;
  counter-to-3 + break → `1 2 3 done`; the `repeat_break` smoke fixture → `0 1 2`. Icon smoke 10/12 → **11/12**
  both modes (only `every` postfix-shape remains). Corpus 82/289 unchanged, identical FAIL set (stash/rebuild
  diff). Mutation gate HARD=4 unchanged (LOWER-only change, gate doesn't scan it). LOWER-only, one file
  (`lower_icon.c`, 7 lines). **TECHNIQUE — see "LOOP-BACK & UNCONDITIONAL-JUMP IDIOM" below.** Root cause was
  exactly as diagnosed: the old `lower_repeat` looped back through an `IR_FAIL` placeholder whose γ-target the
  BFS *discards* (an edge pointing AT an `IR_FAIL` resolves to the chain ω-exit per `emit.cpp:1002`), so the
  body ran once then exited; `break` had the identical disease (it was an `IR_FAIL` whose loop-exit edge was
  thrown away). Fix: route the loop-back and the break/next jumps through a **real chain node** (`IR_CONJ`,
  whose driver is pure jump-to-γ and whose edges the BFS *follows*), never a sentinel terminator.
- `TT_TO_BY` (3-arg `to ... by ...`) — IR_FAIL-stubbed; `TT_TO` (2-arg) works. Per JCON `ir_a_ToBy`: the `by`
  step is the 3rd operand of one `ir_operator("...",3,...)` — extend `bb_to`/`lower_to`'s `varby` path, which
  already builds the operands but emits no generator.

**🔴 GAP — unowned/crash:**
- `TT_ALTERNATE` (`a | b`) → `IR_ALT` unowned in `emit_drive` → **ABORT** (verified). **CONFIRMED 2026-06-30
  (Claude Sonnet 4.6) against `refs/jcon-master/tran/ir.icn` directly: there is NO `ir_Alt` record/enumerator.**
  `ir_a_Alt` (`irgen.icn`) emits ONLY `ir_Goto`/`ir_IndirectGoto`/`ir_MoveLabel` chunks — alternation is PURE
  Goto threading among the arms (shape 1, same as `TT_IF`), not a value-producing node kind at all. JCON wires
  `e[i].success → ir.success` and `e[i].failure → e[i+1].start` directly; there is no intermediate "alt box."
  **`IR_ALT` as an `IR_e` enum member is therefore a SCRIP-side bookkeeping artifact** (somewhere for the 2-edge
  γ/ω model to land each arm's success, since SCRIP can't splice an edge directly into "whatever γ the ALT's
  caller passed in" the way JCON's pure-Goto form can) — not wrong on its face, but it means there is no JCON
  reference for what an `IR_ALT` *runtime box* should do, because JCON has none.
  **DEAD END, attempted + reverted this session:** wired `IR_ALT → bb_alt()` (a pre-existing, never-dispatched
  template that cascades through a frame-slot arm-counter, literal arms only, ≤32 arms) via a new
  `case IR_ALT` in `emit_drive` populating `op_parts_*`. Never built/tested; reverted unbuilt after re-reading
  `ir.icn` confirmed the premise (a literal-arm runtime cascade) has no JCON basis to validate it against —
  building machine behavior with no canonical source to check it against is exactly what RULES.md's "CONSULT
  CANONICAL SOURCES" rule exists to prevent, so it was pulled rather than landed half-verified. The
  `bb_alt.cpp` template itself is untouched (still present, still undispatched, still unverified either way).
  **REAL NEXT STEP, not yet attempted:** redesign as shape-1 pure edge-threading, JCON-faithful — `lower_alt`
  should wire each arm's success directly to the ALT's OWN passed-in γ (no IR_ALT node at all, mirroring
  `lower_if`'s `then_entry`/`else_entry` pattern) and each arm's failure to the next arm's start (already
  correct in the existing `lower_alt`). If a 2-edge node is still needed as a landing point for "this arm
  succeeded," it should do NOTHING but forward γ (a pure-thread shape, like the zero-template limit case
  `IR_CONJ`/`bb_conj` the playbook already names for `ir_conjunction`) — not own runtime cascade behavior.
  **⚠ Mind the BFS skip** — the chain-BFS deliberately *skips* alt arms (`ir_skip_alt_arms`/
  `ir_node_is_alt_arm`), so arms must emit via a separate inline cascade, not the main loop, however the
  redesign lands. `lower_alt` already builds the operand-cascade wiring (arm[i].ω→arm[i+1].start) correctly.
- `TT_IDX`/`TT_MAKELIST`/`TT_VLIST` (`L:=[…]; L[i]`) → SEGV. Per JCON `ir_MakeList`+`ir_a_Sectionop`.
- `TT_FIELD`, `TT_SECTION`/`_PLUS`/`_MINUS` (`s[i:j]`) → IR_FAIL-stubbed.
- `TT_SCAN` (`s ? expr`), `TT_CASE`, `TT_SUSPEND`, `TT_CREATE` (co-expr — already ucontext-based in
  `coro_runtime.c`, not Byrd-box; needs wiring to `emit_drive`, not new design), `TT_LIMIT` — not wired into
  the new driver. (`TT_CASE`: per JCON `ir_a_Case`, decomposes to a chain of `===` relop nodes — shape 1,
  mostly LOWER work, no new template.)
- Global `TT_ASSIGN` (`global g; g:=5`) → aborts on the global arm.

**NEXT (in order):** (1) `TT_ALTERNATE` redesign — shape-1 pure edge-threading per the corrected punch-list
entry above, NOT the `bb_alt()`/`op_parts_*` cascade (tried, reverted, no JCON basis). (2) `TT_IDX`/`MAKELIST`
segv. (3) global `TT_ASSIGN`. (4) `TT_TO_BY` 3-arg generator.

## Watermark
**2026-06-30 (Claude Sonnet 4.6) — `TT_REPEAT`+break+next landed; `TT_ALTERNATE` attempted+reverted; baseline
gate retired.** `TT_REPEAT`/`TT_LOOP_BREAK`/`TT_LOOP_NEXT` landed and verified (see PUNCH LIST entry + new
CONVERSION PLAYBOOK "LOOP-BACK & UNCONDITIONAL-JUMP IDIOM" section) — icon smoke **10/12 → 11/12** both modes,
zero regressions (289-program corpus suite stash/rebuild/diff: identical FAIL set), mutation gate HARD=4
unchanged. `TT_ALTERNATE`: wired `IR_ALT → bb_alt()` via a new `emit_drive` case, then reverted UNBUILT after
confirming directly against `refs/jcon-master/tran/ir.icn` that no `ir_Alt` enumerator/record exists — JCON's
`ir_a_Alt` is pure Goto threading with no node of its own, so the literal-arm-counter-cascade premise had no
canonical source to verify against (see corrected punch-list entry for the real next approach). The retired
"two-snippet baseline gate" directive (`write("hello world")`+`write(1+1)`, every commit) is REMOVED from the
STANDING DIRECTIVE — it was never a script (confirmed: no `scripts/*.sh` referenced it), only this file's prose;
the real per-rung signal is `scripts/test_smoke_icon.sh` + the corpus diff, both already in use above. SCRIP
`74281db6` (this session's `lower_icon.c` diff is LOCAL, NOT YET PUSHED — see push status below). Icon smoke
11/12 both modes. **NEXT: `TT_ALTERNATE` shape-1 redesign, per the PUNCH LIST.**

**2026-06-30 (Claude Sonnet 4.6) — CONVERSION PLAYBOOK written + `TT_EVERY` keystone landed.** This file
pruned to current+actionable content only (old TRACK A/B/C ladder, the driver-construction LOCKED-TECHNIQUE/
ENTRY-POINT sections, and seven stacked prior watermarks removed — all superseded by the STANDING DIRECTIVE's
"go straight to the JCON spine" pivot and by the universal driver now being long-since landed and stable;
full prior text recoverable via `git log -p` on this file). SCRIP `74281db6`. Mutation gate HARD=4 unchanged.
Icon smoke 10/12 both modes unchanged. **NEXT: `TT_REPEAT` loop-back, per the PUNCH LIST.**
