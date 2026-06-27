# GOAL-ICON-GATE-WIDEN.md — Icon native-coverage rung ladder (gate-first conversion)

**Premise (proven 2026-06-24, see `ICON-BB-PUNCH-LIST-2026-06-24.md`):** the dominant blocker for
the 89 EXCISED + 5 FAIL Icon rungs is the native-eligibility GATE
`graph_native_emittable_mode()` (`src/driver/scrip.c:288`), NOT absent lowering or templates. Most
EXCISED programs lower to clean IR and have real `bb_*.cpp` templates; the gate's conservative
whitelists reject them. This ladder widens the gate construct-by-construct, building the one missing
box arm only where genuinely absent, and TESTS every rung through the three-mode suite. The
`[SMX]→EXCISED` mechanism makes every half-built rung fail LOUD, never silently wrong — so each rung
is floor-safe.

**Discipline (every rung):** read canonical JCON `ir_a_*` first · keep `bb_*` templates pure
`x86()` · no value stack · one-register ζ-frame · four Greek ports · test both native modes ·
`[SMX]` excise on any uncovered shape · floor (suite PASS) must not drop.

**Watermark:** HEAD `a872f56`, suite **153/283** (run), smoke 12/12 m3+m4, 5 FAIL. **Local tree
(UNCOMMITTED, this session): suite 155/283 both modes (records_basic + records_field_assign now native),
FAIL 5 (unfinished record shapes EXCISE), smoke 12/12, all discipline gates green.**

---

## RUNG R1 — RECORDS (Tier A, gate-widen + register-order fix) ⬅ PARTIAL (2/5 native, 3 EXCISE)

**Target:** rung24 ×5. **LANDED (2026-06-24, Claude): records_basic + records_field_assign now native
in BOTH m3+m4.** Suite 153→155, FAIL stays 5 (unfinished shapes EXCISE, never FAIL), smoke 12/12, all
discipline gates green.

**Root cause (traced, gate-instrumented):** record alloc (`dat_construct`), field read
(`bb_field_get`), and the runtime route (`by_name_dispatch` → `dat_construct`) ALL already work. The
fixes were: (1) `dat_register` ran AFTER the gate, so `rt_builtin_is_known("point")==0` at gate time;
(2) `rhs_kind_ok` didn't whitelist a record-constructor call as an assignment RHS.

- [x] **R1-S1** — `icn_register_record_types(s2)` helper hoists `IR_RECORD_DEF → dat_register` BEFORE
      both native gates (m3 + m4) in `scrip.c`. `rt_builtin_is_known("point")` now true at gate time.
- [x] **R1-S2** — `rhs_kind_ok` accepts `IR_CALL dval==3.0 && dat_find_type(sval)` (constructor RHS).
- [x] **R1-S3** — bare `IR_CALL(point)` routes `CALL_ROUTE_FN`; field read via `bb_field_get` works.
- [x] **R1-S4** — shared-object double-emission fixed: `flat_drive_field_get` (and `_field_set`) skip
      re-walking an object box already on the chain or slotted (was m4 duplicate-label asm error).
- [x] **R1-S5 (FIELD_SET)** — `b.x := v`: added `dat_field_set` runtime (`driver_data.c`), `TT_FIELD`-LHS
      → `IR_FIELD_SET` lowering, `bb_field_set.cpp` template (pure `x86()`), `emit_core` dispatch arm,
      `descr_chain_arity` entry, Makefile. records_field_assign PASS both modes.
- [ ] **R1-S6 (binop-of-fieldget value flow)** — `p.a + p.b` (proc_arg, two_types) EXCISES: a binop fed
      by FIELD_GET producers on the spine resolves `op_sa` to the field-get's OBJECT var slot, not the
      field-get RESULT slot (chain operand-ref wires the wrong node when two consecutive arity-0
      producers feed a binop). Gate guard added (excise any binop with a FIELD_GET γ-predecessor). FIX:
      the chain operand-ref builder must wire a binop operand to the producer that WROTE the slot, not
      the producer's own operand. Shared with the general two-producer chain wiring (touches R3/R5).
