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
8. **Unified dispatch owns mode-setting.** Per-opcode iteration calls `emit_mode_set(TEXT_MODE(), out)` at entry. Individual dispatchers stay idempotent.
9. **One file per Byrd Box in `BB_templates/`.** Each Byrd Box (`bb_lit`, `bb_any`, ..., `bb_capture`, `bb_pl_arith`, ...) lives in its own `bb_<name>.c`. No consolidated multi-BB TUs. EC-UNI-13(a) and 13(e) violated this and were reversed at one4all@266fc28a.

## Session Setup

Every session container hits the same three friction points. The block below installs around them; each step is idempotent.

```bash
# (1) System packages — installs libgc-dev (Boehm GC, fixes the recurring
#     'fatal error: gc/gc.h: No such file or directory'), bison, flex, nasm,
#     wabt, libgmp-dev, m4. SKIPs when present.
bash /home/claude/one4all/scripts/install_system_packages.sh

# (2) Build scrip with FULL output to log (the build_scrip.sh wrapper's
#     'tail -3' truncates real errors; bypass it). On failure, grep for
#     the cause in one line.
cd /home/claude/one4all && make -j4 scrip > /tmp/build_full.log 2>&1
if [ ! -x /home/claude/one4all/scrip ]; then
    echo "BUILD FAILED — first error:"; grep -E "error:|fatal error" /tmp/build_full.log | head -5
    exit 1
fi
echo "OK scrip built"

# (3) Git identity in all three repos (per RULES.md).
for r in /home/claude/one4all /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done

# (4) SPITBOL oracle (ships with prebuilt bin/sbl).
[ -d /home/claude/x64 ] || git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64

# (5) Per-kind diff baseline check (EC-UNI-PER-KIND-DIFF, primary invariant
#     since one4all 9b905d26).  Replaces the matrix + beauty + smoke session-
#     start sweep.  ~5–10s for 1059 cells.
bash /home/claude/one4all/scripts/test_per_kind_diff.sh
# Expect: PASS=399 FAIL=0 STUB=660 NEW=0 GONE=0  (at one4all 9b905d26).
# If FAIL>0 or GONE>0: prior session left damage; investigate before cutting.
```

## Architecture

```
AST --(lower)--> SM_sequence_t  [SM_BB_XXX bridge opcodes]
                 BB_graph_t*    [pre-built per bridge op, single-structure via SM_sequence_t.bb_table]
```

Mode 2 (`--interp`) is the reference path for Icon at 194/265. Mode 4 (`--compile`) emits wired x86 — no `bb_broker`.

## Gates

### Directive: ALWAYS test in --run mode for emitter work

**`--run` is the only mode that exercises the x86 emitter through the JIT path
(`SM_sequence_t → x86 bytes → mmap → jump in`).  `--interp` runs the SM
dispatch interpreter and NEVER touches the x86 emission code at all.**

For ANY work touching `emit_bb.c`, `emit_sm.c`, `BB_templates/`, `sm_*.c` templates,
the x86 lowering, the byte-emission primitives, or anything else that ends up in
JIT-emitted code: test under `--run` (or `--compile` for byte-identity), not
`--interp`.  An `--interp` pass on emitter changes is a blank test — it confirms
the interpreter still works while telling you nothing about whether your edit
broke the emitter.

**Use these gate scripts for emitter work:**
- `scripts/test_crosscheck_icon.sh` — cross-checks Icon corpus under all three modes including `--run` (JIT).
- `scripts/test_smoke_snobol4_jit.sh` — SNOBOL4 corpus three-mode parity, explicit `--run PASS` baseline (currently 186).
- `scripts/test_gate_ec_uni_complete.sh` — beauty.sno `--compile` md5 (this DOES exercise the x86 emitter; that's why it has been catching things).
- `scripts/test_gate_em_template_matrix.sh` — static structural invariant.

**Avoid for emitter work:** any `*_smoke_icon.sh` / `*_smoke_unified_broker.sh` /
`*_icon_all_rungs.sh` that defaults to `--interp` — those scripts run the
interpreter and are valid for INTERPRETER work, not emitter work.

### Directive: emitter-refactor session pace (revised 2026-05-21 Lon)

**The per-kind filter-diff harness (EC-UNI-PER-KIND-DIFF, one4all `9b905d26`)
is the new primary per-slice invariant.**  It is ~5–10 seconds end-to-end,
covers all 1059 (SM op × BB kind) × (backend × submode) cells, and detects
byte-level drift through a filter-then-diff pipeline that strips known-OK
variability (compiler-generated label numbers, rodata pointer addresses,
node ids).  This subsumes most of what the legacy matrix + beauty + smoke
gates were catching indirectly.

The legacy gates remain useful for **escalation scenarios** — see "When to
escalate" below — but are no longer required per-slice.

Use this tiered cadence:

**Per-slice fast cycle (the new default — use this for every slice):**
```
make -j4 scrip                                                # must build clean
bash scripts/test_per_kind_diff.sh                            # PRIMARY invariant: 1059 cells, ~5–10s
```
Exit 0 = slice is good.  Commit + push.

**Session-start gate (run ONCE at session start):**
```
make -j4 scrip                                                # confirm clean build
bash scripts/test_per_kind_diff.sh                            # confirm prior session's baseline still passes
```
If both pass, start cutting.  No need to re-run the legacy matrix/beauty
gates unless your work crosses one of the escalation triggers below.

**Session-end gate (run ONCE at handoff):**
```
bash scripts/test_per_kind_diff.sh                            # primary
bash scripts/test_gate_em_template_matrix.sh                  # confirm structural invariant (matrix N×7 cells)
bash scripts/test_gate_ec_uni_complete.sh                     # beauty.sno --compile md5 + 9-gate roll-up
```
The matrix + beauty gates here are belt-and-suspenders coverage of paths
that DON'T flow through emit_bb_node / emit_sm_dispatch (e.g. emit_flat_ir
direct calls, dispatchers themselves).  If per-kind-diff is clean, these
will be clean too in nearly all cases; if not, the divergence itself is
informative.

**Escalate to full legacy gates mid-session ONLY when:**
- Per-kind-diff reports a FAIL or GONE — the diff names the cell; before
  fixing, run the legacy gate that exercises that cell's live path to
  confirm the same regression is visible there too.
- The slice touches LIVE PATH dispatchers (`emit_flat_ir`, `emit_walk_codegen`,
  `dispatch_one_x86`, the WASM/JS/NET silo walkers) — these are NOT
  exercised by the synthetic single-node audit, so per-kind-diff can't see
  their regressions.  Run `test_crosscheck_icon.sh` + `test_smoke_snobol4_jit.sh`
  to cover the dispatcher path.
- The slice changes `g_emit` shape (new fields, renamed fields) — re-run
  full to confirm no follow-on damage to fields you didn't touch.
- The slice deletes any `emit_bb_x*` / `emit_sm_*` function — confirm the
  live path still resolves.

### Gate commands

```
GATE-PK bash scripts/test_per_kind_diff.sh                     # PRIMARY: per-(SM op × BB kind × backend × submode) byte-identity (per-slice)
GATE-M  bash scripts/test_gate_em_template_matrix.sh           # matrix structural invariant            (session-end / escalation)
GATE-E  bash scripts/test_gate_ec_uni_complete.sh              # beauty md5 + 9-gate roll-up             (session-end / escalation)
GATE-J  bash scripts/test_crosscheck_icon.sh                   # Icon three-mode incl. --run             (escalation: live-path dispatcher edits)
GATE-S  bash scripts/test_smoke_snobol4_jit.sh                 # SNOBOL4 three-mode --run≥186            (escalation: live-path dispatcher edits)
```

Legacy --interp-mode gates (KEEP for interpreter work, NOT for emitter work):
```
        bash scripts/test_smoke_icon.sh                        # PASS=5            --interp; INTERPRETER coverage only
        bash scripts/test_smoke_unified_broker.sh              # PASS≥23           --interp; INTERPRETER coverage only
        bash scripts/test_icon_all_rungs.sh                    # PASS=194          --interp; INTERPRETER coverage only
```

### Re-freezing the per-kind baseline

When a change is INTENTIONAL — refactoring template output, adding a new
backend cell, fixing a known-wrong emission — the per-kind diff will FAIL
because the baseline is stale.  In that case:
```
bash scripts/freeze_per_kind_baseline.sh                       # records current scrip output as the new oracle
bash scripts/test_per_kind_diff.sh                             # confirm post-freeze: PASS=N FAIL=0 NEW=0 GONE=0
```
Commit the regenerated `baselines/per_kind/` along with the source change.
The diff between old and new baseline IS the regression-test record of
what was intentionally changed — read it before committing to confirm
only the expected cells moved.


