<!-- GOAL-SNOBOL4-BB · SCRIP native pattern-match ladder for modes 3/4 (--run/--compile) -->

# ▶▶▶ NEXT SESSION — START HERE (session 23, 2026-06-24)

**KEYWORD-CONCAT BOMB FIXED (SCRIP `c6d8c28`).** `X = &UCASE &LCASE` (and any concat with a `TT_KEYWORD` operand) no longer bombs `bb_gvar_assign_concat: no parts (not flattenable)`. Root cause: `sno_seq_flatten_ops` did not flag `TT_KEYWORD` as `nonleaf`, so keyword operands fell through the foldable-leaf path (which accepts only `TT_QLIT`) and dropped into the unimplemented `IR_SEQ` runtime-concat path with zero `op_parts`. Fix: one line — add `t->t == TT_KEYWORD` to the `nonleaf` trigger, routing keyword operands through the already-proven `sno_concat_chain` binary-chain path (`IR_BINOP_CONCAT`). Gate: crosscheck PASS=171 FAIL=84, fail set byte-identical to pristine HEAD (zero regressions). `wordcount.s` feature artifact updated (was bomb stub, now real codegen). 5 new demo `.s` committed (arithmetic/counter/hello/pattern_test/porter — previously never generated). Note: `wordcount` closes the codegen bomb but still **hangs** in its inner match-replace loop (`NEXTW LINE ? WPAT =`) because `WPAT = BREAK(WORD) SPAN(WORD)` with runtime-computed `WORD` cset hits the same deep pattern-engine gap as `word1`–`word4`/treebank/claws5 (crosscheck fail set, broader pattern-engine work). Benchmark timing confirmed across all 16 benchmarks: PASS=15/16 (eval_dynamic = documented OOM, correct at low N). Mode-4 native vs mode-3: arith_loop 113ms/862ms (7.6×), op_dispatch 233ms/2008ms (8.6×), table_access 3153ms/7088ms (2.2×).

**▶ NEXT MOVE: Lon decides — FZ-5b timing confirmation, GVA-4, OPSINGLE, or the computed-cset pattern-engine gap (word1–wordcount/treebank/claws5 family).**

**FZ-5b LANDED (SCRIP `6141434`).** Match sites referencing a once-assigned invariant pattern variable now bake the sealed matcher head directly (RIPSEAL lea) and skip the per-match `rt_defer_get_pat_fn` fetch — the hot-loop win for string_pattern/pattern_bt (500k× fetch eliminated). Three pieces: (1) FZ-5a: `fz_inlinable_head()` once-assigned-invariant analysis in `lower_snobol4.c` — conservative proof (assigns==1 AND frozen head recorded AND no indirect-assign/EVAL/CODE/CONVERT in program); behavior-neutral foundation. (2) FZ-5b: `flat_drive` IR_MATCH_DEFER case in `emit_bb.c` stages `child_cache_get`/`child_cache_get_lbl` when `fz_inlinable_head` hits; `bb_match_defer.cpp` branches on `bb_child_fn`/`bb_child_lbl` presence — inline path bakes frozen head, fetch path unchanged. Reuses RIPSEAL lea (both-medium clean). Cross-language safe (NULL for non-SNOBOL4). Gate MET: crosscheck PASS=171 FAIL=84 SKIP=6, fail set byte-identical to baseline (zero regressions). `.s` artifacts updated: string_pattern/pattern_bt/mixed_workload benchmarks now show inline marker + zero `rt_defer_get_pat_fn` calls. FZ-5b timing benchmark (wall-clock delta vs FZ-3 baseline) was NOT run — confirm that before treating speedup as quantified.

**FZ-4 (Option B) LANDED (SCRIP `6141434`).** Bare invariant captures (`PAT = BREAK(',') . W`) now freeze to `IR_REF_INVARIANT` — the general `sno_freeze_pat_graph_entry` path — retiring `bb_build_break_capture_blob`. Full deletion set: `bb_build_break_capture_blob`, `bb_build_break_cap_lit_blob`, `sno_break_cap_lit_graph`, `sno_freeze_break_cap_lit_bin`, `sno_freeze_break_cap_lit_text` (all removed from `bb_pat_build.cpp`). `bb_pattern_cat.cpp` / `bb_pattern_capture.cpp` reduced to passthrough-only (Raku keeps passthrough; SNOBOL4 pat_via_dtp builder arm removed). `emit_core.c` dead pat_via_dtp BREAK.VAR-LIT extraction collapsed to stub. Key correction vs goal-file premise: `bb_build_break_capture_blob` was NOT dead before this rung — bare buildable captures still routed through it; FZ-4 Option B REDIRECTED that path to freeze rather than simply deleting a dead function. Gate MET: crosscheck byte-identical, build clean.

**▶ NEXT MOVE: FZ-5b timing + GVA-4 or OPSINGLE — Lon decides.**


## ▶ PRIORITY RUNG (do FIRST): PERF-GVA — Global Variable Array

**GVA-0/1/2 LANDED (SCRIP `ef7594d`). GVA-3a/3b + str_concat_d fix LANDED (SCRIP `9222a33`). GVA-3a string-coercion fix LANDED (SCRIP `1d2c976`, rebased onto `fe2d39e`).**

Session 16 (2026-06-24): arith_loop ~870ms → ~141ms (~6×). Hot loop now branch-only: LT(N,1000000) emits cmp+jcc (GVA-3b), N=N+1 emits mov [rbx+k*16+8]+add (GVA-3a). Zero crosscheck regressions (87 fails, byte-identical set to pristine).

