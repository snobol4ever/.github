# GOAL-ICON-BB.md — Icon, 100% Byrd Boxes, from zero

**Reset:** 2026-05-28. All Icon legacy SM dispatch deleted. No env-gate `SCRIP_ICN_BB`. The BB-graph lowering is the only path. Every BB template MEDIUM_BINARY arm that isn't real ABORTs loudly at a named site.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7 · Claude Sonnet 4.6
**Architecture pointers:** `ARCH-ICON.md` · `ARCH-x86.md` · `GOAL-ICON-BB-NATIVE.md` · `.github/test_icon.c` · `.github/jcon_irgen.icn`.

---

## Premise

Icon IS a Byrd Box graph. Every construct is a box. The whole program is one connected port-graph. **There is no SM around it at all.**

- Mode 2: driver detects Icon and calls `bb_exec_once(s2->sm.bb_table[main_bb_idx])` directly. `sm_interp_run` is never entered. Icon SM stream is empty.
- Modes 3/4: emit `lea r10, [rip + Δ_root]; jmp .Lroot_α`. `SM_HALT`. Boxes are CODE+DATA in `bb_pool` (mode 3) or in the linked binary's `.text`/`.data` (mode 4). Inter-box transitions are `jmp rel32`. No `call`, no `ret`, no SM dispatch loop, no broker, no C walker in mode-4.

Per `test_icon.c`: every construct gets `_start` / `_resume` / `_succeed` / `_fail` labels wired by flat `goto`. Three-column form: `LABEL / ACTION / GOTO`. That is the target shape.

---

## ⛔ GOAL RULE (Icon SM streams)

**ZERO SM opcodes emitted for an Icon program.** No `SM_BB_INVOKE`, no `SM_HALT`, no `SM_CALL_FN`, nothing. Driver calls `bb_exec_once(main_bb_graph)` directly.

Completion tests:
```bash
./scrip --dump-sm any_icon_program.icn        # ; SM_sequence_t  count=0
./scrip --dump-sm any_icon_program.icn | grep -c '^   [0-9]'   # 0
```

---

## Current state (2026-05-29, IBB-8b string relops landed, one4all `0e926c16`)

| Mode | Path | Canonical-5 | Full corpus (m2-OK filter) |
|------|------|-------------|---------------------------------|
| 2 (`--interp`) | `bb_exec_once` C tree-walker | **5 / 5** | — |
| 3 (`--run`) | `bb_build_flat` → seal RX → call slab | **5 / 5** | **same-sweep 22→28 PASS (+6), SEGV 0** |
| 4 (`--compile`) | deferred per Lon directive | hello.icn ✅ (`f387a7b9`) | n/a |

Canonical-5: `hello.icn`, `add.icn`, `every_to.icn`, `alt.icn`, `full.icn`. All byte-identical m2 vs m3.

Mode-3 corpus delta IBB-7 → IBB-8a: **+15 PASS (17→32), SEGV 2→0**. Two fixes: (1) xa_flat slab call-alignment (`sub/add rsp,8`) cleared the DT_R `fprintf("%g")` SEGV in `rung26_pow_pow_expr` + `rung37_augop_pow`; (2) DT_R-producing write args (BB_BINOP / BB_BINOP_GEN) now route through `rt_pop_write_any_nl` with canonical `real_str` formatting instead of the int-write trailer printing raw IEEE bits — fixed `rung26_pow_pow_assoc` and ~10 other real-valued write cases. Zero regressions.

ABORT breakdown after IBB-8a (~193):
- `bb_call: unsupported call shape` — non-write fn calls (user-proc dispatch), write(BB_CALL/proc result), write(BB_LIT_S in non-write fn) — main remaining cluster.
- `flat_drive_binop_tree: missing α or β child` — **relop in if-condition (~13). FULLY DIAGNOSED, see IBB-8b below.**
- `flat_drive_every: every-with-do-body` (~4).
- Two new SEGVs: `rung26_pow_pow_expr`, `rung37_augop_pow` — DT_R via `^`, fprintf(`%g`) inside slab. Pre-existing latent stack-alignment issue, exposed by IBB-7 progressing past the prior ABORT site. Both were ABORTing in baseline.

---

## Closed rungs

