# GOAL-HEADQUARTERS.md — one4all Maintenance HQ

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-ICON-BB-NATIVE ✅ `7efdf09a`

## Invariants

1. **No AST walking in modes 2/3/4.** `[NO-AST] FOO` → fresh SM/BB lowering, never restore AST walk.
2. **Zero C Byrd-box functions.** No `DESCR_t foo(void *zeta, int entry)`. Only permitted: `icn_bb_dcg`.
3. **Cross-language:** SM↔SM via `g_user_call_hook`; BB↔BB via universal α/β/γ/ω contract. Never cross language-A SM-bridge with language-B BB object.
4. **Four ports hard-wired.** `BB_node_alloc` bakes α=nd, β=nd, γ=NULL, ω=NULL.
5. **Single gate run at end of session.**
6. **Builder/consumer case rule.** UPPERCASE builds IR (`SM_*`, `BB_*`). lowercase consumes (`sm_*`, `bb_*`).
7. **EC-UNI matrix.** Backends are columns (X86/JVM/JS/NET/WASM). Text-vs-binary lives inside each `IS_<BE>` arm — never as a matrix dimension.
8. **Unified dispatch owns mode-setting.** Per-opcode iteration calls `emit_mode_set(TEXT_MODE(), out)` at entry.
9. **One file per Byrd Box in `BB_templates/`.** Each lives in its own `bb_<name>.c`. No consolidated multi-BB TUs.
10. **Grouped templates allowed (Lon directive, session #N+2).** Where N opcodes share emit shape, a single `sm_<group>()` / `bb_<group>()` template fn handles all of them — opcode communicated via `g_emit.instr->op` and dispatched by per-backend `switch(op)`. All emission code stays inside that one TU. **No external helpers, no cross-template calls.** Locality first; grouping reduces duplication only when it earns its keep via shared shape. Examples landed: `sm_arith` (5 opcodes), `sm_compare` (2), `sm_pat_nullary` (22). This SUPERSEDES the prior pure-duplication / one-fn-per-opcode reading of INLINE-ALL.

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh   # libgc-dev, bison, flex, nasm, wabt, libgmp-dev, m4 (idempotent)

cd /home/claude/one4all && make -j4 scrip > /tmp/build_full.log 2>&1
[ -x /home/claude/one4all/scrip ] || { grep -E "error:|fatal error" /tmp/build_full.log | head -5; exit 1; }

for r in /home/claude/one4all /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done

[ -d /home/claude/x64 ] || git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64

bash /home/claude/one4all/scripts/test_per_kind_diff.sh
# Expect: PASS=399 FAIL=0 STUB=660 NEW=0 GONE=0  (at one4all 44a5f9a5).
```

## Architecture

```
AST --(lower)--> SM_sequence_t  [SM_BB_XXX bridge opcodes]
                 BB_graph_t*    [pre-built per bridge op, single-structure via SM_sequence_t.bb_table]
```

Mode 2 (`--interp`) is the reference path for Icon at 194/265. Mode 4 (`--compile`) emits wired x86 — no `bb_broker`.

## Gates

### ALWAYS test in --run for emitter work

`--run` is the only mode that exercises the x86 emitter through the JIT path. `--interp` runs the SM dispatch interpreter and NEVER touches x86 emission. For work touching `emit_bb.c`, `emit_sm.c`, `BB_templates/`, `sm_*.c` templates, x86 lowering, or byte-emission primitives: test under `--run` (or `--compile` for byte-identity), not `--interp`.

Use for emitter work:
- `scripts/test_crosscheck_icon.sh` — three modes including `--run` (JIT).
- `scripts/test_smoke_snobol4_jit.sh` — three-mode parity, `--run` baseline 186.
- `scripts/test_gate_ec_uni_complete.sh` — beauty.sno `--compile` md5 + 9-gate roll-up.
- `scripts/test_gate_em_template_matrix.sh` — structural invariant.

⛔ **BEAUTY GATE SUSPENDED** (Lon directive, 2026-05-21 session #6): beauty.sno `--compile` md5 is NOT a binding gate during BB template consolidation. Every IS_X86 arm completion changes compiled output. Re-enable and re-stamp when ALL BB templates are complete across all backends. GATE-E still run for smoke/matrix sub-gates; beauty md5 mismatch is expected and non-blocking until consolidation closes.

### Cadence (per Lon, 2026-05-21)

Per-kind diff is the **primary per-slice invariant** (~5–10s, 1059 cells, byte-level filter+diff). Subsumes most of what matrix + beauty caught indirectly. Legacy gates are session-end / escalation only.

**Per-slice fast cycle:**
```
make -j4 scrip
bash scripts/test_per_kind_diff.sh
```

**Session-end:**
```
bash scripts/test_per_kind_diff.sh
bash scripts/test_gate_em_template_matrix.sh
# GATE-E sub-gates only: beauty md5 SUSPENDED — mismatch expected during consolidation
```

**Escalate mid-session ONLY when:** per-kind-diff reports FAIL/GONE; the slice touches LIVE PATH dispatchers (`emit_flat_ir`, `emit_walk_codegen`, `dispatch_one_x86`, WASM/JS/NET silo walkers); the slice changes `g_emit` shape; the slice deletes any `emit_bb_x*` / `emit_sm_*` fn.

### Gate commands

```
GATE-PK bash scripts/test_per_kind_diff.sh                # PRIMARY per-slice
GATE-M  bash scripts/test_gate_em_template_matrix.sh      # session-end
GATE-E  bash scripts/test_gate_ec_uni_complete.sh         # session-end
GATE-J  bash scripts/test_crosscheck_icon.sh              # escalation
GATE-S  bash scripts/test_smoke_snobol4_jit.sh            # escalation
```

Legacy --interp gates (interpreter work only):
```
bash scripts/test_smoke_icon.sh                  # PASS=5
bash scripts/test_smoke_unified_broker.sh        # PASS≥23
bash scripts/test_icon_all_rungs.sh              # PASS=194
```

### Re-freezing the per-kind baseline

When a change is INTENTIONAL (refactoring, new backend cell, fix to a known-wrong emission), per-kind diff will FAIL because the baseline is stale:
```
bash scripts/freeze_per_kind_baseline.sh
bash scripts/test_per_kind_diff.sh                # confirm PASS=N FAIL=0 NEW=0 GONE=0
```
Commit `baselines/per_kind/` with the source change. The diff IS the regression-test record of what intentionally moved.

## Watermark

```
one4all: 8aa204c2  (EC-UNI-INLINE-GROUP slice 18: sm_incr+sm_decr -> sm_incr_decr().
                     Vestigial 2-opcode group (emitted only by sm_interp_test.c).
                     3 files changed, 37 insertions / 39 deletions (net -2 LOC).
                     Per-backend switch on macro/rt_fn (X86) and arith index (WASM).
                     GATE-PK PASS=420 FAIL=0 STUB=639.)
one4all: 18bd48c9  (EC-UNI-INLINE-GROUP slice 17: 7 misc-nullary opcodes
                     -> sm_misc_nullary(). SM_CONCAT/NEG/COERCE_NUM/EXP +
                     SM_PUSH_NULL/PUSH_NULL_NOFLIP/VOID_POP. 5 files changed,
                     97 insertions / 138 deletions (net -41 LOC). Irregularities
                     preserved verbatim: VOID_POP uses emitter_init_text (use_init_text
                     flag); PUSH_NULL_NOFLIP collapses to push_null on JVM/JS/NET/WASM;
                     NEG uses NET 'negate'; EXP uses 'exp_op' on JVM/JS/NET/WASM.
                     sm_arith.c now hosts 2 grouped fns (sm_arith + sm_misc_nullary,
                     12 opcodes). GATE-PK PASS=420 FAIL=0 STUB=639.)
one4all: 87d485d3  (EC-UNI-INLINE-GROUP slice 16: sm_jump+sm_jump_s+sm_jump_f
                     -> sm_jump_group(). 4 files changed, 122 insertions /
                     69 deletions (net +53 LOC, dominated by ~35-line group
                     header comment; body roughly equivalent). int return-value
                     contract preserved (1 = terminal jump, 0 = walker emits
                     next-pc). Per-backend switch on jump shape:
                     IS_JVM ifeq vs ifne, IS_NET brfalse vs brtrue,
                     IS_WASM last_ok vs eqz(last_ok). At 3 opcodes with cleanly
                     varying tokens, grouping pays off in locality consolidation
                     rather than LOC reduction. GATE-PK PASS=420 FAIL=0 STUB=639.)
one4all: 6a806546  (EC-UNI-INLINE-GROUP slice 15: 22 simple-nullary pat
                     opcodes -> sm_pat_nullary(). 9 files changed, 537
                     deletions vs 233 insertions (net -304 LOC). Largest
                     grouping yet; demonstrates that grouped templates
                     reduce LOC without breaking locality.)
one4all: 2ad1896d  (EC-UNI-INLINE-GROUP slice 14: sm_acomp+sm_lcomp -> sm_compare().)
one4all: 710b2fd5  (EC-UNI-INLINE-GROUP slice 13: sm_add/sub/mul/div/mod
                     -> sm_arith(). FIRST grouped template — Lon directive
                     this session: ONE template per opcode-group, opcode
                     dispatched via g_emit.instr->op in per-backend switch.
                     Replaces pure one-fn-per-opcode INLINE-ALL reading.
                     5 files changed, 92 insertions / 102 deletions.)
one4all: 16e0515f  (INLINE-1 slice 12: sm_push_lit_f + sm_push_expr.)
one4all: 39f67bc3  (INLINE-2 slice 11: sm_add/sub/mul/div/mod first table
                     elimination — g_sm_arith table_lookup folded into
                     literal macro strings. Pre-grouping; later merged
                     into sm_arith() at slice 13.)
one4all: 2021de8e  (INLINE-1 slice 10: sm_incr + sm_decr.)
one4all: 39b9f0f6  (INLINE-1 slice 9: sm_acomp + sm_lcomp (with IS_TEXT fork
                     preserved); pre-grouping, merged at slice 14.)
one4all: 74ba8f11  (INLINE-1 slice 8: sm_label.)
one4all: 8097af13  (INLINE-1 slice 7: sm_push_null + push_null_noflip + void_pop.)
one4all: 877dd549  (INLINE-1 slice 6: sm_concat + neg + coerce_num + exp.)
one4all: af013804  (INLINE-1 slice 5: sm_pat_cat + sm_pat_alt; pre-grouping,
                     merged into sm_pat_nullary at slice 15.)
one4all: eb6c2e62  (INLINE-1 slice 4: sm_pat_{fence0,fence1,abort,fail,
                     succeed,arbno}; pre-grouping, merged at slice 15.)
one4all: b28f0577  (INLINE-1 slice 3: sm_pat_{len,pos,rpos,tab,rtab,rem,
                     bal,eps}; pre-grouping, merged at slice 15.)
one4all: 2bd3f069  (INLINE-1 slice 2: sm_pat_{any,any_i,notany,span,break,
                     deref}; pre-grouping, merged at slice 15.)
one4all: 43923af9  (INLINE-1 slice 1: sm_pat_arb FIRST inline-from-dispatcher.
                     Header promotions: emit_sm_consume_pc_label + TEXT_MODE()
                     macro to emit_sm.h.)
one4all: 794b9435  (PPV-9: IS_WASM arms for bb_any/arbno/break/len/lit/notany/
                     pos/span/tab. Each emits (call $bb_<kind>_new). Baselines
                     re-frozen. GATE-PK PASS=420 FAIL=0 STUB=639.)
one4all: 0ef0f7fc  (EC-UNI-NAMEKEY-BIN: IS_BIN arms for 14 live BB kinds.
                     lbl_succ/fail/back_p added to g_emit; templates
                     use them for binary patch-back. Audit fix: static
                     audit labels in binary cells. GATE-PK 411/0.
                     --run PASS=186. emit_bb_x* callers gone from switch.)
one4all: 1b83cb1f  (EC-UNI-REWIRE complete: all 14 live simple BB kinds
                     route through emit_bb_node (IS_TEXT). ARBNO/CAP_IMM/
                     CAP_COND slow-path wired. flat_fill_and_call +
                     flat_fill_charset helpers. GATE-PK 411/0, GATE-M
                     855/855, GATE-E 8/9 (beauty suspended).)
one4all: fcb86d2e  (EC-UNI-REWIRE slice 1: REM/ARB/ABORT/LEN/POS/TAB/LIT/SPAN/ANY/BREAK/NOTANY.
                     GATE-PK 411/0.)
                     Each emits (call $bb_<kind>_new). Baselines re-frozen.
                     GATE-PK PASS=411 FAIL=0 STUB=648. Beauty gate suspended.)
