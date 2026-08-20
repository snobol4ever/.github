# FINDING s186 — gimpel batch B: 24 drivers, and a store through the name of a DATA field that silently does nothing

**Session:** 2026-08-20 s186 · seat2 `/home/claude2` (Claude Opus 5) · queue row `gimpel-drivers-B`
**Trees:** SCRIP `8d7c5917` (untouched this session — no compiler edit) · corpus `programs/gimpel/` + `probe/gimpel/`
**Ruling served:** Lon, s183 in-chat — *"You should make tests out of each Gimpel function. Make an entire test suite around it."*

---

## 1. WHAT LANDED

25 manifest rows in batch B → **24 drivers**, each `corpus/programs/gimpel/<NAME>_driver.sno` beside its module, `-INCLUDE "<NAME>.sno"` at the top, cases written from the module's **header comment** and never from its implementation, `.ref` minted from the **live oracle** (`x64/bin/sbl -b`; every driver in this batch took plain `-b`, none needed `-bf`), deterministic, no `DATE()`/`TIME()`/randomness.

**9 GREEN both modes:** `LIKE` `LPAD` `PERMUTAT` `PLI_STMT` `PUSH` `READ` `READRL` `RESOLUTI` `REVERSE`.
**15 checked in RED per law 0d,** named in §3.

Four drivers needed input; they carry it as `<NAME>_driver.in` (plus `.d1`/`.d2` for MFREAD), which is the stdin convention `scorecard_snobol4.sh`'s own `stdin_for()` already implements.

## 2. THE TWO ROWS THAT ARE NOT DEFECTS AND MUST NOT BE READ AS ONE

**`PHRASES` gets no driver, and should not.** `PHRASES.sno` is **not a module** — it is a BNF grammar data file (`<GOOD>::=excellent|wonderful|…`), the same bytes as `PHRASES.IN` modulo CRLF, defining nothing, and **no gimpel module reads either file**. `sbl` does not merely reject it, it **SIGSEGVs (rc=139)** on it. It is an orphan data file wearing a `.sno` extension, and it sits in the `gimpel` suite's denominator today as a permanent unscoreable row. Corpus hygiene, not codegen: it wants renaming to `.IN`/`.dat` or moving out of the `-name *.sno` sweep. **Not done here — it is another seat's suite, and the row that owns the suite's enumeration is `gimpel-suite-harness`.**

**`MFREAD` ships without a `.ref`, and cannot have one.** `MFREAD.sno` **cannot load under the live oracle at all**: its setup runs `OPSYN('REWIND.','REWIND')` and SPITBOL raises `ERROR 248 — attempted redefinition of system function` at `MFREAD.sno(8)`. No driver can produce oracle ground truth for it. `MFREAD_driver.sno` is committed anyway (it is the driver the contract asks for, and it is what the next seat re-runs the day the oracle question is answered) but with **no `.ref`, deliberately** — hand-authoring one is forbidden. SCRIP independently FATALs on it (`assignment subject form not in the landed subset`).

## 3. ⭐ THE BOARD — 15 REDS, AND WHAT EACH ONE IS

| module | m3 | m4 | what it is |
|---|---|---|---|
| `LEXGT` | DIFF | DIFF | **silent wrong answer** — `LEXGT` never succeeds; every one of 8 cases answers `notgt`, oracle says `gt` for 3. The whole `BLEND`→`DIFF`→`REPLACE(&ALPHABET, ALPHA, &ALPHABET)` transliteration chain yields a wrong verdict. Both modes agree, so **not** a 1:1 divergence. |
| `LINEARIZ` | RC1 | RC1 | **silent wrong answer then Error 5** — the linearized chain is truncated after 2 of 6 nodes. Root-caused, §4(a). |
| `LPROG` | parse error | COMPILE_FAIL | `:<CODE(' LPROG = &STNO :(RETURN)')>` — the direct-goto-into-`CODE()` edge (`DEFINITION OF DONE` item 5 names this edge explicitly). |
| `LSORT` | FATAL | COMPILE_FAIL | lowerer: *"name operator over this form is outside the landed subset"* — `.LSORTA` (name of the return variable) and `.NFLD(L2)` (name of a field-function call). |
| `MDY` | **SIG11** | **PASS** | **1:1 DIVERGENCE.** m4 runs all 10 cases correctly; m3 SIGSEGVs. Root-caused, §4(b). |
| `MFREAD` | FATAL | FATAL | oracle-blocked, §2. |
| `ONCE` | Error 22 | ASM_FAIL | `CONVERT('ONCE(' &STCOUNT ')','EXPRESSION')` used as a pattern — a converted expression re-evaluated at each match attempt. |
| `ORBREAK` | **SIG6 / DIFF, run to run** | **SIG11 / SIG6** | **NONDETERMINISTIC.** §4(c). |
| `ORDER` | DIFF | **SIG11** | **silent wrong answer** — `ORDER('banana')` = `ann`, oracle `aaabnn`. Root-caused, §4(d). |
| `PERMS` | FATAL | COMPILE_FAIL | lowerer: *"SN4-REPL slice 1: replacement subject must be a plain variable"* — `FIRST_OP<K> LEN(1) . S1 TAB(K) . S2 = S2 S1`, a pattern replacement over a **subscripted** subject. |
| `RANDOM` | parse error | COMPILE_FAIL | trailing-dot real literal, §5. |
| `READL` | DIFF | DIFF | **silent wrong answer** — returns an empty list where the oracle returns `one two three`. Same root as `LINEARIZ`, §4(a). |
| `REDEFINE` | FATAL | COMPILE_FAIL | lowerer: *"DEFINE with a non-literal prototype string"* — `DEFINE(DEF, LBL)` over a computed prototype. |
| `REORDER` | **PASS** | **SIG11** | **1:1 DIVERGENCE, the other way round** — m3 produces all 11 lines correctly; m4 SIGSEGVs. |
| `REVL` | RC1 | RC1 | omitted leading argument, §5. |

