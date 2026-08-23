# ⛔⭐⭐⭐⭐ GOAL-HQ-PERFORM — HEADQUARTERS FOR **SPEED**

**Opened 2026-08-22 s256 by Lon, in-chat, verbatim in substance:** *"the second HQ for SPEED PERFORMANCE for the same three and the same priority."* · The product promise is **TEN TIMES FASTER**.

**Seat root:** `/home/claude_P` · **postoffice identity:** `hq_P` · **twin:** `GOAL-HQ-COMPLETE.md` (`/home/claude_C`, `hq_C`)

## THE ONE QUESTION THIS HQ OWNS

**How many instructions does it take?** Correctness belongs to `hq_C`. ⛔ But **a wrong answer is never a fast answer**: before any number is published, the program's OUTPUT must be verified. beauty mode-3 emits 278 bytes today instead of 40,971 — timing it would show a spectacular speedup for a program that quits after its header.

| | |
|---|---|
| **priority** | **SNOBOL4 #1 · Icon #2 · Prolog #3** |
| **instrument** | **callgrind Ir at FIXED WORK.** Deterministic, layout-immune, load-immune |
| **oracle** | **`/home/resources/spitbol-clean/sbl`** — the s255 benchmark oracle. ⛔ NEVER time against `x64/bin/sbl`: not because its clock is wrong (HQ measured both at ~1.0e9 ticks/sec, both nanoseconds) but because it is **2.30x handicapped** by monitor hooks |
| **authority** | `scripts/lib_oracle_flags.sh` — `sbl_clean_bin()` for timing, `sbl_lang_flags()` → `-bf` for grading |

## ⛔⛔ LON s259: THIS SEAT MEASURES **AND** CURES — **THERE IS NO FLEET. THIS SEAT IS THE ONLY ONE WORKING.**
Verbatim in substance: *"You are the only one working. There is no FLEET."* and, on being told a 25% win was
"dispatched": *"do you mean you told God about it? Or you did something about? … And why is it is not done?"*
⛔ **"Dispatched" means a row in a TSV and a task file. Nobody is working it. Nothing is fixed.** Stop using
the word as if it were an action. **A delegate-only rule presumes a fleet to delegate to; there isn't one. HQ does the
work itself now.**

### ⭐ START HERE NEXT SESSION — THE EDIT POINT IS FOUND, DO NOT RE-DERIVE IT
Worth **~25% of roman** and needs **no semantic ruling** (row `defer-nv-read-by-pointer-not-name`, rank 0).
- `rt_defer_nv_read(const char *name)` (`pattern_match.c:862`) ends in `NV_GET_fn(name)` — a by-name
  resolution on **every** deferred re-read. **140 per iteration** on a pattern with ONE deferred variable,
  because `&ANCHOR = 0` retries at every start position.
- ⭐ **The cacheable thing exists already:** `NV_GET_fn` (`core/core.c`) resolves through
  **`_var_find_cached(name)` → `NV_t *e`**. Cache **that pointer** in the defer read path, keyed on the call
  site's name POINTER, and repeat reads skip the hash+`strcmp` entirely.
- ⛔ **USE THE s258 HARDENING OR REPEAT ITS BUG:** name pointers are **NOT stable** (the runtime passes stack
  buffers) and inserts can shadow — so `strcmp` validation **plus a generation counter**, exactly as the
  shipped `NV_*` memo does at all three insertion sites. The killswitch caught the unsound first draft at
  **335/22 vs 355/2**; run it.
- **Verify before believing:** `make pristine` → `test_corpus_snobol4.sh` (expect m3 355/4, m4 354/3+2SKIP at
  `-O2`) → killswitch A/B → re-measure roman `check: 1102` first, then Ir.

## ⛔ THE LAW BOTH HQs SHARE: **YOU MEASURE *AND* YOU CURE** (Lon s259)

Build, run, profile, bisect — all of it. **And when a measurement becomes a DEFECT, fix it.** The bug stops with the seat that finds it.

## ⭐⭐⭐ RUNG P-0 — THE MAP IS ALREADY DRAWN. START FROM IT, DO NOT RE-DERIVE IT

Measured s256, identical fixed work, both engines, `make pristine` EXIT=0 at `2659558e`, **RT_OPT=`-O0`**, SCRIP mode-4 native binary (**compile excluded by construction** — Lon: *"Worry not about compile time. We are zooming on runtime."*):

