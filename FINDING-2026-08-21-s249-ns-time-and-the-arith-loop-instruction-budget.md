# FINDING s249 — ONE NANOSECOND CLOCK IN ALL THREE ENGINES, AND arith_loop's INSTRUCTION BUDGET CUT 29%

**Session:** s249 (HQ) · **Date:** 2026-08-21 · **Directive:** Lon, in-chat — *"Get arith_loop.sno MAXIMALLY optimized … we should change SCRIP, SPITBOL, and CSNOBOL4 to use a nanosecond clock. That way it is consistent between all three."*

---

## 1. THE HEADLINE

`arith_loop` retires **29.4% fewer instructions** and runs **+40.7% faster**, measured with hardware counters, correctness-gated throughout. Against the oracle it goes **5.37x → 6.67x** (m3) and **6.95x** (m4) of `sbl`.

| arm | M iters/s | instr/iter | cyc/iter | IPC | branch-miss/iter |
|---|---|---|---|---|---|
| before | 118.0 | 187.27 | 45.50 | 4.12 | 0.0054 |
| after | 166.0 | 132.19 | 31.26 | 4.23 | 0.0039 |
| **Δ** | **+40.7%** | **−29.4%** | **−31.3%** | +2.7% | −28% |

Instructions down 29.4%, cycles down 31.3%, IPC essentially unmoved. **That is the whole story: this kernel is instruction-count-bound and the only lever is emitting less.** (Whole-program counts; the inner loop alone is 165 → 120 instr/iter, and hardware agrees with callgrind to within one instruction — 120.16 measured against 120 attributed.)

---

## 2. THE METHOD — MEASURE, THEN CUT

`scripts/profile_box_histogram.sh` (callgrind at instruction granularity, addresses joined against the emitted box labels) gave the per-iteration budget. The first read is the one that decided everything:

```
165 Ir/iter total    D1 misses 0    LL misses 0    branch mispredicts ~0
```

Nothing stalls. No cache work, no layout work, no prefetch work would have moved this row a single percent. The entire optimisation surface was *instruction count*, and the histogram named the owners:

| box family | Ir/iter (before) | after | what it was |
|---|---|---|---|
| `binop_α` | 41 | 28 | 3 boxes: 2 arith + 1 concat |
| `coerce_numeric_α` | 28 | 28 | 2 boxes feeding `LT` |
| `var_α` | 24 | 24 | 4 boxes × 6 |
| `rt:str_concat_d` | 19 | **0** | concatenating a statically null string |
| `rt:rt_cmp_d` | 14 | **0** | PLT call to compare two integers |
| `cmp_test_α` | 13 | 14 | |
| `lit_integer_α` | 10 | 10 | the constant `1`, loaded from memory |
| `assign_α` | 10 | 10 | |
| `statement_end_α` | 4 | 4 | |
| `statement_begin_α` | 2 | 2 | two bare `jmp`s |
| **total** | **165** | **120** | |

The hot loop now contains **no runtime call at all** — emitted boxes rose from 74.0% to 89.9% of the cycle proxy.

---

## 3. THE THREE CUTS

### 3.1 `IR_BINOP_CONCAT` — the null string is the identity (−25 Ir/iter)

`PRED(a,b) expr` is **the** SNOBOL4 conditional-value idiom, and it lowers to a concatenation whose one side is always the null string. We were calling `str_concat_d` through the PLT, every iteration, to compute an identity: 12 in-box + 19 in the callee.

⭐ **Probed against the live oracle, not assumed.** `sbl -bf` returns the *other operand unchanged, datatype intact*, for INTEGER, REAL, STRING, ARRAY, TABLE and PATTERN — all six. The identity is total, not a string-only special case, so the box is a two-word copy.

New `ir_value_is_null_string()` in `src/optimizer/ir_query.c` names the property by **what the node produces** (predicate results; the empty string literal), not by opcode identity. `CONCAT_FRACDIGIT` is excluded — `""` is not its identity.

### 3.2 `IR_CMP_TEST` — an integer compare is three instructions, not a call (−14 Ir/iter)

Both operands arrive from `coerce_numeric`, so DT_I ⊕ DT_I is the dominant shape and `cmp rax, rdx` settles it outright. `rt_cmp_d` stays for real, string and mixed. Four of the six predicates share a fail mnemonic between the sign test and the direct compare — only LT and GE differ (`jns`/`js` are sign-of-a-difference tests, `jge`/`jl` are the signed comparisons) — so both mappings are written out rather than derived from one another.

### 3.3 `IR_BINOP` arith — the four combinations (−6 Ir/iter)

**Lon's call, in-chat:** *"Do you not have 4 combinations that would lead to a better BB_BINOP BB box? unknown + unknown, unknown + LITERAL, LITERAL + unknown, and LITERAL + LITERAL? … a 4-way direct dispatch known at compile-time."*

