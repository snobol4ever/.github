# FINDING 2026-08-11 — RTX-FUNC-11 REDUCED TO A 4-LINE WITNESS: THE SCALE VARIABLE IS A **PRODUCT** (vars × iterations), NOT AN ENTRY COUNT. FOUR HYPOTHESES FALSIFIED BY MEASUREMENT, TWO OF THEM MINE. CRASH PC IS IN EMITTED CODE AND `rbx` IS WILD.

**Seat:** Claude Opus 5, 2026-08-11, fresh three-repo clone + `install_system_packages.sh`.
**Fingerprint:** SCRIP `565ecfa8` · corpus `bea31de0` · `.github` `6bb9f32f`. `scrip` + `libscrip_rt.so` built together, mtime **00:23**, verified unmoved across every measurement below. `AB=0` (default), `RT_OPT=-O0`.
**Code changed: NONE.** No edit to SCRIP. This is a characterisation + witness-minting rung only.

---

## 0. WHY THIS RUNG

Inherited LIVE CURSOR (s_this+7) recorded RTX-FUNC-11 as: all 17 `beauty_suite/*_driver.sno` SEGV, "scale-thresholded (≤88 entries clean 8/8, ≥112 crashes 8/8, 104 probabilistic)", "address-layout-sensitive", "both modes", **not root-caused**, MONITOR-FIRST not discharged. s_this+6 had reduced it to an inline-vs-`-INCLUDE` path swap.

## 1. REPRODUCED, THEN REDUCED FROM 17 DRIVERS TO 8 LINES

17/17 drivers SEGV at this build, rc=139, zero bytes. Reduction ladder, each step one experiment:

| probe | content | verdict |
|---|---|---|
| trivial `-INCLUDE` (1 line, empty file) | — | **clean** ⇒ `-INCLUDE` is not broken per se |
| TABLE + 40 entries | no loop | clean |
| + `SORT` | no loop | clean |
| + `SORT` + ONE array read | no loop | clean |
| + label/goto loop | **SEGV** |
| plain `ARRAY(40,2)` + loop | no TABLE/SORT | clean |
| 40 entries, no SORT, loop | | SEGV |
| **40 plain scalars + loop reading one of them** | no TABLE, no SORT, no array | **SEGV** |

⇒ TABLE, SORT, `$`-indirect assignment, array subscripting, and cross-include label+goto are **each exonerated**. What survives is minimal: *N scalar assignments in an included file, plus a loop that reads one of them.*

## 2. ⭐⭐ THE SCALE VARIABLE IS A PRODUCT, NOT AN ENTRY COUNT

2-D scan, include arm, N=1 per cell first (see §5a for why that was not enough), then N=8 at the boundary:

| vars × iters | N=8 result |
|---|---|
| ≤ 1024 | **0/8 crash** |
| 1280 | **1/8 crash** ← probabilistic band |
| ≥ 1600 | **8/8 crash** |

Crash iff `vars × iterations ≳ 1500`. `24×64`, `40×40`, `64×24` all crash; `24×40`, `40×32`, `64×16` all clean. **Neither factor alone does anything:** 40 vars × 3 iters clean; 0 vars × 40 iters clean; 40 vars × 0 iters clean.

⇒ **The inherited "≤88 / 104 / ≥112 entries" law is a SLICE of this surface, not the law.** The prior seat scaled UTF entries in `global.sno` while its loop length was held fixed by the file, so a product law presented as an entry threshold. The three-zone shape (clean / probabilistic / deterministic) is identical, which is why the slice looked like the whole thing. **Any future probe must name BOTH factors or it will re-derive a threshold that does not transfer.**

## 3. WITNESS MINTED, TWO-SIDED, SPITBOL-VALIDATED

`corpus/probe/rtx_func_11_include.sno` + `rtx_func_11_inc.sno` + `rtx_func_11_inline.sno` + `.ref` ×2.
SPITBOL oracle (`/home/claude/x64/bin/sbl -b`) runs **both** arms and gives identical correct output (`i=40 / B=1 / DONE`) — the `.ref`.

| arm | mode 3 | mode 4 |
|---|---|---|
| `-INCLUDE` | rc=139 **DIVERGE** | rc=139 **DIVERGE** |
| inline (byte-identical statements) | rc=0 **ORACLE-EXACT** | rc=139 **DIVERGE** |

## 4. ⭐⭐ THE INLINE ARM IS A CONTROL IN m3 ONLY — m4 KILLS BOTH ARMS, AND HAS ITS OWN SILENT-WRONG DEFECT

s_this+6 recorded the inline arm as "a perfect zero-cost control — same bytes, one path crashes." **True in m3, FALSE in m4:** the m4 binary segfaults on the inline arm too. Recipe validated by control — m4 `hello` builds and prints `HELLO` rc=0 through the identical `--compile | gcc -no-pie … -lscrip_rt` pipeline.