| workload | Ir/iter SCRIP | Ir/iter SPITBOL | verdict |
|---|---|---|---|
| `var_access` | 529 | 808 | **SCRIP 1.52x FASTER** |
| `arith_loop` | 398 | 439 | **SCRIP 1.10x FASTER** |
| `table_access` | 997,130 | 359,532 | 2.8x slower |
| `string_manip` | 3,123 | 842 | 3.7x slower |
| `roman` | **67,170** | 7,966 | ⛔ **8.4x slower** |
| **beauty runtime** | 2,129,544,838 Ir | 228,082,817 Ir | ⛔ **9.34x slower** |

⭐ **THE SHAPE, AND IT IS THE WHOLE STRATEGY: SCRIP is good at exactly what real programs don't do, and bad at exactly what they do.** Scalar and register-resident work — the BB codegen — genuinely beats SPITBOL. Tables, strings, and whole realistic programs lose by 3–8x.

⭐ **THE 10x IS NOT BLOCKED ON CODEGEN.** Emitted code already wins where measured directly. **Every remaining multiple lives in the RUNTIME SERVICES the emitted code calls out to.** Further box-template tuning improves the one bucket already winning. (⚠️ The older *"emitted code is 0.64% of Ir"* ranking remains true for the compile-dominated m3 beauty measurement it was taken on — it is not the general fact.)

⛔ **`roman` IS THE FIRST TARGET, NOT beauty.** 8.4x and 9.34x are the same program shape (string + pattern + table) giving the same answer; `roman` is far smaller, fixed-work reproducible, and almost certainly shares beauty's dominant cost. Rows: `perf-roman-8x` · `perf-table-array-runtime` · `perf-string-runtime` — all three are **row factories** (rank buckets, mint rows, cure nothing).

## ⛔⛔ HOW TO MEASURE — THE OLD HQ PUBLISHED A WRONG TABLE BY IGNORING THIS

**`harness.inc` has TWO MODES and they answer different questions** (both landed 12:05–12:59 s256, all four oracle×mode cells verified working):

| mode | how | reports | use it for |
|---|---|---|---|
| **TIME** | stdin `/dev/null` | `iters` in a fixed ~500 ms budget | *is it alive* |
| **FIXED-WORK** | stdin = **N** (`fixed_n = INPUT`) | time for exactly N iterations | *is it fast* — pair with callgrind |

1. ⛔ **`ms` IS CONSTANT BY CONSTRUCTION in TIME mode.** HQ's first table read 510–615 ms across fifteen unrelated workloads — that is the `ZBUD` budget, not a result. The real spread hides in `iters`: `arith_loop` 39,845,888 vs `table_access` 3,072, a **13,000x range** behind fifteen identical-looking times. This is the "plausible false table" `bench-harness-unmeasurable` was raised about.
2. ⛔ **TIME-mode `iters` IS UNQUOTABLE ON A LOADED MACHINE.** With 16 seats building, back-to-back runs swung **2x** (`arith_loop` 46,137,344 then 18,874,368) — turning a real **1.10x into a flattering 4.88x**. The wall-clock table said SCRIP was 3–5x faster on its best kernels; deterministic Ir said 1.1–1.5x.
3. ⭐ **EVERY PUBLISHED RATIO MUST BE FIXED-WORK Ir, AND EVERY NUMBER MUST CARRY ITS `RT_OPT`.** O0-DEV-O2-BENCH: `-O0` is the dev default, `-O2` passed explicitly for benchmark runs. A benchmark quoted without its RT_OPT is not comparable.
4. ⛔ **VERIFY THE OUTPUT BEFORE BELIEVING THE NUMBER.**

## WHAT ONE FLEET-DAY ACTUALLY BOUGHT — the honest baseline this HQ inherits

Identical method both ends (9am tree built in an isolated worktree, same fixed work, same callgrind):

| workload | 09:00 | s256 | delta |
|---|---|---|---|
| **beauty self-host runtime** | 4,811,232,217 | 2,129,544,838 | **2.26x** |
| `roman` | 1,360,546,795 | 1,343,411,963 | **1.01x** |
| `arith_loop` | 79,486,556 | 79,507,515 | **0.99x** |
| `string_manip` | 62,919,777 | 62,457,691 | **1.00x** |

