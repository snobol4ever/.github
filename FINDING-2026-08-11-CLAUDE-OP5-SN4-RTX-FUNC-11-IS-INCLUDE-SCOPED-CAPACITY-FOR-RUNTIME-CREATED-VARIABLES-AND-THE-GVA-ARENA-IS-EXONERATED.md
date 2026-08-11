# FINDING 2026-08-11 — CLAUDE-OP5 — SN4 RTX-FUNC-11 REDUCED TO A 45-LINE TWO-SIDED WITNESS: THE TRIGGER IS RUNTIME-CREATED VARIABLES (`$` INDIRECT ASSIGNMENT) ARRIVING VIA `-INCLUDE`, THE CAPACITY IS SIZED FROM THE **MAIN FILE**, AND THE GVA ARENA IS EXONERATED BY ITS OWN KILL-SWITCH

**Fingerprint at measurement:** SCRIP `565ecfa8` (3155 commits, unshallowed) · corpus `eb23c7ee` · `.github` `984414e3` · `scrip` mtime 00:37:45 · `RT_OPT` default (`-O0`, NOT directed otherwise) · AB default (OFF).
⚠ **Trees moved under this seat mid-session** — corpus `bea31de0`→`eb23c7ee` and `.github` `6bb9f32f`→`984414e3` within seven minutes of the clone, and `/home/claude/x64` was checked out at 00:33 by another actor. Every number below was taken against ONE binary whose mtime was verified unmoved across the whole run.

---

## 1. BASELINE RE-PROVEN AT HEAD — THE DEFECT IS NOT FIXED BY THE RTCC/WREG/ZCTX LANDINGS

All **17/17** `corpus/programs/snobol4/beauty_suite/*_driver.sno` SIGSEGV (rc=139) in m3 at `565ecfa8`. The s+7 cursor recorded the same 17 at `bce9a4b`; everything that landed between (RTCC default-on, WREG, ZCTX header contract) leaves it untouched. **Verdicts taken by output-diff against `.ref`, not by exit-code test** — the s+7 self-falsification (SIGBUS 135 scored as clean by a probe that only tested 139) is not repeated here.

## 2. MONITOR-FIRST DISCHARGED — FIRST TIME ON THIS RUNG

The prior cursor recorded MONITOR-FIRST as **not** discharged because "neither oracle is present." Both were cheap:
- `/home/claude/x64/bin/sbl` runs `fence_driver.sno` **clean and byte-equal to `fence_driver.ref`**.
- `scripts/test_monitor_2way_spitbol_vs_run.sh` already exists and is a thin wrapper setting `PARTICIPANTS="spl scr" SCRIP_RUN_FLAG=--run`. The cursor's note that the 2-way script "runs `csn spl`, not `spl scr`" is true of `test_monitor_2way_sync_step_bin.sh` but **not** of this sibling. Nothing needed building.

Monitor result on `fence_driver.sno` — **DIVERGE step 48, stno 28**, source `global.sno:29`:

```
UTF[CHAR(194) CHAR(160)] = 'NO_BREAK_SPACE'
  spl : @28 VALUE <lval> = STRING(14)='NO_BREAK_SPACE'
  scr : LABEL stno=INT=29          <-- no VALUE event emitted at all
```

⚠ **THIS DIVERGENCE IS REAL BUT ITS RELATION TO THE SEGV IS UNPROVEN.** It occurs *before* the crash. It is recorded as an independent observation and **not** claimed as the crash's root cause. See §7(b) for a self-falsification I made about exactly this.

## 3. THE ZERO-COST CONTROL REPRODUCES — AND REDUCES TO ONE LINE

s+6 reduced this to a path-swap (identical bytes, inline vs `-INCLUDE`). Reproduced in seconds:

| arm | result |
|---|---|
| `-INCLUDE 'global.sno'` + `OUTPUT='done'` | **SIGSEGV** |
| identical bytes inlined | `done-inline`, rc=0 |

Bisect by included line count (`head -N global.sno`): N≤160 clean, **N=161 crashes**. Line 161 is

```
	$UTF_Array[i, 2] = UTF_Array[i, 1]   :S(G1)
```

i.e. the **indirect reference operator `$` used as an lvalue** — SPITBOL manual Ch.7/Ch.9, assignment to a variable whose *name* is computed at run time — looping via `:S(G1)` over `SORT(UTF)` and thereby creating one new variable per table entry. At N=160 the loop body is truncated, the loop never runs, and nothing crashes.

