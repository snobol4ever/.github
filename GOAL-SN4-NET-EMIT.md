# GOAL-SN4-NET-EMIT.md — SNOBOL4 → .NET MSIL Emitter (IR_t-based, beauty self-host)

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
║  Mode 1 (`--ir-run` standalone AST interp) is unchanged and remains the reference path.        ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝


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
**Done when:** smoke_snobol4_net + broader SNOBOL4 corpus test suites pass (pattern matching complete). NOTE: beauty.sno removed as finality requirement — beauty contains EVAL/CODE which require mode-1 AST evaluation; .NET emitter focusing on deterministic pattern + arithmetic + function paths.

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

SN4-NET-5 covers everything needed to take beauty.sno from "assembles and runs" to "byte-identical to SPITBOL oracle." During session 2026-05-15 (Claude Opus 4.7) the work decomposed into substeps as the actual semantics of `SM_CALL_FN`, `SM_SUSPEND_VALUE`, and the SPITBOL-style call frame became clearer. Substeps are landed incrementally so each is independently testable against the smoke gate.

#### SN4-NET-5a — Emit-side correctness fixes (control flow, comment syntax)

- [x] **SN4-NET-5a** (one4all `eb74b9a5`) — Fix the cases where emit_net.c was producing invalid MSIL or silent no-ops that previously assembled-and-ran but did wrong things:
  - MSIL comment syntax: `;` is not a comment in MSIL — use `//`. The `default:` case in the SM dispatch was emitting `; [net SM op N unimplemented]` which caused ilasm syntax errors. Now emits `//`.
  - `SM_JUMP`, `SM_JUMP_S`, `SM_JUMP_F` were silently `break;` with no `br` instruction emitted — assembled clean, did nothing. Now emit conditional `br` to `NET_L{target}` via `SnoRt::last_ok()`.
  - `SM_HALT` was falling through to the auto-trailer `stloc _pc; br NET_DISPATCH` — now branches to `NET_DONE`.
  - Added a `has_continue` flag to each iteration of the SM walker. When set, the auto-trailer is suppressed. Jumps, returns, and halt all set `has_continue=1`.
  - Added safe-default cases (no-op `break`) for all opcodes that lack semantic emission in this rung: SM_CALL_FN, SM_RETURN family, SM_PAT_* family, SM_BB_* family, SM_DEFINE_ENTRY, SM_DEFINE, SM_EXEC_STMT, SM_INCR/DECR, SM_LOAD/STORE_FRAME, SM_LOAD/STORE_GLOCAL, SM_PUSH_EXPRESSION, SM_PUSH_EXPR, SM_CALL_EXPRESSION, SM_SUSPEND, SM_SUSPEND_VALUE, SM_ICMP_GT/LT.

  Runtime-side fixes in SnoRt.il:
  - `coerce_num` used `Double::Parse(string)` which threw on any non-numeric input — that's everywhere in SNOBOL4. Now uses `Double::TryParse(string, float64&)` and defaults to 0.0 on parse failure. Same fix in `_obj_to_dbl`.
  - `do_return` now sets `_last_ok` per return kind: FRETURN→false, RETURN/NRETURN→true. Was a no-op.
  - `sno_call` now dispatches over 8 built-ins (SIZE, TRIM, DUPL, SUBSTR, IDENT, DIFFER, INTEGER, DATATYPE), with a fail-and-pop-nargs default for unknown names that sets `_last_ok=false` and pushes `""`. Mirrors `SnoRt.j` skeleton.

  **Gate:** smoke 7/7 maintained; beauty.il assembles with ilasm clean; mono exits 0 on `beauty.exe`.

#### SN4-NET-5b — User-function dispatch (call/return; no params yet)