⛔ **One workload moved and every other stayed flat.** The day's gain was `byname-bake-cell-address` (`8c1f2d41`), which cures by-name procedure resolution — beauty does that constantly, the kernels barely at all. ⭐ **THE LESSON THAT JUSTIFIES THIS HQ EXISTING: a fleet optimizing whatever the flagship happens to stress is not a performance campaign.** This seat's job is to make sure the OTHER workloads move too.

## KNOWN INSTRUMENT GAPS — do not build a strategy on an unverifiable number

- ⛔ **HARDWARE COUNTERS DO NOT WORK HERE** (seat2: perf unusable for IPC/branch-miss). Everything is Ir. **And a load-bearing claim depends on exactly that blind spot:** the s251 board asserts SCRIP is *instruction-count bound* at **IPC 3.20 vs 2.33**, and `ARCH-PERF-TOOLING` §7 builds a **1.4x asm ceiling** on it. Neither is currently reproducible. Row `perf-tooling-hardware-counters`. **Until it is checked, label that ceiling UNVERIFIED wherever it appears.**
- **The 1,426x compile figure** (SCRIP 12,995,512,724 Ir vs SPITBOL 9,113,074 to compile beauty) is a **recorded fact, NOT a campaign** — Lon s256 de-prioritised compile time explicitly.
- **The perf board is dead arithmetic:** ~20 rows were ranked against a profile whose #1 item (43.8% of all instructions) no longer exists, against a denominator 2.30x off. Rows `perf-board-rebaseline` · `reprofile-after-byname-bake`.

## SESSION SETUP

```bash
cd /home/claude_P && for r in SCRIP corpus .github; do git -C $r fetch -q origin && git -C $r merge --ff-only origin/main; done
bash SCRIP/scripts/s4e_msg.sh check                       # hq_P inbox
ls /home/resources/spitbol-clean/sbl                      # the BENCHMARK oracle -- absent = every number false
cd SCRIP && make pristine                                 # HQ-27
# fixed-work + callgrind, the only quotable arm:
#   echo <N> | valgrind --tool=callgrind ./prog.bin
```

## ⛔⭐⭐⭐⭐ LON s258 — NO FLEET. TWO HQs ONLY. (routed same session, LOOP law 6)

**Lon, in-chat, verbatim in substance:** *"Just so we are clear we are run only duo here, no FLEET, just 2 HQ's."*

⛔ **THE CONSEQUENCE, STATED PLAINLY: A DELEGATE-ONLY RULE HAS NO RECEIVER.** That rule (Lon s256) was
written for an HQ commanding 16 seats, and its own one-line test was *"does this end in a brief in a seat's
inbox?"* With no fleet there is no inbox to end in. Held literally it now guarantees that **nothing is ever
fixed** — it would convert this seat into a generator of perfectly-documented queue rows nobody works.

⭐ **OPERATING ASSUMPTION UNTIL LON SAYS OTHERWISE: the two HQs DO the work.** hq_P measures and then CURES in
the performance lane; hq_C holds the correctness gates (the SNOBOL4 blocking set) and cures in its own. The
cross-HQ interlock survives unchanged and is now the *only* division that matters: a perf change that moves an
oracle diff is hq_C's red, and the work stops until it is green.

⛔ **WHAT IS NOW MOOT** (do not spend another minute on it): the firing gate, the 16 `tasks/*.task.md` files
(item 5), the 8/8 seat→HQ split for `$PO/<seat>/HQ`, and `fleet` on a cadence. ⭐ **WHAT SURVIVES AND EARNED ITS
KEEP:** the postoffice itself is the two HQs' working bus — hq_C and hq_P used it productively across s258
(cross-verification both ways, V2-1 sign-off, the correctness-lane handoff) — and the drain cleared 29 real
questions left by earlier sessions.

