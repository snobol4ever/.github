# GOAL-ICON-BB.md — All Icon Byrd-Box constructs, modes 1/2/3/4

**Repo:** one4all + .github · **Sister:** GOAL-CHUNKS*, GOAL-LANG-ICON · **Carved:** 2026-05-10

---

## ⛔ MODE PRIORITY (Lon, 2026-05-26) — MODE 2 then 3; MODE 4 DEFERRED

Get correctness in **mode 2 (`--interp`)** first, then **mode 3 (`--run`, in-proc)**. **Mode 4
(`--compile`) is DEFERRED until further notice** — it is the slowest to iterate (emit asm → gcc -c →
link libscrip_rt → run) and should not gate generator/AG work. Bring constructs up in 2→3 order;
mode 4 follows for free once 3 is flat-wired (mode 3 ≡ mode 4 x86, differing only in process
boundary). Do NOT spend a session round-tripping mode-4 binaries while mode 2/3 still have gaps.

---

## ⚡ CURRENT WATERMARK (one4all `7bfd1178` + uncommitted)

GATES: smoke_icon **5/5** ✅ · broker **23** · icon_all_rungs **198** ✅ · smoke_prolog **5/5** ✅
(2026-05-26, Opus 4.7: every-loop control ports FLAT-WIRED per ir_a_Every — `gen.γ→body`,
`body.γ→gen`, `body.ω→gen`, `gen.ω→every` — additive over literal generators; mode-2 oracle intact.
`lower_every` SM back-edge also fixed. β-synthesis in lower_icn_expr_threaded now matches Prolog
zipper rule (resumable→self, single-shot→ω_in via new icn_kind_is_resumable). FACT-RULE 0.)
✅ `grep -rnE 'seg_byte\(SEG_|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/` outside `*_templates/`+`emit_core.c` == **0**.

⛔ **SESSION 2026-05-26 (Sonnet) — J-4a LOWER + SM template + BB box reached; ONE bug remains.**

**DONE (real, verified, non-regressing — smoke_icon 5/5, rungs 198, smoke_prolog 5/5, FACT-RULE 0):**
1. **LOWER fixed (mode-2 generators now correct end-to-end).** `lower_to`/`lower_to_by` (lower.c)
   were building the BB graph then FREEING it + emitting `SM_PUSH_NULL` — the root cause of dead
   generators. Now they `SM_seq_bb_add(g_p,cfg)` to register the graph and emit `SM_BB_SWITCH`
   carrying the bb_idx, tagged `SM_BBSW_ICN_GEN` (new tag in SM.h, twin of SM_BBSW_PL_ENTRY).
   `sm_interp.c` SM_BB_SWITCH consumer got the Icon-gen arm: `bb_exec_once` first / `bb_exec_resume`
   after, γ pushes value + last_ok=1, ω resets a[0].i + last_ok=0. SM dump now shows `SM_BB_SWITCH`
   at the generator slot (was `SM_PUSH_NULL`); `every write(1 to 3)` prints `1 2 3` in --interp.
2. **SM template created** `src/emitter/SM_templates/sm_bb_switch.cpp` (wired: sm_templates.h,
   emit_core.c dispatch de-stubbed, both Makefile lists + per-file compile rule). MACRO_DEF/BINARY/
   TEXT arms. ICN_GEN TEXT arm fetches `g_stage2.sm.bb_table[idx]->entry`, sets α/β/γ/ω labels, and
   calls `walk_bb_node(gen)` — emitting the generator box's four-port x86 INLINE at emit time
   (no runtime BB walk, no C Byrd box — RULES-clean).
3. **BB box now reached + emits valid x86.** Fixed `bb_icn_to.cpp` TEXT yield: was raw-r12 push
   (brokered convention) → segfault in SM mode-4 ABI; now `mov rdi,rcx; call rt_push_int@PLT`
   matching bb_upto's TEXT convention. mode-4 emit of `every write(1 to 3)` now contains the real
   `# BOX TO(lo=1 hi=3)` inline four-port body (α sets cur, β increments, chk `jg ω`, yields via
   rt_push_int); assembles + links clean.

