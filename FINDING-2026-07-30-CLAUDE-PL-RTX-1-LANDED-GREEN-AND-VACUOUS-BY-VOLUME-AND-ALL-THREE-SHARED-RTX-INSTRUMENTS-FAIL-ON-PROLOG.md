# FINDING 2026-07-30 — PL-RTX-1 LANDED GREEN AND COMMITS 100% OF ARRIVALS, THE `det_fuse` MYSTERY IS A WRONG-ARM STRUCTURAL FACT NOT AN ELIGIBILITY BUG, AND ALL THREE SHARED RTX INSTRUMENTS FAIL ON PROLOG FOR THREE DIFFERENT REASONS

**Session:** s223-PL · **Ladder:** `GOAL-PROLOG-RTX.md` (`PL-RTX`) · **Contract:** `ARCH-PROLOG-RTX.md`
**SCRIP base:** `b1ca896e` + this session's edits · **RT_OPT = `-O0`** (label every number with it)
**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet

---

## 1. ⭐⭐ RUNG RTX-1-PL LANDED — `rt_proc_call_open_det` IS ASSEMBLY, AND IT EXECUTES

New `src/runtime/rtx/rtx_plcall.S`, new family gate `PLCALL` (`SCRIP_RTX_PLCALL`, default ON), C body
renamed `c_rt_proc_call_open_det`, gate-off tail-jumps to it. **Three of the four C levels are absorbed, so
the success path contains NO CALL:**

- `rt_proc_call_prologue_lex` computes `fbytes` (a max, then a 16-align) and **every caller on this path
  discards it behind a `(void)` cast.** The computation is side-effect-free ⇒ **ELIDED ENTIRELY.** That is
  dead work the C pays on every arrival.
- `rt_pcall_grow` is `if (g_pcall_top < g_pcall_cap) return;` ⇒ inlined as a capacity compare with a **cold
  out-of-line arm**; the frame is built only there, so the hot path is frameless.
- `rt_value_trail_mark` is `{ return g_pl_trail.top; }` ⇒ inlined as one load.

`rt_pcall_grow` was `static` (`nm`: lowercase `t`) hence **unreferenceable from `.S`**; de-static'd to
`visibility("hidden")` — the s187 `rt_nret_fix` precedent, no contract amendment owed.

**LINKAGE SPLIT, READ FROM `rt.o` NOT THE `.so`** (shared §7 0(c), the s209 lesson — the link demotes hidden
globals to lowercase so the `.so` is *structurally incapable* of separating `static` from
`visibility("hidden")`). Measured with `readelf -sW`:
`HIDDEN ⇒ rip-direct`: `g_rt_gen_procs` `g_rt_gen_proc_count` `g_pcall` `g_pcall_top` `g_pcall_cap`
`g_pcall_wires` `rt_k_level` · `DEFAULT ⇒ @GOTPCREL`: `rt_g_want_name` `Σ` `Σlen` `g_pl_trail`.
Disassembly of the linked `.so` confirms it emitted exactly that way.

**EVERY BAKED OFFSET IS ANCHORED BY `_Static_assert` IN THE OWNING TU** — `rt_proc_t.dyn_scope == 80`,
`sizeof(rt_proc_t) == 128` (⇒ `shl 7` stride), `rt_proc_t.frame_bytes == 48`, `rt_pcall_t.rname/save_base/
lex/nargs == 8/28/36/40`, `CALL_ARGS_MAX == 64`, and in `resolution.c` `pl_trail_t.top == 32` +
`sizeof(pl_area_t) == 32`. **The build passing IS the offset verification** — a struct move now breaks the
COMPILE instead of shearing the asm silently.

### GATES
| Gate | Result |
|---|---|
| Prolog watermark, **PRISTINE** | interp **164/164** · compile **164/164**, FAIL=0 |
| Prolog watermark, **port ON** | interp **164/164** · compile **164/164**, FAIL=0 |
| Falsification probe, **m3** | 164/0 → **111/53** |
| Falsification probe, **m4** | 164/0 → **111/53** |
| SNOBOL4 no-regression | **7/0** (m4 hard gate) |
| Icon no-regression | **14/14 m3 + 14/14 m4** |
| Arm census (`queens.pl`) | ENTRIES **12,957** · BAILED_C **0** · COMMITS **12,957** |

⭐ **THE FALSIFICATION PROBE IS THE LOAD-BEARING EVIDENCE, NOT THE GREENNESS.** Per §7 step 2b an unmoved
battery may not be cited as evidence the asm executes. Deliberately breaking the asm moved the Prolog
battery **164/0 → 111/53 in BOTH modes** ⇒ the asm executes, the coverage set is **53 of 164 programs
(32%)**, and **mode 4 is real evidence too** (the s214 "do not close on m3 alone" trap is discharged, not
assumed). SNOBOL4 and Icon are cited ONLY as no-regression evidence for the C-side de-static — which is
exactly the change class they can see.

---