## Watermark

```
.github: (this commit — gate cadence change: per-kind-diff is the new primary
                     per-slice invariant; matrix + beauty demoted to session-end /
                     escalation per Lon directive 2026-05-21.  Verified clean at
                     one4all 9b905d26: PK PASS=399 FAIL=0, matrix 855/855,
                     EC-UNI-21 9/9.  Session Setup now includes a per-kind-diff
                     verification step.)
one4all: 9b905d26   (EC-UNI-PER-KIND-DIFF: honest 5-backend × submode geometry.
                     Refactored audit harness directory layout from <be>/<KIND>.<ext>
                     to <backend>/<submode>/<KIND>.<ext>.  Per Lon directive
                     2026-05-21: 5 backends total (x86, jvm, net, js, wasm); x86
                     has 3 sub-modes (text, binary_wired, text_macro_def); JVM
                     and .NET may grow binary sub-modes later; JS and WASM are
                     text-only by design.  Brokered entry/exit emissions are
                     a separate fixup layer, not a per-template concern.

                     Coverage at this commit:
                       BB:  97 kinds × 7 cells = 679 cells.
                            Cells per kind: x86/{text,binary,text_macro} +
                            jvm/text + net/text + js/text + wasm/text.
                       SM:  76 dispatcher-covered opcodes × 5 backend text cells = 380.
                       Total: 1059 cells per run.

                     Baseline at one4all 9b905d26:
                       PASS=399  STUB=660  FAIL=0  NEW=0  GONE=0
                       Footprint 3.4 MB (1.6 MB .raw + 1.6 MB .norm + 200 KB
                       manifest/asm-md5/stub overhead).

                     Per backend/submode size:
                       x86/text       748 KB (346 files)
                       x86/binary      84 KB (194 files)
                       x86/text_macro 132 KB (194 files)  ← new this commit
                       jvm/text       688 KB (346 files)
                       net/text       472 KB (346 files)
                       js/text        672 KB (346 files)
                       wasm/text      568 KB (346 files)

                     Regression detection verified empirically in new layout:
                       Inject ';canary' in emit_core.c bipush path →
                       FAIL=1 (jvm/text/SM_PUSH_LIT_I.j), exit=1.
                       Restore → FAIL=0, exit=0.

                     Predecessor one4all bb04e8e1 — same harness, flat
                     <be>/<KIND>.<ext> layout (now superseded).)
one4all: bb04e8e1   (EC-UNI-PER-KIND-DIFF harness landed.  tools/emit_per_kind_audit.c
                     plus scripts/{freeze_per_kind_baseline,test_per_kind_diff,normalize_per_kind_cell}
                     plus baselines/per_kind/ (3.3 MB committed).  scrip gains
                     --audit-per-kind <dir> subcommand; short-circuits the normal
                     compile pipeline and writes one file per (SM_op × backend) +
                     (BB_kind × backend) cell.

                     Coverage:
                       BB: 97 kinds × 6 backends (x86_text, x86_bin, JVM, JS, NET, WASM) = 582 cells.
                       SM: 76 dispatcher-covered opcodes × 5 text backends = 380 cells.
                       Total: 962 cells per run.

                     Baseline freeze at THIS commit:
                       PASS=384  STUB=578  FAIL=0  NEW=0  GONE=0
                       (384 of 962 cells emit real content today; 578 are
                       honest no-op stubs — both sides agree they emit nothing.)

                     Filter-then-diff pipeline (Lon directive 2026-05-21):
                       scripts/normalize_per_kind_cell.py canonicalizes per-cell
                       text output (strip comments, .L<digits>→.Lxxx,
                       _<sid>_<nid>→_S_N, large rodata-pointer decimals→ADDR).
                       Both raw and normalized form committed under
                       baselines/per_kind/<be>/<KIND>.<ext>.{raw,norm}.

                     Assemble-then-md5 (Lon's second idea):
                       baselines/per_kind/x86_text_assembled_md5.txt records
                       `as`-assembled .o md5 per x86_text cell where assembly
                       succeeds (17 of 22 PAT cells).  Cells that fail to
                       assemble due to synthetic-single-node unresolved label
                       refs are recorded as NOASM — honest limitation.

                     x86_bin special case: process-local addresses (memcmp@PLT,
                     rodata literal pointers) get baked into binary-mode
                     emission; ASLR randomizes them every run.  Bit-identity is
                     impossible by construction.  test_per_kind_diff.sh applies
                     a STRUCTURAL comparison for x86_bin cells — same byte
                     count = same instruction sequence shape.  Full byte-level
                     comparison for x86 should use the assembled-md5 path on
                     x86_text cells instead.

                     Regression detection verified empirically:
                       - inject `;canary` in jvm_push_int2 bipush path →
                         FAIL=3 (SM_PUSH_LIT_I, SM_PAT_CAPTURE_FN_ARGS,
                         SM_PAT_USERCALL_ARGS all reach bipush 42).
                         exit=1.
                       - restore → FAIL=0, exit=0.

                     This supersedes PLAN.md's EC-UNI-PER-KIND-DIFF row.
                     The harness exists; the next rung is EC-UNI-REFAITH —
                     for any kind whose live emit_bb_x* output differs from
                     the lifted template's output, re-lift byte-faithfully.
                     Coverage gate now exists; refaith work can proceed
                     against it.

                     NEXT after this watermark:
                     1. EC-UNI-REFAITH — re-lift FAILing kinds byte-faithfully
                        (the harness will tell us which).
                     2. EC-UNI-REWIRE-ALL — route emit_flat_ir through
                        emit_bb_node for IS_TEXT once per-kind diff is
                        100% PASS for the live path.
                     3. EC-UNI-NAMEKEY-BIN — name-keyed binary primitives;
                        delete emit_bb_x* originals.

                     Completeness over format-faithfulness: end state is one
                     template per kind for ALL kinds, dormant or not.)
one4all: d2b6dac3   (EC-UNI-REWIRE coverage audit landed.  scripts/test_audit_bb_x86_
                     exercise.sh walks corpus/programs/snobol4/ under --compile and
                     counts `# BOX <KIND>` banners per BB pat-kind.  Result across 177
                     files (1 segfault, 176 compile OK): LIT=9 files=8, SPAN=3 files=3,
                     POS=3 files=3, ANY=3 files=1, all other 13 kinds zero.  Audit
                     proves 4 of 17 BB pat-kinds flow through emit_bb_xstar/etc. in
                     current corpus; 13 are dormant.

                     Slice 1-7 history (045baf4a — see preceding watermark):
                     all 17 pat-level emit_bb_x* fn bodies physically inside
                     BB_templates/ files.  Live path UNCHANGED — emit_bb_node
                     does not yet fill g_emit fields, so emit_bb.c originals run.
                     Beauty byte-identical and matrix gate 855/855 throughout.

                     NEXT (Lon directive 2026-05-21 evening):
                     1. EC-UNI-PER-KIND-DIFF — author tools/emit_per_kind_audit.c +
                        scripts/test_per_kind_diff.sh: for each SM opcode and each
                        BB kind, synthetically construct an instance, emit via
                        legacy path AND template path, diff.  Per-kind PASS/FAIL
                        table replaces "hope corpus triggers kind" coverage.
                     2. EC-UNI-REFAITH — re-lift FAILing kinds byte-faithfully.
                     3. EC-UNI-REWIRE-ALL — route emit_flat_ir through emit_bb_node
                        for IS_TEXT once per-kind diff is 100% PASS.
                     4. EC-UNI-NAMEKEY-BIN — name-keyed binary primitives;
                        delete emit_bb_x* originals.

                     Completeness over format-faithfulness: end state is one
                     template per kind for ALL kinds, dormant or not.  Dead-code
                     deletion (Path c) ruled out by Lon directive.)