✅ **`lower_every` back-edge target — FIXED (2026-05-26, Opus 4.7).** The diagnosed bug
(`switch_pc = SM_label(g_p)-1` captured the CALL PC, not the SWITCH PC) is now fixed in
`lower.c` `lower_every`: capture `gen_start = g_p->count` BEFORE `lower_expr(gen_expr)`, then
scan forward `[gen_start, g_p->count)` for the first `SM_BB_SWITCH` and use that PC as the
back-edge target. SM dump now shows `SM_JUMP -> 2` (the SWITCH), not `-> 3` (the CALL). The
stray `SM_LABEL` the old `SM_label()` side-effect emitted is gone (count 15→14). **mode-2
`every write(1 to 3)` → `1 2 3` ✅; gates non-regressing (smoke_icon 5/5, broker 23, rungs 198,
smoke_prolog 5/5, FACT-RULE 0).**

⛔ **MODE 3 (`--run`) IS A GLOBAL STUB.** `--run` currently prints
`[NO-SM-BB] --run: linear emitter deleted (FACT RULE); use --interp until templates land` — the
SB-LINEAR emitter was deleted under the FACT RULE and the `bb_*`/`sm_*` mode-3 templates have not
landed. This is NOT Icon-specific; it is the Phase J work. **NEXT for this goal (per Lon's
MODE-PRIORITY directive): bring `--run` (mode 3) up via the shared template producer** — route
`--run` through `sm_emit_linear`→`sm_run_linear` (PROT_EXEC slab), reusing the SAME template
functions mode 4 uses, so mode 3 and mode 4 stay byte-identical. Until `--run` exists, generator
correctness can only be validated in mode 2.

