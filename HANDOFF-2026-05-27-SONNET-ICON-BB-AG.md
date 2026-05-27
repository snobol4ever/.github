# HANDOFF — 2026-05-27 — Sonnet 4.6 — GOAL-ICON-BB: 4-Attr AG Infrastructure

**one4all** `aca30894` · **goal:** GOAL-ICON-BB · **mode priority:** mode 2 then mode 3

---

## WATERMARK

GATES: smoke_icon **5/5** · broker **23** · rungs **198** · smoke_prolog **5/5** — ALL UNCHANGED

---

## WHAT WAS DONE THIS SESSION

### Core work: 4-Attribute AG infrastructure added to lower_icn.c (additive, mode-2 safe)

The complete attribute grammar wiring map was extracted from **irgen.icn** (the canonical JCON
source) and translated from label-goto style into live BB_t* pointer assignments. The 4 attrs:

- `γ_in` / `ω_in` — **inherited DOWN** from caller (success / failure continuations)
- `α_out` / `β_out` — **synthesized UP** to caller (fresh-entry / retry-entry)

**New functions added** (`lower_icn.c` + `lower_icn.h`):

| Function | Purpose |
|---|---|
| `icn_kind_is_resumable(BB_op_t)` | Generator vs single-shot: β=self for generators, β=ω for single-shot |
| `icn_kind_owns_omega_operand(BB_op_t)` | Guards BB_IF (ω = else-arm operand, not failure continuation) |
| `lower_icn_expr_threaded(cfg, e, γ_in, ω_in, &α_out, &β_out)` | 4-attr wrapper; stamps γ/ω on ROOT node only |

### SHALLOW vs DEEP threading — the critical architectural finding

**SHALLOW THREADING was chosen** — stamps γ/ω only on the root node returned by
`lower_icn_expr_node`. Deep threading was implemented first but regressed 198→177 rungs.

**Root cause of deep-threading failure:**

BB_SEQ executor walks `while (last_child->γ) last_child = last_child->γ;` to find the last
statement. When child nodes have non-NULL γ (pointing to outer continuations), the walker
chases off the end of the sequence into outer scopes. **BB_SEQ's γ port is OVERLOADED —
it serves as BOTH operand-chain linkage AND the 4-attr success continuation.** These two
uses are incompatible when γ is set on child nodes.

Additional breakage: BB_NOT, BB_ALT arms, etc. — setting γ/ω on children caused bb_exec
to follow continuations where it previously returned NULL (relying on C-stack propagation).

**Mode-2 bb_exec.c uses the C call stack as implicit control flow.** Children with non-NULL
γ/ω = double-advance or wrong-direction propagation. Shallow stamping on root only is safe
because bb_exec's `return nd->γ` at the root IS the intended continuation.

### lower_icn_proc_body

Updated to use `lower_icn_expr_threaded`. Back-to-front (zipper) build: each stmt born with
γ/ω = next stmt's entry. irgen ir_a_Compound: both γ AND ω of intermediate stmts advance
(failures also advance in a statement sequence — only the LAST stmt propagates γ/ω outward).

---

## WHAT REMAINS (NEXT SESSION ENTRY POINT)

### The complete irgen.icn AG wiring map is specified

The conversation history contains the **complete per-construct wiring table** for every
`ir_a_*` procedure (NoOp, Intlit, Ident, ToBy, Every, If, Alt, Compound, Mutual, Call,
RepAlt, Not, etc.) translated to BB_t* pointer assignments. This is the implementation spec.

### NEXT STEP: Resolve the BB_SEQ γ-chain overload

The BB_SEQ γ-chain overload is the **architectural obstacle** blocking deep threading.
Options:

**Option A — Add a `seq_next` field to BB_t** (clean but requires struct change):
BB_SEQ's walker uses `seq_next` for operand-chain; γ becomes pure control flow.
BB_t is declared FINAL per GOLDEN BB RULE — this needs Lon's decision.

**Option B — Per-construct migration** (safest, no struct change):
Convert one TT_* case at a time from `lower_icn_expr_node` into `lower_icn_expr_threaded`
with proper recursive child builds — NULL γ/ω to children for those that are BB_SEQ members,
explicit wiring only where bb_exec does NOT walk γ-chains. Gate after each case. The irgen
wiring map is the spec. Order: leaves first (TT_ILIT/TT_VAR), then TT_TO_BY, TT_EVERY,
TT_IF, TT_ALTERNATE (N-arm), TT_SEQ (CONJ), TT_FNC (CALL), TT_SEQ_EXPR last.

**Option C — Emitter-time threading** (deferred):
Keep lower_icn_expr_node unchanged; let the emitter thread γ/ω at emit time by walking
the BB graph with irgen knowledge. No mode-2 risk. Requires emitter changes.

### J-4a remains open

`--run` (mode 3) is globally stubbed. Phase J: generators need flat-wired x86 in the SM
template. The EVERY back-edge bug (lower_every in lower.c) is fixed. SM_BB_SWITCH ICN_GEN
arm template exists. What remains: implement four-port literal generator x86 in
`bb_icn_to_by.cpp` / `bb_icn_to.cpp` hollow PLATFORM_X86 arms so mode-3 can execute.

---

## SESSION SETUP

```bash
git clone https://TOKEN@github.com/snobol4ever/.github /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/one4all  /home/claude/one4all
git clone https://TOKEN@github.com/snobol4ever/corpus   /home/claude/corpus
cd /home/claude/one4all
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
bash scripts/test_smoke_icon.sh            # PASS=5
bash scripts/test_smoke_unified_broker.sh  # PASS=23
bash scripts/test_icon_all_rungs.sh        # PASS=198
```

---

## KEY FILES CHANGED THIS SESSION

- `src/lower/lower_icn.c` — added `icn_kind_is_resumable`, `icn_kind_owns_omega_operand`,
  `lower_icn_expr_threaded`, updated `lower_icn_proc_body` to use it
- `src/lower/lower_icn.h` — exported `icn_kind_is_resumable`, `lower_icn_expr_threaded`

**one4all** `aca30894`

---

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
