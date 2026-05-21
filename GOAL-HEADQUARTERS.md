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
```

## Architecture

```
AST --(lower)--> SM_sequence_t  [SM_BB_XXX bridge opcodes]
                 BB_graph_t*    [pre-built per bridge op, single-structure via SM_sequence_t.bb_table]
```

Mode 2 (`--interp`) is the reference path for Icon at 194/265. Mode 4 (`--compile`) emits wired x86 — no `bb_broker`.

## Gates

### Directive: emitter-refactor session pace

**During CORRAL / lift / template-physical-placement work where the LIVE PATH IS
UNCHANGED, the full gate matrix at session start is wasteful and slow.**  These
slices are byte-identical by construction — the originals in `emit_bb.c` / `emit_sm.c`
still run; the template arms are dormant code waiting for `emit_bb_node` /
`emit_program` to be wired.  Re-running the same 194-rung Icon suite three times
per slice tells us nothing the build + matrix gate didn't already.

Use this tiered cadence:

**Per-slice fast cycle (default — use this for every CORRAL slice):**
```
make -j4 scrip                                               # must build clean
bash scripts/test_gate_em_template_matrix.sh                 # invariant; matrix grows N×5 per new template
bash scripts/test_gate_ec_uni_complete.sh                    # beauty.sno --compile md5 byte-identity (THE byte-identical proof)
```
If both gates pass, the slice is good.  Commit + push.  No Icon-all-rungs.
No smoke_broker.  No smoke_icon.

**Session-end gate (run ONCE at handoff, not per slice):**
```
bash scripts/test_smoke_icon.sh                              # PASS=5
bash scripts/test_smoke_unified_broker.sh                    # PASS >= 23
bash scripts/test_icon_all_rungs.sh                          # PASS=194 --interp
```

**Session-start gate (run ONCE at session start, NOT before each slice):**
The session-end gate from the prior session is your baseline; if it was clean on
the watermarked commit, you do not need to re-establish it before your first
edit.  Just `make -j4 scrip` to confirm the build, then start cutting.

**When to escalate to full gates mid-session:**
- The slice touches the LIVE PATH (changes `emit_bb.c` / `emit_sm.c` / dispatchers).
- The slice removes a function (delete originals after wire-up).
- The slice changes `g_emit` shape (new fields, renamed fields).
- The build broke and was fixed — re-run full to confirm no follow-on damage.
- An unfamiliar template kind is being filled for the first time (e.g. first SM-side
  slice after BB-side is done).

For pure physical-placement CORRAL slices like 5/6/7, the fast cycle is sufficient.

### Gate commands

```
GATE-1  bash scripts/test_smoke_icon.sh                        # PASS=5            (session-end only)
GATE-2  bash scripts/test_smoke_unified_broker.sh              # PASS >= 23        (session-end only)
GATE-3  bash scripts/test_icon_all_rungs.sh                    # PASS=194          (session-end only)
GATE-M  bash scripts/test_gate_em_template_matrix.sh           # matrix invariant  (per-slice)
GATE-E  bash scripts/test_gate_ec_uni_complete.sh              # beauty md5 + 9-gate roll-up (per-slice)
```


## Watermark

```
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

**Lon directive (2026-05-20, verbatim):**
> *"You do know you can just lift the entire 3-layer cake and drop it in I suspect.  Then wire it with globals.  We'll do the expansion at the next step."*
> *"Put the helpers anywhere you want because we are about to delete 90% of them."*
> *"What I am saying is you drop that into the new template location and wire it up.  Put the helpers anywhere you want because we are about to delete 90% of them."*

**The job:** for each x86 codegen fn still living in `src/emitter/emit_sm.c` or `src/emitter/emit_bb.c`, **copy-paste its body verbatim** into the matching template's `IS_X86` arm.  That's it.  No refactoring, no helper extraction, no factoring across templates, no design conversation.

**Mechanical recipe (per fn):**

1. Identify the fn.  Examples: `emit_bb_xstar` (BB_PAT_REM), `emit_bb_xlnth` (BB_PAT_LEN), `emit_bb_xchr` (BB_PAT_LIT), `emit_bb_charset` (BB_PAT_SPAN/ANY/BREAK/NOTANY), `emit_sm_concat_dispatch` (SM_CONCAT), `emit_sm_jump_line` (SM_JUMP), etc.
2. Find the matching template file: `BB_templates/bb_<kind>.c` or `SM_templates/sm_<op>.c`.  The stub line `if (IS_BIN) return; /* x86 binary: emit_flat_body path, not emit_bb_node */` (BB templates) or the `if (IS_X86) return emit_sm_<op>_dispatch(out, instr, 0);` line (SM templates) marks where the lifted body lands.
3. **Copy the entire fn body verbatim** into the template's `if (IS_X86) { ... return; }` arm.  Preserve the original local variable names; just rewrite parameters as reads from `g_emit`:
   - `s`/`f`/`b` (succ/fail/back labels) → `g_emit.lbl_succ` / `g_emit.lbl_fail` / `g_emit.lbl_back`
   - `n` (LEN/TAB count) → `nd->ival` (where `nd = g_emit.node`)
   - `lit` (PAT_LIT string) → `nd->sval`
   - `out` → `g_emit.out` (or local `FILE * o = emit_outf();` as the lifted body already does)
