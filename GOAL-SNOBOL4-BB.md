**SESSION WATERMARK — 2026-06-13 · Sonnet 4.6 · SCRIP=eb98b8e. This session: fixed M3-CONCAT-MULTIPART. `bb_gvar_assign_concat.cpp` rdi BINARY ptr (destination variable name) was wrong in BOTH arms: lit_s used `_.op_sval` (NULL for ASSIGN_CONCAT — never set by flat_drive_gvar_assign), multi-part used `_.bb_ls` (scratch label-name buffer, not the var name). Both → `IR_LIT(_.node).sval` (permanent IR dest-var-name ptr). TEXT arm byte-identical (reads `_.bb_ls` label); only the BINARY movabs immediate changed. GATES at eb98b8e: smoke 7/7/7 HARD · pat-rung m2/m3/m4 19/19/19 no-SKIP · fence HARD. Corpus this container: M2=172 M3=152 (+8 from fix) M4=148 (counts container-sensitive — stash-baseline before treating as regression). 055 now green all three modes. Next: M4-SMOKE-REGRESS or M4-FENCE cluster per ladder priority.**

---

## 🔴🔴🔴 TOP PRIORITY — GROUND-ZERO PATTERN BUILDING THROUGH RT FUNCTIONS · NO BB_INVARIANT

Every pattern BUILT at runtime via `rt_pattern_build`/`rt_pattern_stitch_cat`/`rt_pattern_stitch_alt`. All 8 `bb_pattern_*.cpp` builders done — `ins*`=0 ✅. All D7 rungs DONE. Full ladder: `SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md`. GATE: smoke 7/7/7 · pat-rung m2==m3==m4 no-SKIP · corpus non-decreasing · fence HARD.

---

## ⛔ SESSION DIRECTIVE — modes 2/3/4 CO-EQUAL HARD GATES. See `SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md` D7.

## ⭐ PIVOT (Lon 2026-06-07) — BUILDERS REPLACE SM · DT_P SEAL-ON-MATCH

(1) BB_INVARIANT/REF_INVARIANT — quit using. (2) No constant-folding. (3) BBs replace ALL SM. (4) ✅ bb_pat_*→bb_match_*. BUILDER TAXONOMY: `bb_pattern_nullary`·`_unary_i`·`_unary_s`·`_unary_p`·`_stitch`·`_capture`·`_defer`. DT_P: build-unsealed, seal-on-match.

## 🔴🔴 #0 PRIORITY — OWNED 5-STAGE BUILD

Master ladder: `SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md`. Arch: `.github/ARCH-SNOBOL4.md`. RoE: BBs/XAs through templates only; one template may serve multiple IRs; no runtime calls without ledger stamp; probe-first vs sbl; one rung = one commit; m2/m3/m4 co-equal hard gates; corpus non-decreasing HARD.

## MODE 4 BUG LADDER

Inventory: smoke m4 **7/7** · pat-rung m4 **19/19 no-SKIP** · broad m4 corpus **155/280** · beauty m4 **1/17**.

- [ ] **M4-SMOKE-REGRESS** — m3 concat + m4 define fail with `< /dev/null`. m4 define: upstream regression from 14ae014 (`bb_unify.cpp` duplicate label `.Lx2_0`). Bisect to confirm; fix define duplicate-label.
- [ ] **M4-CRASH** — `scrip --compile` must never abort/segfault: 29 corpus SKIPs + 4 beauty emit-crashes.
- [ ] **M4-FENCE** — ~10 corpus fails (061/062/064/066/100/101/103/108/110/112). FENCE matches null L→R, fails on retreat (SPITBOL p.204).
- [ ] **M4-ONESHOT** — probe: `'aab' ? SPAN('ab') . A 'b' . B` → sbl `:`, m4 `aa:b`. Fix: β→ω on span twins; audit ANY/NOTANY/BREAK/LEN/TAB/RTAB/POS/RPOS β arms.
- [ ] **M4-CAPTURE-COND** — probe: `V='unset'; S='ab'; S 'a' . V 'x' :F(NO)` → m4 `nomatch a`, sbl `nomatch unset`.
- [ ] **M4-STARVAR** — 070/071/073/075/061+053 class. PB-RB-6: BB_PAT_BUILD for `*E`/`$NAME`/pattern-valued var.
- [ ] **M4-ARBNO-REENTRY** — matched ARBNO instance's remaining alternatives not re-enterable on backtrack.
- [ ] **M4-DATA** — 091/092/093/094/095/096.
- [ ] **M4-DEFINE** — 084/088/089.
- [ ] **M4-BUILTIN** — 076/077/081/082/097/006/030/020/014/015.
- [ ] **M4-BEAUTY** — 16 fails: link=5, diff=7, emit=4.
- [ ] **M4-REPL-NATIVE** — replacement natively (PB-RB-7). Probe: `S 'b' = 'X'` → `aXc`.