⛔ **THE FOUR ROWS MINTED THIS SESSION HAVE NO WORKER**, so they are not dispatch rows any more; they are this
seat's own worklist, in this order once P-0 lands: `zeta-frame-rsp-capture-home`, `zeta-cell-heap-segv` (both
hq_P), `rtx-icnnum-icnsub-bail-invariant` (design answer first), and `opt0-define-beta-link` (hq_C's lane).
Likewise the four rulings sent to seat06/seat08/seat13/seat15 were delivered to mailboxes nobody will read —
their SUBSTANCE is preserved in this file's STANDING RULINGS section, which is now the only live copy.

## ⛔⭐⭐⭐ LON s258 REFOCUS — THE RUNTIME IS THE TARGET (routed the session it landed, LOOP law 6)

**Lon, in-chat, verbatim in substance:** *"you said the main optimizations needed now are ALL in the RUNTIME. So we
should refocus. Is not the task rewrite RT in highly optimized register aware ASM with R10 and R11 and no RTCC
VENEER. And TABLE and ARRAY rewritten. That was supposed to happen today, but that was a fiasco."*

⭐ **THE REFOCUS IS ACCEPTED AND IT IS THIS FILE'S OWN RULING** — *the 10x is not blocked on codegen; every remaining
multiple lives in the runtime services the emitted code calls out to.* Two design questions (box-fusion, a standalone
peephole) were allowed to pull focus off it in one session; that stops here. **The named work is the standing goal:**
`GOAL-RTCC.md` (veneer at every C-RT boundary, claim the caller-saved GPRs as VM globals) plus a TABLE/ARRAY rewrite.

⛔ **AND THE FIASCO IS NAMED, because it was a DISPATCH failure, not a technical one.** The fleet-day moved beauty
runtime 2.26x and moved `roman` 1.01x, `arith_loop` 0.99x, `string_manip` 1.00x — one workload, because the one real
win cured by-name resolution, which the flagship does constantly and the kernels barely at all. Meanwhile seat08's
`rung-A2-rtx-icon-family` ended with a **complete register-liveness analysis of all 5 files and ZERO code touched**.
hq_P's s258 ruling refused only `rtx_icnnum.S`/`rtx_icnsub.S` (bail-safety invariant, unverifiable by a corpus that
exercises error paths thinly); `rtx_icnrel.S` (13 sites) and `rtx_icnvar.S` (11 sites) were LOW RISK and *ready as
analysed* and should have landed anyway. **A row that produces an analysis and no diff is a row that did not run.**

## ⛔ THE ONE FORK THE PROFILE MUST SETTLE BEFORE WEEKS ARE SPENT — registers vs algorithms

Lon's task list bundles two different cures with very different ceilings, and **Ir-per-call separates them**:

- **call-boundary work** (free r10/r11, drop the RTCC veneer, hand-ASM the leaves) pays off when the top functions show
  **LOW Ir-per-call and HUGE call counts**. Bounded: a spill/reload pair is ~2 instructions; hand-ASM over `-O2` C
  typically buys 1.2–2x on hot leaves. It optimises **the cost of CROSSING INTO** the runtime.
- **data-structure / engine work** (TABLE, ARRAY, the pattern engine) pays off when the top functions show **HIGH
  Ir-per-call**. Unbounded, and the precedent is in this file: `bb_ab_slot_for` at **22,089 Ir per procedure call** was
  a linear scan. It optimises **what happens once INSIDE**. ⛔ Hand-written assembly makes a linear scan a faster
  linear scan.

⛔ **AND THE MEASUREMENT TRAP THAT WOULD SEND US THE WRONG WAY:** `RT_OPT` defaults to `-O0`. Profiling the runtime at
`-O0` and concluding *"the C runtime is slow, rewrite it in ASM"* measures **the compiler flag, not the language** —
`-O0` C runs 2–4x slower than `-O2`. Every RT-vs-ASM comparison is `-O2` only (O0-DEV-O2-BENCH).

## ⭐ HYPOTHESIS FROM THE WORKLOAD SOURCES (hq_P s258 — marked HYPOTHESIS per LAW 0; the profile confirms or kills it)

Derived by reading the two kernels, arithmetic shown so anyone can recompute it:

- **`table_access` is not measuring lookup.** `T = TABLE(512)` sits **inside** the loop, so each iteration is one
  512-bucket allocation plus 500 stores and 500 fetches. **997,130 Ir ÷ ~1000 ops ≈ 997 Ir per operation**, against
  SPITBOL's ~360. Both are far too high for a hashed store, which points at **allocation strategy** (eager zeroing of
  512 buckets vs lazy) rather than hashing — and neither registers nor hand-ASM touch that.
- **`roman` is a pattern-engine workload, not a dispatch workload.** ~4 recursion levels × (2 pattern matches +
  1 `REPLACE`) ≈ 12 string/pattern operations per iteration ⇒ **67,170 ÷ 12 ≈ 5,600 Ir per pattern operation**, against
  SPITBOL's ~660. 5,600 instructions to match a pattern against a ≤40-character string is not a register-pressure
  number.