one4all: 045baf4a   (EC-UNI LIFT Snocone-shape slices 1-7.  CORRAL of all
                     known pat-level emit_bb_x* bodies COMPLETE.  Slices 1-4
                     (44e41588) corraled the 14 active emit_bb_x* fns.  Slices
                     5-7 (3e2d982f → 5ad56a4b → 045baf4a) finish the trailing
                     three: xarbn, xeps, xbrkx (dead).  Live path UNCHANGED —
                     emit_bb_node does not yet fill g_emit fields, so originals
                     in emit_bb.c are still the live path.  Beauty byte-identical
                     proves no harm at every step.

                     Slice 5 (3e2d982f) — bb_arbno.c IS_X86 arm filled with
                       emit_bb_xarbn body.  Reads g_emit.child_fn + lbl_*.
                       No new template file; bb_arbno.c already had JVM/JS/NET
                       arms.  Both IS_TEXT and IS_BIN sub-branches mirrored.
                     Slice 6 (5ad56a4b) — new bb_eps.c, corrals one-line
                       emit_bb_xeps.  No BB_op_t dispatch slot (EPS is the
                       NULL-node case in emit_flat_ir, like bb_charset_helper).
                       Matrix 845 → 850.
                     Slice 7 (045baf4a) — new bb_brkx.c, corrals emit_bb_xbrkx
                       (dead in both places — declared but uncalled).  IS_TEXT
                       only, no IS_BIN fork (mirrors original).  Matrix 850 → 855.

                     Slice 4 inventory (held over for reference):
                       - g_emit fields: child_fn (void *), op_name1, op_name2,
                         op_kind — per-op parameters from emit_bb_x* signatures.
                       - un-static of emit_bb_ptr_slot, child_cache_get_lbl,
                         g_cap_fixup_cb in emit_bb.c.
                       - bb_label_from_name() scaffolding in bb_template_common.h.
                       - bb_charset_helper.c (emit_bb_charset).
                       - bb_capture.c (xcallcap/xfnme/xnme combined).
                       - bb_fence.c (xfnce).
                       - bb_dsar.c (xdsar / DEREF).
                       - bb_atp_template.c (xatp / USERPAT).

                     Status: 17/17 pat-level BB-x86 fn bodies physically in
                     templates (14 active from slices 1-4 + xarbn + xeps + dead
                     xbrkx).  Matrix gate 855/855 after slice 7.  Beauty stays
                     at md5 0c192b2f26fd1288e19c21614af95218 (--interp) and
                     40df9e004c3e963c99af716c65f2c970 (--compile) throughout.

                     Remaining pat-level x86 emission not yet in BB_templates/:
                       - emit_flat_ir_alt  (file-static control-flow helper)
                       - emit_flat_ir_cat  (file-static control-flow helper)
                       - emit_flat_ir_fence (file-static control-flow helper)
                     These three are dispatcher-style helpers, not Byrd-box
                     bodies; corraling them belongs to a separate slice when
                     we tackle control-flow assembly extraction.

                     Slice trail: 9b5ba0b6 → 869b397a → 56b5afb6 → b496198c →
                     8b2f65e1 → a6a3b736 → 99630c7e → 71bd8b6f → 1a9571fe →
                     90235416 → 87d11afc → 44e41588 → 3e2d982f → 5ad56a4b →
                     045baf4a.

                     NEXT: wire emit_bb_node to fill g_emit fields per BB node
                     kind, then call the template fn (which now contains the
                     proper x86 body).  Once the template path emits byte-for-
                     byte identical output, delete the originals in emit_bb.c.
                     Then mirror this whole sweep on the SM side
                     (~70 SM fns from emit_sm.c into sm_*.c templates).)
corpus:  5fc1427    (demo/beauty/ canonical; beauty_suite/ apparatus separated)
.github: (this commit — record EC-UNI LIFT PATTERN block + watermark refresh + handoff)
smoke icon:    5/0    smoke prolog: 5/0    smoke rebus: 4/0
smoke raku:    5/0    smoke snobol4: 7/0    smoke snocone: 5/0
broker:        23/26
icon rungs:    194/36/35
matrix gate:   830/830 PASS  (was 450/450 pre-99630c7e; now 110 files / 166 fns / 830 cells)
firewall lower:   9/6   firewall runtime: 16/8   firewall stage2: 10 (token gate)
beauty.sno --compile md5:           40df9e004c3e963c99af716c65f2c970  (882901 bytes)
beauty.sno --compile assembled .o:  3adbb73f88edcc5416d38baade6faf97  (494336 bytes)
                                    EC-UNI-14(c)(5) — flag removed; one path only.
emit_io self-test: 6/6 PASS
EC-UNI-14 ladder closed: 14-PREREQ d6e5c8f1 -> 14(a) 66cf8506 -> 14(b) dc4e6a9d/5dc52dd4/fe195613.
                  EC-UNI-14(c)(1..7): 90557fbe -> 098a03ba -> c599bbab -> 46e8c531 ->
                                       862f817a -> c081758f -> 9b5ba0b6.
                  EC-UNI-14 proper SM-side + BB-side: CLOSED.  EC-UNI-21 CLOSED (close gate
                  scripts/test_gate_ec_uni_complete.sh, 9/9 PASS on HEAD).  M1 oracle DRIFTED
                  (current md5 9cddff2534472b822438801d8db58a99, 622 lines, vs M1 baseline
                  abfd19a7..., 646 lines) — EC-UNI-21-followup tracks reconcile vs retire.
                  Remaining open in EC-UNI: EC-UNI LIFT sweep (~70 SM + ~12 BB fns still
                  unmoved), then EC-UNI-17/18/19/20/21-followup/22.
beauty.sno in corpus: ONE — programs/snobol4/demo/beauty/beauty.sno (627 lines,
                            md5 5be1de188af42be42e15e6d9a552f759, self-contained).
                            Subsystem apparatus at programs/snobol4/beauty_suite/.
