**WATERMARK: SCRIP `f0e1e011` · suite PASS=250 FAIL=11 XFAIL=32 / 293 · RT_OPT=-O0 · Icon bench vs iconx 9.5.25a: correctness **8/8 byte-identical** (rsg CLOSED).**

## ▶ LIVE CURSOR (s167, 2026-07-26)

**NEXT RUNG:** FZ-B1 / FZ-B2 cluster or XFAIL-ZERO sweep — rsg is closed, bench is 8/8. Suite at 250/11/32; 11 remaining FAILs are Cluster A (env math-drift, 5), Cluster B (emit-time IR aborts, 2), Cluster C (SEGV, 3), Cluster D (parse errors, 2) per FAIL-ZERO table below. Re-derive counts fresh from `test_icon_all_rungs.sh` before attacking.
**WATERMARK:** SCRIP `f0e1e011` · suite 250/11/32 · bench correctness 8/8 IDENTICAL.
**LAST SESSION:** s167 — rsg FIXED (ICN-CASE-ALT alpha-force gate widened to check entry-node generator-kind, not just source-tree is_resumable); bench correctness 7/8 → 8/8; suite 249/12/32 → 250/11/32. Also: JCON self-host tested across all 17 modules (10/17 COMPLETE, 7 SHORT); `many`/`any` elided-startpos defect root-caused and causally proven; `ir.class` 9.6× blowup flagged; perf benchmark 2.22× SCRIP slower (geomean, RT_OPT=-O0 vs iconx -O, verified-equal-work modules only). See `FINDING-2026-07-26-CLAUDE-ICN-RSG-CASE-ARM-ALPHA-FORCE-GATE-WIDENED-AND-SELFHOST-7MODULE-GAP.md`.

⛔ **s164/s165's `rsg` pointers (`defnon`, `syms` `nsym=0`, "grammar table never populates") are STALE and
MEASURED FALSE — s165b's fix cascaded further than credited. Do NOT re-chase them; the grammar table is
correct inside the running program.** The real defect: **a disjunction leading a MULTI-statement `case` arm
selects its LAST arm instead of its first.** Repro (`corpus/programs/icon/repro/rsg_case_arm_disjunction.icn`):
`case type(x) of { ... "string": { pending := [1,2] | [9]; n +:= 0 } }` → iconx `int=1 int=2 iters=3`,
SCRIP m3+m4 `int=9 iters=2`. Three necessary ingredients, each measured by removal: (1) `case` — the same
body under `if` is CORRECT; (2) the arm's FIRST expression is an assignment whose RHS is a disjunction —
a plain assign is CORRECT; (3) at least one MORE expression follows in the arm — the assign alone is
CORRECT. `break` is NOT involved. IR evidence: the ONLY wiring difference is the dj's **ω edge** (case glue
`24@` when the arm ends there vs the trailing statement's own slot `29` when one follows). **START IN THE
EMITTER** (`emit.cpp` L1100/L1101/L1112 + `bb_disjunction()`), NOT `lower_icon.c`. Fixing it closes the last
bench defect (8/8) and plausibly part of FZ-E.