**CORRECTION (session 17, 2026-06-24): the session-16 line above originally claimed "Bench OK=14/16, FAIL=0" — that was WRONG. GVA-3a shipped a correctness regression: its inline-arith direct cell read `mov rax,[rbx+k*16+8]` takes the raw value field assuming DT_I, but for a DT_S/DT_R operand that field is a char*/double-bits, not an integer. So `T<IDX> = WORD + 0` (WORD a pattern capture) stored a pointer, and mixed_workload returned nondeterministic garbage instead of 550 — real state was OK=13 FAIL=1 CRASH=2. The pre-GVA path used rt_gvar_get_int (which coerces via strtoll); GVA-3a dropped that. Integer counters are always DT_I so arith_loop/fibonacci were unaffected, which is why it slipped through. The relop (GVA-3b) was already correct — it calls rt_gvar_get_int for named globals. FIX (`bb_binop_gvar_arith.cpp`, arms 2 both-names + 3 one-name): inline type-tag guard — `cmp edx,DT_I` on the cell type, fast raw read when DT_I (hot path stays call-free, branch predicts), else fall to rt_gvar_get_int slow path that coerces. arith_loop/fibonacci timings unchanged; bench now GENUINELY OK=14/16, FAIL=0, CRASH=2 (the 2 = pre-existing EVAL OOM eval_dynamic/eval_fixed, unchanged). Crosscheck still 87 fails byte-identical (zero regressions, verified before and after rebasing onto PB-NBODIES-32). All 16 benchmark + feature + demo .s artifacts regenerated side-by-side (idempotent on the combined tree).**

**EVAL OOM — DIAGNOSED (session 17, not fixed; deep + deferred).** eval_fixed (1M× `EVAL('X + 1')`) and eval_dynamic (1M× `EVAL('N + ' N)`) are the only two non-green benches (bench OK=14/16; these are CRASH, OOM-killed, NOT timeout — eval_fixed dies at ~3s). EVAL itself is CORRECT (small counts return the right value); the failure is a ~75KB/call memory leak (measured: 80MB@1k iters → 2.2GB@30k → OOM@150k, linear). Path: `EVAL_fn` (pattern_match.c) → `CONVE_fn` → `eval_build_chain` (runtime_eval.c) runs EVERY call: it re-parses the string, `lower_snobol4`s it, and `gvar_flat_chain_build` emits fresh machine code into the BB pool. The BB pool (`src/machine/bb_pool.c`) is a fixed mmap arena with a BUMP allocator (`bb_alloc` advances `pool_top`, never reclaims; `bb_pool_init` early-returns once `pool_base` set). So every EVAL bump-allocates new sealed (mprotect RX) code pages that are never freed; the per-call AST/IR (`ast_stmt_new`/`strdup`/lowered graph `g`) also leak. FIX OPTIONS for next session: (a) string→DT_E-chain CACHE — builds once, reuses; fixes eval_fixed fully (and makes it fast) but NOT eval_dynamic (1M distinct strings → cache grows + still bump-allocates per new string); (b) RECLAIM per run — snapshot `pool_top` before `eval_build_chain`, run the chain, restore `pool_top` (needs mprotect RX→RW back before reuse) + free AST/IR — fixes BOTH but is the deeper change (watch: chain must not be referenced after reset; GC interactions). Note the new cross-repo DIRECTIVE (`.github` `d26f002a`): BB-local collections use dynamic realloc-2x (cap-bumps retired) — a cache added here must follow that.

**str_concat_d correctness fix (SCRIP `9222a33`):** SPITBOL null-string-identity: `"" N` preserves N's type. Pristine returned STRING after `LT(N,5) N`; oracle expects INTEGER. GVA-3a removed the accidental `strtoll` mask that hid the bug. Fixed: `IS_NULL_fn` early-return in `str_concat_d`.

**▶ NEXT MOVE: PB-FZ** (constant-fold invariant patterns — see PRIORITY RUNG below). Then GVA-4 (indirect `$X` fast path via rbp-based GST hash index). Alternatively OPSINGLE or REC-COV — Lon decides.

---

## ▶ PRIORITY RUNG: PB-FZ — ALWAYS constant-fold invariant patterns (Lon pivot, 2026-06-24)

**PIVOT (Lon):** NO command-line switch between constant-folding and build-from-scratch. ALWAYS freeze every invariant pattern subtree at COMPILE time. `bb_pat_build.cpp` survives ONLY as the STITCH path for the case where an INVARIANT and a structurally-VARIANT pattern are combined. This promotes ARCH-SNOBOL4.md's "ALL-INVARIANT BLOB FREEZE" optimization to the ONLY path and deletes the baseline instance-wiring.

**VARIANCE TAXONOMY (the trigger is STRUCTURAL variance, not operand variance):**
- INVARIANT (→ FREEZE to one sealed `bb_box_fn` blob): literal-operand primitives (`POS(0)`, `SPAN('0-9')`, `LEN(3)`, `"abc"`), invariant combinators (SEQ/ALT/ARBNO/`.`/`$` of invariants), and `*E` (deferred-eval box has FIXED code → its graph is static; `ARBNO(*var)` is INVARIANT). **CORRECTION to ARCH-SNOBOL4.md: it lumps `*E` with the structural variants — wrong; `*E` is a fixed box doing a dynamic sub-call, so it FREEZES.**
- OPERAND-variant (→ FREEZE structure, box reads operand LATE from a slot; NO build, NO stitch): `POS(X)`, `SPAN(cvar)`, `LEN(N)`. `POS(0)` and `POS(X)` are the SAME `BB_MATCH_POS` unary matcher fed by different operand-source boxes (baked-immediate vs `[ζ+off]`/`[rbx+k·16]` load); the operand-source is polymorphic across same-arg-type matchers (one int-source feeds POS/RPOS/LEN/TAB/RTAB; one string-source feeds SPAN/BREAK/BREAKX/ANY/NOTANY). So `POS(START_LINE) SPAN(CHARS) RPOS(FINISH_LINE)` freezes WHOLE to one blob, late operand reads, ZERO runtime stitch. **GUARDRAIL:** late read is sound ONLY for IMMEDIATE matches (construct+match same statement); a STORED operand-variant pattern must SNAPSHOT operands into per-instance slots at construction (else post-construction mutation diverges from SPITBOL, which freezes operand values at the `P = …` assignment).
- STRUCTURAL-variant (→ the ONLY case needing `bb_pat_build` STITCH): a pattern-valued variable used as a sub-pattern (`var_pattern`, no `*`), `$NAME` indirect resolving to a pattern, a function call returning a pattern. These splice a runtime box-graph into the enclosing combinator.

