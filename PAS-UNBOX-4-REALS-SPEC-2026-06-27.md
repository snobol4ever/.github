# PAS-UNBOX-4 — real correctness: asm+source-grounded implementation spec (2026-06-27, Claude Sonnet)

Design-freeze for the reals rung, written from the live SCRIP/corpus tree (gates green at
**M3 128/0, M4 128/0** this session) so the implementation is mechanical next session with a full
context window and the four-language gate budget. **No code changed in this rung — spec only.**
Supersedes the reals paragraph of `PAS-UNBOX-ANALYSIS-2026-06-27.md` with the exact failing arm.

## Why this is its own session, not bolted onto UNBOX-1/2

UNBOX-1/2 landed Pascal-only (`pascal.y` + `lower_pascal.c`) because the runtime `DT_A` foundation
already existed; they only flipped array *creation*. Reals have **no** Pascal-only slice: the static
real classifier lives in **shared** `emit_bb.c` (`binop_operand_real_static`, line 1362) and the
assign consumer that bombs is **shared** `bb_gvar_assign.cpp`. Any edit there demands the full
four-language gate (SNOBOL + Icon + Prolog + Pascal) + template byte-identity before landing. Reals
are also flagged repo-wide as a known-fragile area. Hence: dedicated session, characterize-first done.

## Ground truth measured this session

| Probe | Source shape | M3 result | Verdict |
|-------|--------------|-----------|---------|
| `constreal.pas` | `r := pi` (real *const*), `writeln(r)` | `3.141592650000E+000` ✓ | real const→var→io OK |
| `realwidth.pas` | `r := sqrt(2.0)`, `writeln(r:N)` | all 6 lines ✓ | real builtin result + width OK |
| `realparam.pas` | `function half(x:real):real; half:=x/2.0; … writeln(half(r):10:1)` | **BOMB** `bb_gvar_assign int-binop: op_a_slot==-1 (binop slot not promoted)` (Aborted) | real param arith + fn-result assign BROKEN |

`realparam.ref` is a 1-byte `\n` (false-pass stub); correct value is `       3.0`. `rarith.pas` cited
in the older analysis is **not a committed probe** (it was an inline example) — do not look for it.

## Root cause, two entangled layers (both must be understood before touching code)

### Layer A — the static real classifier is a graph-scan heuristic, not a type system
`emit_bb.c:1362 binop_operand_real_static(g, o, depth)`:
- `o->op == IR_LIT_F` → **real** (this is the ONLY solid signal; it is why const/builtin reals work).
- `o->op == IR_VAR` → `var_assigned_real_static(g, name)`: scans `g->all[]` for an `IR_ASSIGN` whose
  `sval==name` and recurses on its RHS. **Real iff the var was assigned a (transitively) real RHS
  somewhere in the graph.**
- `IR_BINOP` → OR over children (with `operand_aux` for flat 2-operand nodes).

**Blind spots (the bug class):**
1. **Real PARAMS** — never assigned in the body, so `var_assigned_real_static` returns 0. `x` in
   `half` classifies non-real on its own. (`x / 2.0` happens to classify real *only* because the
   sibling `2.0` is `IR_LIT_F`; change it to `x / y` with both real params and it misclassifies int.)
2. **Real FUNCTION RESULTS** consumed by a caller (`half(r)` feeding `writeln`) — no `IR_LIT_F` in
   sight at the call site.
3. **Pure real-var/real-var ops** `z := x*y` where both sides are params or only-ever-assigned-from
   -other-vars: the scan can dead-end and classify int → silent `imul`/truncation.

### Layer B — `lower_pascal.c` tracks NO declared types (the actual root)
Confirmed in tree: the only real tag minted is `IR_LIT_F` from `TT_FLIT` (`lower_pascal.c:452`). The
`lower_var`/`lower_assign_var` arms (79/85/108/114) set `IR_LIT.sval=name`, `.ival=slot`,
`.dval=(double)hops` — **no type bit**. So a real *variable* read is indistinguishable at the IR from
an integer one; the emitter is forced into the Layer-A heuristic, which is fragile by construction.

### The `realparam` BOMB specifically (Layer B feeding a Frontier-1 fault)
The abort is NOT at the arith node — it is at `bb_gvar_assign.cpp`'s int-binop arm, `op_a_slot==-1`.
`half := x/2.0` assigns a binop result to the function-name var (`half`), routed through
`bb_gvar_assign`; that arm requires the RHS binop's operand slot to have been promoted, and it wasn't.
This is the **same assign-RHS-binop-slot-promotion shape as "Frontier #1"** (`s := s + a[j]`), now on
the real/function-result path. **Cause vs symptom (real-misclass vs slot-promotion) must be separated
with the monitor→gdb bracket, per RULES.md — do not guess-patch.**

## The principled fix (replace the heuristic with a declared-type bit) — 4 parts, ordered

Mirror the existing Pascal declaration registries (`g_pas_arrays` / `g_pas_recvars` / `g_pas_chararr`
+ `pas_is_chararr` / `pas_is_strtyped` in `pascal.y`). Add a **real-var registry**.