- **s165 (2026-07-25) — BENCH-HONESTY-2 + `geddump` ROOT-CAUSED. SCRIP `fbce47dc`. No codegen touched.**
  **THE CORRECTNESS HARNESS WAS GRADING `geddump` — a KNOWN LIVE DEFECT — AS A PASS.** `honest_icon_correctness.sh`'s `window()` extracts between post.icn's marker and the elapsed-time line; `geddump`/`micsum`/`tgrlink` DO NOT LINK post.icn, so the window came back EMPTY on both engines and `cmp` of two empty files printed IDENTICAL. Fixed: fall back to whole file when the marker is absent, and grade two empty windows `NO-OUTPUT`. Mirror defect fixed in `honest_icon_bench.sh`, which claimed a correctness verdict from a run whose output post.icn SUPPRESSES — a **false red on concord/deal/ipxref/queens, all four byte-identical to the oracle**; it now prints `n/a` and defers. ⚠ **This is s164's own lesson recurring one layer down — an EMPTY COMPARISON MUST NEVER BE A PASS. Worth auditing the Prolog/SNOBOL4 runners for the same shape.**
  **`geddump` ROOT CAUSE = A FAILING `not` DELIVERS SUCCESS.** Divergence is 1,077 lines present ONLY in SCRIP, ZERO missing — a strict superset, i.e. over-emission. Its line-54 guard `(p.r === gedref(fam,"HUSB")) | (not gedref(fam,"HUSB"))` must FAIL for the wife; instead the arm succeeds and every child prints twice.
  **⭐ `not` IS A ONE-LINE REPRO OF THE s164 SCAN/`else` DEFECT — USE IT INSTEAD OF THE SCAN ONE:** `procedure main(); if not (1 = 1) then write("THEN") else write("ELSE"); end` → iconx `ELSE`, SCRIP m3 AND m4 print **nothing**. No scan env, no subject, no procedure.
  **CANDIDATE UNIFIED ROOT CAUSE (INFERRED FROM IR DUMPS, NOT YET CONFIRMED IN `emit.cpp`):** both `not` and scan express arm-failure as a transition INTO the DISJUNCTION node itself (its β edge) — `not` repro node 5 γ=1, s164 scan dump node 14 γ=1 — and that node's own γ/ω are both FAIL. Plain failing comparisons do NOT take that path and work correctly. So the emitter appears to treat arm-failure re-entry at the DISJUNCTION as arm-list EXHAUSTION instead of advancing to the next arm. **LOWER is faithful to canonical `ir_a_Not` (verified against `refs/jcon-master/tran/irgen.icn` L142-159) — do not go back to `lower_icon.c`.** Full detail incl. the discriminating table: `FINDING-2026-07-25-CLAUDE-ICN-NOT-IS-A-ONE-LINE-REPRO-OF-THE-SCAN-ELSE-DEFECT-AND-GEDDUMP-ROOT-CAUSE.md`.

- **s165b (2026-07-25) — `not` FAIL-CONDUIT LANDED. `geddump` BYTE-IDENTICAL. s164 SCAN REPRO FIXED. SCRIP `6c740055` + corpus `fcd7a9f0`. Suite 249/12/32 UNCHANGED.**
  **ONE-LINE FIX IN `lower_not`.** Canonical `ir_a_Not` lowers the inner expr with succ=ω, so every γ edge landing ω means "inner succeeded ⇒ the not FAILED" — a fail conduit. `lower_not` never marked them, so the nary retag (L1045) saw only `γ.node == dj` and stamped **σ**, resolving the edge to the disjunction's SUCCESS glue `na_s` instead of `na_f`. Read straight off the emitted `.s`: `cmp rax,rcx / jne n7_α / jmp xchain0_n0_as`. The dj's own γ is its ω=FAIL, so NEITHER arm ran. Fix reuses the producer-marks-at-construction contract already at L692 (scan `leave_fail`).
  **MEASURED WITH A REAL PRE-FIX BASELINE** (change stashed + rebuilt — not inferred):

  | | pre | post | iconx |
  |---|---|---|---|
  | `if not (1=1) then A else B` | prints NOTHING | `ELSE` | `ELSE` |
  | s164 2-line scan repro | `*** PROC FAILED ***` | `ELSE` | `ELSE` |
  | `geddump` | 13,645L DIVERGE | **12,568L IDENTICAL** | — |
  | suite | 249/12/32 | **249/12/32** | — |

  ⚠ **`rsg` STILL DIVERGES (5,000L vs 1,000L). The scan repro was NECESSARY BUT NOT SUFFICIENT for it** — s164 asserted the repro was rsg's root cause; that is now falsified in the strict sense: the repro passes and rsg does not. rsg needs its own bracket; `defnon` is the place to instrument next.
  ⚠ **WHY A `not` FIX MOVED THE SCAN REPRO IS NOT MECHANISTICALLY EXPLAINED.** Both are measured, both pre/post verified — but `sc.icn` contains no `not`, so the causal path is unproven. Do NOT cite this as understood; establish it before building on it.

