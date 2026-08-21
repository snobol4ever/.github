# FINDING — 2026-08-20 s190 (seat4 `/home/claude4`, Claude Opus 5; queue row `gimpel-drivers-F`, rank 4)
# BATCH F: A GOTO WHOSE OPERAND IS A **FUNCTION CALL** IS A PARSE ERROR — AND IT IS THE ENTIRE PUBLISHED CONTRACT OF `STATEF.inc`. SEVEN OF TWENTY MODULES FALL IN THE ORACLE GAP, AND THE PARSER REPORTS ITS ERROR **TWO LINES LATE**.

**WATERMARK (SCRIP `2cf31532`, RE-PROVED at merged SCRIP `28e2122a` after a second rebase — board identical row for row, `make pristine`, tree clean, RT_OPT `-O0`, NO COMPILER FILE TOUCHED):** corpus board **m3 332/5 · m4 325/11 · SKIP 1 (337)** — the brief's numbers exactly, fail-set identical **by name**. A no-op by construction: the board enumerates `crosscheck` + `beauty_suite` + 4 demos and never reaches `programs/gimpel` or `probe/`.

## 1. THE BOARD — 20 MODULES
**3 GREEN both modes:** `SKIM` · `SPACING` · `TREEREAD`.
**2 SIG11 both modes:** `TR` · `TRUNC`.
**5 PARSE ERROR (no code generated, both modes):** `RSELECT` · `RWORD` · `TRIG` · `STATEF` · `TPROFILE`.
**3 LOUD REFUSAL (the honest arm — SCRIP says what it cannot do):** `SNOREAD` (*expression form not in the landed subset: tree kind 9*) · `STACK` (*DEFINE with a non-literal prototype string*) · `VISIT` (*name operator over this form*).
**7 ORACLE GAP — shipped WITHOUT a `.ref`, deliberately:** `RSEASON_lib` · `RSENTENC` · `RSTORY` · `SNOPUT` · `STONE` · `TIMEGC` · `TIMER`.

## 2. ⭐⭐ THE ONE NEW DEFECT — A GOTO CANNOT CALL A FUNCTION
`:(GO())` — a goto whose operand is a **function call** — is a **PARSE ERROR** in SCRIP, in both modes. The oracle compiles and runs it: the function returns a label NAME **by name** (`:(NRETURN)`) and control transfers there.
**Probe `corpus/probe/gimpel/gim_goto_function_call_parse.sno`, checked in RED per law 0d, shipping its passing siblings in the same file** — an ordinary `:(L1)` and an indirect `:($W)` to the *same* targets are both ACCEPTED, so the refused ingredient is **the call in the goto**, not the goto, not the indirection, and not the by-name return.
⛔ **This is not exotic.** It is the whole published contract of `STATEF.inc`: *"State functions return by executing `:(RET(label))` instead of `:(RETURN)`."* The module itself loads (with the runtime-`DEFINE` refusal); it is the **documented way of calling it** that the parser rejects.
⛔ **NOT the batch-C/D `:<ARG_S>` class** (`gim_seq_code_loop_in_function`): that is an ANGLE-BRACKET direct goto and it SEGVs at RUN time. This one never reaches the parser's exit, and the parenthesised goto is the ordinary spelling.

## 3. ⛔ THE PARSER REPORTS ITS ERROR TWO LINES LATE — IT COST ME A PROBE CYCLE, IT WILL COST THE NEXT SEAT ONE
`TRIG_driver` reports `snobol4:44`. Line 44 is `SIN. = A * (3 - 4 * A * A)`, which **parses perfectly on its own** (verified: `l44_exact` is green). The offending token is on **line 42** — `EQ(27., 27. - 4 * A * A)`, the trailing-dot real literal. Same shift on `TPROFILE`: reported at 18 (`DEFINE('TPROFILE()S,T')`), offending line **16** (`:<CODE(...)>`), confirmed by a two-line probe where `:<CODE(' F = 1 :(RETURN)')>` is a parse error and the plain control is green.
⭐ I spent a full probe cycle proving trailing-dot *identifiers* (`SIN.`, `PI.2`, `SIN.(A)`, a `SIN.` label) are all **accepted**, because the reported line pointed at one. **Expand the includes and read the two lines ABOVE the reported one before minting anything.**

