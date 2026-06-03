# GOAL-ICN-GLOBAL-NV.md — Icon Globals via NV Dictionary

**Repos:** SCRIP + .github
**Branch:** main

## ▶ WATERMARK (2026-06-03, SCRIP HEAD `7fc5ae9`)

**GN-1 + GN-2 + GN-3 DONE.** Icon global variable *references* now (a) tag as `IR_VAR state=1` at lower time (GN-2, grounded in JCON `irgen.icn ir_a_Ident`: a bare `ir_Var` carries the name; global/local is a late binding against `ir_Global`'s nameList) and (b) route to the new stackless `bb_var_global` NV_GET_fn read template in the native emitter (GN-3). `icn_is_global` (GN-1) wraps the already-populated `is_global()`/`global_names[]` table (filled by `global_register` in `polyglot_init` before `lower` runs). All three steps verified zero-behavior-change against the m2 oracle (interp `IR_VAR` case never reads `state`).

**The read path is written and wired but DORMANT.** A global-touching Icon graph cleanly EXCISES `[SMX]` (rc=0) in `--run`/`--compile` — `icn_graph_native_emittable` declines any graph with an `IR_VAR state==1` or an `IR_ASSIGN` to a global. This replaced a hard ABORT (rc=134): `bb_var` used to bomb on the global read and `IR_ASSIGN`-to-global was a `kind=5` unhandled tree node. The EXCISE is the honest boundary until **GN-4** lands the `NV_SET_fn` assign path; only then do global programs run native (GN-5 probe, GN-6 sweep).

**NEXT = GN-4** — `IR_ASSIGN` with a global lhs → `flat_drive_icn_global_assign` emitting `call NV_SET_fn(name, value)` (value already in a frame slot/reg). The `bb_var_global` read template is the consumer that will read it back. Once the assign lands, REMOVE the `IR_ASSIGN`-to-global (and, once the full chain threads, the `IR_VAR state==1`) decline from `icn_graph_native_emittable` to light the family up, then GN-5 cross-language probe + GN-6 corpus sweep (floor **m2 ≥ 130**) + GN-FENCE structural grep. Study `ir_a_Assign` in `refs/jcon-master/tran/irgen.icn` FIRST per CONSULT-CANONICAL-SOURCES.

**Gates (all green at `7fc5ae9`):** m2 corpus 130 PASS (HARD) · Icon smoke m2 12/12 (HARD) · m3/m4 5/12 (unchanged) · prove_lower2 67 PASS · bb_bin_t=0 · g_vstack=0 · no-handencoded `--strict` clean · no-stack 10≤127 · one-reg-frame 0≤21 · FACT bytes-outside-templates=0 · `bb_var_global` medium-invisible clean. Survived rebases onto peer Raku-NFA + Prolog PL-HY-FENCE + RS-2 runtime-reorg commits (all orthogonal).

---

## Objective

Icon currently gives every procedure-level global variable a frame slot (`g_bb_varslot` / `bb_varslot_peek`), addressed as `[reg+off]` in the one-register frame. This is a local optimization inherited from the Icon compiler's integer-index model.

The correct model — and the one that enables cross-language variable sharing — is: **Icon global variables live in the shared NV dictionary (`NV_GET_fn` / `NV_SET_fn`), exactly like SNOBOL4/Snocone/Rebus globals.** Locals (procedure-scoped, stack-saved/restored) remain frame slots or the shadow mechanism. Globals become name-keyed NV lookups, making the Icon global namespace directly visible to and from all other languages with zero extra machinery.

**What changes at emit time:** When an `IR_VAR` node carries the name of a program-level global (declared via `global` in the Icon source), the emitter produces a call to `NV_GET_fn` / `NV_SET_fn` instead of a `[reg+off]` frame slot access. The `bb_var` template gains a new arm — or a new sibling template `bb_var_global` — for this path. The `g_descr_flat_chain` / `g_bb_varslot` slot mechanism continues to serve Icon locals (procedure parameters + `local` declarations).

**What does NOT change:** The one-register frame model (RULES.md). Locals keep their frame slots. The `g_descr_flat_chain` path is unchanged for locals. Only the global arm of `IR_VAR` is rerouted to NV.

## ⛔ DUAL-MODE DIRECTIVE — KEEP THE OLD FRAME-SLOT WAY AND THE NEW NV-DICTIONARY WAY SIDE BY SIDE, CLI-SELECTED (Lon, 2026-06-03)

**Do NOT delete the OLD frame-slot global path when the NEW shared-dictionary path lands. KEEP BOTH, selected by a command-line switch.** The OLD path (`g_bb_varslot` / `bb_varslot_peek`, `[r12+off]`) already exists and is proven; the NEW path (`NV_GET_fn`/`NV_SET_fn`, the shared hash dictionary) is being added at the SAME call sites (`IR_VAR` read → `bb_var`/`bb_var_global`; `IR_ASSIGN` write → `flat_drive_assign`/`flat_drive_icn_global_assign`), so making it switch-selectable is a cheap refactor, not a rewrite. Rationale, two parts:

1. **PERFORMANCE MEASUREMENT.** We want the head-to-head cost of frame-slot globals vs NV-dictionary globals — a `[r12+off]` load/store vs a `_var_hash(name)` lookup + bucket-chain walk. The switch lets the SAME Icon corpus run BOTH ways for a clean A/B benchmark (record numbers in `BENCHMARKS.md` / `bench/`).

2. **INDEPENDENT-ICON COMPILATION.** When Icon is compiled standalone (no polyglot mix needing cross-language sharing), the OLD frame-slot model stays available as the faster self-contained option; the NEW shared-dictionary model is for the cross-language case (Icon globals sharing the ONE namespace with SNOBOL4/Snocone/Rebus, EXACTLY the same dictionary). **End state = BOTH backends retained, switch-selected — not OLD-deleted-for-NEW.**

**Switch shape (to be finalized in GN-3.5/GN-4):** a driver flag (e.g. `--icn-globals=slot|nv`, default TBD by Lon) that sets a global mode read by the `IR_VAR`/`IR_ASSIGN` dispatch arms; `slot` = OLD (`bb_varslot`), `nv` = NEW (`bb_var_global` + `NV_SET_fn`). The GN-2 `state=1` tag identifies which `IR_VAR`/`IR_ASSIGN` nodes are global *candidates*; the switch then chooses the backend for those nodes. Mode-2 already resolves globals through the dictionary regardless of the switch (see Objective note + ARCH-ICON.md "Variable model"); the switch is a mode-3/4 native-codegen distinction. **This dual-mode requirement REVISES GN-FENCE** (the "zero frame-slot for globals" grep is conditional on `nv` mode, not unconditional) — see GN-FENCE below.

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

- [x] **GN-3 — New `bb_var_global` template: NV_GET_fn call. DONE (SCRIP `7fc5ae9`), DORMANT pending GN-4.**
  `src/emitter/BB_templates/bb_var_global.cpp` written: seals the name string RO, loads its `char*` into `rdi` via `[rip+disp]` (`x86_ro_load_q` after `x86_ro_seal_str`), `call NV_GET_fn`, stores the returned `DESCR_t` `rax:rdx` into the box's own 16-byte frame slot `[r12+off]`/`[r12+off+8]`, then `jmp γ / def β / jmp ω`. Non-generator: succeeds once on α, fails on β (NV_GET_fn never fails — unset → NULVCL, confirmed core.c:2337). Pure `x86()` concatenation mirroring `bb_lit_scalar.cpp` + `bb_to.cpp` — FACT-clean (no raw-byte producers, no `MEDIUM_BINARY` branch, no `bb_bin_t`; absent from the medium-invisible REMAINING list). `NV_GET_fn`/`NV_SET_fn` confirmed exported (T) from `libscrip_rt.so` so mode-4 links `@PLT`. **Wiring:** `bb_templates.h` declares it; `emit_core.c` IR_VAR dispatch routes `nd->state==1 → bb_var_global` else `bb_var`; `emit_bb.c` IR_VAR flat arm allocates `op_off` (own 16-byte slot) for the global case (local keeps `bb_varslot_peek`); Makefile adds it to `RT_PIC_SRCS` + its own compile rule. **CLEAN EXCISE (honest GN-3 boundary):** a global-touching program previously ABORTED native (rc=134 — `bb_var` bombed on the global read, `IR_ASSIGN`-to-global was a `kind=5` unhandled tree node). Per "a missing box falls clean-LOUD, never silent," `icn_graph_native_emittable` (scrip.c) now declines (clean `[SMX]`, rc=0) any graph with an `IR_VAR state==1` OR an `IR_ASSIGN` to a global name. So the read template is written + wired but DORMANT until **GN-4** lands the `NV_SET_fn` assign path — exactly the staged pattern `bb_to` followed before ICN-HY-4. Verified `G:=10;write(G)` now prints `[SMX]` in `--run` and `--compile` instead of aborting. Gate: build rc=0; m2 corpus 130 PASS (HARD, unchanged); smoke m2 12/12; all FACT/structural gates green. **(The goal's per-kind `NEW=0 GONE=0` gate needs a full build with the audit tool linked — unavailable in this env, GONE=1115.)**

