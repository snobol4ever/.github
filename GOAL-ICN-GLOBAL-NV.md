# GOAL-ICN-GLOBAL-NV.md — Icon Globals via NV Dictionary

**Repos:** SCRIP + .github
**Branch:** main

---

## Objective

Icon currently gives every procedure-level global variable a frame slot (`g_bb_varslot` / `bb_varslot_peek`), addressed as `[reg+off]` in the one-register frame. This is a local optimization inherited from the Icon compiler's integer-index model.

The correct model — and the one that enables cross-language variable sharing — is: **Icon global variables live in the shared NV dictionary (`NV_GET_fn` / `NV_SET_fn`), exactly like SNOBOL4/Snocone/Rebus globals.** Locals (procedure-scoped, stack-saved/restored) remain frame slots or the shadow mechanism. Globals become name-keyed NV lookups, making the Icon global namespace directly visible to and from all other languages with zero extra machinery.

**What changes at emit time:** When an `IR_VAR` node carries the name of a program-level global (declared via `global` in the Icon source), the emitter produces a call to `NV_GET_fn` / `NV_SET_fn` instead of a `[reg+off]` frame slot access. The `bb_var` template gains a new arm — or a new sibling template `bb_var_global` — for this path. The `g_descr_flat_chain` / `g_bb_varslot` slot mechanism continues to serve Icon locals (procedure parameters + `local` declarations).

**What does NOT change:** The one-register frame model (RULES.md). Locals keep their frame slots. The `g_descr_flat_chain` path is unchanged for locals. Only the global arm of `IR_VAR` is rerouted to NV.

---

## How the parser/lowerer already marks this

- `icon_parse.c:776` — `global X` declarations produce a `TT_GLOBAL` AST node.
- `icon_parse.c:678` — `local X` / `static X` declarations produce `TT_LOCAL` / `TT_STATIC_DECL`.
- `lower.c:914` — `TT_GLOBAL` / `TT_LOCAL` / `TT_STATIC_DECL` are already handled (emit `IR_SUCCEED` no-op — the declaration itself does nothing at runtime).
- `lower.c:174` — Every variable *reference* (TT_VAR / TT_NAME) emits `IR_VAR` with `sval = name`. The lowerer does NOT currently distinguish global-ref from local-ref at the IR level.

**The gap:** The lowerer knows which names are global (they appear under `TT_GLOBAL` nodes) but does not tag `IR_VAR` nodes to say "this name is a global." The emitter (`emit_bb.c:1596`) treats every `IR_VAR` identically — slot-lookup if `g_descr_flat_chain`, NV pass-through if `g_gvar_flat_chain` (the SNO path).

---

## Steps

- [x] **GN-1 — Collect global names at lower time. DONE (SCRIP `ed47496`).**
  The collection already happens: `polyglot_init` (polyglot.c:92-95) walks every `TT_GLOBAL` node and calls `global_register` (name_binding.c:13) into `global_names[]` BEFORE `lower` runs, and `is_global(name)` (name_binding.c:7) does the lookup. `lower.h` already includes `gen_runtime.h` which declares `is_global`. So GN-1 is one line: `static int icn_is_global(const char *name) { return name ? is_global(name) : 0; }` in lower.c (beside `icn_proc_is_generator`), giving GN-2 a named hook. The `prove_lower2.c` standalone harness (which links neither name_binding.o) gained a local `is_global` stub returning 0 — Figure-1 ASTs declare no globals — mirroring its existing standalone `g_stage2` definition. No IR changes, no emitter changes, no behavior change. Gate: `make -j4 scrip` rc=0; m2 corpus 130 PASS (unchanged); prove_lower2 67 PASS.

- [x] **GN-2 — Tag `IR_VAR` nodes for globals. DONE (SCRIP `ed47496`).**
  In `v_literal` (lower.c:184, after the leaf switch — ONE check, not duplicated across the `TT_VAR`/`TT_NAME` arms), when `cx.lang == IR_LANG_ICN && icn_is_global(n->sval)` is true, set `n->state = 1` (global; 0 = local, the default). The other `IR_VAR` sites (`pas_leaf_node`, Pascal for-loop) are `IR_LANG_PAS` and excluded by the lang guard. **Grounded in JCON `irgen.icn` `ir_a_Ident` (lines 1061-1079): a variable reference emits a bare `ir_Var(coord, target, p.id)` carrying the name symbolically — global/local is NOT decided at IR-gen, it is a late binding the linker resolves against `ir_Global`'s nameList (`ir.icn:6,15`). `state=1` is exactly the SCRIP encoding of that resolution, recorded on the node at lower time.** Verified zero-behavior-change against the m2 oracle: the interp `IR_VAR` case (IR_interp.c:1749-1768) never reads `state` — it recomputes from the frame slot (`frame_depth>0`+`scope_get`) or falls through to `NV_GET_fn` (the global path); and every consumer that re-dispatches an `IR_VAR` operand resets `operand->state=0` first (IR_interp.c:2206-2207, 2220, 2007). The emitter likewise ignores `state` on `IR_VAR`. `dump-bb` now annotates `IR_VAR` with ` scope=global` when `state==1` (debug formatter, scrip_ir.c:346; aids GN-FENCE). Probe `global G / local L; G:=10; L:=20` → dump shows `IR_VAR var="G" scope=global` and `IR_VAR var="L"` (no scope). Gate: m2 corpus 130 PASS (unchanged).