**THE STITCH SET IS CLOSED** (SPITBOL pattern algebra — manual Ch.6 "Pattern operations" + ARBNO + immediate-assign). Exactly five combinators, so exactly these stitch boxes, and ONLY when an operand is structurally variant:
1. `STITCH_SEQ` — Subsequent (concatenation `P Q`), n-ary (assoc-flatten).
2. `STITCH_ALT` — Alternate (alternation `P | Q`), n-ary.
3. ARBNO-stitch — `ARBNO(P)` loop wrapper (variant body; `ARBNO(*P)` freezes).
4. CAPTURE-stitch `.` — conditional assignment `P . NAME` (capture-on-overall-success wrapper).
5. CAPTURE-stitch `$` — immediate assignment `P $ NAME` (capture-on-submatch wrapper).
Precedence (manual): `.`/`$` > blank(SEQ) > `|`(ALT) — fixes the stitch-tree shape. `@NAME`, `*E`, and all primitive functions are LEAVES, never combinators.

**BENCHMARK INVENTORY (verified this session — build clean, bench OK=15 FAIL=0 CRASH=1, only eval_dynamic = known throughput timeout). All three pattern benchmarks are FULLY INVARIANT → the STITCH boxes are NOT exercised by the bench corpus (they are for the wider crosscheck corpus). The bench is a pure FREEZE exercise, split immediate-vs-stored:**
- **roman** (immediate: `N RPOS(1) LEN(1).T =` and `'…' T BREAK(',').T`): ALREADY inline-frozen — emits `IR_MATCH_RPOS`/`LEN`/`CAPTURE` boxes inline; bare `T` is `IR_MATCH_DEFER` (dynamic fetch, correct). **DONE — no work.** Result-sensitive, passes .ref.
- **string_pattern** (stored: `PAT = BREAK(',').WORD ','`): built ONCE via per-shape fused runtime builder `bb_build_break_cap_lit_blob` (`src/runtime/rt/bb_pat_build.cpp:88`), matched 500k× via DEFER. Correct (result-sensitive, passes .ref). FZ replaces the fused builder with a frozen blob.
- **pattern_bt** (stored: `PAT = ('aaa'|'bbb'|'ccc'|'ddd') SPAN('abcd').W`): **stored ALT-pattern build is UNIMPLEMENTED in mode-4** — pattern literals are ABSENT from the `.s`, PAT is a no-op stub. "OK" is a FALSE PASS: result is the loop counter `N`, and a null PAT matches the null string every iteration → 500000 regardless. FZ IMPLEMENTS it. (Add a result-sensitive check — output `W` — so the freeze is actually validated.)

**SEAM (verified):** stored pattern `PAT = <invariant>` lowers (`src/lower/lower_snobol4.c`) to `IR_PATTERN_CAT` + `pat_via_dtp`; `src/emitter/BB_templates/bb_pattern_cat.cpp` emits a C-call to the per-shape `bb_build_break_cap_lit_blob`. Per-shape fused builders don't scale (no `alt4_span_cap` builder ⇒ pattern_bt stub). **`IR_REF_INVARIANT` is ALREADY a reserved opcode (`src/contracts/IR.h:174`, "REFINV" in `prove_lower.c`) but UNWIRED in the emitter — it exists for exactly this.** The immediate matchers (`bb_match_*()` dispatched in `src/emitter/emit_core.c`) ARE the frozen boxes to reuse. **FZ = redirect the existing immediate-matcher emission into a standalone sealed blob under a label + store its head as a `DT_P` via `IR_REF_INVARIANT`, replacing the `pat_via_dtp` build-call.** Match site keeps its DEFER fetch (FZ-2/3); inlining the sealed head to skip per-match DEFER is the FZ-5 perf step.

### STEPS
- [x] **FZ-2 — `IR_REF_INVARIANT` store + DEFER fetch.** ✅ LANDED (session 20, SCRIP `c3b6a83`). `PAT = BREAK(',') . W ','` lowers to a sealed matcher blob + `IR_REF_INVARIANT` storing the head as DT_P (no `bb_build_break_cap_lit_blob`). Gate MET: mode-3 AND mode-4 output == `string_pattern.ref`; builder call absent from `string_pattern.s`. See prior START-HERE header for the six pieces.
- [x] **FZ-3 — ALT-of-literals freeze.** ✅ LANDED (session 21, SCRIP `973df9e`). `PAT = ('aaa'|'bbb'|'ccc'|'ddd') SPAN('abcd').W` constant-folds to one sealed `IR_REF_INVARIANT` blob; pattern_bt mode-3 AND mode-4 output `result: 500000` + `W: ccccddddaaaa` (W hand-computed; oracle confirm pending token). Added `sno_freeze_pat_ir()` — general recursive kids-channel matcher-graph builder for invariant patterns — replacing the narrow FZ-2 per-shape constructor. Key insight: `flat_drive_cat/alt` read arms from the **kids channel** (`bb_match_kids_state_t`), not the γ/ω spine; must build in kids-channel form. `sno_has_pat()` guard prevents value-concat expressions (e.g. `42 ' items'`) from entering the freeze path. pattern_bt.sno+.ref updated (W output added). `string_pattern.s` byte-identical. Bench OK=15 FAIL=0 CRASH=1 (eval_dynamic OOM pre-existing). Crosscheck PASS=171 FAIL=84 vs pristine 168/87 — zero new failures, +3 fixed (132/133/134_pat_fence_eps_recur also freeze via the new general path).
- [x] **FZ-4 — retire dead fused builders.** Remove now-unused per-shape builders in `bb_pat_build.cpp` (keep ONLY the structural-variance STITCH path). Gate: `test_crosscheck_snobol4.sh` byte-identical (zero regressions).
- [ ] **FZ-5 (follow-on perf) — match-site direct reference.** When the compiler proves PAT holds a once-assigned invariant pattern (assigned, never reassigned), inline the sealed head at the match site and skip the per-match `rt_defer_get_pat_fn` (runs 500k× in string_pattern/pattern_bt) — the actual hot-loop win, turning stored into roman's inlined form.

