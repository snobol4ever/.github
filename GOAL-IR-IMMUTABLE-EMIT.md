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

**⚙ IR_ref_t CARRIES A NODE, NOT AN α/β BIT — THE BFS PICKS α-vs-β (verified `emit.cpp:978,984`).** An
`IR_ref_t` (`{IR_t* node; …}`) on `nd->γ`/`nd->ω` points only at a TARGET NODE. The α-vs-β selection is made
ONCE, downstream, by the chain-BFS, by exactly this test for each edge:
`label = (consumer_index > target_index && ir_is_generator_kind(target)) ? target.β : target.α`.
In English: an edge resolves to the target's **β (resume)** iff the node holding the edge sits LATER in chain
order than the target AND the target is a generator kind; otherwise it resolves to the target's **α (fresh
entry)**. So "point at α vs β as the situation needs" is achieved NOT by storing a flag in the ref but by
(1) which node you point `γ`/`ω` at, and (2) whether that node is `ir_is_generator_kind` + sits earlier. A
forward edge to a non-generator, or to any node later in the chain, is α; a backward edge to an earlier
generator is β. This is the whole DIVISION RULE in two lines of resolver. **LIMITATION you will hit:** this
expresses only STATIC resume targets; a DATA-dependent resume target (resume whichever-of-N last fired — the
unbounded-alt case) needs JCON's label variable, NOT a wider generator-kind set (see the `TT_ALTERNATE`
PUNCH LIST entry).

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
- `TT_ALTERNATE` (`a | b`) — **`IR_ALT` DELETED 2026-06-30 (Claude Sonnet 4.6); it was not a valid IR code.**
  Confirmed against `refs/jcon-master/tran/ir.icn` directly: no `ir_Alt` record/enumerator exists there.
  `ir_a_Alt` (`irgen.icn`) emits ONLY `ir_Goto`/`ir_IndirectGoto`/`ir_MoveLabel` chunks — alternation is PURE
  Goto threading among the arms (shape 1, same as `TT_IF`), never a node of its own. An `IR_ALT` node, and
  the unverified literal-arm `bb_alt()` runtime cascade an earlier pass in this same session built to consume
  it, had no canonical source to validate either against — both are now gone, not just unwired.
  **WHAT CHANGED (one session, six files, net −72 lines: 85 deleted / 13 added, zero regressions):**
  `IR_ALT` removed from the `IR_e` enum (`IR.h`) and its name-table entry (`scrip_ir.c`); `lower_alt`
  (`lower_icon.c`) rewritten to pure edge-threading — each arm lowered with γ pointing DIRECTLY at the alt's
  own caller-supplied γ (`e[i].success → ir.success`, JCON-literal) and ω at the next arm's start
  (`e[i].failure → e[i+1].start`, unchanged from before), no intermediate node built at all, mirroring
  `lower_if`'s already-landed `then_entry`/`else_entry` shape; the dead pre-emission gate this enabled
  (`alt_arms_all_simple_lit`/`alt_safe_kind`/`graph_has_alt` + their call site, `scrip.c` — could never fire
  once no graph can contain an `IR_ALT` node) deleted; the `IR_ALT` arm-walk in `binop_operand_real_static`
  (`emit.cpp`) deleted (dead, same reason); the `wintexpr` `IR_ALT` disjunct (`emit.cpp`, `bb_call_write_route`)
  deleted (a0->op can never be IR_ALT); `descr_chain_arity`'s `case IR_ALT` (`emit.cpp`) deleted (compile-error
  otherwise); `ir_is_generator_kind`'s `case IR_ALT` (`ir_query.c`, the LIVE, Makefile-built copy — load-bearing
  for the whole DIVISION RULE) deleted; the never-dispatched `bb_alt.cpp` template deleted outright + its
  Makefile line removed. `ir_node_is_alt_arm` (`emit.cpp`) collapsed to an unconditional `return 0` (still
  called from 13 BFS sites — `ir_skip_alt_arms` and the chain-walk — left AS PLUMBING rather than torn out of
  the BFS itself; touching 13 load-bearing call sites in one pass to chase a rename that's already a correctness-
  preserving no-op was judged the wrong risk/reward this session — a real follow-up, not a blocker). **Four
  files intentionally NOT touched** — `lower_snobol4.c`, `lower_raku.c`, `prove_lower.c`, `emit_per_kind_audit.c`
  — confirmed (compiler-checked, not assumed) to already fail to build for unrelated reasons (missing headers/
  stale pre-GZ#5 opcode names) and absent from the Makefile; their `IR_ALT` mentions are inert either way.
  **VERIFIED:** `scrip`+`libscrip_rt` build clean; `write(1|2)` no longer aborts, correctly prints `1` (first-
  arm-succeeds-wins is right Icon semantics for a non-generator context — `write` asks for one value); icon
  smoke 11/12 both modes unchanged; 289-program corpus suite IDENTICAL pass/fail set (82/289, stash/rebuild/
  diff) — zero regressions despite the six-file span; mutation gate HARD=4 unchanged.
  **REMAINING GAP — UNBOUNDED (resumable) alternation, e.g. `every write(1|2|3)` prints `1` not `1 2 3`.**
  The BOUNDED case is done and correct (`write(1|2)` → `1`; a bounded consumer wants one value, first-arm-wins,
  no resume — exactly JCON's `else`/bounded arm of `ir_a_Alt` where each arm success is a plain `ir_Goto` to
  `ir.success`). The unbounded case needs JCON's UNBOUNDED arm, which is a **label variable** —
  `ir_MoveLabel(t, eList[i].resume)` on each arm's success, then `ir_IndirectGoto(t)` at the alt's resume
  (`irgen.icn:183-190`, verified). **WHY A STATIC EDGE CANNOT DO THIS (proven against the live BFS, do not retry
  the `cx->beta` hypothesis — it is WRONG):** the chain-BFS resolves a consumer's ONE backtrack ref to a target's
  β ONLY via `i > k && ir_is_generator_kind(target)` (`emit.cpp:978,984`). That picks ONE static target. But a
  resumed alt must re-enter *whichever arm last succeeded* — arm 0 on the 2nd pull, arm 1 on the 3rd, … — which
  is DATA-dependent, not statically known. No widening of `ir_is_generator_kind` and no `cx->beta` arm-tracking
  can express "resume the dynamically-last-fired arm" with a single static edge; that is precisely the gap the
  label variable fills. (Literal arm's `.resume` = its failure = next-arm-start, so `t` effectively holds
  "next arm to try after the one that just produced": enter→arm0; arm0 succeeds→`t:=&arm1`,goto consumer;
  consumer backtracks→`goto *t`→arm1; …; last arm succeeds→`t:=&alt.ω`; backtrack→exhausted.)
  **REQUIRED INFRASTRUCTURE (none exists yet; this is why it's DEFERRED, not a quick patch):** (a) a frame slot
  for `t`; (b) an `IR_INDIRECT_GOTO` template (`jmp qword ptr [r12+slot]` — the enum member EXISTS, unused, no
  template); (c) a MoveLabel mechanism that emits `lea rax,[rip+<chain-label-of-another-node>]; mov [r12+slot],rax`
  — which needs the emitter to resolve the chain α-label of an ARBITRARY referenced node (templates today only
  see the BFS-provided γ/ω/β of the CURRENT node; addressing a *sibling* node's label is new). **NO `IR_ALT`
  NODE — alternation is pure Goto threading + this label variable, exactly as JCON. `lower_alt` stays the
  edge-threading shape; the label variable is added as explicit nodes (`IR_INDIRECT_GOTO` + a move-label node),
  not a generator node.** This is a multi-piece feature (label-address-of-sibling is the hard part); size it as
  its own rung, do not bolt it on.
- `TT_FIELD`, `TT_SECTION`/`_PLUS`/`_MINUS` (`s[i:j]`) → IR_FAIL-stubbed.
- `TT_SCAN` (`s ? expr`), `TT_CASE`, `TT_SUSPEND`, `TT_CREATE` (co-expr — already ucontext-based in
  `coro_runtime.c`, not Byrd-box; needs wiring to `emit_drive`, not new design), `TT_LIMIT` — not wired into
  the new driver. (`TT_CASE`: per JCON `ir_a_Case`, decomposes to a chain of `===` relop nodes — shape 1,
  mostly LOWER work, no new template.)
- Global `TT_ASSIGN` (`global g; g:=5`) → aborts on the global arm.

**NEXT (in order):** (1) `TT_ALTERNATE` resumability — the base case (first-arm-succeeds, no `IR_ALT` node)
is landed; only the generator/backtrack side (`every write(1|2|3)` should yield `1 2 3`, currently yields `1`)
remains, per the corrected punch-list entry above. (2) `TT_IDX`/`MAKELIST` segv. (3) global `TT_ASSIGN`.
(4) `TT_TO_BY` 3-arg generator.

## Watermark
**2026-06-30 (Claude Sonnet 4.6) — alt-arm plumbing PURGED from live emit.cpp; ICON-ONLY rule added; IR_ref_t
α/β resolution + alt label-variable requirement documented.** Removed the dead `ir_node_is_alt_arm` (always
`return 0`) and `ir_skip_alt_arms` (identity) helpers and ALL ~13 BFS call sites in `src/emitter/emit.cpp`
(forward decls, both definitions, every `ir_skip_alt_arms(X)→X` inline, every `if(ir_node_is_alt_arm(c))continue`
deleted) — the leftover plumbing the prior watermark called "MOOT" but left wired. Behavior-preserving (identity/
false inlined): `make scrip`+`libscrip_rt` clean, icon smoke 11/12 both modes unchanged, mutation gate HARD=4
unchanged. **The 10 stray `IR_ALT` references that remained are now 0 in live code; the rest live ONLY in parked,
build-excluded non-Icon files (`lower_snobol4.c` ×5, `lower_raku.c`, `prove_lower.c`, `emit_per_kind_audit.c`)
which reference a wholesale-dead pre-GZ#5 IR vocabulary (IR_SEQ/IR_PATTERN_*/IR_DTP_ASSIGN/IR_ALT, none in the
enum) and are OUT OF SCOPE by the new ICON-ONLY HARD RULE at the top of this file — left untouched deliberately.**
Corrected two pieces of wrong/stale doc: (1) the `TT_ALTERNATE` punch-list hypothesis ("`cx->beta` tracks active
arm") is WRONG and replaced with the proven label-variable requirement (a static edge cannot express dynamic
resume-target; `emit.cpp:978,984` is the proof); (2) the prior watermark's "LOCAL, NOT YET PUSHED" was stale
(`bfd8b744` is on origin). SCRIP commit for the emit.cpp purge is LOCAL, push BLOCKED pending credential (see
session close). **NEXT: unbounded `TT_ALTERNATE` is DEFERRED (needs the label-variable infra: frame slot +
`IR_INDIRECT_GOTO` template + sibling-label-address MoveLabel — sized as its own rung, per the PUNCH LIST). The
nearer clean wins are (1) global `TT_ASSIGN`, (2) `TT_TO_BY` 3-arg, (3) `TT_IDX`/`MAKELIST` segv.**

**2026-06-30 (Claude Sonnet 4.6) — `IR_ALT` DELETED repo-wide; `TT_ALTERNATE` base case landed.** Lon flagged
that `IR_ALT` is not a valid IR code (confirmed: no `ir_Alt` enumerator in `ir.icn`) and that the prior turn's
hand-off summary describing it as "reverted" was misleading — the unbuilt driver-case attempt was reverted, but
`IR_ALT` itself (the enum member, and every site referencing it) was still live in the tree, which is the
actual confusion being pointed at. Removed it everywhere it could be reached from the Makefile build (6 files,
−72 net lines) and rewrote `lower_alt` to the JCON-faithful pure-edge-threading shape instead of leaving a hole
— see the corrected PUNCH LIST entry above for the full file-by-file account. Icon smoke 11/12 both modes
unchanged; 289-program corpus suite identical pass/fail set (82/289, stash/rebuild/diff); mutation gate HARD=4
unchanged. `write(1|2)` now correctly prints `1` instead of aborting. SCRIP HEAD `bfd8b744` is PUSHED and on
`origin/main` (verified `git rev-parse HEAD == origin/main`, working tree clean — the earlier "LOCAL, NOT YET
PUSHED" note in this watermark was stale and is corrected here). **NEXT: `TT_ALTERNATE`
resumability (the generator/backtrack side), per the PUNCH LIST.**

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
