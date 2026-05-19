# HANDOFF — 2026-05-19 — PST-SN4-SC Session

**Author:** Claude Sonnet 4.6
**Session goal:** GOAL-PST-SNOBOL4 Phase 2 — pure shift/reduce rewrite of parser_snobol4.sc

---

## What was completed

**PST-SN4-SC ✅ COMPLETE** — `corpus/SCRIP/parser_snobol4.sc` is now pure shift/reduce.

| Step | Description | Result |
|------|-------------|--------|
| SN4-SC-1 | 12× `reduce_prim(...)` → `reduce(kind, 'nTop()')` | ✅ |
| SN4-SC-2 | 2× `reduce_call()` → `reduce("'TT_FNC'", 'nTop()')` | ✅ |
| SN4-SC-3 | 4× `reduce_opsyn(op,2)` → `reduce("'TT_SCAN'"/`'TT_SEQ'`/`'TT_CAPT_CURSOR'`/`'TT_NOT'`, 2)` | ✅ |
| SN4-SC-4 | 17× `foldop` eliminated: Expr3/4 → n-ary `nPush/nInc/X/nPop`; Expr6–10 → right-recursive `reduce(tag,2)`; all `*cont` rules deleted | ✅ |
| SN4-SC-5 | grep verify: zero code hits on forbidden primitives; only `sn_match`+`sn_upr` functions remain | ✅ |
| SN4-SC-6 | ⚠ MIRROR-GAP-SN4-SC-6: smoke blocked by EC-3* --interp regression (see below) | filed |

**Commits:**
- corpus: `68aa237` (rebased onto `d1c08ff`)
- .github: `e757cd22`

---

## ⚠ EC-3 --interp regression (discovered this session, NOT caused by PST edits)

`scrip --interp` (Snocone runtime) is broken as of today's EC-3b–3f commits.

**Symptoms:**
- `test_smoke_snocone`: was 5/0, now **2/3 FAIL** (procedure/if_eq/while)
- `if()`, `while()`, `EQ()`, `LE()`, function calls → segfault
- `OUTPUT = expr;` and `x = expr;` still work
- `scrip --run` (SNOBOL4 native) is fine: smoke_snobol4 7/0 ✅
- `&ALPHABET`, `&UCASE`, `&LCASE`, `SIZE()`, `REPLACE()`, `IDENT()` all segfault in --interp

**Root cause:** EC-3b–3f unified SM emitter templates (sm_arith.c, sm_compare.c,
sm_control.c, sm_pat.c). One of these introduced a regression in the SM dispatch
path used by `--interp`. The no-crash baseline `db89a804` (2026-05-18) had
smoke_snocone 5/0; regression appeared between that and `5cb3b909` (EC-3f, today).

**Bisect target:** `git bisect` between `db89a804` and `5cb3b909` on `test_smoke_snocone.sh`.
Likely culprit: EC-3b (`774c1e0e`, sm_arith.c — SM_ADD/SUB/MUL/DIV/CONCAT).

**Fix required before:** SN4-SC-6 smoke, PST-SC-SC smoke, any parser_*.sc validation.

---

## Next session recommended order

1. **Fix EC-3 --interp regression** (bisect, small fix, validate smoke_snocone 5/0)
2. **PST-SC-SC** — `parser_snocone.sc` Phase 2 (largest job, 4–6 h):
   - Delete ~110 helper functions + state variables
   - Rewrite all control-flow grammar rules per GOAL-PST-SNOCONE.md templates
   - Steps: SC-SC-1 (delete), SC-SC-2 (control flow), SC-SC-3 (expressions),
     SC-SC-4 (grep), SC-SC-5 (smoke)
   - Start fresh session at <30% context

---

## Repo heads at handoff

- one4all: `5cb3b909`
- corpus:  `68aa237`
- .github: `e757cd22`