**Prereq reads (PLAN.md step 7 — touches per-box state):** ARCH-SNOBOL4.md §"Native pattern architecture" + §"ALL-INVARIANT BLOB FREEZE", ARCH-x86.md §Boxes-are-stackless + §Flat-BB-ABI, `src/emitter/bb_regs.h`, `src/emitter/BB_templates/bb_pattern_cat.cpp`, `src/runtime/rt/bb_pat_build.cpp`, `src/emitter/emit_core.c` (matcher dispatch).

---

**Build:** `apt-get install -y libgc-dev && make && make libscrip_rt`. Oracle: `git clone …/x64 /home/claude/x64; sbl -b`. Tri-probe: `scrip --compile p.sno > p.s; gcc -no-pie -x assembler p.s -Lout -lscrip_rt -lgc -lm -Wl,-rpath,$PWD/out -o p.bin; ./p.bin` vs `sbl -b`. Bench/crosscheck gates: `scripts/test_bench_snobol4_modes.sh`, `scripts/test_crosscheck_snobol4.sh`.

---

## Prior context (session 13 — literal-subject native scan, now history)

roman's scan 2 (`'0,1I,…,9IX,' T BREAK(',') . T`) declined native because `flat_drive_scan_stmt` gated on a *named* subject only. Four-layer fix landed: `emit_bb.c` gate accepts `op_scan_subj_lit`; `flat_drive_scan_native` attaches an `IR_LIT_S` operand to `IR_SUBJECT`; `bb_subject.cpp` lit arm fixed (`mov→lea`, `bb_subj_litlbl()`, `rt_subject_load_lit`); `pattern_match.c` `rt_subject_load_lit` sets ζ-slot AND `Σ`/`Σlen`. Roman's earlier `MCXI` (recursive re-descent) symptom was resolved by the turn-1 local-var fix above. Roman reproduction:
```snobol4
    &TRIM = 1
    DEFINE('ROMAN(N)T')                   :(RE)
ROMAN N RPOS(1) LEN(1) . T =              :F(RETURN)
    '0,1I,2II,3III,4IV,5V,6VI,7VII,8VIII,9IX,' T BREAK(',') . T :F(FRETURN)
    ROMAN = REPLACE(ROMAN(N), 'IVXLCDM', 'XLCDM**') T :S(RETURN)F(FRETURN)
RE  R = ROMAN('176')
    OUTPUT = 'RESULT=' R
END
```

**Design note (carried):** the `walk_bb_node` preamble clobbering `op_a_sval` from `operands[0]` is the ambient-`g_emit` class flagged in session 12; the general cure (port-field reset / FILL-only / debug gen-counter assert) is still unbuilt.

---

# Open rungs (not yet started)

## PERF-GVA — Global Variable Array: eliminate GST hash lookup on hot path

### Naming

| Abbrev | Full name | What it is | Register | Access |
|--------|-----------|------------|----------|--------|
| **GST** | Global Symbol Table | Hash dictionary: name→DESCR_t. Runtime/dynamic. Currently called NV. | `rbp` (BBREG_HASH) | by name string |
| **GVA** | Global Variable Array | Flat `DESCR_t[N]` for compile-time-known globals. Static `.data`. | `rbx` (BBREG_BASE) | by integer index k |
| **LVA** | Local Variable Array | Per-call-frame `DESCR_t` slots for procedure locals/params. Already exists as ζ-frame. | `r12` (BBREG_ZETA) | by byte offset |

**The problem:** every global variable read is `call NV_GET_fn@PLT` (hash walk + string compare). Every write is `call rt_gvar_assign_*@PLT`. For `arith_loop` at 1M iterations that is ~14 PLT+hash calls per iteration. SPITBOL bakes variable addresses into code at compile time — zero calls per access.

**The fix:** at compile time, assign each program-global variable name an integer index k. Emit a flat `DESCR_t __gva[N]` array in the program's `.data` section. At preamble, call `gva_register(names, __gva, N)` which (a) populates `__gva[k]` = current GST value (null for new vars), (b) sets `GST_t.is_gva=1` and `GST_t.cell=&__gva[k]` so existing `NV_GET_fn`/`NV_SET_fn` paths transparently read/write through the GVA cell, (c) returns `__gva` base. Preamble stores that base in `rbx`. Templates then access `[rbx + k*16]` — two `mov` instructions, zero calls.

**GC safety:** `__gva` lives in `.data` (static storage, not GC heap). `DESCR_t.s` string payloads are still GC-managed heap pointers written into the cell — BDW scans `.data` as a root, so strings in GVA cells are reachable and not collected. The cell address itself never moves.

**GST forwarding invariant:** after `gva_register`, every GVA-backed variable in GST has `is_gva=1` and `cell→__gva[k]`. `NV_GET_fn` returns `*cell`; `NV_SET_fn` writes `*cell`. Dynamic paths (indirect refs `$X`, EVAL) that resolve to a GVA-backed name still work correctly at the cost of one extra pointer dereference — no correctness regression.

---

### GVA-0 — Infrastructure: GST forwarding flag + gva_register runtime  ✅ DONE (local, unpushed)

**GVA-0a — `GST_t` (rename from `NV_t`) gains `is_gva` + `cell`:**
In `src/runtime/core/core.c` (binary; edit via patch or sed):
```c
typedef struct _VarEntry {
    char              *name;
    DESCR_t            val;    /* live value when is_gva==0 */
    DESCR_t           *cell;   /* points into __gva when is_gva==1 */
    int                is_gva;
    struct _VarEntry  *next;
} GST_t;   /* was NV_t */
```
`NV_GET_fn`: `if (e->is_gva) return *e->cell;` before returning `e->val`.
`NV_SET_fn`: `if (e->is_gva) { *e->cell = val; return val; }` before writing `e->val`.
`NV_PTR_fn`: `if (e->is_gva) return e->cell;`
**Rename `NV_t` → `GST_t` throughout `core.c`.** Public API names `NV_GET_fn`/`NV_SET_fn`/`NV_PTR_fn`/`NV_CLEAR_fn` keep their names for now (rename is a separate rung, not required for correctness).

