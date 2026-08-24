# FINDING — src reorg carve list: adversarial verification (hq_C, s269)

**Brief:** ceo → hq_C `src-reorg-verify-and-layout`, s268. Correctness lens on the CEO deep scan
`survey-src-2026-08-23/` (index `711ce2f8`). Task (1) adversarially verify the carve list before
anything dies; (2) switch-collapse safety; (3) layout draft (→ `ARCH-SRC-LAYOUT-DRAFT-hq_C.md`).

**Tree:** `/home/claude_C/SCRIP` @ `f110760f`. `RT_OPT` default (`-O0`), no pristine rebuild (none of
the receipts below needs one; the two gate runs are static greps). Report `13-switches.md` was **not on
disk** when this ran — § G is an independent census, to be reconciled with it, not a substitute.

**Verdict key:** ✅ CONFIRMED · ⛔ REFUTED · ⚠ AMENDED (claim survives with a corrected number or scope).

---

## A. The 27 unbuilt sources — ⚠ AMENDED: **five of them are live**

Ground truth recomputed from the Makefile itself, not from the literal text of the list (a wrapper
makefile that `include`s it and echoes `$(RT_PIC_SRCS)`), diffed against `find src -name '*.c|*.cpp|*.S'`:

| | count |
|---|---|
| in `RT_PIC_SRCS` | 262 |
| on disk | 292 |
| on disk, not in build | **30** |
| in build, not on disk | **0** |

30 = the CEO's 27 carve candidates + `scrip.c` / `csnobol4_shim.c` / `sync_monitor.c` (other rules). Exact match on the census.

**Refutation channel 1 — `#include`d by a built file (unity build):** ZERO of the 30. No refutation there.

**Refutation channel 2 — compiled by a script:** five are alive and one script is a corpse.

| file | status | receipt |
|---|---|---|
| `src/driver/rs23_diag.c` | ⛔ **LIVE — not a carve candidate** | compiled at `scripts/build_scrip_rs23_diag.sh:35`; consumed by `test_rs23_diag_capture.sh`. Opt-in diagnostic build of `scrip`. |
| `src/runtime/rtx/rtx_unit_test.c` | ⛔ **LIVE** | `scripts/test_rtx_unit.sh:8` — built + run this session (binaries stamped 19:58) |
| `src/runtime/rtx/rtx_alloc_test.c` | ⛔ **LIVE** | same; ran `36 checks, 0 mismatches -> PASS` |
| `src/runtime/rtx/rtx_str_test.c` | ⛔ **LIVE** | same; ran `8426 cases, 0 mismatches` |
| `src/runtime/rtx/rtx_varval_test.c` | ⛔ **LIVE** | same; ran `20 cases, 0 mismatches` |
| `src/tools/emit_per_kind_audit.c` | ✅ carve stands | the only reference (`test_gate_icn_scan.sh:27`) is a **comment**. ⚠ `--audit-per-kind` in `scrip.c:791` is a separate live driver flag — check for duplicated logic before deleting. |
| `src/tools/test_template_byte_identity.c` | ✅ carve stands, **and its builder dies with it** | `build_and_run_test_template_byte_identity.sh` names five `$RT/x86/…` paths, **none of which exist**. Reproduced: `cc1: fatal error: …/src/runtime/x86/templates/sm_halt.c: No such file`, `FAIL: build failed (rc=1)`. The script has been dead for as long as those paths have. The live gate `test_gate_em_template_byte_identity.sh` does not use this .c — it drives `./scrip`. |

⭐ **Standing red found while proving liveness:** `rtx_unit_test` reports
`MISMATCH faildescr asm{v=104,slen=0,i=0} golden{v=104,slen=0,i=0}` → `RTX unit: 21 checks, 1 mismatches -> FAIL`,
and `test_rtx_unit.sh` exits 1 (`RTX UNIT: FAILURES`). An RTX asm-vs-C differential battery is failing
today. Not in the blocking set, so nobody sees it. Owner: hq_C, separate rung.

**Carve list after verification: 22 files** (27 − 5 live).

---

## B. Orphan headers — 4 ✅, 1 ⛔, 2 ⚠

