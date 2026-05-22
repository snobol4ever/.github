# GOAL-HEADQUARTERS.md — one4all Maintenance HQ

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-ICON-BB-NATIVE ✅ `7efdf09a`

## Invariants

1. **No AST walking in modes 2/3/4.** `[NO-AST] FOO` → fresh SM/BB lowering, never restore AST walk.
2. **Zero C Byrd-box functions.** No `DESCR_t foo(void *zeta, int entry)`. Only permitted: `icn_bb_dcg`.
3. **Cross-language:** SM↔SM via `g_user_call_hook`; BB↔BB via universal α/β/γ/ω contract.
4. **Four ports hard-wired.** `BB_node_alloc` bakes α=nd, β=nd, γ=NULL, ω=NULL.
5. **Single gate run at end of session.**
6. **Builder/consumer case rule.** UPPERCASE builds IR (`SM_*`, `BB_*`). lowercase consumes.
7. **EC-UNI matrix.** Backends are columns (X86/JVM/JS/NET/WASM). Text-vs-binary inside each `IS_<BE>` arm — never a matrix dimension.
8. **Unified dispatch owns mode-setting.** Per-opcode calls `emit_mode_set(TEXT_MODE(), out)` at entry.
9. **One file per Byrd Box in `BB_templates/`.** Each in its own `bb_<name>.c`.
10. **Grouped templates allowed.** N opcodes sharing emit shape → single `sm_<group>()`/`bb_<group>()` with inner `switch(op)`. All emission stays in that TU. No external helpers. Examples: `sm_arith` (5), `sm_compare` (2), `sm_pat_nullary` (22).
11. **INLINE-ALL complete.** Every SM/BB code-gen path lives exclusively in `SM_templates/*.c` and `BB_templates/*.c`. Adding a backend = adding `IS_NEW` arms inside existing template files only.
12. **No shadow locals in templates.** No `const SM_t *instr = _.instr`, `FILE *out = _.out`, `int op = (int)_.instr->op`. Use `_.instr->`, `_.out`, `(int)_.instr->op` inline. Loop-counter locals (`int j`, `int fk`) are fine.

## Session State (2026-05-22, session ~22)

**one4all HEAD: `6abafcb2`** — STYLE-NO-LOCAL-SHADOWS (sm_pat_nullary instr/op) + IS_X86-STRUCTURE fix + STYLE-BASELINE-COMPRESS ✅. GATE-PK 407/0/647.

**Gate entering next session: PASS=407 FAIL=0 STUB=647. Verify `git -C one4all log origin/main..HEAD` at session start.**

**Next session — pick one:**
- **EAO-1** — Inventory full asm blocks with no opcode in `emit_sm.c`/`emit_bb.c` → `docs/XA-OPCODE-INVENTORY.md`. Needs one4all + .github.
- **ISO-4** — `scrip_parse` subprocess.
- Any STYLE step (SJ/SNS/STL/SOP/SCE/SNC) — all depend on EAO completing first.

## Session ~21 full audit summary (2026-05-22)

All HQ maintenance steps for this cycle complete:

| Step | Result |
|------|--------|
| INLINE-SPLIT-GROUPS (BB) | ✅ 4 group files → 13 per-opcode files |
| STYLE-BASELINE-COMPRESS | ✅ .raw == .norm, 165 files normalized |
| IS_X86-STRUCTURE (bb_pat_alt/cat) | ✅ dead top-level IS_BIN removed |
| STYLE-NO-LOCAL-SHADOWS (sm_pat_nullary) | ✅ instr/op/i aliases removed |
| sm_pat_nullary audit | ✅ valid group — all 22 opcodes share outer shape |
| sm_misc_nullary audit | ✅ valid group — all 7 opcodes share outer shape |
| sm_var audit | ✅ valid group — name-only variation |
| nid/sid locals in BB templates | ✅ computed values, not g_emit aliases — OK |

Gate: PASS=407 FAIL=0 STUB=647 throughout. one4all HEAD `6abafcb2`.

**sm_misc_nullary audit ✅ CLEARED (session ~19):** All 7 opcodes share identical outer shape in every backend (one-liner call). VOID_POP/PUSH_NULL_NOFLIP/NEG/EXP name-level irregularities preserved; outer structure uniform. No split.

**IS_X86-STRUCTURE fix (session ~19):** bb_pat_alt.c and bb_pat_cat.c had dead top-level `if (IS_BIN) return;` inherited from combine_group. Removed. emit_flat_ir inside IS_X86 handles both TEXT and BIN. GATE-PK 407/0/647.

**Step 10 STYLE-BASELINE-COMPRESS ✅ COMPLETE (session ~18):** freeze_per_kind_baseline.sh now writes .raw through normalizer. 165 files changed, raw==norm. GATE-PK 407/0/647. one4all HEAD 774c981f.

**Step 12 SM-PAT-NULLARY-AUDIT ✅ CLEARED (session ~18, no code change):** sm_pat_nullary is a valid group. All 22 opcodes share the same outer emit shape in every backend: x86 = identical 7-line macro call body (only macro name differs), JS = rt.pat_<name>(); one-liner, WASM = (call $sno_pat_<name>) one-liner, NET = documented stub, JVM = internal switch over 5 helper fns but the outer structure is uniform. SM_PAT_DEREF/CAT/ALT do not break shape. No split warranted.

## Session ~17 inventory (2026-05-22)

BB template grid (23 functions, 98 opcodes total):
- 1-opcode files: bb_lit, bb_pat_any, bb_pat_notany, bb_pat_span, bb_pat_break, bb_pat_arb, bb_arbno, bb_pat_cat, bb_pat_alt, bb_pat_len, bb_pat_rem, bb_pat_fence, bb_pat_abort, bb_fail (14 functions × 1)
- 2-opcode files: bb_pat_pos(POS+RPOS), bb_pat_tab(TAB+RTAB), bb_capture(ASSIGN_IMM+ASSIGN_COND), bb_lit_scalar(×4 actually), sm_var (4 functions × 2)
- Stub groups: bb_pl(10), bb_lit_scalar(4), bb_stub(28), bb_cset(20), bb_icn_stub(17)
- Non-dispatch: bb_eps (null-node path), bb_charset_emit (x86 helper)

