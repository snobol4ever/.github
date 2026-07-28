# FINDING 2026-07-27l — RTX-3b SURVIVED, REVALIDATED ON CURRENT MAIN, AND THREE RECORDED BOARD CLAIMS ALL DISAGREED WITH MEASUREMENT

**Session:** s200 · **Goal:** `GOAL-SNOBOL4-RTX.md` · **Branch:** SCRIP `rtx-3b-s200`
**Predecessors:** s199 (`FINDING-2026-07-27k-...RECONSTRUCTED-AFTER-SANDBOX-LOSS...`), s190 (lost), s188 (RTX-0b instrument)

---

## 1. HEADLINE — THE WORK WAS NOT LOST, AND THE CURSOR SAYING IT MIGHT BE WAS WRONG IN THE SAFE DIRECTION

s199's LIVE CURSOR read **"ON BRANCH `rtx-3b-s199` — PUSH PENDING A CREDENTIAL"** and **"NOT PUSHED — credential needed. DO NOT REPEAT s190: push the branch."**

**Measured first act of this session:** `git ls-remote --heads origin` shows
`1f0e53ccf41be34f5e324a0a2448065f9e1ffbea refs/heads/rtx-3b-s199`.
Both commits are on origin. `c5ee5f0b` is a valid object. `rtx_str.S` on that branch carries **9 `SNUL` references** — s190's diagnostic tell for the *lost* port was **zero**.

⭐ **THIS IS RULES.md (a)-CLASS ROT, CAUGHT IN THE ACT, AND IT IS THE FIFTH INDEPENDENT CONFIRMATION OF THE RULE.**
RULES.md line 98(a): *"NEVER WRITE PUSH STATUS INTO A DOC. A 'PUSH PENDING' banner is a claim about an event that occurs AFTER the text is frozen into the commit — it is structurally incapable of being true."*
s199 wrote the banner, then evidently obtained the credential and pushed, and the banner was never corrected because nobody edits a committed session-state block. **The doc was frozen mid-fact.**

⚠ **THE ASYMMETRY WORTH NAMING:** this failure mode is not symmetric in cost.
- A stale **"pushed"** claim loses work (s190 — the code died with its sandbox).
- A stale **"not pushed"** claim costs only a re-verification (s200 — two minutes).

s199 erred toward the safe side *by accident of ordering*, not by design. **The rule stands unchanged: `handoff_status.sh` and `git ls-remote` are the only truth. But note that when the banner must be wrong, "understated" is the cheaper direction to be wrong in.**

---

## 2. THREE RECORDED BOARD CLAIMS, THREE DIFFERENT NUMBERS, NONE MATCHING MEASUREMENT

| source | claim | kind |
|---|---|---|
| `GOAL-SNOBOL4-RTX.md` LIVE CURSOR (s199) | **221/94** | frozen session state |
| SCRIP `main` HEAD `8d0665c8` commit msg (FLATDISP-8, s197) | **SNOBOL4 221/219 → 295/294** | frozen commit message |
| **MEASURED s200, `scripts/test_crosscheck_snobol4.sh`, main @ `8d0665c8`** | **m3 268/47 · m4 267/46 · DIVERGE=2** | ground truth |

Suite total is **315** in every case (268+47), so these are the same suite and are directly comparable — the disagreement is real, not a units mismatch.

⭐ **THE GENERALIZATION, AND IT IS BROADER THAN THE PUSH-STATUS RULE:** the push-status rule (a) covers claims about events *after* text freeze. This finding shows the **same rot afflicts claims about events BEFORE freeze** — a board number measured at commit time, in a *different sandbox, under a different parallel-session tree state*. FLATDISP-8's 295/294 was presumably true where it was measured. It is not true here. **A board number is a measurement, and a measurement without its environment is not a fact — it is an anecdote.**

⛔ **CONSEQUENT RULE PROPOSED FOR `RULES.md`: A BOARD NUMBER IN PROSE IS A CLAIM ABOUT A TREE STATE THAT NO LONGER EXISTS. RE-PROVE THE WATERMARK LIVE AT SESSION START — ARCH §7 ALREADY SAYS THIS, AND THIS SESSION IS THE THIRD TIME IT PAID.** Do not gate against, or panic about, a number read from a document. Three sessions in a row (s187, s188, s200) re-proved and found something different from what was written.

---

## 3. RTX IS MECHANICALLY RULED OUT OF THE 47 FAILURES — RE-PROVEN, NOT INHERITED

s199 asserted RTX was not the cause. **This session re-measured it rather than trusting the assertion.**

Gates enumerated from the tree, not from prose (`src/runtime/rtx/rtx_init.c:10`): `SCRIP_RTX_MISC`, `SCRIP_RTX_ALLOC`, `SCRIP_RTX_STR`, `SCRIP_RTX_CALL` — **four**, all default ON.

| arm | board |
|---|---|
| all gates default ON | m3 268/47 · m4 267/46 · DIVERGE=2 |
| all four gates forced OFF | m3 268/47 · m4 267/46 · DIVERGE=2 |
| **failure-set diff** | **byte-identical** |

⭐ **This is simultaneously the kill-switch proof for the whole RTX surface** — ON == OFF over all 315 programs, obtained free as a by-product. The 47 failures are overwhelmingly `*_pat_*` (pattern family) and belong to the parallel ζ session's in-flight work.

---

## 4. RTX-3b REVALIDATED ON CURRENT MAIN — THE PORT IS BASE-INDEPENDENT

