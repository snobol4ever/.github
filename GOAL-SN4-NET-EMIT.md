# GOAL-SN4-NET-EMIT.md — SNOBOL4 → .NET MSIL Emitter (IR_t-based, beauty self-host)

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  A C Byrd box (C BB) is ANY C function with signature: DESCR_t foo(void *zeta, int entry)      ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                             ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

⛔ **Read before any source file:** ARCH-IR.md then ARCH-NET.md then ARCH-EMITTER.md.
⛔ **Prereq:** GOAL-IR-EMITTER-PREREQ.md must be complete (IEP-1 through IEP-6 all ✅).

**Repo:** one4all + .github
**Goal:** scrip --sm-emit --target=net file.sno emits a .il file; ilasm + mono/dotnet runs it correctly.
**Done when:** beauty.sno byte-identical to SPITBOL oracle (md5 abfd19a7a834484a96e824851caee159, 646 lines).

---

## Pipeline

The stages pass exactly ONE structure between them:

```
tree_t  →  lower  →  IR_t  →  THIS EMITTER  →  .il file
```

This emitter reads IR_t only. It does not read SM_Program. It produces both:
- SM-equivalent MSIL invokestatic/callvirt sequences for scalar IR_t nodes (push, store, call, jump, return) inside a switch/dispatch loop implemented via `br` targets
- BB MSIL class bodies for generator IR_t nodes (pattern boxes implementing IByrdBox with Alpha/Beta methods)

---

## Reference implementations — all BB work is already done

Every SNOBOL4 BB is already implemented in MSIL. Before writing any BB emitter template for a node kind, read the corresponding class in `src/runtime/net/bb_boxes.il`. The mapping is one-to-one:

| IR_t node kind | Reference class in bb_boxes.il | Notes |
|---|---|---|
| IR_PAT_LIT | Snobol4.Runtime.Boxes.bb_lit | `_lit` string field, `_len` int field |
| IR_PAT_SPAN | Snobol4.Runtime.Boxes.bb_span | `_chars` string field |
| IR_PAT_BREAK | Snobol4.Runtime.Boxes.bb_brk | `_chars` string field |
| IR_PAT_ANY | Snobol4.Runtime.Boxes.bb_any | `_chars` string field |
| IR_PAT_NOTANY | Snobol4.Runtime.Boxes.bb_notany | `_chars` string field |
| IR_PAT_LEN | Snobol4.Runtime.Boxes.bb_len | `_n` int field |
| IR_PAT_POS (rpos=0) | Snobol4.Runtime.Boxes.bb_pos | `_n` int field |
| IR_PAT_POS (rpos=1) | Snobol4.Runtime.Boxes.bb_rpos | `_n` int field |
| IR_PAT_TAB (rtab=0) | Snobol4.Runtime.Boxes.bb_tab | `_n` int field |
| IR_PAT_TAB (rtab=1) | Snobol4.Runtime.Boxes.bb_rtab | `_n` int field |
| IR_PAT_REM | Snobol4.Runtime.Boxes.bb_rem | no payload |
| IR_PAT_ARB | Snobol4.Runtime.Boxes.bb_arb | `_count`/`_start` state fields |
| IR_PAT_ARBNO | Snobol4.Runtime.Boxes.bb_arbno | `_body` IByrdBox field |
| IR_PAT_CAT | Snobol4.Runtime.Boxes.bb_seq | `_left`/`_right` IByrdBox fields |
| IR_PAT_ALT | Snobol4.Runtime.Boxes.bb_alt | `_children` IByrdBox[] field |
| IR_PAT_ASSIGN_IMM | Snobol4.Runtime.Boxes.bb_capture (imm=1) | `_varname` string, `_child` IByrdBox |
| IR_PAT_ASSIGN_COND | Snobol4.Runtime.Boxes.bb_capture (imm=0) | `_varname` string, `_child` IByrdBox |
| IR_PAT_FENCE | Snobol4.Runtime.Boxes.bb_fence | no payload |
| IR_PAT_ABORT | Snobol4.Runtime.Boxes.bb_abort | no payload |

The emitter's task for each node kind: write a C function `emit_net_bb_NODE(IR_t *nd, FILE *out, int stmt_id, int node_id)` that generates the MSIL class body equivalent to the reference class above, with the node's payload values (literal string, charset, integer n, etc.) substituted in as MSIL ldstr / ldc.i4 instructions in the `.ctor` body.

