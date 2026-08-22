# ARCH-PERF-TOOLING — the empirical stack for BEAUTY-10X

**Opened 2026-08-21 by Lon in-chat, verbatim in substance:** *"Let's get beauty self host highly optimized using empirical techniques like valgrind giving STATEMENT and BB level coverage information. And a perf tool where we make global in the executable labels of choice and get call graph performance data … 10 times faster than SPITBOL. Well I'd be happy with 3-5 times faster. But I stuck that 10x banner up 4.5 months ago."* Priority #1 now that Milestone 1 (beauty self-host, s197) is landed. **No fleet — Lon and HQ only** (supersedes HQ-69; see `GOAL-SCRIP-HQ.md`).

**Two standing directives from Lon, binding on everything below:**
1. ⛔ **`-O2` is not an answer to a slow C function.** The answer is to rewrite it as highly optimized register-aware x86-64 asm. Per the repo's own law that asm ships through `x86(...)` in `src/templates/x86_asm.h` and is **inlined into the `bb_*.cpp` template**, not written as a new C function ("No C Byrd-box functions").
2. **Empirical over intuitive.** No optimization lands without a before/after number.

---

## 0. THE ARCHITECTURAL FACT THAT PICKS THE TOOLS

SCRIP is **not a call/return machine**. Byrd-box ports (α proceed, β recede, γ succeed, ω concede) are wired at compile time into `jmp`. There is no call stack to unwind inside the wired region, so **classic call-graph profiling is the wrong model** — a flame graph of the slab is nearly flat and tells you almost nothing.

The right model is **edge profiling over a control-flow graph**: which α/β/γ/ω edges are hot, and which are mispredicted. Two consequences:

- `callgrind --collect-jumps=yes` is the primary instrument, not `perf record --call-graph`.
- `--dump-bb` **already emits the box graph as JSON** (for `tools/bb_viewer.html`). Joining callgrind edge counts onto that JSON gives a heat-mapped Byrd-box graph — the single most informative view available to this project, and it costs one script.

The second fact: **two modes, two toolchains.**

| | m4 `--compile` | m3 `--run` (default) |
|---|---|---|
| Output | real ELF via `as`+`gcc`, links `libscrip_rt.so` | flat-wired blobs in a sealed RX slab |
| Tool support | everything works today | shows as `[unknown]` — needs a JIT map (§2.1) |
| Use it for | all deep analysis | end-user wall clock, and parity checking |

Do the analysis in **m4**. `m3 ≡ m4 output is a design invariant`, so an m4 finding is an m3 finding.

---

## 1. INSTALL LIST (Lon has sudo; all verified available 2026-08-21)

```bash
sudo apt install -y \
  linux-tools-6.17.0-1032-oem linux-tools-common \   # ⛔ perf is BROKEN without this (wrapper only)
  kcachegrind hotspot heaptrack heaptrack-gui massif-visualizer \
  llvm graphviz binutils
git clone https://github.com/brendangregg/FlameGraph ~/FlameGraph   # differential flame graphs
```

Already present: `valgrind 3.22.0` (callgrind, cachegrind, massif, **dhat**), `callgrind_annotate`, `cg_annotate`, `objdump`, `gdb`.

**Machine:** AMD Ryzen 7 PRO 8840U (**Zen 4**), 8C/16T. `perf_event_paranoid=1` (own processes fine, kernel symbols not). `ibs_op` + `ibs_fetch` PMUs **present** — AMD Instruction-Based Sampling is available, which is the precise (skid-free) sampling path, Zen's PEBS equivalent. ⚠️ `toplev.py`/pmu-tools is **Intel-only** — don't reach for it here; use `perf stat` metric groups instead.

⚠️ Pin the clock before any wall-clock number: `sudo cpupower frequency-set -g performance`. The 8840U is a mobile part and boosts erratically — `CPU(s) scaling MHz: 47%` was observed idle. Unpinned wall-clock A/B on this box is noise.

---

## 2. THE PLUMBING — three items that make every tool speak SNOBOL4

These are compiler-side, done once, and they multiply the value of everything after.

