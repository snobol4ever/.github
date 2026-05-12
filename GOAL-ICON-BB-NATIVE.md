# GOAL-ICON-BB-NATIVE.md — Icon via native Byrd Box templates

**Repo:** one4all + .github
**Sister docs:** `GOAL-ICON-BB-COMPLETE.md` (superseded), `GOAL-LANG-ICON.md`,
                 `GOAL-MODE4-EMIT.md`, `ARCH-x86.md`, `ARCH-ICON.md`
**Carved:** 2026-05-12

⛔ **REQUIRED READING before any code:**
1. `ARCH-x86.md` — full file. Boxes are x86 blobs. CODE is shared machine code.
   DATA is per-invocation heap. α/β/γ/ω are goto labels inside x86 code.
   Two emission forms: FLAT (wired, jmp-threaded) and BROKERED (legacy C ABI).
2. `ARCH-SCRIP.md` — full file. Mode 1/2/3/4 definitions.
3. `GOAL-MODE4-EMIT.md` §"THE LAW OF TEMPLATE FUNCTIONS" — one C template
   function per SM opcode and per BB box kind. t_* helpers only. No other path.

---

## The insight that killed GOAL-ICON-BB-COMPLETE

GOAL-ICON-BB-COMPLETE was encoding the four-port BB protocol as SM bytecode:
SM_JUMP / SM_RESUME / SM_STORE_GLOCAL / SM_SUSPEND / SM_RETURN.
This is wrong for two reasons:

1. **BB boxes are x86 assembly blobs**, not SM instructions. The four ports
   (alpha=start, beta=resume, gamma=succeed, omega=fail) are goto targets inside
   machine code, exactly as shown in .github/test_icon.c. The SM layer is the
   CARRIER that calls into the BB engine — not the executor of Icon semantics.

2. **The right architecture** (per ARCH-SCRIP.md RS-20, 2026-05-03):
   "Icon and Prolog programs may lower thinly into SM — often a single
   SM_BB_PUMP / SM_BB_ONCE instruction that hands the whole program to the
   BB engine."
   SM is thin. BB is the executor. Icon semantics live in BB boxes.

---

## What currently exists and works

**Statement level (SM_BB_PUMP): already correct.**
- lower.c emits SM_PUSH_EXPR <tree_t*> + SM_BB_PUMP for each Icon statement.
- sm_interp.c pops the tree_t*, calls coro_eval() -> bb_node_t, then
  bb_broker(node, BB_PUMP, pump_print, NULL).
- sm_codegen.c mirrors this exactly in h_bb_pump.
- This path is CORRECT AND COMPLETE. Do not touch it.

**coro_eval() / coro_runtime.c**: the existing C-function dispatched boxes
(coro_bb_every, coro_bb_limit, coro_bb_bang_binary, coro_bb_to_by,
coro_bb_seq_expr, icn_bb_assign_gen, icn_bb_identical_gen, etc.) are the
EMIT_BINARY_BROKERED (legacy) form — each is a C function fn(zeta, port).
They work correctly today as the --ir-run and honest --sm-run engine.
They are NOT the architectural target but ARE the semantic reference.

**The architectural target** is EMIT_BINARY_WIRED (flat BB):
One template C function per Icon box kind (e.g. emit_bb_icn_to,
emit_bb_icn_iterate) that emits raw x86-64 bytes via t_* helpers,
producing a jmp-threaded blob with no C-call overhead per box.
This is what bb_xchr.c, bb_xor.c, bb_xstar.c etc. do for SNOBOL4.
Icon needs the same treatment.

---

## Done when

1. Every Icon generator construct has a template C function emit_bb_icn_*
   in src/runtime/x86/templates/ that emits correct flat-BB x86.
2. lower.c wires each Icon construct to its emit_bb_icn_* template rather
   than emitting SM coroutine opcodes or SM_BB_PUMP_AST fallthrough.
3. SCRIP_NO_AST_WALK=1 ./scrip --sm-run == ./scrip --ir-run for every
   program in the --ir-run PASS set (the honest gate).
