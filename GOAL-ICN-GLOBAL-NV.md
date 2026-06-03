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

- [ ] **GN-1 — Collect global names at lower time. Gate: build green.**
  The lowerer walks `TT_GLOBAL` nodes before lowering procedure bodies and records each declared global name into a per-graph set. Add `int icn_is_global(const char *name)` (checked against that set) to the lower context. No IR changes. No emitter changes. No behavior change — pure bookkeeping. Gate: `make -j4 scrip` rc=0; Icon smoke m2 baseline unchanged.

- [ ] **GN-2 — Tag `IR_VAR` nodes for globals. Gate: build + m2 smoke unchanged.**
  In `lower.c:174` (the `TT_VAR` / `TT_NAME` → `IR_VAR` path), when `cx.lang == IR_LANG_ICN` and `icn_is_global(sval)` is true, set a flag on the IR node (use `nd->state = 1` — "global"; `state = 0` = local, the default). No emitter changes yet — the `state` field is ignored by the emitter. Gate: m2 smoke baseline unchanged.

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

This rung's gate is **m2 corpus does not regress below 127 PASS** and **GN-FENCE exits 0**.

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
