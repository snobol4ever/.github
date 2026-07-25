# FINDING 2026-07-25 (Claude) — SN4: VALUE-ASSIGNMENT CAPTURE START ZEROED AT THE 20th ARBNO ITERATION (claws5); BOTH MODES; MINIMAL REPRO LANDED

**Session context:** Lon widened the demo working set from the documented TEN (`*-match.sno` + `*-match-fence.sno`)
to **FIFTEEN** — every `.sno` in the CLAWS5 / TREEBANK / JSON / CALCULATOR families, i.e. the ten PLUS
`claws5.sno`, `calculator-1.sno`, `calculator-2.sno`, `treebank-list.sno`, `treebank-array.sno`.
⚠ `GOAL-SNOBOL4-BB.md`'s WORKING SET banner (s151) explicitly fences those five out ("Do NOT wander into … the
non-`-match` base variants"). **That banner is now STALE BY DIRECTIVE and must be updated** — the five are in scope.

---

## 1. THE BOARD OF 15 (first time all fifteen were run; identity vs SPITBOL oracle, both modes)

Oracle recipe per `test_demo_full_3way.sh`: temp-prepend `-CASE 0` + tab `&TRIM = 0` (never patch corpus),
`sbl -b -d512m -i64m` (this build REJECTS `-P`), treebank adds `-s256m`, `ulimit -s unlimited` for SCRIP.

| program | m3 | m4 |
|---|---|---|
| claws5 | **DIVERGE** | IDENT |
| treebank-list | IDENT | **DIVERGE** (emits a single `''`, rc=0) |
| treebank-array | IDENT | **DIVERGE** |
| the other 12 | IDENT | IDENT |

**These are MODE34-IDENTICAL violations, not merely wrong answers** — each fails in exactly ONE mode.
`scripts/test_demo_full_3way.sh` **FAILS today** (`claws5: DIVERGES`, `treebank: DIVERGES`) and is
PRE-EXISTING: recent sessions reported "10 demos 3-way clean", which is the working-set ten — a DIFFERENT set.
The gate that covers these two was not being run. Widening to 15 is what surfaced it.

---

## 2. THE claws5 BUG — CHARACTERIZED EXACTLY

Failing construct (claws5.sno main pattern):
```
+                | (NOTANY('_') BREAK('_')) . wrd
+                  '_'
+                  (ANY(UCASE) SPAN(DIGITS UCASE)) . tag
```
**Symptom:** for exactly ONE token, `wrd` receives a string running from **offset 0 of the whole subject**
through the end of that token's word part. The END of the captured span is CORRECT; the START is zeroed.
`tag` is correct. Every other token in the same run is correct.

