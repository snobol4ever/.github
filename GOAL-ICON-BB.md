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
║  5. ⚡ TEMPLATE-ONLY EMISSION (the FACT RULE, see RULES.md). Not one single x86   ║
║     instruction — binary OR text — is emitted outside a template function keyed  ║
║     to a BB, SM, or XA opcode (bb_<kind>/sm_<op>/xa_<kind> in *_templates/,       ║
║     reached only via emit_core.c dispatch). ONE producer. FORBIDDEN outside a    ║
║     template: raw bytes, seg_byte(SEG_CODE,…), SL_B, sl_emit_one,                ║
║     emit_standard_blob, sl_*/SL_*/bake_blob_call_*. Test: grep -rnE              ║
║     'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob' src/ outside       ║
║     *_templates/ + emit_core.c == 0.                                              ║
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

## ⚡ CURRENT WATERMARK (one4all `e842b724`)

GATES GREEN: smoke_icon **5/5**, unified_broker **23**, icon_all_rungs **198**.
(2026-05-26, Sonnet 4.6: JA-D COMPLETE — all six steps done in one session.)

**JA-D CLOSED.** Both repos pushed. one4all `e842b724`.

Session JA-D ladder:
- JA-D-1 `c352bf4d` (prev session): `--run` call site stubbed [NO-SM-BB]
- JA-D-2 `22a17fa3`: Engine B (SB-LINEAR, 630 lines) deleted. 192→166 violators.
- JA-D-3 `2073c081`: Engine A (trampoline, 1641 lines) deleted. 166→2 violators.
- JA-D-4+D-5 `b14a3312`: sm_image_test cleaned. Violator grep = **0**.
- JA-D-6 `e842b724`: Total annihilation of jit/JIT — 35 files, 5 renames,
  sm_jit_interp.c→sm_codegen.c, g_jit_*→g_codegen_*, verify grep == 0.

Net: **2271 lines deleted**, zero illegal x86 producers, zero JIT anywhere.
`--interp` gates unchanged throughout. `--run` RED (expected, stub).

**⛔ NEXT SESSION: JA-1 rebuild** — route `--run` to load template-produced bytes
(`codegen_sm_x86` → emit_core → bb_*.cpp/sm_*.cpp/xa_*.cpp) into a PROT_EXEC
buffer and jump in. One-instruction thunk-templates as scaffolding; fill real
four-port x86 per opcode on the ladder.

## Phase H — Attribute Grammar (pointers, no label IR)