### 2.1 A perf map for mode 3 — *this is Lon's "global labels of choice"*
perf reads `/tmp/perf-<pid>.map` for any address it can't resolve. Format is one line per region:
```
<hex-start> <hex-size> <symbol-name>
```
Emit one line per Byrd box as the slab is sealed, behind an env guard (`SCRIP_PERF_MAP=1`) so shipped runs write nothing. ~20 lines of C in the slab builder. Payoff: every `[unknown]` in `perf report` becomes a named box.
**Upgrade path:** jitdump (`/tmp/jit-<pid>.dump` + `perf inject --jit`) gives per-region ELF + DWARF, so `perf annotate` and source lines work *inside* the slab too. Do perf-map first; it is 90% of the value for 10% of the work.

### 2.2 DWARF line directives in m4 — statement-level everything, for free
Emit `.file 1 "beauty.sno"` once and `.loc 1 <line> <col>` ahead of each statement's instructions. Then, with no further work:
- `perf annotate --source` and `perf report --sort=srcline` attribute cycles to **SNOBOL4 source lines**
- `callgrind_annotate --auto=yes` prints the `.sno` source with instruction counts in the margin
- `objdump -dS` and gdb `list` show SNOBOL4 next to x86
- **statement-level coverage falls out**: count 0 = never executed

**Medium note:** `.loc` is a TEXT-medium directive, so BOTH-MEDIUM MANDATORY applies. The clean shape is a new medium-complete op — `x86("loc", file, line)` — that emits a `.loc` directive in TEXT and records a map entry in BINARY, exactly as `x86("label")`/`x86("comment")` already do.

### 2.3 Real symbols per box in m4
Emit `.globl <box>`, `.type <box>,@function`, and `.size <box>, .-<box>` for each box. Tools then treat every Byrd box as a first-class symbol *with an extent*, which is what makes `perf annotate` per-box, `objdump` sectioning, and callgrind's function-level rollup work at box granularity instead of lumping the whole blob into one nameless region.

---

## 3. THE INSTRUMENTS, BY THE QUESTION THEY ANSWER

### Q1 — "What kind of bound am I even?" *(ask this FIRST; the answer redirects everything else)*
```bash
perf stat -r 20 -e cycles,instructions,branches,branch-misses,\
L1-icache-load-misses,L1-dcache-load-misses,stalled-cycles-frontend,stalled-cycles-backend \
  ./scrip --compile-built-beauty < beauty.sno
```
Read **IPC**, **branch-miss rate**, and the frontend/backend stall split.
**Prior for this machine:** a backtracking pattern matcher wired as jumps should be **bad-speculation bound** — every β (recede) port is a backtrack, and backtracks are inherently unpredictable. Flat-wiring also inflates code size, so **frontend-bound** is the other candidate. If either confirms, the lever is *box fusion* and *fewer unpredictable branches* (cmov/branchless idioms in hot leaves), **not** faster arithmetic.

### Q2 — "Which statement, which box, exactly?" *(deterministic — the workhorse)*
```bash
valgrind --tool=callgrind --dump-instr=yes --collect-jumps=yes \
         --cache-sim=yes --branch-sim=yes --callgrind-out-file=cg.out ./prog
callgrind_annotate --auto=yes --threshold=99 cg.out
kcachegrind cg.out          # callee-map treemap + edge-annotated CFG
```
Gives per-instruction counts, **per-jump-edge counts** (= the Byrd port profile), simulated I/D cache misses and branch mispredicts. 20–100× slowdown, irrelevant for beauty.
Zero-count regions are **coverage**: never-executed boxes are both dead weight and a bug smell.

### Q3 — "What does real silicon do?" *(AMD-specific)*
```bash
perf record -e ibs_op//p -c 50000 -- ./prog     # precise, skid-free (Zen IBS)
perf record --call-graph=fp -F 4000 -- ./prog   # RT_OPT already carries -fno-omit-frame-pointer
perf annotate --source
hotspot perf.data                               # GUI: flame graph + caller/callee + timeline
```
IBS also reports load latency and miss info per sample, which is how you find the specific load that stalls.

### Q4 — "Is this hand-written asm sequence actually good?" *(the asm-writing loop)*
```bash
llvm-mca -mcpu=znver4 -timeline -iterations=100 seq.s
```
Static: uop counts, **execution-port pressure**, dependency chains, estimated IPC, and a cycle-by-cycle timeline. Tells you *port-limited vs latency-limited* without running anything — the exact question when writing register-aware asm. Confirm with `perf stat -r 20` on a microbench loop. Read the truth with `objdump -d -M intel`.
Cheap experiment worth running early: `.p2align 4`/`.p2align 5` on hot loop heads — Zen 4's op cache is alignment-sensitive.

