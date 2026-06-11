# GOAL-ICON-FULL-PASS.md — Icon: m2 247/247 non-xfail PASS

**PIVOT 2026-06-06 (Lon):** REVAMP/HYGIENE delegated to GOAL-BB-FIXUP. This goal owns ONLY: lowerer correctness (`src/lower/nl/lower_icon_nl.c` — the NL lowerer is now the SOLE Icon path; `lower_icon.c` is DELETED), m2 interpreter semantics (`IR_interp.c`), and Icon runtime (`by_name_dispatch.c`, `aggregates.c`, `keywords.c`). Native m3/m4 follows once m2 is correct — no template steps here.

**Status:** m2 184/247 · m3 29 · m4 32. Target 247/247 m2. XFAIL pool (36) out of scope.
**Gate every step:** `bash scripts/test_icon_rung_suite.sh` — m2 count must never decrease.

---

## ⛔ STANDING FINDING — NL β-chain (RESOLVED 2026-06-10)

The 193→150 cliff was `3546ea2` (DELETE lower_icon.c): post-deletion `SCRIP_NL=0` selected nothing, so the flip-gate cross-checks compared NL against itself. Root defect was the generator β-chain plus a cluster of missing/mis-routed constructs. RESOLVED this session (m2 150→178). Recipe that worked: build the real `15608cf` oracle in a `git worktree add /tmp/oracle 15608cf` (then `make -j4 scrip` directly — `build_scrip.sh` hard-codes `$ROOT/SCRIP`), and for each failing rung `diff <(./scrip --dump-bb f) <(/tmp/oracle/scrip --dump-bb f)` — BUT confirm by output too, since `--dump-bb` hides `operand_aux`.

**Flag for Lon (still open):** future lowerer flips need full-corpus EXECUTION parity as the gate, not 8-program dump samples — the broken `SCRIP_NL=0` oracle let a deficit-carrying flip through. Consider snapshotting expected `--dump-bb` per rung before the next conversion.

---

## Failure taxonomy

**A. LOWER UNHANDLED** (rc=134 `[lower2] UNHANDLED kind=N`) — add a case in `lower_icon_nl.c`; consult JCON `irgen.icn` first. *(none open for current rung set.)*

**B. M2 OUTPUT MISMATCH** — fix in `IR_interp.c` / `by_name_dispatch.c` / runtime:

| Symptom | Rung |
|---|---|
| nested-generator β mis-wire (16 cases) | see STANDING FINDING |
| coerce `integer("3")`/`real(x)` all type combos | 36, 37 |
| `type()` wrong name; `&lcase`/`&ucase`/`&pos` keywords | 37 |
| scan-in-alt `s ? (e1\|e2)` resume | 37 |
| str relop remaining (`ac=='ca'`) | 37 |
| mutual recursion forward refs | 37 |
| `sort(L)` / `sort(T,i)` unimplemented | 31 |
| alt cross-arg partial | 13 |

---

## Open steps (m2 interpreter + lowerer only)

- **β-CHAIN-REST** ✅ DONE 2026-06-10 (m2 155→178). UNOP/bang/section/not/conjunction/augop/generator-call all fixed; see Watermark.
- **FULL-12 coerce()** — `integer(x)`/`real(x)` all type combos; consult `oarith.r`. Rungs 36, 37. +5.
- **FULL-13-resid keywords** — rung37_keywords 3 residuals: `& &e` parse ambiguity, &error write-back, &dump/trace/random.
- **FULL-14 scan-alt** — `IR_GEN_SCAN` resume re-enters scan across alt. Rung 37. +2.
- **FULL-15 str relop** — remaining lexicographic cases in `by_name_dispatch.c`. +1.
- **FULL-16 mutual recursion** — forward refs via `rt_call_named_proc`, verify no crash. +1.
- **FULL-17 sort()** — `rt_list_sort`/`rt_table_sort` in `aggregates.c`; consult `fstranl.r`. Rung 31. +5.
- **FULL-18-resid assign-gen β (alt cross-arg, partial)** — `lower_alt` LANDED this session; `rung13_alt_nested` (cross-product) now PASSES. Residual `rung13_alt_filter` `every (x := (1|2|3|4)) > 2 & write(x)` still empty. NOT an alt bug: `(1|2|3|4) > 2` alone yields `2 2` correctly (relop returns its right operand). The gap is the **assign-generator** `x := alt` not propagating its self-resume β up through the chaining `write` call to the enclosing `every` — the chaining-call path in `lower_call` resets `cx->beta = ω` unless `g_icn_postfix_resume` is set (the `c9ec94c` gate). β-chain family, distinct from alt lowering; needs its own step (do not loosen the `c9ec94c` gate blindly — it guards the write-chaining tests). Rung 13.
- **FULL-32 rung36/37 sweep** — triage residuals one by one; document genuine XFAILs.

