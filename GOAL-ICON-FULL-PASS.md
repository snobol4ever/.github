# GOAL-ICON-FULL-PASS.md — Icon: m2 247/247 non-xfail PASS

**PIVOT 2026-06-06 (Lon):** REVAMP and HYGIENE work is DELEGATED to GOAL-BB-FIXUP. This goal owns ONLY: lowerer correctness (`lower_icon.c`), m2 interpreter semantics (`IR_interp.c`), and Icon runtime behavior. Native template work (m3/m4) follows organically once m2 is correct; no Phase 3/4 template steps here.

**Status (2026-06-06-j):** m2 194/247 · m3 31 · m4 34. Target: 247/247 m2.
**XFAIL pool (36):** not in scope — known-unimplemented tiers with explicit xfail markers.
**Gate every step:** `bash scripts/test_icon_rung_suite.sh` — m2 count must never decrease.

---

## Failure taxonomy (updated 2026-06-06-j)

### A. LOWER UNHANDLED — m2 ABORTS (rc=134, `[lower2] UNHANDLED role=0 kind=N`)
Fix = add a lowerer case in `src/lower/lower_icon.c`. Consult JCON `refs/jcon-master/tran/irgen.icn` first.

*(All Phase-1 constructs landed — no open LOWER UNHANDLED for the current rung set)*

### B. M2 OUTPUT MISMATCH — interpreter runs but wrong result
Fix = IR_interp.c / runtime semantics / by_name_dispatch.c.

| Symptom | Construct | Rungs |
|---------|-----------|-------|
| `find()` returns only first match (not generative) | find() generator mode | 08 |
| alt cross-arg partial (only first combination) | alt with proc call side-effects | 13 |
| coerce() fails (`integer("3")` etc) | string→int/real coercion builtins | 36, 37 |
| `type()` returns wrong type name | &type keyword / type() builtin | 37 |
| `&lcase`/`&ucase` keyword values | keyword cset values | 37 |
| `&pos` lhs/rhs swap incorrect | &pos in swap lhs/rhs | 37 |
| scan resumable across alt not completing | scan-in-alt generator | 37 |
| str relop `ac=='ca'` missing | lexicographic relop remaining cases | 37 |
| mutual recursion crashes | mutual proc forward refs | 37 |
| `integer(x)` / `real(x)` coercion | integer() / real() builtins | 37 |
| `sort()` unimplemented | sort(L) / sort(T,i) | 31 |

---

## Steps — m2 interpreter + lowerer only

### FULL-10: find() generative mode (rung 08)
- `find(s1,s2)` must be generative: resume finds next occurrence.
- Consult `refs/icon-master/src/runtime/fstranl.r` — `find` is generative in canonical Icon.
- Fix: `IR_FIND_GEN` node in `IR_interp.c` or `by_name_dispatch.c` — ensure resume cursor advances.
- Gate: rung08 m2 PASS (+2 or +3 subtests).

### FULL-12: coerce() / integer() / real() (rungs 36, 37)
- `integer(x)` converts string/real to integer; `real(x)` converts to real.
- Verify `rt_integer_fn` / `rt_real_fn` in `by_name_dispatch.c` handle all type combinations.
- Consult `refs/icon-master/src/runtime/oarith.r` for coercion rules.
- Gate: rung36_jcon_coerce m2 PASS, rung37_coerce m2 PASS (+5).

### FULL-13: keywords (&type, &lcase, &ucase, &pos) (rung 37)
- `&type` → type name string; `&lcase` / `&ucase` → cset constants; `&pos` lhs/rhs.
- Fix: `IR_KEYWORD` / `keywords.c` / NV entries for &lcase &ucase.
- Consult `refs/icon-master/src/runtime/fmiscops.r` for &type semantics.
- Gate: rung37_type, rung37_keywords m2 PASS (+3).

### FULL-14: scan-in-alt generator (rung 37)
- `s ? (expr1 | expr2)` — scan resumable across alt branches.
- Fix: `IR_GEN_SCAN` interp in `IR_interp.c` — verify alt resume re-enters scan correctly.
- Gate: rung37_scan_alt m2 PASS (+2).

### FULL-15: str relop remaining (rung 37)
- Lexicographic relop for remaining cases (ac == ca etc).
- Fix: `by_name_dispatch.c` str compare operators.
- Gate: rung37_str_relop m2 PASS (+1).

### FULL-16: mutual recursion (rung 37)
- Forward proc references resolve lazily via `rt_call_named_proc` — verify no crash.
- Gate: rung37_mutual m2 PASS (+1).

### FULL-17: sort() (rung 31)
- `sort(L)` → new sorted list; `sort(T,i)` sorts table by key/value.
- Runtime: add `rt_list_sort` / `rt_table_sort` to `aggregates.c`.
- Consult `refs/icon-master/src/runtime/fstranl.r` — `sort`.
- Gate: rung31 m2 PASS (+5).

### FULL-18: alt cross-arg (rung 13)
- `every f(1|2) | g(3|4)` — all cross-product combinations.
- Verify `IR_ALT` wiring in lowerer per JCON `ir_a_Alt`.
- Gate: rung13_alt_alt_cross_arg m2 PASS (+1).

