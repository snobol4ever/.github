# HANDOFF 2026-06-02 — Claude Sonnet — ICON-BB bb_call + bb_unop → x86() medium-invisible

**Goal:** GOAL-ICON-BB.md — x86() TEMPLATE-REVAMP (the ▶ CURRENT PRIORITY)
**SCRIP HEAD:** `0b7a166`
**.github HEAD:** (this commit)

---

## One-line summary

Converted the last two Icon BB boxes carrying raw-byte producers (`bb_call`, `bb_unop`)
onto the `x86()` self-encoding front-end. **`scripts/test_gate_template_medium_invisible.sh`
now reads 0 for all Icon boxes** (was 61). Purely structural — byte-identical machine code,
zero behavioral change.

---

## What landed (SCRIP `0b7a166`)

3 files, +60/−70.

### `x86_asm.h` (additive, shared — append-only, no peer collision)
- **`x86_neg(reg)`** — REX.W `NEG r/m64` (`48 F7 /3`) + `"neg"` case in `x86(mnem, op1)`
  (beside push/pop/idiv). Byte-verified vs ` neg <reg>` TEXT form.
- **`x86_pair_jmp(idx)`** — emits the in-band `E9` + `'F' idx` pair-loop jmp record (the
  non-omega β target). Mirrors the jmp half of the existing `x86_pair_loop()`. BINARY emits
  the record stream `bb_emit_x86` discovers; TEXT emits ` jmp <pairname>`. This replaces the
  7 hand-written `x86_Lrec(x86_b1(0xE9)); s += 'F'; s += 0;` sequences that were the last
  raw-byte sites in `bb_call`.

### `bb_unop.cpp`
- NEG arm: `x86_Lrec(x86_b3(0x48,0xF7,0xD8))` → `x86("neg","rax")` (1 site). `bb_unop` was
  already bb_bin_t-free (`ce64450`); this was its one residual raw byte.

### `bb_call.cpp` (all 60 sites)
- `movabs rdi,ptr` + `call rax`  → `x86("mov","rdi",ptr64)` + `x86("call",sym,fptr)`
- frame loads/stores            → `x86_frame_load64` / `x86_frame_store64` (existing)
- RO-int literal / strlit ptr   → `x86_ro_load_q` + `x86_ro_seal_q` (existing REG-RO encoders)
- `E9 'F' 0` β-jmp              → `x86_pair_jmp(0)` (new)
- `mov32 edx/esi,imm`           → `x86("mov32",reg,imm)` (existing)
- `cmp eax,99` + `je`           → `x86("cmp","eax",99)` + `x86("je",PORT_OMEGA)` (existing)

The BINARY arms now emit byte-identical code via the encoders (the whole point of the revamp:
one description, medium switched invisibly inside the encoder).

---

## IMPORTANT — what this slice did NOT do

`bb_call` **keeps its `pBB` parameter**. It still reads neighbor nodes (`subs[i]->entry`,
`pBB->α`, `pBB->counter`) for argument marshaling. The full **no-`pBB`/`_.node` FACT-RULE**
conversion — where the driver (`emit_bb.c`/`emit_core.c`) resolves operand slots and promotes
them to `g_emit` scalars BEFORE the box is called (as `bb_binop_arith` / `bb_unop` / `bb_binop_relop`
already do) — is a SEPARATE later step. This slice cleared ONLY the raw-byte/medium-branch debt,
which is precisely what the three medium gates (`medium_invisible`, `no_bb_bin_t`,
`no_handencoded_bytes`) measure. They are all 0 now; the pBB-removal is orthogonal and not gated
for `bb_call` yet (it genuinely needs the driver-side operand promotion built first).

---

## Gates at handoff (all green / byte-stable)

- **medium-invisible: 0** (was 61) ✅ — the headline result
- bb_bin_t: 0 ✅
- no-handencoded-bytes (b.size): 0 ✅
- no-stack: 8 ≤ 127 ✅
- one-reg-frame: 0 ≤ 21 ✅
- FACT (bytes outside templates): 0 ✅
- purity audit: 2 (sanctioned BINARY rel32 idiom in `bb_call`+`bb_every` — exempt)
- Icon smoke: **m2 12/12 HARD** · m3 3/12 · m4 3/12 (m3/m4 pre-existing GZ-11+ gaps)
- Icon corpus: **m2 127 HARD** · m3 5 · m4 5 · EXCISED 33 — **byte-identical to baseline**
  (verified by stash/rebuild/compare)
- Prolog smoke: m2 5/5 HARD
- crosscheck: PASS=1 FAIL=3 — **identical with changes stashed** (FAILs = concat/if_expr/every_to
  = the STILL-OPEN relop/concat/generator tiers, NOT a regression)

---

## NEXT (Icon divvy-up — TEMPLATE-REVAMP)

Remaining Icon boxes with raw byte counters: `bb_iterate`(17), `bb_binop_gen`(11), `bb_upto`(6),
`bb_to_by`(5), `bb_to`(5), `bb_alt`(5), `bb_seq`(4), `bb_suspend`(2).

**Start with the smallest pair-driven leaves: `bb_seq`(4) or `bb_suspend`(2).**

**CAUTION (recorded in the watermark, learned from `bb_every`):** the looping/pair-driven boxes
(`bb_seq`, `bb_alt`, the combinators) discriminate their arms on **MEDIUM, not `g_icn_flat_chain`**
(the flag is cleared by the time the pair-fill walker reaches them). Expect the variable-length
`D`/`J` / `x86_pair_loop()` idiom since their pair count is runtime-variable (unlike succeed/every's
fixed count). `x86_pair_loop()` already exists in `x86_asm.h` and reads `g_emit.xa_bb_emit_pair_*`.

Beyond the revamp, the open Ground-Zero rungs (native m3/m4 lighting) remain: GZ-DEFER (EVAL/CODE/`*P`
per `test_sno_3.c`), the relop/concat tiers (need a STRING REG-RO analogue so IR_LIT_S produces a
slot), and generator-operand binops (Proebsting Fig-1 native).

---

## Session setup for next session

```bash
git clone https://TOKEN@github.com/snobol4ever/.github.git /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/SCRIP.git /home/claude/SCRIP
git clone https://TOKEN@github.com/snobol4ever/corpus.git /home/claude/corpus
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
bash scripts/test_smoke_icon.sh                 # m2 12/12 HARD
bash scripts/test_gate_template_medium_invisible.sh   # 0
# Canonical sources (from uploaded zips or clone):
mkdir -p refs && cd refs
# unzip the uploaded icon-master.zip / jcon-master.zip here, OR:
# git clone https://github.com/proebsting/jcon jcon-master
# git clone https://github.com/gtownsend/icon  icon-master
```
