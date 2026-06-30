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
- **⛔⛔ THE `.s` BYTE-IDENTICAL RULE IS DELETED — PERMANENTLY, NOT "FOR NOW" (Lon, repeated 4×; honored 2026-06-28).**
  There is NO requirement, anywhere, that any `.s` stay byte-identical — not `beauty.sno`, not `capgood.sno`,
  not any benchmark/feature/demo artifact, not across modes, not vs any prior commit. The `.s` is the HONEST
  CURRENT compiler output and **it WILL change drastically** as GROUND ZERO #5 rewrites LOWER + the EMITTER
  DRIVER from scratch. Byte-identity of `.s` is NOT a gate, NOT a completion test, NOT a regression signal,
  and must NEVER be wired into one. Any rung or handoff that cites `.s` byte-identity as a requirement is
  defective — strike it. (`.s` regen scripts still exist to TRACK current output; they are not pass/fail.)
- **NO full regression. NO artifact regen.** The big suites take too long. **Icon regression does not matter
  AT ALL — let it go to ZERO and GROW back up.** We have `write("hello world")` and `1 + 1`; we GROW from there.
- **THE ONLY PROGRAMS THAT MUST WORK ARE `write("hello world")` AND `write(1 + 1)`.** That is the entire gate.
  Drive the wholesale conversion until both compile + run through the NEW spine: each language keeps its OWN LOWER
  (there are SIX lowers — SNOBOL4, Snocone, Rebus, Icon, Prolog, Pascal — NOT one), and they all use the SAME
  TECHNIQUE: a LOWER-time pass assigns ALL slots to the producing node's `tmp` field (three-address-code temporary
  allocation). There is ONE language-INDEPENDENT EMITTER DRIVER handling generic CS constructs: it reads `nd->tmp`
  + operands, sets `g_emit`, invokes the proper BB, and NEVER mutates IR. The ONLY guarantee required: the proper BB
  is invoked and every variable lives in the ONE place (`g_emit`) set correctly. Icon regression may go to ZERO and
  grow back. Then Lon spins up the other languages onto the same ONE driver.
- **IR_t.`tmp` (NOT `lhs`) IS THE TEMPORARY SLOT; there is NO `IR_TMP` opcode.** JCON's `ir.icn` records name the
  result-temp field `lhs` and point it at an `ir_Tmp` NODE. SCRIP realizes the temp as a plain `int` FIELD on the
  producing node (cleaner: one node per value, slot lives on it) — so the `IR_TMP` opcode was DEAD (zero nodes ever
  constructed) and is REMOVED (`19cbedd5`); the field, mis-named `lhs` (there is no `=` for `write(1+1)`), is RENAMED
  `tmp`. NOT every IR fills it — only value-producers (`ir_node_produces_value`: lits/var/binop/unop/call/proc_gen).
  Control/effect ops (GOTO/IF/SUCCEED/FAIL/ASSIGN-effect) produce no value and carry no `tmp`. The `own`/`idx` fields
  STAY — load-bearing (`IR_LIT(nd)`≡`nd->own->lit[nd->idx]`, `IR_EXEC(nd)`≡`nd->own->exec[nd->idx]`, sidecar pattern).

### LOCKED TECHNIQUE (2026-06-28, proven on `write("hello world")`, SCRIP `486eb1a3`)
The from-scratch path is **not** a template rewrite — TEMPLATES STAY (gate-clean `bc_gen_ir_*` analogs;
fixes/consolidation only). **LOWER + the EMITTER DRIVER are the from-scratch surfaces.** The driver's job
per node, proven composable on hello world:
  1. **LOWER wires `operands[]` explicitly** (JCON `ir_Call` shape) — `lower_call` now pushes every chained
     arg as an operand tmp (`9dd48524`), not just idx/list. `--dump-ir` shows `IR_CALL [3]`.
  2. **Emitter reads `nd->lhs` for the result slot** — `IR_LIT_S` sources `op_off` from the LOWER-assigned
     `nd->lhs` (=16), no emit-time `bb_slot_alloc16` (`b4f75d98`). Literal lands at `[r12+16]`; the `write`
     consumer reads the same slot. The base-shift catastrophe (prior −40) was suite-coexistence only.
  3. **Reconstruction demoted to a gap-filler** — `descr_chain_operand_refs` now TRUSTS LOWER operands
     (skips the `n_operands=0` clobber when `n_operands>=ar`) (`486eb1a3`). The new driver does steps 1–2
     universally and DELETES the gap-filler entirely.
Verified green: mode-3 (`SCRIP_ICN_BB=1 --run`) + mode-4 (`--compile --target=x86` → as+gcc+link → run).
Setup: `apt-get install -y libgc-dev`; `make scrip && make libscrip_rt`; link recipe in
`scripts/cmp3_snobol4.sh` (`gcc -no-pie -x assembler X.s -Lout -lscrip_rt -lgc -lm -Wl,-rpath,out`).
NEXT: stand up the from-scratch driver `emit_jcon` over the JCON instruction set for the hello-world spine
{StrLit, Var/Deref, Call, Succeed, Fail, EnterInit} reading `operands[]`+`lhs`; route Icon to it; delete the
`flat_drive_*` / reconstruction / `bb_slot_alloc16` legacy for that path. Extend `ir_jcon_slot_assign` from
literals-only to ALL producers.

## ⛔ ENTRY POINT — WHICH DRIVER IS LIVE (READ FIRST; fn renamed 2026-06-29 Sonnet 4.6)
**The ONE and ONLY per-node emit driver — for ALL languages — is `emit_drive` in `src/emitter/emit_drive.c`.**
(Function renamed 2026-06-29 from `emit_drive_node`. File stays `emit_drive.c`: the driver is LANGUAGE- AND
BACKEND-NEUTRAL — it reads `nd->op` + `nd`'s fields, sets `g_emit`, and dispatches to whatever Byrd-Box
templates are wired; nothing in the DRIVER itself is Icon-specific or x86-specific. The x86 lives in the
templates it dispatches to, not in the driver — so it is NOT named `emit_x86.c`.) It is called once per chain
node by `codegen_flat_chain_body` (`emit_bb.c`, the per-node loop ~line 1552:
`emit_drive(nodes[i], node_γ, node_ω, betas[i])`), AFTER that loop computes each node's γ/ω/β labels (the
four-port→two-edge reconciliation). A `grep` for the call site is FOOLED by the Greek chars in `emit_bb.c`
(grep prints "binary file matches" and hides the line) — use `grep -a` or you will wrongly conclude
`emit_drive` is dead and waste a session re-deriving the routing (this happened 2026-06-29).
- **The old fat driver was DELETED WHOLESALE (`f8e88daf`); the dead `emit_jcon_node` predecessor is GONE.**
  `emit_drive` is the sole driver; there is no parallel path and no `SCRIP_ICN_JCON` toggle anymore.
- **`emit_drive`'s `default:` is `drive_unowned` → HARD ABORT (`FATAL emit_drive: op=N has no template`), NOT a fallback and NOT a soft decline.**
  Every IR op the switch does not own ABORTS LOUDLY at the point of confrontation — there is no [SMX] print, no
  "ABORT", no ignorable message. An unimplemented op is a bug to FIX (implement the op), never a feature to defer.
  So any IR op the switch does not own FATALs (`bb_build_flat returned NULL`). To grow the driver you ADD a
  `case IR_X` to `emit_drive`; the universe of owned ops IS the switch. `walk_bb_flat` (`emit_bb.c`) is
  the OLD fat driver residue — still used for nested sub-walks (alt arms, every-body, swap, rasgn) but being retired.
- **`DRIVE_FILL(nd,…)` dispatches through `walk_bb_node` (`emit_core.c`) on `nd->op`** to the `bb_*()`
  template. So a new op that emits via a template needs BOTH: a `case IR_X` in `emit_drive` (sets
  `g_emit`/pair-table) AND a matching `case IR_X: bb_emit_x86(bb_x()); return 0;` in `walk_bb_node`.
  (E.g. IR_CONJ needed adding to `walk_bb_node` — it had `IR_GCONJ` (Prolog) but not `IR_CONJ` (Icon).)
- **IR_IF needs NO driver case** — `lower_if` produces pure edge-threading (condition/then/else wired by
  γ/ω); the IR_IF node never reaches the driver (faithful to JCON `ir_a_If`, which emits only `ir_Goto`).
- **OWNED by `emit_drive` as of 2026-06-29:** IR_LIT_{S,I,F,NUL}, IR_KEYWORD, IR_VAR, IR_BINOP,
  IR_UNOP/NEG/POS/NONNULL/NULL_TEST/SIZE/NOT, IR_ASSIGN (local), IR_CALL{,_BUILTIN,_PROC_STAGED,_USERPROC,
  _BYNAME,_GVAR_USERPROC}, IR_CONJ, IR_SUCCEED, IR_FAIL, IR_RETURN. **NOT YET IMPLEMENTED — these ABORT (fix them, do not defer):** IR_EVERY(18)+
  IR_TO(103)/IR_TO_BY(17) [one atomic generator unit — resume port = β], IR_ALT(22), IR_SUSPEND(28),
  IR_LIMIT, IR_SCAN/GEN_SCAN, GVAR-arith assign family, IR_IDX/IDX_SET, IR_FIELD_*, IR_CASE, …

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

