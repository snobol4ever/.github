# FINDING s186 — gimpel batch C: 9 green, 15 red, and 3 modules the Spitbol oracle cannot run at all

**Session:** 2026-08-20 s186 · seat6 · queue row `gimpel-drivers-C` · corpus `f79826f7`, SCRIP `47064a1c` (pristine, RT_OPT `-O0`)
**RE-PROVEN ON THREE TREES**, each its own `make pristine`: `47064a1c` → `06358b06` (m1-class-b chained deferral; moved `emit.cpp`/`lower_snobol4.c`/`pattern_match.c`/`x86_asm.h`) → **`213771e2` (the s187 DEFER-DEPTH FLOOR fix, `fccc81cc`)**. Corpus **m3 332/5 · m4 325/11** on all three, and the batch-C verdict table **byte-identical on all three**. See §7 — the third tree is not bookkeeping, it is a result.
**Brief:** Lon s183 ruling — *"You should make tests out of each Gimpel function. Make an entire test suite around it."* Batch C = 25 modules (18 self-contained + 7 include-bearing).
**Delivered:** 24 new `<NAME>_driver.sno` + oracle `.ref` (BLANKS was HQ's worked example), 1 `.input`, 3 probes in `corpus/probe/gimpel/`.
**Corpus fail-set for the existing suites: UNCHANGED — m3 332/5, m4 325/11**, fail-sets identical by name (§6).

---

## 1. THE BOARD

| module | m3 | m4 | module | m3 | m4 |
|---|---|---|---|---|---|
| ROMAN | PASS | PASS | TICTACTO | **TIMEOUT** | **TIMEOUT** |
| ROTATER | PASS | PASS | TREE | **SIG11** | **SIG11** |
| RPAD | PASS | PASS | TSORT | **DIFF** | **DIFF** |
| SPELL | PASS | PASS | AI | **SIG11** | **SIG11** |
| STRINGOU | PASS | PASS | AOPA | **SIG11** | **SIG11** |
| SWAP | PASS | PASS | BLANKS | **TIMEOUT** | **TIMEOUT** |
| SYSTEM | PASS | PASS | BRKREM | **DIFF** | **DIFF** |
| UPLO | PASS | PASS | SQRT | **COMPILE_FAIL** | **COMPILE_FAIL** |
| BNORM | PASS | PASS | TUPLE | **SIG11** | **SIG11** |
| SEQ | **SIG11** | **SIG11** | ARC | **COMPILE_FAIL** | **COMPILE_FAIL** |
| SSORT | **SIG11** | PASS | ASM | **SIG6** | **COMPILE_FAIL** |
| SUBSTR | **DIFF** | **DIFF** | TEMP | **DIFF** | **DIFF** |
| TEST | **RC1** | **COMPILE_FAIL** | | | |

**9 GREEN both modes · 16 RED** (BLANKS pre-existing, HQ s183). Every red is **checked in red** per law 0d.

⛔ **THREE m3 ≢ m4 DIVERGENCES — the design invariant is broken on this batch:** `SSORT` (SIG11 vs **PASS**), `TEST` (RC1 vs COMPILE_FAIL), `ASM` (SIG6 vs COMPILE_FAIL). SSORT is the sharp one: mode 4 gets the right answer and mode 3 dies.

## 2. THE DEFECTS, NAMED

**Silent wrong answers (4) — the class that certifies nothing while looking green:**

| module | call | oracle | SCRIP |
|---|---|---|---|
| `SUBSTR` | `SUBSTR('ABC',2,5)` | statement **FAILS** | returns `BC` and **succeeds** |
| `TEMP` | `N = TEMP(); $N = 'stored'; OUTPUT = N '=' $N` | `TEMP3=stored` | `TEMP3=` |
| `TSORT` | `TSORT(A)` over `pear apple mango fig` | `apple fig mango pear` | `fig mango apple pear` — and the table case emits **no line at all**, shifting every later line up |
| `BRKREM` | `'abc,def' BRKREM(',') . W` | `[abc]` | `[]` — the returned pattern matches null instead of breaking; 4 of 5 cases wrong |

**Crashes (6):** `SEQ`, `AI`, `AOPA` (one cause, §3), `TREE` (SIGSEGV with **zero** output), `TUPLE` (SIGSEGV after one line), `ASM` (SIGABRT).
**Non-termination (1):** `TICTACTO` — >20s in both modes where the oracle finishes immediately.
**Front-end gaps (3):** trailing-dot real literals (§4) take `SQRT` and `ARC`; `?` (tree kind 9) takes `TEST` — *"expression form not in the landed subset"*.
**Missing built-in (1):** `SQRT` is a Spitbol built-in and SCRIP has none — `OUTPUT = SQRT(4)` raises `Error 5, Undefined function or operation` where sbl prints `2.`. No driver covers this any more (SQRT_driver now drives the module), so it is recorded here.

## 3. ⭐ THREE PROBES, EACH WITH ITS PASSING SIBLINGS BESIDE IT

Each is minimal by ablation and ships the near-miss variants **in the same file**, so a future reader sees what the ingredient actually is rather than a bare failing line.

**`probe/gimpel/gim_indirect_read_third_operand.sno`** (from `TEMP`). An indirect read `$N` whose cell was created **only** by a preceding indirect store reads as NULL when `N` is **also the first operand of the same three-operand concatenation**. Three ingredients, all required:
- the name in `N` is built at **run time** — `N = 'V1'` written literally is correct, and **one literal mention of `V1` anywhere masks it**;
- the exact shape `N <literal> $N` with `$N` **last of three** — `$N` alone, `N $N`, `N 'x' 'y' $N`, `N 'x' $N 'y'`, `'p' 'q' $N`, `M 'x' $N` and `$N 'x' N` are all correct;
- **nothing may read `N` before the witness** — a bare `M = N` above the store masks it entirely.

⛔ **AND IT CASCADES:** run the witness first and *every later* indirect read of `$N` goes null too, including the five shapes that are correct in isolation. The damage is not confined to the offending statement. Identical in m3 and m4, under `SCRIP_OPT=0`, and under `SCRIP_RTSEQ_RESUME=0`.

**`probe/gimpel/gim_seq_code_loop_in_function.sno`** (from `SEQ`; takes `AI` and `AOPA` with it — both route through SEQ). A `DEFINE`d function that reaches its loop variable indirectly through a **name argument**, drives a `CODE()`-compiled statement by **indirect goto `:<ARG_S>`**, and returns once that loop fails, runs the body correctly and then **SIGSEGVs on the way out**. ⛔ **This is NOT "CODE is unimplemented"** — the probe proves each half correct in the same run: the top-level `CODE` + `:<C>` loop exits cleanly with `J = 4`, and a function writing then reading `$ARG_NAME` and FRETURNing is right. Only the two together crash.

**`probe/gimpel/gim_real_print_precision.sno`** (from `SQRT`/`ARC`). Reals **print at a different precision**: `2 ** 0.5` is `1.4142135623731` from the oracle (Spitbol's `&FMT`, 14 significant digits) and `1.4142135623730951` from SCRIP; likewise `1.0/3.0` and `2.0/3.0`. The integer and exact-value controls in the same file stay correct, so this is a precision defect and not a formatting change.

⛔ **The OTHER half of what batch C hit here was already landed by the batch-B seat as `gim_real_literal_parse.sno`** — a trailing-dot real with no fraction digits (`1.` `4.` `25.`) is legal Spitbol and is the notation `SQRT.sno` and `ARC.sno` are written in, but SCRIP raises `parse error: syntax error`, which is why those two modules do not compile **at all**. Batch C independently distilled the same witness and it is **deliberately not committed twice**; the precision probe above is kept separate because it needs no trailing-dot literal and would still be wrong after that parse gap closes.

Likewise **no probe was minted for `SSORT`**: its `*LGT(T,S)` — a deferred predicate call with arguments inside a pattern — is already the batch-B seat's `gim_defer_pred_in_pattern_segv.sno`, down to the same m3-crashes/m4-passes divergence.

## 4. ⛔⛔ THE CONVENTION NEEDS AN AMENDMENT BEFORE BATCHES D–F: `sbl` EXITS 0 WHILE PRINTING AN ERROR DUMP

**Three of 25 batch-C modules cannot be run by the Spitbol oracle at all** — not a defect in SCRIP, and not something normalization reaches:

| module | sbl verdict | why |
|---|---|---|
| `SQRT.sno` | `SQRT.sno(8) : ERROR 248 — attempted redefinition of system function` | `DEFINE('SQRT(Y)...')`; SQRT is a Spitbol built-in |
| `TUPLE.sno` | `TUPLE.sno(31) : ERROR 248 — attempted redefinition of system function` | `DEFINE('LOAD(LOC)')`; LOAD is a Spitbol built-in |
| `ASM.sno` | `ERROR 160 — inappropriate file specification for output` | `OUTPUT(.DISK,10,,'ASMTEMP')`, a four-argument form Spitbol does not accept |

⛔ **THE TRAP: `sbl` RETURNS rc=0 ON ALL THREE.** A refgen that trusts the exit status pins the **error dump** as the `.ref` — and that dump carries `execution time msec`, `memory used (bytes)` and `memory left (bytes)`, so the pin is **non-deterministic as well as wrong**, and the module then scores against a fiction. Batch C caught this only because the SQRT dump was eyeballed. **Refgen for batches D–F must grep the oracle output for `ERROR <n> --` / `execution time msec` and refuse, never trust rc.**

**The cure used here:** CSNOBOL4 (`snobol4 -b`) is the *other* sanctioned SNOBOL4 oracle (CLAUDE.md: *"CSNOBOL4 + SPITBOL for SNOBOL4"*), it has no `SQRT`/`LOAD` built-in collision and accepts the four-argument `OUTPUT()`, and it runs all three modules as written. Those three `.ref`s are CSNOBOL4-generated and **each driver's header says so and why**. `ARC_driver` inherits it (ARC includes SQRT). The scorecard grades PASS against pin **or** live, so a CSNOBOL4 pin costs nothing.

## 5. THREE THINGS ABOUT THE CORPUS ITSELF

- **`TUPLE.sno` is the only batch-C module with NO header comment**, so it has no contract to write cases from. Its cases come from the one place machine M *is* documented — `ASM.sno`'s header (chapter 18 of *Algorithms in SNOBOL4*) and its `LIST` opcode table — driven through the published `TUPLE(OP,ARG1,ARG2,ARG3)` signature only, never off the implementation. Batches D–F should expect more of these; the manifest's `contract_line` column is empty exactly when this happens.
- **`RPAD.sno` and `SUBSTR.sno` comment their own `DEFINE` out** and say so — they are built-ins under Spitbol, so their drivers necessarily drive the built-in. That is where the `SUBSTR` defect lives: it is a **built-in** defect, not a module defect.
- **`ASM_driver` writes `ASMTEMP` into the corpus directory**, per ASM.sno's own header. Added to `corpus/.gitignore`.

## 6. GATE

`make pristine` first (HQ-27), then `bash scripts/test_corpus_snobol4.sh`:

```
mode-3 (--run):     PASS=332 FAIL=5
mode-4 (--compile): PASS=325 FAIL=11 SKIP=1  (337 total)
```

Identical to the brief's stated baseline, and the fail-sets match **by name**: m3 `145_pat_left_assoc_via_arbno_fence 160_pat_alt_inner_gen_resume 175_pat_bal_generator_retry 1110_array_1d 216_indirect_goto_computed`; m4 those five plus `expr_eval 140_pat_eval_double_fn_trick 141_pat_eval_double_fn_arbno semantic_driver demo_treebank demo_claws5`, skip `132_pat_fence_eps_recur_shallow`. This batch touched **no SCRIP code** — corpus files only — so the invariance is expected and is stated as confirmation, not as a claim of work.

## 7. WHAT THIS SAYS ABOUT THE M1 WALL CLAIM

HQ predicted gimpel would be a second independent witness source for the M1 pattern class. Batch C **partly** bears that out and partly does not, and the distinction matters:

- `SSORT` (`*LGT(T,S)` — a deferred call with args inside an alternation), `TREE` (recursive deferred `*ARB_TREE`), `BRKREM` (a pattern built and returned by a function), `TICTACTO` and `BLANKS` are all pattern-engine reds and looked like that family. `SSORT` is the one already settled, and by someone else: `gim_defer_pred_in_pattern_segv` from batch B.

⛔⭐ **AND THE OBVIOUS TEST WAS RUN, AND IT SAYS NO.** seat2's **DEFER-DEPTH FLOOR** fix (`fccc81cc`, s187 — *"the DT_X chain was resolved ONCE, so a pattern two `*defer` links deep came back NOMATCH in both modes"*) plus seat3's one-authority follow-up `213771e2` landed mid-handoff. Rebuilt pristine on it and re-ran the whole batch: **the verdict table is byte-identical — not one red moves, in either mode.** `TREE`, whose `*ARB_TREE` recurses through a defer, still SIGSEGVs with zero output; `TICTACTO` still hangs; `BRKREM` still returns a null-matching pattern. So the batch-C pattern reds are **not** the defer-depth class, and saying so is worth more than the guess: the next seat should not spend the rung re-testing them against it.
- But four reds are **not** pattern reds at all and would never have been found by pointing more patterns at the engine: a **parser** gap (trailing-dot reals), a **printing** gap (real precision), a **missing built-in** (SQRT), and a **built-in semantics** gap (SUBSTR clamping where Spitbol fails). The `TEMP` indirect-read defect is a fifth, and its ingredient list — runtime-built name, operand position, and a masking read *anywhere earlier* — is a storage/liveness shape, not a Byrd-box shape.

⭐ **The value of driving a library nobody wrote for SCRIP is not that it aims better at the wall we already know about; it is that a third of its reds are nowhere near that wall.**
