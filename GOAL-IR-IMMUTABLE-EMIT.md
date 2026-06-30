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
**This goal does not run, invoke, or depend on the result of any non-Icon test, smoke, or gate script —
not as a setup step, not as a sanity check, not as a "while I'm at it." This is stricter than the scope
rule above: that rule says don't *edit* another language's lowerer; this rule says don't *execute*
another language's test at all, even read-only, even one that already exists and already passes/fails.**
- **FORBIDDEN, every session, no exceptions while this rule stands:** `scripts/test_smoke_prolog.sh`,
  `scripts/test_smoke_snobol4*.sh`, `scripts/test_smoke_raku*.sh`, `scripts/test_smoke_unified_broker.sh`
  (it dispatches across languages), any `scripts/test_*` script whose name contains `prolog`, `snobol4`,
  `raku`, `rebus`, `snocone`, or `pascal`, and any other-language entry in a doc's "Session Setup"/"Per-rung
  gate" block (e.g. `GOAL-ICON-BB.md`'s Session Setup currently lists `test_smoke_prolog.sh` —
  **that line does not apply to this goal**, ignore it there too).
- **WHY:** those frontends are PARKED (see the rule above) — running their smokes produces a FAIL signal
  that means nothing for this goal (it's pre-existing, expected, and was true before this session and will
  stay true until each language gets its own GZ#5 rebuild), yet a FAIL in a terminal is the kind of thing
  that invites "should I look into that" — it is noise this goal does not pay for. **A 0/5 Prolog smoke run
  during an Icon session is not a finding, it's wasted wall-clock; don't generate it.**
- **PERMITTED — these are not "running a non-Icon test," they're shared build steps:** `make scrip` /
  `make libscrip_rt` (the build compiles all frontends because the Makefile is shared; building is not
  testing), cloning the SPITBOL `x64` oracle (referenced below for completeness, not invoked unless a
  future Icon-specific rung needs cross-checking against it), and any script whose name is `test_*icon*`
  or `test_gate_icn_*` or `test_smoke_icon.sh` — these ARE this goal's signal and stay mandatory.
- **THE ONLY GREEN SIGNALS THIS GOAL READS:** `bash scripts/test_smoke_icon.sh` (12 programs, both modes),
  `bash scripts/test_icon_all_rungs.sh` (the 289-program corpus), the four `test_gate_icn_*.sh` discipline
  gates, and `bash scripts/test_gate_emit_no_ir_mutation.sh` (language-agnostic by construction — it greps
  `src/emitter/` for op-writes, not a per-language behavior test). Nothing else is consulted to decide
  whether a change in this goal is good or bad.
- **COMPLETION TEST:** a session working this goal invokes zero non-Icon test/smoke scripts in its tool-call
  history; if one was run anyway (e.g. inherited from a stale doc's Session Setup block), its output is not
  cited as evidence for or against this goal's state.


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
explicitly (so the fallback can be deleted) is the follow-up rung. **NOTE — this does NOT solve unbounded-alt:**
a generator NODE's resume is a single static target the stamp can name; the unbounded-alt resume is DATA-dependent
(whichever arm last fired) and still needs the label variable (see `TT_ALTERNATE` PUNCH LIST).

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
- Arithmetic/relop/concat binops, unary `TT_MNS/PLS/SIZE/NONNULL/NULL` (**CORRECTED 2026-06-30:** `TT_NONNULL`/`TT_NULL`/`TT_SIZE`/`TT_MNS`/`TT_PLS` were previously broken — `ir_operand_push` was missing from the `is_unop_tt` lowering path, so `op_sa=-1` and `bb_unop` emitted nothing. Fixed in SCRIP `2d2b1ec8`.)
- `TT_ASSIGN` (local var only), `TT_WHILE`/`TT_UNTIL` (**CORRECTED 2026-06-30:** both used `IR_FAIL` as the loop-exit sentinel; BFS skips `IR_FAIL` nodes so the loop-back target was discarded — loops ran once then exited. Fixed: sentinel changed to `IR_CONJ` in `lower_while`/`lower_until`, same fix as `lower_repeat`. SCRIP `2d2b1ec8`.), `TT_FNC` (builtin + zero-arg user proc), `TT_RETURN`
- `TT_IF` (statement form — JCON `ir_a_If` edge-threading, zero opcode/template). Value-context `if`
  (`write(if c then a else b)`) still wrong: then/else write distinct slots, consumer reads only then's —
  **fix is JCON's own pattern**, a single shared `target` tmp passed to BOTH branches (`ir_a_If` passes the
  same `target` var to both `ir(thenexpr,...)` and `ir(elseexpr,...)`); SCRIP currently doesn't.
- **`TT_EVERY` — keystone case PARTIAL, claim was OVERSTATED (corrected 2026-06-30, RE-VERIFIED AND CORRECTED
  AGAIN 2026-06-30, Claude Sonnet 4.6 — the symptom has CHANGED SHAPE since the cited baseline, do not trust
  the `2e7cd455`-era description below without re-testing).** `every x:=GEN do BODY` (assign-wrapped generator
  + a body that just reads the loop var, e.g. `write(x)`) was claimed "landed/verified correct both modes" on
  the strength of `every x:=1 to 3 do write(x)` → `1 2 3`. That spot-check was misleading at the time it was
  written (baseline `2e7cd455`): `every x:=3 to 7 do write(x)` → `1 2 3 4 5 6 7` (wants `3 4 5 6 7`), the
  "consumed loop value ignores `from`, reports a counter `1..to`" framing below. **That framing no longer
  matches current HEAD (`8e296381`, this session) — re-tested fresh, not assumed:**
  - `every x:=1 to 3 do write(x)` (from=1) → prints `1` ONLY, then **terminates** (exit 0) — does NOT continue
    to `2 3` and does NOT report a `1..to` counter. Different symptom than documented.
  - `every x:=5 to 5 do write(x)` (degenerate, from==to) → correctly prints `5`. This ONE repro from the old
    description now passes — do not re-break it chasing the other two.
  - `every x:=7 to 9 do write(x)` (from≠1, from<to) → **HANGS** (`timeout 3` kills it after printing `7`
    several million times) — this is new information, not in any prior watermark; the old "reports counter
    1..to" framing would have terminated, this does not.
  - **Postfix, no-assignment shape `every write(1 to 3)` → correctly `1 2 3`, terminates cleanly, unaffected**
    (this is the smoke-test `every` fixture, which is exactly why smoke stays 12/12 despite the above — the
    smoke suite does not exercise the assign-wrapped shape at all, so its green result says nothing about
    this bug).
  - **Conclusion: this is a REGRESSION, not a never-worked construct — bisected this session (three worktree
    builds, see the corrected `TT_TO_BY` entry below for the full bisection).** `every x:=A to B do write(x)`
    worked correctly at SCRIP `f879cc78` and `baa3a592`; broke starting at `feab99c7` (the GVA-FLAT landing)
    and is still broken at current HEAD (`8e296381`) — `024abd2f`'s "fix the `feab99c7` regression" commit
    fixed a DIFFERENT collision (procedure-parameter slots) and never re-tested this repro. **This narrows the
    search space a lot: the bug is somewhere in `feab99c7`'s diff** (the GVA-FLAT driver split + the IR_VAR
    tmp-slot-gap fix it also bundled — that commit's own message admits both pieces, see its full text via
    `git show feab99c7`), not in `TT_TO`/`TT_EVERY`'s own lowering, which hadn't been touched since `f879cc78`.
    Next session: MONITOR-FIRST/gdb on `every x:=7 to 9 do write(x)` (the hanging case — more mechanical to
    bracket than the truncating one), and diff against `feab99c7`'s changed files specifically rather than
    searching `lower_icon.c`/`emit.cpp` broadly — the regression is provably inside that one commit's surface.
  - Other gaps, isolated + reproduced in prior sessions, status NOT re-verified this pass (do not assume still
    accurate, same caution as above):
  - body containing its own value-producer (`every x:=1 to 3 do write(x*2)`) yields only the first
    iteration (`2`, not `2 4 6`) as of the last time this was checked — **NOT re-verified this session, status
    unknown at current HEAD; re-test before trusting, per the caution above.** `--dump-ir` shows the expected
    shape (`IR_BINOP` between assign and call, `ω→IR_TO`) — root cause not yet bracketed; needs MONITOR-FIRST.
  - ~~postfix/chained-call-wrapped generator with no assignment also yields only the first value~~ **STALE,
    CONTRADICTED ABOVE** — re-verified this session: `every write(1 to 3)` correctly yields `1 2 3`. This line
    described the state before the "postfix `every(gen)` fixed" watermark entry further down landed; it was
    never deleted when that fix shipped. Left struck-through rather than removed so the next reader sees the
    fix is real and doesn't re-doubt it.
  - ~~Icon smoke: 11/12 both modes~~ **STALE** — smoke is 12/12 both modes as of this session (confirmed
    fresh run); see the corrected sub-bullets above for what 12/12 does and doesn't cover (it does NOT
    exercise the assign-wrapped `every x:=GEN do BODY` shape at all).

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
- **`TT_TO_BY` (3-arg `to ... by ...`) — LANDED 2026-06-30 at SCRIP `f879cc78` (Claude Sonnet 4.6), then
  REGRESSED at `feab99c7` (same day, GVA-FLAT landing), REGRESSION STILL PRESENT at current HEAD (`8e296381`)
  — bisected this session, do not re-trust "LANDED" without re-testing `every x:=A to B [by C] do write(x)`
  specifically.** `by` is `operands[2]`, a producer node (constant step → `IR_LIT_INTEGER`, variable step →
  `IR_VAR`, same path); the runtime-step arm in `bb_to.cpp` reads it from `[op_sc+8]` and does a runtime
  `cmp by,0` sign branch per `omisc.r` `toby`. At `f879cc78` this was genuinely verified correct (`every
  x:=7 to 9 do write(x)` → `7 8 9`, confirmed by re-building that exact commit in a worktree this session).
  **Bisected the regression precisely, three worktree builds, each re-tested with the same repro:** still
  correct at `baa3a592` (the segfault-fix commit immediately before GVA-FLAT) → **broken starting at
  `feab99c7`** (`every x:=7 to 9 do write(x)` now hangs, printing `7` forever) → **still broken at `024abd2f`**
  (the commit that explicitly claims to fix "the `feab99c7` regression" — it does fix the param/value-slot
  collision repros it names, `rung02_proc_add_proc`/`rung10_augop_break_repeat`, but those are both
  PROCEDURE-PARAMETER collisions; the `to`-generator hang has no procedure parameters in its repro at all, so
  it's a DIFFERENT bug that happens to share the same introduction commit, and `024abd2f`'s own commit
  message never mentions the `to`-generator case — it was not re-tested before being folded into the "fixed"
  narrative). **Current status: BROKEN, not bracketed past "introduced in `feab99c7`," root cause not yet
  found.** See the corrected `TT_EVERY` entry above for the full current-HEAD symptom matrix (from=1 truncates
  to one value and terminates; from≠1 hangs; from==to degenerate case is fine) — `TT_TO_BY`'s `by`-stepped hang
  (`every x:=1 to 9 by 3 do write(x)`, confirmed this session) is the SAME bug, not a separate one; fixing the
  plain `to` case should be attempted first and the `by` case re-tested after, not designed for independently.
  The two previously documented DEAD ENDS (params[] node-scalar; widening `ir_node_produces_value` for
  `IR_TO`) remain dead and irrelevant to this regression — neither is implicated by the bisection above.


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
- ~~Global `TT_ASSIGN` (`global g; g:=5`) → aborts on the global arm.~~ **CLOSED** — see the STATUS section
  below the PUNCH LIST; was already landed before this watermark caught up to it (SCRIP `feab99c7`).