## 2. ⭐⭐ THE OPEN `det_fuse` ITEM (s221 item 8 / proposed RTX-13-PL) IS SETTLED, AND ITS FRAMING WAS WRONG

s221 recorded that `rt_proc_call_open_det0…_det4` measure **ZERO** while generic `_det` measures 430,081,
inferred that `det_fuse` must be false because one of its conjuncts fails, and proposed **RTX-13-PL — fix
the eligibility — as work that would OUTRANK RTX-1-PL** ("a LOWERING fix that beats an ASM fix"). It
explicitly refused to name a cause on a partial read. **Correct refusal; the answer is not on that axis at
all.**

`bb_call_proc_staged.cpp` has **TWO arms that call this symbol, not one:**
1. the **DET arm**, whose chained ternary offers PL-DC → fused `_detN` → generic `_det` (`det_fuse` is
   tested HERE, and only here);
2. **`bcps_spine_gen_arm`, THE GENERATOR ARM**, whose own in-tree comment states that *"every nondet Prolog
   predicate (`app/3`, `nrev/2`, every multi-clause pred) is dispatched HERE"*.

**The generator arm contains no fused family and no `det_fuse` test whatsoever.** Its only choice is
`gi_idx >= 0 ? rt_proc_call_open_det : rt_proc_call_open`. ⇒ **`_det0…_det4` measure zero for a STRUCTURAL
reason — the hot sites never evaluate `det_fuse` at all, because they are emitted by a different function.**
Not an eligibility failure, not the arity conjunct, not the `"$call/N"` synthetic-name hypothesis, not the
frame regime. **RTX-13-PL as written is misconceived**: the work it names ("fix which conjunct fails") has no
referent. The real (and much larger) question is whether the fused family should be extended to the
generator arm — a separate rung, and one whose prize is the ~10M-call nondet path.

⭐ **AND IT RAISES THIS RUNG RATHER THAN LOWERING IT:** the generator arm calls `rt_proc_call_open_det`
**directly and by index**, so RTX-1-PL ports the live arm on the hot path and **cannot be made moot by any
fused-family fix in the det arm.** The EMITTING-TEMPLATE CHECK is what produced this; it would not have been
found by any amount of runtime measurement.

---

## 3. ⛔⛔ THE PERF VERDICT IS A NULL — AND I NEARLY REPORTED A 3.4× WIN

**FIRST MEASUREMENT: `queens.pl` PRISTINE 204 ms → ON 60 ms = 3.4×.** It was **entirely cold page-cache on
the first arm measured.** Warmed and interleaved, the same program reads PRISTINE ~53 / OFF ~51 / ON ~52 ms.
⇒ **the 3.4× was an artifact of measurement ORDER, and nothing but re-measuring caught it.** This is the
`ARCH-SNOBOL4-RTX.md` §7 step 4 instability class, in its most seductive direction: it did not look like a
bad measurement, it looked like a triumph.

**THE HONEST NUMBER, on the longest gradeable Prolog workload (`chat_parser.pl`, ~576 ms, 7 warmed
interleaved rounds, medians, `RT_OPT=-O0`):**

| arm | median | ratio |
|---|---:|---|
| PRISTINE | 576 ms | — |
| OFF | 583 ms | OFF/PRISTINE **0.99×** (kill-switch tax ≈ 0) |
| ON | 569 ms | **ON/PRISTINE 1.01×** |

Within-arm spread is ±6%, so per the contract's own rule (*no two-arm number below ~1.10× is trustworthy*)
**this is a NULL, and per the s187/s204 rule a ~1.00 ON/PRISTINE IS THE ANSWER, not a failed measurement.**

**WHY IT IS NULL — AND THIS IS THE PART THAT MATTERS.** The arm census on the one program it can grade
reports **12,957 arrivals**, against the board's **430,081 for "queens.pl"**. That is a **33× disagreement**,
and the most likely reconciliation is that the two numbers name **two different programs both called
`queens`** (`corpus/programs/prolog/queens.pl`, which I graded, vs. a van Roy `queens_8`/`queensn`, on which
the s221 ranking was built). At ~13,000 arrivals × ~10 instructions saved ≈ 130 k instructions inside a 52 ms
program, **the port is invisible by construction on the workload I could measure.** ⇒ **RTX-1-PL is correct,
green, proven-executing, and VACUOUS-BY-VOLUME on every workload this tree can currently grade.**

---

## 4. ⛔⛔ THE REAL BLOCKER: ALL THREE SHARED RTX INSTRUMENTS FAIL ON PROLOG, FOR THREE DIFFERENT REASONS

The third ladder inherited instruments that were built SNOBOL4-shaped, and **not one of them grades Prolog as
shipped.** This is the ladder's actual governing constraint — more than the SINK collision §SCOPE names.

