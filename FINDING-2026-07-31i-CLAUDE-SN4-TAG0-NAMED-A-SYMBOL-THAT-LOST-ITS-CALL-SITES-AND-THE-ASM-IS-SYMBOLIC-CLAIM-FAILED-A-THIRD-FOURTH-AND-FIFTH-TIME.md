# FINDING-2026-07-31i — TAG-0 NAMED A SYMBOL THAT HAD LOST ITS CALL SITES, AND "THE ASM IS SYMBOLIC" FAILED A THIRD, FOURTH AND FIFTH TIME

**Session s230 (2026-07-31). SCRIP `dfb6fc87` (branch `tag-renumber-s229`) + corpus `ae13c424`, `49eb1462`. NOT ON MAIN. NOT PUSHED.**

## 1. ⭐⭐ TAG-0 IS DISCHARGED AND IT FALSIFIES ITS OWN STOP CONDITION

`GOAL-DESCR-TAG-ENCODING.md` §7 mandates: run 0(d) on the arith benchmarks; **if the dispatcher is not entered, STOP — the rung optimises a bypassed path.** Measured, `LD_PRELOAD` interposer, `util_rtx_count_syms.sh`:

| symbol | arith_int | arith_loop | arith_mixed | same program, N=500k → 1M |
|---|---|---|---|---|
| `rt_num_arith` — **the symbol §7 names** | **0** | **0** | **0** | 0 → 0 |
| `rt_add` | 100,000,000 | 1,000,000 | 80,000,001 | **exactly 2.00×** |
| `rt_cmp_d` | 100,000,000 | 1,000,000 | 40,000,001 | **exactly 2.00×** |
| `c_rt_add` (C fallback) | 0 | 0 | 0 | zero bails ⇒ asm handles 100% |

**The dispatcher IS cold — s203 reproduces exactly. And the STOP is WRONG.** The BOTH-INT predicate did not die when the dispatcher went cold; it **migrated** into `rt_add`/`rt_cmp_d`, which are already asm and literally execute

```
cmp edi, DT_I ; jne … ; cmp edx, DT_I ; jne …      (rtx_arith.S:182, and rt_cmp_d:59)
```

— the exact 2-compare-2-branch shape the renumber collapses to `and edi,edx ; cmp edi,DT_I` — roughly 200M times inside a 1353 ms window.

⭐ **THIS IS THE RTX-7 "BYPASSED FAMILY" CLASS INVERTED, AND IT IS THE DANGEROUS DIRECTION.** RTX-7's premise decayed because an unrelated rung (GVA slots) *removed* the call sites, and the symptom was a wasted port — which announces itself. Here the call sites **moved to a symbol the gate did not name**, and the symptom is a **FALSE STOP**: a correct, hot rung is abandoned and nothing ever says so. Same asymmetry s226 recorded for static-vs-dynamic ranking: a false positive is loud, a false negative is silent.
⇒ **RULE: A 0(d) GATE MUST NAME THE PREDICATE, NOT A FUNCTION.** Ask "where is this test executed", never "is this function called". §7 and the TAG-4 rung re-aimed at `rtx_arith.S`.

## 2. ⛔ THE BRANCH COULD NOT BUILD, AND ITS OWN GATE COULD NOT SEE THAT

`descr.h` used `_Static_assert` — **C11, not a C++ keyword** — and `descr.h` is included by the C++ template TUs (`-std=c++17`). The s229 FINDING's "✅ 11 `_Static_assert`s compile clean" exercised a **C** TU only. Now `DESCR_SASSERT` (`#ifdef __cplusplus`).
⚠ Same shape as the s225 fabricated-gate lesson one level down: the gate was *run*, it was simply **narrower than the claim it was used to support**.

## 3. ⭐⭐ "THE ASM IS SYMBOLIC / NO HAND-EDITED IMMEDIATES" HAS NOW FAILED FIVE TIMES, AND THE CAUSE IS STRUCTURAL

`GOAL-DESCR-TAG-ENCODING.md` §5 asserts it. s229 falsified it twice (`rtx_arith.S` range trick, `rtx_match.S` literals 99/1) and **fixed the instances, leaving the class open.** The class immediately produced three more:

| file | shape | why it escaped |
|---|---|---|
| `rt/rt_asm_helpers.S` | `$9` (DT_N) `$99` (DT_FAIL) `$6` (DT_I) | AT&T — **cannot** include `rtx_abi.inc` |
| `rtx/rtx_icnsub.S` | **5×** `mov rax, 0x200000009` | tag **fused inside a packed 64-bit literal** |
| 6 template files | 32 sites baking old `DT_FAIL` 99 | vs **36 already-symbolic** sites in the same files |

