# HANDOFF — 2026-06-10 — BB-FIXUP 40th attended run (Opus 4.8) — RING STOP bb_assign_frame.cpp 66→9

**Run shape:** RING STOP (first since the 37th — 38th/39th were Lon-directed bb_alt redos that parked the cursor here). Cursor file `bb_assign_frame.cpp` swept under OPERATING MODE v3 + all CONVERSIONS CV1-CV10. Lon attending, context % each turn; opened ~25%.

## Landed — SCRIP (on origin)
**`bb_assign_frame.cpp` 66 → 9 violations.** Cleared completely:
- **bypass 17→0** — every `x86_frame_*`/`x86_reg_disp32_*` bypass call replaced by `x86("mov"/"lea", reg, FRQ(off)/RDQ(base,off))`. NEW `RDQ(base, off)` speller added in `x86_asm.h` beside `FRQ`/`ROQ` — emits `qword ptr [base + off]`, parses to XK_REGDISP, routes to the SAME byte-verified `x86_reg_disp32_*` encoders (24th-run dispatch). Zero-emit fragment builder.
- **medium_any 1→0** — the `IF(MEDIUM_TEXT, x86("label")+x86("comment"))` head-wrapper dropped; encoders are medium-complete post-7b.
- **sig_decls 3→0**, **over_col 4→0**, **multi_x86 9→0** (one `x86()` per line).
- **hc 13→3** — the `baf_*` multi-emit constellation (`baf_lit_i/nul/s/var/vframe/vfref/binop/call/arm/hdr/known`) DELETED; arms inlined into a single one-return lazy-IF chain keyed on `_.bb_lk`. KEPT `baf_voff/baf_soff/baf_hop/baf_srchop` as zero-emit value+fragment builders. The canonical `audit_multi_emit_helpers.py` reports **0 INLINE+DELETE candidates** for the file — `baf_hop`/`baf_srchop` are fragment builders (return a `std::string` spliced into arm expressions), not 8b multi-emit helpers.

### CONVERSIONS applied
- **CV1** R1 terse comment: `x86("comment", "IR_ASSIGN_FRAME")`.
- **CV9** parameterless: `bb_assign_frame(void)`; dispatch `bb_prepare(nd); bb_assign_frame();`.
- **CV10** IR-graph-free: NEW `bb_prepare` IR_ASSIGN_FRAME block classifies the RHS operand kind into `_.bb_lk` (1=LIT_I 2=LIT_NUL 3=LIT_S 4=VAR 5=VAR_FRAME 6=VAR_FRAME_REF 7=BINOP 8=CALL 0=unknown — the IR_UNIFY `bb_lk` precedent) and interns the LIT_S/VAR label into `_.bb_ls` via `bb_intern_into`. The template reads ONLY scalars — zero `pBB`/`_.node`/`IR_t`/`bb_operand_aux_get`. The old `baf_known()`/`baf_arm()` IR-enum dispatch is GONE.
- **CV8** platform fence: `if (PLATFORM_X86) return ...;` then fallthrough `return std::string();` — the predicate never enters an IF() combinator.

