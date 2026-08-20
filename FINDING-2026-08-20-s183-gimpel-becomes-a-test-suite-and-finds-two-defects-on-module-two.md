# FINDING s183 — gimpel becomes a TEST SUITE, and finds two real defects on the second module tried

**Session:** 2026-08-20 s183 · HQ (Fable 5) · corpus `programs/gimpel/`, SCRIP `3da13598`
**Ruling routed:** Lon, s183 in-chat, verbatim in substance — *"You should make tests out of each Gimpel function. Make an entire test suite around it."*
**Queue rows minted:** `gimpel-drivers-A`…`F` + `gimpel-suite-harness` (both channels, TWO-CHANNEL LAW).
**Answers:** the question HQ escalated at HQ-73 on seat1's behalf (row `oracle-format-unscr`).

---

## 1. THE PROBLEM, AND WHY NORMALIZATION COULD NEVER FIX IT

gimpel scores **0.0** with all 145 rows UNSCR. seat1 measured the real causes (not the guessed ERROR 214): **ERROR 230 from CRLF** in 143/145 files, and **ERROR 285** from `-INCLUDE` name case-mismatch — a DOS-authored library on a case-sensitive filesystem. Both were cured by pure corpus normalization (CRLF stripped; 129 spellings in 75 files).

That took UNSCR **145 → 135, and stopped.** The remaining **131 are library modules**: a `DEFINE` plus a `:(X_END)` label, no main body, no `END`, **no output to score**. They are unscoreable **by construction, not by defect**. No amount of normalization reaches them — the missing thing is not a fix, it is **a caller**.

## 2. THE CONVENTION (proven end-to-end, committed as worked examples, not prose)

- `corpus/programs/gimpel/<NAME>_driver.sno`, beside the module (the `beauty_suite` precedent).
- `-INCLUDE "<NAME>.sno"` at the top. The module's setup runs, falls through its `<NAME>_END` label, and control continues into the driver's statements. **Verified for both the self-contained and the include-bearing shape.**
- ⭐ **THE MODULE'S HEADER COMMENT IS THE SPEC.** e.g. `BASE10.sno` documents *"convert the string N assumed to be a numeral expressed in base B arithmetic to decimal … digits beyond 0-9 are from the set A-Z"*. Write cases from the **contract**, never from reading the implementation — otherwise the suite encodes the bug as the expectation and certifies the defect.
- `.ref` generated from the **live oracle** (`sbl -b`, fall back to `-bf` and say which). Never hand-authored, never md5-pinned.
- Deterministic only: no `DATE()`/`TIME()`/random.
- **A red is never denied (law 0d):** where SCRIP disagrees or hangs, the driver is **checked in red** and named.

`corpus/programs/gimpel/DRIVER-MANIFEST.tsv` classifies all 145 modules into 6 batches of ~25, **self-contained first** (68) then include-bearing (77, which can additionally trip `lon-include-root`), carrying per module the `DEFINE`'d function names, includes, `END` presence, and the contract line. Census: 103 modules define 1 function, 15 define 2, 11 define 3, 3 define 4, one defines 8, 10 define none — **~186 functions**; 9 already carry an `END`.

## 3. ⭐ IT WORKS, AND IT FOUND TWO DEFECTS ON THE SECOND MODULE TRIED

**`BASE10_driver` — GREEN exemplar.** Self-contained, 1 `DEFINE`. Oracle and SCRIP byte-agree: `255 / 10 / 511 / 1295 / 0` for bases 16/2/8/36/10.

**`BLANKS` — TWO independent defects.** The hardest common shape: `-INCLUDE "DIFF.sno"`, 2 `DEFINE`s, recursive `FBAL = ARBNO(ITEM2 FENCE)` reached through `*FBAL`, and `LEN(*DIFF(N,' '))` — a **deferred call with args inside `LEN`**.

| call | oracle (`sbl -b`) | SCRIP m3 | verdict |
|---|---|---|---|
| `BLANKS('X = A')` | `X=A` | **`X = A`** | **silent wrong answer** — blanks not removed |
| `BLANKS('IF( A .EQ. B ) GO TO 10')` | `IF(A.EQ.B)GOTO10` | **hang >60s** | **non-termination** |
| `BLANKS('X = A + B')` | `X=A+B` | (hang, same driver) | |

⛔ **BOTH ARE PRE-EXISTING AND NOT s183's DOING** — `SCRIP_RTSEQ_RESUME=0` reproduces the wrong answer verbatim, so the RT-CARRIER rung is not implicated. Checked in: `BLANKS_driver` (red, the hang) and `probe/gimpel/gim_blanks_min_wrong` (the minimal wrong-answer witness, directory-self-contained with `BLANKS.sno` + `DIFF.sno` copied in, the `ca18508f` precedent).

## 4. ⭐⭐ THE STRATEGIC POINT — WORTH MORE THAN THE META POINTS

`BLANKS` is built from **recursive ARBNO through a defer, FENCE inside ARBNO, and a deferred call with args**. That is **the same family as beauty's grammar** (`X4 = nInc() *Expr5 FENCE(*White *X4 | epsilon)`), which is the M1 wall's own territory.

So gimpel is a **second, independent source of witnesses for the M1 class** — 145 programs written in the 1970s by someone with no knowledge of SCRIP, exercising exactly the constructs beauty exercises, with a live oracle for every one. Witnesses minted *for* a bug can accidentally encode the theory of the bug; these cannot. Any minimal witness distilled from a batch belongs in `corpus/probe/gimpel/`.

## 5. WHAT THIS ROW IS NOT

⛔ **Not a weights change.** Whether and how the gimpel suite is weighted in `scorecard_snobol4.sh` is **Lon's knob** (GOAL-SNOBOL4-100 § THE INSTRUMENT). `gimpel-suite-harness` changes only *which rows the suite enumerates* — drivers instead of library modules — and records the META delta; it does not touch a weight.