4. **Helpers stay where they are.**  `emit_bb_box_banner`, `bb3c_format`, `emit_outf`, `emit_label_define`, `insn_*`, `emit_store_delta`, `emit_jmp`, `emit_seq_bounds_len`, `emit_add_delta_imm`, `TEMPLATE_ADDR_SIGLEN`, `JMP_*` — all stay in their current files.  ~90% of them will be deleted in the next pass anyway.  **Do not move helpers.  Do not extract helpers.  Do not factor across templates.**  Just link against them.
5. Leave the original fn in `emit_bb.c` / `emit_sm.c` for now.  The dispatcher (`emit_flat_ir` or `emit_walk_codegen`) still calls the old fn; two paths coexist temporarily.  Rewire/delete happens after the lift sweep is complete.
6. Build → matrix gate (`scripts/test_gate_em_template_matrix.sh`) → beauty md5 check (`./scrip --compile .../beauty.sno | md5sum` should still be `40df9e004c3e963c99af716c65f2c970`) → commit.  Each slice is 1–10 fns; small commits, often.

**Canonical example landed:** one4all `71bd8b6f` lifted `emit_bb_xstar` → `bb_rem` IS_X86 arm and `emit_bb_xlnth` → `bb_len` IS_X86 arm.  `g_emit` gained three label fields: `lbl_succ`, `lbl_fail`, `lbl_back` (in `src/emitter/emit_globals.h`).  Read those files for the canonical shape.

**What NOT to do (mistakes made before this directive landed; do not repeat):**
- Do NOT extract a `static` helper inside a template that collapses two opcodes into one body (slice 1, reverted in `8b2f65e1`).
- Do NOT add Layer-2 helpers in `emit_core.c` that factor a common pattern across multiple templates (slice 2, reverted).
- Do NOT enforce or measure "fn fits on a screen" — that rule was removed (2026-05-20).
- Do NOT pause to ask design questions about helpers, file structure, or which fn to do first.  Just pick any unmoved `emit_bb_x*` or `emit_sm_*` and lift it.
- Do NOT touch the matrix gate's same-file-helper-delegation logic — there are no template-local helpers in the consolidation phase.

**What "complete" means here:** every x86 codegen fn that lives in `emit_bb.c` or `emit_sm.c` has been copy-pasted into its matching template's `IS_X86` arm.  After the lift sweep, the rewire/delete pass will:
- Update `emit_flat_ir` / `emit_walk_codegen` to call the templates directly (via `emit_bb_node` and `emit_sm_dispatch`).
- Delete the original `emit_bb_x*` / `emit_sm_*_dispatch` fns from `emit_bb.c` and `emit_sm.c`.
- Trim 90% of the now-unreachable helpers.
- That's "Phase B" expansion (one-source-line-per-output-line) territory.

**Lift queue, approximate** — see `git grep -nE '^(void|int) emit_(bb_x|sm_)\w+_(dispatch|template|line|x\w+)\s*\(' src/emitter/emit_bb.c src/emitter/emit_sm.c` for the live list:

BB-side (in `emit_bb.c`): `emit_bb_xchr`, `emit_bb_xfarb`, `emit_bb_charset` (× SPAN/ANY/BREAK/NOTANY), `emit_bb_xposi`, `emit_bb_xrpsi`, `emit_bb_xtb`, `emit_bb_xrtb`, `emit_bb_xfail`, `emit_bb_xeps`, `emit_flat_ir_fence`, `emit_flat_ir_cat`, `emit_flat_ir_alt`, etc.

SM-side (in `emit_sm.c`): ~62 distinct `emit_sm_*_dispatch` / `_template` / `_line` fns.  Most are 1–10 lines.  Source list available via `grep -n '^int  emit_sm_\|^void emit_sm_' src/emitter/emit_sm.c`.

**Verification per commit:** matrix gate stays at 830/830; beauty.sno --compile md5 stays at `40df9e004c3e963c99af716c65f2c970` (byte-identical — the lifts add code paths but don't change output until the dispatcher is rewired).

---

**Scope inventory:** SM has 91 opcodes in the enum, 76 dispatched by `emit_sm_dispatch` (the other 15 are runtime/sentinel — BB-bridge `_PROC` variants, frame/global ops, compare aliases, `SM_SUSPEND`/`SM_OPCODE_COUNT` — not template work).  BB has 97 kinds in `BB_op_t`; **all 97 are dispatched by `emit_bb_node` and have template slots** as of one4all `99630c7e` (21 pattern + Prolog kinds carry real code, 76 are honest no-op stubs awaiting Phase B per-backend codegen).  Walkers delete after coverage lands: net −2500 to −3500 LOC.

**Unblocks Phase B:** five per-backend GOAL files (`GOAL-SN4-X86-EMIT` [new], `GOAL-SN4-JVM-EMIT`, `GOAL-SN4-JS-EMIT`, `GOAL-SN4-NET-EMIT`, `GOAL-SN4-WASM-EMIT`).

Closed sub-rungs trail: EC-UNI-10..13(e), 14-PREREQ, SUSPEND_VALUE fix, 14(a), 14(b), 14(c)(1..7), 15, 16 (closed-by-supersession), 21.
See git log for per-commit detail.

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
