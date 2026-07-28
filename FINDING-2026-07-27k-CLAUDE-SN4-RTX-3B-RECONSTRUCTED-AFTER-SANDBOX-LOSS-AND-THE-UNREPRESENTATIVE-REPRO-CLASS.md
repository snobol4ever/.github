# FINDING 2026-07-27k — RTX-3b RECONSTRUCTED AFTER SANDBOX LOSS; THE UNREPRESENTATIVE-REPRO CLASS; MEASUREMENT RELIABILITY ON A 1-CORE BOX

**Session s199. SCRIP branch `rtx-3b-s199` — `c5ee5f0b` (port) + `1f0e53cc` (asserts + measurement).**
**`handoff_status.sh` is the push truth — not this block.**

---

## 1. ⛔ RTX-3b WAS LOST. THE RULE THAT PREDICTED IT WAS ALREADY WRITTEN.

s190 landed RTX-3b on branch `rtx-3b-s190`, commit `a5ff0a9d`, **local only**, reasoning that
*"pushing onto a 185/130 tree would bury the port in someone else's breakage."* The sandbox died
and took the port with it. Measured s199 at a fresh clone: `git cat-file -t a5ff0a9d` → **not a
valid object**; no such branch on origin; `rtx_str.S` contains **zero** `SNUL` references.

RULES.md line 54 already says it verbatim: *a local commit is NOT a handoff; the bytes are on this
disposable sandbox and vanish with it.*

⭐ **THE TRADEOFF WAS FALSE.** A **branch** push cannot pollute `main`. The choice was never
"pollute the tree vs. keep it clean" — it was "persist the work vs. lose it." **Push the branch;
let the human merge.**

⚠ **AND THE PROSE SURVIVED WHILE THE CODE DID NOT.** The s190 FINDING reached `.github` and says
**LANDED**; the tree says otherwise. An orientation that trusts the FINDING is wrong in the most
expensive direction — it believes work exists. This is the (a)-class rot of RULES.md's
STALE-ORIENTATION rule, with a new twist: **the doc and the code have different durability, so a
doc asserting a code state is a claim it structurally cannot keep.** Cross-check the tree.

⭐ **RECOVERY WAS CHEAP BECAUSE THE RUNG CARRIED THE SPEC.** Guard order, return convention and the
exact `mov` sequences were all in `GOAL-SNOBOL4-RTX.md`. Reconstruction, not re-derivation — well
under an hour. **A rung written to that level of detail is itself a backup.**

## 2. ⭐⭐ THE UNREPRESENTATIVE REPRO — A NEW MEMBER OF THE VACUITY FAMILY

The port was verified against a hand-written program exercising the manual's own p.22 example.
**All three arms agreed — SPITBOL oracle, RTX ON, RTX OFF — and the agreement was worthless.**
Inverting the port changed *nothing*, because the test never reached it.

**ROOT CAUSE:** the source literal `''` arrives at `str_concat_d` as **`DT_S` with `slen==0`**, not
`DT_SNUL`. `IS_NULL_fn` catches it on its *second* arm — the one the rung explicitly says not to
implement. The `DT_SNUL` arm is produced by *runtime* nulls, never by a source literal.

⛔ **THE TELL:** a passing test whose output is identical to the feature being absent. s187's probe
rule catches it — *state what the output would look like if the thing under test did not exist; if
that equals the passing output, the probe is vacuous* — but only if the rule is applied to
**hand-written repros**, not just to falsification builds. **FOURTH MEMBER:** s184 (failed compile
scored clean) · s186 (zero bytes passing vacuously) · s187 (a break that is a no-op at its site) ·
**s199 (a repro that never reaches the code it tests).**

⭐ **STANDING RULE:** a hand-written repro is a HYPOTHESIS about which code path runs. **Confirm the
path with a counter before trusting agreement.** The `LD_PRELOAD` interposer costs two minutes and
settled it immediately.

## 3. ✅ RELEVANCE MEASURED — AND THE RUNG'S PREMISE HELD WHERE IT COUNTS

`LD_PRELOAD` tag census (ARCH §7 step 0d) over the four STR benchmarks:

| program | `str_concat_d` calls | dominant shape |
|---|---|---|
| `var_access` | 10,000,000 | `DT_SNUL + DT_I` |
| `func_call` | 10,000,000 | `DT_SNUL + DT_I` |
| `string_manip` | 5,000,000 | `DT_SNUL + DT_I` |
| `table_access` | 5,006,000 | `DT_SNUL + DT_I` |

The rung's claim — *all measured calls are plain `DT_SNUL`* — is **correct for the benchmarks** and
**false for a source literal**. Both facts are needed: the first justifies the rung, the second
explains why the obvious repro proves nothing.

⭐ The idiom is `var_access.sno:18` — `N = LT(N, 10000000) N + 1`. `LT` returns null on success,
concatenated with `N + 1`. **The manual's p.22 exception is load-bearing: it keeps `N` an INTEGER
instead of degrading it to a string**, which is exactly why the rule exists.

## 4. ✅ THE PORT, AND WHAT IT COST

`DT_SNUL` arm only, in `str_concat_d`'s fast path, guard order equivalent to `c_str_concat_d`
(`!g_gc_pending` → neither `DT_P`/`DT_X` → neither `DT_FAIL` → the null arms). **13 instructions to
`ret`.**