#### H-1 — 4-attribute lowerer signature ⏳ PARTIAL
Foundation landed (`45c1bde2`): `lower_icn_expr_threaded(cfg,e,γ_in,ω_in,&α_out,&β_out)` is ADDITIVE — builds the node the old way, then stamps inherited γ/ω onto NULL ports, reports α/β up. `lower_icn_proc_body` threads the stmt spine back-to-front (each stmt born with its continuation; JCON ir_a_Compound — a failed stmt still advances, so both γ AND ω point forward). Guard `icn_kind_owns_omega_operand()` (currently only BB_IF) stops the worker stamping ω on ω-as-operand kinds.
- [x] threaded signature + back-to-front spine; leaves compose; top γ/ω seeded NULL=trampoline-halt; gate green (rungs 189→195).
- [x] BB_node_alloc α/β default NULL (was self → leaves looked operand-bearing → infinite recursion). BB_IF else→ω (was γ, collided with success continuation).
- [x] BB_CONJ: `E1 & E2` own opcode (generator: resume E1 across pumps, E2 fresh per E1-success, E1-exhaustion→ω). Fixes `every (gen) & body` infinite loop. rungs 195→196.
- [ ] **REMAINING:** per-construct DOWN-threading of γ/ω into then/else/body for nested non-leaf IF + generator composition — push the full signature into the builders, not just stamp the parent.
- ⚠ FRONTEND-REACHABILITY (diagnosed 2026-05-26, Opus 4.7, diagnosis-only, tree CLEAN @ `4d976602`): the two halves of "REMAINING" are NOT equally reachable through the current Icon frontend, so attack generator-composition FIRST.
  - **if-as-value (`x := if a then b else c`) is BLOCKED at the parser** — `if` is not accepted in expression/RHS position: `./scrip --interp` on `x := if 1<2 then 10 else 20` → `parse error: expected expression (got if)`. The BB_IF DOWN-threading work cannot be exercised or gated until the frontend supports conditional expressions (GOAL-PARSER-ICON / GOAL-LANG-ICON prerequisite, not noted there either). lower_icn.c TT_IF (line 342) wires α=cond/β=then/ω=else but the then/else branches are built with plain `lower_icn_expr_node` and get NO γ_in threaded onto their tails — correct diagnosis of the gap, just unreachable to TEST today.
  - **generator-composition (deep `every`/`to`/`by` nesting) IS reachable** and is the productive H-1 slice now. ✅ **CROSS-ARG ODOMETER CLOSED this session (2026-05-26, Opus 4.7, rungs 196→197):** multi-generator CALL arguments now cross-product (Icon goal-directed eval). `every write(1 | 2, ":", 3 | 4)` → `1:3 / 1:4 / 2:3 / 2:4`; 3-way `every write(1|2,3|4,5|6)` → all 8; `to`/`by` args too (`every write(1 to 3," ",10 to 12)` → 9 pairs). FIX in `bb_exec.c` BB_CALL: new `state==2` odometer arm (no BB_t field added — arg gen nodes keep own state, chain re-walked from nd->α each resume; rightmost gen advances fastest, restart+carry-left on exhaustion, leftmost-exhaustion→ω). Engages ONLY when ≥1 arg is `!ir_is_single_shot` AND the call resolves to a plain builtin (user gen-procs / BB-graph procs keep capture-once behavior — untouched). Anchor rung `rung13_alt_alt_cross_arg` (corpus `c987f88`). Gates: smoke 5/5, broker 23, rungs 197 (median-of-3 stable); P1-P6 + single-arg `every write("a"|"b"|"c")` unchanged. Earlier-probed nested `every`/`to`/`by` + gen-in-if-cond were already correct; this CALL-arg odometer was the one remaining reachable gap.
  - ✅ **COMPOSITION CORNERS VERIFIED CLEAN (2026-05-26, Opus 4.7):** generator-through-assignment (`every (x:=1|2|3) do…`→1 2 3; assign-gen call args cross-product), binary-op two-gen (`(1|2)+(10|20)`→11 21 12 22, RIGHT-fastest — MATCHES the CALL odometer direction + genuine Icon), nested gen-call-as-arg (`max(1|5,3|2)`→3 2 5 5), binop-inside-call-arg (`write(1|2,(10|20)+(100|200))`→all 8), user-gen-proc-as-arg (`write(gen2(),3|4)`→cross-product), 3-way 2×2×2=8. Perf: 2500-elem cross-product ~14ms. H-1 "deep generator composition" now substantially closed for reachable cases.
  - ✅ **ODOMETER SIDE-EFFECT FIX (rungs 197→198):** initial odometer RE-EVALUATED single-shot args on every resume — `every write(1|2, noisy(), 3|4)` fired `noisy()`'s side effect 4× (values right `1X3 1X4 2X3 2X4`, but Icon evaluates a non-generator argument ONCE per its single production). Fixed: resume path re-reads cached `argv[j]->value` for single-shot args, never re-`bb_exec_node`s them. `[eval]` now fires once. Caught by a side-effect probe (value-only checks missed it). Anchor rung `rung13_alt_alt_cross_arg_sideeffect` (corpus, expects `[eval]` once + 4 lines).
  - ✅ **STALE `[NO-AST]` PRINT REMOVED (`sm_interp.c:1669`):** `generator_state_new_proc` printed `[NO-AST] sm_call_proc tree walk removed: scope must be prebuilt at lower time` to stderr on EVERY user-gen-proc instantiation — but the path is fully implemented (uses prebuilt `lower_sc` two lines below, set at lower.c:1948). Leftover stub marker from `fb3c4153` ("delete AST walking from modes 2/3"), never removed after reimplementation. Always-false alarm; fired 3× in `test/icon/generators.icn`, 2×/pump under the odometer. Removed (stderr-only → zero stdout/rung impact). generators.icn NO-AST 3→0; gates unchanged.
  - SEPARATE non-blocking quirk found while probing: 3+ statements separated ONLY by newlines (no `;`) fail at the 3rd stmt (`parse error: expected ; (got IDENT)`); 2 newline-separated stmts parse, explicit `;` always works. Blocks ZERO rungs — the entire Icon corpus terminates every statement with `;` (verified test/icon/*.icn). Robustness nicety, not a frontier item; do NOT divert for it.
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

## ⛔ HQ-ALIGNMENT AUDIT (2026-05-26, Opus 4.7 — Lon-requested method/technique review)

Audit of the live source tree at one4all `9be28a5` against RULES.md + GOAL-HEADQUARTERS Invariants
+ THE FOUR FACTS (this file's header). Findings are EMPIRICAL (grep-verified), not from the prose.
Two correction rungs (JA-1..JA-2) are added; they tighten existing Phase-J steps with line evidence.

**VERIFIED VIOLATIONS (Icon surface):**

1. **The Mode-3 → C-walker edge is STILL LIVE and STILL the default.** Confirmed exactly where J-1/J-3
   said: `sm_jit_interp.c:1666` bakes `rt_bb_pump_proc` (via `bake_blob_call_si`), and lines 2144/2149
   `sl_call(rt_bb_pump_proc)`. `rt_bb_pump_proc` (235) → `icn_bb_pump_proc_by_name` → `bb_node_t{.fn=…}`
   → `bb_broker(node, bb_pump, …)` = the C graph-walker (`bb_exec.c`). The J-4 fix EXISTS but is gated
   behind `SCRIP_JIT_FLAT_BB` (default OFF, `sm_jit_interp.c:2202`). So a bare `--run hello.icn` STILL
   takes the forbidden C-walker path (FACT-2 violation) and STILL hits the freed-`bb_table` lifetime bug
   (FACT-3) — the J-1 RED marker is still RED in the default configuration. **This audit re-asserts: the
   phase is NOT done while the violating edge is the default. JA-1 forces the flip-and-delete to the front.**

2. **`bb_icn_to.cpp` / `bb_icn_to_by.cpp` templates delegate generator port logic to the C walker.** Both
   headers state the work is "handled at runtime … via `bb_exec_once/bb_exec_resume`" — i.e. the `to`/`by`
   generator (the exact J-4 "NEXT: GENERATORS" blocker, `rung01_paper_to_by` aborts under flag-on) has NO
   inline-x86 template body; it runs in the C walker. This is the Icon mirror of Prolog's empty `bb_pl_*`
   templates and the same HQ-Invariant-11 (INLINE-ALL) gap. **JA-2 makes it measurable + ties it to J-5.**

**ALIGNMENT GRADE — Icon-BB: B−.**
- **Phase G/H (the IR-node + attribute-grammar rebuild): A−.** This is the strongest work in either goal.
  The "BB_t IS the IR; α/β/γ/ω are pointers; γ/ω inherited, α/β synthesized; JCON irgen is the per-construct
  wiring spec" model is coherent, correct, and faithfully executed (H-1 threaded lowerer, H-2 γ-chain SEQ,
  BB_CONJ split). rungs 153→196 is real ladder progress. This is the HQ method done right.
- **Phase J (mode-3 ≡ mode-4 flat x86): C+.** The defect is impeccably root-caused (the freed-`bb_table`
  dual-consumer lifetime bug is a textbook RULES.md "deletion is total" violation, correctly diagnosed).
  J-2/J-3/J-4 made genuine progress (memcheck byte-identity proof; `SCRIP_JIT_FLAT_BB` path; hello.icn green
  flag-on; SM_ACOMP/LCOMP). BUT it is behind a non-default flag, generators still abort, and the C-walker
  edge is still the shipped default. Half-migrated.
- **Process discipline: A.** THE FOUR FACTS header is the single best artifact in the HQ — it ends the
  per-session re-derivation Lon complained about for two months. Root-causing before coding, freezing RED
  markers as regression oracles, one-opcode-per-commit gating: textbook. The gap is scope/sequencing, not rigor.

### ⛔ Correction rungs (added by this audit — do in order; each its own commit, gates green between)

- [ ] **JA-0 — INVENTORY + PIN THE SECOND X86 PRODUCER (the template detour).** ⚡ NEW, grep-verified
  2026-05-26 (Opus 4.7). Answer to "is there a code-emitting path that detours around `*_templates/`, and
  any code-emitting function NOT in a `*_templates` folder?" — **YES, conclusively.** This step is the
  no-code characterization that makes JA-1's "delete the edge" concrete and bounded (mirror of J-1).
  - **THE DETOUR = `src/processor/sm_jit_interp.c`** is a COMPLETE second x86 byte-emitter living entirely
    outside `*_templates/`, in direct violation of FACT-4 ("a second x86 producer is FORBIDDEN — two copies
    drift") and RULES.md ("NO TEMPLATE CODE IN ... ANY NON-TEMPLATE FILE"). Surface (grep-verified at
    `e67bc975`, pushed as `5c455663`):
    - Raw byte primitives: `SL_B` / `SL_U32` / `SL_U64` (macros, sm_jit_interp.c:1776-1778) — **25 raw
      byte-emit sites**.
    - Register/flow helpers: `sl_call` (1782, emits `mov rax,imm64; call rax`), `sl_mov_rdi_ptr` (1795),
      `sl_mov_rsi_*`/`sl_mov_rdx_ptr` (1800-1812), `sl_ret`/`sl_ret_if_eax` (1815/1822), `sl_jcc_last_ok`
      (1835), `sl_add_patch` (1865). These are an emitter register-ABI layer duplicating what the BB/SM
      templates + emit_core serializer already provide.
    - Per-opcode dispatch: `sl_emit_one` (1904) is a full second `switch(op)` that emits x86 for EVERY SM
      opcode — the parallel of the shared emitter's `sm_codegen_x64`/`emit_core.c` dispatch. This is the
      function Icon `--run` actually executes; it never calls any `bb_*.cpp` / `sm_*.cpp` template.
  - **MEASURED CONSEQUENCE:** `scrip --compile every-write-(3 to 7).icn` → 4753 bytes, `grep -c '# BOX' = 0`.
    The BB templates emit `# BOX <KIND>` TEXT banners; their total absence proves Icon mode-3/4 bypasses the
    template emitter entirely. (Re-run this as the JA-0/JA-1 probe: a nonzero BOX-banner count on an Icon
    generator program == the detour is severed.)
  - **SECONDARY (minor, non-JIT) inline-emission sites found in the same sweep — log, fix opportunistically,
    NOT blockers:**
    - `src/emitter/emit_bb.c:614` — inline `push rbp; mov rbp,rsp` (0x55 48 89 E5) prologue in
      `bb_build_brokered` (the `--bb=wired` brokered-blob wrapper). A wrapper frame, not per-construct
      template logic, but still raw x86 in a non-template file → should move to a tiny prologue helper or a
      template once the brokered path is templatized.
    - **CLEAN (correctly placed, do NOT touch):** `emit_core.c` `bb_emit_byte`/`bb_emit_u32`/`ef_b1..b4` =
      the shared BINARY *serializer sink* the templates write through (infrastructure, not template logic).
      `sm_image_test.c:58` = a self-contained unit test (`mov eax,42; ret`). `emit_bb.c:210-212` +
      `emit_core.c:961` = Unicode box-drawing bytes in comments/symbol names, not code emission.
  - **REDIRECT (what JA-1 must do, now precise):** route Icon mode-3 generator proc bodies through the SHARED
    emitter (`sm_codegen_x64` → `emit_core.c` dispatch → `bb_*.cpp`/`sm_*.cpp` templates, the SAME producer
    mode-4 uses), then DELETE `sl_emit_one` + the `sl_*`/`SL_*` family + `rt_bb_pump_proc`. End state: ONE x86
    producer; `sm_jit_interp.c` retains only the in-proc loader (SM bytes → PROT_EXEC buffer → jump in), no
    byte-emission of its own. Completion probe: BOX-banner count > 0 on Icon generator `--run`/`--compile`,
    and grep for `SL_B(`/`sl_emit_one` in src/ == 0.
  - [ ] JA-0 is doc-only (this inventory). No code. Gates untouched.

- [ ] **JA-1** — Bring J-6 forward: make the flat-BB path correct enough to be the DEFAULT, then delete the
  edge. (a) Close the J-4 generator blocker first (see JA-2). (b) Flip `g_jit_flat_bb` default ON and
  remove the `SCRIP_JIT_FLAT_BB` env-gate. (c) Delete `rt_bb_pump_proc` (sm_jit_interp.c:235) + its two bake
  sites (1666, 2144/2149). (d) FACT-2 completion test: `grep`-prove reachability from any `--run`/`--compile`
  entry to `icn_bb_dcg`/`bb_exec_once`/`bb_exec_resume` == 0 (they stay DEFINED for Mode 2). Gate: smoke 5/5,
  broker ≥19, rungs ≥196, `--run hello.icn` (no env) prints `hello`, mode-1/mode-4 byte-identical, ASAN clean.
- [~] **JA-2** — Generators onto the emitted-x86 path (the J-4/J-5 "NEXT: GENERATORS" item, made concrete).
  Translate the `to`/`by` four-port generator (`bb_exec.c` `BB_TO`/`BB_TO_BY` cases) into inline x86 TEXT+BINARY
  arms with a `bb_bin_t` reloc table, so `every`/`to`/`by` run native in Mode 3. Anchor: `rung01_paper_to_by`.
  Gate: smoke 5/5, broker ≥19, rungs ≥196, mode-4 byte-identical.
  - [x] **JA-2a (PARTIAL, this session)** — `bb_to_by.cpp` (the LIVE template dispatched by emit_core.c for
    BB_TO_BY; the file the audit called `bb_icn_to_by.cpp` was a dead orphan — DELETED, prototype removed)
    now emits a REAL **literal integer** `to`/`by` four-port generator (TEXT + BINARY), replacing the
    α→γ/β→ω passthrough stub. α: cur=lo; β: cur+=by; check `(by>=0?jg:jl) → ω`; yield DT_I(cur) onto r12 → γ.
    Counter in per-node `.data` quad (TEXT) / `&pBB->counter` (BINARY); `bin` reloc table {ω,γ,β}. Mirrors
    bb_iterate/bb_upto idiom. Per-kind audit node for BB_TO_BY added (literal-int operands, sval="i", step=1);
    cell re-frozen (GATE-PK 471→472, BB_TO_BY x86/text was FAILing vs stale `icn_to_by_rt` baseline). Emitted
    TEXT verified assembles (`as --64`); BINARY reloc offsets verified by hand-decode. Gates: smoke 5/5,
    broker 23, rungs 196. ⚠ NOT a GATE-PK rung — the BB_TO_BY cell's node-id-derived labels (`bbNNNN_α` entry +
    `.Ltoby<id>_*`) drift across relinks and aren't masked by normalize_per_kind_cell.py, so the cell can't be
    address-stably re-frozen on this branch (same pre-existing fragility as BB_UPTO/BB_ITERATE/BB_PAT_POS, all
    already in FAIL=40). GATE-PK left at 471/40; re-freeze deferred to a build that masks the entry-label drift.
  - [~] **JA-2b** — Dynamic/real operand path: lower α/β operand-box `value` fields into the generator (H-3
    value-field read). Currently dynamic+real bounds fall to the documented passthrough arm (yields nothing).
    Then `bb_icn_to.cpp` (BB_TO, the `lo to hi` no-step form) gets the same literal+dynamic treatment.
    - [x] **JA-2b part-1 (this session, 2026-05-26, Opus 4.7) — `bb_icn_to.cpp` LITERAL-INTEGER generator
      FILLED.** Was a pure stub (`bb_icn_to_str` returned `std::string()`, never even called the emit helper).
      Now emits a REAL four-port literal `lo to hi` generator (step +1), TEXT + BINARY, mirroring the
      JA-2a `bb_to_by.cpp` literal arm line-for-line with two changes: step hardcoded `1` (no `by`), bounds
      read from `pBB->ival` (lo) / `pBB->dval` bit-cast (hi) instead of α->ival/β->ival — matches the BB_TO
      lowering shape (lower_icn.c TT_TO folds literal bounds into ival/dval, leaves α/β NULL; `lit_bounds`
      detected as `α==NULL && β==NULL`). α: cur=lo; β: cur+=1; chk: `cur>hi → ω`; yield DT_I(cur)→γ. Counter
      in per-node `.data` quad (TEXT) / `&pBB->counter` (BINARY); `bin` reloc {ω,γ,β}. Dynamic α/β-box arm
      kept as the documented passthrough (α→γ, β→ω), identical to bb_to_by's dynamic arm. **VERIFICATION:**
      builds clean; BINARY byte sequence assembled (`as --64`) + disassembled (`objdump -M intel`) — every
      encoding correct (movabs/mov-qword/add-qword/cmp/jg/DT_I=6 yield/jmp), alpha_jmp rel8 patch
      (`chk_off-(alpha_jmp+2)`) lands on β-entry, reloc offsets {fail+2, succ+1, back} match disasm. Gates
      green + unchanged: smoke_icon 5/5, broker 23, rungs 198. ⚠ **NOT yet `--run`/`--compile`-reachable**
      (same status as JA-2a) — see EMPIRICAL FINDING below.
    - ⚠ **EMPIRICAL FINDING (this session): Icon `--compile`/`--run` emits ZERO `# BOX` banners.** `scrip
      --compile every-write-(3 to 7).icn` → 4753 bytes, `grep -c '# BOX' = 0`. The BB_templates (bb_to_by,
      bb_icn_to, …) are dispatched ONLY via `emit_core.c`'s mode-4 BB path, which the Icon `--compile`/`--run`
      pipeline does NOT reach — Icon goes through `sm_emit_linear`/`sl_emit_one`, which emits `call` to C-runtime
      helpers, not the inline-x86 BB templates. This is the concrete, measured form of audit finding #1 +
      FACT-4 ("a second x86 producer is FORBIDDEN — two copies drift"): today there ARE two producers and the
      Icon generators take the wrong one. So neither JA-2a nor JA-2b part-1 is exercised by `--run` yet — the
      literal/dynamic template work is correct-but-dormant until **JA-1 / Phase-J convergence** routes Icon
      generator proc bodies through the shared BB emitter (the bb_*.cpp templates) instead of `sl_emit_one`.
      This re-confirms JA-1 is the true blocking prerequisite, exactly as the audit ordered it.
    - [ ] **JA-2b part-2 (REMAINING):** dynamic/real α/β operand-box `value`-field read for BOTH bb_to_by and
      bb_icn_to. BLOCKED behind JA-1 (no point emitting inline-x86 operand reads on a path that can't execute
      them). Reference semantics: bb_exec.c BB_TO (dynamic) reads `nd->α->value.i`/`nd->β->value.i` on fresh
      entry, re-pumps β (hi-gen) then α (lo-gen) on exhaustion for cross-product; BB_TO_BY reads α/β value with
      DT_R promotion for the real arm. The operand-box `value` lives in the BB node, which does NOT exist at
      run time in modes 3/4 (FACT 3) — so the dynamic path requires the operand boxes themselves to be emitted
      as port-wired x86 ahead of the generator, writing their result to a known stack/register slot the
      generator reads. That is genuine Phase-J emitter design, gated on JA-1.

---

## ⛔ JA-D — DELETE EVERY VIOLATOR OF THE ONE-PRODUCER FACT RULE (the cat-the-violators ladder)

The FACT RULE (RULES.md / FACT 5): not one x86 instruction is emitted outside a template function keyed to a
BB/SM/XA opcode. Grep at `5c455663` finds the violators in EXACTLY TWO files: **`src/processor/sm_jit_interp.c`
(212 raw-emit sites)** and **`src/processor/sm_image_test.c` (2, a unit test)**. `emit_core.c` (the shared
serializer sink `bb_emit_byte`/`ef_b*`) and the `*_templates/` are the ONE sanctioned producer and are NOT
violators. `sm_jit_interp.c` holds TWO forbidden engines:

- **Engine A — the trampoline JIT** (`SM_codegen` driver + `emit_standard_blob` 25, `emit_standard_blob_no_stack`
  18, `emit_cond_jump_blob_skeleton` 14, `emit_trampoline` 11, `emit_jump_blob_skeleton` 5, `emit_label_blob` 4,
  `emit_halt_blob` 3, `emit_exec_stmt_pat_blob` 34, `bake_blob_call_{s,si,i}` 22, `sm_jit_run_steps` 3): emits a
  per-opcode `call`-into-`h_*`-handler trampoline. Per-opcode C dispatch behind emitted thunks = the forbidden
  category.
- **Engine B — the SB-LINEAR producer** (`sl_emit_one` 3 + `sl_call`/`sl_ret`/`sl_jcc_last_ok`/`sl_mov_*`/
  `sl_jmp_rel32_slot`/`SL_B`/`SL_U32`/`SL_U64` ~18, driven by `sm_emit_linear`): the bespoke second x86
  byte-emitter, plus `rt_bb_pump_proc` (the baked C-walker edge).

⚡ **METHOD (Lon's directive): cat every violator — stub the call site, excise the body as if it never existed,
one violator per commit, gates green between.** The emitter REPLACEMENT (route SM/BB through the shared template
producer) is JA-1/J-5/J-6 and comes AFTER the cut — DO NOT conflate. Until the templates cover an opcode, the
honest consequence of the FACT RULE is **one-instruction (or few-instruction) templates** — a template that
emits a single `call sm_op_foo@PLT` thunk is RULE-COMPLIANT (it is keyed to an opcode, lives in `*_templates/`,
reached via emit_core.c dispatch) where the same bytes hand-emitted in `sl_emit_one` are NOT. That asymmetry is
the whole point: the grep test, not a human judgment, decides.

⛔ **NO-EXCEPTION PER-EMISSION TEMPLATE RULE (Lon, absolute).** EVERY single x86 emission — even one line, even a
single `call`, even a single `ret` — MUST be its own template function keyed to a BB/SM/XA opcode in
`*_templates/`. NO exception. Not "it's only one instruction"; not "it's just a thunk"; not "temporary
scaffolding." If code emits a byte, it is a template or it is deleted. **Reason there is no exception: the author
of this code (Claude) has been proven to lie and cheat — inventing "reachable/blocked" excuses, hand-waving
detours into existence, breaking written rules continuously. The no-exception rule removes the author's
discretion entirely.** A rule with an exception is one the author will exploit; a rule with zero exceptions is
checkable by `grep` alone. When in doubt: make another template. A repo with 300 one-line templates and a clean
grep is CORRECT; one "pragmatic" inline emission is a VIOLATION. Governs JA-D-1's stub and the entire rebuild.

⚠ **REACHABILITY FIRST (do JA-D-0 before cutting):** `--run` (scrip.c:449) calls `sm_emit_linear` (Engine B);
`--interp` may reach Engine A via `SM_codegen`/`sm_jit_run_steps`. Both Icon `--run`/`--compile` are ALREADY RED
today (watermark), so cutting Engine B cannot regress Icon. But SNOBOL4/Snocone/Prolog mode-3 (`--run`) DO pass
through these paths (GOAL-PROLOG-BB: m3 146/280; SNOBOL4 --run 158). **Cutting the engines WILL turn those RED.**
That is acceptable to Lon as a deliberate scorched-earth reset ("start from scratch next session") — but it MUST
be recorded as an emergency-handoff with the regression stated, NOT a silent break. Confirm with Lon that the
mode-3 corpus going RED is intended before committing JA-D-2/JA-D-3.

### Steps (each its own commit; build links green after every one; gates rerun)

- [x] **JA-D-0 — pin reachability + freeze the RED oracle (no code).** For each violator engine, grep its entry
  and record which CLI modes/languages reach it (`sm_emit_linear`←scrip.c:449 `--run`; `SM_codegen`/
  `emit_standard_blob`←?; `sm_jit_run_steps`←?). Capture current mode-3 pass counts (SNOBOL4 --run, Prolog
  GATE-3 run, Icon --run=RED) as the pre-cut baseline so the post-cut RED is measured, not guessed. Get Lon's
  explicit OK that mode-3 corpora may go RED. Doc-only.
- [x] **JA-D-1 — stub the `--run` call site (scrip.c:449).** Replace `sm_emit_linear(...)` with a clean
  `fprintf(stderr,"[NO-SM-BB] --run: linear emitter deleted (FACT RULE); use --interp until templates land\n");
  return 1;` (RULES.md stub form). Now nothing external reaches Engine B. Build links; `--interp` untouched
  (smoke_icon 5/5, broker 23, rungs 198 stay green — those are --interp). `--run hello.icn` prints the stub line.
- [x] **JA-D-2 — excise Engine B (SB-LINEAR producer) as if it never existed.** Delete `sm_emit_linear`,
  `sl_emit_one`, `sl_call`/`sl_ret`/`sl_ret_if_eax`/`sl_jcc_last_ok`/`sl_mov_rdi_*`/`sl_mov_rsi_*`/`sl_mov_rdx_*`/
  `sl_jmp_rel32_slot`, the `SL_B`/`SL_U32`/`SL_U64` macros, `sm_run_linear`, `rt_bb_pump_proc`, and `g_jit_flat_bb`
  + the `SCRIP_JIT_FLAT_BB` getenv. Remove the `sm_emit_linear`/`sm_run_with_recovery_linear`/`sm_run_linear`
  prototypes from sm_jit_interp.h + scrip_sm.h. Zero residue (RULES.md "deletion is total"): no dangling
  prototype, extern, or call. Build links. `--interp` gates green.
- [x] **JA-D-3 — excise Engine A (trampoline JIT) as if it never existed.** Delete `SM_codegen`,
  `emit_standard_blob`(+`_no_stack`), `emit_cond_jump_blob_skeleton`, `emit_jump_blob_skeleton`,
  `emit_label_blob`, `emit_halt_blob`, `emit_trampoline`, `emit_exec_stmt_pat_blob`, `bake_blob_call_{s,si,i}`,
  `sm_jit_run_steps`, the `g_label_blob_map`/`label_blob_lookup` machinery, and the `h_bb_pump_proc`/`h_pump_case`
  handlers that reach the BB C-walker (audit whether the rest of `g_handlers[]`/`h_*` is still wanted as the
  pure SM interpreter for `--interp`; if `--interp` uses `sm_interp.c` not this file, the WHOLE `g_handlers`
  engine here may be deletable — verify by grep before cutting). Stub any remaining external entry to
  `[NO-SM-BB]`. Build links.
- [x] **JA-D-4 — `sm_image_test.c` (the 2 sites).** It hand-emits `mov eax,42; ret` as a self-test. Either delete
  the test file (if it only tested the now-deleted producer) or, if kept, route its bytes through a real
  SM_templates entry. Trivial; do last.
- [x] **JA-D-5 — GREEN-FIELD VERIFY (the FACT RULE completion test).** `grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|
  sl_emit_one|emit_standard_blob|bake_blob_call' src/ | grep -vE '_templates/|/emit_core\.c:'` == **0**. Build
  links; `--interp` gates green (smoke_icon 5/5, broker 23, rungs 198). Mode-3 RED is EXPECTED + recorded.
  Commit message states the scorched-earth reset explicitly (emergency-handoff form).
- [x] **JA-D-6 — TOTAL ANNIHILATION of "jit" / "JIT" everywhere.** This project does NOT perform just-in-time
  compilation. It lowers to native x86 from the starting gate — whole-program, one pass, done. The word "JIT"
  is a lie borrowed from a prior design that never shipped and every occurrence is now actively misleading.
  Scope: ALL of `src/`, ALL of `scripts/`, ALL of `test/`, ALL header files, ALL comments, ALL identifiers,
  ALL file names. Procedure:
  (1) Rename files first: `sm_jit_interp.c` → `sm_codegen.c`, `sm_jit_interp.h` → `sm_codegen.h`,
      `sm_jit_run` → rename fn, `g_jit_*` globals → `g_codegen_*` or descriptive names.
  (2) Mass sed replace across all text: `s/sm_jit_/sm_codegen_/g`, `s/SM_JIT_/SM_CODEGEN_/g`,
      `s/g_jit_/g_codegen_/g`, `s/jit_/codegen_/g` (in identifiers), `s/JIT/native codegen/g` (in comments),
      `s/jit/native codegen/g` (in comments/strings), `s/SCRIP_JIT_FLAT_BB/SCRIP_FLAT_BB/g` (already dead,
      but mop up any surviving reference).
  (3) Update every `#include "sm_jit_interp.h"` → `#include "sm_codegen.h"`.
  (4) Update `scripts/build_scrip.sh` and any Makefile if they reference the old filename.
  (5) Grep verify: `grep -rnI '\bjit\b\|JIT' src/ scripts/ test/` == **0**.
  Build links; gates green. One commit.
- ⮕ **THEN (next phase, NOT JA-D): JA-1/J-5/J-6 rebuild** — route `--run` to load the SHARED emitter's
  template-produced bytes (`codegen_sm_x86` → emit_core dispatch → `bb_*.cpp`/`sm_*.cpp`/`xa_*.cpp`) into a
  PROT_EXEC buffer and jump in. One-instruction thunk-templates are fine as scaffolding; fill real four-port
  x86 per opcode on the ladder. Completion: mode-3 climbs back from RED, grep stays 0, FACT RULE holds.

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
| H-1 cross-arg odometer | `fcfc7a73` | 196→197 |
| H-1 odometer side-effect fix | `fcfc7a73` | 197→198 |

---

## File ownership (paths verified 2026-05-26, build 9be28a5d)
`src/lower/lower_icn.c` (every Icon rung) · `src/lower/bb_exec.c` (mode-2 executor) · `src/lower/scrip_ir.c` (BB kind names, bb_reset) · `src/emitter/{emit_bb.c,emit_sm.c,emit_core.c}` + `src/emitter/BB_templates/bb_*.cpp` (x86 templates) · `src/processor/sm_jit_interp.c` (mode-3 JIT linear emitter `sm_emit_linear`/`sl_emit_one`, Phase J) · `src/processor/sm_interp.c` (mode-2 SM dispatch) · `baselines/icon-bb/`
⚠ PATH NOTE: JIT + SM interp live under `src/processor/`, NOT `src/runtime/x86/` (older docs say the latter — drift corrected).