⛔ **AND, INDEPENDENTLY, AT 8×8 (far below every threshold above): m4 prints NOTHING at rc=0 where m3 prints `i=8`.** A silent wrong answer, not a crash — a direct violation of the modes-are-1:1 contract, invisible to any exit-code probe. **This is its own rung and does not belong to RTX-FUNC-11.**

## 5. FOUR HYPOTHESES FALSIFIED BY MEASUREMENT

Each killed at N≥4, none by reading code:

1. **Array subscript overrun** (the loop exits by out-of-range subscript failure) — **DEAD**: a *bounded* loop that never oversteps crashes identically.
2. **Stack overflow** — **DEAD**: `ulimit -s` 2048 / 4096 / 8192 / 32768 / 131072 / unlimited ⇒ **24/24 SEGV**. The threshold does not move at all.
3. **Arena / heap exhaustion** — **DEAD**: `SCRIP_HEAP_MB` 64 / 128 / 512 / 1024 / 2048 / 4096 ⇒ **24/24 SEGV**. Also note the arena *does* have an exhaustion check (`gc_heap.c:233`, `[ZHP] heap exhausted`) and it never fires — whatever faults is not going through it.
4. **RTCC register claim** (RTCC went DEFAULT-ON at `c4cb8813`, and the cross-goal bulletin claims r10/r11 product-wide) — **DEAD**: `SCRIP_RTCC=0` ⇒ repro 4/4 SEGV, beauty drivers **0/17 recovered**. RTCC is not this.

### 5a. ⛔ TWO SELF-FALSIFICATIONS, RECORDED SO NOBODY INHERITS THEM

- **I nearly convicted `SUBSTR` on a probe with an unbounded loop.** Probe P4 (`B = SUBSTR(S,i,1) :S(G1)`) crashed via include and looked like a clean discriminator — until its **inline arm returned rc=124 (timeout)**. The loop never terminates; the two arms were failing *differently*, not one passing. **A discriminator requires the control arm to be not merely non-crashing but CORRECT and TERMINATING.** Caught only because I ran the inline control.
- **My first 2-D scan was N=1 and put `40×32` in the CLEAN column; at N=8 it sits in the probabilistic band.** I then drew a stack-limit conclusion off those N=1 cells that came out *backwards* (a smaller `ulimit -s` appeared to produce **more** clean runs). That conclusion was discarded and re-run at a deterministic point. ⭐ Same genus as the recorded `160_pat_alt_inner_gen_resume` coin-flip and the s+7 SIGBUS miscount: **an N=1 sweep across a probabilistic band manufactures a law.**
- **A third instrument was simply blind:** peak-RSS was flat (12536→12692 KB) and I briefly read that as "no leak". At ~1500 × 16 B ≈ 24 KB against a 12 MB baseline, RSS **cannot** see this. Reporting it as evidence either way would have been false.

## 6. WHERE IT FAULTS — MECHANICAL, FROM THE CORE

No gdb in this container; used the ladder's recorded technique (parse `NT_PRSTATUS` / `NT_FILE` out of the core directly, ~40 lines of python).

- **`rip = 0x7f69ba000cec` lies in NO file-backed mapping** — it is in the anonymous **JIT / RX slab**, i.e. **EMITTED CODE**, below `libscrip_rt.so` (`0x7f69bce00000`). The fault is not in the C runtime.
- **`rbx = 0x347a25d8`** — `rbx` is the **arena heap top / DESCR mint pointer** (ARCH-SNOBOL4-RTX §2 register contract). That value is **in no mapping at all**: wild, not merely past an end. Combined with §5.3 (arena size irrelevant) this reads as a **clobbered pin**, not exhaustion.
- Core file is 1.17 GB, consistent with a runaway/wild write rather than a tidy fault.

⛔ **MECHANISM DELIBERATELY NOT NAMED.** MONITOR-FIRST is not discharged (see §7). "`rbx` is clobbered" is where the *evidence* stops; naming the clobberer without the monitor would be exactly the guess this project keeps paying for.

## 7. NOT DONE / OWED

- **MONITOR-FIRST NOT DISCHARGED.** The oracle is now present (`/home/claude/x64` cloned this seat, `sbl` runs, `.ref` minted) — that was the blocker s+7 recorded. The 2-way/3-way sync-step monitor was **not run**. **This is the next action** and the witness is small enough to make it cheap.
- **No bisect run.** SCRIP was cloned full-depth here (3148 commits) so it is possible. Use a **product ≥1600** probe — it is 8/8 deterministic; anything in the 1280 band will bisect to noise.
- m4's silent-empty-at-8×8 (§4) is unowned and needs its own rung.
- Watermark not re-proven this seat (no code changed, so nothing to regress; stated plainly rather than implied).

## 8. NEXT, IN ORDER

1. Monitor `rtx_func_11_include.sno` vs SPITBOL → first divergent event.
2. Bisect the ≥1600 probe over the 407-commit range.
3. Mint the m4 8×8 silent-empty divergence as its own witness + rung.

`handoff_status.sh` is the push truth — NOT this document.
