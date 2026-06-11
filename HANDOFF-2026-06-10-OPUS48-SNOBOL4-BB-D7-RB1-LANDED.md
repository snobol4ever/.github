# HANDOFF — 2026-06-10 · Opus 4.8 · D7-RB-1 LANDED (053 PARITY m2==m3==m4)

**SESSION WATERMARK — 2026-06-10 · Opus 4.8 · D7-RB-1 LANDED — 053 PARITY m2==m3==m4 → `b`. NEXT = D7-RB-2.** Pattern-VARIABLE builders now route through the RT functions in all three modes. Gates: smoke 7/7/7 · pat-rung M2 19/19 · M3 19/19 (both 18→19, +053) · M4 16/19 (053 PASS; 050/051/054 = pre-existing b11a963) · fence HARD · --dump-sno OK · m4 spot-check 12/12 clean. Full goal state: `GOAL-SNOBOL4-BB.md` watermark (single source of truth).

---

## WHAT 053 IS (and why it was the lone m2/m3 hole)

`053_pat_alt_commit.sno`: `P = ('a' | 'b' | 'c')` (a pattern-VALUED variable), then `X = 'b'`, then scan `X P . V`. Oracle (`sbl`) → `b`. It is the inverse of 050/051/054 — those are ANONYMOUS in-scan patterns (IR_PAT_* MATCH family, interpreted directly in m2) that fail M4 only; 053 is the only NAMED-variable test (IR_PATTERN_*/IR_DTP_ASSIGN BUILDER family) and failed m2/m3 only.

Two distinct node families (do not confuse — this cost time):
- `IR_PAT_LIT`/`IR_PAT_ALT`/`IR_PAT_DEFER`/`IR_PAT_ASSIGN_COND` = MATCH family (dump shows `PAT_*`). Match against the subject directly; interpreted in m2 by `IR_interp_node`; emitted as `bb_match_*` in m3/m4.
- `IR_PATTERN_LIT`/`IR_PATTERN_ALT`/`IR_DTP_ASSIGN` = BUILDER family (dump shows `PATTERN_*`/`DTP_ASSIGN`). CONSTRUCT a reusable DT_P object; emitted as `bb_pattern_*`/`bb_dtp_assign`.

053 IR (from `--dump-bb`): main graph builds P via PATTERN_LIT 'a' → PATTERN_LIT 'b' → PATTERN_ALT[a,b] → PATTERN_LIT 'c' → PATTERN_ALT[ab,c] → DTP_ASSIGN("P", ops:[alt]). The SCAN's sub-graph is PAT_ASSIGN_COND("V") → PAT_DEFER("P"). Each builder stores its DTP_FRAG_t* in its own `IR_EXEC(node).counter`; ALT reads ops[0]/ops[1] counters; DTP_ASSIGN reads ops[0].

## ROOT CAUSE (verified empirically, not assumed)

- Production: builder nodes had NO m2 arm (fell to default → m2 empty) and binary templates were `ins*`-only (emit nothing → m3 corrupt DT_P → segfault once the consumer ran it). m4 worked because TEXT `ins*` emit.
- Consumption: `IR_PAT_DEFER` (`IR_interp.c`) — its `DT_P` branch was a hard `abort()` (`[B0] BOMB IR_PAT_DEFER…`), NOT an `rt_dtp_run` call. Both m2 (`--interp`) and m3 (`--run`, whose native scan box calls back into IR_interp for the pattern sub-graph) funnel through this arm.
- The pat pool is `__attribute__((constructor))` + mmap RWX (`pat_pool.c`), so building/executing DT_P blobs in m2 is safe.

## THE FIX (7 files, +146/−159 — templates SHRANK)

