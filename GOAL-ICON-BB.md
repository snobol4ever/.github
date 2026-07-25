# GOAL-ICON-BB.md — Icon, 100% Byrd Boxes, from zero

## ⛔ FACT RULE — ASM-RUNTIME: THE RUNTIME GETS FAST BY BEING HAND-WRITTEN x86, NOT BY BEING COMPILED HARDER (Lon directive, 2026-07-25 s159)

**The destination is a runtime built from hand-written x86 assembly fast paths shipped as `*.s` files and linked into `libscrip_rt.so` — registers and hand-chosen instruction sequences, NOT C that a compiler is asked to rescue.** C in the runtime is scaffolding: correct, readable, and the reference semantics for each operation. It is not the performance artifact. **THIS IS WHY THE BUILD STAYS AT `-O0` (or at most `-O1`) — the optimization level is not a lever we are declining to pull, it is a lever we are deliberately not building on.** A runtime whose speed comes from `-O2` is a runtime whose speed lives in GCC's inliner, evaporates under a compiler upgrade, and cannot be reasoned about register-by-register. A runtime whose speed comes from `*.s` leaves is one we own.

**THE s159 MEASUREMENT IS THE EVIDENCE FOR THIS DIRECTION, NOT AGAINST IT.** s156/s157/s158 each deferred `-O2` on `libscrip_rt.so` as "the biggest untried lever." s159 ran it under the full s126 protocol and it delivered **1.15×** — see `FINDING-2026-07-25-CLAUDE-ICN-BID-1-BUILTIN-ID-DISPATCH-AND-O2-FALSIFIED.md`. Asking the compiler to optimize the C bought almost nothing, because what is slow is *what the code does* (an O(n) by-name scan, a `DESCR_t` copied by value through every call, a heap cell minted per subscript), not how tightly it is compiled. Those are fixed by choosing different instructions and keeping values in registers — which is what an `.s` leaf does and what `-O2` cannot do for you.

**THE PROVEN PATTERN (s157, PERF-ASM-HELPERS, SCRIP `32ffde7f`) AND ITS PROVEN LIMIT:** `rt_deref` and `to_int` were rewritten as hand-written x86 (`+6%` nqueens n=10 at `-O0`), small-shape-inline / large-shape tail-jump to a C `*_slow` sibling, SysV AMD64 ABI verified against the emitted caller. **The limit found the same session: this works ONLY for leaves that make ZERO internal calls.** An asm `rt_subscript_var` came out ~3% SLOWER because two internal calls forced callee-saved push/pop around them, and the hand-written prologue lost to what the C already did. **So the rule for choosing an asm target is not "is it hot" — it is "is it hot AND a zero-internal-call leaf AND does it carry values that want to stay in registers across the whole body."**

**HOW AN ASM LEAF IS ADDED (the shape to follow):**
- The `.s` file lives beside the runtime source and is added to the Makefile's `RT_PIC_SRCS` so it links into `libscrip_rt.so` like any other TU. It must be `-fPIC`-clean (no absolute relocations into the `.so`).
- SysV AMD64 ABI, verified against the ACTUAL emitted caller, not against the C prototype's appearance: `DESCR_t` (16 bytes) comes in `RDI:RSI` and returns in `RAX:RDX`. Confirm by reading the emitted box, per `ARCH-ICON.md`'s register contract.
- **Honor the live register contract — it is NOT free real estate.** `RSP`=ζ under the `ZC_FRAME_RSP` default, `RBP`=ζ value-slot frame base, `R13`=Σ subject base, `R14`=δ cursor, `R15`=Δ subject length, `RBX` reserved as the WS/GC bump frontier under the HEAP arm. Clobbering any of these from a runtime leaf is a landmine that will not show up until a scan-heavy or GC-heavy program runs.
- Small/hot shape inline in asm; every cold, large, or error shape **tail-jumps to a C `*_slow` sibling** that keeps the reference semantics. The C stays; it stops being the hot path.
- Gate: full Icon suite unchanged (`PASS=249 FAIL=12 XFAIL=32` at s159) **plus** an A/B at identical emitted code — build one `P.o` and link it against two `.so` builds, per the DYNLINK recipe below.

