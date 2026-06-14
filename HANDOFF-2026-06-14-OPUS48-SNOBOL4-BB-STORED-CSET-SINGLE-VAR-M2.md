# HANDOFF — STORED single-variable cset (NEXT-1), M2 landed

**Session 2026-06-14 · Opus 4.8 · SCRIP base 448f529 + 1 commit.**

## What landed
Bare stored single-variable cset — `P = ANY(var)` / `SPAN` / `BREAK` / `BREAKX` / `NOTANY`
(single `TT_VAR` arg, NO capture) — now builds CORRECTLY in **mode 2** via construction-time
evaluate-and-bake. Mode 3/4 FAIL LOUDLY (bomb), pending a ledger stamp (see below).

Before: M2/M3 produced EMPTY, M4 bombed (`P=ANY(var)` fell through every LIVE build branch in
`lower_assign` — each required `TT_QLIT`/`TT_ILIT` — to the orphan `IR_ASSIGN_CONCAT+IR_SEQ` path
which builds no working DT_P).

## Why construction-time (oracle-verified, do-not-re-derive)
STORED `P=ANY(a)` binds the cset at CONSTRUCTION (when `P=...` executes), NOT at match.
`a="xyz"; P=ANY(a); a="abc"; "bcz"?P.C` → sbl `z` (set {x,y,z}), NOT `b`. The forbidden shortcut
(route stored through the immediate path's match-time name lookup) returns `b` and diverges from sbl.
Fix EVALUATES `a` at the build site and bakes the resulting string into the pattern object.

## The fix — 4 sites, 1 commit
- **lower_snobol4.c `lower_assign`** — NEW LIVE branch after the QLIT cset branch (~line 612):
  single-primitive cset with `c[0]->t==TT_VAR` → LIVE `DTP_ASSIGN` + `PATTERN_*` with
  `sval=NAME` + `dval=1.0` (var-flag). UNIFORM `dval` flag across all 5 kinds (the OBJECT path has
  no BREAKX `ival`-collision, unlike the immediate matcher's split). QLIT branch UNTOUCHED →
  literal byte-identical.
- **IR_interp.c** 5 cset object cases (`IR_PATTERN_ANY/NOTANY/SPAN/BREAK/BREAKX`, ~3379-3417):
  at the `rt_pattern_build` site, `dval==1.0 → cset = VARVAL_fn(NV_GET_fn(sval))` (current value,
  baked into the built object); else literal `sval`. Build-cache guard `if(state)` →
  `if(state && dval!=1.0)` so a re-run of `P=...` REBUILDS with the current var value
  (construction-time-per-eval = SPITBOL's rebuild-per-evaluation). Literal `dval=0` → guard +
  cset resolve IDENTICALLY to before (no M2 regression).
- **emit_bb.c** dispatch (5 cset cases ~3053-3057): carry `g_emit.op_dval = IR_LIT(nd).dval`.
- **bb_pattern_unary_s.cpp**: `dval==1.0` → LOUD `x86_bomb` (unconverted-box idiom: label α +
  bomb + def β + bomb). Prevents M3/M4 mis-baking the NAME as a literal cset (silent divergence).
  Literal `dval=0` skips the bomb → M3/M4 literal UNTOUCHED.

## Probes (M2==sbl, 6)
`P=ANY(a)` stored→`z` · loop-reassign `P=ANY(a)` (xy→bc)→`b` · `SPAN(d)`→42 · `BREAK(b)`→ab ·
`NOTANY(x)`→q · `BREAKX(s)`→abXc. IMMEDIATE control `ANY(a).C`→`b` UNCHANGED.

## Gates (non-decreasing HARD, all at floor, zero-regress)
smoke 7/7/7 · pat-rung 19/19/19 no-SKIP · fence TIER1=0 TIER2=0 · corpus M2=186(=) M3=171(=)
M4=166(=) SKIP=8(=). M2 held at 186 — the corpus has NO bare stored-single-var-cset row, so the
capability is proven by the 6 probes, not yet a corpus row (latent until a test exercises it).

## NEXT (do-not-re-derive)
1. **M3/M4 native** — ledger-stamp `rt_nv_cstr` (rt.c:257, `const char*(const char*name)`); in
   `bb_pattern_unary_s` the `dval==1.0` branch emits `mov rdi,[rip+name]; call rt_nv_cstr; mov r9,rax`
   in place of `lea r9,[rip+sealed]` (ONLY the op_s marshalling changes; clean char*, no DESCR_t ABI).
   Verify emitted build re-runs each `P=...` execution (per-eval rebuild).
2. **cset+CAPTURE compound** (`P = SPAN(d) . N` — the p3/p4 shape): RHS is `CAPTURE(SPAN…)`, not bare
   cset — my branch correctly skips it; needs the cset+capture object path.
3. **seq stored** (`P = SPAN(d) REM`, multi-element): extend `sno_leaf_buildable` (line 494) +
   `sno_build_leaf_ir` (line 526) for the `TT_VAR` cset arg so multi-element `TT_SEQ` builds.
4. **computed-concat cset** (`ANY(a b)` / `ANY(&UCASE &LCASE)` = old NEXT-2/064) — match-time expr eval.

## Ledger boundary (RULE 3)
M3/M4 native needs `call rt_nv_cstr` = NV-get from emitted code = ledger "nv get/set · S2 operand
fetch", STATUS **REQUESTED** (not Lon-stamped). Until stamped, M3/M4 bomb. M2 unaffected (interpreter,
not emitted code — same reason the immediate path defers to rt_scan in M3).

FILES: src/lower/lower_snobol4.c, src/interp/IR_interp.c, src/emitter/emit_bb.c,
src/emitter/BB_templates/bb_pattern_unary_s.cpp.