## ⛔ TRACK D — COLLAPSE IR_t (the STRUCT, not the opcodes) — JCON FIELD DISCIPLINE (Lon, 2026-06-28)

**Goal: `IR_t`'s value payload becomes a 3-way C union `{ const char* sval; int64_t ival; double dval; }`
and `counter` is DELETED.** JCON's discipline (`ir.icn`): each record field holds ONE kind of thing —
`IntLit.val` is always an int, `StrLit.val` always a string, `Call.argList` always a LIST of children;
subtypes are DISTINCT RECORDS (= distinct `op` values). SCRIP collapsed JCON's ~30 records into one
`IR_t` selected by `op`, and in doing so introduced two overloads JCON never has:
  - **`dval`-as-discriminant-tag** — `dval ∈ {1.0,2.0,3.0,5.0}` selects a subtype on SEQ/CALL/SCAN/SUSPEND/
    BINOP, riding co-resident with real payload. JCON-clean = move the tag to the `op` enum (or a tiny
    `subtag`), leaving `dval` = real literal ONLY.
  - **`ival`/`counter`-as-smuggled-`IR_graph_t*`** — child sub-graphs cast through an int64 via `(intptr_t)`.
    JCON-clean = children live in `operands[]` (its `argList`/`valueList`), reached as nodes, never smuggled.

These two overloads are the ONLY reason `{sval,ival,dval}` can't union today: CALL holds `sval`(name)+`ival`
(argc)+`dval`(tag) at once; SEQ holds `dval`(tag)+`ival`(child). Remove the overloads → each node uses
exactly ONE of the three → union is valid (−16 bytes/node) and `counter` deletes.

**THE SEQUENCING (Lon, 2026-06-28): FIX ICON PROPER → WHACK THE FIELDS → BREAK ALL OTHER LANGUAGES.**
Icon is fixed to the discipline FIRST so it SURVIVES the whack; the whack (delete `counter`, union the
values) then STRUCTURALLY breaks every other lower (they still smuggle / tag) — which is the FORCING
FUNCTION: the rebuilt SNOBOL4/Snocone/Rebus/Prolog/Pascal lowers have NO field left to abuse, so they MUST
adopt operands[]-children + op-subtypes. There is no avenue to violate.

### KEY FINDING (2026-06-28, Sonnet 4.6) — ICON CORE IS ALREADY CLEAN
`--dump-ir` on `a:=10;b:=20;write(a+b)` and on `if/while` programs shows the disciplined FLAT model already:
statements chain via `γ` edges, operands sit in `[operands]` (`IR_BINOP [4 5]`, `IR_ASSIGN [9]`, `IR_CALL [3]`),
payloads are clean (`ival`=int literal, `sval`=name, binop kind in `ival`). **ZERO `IR_SEQ` sub-graphs, ZERO
pointer-smuggling, ZERO dval-tags on the ordinary Icon path.** The smuggling/tagging is confined to a few
LEGACY GENERATOR constructs + the other languages.

**Icon's COMPLETE holdout list (only 9 lower sites, `lower_icon.c`):** all are the **`dval=1.0`
"generator/resumable" flag** on four node types — CALL (L106), BINOP (L142/146), SUSPEND (L210), GEN_SCAN
(L270) — plus GEN_SCAN's sub-graph smuggling (L273 write, 131/132 read; the `s ? expr` scan operator).
**NOTE:** the `dval=1.0` generator flag is itself a violation of this file's own DIVISION RULE
("resumability = ω-WIRING ONLY, zero stored flag"). Fixing Icon proper = (a) replace the `dval=1.0` flag
with ω-wiring (or a `subtag` bit if a stored marker is truly needed — but try ω first), (b) move GEN_SCAN's
two sub-graphs onto operands[]/flat edges. Verify the generator flag is even READ-to-effect first (it may be
vestigial like `state`/`stno` were — confirm before assuming a behavior change).

### LANDED (2026-06-28, Sonnet 4.6 cont'd) — GROUND ZERO #5 RUNG #2: IR_RETURN owned + zero-arg user procs END-TO-END
- **IR_RETURN owned by the universal driver** (`0c6bbf94`). `emit_drive_node` gained `case IR_RETURN:
  DRIVE_FILL(...)` → routes to the already-correct `walk_bb_node` descr-chain handler (reads `operands[0]`
  value slot + `op_dval`, emits `bb_return`). `DRIVE_FILL` ≡ old `FILL` byte-for-byte. JCON model: `return E`
  = eval E then `Succeed(t, /*no resume*/)` (irgen.icn:867; there is no `bc_gen_ir_Return`).
- **D1-CALL step 1** (`4a308ca2`): Icon non-idx/list calls now take the flat-operand chaining path, not the
  dead subgraph path. `lc_call_argblks`'s only live effect was `IR_LIT(call).dval=tag`, which (union with
  `sval`) clobbered the call name → `resolve_call_kinds_descr` deref'd the double bits `0x4008…`=3.0 as a
  pointer → SEGV. Flat operands = JCON model; names survive.
- **D1-CALL step 2** (`ec3bd5b3`): `bb_call_route_classify` routes a registered user proc → PROC_STAGED
  WITHOUT the `dval` gate (the flat call no longer carries `dval=3.0`). One relaxed condition; same
  `rt_proc_is_registered` query; generator-proc/builtin cases unaffected.
- **RESULT: zero-arg user-defined procedures work END-TO-END, both modes.** `write(f())` with `f` returning
  a literal/string/expression (`return 3+4*2` → `11`) — mode-3 `--run` AND mode-4 text. **Proves the
  IR_RETURN conversion end-to-end** (RETURN was un-exerciseable until a proc became callable).
- **NEXT RUNG: calls WITH args (op=200 arg-handling) + B4 de-`dval` of the call stack.** Fully diagnosed in
  HANDOFF-2026-06-28-SONNET46-JCON-RETURN-AND-CALL-FLAT.md. Heartbeat green throughout; no green program
  regressed (builtin/arg calls were already broken by the same union collision).

### LANDED (2026-06-28, Sonnet 4.6 cont'd) — GROUND ZERO #5 RUNG #1: universal driver + counter DELETED + regression reinstated
- **⛔ NEW UNIVERSAL EMITTER DRIVER `emit_drive.c`/.h.** `emit_drive_node` is now THE per-node dispatch for
  ALL languages (replaces the `emit_jcon_node`/`walk_bb_flat` branch in `codegen_flat_chain_body`). It reads the
  LOWER-assigned value slot (`nd->tmp`) and operand slots, sets `g_emit`, and invokes the proper Byrd Box via
  `walk_bb_node` — and NEVER mutates IR. No fallback to the old walker: an unowned op prints the `[SMX]` banner +
  sets `bb_emit_overflow` → the proc build declines cleanly. De-static'd 7 helpers (bb_child0/1, binop_slot_kind,
  bb_call_write_route, descr_binop_opnd_slot, binop_is_num_real, bb_fill_alpha) + added bb_flat_cursor_reserve so
  LOWER tmp slots size the r12 frame. `emit_drive.c` is in the emit-no-mutation gate scan and contributes **0**.
- **⛔ `counter` DELETED from IR_t (+ vestigial IR_exec_t typedef gone).** No `IR_t` field points to an
  `IR_graph_t` anymore — not `counter`, and the `ival`→`IR_graph_t*` smuggle (GEN_SCAN `bsg`, raku arg-block `bg`)
  is gone too, so the `{sval,ival,dval}` union holds ONLY scalars. ~80 smuggle sites converted: dead readers stubbed
  (their rebuild-me constructs abort on the new driver), writer RHS preserved via `(void)(...)`. IR_t is
  now `{op, γ, ω, operands[], n_operands, tmp, value-union}`; children reached ONLY through operands[]. Remaining
  union state-pointer smuggles (bb_conj_state_t* etc. for Prolog/SNOBOL4 runtime) are NOT IR_graph_t → later rung.
- **FIELD-DISCIPLINE GATE 190 → 119** (P2 read-smuggle **50 → 0** — nothing is read as an `IR_graph_t*`; P1
  write-smuggle 57 → 36). TARGET ratcheted 192 → 119 to lock it.
- **FULL ICON REGRESSION REINSTATED** (`test_icon_rung_suite.sh`, mode-3 `--run`): **PASS=43  DECLINED=96 (stale; mechanism REMOVED)
  FAIL=114  XFAIL=36** (vs old fused walk_bb_flat path PASS=195 — the deliberate Ground Zero reset onto the clean
  driver; 43 ≫ the sanctioned "TWO"). the now-REMOVED soft-decline of unowned ops (they ABORT now); FAIL = owned op the immature driver
  mis-wires (e.g. user-proc-call segfault, rung02_proc_fact rc=139) = the growth/cleanup target. **NEXT: grow
  emit_drive_node op ownership (implement-the-op→PASS) and drive FAIL→0; then delete the dead emit_bb.c walk_bb_flat /
  flat_drive_* zoo (emit-mutation gate 38→down).** emit-mutation gate unchanged at HARD=38 (all in the now-dead,
  bypassed emit_bb.c paths). **PUSH PENDING — credential needed; handoff INCOMPLETE until pushed.**


