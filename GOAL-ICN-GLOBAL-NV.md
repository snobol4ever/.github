# GOAL-ICN-GLOBAL-NV.md — Icon Globals via NV Dictionary

**Repos:** SCRIP + .github
**Branch:** main

## ▶ WATERMARK (2026-06-03, SCRIP HEAD `c66723e` — GN-4 + GN-5 + nv-DEFAULT + GN-6 partial + IR_RETURN native)

**⭐ `--icn-globals=nv` IS NOW THE DEFAULT (Lon directive, 2026-06-03).** `g_icn_globals_nv = 1` in `lower.c`. Icon globals default to the shared NV dictionary (key/value); the OLD frame-slot model (slot/value) is opt-in via `--icn-globals=slot`. Both backends remain — neither deleted, CLI-swappable — per the DUAL-MODE directive; Lon's call resolves the "default TBD" to `nv`.

**GN-4 + GN-5 DONE; GN-6 partial (globals lit native).** Icon global assignment has the NEW shared-NV backend (`bb_gvar_assign_icn.cpp` → `call NV_SET_fn(name, rhs)`, rhs DESCR_t from the `nd->α` rhs-handle `v_assign` records for ICN); combined with GN-3's `bb_var_global` read, global-touching Icon programs run **native by default**. **Corpus delta (no flag = nv): m4 PASS 12→19** (+7: `rung21_global_initial_*`, `rung25_global_*` — global vars across procedures, e.g. `rung25_global_global_three_procs`→`5`, all outputs ✓-verified correct, zero silent-wrong). **m2 130 (HARD) unchanged.** m3 PASS stays 12 (see user-proc note).

**Two hardening fixes (both convert pre-existing ABORTS → clean EXCISE, honoring "a missing box falls LOUD, never silent"):**
1. **`icn_graph_native_emittable` declines any IR_ASSIGN whose native store box is not built** — local assigns (either mode) + slot-mode global assigns now EXCISE cleanly instead of aborting `kind=5 unhandled` (was: `x:=42` and global+local-mixed programs aborted rc=134). Only the nv-mode global assign (`bb_gvar_assign_icn`, BUILT) is allowed through.
2. **m3 (`--run`) declines user-proc-call graphs** (`IR_CALL` dval==3 / registered proc) via a new `for_run` arg to the emittability gate — the in-process binary-pool user-proc path **segfaults pre-existing** (independent of globals: a plain `greet()` call crashes m3, works m4). They now EXCISE in m3 (rc=0) while m4 emits them correctly. **Corpus m3 FAIL 190→81** (−109 crashes→clean EXCISE), EXCISED 45→154. This is the "systemic decline-gate pass" the GOAL-ICON-BB watermark explicitly called for.

**FACT-clean.** `bb_gvar_assign_icn.cpp` is pure `x86()` (0 raw-byte producers, no `bb_bin_t`, no `IF(MEDIUM_BINARY)`). Gates green: m2 corpus **130 (HARD)** · Icon smoke m2 12/12 (HARD) · Prolog m2 5/5 · unified-broker 32 · bb_bin_t=0 · no-handencoded `--strict` clean · g_vstack=0 · no-stack 10≤127 · one-reg-frame 0≤21 · prove_lower2 PASS.

