# FINDING s234 (2026-08-01) — THE TAG-3 EVAL BLOCKER IS THE γ **SUCCESS** CODE, NOT THE ω **FAIL** CODE. TWO SESSIONS SEARCHED THE RIGHT FILE AND THE WRONG LINE.

**Rung:** SNOBOL4-RTX / TAG-3 (`GOAL-SNOBOL4-RTX.md`). **Result:** renumber LANDED ON MAIN, watermark EXACT HOLD, blocker closed.
**SCRIP `5ddd5738`** (source) + `026f1cb5` (feature `.s`) · **corpus `2b2f0ab9`** (benchmarks) + `92a882e4` (demos).

---

## 1. THE HEADLINE

`bb_glue_flat.cpp`'s **γ landing** wrote the chain's **SUCCESS** status as a hardcoded `1` — old `DT_S` —
inside an `IF(MEDIUM_BINARY, ...)` block. After the renumber `DT_S == 2`, so a **succeeding**
runtime-compiled chain returned tag `1`, which is not a valid tag under the new layout, and
`eval_chain_run_capture` read `ZZEVALZZ` back as the null string.

**s233 symbolized the ω line (`:92`, the FAIL code) and left γ (`:83`) alone.** EVAL *succeeds*, so only
γ ever fired. That is the whole reason s233's five converging corroborations "did not survive one build":
the file was right, the class was right, the **line** was wrong — and the line they picked is on a path the
failing program never takes.

⭐ **THIS ALSO EXPLAINS THE ASYMMETRY NOBODY EXPLAINED FOR THREE SESSIONS: the defect was m3-only while m4
held EXACTLY.** In TEXT medium γ/ω call `exit(0)`/`exit(1)` and touch **no tag at all**; only
`MEDIUM_BINARY` carries a tag-shaped status code. An m3-only symptom was a *structural consequence*, not a
coincidence, and it was readable from the template the entire time.

⇒ **RULE: WHEN A DEFECT IS MODE-ASYMMETRIC, GREP THE `IF(MEDIUM_*)` BLOCKS FIRST.** The set of things that
can differ between m3 and m4 is small, enumerable, and one grep wide.

⇒ **RULE: A STATUS CODE THAT HAPPENS TO EQUAL A TAG IS A TAG.** γ/ω's `1`/`99` were documented in-file as a
protocol ("1 = the chain succeeded, 99 = it failed") — which reads as *not a tag* and is exactly why two
sessions walked past it. The chain's type is `DESCR_t (*)(void*, int)`; `eax` **is** the returned `v` field.
Prose calling it a protocol code did not stop it from being a descriptor tag.

## 2. IT IS NOT A MERGE DEFECT — REPRODUCED FROM A CLEAN RE-APPLICATION