Grepped `#include` across `src/` and `src/backends/`, plus `.l` / `.y` / `.S` / `scripts/` / `Makefile`
(so a regenerated parser cannot resurrect one).

| header | verdict |
|---|---|
| `src/templates/bb_common.h` | ✅ **orphan — the `⚠ RECONCILE` flag in 00-INDEX is resolved.** Zero includers anywhere. |
| `src/runtime/builtins/box_rt.h` | ✅ orphan, zero includers |
| `src/parser/prolog/pl_resolve.h` | ✅ orphan, zero includers |
| `src/parser/snobol4/unicode_alpha_ranges.h` | ✅ orphan, zero includers (661 lines) |
| `runtime_shim.h` | ⛔ **REFUTED — LIVE.** Included by `src/driver/driver_private.h:26` and `src/driver/scrip.c:35`. Report 12 has it dead. It is also at **`src/runtime/core/`**, not `runtime/rt/`. |
| `src/contracts/zeta_storage.h` | ⚠ "included by NOBODY" is false — `zeta_storage.c:3` includes it. The true claim: **no consumer** includes it; 12+ hand-extern instead. |
| `src/contracts/zeta_depth.h` | ⚠ same shape — `zeta_depth.c:1`. |

---

## C. Dead code inside live files

**`bb_match_arbno.cpp` — ✅ CONFIRMED, ⚠ number corrected.** 426 lines.
`static std::string bb_match_arbno_DELETED_ARMS()` at line 229 runs to EOF = **198 lines, zero callers**.
Also dead and not in the report: `static std::string bb_match_arbno_rbp()` (176–209, **34 lines, zero
callers**). Measured dead = **232 / 426 (54%)**, not ~306.

**`driver_call.c` g_exec_prog interpreter — ✅ CONFIRMED.** The only definition in the tree is
`driver_ast_stubs.c:4: const tree_t *g_exec_prog = NULL;`. `grep -rn 'g_exec_prog *=' src backends`
returns that line and nothing else — **no assignment exists**. The guard is `driver_call.c:139
if (body && g_exec_prog)`; every later use including `:369` is nested inside it (it reads `nch`, set at
`:143`). Dead span ≈ 139→380 of 400 lines.

**`xa_dispatch` — ✅ CONFIRMED and tightened.** The switch (`emit.cpp:356`) carries **23 case labels**,
four of which are already empty `return;` no-ops. `xa_dispatch` has exactly **three call sites**, each
with a literal op: `XA_STRTAB_RODATA` (`emit.cpp:425`), `XA_CSETTAB_RODATA` (`:475`),
`XA_FLAT_DATA_SECTION` (`:3184`). Second channel closed: every `xa_*` entry point was grepped
individually — each has exactly one definition plus one prototype in `xa_templates.h` and **no other
caller**; the internal `_str()` helpers (`xa_prologue_str`, `xa_epilogue_str`, `xa_entry_dispatch_str`,
`xa_wasm_main_open_str`, `xa_js_label_register_str`) are each called only by their own dead wrapper.
**20 of 23 arms unreachable.**
⚠ **`xa_flat.cpp` is half live:** `xa_flat_data_section` (line 139, LIVE) and `xa_entry_dispatch`
(line 138, dead) are adjacent in the same file. **Carve by function, not by file.**

**`emit_str.cpp` — ⚠ AMENDED.** There is **no `IS_JVM` / `IS_NET` guard in the file, or anywhere in
`src/emitter/`**. The dead half is a set of named builders, not a guarded region: all 7 `jvm_*_str` and
all 12 `net_*_str` have zero callers; `js_escape_string_str` has exactly one caller,
`xa_js_label_register.cpp:11`, which is itself a dead `xa_` arm → transitively dead. Live in that file:
`emit_fmt`, `u8`/`u32le`/`u64le`/`bytes`, `bomb_text`, and `gas_escape_str` (`emit.cpp:419`).

