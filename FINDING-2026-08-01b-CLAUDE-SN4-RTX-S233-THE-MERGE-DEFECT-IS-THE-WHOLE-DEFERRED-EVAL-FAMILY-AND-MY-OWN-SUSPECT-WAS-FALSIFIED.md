# FINDING s233 (2026-08-01) — THE TAG-3 MERGE DEFECT IS THE ENTIRE DEFERRED-EVAL FAMILY, NOT ONE PROGRAM; AND THE ONE SUSPECT THE EVIDENCE POINTED AT WAS FALSIFIED BY MEASUREMENT

**Session: s233. NOTHING PUSHED TO SCRIP. `main` UNTOUCHED (`main == origin/main` at `eb0c08a8`, zero unpushed). The trial merge lives on a LOCAL branch `trial-merge-s233` and MUST NOT LAND.**

---

## 1. WATERMARK — RE-PROVEN AT SESSION START, N=4, SAID OUT LOUD

⛔ **s232's baseline (m3 200/117) IS STALE AND QUOTING IT WOULD REPEAT THE s228 ERROR. Main has moved 48 commits past merge-base — s232 saw 27.**

| tree | m3 | m4 | DIVERGE | N | hold |
|---|---|---|---|---|---|
| `main` @ `eb0c08a8` | **294/23/0** | **280/35/2** | **17** | 4 | EXACT, fail sets byte-identical |
| trial merge | **292/25/0** | **280/35/2** | **15** | 4 | EXACT, fail sets byte-identical |

All runs `setarch -R`. ⭐ **s231's ASLR root-cause REPRODUCES: with ASLR off, `151`/`160` are STABLE and the whole suite is byte-reproducible over 4 runs on BOTH legs. No oscillation, no quarantine needed this session.**

**GATE: FAILED.** m3 −2, m4 held EXACTLY, DIVERGE fell 17→15. ⚠ **A FALLING DIVERGE LOOKS LIKE IMPROVEMENT AND IS THE OPPOSITE** — it fell because two programs moved (m3 pass / m4 fail) → (fail / fail), leaving the DIVERGE set. Read DIVERGE only alongside the m3 set-diff.

**Set-diff, m3: ADDED `1016_eval`, `161_pat_defer_fn_nested_match`. REMOVED: NOTHING.** Pure regression. m4 fail set md5-identical across the change.

⭐⭐ **s232 REPRODUCES AND HAS GROWN: it reported ONE program. There are TWO. `161_pat_defer_fn_nested_match` was not in s232's report — it is a defer/pattern program, which is the tell (see §3).**

---

## 2. THREE INHERITED CLAIMS WERE STALE — ALL RE-DERIVED AGAINST THE TREE, NOT TRUSTED

⭐ **This is the (a)-class rot in RULES.md STALE-ORIENTATION, three times in one cursor. Every one was cheap to check and would have cost a session to inherit.**

1. ⛔ **"REPO HAZARD: a fresh clone lands on `tag-renumber-s229`, NOT `main`."** **FALSE at s233** — a fresh clone lands on `main`; `origin/HEAD -> origin/main`. The default branch was evidently flipped. **Strike this line.**
2. ⛔ **"ONE real source conflict, `xa_flat.cpp` (delete/modify, HEAD side empty)."** **The file EXISTS on main today** — it is now a CONTENT conflict, not delete/modify. The resolution still comes out the same, but by a different route: main deleted a 501-line block (CARVE-KILL) and **all 11 branch edits are `99`→`DT_FAIL` swaps INSIDE that block** (verified: `git diff --numstat` = 11/11, every changed line a tag swap). ⇒ take main's deletion, forced. **Re-derived, not inherited.**
3. ⛔ **"the hazard I audited for was measured absent (1252 lines, ZERO `DT_` refs, ZERO 99/100 literals)."** **That audit covered 27 commits. Main is now 48 ahead.** Re-run over the full delta (472 added src lines): **it FIRES.** See §4.

---

## 3. ⭐⭐ THE DEFECT IS FAR WIDER THAN THE CROSSCHECK SHOWS — THE WHOLE DEFERRED-EVAL FAMILY IS DEAD IN m3

The crosscheck reports 2 programs. **A 6-line probe shows the entire `EVAL(*expr)` family returning the null string.** `1016_eval` terminates at its FIRST failing assertion (`:(END)`), which MASKS its own assertions 2 and 3 — so the corpus under-reports the blast radius by construction.