**NEXT (in order):** (1) **`every x:=GEN do BODY` assign-wrapped-generator regression** — bisected this
session to SCRIP `feab99c7` (the GVA-FLAT landing commit); worked at `f879cc78`/`baa3a592`, broken from
`feab99c7` onward through current HEAD. `every x:=7 to 9 do write(x)` hangs; `every x:=1 to 3 do write(x)`
truncates after one value; `TT_TO_BY`'s `by`-stepped variant exhibits the identical hang — all one bug, fix
the plain-`to` case first. MONITOR-FIRST/gdb the hanging case; diff against `feab99c7` specifically (driver
split + IR_VAR tmp-slot-gap fix) rather than searching broadly — the bisection already narrows the surface.
(2) `TT_ALTERNATE` resumability — the base case (first-arm-succeeds, no `IR_ALT` node) is landed; only the
generator/backtrack side (`every write(1|2|3)` should yield `1 2 3`, currently yields `1`) remains, per the
corrected punch-list entry above. (3) `TT_FIELD`/`TT_SCAN`/`TT_CASE`/`TT_SUSPEND`/`TT_LIMIT`/`TT_SECTION*` —
the `IR_FAIL`-stubbed set, one at a time per the MECHANICAL JCON→SCRIP CONVERSION TECHNIQUE below. **`TT_IDX`/
`MAKELIST` segv and global `TT_ASSIGN` are CLOSED — do not re-pick them up; see the STATUS section below the
PUNCH LIST for what landed and where.**

## ⛔⛔ MECHANICAL JCON→SCRIP CONVERSION TECHNIQUE (Claude Sonnet 4.6, 2026-06-30) — read before starting any new TT
**This is the by-eye/by-hand recipe used this session, written up so the next session (Icon or, later, any
other language doing the same JCON-mirroring exercise) doesn't have to re-derive it.** It is a refinement of
the CONVERSION PLAYBOOK above with the actual workflow steps that playbook assumes but doesn't spell out.