- **It unifies the losers:** `roman` 8.4x, `string_manip` 3.7x, beauty 9.34x are all pattern/string; the two winners,
  `var_access` 1.52x and `arith_loop` 1.10x, touch neither engine.

**If this holds, the highest-value RT target is the pattern/string engine and the allocator, with the call-boundary
work second.** If the profile shows low Ir-per-call and enormous call counts instead, Lon's ordering is right as
written and the veneer/register work leads. ⛔ **Nobody spends a week on either until the profile says which.**

## ⭐ STANDING RULINGS FROM THIS SEAT (routed here the session they were made — the chat is not the record)

### ⛔ RULING s258 — BOX-FUSION RUNG 1 IS ON HOLD, WITH A COMPUTED RE-ENTRY CONDITION
Asked by **seat06 and seat15 independently, on the same row, after three prior escalations that never landed.**
Their measurements are ACCEPTED IN FULL and are why the row survives: seat15 — `(ASSIGN,BINOP,LIT_INTEGER,VAR)`
same-name self-update is the most frequent ≥3-box chain in real BM-4 grammars (**45/765 stmts, 5.9%**), and the
dead templates `bb_binop_gvar_arith[_slot].cpp` stop at an operand slot without folding back into the GVA cell,
so wiring them as-is buys 3→2 boxes, not s250's 4→1. seat06 — on `arith_loop.sno` emitted-box share is **29.18%**
of Ir and the fusion-target statement alone is **4.49–15.11%** of kernel Ir, two instruments agreeing to within
3%; and the old **0.64% demotion basis was beauty self-host, which is COMPILE-dominated** and therefore the wrong
denominator. All of that stands.

⛔ **It still waits, and one number decides it:** `arith_loop` is **398 Ir/iter SCRIP vs 439 SPITBOL — already
1.10x FASTER**, and `var_access` 1.52x faster. The buckets that LOSE are `roman` 8.4x, `string_manip` 3.7x,
`table_access` 2.8x, beauty runtime 9.34x. Box fusion is further box-template tuning on **the one bucket already
winning**. Grant it its best case, the full 15.11%, and `arith_loop` goes 1.10x → ~1.29x while `roman` stays 8.4x
adrift of a 2–3x product target — and the cost is a NEW optimizer pass plus a new fused op+literal IR opcode plus
a completed write-back arm, spent on the winning bucket while the losing buckets have not been profiled once.
That is this HQ's founding lesson restated: *a fleet optimizing whatever the flagship happens to stress is not a
performance campaign* — and neither is one optimizing the kernel that already wins.

⭐ **RE-ENTRY, COMPUTED, so nobody asks a fourth time.** Box-fusion rung 1 fires the moment EITHER **(a)** `roman`'s
Ir/iter comes within **2x** of clean SPITBOL — the runtime-services gap is closed and emitted code becomes the top
bucket — OR **(b)** a fixed-work callgrind profile of whichever workload is then furthest from its PLAN.md TARGET
shows **emitted-box Ir > 50%** of total. Both are commands. Either green ⇒ dispatch without further debate.

### ⛔ RULING s258 — NO PERF CLAIM MAY CITE A ζ-STORAGE COMPARISON WHILE THE AXIS IS RED
Of the four `ZC_STORAGE` configs: `frame-r12` retired, `frame-rsp` **aborts on beauty**, `cell-heap` **SIGSEGVs on
roman**, `cell-stack` (the default) solid. **One working arm.** A config delta measured against a crashing arm is
not a measurement. Rows `zeta-frame-rsp-capture-home` + `zeta-cell-heap-segv` (both rank 0, hq_P) lift this.
Evidence: `FINDING-2026-08-22-hq_P-the-zeta-ab-axis-has-one-working-arm.md`.

### ⛔ RULING s258 — THE `rtx_icnnum.S` BAIL-SAFETY INVARIANT IS NOT NEGOTIABLE FOR A REGISTER-LIBERATION ROW
seat08's `rung-A2-rtx-icon-family`: land `rtx_icnrel.S` (13 sites) and `rtx_icnvar.S` (11 sites), both LOW RISK and
ready as analysed, plus `rtx_icnagg.S`'s single spill with the matching `add rsp` before **all three** exits. Refuse
`rtx_icnnum.S` and `rtx_icnsub.S` on this row. Reason: a bail is an **error path**, the corpus exercises error paths
thinly, so a green corpus would NOT be evidence that multi-exit `rsp` bookkeeping is safe — a blind instrument, and
no DONE-WHEN may rest on one. Split to row `rtx-icnnum-icnsub-bail-invariant`, whose first deliverable is a DESIGN
answer (can an xmm packing satisfy `SCAN_SIMPLE_INT` without touching `rsp`), not an edit.
⭐ Escalated to `ceo`: SNOBOL4-FIRST says never run the Icon check scripts, PLAN.md s257 gives Icon a ruled numeric
target — an Icon row therefore has no sanctioned instrument. Topic `escalate-icon-checks-vs-icon-target`.