SM template grid (28 functions, 82 opcodes total):
- sm_pat_nullary: 22 opcodes — largest group; SM_PAT_DEREF/EPS/CAT/ALT may not share shape with true nullaries → audit candidate for Step 12.
- sm_misc_nullary: 7 opcodes (PUSH_NULL, PUSH_NULL_NOFLIP, VOID_POP, CONCAT, NEG, COERCE_NUM, EXP)
- sm_return/freturn/nreturn: 3 opcodes each (S/F/bare variants share shape ✓)
- sm_jump_group: 3 (JUMP/JUMP_S/JUMP_F share shape ✓)
- sm_arith: 5 (ADD/SUB/MUL/DIV/MOD share shape ✓)

## Step 11 — INLINE-SPLIT-GROUPS

**Why:** Invariant #10 permits grouping only when opcodes share emit shape across ALL backends.
The four `bb_pat_*_group.c` files violate this: they bundle opcodes with entirely distinct
x86 / JVM / JS / NET / WASM bodies, using `switch(op)` purely on opcode-family membership,
not on shared emission shape. This makes each group file a maintenance hazard and obscures
where code lives.

**What:** Delete the 4 group `.c` files and the 4 group declarations from `bb_templates.h`.
Replace with one `.c` file per logical opcode (14 total). Wire each new function in `emit_core.c`.

| Group file deleted | New per-opcode files |
|--------------------|----------------------|
| `bb_pat_nullary_group.c` | `bb_pat_rem.c` `bb_pat_arb.c` `bb_pat_abort.c` `bb_pat_fence.c` |
| `bb_pat_anchor_group.c`  | `bb_pat_pos.c` (POS+RPOS via ival2) `bb_pat_tab.c` (TAB+RTAB via ival2) `bb_pat_len.c` |
| `bb_pat_charset_group.c` | `bb_pat_any.c` `bb_pat_notany.c` `bb_pat_span.c` `bb_pat_break.c` |
| `bb_pat_combine_group.c` | `bb_pat_alt.c` `bb_pat_cat.c` |

POS+RPOS in one file and TAB+RTAB in one file is permitted: within each pair, both backends
and the x86 arm dispatch on a single `ival2` bit, so the two opcodes share emit shape globally.

**Steps:**
- [x] SPLIT-1: write `bb_pat_rem.c`, `bb_pat_arb.c`, `bb_pat_abort.c`, `bb_pat_fence.c`; delete `bb_pat_nullary_group.c`; update `bb_templates.h` + `emit_core.c`; gate green.
- [x] SPLIT-2: write `bb_pat_pos.c` (POS+RPOS), `bb_pat_tab.c` (TAB+RTAB), `bb_pat_len.c`; delete `bb_pat_anchor_group.c`; update; gate green.
- [x] SPLIT-3: write `bb_pat_any.c`, `bb_pat_notany.c`, `bb_pat_span.c`, `bb_pat_break.c`; delete `bb_pat_charset_group.c`; update; gate green.
- [x] SPLIT-4: write `bb_pat_alt.c`, `bb_pat_cat.c`; delete `bb_pat_combine_group.c`; update; gate green.
- [x] SPLIT-5: final gate: `bash scripts/test_per_kind_diff.sh` — PASS=407 FAIL=0 STUB=647. Commit: `BB-split: dissolve 4 invalid group files into 14 per-opcode templates`.

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
cd /home/claude/one4all && make -j4 scrip > /tmp/build_full.log 2>&1
[ -x /home/claude/one4all/scrip ] || { grep -E "error:|fatal error" /tmp/build_full.log | head -5; exit 1; }
for r in /home/claude/one4all /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done
[ -d /home/claude/x64 ] || git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64
bash /home/claude/one4all/scripts/test_per_kind_diff.sh
# Expect: PASS=407 FAIL=0 STUB=647 at cc134d49
```

## Architecture

```
AST --(lower)--> SM_sequence_t  [SM_BB_XXX bridge opcodes]
                 BB_graph_t*    [pre-built per bridge op, via SM_sequence_t.bb_table]
