# GOAL-ICON-BB-NATIVE.md — Icon via native Byrd Box templates

## ⛔ FACT RULES POINTER (Lon 2026-06-06)
ONE MEDIUM, INVISIBLE + TEMPLATE-ONLY EMISSION (corrected): canonical text in GOAL-SNOBOL4-BB.md / GOAL-ICON-BB.md / GOAL-PROLOG-BB.md / GOAL-RAKU-BB.md and RULES.md. ZERO BINARY emission anywhere in a `bb_*.cpp` (top level or helpers); `x86()` internals are the ONLY emitter of BINARY and TEXT.

**STATUS (2026-06-04, Lon prune directive): SUPERSEDED-ERA GOAL.** The IB-* rung ladder and its watermark were
pre-GROUND-ZERO-3 SM/value-stack work (last session 2026-05-12) and are PRUNED. **The live Icon ladder is
`GOAL-ICON-BB.md`.** This file is retained for its doctrine sections only (architecture distinction, box
structure/taxonomy, invariants, the permanent what-NOT-to-do record).

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ NO AST WALKING IN MODES 2/3/4 — see RULES.md § "NO AST WALKING IN MODES 2, 3, OR 4"         ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  Sess 2026-05-15g removed all tree_t* dereferences from sm_interp.c (mode 2) and                ║
║  sm_jit_interp.c (mode 3). Stubs print [NO-AST] <opcode> on stderr.                              ║
║                                                                                                  ║
║  If a gate breaks with [NO-AST] FOO — write fresh SM/BB lowering for FOO.                       ║
║  Do NOT restore the AST-walking call.  Do NOT route through proc_table_call or any              ║
║  other back-door that hands a tree_t* to mode-2/3/4 code.                                       ║
║                                                                                                  ║
║  Mode 1 (`--interp` standalone AST interp) is unchanged and remains the reference path.        ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝


╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** SCRIP + .github
**Sister docs:** `GOAL-ICON-BB-COMPLETE.md` (superseded), `GOAL-MODE4-EMIT.md`,
                 `ARCH-x86.md`, `ARCH-ICON.md`, `ARCH-SCRIP.md`
**Carved:** 2026-05-12

⛔ **REQUIRED READING before any code — no exceptions:**
1. `ARCH-x86.md` full file — boxes, WIRED vs BROKERED, t_* primitives, zeta.
2. `ARCH-SCRIP.md` full file — mode 1/2/3/4 definitions.
3. `GOAL-MODE4-EMIT.md` §"THE LAW OF TEMPLATE FUNCTIONS".
4. `ARCH-ICON.md` — Icon four-port model, what exists, what is missing.
5. `.github/test_icon.c` — the canonical three-column alpha/beta/gamma/omega form.
6. `.github/jcon_irgen.icn` — JCON `irgen.icn` reference (43 `ir_a_*` procedures,
   one per Icon AST construct). The canonical BB enumeration for Icon. The
   IB ladder migrates 8 of these 43 to native template form; the remaining
   35 stay on the SM_BB_PUMP_AST path (statement-level dispatch via coro_eval)
   until later ladders pick them up.

---

## Why GOAL-ICON-BB-COMPLETE was wrong (one month lost)

It encoded the four-port BB protocol as SM bytecode:
SM_JUMP / SM_RESUME / SM_STORE_GLOCAL / SM_SUSPEND / SM_RETURN.
This is wrong. Boxes are x86 blobs. SM is the thin carrier. BB is the executor.
See ARCH-SCRIP.md RS-20: "Icon programs may lower thinly into SM — often a
single SM_BB_PUMP instruction that hands the whole program to the BB engine."

---

## The critical architecture distinction: emit-time vs runtime zeta

SNOBOL4 boxes: arguments come from Σ/Δ/Ω globals (implicit subject). The
zeta is allocated at EMIT TIME (during lower()), baked as an immediate ptr
into the x86 blob. See bb_xarbn.c: `void *z = bb_arbno_new(...)`.

Icon generators: arguments are RUNTIME VALUES from the value stack (lo, hi
for `1 to N`; subject DESCR_t for `!s`). The zeta must be allocated and
populated at RUNTIME, not at emit time.

