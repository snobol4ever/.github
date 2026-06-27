# GOAL-PASCAL-BB.md — Pascal, 100% Byrd Boxes

## ⛔ FACT RULES POINTER
ONE MEDIUM, INVISIBLE + TEMPLATE-ONLY EMISSION: canonical text in GOAL-SNOBOL4-BB.md / GOAL-ICON-BB.md / RULES.md. ZERO BINARY in any `bb_*.cpp`; `x86()` internals are the ONLY binary+text emitter.

## ⛔ LANGUAGE-BLIND BB/XA TEMPLATES
No language enums/guards in `src/emitter/BB_templates/` or `XA_templates/`; dispatch on IR shape only. Completion test: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md` grep == 0.

**Repo:** SCRIP · corpus (`programs/pascal/`). **The 7th frontend.**

---

## ▶ ACTIVE RUNG (TOP / FIRST) — PAS-GVA: Pascal globals via `[rbx+k*16]` arena (Lon directive, 2026-06-27)

**Goal:** Make ALL Pascal variable access optimal by routing the program's top-level `var`s through the **slotted global arena** `[rbx+k*16]` (rbx = DESCR base, program-lifetime BSS), exactly as **Icon** and **SNOBOL4** do — retiring the NV by-name hash (`rt_gvar_get_int` / `rt_gvar_assign_int` / `rt_gvar_assign_descr` / `NV_GET_fn`, rbp-hash) for Pascal program globals. Direct memory replaces per-access hash lookup ("ten times faster"), and producer/consumer share ONE 16-byte descriptor representation (no `int`-vs-`descr` sink split).

**Why this is the right model (verified this session):** the arena is program-lifetime + single-representation; it is the correct home for Pascal top-level `var`s (which are visible to every nested routine across all activations). ζ frame `[r12+off]` is **per-activation** storage — correct for locals/params (Pascal already uses it for `decl_level>1` / byref / has-children), **wrong** for program-global lifetime. So globals → arena, locals → ζ frame. That is "optimal" for both.

**Verified current state (the bug this dissolves):**
- The slotted-global table (`global_names[]` / `is_global` / arena) is fed by exactly ONE site: `src/driver/polyglot.c:89-94`, which calls `global_register()` from a `TT_GLOBAL` node — already enabled for `LANG_PASCAL`. **But Pascal never emits `TT_GLOBAL`:** its top-level `var`s are `TT_VAR` children of `TT_PROGRAM` (`src/parser/pascal/pascal.y`), and `build_scope` (`src/lower/lower_pascal.c:515`) populates a `pas_scope_t` **only for `TT_PROC_DECL`** — the main program's vars enter NO scope. So `lower_var`/`lower_assign_var` (`lower_pascal.c:60/91`) hit the `slot < 0` branch and emit bare `IR_VAR`/`IR_ASSIGN` → NV by-name.
- M4 generic path (`src/driver/scrip.c:3150`) does call `gva_collect_graph(sbbg)` and set `g_gva_active=(n_gva>0)` (`:3178`); `gva_name_eligible` (`emit_bb.c:118`) rejects only SNOBOL keyword names, so a plainly-named Pascal global that appears as `IR_VAR`/`IR_ASSIGN` in the **main** graph IS collectible — but only if lowering does not need a frame for it and the name actually surfaces. **M3 generic `--run` path (`scrip.c:~3354`) never calls `gva_collect_*` at all** → `g_gva_active` stays 0 → Pascal globals are by-name in M3 unconditionally. Two-sided fix required.
- Consumers already have the arena arm: `bb_gvar_assign.cpp` / `bb_gvar_assign_call.cpp` `op_gva_k >= 0` branches write the FULL rax/rcx descriptor pair to `[rbx+k*16]` / `[rbx+k*16+8]`; `op_gva_k` is set at `emit_core.c:354` via `gva_index_of` when `g_gva_active`. Producer `bb_binop_gvar_arith_slot.cpp` and these consumers then share representation.

**Scope honesty:** Frontier #1's three probes (`arr2dtype`/`arr2dtype2`/`arrparam`) are dominated by **local/param** arith (`s := s + a[j]` where `s,j` are function locals and `a` is a value-param array), NOT program globals — so this rung primarily makes TRUE globals (top-level `var`s like `r`, `m`, `v`, `i`) optimal. Whether it closes those three depends on PAS-GVA-0 findings (the residual fault may be global-aggregate marshalling, which this fixes, OR the local-temp `int`-vs-`descr` mismatch, which is a separate rung). Do not claim those three closed off this rung without re-running them under PAS-GVA-4.

### Steps (do top-to-bottom; each ends at its gate; first `- [ ]` is the cursor)

- [x] **PAS-GVA-0 — CHARACTERIZE (DONE 2026-06-27, no code change).** Built (`scrip` 18.4M, `libscrip_rt` 18.4M). Minimal probe `program g; var a,b: integer; begin a:=1; b:=a+2; writeln(b) end.` M3 `--run` → `3` ✓; M4 `--compile`→`gcc`→link→run → `3` ✓. **FINDING — the M4 arena is HALF-WIRED, and "works" only by accident:**
  - The generic M4 path already emits the arena preamble: `__gva: .space 32` (k*16, `b`=k0→`[rbx+0]`, `a`=k1→`[rbx+16]`), `gva_register@PLT`, `mov rbx,rax`. `g_gva_active=1`, `gva_index_of` resolves both.
  - **READ arms honor the arena:** `IR_VAR gva` and `IR_BINOP_GVAR_ARITH` read `[rbx+k*16]`/`[rbx+k*16+8]` — BUT each read carries a `cmp edx,6 / jne fallback` DT_I-tag guard that, on tag≠DT_I, **falls back to `rt_gvar_get_int(name)` (NV hash)**.
  - **ASSIGN arms do NOT honor the arena for literals/vars:** in `bb_gvar_assign.cpp` the `IR_LIT_I`/`IR_LIT_S`/`IR_LIT_F`/`IR_VAR` assign arms (lines 20–48) ignore `op_gva_k` and always call `rt_gvar_assign_*` (by-name) — so `a := 1` writes the **NV hash**, never `[rbx+16]`. Only the `IR_BINOP`/`IR_CALL`/`IR_IDX`/frame-var assign arms (lines 52–) check `op_gva_k>=0` and write the arena (so `b := a+2`'s computed result writes `[rbx+0]`).
  - **Net:** `a`'s arena slot is NEVER populated (its write went by-name); the arena READ of `a` sees tag=0≠DT_I and falls through to the by-name hash where the value actually lives. The program is correct purely because every gva read has a by-name escape hatch. The arena is decorative for scalar literals. **This is latent breakage waiting for any read path without the tag-guard fallback, and it defeats the "ten times faster" goal (still a hash hit on the hot path).** PAS-GVA-1/3 must make the assign arms honor `op_gva_k` so writes land in the arena, and then the read fallback becomes truly dead and removable. M3 (`--run`) has NO arena at all (no `gva_collect`) — pure by-name — confirming PAS-GVA-2 is required. (arr2dtype2 dump deferred into PAS-GVA-4 where the aggregate path is the subject.)

- [~] **PAS-GVA-1 — SCALAR LITERAL GLOBAL WRITES → ARENA (LANDED 2026-06-27, M4).** Root re-scoped by PAS-GVA-0: globals are ALREADY collected/registered (arena exists, `gva_index_of` resolves them) and `op_gva_k` is already set per-node at `emit_core.c:354`. The gap was purely in the consumer: `bb_gvar_assign.cpp`'s `IR_LIT_I`/`IR_LIT_F` assign arms ignored `op_gva_k` and always called `rt_gvar_assign_*` (by-name). **Edit:** added the `op_gva_k >= 0` arena branch to both arms (store `DT_I`/`DT_R`-tag + value to `[rbx+k*16]`/`[rbx+k*16+8]`), mirroring the existing BINOP/CALL arms; the `op_gva_k == -1` path is byte-for-byte the original (so SNOBOL by-name is untouched). **Verified:** minimal probe `a:=1` now emits `mov [rbx+16],6; mov [rbx+24],1` (was `rt_gvar_assign_int`); zero `rt_gvar_assign_int` left in that probe; M3 `3`✓ M4 `3`✓. **Gate:** Pascal M4 **127/0** and M3 **127/0** (up from the 124/3 floor — `arr2dtype`/`arr2dtype2`/`arrparam` now PASS). **Cross-language (landmine #5):** SNOBOL crosscheck identical before/after edit (`--run` 152/109, `--compile` 172/83 — all pre-existing, regression-neutral; baseline measured by revert+rebuild). Icon global-scalar assign lowers to `IR_ASSIGN_DESCR` (a different template that already honored the arena), so Icon is unaffected — confirmed by direct smoke `global g; g:=5; g:=g+3; write(g)` → `8` in BOTH modes. The edit targets exactly the Pascal lowering shape. **REMAINING in -1:** `IR_VAR` (global:=global copy) and `IR_LIT_S` (string lit → global) assign arms still ignore `op_gva_k` (rarer in Pascal; defer to -1b only if a probe needs it). Also the gva READ arms still carry the by-name tag-guard fallback — now that scalar writes populate the arena, that fallback is becoming dead; removal is PAS-GVA-3. **NOTE the surprise win:** because the 124/3 floor's three failing probes (`arr2dtype`/`arr2dtype2`/`arrparam`) were exercising a global-scalar write that silently went by-name while a sibling read came from the (zeroed) arena, making writes land in the arena closed them — so Frontier #1 partially dissolved exactly as the rung predicted, via storage unification rather than a local-temp patch. Re-confirm the nature of any *remaining* Frontier-1 residue under PAS-GVA-4.

- [ ] **PAS-GVA-1b — (optional) `IR_VAR`/`IR_LIT_S` global-assign arena arms.** Only if a Pascal probe assigns a string literal or copies global←global. `IR_VAR` arena form: read src (arena or by-name) → write dst `[rbx+k*16]` pair. Guard `op_gva_k>=0`; preserve by-name otherwise. Gate: full M3+M4 + cross-lang smoke.

- [x] **PAS-GVA-2 — M3 ARENA SETUP (`--run`) — LANDED 2026-06-27.** Generic `[SBB]` M3 run branch (`scrip.c`, the branch Pascal falls into when not is_icon/is_raku/is_prolog) now sets up the in-process global arena, gated `if (is_pascal)`. **Edit (two hunks, both inside the `--run` branch):** (1) after `rt_proc_reset()`, before the proc-build + main-build loops: `gva_collect_reset()` → `gva_collect_graph(main_graph)` (Pascal globals surface as `IR_VAR`/`IR_ASSIGN` in the main graph, all in `gva_collect_graph`'s switch; survive `gva_name_eligible` which excludes only SNOBOL keyword names) → `calloc` the DESCR arena → `gva_register(names,arena,n)` → `g_gva_active=1`; trace under `SCRIP_M3_GVA_TRACE`. Placed BEFORE both loops so the arena is live during proc emission AND main emission (globals are visible to nested procs). (2) at the main-graph exec site: `m3_enter_with_rbx(fn, rt_frame(), 0, m3_gva_arena)` when active (loads rbx=arena before entry) instead of bare `fn(rt_frame(),0)`, then `g_gva_active=0`. **Verified:** `SCRIP_M3_GVA_TRACE=1 ./scrip --run g.pas` now prints `[M3-GVA] m3 globals via rbx-arena: active=1`; arena genuinely used (M4 `.s` of a 4-global probe: 42 `[rbx+N]` accesses vs 6 residual read-fallback `rt_gvar_*`, the latter retired by PAS-GVA-3). **Gates:** Pascal M3 **127/0**, M4 **127/0** (M4 path untouched — edit is `--run`-only). **Cross-language (shared `scrip.c`, landmine #6):** proven regression-neutral by stash+rebuild — SNOBOL M3 crosscheck byte-identical at **155/106** with and without the edit (the collection is `is_pascal`-gated, so SNOBOL never enters the arena setup and stays by-name; confirmed: a SNOBOL probe emits NO `[M3-GVA]` trace line).

- [ ] **PAS-GVA-3 — RETIRE NV FOR PASCAL GLOBALS.** With both modes routing the arena, confirm NO Pascal top-level var still reaches `rt_gvar_get_int`/`rt_gvar_assign_*`/`NV_GET_fn`. Remove any now-dead by-name path reachable only from Pascal globals (do not disturb SNOBOL, which still legitimately uses NV). Gate: asm grep — Pascal global access emits zero `rt_gvar_*`/`NV_GET` calls in both modes; full M3+M4 gate.

- [ ] **PAS-GVA-4 — AGGREGATE GLOBALS + FRONTIER-1 RE-CHECK.** Ensure global arrays/records/sets (`r: row`, `m: mat`, `v: vec`) route through the arena correctly (slot holds the aggregate descriptor/pointer); verify `r[i]:=i+1` write and `writeln(sumvec(v))` arg marshalling of a global aggregate. Then RE-RUN `arr2dtype`/`arr2dtype2`/`arrparam` and record whether they close or whether the residual local-temp `int`-vs-`descr` mismatch remains (→ spin off as a separate Frontier-1 rung; do not fold its claim here). Gate: full M3+M4; updated probe tally recorded.

- [ ] **PAS-GVA-5 — OPTIMAL LOCALS CLOSURE.** Confirm non-global locals/params use direct `[r12+off]` descriptor storage uniformly with no by-name leakage, completing "all Pascal variable access optimal" (globals=arena, locals=ζ frame, params=ζ frame/cell). Gate: full M3+M4; brief invariant note added to Mechanism inventory.

### PAS-VAR — proper variable processing in general (the layered nested model)

The arena (globals) + ζ frame (locals) split is only complete when the THREE-TIER nested-access model is uniform and audited end to end. Tiers: **(0)** program globals → `[rbx+k*16]` arena, reachable with the same `rbx` from ANY nesting depth (zero static-link walk — the arena removes the *longest* walks); **(1)** own locals/params of the current activation → `[r12+off]` ζ frame, zero hops; **(2)** an enclosing routine's non-global local at lexical level 1..N-1 → static-link chain walk of exactly `hops` frames (`IR_VAR_FRAME`/`IR_ASSIGN_FRAME` carry `dval=hops`). Existing hooks: `lower_pascal.c` `lower_var`/`lower_assign_var` compute `hops` (`:78`) and `use_frame`; `build_scope`/`build_scope_chain` set `byref`/`has_children`. This family makes the tiers correct and provably non-overlapping.

- [ ] **PAS-VAR-1 — TIER AUDIT MATRIX.** For a deliberately deep probe (3+ nesting levels: `main` → `outer` → `inner`, with `inner` reading a main global, an `outer` local, and its own local), dump M3+M4 and record which tier each of the three reads resolves to (arena vs own-frame vs N-hop SL walk) and that `hops` is exactly right at each site. Catalogue every (tier × read/write × scalar/aggregate) cell that is exercised by the corpus. Gate: documentation; matrix recorded here.
- [ ] **PAS-VAR-2 — STATIC-LINK WALK CORRECTNESS (tier 2).** Verify the `hops`-deep frame walk reads/writes the correct enclosing slot for every depth the corpus exercises (nestvar*/nestpv*/nestcount/nestshadow/nest2). Fix any off-by-one in the SL chain (the `decl_level`/`hops` pairing in `lower_pascal.c` + the frame-load helper). Gate: full M3+M4; the nest* probe family green.
- [ ] **PAS-VAR-3 — VAR-PARAM (byref) CELL UNIFORMITY.** Confirm var-params resolve to cell addresses uniformly (`IR_VAR_FRAME_REF`/`IR_ASSIGN_FRAME_REF`), including a global passed byref into a nested routine (the callee must reach the GLOBAL's arena cell, not a stale copy) and an enclosing local passed byref further down. Gate: full M3+M4; varparam/vparr/vpfld/nestpv* green.
- [ ] **PAS-VAR-4 — NO BY-NAME LEAKAGE SWEEP.** Final asm grep across ALL Pascal probes in BOTH modes: every variable access is arena (`[rbx+k*16]`), own-frame (`[r12+off]`), or SL-walk — **zero** `rt_gvar_*`/`NV_GET_fn` remaining for Pascal. Then the gva READ-arm by-name tag-guard fallback (still emitted today) is provably dead → remove it (coordinate with PAS-GVA-3). Gate: grep==0; full M3+M4; cross-lang gates before pushing shared files.

---

## ▶ PAS-DISPLAY — lexical display in r13/r14/r15: O(1) enclosing-scope access (Lon directive, 2026-06-27)

**Goal:** Replace the Tier-2 (enclosing-routine local) **static-link chain-walk** with a **register-resident lexical display**. Map the three SNOBOL pattern registers — idle for the whole of any Pascal program — to absolute lexical levels: `rbx`=display[0] (globals, already done via PAS-GVA), `r13`=display[1], `r14`=display[2], `r15`=display[3], `r12`=current activation's frame. Then a read/write of a variable at lexical level L is a SINGLE register-relative load/store `[display_reg(L)+off]` — O(1) — instead of `op_dval` dependent `mov rax,[rax+0]` pointer-chases. This is the SPEED half of "clean hierarchical scoped variable access" (PAS-VAR audits the walk for *correctness*; this rung makes it *fast* and retires the walk for the common depth).

**Why r13/r14/r15 are free (verified this session):** `src/emitter/bb_regs.h` assigns `r13`=Σ subject, `r14`=δ cursor, `r15`=Δ limit — the Byrd-box pattern matcher's working set. A **Pascal program emits ZERO pattern-match boxes**, so all three are dead for the entire run (`grep` of r13/r14/r15 across `bb_var_frame*.cpp`/`bb_assign_frame*.cpp`/`bb_callee_frame.cpp` == 0 refs). They are three callee-saved 64-bit registers sitting idle — exactly the home a display wants.

**Why a display beats static links here:** each call touches EXACTLY ONE display register (the callee's own lexical level): `push display[L]; mov display[L],<my frame>` on entry, `pop display[L]` on exit — O(1) per call regardless of nesting depth. Access is then O(1). Static links are O(hops) *per access*; a display is O(1) per call + O(1) per access. Any nested code that reads an uplevel variable more than ~once per call (i.e. essentially all of it, and emphatically loops) wins. The current cost lives at `bb_var_frame.cpp:18` — `FOR(0,op_dval,[]{ mov rax,[rax+0]; })` is a serial dependency chain the CPU cannot pipeline.

**Depth budget (measured):** `pcom.pas` proc/function decls cluster at lexical levels ~1–5 (bulk ≤4, a couple deeper). Three display registers cover levels 1–3; level ≥4 needs a fallback (spilled memory display, OR retain the existing chain-walk for the overflow tail only). Common case is fully register-served.

### Steps (top-to-bottom; first `- [ ]` is the cursor)

- [x] **PAS-DISPLAY-0 — CHARACTERIZE (DONE 2026-06-27, no code change).** Findings recorded; design FROZEN.
  - **Regs confirmed idle:** `grep` of `r13|r14|r15` across `bb_var_frame*.cpp`/`bb_assign_frame*.cpp`/`bb_callee_frame.cpp` == **0 refs**. They are Σ/δ/Δ (bb_regs.h) and a Pascal program emits no pattern boxes, so all three are dead for the whole run.
  - **Walk located + quantified.** 3-level probe `nest3.pas` (`main` L0 / `outer` L1 / `inner` L2; `inner` does `ov:=ov+iv` and `g:=g+ov`). M3+M4 both correct (`11`,`111`). The level-2→level-1 read of `ov` emits, at `nest3.s:30`:
    ```
    lea rax, [r12 + 0]            ; own (L2) frame
    mov rax, qword ptr [rax + 0]  ; ← hop 1: chase static link to L1 frame   (FOR op_dval loop body)
    mov rcx, qword ptr [rax + 16] ; read ov low
    mov rcx, qword ptr [rax + 24] ; read ov high
    ```
    One dependent `mov rax,[rax+0]` per lexical hop — a serial load chain. With display: `mov rcx,[r13+16]` (one load, no walk). `--dump-ir` confirms the `IR_VAR_FRAME`/`IR_ASSIGN_FRAME sval="ov"/"iv"` nodes; the own-frame access of `iv` (hop 0) correctly emits no walk (`nest3.s:42`, reads `[r12+...]`), so the loop trip count == hop count is already right.
  - **`op_dval` = HOP COUNT (relative), not absolute level.** Lowering (`lower_pascal.c` `lower_var`/`lower_assign_var`) stores `IR_LIT(nd).dval = #scope-chain steps from current scope to the declaring scope`. So for the display the codegen must compute **absolute target level = current_proc_level − op_dval**, then pick `display_reg(level)`: level 0→rbx (but globals are already routed via GVA, not IR_VAR_FRAME — so a frame node never targets level 0), 1→r13, 2→r14, 3→r15. The current proc's lexical level is available at emit time (the proc-build path already sets `g_emit_frame_caller_dl`/`decl_level`; PAS-DISPLAY-1 must thread the *current* level into the frame-access templates, e.g. via an emit-global `g_cur_lex_level`, dispatched on IR shape — NO `LANG_PASCAL` guard).
  - **Depth budget OK:** pcom proc/func decls cluster L1–5 (bulk ≤4); 3 display regs serve L1–3, fallback (chain-walk retained) for L≥4. **Mapping FROZEN:** rbx=L0(globals via GVA), r13=L1, r14=L2, r15=L3, r12=current; L≥4 → keep the `FOR op_dval` walk as the else-branch.
