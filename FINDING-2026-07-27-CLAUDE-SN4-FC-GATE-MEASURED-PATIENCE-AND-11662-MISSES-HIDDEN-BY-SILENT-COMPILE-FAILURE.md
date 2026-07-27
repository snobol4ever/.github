# FINDING — 2026-07-27 — s184 — FC GATE MEASURED WALL-CLOCK PATIENCE, NOT THE COMPILER; 11,662 MISSES WERE HIDDEN BEHIND A SILENT COMPILE FAILURE

**RUNG.** s183 LIVE CURSOR item (6), first entry: *"fix `test_gate_fc_no_residual_rbp.sh` to exclude beauty or fail on timeout."* LANDED as SCRIP `e63a8b6a`. The rung named one defect; measuring first found three.

---

## 1. THE GATE'S DOCUMENTED BASELINE WAS NEVER TRUE OF THE SCRIPT

Header claimed `BASELINE AT LANDING (s182): 0 misses across 52 demo+feat programs / 643 graphs`. The script asserted `total -ne 0 -> exit 1`. **It measured 5,328 and therefore FAILED on every run since it landed** — permanently red, which is why s183 correctly wrote "do NOT use gate headline as a regression signal." Three independent defects, all fixed:

**(1) TIMEOUT COUNTED AS DATA.** The body piped `timeout 20 "$SCRIP" ... 2>&1 >/dev/null | grep -c '\[FC-MISS\]'`. The pipeline's exit status is **grep's**, so `timeout`'s 124 was discarded and a killed compile's partial stderr was scored as if it were a completed measurement. `beauty.sno` does not finish, so its contribution measures how long you were willing to wait:

| budget | beauty.sno misses |
|--------|-------------------|
| 20 s   | 3,984 / 4,014     |
| 120 s  | 26,088            |

This is the arithmetic explanation for a discrepancy already visible in the prose: s183 read ~5,600 total where s184 reads 5,328 **on the identical tree** (`e5ce9f12`+`c98ce1c9`, verified present). Same compiler, different truncation point. Any "total" containing this number is unreproducible across machines, loads, and sessions.

**(2) A FAILED COMPILE SCORED AS A CLEAN PASS.** A program emitting `-- no code generated` produces zero `[FC-MISS]` lines and was indistinguishable from a program that compiled perfectly. Two of the 52 were in this state.

**(3) INCLUDES NEVER RESOLVED — AND THIS ONE HID THE LARGEST POPULATION IN THE CORPUS.** `demo/expression.sno` `-INCLUDE`s `semantic.sno` / `omega.sno` / `trace.sno`. The gate set no search path, so the program took defect (2) and silently scored 0. With the path supplied it compiles clean (0 errors) and reports **11,662 misses in 27 s** — deterministic across three runs, and larger than everything else in the corpus combined. **It was invisible for the entire life of the old gate.**

Resolution rule, read from `src/driver/scrip.c:545-573`: search order is source-file dir → `$SNO_LIB` (colon-separated) → nearest ancestor containing `lib/` → `.`. **There is no `-I` flag.** ⚠ `REPO-corpus.md` documents the include dir as `programs/snobol4/demo/inc/` — **that path does not exist in the tree**; the files live in `programs/snobol4/beauty_suite/`. Corpus doc needs correcting.

## 2. HONEST BASELINE (deterministic, repeated passes byte-identical)

| class | programs | misses | note |
|-------|----------|--------|------|
| OK | 50 | **13,006** | the ratchet |
| TIMEOUT | 1 | — | `beauty.sno`, quarantined, contributes nothing |
| NOCODE | 1 | — | `f13_eval_code.sno`, §4 |

1,344 of the 13,006 sit outside `expression.sno` — **exactly the number s183 measured**, which is what confirms both sessions are reading the same tree.

## 3. GATE IS NOW A RATCHET, NOT A ZERO-ASSERT

Zero is not reachable mid-conversion; asserting it leaves the gate permanently red and therefore ignored — the failure mode it was already in. Now: classify OK/TIMEOUT/NOCODE, headline over OK only, fail on regression above `FC_BASELINE`, and fail on any **new** timeout or **new** compile failure. Known-bad programs are named in-script and reported loudly every run — they are defects on record, not exemptions, and leave the list only by being fixed.

