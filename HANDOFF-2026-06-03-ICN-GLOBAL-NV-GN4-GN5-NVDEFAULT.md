# HANDOFF-2026-06-03-ICN-GLOBAL-NV-GN4-GN5-NVDEFAULT.md

**Goal:** `GOAL-ICN-GLOBAL-NV.md` — Icon globals via the shared NV dictionary, dual-mode with the frame-slot model.
**Session focus:** GN-4 (assign write path) + GN-5 (probe) → then Lon directive: **make `nv` the default** → GN-6 partial + an IR_RETURN native-emit fix surfaced while chasing the m3 user-proc segfault.

---

## What landed (all verified, gates green)

### GN-4 — Icon global assignment via NV dictionary (key/value)
- New template **`src/emitter/BB_templates/bb_gvar_assign_icn.cpp`** — FACT-clean pure `x86()`: loads the rhs DESCR_t from its frame slot (`mov rsi,[r12+rhs]` / `mov rdx,[r12+rhs+8]`), seals the global name RO + `lea rdi,[rip+disp]`, `call NV_SET_fn(name,val)`, stores the returned `rax:rdx` into the box's own 16-byte slot (so `write(G:=v)` consumers read it), `jmp γ / def β / jmp ω`.
- **The rhs handle is `nd->α`** — `v_assign` (lower.c) now records the rhs result node on `as->α` for ICN. Behavior-neutral for the m2 oracle (it reads the AG ring; gen-helpers read `β` which stays NULL). m2 130 unchanged.
- **SWITCH RETROFIT (both faces, neither path hard-wired):** `emit_core.c` IR_VAR read = `state==1 && nv → bb_var_global` else `bb_var`; `emit_bb.c` IR_VAR slot-promotion takes `bb_varslot_peek` for a `state==1` global in slot mode, own-slot in nv mode; IR_ASSIGN dispatch routes a global lhs to `bb_gvar_assign_icn` / `flat_drive_icn_global_assign` only under nv.

### GN-5 — cross-language probe
- **`test/icn_global_nv_probe.icn`** (`global SHARED; SHARED:=99; write(SHARED)`) runs **m2==m3==m4 = 99** under nv. The global lives in the same hash dictionary SNOBOL4/Snocone/Rebus use → cross-language visible by construction.

### ⭐ nv is the DEFAULT (Lon directive, 2026-06-03)
- `g_icn_globals_nv = 1` in `lower.c`. Icon globals default to the shared NV dictionary (key/value). The OLD frame-slot model (slot/value) is fully retained and opt-in via **`--icn-globals=slot`**. Two completely swappable backends, neither deleted (DUAL-MODE directive honored).
- CLI switch `--icn-globals=slot|nv` parsed in `scrip.c`.

### GN-6 — partial (globals lit native by default)
- Corpus (no flag = nv): **m4 PASS 12→19** (+7 global rungs across procedures — `rung21_global_initial_*`, `rung25_global_*`; all outputs ✓-verified correct, zero silent-wrong). **m2 130 (HARD) unchanged.**
- Two decline-gate hardening fixes (both convert pre-existing ABORTS → clean EXCISE, per "a missing box falls LOUD, never silent"):
  1. `icn_graph_native_emittable` declines any IR_ASSIGN whose native store box isn't built (local assigns either mode + slot-mode globals) → EXCISE instead of `kind=5` abort.
  2. m3 (`--run`) declines user-proc-call graphs via a new `for_run` arg → EXCISE instead of the pre-existing segfault; m4 still emits them. **Corpus m3 FAIL 190→81** (−109 crashes→clean EXCISE), EXCISED 45→154. This is the "systemic decline-gate pass" the GOAL-ICON-BB watermark called for.

