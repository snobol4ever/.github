# GOAL-ICON-BB.md — All Icon Byrd-Box constructs, modes 1/2/3/4

**Repo:** one4all + .github · **Sister:** GOAL-CHUNKS*, GOAL-LANG-ICON · **Carved:** 2026-05-10

---

## ⚡ CURRENT WATERMARK (one4all `0206b998`)

GATES: smoke_icon **5/5** ✅ · broker **23** (pattern rungs RED — expected) · icon_all_rungs **198** ✅
(2026-05-26, Sonnet 4.6: all 10 `rt_bb_*` C runtime Byrd-box functions deleted. `grep rt_bb_ src/ == 0`.)

⛔ **NEXT: fill inline-x86 four-port bodies** in the hollow `PLATFORM_X86 { return std::string(); }` arms.
Order: SPAN → ANY → NOTANY → BREAK → CAP → ARBNO (simplest first; each its own commit, gates green between).

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