one4all: ddd08f01  (PPV-8 prev: bb_abort IS_X86 arm added; dead IS_BIN guards
                     removed from bb_rem/bb_arb/bb_fence; WASM comments
                     normalized to "deferred". GATE-PK PASS=401 FAIL=0
                     STUB=658. Beauty gate suspended per Lon directive.)
one4all: f6e4968a  (PPV-7: fix RPOS/RTAB --compile segfault. emit_flat_invariant
                     + pre_build_children_text + pre_build_children all walked
                     nd->c[i] for i<nd->n without guarding nd->c==NULL.
                     pat_node_intarg sets nd->n=1 as reverse-flag, not child
                     count. Guard: if (!nd->c) return. All gates unchanged.)
one4all: 1c47a59a   (PPV-2: lower-time SM_PAT_* substitution for protected names
                     in lower_pat_expr TT_VAR arm.  Also: normalize_per_kind_cell.py
                     normalizer hole fixed (lookahead in sid_nid regex); baseline
                     re-frozen PASS=399.  Beauty md5 → 6bf2e9daa777f54f04c8f7160da435d1
                     (882524 bytes).  PPV-3/4/5/6 verified and closed.
                     GATE-PK PASS=399 FAIL=0; GATE-M 855/855; GATE-E 9/9;
                     --run smoke 186 unchanged.)
