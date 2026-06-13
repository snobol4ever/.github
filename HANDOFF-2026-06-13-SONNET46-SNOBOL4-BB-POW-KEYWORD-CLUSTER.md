# HANDOFF 2026-06-13 · Sonnet 4.6 · SNOBOL4-BB — POW int-coercion + keyword cluster

**SCRIP HEAD:** d2d307c (rebased onto concurrent a6e0a18)
**.github HEAD:** (this commit)

---

## Baseline entering session
M2=181 M3=159 M4=149 · smoke 7/7/7 · pat-rung 19/19/19 · fence HARD
(repo HEAD was 9f0d809 + a behavior-neutral Prolog reorg 2d6487a)

## Result
M2=182(+1) M3=168(+9) M4=158(+9) · all gates HARD · **M3↔M2 gap 22→14**

---

## Rung 1 — POWER_fn int-coercion (027) · commit 966bb35 (rebased)

`src/runtime/arithmetic.c`. `POWER_fn` was the only arithmetic op ignoring the
`IS_INT(a)&&IS_INT(b) → INTVAL` convention that add/sub/mul/DIVIDE_fn all follow —
it always returned `REALVAL(pow())`, so `2 ** 8` = `256.` (real) in ALL THREE modes.

SPITBOL semantics (oracle-probed): int**non-neg-int → INTEGER (exact, via repeated
multiply — `pow`-then-truncate loses precision for large values); int**neg-int → REAL
(`2**-1`=0.5); either operand real → REAL; `0**0` → error. Now mirrors add/sub
(IS_NULL→0, coerce_numeric).

All three modes route POWER_fn (M2 `IR_BINOP`→`binop_apply` lower_common.c:56;
M3/M4 `call POWER_fn@PLT`), so one fix moved 027 fail/fail/fail → PASS/PASS/PASS.
Corpus +1/+1/+1.

## Rung 2 — SNOBOL4 keyword reads in M3/M4 · commit d2d307c (rebased)

`&LCASE`/`&UCASE`/`&ALPHABET`/`&STNO`/… lower to `IR_KEYWORD` and dispatch
(emit_core.c:462) to `bb_keyword`, which only handled the Icon keywords
(subject/pos/null/fail) and was gated on `g_descr_flat_chain`. SNOBOL4 sets
`g_gvar_flat_chain`, so FILL(IR_KEYWORD) at emit_bb.c:2901 fell to `else → op_off=-1`
→ `bb_keyword: no slot` bomb. (M2 was fine — its `IR_KEYWORD` case calls
`kw_read` then `NV_GET_fn`.)

Fix mirrors M2's `IR_KEYWORD` **exactly**, so m2==m3==m4 by construction:
- **keywords.c** — `rt_keyword_read(sval)` = strip-&, `kw_read(kw)`, `NV_GET_fn(sval)`
  fallback. The same two calls M2 makes. `kw_read` is the SHARED Icon+SNOBOL4 reader.
- **emit_bb.c:2901** — FILL allocates slot + sets op_sval when `g_gvar_flat_chain`
  too (mirror the Icon arm). One char of change.
- **bb_keyword.cpp** — guard accepts `g_gvar_flat_chain`; the unsupported-keyword
  bomb becomes a language-blind general arm copied **verbatim** from `bb_var`'s
  both-medium idiom (`mov rdi,ROQ(0)` / `call` / store rax:rdx / inline `.quad`+`.string`
  seal), swapping `NV_GET_fn`→`rt_keyword_read`. Icon's other keywords (date/clock/…)
  now also resolve via `kw_read` instead of bombing.

**+8 in M3 and +8 in M4** — cleared 081/082/089/097/099/100 and more (every test that
referenced a SNOBOL4 keyword). ICON smoke UNCHANGED (M2 12/12 HARD, M3/M4 10/2) —
the shared-box touch is safe.

---

## Gates at session end
- SNO smoke **7/7/7** HARD ✓
- SNO pat-rung **19/19/19 no-SKIP** ✓
- ICON smoke **M2 12/12** HARD (M3/M4 10/2 unchanged) ✓
- fence **HARD** ✓
- broad corpus M2=182 M3=168 M4=158

(SCRIP rebased cleanly onto concurrent a6e0a18 / `icon-m3m4-jz-fix`; rebuilt + SNO/Icon
smoke + 081 re-verified green before push.)

---

## NEXT SESSION — do-not-re-derive map (diagnosed live this session)

**Gap-closers remaining (M2 passes, M3/M4 fail):**
- **084 concat-with-CALL part** — `S = S bump(2*J)`: `gvar_seq_flatten` (emit_bb.c)
  can't flatten a function-call part → `bb_gvar_assign_concat: no parts` bomb. Fix
  needs the call evaluated into a ζ-slot first, then concatenated (not a plain
  flatten-to-parts). 096 DATA-datatype also a gap-closer (less diagnosed).

**Unary-minus / literals M3 runaway (serious; emitter rung):**
- `OUTPUT = -1` prints `-1` ~5.2M× in M3 (runaway). IR is clean
  (`LIT_I(1) → UNOP negate(op 11) → ASSIGN`). `walk_bb_node` (emit_core.c:372) emits
  `; [walk_bb_node: kind=N unhandled]` when `IR_BINOP`(ord 7) / `IR_UNOP`(8) /
  `IR_LIT_F`(2) appear as flat-chain **operands** → the chain falls through and loops.
  Note: 027 (a single-statement BINOP) emits fine; the bug is these kinds as operands
  inside the flat gvar chain (multi-statement / unary-minus / real-literal). M2 is correct.
- Same root surfaced as 6× `kind=7 unhandled` on a `2**8 / (-2)**3 / 2.0**8 / 10**9`
  battery: `(-2)**3` (-8) and `2.0**8` (256.) were dropped in M3.

**All-mode gaps (M2 also fails — raising these lifts M2 too):**
- **091/092** array subscript `A<i>` assign+access — only the `ARRAY()` create is
  emitted; every subscript op is dropped (all three modes).
- **093** table subscript. **094/095** DATA field-set — 095 M3/M4 give `10|20|10` vs
  `10|20|99` (field write not persisting); 094 aborts during M4 compile.

**Minor / latent:**
- bare `OUTPUT = &LCASE` (cset→OUTPUT) aborts in M3 at cset-print — a separate
  pre-existing cset-as-gvar-value gap, surfaced (not caused) by rung 2; previously
  masked by the `bb_keyword` bomb. No corpus test does bare-keyword-to-OUTPUT.
- `kw_read` (keywords.c) has no distinct `alphabet` / `stno` rows — these currently
  resolve via the `NV_GET` fallback inside `rt_keyword_read`. Add exact-value rows
  (e.g. `&ALPHABET` = 256 chars collating order) if a test needs precise semantics.