---

## Session Setup

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
bash scripts/test_smoke_icon.sh        # m2 12/12 HARD
bash scripts/test_smoke_prolog.sh      # m2 5/5 HARD
bash scripts/test_gate_bb_one_box.sh
```
Extract the uploaded Icon/JCON zips into `refs/` if absent.

## Gate after every step

```bash
bash scripts/build_scrip.sh && make libscrip_rt
bash scripts/test_icon_rung_suite.sh   # m2 >= previous; m3/m4 PASS-or-EXCISED only
bash scripts/test_gate_bb_one_box.sh
bash scripts/test_smoke_prolog.sh
```

## Canonical source rule (RULES.md)

Before ANY construct: grep canonical FIRST. Port topology → `refs/jcon-master/tran/irgen.icn` (`ir_a_<Construct>`). Runtime → `refs/icon-master/src/runtime/*.r` (`fstranl.r`, `oarith.r`, `oref.r`, `ocomp.r`). The m2 oracle (`IR_interp.c`) is a transcription; canonical wins.

---

## Watermark

**HEAD (SCRIP) = `2dd9a2a`** — FULL-14 alternation lowering (`lower_alt`). m2 **184** · m3 29 · m4 32. HEAD (.github) = this session's handoff.

Session 2026-06-10 (Opus 4.8, FULL-14 ALTERNATION): `lower_alt` added to `lower_icon_nl.c` — `TT_ALTERNATE` was entirely unhandled (fell to `default`→IR_SUCCEED, so `write(1|2)` printed nothing). Mirrors oracle `wire_alt` (lower.c:124): arms lowered right-to-left, arm j's ω = arm j+1's entry (last → inherited ω), `arm_succ` = ALT node, arms deposited via `bb_operand_aux_set` (verified the HEAD interp `IR_ALT` at IR_interp.c:3021 reads `bb_operand_aux_get`, the OPPOSITE of the NOT/SECTION/BANG `ir_operand_push` convention — the flagged trap), β = node self-resume; route `case TT_ALTERNATE`. m2 178→184 (+6), m3 27→29, m4 30→32, zero regression; icon m2 12/12 HARD, prolog 5/5 HARD, one-box PASS. Proofs: `write(1|2)`→1, `every write(1|2|3)`→1,2,3, scan-in-alt `match("xyz")|0`→0. FULL-18: `rung13_alt_nested` (cross-product) now PASSES; residual `rung13_alt_filter` is assign-generator β-propagation — see FULL-18-resid step.

Session 2026-06-10 (Opus, β-CHAIN-REST + missing constructs): built the REAL 15608cf oracle in a `/tmp/oracle` git worktree (prior `SCRIP_NL=0` oracle was vacuous post-deletion). Eight fixes, m2 155→178 (+23), all gates green throughout (icon m2 12/12 HARD, prolog 5/5 HARD, one-box PASS): (1) `c9ec94c` write/writes chaining call resumes to last-arg β — NL ignored the driver-set `g_icn_postfix_resume`; (2) `20bee0e` subgraph generator calls (find/upto/gen-procs) self-resume β=call via `icn_call_allow_gen`; (3) `38382a1` `not`→IR_NOT (was IR_UNOP); (4) `c734630` bang `!x`→IR_LIST_BANG self-β (+11, widely used); (5) `1f57db3` `s[i:j]`→IR_SECTION; (6) `35718b7` `x op:= y` AST-rewritten to `x:=(x op y)` so the BINOP gets operand_aux + β-chain; (7) `d6964d4` `&` conjunction (TT_SEQ) routed through IR_CONJ like TT_SEQ_EXPR — old handler ran the right operand even when the left failed. Several fixes are byte-identical to the oracle `--dump-bb`; the residual deltas (NOT/SECTION/BANG) are the HEAD interp's `operands[]`-vs-`operand_aux` convention (output is ground truth — `operand_aux` is invisible in `--dump-bb`, which made the augop bug look like a phantom interp regression).

**Standing intel:** (a) the `--dump-bb` view does NOT show `operand_aux`; two graphs printing identically can still differ — verify by output, not dump alone. (b) the 15608cf oracle interp read `operand_aux` for NOT/SECTION/BANG; HEAD reads `bb->operands[0]` — when matching the oracle, push operands via `ir_operand_push`, not `bb_operand_aux_set`. (c) the original-16 regression cluster is CLOSED — the last item `rung08_strbuiltins_match` (alt-in-scan `match("xyz") | 0`) was the unhandled-alternation bug, fixed this session by `lower_alt`.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