## LIVE CURSOR — hq_P

**s261 (2026-08-23) — ✅ ROMAN CUT 56.3%, SIX CURES, ALL PUSHED. THE DEFER PATH NOW MAKES NO CALL AT ALL.**

⭐ **THIS SEAT MEASURES *AND* CURES.** (Lon s261 — see the section above and
`RULES.md` §§ THE TWO MODES / MEASURE AND CURE). **We are in DUO MODE and DUO IS THE DEFAULT**: Lon watching, two
HQs, ceo. There is no fleet to delegate to, so **filing a queue row is not a deliverable — it is the shape of not
doing the work.**

### ✅ ROMAN — `bash /tmp/.../rig/roman_ir.sh <tag> 2000` (rig is scratch; rebuild it from the recipe below)
| arm | Ir @ N=2000 | Ir/iter |
|---|---|---|
| baseline `f4657712` | 80,371,475 | 40,186 |
| `97ef3c3a` FAIL-strcmp guard | 77,638,799 | 38,819 |
| `454b5190` one resolution, not two | 62,788,744 | 31,394 |
| `f8081604` drop the unobservable dfx frame | 54,315,629 | 27,157 |
| `a16598a2` cache the cell (SPITBOL vrblk) | 47,143,490 | 23,571 |
| `84aaef7e` **inline the read into emitted code** | **35,130,646** | **17,565** |

**−56.3% cumulative. vs the clean oracle (7,966 Ir/iter): 6.58x → 2.21x.** `check: 1102` on every arm.
Killswitches: `SCRIP_DEFER_MERGE=0` (runtime) · `SCRIP_DEFER_INLINE=0` (⛔ **EMIT-time — must be re-COMPILED,
toggling it on a baked binary proves nothing**). Full detail:
`FINDING-2026-08-22-hq_P-roman-defer-path-cut-32-percent-three-cures.md` (extended with the s261 continuation).