### Step 0 — find the JCON procedure, read it as a literal wiring diagram
`refs/jcon-master/tran/irgen.icn` has one `ir_a_X` procedure per AST node kind (`grep '^procedure ir_a_'`
gives the full list — 47 of them, one-to-one with JCON's `a_X` AST records). Each is a `suspend
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

## ⛔⛔ CORRECTIONS TO PRIOR-SESSION CLAIMS IN THIS FILE (Claude Sonnet 4.6, 2026-06-30)
**Per Lon's standing instruction to correct any information in any MD file found to be wrong, found this
session, verified against fresh repro + gdb, not assumed:**

1. **"Global `TT_ASSIGN` aborts on the global arm" (prior watermark / GAP section) is TRUE but INCOMPLETE —
   there is a SECOND, MORE SEVERE, UPSTREAM bug that fires FIRST.** Before `emit_drive`'s `IR_ASSIGN` arm ever
   reaches its own `is_global(vn)` check (which correctly, deliberately calls `drive_unowned()`→`abort()` — that
   part of the prior description was accurate), `walk_bb_node`'s per-node preamble (lines ~745-748, run for
   EVERY node dispatched, not just `IR_ASSIGN`) unconditionally dereferences `IR_LIT(nd).sval` through
   `gva_index_of()`/`proc_slot_of()` whenever ANY global is active in the program (`g_gva_active`/
   `g_proc_direct_active`), regardless of `nd->op`. For `IR_LIT_INTEGER`/`IR_LIT_REAL` nodes, that union slot
   legitimately holds `.ival`/`.dval`, not a pointer — reinterpreting it as `const char*` and `strcmp`-ing
   against it is undefined behavior that reliably **segfaults** (confirmed via gdb: `gva_index_of(name=0x5)`,
   where `0x5` is the literal integer `5`'s bit pattern). **Practical impact: ANY Icon program with a global
   declared anywhere, that also contains an integer or real literal anywhere in its reachable chain (i.e.
   nearly every real program), crashes before reaching the documented abort.** FIXED this session (SCRIP
   `baa3a592`) — see Watermark below. The fix is upstream-of and a precondition for actually wiring global
   assign; without it, no amount of `IR_ASSIGN`-arm work would even be reachable for testing.
2. **The watermark's "corpus 82/289" figure does not match a fresh run of `bash scripts/test_icon_all_rungs.sh`
   at the SAME commit (`f879cc78`) this session, which gives 91/289** (`PASS=91 FAIL=162 XFAIL=36 TOTAL=289`,
   captured to `/tmp/baseline_pass.txt`/`/tmp/baseline_fail.txt` this session, not yet committed anywhere durable
   — re-capture if this file moves). Did not chase down why (likely a counting-convention difference between this
   script's absolute total and whatever "stash/rebuild/diff" delta-counting prior sessions used, since every
   individual rung-level claim in the watermark — e.g. the +9 FAIL→PASS list — looks self-consistent and
   plausible on its own). **Not asserting the prior figure was wrong, only that it doesn't reproduce from a
   plain script run, so it should not be trusted as the diffing baseline without re-deriving it.** Treat 91/289
   at `f879cc78` (this session, freshly captured, reproducible by re-running the script) as the baseline for any
   future regression diff until someone reconciles the discrepancy.
3. **Build note, not a doc error but worth recording:** this session's sandbox needed `apt-get install -y
   libgc-dev` (Boehm GC dev headers) before `make scrip` would link — `gc/gc.h` not found otherwise. Unrelated
   to project code; a fresh-container gap, not a regression. `gdb` also needed installing for the RULES.md
   MONITOR-FIRST methodology to be usable at all (`gva_index_of` crash bracket above used it).

## ⛔ STATUS — GVA-FLAT (global `TT_ASSIGN` write-side) and `TT_IDX`/`MAKELIST` segv are BOTH CLOSED
**Both items this section used to describe as open are done. Recorded here, not deleted outright, because
the discrepancy between this file's prose and the actual repo state was itself a real cost this session paid
to discover — worth one paragraph so it isn't paid again.**

**GVA-FLAT was landed BEFORE this session started**, in SCRIP commits `feab99c7` (the write-side template +
driver split, exactly as this section's old design specified — `bb_assign_global.cpp` mirrors
`bb_var_global.cpp`'s dual-path shape, GVA-fast `[rbx+gva_k*16]` / `NV_SET_fn` fallback, β as a no-op resume),
`024abd2f` (a same-day regression fix — a param/value-slot collision in `ir_drive_slot_assign`, gdb-bracketed,
see that commit's own message), and `1ee81ff7` (unrelated cleanup, `g_descr_flat_chain` flag removal). All
three were already pushed and on `origin/main`, working tree clean, when this session cloned the repo — this
file's watermark simply hadn't been updated to say so. **Verified this session, independently:** the exact
`gtest.icn` repro this section specified (`global g; procedure main(); g:=5; write(g); end`) prints `5`, both
modes identical; `test_gate_icn_local_no_nv.sh` LOCK 3 (which a prior watermark entry under CORRECTIONS above
documented as FAILING) now PASSES (`global uses the GVA array, 4 refs`). **Lesson for next session: this
file's prose is not the ground truth for what's landed — `git log` and a fresh gate/smoke run are. Re-derive
before trusting a "NOT yet coded" claim, the same caution the CORRECTIONS section already demands for "X
aborts" claims.**

**`TT_IDX`/`MAKELIST` segv — FIXED this session, SCRIP `8e296381`.** The leading hypothesis this section
recorded (JCON's `ir_a_ListConstructor` being a structurally distinct sentinel-threaded shape vs. SCRIP's
generic call path) was directionally right but the actual bug was sharper: `lower_call`'s `is_idx_or_list`
branch called `lc_call_argblks`, which clobbers the call node's name (`IR_LIT(call).sval`) via a union write
to `.dval` one line after the name was set, AND discards the per-argument sub-graph array it builds without
ever attaching it to the node — every downstream reader of that array reads a hardcoded null behind a guard
that can never be true. Confirmed via gdb (RULES.md MONITOR-FIRST) and against `irgen.icn:1313-1354`/`:384`
directly: `ir_a_ListConstructor`'s element chain is the SAME shape as `ir_a_Call`'s ordinary argument chain
(`L := [p.fn] ||| p.args.exprList`) — both thread already-lowered sub-expressions with sentinel bookends, no
detached sub-graph anywhere. Fix: deleted the broken special case; `TT_IDX`/`TT_MAKELIST` now fall through to
the SAME chained-arg loop every ordinary call already uses correctly — no new opcode, no new template, no
runtime change (confirmed `by_name_dispatch.c`'s `"[]"`/`"MAKELIST"` entries already expect a flat marshaled
arg array, which is exactly what the chained loop produces). `write(x[1])` on `x:=[1,2,3]` → `1`, both modes;
multi-index and empty-list also verified. Full corpus PASS 99→109 (+10), zero regressions (rigorous
before/after diff). Full detail in the commit message. **`lc_call_argblks` itself is untouched** — still used
by the parked `lower_snobol4.c`/`lower_raku.c`/`lower_pascal.c`, out of scope per the ICON-ONLY hard rule; if
those languages hit the same union-clobber bug on their own resumption, that is their own session's find, not
inherited from this fix.

**NOT in scope, still genuinely open (carried forward unchanged from the prior framing):** global
`TT_AUGOP`/`TT_REVASSIGN` (same address-resolution principle as GVA-FLAT per the `oasgn.r` reading, but verify
the AUGOP/REVASSIGN LOWER arms actually reach a global-named `IR_ASSIGN`-shaped node before assuming GVA-FLAT
covers them for free — not checked either session); unbounded `TT_ALTERNATE` (still needs the label-variable
infra per the existing PUNCH LIST entry — `ir_a_Alt`/`ir_a_RepAlt` read in full a prior session at
`irgen.icn:167-229`, nothing to correct there).

## Watermark
**2026-06-30 (Claude Sonnet 4.6) — IR_UNOP missing operand + lower_while/lower_until sentinel IR_FAIL→IR_CONJ
fixed; PLAN.md six-doc BB-CODEGEN read restored as mandatory. SCRIP `2d2b1ec8` (LOCAL — push BLOCKED pending
credential). `.github` `cafc3013` (LOCAL — push BLOCKED pending credential).** Corpus 122/289 → 129/289 (+7
PASS, zero regressions). Smoke 12/12 both modes. Mutation gate HARD=4 unchanged. Icon-only discipline gates
unchanged (prove_lower failures pre-existing, not regressions).

**THREE BUGS FIXED (all lower_icon.c, LOWER-only — zero emitter/template changes):**

1. **IR_UNOP missing `ir_operand_push`** — the `is_unop_tt` path built `IR_UNOP` and called
   `lower(cx, t->c[0], op, ω, &orr)` but never called `ir_operand_push(op, orr)`. Same defect in
   `TT_NULL`'s `IR_UNOP` arm. `bb_child0(nd)` in `emit_drive` returned NULL → `op_sa=-1` → `bb_unop()`
   emitted nothing. Fix: add `ir_operand_push(op, orr)` at both sites (one line each).
   Fixes: `TT_NONNULL` (`\expr`), `TT_NULL` (`/expr`), `TT_SIZE` (`*expr`), `TT_MNS`, `TT_PLS`.
   Verified: `rung34_null_test_nonnull_fails/null_fails/null_succeeds` all pass both modes.

2. **`lower_while` sentinel = `IR_FAIL`** — built `W = IR_FAIL(γ,ω)` as the loop-exit sentinel;
   the BFS skips `IR_FAIL` nodes (`if (c->op == IR_FAIL) continue`) so the loop-back target in
   W's operand was never enqueued. Fix: `W = IR_CONJ`, `γ_to(W,γ); ω_to(W,γ)` — same as
   `lower_repeat`'s fix (LOOP-BACK & UNCONDITIONAL-JUMP IDIOM, already documented above).

3. **`lower_until` sentinel = `IR_FAIL`** — identical disease; `U = IR_FAIL` discarded its
   loop-back operand. Fix: `U = IR_CONJ`, `γ_to(U,γ); ω_to(U,γ)`.
   Fixes 2+3: `rung09_loops_repeat_break` (until with side-effect in cond), `rung09_loops_until_while`,
   `rung09_loops_until_gen`. Mode-3 == mode-4 verified on all three.

**PLAN.md step 7 restored (`.github` `cafc3013`):** Commit `3f55a997` had added "skip this whole list and
read ORIENTATION SYNOPSIS instead" as the last bullet of step 7's BB-CODEGEN DESIGN SET. Lon's directive
(2026-06-30): the six original docs must be read — the SYNOPSIS is additive, not a replacement. Changed to
"also read the ORIENTATION SYNOPSIS — it supplements the six docs; read six first, then SYNOPSIS; do NOT
substitute." The "see ORIENTATION SYNOPSIS for authoritative description" bypass from the ARCH-SCRIP.md
annotation was also removed. All path corrections from `3f55a997` preserved.

**TT_ITERATE (`!`) — IN PROGRESS, NOT LANDED (next session's first task):**
- `bb_iterate.cpp` exists and is complete (`rt_list_bang_at(obj, idx)` loop with α/β/γ/ω).
- `bb_iterate` added to `RT_PIC_SRCS` in Makefile this session (one line; not yet committed separately —
  included in the `2d2b1ec8` working tree but NOT yet staged/committed; `git status` will show it dirty).
- Still needed: (a) add `IR_ITERATE` to `IR_e` enum in `IR.h`; (b) add to `ir_is_generator_kind` and
  `ir_node_produces_value` in `ir_query.c`; (c) wire `TT_ITERATE` → `IR_ITERATE` in `lower_icon.c`
  (replace the current stub `IR_FAIL` build with `build(cx, IR_ITERATE, γ, ω)` + `ir_operand_push(nd, orr)`
  + set `cx->beta = nd`); (d) add `emit_drive` case (op_sa=object slot, op_sb=index counter slot fresh-
  allocated, op_off=output slot via `drive_value_slot`); (e) add `walk_bb_node` dispatch → `bb_iterate(nd)`.
  Template expects `op_sa` (object), `op_sb` (idx counter at `[r12+op_sb]`, inits to 0 at α, increments
  at β), `op_off` (output DESCR_t at `[r12+op_off]`). `op_sb` needs its own fresh frame slot (not a
  value-producer slot — it's scratch storage for the counter, like `IR_TO`'s `[op_off+16]`).
- AFTER landing `IR_ITERATE`: the 16 rung13_alt_* failures (unbounded alternation) are the next
  high-yield cluster; then rung05/rung06/rung08 scan/cset families (pre-existing `bb_scan_*.cpp` templates
  need wiring via `lower_scan`).

**NEXT (in order):**
1. **`TT_ITERATE` (`!x`)** — land it per the IN-PROGRESS notes above. Verify `every write(!s)` → `a b c`
   and `every write(![1,2,3])` → `1 2 3`. Commit `Makefile` + `IR.h` + `ir_query.c` + `lower_icon.c` +
   `emit.cpp` together as one atomic "IR_ITERATE landed" commit.
2. **`TT_ALTERNATE` resumability** — unbounded `every write(1|2|3)` (label-variable infra:
   `IR_INDIRECT_GOTO` template + sibling-label MoveLabel mechanism). Sized as its own rung per punch list.
3. **Scan family** (`TT_SCAN`, `bb_scan_stmt.cpp` + the scan-builtin templates) — pre-existing templates,
   needs `lower_scan` wiring.
4. **`TT_CASE`** — current lowering uses `IR_FAIL` nodes as arm-carriers (BFS skips them); needs
   JCON-faithful rewrite as a chain of `===` relop comparisons (shape 1, pure edge-threading, no node).

**2026-06-30 (Claude Sonnet 4.6, continuation session) — every/`TT_TO_BY` slot-collision regression (DISCOVERED+
BISECTED but NOT fixed by the watermark entry directly below this one) is now FIXED + VERIFIED. SCRIP `d225d4a2`
(LOCAL — push BLOCKED pending credential, see session close), `.github` `d66a7365`.** Picked up exactly
where the entry below left off: `every x:=A to B do write(x)` with `A≠1, A<B` hangs forever printing the seed
value (`from=7,to=9` → `7,7,7,...`); `A==1` truncates to printing `1` only; `A==B` (degenerate) is fine. Root
cause, precisely: `ir_drive_slot_assign` (LOWER, `scrip_ir.c`) and the emitter's `bb_slot_alloc16_or_get`/
`bb_slot_claim` (called only from `IR_TO`'s own `emit_drive` case) are TWO INDEPENDENT ALLOCATORS over the SAME
flat-frame byte-offset space with no shared bookkeeping — `IR_TO` needs 24-32 bytes (16-byte result + 8/16-byte
`current` scratch for the int/real arms) but LOWER had zero visibility into that extra claim, so a later
value-producer's LOWER-assigned `tmp` could land inside `IR_TO`'s live scratch region: every `write(x)` inside
the loop re-copies `x`'s named-variable value over `IR_TO`'s loop counter at `[op_off+16]`, pinning it at the
seed forever (or, for `A==1`, printing it once on the way out before the next iteration's `inc` lands on stale
memory and the comparison silently exits). **Gdb-confirmed exact offsets both pre- and post-fix** (not inferred
from symptom alone) — see commit `d225d4a2`'s message for the full byte-level trace.
- **CORRECTS the prior log's item 2 ("Widening `ir_node_produces_value` to include `IR_TO`... do NOT re-attempt
  without ALSO redesigning slot sizing")** — that prior attempt and this session's working fix are NOT the same
  thing repeated a third time: the prior attempt gave `IR_TO` a bare 16-byte `tmp` (no slot-sizing change),
  which is exactly what its own writeup says was the missing half. This session's fix does the missing half:
  `IR_TO` gets a `tmp` sized for its FULL footprint (LOWER's `k` advances by 2 units = 32 bytes, not 1), AND its
  `emit_drive` arm now reads that slot via `drive_value_slot(nd)` — the same coordinated path every other
  value-producer uses — instead of staying on the separate `bb_slot_alloc16_or_get`/`bb_slot_claim` allocator,
  with `bb_flat_cursor_reserve(op_off+32)` added so the live emit-time cursor also reflects the full footprint
  for any downstream node that reads the cursor directly rather than through `drive_value_slot`.
- **This session's OWN first attempt also failed, instructively** — a LOWER-only fix (a separate running
  `extra` counter, bumped on encountering `IR_TO` in creation order, added into later `tmp` computations)
  built clean and gdb showed DIFFERENT post-fix offsets, but the hang persisted unchanged. Root cause of THAT
  failure: `IR_TO`'s own emit-time claim still read the LIVE `g_flat_slot_count` cursor independently of the
  `extra` counter — the fix shifted WHICH offsets collided without closing the gap. Caught by re-deriving the
  post-fix `.s` (not trusting the gdb numbers in isolation) and finding the collision had simply relocated to
  a new pair of offsets. Reverted in favor of the `drive_value_slot`-coordinated fix above. **Lesson for future
  sessions on this construct: verify a slot-collision fix by re-deriving the `.s`, not just by diffing
  `nd->tmp` values — two independently-shifted allocators can produce different absolute offsets that still
  collide with each other.**
- **Verification:** 3 hand-written repros (`from=7,to=9` hang; `from=1,to=3` truncation; `from==to` degenerate)
  now correct in BOTH `--run` and `--compile` modes (gcc-link-and-run the mode-4 `.s`, not just inspected).
  Icon smoke 12/12 both modes unchanged. Mutation gate `HARD=4` unchanged (zero new IR-mutation sites — the
  `IR_TO` emitter edit reads `nd->tmp`/calls existing helpers, doesn't write IR fields). Full 289-program corpus:
  PASS 109→118 (+9), FAIL 144→135, XFAIL flat at 36; rigorous diff (not eyeballed) confirms ZERO newly-broken
  tests and exactly 9 genuine fixes — `rung01_paper_compound`, `rung01_paper_mult`, `rung01_paper_paper_expr`,
  all four `rung02_arith_gen_*` tests, `rung35_block_body_every_do_block`, `rung36_jcon_primes` (a primes sieve
  — exactly the shape this bug would be expected to hang on).
- **Session housekeeping (unrelated to the fix, recorded for the next session's orientation):** removed
  `x64` and `harness` from the workspace this session (both genuinely SNOBOL4/SPITBOL-oriented per
  `REPO-harness.md`'s own Session Start block, which clones `x64`/`csnobol4` and references `.NET`/SCRIP-backend
  crosscheck adapters — neither relevant to this Icon-only goal).
- **NEXT:** the original punch list's remaining clean wins — `TT_FIELD`, `TT_SECTION`/`_PLUS`/`_MINUS`,
  `TT_SCAN`, `TT_CASE`, `TT_SUSPEND`, `TT_CREATE`, `TT_LIMIT` (check for pre-existing template infra before
  writing new — `bb_section.cpp`/`bb_suspend.cpp`/`bb_limit.cpp`/`bb_field_get.cpp`/`bb_field_set.cpp`/
  `bb_gen_scan.cpp` already exist per the CONVERSION PLAYBOOK's TT PUNCH LIST) — plus unbounded `TT_ALTERNATE`
  (still needs the label-variable infra, unchanged, sized as its own rung).


directive); GVA-FLAT/TT_IDX watermark staleness reconciled against real repo state; TT_IDX/MAKELIST segv
FIXED; `every`/`TT_TO` assign-wrapped-generator regression DISCOVERED+BISECTED (not fixed). SCRIP `8e296381`,
`.github` `bbb68169` (push status TBD — see session close).** Session opened on a fresh clone at SCRIP HEAD
`1ee81ff7` — three commits (`feab99c7`/`024abd2f`/`1ee81ff7`) ahead of what this file's previous watermark
entry (below) described as "local, push blocked." Confirmed all three were genuinely already pushed
(`git status` clean, `HEAD == origin/main`, no credential needed to discover this — only a push would have
needed one). Re-derived ground truth rather than trusting the stale prose, per this file's own STATUS section
methodology: ran a fresh 289-program corpus (`PASS=99` at `1ee81ff7`, captured to
`/tmp/baseline_2026-06-30_1ee81ff7.txt`), re-verified the GVA-FLAT `gtest.icn` repro (prints `5`, both modes
— the design this file described as "NOT yet coded" was actually done), confirmed `TT_IDX`/`MAKELIST` still
genuinely segfaults as documented. **Fixed `TT_IDX`/`MAKELIST`** (SCRIP `8e296381`, full root-cause + fix
detail in the commit message and the STATUS section above) — `lower_call`'s `is_idx_or_list` branch called
`lc_call_argblks`, which clobbers the call node's name via a union write and discards a sub-graph array that
was never attached to the node; deleted the branch, falls through to the proven chained-arg loop instead,
matching `ir_a_ListConstructor`'s actual JCON shape (same chain-of-already-lowered-elements pattern as
`ir_a_Call`). Corpus PASS 99→109 (+10), zero regressions (rigorous diff). **While verifying the doc's
`TT_TO_BY`/`TT_EVERY` claims before trusting them for the NEXT-list, found those claims are ALSO stale, but
in a different and more interesting way — not "never finished," but a genuine REGRESSION:** `every x:=A to B
do write(x)` worked correctly at `f879cc78` (verified by rebuilding that exact commit in a worktree this
session — `every x:=7 to 9 do write(x)` → `7 8 9`) and still worked at `baa3a592`, then broke starting at
`feab99c7` (now hangs/truncates) and is STILL BROKEN at current HEAD — `024abd2f`'s "fix the `feab99c7`
regression" commit fixed a different bug (procedure-parameter slot collision) and never re-tested this repro,
so the regression slipped through undetected across two more commits. Bisected via three additional worktree
builds (`baa3a592` clean, `feab99c7` broken, `024abd2f` still broken), narrowing the search surface to
`feab99c7`'s diff specifically. **NOT fixed this session** — flagging precisely (with the bisection, so the
next session doesn't have to re-derive it) was judged higher-value than rushing a fix for a regression with
two independently-confirmed introduction commits already eliminated as the cause. Icon smoke 12/12 both modes
throughout (unaffected — the smoke fixture doesn't exercise the assign-wrapped `every` shape, which is itself
now documented precisely so the green smoke result isn't misread as covering this). All four discipline gates
green, mutation gate HARD=4 unchanged. **NEXT:** MONITOR-FIRST/gdb `every x:=7 to 9 do write(x)` (the hanging
repro), diffing against `feab99c7` specifically rather than searching broadly.

**2026-06-30 (Claude Sonnet 4.6) — universal op_sval/gva_index_of segfault FIXED (upstream of global-assign);
fresh 91/289 corpus baseline captured at f879cc78; JCON→SCRIP conversion technique + corrections written up
above. SCRIP `baa3a592` (LOCAL — push BLOCKED pending credential; see session close).** Read JCON canonical
source directly for the live frontier constructs (`ir_a_Alt`/`ir_a_RepAlt` for unbounded alternation,
`ir_a_ListConstructor` for MAKELIST, `ir_a_Sectionop` for TT_SECTION, `ir_a_Global`/`ir_a_Ident` for the
global/local var-reference model, `ir.icn` confirming no `ir_Alt` record exists — corroborating the prior
session's `IR_ALT` deletion) and the C runtime (`oasgn.r`'s `GeneralAsgn`, `rmacros.h`'s `VarLoc`/`Offset`,
`fstruct.r`'s `list()`) to ground every open punch-list item against authoritative source rather than prose.
Set up `refs/icon-master`+`refs/jcon-master` from the user's uploaded canonical-source zips (matches the exact
paths RULES.md/this file already cite). Investigated global `TT_ASSIGN` (the punch list's documented gap):
reproduced with gdb per RULES.md MONITOR-FIRST, found the actual bug is upstream and more severe than
documented (segfault, not abort — see CORRECTIONS above), fixed the upstream segfault, designed (but did not
yet code) the full write-side wiring to the pre-existing `bb_gvar_assign*`/`bb_var_global` template family.
**PROVEN:** icon smoke 12/12 both modes unchanged (byte-identical to pre-session baseline); mutation gate
HARD=4 unchanged (fix is reads-only on IR, scoped to existing `g_emit` preamble); fresh corpus baseline
captured (91/289 at unchanged commit, available at `/tmp/baseline_pass.txt`/`baseline_fail.txt` this session —
re-capture if stale). **NEXT:** code the GVA-FLAT rung exactly as designed above (driver split + new
`bb_assign_global.cpp` template, mirroring `bb_var_global.cpp`'s shape); then `TT_IDX`/`MAKELIST` segv (leading
hypothesis: generic-call-path vs. JCON's sentinel-threaded list-constructor shape mismatch, per
`ir_a_ListConstructor` reading above); then continue down the `IR_FAIL`-stubbed set
(`TT_FIELD`/`TT_SCAN`/`TT_CASE`/`TT_SUSPEND`/`TT_LIMIT`/`TT_SECTION*`/`TT_SWAP`/`TT_LCONCAT`/`TT_REPALT`) one
at a time per the MECHANICAL JCON→SCRIP CONVERSION TECHNIQUE above, landing each construct's bounded/simple
case before its generator/unbounded case where the two are separable. Unbounded `TT_ALTERNATE` remains
correctly deferred pending the label-variable infrastructure (frame slot + `IR_INDIRECT_GOTO` template +
sibling-label-address resolution), unchanged from prior analysis, now independently corroborated against
`ir_a_Alt`/`ir_a_RepAlt` source directly.

**2026-06-30 (Claude Sonnet 4.6) — TO from-ignoring bug ROOT-CAUSED + FIXED; TO BY landed (operand[2]
runtime step); postfix `every(gen)` loop-back fixed. SCRIP `f879cc78`, corpus `d77fb618` (LOCAL — push
BLOCKED pending credential; see session close).** The from-ignoring `to`-generator bug (every prior watermark
bracketed it to "the runtime value" and prescribed gdb) was NOT a runtime-value bug — it was a CONTROL-FLOW
bug, found by gdb on the emitted box exactly as RULES prescribes: a breakpoint at the IR_TO α
(`bb3_α`/`xchain0_n2_α`) NEVER FIRED because the `to`-operand's forward feed edge into IR_TO was being
α/β-stamped as **β** by `build()`/`γ_to` (which stamp any edge whose TARGET is `ir_is_generator_kind` as a
resume edge). So control entered the generator at its β (resume = `inc current; loop`) on the FIRST and only
forward pass, **skipping the `current := from` seed entirely** — `current` started at frame garbage/0, got
`inc`'d to 1, and counted 1..to. The asm was "slot-plumbed correctly" (prior watermark was right about that)
but the box entered at the wrong PORT. **Fix (`lower_to`, `lower_icon.c`): re-stamp the operand-feed edge
to α with `lc_γ_to` after lowering** — mirroring JCON `ir_a_ToBy` where `toexpr.success → byexpr.start` (a
start/α edge, never a resume). The generic "target-is-generator ⇒ β" heuristic is correct for a downstream
CONSUMER's backtrack edge but wrong for the forward OPERAND-FEED edge that constructs/seeds the generator;
they must be distinguished, and LOWER is where that knowledge lives.
- **TO BY landed** (was an `IR_FAIL` stub) via the goal file's prescribed by-as-operand[2] technique, all three
  files: LOWER builds `IR_TO` and pushes `by` as `operands[2]` (a producer node — NOT a node scalar; the
  scalar-on-node aliasing was the documented dead end), chaining from→to→by→generator with α-restamps on the
  forward edges; DRIVER (`emit_drive IR_TO`) reads `operands[2]` into `op_sc` (−1 ⇒ plain `to`, step 1);
  TEMPLATE (`bb_to.cpp`) gains a runtime-step integer arm — loads `by` from `[op_sc+8]`, does a RUNTIME
  `cmp by,0` sign branch (canonical `omisc.r` `toby`: `by>0` ascending, exit when `current>to`; `by<0`
  descending, exit when `current<to`), and advances `current += by` on resume. **Variable step works for free**
  (`k:=2; every x:=1 to 9 by k` → `1 3 5 7 9`) because `by` is just another producer operand. Verified +/−/
  degenerate steps, both modes identical.
- **postfix `every(gen)` fixed** (`every write(1 to 10 by 3)`, the empty-`every`-body shape — also the Icon
  smoke `every` fixture): the empty body was lowered to an `IR_SUCCEED` sentinel whose loop-back edge the
  chain-BFS DISCARDS (an edge pointing at `IR_SUCCEED` resolves to the proc γ-exit, `emit.cpp:1001-1002`), so
  the call's success jumped to `main_γ` and terminated after ONE value. Fix (`lower_every`): for empty `B`,
  route the loop-back through a REAL `IR_CONJ` node (γ=ω=gen_beta) — the same real-node-not-sentinel idiom the
  LOOP-BACK PLAYBOOK section already documents for repeat/break/next — so the BFS follows the edge back to the
  generator resume. JCON `ir_a_Every` defaults an empty body to `a_Key("fail")` whose success+failure both go
  to `expr.resume`; this is the stackless realization.
- **PROVEN (per-program harness, pristine-baseline build vs this build, identical harness):** Icon smoke
  **11/12 → 12/12 both modes** (first time fully green); corpus **+9 FAIL→PASS, ZERO PASS→FAIL** —
  `rung01_paper_to5`/`paper_to_by`/`paper_lt`, `rung07_control_to_by`, `rung02_arith_gen_range`,
  `rung16_seqexpr_gen_basic`/`subscript_sub_every`, `rung34_null_test_nonnull_in_every`,
  `rung10_augop_break_repeat`. Mode-3==mode-4 verified on every case. Discipline gates green (no-stack 0,
  one-reg 0, semicolon-prison PASS); mutation gate **HARD=4 unchanged** (emitter `IR_TO` edit is reads-only;
  gate doesn't scan LOWER). `.s` regenerated (`corpus/benchmarks/icon/version.s`). **NEXT:** the original punch
  list's remaining clean wins — `TT_IDX`/`MAKELIST` segv, global `TT_ASSIGN`, and the value-context `if`
  shared-target tmp — plus unbounded `TT_ALTERNATE` (still needs the label-variable infra, unchanged).

**2026-06-30 (Claude Sonnet 4.6) — legacy slot-alloc fallback BOMBED for genuine value-producer gaps; TT_TO_BY
attempted+reverted twice (params array, then `ir_node_produces_value` widening — BOTH WRONG, see below); pre-existing
`from`-ignoring `to`-generator bug found, bracketed, NOT fixed. SCRIP `<pending — see commit below>`.**
- **`drive_value_slot`'s legacy `bb_slot_alloc16` fallback is now SCOPED, not blindly removed.** Lon directive: "remove
  the fallback, make it a bomb." First attempt bombed unconditionally — broke smoke 11/12→6/12 (`bare_if`, a trivial
  `if`/`write` program with no generator anywhere, hit it too: `IR_ASSIGN`'s own driver arm legitimately calls
  `drive_value_slot` for a staging slot even though `IR_ASSIGN` is correctly NOT in `ir_node_produces_value` — that's
  by design, not a gap). **Corrected: the bomb fires ONLY when `ir_node_produces_value(nd->op)` is true** (the registry
  itself says this node should own a `tmp`) **and no `tmp` was found** — that combination is unambiguously a LOWER bug
  (a value-producer the registry claims is covered but isn't). Nodes the registry doesn't claim (assign-staging, etc.)
  still legacy-alloc exactly as before — unchanged, not a regression target. Verified: smoke 11/12 both modes restored
  (byte-identical to baseline), full corpus 82/289 byte-identical FAIL/PASS set (rigorous diff, not eyeballed), all
  four icn gates green (no-stack 0, one-reg 0, semicolon-prison PASS, mutation HARD=4 unchanged).
- **IMPORTANT — this bomb does NOT cover `IR_TO`** (and will not fire for it), because `IR_TO` is NOT in
  `ir_node_produces_value` (see below) — it still silently legacy-allocs via `bb_slot_alloc16_or_get` in its OWN
  `emit_drive` case (a different, intentional call, for re-walk idempotency — do not confuse the two). The from-ignoring
  bug (next item) is therefore UNAFFECTED by this change, proven by direct re-test.
- **TT_TO_BY — TWO WRONG ATTEMPTS, BOTH REVERTED, DO NOT REPEAT EITHER:**
  1. *Params array on the IR node.* Added `IR_t.params[]` (a union array) to carry the constant `by` step, because the
     single `union{sval;ival;dval;}` was already spent on the `"ag"`/`"ar"` int-vs-real discriminator (`IR_LIT(to).ival
     = step` aliased the discriminator pointer → wild step → segfault). **Lon corrected this directly: `by` is a THIRD
     OPERAND, full stop — nothing is ever stored as a scalar value ON an IR node for this.** `params[]` was removed
     entirely (`IR.h`/`scrip_ir.c`/`emit.h` reverted). The correct technique (by-as-operand[2]) is below and STILL
     UNIMPLEMENTED — it's blocked on the bug in item 3.
  2. *Widening `ir_node_produces_value` to include `IR_TO`.* Tried giving the generator its own `tmp` like every other
     producer. Built clean, smoke unchanged, but did NOT fix the from-ignoring bug (just shifted slot layout) — REVERTED.
     Also WRONG in principle even if it had "worked": `ir_tmp_slot_assign` grants a flat 16 bytes per producer, but the
     integer generator's `bb_to.cpp` arm uses `[off+16]` as current-value scratch BEYOND that 16 bytes — a 16-byte tmp
     here would alias the NEXT node's slot. `IR_TO` needs >16B and must keep using `bb_slot_alloc16_or_get` (its own
     `emit_drive IR_TO` case already does this correctly) — it should NOT be added to `ir_node_produces_value` without
     ALSO redesigning slot sizing, which is out of scope for a tmp-discipline cleanup. Do not re-attempt without that.
  3. **⛔ BLOCKING BUG (confirmed, bracketed to the RUNTIME VALUE, not slot wiring) — must be fixed FIRST:** on the
     UNTOUCHED baseline, `every x:=A to B do write(x)` prints a COUNTER `1,2,…,B`, ignoring `A` entirely. Repro:
     `every x:=7 to 9 do write(x)` → `1 2 3 4 5 6 7 8 9` (wants `7 8 9`); `every x:=5 to 5 do write(x)` → `1 2 3 4 5`
     (wants `5`); `if x:=7 to 9 then write(x)` → `1` (wants `7`); `every write(7 to 9)` → `1`. The WATERMARK ENTRY
     BELOW THIS ONE ("`TT_EVERY` keystone landed") is THEREFORE CORRECTED (see its own entry, edited in place) — it
     was only ever spot-checked at `from=1`, where the counter and the true sequence coincide and the bug is invisible.
     Asm inspection (mode-4 `.s` for `7 to 9`) shows the SLOTS are wired correctly — `bb_to`'s `α` reads the from-
     operand's value at `[from_tmp+8]` and stores it as `current`; the fault is downstream of that, in what VALUE ends
     up there or what overwrites it across resumes. **NEXT: gdb on the emitted `IR_TO` box — breakpoint at its own `α`
     chain-label, inspect `[current]` written on first pass and after each `β` resume, compare against what `write`
     reads. Icon has no 2-way monitor (that's SNOBOL4-specific); this is the RULES.md gdb-breakpoint-hit-count
     methodology applied directly to the emitted box.** Once fixed, `TT_TO_BY`'s by-as-operand[2] technique (LOWER:
     drop the `varby` special-case, always `ir_operand_push(to, lower(t->c[2]))`; DRIVER: `op_sc = bb_slot_get(operands[2])`;
     TEMPLATE: runtime `add [cur], [op_sc+8]` + a runtime `cmp by,0` sign branch replacing the compile-time `jg`/`jl`
     choice) is a short, mechanical, verifiable follow-on — do not implement it before this bug is green, its output
     cannot be trusted.
  - **SECOND pre-existing bug found alongside, undiagnosed:** `--dump-ir` SEGFAULTS on `to-by`/`seq` shapes (the
    `IR_FAIL`-stub generator nodes) — the dumper can't be used to inspect these constructs until it's fixed separately.


reconstruction, no safety net. SCRIP `2e7cd455`.** Following `bb70a841` (which added the `IR_ref_t.sz` stamp
but kept the old `i>k && generator-kind` guess as a fallback "for safety"), Lon directive: remove the net —
an un-stamped edge should ABORT or visibly misroute, not silently guess, so a gap is found and fixed instead
of hidden. Deleted BOTH positional mechanisms: the main γ/ω resolution guess AND the secondary BINOP-omega-
routing patch (the `i > omega_k && nodes[omega_k]->op==IR_BINOP` correction). The chain-BFS now does exactly
ONE thing per edge: read `nd->γ.sz`/`nd->ω.sz`, route to `betas[k]` if `"β"`, else `lbls[k]`. **PROVEN
(not assumed):** full Icon corpus PASS=82/289 — byte-identical to the fallback-retained and original
baselines; icon smoke 11/12 both modes unchanged; mutation gate HARD=4 unchanged; no-stack/one-reg gates 0.
Zero divergence means LOWER's stamps already covered every edge the corpus exercises — the fallback was dead
weight, never a real safety net. **FOUND, NOT FIXED (pre-existing, unrelated to this change — confirmed by
testing at the PRIOR commit `bb70a841`, where it already fails the same way, worse — segfault):**
`scripts/test_gate_icn_local_no_nv.sh` LOCK 3 fails — an Icon program with a global var does not route through
the GVA `[rbx+k*16]` array in mode-4 (`rbx refs=0`), contradicting the GOAL-ICON-BB.md GVA-2 "DONE" claim;
this is the global-storage rung's drift, not an α/β-stamping regression, and is left for its own session.
SCRIP commits `443cdec5`+`bb70a841`+`2e7cd455` — push status confirmed by `handoff_status.sh` at session
close, not asserted here. **NEXT:**
(1) stamp the remaining resume sites that may be relying on the now-deleted fallback in PATHS NOT YET COVERED
BY THE 82-PASS CORPUS (the 171 FAILs/36 XFAILs were never proven stamp-correct — only verified NOT TO REGRESS;
if a future rung's program hits an un-stamped resume edge it will misroute/abort LOUDLY now, which is correct
per directive — fix the stamp at that LOWER site when found, do not re-add a fallback); (2) re-investigate the
LVA-1 LOCK 3 drift; (3) unbounded-`TT_ALTERNATE` via the label variable (own rung, per PUNCH LIST).

**2026-06-30 (Claude Sonnet 4.6) — IR_FIELD_SET + IR_PROC_GEN + IR_SUSPEND (WIP) dispatch; mode-4 link fixed. SCRIP `44c0da0f` (push BLOCKED pending credential).** Smoke 12/12 both modes, corpus 122/289, mutation gate HARD=4 unchanged, discipline gates 0.

**Mode-4 link broken for ALL programs FIXED:** `bb_field_get.cpp`, `bb_field_set.cpp`, `bb_suspend.cpp` were compiled as separate `.o` files but absent from `RT_PIC_SRCS` (the `libscrip_rt.so` source list) — `emit.cpp` (which IS in the `.so`) references all three, causing `undefined reference to bb_field_get[abi:cxx11]()` on every link. Added all three to `RT_PIC_SRCS`. Mode-4: 0/12 → 12/12.

**`IR_FIELD_SET` (field write `p.x := v`) fully landed:** IR.h enum entry; name table; `lower_icon.c` TT_ASSIGN lhs==TT_FIELD wired to `IR_FIELD_SET` (was `IR_FAIL` stub); `emit.cpp` op_sval allowlist + `walk_bb_node` dispatch (→`bb_field_set()`) + `emit_drive` arm (op_a_slot=obj, op_sb=rhs, op_sval=field name, no own tmp). `bb_field_set.cpp`: added `cmp eax,99 / je ω` fail-check (same as `bb_field_get`). Verified both modes: `p.x := 99; p.y := 77; write(p.x); write(p.y)` → `99 77` both modes. Corpus +4 PASS.

**`IR_SUBSCRIPT` removed from `ir_node_produces_value`:** dead opcode — JCON has no `ir_a_Subscript` procedure (verified against `refs/jcon-master/tran/irgen.icn`); `TT_IDX` already routes through `IR_CALL("[]")` since commit `8e296381`. Removing it eliminates a spurious tmp-slot claim on a node that will never appear in any live Icon IR graph.

**`IR_PROC_GEN` dispatch landed:** was aborting `op=28` at the clean baseline (no `walk_bb_node` or `emit_drive` arm). Fixed: op_sval allowlist (`|| nd->op == IR_PROC_GEN`); op_ival uses `n_operands` (not `IR_LIT.ival`); `walk_bb_node` joined to call family → `bb_call(nd)`; `emit_drive` joined to call family arm; `scrip.c` `rhs_kind_ok` added `IR_PROC_GEN` (generator call result passable as rhs in pre-emission filter, same as `IR_TO`). **ROUTING NOTE:** `lower_call` now builds `IR_PROC_GEN` directly for user-defined generator procs (`icn_proc_is_generator(name)` only — NOT the hardcoded `upto`/`find`/`key` names in `icn_call_allow_gen`, which are builtin scanning functions (`bb_scan_upto.cpp`, `bb_scan_find.cpp`, etc.) that must stay `IR_CALL` for the `icn_scan_kind_for` retag path). Also: last arg's feed edge into `IR_PROC_GEN` re-stamped to α via `lc_γ_to` (was auto-β-stamped by `build()` since the target is generator-kind — same bug class as `TT_TO`'s from-ignoring fix); `cx->beta = call` (the `IR_PROC_GEN` node) so `lower_every` routes `body.success` back to the generator's β (resume port), mirroring `lower_to`'s `cx->beta = to`.

**`IR_SUSPEND` (user-defined generator `suspend expr do body`) — WIP, caller side correct, generator-body iteration not yet working:** IR.h enum; name table; `lower_icon.c` TT_SUSPEND wired to `IR_SUSPEND` (was `IR_FAIL` stub, `dval=1.0` marker); `emit.cpp`: op_sval allowlist; `walk_bb_node` dispatch → `bb_suspend()`; `emit_drive` arm (op_sa=expr slot, lbl_t0/lbl_t0_p from `g_suspend_dobody_beta`); BFS do-body enqueue — `operands[1]` (the do-body entry) queued in both BFS passes so the do-body chain joins the flat chain; `g_suspend_dobody_beta` lookup (finds operands[1]'s `lbls[k]` = do-body α-label, set before `emit_drive`); chain-tail `lbl_β` trampoline: when an `IR_SUSPEND` is in the chain, `lbl_β` jumps to that node's individual `betas[i]` instead of `lbl_ω` — this is the proc-slab resume entry (prologue `jmp flat_lbl_β` on `entry=1`). **VERIFIED (mode-4 asm):** caller in `main` is correct — LIT_4 feeds `n1_α` (`rt_proc_call_gen`), write success backtrack routes to `n1_β` (`rt_proc_resume_gen`), `proc_upto_β` trampolines to `xchain0_n6_β` (the suspend's do-body entry). **REMAINING BUG (next session):** the generator body (`upto`'s while-loop + suspend) yields only the last value — the proc-slab resume entry fires but the suspend re-entry iterates to exhaustion in one call rather than yielding one value per resume. Root not bracketed; MONITOR-FIRST/gdb on the upto proc slab with `entry=1` is the next step. Clean baseline also aborted (`op=28`, no `IR_PROC_GEN` dispatch) — `DESIGN-ICON-SUSPEND.md`'s "DONE" is stale since GZ#5 rewrite; this is a GZ#5 regression not introduced by this session.

**NEXT (in order):** (1) `IR_SUSPEND` generator iteration bug — gdb the upto slab with `entry=1`, the `bb_suspend` template + proc prologue asm are correct per inspection, bug is in how the while-loop re-arms after the do-body runs; (2) `TT_ALTERNATE` resumability (label-variable infra, unchanged from prior watermark); (3) remaining `IR_FAIL`-stubbed set: `TT_SECTION`/`_PLUS`/`_MINUS`, `TT_SCAN`, `TT_CASE`, `TT_LIMIT` (pre-existing `bb_scan_*.cpp` templates for the scan builtins — `bb_scan_upto`, `bb_scan_any`, `bb_scan_many`, `bb_scan_find`, `bb_scan_match`, `bb_scan_tab`, `bb_scan_move` all exist, need wiring).

**2026-06-30 (Claude Sonnet 4.6) — IR_SUSPEND binary-mode fix: resume-slot machinery now works in JIT (mode-3) and compile (mode-4). SCRIP `90dc36b7` pushed.** Smoke 12/12 both modes, mutation gate HARD=4 unchanged.

**Root cause of IR_SUSPEND infinite-loop:** The resume-slot machinery (frame-slot init, per-suspend β-pointer store, `proc_gen_β` indirect-goto trampoline) was **text-mode only** — all three paths used `emit_text_n`/`snprintf` strings that are silently dropped in binary JIT mode. In binary mode the gen proc had `jne → instant-succeed` on every resume (entry=1 → `jmp 0x8d: mov eax,1; ret`), reading stale DESCR from frame[0] (the last-stored integer, always 2 in a 1/2/3 generator). Diagnosis path: strace showed 100K `write(1,"\n",1)` calls; gdb backtrace identified `try_call_builtin_by_name(fn="write")` as the caller from JIT code; disassembly of the gen proc slab confirmed `jne → 0x8d` with no resume-slot stores; `0x55776c` = `rt_proc_resume_gen` confirmed the resume call was correct but the slab didn't implement the indirect-goto.

**Three fixes (emit.cpp + bb_suspend.cpp):**
- `emit.cpp` resume-slot init (was `if (g_is_text)`): added `else` binary branch: `ef_b3(0x48,0x8D,0x05)` + `bb_emit_patch_rel32(betas[first_suspend])` + `ef_b4(0x49,0x89,0x84,0x24)` + `bb_emit_u32(slot)` — `lea rax,[rip+β0]; mov [r12+slot],rax`.
- `emit.cpp` `proc_gen_β` trampoline (was `emit_text_n`): added `else` binary branch: `ef_b4(0x49,0xFF,0xA4,0x24)` + `bb_emit_u32(slot)` — `jmp qword ptr [r12+slot]`.
- `bb_suspend.cpp` per-suspend β-store (was raw `snprintf` string appended to binary buffer — parsed as garbage tags): gated on `!MEDIUM_BINARY`; BINARY path uses `x86_Lrec(48 8D 05)` + `x86_Jrec(X86T_TGT1)` + `x86_Lrec(49 89 84 24 <slot_u32>)` so `bb_emit_x86` patches `_.lbl_t1_p` (this suspend's own β) via the J-record mechanism.

**Verified:** `every x := gen() do write(x)` with `gen()` suspending 1, 2, 3 now prints `1\n2\n3` correctly in both modes. The indirect-goto resume chain works: each suspend's α stores its own β into the resume slot before yielding; `proc_gen_β` does `jmp [r12+slot]`; on resume the right β fires and advances to the next suspend or exhausts.

**NEXT (in order):** (1) `suspend EXPR do BODY` (lbl_t0 ≠ NULL path) — test with an actual do-body; (2) `TT_ALTERNATE` resumability (label-variable infra); (3) remaining `IR_FAIL`-stubbed set: `TT_SECTION`/`_PLUS`/`_MINUS`, `TT_SCAN`, `TT_CASE`, `TT_LIMIT`.

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