| Rung | Closed | Test | Commit |
|------|--------|------|--------|
| IBB-0 | Reset | — | — |
| IBB-1 | mode-2 hello | `write("hello")` | reset session |
| IBB-2 | Boot shape decision: zero SM, driver-level bypass | — | — |
| IBB-3 | mode-2 + mode-3 add | `write(1+2)` | `e612d519` |
| IBB-4 | mode-2 + mode-3 every-to | `every write(1 to 3)` | `fac53504` (bin-site reorder) |
| IBB-5 | mode-2 + mode-3 alt | `every write(1\|2\|3)` | `1a97c0a3` (counter-state dispatch) |
| IBB-6 | mode-2 + mode-3 full | `every write(5 > ((1 to 2)*(3 to 4)))` | `3aa200cd` (BINOP_GEN odometer) |
| IBB-7 | write(BB_VAR) + BB_ASSIGN flat-wire (AG-PURE deep-thread aware) | `x := 42; write(x)` byte-identical | `d1c55b0c` |
| IBB-1..32 (mode-2 only) | 22 programs verified zero-SM mode-2 | various | `936b8182` |

Mode-2 verified programs: write_str, arith, every_to/by, alt, conj, if, while, repeat, assign, augop, list-len, bang, idx, idx-gen, section, limit, user-proc, return, fail, table, cset, scan, scan-gens, recursion.

---

## Rungs

### IBB-8 (next) — DT_R fprintf SEGV + remaining mode-3 corpus

Two distinct fronts:

- [x] **DT_R fprintf SEGV** — CLOSED (IBB-8a, this commit). Root cause (gdb-verified): the flat BINARY slab is entered via the driver's `call fn(NULL,0)` at rsp%16==8, but `xa_flat_prologue` pushed nothing, so every internal `call *rax` to a runtime helper was made at rsp%16==8 → callees entered at rsp%16==0, one slot off the SysV ABI. Integer helpers tolerated it; `fprintf("%g")` faulted on its 16-byte-aligned `movaps %xmm0,-0x80(%rbp)`. Fix in `xa_flat.cpp`: `sub rsp,8` (48 83 EC 08) in the BINARY prologue before the esi-dispatch (so both α fall-through and β branch carry it; jne-β rel32 bin-site shifted +4), paired with `add rsp,8` (48 83 C4 08) before each `ret` in the BINARY epilogue (both succ and fail halves; fail-label bin-site tracks succ_half.size() automatically). Plus: `rt_pop_write_any_nl` DT_R branch now uses canonical `real_str` (matches mode-2 `9.0`/`1000000000.0`) instead of naive `%g`; and `bb_call.cpp` extended `arg_is_any` to BB_BINOP/BB_BINOP_GEN so DT_R-producing arithmetic routes through the type-aware any-write trailer (DT_I via %lld unchanged) rather than printing raw IEEE bits. Verified: `rung26_pow_pow_expr`, `rung37_augop_pow`, `rung26_pow_pow_assoc` PASS byte-identical; canonical-5 byte-identical + zero-SM; smokes 5/5/5/39; FACT 0; corpus 17→32, SEGV 2→0.
- [~] **relop in if-condition** — STRING relops DONE (IBB-8b, `0e926c16`); numeric/real relops still blocked on BB_LIT_F push (IBB-8c). **The IBB-8 diagnosis below proposed `flat_drive_if` walking a cond chain off the BB_IF node — that plan was WRONG: BB_IF has no field pointing back to the cond chain (PEERS RULE forbids adding one), and the cond chain is part of the ENCLOSING BB_SEQ, not owned by BB_IF.** Actual topology (verified by graph dump): `if (relop) then T else E` lowers to a branching CFG flattened into the BB_SEQ γ-chain — the relop (AG-pure, α=β=NULL, state=1) has γ==ω==BB_IF; BB_IF has γ=then-entry, ω=else-entry; with no else, BB_IF.ω points at the next statement (branches reconverge via fall-through, no join node). Mode-2's BB_SEQ oracle is itself a per-node CFG walk (γ AND ω both advance). **Implemented (not flat_drive_if):** (1) `flat_drive_seq` became a node-keyed CFG emitter — BFS from pBB->α following γ always + ω only for BB_IF, one arena label per node, emitted once, successors resolved via node→label map; non-IF nodes keep outer lbl_ω (matching baseline — resolving ω generally caused a SEGV regression by mis-wiring operand children, since tree-shape BB_BINOP / write-intexpr drivers walk their own children inline and the deep-thread dval==1.0 gate prevents double-walk only when ω stays outer). (2) `bb_binop.cpp` AG-pure relop/strrel arm: rt_acomp/rt_lcomp + unconditional jmp γ. (3) `bb_if.cpp` router: rt_pop_void; rt_last_ok; test; jz ω; jmp γ. **NEXT for numeric/real (IBB-8c):** add a BB_LIT_F push arm to `bb_lit_scalar.cpp` (currently a pass-through stub that never pushes the real → relop compares garbage → abort/SEGV on rung18_real_relop_*). Targets remaining: rung18_real_relop_{mixed,real_eq,real_gt,real_lt}, rung35_block_body_if_{block,else_block} (needs nested-block flattening).
- [ ] **every E do body** — 4 cases. `flat_drive_every` with `bb->β` set.
- [ ] **write(BB_CALL)** — user-proc result → vstack → write trailer. Requires BB_CALL-as-arg semantics + BB_RETURN flat-wire.
- [ ] **user-proc dispatch (non-write fn calls)** — large remaining cluster. Requires BB_CALL of arbitrary fn name + caller-side rt_call_proc helper.