- [ ] **GN-4 — Wire assign path: `IR_ASSIGN` with global lhs uses `NV_SET_fn` (NEW path, under the switch — KEEP the OLD slot assign). Gate: build + m2 smoke ≥ pre-rung baseline.**
  The `IR_ASSIGN` emitter path (`emit_bb.c:1659`) currently routes through `flat_drive_gvar_assign` (SNO) or `flat_drive_assign` (ICN). For Icon globals (the assign is to a global name — `nd->sval && is_global(nd->sval)`, or `nd->α->t == IR_VAR && nd->α->state == 1`), add a new `flat_drive_icn_global_assign` that emits `call NV_SET_fn(name, value)` (value = rhs result already in a frame slot/reg). **Per the DUAL-MODE DIRECTIVE: this is the NEW arm, reached only when the global-mode switch is `nv`; the OLD frame-slot assign arm (`flat_drive_assign` + `bb_varslot`) STAYS in place and is reached when the switch is `slot`. Do NOT delete the slot assign.** This is also where the global-mode CLI switch is finalized (see the DUAL-MODE DIRECTIVE in the Objective): a driver flag setting the mode the `IR_VAR`/`IR_ASSIGN` arms read. Once the NEW assign lands AND the chain threads, remove the `IR_ASSIGN`-to-global decline from `icn_graph_native_emittable` (then, when the read chain also threads, the `IR_VAR state==1` decline) so `nv`-mode programs run native (m2==m3==m4); the `slot` mode keeps the existing behavior. Study `ir_a_Assign` in `refs/jcon-master/tran/irgen.icn` FIRST per CONSULT-CANONICAL-SOURCES. Gate: m2 smoke ≥ baseline; a new Icon global-assign probe passes under `nv`; the OLD `slot` path still passes its existing tests.