⭐ **THIS RE-READS s+7's "SCALE LAW".** s+7 measured "entries ≤88 clean / ≥112 crash" and reasonably read *entries* as table entries. It is not table capacity — it is **the count of variables created at run time by `$` assignment**, which in `global.sno` happens to equal the UTF table's entry count because the loop walks it one-for-one. The two are numerically identical in that program and completely different mechanisms.

## 4. MINIMAL WITNESS — MINTED, TWO-SIDED, 45 LINES

`corpus/probe/rtx11_dynvar.inc` (N=40) + `rtx11_dynvar_include.sno` + `rtx11_dynvar_inline.sno` + oracle `.ref` for both.

```
	T = TABLE()
	T['k1'] = 'DYNVAR1'          ... N entries ...
	A = SORT(T)
	i = 0
G1	i = i + 1
	$A[i,2] = A[i,1]	:S(G1)
```

| | oracle | SCRIP m3 | SCRIP m4 |
|---|---|---|---|
| `-INCLUDE` arm | `done` | **rc=139** | **rc=139** |
| inline control | `done` | rc=0 `done` | rc=0 `done` |

**BOTH MODES DIE, independently confirmed on a 45-line program.** m4 built with `gcc -no-pie f.s -L$(dirname libscrip_rt.so) -lscrip_rt` — note the `.so` lives at `SCRIP/out/libscrip_rt.so`, not the repo root; a bare `-L/home/claude/SCRIP` link-fails.

## 5. THE THREE-ZONE THRESHOLD REPRODUCES, WITH A PROBABILISTIC BAND

With a bare 3-line driver, sweeping N (runtime-created variables):

| N | verdict |
|---|---|
| ≤15 | clean |
| **16** | **probabilistic — 139, 0, 139, 139, 0 over 5 runs** |
| ≥17 | crashes 100% |

Same three-zone shape s+7 measured (≤88 / 104 probabilistic / ≥112) at different absolute numbers. **A coin-flip band at the boundary is the signature of an out-of-bounds write landing on memory whose contents vary** — independent corroboration of s+7's ASLR conclusion (address-layout changes the signal, not the incidence) by a different instrument.

## 6. ⭐⭐ THE CAPACITY IS SIZED FROM THE **MAIN FILE** — FALSIFIABLE PREDICTION, CONFIRMED

If the capacity that `$`-created variables overflow were sized from the main file's statements, padding the driver with inert statements should raise the threshold. Measured, `PAD` = dummy `PADj = j` statements added to the driver:

| driver statements added | max clean N |
|---|---|
| 0 | 16 |
| 10 | 20 |
| 30 | 30 |
| 60 | 60 |

**Monotonic.** This is why the real suite needed 161 included lines to fall over while a 3-line driver needs only 17: `fence_driver.sno` supplies its own headroom. ⇒ **MECHANISM CLASS: a capacity for run-time-created variables is sized at compile time from the MAIN file, and statements arriving through `-INCLUDE` do not enlarge it.** The exact allocation is **NOT named** — see §8.

## 7. FALSIFICATIONS — THREE HYPOTHESES KILLED, TWO OF THEM MINE

(a) **TABLE GROWTH / REHASH — DEAD.** The first hypothesis from the monitor's step-48 line was a hash-table growth defect. Direct sweep: plain table inserts with integer, string, and `CHAR(194) CHAR(n)` computed keys are **clean at 80/100/112/125/200/400 entries, all three key kinds**. Table growth is exonerated and the computed-key expression is irrelevant.

(b) ⛔ **"THE MONITOR IS STRUCTURALLY BLIND BECAUSE `MONITOR_BIN` DISABLES THE GVA ARENA" — MY OWN CLAIM, FALSIFIED BY MY OWN NEXT COMMAND.** `driver/scrip.c:1537` reads `int n_gva_m3 = getenv("MONITOR_BIN") ? 0 : gva_count();`, and I asserted from that line that the monitor cannot see this crash. Measurement: **the witness segfaults with `MONITOR_BIN` set exactly as it does without it** (N=40, 3/3 each arm; `fence_driver.sno` likewise 139 in both). The GVA arena is **exonerated by its own kill-switch**, and my "structurally blind" claim is withdrawn. ⭐ I convicted a mechanism from a single line of source one command before the tree falsified it — the exact failure this project's MONITOR-FIRST rule exists to prevent, committed while quoting that rule.