## ⛔ FACT RULE — LANGUAGE-BLIND BB/XA TEMPLATES (Lon, 2026-06-03)

No language-specific logic in any BB or XA template. Templates dispatch on IR shape/flags only. FORBIDDEN in `src/emitter/BB_templates/` and `XA_templates/`: `IR_LANG_*`, `LANG_*`, `is_<lang>`, language-named arms, hardcoded language-builtin names. Language-varying behavior → runtime (by-name dispatch) or LOWER (distinct IR shape). Inventory: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md` (XA clean 2026-06-03). COMPLETION TEST: Tier-1 grep returns 0.

## ⛔ TEMPLATE SPEC v2 (Lon 2026-06-04) — REGENERATE, DON'T PATCH

No local variables · ONE return per PLATFORM · IF()/FOR() for conditionals/loops · ONE source line = ONE asm line · real Greek α β γ ω · no MEDIUM_TEXT/MEDIUM_BINARY at top level · zero emit_fmt() · zero C comments · zero blank lines · **ONE-IR-ONE-LOGIC:** N IR→1 BB allowed; 1 IR→1 BB norm; 1 IR→N BB never (split IR kinds in LOWER) · **EMIT-BLIND:** template reads only its own `_` context — never dereferences a neighbor node. Regenerate whole, never patch. Full directive: `HANDOFF-2026-06-04-OPUS48-SNOBOL4-BB-HYGIENE-SWEEP-SPEC-V2.md`.

## ⛔ `bb_bin_t` IS ABOLISHED (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

`bb_bin_t {sites,labels,is_def,bytes}` and `bb_emit_asm_result`/`bb_emit_asm_result_pairs` are DELETED. Every BB template returns ONE concatenation of `x86(...)` calls emitted by `bb_emit_x86(out)`. Patch sites are in-band tagged records (`L`/`J`/`D`/`L(n)`/`E`/`F`); `bb_emit_x86` discovers each byte position as it copies. FORBIDDEN: `struct bb_bin_t`, `bb_bin_t bin`, `bb_emit_asm_result(...)`, `bin.sites`/`bin.labels`/`bin.is_def`, `(int)b.size()` as patch offset, anywhere in `BB_templates/`/`XA_templates/`/`emit_str.*`. Not-yet-converted box → `x86_bomb(msg)` stub. COMPLETION TEST: (a) `emit_str.h` declares neither; (b) gate `test_gate_no_bb_bin_t.sh` reads 0; (c) every BB template emitted via `bb_emit_x86`; (d) build rc=0; (e) body byte-identical across four GOAL files.

## ⛔ ONE MEDIUM, INVISIBLE (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

A template NEVER writes an instruction twice (once as GAS, once as raw bytes) and NEVER branches on medium. Every instruction goes through ONE `x86(mnem,…)` call; encoder switches medium internally. FORBIDDEN in `BB_templates/*.cpp`: `x86_Lrec`, `x86_Jrec`, `x86_Drec`, `x86_b1(`, `x86_b2(`, `x86_b3(`, `bytes(`, `u8(`, `u32le`, `u64le`, any `IF(MEDIUM_BINARY,…)` or `IF(MEDIUM_MACRO_DEF,…)` carrying instruction bytes. Missing encoder → ADD to `x86_asm.h`. TEXT-only annotations (label/comment) with no binary counterpart are allowed. COMPLETION TEST: (a) zero raw-byte producers + zero `IF(MEDIUM_BINARY/MACRO_DEF)` in any `BB_templates/*.cpp`; (b) every instruction via `x86()`; (c) gate green under `--strict`; (d) body byte-identical across four GOAL files.

## ⛔ NO C BYRD-BOX FUNCTIONS (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

A byrd box is emitted machine code entered by JUMPING to α or β label — never a C function `DESCR_t NAME(void*,int entry)`. The `(ζ,int entry)` signature is FORBIDDEN. Brokered-BB calling convention is gone. `bb_box_fn` typedef KEEPS `(void*,int entry)` — survivors `rt.c:480/529/595` (C α-entry into DEFINE blobs); convert those to jmp-threading before touching the typedef. COMPLETION TEST: (a) grep for `(void*,int entry)` in defs == 0; (b) no `bb_broker`; (c) body byte-identical across five GOAL files.

## ⛔ NO VALUE STACK — EVER (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

No value stack in any form. Every box-held value lives in `[rip+disp]` (RO) or `[r12+off]` (RW frame). `g_vstack` is DELETED and must stay at zero. FORBIDDEN: global/static push/pop value arena, `rt_push_*`/`rt_pop_*`/`vstack_*`. KEEP (not value stacks): Prolog trail, choice-point ledger, C call stack for recursion, ARBNO per-activation frame array. Residual `vstack_*/rt_vstack_ops_t` scaffolding in `rt.c` is dead/aborting — do not wire. GATE: `test_gate_no_vstack.sh`. COMPLETION TEST: (a) `grep -rn 'g_vstack' src/` == 0; (b) no new push/pop arena; (c) body byte-identical across five GOAL files.

> **⭐⭐⭐ CORRECTED PATTERN ARCHITECTURE (Lon 2026-06-01).** A SNOBOL4 pattern = graph of EMITTED BYRD-BOXES (`bb_box_fn`). `DT_P` = HEAD BLOCK = `{entry, OUTSIDE-γ slot, OUTSIDE-ω slot}`. Build = SPLICE (wire ports). Runtime `STITCH_SEQ`/`STITCH_ALT` = runtime twins of `wire_seq`/`wire_alt`. `BB_LINK` = pure-tail `jmp [r12+slot]` for shared sealed heads.

## ⛔ SHARED-LOWERER ONE-FILE CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

`lower.c` = ONE file, ONE entry (`lower2`), ONE switch over `tree_e`. Prolog split to `lower_prolog.c` (d6d93c6). Rules: (1) ONE case per `TT_*`. (2) Language variation inside the case, branch on `cx.lang`. (3) Edit only your language's arm. (4) Missing arm → `lower_unhandled` (loud), never silent. (5) Shared scaffolding additive; signature changes lockstep across all three GOAL files. (6) `prove_lower2.sh` must stay green. COMPLETION TEST: (a) no duplicate `case TT_` per switch; (b) every case ends in real arm or `lower_unhandled`; (c) body byte-identical across three GOAL files; (d) `prove_lower2.sh` green.

## ⛔ TEMPLATE-ONLY EMISSION — ONE-DISPATCH CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

`emit_core.c` ONE switch over `IR_e` → per-box template fns in `{BB,SM,XA}_templates/`. Rules: (1) ONE dispatch case per `IR_*`. (2) ONE template file per box. (3) Edit only your language's boxes. (4) Missing box → loud default (assert/abort). (5) Makefile `RT_PIC_SRCS` append-only. (6) Gates: `util_template_purity_audit.sh`, `test_gate_em_template_byte_identity.sh`, `test_gate_em_template_matrix.sh` green. COMPLETION TEST: (a) no duplicate `case IR_` in `emit_core.c`; (b) zero forbidden byte-emitters outside templates; (c) body byte-identical across three GOAL files; (d) gates green.

## ⛔ NO DUPLICATED LOGIC (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

Each piece of logic written ONCE. Box = PORT work (α/β/γ/ω wiring). Runtime = VALUE work (build term, compare, arithmetic, concat). FORM 1: same algorithm in two media — delete both, call `rt_*` once. FORM 2: emit-time logic that is a runtime job — belongs behind one `rt_*` call. FORM 3: operand box reimplemented inside consumer — consumer reads producer's slot, not the value inline. COMPLETION TEST: (a) no algorithm in both TEXT and BINARY arm; (b) no emit-time reimplementation of runtime value work; (c) no `pBB->α->ival/sval/dval` inside consumer box; (d) body byte-identical across four GOAL files.

## ⛔ X86-64 REGISTER / SUBJECT-MODEL CONVENTION (FACT — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

| Reg | Name | Role |
|-----|------|------|
| R13 | Σ | subject BASE ptr |
| R14 | δ | CURSOR (moving) |
| R15 | Δ | subject LENGTH/END (fixed) |
| R12 | ζ | BB-local RW FRAME base `[r12+off]` |
| R10 | — | per-BLOB DATA-block ptr |
| rbx | — | callee-saved scratch |
| rbp | — | DEFINE'd frame ptr when active |

γ-success return: `rax=σ ptr`, `rdx=δ int`. Changing any assignment = lockstep update across all three GOAL files.

## ⛔ PER-BOX LOCAL STORAGE (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

Every box value: **(RO)** `[rip+disp]` sealed data, or **(RW)** `[ζ+off]` per-sequence frame. No AG ring, no value stack, no name-table round-trip for intermediates. COMPLETION TEST: (a) no `bb_exec_once`/AG-ring on mode-3/4 path; (b) no `g_vstack`/`rt_push_*`/`rt_pop_*`; (c) no `NV_GET`/`NV_SET` for intermediate values; (d) no `movabs …&pBB->slot`; (e) BINARY and TEXT arms do identical processing.

---

## ⭐⭐ REBUILT LADDER — PB-RB (CORRECTED PATTERN ARCHITECTURE)

`wire_seq`/`wire_alt` shared LOCKSTEP helpers. All PB-RB gates mode 4 HARD. Open:

- [ ] **PB-RB-5** — Operand-variant element matchers. `LEN(N)`/`SPAN(cvar)`: existing box reads operand late from ζ-slot. Prove + mode-3 `S LEN(2)`, `S SPAN('abc')`.
- [ ] **PB-RB-6** — BB_PAT_BUILD for structural variance. `*E`/`$NAME`/pattern-valued var.
- [ ] **PB-RB-7** — REPLACEMENT BB (ph.4) + SUBSTITUTION BB (ph.5). `S 'b' = 'X'` → `aXc`.
- [ ] **PB-RB-CONV** — IR_SCAN convergence: retire dual shape once native chain covers corpus breadth.
- [ ] **PB-RB-OPT** — All-invariant BLOB freeze after correctness rungs done.

## BROK residue (eradication ✅)

- [ ] ARBNO child-β re-entry gap: matched instance's remaining alternatives not re-enterable on backtrack. Own rung.
- `bb_box_fn` typedef survivors `rt.c:480/529/595` — convert to jmp-threading before touching typedef.

## Architecture references

- Mode-2 oracle: `src/interp/IR_interp.c`
- Flat driver: `src/emitter/emit_bb.c` (`codegen_gvar_flat_chain_body`, `walk_bb_flat`)
- Template dispatch: `src/emitter/emit_core.c`
- Template dir: `src/emitter/BB_templates/bb_pat_*.cpp`
- Lowering: `src/lower/lower.c` + `lower_prolog.c` + `lower_program.c`
- Bomb infra: `src/emitter/emit_str.{cpp,h}`
- M4 scan routing: literal pattern → `bb_scan_stmt` literal arm → `rt_scan_lit`; non-literal + named-var subject + NO repl → `flat_drive_scan_native`; else → `rt_scan` shim.

## ⏸ PARKED

- **M2-ARBNO-SHY** — m2 ARBNO greedy vs sbl shy; m4 already correct — mode-2-only bug.
- **SR-2** — save/restore→ζ-frame migration.
- **LOWER2 BOX LADDER** — parked.

## Session log

**Watermark (D7 all rungs ✅; eb98b8e; 2026-06-13 Sonnet 4.6).** smoke 7/7/7. pat-rung m2/m3/m4 19/19/19 no-SKIP. fence HARD. M3-CONCAT-MULTIPART fixed: bb_gvar_assign_concat rdi BINARY ptr → IR_LIT(_.node).sval in both lit_s arm (was _.op_sval, NULL) and multi-part arm (was _.bb_ls scratch buf). TEXT byte-identical. Corpus this container M3 144→152. Next: M4-SMOKE-REGRESS or M4-FENCE per ladder.

## Session Setup

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64
```