⭐ **`bomb_bytes` — ✅ CONFIRMED DEAD.** Defined `emit_str.cpp:46`, declared `emit.h:768`, **zero
callers**. This matters beyond the line count: CLAUDE.md and RULES.md name `bomb_bytes` *"the sole
legacy exception"* to the raw-byte-producer rule. **The exception is dead.** Carving it makes
TEMPLATE-ONLY EMISSION absolute, with no exception clause to maintain. Recommend Lon rule on the rule
text in the same motion.

**`unification.c` meta scaffold — ✅ CONFIRMED.** `typedef struct meta_fr` (215–220), `meta_root` (221),
and forward declarations `static int meta_solve(...)` / `static int meta_redo(...)` at 223/224 with **no
definition anywhere in the file and no external reference**. Pure scaffold.

**`pat_pool` — ⛔ REFUTED as "dead", and it is worse than dead: LIVE AND USELESS.**
`pat_pool_init()` is invoked two ways — `__attribute__((constructor)) pat_pool_ctor` at `pat_pool.c:32`,
which fires **on every load of `libscrip_rt.so`** (so: every `scrip` run *and* every emitted mode-4
binary), and again from `scrip.c:1043`. It mmaps 4 MB **`PROT_READ|PROT_WRITE|PROT_EXEC`** anonymous.
`pat_pool_emit()` and `pat_pool_reset()` have **zero callers anywhere** — nothing is ever written into
the pool. No `.S` file references the symbols. Carving removes a 4 MB RWX mapping from every process;
emitted `.s` is untouched (runtime-only), so **m3≡m4 is unaffected**.

**`resolution.c` jmp_buf CP stack — partial.** `#include <setjmp.h>` (18) and two `jmp_buf` locals
(97, 127) confirmed present; liveness not established this pass. **Remaining work, not cleared for carve.**

---

## D. The three landmines — plus a fourth

**Instrument:** every crosscheck program run in mode 3, stderr grepped for
`NO-IR-INTERP | BOMB eval_node | BOMB eval_ast_pat | sm_eval_subexpr | [SMX] FATAL`.
**Result: 326 programs swept, 0 hits.** None of these fires anywhere in the corpus today.
(m3 only; `timeout 10s`; `corpus/crosscheck` recursed, `corpus/programs/lon/` never touched.)

**1. `eval_node` / `eval_ast_pat` — ✅ live-caller confirmed, ⚠ which caller corrected.**
- `eval_ast_pat`'s only caller is `driver_call.c:204` — **inside the dead `g_exec_prog` block**. The stub
  is therefore unreachable. Report's "live callers" is wrong for this half.
- `eval_node` has two: `eval_expr` (`runtime_eval.c:307`) and the fall-through arm of `EXPVAL_fn`
  (`:448`). **`EXPVAL_fn` is live** (`pattern_match.c:415`). The fall-through is taken when a `DT_E`
  descriptor has `slen ∉ {1,2,3}`, and `compile_to_expression` (`pattern_match.c:547`) mints exactly
  that shape (`slen = 0`, `ptr = tree`), reachable from `core.c:1182`. **So the abort is reachable in
  principle.** Probed with three SNOBOL4 witnesses — deferred expression `E = *(X + 1)` + `EVAL(E)`
  across a rebinding of `X`; `LEN(*N)` inside a pattern match; `EVAL('2 + 3')` + `CODE()` — all three
  produce correct output (`6` / `11`, `aaa`, `5`) and none reaches `eval_node`.
  **Verdict: reachable-in-principle, unreached by every witness tried and by all 326 corpus programs.**

**2. `sm_eval_subexpr` — ⭐ NOT IN THE CEO LIST, same class, sharper.**
`rt.c:1920` defines it `__attribute__((weak))` as an abort stub, and **no strong definition exists**:
the emitter emits no such symbol (`src/emitter`, `src/templates`, `src/machine`, `src/driver` — zero
hits). Its callers are live: `invocation.c:52` inside `sm_call_proc` (real code — `nm` on the built
object shows `T sm_call_proc`, `T proc_table_call`), reached from `proc_table_call` ←
`by_name_dispatch.c:691` and `driver_hooks.c:57`; and `runtime_eval.c:434` (the `EXPVAL` `slen==1` arm).
**Any call with `entry_pc ≥ 0` aborts the process.** 0/326 corpus hits.