- [x] **SN4-NET-5b** (one4all `bb77ac29`) — Wire `SM_SUSPEND_VALUE` / `SM_CALL_FN` (for named user functions) and the `SM_RETURN` family to actually invoke and return from user-defined function bodies. Without this, all SNOBOL4 programs that use DEFINE produce empty output for their function-call sites.
  - **Pre-scan pass** in `emit_net_from_sm`: build a `(name → entry_pc)` table by walking the SM_Program once and recording every `SM_LABEL` instruction whose `a[2].i` is non-zero (the `define_entry=1` marker).
  - **SM_SUSPEND_VALUE / SM_CALL_FN** for known user functions: emit a 3-instruction sequence — `push_ret_pc(i+1); ldc.i4 entry_pc; stloc _pc; br NET_DISPATCH`. The `i+1` is the PC immediately after the call site, so return resumes at the right place. Functions not in the table fall through to the existing `sno_call(name, nargs)` built-in dispatch.
  - **SM_RETURN / SM_FRETURN / SM_NRETURN** (all variants): in addition to existing `do_return(kind, has_val)` call which sets `_last_ok`, now also emit `pop_ret_pc(); stloc _pc; br NET_DISPATCH` to actually return to the caller's PC. Without this, returns just set last_ok and then fell through to the next SM instruction, which was undefined behavior.
  - **SnoRt.il additions:**
    - `_ret`: `Stack<int32>` static field for return PCs.
    - `_frames`: `Stack<Dictionary<string, object>>` static field (allocated and initialized but not yet used — wiring for SN4-NET-5c).
    - `push_ret_pc(int32) : void`, `pop_ret_pc() : int32` with empty-stack guard returning -1.
    - Both new fields initialized in `.cctor` and `_init`.

  **Gate:** smoke 7/7 maintained; a single-argument DEFINE'd function executes its body and returns. For `Greet(who)` calling `Greet('World')`, the function body is reached (versus skipping it entirely in SN4-NET-5a). Argument binding gap means the body sees the param uninitialized — that's SN4-NET-5c.

#### SN4-NET-5c — Parameter binding and frame save/restore