### Q5 — "Where is the allocation pressure?" *(beauty is string-heavy; this matters)*
```bash
valgrind --tool=dhat ./prog        # ⭐ the standout
valgrind --tool=massif ./prog ; massif-visualizer massif.out.*
heaptrack ./prog ; heaptrack_gui heaptrack.*.zst
```
**DHAT is the one to run.** Per allocation site it reports total blocks, bytes, **average lifetime**, and **read/write counts**. The pattern it finds in descriptor-heavy runtimes — *"allocated 48 bytes, written once, read twice, freed immediately"* — is a direct nomination for stack or inline allocation. This is usually where the surprise win is.

### Q6 — "Show me something beautiful"
- **KCachegrind** callee-map treemap — still the best profiling GUI ever made.
- **Differential flame graphs** (red/blue) between two commits: `stackcollapse-perf.pl` → `difffolded.pl` → `flamegraph.pl`. Red = got slower. This is the A/B view.
- **The bespoke one:** join callgrind `--collect-jumps` edge counts onto the existing `--dump-bb` JSON and heat-map `tools/bb_viewer.html`. Hot α/β/γ/ω edges in red. Nobody else has this view of a program.

---

## 4. WHERE THE 10X ACTUALLY COMES FROM

Tools find the work; they do not do it. The project's own measurements already name the targets — this is a ranking, not a guess:

1. **Kill the table path.** s199 measured *"the table path is 91 percent"*. A hash lookup per variable reference, where a compile-time-resolved slot offset would do, is the whole ballgame — order-of-magnitude on the dominant operation. Resolve names to fixed slots at compile time wherever the program does not construct names dynamically; keep the table only for genuine `$` indirection. **This is a binding problem, not an asm problem, and it is the single biggest lever.**
2. **Inline concat and store.** s200: *"PLUS is already inlined, LT/concat/store are not."* Every concat is a call out to `libscrip_rt.so` — PLT indirection + ABI shuffle + frame + descriptor spill. For short strings the call overhead exceeds the work. Inline a fast path ("fits in remaining capacity → memcpy") into the wired blob and the call disappears entirely.
3. **Box fusion.** s250: *"slot coalescing is negative, box fusion is the real lever."* Fewer boxes ⇒ fewer jumps ⇒ fewer mispredicts ⇒ smaller I-footprint. Attacks the likely Q1 answer directly.
4. **Kill the PLT.** ⭐ *Free, structural, nobody has tried it.* `out/libscrip_rt.so` is built `-shared` and linked dynamically on purpose, so runtime edits only need a `.so` rebuild — but that convenience taxes **every single runtime call** with GOT/PLT indirection. For benchmark and demo builds, static-link the runtime, or at minimum build with `-fno-plt -fvisibility=hidden -Wl,-Bsymbolic-functions`. Costs no asm and is measurable in an afternoon. Keep the `.so` for development.

**Then** hand-write register-aware asm on the leaves that survive. Doing it before steps 1–4 means polishing a leaf that is called through a PLT inside a 91% table path — beautiful work that will not show up in the number.

### ⚠️ On `-O0` vs `-O2` — the one place `-O2` still earns its keep
Lon's directive stands: `-O2` is not the *solution*. But `RT_OPT` defaults to `-O0`, where **every C local is a stack spill**, so an `-O0` profile nominates functions whose cost is a build artifact rather than an algorithm. Writing asm against that list wastes effort on leaves `-O2` would have made free, and the win won't materialize.

**Use `-O2` as a measurement lens, never as a shipped answer:** profile once at `-O2` to identify what is *genuinely* hot, then hand-write asm that beats `-O2`. That is a real bar and clearing it is a real result. (s198 already found the `-O2` arm red on Milestone 1 — so this lens needs that fixed first, or applied only to isolated leaves.) Label every number with its RT_OPT, per O0-DEV-O2-BENCH.

### Measuring against SPITBOL, honestly
`sbl -bf` **compiles and runs** in one invocation, so a naive comparison charges SPITBOL for compile time SCRIP paid earlier. Either separate compile from run on both sides, or amortize with an input large enough that compile time vanishes. State which you did next to every ratio.