⭐⭐ **THE PACKED LITERAL IS THE WORST VARIANT AND EXPLAINS THE WHOLE HISTORY.** `0x200000009` is `(slen 2 << 32) | DT_N`. The tag is not an immediate a reader or a grep recognises — it is a **nibble inside a constant**. No pattern for "a bare tag literal" can see it.
⭐⭐ **AND THE ROOT CAUSE IS NOT CARELESSNESS.** `rt_asm_helpers.S` and `rtx_icnsub.S` are AT&T syntax; `rtx_abi.inc` opens with `.intel_syntax noprefix`, so **including it was impossible and hand-encoding was the only option available.** Editing instances could never have closed this.
⇒ **FIX THE CLASS: new `src/contracts/descr_tags.inc` — pure `#define`, no syntax directive, no C construct, includable from Intel asm, AT&T asm and C alike**, plus `DT_NAMETRAP_LO` so the packed form cannot be re-fused. `rtx_abi.inc` now includes it rather than carrying copies.

## 4. ⚠ THE EMITTER IS HALF-CONVERTED, AND ONE HALF IS A LANGUAGE THE SNOBOL4 BATTERY CANNOT SEE

32 hardcoded vs 36 symbolic `DT_FAIL` sites in the same directories. Worse, `bb_call_fn.cpp`'s **Prolog** unify arm baked old `DT_PLVAR` 13 / `DT_PLREF` 14 / `DT_I` 6 / `DT_S` 1 / `DT_N` 9. A SNOBOL4-only crosscheck is **structurally blind** to it — the exact "citing an unmoved battery" trap of ARCH §7 2b.

⛔ **AND THE PROLOG BATTERY IS A FALSE GREEN FOR THAT ARM — MEASURED, NOT ASSUMED.** Falsification probe per §7 2b: the wrong literal `14` deliberately restored ⇒ **Prolog STILL 188/0**. Reading the source explains it: `bb_call_fn.cpp:513`'s `$unify` **CU** arm precedes the **SINK** arm at `:552` in one `if/else` chain, so the sink arms are **not emitted by default**.
⇒ **The Prolog tag fixes are correct BY READING and UNGATED BY MEASUREMENT.** Said plainly rather than dressed up. Anyone grading that arm must set `SCRIP_NO_CU=1` first, or they are grading dead code.

## 5. ⛔ THE WATERMARK, STATED HONESTLY — m3 EXACT, m4 NON-DETERMINISTIC

- **m3 276/41/0 — STABLE over 4 runs, fail set BYTE-IDENTICAL to baseline. EXACT HOLD.**
- **m4 OSCILLATES: 275/41/1 (DIVERGE 2) ↔ 276/40/1 (DIVERGE 3)** on `151_pat_arbno_inline_fence_backtrack`, across repeated runs of **one unchanged binary**. m3 segfaults on it deterministically 4/4.

⚠⚠ **I CANNOT ATTRIBUTE THE OSCILLATION, AND THE REASON IS MY OWN GAP: THE BASELINE WAS N=1.** Mid-session I read 276/40 once and nearly wrote it up as an improvement; later I read 275/41 once and nearly wrote it up as an exact hold. **Both were coin flips of the same underlying non-determinism** — precisely the failure the kill-switch contract predicts for N=1. ⇒ **`151` joins `160` in the QUARANTINE class**, and **no m4 number from this session may be quoted as a mover or a fix.**

## 6. WHAT IS OWED BEFORE MAIN

1. **Re-run the baseline at N≥4** and characterise `151`'s m4 hash set — the oscillation is unattributed until then.
2. **`SCRIP_NO_CU=1` Prolog run** to actually gate the unify tag fixes.
3. **Sweep the remaining old-tag literals for the small tags** (`DT_S`1 `DT_P`3 `DT_A`4 `DT_T`5 `DT_R`7 in emitter code) — 99/100 were distinctive and are done; the small ones are indistinguishable from offsets and counts by grep and need the `[reg+0]`=tag / `[reg+4]`=slen reading rule applied per site.
4. **NOT concurrency-safe with the ζ ladder** — Lon's routing (granted s230: "all your choices").

## 7. ⭐ THE READING RULE THAT MADE §3/§4 SAFE — DO NOT LOSE IT

In **both** asm files and in `bb_call_fn.cpp` the DESCR word is `[reg+0] = TAG`, `[reg+4] = SLEN`. Therefore:
- `$1` / `$2` and `cmp esi,1` / `cmp esi,2` are **SLEN discriminants** (pointer cell / nametrap) — **NEVER renumber them.**
- `cmp eax,2` at `bb_call_fn.cpp:366` is **`g_zeta_mode`, a mode flag** — not a tag.
- `mov32 edx,0/1` following a tag load is the **VALUE half** of the returned DESCR.
A blanket "replace the old tag numbers" pass corrupts all three. Every site in this session was classified by reading the register's last load, not by matching a number.