**WHAT THIS MEANS FOR THE PERF LADDER:** a rung is "make this operation cheaper in instructions and registers," never "raise the optimization level." Any perf number reported must still carry its `RT_OPT` label (s126), and the Makefile default stays `-O0`. **`-O2` is now documented as measured-and-declined, not untried — do not re-propose it as the big lever.**

**LIMITATION (do not oversell — same honest shape as every rule here):** a markdown rule cannot make hand-written asm correct, and asm defects are far more expensive than C defects (wrong register saved, ABI mismatch, a clobber that only manifests under GC). The enforcement that works is the pairing: **zero-internal-call leaves only, a C `*_slow` sibling always retained, and the 293-program suite plus an identical-emitted-code A/B before any asm rung is called done.**

## ⛔ FACT RULE — O0-DEV: FEATURE BUILDS ARE `-O0`; `-O1`/`-O2` ARE PERF-ONLY (Lon directive, 2026-07-21 s119)

**While developing, debugging, or iterating on any FEATURE, EVERY build is `-O0`. `-O1` and `-O2` are FORBIDDEN during feature work and are reserved EXCLUSIVELY for perf/benchmark/release measurement.** The runtime `libscrip_rt.so` at `-O2` takes MINUTES (heavy template TUs), which is intolerable in a compile→test→fix loop and burned real session time repeatedly. `scrip` itself already builds `-O0` (Makefile `CBASE`/`CXXRT`); the offender was the runtime `.so`, whose `RT_OPT` default was `-O2`.

**THE MECHANICAL ANCHOR (why this is a FACT RULE, not a convention):** the Makefile default is now `RT_OPT ?= -O0 …` (SCRIP `Makefile` lines ~33 + ~281), so a bare `make libscrip_rt` / `make scrip` / `build_scrip.sh` is `-O0` by DEFAULT — the fast path is the path you get for free. `-O2` is now EXPLICIT opt-in, used ONLY for measurement:
```
make RT_OPT="-O2 -g -fno-strict-aliasing -fwrapv -fno-omit-frame-pointer" libscrip_rt   # perf/bench ONLY
PERF=1 bash scripts/jcon_selfhost_build.sh                                               # perf .so via the selfhost builder
```
Benchmark builders that need `-O2` already pass it explicitly (`jcon_selfhost_build.sh PERF=1`; the official-oracle trees build their own way), so the default flip does NOT silently corrupt any perf number — a perf run that forgets `-O2` is a mis-measurement the operator owns, not a default that lies.

