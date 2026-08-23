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

## ⛔ THE LAW BOTH HQs SHARE: MEASURE FREELY, CURE NEVER

Build, run, profile, bisect — all of it. **The moment a measurement becomes a DEFECT it becomes a row and a brief, never an edit.**

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

⛔ **THE CONSEQUENCE, STATED PLAINLY: `MEASURE FREELY, CURE NEVER` HAS NO RECEIVER.** That law (Lon s256) was
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

**s258 (2026-08-22) — P-0 ANSWERED AND THE FIRST CURE LANDED. Sovereign question moved 6.58x → measurably better; exact `-O2` number PENDING (command below).**

### ✅ LANDED AND PUSHED
- **Preflight V2-3 + V2-4** (SCRIP `8e2fb884`, `3f951354`) — identity asserted not globbed, `.msg.*` orphan sweep,
  `/home/claude`→`ceo`, census by mailbox with a MAIL column, HQ drain refusal, board age+topic. Gate
  `test_gate_postoffice_identity.sh` **18/0 current vs 3/15 pre-patch**, subject redirectable via `S4E_MSG_BIN`.
- **Legacy `hq` drained 29 → 0**; phantom `claude01/` retired; a 46-hour orphan delivered. `fleet` shows **Q=0**.
- **hq_C cross-verified BOTH WAYS** — V2-1 ✅ (rank inversion, assign-beats-free, both refusals), V2-2 ✅ (0 rows
  swept without a `DONE` marker). hq_C signed off my V2-4 and caught a real defect in my gate (hardcoded subject).
- ⭐ **RUNG P-0 ANSWERED** — `FINDING-2026-08-22-hq_P-roman-is-44-percent-variable-name-lookup-not-registers.md`.
  `roman` `-O2` **50,648 Ir/iter vs clean SPITBOL 7,966 = 6.36x** (m4), output verified `check: 1102` both engines.
  **NO linear scan anywhere — every Ir/call 20–80.** The defect was call COUNT: 159 variable lookups and 250
  `strcmp` per iteration. Emitted code is only **11.8%**; the gap is entirely runtime services.
- ⭐ **FIRST CURE LANDED** (SCRIP `db8f96d6`) — the NV_* memo, SPITBOL's `vrblk` discipline applied to `NV_t`.
  Corpus **m3 357/2, m4 355/2+2SKIP**, identical to the killswitch control; both blocking gates green.
  ⛔ **Its killswitch caught an unsound first draft (335/22 vs 355/2)** — name pointers are NOT stable (the runtime
  passes stack buffers) and inserts can shadow. Cured with `strcmp` validation + a generation counter at **all three**
  insertion sites. **NEW GLOBALS granted by Lon in-chat s258.**

### ⛔ THE ONE THING OWED — 5 MINUTES, DO IT FIRST
The `-O2` re-measure of the **hardened** memo. The 25.2% / 39,255 Ir-per-iter figure in circulation belongs to the
**unsound draft**; the shipped version pays a `strcmp` per hit, so the real number is lower and is **not yet taken**.
An `-O2 pristine` was in flight when the session ended (a partially-built `out/` may be on disk — rebuild, do not trust it).
```bash
cd /home/claude_P/SCRIP && RT_OPT="-O2 -g -fno-strict-aliasing -fwrapv -fno-omit-frame-pointer" make pristine
cd ../corpus/benchmarks/snobol4 && echo 20000 | valgrind --tool=callgrind ./…/scrip roman.sno   # must print check: 1102
# baseline to beat: 1,049,108,015 Ir (52,455/iter, 6.58x).  Publish with RT_OPT, never without.
```

### ⭐ NEXT RUNG — ONE CALL SITE WORTH 29.8%
`c_rt_defer_close` 11.60% + `rt_defer_run_all` 8.40% + `rt_defer_get_pat_dtp` 6.26% + `rt_dfx_push` 3.58%, each called
**exactly 1,403,811 times** (70/iteration) — one fixed pipeline, now **larger than our emitted code (15.77%)**.
`roman.s` has **exactly one** defer site, `n44_match_defer`: the bare `T` in `'0,1I,…' T BREAK(',') . T`, re-read at
every unanchored start position.
⛔ **CORRECTNESS FIRST, AND IT IS hq_C's CALL.** §7 of `REFERENCE-SPITBOL-BEAUTY-CONSTRUCTS.md`: deferral is what
`*expr` MEANS; a bare variable is evaluated at construction. `lower_snobol4.c:1398` lowers `case TT_VAR:` straight to
`IR_MATCH_DEFER`. If a pattern assigns the variable mid-match (beauty's `NRETURN` idiom), SPITBOL matches the
already-built pattern and we would not. Answers agree today (`check: 1102`), so it is conservative deferral, not a
wrong answer. **No unilateral change from this seat.**
⭐ Three mechanisms already in the tree bypass the defer and none reaches this case: `cx->pre[]`
(`lower_snobol4.c:1399`, consumed :1842 → `PATV$n`, `pat_static=1`) · `SCRIP_PAT_INLINE`+`sno_fz_tree()` (needs a
pattern value; `T` holds a string) · ⭐ **`&user_defined_constants` (Lon s258)** — `lower_snobol4.c:1393` folds a
sealed `&NAME` via `sno_const_val`/`sno_const_pat` against `g_sno_seal[]` and never reaches `IR_MATCH_DEFER`.
⛔ It cannot help `roman`'s `T` (capture target, genuinely varies, sealing → error 341); **it pays on variables
assigned once and thereafter only read — beauty's `*Expr0…*Expr17` grammar is the textbook case.**

### ⛔ STANDING CONSTRAINTS
- **NO BEAUTY NUMBER AT `-O2`.** hq_C measured C-0 reopening at `-O2` (both media 278 bytes, md5 `1c75f97d`,
  byte-identical to the pre-cure failure) while `-O0` self-hosts correctly at 40,971. The inherited
  **2,129,544,838 Ir figure is VOID if it was taken at `-O2`**. Date every beauty number by commit AND RT_OPT.
- **No perf claim may cite a ζ-storage comparison** while `zeta-frame-rsp-capture-home` / `zeta-cell-heap-segv` are red.
- Rows owned here: those two (rank 0) + `rtx-icnnum-icnsub-bail-invariant` (rank 2, design answer before any edit).
  `opt0-define-beta-link` is hq_C's via the interlock. **No fleet — these are this seat's own worklist (Lon s258).**
- Open with `ceo`: `escalate-icon-checks-vs-icon-target` (SNOBOL4-FIRST forbids the Icon gates; PLAN gives Icon a
  numeric target — an Icon row therefore has no sanctioned instrument).