He was right, and **half the machinery was already in the tree pointed at the wrong arm.** `op_imm_a_ok` / `op_imm_b_ok` have been computed for every non-`num_real` binop since `emit.cpp:1423-1425` was written, and the *frame* arm of `bb_binop_arith.cpp` consumes them. `inl2_ok()` even excludes LIT⊕LIT explicitly, because that is const_fold's job — Lon's fourth combination, already accounted for.

The **ζ-spine arm** — which is what SNOBOL4 actually compiles to — re-read both tags off the spine and threw the knowledge away. `A + 1` paid a tag load, an `and`, and a value load for an operand the compiler was holding. The fix mirrors the frame arm: same two flags, same meaning, LIT⊕LIT still left to const_fold.

⛔ **The lit box still WRITES its spine slot** and the cold arms still read it. This arm must not outlive that.

---

## 4. NS-TIME — ONE CLOCK, ONE UNIT, THREE ENGINES

| engine | site | was | now |
|---|---|---|---|
| SCRIP | `by_name_dispatch.c:bn_time` | `clock()*1000/CLOCKS_PER_SEC` — CPU ms | `rt_time_ns()` — `CLOCK_MONOTONIC` ns, integer |
| SPITBOL | `osint/systm.c:zystm` | `CLOCK_PROCESS_CPUTIME_ID` ms | `CLOCK_MONOTONIC` ns |
| CSNOBOL4 | `lib/bsd/mstime.c` | `getrusage` user CPU ms | `CLOCK_MONOTONIC` ns, zeroed at first call |

### 4.1 ⛔ SCRIP HAD TWO TIME() IMPLEMENTATIONS AND THE LIVE ONE WAS THE WORSE ONE

`core.c`'s registered `_TIME_` (monotonic, ms) **never fired**. Every `TIME()` call went to `by_name_dispatch.c:bn_time`, which used ANSI `clock()` — CPU time truncated to whole milliseconds. Both now call one exported `rt_time_ns()`. A second implementation of a language builtin, shadowing the documented one, is its own finding: **grep for the dispatch table before believing the registration table.**

### 4.2 THE ARM WAS CHOSEN BY MEASUREMENT, NOT BY TRADITION

| clock | `getres` | min observed tick | cost per read |
|---|---|---|---|
| `CLOCK_MONOTONIC` | 1 ns | 50 ns | **20 ns** (vDSO) |
| `CLOCK_MONOTONIC_RAW` | 1 ns | 20 ns | 17 ns |
| `CLOCK_PROCESS_CPUTIME_ID` | 1 ns | **471 ns** | **502 ns** (syscall) |

SNOBOL4 tradition says `TIME()` is CPU time, and two of the three engines obeyed it. But a CPU-clock "nanosecond" `TIME()` would be **fake precision** — it cannot resolve below ~471 ns — and each read costs ~65 arith_loop iterations of the engine under test, perturbing the very loop it measures. Wall-monotonic is the only arm on which "nanosecond" is a true statement. The deviation from tradition is deliberate and is recorded here.

### 4.3 SPITBOL: THIS IS A REVERT, AND IT FIXES A LATENT BUG

`3e519f9` replaced upstream's nanosecond `zystm` with milliseconds. **`sbl.min:16746-16752` — the end-of-run statistics block — still divides the value by 1000 twice to reach ms**, and has therefore been silently wrong for the whole interval. Restoring the unit fixes it for free.

### 4.4 THE ORACLE REBUILD WAS PROVEN, NOT ASSUMED

⛔ `bin/sbl` was **two commits behind its own sources**, so any rebuild also picks up the `dd66e14`/`5035571` PM/Byrd fire-points (`pmcll pmext pmred pmfal`, gated on `SPL_PM_TRACE`) and the osint monitor IPC runtime — which had **no `.o` in the stale Apr-6 object cache at all**, so a naive relink would have silently dropped 38 symbols with no link error. `./bootsbl` was a dangling symlink, so the bootstrap-free path was unavailable; built the documented way with `BASEBOL=./bin/sbl` in an **isolated copy** of the tree.

**Equivalence sweep: all 321 `corpus/crosscheck` programs through old and new, comparing output+rc md5.** 320 identical. The one differing program, `coverage/coverage_sno_nodes.sno`, is **nondeterministic under the OLD binary too** — three runs, three md5s. Previous oracle preserved at `/home/claude/x64-sbl-PRE-NSTIME.bak`, outside the repo.

### 4.5 `harness.inc`

`ZBUD`/`ZFLR` **stay in milliseconds** — the contract is unchanged and all 15 benchmark bodies are untouched; the harness converts once, in place, after the check line. It now prints `ns:` alongside the legacy `iters:`/`ms:`, so every existing runner parses unchanged and the full-resolution reading is available to anything that wants it.

---

## 5. COLLATERAL FINDINGS

