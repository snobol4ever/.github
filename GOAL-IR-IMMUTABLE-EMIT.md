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



## ⛔ KEYSTONE (Lon, 2026-06-27) — IR_TMP MAKES THE EMITTER READ-ONLY

**The disease and the cure are the same fact.** Today slots are allocated at EMIT time (`bb_slot_alloc16`
inside `walk_bb_flat`) and producer→consumer is RECONSTRUCTED at emit time (the `op_a_slot`/`op_sb`/`op_sc`
forwarding dance). That reconstruction IS why the emitter mutates IR. JCON's `ir_Tmp` is the answer: every
value-producing node has an `lhs` tmp; operands reference tmps; a LOWER-time pass assigns tmp→`[r12+off]`.
Then the emitter reads `operand = tmp N → off(N)` — pure read. IR_TMP is language-blind; SNOBOL4, Prolog,
Pascal all inherit it. **B0 (IR_TMP) front-runs the IRM ladder — IRM-2/IRM-3 are tractable only once tmps
carry slots from lower. The original IRM-1..7 ladder stalled because it tried emitter-read-only WITHOUT the
tmp keystone.** The IRM rungs below are ABSORBED into Track B.

## ⛔ DIVISION RULE (Lon, 2026-06-27) — NO THREE LANGUAGE-VERSIONS OF BINOP/UNOP IN THE EMITTER

"Generator (Icon) vs coercive (SNOBOL4) vs plain" is NOT three operators. It is the OPERATION plus two
INDEPENDENT CS-generic axes, none a language branch:
  - **Operation** (ADD/LT/CONCAT…) → immediate on ONE `IR_BINOP` node (JCON: operation is DATA, not opcode identity).
  - **Resumability** (Icon "generator") → **ω-WIRING ONLY**. Operands are tmps written by producer boxes;
    BINOP reads the current tmp and on resume jmps wherever ω points. Lower wires `ω→right.resume→left.resume→fail`
    for the Cartesian case. The BINOP template is OBLIVIOUS to whether operands generate. **ZERO template cost.**
    This is why `flat_drive_binop_gen_tree` (the dead Cartesian driver) stays deleted — the ω-chain subsumes it.
  - **Coercion** (SNOBOL4/Icon vs Pascal) → **operand REPRESENTATION**. Boxed-descriptor → coercing sink
    `rt_num_arith` (Icon and SNOBOL4 SHARE it); unboxed → raw `add` (Pascal, via PAS-UNBOX). Template reads a
    repr flag. If Icon/SNOBOL4 coercion ever diverges in detail, the escape hatch is a COERCION-POLICY immediate
    on the node, switched inside the runtime sink — never a language `#ifdef` in the emitter.

---

## TRACK A — DELETE (shrink the 222 IR opcodes)

- [ ] **A0 — DEAD-IR AUDIT (DYNAMIC, NOT GREP).** Static grep is UNRELIABLE (proven 2026-06-27: `IR_MATCH_HEAD`
      is emit-retag-produced at L2523 yet a producer-grep flagged it dead; `emit_bb.c` greps as one binary blob;
      lowerers build via helpers/macros not literal `build(…IR_X…)`). Instrument every lowerer's node-constructor
      AND the emitter's dispatch to log op-kind on first produce/dispatch; run the WHOLE corpus (6 langs, both
      modes). Extend `src/tools/emit_per_kind_audit.c`. **Done:** reproducible `IR-LIVE-SET.txt` (produced∪dispatched)
      + complement `IR-DEAD-SET.txt`.

- [ ] **A1 — DELETE proven-dead opcodes** + enum slots + name-table entries + unreachable consumer arms + dead
      template files. Confirmed-suspect (NOT yet proven dead): `IR_GEN_BINOP`, `IR_BINOP_GEN`,
      `flat_drive_binop_gen_tree`, attic-only kinds. **Done:** `IR_OP_COUNT` drops by the dead count; build green;
      all suites green.

## TRACK B — COLLAPSE (absorbs IRM-1..7; IR_TMP first)

- [ ] **B0 — IR_TMP KEYSTONE.** Add `IR_TMP` (JCON `ir_Tmp` — a named value-slot node). Add a LOWER-time
      tmp-allocation pass (each value-producing node gets an `lhs` tmp; operands reference tmps) + a LOWER-time
      slot-assignment pass (tmp → `[r12+off]`). **Done:** `--dump-ir` shows tmps on nodes; a global+global add
      carries `lhs=tmpK`, operands=`tmpI,tmpJ`.

- [ ] **B1 — EMITTER READS TMP SLOTS (was IRM-2).** `bb_binop_arith/_relop/_concat/_assign/_unop` read
      `off(node.lhs)` and `off(operand_tmp)`; never call `bb_slot_alloc16` at emit, never read `->ival`/`->t`
      inline. **Done:** each reads slot offsets only.

- [ ] **B2 — FOLD operation+source variants into the bare op (was IRM-3).** `IR_BINOP` carries operation as
      immediate + a representation flag (boxed→`rt_num_arith` / unboxed→raw) + a coercion-policy immediate if
      needed. Delete `IR_BINOP_GVAR_ARITH/_ARITH_SLOT/_RELOP/_CONCAT`, `IR_UNOP_GVAR_SLOT`, `IR_BINOP_ARITH/_RELOP/_CONCAT`,
      operand-source `IR_ASSIGN_{LIT_I,LIT_S,VAR,CALL,CONCAT,DESCR}`, + their swap-sites + `bb_*_gvar_*` template files.
      **Done:** `grep -c GVAR_ARITH src/emitter`==0; one template per operation, repr-dispatched.

