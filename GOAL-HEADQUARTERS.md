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

## Session State (2026-05-22, session ~21)

**one4all HEAD: `6abafcb2`** — STYLE-NO-LOCAL-SHADOWS (sm_pat_nullary instr/op) + IS_X86-STRUCTURE fix + STYLE-BASELINE-COMPRESS ✅. GATE-PK 407/0/647.

**Gate entering next session: PASS=407 FAIL=0 STUB=647. Verify `git -C one4all log origin/main..HEAD` at session start.**

**Next session — pick one:**
- **ISO-4** — `scrip_parse` subprocess: parsers in separate executable, stdin=source, stdout=TDump S-expression. Write deserializer + roundtrip self-test first. Needs one4all + .github.
- Any other active goal from the table (CHUNKS Step 17, PST goals, etc.).

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