- **`lib/posix2001/mstime.c` is dead code in the csnobol4 tree.** `configure:1040-1043` selects `lib/bsd` on any host with `getrusage`, and `configure:1033` rejects `clock_gettime` outright: *"reports combined user/system time, so removed it."* Read the configure selection rule before editing a `lib/<flavour>/` file.
- **`isnobol4.c` is compiled, `snobol4.c` is not** (`Makefile2:23` sets `SNOBOL4=isnobol4`). Both carry the same generated `TIME()`; citing the wrong one wastes a session.
- **The csnobol4 tree had NO built binary on this host** before s249, and does not build out of the box — `bzlib.h` was absent (`lib/compio_obj.c:190`). There was no CSNOBOL4 oracle here to regress.
- **`/usr/local/bin/snobol4`** (root-owned, Apr 6, 499832 bytes — a *different* binary from our 509656-byte build) was being picked up off `PATH` by `test_3way_snobol4.sh:12` and `test_smoke_self_beautify.sh:27` instead of `$S4A/csnobol4/snobol4`. Moved aside to `snobol4.APR6-STRANGER` so those scripts fail loudly rather than grading against a stranger. **This is the false-oracle class again.**
- **80 root-owned files in `/home/claude/x64`** from an Apr-6 root build could not be overwritten by `satirical`, which is why the SPITBOL rebuild had to happen in a copy. Now `chown`ed back.

---

## 6. MEASUREMENT CONDITION — READ THIS BEFORE COMPARING TO ANY EARLIER NUMBER

⛔ **The CPU governor was `powersave` on `amd-pstate-epp` for the first half of this session, with cores at ~37% of max clock** (1.9 GHz against a 5.13 GHz ceiling). It is now `performance`. **Every absolute number baked before 2026-08-21 was taken on a throttled, drifting clock.** `NOISE-FLOOR.tsv` was re-baked under the new governor; interleaved A/B *ratios* survive the change (both arms were throttled equally) but absolute rates do not.

Tooling now available and not previously present here:

- **`perf`** — `/usr/bin/perf` refuses to run because the running 6.17-oem kernel's `linux-tools` package **ships no perf binary at all**. `linux-tools-generic`'s 6.8 perf counts correctly on this kernel; shim at `/home/claude/.tools/bin/perf`. `kernel.perf_event_paranoid` was **4** (blocks even user-space counters) and is now 1, persisted in `/etc/sysctl.d/99-perf.conf`.
- **`valgrind`** installed system-wide, so `profile_box_histogram.sh` and `profile_callgrind.sh` work with no PATH juggling for the fleet seats.

RT_OPT for every number in this document: **-O0**.

---

## 7. GATES

| gate | before | after |
|---|---|---|
| `test_corpus_snobol4.sh` m3 | PASS=338 FAIL=2 | PASS=338 FAIL=2 |
| `test_corpus_snobol4.sh` m4 | PASS=337 FAIL=2 SKIP=1 | PASS=337 FAIL=2 SKIP=1 |
| `test_bench_snobol4_timed.sh` | — | **15/15 checks ok, 0 bad, gc=0 every row** |
| SPITBOL crosscheck equivalence | — | **320/320 deterministic programs identical** |

The two failures (`160_pat_alt_inner_gen_resume`, `demo_treebank`) are pre-existing and identical on both sides — **verified by stashing the entire change, rebuilding, and re-running**, not by assertion.

---

## 7A. ⛔ TWO PLAUSIBLE HYPOTHESES, BOTH MEASURED, BOTH FALSIFIED — DO NOT RE-SPEND THIS

Hardware counters became available mid-session (`perf`; see §6). Two obvious next optimisations were prototyped at the `.s`
level and measured before any compiler work. **Neither is worth building.** Both are recorded so nobody pays for them twice.

### 7A.1 Fallthrough-`jmp` elision buys ZERO cycles

The loop retires **30.0 branches per iteration out of 120 instructions** — one in four — and most are `jmp` to the
immediately-following label, a box-to-box hand-off that should be fallthrough. The front-end argument is seductive: Zen4
takes at most ~2 taken branches per cycle and every taken branch ends a fetch block, so 30 branches in 28 cycles looks like
the cap. It is not.

| | instr/it | **cyc/it** | br/it | IPC | wall |
|---|---|---|---|---|---|
| shipped | 120.16 | **28.26** | 30.03 | 4.25 | 0.58s |
| 6 fallthrough `jmp`s elided | 114.16 | **28.23** | 24.03 | 4.04 | 0.59s |

Six taken branches per iteration removed, **0.03 cycles saved**. The front end absorbs perfectly-predicted `jmp`s for free
and dispatch width had slack. The IPC *drop* is arithmetic, not regression — fewer instructions in the same cycles.

⛔ **A peephole for this would be pure cost: BOTH-MEDIUM work on the BINARY relocation stream, for nothing.**

### 7A.2 Operand forwarding WITHOUT deleting the producing box buys ~1 cycle

Rewriting six spine reads to read their global source directly (`[rsp+32]` → `[r9+32]`), instruction count held **identical**
at 120.18, moved 28.8 → 28.1 and 28.7 → 27.5 cyc/it: **~3.4%**. Real but small, because it removes the *load-after-store
dependency* and leaves the **store** in place. Store→load forwarding on this core is cheap; the store is not.