This means the flat-BB template for an Icon generator cannot bake the zeta
ptr as an immediate. Instead:

  **Pattern A — runtime-allocated zeta via SM opcodes:**
  lower.c emits instructions to: evaluate args onto stack, call
  icn_FOO_make() (a runtime allocator that pops args and returns zeta*),
  then branch into the x86 blob. The blob's alpha port reads state from
  the zeta* passed in rdi (BROKERED ABI: rdi=zeta, esi=port).

  **Pattern B — BROKERED template + bb_broker at statement level:**
  Keep using coro_eval() + bb_broker at statement level (already done).
  The BROKERED coro_bb_* C functions ARE the box implementation.
  Write template functions emit_bb_icn_* that emit BROKERED-form blobs
  (rdi=zeta, esi=port, call C runtime helper, ret) using t_bb_port_call.
  This is identical to what bb_xarbn.c, bb_xatp.c, bb_xbal.c do —
  they are all BROKERED, calling C helpers with zeta allocated at emit time.
  For Icon, the zeta is allocated at RUNTIME by SM code before broker entry.

**Decision: Pattern B is correct for this goal.**
The statement-level SM_BB_PUMP already calls coro_eval() at runtime to
build the bb_node_t (with zeta). The template functions emit BROKERED blobs
that are called via bb_broker. The wiring already exists. What is missing is
the template C functions that codify the box structure in the one-template-
per-box law, replacing the ad-hoc SM coroutine / SM_BB_PUMP_AST paths.

---

## Box structure (three-column form, from test_icon.c)

Every Icon construct maps to four labeled sections in the x86 blob:

  alpha: initialize state from args; compute first value; jmp gamma or omega
  beta:  advance state; compute next value; jmp gamma or omega
  gamma: value is ready — jmp to caller's success label
  omega: exhausted — jmp to caller's fail label

In BROKERED form (rdi=zeta, esi=port):
  prologue: cmp esi,0; je alpha; jmp beta

The template function emits this via t_bb_port_call for alpha and beta,
with t_label_define(lbl_beta) between them.

---

## Box taxonomy

  Construct         TT_ kind          Template              Semantic ref in coro_runtime.c
  ---------         --------          --------              ------------------------------
  Integer range     TT_TO / TT_TO_BY  emit_bb_icn_to        coro_bb_to_by
  Iterate !E        TT_ITERATE        emit_bb_icn_iterate   (ICN_BANG_NEXT path)
  Alternate A|B     TT_ALTERNATE      emit_bb_icn_alt       coro_bb_alternate
  Every E [do B]    TT_EVERY          emit_bb_icn_every     coro_bb_every
  Limitation E\N    TT_LIMIT          emit_bb_icn_limit     coro_bb_limit
  Bang binary E1!E2 TT_BANG_BINARY    emit_bb_icn_bang      coro_bb_bang_binary
  List concat |||   TT_LCONCAT        emit_bb_icn_lconcat   coro_bb_cat (gen path)
  Seq expr (E1;E2)  TT_SEQ_EXPR       emit_bb_icn_seq       coro_bb_seq_expr

JCON reference: jcon-master/tran/irgen.icn ir_a_* procedures.

---

## Invariants — ANY violation stops the session

1. GATE-1: test_smoke_icon PASS=5. Never regress.
2. GATE-2: test_smoke_unified_broker PASS=49. Never regress.
3. GATE-3: --ir-emit byte-identical. Never regress.
4. GATE-4: honest count never decreases between rungs.
5. GATE-5: --sm-native == --sm-interp for anchor at every rung.
6. GATE-6: SM_BB_PUMP_AST count for migrated construct = 0 in dump-sm.
7. GATE-7: --ir-emit diff vs baseline is empty.
8. Template law: t_* helpers only in template bodies. No e-> calls. No raw bytes.
9. One construct per rung. No bundling. Each rung gets its own commit.
10. Each rung flips at least one program from non-honest to honest PASS.

---

## What NOT to do (permanent record)

- SM coroutines for Icon constructs — WRONG. One month lost on this.
- New SM opcodes (SM_BB_EXEC etc.) — unnecessary. SM_BB_PUMP exists.
- e-> vtable calls in templates — forbidden by Law of Template Functions.
- Touching the statement-level SM_BB_PUMP path — it is correct, leave it.
- Allocating zeta at emit time for constructs with runtime arguments —
  SNOBOL4 boxes can do this (implicit Sigma/Delta globals) but Icon
  generators cannot (lo/hi/subject are runtime stack values).

---

## Watermark

PRUNED (superseded SM-era history, last 2026-05-12). Live state: `GOAL-ICON-BB.md` Watermark; history: git log.
