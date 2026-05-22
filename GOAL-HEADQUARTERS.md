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
11. **INLINE-ALL complete (session ~10, 2026-05-22).** Every SM/BB code-generation path lives exclusively in `SM_templates/*.c` and `BB_templates/*.c`. No wrapper functions, no table-driven dispatch, no per-opcode helpers outside template files. `emit_sm.c` carries only the walker, string-table, pattern-window, and pc-label infrastructure. Adding a backend = adding `IS_NEW` arms inside existing template files only.

## ⚡ SESSION ACCOUNTING (2026-05-22, session ~12 — IS_X86-STRUCTURE sweep + GOAL steps 4–8)

**Commits this session (1, one4all pending — IS_X86-STRUCTURE):**
- IS_X86-STRUCTURE: fix if/else spine in all violating SM/BB templates. 3 BB files (bb_abort, bb_rem, bb_charset_helper) + 11 SM files (sm_halt, sm_compare, sm_calls, sm_pat_anchors, sm_jumps×2, sm_arith×2, sm_bb_calls, sm_defines×2, sm_expr_incr, sm_pat_combine, sm_pat_nullary). IS_MACRO_DEF and IS_BIN are now always subordinate branches inside IS_X86 — never at the same level. PASS=407 FAIL=0 STUB=647.

**.github (this session):** added steps 4–8 to next-session list (DEAD-EMIT-AUDIT, BIN-INTO-TEMPLATES, IS_X86-STRUCTURE ✅, STYLE-ONE-SPACE, STYLE-NO-LOCAL-SHADOWS).

**Gate entering next session: PASS=407 FAIL=0 STUB=647 (one4all `3529f907` + uncommitted IS_X86-STRUCTURE changes). Verify `git -C one4all log origin/main..HEAD` and `git -C one4all diff --stat` at session start.**