Gates — modes 2/3/4 CO-EQUAL HARD:
```bash
bash scripts/test_smoke_snobol4.sh                              # 7/7/7 HARD (currently 6/7 — upstream regressions)
bash scripts/test_snobol4_pat_rung_suite.sh                     # 19/19 no-SKIP
SCRIP=$PWD/scrip bash scripts/test_mode4_only_corpus_snobol4.sh # 155/280 floor
bash scripts/test_gate_em_beauty_subsystems_mode4.sh            # 1/17 floor
bash scripts/test_gate_sno_pat_reg.sh                           # fence HARD
```

## Hard-won facts (do not re-derive)

- `flat_drive_cat_arms(pBB=NULL,arms,nc,...)`: pBB=NULL supported — emit tail trampolines explicitly.
- `operand_aux` is PER-GRAPH: walking a sub-graph (ARBNO inner, pattern graphs) requires switching `g_emit_cfg` first (save/restore, cf. emit_bb.c:1477).
- Flat emission of driver-owned kinds (PAT_CAT/PAT_ALT/PAT_FENCE/GCONJ) starts at JOIN node; always `ir_skip_alt_arms` before single-node walk.
- SPITBOL primitives ONE-SHOT: SPAN/BREAK/ANY/NOTANY/LEN/TAB/RTAB/POS/RPOS. Only BREAKX/ARB/ARBNO/BAL generate rematch alternatives. No quickscan heuristics (&FULLSCAN non-zero, p.123).
- Stream-fn by-var kind-split = 13 sites: IR.h, scrip_ir names, lower kind-select, lower leaf-predicate, m2 case-label, is_pat_chain_elem, walk_bb_flat FILL, emit_core dispatch, bb_templates.h, new template, Makefile ×2, prove_lower2, emit_per_kind_audit.
- emit_fmt has ONE static buffer — never two emit_fmt in one x86() call.
- Broad-corpus gate counts are container-sensitive — stash-baseline before treating count as regression.
