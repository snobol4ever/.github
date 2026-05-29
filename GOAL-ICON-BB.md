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

## Current state (2026-05-29, IBB-9-1 every-x-assign-do landed, one4all `e8f66866`)

| Mode | Path | Canonical-5 | Full corpus (m2-OK filter) |
|------|------|-------------|---------------------------------|
| 2 (`--interp`) | `bb_exec_once` C tree-walker | **5 / 5** | — |
| 3 (`--run`) | `bb_build_flat` → seal RX → call slab | **5 / 5** | **same-sweep 213→216 PASS (+3), SEGV 0** |
| 4 (`--compile`) | deferred per Lon directive | hello.icn ✅ (`f387a7b9`) | n/a |

**GATE METHODOLOGY (canonical, use this exact script every session):** same-sweep over `/home/claude/corpus/programs/icon/*.icn`: for each, run `--interp` (skip if rc≠0 — m2-OK filter), then `--run`; PASS iff `m3 rc==0 && m2==m3` (byte-identical). Count PASS / SEGV(rc=139) / ABORT(rc≥134) / FAIL(other). Baseline `30e7c0a1`=213 PASS; `e8f66866`=216. The earlier "22→28"/"28→46" rows used a NARROWER filter (subset dirs) — the 213/216 absolute counts are the whole-tree measure; trust deltas within one methodology only.

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
- [~] **every E do body** — PARTIAL. ival=1 simple-gen (`every 1 to 3 do B`) DONE (IBB-8c). `every x := 1 to N do B` static-TO-assign DONE (IBB-9-1, `e8f66866`). Remaining ival=2/3 shapes → IBB-9.
- [ ] **write(BB_CALL)** — user-proc result → vstack → write trailer. Requires BB_CALL-as-arg semantics + BB_RETURN flat-wire. → IBB-9-7.
- [ ] **user-proc dispatch (non-write fn calls)** — large remaining cluster. Requires BB_CALL of arbitrary fn name + caller-side rt_call_proc helper. → IBB-9-6.

### IBB-9 (CURRENT) — JCON-grounded control-flow completion

