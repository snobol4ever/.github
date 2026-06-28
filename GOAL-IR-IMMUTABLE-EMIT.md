# GOAL-IR-IMMUTABLE-EMIT.md — The emitter READS IR. It NEVER mutates it. (Ground Zero #5)

## ⛔⛔ STANDING DIRECTIVE (Lon, 2026-06-28) — WHOLESALE JCON-IN-SCRIP, ICON-ONLY, HELLO-WORLD GATE
**This supersedes every "DO NOT REGRESS" below and in all handoffs.** We are doing a COMPLETE wholesale
rewrite of the Icon LOWER + EMITTER drivers + templates to mirror JCON (`refs/jcon-master/tran/`), because
JCON has it CORRECT. Same IR as JCON's `ir.icn` EXCEPT we keep our fine-grained `IR_BINOP`/`IR_UNOP` split
instead of one `ir_OpFunction`. Four JCON labels → TWO x86 instruction labels (α/β) + TWO `IR_ref_t` edge
pointers (γ/ω); CHUNKS-vs-DRIVERS/TEMPLATES is the only shape difference. Build NEW beside old, route Icon
to the new path, let the old rot.
- **DEFER P1 and P2** (the dual-walker collapse + N-builder unification in JCON-TO-SCRIP-IR-MAP.md). They do
  not help. Go straight to the JCON spine.
- **EVERYTHING BREAKS.** ALL non-Icon languages are CANCELLED until Icon lands (they are already broken: no
  IR_TMP, slots never tied to boxes). They will be REBUILT later with many new/different boxes.
- **NO full regression. NO artifact regen.** The big suites take too long. `beauty.sno` is NO LONGER a
  do-not-regress. Even Icon regressions do not matter for now.
- **THE ONLY PROGRAM THAT MUST WORK IS `write("hello world")`.** That is the entire gate this session.
  Drive the wholesale conversion until hello world compiles + runs through the new JCON-faithful spine
  (LOWER assigns ALL slots to `nd->lhs`; emitter reads slots, never mutates IR; call carries explicit
  operand tmps). Then Lon spins up the other-language sessions.

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
      **SUBSTRATE + PASS (DUMP SIDE) LANDED 2026-06-27 (additive, inert):** `IR_TMP` enum + `IR_t.lhs`
      result-slot field (init -1) + `kind_names[IR_TMP]`; `ir_node_produces_value()` + `ir_tmp_slot_assign()`
      (language-blind, writes ONLY `nd->lhs`, recurses leaf-SEQ sub-graphs) wired into `--dump-ir`; `bb_print`
      shows `lhs=`. VERIFIED: `x:=a+b;write(x)` → IR_BINOP `lhs=32` operands `[6 7]` = IR_VAR `a`(lhs=48)/
      `b`(lhs=64); IR_ASSIGN/IR_SUCCEED/IR_FAIL carry no lhs. Gate 42 / Icon 213 unchanged (pass runs in
      dump path only; emit still uses its own slotmap). **LOCKED** by `scripts/test_gate_ir_tmp_slots.sh`
      (structural: producers carry `lhs=`, side-effecting/control do not — pins the contract, not offsets).
      REMAINING (B1): wire `ir_tmp_slot_assign` into the EMIT path + flip the emitter to read `nd->lhs` instead of `bb_slot_alloc16`/`bb_slot_get` — that is
      behavior-changing, gate-and-suite-gated, and is the next rung (Cluster 1). Predicate currently covers
      the common value-producers (lits/var/binop/unop/call+kinds/proc_gen); extend as clusters land.

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
**B1 ATTEMPT — VALUE-TMP BAND LANDED, SUITE-RED MID-MIGRATION — 2026-06-28 (Sonnet 4.6, Lon: "let it break").**
Pushed `SCRIP@18bb0eda`. First emit-CONSUMING step of the ir_Tmp model: `ir_tmp_slot_assign_flat` (in
`scrip_ir.c`, run over all Icon graphs in `scrip.c` before emit) gives every value-producer EXCEPT `IR_VAR`
a lower-assigned slot `lhs=K*16` and sets a dedicated `IR_graph_t.nvalue_slots`; the 5 emit entries reserve
`[base, base+nvalue_slots*16)` and start scratch/varslots after it; `bb_slot_alloc16` returns `band_base+lhs`.