### 7A.3 WHAT THE COUNTERS ACTUALLY SAY

| | instr/it | cyc/it | **loads/it** | **stores/it** |
|---|---|---|---|---|
| before §3's cuts | 187.3 | 45.24 | 55.6 | 36.3 |
| after | 131.6 | 30.92 | 35.1 | 30.7 |
| Δ | −29.7% | −31.7% | **−36.9%** | −15.4% |

**Half of every instruction in this loop is a memory access.** The cycle win tracked the LOAD reduction, not instruction
count in general — which is exactly why 7A.1 failed and why §3's cuts succeeded (they removed a PLT call's argument
marshalling and redundant tag/value reads, i.e. loads).

⭐ **THE STRUCTURAL NUMBER.** Of the 28 stores per iteration (`ls_dispatch.store_dispatch` ÷ iterations, exact):

| owner | stores/iter |
|---|---|
| `var` ×4 | 8 |
| `lit_integer` ×2 | 4 |
| `binop` ×2 | 4 |
| `coerce_numeric` ×2 | 4 |
| `cmp_test` | 2 |
| `concat` (identity) | 2 |
| **`assign` ×2 — the only semantically necessary stores** | **4** |
| total | **28** |

**24 of 28 stores exist solely so the next box can read the value back.** The correct next optimisation is therefore not
"emit fewer instructions" — it is **delete hand-off boxes**. Each box removed takes ~6 instructions, 2 stores and 2 loads
with it. Metric to track: `ls_dispatch.store_dispatch / iterations`, currently 28, floor 4.

---

## 7B. ⭐ THE COST MODEL — INSTRUCTIONS ARE FREE, POSITIONS ON THE DEPENDENCY CHAIN ARE NOT

Lon pointed at **Proebsting, "Simple Translation of Goal-Directed Evaluation"** (`/home/resources/`, and `SCRIP/docs/8_*.pdf`)
— the source paper for our four-port model — and named its two optimisations: **branch-to-branch elimination** (our trampolines)
and **result copy propagation** (our spine-slot sharing). §5:

> *"while the technique is simple, it suffers from generating many simple copies and many branches to branches. Propagating
> copies and eliminating branches to branches (by branch chaining and re-ordering the code) optimizes the code well … The
> result closely resembles code that would be produced from two generic `for` loops, which is exactly what one would hope for."*

His per-operator run-time temporary **is** our ζ-spine slot, so his "simple copies" are our hand-off stores. Figure 1 → Figure 2
collapses ~40 labelled chunks to 12 lines and copy propagation does the heavy lifting.

### 7B.1 BOTH PASSES ALREADY EXIST HERE AS STUBS, AND THEY ALREADY COMPOSE

| pass | file | what it recognised before s249 |
|---|---|---|
| copy propagation | `src/optimizer/copy_prop.c` | `cp_source()`: **two** cases — `COERCE_STRING(LIT_STRING)`, `COERCE_INTEGER(LIT_INTEGER)` |
| branch-to-branch | `src/optimizer/branch_chain.c` | `bc_is_passthrough()`: **two** ops — `IR_SUCCEED`, `IR_GOTO`. No code re-ordering. |

⭐ **And the box-deletion pipeline between them is already wired end to end:** `cp_run` redirects the consumer's operand edge →
the copy node falls out of the reference set → it is turned into `IR_SUCCEED` → `bc_chase()` walks γ straight through it → the
box never executes. **The "architectural rung" §7A implied was already built.** Widening `cp_source()` *is* the mechanism.
s249 added the first new case (the null-concat identity, `979feb4a`), which deletes the whole box rather than just the call:
−8 instructions, −2 loads, −4 stores per iteration.

### 7B.2 AND IT BOUGHT 0.3% — HERE IS WHY, AND IT IS THE MOST USEFUL NUMBER IN THIS DOCUMENT

Payload scaling — the same kernel with 0, 1, 2, 3 copies of `A = A + 1` in the loop:

| payload | instr/it | cyc/it | Δcyc per statement | stores/it |
|---|---|---|---|---|
| 0 × | 84.14 | 19.55 | — | 16.03 |
| 1 × | 112.16 | 28.36 | **+8.81** | 24.04 |
| 2 × | 142.20 | 37.59 | **+9.23** | 32.05 |
| 3 × | 172.21 | 44.22 | **+6.63** | 40.05 |

| | instructions | cycles | **cyc/instr** |
|---|---|---|---|
| marginal `A = A + 1` statement | +30 | +8.8 | **0.30** |
| the concat box copy propagation deleted | −8 | −0.16 | **0.02** |

**Fifteen times cheaper per instruction.** The concat box was six `mov`s sitting **off** the value dependency chain with its
operands already computed, and the out-of-order engine hid it completely. `A = A + 1` is three **serial store→load round trips**
— load `A` from `[r9+40]`, store spine, load spine, add, store spine, load spine, store `[r9+40]` — at ~5 cycles of
store-forwarding each. That chain *is* the 8.8 cycles.