**Source-of-truth:** `jcon/tran/irgen.icn` (the Icon→IR translator SCRIP's lowering mirrors). Read the cited
`ir_a_*` procedure BEFORE implementing each step; the chunk-wiring in JCON is the canonical CFG and SCRIP's
BB port-graph (α=start, β=resume, γ=success, ω=failure) is a direct transcription. The recurring JCON pattern:
each construct lays `ir_chunk`s for `ir.start / ir.resume / sub.success / sub.failure`, and the *only* structural
difference between loop forms is **where body-success/failure routes** — to `expr.resume` (every: pull next
generator value) vs `expr.start` (while/until: re-evaluate condition fresh). This single distinction (JCON
`ir_a_Every:327-330` vs `ir_a_While:1024-1031`) is the spine of every step below.

**Architectural prize from JCON (the deep idea):** for UNBOUNDED (resumable) control structures — if/case/alt
used in expression position — JCON does NOT hardcode the resume target. It emits `ir_MoveLabel(t, chosen.resume)`
on the taken branch and `ir_IndirectGoto(t)` at `ir.resume` (`ir_a_If:596-605`, `ir_a_Alt:183-188`). The taken
arm records its own resume label into a temp-location `t`; re-entry dispatches through `t`. This is a
**computed-goto continuation** — the same mechanism WAM-CP uses for Prolog. SCRIP currently only handles BOUNDED
(statement-context) Icon, where branches reconverge by fall-through and no `t` is needed. Expression-context
generators (`x := if a then (1 to 3) else (4 to 6); every write(x)`) will REQUIRE this. Captured here so it is
not rediscovered; deferred until a corpus program needs it (IBB-9-8).

- [x] **IBB-9-1 — `every x := 1 to N do B` (static-TO assign).** `e8f66866`. JCON `ir_a_Every` treats this as
  `every (x := GEN) do B`: the assignment is the `p.expr`, and because `:=` is in `ir_a_Binop`'s `funcs` set,
  `ir_binary:438-444` routes `expr.resume → right.resume` — the assign is transparent to resume, forwarding it
  into the generator. SCRIP transcription: interpose a BB_ASSIGN store node (ival=1, β=gen for the mode-2 null
  guard) on the ival=1 every topology; `flat_drive_every` emits gen→store→body→gen_β. Corpus 213→216.
- [ ] **IBB-9-2 — `while C do B`: fix cond-result routing (driver exists, JCON-faithful, but cond does not gate).**
  `flat_drive_while` (emit_bb.c:1029, IBB-9-2 partial) already transcribes JCON `ir_a_While` (irgen.icn:1008-1032)
  correctly: `ir.start→expr.start`; `expr.success→body.start`; `expr.failure→ir.failure`; **`body.success→expr.START`**
  and **`body.failure→expr.START`** (NOT resume — the while/every distinction). BUT the relop condition's RESULT is
  not gating the loop. **Probe-confirmed bug (2026-05-29, Opus 4.8):** `i:=5; while i<=3 do write(i); write(99)` prints
  `5 5 5…` in m3 (infinite) vs `99` in m2. The cond walk routes the relop's γ straight to body unconditionally.
  **ROOT CAUSE:** same shape as IBB-8b BB_IF — a relop-in-condition needs a ROUTER that tests the comparison result
  and branches body (true) vs exit (false). **CONFIRMED CRITICAL DETAIL (do not repeat my dead-end):** the while-cond
  relop is a **TREE-SHAPE BB_BINOP** (α/β operand children NON-NULL, `ival` = the relop opcode, observed `ival=6`),
  NOT the AG-pure (α==β==NULL) shape that BB_IF conds use. So detecting the relop via `α==NULL && β==NULL` FAILS —
  must detect by the BB_BINOP **opcode** (`ival` ∈ relop-op set: `<,<=,=,~=,>=,>` numeric + `<<,<<=,==,…` string).
  Must FIRST verify whether `flat_drive_binop_tree` (emit_bb.c:805) sets LAST_OK + does unconditional jmp γ (→ router
  needed, reuse `bb_if.cpp`) or already routes on result via γ/ω (→ no router, just wire cond.ω=cond_false). Inspect
  the relop apply arm in `bb_binop.cpp` tree-shape path before coding. **REGRESSION WARNING (cost me 26 programs this
  session):** the router must fire ONLY for relop conds. A NON-relop cond — assignment (`while line := read() do …`),
  generator, or plain call — signals truth via its OWN γ (produced a value) / ω (none) and does NOT set LAST_OK;
  inserting a LAST_OK router there sends control on garbage. Gate the router strictly on relop-opcode detection;
  `while line := read()` (BB_ASSIGN cond), `while c := a[i]` etc. MUST keep the direct γ/ω routing. Verify against the
  full corpus sweep (`/tmp/sweep.sh` shape: m2-OK filter, m2==m3 && m3 rc=0) — baseline at `e8f66866` is **216 PASS**;
  any drop below 216 means the router is over-firing. Then the augop (`+:=`) body — JCON `ir_augmented_assignment:417-428`
  (`tmp := lv op rv; target := lv := tmp`); `rung35_block_body_while_do_block` already has `i +:= 1` and works once the
  cond gates (verified: with an unconditional router it goes 1 2 3, but that router regresses the 26 read-loop programs).
  Target: `rung35_block_body_while_do_block` (m3 infinite today → `1 2 3`, +1) WITHOUT dropping the 216.
- [ ] **IBB-9-3 — `until C do B`.** Shares `flat_drive_while` (BB_UNTIL flips cond_true/cond_false). Inherits the SAME
  cond-routing bug as IBB-9-2 — fix once in the shared driver and both forms work. **JCON `ir_a_Until` (irgen.icn:981-1005)**:
  `expr.success→ir.failure` (cond true ⇒ until ENDS), `expr.failure→body.start` (cond false ⇒ run body). Body
  success/failure → `expr.start`. The inverse-sense twin of while. Most corpus `until` tests
  (`rung09_loops_until*`) ALSO need user-proc dispatch (they wrap the loop in a `procedure countdown(n)`) — so they
  stay blocked on IBB-9-6 even after the cond-router lands; pick a proc-free `until` repro to gate this step.
- [ ] **IBB-9-4 — `every E do B` ival=2 (gen-bearing chain, simple body).** `every v := !t do B`, `every (i to j) do B`
  where the gen is a streaming generator (BB_ALT/BB_LIST_BANG/BB_BINOP_GEN/BB_ITERATE). JCON: identical `ir_a_Every`
  wiring — there is no ival distinction in JCON, the generator's own resume chain handles re-pumping. SCRIP's ival=2
  branch exists in lower; the gap is the mode-3 `flat_drive_every` ival=2 emit (gen-bearing β-chain). Body must be a
  non-generator (lic_body_bears_gen guard already in lower).
- [ ] **IBB-9-5 — `every E do { block }` ival=3 (BODY-MEDIATED).** `every x := 1 to 3 do { y := x*2; write(y) }`.
  The hardest: bb sits ON the back-edge (gen.γ=bb, gen.ω=bb, body.γ=bb, body.ω=bb) with a phase machine on bb->state
  (1=just-dispatched-gen, 2=just-dispatched-body) and per-pass BB_SEQ_EXPR state reset. Mode-2 ival=3 executor
  exists (bb_exec.c:1710); mode-3 flat_drive_every ival=3 is the gap. NOTE: corpus `rung35_block_body_every_do_block`
  currently exposes a **mode-2 bug** (`every x:=1 to 3 do {y:=x*2;write(y)}` prints `2 2 2` in m2, correct `2 4 6`
  in m3) — fix mode-2 ival=3 x-rebind alongside, or the byte-identical gate will never pass. Honor break/next/return
  via FRAME flags (JCON `ir_a_Break:1107`/`ir_a_Next:1082` route to `curloop.ir.x.nextlabel`).
- [ ] **IBB-9-6 — user-proc dispatch (non-write fn calls).** Transcribe **JCON `ir_a_Call` (irgen.icn:360-403)**: args
  lowered via `ir_value`, chained `L=[fn]|||args` with `L[i].success→L[i+1].start`, `L[i].failure→L[i-1].resume`
  (generator args re-pump through the chain), then `ir_Call(closure, fn, args, resume); Move(target,closure)`. SCRIP:
  BB_CALL of an arbitrary proc name needs a caller-side `rt_call_proc` runtime helper (push args, invoke proc BB
  graph, leave result on vstack) + BB_RETURN flat-wire (JCON `ir_a_Return:867-903`: `Succeed(t)` on success path).
  Largest remaining ABORT cluster. Start with a 0-arg and 1-arg user proc returning a value.
- [ ] **IBB-9-7 — `write(BB_CALL)` / `write(proc-result)`.** Depends on IBB-9-6. Once a user proc leaves its result on
  the vstack, route it through the existing `rt_pop_write_any_nl` trailer (the BB_CALL-as-arg path bb_call.cpp already
  has `arg_is_any`). Also `write(f(x))` where f is a generator proc → every-resumes through the call chain.
- [ ] **IBB-9-8 — DEFERRED: unbounded/expression-context resume (computed-goto continuation).** Only when a corpus
  program assigns a generator-bearing if/case/alt to a variable and resumes it (`x := if … then (1 to 3); every write(x)`).
  Implement JCON's `ir_MoveLabel(t, arm.resume)` + `ir_IndirectGoto(t)` (`ir_a_If:596`, `ir_a_Alt:183`). This is the
  `bounded` flag SCRIP currently ignores. Big; do not start until forced.

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
| IBB-9-1 ✅ | 5/5 canonical; corpus same-sweep 213→216 (+3), SEGV 0 | `e8f66866` (Opus 4.8, 2026-05-29). `every x := 1 to N do body` (static-TO assign). JCON-grounded: `ir_a_Every` treats it as `every (x:=GEN) do B`; `:=` ∈ `ir_binary` funcs → `expr.resume→right.resume` (assign transparent to resume). SCRIP: `lower_icn_new_Every_ag` intercepts TT_EVERY whose c[0] is TT_ASSIGN over a static literal TT_TO (BB_TO α==β==NULL) + plain TT_VAR lhs; interposes a BB_ASSIGN store node (ival=1, β=gen for mode-2 null guard) on the ival=1 topology (gen.γ=store, store.γ=body, body.γ=gen, body.ω=gen, gen.ω=bb). `flat_drive_every` ival=1 detects the store (β is BB_ASSIGN ival=1 w/ γ) and emits gen→store→body→gen_β; store's β routed to a dead store_ω stub (NOT gen_β — would self-jump gen_β into an infinite loop). TT_TO_BY excluded (keeps operand boxes). Mode-2 reads via ag_ring_peek(0); mode-3 pops vstack via rt_pop_nv_set. Newly passing: every_do_hello, block_body_nested_block, range_to. Gates: FACT 0, smoke icon/prolog 5/5, broker 42/11, zero-SM holds, no regressions. **NEXT (IBB-9-2):** `while C do B` — first verify the `do {block}` parser gap (`expected ; got while`), then transcribe JCON `ir_a_While` (body.success/failure → expr.START, the every-vs-while distinction). Then until (IBB-9-3), every ival=2/3 (IBB-9-4/5), user-proc dispatch (IBB-9-6, JCON `ir_a_Call`), write(BB_CALL) (IBB-9-7). |
| IBB-8c ✅ (partial) | 5/5 canonical; corpus same-sweep 28→46 (+18), SEGV 0 | `91874d71` (Sonnet 4.6, 2026-05-29). THREE fixes: (1) `bb_lit_scalar.cpp` **BB_LIT_F vstack-push** (`0be6e78d`) — mirror BB_LIT_I arm, bit-cast `pBB->dval`→u64, call `rt_push_real_bits` (existing helper used by sm_push_pop_lits.cpp); 32-byte layout, sites {23,27,28}. Fixes rung18 real relops real_gt/real_lt/real_eq/mixed_relop (4/5; real_relop_goal still fails — float LHS in BB_BINOP_GEN gen-context). (2) `emit_bb.c` **BB_SEQ_EXPR flat-wire** (`37517836`) — `{}` block then/else lowers to BB_SEQ_EXPR (γ-chain off α, identical topology to BB_SEQ); `walk_bb_flat` had no case → hit `default:` → silent no-output. Routed through `flat_drive_seq`. Fixes rung35_block_body_if_block/if_else_block. (3) `emit_bb.c` **every-E-do-body ival=1** (`91874d71`) — `every 1 to 3 do write("x")` two-node gen↔body loop; walk gen γ→body_α ω→outer-γ β→gen_β; walk body γ/ω→gen_β (re-pump). Body result discarded, runs once per generated value. Gates: FACT 0, smoke icon/prolog 5/5, broker 39/14, zero-SM holds, no regressions. **NEXT (IBB-8c cont):** every-do ival=2 (gen-bearing chain) and ival=3 (BODY-MEDIATED BB_SEQ_EXPR block + phase machine on bb->state) — corpus rung35 `every x:=1 to 3 do {block}` cases; then while-do-body (rung35_block_body_while_do_block, empty m3, needs while driver + augop body); then real_relop_goal; then write(BB_CALL), user-proc dispatch. |
| IBB-8b ✅ (partial) | 5/5 canonical; corpus same-sweep 22→28 (+6), SEGV 0 | `0e926c16` (Opus 4.8, 2026-05-29). STRING relops in if-condition. Three pieces: (1) `bb_binop.cpp` AG-pure relop/strrel apply arm — `rt_acomp`(numeric)/`rt_lcomp`(string) + unconditional `jmp γ` (both ports of an AG-pure relop reach the BB_IF router, per mode-2 oracle); (2) NEW `bb_if.cpp` router — `rt_pop_void; rt_last_ok; test eax,eax; jz ω(else); jmp γ(then)`; (3) `flat_drive_seq` rewritten from γ-only linear walker into a **node-keyed CFG emitter** (BFS follows γ always, ω ONLY for BB_IF so operand children aren't double-emitted; non-IF nodes keep outer lbl_ω as baseline; one stable arena label per node). AG-pure BB_BINOP routes to FILL; added `case BB_IF`. BB_SEQ is Icon-exclusive → no cross-family impact. Newly passing: rung12_strrelop_size_{slt,sge,sne}, rung37_strrelop_hello, rung07_control_seq, canonical if_expr crosscheck. Gates: FACT 0, smoke icon/prolog 5/5, broker 39/14, zero-SM holds, no regressions. **NOTE:** the "32" in the IBB-8a row used a different corpus filter than this same-sweep 22→28 (+6) measurement — reconcile gate methodology before trusting absolute counts; the +6 delta is apples-to-apples. **NEXT (IBB-8c):** real relops need **BB_LIT_F vstack-push** — `bb_lit_scalar.cpp` BB_LIT_F path is a pass-through stub that never pushes the real (mirror the BB_LIT_I arm with a DT_R DESCR_t push); rung18_real_relop_* blocked on this. Then block-body if (rung35_block_body_if_*) needs nested-block flattening. Then every-E-do-body (~4), write(BB_CALL), user-proc dispatch. |