4. --ir-emit byte-identical to pre-goal baseline for every corpus program.
5. SM_BB_PUMP_AST, SM_BB_PUMP_SM, SM_RESUME, SM_STORE_GLOCAL,
   SM_SUSPEND_VALUE, SM_RETURN never appear in the emitted SM_Program
   for any Icon construct. These were SM-coroutine workarounds; now gone.
6. Smokes unchanged throughout every rung.

---

## Architecture of an Icon BB box

From test_icon.c — three-column form, every construct has four ports:

  /* alpha port — fresh entry */
  to_start:  lo = eval(lo_expr);  cur = lo;   goto to_check;
  /* beta port — resume/backtrack */
  to_resume: cur++;               goto to_check;
  to_check:  if (cur > hi)        goto to_fail;
             value = cur;         goto to_succeed; /* gamma port */
  to_fail:   /* propagate omega */

In the template C function this becomes t_* calls. The runtime helpers
(icn_to_alpha, icn_to_beta) are small C functions that read/write the
DATA block (zeta struct). The template wires control flow; the runtime
helper does the arithmetic. t_bb_port_call emits the call + branch.

---

## Box taxonomy for Icon

Generator constructs need flat-BB templates. Scalar constructs (succeed/fail
only: relops, arith, field get) are already handled by coro_eval ->
coro_oneshot and work correctly; they do not need new templates in this goal.

  Construct        TT_ kind        Template                Generator?
  -----------      ---------       --------                ----------
  Integer range    TT_TO/TO_BY     emit_bb_icn_to          yes
  Iterate !E       TT_ITERATE      emit_bb_icn_iterate     yes
  Alternate A|B    TT_ALTERNATE    emit_bb_icn_alt         yes
  Every            TT_EVERY        emit_bb_icn_every       yes
  Limitation E\N   TT_LIMIT        emit_bb_icn_limit       yes
  Bang binary E1!E2 TT_BANG_BINARY emit_bb_icn_bang        yes
  List concat |||  TT_LCONCAT      emit_bb_icn_lconcat     yes
  Seq expr (E1;E2) TT_SEQ_EXPR     emit_bb_icn_seq         yes

JCON reference for each: jcon-master/tran/irgen.icn ir_a_* procedures.
Semantic reference: coro_runtime.c coro_bb_* functions (BROKERED form).

---

## File layout

  src/runtime/x86/templates/
    bb_icn_to.c         emit_bb_icn_to        TT_TO / TT_TO_BY
    bb_icn_iterate.c    emit_bb_icn_iterate   TT_ITERATE (!E)
    bb_icn_alt.c        emit_bb_icn_alt       TT_ALTERNATE (A|B)
    bb_icn_every.c      emit_bb_icn_every     TT_EVERY
    bb_icn_limit.c      emit_bb_icn_limit     TT_LIMIT (E\N)
    bb_icn_bang.c       emit_bb_icn_bang      TT_BANG_BINARY (E1!E2)
    bb_icn_lconcat.c    emit_bb_icn_lconcat   TT_LCONCAT (|||)
    bb_icn_seq.c        emit_bb_icn_seq       TT_SEQ_EXPR ((E1;E2))

  src/runtime/interp/
    icn_box_rt.c        runtime alpha/beta port helpers called by templates
    icn_box_rt.h        declarations

  src/runtime/x86/lower.c
    lower_to, lower_to_by   -> emit_bb_icn_to    (was SM coroutine)
    lower_iterate           -> emit_bb_icn_iterate (was SM coroutine)
    lower_alternate         -> emit_bb_icn_alt    (was lower_bb_pump_ast)
    lower_every             -> emit_bb_icn_every  (was SM_BB_PUMP_EVERY)
    lower_limit             -> emit_bb_icn_limit  (was emit_push_expr+SM_BB_PUMP)
    lower_bang_binary       -> emit_bb_icn_bang   (was SM_BB_PUMP_AST)
    lower_lconcat           -> emit_bb_icn_lconcat (was SM_BB_PUMP_AST)
    lower_seq_expr          -> emit_bb_icn_seq    (was scalar only)

---