(c) ⛔ **A PIPED `head` MASKED AN EXIT CODE AND MANUFACTURED A FALSE "FIX".** `$SCRIP --run fence_driver.sno | head -2; echo rc=$?` reports **`head`'s** status, not scrip's. That printed `rc=0` for an arm that in fact segfaults, and for several minutes I believed the GVA kill-switch had cured the real driver. Caught by re-measuring with `>file` redirection instead of a pipe. ⭐ **Same genus as s+7's SIGBUS-scored-as-clean and s+5b's `grep -c "fn_cell\$"` anchor bug: a probe that can only observe one outcome reports every other outcome as the one it can see.** Third instance in three sessions — the standing remedy is to redirect and diff, never to pipe into a truncating filter and read `$?`.

## 8. ⛔ WHAT IS **NOT** DONE — NO SITE IS CONVICTED

- **The allocation is not named.** `src/optimizer/gva_collect.c` grows correctly (realloc doubling) and the GVA arena is exonerated in §7(b). `rt_indirect_assign_str` → `rt_gvar_assign_str` → `NV_SET_fn` is the runtime path but was **not** instrumented. **No code site is convicted; §6 establishes a mechanism CLASS by measurement, nothing finer.**
- **gdb single-step not run** (no gdb in container; the s+4 core-file technique — parse `NT_PRSTATUS` for RIP/RAX — is the standing substitute and is the obvious next instrument).
- **Bisect not run**, though now possible: SCRIP is unshallowed at 3155 commits. Whether this is a regression or original debt is **unknown**; the witness is cheap enough to be a bisect predicate (`rc==139` on a 45-line program, sub-second).
- The step-48 monitor divergence (§2) is **unowned** — it may be a second, independent defect in table-element assignment tracing.
- No `.s` regen (no templates touched). No corpus watermark sweep re-run this seat.

## 9. NEXT, IN ORDER

1. **Bisect** with the new witness as predicate — it is fast, deterministic at N≥17, and needs no corpus.
2. **Core-file the crash** (§8) to get RIP and name the write.
3. **Own the `-INCLUDE` coverage hole** that s+7 flagged and this seat corroborates: `crosscheck/` has zero live `-INCLUDE`, so a 269-program suite is structurally incapable of catching this class. The witness minted here is the first `-INCLUDE` probe outside the 17 red drivers.
4. Settle whether §2's step-48 divergence is a second defect.

**`handoff_status.sh` is the push truth — NOT this document.**

---

## 10. ⚠⚠ CROSS-SEAT RECONCILIATION — A PARALLEL Opus 5 SEAT LANDED AN `s_this+8` CURSOR ON THIS SAME RUNG WHILE I MEASURED

Discovered at cursor-write time (`.github` moved `6bb9f32f`→`984414e3` under this seat). That seat minted an 8-line witness, read the core without gdb (`rip` in an anonymous JIT slab ⇒ **emitted code, not `libscrip_rt`**; `rbx` — the pinned DESCR mint pointer — wild), and killed four hypotheses (subscript-overrun, stack overflow, arena exhaustion, RTCC). **Their reduction is tighter than mine and their core read is strictly more informative. I do not restate it; read their FINDING.** What follows is only what this seat adds or contradicts.

**ADDS — their explicit NEXT ACTION, now done.** Their cursor reads *"MONITOR-FIRST NOT DISCHARGED — but the blocker is gone. NEXT ACTION: run the monitor on it."* **§2 above ran it** and it yields a named first divergence (step 48 / stno 28, missing VALUE event on a table-element assignment). Also new here: **table growth exonerated to 400 entries** (§7a) and the **GVA arena exonerated by its own `MONITOR_BIN` kill-switch** (§7b) — neither appears in their hypothesis list.

**⛔ CONFLICT 1 — THE PRODUCT LAW DOES NOT SURVIVE MY PADDING SWEEP.** They state the scale law is a **product**, include-defined vars × loop iterations ≳1500, and warn that *"any probe naming only ONE factor re-derives a threshold that does not transfer."* In my reproducer vars and iterations are both `N`, so the product is `N²`. Measured: **N=17 crashes (product 289)** with a bare driver, while **N=60 is clean (product 3600)** once the driver carries 60 inert statements. A pure product law predicts the opposite ordering. ⇒ **there is a THIRD factor neither of us had isolated: the MAIN FILE's own statement count, which supplies headroom** (§6, monotonic over pad 0/10/30/60). The honest synthesis is that the governing quantity looks like created-variables measured **against a main-file-derived capacity** — a headroom/ratio, not a product — and their 1500 constant is then a slice taken at one fixed driver size, exactly the transfer failure their own warning describes, one level up. **Neither law is established; both are slices. This needs a 3-D sweep (vars × iters × driver statements) before any constant is quoted again.**

