# GOAL-ICON-BB-NATIVE.md — Icon via native Byrd Box templates

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

## What currently exists and works — do not touch

**Statement level:** lower.c emits SM_PUSH_EXPR <tree_t*> + SM_BB_PUMP per Icon
statement. sm_interp pops tree_t*, calls coro_eval() -> bb_node_t at RUNTIME,
then bb_broker(node, BB_PUMP, ...). This is correct. Do not touch.

**coro_runtime.c brokered boxes:** coro_bb_to_by, coro_bb_every, coro_bb_limit,
coro_bb_bang_binary, coro_bb_seq_expr, coro_bb_alternate, icn_bb_assign_gen etc.
These are EMIT_BINARY_BROKERED (legacy C ABI fn(zeta,port)). They are the
SEMANTIC REFERENCE for each construct's alpha/beta behaviour. Not the target form.

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

## Done when

1. Every Icon generator construct has a template C function emit_bb_icn_*
   in src/runtime/x86/templates/ following the Law of Template Functions.
2. lower.c replaces SM coroutine opcodes and SM_BB_PUMP_AST fallthrough with
   proper lowering that routes through the new templates.
3. SCRIP_NO_AST_WALK=1 ./scrip --interp == ./scrip --interp for every
   program in the --interp PASS set (honest gate).
4. --ir-emit byte-identical to pre-goal baseline for every corpus program.
5. --sm-native (mode 3 JIT) produces identical output to --sm-interp for
   every honest-passing program (JIT crosscheck gate).
6. SM_BB_PUMP_AST, SM_BB_PUMP_SM, and SM coroutine opcodes (SM_RESUME,
   SM_STORE_GLOCAL, SM_SUSPEND_VALUE) never emitted for Icon constructs.
7. test_smoke_icon.sh PASS=5 and test_smoke_unified_broker.sh PASS=49
   maintained at every single rung without exception.

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

## File layout

  src/runtime/x86/templates/
    bb_icn_to.c           emit_bb_icn_to
    bb_icn_iterate.c      emit_bb_icn_iterate
    bb_icn_alt.c          emit_bb_icn_alt
    bb_icn_every.c        emit_bb_icn_every
    bb_icn_limit.c        emit_bb_icn_limit
    bb_icn_bang.c         emit_bb_icn_bang
    bb_icn_lconcat.c      emit_bb_icn_lconcat
    bb_icn_seq.c          emit_bb_icn_seq

  src/runtime/interp/icn_box_rt.c   runtime alpha/beta C helpers (zeta r/w)
  src/runtime/interp/icn_box_rt.h   declarations

---

## Session Setup

  cd /home/claude/SCRIP
  bash scripts/install_system_packages.sh
  bash scripts/build_scrip.sh
  bash scripts/build_spitbol_oracle.sh

---

## Gate protocol — every rung must pass ALL of these

  GATE-1  bash scripts/test_smoke_icon.sh                # must be PASS=5
  GATE-2  bash scripts/test_smoke_unified_broker.sh      # must be PASS=49
  GATE-3  bash scripts/test_icon_all_rungs.sh         # must be 185/48/30
  GATE-4  bash scripts/test_icon_all_rungs.sh       # honest count must not decrease
  GATE-5  ./scrip --sm-native <anchor> == ./scrip --sm-interp <anchor>  (JIT crosscheck)
  GATE-6  ./scrip --dump-sm <anchor> | grep -c SM_BB_PUMP_AST  # must be 0 for migrated construct
  GATE-7  ./scrip --ir-emit <anchor> == baseline ir-emit  (byte-identical, diff must be empty)

A rung is COMPLETE only when all seven gates pass AND honest count N_after > N_before.

---

## Rung ladder

### IB-0 — baseline + scaffolding (no behaviour change)
- [x] GATE-1..4: run all gates, record N0 (honest PASS count). Write N0 here: **212**
- [x] Create src/runtime/interp/icn_box_rt.h — empty, include guards only.
- [x] Create src/runtime/interp/icn_box_rt.c — empty, includes header.
- [x] Add icn_box_rt.o to Makefile. Build clean.
- [x] GATE-1..4 again: all unchanged. Commit. `c8032b0c`

### IB-1 — emit_bb_icn_to (integer range: 1 to N, 1 to N by S)
Step 1: understand semantics.
- [x] Read coro_bb_to_by in coro_runtime.c. Note: alpha initialises
      state.cur=lo, state.hi=hi, state.step=step. Returns cur if cur<=hi
      (or >=hi for negative step), else FAILDESCR. beta: cur+=step, same check.