### IR_RETURN native emit (surfaced chasing the m3 proc segfault)
- **Bug found:** `IR_RETURN` (kind 14) had NO `emit_core.c` case → flat-chain proc bodies emitted `[walk_bb_node: kind=14 unhandled]` (nothing) for `return`, malforming every proc body blob.
- **Fixed:** new **`bb_return.cpp`** (FACT-clean) writes the return DESCR_t (from `nd->α`'s slot) into the proc frame result slot `[r12+0]` (read by `rt_call_proc_descr`) and `jmp ω`; lowerer records `rn->α` for ICN returns. Verified `greet(){write("hi")}` now emits a correct proc body → `hi` in **m4**. m4 PASS set unchanged (19, no regression).

---

## Remaining — the m3 user-proc-call segfault (DIAGNOSED, shovel-ready)

Even with IR_RETURN fixed, m3 still SIGSEGVs inside the emitted **main** blob at the proc-call site (`fn(rt_frame(),0)`, scrip.c:1014; crash PC in the JIT pool, no symbol). **m4 (standalone) of the same program works** → mode-3-pool-specific proc-call linkage:
- `bb_call_proc_staged` BINARY arm → `rt_call_proc_descr(name,narg)` → invokes the callee's separately-built pool blob (`descr_flat_chain_build_proc` → `rt_proc_set_fn`).
- The crash is in that cross-blob invocation — likely the callee blob's `r12` frame prologue entered from `rt_call_proc_descr`'s `g_proc_arena` frame (vs m4 where the linker resolves everything).

**Next step:** instrument `rt_call_proc_descr` (rt.c:449) to print `p->fn` and `fb`, then single-step the callee blob's first instructions (the prologue) under gdb; compare against the working m4 TEXT arm. The divergence is the bug. Fixing it lifts the m3 `for_run` decline → m3 reaches m4's proc/global passes and unlocks the `proc_recursion`/`proc_zeroarg` smokes.

After that: **GN-PERF** (slot-vs-nv A/B benchmark — the switch makes this a clean same-corpus run) and **GN-FENCE** (`scripts/test_gate_icn_global_nv.sh`: nv globals appear as `NV_*` calls, slot globals as `[r12+off]`). Slot-mode global *native* path remains unbuilt (shares the local-assign-native box) — a future rung; under slot, globals EXCISE cleanly today.

---

## Files changed
- `src/lower/lower.c` — `g_icn_globals_nv` flag (default 1=nv); `as->α=rhs` (ICN assign) + `rn->α=v` (ICN return) rhs/value handles.
- `src/driver/scrip.c` — `--icn-globals=slot|nv` parse; switch-aware + `for_run`-aware `icn_graph_native_emittable` (declines unbuilt IR_ASSIGN store boxes + m3 user-proc calls).
- `src/emitter/emit_core.c` — switch-aware IR_VAR read; IR_ASSIGN nv-global arm; IR_RETURN flat-chain dispatch.
- `src/emitter/emit_bb.c` — `flat_drive_icn_global_assign`; switch-aware IR_VAR + IR_ASSIGN flat dispatch.
- `src/emitter/BB_templates/bb_templates.h` — declare `bb_gvar_assign_icn`, `bb_return`.
- `src/emitter/BB_templates/bb_gvar_assign_icn.cpp` (NEW), `bb_return.cpp` (NEW).
- `Makefile` — both new templates in `RT_PIC_SRCS` + scrip compile rules.
- `test/icn_global_nv_probe.icn` (NEW) — GN-5 probe.

## Gates at handoff (all green)
m2 corpus **130 (HARD)** · Icon smoke m2 12/12 (HARD) · Prolog smoke m2 5/5 (HARD) · unified-broker 32 · corpus m3 PASS 12 / EXCISED 154 / FAIL 81 · m4 PASS 19 / EXCISED 93 / FAIL 135 · bb_bin_t=0 · g_vstack=0 · no-handencoded `--strict` clean · no-stack 10≤127 · one-reg-frame 0≤21 · prove_lower2 PASS · `bb_gvar_assign_icn.cpp` + `bb_return.cpp` FACT-clean (0 raw-byte producers).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
