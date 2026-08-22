# FINDING — seat1: the FENCE(P) work silently regressed plain pattern matching, and the edit that did it exists only in generated output

**Date:** 2026-08-21 · **Seat:** seat1 (`/home/claude1`, Claude Opus 5) · **Topic:** `csnobol4-clean-fork` · **Status:** MEASURED, four-way witness

Lon's s249 ruling was that the FENCE(P) work "was a disaster and is tainting the tool as an oracle." That was a judgement call. It now has a mechanical witness, an attributed commit, and a named consequence.

## 1. The witness

`corpus/crosscheck/patterns/172_pat_fail_forces_retry.sno` — a four-line program from the SPITBOL manual Ch.9 p.125. **It contains no FENCE.**

```
 'abc' ? LEN(1) $ OUTPUT FAIL   :S(Y)F(N)
```

| Binary | Output |
|---|---|
| SPITBOL `x64/bin/sbl` (reference) | `a b c failed as expected` |
| upstream 2.3.4+ + our keepers (`csnobol4-clean`) | `a b c failed as expected` |
| our snapshot at root `a509cd7`, pre-FENCE-impl | `a b c failed as expected` |
| **live oracle `/home/claude/csnobol4/snobol4`** | **`a c failed as expected`** |
| `.ref` expectation | `a b c failed as expected` |

The live oracle **drops a scanner start position**. FAIL's whole documented purpose is that, unlike ABORT, it lets the scanner advance — so the one semantic the program exists to test is the one that is wrong.

## 2. Attribution — bisected to a single commit

Nineteen commits between `a509cd7` and HEAD touch the matcher (`v311.sil`, `lib/pat.c`, generated `isnobol4.c`/`syn.c`). Each was built and run against the witness:

- `7654cda` (FENCE(P) 1-arg impl) … `a2b69e0` (session #60) — **all GOOD**
- **`723ac19` — "F-2 Step 3a session #64: TXSP write-site fix at isnobol4.c:11498; gate-neutral" — BROKEN**

The commit that declares itself *gate-neutral in its own subject line* is the one that broke it. It moved `S_L(TXSP) = D_A(YCL)` inside a new `!(D_F(PATICL) & FNC)` guard at `L_SALT2`. Before: TXSP was restored unconditionally and only the `goto L_SCIN3` was gated. After: for every FNC trap the scan cursor is no longer restored — and ordinary constructs (`$` conditional assignment, `FAIL`) travel the FNC trap path, so the blast radius was never FENCE-only.

**Why the gates missed it.** The four gates cited in that commit — `fence_function 10/10`, `fence_suite 44/4/0`, `guard5`, `beauty 42 lines` — are all FENCE-shaped or whole-program-shaped. None covers plain FAIL/scanner-retry. "Gates unchanged from baseline" was true and meant nothing. This is the `.ref`-vs-oracle false-signal class CLAUDE.md already warns about, in a new costume: **a green gate set that does not intersect the changed semantics is not evidence.**

## 3. ⛔ The load-bearing consequence: the live oracle is not reproducible from its own source

`723ac19` edited **`isnobol4.c`** — generated output — and **not `v311.sil`**, the tracked SIL source of record.

`v311.sil` at HEAD still carries the original unconditional sequence:

```
       PUTLG   TXSP,YCL		   Insert old length of head
       TESTF   PATICL,FNC,SCIN3	   Check for function
```

No commit in `a509cd7..HEAD` touches `SALT2` in `v311.sil`. Therefore **regenerating `isnobol4.c` from `v311.sil` produces a different binary than the live oracle**, and nobody would be told. The oracle currently in use is a binary whose behaviour cannot be derived from the source that is supposed to define it.

## 4. What this settles

- Lon's "it comes OUT" ruling is confirmed empirically, not just editorially. The FENCE work does not merely add a dubious feature; it **subtracts correctness from unrelated pattern matching.**
- It answers the fire-point question left blocked in `FINDING-2026-08-21-seat1-csnobol4-is-not-a-fork-...`: option **(A) re-express in `v311.sil`** is not merely the tidier choice — hand-patching generated `isnobol4.c` is the exact practice that produced this regression and hid it from source review. The monitor fire-points must go through `v311.sil` or a maintained post-generation patch, never a committed hand-edit to generated output.
- Anything that cited the live csnobol4 oracle for a SNOBOL4 pattern verdict since `723ac19` (2026-05-01) should be re-checked. `csnobol4-clean` and SPITBOL agree with each other and with the `.ref`.

## 5. Reproduction

```
cd /home/claude1/corpus/crosscheck/patterns
/home/claude1/x64/bin/sbl -b 172_pat_fail_forces_retry.sno   # a b c failed as expected
/home/claude/csnobol4/snobol4 -f 172_pat_fail_forces_retry.sno   # a c failed as expected
```

Nothing under `/home/claude/csnobol4` was modified to obtain any of this; every historical build was done in a `git worktree` that has since been removed.