**GVA-0b — `gva_register` in `src/runtime/rt/rt.c` + `rt.h`:**
```c
/* Register N compile-time globals. Returns cells base (stored in rbx by preamble). */
DESCR_t *gva_register(const char **names, DESCR_t *cells, int n);
```
Implementation: for k in 0..n-1: find-or-create GST entry for `names[k]`; copy existing `e->val` into `cells[k]`; set `e->is_gva=1`, `e->cell=&cells[k]`.
**Exclude** names where `NV_PTR_fn` returns NULL (INPUT, OUTPUT, PUNCH, keyword `&`-prefix vars) — these stay GST-only, no GVA slot.

**GVA-0c — emitter: GVA name collection in `emit_bb.c`:**
New pass before any box emission: walk all IR nodes, collect distinct `op_sval` names for `IR_VAR`, `IR_ASSIGN`, `IR_BINOP_GVAR_ARITH`, `IR_BINOP_GVAR_ARITH_SLOT` that are non-keyword, non-`&`-prefix, non-INPUT/OUTPUT. Assign each a slot index k (stored in a new `int g_gva_slots[]` parallel to a `const char *g_gva_names[]` table, max 1024 entries). Store per-name GVA index in a lookup table `gva_index_of(name) → k` used by all templates.

**GVA-0d — emitter: emit `__gva` array + preamble call in `xa_flat.cpp` / `xa_prologue.cpp`:**
In TEXT mode, after `.section .data` banner:
```asm
  .align 16
__gva:
  .space N*16, 0
__gva_names:
  .quad .Lgvan0, .Lgvan1, ...   /* N name pointers */
  .section .rodata
.Lgvan0: .string "VARNAME0"
...
  .section .text
```
In preamble (before first user BB):
```asm
  lea rdi, [rip + __gva_names]
  lea rsi, [rip + __gva]
  mov edx, N
  call gva_register@PLT
  mov rbx, rax              /* rbx = __gva base for lifetime of program */
```
Also `push rbx` / `pop rbx` around any call that may clobber it per ABI — but since `rbx` is callee-saved in SysV ABI, callees preserve it automatically. No push/pop needed around `call` instructions in templates.

**GVA-0e — update `bb_regs.h` comment block** to document `rbx=GVA base` and `rbp=GST hash base` with new names.

**Gate GVA-0:** compile `arith_loop.sno` → verify `__gva` in `.s`; link and run → output identical to oracle; `gva_register` called once; `NV_GET_fn("N")` returns value through `e->cell`.

---

### GVA-1 — Direct load: IR_VAR global read → `[rbx + k*16]`  ✅ DONE (local, unpushed)

**Mandate:** In `bb_var.cpp` (and `bb_var_global.cpp` if separate), when `gva_index_of(_.op_sval) >= 0` (name has a GVA slot), replace `call NV_GET_fn` with inline load.

Add to `emit_globals.h` `sm_emit_t`:
```c
int op_gva_k;   /* GVA slot index for this node, -1 if GST-only */
```
Populated in `emit_bb.c` `walk_bb_node` preamble alongside existing `op_sval` fill.

Add to `x86_asm.h`:
```c
inline const char *GVAQ(int k, int hi) {
    static char b[8][40]; static int i; i=(i+1)&7;
    snprintf(b[i],40,"qword ptr [rbx + %d]", k*16+hi);
    return b[i];
}
```

`bb_var.cpp` new first arm (checked before existing `g_gvar_flat_chain` arm):
```cpp
(_.op_gva_k >= 0) ?
  x86("comment", "IR_VAR gva")
+ x86("label",   _.lbl_α)
+ x86("mov",     "rax", GVAQ(_.op_gva_k, 0))
+ x86("mov",     "rdx", GVAQ(_.op_gva_k, 8))
+ x86("mov",     FRQ(_.op_off),     "rax")
+ x86("mov",     FRQ(_.op_off + 8), "rdx")
+ x86("jmp",     "γ")
+ x86("def",     "β")
+ x86("jmp",     "ω") :
```

**Gate GVA-1:** `grep "call NV_GET_fn" arith_loop.s` == 0; full `test_crosscheck_snobol4.sh` oracle-identical.

---

### GVA-2 — Direct store: IR_ASSIGN global write → `[rbx + k*16]`  ✅ DONE (local, unpushed)

**Mandate:** Replace `call rt_gvar_assign_int` / `call rt_gvar_assign_descr` / `call rt_gvar_assign_var` / `call rt_gvar_assign_lit_i` / `call rt_gvar_assign_lit_s` with inline stores when the destination name has a GVA slot.

Integer literal store (`N = 5`), DT_I=6:
```asm
mov dword ptr [rbx + k*16],     6
mov dword ptr [rbx + k*16 + 4], 0
mov qword ptr [rbx + k*16 + 8], IMM
```

DESCR_t from frame slot (result already split lo=rax hi=rdx):
```asm
mov qword ptr [rbx + k*16],     rax
mov qword ptr [rbx + k*16 + 8], rdx
```

Steps:
- GVA-2a: `bb_gvar_assign.cpp` — integer and descr paths
- GVA-2b: `bb_gvar_assign_lit_i.cpp`, `bb_gvar_assign_lit_s.cpp`
- GVA-2c: `bb_gvar_assign_var.cpp` — var→var copy through GVA
- GVA-2d: `bb_gvar_assign_call.cpp`, `bb_gvar_assign_concat.cpp`

**Gate GVA-2:** `grep "call rt_gvar_assign" arith_loop.s` == 0; crosscheck suite green.

---

### GVA-3 — Fused integer arithmetic + relop  ✅ DONE (session 16, SCRIP `9222a33`)

**Mandate:** `N = N + 1` where both operands and destination are GVA-backed integer vars emits zero calls. Detect in `bb_binop_gvar_arith.cpp` when `op_parts` names all have GVA slots.

`N = N + 1` (add, immediate RHS):
```asm
mov rax, qword ptr [rbx + kN*16 + 8]   /* N.i */
add rax, 1
mov dword ptr [rbx + kN*16],     6      /* DT_I */
mov dword ptr [rbx + kN*16 + 4], 0
mov qword ptr [rbx + kN*16 + 8], rax
```