---

## 5. THE DISCIPLINE — an instruction-count gate

Wall clock on a boosting mobile CPU is noise; **callgrind's `Ir` total is exact and reproducible to the instruction**. Pin beauty self-host's Ir count in a gate script with a tolerance band, and commit-to-commit deltas become trustworthy signal — a regression is visible the moment it lands, not three weeks later. s249 already reasoned in terms of an *"arith loop instruction budget"*, so the idiom is native here. Pair every gate number with a wall-clock number labeled with its RT_OPT.

---

## 6. FIRST SEQUENCE

1. `sudo apt install` the list in §1; pin the governor.
2. `perf stat -r 20` on beauty self-host → answer Q1. **Everything downstream is chosen by this result.**
3. Callgrind + `callgrind_annotate --auto` → the hot statement and hot box list; open it in KCachegrind.
4. DHAT → the allocation-pressure list.
5. Land the two zero-risk structural experiments (`.p2align` on hot heads; the `-fno-plt`/static-link arm) and measure both — these need no asm and may be worth a chunk on their own.
6. Only then start writing asm, with `llvm-mca -mcpu=znver4` in the loop.

Findings route to `FINDING-*.md` as they land; the cursor for this campaign lives in `GOAL-SNOBOL4-100.md`.

---

## 7. QUEUE PRIORITY POLICY (Lon s251)

Lon, in-chat: *"Organize all task by priority based on current knowledge of bottlenecks on benchmarks, demos, and beauty. Those three are most important to me as examples of speed"*, then: **"Put all performance items higher priority than all others."**

`QUEUE.tsv` was re-ranked accordingly — 129 rows, **48 performance rows occupying ranks 0–4, above all 81 others**. Prior ordering is preserved in `QUEUE.tsv.bak.s251`.

| rank | n | meaning |
|---|---|---|
| **0** | 15 | **PERF BLOCKER** — the program will not run, or the number it prints is a lie. Nothing downstream is measurable until these clear. |
| **1** | 10 | **TOP RUNTIME LEVER** — measured, mode-4 runtime, largest known wins. |
| **2** | 17 | **SECONDARY CODEGEN** — real but smaller or unmeasured. |
| **3** | 4 | **PERF INFRASTRUCTURE** — makes every later row cheaper to work. |
| **4** | 2 | **COMPILE-SIDE PERF** — pays into `CODE()`/`EVAL()` and the dev loop, *not* the m4 benchmark (Lon s251: *"If you measure compile time of the program that is not a benchmark"*), hence ranked below every runtime row. |
| 5–8 | 81 | correctness · parser/feature · harness/hygiene · admin, relative order preserved. |
| 99 | 1 | `beauty-fixed-point`, an explicit HOLD gate row, untouched. |

**Rank 0 is deliberately not all "make it faster."** A benchmark that grades against the wrong oracle arm, a harness that adds a procedure boundary, an instrument with a permanent noise floor, a demo with no corpus row, and a `match_ms` that reports 11 minutes for a 3-byte parse are all ways of producing a *confident wrong number*. Those rank above optimization because optimizing against a false measurement is worse than not optimizing.

**Two rows were re-scoped by this session's evidence:**
- `chain-slot-coalescing` sat at rank 0 pursuing slot coalescing, which FINDING-2026-08-21-s250 **measured as negative**. Demoted to rank 2 pending re-scope; the successor `box-fusion` — the lever s250 actually named, and which was never queued — is filed at rank 1.
- `pt-group-defer` (*group defer = 59.4% of all treebank-match cycles) was at **rank 12** despite being a measured demo bottleneck. Promoted to rank 1.

**The instruction-count argument behind the whole ranking** (FINDING s251 §2): SCRIP already beats SPITBOL on every microarchitectural axis — IPC 3.20 vs 2.33, mispredicts 0.14% vs 0.83%, frontend idle 4.93% vs 22.70%. It is **instruction-count bound**, so hand-written register-aware asm and box-level polish are capped near 1.4× and are the *last* mile. Rank 1 is therefore populated by rows that delete work (table path, PLT indirection, un-inlined calls, fused boxes), not rows that shave cycles off work that stays.
