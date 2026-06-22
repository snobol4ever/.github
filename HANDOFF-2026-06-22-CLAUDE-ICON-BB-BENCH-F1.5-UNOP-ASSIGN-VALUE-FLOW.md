# HANDOFF — GOAL-ICON-FULL-PASS (Claude)
## BENCH-F1.5: flat-chain UNOP-assign value-flow LANDED (`a18778b`, pushed). Suite 138→140 both modes. Two benchmark features (F2 `<-`, `limit`) fully scoped + deferred.

**SCRIP HEAD: `a18778b`** (pushed to origin/main). Base was `e0fc8e4` (already ahead of the prior handoff's `c8838f8`; rebased clean). **m3/m4 = 140/283**, FAIL 18, XFAIL 36, EXCISED 89. All FACT gates green (no-stack 0, one-reg-frame 0, g_vstack 0, bb_bin_t 0, medium-invisible 0 strict). icon smoke 12/12 m3+m4, prolog 5/5 m3+m4.

**.github:** this handoff + GOAL-ICON-FULL-PASS.md (Status line + watermark + tractable-ladder rung34 marked DONE). PLAN/tracker untouched.

---

## WHAT LANDED — BENCH-F1.5 flat-chain UNOP-assign value-flow

Implements the prior handoff's recommended NEXT STEP. **`x := \expr` / `x := /expr`** (and any local `x := <unop>`) now emit natively in m3+m4.

**Two-line fix:**
1. `src/driver/scrip.c` `rhs_kind_ok` — admit `IR_UNOP` (sub-ops `TT_MNS/PLS/SIZE/NONNULL/NULL/NOT`) and the dedicated unop kinds (`IR_NEG/POS/SIZE/NONNULL/NULL_TEST/NOT`) as a local-assign RHS.
2. `src/emitter/emit_bb.c` `codegen_flat_chain_body` — after the BFS that builds `nodes[]`, **pre-register a varslot for every locally-assigned var** (`IR_ASSIGN`/typed variants, non-global sval) BEFORE the per-node walk loop.

**Root cause (verified, not guessed).** I instrumented `bb_varslot`/`bb_varslot_peek` with register/peek probes and diffed the working `x := 1+2` against the bombing `x := \(1+2)`:
- BINOP rhs: `REGISTER x→48` *then* `peek x→48 HIT` (assign walked before the var-read). Works.
- UNOP rhs: `peek x→-1 MISS` *then* `REGISTER x→64` (var-read walked before the assign). → `bb_var` BOMB.

The BFS emission walk in `codegen_flat_chain_body` enqueues binop/call **ω (failure) edges**. The chain is `LIT1→LIT2→BINOP→UNOP→ASSIGN→VAR(read)→WRITE`. The BINOP's ω-edge points at the var-read (node 3) — which is *also* the ASSIGN's γ-successor. With the UNOP inserted, the BINOP's γ is the UNOP (one extra hop to the ASSIGN), so the var-read gets dequeued *before* the ASSIGN; dedup keeps that earlier (failure-path) slot. So `write(x)` peeked x's varslot before the ASSIGN registered it. Pre-registering all assigned locals (identical pattern to param pre-registration in `descr_flat_chain_build_proc`) makes the read resolve regardless of BFS order. The UNOP itself was never the problem — it already slots correctly (`op_off = bb_slot_alloc16(nd)` in the `IR_UNOP` dispatch arm @emit_bb.c:3219) and `bb_prepare` already sets the assign's `op_a_slot = bb_slot_get(operands[0])`.

**Verified (both modes):** all 5 `rung34_null_test_*` PASS (2 targeted moved EXCISED→PASS: `nonnull_succeeds` `x:=\(1+2)→3`, `null_succeeds` `x:=/(1>2)→ok`). Suite 138→140, FAIL unchanged 18 (same names), EXCISED 91→89, ZERO EXCISE→FAIL (explicit FAIL-name + EXCISED-name diffs both modes). All FACT gates 0, prolog 5/5, icon 12/12.

**Note for whoever extends this:** the handoff's correction #2 trap ("admitting the gate turns the clean EXCISE into a `bb_var` BOMB") is now RESOLVED at the root — the pre-registration fix means you can admit further RHS shapes without re-hitting it, as long as the assigned var is a real `IR_ASSIGN` in the chain. Correction #3 (`/(1>2)` needs relop-operand acceptance) turned out to be a non-issue: the relop operand is walked as a normal chain node and slots fine; `/(1>2)` passes as-is.

---

## NEXT — two benchmark features fully scoped this session (both DEFERRED: each is a full session)

I scoped both queens-critical features end-to-end but did not start them, to avoid leaving broken state near my budget. Both are ready to execute.

### BENCH-F2 — reversible assign `<-` (THE queens keystone; both queens + genqueen lean on it)
- **Parser ✅** — `<-` → `TT_REVASSIGN (TT_VAR x) (expr)`, confirmed via `./scrip --dump-ast`. `TT_REVASSIGN`/`TT_REVSWAP` exist in `ast.h`.
- **Lowerer ✗** — NO `case TT_REVASSIGN` arm; the node is silently dropped (vanishes from `--dump-ir`). Add the arm in `src/lower/lower_icon.c`, model on `case TT_SWAP` @L258 (which builds `IR_SWAP`).
- **IR kind ✗** — add `IR_RASGN` (sibling `IR_SWAP` @IR.h:159). (Add `IR_REVSWAP` for `<->` too if doing both.)
- **Template ✗** — new `bb_rasgn.cpp`, model on `bb_swap.cpp` (already a working reversible-ish two-var box). Shape: **α** = save x's old DESCR to a per-box `[ζ+off]` save slot, `GeneralAsgn(x, v)`, jmp γ; **β** = restore x from save slot, jmp ω(fail). NO value stack — the save slot is `[ζ+off]` per PER-BOX LOCAL STORAGE.
- **Canonical:** `refs/icon-master/src/runtime/oasgn.r` rasgn `operator{0,1+}`: `GeneralAsgn(x,y); suspend x; [resume] GeneralAsgn(x, saved_x); fail`. JCON `refs/jcon-master/tran/irgen.icn:472` `ir_a_Binop` op `"<-"`; `ir_rval` returns `&null` for arg 1 (the lvalue is NOT rval'd).
- **Plumbing:** flat-drive (save-slot alloc + port wiring), `emit_core.c` dispatch case, Makefile `RT_PIC_SRCS`, `descr_chain_arity` entry, gate admission in `scrip.c`.
- **Composition (do AFTER plain-var case):** queens `rows[r] <- up[n+r-c] <- down[r+c-1] <- 1` — chained `<-` on **subscript lvalues** → the store/restore must generalize from a varslot to an `IR_IDX_SET`-style element store (reuse `subscript_set`, already in `pattern_match.c`; F1's `bb_idx_set` is the store half). genqueen chains `<-` with `/`: `/rw[r] <- /dd[r+c-1] <- /ud[n+r-c] <- c`.

### `limit` `\` (rung14, 3 FAIL rc=124) — generator-control, benchmark-relevant
`src/emitter/emit_bb.c` `flat_drive_limit` @L1915 is **structurally incomplete**: pure port-wiring (walk + jmp), NO counter, NO result slot. `(1 to 10)\3` → blank lines + hang (unbounded generation; value never reaches `write`). FIX:
- **New `bb_limit.cpp` template** — the counter compare/increment/gate BYTES must live in a template (TEMPLATE-ONLY EMISSION), NOT inline in `flat_drive_limit`.
- **(1) value pass-through:** alias the LIMIT node's result slot to its generator's slot — `bb_slot_register(pBB, bb_slot_get(operands[0]))` after walking the generator — so the consumer reads the gen's current value (Proebsting pass-through).
- **(2) counter:** canonical `ir_a_Limitation` (jcon `irgen.icn:113`): `t := #limit; c := 1; goto expr.start`; expr.success → emit; resume → `if (t > c) { c++; goto expr.resume } else fail`.
- **Edge case `\0`** (rung14_limit_limit_zero expects ZERO emissions, then `done`): must gate the FIRST emission (`c <= t` before initial expr.start, since t=0 → nothing). IR: `IR_LIMIT [gen, count, one]` (operands[2] is the spare LIT for `+1`).
- Baseline `every write(1 to 3)` value-flow WORKS (TO gen→write confirmed), so only LIMIT's pass-through + counter are missing.

---

## CANONICAL ANCHORS (verified this session)
- `refs/icon-master/src/runtime/ovalue.r` — `\` nonnull (operator{0,1}, fail-if-null), `/` null (operator{0,1}, return-if-null). Both two-port, no save slot. [F1.5 — DONE]
- `refs/icon-master/src/runtime/oasgn.r` — `<-` rasgn @142 `operator{0,1+}`, `<->` rswap @168, `:=:` swap @267. [F2 keystone]
- `refs/jcon-master/tran/irgen.icn` — `ir_a_Limitation` @113 (counter t>c gate), `ir_a_Binop` @472 (`<-` via op), `ir_rval` (&null for assign/`<-` arg 1), `ir_a_Every` @309, `ir_a_Suspend` @937.

## REUSABLE INTEL
- BFS emission order in `codegen_flat_chain_body` enqueues binop/call **ω-edges** → a γ-successor read can be emitted before its producer assign. Pre-register assigned-local varslots before the walk (now done) to decouple read-resolution from walk order.
- `descr_chain_operand_refs` (RPN reconstruction over the γ/ω-walked chain) correctly sets `n_operands` for UNOP/BINOP/ASSIGN — operand reconstruction was NOT the bug.
- The real native gate is `icn_graph_native_emittable_mode` (scrip.c, permissive-by-default); reject a kind there to EXCISE; `rhs_kind_ok`/`local_assign_rhs_ok_g` gate local-assign RHS shapes (RHS = `operands[0]`, or the γ-predecessor fallback loop).
- m3 binary tolerates dup labels (last-wins); m4 `as` rejects them — always assemble the m4 `.s` standalone when a kind passes m3 but not m4.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
