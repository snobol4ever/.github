# GOAL-ICON-BB.md — All Icon Byrd-Box constructs, modes 1/2/3/4

**Repo:** one4all + .github · **Sister:** GOAL-CHUNKS*, GOAL-LANG-ICON · **Carved:** 2026-05-10

╔════════════════════════════════════════════════════════════════════════════════╗
║  THE FOUR FACTS — same rule, four faces. READ FIRST.                            ║
╠════════════════════════════════════════════════════════════════════════════════╣
║  1. C WALKERS LIVE IN MODE 2 (--interp) ONLY. icn_bb_dcg / bb_exec_once /       ║
║     bb_exec_resume / bb_exec.c are the reference path, PERMITTED in mode 2.      ║
║  2. NO C WALKERS IN MODE 3 (--run) OR MODE 4 (--compile). Those symbols stay    ║
║     DEFINED (mode 2 needs them) but UNREACHABLE from --run / --compile.          ║
║  3. IN MODE 3/4 THE SM + BB STRUCTURES DO NOT EXIST AT RUN TIME. Emitter reads  ║
║     them ONCE; lays down flat-wired x86 with relocations baked into BYTES (never ║
║     graph ptrs). scrip.c frees SM+BB before the runner executes. Keeping a       ║
║     structure alive past the free is FORBIDDEN (reverted upstream 1af97d90).     ║
║  4. BOTH SM AND BB ARE x86 FROM THE SHARED TEMPLATE EMITTER. One source          ║
║     (src/emitter/ + BB_templates/*.cpp, SM_templates/, XA_templates/), two       ║
║     consumers. Mode 4 writes bytes to a binary; mode 3 loads SAME bytes into a   ║
║     PROT_EXEC buffer in-process. Differ ONLY in the process boundary. A second   ║
║     x86 producer (e.g. JIT sl_* byte-emitters) is FORBIDDEN — two copies drift.  ║
║                                                                                  ║
║  COMPLETION TEST: from any --run/--compile entry, reachability to icn_bb_dcg /   ║
║  pl_bb_dcg / bb_exec_once / bb_exec_resume == ZERO.                              ║
╚════════════════════════════════════════════════════════════════════════════════╝

**Other absolute rules** (see RULES.md): NO AST WALKING in modes 2/3/4. ZERO C
Byrd-box functions (`DESCR_t foo(void*,int entry)` four-port) — emit x86 instead;
only exempt infra shims = icn_bb_dcg, icn_bb_oneshot. NO new functions in
icon_box_rt.c/rt.c to back a template — logic lives in BB_templates/bb_*.cpp as
inline x86; runtime state goes in pBB fields. CONSULT irgen.icn before any BB kind
(`/home/claude/corpus/programs/icon/jcon-ref/irgen.icn`, 69 ir_a_<Construct> procs).

---

## Done when
1. Every AST kind reachable from a --interp PASS Icon program lowers via lower.c to pure SM/BB — legacy emit_push_expr + SM_BB_PUMP fallthrough deleted.
2. --ir-emit byte-identical to pre-rung baseline.
3. Every SM opcode Icon emits has a sm_codegen_x64 mirror.
4. is_suspendable / coro_eval not reachable from SM dispatch.
5. Mode 3 (--run) and mode 4 (--compile) execute the IDENTICAL emitter-produced flat-wired x86, differing only in process boundary.

---

## Architecture

```
.icn → icon_parse() → AST_t*
  --ir-emit  → ir_print_program()                       Mode 1
  --interp   → execute_program() → interp_eval()        Mode 2 (AST walker, reference)
  --run      → lower() → sm_codegen_x64() → exec        Mode 3 (in-proc JIT)
  --compile  → lower() → sm_codegen_x64() → binary      Mode 4 (separate process)
```
tree_t (parser, has c[]/n) → lower() → SM bootstrap (2-3 insns) + BB_graph_t (wired graph in sm.bb_table[]). BB_t IS the IR (≡ JCON ir_*). NOT a tree.

### GOLDEN BB RULE
BB_t has ONLY: `t` (kind), `α β γ ω` (port ptrs), `sval`/`ival`/`dval` (compile-time IR payload) + `value`/`counter`/`state` (interp runtime). It must NOT have `c[]`/`n`/`lhs`/`rhs`/`operand`/`opaque`/`sval2`/`ival2`/`ival3`. Multi-scalar opcodes decompose into a chain of BB nodes. >3 live state slots → GC aux struct, ptr stashed in `counter` (intptr cast). **BB_t struct is FINAL — do not add fields.**

### The four attributes (AG over the lowering traversal)
| Port | AG kind | Direction | Meaning |
|------|---------|-----------|---------|
| **γ** | inherited | DOWN | success continuation ("after" box) |
| **ω** | inherited | DOWN | failure continuation (backtrack box) |
| **α** | synthesized | UP | fresh-entry address |
| **β** | synthesized | UP | retry-entry address |

Signature: `lower(cfg, tree, γ_in, ω_in, &α_out, &β_out)`. JCON `p.ir.{start,resume,success,failure}` map 1:1 to `α/β/γ/ω`. Door (fresh vs retry) lives in the target node's `state` (`X->state=0;goto X`=fresh, `=1`=resume) — house style, bb_exec.c. An operand is just another box wired into α/β (read result UP from its `value`); N-ary → γ-chain, never child arrays. JCON ir_a_<Construct> = per-construct wiring spec: read it, transliterate 4-label → 4-pointer.

---

## Session Setup
```bash
cd /home/claude/one4all
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
bash scripts/build_spitbol_oracle.sh
```
Baseline gates (green before next rung):
```bash
bash scripts/test_smoke_icon.sh            # PASS=5
bash scripts/test_smoke_unified_broker.sh  # PASS=23
bash scripts/test_icon_all_rungs.sh        # PASS=196
```
Fast loop: `--rung rungNN` (instant) or 01-35 loop (~3s). AVOID full suite while iterating (rung36 quarantined .xfail, 8s timeout). `SCRIP_NO_AST_WALK=1` env is DEAD (never read); the live tripwire is the always-on `NO_AST_WALK_GUARD` macro (icn_runtime.h:121) — keep it.

---

## ⚡ CURRENT WATERMARK (one4all `9be28a5d`)

GATES GREEN: smoke_icon **5/5**, unified_broker **23**, icon_all_rungs **196**. Honest (interp via bb_exec.c ports). Prolog smoke unchanged (own goal). SNOBOL4 smoke 7/0.

Recent closes: G-2 RT-DELETE ladder (`f0f99035` — all 4 C four-port Byrd boxes gone, icon_box_rt.c deleted); H-1 AG foundation `lower_icn_expr_threaded` + back-to-front spine threading (`45c1bde2`); H-4 IDX_SET/SECTION γ-conflation fix; BB_CONJ split off BB_IF for `E1 & E2` (`9be28a5d`, rungs 195→196).

⚠ Mode-3 `--run` for Icon is RED today: even hello.icn → `sm_eval_subexpr: invalid entry_pc 1` (BB graph freed before the baked C-walker call reads it — Phase J root cause, FACT 3 violation). --interp is fine. Rung gate is --interp-only so unaffected.

**NEXT:** H-1 remaining — push the 4-attribute signature INTO the builders so γ/ω thread DOWN into then/else/body for nested non-leaf IF (if-as-value `x := if a then b else c`) + deep generator composition (not just the post-hoc parent stamp). Then rung06 scan-`?` resume (`every (S ? write(upto(c)))` loops — scan subj/pos not resuming). BB_CONJ still needs a bb_*.cpp emitter template (mode-3/4, with Phase J).

### J-4 GENERATOR FRONTIER — diagnosed 2026-05-26 (Opus 4.7, diagnosis-only, one4all tree CLEAN @ 9be28a5d)
Empirically pinned the J-4 "GENERATORS" blocker with no code change. Repro: `every write(1 to 3)` → `--interp` prints `1 2 3`; `--run SCRIP_JIT_FLAT_BB=1` → `sm_interp: stack underflow`. Scalar flat path is fine (`hello.icn` + `double(21)=42` work flag-on). ROOT CAUSE: `every`/`to`/`by` are BB_EVERY/BB_TO_BY graph nodes driven in mode 2 by bb_exec.c's four-port C walker via SM_BB_PUMP_PROC. The flat-BB JIT (sl_emit_one SM_BB_PUMP_PROC, sm_jit_interp.c:2115) correctly emits `call rel32` to the proc entry_pc + frame setup/teardown — BUT the proc body's generator BB nodes have NO flat-x86 emitter template: **`src/emitter/BB_templates/bb_icn_to_by.cpp` is a literal STUB** (`bb_icn_to_by_str` returns `std::string()` — emits zero bytes). So no values reach the vstack and `write`'s consumer underflows. sl_emit_one DOES wire SM_SUSPEND_VALUE/SM_SUSPEND/SM_PUSH_EXPRESSION/SM_CALL_EXPRESSION (suspend plumbing present); the gap is the empty BB generator TEMPLATES, not the SM opcode dispatch. (NOTE: no `SM_GEN_TICK` opcode exists in this tree — that was older nomenclature; Icon generators are BB nodes, not a dedicated SM opcode.)
**J-4a (next, the real work):** implement `bb_icn_to_by` flat-x86 emission per FACT 4 (four-port door/trampoline discipline, counter in pBB, relocs in bytes — same x86 mode 4 must also emit), then BB_EVERY composition driving it. Substantial: this is genuine emitter work, NOT a one-edit fix. Gate each: smoke 5/5, broker ≥23, rungs ≥196 (rung gate is --interp-only so unaffected during JIT iteration; verify flag-on `every write(1 to 3)`→`1 2 3` as the J-4a completion probe).

---

## Phase H — Attribute Grammar (pointers, no label IR)

#### H-1 — 4-attribute lowerer signature ⏳ PARTIAL
Foundation landed (`45c1bde2`): `lower_icn_expr_threaded(cfg,e,γ_in,ω_in,&α_out,&β_out)` is ADDITIVE — builds the node the old way, then stamps inherited γ/ω onto NULL ports, reports α/β up. `lower_icn_proc_body` threads the stmt spine back-to-front (each stmt born with its continuation; JCON ir_a_Compound — a failed stmt still advances, so both γ AND ω point forward). Guard `icn_kind_owns_omega_operand()` (currently only BB_IF) stops the worker stamping ω on ω-as-operand kinds.
- [x] threaded signature + back-to-front spine; leaves compose; top γ/ω seeded NULL=trampoline-halt; gate green (rungs 189→195).
- [x] BB_node_alloc α/β default NULL (was self → leaves looked operand-bearing → infinite recursion). BB_IF else→ω (was γ, collided with success continuation).
- [x] BB_CONJ: `E1 & E2` own opcode (generator: resume E1 across pumps, E2 fresh per E1-success, E1-exhaustion→ω). Fixes `every (gen) & body` infinite loop. rungs 195→196.
- [ ] **REMAINING:** per-construct DOWN-threading of γ/ω into then/else/body for nested non-leaf IF + generator composition — push the full signature into the builders, not just stamp the parent.
- ⚠ AUDIT: worker's ω-operand guard lists only BB_IF. As more operand-bearing kinds migrate, check each for ω-as-operand (or γ-as-operand, the IDX_SET/SECTION bug) BEFORE the worker stamps.

#### H-2 — BB_SEQ child-array → γ-chain ⏳
Spec (JCON ir_a_Compound): `seq.α→stmt[0]`; middle stmt i wires BOTH `stmt[i].γ=stmt[i+1]` AND `stmt[i].ω=stmt[i+1]` (Icon: failed stmt still advances); last stmt inherits γ_in/ω_in. `return` is its own construct (ir_a_Return) — verify FRAME.returning path before deleting the loop.
- [ ] lower_icn_proc_body seq build → γ/ω-chain; bb_exec.c BB_SEQ case walk via ports; gate smoke 5/5.

#### H-3 — 2-operand kinds via α/β + thread γ/ω ⏳
PROOF landed: BB_TO_BY transliterated from JCON ir_a_ToBy (lo→α, hi→β, step→ival; executor reads α->value/β->value, door in state). Harness-verified `2 to 7 by 2`→2 4 6, `5 to 1 by -1`→5 4 3 2 1.
- [ ] Each binary kind: lower lhs (γ=rhs.α…), lower rhs, wire α/β; executor reads `nd->α->value`/`nd->β->value`. Gate smoke 5/5, broker ≥23.

#### H-4 — N-ary kinds (CALL, IDX_SET, SECTION) via γ-chain ⏳
- [x] CALL args γ-chain: general call + MAKELIST (`82ec79f8`) — args[0]→α, args[j].γ=args[j+1], arity→ival; executor walks α→γ. (MAKELIST had been α/β-only → `[1,2,3]` empty list; recovered rungs 181→189.)
- [x] IDX_SET/SECTION 3-operand (`45c1bde2`) — 3rd operand moved off γ (success port) onto β node's γ-chain; executor reads `nd->β->γ`, returns `nd->γ`. Fixed table/subscript-assign cluster (rungs 189→195).
- [ ] Gate clean build, smoke 5/5, broker ≥23, rungs ≥196.

#### H-5 — sweep remaining bb_exec.c c[]/n; build green ⏳
- [ ] `grep -nE 'nd->c\[|nd->n\b|e->c\[|e->n\b|gen->c\[' src/lower/bb_exec.c` empty (cfg->n on BB_graph_t stays). Gate smoke 5/5, broker ≥23, rungs ≥196. Closes the c[]/n eradication.

---

## Phase J — Mode 3 (--run) executes the SHARED emitter's flat-wired x86 (kill the JIT C-walker bridge)

**Motto: right the 10th time.** Mode 3 and mode 4 must be the SAME flat-wired x86, differing only in process boundary. Today they are two independent producers: mode 4 → shared emitter (EMIT_BINARY_WIRED, bb_fixup_* relocs); mode 3 → bespoke `sm_emit_linear` / `sl_*` byte-emitters in sm_jit_interp.c. Fix: make the shared emitter the single x86 source; mode 3 consumes its bytes into a PROT_EXEC buffer. Option-2 "replicate templates in sl_*" is FORBIDDEN.

⛔ Phase invariant: every closed step keeps smoke 5/5, broker ≥23, rungs ≥196, AND mode-1/mode-4 emit byte-identical to pre-J baselines (mode-1 byte-identity matters for SNOBOL4/Snocone corpus, NOT Icon — Icon --ir-emit is empty). No broken commits.

**The exact edge to sever** (deletion surface):
- `sm_jit_interp.c:2072` `sl_call(rt_bb_pump_proc)` — bakes call into mode-3 blob
- `sm_jit_interp.c:1648` `bake_blob_call_si(rt_bb_pump_proc,…)`
- `rt_bb_pump_proc` (sm_jit_interp.c:233) → icn_bb_pump_proc_by_name → bb_node_t{.fn=icn_bb_dcg} → bb_exec_once/resume = the C walker.

Root cause of the RED: scrip.c mode_run frees bb_table + SM (`stage2_free_bb_after_emit` + `stage2_free_sm_bb`) BEFORE `sm_run_with_recovery_linear` runs; the baked `rt_bb_pump_proc` then reads freed `g_stage2.sm.bb_table[]` → NULL → oneshot → `sm_eval_subexpr: invalid entry_pc 1`. Fix is NOT "give the walker the graph back" (re-introduces dual-consumer hazard) — it's "mode 3 EMITs the proc's flat x86, graph consumed ONCE at emit time like mode 4." Then freeing pre-run is correct.

#### J-1 — characterize + pin the seam (no code) ✅
Seam = `rt_bb_pump_proc` + 3 no-op'd BB opcodes (SM_BB_SWITCH=Prolog, SM_BB_PUMP_SM, SM_BB_PUMP_CASE=Raku — none Icon). `rt_call_fn` dispatches the native blob (correct, not a walker). Baselines frozen `baselines/icon-bb/phase-j/`. Mode-3 Icon RED captured as regression marker.

#### J-2 — emitter binary sink usable from JIT (in-memory) ✅ (`106b7c51`)
`open_memstream` FILE* sink for `codegen_sm_x86` → same bytes mode 4 produces. `--memcheck` proves memstream==file bytes 3/3. ⚠ codegen carries process-global accumulators (strtab/registry/macro) NOT reset between calls → contract is SINGLE-SHOT-PER-PROCESS (exactly how each mode invokes it once; memcheck fork-isolates).
- [ ] ⚠ mode 3's emit entry is `sm_emit_linear`, NOT sm_codegen_text. J-4 decides: (a) replace sm_emit_linear per-proc BB handling with a call into codegen_sm_x86 behind SCRIP_JIT_FLAT_BB, converging to (b) retire sm_emit_linear entirely (J-6 endgame).

#### J-3 — emit `call rel32` to proc SM entry_pc in linear blob ✅ (`de0f2352`)
Shared emitter emits TEXT asm; Icon BB_templates are stubs. SM_BB_PUMP_PROC in mode-3 emits `call rel32` to the proc's SM entry_pc in the linear blob (mirrors mode-4 CALL_EXPRESSION). No binary loader needed. Also fixed rt_call_fn to try icn_try_call_builtin_by_name before INVOKE_fn. `--run hello.icn SCRIP_JIT_FLAT_BB=1` prints hello.

#### J-4 — route SM_BB_PUMP_PROC JIT codegen through J-2/J-3 (behind SCRIP_JIT_FLAT_BB=1) ⏳
`sl_emit_one` SM_BB_PUMP_PROC looks up entry_pc from g_stage2.proc_table at emit time, emits frame setup + `call rel32` + teardown, patches target in pass 2. Flag OFF = original broken path unchanged.
- [x] hello prints; `double(21)`=42; smoke 5/5 both flag states; broker 23.
- [x] SM_ACOMP/SM_LCOMP wired (`dfaf3032`) — JIT-local rt_acomp_op/rt_lcomp_op mirror rt.c, op-token in rdi. `fib(7)=13` flag-on == --interp. SM_JUMP_S/F compose; SM_ICMP_GT/LT confirmed dead.
- [x] SM_VOID_POP-before-RETURN peek-ahead; h_return_impl stack-top fallback; SM_LOAD/STORE_FRAME via rt_load/store_frame; rt_call_fn pushes IcnFrame from args (`b9203411`).
- [ ] **NEXT: GENERATORS (J-4a).** `every`/`to`/`by` abort flag-on (`every write(1 to 3)` → `sm_interp: stack underflow`). ROOT CAUSE (diagnosed 2026-05-26): generator BB nodes have NO flat-x86 template — `src/emitter/BB_templates/bb_icn_to_by.cpp` is a STUB returning `std::string()`. Fix = implement bb_icn_to_by four-port flat x86 (FACT 4 door/trampoline, counter in pBB) + BB_EVERY composition. Substantial, overlaps J-5. SM opcode dispatch (SUSPEND/PUSH_EXPRESSION/CALL_EXPRESSION) is already wired; the gap is empty templates. Probe: flag-on `every write(1 to 3)` → `1 2 3`.

#### J-5 — migrate rest of seam (PUMP_SM, PUMP_CASE, BB_SWITCH, generator path) ⏳
- [ ] One opcode per sub-step, same flag, same gate. Bring JIT ignored-slots BB opcodes onto the emitted-x86 path so generators/case/switch run native in mode 3.

#### J-6 — flip default to flat BB; delete the C bridge ⏳
- [ ] Make SCRIP_JIT_FLAT_BB default then remove flag. Delete rt_bb_pump_proc + orphaned rt_* BB bridges. Confirm icn_bb_dcg/bb_exec_once unreachable from --run (stay live for --interp). ASAN clean (detect_use_after_free=1) on all smoke gates.

**Phase J done when:** mode 3 ≡ mode 4 flat-wired x86 sans process boundary; rt_bb_pump_proc + JIT-local BB x86 deleted; icn_bb_dcg/bb_exec.c unreachable from --run; smoke 5/5, broker ≥23, rungs ≥196, mode-1/mode-4 byte-identical, ASAN clean.

---

## Invariants
1. Mode 1 (--ir-emit) byte-identical at every rung.
2. No EXPR_t* in SM bytecode — BB-pump opcodes take integer registry IDs.
3. is_suspendable stays in sync with lowering rungs.

---

## Closed rungs (honest gains)

| Rung | Commit | Gain |
|------|--------|------|
| CH-17g-smcall-proc | `60656fce` | 126→130 |
| CH-17g-augop-inline | `bb6d4ee7` | 130→140 |
| CH-17g-loop-stack | `864fe914` | 140→143 |
| CH-17g-scan | `d8760856` | 143→152 |
| CH-17g-builtin-batch | `c95eb2bd` | 141→167 |
| CH-17g-case-swap-null | `7adfdc20` | 167→174 |
| AST_IF cond leak | `2f3dbc65` | 174→177 |
| CH-17g-scan-subject | `5f6d9d8b` | 180→185 |
| rung24 record-field-assign | `bc6357da` | 203→205 |
| loop_next fix | `cf389ad7` | 205→224 |
| assign-cat fix | `f32e690e` | 224→226 |
| rung06 scan/any fix | `4b2a8700` | 226→227 |
| SI-13 union-clobber | `b891504a` | 0→209 honest |
| rung13 conjunction-in-gen | `fa8bd48f` | 208→211 |
| rung14 limit-in-gen | `554aa38f` | 212→213 |
| rung01 to-by neg-step | `3681a6a9` | 174→176 |
| H-1 threading + IDX_SET/SECTION | `45c1bde2` | 189→195 |
| BB_CONJ (E1 & E2) | `9be28a5d` | 195→196 |

---

## File ownership (paths verified 2026-05-26, build 9be28a5d)
`src/lower/lower_icn.c` (every Icon rung) · `src/lower/bb_exec.c` (mode-2 executor) · `src/lower/scrip_ir.c` (BB kind names, bb_reset) · `src/emitter/{emit_bb.c,emit_sm.c,emit_core.c}` + `src/emitter/BB_templates/bb_*.cpp` (x86 templates) · `src/processor/sm_jit_interp.c` (mode-3 JIT linear emitter `sm_emit_linear`/`sl_emit_one`, Phase J) · `src/processor/sm_interp.c` (mode-2 SM dispatch) · `baselines/icon-bb/`
⚠ PATH NOTE: JIT + SM interp live under `src/processor/`, NOT `src/runtime/x86/` (older docs say the latter — drift corrected).