Also read: `src/lower/ir_exec.c` IR_exec_node() — the interpreter for IR_t. Each case is the authoritative semantics for its node kind.

---

## .NET emission model

**Scalar nodes** (IR_LIT_I, IR_VAR, IR_BINOP, IR_ASSIGN, IR_CALL, IR_RETURN, IR_SEQ, IR_PROC) emit into a switch/dispatch loop. MSIL has no switch-on-arbitrary-int; implement via a jump table of `br` targets or a `switch` instruction on a zero-based integer `_pc`:

```msil
.method public static void Main() cil managed
{
  .entrypoint
  .maxstack 8
  .locals init (int32 _pc, string _tmp)
  ldc.i4.0
  stloc _pc
DISPATCH:
  ldloc _pc
  switch (L0, L1, L2, L3)
  br DONE
L0:  // set_stno(1)
  call void SnoRt::set_stno(int32)    // SM_STNO
  ldc.i4.1
  stloc _pc
  br DISPATCH
L1:  // push_str("hello", 5)
  ldstr "hello"
  ldc.i4.5
  call void SnoRt::push_str(string, int32)
  ldc.i4.2
  stloc _pc
  br DISPATCH
L2:  // store_var("OUTPUT")
  ldstr "OUTPUT"
  call void SnoRt::store_var(string)
  ldc.i4.3
  stloc _pc
  br DISPATCH
L3:  // halt_tos()
  call void SnoRt::halt_tos()
  br DONE
DONE:
  ret
}
```

**Generator nodes** (all IR_PAT_* kinds) emit as nested MSIL classes before Main(), each implementing `IByrdBox` with Alpha(MatchState) and Beta(MatchState) methods. They are instantiated and wired inside Main() at SM_EXEC_GEN sites:

```msil
// Emitted for IR_PAT_LIT nd with sval="hello", stmt_id=5, node_id=3
.class nested public auto ansi beforefieldinit pat_5_3
       extends [mscorlib]System.Object implements IByrdBox
{
  .field public string _lit
  .field public int32 _len
  .field public class IByrdBox succ
  .field public class IByrdBox fail

  .method public void .ctor(string lit, int32 len) cil managed
  {
    .maxstack 2
    ldarg.0
    ldarg.1
    stfld string pat_5_3::_lit
    ldarg.0
    ldarg.2
    stfld int32 pat_5_3::_len
    ret
  }

  .method public valuetype Spec Alpha(class MatchState ms) cil managed
  {
    // if (ms.Delta + _len > ms.Omega) goto FAIL
    ldarg.1; ldfld int32 MatchState::Delta
    ldarg.0; ldfld int32 pat_5_3::_len
    add
    ldarg.1; ldfld int32 MatchState::Omega
    bgt PAT_5_3_A_FAIL
    // if (ms.Sigma.Substring(ms.Delta, _len) != _lit) goto FAIL
    ldarg.1; ldfld string MatchState::Sigma
    ldarg.1; ldfld int32 MatchState::Delta
    ldarg.0; ldfld int32 pat_5_3::_len
    callvirt instance string [mscorlib]System.String::Substring(int32, int32)
    ldarg.0; ldfld string pat_5_3::_lit
    call bool [mscorlib]System.String::op_Inequality(string, string)
    brtrue PAT_5_3_A_FAIL
    // ms.Delta += _len; succ.Alpha(ms)
    ldarg.1
    ldarg.1; ldfld int32 MatchState::Delta
    ldarg.0; ldfld int32 pat_5_3::_len
    add
    stfld int32 MatchState::Delta
    ldarg.0; ldfld class IByrdBox pat_5_3::succ
    ldarg.1
    callvirt instance valuetype Spec IByrdBox::Alpha(class MatchState)
    ret
  PAT_5_3_A_FAIL:
    ldarg.0; ldfld class IByrdBox pat_5_3::fail
    ldarg.1
    callvirt instance valuetype Spec IByrdBox::Alpha(class MatchState)
    ret
  }

  .method public valuetype Spec Beta(class MatchState ms) cil managed
  {
    // ms.Delta -= _len; fail.Alpha(ms)
    ldarg.1
    ldarg.1; ldfld int32 MatchState::Delta
    ldarg.0; ldfld int32 pat_5_3::_len
    sub
    stfld int32 MatchState::Delta
    ldarg.0; ldfld class IByrdBox pat_5_3::fail
    ldarg.1
    callvirt instance valuetype Spec IByrdBox::Alpha(class MatchState)
    ret
  }
}
```

