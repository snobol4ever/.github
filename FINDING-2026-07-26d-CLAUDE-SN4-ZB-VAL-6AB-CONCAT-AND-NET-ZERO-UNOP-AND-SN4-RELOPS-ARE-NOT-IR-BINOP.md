# FINDING — ZB-VAL-6a/6b: CONCAT + net-zero UNOP land; SNOBOL4 relops are NOT IR_BINOP (s179, 2026-07-26)

**SCRIP commits:** `044d2ccc` (ZB-VAL-6a/6b) · `92e926cf` (feature artifacts).
**Corpus:** `2cf53f35` (benchmarks) · `3df944f3` (demos).
**Watermark: m3 314/1 · m4 312/1 · DIVERGE=0 — WATERMARK-EXACT after EVERY rung** (sole fail `test_case`, pre-existing).
icon 14/14×2 · prolog 5/5×3 · raku 695/695×2 · all-langs hello 6/6 ROWS_DRIFT=0 (run after the `zeta_storage.c` touch — the scan runs for every language's graphs).

⚠ **WATERMARK DISCREPANCY, UNRESOLVED — for Lon.** `scripts/test_crosscheck_snobol4.sh` reports **m3 314/1 · m4 312/1**, which is exactly **s176's** cursor number, NOT s178's claimed **m3 332/2 · m4 323/1**. Measured three times this session (baseline-equivalent, post-6a, post-6b) — identical every time. Either s178's watermark came from a different/wider runner than this script, or it is prose that outran its measurement. This session reports the number the script printed. **Do not treat 332/323 as this script's baseline until someone names the runner that produces it.** (Same rule shape as s47's PUSH-PENDING finding: the script is the truth, the prose is the rot.)

## What landed (Lon directive: each BB allocates its RESULT if used + LOCALS if any, ONE instruction, offsets from RSP)

6. **ZB-VAL-6a CONCAT** — THE SNOBOL4 operation joins the spine. `fc_vbinop_ok` admits `BINOP_CONCAT`
   alongside ADD/SUB/MUL; `IR_LIT_STRING` joins `IR_LIT_INTEGER` as a tree leaf. `bb_binop_concat_slot`
   gets a `vfcc()` arm: reads lhs `[rsp+16/24]` / rhs `[rsp+0/8]`, ONE `str_concat_d` call, then the
   same ONE-INSTRUCTION net `add rsp,16` (release both operand cells + carve RESULT).
   **It needs NO fast/overload/generic ladder and NO omega edge** — unlike the arith arm, because
   `str_concat_d` is TYPE-BLIND: it owns both the to-string coercion AND the null-string identity
   (manual p.22 — *if either operand is the null string the other is returned UNCHANGED, not coerced*).
   Oracle-verified: `Y = (20 - 17) ''` → `3` / `DATATYPE=INTEGER` in SPITBOL, m3, and m4 alike.
7. **ZB-VAL-6b UNOP** — `TT_MNS`/`TT_PLS`, and **those two only**. Manual p.181 is the authority: SNOBOL4's
   unary set is `@ ~ ? & + - * $ .` and unary `*` is **DEFER, not size** — so `TT_SIZE`/`TT_CSET_COMPL`
   (other languages' shapes) stay off this rung.
   **THE NET IS ZERO.** Release 16 + carve 16 cancel exactly, so the box emits **no rsp instruction at
   all** and writes its result straight over its operand in place. Byte-read from the `.s`: the whole
   `n3_unop_α` body is `mov rdi,[rsp+0]` / `mov rsi,[rsp+8]` / `call rt_num_neg` / `mov [rsp+0],rax` /
   `mov [rsp+8],rdx`. `rt_num_neg`/`rt_num_pos` own the string→number coercion and the null-string-is-0
   identity (manual p.22); both are infallible, so no ω edge here either.
   Mechanics: unops SHARE the `fvb` operator registry (`fc_vbinop_active` relaxed to accept `IR_UNOP`)
   and are therefore counted against **its** cap, not the leaf cap — a miscount there is the exact shape
   of the ZB-VAL-0 partial-quartet latent. Depth simulation: `d` UNCHANGED (one cell consumed, one
   produced). A unop may also be the tree ROOT (`X = -Y`), so the entry gate widened too.

Geometry byte-read end to end on `X = 'AB'` / `OUTPUT = X 'CD'`: `sub rsp,16` (var) · `sub rsp,16` (lit) ·
read `[rsp+16/24]`+`[rsp+0/8]`, `add rsp,16` net (binop) · `add rsp,16` release (assign). **rsp balanced,
ZERO rbp anywhere in the statement.**

## ⭐ β-DEAD INVARIANT — now CONFIRMED EMPIRICALLY, not assumed
`x86_beta_trampoline()` is `β-label + jmp ω`, and the `X86H_JMP`+`X86P_OMEGA` site is **exactly** where
`op_wpop` is spent (x86_asm.h ~1761). So a live β trampoline on a registered box would spend the full
`d*16` at a moment when only `(d-1)*16` is actually live — an over-pop of 16 per operand consumed.
**It never fires: on the value spine `op_beta_dead` is true and NO trampoline is emitted** (verified by
absence from the `.s` on every spine statement inspected). THIS is what makes the uniform `wpop = d*16`
registration safe — the only ω exits are α-time failure edges, where the full depth genuinely IS live.
Write this down: it is load-bearing for every rung after this one, and it was previously implicit.

## ⛔ THE RUNG LADDER IS WRONG ABOUT ZB-VAL-7 — SNOBOL4 RELOPS ARE NOT `IR_BINOP`
s178 names **ZB-VAL-7 relops (`IR_BINOP_TEST`)** as a next-rung candidate on the roman/SNOBOL4 anchor.
**Measured: unreachable from SNOBOL4 source.** `LT(A,B)` does not lower to an `IR_BINOP` of relop
category at all — the emitted boxes for `X = LT(A,B) 'yes'` are `n7_op75` / `n9_op75` / `n10_op77`
(the COERCE/CMP family), whose bodies are DT-code tests and `lea` on **`[rbp+...]`** slots, feeding a
plain `IR_BINOP` concat. `binop_slot_kind`'s `BINOP_CAT_RELOP` arm is fed by Icon/Raku/Snocone infix
relops, not by SNOBOL4 — SNOBOL4 has no infix relational operator (manual p.182's binary table lists
none; the predicates are FUNCTIONS `EQ/NE/GT/GE/LT/LE/LGT` that SUCCEED or FAIL, manual p.32).
**Consequence:** ZB-VAL-7 is an ICON/RAKU-anchored rung, and doing it does not advance the roman anchor.
The SNOBOL4-anchored continuation is the **COERCE/CMP family** the predicates actually decompose into
(`IR_COERCE_NUMERIC` / `IR_COERCE_REAL` / `IR_CMP_TEST`) — and THAT is where the spine first meets a
routinely-taken ω, because a failing SNOBOL4 predicate fails the STATEMENT (F() goto / fall-through),
unlike the arith DT_FAIL edge which ZB-VAL-5 could only byte-verify and never run (that latent stands).

## THE WALL — still not hit
Seven rungs, zero rbp dependency. Offsets stay rsp-relative and STATIC because the compile-time depth
simulation IS the sliding-offset tracking. The wall's outline is unchanged from s178: SPD-2 scanfail does
`rsp = rbp` frontier restore, so pattern-scan RETRY already anchors on rbp — the spine meets it when value
cells coexist with scan retries in one statement, and ω-merge-depth (one label, two arrival depths) is the
same wall from the failure side, still fenced by single-depth-arrival registration. **6a/6b did not
approach it**: concat and unop are both infallible, so neither adds an ω arrival at all.

## LATENT (noted, not chased)
- `OUTPUT = 19 (2. / 3.)` (manual p.21, verbatim from the concatenation section) is a **PARSE ERROR** in
  SCRIP — real-literal inside a concat. Pre-existing, same family as s175's GT/lexer latents. SPITBOL
  prints `190.666666666666667`.
- `x86("comment", …)` still does not render in mode-4 `.s` (s178 noted it; still true, cosmetic).
- The feature tests under `test/snobol4/**` have **no `.ref` files** — `.s` artifact diffing plus the
  crosscheck are the verification instruments there, not ref comparison. Worth knowing before someone
  writes a gate that assumes refs exist.
- Registered producers still receive their (now-unread) flat rbp slots — the DIET rung, unchanged.

## BLAST RADIUS (measured against committed artifacts, not estimated)
21 of 155 feature tests changed their `.s`, ALL concat-adjacent (the 6 `concat/*`, the 3 `strings/word*`,
`literals`, `coverage_sno_nodes`, the 4 `library/*`, `055_pat_concat_seq`, `060_capture_multiple`,
`fileinfo`, `086_define_locals`, `1012_func_locals`, `1016_eval`). Plus 15 benchmark and N demo artifacts.

## NEXT RUNG CANDIDATES
**ZB-VAL-8 COERCE/CMP** (the SNOBOL4-anchored one — `IR_COERCE_NUMERIC`/`IR_COERCE_REAL`/`IR_CMP_TEST`
on the spine; FIRST routinely-taken ω, so the wpop mechanism finally gets exercised at runtime rather
than byte-verified) · **ZB-VAL-7 relops** (re-labelled ICON/RAKU-anchored, `IR_BINOP_TEST`) ·
then the DIET (elide registered producers' flat slots).