- [x] **B3 — RESUMABILITY IS ω-WIRING — CONFIRMED (2026-06-27).** Live four-port chain enumerates both
      `(1 to 3)+10` → `11 12 13` AND Cartesian `(1 to 3)+(1 to 2)` → `2 3 3 4 4 5` (exact Icon order, right
      operand inner) WITHOUT `flat_drive_binop_gen_tree` (that driver is reachable ONLY from the dead `IR_BINOP_GEN`
      arm, which has no producer). Capability proven NOT stranded → the GEN-binop machinery is deletion-authorized
      (folds into A1). DIVISION RULE validated empirically: resumability = ω-wiring, zero template cost.

- [ ] **B4 — F2 → COMPILE-TIME CALL RESOLUTION (was IRM-4).** Lower emits the FINAL call opcode from the program's
      own proc table + a STATIC builtin/generator table — NOT `rt_proc_is_*`/`rt_builtin_is_*`. **Done:** zero `rt_*`
      opcode-picking calls in `emit_bb.c`; zero `IR_CALL` op writes in the emitter.

- [ ] **B5 — F3 → MATCH STEPS IN LOWER (was IRM-5).** `lower_snobol4.c` builds `IR_MATCH_HEAD`/`_RETRY`/`_ADVANCE`;
      delete the 3 emit-time retags (L2523/2528/2551). **Done:** emitter has 0 match-op writes; beauty.sno byte-identical.

- [ ] **B6 — F4 → `IR_LIT` WRITE TRIAGE (was IRM-6).** Classify the 11 `IR_LIT(...)`/`IR_EXEC(...)` field writes:
      input-node mangle → move to lower; fresh scratch-node init → marked builder or have lower produce it. **Done:**
      zero `IR_LIT(...).x =` on an input node in the emitter.

- [ ] **B7 — GATE STRICT 0 + LOCK (was IRM-7).** `test_gate_emit_no_ir_mutation.sh` reads 0 under `--strict` in
      every BB GOAL's Session-Setup; FACT RULE body byte-identical across the four BB GOAL files; all suites at/above
      pre-reset numbers.

- [ ] **B8 — (STRETCH) ONE WALKER (was IRM-8).** Collapse `codegen_flat_chain_body`, `codegen_gvar_flat_chain_body`,
      and Prolog's `pl_gz_*` chain builders toward ONE language-blind graph walker. Sequence after B7.

## TRACK C — ADD (the 8 missing canonical IRs; JCON-mimicry)

- [ ] **C1 — IR_CREATE / IR_CORET / IR_COFAIL (co-expressions).** The one genuine feature gap (`create e`, `@C`,
      `^C`). STEPS: (a) `IR_CREATE` + coexp-block lowering in `lower_icon.c`; (b) runtime coexp object + stack;
      (c) `IR_CORET`/`IR_COFAIL`; (d) templates `bb_create/bb_coret/bb_cofail`; (e) test
      `c:=create(1 to 3); write(@c); write(@c)`.

- [ ] **C2 — IR_CSET_LIT.** First-class cset literal. STEPS: (a) verify a cset literal compiles today at all
      (empirical); (b) add node only if the gap is real; (c) `bb_cset_lit` template (sealed bitmap, RIP-relative).

- [ ] **C3 — IR_MAKE_LIST (judgment call).** `list(n,x)` works today as builtin `IR_CALL`; add a node only if
      `[a,b,c]` literal lists need uniform construction. STEPS: decide keep-as-builtin vs node; if node, `bb_make_list`.

- [ ] **C4 — IR_UNREACHABLE.** Dead-code/safety marker after non-returning tails. STEPS: lower emits after `IR_FAIL`
      tails; `bb_unreachable` template (emits `ud2`/bomb).

- [ ] **C5 — IR_LINK / IR_INVOCABLE (likely WONTFIX).** Program-linking directives; likely N/A for SCRIP's
      single-unit model. STEPS: confirm N/A and mark WONTFIX, or stub if `invocable` keyword support is wanted.

---

## DO NOT
- Re-introduce ANY `->op =` write in `src/emitter/**`.
- Decide a call kind from `rt_*` runtime state at emit time — the proc/builtin tables are compile-time.
- Encode operand-source in an IR opcode — operand-source lives on the OPERAND node (a producer box).
- Add a per-language function to the emitter/templates — language lives in parser + lower ONLY.

## Watermark
**Re-planned Ground Zero #5 — 2026-06-27 (Lon directing).** Ladder restructured into THREE tracks:
A (DELETE dead IRs, dynamic audit), B (COLLAPSE — IR_TMP keystone B0 front-runs, absorbs IRM-1..7),
C (ADD the 8 missing canonical IRs). KEYSTONE + DIVISION RULE added above. Gate baseline unchanged:
HARD=45 (34 op-writes + 11 field-writes) in `emit_bb.c`, 0 elsewhere; C=19 runtime-query refs.
Suites at reset: Icon 213/40 (XFAIL 36), SNOBOL4 m4 7/7, Prolog 5/5, Raku 192, Pascal smoke 25.
**NEXT (in progress):** B3 empirical probe — does the live ω-chain enumerate `(1 to 3)+(1 to 2)`? — run
FIRST (tells us if B3 is "confirm" or "rebuild"), alongside A0 dynamic dead-IR audit. Breaking individual
languages mid-ladder is AUTHORIZED. Gate strict-0 (B7) is the recovery target.
