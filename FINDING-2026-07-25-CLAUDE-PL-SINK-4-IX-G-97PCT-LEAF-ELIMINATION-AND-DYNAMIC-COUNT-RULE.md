# FINDING — PL-SINK-4 (`$ix_g`) LANDED: 97.1% OF LEAF CALLS ELIMINATED, 1.068× ISOLATED — AND STATIC SITE COUNTS PICK THE WRONG RUNG

**Session:** s148, 2026-07-25 · **Goal:** `GOAL-PROLOG-BB.md` · **Rung:** PL-SINK-4 · **RT_OPT:** `-O0` (no `-O2` directed this session)

---

## 0. HEADLINE

`$ix_g` — the clause **index guard** — now emits a per-`kk` specialized guard inside the box. Measured on failure-driven nrev(30)×2000, mode-4, two baked binaries:

| metric | sink OFF | sink ON |
|---|---|---|
| `rt_pl_dop_ix_g` leaf entries | **2,108,000** | **62,000** (−97.1%) |
| wall mean (n=40 interleaved) | 403.0 ms | 378.0 ms |
| wall mean (n=35 confirm block) | 392.6 ms | 366.7 ms |

**RATIO 1.066× / 1.071× across two independent blocks (≈6.8%), sign consistent in 60 of 75 paired runs.** Best-of-min 1.10–1.12×. This is the rung's OWN number — it is gated behind `SCRIP_NO_SINK4` nested inside the family switch, so it is not harvesting SINK-1/2/3's wins (the s146 correction).

---

## 1. ⭐⭐ THE RULE THIS EARNS — **STATIC CALL-SITE COUNTS INVERT THE TRUE RANKING; MEASURE DYNAMICALLY OR PICK THE WRONG RUNG**

s147 earned "PROVE the emitted `.s` reaches the code you are about to edit." This session extends it, because the `.s` proof **is not sufficient** — it tells you a leaf is reachable, not that it is hot.

Static call sites in the emitted `.s` vs. actual dynamic calls:

| leaf | qsort sites | qsort CALLS | nrev sites | nrev CALLS |
|---|---|---|---|---|
| `rt_pl_dop_mkc` | **51** (rank 1) | 100 | 4 | 30 |
| `rt_pl_dop_ix_g` | 5 | **649** (rank 1) | 10 | **1022** (rank 1) |
| `rt_pl_dop_unify` | 9 | 448 | 15 | 31 |

**`mkc` has 10× the call SITES of `ix_g` in qsort and 6.5× FEWER calls; in nrev it has 34× fewer.** A rung chosen by reading the `.s` would have gone to `mkc` and optimized a cold leaf — the same class of error as s147's falsified SINK-6/7, reached by a different road. `ix_g` is the #1 dynamic leaf in **all three** benchmarks measured (nrev 1022, qsort 649, deriv 67).