**NEXT — the m3 user-proc-call segfault is the highest-value fix** (it gates m3 globals + recursion + all proc programs). **DIAGNOSIS THIS SESSION (two bugs, one fixed):** (1) ✅ FIXED — `IR_RETURN` (kind 14) had NO `emit_core.c` case, so the flat-chain proc body emitted `[walk_bb_node: kind=14 unhandled]` (nothing) for `return`, making every proc body's blob malformed. Added `bb_return.cpp` (FACT-clean pure `x86()`): writes the return DESCR_t from its value-slot (`nd->α`, now recorded by `v_assign`-style lowering in the TT_RETURN arm) into the proc frame result slot `[r12+0]` (which `rt_call_proc_descr` reads via `*(DESCR_t*)(fb+0)`) and `jmp ω`. Verified: `greet(){write("hi")}` now emits a correct proc body and prints `hi` in **m4** (was malformed). (2) ⏳ REMAINING — even with the return fixed, m3 still SIGSEGVs inside the emitted MAIN blob at the proc-call site (`fn(rt_frame(),0)`, scrip.c:1014; crash PC in the JIT pool, no symbol). m4 (standalone) of the SAME proc program works, so this is **mode-3-pool-specific proc-call linkage** — the `bb_call_proc_staged` MEDIUM_BINARY arm calls `rt_call_proc_descr(name,narg)` which invokes the callee's separately-built pool blob (`descr_flat_chain_build_proc` → `rt_proc_set_fn`); the crash is in that cross-blob invocation (likely the callee blob's frame/`r12` prologue or an internal address not valid when entered from `rt_call_proc_descr`'s `g_proc_arena` frame, vs m4 where the linker resolves everything). **SHOVEL-READY NEXT STEP:** compare the m3 `bb_call_proc_staged` BINARY arm's arg-staging + `rt_call_proc_descr` path against the working m4 TEXT arm; instrument `rt_call_proc_descr` to print `p->fn` and `fb` then single-step the callee blob's first few instructions (the prologue) — the divergence from m4 is the bug. The m3 decline (`for_run` in `icn_graph_native_emittable`) stays until this lands, so proc programs EXCISE cleanly in m3 (rc=0). Fixing it lifts the decline → m3 reaches m4's proc/global passes + unlocks `proc_recursion`/`proc_zeroarg` smokes. Then **GN-PERF** (slot-vs-nv A/B) and **GN-FENCE** (`scripts/test_gate_icn_global_nv.sh`). Slot-mode global *native* path remains unbuilt (shares local-assign-native box) — future rung; under slot, globals EXCISE cleanly today.

---

## ▶ PRIOR WATERMARK (2026-06-03, SCRIP HEAD `7fc5ae9`)