```

---

## Active rungs

### EC-UNI — unify all walkers; one fn per opcode/kind, one arm per backend

**Target:** one fn per SM opcode, one fn per BB kind, each with five `if (IS_<BE>)` arms (X86/JVM/JS/NET/WASM). Text-vs-binary hides inside each arm. After completion, `emit_walk_codegen`/`emit_jvm_from_sm`/`emit_js_from_sm`/`emit_net_from_sm`/`emit_wasm_from_sm`/`dispatch_one_x86` all delete. "Fix backend X for opcode Y" becomes "open `sm_<y>.c`, edit the `IS_X` arm."

**Three-layer cake:**
- **Layer 1** — top-level templates `SM_templates/sm_<op>.c` / `BB_templates/bb_<kind>.c`. Signature `void sm_<op>(void)` / `void bb_<kind>(void)`. Reads `g_emit.*`. Branches ONLY on `IS_<BE>`. Verbose and explicit — literal output strings visible in every arm.
- **Layer 2** — per-backend `static` helpers in the same file.  **Deferred.**  Per Lon directive (2026-05-20), templates currently carry raw output with no static helpers and no cross-template factoring (beyond pre-EC-UNI helpers like `jvm_class_hdr`/`net_alpha_hdr` that predate this work).  Layer 2 extraction was previously planned at EC-UNI-16; that rung is closed-by-supersession.  Future expansion to one-source-line-per-output-line happens after the whole template body is in place (Phase B), not as a REDUCE phase.
- **Layer 3** — string-builder primitives in `src/emitter/emit_io.{c,h}`: `emit_text`/`emit_textf`/`emit_byte`/`emit_bytes`. Funnel for all output.

**`g_emit` single global** (in `emit_globals.{c,h}`) carries all per-template state. Not re-entrant. Snocone bootstrap maps 1:1 to flat `DATA('Sm_emit(...)')` declaration.

---

### ⚡ EC-UNI LIFT PATTERN — read this before touching any template

**Lon directive (2026-05-21, supersedes 2026-05-20):** *"I will stand down on my directive to slap the code in.  If you feel there is a better way go back to that.  It was just too slow before, but now I think it was due to too much regression testing.  Go back to doing your methodical approach which you had before I redirected you to start slapping one around."*

**Root cause of prior slow pace identified:** the per-slice work itself was fine; the friction was running the full regression suite per slice when only the fast-cycle gates (build + matrix + beauty md5) were needed.  The per-slice fast cycle directive (above) addresses that.  The pace problem was a gate-cadence problem, not a methodology problem.

**The job (restored methodical form):** for each x86 codegen fn still living in `src/emitter/emit_sm.c` or `src/emitter/emit_bb.c`, lift it into the matching template's `IS_X86` arm in a way that respects existing abstraction boundaries.  Where a fn's body is self-contained (calls only widely-visible helpers like `insn_*`, `emit_label_define`, `emit_outf`, `bb3c_format`), copy-paste the body verbatim — that path is canonical for the BB-side slices 1-7.  Where a fn's body depends on file-static plumbing (e.g. `render_call_line`, `sm_template_lookup`, `emit_sm_args_t` inside `emit_sm.c`), do NOT un-static the dependencies just to fit the verbatim-paste recipe — those file-static helpers ARE the abstraction the template is supposed to call through, and the existing one-line wrapper (`if (IS_X86) return emit_sm_jump_line(out, instr, 0);`) is the correct shape.  In that case, recognize the lift has already happened: the template owns the dispatch decision, and the named C function is the helper, not the body.

**Mechanical recipe (per fn):**

1. Identify the fn.  Examples: `emit_bb_xstar` (BB_PAT_REM), `emit_bb_xlnth` (BB_PAT_LEN), `emit_bb_xchr` (BB_PAT_LIT), `emit_bb_charset` (BB_PAT_SPAN/ANY/BREAK/NOTANY), `emit_sm_concat_dispatch` (SM_CONCAT), `emit_sm_jump_line` (SM_JUMP), etc.
2. **Inspect the body before lifting.**  Does it call only file-public helpers and standard runtime functions?  If yes — proceed to verbatim copy-paste (steps 3-6 below).  Does it call file-`static` helpers in the same `emit_sm.c` / `emit_bb.c`?  If yes — the wrapper is the abstraction; mark the fn as "already-lifted-as-helper" and move on to the next.  Do NOT un-static the file-private machinery to force a verbatim paste.
3. Find the matching template file: `BB_templates/bb_<kind>.c` or `SM_templates/sm_<op>.c`.  The stub line `if (IS_BIN) return; /* x86 binary: emit_flat_body path, not emit_bb_node */` (BB templates) or the `if (IS_X86) return emit_sm_<op>_dispatch(out, instr, 0);` line (SM templates) marks where the lifted body lands.
4. **Copy the entire fn body** into the template's `if (IS_X86) { ... return; }` arm.  Preserve the original local variable names; just rewrite parameters as reads from `g_emit`:
   - `s`/`f`/`b` (succ/fail/back labels) → `g_emit.lbl_succ` / `g_emit.lbl_fail` / `g_emit.lbl_back`
   - `n` (LEN/TAB count) → `nd->ival` (where `nd = g_emit.node`)
   - `lit` (PAT_LIT string) → `nd->sval`
   - `out` → `g_emit.out` (or local `FILE * o = emit_outf();` as the lifted body already does)
5. **Helpers stay where they are.**  `emit_bb_box_banner`, `bb3c_format`, `emit_outf`, `emit_label_define`, `insn_*`, `emit_store_delta`, `emit_jmp`, `emit_seq_bounds_len`, `emit_add_delta_imm`, `TEMPLATE_ADDR_SIGLEN`, `JMP_*` — all stay in their current files.  Many will be deleted in the next pass anyway.  **Do not move helpers.  Do not extract helpers.  Do not factor across templates.**  Just link against them.
6. Leave the original fn in `emit_bb.c` / `emit_sm.c` for now.  The dispatcher (`emit_flat_ir` or `emit_walk_codegen`) still calls the old fn; two paths coexist temporarily.  Rewire/delete happens after the lift sweep is complete.
7. Per-slice fast cycle ONLY: `make -j4 scrip` → `scripts/test_gate_em_template_matrix.sh` → `scripts/test_gate_ec_uni_complete.sh`.  Commit.  Full regression at session-end only.

**Canonical example landed:** one4all `71bd8b6f` lifted `emit_bb_xstar` → `bb_rem` IS_X86 arm and `emit_bb_xlnth` → `bb_len` IS_X86 arm.  `g_emit` gained three label fields: `lbl_succ`, `lbl_fail`, `lbl_back` (in `src/emitter/emit_globals.h`).  Read those files for the canonical shape.

**What NOT to do (mistakes recorded across both directives; do not repeat):**
- Do NOT extract a `static` helper inside a template that collapses two opcodes into one body (slice 1, reverted in `8b2f65e1`).
- Do NOT add Layer-2 helpers in `emit_core.c` that factor a common pattern across multiple templates (slice 2, reverted).
- Do NOT enforce or measure "fn fits on a screen" — that rule was removed (2026-05-20).
- Do NOT un-static file-private machinery in `emit_sm.c` / `emit_bb.c` just to fit the verbatim-paste recipe — the wrapper IS the lift in that case.  (Added 2026-05-21.)
- Do NOT run the full regression suite per slice.  The fast cycle (build + matrix + beauty md5) is the per-slice gate; full crosscheck/smoke gates are session-end only.  (Added 2026-05-21 — this was the source of slow pace, not the methodology.)
- Do NOT touch the matrix gate's same-file-helper-delegation logic — there are no template-local helpers in the consolidation phase.

**What "complete" means here:** every x86 codegen fn that lives in `emit_bb.c` or `emit_sm.c` is either (a) copy-pasted into its matching template's `IS_X86` arm, or (b) recognized as an already-extracted file-public helper that the template calls through.  After the lift sweep, the rewire/delete pass will:
- Update `emit_flat_ir` / `emit_walk_codegen` to call the templates directly (via `emit_bb_node` and `emit_sm_dispatch`).
- Delete the originals that were case (a); keep the helpers from case (b).
- Trim now-unreachable helpers.
- That's "Phase B" expansion (one-source-line-per-output-line) territory.

**Lift queue, after 2026-05-21 audit:**

**BB-side (in `emit_bb.c`): COMPLETE through slice 7 (one4all `045baf4a`).**  All 17 pat-level `emit_bb_x*` fns physically inside `BB_templates/` files.  Remaining x86 emission in `emit_bb.c` is the dispatcher-style control-flow trio `emit_flat_ir_alt` / `emit_flat_ir_cat` / `emit_flat_ir_fence`; these are NOT Byrd-box bodies and belong to a separate control-flow-assembly slice, not the lift sweep.

**SM-side (in `emit_sm.c`): the apparent "~62 unmoved fns" was a 2026-05-20 mis-classification.**  Audit (2026-05-21) of the 36 `emit_sm_*_(dispatch|line|template)` fns by body size and dependency:
- 31 are 1-11 line wrappers that marshal args from `SM_t *ins` into `emit_sm_args_t` and call `render_call_line(out, sm_template_lookup(SM_<OP>), &a)` (or `emit_sm_noop` / `emit_sm_int64` / `emit_sm_lbl` family).  All depend on `emit_sm.c`'s file-private machinery: `sm_op_template_t` type, `emit_sm_args_t` type, `sm_template_lookup`, `render_call_line`, `build_args_col`, `g_pending_pc_label`, `bb3c_format`.
- 5 are larger (18-77 line) bodies — `emit_sm_exec_stmt_template`, `emit_sm_return_variant_dispatch`, `emit_sm_bb_pump_proc_dispatch`, `emit_sm_define_dispatch`, `emit_sm_define_entry_dispatch`.  Same dependency on file-private machinery.

The `sm_op_template_t` type and `render_call_line` machinery in `emit_sm.c` IS the SM-side macro-rendering abstraction; the templates' `if (IS_X86) return emit_sm_<op>_dispatch(out, instr, 0)` line IS the lift.  These fns are already-lifted-as-helper per the criterion above; no SM-side body lifting work remains.

**Verification per commit:** matrix gate stays at 855/855; beauty.sno --compile md5 stays at `40df9e004c3e963c99af716c65f2c970` (byte-identical — the lifts add code paths but don't change output until the dispatcher is rewired).

---

**Scope inventory:** SM has 91 opcodes in the enum, 76 dispatched by `emit_sm_dispatch` (the other 15 are runtime/sentinel — BB-bridge `_PROC` variants, frame/global ops, compare aliases, `SM_SUSPEND`/`SM_OPCODE_COUNT` — not template work).  BB has 97 kinds in `BB_op_t`; **all 97 are dispatched by `emit_bb_node` and have template slots** as of one4all `99630c7e` (21 pattern + Prolog kinds carry real code, 76 are honest no-op stubs awaiting Phase B per-backend codegen).  Walkers delete after coverage lands: net −2500 to −3500 LOC.

**Unblocks Phase B:** five per-backend GOAL files (`GOAL-SN4-X86-EMIT` [new], `GOAL-SN4-JVM-EMIT`, `GOAL-SN4-JS-EMIT`, `GOAL-SN4-NET-EMIT`, `GOAL-SN4-WASM-EMIT`).

Closed sub-rungs trail: EC-UNI-10..13(e), 14-PREREQ, SUSPEND_VALUE fix, 14(a), 14(b), 14(c)(1..7), 15, 16 (closed-by-supersession), 21.
See git log for per-commit detail.

---

### ⚡ EC-UNI-REWIRE — BB-side: route x86 through emit_bb_node, not direct emit_bb_x* (2026-05-21)

**Status:** OPEN — substantive design question requires Lon direction before code lands.

**Context.**  BB-side LIFT (slices 1-7) is complete: all 17 pat-level `emit_bb_x*` fn bodies are physically in `BB_templates/bb_*.c` IS_X86 arms.  The watermarked NEXT step is to *use* them — route x86 emission through `emit_bb_node` instead of `emit_flat_ir` → `emit_bb_x*` direct calls.

**Today's live path for x86:**
- `emit_flat_body(nd, prefix, ...)` (in `emit_bb.c`) is the x86 driver.  Computes `bb_label_t lbl_succ`/`lbl_fail`/`lbl_β` on the stack.
- Calls `emit_flat_ir(nd, &lbl_succ, &lbl_fail, &lbl_β)`.
- `emit_flat_ir` switches on `nd->t` and calls `emit_bb_xstar(lbl_succ, lbl_fail, lbl_β)` / `emit_bb_xlnth(...)` / etc. — passing `bb_label_t *` directly.
- Templates' IS_X86 arms are dormant: they reconstruct `bb_label_t` from `g_emit.lbl_*` names via `bb_label_from_name()`.

**The fork: text mode vs binary mode in JIT.**

The deliberate design choice in `emit_globals.h:44-50` is that `g_emit.lbl_*` are **name strings**, not `bb_label_t *` pointers.  Rationale: "the label *name* is the Snocone-translatable identity, since in Snocone a label is identified by a name string and its offset is looked up in a name-keyed table.  C strings are the one admitted pointer type here because Snocone strings transliterate to const char *."

Text mode (`--compile`) tolerates name-only labels: offsets are resolved by name in a later assembler pass.  Binary mode (`--run` / JIT) does NOT — it patches `bb_label_t` struct offsets in place during emission.  `bb_label_from_name()` creates a fresh stack-local struct; the patching is lost (`bb_template_common.h:21-23` documents this explicitly: *"Side-effects on the bb_label_t (offset patching) survive only within text-mode templates; binary-mode handling will need name-keyed primitives in a future sweep."*).

**Two paths forward, Lon's choice:**

**Path (a) — Text-first staged rewire.**  Rewire `emit_flat_ir` to fill `g_emit.lbl_*` names + `g_emit.child_fn` + call `emit_bb_node` ONLY when `IS_TEXT` (i.e. `--compile`).  Keep binary mode (`--run`) on the legacy direct-call path until name-keyed binary primitives exist.  Cost: temporary two-path code (text via template / binary via legacy) — explicit, time-boxed.  Verification: beauty.sno --compile md5 byte-identical; `--run` corpus unchanged because the binary path is untouched.  Unblocks: deleting the text-half of the original `emit_bb_x*` fns once the rewire lands.  Does NOT unblock final deletion of `emit_bb_x*` until path (b) also lands.

**Path (b) — Name-keyed binary primitives first.**  Build a name-keyed analog to the offset-patching binary primitives (e.g. `emit_seq_port_call_by_name`, `emit_jmp_by_name`).  Then rewire `emit_flat_ir` for BOTH modes in one go.  Cost: substantial new binary-emit primitive work BEFORE any visible progress on the rewire; the offset-patching state machine in `bb_label_t` is intricate.  Unblocks: clean single-path rewire and full deletion of `emit_bb_x*` originals.

**Recommendation pending Lon decision:** Path (a).  Text-mode rewire is byte-identical-verifiable via the existing EC-UNI-21 gate (`scripts/test_gate_ec_uni_complete.sh`); binary-mode work can proceed in parallel as a separate rung (`EC-UNI-NAMEKEY-BIN`) without blocking text-mode progress.  The two-path interlude is small and the rewire dependency graph becomes a DAG instead of a single critical path.

**Why this is NEXT and not a slice 8 lift:** the SM-side audit (2026-05-21) confirmed no SM body-lifting remains; all `emit_sm_*_(dispatch|line|template)` fns are already-lifted-as-helper.  The BB-side LIFT is complete through slice 7.  The next step IS the rewire — there's no more lift work to delay it with.

**⚠ Format-drift finding (2026-05-21, blocks Path (a) execution).**

Even Path (a) (text-only rewire) does NOT produce byte-identical text output today.  Verified by direct read of the lifted vs original code paths for `BB_PAT_REM`:

- Original `emit_bb_xstar` IS_TEXT path emits jumps via `bb3c_format(out, "", "jmp", target)` — action column 2 gets "jmp", goto column 3 gets the target name.  `bb3c_write_line` pads L=24, A=16, then writes target into col 3.
- Template `bb_rem` IS_X86 emits jumps via `emit_text_jmp(target, JMP_JMP)` → `bb3c_emit_jmp(out, "jmp", target)` (`emit_core.c:589`).  That function builds `rest = pad("", 27) + "jmp " + target` and calls `bb3c_format(out, "", "", rest)` — action column is EMPTY, all of "jmp <target>" goes into col 3.

The two paths produce **demonstrably different column layouts** for every jump.  Empirical confirmation: beauty.sno only exercises POS among the pat-level emissions (one `# BOX POS(0)` in 882901 bytes of output), but the same `emit_text_jmp` substitution exists across all 17 lifted templates — so a fuller corpus (programs that exercise REM/LEN/CAT/etc.) would surface the drift even if beauty.sno alone might be lucky.