The two s199 commits cherry-picked cleanly onto `origin/main` (3 commits ahead of the branch's base), **zero conflicts** → branch `rtx-3b-s200` (`6154217c`, `5893d173`).

| gate | result |
|---|---|
| build (`scrip` + `libscrip_rt.so`) | clean |
| crosscheck vs s200 baseline | **failure set byte-identical — zero regression** |
| RTX unit | 21/21, 0 mismatches |
| RTX alloc unit | 36/36, 0 mismatches |
| RTX-3 STR differential battery | **8426 cases, 0 mismatches** |

**FALSIFICATION PROBE RUN, NOT INHERITED** (the ladder's standing discipline). Inverting the a-arm SNUL test (`jne .Lsc_nb` → `je`) at `rtx_str.S:247`, rebuilding, and re-running: **8426 cases → 22 mismatches, `RTX STR UNIT: FAIL`**, with named mismatches on `FAIL + SNUL (FAIL wins)` and `FAIL left`. Restored; battery green again; `git diff` empty. **The battery is a live instrument, and the asm demonstrably executes.**

### MEASUREMENT — THE EFFECT REPRODUCES ON A THIRD BASE IN A THIRD LOAD WINDOW

`scripts/bench_sno_rtx.sh STR`, RT_OPT=-O0, mode 3, R=5 interleaved medians, gate A/B on ONE binary, ON/OFF output byte-identity enforced by the harness:

| program | s199 (old base) | **s200 (current main)** |
|---|---|---|
| `var_access` | 1.391× / 1.396× | **1.366×** |
| `func_call` | 1.089× | **1.080×** |

⭐ **THE POINT IS NOT THE RATIO, IT IS THE INVARIANCE.** Both numbers land slightly below s199's and well outside the ±3% null floor (AGG null control, s188: 1.036 / 1.003). Three bases, three load windows, same effect ⇒ **the win is a property of the port, not of the tree it was developed against.** s199 established the ratio held across load; s200 establishes it holds across *base*.

---

## 5. ⭐ DEBT DISCHARGED — `string_pattern` NON-REGRESSION, BY CORRECT CLASSIFICATION RATHER THAN BY MEASUREMENT

s199 recorded: *"STILL OWED: `string_pattern` non-regression from 2.016× **UNDISCHARGED** — segfaults under BOTH arms including `SCRIP_RTX_STR=0`. Pre-existing, pattern-family. Not waived."*

s199's evidence was gate-based (gate OFF still segfaults). **That is strong but not airtight: "gate off" is not the same as "commits absent."** This session closed the gap:

| arm | rc |
|---|---|
| branch, all four RTX gates OFF | 139 (segv) |
| branch, all gates ON | 139 (segv) |
| **pristine `origin/main`, RTX-3b commits ABSENT ENTIRELY, rebuilt from scratch** | **139 (segv)** |

⭐ **DISCHARGED.** The fault reproduces with the commits not in the tree at all. It cannot be an RTX-3b regression, and **RTX-3b is not blocked on it.** It remains an open pattern-family fault owned by the ζ ladder.

⭐⭐ **THE METHODOLOGICAL POINT, AND IT GENERALIZES BEYOND THIS DEBT: A KILL-SWITCH IS NOT AN ABLATION.** A gate proves the *body* is bypassed. It does not prove the *commit* is inert — the same commit may also touch headers, `.inc` files, build inputs, or symbol visibility that a runtime gate cannot switch off (RTX-3b touches `rtx_abi.inc`). **To attribute or exonerate a fault, remove the commits and rebuild. The gate is the cheap screen; the pristine rebuild is the proof.** This is the same shape as s165's rule that an unmoved battery is not evidence — an unmoved *gate* is not evidence either, when the commit's footprint exceeds the gate's reach.

---

## 6. STATE AT HANDOFF

- **SCRIP branch `rtx-3b-s200`** = `origin/main` + the two revalidated RTX-3b commits. Gates green, zero regression, tree clean.
- **`rtx-3b-s199` remains on origin**, unmerged, 3 behind main. `rtx-3b-s200` supersedes it.
- **Baseline of record for the next RTX rung: m3 268/47 · m4 267/46 · DIVERGE=2**, invariant under all four RTX gates. ⚠ Re-prove it live; do not inherit it from this document — that is the whole point of §2.
- **NEXT: RTX-5 (AGG).** Step 0(a)(b)(c)(d) already done in the rung — do not re-derive. Carries an **unresolved fork needing Lon's ruling** (integer-key `tbl_key_str` stringify → `_tbl_hash` → `strcmp` → per-subscript `rt_agg_alloc`): (i) port as-is for `-O0` ceremony only, (ii) promote the table-LAYOUT rung ahead of it, or (iii) the layout-preserving middle path — fuse itoa+hash in one pass.
- ⚠ **CONCURRENCY:** `rt_subscript_var` lives in `pattern_match.c`, which is the ζ ladder's active territory *and* the home of the 47 current failures. Check the other session's cursor before starting RTX-5.
- **SPITBOL manual v3.7 read for this session's constructs:** p.22 (type-preserving null concatenation — verified verbatim against the port's own comment block, they agree); Ch.7 pp.88–93 (Arrays and Tables) for the upcoming AGG rung — bounded integer array subscripts with out-of-bounds *failure* semantics, vs. unbounded any-datatype table keys, table initial-value/initial-size args, and CONVERT table↔array ordering by time-of-entry.