⭐⭐ **THE RULE FOR EVERYTHING THAT FOLLOWS: copy propagation pays when it coalesces a slot ON the value chain
(`var → binop → assign`), and pays nothing beside it.** Count chain positions, not instructions, not stores, not branches.
This reconciles every null result in §7A and is why the three cuts in §3 worked — they removed PLT calls, which are chain
positions with a serialising register save/restore through memory on either side.

Queued as rank-0 rung **`chain-slot-coalescing`**, ordered by chain position: `COERCE_NUMERIC` of a statically-numeric operand
first, then `IR_VAR` with a single consumer and no side-effecting node between — the latter gated on a written-out safety
argument, because SNOBOL4's left-to-right evaluation makes `f(x) + A` safe and `A + f(x)` unsafe.

---

## 7C. THE THIRD LEVER — ONE CARVE PER STRETCH, AND THE PRICE LIST THAT RANKS ALL THREE

Lon, in-chat: *"for any sequence of BB that are guaranteed to execute … and that have no outward branch … have the first BB do
the SPINE CARVE for the whole short sequence … save the extra RSP BUMPING"*, with the constraint *"you never want to carve past
a GAMMA, since that is why we are doing FORTH-style stack to keep it SMALL SMALL and grow as needed."*

⭐ **The constraint is exactly right and it is the spec.** Two refinements found while measuring it:

- **Inside a fall-through stretch, PEAK DEPTH IS UNCHANGED.** Same maximum RSP excursion, reached a few instructions earlier
  and held a few nanoseconds longer. The FORTH "small small, grow as needed" property survives fully — which is what separates
  this from a C-style whole-frame prologue, where depth × recursion is exactly what a SNOBOL4 matcher cannot afford. The
  property breaks only when a γ can *leave* the stretch, because then a path that never runs boxes 3–5 still paid for them.
  That is precisely the case Lon's rule excludes.
- **A `_β` label inside the stretch does NOT break it.** `n26_lit_integer_β` unwinds `add rsp,16; add rsp,16` = 32; if `n25`
  carves 32 and `n26` carves 0, the unwind total is still 32 and the handler is correct with no change. An early census that
  disqualified stretches containing β entries was wrong and reported 5.9% coverage; the corrected criterion is γ-fallthrough.
- **The release side is ALREADY coalesced** — `statement_end` emits one `add rsp, 48` / `add rsp, 144` for a whole statement.
  The design already accepts the asymmetry; this closes it.

### 7C.1 THE MEASURED PRICE OF A CARVE

Isolated microbenchmark (8 chained `sub rsp,16`+2-store groups vs one `sub rsp,128` and the same 8 store pairs at re-based
offsets — identical stores, identical final RSP, only the carve count differs): **7 carves removed = 0.24–0.35 ns/iteration**,
i.e. **~0.17 cycles per carve** at ~4.9 GHz.

⭐ **THE PRICE LIST — this is the durable output of s249, use it to rank any future idea before building it:**

| work | cyc/instr | measured by |
|---|---|---|
| off-chain `mov` (the concat box) | **0.02** | copy-prop box deletion: −8 instr, −0.16 cyc |
| **`sub rsp,16` spine carve** | **0.17** | the microbenchmark above |
| on-chain statement work | **0.30** | payload scaling: +30 instr, +8.8 cyc per statement |
| taken `jmp` to the next label | **~0.00** | §7A.1: 6 removed, 0.03 cyc |

A carve is **8× an ordinary off-chain instruction and about half a chain position.** Worth attacking; not free-instruction cheap.

### 7C.2 THE STRETCH CENSUS

Criterion = consecutive α-boxes each carving exactly 16, moving RSP no other way, with γ jumping to the **next** box's α label.

| scope | carves | removable | mean stretch |
|---|---|---|---|
| `arith_loop` **hot loop** | 12 | **10 (83%)** | **6.00** |
| `arith_loop.s` whole file | 82 | 52 (63%) | 2.73 |

**Stretches are longer where it is hot** — six-box runs in the loop body against ~2.7 elsewhere. Estimated payoff on
`arith_loop`: 10 × 0.17 = **~1.7 cycles of 28.4 ≈ 6%**, twenty times the concat win and second only to chain-slot coalescing.

⭐ **And it needs NO dataflow analysis**, unlike chain-slot coalescing. The condition is local and the emitter already computes
it: its per-node loop holds `nodes[i]`, `lbls[i]` and `node_γ`, so **`node_γ == lbls[i+1]` IS the stretch test** — the very test
built for the fallthrough-jmp peephole in §7A.1, measured at zero, and discarded. Same test, different payload, 6% not 0%.