- **(a) lower/parse — declared real type [Pascal-only files; START HERE].**
  In `pascal.y`: a `g_pas_reals` name set, populated at decl parse for every `: real` var, value-param,
  var-param, and `function …: real` result name (and real const names already implied by `IR_LIT_F`).
  In `lower_pascal.c` `lower_var`/`lower_assign_var`: when the name ∈ `g_pas_reals`, set a real-type
  bit on the emitted `IR_VAR`/`IR_ASSIGN` node. **Pick the carrier deliberately:** `IR_LIT.dval` on a
  var node is ALREADY `hops` (79/85/108/114) — do NOT overload it. Use a distinct field/flag (a
  dedicated `IR_LIT` bit, or an `operand_aux` tag, or a new node-flag) so hops and real-type are
  orthogonal. Document the carrier in the Mechanism inventory.
  *This part alone is behavior-neutral until (b)/(c) consume the bit — but do NOT land it alone (it
  would be a set-but-unread tag = dead code, which this repo forbids). Land (a)+(c) together minimum.*

- **(c) emit — make `binop_operand_real_static` honor the declared bit [shared emit_bb.c].**
  Add, as the FIRST check in the `IR_VAR` arm of `binop_operand_real_static` (line ~1366):
  "if this var node carries the declared-real bit → return 1," before falling back to the existing
  `var_assigned_real_static` scan (keep the scan as the fallback for untagged shapes so nothing
  regresses). This is the shared edit → **four-language gate required**: SNOBOL/Icon/Prolog never set
  the Pascal real bit, so their classification is unchanged by construction — but PROVE it (stash+
  rebuild byte-identity on the three, per the PAS-GVA/DISPLAY landmine drill).

- **(b) emit — assign arms store `DT_R` for a real RHS [shared].**
  Audit every assign arm (`bb_gvar_assign.cpp`, `bb_assign_frame.cpp`, gvar + frame) so a real RHS
  writes tag `DT_R` (not `DT_I`) to the descriptor tag-half. Today literal reals work because they
  carry `IR_LIT_F`; the gap is real *variable*/result RHS. Coordinate with the `op_num_real` plumbing
  already present (`emit_bb.c:1387,1553,1559,1719`) — that flag is the existing real-routing signal;
  the fix is making it TRUE for declared-real var/result RHS, not only `IR_LIT_F`/`"ar"`.

- **(d) real arrays — native `double` ARBLK element [after (a)-(c), own gate].**
  An `array … of real` must use a native-`double` `ARBLK` element, not the `sprintf("%d")` text path
  (which cannot round-trip a double). Sequence AFTER the scalar real path is correct; this is the real
  analogue of UNBOX-1's integer `DT_A`.

## The `realparam` BOMB — resolve via monitor/gdb, not patch (RULES.md mandatory)

1. Monitor/bracket: the abort site is `bb_gvar_assign.cpp` int-binop arm (`op_a_slot==-1`). The
   bracketing statement is `half := x / 2.0`.
2. `gdb` break at the `bb_gvar_assign` int-binop arm + the slot-promotion site for the RHS binop;
   determine whether the slot is unpromoted because (i) the binop was misclassified int (Layer A) and
   took a no-slot path, or (ii) the fn-result assign consumer reads the wrong slot (Frontier-1). Use
   `SCRIP_NO_SEGV_HANDLER=1` for a clean backtrace; HW watchpoints do not work in this container.
3. Fix at the land-mine instruction. Re-run the monitor; confirm the divergence moves past the site.
4. Then fix `realparam.ref` from the 1-byte stub to `       3.0` (width-10, value-cross-checked vs
   fpc per the ⚖ Provenance rule) and treat the probe as a genuine pass.

## Gate (this rung is NOT done until all green)
- Pascal **M3 + M4** (target ≥ 128/0; `realparam` flips from BOMB to pass; `realparam.ref` corrected).
- New real probes worth adding: a real-param/real-param op (`z := x*y`, both params), a real fn-result
  arith, a real `for`/loop accumulation — to lock the Layer-A blind spots.
- **Four-language gate + template byte-identity** before pushing any `emit_bb.c`/`bb_*assign*.cpp`
  edit (stash+rebuild SNOBOL/Icon/Prolog fingerprints; SNOBOL M3 crosscheck must be byte-identical).
- DT_R real-array probe green in both modes (part d).

## Landmines
- **Do NOT overload `IR_LIT.dval` on var nodes** — it is `hops`. A separate real-type carrier only.
- **Land (a)+(c) together** — a set-but-unread real bit is dead code (forbidden here).
- **`binop_operand_real_static` / assign arms are shared** — four-language gate is non-negotiable;
  the Pascal real bit is never set for the other three, so they are unchanged *by construction* — but
  prove it with byte-identity, don't assert it.
- **Separate cause from symptom on the BOMB** with the monitor→gdb bracket before editing — the
  `op_a_slot==-1` abort may be Frontier-1 slot-promotion, real-misclass, or both.
- **Reals truncate silently when misclassified** (`imul` on truncated halves) — a wrong *value* with
  no crash is the dangerous case; the new param/param and fn-result probes are the tripwires.