- **s164 (2026-07-25, Opus 4.5) — BENCH-HONESTY: oracle-diffed the whole Icon bench corpus; README grid replaced; `rsg` short-circuit named. SCRIP `54b047cc`. No codegen touched.**
  **Correctness 6/9 byte-identical to `iconx` 9.5.25a** (concord 1,345L · deal 17,000L · ipxref 1,208L · queens 16,653L · tgrlink 3,239L · micsum) — established with a NEW `OUTPUT=1` pass (`scripts/honest_icon_correctness.sh`), because the stock timing run has `post.icn`'s `write := 1` suppression active and **stdout therefore cannot validate a timing run at all**. `version` divergence is benign (`&version`). Live defects: `geddump`, `rsg`.
  **TIMING TRUTH (RT_OPT=-O0):** geomean over the five correctness-verified workloads **m4 = 0.62× (1.62× SLOWER than iconx), m3 = 0.50×**. Per-program m4: concord 0.56 · deal 0.33 · ipxref 0.52 · queens 1.10 · tgrlink 0.86.
  ⚠ **THE README's PRIOR ICON GRID (2026-07-18 `f405c6a7`, "6.8×/13.8× faster") IS SUPERSEDED AND MUST NOT BE CITED** — it came from `test_icon_bench_corpus.sh` (grades `rc==0 && non-empty`), and five of its six times sat on the ~4 ms process floor, which is precisely the skipped-workload signature the diffing runner exists to detect.
  **Ir INDEPENDENTLY REPRODUCES THE s163 DIAGNOSIS:** tgrlink SCRIP **1,303,410,904** vs iconx **1,338,636,521** — SCRIP executes **1.027× FEWER** instructions and still loses wall clock. Instruction count is not the deficit; memory behaviour is.

- **s163 (2026-07-25, Sonnet 4.6) — HP-1 + HP-2: hugepage arena + virgin-zero elision. tgrlink 212→177ms (1.20×), queens 67→51ms, concord 95→62ms. Zero regression.**
  **KEY FINDING:** SCRIP already beats iconx on Ir (1.307G vs 1.339G) and branch mispredicts (11.3M vs 25.8M). The gap is 25× LL cache misses and 25× page faults — virgin bump-alloc through 61MB of cold memory vs iconx's 8.3MB warm heap. Instruction rungs cannot close this gap. Full findings: `FINDING-2026-07-25-CLAUDE-ICN-MEM-1-HUGEPAGE-VIRGIN-ZERO-ELIDE-AND-GC-ABORT-DIAGNOSIS.md`.
  **GC ABORT FINDING:** GC fires on tgrlink at ≤16MB and aborts (not wrong output). Basic GC correctness is demonstrated (800MB churn, all struct types down to 4–8MB). Root cause NOT yet determined: over-retention vs legitimately large live set. See FINDING for separation protocol.

### ▶ SUPERSEDED RUNG — SCAN-ARM VALUE SLOT IN NARY-DISJUNCTION (s164 diagnosis; kept for its falsified list)

**⭐ SUPERSEDED BY A ONE-LINE REPRO (s165) — START HERE:**
`procedure main(); if not (1 = 1) then write("THEN") else write("ELSE"); end` → iconx `ELSE`, SCRIP m3 AND m4 print **nothing**. No scan environment, no subject, no procedure — same symptom as the scan case with every scan variable removed. **This is also `geddump`'s root cause** (its line-54 guard is `A | (not B)`), so the rung now closes TWO of the two remaining bench defects, not one.

**Prior 2-line scan repro (still valid, use as the second test after the `not` one passes):**
`procedure f(s); if s ? (="'") then return "THEN" else return "ELSE"; end` → iconx `ELSE`, SCRIP fails the whole procedure.

**CANDIDATE UNIFIED ROOT CAUSE (s165, inferred from both IR dumps — CONFIRM IN `emit.cpp` FIRST):** both constructs route arm-failure INTO the DISJUNCTION node itself (`not` repro node 5 γ=1; s164 scan dump node 14 γ=1), and that node's own γ/ω are both FAIL — so the emitter looks to be treating arm-failure re-entry as arm-list EXHAUSTION rather than advancing to the next arm. Canonical `ir_a_Alt` (`irgen.icn` L196-198) requires arm *i* failure → arm *i+1* START, with ONLY the last arm's failure going to the disjunction's failure.

