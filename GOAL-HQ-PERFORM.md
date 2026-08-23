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

**s259 (2026-08-22) — THE OWED NUMBER IS PAID AND RETRACTED DOWNWARD; V2-5 LANDED; DUO WITH hq_C IS NOW LON-ORDERED.**

### ⛔⭐ LON OVERRIDE, ROUTED THE SAME SESSION (protocol law 6)
Lon, in-chat, mid-session, contradicting the row this seat had just locked. Verbatim in substance:
*"Ensure you get the FLEET protocol complete before we continue... When done with FLEET protocol continue on
ROMAN like before and run duo with the other HQ. Y'all can talk back and forth. He'll fix you bugs and you can
speed up his programs."*
- **Priority order is now: fleet protocol FIRST, then roman.** Same ruling hq_C received independently
  (*"get the FLEET protocol working, or we can not blast development later"*).
- **The duo is the staffing and it has a division: hq_C cures, hq_P measures.** The fleet returns for
  Icon/Prolog; the protocol must be finished and PROVEN before it does.
- ⛔ `next` had locked `zeta-frame-rsp-capture-home`. Lon's redirect wins, so **the claim was RELEASED** (not
  parked silently) and the analysis banked below so the row is not re-derived from scratch.
- Sent to hq_C as `duo-v2-5-taken`. **This block is the routing.**

### ✅ LANDED AND PUSHED
- ⭐ **THE OWED -O2 RE-MEASURE IS PAID, AND IT RETRACTS ONE OF THIS SEAT'S OWN NUMBERS.**
  `FINDING-2026-08-22-hq_P-hardened-nv-memo-is-17-percent-not-25.md`. roman mode-4, FIXED-WORK N=20000,
  callgrind, RT_OPT=`-O2`, full `make pristine`, commit `aa583ad8`, **output verified `check: 1102` first**:
  **869,577,578 Ir = 43,478.9 Ir/iter = 5.46x clean SPITBOL**, i.e. **-17.1%**, not the -25.2% in circulation.
  ⛔ **The 25.2% / 39,255 figure belonged to the UNSOUND DRAFT the killswitch caught. Do not re-cite it.**
  Sovereign question: **6.58x → 5.46x, verified.**
- ⭐ **V2-5 GATE HONESTY LANDED — SCRIP `e88e77db`** —
  `FINDING-2026-08-22-hq_P-v2-5-thirty-one-gates-can-now-say-no.md`. **31/31** formerly-vacuous gates now
  refuse an empty tree (measured **26 vacuous → 6 → 0**, which is the negative test). New `scripts/lib_gate.sh`
  (three exit codes: 0 CLEAN / 1 VIOLATION / **2 UNPROVEN**) and `scripts/test_gate_gates_can_say_no.sh`.
  **Strict is now the default**; nothing in the repo had ever passed `--strict`.
  Blocking set re-proven: `emit_no_lang` 0, `template_medium_invisible` 0, `test_corpus_snobol4` 0
  (m3 355/4, m4 354/3+2SKIP). hq_C's `test_gate_fleet_protocol_e2e.sh` **11/11** on this tree.
- **FIVE gates are now correctly RED — all pre-existing live defects, none in the blocking set, all minted as
  rows, none cured here** (MEASURE FREELY, CURE NEVER): `rtcc-r9-gvarq-collision` ·
  `c-to-bb-unledgered-scrip-c-57` · `vstack-residue-rt-h` · `const-graph-marginal-over-watermark` ·
  `bb-fixup-rank-85-dirty-templates`.

### ⭐⭐ ROMAN IS ANSWERED, AND IT IS **ONE NODE** — supersedes the two-buckets reading below
`FINDING-2026-08-22-hq_P-roman-is-one-defer-site-54-percent.md`. **~54.2% of every instruction roman executes
is a single deferred pattern node** — the bare `T` in `'0,1I,…' T BREAK(',') . T`, emitted as the one site
`n44_match_defer`. Our entire emitted code is **12.96%**.
⛔ **The "two independent buckets" reading earlier in this cursor was WRONG and is corrected here.** Plain
`callgrind_annotate` hid it: `NV_GET_fn`'s caller resolved to a bare address `0x488dfe0`. With
**`--separate-callers=2`** the chain names itself — `NV_GET_fn' … 'rt_defer_nv_read` at **19.35%**, and **~92%
of all `NV_GET_fn` cost arrives through `rt_defer_nv_read`.** The name lookup is not competing with the defer
pipeline; it **is** what the defer pipeline does.
⭐ **Mechanism:** `rt_defer_nv_read(const char *name)` ends in `NV_GET_fn(name)` — every deferred re-read goes
through the global name table by hash+`strcmp`. `&ANCHOR = 0` makes the match unanchored, so the pattern
retries at every start position and re-reads `T` **by name** each time: **2,807,622 calls at N=20000, 140 per
iteration**, for a pattern with exactly ONE deferred variable.
⭐ **This is why the memo bought only 17%** — it made each lookup cheaper (hash→`strcmp`) without touching the
**count**. ⛔ Do not cure by memoising harder; that ceiling is reached.
- **NARROW row minted, rank 0, `defer-nv-read-by-pointer-not-name`** — keep the deferral, kill the by-name
  resolution (resolve to `vrblk`/slot once at node build, follow a pointer). **No semantic ruling needed**,
  worth most of the 25.3% `NV_GET_fn`+`strcmp` cost. DONE-WHEN demands 10% against ~25% available.
- **WIDE — hq_C's call, deliberately NOT minted here:** don't defer a bare `TT_VAR` (`lower_snobol4.c:1398`).
  Worth up to the full 54%. ⛔ Hard case: `T` is also the capture target, so it genuinely varies mid-match.