⚠ **SELF-INFLICTED WART CAUGHT IN TEST.** A program that leaves the OK set takes its misses with it, so the count *drops* and the first draft printed `IMPROVED — lower FC_BASELINE to lock the win in`. Acting on that advice bakes a truncation artifact into the baseline — precisely the bug class this rewrite exists to kill. Ratchet reporting now runs **after** failure detection and suppresses the advice when anything left the OK set. **All three arms verified to fire:** baseline exit 0 · regression exit 1 · new-timeout exit 1.

## 4. INCIDENTAL DEFECT — DIRECT GOTO REJECTS INTERIOR BLANKS (ORACLE-CONFIRMED)

`feat/f13_eval_code.sno` fails to parse at line 4, `:< C >`. Manual p.187 documents `:<VAR>` as the **direct Goto** — branch to the start of a `CODE` block — with conditional `:S<VAR>`/`:F<VAR>` forms. Isolated:

| form | SCRIP | SPITBOL `sbl -b` |
|------|-------|------------------|
| `:<C>` | parses | prints `1` |
| `:S<C>` | parses | — |
| `:< C >` | **parse error: syntax error** | prints `1` |

Only interior blanks fail. SPITBOL accepts both; RULES.md makes SPITBOL semantics binding for SNOBOL4. **This is a real parser defect, not an unimplemented feature.** It is currently quarantined by the gate rather than hidden by it. Not fixed here — it is a lexer/parser rung, not an emitter rung.

## 5. beauty.sno RUNAWAY — MEASURED, NOT SOLVED

Handing off with the measurement, explicitly **not** a diagnosis.

**MEASURED:** 627 source lines → **34,585,351 asm lines at 280 s, still running** (killed, not finished). Emission rate is *flat* across a 7× time span — 115k lines/s at 40 s, 123k lines/s at 280 s, no deceleration. ~55,000 asm lines per source line and climbing. In a 30 s sample: `.intel_syntax noprefix` (a **once-per-file** directive) emitted **28,722** times with irregular spacing; 23 distinct `proc_*` labels each emitted **exactly once** (so top-level procs are *not* duplicated); 564 distinct `.Lbynamefn` names across 12,978 emissions.

**NOT PROVEN: that it never terminates.** Flat rate over 7× time is strong evidence, not proof. The decisive experiment — comparing two windows far apart in the stream to exhibit a repeating cycle — was **not run**; it was cut for session budget. Do not record non-termination as established until someone runs it.

⚠ **CORRECTION TO `FINDING-2026-07-26-...-BYNAMEFN-DUP-LABELS-BEAUTY-M4-NEVER-ASSEMBLABLE.md`.** That finding's completion test says *"beauty `--compile` (budget ≥5 min)"*. **280 s is not remotely close** — the stream was still accelerating slightly at 34.6M lines. Its `.Lbynamefn`-from-`nid` collision diagnosis is consistent with what s184 measured (nid resets per chain; 564 names covering 12,978 sites is exactly that shape), but **the relationship between the label collision and the unbounded emission is unestablished.** They may share a cause or may be independent; the 28,722 file-preamble re-emissions are not explained by label naming at all. **Renaming labels on a compile that never yields a complete `.s` fixes nothing observable** — settle termination first, then the labels.

**METHOD NOTE.** The MONITOR-FIRST rule does not reach this bug: the monitor compares *runtime* trace events against SPITBOL/CSNOBOL4, and this is a compile-time non-termination with no runtime to observe. The bracket theorem does not apply. Stated so the next session does not burn its budget trying to point the monitor at it.

---

**FILES.** SCRIP `e63a8b6a` — `scripts/test_gate_fc_no_residual_rbp.sh` (sole file; no codegen touched, so no `.s` artifact regeneration per RULES.md step 4).
**WATERMARK.** Untouched by this session: m3 314/1 · m4 312/1 · DIVERGE=0.
