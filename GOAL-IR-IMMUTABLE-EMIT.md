# GOAL-IR-IMMUTABLE-EMIT.md — The emitter READS IR. It NEVER mutates it. (Ground Zero #5)

## ⛔ FACT RULE — THE EMITTER NEVER MUTATES AN IR NODE

**The IR is the language-independent CONTRACT and it is READ-ONLY at emit time.** The emitter
(`src/emitter/**`) dispatches on `nd->op` and reads `nd`'s fields. It does **NOT** write `nd->op`,
does **NOT** write `IR_LIT(nd).*` / `IR_EXEC(nd).*` on an input node, does **NOT** synthesize IR
nodes, and does **NOT** consult the RUNTIME (`rt_*`) to decide IR shape. Every specialization
decision — which operand source, which call target, which match step — is made in LOWER (per-language,
where language belongs) and is BAKED INTO THE IR SHAPE the emitter receives. The emitter then only
walks and emits.

**WHY THIS RULE EXISTS (the violation that triggered Ground Zero #5).** `emit_bb.c` was found to
mutate IR at **34 sites**: a "save op / swap op / emit / restore op" idiom that breaks ONE generic
`IR_BINOP` into SEVEN templates by inspecting operands at emit time (the exact one-IR→many-BB pattern
that was explicitly rejected), plus PERMANENT `IR_CALL` retags driven by **runtime queries**
(`rt_proc_is_registered`/`rt_builtin_is_known`/`rt_proc_is_generator`) at emit time, plus pattern-match
retags, plus `IR_LIT` field writes. The blessed pattern is the opposite and already exists:
`bb_lit_scalar` takes FOUR literal opcodes → ONE box; the general `bb_binop_arith` reads operand SLOTS.
Operands are producer boxes; the consumer reads slots; the operation opcode is **source-agnostic**.

**GATE:** `scripts/test_gate_emit_no_ir_mutation.sh` (comments stripped), over all of `src/emitter/`:
  - `[-]>op[[:space:]]*=`  (op writes)  == 0
  - `IR_LIT([^)]*)\.[a-z_]+[[:space:]]*=` on an input node  == 0 (scratch-node builders exempt only if
    a clearly-marked fresh-allocation helper — ideally also zero)
  - emit-time `rt_*` calls used to choose an opcode/shape == 0
**COMPLETION TEST:** gate reads 0; `emit_core.c` + every template already read 0 (verified 2026-06-27);
existing suites green (Icon 212, SNOBOL4 m4 7/7, Prolog 5/5, Raku 192, Pascal smoke 25) or per-rung
LOUDLY red while a family is mid-migration (breaking is authorized — the gate + suites are the recovery target).

---

## Verified baseline (2026-06-27, Opus 4.8) — gate-measured, ALL in `src/emitter/emit_bb.c`

Gate `scripts/test_gate_emit_no_ir_mutation.sh` reports the canonical count: **45 hard mutations**
(A = 34 op-writes including the swap-restores + B = 11 `IR_LIT`/`IR_EXEC` field-writes) + C = 19
informational runtime-query refs (IRM-4). `emit_core.c` = 0, all BB/XA templates = 0 op-writes.
The disease is one file. The table below lists the 24 DISTINCT retag decisions (the 34 op-writes =
these 24 sets + their ~10 `->op = _sk` restores).

| Family | sites | kind | target ops / detail |
|--------|-------|------|---------------------|
| **F1 operand-source fusion** | 14 | temporary swap+restore | `IR_BINOP_GVAR_ARITH` ×6 (L2288,3065,3074,3083,3092,3101), `_GVAR_ARITH_SLOT` ×2 (L3120,3139), `_GVAR_RELOP` (L3165), `_GVAR_CONCAT` (L2267), `IR_UNOP_GVAR_SLOT` (L3316), `IR_ASSIGN_DESCR` (L2599), `IR_LIT_I` (L2295), `IR_BINOP` restore (L3204) |
| **F2 call routing** | 7 | **permanent + queries runtime** | `IR_CALL`→`IR_PROC_GEN`/`IR_CALL_PROC_STAGED`/`IR_CALL_BUILTIN`×3/`IR_CALL_GVAR_USERPROC` (L3321,3736–3751), chosen via `rt_proc_is_*`/`rt_builtin_is_*` at emit time |
| **F3 pattern-match retag** | 3 | retag (SNOBOL4) | `IR_MATCH_HEAD`/`IR_MATCH_RETRY`/`IR_MATCH_ADVANCE` (L2523,2528,2551) |
| **F4 `IR_LIT` field writes** | 10 | field write | need per-site triage: scratch-node init vs real-node mangle |

Enabling facts already true: Icon binop operands are producer boxes via `operand_aux` (Icon already
escaped F1 for arith); `bb_var_global` writes a result slot in BOTH GVA (`[rbx+k*16]`) and NV-hash
(`NV_GET_fn`) arms; the general `bb_binop_arith` reads operand slots `[r12+off]`. SNOBOL4 wires binop
operands as DIRECT `c[]` children (which is what trips F1) — that is the per-language gap to close.

---

## ⛔ THE TARGET IS THE CANONICAL REDUCED SET — JCON's 33 IR INSTRUCTIONS (per language, near its minimum)

**JCON (`refs/.../irgen.icn`) compiles ALL of Icon with exactly 33 IR instructions** — the complete
reduced set: `ir_Assign` (ONE, no LIT/VAR/CALL/CONCAT/DESCR variants), `ir_Call` (ONE, no staged/builtin/
gen/gvar variants — invocation resolves the callee value), `ir_OpFunction` (ONE — EVERY operator is a
function, so binop, unop, AND operator-string invocation `o("+")` all go through it), the four literals
`ir_{Int,Real,Str,Cset}Lit`, the storage refs `ir_{Var,Global,Field,Tmp}`, control `ir_{Goto,IndirectGoto,
Label,MoveLabel,TmpLabel}`, the goal-directed core `ir_{Succeed,Fail,ResumeValue,Move,Deref}`, structure
`ir_{Record,MakeList,Function,Key,Link,Invocable,EnterInit}`, co-expr `ir_{Create,CoRet,CoFail}`, and
`ir_{ScanSwap,Unreachable}`. **`ir_Tmp` IS the slot** — every value lives in a tmp produced by some node and
consumed by reading it. No operand-source in the opcode; the SOURCE is whichever node produced the tmp.

**SCRIP today = 224 IR opcodes (7×).** The bloat is operand-source variants (`IR_*_GVAR_*`, `IR_ASSIGN_<src>`),
emit-time call-routing retags, and cross-language accretion. **The clean target: each language's IR set ≈ its
canonical minimum (Icon → ~33), and ONE BB per instruction, each a slot-producer/consumer.** Operators unify
under `ir_OpFunction`/Invoke — which delivers indirect invocation for free. This is the reduced BB set too.

**COMPLETION TEST (Icon):** `./scrip --dump-ir prog.icn` over the corpus uses only instructions in the
JCON-33 set (or a justified, documented superset); no operand-source opcode variant survives; one BB per
instruction. Do this BEFORE the per-language sessions spin up — a clean reduced set is the shared spine they build on.



- [ ] **IRM-0 — GATE.** Write `scripts/test_gate_emit_no_ir_mutation.sh` (the three greps above; baseline
      prints 34, target 0). Add to every BB GOAL's Session-Setup list. **Done:** gate exists, prints the
      live count, exits nonzero while >0.

- [ ] **IRM-1 — PRODUCER-BOX UNIVERSALITY (the enabler).** Every operation operand (binop L/R, unop arg,
      assign RHS) is lowered as its OWN producer box that writes a slot, in EVERY frontend's lower —
      uniformly, the way Icon already does via `operand_aux`. Change `lower_snobol4.c` (and any other lang
      that wires operands as direct `c[]` children) to wire binop/unop/assign operands as producer boxes.
      **Done:** for a global+global / global+lit / call-result-operand program in each language, the operands
      emit as standalone producer boxes (each writes a slot); no consumer reads a child's value inline.

- [ ] **IRM-2 — ONE SOURCE-AGNOSTIC CONSUMER PER OPERATION.** Confirm/extend `bb_binop_arith`,
      `bb_binop_relop`, `bb_binop_concat`, `bb_assign`, `bb_unop` to read operand SLOTS only (op as an
      immediate). The opcode axis is OPERATION (arith/relop/concat), never operand-source. **Done:** each
      reads `bb_slot_get` on its operands; none reads `pBB->α->ival`/`->t==IR_LIT_*`/a global name inline.

- [ ] **IRM-3 — DELETE F1 (operand-source fusion).** Remove the 14 swap sites in `emit_bb.c`
      (`flat_drive_binop_tree` + the L2267/2288/2599 arms). Delete the `IR_BINOP_GVAR_ARITH`,
      `_GVAR_ARITH_SLOT`, `_GVAR_RELOP`, `_GVAR_CONCAT`, `IR_UNOP_GVAR_SLOT`, and operand-source
      `IR_ASSIGN_*` opcodes + their dispatch cases + their `bb_*_gvar_*` template files. **Done:** those
      opcodes/templates gone; `grep -c GVAR_ARITH src/emitter` == 0; binop/assign/unop go through the
      general slot consumers in all languages; suites green or per-rung red.

- [ ] **IRM-4 — F2 → COMPILE-TIME CALL RESOLUTION (no runtime queries).** Move the 7 `IR_CALL` retags out
      of the emitter into a COMPILE-TIME resolution pass (in lower or a dedicated post-lower pass) that uses
      the program's own proc table (built from parsed procs) + a STATIC builtin/generator name table — NOT
      `rt_proc_is_*`/`rt_builtin_is_*`. Lower emits the FINAL call opcode (`IR_CALL_PROC_STAGED` /
      `IR_PROC_GEN` / `IR_CALL_BUILTIN` / `IR_CALL_GVAR_USERPROC` / indirect). Emitter dispatches, reads only.
      **Done:** zero `rt_*` calls in `emit_bb.c` used to pick an opcode; zero `IR_CALL` op writes in the emitter.

- [ ] **IRM-5 — F3 → MATCH STEPS IN LOWER (SNOBOL4).** `lower_snobol4.c` emits `IR_MATCH_HEAD`/`_RETRY`/
      `_ADVANCE` as distinct nodes; delete the 3 emit-time retags (L2523/2528/2551). **Done:** SNOBOL4 pattern
      programs build these nodes in lower; emitter has 0 match-op writes; SNOBOL4 oracle (beauty.sno) byte-identical.

- [ ] **IRM-6 — F4 → `IR_LIT` WRITE TRIAGE.** Classify the 10 `IR_LIT(...)` field writes: (a) writes to a
      REAL input node → move the value-setting to lower; (b) initialization of a FRESH scratch node the
      emitter created → replace with a marked fresh-node builder OR eliminate by having lower produce that
      node. **Done:** zero `IR_LIT(...).x =` on an input node in the emitter.

- [ ] **IRM-7 — GATE STRICT + LOCK.** `test_gate_emit_no_ir_mutation.sh` reads 0 and is flipped to a HARD
      `--strict` zero-check in every BB GOAL's Session-Setup. **Done:** gate 0; all language suites back to
      their pre-reset numbers (or better); FACT RULE body copied byte-identical into the four BB GOAL files.

- [ ] **IRM-8 — (STRETCH) ONE WALKER.** Collapse the three chain-body walkers
      (`codegen_flat_chain_body`, `codegen_gvar_flat_chain_body`, Prolog's `pl_gz_build_chain_from`/
      `pl_gz_chain_det`/`pl_gz_nsynth_chain`) toward ONE language-blind graph walker. This is the
      "we are WAY past LANGUAGE in the emitter" goal and is a full reorg; sequence after IRM-7.

---

## DO NOT
- Re-introduce ANY `->op =` write in `src/emitter/**`.
- Decide a call kind from `rt_*` runtime state at emit time — the proc/builtin tables are compile-time.
- Encode operand-source in an IR opcode — operand-source lives on the OPERAND node (a producer box).
- Add a per-language function to the emitter/templates — language lives in parser + lower ONLY.

## Watermark
**Reset Ground Zero #5 — 2026-06-27.** Gate-measured baseline: 45 hard IR-mutation sites in `emit_bb.c`
(34 op-writes + 11 field-writes), 0 elsewhere in `src/emitter/`; 19 informational runtime-query refs (IRM-4).
IRM-0 gate `scripts/test_gate_emit_no_ir_mutation.sh` LANDED (prints the live count, exits nonzero while >0).
Suites at reset: Icon 212/40, SNOBOL4 m4 7/7, Prolog 5/5, Raku 192, Pascal smoke 25.
All development ON HOLD until IRM-7 (gate strict 0). Breaking individual languages mid-ladder is AUTHORIZED.