- [ ] **PAS-DISPLAY-1 — DISPLAY SAVE/SET/RESTORE at proc entry/exit.** In the proc preamble/epilogue emission (the proc-build path, `gvar_flat_chain_build_at` callees + `bb_callee_frame.cpp`), for a proc whose lexical level L∈{1,2,3} emit `push display[L]` + `mov display[L], <frame ptr>` on entry and `pop display[L]` on exit. Dispatch on the proc's absolute level (IR shape), NOT a language flag. Main program (level 0) sets nothing (globals are rbx). Gate: a 3-level nest probe shows each display reg holding the right frame at each depth (gdb or a trace); full M3+M4 **127/0**; cross-lang gates (shared emit path) — SNOBOL/Icon/Prolog identical before/after.
- [ ] **PAS-DISPLAY-2 — TIER-2 READ via display.** `bb_var_frame.cpp` emits `mov rcx, [display_reg(level) + 16 + slot*16]` (+`+8` for the value half) instead of the `lea rax,[r12]` + `FOR op_dval{mov rax,[rax+0]}` walk, when the target level∈{1,2,3}. Keep the walk as the `else` for level≥4 (the fallback). Gate: `nestvar*`/`nest2`/`nestcount` green; emitted `.s` shows a single load (no `FOR`-loop) for the in-budget case; full M3+M4; cross-lang.
- [ ] **PAS-DISPLAY-3 — TIER-2 WRITE + byref via display.** Same substitution in `bb_assign_frame.cpp`, `bb_assign_frame_ref.cpp`, `bb_var_frame_ref.cpp` (var-param cell addresses): `[display_reg(level)+off]`. A global passed byref into a nested routine must still reach the GLOBAL's arena cell (rbx), not a display slot — verify the byref-of-global path is unchanged. Gate: `nestpv*`/`nestshadow`/`varparam`/`vparr` green; full M3+M4; cross-lang.
- [ ] **PAS-DISPLAY-4 — DEEP-NEST FALLBACK + WALK RETIREMENT.** Implement the chosen level-≥4 fallback (spilled memory display, or chain-walk for the overflow tail only). Confirm the `FOR op_dval` walk is emitted ONLY for the fallback path (asm audit: in-budget probes have zero `mov rax,[rax+0]` chains). Verify the deepest pcom-shaped probe. Gate: full M3+M4; deep probe green; cross-lang; asm audit clean.
- [ ] **PAS-DISPLAY-5 — BENCH.** Add a synthetic uplevel-in-loop benchmark (a level-3 inner loop reading a level-1 variable N times) + re-run any nesting-heavy corpus, and record the speedup vs the pre-rung chain-walk baseline in `corpus/BENCHMARKS-PASCAL.md`. Honest numbers; note this is the addressing win only (orthogonal to the boxed-integer and call-frame-allocation forks).