### FULL-32: rung36/37 remainder sweep
- After above, triage remaining rung36/37 failures one by one.
- Each residual failure diagnosed from `./scrip --interp prog.icn 2>&1`.
- Gate: maximize m2 PASS count; document genuine XFAILs.

---

## Session Setup (inherited from GOAL-ICON-BB.md)

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
bash scripts/test_smoke_icon.sh
bash scripts/test_smoke_prolog.sh
bash scripts/test_smoke_unified_broker.sh
bash scripts/test_gate_bb_one_box.sh
```

## Gate after every step

```bash
bash scripts/build_scrip.sh
make libscrip_rt
bash scripts/test_icon_rung_suite.sh
# m2 count must be >= previous run's count
# m3/m4: PASS or EXCISED only, no silent FAIL
bash scripts/test_gate_bb_one_box.sh
bash scripts/test_smoke_prolog.sh
bash scripts/test_smoke_unified_broker.sh
```

## Canonical source rule (from RULES.md)

Before implementing ANY construct: grep the canonical sources FIRST.
- Port topology: `refs/jcon-master/tran/irgen.icn` — procedure `ir_a_<Construct>`.
- Runtime semantics: `refs/icon-master/src/runtime/*.r` — `fstranl.r`, `oarith.r`, `oref.r`, `ocomp.r`.
- The m2 oracle (`IR_interp.c`) is a transcription; canonical wins when they disagree.

---

## Progress tracker

| Step | Rungs unlocked | M2 delta | Status |
|------|---------------|----------|--------|
| ICN-FULL-1 TT_INITIAL | 21, 25 | +5 | ✅ `1589bd5` |
| ICN-FULL-2 TT_LIMIT | 14 | +5 | ✅ `1589bd5` |
| ICN-FULL-3 TT_MAKELIST | 22 (+31,35 partial) | +5 | ✅ `1589bd5` |
| ICN-FULL-4 TT_IDX/SECTION | 16, 20 | +8 | ✅ `1589bd5` |
| ICN-FULL-5 TT_CASE | 33 | +5 | ✅ `1589bd5` |
| ICN-FULL-6 TT_IDX tables | 23, 35 | +8 | ✅ `1589bd5` |
| ICN-FULL-7 TT_FIELD/RECORD | 24 | +5 | ✅ `1589bd5` |
| ICN-FULL-8 TT_CSET_DIFF | 37 subset | +2 | ✅ `1589bd5` |
| ICN-FULL-9 TT_REVASSIGN | 15, 37 | +3 | ✅ `1589bd5` |
| BUG-1 IR_LIMIT body topology | 14 | fix | ✅ `f86427a` |
| BUG-2 IR_CASE arm-descriptor chain | 33 | +5 | ✅ `f15cfc8` — flat-pair AST, arm_key descriptor (γ=key,β=val,ω=next), selector sentinel sel->γ=cas |
| BUG-3 TT_SWAP dispatch missing | 15 | +2 | ✅ `f15cfc8` — add TT_SWAP to icn_swap case |
| BUG-4 IDX_SET/FIELD_SET | 13,23,24 | — | ✅ already working in icn_assign |
| BUG-5 BINOP_POW→real | 19,26 | +9 | ✅ `f15cfc8` — remove int shortcut in binop_apply |
| BUG-6 IR_INITIAL NV flag | 21,25 | +5 | ✅ `f15cfc8` — NV_GET/SET keyed on bb ptr |
| **ICN-FULL-10 find() generative** | 08 | +1 | ✅ `15608cf` — allow_gen for find/upto in icn_det_call; dval==3.0 precompute-all-matches into susp_gen_cache |
| **ICN-FULL-12 coerce()** | 36, 37 | +5 | ☐ |
| **ICN-FULL-13 keywords** | 37 | +0 net | ✅ `15608cf` — TT_VAR with sval[0]=='&' → IR_KEYWORD in lower_icon.c; unblocks downstream. rung37_keywords still FAIL (3 residuals: `& &e` parse ambiguity, &error write-back, &dump/trace/random) |
| **ICN-FULL-14 scan-alt** | 37 | +2 | ☐ |
| **ICN-FULL-15 str relop** | 37 | +1 | ☐ |
| **ICN-FULL-16 mutual recursion** | 37 | +1 | ☐ |
| **ICN-FULL-17 sort()** | 31 | +5 | ☐ |
| **ICN-FULL-18 alt cross-arg** | 13 | +1 | ☐ |
| **ICN-FULL-32 rung36/37 sweep** | 36, 37 | triage | ☐ |

**Watermark:** HEAD (SCRIP) = `15608cf` — FULL-10 + FULL-13 LANDED 2026-06-10. m2 193 · m3 30 · m4 33.
Session 2026-06-06 (Sonnet 4.6, PIVOT + BUG fixes): BUG-2 IR_CASE arm-descriptor chain (5/5 rung33 PASS) · BUG-3 TT_SWAP dispatch (all rung15 swap PASS) · BUG-4 IDX_SET already working · BUG-5 BINOP_POW→real (all rung26 PASS) · BUG-6 IR_INITIAL NV persistent flag (all rung21/25 PASS). Revamp/hygiene delegated to GOAL-BB-FIXUP per Lon directive. Phase 3/4 native template steps REMOVED from this goal.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
