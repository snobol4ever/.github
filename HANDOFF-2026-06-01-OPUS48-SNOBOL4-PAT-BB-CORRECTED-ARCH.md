# HANDOFF 2026-06-01 — Opus 4.8 — SNOBOL4 PAT-BB: CORRECTED PATTERN ARCHITECTURE

**Goal:** GOAL-SNOBOL4-BB.md (SESSION RUNG #0 — SBL-PAT-BB, the 5-phase native pattern execution).
**Type:** DESIGN PIVOT — no SCRIP code committed. SCRIP HEAD unchanged at `6483bb5`.
**Watermark:** SCRIP `6483bb5` (unchanged) · .github `0dfe9552` (design commit, pushed).

---

## What happened

Mid-PB-2, Lon corrected the pattern-construction design. The trigger: PB-1 (landed `6483bb5`) and a draft
PB-2 were both wiring the native pattern path onto `PATND_t` — the redundant runtime pattern-IR that is
slated for demolition ("KILL PATND_t" / PND-1). Building on the type being deleted is backwards.

**The corrected model (now the source of truth in GOAL-SNOBOL4-BB.md "CORRECTED PATTERN ARCHITECTURE" +
ARCH-SNOBOL4.md):**

1. A SNOBOL4 pattern is a graph of **EMITTED BYRD-BOXES** (`bb_box_fn` in the RX pool), driven by
   `bb_broker.c` four-port (α/β/γ/ω) — the SAME broker as Icon/Prolog. NOT a `PATND_t`, NOT a `tree_t`.
   There is no second runtime IR and no interpreted pattern tree.
2. `tree_t` (AST) is for **EVAL/CODE only** (they compile a runtime *source string*). A pattern's structure
   is known at COMPILE time, so baking its `tree_t` to re-walk at runtime is a pointless round-trip.
3. **`DT_P`** (the pattern datatype, `descr.h` `.p` slot, demolished with `PATND_t`) BECOMES a `bb_box_fn`
   graph head. `COLOR = 'GOLD' | 'BLUE'` stores a box-graph; `B ? COLOR` runs it; `BOTH = COLOR CRITTER`
   stitches two box-graphs.
4. **SEAL at element granularity, WIRE at instance level.** Each element matcher's code is sealed (RO); the
   graph is instance-level. `STITCH_*` boxes wire instance records whose `code` points at sealed element
   matchers — so STITCH NEVER touches sealed interior jumps. (This dissolved the "boundary ports of a sealed
   subgraph" problem — and the tree-instinct: back-edges ω/β are why it must be a graph, and postfix emit
   order means no tree is ever held, exactly like LOWER.)
5. The build sequence = the runtime twins of LOWER's `wire_seq`/`wire_alt`. `STITCH_SEQ`/`STITCH_ALT` wire
   box-instances with the SAME port equations. ONE construction, TWO times: all-constant → wire at EMIT time
   (sealed); any runtime operand → wire at MATCH-BUILD time.

**Decided forks (Lon delegated judgment):** A — `BB_PAT_BUILD_*` is NARROW, only for STRUCTURAL variance
(`*E`/`$NAME`/pattern-var); operand variance (`LEN(N)`/`SPAN(cvar)`) is operand-binding read late from a
ζ-slot, no builder. B — "build" = SPLICE/wire, not JIT-emit (real codegen only for `*E`/EVAL/CODE via the
`tree_t` path). C — REUSE the existing `IR_PAT_*` matcher templates. D — ε-merge (Thompson/NFA, reuse
`bb_nfa.cpp`) boundaries for the variant path; all-invariant seals to direct jumps. E — seal at element
granularity; the all-invariant single-BLOB freeze is the PB-RB-OPT optimization, not a base case.

---

## Actions taken this session

- **Reverted** the draft PB-2 (uncommitted: `IR_PAT_MATCH` + `bb_sno_match.cpp` calling a `PATND_t`-inspecting
  `rt_sno_match`, plus emit wiring). SCRIP tree clean at `6483bb5`. Nothing was compiled; no validation lost.
- **Re-cut the PB ladder** in GOAL-SNOBOL4-BB.md into **PB-RB-1 … PB-RB-OPT** (the rebuilt ladder).
- **Flagged OLD PB-1 for rework** (PB-1-REWORK): `IR_PAT_BUILD_LIT`/`rt_sno_pat_build_lit`/
  `bb_sno_pat_build_lit.cpp` build a `PATND_t` → retire in PB-RB-1, replace with `REF_INVARIANT` + the
  existing `IR_PAT_LIT` matcher box.
- **Marked the old `tree_t`-bake DESIGN QUESTION SUPERSEDED** (the `beauty.sno` / `tree(t,v,n,c)` memorial is
  retained — it is the AST shape for EVAL/CODE, not patterns).
- Updated **ARCH-SNOBOL4.md** (phase-2 build, build/run split, optimization section, header).
- Committed + pushed the doc update to `.github` (`0dfe9552`). No SCRIP/corpus changes.

**Survivors (correct as-is):** PB-0 (`IR_SUBJECT` / `bb_sno_subject` / `rt_sno_subject_load` — no `PATND_t`,
loads Σ/Δ); `rt_sno_match_lit` (the `PATND_t`-free ch.18 literal-scan kernel, unit-tested 7/7 — becomes the
literal element matcher's inner scan).

---

## Gates (UNCHANGED this session — no compile; baselines at `6483bb5`)

```
make scrip                     rc=0
make libscrip_rt               rc=0
test_smoke_snobol4.sh          m2 7/7 (HARD) / m3 5/6 / m4 0/6
prove_lower2.sh                64/0
test_gate_sm_dead.sh           1 (<=1)
audit_concurrency_invariants.sh OK
test_gate_no_vstack.sh         g_vstack==0
```

---

## NEXT (#1): PB-RB-1 — REF_INVARIANT + retire the PATND_t literal builder

Delete `IR_PAT_BUILD_LIT` / `rt_sno_pat_build_lit` / `bb_sno_pat_build_lit.cpp`. Add `IR_REF_INVARIANT`
(IR.h, append-only) + `bb_ref_invariant.cpp` (load a sealed element `bb_box_fn` head, RO `[rip+disp]`/movabs,
into a ζ-slot). Lower `TT_QLIT` pattern → REF_INVARIANT over a sealed `IR_PAT_LIT` (`bb_lit.cpp`); keep
`rt_sno_match_lit` as the literal element's inner scan. Prove topology; mode-3 probe.

**Open question for Lon before starting PB-RB-1:** it deletes a committed box family
(`IR_PAT_BUILD_LIT`). Confirm retire-and-replace (vs. leaving the dead box behind `REF_INVARIANT`).
Discipline reminder: every PB-RB box = prove four-port topology → BINARY arm (mode-3 `--run`) → TEXT arm
(mode-4 `--compile`); mode-2 (`IR_SCAN`) must NOT regress (m2 7/7 HARD); no `PATND_t`, no `tree_t`, no value
stack, no ring.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus

---

## ADDENDUM — PB-RB-1 scaffolding landed + retire decision (2026-06-01, same session)

**SCRIP watermark advanced to `61edf77`** (pushed at handoff). Additive, DORMANT plumbing for PB-RB-1 so
the next session writes logic, not scaffolding:
- `IR.h` — `IR_REF_INVARIANT` kind (append-only before `IR_OP_COUNT`).
- `bb_ref_invariant.cpp` — structured fail-loud STUB (bomb_text TEXT / abort inside MEDIUM_BINARY, both
  audit-exempt). Documented intended role: load a sealed element `bb_box_fn` head (RO `[rip+disp]`/movabs)
  into a `ζ`-slot; distinct from STITCH (wire instances) and BB_PAT_BUILD (build dynamic boxes).
- `emit_core.c` — one dispatch case `IR_REF_INVARIANT -> bb_ref_invariant`.
- `Makefile` — `bb_ref_invariant.cpp` appended to `RT_PIC_SRCS` + per-template `.o`.

DORMANT = nothing lowers to `IR_REF_INVARIANT`, so the stub is unreachable. **All gates INVARIANT vs
`6483bb5`:** make scrip rc=0, libscrip_rt rc=0, smoke SNOBOL4 m2 7/7 HARD / m3 5/6 / m4 0/6, smoke Icon
m2 10/10 HARD / m3 9/10 / m4 9/10, prove_lower2 64/0, sm_dead 1, concurrency invariants OK, template
purity 7, no-vstack g_vstack==0.

**RETIRE DECISION (Lon delegated "your choice"):** RETIRE the dormant PB-1 BUILDER artifacts
(`IR_PAT_BUILD_LIT` + `rt_sno_pat_build_lit` + `bb_sno_pat_build_lit.cpp` + their dormant arms in
lower.c/bb_exec.c/emit_core.c/emit_bb.c/Makefile) as the FIRST action of PB-RB-1 proper — they are unwired
from `v_scan`, so deletion is BYTE-NEUTRAL to every gate (nothing emits `IR_PAT_BUILD_LIT`), and code that
builds the doomed `PATND_t` contradicts the locked architecture. KEEP the `PATND_t` TYPE removal
(`pattern.c`/`descr.h`/`patnd.h`) as the SEPARATE Track-B runtime-demolition slice — do NOT fold it in.
`rt_sno_match_lit` (the PATND_t-free ch.18 literal-scan kernel, 7/7) SURVIVES as the literal element
matcher's inner scan.

**NEXT (#1) is now logic-only:** in `bb_ref_invariant.cpp` write the sealed-head load (BINARY + TEXT arms,
model on bb_sno_subject.cpp), add `lower2_ref_invariant_entry` lowering `TT_QLIT` pattern -> REF_INVARIANT
over a sealed `IR_PAT_LIT` (`bb_lit.cpp`), prove the topology in prove_lower2.c, run a mode-3 probe — and
retire the PB-1 builder per the decision above. Then PB-RB-2 (matcher-box four-port ABI) and PB-RB-3 (BB_MATCH
driver). Discipline: prove topology -> BINARY arm (mode-3) -> TEXT arm (mode-4); mode-2 (`IR_SCAN`) must NOT
regress (m2 7/7 HARD); no `PATND_t`, no `tree_t`, no value stack, no ring.