**3. `ir_call_proc` — ✅ CONFIRMED, guard shape pinned.** `rt_runtime.c:531-533` prints
`[NO-IR-INTERP]` and returns `FAILDESCR`. Five call sites in `by_name_dispatch.c` (689, 708, 736, 3614,
3759). **Every one is the else-arm of the same test:**
`if (pi >= g_stage2.proc_count || rt_proc_has_native_fn(name)) { …rt_call_proc_descr… } else { …ir_call_proc… }`
— i.e. taken exactly when a proc **is** in the stage2 table but has **no** native fn. Not silent (it
prints), but it returns `FAILDESCR` instead of calling. 0/326 corpus hits.

**4. `sm_call_proc` / `GenFrame` SM-residue — ✅ CONFIRMED residue.** `invocation.c` is 80 lines; both
functions have real linkage. `sm_call_proc` builds a `GenFrame`, then **walks `g_stage2.proc_table[].proc`
as a `tree_t` AST** (25–27, 33–49, 55–66) — AST walking at runtime, against the standing rule — and then
calls the always-aborting `sm_eval_subexpr`. **The whole file is an SM-era path that cannot complete.**

⚠ Method note for whoever carves `invocation.c`: its 200-char `/*----*/` separators read as unterminated
in any truncating view. Confirm with `nm` on the built `.o`, not by eye — I nearly filed it as
"entire file commented out" before checking (`nm` says otherwise).

---

## E. Not on the CEO list — found while verifying

- **`core.h:429-431` and `rt.h:229-231` declare functions after the final `#endif`** — ✅ confirmed at
  those exact lines (`indirect_goto`, two `extern int`; `rt_gvar_assign_concat_parts`,
  `rt_concat_parts_d`, `rt_nofail_abort`). Outside the include guard, re-emitted on every include.
- **`core.c:26` `#include "../../../scripts/monitor/monitor_wire.h"`** — ✅ `src/` reaches into
  `scripts/`. A hard constraint on any reorg: the build tree depends on the test tree.
- **`csnobol4_shim.c:11` `#include "/home/claude/csnobol4/data.h"`** — ✅ absolute path into the
  **retired** root. Breaks D-17 PORTABLE-HOME and cannot resolve from a slim root at all.
- **`NPUSH_fn` / `NINC_fn` / `NPOP_fn` (`core.c:2513/2519/2527`) each carry an unconditional
  `fprintf(stderr, "SEQ%04d …")`.** ⚠ AMENDMENT to report 12's *"hot N-stack path"*: `NPUSH_fn` has
  exactly one caller (`core.c:1225`) and **0 of 60 corpus programs emitted a single SEQ line**. The spew
  is **latent, not hot**. Still a shipped unconditional debug write on a runtime entry point.
- ⭐ **`src/backends/` contains ZERO C/C++/H files.** 40 files: 11 `.cs`, 7 `.java`, 6 `.il`, 4 `.wat`,
  4 `.js`, 4 `.j`, 1 `.mjs`, 1 `.md`, 1 `.jar`, 1 `.csproj`. Nothing of it is in `RT_PIC_SRCS`. Report 11's
  *"driver/net+jvm don't compile"* is true in a stronger sense — **there is nothing there for the C build
  to compile**. Moving the tree out of `src/` cannot affect the C build by construction.

---

## F. Gate honesty — the fossil paths

Recomputed: `scripts/` + `Makefile` name **121 distinct `src/…` file paths; 52 do not exist**, across 19
files (18 scripts + `scripts/monitor/monitor_wire.h`). Adversarial pass on the six `test_gate_*`:

| gate | verdict |
|---|---|
| `test_gate_rtcc_noclob_injection.sh:21` | ⛔ **census false positive** — it *writes* `"$TMP/src/runtime/rtx/rtx_inject_stub.S"`. Not a fossil. |
| `test_gate_lower_isolation.sh` (31,38,72) · `test_gate_runtime_isolation.sh` (31) | ⛔ comments / worked examples. Harmless. |
| `test_gate_stage2_isolation.sh` (67-69) | ⛔ **not a false-green.** The `interp_private.h:` rows are **allowlist** entries. A dead allowlist row makes the gate *stricter*, never weaker. |
| `test_gate_pl_no_new_global.sh` (34,35) | 2 fossils in a live `\`-continued file list. Prolog — SNOBOL4-FIRST do-not-run set; not evaluated further. |
| `test_gate_bb_one_box.sh` | ✅ **honest, and standing RED** — see below. |

⭐ **`test_gate_bb_one_box.sh` does not lie — it screams.** Its loop is
`[ -f "$f" ] || { echo "FAIL: expected … missing: $f"; fail=1; continue; }`, so a fossil path makes it
fail loudly. Ran it: **rc=1**, and the damage is far larger than the fossils — ten-plus *live* templates
report `0 extern "C" void bb_*` (`bb_call.cpp`, `bb_return.cpp`, `bb_binop_arith.cpp`,
`bb_binop_relop.cpp`, `bb_unop.cpp`, `bb_succeed.cpp`, …) because **the gate's regex no longer matches
how templates declare their entry point**, and `bb_call_proc_staged.cpp` reports 3 where 0 is expected.
This gate has drifted away from the code it guards. It is not in the blocking set, so it fails unseen.
**Repair it or retire it before the reorg** — "already red" is exactly how a real regression hides.

⚠ **Two of the 19 fossil-carrying scripts are the MANDATORY handoff regen scripts**
(`util_regen_benchmark_s_artifacts.sh`, `util_regen_feature_s_artifacts.sh`).

**Blocking-set baseline, measured this session** (static gates, no pristine needed):

| gate | rc | verdict |
|---|---|---|
| `test_gate_emit_no_lang.sh` | 0 | GREEN — *"no language-identity identifier in src/emitter or src/templates"* |
| `test_gate_template_medium_invisible.sh` | 0 | GREEN — 0 sites, ratchet ceiling 0 (`xa_flat.cpp(8)` informational only) |
| `test_corpus_snobol4.sh` | not run | needs pristine; out of scope for a scan+proposal brief |

---

## G. Switch collapse — safety proof

Independent census (report `13-switches.md` was absent). Reconcile, don't replace.

### G.1 ⭐ The four ZETA modes are **not compile-time branches at all**

`ZC_STORAGE` appears outside `zeta_choices.h` in exactly **four** places: `scrip.c:1309` and `:1493`
(bake a `rt_zeta_storage_set` call into the m4 preamble when the runtime value differs from the compiled
default) and `zeta_alloc.c:160/161` (the runtime setter/getter). Same shape for `ZC_PORT`
(`scrip.c:1310/1494`, `zeta_alloc.c:155/156`) and `ZC_ZETA` (`scrip.c:1308/1492`,
`xa_file_header.cpp:11`, `zeta_alloc.c:149`). **There is not one `#if ZC_STORAGE == …` in the tree.**

So *"delete the combinations, remove the guards"* on the storage axis is **not an `#ifdef` job**. It is:
delete the runtime selector (`g_zeta_storage` / `g_zeta_port` / `g_zeta_mode`, `rt_zeta_*_set/get`),
delete the CLI flags `--zeta-storage` / `--zeta-port` / `--zeta`, and delete the m4 preamble **bake**.
The bake is the only piece that changes emitted bytes — and it is **already a no-op whenever no flag is
passed** (`if (rt_zeta_storage_get() != (int)ZC_STORAGE)`), which is every compile any gate performs.

### G.2 Arms already dead by construction

`zeta_choices.h` `#error`s on `ZC_COL_GC`, `ZC_FRAME_DEAD5`, `ZC_PROMOTE_ON`. Selecting them fails the
build, so deleting them plus their guards **cannot change any byte**. Free.

### G.3 The population

| axis | count | receipt |
|---|---|---|
| compile-time `ZC_*` selectors | 21 | `src/contracts/zeta_choices.h`, 127 lines; every selector has ≤20 refs outside it, most ≤5 |
| runtime `getenv("…")` switches in `src/` | **351** distinct | |
| …named by any script or the Makefile | 56 | |
| …named by **nothing** outside `src/` | **295** | |
| …named by nothing at all — no script, no Makefile, **no `.github`** | **149** | pure archaeology |
| …read inside `src/templates` or `src/emitter` (**can steer emitted bytes**) | **194** | + 12 more in `src/driver` |