## Session Setup

  cd /home/claude/one4all
  bash scripts/install_system_packages.sh
  bash scripts/build_scrip.sh
  bash scripts/build_spitbol_oracle.sh

Baseline gates (all green before every rung):
  bash scripts/test_smoke_icon.sh                 # PASS=5  never regress
  bash scripts/test_smoke_unified_broker.sh       # PASS=49 never regress
  bash scripts/test_icon_ir_all_rungs.sh          # 185/48/30 byte-identical
  bash scripts/test_icon_sm_no_ast_walk.sh        # honest dial rises each rung

---

## Rungs

### IB-0 — baseline
- [ ] Run session setup. Confirm smoke 5/5, broker 49/49, ir-all 185/48/30.
- [ ] Record honest baseline N0 (SCRIP_NO_AST_WALK=1 pass count).
- [ ] Create src/runtime/interp/icn_box_rt.h and icn_box_rt.c — empty stubs,
      include guards, placeholder comment. Wire into Makefile.
- [ ] Build clean. Smokes unchanged. Commit.

### IB-1 — icn_to template (integer range generator)
- [ ] Study coro_bb_to_by in coro_runtime.c for alpha/beta semantics.
      Study test_icon.c to1_* labels for the three-column form.
- [ ] Implement runtime helpers in icn_box_rt.c:
      icn_to_alpha(zeta, lo, hi, step) — init state, return first value or FAIL.
      icn_to_beta(zeta) — advance cur, return next value or FAIL.
- [ ] Write src/runtime/x86/templates/bb_icn_to.c:
      emit_bb_icn_to(e, lbl_succ, lbl_fail, lbl_beta, zeta_ptr).
      alpha: t_bb_port_call(zeta_ptr, "icn_to_alpha", ..., lbl_succ, lbl_fail).
      beta:  t_label_define(lbl_beta) + t_bb_port_call("icn_to_beta",...).
- [ ] Wire lower_to and lower_to_by in lower.c to call emit_bb_icn_to.
      Delete SM coroutine emission for TT_TO / TT_TO_BY.
- [ ] Anchor: write(1 to 3) in scalar context.
      Gate: honest PASS, N1 > N0. dump-sm shows no SM_RESUME/GLOCAL/SUSPEND.
      Smokes unchanged. Commit.

### IB-2 — icn_iterate template (!E)
- [ ] Study coro_runtime.c for iterate semantics. State: {subject DESCR_t, index}.
      alpha: init index=0, get element[0] or FAIL.
      beta: index++, get element[index] or FAIL.
- [ ] Runtime helpers icn_iterate_alpha, icn_iterate_beta in icn_box_rt.c.
- [ ] Template bb_icn_iterate.c. Wire lower_iterate. Delete SM coroutine body.
- [ ] Anchor: rung15_iterate_string.icn. Gate: honest PASS, N up. Commit.

### IB-3 — icn_alt template (A|B alternate)
- [ ] Study coro_bb_alternate / icn_alternate_state_t in coro_runtime.c.
      alpha: try left. On left-omega try right. On right-omega -> own omega.
      beta: resume whichever branch is live.
- [ ] Runtime helpers icn_alt_alpha, icn_alt_beta.
- [ ] Template bb_icn_alt.c. Wire lower_alternate non-hoisted path.
      Delete lower_bb_pump_ast call for TT_ALTERNATE.
- [ ] Gate: honest PASS, N up. Smokes OK. Commit.

### IB-4 — icn_every template (every E [do body])
- [ ] Study coro_bb_every. Pump generator alpha/beta; run body each tick.
      Body runs through bb_exec_stmt (not re-lowered).
- [ ] Runtime helpers icn_every_alpha, icn_every_beta.
- [ ] Template bb_icn_every.c. Wire lower_every. Delete SM_BB_PUMP_EVERY Icon path.
- [ ] Anchor: every write(1 to 3). Gate: honest PASS, N up. Smokes OK. Commit.

### IB-5 — icn_limit template (E\N)
- [ ] Study coro_bb_limit. Wrap inner generator; cap at N values.
      alpha: reset count, pump inner alpha. beta: if count < N pump inner beta else omega.