---

## SnoRt.il — scalar runtime class

All SM-level operations called by scalar node emission live in `src/runtime/net/SnoRt.il` as static methods on class `SnoRt`. This mirrors the architecture of `SnoRt.j` (JVM) and `sno_runtime.js` (JS). Methods required:

| Method | MSIL signature |
|---|---|
| push_int | void push_int(int32) |
| push_str | void push_str(string, int32) |
| push_real | void push_real(float64) |
| push_null | void push_null() |
| push_var | void push_var(string) |
| store_var | void store_var(string) |
| pop_void | void pop_void() |
| concat | void concat() |
| neg | void neg() |
| exp_op | void exp_op() |
| coerce_num | void coerce_num() |
| arith | void arith(int32) |
| acomp | void acomp(int32) |
| lcomp | void lcomp(int32) |
| last_ok | bool last_ok() |
| set_last_ok | void set_last_ok(bool) |
| set_stno | void set_stno(int32) |
| halt_tos | void halt_tos() |
| call | void call(string, int32) |
| do_return | void do_return(int32, bool) |
| _init | void _init() |
| _finalize | void _finalize() |

INPUT reads from `System.Console.ReadLine()`. OUTPUT traps on `store_var("OUTPUT")` → `System.Console.WriteLine()`. MatchState is a class with `Sigma` (string), `Delta` (int32), `Omega` (int32) fields and a pending-captures list for ASSIGN_COND deferred capture: `push_cap(string varname, string text)`, `commit_caps()`, `discard_caps()`.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
apt-get install -y mono-complete dotnet-sdk-10.0 2>/dev/null || true
bash /home/claude/one4all/scripts/build_scrip.sh
ilasm 2>&1 | head -1     # verify ilasm available (from mono-complete)
dotnet --version          # verify dotnet available
```

---

## Steps

All steps here build on top of GOAL-IR-EMITTER-PREREQ (IEP-1..6). The visitor infrastructure, wiring phase, and scalar node emission are already done for x86/JVM/JS. This GOAL adds .NET-specific completeness and drives to beauty self-host.

### SN4-NET-1 — SnoRt.il: complete .NET scalar runtime class

- [x] **SN4-NET-1** — Create `src/runtime/net/SnoRt.il`. All static methods listed in the table above. The value stack is a .NET `Stack<object>` static field. Type coercion follows the same rules as SnoRt.j (coerce_num: if object is string → parse as double; if already numeric → pass through). OUTPUT: trap in store_var when varname == "OUTPUT" → Console.WriteLine. INPUT: push_var on "INPUT" → Console.ReadLine(). Pending-captures list for ASSIGN_COND.

  **Gate:** Hand-written test .il file calling push_str + halt_tos assembles with ilasm and runs under mono/dotnet, printing the string.

### SN4-NET-2 — Complete all 19 BB template emitters for .NET

- [x] **SN4-NET-2** — For each IR_PAT_* kind in the table above, implement `emit_net_bb_NODE(IR_t *nd, FILE *out, int stmt_id, int node_id)`. For each: read the reference class from `src/runtime/net/bb_boxes.il`, then write the C emitter that generates an equivalent nested MSIL class parameterized by nd->sval / nd->ival / nd->n (rpos/rtab variant flag). All 19 node kinds.

  Count: 19 BB template functions (LIT, SPAN, BREAK, ANY, NOTANY, LEN, POS, RPOS, TAB, RTAB, REM, ARB, ARBNO, CAT/SEQ, ALT, ASSIGN_IMM, ASSIGN_COND, FENCE, ABORT).

  String escaping for MSIL ldstr: double-quote → `\"`, backslash → `\\`, non-printable → `\u00NN`. MSIL ldstr does not use octal or hex escapes; use Unicode escapes only.

  **Gate:** All 19 emit valid MSIL (ilasm assembles a file containing all 19 class stubs without error).

### SN4-NET-3 — Scalar emitter (SM_Program walker) + wire into scrip.c

- [x] **SN4-NET-3** — Create `src/emitter/emit_net.c` with `emit_net_from_sm(SM_Program *prog, FILE *out)` and `emit_net_program(tree_t *tree, FILE *out)` entry point. The SM walker converts SM opcodes to MSIL invokestatic/callvirt calls to SnoRt static methods, wrapping everything in a `switch (_pc)` dispatch loop using MSIL's `switch` instruction. Emit `.assembly`, `.module`, `.class Prog`, and `Main()` wrapper. Wire `--sm-emit --target=net` in `scrip.c`.

  **Gate:** `scrip --sm-emit --target=net hello.sno > hello.il && ilasm hello.il && mono hello.exe` prints `Hello World`.