**REUSABLE SUB-PARTS (keep across any future strategy):** (1) slot↔materialised invariant — `bb_slot_get`
stays slotmap-only, `bb_slot_alloc16` returns the band offset AND pushes it to the slotmap, so every
`bb_slot_get(x)<0`-gated walk still fires (making `bb_slot_get` lhs-aware breaks them — confirmed). (2)
`IR_VAR` is an lvalue ref (JCON `ir_Var`), storage by-name via `bb_varslot`, NOT a value-tmp — excluded
(a per-node band slot for it breaks `a:=5;write(a)`). (3) dedicated `nvalue_slots`; never overload `nslots`
(Prolog/Pascal own it).

**THE WALL (why suite 212→186, −26):** the 3 emit entries carry 2 frame-base conventions (0 / 16) and
allocate value+var+scratch from ONE walk-order cursor; a reserved band overlaid on that perturbs frame
layout for ~26 varied tests (jcon structs, coerce, file_io, scan, mutual recursion). **PIVOT:** do NOT keep
overlaying a band — either land B8 single-walker FIRST (unify the frame bases) or move ALL slot allocation
(value+var+scratch) wholesale into LOWER so emit reads a complete slotmap. Separately, the `a[i]:=x+y` bomb
(binop-as-idx-value has no persistent result slot) is its own consumption bug: the binop computes correctly
to `op_off` in `write()`/`x:=…` contexts but idx_set yields a constant 6 when routed — NOT root-caused.
Gates unchanged: emit-mutation HARD=42, ir_Tmp keystone PASS. `.s` fixtures deliberately NOT regenerated
(would mask the regression); regen on suite recovery. **NEXT:** pick B8-frame-unification-first vs
lower-wholesale-slots, then re-attempt the value-slot consume.

---

## Watermark (prior)
**SESSION 2026-06-28 (Opus 4.8, Lon directing) — baseline restored green + 3 verified rungs.**
Lon's standing order this session: COMPLETE Icon LOWER+emitter rewrite, breakage of other languages
AUTHORIZED (they will be rebuilt later with new boxes), Icon-only checks (no full regression / no
artifact regen — too slow), drive Icon to 100% via wholesale JCON conversion. Inherited tree was
suite-RED (Icon 187) from the half-landed B1 value band (`18bb0eda`). Results (all committed local;
PUSH PENDING — 4 SCRIP commits + this watermark):
1. **Reverted B1 emit band → green** (`f23ff36f`). emit_bb.c back to pre-band parent; B0 keystone
   substrate KEPT (`IR_t.lhs`+`nvalue_slots`, `ir_tmp_slot_assign_flat`, driver wiring). Diagnosis
   confirmed: band overlaid a reserved value region on the walk-order cursor across 3 entries / 2
   frame bases (0/16) → broke 26 Icon tests. Partial slot-conversion has producer↔consumer seams →
   the path is ALL slots from LOWER, fresh parallel driver, NOT a band overlay on the fat driver.
2. **Capture box stops mutating IR** (`84b3d995`). Phase rides in new `op_phase` field, not
   `IR_LIT(pBB).ival`. Gate 42→40 (field-writes 11→9). .s byte-identical (capgood.sno + beauty.sno).
3. **Binop dispatch stops swapping ->op** (`ea09c10c`). Kind rides in new `op_binop_kind` field;
   new `walk_bb_node case IR_BINOP` dispatches to relop/concat/arith. Gate 40→38. .s byte-identical
   (add/sub/mul/relop/concat); mode-3 prints 3/7/20/9/foobar.
**Gate now HARD=38** (A op-writes=29 + B field-writes=9). Icon 213; SNOBOL4 mode-3 smoke 7/7.

**THE MECHANICAL PATTERN (reusable recipe — every ->op swap converts this way):**
The emitter specializes a generic op into a variant by mutating the node — `_sk = nd->op;
nd->op = VARIANT; EMIT_PAIR_FILL(...); nd->op = _sk;` — so `walk_bb_node`'s switch routes to the
variant template. Convert WITHOUT touching `nd->op` (keeps all `== GENERIC` checks working, zero
blast radius):
  (a) add a dedicated `sm_emit_t` field carrying the routing decision (op_phase/op_binop_kind/…);
      it survives EMIT_PAIR_FILL because `bb_fill_alpha`+`walk_bb_node` never touch new fields, and
      is consumed synchronously by the immediately-following FILL (safe under nesting, like op_off);
  (b) at the swap site, set the field instead of mutating ->op;
  (c) add a generic `case GENERIC:` in walk_bb_node (emit_core.c) that dispatches on the field to the
      variant template(s); KEEP the existing variant cases (other swap sites may still reach them);
  (d) VERIFY: `--compile --target=x86` .s diff BASE-vs-NEW must be 0 for a program exercising it.