### the earlier per-function view (kept — still true, now understood as ONE chain, not two)
| bucket | share | note |
|---|---|---|
| **variable-name lookup** | **36.5%** | `NV_GET_fn` 21.04% (**still #1 — the memo did NOT dethrone it**) · `__strcmp_avx2` 10.91% (substantially the memo's OWN validation cost) · `NV_SET_fn` 4.58% |
| **defer pipeline** | **26.9%** | `c_rt_defer_close` 10.47 · `rt_defer_run_all` 7.59 · `rt_defer_get_pat_dtp` 5.65 · `rt_dfx_push` 3.23 — down from the 29.8% predicted |
| our emitted code | 13.4% | |

**63.4% of every instruction roman executes is in two runtime buckets and NEITHER IS CODEGEN.** The memo
turned a hash into a `strcmp`; the next rung is to **stop doing the lookup at all**, not to make it cheaper
again. ⛔ The defer half is hq_C's call (roman has exactly ONE defer site, `n44_match_defer`); no unilateral
change from this seat.

### ⭐⭐ ALL THREE LOSING KERNELS PROFILED — THREE ROOT CAUSES, AND **TWO ARE THE SAME CLASS**
`FINDING-2026-08-22-hq_P-three-losing-kernels-three-root-causes-two-are-by-name.md`. Same rail throughout:
mode-4, FIXED-WORK, `-O2`, SCRIP `e88e77db`, `--separate-callers=2`, **every output diffed against `.ref`
before any number was read**.

| kernel | N | verified | Ir/iter | root cause | rooted share |
|---|---|---|---|---|---|
| `roman` | 2,000 | `check: 1102` | 40,186 | one deferred node re-reads a var **by name** | **~54%** |
| `string_manip` | 20,000 | `check: 43` | 2,138 | builtins dispatched **by name** | **~59%** |
| `table_access` | 100 | `check: 250500` | **905,108** | key stringify + double resolve + **alloc on read** | ~40% |

⭐ **THE CLASS: SCRIP resolves at RUN TIME, every operation, what the compiler already knew.** Two of three.
`name-lookup-strcmp` **re-ranked 4 → 1** on this evidence — it is not a cleanup row, it is the dominant cost
in two of the three kernels we lose on. `defer-nv-read-by-pointer-not-name` (rank 0) is **one instance**.
⛔ Do not cure by memoising harder — the NV_* memo already did that and returned 17% because it cut cost per
lookup, not lookup **count**.

⛔ **`table_access` is NOT in that class — do not dispatch it as if it were.** And the obvious assumption is
wrong: **the hash is fine** (only 2.3 `strcmp` per `table_find_pair`, a short probe, not a linear scan). Its
three real questions, per-iteration counts against 600 writes: `rt_agg_alloc` **1801 (3x) — a SUBSCRIPT
ALLOCATES**; `tbl_key_str` and `table_find_pair` both **1200 (2x)** through two distinct chains, which reads
as **each subscript resolved twice** — close to a free halving if real; and why a key is stringified on the
read path at all. ⭐ The 2x is inferred from call-count **ratios**, not from reading the code — confirming or
killing it by reading `c_rt_subscript_var` vs `rt_subscript_var_container_only` is the cheapest next step in
the whole SNOBOL4 front.

⭐ New row `setjmp-per-builtin-call` (rank 2): **every builtin call pays a `setjmp`** (2.1/iter, 2.16% of
string_manip), independent of name resolution and surviving any cure to it. Answer *what it guards* before
touching it — if the Byrd ω port can carry it, it is pure overhead.

⭐ **`--separate-callers=2` IS NOW THIS SEAT'S DEFAULT AND SHOULD BE YOURS.** Plain `callgrind_annotate`
reported roman's hottest caller as a bare address and cost this seat a published wrong reading.

### 🔖 BANKED — `zeta-frame-rsp-capture-home`, released mid-analysis, DO NOT RE-DERIVE
- ⛔ **The abort message is MISLEADING.** It blames *"classifier and ZD plan disagree"*, but
  `cap_anchor_of()` at `emit.cpp:973` is a **stub that returns 0**, so `havehome()` reduces to `op_zres`
  alone and the entire ζ-STANDING arm of that test is **dead code**.
- `--zeta-storage=frame-rsp` routes through `rt_zeta_storage_set` to **`rt_zeta_port_set_mode(ZC_PORT_CSTACK)`**,
  and `x86_fc_on()` is hardcoded to `port == ZC_PORT_FORTH` — so **every forth-cell mechanism switches off
  together** under frame-rsp. `zeta_storage.c` never consults the storage mode at all.
- ⭐ Reading: this is an **UNIMPLEMENTED config**, not a misclassification. ⛔ **Do not cure it by widening
  the classifier.** NOT proven — no binary was available before the redirect. `SCRIP_CAP_DIAG=1` prints
  `zres`/`anchor`/`frame_off` per capture node and is the instrument to finish it with.

### ⛔ STANDING CONSTRAINTS
- **NO BEAUTY NUMBER AT `-O2`** (roman at `-O2` is fine and was verified this session; hq_C has localised the
  `-O2` defect to **two files of 261**, `rt.c` + `pattern_match.c`).
- No perf claim may cite a ζ-storage comparison while `zeta-frame-rsp-capture-home` / `zeta-cell-heap-segv` are red.
- Open with `ceo`: `escalate-icon-checks-vs-icon-target`.
- ⚠️ `test_gate_fb_predicate_tripwire.sh` times out at 100 s on the real tree (exit 124). Pre-existing, not V2-5 fallout.