- [ ] **GN-5 — Probe program: cross-language global read. Gate: probe passes m2.**
  Write `test/icn_global_nv_probe.icn` — a minimal Icon program that sets a global variable and reads it back through a SNOBOL4 statement (or vice versa) exercised via the mode-2 interp. Confirms the shared namespace is live. This is the proof-of-concept for the cross-language goal. Gate: probe passes `--interp`.

- [ ] **GN-6 — Sweep Icon corpus globals. Gate: m2 corpus ≥ pre-rung baseline; no regressions.**
  Run `test_icon_all_rungs.sh`. Every program that previously passed must still pass. Programs that use globals should now go through NV. Regressions indicate a global that was misclassified as local or vice versa — fix the `icn_is_global` set construction. Gate: m2 PASS ≥ pre-rung count.

- [ ] **GN-PERF — A/B benchmark OLD (slot) vs NEW (nv) globals. Gate: numbers recorded.**
  Per the DUAL-MODE DIRECTIVE rationale (1): run the SAME global-heavy Icon corpus under both `--icn-globals=slot` and `--icn-globals=nv` and record the wall-clock / instruction-count delta (frame-slot `[r12+off]` load/store vs `NV_GET_fn`/`NV_SET_fn` hash lookup + chain walk). Land the comparison in `BENCHMARKS.md` (and/or a `bench/` harness). This is the measurement that motivated keeping both paths; it informs the default switch value and whether standalone-Icon should default to `slot`.

- [ ] **GN-FENCE — In `nv` mode, zero frame-slot references for names in the global set (CONDITIONAL — both backends coexist). Gate: structural grep.**
  **REVISED per the DUAL-MODE DIRECTIVE: the fence is NOT unconditional.** With `--icn-globals=nv`, `grep` the emitted text (mode-4 `--compile` output) for the global variable names and confirm none appear as `[reg+off]` frame-relative addresses — all appear as `NV_GET_fn`/`NV_SET_fn` call sites (structural proof the NEW path is wired). With `--icn-globals=slot`, the OPPOSITE must hold — globals DO appear as `[reg+off]` and there are NO `NV_*` call sites for them (proof the OLD path is intact and was not deleted). The gate `scripts/test_gate_icn_global_nv.sh` (new this rung) runs BOTH modes and asserts each invariant for its mode; it exits 0 only when both the NEW and OLD backends are correctly switch-selected. (A unified `bb_var_global` for SNO+ICN globals with no language check is a possible LATER refinement of the `nv` arm only.)

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

`IR_VAR`/`IR_ASSIGN` dispatch at the IR level, with `state` identifying global *candidates* and the global-mode switch picking the backend (DUAL-MODE DIRECTIVE):

```
IR_VAR (state == 0)                      →  bb_var        (frame slot: local, param, static — ALWAYS)
IR_VAR (state == 1) + switch == slot     →  bb_var        (OLD: global as a frame slot [r12+off])
IR_VAR (state == 1) + switch == nv       →  bb_var_global (NEW: NV_GET_fn, shared namespace)
IR_ASSIGN to global + switch == slot     →  flat_drive_assign            (OLD: slot store)
IR_ASSIGN to global + switch == nv       →  flat_drive_icn_global_assign (NEW: NV_SET_fn)
```

The SNO/SCO/REB path already uses the NV dictionary for everything (via `g_gvar_flat_chain` and the by-name pass-through arm of `bb_var`). In `nv` mode Icon globals join that same dictionary — the SAME hash, the SAME namespace, cross-language visible. In `slot` mode Icon globals keep the OLD `g_bb_varslot` frame-slot model (faster, self-contained, no sharing). **Both backends are retained and switch-selected (Lon, 2026-06-03) — the OLD path is NOT deleted.** Locals are frame slots in BOTH modes. A future rung can unify the SNO and ICN `nv` global arms into a single `bb_var_global` template with no language check; that unification touches only the `nv` arm and leaves the `slot` arm intact. See `ARCH-ICON.md` → "Variable model — frame slots (OLD) and shared NV dictionary (NEW)" for the full architectural statement.