Same finding applies to `emit_text_label` vs `emit_label_define`: original uses `emit_label_define(b)` which patches the offset into the `bb_label_t` struct AND writes the label line in text mode.  Template uses `emit_text_label(name)` which writes a text label line but cannot patch the struct (because the template only has the name).  Text output may still be byte-identical IF `bb3c_format(out, label_col, "", "")` writes identical bytes to whatever `emit_label_define` does in text — needs verification per-helper.

**This means Path (a) requires one of:**

**Path (a.1)** — Re-lift the templates preserving the EXACT original `bb3c_format(out, "", "jmp", target)` calls verbatim (and `emit_label_define` calls verbatim, taking a reconstructed `bb_label_t` via `bb_label_from_name`).  The templates' current `emit_text_jmp`/`emit_text_label` substitution is a faithful refactoring that nonetheless changed bytes.  Pure mechanical: the lifted bodies become byte-faithful to the originals at the cost of reading less cleanly.

**Path (a.2)** — Re-baseline the EC-UNI-21 gate's expected md5 to the post-rewire output, with a one-time documented drift commit.  This makes the rewire visible (md5 changes) but accepts the new output as canonical.  The change is purely cosmetic (jmp/label column layout); semantically identical assembly is produced and the assembled `.o` md5 should be unchanged.  EC-UNI-21 gate already tracks both source md5 AND assembled `.o` md5 (`3adbb73f88edcc5416d38baade6faf97`); the assembled md5 is the semantic ground truth.

**Recommendation:** Path (a.2).  The assembled `.o` md5 is what actually matters for correctness; the text md5 is a useful invariant but ultimately a presentation choice.  One-shot re-baselining keeps the rewire small and forward-progress; re-lifting all 17 templates to preserve text format would re-do existing work for cosmetic reasons.  Confirm with Lon before re-baselining.

**Why this finding only surfaces now:** the templates' IS_X86 arms have been dormant since slice 1 (`9b5ba0b6`).  The matrix gate (`test_gate_em_template_matrix.sh`) confirms each backend arm EXISTS but does not check byte-identity of output (because the templates aren't called).  EC-UNI-21 confirms the LIVE path (legacy `emit_bb_x*`) byte-output, which has been unchanged.  The drift was structurally invisible until someone read the lifted templates against the originals — which this session is the first to do for the rewire purpose.

**Net:** Path (a.2) likely.  But Lon must choose between (a.1 — re-lift faithfully) / (a.2 — re-baseline gate) / (b — name-keyed binary primitives first, side-stepping the question) before code lands.

**⚠ Coverage finding (2026-05-21 PM, deepens the rewire blocker).**

Empirical inspection of beauty.sno's `--compile` output (882901 bytes) shows **only ONE `# BOX` banner total: `# BOX POS(0)`**.  The other 16 BB pat-level kinds (REM, LEN, ARB, CAT, ARBNO, etc.) produce zero banners in beauty's output despite REM and other pattern primitives appearing in the source.

Root cause: `--compile` lowers most pattern uses to SM macro calls (`PAT_REM`, `PAT_LEN` text macros + `PUSH_VAR .S430 # REM` keyword lookups), NOT to BB graphs that flow through `emit_flat_ir` → `emit_bb_xstar`.  BB-lowering is gated by the invariant-pattern optimizer in `emit_sm.c` (`g_pat_windows[i].is_invariant`) — it fires only for patterns the compiler can statically prove are runtime-invariant.  In beauty.sno, that's just one POS(0).