**METHOD (reusable, and it works where s141's does not):** ⚠ this container has **no `perf` and no `gdb`**, so the s141 gdb-sampling profile cannot be re-run. Dynamic counts were taken by **LD_PRELOAD PLT interposition** — the emitted code calls `rt_pl_dop_*@PLT`, so a preloaded `.so` interposes, counts, and forwards via `dlsym(RTLD_NEXT, ...)`, returning the 16-byte `DESCR_t` blob unchanged. Exact, zero source edits, no rebuild. Shim kept at `/home/claude/plcount.c`. **This should be the default hotness instrument for this ladder** — it is cheaper AND more precise than sampling, and it survives a container with no profiler.

---

## 2. ⚠⚠ SECOND FINDING — **THE ~20% `lexprep2` SINK IS BLOCKED BEHIND THE `xa_flat` TEMPLATE REVAMP; IT IS NOT A SINK RUNG**

The s147 cursor named the callee-prologue double copy (`rt_jmp_frame_lexprep2` + `rt_frame_bind_args`, ~20% of profile) as a live target. **It cannot be taken as a sink rung.** That code is emitted by `src/templates/xa_flat.cpp`, which is still the **unconverted legacy raw-byte family**: separate BINARY and TEXT arms (`:182` vs `:310`), `bytes()`/`u64le()`/hand-rolled `movabs`, with in-source comments stating an L-record "would corrupt the stream."

Adding an inline arm there means writing the `IF(MEDIUM_TEXT,…)+IF(MEDIUM_BINARY,…)` pair that the ONE-MEDIUM-INVISIBLE FACT RULE names as its **forbidden shape** — the rule added 2026-07-07 *after that exact mistake was made twice in one SNOBOL4-BB session*.

**INDEPENDENTLY CONFIRMED BY THE GATE:** `scripts/test_gate_template_medium_invisible.sh --strict` reports `REMAINING: xa_flat.cpp(128)` — xa_flat is the **sole** remaining violator in the tree, with 128 hits. **Proven pre-existing** by `git stash` + re-run on the clean s147 baseline (identical output), per the s126/s145 precedent.

**ACTION:** the lexprep2/bind-args sink is gated on an `XA-FLAT-CONVERT` rung (convert `xa_flat.cpp` to `x86()` concatenation, 128 sites). Until that lands, **do not plan the 20% as sink work** — it is revamp work wearing a perf hat.

---

## 3. THE RUNG

**WHAT `$ix_g` IS.** `lower_prolog.c:837` emits `$ix_g(Subject, kk|kar<<8, Key)` before each clause's head-unify chain when a multi-clause predicate's arg0 is non-var: a bound subject with a provably non-unifiable principal functor SKIPS the clause. It runs **per clause try**, which is why it dominates dynamically.

**WHY THE PREMISE IS LIVE (unlike SINK-6/7).** `rt_pl_dop_ix_g` (`by_name_dispatch.c:1442`) has **no wrapper fast path** — it calls `dop_ix_g` directly — and, unlike most leaves, **does not go through `dop_call`**, so there is no setjmp ceremony hiding the cost. The cost is genuinely the call + `plw_entry`/`plw_cell_deref` + the general switch. Verified by reading the exported wrapper, not the same-named static leaf (the s147 rule).

**THE DESIGN — SPECIALIZE ON `kk`, WHICH IS AN EMIT-TIME CONSTANT.** `args[1]` is an `IR_LIT_INTEGER` packing `kk | kar<<8` and `args[2]` a LIT int/string, so the box emits **one specialized guard per kk** instead of the leaf's runtime switch:
- **kk==3 (list cell):** `DT_PLREF` → `slen == g_plw_dot_sl` ? OK : FAIL; `DT_I`/`DT_S` slen0 → FAIL; else OK. Reuses SINK-2's already-exported `g_plw_dot_sl`; `==0` → SLOW, so a not-yet-interned run defers to the leaf (which interns and answers) rather than mis-failing a real cons.
- **kk==2 (atom):** inlines the hot tag arms — `DT_PLREF` → FAIL, `DT_I` → OK, non-atom → OK — and defers **only** the atom-vs-atom `strcmp`. The ladder's written design deferred all of kk==2 to SLOW; that would have left **527 of nrev's 1022 calls** on the table, because the dominant path (`nrev([],[])` tested against a cons during recursion) is a *tag test*, not a string compare.
- **kk==1 (int):** compares the payload against the emit-time immediate.
- **kk==4 (functor):** **NO sink** — needs a per-site intern cache (contract §3). Follow-on rung. `deriv` is entirely kk==4 and is a clean control: **0 sink sites in both arms, outputs match.**

**MEASURED, AND IT DECIDED THE DESIGN: `args[0]` is `DT_N` in 100% of calls** — the contract §2 trap that made SINK-1's first cut a *net loss* (+8%). `sink_deref` is reused **verbatim** so the name-ref chase stays faithful.

**NO NEW GLOBALS.** `no_new_global` PASS, doomed-ratchet **14 / floor 14, unmoved**.

**LABELS:** 110–120 (SINK-1 40–58, SINK-2 60–77, SINK-3 80–99, SINK-8 100–101).

---

## 4. ENCODER NOTE — THE s143 TRAP WAS LIVE AND WAS AVOIDED BY CHECKING FIRST

kk==3 needs a **32-bit reg/reg** compare (`cmp esi, edx`, slen vs. dot_sl). Per s143, an unsupported operand shape **emits nothing, silently, with no bomb** — the failure signature is the *following* `jcc` reading stale flags. Checked `x86_asm.h` dispatch BEFORE writing: `cmp` supports REG/REG, REG/IMM, REG/ABS64 (and `x86_alu_rr` derives width from the register names, so `esi`/`edx` correctly emit without REX.W). Then **eyeballed the emitted `.s`** and confirmed `cmp esi, edx` is present. `as` accepts all 22 bench artifacts (**rejected=0**).

---

## 5. GATES

- Rung suite **164/164 × 3 modes (interp/run/compile), run TWICE** — unchanged from the s147 baseline (also measured green before any edit).
- Smoke 5/5/5 all three modes.
- **A/B byte-identity ON vs `SCRIP_NO_SINK4=1`, mode-3 AND mode-4, 5/5 PASS**, and m3==m4 on every case. Smoke covers kk==1 (ints), kk==2 (atoms), kk==3 (lists), **backtracking that unwinds inline-decided guards** (`findall` + fail-driven), and unbound subjects.
- **3-way oracle:** gprolog 1.4.5 installed and cross-checked — all 5 smoke cases semantically identical. Only difference anywhere is fresh-variable *naming* (`_37` vs `_G0`), cosmetic and pre-existing.
- Bench corpus `test_bench_prolog_modes.sh`: **green(m3&m4)=22, broken=0, total=22**.
- `no_new_global` PASS (14/14) · `no_value_stack` PASS.
- Bench `.s` regen: emitted=22 changed=12 **rejected=0 errored=0**.
- ⚠ **PRE-EXISTING, NOT MINE:** `test_gate_template_medium_invisible.sh --strict` FAILs on `xa_flat.cpp(128)` — proven pre-existing by stash + re-run (§2).

---

## 6. METHOD NOTES WORTH CARRYING

**(a) THE SINGLE-RUN READING HAD THE WRONG SIGN.** First timing probe: ON 499 ms vs OFF 392 ms — the sink looked **27% slower**. Interleaved 40-run measurement: ON is **6.6% faster**, 33/40 paired runs. s146 said a ~5% effect needed ~60 runs/arm before its sign settled; this is a second, independent confirmation, and a reminder that **one run is not a measurement**. Arms were **interleaved run-by-run** (not block-by-block) so drift hits both equally — recommend this over the two-block recipe.

**(b) EQUAL WORK PROVEN INDEPENDENTLY (contract §8 corollary).** A failure-driven bench printing only `done` prints it faster if it silently does less. Verified via unsunk counters identical in both arms: `trail_unwind` **1,058,000 both**, `mkc` 60,000 both, `unify` 64,001 both, `unwind_nothrow` 128,001 both. Only `ix_g` moved.

**(c) THE `-O0` LABEL IS LOAD-BEARING.** All numbers here are RT `-O0`. The 97.1% call-elimination is optimization-level-independent (it is a count, not a time); the 1.068× wall ratio is not — a `-O2` runtime would shrink the C leaf and likely shrink this ratio.

---

## 7. NEXT

1. **REGAIN-1 slice C (THE SPINE) remains the big rung** — proc-call spine ~36%; needs the driver-minted proc-entry `bb_label_t` table + one in-band `E`/`F` record. Untouched.
2. **`XA-FLAT-CONVERT`** (new, §2) — prerequisite for the ~20% lexprep2/bind-args sink. 128 sites. Also clears the last `--strict` medium-invisible failure in the whole tree.
3. **SINK-4 follow-on: kk==4** (functor) with a per-site intern cache — unlocks deriv-shaped workloads.
4. **Re-measure SINK-1/2/3 with per-rung switches** (s146, still open). SINK-4 and SINK-8 now have theirs; SINK-1/2/3 do not, so the ladder's per-rung numbers still cannot be summed.
5. `mkc` is a **poor** next target despite its site count (§1) — 60,000 calls to `ix_g`'s 2,108,000 on the same bench.
