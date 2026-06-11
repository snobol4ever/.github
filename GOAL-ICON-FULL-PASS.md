# GOAL-ICON-FULL-PASS.md — Icon: m2 247/247 non-xfail PASS

**PIVOT 2026-06-06 (Lon):** REVAMP/HYGIENE delegated to GOAL-BB-FIXUP. This goal owns ONLY: lowerer correctness (`src/lower/nl/lower_icon_nl.c` — the NL lowerer is now the SOLE Icon path; `lower_icon.c` is DELETED), m2 interpreter semantics (`IR_interp.c`), and Icon runtime (`by_name_dispatch.c`, `aggregates.c`, `keywords.c`). Native m3/m4 follows once m2 is correct — no template steps here.

**Status:** m2 155/247 · m3 10 · m4 10. Target 247/247 m2. XFAIL pool (36) out of scope.
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
- **FULL-14 ALTERNATION (root cause found, NOT a scan bug)** — `a | b` (TT_ALTERNATE) is ENTIRELY UNHANDLED in `lower_icon_nl.c`: it's in `is_resumable` but has no `lower()` case, so it falls to `default`→IR_SUCCEED. `write(1 | 2)` prints nothing (oracle: `1`); `"world" ? write(match("xyz") | 0)` prints nothing (oracle: `0`). This is the `rung08_strbuiltins_match` residual AND likely FULL-18 (alt cross-arg). FIX: add a `lower_alt` mirroring oracle `wire_alt(IR_ALT,…)` (lower.c:172) + route `case TT_ALTERNATE:`/`TT_ALT:`. Wiring per arm j: γ=ALT node, ω=entry[j+1] (next arm) or ω_in (last arm); set arm.γ=node if unset; `bb_operand_aux_set(node, arms, n)`; entry=arms[0] entry; β=node (self-resume). **CRUCIAL:** the HEAD interp IR_ALT (IR_interp.c:3021) reads arms via `bb_operand_aux_get` — so for ALT use `bb_operand_aux_set` (NOT `ir_operand_push` — opposite of the NOT/SECTION/BANG convention). Expected to clear several tests at once.
- **FULL-12 coerce()** — `integer(x)`/`real(x)` all type combos; consult `oarith.r`. Rungs 36, 37. +5.
- **FULL-13-resid keywords** — rung37_keywords 3 residuals: `& &e` parse ambiguity, &error write-back, &dump/trace/random.
- **FULL-14 scan-alt** — `IR_GEN_SCAN` resume re-enters scan across alt. Rung 37. +2.
- **FULL-15 str relop** — remaining lexicographic cases in `by_name_dispatch.c`. +1.
- **FULL-16 mutual recursion** — forward refs via `rt_call_named_proc`, verify no crash. +1.
- **FULL-17 sort()** — `rt_list_sort`/`rt_table_sort` in `aggregates.c`; consult `fstranl.r`. Rung 31. +5.
- **FULL-18 alt cross-arg** — `IR_ALT` wiring per JCON `ir_a_Alt`. Rung 13. +1.
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

**HEAD (SCRIP) = `f5072d0`** — NL β-chain + missing-construct sweep. m2 **178** · m3 27 · m4 30. HEAD (.github) = this session's handoff.

Session 2026-06-10 (Opus, β-CHAIN-REST + missing constructs): built the REAL 15608cf oracle in a `/tmp/oracle` git worktree (prior `SCRIP_NL=0` oracle was vacuous post-deletion). Eight fixes, m2 155→178 (+23), all gates green throughout (icon m2 12/12 HARD, prolog 5/5 HARD, one-box PASS): (1) `c9ec94c` write/writes chaining call resumes to last-arg β — NL ignored the driver-set `g_icn_postfix_resume`; (2) `20bee0e` subgraph generator calls (find/upto/gen-procs) self-resume β=call via `icn_call_allow_gen`; (3) `38382a1` `not`→IR_NOT (was IR_UNOP); (4) `c734630` bang `!x`→IR_LIST_BANG self-β (+11, widely used); (5) `1f57db3` `s[i:j]`→IR_SECTION; (6) `35718b7` `x op:= y` AST-rewritten to `x:=(x op y)` so the BINOP gets operand_aux + β-chain; (7) `d6964d4` `&` conjunction (TT_SEQ) routed through IR_CONJ like TT_SEQ_EXPR — old handler ran the right operand even when the left failed. Several fixes are byte-identical to the oracle `--dump-bb`; the residual deltas (NOT/SECTION/BANG) are the HEAD interp's `operands[]`-vs-`operand_aux` convention (output is ground truth — `operand_aux` is invisible in `--dump-bb`, which made the augop bug look like a phantom interp regression).

**Standing intel:** (a) the `--dump-bb` view does NOT show `operand_aux`; two graphs printing identically can still differ — verify by output, not dump alone. (b) the 15608cf oracle interp read `operand_aux` for NOT/SECTION/BANG; HEAD reads `bb->operands[0]` — when matching the oracle, push operands via `ir_operand_push`, not `bb_operand_aux_set`. (c) ONE original-16 item remains: `rung08_strbuiltins_match` (alt-in-scan `match("xyz") | 0` — top-level dump identical, divergence inside the GEN_SCAN subgraph) = FULL-14.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