This is faithful JCON (decision rides in emit-state / lowered shape; emitter reads, never writes IR).

**REMAINING ->op SWAP SITES (emit_bb.c, line nums approx; apply the pattern):**
- GVAR-arith cluster (Icon global-var arith) — ENTANGLED variant: 2215 (GVAR_CONCAT), 2236 + 3013/
  3022/3031/3040/3049 (GVAR_ARITH), 3068/3087 (GVAR_ARITH_SLOT), 3113 (GVAR_RELOP), 3126
  (binop_slot_kind), 3254 (UNOP_GVAR_SLOT). Base node is IR_ASSIGN (gvar store w/ binop rhs) swapped
  to a binop-gvar op → needs an `op_gvar_route` field + a redirect inside walk_bb_node's existing
  IR_ASSIGN handling (more invasive than the clean binop case; verify on `global g; g:=5;
  write(g+1)` style). ~11 op-writes — the biggest Icon cluster.
- Match retags (SNOBOL4 — deprioritized, Icon-first): 2471/2476/2499 (MATCH_HEAD/RETRY/ADVANCE),
  2547 (ASSIGN_DESCR). Clean single-target swaps.
- PERMANENT call retags (no restore): 3674-3689 set nd->op = IR_PROC_GEN/CALL_PROC_STAGED/
  CALL_BUILTIN/CALL_GVAR_USERPROC from rt_proc/builtin queries; 3259 (PROC_GEN→userproc), and the
  2243/2248 c0 IR_LIT_I save/restore. These are a pre-emit classification pass that mutates nodes —
  faithful fix is a LOWER/resolve pass writing kinds into lowered shape, OR an emit-state side-table.
**Remaining 9 F4 field-writes:** gz_query 715, capture-pair DONE, case 1732/50/62, limit 1797, gvar
2244/48, scan 2298-2303 — mostly input-node mangles needing per-site LOWER moves.

**NEXT:** apply the pattern to the GVAR cluster (op_gvar_route) for the biggest Icon gate drop, then
the call retags. The clean binop case (ea09c10c) is the worked template to copy.

---

**JCON-IN-SCRIP WHOLESALE CONVERSION — 2026-06-27 (Lon directing).** New campaign on top of the
A/B/C tracks: mirror JCON's `gen_bc.icn` (one `bc_gen_ir_<X>` per instruction) as one `bb_<x>` template
per instruction, x86 instead of JVM bytecode. The full correspondence — slot mechanic (JCON tmp = JVM
local ≡ SCRIP `lhs` = `[r12+off]`), four-label→α/β-internal + γ/ω-edge reconciliation, the one deliberate
`ir_OpFunction`→`bb_binop`/`bb_unop` arity split — is written in **`.github/JCON-TO-SCRIP-IR-MAP.md`**
(per-instruction table + build order). LOWER is ALSO being redone (the construct opcodes IR_EVERY/IR_TO_BY/
IR_WHILE are anti-JCON; JCON decomposes constructs into the primitive chunk stream at lower time). Build the
new path BESIDE the old fused path; flip Icon cluster by cluster; gate strict-0 + Icon suite are the recovery
target. **Foundation landed this session (additive, inert):** `IR_TMP` enum + `IR_t.lhs` field. Gate
HARD=42 (A=31 op-writes + B=11 field-writes), Icon 213/40/36 — both unchanged. **NEXT:** Cluster 1 — LOWER
tmp-slot pass + `bb_int_lit`/`bb_assign` first mirrors.

---

## Watermark (prior)
**Re-planned Ground Zero #5 — 2026-06-27 (Lon directing).** Ladder restructured into THREE tracks:
A (DELETE dead IRs, dynamic audit), B (COLLAPSE — IR_TMP keystone B0 front-runs, absorbs IRM-1..7),
C (ADD the 8 missing canonical IRs). KEYSTONE + DIVISION RULE added above. Gate baseline unchanged:
HARD=45 (34 op-writes + 11 field-writes) in `emit_bb.c`, 0 elsewhere; C=19 runtime-query refs.
Suites at reset: Icon 213/40 (XFAIL 36), SNOBOL4 m4 7/7, Prolog 5/5, Raku 192, Pascal smoke 25.
**NEXT (in progress):** B3 empirical probe — does the live ω-chain enumerate `(1 to 3)+(1 to 2)`? — run
FIRST (tells us if B3 is "confirm" or "rebuild"), alongside A0 dynamic dead-IR audit. Breaking individual
languages mid-ladder is AUTHORIZED. Gate strict-0 (B7) is the recovery target.