### Proof
- 5 probes covering ALL 8 arms: `nestfunc`=LIT_I, `alias`=BINOP, `swap`=VAR_FRAME+VAR_FRAME_REF, `arr2dtype3`=CALL, `pcom`=VAR+4-arm mix.
- bbN+LxN-normalized asm-diff EMPTY on alias/arr2dtype3/pcom; sole delta on nestfunc/swap = the sanctioned R1 comment collapse (`# BOX IR_ASSIGN_FRAME "x" slot=.. hops=.. rhs_kind=..` → `# IR_ASSIGN_FRAME`). Instruction streams BYTE-IDENTICAL.
- Behavior m2=m3=m4 parity on all 4 runnable probes (swap `8`/`3`, alias `11`, arr2dtype3 `30`, nestfunc `11`).
- `pcom` rc=134 is PRE-EXISTING — identical abort on A and B sides (`[IBB] FATAL flat_drive_assign: lhs (α) must be IR_VAR with sval (got kind=156)` — an unrelated box, not this file's). It emits the full 8788 lines on both sides; the asm-diff over the emitted prefix is EMPTY.

### Residue TOTAL=9 (zero real violations)
- **rp=6** — FOR-lambda returns + `baf_hop`/`baf_srchop` helper returns + the CV8 platform-fence return. The rp counter is blind to lambda + fence returns (the standing counter-scope verdict).
- **hc=3** — the `grep -c ^static` minus-2 heuristic over the 4 zero-emit builders, CONTRADICTED by the canonical multi-emit detector (0 candidates).
- Matches the bb_alt precedent exactly (its residue was rp=3 from FOR-lambda + CV8-fence, declared sanctioned).

## Gates at floors (after build)
smoke m4 7/7 HARD · pat M4 19/0 · icon m2 12/12 HARD m3=m4 10/2 · prolog m2 5/5 HARD m3=m4 5/5 · prove_lower 68P · purity 2 (bb_assign_frame NOT listed) · bin_t 0 · vstack 3 · sno_pat_reg HARD · **med_inv: bb_assign_frame DROPPED OUT (1→0)**.

## Re-rank
115 files / 109 dirty / 6 clean / GRAND **2436** (foreign drift from the 39th-run 2488 ceiling via LAD-2c pascal + IRD renames between runs; my −57 included in this reading). `bb_assign_frame` STAYS in the dirty bucket (9 counter-residue).

## ⛔ Concurrent absorbed at push — Pascal NL default flip (e5ee443)
`e5ee443` (CONVERSION: pascal production lowering = `lower_pascal_nl`, default flipped) + its prereqs (1eff001 LAD-2c execution channel, etc.) landed during this session. **My probes are ALL pascal**, so this directly touches the lowering my asm-diff proof depends on. Rebased onto it and RE-PROVED on the combined production head per the 8th-run precedent:
- Built A' (pre-FIXUP 4-file state) and B' (FIXUP) both on the flipped-default tree; isolated my template's sole effect.
- bbN+LxN-normalized asm-diff A' vs B' on production lowering: **EMPTY on alias + arr2dtype3; swap sole delta = the sanctioned R1 comment**. Instruction streams BYTE-IDENTICAL. The VAR_FRAME_REF (swap), BINOP (alias), CALL (arr2dtype3) arms all re-proven on the flip.
- Behavior on flip: m2=m4 parity (alias 11, swap 8/3, arr2dtype3 m2=30 / m4 empty — arr2dtype3 m4 is empty on A' TOO = pre-existing, not mine).
- nestfunc/pcom no longer route through this box under the flip (0 boxes) — coverage preserved via alias/swap/arr2dtype3.
- Combined-head battery at floors: smoke m4 7/7 HARD · pat M4 19/0 · icon m2 12/12 HARD · prolog m2 5/5 HARD · purity 2 · bin_t 0 · vstack 3 · sno_pat_reg HARD. The flip regressed nothing of mine.


```bash
apt-get install -y libgc-dev
bash scripts/build_scrip.sh
make libscrip_rt        # icon/prolog m4 smokes read 0 until this exists
```

## CV10 class implication (re-confirmed)
A multi-arm box whose per-arm shape is driver-deliverable reaches near-clean via `bb_prepare` relocation + lazy-IF one-return — NO LOWER split needed. The [S]/split is required ONLY where the inquiry IS lowering (shape → different four-port logic), not mere operand delivery. Re-read each [S] on arrival.

## Lon verdicts outstanding (unchanged)
Standing 6: x86_movimm uint32-trunc (bb_call_fn) · prove rc=0-on-FAIL hardening · PL-GZ-8 arith-is 2-vs-5 (owner PL-GZ) · m2 disj-backtrack silent-empty (owner PROLOG-BB) · IRD-2b IR_t.own ratify · ml comment-substring false-positive. Plus: counter-scope trio (rp/hc/lv vs sanctioned forms — this run is a fresh datapoint: rp=6 hc=3 ALL sanctioned) · bb_arith dead-dispatch retirement · ceiling-ratify · c3b1dbb alternation-in-every regression (owner ICON-NL) · two-chunk template design.

## Next session
Cursor stop `bb_assign_frame_ref.cpp` (ring successor). Per the 38th-run class note its [S] is likely a CV10 driver-prep relocation rather than a LOWER-split wait — re-read on arrival. Its byref VAR_FRAME_REF lowering parallels this file's arms 5/6, so the same `_.bb_lk` + RDQ treatment likely applies.
