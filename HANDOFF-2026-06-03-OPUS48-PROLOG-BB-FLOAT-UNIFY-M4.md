# HANDOFF 2026-06-03 (Opus 4.8) — Prolog-BB: scalar float-unify lands in mode-4 (m4 87→89)

## TL;DR

`X = 3.14` (variable unified with a float literal) now **emits and runs natively in
mode-4**, both operand orders and float==float (dis)equality. m4 **87 → 89**; GATE-3
m2/m3 **112 → 114** (two new corpus rungs, all three modes AGREE). Mode-3 routes
float-unify through the interpreter (exactly like compound-unify), so it stays correct
without crashing. Four small touches; sibling languages and all FACT gates untouched.

## What landed

The runtime was **already** float-capable for unification (`rt_node_to_term` →
`term_new_float(dval)`; `rt_unify_const`/`rt_unify_terms` handle `TERM_FLOAT`). The only
gap was the EMITTER: `bb_unify.cpp` bombed on any float operand, and `u_build_scalar`
hard-zeroed `xmm0` (`xorps`), losing the literal's value. This is **separate** from the
deferred CAT-D float-*arith* substrate (`sqrt`/`sin`/`cos`, `rt_pl_arith_d`/`rt_pl_is_d`),
which remains open.

### Touches (3 source files + 2 corpus rungs)

1. **`src/emitter/BB_templates/x86_asm.h`** (+19, additive only — siblings byte-identical):
   - `x86_movabs_r64(dst, imm64)` — true 64-bit `mov r64, imm64` (`48 B8 <8 LE>`; the
     existing `x86_movimm` truncates to 32 bits, and the `uint64_t` `x86()` overload is
     taken by `call`). First TEXT emission of a bare imm64 in the codebase — GAS accepts
     the decimal in Intel syntax (verified vs `as`).
   - `x86_movq_xmm0_r64(src)` — `movq xmm0, r64` (`66 48 0F 6E C0`, verified vs `as`).
   - `x86_set_xmm0_double(double)` — composite `movabs rax,<ieee754 bits>; movq xmm0,rax`
     (both media; raw bytes legal here — this is the encoder header, not a `*.cpp`).
   - `struct x86_f64`/`F64(d)` + overload `x86("movsd","xmm0",F64(d))` so the template
     stays x86()-pure (mirrors the `FR`/`RSP`/`L` wrapper idiom; one logical instruction
     → fixed sequence, exactly like `x86_call_ro` = `movabs rax,fn; call rax`).

2. **`src/emitter/BB_templates/bb_unify.cpp`**: deleted the float bomb + the now-unused
   `u_float_kind`/`u_deferred_float` helpers; `u_build_scalar` gains a `double dval` param
   and emits the real `xmm0` load **only for `IR_LIT_F`** (every other kind keeps
   `xorps xmm0,xmm0` → **byte-identical** to before). The general arm reads the operand's
   `dval` straight off the `_.bb_ln`/`_.bb_rn` sidecar node-pointers — the **same**
   "bb_unify reads its operand nodes from the sidecar" mechanism the compound-unify
   landing (`374c2ff`) established; `pBB`-free, `_.node`-free, x86()-pure (medium-invisible
   bb_unify stays 0).

3. **`src/driver/scrip.c`**: `pl_rich_node_emittable`'s `IR_UNIFY` arm drops the
   `IR_LIT_F` rejection (keeps `IR_ARITH` rejected — arith-in-unify is a separate
   deferral). The **flat** gate (`pl_flat_goal_is_simple`) is **deliberately left
   rejecting** `IR_LIT_F` — see the mode-3 note below.

4. **corpus** `programs/prolog/rung42_floatunify_{bind,match}.{pl,expected}`:
   - `bind` — `X = 3.14, 2.5 = Y, …` → `3.14 2.5` (both operand orders).
   - `match` — `(2.5 = 2.5 -> …)`, `(1.5 = 2.5 -> …)` → `yes neq` (float ==/\=).

## The mode-3 hazard that shaped the design (READ before extending unify)

Admitting `IR_LIT_F` to the **flat** gate made mode-3 `--run` build float-unify as
**in-process native blobs** (`pl_flat_body_root` → `bb_build_flat` → jump in) and
**segfault**. Root cause: this is the **first** time the `bb_unify` *general arm*
(build-left → save `[rsp+0]` → build-right → `rt_unify_terms`) is exercised on the m3
in-process path — every prior unify shape took the var-var / var-const / interpreter
route, and compound-unify explicitly interprets in m3. The general arm runs fine in m4
(separate `as`+`gcc` process) but crashes in m3 in-process. Per "clean EXCISE > crashing
false-PASS," float-unify is **m4-native, m3-interpreted** (flat gate keeps rejecting
`IR_LIT_F` → m3 falls to `IR_interp_once` → correct `3.14`; m4 falls to the rich path →
native). **Do not admit `IR_LIT_F` (or compound, or any general-arm shape) to the flat
gate until the general arm's m3 in-process execution is debugged** (likely the next real
piece of work here; the m4 win is independent of it).

## Gate state (HEAD 873792f, all re-verified)

| Gate | Before | After |
|---|---|---|
| GATE-1 smoke | m2 5/5 · m3 4/5 · m4 5/5 | unchanged |
| GATE-3 rung suite | m2 112 · m3 112 · m4 87/0/25 | **m2 114 · m3 114 · m4 89/0/25** |
| PL-HY-FENCE one-box | PASS | PASS |
| medium-invisible | 343 (bb_unify 0) | 343 (bb_unify still 0) |
| no_bb_bin_t / b.size() | 0 / 0 | 0 / 0 |
| seg_byte/SL_B · g_vstack | 0 · 0 | 0 · 0 |
| siblings | Icon m2 12 · SNOBOL4 m2 7 | unchanged (x86_asm.h additive) |

The 25 m4-EXCISED rungs are unchanged (findall / retract / abolish / aggregate /
catch-throw / dcg_generate + rung10 puzzles — all the PLG-9g runtime-substrate cluster).
No float rung is among them; the GOAL note's "float-unify (IR_LIT_F)" in that list was a
blocked *capability*, now cleared.

## Still open (unchanged by this session)

- **General-arm m3 in-process crash** (above) — gating native float-unify (and any other
  general-arm shape) in `--run`.
- **Compound-nested float** — `emit_build_compound_term`'s `IR_LIT_F` arm builds
  `term_new_float(0.0)` (no xmm0 setup); a float inside a struct (e.g. `point(1.5,2.5)`)
  loses its value. Latent, no corpus test yet.
- **CAT-D float-result arith** (`sqrt`/`sin`/`cos`/…) — needs `rt_pl_arith_d`/`rt_pl_is_d`.
- All prior open items (WAM-CP-9 ITE-commit semantics, findall/catch in-process pointer
  trap, etc.) untouched.

## Build / verify

```bash
cd /home/claude/SCRIP && make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_prolog.sh          # m2 5/5
bash scripts/test_prolog_rung_suite.sh     # m2 114 · m3 114 · m4 89/0/25
# float-unify probe:
printf ':- initialization(main).\nmain :- X = 3.14, write(X), nl.\n' > /tmp/fu.pl
./scrip --interp /tmp/fu.pl; ./scrip --run /tmp/fu.pl       # 3.14 / 3.14 (interp)
bash scripts/run_prolog_via_x86_backend.sh /tmp/fu.pl       # 3.14 (native m4)
```
The suite regenerates `corpus/programs/prolog/*.s`; `git checkout HEAD -- 'programs/prolog/*.s'` to re-clean.

Authors: LCherryholmes · Claude Opus 4.8