### ⭐ NEXT ROW — NAMED, SIZED, AND IT HAS A WORKED EXAMPLE
**`NV_SET_fn` is ~8% of roman and it is the SAME by-name defect on the WRITE side** (`rt_dcap_pump` 3.82% ·
below-main 1.87% · `rt_match_replace` 1.43% · its strcmp 1.10%). The read-side cure is already worked twice —
`a16598a2` caches the stable cell per site in a **self-validating (key,cell) pair** (a slot collision misses and
re-resolves; it can never hand one site another's cell), and `84aaef7e` then removes the call entirely. Apply the
same shape to the store path. After that the defer cluster is no longer #1 — **our own emitted code is, at 21.4%**.

### ⛔ THREE THINGS THE NEXT SESSION MUST NOT RE-DERIVE
1. **`demo_calculator_1` is a known `-O2`-ONLY red, NOT a regression.** hq_C adjudicated it: the compiler is
   hardcoded `-O0` and ignores `RT_OPT`, so codegen is identical across arms — it is an RT_OPT split.
   **`53819b4a` is CLEARED; do not revert it.** ⛔ Lon: *"Do NOT fix -O2 bug for BEAUTY. Do not care. Next."*
   The `-O2` fail-set is `160_pat_alt_inner_gen_resume` · `161_pat_defer_fn_nested_match` · `demo_treebank` ·
   `demo_porter` · `demo_calculator_1`; m3 354/359, m4 353/359 + 2 SKIP.
2. **VERIFY REGISTER MAPS, DO NOT ASSUME THEM.** This seat asserted one in `bb_match_defer` and was wrong (the
   hot deferred name is `PATV$0`, a compiler-generated marshalling variable, **not `T`**). The inline arm's map is
   sourced from `bb_match_break`'s emitted scan — `movsxd rcx,r14d / cmp ecx,r15d / movzx esi,byte ptr [r13+rcx]`
   ⇒ **r13 = subject, r14d = cursor, r15d = length.**
3. **`g_sno_defer_cells` is now SHARED:** lower half (< 2048) = the DTP cache (`ci`), upper half = the merged
   arm's (key,cell) pairs at `2048 + msite*2`. The `ci` bound was tightened 4096 → 2048 for exactly this reason.

### RIG RECIPE (scratch is not durable — rebuild it)
`./scrip --compile -o r.s corpus/benchmarks/snobol4/roman.sno` → `gcc -no-pie r.s -o r -Lout -lscrip_rt -lm -lpthread`
→ `valgrind --tool=callgrind --separate-callers=2 ./r <<< 2000`. ⛔ **REFUSE to print an Ir number unless the
output is exactly `check: 1102`** — a broken program is fast.

---

**s259 (2026-08-22) — ✅ PRE-FLIGHT COMPLETE, 8/8, COMPUTED BY A GATE. V2-6 (Lon's flip) is the only rung left.**

### ✅ PRE-FLIGHT — `bash SCRIP/scripts/test_gate_preflight_complete.sh` (exit 0), re-checkable in ONE command
Phase 0: V2-1 picker · V2-2 queue purge (0 malformed, 0 blank) · V2-3 banner · V2-4 identity ·
**V2-2 batons: 86/86 DONE-WHENs runnable, top-16 DEMONSTRATED able to say NO.**
Firing gate: **fleet Q=0** · **every seat resolves a `-bf`-capable oracle** · **hq_P repos clean and pushed.**
⭐ **Four things "85 batons exist" was hiding, each invisible to the one before:** 34 criteria were PROSE
(permanently uncloseable) · 18 hardcoded `/home/claude_C` (a seat would grade its own row against hq_C's tree
— a false GREEN) · 9 `cd`-ed away from the root so they could only exit **127** (⛔ **my own regression from
fixing the previous layer**) · **8 of 16 seat dirs had NO ORACLE**, which would have printed false all-FAIL
tables across half the fleet.

### ✅ ASSET ROOT — ONE clone, no symlinks, no copies (Lon s259)
`S4A="${S4E_ASSETS:-… || echo /home/resources}"` — changed **only the fallback** in the 54 scripts that
already had the override. ONE real `snobol4ever/x64` at `/home/resources/x64` (57M, was ~1.1G over 19 copies);
**zero symlinks**; seats carry only `.github`/`SCRIP`/`corpus` (D-17b). Renamed by role because the old names
lied: `spitbol-pristine` (0 modified files) · `spitbol-bench-oracle` (4 — NOT clean).
⛔ **Trap cured:** three binaries here reject `-f`, so under the mandatory `-bf` they reject EVERY program.
`lib_oracle_flags.sh` now REFUSES a `-f`-incapable binary (`sbl_bf_capable`/`sbl_assert_bf`); gated by
`test_gate_oracle_bf_capable.sh`. ⛔ **`RULES.md:65` still names the trap — needs ceo/Lon, not us.**

### ⭐ SPEED — stated without flattery
roman, `-O2`, fixed work, output verified `check: 1102`, **both engines measured the same way this session**:
**7.08x slower → 5.87x slower = 1.21x faster, −17.1% Ir.** That gain is the **s258** `NV_*` memo — **this
session landed NO speed cure.** Target is **10x FASTER**; we are **59x** away.
⛔ **A cure was tried, MEASURED WORSE, and REVERTED:** replacing libc `strcmp` on the memo hit path with an
inline byte loop moved `strcmp` 10.91%→3.63% but `NV_GET_fn` **21.04%→32.59%**, net **+7.7%**
(43,479→46,819 Ir/iter). Baseline restored exactly. ⛔ **AVX2 `strcmp` beats a naive loop even on
one-character names — do not start there again.**
⭐ **THE 54%:** one deferred node (the bare `T`) is **54.2%** of roman; our emitted code is **12.96%**.
Scoreboard: SCRIP wins **6 of 17** (`fibonacci` 0.60); `mixed_workload` **2.95x** is the fair single number.
⛔ **SCRIP SCALES WORSE** — per-iteration cost grows **1.50x** where SPITBOL's grows **1.25x**, so the gap
**WIDENS** with input size and small benchmarks understate the deficit.

### ⭐ NEXT SESSION STARTS AT THE EDIT, NOT THE ANALYSIS
`defer-nv-read-by-pointer-not-name` (rank 0), ~25% of roman, **no semantic ruling needed**. Edit point,
already located: `rt_defer_nv_read` (`pattern_match.c:862`) ends in `NV_GET_fn(name)` — 140 by-name
resolutions per iteration. `NV_GET_fn` resolves via **`_var_find_cached(name)` → `NV_t *e`**; cache **that
pointer** in the defer read path, keyed on the call site's name pointer.
⛔ Name pointers are **NOT stable** — use `strcmp` validation **plus the generation counter**, exactly as the
shipped memo does at all three insertion sites, and **run the killswitch** (it caught the unsound s258 draft
at 335/22 vs 355/2). Verify: `make pristine` → corpus (m3 355/4, m4 354/3+2SKIP at `-O2`) → killswitch A/B →
roman `check: 1102` **before** believing any Ir number.
⛔ **The WIDE cure (don't defer a bare `TT_VAR`, `lower_snobol4.c:1398`, up to 54%) is hq_C's ruling, not ours.**


## ⛔⭐ LON OVERRIDE s260 — THIS SEAT IS CURING, NOT ONLY MEASURING

**Lon, in-chat 2026-08-22 s260, verbatim: "Target ROMAN. Run in a loop. Find the biggest bottleneck, then fix.
Rinse, repeat."** Also ruled the same message: this seat runs in **DUO mode** — hq_P (PERFORMANCE) alongside
hq_C (CORRECTNESS) and ceo.

⭐ **This SUSPENDS the delegate-only rule for the ROMAN row.** That rule (Lon s256) said HQ may build,
run, profile and bisect but must convert every defect into a queue row and a brief rather than an edit.
Lon has now told this seat directly to **fix**, on a named target, in a loop. Per RULES.md/THE LOOP clause 6
(*"IF LON TELLS YOU SOMETHING THAT CONTRADICTS YOUR BRIEF, LON WINS — THEN YOU MUST TELL HQ"*), the override
is taken IMMEDIATELY and routed here in the same session. Scope of the suspension, stated narrowly so it is
not read wider than it is: **the ROMAN speed row on this seat.** It is not a general repeal for hq_P, and
nothing here changes the interlock — a wrong ANSWER remains hq_C's under their s259 standing order.

## ⛔⛔⭐ YOU MEASURE **AND** YOU CURE — LON s261, AND IT SUPERSEDES MY OWN NOTE ABOVE

**Lon, in-chat 2026-08-23 s261:**

> … Tag you are it. Did I mention you are in DUO mode. I do
> not want to here about you not fixing the bugs. You will measure. You will cure. Make note and tell the
> CORRECTNESS seat through your comm channel, post office, this exact message. Let's see if this system works.

⛔ **THIS CORRECTS THE SECTION IMMEDIATELY ABOVE, WHICH I WROTE AND WHICH WAS WRONG.** At s260 I recorded Lon's
"then fix" as a *narrow suspension* — "the ROMAN speed row on this seat... not a general repeal." Lon has now said
plainly that it is general. **The law is repealed, not suspended:** hq_P measures AND cures, full stop, on every
row, not only ROMAN. "You will measure. You will cure." There is no longer an HQ-may-not-edit rule to route
around, and *"I do not want to hear about you not fixing the bugs"* forecloses converting a defect into a queue row
as a way of not fixing it.

⭐ **WHAT SURVIVES, because Lon did not touch it.** The two-HQ interlock is unchanged: a **wrong ANSWER** is still
hq_C's under their s259 standing order, and this seat still sends bugs the moment it sees them rather than working
around them. Repealing "HQ may not cure" is not a licence to cure in the other seat's lane. Delegation to the 16
worker seats also survives as a *capacity* choice — it is no longer a *permission* boundary.

⛔ **STILL BINDING AND UNCHANGED BY THIS:** NO-NEW-GLOBALS without an in-chat banner grant · PUSH-BEFORE-DISPATCH ·
PULL-BEFORE-TRUST · VERIFY-BEFORE-QUOTE · the chat is not the record · no broken commits · a killswitch and a
control arm on every performance claim.

**Routed the same session** per THE LOOP clause 6, and sent to `hq_C` verbatim as Lon instructed, plus a note to
`ceo` because this repeals a standing HQ law that ARCH-FLEET-CEO says only CEO lands — CEO is being told what Lon
already ruled, not asked to approve it.
