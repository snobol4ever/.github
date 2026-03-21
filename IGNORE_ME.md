# HOLD_ARCHIVE.md — Milestones On Hold

All milestones below were moved here from PLAN.md on 2026-03-21 (session F-211 / clean-slate reset).
They are **not deleted** — they are on hold pending a fresh strategic plan.
Completed milestones (✅) remain in PLAN.md. Only incomplete/deferred milestones live here.

---

## TINY (snobol4x) — On Hold

| ID | Trigger | Last Known Status |
|----|---------|-------------------|
| **M-ASM-TREEBANK** | treebank.sno correct output via ASM backend; artifacts/asm/samples/treebank.s assembles clean and diff vs CSNOBOL4 oracle empty | ❌ treebank.s assembles clean (B-226); runtime correctness not yet verified |
| **M-ASM-CLAWS5** | claws5.sno correct output via ASM backend; artifacts/asm/samples/claws5.s assembles clean and diff vs CSNOBOL4 oracle empty | ❌ claws5.s ~95% — 3 undefined beta labels (NRETURN fns); gates on NRETURN fix |
| **M-ASM-RUNG10** | rung10/ — DEFINE/recursion/locals/NRETURN/FRETURN/APPLY 9/9 PASS via ASM backend | ❌ 4/9 WIP |
| **M-ASM-RUNG11** | rung11/ — ARRAY/TABLE/DATA types 7/7 PASS via ASM backend | ❌ Sprint A-RUNG11 |
| **M-ASM-LIBRARY** | library/ crosscheck tests PASS via ASM backend; -include resolved correctly | ❌ Sprint A-LIBRARY |
| **M-ENG685-TREEBANK-SNO** | treebank.sno correct via CSNOBOL4: nPush/nInc/nPop + Shift/Reduce; .ref oracle committed | ❌ Sprint B-ENG685-SNO |
| **M-ENG685-CLAWS** | claws5.sno — CLAWS5 POS corpus tokenizer; .ref oracle committed; PASS via CSNOBOL4 and ASM backend | ❌ Sprint B-ENG685 — ~95%: 3 undefined β labels (NRETURN fns) |
| **M-ENG685-TREEBANK** | treebank.sno — Penn Treebank S-expr parser; .ref oracle committed; PASS via CSNOBOL4 and ASM backend | ❌ Sprint B-ENG685 |
| **M-ASM-MACROS** | NASM macro library `snobol4_asm.mac` — every emitted line is `LABEL  MACRO(args)  GOTO` | ❌ Sprint A12 |
| **M-ASM-IR** | ASM IR phase: AsmNode tree between parse and emit | ⏸ DEFERRED — premature unification risks blocking ASM progress |
| **M-BOOTSTRAP** | sno2c_stage1 output = sno2c_stage2 | ❌ |
| **M-SC-CORPUS-R2** | control/control_new all PASS via `-sc -asm` | ❌ |
| **M-SC-CORPUS-R3** | patterns/capture all PASS via `-sc -asm` | ❌ |
| **M-SC-CORPUS-R4** | strings/ all PASS via `-sc -asm` | ❌ |
| **M-SC-CORPUS-R5** | keywords/functions/data all PASS via `-sc -asm` | ❌ |
| **M-SC-CORPUS-FULL** | 106/106 SC equivalent of SNOBOL4 crosscheck | ❌ |
| **M-SNOC-ASM-SELF** | snocone.sc compiles itself via `-sc -asm`; diff oracle empty | ❌ Sprint SC6-ASM |
| **M-SNOC-EMIT** | `-sc` flag in sno2c; `OUTPUT = 'hello'` .sc → C binary PASS | ❌ deferred — C backend |
| **M-SNOC-CORPUS** | SC corpus 10-rung all PASS (C backend) | ❌ Sprint SC4 (deferred) |
| **M-SNOC-SELF** | snocone.sc compiles itself via C pipeline; diff oracle empty | ❌ Sprint SC5 (deferred) |

---

## JVM backend — snobol4x TINY — On Hold

| ID | Trigger | Last Known Status |
|----|---------|-------------------|
| **M-JVM-ROMAN** | roman.sno correct output via JVM backend | ❌ Jasmin error: L_RETURN label not added — RETURN routing bug in emit_byrd_jvm.c |
| **M-JVM-TREEBANK** | treebank.sno correct output via JVM backend | ❌ Jasmin error: L_FRETURN label not added — FRETURN routing bug |
| **M-JVM-CLAWS5** | claws5.sno correct output via JVM backend | ❌ Jasmin error: L_StackEnd (included label) not defined — include/label scope bug |

---

## JVM (snobol4jvm) — On Hold

| ID | Trigger | Last Known Status |
|----|---------|-------------------|
| M-JVM-EVAL | Inline EVAL! — arithmetic no longer calls interpreter | ❌ Sprint `jvm-inline-eval` |
| M-JVM-SNOCONE | Snocone self-test: compile snocone.sc, diff oracle | ❌ |
| M-JVM-BOOTSTRAP | snobol4-jvm compiles itself | ❌ |

---

## NET backend — snobol4x TINY — On Hold

| ID | Trigger | Last Known Status |
|----|---------|-------------------|
| **M-NET-R4** | functions/ data/ — Rungs 10–11 PASS | ❌ Sprint N-R4 — 8 remain: ARRAY/TABLE/DATA + roman |
| **M-NET-INDR** | harness 111/111 — fix `$varname` indirect read: Dictionary/stsfld desync | ❌ Sprint N-210 |
| **M-NET-BEAUTY** | beauty.sno self-beautifies via NET backend | ❌ Gates on M-NET-INDR |
| **M-NET-TREEBANK** | treebank.sno correct output via NET backend | ❌ Gates on M-NET-INDR |
| **M-NET-CLAWS5** | claws5.sno correct output via NET backend | ❌ Gates on M-NET-INDR |

---

## DOTNET (snobol4dotnet) — On Hold

| ID | Trigger | Last Known Status |
|----|---------|-------------------|
| **M-NET-SAVE-DLL** | `-w file.sno` → `file.dll` (threaded assembly); `snobol4 file.dll` runs it | ❌ Sprint `net-save-dll` |
| **M-NET-EXT-NOCONV** | SPITBOL noconv pass-through: ARRAY/TABLE/PDBLK passed unconverted | ❌ Sprint `net-ext-noconv` |
| M-NET-SNOCONE | Snocone self-test: compile snocone.sc, diff oracle | ❌ |
| **M-NET-POLISH** | 106/106 corpus rungs pass, diag1 35/35, benchmark grid published | ❌ see DOTNET.md |
| M-NET-BOOTSTRAP | snobol4-dotnet compiles itself | ❌ |

---

## Shared — On Hold

| ID | Trigger | Last Known Status |
|----|---------|-------------------|
| M-FEATURE-MATRIX | Feature × product grid 100% green | ❌ |
| M-BENCHMARK-MATRIX | Benchmark × product grid published | ❌ |

---

*To resurrect a milestone: move it back to PLAN.md with updated status and sprint assignment.*