### IBB-23 (open) — `suspend E`

Top-level `procedure g() suspend 1; suspend 2; end; every write(g())` prints nothing in both mode-2 and legacy. Pre-existing — needs `lower_icn_proc_gen`'s GeneratorState bridge wired through to outer `every` loop.

### IBB-8..34 — remaining (deferred mode-3 + mode-4)

Strings, to-by, conj, if, while, until/repeat, assign, augop, list, bang, idx, idx-gen, section, limit, user-call, suspend, return, fail, tables, sets, records, csets, scan, scan-prims, scan-gens, co-expressions, JCON ir_a_* sweep.

---

## Mode-3 abort map (canonical-5)

| Test | State |
|------|-------|
| hello.icn  | ✅ `6393c743` |
| add.icn    | ✅ `e612d519` |
| every_to.icn | ✅ `fac53504` |
| alt.icn    | ✅ `1a97c0a3` |
| full.icn   | ✅ `3aa200cd` |

---

## Per-rung gate

```bash
bash scripts/build_scrip.sh
./scrip --interp  /tmp/rung_NN.icn  > out_m2.txt
./scrip --run     /tmp/rung_NN.icn  > out_m3.txt
diff out_m2.txt out_m3.txt    # must be empty
./scrip --dump-sm /tmp/rung_NN.icn  # ; SM_sequence_t  count=0

# FACT gate
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/ \
  | grep -v _templates/ | grep -v emit_core | wc -l   # == 0

# Smokes (must hold)
bash scripts/test_smoke_icon.sh                # PASS=5
bash scripts/test_smoke_prolog.sh              # PASS=5
bash scripts/test_smoke_unified_broker.sh      # PASS>=35
```

---

## DO NOT

- Touch SNOBOL4 / Snocone / Rebus / Raku / Prolog lower or BB families.
- Use `SM_BB_INVOKE` for Icon programs going through `lower_icn_bb`.
- Write `DESCR_t foo(void *zeta, int entry)` C Byrd box functions. See `GOAL-ICON-BB-NATIVE.md`.
- Add fields to `BB_t`.
- Walk SM or BB at runtime in modes 3/4.

---

## Session Setup

```bash
cd /home/claude/one4all
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
bash scripts/test_smoke_icon.sh                # PASS=5
bash scripts/test_smoke_prolog.sh              # PASS=5
bash scripts/test_smoke_unified_broker.sh      # PASS>=35
```

---

## Watermark

Programs PASS, both modes, byte-identical.