⛔ **Three of these are m3≢m4 all by themselves** — `MDY` (m3 dies, m4 correct), `REORDER` (m3 correct, m4 dies), `ORDER` (m3 wrong answer, m4 dies). The 1:1 law is breached in **both directions** inside one 25-module batch of code nobody wrote to exercise SCRIP.

## 4. ⭐⭐ FOUR CLASSES ROOT-CAUSED, THREE MINIMIZED INTO `probe/gimpel/`

Each witness carries a live-oracle `.ref`; two carry their **own passing sibling in the same file** — the identical statement with one ingredient removed — so the failing ingredient is *named*, not guessed (ASM-DIFF-FIRST's "passing sibling with one ingredient removed").

**(a) A store through the NAME OF A DATA FIELD is a SILENT NO-OP.** `probe/gimpel/gim_name_of_field_store.sno`, 9 lines:

```
	DATA('ND(L,R)')
	X  =  ND('a','b')
	P  =  .R(X)
	$P  =  'CHANGED'
	OUTPUT  =  R(X)        <- oracle CHANGED, SCRIP b
	Y = 'orig' ; Q = .Y ; $Q = 'CHANGED2' ; OUTPUT = Y   <- both CHANGED2
```

The same idiom over a **plain variable** is correct in SCRIP. So the ingredient is **the field name**, not the name operator and not the indirect store. This is one defect with two visible faces: `LINEARIZE` strings its tree through exactly `LAST_NAME = .RSON(T)` … `$LAST_NAME = T` and therefore returns a chain truncated after two nodes; `READL` builds its list through `N = .READL` … `$N = LINK(,S)` … `N = .NEXT($N)` and returns an empty one. **Both are silent — neither errors at the point of loss.**

⛔ **`PUSH_driver` is GREEN and that is the useful negative:** `PUSH` returns `.VALUE(PUSH_POP)` by `NRETURN` and the driver assigns *through the returned name* (`PUSH('z') = 'ASSIGNED-BY-NAME'`, `TOP() = …`) and SCRIP gets it right. **Name-return assignment to a field works; `$NAME =` indirect store to a field does not.** A fix aimed at "names of fields" generally would be aimed at the wrong half.

**(b) A deferred predicate call with arguments inside a pattern SIGSEGVs.** `probe/gimpel/gim_defer_pred_in_pattern_segv.sno`, 8 lines — an immediate value assignment (`$`) plus `*GT(DY,X)` reading the variable the `$` just assigned:

```
	P  =  '(' I $ X *GT(DY,X) ',' I $ M
	T  =  '(334,12)(31,2)(0,1)'
	T  P
```

Distilled it SIGSEGVs **both** modes; inside `MDY.sno` the same construct SIGSEGVs m3 while m4 runs the whole driver correctly. ⭐ **This is the M1 family on independent evidence** — a deferred call *with arguments* inside a pattern is beauty's `nInc() *Expr5 FENCE(…)` and BLANKS's `LEN(*DIFF(N,' '))`. `MDY.sno` is a 1971 date routine; it cannot have encoded a theory of this bug.

**(c) `ORBREAK` is nondeterministic and its accumulator collapses.** Three consecutive m3 runs of the same binary on the same input gave `DIFF`, `SIG6`, `DIFF`; m4 gave `SIG11`, `SIG11`, `SIG6`. The `SIG6` arm is `[ZHP] heap exhausted (512 MB, 1 blocks) after storage regeneration`. When it *does* complete, the answer is wrong in a specific way: `ORBREAK(',LISO,LIST,ABC,LISTER')` returns **`L`** where the oracle returns **`LLAL`**, and `,(abc),XY,(pq)` returns `pq` for `abcXpq` — i.e. **only the last alternative survives the `ORBREAK = ORBREAK C` accumulation.** ⛔ **Not minimized, and I am saying so rather than shipping a guess:** the obvious 6-line repro (a `DEFINE`d function accumulating `ACC = ACC C` around a `LEN(1) . C =` replacement loop) is **GREEN in both modes**, so the trigger is more specific than "self-accumulation in a return variable" — the interleaved `TLIST ANCSEIZE =` replacement, where `ANCSEIZE` is built over `BREAK(BC) | REM` with a value assignment, is still in the frame. Left for the follow-up rung with the symptom pinned.

**(d) `(BREAK(H) | REM) . S1` drops the matched prefix when `H` is large.** `probe/gimpel/gim_break_value_drops_prefix.sno` — SCRIP answers `[bb]` where the oracle answers `[abb]`; the **passing sibling in the same file**, the identical statement with a 25-character literal set, agrees in both modes. Module-level shortest repro is `ORDER('bab')` (oracle `abb`, SCRIP `bb`) — a **three-character** input.

⛔ **Do not read (d) as "large sets are the bug" — I could not close the threshold and am recording the contradiction instead of smoothing it.** A 158-char set carved from `&ALPHABET` fails while a 25-char literal passes; but a **26**-char set carved from `&ALPHABET` and passed as a *function argument* also fails. Size is a *correlate*, not established as the cause; provenance (carved from `&ALPHABET`) and argument-passing are both still live. One further probe (`&ALPHABET LEN(*N) . H`, deferred `LEN`) hit the ZHP heap exhaustion of (c) instead and could not be used to bisect.

## 5. TWO CLASSES BATCH B REACHED INDEPENDENTLY THAT **BATCH A OWNS**

seat1's batch A (corpus `09967f5c`) landed while this batch was in flight and had already minimized both:

- **Omitted LEADING argument shifts arguments left** — batch A's `gim_omitted_arg_shift`. Batch B reached it through `REVL.sno`'s `LINK(,'d')`, which binds `'d'` to `NEXT` instead of `VALUE` and hands back a one-element list.
- **Trailing-dot real literal is a parse error** — batch A's `gim_real_literal_parse`. Batch B reached it through `RANDOM.sno`, whose entire seeded recurrence is written `REMDR(RAN_VAR * 4676., 414971.)`, so `RANDOM_driver` never reaches code generation in either mode.

I had committed near-duplicate witnesses for both and **deleted them** (corpus `0a8ef9e1`): batch A's are strictly better — `gim_omitted_arg_shift` carries the trailing-omission control arm mine lacked. **Two seats hitting the same two classes from different modules on the same afternoon is the suite working, not redundancy** — it is the second independent confirmation.

## 6. ⛔ A HARNESS DEFECT THIS ROW TRIPPED OVER, AND IT BELONGS TO `gimpel-suite-harness`

**`sbl` exits 0 after a fatal runtime ERROR.** Measured: `sbl -b MFREAD_driver.sno` prints `ERROR 248 — attempted redefinition of system function`, its statement/timing/memory dump, and **returns rc=0**.

`scorecard_snobol4.sh` sets `have_live=1` on `[ $rc -eq 0 ]` and then grades SCRIP against that stdout. So for **every** program whose oracle dies at runtime, the board compares SCRIP's output against a **SPITBOL error dump** — one containing `execution time msec`, `memory used (bytes)` and `memory left (bytes)`, i.e. a "ground truth" that is not even stable across runs. Such a row is not scored as `ORACLE_FAIL`; it is scored as `DIFF`, which reads as a SCRIP defect.

I did not change the shared harness from this row (it is `gimpel-suite-harness`'s file and this row's mandate is drivers), but the local runner used here guards it, and the guard is two lines: after `rc -eq 0`, also require that the oracle's stdout does not match `^[^ ]+\([0-9,]+\) : ERROR [0-9]+ --`. **`MFREAD` is the live instance today; the class is every module whose setup aborts SPITBOL.**

## 7. RECEIPTS

- **Corpus fail-set for the existing suites UNCHANGED**, `test_corpus_snobol4.sh` at SCRIP `8d7c5917`, tree clean: **m3 PASS=332 FAIL=5 · m4 PASS=325 FAIL=11 SKIP=1 (337 total)** — the brief's numbers exactly, fail-set identical **by name** (m3: `145_pat_left_assoc_via_arbno_fence` `160_pat_alt_inner_gen_resume` `175_pat_bal_generator_retry` `1110_array_1d` `216_indirect_goto_computed`). This is a no-op by construction — the board enumerates `crosscheck` + `beauty_suite` drivers + 4 demos and never reaches `programs/gimpel` or `probe/` — and **zero SCRIP files were touched this session.**
- Every driver's m3 **and** m4 verdict is in the §3 table; the 9 green ones are green in both.
- corpus `0a8ef9e1` (drivers, probes, dedup, s186 header correction). `.github` this file + cursor.

## 8. WHAT THE NEXT SEAT SHOULD TAKE

1. **§4(a) is the cheapest real fix in this batch** — one silent no-op, two silent wrong answers (`LINEARIZ`, `READL`), a 9-line witness with a green control, and `PUSH_driver` standing by as the negative that says which half is already right.
2. **§4(b) is M1 evidence, not a gimpel curiosity.** Route it into the M1 lane beside beauty's grammar and BLANKS.
3. **`REORDER` (m3 PASS / m4 SIG11) has no witness yet** and is the cheapest remaining 1:1 divergence in the batch — the driver is 16 lines and the module is 10.
4. **Do not re-derive §4(c) or §4(d)'s threshold from scratch** — the failed ablations are recorded above precisely so they are not repeated.
