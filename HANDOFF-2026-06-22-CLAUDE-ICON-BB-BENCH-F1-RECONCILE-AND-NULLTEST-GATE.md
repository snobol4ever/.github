# HANDOFF — GOAL-ICON-FULL-PASS (Claude Opus 4.8)
## BENCH-F1(b) reconciled (landed upstream as `c8838f8`, independently re-derived) + three corrections to the F1 handoff. NO new commit from this session; tree left CLEAN at `c8838f8`.

**SCRIP HEAD (unchanged, shared): `c8838f8`** — "ICON-BB BENCH-F1(b): subscript-read value-flow — nested call-kind + global-var args". Working tree clean, matches `origin/main`. **m3/m4 = 138/283**, FAIL 18, XFAIL 36, EXCISED 91. All FACT gates green (no-stack 0, one-reg-frame 0, g_vstack 0, bb_bin_t 0, medium-invisible 0 strict).

**.github:** this handoff only. **GOAL watermark NOT bumped** (no landing this session — the +2 was an upstream commit, not mine). PLAN/tracker not edited.

---

## WHAT HAPPENED (concurrency note — the SHARED-EMITTER model worked)

I began on BENCH-F1(b) at clone-HEAD `04197ed`. I independently diagnosed the subscript-read value-flow bug and wrote the fix. Mid-session a `pull --rebase` pulled **`c8838f8` from origin — the identical fix, same commit title, same one-line change** — landed by a concurrent session. My duplicate commit was absorbed by the rebase (same diff → upstream won). Net: the fix is in, verified, mine dropped out cleanly. This is the convergent non-overlapping-work model behaving as designed.

I also found and **reverted a stray uncommitted `TEMP-PROBE-IDXSET-GATE-OFF` edit** in `src/driver/scrip.c` (it had replaced the `IR_IDX_SET → return 0` gate at line ~290 with a probe stub). The committed HEAD correctly retains the gate; only the working tree was dirty. Tree is now clean.

---

## BENCH-F1(b) — what the landed fix is (re-derived, fully understood)

**Symptom:** `write(L[i])` and even inline `list(3,7)[2]` produced NO output (m3 rc=0, empty). Subscript-READ value did not reach its consumer.

**Root cause (traced by m4 `.s` inspection + a marshal-entry `fprintf` probe):** A subscript read lowers to `IR_CALL sval="[]"` whose **arg0 is itself a call** (the `list(...)` constructor, or any nested builtin). `resolve_call_kinds_descr` (emit_bb.c) recursively retags every in-arg builtin call `IR_CALL`(9) → **`IR_CALL_BUILTIN`(200)**. But `marshal_call_arg` (bb_call.cpp:348) routed nested-call args to `marshal_single_call` only for raw `IR_CALL`/`IR_CALL_DEFINE` — **not `IR_CALL_BUILTIN`**. So the nested `list` call was never emitted as a producer; the marshaller fell through to a **phantom varslot** (`[r12+48]`, never written) → `subscript_get` read garbage → empty/fail.

**Fix (the landed one-liner):** add `|| ir_is_call_kind(lf->op)` to the bb_call.cpp:348 predicate, so any resolved call-kind arg (incl. `IR_CALL_BUILTIN`) goes to `marshal_single_call`. `ir_is_call_kind` is in IR.h:243 (covers BUILTIN/USERPROC/BYNAME/PROC_STAGED/GVAR_USERPROC); reachable in bb_call.cpp via bb_templates.h→IR.h.

**Verified (both modes):** `list(3,7)[2]`→7, global `L`-read→7, `reverse(trim(...))`, `abs(min(...))`, `dbl(abs(...))` (userproc←builtin) all correct. Suite: **136→138**, fixed `rung28_builtins_str_char_ord` + `rung36_jcon_trim`, ZERO regressions, ZERO EXCISE→FAIL, all FACT gates green. This is a GENERAL nested-builtin-call-arg fix, broader than lists.

---

## THREE CORRECTIONS to the BENCH-F1 handoff (these change the next move)

### 1. BENCH-F1's WRITE gate is a suite-level NO-OP — it is NOT the blocker.
The `04197ed` handoff said flipping `IR_IDX_SET → return 0` (scrip.c:290) is blocked by "LIT-operand slotting (m3) + global-list value flow." **Empirically false at `c8838f8`.** I probed with the gate OFF (`if (0 && nd->op == IR_IDX_SET)`, throwaway, reverted):
- **global** `L[2]:=9; write(L[2])` → prints **9**, ZERO abort. The write path is CORRECT.
- **local** `L[2]:=9; …` → cleanly EXCISES for an UNRELATED reason (`no MEDIUM_BINARY arm` on a local-var box, not `IR_IDX_SET`).
- **Full suite with gate OFF: 138, identical FAIL/EXCISED sets to gate-ON.** No near-passing benchmark is blocked *solely* on `IR_IDX_SET`.

**Implication:** Do NOT spend effort flipping the F1 write gate expecting +PASS. The LIT-operand slotting concern is moot for the global path (works) and the local path excises before reaching idx_set. Whatever value F1 has is masked behind other EXCISE reasons. Leave the gate as-is (harmless) until a benchmark is otherwise green and only idx_set remains.

