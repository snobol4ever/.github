# GOAL-ICON-FULL-PASS.md — Icon: m2 247/247 non-xfail PASS

**PIVOT 2026-06-06 (Lon):** REVAMP/HYGIENE delegated to GOAL-BB-FIXUP. This goal owns ONLY: lowerer correctness (`src/lower/lower_icon.c` — NL-promoted, sole Icon path), m2 interpreter semantics (`IR_interp.c`), and Icon runtime (`by_name_dispatch.c`, `aggregates.c`, `keywords.c`). Native m3/m4 follows once m2 is correct.

**Status:** m2 198/247 · m3 29 · m4 32. Target 247/247 m2. XFAIL pool (36) out of scope.
**Gate every step:** `bash scripts/test_icon_rung_suite.sh` — m2 count must never decrease.

---

## Failure taxonomy

**A. LOWER UNHANDLED** (rc=134 `[lower2] UNHANDLED kind=N`) — add a case in `lower_icon.c`; consult JCON `irgen.icn` first. *(none open for current rung set.)*

**B. M2 OUTPUT MISMATCH** — fix in `IR_interp.c` / `by_name_dispatch.c` / runtime:

| Symptom | Rung |
|---|---|
| nested-generator β mis-wire (16 cases) | CLOSED (β-CHAIN-REST 2026-06-10) |
| coerce `integer("3")`/`real(x)` all type combos | 36, 37 |
| `type()` wrong name; `&lcase`/`&ucase`/`&pos` keywords | 37 |
| scan-in-alt `s ? (e1\|e2)` resume | 37 |
| str relop remaining (`ac=='ca'`) | 37 |
| mutual recursion forward refs | 37 |
| `sort(L)` / `sort(T,i)` unimplemented | 31 |
| alt cross-arg partial | 13 |

---

## Open steps (m2 interpreter + lowerer only)

- **FULL-11 next-in-every** — INVESTIGATED: `NEXT.γ=generator.α` was hypothesized but not the real bug. The primes test (`rung36_jcon_primes`) ALREADY PASSES at m2=198. Closed.
- **FULL-19 real to-by** ✅ DONE 2026-06-12 (`3e08aaa`). `IR_TO_BY` `is_real` detection fixed for `sval="ar"` (ag+real with operand nodes). rung19 +2.
- [ ] **FULL-18-resid generator-in-user-proc-call-arg** — `every write(tag("a"|"b"|"c"))` outputs only `[a]`; `every write(s[1 to 3])` outputs only `a`. Root: `lower_call` in `lower_icon.c` line 82 sets `cx->beta = icn_call_allow_gen(name) ? call : ω` — user procs like `tag` return false from `icn_call_allow_gen`, so `cx->beta=ω`, and the ALT/TO arg generator is never wired into the flat graph (disappears from `--dump-bb`). Fix: detect generator in arg subtree and keep `cx->beta = call`. Affects rung16 (+1), rung32 (+1), many rung36/37. Do NOT loosen `g_icn_postfix_resume` gate blindly.
- **FULL-12 coerce()** — `integer(x)`/`real(x)` all type combos; consult `oarith.r`. Rungs 36, 37. +5.
- **FULL-13-resid keywords** — rung37_keywords 3 residuals: `& &e` parse ambiguity, &error write-back, &dump/trace/random.
- **FULL-14 scan-alt** — `IR_GEN_SCAN` resume re-enters scan across alt. Rung 37. +2.
- **FULL-15 str relop** — remaining lexicographic cases in `by_name_dispatch.c`. +1.
- **FULL-16 mutual recursion** — forward refs via `rt_call_named_proc`, verify no crash. +1.
- **FULL-17 sort()** — `rt_list_sort`/`rt_table_sort` in `aggregates.c`; consult `fstranl.r`. Rung 31. +5.
- [ ] **FULL-18-resid assign-gen β** — `every (x := (1|2|3|4)) > 2 & write(x)` still empty. `lower_call` resets `cx->beta = ω` unless `g_icn_postfix_resume` set; the assign-generator `x := alt` doesn't propagate self-resume β up through the chaining write call. Do not loosen the `c9ec94c` gate — it guards write-chaining. Rung 13.
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

**HEAD (SCRIP) = `3e08aaa`** — IR_TO_BY: fix is_real for sval='ar' with operand nodes; real to-by works. m2 **198** · m3 29 · m4 32. HEAD (.github) = HANDOFF-2026-06-12-SONNET46-ICON-FULL-PASS-TOBY-REAL-GENARG.md.

**Key intel:** `--dump-bb` does NOT show `operand_aux` — two identical dumps can still differ; verify by output. NOT/SECTION/BANG push via `ir_operand_push` (HEAD reads `bb->operands[0]`), while ALT uses `bb_operand_aux_set` (HEAD interp reads `bb_operand_aux_get`).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