**COMPLETION TEST:** (a) `grep -nE 'RT_OPT *[?:]?= *-O0' Makefile` matches (default is `-O0`) and no un-opted `RT_OPT ?= -O2` remains; (b) session-setup / feature-dev build scripts (`build_scrip.sh`, smoke/crosscheck runners) invoke `make` with NO `RT_OPT` override (so they inherit `-O0`); (c) any `-O2` in a script is either a monitor/oracle-side helper (separate lib) or gated behind an explicit perf flag (`PERF=1`); (d) this FACT RULE body is byte-identical across the six GOAL-*-BB files (md5-locked, per the Prolog file's sibling-verbatim note).

**LIMITATION (do not oversell — same honest shape as the other rules here):** a Makefile default and a markdown rule cannot COERCE a session to avoid typing `RT_OPT=-O2` during feature work; they make the fast path the default and the slow path a deliberate, visible choice. The human reviewer remains the real enforcer — **reject any feature-work handoff whose build log shows `-O2` on the runtime `.so`.**

## ▶ LIVE CURSOR (updated every handoff — RULES.md STALE-ORIENTATION rule)

**WATERMARK: SCRIP `see below` · suite PASS=249 FAIL=12 XFAIL=32 / 293 · tgrlink 188ms (1.20× vs pre-session 212ms; 0.80× vs iconx 150ms) · RT_OPT=-O0.**

- **s163 (2026-07-25, Sonnet 4.6) — HP-1 + HP-2: hugepage arena + virgin-zero elision. tgrlink 212→177ms (1.20×), queens 67→51ms, concord 95→62ms. Zero regression.**
  **KEY FINDING:** SCRIP already beats iconx on Ir (1.307G vs 1.339G) and branch mispredicts (11.3M vs 25.8M). The gap is 25× LL cache misses and 25× page faults — virgin bump-alloc through 61MB of cold memory vs iconx's 8.3MB warm heap. Instruction rungs cannot close this gap. Full findings: `FINDING-2026-07-25-CLAUDE-ICN-MEM-1-HUGEPAGE-VIRGIN-ZERO-ELIDE-AND-GC-ABORT-DIAGNOSIS.md`.
  **GC ABORT FINDING:** GC fires on tgrlink at ≤16MB and aborts (not wrong output). Basic GC correctness is demonstrated (800MB churn, all struct types down to 4–8MB). Root cause NOT yet determined: over-retention vs legitimately large live set. See FINDING for separation protocol.

### ▶ NEXT RUNG — GC LIVE-SET MEASUREMENT (prerequisite for warm-nursery path)

Instrument `rt_gc_collect()` to print bytes-live before and after one collection on tgrlink. Compare against expected reachable set. Two outcomes: (A) over-retention confirmed → fix GC, shrink heap, gain warm-nursery perf; (B) legitimately large live set → SCRIP representation overhead is the issue, different fix. Either way this gates the structural memory improvement. **~30-minute rung.** After this: BID-AT-LOWER.

- **s162 (2026-07-25, Opus 4.5) — LV-1 + VV-1, SCRIP `556d9b7c` + `030d6263`. tgrlink Ir −12.63% (**1.1446×**), zero regression.**
  **LV-1 (−9.76%):** the five list builtins (`get`/`put`/`push`/`pop`/`pull`) reached the list frame BY NAME. `FIELD_GET_fn(ld,"gen_type")` cost **224 Ir/call** (field index 2 → three `strcasecmp`s) vs `"frame_elems"` **102 Ir/call** (index 0) — **cost tracked field POSITION, which is what proved the scan was the expense.** `rt_list_view` promoted to `src/runtime/rt/rt_list_view.h` and adopted at all five. `strcasecmp` (6.70%) and `FIELD_GET_fn` (4.14%) left the profile top. Zero-regression BY CONSTRUCTION: each arm keeps its by-name body as fallback, and `FIELD_SET_fn`'s only side effect (`rt_sxt_break`) fires on DT_S, which these sites never write.
  **VV-1 (−3.18%):** `VARVAL_fn` was **780 Ir × 111,601 calls, ALL from `right()`** — its DT_I arm ran `snprintf`. Replaced with direct digit conversion (INT64_MIN-safe).
  Full detail: `FINDING-2026-07-25-CLAUDE-ICN-LV-1-VV-1-LIST-SLOTS-AND-SNPRINTF-AND-THE-STRUCTURAL-GAP.md`.

### ▶ NEXT RUNG — BID AT LOWER TIME (the structural one; runtime ladder is spent)

`bid_of` burns **75,177,697 Ir (5.57%) over 533,135 calls**: LOWER knows which builtin `get` is, discards it, and the runtime re-hashes the string every dispatch — plus a per-dispatch uppercase `switch` (1.64%) and `_setjmp` (1.50%). **Rung:** `lower_icon.c` resolves a known-builtin callee to its `BID_*` and the emitter passes the INTEGER; `src/runtime/builtin_ids.h` already generates the table. **This changes the emitted call's argument shape, so it must land in BOTH media (`bb_call.cpp` + the `x86()` encoders) under BOTH-MEDIUM MANDATORY — a dedicated full-budget rung; half-landing it is worse than not starting.** Then: emitted inline fast paths so scalars stop entering the runtime (`dop_direct_fp` in `bb_call.cpp` is the precedent; operators/known builtins cannot be shadowed, so early binding is sound by construction).

**⛔ WHY NO RUNTIME RUNG REACHES 2–3×.** `iconx` is a bytecode interpreter and SCRIP emits native code, yet loses. That is not one hot function — **every scalar op still round-trips through a by-name runtime call.** `IR_BINOP_ARITH` already emits a correct inline DT_I fast path (verified in the emitted `.s`: `add rax, rcx`), proving the emitter CAN do this; `get`/`put`/`right`/`integer` cannot, because they exit through `rt_call_arr` by name. **Until the call spine stops being by-name the ceiling is near parity.**

## ⛔ STANDING NEGATIVE RESULTS — MEASURED, DO NOT RETRY

**THE RULE THEY ALL PROVE: at `-O0`, adding a TEST to avoid a short libc call is a LOSING trade, and making each step cheaper cannot fix a complexity class. ONLY REMOVING WORK OUTRIGHT PAYS.** (LV-1 deleted a scan, VV-1 deleted format parsing, SORT-1 deleted an O(n²) — all three paid.)

| Tried | Measured | Session |
|---|---|---|
| `-O2` on `libscrip_rt.so` | **1.15×** — falsified as "the big lever"; documented measured-and-declined | s159 |
| Instruction-shaving rungs to close the iconx gap | **STRUCTURAL MISMATCH** — SCRIP already beats iconx on Ir (1.307G vs 1.339G) and branch mispredicts (2.3×). Gap is 25× LL cache misses + 25× page faults (cold 61MB arena vs iconx 8.3MB warm heap). No instruction rung can fix this. | s163 |
| `switch(_bid)` jump table over the 197-arm chain | **2.4%** — dispatch is not the elephant; the bodies are inline real work | s160 |
| First-char / case-folded guards on field scans | **+1.4% WORSE**, reverted (`tolower()` is an out-of-line locale call at `-O0`) | s161 |
| `always_inline` carve + inline zero for payload ≤ 64B | **+0.06%, a wash**, reverted byte-identical | s162 |
| asm `rt_subscript_var` | **~3% SLOWER** — two internal calls force callee-saved push/pop; fails the zero-internal-call test | s157 |
| Value-subscript fusion | no win despite removing 3M allocs + 3M boxes; reverted | s-SUBSCRIPT-FUSE |
| `(DATBLK_t*, fn)` pointer-keyed memo cache | **UNSOUND** — a stale hit is silently wrong; key on CONTENT and verify on every hit if ever revived | s159/s160 |
| `goto`/label dispatch past the chain | **UNSOUND** — an unconditional `strlen`+`switch` block sits in the chain; a `goto` past it skips live code | s159 |

**⚠ A FIRST-CHAR GUARD IN THE 288-ARM SCRIPT FALLBACK IS WRONG.** Lines 1630–2400 suggest every literal starts with `$`/`_`; the full 2,259-line body has 288 literals of which **68 are bare names** (`open` `close` `trim` `length` `where` `seek` …). Audit the whole function, not the window you printed.

**⚠ BEFORE OPTIMIZING A HIGH-CALL-COUNT FUNCTION, CHECK WHETHER ONE CALLER GENERATES ALL THE CALLS.** SORT-1: 6,476,858 of `VARVAL_fn`'s 6,630,400 calls came from one line. VV-1: all 111,601 came from `right()`. Both times that reframed the fix.

**⚠ CORRECTNESS GAP, DELIBERATELY NOT FIXED (own rung):** canonical `anycmp` (`refs/icon-master/src/runtime/rcomp.r`) orders by type collating number first via `order()`, comparing only within a type; SCRIP does "both-int numeric, else stringify and strcmp". Agrees on homogeneous tables/lists, **diverges on mixed-type.** Changing sort ORDER would move output on the 249 green tests.

## ⚠ MEASUREMENT PROTOCOL

- **Ir (callgrind) is the honest metric.** Wall-clock on this corpus is startup-dominated (`version` is 4ms of pure startup; `concord` once moved 97→114ms across a change that LOWERED Ir). Trust wall-clock only on `tgrlink`/`geddump`.
- **Label every perf number with its `RT_OPT`.** Default is `-O0`; `-O2` needs a Lon directive in-session (FACT RULE O2-DIRECTED-ONLY).
- **A/B a runtime change at IDENTICAL emitted code:** build ONE `P.o`, relink it against two `.so` builds.
  `scrip --compile --target=x86 P.icn > P.s && as --64 -o P.o P.s && gcc -no-pie -o P.bin P.o out/libscrip_rt.so -lm -lstdc++ -Wl,-rpath,$PWD/out`
- **Build loop:** after editing runtime `.c` / template `.cpp` → `make libscrip_rt` then `make scrip` (≈22s + 1s). **Header edits are NOT dep-tracked — `rm -rf out/rt_pic` to force a full recompile.**
- **Oracle-diffing bench:** `scripts/honest_icon_bench.sh` (compares stripped output vs iconx). Use it, NOT `test_icon_bench_corpus.sh`, which grades on `rc==0 && non-empty` and cannot tell "fast" from "skipped the workload".
- **`valgrind` installs with `apt-get install -y valgrind` (root, no sudo). Profile BEFORE optimizing — intuition has been wrong here repeatedly.**
- Diagnostic: `SCRIP_BID_PROF=1` prints the builtin-id histogram.

## ▶▶ ZERO-FAILURE MANDATE: END STATE = 289/0/0. Re-derive counts fresh from `test_icon_all_rungs.sh` — never from prose.

### ▶ FAIL-ZERO — 12 live FAILs

**Cluster A — env math-drift (not code bugs):** `rung17_real_arith_*`, `rung19_pow_toby_*`, `rung26_pow_real_pow`, `rung30_builtins_misc_sqrt`, `rung37_math_hello`. Vary run-to-run; re-derive fresh before attacking.

**Cluster B — emit-time IR aborts:**
- [ ] **FZ-B1** — `rung36_jcon_var` — `emit_drive IR_ASSIGN guard: nameless 2-operand assign`. Fix in `lower_icon.c` TT_ASSIGN lvalue path. Also needs `rt_icon_variable(name)` per-proc name→frame-offset table for locals.
- [ ] **FZ-B2** — `rung36_jcon_scan` — `bb_call marshal: IR_VAR arg names a local with no LOWER-granted varslot (TE-4)`. Grant varslot in `ir_drive_slot_assign`.

**Cluster C — SEGV rc=139:** run under `CSN_NO_SEGV_HANDLER=1` for a clean backtrace; MONITOR→bracket→gdb.
- [ ] **FZ-C1** — `rung36_jcon_endetab`
- [ ] **FZ-C2** — `rung36_jcon_fncs1`
- [ ] **FZ-C3** — `rung36_jcon_scan2`

**Cluster D — parse errors (`function call: expected ) (got ;)`):**
- [ ] **FZ-D1** — `rung36_jcon_htprep` (line 160)
- [ ] **FZ-D2** — `rung36_jcon_prepro` (line 39) — *(note: may already be fixed; re-run first)*

**Cluster E — wrong output, ran clean:** MONITOR-FIRST; bracket the first divergent event.
- [ ] **FZ-E1** — `rung36_jcon_args`
- [ ] **FZ-E2** — `rung36_jcon_coerce` *(⚠ can emit ~241MB; always `| head -c` when running manually)*
- [ ] **FZ-E3** — `rung36_jcon_mffsol`
- [ ] **FZ-E4** — `rung36_jcon_mindfa`
- [ ] **FZ-E5** — `rung36_jcon_kwds`
- [ ] **FZ-E6** — `rung36_jcon_scan1`
- [ ] **FZ-E7** — `rung36_jcon_string`

### ▶ XFAIL-ZERO — 32 `.xfail` markers

Per marker: remove `.xfail`, run, read the real failure, fix SCRIP or the source artifact, delete the marker. Some may already pass (free win).
- [ ] **XZ-3** `radix` — bignum: literals > 64 bits need arbitrary-precision ints.
- [ ] **XZ-4** `lgint` — same bignum gap.
- [ ] **XZ-5** `ck` — generative arg to `tab(span-1|0)`; `Image()` needs generator-in-arg.
- [ ] **XZ-7** `profsum` — `next` inside `line ? {}` doesn't restart enclosing `while`.
- [ ] **XZ-8–11** (reserved)
- [ ] **XZ-E-BIGNUM** — arithmetic cluster (`arith`, `checkfpx`, `cxprimes`).

**Empty markers (24) — classify on a fresh run, then fix or delete:** `arith btrees case checkfpx collate cxprimes diffwrds errkwds errors evalx every fncs geddump gener image io iobig large misc nargs others prefix recent sets sieve sorting struct toby`.

## Permanent notes

**⛔ ORACLE IS icont/iconx — NEVER INSTALL JAVA OR RUN THE JVM SELF-HOST PATH (Lon directive, 2026-07-21 s121).** Validating SCRIP's Icon front-end needs no Java, `jcon.zip`, `jtran`→`jlink`→JVM, or JCON bytecode execution — that whole pipeline is a TIME SINK and was mistakenly walked end-to-end in s121. The ONLY sanctioned check: run under `scrip --run` (mode 3) and/or `scrip --compile`+link (mode 4), run the SAME program under Arizona Icon (`icont -s prog.icn -x`), and DIFF. Build the oracle once from the uploaded source: `cd icon-master && make Configure name=linux && make` → `bin/icont`, `bin/iconx` (v9.5.25a). For JCON *compiler* modules (`tran/*.icn`, no `main()`), the Java-free equivalent is to byte-compare SCRIP-jtran's emitted bytecode as DATA. **If a step needs `java`/`javac`/`jar`, it is the wrong step.**

**⚠ Harness blind spot:** `test_icon_all_rungs.sh` grades stdout only (exit code discarded). Use `/tmp/icon_m3_honest.sh` for a crash-aware CLEAN/DIRTY split.

**FZ-B1 `var` detail:** `lower_lvalue_var` has no case for `variable(...)` as lvalue → TT_ASSIGN mints a nameless placeholder → emitter abort. Awaits Lon's call on name-table form (sealed RO blob vs startup-built table).

**FZ-E scan root (recogn/scan/scan1/scan2):** emitter wires the SCAN_MATCH fail-edge to arm-B beta (resume, mid-flight) not alpha (fresh start). Land mine: `emit.cpp` ~L887-904 / IR_SCAN_SEQUENCE ~L1101.

**Open residuals (not in FAIL-ZERO):** `type()`/`image()` for record constructors return `"function"` not `"procedure"`/`"record constructor N"` — `by_name_dispatch.c` type() DT_E branch. Pre-pinned regressions: geddump/tgrlink → `git revert 7aade169`; ipxref → LOWER-side `lower_alt` arm-interior BFS slot-wiring. `geddump` diverges 11,222L vs oracle 10,145L; `rsg`'s 2.88× is noise/short-circuit until its DIVERGE is explained — neither counts as a win.

**Baselines:** 2026-07-01 `6a509382` 190/63/36 · R12 `b404fb95` 242/15/32 · s162 `030d6263` 249/12/32.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
**Architecture:** `ARCH-ICON.md` · `ARCH-x86.md` · `GOAL-ICON-BB-NATIVE.md`

## Session-close / push protocol
See RULES.md — `scripts/handoff_status.sh` verbatim stdout is the ONLY sanctioned completion claim.