### PAS-DISPLAY landmines
- **LANGUAGE-BLIND:** the register repurposing is legal ONLY because dispatch is on the frame node's absolute level / `op_dval` (IR shape), and a Pascal program never co-hosts SNOBOL pattern boxes — so r13/r14/r15 are unambiguously the display in a Pascal program and unambiguously Σ/δ/Δ in a SNOBOL program; the two never coexist in one program. NO `LANG_PASCAL` guard in any `bb_*.cpp`. Completion still passes `SCRIP/BB-TEMPLATES-LANG-AUDIT.md` grep == 0.
- **CALLEE-SAVED ABI:** r13/r14/r15 are callee-saved; the display push/set/pop composes with that, but VERIFY every runtime helper a Pascal box calls (`rt_call_named_proc_sl`, `rt_frame`, arr/record sinks) preserves them — a helper that clobbers a display reg corrupts uplevel access. (rbx already survives as the program-global arena, so the precedent holds.)
- **SHARED EMIT FILES:** `bb_var_frame*.cpp`/`bb_assign_frame*.cpp`/`bb_callee_frame.cpp` + any `emit_bb.c`/`emit_core.c` hook are shared → run ALL FOUR language gates + template-byte-identity before landing.
- **SUPERSEDES PAS-VAR-2's framing:** PAS-VAR-2 "verify the SL walk" becomes "the walk is the depth-≥4 fallback only"; keep PAS-VAR-2 as the correctness audit feeding PAS-DISPLAY-2/3.