| State | Programs PASS | Notes |
|-------|---------------|-------|
| IBB-6 ✅ | 5/5 canonical (m2 + m3) | `3aa200cd`. BB_BINOP_GEN odometer. |
| IBB-7 ✅ | 5/5 canonical; corpus 13→17 (+4) | `d1c55b0c`. BB_VAR + BB_ASSIGN flat-wire; AG-PURE deep-thread gates (ival==1 / dval==1.0). |
| IBB-8a ✅ | 5/5 canonical; corpus 17→32 (+15), SEGV 2→0 | `e9f09fdc`. xa_flat slab call-alignment (`sub/add rsp,8`) clears DT_R fprintf SEGV; DT_R write args (BB_BINOP/BB_BINOP_GEN) route through any-write trailer w/ canonical real_str. |
| IBB-8c ✅ (partial) | 5/5 canonical; corpus same-sweep 28→46 (+18), SEGV 0 | `91874d71` (Sonnet 4.6, 2026-05-29). THREE fixes: (1) `bb_lit_scalar.cpp` **BB_LIT_F vstack-push** (`0be6e78d`) — mirror BB_LIT_I arm, bit-cast `pBB->dval`→u64, call `rt_push_real_bits` (existing helper used by sm_push_pop_lits.cpp); 32-byte layout, sites {23,27,28}. Fixes rung18 real relops real_gt/real_lt/real_eq/mixed_relop (4/5; real_relop_goal still fails — float LHS in BB_BINOP_GEN gen-context). (2) `emit_bb.c` **BB_SEQ_EXPR flat-wire** (`37517836`) — `{}` block then/else lowers to BB_SEQ_EXPR (γ-chain off α, identical topology to BB_SEQ); `walk_bb_flat` had no case → hit `default:` → silent no-output. Routed through `flat_drive_seq`. Fixes rung35_block_body_if_block/if_else_block. (3) `emit_bb.c` **every-E-do-body ival=1** (`91874d71`) — `every 1 to 3 do write("x")` two-node gen↔body loop; walk gen γ→body_α ω→outer-γ β→gen_β; walk body γ/ω→gen_β (re-pump). Body result discarded, runs once per generated value. Gates: FACT 0, smoke icon/prolog 5/5, broker 39/14, zero-SM holds, no regressions. **NEXT (IBB-8c cont):** every-do ival=2 (gen-bearing chain) and ival=3 (BODY-MEDIATED BB_SEQ_EXPR block + phase machine on bb->state) — corpus rung35 `every x:=1 to 3 do {block}` cases; then while-do-body (rung35_block_body_while_do_block, empty m3, needs while driver + augop body); then real_relop_goal; then write(BB_CALL), user-proc dispatch. |
| IBB-8b ✅ (partial) | 5/5 canonical; corpus same-sweep 22→28 (+6), SEGV 0 | `0e926c16` (Opus 4.8, 2026-05-29). STRING relops in if-condition. Three pieces: (1) `bb_binop.cpp` AG-pure relop/strrel apply arm — `rt_acomp`(numeric)/`rt_lcomp`(string) + unconditional `jmp γ` (both ports of an AG-pure relop reach the BB_IF router, per mode-2 oracle); (2) NEW `bb_if.cpp` router — `rt_pop_void; rt_last_ok; test eax,eax; jz ω(else); jmp γ(then)`; (3) `flat_drive_seq` rewritten from γ-only linear walker into a **node-keyed CFG emitter** (BFS follows γ always, ω ONLY for BB_IF so operand children aren't double-emitted; non-IF nodes keep outer lbl_ω as baseline; one stable arena label per node). AG-pure BB_BINOP routes to FILL; added `case BB_IF`. BB_SEQ is Icon-exclusive → no cross-family impact. Newly passing: rung12_strrelop_size_{slt,sge,sne}, rung37_strrelop_hello, rung07_control_seq, canonical if_expr crosscheck. Gates: FACT 0, smoke icon/prolog 5/5, broker 39/14, zero-SM holds, no regressions. **NOTE:** the "32" in the IBB-8a row used a different corpus filter than this same-sweep 22→28 (+6) measurement — reconcile gate methodology before trusting absolute counts; the +6 delta is apples-to-apples. **NEXT (IBB-8c):** real relops need **BB_LIT_F vstack-push** — `bb_lit_scalar.cpp` BB_LIT_F path is a pass-through stub that never pushes the real (mirror the BB_LIT_I arm with a DT_R DESCR_t push); rung18_real_relop_* blocked on this. Then block-body if (rung35_block_body_if_*) needs nested-block flattening. Then every-E-do-body (~4), write(BB_CALL), user-proc dispatch. |