| probe | ORACLE (`sbl`) | MERGE m3 |
|---|---|---|
| plain concat `'abc' 'def'` | `abcdef` | `abcdef` ✅ |
| `EVAL(*'abc')` | `abc` | **`` (empty)** |
| `EVAL(*q)` | `qqq` | **`` (empty)** |
| `EVAL(*('abc' 'def'))` | `abcdef` | **`` (empty)** |
| `EVAL(*(q 'X'))` | `qqqX` | **`` (empty)** |
| `EVAL(*(1 + 2))` | `3` | **`` (empty)** |

⭐ **DEFERRED CONSTRUCTION IS INTACT — ONLY DELIVERY IS BROKEN.** `DATATYPE(*expr)` = `EXPRESSION` on BOTH engines, so `*` mints and tags the object correctly (`DT_E`, 11→0x38, round-trips). The result of `EVAL` is `DATATYPE=STRING, SIZE=0`.

⭐⭐ **THAT SIGNATURE NAMES THE MECHANISM CLASS.** `eval_chain_run_capture` (`runtime_eval.c:203`) does NOT read the blob's return value at all — it saves `EVAL_TMP`, calls `rt_chain_enter(fn)`, then reads the result back out of `EVAL_TMP` via `NV_GET_fn`. **An empty STRING of size 0 is exactly what `EVAL_TMP` holds when the blob NEVER WROTE IT.** ⇒ the chain runs and its store is skipped or misrouted — a successful evaluation is taking a path that bypasses its own assignment. **It is a LOST STORE, not a corrupted value.**

⚠ **`161_pat_defer_fn_nested_match` is a DEFER program.** Both regressions sit in the defer family. This is one defect, not two.

---

## 4. ⛔⛔ MY OWN SUSPECT WAS THE BEST-EVIDENCED CANDIDATE IN THE TREE AND IT WAS FALSIFIED IN ONE BUILD

The audit of main's 48-commit delta found **exactly one** surviving stale tag literal tree-wide:

`src/templates/bb_glue_flat.cpp:92` — `IF(MEDIUM_BINARY, x86("mov32", "eax", 99) + x86("ret"))`, introduced by main AFTER the branch was cut.

**Everything lined up:**
- `99` is old `DT_FAIL`; TAG-3 moves it to `0x68` (104).
- ⭐ Under the NEW **bit-encoded** layout, `DT_CHARS_BIT = 0x02` and `99 = 0b1100011` has **bit 1 SET** ⇒ a descriptor still carrying 99 classifies as a STRING with slen 0 — **an empty string, precisely the observed symptom.**
- It is `IF(MEDIUM_BINARY, ...)` ⇒ **m3-only**, and the regression is m3-only with m4 byte-identical.
- Its own comment says the BINARY arm exists to `ret` a value **back to a C caller** in the JIT slab.

**MEASURED: swapped `99` → symbolic `DT_FAIL`, rebuilt, re-probed. ALL SIX DEFERRED FORMS STILL RETURN EMPTY. FALSIFIED.**

⭐⭐ **WHY IT WAS WRONG, AND IT IS READABLE FROM THE SOURCE:** `rt_chain_enter` (`runtime_eval.c:81`, hand-written AT&T inline asm) wires outside-γ→`rcx` and outside-ω→`rdx` to ONE shared landing and `jmp *%rax`. **It never reads the blob's return value, and the chain never reaches `bb_glue_outer_γ/ω` at all** — the outer bridge is the WHOLE-PROGRAM exit; `BB_DEFER`'s blob entry is documented (`bb_glue_flat.cpp:101`) as a consumer of the PASS-THROUGH glue, which carries no tag literal.

⛔ **THE LESSON, AND IT IS THE CURSOR'S OWN: s232 wrote "`bb_call_fn.cpp` is a SUSPECT, not a diagnosis" and deliberately refused to name a cause. I found a different file with FIVE independent corroborations — right medium, right mode, right symptom, right bit-arithmetic, right stated purpose — and it was still wrong. FIVE CONVERGING CIRCUMSTANTIAL FACTS DID NOT SURVIVE ONE BUILD. Had this landed as the diagnosis, the fix would have been committed, the gate would still have failed, and the next session would have inherited a FALSE root cause with a plausible story attached — strictly worse than no cause at all.**

