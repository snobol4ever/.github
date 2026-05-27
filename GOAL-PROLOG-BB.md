# GOAL-PROLOG-BB.md — Prolog: BB-land DCG per predicate + lower_pl DCG

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-PROLOG-BB-COMPLETE ✅ `c9b7428d` (PB-8 honest 111/294 FAIL=0 ABORT=0)
**Sister:** GOAL-HEADQUARTERS.md — mirror; only port semantics and names differ.

## ⛔ MANDATORY: ARCHITECTURE OF PJ-AG-WIRE — READ BEFORE EVERY SESSION

**What PJ-AG-WIRE is:** two things, in order:
1. **LOWER** — `lower_pl` walks the Prolog AST and builds a properly 4-port-wired `BB_t` graph.
   AG threading: γ/ω inherited DOWN into each node, α/β synthesized UP out of each node.
   Signature: `lower_pl(cfg, tree, γ_in, ω_in, &α_out, &β_out)`.
   Leaf nodes: `*α_out = *β_out = nd; nd->γ = γ_in; nd->ω = ω_in;`.
2. **EMITTER** — the emitter port-DFS walks the wired graph and emits inline x86 via
   per-kind `bb_pl_*.cpp` templates with `bb_bin_t` reloc tables. NO C Byrd boxes.
   NO new `rt_*` port helpers. One template file per BB kind.

**The pipeline:** `Prolog AST → lower_pl (AG-wired BB_t graph) → emitter port-DFS → bb_pl_*.cpp → x86`

**BB_t is the IR for ALL modes (2/3/4).** BB_t is SCRIP's IR node — equivalent to JCON's `ir_*`
instruction records. The four ports (α/β/γ/ω) are pointers, not labels. The SM is NOT the IR;
it is a 3-instruction bootstrap only (`SM_JUMP`, `SM_LABEL`, `SM_BB_SWITCH`).

**Mode 2 (`--interp`):** `sm_interp_run` dispatches `SM_BB_SWITCH` → `pl_bb_dcg` → `bb_exec_once`
walks the live BB graph in C. This is the correctness reference path.

**Mode 4 (`--compile --target=x86`):** the emitter port-DFS walks the BB graph at emit time
and writes GAS text via `bb_pl_*.cpp` templates. The BB graph is consumed at emit time and
then **freed by `stage2_free_bb_after_emit`**. The emitted x86 runs without any BB graph.

**Mode 3 (`--run`) — DO NOT TOUCH FOR PROLOG:**
Mode 3 JIT-compiles SM to native x86 blobs via `sm_emit_linear`. For Prolog, Mode 3
routes through `sm_interp_run` (Mode 2 path) until `bb_pl_*.cpp` templates are filled
(AGW-8..10). The `crosscheck_prolog FAIL=6` for `--run vs --interp` is **correct and
expected** — it is pre-existing. Do NOT fix it by:
- keeping the BB graph alive past `stage2_free_bb_after_emit`
- calling `bb_exec_once` from `sm_run_linear` at runtime
- adding `rt_bb_switch_pl_entry` or any runtime BB-graph walker to Mode 3
Those approaches violate RULES.md "BB/SM deletion is total" and the deliberate
`stage2_free_bb_after_emit` contract. Leave FAIL=6 alone until AGW-8..10.

**No C Byrd boxes. Ever.** A C Byrd box is `DESCR_t foo(void *zeta, int entry)` implementing
α/β/γ/ω. Zero permitted. All four-port logic lives in `bb_pl_*.cpp` inline x86 templates.
If you find yourself writing a new C function with port logic to make something work in
Mode 3 — stop. That is a Byrd box. Delete it. Implement as a template.

**No SM/BB walking at runtime in Modes 3/4** (RULES.md absolute rule). Modes 3/4 run native x86
only: no `g_jit_prog->instrs[STATE->pc]` opcode loop, no `h_*` trampoline handler, and no
`bb_exec_once`/`bb_exec_resume`/`bb_exec_node`/`bb_broker` reached from a mode-3/4 run path.
The emitter walking SM/BB **at emit time** (Mode 4) is required and permitted; the emitted binary
holds no graph (`stage2_free_bb_after_emit`). The reference SM/BB walkers (`sm_interp_run`,
`bb_exec_*`) are the **Mode-2 (`--interp`) path ONLY**. The single documented temporary exception is
Prolog `--run` → `sm_interp_run` (AGW-1c), to be deleted once `bb_pl_*.cpp` templates land (AGW-8..10).

---

## ⛔⛔ TOP PRIORITY — Prolog RUNG LADDER: proper LOWER + proper EMITTER ⛔⛔

**Order of work (2026-05-26, Lon):** drive the Prolog **rung ladder** up via the two principled
paths, in this order:

1. **Proper LOWER** — `PJ-AG-WIRE` (PJ-AGW-1..7): Attribute-Grammar lowering of the Prolog AST into
   a properly 4-port-wired `BB_t` graph (γ/ω inherited DOWN, α/β synthesized UP). This is the
   principled fix for smoke_prolog 0/5 (the `counter`-overload aliasing) and restores Mode-2
   `--interp` rungs *by construction*. See the `## ⛔ Step PJ-AG-WIRE` section below.
2. **Proper EMITTER** — Mode-4 (`--compile --target=x86`) emit of the AG-wired BB graph for each
   Prolog rung: emit the four-port boxes as inline x86 (no C Byrd boxes; RULES.md), close the
   PJ-9e multi-clause registry gap, and bring each rung's Mode-4 output to parity with Mode 2/3.

**The rung ladder is the source of truth for both.** A rung is "up" only when it passes through the
proper LOWER path (Mode 2 AG-wired ports) AND, when EMITTER work reaches it, Mode 4 agrees.
Track every rung honestly via the aggregate gate (GATE-3 below); no "done" without green numbers.

### ⏸ DEFERRED — SNOBOL4 Mode-4 benchmark work (do later)
The SNOBOL4 Mode-4 emitter + benchmark steps — `SBL-M4-ASM` ✅, `SBL-M4-OPDISPATCH` ✅, `SBL-BENCH`,
`SBL-BENCH-ALL`, and the `m2=m3=m4` benchmark-equivalence push — are **paused** in favor of the
Prolog rung ladder above. The already-landed SNOBOL4 dual-mode smoke gate (13/13) stays a permanent
non-regression gate, but no NEW SNOBOL4 Mode-4 / benchmark work this session. Resume after the
Prolog rung ladder is up through proper LOWER + EMITTER.

### Prolog rung honest gate (run EVERY time; this is the source of truth)
```
cd /home/claude/one4all && bash scripts/build_scrip.sh   # needs libgc-dev (apt-get install libgc-dev)
bash scripts/test_smoke_prolog.sh        # GATE-1 — 5/5 target (currently 0/5: counter-aliasing)
bash scripts/test_prolog_rung_suite.sh   # GATE-3 — aggregate rung-ladder count, PASS >= prev
                                         #   (aggregate runner: build it if absent, mirror
                                         #    scripts/test_icon_all_rungs.sh; walk corpus
                                         #    /home/claude/corpus/programs/prolog/rung*)
```

### SB-LINEAR steps (do top-down) — ⏸ SECTION DEFERRED (SNOBOL4 Mode-4/bench; see TOP PRIORITY)

> ⏸ **This section is the deferred SNOBOL4 work.** Completed rows (✅) remain accurate history and
> their gates stay non-regressive, but the OPEN SNOBOL4 Mode-4 / benchmark rows below
> (`SBL-BENCH`, `SBL-BENCH-ALL`, and any remaining `SBL-M4-*` follow-ups) are **paused** in favor
> of the Prolog RUNG LADDER (proper LOWER `PJ-AG-WIRE` + proper EMITTER). Resume after the ladder is up.

### ⛔ Step PJ-MODENAME — eradicate `--interp` / `--interp` / `--run` jargon; use only `--interp` / `--run` / `--compile`

**Directive (2026-05-26, Lon):** the labels `--interp`, `--interp`, and `--run` are not sanctioned names.
There are exactly three modes and they are named by their CLI flags: **`--interp`** (Mode 2),
**`--run`** (Mode 3), **`--compile`** (Mode 4). Replace every user-facing occurrence of the jargon
labels in test/diagnostic OUTPUT and comments with the flag name of the mode it denotes
(`--interp`→`--interp`, `--interp`→`--interp`, `--run`→`--run`, plus any `--compile` comparison).

- [x] **PJ-MN-1** — Mode-name eradication COMPLETE 2026-05-26 (Opus 4.7). The three legacy mode-jargon
  strings were removed from ALL source, comments, scripts, Makefile, test fixtures, one4all/docs, and every
  `.github` HQ MD file (full-tree grep = 0, excluding `.git`). Only the sanctioned CLI names remain:
  `--interp` (Mode 2), `--run` (Mode 3), `--compile` (Mode 4). Also fixed two bogus flag hints in icn_main.c
  → `--interp`/`--run`; renamed baseline file to `interp-honest.md5` (+ icon_bb_probes.sh refs). `test_crosscheck_prolog.sh`
  + `util_crosscheck_3mode.sh` collapsed the dead `--interp vs --interp` comparison to the real `--run vs --interp`;
  the other 5 crosscheck scripts kept pristine logic with labels-only renamed. Build OK, Makefile parses,
  smoke_prolog 5/5. NOTE surfaced (pre-existing, NOT this step): Icon `--run` errors `sm_eval_subexpr: invalid
  entry_pc 1` — a GOAL-ICON-BB concern that the old icon crosscheck script was masking.