Implications:
1. **The EC-UNI-21 gate (beauty md5) has been structurally insensitive to 16/17 BB-side LIFT slices**.  Slices 1-6 lifted bodies for REM, LEN, CAT, ARB, FENCE, ARBNO, FAIL, FARB, TB, RTB, LIT, capture-family, charset, DSAR, ATP, EPS — none of these are exercised by beauty.sno's --compile output.  Only `bb_pos` (slice that lifted POS) is in the actually-tested set.
2. **The matrix gate (855/855) confirms templates EXIST but does NOT confirm they EMIT CORRECT bytes** — the lifted code paths are dead for all 16 non-POS kinds.  The matrix gate is a structural invariant (no missing arm), not a behavioral one.
3. **The rewire under any path (a.1/a.2/b) needs a coverage gate that actually exercises the BB-lower path for each pat-level kind**.  Without it, a "byte-identical" verification is misleading: the rewire could leave 16 kinds silently broken in `--compile` and the gate would still pass.

**Possible next pre-rewire rung:** `EC-UNI-COVER-PAT` — author a `corpus/programs/snobol4/feat/invariant_patterns.sno` that forces invariant lowering of REM, LEN, ARB, CAT, ARBNO, etc., one pattern per statement.  Run under `--compile` and `--run`; record `.s` md5 and assembled `.o` md5 per kind.  This becomes the actual regression gate for the rewire.  Without this, any "passes the gate" claim about the rewire is empty.

Alternative: scan `corpus/crosscheck/` for existing `.sno` files that already exercise enough BB-lowering to be useful — `test_crosscheck_x86_full_corpus.sh` does end-to-end execute/diff testing, but its `.ref` comparison is on stdout, not on emitted `.s` text.  It catches semantic regressions, not text format drift.  Likely useful for verifying Path (b) once name-keyed primitives exist, less useful for verifying Path (a.x).

**Net (revised):** the rewire is blocked on TWO open questions: (1) Lon's choice between (a.1)/(a.2)/(b), and (2) a coverage gate that actually exercises the 17 lifted paths.  Both should be answered before code lands.

**⚠ Deeper coverage finding (2026-05-21 evening, deepens the prior coverage finding).**

Empirical probe: a minimal test program `S = 'hello world' \n S POS(0) REM :F(FAIL)` (REM in general-expression context with no `.` capture) compiles via `--compile` without segfault, but its output uses `PUSH_VAR .S2 # REM` followed by `PAT_DEREF` — NOT `SM_PAT_REM`.  The runtime keyword-lookup machinery handles REM at execution time via the variable name, not the parser's `TT_REM` token.

Investigation in `src/lower/lower.c:375` shows `case TT_REM: SM_emit(g_p, SM_PAT_REM)` lives inside `lower_pat_expr` — a function called only when the AST node is **already known to be a pattern context**.  The parser+lexer mostly emit REM as a general variable lookup (`TT_VAR` with name "REM"), which the runtime keyword machinery dispatches.  Only AST nodes that the parser explicitly marks as pattern-expression children flow through `lower_pat_expr` and reach `SM_PAT_REM`.

Result: across simple SNOBOL4 programs that name REM, the `SM_PAT_REM` opcode emission path is rare.  And since `--compile` then needs the invariant-pattern optimizer in `emit_walk_phase2` to fire (which requires all stack values be non-variant), the cascade is: source must hit the pattern-expression AST → must hit `SM_PAT_REM` opcode → must be in a window where no `PUSH_VAR` flagged the window as variant → must pass `emit_flat_invariant` check.  That's a narrow gate.

**This means `emit_bb_xstar` may be near-dead in practice for current SNOBOL4 corpus.**  Same likely holds for `emit_bb_xlnth`, `emit_bb_xtb`, etc.  The previous "1 of 17 BB kinds exercised in beauty.sno" finding is even more dramatic in light of this: it may be more like "1 of 17 BB kinds exercised across all current SNOBOL4 corpus under --compile".

**Implications for EC-UNI work:**
- The matrix gate (855/855) confirms templates exist; the EC-UNI-21 gate confirms beauty.sno's --compile output (which uses ≤1 BB kind).  Together they offer little coverage of the BB-x86 lifted bodies.
- The slices that lifted bodies for REM/LEN/CAT/ARBNO/etc. may have introduced bugs that no current gate detects, because no current corpus program reaches those code paths.
- An accurate `EC-UNI-COVER-PAT` corpus is harder to author than initially proposed: it must construct programs that the SNOBOL4 parser+lower will recognize as pattern-expression contexts (e.g., via explicit `&PATTERN` declarations or specific syntactic forms), then exercise each BB pat-kind through that path, then trip the invariant optimizer.  Each of those is a separate constraint.

**Lon-decision matrix expanded:**
- Path (a.1) — re-lift faithfully — possible but unverifiable without `EC-UNI-COVER-PAT`.
- Path (a.2) — re-baseline gate — same: re-baselined to what? Beauty.sno output that exercises 1 kind?
- Path (b) — name-keyed binary primitives first — also unverifiable without coverage.
- **Path (c) — newly visible** — investigate first WHETHER `emit_bb_xstar` etc. are actually live anywhere.  If they're vestigial relative to the current SNOBOL4 frontend, the rewire question changes shape: there may be no rewire to do, just dead-code removal.  This is the GOAL-HEADQUARTERS analogue of the SN_INCR/SN_DECR observation in EC-UNI-14(c)(5)'s side-effects list ("vestigial — emitted only by sm_interp_test.c; no live frontend lowers either today").

Recommendation: pause the rewire entirely.  Author a coverage probe instead — `scripts/test_audit_bb_x86_exercise.sh` that runs each `corpus/` SNOBOL4 program under `--compile` and counts `# BOX ` banners by kind.  This reveals empirically which BB pat-kinds reach `emit_bb_xstar` etc.  Decision (a.x vs b vs c) becomes data-driven from that audit.

**Audit landed and run (one4all `d2b6dac3`, 2026-05-21 evening).**

Across 177 .sno files in `corpus/programs/snobol4/` (1 segfault, 176 compile OK), only 4 of 17 BB pat-kinds emit any `# BOX` banner: LIT (9), SPAN (3), POS (3), ANY (3).  The other 13 — REM, LEN, CAT, ARBNO, ARB, BREAK, NOTANY, RPOS, TAB, RTAB, FENCE, ABORT, ASSIGN_IMM, ASSIGN_COND — emit zero banners.  Their lifted bodies in `BB_templates/` are dormant in current corpus exercise.

**Lon directive 2026-05-21 evening — the end state is one template per kind for ALL kinds, dormant or not.**  Completeness is the priority, not format-faithfulness.  The 13 dormant kinds stay in `BB_templates/` and get rewired through `emit_bb_node` like the 4 live ones; corpus exercise level is not the criterion for which kinds get a template.  This rules out Path (c) (vestigial deletion) — even dormant code needs to flow through the unified template path.

**The verification problem this leaves:** the existing gates (EC-UNI-21 = beauty, smoke tests, JIT corpus) only naturally exercise 4 of 17 BB kinds in the source corpus.  How do we verify that the rewire of the 13 dormant kinds produces correct emission?

**Lon directive 2026-05-21 evening (verification):** *"Emit all SM and BB once and just compare the outputs."*

**Plan: per-kind unit regression `EC-UNI-PER-KIND-DIFF`.**  Author a test program (likely `tools/emit_per_kind_audit.c` driven by `scripts/test_per_kind_diff.sh`) that, for every SM opcode and every BB kind:

1. Constructs a minimal synthetic instance: a `BB_t` of the right kind with stub child/`ival`/`sval`/`value` fields filled, OR an `SM_t` of the right opcode with stub `a[]` operands.
2. Runs the **legacy path** (`emit_bb_xstar` / `emit_sm_*_dispatch` called directly with synthetic `bb_label_t` and `FILE *`) and captures the text output to `/tmp/legacy_<kind>.s`.
3. Runs the **template path** (fill `g_emit.lbl_*` / `g_emit.node` / `g_emit.instr`, call `emit_bb_node(nd, out)` or `sm_<op>()` directly) and captures to `/tmp/template_<kind>.s`.
4. `diff` the two; record per-kind PASS/FAIL.

Output: a 91-row SM table + a 17-row BB pat-kind table (plus the 76 stub BB kinds, expected uniformly empty-vs-empty PASS) showing per-kind byte-identity.  The 4 live kinds are exercised redundantly by EC-UNI-21 + smoke + crosscheck; the 13 dormant kinds are exercised for the FIRST time here.  Per-kind failures pinpoint exactly which template bodies drifted from their originals.

This gate replaces the "hope a corpus program triggers the kind" approach with **direct per-kind exercise**.  Coverage becomes total over the SM × BB opcode × kind matrix, not a function of what corpus happens to exist.

**Implementation sketch (subject to refinement):**