| File | Change |
|---|---|
| `src/runtime/pattern_match.c` | + `rt_dtp_head_build(frag,varname)` (36B head proto: 3 quads {entry,out_γ,out_ω} + 2 jmp thunks; patch entry, point frag γ/ω sites at thunks, `rt_gvar_assign_pat`). + shared `const uint8_t bb_lit_proto[125]` and `const DTP_PROTO_DESC bb_lit_proto_desc = {47,32,16,24,-1,0,8}` (verified bytes). + fwd-decl `rt_gvar_assign_pat`. |
| `src/include/dtp.h` | + decls for `rt_dtp_head_build`, `extern bb_lit_proto`, `extern bb_lit_proto_desc`. |
| `src/interp/IR_interp.c` | + `#include "../include/dtp.h"`. + 3 m2 builder arms before `case IR_SCAN:` (PATTERN_LIT→`rt_pattern_build`, PATTERN_ALT→`rt_pattern_stitch_alt`, DTP_ASSIGN→`rt_dtp_head_build`; frag in `IR_EXEC(bb).counter`, `state` idempotency guard). + **DEFER fix**: `IR_PAT_DEFER` `DT_P` branch `abort()` → `rt_dtp_run((DTP_t*)val.p, Σ, Δ, Σlen)`, advance Δ, one-shot (`state=2`). |
| `src/emitter/emit_bb.c` | IR_PATTERN_LIT case now sets `g_emit.op_sval = IR_LIT(nd).sval` (was unset → NULL; siblings ANY/SPAN/etc. always set it). |
| `bb_pattern_lit.cpp` | Rewrite → `lea rdi,FRQ(op_off)` · `lea rsi,"[rip+__]"(proto)` (RIPSEAL: text local `.Lpb_s` / bin movabs &bb_lit_proto) · `mov32 edx,125` · `lea rcx,"[rip+__]"(desc)` · `mov32 r8d,litlen` · `lea r9,"[rip+__]"(litstr)` · stack-align · `call rt_pattern_build` · jmp γ · inline proto `raw .byte`(125) + desc `raw .long 47,32,16,24,-1,0,8` (TEXT only) · def β · jmp ω. 0 `ins*`. |
| `bb_pattern_alt.cpp` | Rewrite → `lea rdi/rsi/rdx, FRQ(off/sa/sb)` · stack-align · `call rt_pattern_stitch_alt` · jmp γ/def β/jmp ω. 0 `ins*`. |
| `bb_dtp_assign.cpp` | Rewrite → `lea rdi,FRQ(op_sa)` · `lea rsi,"[rip+__]"(varname)` · stack-align · `call rt_dtp_head_build` · jmp γ/def β/jmp ω. 0 `ins*`. |

Register convention preserved: r12=frame r13=subj r14=cursor r15=subjend are callee-saved across the C calls; rbx push/pop is the 16-align idiom only.

## DESIGN-DOC CORRECTIONS (the prior session's `…-D7-RB1-DESIGN.md` was NEVER compiled and is wrong 3 ways)

1. **ZERO `x86_asm.h` edits required.** Its shopping list was stale — `x86_and` (266/605), `mov32`/`x86_movimm32` (179/580), `XK_ROSLOT`+parser (437/469), `ROQ` (348), binary `call SYM,addr`→`x86_call_ro` (547) ALL already exist. Its new `rsi_proto_imm` is redundant with the existing RIPSEAL `lea` (text→`lea[rip+label]`, bin→`movabs`). Its `proto_len_edx`/`x86_reg_disp32_lea64` BINARY-arm worry is moot: the proto length is a compile-time constant → `mov32 edx,125` gives identical bytes both media.
2. **It OMITTED the consumer fix.** It adds the 3 builder arms but leaves `IR_PAT_DEFER` bombing on DT_P — so as written m2 would `abort()`, not pass. The `rt_dtp_run` swap is REQUIRED and is the actual gate-maker.
3. Shared proto/desc + `rt_dtp_head_build` belong in `pattern_match.c` (runtime), not in `bb_pattern_lit.cpp` — single definition the m2 interp arm AND the binary template both reference; avoids a .so-symbol-in-TEXT linker problem (TEXT keeps the proto inline; BINARY movabs's the in-process extern).

## GATES (re-run to confirm; floor)

```
bash scripts/test_smoke_snobol4.sh                                   # 7/7/7
bash scripts/test_snobol4_pat_rung_suite.sh                          # M2 19/19 · M3 19/19 · M4 16/19 (053 PASS; 050/051/054 fail)
bash scripts/test_gate_sno_pat_reg.sh                                # fence Tier1+Tier2 = 0 HARD
./scrip --dump-sno test/snobol4/patterns/053_pat_alt_commit.sno      # OK
# 3-mode corpus runner is SLOW (>110s, runs m2+m3+m4 over ~280); not completed this session — spot-check of 12 pattern progs in m4 was clean.
```

053 verify (all three → `b`):
```
./scrip --interp test/snobol4/patterns/053_pat_alt_commit.sno < /dev/null     # b
./scrip --run    test/snobol4/patterns/053_pat_alt_commit.sno < /dev/null     # b
./scrip --compile … | gcc -no-pie - -L out -lscrip_rt -o /tmp/053 && LD_LIBRARY_PATH=out /tmp/053   # b
```

## NEXT — D7-RB-2

Convert unary_i/unary_s/nullary/arb/cat the SAME way (each its own commit). Reuse the proven pattern (see goal ladder step 2). Each needs: (a) template marshal→`call rt_pattern_build` with its own proto/desc (build the proto bytes + verify vs a `rt_dtp_run` harness as the design session did for LIT/head); (b) the matching m2 `IR_interp.c` arm storing the frag in `IR_EXEC(bb).counter`. For multi-operand shapes (cat = stitch) mirror `bb_pattern_alt` (no proto, pure stitch). D7-RB-3 then closes the `P=LEN(3)` value-assign lowering gap.