**GN-1 + GN-2 + GN-3 DONE.** Icon global variable *references* now (a) tag as `IR_VAR state=1` at lower time (GN-2, grounded in JCON `irgen.icn ir_a_Ident`: a bare `ir_Var` carries the name; global/local is a late binding against `ir_Global`'s nameList) and (b) route to the new stackless `bb_var_global` NV_GET_fn read template in the native emitter (GN-3). `icn_is_global` (GN-1) wraps the already-populated `is_global()`/`global_names[]` table (filled by `global_register` in `polyglot_init` before `lower` runs). All three steps verified zero-behavior-change against the m2 oracle (interp `IR_VAR` case never reads `state`).

**The read path is written and wired but DORMANT.** A global-touching Icon graph cleanly EXCISES `[SMX]` (rc=0) in `--run`/`--compile` — `icn_graph_native_emittable` declines any graph with an `IR_VAR state==1` or an `IR_ASSIGN` to a global. This replaced a hard ABORT (rc=134): `bb_var` used to bomb on the global read and `IR_ASSIGN`-to-global was a `kind=5` unhandled tree node. The EXCISE is the honest boundary until **GN-4** lands the `NV_SET_fn` assign path; only then do global programs run native (GN-5 probe, GN-6 sweep).

**NEXT = GN-4** — `IR_ASSIGN` with a global lhs → `flat_drive_icn_global_assign` emitting `call NV_SET_fn(name, value)` (value already in a frame slot/reg). The `bb_var_global` read template is the consumer that will read it back. Once the assign lands, REMOVE the `IR_ASSIGN`-to-global (and, once the full chain threads, the `IR_VAR state==1`) decline from `icn_graph_native_emittable` to light the family up, then GN-5 cross-language probe + GN-6 corpus sweep (floor **m2 ≥ 130**) + GN-FENCE structural grep. Study `ir_a_Assign` in `refs/jcon-master/tran/irgen.icn` FIRST per CONSULT-CANONICAL-SOURCES.

**⛔ DUAL-MODE (Lon, 2026-06-03) — BOTH global backends are kept and maintained.** The OLD frame-slot global path (`bb_varslot`, `[r12+off]`) is NOT deleted; the NEW shared-NV-dictionary path (`bb_var_global`/`NV_SET_fn`, the SAME dictionary/namespace as SNOBOL4) is added beside it, CLI-selected (`--icn-globals=slot|nv`, **default `nv`** per Lon 2026-06-03), for an A/B performance comparison (GN-PERF) and for standalone-Icon (keep the faster `slot` model when no cross-language sharing is needed). See the Objective's DUAL-MODE DIRECTIVE block + `ARCH-ICON.md` "Variable model". **GN-4 must make BOTH dispatches switch-aware:** GN-3 currently hard-routes a `state==1` read to `bb_var_global` (nv-only) — GN-4 retrofits that `emit_core.c`/`emit_bb.c` IR_VAR arm so `slot` mode sends globals back through `bb_var`'s frame-slot path (see the GN-4 SWITCH RETROFIT note). Neither global path may be hard-wired once the switch exists.

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

**Switch shape (to be finalized in GN-3.5/GN-4):** a driver flag (`--icn-globals=slot|nv`, **default `nv`** — Lon 2026-06-03) that sets a global mode read by the `IR_VAR`/`IR_ASSIGN` dispatch arms; `slot` = OLD (`bb_varslot`), `nv` = NEW (`bb_var_global` + `NV_SET_fn`). The GN-2 `state=1` tag identifies which `IR_VAR`/`IR_ASSIGN` nodes are global *candidates*; the switch then chooses the backend for those nodes. Mode-2 already resolves globals through the dictionary regardless of the switch (see Objective note + ARCH-ICON.md "Variable model"); the switch is a mode-3/4 native-codegen distinction. **This dual-mode requirement REVISES GN-FENCE** (the "zero frame-slot for globals" grep is conditional on `nv` mode, not unconditional) — see GN-FENCE below.

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

- [x] **GN-4 — Wire assign path: `IR_ASSIGN` with global lhs uses `NV_SET_fn` (NEW path, under the switch — KEEP the OLD slot assign). DONE (working tree, Sonnet 2026-06-03), nv-mode native; slot-mode EXCISES (slot-global native = future, shares the local-assign-native rung).**
  The `--icn-globals=slot|nv` CLI switch is finalized (`scrip.c`, sets `g_icn_globals_nv` defined in `lower.c`; default flipped to `nv`=1 immediately after, per Lon 2026-06-03). New template `src/emitter/BB_templates/bb_gvar_assign_icn.cpp`: loads the rhs DESCR_t from its frame slot (`x86_frame_load64 rsi,[r12+rhs]` / `rdx,[r12+rhs+8]`), seals the global name RO and loads `rdi` via `[rip+disp]`, `call NV_SET_fn(name, val)`, stores the returned `rax:rdx` into the box's own 16-byte slot (so `write(G:=v)` consumers read it), then `jmp γ / def β / jmp ω`. **The rhs handle is `nd->α`** — `v_assign` (lower.c) now records the rhs result node on `as->α` for ICN (behavior-neutral: the m2 oracle reads the AG ring, the gen-helpers read `β` which stays NULL; verified m2 130 unchanged), so `flat_drive_icn_global_assign` resolves the rhs slot via `bb_slot_get(nd->α)`. Pure `x86()` concatenation mirroring `bb_var_global.cpp` — FACT-clean (0 raw-byte producers, no `bb_bin_t`, no `IF(MEDIUM_BINARY)`; absent from the medium-invisible REMAINING list). **SWITCH RETROFIT done (both faces):** `emit_core.c` IR_VAR read routes `state==1 && nv → bb_var_global` else `bb_var`; `emit_bb.c` IR_VAR slot-promotion takes the `bb_varslot_peek` branch for a `state==1` global in slot mode and the own-slot branch in nv mode; the `emit_core.c`/`emit_bb.c` IR_ASSIGN dispatches route a global lhs to `bb_gvar_assign_icn`/`flat_drive_icn_global_assign` only when `nv`. **`icn_graph_native_emittable` (scrip.c) is switch-aware:** in `nv` mode the `IR_VAR state==1` + `IR_ASSIGN`-to-global declines are LIFTED (read+write paths exist → runs native); in `slot` mode they remain (slot-global native not built → clean `[SMX]` EXCISE). Grounded in JCON `ir_a_Binop`/`ir_augmented_assignment` (irgen.icn): `:=` ∈ `funcs` (bounded, success→`p.ir.success`, rhs evaluated first) — matches the chain structure. Verified `G:=42;write(G)`, `S:="hello";write(S)`, `A:=10;B:=20;write(A);write(B)` all **m2==m3==m4** under `--icn-globals=nv`; default/slot mode EXCISES cleanly (rc=0); m2 switch-independent (oracle always resolves globals via NV). Makefile: `bb_gvar_assign_icn.cpp` in `RT_PIC_SRCS` + scrip compile rule (auto-linked via `$(OBJ)/*.o`). Gate: m2 corpus **130 (HARD, unchanged)**; Icon smoke m2 12/12; all FACT/structural/Icon-lane gates green (bb_bin_t=0 · no-handencoded `--strict` clean · g_vstack=0 · no-stack 10≤127 · one-reg-frame 0≤21 · prove_lower2 PASS).
  - **⚠ SWITCH RETROFIT — the GN-3 read dispatch is currently `nv`-ONLY and must be made switch-aware in GN-4 (so the OLD slot path stays reachable for globals). DONE — see above.**

- [x] **GN-5 — Probe program: cross-language global read. DONE — `test/icn_global_nv_probe.icn` passes m2==m3==m4 under `--icn-globals=nv`.**
  `test/icn_global_nv_probe.icn` (`global SHARED; SHARED := 99; write(SHARED)`) sets a global and reads it back. Under `nv` the write goes through `NV_SET_fn` and the read through `NV_GET_fn` — the SAME shared hash dictionary SNOBOL4/Snocone/Rebus use, so the global is cross-language visible by construction (an Icon `bb_gvar_assign_icn` write and a SNOBOL `bb_var` by-name read hit the same NV bucket with zero dispatch). m2 (oracle) = `99`; m3 (`--run`) = `99`; m4 (`--compile`+link `libscrip_rt.so`) = `99`. This is the proof-of-concept for the cross-language goal. (A two-language probe — Icon sets, SNOBOL reads in one program — is the natural GN-5b extension once a polyglot driver harness is wired; the namespace identity is already established.)

- [~] **GN-6 — Sweep Icon corpus globals. PARTIAL (Sonnet 2026-06-03): with nv DEFAULT, global programs run native — m4 PASS 12→19 (+7 global rungs, all outputs ✓-verified). m2 130 (HARD) held. m3 +7 blocked on the pre-existing user-proc-call segfault (m3 declines user-proc graphs).**
  Ran `test_icon_rung_suite.sh` (no flag = nv default). m2 unchanged at 130. The +7 m4 passes are `rung21_global_initial_{global_basic,global_str,multi_global}` and `rung25_global_{global_basic,global_str,global_three_procs,multi_global}` — globals set/read across procedures, correct outputs. Two decline-gate hardening fixes converted ~109 pre-existing m3 aborts/segfaults into clean EXCISEs (FAIL 190→81). **Remaining for full GN-6:** the m3 user-proc-call segfault fix (lifts the m3 decline → m3 reaches m4's +7); optionally an explicit `--icn-globals=nv`/`ICN_GLOBALS` hook is now unnecessary since nv is the default (the harness exercises nv automatically). Gate: m2 PASS ≥ 130 (held).

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