🟡 **MODE 4 (`--compile`) — DEFERRED (Lon, 2026-05-26).** Progress was made this session before
the defer directive: `sm_bb_switch.cpp` ICN_GEN arm now emits an α/β entry-state dispatch (per-
switch `.data` flag mirroring the interp's `a[0].i`: first entry → α fresh, re-entry → β retry),
fixing the infinite-`1` restart. REMAINING mode-4 bug (do NOT pursue until un-deferred): the
generator-exhaustion (ω) path falls through to `SM_CALL_FN write` before the loop-exit `SM_JUMP_F`,
so `write` runs on an empty value-stack on the final iteration → underflow. Fix when resumed:
restructure `lower_every` so the ω test gates the consumer (emit SWITCH → `SM_JUMP_F loop_exit`
BEFORE the consumer body), OR have the ω path skip to loop-exit directly.

**Files touched this session (Opus 4.7, mode 2/3 focus):** src/lower/lower.c (lower_every scan fix),
src/emitter/SM_templates/sm_bb_switch.cpp (α/β dispatch — mode-4, deferred). NOT yet committed.

**GATE-PK still RED/stale (455/62/592) since `a5775d1a` — owner decision on re-freeze pending. With
mode 4 deferred, GATE-PK is not a blocking gate; revisit when mode 4 resumes.**

---

(prior NEXT, still valid follow-on) fill hollow pattern arms SPAN→ANY→NOTANY→BREAK→CAP→ARBNO.

Files to fill:
- `src/emitter/BB_templates/bb_pat_span.cpp` — SPAN(cset)
- `src/emitter/BB_templates/bb_pat_any.cpp` — ANY(cset)
- `src/emitter/BB_templates/bb_pat_notany.cpp` — NOTANY(cset)
- `src/emitter/BB_templates/bb_pat_break.cpp` — BREAK(cset) + BREAKX
- `src/emitter/BB_templates/bb_capture.cpp` — CAP
- `src/emitter/BB_templates/bb_arbno.cpp` — ARBNO(pat)

Each gets TEXT + BINARY x86 four-port body (α fresh-entry, β retry, γ success, ω fail).
Anchor gate per template: broker pattern rungs climb from RED.
`rt_cs_new` (allocates `rt_cs_t {chars,delta}`) is still live — use it for the charset state pointer.
ARBNO needs a growable frame stack; stash ptr in `pBB->counter` (intptr cast), or GC aux struct.

---

## Session Setup
```bash
cd /home/claude/one4all
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
bash scripts/build_spitbol_oracle.sh
```
Gates:
```bash
bash scripts/test_smoke_icon.sh            # PASS=5
bash scripts/test_smoke_unified_broker.sh  # PASS=23
bash scripts/test_icon_all_rungs.sh        # PASS=198
```

---

## THE FOUR FACTS — READ FIRST

1. **C WALKERS: MODE 2 ONLY.** `icn_bb_dcg` / `bb_exec_once` / `bb_exec_resume` / `bb_exec.c` — permitted in `--interp` only.
2. **NO C WALKERS IN MODE 3/4.** Those symbols stay DEFINED (mode 2 needs them) but UNREACHABLE from `--run`/`--compile`.
3. **SM + BB DO NOT EXIST AT RUNTIME IN MODE 3/4.** Emitter reads them once, bakes flat-wired x86. `scrip.c` frees SM+BB before the runner executes.
4. **ONE x86 PRODUCER.** `src/emitter/ + BB_templates/*.cpp / SM_templates/ / XA_templates/` only. A second producer ALWAYS drifts.
5. **TEMPLATE-ONLY EMISSION (FACT RULE).** Every byte of emitted x86 lives in a template function keyed to a BB/SM/XA opcode, reached only via `emit_core.c` dispatch. `grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob' src/` outside `*_templates/` + `emit_core.c` == 0.

**Completion test:** from any `--run`/`--compile` entry, reachability to `icn_bb_dcg`/`pl_bb_dcg`/`bb_exec_once`/`bb_exec_resume` == ZERO.

**Other rules:** NO AST WALKING modes 2/3/4. ZERO C Byrd-box functions (`DESCR_t foo(void*,int entry)`); only exempt: `icn_bb_dcg`, `icn_bb_oneshot`. NO new C functions in `icon_box_rt.c`/`rt.c` to back a template — logic lives inline in `bb_*.cpp`. CONSULT `irgen.icn` before any BB kind (`/home/claude/corpus/programs/icon/jcon-ref/irgen.icn`).

---

## Architecture

```
.icn → icon_parse() → AST_t*
  --interp   → execute_program() → interp_eval()        Mode 2 (SM+BB C walker, reference)
  --run      → lower() → sm_codegen_x64() → exec        Mode 3 (in-proc, PROT_EXEC)
  --compile  → lower() → sm_codegen_x64() → binary      Mode 4 (separate process)
```

`tree_t` → `lower()` → SM bootstrap + `BB_graph_t`. **BB_t IS the IR** (≡ JCON `ir_*`). NOT a tree.

**GOLDEN BB RULE:** BB_t has ONLY: `t` (kind), `α β γ ω` (port ptrs), `sval`/`ival`/`dval` (IR payload), `value`/`counter`/`state` (interp runtime). No `c[]`/`n`/`lhs`/`rhs`/`opaque`/`sval2`/`ival2`/`ival3`. **BB_t struct is FINAL.**

**Four ports (AG over lowering):**
| Port | Direction | Meaning |
|------|-----------|---------|
| γ | DOWN (inherited) | success continuation |
| ω | DOWN (inherited) | failure continuation |
| α | UP (synthesized) | fresh-entry address |
| β | UP (synthesized) | retry-entry address |

Signature: `lower(cfg, tree, γ_in, ω_in, &α_out, &β_out)`. JCON `{start,resume,success,failure}` → `α/β/γ/ω`.

---

## Done when
1. Every AST kind reachable from a `--interp` PASS Icon program lowers via `lower.c` to pure SM/BB.
2. Every SM opcode Icon emits has a `sm_codegen_x64` mirror.
3. `is_suspendable` / `coro_eval` not reachable from SM dispatch.
4. Mode 3 and mode 4 execute the IDENTICAL emitter-produced flat-wired x86, differing only in process boundary.

---

## Phase H — Attribute Grammar (pointers, no label IR)

#### H-1 — 4-attribute lowerer ✅ SUBSTANTIALLY COMPLETE
- [x] Threaded signature + back-to-front spine; leaves compose; top γ/ω seeded NULL=trampoline-halt.
- [x] BB_IF else→ω. BB_CONJ (`E1 & E2`) own opcode.
- [x] Cross-arg odometer: multi-generator CALL args cross-product (rungs 196→198). Side-effect fix: single-shot args cached, not re-evaluated.
- [ ] **REMAINING:** DOWN-threading of γ/ω into then/else/body for nested non-leaf IF. Blocked: `if` not accepted in expression position by parser (GOAL-PARSER-ICON prereq). Generator-composition corners verified clean.

#### H-2 — BB_SEQ child-array → γ-chain ⏳
- [ ] `lower_icn_proc_body` seq build → γ/ω-chain; `bb_exec.c` BB_SEQ walk via ports. Gate smoke 5/5.

#### H-3 — 2-operand kinds via α/β + thread γ/ω ⏳
- [x] BB_TO_BY proof: JCON `ir_a_ToBy` transliterated; `2 to 7 by 2`→2 4 6.
- [ ] Each binary kind: lower lhs (γ=rhs.α…), lower rhs, wire α/β; executor reads `nd->α->value`/`nd->β->value`.

#### H-4 — N-ary kinds via γ-chain ✅
- [x] CALL args γ-chain + MAKELIST (`82ec79f8`).
- [x] IDX_SET/SECTION 3-operand (`45c1bde2`).

#### H-5 — sweep `c[]/n` in bb_exec.c ⏳
- [ ] `grep -nE 'nd->c\[|nd->n\b|e->c\[|e->n\b|gen->c\[' src/lower/bb_exec.c` empty.

---

## Phase J — Mode 3 executes shared emitter's flat-wired x86

**Root cause of RED:** `scrip.c` mode_run frees `bb_table` + SM before the runner executes; the old baked `rt_bb_pump_proc` read freed `bb_table[]` → NULL → crash. Fix: mode 3 EMITs via the shared template producer, not a C walker.

#### J-2 — memstream sink ✅ (`106b7c51`)
`open_memstream` FILE* sink for `codegen_sm_x86`. `--memcheck` proves memstream==file bytes 3/3.

#### J-3 — `call rel32` to proc SM entry_pc ✅ (`de0f2352`)

#### J-4 — route SM_BB_PUMP_PROC through J-2/J-3 ⏳
- [x] `hello` prints; `double(21)`=42; SM_ACOMP/LCOMP wired; SM_LOAD/STORE_FRAME via rt helpers.
- [ ] **NEXT (J-4a): GENERATORS.** `every`/`to`/`by` abort flag-on. Root cause: `bb_icn_to_by.cpp` / `bb_icn_to.cpp` PLATFORM_X86 arms now hollow (deleted with `rt_bb_*`). Fix = implement four-port literal generator x86 in those templates. Probe: `every write(1 to 3)` → `1 2 3` flag-on.

#### J-5 — migrate PUMP_SM, PUMP_CASE, BB_SWITCH, generator path ⏳
#### J-6 — flip default to flat BB; delete C bridge ⏳

**Phase J done when:** mode 3 ≡ mode 4 flat-wired x86; `icn_bb_dcg`/`bb_exec.c` unreachable from `--run`; smoke 5/5, broker ≥23, rungs ≥198, ASAN clean.

---

## Invariants
1. `--ir-emit` byte-identical at every rung.
2. No `EXPR_t*` in SM bytecode.
3. `is_suspendable` stays in sync with lowering rungs.

---

## Closed rungs
| Rung | Commit | Gain |
|------|--------|------|
| H-1 threading + IDX_SET/SECTION | `45c1bde2` | 189→195 |
| BB_CONJ (E1 & E2) | `9be28a5d` | 195→196 |
| H-1 cross-arg odometer | `fcfc7a73` | 196→197 |
| H-1 odometer side-effect fix | `fcfc7a73` | 197→198 |
| JA-D (engines + JIT deleted) | `e842b724` | — |
| rt_bb_* total deletion | `0206b998` | — |

---

## File ownership (`0206b998`)
`src/lower/lower_icn.c` · `src/lower/bb_exec.c` · `src/lower/scrip_ir.c` · `src/emitter/{emit_bb.c,emit_sm.c,emit_core.c}` · `src/emitter/BB_templates/bb_*.cpp` · `src/processor/sm_codegen.c` · `src/processor/sm_interp.c` · `baselines/icon-bb/`

---

## ⚡ HOW AG-LOWERING + EMITTER TEMPLATES ACTUALLY WORK (Sonnet, 2026-05-26 — learned by reading code)

Hard-won mental model. Read this before touching generators; it cost a full session to assemble.

### The two-stage pipeline, concretely

```
Icon AST → LOWER (builds SM bootstrap + BB graph) → EMITTER walks BB at emit time → x86 via templates
```

There are TWO lowerers and they are NOT the same file:
- `lower.c` — the SM-spine lowerer. Emits the flat `SM_sequence_t` (PUSH/CALL/JUMP/BB_SWITCH...).
  This is the "bootstrap" / statement scaffold. `lower_to`, `lower_to_by`, `lower_every` live here.
- `lower_icn.c` — the BB-graph builder. `lower_icn_expr_top(tree)` returns a `BB_graph_t*` whose
  `->entry` is a four-port-wired `BB_t` tree. THIS is the IR the emitter walks. `BB_t IS the IR`.

The bridge between them: `SM_seq_bb_add(g_p, cfg)` registers a `BB_graph_t*` into
`g_stage2.sm.bb_table[]` and returns an `int bb_idx`. The SM carries that idx in an
`SM_BB_SWITCH` instruction. This is the SAME mechanism SNOBOL4 patterns use (`SM_EXEC_STMT`
carries a bb_idx) and Prolog uses (`SM_BB_SWITCH` + `SM_BBSW_PL_ENTRY`). One pattern, three langs.

### Attribute Grammar = the four ports, threaded by lower_icn.c

γ/ω are INHERITED (passed DOWN into children): success-continuation, fail-continuation.
α/β are SYNTHESIZED (returned UP from children): fresh-entry addr, retry-entry addr.
Signature shape: `lower(cfg, tree, γ_in, ω_in, &α_out, &β_out)`. Leaf: `α=β=self; γ=γ_in; ω=ω_in`.
Composition wires child.γ → next sibling, last.γ → parent.γ, etc. (see `lower_icn.c` arg-γ-chain
at the `BB_CALL` case: `args[j-1]->γ = args[j]`). The mode-2 reference walker `bb_exec.c`
(was `ir_exec.c`) executes this graph by following ports — it is the SEMANTIC SOURCE OF TRUTH for
every BB kind. To implement any construct: read its `case BB_X:` in bb_exec.c, translate to x86.

**ALL FOUR PORTS MUST BE WIRED — flat-wired, no NULL, no trampoline (corrected 2026-05-26, Opus
4.7, after Lon).** The canonical model is JCON `irgen.icn` `record ir_info(start, resume, failure,
success)` ≡ our `α/β/γ/ω`. In irgen EVERY chunk wires EVERY port to a concrete target via
`ir_Goto(coord, <other-port>)` — there is NO NULL exit and NO fall-through to any "trampoline/halt".
Even a LEAF wires all ports: `ir_a_Intlit` does `start: [IntLit; Goto(success)]` and (bounded)
`resume: [Goto(failure)]`. A generator like `ir_a_ToBy` wires eight chunks — `start→fromexpr.start`,
`resume→[ResumeValue; Goto success]`, `fromexpr.success→toexpr.start`,
`fromexpr.failure→ir.failure`, `toexpr.success→byexpr.start`, `toexpr.failure→fromexpr.resume`,
`byexpr.success→[opfn; Move; Goto success]`, `byexpr.failure→toexpr.resume`. Every port lands on a
port; the top-level seeds the terminal success/failure with real halt chunks.

⛔ **OUR CURRENT lower_icn.c DIVERGES — this is the real defect to fix.** Two problems:
(1) **Leaves leave ports NULL.** `BB_node_alloc` NULLs α/β/γ/ω and leaf cases (TT_ILIT/TT_VAR/…)
set only the payload (ival/sval), never wiring start→success / resume→failure as irgen requires.
(2) **α/β are OVERLOADED as operand-child pointers, not control-flow ports.** e.g. TT_TO_BY does
`nd->α = lo; nd->β = hi;` (the lo/hi OPERAND boxes), and the BB_CALL case chains args as
`e->α … a = a->γ` (γ = "next operand sibling"). So `bb_exec.c` walks α/β/γ as an OPERAND TREE in C —
that is AST-walking-in-disguise and is exactly what flat-wiring must eliminate. It "works" in mode 2
ONLY because the C executor patches the holes at runtime (the `? : NULL` guards I earlier mis-read
as "design"). Flat-wired x86 (mode 3/4) has nowhere to fall back to: an unwired port = jump-to-
garbage; an operand-in-port = no control-flow successor at all. **NEXT (mode 2→3): rewire lower_icn.c
so α/β/γ/ω are PURE control-flow links per irgen — operands become separate boxes whose `success`
(γ) flows into the next box's `start` (α) — and verify against `bb_exec.c` re-expressed as a flat
port-follower (no tree recursion). Read each `ir_a_*` in irgen.icn for the exact per-port wiring.**

#### Canonical per-port wiring (extracted from irgen.icn — α=start β=resume γ=success ω=failure)

Terminal seeding (`ir_a_ProcBody`/`ir_a_ProcCode`): the proc's last stmt `γ → proc.γ` and
`ω → proc.ω`; proc.γ/proc.ω are real terminal chunks (`ir_Fail`/halt). The buck stops at concrete
top-level chunks — NEVER a NULL or an implicit trampoline.

- **Intlit/Reallit/Stringlit/Csetlit (leaf):** `α: [emit lit; Goto γ]`; (bounded) `β: [Goto ω]`.
- **Ident/Var (leaf):** same shape — `α` does the load then `Goto γ`; `β → ω`.
- **ToBy:** `α→from.α`; `β: [ResumeValue; Goto γ]`; `from.γ→to.α`; `from.ω→ω`; `to.γ→by.α`;
  `to.ω→from.β`; `by.γ: [opfn "..."; Move target; Goto γ]`; `by.ω→to.β`.
- **Every:** `α→expr.α`; `expr.γ→body.α`; `expr.ω→ω`; `body.γ→expr.β`; `body.ω→expr.β`.
  (`body.γ→expr.β` IS the loop back-edge — a PORT WIRE, not an SM_JUMP. The whole loop is BB-graph
  internal; no SM scaffold needed once lower_icn wires it.)
- **If:** `α→cond.α`; `cond.γ→then.α`; `cond.ω→else.α` (or `→ω` if no else); `then.γ→γ`;
  `then.ω→ω`; `else.γ→γ`; `else.ω→ω`. (Read ir_a_If:577 for the exact bounded/rval variant.)
- **Compound (seq):** chain `stmt[i].γ→stmt[i+1].α`; last `.γ→γ`; failures per ir_a_Compound:1231.
- **Alt (`E1|E2`):** `α→e1.α`; `e1.γ→γ`; `e1.ω→e2.α`; `e2.γ→γ`; `e2.ω→ω`; resume re-enters the
  currently-active arm (ir_a_Alt:167).
- **Field/Binop/Unop/Call:** operand boxes are SEPARATE nodes wired `operand.γ→next.α`; the op's own
  `α` is the first operand's `α`, the result is produced in the last operand's `γ` chunk which then
  `Goto γ`. Operands are NOT stored in α/β as child pointers (our current bug).

REWIRE ORDER (mode 2 must stay green each step — bb_exec.c is the oracle): (1) leaves
(Intlit/Var/Stringlit/Cset) wire α→γ, β→ω; (2) ProcBody/ProcCode terminal seeding; (3) Compound
seq γ-chain; (4) If/Alt; (5) ToBy/Every/Upto generators (back-edge = body.γ→expr.β port wire);
(6) Call/Binop operand-box chains (retire α/β-as-operand-child). After each: smoke_icon 5/5,
rungs ≥198. bb_exec.c must be re-expressed as a pure port-follower (no `a = a->γ` operand-tree
recursion) once ports are control-flow only.

#### THE ZIPPER — copy Prolog's lower_pl.c exactly (Lon, 2026-05-26). lower_pl ALREADY does this.

Two inherited attrs go DOWN (γ_in, ω_in = where to go on success/fail); two synthesized attrs come
UP (α_out, β_out = my fresh-entry, my retry-entry). Signature (mirror EXACTLY):
`lower_icn_expr_node(cfg, e, BB_t *γ_in, BB_t *ω_in, BB_t **α_out, BB_t **β_out)`.

LEAF SEEDER (twin of `pl_leaf`, lower_pl.c:21 — add `icn_leaf`):
```c
static BB_t *icn_leaf(BB_t *nd, BB_t *γ_in, BB_t *ω_in, BB_t **α_out, BB_t **β_out){
    if(!nd) return NULL;
    nd->γ=γ_in; nd->ω=ω_in;            /* inherited DOWN */
    if(α_out)*α_out=nd;                /* leaf is its own fresh-entry, synth UP */
    if(β_out)*β_out=ω_in;              /* leaf has no retry: β=ω → ω-chain skips through it */
    return nd; }
```
Every leaf case becomes: `return icn_leaf(nd, γ_in, ω_in, α_out, β_out);` (see lower_pl.c:62-63).

CONJUNCTION/SEQ = back-to-front zipper (lower_pl_goal conjunction, lower_pl.c:160-203):
build goal[n-1] first with γ=γ_in; then i=n-2..0 with `my_γ = gα[i+1]` (success→next entry);
wire `goal[i].ω = gβ[i-1]` (fail→redo nearest LEFT generator). β-by-kind:
resumable (generators: TO/TO_BY/UPTO/ALT/EVERY/PROC_GEN…) → β=self; non-resumable → β=left neighbor's β.

DISJUNCTION/ALT (lower_pl.c:206-217): lower 2nd branch first (γ_in,ω_in)→bα; lower 1st with
`ω=bα` (1st fails→try 2nd)→aα; node α=aα β=bα γ=γ_in ω=ω_in.

This is NOT additive — it is a signature change touching ~70 call sites in lower_icn_expr_node, done
in ONE pass top-to-bottom (you cannot half-zip). After: α/β/γ/ω are PURE control flow; retire the
α/β-as-operand reads in bb_exec.c (operands become boxes wired operand.γ→next.α). Gate each language
construct group: smoke_icon 5/5, rungs ≥198. EVERY already pre-wired (gen.γ→body, body.γ→gen,
gen.ω→every) for literal generators — fold into the zipper when EVERY's turn comes.

### EMITTER templates — the THREE things that are easy to get wrong

1. **emit_core.c is DISPATCH-ONLY.** Template bodies live in `BB_templates/bb_*.cpp`,
   `SM_templates/sm_*.cpp`, `XA_templates/xa_*.cpp`. emit_core just does `case BB_X: bb_x(nd);`.
   A template emitting empty string / stub jumps is NOTHING (Invariant 0). Real GAS in MEDIUM_TEXT
   AND real bytes in MEDIUM_BINARY, or it is not done.

2. **There are TWO value-stack conventions and they DIFFER BY MEDIUM. This is the #1 trap.**
   - MEDIUM_TEXT (mode-4 `--compile`): values go through the rt ABI — `mov rdi,<v>; call rt_push_int@PLT`.
     This is what `bb_upto.cpp` TEXT does and what WORKS in the SM mode-4 ABI.
   - MEDIUM_BINARY (mode-3 flat/brokered): raw `r12` value-stack — `mov [r12+8],rax; add r12,16`.
   `bb_icn_to.cpp` originally used raw-r12 in its TEXT arm (brokered convention) → SEGFAULT in
   mode-4 because r12 is not set up as a vstack there. FIX was `rt_push_int@PLT`. When you write a
   TEXT arm, push via rt helpers; r12 is for BINARY only. (Invariants 8/9: BINARY must embed no
   emitter-process pointers and no four-port rt_* helper; TEXT may `call util@PLT` for non-port utils.)

3. **last_ok is a FUNCTION, not a data symbol.** `nm` shows `T rt_last_ok` (getter) and
   `T rt_set_last_ok` (setter). Writing `mov [rip+rt_last_ok],1` corrupts code. Use
   `mov rdi,<0|1>; call rt_set_last_ok@PLT`.

### How to make a registered generator graph emit inline (the SM_BB_SWITCH ICN_GEN pattern)

The SM_BB_SWITCH template, for an Icon generator, fetches `g_stage2.sm.bb_table[idx]->entry`,
sets `g_emit.lbl_α/β/γ/ω` (+ `_p` pointers) to fresh labels, then calls `walk_bb_node(gen, out)`.
walk_bb_node dispatches to the box's `bb_*` template, which emits its α-body at lbl_α and jumps to
lbl_γ/ω/β. The SM template then defines those labels: γ → set last_ok=1 + continue; ω → set
last_ok=0 + continue. This emits the box's four-port x86 INLINE at emit time — NO runtime BB walk,
NO C Byrd box (the PD-8 trap). MUST set lbl_α too or the box emits `(null):` → assembler error.

### The every-loop back-edge gotcha (the open J-4a bug)

`lower_every` (lower.c) captures `switch_pc = SM_label-1` AFTER `lower_expr(gen_expr)`. For
`every write(1 to 3)`, gen_expr is the WHOLE call, so lower_expr emits SM_BB_SWITCH (inner `to`)
THEN SM_CALL_FN write — `switch_pc` wrongly points at the CALL. The loop back-edge must re-enter
the GENERATOR's switch PC, not the consuming CALL. Fix: locate the SM_BB_SWITCH PC emitted within
gen_expr (or lower the bare generator separately from its consumer body). mode-2 is immune because
SM_BB_PUMP_PROC drives the whole proc via the C graph walk, ignoring the SM loop scaffold.

### Gate reality

- `test_icon_all_rungs.sh` is `--interp` (mode-2) ONLY — pinned ~198 regardless of emitter work.
  It CANNOT measure mode-4 generator progress. Build a mode-4 Icon rung gate (mirror Prolog GATE-3:
  per-rung emit→assemble→link→run, assert == mode-2 output) to make EMITTER rungs honestly count.
- GATE-PK (per-kind) is the emitter-output gate but has been stale-RED since `a5775d1a` (baseline
  not re-frozen across ~9 emitter commits). Owner decision needed: verify cells then re-freeze.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