- [ ] Runtime helpers icn_limit_alpha, icn_limit_beta.
- [ ] Template bb_icn_limit.c. Wire lower_limit.
      Delete emit_push_expr + SM_BB_PUMP for Icon TT_LIMIT.
- [ ] Anchor: rung14 limit program. Gate: honest PASS, N up. Smokes OK. Commit.

### IB-6 — icn_bang template (E1!E2 bang binary)
- [ ] Study coro_bb_bang_binary. Pump E2 generator; call E1(arg) each tick.
      If E1 fails on arg, skip to next E2 (goal-directed).
- [ ] Runtime helpers icn_bang_alpha, icn_bang_beta.
- [ ] Template bb_icn_bang.c. Wire lower_bang_binary. Delete SM_BB_PUMP_AST call.
- [ ] Gate: honest PASS, N up. Smokes OK. Commit.

### IB-7 — icn_lconcat + icn_seq templates
- [ ] icn_lconcat: generator over list concat (study lower_lconcat, coro_bb_cat).
- [ ] icn_seq: seq_expr generative (study coro_bb_seq_expr).
- [ ] Templates bb_icn_lconcat.c, bb_icn_seq.c. Wire both in lower.c.
      Delete SM_BB_PUMP_AST calls for TT_LCONCAT and generative TT_SEQ_EXPR.
- [ ] Gate: honest PASS, N up. Smokes OK. Commit.

### IB-8 — delete SM_BB_PUMP_AST from Icon path entirely
- [ ] grep lower.c for SM_BB_PUMP_AST in LANG_ICN-reachable paths. Must be zero.
- [ ] Replace any remaining lower_bb_pump_ast for Icon with:
      abort("BUG: Icon AST pump reached — missing template for kind %d", t->t)
- [ ] Full corpus sweep: zero AST-pump fires under SCRIP_NO_AST_WALK=1.
- [ ] Gate: honest PASS count == ir-run PASS count (explain any gap). Commit.

### IB-9 — cleanup
- [ ] Delete unused SM coroutine helpers from lower.c (SM_RESUME, SM_STORE_GLOCAL,
      SM_SUSPEND_VALUE, SM_RETURN sites that were Icon-only).
- [ ] is_suspendable returns false for all migrated TT_ kinds.
- [ ] coro_eval not reachable under SCRIP_NO_AST_WALK=1 for any Icon program.
- [ ] Build clean. Full gate sweep. Commit.

---

## Invariants — never break

1. test_smoke_icon.sh PASS=5 at every rung.
2. test_smoke_unified_broker.sh PASS=49 at every rung.
3. --ir-emit byte-identical to pre-goal baseline at every rung.
4. SM_BB_PUMP_AST count in Icon-reachable lower.c paths never increases.
5. Each rung commits at most two constructs. One is better.
6. Each rung's anchor must flip at least one program honest.
7. Template files: t_* helpers only. No e-> vtable calls. No raw byte emission.
   Per GOAL-MODE4-EMIT "THE LAW OF TEMPLATE FUNCTIONS".

---

## What NOT to do

- DO NOT implement Icon constructs as SM coroutines (SM_JUMP/SM_RESUME/
  SM_STORE_GLOCAL/SM_SUSPEND/SM_RETURN). That encodes BB protocol in SM.
  It is wrong. It is what GOAL-ICON-BB-COMPLETE did. One month lost.
- DO NOT write new C functions called at runtime as the box form.
  coro_bb_* in coro_runtime.c are BROKERED (legacy). Target is WIRED flat.
  Use coro_bb_* only as semantic reference, not as implementation target.
- DO NOT invent new SM opcodes (SM_BB_EXEC, SM_GEN_SUSPEND, etc.).
  SM_BB_PUMP at statement level is correct and sufficient.
  Sub-expression generators are flat BB blobs, not new SM opcodes.
- DO NOT call through e-> in template bodies. t_* only.

---

## Watermark

  Last session:      2026-05-12 (carved + architecture fully clarified)
  one4all HEAD:      (set at IB-0)
  Honest PASS N0:    (set at IB-0)
  Current rung:      IB-0
