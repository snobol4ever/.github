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

**s258 (2026-08-22) — PHASE 0 PREFLIGHT: THIS SEAT'S HALF IS LANDED AND PUSHED.**

- ✅ **V2-3 + V2-4 landed** at SCRIP `8e2fb884`, gated by `scripts/test_gate_postoffice_identity.sh` — 18 checks,
  **negative-injection proven: 15 of them fail against the pre-patch script.** Identity canonicalised then
  ASSERTED (no mailbox ⇒ exit 3, never a fresh directory); every implicit `mkdir -p` on a mailbox path deleted;
  `.msg.*` orphan sweep; `/home/claude` → `ceo`; `fleet` census by mailbox with a MAIL column; HQ banner refuses
  the ✅ on inbox mail older than 30 min; board line carries oldest-unanswered age + row topic.
- ✅ **Drain complete: legacy `hq` inbox 29 → 0.** 7 answered (perf lane), 7 forwarded to hq_C with original text
  verbatim, 15 archived as read. The 46-hour orphaned message was delivered to seat08 by the sweep's first live
  run. Phantom `claude01/` retired (messages archived, not re-delivered — seat01 had already acked them).
- ✅ **Rows minted:** `zeta-frame-rsp-capture-home` · `zeta-cell-heap-segv` (rank 0, hq_P) · `opt0-define-beta-link`
  (rank 1, hq_C, cross-HQ interlock).
- ✅ **CROSS-VERIFICATION OF hq_C COMPLETE — BOTH RUNGS SIGNED OFF.** V2-2 purge: **PASS** (audited every row in
  `QUEUE.done.tsv` against its claim — 0 swept whose claim lacked a `DONE` marker). V2-1: **FAIL at first
  measurement, PASS after hq_C pushed.** First pass, against `origin/main`, a rank-5-first / rank-0-second queue
  served **rank 5** and `assign` printed usage — the code was in hq_C's tree but **uncommitted**, while `QUEUE.tsv`
  line 3 already told 16 seats the picker was rank-sorted. hq_C pushed (`646b8047`, `93d3ef16`); re-verified on the
  merged tree — rank inversion serves rank 0 then rank 3, `assign` dispatches ASSIGNED→RUNNING with a doorbell, and
  refuses both an unrowed topic and another seat's row. hq_C's `test_gate_s4e_picker_v2.sh` 18/18; my
  `test_gate_postoffice_identity.sh` still 18/18 after the rebase. `QUEUE.tsv` line 3 stays **computed** rather than
  restored to a status claim, so it cannot rot again.

- ⛔ **BEAUTY NUMBERS ARE FROZEN PENDING hq_C's C-0 VERDICT.** hq_C measures C-0 as **not reproducing at HEAD**
  (classic beauty self-hosts to its fixed point in both m3 and m4; confirmation control building). Until that lands
  at a named HEAD, the inherited **2,129,544,838 Ir beauty runtime and the 9.34x it anchors are MEASURED-BUT-SUSPECT**
  and this seat publishes no beauty ratio. Re-take it myself at the named commit rather than inherit it. Costs P-0
  nothing — `roman` was already the first target for exactly this reason.
- ⛔ **MY OWN GATE HAD THE BLIND-INSTRUMENT DEFECT** (hq_C caught it): hardcoded subject ⇒ their injection was a
  no-op and it said 18/18 over the wrong binary. Fixed `3f951354` (`S4E_MSG_BIN` override, subject printed, exit 2
  if missing); now **18/0 current vs 3/15 pre-patch**, matching hq_C independently. ⭐ Rule for V2-5's 31 gates:
  negative-injection is proven by a gate whose **subject can be redirected by someone other than its author**.

**⭐ NEXT ACTION, in order:**
1. **RUNG P-0 — profile `roman`.** Unchanged and still the sovereign question: callgrind at fixed N, top functions by
   **Ir WITH call counts and Ir-per-call** — Ir-per-call is the signature that exposes a linear scan, which is exactly
   how `bb_ab_slot_for` was caught at 22,089 Ir per procedure call. Then check whether the same function dominates
   beauty runtime; if it does, **one cure moves both.** Row `perf-roman-8x` is rank 0 and FREE.
2. **`s4e_msg.sh fleet` on a cadence** — now that it can actually see both HQs and shows mail age, there is no excuse
   for a row sitting 115 minutes unnoticed.

⛔ **Seat→HQ ownership (`$PO/<seat>/HQ`) is IMPLEMENTED but NOT POPULATED.** `ask` resolves `$S4E_HQ` → that file →
legacy `hq`, so questions still land in `hq/` — which is now drained and visible in the census, so nothing rots. The
8/8 split between hq_C and hq_P is a joint decision and should be written the session Lon fires the wave.
