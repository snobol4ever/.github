# GOAL-TEXTF-TEMPLATES.md — literal emit_textf templates, delete formatting layer

**Repo:** SCRIP + .github
**Prereq:** EC-UNI-PER-KIND-DIFF baseline frozen at SCRIP `ddd08f01` or later (PASS≥401, FAIL=0, STUB=658).
**Why:** templates currently call `bb3c_format`/`emit_text_jmp`/`emit_label_define` per line. The 3-column GAS alignment is human readability — once the baseline `.raw` files capture the canonical output, the alignment machinery is dead weight. Convert each template arm to one `emit_textf(LITERAL, vars...)` of the captured text with `%s`/`%d` for variable parts. Then delete the formatting layer and the legacy `emit_bb_x*` helpers. Net: −2500 to −3500 LOC.

## Invariants

1. **Byte-identity preserved.** After every group, GATE-PK (`scripts/test_per_kind_diff.sh`) must show PASS unchanged, FAIL=0, GONE=0.
2. **No new behavior.** Conversion is pure refactor. If output differs from baseline, the conversion is wrong; do NOT re-freeze to hide it.
3. **Beauty gate stays suspended** (per Lon 2026-05-21 session #6) for duration of this goal.
4. **Semantic `if` branches survive.** See "Variant inventory" below.

## Done when

1. Every non-empty cell in `baselines/per_kind/` is reproduced by `emit_textf` literals in its template arm.
2. Deleted: `bb3c_format`, `emit_label_define`, `emit_bb_box_banner`, `emit_text_jmp`, `emit_text_label`, `emit_outf`, `bb3c_flush_pending_*`, pending-label fusion state.
3. Deleted: all `emit_bb_x*` legacy helpers (xstar, xfarb, xlnth, xtb, xrtb, xposi, xrpsi, xchr, xfnme, xnme, xarbn, charset, xfail, xeps, xfnce).
4. `emit_flat_ir` switch in `emit_bb.c` collapsed to call `emit_bb_node` (with `g_emit.lbl_succ/.lbl_fail/.lbl_back/.op_name1/.op_name2/.child_fn` filled) for every kind except the few that need recursion into children (CAT, ALT, FENCE, ARBNO, ASSIGN_IMM, ASSIGN_COND).
5. GATE-PK PASS unchanged. GATE-M 855/855. `--run` smoke 186.

## Variant inventory (the only `if`s inside template arms)

Audit performed 2026-05-21 session #6. **23 non-IS_* `if` statements across 6 files.** All must survive the conversion:

| File | Lines | Class | How it survives |
|------|-------|-------|-----------------|
| `bb_pos.c` | 21,50,65,80 | FLAG-N (rpos vs pos) | `if (rpos)` stays; two `emit_textf` calls — one per branch with different literal text |
| `bb_tab.c` | 23,54,83,98 | FLAG-N (rtab vs tab) | Same pattern as bb_pos |
| `bb_capture.c` | 34 | NULL-guard (`!name \|\| !name[0]`) | Two-branch `emit_textf` |
| `bb_capture.c` | 43 | NULL-guard (op_name2 present) | Two-branch `emit_textf` |
| `bb_capture.c` | 53, 81 | CAP side-effect (`clbl && g_cap_fixup_cb`) | Side-effect call stays; `emit_textf` adjacent |
| `bb_arbno.c` | 34 | CAP side-effect | Same |
| `bb_brkx.c` | 41, 44, 48 | BOUNDS/ESCAPE | Pre-build escaped buffer `esc[]`, then `emit_textf("...%s...", esc)` |
| `bb_charset_helper.c` | 25 | MODE lookup (strcmp on c_fn_name) | Pre-resolve to `const char *rt_name`; single `emit_textf` |
| `bb_charset_helper.c` | 38, 41, 45 | BOUNDS/ESCAPE | Same as bb_brkx pattern |
| `bb_lit.c` | 25 | BOUNDS (preview snprintf for banner) | Pre-build preview string, `emit_textf` uses `%s` |
| `bb_lit.c` | 43 | MODE (`emit_bb_is_format_mode`) | KEEP the `if` — structural macro-mode vs inline-mode toggle |

**Rule:** if you find a non-IS_* `if` not in this table, STOP and update the table. New variants require explicit decision, not silent rewriting.

## Steps (groups; one commit per group; one GATE-PK per group)

Each group: read baseline `.raw` for the cells, identify variables, replace template arm body with `emit_textf(LITERAL_FROM_BASELINE, vars...)`, build, run GATE-PK, commit.

### Phase 1 — x86/text template arms (the bulk of the formatting indirection)

- [ ] **G1: simple pat** — `bb_rem`, `bb_arb`, `bb_abort`, `bb_eps`, `bb_fence` IS_X86 arms. No internal `if`. ~5 cells.
- [ ] **G2: int-arg pat** — `bb_len`, `bb_pos` (rpos branch), `bb_tab` (rtab branch). Keep `if (rpos)`/`if (rtab)`. ~5 cells.
- [ ] **G3: charset** — `bb_span`, `bb_any`, `bb_break`, `bb_notany` via `bb_charset_helper`. Pre-resolve rt_name; escape-loop produces `esc[]`. ~4 cells.
- [ ] **G4: LIT** — `bb_lit`. Has rodata literal label + format-mode `if`. ~1 cell.
- [ ] **G5: compound (recursive)** — `bb_cat`, `bb_alt`, `bb_arbno`, `bb_assign` (IMM+COND), `bb_capture`. These walk children via `emit_flat_ir` recursion. Conversion changes the in-arm formatting only; recursion stays. ~5 cells.
- [ ] **G6: tail** — `bb_brkx`, `bb_callout`, `bb_fail`, `bb_succeed`, `bb_dsar`. ~5 cells.

### Phase 2 — non-x86 backends (already use `emit_textf`; no `bb3c_format` to delete)

Survey first: how many JVM/NET/JS arms still use indirection vs. already use `emit_textf`?

- [x] **G7: JVM** — verify all JVM arms already use `emit_textf`; if any use indirection, convert.
- [x] **G8: NET** — same.
- [x] **G9: JS** — same.
- [ ] **G10: WASM** — currently all "deferred"; out of scope unless WASM lands.

### Phase 3 — rewire emit_flat_ir → emit_bb_node

- [ ] **G11: emit_flat_ir rewire.** Add static helper `flat_ir_via_node(nd, lbl_succ, lbl_fail, lbl_β)` that fills `g_emit` and calls `emit_bb_node`. Replace each non-recursive case in `emit_flat_ir`'s switch with this call. Recursive cases (CAT, ALT, FENCE, ARBNO, ASSIGN_IMM, ASSIGN_COND) keep their `emit_flat_ir_*` helpers.

### Phase 4 — delete the formatting layer

- [ ] **G12: delete emit_bb_x* helpers.** After G11, `emit_bb_xstar`, `emit_bb_xfarb`, `emit_bb_xfail`, `emit_bb_xlnth`, `emit_bb_xposi`, `emit_bb_xrpsi`, `emit_bb_xtb`, `emit_bb_xrtb`, `emit_bb_charset`, `emit_bb_xfnme`, `emit_bb_xnme`, `emit_bb_xarbn`, `emit_bb_xchr`, `emit_bb_xeps`, `emit_bb_xfnce` should be zero-caller. Delete bodies + decls in `emit_templates.h`. ~−2500 LOC.
- [ ] **G13: delete formatting primitives.** `bb3c_format`, `emit_label_define`, `emit_bb_box_banner`, `emit_text_jmp`, `emit_text_label`, `emit_outf`, `bb3c_flush_pending_*`, pending-label state globals (`g_bb3c_pending_*`). Templates use `emit_textf` directly; no formatter. ~−700 LOC.
- [ ] **G14: emit_bb_is_format_mode.** Last reference is in `bb_lit.c:43`. If that `if` can be resolved (one branch dead), delete the macro-mode infrastructure too.

## Per-group recipe (literal)

For each cell `BB_<KIND>.<ext>.raw`:

```bash
# 1. View baseline
cat baselines/per_kind/x86/text/BB_<KIND>.s.raw

# 2. Identify variable parts by inspection:
#    label names      → %s   (g_emit.lbl_succ/.lbl_fail/.lbl_back)
#    sid/nid          → %d   (g_emit.sid/.nid)
#    sval             → %s   (g_emit.op_name1 or nd->sval)
#    ival             → %d   (nd->ival)
#    rt fn name       → %s   (pre-resolved const char *)
#    escaped charset  → %s   (pre-built esc[] buffer)

# 3. Replace template arm body:
#    BEFORE: 8-15 lines of bb3c_format(out, "", "lea", "rax, [rip + Σlen]"); etc.
#    AFTER:  one emit_textf("    .intel_syntax    noprefix\n    lea ... \n    jmp %s\n%s:    jmp %s\n", lbl_succ, lbl_back, lbl_fail);

# 4. Build + gate
make -j4 scrip && bash scripts/test_per_kind_diff.sh
# Must show: PASS=<previous count or +N>, FAIL=0, GONE=0

# 5. Commit + push.
```

## Failure modes & rules

- **GATE-PK FAIL after conversion:** the literal text didn't match. Diff the cell — usually a missing `\n`, wrong column padding, or wrong variable substitution. DO NOT re-freeze; fix the literal.
- **GATE-PK GONE>0:** something stopped emitting. Likely a deleted call site without replacement. Check the diff.
- **Build error after delete:** an `emit_bb_x*` helper still has a caller. Find it, route through `emit_bb_node` first (G11), then delete (G12).
- **Variant `if` you can't classify:** STOP. Add a row to the variant inventory table above. Do not silently rewrite.

## Gates (every group)

```
make -j4 scrip
bash scripts/test_per_kind_diff.sh    # PRIMARY: must show PASS unchanged or +N, FAIL=0
bash scripts/test_gate_em_template_matrix.sh   # 855/855
```

`--run` smoke run once per phase (1, 2, 3, 4):
```
bash scripts/test_smoke_snobol4_jit.sh   # PASS=186 invariant
```

Beauty gate (`test_gate_ec_uni_complete.sh` GATE-1) remains SUSPENDED per Lon 2026-05-21 directive.

## Session Setup

```bash
cd /home/claude/SCRIP && make -j4 scrip
bash scripts/test_per_kind_diff.sh   # confirm clean baseline before starting
[ -d /home/claude/x64 ] || git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64
```

## Watermark

```
SCRIP: ddd08f01   (PPV-8 landing: bb_abort IS_X86, dead IS_BIN guards, beauty suspended)
GATE-PK: PASS=401 FAIL=0 STUB=658
```

## Authors

Plan drafted Sonnet 4.6, 2026-05-21 session #6. Three-developer agreement: Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet.

## Session #7 watermark (2026-05-21, Sonnet 4.6)

```
SCRIP: 1974df8a
GATE-PK: PASS=406 FAIL=0 STUB=653
Matrix:  855/855

G1 ✅  bb_abort/fence/rem/arb IS_X86 → emit_textf verbatim text + %s/%d splices
G2 ✅  bb_len/pos/tab IS_X86 → emit_textf (bb_pos insn_* helpers unchanged; banner converted)
G3 ✅  bb_charset_helper data-section preamble → emit_textf (emit_seq_port_call_rip unchanged)
G4 ✅  bb_lit banner + mov-rdx line → emit_textf (insn_*/emit_seq_*/emit_text_jmp unchanged)
NEXT:  G5 — bb_cat/alt/arbno/assign/capture (compound/recursive; in-arm formatting only)
```

Approach confirmed: take raw baseline text verbatim, splice `%s`/`%d` for variable parts
(labels, integers, node ids). One `emit_textf` per instruction line. No padding/width math.
G3/G4 partial because `emit_seq_port_call_rip`/`insn_*` are not `bb3c_format` wrappers.

## Session #8 watermark (2026-05-21, Sonnet 4.6)

```
SCRIP: 6ee301e9
GATE-PK: PASS=407 FAIL=0 STUB=652
Matrix:  855/855

G5 ✅  bb_arbno banner, bb_capture 2 banners -> emit_textf
G6 ✅  bb_fail banner+jmps, bb_dsar banner, bb_brkx 30+ bb3c_format -> emit_textf
sweep ✅ bb_atp_template, bb_eps last banners -> emit_textf

Zero emit_bb_box_banner, zero bb3c_format in all BB_templates/ and SM_templates/.
emit_text_jmp stays in bb_pos/bb_lit (fused cjmp output, cannot be emit_textf).
NEXT: G11 — emit_flat_ir rewire (path-a/b decision from Lon required). G7/G8/G9 surveyed clean — all non-x86 arms already use emit_textf/ jvm_*/net_*/js_escape directly. No indirection to remove.
```