### 2. The null-test operators `\` (nonnull) and `/` (null) need FLAT-CHAIN UNOP-ASSIGN VALUE-FLOW, not a gate predicate.
Canonical (`refs/icon-master/src/runtime/ovalue.r:8,31`): `\x` = fail-if-null-else-return-x; `/x` = return-x-if-null-else-fail. Both `operator{0,1}` (two-port, no save slot). **`bb_unop.cpp` ALREADY implements `UO_NONNULL` + `UO_NULL_TEST`** (dispatch at lines 28–29: TT_NONNULL=80→UO_NONNULL, TT_NULL=81→UO_NULL_TEST). The two benchmarks (`rung34_null_test_nonnull_succeeds` = `x:=\(1+2)`, `rung34_null_test_null_succeeds` = `x:=/(1>2)`) EXCISE because the gate's `local_assign_rhs_ok_g`/`rhs_kind_ok` (scrip.c:206,~185) does not admit an `IR_UNOP` RHS.

**TRAP (cost me a cycle, documented so you skip it):** Extending the gate to admit `x := <unop>` is easy BUT turns the clean EXCISE into a **`bb_var` BOMB** (`bb_var: unhandled arm (no flat-chain mode or missing slot)`). The flat-chain path does NOT slot the assigned var `x`, so the later `write(x)` read aborts. Per never-abort, I reverted. **The real prerequisite is flat-chain UNOP-assign value-flow: after `x := <unop>`, `x` must get a frame slot that a later read resolves** — same machinery the arithmetic/CASE/GEN_SCAN RHS arms already have, just not wired for UNOP.

Two more gotchas when you build it:
- In the GATE's `IR_graph_t` snapshot, a UNOP's operand is **NOT in `operands[]`** — it's linked by **γ-edge** (`p->γ.node == unop`); must scan `g->all[]` (the `local_assign_rhs_ok_g` fallback loop shows the idiom). NB the EMITTER's `bb_child0` *does* use `operands[]` — different graph snapshot, don't assume symmetry.
- `-(5)` is **constant-folded to `IR_LIT_I -5` at lower time** (never exercises the UNOP path) — useless as a UNOP test. Use `\(1+2)` shapes. Also: shell `\\` doubles into two stacked `IR_UNOP` nodes — write test `.icn` via heredoc, not `printf`.

Token values: TT_NONNULL=80, TT_NULL=81, TT_NOT=?(in ast.h), IR_UNOP=8, IR_BINOP=7, IR_ASSIGN=5, IR_CALL=9, IR_CALL_BUILTIN=200, IR_IDX_SET=129, IR_LIT_NUL=3.

### 3. `/(1>2)` additionally needs RELOP-operand acceptance.
`rhs_kind_ok` admits only arithmetic/concat BINOPs, not relops. `/(1>2)`'s operand is a relop (`1>2`) producing null-or-fail. So even after UNOP value-flow lands, the nonnull case (`\(1+2)`, arithmetic operand) will pass FIRST; the null case (`/(1>2)`, relop operand) needs the relop-as-slotted-operand path too.

---

## RECOMMENDED NEXT STEP (smallest clean +PASS)
Build **flat-chain UNOP-assign value-flow** (slot the assigned var after `x := <unop>` so a later read resolves), then admit `IR_UNOP` (template tokens NEG/POS/SIZE/NONNULL/NULL/NOT) as a local-assign RHS in `rhs_kind_ok`/`local_assign_rhs_ok_g`. Target: `rung34_null_test_nonnull_succeeds` as first +PASS, both modes. Self-contained; smaller than `<-` (BENCH-F2) or generator-in-relop pumping (BENCH-F3). Verify with the standard suite diff (guard EXCISE→FAIL and the `bb_var` BOMB), then the FACT gates.

## TRACTABLE EXCISED LADDER (smallest first, all confirmed EXCISING at `c8838f8`)
- `rung34_null_test_*` — `\`/`/` → **flat-chain UNOP value-flow** (above). FIRST.
- `rung13_alt_alt_nested` (`("a"|"b")||("x"|"y")`), `rung18_real_relop_real_relop_goal` (`3.0<(2.5|3.5|4.5)`) → alternation/relop with generator operand = **BENCH-F3** (bb_binop_gen β re-pump).
- `rung14_limit_limit_str` (`(…)\2`) → binary `\` limit operator.

## CANONICAL ANCHORS (verified this session)
- `refs/icon-master/src/runtime/ovalue.r` — `\` nonnull (8), `/` null (31), `.` value (53), `&` conj (65).
- `refs/icon-master/src/runtime/oasgn.r` — `<-` rasgn `operator{0,1+}` (142), `<->` rswap (168), `:=:` swap (267). [BENCH-F2 keystone, still EXCISED.]
- `refs/icon-master/src/runtime/oref.r:581` — `[]` subsc. `refs/jcon-master/tran/irgen.icn:461` — `<-` rval returns &null for arg 1.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.8