⚠ **The edit is RETAINED as hygiene and is PROVABLY A NO-OP ON MAIN TODAY** (`DT_FAIL == 99` pre-renumber, so the emitted byte is unchanged); it becomes load-bearing only once the renumber lands. **It is correct by reading, UNGATED by a watermark run, and IS NOT THE CAUSE OF THIS DEFECT. Do not let its presence read as a fix.**

---

## 5. MONITOR — RUN FIRST, AS THE CURSOR DIRECTED

`PARTICIPANTS="spl scr" test_monitor_3way_sync_step_auto.sh` on the minimal repro:

```
| step | stno | spl                     | scr            | source                        |
| 1    | 1    | LABEL stno=INT=1        | LABEL stno=INT=1 | expr = *('abc' 'def')       |
| >2   | 1    | @1 VALUE expr = UNKNOWN | @1 CALL EXPR$0   | expr = *('abc' 'def')       |
```

**Bracket: statement 1.** SPITBOL records a VALUE store; SCRIP records a CALL into `EXPR$0`. ⚠ **NOT yet proven to be the fault rather than trace-granularity** — the control (same monitor against a `main` build) was NOT run, and until it is, this row must not be quoted as the defect. **That control is rung 0 for the next session.**

---

## 6. WHAT IS RULED OUT, BY MEASUREMENT

- ⭐ **NOT a dropped tag symbolization in the silent auto-merge.** The collision set is exactly FOUR files (`bb_call.cpp`, `bb_call_fn.cpp`, `bb_call_proc_staged.cpp`, `xa_flat.cpp`); only `xa_flat.cpp` conflicted loudly. `DT_*` symbol counts in the merged tree MATCH the branch's exactly in all three auto-merged files (8/8, 23/23, 6/6) ⇒ the branch's fixes SURVIVED.
- ⭐ **NOT a stale tag literal anywhere else in the tree** — one hit tree-wide (§4), falsified.
- ⭐ **NOT deferred construction / `DT_E`** — `DATATYPE` round-trips as `EXPRESSION`.
- ⭐ **NOT m4 / TEXT medium** — m4 fail set byte-identical across the merge.
- ⚠ **NOT ruled out: an interaction with main's in-flight WIREREG surgery (s22u).** Main's 48 commits rewrote `bb_match_defer.cpp`, `bb_save_restore.cpp`, `bb_call_value.cpp`, `bb_match_capture.cpp`, `bb_match_release.cpp` and added a NEW hand-asm `rt_outer_call` — i.e. the call/wire/defer protocol EVAL rides was under active reconstruction while the branch sat. **This is now the leading hypothesis and it is UNTESTED.**

---

## 7. NEXT SESSION — ORDERED

0. ⭐⭐ **RUN THE MONITOR CONTROL: same 2-way run against a `main` build.** If `main` shows the SAME step-2 row, that row is trace-granularity and the bracket must be re-taken. **Do this before anything else — every downstream step keys off it.**
1. ⭐⭐ **BISECT THE 6 BRANCH COMMITS onto today's main** (`50689805` renumber → `9dcc0851` → `0bc20587`). Mechanical, ~3 builds at ~4 min. Names the exact commit. ⚠ If the renumber ALONE (`50689805`) breaks it, the cause is main-side code the renumber exposes. If a LATER "fix" commit breaks it, the cause is an OVER-SWAP — the s230 READING RULE hazard (`[reg+0]`=TAG, `[reg+4]`=SLEN; `cmp esi,1/2` is SLEN; `cmp eax,2` @ `bb_call_fn.cpp:366` is `g_zeta_mode`) — a genuinely different defect with a different fix.
2. Instrument the LOST STORE directly: does the chain blob for `*'abc'` execute its `EVAL_TMP` store at all? A `ud2` on the store path settles it in one run (ARCH §7 0(f): prefer a HARD probe over a value probe when a silent result reads two ways).
3. Only then re-gate the merge at main's THEN-CURRENT watermark. ⛔ **Main moves; never reuse 294/23. Re-prove at session start, N≥4, `setarch -R`.**
4. ⚠ `.s` regen ×3 is OWED by any landing and was NOT run (nothing landed).

**⛔ THE MERGE MUST NOT LAND UNTIL THIS IS ROOT-CAUSED.** It builds clean and git raises no conflict on the three colliding files — s232's warning that "a clean build is exactly what a session merging this would have seen" is confirmed a second time, against a different main.

`handoff_status.sh` is the push truth — NOT this document.