- [ ] **GN-3 — New `bb_var_global` template: NV_GET_fn call. Gate: build green; per-kind audit NEW=0 GONE=0.**
  Add `src/emitter/BB_templates/bb_var_global.cpp`. The template emits an x86 call to `NV_GET_fn(sval)` and jumps γ on success (always — NV_GET returns a DESCR_t, never fails; unset variables return SNUL). On β (resume) jumps ω. This is a non-generator: start → succeed immediately; resume → fail. Wire it into `emit_bb.c` dispatch: add `extern "C" void bb_var_global(IR_t*)` and call it from the `IR_VAR` case when `nd->state == 1`. Establish a per-kind baseline for `BB_VAR_GLOBAL` in `baselines/per_kind/`. Gate: `test_per_kind_diff.sh` PASS unchanged NEW=0 GONE=0 (new kind adds its own baseline cell, does not disturb existing ones).

- [ ] **GN-4 — Wire assign path: `IR_ASSIGN` with global lhs uses `NV_SET_fn`. Gate: build + m2 smoke ≥ pre-rung baseline.**
  The `IR_ASSIGN` emitter path (`emit_bb.c:1597`) currently routes through `flat_drive_gvar_assign` (SNO) or `flat_drive_assign` (ICN). For Icon globals (`nd->α->t == IR_VAR && nd->α->state == 1`), route to a new `flat_drive_icn_global_assign` that emits a call to `NV_SET_fn(name, value)`. The value is the rhs result already in a frame slot or register. Gate: m2 smoke ≥ baseline; a new Icon global-assign probe program passes.

- [ ] **GN-5 — Probe program: cross-language global read. Gate: probe passes m2.**
  Write `test/icn_global_nv_probe.icn` — a minimal Icon program that sets a global variable and reads it back through a SNOBOL4 statement (or vice versa) exercised via the mode-2 interp. Confirms the shared namespace is live. This is the proof-of-concept for the cross-language goal. Gate: probe passes `--interp`.

- [ ] **GN-6 — Sweep Icon corpus globals. Gate: m2 corpus ≥ pre-rung baseline; no regressions.**
  Run `test_icon_all_rungs.sh`. Every program that previously passed must still pass. Programs that use globals should now go through NV. Regressions indicate a global that was misclassified as local or vice versa — fix the `icn_is_global` set construction. Gate: m2 PASS ≥ pre-rung count.

- [ ] **GN-FENCE — Zero frame-slot references for names in the global set. Gate: structural grep.**
  `grep` in the emitted text (mode-4 `--compile` output) for the global variable names — confirm none appear as `[reg+off]` frame-relative addresses; all appear as `NV_GET_fn` / `NV_SET_fn` call sites. This is the structural proof the rung is complete. Gate: `scripts/test_gate_icn_global_nv.sh` (new script, created this rung) exits 0.

---

## Oracle

Pre-rung Icon baselines (2026-06-02, SCRIP HEAD `85677cb`):
- `test_smoke_icon.sh`: m2 0/12, m3 0/12, m4 0/12 (GZ-10 work in progress — smoke baseline is zero because the smoke suite uses programs beyond current GZ rung; this rung does NOT fix that)
- `test_icon_all_rungs.sh`: m2 127 PASS / 120 FAIL / 36 XFAIL (the meaningful gate for this rung)
- `test_per_kind_diff.sh`: PASS=504 FAIL=0 STUB=625 NEW=0 GONE=0

**Current state (2026-06-03, SCRIP HEAD `ed47496` — GN-1+GN-2 landed):** `test_icon_all_rungs.sh` m2 **130 PASS** / 117 FAIL / 36 XFAIL (the +3 vs the 127 baseline is from ICN-HY-3 bang + `to`/`to_by` native landing on the GOAL-ICON-BB main line between the baseline snapshot and this rung; not from GN work — GN-1/GN-2 are zero-behavior-change). **GN-6's floor is therefore m2 ≥ 130** (must not regress below the live count, not the stale 127). `test_per_kind_diff.sh` reports GONE=1115 in THIS environment because the per-kind audit tool is unlinked here (environment limitation per the design handoff, NOT a regression) — GN-3's `NEW=0 GONE=0` per-kind gate must be run from a full build with the audit tool linked.

This rung's gate is **m2 corpus does not regress below 130 PASS** and **GN-FENCE exits 0**.

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && make -j4 scrip > /tmp/build_full.log 2>&1
[ -x /home/claude/SCRIP/scrip ] || { grep -E "error:|fatal error" /tmp/build_full.log | head -5; exit 1; }
for r in /home/claude/SCRIP /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done
bash /home/claude/SCRIP/scripts/test_per_kind_diff.sh
bash /home/claude/SCRIP/scripts/test_icon_all_rungs.sh 2>/dev/null | tail -3
```

---

## Architecture Note

After this rung, `bb_var` splits cleanly into two cases at the IR level:

```
IR_VAR (nd->state == 0)  →  bb_var        (frame slot: local, param, static)
IR_VAR (nd->state == 1)  →  bb_var_global (NV_GET_fn: global, shared namespace)
```

The SNO/SCO/REB path already uses the NV dictionary for everything (via `g_gvar_flat_chain` and the by-name pass-through arm of `bb_var`). After this rung, Icon globals join that same path. The `g_bb_varslot` table continues to exist for locals only. A future rung can unify the SNO and ICN global arms into a single `bb_var_global` template with no language check.