```

Mode 2 (`--interp`) = reference. Mode 4 (`--compile`) emits wired x86.

## Gates

**Per-slice fast cycle:**
```
make -j4 scrip && bash scripts/test_per_kind_diff.sh
```
**Session-end:**
```
bash scripts/test_per_kind_diff.sh
bash scripts/test_gate_em_template_matrix.sh
# beauty md5 SUSPENDED during BB consolidation
```
**Escalate mid-session only when:** per-kind-diff FAIL/GONE; slice touches live-path dispatchers; slice changes `_` shape; slice deletes `emit_bb_x*`/`emit_sm_*`.

```
GATE-PK  bash scripts/test_per_kind_diff.sh                # PRIMARY
GATE-M   bash scripts/test_gate_em_template_matrix.sh      # session-end
GATE-E   bash scripts/test_gate_ec_uni_complete.sh         # session-end
GATE-J   bash scripts/test_crosscheck_icon.sh              # escalation
GATE-S   bash scripts/test_smoke_snobol4_jit.sh            # escalation
```
**⛔ BEAUTY GATE SUSPENDED** — beauty.sno `--compile` md5 non-binding during BB template consolidation.

**Re-freeze baseline** (after intentional change):
```
bash scripts/freeze_per_kind_baseline.sh && bash scripts/test_per_kind_diff.sh
```

## Active Rungs

### EC-UNI-23 — Delete SM_PUSH_EXPR ⚡ (PRIORITY)

`SM_PUSH_EXPR` is the last AST escape hatch: `emit_push_expr()` in `lower.c` freezes a raw `tree_t*` into the instruction stream. No test program emits it (0/200), but 3 live lowering sites still produce it. Deleting it forces Icon LIMIT and Prolog UNIFY/CUT to build real BB graphs — the [NO-AST] invariant made unavoidable.

- [x] **EC-23a** — Survey 3 `emit_push_expr` callers; define BB-graph replacements:
  - `lower_limit` (TT_LIMIT ~1468): `emit_push_expr(t); SM_emit(SM_BB_PUMP)` → real generator BB graph + pump/count box.
  - TT_UNIFY (~1893): `emit_push_expr(t); SM_emit_si(SM_CALL_FN,"PL_UNIFY",0)` → `BB_PL_UNIFY` over lowered args.
  - TT_CUT (~1894): `emit_push_expr(t); SM_emit_si(SM_CALL_FN,"PL_CUT",0)` → `BB_PL_CUT`.
- [x] **EC-23b** — Add BB-graph smoke tests for LIMIT/UNIFY/CUT first (TDD). Gate: each runs in `--interp` and `--run`.
- [x] **EC-23c** — Rewire the 3 sites to build BB graphs; delete `emit_push_expr`.
- [x] **EC-23d** — Delete `SM_PUSH_EXPR` from `src/include/SM.h` enum. ⚠ Enum is index-aligned with `g_sm_op_names[]` and handler table — remove member + name-array slot + handler-table slot together; rebuild catches mismatches.
- [x] **EC-23e** — Delete orphaned `sm_push_expr` template arm, dispatch case (`emit_core.c:1360`), interp handler `h_push_expr`, doc comments.
- [x] **EC-23f** — GATE-PK + GATE-S + GATE-J. Prolog/Icon smoke must stay green. Freeze baseline. Commit.

### EC-UNI INLINE — Remaining work

**SM-side:**
- [x] **INLINE-4** ✅ — All SM templates route directly to sm_*() fns. No shim layer survives.
- [x] **INLINE-4b** ✅ — Orphaned dispatchers already deleted in prior sessions.
- [x] **INLINE-4c** ✅ `df5838e8` — sm_define_group done. sm_var/sm_pat_string_arg/sm_call already grouped. sm_bb_calls shapes diverge too much to group profitably.
- [x] **INLINE-6** ✅ — emit_sm.c is walker-only infrastructure; no dead machinery remains.

**BB-side:**
- [x] **INLINE-3** ✅ — `emit_flat_ir_alt`/`_cat`/`_fence` already inlined in BB_templates.
- [x] **INLINE-3-GROUP** — BB grouped templates: `bb_pat_anchor_group` (POS/RPOS/TAB/RTAB/LEN), `bb_pat_charset_group` (ANY/NOTANY/SPAN/BREAK), `bb_pat_nullary_group` (REM/ARB/ABORT/FENCE), `bb_pat_combine_group` (ALT/CAT).
- [x] **INLINE-8** — Orphan sweep: delete absorbed `emit_bb_x*`/`emit_sm_*` fns.

### Step 10 — STYLE-BASELINE-COMPRESS

Store per-kind baseline `.s.raw` files pre-normalized (whitespace collapsed). Steps: (a) post-process `freeze_per_kind_baseline.sh` output through `normalize_per_kind_cell.py`; (b) update `test_per_kind_diff.sh` to diff normalized-current vs normalized-baseline directly; (c) re-freeze; (d) GATE-PK PASS=N FAIL=0; (e) commit.

### ISO — parse→lower / parse→runtime firewalls

- [x] ISO-1..3 ✅
- [ ] **ISO-4** — `scrip_parse` subprocess: parsers in separate executable, stdin=source, stdout=TDump S-expression. Write deserializer + roundtrip self-test first.
- [ ] ISO-5, ISO-6, ISO-7 — shrink firewall allowlists toward 0.

### EMIT-ALL-FROM-OPCODES — every full asm block gets an opcode ⚡ PREREQUISITE FOR ALL STYLE STEPS

**The problem:** Several full-bodied asm sequences exist in `emit_sm.c` and `emit_bb.c` that are emitted by C functions called directly — they have no SM or BB opcode naming them, no dispatch table entry, no template function. Examples:

- `emit_sm_exec_stmt_blob` — emits `lea rdi`, conditional `lea rsi`/`xor esi`, `mov edx`, `call rt_match_blob@PLT` — a 4-instruction pattern-match call sequence with no opcode
- `emit_sm_macro_library` — emits the full `.intel_syntax` + all GAS macro definitions that prelude every compilation unit — a full asm block with no opcode
- `emit_flat_entry_dispatch` — emits `cmp esi,0` / `je α_body` / `jmp β` — the Byrd-box entry trampoline, called from `emit_flat_body`, no opcode
- `emit_flat_body` (prologue) — emits `.globl` declarations + `lea r10,[rip+Δ]` setup before routing to `emit_flat_ir` — no opcode
- `emit_sm_stno` / `emit_sm_set_pc_label` — asm emission called from the SM walker outside the template dispatch path

**The rule:** Every full asm block — every named multi-instruction sequence that constitutes a recognisable unit of generated code — must have an opcode in the dispatch table and a template function that owns it. No asm is emitted by C functions called directly outside the template system.

**New opcode class: `XA_*` / `xa_*` — eXecution Administrative**

These are **administrative** opcodes: prologues, epilogues, trampolines, dispatch stubs, and other named asm fragments that form the skeleton around the semantic SM/BB opcodes. They have no language-semantic meaning — they manage the runtime scaffold.

```
XA_MACRO_LIBRARY       — the full GAS macro-definition preamble (.intel_syntax + all .macro blocks)
XA_EXEC_STMT_BLOB      — pattern-match call sequence (lea rdi/lea rsi|xor esi/mov edx/call rt_match_blob)
XA_ENTRY_DISPATCH      — Byrd-box entry trampoline (cmp esi,0 / je α / jmp β)
XA_FLAT_PROLOGUE       — .globl declarations + lea r10,[rip+Δ] before flat IR walk
XA_STNO                — mov edi,N / call rt_set_stno@PLT (the stno emission currently in emit_sm_stno)
XA_PC_LABEL            — pending-label flush (currently emit_sm_set_pc_label / emit_sm_consume_pc_label)
```

Template files live in `XA_templates/xa_*.c`. Header: `XA_templates/xa_template_common.h`. Opcode enum: `XA_op_t` in `src/include/XA.h`. Dispatcher: `xa_dispatch()` in `emit_core.c`, same pattern as `emit_sm_dispatch()`.

**Steps:**

- [ ] **EAO-1 — INVENTORY** — Read every C function in `emit_sm.c` and `emit_bb.c` that fires emission (any `emit_textf`, `fprintf(emit_outf()`, `emit_seq_*`, `emit_flat_*`, `insn_*`) and is **not** called through the SM/BB template dispatch. List each in `docs/XA-OPCODE-INVENTORY.md` with: function name / asm block description / call site(s) / proposed `XA_` opcode name. Gate: doc only. Commit.
- [ ] **EAO-2 — SCAFFOLD** — Create `src/include/XA.h` (`XA_op_t` enum, initially empty). Create `src/emitter/XA_templates/` with `xa_template_common.h` and `xa_templates.h`. Add stub `xa_dispatch(XA_op_t op)` to `emit_core.c`. Build. Commit: `EAO-2: XA_templates scaffold + XA.h + dispatcher stub.`
- [ ] **EAO-3 — XA_MACRO_LIBRARY** — Add `XA_MACRO_LIBRARY` opcode. Write `XA_templates/xa_macro_library.c` whose IS_X86 arm emits the `.intel_syntax` header then calls `emit_sm_dispatch()` for each macro-def representative (absorbing the loop from `emit_sm_macro_library`). Replace the `emit_sm_macro_library` call site with `xa_dispatch(XA_MACRO_LIBRARY)`. Build + GATE-PK. Commit.
- [ ] **EAO-4 — XA_EXEC_STMT_BLOB** — Add `XA_EXEC_STMT_BLOB`. Write `XA_templates/xa_exec_stmt_blob.c` absorbing the 4-instruction sequence from `emit_sm_exec_stmt_blob`. Replace call site. Build + GATE-PK. Commit.
- [ ] **EAO-5 — XA_ENTRY_DISPATCH + XA_FLAT_PROLOGUE** — Add both opcodes. Write `XA_templates/xa_flat.c` absorbing `emit_flat_entry_dispatch` and the `.globl`+`lea r10` prologue from `emit_flat_body`. Replace call sites. Build + GATE-PK. Commit.
- [ ] **EAO-6 — XA_STNO + XA_PC_LABEL** — Add both opcodes. Write `XA_templates/xa_sm_misc.c` absorbing `emit_sm_stno` asm block and `emit_sm_set_pc_label`/`emit_sm_consume_pc_label`. Replace call sites. Build + GATE-PK. Commit.
- [ ] **EAO-7 — VERIFY** — `grep -rn "emit_textf\|fprintf.*emit_outf\|emit_seq_\|insn_" src/emitter/emit_sm.c src/emitter/emit_bb.c` returns zero asm-emitting lines. All asm now owned by SM, BB, or AD template functions. GATE-PK + GATE-M. Commit: `EMIT-ALL-FROM-OPCODES: all asm blocks have XA_/SM_/BB_ opcodes. GATE-PK N/0/647.`

**Goal:** every backend (X86/JVM/JS/NET/WASM) is fully wired in every SM and BB template — no silent `return;` stubs, no missing arms, no asymmetric coverage. Adding a new opcode means touching exactly one template file and filling all five `IS_<BE>` arms. Adding a new backend means adding one `IS_NEW` arm per template file.

**Current state (session ~21):**
- SM templates: X86=27 arms, JVM=16, JS=11, NET=10, WASM=12. Net/JS lag X86 by ~15–17 arms.
- BB templates: X86=19 arms, JVM/JS/NET=16 each, WASM=2 (almost entirely stub).
- Stub sentinels (`bb_stub`, `bb_pl`, `bb_lit_scalar`, `bb_icn_stub`, `bb_cset`) return immediately in all backends — these are known-incomplete opcodes, not structural defects.
- WASM BB coverage is the largest gap: only `bb_pat_span/any/break/notany/rem/len/fence/arb/arbno/lit` have real WASM arms; all composite-pattern BB nodes (`bb_pat_alt`, `bb_pat_cat`, `bb_capture`, `bb_arbno` wiring, `bb_fail`) are stubs.

**Invariants (from GOAL-HEADQUARTERS #7, #11):**
- EC-UNI matrix: backends are columns. Text-vs-binary is inside each `IS_<BE>` arm. Never a matrix dimension.
- INLINE-ALL: all emission lives in `SM_templates/*.c` and `BB_templates/*.c`. No helpers outside.

**Steps:**

- [ ] **EU-1 — AUDIT** — For each SM template file, tabulate which backends have real arms vs silent stubs. Output: `docs/EMIT-UNIFY-AUDIT.md` table with columns SM-fn / X86 / JVM / JS / NET / WASM / notes. Gate: PASS=407 FAIL=0 STUB=647 throughout.
- [ ] **EU-2 — SM-NET-FILL** — Fill missing IS_NET arms in SM templates (estimated ~17 gaps). Each gap gets a real `emit_textf` call matching the .NET IL calling convention (`SnoRt::` static methods). Gate after each file.
- [ ] **EU-3 — SM-JS-FILL** — Fill missing IS_JS arms in SM templates (~15 gaps). Each gap gets a real `emit_textf` call matching the JS runtime (`rt.<method>()`). Gate after each file.
- [ ] **EU-4 — BB-WASM-FILL** — Fill WASM arms in BB templates for composite patterns (`bb_pat_alt`, `bb_pat_cat`, `bb_capture`, `bb_fail`, `bb_arbno`). Each gets a real `(call $bb_<name>_new)` WASM text emission. Gate after each file.
- [ ] **EU-5 — AUDIT-CLOSE** — Re-run audit; confirm zero silent stubs remain outside the known-incomplete sentinel group (`bb_stub`, `bb_pl`, `bb_lit_scalar`, `bb_icn_stub`, `bb_cset`). Update `docs/EMIT-UNIFY-AUDIT.md`. Freeze baseline. Commit: `EMIT-UNIFY: all SM/BB backends fully wired. GATE-PK N/0/647.`

### STYLE-JVM-ONE-SPACE — one space before every JVM opcode in emit_textf strings

**Problem:** JVM opcode strings inside `emit_textf()` calls use 4-space indent before each opcode token:
```c
emit_textf("    aload_0\n    getfield bb/bb_any/ms Lbb/bb_box$MatchState;\n");
```
Rule: **one space** before each opcode token, matching the one-space convention used everywhere else:
```c
emit_textf(" aload_0\n getfield bb/bb_any/ms Lbb/bb_box$MatchState;\n");
```

**Scope:** 28 files — 16 BB_templates + 11 SM_templates + sm_template_common.h. Total ~520 occurrences of `"    ` (4-space) prefix inside emit_textf string literals in JVM arms. NET strings (`.ldfld`, `.call`, etc.) are unaffected — they use their own indent convention. Only JVM opcodes (`aload_`, `getfield`, `invokestatic`, `invokevirtual`, `invokespecial`, `istore_`, `iload_`, `bipush`, `iconst_`, `iadd`, `isub`, `putfield`, `if_icmp*`, `goto`, `ireturn`, `areturn`, `aconst_null`, `dup`, `new`, etc.) are in scope.

**Invariant:** GATE-PK PASS=407 FAIL=0 STUB=647 must hold after every file. The per-kind baselines for JVM cells will change — re-freeze after the sweep.

**Steps:**

- [ ] **SJ-1 — BB sweep** — In every `BB_templates/*.c` file, replace `"    ` → `" ` inside `emit_textf` string literals inside `IS_JVM` arms only. One commit per file. Gate after each. Files (16): `bb_pat_any`, `bb_pat_notany`, `bb_pat_span`, `bb_pat_break`, `bb_pat_abort`, `bb_pat_rem`, `bb_pat_arb`, `bb_pat_fence`, `bb_pat_len`, `bb_pat_pos`, `bb_pat_tab`, `bb_pat_alt`, `bb_pat_cat`, `bb_arbno`, `bb_capture`, `bb_lit`.
- [ ] **SJ-2 — SM sweep** — Same replacement in every `SM_templates/*.c` and `sm_template_common.h` inside `IS_JVM` arms. One commit per file. Gate after each. Files (12): `sm_arith`, `sm_compare`, `sm_jumps`, `sm_returns`, `sm_push_pop_lits`, `sm_pat_nullary`, `sm_pat_anchors`, `sm_pat_combine`, `sm_calls`, `sm_halt`, `sm_defines`, `sm_template_common.h`.
- [ ] **SJ-3 — REFREEZE** — `bash scripts/freeze_per_kind_baseline.sh` for JVM cells only; verify `bash scripts/test_per_kind_diff.sh` returns PASS=407 FAIL=0 STUB=647. Commit: `STYLE-JVM-ONE-SPACE: refreeze JVM baselines. GATE-PK 407/0/647.`

### STYLE-NO-SHADOW-LOCALS — no local aliases for g_emit fields in templates

**Rule (from GOAL-HEADQUARTERS invariant #12):** No shadow locals in templates. Use `_.node`, `_.instr`, `_.out`, `_.i` inline everywhere. Never declare `BB_t * nd = _.node`, `const SM_t * instr = _.instr`, `FILE * out = _.out` — these are aliases that obscure the actual source of truth and were banned by STYLE-NO-LOCAL-SHADOWS.

**Current violations (all that remain after prior STYLE sweeps):**

| File | Shadow | Occurrences |
|------|--------|-------------|
| `SM_templates/sm_pat_combine.c` | `const SM_t * instr = _.instr` | 5 (one per function) |
| `SM_templates/sm_calls.c` | `const SM_t * instr = _.instr` | 1 |
| `SM_templates/sm_jumps.c` | `const SM_t * instr = _.instr` | 1 |
| `SM_templates/sm_template_common.h` | `FILE * out = _.out` | 2 (in `jvm_ret_guard`, `net_ret_guard`) |

**Exception — permitted locals (not shadows):** Loop counters (`int i`, `int j`, `int fk`), computed values (`int sid = _.sid`, `int nid = _.nid`, `const char * tag`), and function parameters that vary per call site are fine. Only direct re-aliases of `_.node` / `_.instr` / `_.out` are banned.

**Note on `sm_template_common.h`:** `jvm_ret_guard` and `net_ret_guard` each declare `FILE * out = _.out` and `int i = _.i`. The `int i = _.i` is a computed copy (fine). The `FILE * out = _.out` is a shadow — replace with `_.out` inline in the two `fprintf` calls within each helper.

**Steps:**

- [ ] **SNS-1 — sm_pat_combine.c** — Remove `const SM_t * instr = _.instr` from all 5 functions; replace every `instr->` with `_.instr->` throughout. Build + GATE-PK. Commit.
- [ ] **SNS-2 — sm_calls.c + sm_jumps.c** — Same removal in both files. Build + GATE-PK. Commit.
- [ ] **SNS-3 — sm_template_common.h** — In `jvm_ret_guard` and `net_ret_guard`: remove `FILE * out = _.out`; replace `out` with `_.out` in the two `fprintf` calls in each helper. Build + GATE-PK. Commit: `STYLE-NO-SHADOW-LOCALS: remove FILE*/SM_t* aliases from SM templates. GATE-PK 407/0/647.`

### STYLE-NO-TRANSFORM-LOCALS — no locals that are simple casts or one-shot computations on globals

**Rule:** Do not declare a local whose sole purpose is to cast or trivially transform a global/field for use in one or a few call sites. Use the expression inline. Example:
```c
/* BEFORE */
int lineno = (int)_.instr->a[1].i;
emit_textf("... %d ...", lineno);

/* AFTER */
emit_textf("... %d ...", (int)_.instr->a[1].i);
```

**Classification — what is banned vs permitted:**

| Local | File | Verdict | Reason |
|-------|------|---------|--------|
| `int sid = 0` | 13 BB files | **BANNED** — inline as literal `0` | always zero, no computation |
| `int i = _.i` | `sm_template_common.h` | **BANNED** — inline `_.i` | direct alias of field |
| `int lineno = (int)_.instr->a[1].i` | `sm_compare.c` | **BANNED** — used twice, inline both | trivial cast |
| `int val = (int)_.instr->a[0].i` | `sm_compare.c` | **BANNED** — inline | trivial cast |
| `int is_entry = (...)` | `sm_defines.c` | **BANNED** — inline | one boolean comparison |
| `int pc = _.i` | `sm_defines.c` | **BANNED** — inline `_.i` | direct alias |
| `int has_repl = (int)_.instr->a[1].i` | `sm_defines.c`, `sm_pat_combine.c` | **BANNED** — inline | trivial cast |
| `int is_imm = (int)_.instr->a[1].i` | `sm_pat_combine.c` | **BANNED** — inline | trivial cast |
| `int nargs = (int)_.instr->a[N].i` | `sm_pat_combine.c`, `sm_calls.c`, `sm_bb_calls.c` | **BANNED** — inline | trivial cast |
| `int arity = (int)_.instr->a[1].i` | `sm_bb_calls.c` | **BANNED** — inline | trivial cast |
| `int addr = wasm_intern_*(s)` | `sm_push_pop_lits.c`, `sm_pat_anchors.c`, `sm_pat_combine.c` | **BANNED** — inline into single `emit_textf` | one-shot, used immediately |
| `int cond = (...)` | `sm_returns.c` (×3) | **BANNED** — inline both uses | used twice each, short expr |
| `int fk = (...)` | `sm_returns.c`, `sm_calls.c` | **BANNED** — inline | used in one conditional |
| `int nid = bb_node_id(_.node)` | all BB files | **PERMITTED** — keep | function call, used 4–39× |
| `int rpos = (int)(_.node->ival2 != 0)` | `bb_pat_pos.c` | **PERMITTED** — keep | flag drives structural if, used 10× |
| `int rtab = (int)(_.node->ival2 != 0)` | `bb_pat_tab.c` | **PERMITTED** — keep | same |
| `const char * s = _.instr->a[0].s ? ... : ""` | SM files | **PERMITTED** — keep | null-guard conditional, not a simple cast |
| `const char * fname = ...` (multi-expr) | `sm_returns.c`, `sm_calls.c` | **PERMITTED** — keep | real conditional computation |

**Steps:**

- [ ] **STL-1 — BB sid=0 sweep** — In all 13 BB_templates files that declare `int sid = 0`: remove the declaration; replace every use of `sid` with `0` inline. Files: `bb_pat_any`, `bb_pat_notany`, `bb_pat_span`, `bb_pat_break`, `bb_pat_len`, `bb_pat_pos`, `bb_pat_tab`, `bb_pat_alt`, `bb_pat_cat`, `bb_pat_abort`, `bb_pat_rem`, `bb_pat_arb`, `bb_arbno`, `bb_capture`, `bb_lit`. Build + GATE-PK. One commit.
- [ ] **STL-2 — sm_template_common.h `int i = _.i`** — Remove `int i = _.i` from `jvm_ret_guard` and `net_ret_guard`; replace `i` with `_.i` inline. Build + GATE-PK. Commit.
- [ ] **STL-3 — sm_compare.c** — Inline `lineno` and `val`. Build + GATE-PK. Commit.
- [ ] **STL-4 — sm_defines.c** — Inline `is_entry`, `pc`, `has_repl`. Build + GATE-PK. Commit.
- [ ] **STL-5 — sm_returns.c** — Inline `cond` (×3 functions) and `fk` (×2 functions). Build + GATE-PK. Commit.
- [ ] **STL-6 — sm_pat_combine.c + sm_calls.c + sm_bb_calls.c** — Inline `has_repl`, `is_imm`, `nargs`, `arity`, `fk`, `addr`. Build + GATE-PK. One commit per file.
- [ ] **STL-7 — sm_push_pop_lits.c + sm_pat_anchors.c** — Inline `addr` into single `emit_textf` call site. Build + GATE-PK. Commit.

### STYLE-NO-OUT-PARAM — remove FILE * out parameter from all emitter helpers; use g_emit.out globally

**Rule:** No helper function in the emitter takes `FILE * out` as a parameter. The output sink is `g_emit.out` — a global. Every `fprintf(out, ...)` inside a helper becomes `emit_textf(...)` (or `emit_byte`/`fputc(b, g_emit.out)` for binary). Every call site drops the `_.out` argument. The parameter disappears from signatures and declarations.

**Why:** `FILE * out` threading is ceremony — every caller passes `_.out`, every body uses it only for `fprintf`. Making `g_emit.out` implicit at the call site removes ~188 redundant argument slots and aligns with `emit_textf` already being parameterless.

**Scope:** 20 helpers defined in `emit_core.c`, declared in `BB_templates/bb_template_common.h` and `SM_templates/sm_template_common.h`, called from 16 BB template files + SM template files + `emit_core.c` itself (188 call sites total).

**Helpers to convert (all in `emit_core.c`):**

| Helper | Change |
|--------|--------|
| `js_escape(FILE *out, const char *s)` | → `js_escape(const char *s)`; body: `fprintf(out,…)` → `emit_textf(…)` / `fputc(c, g_emit.out)` |
| `js_escape_string(FILE *out, const char *s)` | same pattern |
| `jvm_class_hdr(FILE *out, const char *name)` | → `jvm_class_hdr(const char *name)` |
| `jvm_init_ms_only(FILE *out, const char *name)` | → `jvm_init_ms_only(const char *name)` |
| `jvm_init_ms_int(FILE *out, const char *name, const char *field)` | → drop `out` |
| `jvm_init_ms_str(FILE *out, const char *name, const char *field)` | → drop `out` |
| `jvm_val_helper(FILE *out, const char *name)` | → drop `out` |
| `net_class_hdr(FILE *out, int sid, int nid)` | → drop `out` |
| `net_alpha_hdr(FILE *out)` | → `net_alpha_hdr(void)` |
| `net_beta_hdr(FILE *out)` | → `net_beta_hdr(void)` |
| `net_cursor_load(FILE *out)` | → `net_cursor_load(void)` |
| `net_ms_length(FILE *out)` | → `net_ms_length(void)` |
| `net_spec_of(FILE *out)` | → `net_spec_of(void)` |
| `net_fail_ret(FILE *out)` | → `net_fail_ret(void)` |
| `net_push_i4(FILE *out, int v)` | → `net_push_i4(int v)` |
| `net_ctor_none(FILE *out, int sid, int nid)` | → drop `out` |
| `net_spec_zw(FILE *out)` | → `net_spec_zw(void)` |
| `net_escape_ldstr(FILE *out, const char *s)` | → drop `out`; `fputc(*p, out)` → `emit_byte(*p)` |
| `net_charset_class(FILE *out, int sid, int nid, const char *tag)` | → drop `out` |
| `jvm_pat_str_push(FILE *out, int i, …)` | → drop `out` (inline in sm_template_common.h) |
| `jvm_pat_long_push(FILE *out, …)` | → drop `out` |
| `jvm_pat_noarg_push(FILE *out, …)` | → drop `out` |
| `jvm_pat_pat_push(FILE *out, …)` | → drop `out` |
| `jvm_pat_2pat_push(FILE *out, …)` | → drop `out` |

**Steps:**

- [ ] **SOP-1 — Update declarations** — In `BB_templates/bb_template_common.h` and `SM_templates/sm_template_common.h`: remove `FILE *out` from every helper declaration. Remove `FILE * out` from inline body parameters (`jvm_pat_*`). Build only (no gate yet — call sites still pass `_.out`; compiler errors show remaining sites). Do not commit standalone.
- [ ] **SOP-2 — Update definitions in emit_core.c** — Remove `FILE * out` parameter from all 20 helper signatures. Replace every `fprintf(out, ...)` with `emit_textf(...)`. Replace `fputc(b, out)` with `emit_byte(b)` (in `net_escape_ldstr`). Build. Do not commit standalone.
- [ ] **SOP-3 — Update BB call sites** — In all 16 BB_templates files: remove `_.out` argument from every helper call. Build + GATE-PK. One commit: `STYLE-NO-OUT-PARAM: remove FILE*out from BB helpers. GATE-PK 407/0/647.`
- [ ] **SOP-4 — Update SM call sites** — In SM_templates files and `emit_core.c` internal calls: remove `_.out` / `g_emit.out` argument from every helper call. Build + GATE-PK. Commit: `STYLE-NO-OUT-PARAM: remove FILE*out from SM helpers + emit_core internal calls. GATE-PK 407/0/647.`

### STYLE-SWITCH-TO-EXPR — Collapse name-only op switches to ternary/table expressions

**Problem:** Every SM template that groups multiple opcodes has a `switch((int)_.instr->op)` per backend arm. In most cases every case produces the same call sequence with only one token (method name, macro name, integer constant) varying. This is a selection masquerading as control flow — the switch can be replaced by a single expression that selects the varying token inline, collapsing the switch entirely.

**Rule:** If a `switch` on `_.instr->op` has N cases and every case is a single `emit_textf(fmt, ...)` or helper-then-`emit_textf` where only one argument string/int differs, replace with:
```c
/* 2-case: */ emit_textf("... %s ...\n", (int)_.instr->op == SM_A ? "nameA" : "nameB");
/* N-case: */ static const char *nm[] = {"nameA","nameB","nameC",...};
              emit_textf("... %s ...\n", nm[(int)_.instr->op - SM_BASE]);
```
**Exception:** Structurally distinct cases (different number/sequence of emit calls per case — e.g. `sm_jumps` JVM arm) stay as switches.

**Scope:** SM_templates only. BB_templates have no op-dispatch switches (each file handles one opcode).

**Steps:**

- [ ] **SCE-1 — AUDIT** — Enumerate every `switch((int)_.instr->op)` across all SM_templates. Classify each as: (A) **name-only** — all cases have identical call structure, only one string/int token varies → collapse to ternary/table; (B) **structurally distinct** — cases produce different sequences of calls → keep as switch. Output: one-line entry per switch in `docs/SWITCH-EXPR-AUDIT.md`. Gate: doc only. Commit.
- [ ] **SCE-2 — sm_compare** — Both switches are name-only (2-case): `"acomp"/"lcomp"` token varies, `jvm_push_int2`+`emit_textf` / `net_push_i4`+`emit_textf` / `emit_textf` calls are identical per backend. Replace each switch with an inline ternary on `(int)_.instr->op == SM_ACOMP`:
  ```c
  /* JVM: */ jvm_push_int2((long)_.instr->a[0].i);
             emit_textf("    invokestatic rt/SnoRt/%s(I)V\n",
                 (int)_.instr->op == SM_ACOMP ? "acomp" : "lcomp");
  /* NET: */ net_push_i4((int)_.instr->a[0].i);
             emit_textf("    call       void SnoRt::%s(int32)\n",
                 (int)_.instr->op == SM_ACOMP ? "acomp" : "lcomp");
  /* WASM: */ emit_textf("          (call $sno_%s (i32.const %lld))\n",
                 (int)_.instr->op == SM_ACOMP ? "acomp" : "lcomp",
                 (long long)_.instr->a[0].i);
  ```
  Build + GATE-PK. Commit.
- [ ] **SCE-3 — sm_expr_incr** — X86 switch (2-case, name-only: `"INCR"/"DECR"`), WASM switch (2-case: constant `0`/`1`). Replace both with ternary on `(int)_.instr->op == SM_INCR`. Build + GATE-PK. Commit.
- [ ] **SCE-4 — sm_arith** — Five switches (ADD/SUB/MUL/DIV/MOD, one per backend). X86/JS: name varies → `const char *nm[] = {"ADD_NUM","SUB_NUM","MUL_NUM","DIV_NUM","MOD_NUM"}; emit_textf("    %s\n", nm[op - SM_ADD])`. JVM/NET/WASM: index varies → `int idx = op - SM_ADD; emit_textf(...)`. MOD irregularity in JVM/NET is a structurally distinct case — keep its own branch, fold ADD..DIV only. Build + GATE-PK. Commit.
- [ ] **SCE-5 — sm_misc_nullary** — Seven switches (one per backend, 7-case each). All name-only: the method/macro name is the sole varying token. Replace each switch with a `static const char *` name table indexed by `op - SM_CONCAT`. Build + GATE-PK. Commit.
- [ ] **SCE-6 — sm_pat_nullary, sm_push_pop_lits, sm_pat_anchors** — Same pattern: each switch selects a name token from a fixed set. Replace with name tables or ternaries. One commit per file. Build + GATE-PK each.
- [ ] **SCE-7 — VERIFY** — `grep -rn "switch.*instr->op\|switch.*\bop\b" SM_templates/` — confirm only structurally-distinct switches remain (i.e. `sm_jumps` JVM arm where each case produces a different sequence). Zero name-only switches permitted. GATE-PK. Commit: `STYLE-SWITCH-TO-EXPR: all name-only op switches collapsed to ternary/table. GATE-PK 407/0/647.`

### STYLE-NO-COMMENTS — remove all comments from SM_templates and BB_templates source

**Rule:** No comments of any kind in `SM_templates/*.c`, `BB_templates/*.c`, `sm_template_common.h`, `bb_template_common.h`. The code must be self-explanatory through naming. Three forms to remove:

1. **Separator lines** — `/*----...----*/` (200-char dashes) between functions. Remove the line entirely; functions abut directly.
2. **Block comments** — `/* prose ... */` on their own line(s) before a function or section. Remove all lines from `/*` through closing `*/`.
3. **Trailing inline comments** — `code; /* note */` or `code; // note` at end of a code line. Strip the comment suffix, preserve the code.

**Note on sm_template_common.h / bb_template_common.h:** These headers have substantial block comments explaining the helper functions. Remove the block comment bodies; keep the declarations. The RULES.md comment style rule ("no inline or end-of-line comments; no comments inside function bodies; block comment on line after separator, before function signature") still applies to non-template files — this step applies only to the template directories.

**Scope:** 13 SM_templates files + 2 common headers + 24 BB_templates files = 39 files total.

**Steps:**

- [ ] **SNC-1 — BB_templates separator lines** — Delete all `/*----...----*/` separator lines from all 24 `BB_templates/*.c` files. Build + GATE-PK. One commit.
- [ ] **SNC-2 — BB_templates block comments** — Delete all `/* ... */` block comments (single-line and multi-line) that stand on their own line(s) in all 24 `BB_templates/*.c` files. Build + GATE-PK. One commit.
- [ ] **SNC-3 — BB_templates trailing inline comments** — Strip trailing `/* ... */` and `// ...` suffixes from code lines in all 24 `BB_templates/*.c` files. Build + GATE-PK. One commit.
- [ ] **SNC-4 — SM_templates separator + block comments** — Delete all separator lines and standalone block comments from all 13 `SM_templates/*.c` files. Build + GATE-PK. One commit.
- [ ] **SNC-5 — SM_templates trailing inline comments** — Strip trailing `/* ... */` and `// ...` suffixes from code lines in all 13 `SM_templates/*.c` files. Build + GATE-PK. One commit.
- [ ] **SNC-6 — sm_template_common.h + bb_template_common.h** — Remove all block comments and separator lines from both headers. Preserve declarations; remove explanatory prose. Build + GATE-PK. Commit: `STYLE-NO-COMMENTS: all comments removed from SM/BB template files. GATE-PK 407/0/647.`

## Watermark

```
4541c4da  INLINE-8: 13 absorbed bb_*.c orphans deleted; group templates own all BB dispatch. GATE-PK 407/0/647.
67da2a22  INLINE-3-GROUP: bb_pat_{charset,anchor,nullary,combine}_group. GATE-PK 407/0/647.
df5838e8  INLINE-4c: sm_define_group; shadow locals; dispatcher cleanup. GATE-PK 407/0/647.
7293cc40  EC-UNI-23: SM_PUSH_EXPR deleted. Invariant #1 [NO-AST] structurally enforced. GATE-PK 407/0/647.
cc134d49  STYLE-8b: inline instr/op shadow locals in all SM templates. GATE-PK 407/0/647.
21fd2715  STYLE-G_EMIT-RENAME: #define _ g_emit. GATE-PK 407/0/647.
8fe5f0a9  STYLE-NO-LOCAL-SHADOWS: remove FILE*/BB_t*/SM_t* aliases. GATE-PK 407/0/647.
d8168555  IS_X86-STRUCTURE: IS_MACRO_DEF/IS_BIN subordinate to IS_X86 in all templates.
3529f907  BREAKX-1: recreate rt_bb_brkx runtime + charset selection hook.
57c96cbd  EC-UNI-INLINE-8: dead emit_bb_x* sweep + retire SM_PUSH_EXPR audit cell.
```

smoke icon: 5/0  smoke prolog: 5/0  smoke rebus: 4/0
smoke raku: 5/0  smoke snobol4: 7/0  smoke snocone: 5/0
broker: 23/26    icon rungs: 194/36/35
matrix gate: 855/855 PASS
beauty.sno --compile md5: SUSPENDED

Grouped templates landed:
  sm_arith (5), sm_compare (2), sm_pat_nullary (22), sm_jump_group (3),
  sm_misc_nullary (7), sm_incr_decr (2) — 41 opcodes in 6 fns.
  sm_pat_string_arg (LIT/REFNAME/USERCALL), sm_var (PUSH_VAR/STORE_VAR).
  sm_returns (9 RETURN opcodes in 3 fns).

**Known issues:**
- Normalizer gap: `normalize_per_kind_cell.py` strips `0x`+8+ hex digits; 6-digit addresses escape.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6