`LT(N, 1000000) N` (relop predicate, GVA int vs immediate):
```asm
mov rax, qword ptr [rbx + kN*16 + 8]
cmp rax, 1000000
jge β_port
/* success fall-through: value = N.i already in rax */
```

Steps:
- GVA-3a: `bb_binop_gvar_arith.cpp` fused path for GVA+GVA and GVA+IMM
- GVA-3b: new `bb_gvar_relop.cpp` for `LT`/`GT`/`LE`/`GE`/`EQ`/`NE` on GVA int operands — emits `cmp` + conditional jump, replaces `call rt_call_arr@PLT`

**Gate GVA-3:** `arith_loop.s` hot loop body (label `LOOP` to next label) contains zero `call` instructions; `fibonacci.s` same; timing run shows ≥5× improvement over baseline on `arith_loop`.

---

### GVA-4 — rbp GST hash path for runtime indirect refs (optimization, not correctness)

**Mandate:** `$X` where X's runtime string value names a GVA-backed variable: use `rbp`-based hash index to skip full GST walk.

New runtime helper `gva_lookup_by_name(const char *name) → int k` (returns -1 if not GVA-backed). Emitted in `.data` beside `__gva`:
```asm
__gst_idx:
  .space GVA_HASH_SIZE*4, 0xff   /* uint32_t[GVA_HASH_SIZE], sentinel=0xffffffff */
```
Preamble fills `__gst_idx` with (hash(name) → k) entries after `gva_register`.

Template for indirect read, fast path:
```asm
/* name string ptr in rdi */
call gva_hash_probe@PLT     /* (rbp, rdi) → k or -1 */
test eax, eax
js   .gst_slow
mov  rdx, qword ptr [rbx + rax*16 + 8]
mov  eax, dword ptr [rbx + rax*16]
jmp  γ
.gst_slow:
call NV_GET_fn@PLT
```

This is an optimization rung — correctness is guaranteed by GVA-0b's `is_gva` forwarding regardless of this rung. Do GVA-4 only after GVA-0 through GVA-3 are green and benchmarked.

**Gate GVA-4:** indirect-ref crosscheck programs (`014_assign_indirect_dollar`, `015_assign_indirect_var`) oracle-identical; `arith_loop` timing unchanged (no indirect refs in that benchmark).

---

### Expected performance impact

| Rung | Calls eliminated per `arith_loop` iteration | Estimated speedup |
|------|---------------------------------------------|-------------------|
| GVA-1 | 2 × `NV_GET_fn` | ~2× |
| GVA-2 | 2 × `rt_gvar_assign_*` | +1.5× |
| GVA-3 | `binop_apply` + both assign calls | closes to ~10× baseline |
| GVA-4 | partial `NV_GET_fn` for indirect | marginal on arith |

---

## OPSINGLE — delete operand_aux, one channel only

**Mandate:** exactly ONE operand channel: `nd->operands[]`. Delete `operand_aux` (`bb_operand_aux_set`/`bb_operand_aux_get`).

Writers still aux-only (add `ir_operand_push`, keep aux until readers flipped): `lower_snobol4.c` CALL args, `lower_icon.c:134,137,315`, `lower_raku.c:210`, `lower_pascal.c:147,162,177,340`, `lower_prolog.c:140`.

Readers to flip (`bb_operand_aux_get` → `nd->operands[]`): `BB_templates/bb_call.cpp:98`; `emit_bb.c:350,411,438,846,1072,1492,1818,2489,2957(DELETE bridge shim),3035,3240,3335,3398,3458`; `driver/scrip.c:102,245,1931`; `contracts/scrip_ir.c:355`.

Delete last (all readers flipped + all language gates green): `bb_operand_aux_set`, `bb_operand_aux_get`, struct fields, all call sites.

**Gate:** `grep operand_aux src/` (excl attic) == 0 AND all language gates green.

## REC-COV — community-recognized corpora

**Mandate:** extend coverage into community corpora. PB-GREEN stays session-first.