**⛔ CONFLICT 2 — THE m4 INLINE CONTROL HOLDS ON MY WITNESS.** They state *"THE INLINE ARM IS A CONTROL IN m3 ONLY — m4 KILLS BOTH ARMS."* On `corpus/probe/rtx11_dynvar_*` at N=40, assembled `gcc -no-pie f.s -L SCRIP/out -lscrip_rt`: **m4 include rc=139, m4 inline rc=0 printing `done`** (§4). Both arms measured in the same command, same binary. Either the two witnesses differ in a way that matters, or one of the two m4 recipes is wrong. ⚠ **I do not claim theirs is wrong** — their m4 recipe was validated by a green `hello` control, and mine differs at least in the `-L` path (`SCRIP/out`, not the repo root; a bare `-L/home/claude/SCRIP` link-fails, which is a plausible way for an m4 arm to look broken for a non-defect reason). **UNRESOLVED — settle before either m4 claim is treated as load-bearing.**

**METHOD NOTE:** two seats independently reduced the same defect within one hour and reached *different* scale laws from *non-overlapping* probe geometries, each internally consistent. That is not redundancy — the disagreement is the finding, and neither seat could have produced it alone.

---

## 11. ⭐⭐ THE 3-D SWEEP RAN — AND IT FALSIFIES **EVERY** SCALE LAW SO FAR, INCLUDING BOTH OF MINE

§10 said a 3-D sweep was owed before any constant is re-quoted. It ran. The enabling move is **decoupling**: in s+8's witness and in my §4 witness, distinct-variables and loop-iterations move together, so neither seat could tell which drives the fault. An outer repeat loop separates them — `V` distinct names, `R` repeats, `V×R` total assignments (`/tmp/gen3.py` shape, inner loop terminating on the failing subscript as the original idiom does).

**MEASURED, D=0 (bare 3-line driver), N=3–4 per point:**

| geometry | distinct V | repeats R | total assigns | crash |
|---|---|---|---|---|
| V=16 R=1 | 16 | 1 | 16 | 2/3 |
| V=8 R=2 | 8 | 2 | 16 | **0/3** |
| V=1 R=16 | 1 | 16 | 16 | **0/3** |
| V=20 R=1 | 20 | 1 | 20 | **3/3** |
| V=10 R=2 | 10 | 2 | 20 | 2/3 |
| V=5 R=4 | 5 | 4 | 20 | **0/3** |
| V=1 R=20 | 1 | 20 | 20 | **0/4** |
| V=1 R=30 | 1 | 30 | 30 | **0/4** |
| V=1 R=40 | 1 | 40 | 40 | **4/4** |
| V=1 R=5000 | 1 | 5000 | 5000 | 3/3 |

**FOUR LAWS FALSIFIED:**
1. **TOTAL ASSIGNMENTS — DEAD.** total=20 gives `V=20,R=1` **3/3 crash** and `V=1,R=20` **0/4 clean**. Same total, opposite verdicts.
2. **DISTINCT VARIABLES ALONE — DEAD.** `V=10,R=1` is clean; `V=10,R=2` crashes 2/3. The *same ten names* reassigned. ⇒ **re-assigning an ALREADY-EXISTING variable still consumes capacity** — the consumption is not per-name.
3. **s+8's PRODUCT (vars × iters ≳1500) — DEAD in this geometry.** `V=20,R=1` (product 20) crashes; `V=3,R=500` (product 1500) also crashes; `V=1,R=30` (product 30) is clean while `V=16,R=1` (product 16) crashes 2/3. The ordering is not monotone in the product.
4. **SIMPLE LINEAR COMBINATIONS — DEAD.** Fitting `cost = aV + b·VR` against the two near-threshold points (`V=16,R=1`, `V=10,R=2`) yields `b=1.5a`, `T=40a`, which then predicts `V=1,R=30` **crashes**; measured **0/4 clean**. Fitting `cost = aV + bR` gives `b=6a`, `T=22a`, which mispredicts the same point far worse. **No one- or two-term model fits.**