one4all: 44a5f9a5   (PPV-1: protect REM/ARB/FENCE/FAIL/SUCCEED/ABORT/BAL.
                     ERROR 042 on user-reassign, matching SPITBOL.  Closes
                     HQ-BUG-PROTECTED-PATTERN-VARS.  Guard at NV_SET_fn
                     chokepoint with init-phase flag g_protected_pat_vars_armed.
                     New helper module src/runtime/rt/rt_protected.{h,c}.
                     Discovery: --interp h_store_var calls NV_SET_fn
                     directly, bypassing rt_nv_set — NV_SET_fn is the
                     only universal chokepoint.  PK PASS=399 unchanged;
                     SNOBOL4 smoke --run 186 unchanged.)
.github: afa893a0   (PPV-0 inventory.  Deliverable: PPV-0-INVENTORY.md.
                     7 pat-name enums confirmed.  Substitution site
                     lower.c:373; protection site NV_SET_fn:2462.)
one4all: 9b905d26   (EC-UNI-PER-KIND-DIFF harness.  5 backends × submode:
                     x86/{text,binary,text_macro}+jvm+net+js+wasm text.
                     1059 cells.  Baseline PASS=399 STUB=660 FAIL=0.
                     baselines/per_kind/ 3.4 MB committed.  Regression
                     detection verified empirically.)
corpus:  5fc1427    (demo/beauty/ canonical; beauty_suite/ apparatus separated)

smoke icon: 5/0    smoke prolog: 5/0   smoke rebus: 4/0
smoke raku: 5/0    smoke snobol4: 7/0  smoke snocone: 5/0
broker: 23/26      icon rungs: 194/36/35
matrix gate: 855/855 PASS
beauty.sno --compile md5:           SUSPENDED per Lon directive (consolidation)
beauty.sno --compile assembled .o:  SUSPENDED per Lon directive (consolidation)
EC-UNI-21 9/9 PASS.  M1 oracle DRIFTED (9cddff25, 622 lines vs M1 abfd19a7, 646 lines).
beauty.sno in corpus: programs/snobol4/demo/beauty/beauty.sno (627 lines,
  md5 5be1de188af42be42e15e6d9a552f759, self-contained).

Grouped templates landed (slices 13-18):
  sm_arith         5 opcodes  SM_ADD/SUB/MUL/DIV/MOD                        (slice 13)
  sm_compare       2 opcodes  SM_ACOMP/SM_LCOMP                             (slice 14)
  sm_pat_nullary  22 opcodes  SM_PAT_{ARB,ARBNO,REM,FENCE0,FENCE1,FAIL,SUCCEED,
                              ABORT,BAL,EPS,DEREF,ANY,NOTANY,SPAN,BREAK,LEN,
                              POS,RPOS,TAB,RTAB,CAT,ALT}                    (slice 15)
  sm_jump_group    3 opcodes  SM_JUMP/JUMP_S/JUMP_F                         (slice 16)
  sm_misc_nullary  7 opcodes  SM_CONCAT/NEG/COERCE_NUM/EXP/
                              PUSH_NULL/PUSH_NULL_NOFLIP/VOID_POP           (slice 17)
  sm_incr_decr     2 opcodes  SM_INCR/SM_DECR                               (slice 18)
  (41 opcodes in 6 grouped fns; previously 41 separate fns plus dispatcher trail.)