Inventory (pass-rates unmeasured — RC-0's job):
- `corpus/programs/gimpel/` — 145 `.sno` (no `.ref`)
- `corpus/programs/csnobol4-suite/` — 124 `.sno` WITH `.ref` ← start here
- `corpus/programs/snobol4/demo/` — 18 `.sno`

Steps: RC-0 honest runner + oracle-gen refs + triage table → RC-1 csnobol4-suite → RC-2 gimpel → RC-3 demo → RC-4 promote counts to hard floors → RC-5 re-ground "10×" claim.

---

## BBGC — slide-compaction garbage collector for the BB code arena  ⬇ LOW PRIORITY / EXPLORATORY (Lon 2026-06-24)

**Status: design-only spike. Do NOT start ahead of GVA-4 / OPSINGLE / REC-COV.** Picked up only when the `bb_pool` bump arena's lack of compaction becomes a real ceiling (the EVAL leak fix landed a LIFO watermark — `bb_pool_mark`/`bb_pool_release` — and a 2MB retention budget, which BOUNDS but does not COMPACT: cached/retained chains pin non-top regions, so pure-LIFO leaves holes a long-running EVAL/CODE-heavy program eventually exhausts).

**Vision (Lon):** treat `bb_pool` as a GC heap of *code*. When it fills, mark live BB blobs, sweep the unreferenced, and **slide the survivors down to compact**, re-stitching ONLY the four ports (α β γ ω) and touching nothing else inside a blob body.

**Why this is viable — relocatability taxonomy (grounded in `x86_asm.h` binary encoder + `bb_regs.h`, verified 2026-06-24).** Setting the 4 ports aside, here is everything baked into a sealed blob and its behavior under a slide:
1. **Register-relative state** (`[r12+off]` ζ, `rbx` GVA, `rbp` GST, `r13/r14/r15` Σ/δ/Δ, `r10` DATA) — encodes NO code/data address → **zero fixup**. This register-centric ABI is the whole reason compaction is tractable.
2. **RIP-relative to adjacent sealed RO** (`lea reg,[rip+disp32]` to interned name/lit bytes) — disp32 = target−rip_next → **invariant IFF the RO tail moves with its blob as one indivisible unit**. ⇒ relocation unit = blob + adjacent RO, never split.
3. **Immediate data constants** (`movabs reg,<int|float-bits>`) — values, not addresses → **position-independent**.
4. **Runtime-function calls** — binary encoder ALREADY emits `movabs rax,&fn ; call rax` (`x86_asm.h:196`, abs addr) NOT `call rel32`. The runtime never moves, so the absolute target is invariant under caller movement → **zero fixup**. (Ports, by contrast, are `0xE8 rel32` / `XK_PORT` — relative, the one thing that breaks.)
5. **The four ports** — `call/jmp rel32` between boxes → break on move → **re-stitch (recompute rel32)**. Exactly the scoped work; nothing else in the body needs it.
6. **⚠ THE REAL HAZARD — stored pointers to blob ENTRY points held OUTSIDE the pool.** A moving collector must fix these: (a) the EVAL cache (`runtime_eval.c` `g_eval_cache[].fn`); (b) DT_C/DT_E descriptors on the SNOBOL heap (`code()`/`CONVE_fn` stash `d.ptr=blob_addr` into first-class values a user var can hold — `:<C>` direct-goto, `CONVERT(s,'CODE')`, retained `*expr`); (c) the runtime label→code map; (d) **live return addresses on the native C stack** pointing INTO a blob if GC can fire while a BB frame is active (the precise-moving-GC-of-JIT-code problem).

**Two design decisions that make "touch nothing else" literally true:**
- **Entry-table handle indirection.** Hand out a stable handle (index into a per-pool entry-table the collector owns) instead of a raw blob-entry address; cache/descriptors/direct-gotos store the handle, the table holds the live address, relocation updates ONLY the table. Bounds category-6 fixups to one table.
- **Compact only at a safepoint with no active BB frame** (between top-level statements / after an EVAL/CODE returns — easy to guarantee since those run synchronously to completion and the pool is touched only between statements). Eliminates category-6(d) entirely, avoiding return-address rewriting.

### STEPS
- [ ] **BBGC-0 — measure + baseline.** Add `bb_pool` occupancy/hole stats; build an EVAL/CODE-heavy stress program that pins retained chains AND keeps allocating (forces holes the 2MB-budget LIFO can't reclaim). Confirm the failure mode (NULL from `bb_alloc` while total live < pool) and document why LIFO watermark alone is insufficient. NO behavior change.
- [ ] **BBGC-1 — root enumerator.** Enumerate all live BB entry-point references: `g_eval_cache`, DT_C/DT_E descriptors reachable from GST (BDW already roots the SNOBOL heap — walk code-typed cells), the runtime label→code map, direct-goto code values. Output a `(holder, entry_addr)` root list. Read-only; no relocation yet.
- [ ] **BBGC-2 — entry-table handle indirection.** Replace raw entry addresses handed to cache/descriptors/direct-goto with handles into a collector-owned per-pool entry-table; the table holds the current address. Floor: EVAL/CODE crosscheck byte-identical (one extra deref on the slow path only).
- [ ] **BBGC-3 — mark.** From roots, mark reachable blobs; follow inter-blob refs (ports + entry-table) transitively. Verify mark set ⊇ everything the stress program calls.
- [ ] **BBGC-4 — safepoint discipline.** Define + assert the compact safepoint (no active BB frame on the C stack). Confirm EVAL/CODE return BEFORE any compaction trigger. (Closes category-6(d).)
- [ ] **BBGC-5 — sweep + slide-compact.** Slide live blobs (blob + adjacent RO, one unit) down to remove holes; update the entry-table; re-stitch the 4 ports per moved box (recompute rel32). Add a verifier that asserts NO code-internal absolute pointer exists outside the covered categories (1/3/4 must need nothing). 
- [ ] **BBGC-6 — trigger.** On `bb_alloc` overflow, run compaction (at a safepoint) and retry instead of returning NULL.
- [ ] **BBGC-7 — gate.** EVAL-heavy stress (e.g. 1M distinct EVALs) runs with BOUNDED pool, output == SPITBOL oracle, compaction firing ≥N times; full `test_crosscheck_snobol4.sh` byte-identical (zero regressions); bench unaffected.

**Prereq reads when picked up (per PLAN.md step 7 — this touches per-box state + relocation):** `ARCH-x86.md` §Boxes-are-stackless + §Flat-BB-ABI, `ARCH-ICON.md` §register-contract, `REGISTER-LAYOUT.md`, `src/emitter/bb_regs.h`, `src/emitter/XA_templates/xa_flat.cpp`, `src/machine/bb_pool.c` (the new `bb_pool_mark`/`bb_pool_release`).

---

# Completed / superseded (summary only)

Sessions 1–12 built the full SNOBOL4-BB ladder bottom-up:
- **DDS-0** (session ~8): deleted all `bb_*_proto[]` byte arrays, `DTP_t` head, `rt_dtp_run`. Ground-zero rebuild.
- **TR-1** (`7d6a9c9`): `sno_leaf_buildable` extended for `TT_CAPT_COND_ASGN`; capture patterns routed to builder, not orphaned.
- **TR-LEN** (`75f97e5`): `bb_build_len_blob` allocates `IR_MATCH_LEN` (matcher), not `IR_PATTERN_LEN` (builder). `r1`→`W=CD`.
- **Rename** (`2e5a5a3`): `IR_PAT_*` → `IR_MATCH_*` throughout.
- **TR-BREAK** (`15bda9d`): `bb_pattern_break.cpp` + `bb_build_break_blob`. First ζ-slot box; proves frame mechanism end-to-end.
- **TR-CAPTURE** (`1e962ed`): `bb_build_break_capture_blob`; `PAT=BREAK(',') . W`→`W=alpha`.
- **TR-CAT** (`5d6e7cd`): `bb_build_break_cap_lit_blob`; `PAT=BREAK(',') . W ','`→`W=alpha`.
- **splice fix** (`9ea1251`): `bb_scan_splice_empty` stripped of stale port scaffolding; string_pattern + mixed_workload GREEN.
- **literal-subject scan** (`f3f7cdb`, session 13): gate + `IR_LIT_S` operand + `bb_subj_litlbl` + `rt_subject_load_lit`. Last bomb removed.

Architecture constants (do not re-derive):
- `walk_bb_node` preamble (emit_core.c:328–333) overwrites `op_sval`/`op_ival`/`op_a_sval`/etc. from node+operands every emission — never rely on ambient values set before `FILL`.
- `rt_cap_assign_cursor` reads global `Σ` (set by `rt_subject_load_nv` and now `rt_subject_load_lit`).
- `flat_drive_cat_arms` reads the kids channel (`IR_EXEC(cat).counter`), NOT `operands[]`; a CAT with `nkids==0` emits empty.
- `bb_build_flat` entry CAT with nkids==0 emits empty — kids channel is mandatory.

## ⛔ FACT RULE — "HANDOFF COMPLETE" REQUIRES A CONFIRMED PUSH (Lon directive, 2026-06-24)
**The phrase "handoff complete" — or any terminal claim of doneness ("done", "all set", "wrapped up", "committed and clean" presented as the end state) — MUST NOT be spoken until `git push` has SUCCEEDED and `git log origin/main --oneline -1` (step 7) shows THIS SESSION'S hash on origin for EVERY touched repo.** A local commit is NOT a handoff; the bytes are on this disposable sandbox and vanish with it. "Pending push awaiting credential", "ready to push", or "the local commits are safe" is an **INCOMPLETE handoff and must be reported as INCOMPLETE — never dressed up as complete.** If a credential is missing or the push fails, the handoff is **BLOCKED**: state that plainly, say exactly what is needed, and STOP — do NOT declare completion. The push (step 6) and the `origin/main` hash confirmation (step 7) are the LAST and MANDATORY acts of every handoff; skipping either means the handoff did not happen, regardless of how green the local tree is. Verify HEAD == origin/HEAD per repo, or it is not done.

**HOW THIS WAS MISSED (root cause, 2026-06-24 — so it is not repeated):**
1. **BLOCKED was reframed as COMPLETE.** The push failed for a missing credential; instead of reporting the handoff BLOCKED, the green *local* state was reported as done with the push demoted to a suggested user follow-up. The rule's real success criterion (the session's bytes living on `origin`) was silently swapped for a weaker proxy (bytes committed to a disposable sandbox). A locally-committed handoff is the same failure as an uncommitted one, one step later.
2. **A bad precedent was inherited.** Prior HANDOFF docs in this repo literally recorded "commits pending push awaiting user token" as a handoff outcome, normalizing the incomplete pattern; it was pattern-matched instead of challenged. "Pending push" is NOT an outcome — it is an unfinished, BLOCKED handoff.
3. **The completion claim was free-authored text.** Nothing forced the status line to be checked against ground truth, so under optimism it drifted from reality. Free-text status will always drift; it must be computed.

**PROTOCOL — THE STATUS LINE IS COMPUTED, NEVER TYPED (the mechanical gate):**
The assistant MUST NOT write the string "HANDOFF COMPLETE" (or any terminal doneness claim) as its own prose. The ONLY sanctioned source of that claim is the verbatim stdout of **`bash scripts/handoff_status.sh`**, which reads ground truth (working tree clean + local HEAD == `origin/<branch>` + zero unpushed) for every git repo it AUTO-DISCOVERS under the workspace (no hardcoded repo list — it enumerates every repo with an `origin` remote, so it cannot miss a touched one and reports the count it found) and prints `HANDOFF COMPLETE` (exit 0) or `HANDOFF BLOCKED` with the reason (exit 1). Handoff step 7 is now: **run `handoff_status.sh`, paste its output verbatim, and only treat the handoff as done if that output — not the assistant — says `HANDOFF COMPLETE`.** If it says BLOCKED, the handoff is BLOCKED: fix the listed reason (commit, then `git pull --rebase && git push`) and re-run. Reading `origin` needs no credential; only the push that PRECEDES the check does. The script blocks on its own uncommitted bytes, so it cannot be satisfied by a tree that still has the rule edit unpushed — closing the loop on itself.

**LIMITATION — DO NOT OVERSELL THIS GATE.** A markdown rule CANNOT coerce the assistant to run the script; this rule has the SAME enforcement gap as the rule it replaces (the assistant must still choose to honor it — exactly what failed on 2026-06-24). The script makes the truth cheap to obtain and hard to FAKE; it does not make the lie IMPOSSIBLE. Real coercion can only live OUTSIDE the model: (a) a harness/product layer that blocks any completion claim not backed by a fresh `handoff_status.sh` run (only the platform can add this), or (b) the human reviewer, who is the enforcer that actually works — **reject any "HANDOFF COMPLETE" not accompanied by the script's verbatim stdout with hashes matching `origin`, and treat a bare completion claim as FALSE by default.**


## ⛔ FACT RULE — THE WORD "HANDOFF" IS FORBIDDEN IN THE ASSISTANT'S OWN PROSE AT SESSION CLOSE (Lon directive, 2026-06-24)
When closing a session, the assistant MUST NOT type the word "HANDOFF" in any sentence it authors itself. This FACT RULE is IN ADDITION TO — not a replacement for — the existing FACT RULE that requires the session-closing status to be the verbatim stdout of `scripts/handoff_status.sh`. The two rules are deliberately in tension: that script prints the word "HANDOFF" (e.g. `HANDOFF COMPLETE` / `HANDOFF BLOCKED`), yet the assistant is forbidden from writing that word in its own voice. **Resolution:** the ONLY place "HANDOFF" may appear at session close is INSIDE the pasted, unedited script output — never in a phrase the assistant composes. Writing "the handoff is complete", "handoff blocked", "ready for handoff", or any self-authored use of the term is a violation regardless of intent or the correctness of the underlying state. To close a session: (a) paste the verbatim `handoff_status.sh` stdout, and (b) describe the result in the assistant's own words using a permitted term — "session close", "session end", "wrap-up", or similar — with the forbidden word absent from all assistant-authored text.