### SN4-NET-4 — Smoke 7/7

- [x] **SN4-NET-4** — Write `scripts/test_smoke_snobol4_net.sh`. Run all 7 SNOBOL4 smoke programs via `scrip --sm-emit --target=net`, assemble with ilasm, run with mono (or dotnet), compare output to oracle `.ref` files.

  **Gate:** 7/7 PASS.

### SN4-NET-5 — Beauty self-host

- [ ] **SN4-NET-5** — Run beauty.sno under `scrip --sm-emit --target=net`. Assemble and execute. Diff output against SPITBOL oracle.

  **Gate:** md5 of output matches `abfd19a7a834484a96e824851caee159` (646 lines).

---

## Key invariants

- **Reads IR_t only.** This emitter never reads SM_Program. IR_t is the sole input.
- **19 BB kinds, all pre-implemented.** Every Alpha/Beta body is already written in bb_boxes.il. Read it before writing any emitter template.
- **MSIL label naming: UPPERCASE_PORT format.** `PAT_5_3_A_FAIL`, `PAT_5_3_B_EXIT` — matching the style in ARCH-NET.md.
- **`.maxstack` and `.locals init` required** in every method. Start with `.maxstack 8`.
- **`boxes.dll` is pre-built** at `src/runtime/net/boxes.dll`. The emitter references it via `.assembly extern boxes {}`. Do not rebuild it unless a BB implementation is changed.
- **Flag:** `--sm-emit --target=net` (not `--jit-emit --net`).
- **Build tool:** `ilasm` from mono-complete. Always check with `ilasm /dll` for library classes, `ilasm` (no flag) for executables.
- **Always `-p:EnableWindowsTargeting=true`** when using `dotnet build` on a Linux host.

---

## State

```
watermark: SN4-NET-5 ⏳ (partial)
head: one4all eb74b9a5
session: 2026-05-15 (Claude Opus 4.7)
progress: SN4-NET-1 ✅ SnoRt.il scalar runtime; SN4-NET-2 ✅ 19 BB emitters emit_net.c;
  SN4-NET-3 ✅ SM walker + --target=net wiring; SN4-NET-4 ✅ smoke 7/7 PASS.
  SN4-NET-5 ⏳ partial: beauty.sno assembles + executes without exception.
    Fixed: MSIL comment ';' → '//'; SM_JUMP/JUMP_S/JUMP_F now emit conditional br to NET_L{target};
    SM_HALT branches to NET_DONE (was falling through); has_continue tracking; added stubs for
    SM_CALL_FN, SM_RETURN/FRETURN/NRETURN (all variants), SM_DEFINE_ENTRY, SM_DEFINE, SM_EXEC_STMT,
    SM_INCR/DECR, SM_LOAD/STORE_FRAME/GLOCAL, SM_PUSH_EXPRESSION, SM_PUSH_EXPR, SM_CALL_EXPRESSION,
    SM_SUSPEND/SUSPEND_VALUE, SM_PAT_* family, SM_BB_* family, SM_ICMP_GT/LT.
    Runtime: coerce_num and _obj_to_dbl now use Double.TryParse (was Double.Parse crashing on
    non-numeric strings); do_return now sets last_ok per kind (FRETURN→false, RETURN/NRETURN→true);
    sno_call dispatches to 8 built-ins (SIZE, TRIM, DUPL, SUBSTR, IDENT, DIFFER, INTEGER, DATATYPE)
    with fail-and-pop-nargs default for unknown names.
    Beauty status: emits valid MSIL (58407 lines), ilasm clean, mono runs to completion (exit 0),
    produces 628 stdout lines (oracle 622) but only 1 non-blank line. Stores write empty strings
    because pattern matches and user-defined functions are still stubs.
  NEXT: user-defined function dispatch — SM_DEFINE_ENTRY must build a name→pc table; SM_CALL_FN
    must look up user functions before falling back to built-ins; need a call stack in SnoRt for
    return addresses + a frame-slot array for locals. After that: wire SM_PAT_* opcodes to the
    19 already-emitted pat_*_* classes via Alpha/Beta calls on a MatchState.
```