- `tools/emit_per_kind_audit.c` — a standalone C program linked against the emitter / runtime, no SNOBOL4 frontend.  For each kind:
  - Build synthetic instance with placeholder operands (constant strings "TEST", labels "L_succ" / "L_fail" / "L_back", `ival=0`, etc.).
  - Save current `g_emit` snapshot.  Set `bb_emit_mode = EMIT_TEXT`.
  - Call legacy fn → `/tmp/per_kind/legacy_<kind>.s` (closing the FILE).
  - Reset `g_emit`.  Call template fn (via `emit_bb_node` for BB, direct `sm_<op>()` for SM with `g_emit.instr` set).
  - `/tmp/per_kind/template_<kind>.s`.
  - Restore `g_emit`.
- `scripts/test_per_kind_diff.sh` — runs the C audit, diffs each pair, reports PASS/FAIL counts, writes per-kind .diff files for inspection.
- One-time baseline run records expected drift per kind in `tools/per_kind_baseline.csv` (commit-tracked).  Subsequent runs compare against baseline — any new drift fails the gate.

**Sequencing of next rungs:**

1. **`EC-UNI-PER-KIND-DIFF` (proposed, NEXT)** — author the per-kind unit audit.  Run it on `045baf4a` baseline to measure existing drift per kind.  Result: a per-kind PASS/FAIL table that documents the *current* template-vs-original divergence for each of the 17 BB pat-kinds and 91 SM opcodes.  Many will FAIL on text-format drift (template uses `emit_text_jmp`, original uses `bb3c_format(out,"","jmp",t)`); a few may FAIL on substantive bugs that have been invisible until now.
2. **`EC-UNI-REFAITH` (proposed, post-DIFF)** — re-lift the FAILing kinds to byte-faithfully match the original.  No format-drift acceptance, no gate re-baselining — the per-kind diff is the gate, and the gate must show 100% PASS.  This is Path (a.1) from the earlier matrix, but now scoped to *exactly the kinds that need it* per the DIFF result.
3. **`EC-UNI-REWIRE-ALL`** — with per-kind diff at 100% PASS, route `emit_flat_ir` through `emit_bb_node` for all kinds in IS_TEXT mode.  Routine: same code path goes through templates from now on.
4. **`EC-UNI-NAMEKEY-BIN`** — name-keyed binary primitives for `--run` mode; rewire binary too; delete `emit_bb_x*` originals.

---

#### Open sub-rungs

- [x] **EC-UNI-14 proper (SM-side + BB-side, CLOSED 2026-05-20)** — Ladder of six commits
  (`90557fbe -> 098a03ba -> c599bbab -> 46e8c531 -> 862f817a -> c081758f`):

  | step | commit | what |
  |------|--------|------|
  | (c)(1) | `90557fbe` | flip SCRIP_UNIFIED_DISPATCH default 0 -> 1 |
  | (c)(2) | `098a03ba` | split sm_push_null() into sm_push_null + sm_push_null_noflip; lift PUSH_NULL_NOFLIP exclusion from dispatch_one_x86 |
  | (c)(3) | `c599bbab` | sm_label() template; lift last (SM_LABEL) exclusion |
  | (c)(4) | `46e8c531` | cover last 5 opcodes (PUSH_EXPR/PUSH_EXPRESSION/CALL_EXPRESSION/INCR/DECR) via new SM_templates/sm_expr_incr.c; drop JS PUSH_EXPRESSION and WASM INCR/DECR walker overrides |
  | (c)(5) | `862f817a` | delete legacy switch + dispatch_one_x86 + SCRIP_UNIFIED_DISPATCH flag; emit_walk_codegen per-PC body collapsed to ~12 lines |
  | (c)(6) | `c081758f` | wire bb_pl_{arith,atom,builtin,call} into emit_bb_node (now total over 21 BB kinds) |
  | (c)(7) | `9b5ba0b6` | **emergency build fix** — `46e8c531` had pushed a broken HEAD: (a) name collision `void sm_call_expression(void)` (new template) vs `DESCR_t sm_call_expression(int)` (long-standing runtime helper) prevented `emit_core.c` from compiling; (b) `sm_expr_incr.c` was never added to the Makefile, so its 5 templates link-undefined even with the collision fixed.  Resolution: rename runtime `sm_call_expression(int)` → `sm_eval_subexpr(int)` (5 files, ~12 call sites; preserves the structural `sm_<OPCODE>` template convention); add `sm_expr_incr.c` to the Makefile source list + compile rule.  All watermark numbers reproduce post-fix (beauty md5 byte-identical at `40df9e004...`, broker 23/26, icon rungs 194/36/35, all smoke 5/0..7/0).  Lesson: future (c)(*) rungs that add new template files MUST verify `make scrip` from a clean tree before commit; the build was broken at HEAD `c081758f` between push and this session. |

  **Original goal text framing correction:** the goal said "delete the five silo walkers";
  in practice only `dispatch_one_x86` was a silo and was deleted.  The four backend
  frame-emitters (`emit_jvm_from_sm`, `emit_js_from_sm`, `emit_net_from_sm`,
  `emit_wasm_from_sm`) survive because they own per-backend file structure that's above
  the opcode level — JVM method-split, JS switch frame, .NET class scaffolding, WASM
  block-loop.  They're already thin (each routes opcode bodies through emit_sm_dispatch),
  and cannot dissolve into per-opcode templates without conflating frame structure with
  opcode routing.

  Net LOC across the rung: roughly -130 (Step (c)(5) alone was -136 in emit_sm.c).

  **Side effects identified, queued as separate rungs:**
  - **emit_push_expr in lower.c is dead in practice** — called by TT_UNIFY / TT_CUT /
    TT_LIMIT arms that are unreachable across all observed gates (Prolog uses lower_pl.c
    BB path, Icon \\limit goes through lower_limit_every).  sm_push_expr() template kept
    for safety.  Standalone cleanup rung's worth.
  - **SM_INCR / SM_DECR are vestigial** — emitted only by `sm_interp_test.c`; no live
    frontend lowers either today.  Could be deleted entirely in a sibling rung.
  - **NET's inline SM_LABEL function-prologue handling** could move into `sm_label()`'s
    NET arm.  Needs walker-local `fn_params`/`fn_nparams` in `g_emit`.  Not part of EC-UNI
    any longer (Layer-2 deferred per Lon directive); standalone rung if pursued.

- [x] **EC-UNI-21 (CLOSED 2026-05-20)** — beauty.sno byte-identity gate matrix.
  `scripts/test_gate_ec_uni_complete.sh` runs all five gates + baseline md5
  (`40df9e004c3e963c99af716c65f2c970`) + M1 oracle md5
  (`abfd19a7a834484a96e824851caee159`).  9/9 cells PASS on HEAD after the
  (c)(7) build fix.  **M1 status: DRIFTED.**  Current SPITBOL oracle output on
  beauty.sno is md5 `9cddff2534472b822438801d8db58a99` (622 lines), not the
  `abfd19a7...` baseline (646 lines).  Reported by the gate, not enforced.
  Re-converge to oracle parity OR formally retire M1 — tracked as
  **EC-UNI-21-followup** in this file.

- [x] **EC-UNI-15 (CLOSED 2026-05-20)** — top-level shape: every template fn is a verbose `if (IS_<BE>)` five-arm switch.  Evidence: `scripts/test_gate_em_template_matrix.sh` reports **450/450 cells covered** across 34 files / 90 fns (0 misses).  The matrix gate establishes that no fn is missing a backend arm.  No fn-size / "one screen per fn" criterion is enforced; per Lon directive (2026-05-20) the guideline is removed — the goal of the templates is to **carry the raw output** for each opcode/kind across each backend.  Consolidation first; expansion to one-source-line-per-output-line comes after the whole body is in place (Phase B work, not EC-UNI work).