### G.4 What the gates actually exercise

⭐ **The three blocking gates set ZERO environment switches** — grepped all three for
`SCRIP_*` / `MONITOR_*`: empty. **No env switch is exercised by the blocking set**, so every env-switch
collapse is a no-op to the blocking set provided the default arm is preserved.

Only **five scripts in the whole tree** touch a zeta flag:

| script | arms | note |
|---|---|---|
| `test_gate_zeta_no_arena.sh:29` | `SCRIP_ZETA_TELEM=1 SCRIP_ZLS2_TRACE=1` | telemetry only |
| `test_gate_instr_budget.sh:48` | — | **comment only** |
| `test_bench_snobol4_timed.sh:85,89` | `SCRIP_ZETA_TELEM`, `SCRIP_HEAP_MB`, `SCRIP_NOHUGE` | bench, hq_P lane |
| `test_gc_stress_suite.sh:11` | `ZCFLAGS="-DZC_HEAP_MB=2"` | **in a usage comment**, not executed |
| `util_fc_spine_census.sh:15` | `SCRIP_ZETA_PORT=6` | **6 == `ZC_PORT_FORTH`, the compiled default → a no-op** |

### G.5 Classification of guard removals

**CLASS A — provably byte-identical, no before/after diff required:**
- **A1** the three `#error` arms (§ G.2) — unbuildable, therefore unreachable.
- **A2** any guard comparing two literal macros where the live arm is the compiled default and the
  alternate arm is not selectable by any script — every `ZC_*` except `ZC_LIT_GUTS` / `ZC_SPAN_GUTS`.
- **A3** removal of an env switch whose `getenv` is named by no script and no Makefile, with the default
  branch preserved — **295 of 351 qualify** on the naming test.

**CLASS B — requires a before/after byte diff (m3≡m4 law):**
- **B1** `ZC_LIT_GUTS` (20 refs / 4 files) and `ZC_SPAN_GUTS` (12 refs / 5 files). These are the *only*
  compile-time selectors that reach emitted code, and they are used as ordinary constant-folded C
  expressions (`ZC_LIT_GUTS == ZC_LIT_GUTS_CALL`), not `#if`. Collapsing to the compiled defaults
  (`UNROLL` / `INLINE`) is provably folded — but the diff here is cheap and decisive, so require it.
- **B2** removal of the m4 zeta preamble bake (`scrip.c:1308-1310`, `:1492-1494`,
  `xa_file_header.cpp:11`).
- **B3** any of the **194** env switches read inside `src/templates` or `src/emitter` (+12 in
  `src/driver`) — e.g. `SCRIP_ARBNO_NOFILL`, `SCRIP_ARBNO_FRAMELESS`, `SCRIP_ARBNO_ROOTSPINE`,
  `SCRIP_ARBNO_FPRPOP`, `SCRIP_ZLS_POISON` in `bb_match_arbno.cpp` alone. Each can steer emitted bytes.

**The diff protocol for Class B** (proposed, hq_C owns it): fix a witness set; for each program
`./scrip --compile -o w.s prog.sno` before and after, `md5sum` every `.s`, require identical; then the
same set through m3 and require the same verdicts. Any difference is a carve error, not a judgement call.

---

## H. Reconciliation with report `13-switches.md` (landed `8f858f72`, after § G was written)

Independent instruments, and they agree on the headline: **351 unique `getenv` env vars** — the same
number from two different censuses. Their "~292 never set by any script" and my "295 named by nothing
outside `src/`" are the same fact measured two ways; mine is the conservative bound, since *named* ⊇ *set*
(mine is whole-word `grep -w` over `scripts/` + `Makefile`).

**⛔ ONE DIRECT CONTRADICTION, and report 13 is wrong.** Its § 1 lists

> `RS23_DIAG` … whole `rs23_diag.c` `#ifdef`-wrapped, **unreferenced by Makefile** → **DELETE** (~87 ln)