**SPITBOL manual authority (Ch. "BREAK/SPAN", read this session):** *BREAK(S) matches up to but not including
any character in S; the string matched must always be followed in the subject by a character in S;*
**BREAK(S) will never return a string containing any characters in S.** The bad capture is FULL of `_`.
So this is a definitive semantic violation, not a tolerable difference. (The manual also names
`(NOTANY(S) BREAK(S))` as the sanctioned construction for "a BREAK which will not match the null string" —
claws5's idiom is textbook, not exotic.)

### 2.1 MEASURED PROPERTIES (each one an experiment, not an inference)

- **It is the 20th word token.** Corpus: the mis-captured token is `too_AV0`, the **20th** word token after the
  single `1_CRD :_PUN` sentence marker. Synthetic (`t01_AA`…`t30_AA`): the mis-captured token is **`t20`**.
  Two independent settings, same index.
- **CONTENT-INDEPENDENT.** Replacing the word part at that position with `zzz` / `zz` / `zzzz` / `z` all
  DIVERGE. The original `to`/`too` prefix-overlap hypothesis is **FALSIFIED** — it has nothing to do with `to`.
- **NOT byte-offset-driven.** The failing token sits at offset 172 in the corpus case and 145 in the synthetic
  case. Different offsets, same ordinal.
- **ONE-SHOT, NOT PERIODIC.** With 70 tokens, ONLY `t20` fails — `t40`, `t60` are fine. A single boundary
  crossing, not a recurring modulus.
- **BOTH MODES.** On the minimal synthetic repro **m3 AND m4 both DIVERGE**. The full-corpus m4 IDENT in §1 is
  therefore LUCK, not correctness — with many sentence markers the trigger does not arise. Do not read the
  m3-only column as "mode-3 bug".
- **⚠ UNEXPLAINED (do not paper over):** prepending a SECOND sentence marker (`1_CRD :_PUN 2_CRD :_PUN `)
  makes the divergence **vanish entirely** rather than shift by one. Three markers likewise clean. So the
  trigger is NOT a plain "21st ARBNO iteration" counter. This is the loose thread — chase it first.

### 2.2 MINIMAL REPRO (deterministic, ~40 bytes of input)

```
printf '1_CRD :_PUN %s \n' "$(python3 -c "print(' '.join('t%02d_AA'%i for i in range(1,31)))")" > z.dat
scrip --run corpus/programs/snobol4/demo/claws5.sno < z.dat      # key 't20' replaced by a giant span
```
Bisected from the full 989-line corpus down to this; the transition IDENT→DIVERGE is exact at token 22 of the
first three corpus lines (= the 20th word token).

⚠ **BISECT TRAP (cost a detour, recorded so it is not re-paid):** any input LACKING a `<digits>_CRD :_PUN`
sentence marker diverges for an UNRELATED reason — `sentno` is null, SPITBOL raises `ERROR 235 subscripted
operand is not table or array` while SCRIP silently prints nothing. That is a SECOND defect (SCRIP should
error too) and it CONTAMINATES any bisect that shortens the input past the marker. Always keep the marker.

### 2.3 HYPOTHESES FALSIFIED BY MEASUREMENT (negative results — do not re-walk these)

Under gdb (installed this session; `break … ; run < z.dat`) on the mode-4 binary, **none of these functions is
ever called** by this program:
- `rt_zcol_push` (pattern_match.c:1275) — the ARBNO v2 per-iteration collection, `ZC_COLLECTION ==
  ZC_COL_MALLOC` confirmed live, doubling 4→8→16→32. **Zero hits.** Not the mechanism.
- `rt_cap_push` / `rt_cap_top` (pattern_match.c:740/765) — the capture-frame stack whose `rt_cap_top` returns
  **0** on `gen != g_cap_gen || !sp` (a perfect symptom match, capacity starts at 16 and doubles — *very*
  tempting). **Zero hits.** Not the mechanism.
- `rt_dcap_end_ok_open` (pattern_match.c:695) — takes `(mark, top, subj)`, i.e. exactly the span pointers.
  **Zero hits.** Not the mechanism.

⇒ **The capture span is computed ENTIRELY IN EMITTED CODE**, consistent with pattern_match.c:775's own note
(*"rbp-dcap: the COND (deferred) arm no longer calls here — bb_match_capture phase 1 records its entry inline
on the rbp stack"*). **NEXT RUNG: `src/templates/bb_match_capture.cpp` + the `flat_cap_off` / CAP-NOFILL
zeroing arm** (`emit.cpp:2319`, `emit.h:587` — capture head cells are "implicit-zero citizens", 48-site cap,
`SCRIP_CAP_NOFILL=0` falls back to the s139 blanket pull-down).

⚠ **BUT TWO MORE CANDIDATES ARE ALREADY EXCLUDED BY A/B (run this session against the minimal repro):**
`SCRIP_CAP_NOFILL=0`, `SCRIP_OPT=0`, and both together each leave the failure **bit-for-bit unchanged**
(still exactly `t20` lost, exactly 1 bogus giant key). So it is **NOT** the CAP-NOFILL capture-head zeroing
arm and **NOT** the optimizer. The remaining surface is `bb_match_capture.cpp`'s inline rbp-stack entry
recording itself and the ARBNO body's per-iteration save-cell geometry (`bb_match_arbno.cpp`
`arbno_fill_cells` zeroes "the cap BUF QUAD of each body SAVE cell at its window-relative offset").
Recommended next probe: dump `--compile` asm for the repro and read the capture-start store/reload around the
ARBNO body SAVE cell; the ordinal-20 boundary should show up as a cell that is re-zeroed or re-based once.

---

## 3. HONEST STATE

**NOT FIXED.** Localized to the emitted capture path with a deterministic minimal repro and three
runtime candidates positively excluded. No code changed this session; tree is pristine.

`treebank-list` / `treebank-array` m4 (`''`, rc=0) were NOT investigated beyond §1.

RT_OPT=-O0 throughout (no `-O2` anywhere — O2-DIRECTED-ONLY honored). Gates re-proven green at session start:
smokes 7/7 both modes; crosscheck m3 314/1 · m4 309/4 · DIVERGE=3 = the s157 watermark exactly.