1. **`test_gate_rtx_killswitch_sets.sh` — hardcoded `find "$DIR" -name '*.sno'`.** It had **NO Prolog and no
   Icon arm at all**, while three ladders are told to gate on it. ✅ **FIXED THIS SESSION**: added a 5th
   parameter `EXT` (default `sno`, so every existing invocation is byte-unmoved); the per-program logic was
   already language-agnostic because first dispatch selects the frontend from the extension. ⚠ **The Prolog
   sweep was LAUNCHED and NOT COMPLETED** — 164 programs × N=4 × 2 arms on a 1-CPU container is ~1,300 runs
   and it was killed to free the CPU for timing. **STILL OWED.**
   ⭐ Note the shape: this is the *same* defect this script documents about ITSELF (s219–s221 recorded
   suite-wide passes that were m3-only while the contract read "both"). A gate that is silently scoped
   narrower than its callers believe, twice, in one file.
2. **`bench_rtx_3arm.sh` — requires a self-timed `ms:` window and NO PROLOG PROGRAM EMITS ONE.** Verified:
   zero matches for `ms:` across `corpus/programs/prolog/*.pl` and the van Roy set. The harness runs, finds
   no window, and prints `NOT GRADED` for every program. ⇒ **the sanctioned 3-arm harness cannot produce a
   single Prolog number today.** The table in §3 is hand-rolled warmed-interleaved wall clock, and is
   labelled as such rather than dressed up as the harness's output.
3. **`util_rtx_arm_census.sh` — SIGABRT (rc=134) under `LD_PRELOAD` on the van Roy benchmarks.**
   Reproduced on **`chat_parser.pl` and `boyer.pl`, 2 of 2 tried**; it works fine on
   `corpus/programs/prolog/queens.pl`. ⇒ **the census cannot grade the very corpus the s221 ranking was
   built from**, so the 2,060,043-arrival board figure **cannot be cross-checked by the census at all**, and
   the 33× discrepancy in §3 cannot be resolved without fixing this. Cause not diagnosed — one session's
   remaining budget went to the port. **This is the next rung.**

⇒ **COMBINED CONSEQUENCE, stated plainly: RTX-1-PL's PERFORMANCE CLAIM IS CURRENTLY UNFALSIFIABLE ON THE
WORKLOADS THAT MOTIVATED IT.** Its CORRECTNESS claim is not — that is fully discharged by the watermark in
both modes plus the both-mode falsification probe plus zero census bails. **The instrument gap is the
finding; the null is a symptom of it.** ⛔ **Do NOT read §3's 1.01× as "the port does not help." Read it as
"this tree cannot yet measure whether it helps," and fix instrument 3 first.**

---

## 5. WHAT THE OTHER TWO LADDERS SHOULD TAKE FROM THIS

- ⛔ **MEASURE WARMED AND INTERLEAVED, OR DO NOT MEASURE.** A 3.4× that is entirely first-arm page-cache is
  reachable in one command. `bench_rtx_3arm.sh` interleaves and discards round 1 — **which is exactly why the
  contract says to use it** — and my hand-rolled substitute only avoided the trap because I re-ran it after
  disbelieving the result. If your ladder ever reports a number from a non-interleaved loop, void it.
- ⭐ **THE EMITTING-TEMPLATE CHECK CAN CHANGE A RUNG'S STORY IN THE OPPOSITE DIRECTION FROM s211's.** s211-ICN
  minted the check because a guard steered arrivals AWAY from the intended arm (port the arm the guard
  rejects). Here the same check found a **second, unguarded, hotter emit site** the ladder did not know
  existed, which made the target *more* valuable and killed a proposed competing rung outright. The check is
  not just a refusal instrument.
- ⭐ **RUN YOUR GATE SCRIPTS' GLOBS BEFORE TRUSTING THEIR VERDICTS.** Two of three shared instruments are
  scoped narrower than their documentation, and both scopings are invisible at the call site.

---

## 6. STATE

**LANDED (local commits only — ⛔ PUSH BLOCKED, CREDENTIAL NEEDED, NOTHING IS ON ORIGIN):**
SCRIP — `src/runtime/rtx/rtx_plcall.S` (new), `src/runtime/rt/rt.c`, `src/runtime/builtins/resolution.c`,
`src/runtime/rtx/rtx_init.c`, `Makefile`, `scripts/test_gate_rtx_killswitch_sets.sh`.
`.github` — this FINDING, `GOAL-PROLOG-RTX.md`, `RTX-CLAIMS.md`.

**OWED, in priority order:**
1. **Diagnose the arm-census SIGABRT on the van Roy corpus** (instrument 3). Until then no Prolog perf claim
   is falsifiable and every ranking on that corpus is single-instrument.
2. Complete `test_gate_rtx_killswitch_sets.sh PLCALL <prolog corpus> 4 both pl`.
3. Reconcile the 12,957 vs 430,081 `queens` discrepancy by naming the exact file each number came from.
4. Give `bench_rtx_3arm.sh` a Prolog-capable timing arm (or self-time the Prolog benchmarks).
5. Then, and only then, decide whether RTX-1-PL stays or is reverted as vacuous — **and note it is currently
   FREE to keep: the kill-switch tax measured 0.99×.**
6. The §SCOPE ruling from Lon is still open and still unblocking (RTX-1-PL never needed it).