s232/s233 both framed this as "the merge breaks a program neither parent breaks" and spent their budget on
merge archaeology (auto-merged `bb_call_fn.cpp`, main's WIREREG surgery, `xa_flat.cpp` conflict resolution).
Re-applying the change set **directly onto main**, no merge involved, reproduces **the identical two-program
regression** (`1016_eval` + `161_pat_defer_fn_nested_match`, zero removed).

⇒ **THE 50-COMMIT MERGE WAS NEVER THE CAUSE, AND THE MERGE-SHAPED FRAMING IS WHAT KEPT IT ALIVE.** When a
change breaks only under a merge, the cheapest disambiguation is to re-apply the change set to the target
branch and see whether the merge was ever load-bearing. Two sessions never ran that experiment.

## 3. THE NARROWING s233 MISSED, AND IT IS ONE PROBE WIDE

s233 recorded the blast radius as "**the whole deferred-eval family**" — every `EVAL(*expr)` form.
**`EVAL` of a plain STRING fails identically** (`EVAL('2 + 3')`, `EVAL('x')`). The family is not
deferred-expression handling at all; it is **every runtime-compiled chain**. And the chain **executes**:
a `DEFINE`d function called through `EVAL` prints its side effect and returns correctly — only the value
fails to land. "Deferred eval is broken" and "the chain's result never lands" point at different code.

## 4. TWO UNSYMBOLIZED SITES THE BRANCH MISSED

- **`bb_call_fn.cpp:197,200` — `cmp64 rax, 6`, a PACKED tag+slen compare** (tag = low dword, slen = high).
  The branch symbolized the 32-bit `cmp ecx,6` two lines above and missed this one. **Fourth instance of the
  s230 invisible-packed-literal class**, after `rtx_icnsub.S`'s `mov rax,0x200000009`. The class is not
  closed by `descr_tags.inc`: that header stops *asm* hand-encoding, and this one is in a **C++ template**.
- **`bb_call.cpp:451,453` — `mov32 edi,6` / `edi,1`**, `DT_I`/`DT_S` mints for `rt_is_truthy`, **added by
  MAIN after the branch was cut**. s232's absent-hazard audit read 27 commits as clean; main is now 50 past
  merge-base and these are live. ⇒ **AN AUDIT HAS AN EXPIRY DATE MEASURED IN COMMITS.**

## 5. GATES — ALL MEASURED THIS SESSION, NOTHING INHERITED

**BASELINE re-proven on main `afbcab9b`, N=4, `setarch -R`, byte-reproducible across all four runs:**
`m3 295/22/0 · m4 280/35/2 · DIVERGE 16 · fail-set md5 ac8908de8333d6a2f9879b86a2032e18`
⚠ s233's `294/23/0 · DIVERGE 17` is STALE (main moved 2 commits). Not quoted.

**AFTER: identical on all four counts, fail-set md5 BYTE-IDENTICAL, N=4. EXACT HOLD.**
tag layout gate **13/13 PASS** (incl. `descr.h` ↔ `descr_tags.inc` cross-check and the `.S` sweep) ·
RTX unit **ALL PASS 8426/0** · store-width **GATE PASS** · `.s` regen ×3 RUN.
Prolog `0/4/185` and Icon `4/0/0` both sides, artifacts swapped to measure pristine.
⚠ **POPULATION IN THE SAME SENTENCE (s224 rule): Prolog is 185/189 SKIP and Icon is 4 programs — both are
weak evidence for THIS change, not confirmation.** Stated, not omitted.

**NO SPEED NUMBER CLAIMED.** Correctness/eradication rung; the 3-arm rail was deliberately not run.

## 6. TWO PRE-EXISTING MAIN DEFECTS, NEITHER CAUSED NOR FIXED HERE

1. **Deferred ARITH `*(n + 3)` SEGVs in m3** — on pristine main, before any change.
2. ⭐⭐ **m4 EVAL IS SILENTLY EMPTY.** `1016_eval` produces **no output at all** in m4 on pristine main
   (rc=0), while hello-world compiles and runs. It sits in `FAIL(m4)` **and** `DIVERGE` at baseline.
   **This may well be what s233 was actually chasing through the merge** — an m4 EVAL failure that predates
   the branch entirely. Own rung; Lon's routing.

## 7. INSTRUMENT NOTES

- ⛔ **BACKGROUNDED BUILDS DO NOT SURVIVE A TOOL-CALL BOUNDARY IN THIS CONTAINER.** A `nohup ... &` build died
  silently at 43/253 objects and its log simply stopped; nothing reported failure. **`setsid` survives.**
  Add to the ENVIRONMENT FACTS block — a half-built tree that reports nothing is the worst kind of null.
- ⚠ **`test_crosscheck_prolog.sh` HARDCODES `SCRIP="${HERE}/../scrip"`** and ignores a `SCRIP=` env override,
  so an A/B "measured" that way silently compares a binary against ITSELF. Swap the artifacts on disk
  instead. (Caught here before it produced a false hold — the s223 hand-rolled-invocation class.)
- ⚠ **The `NV_SET_fn`/`NV_GET_fn` LD_PRELOAD interposer sees only PLT-routed calls**; the chain's own store
  is internal to `libscrip_rt` and never appears. A zero from it is not evidence of a lost store.
