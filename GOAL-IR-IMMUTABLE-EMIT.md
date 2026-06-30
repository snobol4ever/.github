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
- **The gate that matters: `write("hello world")` and `write(1+1)` must keep working, both modes, every commit.**
  Beyond that, each TT is its own honest pass/fail — land it, document it precisely, move on.
- **`IR_t.tmp` IS the temporary slot** (not `lhs`; no `IR_TMP` opcode — see CONVERSION PLAYBOOK). Only
  value-producers carry one (`ir_node_produces_value`); control/effect ops don't.

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

**🔴 GAP — resume-gap family (TT_EVERY's keystone now works; these don't yet):**
- `TT_REPEAT`+`TT_BREAK`/`TT_LOOP_NEXT` — `repeat{…}` runs the body ONCE then exits. Root cause (diagnosed,
  not fixed): `lower_repeat` loops back through an `IR_FAIL` placeholder, which always takes ω, so
  body→placeholder→ω exits instead of re-entering. JCON `ir_a_Repeat` loops body.success/failure straight to
  `ir.start` with NO fail node — `while`/`until` happen to work because their `IR_FAIL`-exit semantics align;
  `repeat` (no failure exit) doesn't. Needs loop-back redesign, not a patch — same class of fix as `TT_EVERY`'s
  keystone (route to the real continuation, not a synthetic dead-end node).
- `TT_TO_BY` (3-arg `to ... by ...`) — IR_FAIL-stubbed; `TT_TO` (2-arg) works. Per JCON `ir_a_ToBy`: the `by`
  step is the 3rd operand of one `ir_operator("...",3,...)` — extend `bb_to`/`lower_to`'s `varby` path, which
  already builds the operands but emits no generator.

**🔴 GAP — unowned/crash:**
- `TT_ALTERNATE` (`a | b`) → `IR_ALT` unowned in `emit_drive` → **ABORT** (verified). Per JCON `ir_a_Alt`:
  pure Goto threading, bounded case. **⚠ Not a clean `bb_conj` mirror** — the chain-BFS deliberately *skips*
  alt arms (`ir_skip_alt_arms`/`ir_node_is_alt_arm`), so arms emit via a separate inline-alt cascade, not the
  main loop. `lower_alt` already builds the operand-cascade wiring.
- `TT_IDX`/`TT_MAKELIST`/`TT_VLIST` (`L:=[…]; L[i]`) → SEGV. Per JCON `ir_MakeList`+`ir_a_Sectionop`.
- `TT_FIELD`, `TT_SECTION`/`_PLUS`/`_MINUS` (`s[i:j]`) → IR_FAIL-stubbed.
- `TT_SCAN` (`s ? expr`), `TT_CASE`, `TT_SUSPEND`, `TT_CREATE` (co-expr — already ucontext-based in
  `coro_runtime.c`, not Byrd-box; needs wiring to `emit_drive`, not new design), `TT_LIMIT` — not wired into
  the new driver. (`TT_CASE`: per JCON `ir_a_Case`, decomposes to a chain of `===` relop nodes — shape 1,
  mostly LOWER work, no new template.)
- Global `TT_ASSIGN` (`global g; g:=5`) → aborts on the global arm.

**NEXT (in order):** (1) `TT_REPEAT` loop-back redesign (same root-cause class just fixed for EVERY).
(2) `TT_ALTERNATE` (mind the BFS skip). (3) `TT_IDX`/`MAKELIST` segv. (4) global `TT_ASSIGN`.

## Watermark
**2026-06-30 (Claude Sonnet 4.6) — CONVERSION PLAYBOOK written + `TT_EVERY` keystone landed.** This file
pruned to current+actionable content only (old TRACK A/B/C ladder, the driver-construction LOCKED-TECHNIQUE/
ENTRY-POINT sections, and seven stacked prior watermarks removed — all superseded by the STANDING DIRECTIVE's
"go straight to the JCON spine" pivot and by the universal driver now being long-since landed and stable;
full prior text recoverable via `git log -p` on this file). SCRIP `74281db6`. Mutation gate HARD=4 unchanged.
Icon smoke 10/12 both modes unchanged. **NEXT: `TT_REPEAT` loop-back, per the PUNCH LIST.**
