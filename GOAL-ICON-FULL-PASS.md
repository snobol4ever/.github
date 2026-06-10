# GOAL-ICON-FULL-PASS.md — Icon: m2 247/247 non-xfail PASS

**PIVOT 2026-06-06 (Lon):** REVAMP/HYGIENE delegated to GOAL-BB-FIXUP. This goal owns ONLY: lowerer correctness (`src/lower/nl/lower_icon_nl.c` — the NL lowerer is now the SOLE Icon path; `lower_icon.c` is DELETED), m2 interpreter semantics (`IR_interp.c`), and Icon runtime (`by_name_dispatch.c`, `aggregates.c`, `keywords.c`). Native m3/m4 follows once m2 is correct — no template steps here.

**Status:** m2 155/247 · m3 10 · m4 10. Target 247/247 m2. XFAIL pool (36) out of scope.
**Gate every step:** `bash scripts/test_icon_rung_suite.sh` — m2 count must never decrease.

---

## ⛔ STANDING FINDING — NL β-chain (2026-06-10, this session's headline)

The 193→150 m2 cliff was NOT post-flip BB-FIXUP/Pascal work (the prior handoff's guess). Two bisect passes pin it at **`3546ea2` (DELETE lower_icon.c)**. After that commit `SCRIP_NL=0` selects nothing — so the 8-program flip-gate cross-checks that justified the `c3b1dbb` conversion compared the NL lowerer **against itself**. The real defect: NL never threaded the generator **β-chain**.

OLD contract (from `v_binop`/`v_to`/`emit_leaf` in `lower.c`): a BINOP lowers its RIGHT operand with ω = LEFT's β; `v_to` lowers HI with ω = LO's β. β(TO)=the-node · β(leaf)=inherited-ω · β(BINOP)=right-child-β. So an exhausted inner generator **re-pumps the outer generator** (its β), not the enclosing EVERY. NL passed the caller's ω to every child → inner TO aborted to EVERY (`rung01_paper_mult` inner TO ω=2β-EVERY vs oracle ω=5β-outerTO).

**Partial fix landed (`aff86df`):** `icx_t.beta` threaded — `lower()` entry defaults beta=ω; BINOP right child + `lower_to` hi get the left's β; `lower_to` sets beta=to; `lower_call` chains args through beta then resets beta=ω (det-call contract); `lower_every` loop_back = the threaded β. `rung01_paper_mult` dump now byte-identical to the 15608cf oracle. **+5 of 21 regressions** (paper_compound, paper_mult, nested_add, nested_filter, proc_locals).

**16 regressions still open** — same β-contract not yet applied to their constructs. Diff-driven recipe: `git show 15608cf:src/lower/lower_icon.c` (the deleted oracle lowerer) + `git show 15608cf` build → `--dump-bb prog.icn` is the byte oracle; make NL match. Open set:
`rung03_suspend_gen{,_compose,_filter}` · `rung01_paper_nested_to` · `rung06_cset_any_fail` · `rung07_control_not` · `rung07_control_repeat_break` · `rung08_strbuiltins_find_gen` · `rung08_strbuiltins_match` · `rung10_augop_break_repeat` · `rung11_bang_augconcat_bang_{concat,str}` · `rung13_table_iterate` · `rung20_section_seqexpr_section_{basic,full,var}`.
Constructs needing the β-thread: UNOP (`!x`), SECTION, SUSPEND arg-blocks, GEN_SCAN (`?`), `not`, REPEAT/BREAK, the bang generator.

**Flag for Lon:** the conversion-ladder evidence bar (full-corpus execution parity, not 8-program samples) should gate any future lowerer flip — the broken `SCRIP_NL=0` oracle let a deficit-carrying flip pass.

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

- **β-CHAIN-REST** — apply the β-contract to UNOP/SECTION/SUSPEND/GEN_SCAN/not/REPEAT-BREAK/bang. Diff each vs the 15608cf `--dump-bb` oracle. +16 target.
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

**HEAD (SCRIP) = `aff86df`** — NL β-chain partial fix. m2 **155** · m3 10 · m4 10. HEAD (.github) = this session's handoff.

Session 2026-06-10 (Sonnet 4.6 / Opus): two-pass bisect overturned prior handoff — regression root is `3546ea2` (lower_icon.c deletion), not later commits; the NL flip's cross-check was self-comparing because `SCRIP_NL=0` no longer selected the old lowerer. Threaded `icx_t.beta` (generator β-chain) through lower/BINOP/lower_to/lower_call/lower_every. m2 150→155 (+5 nested-generator regressions). Icon smoke 12/12 HARD, prolog 5/5 HARD ×3, one-box gate PASS. 16 regressions remain — same β-contract for UNOP/SECTION/SUSPEND/GEN_SCAN/not/REPEAT-BREAK/bang.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