Queued as rank-0 rung **`spine-carve-coalescing`**, with the silent-corruption hazard named: each box re-bases **its own**
result write to `[rsp + 16*(L-i)]` while every downstream reference stays byte-identical, and a deep-recursion program must be
run to confirm peak stack depth did not grow — the one regression throughput numbers cannot see.

---

## 7D. ⛔⛔ MEASUREMENT AUDIT — TWO OF THE NUMBERS ABOVE ARE NOISE READINGS. READ THIS BEFORE QUOTING §7A–§7C.

Lon asked "are you sure of the accuracy and precision of your measurements?"  Re-measured properly, and **no**.

⭐ **THE INSTRUMENT'S DETECTION LIMIT IS ±0.22 cyc/iteration ≈ 0.8%**, established the way it should have been first:
six interleaved samples per arm, both orders, warm-up discarded.  `al_fixed` min 28.292 / mean 28.395 / max 28.504;
`al_cp` min 28.315 / mean 28.406 / max 28.542 — **within-arm spread 0.212 and 0.228 cyc.**  Any delta below that is not
a reading.  This project's own README says *"read NOISE-FLOOR.tsv before calling any difference real"*; that discipline was
applied rigorously to the throughput benchmarks in §6 and then **not applied at all** to the perf cycle deltas in §7A–§7C.

### CORRECTIONS

| claim as first written | corrected |
|---|---|
| concat-box deletion "−0.16 cyc", "0.02 cyc/instr" | **UNMEASURABLE.** delta = −0.023 cyc at the min, i.e. the "faster" arm is fractionally slower. Effect is *< 0.028 cyc/instr*, an UPPER BOUND, not a measurement |
| fallthrough-jmp elision "saved 0.03 cycles" | **BELOW DETECTION.** Effect is *< 0.037 cyc/branch*, an upper bound |
| "15× cheaper per instruction" | **UNFOUNDED AS A RATIO** — one of the two terms was a noise reading |
| spine carve "0.17 cyc" | **0.14 ± 0.015 cyc**, from an interleaved min-of-9 with warm-up discarded (the first run had no warm-up, fixed A-then-B order — a systematic bias favouring B — and 2–3 samples) |
| clock "~4.9 GHz" | **4.624 GHz measured** (`cycles ÷ task-clock`). Every ns→cycle conversion above was 6% off |
| payload scaling "0.30 cyc/instr" | deltas were +8.81, +9.23, **+6.63** — the third breaks the pattern and was under-flagged. Honest range **0.22–0.31** |

Two further process faults, both mine: the fixed-count perf runs were made **without `SCRIP_NOHUGE=1`**, contrary to this
project's own stated measurement condition; and the §7C stretch census ran against `.s` artifacts regenerated **before** the
copy-prop commit `979feb4a` — stale, and a RULES.md handoff-step-4 violation.

### WHAT SURVIVES, AND WHY THE CONCLUSIONS STILL STAND

Above the noise floor by a wide margin, and defensible: the **+41.9%** headline (8 interleaved pairs, 1.375–1.451, ~50× the
floor); the **instruction/load/store counts** (exact over 10⁸ iterations, and 120.16 measured agrees with callgrind's 120
attributed); **+8.8 cyc per added statement** (40× the floor); the SPITBOL 320/321 equivalence; and the gate proven by
stash-and-rerun.

⭐ **THE QUALITATIVE FINDING IS UNCHANGED AND IS THE POINT: chain work is expensive and measurable, work beside the chain is
below the noise floor.**  What is retracted is every precise cyc/instr figure for the cheap items — they are upper bounds and
were presented as measurements.  §7C's projection for `spine-carve-coalescing` is therefore ~10 × 0.14 = **1.4 cyc of 28.4 ≈
4.9%, only ~6× the detection limit** — it must be confirmed with interleaved min-of-N and may come in at half that.

⛔ **THE RULE THIS BUYS: before quoting a cycle delta, measure the within-arm spread of the same two binaries interleaved, and
refuse to report anything smaller.**  A point estimate below the spread is a story, not a result.

---

## 7E. WHERE THE REAL DEFICITS ARE — TABLES STRINGIFY INTEGER KEYS, AND N-D ACCESS DISPATCHES ONCE PER DIMENSION

`table_access` profiles at **8.5% emitted boxes / 91.5% runtime C** — the exact inverse of `arith_loop`. Top: `c_rt_subscript_var`
14.2% (43,788 D1 + 43,751 LL misses), `tbl_key_str` 9.1%, `_tbl_hash` 7.4%, `table_set_descr_keyown` 6.1%, `__strcmp_avx2` 4.8%,
`rt_gcheap_alloc` 4.1%, `table_find_pair` 3.9%, `rt_agg_alloc` 3.8%, `rt_ws_strdup_c` 1.7%.

⭐ **`aggregates.c:122 tbl_key_str()` converts EVERY table key to a string.** `DT_I` builds `"\001i"` plus decimal digits by
repeated div/mod; the string is then hashed and collisions resolved with `strcmp`, and `table_set_descr_keyown` +
`rt_ws_strdup_c` allocate to own it.