- [x] **EC-UNI-16 (CLOSED 2026-05-20 — superseded by Lon directive)** — original framing was a REDUCE phase: extract Layer-2 helpers where they carried real conditionals or de-duplicated ≥2 templates.  Two slices landed and were reverted in commit `8b2f65e1` per Lon directive (2026-05-20):
  - Slice 1: `sm_calls.c` byte-near-duplicate pair `sm_call_fn` + `sm_suspend_value` collapsed via `sm_call_or_suspend(int suspend)` static helper.  Reverted.
  - Slice 2: `jvm_alpha_method_hdr(stack, locals)` / `jvm_beta_method_hdr(stack, locals)` helpers added to `emit_core.c`, used by 30 sites across 15 BB templates.  Reverted.

  **Directive (verbatim):** *"Leave the SM and BB templates without any helpers for now ... We will be breaking these into one function line per one output line after the consolidation is finished.  So remove the rule.  It serves no purpose any longer.  The goal now is to get the raw output into each template.  We will collapse once we know what all we have to work with from the entire body of source."*

  The REDUCE phase is therefore closed-by-supersession.  SM and BB templates carry the raw output verbatim; no static helpers within template files; no cross-template factoring helpers beyond the long-standing ones that predate EC-UNI (e.g., `jvm_class_hdr`, `net_alpha_hdr`, `net_class_hdr` — these stay; they're not the subject of this directive, which targets new EC-UNI-16-style extractions).

  Future "expand to one-source-line-per-output-line" work happens *after* all templates are in (Phase B territory), not as a REDUCE phase.

- [ ] **EC-UNI-17 (deferred)** — Layer-3 primitives audit.  Original framing: add new universal output primitives (beyond `emit_text`/`emit_textf`/`emit_byte`/`emit_bytes`) only if a multi-line pattern recurs in ≥3 sites across ≥2 backends.  Per Lon directive (2026-05-20), all such audits are deferred until after the whole template body is in place.  Skipping is the expected answer; this rung is informational/parked.

- [ ] **EC-UNI-18** — table-driven dispatch where it earns its keep. x86's `g_sm_nullary`/`g_sm_arith` work; extend to JVM/NET/JS/WASM for nullary + arith only.

- [ ] **EC-UNI-19** — add-a-backend test (`EMIT_NULL=99`). Mechanical patch + revert. Records LOC cost.

- [ ] **EC-UNI-20** — add-an-opcode test (`SM_NOP`). Mechanical patch + revert. Records LOC cost.

- [ ] **EC-UNI-22** — close: update `ARCH-IR.md`, `ARCH-SCRIP.md`, invariant block to reflect three-layer cake + `g_emit`. Update four per-backend GOAL files. Mark EC-UNI complete; Phase B opens.

- [ ] **EC-UNI-21-followup** — reconcile or retire M1 oracle baseline.  Choose one:
  (a) **Re-converge**: find the regression between M1 (oracle md5 `abfd19a7...`,
  646 lines) and current (`9cddff25...`, 622 lines), fix it in the SNOBOL4 runtime
  or beauty.sno source, restore byte-identity to the oracle baseline.  (b) **Retire
  M1**: declare the M1 oracle md5 obsolete in the THREE-MILESTONE AUTHORSHIP
  AGREEMENT (PLAN.md), record the new baseline md5 (`9cddff2534472b822438801d8db58a99`,
  622 lines) and re-stamp Milestone 1 with the current state.  Lon's choice; this
  rung blocks formal "Milestone 1 = oracle parity" claims until resolved.

#### EC-UNI gate (every step from EC-UNI-10 on)

```
GATE-1  beauty.sno --compile  →  md5 40df9e004c3e963c99af716c65f2c970  (882901 bytes)
GATE-2  bash scripts/test_smoke_icon.sh                                  # PASS=5
GATE-3  bash scripts/test_smoke_unified_broker.sh                        # PASS≥23
GATE-4  bash scripts/test_icon_all_rungs.sh                              # PASS=194/36/35 (--interp by default)
GATE-5  bash scripts/test_smoke_{snobol4,snocone,prolog,rebus,raku}.sh   # 7/0 5/0 5/0 4/0 5/0
```

---

### ISOLATION — parse->lower / parse->runtime boundary firewalls

**Goal:** lex/parse produces exactly `tree_t *`. Two boundaries: parse→lower (consumed by `lower()`) and parse→runtime. Today partially porous; ratchet shrinks the gap.

Completed: ISO-1 `261ff13d` (`lower(const tree_t *)`, ParserOutput deleted), ISO-2 `1691f44f` (lower firewall 10/7), ISO-3 `cb1738f6` (relocated `icon_gen.h`; lower 9/6, runtime firewall 16/8).

- [ ] **ISO-4 (NEXT)** — `scrip_parse` subprocess: parsers in a separate executable, stdin = source, stdout = TDump/TLump S-expression. SCRIP forks/execs, deserializes back to `tree_t`. Unsolved: no C-side TDump deserializer exists yet. **First sub-step:** write deserializer + roundtrip self-test before introducing the process boundary.
- [ ] **ISO-5** — Shrink lower firewall allowlist toward 0: extract `IcnTkKind` to `src/include/icon_tk.h`; split `raku_driver.h` → `raku_parse.h` + `raku_runtime.h` (relocate); relocate `frontend/prolog/{term,prolog_runtime,prolog_atom}.h` to `src/runtime/interp/prolog/`; rename `scrip_cc.h` → `src/include/scrip_lang.h` (54 includers, mechanical).
- [ ] **ISO-6** — Shrink runtime firewall allowlist toward 0 (overlaps ISO-5).
- [ ] **ISO-7** — Link-time isolation test: `lower.o` + `lower_*.o` linked against a tree with all `src/frontend/*.o` absent. Any unresolved symbol = real leakage. **Honest scope:** today's firewalls are header-level; ISO-7 closes the symbol-reachability gap (most acutely through `scrip_cc.h`).

### IR Rename — builder/consumer case scheme

UPPERCASE builds IR (`SM_t`, `BB_t`, `SM_seq_new`, `BB_alloc`). lowercase consumes (`sm_interp_*`, `bb_print`, `bb_broker`, all `SM_templates/` dispatchers). Case at the call site = side of the pipeline.

Completed: IR-RN-0 `9ce69899` (bulk rename, 48 files), IR-RN-1 `c710506f` (lower.c audit; `SM_pat_capture_fn_arg_names` fix), IR-RN-2 `92417a85` (emitter audit; 4 stale `ir_*` consumers → `bb_*`), IR-RN-3 `4a1fcc63` (runtime audit; `SM_label_pc_lookup`→`sm_label_pc_lookup`, `BB_reset`→`bb_reset`; `SM_codegen` kept UPPERCASE).

- [ ] **IR-RN-4 (NEXT)** — Update arch docs (`ARCH-IR.md`, `ARCH-ICON.md`, `ARCH-SCRIP.md`).
- [ ] IR-RN-5 — Full cross-language gate run; close rung.

Reserved (untouched): `IR_LANG_*`, `SM_INTERP_*`, `SM_CALL_STACK_MAX`/`SM_GEN_LOCAL_MAX`/`SM_MAX_OPERANDS`, `BB_POOL_SIZE`, header guards, `SM_*` opcode tags, `SM_templates/`/`BB_templates/` dir names.

---

## Completed ledgers (audit trail)

Full per-cluster detail lives in commit messages (git log is authority per RULES.md). This list is one-line summaries only.

- **IJ-* / DAI-1..7 / IJ-HELLO matrix** — 6/6 wired hello-world matrix closed 2026-05-18. Icon `--interp` (mode 2) = `--ast-run` (mode 1) at 194/265; mode 1 deleted. Icon AST walker amputated. `rt_bb_once_proc` deleted; bridge shims = `rt_pl_once` + `icn_bb_dcg`.
- **DAI-8 dead-code sweep C1–C17** — ~2700 LOC removed across 17 clusters. Final cluster C17 `d48681fb`. Methodology (kept for future audits): linker-GC + `@PLT` regex filter; grep + `&NAME` audit; Method-7 sub-graph deletion.
- **EC (emitter consolidation) 0..WASM-SM** — three silo files + emit_ir.c + emit_ir_targets.c deleted. Unified `emit_program(ast_prog, out, mode)`. Net −2504 LOC. Final commits `8890d685`/`e1c8a4ac`/`7c33121c`/`268619c1`.
- **EC-UNI 0..9d** — 52 SM templates with IS_X86 arms; matrix gate 0/365. Axis correction (false 10-cell text/binary axis → 5-cell backend matrix).
- **IR-CONSOLIDATE-DCG 1..7** — `ir_body` field deleted; mode-4 standalone uses `SM_seq_bb_add` lazy-alloc. ARCH-IR updated. Carve-out: mode-4 standalone binaries keep `ir_body` fallback (no `SM_sequence_t` at runtime). Final commit `489ff5b3` + close-out gate run.
- **ST2 — Stage 2 handoff as named struct** — `stage2_t` embeds `SM_sequence_t` and owns sidecars; `g_stage2` is a global value. Six reader shim macros burned down (`14655275`/`4f5d0512`/`d73cded0`/`27ad177b`). Dynamic-grow `label_table`/`proc_table` (`b42b7979`); ~150KB .bss freed; >4096 labels or >256 procs no longer truncate. Token firewall gate `b733dd13`. Honest scope: token-level, link-time analog deferred.

**Authors (Three-developer agreement, Milestone 1):** Lon Jones Cherryholmes · Claude Sonnet 4.7.
