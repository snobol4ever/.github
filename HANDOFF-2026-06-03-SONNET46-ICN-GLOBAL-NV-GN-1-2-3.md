# HANDOFF-2026-06-03-SONNET46-ICN-GLOBAL-NV-GN-1-2-3.md

## Session summary

GOAL-ICN-GLOBAL-NV ladder, steps **GN-1, GN-2, GN-3** landed (the design handoff
`HANDOFF-2026-06-03-SONNET46-ICN-GLOBAL-NV-DESIGN.md` opened this goal; this session
implemented the first three rungs). All three are zero-behavior-change against the
mode-2 oracle; GN-3's native read template is written + wired but DORMANT pending GN-4.

| Repo | HEAD pushed |
|------|-------------|
| SCRIP | `7fc5ae9` |
| .github | (this commit) |

---

## What landed

### GN-1 — `icn_is_global()` hook (lower.c)
The global-name collection already existed end-to-end: `polyglot_init`
(polyglot.c:92-95) walks every `TT_GLOBAL` node and calls `global_register`
(name_binding.c:13) into `global_names[]` BEFORE `lower` runs; `is_global(name)`
(name_binding.c:7) does the lookup; `lower.h` already includes `gen_runtime.h`
which declares `is_global`. So GN-1 = one static wrapper beside
`icn_proc_is_generator`:
```c
static int icn_is_global(const char * name) { return name ? is_global(name) : 0; }
```
The standalone `prove_lower2.c` topology harness links neither `name_binding.o`,
so it got a local `is_global` stub returning 0 (Figure-1 ASTs declare no globals),
mirroring its existing standalone `g_stage2` definition.

### GN-2 — tag `IR_VAR` globals (lower.c `v_literal`)
One check after the leaf switch (NOT duplicated across the `TT_VAR`/`TT_NAME` arms):
```c
if (n && n->t == IR_VAR && cx.lang == IR_LANG_ICN && icn_is_global(n->sval)) n->state = 1;
```
Grounded in JCON `irgen.icn` `ir_a_Ident` (lines 1061-1079): a variable reference
emits a bare `ir_Var(coord, target, p.id)` carrying the name symbolically —
global/local is NOT decided at IR-gen, it is a late binding the linker resolves
against `ir_Global`'s nameList (`ir.icn:6,15`). `state=1` is the SCRIP encoding of
that resolution recorded on the node. The other `IR_VAR` sites (`pas_leaf_node`,
Pascal for-loop) are `IR_LANG_PAS` and excluded by the lang guard.

**Zero-behavior-change proof (the m2 HARD gate):** the interp `IR_VAR` case
(IR_interp.c:1749-1768) never reads `state` — it recomputes from the frame slot
(`frame_depth>0` + `scope_get`) or falls through to `NV_GET_fn` (the global path);
every consumer that re-dispatches an `IR_VAR` operand resets `operand->state=0`
first (IR_interp.c:2206-2207, 2220, 2007). The emitter likewise ignored `state` on
`IR_VAR`. `dump-bb` now annotates `IR_VAR` with ` scope=global` when `state==1`
(debug formatter, scrip_ir.c:346; aids GN-FENCE). Probe `global G / local L;
G:=10; L:=20` → `IR_VAR var="G" scope=global` and `IR_VAR var="L"` (no scope).

### GN-3 — `bb_var_global` NV_GET_fn read template + clean EXCISE
`src/emitter/BB_templates/bb_var_global.cpp` (new): seals the name string RO, loads
its `char*` into `rdi` via `[rip+disp]` (`x86_ro_load_q` after `x86_ro_seal_str`),
`call NV_GET_fn`, stores the returned `DESCR_t` `rax:rdx` into the box's own 16-byte
frame slot `[r12+off]`/`[r12+off+8]`, then `jmp γ / def β / jmp ω`. Non-generator
(succeeds once on α, fails on β — NV_GET_fn never fails, unset→NULVCL, core.c:2337).
Pure `x86()` concatenation mirroring `bb_lit_scalar.cpp` + `bb_to.cpp`; FACT-clean
(no raw-byte producers, no `MEDIUM_BINARY` branch, no `bb_bin_t`; absent from the
medium-invisible REMAINING list). `NV_GET_fn`/`NV_SET_fn` confirmed exported (T) from
`libscrip_rt.so`.