### Next session — pick one:
1. **EC-UNI-23 NO-AST-PUSH-EXPR** (Lon's priority — delete SM_PUSH_EXPR, force Icon LIMIT + Prolog UNIFY/CUT to grow BB graphs). TDD: add LIMIT/UNIFY/CUT BB-graph smoke tests FIRST. Steps EC-23a–f below.
2. **BREAKX-2** — finish the enum-insertion chain so `lower.c` routes BREAKX→`rt_bb_brkx` (steps in `87957d79`/`3529f907` commit bodies; insert `SM_PAT_BREAKX`/`BB_PAT_BREAKX` at END of enums — mid-list renumbers index-aligned name arrays + audit).
3. Per-backend Phase B GOAL files (post-INLINE-ALL).
4. **DEAD-EMIT-AUDIT** (Lon, session ~12) — survey all `emit_*` functions outside `SM_templates/` and `BB_templates/` that emit x86 text or binary; verify each is either (a) genuine program-level infrastructure (file header/footer, rodata, predicate registry) or (b) dead — superseded by a template. Delete category (b). Record category (a) as explicitly out-of-scope for template migration with rationale.
5. **BIN-INTO-TEMPLATES** (Lon, session ~12) — move IS_BIN (x86 binary) emission arms from any remaining non-template sites into the appropriate SM/BB template files, so that both IS_TEXT and IS_BIN arms live exclusively inside `SM_templates/*.c` / `BB_templates/*.c`. Prerequisite: DEAD-EMIT-AUDIT complete. Start with templates that already have IS_X86 text arms and are missing binary arms.
6. **IS_X86-STRUCTURE** (Lon, session ~12) — enforce the canonical if/else spine in every SM/BB template: `IS_X86` is the outer gate; `IS_TEXT`, `IS_BIN`, `IS_MACRO_DEF` are subordinate branches inside it. No template may have `IS_TEXT`/`IS_BIN`/`IS_MACRO_DEF` at the same level as `IS_X86`. Fix all violating templates. Correct spine: `if (IS_X86) { if (IS_MACRO_DEF) { … } else if (IS_TEXT) { … } else { /* IS_BIN */ … } return; } if (IS_JVM) { … } if (IS_JS) { … } …` ✅ COMPLETE session ~12 (3 BB + 11 SM templates fixed). PASS=407 FAIL=0 STUB=647.
7. **STYLE-ONE-SPACE** (Lon, session ~12) — `emit_textf` string arguments must have exactly one space between instruction mnemonic and operands. No leading multi-space padding inside string literals (e.g. `"    aload_0\n"` → `"aload_0\n"`). Sweep all SM/BB templates and fix. Exception: intentional alignment in human-readable assembly comments is permitted.
8. **STYLE-NO-LOCAL-SHADOWS** (Lon, session ~12) — templates must not declare locals that shadow globals. Banned patterns: `BB_t *nd = g_emit.node;`, `FILE *out = g_emit.out;`, `int new_x = f(x);`. Use `g_emit.node` directly everywhere in the template body. Hide `out` completely — use it only at lower levels as a global reference; do not pass it or alias it. Do not create locals as transformations of globals (`int foo = f(g_emit.x)` → use `f(g_emit.x)` inline). Sweep all SM/BB templates and fix.
9. **STYLE-G_EMIT-RENAME** (Lon, session ~13) — rename `g_emit` → `_` everywhere in `SM_templates/`, `BB_templates/`, and their common headers (`sm_template_common.h`, `bb_template_common.h`, `emit_globals.h` extern decl). Rationale: `_` is a legal C identifier, easy to grep for intentionally (`grep '\b_\.'`), and visually recedes so that field names **pop**: `_.i`, `_.out`, `_.node`, `_.instr`, `_.op`, `_.lbl_succ`, `_.n` read like natural locals without any aliasing. The eye blurs `_` away; the signal is the field. This is the complement of STYLE-NO-LOCAL-SHADOWS: instead of promoting globals into aliases, we make the global itself as terse as a local. **Mechanical rename — no logic changes.** Steps: (a) rename `g_emit` in `emit_globals.{c,h}` declaration and definition; (b) sed-replace `g_emit\.` → `_.` across all `SM_templates/*.c`, `BB_templates/*.c`, `sm_template_common.h`, `bb_template_common.h`; (c) also replace in any helper files that call templates directly (`emit_core.c`, `emit_sm.c`, `emit_bb.c` — these own the walker and set `_.field =` before dispatch); (d) `make -j4 scrip`; (e) GATE-PK must be PASS=N FAIL=0; (f) freeze baseline if any cell shifts (should not); (g) commit. After this step, the remaining `instr` and `op` shadow locals (deferred from step 8) become trivial to inline: `g_emit.instr->op` → `_.instr->op` is short enough to use directly everywhere.

**Known issues flagged:** (a) `SM_PUSH_EXPR` opcode + `emit_push_expr` + 3 callers (`lower.c` TT_LIMIT/TT_UNIFY/TT_CUT) still live though 0/200 programs emit it — EC-UNI-23 retires them. (b) Normalizer gap: `normalize_per_kind_cell.py` strips `0x`+8+ hex digits, so 6-digit addresses escape — surfaced when code-size shift moved a baked address across the digit boundary.

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
one4all: 48497c58  (Formatter deletion + IS_MACRO_DEF, session 2026-05-21.
                     DELETED: bb3c_format (144 call sites→direct fprintf),
                     bb3c_flush_pending*, bb3c_emit_jmp, emit_text_3col,
                     emit_pad_to_blob_size, fmt_body_append, fmt_flush_jmp*,
                     emit_three_column_line (86 refs), g_fmt_label, g_fmt_body,
                     emit_bb_is_format_mode, fmt_label_save, g_bb_emit_format,
                     g_in_text_macro_body, --bb-format flag. Net: ~-400 LOC.
                     ADDED IS_MACRO_DEF to all 27 SM template fns; IS_X86
                     narrowed to exclude EMIT_MACRO_DEF. emit_sm_macro_library
                     rewired to call emit_sm_dispatch under EMIT_MACRO_DEF mode.
                     GATE-PK 420/0/639.
                     NEXT: delete render_macro_body + g_sm_templates[] +
                     sm_template_lookup + sm_op_template_t + emit_sm_template +
                     emit_sm_rtcall + emit_sm_noop + emit_sm_int64 + emit_sm_lbl
                     + emit_sm_ret + build_args_col (INLINE-6 / phase E3).
                     Then delete EMIT_MACRO_DEF/EMIT_TEXT_INLINE/emit_macro_begin
                     /emit_macro_end from emit_core once all callers gone.)
one4all: 70ac4ff9  (INLINE-4a+4b+4c slices 1-3, session 2026-05-21.
                     INLINE-4a: all remaining 8 dispatcher-backed IS_X86 arms
                     inlined to bare emit_textf — sm_halt, sm_push_lit_i,
                     sm_push_expression, sm_call_expression, sm_call_fn,
                     sm_suspend_value, sm_bb_once_proc, sm_bb_pump_proc.
                     INLINE-4b: 15 orphaned dispatcher fns + 14 header decls
                     deleted from emit_sm.c/h (-192 LOC net).
                     INLINE-4c slices 1-3: sm_var (PUSH_VAR/STORE_VAR),
                     sm_call (CALL_FN/SUSPEND_VALUE), sm_pat_string_arg
                     (PAT_LIT/REFNAME/USERCALL) grouped into single template fns.
                     GATE-PK 420/0/639. GATE-M 285/0. GATE-E 8/1 (beauty SUSPENDED).
                     NEXT: sm_define grouping (DEFINE/DEFINE_ENTRY) or INLINE-3
                     (BB-side: inline emit_flat_ir_alt/cat/fence into BB_templates).)
one4all: 1bd95155  (PIVOT — FORMATTING LAYER DELETED, session 2026-05-22.
                     Lon directive: templates/emitters carry ZERO formatting; do
                     straight prints; comparison is FILTERED not byte-identity.
                     emit_core.c: bb3c_format/bb3c_emit_jmp -> single-spaced
                     straight prints; bb3c_write_line/pad_to_width/visual_width/
                     is_cond_jmp + pending-state globals DELETED; flush fns no-op;
                     t3/tf/T3C/tj -> fprintf. emit_sm.c: emit_three_column_line ->
                     straight print; dispatch loop emits ".L<pc>:" standalone via
                     fprintf (LOOP owns label placement, templates never touch it);
                     invariant blobs exec_stmt/pat_baked bare. emit_bb.c:
                     emit_flat_entry_dispatch splits cmp/je/jmp into 3 plain lines
                     (no ;-fusion, no col-27 pad); data_buf_three_col + pend-label
                     de-padded. Net -132 LOC. 60/60 run-parity vs c44c3db6;
                     GATE-PK 420/0/639 (re-frozen, x86 baselines only); GATE-S 184
                     three-mode; GATE-J 4/0. ⚠ NOT PUSHED if hand-off interrupted —
                     verify `git -C one4all log origin/main..HEAD`.)
one4all: c44c3db6  (pre-pivot baseline: INLINE-4a-LABELFIX via dispatch-loop label
                     ownership + exec_stmt/pat_baked blobs as bare emit_textf.
                     Superseded by the pivot above but kept as the run-parity
                     reference binary. GATE-PK 420/0/639.)

✅ RESOLVED — INLINE-4a-LABEL-DISPLACEMENT was a FORMATTING artifact, not a real
   codegen bug. The renderer's bb3c layer co-located/suppressed pc-labels; bare
   emit_textf emitted them verbatim. With bb3c deleted, the dispatch loop now owns
   pc-label placement (prints ".L<pc>:" standalone before dispatch). A standalone
   label resolves to the same address as the old fused placement (intervening SM
   pseudos LABEL/DEFINE emit zero bytes). The OLD fix plan below (emit_pc_label_flush
   threaded into every template) is OBSOLETE — it would have put formatting back into
   templates. Comparison harness is /tmp/semdiff8.py (labels bind to next real instr,
   whitespace collapsed). Historical bug analysis retained below for context only.

⛔⛔⛔ (HISTORICAL — RESOLVED) INLINE-4a-LABEL-DISPLACEMENT ⛔⛔⛔
  Slices 23 & 24 (and likely 19-22) introduced a JUMP-TARGET LABEL DISPLACEMENT
  regression. GATE-PK does NOT catch it (synthetic single-instruction audit has
  no pc-labels). Diagnosis is COMPLETE; the fix is designed but NOT yet correct
  for all templates. DO NOT inline more templates until this is fixed and the
  golden diff is 0/153.

  ROOT CAUSE: the dispatch loop (emit_program, emit_sm.c ~line 2981-2994) emits a
  jump-target's ".L<pc>:" via bb3c_format(out, lbl, "", "") at the START of the
  *next* instruction's iteration. bb3c_format (emit_core.c ~505) BUFFERS a
  label-only call in g_bb3c_pending_label and attaches it to the next bb3c_format
  carrying content (co-locating label with that instr's line). Bare-inlined
  templates emit via emit_textf (raw fprintf) which does NOT flush that buffer —
  so the buffered label slides forward onto the next renderer-based instruction,
  addressing the WRONG pc. Real correctness bug for jump targets (a JUMP would
  land one-or-more instructions late).

  PARTIAL FIX (designed, verified for PUSH_*/STORE_VAR, NOT yet for others):
  Layer-3 helper emit_pc_label_flush(out) { (void)out; bb3c_flush_pending(); }
  added in emit_sm.c after emit_sm_consume_pc_label; declared in
  sm_template_common.h. Called at top of each inlined X86 arm BEFORE first
  emit_textf. For recursion.sno this gave a BYTE-FAITHFUL result vs slice 22
  (256 lines, 0 semantic diff after normalizing whitespace + label-colocation).

  STILL BROKEN (golden diff slice-18 8aa204c2 vs current = 13/153 mismatches):
  DEFINE_ENTRY still displaces (.L6 lands AFTER push rbp instead of on
  DEFINE_ENTRY) — flush ordering interacts with insn_push_rbp/mov + surrounding
  LABEL/STNO. RETURN family, PAT_LIT, PAT_REFNAME, PAT_CAPTURE*, EXEC_STMT
  (slices 19-22) ALSO need the flush and were never touched. Affected programs:
  control/expr_eval, functions/083-090 define_*, keywords/100_roman_numeral,
  library/test_case, patterns/053_pat_alt_commit, strings/cross.

  GOLDEN-DIFF HARNESS (the gate this bug needs — per-kind audit is insufficient):
  Build slice-18 reference: clone one4all to /tmp/one4all_pre, checkout 8aa204c2,
  make scrip. Then /tmp/semdiff.py (recreate below) compiles every
  test/snobol4/**/*.sno with both binaries, normalizes (strip leading ws, collapse
  internal ws runs, merge standalone "^.Lxxx:$" label lines onto next line), and
  reports mismatches. TARGET: 0/153.
    --- /tmp/semdiff.py ---
    import re,subprocess,glob
    def normalize(p):
      L=open(p).read().split('\n');o=[];i=0
      while i<len(L):
        s=L[i].strip();m=re.match(r'^(\.[A-Za-z0-9_]+:)$',s)
        if m and i+1<len(L): o.append(re.sub(r'\s+',' ',m.group(1)+' '+L[i+1].strip()));i+=2;continue
        o.append(re.sub(r'\s+',' ',s));i+=1
      return o
    G="/tmp/one4all_pre/scrip";C="./scrip"
    mism=[]
    for p in sorted(glob.glob("test/snobol4/**/*.sno",recursive=True)):
      g=subprocess.run([G,"--compile",p],capture_output=True,text=True).stdout
      c=subprocess.run([C,"--compile",p],capture_output=True,text=True).stdout
      open("/tmp/g.s","w").write(g);open("/tmp/c.s","w").write(c)
      if normalize("/tmp/g.s")!=normalize("/tmp/c.s"): mism.append(p)
    print(f"checked {len(...)}; {len(mism)} mismatches"); [print(" ",m) for m in mism]
    --- end ---

  FIX PLAN (next session):
  1. Recreate emit_pc_label_flush + declaration (was reverted in clean-up).
  2. Add the flush to ALL inlined X86 arms: sm_push_pop_lits (3), sm_defines (2),
     sm_calls (2), sm_returns (9), sm_pat_anchors (pat_lit/pat_refname),
     sm_pat_combine, sm_compare, sm_expr_incr, sm_halt — any that emit via
     emit_textf AND can sit at a target pc.
  3. For DEFINE_ENTRY: flush must precede the DEFINE_ENTRY text AND the label must
     not be re-buffered by the subsequent insn_push_rbp/mov_rbp_rsp. Investigate
     whether insn_* (t3/bb3c) re-buffer; may need flush AFTER emit_mode_set or a
     second flush. Trace with the [DBG] instrumentation pattern (set/leftover in
     the loop; "[BB3C flush] buffered=" in bb3c_flush_pending).
  4. Iterate against /tmp/semdiff.py until 0/153.
  5. THEN freeze per-kind baseline, run GATE-PK (420/0/639), commit as
     "INLINE-4a-LABELFIX: emit_pc_label_flush across all inlined templates".
  6. Lon directive (this session): templates carry ZERO formatting — bare
     emit_textf, single space between tokens, one line per emit, built by concat
     of string literals + globals with conditional concats as needed. Regenerated
     text must be byte-equal (via golden diff) to the pre-inline renderer output.
⛔⛔⛔ END CRITICAL OPEN BUG ⛔⛔⛔

one4all: 2187693e  (INLINE-4a slice 22: 9 RETURN-family templates inlined to bare
                     emit_textf form. sm_return: SM_RETURN -> "RETURN\n" with
                     g_in_define_body+insn_pop_rbp guard; SM_RETURN_S/F ->
                     "RETURN_VARIANT 0, cond, pc # opname\n". sm_freturn ->
                     "RETURN_VARIANT 1, cond, pc # opname\n". sm_nreturn walks
                     prog->instrs for SM_LABEL; emits NRETURN_VAR if found,
                     else RETURN_VARIANT 2, cond, pc. codegen_intern_str
                     promoted to public Layer-3 accessor. 6 emit_sm_*_dispatch/
                     template/ret_* fns now orphaned for INLINE-4b.
                     GATE-PK PASS=420 FAIL=0 STUB=639.)
one4all: 2e33f0fd  (INLINE-4a slice 21: 6 PAT-family + EXEC_STMT templates inlined
                     to bare emit_textf. sm_pat_capture, sm_pat_capture_fn,
                     sm_pat_capture_fn_args, sm_pat_usercall, sm_pat_usercall_args,
                     sm_exec_stmt. GATE-PK PASS=420 FAIL=0 STUB=639.)
one4all: 043be429  (INLINE-4a slice 20: sm_pat_refname bare emit_textf.)
one4all: 29319ad7  (INLINE-4a slice 19: sm_pat_lit bare emit_textf. First slice
                     of the bare-inline sweep superseding the column-padded
                     dispatcher path. strtab_label promoted to Layer-3 accessor.)

Earlier slices (git log for detail):
  slices 13-18  EC-UNI-INLINE-GROUP: 41 opcodes in 6 grouped fns (sm_arith,
                  sm_compare, sm_pat_nullary, sm_jump_group, sm_misc_nullary,
                  sm_incr_decr). Lon's grouped-template directive landed at
                  slice 13. See "Grouped templates landed" table below.
  slices 1-12   INLINE-1/2: pre-grouping per-opcode inlines + table eliminations.
                  All merged into grouped fns at slices 13-18.
  PPV-0..9      Protected pat-vars (REM/ARB/FENCE/etc -> SPITBOL ERROR 042).
                  Lower-time SM_PAT_* substitution + NV_SET_fn runtime guard.
                  Closes HQ-BUG-PROTECTED-PATTERN-VARS. All IS_WASM arms added.
                  GATE-PK 399 -> 420 via coverage gain.
  EC-UNI-REWIRE All 14 live BB kinds route through emit_bb_node (IS_TEXT+IS_BIN).
  EC-UNI-NAMEKEY-BIN  lbl_*_p in g_emit; binary patch-back; emit_bb_x* callers
                  gone from switch.
  9b905d26      EC-UNI-PER-KIND-DIFF harness (1059 cells, baseline PASS=399).
corpus:  5fc1427    (demo/beauty/ canonical; beauty_suite/ apparatus separated)

smoke icon: 5/0    smoke prolog: 5/0   smoke rebus: 4/0
smoke raku: 5/0    smoke snobol4: 7/0  smoke snocone: 5/0
broker: 23/26      icon rungs: 194/36/35
matrix gate: 855/855 PASS
beauty.sno --compile md5/.o: SUSPENDED per Lon directive (consolidation)
M1 oracle: DRIFTED (9cddff25 622 lines vs M1 abfd19a7 646 lines)
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

Pending-INLINE-4a-inline (current dispatchers in emit_sm.c go through emit_sm_<op>_dispatch -> emit_sm_lblopt -> sm_template_lookup -> renderer; need inlining into each template's IS_X86 arm using bare emit_textf — NOT header promotion of renderer machinery; renderer machinery to be DELETED, not exposed):
  COMPLETED (slices 19-22):
    sm_pat_lit                          (slice 19, 29319ad7)
    sm_pat_refname                      (slice 20, 043be429)
    sm_pat_usercall, sm_pat_capture,
      sm_pat_capture_fn,
      sm_pat_capture_fn_args,
      sm_pat_usercall_args,
      sm_exec_stmt                      (slice 21, 2e33f0fd)
    sm_return, sm_freturn, sm_nreturn
      (9 opcodes; codegen_intern_str
       promoted to Layer-3 accessor)    (slice 22, 2187693e)
  REMAINING (~13 templates):
    sm_push_lit_s    (sm_push_pop_lits.c)                                    (LBL_INT32 shape; needs render_str_preview inline or Layer-3 promotion)
    sm_push_var / sm_store_var                                               (LBL shape)
    sm_define / sm_define_entry                                              (NOOP shape; sm_define_entry also emits push rbp/mov rbp,rsp via insn_*)
    sm_call_fn / sm_suspend_value                                            (LBL_INT32 + RET shape)
    sm_bb_once_proc / sm_bb_pump_proc                                        (LBL_INT32 shape)
    sm_push_expression / sm_call_expression                                  (PCREF shapes)
    sm_stno          (special — reads SrcLines + builds banner; defer)
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

### ⚡ EC-UNI LIFT PATTERN — grouped templates

Where N opcodes share emit shape, they collapse into a SINGLE template fn
`sm_<group>()` / `bb_<group>()`. Opcode is communicated via
`g_emit.instr->op`. Each backend arm contains an inner `switch (op)`
selecting only the varying tokens. All emission code stays inside the
template TU — no external helpers, no cross-template calls, no shared
types in public headers. (Restated more formally in Invariant #10.)

**Recipe for grouping:**
1. Identify opcodes with same emit shape (same arg-count, same call sequence pattern, only string names varying).
2. Create / reuse `sm_<group>.c` (or `bb_<group>.c`).
3. Single `void sm_<group>(void)` reading `g_emit.instr->op`.
4. One per-backend block (`if (IS_X86)` etc.) with inner `switch (op)` on varying tokens.
5. Update `sm_templates.h` + `emit_core.h` decls (delete N, add 1).
6. Update master dispatch in `emit_core.c` (all N cases call `sm_<group>()`).
7. Delete old per-opcode fns; stub empty files with a comment for Makefile.
8. `make -j4 scrip` + `test_per_kind_diff.sh` → 0 FAIL.
9. Commit. One group per commit. **Stop condition:** if shape diverges beyond a `switch` on a few tokens, do NOT group — leave the kinds individual. Grouping must earn its keep via shared shape.

**Mistakes already made (sessions #1-9):**
- Static helpers inside templates "collapsing" opcodes — bad pattern; grouped templates use an inline switch in one fn.
- Layer-2 helpers in `emit_core.c` factoring across templates — rejected.
- "Fn fits on a screen" — removed as a rule.
- Running full regression per slice — per-kind-diff is binding per-slice; full gates session-end only.

**Lift queue status:**
- **SM-side grouped:** 41 opcodes in 6 grouped fns (slices 13-18; see "Grouped templates landed" in Watermark). Plus 9 RETURN opcodes inlined-but-not-yet-grouped in `sm_returns.c` (slice 22). Remaining ~13 templates pending INLINE-4a-inline (table-driven renderer still in path). After INLINE-4 → INLINE-4c grouping pass.
- **BB-side:** all 17 pat-level `emit_bb_x*` physically in `BB_templates/` (slice 7, `045baf4a`). x86 dispatcher trio (`emit_flat_ir_alt`/`_cat`/`_fence`) still in `emit_bb.c` — to be inlined per INLINE-3. After INLINE-3: **INLINE-3-GROUP** — BB-side grouping pass. Candidate groups:
  - `bb_pat_anchor_group` — POS/RPOS/TAB/RTAB/LEN (offset-anchored, int arg)
  - `bb_pat_charset_group` — ANY/NOTANY/SPAN/BREAK (charset arg)
  - `bb_pat_nullary_group` — REM/ARB/ABORT/FENCE (zero arg)
  - `bb_pat_string_arg_group` — LIT (solo; group if INLINE-4 exposes more)
  - `bb_pat_combine_group` — ALT/CAT (child-walking; from `emit_flat_ir_alt`/`_cat`)

**Verification per commit:** GATE-PK PASS=420 FAIL=0 STUB=639. Beauty md5 suspended throughout.

**Scope:** SM has 91 opcodes; ~50 grouped or inlined, ~13 still blocked on INLINE-4. BB has 97 kinds.

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
- [x] **EC-UNI-REWIRE-ALL** (CLOSED 2026-05-21 sessions #7/#8, `0ef0f7fc`). IS_TEXT + IS_BIN both route through emit_bb_node. NAMEKEY-BIN complete: lbl_succ/fail/back_p in g_emit; all 14 live BB kind templates have IS_BIN arms.
- [x] **EC-UNI-NAMEKEY-BIN** (CLOSED 2026-05-21 session #8, `0ef0f7fc`). g_emit.lbl_*_p for binary patch-back. Audit static labels fix. emit_bb_x* callers gone from switch.
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
    - [ ] **INLINE-4** ⚠ **RECIPE.**

      **Rule:** the X86 arm becomes `emit_textf("MNEMONIC arg1, arg2 # anno\n", ...)` — one printf of a literal with `%s`/`%d` holes for globals from `g_emit.instr->a[*]`, `g_emit.i`, etc. No padding, no width, no truncation, no `%-24s%-16s`, no `bb3c_format`, no `pat_arg_label`, no `emit_sm_lblopt`, no `sm_template_lookup`, no intermediate snprintf-then-emit_textf. **`emit_textf` IS `fprintf(out, ...)`.** Model: `BB_templates/bb_rem.c`, `sm_pat_lit`, `sm_returns` (slice 22). Lon: prior agents over-engineered this for hours — if you find yourself adding ceremony, RIP IT OUT.

      The OLD column-aligned `.s` output (`                        RETURN_VARIANT   0, 1, 0 # SM_RETURN_S`) is being abandoned wholesale. New baseline is `RETURN_VARIANT 0, 1, 0 # SM_RETURN_S` — single-space tokens, no padding. Baselines re-frozen as each template lands.

      **Allowed Layer-3 registry accessors** (declared in `sm_template_common.h`): `strtab_label(buf,sz,s)`, `codegen_intern_str(s)` (intern + label in one call), `wasm_intern_str(s)` / `wasm_intern_name(s)`. Any new one needs the same justification (registry accessor for irreducible-bottom layer) and goes in the same header.

      **Procedure per template:**
      1. Open template (e.g. `sm_returns.c`) and matching dispatcher in `emit_sm.c`.
      2. Replace IS_X86 arm body with bare `emit_textf("MNEMONIC ... # anno\n", ...)`.
      3. `make -j4 scrip` (clean build).
      4. `./scrip --audit-per-kind /tmp/audit_inspect && cat /tmp/audit_inspect/x86/text/SM_<OP>.s` — confirm bare form.
      5. `bash scripts/test_per_kind_diff.sh` — expect FAIL only on the cells touched (intentional regression).
      6. `bash scripts/freeze_per_kind_baseline.sh` — capture new baseline.
      7. Confirm `test_per_kind_diff.sh` reports `PASS=420 FAIL=0 STUB=639 NEW=0 GONE=0`.
      8. Commit template + baseline files together. Next opcode.

      Pace target: **~10 min per template**.

      **Dispatchers to leave in place (orphaned for INLINE-4b sweep):**
        `emit_sm_<op>_dispatch`, `emit_sm_<op>_template`. They become unreachable as each template's IS_X86 arm bypasses them. Delete in 4b after all are inlined.

      **Targets** (simplest first):
        ✅ `sm_pat_lit` (slice 19, `29319ad7`).
        ✅ `sm_pat_refname` (slice 20, `043be429`).
        ✅ `sm_pat_usercall`, `sm_pat_capture`, `sm_pat_capture_fn`,
           `sm_pat_capture_fn_args`, `sm_pat_usercall_args`, `sm_exec_stmt`
           (slice 21, `2e33f0fd`).
        ✅ `sm_return` / `sm_freturn` / `sm_nreturn` (9 opcodes, slice 22, `2187693e`).
           Plain RETURN: `g_in_define_body` guard + `insn_pop_rbp()` + `"RETURN\n"`.
           Variants: `"RETURN_VARIANT %d, %d, %d # %s\n"`. NRETURN special-cases
           prog-walk for SM_LABEL → `"NRETURN_VAR %s, %d, %d # %s\n"` if found.
           `codegen_intern_str` promoted to Layer-3 accessor.

        **NEXT — `sm_push_lit_s` / `sm_push_var` / `sm_store_var`** (LBL family).
           Bare forms:
             PUSH_STR  → `PUSH_STR %s, %d # "<preview>"\n`   (label, len, 40-char-with-ellipsis preview)
             PUSH_VAR  → `PUSH_VAR %s # %s\n`               (label, name)
             STORE_VAR → `STORE_VAR %s # %s\n`              (label, name)
           PUSH_STR preview: `render_str_preview` is currently `static` in
           `emit_sm.c`. Lon's call — either (a) promote to Layer-3 (declare
           in `sm_template_common.h`), or (b) inline the 40-char-with-ellipsis
           logic into the template. Slice 22 chose (a) for `codegen_intern_str`.

        **After LBL family — `sm_define` / `sm_define_entry`** (NOOP shape).
           `sm_define_entry` also emits `push rbp / mov rbp, rsp` byte
           sequence — call `insn_push_rbp()` from `emit_core.h`. Sets
           `g_in_define_body = 1` (preserves the flag `sm_return` checks).

        **LBL_INT32 + RET family:** `sm_call_fn`, `sm_suspend_value`,
        `sm_bb_once_proc`, `sm_bb_pump_proc`. Pending-pc-label consume
        likely needed — inspect dispatcher.

        **PCREF:** `sm_push_expression`, `sm_call_expression`.

        **STNO (defer):** `sm_stno` reads SrcLines + builds banner; doesn't
        share the simple printf-of-globals shape.
    - [ ] **INLINE-4b** — Delete now-orphaned dispatchers: `emit_sm_<op>_dispatch`, `emit_sm_<op>_template`, `emit_sm_template` + `render_*` + `build_args_col`, `sm_template_lookup`, `g_sm_templates[]`, `sm_op_template_t` typedef. Build catches stragglers.
    - [ ] **INLINE-4c** — Group inlined templates (same shape-divergence stop-condition as slices 13-18): `sm_pat_string_arg` (LIT/REFNAME/USERCALL), `sm_pat_capture` (CAPTURE/CAPTURE_FN/CAPTURE_FN_ARGS/USERCALL_ARGS), `sm_var` (PUSH_VAR/STORE_VAR), `sm_define` (DEFINE/DEFINE_ENTRY), `sm_call` (CALL_FN/SUSPEND_VALUE), `sm_bb_calls` (BB_ONCE_PROC/BB_PUMP_PROC), `sm_expression` (PUSH_EXPRESSION/CALL_EXPRESSION), `sm_returns` (already grouped — 9 RETURN opcodes in 3 fns; further consolidation if shapes align after sm_return's `g_in_define_body` special-case is reviewed).
    - [ ] **INLINE-5** — DEPRECATED by grouped-template directive. `SM_templates/` organized by group, not opcode. Stub `.c` files (e.g. `sm_pat_control.c`, `sm_pat_position.c`) pending cleanup.
    - [ ] **INLINE-6** — Delete `emit_sm.c` machinery surviving INLINE-1..5 (currently 182 KB → expected ~minimal). `emit_bb.c` drops after INLINE-3.
    - [ ] **INLINE-7** — Per-kind diff baseline re-frozen each substep. Beauty md5 expected to shift; gate suspended until INLINE-ALL closes. GATE-PK binding throughout.
    - [ ] **INLINE-8** ⚡ — **Orphan sweep (LAST).** Delete any `emit_bb_x*` / `emit_sm_*` fn whose body has been absorbed. Per deletion: `make -j4 scrip` (catches missed callers); GATE-PK unchanged. Stop on build break — restore fn, re-audit indirect path, route through template, resume.
    - [ ] **INLINE-8-stale-comments** — Update stale "lift trail" comments in BB_templates during INLINE-8.
- [ ] **EC-UNI-18** ⚠ SUPERSEDED by EC-UNI-INLINE-ALL — was: table-driven dispatch where it earns its keep, extend x86's `g_sm_nullary` / `g_sm_arith` pattern to JVM/NET/JS/WASM for nullary + arith. Lon's 2026-05-21 directive reverses direction: tables go away, inlining wins.
- [ ] **EC-UNI-19** — add-a-backend test (`EMIT_NULL=99`). Mechanical patch + revert. Records LOC cost. Re-run after EC-UNI-INLINE-ALL to measure new cost (expected: 76 SM × 1 line + 97 BB × 1 line ≈ +173 lines per backend, all in templates).
- [ ] **EC-UNI-20** — add-an-opcode test (`SM_NOP`). Mechanical patch + revert. Records LOC cost. Post-INLINE-ALL cost: 1 new template file with 5 inlined arms.
- [ ] **EC-UNI-21-followup** — reconcile or retire M1 oracle baseline. Choose (a) re-converge to `abfd19a7...` (646 lines), or (b) retire M1, record new baseline `9cddff25...` (622 lines), re-stamp Milestone 1.
- [x] **EC-UNI-22** ✅ — closed: `ARCH-IR.md` updated (new-opcode instructions reflect INLINE-ALL), invariant #11 added to HQ. Per-backend GOAL files clean (no stale refs). EC-UNI-INLINE-ALL complete; Phase B opens. (`302a1207`, session ~10, 2026-05-22)
- [ ] **EC-UNI-23 — NO-AST-PUSH-EXPR (delete `SM_PUSH_EXPR`)** ⚡ **Runs DIRECTLY AFTER emitter consolidation (EC-UNI-22).** **Rationale (Lon, 2026-05-22):** `SM_PUSH_EXPR` is the last AST escape hatch in lowering — `emit_push_expr()` (`lower.c` ~74) does `SM_emit_ptr(g_p, SM_PUSH_EXPR, ast_gc_clone(t))`, freezing a raw `tree_t*` into the instruction stream so the runtime can fall back to AST interpretation. Deleting it is a **forcing function**: with no `PUSH_EXPR`, the Icon `LIMIT` and Prolog `UNIFY`/`CUT` lowering paths CANNOT defer to the AST and MUST grow real BB graphs. This is the [NO-AST] invariant (Invariant #1) made unavoidable — the correct control. Superseded in practice by `SM_PUSH_EXPRESSION` (`entry, arity` — a hoisted-thunk reference, no frozen AST). No test program emits `SM_PUSH_EXPR` today (0/200 surveyed), but 3 live dispatch sites still lower to it.
    **Current state (session ~11, 2026-05-22):** audit cell already retired (`57c96cbd`) — the x86 arm emitted an unstable host pointer. Opcode + `emit_push_expr` + 3 callers remain.
    **Steps:**
    - [ ] **EC-23a** — Survey the 3 `emit_push_expr` callers and define their BB-graph replacement:
        - `lower.c` `lower_limit` (`TT_LIMIT`, ~1468): currently `emit_push_expr(t); SM_emit(SM_BB_PUMP)`. Icon LIMIT(e,n) — must lower `e` to a real generator BB graph + a pump/count box, not a frozen AST thunk.
        - `lower.c` `TT_UNIFY` (~1893): `emit_push_expr(t); SM_emit_si(SM_CALL_FN,"PL_UNIFY",0)`. Prolog `=/2` — must build `BB_PL_UNIFY` over lowered argument BB nodes.
        - `lower.c` `TT_CUT` (~1894): `emit_push_expr(t); SM_emit_si(SM_CALL_FN,"PL_CUT",0)`. Prolog `!` — must build `BB_PL_CUT`.
      Cross-ref `GOAL-PROLOG-BB-JCON.md` (PJ-9e multi-clause bodies) and `GOAL-LANG-ICON.md` (IC-9) — these are the sessions this deletion forces forward.
    - [ ] **EC-23b** — Add BB-graph smoke tests for LIMIT / UNIFY / CUT FIRST (TDD: deletion must not silently break Prolog cut/unify — there is no current coverage). Gate: each runs correctly in `--interp` and `--run`.
    - [ ] **EC-23c** — Rewire the 3 sites to build BB graphs (per EC-23a); delete `emit_push_expr` helper.
    - [ ] **EC-23d** — Delete `SM_PUSH_EXPR` from `src/include/SM.h` enum. ⚠ **Delete in place is safe ONLY if it is the LAST member or removal is paired with a full rebuild** — but the SM opcode enum is index-aligned with the name array `sm_prog.c:242` (`g_sm_op_names[]`) and the interp handler table `sm_jit_interp.c:1009`. Removing a mid-enum member renumbers all subsequent opcodes. Either (a) remove the enum member AND the corresponding name-array slot AND handler-table slot together (all index-aligned, rebuild catches mismatches via the per-kind audit), or (b) if any serialized SM persists across the boundary, leave a `SM_PUSH_EXPR_DEAD` placeholder. Prefer (a).
    - [ ] **EC-23e** — Delete the now-orphaned `sm_push_expr` template arm (`SM_templates/sm_expr_incr.c`), its dispatch case (`emit_core.c:1360`), the interp handler `h_push_expr` (`sm_jit_interp.c`), and the `SM.h` doc comments referencing `SM_PUSH_EXPR`. Build catches stragglers.
    - [ ] **EC-23f** — GATE-PK + GATE-S + GATE-J. Prolog/Icon smoke must stay green (now via BB graphs, not AST). Freeze baseline. Commit.

---

### EC-UNI-PROTECTED-PAT-VARS (PPV) — ✅ COMPLETE

Recognized REM/ARB/FENCE/FAIL/SUCCEED/ABORT/BAL as protected PATTERN-typed
names (SPITBOL ERROR 042); SM_PAT_<KIND> substitution at lower-time
(`lower.c` TT_VAR pat-context arm); runtime guard at NV_SET_fn chokepoint
(`src/runtime/rt/rt_protected.{h,c}`). PPV-0..9 closed (sessions #4-9).
GATE-PK coverage: 399 → 420 via new live x86/wasm cells. **Closes
HQ-BUG-PROTECTED-PATTERN-VARS, HQ-BUG-RPOS-COMPILE-SEGFAULT,
HQ-BUG-RTAB-COMPILE-SEGFAULT.** Detail in git log (PPV-1 `44a5f9a5`,
PPV-2 `1c47a59a`, PPV-7 `f6e4968a`, PPV-8 `ddd08f01` / `3e3b67b1`,
PPV-9 `794b9435`).

BB coverage table (current): all 14 live BB pat-kinds have x86 (text+bin),
JVM, NET, JS, WASM arms. FAIL/SUCCEED/BAL have no BB kind (Phase B).

---

### EC-UNI gates — see "Gates" section at top of file

Beauty md5 binding gate is SUSPENDED per Lon directive throughout consolidation.
GATE-PK is the binding per-slice gate. GATE-M / GATE-S / GATE-J for session-end / escalation.

---

### ISOLATION — parse→lower / parse→runtime boundary firewalls

**Goal:** lex/parse produces exactly `tree_t *`. Two boundaries: parse→lower (consumed by `lower()`) and parse→runtime. Today partially porous; ratchet shrinks the gap.

Completed: ISO-1 `261ff13d` (`lower(const tree_t *)`, ParserOutput deleted), ISO-2 `1691f44f` (lower firewall 10/7), ISO-3 `cb1738f6` (relocated `icon_gen.h`; lower 9/6, runtime firewall 16/8).

- [ ] **ISO-4 (NEXT)** — `scrip_parse` subprocess: parsers in a separate executable, stdin = source, stdout = TDump/TLump S-expression. SCRIP forks/execs, deserializes back to `tree_t`. First sub-step: write deserializer + roundtrip self-test before introducing the process boundary.
- [ ] **ISO-5** — Shrink lower firewall allowlist toward 0: extract `IcnTkKind` to `src/include/icon_tk.h`; split `raku_driver.h` → `raku_parse.h` + `raku_runtime.h`; relocate `frontend/prolog/{term,prolog_runtime,prolog_atom}.h` to `src/runtime/interp/prolog/`; rename `scrip_cc.h` → `src/include/scrip_lang.h` (54 includers).
- [ ] **ISO-6** — Shrink runtime firewall allowlist toward 0 (overlaps ISO-5).
- [ ] **ISO-7** — Link-time isolation test.

### IR Rename — ✅ COMPLETE

UPPERCASE builds IR (`SM_t`, `BB_t`, `SM_seq_new`, `BB_alloc`); lowercase
consumes (`sm_interp_*`, `bb_print`, `bb_broker`, `SM_templates/`
dispatchers). IR-RN-0..5 all closed. See git log
(IR-RN-0 `9ce69899`, IR-RN-1 `c710506f`, IR-RN-2 `92417a85`,
IR-RN-3 `4a1fcc63`, IR-RN-4/5 `.github 08e9e188`).

Reserved (do not rename without HQ amendment): `IR_LANG_*`, `SM_INTERP_*`,
`SM_CALL_STACK_MAX`/`SM_GEN_LOCAL_MAX`/`SM_MAX_OPERANDS`, `BB_POOL_SIZE`,
header guards, `SM_*` opcode tags, `SM_templates/`/`BB_templates/`
directory names.

---

## Completed ledgers

Per RULES.md, **git log is the authority** for per-cluster detail.
Cluster pointers (search `git log --oneline --grep=<token>`):

- **IJ-* / DAI-1..7 / IJ-HELLO** — wired hello-world matrix 6/6 (2026-05-18).
  Icon `--interp` (mode 2) = `--ast-run` (mode 1) at 194/265; mode 1 deleted.
- **DAI-8** — dead-code sweep C1–C17, ~2700 LOC removed. Final `d48681fb`.
- **EC** — emitter consolidation: silos + emit_ir.c deleted; unified
  `emit_program(ast_prog, out, mode)`. Net −2504 LOC.
- **EC-UNI 0..9d** — 52 SM templates with IS_X86 arms; matrix gate 0/365.
- **EC-UNI LIFT slices 1-7** `045baf4a` — all 17 pat-level `emit_bb_x*` in
  `BB_templates/`. Matrix 855/855.
- **EC-UNI-REWIRE + NAMEKEY-BIN** `0ef0f7fc` — IS_TEXT + IS_BIN route through
  emit_bb_node. lbl_*_p binary patch-back. 14 BB kind templates have IS_BIN
  arms. emit_bb_x* switch-callers gone.
- **EC-UNI-PER-KIND-DIFF** `9b905d26` — harness operational; baseline
  PASS=399 STUB=660 FAIL=0 at landing.
- **IR-CONSOLIDATE-DCG 1..7** — `ir_body` field deleted; mode-4 standalone
  uses `SM_seq_bb_add` lazy-alloc.
- **ST2** — `stage2_t` embeds `SM_sequence_t`; dynamic-grow tables;
  ~150KB .bss freed.
- **PPV-0..9** — see PPV section above.
- **IR-RN-0..5** — see IR Rename section above.

**Authors (Three-developer agreement, Milestone 1):** Lon Jones Cherryholmes · Claude Sonnet 4.7.