**START IN THE EMITTER.** The IR is structurally CORRECT (dumped s164: the else arm exists, `leave_fail` routes back to the DISJUNCTION). The defect is EXECUTION of nary-DISJUNCTION **arm value-slot delivery** when the arm's tail is an `IR_SCAN` — the `op_parts`/CV10 channel plus the `na_s`/`na_f` success/fail glue in `emit.cpp`. Decisive evidence: `(s ? (="'")) | "ALT-ELSE"` returns **null**, i.e. the arm neither fails cleanly nor yields the alternative — it delivers an EMPTY VALUE SLOT.
**⛔ DO NOT re-try the `lower_icon.c` TT_SCAN subject-β `ir_is_generator_kind` guard — tried s164, zero behaviour change, reverted.** Seven other hypotheses also falsified; all listed in `FINDING-2026-07-25-CLAUDE-ICN-SCAN-COND-ELSE-EDGE-IS-THE-RSG-ROOT-CAUSE.md`. Read it BEFORE coding.
Re-test after the fix: `rsg` bench, `rung36_jcon_scan`/`scan1`/`scan2`, `recogn`, and the FZ-E cluster.

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

**FZ-E scan root — NOW HAS A 2-LINE REPRO (s164):** `if s ? (="'") then A else B` fails the enclosing procedure instead of taking `else`; scan-specific, both modes. This is also `rsg`'s root cause. Start here, not on the big programs: `FINDING-2026-07-25-CLAUDE-ICN-SCAN-COND-ELSE-EDGE-IS-THE-RSG-ROOT-CAUSE.md`.

**FZ-E scan root (recogn/scan/scan1/scan2):** emitter wires the SCAN_MATCH fail-edge to arm-B beta (resume, mid-flight) not alpha (fresh start). Land mine: `emit.cpp` ~L887-904 / IR_SCAN_SEQUENCE ~L1101.

**Open residuals (not in FAIL-ZERO):** `type()`/`image()` for record constructors return `"function"` not `"procedure"`/`"record constructor N"` — `by_name_dispatch.c` type() DT_E branch. Pre-pinned regressions: geddump/tgrlink → `git revert 7aade169`; ipxref → LOWER-side `lower_alt` arm-interior BFS slot-wiring. `geddump` diverges 11,222L vs oracle 10,145L; **`rsg`'s DIVERGE is now EXPLAINED (s164) — it is a SHORT-CIRCUIT, and its 2.83–3.40× m4 "speedup" is VOIDED.** SCRIP emits **1,000 blank lines (1 distinct value)** vs the oracle's 5,000 lines / **1,604 distinct sentences**; 1,000 is `rsg.icn`'s default `limit := \opts["l"] | 1000`, so the generator loop runs to its bound producing empty strings — the grammar table never populates. Same defect in BOTH modes. **ROOT CAUSE PINNED s164 — the procedure-value hypothesis is FALSIFIED (`(!plist)(line)` works fine).** A failing SCAN used as an `if` condition never reaches `else`. 2-line repro: `procedure f(s); if s ? (="'") then return "THEN" else return "ELSE"; end` -> iconx `ELSE`, SCRIP fails the WHOLE procedure. Scan-specific: `s == "zzz"` and bare `="q"` both take `else` correctly. `rsg`'s `defnon` is exactly this shape, so `syms` returns `[]` and every grammar alternative is empty (measured: oracle `ALT s[1] nsym=2` vs SCRIP `nsym=0`). Same family as the FZ-E scan root below, which now has a deterministic repro it previously lacked. See `FINDING-2026-07-25-CLAUDE-ICN-SCAN-COND-ELSE-EDGE-IS-THE-RSG-ROOT-CAUSE.md` — it lists 7 falsified hypotheses and one falsified fix; do not re-try them.

**Baselines:** 2026-07-01 `6a509382` 190/63/36 · R12 `b404fb95` 242/15/32 · s162 `030d6263` 249/12/32.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
**Architecture:** `ARCH-ICON.md` · `ARCH-x86.md` · `GOAL-ICON-BB-NATIVE.md`

## Session-close / push protocol
See RULES.md — `scripts/handoff_status.sh` verbatim stdout is the ONLY sanctioned completion claim.