- [x] **SN4-NET-5c** — Make user-function calls bind their argument values into the parameter names' globals, mirroring SPITBOL semantics. The h_call function in `src/processor/sm_jit_interp.c` is the reference implementation; this step ports its parameter binding loop to the .NET emit path.

  ##### Step 1: Parse parameter list from DEFINE literal
  
  In the SM_Program pre-scan pass (already added in SN4-NET-5b), when an `SM_SUSPEND_VALUE s="DEFINE" nargs=1` is encountered, walk backward to find the immediately-preceding `SM_PUSH_LIT_S`. Its `a[0].s` is the DEFINE argument string in the form `"FuncName(p1,p2,...)"` or `"FuncName(p1,p2,...)locals..."`. Parse out the parameter names (split on `(`, then `,`, until `)`), strip whitespace and uppercase if `-f` case-folding is active. Store the parameter list for `FuncName` alongside the entry_pc in the function table. Use a parallel array or extend the existing structure.

  ##### Step 2: Emit parameter binding at function entry
  
  After the pre-scan, when emitting the SM_LABEL with `define_entry=1` (the function's entry), follow that label with a per-parameter binding sequence:
  ```
  NET_L<entry_pc>:
      ; bind params in reverse order — args are on _stk in push-order, so last
      ; arg is on top. Pop in reverse to match param order.
      ldstr      "<paramN>"
      call       void SnoRt::store_var(string)
      ...
      ldstr      "<param1>"
      call       void SnoRt::store_var(string)
  ```
  Each `store_var` pops the value stack into the param-name's global. Order matters: args were pushed left-to-right at the call site, so the rightmost arg is on top of the stack and must bind to the rightmost parameter.
  
  Special case: when caller passed fewer args than the function declares, the missing slots must be bound to the null string. Easiest approach: at the call site (SM_SUSPEND_VALUE / SM_CALL_FN), if nargs < declared_arity, push `null` (empty string) `declared_arity - nargs` times before the call. This keeps the entry-side emit uniform.

  ##### Step 3: Frame save/restore via _frames
  
  SNOBOL4 functions use the global name-value store — parameter names are real variables that the caller's code may also be using. To prevent corruption across recursive or nested calls, on entry we must save the prior values of every parameter name AND the function name (used as the return value receptacle), and on return we must restore them.
  
  Use the `_frames` Stack<Dictionary<string,object>> field added in SN4-NET-5b. New methods on SnoRt:
  - `frame_save(string name) : void` — read current var value (or null), push a single-key dictionary onto `_frames`, also call store_var to bind a new initial value. Actually simpler: combine into one method.
  - `frame_push_save(string name, object initial) : void` — push current value of var `name` onto a frame dict, then `store_var(name)` to the new value.
  - At entry: a sequence of `frame_push_save` calls (one per param and one for the function name itself).
  - At return (in SM_RETURN family handlers, before `pop_ret_pc`): a single call to `frame_restore_all()` that walks the top frame's dict and restores every key, then pops the frame.
  
  Alternative design: one big save list per call. The frame dict has the function-name as key 0 and params as keys 1..N. `frame_enter(string fname, string[] pnames)` and `frame_exit()` are the only two methods.

  ##### Step 4: Return-value handling
  
  In SNOBOL4 the function name (e.g. `Greet`) is the variable that holds the return value — `Greet = 'Hello, ' who` assigns the return value. On entry to the function, this name's prior value is saved (covered by step 3). On RETURN, before frame_exit pops everything back, we need to peek the function-name's current value and push it onto the value stack as the call's result. On FRETURN, push FAIL (or skip the push and let last_ok=false signal failure). On NRETURN, push the name itself (the var indirection) rather than the dereferenced value.
  
  Pre-scan needs to also record the function name → return-value-name (typically same as function name, but `&FNCLEVEL` or aliasing may differ).

  **Gate:** smoke 7/7 maintained. New test: `Greet(who) Greet = 'Hello, ' who :(RETURN)` followed by `OUTPUT = Greet('World')` produces `Hello, World` matching SPITBOL oracle. Recursive factorial `Fact(n)` returns the correct value and doesn't corrupt the caller's local n.

#### SN4-NET-5d — Pattern opcode wiring

- [ ] **SN4-NET-5d** — Wire `SM_PAT_*` opcodes to invoke the already-emitted `pat_*_*` BB classes (those produced by SN4-NET-2's BB template emitters). Beauty uses pattern matching for its main parse loop; without this, ~half of beauty's logic still runs on empty strings.

  - Each SM_PAT_* opcode is a marker that says "construct a BB pattern node of type X here." Beauty's compiled SM program has hundreds of these between an outer `SM_BB_PUMP` / `SM_BB_ONCE` driver.
  - At emit time, the SM walker needs to: (a) instantiate the right pat_*_* class with the right constructor args from `instr->a[*]`, (b) chain them (CAT and ALT compose children), (c) hand the root to the SM_BB_PUMP/ONCE driver.
  - The runtime model: a MatchState struct holds cursor, subject, anchor; BB Alpha() returns success and updates cursor; BB Beta() retries.
  - This is mostly mechanical given the 19 BB classes already emitted, but needs a per-PAT-opcode stack-based composition: SM_PAT_LIT pushes a new BB instance onto a "current pattern" stack, SM_PAT_CAT pops two and pushes a CAT wrapper, etc.
  - SnoRt needs a `_pat_stack : Stack<IByrdBox>` and helpers `pat_push(IByrdBox)`, `pat_pop_cat()`, `pat_pop_alt()`, `pat_run_pump()`, `pat_run_once()`.

  **Gate:** A simple pattern program (e.g. `S = 'hello world' ; S 'hello' = 'goodbye' ; OUTPUT = S`) produces the correct output via .NET emit path.

#### SN4-NET-5z — Byte-identical beauty (closeout)

- [ ] **SN4-NET-5z** — With 5a, 5b, 5c, 5d landed, run beauty.sno and diff against SPITBOL oracle. Resolve any remaining built-ins beauty uses that aren't in the SnoRt 8 (likely: REPLACE, ARRAY, TABLE, CONVERT, PROTOTYPE, and others — discover by running and adding as needed). Address whitespace, line-ending, and minor formatting differences if any remain.

  **Gate:** `md5sum` of `mono beauty.exe < beauty.sno` matches the oracle. Per session 2026-05-15 oracle is 622 lines under current corpus (the GOAL header's 646-line / `abfd19a7...` md5 was captured at an earlier corpus state and may have drifted; the live gate is "byte-identical to the live oracle output").

### SN4-NET-6 — Cross-check ladder against SNOBOL4 corpus

- [ ] **SN4-NET-6** — After beauty self-hosts, run the broader SNOBOL4 corpus (≈260 programs in `corpus/crosscheck/`) through `scrip --sm-emit --target=net` and diff each against the JIT-mode reference. Mirrors the JS ladder (`test_sn4_js_ladder_safe.sh` 10/129) and the JIT-mode crosscheck (180-program parity).

  Build the test runner script `scripts/test_sn4_net_ladder.sh` following the pattern of `test_sn4_js_ladder_safe.sh`: for each .sno in the corpus, emit + assemble + run, diff output to the .ref oracle, count PASS/FAIL/SKIP. Use the existing `--jit-run` as the secondary reference for programs without .ref files.

  **Gate:** ≥ JS ladder's PASS count, ideally ≥ JIT-mode parity baseline (180). Document remaining failures and their root causes (typically missing built-ins, pattern features, or extensions beauty doesn't exercise).

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
watermark: SN4-NET-5 ⏳ (5a ✅, 5b ✅, 5c ✅ — parameter binding + frame save/restore)
head: one4all b3c0527d (main) — sn4-net-5c-wip merged
session: 2026-05-15 (Claude Opus 4.7) — SN4-NET-5c closed
progress:
  SN4-NET-1 ✅ SnoRt.il scalar runtime;
  SN4-NET-2 ✅ 19 BB emitters in emit_net.c;
  SN4-NET-3 ✅ SM walker + --target=net wiring;
  SN4-NET-4 ✅ smoke 9/9 PASS (now with define_simple + define_recursive);
  SN4-NET-5a ✅ control-flow / comment / runtime fixes (one4all eb74b9a5);
  SN4-NET-5b ✅ user-function dispatch — call/return without param
    binding via pre-scan name→pc table + push/pop_ret_pc on _ret stack
    (one4all bb77ac29);
  SN4-NET-5c ✅ parameter binding + frame save/restore (one4all 64a89740, merged b3c0527d).
    Step 1: parse param list from DEFINE literal ✅
    Step 2: emit param binding (reverse pop) at function entry ✅
    Step 3: frame save/restore — frame_push + frame_save(name) at
      define_entry; frame_exit() at all RETURN/NRETURN/FRETURN sites
      AND on null-name SM_CALL_FN implicit return. Recursive Fact(5)=120 ✅
    Step 4: return-value via push_var(fname) on RETURN ✅
  SN4-NET-5d ⏳ SM_PAT_* opcode wiring to pat_*_* BB classes — NEXT.
  SN4-NET-5z — byte-identical beauty closeout.
  SN4-NET-6 — broad SNOBOL4 corpus ladder.

session 2026-05-15 gates (on main @ b3c0527d):
  smoke_snobol4_net    9/9 PASS  (was 8/8; +define_recursive)
  smoke_snobol4        7/7 PASS  (unchanged)
  smoke_snocone        5/5 PASS  (unchanged)
  smoke_icon           5/5 PASS  (unchanged)
  smoke_prolog         5/5 PASS  (unchanged)
  smoke_rebus          4/4 PASS  (unchanged)
  unified_broker      23/49 PASS (unchanged vs sn4-net-5c-wip baseline)
  all_modes            2/3 PASS  (--jit-emit --net failure pre-existing on main)
```

## Step 3 implementation notes (closed)

Three SnoRt.il methods added between push_ret_pc/pop_ret_pc and the push helpers:

- `frame_push()` — push new empty `Dictionary<string,object>` onto `_frames`.
- `frame_save(string name)` — peek top frame, lookup `_vars[name]` via
  `ContainsKey + get_Item` (avoids `TryGetValue` because mono ilasm
  rejects `ldloca` against `[mscorlib]System.Object` ref params with
  generic instantiations in this pattern), default to `""` if not
  present, store into top frame under `name`.
- `frame_exit()` — pop top frame, materialize its keys via
  `List<string>::.ctor(IEnumerable<T>)` taking the
  `Dictionary`2/KeyCollection<!0,!1>` directly. Loop the list by
  integer index and restore each var from the frame dict. Note the
  type syntax `Dictionary`2/KeyCollection<!0,!1>` (parameters on the
  nested type) is the form mono ilasm accepts; the alternative
  `Dictionary`2<!0,!1>/KeyCollection` form parses but generates code
  that throws `MissingMethodException` at runtime, and casting to
  `IEnumerable<T>` or `ICollection<T>` directly fails the same way.

Emitter changes in `emit_net.c`:

- `SM_LABEL define_entry`: after the existing last_ok=true, emit
  `frame_push()`, then `frame_save(fname)` for the function name and
  `frame_save(param_i)` for each parameter, then the existing reverse-
  pop `store_var` loop. Order matters: save before store.
- `SM_RETURN/_S/_F`, `SM_FRETURN/_S/_F`, `SM_NRETURN/_S/_F`: emit
  `frame_exit()` before the existing `pop_ret_pc + stloc _pc + br
  NET_DISPATCH` sequence. `frame_exit` pops AFTER `push_var(fname)`
  has read the return value, so the return value survives the frame
  pop.
- `SM_CALL_FN` with null/empty `a[0].s` inside a function body (i.e.
  `pc_to_fn[i] >= 0`): treat as implicit `:(RETURN)`. Emit
  `push_var(fname) + frame_exit + do_return + pop_ret_pc + br
  NET_DISPATCH`. This is the trailer that the SNOBOL4 lowering emits
  at the end of every DEFINE body to handle fall-through.

## Hand-off — frame save/restore remaining (SN4-NET-5c step 3)

Branch `sn4-net-5c-wip @ 06576570` is in a good state — non-recursive
DEFINEs work, smoke 8/8, broker +9 vs main, no regressions. Ready to
merge to main when the user gives the handoff phrase.

What's still needed for full SN4-NET-5c ✅:

**Step 3 — Frame save/restore.** SNOBOL4 parameters are global variables.
Without saving them across calls, recursive `Fact(n)` overwrites the
caller's `n`. The fix mirrors h_call in src/processor/sm_jit_interp.c
lines 880-925: at function entry, save the current values of the
function-name var AND every param-name var into a frame dict, then bind
the new arg values. At return, restore from the frame.

The SnoRt.il already has _frames : Stack<Dictionary<string,object>>
allocated and initialized but unused (added in 5b). Needed methods:

  void frame_enter(string fname, string[] pnames)
    — push new frame dict;
    — for fname and each pname, save current var value into the dict;
    — caller still does store_var on each param after (or fold the
      "set new value" into a different helper).

  void frame_exit()
    — pop top frame dict;
    — for each entry, restore var to saved value.

Then in emit_net.c:
  - SM_LABEL define_entry: before the existing per-param store_var loop,
    emit a frame_enter call (need to build a string[] of param names —
    can do via a precomputed array in MSIL static fields, or via repeated
    push then frame_enter_n style).
  - SM_RETURN / SM_NRETURN / SM_FRETURN (all variants): before the
    existing do_return + pop_ret_pc, emit a frame_exit call.

Verification: Fact(5) should produce "120" matching SPITBOL oracle.
Add `define_recursive` to the smoke gate guarding against future regressions.

## Hand-off — original SN4-NET-5c hand-off below (now mostly resolved)


This session got most of SN4-NET-5c built but the integration of the
function-body-end return is wrong. Smoke 7/7 still passes on the branch
because none of the smoke programs use DEFINE.

### What the WIP branch contains

`emit_net.c`:
- `net_parse_define_proto()` helper that parses `"Name(p1,p2,...)"` from
  the `SM_PUSH_LIT_S` that precedes `SM_SUSPEND_VALUE s="DEFINE"`.
- Pre-scan extended to a 3-pass walk:
  1. Collect `SM_LABEL define_entry=1` → `(name, entry_pc)`
  2. Link param lists to function entries via the prototype parse
  3. Build `pc_to_fn[]` map: each PC → which function (if any) it
     belongs to, computed via the `SM_JUMP`-around target.
- `SM_LABEL define_entry` case: emit `set_last_ok(true)` followed by
  per-parameter `store_var()` in reverse-pop order.
- `SM_RETURN/NRETURN` family: push function-name's value via `push_var`
  before `do_return + pop_ret_pc`.
- Conditional `SM_RETURN_S/SM_RETURN_F` (and NRETURN/FRETURN `_S/_F`
  variants): now conditional on `last_ok` (`_S` branches to next PC if
  `!last_ok`, `_F` if `last_ok`). Was unconditional before — that was
  a separate bug from SN4-NET-5b worth fixing on its own.

`SnoRt.il`:
- `_vars`: `Dictionary<string,object>` static field (was missing — real
  variable storage replaces stubs).
- `push_var` now does `Dictionary.TryGetValue` lookup, falling back to
  empty string on miss. Still INPUT-special-cased.
- `store_var` now does `Dictionary.set_Item` for non-OUTPUT names. Was
  a complete no-op for non-OUTPUT before — which the smoke tests didn't
  catch because they're all literal-only.
- `_vars` initialized in `.cctor` and `_init`.

### Why it doesn't work yet

Test program `def_test.sno`:
```
        DEFINE('Greet(who)')                          :(end_g)
Greet   Greet = 'Hello, ' who                         :(RETURN)
end_g   OUTPUT = Greet('World')
END
```

Expected output: `Hello, World`
Actual .NET output: `Hello, ` then `World` on two lines.

Diagnosis: looking at the SM dump, PC 12 in `def_test.sno` is
`SM_CALL_FN` with **no `a[0].s` and no `a[1].i`** — appearing to be a
synthetic "implicit fall-through return" marker that scrip's JIT
handles somehow. In the .NET emit path, this `SM_CALL_FN` with
empty/null name falls through to `sno_call` default-handler (pushes
`""`, sets `last_ok=false`), then the auto-trailer moves to PC 13 =
`end_g` label, then PC 14, PC 15, and the program calls `Greet`
AGAIN — but now `who` is already bound to `"World"` from the first
(partial) call, so the inner call's body prints `"Hello, World"`,
then the OUTER `OUTPUT = Greet('World')` evaluates Greet again and
prints `"World"` (or some leftover). Either way, the function body
is effectively being inlined into the surrounding program.

### Fix paths for next session

1. **Look at how the JIT distinguishes** — `h_call` in
   `src/processor/sm_jit_interp.c` at line 699+ shows the dispatch
   logic. When `name` is `NULL`, what code path does it take? There
   must be a special case (maybe `INVOKE_fn(NULL, ...)` crashes
   cleanly and last_ok=false, which is then a guard for a separate
   compile-time-synthesized return). Read until the answer is clear,
   then mirror it.

2. **Likely fix in `emit_net.c`**: at the `SM_CALL_FN`/`SM_SUSPEND_VALUE`
   case, when `instr->a[0].s` is NULL or empty AND `pc_to_fn[i] >= 0`
   (we're inside a function body), treat it as an implicit return:
   emit `push_null; pop_ret_pc; stloc _pc; br NET_DISPATCH`.

3. **Strengthen the smoke gate** so future iterations catch this:
   add a `define_simple` smoke program to `test_smoke_snobol4_net.sh`
   that exercises `DEFINE(Greet(who))` → `Greet = 'Hello, ' who` →
   `:(RETURN)` → `OUTPUT = Greet('World')`. With it in the gate, this
   regression class can't slip through.

4. **After fixing the implicit return**, re-run the 31-script test
   harness to confirm no regressions, then commit `sn4-net-5c-wip`
   onto main and mark `SN4-NET-5c ✅`.

### Recipe to resume

```bash
cd /home/claude/one4all
git fetch origin
git checkout sn4-net-5c-wip
bash scripts/build_scrip.sh

# Quick verify reproduction:
cd /tmp
cat > def_test.sno <<'EOF'
        DEFINE('Greet(who)')                          :(end_g)
Greet   Greet = 'Hello, ' who                         :(RETURN)
end_g   OUTPUT = Greet('World')
END
EOF
/home/claude/one4all/scrip --sm-emit --target=net def_test.sno > def_test.il
ilasm /output:def_test.exe def_test.il /home/claude/one4all/src/runtime/net/SnoRt.il
mono def_test.exe        # currently prints "Hello, \nWorld\n"
                         # expected: "Hello, World\n"

# Also dump SM to inspect:
/home/claude/one4all/scrip --sm-run --dump-sm def_test.sno
```
```