- [ ] **R1-S7 (generator-RHS field-set)** — `every c.n := 1 to 3` (record_loop) EXCISES: FIELD_SET whose
      RHS is a generator (`1 to 3`) leaves `op_sb` unfilled. Needs generator-into-field value flow
      (the generator yields into the field-set's rhs slot each iteration).

---

## RUNG R2 — SUSPEND resume-spine (Tier B1, the long-standing top lever)

**Target:** rung03 ×3 (`suspend_gen`, `suspend_gen_compose`, `suspend_gen_filter`). Design fully
signed off in `DESIGN-ICON-SUSPEND.md` §4A (Lon ruling: `(void*,int entry)` proc re-entry is allowed
because the dispatched code is emitted x86, not a C box). Pieces 1/3/4 + chain wiring already landed
(`aa16969`/`ecef926`). Two pieces remain.

- [ ] **R2-S1** — Piece 2: prologue entry-dispatch in `xa_flat.cpp` frame-active arm, gated on a new
      `g_gen_proc_active` (set in scrip.c proc-emit loop from `proc_table[pi].is_generator`):
      append `cmp esi,0 / jne <flat_lbl_β>` after `mov r12,rdi`. esi≠0 ⇒ resume ⇒ jump the
      chain β (already routed to the suspend resume β by `ecef926`). Non-generator procs byte-unchanged.
- [ ] **R2-S2** — Piece 5: caller gen-call box. Add `int rt_proc_is_generator(const char*)` (reads
      `proc_table`); in `bb_call_route_classify`, when `rt_proc_is_registered && rt_proc_is_generator(fn)`
      pick `CALL_ROUTE_PROC_GEN`; new box α=`rt_proc_call_gen` (stage args, value→slot,
      `cmp type,99: je ω; jmp γ`), β=`rt_proc_resume_gen` (value→slot, same test). Model on
      `bb_call_proc_staged.cpp`.
- [ ] **R2-S3** — Flip the gate: delete `if (nd->op == IR_SUSPEND) return 0;` (scrip.c). Build.
- [ ] **R2-S4** — Run rung03 ×3 both modes. Expect `1\n2\n3\n4\n` etc. Debug slot/label/ABI. Verify
      floor + smoke 12/12 + rung03 ×3 PASS. `_compose` (two sequential activations) and `_filter`
      (count-down) must both pass — single-activation arena suffices (never two live at once).

---

## RUNG R3 — SCAN double-emission (Tier B2)

**Target:** rung06 ×2 (`cset_upto_basic`, `cset_cset_var`) + the every+scan cluster. Root cause
(verified last session): `flat_emit_arg_subchain` (`emit_bb.c:2224`) re-emits already-emitted boxes
because it doesn't dedup against the chain-body emitted set (`flat_chain_set_has`, `emit_bb.c:2762`).
m3 doubles output (`6\n6`), m4 asm-fails (label defined twice).

- [ ] **R3-S1** — Thread the chain-body emitted-set into `flat_emit_arg_subchain`; skip any box
      already in the set (the `flat_chain_set_has` guard the every-drive uses). 
- [ ] **R3-S2** — Drop the `gen_scan_body_slotful` gate reject for the now-covered every+scan shape.
- [ ] **R3-S3** — Run rung06 ×2 + every+scan rungs both modes; expect no doubling, asm clean.
      `cset_cset_var` (runtime variable-cset `any(vowels)`) may need separate variable-cset dispatch
      — split to R3-S4 if so.

---

## RUNG R4 — FIND as a resumable generator (Tier B3)

**Target:** rung08 `strbuiltins_find_gen` (FAIL rc=124 hang). `find` in a generator context isn't
advancing on resume — its β re-runs from the start instead of from the saved position.

- [ ] **R4-S1** — Read canonical `fscan.r` find + JCON resume wiring; the find box must save its match
      position and advance on β (like `bb_to`/`bb_scan_move` reverse-on-resume). Wire `bb_scan_find` β.
- [ ] **R4-S2** — Run rung08 both modes; expect termination + correct generated positions.

---

## RUNG R5 — CROSS-ARG ALTERNATION value flow (Tier B4 + A3/A4)

**Target:** rung13 ×2 hard FAILs (`alt_alt_cross_arg`, `alt_alt_cross_arg_sideeffect`) +
EXCISED alt cluster (augconcat/nested/filter) + queens. Also frees rung14 `limit_alt`/`limit_str`.

- [ ] **R5-S1** — Build alt-value-in-binop/conj emitter (the alt arm's value must reach a consuming
      operand slot across argument positions). Canonical `ir_a_Alt` MoveLabel/IndirectGoto → SCRIP
      `bb_alt` counter already gives N-arm resume; the gap is the cross-product value plumbing.
- [ ] **R5-S2** — Arm-scope `alt_safe_kind` (only the alt's arms must be alt-safe, not the whole
      graph) and relax `alt_arms_all_simple_lit` to admit IR_VAR/IR_CALL arms. (Verified: blanket
      arm-scoping without S1 regresses 3 rungs — S1 MUST precede S2.)
- [ ] **R5-S3** — Run rung13 cluster + rung14 ×2 + queens-applicable; floor must not drop.

---

## RUNG R6 — INITIAL / STATIC persistent-static store (Tier C1)

**Target:** rung21 ×2, rung25 ×3 + queens/deal/post/tgrlink/ipxref. Needs the persistent-writable
`.bss` arena — the GVA `__gva` array extended (ICON-AUDIT §D + GOAL-ICN-GVA-M3). m3 RX slab is RO,
so this also needs the m3 heap-arena from GOAL-ICN-GVA-M3.

- [ ] **R6-S1** — (m4) Allocate one persistent `.bss` cell per `initial` site / `static` var in the
      `__gva` arena; `initial`'s done-flag + body run-once on first activation; address `[rbx+k*16]`.
- [ ] **R6-S2** — Lower `TT_STATIC_DECL` to a real persistent slot (currently `IR_SUCCEED` no-op);
      `bb_initial.cpp` (dead) wired to the done-flag-guarded body.
- [ ] **R6-S3** — Lift the gate's `IR_INITIAL ⇒ 0` reject for the proven shape. Run rung21/rung25.
- [ ] **R6-S4** — (m3) extend to in-process via GVA-M3 heap arena (depends on GOAL-ICN-GVA-M3).

---

## RUNG R7 — TABLES datatype (Tier C2)

**Target:** rung13/rung23 table ×9. Lists work; tables (`T[k]`, default, member, delete, iterate)
don't — `IDX_GET`/`IDX_SET` on a table value isn't wired (only list subscript).

- [ ] **R7-S1** — Table datatype create + default; `T[k]` read (`IDX_GET` on table) + write
      (`IDX_SET` on table) via `by_name_dispatch` (`table`/`member`/`insert`/`delete`/`key` already in
      known[]). Admit in gate.
- [ ] **R7-S2** — `every k := key(T)` / `!T` iteration generator. Run rung23 ×5 + rung13 table ×4.

---

## RUNG R8 — SORT + top-level list value-gen (Tier C5)

**Target:** rung15, sort ×3, shuffle/deal/post. `every put(a, expr)` accumulate + `sort()`.

- [ ] **R8-S1** — `every put(L, expr)` accumulate at top level (value-flow of a generator into a
      list-mutating builtin). `sort(L)`/`sortf` builtin admit.
- [ ] **R8-S2** — Run sort/shuffle/deal/post rungs.

---

## RUNG R9 — COEXPRESSIONS / create (Tier C4, true JCON transcription)

**Target:** micro.icn, args, and any `create e` / `@C` / `^C`. The ONE family where SCRIP has a
genuine port-wiring gap — transcribe canonical `ir_a_Create` + `ir_ResumeValue`/`ir_CoRet`/`ir_CoFail`
directly. Large (coroutine stack). Deferred until R1–R8 land.

- [ ] **R9-S1** — `IR_CREATE` lower + coexpr activation (separate stack/frame); `ir_ResumeValue`
      resume protocol. `@`/`^` operators.

---

## Per-rung gate (run before declaring any rung done)
```bash
bash scripts/build_scrip.sh && make libscrip_rt
bash scripts/test_icon_rung_suite.sh --rung <rungNN>           # both native modes
bash scripts/test_icon_rung_suite.sh --mode run | grep PASS=   # floor check
bash scripts/test_smoke_icon.sh                                # 12/12 m3+m4
bash scripts/test_gate_icn_no_stack.sh
bash scripts/test_gate_icn_one_reg_frame.sh
bash scripts/test_gate_icn_semicolon_required.sh
bash scripts/test_gate_icn_local_no_nv.sh
```

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