**WHAT SURVIVES — ONLY THIS, AND IT IS DELIBERATELY WEAK:**
- Both axes reach the fault **independently** (V=1 crashes at R≥40; R=1 crashes at V≥20).
- **Strong asymmetry: distinct variables are far more expensive than repetitions** — ~20 names ≈ ~40 repeats of one name at D=0.
- **V=1 threshold is bounded: R=30 clean 0/4, R=40 crash 4/4.**
- The **third axis D** (main-file statement count) shifts thresholds monotonically (§6).
- Every boundary carries a **probabilistic band** (2/3, 2/4), consistent throughout with an out-of-bounds write, never a logic error.

⇒ ⛔⛔ **STANDING INSTRUCTION FOR THE NEXT SEAT: STOP DERIVING THRESHOLD CONSTANTS.** s+7's `112`, s+8's `1500`, and my own `16`/`17` are each a **1-D slice of a ≥3-D surface**, each internally valid on its own probe geometry and each non-transferable. Three seats have now independently produced a constant and each was falsified by the next geometry tried. **The instrument to reach for is not another sweep — it is instrumentation of the allocation itself** (count the consuming events directly, via the s+8 core-file technique or a counter in the runtime path), because the quantity being consumed is evidently NOT any of {names, assignments, their product, their linear combination} and cannot be inferred from black-box thresholds.

⚠ **THIS SECTION FALSIFIES §6 AND §10 OF THIS SAME DOCUMENT, WRITTEN ONE HOUR EARLIER BY THIS SEAT.** §6 read the padding sweep as "capacity sized from the main file, consumed by runtime-created variables" — the padding result stands as measured, but "runtime-created variables" is the wrong consumption unit (falsification 2). §10's contradiction of s+8 stands, but my own replacement law was no better than theirs. **Recorded rather than edited away: three of the four dead laws in this section are mine.**

## 12. THREE MORE EXONERATIONS FROM THE EMITTED ASM — ALL MINE, ALL DEAD, RECORDED SO NOBODY RE-SPENDS THEM

Following §11's own instruction (instrument, do not sweep), the zero-build instrument is the emitted `.s`. **The lowering of `$A[i,2] = A[i,1]` is `rt_deref` → `rt_call_arr` (with a `"SNO$NAME"` literal), NOT `rt_indirect_assign_str`** — §8's named runtime path is not the one the emitted code takes, which retro-justifies §8's refusal to convict it. Three hypotheses raised from that asm and killed the same session:

- ⛔ **INLINE STRING IN THE CODE PATH — FALSE ALARM.** `.Lrkfnzd717: .string "SNO$NAME"` appears between `n306_call_α:` and its `call`, which would be data executed as instructions. It is correctly bracketed by `.section .rodata` / `.section .text` and is never in the instruction stream. **Checked before claiming; the claim died on inspection.**
- ⛔ **MIXED ADDRESSING REGIME SPLITTING ONE GLOBAL — DEAD.** The RTCC writeback emits `mov [g_rtcc_block + 0], rax` (direct) alongside `mov rax,[rip + g_rtcc_block@GOTPCREL]` then `[rax+8]`, `[rax+16]`… — two regimes for one object, the s+4 `fn_cell` genus. Measured: the m4 binary carries `R_X86_64_COPY` **and** `R_X86_64_GLOB_DAT` for `g_rtcc_block`, **both resolving to `0x408080`**. The copy relocation is handled correctly; the regimes agree. No split.
- ⛔ **COPY-RELOCATION SIZE OVERFLOW — DEAD.** A copy reloc reserves a fixed-size copy from the link-time symbol size, so emitted code indexing past it would write into adjacent `.bss`. Measured: `g_rtcc_block` is **256 bytes** in both `.so` and executable; the maximum offset any emitted instruction uses off that base is **+64**. Four-fold headroom. No overflow.

⚠ **These are m4-side observations and could not have explained a both-modes fault anyway** — m3 has no copy relocations. Recorded because each looked like a live lead from the asm and each cost a measurement to kill; and because the `rt_deref`/`rt_call_arr` correction above is load-bearing for whoever instruments next. ⭐ **Running total for this seat: seven hypotheses raised, seven dead, five of them mine.** The mechanism remains unnamed, which is the correct state — §11's instruction stands: put a counter in `rt_call_arr`/`rt_deref` and measure the consuming events directly.