- **⛔ THE UNION LANDED + PASS=2 (Lon command decision).** `IR_t`'s value payload is now ONE anonymous union
  `union { const char * sval; int64_t ival; double dval; }`. **`write("hello world")` → `hello world` and
  `write(1 + 2)` → `3` both green mode-3 AND full mode-4 cycle.** Enabled by making the CALL node hold ONLY
  `sval`(name): arity now reads `n_operands` (preamble `op_ival` branch on `ir_norm_call_kind==IR_CALL`;
  `descr_chain_arity` IR_CALL case → `n->n_operands`), and the `ival=nargs` (L93) + inline `dval=1.0` (L106)
  co-use writes were dropped. The struct collapse is DONE; per Lon the language LOWER sessions rewire their own
  from GROUND ZERO #5, so PASS=2 is the entire gate for this work. **Bonus survivors (single-member constructs,
  not required):** variables, arithmetic, if/while, relops, and `every`/`to` generators all still run. Constructs
  that genuinely co-use the value fields (scan `s?e`, nested-scope VAR hop-count, suspend, complex-call subgraphs)
  are now corrupted-by-design — they rebuild on the flat operands+edge model.
- **`counter` DELETED (2026-06-28 RUNG #1).** Field gone + vestigial `IR_exec_t` typedef gone; ~80 smuggle
  sites converted (dead readers stubbed — their rebuild-me constructs abort on the new driver; writer
  RHS preserved via `(void)(...)`). The `ival`→`IR_graph_t*` smuggle was killed too, so NO `IR_t` field points to
  an `IR_graph_t`. See the top LANDED watermark.
- **`state` DELETED.** Dead: never written (calloc'd 0), emitter reads vacuous; folded 5 reads. Exposed
  `flat_drive_while` as already-dead (its gate `while_cond_emittable` can never return true) — sweep candidate, left.
- **`stno` → `ival`, then DELETED.** SUCCEED-only (SNOBOL4 stmt numbers); 5 sites moved; smoke green; dump `stno=N ival=N`.
- **ENFORCEMENT GATE built:** `scripts/test_gate_ir_field_discipline.sh` — P1 write-smuggle + P2 read-smuggle +
  P3 dval-tag over all live src; ratchet `IR_FIELD_DISCIPLINE_TARGET` (now 192; live debt 190) fails on growth.
  Wire into every BB GOAL Session-Setup. **The remaining 190 are smuggling in NOW-BROKEN rebuild-me code** — the
  GZ#5 language rebuilds eliminate them (children→operands[], subtypes→op). Ratchet toward 0 as each language lands.
- **D1-BINOP DONE.** `lower_icon.c` BINOP cached the relop predicate in `dval=1.0` (redundant = `ival in 5..10`,
  never read at emit). Removed the cache; L146 reads the predicate inline. Relops verified green.

### REFINED FINDING — `dval` HAS THREE MEANINGS (not just "the generator flag")
Quantified 2026-06-28: discriminant **TAG** `{1.0,2.0,3.0,5.0}` = **68 reads** (SEQ-pair/CALL/SUSPEND/GEN_SCAN/
RETURN); **`(int)dval` HOP-COUNT** for nested-scope VAR access = **6 reads** (`bb_call.cpp` — co-resident with
`sval` name on VAR nodes, a SECOND union blocker independent of the tag); real-literal `dval` (LIT_F) = legit.
ALL non-real-literal `dval` uses must move off for the union. **Per-construct method (proven on BINOP): grep the
EMIT readers for that op FIRST — if `dval` is never read at emit for it, the flag is lower-scratch and converts
cheaply (inline the predicate / drop the cache); if read at emit, move to ω-wiring or a `subtag` bit.**

### TRACK D RUNGS (remaining — Icon settle FIRST, then whack)
- [x] **D1-BINOP** — relop-predicate cache off `dval`. DONE (gate 192).
- [ ] **D1-CALL** — `lower_icon.c:106` sets `dval=1.0` on the SIMPLE (non-subgraph) call. Verify emit-readership
      (staged template `bb_call_proc_staged.cpp:33` reads `dval==1.0` but on the SUBGRAPH path — confirm the simple
      call's flag is/ isn't read at emit, as done for BINOP). Convert per method above.
- [ ] **D1-SUSPEND** — `lower_icon.c:210` `dval=1.0` on SUSPEND. Verify emit-readership; convert.
- [ ] **D1-VAR-HOPS** — the 6 `(int)dval` hop-count reads in `bb_call.cpp` (VAR nested-scope). Move hop count off
      `dval` (it co-resides with `sval` name). Candidate home: a `subtag`/small int, or `ival` if VAR doesn't use it.
- [ ] **D2 — GEN_SCAN → operands[]/flat.** Scan operator (`s ? expr`): `dval=1.0` + counter/ival sub-graph smuggling
      (lower L270/273, read L131/132, emit L2068/2069). Convert off `counter`/`ival`. After D1-* + D2, `lower_icon.c` debt = 0.
- [x] **D3 — WHACK: delete `counter`** (DONE 2026-06-28 RUNG #1). Union `{sval,ival,dval}` already landed
      earlier; `counter` field + `IR_exec_t` typedef removed; the `ival`→`IR_graph_t*` smuggle killed too. ~80
      reader/writer sites converted (dead readers stubbed; constructs abort on the new driver). NO `IR_t`
      field points to an `IR_graph_t`. Field-discipline gate 190→119 (P2 read-smuggle 50→0).
- [ ] **D4 — Gate to 0.** Ratchet `IR_FIELD_DISCIPLINE_TARGET` toward 0 (now **119** after D3; remaining = P1
      non-graph runtime-state smuggles in lower_snobol4/raku + P3 dval-tags); lock in every BB GOAL Session-Setup.

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
      delete the 3 emit-time retags (L2523/2528/2551). **Done:** emitter has 0 match-op writes.

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

## ⛔ TT_* COVERAGE PUNCH LIST (Icon ladder — Lon 2026-06-29, crawl UP this instead of the ir_* ladder)
The practical ladder is the AST construct (TT_*), not the JCON ir_* record. Coverage measured by `SCRIP_ICN_BB=1
--run` this session (the TT_* enum in ast.h is shared across all 6 langs; only Icon-reachable rows listed). Climb the
GAPs top-down; the resume-gap cluster is ONE fix.

**✅ COVERED (run correct, mode-3 verified):**
- `TT_ILIT`/`TT_FLIT`/`TT_QLIT`/`TT_CSET` — literals → IR_LIT_{INTEGER,REAL,STRING,CHARSET}
- `TT_VAR` (local + global rval) → IR_VAR ; `TT_KEYWORD` → IR_KEYWORD (incl &line/&file→literal, THIS SESSION)
- `TT_ADD/SUB/MUL/DIV/MOD/POW` + `TT_CAT`/`TT_LCONCAT` + relops (`TT_LT/LE/GT/GE/EQ/NE` + string LLT…LNE) → IR_BINOP/_RELOP
- `TT_MNS`/`TT_PLS`/`TT_SIZE`/`TT_NONNULL`/`TT_NULL`(unary) → IR_UNOP ; `TT_ASSIGN` (LOCAL only)
- `TT_WHILE`/`TT_UNTIL` (non-generator cond) ; `TT_FNC` (builtin + zero-arg user proc) ; `TT_PROC_DECL` ; `TT_RETURN`
- `TT_IF`/(bare if), statement/unbounded form (`if C then X [else Y]`, value discarded) — JCON `ir_a_If` edge-threading, no opcode/template/driver-case (SCRIP `59dafbc0`, 2026-06-30 Sonnet 4.6). `proc_recursion` (`if n<=1 then return 1 else …`) green via this. **Value-context `if` (`write(if c then a else b)`) NOT yet correct** — then/else write distinct result slots, consumer reads only then's; needs a shared result slot or IR_MOVE join (JCON unifies via one `target` tmp). Deferred.

**🔴 GAP — RESUME-GAP CLUSTER (all one root cause; FIX FIRST, unblocks 4 constructs at once):**
Root cause (localized via --dump-ir this session): a generator's consumer routes its resume edge to the wrong node
(e.g. body tail → IR_ASSIGN wrapper instead of the inner IR_TO generator's resume port → loop/empty). FIX:
assignment-lowering must forward the generator's resume as `cx->beta`, OR add a bounded-body primitive (JCON
"always bounded"). Then:
- `TT_EVERY` — `ir_a_Every` threading written+reverted; canonical `every i:=1 to N do write(i)`=1|2|3 OK, non-trivial bodies hang.
- ~~`TT_IF`~~ DONE 2026-06-30 (statement form; see COVERED). Value-context unification still open.
- `TT_UNTIL` — DONE 2026-06-30 (`until i<=0 do …` → 5 4 3 2 1, both modes). Was never an `until`-lowering bug: it was gated on the `IR_BINOP_RELOP` ω-reachability gap (relop failure-branch never discovered by the flat-chain BFS), fixed in `59dafbc0`. `TT_REPEAT`+`TT_BREAK`/`TT_LOOP_NEXT` — partial: `repeat{…}` runs the body ONCE then exits. ROOT CAUSE (diagnosed 2026-06-30, NOT yet fixed): `lower_repeat` uses an `IR_FAIL` node `R` as the loop-back target (`R.γ→body`, `R.ω→ω`); because `R` is IR_FAIL it always takes ω, so body.success→R→ω exits instead of re-entering the body. JCON `ir_a_Repeat` loops body.success/failure→ir.start→body.start with NO fail node. Fix needs the loop-back to route to the body entry without an IR_FAIL placeholder (same placeholder-strands-BFS class as the if absent-else fix) — `while`/`until` happen to work because their IR_FAIL exit semantics align; `repeat` (no failure exit) does not. This is loop-back redesign, not a patch.
- `TT_TO`/`TT_TO_BY` as bare/driven generator — yields only first value outside a wired consumer; `by` variant IR_FAIL-stubbed.

**🔴 GAP — UNOWNED/CRASH (distinct fixes):**
- `TT_ALTERNATE` (`a | b`) → builds IR_ALT(op=0) which is UNOWNED in emit_drive → **ABORT**. Per JCON `ir_a_Alt`:
  pure Goto threading (alt.start→e1.start; ei.success→alt.success; ei.failure→e(i+1).start; needs IR_INDIRECT_GOTO
  for bounded resume). lower_alt already builds the operand wiring; needs emit_drive case + bb_alt (mirror bb_conj).
- `TT_IDX`/`TT_MAKELIST`/`TT_VLIST` (`L:=[…]; L[i]`) → **SEGV**. Per JCON `ir_MakeList` + `ir_a_Sectionop`/subscript.
- `TT_FIELD` → IR_FAIL stub ; `TT_SECTION`/`TT_SECTION_PLUS/MINUS` (`s[i:j]`) → IR_TERNOP, lower stubbed.
- `TT_SCAN` (`s ? expr`) ; `TT_CASE` ; `TT_SUSPEND` ; `TT_CREATE` (co-expr) ; `TT_LIMIT` — not Icon-wired.
- Global `TT_ASSIGN` (`global g; g:=5`) → emit_drive IR_ASSIGN aborts on global (chain-flag split, P2 prereq).

**NEXT (in order):** (1) resume-gap cluster fix → re-land every + convert if/until/repeat ; (2) TT_ALTERNATE
(bb_alt, clean, mirrors bb_conj) ; (3) TT_IDX/MAKELIST segv ; (4) global TT_ASSIGN (needs chain-flag P2 unify).


SCRIP `65651f7a`→`c8ab2ad7` (2 commits, PUSHED to origin/main). Methodology established per Lon: "IR" = JCON IR
record (`ir.icn`), each mapped to its SCRIP `IR_e` counterpart, converted wholesale from `irgen.icn` (4-port→γ/ω
edge wiring) + `gen_bc.icn` (emission) into `lower_icon.c` + `emit_drive` + `bb_*.cpp`. Gate programs green mode-3+4
throughout; mutation gate HARD=4 unchanged (both changes lower-only / dump-only). No artifact regen (per standing
directive: Icon-only behavior change, big suites too slow, .s not a gate).
1. **`65651f7a` — ir_Key→IR_KEYWORD (JCON `ir_a_Key`, irgen.icn:1262).** New `lc_key()` in lower_icon.c: `&line`→
   IR_LIT_INTEGER, `&file`→IR_LIT_STRING (JCON's "line"/"file" emit ir_IntLit/ir_StrLit, NOT a runtime ir_Key fetch);
   all other keywords→IR_KEYWORD runtime path (unchanged). FIXES live bug: &line/&file previously hit rt_keyword_read
   →empty output+segfault. CAVEAT: tree_t has NO source coordinate (no JCON p.coord), so VALUES are placeholders
   (&line=0, &file=""); STRUCTURE is faithful. Generator-keyword resume (&features via ir_ResumeValue) = only
   un-converted ir_a_Key slice, deferred (rare).
2. **`c8ab2ad7` — --dump-ir segfault fixed.** bb_print tail loop cast operand IR_t*→IR_graph_t* and recursed (read
   n/all/entry from a node's bytes) → SEGV on EVERY program (rc=139 even on write("x")). Dead pre-flat residue;
   removed + NULL guard. --dump-ir now rc=0; now a working verify tool.
3. **ir_Every (JCON `ir_a_Every`, irgen.icn:309) — ATTEMPTED, REVERTED, NOT LANDED.** Exact JCON threading (NO
   IR_EVERY opcode — pure Goto: E.success→B.start, E.failure→exit, B.success/failure→E.resume). CORRECT on canonical
   `every i:=1 to N do write(i)` → 1|2|3. BUT non-trivial bodies (write(i*2), write("x"||i)) HANG/mis-iterate: body
   tail success edge resolves to the IR_ASSIGN wrapper, not the inner IR_TO generator resume port → loops re-running
   the assign with the same value. Localized via --dump-ir. Reverted vs shipping an infinite loop. FIX: assignment-
   lowering must forward generator resume as cx->beta, OR a bounded-body primitive (JCON "always bounded" has no
   SCRIP lower equivalent).
**Icon smoke 6/12 both modes** (pass: write_str/write_int/arith/string_op/while/proc_zeroarg; fail: if_expr/every/
until/repeat_break/proc_recursion/bare_if — all control-flow generators sharing the same resume gap ir_Every
surfaced). **NEXT: the generator-resume-through-assignment fix unblocks every/while-gen/until/repeat at once — do it
before more ir_a_* conversions.** Then continue the JCON-IR checklist (ir_Goto/ir_Succeed/ir_Fail/ir_Call verify-
faithful; ir_Alt/ir_ToBy/ir_Field/ir_Deref/ir_OpFunction convert). JCON IR-record→SCRIP map + checklist in handoff.

## Watermark (prior)
**HEADER-MERGE LANDED + IR_LIT_* RENAME + IR_SEQ DELETED — 2026-06-30 (Sonnet 4.6, Lon directing).** SCRIP
`f54777b6`→`dd082890`→`a0e86b41` (2 commits). Suite **PASS=62/XFAIL=36** and mutation gate **HARD=4/C=14**
unchanged at every step; both gate programs (`hello world`, `write(1+1)`) green mode-3 AND mode-4 throughout.
Per the standing directive, NO `.s` artifact regen run this session (deliberate, not an oversight — the
directive states regen scripts track output, they are not pass/fail gates, and the big suites are too slow
to be worth it for behavior-preserving changes).
1. **`dd082890` — emitter header consolidation, 15 → 2 (`emit.h` + `sil_macros.h`).** This was prior-session
   work exported as an unpushed-commit zip (parent `f54777b6`, the SCRIP tip at session start) and reapplied
   via `git apply` against a verified-matching parent; see the commit body for the full header-merge detail.
   Confirms independently: **`bb_regs.h` had 0 repo references before this merge** — the register contract
   PLAN.md calls "the SINGLE source of truth" is hard-coded as bare `"r12"`/`"r13"` strings in templates, not
   read through `bb_regs.h` macros. PLAN.md's session-start step 7 (which still names `src/emitter/bb_regs.h`)
   is now stale — the file doesn't exist; `emit.h` is the merged target. Flagging here rather than editing
   PLAN.md per RULES.md ("do NOT edit PLAN.md goals table on routine handoff" — this is the same spirit for
   the session-start checklist, which isn't the goals table but is still PLAN.md content best left to Lon's
   call). Also clarifies a doc/reality gap from earlier this session: `emit_bb.c`/`emit_core.c`/`emit_drive.c`
   named throughout this goal file's body and in REPO-SCRIP.md/PLAN.md's BB-CODEGEN reading list **no longer
   exist as separate files** — `a4f51066` (2026-06-29, already on origin before this session) consolidated all
   three into the single `src/emitter/emit.cpp` (1211 lines). The goal-file prose pre-dates that consolidation
   throughout; treat every standalone mention of `emit_bb.c`/`emit_core.c` as "the corresponding region of
   `emit.cpp`," confirmed via `git log --follow`/commit-message archaeology, not asserted from absence alone.
2. **`a0e86b41` — two independent cleanups, gate-verified together.** (a) Renamed `IR_LIT_I/_F/_S` →
   `IR_LIT_INTEGER/_REAL/_STRING` and `IR_CSET_LIT` → `IR_LIT_CHARSET` (whole-word match, 34 files spanning
   all six `lower_*.c`, `emit.cpp`, runtime, templates, tools, driver, test probes; `IR_e` re-alphabetized
   per the `a0b2d18e` convention). (b) Deleted the dead `IR_SEQ` opcode: every live-build site read it through
   a `nd->op != IR_SEQ || IR_LIT(nd).dval != 1.0` discriminant-tag guard (the exact pattern this file's TRACK D
   names as the violation to eliminate) feeding into recursion/return paths gated on **permanently-null**
   `IR_graph_t * L/R/sl/sr = (IR_graph_t *)0` locals — meaning every `IR_SEQ` branch in `scrip_ir.c`
   (`ir_tmp_slot_assign`, `ir_drive_slot_assign`, `bb_print`'s dump label) and `bb_call.cpp` (the concat-arg
   inline-flatten fast path + its sole helper `carg_seq_flatten`) was structurally unreachable-to-success —
   confirmed by direct read of each site, not inferred from JCON-absence. `lower_snobol4.c` is the only
   non-degenerate `IR_SEQ` producer (real γ/ω-wired nodes with `dval=1.0`) but does not compile against the
   current `IR.h` at all (confirmed via standalone `gcc -c`: dozens of pre-existing undeclared-`IR_*` errors,
   e.g. `IR_LIT_NUL`/`IR_IDX`/`IR_CALL_DEFINE`) and is not in the Makefile — wholesale stale since before the
   IR_e amputation series, out of scope per the standing directive (non-Icon cancelled until Icon lands).
   `lower_raku.c` is in the identical state for the identical reason (also referenced `IR_FIELD_GET`/
   `IR_FIELD_SET`, real enum members before the amputation collapsed them to bare `IR_FIELD`; not restored —
   the file as a whole needs a from-scratch rebuild against the current enum, not a two-name patch).
3. **`IR_NOT` and `IR_CONJ` — investigated this session, NOT changed. Read before touching either.**
   - **`IR_NOT` is a live BUG, confirmed by direct testing, not merely an architectural-purity issue.**
     `write(not (1 = 2))` — `not` on a genuinely-failing sub-expression, wrapped as a call argument — produces
     **zero output and exit 0**, when correct Icon semantics (confirmed against JCON's `ir_a_Not`, which is
     pure `ir_Goto` threading: `success→failure`, `failure→write-null+success`, no dedicated operator node)
     demand either an empty-line print-then-continue (current-failure path succeeds) or a clean skip-and-
     continue (current-failure path itself fails) — neither happens; the calling statement chain never
     resumes (`"after-not"` style markers placed after the `write(not …)` line never print). Isolated against
     a clean baseline: `write(1 = 2)` alone (no `not`) correctly prints nothing AND correctly continues to the
     next statement, so the break is specific to `IR_NOT`'s wiring, not a general failure-propagation gap.
     SEPARATELY, `--dump-ir` segfaults on the same program after only 2 of 9 nodes print — a second symptom of
     the same malformed graph, not a separate bug. **This needs RULES.md's MONITOR-FIRST protocol (2-way
     sync-step monitor against SPITBOL/CSNOBOL4, bracket the divergence, gdb hit-count break) before any fix
     attempt** — it was surfaced while investigating whether `IR_NOT` could fold to `IR_UNOP_TEST` (the wrong
     target, see below), not hunted deliberately, so the bracket/divergence work has not started.
   - **`IR_UNOP_TEST` is NOT the right target for `IR_NOT`** — this was the working hypothesis going into the
     session and it's wrong. Checked: `IR_UNOP_TEST` is currently fully inert (named, counted as a value-
     producer in `ir_node_produces_value`, zero producers, zero driver/template wiring). Icon's actual `/x`/
     `\x` null-test operators (the genuine intended use for an `IR_UNOP_TEST`-shaped slot) are ALREADY correctly
     wired end-to-end today via a different mechanism: `lower_icon.c`'s `TT_NULL` case builds a generic
     `IR_UNOP` tagged `ival=TT_NULL`, and `bb_unop.cpp`'s existing `unop_op` dispatch (`UO_NULL_TEST`,
     `UO_NONNULL`) already has full, live x86 codegen for both cases keyed off exactly that tag. So there is
     no live gap to fill at `IR_UNOP_TEST` — it is closer to `IR_BINOP_GENERIC`/`IR_UNOP_GENERIC` (reserved-
     but-superseded scaffolding) than to a missing wire. Do not retag `TT_NULL` onto `IR_UNOP_TEST` without
     first confirming the `ival`-tag mechanism it would replace is itself something Track D wants gone (it
     IS the discriminant-tag pattern Track D targets in spirit, but unlike `IR_SEQ`'s dead branches, this one
     is LIVE and WORKING — folding it is a real Track-D-style migration with a working baseline to preserve
     via before/after `.s` diff, not a dead-code deletion). Separately: `TT_NONNULL` (`\x`) has NO dispatch
     case in `lower_icon.c`'s main switch at all (only appears in an arity-counting helper) — a genuine
     missing-construct gap, distinct from the `IR_NOT`/`IR_UNOP_TEST` question, not investigated further this
     session (new feature work, not in scope for a rename/cleanup pass).
   - **`IR_CONJ` confirmed foldable to pure `IR_GOTO`/edge-threading, matching the existing `IR_IF`/`IR_EVERY`
     precedent** (`ae70cb2b`, this file's IR-PARITY watermark: "no JCON `ir_If`/`ir_Every` records exist...
     Goto/Succeed/Key threading only, no dedicated opcode"). Verified by reading JCON's `ir_a_Compound`
     directly (`irgen.icn:1231`): Icon's compound/sequencing expression (`e1; e2; e3` semantics — NOT
     short-circuit `&`; each sub-expression's success AND failure both thread to the next sub-expression's
     `start`, only the LAST sub-expression's success/failure reach the compound's own success/failure) is
     built with nothing but `ir_chunk`+`ir_Goto` wiring across sub-expression `.start`/`.success`/`.failure`
     labels — zero dedicated conjunction node, zero `ir_OpFunction` involvement. SCRIP's `IR_CONJ` reifies
     this as a real opcode with real `emit_drive` driver logic (`DRIVE_PAIR_JMP(lbl_γ)` etc., not a stub) and
     three live lower-side producers (`lower_icon.c`, `lower_pascal.c`, `lower_raku.c` — note `lower_raku.c`'s
     `IR_CONJ` sites are NOT proof of live-Raku status; the file is non-building for unrelated reasons listed
     above, this is just the one opcode name among its many broken references that happens to still exist in
     `IR.h`). **NOT folded this session** — unlike `IR_SEQ`, `IR_CONJ`'s current implementation is NOT known
     to be broken (not tested as rigorously as `IR_NOT` was; the `not`-investigation detour consumed the
     session's remaining budget for this kind of probing), so there is a working baseline to risk regressing,
     and the fold touches real driver edge-wiring logic across three lowers rather than deleting unreachable
     branches. Treat as its own rung: convert `lower_icon.c`'s/`lower_pascal.c`'s `IR_CONJ` construction sites
     to direct success/failure→next-start `IR_GOTO` wiring per `ir_a_Compound`'s exact shape, verify `.s`
     byte-identical on a multi-statement Icon program exercising it (e.g. `write(1); write(2); write(3)` or
     whatever currently lowers through `lower_conj`/equivalent — locate the call site first), THEN delete the
     opcode + driver case + `bb_conj` template once zero producers remain.
**NEXT:** either (a) MONITOR-FIRST diagnosis of the `IR_NOT` bug per RULES.md (bracket the divergence against
SPITBOL on a minimal `not`-exercising program, gdb hit-count break at the bracketed site), or (b) the
`IR_CONJ`→edge-threading fold per the recipe above, run independently with its own before/after `.s` check.
Both are scoped and ready to pick up; neither was started beyond the investigation already on record above.

**Prior watermark below.**

**IR-PARITY: IR_e 26 → 37 — full bc_gen instruction parity with JCON; IR_IF/IR_EVERY removed — 2026-06-29 (Sonnet 4.6, Lon directing).** SCRIP `ae70cb2b`. Session was orientation + IR shaping. Three decisions made and locked: (1) **VAR/DEREF SPLIT** — `IR_VAR` = lvalue reference, `IR_DEREF` = value, faithful to JCON's `ir_Var`/`ir_Deref` split; rval sites will emit IR_DEREF explicitly when the mechanical gen_bc transcription lands. (2) **IR_IF + IR_EVERY REMOVED** — no JCON `ir_If`/`ir_Every` records exist; both lowerers stubbed to IR_FAIL in lower_icon.c; dispatch cases/branches deleted from emit_core.c, emit_x86_drive.c, emit_bb.c, scrip.c. Will be rebuilt mechanically from irgen.icn's ir_a_If/ir_a_Every (Goto/Succeed/Key threading only — no dedicated opcode). (3) **13 JCON-mirror opcodes added inert** (enum + name table only; no driver/lower wiring): IR_CSET_LIT, IR_FIELD, IR_DEREF, IR_MAKE_LIST, IR_SCAN_SWAP, IR_ENTER_INIT, IR_INDIRECT_GOTO, IR_UNREACHABLE, IR_CREATE, IR_CORET, IR_COFAIL, IR_MOVE, IR_RESUME_VALUE. Every bc_gen_ir_* instruction target now has a SCRIP opcode except the four sanctioned structural divergences (ir_Tmp→tmp field; ir_Label/TmpLabel/MoveLabel→bb_label_t+γ/ω edges). Gate: HARD=4 (unchanged). Gate programs: both green. NEXT: mechanical gen_bc.icn → driver transcription, starting with the Var/Deref/StrLit/Call/Succeed/Fail spine.

**Prior watermark below.**

**SECOND ENUM AMPUTATION LANDED — IR_e 94 → 26 members (68 more deleted); branchopt.c removed — 2026-06-29 (Sonnet 4.6, Lon directing).** Deleted every IR_e member unused by the 87/86 passing programs in mode-3/mode-4. Keep-set: IR_LIT_{I,S,F}, IR_VAR, IR_ASSIGN, IR_BINOP, IR_UNOP, IR_CALL, IR_SEQ, IR_FAIL, IR_SUCCEED, IR_GOTO, IR_RETURN, IR_IF, IR_CONJ, IR_EVERY, IR_ALT, IR_NOT, IR_TO, IR_PROC_GEN, IR_KEYWORD, IR_CALL_{PROC_STAGED,USERPROC,BYNAME,BUILTIN,GVAR_USERPROC}. Key finding: IR_UNOP retained (prior session's dump-derived list had it wrong; --dump-ir segfaults hid write(-x)/write(*s) usage; real gate caught it). Fanned variants IR_NEG/POS/SIZE/NONNULL/NULL_TEST deleted correctly. binop_cat_t added to IR.h (BINOP_CAT_ARITH/RELOP/CONCAT) replacing deleted IR_BINOP_RELOP/CONCAT/ARITH; binop_slot_kind() returns int. ir_is_scan_kind() neutralized (return 0). lower_icon.c: 20 deleted-op build() calls → IR_FAIL (constructs that already FAILed; rebuilt later). branchopt.c/h git-rm'd (bopt_chain had zero callers after GZ reduction; GROUND ZERO, rebuilt later). Gate: HARD=4 (unchanged). Suite: PASS=91/289 mode-3, PASS=90/289 mode-4, zero regressions verified by stash-rebuild-diff. Heartbeat green. SCRIP a0cec369. NEXT: B4 (call-kind classification to LOWER for gate=0); pull remaining dead BB templates from Makefile build.

**Prior watermark below.**

**R1 LANDED (Icon severed from legacy fat driver) + MODE-4 TEXT PATH RESTORED + BOTH MODES GREEN ON THE
162-PROGRAM PASS SET — 2026-06-29 (Sonnet 4.6, Lon directing).** Two rungs, both Icon-smoke-and-sweep verified.

**Measurement first (this session opened by grounding the "87" claim):** the Icon corpus has grown — **162**
programs now pass `SCRIP_ICN_BB=1 --run` (multiline-safe comparison; "87" was the official rung-suite snapshot
at an earlier commit). `--dump-ir` over all 162 shows **16 distinct LOWER-produced ops** (`IR_LIT_{S,I,F}`,
`IR_VAR`, `IR_KEYWORD`, `IR_BINOP`, `IR_NOT`, `IR_ASSIGN`, `IR_CALL`, `IR_TO`, `IR_EVERY`, `IR_CONJ`, `IR_IF`,
`IR_SUCCEED`, `IR_FAIL`, `IR_RETURN`); the emit-time call resolver fans `IR_CALL`→`IR_CALL_BUILTIN`/
`IR_CALL_PROC_STAGED`/`IR_PROC_GEN`, so **19 ops are actually dispatched** out of **222** in `IR.h`. The
enum-amputation target is therefore 19 (runnable floor; literal-16 won't link — the 3 call variants are
emit-produced) up to the ~37 keep-set (template/cross-TU bare-ref pins). **The amputation is GATED:** deleting
to 19 currently breaks **159 enum members across the live build** — 115 in `emit_bb.c` (SNOBOL pattern +
Prolog `gz_*`/`pl_gz_*` clusters), 70 in `scrip.c` (`pl_gz_*`), 40 in `opt/ir_query.c`, 36 in `lower_icon.c`
(Icon lower still emitting unowned ops). Confirms the prior handoff: **remove the non-Icon emitter code FIRST
(R2/R3), then the enum delete falls out as a ~36-site Icon-only edit.** Measurement scripts on sandbox.

**R1 — Icon dispatch flipped off the legacy `bb_build_flat` path (committed `4d31aff0`).** `ring_to_tree` (the
stack-reconstruction reconstructor) bailed to NULL for any chain containing a literal or binop (every real
program), so all 162 already flowed through `descr_flat_chain_build` → `emit_drive`; the `root_node!=NULL`
branch only reached the GROUND-ZERO abort stubs `bb_build_flat`/`codegen_flat_build`. Proved dead empirically
(instrumented branch, rebuilt, ran 162 → **0 hits**), then made the flip explicit on BOTH the mode-3 (`--run`)
and mode-4 (`--compile`) dispatches and deleted the dead `ring_to_tree` + sole helper `node_arity` (43 lines).
This severs Icon from `walk_bb_flat`/`bb_build_flat`/`codegen_flat_build` — the R2 prerequisite.

**MODE-4 TEXT RESTORED (0 → 161/162).** Lon's directive: both modes must work on the pass set. Mode-4 was at
**0/162** — the GROUND-ZERO reduction `a7958465` had DELETED the entire text-emit path to abort stubs (the
"mode-4 green" claim predated it, at `6058d6f8`). Restoration was SMALL because **the text path reuses the
mode-3 driver**: `descr_flat_chain_build_text` calls the same `codegen_flat_chain_body` → `emit_drive` loop,
medium-agnostic. Un-stubbed five thin wrappers to their original bodies (`g_bb_alpha_seq_reset`,
`descr_flat_chain_build_text`, `descr_flat_chain_build_proc_text`, `data_buf_reset`,
`data_buf_flush_pending_label`) + re-added the deleted helper `data_buf_appendf`. No new driver logic; the
SNOBOL-only `pre_build_children_text` stays stubbed (Icon never reaches it). The `.so` link gap (4 undefined
non-Icon symbols `prolog_lower`/`rebus_compile`/`bb_gather_prepare`/`bb_mapgrep_prepare`, from the Icon-only
Makefile trim) is closed by a NEW `src/lower/rt_noicon_stubs.c` added to **RT_PIC_SRCS ONLY** — NOT the `scrip`
binary recipe, which compiles the real TUs (a first attempt to stub them in the shared `lower_noicon_stubs.c`
multiply-defined and was reverted). The sole mode-4 holdout is `parser/cset_lit.icn` (`x:='aeiou'`) — a
PRE-EXISTING cset-literal segfault that hits `--dump-ir`/`--compile` even on the R1-only tree (confirmed not
introduced here); it passes mode-3 `--run`.

**Verified:** mode-3 `--run` 162/162 (0 regression); mode-4 compile→as→ld→run 161/162; both gate programs full
mode-4 cycle (`hello world`, `3`); mutation gate unchanged **HARD=4**. **NEXT: R2 — remove the now-dead
SNOBOL/Prolog clusters from `emit_bb.c` + `scrip.c` (the 115+70 break-refs), then R3/R4/R5 enum amputation.**


## Watermark (prior)
**IR_t VALUE PAYLOAD COLLAPSED TO ONE UNION + `state`/`stno` WHACKED + FIELD-DISCIPLINE GATE BUILT + PASS=2 GREEN
— 2026-06-28 (Sonnet 4.6, Lon command decision).** This session collapsed `IR_t` per JCON field discipline.
`state` DELETED (dead), `stno` folded into `ival` then DELETED (SUCCEED-only), and the three value payload fields
became ONE anonymous union `union { const char * sval; int64_t ival; double dval; }`. The CALL co-use (name+argc+
dval-flag) was resolved by sourcing arity from `n_operands`, so a CALL holds only `sval`. **GATE = PASS=2:
`write("hello world")` → `hello world` and `write(1 + 2)` → `3`, both mode-3 AND full mode-4 cycle.** Per Lon the
language LOWER sessions rewire from GROUND ZERO #5, so PASS=2 is the entire completion test for the collapse;
co-use constructs (scan, nested VAR hops, suspend, complex-call subgraphs) are corrupted-by-design and rebuild on
the flat operands+edge model. Bonus survivors (not required): vars, arith, if/while, relops, every/to generators.
`counter` kept SEPARATE (its ~60 child-smuggle sites move to `operands[]` in a later rung; folding/deleting now
breaks the build). ENFORCEMENT GATE `scripts/test_gate_ir_field_discipline.sh` built (ratchet, live debt 190 — all
in now-broken rebuild-me code; lower toward 0 as languages land). See TRACK D for the full landed list + remaining rungs.
IR-mutation gate unchanged at HARD=38. **PUSH PENDING — credential needed; handoff INCOMPLETE until pushed.**

**PRIOR watermark below (unified slot pass / `.s` byte-identity rule deletion) retained for history.**

**⛔ RULE DELETED (Lon, 4th request — honored).** The `.s`-byte-identical requirement is GONE permanently (see
the STANDING DIRECTIVE bullet at the top of this file). It is NOT a gate, completion test, or regression signal,
anywhere. The `.s` WILL change drastically as LOWER + the EMITTER DRIVER are rewritten. Struck from the directive
bullet and the B5 completion test. (RULES.md step-4 was already correct — `.s` scripts "NEVER enforce sameness".)

**⛔ ARCHITECTURE DECISION (Lon, corrected): there are SIX LOWERS (one per language), each calling the SAME slot
TECHNIQUE; there is ONE language-INDEPENDENT EMITTER DRIVER (`emit_jcon_node`) handling generic CS constructs.**
The slot technique = a LOWER-time pass assigning every value-producer's `tmp` field (`ir_drive_slot_assign` is the
shared utility today; each of the six lowers invokes it). The ONE driver's only guarantee: the proper BB is invoked
and every variable lives in the ONE place (`g_emit`) set correctly. It reads `nd->tmp` + operands, never mutates IR,
ZERO chain-flag dependencies. Icon regression may go to ZERO and grow back — gate is `write("hello world")` +
`write(1 + 1)` only.

**⛔ IR_TMP OPCODE REMOVED + `lhs` FIELD RENAMED `tmp` (`19cbedd5`).** The `IR_TMP` enum value was DEAD (zero nodes
ever constructed — JCON uses `ir_Tmp` as a NODE; SCRIP realizes the temp as a plain `int` FIELD on the producer).
Removed enum value + name-table entry → `IR_OP_COUNT` −1. The field, mis-copied from JCON's `ir.icn` record-field
name `lhs` (a misnomer — there is no `=` for `write(1+1)`; it is a three-address-code TEMPORARY slot), is RENAMED
`tmp`. `--dump-ir` now prints `tmp=`. `own`/`idx` KEPT — load-bearing sidecar (`IR_LIT`/`IR_EXEC` index through them).

**LANDED THIS SESSION (5 SCRIP commits):**
1. `e44e2359` — `IR_LIT_F` + `IR_LIT_NUL` → clean dispatch (`jcon_value_slot` reads `nd->tmp`).
2. `be7d8c8f` — `IR_KEYWORD` → clean dispatch + added to LOWER producer set (scalar keyword `&ucase`/`&digits`).
3. `c1e282c7` — **NEW UNIFIED SLOT PASS.** Collapsed the TWO competing passes (`ir_tmp_slot_assign_flat` numbering
   value-producers from 0 + `ir_jcon_slot_assign` renumbering only literals from 16 — the disagreement that made
   every prior attempt wobble) into ONE `ir_drive_slot_assign` (in `scrip_ir.c`): slots EVERY `ir_node_produces_value`
   node EXCEPT `IR_VAR` (lvalue-ref, by-name via varslot) on one base from 16, recurses leaf-SEQ. Single source of truth.
4. `19cbedd5` — **IR cleanup:** remove dead `IR_TMP` opcode, rename `lhs`→`tmp` field (see above).

**VERIFIED GREEN (the gate + more):**
- `write("hello world")` → `hello world` — mode-3 AND full mode-4 cycle (`as+gcc+link+run`).
- `write(1 + 1)` → `2` — mode-3 AND full mode-4 cycle.
- `a:=10;b:=20;c:=a+b;write(c);write(a*b)` → `30`/`200` both modes (varslot region + value region coexist cleanly).
- Spine survivors (regression-to-zero authorized but these held): `write(2+3*4)=14`, `write(-7)`, reals, `&ucase`.
- Both gate programs use ONLY converted ops (LIT_S/LIT_I/BINOP/CALL/SUCCEED/FAIL) — `default: walk_bb_flat` NEVER
  fires for them; within those arms `jcon_value_slot` reads `nd->tmp` so `bb_slot_alloc16` is never hit. NEW path genuinely drives the spine.

**Gate: HARD=38 (A=29 op-writes + B=9 field-writes). Unchanged all session.**

**ANSWER — does every IR produce a result / use the temp field?** NO. Only value-producers (`ir_node_produces_value`:
lits/var/binop/unop/call-kinds/proc_gen) carry a `tmp`. Control/effect ops (GOTO/IF/SUCCEED/FAIL, and ASSIGN whose
effect is the store) produce no value and fill no `tmp`. As of `c1e282c7`+`19cbedd5` the `tmp` slot is assigned by
ONE LOWER pass (single source); the EMITTER reads it in the converted spine arms only — the chain-flag-gated ops
(global assign, IF, SEQ) still fall back to `walk_bb_flat`. Extending the driver's read to those is the next work.

**NEXT (grow the driver from the gate):**
1. Drive `emit_jcon_node` to read operand slots from `operands[]->lhs` directly (single source) rather than
   `descr_binop_opnd_slot`/`bb_slot_get` (slotmap) — purely cosmetic now that the unified pass feeds both, but it
   makes the read independent of emit-order.
2. Grow the converted op set toward the chain-flag-gated ops by FIRST unifying `g_descr_flat_chain` vs
   `g_gvar_flat_chain` (the P2 consolidation) so global `IR_ASSIGN`/`IR_IF`/`IR_SEQ` can read the unified slotmap.
3. Retire `walk_bb_flat` fallback op-by-op as each converts; retire `jcon_value_slot`'s `bb_slot_alloc16` fallback.
4. When a second language is ready, route it through `emit_jcon_node` + `ir_drive_slot_assign` (the universal driver
   + universal LOWER technique) — proving the all-language claim.
5. Gate strict-0 (B7) — the op-writes/field-writes fall as `walk_bb_flat` paths are retired.

---

## Watermark (prior)
**TT_IF CONVERTED (JCON `ir_a_If`) + IR_BINOP_RELOP ω-REACHABILITY — 2026-06-30 (Sonnet 4.6, Lon directing).**
SCRIP local HEAD `59dafbc0` (1 commit past `c8ab2ad7`; **PUSH PENDING — credential needed, handoff INCOMPLETE
until pushed**). First TT converted by the mechanical JCON→SCRIP methodology this campaign asks for: take the
four-port wiring from `irgen.icn` (`ir_a_If`, unbounded form = pure `ir_Goto` threading, NO dedicated opcode)
and realize it as SCRIP edge-threading in `lower_icon.c` — `cond.γ→then_entry`, `cond.ω→else_entry`,
`then/else.γ→if.γ`, `then/else.ω→if.ω`, absent-else routes `cond.ω` straight to the if's ω node (JCON
`a_Key("fail")→Goto failure`; an `IR_FAIL` placeholder is WRONG here — the flat-chain BFS skips IR_FAIL nodes
and does not follow their edges, stranding the fall-through). NO template, NO `emit_drive` case (faithful to
JCON, which has no `ir_If` record — the goal body's "IR_IF needs NO driver case" is correct).
**Paired emitter fix (the actual unlock):** `codegen_flat_chain_body`'s BFS (two sites in `emit.cpp`) followed
the ω-target of `IR_BINOP` but NOT `IR_BINOP_RELOP` — a gap left by the 2026-06-29 IR-FORM-SPLIT (`8f346962`)
that minted `IR_BINOP_RELOP` as its own opcode. So every relop's FAILURE branch (the whole job of an if/while/
until condition) was undiscovered and emitted nothing. Additive reachability (surfaces real ω targets, removes
no edge). **RESULT: Icon rung suite PASS 61→80 (+19), byte-identical mode-3 (`--run`) and mode-4 (`--compile`);
icon smoke 6/12→10/12 both modes** — `if_expr`/`bare_if` (direct), plus `until` and `proc_recursion` which were
gated on the same relop-ω gap, not on if-lowering. Verified through the full mode-4 cycle (`--compile`→as→gcc
`-no-pie`→`libscrip_rt`→run): `fact(5)`=120, `until` 5..1, if/else→correct branch. Both gate programs green both
modes. **Mutation gate unchanged HARD=4.** no-stack/one-reg/semicolon gates green; `local-no-nv` LOCK 3 (global
`TT_ASSIGN` GVA) was ALREADY FAIL on baseline (known punch-list GAP, confirmed via stash-rebuild — not introduced).
No artifact regen (standing directive: `.s` not a gate). **NEXT (in order):** (1) value-context `if` unification
(shared result slot / IR_MOVE join — JCON's one-`target`-tmp trick); (2) `repeat` loop-back redesign (the
IR_FAIL-placeholder-as-loop-target bug, root-caused above — `repeat{…}` runs body once then exits); (3) `every`
resume-gap (the documented two-attempt minefield: body tail success must forward the generator's resume as
`cx->beta`, OR a bounded-body primitive). The relop-ω-reachability fix is general infrastructure the loop/every
work now builds on.


Local HEAD `SCRIP@be7d8c8f` (2 commits past `0e677f4c`; **PUSH PENDING — credential needed, handoff INCOMPLETE
until pushed**). Climbed two clean rungs off the beachhead, then probed the GVAR-assign frontier and REVERTED
before commit (stash/pristine discipline held). Gate **HARD=38 unchanged** across both landed rungs.

**LANDED RUNG 1 (`e44e2359`) — `IR_LIT_F` + `IR_LIT_NUL`.** Same one-liner pattern as `IR_LIT_I/S`:
`g_emit.op_off = jcon_value_slot(nd); FILL(...)`. `write(3.14)`/`write(2.0+1.5)=3.5` correct mode-3 +
full-cycle (`as+gcc+link`). Structurally identical to old (31=31 insns; offsets renumbered to LOWER
`16+k*16` scheme — NOT byte-identical, correct by design). Gate 38, hello world green.

**LANDED RUNG 2 (`be7d8c8f`) — `IR_KEYWORD`.** Two coordinated halves: (a) emit arm
`g_emit.op_sval = IR_LIT(nd).sval; g_emit.op_off = jcon_value_slot(nd); FILL(...)`; (b) added `IR_KEYWORD`
to LOWER `jcon_converted_producer` (`scrip_ir.c`) so it gets a real `lhs` slot. `write(&ucase)`/`write(&digits)`
preserved mode-3 + full-cycle; 33=33 insns, pure offset renumber (`[r12+0/8]`→`[r12+32/40]`). Gate 38.
(NOTE: `&letters` prints empty — PRE-EXISTING, not introduced here; `&ucase`/`&digits` fine.)

**FRONTIER PINNED — THE CHAIN-CONTEXT WALL (the reason the remaining ops are NOT one-liners):**
Attempted to route simple global `IR_ASSIGN` (literal/var/call RHS) through `emit_jcon_node` →
`flat_drive_gvar_assign`. **REGRESSED (run went empty) → REVERTED, tree clean at `be7d8c8f`.** Root cause,
now fully diagnosed and decisive for the next session:
- The real `walk_bb_flat` global `IR_ASSIGN` dispatch (L3164–3174) is **gated on `g_descr_flat_chain` vs
  `g_gvar_flat_chain`** and selects between **TWO different drivers** — `flat_drive_global_assign` (descr
  chain, emits `# IR_ASSIGN_DESCR gva` → store to `[rbx]` arena) and `flat_drive_gvar_assign` (gvar chain).
  Picking one without replicating the chain-flag dispatch silently took the LOCAL store path
  (`# IR_ASSIGN local` → `[r12]`), so the global write never hit the arena.
- **`IR_IF` (L3137) and `IR_SEQ` (L3149) are ALSO chain-gated** on the same two flags.
- **KEY STRUCTURAL FACT (preserve this property):** `emit_jcon_node` itself is **100% chain-flag-free**
  (grep `g_descr_flat_chain|g_gvar_flat_chain` in its body = 0). All chain entanglement lives ONLY in the
  `walk_bb_flat` paths it delegates to. So the clean-convertible ops are EXACTLY the chain-independent ones
  (lits, keyword, local+global `IR_VAR` rval, binop, unop, call, succeed, fail — all DONE); the remaining
  fallbacks (`IR_ASSIGN`-global, `IR_IF`, `IR_SEQ`, the gvar-binop F1 cluster) are blocked behind the
  `g_descr_flat_chain`/`g_gvar_flat_chain` split. **This is precisely the P1/P2 consolidation the prior
  watermark called for: the N chain conventions must be unified into ONE base discipline BEFORE these ops
  convert cleanly.** Converting them piecemeal against the live chain flags is what regressed this session
  and the band-overlay sessions before it.

**Converted arms in `emit_jcon_node` (as of `be7d8c8f`):**
`IR_LIT_S` · `IR_LIT_I` · `IR_LIT_F` · `IR_LIT_NUL` · `IR_KEYWORD` · `IR_VAR` (local lvalue-ref via varslot;
global via `op_gva_k`/`gva_index_of`; `&`-keyword) · `IR_BINOP` (operand tmps, `op_binop_kind` dispatch, no
`->op` swap) · `IR_UNOP`/NEG/POS/NONNULL/NULL_TEST/SIZE/NOT · `IR_ASSIGN` (LOCAL store; global→fallback) ·
`IR_CALL` · `IR_SUCCEED` · `IR_FAIL`. **All chain-flag-free.**

**Gate: HARD=38 (A=29 op-writes + B=9 field-writes). Unchanged.** No full regression (authorized). No artifact
regen. hello world + lits/reals/keyword/var/arith/IO spine verified mode-3 + full-cycle every landed rung.

**NEXT RUNGS (next session, in order):**
1. **P2 FIRST — unify the chain conventions.** Before any of `IR_ASSIGN`-global / `IR_IF` / `IR_SEQ` can
   convert, collapse `g_descr_flat_chain` vs `g_gvar_flat_chain` (and the `flat_drive_global_assign` vs
   `flat_drive_gvar_assign` driver pair) into ONE base discipline with an explicit per-graph slot layout.
   This is the documented prerequisite — do NOT attempt the global ops against the live two-flag split.
2. THEN global `IR_ASSIGN` (literal/var/call RHS) → clean dispatch reading the unified slotmap.
3. THEN `IR_IF` / `IR_SEQ` control flow against the unified base.
4. THEN the gvar-binop F1 cluster (the 11 `->op` swaps, biggest gate drop) via `op_gvar_route` field.
5. Extend `ir_jcon_slot_assign` to ALL producers (value+var+scratch) → emit cursor retires wholesale.
6. Gate strict-0 (B7).

---

## Watermark (prior)
**JCON-DRIVER BEACHHEAD + 5 SPINE RUNGS — 2026-06-28 (Sonnet 4.6).**
Pushed `SCRIP@0e677f4c`. Strategy shift: STOP overlaying a band on the walk-order cursor. Instead build
`emit_jcon_node` — a from-scratch dispatch (the `bc_gen` analog) inserted beside `walk_bb_flat` as the
Icon chunk-walker's primary dispatch, with `walk_bb_flat` demoted to `default:` fallback that shrinks as
each op converts. `SCRIP_ICN_JCON=0` keeps old path as live A/B oracle.

**KEY TECHNIQUE (`jcon_value_slot`):** a converted producer reads `nd->lhs` (LOWER-assigned slot) AND
reserves it in the cursor (`if nd->lhs+16 > g_flat_slot_count: g_flat_slot_count = nd->lhs+16`) before
registering. This kills the collision wall that sank every prior attempt: without the reserve, the next
fallback `bb_slot_alloc16` would reuse the same offset. Storage rungs byte-identical to old path;
arithmetic structurally identical (same instruction count, offsets renumbered to LOWER scheme). Correct.

**Converted arms in `emit_jcon_node` (as of 0e677f4c):**
`IR_LIT_S` · `IR_LIT_I` · `IR_VAR` (lvalue-ref via varslot, not a value-tmp) · `IR_BINOP` (reads operand
tmps, `op_binop_kind` dispatch — no `->op` swap, F1 disease avoided) · `IR_UNOP`/NEG/POS/NONNULL/
NULL_TEST/SIZE/NOT · `IR_ASSIGN` (local store, global→fallback) · `IR_CALL` · `IR_SUCCEED` · `IR_FAIL`.

**Gate: HARD=38 (A=29 op-writes + B=9 field-writes). Unchanged across all 5 rungs.**
No full regression run (authorized). No artifact regen. hello world + expression/storage/IO spine verified
correct mode-3/4/full-cycle (`as+gcc+link+run`) every rung.

**NEXT RUNGS (next session climbs from here in order):**
1. `IR_LIT_F` / `IR_LIT_NUL` — trivial, same pattern as LIT_I.
2. `IR_KEYWORD` — descr arm sets `op_sval` + `jcon_value_slot`.
3. Global-var `IR_VAR` + `IR_ASSIGN` — currently fallback; needs `op_gva_k` + gva-index path.
4. `IR_GOTO` / `IR_IF` / `IR_CONJ` — control flow.
5. Extend `ir_jcon_slot_assign` to ALL producers (value+var+scratch) → emit cursor retires wholesale.
6. Gate strict-0 (B7): after option-(a) lands, sweep remaining op-writes + field-writes to 0.

---

## Watermark (prior)
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
**SESSION 2026-06-29 (Sonnet 4.6, Lon directing) — IR form-split: 6 new operator opcodes + relop migration.**
Added `IR_BINOP_RELOP`, `IR_BINOP_GENERIC`, `IR_UNOP_TEST`, `IR_UNOP_GENERIC`, `IR_SECTION`, `IR_SUBSCRIPT`
to `IR_e` (enum 37→43 members + `IR_OP_COUNT`). Each earns its opcode by having a distinct emitted BB
control-flow form (value vs failable/branch-to-ω vs resumable/closure vs lvalue-capable). `IR_SECTION`
naming confirmed from Icon canonical sources (`Op_Sect`, grammar `section`, JCON `a_Sectionop`) — not
"slice" (Python-only term). Migrated Icon relops: `lower_icon.c` now builds `IR_BINOP_RELOP` for codes
`BINOP_LT..NE`/`BINOP_SLT..SNE`; arith+concat stay `IR_BINOP`. `walk_bb_node` routes `IR_BINOP_RELOP`
directly to `bb_binop_relop()` (no sub-switch). 150/150 Icon programs byte-identical output (parent vs HEAD).
Mode-4 relop full cycle green. Mutation gate unchanged HARD=4. SCRIP `8f346962` pushed.
NEXT: `IR_UNOP_TEST` migration (same pattern: `/` `\` are `TT_NULL`/`TT_NONNULL` in lower_icon.c);
then `IR_BINOP_GENERIC` wiring; then `IR_SECTION`/`IR_SUBSCRIPT` (need real lower arms, currently IR_FAIL-stubbed).

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