Wiring: `bb_templates.h` declares it; `emit_core.c` IR_VAR dispatch routes
`nd->state==1 → bb_var_global` else `bb_var`; `emit_bb.c` IR_VAR flat arm allocates
`op_off` (own 16-byte slot) for the global case (local keeps `bb_varslot_peek`);
Makefile adds it to `RT_PIC_SRCS` + its own compile rule (globbed into `scrip` via
`OBJ/*.o`).

**The clean-EXCISE is the honest GN-3 boundary.** Before this session a
global-touching program ABORTED native (rc=134): `bb_var` bombed on the global read
(globals have no frame slot) and `IR_ASSIGN`-to-global was a `kind=5` unhandled
tree-path node. Per the FACT rule "a missing box falls clean-LOUD, never silent,"
`icn_graph_native_emittable` (scrip.c) now declines (clean `[SMX]`, rc=0) any graph
containing an `IR_VAR state==1` OR an `IR_ASSIGN` to a global name. So the read
template is written + wired but DORMANT until GN-4 lands the assign path — the same
staged pattern `bb_to` followed before ICN-HY-4. Verified `G:=10;write(G)` now prints
`[SMX]` in `--run` and `--compile` instead of aborting.

---

## Baselines / gates (SCRIP HEAD `7fc5ae9`, all green)

- Build: `make -j4 scrip` rc=0; `make libscrip_rt` rc=0
- `test_icon_all_rungs.sh`: **m2 PASS=130** FAIL=117 XFAIL=36 (HARD — unchanged across all three rungs; the +3 vs the design handoff's 127 came from ICN-HY-3 bang + `to`/`to_by` native on the GOAL-ICON-BB main line, NOT from GN work)
- `test_smoke_icon.sh`: m2 12/12 (HARD), m3 5/12, m4 5/12 (unchanged)
- `prove_lower2.sh`: 67 PASS
- `test_gate_no_bb_bin_t.sh`: bb_bin_t=0
- `g_vstack`: 0
- `test_gate_no_handencoded_bytes.sh --strict`: clean
- `test_gate_icn_no_stack.sh`: 10 ≤ 127
- `test_gate_icn_one_reg_frame.sh`: 0 ≤ 21
- FACT bytes-outside-templates: 0
- `bb_var_global` medium-invisible: clean (absent from REMAINING)
- `test_per_kind_diff.sh`: GONE=1115 — the per-kind audit tool is UNLINKED in this
  environment (limitation, not a regression). GN-3's `NEW=0 GONE=0` per-kind gate must
  be run from a full build with the audit tool linked.

---

## Next session entry point — GN-4

Read `GOAL-ICN-GLOBAL-NV.md` (watermark at top is the single source of truth). Run
Session Setup (incl. `make libscrip_rt`). Start at **GN-4**: `IR_ASSIGN` with a
global lhs → a new `flat_drive_icn_global_assign` emitting `call NV_SET_fn(name,
value)` (the value is the rhs result already in a frame slot/reg). The `bb_var_global`
read template (this session) is the consumer that reads the value back. Study
`ir_a_Assign` in `refs/jcon-master/tran/irgen.icn` FIRST per CONSULT-CANONICAL-SOURCES
(the `ir_Var` lhs + `ir_Asgn`/`ir_Deref` topology). The `IR_ASSIGN` native arm is
emit_bb.c:1659 (currently `flat_drive_assign`/`flat_drive_gvar_assign`); the global
case is `nd->sval && is_global(nd->sval)` (or tag the assign node in the lowerer for
symmetry with GN-2's read tag). Once the assign lands and the full chain threads,
REMOVE the `IR_ASSIGN`-to-global decline (then the `IR_VAR state==1` decline) from
`icn_graph_native_emittable` to light the family up; verify `G:=10;write(G)` now runs
`1 2 3`-style native (m2==m3==m4). Then GN-5 cross-language probe (Icon sets / SNOBOL4
reads via the shared NV namespace), GN-6 corpus sweep (floor **m2 ≥ 130**),
GN-FENCE structural grep (no global name appears as `[reg+off]`; all as
`NV_GET_fn`/`NV_SET_fn`).

### refs note
`refs/jcon-master/` and `refs/icon-master/` were extracted from the uploaded zips into
SCRIP/refs/ this session (gitignored — local-only). If absent next session, restore
per RULES.md: `git clone https://github.com/proebsting/jcon refs/jcon-master` and
`git clone https://github.com/gtownsend/icon refs/icon-master`.