and its § 6 puts that delete in **step 1, "zero-risk, grep-provable"**. It is not zero-risk: the file is
**unreferenced by the Makefile and compiled by a script** — `scripts/build_scrip_rs23_diag.sh:35`
(`-c "$SRC/driver/rs23_diag.c" -o "$OBJ/rs23_diag.o"`), consumed by `scripts/test_rs23_diag_capture.sh`.
Report 13 checked only the Makefile. **`RS23_DIAG` must come off the step-1 list** — with it, so does the
general inference that "Makefile-unreferenced ⇒ deletable": ✅ five of the 27 unbuilt files are live
exactly this way (§ A). The same caveat applies to its § 5 note that *"all of `src/tools/` is
unreferenced by the Makefile"* — true, and two of the five nevertheless have script builders (one of
which is itself broken, § A).

**Everything else of report 13's step 1 that I checked, ✅ holds:**

| claim | verdict |
|---|---|
| `g_platform` is always X86 | ✅ assigned at exactly three sites, all `BB_PLATFORM_X86`: `emit.cpp:25` (initialiser), `:195`, `:204`. Nothing else ever writes it. |
| `PLATFORM_X86` foldable at 193 sites | ✅ 193 total, 192 outside `emit.h` |
| `PLATFORM_{JVM,NET,JS,WASM}` have no call sites | ⚠ **AMENDED — they have eight, and all eight are already dead.** Every non-X86 use is in `xa_epilogue.cpp` (9,10,14,20) and `xa_prologue.cpp` (9,23,30,44) — ✅ both files are dead `xa_` arms (§ C: `xa_prologue`/`xa_epilogue` have zero callers; `XA_PROLOGUE`/`XA_EPILOGUE` are never dispatched). |
| `DYN_ENGINE_LINKED` and `IR_DEFINE_NAMES` have zero guard sites | ✅ **zero occurrences in all of `src/`.** The Makefile passes two `-D` flags that nothing reads (`Makefile:392,394,396`, `CRT`, `CXXRT`). Deleting them is inert. |
| exactly one `#if 0` in `src/` | ✅ `src/tools/tmatch_proto.c:27` |

⭐ **The two collapse jobs compose — sequence them.** Because the entire non-X86 `PLATFORM_*` family
lives *only* inside the two dead `xa_` files, doing the § C `xa_` carve **first** deletes the last
non-X86 consumer for free. After that carve, `PLATFORM_X86` is the only platform macro with any live
use and all 192 of its sites are `if (PLATFORM_X86)` → always true — which turns report 13's step 3
from "keep the X86 body, delete the other bodies across 145 files" into a pure guard strip.
**Recommended order: carve (§ A–C) → fossil paths (§ F) → report 13 step 1 minus `RS23_DIAG` →
step 2 → step 3 → the ζ complex.**

Two smaller reconciliations: report 13 lists `ZC_STORAGE_FRAME_R12` as CLI-erroring, which is right and
narrower than my § G.2 — `zeta_choices.h` `#error`s only on out-of-range, so `FRAME_R12` is
compile-legal and rejected by the driver, while `ZC_COL_GC` / `ZC_FRAME_DEAD5` / `ZC_PROMOTE_ON` are the
three genuine `#error` arms. And its `test_gate_instr_budget.sh:48` citation (cell-heap SIGSEGVs on
roman, frame-rsp aborts beauty) is the affirmative evidence my § G.4 lacked: the losing ζ arms are not
merely unexercised, they are **known broken** — which is why collapsing to the compiled default cannot
lose a working configuration.

## Routing

- Layout draft (deliverable 3): **`ARCH-SRC-LAYOUT-DRAFT-hq_C.md`**, same push.
- Open for hq/CEO arbitration: whether `bomb_bytes`' death retires the RULES.md exception clause; whether
  `test_gate_bb_one_box.sh` is repaired or retired; the `rtx_unit_test` faildescr red (hq_C rung).
- Not cleared for carve, needs another pass: `resolution.c` jmp_buf CP stack; the prolog dead-prototype
  families (report 06) — not reached this session.