Per-shape cost, store+load pair with an empty-loop baseline subtracted, SCRIP m3 vs `sbl -bf`:

| shape | SCRIP | SPITBOL | |
|---|---|---|---|
| 1-D `a[1]` | **33 ns** | 43 ns | **SCRIP 1.3× FASTER — the plain array path is fine** |
| 2-D `a[1,2]` | 73 ns | 44 ns | 1.66× slower |
| table **int** key `t[1]` | 71 ns | 44 ns | 1.61× slower |
| table **str** key `t['abc']` | 60 ns | 47 ns | 1.28× slower |
| chained `t['a'][1]['x']` | 185 ns | 82 ns | 2.26× slower |

⛔ **An integer key costs MORE than a string key (71 vs 60 ns)** — backwards, and the cleanest proof of the stringification.

⭐ **Second defect: an N-dimensional access emits exactly N subscript dispatches.** Counted from the emitted `.s`, store+load:
1-D = 2 calls (one per access), 2-D = 4 (two), 3-D = 6 (three). The address formula exists and is correct at
`aggregates.c:59-73`; it simply sits behind one wasted dispatch per extra dimension.

⛔⛔ **`a[1,2]` and `a[1][2]` ARE NOT THE SAME THING** (Lon, correcting HQ in-chat). `a[1,2]` is one subscript on an N-D array,
where N dispatches is a defect. `a[1][2]` subscripts the **object returned by** `a[1]` — two lookups there are correct and
unavoidable. Measured separately: chained `a[1][2]` store+load = 5 subscript calls + 3 `rt_deref` + 2 `rt_assign_var`. The
185 ns three-level table figure above is a **chained** case, not an N-D one, and must not be scored against the N-D row.

⛔ **Third, UNQUANTIFIED: `.NAME` has three representations and one is a string.** `descr.h:19,68-72` — `DT_N = 0x28`, `slen==2`
a name-trap pointer, `slen==1` a pointer, `slen==0` carrying `.s`, a character string. A name held as a string resolves by
lookup rather than by address. Lon flagged it; it is **not measured** and must be before anything is done about it.

### 7E.1 WHY "WRITE IT ALL IN ASM" IS THE WRONG FIRST MOVE, AND THE DATA THAT SAYS SO

The **1-D array path is already faster than SPITBOL while written in C.** Hand-writing a stringify-then-`strcmp` table in
assembly would win perhaps 20%; deleting the stringification is worth several times that. Order that pays: (1) type-tagged
hashing — hash a `DT_I` key from its integer value, compare descriptors, never build a string; (2) one dispatch per N-D access;
(3) *then*, if the residue is the call boundary, emit the subscript fast path as a `bb_*` box through the `x86()` encoder —
which is what "in asm" means in this architecture — but only once the algorithm underneath is right.

⛔ The wall-clock `TIME()` figures in this section are single-run and are trustworthy only for the ~2× effects they are used
for. Anything finer needs §7D's layout-swept protocol.

---

## 7F. ⭐⭐⭐ THE BIGGEST WIN OF THE SESSION WAS A FOUR-CHARACTER FIX — getenv() ON EVERY CALL

`string_manip` **0.29x → 0.61x** of sbl. `indirect_dispatch` **0.46x → 0.80x**. `eval_fixed` **0.59x → 0.91x**.

**Found by measurement, not by reading.** Per-box callgrind of `string_manip` put the emitted boxes at **1.8%** of the cycle
proxy — codegen was irrelevant — and `rt:getenv` at **22.6%**, 5.8M instructions and 86,132 branch misses, in a program that
never calls the `getenv` builtin. `callgrind_annotate --separate-callers=1` named the caller: `getenv'rt_call_arr` and
`getenv'rt_call_arr_impl`, **10,217 times each, 21.56% of the run**.

```c
static long _rspc = -1;
if (_rspc < 0) { const char *ev = getenv("SCRIP_CALLARR_TRACE");
                 _rspc = (ev && *ev && *ev != '0') ? 0 : -2; }
if (_rspc >= 0) { ...trace... }
```

The sentinel for **trace OFF is −2**, and the cache guard is **`< 0`**. −2 is less than 0, so in the only case that ever
occurs in production — the variable unset — the guard re-fires on every call and each one walks the whole environment doing
`strcmp`. The idiom *reads* as a cached env probe and is one; it simply never caches. **Enabling the trace would have hidden
the bug**, because then the sentinel is 0 and the guard finally holds.

Four sites, all on paths every function and builtin call takes: `by_name_dispatch.c:4634`, `:4650`, `core.c:2326`, `:2364`.
Guard changed `< 0` → `== -1`. Runtime swept for the same shape: **zero remaining**.

⛔ **THE LESSON: a cached-env-probe with a NEGATIVE "off" sentinel under a `< 0` guard is a silent per-call cost that appears
only when the feature is DISABLED.** Grep for the shape before adding another one.