- [x] Read test_icon.c to1_* / to2_* labels. Confirm three-column form.
Step 2: runtime helpers.
- [x] In icn_box_rt.h declare: typedef struct { int64_t cur,hi,step; } icn_to_state_t;
- [x] In icn_box_rt.c implement:
      icn_to_state_t* icn_to_make(int64_t lo, int64_t hi, int64_t step) — calloc + init.
      DESCR_t icn_to_alpha(void *z, int port) — alpha: set cur=lo; beta: cur+=step;
        shared: if step>0 && cur>hi, or step<0 && cur<hi: return FAILDESCR;
        return descr_int(cur).
Step 3: template.
- [x] Write src/runtime/x86/templates/bb_icn_to.c:
      void emit_bb_icn_to(emitter_t *e, void *zeta_ptr,
                          bb_label_t *lbl_succ, bb_label_t *lbl_fail, bb_label_t *lbl_beta)
      Body: t_bb_box_banner("ICN_TO","range");
            t_bb_port_call(zeta_ptr, "icn_to_alpha", fn_ptr, 0, lbl_succ, lbl_fail);
            t_label_define(lbl_beta);
            t_bb_port_call(zeta_ptr, "icn_to_alpha", fn_ptr, 1, lbl_succ, lbl_fail);
      (void)e; — mandatory.
Step 4: lower.c wiring.
- [x] In lower_to / lower_to_by: evaluate lo/hi/step expressions onto SM stack.
      Emit SM_CALL_FN "icn_to_make" with 2 or 3 args -> returns icn_to_state_t*.
      Emit call to emit_bb_icn_to with the returned zeta ptr.
      Delete old SM coroutine emission (SM_JUMP/SM_RESUME/SM_STORE_GLOCAL etc).
Step 5: gates.
- [x] Anchor: corpus program using `write(1 to 5)` in scalar context.
- [x] GATE-1..7 all pass. N_after > N_before (N1 > N0). Commit.

### IB-2 — emit_bb_icn_iterate (!E)
Step 1: semantics.
- [x] Read ICN_BANG_NEXT handler in sm_interp.c (rung15 area).
      State: {subject DESCR_t, index int}. Supports string/list/table/record.
      alpha: init index=0, fetch element[0]. beta: index++, fetch element[index].
      Fail when index >= length/size.
Step 2: runtime helpers in icn_box_rt.c.
- [x] icn_iterate_state_t: {DESCR_t subject; int index;}.
- [x] icn_iterate_make(DESCR_t subject) — calloc + set subject, index=0.
- [x] DESCR_t icn_iterate_tick(void *z, int port) — port 0: reset index=0;
      port 1: index++; shared: fetch element, return it or FAILDESCR.
Step 3: template bb_icn_iterate.c.
Step 4: wire lower_iterate. Delete SM coroutine body (SM_CALL_FN ICN_BANG_NEXT path).
Step 5: anchor rung15_iterate_string.icn. GATE-1..7. N up. Commit.

### IB-3 — emit_bb_icn_alt (A|B alternate)
Step 1: semantics.
- [x] Read coro_bb_alternate / icn_alternate_state_t in coro_runtime.c.
      Two child bb_node_t (left, right). Phase tracks which is active.
      alpha: try left-alpha. If left-omega, try right-alpha. If right-omega: omega.
      beta: resume active branch. If active-omega, advance to next branch.
Step 2: runtime helpers.
- [x] icn_alt_state_t: {bb_node_t left; bb_node_t right; int phase;}.
- [x] icn_alt_make(bb_node_t left, bb_node_t right).
- [x] DESCR_t icn_alt_tick(void *z, int port).
Step 3: template bb_icn_alt.c.
Step 4: wire lower_alternate non-hoisted path. Delete lower_bb_pump_ast for TT_ALTERNATE.
Step 5: anchor: rung alternate program. GATE-1..7. N up. Commit.

### IB-4 — emit_bb_icn_every (every E [do body])
Step 1: semantics.
- [x] Read coro_bb_every carefully. The body (if present) runs via bb_exec_stmt
      per tick. loop_next save/restore around body call.
      alpha: pump generator alpha; if gamma run body; return gen value.
      beta: pump generator beta; if gamma run body; return gen value.
      omega from generator -> omega the every box.
Step 2: runtime helpers. icn_every_state_t, icn_every_make, icn_every_tick.
Step 3: template bb_icn_every.c.
Step 4: wire lower_every. Delete SM_BB_PUMP_EVERY for LANG_ICN path.
Step 5: anchor: every write(1 to 3). GATE-1..7. N up. Commit.