---

## ▶ PAS-BENCH — official Pascal benchmarks into corpus + x86-64 speed comparison (Lon directive, 2026-06-27)

**Goal:** put the canonical Pascal benchmark programs into `corpus/programs/pascal/bench/` (or `corpus/benchmarks/pascal/`) and run SCRIP M3/M4 vs available native x86-64 Pascal systems (fpc is the obvious peer; gpc if installable), reporting speed the same way `corpus/BENCHMARKS.md` already does for SNOBOL (in-program `TIME()`, startup excluded, normalized, same machine).

**Research findings (web, 2026-06-27 — recorded so they are not re-derived):**
- **Todd Proebsting** (PhD Wisconsin 1992; Arizona; later MSR) is a compiler-codegen researcher: BURG/iburg/wburg/gburg (tree-pattern-matching instruction selection), "Optimizing an ANSI C Interpreter with Superoperators" (POPL'95), DCG dynamic code generation, demand-driven register allocation. **No dedicated Proebsting *Pascal* compiler exists** in his record — the "Pascal" hits in search are Anders Hejlsberg (Turbo Pascal), a different person. So "Todd's Pascal" is a non-entity; do not chase it.
- **Did Todd use BB techniques?** YES — but for **Icon**, not Pascal, and it is the DIRECT ANCESTOR of THIS repo's model. Proebsting & Townsend, *"A new implementation of the Icon language"* (Softw. Pract. Exper. 30(8):925-972, 2000) = **Jcon**, whose **"four-chunk control-flow model handles goal-directed evaluation and produces constructs not expressible as Java code"** — that four-chunk/four-port control-flow model is exactly our four-port Byrd-box (α β γ ω) generator model. Companion: Proebsting, *"Simple Translation of Goal-Directed Evaluation"* (PLDI'97). This repo already carries `jcon_irgen.icn` and `LOWER-REWRITE-FROM-JCON.md` — the lineage is acknowledged. (Aside: superoperators ≈ our composite/fused BB templates in spirit.) **Takeaway:** the BB technique is Proebsting-Icon heritage applied across all 7 frontends here; Pascal reuses it but Proebsting himself never wrote a BB Pascal.
- **Canonical Pascal benchmarks (the "official" set):** **(a) Whetstone** (Curnow & Wichmann, NPL, 1972 — synthetic FP, originally Algol 60, classic Pascal port); **(b) Dhrystone** (Weicker, Siemens, 1984 — synthetic integer/string/proc-call; v2 is the optimizer-resistant one). **The original Pascal Dhrystone v2 source is fetchable and confirmed:** `github.com/Keith-S-Thompson/dhrystone` → `original-sources/dhry-pascal` (a `sh`-unbundle shar containing Weicker's "Dhrystone Benchmark (Pascal Version 2)" RATIONALE + source; 1453 lines). **(c) Hennessy's Stanford integer suite** (perm, towers, queens, intmm, mm, puzzle, quick, bubble, tree(sort), FFT) — Pascal-origin, the small-but-control-flow-rich set used throughout the Icon/Unicon world. **(d) Byte Sieve** (Sieve of Eratosthenes) — already have `sieve.pas` in the corpus.

### Steps

- [ ] **PAS-BENCH-0 — SCOPE vs P4 DIALECT.** Whetstone/Dhrystone use reals, records, pointers, and (Dhrystone) strings/enotation; check each against the P4 subset (`pcom.pas` acceptance — integer=16-bit, `array/record/set(0..58)/pointer`, value+var params). Triage which benchmarks run as-is, which need a P4-faithful trim, which are out of scope. Record the triage. Gate: documentation.
- [ ] **PAS-BENCH-1 — IMPORT + PROVENANCE.** Add the in-scope sources under `corpus/` with a `PROVENANCE`/`NOTICE` line per file (author, origin URL, license/PD status — Dhrystone is widely treated PD/permissive; Whetstone/Stanford likewise long-circulated, but record the source). Smaller hand-portable ones (Sieve already present; Stanford perm/towers/queens/bubble/quick) first; Dhrystone/Whetstone after PAS-BENCH-0 trim. Use the existing `corpus/benchmarks/` layout convention (`LAYOUT.md`). Gate: files committed to corpus with provenance.
- [ ] **PAS-BENCH-2 — SCRIP CORRECTNESS GATE.** Each imported benchmark gets a `.ref` (value-cross-checked vs fpc per the ⚖ Provenance rule — SCRIP width-10 ints, NOT fpc's unpadded) and must pass the Pascal M3+M4 gate before it counts. A benchmark that bombs an unimplemented shape is logged as a frontier, not silently skipped. Gate: imported set green in both modes (or each failure ticketed).
- [ ] **PAS-BENCH-3 — TIMING HARNESS + PEER INSTALL.** Mirror `BENCHMARKS.md` methodology: in-program timing where the source allows (Dhrystone already self-times; add a loop-count knob), startup excluded, normalized per-iteration, same machine. Install peers: `fpc` (Free Pascal, native x86-64 — `apt-get install fpc`), optionally `gpc`. Peer compile flags recorded (e.g. `fpc -O2`). Gate: harness script in `SCRIP/scripts/` or `corpus/run/`.
- [ ] **PAS-BENCH-4 — RUN + REPORT.** Produce a `corpus/BENCHMARKS-PASCAL.md` table: SCRIP-M3 vs SCRIP-M4 vs fpc(-O2) [vs gpc], ms/iteration normalized, ratio columns. Honest reporting: note where SCRIP is a tree-walking-free flat-BB native vs fpc's mature optimizer; do not cherry-pick. Gate: report committed; numbers reproducible by the harness.

**Bench landmines:** keep benchmark sources OUT of the M3/M4 *correctness* gate loop if they are long-running (use the `timeout 30s` corpus-runner budget, not the 8s smoke); never wire benchmark `.s` byte-identity into a gate; record peer versions/flags so numbers are reproducible.

---

## ▶ CURRENT STATE (Session 66, 2026-06-24)

**Gate: M3 124/3 XFAIL=0 NOREF=2. M4 124/3 ASMFAIL=0.** (NOREF=2: `chararr_probe` has no `.ref`; `recursion` has no `.ref`. `realparam` false-passes — its `.ref` is 1 byte `\n`; correct value `       3.0`; probe crashes rc=134.)

**What landed this session (SCRIP `cd4672a`):** `emit_bb.c` — fixed nested descriptor-arith representation mismatch. When a `IR_BINOP_GVAR_ARITH_SLOT` Arm-2 arith node has an operand that itself is a descriptor-producing nested arith BINOP (e.g. the `a.x*b.x` sub-product in `dot := a.x*b.x + a.y*b.y`), that operand's result lives in a 16-byte descriptor slot (tag@+0, value@+8 via `rt_num_arith`), but the Arm-2 read was using offset +0 (the tag field), yielding `6+6=12` instead of `3+8=11`. New `arith_emits_descr()` helper mirrors the dispatcher's Arm-1-vs-Arm-2 choice exactly: a BINOP emits a descriptor iff `bb_arith_is_dynamic` is true and *both* of its operands are call/idx-kind (or are themselves descriptor-emitting). When an Arm-2 operand satisfies this, its kind is normalized to `IR_CALL` so the existing `+8` value-read fires. Routing unchanged; bare-int chain (gvar/literal operands) untouched. Validated: SNOBOL feature `.s` 0/153 changed, SNOBOL bench OK=15/FAIL=0 identical, Prolog parity 115/0 identical, no Icon path hit, template byte-identity unchanged. M3/M4 123/4→124/3. `recparam3` CLOSED.

**Closed this session:** `recparam3` (`dot := a.x*b.x + a.y*b.y` — nested product sum over record fields).

**NEXT FRONTIERS (priority order):**

1. **Flat assign-RHS arith: gvar + call operand (Arm-2 bare-int vs IR_ASSIGN descriptor consumer).** `s := s + a[j]` → blank/"TABLE"/segfault. Affects `arr2dtype`, `arr2dtype2`, `arrparam`. Root cause fully diagnosed: the `IR_BINOP_GVAR_ARITH_SLOT` Arm-2 writes a **bare int** to slot+0, but the consuming `IR_ASSIGN` (via `flat_drive_gvar_assign_binop`, `emit_bb.c:3327`) reads that slot as a full **tagged descriptor** (`+0`=tag→rbx+0, `+8`=value→rbx+8), so the tag field receives the numeric result and the value field is garbage. This differs from the nested-product case (which was an Arm-2 *read* offset bug, not an Arm-2 *write* representation bug). The `t := t + f + 2` case works because its terminal assign hardcodes `mov [rbx+0],6` (DT_I) — but the gvar-assign-binop path does not. Fix shape: make the gvar-assign-binop path apply the DT_I tag when the RHS BINOP took Arm-2 (bare int), OR make Arm-2 write a full descriptor. The latter is principled but touches Arm-2's shared representation; beware cross-language regression — the fix landed in this session's early attempt regressed `alphacmp/enum2/pb33/pb34/pb35` until the correct `arith_emits_descr` predicate was applied. The flat case needs an analogous "Arm-2 output is bare int, not descriptor" signal at the assign consumer.

2. **`realparam.ref` gate-integrity fix.** Ref is 1 byte `\n`; correct value `       3.0`. Probe crashes rc=134 (`flat_drive_assign` missing α, real-valued fn param). Fix: update ref and treat as genuine crash.

3. **pcom self-compilation (deeper, after floor is real).** `var x: integer;` raises spurious `error(103)` from `searchid` — pointer-BST symbol table corrupts at scale. `procedure` decl segfaults rc=139 M3+M4.

No mode-2 `--interp` (DE-INTERP done); only `--run` (M3) and `--compile` (M4).

---

## Session Setup
```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && rm -f scrip && make -j4 scrip > /tmp/build_full.log 2>&1
[ -x scrip ] || { grep "error:" /tmp/build_full.log | head -5; exit 1; }
make libscrip_rt
for r in /home/claude/SCRIP /home/claude/corpus /home/claude/.github; do ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" ); done
bash /tmp/run_gate_m3.sh # must be 127/0
bash /tmp/run_gate_m4.sh # must be 127/0 (assemble+link+run; -no-pie). NEVER trust an M4 watermark not from this recipe.
```
Gate scripts (recreate in /tmp): loop `*.pas` in `corpus/programs/pascal`, skip `pcom/pint/ppp`, XFAIL `recursion.pas`; M3 = `scrip --run f < inp` vs `f.ref`; M4 = `scrip --compile` → `gcc -c` → link `out/libscrip_rt.so` (`-no-pie -lscrip_rt -lgc -lm -Wl,-rpath`) → run vs `f.ref`.

---

## Mechanism inventory
- **Rail:** `LANG_PASCAL`=6, `IR_LANG_PAS`=7, body walker `lower_pascal_body`.
- **Frame-as-BB:** `[fb+0]`=SL, `[fb+16+k*16]`=DESCR slot k. VAR params = cell addresses (IR_VAR_FRAME_REF/IR_ASSIGN_FRAME_REF). Migration: `decl_level>1 || byref_mask`; main stays NV. var-param-of-aggregate-element uses copy-in/out (`lower_pascal.c` rewrites `genlabel(agg[i])`→`tmp:=agg[i]; genlabel(tmp); agg[i]:=tmp`).
- **2D arrays:** rule `selector '[' expr_list ']'` (2 elts) → flat `BINOP_ADD(BINOP_MUL(i,ncols),j)`, `TT_IDX(a,flat)`. PEERS aux (`bb_operand_aux_set` in lower_binop) records both operands; `walk_bb_flat case IR_BINOP` wires them when `bb_child0==NULL` using `g_emit_cfg`. `lc_arg_block` = isolated subgraph; save/restore `g_emit_cfg` around `flat_emit_arg_subchain`.
- **Calls:** dval=2.0 → `rt_call_arr`; dval=3.0 → `rt_call_named_proc(_sl)`. `marshal_call_arg` (gvar) dispatch: pre-computed DESCR slot → inline-arith(+DT_I) → relop → nested slot → terminal CALL → LIT → varslot. Known issue: `marshal_single_call` allocs fresh slots bypassing `gvar_drive_call_arg_slots` → zeros.
- **Booleans:** INTVAL(1/0); `pas_cond`=`expr≠0`; and/or=MUL/ADD; not=`pas_flip_rel`. **Polymorphic relop (all 6, char-array/string-aware):** `IR_BINOP_GVAR_RELOP` arm (`bb_binop_gvar_relop.cpp`) → `rt_relop_descr2`→`binop_apply`; DT_I falls to int cmp. String-type hint set by `pas_rel`/`pas_is_strtyped` (`IR_LIT.dval=1.0`) for whole char-arrays, string lits, or `TT_IDX(TT_VAR,…)` of a char-array.
- **goto/label:** pass-1 pre-registers IR_SUCCEED landings; intra-proc only.
- **I/O:** `__pas_writeln/__pas_write` interleaved (value,width). Default int=10, real=20, char=-2.
- **Char:** ordinals; charvar args wrapped `__pas_chr`. **Arrays/records/ptrs:** TT_IDX→`arr_get`; `a[i]:=v`→`arr_set_pure`; records=field-index arrays; sets=`__pas_set*/in`; nested record-in-record stored as `\x05`-separated string in parent SOH slot (`__pas_nrec_*`). **Functions:** body ends `IR_RETURN(dval 0)` reading `IR_VAR(funcname)`.

## Target dialect — P4 subset
`pcom.pas` + `grammar/pascalp.y`. integer=16-bit; array, record, set(0..58), pointer; value+var params; nested routines; goto intra-proc only. If pcom rejects a probe, out of scope.

## ⚖ Provenance
`pcom.pas`/`pint.pas` = behavioral oracle only — never transliterated. `.ref` = SCRIP width-10 integers (from M3, value-cross-checked vs fpc), NOT fpc's unpadded ints.

## Invariants
No AST walking in modes 3/4. Zero C Byrd-box functions. Four ports (α β γ ω). Modes 3/4 emit no byte outside `bb_emit_x86`.

## Where things live
| Thing | Path |
|-------|------|
| Oracle | `corpus/programs/pascal/pcom.pas` / `pint.pas` |
| Grammar | `corpus/programs/pascal/grammar/pascalp.{l,y}` |
| Probes | `corpus/programs/pascal/*.pas` |
| Frontend | `src/parser/pascal/pascal.{l,y}` |
| Lowering | `src/lower/lower_pascal.c` + `lower_program.c` |
| BB templates | `src/emitter/BB_templates/` |

## ⚠ Landmines
1. `rm -f scrip` before `make scrip` — no prerequisites.
2. Pascal regen ONLY: `cd src/parser/pascal && bison -d -o pascal.tab.c pascal.y`. NEVER full regen. After editing `pascal.y` you MUST regen AND recompile `pascal.tab.o` (`rm -f scrip` alone leaves it stale).
3. `touch` templates before `make scrip` after any template edit.
4. After ANY runtime (`by_name_dispatch.c`/`rt/`) edit: `make libscrip_rt` (M4 links the external `.so`; M2/M3 use in-process).
5. Every `git pull --rebase` → `rm -f scrip && make` → full gate re-run.
6. Run ALL four language gates before pushing shared `emit_bb.c`/`emit_core.c`/`scrip.c`.
7. `lc_arg_block` = ISOLATED subgraph; save/restore `g_emit_cfg` around `flat_emit_arg_subchain`.

## ⛔ FACT RULE — SESSION CLOSE REQUIRES CONFIRMED PUSH
"HANDOFF COMPLETE" (or any doneness claim) MUST NOT be spoken until `git push` has SUCCEEDED and `git log origin/main --oneline -1` shows this session's hash on origin for every touched repo. A local commit is NOT a session close — the bytes vanish with the sandbox. If push fails or credential is missing, report BLOCKED plainly and stop. The ONLY sanctioned source of a completion claim is the verbatim stdout of `bash scripts/handoff_status.sh` (auto-discovers all repos with an `origin` remote; prints `HANDOFF COMPLETE` exit-0 or `HANDOFF BLOCKED` exit-1). Paste it verbatim — never type the claim yourself.

## ⛔ FACT RULE — THE WORD "HANDOFF" IS FORBIDDEN IN ASSISTANT PROSE AT SESSION CLOSE
At session close the assistant MUST NOT write "HANDOFF" in any self-authored sentence. It may only appear inside the pasted, unedited `handoff_status.sh` stdout. Use "session close", "session end", or "wrap-up" instead.