⭐ And the methodological point: the row we had spent the session *not* looking at was 98.2% runtime C and 1.8% emitted boxes.
**Profile the row before optimising the compiler for it.**

---

## 8. WHAT IS LEFT — 120 INSTRUCTIONS, AND THEY ARE ALL THE SAME SHAPE

| box | Ir/iter | the waste |
|---|---|---|
| `binop_α` | 28 | 2 boxes; ζ-spine push/pop is most of what remains |
| `coerce_numeric_α` | 28 | 2 boxes that mostly **copy an already-numeric descriptor** |
| `var_α` | 24 | 4 boxes × 6 — move a global to the spine so the next box reads it back |
| `cmp_test_α` | 14 | |
| `lit_integer_α` | 10 | materialises a constant the binop no longer reads on the fast path |
| `assign_α` | 10 | |
| `statement_end_α` / `_begin_α` | 6 | `statement_begin` is two bare `jmp`s to the next label |

The next three cuts are one idea — **operand forwarding**: let a box read its operand where it already lives instead of round-tripping it through the ζ-spine. `lit_integer` is nearly dead already (finish the cold arms and it need not be emitted, −10); a `var` feeding a binop could read `[r9+off]` directly (−24); the `coerce_numeric` pair in front of a `cmp_test` that now does its own type dispatch may be redundant outright (−28). Plausible end state: **120 → ~60**.

⛔ **arith_loop was never SCRIP's problem.** The rows where we LOSE to the oracle, from the post-governor suite run (m3:sbl): `string_manip` **0.29x**, `indirect_dispatch` 0.46x, `roman` 0.46x, `table_access` 0.46x, `mixed_workload` 0.56x, `eval_fixed` 0.58x, `array_sum` 0.96x. A **3.4x deficit** on `string_manip` is worth more than another 2x on a row we already win 7.12x.

### 8.1 THE POST-GOVERNOR BASELINE (2026-08-22, `performance`, RT_OPT=-O0, floor re-baked the same hour)

| bench | sbl/s | m3/s | m4/s | m3:sbl | m4:m3 | min-det |
|---|---|---|---|---|---|---|
| arith_loop | 22.3M | 158.4M | 166.1M | **7.12x** | 1.05x | 1.3% |
| array_sum | 19.5K | 18.6K | 18.3K | 0.96x | 0.98x | 2.5% |
| eval_fixed | 6.1M | 3.5M | 3.8M | 0.58x | 1.07x | 4.6% |
| fibonacci | 6.6K | 35.7K | 36.5K | 5.44x | 1.02x | 2.6% |
| func_call | 13.0M | 92.1M | 89.6M | 7.07x | 0.97x | 1.8% |
| indirect_dispatch | 10.5M | 4.8M | 4.9M | 0.46x | 1.02x | 1.5% |
| mixed_workload | 290.3K | 161.6K | 152.9K | 0.56x | 0.95x | 4.1% |
| op_dispatch | 9.8M | 70.7M | 74.6M | 7.23x | 1.05x | 2.6% |
| pattern_bt | 1.0M | 3.0M | 2.9M | 2.92x | 0.97x | 6.3% |
| roman | 457.7K | 211.3K | 218.9K | 0.46x | 1.04x | 2.1% |
| string_concat | 5.3M | 17.8M | 18.2M | 3.36x | 1.02x | 3.6% |
| string_manip | 9.2M | 2.7M | 2.7M | **0.29x** | 1.02x | 10.3% |
| string_pattern | 3.8M | 5.8M | 5.8M | 1.52x | 1.00x | 14.9% |
| table_access | 17.8K | 8.2K | 8.1K | 0.46x | 0.98x | 4.3% |
| var_access | 8.5M | 62.4M | 75.0M | 7.31x | **1.20x** | 0.9% |

15/15 checks ok, gc=0 on every row. The re-baked floor is 0.3–3.8% cv on most rows (against up to 47.9% under the eight-seat load bake of s200), so this table can finally see a small regression. Two rows still cannot: `string_pattern` m3 (14.9%) and `string_manip` m3 (10.3%). `var_access` m4:m3 = 1.20x is a real m3-vs-m4 divergence on a 0.9% floor and is worth its own look — m3 ≡ m4 output is supposed to be a design invariant.

---

## 9. COMMITS

| repo | commit |
|---|---|
| SCRIP | `ec34eba0` — arith_loop +41.9%, 165→120 Ir/iter, NS-TIME |
| x64 | `ec80390` — SPITBOL `TIME()` ns on `CLOCK_MONOTONIC`, `bin/sbl` rebuilt |
| csnobol4 | `c5ead01` — `mstime()` ns on `CLOCK_MONOTONIC` |
| corpus | `6fb809ea2`, `fa80099d1`, `6e5992783` — `harness.inc` ns + regenerated `.s` artifacts |
| .github | `cbe1de27` — FACT RULE **NAME-16** |

All five pushed. `x64` and `csnobol4` had HTTPS remotes that cannot authenticate here; switched to SSH like the other three.