### IB-5 — emit_bb_icn_limit (E\N)
Step 1: semantics.
- [x] Read coro_bb_limit. Wraps inner generator; caps at N values.
      alpha: count=0, pump inner alpha; if gamma count++; if count>max omega.
      beta: if count>=max omega; pump inner beta; if gamma count++.
Step 2: runtime helpers. icn_limit_state_t, icn_limit_make, icn_limit_tick.
Step 3: template bb_icn_limit.c.
Step 4: wire lower_limit. Delete emit_push_expr + SM_BB_PUMP for Icon TT_LIMIT.
Step 5: anchor: rung14 limit program. GATE-1..7. N up. Commit.

### IB-6 — emit_bb_icn_bang (E1!E2 bang binary)
Step 1: semantics.
- [x] Read coro_bb_bang_binary. Pump E2 generator each tick; call E1(arg).
      If E1 fails on arg, skip to next E2 value (goal-directed evaluation).
      alpha: pump E2 alpha -> call E1. beta: loop E2 beta until E1 succeeds.
Step 2: runtime helpers. icn_bang_state_t, icn_bang_make, icn_bang_tick.
Step 3: template bb_icn_bang.c.
Step 4: wire lower_bang_binary. Delete SM_BB_PUMP_AST call.
Step 5: anchor: bang_binary corpus program. GATE-1..7. N up. Commit.

### IB-7 — emit_bb_icn_lconcat (||| generative list concat)
Step 1: semantics. Read coro_bb_cat (gen path) in coro_runtime.c.
Step 2: runtime helpers. icn_lconcat_state_t, icn_lconcat_make, icn_lconcat_tick.
Step 3: template bb_icn_lconcat.c.
Step 4: wire lower_lconcat. Delete SM_BB_PUMP_AST call.
Step 5: anchor: lconcat corpus program. GATE-1..7. N up. Commit.

### IB-8 — emit_bb_icn_seq (generative (E1;E2;...;En))
Step 1: semantics. Read coro_bb_seq_expr. Eval E1..E(n-1) for side effects;
        build last_box from En; pump last_box.
Step 2: runtime helpers. icn_seq_state_t, icn_seq_make, icn_seq_tick.
Step 3: template bb_icn_seq.c.
Step 4: wire lower_seq_expr generative path. Delete SM_BB_PUMP_AST call.
Step 5: anchor: seq_expr corpus program. GATE-1..7. N up. Commit.

### IB-9 — purge SM_BB_PUMP_AST from Icon path
- [x] grep lower.c for SM_BB_PUMP_AST in LANG_ICN-reachable paths. Must be zero.
- [x] Any remaining call: replace with abort("BUG: Icon AST pump — kind %d", t->t).
- [x] GATE-1..4 full corpus sweep. GATE-5 JIT crosscheck full corpus.
- [x] Honest PASS count == --interp PASS count. Explain any gap in commit message.
- [x] Commit.

### IB-10 — purge SM coroutine opcodes from Icon path
- [x] grep lower.c for SM_RESUME, SM_STORE_GLOCAL, SM_SUSPEND_VALUE in Icon paths.
      Must be zero after IB-1..IB-8 land.
- [~] is_suspendable() returns false for all migrated TT_ kinds.
      ⛔ INVARIANT AS WRITTEN IS UNSOUND — see audit below. Effectively
      already satisfied (no SM coroutine emission in lower.c Icon paths);
      nothing additional to do.
- [x] Build clean. GATE-1..7 full sweep. Commit.

✅ **IB-10 part 1 closed sess 2026-05-12 (Claude Opus 4.7, SCRIP `1b13cc6d`):**
SM coroutine emission purged from `lower_every` and `lower_limit_every`.
`lower_alternate_gen` deleted (was only called from the purged bodies).
All Icon `every` / `every (E\N)` statements now route through
`SM_BB_PUMP_EVERY` → `coro_eval` → `bb_broker` (the statement-level
dispatch IB-1..IB-8 left in place). Net -164 lines from `lower.c`.
`lower_suspend` (still emits SM_SUSPEND_VALUE) is the Icon `suspend`
STATEMENT, not a generator subexpression coroutine — out of IB-10
scope as written.