## 4. NOT DEFECTS OF MINE — EVERY RED ATTRIBUTED TO AN ALREADY-FILED CLASS, CHECKED NOT ASSUMED
- `RSELECT` · `RWORD` · `TRIG` → batch B's **`gim_real_literal_parse`** (`RANDOM.sno:5`'s `4676.`/`414971.`; `DEXP.sno`'s `27.`). Verified directly: bare `27.`, `27. - 4`, `EQ(27.,27.)`, `6. / 3.` are each a parse error where the oracle answers. **No duplicate probe minted.**
- `TPROFILE` → batch D's **`:<expr>` direct-goto** class, via `LPROG.sno:16`.
- `TRUNC` → batch C's **`gim_seq_code_loop_in_function`** (through `SEQ.sno`); `TR` → batch B's **`gim_defer_pred_in_pattern_segv`** family (`$('TR_' OP)` + `*PUSH()` in a pattern). Both filed probes re-run at HEAD: **still rc=139**. **No duplicates minted.**

## 5. ⛔ THE SEVEN ORACLE-GAP MODULES, AND THE TWO WALLS ARE STILL DISJOINT (batch E's headline, re-confirmed on a fresh set)
| module | `sbl -bf` | CSNOBOL4 |
|---|---|---|
| `RSENTENC`, `SNOPUT` | `BAL.sno(11) ERROR 042` — protected built-in `BAL` | `RANDOM.sno:5 Error 1` |
| `RSEASON_lib` | `ERROR 041` field function wrong datatype | `RANDOM.sno:5 Error 1` |
| `RSTORY`, `STONE` | 4-argument `INPUT`/data file | *"Could not open rstory.in / phrases.in"* |
| `TIMEGC`, `TIMER` | `ERROR 285 — include file cannot be opened` | `Error 30` |
⛔ **`TIMEGC`/`TIMER` are the `lon-include-root` row, NOT a batch-F defect**, per this row's own caveat. Measured: **`resolution.sno` does not exist anywhere in the corpus**, and `system.inc` exists only at `corpus/programs/include/system.inc`, which neither engine's search path reaches from `programs/gimpel`.
⛔ **`RSTORY`/`STONE`'s CSNOBOL4 refusal is batch E's lowercase data-file trap** (`rstory.in` vs shipped `RSTORY.IN`; `phrases.in` vs `PHRASES.IN`). **Batch E measured the obvious cure INERT and said not to spend a rung on it — I did not.**

## 6. ⭐ TWO NEAR-MISSES I ALMOST CHECKED IN, KEPT VISIBLE
1. **I almost reported "a goto cannot take a function call" from a probe the ORACLE ALSO REJECTS.** My first probe's function returned a *value*, so `sbl` gave `ERROR 021 — function called by name returned a value`. The defect is real, but only the **by-name** (`:(NRETURN)`) probe proves it, which is exactly what `STATEF.inc` does. **A probe whose oracle arm errors proves nothing about SCRIP.**
2. **I almost pinned three error dumps as `.ref`s.** `sbl` exits 0 after a fatal error (batch B's harness finding) and CSNOBOL4 prints *"Could not open …"* and exits 0 too. A guard that rejects any candidate ref matching `ERROR [0-9]+` caught two; the third (*"Could not open"*) matched no error keyword at all and was caught only by reading it. ⭐ **The keyword guard is necessary and not sufficient — a `.ref` must be READ before it is committed.**

## 7. STONE'S DOUBLE INCLUDE IS REAL BUT MASKED
Computing the transitive include closure **before writing any driver** predicted one double include in the batch: `STONE` → `PHRASE.sno` → `RSENTENC.sno` and `STONE` → `QUEST.sno` → `RSENTENC.sno`. Batch D's headline says that hangs SCRIP with no output and no diagnostic. It does **not** hang here — SCRIP dies earlier, at the `RANDOM.sno` parse error, so the double include is **masked, not absent**. It will surface the moment the real-literal parse gap is fixed. Recorded so that fix's blast-radius sweep expects it.

## 8. WHAT THE NEXT SEAT INHERITS
1. **The real-literal parse gap is still the highest-yield defect in this corpus** — batch E said 5 of its 12 reds; batch F adds 3 more directly and masks a 4th. One parse rule.
2. **`gim_goto_function_call_parse` is the cheapest new thing here** — a parser gap with three passing siblings already isolating the ingredient.
3. Batch F ships **13 drivers with oracle `.ref`s and 7 without**, every one named above with the reason.

**WITNESSES (corpus):** 20 `<NAME>_driver.sno` in `corpus/programs/gimpel/` (13 with live-oracle `.ref`, 7 deliberately without) + 5 `.in` fixtures + `corpus/probe/gimpel/gim_goto_function_call_parse.{sno,ref}`.
**SCRIP:** no source change. **`.s` regen NOT APPLICABLE.**