| Step | Description | Status |
|---|---|---|
| **SBL-FN-RET** | Function call/return in linear x86. `rt_call_fn` enters body via native `((blob_fn_t)blob)()`; `SM_RETURN` must do a NATIVE `ret`, not just `STATE->pc` bookkeeping. Made `h_return_impl`/`rt_return*` return int; emit `test al,al; jz +1; ret` (`sl_ret_if_eax`) after every RETURN-family helper. | ✅ verified — `define` 0/abort → PASS=42 |
| **SBL-FN-ARGS** | `rt_call_fn` bound params to `NULVCL`, never to actual args (so `DOUBLE(21)` saw `X=0`). Pop args before `sp=0`, bind `call_args[k]` to each param (mirror trampoline `h_call`). | ✅ verified — part of `define` PASS |
| **SBL-EXEC-PATD** | `rt_exec_stmt` passed `NULVCL` instead of popped `pat_d` on the no-blob branch. Now pops `pat_d` and passes it to `exec_stmt`. | ✅ landed (no-blob branch only) |
| **SBL-PAT-BLOB** ✅ | `pattern` (`S 'b' = 'X'`) Mode 3 `Xabc` → `aXc`. **Landed `a6dd2735` (2026-05-26 Opus).** Root cause was TWO empty/wrong `MEDIUM_BINARY` arms in the shared flat BB-box emitter (`src/emitter/XA_templates/xa_flat.cpp`), NOT a deep pattern-compiler bug: (1) `xa_flat_prologue_str` binary arm returned `""`, so the brokered blob never set `r10=&Δ` nor dispatched on entry port — literal box read garbage delta. Fixed: emit `mov r10,&Δ; cmp esi,0; jne β` (β via `bb_bin_t` reloc site @ off 15 using new `g_emit.flat_β_p`; new `TEMPLATE_ADDR_DELTA`). (2) `codegen_flat_body` (emit_bb.c) defined BOTH γ and ω at the SAME address before the epilogue, so every ω/fail jump landed on the SUCCESS epilogue → failed match at pos 0 falsely "succeeded" empty (start=end=0) → `Xabc` splice. Fixed: removed premature ω define; epilogue now defines ω BETWEEN success-ret and fail-half (binary `is_def` site @ succ_half.size(); text inline label). | ✅ verified — `pattern` PASS, smoke 6/6 |
| **SBL-IDX** | Mode 3 (`--run`) linear `rt_call_fn` (`sm_jit_interp.c`) did not special-case the synthetic `IDX` / `IDX_SET` opcodes that table indexing (`T<I>` / `T<I> = v`) lowers to — it fell through to `INVOKE_fn("IDX",…)` which doesn't know them → "Error 5 Undefined function or operation". The JIT trampoline `h_call` already handled IDX/IDX_SET; mirrored that logic into `rt_call_fn` (using `subscript_get`/`subscript_get2`/`subscript_set`/`subscript_set2`, `g_jit_state->last_ok`; omitted the `comm_var` monitor hook — not needed for correctness in the linear path). **Landed 2026-05-26 (Opus).** A/B verified against pre-fix HEAD: smoke_snobol4_jit `--run` PASS **137→146 (+9)**, FAIL 124→115; `--interp` unchanged at 181 (proves linear-path isolation); table_access bench Mode 3 now matches Mode 2 (`result: 250500`). | ✅ done — +9 |
| **SBL-DIVERGE** (survey) | Ran ALL SNOBOL4 x86 suites in Mode 2 (`--interp`) AND Mode 3 (`--run`). Broad-corpus crosscheck (`/home/claude/corpus/crosscheck`, 261 with .ref): **both_ok=141, M2-passes-M3-fails=38, M3-only=4, both_fail=78.** NOTE: `scrip` default mode is `--run` (Mode 3) — `scrip.c:121` sets `mode_run=1` when no flag given; so `test_interp_broad_corpus_and_beauty.sh` (no flag) was silently running Mode 3, not Mode 2. Explicit both-mode counts: **Mode 2 = 186/280, Mode 3 = 146/280** (40-test gap). `--monitor` confirmed the gap but itself segfaults on the offending programs (it drives the JIT step-runner into the same crash). **Root cause of the largest cluster (pattern primitives) located:** `ANY('aeiou')` Mode 3 → `bb_emit_end: 1 unresolved forward reference(s): label='pat_brok_β'`, then abort/segfault. The `bb_pat_any` BINARY arm (`BB_templates/bb_pat_any.cpp`) emits raw bytes via `emit_text_n` with **NO `bb_bin_t` relocation table** — so its rel32 port jumps (`0F 85 …`, `E9 …`) are never patched and the β (retry) label is never defined. Contrast `bb_lit.cpp` which builds `bb_bin_t bin = {{offsets},{label_ptrs},{is_define}}` and calls `bb_emit_asm_result(str,bin)` — that's how LIT defines β (SBL-PAT-BLOB). Same gap affects NOTANY/SPAN/BREAK/LEN/TAB and the `W05_*`/`pat_*` family. **FIX SHAPE (next step SBL-PAT-PRIM):** give each pattern-primitive BINARY arm a `bb_bin_t` reloc table (offsets for the two rel32 sites + a β define site), refactor `bb_pat_<x>_str` to take `bb_bin_t &bin` and emit via `bb_emit_asm_result` like `bb_lit`. | ⛔ TODO — root-caused, fix scoped |
| **SBL-BENCH** | Run the SNOBOL4 benchmark suite under **all three modes** — Mode 2 (`--interp`, SM dispatch), Mode 3 (`--run`, SB-LINEAR linear x86), Mode 4 (`--compile --target=x86`, emitted standalone binary) — and record timings + output-equivalence. Bench corpus lives under `/home/claude/corpus/benchmarks/` (see `corpus/BENCHMARKS.md` / `one4all/bench/BENCHMARKS.md`); SKIP gracefully if corpus absent (RULES.md). Add/extend a `scripts/test_bench_snobol4_modes.sh` runner: for each bench .sno, run all three modes with `timeout 30s`, assert all three produce identical stdout (correctness gate), and emit a per-mode wall-clock table (parse/lower/exec via `--bench` where available). Goal product line is "Ten times faster" — this step establishes the Mode 2 vs 3 vs 4 baseline. **Only after SBL-GATE is green** (the 6-case smoke must pass in all relevant modes first). | 🔄 runner landed (`test_bench_snobol4_modes.sh`) — baseline captured (see SBL-BENCH-ALL) |
| **SBL-BENCH-ALL** | **Get ALL SNOBOL4 benchmarks running + output-equivalent in all three modes** (m2=m3=m4=N, DIFF=0). The runner (`scripts/test_bench_snobol4_modes.sh`) is the gate: per-bench it runs `--interp`, `--run`, and the Mode-4 compile→assemble→link→exec pipeline, strips timing lines (`ms:` / `BENCH ` / `iterations:`), and asserts all modes that ran agree. **Sub-goals, in order:** (a) Mode 2 baseline — fix any bench that fails even under `--interp` (frontend gaps: `func_call`/`var_access`/`func_call_overhead` time out at 30s — likely &STLIMIT/loop-size, not engine; `roman.sno` segfaults Mode 2 — investigate). (b) Mode 3 parity — depends on **SBL-PAT-PRIM** (pattern primitives) + **SBL-IDX** ✅ (tables, done). (c) Mode 4 — **SBL-M4-ASM ✅** unblocked it (broad corpus 0→126); remaining Mode-4 bench gaps are **SBL-M4-OPDISPATCH** (comparison-builtin runtime abort) + pattern primitives (SBL-PAT-PRIM) + heavy-loop timeouts. Done when the runner prints `m2=m3=m4=<TOTAL> DIFF=0`. | ⛔ TODO — runner ready; baseline below |
| **SBL-PAT-PRIM** | Give each pattern-primitive BB BINARY arm a proper `bb_bin_t` relocation table + β define site, mirroring `bb_lit.cpp`. Currently `bb_pat_any/notany/span/break/len/tab` binary arms emit raw bytes via `emit_text_n` with NO `bb_bin_t` → `pat_brok_β` never defined, rel32 port jumps never patched → `bb_emit_end: unresolved forward reference` abort in Mode 3. Refactor `bb_pat_<x>_str(BB_t*)` → `bb_pat_<x>_str(BB_t*, bb_bin_t &bin)`, populate `bin = {{offsets},{label_ptrs},{is_define}}` for the two rel32 sites + the β-entry define, and emit via `bb_emit_asm_result`. Start with `ANY` (simplest), then NOTANY/SPAN/BREAK/LEN/TAB. This unblocks ~30 of the 38 Mode-2-only broad-corpus programs and the pattern benches in Mode 3. **DONE 2026-05-26 (Opus 4.7) `4bd0ffb6`:** added `bb_bin_t` reloc tables `{43,48,52,95,100}` (γ-ref, ω-ref, β-define, β-body γ/ω) to ANY/NOTANY/SPAN/BREAK; LEN already converted. m2==m3 byte-identical with replacement (`= 'X'`). smoke_snobol4_jit `--run` 146→150. ⚠ standalone `0XX_pat_*` tests STILL fail in Mode 3 — they use `. V` conditional-assignment capture, a SEPARATE pre-existing segfault (crashes for plain LIT capture at clean HEAD `340b14b9`). **TAB still open:** its binary arm has an off-by-one reloc AND an empty-match value bug (reverted to avoid shipping silently-wrong output). | ✅ done (TAB + `. V` capture remain) |
| **SBL-M4-ASM** | Fix Mode-4 (`--compile --target=x86`) assembler + link failures. **Landed 2026-05-26 (Opus).** TWO bug classes: (1) **bare-annotation macro args** — emitter templates appended human-readable annotations as space-separated tokens after GAS macro calls (`STORE_VAR .S0 A`, `CALL_FN .S2, 0 TIME`, `PUSH_STR .S8, 0 "..."`, `RETURN_VARIANT 0,1,20 SM_RETURN_S`, `CALL_EXPRESSION .L5 name...`, `DEFINE_ENTRY FIB`) → `as` "too many positional arguments". Fix: emit the annotation as a `#`-comment line (`s_2asm/s_1asm + s_comment`), not a bare arg. 6 files: `sm_push_pop_lits.cpp`, `sm_calls.cpp`, `sm_returns.cpp` (×3), `sm_bb_calls.cpp`, `sm_defines.cpp`. (2) **unresolved enum symbol** — arith macros emitted `mov edi, SM_ADD` (a C enum NAME with no assembler/linker definition) → `R_X86_64_32S against undefined symbol SM_ADD`. Fix (`sm_arith.cpp`): emit numeric immediate `mov edi, %d` via `(int)SM_ADD` (enum resolves at emitter compile time, always correct). **Result: Mode-4 broad corpus 0 → 126 PASS** (FAIL=26 SKIP=128), matching Mode 3's reach. Bench 3-mode equivalence achieved: arith_loop/eval_dynamic/eval_fixed/string_concat/fibonacci all OK(3). Verified end-to-end: A+B→13, arith_loop→1000000, fibonacci→832040 (recursion+DEFINE work in Mode 4). | ✅ done — 0→126 |
| **SBL-M4-OPDISPATCH** ✅ | `op_dispatch.sno` aborted at runtime ("SM value stack overflow cap=65536"). **FIXED 2026-05-26 (Opus 4.7) `5a8bf79d`.** Root cause was NOT comparison-builtin correctness — it was a missing per-statement vstack reset. Mode 2 `sm_interp.c` SM_STNO does `st->sp=0` every statement; Mode 4 `rt_set_stno` did not, so a statement failing mid-eval (GE/LT → DT_FAIL) left operands on the vstack; over a tight loop the residue overflowed. Fix: `rt_set_stno` resets to `g_vframe_base` (NOT absolute 0 — that regressed recursion; frame base is set by `call_native_chunk` to the caller's `saved_vtop`). op_dispatch m4 `result:122172` == m2 == m3 OK(3). Mode-4 broad corpus 126/26 unchanged; 3 recursion tests confirmed still passing. | ✅ done |

### Session watermark 2026-05-26b (Opus) — SBL-M4-ASM: Mode 4 unblocked (0→126 broad corpus)
```
one4all: 340b14b9 — BUILD GREEN, libscrip_rt rebuilt
6 emitter files fixed (annotation-as-comment) + sm_arith numeric-immediate fix.
Mode 4 broad corpus: 0 → 126 PASS (FAIL=26, SKIP=128) — matches Mode 3 reach.
3-mode bench equivalence OK(3): arith_loop, eval_dynamic, eval_fixed, string_concat, fibonacci.
Timing (TIMEOUT=15): m2 ran 10/16, m3 12/16, m4 4/16 (rest timeout/pattern/opdispatch).
  Note m4 currently slower than m3 (still routes through rt_* call helpers, not inlined).
Gates: smoke_snobol4 13/13 (both modes), icon 5/5, snocone 5/5, rebus 4/4, raku 5/5.
NEXT: SBL-M4-OPDISPATCH (comparison-builtin runtime abort — root of the 26 m4 FAILs),
      then SBL-PAT-PRIM (pattern primitives, helps BOTH Mode 3 and Mode 4).
```

### Session watermark 2026-05-26 (Opus) — SBL-GATE + SBL-IDX landed; pattern-primitive Mode-3 gap root-caused
```
one4all: <this commit> — BUILD GREEN
smoke_snobol4 (both modes): 13/13 (Mode 2: 7, Mode 3: 6) — permanent dual-mode gate
smoke_snobol4_jit: --interp 181/261, --run 146/261 (was 137; +9 from SBL-IDX)
crosscheck_snobol4: 5/6 (1 pre-existing PATTERN/xTrace)
broad corpus: Mode 2 186/280, Mode 3 146/280 (40-gap; largest cluster = pattern primitives)
mode4 broad: 0/280 (280 SKIP) — pre-existing, unrelated: --compile --target=x86 emits
  `STORE_VAR .S0 A` (space-separated macro args) → GNU as "too many positional arguments"
ASAN (Mode 3, leaks off): exercised SM+BB-pattern+fn-call+table → correct output, rc=0,
  ZERO use-after-free. Confirms SM_sequence_t/bb_table[]/BB graphs freed before run are never touched.
Cross-lang smokes: icon 5/5 snocone 5/5 rebus 4/4 raku 5/5. prolog 0/5 pre-existing.
NEXT: SBL-PAT-PRIM — add bb_bin_t reloc tables to bb_pat_any/notany/span/break/len/tab binary arms.
```

**Verified Mode 3 (`--run`) smoke at this watermark: PASS=6 FAIL=0 (output/concat/arith/pattern/goto_s/define).**

### SBL-BENCH baseline (`scripts/test_bench_snobol4_modes.sh`, TIMEOUT=12; 16 benches)

```
bench                  m2(ms)  m3(ms)  m4   equiv     note
arith_loop               2266    1142   -   OK(2)     m3 ~2x faster
eval_dynamic             7072    4677   -   OK(2)
eval_fixed               5875    3752   -   OK(2)
fibonacci               10463    6888   -   OK(2)
func_call                   -       -   -   none      both timeout (heavy loop)
func_call_overhead          -       -   -   none      both timeout
indirect_dispatch          12      10   -   DIFF*     *both error on $FN(X) (unsupported);
                                                       stdout differs by 1 trailing newline only
mixed_workload           3089    1770   -   OK(2)
op_dispatch              5434    2968   -   OK(2)
pattern_bt                 10      10   -   OK(2)
roman                       -      10   -   1mode     m2 segfaults (frontend)
string_concat            2279    2141   -   OK(2)
string_manip                -       -   -   none      both timeout
string_pattern           1565    1043   -   OK(2)
table_access                -    8572   -   1mode     m2 OK at 60s -> 250500 == m3 (SBL-IDX)
var_access                  -       -   -   none      both timeout
ran: m2=10/16 m3=12/16 m4=0/16 | equiv PASS=9 DIFF=1(artifact)
```

**Findings:** (1) Zero *genuine* Mode 2 vs Mode 3 divergences — every bench that runs in both
produces identical normalized output; the lone DIFF (indirect_dispatch) is a 1-byte stderr-path
stdout-newline artifact on a builtin (`$FN(X)`) unsupported in BOTH modes. (2) **Mode 3 (SB-LINEAR)
is consistently ~1.5–2× faster than Mode 2** on the compute benches — the "Ten times faster" baseline.
(3) Mode 4 = 0/16 (SBL-M4-ASM assembler bug). (4) Remaining gaps to all-3-mode-green: SBL-PAT-PRIM
(Mode 3 pattern primitives), SBL-M4-ASM (Mode 4), heavy-loop timeouts + roman m2 segfault (frontend).
Landed `a6dd2735`. one4all build GREEN. Mode 2 `--interp` 7/7 unregressed; icon 5/5, snocone 5/5,
rebus 4/4, raku 5/5 all unchanged. NOTE: this work sits on the `f2ecf7af` emergency-handoff branch
where `smoke_prolog` is 0/5 and `unified_broker` 18/31 — both PRE-EXISTING (confirmed via git stash
A/B against clean HEAD), NOT regressions from SBL-PAT-BLOB.

---

## Invariants (READ FIRST)

The five invariants from GOAL-HEADQUARTERS.md apply verbatim with names substituted:
Icon `proc_table` ↔ Prolog `dcg_table`; `icn_bb_dcg` ↔ `pl_bb_dcg`; `SM_BB_PUMP_PROC` ↔ `SM_BB_ONCE_PROC`. **Cross-language semantics differ per port** — Icon β advances a generator counter; Prolog β pops a choice-point + unwinds the trail; SNOBOL4 β backtracks the pattern anchor. Never invoke language-A's SM-bridge handler with language-B's BB object.

## Session Setup

```
cd /home/claude/one4all && bash scripts/build_scrip.sh
```

## Architecture

Same shape as Icon (SM is entry; SM_BB_XXX bridges into BB-land; nothing dereferences `tree_t*` at runtime), with three differences in port semantics:

| Port | Icon semantics | Prolog semantics |
|---|---|---|
| α | enter generator, first attempt | enter predicate, first clause, trail_mark |
| β | resume, advance generator state | retry: trail_unwind, advance to next clause |
| γ | success (yield value) | success (unification succeeded; head bound) |
| ω | failure (exhausted) | failure (no more clauses) |

**Target shape per Prolog program:** the SM stream contains one `SM_BB_ONCE_PROC` per top-level call (typically just `?- main.`). Each predicate's body is one `IR_block_t*` in `dcg_table[i].ir_body`. Multi-clause predicates compose alternatives via `IR_PL_CHOICE`; recursive calls via `IR_PL_CALL`; cut via `IR_PL_CUT`.

**The `pl_bb_dcg` bridge (to be added):**
```c
typedef struct { IR_block_t *cfg; int first; int trail_mark; } pl_dcg_state_t;
DESCR_t pl_bb_dcg(void *zeta, int entry) {
    pl_dcg_state_t *z = zeta;
    if (entry == α) { z->first = 1; z->trail_mark = pl_trail_top(); }
    if (z->first) { z->first = 0; return IR_exec_once(z->cfg); }
    pl_trail_unwind(z->trail_mark);
    return IR_exec_resume(z->cfg);
}
```

**`dcg_table` (to be added):** mirror of `proc_table`. Indexed by `name/arity`. Each entry holds `ir_body : IR_block_t*` plus argument scope info.

## IR executor cases needed (ir_exec.c)

| IR kind | Purpose | Notes |
|---|---|---|
| `IR_PL_UNIFY` | `X = Y` | calls `pl_unify(L, R)`; γ on success, ω on fail (with trail unwind via caller's mark) |
| `IR_PL_CALL` | predicate call | look up `dcg_table[name/arity]`, build fresh `pl_dcg_state_t`, drive via inner `IR_exec_once`/`_resume` |
| `IR_PL_CHOICE` | multi-clause `A; B; C` | `nd->state` = clause index; `nd->counter` = saved trail position; β unwinds + advances |
| `IR_PL_CUT` | `!` | discard choice points back to enclosing barrier; mark surrounding CHOICE so β skips past cut |
| `IR_PL_BUILTIN` | `write`, `nl`, `is`, type tests | direct C calls; γ on success, ω on failure |

## Gates

```
GATE-1  bash scripts/test_smoke_prolog.sh               # PASS=5 (currently 0)
GATE-2  bash scripts/test_smoke_unified_broker.sh       # PASS >= baseline (Prolog rows non-regressive)
GATE-3  bash scripts/test_prolog_rung_suite.sh          # PASS >= prev
GATE-4  bash scripts/test_icon_all_rungs.sh        # cross-language honest gate non-regressive
```

## Active steps

| Step | Description | Gate |
|---|---|---|
| **PJ-1** ✅ | Add `pl_bb_dcg` bridge + `g_dcg_table[]` registry skeleton. Mirror of `icn_bb_dcg`/`proc_table`. Landed at one4all `e6af028c`. | Build clean; gates unchanged |
| **PJ-2** ✅ | Create `src/lower/lower_pl.c` + `.h`. `lower_pl_predicate(tree_t*)` returns NULL placeholder. Wire `lower()` to populate `dcg_table[i].ir_body = NULL`. Landed `d9fe1496`. | Build clean; gates unchanged |
| **PJ-3** ✅ | Replace `[NO-AST]` stub in `sm_interp.c case SM_BB_ONCE_PROC` with body handler: lookup `dcg_table[name/arity]`, wrap via `pl_bb_once_proc_by_name`, drive via `bb_broker`. Landed `f5db4e5f`. | smoke_prolog still 0/5 (no IR yet) |
| **PJ-4** ✅ | `lower_pl_expr_node` handles TT_FNC(write/nl), TT_UNIFY, TT_FNC("is"), TT_VAR, TT_ILIT/QLIT/NAME. Wire into `lower_pl_predicate` building `IR_SEQ`. IR_PL_BUILTIN/VAR/ATOM/ARITH/UNIFY executors in ir_exec.c. pl_bb_env_push/pop. Landed `cb1417a5`. | smoke_prolog 3/5 (write+unify+arith PASS) |
| **PJ-5/6** ✅ | IR_PL_ALT landed `141c4816`. IR_PL_CHOICE/ALT split done; arity emit fix; n-ary comma fix; ival/sval union collision fixed (IR_PL_VAR/CALL/BUILTIN). smoke_prolog 3/5. NEXT blockers: (A) head-arg unification: IR_PL_UNIFY executor must handle IR_LIT_I/F match (for count(0)); (B) comparison ops: lower_pl_stmt_node must route TT_FNC(">/<") to builtin, not IR_PL_CALL; (C) backtracking: IR_PL_CHOICE multi-clause + pump for clause test. |
| **PJ-5a** ✅ | Fix entry-point invocation + add IR_PL_SEQ + cut barrier. (1) `lower.c` TT_CHOICE-subject stmts made no-op (was auto-invoking every defined predicate at program start, with no args, before main); `:- initialization(name).` now emits `SM_BB_ONCE_PROC name/arity` (was no-op). (2) Added `IR_PL_SEQ` opcode + executor: short-circuit on first goal failure, succeed if all succeed (replaces Icon-flavored IR_SEQ in `lower_pl.c`). (3) `IR_PL_CUT` now sets `g_pl_cut_flag`; `IR_PL_CHOICE` checks it and stops trying alternatives. smoke_prolog 4/5: recursion PASS (was FAIL). broker: 19/49 (was 18). Other smokes & honest gates unchanged. |
| **PJ-7** ✅ | Backtracking pump for `clause` test landed. Three coordinated changes in `src/lower/ir_exec.c`: (1) `IR_PL_CHOICE` made stateful — `nd->state` = next clause to try; resume picks up where prior success left off via `IR_exec_resume` (no reset). (2) `IR_PL_CALL` made resumable — stores `PlCallSt{callee_env, saved_env, trail_mark, nslots}` in `nd->opaque`; shared-term propagation (the same `term_new_var(ai)` instance lives in both caller's `saved_env[caller_slot]` AND `callee_env[ai]` so unifications flow via `term_deref` and respect trail unwind). (3) `IR_PL_SEQ` made backtracking — on goal-j failure, scans leftward via `backtrack_from` cursor for resumable goal (IR_PL_CALL state==1 or IR_PL_ALT state==1); calls `IR_exec_resume` on callee's body; on success restarts forward at `found+1`; on exhaustion continues leftward without restarting the exhausted call. smoke_prolog 5/5: clause PASS (was FAIL). broker: 20/49 (was 19). |
| **PJ-8** ✅ | Stub the AST-walking Prolog branch in `_usercall_hook` (`src/driver/interp_hooks.c:81`) when SM dispatch is active. Single 5-line change: gates the `g_pl_active` branch with `if (g_sm_dispatch_active && !g_ast_pump_active)` printing `[NO-AST] _usercall_hook prolog branch: needs fresh SM/BB lowering (PJ-8)` and returning FAILDESCR. This shuts down the only path by which SM-dispatch code reaches `pl_unified_term_from_expr` / `pl_pred_table_lookup` AST helpers. The `pl_broker.c` AST callers (lines 31, 90-91, 122, 387, 396) are only reached from mode 1 (`pl_runtime.c` and `interp_eval.c`), which RULES.md keeps as the reference AST-walking path. No changes to `pl_broker.c` needed. Gates: smoke_prolog 5/5, broker 20/49, honest_prolog 124/0/0, honest_icon 277/0/0 — all unchanged. |
| **PJ-9a** ✅ | **Wired `h_bb_once_proc` in sm_jit_interp.c through `pl_bb_once_proc_by_name`+`bb_broker` (Mode 3 JIT dispatch).** Was `[NO-AST]` stub, so `--run` Prolog crosscheck was 0/4. Mode 2 (`sm_interp.c:671`) already did this work; Mode 3 now mirrors it: lookup name+arity from `CUR_INS->a[0].s` / `a[1].i`, call `pl_bb_once_proc_by_name`, on `node.fn` push/run/pop `pl_bb_env`, drive via `bb_broker(node, BB_ONCE, NULL, NULL)`, set `STATE->last_ok`. On miss keeps the `[NO-AST]` print. Also regenerated stale `snocone_parse.tab.h` (out-of-sync since `4aa8727b` PST-SC-4b blocked all builds). Gates: `test_crosscheck_prolog.sh` 0→**4/4** ✅ (--run rows now PASS); smoke_prolog 5/5, honest_prolog 124/0/0, honest_icon 277/0/0, unified_broker 20/49 — all unchanged. |
| **PJ-9b** ✅ | **Aligned Mode 3 stub fingerprints with Mode 2 opcode-name convention (RULES.md compliance); extended crosscheck.** RULES.md: *"Each stub fingerprint names the exact opcode that still needs fresh SM/BB lowering."* Mode 2 used opcode names (SM_BB_PUMP, SM_BB_ONCE, etc.); Mode 3 used C handler names (h_bb_pump, etc.). Renamed four miss-arm fingerprints in `sm_jit_interp.c` (h_bb_pump→SM_BB_PUMP, h_bb_once→SM_BB_ONCE, h_bb_once_proc→SM_BB_ONCE_PROC, h_bb_pump_every→SM_BB_PUMP_EVERY). PL_UNIFY/PL_BUILTIN stubs at lines 804/828 already used opcode-style names. Also extended `test_crosscheck_prolog.sh` to walk the flat-file rung corpus (was looking for nonexistent rung01/02/03 subdirs) and split xcheck logic: mode-consistency PASS/FAIL (the dispatch invariant) vs ORACLE_MISS (informational; 3 modes agree but differ from .ref oracle — that's frontend completeness, not mode dispatch). Gates: `test_crosscheck_prolog.sh` **4→128 PASS**, FAIL=0, SKIP=4, ORACLE_MISS=11 (frontend gaps not mode issues). smoke_prolog 5/5, honest_prolog 124/0/0, honest_icon 277/0/0, unified_broker 20/49 — all unchanged. |
| **PJ-9c** ✅ (partial) | **Mode 4 (`--compile --target=x86`) dispatch wiring for `SM_BB_ONCE_PROC` — first Prolog primitive routed through emit pipeline.** Three coordinated changes: (1) **`src/runtime/rt/rt.c`**: added `rt_bb_once_proc(const char *name, int arity)` helper mirroring `case SM_BB_ONCE_PROC` in `sm_interp.c:671` — calls `pl_bb_once_proc_by_name`, on hit pushes `pl_bb_env`, drives `bb_broker(node, BB_ONCE, NULL, NULL)`, pops env. On miss prints the same `[NO-AST] SM_BB_ONCE_PROC stub` fingerprint as Modes 2/3 (PJ-9b consistency). Includes `pl_runtime.h` for types. `pl_runtime.c` already in `RT_PIC_SRCS` so link works. (2) **`src/emitter/emit_sm.c:562`**: changed `g_sm_templates[]` entry from `SM_TPL_ARITH / "rt_unhandled_sm"` to `SM_TPL_LBL_INT32 / "rt_bb_once_proc"` (same shape as `SM_CALL_FN` — string + int operands). (3) **`src/emitter/emit_sm.c`**: added `emit_sm_bb_once_proc_dispatch` (modeled on `emit_sm_call_dispatch`) and `case SM_BB_ONCE_PROC` in the master switch at line 2956. Result: `scrip --compile --target=x86 hello.pl` now emits `BB_ONCE_PROC .S0, 0` (was `UNHANDLED 60`); assembles and links cleanly; produced binary runs and reaches `rt_bb_once_proc` correctly. **Open issue (PJ-9d):** the standalone binary's `g_dcg_table` is empty at runtime because the Mode-4 emit doesn't include a Prolog predicate-registry initialization (analog of the `rt_register_expressions` call already emitted for Snocone). So the runtime helper currently hits its miss-arm `[NO-AST]` print rather than executing the predicate body. Dispatch shape is correct; the registry-population emit is the next step. **All gates hold:** smoke_prolog 5/5, crosscheck_prolog 128/0, honest_prolog 124/0/0, honest_icon 277/0/0, unified_broker 20/49 — all unchanged from PJ-9b. |
| **PJ-9d** 🔄 (partial) | **Predicate-registry emit for Mode-4 Prolog binaries — registry mechanism + simple-body recursion working; multi-clause clause-body recursion is the open gap.** Three coordinated changes plus one new script. (1) **`src/runtime/rt/rt.h`/`rt.c`**: added `rt_predicate_entry_t {name, arity, builder}`, `rt_register_predicates_pl(tbl)`, and a small builder API (`rt_pl_b_begin/_node/_kids/_entry/_end_register`) that lets a per-predicate "builder" function reconstruct an `IR_block_t*` graph at standalone-binary startup by calling back into the runtime. Followed PJ-9c's pattern of including `pl_runtime.h` from `rt.c` (`pl_runtime.c` already in `RT_PIC_SRCS`). The builder helpers handle the `IR_t` union aliasing (`ival`/`dval`/`sval` share storage) by writing only the relevant side based on kind. (2) **`src/emitter/emit_sm.c`**: added `pl_pre_intern_pred_names()` (Phase A — runs **after** `strtab_collect` since that function resets the strtab), `emit_pl_predicate_registry` + helpers `emit_pl_builder_fn`, `emit_pl_b_node_call`, `emit_pl_b_kids_call`, `emit_pl_kids_rodata_for_pred`, plus the kind-awareness helper `pl_ir_kind_uses_sval` (only `IR_PL_ATOM/BUILTIN/ARITH/CALL` carry real sval; `IR_PL_VAR`'s sval comes from a tree_t union slot that holds the variable's slot integer, so it's garbage and must be skipped). Extended `emit_file_header` signature with `has_pl_registry` param to emit `lea rdi, [rip + .Lpl_registry]; call rt_register_predicates_pl@PLT` right after the existing `rt_register_expressions` call. Wired both phases into the master `emit_walk_codegen` driver. (3) **`scripts/run_prolog_via_x86_backend.sh`**: new end-to-end runner — invokes `scrip --compile --target=x86`, assembles with GNU `as --64`, links against `out/libscrip_rt.so`, executes. Uses 8s timeout per RULES.md self-contained-scripts rule. **Verified working in Mode 4 end-to-end:** (i) `:- initialization(greet).` with `greet :- write('hi'), nl.` → prints `hi`; (ii) multi-predicate + cross-predicate call (`main :- say_a, say_b.`) → prints `A\nB\n`; (iii) arithmetic + arg-binding (`addtwo(X,Y) :- Y is X+2.` `:- initialization(addtwo(5,Y)), write(Y).`) → prints `7`; (iv) mixed writes (`main :- write('count: '), write(3), nl.`) → prints `count: 3`. **Open gap (PJ-9e candidate):** multi-clause predicates fail in Mode 4. Root cause located: `lower_pl.c:147` stores each per-clause `IR_block_t*` body in the wrapper `IR_SUCCEED` node's `opaque` field (consumed by `ir_exec.c:1234`). These sub-cfgs are **separate `IR_block_t` allocations not in the parent `cfg->all[]`** — my builder only walks `cfg->all[]`, so it emits the `IR_PL_CHOICE` and the `IR_SUCCEED` wrappers but loses the per-clause bodies. Test cases that exercise this gap: factorial recursion (test5 → mode 4 prints nothing, modes 1/2/3 print `120`); multi-clause facts like `color(red).`/`color(green).`/`color(blue).` with `:- color(green)` (Mode 4 silent, Modes 1/2/3 also fail but for an unrelated frontend reason — not yet differentiated). Fix shape: add `rt_pl_b_set_opaque_cfg(node_idx, sub_builder_fn_ptr)` helper; emit a recursive per-sub-cfg builder; have the parent's builder invoke each sub-builder which returns a fresh `IR_block_t*` to be stashed into `opaque`. Also: this session **completed the cross-language AST-walking audit** Lon asked about — see Watermark below. **All other gates hold:** smoke_prolog 5/5, crosscheck_prolog 128/0, honest_prolog 124/0/0, honest_icon 277/0/0, unified_broker 20/49, all six smoke gates (snobol4 7/7, snocone 5/5, rebus 4/4, raku 5/5, icon 5/5, prolog 5/5). |

## Done when

`SM_BB_ONCE_PROC` routes through `pl_bb_dcg` + `dcg_table[i].ir_body` ✅. PJ-8 closed: SM-dispatch no longer reaches AST helpers (the `_usercall_hook` Prolog branch is `[NO-AST]`-stubbed). `pl_runtime.c` AST-walking paths remain only for mode 1 (`--interp` reference). `pl_bb_build` lazy fallbacks replaced ✅. Inline x86 emitters for Prolog primitives written (mode 4) — STILL TODO for full Mode 4 deliverable. smoke_prolog 5/5 ✅. GATE-1..4 green ✅.

---

## Architecture as understood after PJ-1..12 (2026-05-25)

### The two execution paths

**Mode 2/3 (interpret/JIT):** `rt_pl_once` → `pl_bb_once_proc_by_name` → `bb_broker` → `bb_exec_node` in `bb_exec.c`. The `bb_exec.c` interpreter IS the reference implementation of all BB node semantics. Every `case BB_CHOICE:`, `case BB_PL_SEQ:`, etc. in `bb_exec.c` is the exact logic that must be translated to x86 for Mode 4 templates.

**Mode 4 (emit x86):** `rt_pl_once` (called from emitted `main`) → `rt_register_predicates_pl` → builder functions reconstruct `BB_graph_t` at binary startup → `bb_broker` → (future) emitted x86 Byrd boxes. Currently `bb_exec.c` is still the executor even in Mode 4 because the BB templates (`bb_pl_call.cpp`, `bb_pl_choice.cpp`, etc.) are stubs.

### What the existing PL-T-1..3 templates actually do — and the problem

The existing templates (`bb_builtin.cpp`, `bb_arith.cpp`, `bb_pl_seq.cpp`, etc.) emit x86 TEXT that **calls C helper functions** (`rt_pl_seq_exec`, `rt_pl_arith`, etc.) which do the port logic in C. This violates **INVARIANT 9** from GOAL-BB-TEMPLATE-LADDER: "BB templates may not call RT functions. PERIOD." These were acceptable scaffolding for Mode 2/3. For Mode 4, each template must emit the α/β/γ/ω port logic directly as inline x86 — translating the corresponding `case` in `bb_exec.c`.

### How to translate bb_exec.c → x86 template (the method)

1. **Read `bb_exec.c` `case BB_FOO:`** — this is the complete specification.
2. **State lives in `BB_t` fields:** `nd->state` (int), `nd->counter` (int64), `nd->value` (DESCR_t), `nd->opaque` (void*). Offsets are fixed; use them directly.
3. **Port dispatch:** entry==α → `nd->state==0`; entry==β → `nd->state>0`. `entry` arrives in `edi`.
4. **Return γ/ω:** store result in `nd->value`, tail-call `nd->γ(nd)` or `nd->ω(nd)`.
5. **No `rt_*` port-logic helpers.** Permitted external calls: `trail_mark`, `trail_unwind`, `unify`, `prolog_atom_intern`, `term_new_int`, `term_new_atom` — utility functions with no port state.
6. **Globals:** `g_pl_trail` and `g_pl_env` accessed via `lea rdi, [rip + g_pl_trail]` in TEXT.

### ⛔ RULE (always was): FOUR PORTS = FOUR ONE-CHARACTER GREEK NAMES EVERYWHERE

Every reference to a port — in `g_emit` struct fields, emitter C/C++ code, and in emitted assembly labels — must use the actual Greek character: `α` `β` `γ` `ω`. No English synonyms anywhere.

| Port | Greek | Struct field | Emitted label suffix |
|------|-------|--------------|----------------------|
| fresh entry | α | *(entry is implicit — no field needed)* | `_α` if labelled |
| retry entry | β | `lbl_β`, `lbl_β_p` | `_β` |
| success exit | γ | `lbl_γ`, `lbl_γ_p` | `_γ` |
| failure exit | ω | `lbl_ω`, `lbl_ω_p` | `_ω` |

The current codebase uses `lbl_back`/`lbl_succ`/`lbl_fail` (and `_p` variants) in `emit_globals.h` and all 26 BB template files — **these are all wrong and must be renamed**. See step PJ-13 below.

### Step PJ-13 ✅ — Mass rename lbl_back/succ/fail → lbl_β/γ/ω across all emitter files

34 files, 222 occurrences. Also `flat_lbl_succ`/`flat_lbl_fail` → `flat_lbl_γ`/`flat_lbl_ω`. Landed `6f4996f7`. Gates clean.

---

### Step PJ-14 ✅ — Add lbl_α/lbl_α_p to g_emit; every BB template TEXT arm emits explicit α label

α was implicit (broker fell into box by position; no named entry label). Now all four ports are explicit and jumpable. Three changes landed `eff53b7e`: (1) `lbl_α`/`lbl_α_p` added to `g_emit_t`; (2) `bb_fill_alpha(BB_t*)` in `emit_bb.c` using static ring of 8 labels, called by `FILL`/`EP_FILL`/`walk_bb_flat` null-path, sets `g_emit.lbl_α = "bb<id>_α"`; (3) every BB template TEXT arm emits `s_1asm(emit_fmt("%s:", _.lbl_α))` first. Broker now does `jmp _.lbl_α` (fresh) and `jmp _.lbl_β` (retry). Gates: smoke_prolog 5/5 ✅ smoke_snobol4 7/7 ✅ smoke_icon 5/5 ✅ crosscheck_prolog 128/0 ✅.

### BB_PL_SEQ data layout (conjunction engine)

```
nd->c[i]       = goal node i
nd->c[i]->state = 0=fresh, 1=live (resumable)
nd->c[i]->opaque = PlCallSt* for BB_PL_CALL when state==1
```
Forward: run `bb_exec_once(goal->cfg)`. Backtrack: scan left for state==1 node, call `bb_exec_resume`. Key: `bb_exec_once` / `bb_exec_resume` are C entry points today; they become emitted boxes eventually.

### BB_CHOICE data layout (multi-clause selector)

```
nd->state    = next clause to try (0=fresh)
nd->counter  = (int64_t) trail mark saved at last success
nd->opaque   = (Term**) g_pl_env saved at last success
nd->c[i]     = BB_SUCCEED node; nd->c[i]->opaque = BB_graph_t* clause body
```
β: `trail_unwind(mark)`, restore `g_pl_env`, try `nd->c[nd->state]` body.

### Key fix this session

`g_pl_trail` was never initialized in Mode 4 (`rt_init` skipped `polyglot_init`). Fix: `trail_init(&g_pl_trail)` added to `rt_init`. `1a65b62b`. factorial(5)=120 ✅.

### Next: PL-T-4..7 (in GOAL-BB-TEMPLATE-LADDER)

`BB_PL_CALL` (PL-T-4), `BB_CHOICE` (PL-T-5), `BB_PL_ALT` (PL-T-6), `BB_CUT` (PL-T-7). Each: translate the corresponding `bb_exec.c` block (lines 1783–1935) to x86 TEXT. No new `rt_*`. No C Byrd box functions.

---

## ⛔ Step PJ-RT-PURGE — Delete every RT function that implements 4-port (α/β/γ/ω) logic for Prolog

**Rule being enforced (already written in THIS file, three times):**
- INVARIANT 9 (line ~199): *"BB templates may not call RT functions. PERIOD."*
- Translation method rule 5 (line ~207): *"No `rt_*` port-logic helpers."* Permitted external calls are ONLY the side-effect-free utilities: `trail_mark`, `trail_unwind`, `unify`, `prolog_atom_intern`, `term_new_int`, `term_new_atom`.
- PL-T-4..7 (line ~258): *"No new `rt_*`. No C Byrd box functions."*
- RULES.md line 1: *"NO C BYRD-BOX FUNCTIONS … ZERO permitted."*

**Scope (Lon, 2026-05-26):** Delete ONLY the RT functions that carry 4-port / control-flow / port-state logic. Do NOT touch string/term *conversion* helpers — those stay. The port logic must instead be emitted as inline x86 in the corresponding `bb_*` template (translating the matching `case` in `bb_exec.c`), per the method in this file.

**Classification of the `rt_pl_*` surface at HEAD (`4bd0ffb6`):**

| RT function | Called by template | Verdict |
|---|---|---|
| `rt_pl_once` | `bb_pl_seq.cpp` | **DELETE** — ONCE-port driver (looks up pred, drives `bb_broker`/`bb_exec_once`); pure 4-port control. |
| `rt_pl_unify_generic` | `bb_unify.cpp` | **DELETE** — encapsulates the BB_UNIFY γ/ω decision + trail side-effects in C. |
| `rt_pl_unify_var_atom` | `bb_unify.cpp` | **DELETE** — same; unify port decision in C. |
| `rt_pl_unify_var_var` | `bb_unify.cpp` | **DELETE** — same. |
| `rt_pl_arith` | `bb_arith.cpp` | **KEEP** — pure expression evaluation (term→long), no port state. Conversion. |
| `rt_pl_write_atom` | `bb_builtin.cpp` | **KEEP** — builtin I/O effect (fputs); not a port. Conversion/effect. |
| `rt_pl_write_var` | `bb_builtin.cpp` | **KEEP** — builtin I/O effect (term→text→stdout). Conversion/effect. |
| `rt_pl_atom_push` | `bb_atom.cpp` | **KEEP** — term→DESCR + vstack push. Conversion. |
| `rt_pl_var_push` | `bb_pl_var.cpp` | **KEEP** — slot deref→DESCR + vstack push. Conversion. |
| `rt_pl_b_*` (builder family) | emit_sm.c (Mode-4 startup) | **KEEP** — graph reconstruction at binary startup, not runtime port logic (separate concern; revisit only if Lon directs). |

**Sub-steps — DO ONE AT A TIME, each its own commit, gates green between each. For each: (a) write the inline-x86 port logic into the BB template translating the matching `bb_exec.c` case, (b) delete the RT function from `rt.c` + `rt.h`, (c) confirm no remaining caller, (d) run GATE-1..4 + all six smoke gates, (e) commit.**

- [ ] **PJ-RTP-1** — `rt_pl_unify_var_atom`: emit BB_UNIFY var-vs-atom port logic inline in `bb_unify.cpp` (γ on bind/match, ω on mismatch; trail via whitelisted `trail_mark`/`unify`). Delete `rt_pl_unify_var_atom` from rt.c/rt.h.
- [ ] **PJ-RTP-2** — `rt_pl_unify_var_var`: emit BB_UNIFY var-vs-var port logic inline in `bb_unify.cpp`. Delete from rt.c/rt.h.
- [ ] **PJ-RTP-3** — `rt_pl_unify_generic`: emit BB_UNIFY generic-fallback port logic inline in `bb_unify.cpp`. Delete from rt.c/rt.h.
- [ ] **PJ-RTP-4** — `rt_pl_once`: emit BB_PL ONCE-port driver inline (translate `bb_exec_once` entry in `bb_exec.c`); `bb_pl_seq.cpp` must drive α/β/γ/ω directly. Delete `rt_pl_once` from rt.c/rt.h. NOTE: this is the SM_BB_ONCE_PROC entry shared with Mode 2/3 — verify those paths still resolve (they use `pl_bb_once_proc_by_name` directly, not `rt_pl_once`, but confirm).

**Done when:** zero `rt_pl_*` *port-logic* functions remain in rt.c/rt.h; the four KEEP/conversion helpers are the only `rt_pl_*` runtime callees from BB templates; `grep -nE "rt_pl_(once|unify)" src/runtime/rt/rt.{c,h}` returns nothing; GATE-1..4 + six smoke gates non-regressive.

---

## ⛔ Step PJ-DEL-ONCEPROC — Eradicate the SM_BB_ONCE_PROC opcode (C-traversal, never jumps into a flat BB)

**Lon verdict (2026-05-26):** `SM_BB_ONCE_PROC` (a) uses a C function to traverse a graph — `pl_bb_once_proc_by_name → bb_broker → pl_bb_dcg → bb_exec_once/_resume` in `bb_exec.c` — and (b) does NOT use an emitted BB (`node.fn` == C `pl_bb_dcg`, not flat x86). Same forbidden category as the already-tombstoned `SM_BB_PUMP`/`SM_BB_ONCE` (SM.h: *"stub, never jumped into a BB"*). DELETE it.

**Method = tombstone (matches existing convention).** The SM enum is positional and an index-aligned name table (`sm_prog.c`) + audit table depend on it; physical removal would renumber every later opcode. So rename `SM_BB_ONCE_PROC` → `SM_UNUSED_6` in the enum (inert slot) and DELETE all machinery that emits or handles it.

**Consequence (accepted):** Prolog top-level execution (`:- initialization(X).`) goes dead through this path until the flat-x86 BB replacement exists. smoke_prolog already 0/5 on this branch lineage — no gate regresses.

**Eradication sites (10):**
- [ ] **PD-1** `src/include/SM.h:86` — `SM_BB_ONCE_PROC` → `SM_UNUSED_6 /* was SM_BB_ONCE_PROC — C bb_exec.c walker, never jumped into flat x86 BB */`.
- [ ] **PD-2** `src/lower/lower.c:1462,1603` — delete the two `SM_emit_si(..., SM_BB_ONCE_PROC, ...)` emit sites + now-dead `:- initialization`/predicate-registration logic around them.
- [ ] **PD-3** `src/emitter/emit_core.c:758,810` — remove the dispatch `case` + the grouped case.
- [ ] **PD-4** `src/emitter/emit_sm.c:1168` — remove from opcode list.
- [ ] **PD-5** `src/processor/sm_jit_interp.c:241,527,1287,1677,2103` — delete `h_bb_once_proc`, handler-table wiring, dispatch cases.
- [ ] **PD-6** `src/processor/sm_interp.c:594-609` — delete Mode-2 case.
- [ ] **PD-7** `src/emitter/SM_templates/sm_bb_calls.cpp` — delete `sm_bb_once_proc` template fn (keep SM_BB_PUMP_PROC parts).
- [ ] **PD-8** `src/runtime/rt/rt.c,rt.h` — delete `rt_pl_once` (overlaps PJ-RTP-4; this also discharges that sub-step).
- [ ] **PD-9** `src/lower/sm_prog.c:252` — `"SM_BB_ONCE_PROC"` → `"SM_UNUSED_6"`.
- [ ] **PD-10** `src/tools/emit_per_kind_audit.c:238` — remove the audit entry.

**Done when:** `grep -rn SM_BB_ONCE_PROC src/` returns nothing (except the SM.h tombstone comment if kept); build GREEN; six smoke gates non-regressive (snobol4 13/13, icon 5/5, snocone 5/5, rebus 4/4, raku 5/5; prolog 0/5 pre-existing); Mode-4 broad corpus 126/26 unchanged.

**✅ DONE 2026-05-26 (Opus 4.7) `38e66809`.** All 10 sites eradicated; tombstoned to SM_UNUSED_6; rt_pl_once deleted (also discharges PJ-RTP-4). grep = comments/tombstone only. Build GREEN; snobol4 13/13, icon/snocone/raku 5/5, rebus 4/4, crosscheck_prolog 132/0, Mode-4 broad 126/26 — all unchanged.

---

## ⛔ Step PJ-DEL-PUMP — Eradicate SM_BB_PUMP_PROC, SM_BB_PUMP_SM, SM_BB_PUMP_CASE (C walkers, never jump into x86 BBs)

**Lon verdict (2026-05-26):** audit of all live `SM_BB_*` opcodes. Three more are the same forbidden category as SM_BB_ONCE_PROC — they traverse via C, never jump into an emitted flat x86 Byrd box:
- **SM_BB_PUMP_PROC** — Icon twin of ONCE_PROC: `icn_bb_pump_proc_by_name` → `node.fn = icn_bb_dcg`/`icn_bb_oneshot` (C) → `bb_broker` → C `bb_exec`.
- **SM_BB_PUMP_SM** — `bb_broker_drive_sm(gs,…)` which RE-ENTERS `sm_interp_run` (C SM interpreter) in a loop. Pure C generator driver.
- **SM_BB_PUMP_CASE** — pops case PCs, calls `sm_eval_subexpr(pc)` (C sub-expression evaluator).

**KEEP: SM_BB_SWITCH** — the brand-new GOLDEN-BB-RULE opcode. By definition it jumps into Byrd-Box land: `node->fn(node->ζ, entry)` is the indirect call into an emitted flat x86 box. This is the SOLE legitimate BB-dispatch opcode and the intended end-state (one switch opcode → x86 boxes).

**Method:** tombstone each in the enum (SM.h) → `SM_UNUSED_7/8/9` (positional enum + index-aligned name table in sm_prog.c; do NOT renumber). Delete ALL machinery. Accepted consequence: Icon generator-proc pumping + case-pump + SM-pump dispatch go dead through these paths until flat-x86 BB replacements exist (Icon honest-gate rungs may drop; that path was never jumping into x86 anyway).

**Site map (verified this session; mirror the PD-1..10 pattern):**
- [ ] **PP-1 SM.h** — `SM_BB_PUMP_PROC`→`SM_UNUSED_7`, `SM_BB_PUMP_CASE`→`SM_UNUSED_8`, `SM_BB_PUMP_SM`→`SM_UNUSED_9` (keep SM_BB_SWITCH).
- [ ] **PP-2 sm_prog.c name table** (the line with `"SM_BB_PUMP_PROC","SM_BB_PUMP_CASE","SM_BB_PUMP_SM"`) — rename to matching `"SM_UNUSED_7/8/9"`.
- [ ] **PP-3 emit_per_kind_audit.c** — remove the three `{ SM_BB_PUMP_*, "..." }` audit entries.
- [ ] **PP-4 emit_core.c** — remove dispatch `case SM_BB_PUMP_PROC: return sm_bb_pump_proc(pSM);` and any PUMP_CASE/PUMP_SM cases + their entries in the grouped no-AST case list.
- [ ] **PP-5 emit_sm.c** — remove `SM_BB_PUMP_PROC` (and PUMP_CASE/PUMP_SM if present) from the opcode list (the one ONCE_PROC was just removed from).
- [ ] **PP-6 sm_interp.c (Mode 2)** — delete the three `case SM_BB_PUMP_PROC/PUMP_CASE/PUMP_SM` bodies. Then `bb_broker_drive_sm` / `bb_broker` / `icn_bb_pump_proc_by_name` / `icn_bb_dcg` / `icn_bb_oneshot` / `sm_eval_subexpr` likely become orphaned — delete those too if no remaining callers (grep first; SM_BB_SWITCH does NOT use them — it calls node->fn directly).
- [ ] **PP-7 sm_jit_interp.c (Mode 3)** — delete `rt_bb_pump_proc` + `h_bb_pump_proc`/`h_bb_pump_case`/`h_bb_pump_sm`, their `g_handlers[...]=` wiring, and the bake + SB-LINEAR dispatch cases (mirror PD-5).
- [ ] **PP-8 sm_bb_calls.cpp** — delete `sm_bb_pump_proc` template (the file is now empty of live templates — consider deleting the file + its Makefile SRCS entry, or leave a stub). Remove protos in sm_templates.h / emit_templates.h.
- [ ] **PP-9 rt.c/rt.h** — delete `rt_bb_pump_proc` if present (Mode-4 helper). KEEP conversion helpers.
- [ ] **PP-10 lower.c** — find the emit site(s) for SM_BB_PUMP_PROC/CASE/SM (Icon generator-proc lowering); neutralize like PD-2 (lower to nothing).

**Done when:** `grep -rn "SM_BB_PUMP_PROC\|SM_BB_PUMP_SM\|SM_BB_PUMP_CASE" src/` = comments/tombstones only; SM_BB_SWITCH intact and still the BB-dispatch path; build GREEN (scrip + libscrip_rt); smoke gates: snobol4 13/13, snocone 5/5, rebus 4/4, raku 5/5 non-regressive (icon may drop — note honestly, accepted); Mode-4 broad 126/26 unchanged.

---

## ⛔ Step PJ-AG-WIRE — Attribute-Grammar lowering: AST → properly 4-port-wired BB graph

**This is the Prolog mirror of GOAL-ICON-BB Phase H (the Attribute Grammar, decided with Lon 2026-05-26) — DO EXACTLY WHAT ICON DOES; it is correct.** Read GOAL-ICON-BB.md §"Phase H — The Attribute Grammar" + §"GOLDEN BB RULE" + the G-2/RT-DELETE ladder in full first. The AG is identical; only the port *semantics* differ per the language-A/language-B rule in this file's Invariants. The goal: every Prolog AST node is lowered into a `BB_t` whose four ports are wired by a single attribute-grammar traversal (proper LOWER), then walked by the emitter's port-DFS and emitted as inline x86 via per-kind `BB_templates/bb_*.cpp` templates (proper EMITTER) — exactly Icon's two-path structure.

**Mimic Icon precisely on all four points:**

1. **AG threading (LOWER).** `lower_pl` takes the 4-attribute form `lower(cfg, tree, γ_in, ω_in, &α_out, &β_out)`: γ/ω inherited DOWN, α/β synthesized UP. This is the literal "STRUCTURAL GAP" Icon's G-1 names (GOAL-ICON-BB.md:165-174) — field renaming alone is not enough; the lowerer must thread continuations into every node it creates.

2. **GOLDEN BB RULE — no new fields, and the aux-storage discipline (THE bug fix).** `BB_t` is the IR for all modes; it has ONLY `sval`/`ival`/`dval` (compile-time payload, **survives `bb_reset`**) + `value`/`counter`/`state` (runtime-mutable, **zeroed by `bb_reset`** — confirmed scrip_ir.c:63-65). The smoke 0/5 bug was storing PERSISTENT compile-time aux (goal/clause/arg vectors) in `counter`, which `bb_reset` wipes. **Icon's own resolution is the model:** BB_INITIAL moved its has-run flag from a runtime slot to `ival` *"since ival is IR payload that survives bb_reset, unlike state"* (GOAL-ICON-BB.md:645). So: control flow → ports (no aux at all for SEQ/CHOICE once they are γ/ω-chains); any genuinely-needed persistent pointer (e.g. a per-construct state record, JCON-style) → **bit-cast into `ival`/`dval`** (the reset-surviving payload, option (A) of the HANDOFF), NEVER `counter`. Transient per-activation state (trail mark, current-clause cursor) MAY live in `counter`/`state` because it is *meant* to reset. This split — persistent-in-payload, transient-in-runtime — is what removes the aliasing by construction.

3. **Gold per-construct reference.** Icon transliterates each kind's port wiring from JCON `irgen.icn`'s `ir_a_<Construct>` proc (the absolute rule at GOAL-ICON-BB.md:42-55). Prolog has no JCON; the per-construct spec is the standard Byrd-box / WAM control semantics, encoded in the wiring table below. Treat that table the way Icon treats `ir_a_*`: it is the authority for which port fires when.

4. **Emitter templates (EMITTER).** Mirror Icon's emit path: the emitter follows `α/β/γ/ω` depth-first (Icon's `walk_bb_port`, GOAL-ICON-BB.md:488-489), and each Prolog BB kind emits inline x86 from its `src/emitter/BB_templates/bb_pl_*.cpp` template — **NO C Byrd box, NO new `rt_*` port helper** (RULES.md line 1; this goal's INVARIANT 9; the G-2 RT-DELETE ladder Icon just completed for `rt_binop_gen`/`icn_every_box`/`icn_list_bang`/`icn_to_by_rt`). Port logic translates the matching `bb_exec.c` case into TEXT/BINARY x86 arms with a `bb_bin_t` reloc table (the pattern SBL-PAT-PRIM established for SNOBOL4). Permitted external calls are only the side-effect-free conversion/effect helpers (`trail_mark`, `unify`, `term_*`, `prolog_atom_intern`, the KEEP list in PJ-RT-PURGE) — never a four-port dispatcher.

**The four attributes (identical to Phase H; Prolog port meanings):**

| Port | AG kind | Direction | Prolog meaning |
|------|---------|-----------|----------------|
| **γ** (gamma) | **inherited** | DOWN | continuation on SUCCESS — the next goal / clause-success exit |
| **ω** (omega) | **inherited** | DOWN | continuation on FAILURE — pop choice-point + unwind trail to the predecessor's β |
| **α** (alpha) | **synthesized** | UP | this node's FRESH-solve entry |
| **β** (beta) | **synthesized** | UP | this node's REDO (retry / next-solution) entry |

Lowering signature (mirror H-1): `lower_pl(cfg, tree, γ_in, ω_in, BB_t **α_out, BB_t **β_out)`. γ/ω handed down; α/β written back up. Door (fresh vs redo) lives in the **target node's `state`** field, stamped by the transferer before control passes — exactly as bb_exec.c already does (`X->state=0` fresh / `X->state=1` redo). One pointer per port; a pointer names the BOX, the door selector lives in the target's `state`. No label IR.

**Per-construct wiring spec — the Prolog control constructs and how each threads γ/ω and synthesizes α/β:**

| Construct (BB kind) | α (fresh) | β (redo) | γ wiring (success) | ω wiring (failure) |
|---|---|---|---|---|
| `BB_PL_SEQ` (conjunction `a, b, c`) | first goal's α | — (redo enters via last failing goal's β) | `goal[i].γ = goal[i+1].α`; last goal `.γ = γ_in` | `goal[i].ω = goal[i-1].β` (fail → redo the goal to the LEFT); first goal `.ω = ω_in` |
| `BB_CHOICE` (clause alternatives / `;`) | first alternative's α | next untried alternative's α | each alt `.γ = γ_in` (a solution flows out) | alt[i] `.ω = alt[i+1].α` via β-resume; last alt `.ω = ω_in` (all clauses exhausted) |
| `BB_PL_CALL` (predicate call) | callee entry (callee's α) | callee's β (next solution of callee) | callee success → `γ_in` | callee exhausted → `ω_in` |
| `BB_PL_UNIFY` | self (leaf) | — | bind/match → `γ_in` (trail via whitelisted `trail_mark`/`unify`) | mismatch → `ω_in` |
| `BB_PL_CUT` | self | — | `γ_in` (commit) | sets cut barrier: discard choice-points up to the parent clause entry, then `ω_in` |
| `BB_PAT_ARBNO` / DCG repetition | body's α | body's β (next length) | body success → `γ_in` | body exhausted → `ω_in` |
| leaf (`BB_PL_ATOM`, `BB_PL_VAR`, arith/builtin) | self | — | `γ_in` | `ω_in` |

These are the same topology JCON's `ir_a_*` procedures encode (in irgen.icn) for Icon, with Prolog's backtracking ports substituted: where Icon's ω advances a generator counter, Prolog's ω pops a choice-point and unwinds the trail (Invariant: never invoke language-A's bridge handler with language-B's BB object).

**Sub-steps — DO ONE AT A TIME, each its own commit, gates green between each. LOWER first (AGW-1..7), then EMITTER (AGW-8..10).**

### Proper LOWER (AG threading)
- [x] **PJ-AGW-1** — `lower_pl` aux-discipline: persistent Prolog aux pointers migrated `counter→ival` (survives `bb_reset`, option A per Icon's BB_INITIAL precedent). **DONE 2026-05-26 (Opus 4.7).** All three structs (`bb_pl_seq_state_t`/`bb_pl_call_state_t`/`bb_pl_choice_state_t`) across every writer+reader: `lower_pl.c` (4), `bb_exec.c` (5), `emit_sm.c` (6), `rt.c` Mode-4 builder+sub-builder. Arity recovered from `zc->arity`. This removes the `bb_reset`-wipes-aux hazard permanently. NOTE: the full 4-attribute `lower(cfg,tree,γ,ω,&α,&β)` signature rewrite (γ/ω-chains replacing SEQ/CHOICE aux entirely) is still the larger AGW-2..7 work; this step did the aux-storage half that unblocks execution.
- [x] **PJ-AGW-1b** — Restore Prolog program-entry dispatch via the sanctioned `SM_BB_SWITCH` opcode (PJ-DEL-ONCEPROC had tombstoned `SM_BB_ONCE_PROC` with no replacement → initialization lowered to nothing). **DONE 2026-05-26 (Opus 4.7).** `lower.c` initialization directive now emits `SM_BB_SWITCH` with `a[0].s="name/arity"` key, `a[1].i=arity`, `a[2].i=SM_BBSW_PL_ENTRY` (new tag, SM.h). Mode-2 `sm_interp.c` `SM_BB_SWITCH` handler honors the tag: resolves the predicate at runtime via `pl_bb_once_proc_by_name`→`pl_bb_dcg`→`bb_exec_once`, pushing/popping `pl_bb_env` — exactly the deleted `SM_BB_ONCE_PROC` logic folded into the one kept BB-dispatch opcode. **GATES: smoke_prolog 0/5→5/5 ✅, unified_broker 18→23, icon_all_rungs 189 (baseline, no regression), icon 5/5, snocone 5/5, rebus 4/4, raku 5/5, snobol4 13/13** — all green. crosscheck_prolog 126/6: the 6 FAILs are all `--run vs --interp` (Mode 3 lags Mode 2, which now works) — NOT a regression (both modes previously produced empty/agreed; Mode 2 advanced past Mode 3). → PJ-AGW-1c.
- [x] **PJ-AGW-1c** — ✅ DONE 2026-05-26 (Opus 4.7) `c20ba50e`. Done the CORRECT way: route Mode-3
  (`--run`) Prolog through `sm_interp_run` (the Mode-2 interpreter ENGINE) by detecting `is_prolog`
  (.pl) in `scrip.c`. This is NOT a runtime BB-graph walker in `sm_run_linear`, and does NOT keep the
  graph alive past `stage2_free_bb_after_emit` (that was the earlier reverted attempt). crosscheck_prolog
  FAIL 6→0 (all three modes now agree). SNOBOL4/Icon linear `--run` untouched. The original 1c scope
  (wiring `SM_BBSW_PL_ENTRY` into the `sm_emit_linear` codegen for a future flat-x86 Mode-3 path) is
  SUPERSEDED by AGW-9/10 — Mode 3 routes through interp until the `bb_pl_*.cpp` templates land.
- [x] **PJ-AGW-1d (was PJ-AGW-1's signature half)** — Extend `lower_pl` to the full 4-attribute signature `lower_pl(cfg, tree, γ_in, ω_in, &α_out, &β_out)` (mirror H-1). Leaf nodes set `*α_out = *β_out = nd; nd->γ = γ_in; nd->ω = ω_in;`. This is the prerequisite for the γ/ω-chain SEQ/CHOICE rewrites (AGW-2/3) that eliminate the aux structs altogether. Gate: clean build, no behaviour change.
- [x] **PJ-AGW-2** — `BB_PL_SEQ` (conjunction): replace the goal-vector-in-`counter` representation with the γ/ω-chain per the table above (mirror H-2's BB_SEQ γ-chain, but Prolog ω points LEFT to the predecessor's β, not forward — conjunction backtracks). Delete the `if (!sq) return nd->ω;` guard and the `bb_pl_seq_state_t` aux. bb_exec.c `BB_PL_SEQ` case: walk via ports, not the stashed vector. Gate: smoke_prolog conjunction case executes; broker non-regressive.
- [~] **PJ-AGW-3 (partial — `c0a79a9d`)** — `BB_CHOICE` now resumes the last-successful clause body's OWN inner choice point before advancing to the next clause. On β-resume, if the last body still has a live choice point (`bb_body_has_live_choice`: any BB_PL_CALL/BB_CHOICE/BB_PL_ALT with state>0), `bb_exec_resume` it first; a deterministic body (facts) has none → unwind + advance immediately (keeps fact-clause backtracking terminating). `bb_pl_choice_state_t` gained `last_body`/`last_act`; snapshot/restore (scrip_ir.c) carry them. RESULT: recursive `member/2` generates a,b,c (was a,b — last element dropped); fact backtracking still a,b,c. Gates non-regressive, median-of-3 stable: smoke_prolog 5/5, crosscheck_prolog 132/0, icon rungs 195, broker 23, snobol4 13/13. ⛔ **OPEN → PJ-AGW-3b:** under the disjunction driver `goal, write, nl, fail ; true` `member` OVER-GENERATES — after exhausting `[a,b,c]` the choice keeps yielding empty (unbound-X) solutions → trailing blank lines, so rung05 is NOT yet a clean `.expected` PASS (rung suite still 15). Root: exhaustion-propagation across the BB_PL_SEQ backtrack pump + nested BB_CHOICE/BB_PL_CALL resume — the SEQ pump must stop re-pumping a choice that has truly failed. Also: under multi-`main`-clause driver (`main :- …,fail. main :- …`) `member([a,b])` yields only `a` then the 2nd main clause (the SEQ doesn't backtrack into the call) — same handshake. Gate when closed: rung05 PASS, crosscheck non-regressive.
- [x] **PJ-AGW-3b** ✅ DONE 2026-05-26 (Opus 4.7) — SEQ/CHOICE exhaustion handshake. TWO root causes, both fixed.
  (1) **Under-generation** (`member` yielded only `a` under bare `fail`): `pl_flatten_conj` splits a clause body's
  `,`-conjunction into separate `clause->c[]` statements, and `lower_pl_clause_body` lowered each with `ω=NULL` —
  so `fail` EXITED the clause instead of backtracking into the nearest left generator. FIX: `lower_pl_clause_body`
  now wires the same ω/β backtrack chain that `lower_pl_goal`'s conjunction case builds (Pass 3/4): each body goal's
  ω = nearest resumable predecessor (BB_PL_CALL/BB_CHOICE/BB_PL_ALT); goal[0].ω stays NULL (clause failure → outer ω).
  (2) **Over-generation** (after `[a,b,c]`, endless unbound-X empties): `bb_snapshot_state`/`bb_restore_state`
  captured only `_bcfg`'s own nodes, NOT the BB_CHOICE clause-body sub-graphs (`zc->bodies[]`), which are SHARED
  across recursive activations. A deeper `member` activation clobbered the parent frame's clause-body cursor, so the
  resumed parent re-succeeded instead of failing. FIX: deep snapshot/restore — `bb_node_state_t` gains
  `ch_body_snaps[]`/`ch_nbodies`; snapshot recurses one level into each clause body (the callee's own predicate
  graph is isolated by that CALL's runtime `cs->act`), restore deep-restores + frees the sub-snapshots.
  **RESULT: rung05 PASS in BOTH `--interp` (Mode 2) AND `--run` (Mode 3), byte-identical to `.expected` (a/b/c, no
  trailing empties).** GATES (median-of-3): smoke_prolog 5/5; rung suite 15→16 (rung05 up); crosscheck_prolog FAIL=0
  (all three modes agree; PASS 125-127 / SKIP 5-7 variance is pre-existing mktemp-race, NOT a regression);
  snobol4 13/13, icon 5/5, snocone 5/5, rebus 4/4, raku 5/5. ASAN (`detect_use_after_free=1`) CLEAN on bare-fail
  member, rung05 both modes, and fib(6)=8 — zero use-after-free / invalid-free on the deep snapshot/restore frees.
- [x] **PJ-AGW-4** — ✅ DONE 2026-05-26 (Opus 4.7) `254d3038`. Activation-safe recursion for `BB_PL_CALL`
  + `BB_CHOICE`. NOTE: the "snapshot/restore is unnecessary" prediction in the original step text was
  WRONG for the current architecture — clause bodies + the callee predicate graph are SHARED across
  activations (same `BB_graph_t` re-entered under recursion), so the snapshot/restore IS required (mirrors
  Icon BB_CALL bb_exec.c:218). Fixed: snapshot/restore the callee graph around `bb_exec_once`/`bb_exec_resume`
  (BB_PL_CALL) and the clause-body sub-graph (BB_CHOICE); extended `bb_node_state_t` to also capture the LIVE
  per-activation aux (PL_CALL.cs, CHOICE.cur/mark/saved_env). fib(6)→8, p(3)→2; smoke_prolog 5/5; rung08 PASS;
  icon_all_rungs 189→195. (The aux-free pure-port representation the step envisioned remains a possible future
  cleanup, but is not required for correctness.)
- [x] **PJ-AGW-5 (partial)** — ✅ if-then-else `(Cond->Then;Else)`=TT_IF lowering DONE 2026-05-26 `fd2bcf78`
  (γ/ω-chain: Cond.γ→Then, Cond.ω→Else; deterministic conditions need no barrier). ⛔ STILL TODO: the proper
  `BB_PL_CUT` cut-barrier via ω rewiring (discard choice-points to parent clause entry) + cut-on-cond commit
  for non-deterministic ITE conditions. Gate: cut smoke case correct; backtracking past a cut stops.
- [x] **PJ-AGW-6 ✅ DONE 2026-05-26 (Opus 4.7) `b2c70937`** — compound terms + lists (prior partial) PLUS
  the arith regression CLOSED. The earlier partial added `BB_PL_STRUCT` (compound terms `f(X,a)` + `TT_MAKELIST`
  lists, cons chain `'.'(H,T)`), `pl_node_to_term`, and the head-arg var-slot fix (bare head vars keep arg
  position, nested/body vars above arity) — that took GATE-3 rung suite 5→6 but opened crosscheck_prolog
  132/0→122/10 because `BB_ARITH` was integer-only AND evaluable functors (pi/e, sqrt/exp/…, `**`/`^`, max/min/gcd,
  bitwise, truncate/round/floor/ceiling, float_*) fell through lowering into `BB_PL_STRUCT` → garbage doubles in
  BOTH modes. **FIX = perfect the LOWER + executor:** (1) `lower_pl.c` `pl_is_arith_functor` recognizer routes ALL
  evaluable functors (arity 0/1/2) into `BB_ARITH` (functor in sval, arity in ival, operands on α/β; no γ-chain
  among operands — they are walked by the recursive evaluator, not the port-walker). (2) `bb_exec.c` recursive
  float-aware `pl_arith_eval(BB_t*)` returns type-preserving `DESCR_t` (DT_I/DT_R) per ISO promotion, walks the
  BB graph (IR not AST — **NOT a Byrd box**: signature is `(BB_t*)` not `(void*,int)`, no port logic; ports stay
  in the `case BB_ARITH` via `nd->γ`/`nd->ω`). `is`/comparison operands routed through it (resolves bare pi/e atoms
  + nested arith). New `pl_format_float` (SWI shortest round-trip, always a decimal point). **RESULTS:
  crosscheck_prolog 122/10→132/0 (regression CLOSED); GATE-3 rung suite 6→15 (+9: rung23 bitwise/max_min/power/
  sign/truncate + rung29 float_constants/conversion/math/parts/gcd); smoke_prolog 5/5; icon rungs 195; broker 23;
  snobol4 dual-mode 13/13 — all non-regressive, median-of-3 stable.** Rebased onto upstream `4d498065` (mode-3 JIT
  real-literal xmm0/rdi calling-convention fix) — coexists cleanly; `--run` float output now byte-matches `--interp`.
- [ ] **PJ-AGW-6b** — `BB_PAT_ARBNO`/DCG repetition port wiring per table. Gate: DCG smoke cases.
- [ ] **PJ-AGW-7** — LOWER sweep: `grep -nE 'nd->counter\s*=|nd->c\[|nd->n\b' src/lower/lower_pl.c src/lower/lower_pat_dcg.c src/lower/bb_exec.c` (Prolog kinds) returns nothing; no persistent aux in a reset-cleared slot. Gate: GATE-1 smoke_prolog 5/5 + GATE-3 rung-ladder PASS ≥ prev + the other five smokes.

### Proper EMITTER (Mode-4 x86 templates over the AG-wired graph)
- [~] **PJ-AGW-8 (partial)** — ✅ 2026-05-26 `6118399a`: Mode-4 SM_BB_SWITCH PL-entry now EMITS valid asm
  (assembles + links) — `emit_core.c sm_bb_switch()` emits `call rt_bb_switch_pl_entry@PLT`; the predicate
  graph is rebuilt at startup by the existing `rt_register_predicates_pl` registry. ⛔ STILL TODO: emitted
  binaries SEGFAULT at runtime because the PJ-9d registry BUILDER (`rt_pl_b_*`) predates the AG lowering —
  it walks only `cfg->all[]`, NOT the AG-wired α/β/γ/ω ports or the BB_CHOICE clause-body sub-graphs, so the
  rebuilt graph is malformed. ALSO: `xa_file_header` emits `rt_register_predicates_pl` BEFORE `rt_init` (GC
  alloc before init — investigate). The proper deliverable is the port-DFS `walk_bb_port` for Prolog kinds +
  per-kind `bb_pl_*.cpp` inline-x86 templates (AGW-9), which makes the registry-builder reconstruction
  unnecessary. Gate target: `--compile --target=x86` single-clause predicate runs via run_prolog_via_x86_backend.sh.
- [ ] **PJ-AGW-9** — Per-kind `bb_pl_*.cpp` inline-x86 templates: for each Prolog four-port kind (`bb_pl_seq`, `bb_choice`/clause-alt, `bb_pl_call`, `bb_pl_unify`, `bb_pl_cut`, `bb_pat_arbno`), translate the matching `bb_exec.c` case into TEXT+BINARY x86 arms with a `bb_bin_t` reloc table (offsets for the port rel32 sites + β-define), emitting via `bb_emit_asm_result` (the SBL-PAT-PRIM pattern). NO C Byrd box, NO new `rt_*` port helper — only the KEEP conversion/effect helpers. One kind per commit; gate each.
- [ ] **PJ-AGW-10** — EMITTER sweep + parity: every Prolog rung that passes the proper-LOWER path (Mode 2) also produces byte-identical output in Mode 4 (`--compile --target=x86`); `grep -rnE "DESCR_t\s+\w+\s*\(\s*(void\s*\*\s*(zeta|ζ|z))\s*,\s*int\s+entry\s*\)" src/runtime/rt/ src/emitter/BB_templates/` shows no Prolog four-port C Byrd box. Gate: GATE-1..4 green; Mode-4 Prolog rung count ≥ Mode-2 rung count.

**Done when (both halves):** **LOWER** — Prolog `--interp` (Mode 2) executes via the 4-port BB graph with NO persistent aux in a reset-cleared slot (persistent pointers bit-cast into `ival`/`dval`; only transient state in `counter`/`state`); **smoke_prolog 5/5** restored *by construction*; `bb_exec.c` Prolog cases dispatch purely on ports. **EMITTER** — the emitter port-DFS walks the same graph; each Prolog four-port kind emits inline x86 from its `bb_pl_*.cpp` template with a `bb_bin_t` reloc table; ZERO Prolog four-port C Byrd box or new `rt_*` port helper remains (RULES.md / INVARIANT 9 / Icon's G-2 RT-DELETE precedent); every Mode-2-passing rung is byte-identical in Mode 4. **Gates:** GATE-1..4 green; crosscheck_prolog non-regressive; the other five smoke gates (snobol4 13/13, icon 5/5, snocone 5/5, rebus 4/4, raku 5/5) non-regressive. This supersedes the option-(b) `counter`-overload representation and resolves the HANDOFF decision in favor of option (A) (bit-cast persistent aux into payload), matching Icon's BB_INITIAL precedent.

---

## ⛔ HQ-ALIGNMENT AUDIT (2026-05-26, Opus 4.7 — Lon-requested method/technique review)

Audit of the live source tree at one4all `9be28a5` against RULES.md + GOAL-HEADQUARTERS.md Invariants + the four ABSOLUTE RULES in this file's header. Findings are EMPIRICAL (grep-verified against the source), not from the prose. **Three correction rungs are added below (PA-1..PA-3); they do not duplicate existing AGW/RTP steps — they tighten or supersede them with verified line evidence.**

**VERIFIED VIOLATIONS (Prolog surface):**

1. **`rt_pl_unify_var_atom` / `rt_pl_unify_var_var` / `rt_pl_unify_generic` — LIVE C port-logic in the RT, LIVE-called from a BB template.** `bb_unify.cpp` emits three `call rt_pl_unify_*@PLT` sites (lines 61/75/102); all three functions are still defined in `rt.c` (1090/1110/+generic). This is a direct INVARIANT-9 ("BB templates may not call RT functions") + RULES.md-line-1 violation, and it is *live in Mode 4 emission*, not a comment. Already enumerated as PJ-RTP-1..3 (still `- [ ]`) — **this audit confirms they remain open and re-asserts them as the highest-priority RT purge.** (`rt_pl_once` / PJ-RTP-4 is DISCHARGED — verified deleted at rt.c:1043 tombstone.)

2. **The five Prolog control-flow BB templates are EMPTY STUBS that delegate to the C graph-walker.** `bb_pl_seq.cpp` / `bb_pl_call.cpp` / `bb_pl_choice.cpp` / `bb_pl_alt.cpp` / `bb_pl_cut.cpp` each contain a single `return std::string();` and a header comment stating execution "enters via … `bb_exec_once → bb_exec_node`" (the C walker, `bb_exec.c`). So Mode-4 Prolog four-port logic does NOT live in templates as INLINE-ALL (HQ Invariant 11) requires — it lives in the C walker, reconstructed at binary startup by the `rt_pl_b_*` registry. This is the root cause of the AGW-8 runtime SEGFAULT and is the substance of the still-open AGW-9. **This audit re-scopes AGW-9 as the load-bearing rung and adds the explicit per-template emptiness gate (PA-2).**

3. **`pl_broker.c` holds 11 C Byrd-box functions** (`pl_true_fn`, `pl_fail_fn`, `pl_builtin_fn`, `pl_cat_fn`, `pl_unify_fn`, `pl_head_unify_fn`, `pl_deferred_env_fn`, `pl_cut_fn`, `pl_alt_fn`, `pl_choice_fn`, `pl_chunk_fn`), each `DESCR_t fn(void *zeta, int entry)`. RULES.md exempts ONLY `icn_bb_dcg` (+ `icn_lazy_box`); `pl_bb_dcg` is the documented Mode-2 reference shim. The 11 `pl_*_fn` boxes are NOT on the exempt list. **They are sanctioned ONLY IF reachable solely from Mode 1/2** (`pl_runtime.c` / `interp_eval.c` reference path). `sm_jit_interp.c` (Mode 3) `#include`s `pl_broker.h` (line 536) — **this audit adds PA-3 to PROVE the Mode-3/4 reachability is zero (or sever it), because an include is a latent edge.**

**ALIGNMENT GRADE — Prolog-BB: C+ (was tracking toward B).**
- **LOWER half (AGW-1..7): B+.** The attribute-grammar foundation is real, principled, and Lon-consulted against JCON irgen. Genuinely matches the HQ method. Held back by AGW-3b (the SEQ/CHOICE exhaustion handshake — rung05 over-generates) and the not-yet-done AGW-2/3 aux-elimination (γ/ω-chains still coexist with `bb_pl_seq_state_t`).
- **EMITTER half (AGW-8..10): D.** This is where the grade is dragged down. The Mode-4 templates are empty; Prolog "BB = emitted x86" is aspirational, not realized. Every Prolog four-port decision is still C (`bb_exec.c` walker + `rt_pl_unify_*`). The architecture's central promise (BB ≡ emitted x86, one source two consumers) is unmet for Prolog. This is honestly self-reported in AGW-8/9 prose — credit for honesty — but the work is not done.
- **Process discipline: A−.** Watermarks are meticulous, gates are run and recorded, the rung ladder is the source of truth, commits are atomic. The bookkeeping is exemplary; the gap is execution scope, not honesty.

### ⛔ Correction rungs (added by this audit — do in order; each its own commit, gates green between)

- [x] **PA-1** ✅ DONE `3a384681` (Opus 4.7, 2026-05-26). Deleted the three port-deciding `rt_pl_unify_var_atom/_var_var/_generic` C fns (INVARIANT 9). `bb_unify.cpp` now emits the γ/ω branch INLINE; operands built via pure conversion `rt_pl_node_to_term`, unified via effect helper `rt_pl_unify_terms` (1/0, no jump) — both KEEP-side per PJ-RT-PURGE. grep rt_pl_unify_{var_atom,var_var,generic}=0. BB_UNIFY per-kind cell RE-FROZEN (targeted; pre-existing 39-FAIL/GONE=6 drift untouched; my delta 471→472 FAIL→PASS, NEW=0). Gates: smoke_prolog 5/5, rung 16, crosscheck 126/0, honest 123/0/0, icon/snocone/raku 5/5, rebus 4/4, snobol4 13/13; Mode-2 unify hello/eq OK in --interp & --run. No in-tree ASAN harness (Makefile ignores sanitize flags); risk nil — GC-alloc only, Mode-2 ref path (bb_exec.c) untouched.
- [~] **PA-2 (part 1 ✅; part 2 in progress — 1/5 filled)** `4cb0651d` — `scripts/util_prolog_template_emptiness_audit.sh` created; FAILs (exit 1) while any of bb_pl_seq/call/choice/alt/cut is an empty stub (no s_*asm/emit_fmt/bytes/etc). Confirms audit claim: EMPTY=5 FILLED=0. PART 2 (= AGW-9): fill ONE template per commit (translate its bb_exec.c case to TEXT+BINARY + bb_bin_t reloc), decrementing EMPTY each time; D grade lifts only at EMPTY=0. **bb_pl_cut FILLED 2026-05-26 (Opus 4.7):** simplest box — translates the `BB_CUT` case (`g_pl_cut_flag=1; return nd->γ`) to inline x86. γ/β port jumps emitted INLINE (`bb_bin_t` reloc `{j+1,j+5,j+6}` for γ-ref/β-ref/β-define, TEXT `call rt_pl_cut_set@PLT; jmp γ; β: jmp γ`); only the flag-set EFFECT delegated to new KEEP-side helper `rt_pl_cut_set` (twin of `rt_pl_write_atom`; no port state, no entry selector, no graph walk). EMPTY 5→4. Emitted asm assembles (`as --64` rc=0); Mode-2/3 cut reference path intact (`go:-p(X),!,write(X),nl` → `1` both modes). Remaining EMPTY=4: seq/call/choice/alt. Gate per template: EMPTY drops by 1, GATE-1..4 non-regressive.
- [x] **PA-3** ✅ DONE `659ca95d` (Opus 4.7, 2026-05-26). Reachability proof = 0: sm_jit_interp.c referenced ZERO pl_box_*/pl_*_fn (it uses bb_broker/bb_node_t from bb_broker.h + icn_bb_pump_proc_by_name). The pl_broker.h include (line 536) was DEAD — build links green without it; DELETED + replaced with a documenting comment. pl_broker.c header now documents its 11 pl_*_fn boxes as the Mode-1/2 AST-reference broker ONLY (Prolog analog of the icn_bb_dcg exemption), unreachable from any --run/--compile RUN path. Gates: smoke_prolog 5/5, crosscheck 128/0, rung 16, icon/snocone/raku 5/5, rebus 4/4, snobol4 13/13; per-kind 472/39 NEW=0 unchanged.

## Watermark

```
=== 2026-05-26 Opus 4.7 — AGW-9 / PA-2-part2: bb_pl_cut FILLED (EMPTY 5→4) ===
one4all: <this commit> — BUILD GREEN. .github: (this session).
First of the five empty Prolog four-port templates filled. bb_pl_cut.cpp translates the
bb_exec.c BB_CUT case (g_pl_cut_flag=1; return nd->γ) to inline x86:
  MACRO_DEF: no form (comment). BINARY: `mov rax,0; call rax` + two rel32 port jumps,
    bb_bin_t reloc {j+1,j+5,j+6} → {γ-ref, β-ref, β-define}. TEXT: α: ; call rt_pl_cut_set@PLT;
    jmp γ; β: jmp γ.
  γ/β PORT JUMPS EMITTED INLINE (not in a C walker). Only the flag-set EFFECT is delegated to a
  NEW KEEP-side helper rt_pl_cut_set() (rt.c/rt.h) — the Prolog twin of rt_pl_write_atom: pure
  side effect, no α/β/γ/ω state, no `entry` selector, no graph walk. RULES-compliant (no C Byrd
  box, no rt_* PORT helper).
Emptiness audit: EMPTY=5 FILLED=0 → EMPTY=4 FILLED=1. Emitted asm assembles (as --64 rc=0).
Mode-2 + Mode-3 cut reference path intact: `go :- p(X), !, write(X), nl.` prints `1` (cut commits
  to first solution, no backtrack to 2/3) in BOTH --interp and --run.
GATES (all green / non-regressive): smoke_prolog 5/5; rung suite 16; crosscheck_prolog 127/0;
  icon 5/5, snocone 5/5, rebus 4/4, raku 5/5, snobol4 13/13.
Files: src/emitter/BB_templates/bb_pl_cut.cpp (filled), src/runtime/rt/rt.c (+rt_pl_cut_set),
  src/runtime/rt/rt.h (+proto).
NEXT (AGW-9, remaining EMPTY=4, one per commit): bb_pl_seq → bb_pl_call → bb_pl_choice → bb_pl_alt.
  Then AGW-8 registry-builder rewrite over AG-wired ports + AGW-10 Mode-4 parity. The seq/call/
  choice/alt boxes are materially harder than cut (state in nd->state/counter, trail mark/unwind,
  snapshot/restore of shared sub-graphs) — translate each matching bb_exec.c case carefully.
```

```
=== 2026-05-26 Opus 4.7 — HQ-AUDIT correction rungs: PA-1 ✅, PA-3 ✅, PA-2 part-1 ✅ ===
one4all: 659ca95d — BUILD GREEN. .github: (this session).
Worked the three newly-inserted HQ-ALIGNMENT-AUDIT (d93f07b2) Prolog correction rungs.

PA-2 part 1 ✅ (4cb0651d): scripts/util_prolog_template_emptiness_audit.sh — makes the
  EMITTER half (AGW-9) measurable. FAILs (exit 1) while any of bb_pl_seq/call/choice/alt/cut
  is an empty stub. Confirms the audit's claim empirically: EMPTY=5 FILLED=0. As AGW-9 fills
  one template per commit the count must reach 0 (the D grade lifts only at EMPTY=0).

PA-1 ✅ (3a384681): BB_UNIFY four-port logic emitted INLINE; the three rt_pl_unify_var_atom/
  _var_var/_generic C port-logic fns DELETED (INVARIANT-9 breach closed). bb_unify.cpp now does
  the γ/ω branch in asm (test eax,eax; je ω; jmp γ); operands built via pure CONVERSION helper
  rt_pl_node_to_term(kind,ival,sval,dval), unified via EFFECT helper rt_pl_unify_terms(l,r)
  (trail_mark+unify+unwind; returns 1/0, no jump). Both KEEP-side (conversion + effect, not a
  dispatcher). BB_UNIFY per-kind cell RE-FROZEN, TARGETED — the pre-existing 39-FAIL/GONE=6
  per-kind drift (from the older HQ 504-baseline at c4b8c880, present at clean HEAD 01f35d07)
  was left untouched; PA-1's delta was exactly the one BB_UNIFY cell FAIL→PASS (471→472, NEW=0).

PA-3 ✅ (659ca95d): proved the pl_broker.c Mode-3/4 edge is dead. sm_jit_interp.c referenced
  ZERO pl_box_*/pl_*_fn (it uses bb_broker/bb_node_t from bb_broker.h + icn_bb_pump_proc_by_name);
  the pl_broker.h include (line 536) was stale — build links green without it. DELETED the dead
  include; documented pl_broker.c's 11 pl_*_fn boxes as the Mode-1/2 AST-reference broker ONLY
  (Prolog analog of the icn_bb_dcg exemption). FACT-2 reachability = 0.

GATES (all green / non-regressive): smoke_prolog 5/5; rung suite 16; crosscheck_prolog 126-128/0
  (mktemp-race variance band); prolog_bb_honest 123/0/0; per-kind 472/39 NEW=0 GONE=6 (the 39/6 are
  PRE-EXISTING drift, NOT this session); icon/snocone/raku 5/5; rebus 4/4; snobol4 13/13.

OPEN / NEXT (priority): PA-2 part 2 = AGW-9 — fill the five empty bb_pl_*.cpp templates ONE per
  commit (cut is simplest; then seq/call/choice/alt), translating each bb_exec.c case to TEXT+BINARY
  arms + bb_bin_t reloc, gated by util_prolog_template_emptiness_audit.sh (EMPTY 5→0). THE big one;
  needs fresh context budget. Then AGW-8 registry-builder rewrite over AG-wired ports / AGW-10 parity.
NOTE on the pre-existing 39-FAIL per-kind drift: the HQ per-kind baseline (504/0/625) is frozen at
  c4b8c880; the live tree has drifted to 472/39 with GONE=6 by clean HEAD 01f35d07 — a separate
  HQ baseline-refresh concern, NOT caused by this session (verified via git-stash A/B).

=== 2026-05-26 Opus 4.7 — PJ-AGW-3b ✅ — rung05 backtracking PASS (Mode 2 + Mode 3) ===
one4all: (this session) — BUILD GREEN; ASAN-clean on recursive backtracking paths.
.github: (this session) — PJ-AGW-3b marked done; watermark + PLAN row updated.

PJ-AGW-3b ✅ — SEQ/CHOICE exhaustion handshake. Two root causes:
  (1) UNDER-generation: lower_pl_clause_body lowered each flattened-conjunction body stmt with ω=NULL,
      so `fail` exited the clause instead of redoing the nearest left generator. FIX: wire the ω/β
      backtrack chain across body goals (mirror lower_pl_goal conjunction Pass 3/4) in lower_pl.c.
  (2) OVER-generation: bb_snapshot_state/restore did NOT capture the BB_CHOICE clause-body sub-graphs
      (zc->bodies[]), which are SHARED across recursive activations — a deeper frame clobbered the
      parent's clause-body cursor, so the resumed parent re-succeeded. FIX: deep snapshot/restore of
      clause bodies (bb_node_state_t.ch_body_snaps[]/ch_nbodies) in scrip_ir.c + BB.h.
GATES (median-of-3): smoke_prolog 5/5; rung suite 15→16 (rung05); crosscheck_prolog FAIL=0 (3 modes
  agree); snobol4 13/13, icon 5/5, snocone 5/5, rebus 4/4, raku 5/5. ASAN detect_use_after_free=1 CLEAN
  on bare-fail member + rung05 (both modes) + fib(6)=8. rung05 byte-identical to .expected in Mode 2 AND 3.
NEXT: PJ-AGW-5 cut-barrier (proper BB_PL_CUT ω rewiring) or PJ-AGW-6b (DCG ARBNO), then EMITTER AGW-8..10.

=== 2026-05-26 Opus 4.7 — PJ-AGW-4 ✅ + PJ-AGW-5(partial) ✅ + PJ-AGW-1c ✅ + PJ-AGW-8(partial) ✅ ===
one4all: 6118399a — BUILD GREEN (scrip + libscrip_rt)
.github: (this session) — watermark + steps updated; RT four-port inventory refreshed.

THREE MODES NOW EXERCISED (new GATE-3 runner scripts/test_prolog_rung_suite.sh --mode interp|run|compile,
mirrors test_icon_all_rungs.sh; walks corpus rung*.pl vs .expected):
  Mode 2 (--interp): rungs 2 -> 5/5   (rung08 recursion + rung04 arith/ITE + rung07 cut now PASS)
  Mode 3 (--run):    rungs       5/5   (== Mode 2; routed through sm_interp_run)
  Mode 4 (--compile --target=x86): ASSEMBLES + LINKS (was invalid-asm); RUNTIME SEGFAULTS (expected gap).

PJ-AGW-4 ✅ (254d3038): activation-safe recursion for BB_PL_CALL + BB_CHOICE.
  Root cause = the recursion-shares-the-IR-graph problem Icon's BB_CALL already solves (bb_exec.c:218):
  a recursive call re-enters the SAME callee BB_graph_t; the inner bb_exec_once's bb_reset wipes the
  outer activation's per-node state, so the outer conjunction's later goals (e.g. the 2nd fib() call)
  see garbage and silently fail. fib(6) -> empty; p(3) with two recursive calls -> empty.
  Fix mirrors Icon's bb_snapshot_state/bb_restore_state discipline:
   - bb_exec.c BB_PL_CALL: snapshot/restore the callee graph around BOTH fresh bb_exec_once and resume
     bb_exec_resume; stash this activation's resumable state in cs->act.
   - bb_exec.c BB_CHOICE: snapshot/restore the shared clause-body sub-graph around bb_exec_once(body).
   - BB.h + scrip_ir.c: extend bb_node_state_t + snapshot/restore to ALSO capture the LIVE per-activation
     aux hanging off the persistent ival struct (BB_PL_CALL.cs, BB_CHOICE.cur/mark/saved_env) — these
     alias across concurrent activations otherwise. fib(6)->8, p(3)->2 now correct.
  Bonus: icon_all_rungs 189 -> 195 (shared snapshot improvement helped Icon too).

PJ-AGW-5 (partial) ✅ (fd2bcf78): if-then-else (Cond -> Then ; Else) = TT_IF(cond,then,else) lowering.
  Was UNHANDLED in lower_pl_goal -> whole predicate lowered to NULL -> dropped from bb_table
  ('[NO-AST] SM_BB_SWITCH PL entry main/0/0: predicate not in bb_table'). Lower as a γ/ω-chain driven
  by the outer bb_exec_once loop (NOT single-node BB_PL_ALT): Cond.γ->Then entry, Cond.ω->Else entry;
  Then.γ=Else.γ=γ_in. The comparison BB_BUILTIN executor already returns nd->ω on a false test, so the
  condition routes to Else naturally. No-else form -> Cond.ω to a BB_FAIL leaf. Deterministic conditions
  (the common rung case) need no cut-on-cond barrier; the full barrier is AGW-5 proper (still TODO).

PJ-AGW-1c ✅ (c20ba50e): route Mode-3 (--run) Prolog through sm_interp_run.
  SB-LINEAR JIT (sm_run_linear) has no SM_BB_SWITCH handler -> --run on any .pl aborted with
  'unimplemented opcode 89 (SM_BB_SWITCH)'. Per the MANDATORY READ, Mode-3 Prolog routes through the
  Mode-2 interpreter engine until bb_pl_*.cpp templates exist (AGW-8..10). Detect is_prolog (.pl) in
  scrip.c; under --run take the sm_interp_run path. This selects the interp ENGINE for the whole program
  — NOT a runtime BB-graph walker in sm_run_linear, NOT keeping the graph alive past
  stage2_free_bb_after_emit (that was the wrong AGW-1c, previously reverted). SNOBOL4/Icon linear --run
  untouched. crosscheck_prolog FAIL 6 -> 0 (all three modes now agree).

PJ-AGW-8 (partial) ✅ (6118399a): Mode-4 SM_BB_SWITCH PL-entry emit — assembles + links.
  Mode 4 emitted invalid 'UNHANDLED SM_BB_SWITCH' text -> GNU as 'no such instruction' -> no binary.
   - rt.c/rt.h: rt_bb_switch_pl_entry(name,arity) — runtime dispatcher mirroring the Mode-2 sm_interp.c
     SM_BB_SWITCH PL handler (pl_bb_once_proc_by_name -> pl_bb_env push -> bb_broker(bb_once) -> pop).
     NOT a Byrd box: carries no α/β/γ/ω port state; hands off to bb_exec.c. The predicate graph is
     rebuilt at binary startup by the already-emitted rt_register_predicates_pl registry.
   - emit_core.c: sm_bb_switch() emits, for the SM_BBSW_PL_ENTRY tag, 'lea rdi,[name]; mov esi,arity;
     call rt_bb_switch_pl_entry@PLT'. Name via strtab_label (pl_pre_intern_pred_names already interned).
     Added to codegen_sm_dispatch + sm_op_is_dispatched; emit_core.h declares strtab_label.
  OPEN (the real Mode-4 deliverable, AGW-9/10): emitted binaries SEGFAULT at runtime. The PJ-9d registry
  BUILDER (rt_pl_b_*) predates the AG lowering — it walks only cfg->all[] and does NOT reconstruct the
  AG-wired α/β/γ/ω ports or the BB_CHOICE clause-body sub-graphs, so the rebuilt graph is malformed.
  Also note: xa_file_header emits 'call rt_register_predicates_pl@PLT' BEFORE 'call rt_init@PLT' — the
  registry builder allocates BB graphs via GC before rt_init runs polyglot/trail init; a contributing
  crash factor to investigate. The proper fix is the AGW-9/10 port-DFS emitter + per-kind bb_pl_*.cpp
  inline-x86 templates (NO C Byrd box), replacing the registry-builder reconstruction entirely.

GATES (all green / non-regressive):
  smoke_prolog 5/5; prolog rungs Mode2=Mode3=5/5; crosscheck_prolog 132/0 (ORACLE_MISS 11 = frontend gap);
  icon_all_rungs 195 (>=189); icon/snocone/raku 5/5; rebus 4/4; snobol4 13/13; broker 23/26;
  SNOBOL4 Mode-4 broad 126/26 (unchanged) + A+B=42 sanity.

RT FOUR-PORT INVENTORY (PJ-RT-PURGE status @ 6118399a):
  Remaining DELETE candidates (encapsulate BB_UNIFY γ/ω decision in C):
    rt_pl_unify_var_atom (rt.c:1090), rt_pl_unify_var_var (rt.c:1110), rt_pl_unify_generic (rt.c:1122)
    -> PJ-RTP-1..3, NOT started.
  Already eradicated: rt_pl_once (PJ-DEL-ONCEPROC 38e66809, discharges PJ-RTP-4).
  KEEP (conversion/effect, no port state): rt_pl_arith, rt_pl_write_atom, rt_pl_write_var,
    rt_pl_atom_push, rt_pl_var_push, rt_pl_b_* builder family.
  rt_bb_switch_pl_entry (NEW): dispatch driver, NOT a Byrd box (no port state; defers to bb_exec.c).

NEXT (priority order):
  1. AGW-9/10 — proper Mode-4 emitter: port-DFS walk of the AG-wired graph + per-kind bb_pl_*.cpp
     inline-x86 templates (bb_bin_t reloc), replacing the segfaulting registry-builder path. THE big one.
  2. Compound-term construction (rung03 head unify, lists, structured args) — the dominant
     'predicate not in bb_table' cause keeping Mode-2 rungs at 5; lower_pl_term returns NULL on
     arity>=1 non-arith TT_FNC, dropping the whole predicate.
  3. Broader BB-land builtins (findall, atom_*, sort) — currently only in the AST reference path.
  4. AGW-5 proper: cut-on-cond barrier for if-then-else; AGW-6 BB_PAT_ARBNO/DCG; AGW-7 LOWER sweep.

=== prior watermark below ===
```
=== 2026-05-26 Sonnet 4.6 — PJ-AGW-1d ✅ + PJ-AGW-2 ✅ ===
one4all: 2844fcf6 — BUILD GREEN
smoke_prolog 5/5, broker 23, honest 128/0/0 — all unchanged.

PJ-AGW-1d ✅ (4b99b51c): lower_pl_threaded — 4-attribute AG wrapper.
  Added lower_pl_threaded(cfg, tree, γ_in, ω_in, &α_out, &β_out) mirroring
  lower_icn_expr_threaded. pl_kind_owns_omega_operand always-false placeholder.
  Clean build; no behaviour change.

PJ-AGW-2 ✅ (2844fcf6): proper 4-attribute AG lowerer for Prolog + BB_PL_SEQ port walk.
  lower_pl.c rewritten as full AG: every function lower_pl_*(cfg,tree,γ_in,ω_in,&α,&β).
  γ/ω inherited DOWN at build time; α/β synthesized UP to caller.
  Conjunction (n goals): back-to-front build; β = nearest resumable left ancestor
  (BB_PL_CALL/CHOICE/ALT β=self; leaves β=nearest-resumable-left); ω wired goal[i].ω=gβ[i-1].
  Disjunction (;): alt[0].ω=alt[1].α (fail→try second), alt[1].ω=ω_in.
  BB_PL_SEQ executor simplified: return nd->α (port graph drives all execution).
  BB_PL_CALL gets β-resume path: bb_exec_resume delivers next solution.
  Key bug fixed: pass 3 ω-wiring needed gβ computed AFTER knowing which nodes are resumable.
  Non-resumable nodes (leaves/builtins) get gβ=nearest-left-resumable-ancestor's β,
  so ω-chain skips through them correctly until hitting a node with a real retry.

CONFUSION FROM THIS SESSION (do not repeat):
  PJ-AGW-1c was mistakenly implemented as a runtime bb_exec_once drive from sm_run_linear,
  keeping the BB graph alive past stage2_free_bb_after_emit. REVERTED. The BB graph is
  consumed at emit time and freed — Mode 3 routes through sm_interp_run for Prolog until
  bb_pl_*.cpp templates are filled (AGW-8..10). crosscheck FAIL=6 --run is EXPECTED.
  GOAL-PROLOG-BB.md now has MANDATORY READ section explaining this at the top.

NEXT: PJ-AGW-3 — BB_CHOICE port wiring (multi-clause alternatives as β-chain, replacing
  bb_pl_choice_state_t aux); then AGW-4 BB_PL_CALL full AG threading; then AGW-8..10 emitter.
```

=== 2026-05-26 Opus 4.7 — PJ-AGW-1 ✅ + PJ-AGW-1b ✅ — smoke_prolog 0/5 → 5/5 ===
one4all: c6e0d8c7 — BUILD GREEN (rebased over f0f99035 GOAL-ICON-BB G-2a/b/g; build+smoke re-verified green)
.github: (this session) — GOAL top priority = Prolog rung ladder (LOWER+EMITTER); SNOBOL4 M4/bench DEFERRED;
  PJ-AG-WIRE step authored (AGW-1..10) mirroring GOAL-ICON-BB Phase H; AGW-1/1b marked done.
PJ-AGW-1 ✅: persistent Prolog aux ptrs migrated counter→ival (survives bb_reset; option A, Icon
  BB_INITIAL precedent). 3 structs × all sites: lower_pl.c(4) bb_exec.c(5) emit_sm.c(6) rt.c builder
  +sub-builder. Arity recovered from zc->arity. Removes the bb_reset-wipes-aux hazard permanently.
PJ-AGW-1b ✅: program-entry dispatch restored via the SANCTIONED SM_BB_SWITCH (PJ-DEL-ONCEPROC had
  tombstoned SM_BB_ONCE_PROC with NO replacement → :- initialization(main) lowered to nothing →
  BB_PL_SEQ never reached). New a[2].i=SM_BBSW_PL_ENTRY tag (SM.h); lower.c emits SM_BB_SWITCH with
  "name/arity" key; sm_interp.c (Mode 2) handler resolves at runtime via pl_bb_once_proc_by_name →
  pl_bb_dcg → bb_exec_once (old SM_BB_ONCE_PROC logic folded into the one kept BB-dispatch opcode).
GATES: smoke_prolog 0/5→5/5 ✅; unified_broker 18→23; icon_all_rungs 189 (baseline, no regression);
  icon 5/5, snocone 5/5, rebus 4/4, raku 5/5, snobol4 13/13 — all green.
crosscheck_prolog 126/6: the 6 FAILs are all --run vs --interp (Mode 3 lags now-working Mode 2) —
  NOT a regression (both modes previously empty/agreed; Mode 2 advanced). → PJ-AGW-1c.
Files: src/include/SM.h, src/lower/lower.c, src/lower/lower_pl.c, src/lower/bb_exec.c,
  src/emitter/emit_sm.c, src/runtime/rt/rt.c, src/processor/sm_interp.c.
NEXT: PJ-AGW-1c (mirror SM_BBSW_PL_ENTRY into Mode 3 sm_jit_interp.c → crosscheck FAIL=0), then
  PJ-AGW-1d (full 4-attr lower_pl signature) → AGW-2/3 γ/ω-chain SEQ/CHOICE → EMITTER AGW-8..10.

=== prior watermark below ===
```
=== 2026-05-26 Opus 4.7 — PJ-DEL-ONCEPROC ✅ + audit + PJ-DEL-PUMP authored ===
one4all: 38e66809 — BUILD GREEN
.github: (this session)
PJ-DEL-ONCEPROC ✅ (38e66809): SM_BB_ONCE_PROC eradicated (10 sites, tombstone SM_UNUSED_6);
  rt_pl_once deleted (discharges PJ-RTP-4). It used a C function (pl_bb_dcg→bb_exec_once) to
  traverse a graph and never jumped into a flat x86 BB. Gates all unchanged (snobol4 13/13,
  icon/snocone/raku 5/5, rebus 4/4, crosscheck_prolog 132/0, Mode-4 broad 126/26).
AUDIT of all live SM_BB_*: three more are the same forbidden C-walker category →
  SM_BB_PUMP_PROC (icn_bb_dcg via bb_broker), SM_BB_PUMP_SM (bb_broker_drive_sm re-enters
  sm_interp_run), SM_BB_PUMP_CASE (sm_eval_subexpr). SM_BB_SWITCH is the ONE legit BB-dispatch
  opcode (node->fn(ζ,entry) jumps into emitted x86) — KEEP.
PJ-DEL-PUMP authored (PP-1..10) to dump the three PUMP opcodes; end-state = SM_BB_SWITCH sole
  BB-dispatch opcode. NOT STARTED — next session, full context budget. Icon honest-gate may
  drop (accepted; that path never jumped into x86).
NEXT: execute PJ-DEL-PUMP PP-1..10.

=== prior watermarks below ===
```
=== 2026-05-26 Opus 4.7 — SBL-PAT-PRIM + SBL-M4-OPDISPATCH + PJ-RT-PURGE step authored ===
one4all: 5a8bf79d — BUILD GREEN
.github: (this session) — SBL rows marked ✅; new ⛔ Step PJ-RT-PURGE authored
SBL-PAT-PRIM ✅ (4bd0ffb6): bb_bin_t reloc tables on ANY/NOTANY/SPAN/BREAK cset primitives.
  m2==m3 byte-identical with replacement. smoke_snobol4_jit --run 146→150.
SBL-M4-OPDISPATCH ✅ (5a8bf79d): per-statement vstack reset in Mode 4 rt_set_stno (to
  g_vframe_base, set by call_native_chunk). op_dispatch m4 result:122172 OK(3). Broad corpus
  126/26 (no regression). Root cause was missing st->sp=0 mirror, NOT comparison correctness.
Gates: smoke_snobol4 13/13, icon 5/5, snocone 5/5, rebus 4/4, raku 5/5. Mode-4 broad 126/26.
  smoke_prolog 0/5 + unified_broker 18/31 PRE-EXISTING on this branch (340b14b9 lineage).
PJ-RT-PURGE: NEW step authored to delete the 4-port-logic rt_pl_* helpers (rt_pl_once +
  rt_pl_unify_{var_atom,var_var,generic}) per INVARIANT 9 / RULES.md "NO C BYRD-BOX FUNCTIONS".
  Conversion helpers (rt_pl_arith / write_atom / write_var / atom_push / var_push) KEEP.
  Sub-steps PJ-RTP-1..4, one at a time. NOT YET STARTED.
OPEN: `. V` capture segfault (pre-existing, blocks 0XX_pat_* in Mode 3); TAB binary value bug;
  mixed_workload m4 empty output; PJ-RT-PURGE PJ-RTP-1..4.

=== prior watermarks below ===
```
=== 2026-05-26 Opus — SB-LINEAR Mode 3 (--run) SNOBOL4 — EMERGENCY HANDOFF ===
one4all: 537cb4ec — BUILD GREEN
.github: GOAL top block "SB-LINEAR FIRST" + HANDOFF-2026-05-26-OPUS-SBL-MODE3.md
Mode 3 --run SNOBOL4 smoke: 5/6 — output/concat/arith/goto_s/define PASS; pattern FAIL (Xabc want aXc)
Mode 2 --interp SNOBOL4 smoke: 7/7 (UNREGRESSED — all edits isolated to --run linear path)
Fixed: SBL-FN-RET (native ret on RETURN), SBL-FN-ARGS (bind call args to params), SBL-EXEC-PATD (pass pat_d)
OPEN: SBL-PAT-BLOB — bb_build_brokered/flat (emit_bb.c:611) mis-anchors simple literals; fix to match
      bb_exec_pat interpreter (bb_exec.c:2069). Then SBL-GATE (add --run to test_smoke_snobol4.sh), then Prolog.
Honesty: prior "Mode 3 complete" claims were false (define aborted, pattern wrong). Gate is now sole truth.

=== prior watermarks below ===
```
one4all: a02efe54 (PJ-9e partial)
corpus:  1fe096c
smoke_prolog: 5/5 ✅
crosscheck_prolog: 128/0 ✅
Other smokes: snobol4 7/7, icon 5/5, snocone 5/5, rebus 4/4, raku 5/5
honest gates: prolog 124/0/0, icon 277/0/0 (no regression)
broker: 20/49

one4all: 8837b2b1
smoke_prolog: 5/5 ✅
crosscheck_prolog: 128/0 ✅
Mode-4 hello ✅, simple_call ✅

PL-T-4..7 landed (8837b2b1):
- bb_pl_call.cpp / bb_pl_choice.cpp / bb_pl_alt.cpp / bb_pl_cut.cpp created
- rt_pl_call / rt_pl_choice_exec / rt_pl_alt_exec / rt_pl_cut added to rt.h/rt.c
- .include "bb_macros.s" removed; .intel_syntax noprefix emitted directly
- IR_* → BB_* rename complete: ir_exec.c→bb_exec.c, IR_LANG_*→BB_LANG_*,
  IR_exec_resume→bb_exec_resume, IR_node_state_t→bb_node_state_t, etc.
- RULES.md: two new rules (no template code in emit_core.c; no .include bb_macros.s)

OPEN for next session:
1. factorial Mode-4 segfault — BB_PL_CALL resume path: bb_exec_resume on
   color/1 graph after first success segfaults. Root cause: investigation needed
   (trail/env management in PlCallSt resume path in bb_exec.c BB_PL_SEQ pump).
2. PJ-10b step marker: PJ-10a/10b ✅ already in steps above.
```

---

## Step PJ-10 — Rename BB_PL_* → BB_* (promote opcode sharing)

**Rationale:** Language is mostly gone at the AST/SM/BB boundary. `BB_PL_` prefix is vestigial.
Promote clean names; keep `PL`-prefix compressed only where collision exists with Icon/Snocone ops.

**Collision analysis (four collide with Icon ops — distinct semantics, cannot merge):**

| Old | Conflict | New |
|---|---|---|
| BB_PL_VAR | BB_VAR (Icon variable ref) | **BB_PL_VAR** (kept — readable) |
| BB_PL_CALL | BB_CALL (Icon proc call w/ generators) | **BB_PL_CALL** (kept — readable) |
| BB_PL_SEQ | BB_SEQ (Icon sequence) | **BB_PL_SEQ** (kept — readable) |
| BB_PL_ALT | BB_ALT (Icon alternation generator) | **BB_PL_ALT** (kept — readable) |
| BB_PL_ARITH | — | **BB_ARITH** |
| BB_PL_ATOM | — | **BB_ATOM** |
| BB_PL_BUILTIN | — | **BB_BUILTIN** |
| BB_PL_CHOICE | — | **BB_CHOICE** |
| BB_PL_CUT | — | **BB_CUT** |
| BB_PL_UNIFY | — | **BB_UNIFY** |

**INVARIANT:** `.s` files are always emitted next to the original source (CWD == source dir).
`bb_macros.s` also lands in that same CWD. Run scripts must `cd` to source dir before
invoking scrip AND before invoking the assembler. Never use a temp dir as emit CWD.

**Steps:**

- [x] PJ-10a — sed-rename all `BB_PL_*`/`IR_PL_*` occurrences across `one4all/src/` per table above. Rename `IR_PL_VAR`→`IR_PLVAR` etc. to match. Build clean. Gates unchanged.
- [x] PJ-10b — rename BB_template files: `bb_pl_var.cpp`→`bb_plvar.cpp`, `bb_pl_builtin.cpp`→`bb_builtin.cpp`, etc. Update Makefile RT_PIC_SRCS and main SRCS. Build clean. Gates unchanged.

---

## Step PJ-12 — Free SM_sequence_t and BB_graph_t after emission in modes 3 and 4

**Rationale:** After the pipeline `parser → lower → (SM_sequence_t + BB_graph_t) → emitter`, the `SM_sequence_t` opcode array and every `BB_graph_t` wired into `bb_table[]` are pure build artifacts. In mode 2 (`--interp`) the SM stream is traversed at runtime so it must stay alive. In modes 3 and 4 (`--compile --target=x86` text or binary) the emitter has consumed all information it needs; the structures serve no further purpose. Keeping them alive after emission (a) wastes memory for large programs, and (b) — more importantly — means `BB_t*` pointers embedded in any RT object or `.data` slot are potentially dangling if the arena is ever relocated or freed before the OS reclaims the process. The clean fix is to free immediately after `emit_walk_codegen` (or `SM_codegen`) returns successfully.

**Scope:** `src/driver/scrip.c` modes 3 and 4 exit paths. The comments currently read `/* g_stage2 is global; no free */`; these will become `SM_seq_free` + per-entry `BB_free` calls.

**All gates (modes 2, 3, 4) must be run after every sub-step.**

**Sub-steps:**

- [x] PJ-12a — Add `stage2_free_sm_bb(stage2_t *s2)` in `scrip_sm.c`/`scrip_sm.h`: frees each `BB_graph_t*` in `bb_table[]`, then frees SM arrays (`instrs`, `stno_labels`, `bb_table`), zeroing all pointers and counts. Also adds `ast_tree_free()` inline to `src/include/ast.h` (recursive node+children free, sval not freed — may alias lexer buffers). Landed `d073acf9`.
- [x] PJ-12b — Wire in `scrip.c`: `ast_tree_free(ast_prog)` after every `sm_preamble` call (tree_t no longer needed once SM+BB are built); `stage2_free_sm_bb(s2)` after `sm_codegen_text` (text emit path) and after `sm_jit_run` completes (JIT path — SM instrs still needed during JIT execution via `CUR_INS`). `--interp` path unchanged (SM walked at runtime). Landed `d073acf9`. smoke_prolog 5/5 ✅ crosscheck_prolog 128/0 ✅ crosscheck_snobol4 4/0 ✅ crosscheck_icon 4/0 ✅.
- [x] PJ-12c — Verify with ASAN (`ASAN_OPTIONS=detect_use_after_free=1`) that no use-after-free fires after the SM+BB free. Zero UAF. Compiler-process leaks only (expected short-lived). ✅ 2026-05-25.

one4all: eff53b7e (PJ-13 + PJ-14)
.github: (this session)
PJ-13: lbl_back/succ/fail → lbl_β/γ/ω, 34 files 222 occurrences ✅
PJ-14: lbl_α/lbl_α_p added; every BB template TEXT arm emits α label first ✅
smoke_prolog: 5/5 ✅
crosscheck_prolog: 128/0 ✅
smoke_snobol4: 7/7 ✅
smoke_icon: 5/5 ✅
```

---

## FREE-3 / SM-BAKE steps — eliminate CUR_INS at runtime; free SM+BB after SM_codegen

**Goal:** After `SM_codegen` returns, `sm->instrs` and `bb_table[]` are freed immediately.
`sm_jit_run` executes purely from EXEC space — no `CUR_INS`, no `g_jit_prog->instrs`,
no `bb_table[]` dereference at runtime. Every operand is baked as an immediate in the blob.

**Architecture:** Each SM opcode that currently reads `CUR_INS->a[*]` in a C handler
gets a dedicated `emit_<opcode>_blob(operands..., trampoline_off)` function.
The blob pushes operands as imm64/imm32 into registers before calling the C runtime helper.
The C handler (`h_*`) is then dead and deleted. `emit_standard_blob` is called only for
zero-operand opcodes; all others get baked blobs.

**Free sequence (mode 3) after this work:**
```
sm_preamble(ast_prog)        → s2  (tree_t freed right after)
exec_stmt_pat_table_build()       (consumes SM+BB, produces pat_tbl — already done)
SM_codegen(sm, pat_tbl, ...)      (emits all blobs into EXEC space)
stage2_free_bb_after_emit(s2)     (BB freed — no runtime reference)
stage2_free_sm_bb(s2)             (SM freed — no runtime reference)
sm_jit_run(...)                   (executes purely from EXEC space)
```

### Step SB-1 — Bake SM_STNO: emit stno imm32 inline; delete h_stno CUR_INS read
Operand: `a[0].i` (stno number). Emit blob: inc pc, mov edi imm32, call rt_stno_hook, jmp trampoline.
Remove `emit_standard_blob_no_stack` call for SM_STNO; add `emit_stno_blob(stno, trampoline)`.
`h_stno` body inlined into blob; `h_stno`'s `CUR_INS->a[0].i` read eliminated.
Gate: smoke gates unchanged. SM_STNO no longer reads sm->instrs at runtime.

### Step SB-2 — Bake SM_PUSH_LIT_I / SM_PUSH_LIT_F / SM_PUSH_LIT_S / SM_PUSH_NULL
Operands: `a[0].i`, `a[0].f`, `a[0].s` respectively. Null has none.
Emit blobs: bake value as imm64 (int/float) or pointer (string) directly into PUSH sequence.
Delete `h_push_lit_i/f/s` CUR_INS reads. Gate: smoke gates unchanged.

### Step SB-3 — Bake SM_PUSH_VAR / SM_STORE_VAR / SM_LOAD_GLOCAL / SM_STORE_GLOCAL
Operands: `a[0].s` (name), `a[1].i` (kind/is_imm). Bake name pointer + kind as imm64/imm32.
Delete handler CUR_INS reads. Gate: smoke gates unchanged.

### Step SB-4 — Bake SM_INCR / SM_DECR
Operand: `a[0].i` (delta). Bake as imm32 mov before call to shared helper.
Delete `h_incr`/`h_decr` CUR_INS reads. Gate: smoke gates unchanged.

### Step SB-5 — Bake SM_CALL_FN / SM_CALL_EXPRESSION / SM_PUSH_EXPRESSION
Operands: `a[0].s` (fname), `a[1].i` (is_imm/nargs), `a[2].i` (nargs).
Bake all three as imm64/imm32. Delete handler CUR_INS reads. Gate: smoke gates unchanged.

### Step SB-6 — Bake SM_BB_ONCE_PROC / SM_BB_PUMP_PROC / SM_BB_PUMP_CASE / SM_BB_PUMP_SM / SM_BB_SWITCH
Operands: `a[0].s` (name), `a[1].i` (arity/ncases), `a[1].i` (has_default).
Bake name pointer + int operands. Delete handler CUR_INS reads. Gate: smoke gates unchanged.

### Step SB-7 — Bake SM_PAT_LIT / SM_PAT_REFNAME / SM_PAT_USERCALL / SM_PAT_CAPTURE_FN etc.
Operands: `a[0].s`, `a[1].i`, `a[2].s/i`. Bake all. Delete handler CUR_INS reads.
Gate: smoke gates unchanged.

### Step SB-8 — Bake SM_ADD/SUB/MUL/DIV/MOD/EXP/NEG (arith) — bake CUR_INS->op
Operand: opcode itself (`CUR_INS->op`) passed to `shared_arith`. Bake as imm32.
Delete `h_arith` CUR_INS read. Gate: smoke gates unchanged.

### Step SB-9 — Audit: grep CUR_INS in sm_jit_interp.c → zero hits. Assert g_jit_prog unused.
Remove `g_jit_prog` global and its assignment in `sm_jit_run`. Remove `CUR_INS` macro.
Confirm `sm_jit_run` signature no longer needs `SM_sequence_t *prog` for runtime use
(keep param for `g_blob_addrs` trampoline init if needed, else remove).
Gate: smoke gates unchanged. Build clean.

### Step SB-10 — Move free calls in scrip.c: both stage2_free_bb_after_emit + stage2_free_sm_bb
called immediately after SM_codegen returns, before sm_jit_run.
ASAN verify: zero use-after-free on all smoke gates.
Gate: smoke_prolog 5/5, smoke_snobol4 7/7, smoke_icon 5/5, crosscheck_prolog 128/0.

---

## SB-LINEAR watermark (this session)

```
one4all: 916d61a5
SB-LINEAR: sm_emit_linear + sm_run_linear landed.
- Linear emit: iterate SM instrs, emit call-rt_* blobs sequentially into SEG_CODE.
- Fall-through between instructions. Only SM_JUMP*/SM_HALT emit jmp/ret.
- Pass 2 relocates jump slots. Seals SEG_CODE. Calls sl_instr_addr[0].
- SM + BB freed immediately after sm_emit_linear, before sm_run_linear.
- All rt_* helpers written (arith, pat, return, exec_stmt, call_fn, suspend, etc.)
- label_blob_map populated during emit; rt_call_fn uses label_blob_lookup.
- BLOCKED: build broken by pre-existing G-1 bb_exec.c (BB_t->n/c[] removed).
- NEXT: fix G-1 bb_exec.c to unblock link; run smoke_snobol4 --run gate.
```

---

## SB-LINEAR next session plan

**Immediate blocker: G-1 bb_exec.c**
bb_exec.c references BB_t->n and BB_t->c[] which were removed in the GOLDEN BB RULE
commit (185cb274). These fields moved to BB_graph_t->n and BB_graph_t->all[].
Fix: update all `nd->n` → look up via graph, `nd->c[i]` → `graph->all[i]` or equivalent.
This unblocks the link step and allows smoke_snobol4 --run to run.

**After G-1 fix:**
1. Run smoke_snobol4 --run — expect PASS on output/concat/arith/goto/define/pattern.
2. Add --run variants to test_smoke_snobol4.sh gate (currently only --interp tested).
3. ASAN verify: zero use-after-free (SM+BB freed before sm_run_linear).
4. Remove g_jit_prog global entirely (now unused — label_blob_lookup replaces it).
5. Remove CUR_INS macro (now unused — all handlers read g_baked_* or are dead).
6. Delete dead h_* handlers that are no longer called from SM_codegen switch.