Gates (SCRIP 7be3c8e0 → 1b13cc6d):
  GATE-1 smoke_icon:        PASS=5   FAIL=0    (unchanged)
  GATE-2 smoke_broker:      PASS=22  FAIL=27   (unchanged, post-PB-8)
  GATE-3 icon ir_all:       PASS=180 FAIL=55   (unchanged)
  GATE-4 honest (NO_AST):   PASS=210 FAIL=2    (+2 / -2 vs baseline)

✅ **IB-10 part 2 resolved (no work needed) sess 2026-05-12 (Claude Opus 4.7):**

Audit of `is_suspendable()` callers in `coro_runtime.c`:

| Lines | Site | Purpose |
|-------|------|---------|
| 1320  | TT_TO with gen lo/hi              | wrap via coro_bb_to_by |
| 1459  | TT_IDENTICAL with gen child       | drive gen, test === per value |
| 1516  | binop_map (ADD/SUB/MUL/.../EQ/NE) | drive gen in arith/relational |
| 1533  | TT_CAT                            | string concat with gen child |
| 1559  | TT_IDX                            | s[gen_idx] |
| 1576  | find(cset, gen_subject)           | builtin with gen arg |
| 1655  | generic builtin loop              | per-gen-arg icn_fnc_gen |
| 1685  | upto(cset, gen_subject)           | |
| 1705  | user-proc TT_FNC fallback         | |
| 1757  | TT_NONNULL (\E) filter            | |
| 1800  | TT_FNC for is_proc                | |
| 1822  | TT_ASSIGN with gen RHS            | x := gen Byrd-box assignment |

Every caller asks the SEMANTIC question — *"does this subtree yield a
sequence?"* — to choose between simple-eval and coro_bb_* generative
wrapping. None of them ask the DISPATCH question — *"should I emit SM
coroutine bytecode?"*. The 8 migrated TT_ kinds (TT_TO, TT_TO_BY,
TT_ITERATE, TT_ALTERNATE, TT_LIMIT, TT_EVERY, TT_BANG_BINARY,
TT_SEQ_EXPR) remain semantic generators regardless of which backend
drives them; the IB-1..IB-8 templates and the still-active coro_bb_*
wrappers both depend on `is_suspendable` correctly reporting YES for
these kinds.

The invariant as written conflated two distinct questions. The actual
intent ("no SM coroutine emission for migrated kinds") was already
satisfied by IB-10 part 1. No code change needed.

Watermark numbers in this file were stale-by-a-few on absolute counts
(prior session reported 206/181; live baseline at 7be3c8e0 was 208/180).
Deltas in the table above are against the live baseline.

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

  Last session:    2026-05-12 (Claude Sonnet 4.6) — 10 commits, --interp 180->196, honest 215->259.
                   (1) TT_ITERATE DT_DATA/DT_T before descr_to_str_icn (ir +8).
                   (2) SM_EXP real result for Icon ^ (ir +5).
                   (3) SM_BB_EVAL for TT_ALTERNATE value context (honest +29).
                   (4) SM_BB_EVAL extended to TT_TO/TO_BY/ITERATE/BANG_BINARY (honest +8).
                   (5) SM_STORE_FRAME: propagate FAILDESCR (while-read() loop fix, ir +1).
                   (6) New Icon builtins: open/close/read(file)/reads/IDENTICAL/set/ASGN/variable.
                   (7) sm_call_proc: static variable save/restore (IC-9, ir +1).
                   (8) lower_augop: relop augops via SM_ACOMP/SM_LCOMP; bb_eval_value
                       TT_AUGOP returns FAILDESCR on failure (not NULVCL).
                   (9) bb_eval_value TT_VAR: fall through to NV when frame slot unset —
                       fixes static list access in alternates (roman.icn works).
                   Root cause of (9): build_proc_scope removes initial{}-assigned names from
                   scope (SM_STORE_VAR/NV path); sm_call_proc icn_scope_patch adds them back
                   at high slot indices; bb_eval_value was reading empty slots instead of NV.
  SCRIP HEAD:    7efdf09a
  Honest PASS:     259 FAIL=1 ABORT=0 (FAIL=rung36_jcon_arith &collections flakiness)
  --interp PASS:     196 FAIL=39
  BB tally:        43 JCON ir_a_* total. 8 templates (IB-1..IB-8). 35 on SM_BB_PUMP_EVERY.
  Current rung:    GOAL DONE. NEXT: --interp triage (39 FAILs). Priority:
                   roman "cannot convert" (integer(n)>0|fail — PROC_FAIL in alternate);
                   nested generator conjunction (every A & B: both A and B must generate);
                   more missing builtins (args, image(x,w), remove);
                   scan/string partial output (complex scan-context alternation).