Pending-INLINE-4a-inline (current dispatchers in emit_sm.c go through emit_sm_<op>_dispatch -> emit_sm_lblopt -> sm_template_lookup -> renderer; need inlining into each template's IS_X86 arm using bb3c_format + sprintf-on-globals — NOT header promotion; renderer machinery to be DELETED, not exposed):
  sm_pat_string_arg group: SM_PAT_LIT, REFNAME, USERCALL                   (LBLOPT shape)
  sm_pat_capture   group: SM_PAT_CAPTURE                                   (LBLOPT_INT32 shape)
                          SM_PAT_CAPTURE_FN, CAPTURE_FN_ARGS               (LBLOPT3 / LBLOPT_I_I shapes)
                          SM_PAT_USERCALL_ARGS                             (LBLOPT_INT32 shape)
  sm_exec_stmt     standalone                                              (EXEC_VAR shape)
  sm_push_lit_s    (sm_push_pop_lits.c)                                    (LBL_INT32 shape)
  sm_push_var / sm_store_var                                               (LBL shape)
  sm_define / sm_define_entry                                              (NOOP shape)
  sm_call_fn / sm_suspend_value                                            (LBL_INT32 + RET shape)
  sm_bb_once_proc / sm_bb_pump_proc                                        (LBL_INT32 shape)
  sm_push_expression / sm_call_expression                                  (PCREF shapes)
```

---

## Active rungs

### EC-UNI — unify all walkers; one fn per opcode/kind, one arm per backend

**Target:** one fn per SM opcode, one fn per BB kind, each with five `if (IS_<BE>)` arms (X86/JVM/JS/NET/WASM). Text-vs-binary hides inside each arm. After completion, `emit_walk_codegen` / `emit_jvm_from_sm` / `emit_js_from_sm` / `emit_net_from_sm` / `emit_wasm_from_sm` / `dispatch_one_x86` all delete.

**Three layers:**
- **Layer 1** — `SM_templates/sm_<op>.c` / `BB_templates/bb_<kind>.c`. `void sm_<op>(void)` / `void bb_<kind>(void)`. Reads `g_emit.*`. Branches ONLY on `IS_<BE>`. **Per Lon 2026-05-21 session #9 (EC-UNI-INLINE-ALL): the body of each backend arm is the literal sequence of Layer-3 calls — no shims, no table-drivers, no `emit_sm_<op>_dispatch` indirection. One template C function per opcode/kind; all code emission explicit and inline. Cost — additional LOC and apparent duplication — is accepted as the price of locality.**
- **Layer 2** — **REVERSED 2026-05-21 session #9 by EC-UNI-INLINE-ALL.** Previously: deferred (Lon, 2026-05-20) — no static helpers in templates, no cross-template factoring. Now stronger: the existing dispatch-shim layer (`emit_sm_<op>_dispatch`, `emit_sm_op` table-driver, `emit_bb_x*` helpers) is **scheduled for deletion** under EC-UNI-INLINE-ALL. Templates call Layer 3 directly.
- **Layer 3** — `src/emitter/emit_io.{c,h}`: `emit_text` / `emit_textf` / `emit_byte` / `emit_bytes`. Funnel for all output. Plus truly-shared instruction primitives in `emit_core.c` (`insn_*`, `bb_insn_*`) — these are not Layer 2, they are x86 instruction encoders called once per emitted instruction, the irreducible bottom.

`g_emit` (`emit_globals.{c,h}`) carries all per-template state. Not re-entrant. Maps 1:1 to flat `DATA('Sm_emit(...)')` in Snocone bootstrap.

---

### ⚡ EC-UNI LIFT PATTERN

**Lon directive (2026-05-21 session #N+2): GROUPED TEMPLATES — the perfect middle ground.** The EC-UNI-INLINE-ALL session #9 directive of "one C template fn per opcode/kind with literal inline bodies" is **amended**: where N opcodes share emit shape, they collapse into a SINGLE template fn `sm_<group>()` / `bb_<group>()`. Opcode is communicated via `g_emit.instr->op`. Each backend arm contains a per-opcode `switch` inside; the shared per-shape body (e.g. macro_begin/call/end/pad) appears once per backend. **All emission code stays inside the template TU — no external helpers, no cross-template calls, no shared types in public headers.** Locality preserved 100%; duplication only where shape actually diverges.

**Three grouped templates landed this session as canonical examples** (commits `710b2fd5`, `2ad1896d`, `6a806546`):

- **`sm_arith`** — SM_ADD/SUB/MUL/DIV/MOD (5 opcodes, 1 fn). Per-backend switch on op selects macro name string; NET/JVM MOD irregularities preserved verbatim. Replaces `g_sm_arith` table.
- **`sm_compare`** — SM_ACOMP/SM_LCOMP (2 opcodes, 1 fn). IS_TEXT-vs-binary fork preserved inside X86 arm.
- **`sm_pat_nullary`** — 22 SM_PAT_* opcodes (1 fn). The simple `edp4_label_then` 7-line shape body appears once in X86; JVM dispatches on 5 emission-helper shapes via switch; JS/WASM straight switch-on-string.

**LOC reduction is real and locality-preserving:** `sm_pat_nullary` deleted 304 net lines (537 removed vs 233 added) while keeping every opcode's emit code inside one TU. Each opcode still owns 100% of its emit code (it's right there in the switch).

**Why this is NOT "shared helpers":**
- Shared helpers live in `emit_core.c`/`emit_sm.c` and are called from many templates.
- Grouped templates own their entire emit code in their own TU; the "shared" body is inside one fn, used only for opcodes that share shape.
- Two parallel sessions can't conflict because each group is one fn in one file.

**Recipe for grouping:**
1. Identify opcodes with same emit shape (same number of args, same call sequence pattern, only string names varying).
2. Create / reuse `sm_<group>.c` template file.
3. Single `void sm_<group>(void)` reading `g_emit.instr->op`.
4. One per-backend block (`if (IS_X86)` etc.). Inside: `switch (op)` selecting only the varying parts (macro_name string, rt_fn string, helper-method string, JVM/NET emit literal).
5. Update `sm_templates.h` decls (delete N decls, add 1).
6. Update `emit_core.h` decls (same).
7. Update master dispatch in `emit_core.c` (all N cases call `sm_<group>()`).
8. Delete old per-opcode fns from their files. If a file becomes empty, stub it with a comment (keeps Makefile happy).
9. `make -j4 scrip` + `test_per_kind_diff.sh` — gate must show 0 FAIL.
10. Commit. One group per commit.

**SUPERSEDED methodology:** The earlier per-slice rule "leave the dispatcher alive; INLINE-8 deletes orphans LAST" still applies for the underlying `emit_sm_<op>_dispatch` / `edp4_label_then` family. After grouping, the per-opcode `sm_<op>()` fns deleted in the group commit ARE the orphans for that opcode family — the master dispatch no longer references them. The lower-layer dispatchers in `emit_sm.c` remain alive (still called by edp4_label_then in the few non-grouped opcodes) until INLINE-4 promotes machinery and INLINE-8 sweeps.

**Mistakes to avoid (carried over from sessions #1-9):**
- Static helpers inside templates collapsing opcodes — that was the bad pattern; grouped templates don't introduce statics, just an inline switch in one fn.
- Layer-2 helpers in `emit_core.c` factoring across templates — still rejected. Grouped templates do NOT live in `emit_core.c`.
- "Fn fits on a screen" — still removed as a rule.
- Running full regression per slice — per-kind-diff is the binding gate; full gates session-end only.

**Lift queue status (amended further at session #N+2):**

- **SM-side grouped** (slices 13-18): 41 opcodes in 6 grouped fns (`sm_arith`, `sm_compare`, `sm_pat_nullary`, `sm_jump_group`, `sm_misc_nullary`, `sm_incr_decr`). All HQ-listed "ready to group" entries cleared. **Remaining ~16 opcodes pending INLINE-4a-inline:** dispatchers in `emit_sm.c` still go through the table-driven renderer (`emit_sm_<op>_dispatch` → `emit_sm_lblopt` → `sm_template_lookup` → renderer). Per Lon's directive on end-state — zero template helpers; each template owns full sprintf-on-`g_emit` body — the renderer machinery is to be **inlined into each template** and then **deleted**, NOT promoted to a public header. See INLINE-4 substep below for the corrected reframing.
- **BB-side:** unchanged from session #9 — body of all 17 pat-level `emit_bb_x*` fns physically in `BB_templates/` (slice 7, `045baf4a`). REOPENED for INLINE-ALL: remaining x86 in `emit_bb.c` (dispatcher trio `emit_flat_ir_alt`/`_cat`/`_fence`) to be inlined into `bb_pat_alt.c`/`bb_pat_cat.c`/`bb_fence.c` (INLINE-3). After x86 inlining: **INLINE-3-GROUP** — BB-side grouping pass mirroring SM-side slices 13/14/15. Candidate groups: `bb_pat_anchor_group` (POS/RPOS/TAB/RTAB/LEN), `bb_pat_charset_group` (ANY/NOTANY/SPAN/BREAK), `bb_pat_nullary_group` (REM/ARB/ABORT/FENCE), `bb_pat_combine_group` (ALT/CAT). One slice per group; GATE-PK PASS=420 FAIL=0 STUB=639 between each.

**Verification per commit:** `GATE-PK PASS=420 FAIL=0 STUB=639` (byte-identical at per-kind-diff). Beauty md5 suspended throughout.

**Scope (amended):** SM has 91 opcodes; 29 of them now in 3 grouped fns + ~13 in individual fns still inlined-but-not-yet-grouped + ~20 still blocked on INLINE-4. BB unchanged (97 kinds).

**Unblocks Phase B:** five per-backend GOAL files (`GOAL-SN4-X86-EMIT` [new], `-JVM-`, `-JS-`, `-NET-`, `-WASM-`).

Closed sub-rungs: EC-UNI-10..13(e), 14-PREREQ, SUSPEND_VALUE, 14(a)(b)(c)(1..7), 15, 16, 21. See git log for per-commit detail.

---

### ⚡ EC-UNI-PER-KIND-DIFF (one4all `9b905d26`)

Harness: `tools/emit_per_kind_audit.c` + `scripts/{freeze_per_kind_baseline,test_per_kind_diff,normalize_per_kind_cell}` + `baselines/per_kind/`.

For every (SM op × backend) and every (BB kind × backend × submode) cell, audit constructs synthetic instance, emits via current path, captures text/binary, normalizes (strips label numbers, addresses, node ids), diffs against frozen baseline. 1059 cells per run; baseline PASS=399 STUB=660 FAIL=0.

**Live path notes:**
- BB-side: `emit_flat_ir` → direct `emit_bb_x*` calls is still the live path; `emit_bb_node` does not yet fill `g_emit` fields, so templates' IS_X86 arms are dormant. This is the structural invariant the next rungs (REFAITH, REWIRE-ALL) operate on.
- x86_bin: process-local addresses (memcmp@PLT, rodata literal pointers) get baked in; ASLR randomizes. Bit-identity impossible. Per-kind-diff applies structural comparison for x86_bin (same byte count = same shape); full byte-level via assembled-md5 path on x86_text.

---

### ⚡ Open EC-UNI rungs

- [ ] **EC-UNI-REFAITH** — re-lift FAILing kinds byte-faithfully against per-kind diff baseline. Gate must show 100% PASS.
- [x] **EC-UNI-REWIRE-ALL** (CLOSED 2026-05-21 sessions #7/#8). IS_TEXT + IS_BIN both route through emit_bb_node. NAMEKEY-BIN complete: lbl_succ/fail/back_p in g_emit; all 14 live BB kind templates have IS_BIN arms. `0ef0f7fc`.
- [x] **EC-UNI-NAMEKEY-BIN** (CLOSED 2026-05-21 session #8, `0ef0f7fc`). g_emit.lbl_*_p for binary patch-back. Audit static labels fix. emit_bb_x* callers gone from switch.
- [ ] **EC-UNI-NAMEKEY-BIN** — name-keyed binary primitives for `--run`; rewire binary; delete `emit_bb_x*` originals.
- [ ] **EC-UNI-17** (deferred) — Layer-3 primitives audit. Parked.
- [ ] **EC-UNI-INLINE-ALL** ⚡ — **Lon directive (session #9, AMENDED session #N+2): grouped templates. Where N opcodes share emit shape, ONE template fn handles all of them via per-backend `switch(g_emit.instr->op)`.** No more one-fn-per-opcode duplication. No external helpers. All emission code stays inside the template TU. Locality 100% preserved; LOC reduction occurs naturally where shape is shared. **Three grouped templates landed (slices 13/14/15) as canonical examples.** **Substeps:**
    - [x] **INLINE-1** (slices 1-12, partial) — body of `emit_sm_<op>_dispatch` callers inlined into individual templates. **42 opcodes inlined** before grouping directive arrived. Slices 13-18 then GROUPED 41 of those 42 into 6 grouped fns (`sm_arith`, `sm_compare`, `sm_pat_nullary`, `sm_jump_group`, `sm_misc_nullary`, `sm_incr_decr`). All HQ-listed ready-to-group entries cleared. Next grouping work blocked on INLINE-4 promotion.
    - [x] **INLINE-2** (slice 11) — `g_sm_arith` table use folded into literal strings for SM_ADD/SUB/MUL/DIV/MOD. Pre-grouping; merged into `sm_arith()` at slice 13.
    - [ ] **INLINE-3** — BB-side: remaining `emit_bb_x*` helpers (`emit_flat_ir_alt`, `_cat`, `_fence`) inlined into `bb_pat_alt.c` / `bb_pat_cat.c` / `bb_fence.c` IS_X86 arms. Prerequisite for INLINE-3-GROUP.
    - [ ] **INLINE-3-GROUP** ⚡ — **BB-side grouped templates, mirror of SM-side slices 13/14/15.** After INLINE-3 closes (all `emit_bb_x*` bodies physically resident in `BB_templates/`), collapse BB kinds with shared emit shape into single `bb_<group>()` template fns. Same recipe as SM-side: opcode/kind communicated via `g_emit.instr->op` (or `g_emit.bb_node->kind`), per-backend `switch` dispatches the varying parts (helper-fn name string, slow-path tag, charset literal), shared shape body appears once per backend arm. All emission code stays inside the template TU — no external helpers, no cross-template calls. Candidate groups (subject to shape audit; one slice per group, GATE-PK PASS=420 FAIL=0 STUB=639 between each):
        - **`bb_pat_anchor_group`** — POS/RPOS/TAB/RTAB/LEN (5 kinds; offset-anchored pat with int arg, share `bb_<kind>_new(int)` shape).
        - **`bb_pat_charset_group`** — ANY/NOTANY/SPAN/BREAK (4 kinds; charset-arg pat, share `bb_<kind>_new(cset)` shape).
        - **`bb_pat_nullary_group`** — REM/ARB/ABORT/FENCE (4 kinds; zero-arg pat, share `bb_<kind>_new()` shape). Mirrors SM-side `sm_pat_nullary`.
        - **`bb_pat_string_arg_group`** — LIT (currently solo; group if INLINE-4 promotion exposes more string-arg kinds).
        - **`bb_pat_combine_group`** — ALT/CAT (2 kinds; child-walking pat, share children-pre-build + alt/cat dispatch shape; lifted from `emit_flat_ir_alt`/`_cat` post-INLINE-3).
      Per slice: identify candidate set → confirm shape match across all 5 backend arms (X86 text + bin, JVM, NET, JS, WASM) → create / reuse `BB_templates/bb_<group>.c` → single `void bb_<group>(void)` reading `g_emit.bb_node->kind` → one per-backend block with inner `switch (kind)` selecting only varying tokens → update `bb_templates.h` decls (delete N add 1) → update master BB dispatch in `emit_bb.c` (all N cases call `bb_<group>()`) → delete old per-kind fns from their files → stub empty .c with comment for Makefile → `make -j4 scrip` + `test_per_kind_diff.sh` → commit. One group per commit. **Stop condition same as SM-side:** if shape diverges beyond a `switch` on a few tokens, do NOT group — leave the kinds individual. Grouping must earn its keep via shared shape, not aesthetic preference. Expected LOC delta similar to `sm_pat_nullary` (~−300 net per ~20-kind group, ~−80 net per ~5-kind group).
    - [ ] **INLINE-4** ⚠ **RECIPE — Lon, 2026-05-21 session #N+3 (he repeated this multiple times, prior agents over-engineered it for hours).**
      **The job is reverse-engineering printed text into a printf, nothing more.** Look at JVM/JS/NET/WASM arms in any already-grouped template (e.g. `sm_arith.c`, `sm_misc_nullary` in same file). They are literally `emit_textf("    invokestatic rt/SnoRt/concat()V\n")` — one printf of a literal with `%s`/`%d` holes for globals. **X86 arms become the same thing.** No helpers. No `bb3c_format`. No `strtab_label` calls. No `emit_sm_consume_pc_label`. Just printf.
      **CRITICAL — text format: BARE asm, one space between tokens, NO column alignment.** Look at `BB_templates/bb_rem.c` X86 arm: lines are `mov ecx, dword ptr [rax]\n` / `jmp %s\n` — one space, no padding. The column-aligned 24/16-pad output you see in `baselines/per_kind/x86/text/*.s.raw` is what the OLD dispatcher emits via `bb3c_format`. The TEMPLATE emits bare text. The baseline files are the **starting point being replaced**, not the target to match.
      **Per-kind-diff WILL FAIL after each template inline** — that's expected. Per HQ "Re-freezing the per-kind baseline" section: when the change is intentional (template body replacing dispatcher), run `bash scripts/freeze_per_kind_baseline.sh` to capture the new bare-text output, then commit `baselines/per_kind/` together with the template change. The diff IS the regression-test record.
      **Procedure per template:**
      1. Open the template (e.g. `sm_pat_lit` in `sm_pat_anchors.c`).
      2. Open the matching dispatcher in `emit_sm.c` (e.g. `emit_sm_pat_lit_dispatch`). It does `pat_arg_label` → `emit_sm_lblopt(... sm_template_lookup(SM_PAT_LIT) ... anno)`. The renderer (`render_call_line` + `build_args_col`) then produces the `MNEMONIC arg1, arg2 # anno` form. **Strip that ceremony.**
      3. **Paste a bare `emit_textf("MNEMONIC arg1, arg2 # anno\n", ...)` into the X86 arm.** One space between MNEMONIC and args. No padding. Globals from `g_emit.instr->a[*]`, `g_emit.i`, etc. fill the `%s`/`%d` holes. The strtab label can be looked up with `strtab_label(buf, sizeof buf, s)` — Layer-3 registry accessor, same category as `wasm_intern_str` (`strtab_label` already de-staticed and declared in `SM_templates/sm_template_common.h` as part of slice 19-prep).
      4. Build. `bash scripts/test_per_kind_diff.sh` → expect FAIL on the cells you just changed. Inspect the diffs; confirm the new text is the bare form you intended.
      5. `bash scripts/freeze_per_kind_baseline.sh` to capture the new baseline.
      6. Confirm `test_per_kind_diff.sh` shows 0 FAIL/NEW/GONE.
      7. Commit template + baseline files together. Move to next opcode.
      Expected pace: **~10 minutes per template** (open dispatcher, paste bare text, build, refreeze, commit, repeat). 16 templates remain. One session should sweep most.
      **What NOT to do (mistakes already made):** do NOT create new public headers exposing template machinery. Do NOT route templates through `bb3c_format`/`pat_arg_label`/`emit_sm_lblopt`/`sm_template_lookup` — those are the helpers being **deleted**. Do NOT try to construct a SNOBOL4 program that exercises the opcode just to capture its output — the per-kind audit dump already has every cell. Do NOT try to match the column-aligned baseline format with `%-24s%-16s` — that smuggles the formatting machinery back into the template. Emit bare text and refreeze.
      **Reference for what to delete from emit_sm.c (per template):**
        `emit_sm_<op>_dispatch` (e.g. `emit_sm_pat_lit_dispatch`) — the per-opcode arg-setup that calls into the renderer.
        `emit_sm_<op>_template` (e.g. `emit_sm_pat_lit_template`) — the thin shim called by the template's old IS_X86 arm.
        These delete in INLINE-4b after every template is inlined; for INLINE-4a just bypass them.
      **Targets** (in suggested order — simplest first):
        `sm_pat_lit`, `sm_pat_refname`, `sm_pat_usercall` (LBLOPT shape — one label arg, one anno).
        `sm_pat_capture`, `sm_pat_usercall_args` (LBLOPT_INT32 — label + int).
        `sm_pat_capture_fn`, `sm_pat_capture_fn_args` (LBLOPT3 / LBLOPT_I_I — multi-arg).
        `sm_exec_stmt` (EXEC_VAR).
        `sm_push_lit_s`, `sm_push_var`, `sm_store_var` (LBL family).
        `sm_call_fn`, `sm_bb_once_proc`, `sm_bb_pump_proc` (LBL_INT32 + RET).
        `sm_define`, `sm_define_entry` (NOOP — just emit one line).
        `sm_push_expression`, `sm_call_expression` (PCREF — int-arg).
    - [ ] **INLINE-4b** — After every dispatcher inlined per INLINE-4: delete `emit_sm_<op>_dispatch`, `emit_sm_<op>_template`, the renderer (`emit_sm_template` + `render_*` + `build_args_col`), `sm_template_lookup`, `g_sm_templates[]`, and the `sm_op_template_t` typedef from `emit_sm.c`. Build catches any straggler caller.
    - [ ] **INLINE-4c** — Group the now-inlined templates: `sm_pat_string_arg` (LIT/REFNAME/USERCALL), `sm_pat_capture` (CAPTURE/CAPTURE_FN/CAPTURE_FN_ARGS/USERCALL_ARGS), `sm_var` (PUSH_VAR/STORE_VAR), `sm_define` (DEFINE/DEFINE_ENTRY), `sm_call` (CALL_FN/SUSPEND_VALUE), `sm_bb_calls` (BB_ONCE_PROC/BB_PUMP_PROC), `sm_expression` (PUSH_EXPRESSION/CALL_EXPRESSION). Same shape-divergence stop-condition as slices 13-18.
    - [ ] **INLINE-5** — DEPRECATED by grouped-template directive. Original ("one file per opcode for SM, matching BB") was the duplication-maximalist position; grouped templates supersede it. SM_templates/ now organized by GROUP, not opcode. Files like `sm_pat_control.c` and `sm_pat_position.c` are stubs after slice 15 — pending cleanup to actually delete (currently kept as empty .c files for Makefile compatibility).
    - [ ] **INLINE-6** — Delete `emit_sm.c` machinery surviving INLINE-1..5; should drop from 182 KB → ~minimal. `emit_bb.c` drops similarly after INLINE-3.
    - [ ] **INLINE-7** — Per-kind diff baseline re-frozen at each substep. Beauty md5 expected to shift; gate suspended per Lon directive until INLINE-ALL closes. GATE-PK is binding throughout.
    - [ ] **INLINE-8** ⚡ — **Orphan sweep (runs LAST, after INLINE-1..7 + grouping).** Once every live emit-path goes through SM template fns (grouped or individual) and BB templates, any `emit_bb_x*` / `emit_sm_*` function whose body has been absorbed becomes orphaned. Delete in dependency order. Per deletion: `make -j4 scrip` (catches missed callers); GATE-PK PASS=420 FAIL=0 (behaviour unchanged because what's deleted is unreachable). **Stop condition:** any deletion that breaks the build means the static caller-grep missed an indirect path — restore the fn, re-audit, route through a template, then resume.
    - [ ] **INLINE-8-stale-comments** — Stale "lift trail" comments inside BB_templates need updating during INLINE-8.
- [ ] **EC-UNI-18** ⚠ SUPERSEDED by EC-UNI-INLINE-ALL — was: table-driven dispatch where it earns its keep, extend x86's `g_sm_nullary` / `g_sm_arith` pattern to JVM/NET/JS/WASM for nullary + arith. Lon's 2026-05-21 directive reverses direction: tables go away, inlining wins.
- [ ] **EC-UNI-19** — add-a-backend test (`EMIT_NULL=99`). Mechanical patch + revert. Records LOC cost. Re-run after EC-UNI-INLINE-ALL to measure new cost (expected: 76 SM × 1 line + 97 BB × 1 line ≈ +173 lines per backend, all in templates).
- [ ] **EC-UNI-20** — add-an-opcode test (`SM_NOP`). Mechanical patch + revert. Records LOC cost. Post-INLINE-ALL cost: 1 new template file with 5 inlined arms.
- [ ] **EC-UNI-21-followup** — reconcile or retire M1 oracle baseline. Choose (a) re-converge to `abfd19a7...` (646 lines), or (b) retire M1, record new baseline `9cddff25...` (622 lines), re-stamp Milestone 1.
- [ ] **EC-UNI-22** — close: update `ARCH-IR.md`, `ARCH-SCRIP.md`, invariants. Update four per-backend GOAL files. Mark EC-UNI complete; Phase B opens. **Sequence note:** EC-UNI-22 should follow EC-UNI-INLINE-ALL — closing docs describe the final inlined shape, not the intermediate table-driven shape.

---

### ⚡ EC-UNI-PROTECTED-PAT-VARS (PPV) — in progress

Recognize REM/ARB/FENCE/FAIL/SUCCEED/ABORT/BAL as protected PATTERN-typed names (SPITBOL ERROR 042) and substitute `SM_PAT_<KIND>` at lower-time for bare names in pattern context. Unlocks BB-lower coverage 4→8 active pat-kinds from portable corpus.

| Name    | TT_*      | SM_PAT_*      | BB_PAT_*     | Template     | IS_X86 | IS_JVM | IS_NET | IS_JS | IS_WASM |
|---------|-----------|---------------|--------------|--------------|--------|--------|--------|-------|---------|
| REM     | TT_REM    | SM_PAT_REM    | BB_PAT_REM   | `bb_rem.c`   | ✅      | ✅      | ✅      | ✅     | ✅      |
| ARB     | TT_ARB    | SM_PAT_ARB    | BB_PAT_ARB   | `bb_arb.c`   | ✅      | ✅      | ✅      | ✅     | ✅      |
| FENCE   | TT_FENCE  | SM_PAT_FENCE0 | BB_PAT_FENCE | `bb_fence.c` | ✅      | ✅      | ✅      | ✅     | ✅      |
| FAIL    | TT_FAIL   | SM_PAT_FAIL   | (no BB)      | (Phase B)    | —      | —      | —      | —     | —       |
| SUCCEED | TT_SUCCEED| SM_PAT_SUCCEED| (no BB)      | (Phase B)    | —      | —      | —      | —     | —       |
| ABORT   | TT_ABORT  | SM_PAT_ABORT  | BB_PAT_ABORT | `bb_abort.c` | ✅      | ✅      | ✅      | ✅     | ✅      |
| BAL     | TT_BAL    | SM_PAT_BAL    | (no BB)      | (Phase B)    | —      | —      | —      | —     | —       |

IS_X86 covers both text and binary modes (IS_BIN is a strict subset; dead IS_BIN guards after IS_X86 were removed in session #6). WASM pat-kind BB emission: REM/ARB/FENCE/ABORT ✅ (PPV-8); ANY/ARBNO/BREAK/LEN/LIT/NOTANY/POS/SPAN/TAB ✅ (PPV-9). FAIL/SUCCEED/BAL have no BB kind (Phase B).

(Bare `FENCE` → `SM_PAT_FENCE0`; 1-arg variant uses `SM_PAT_FENCE1` per existing `TT_FENCE` arm in `lower.c`.)

Sites (PPV-0):
- Substitution: `src/lower/lower.c:373` — sole TT_VAR pat-context arm.
- Runtime protection: `src/runtime/snobol4/snobol4.c::NV_SET_fn` (universal chokepoint; --interp h_store_var calls it directly, bypassing rt_nv_set).
- Helper: `src/runtime/rt/rt_protected.{h,c}` — `is_protected_pat_name(name)`, `protected_pat_name_to_sm_op(name)`. Single source of truth for the 7-name → SM_op_t table.
- Error: `sno_runtime_error(42, NULL)`.

**Steps:**

- [x] **PPV-0** (CLOSED 2026-05-21 session #4, .github `afa893a0`) — Inventory. Deliverable: `PPV-0-INVENTORY.md`.
- [x] **PPV-1** (CLOSED 2026-05-21 session #5, one4all `44a5f9a5`) — Runtime protection. New `rt_protected.{h,c}`. Init-phase flag `g_protected_pat_vars_armed` in `snobol4.c` (cleared during pre-binding, armed at end of `SNO_INIT_fn`). Guard at top of `NV_SET_fn` raises `sno_runtime_error(42, NULL)`. Verified vs SPITBOL: scrip ERROR 42 = SPITBOL ERROR 042 ✓. PK PASS=399, --run smoke 186 unchanged. **Closes HQ-BUG-PROTECTED-PATTERN-VARS.**
- [x] **PPV-2** (CLOSED 2026-05-21 session #6, Sonnet 4.6) — Lower-time substitution. `lower.c` TT_VAR arm in `lower_pat_expr` now calls `protected_pat_name_to_sm_op(t->v.sval)`; if ≥ 0 emits `SM_emit(g_p, (SM_op_t)op)` and returns. Confined to `lower_pat_expr`; `lower_expr` untouched. Also fixed normalizer hole in `normalize_per_kind_cell.py` (regex `_(\d+)_(\d+)\b` → `_(\d+)_(\d+)(?=_|\b)`) to canonicalize heap-address-derived label segments; re-froze baseline (PASS=399 unchanged).
- [x] **PPV-3** (CLOSED 2026-05-21 session #6) — `x = REM` → `DATATYPE(x)` = PATTERN ✓. `lower_expr` untouched.
- [x] **PPV-4** (CLOSED 2026-05-21 session #6) — All 7 names via `--dump-sm` emit `SM_PAT_*` directly (no `SM_PUSH_VAR`). `--compile` shows `# BOX REM/ARB/FENCE`; ABORT shows `# BOX FAIL()` (pre-existing: dispatches to `emit_bb_xfail`). FAIL/SUCCEED/BAL: `SM_PAT_*` confirmed via `--dump-sm`.
- [x] **PPV-5** (CLOSED 2026-05-21 session #6) — ⚠ Beauty gate now **SUSPENDED** (see above). Original path-(a) accepted at time of commit; beauty md5 no longer binding.
- [x] **PPV-6** (CLOSED 2026-05-21 session #6) — Docs. GOAL-HEADQUARTERS.md updated. PLAN.md updated.
- [x] **PPV-7** (CLOSED 2026-05-21 session #6) — HQ-BUG-RPOS-COMPILE-SEGFAULT and HQ-BUG-RTAB-COMPILE-SEGFAULT fixed. `nd->c` null-deref guard in 3 sites.
- [x] **PPV-8** (CLOSED 2026-05-21 session #7, Sonnet 4.6) — IS_WASM arms for bb_rem/bb_arb/bb_fence/bb_abort. Each emits `(call $bb_<kind>_new)`. Baselines re-frozen. GATE-PK PASS=411 FAIL=0 STUB=648.
- [x] **PPV-9** (CLOSED 2026-05-21 session #9, Sonnet 4.6, one4all `794b9435`) — EC-UNI-REFAITH audit: all 639 remaining STUBs confirmed genuinely deferred (Phase B Icon/Prolog BB kinds + FAIL/SUCCEED/BAL pending BB). IS_WASM arms added for bb_any/arbno/break/len/lit/notany/pos/span/tab. Baselines re-frozen. GATE-PK PASS=420 FAIL=0 STUB=639.

**Coverage:** GATE-PK PASS=401 FAIL=0 STUB=658 (was 399/0/660). Two new ABORT x86 cells live.

**Sequencing:** PPV-* independent of EC-UNI-REFAITH / REWIRE-ALL / NAMEKEY-BIN. Beauty gate suspended for duration of consolidation.

**Why not part of EC-UNI proper:** EC-UNI's scope is emitter unification. PPV changes frontend lowering + runtime protection, then exposes pre-existing SM_PAT_/BB_PAT_ opcodes to wider source-syntax footprint. Parallel coverage-gain rung, not a dependency.

---

### EC-UNI gate (every step from EC-UNI-10 on)

```
GATE-1  beauty.sno --compile  →  md5 40df9e004c3e963c99af716c65f2c970  (882901 bytes)
GATE-2  bash scripts/test_smoke_icon.sh                                  # PASS=5
GATE-3  bash scripts/test_smoke_unified_broker.sh                        # PASS≥23
GATE-4  bash scripts/test_icon_all_rungs.sh                              # PASS=194/36/35 (--interp by default)
GATE-5  bash scripts/test_smoke_{snobol4,snocone,prolog,rebus,raku}.sh   # 7/0 5/0 5/0 4/0 5/0
```

---

### ISOLATION — parse→lower / parse→runtime boundary firewalls

**Goal:** lex/parse produces exactly `tree_t *`. Two boundaries: parse→lower (consumed by `lower()`) and parse→runtime. Today partially porous; ratchet shrinks the gap.

Completed: ISO-1 `261ff13d` (`lower(const tree_t *)`, ParserOutput deleted), ISO-2 `1691f44f` (lower firewall 10/7), ISO-3 `cb1738f6` (relocated `icon_gen.h`; lower 9/6, runtime firewall 16/8).

- [ ] **ISO-4 (NEXT)** — `scrip_parse` subprocess: parsers in a separate executable, stdin = source, stdout = TDump/TLump S-expression. SCRIP forks/execs, deserializes back to `tree_t`. First sub-step: write deserializer + roundtrip self-test before introducing the process boundary.
- [ ] **ISO-5** — Shrink lower firewall allowlist toward 0: extract `IcnTkKind` to `src/include/icon_tk.h`; split `raku_driver.h` → `raku_parse.h` + `raku_runtime.h`; relocate `frontend/prolog/{term,prolog_runtime,prolog_atom}.h` to `src/runtime/interp/prolog/`; rename `scrip_cc.h` → `src/include/scrip_lang.h` (54 includers).
- [ ] **ISO-6** — Shrink runtime firewall allowlist toward 0 (overlaps ISO-5).
- [ ] **ISO-7** — Link-time isolation test.

### IR Rename — builder/consumer case scheme

UPPERCASE builds IR (`SM_t`, `BB_t`, `SM_seq_new`, `BB_alloc`). lowercase consumes (`sm_interp_*`, `bb_print`, `bb_broker`, `SM_templates/` dispatchers).

Completed: IR-RN-0 `9ce69899`, IR-RN-1 `c710506f`, IR-RN-2 `92417a85`, IR-RN-3 `4a1fcc63`.

- [x] **IR-RN-4** (CLOSED 2026-05-21 session #7, .github `08e9e188`) — Update arch docs (`ARCH-IR.md`, `ARCH-ICON.md`, `ARCH-SCRIP.md`).
- [x] **IR-RN-5** (CLOSED 2026-05-21 session #7) — GATE-PK 411/0, smokes: icon 5/0, broker 23/26, snobol4 7/0, snocone 5/0, prolog 5/0, raku 5/0, rebus 4/0. IR Rename rung COMPLETE.

Reserved: `IR_LANG_*`, `SM_INTERP_*`, `SM_CALL_STACK_MAX`/`SM_GEN_LOCAL_MAX`/`SM_MAX_OPERANDS`, `BB_POOL_SIZE`, header guards, `SM_*` opcode tags, `SM_templates/`/`BB_templates/` dir names.

---

## Completed ledgers (audit trail)

Per-cluster detail in git log (authority per RULES.md). One-line summaries:

- **IJ-* / DAI-1..7 / IJ-HELLO matrix** — 6/6 wired hello-world matrix closed 2026-05-18. Icon `--interp` (mode 2) = `--ast-run` (mode 1) at 194/265; mode 1 deleted.
- **DAI-8 dead-code sweep C1–C17** — ~2700 LOC removed across 17 clusters. Final cluster C17 `d48681fb`.
- **EC (emitter consolidation) 0..WASM-SM** — three silo files + emit_ir.c + emit_ir_targets.c deleted. Unified `emit_program(ast_prog, out, mode)`. Net −2504 LOC.
- **EC-UNI 0..9d** — 52 SM templates with IS_X86 arms; matrix gate 0/365.
- **IR-CONSOLIDATE-DCG 1..7** — `ir_body` field deleted; mode-4 standalone uses `SM_seq_bb_add` lazy-alloc.
- **ST2** — `stage2_t` embeds `SM_sequence_t`; dynamic-grow tables; ~150KB .bss freed.
- **EC-UNI LIFT slices 1-7** — `045baf4a`. All 17 pat-level `emit_bb_x*` in `BB_templates/`. Matrix 855/855.
- **EC-UNI-PER-KIND-DIFF** — `9b905d26`. Harness operational; baseline PASS=399 STUB=660 FAIL=0.
- **PPV-0** — `afa893a0`. Inventory.
- **PPV-1** — `44a5f9a5`. Runtime protection ERROR 042. Closes HQ-BUG-PROTECTED-PATTERN-VARS.
- **PPV-2..6** — `1c47a59a`. Lower-time SM_PAT_* substitution in lower_pat_expr TT_VAR arm. Normalizer fix (sid_nid lookahead). Beauty md5 → 6bf2e9daa777f54f04c8f7160da435d1. GATE-PK 399/0, GATE-M 855/855, GATE-E 9/9.
- **PPV-7** — `f6e4968a`. RPOS/RTAB --compile segfault. nd->c guard in 3 sites (emit_flat_invariant, pre_build_children_text, pre_build_children).
- **PPV-8** — `ddd08f01`. bb_abort IS_X86 arm; dead IS_BIN guard removal; beauty gate suspended.
- **PPV-8 WASM** — `3e3b67b1`. IS_WASM arms for bb_rem/bb_arb/bb_fence/bb_abort. GATE-PK PASS=411 FAIL=0 STUB=648.
- **PPV-9** — `794b9435`. IS_WASM arms for bb_any/arbno/break/len/lit/notany/pos/span/tab. EC-UNI-REFAITH audit confirms remaining 639 STUBs are genuinely deferred (Phase B). GATE-PK PASS=420 FAIL=0 STUB=639.
- **EC-UNI-REWIRE + NAMEKEY-BIN** — `0ef0f7fc`. IS_TEXT + IS_BIN both routed through emit_bb_node. lbl_*_p binary patch-back. 14 BB kind templates have IS_BIN arms. emit_bb_x* switch-callers eliminated.
- **IR-RN-4/5** — `.github 08e9e188`. ARCH-IR/SCRIP/ICON updated to post-IR-RN-0 names. Cross-language gates all green. IR Rename rung COMPLETE.

**Authors (Three-developer agreement, Milestone 1):** Lon Jones Cherryholmes · Claude Sonnet 4.7.
