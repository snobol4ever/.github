# HANDOFF — 2026-05-27 (session c) — Opus 4.7 — GOAL-ICON-BB: ICN-XA-1 + ICN-M4 binop-gen

**SCRIP** `7ff8fce8` · **goal:** GOAL-ICON-BB · **mode priority:** mode 2 then 3 (mode 4 deferred,
but the mode-4 generator gate was the cheapest correctness signal available this session)

---

## WATERMARK

GATES: smoke_icon **5/5** · broker **23** · icon_all_rungs **198** · smoke_prolog **5/5** — ALL
UNCHANGED. **mode4_rung PASS=2→5 FAIL=0.** FACT RULE grep **0**.

---

## THE KEY FINDING (corrects the prior watermark)

The prior session's "sharper target" said `lt`/`mult`/`compound` were a TEMPLATE-ONLY fill of
`bb_binop_gen.cpp` (because the mode-2 BB graph has a single BB_BINOP_GEN with α/β operand boxes).
**That was wrong for mode-4.** Tracing the actual mode-4 lowering (`--dump-sm`):

```
mult: every write((1 to 3)*(1 to 2))
  2  SM_BB_SWITCH   (1 to 3)   <- outer
  4  SM_BB_SWITCH   (1 to 2)   <- inner
  6  SM_MUL                    <- flat multiply
 10  SM_JUMP -> 2              <- back-edge re-drives ONLY the outer switch
```

`lower_mul`/`lower_acomp` (lower.c) emitted a FLAT scaffold of two independent `BB_TO` graphs +
`SM_MUL`. `bb_binop_gen.cpp` was NEVER reached in mode-4. The single every-loop back-edge cannot
express a cross-product. So the fix needed BOTH a lowering change AND the template fill.

## WHAT WAS DONE (3 pieces, all verified non-regressing)

1. **ICN-XA-1 — `walk_bb_node_str_c`** (`emit_core.c` + `emit_core.h`). `BB_t* → char*`: swaps the
   shared emit sink (`bb_emit_out`) to an `open_memstream` FILE* around the EXISTING `walk_bb_node`
   dispatch, flushes, restores. Caller frees. **Not a second producer** — every byte still comes from
   the keyed template fns reached via `emit_core` dispatch (FACT RULE grep stays 0). Rewired
   `sm_bb_switch.cpp` ICN_GEN arm to `pre + walk_bb_node_str_c(gen) + post`; the LOCAL-PURGE violation
   (`emit_text_n` + `walk_bb_node` mid-`_str()`) is GONE.

2. **Generator-binop routing** (`lower.c`). New `lower_icn_gen_binop(t)`: if an Icon arith/relop binop
   has a suspendable operand, register the WHOLE subtree as ONE BB graph (`lower_icn_expr_top` →
   BB_BINOP_GEN, α=lhs β=rhs operand boxes) and emit a SINGLE `SM_BB_SWITCH` — exactly like `lower_to`.
   `lower_add/sub/mul/div/mod/acomp` call it first; on miss they emit the old flat form. Mode-4 now
   routes generator-binops through `bb_binop_gen.cpp`. (`mult` SM dump is now ONE switch, like `to5`.)

3. **`bb_binop_gen.cpp` real odometer** (TEXT/mode-4). Inline x86 cross-product mirroring `bb_exec.c`
   BB_BINOP_GEN (688-762):
   - α (fresh): state=1; enter lhs box α (seed outer). lhs.γ → pop value to `lv`, seed rhs (enter rhs
     α). rhs.γ → pop value to `rv`, apply. lhs.ω → parent ω. rhs.ω → advance lhs (enter lhs β).
   - β (resume): advance inner (enter rhs β).
   - apply: push lv, push rv; `rt_arith`(arith) or `rt_acomp`+`rt_last_ok`(relop). relop-fail → discard
     FAIL + advance; success → parent γ.
   - Operand boxes emitted INLINE: generators via `walk_bb_node_str_c`; `BB_LIT_I` single-shot via
     `synth_single_shot_box` (α pushes the literal, β→ω). Non-int single-shot → `[inline TODO]` ω-stub.
   - **DESCR_t pop reads union `.i` from `rdx`** — the 16-byte struct SysV ABI puts `v|slen` in rax,
     the union in rdx. (Reading rax gave the all-`36` bug.)
   - Child labels are **non-static** (nested BINOP_GEN / `compound` recurses through
     walk_bb_node_str_c → bb_binop_gen reentrantly; static storage would alias across levels).

Results: `lt`→`3 4`; `mult`→`1 2 2 4 3 6`; `compound`→`4 6` — all byte-exact vs `--interp`.

## WHAT REMAINS (NEXT-SESSION ENTRY POINTS)

**ICN-M4 follow-on (documented, not blocking):**
- `synth_single_shot_box` handles only `BB_LIT_I`. Add `BB_VAR` / `BB_KEYWORD` / non-int literals
  (these currently fall to a `[non-gen … inline TODO]` ω-stub → generator yields nothing).
- DT_I round-trip in the apply path assumes integer operand generators (true for the gate seed set).
  Real/string operand values need a descr-preserving holding cell (store full DESCR_t in the `.data`
  cell — 16 bytes — and re-push with a descr-push helper, not `rt_push_int`).
- `bb_binop_gen.cpp` BINARY (mode-3 brokered) arm is still the α→γ/β→ω passthrough stub. Author the
  raw-byte odometer when mode-3 resumes (mirror the TEXT logic; r12 vstack convention).

**Still open from prior watermarks:** ICN-Z-2 explicit ω→α port wire (mode-3/4); ICN-Z-3 BB_CONJ
(needs the full one-pass bb_exec.c port-follower conversion); ICN-Z-4..9 zipper; J-4..6 mode-3.

## SESSION SETUP

```bash
git clone https://TOKEN@github.com/snobol4ever/.github /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/SCRIP  /home/claude/SCRIP
git clone https://TOKEN@github.com/snobol4ever/corpus   /home/claude/corpus
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt                            # required for the mode-4 gate
bash scripts/test_smoke_icon.sh             # PASS=5
bash scripts/test_smoke_unified_broker.sh   # PASS=23
bash scripts/test_icon_all_rungs.sh         # PASS=198
bash scripts/test_icon_mode4_rung.sh        # PASS=5 FAIL=0
```

## FILES CHANGED

- `src/emitter/emit_core.c` / `.h` — `walk_bb_node_str_c`
- `src/emitter/SM_templates/sm_bb_switch.cpp` — ICN_GEN arm now pure (uses walk_bb_node_str_c)
- `src/lower/lower.c` — `lower_icn_gen_binop` + routing in lower_add/sub/mul/div/mod/acomp
- `src/emitter/BB_templates/bb_binop_gen.cpp` — real cross-product odometer

**SCRIP** `7ff8fce8`

---

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