⭐ **HALF THE COMPARES, SAME CONDITION SET.** The `DT_SNUL` test is hoisted above the `DT_P`/`DT_X`/
`DT_FAIL` guards **in the a-arm only**, because `a.v == DT_SNUL(0)` already proves `a` is not
`DT_P(3)`, `DT_X(15)` or `DT_FAIL(99)` — so only the *other* operand still needs guarding.

⛔ **THE b-ARM NEEDS AN EXTRA GUARD THE a-ARM DOES NOT.** Reaching "return a" requires
`IS_NULL_fn(a)` to be **false**, and `a` may be `DT_S` with `slen==0` — null by the second arm.
Returning `a` there would hand back `DT_S`-empty where C returns `b`. That shape routes to C
explicitly rather than dereferencing `a.s` in asm (the RTX-3 LENGTH-UNKNOWN trap).

**`DT_X` was absent from `rtx_abi.inc` entirely** — not "documented but undefined" as s190 recorded;
it appears nowhere in the file. Added.

## 5. ⚠⚠ MEASUREMENT RELIABILITY — THIS CONTAINER IS `nproc=1`

**RELIABLE (reproduced in two independent load windows):**

| program | ON | OFF | ratio |
|---|---|---|---|
| `var_access` | 1229 ms | 1709 ms | **1.391×** |
| `var_access` (re-run, noisier window) | 1360 ms | 1899 ms | **1.396×** |
| `func_call` | 8588 ms | 9356 ms | **1.089×** |

Absolute times drifted ~10% with load; **the ratio held.** Within-config spread 2–5%.
`RT_OPT=-O0`, mode 3, N ×4 to clear RTX-0b's 800 ms floor, output byte-identical ex-timing.

**⛔ NOT RELIABLY MEASURABLE HERE:** `string_manip` and `table_access` swing **4× run-to-run on
identical config** (`table_access` ON: 2395, 5925, 10608) and the two arms visibly **swap ranking
mid-series**. Min-statistic (robust under contention — interference only adds time) puts
`string_manip` at ~1.098×, but **the variance exceeds the effect. NO CLAIM IS MADE.**

⭐ **THE CONTROL IS WHAT MAKES THIS SAYABLE:** `var_access` was re-measured *in the same noisy
window* where `string_manip` went wild, and came back tight at 1.396×. **Instability is a property
of the PROGRAM here, not of the moment** — so "the box was noisy" cannot be used to wave away a
result, and a tight ratio in a noisy window is still evidence.

**CANDIDATE, EXPLICITLY NOT A CAUSE, FOR s188's OPEN ITEM.** s188 measured `string_manip` at 1.279×
under the STR gate, called the sign wrong, and suspected the RTX-3 SXT rework. s199 finds
`string_manip` is simply unstable to time on this box. That is a **simpler candidate than a
mechanism — and it is NOT established.** s188's number came from `bench_sno_rtx.sh` R=3 medians.
**Re-run the proper harness in a quiet window before crediting either explanation.**

## 6. ✅ THE BATTERY WAS BLIND TO THE SHAPE IT EXISTS TO TEST

8404 → **8426 cases, 0 mismatches**. s190 was right: `SNUL+S`, `S+SNUL`, `SNUL+SNUL` and `I+SNUL`
were all present, so **symmetry made `SNUL+I` — the idiom's own shape, 10M calls — look covered.**
Added it plus guard-precedence cases (`SNUL+FAIL` both orders, `slen0`, CSET).
⭐ **PROVEN LIVE:** inverting the a-arm turns the battery **RED** on `"SNUL + int (THE idiom)"`.

Same treatment for the new `_Static_assert`s: flipping `DT_X` to 14 **fails the build**; restored,
green. **Every instrument added this session was itself falsified before being trusted.**

## 7. ⛔ BOARD IS NOT THE WATERMARK — AND IT IS NOT RTX

**m3 221/94 · m4 219/94 · DIVERGE=1** (`W06_tab`), against s188's documented 314/1 · 312/1 · 0.
**93 pattern-family programs down.**

**RTX ruled out mechanically:** the board is **identical with every RTX gate off**
(`SCRIP_RTX_{MISC,ALLOC,STR,CALL}=0`) and identical before and after this session's port.
Failures are `*_pat_*` / capture / fence / arbno — consistent with the parallel ζ session's s198
stored-pattern segv (`bb_match_release` RSP cross-box read, fix-attempt reverted).

✅ **s190's blocker is FIXED and is a DIFFERENT fault:** its 4-line repro (`DEFINE('f(x)')`, every
dummy argument arriving null) now returns 6 and 99 correctly.

**⛔ STILL OWED:** `string_pattern` non-regression from 2.016× is **UNDISCHARGED**. It segfaults
under **both** arms including `SCRIP_RTX_STR=0`, which never enters the asm — pre-existing,
pattern-family, same class as the 93-program hole. Not waived.

## 8. GATES

crosscheck m3 221/94 · m4 219/94 · DIVERGE=1 (== pre-port baseline, == all-gates-off) ·
RTX unit 21/21 · alloc 36/36 · STR 8426/0 · smokes PASS=2 FAIL=0 · SPITBOL oracle agrees on the
p.22 example · ON==OFF byte-identical ex-timing on all four STR benchmarks.
Phase-1 rung: **zero templates touched, no `.s` regen owed by construction.**
