# MILESTONE-RT-SIL-MACROS.md — SIL Macro Classification for SM + scrip-interp

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-05 (revised — dual-axis classification)
**Status:** DESIGN — feeds RT milestones and SM_Program instruction set
**Source:** `v311.sil` (CSNOBOL4 2.3.3, Phil Budne) + `include/macros.h` (C translations)

---

## The Question (Sharpened)

SIL defines ~130 macro instructions and ~211 named procedures.
For each, we need to know **both**:

1. **scrip-interp axis** — does it become a C function / C macro in the RT layer?
   Used by: `snobol4.c`, `argval.c`, `invoke.c`, `nmd.c`, `eval_code.c`, `stmt_exec.c`
2. **SM_Program axis** — does it become a named SM_Program instruction?
   Used by: `sm_interp.c` dispatch loop (RUNTIME-9) + all emitters (x86, JVM, .NET, JS)

These are **independent axes**. A macro can be:
- RT only (too low-level for the SM — e.g. field access macros)
- SM only (pure control flow with no C-level helper needed)
- BOTH (the SM instruction dispatches to a C RT function — most common)
- SKIP (GC/compiler/IO internal — irrelevant to our runtime)

---

## Classification Tags

| Tag | Meaning |
|-----|---------|
| **RT** | C macro/inline/function in `sil_macros.h` or RT source file |
| **SM** | SM_Program instruction in `SM_Op` enum + dispatch case in `sm_interp.c` |
| **BOTH** | SM instruction whose dispatch calls a C RT function by the same name |
| **SKIP** | GC/compiler/IO internal — not useful |
| **DONE** | Already implemented |

---

## Group 1 — Descriptor Access (GETD / PUTD family)

**Axis: RT only.** These are C field accesses on `DESCR_t`.
Too low-level to be SM instructions — the SM operates on typed values,
not raw memory offsets. Every RT function uses these.
C translations are in `include/macros.h` (`D()`, `D_A()`, `D_V()`, `D_F()`).

| SIL Macro | SIL Semantics | C Translation | scrip-interp | SM_Program |
|-----------|---------------|---------------|:---:|:---:|
| `GETD d,base,off` | d = *(base+off) | `d = *(DESCR_t*)((char*)base+off)` | RT macro | — |
| `PUTD base,off,d` | *(base+off) = d | `*(DESCR_t*)((char*)base+off) = d` | RT macro | — |
| `GETDC d,base,off` | d = base->field[off] | struct field access | RT macro | — |
| `PUTDC base,off,d` | base->field[off] = d | struct field assign | RT macro | — |
| `GETAC d,base,off` | d = (ptr)base[off] | pointer load | RT macro | — |
| `PUTAC base,off,d` | base[off] = (ptr)d | pointer store | RT macro | — |
| `SETAC base,val` | base.a = constant | `d.ptr = (void*)val` | RT macro | — |
| `SETAV d,src` | d.a = src.v | `d.ptr = (void*)(intptr_t)src.v` | RT macro | — |
| `MOVD dst,src` | dst = src (full descr) | `dst = src` | RT macro | — |
| `MOVDIC d,doff,s,soff` | d[doff] = s[soff] | indirect struct copy | RT macro | — |
| `MOVV dst,src` | dst.v = src.v | `dst.v = src.v` | RT macro | — |
| `MOVA dst,src` | dst.a = src.a | `dst.ptr = src.ptr` | RT macro | — |
| `MOVBLK dst,src,sz` | memcpy block | `memmove(dst+DESCR, src+DESCR, sz)` | RT macro | — |

**sil_macros.h action:** `#define GETDC(d,base,off)`, `#define PUTDC(base,off,d)`, etc.
Mirror `macros.h` D_A/D_V/D_F field accessors with our `DESCR_t` layout.

---

## Group 2 — Type Test and Comparison

**Axis: RT (all); SM (ACOMP, RCOMP, LCOMP only).**
Type tests are C conditionals in RT functions. Only the three
compare ops that replace common `SM_CALL` paths earn SM status.

| SIL Macro | SIL Semantics | scrip-interp | SM_Program |
|-----------|---------------|:---:|:---:|
| `TESTF d,type,eq,ne` | if (d.f & type) goto eq else ne | **RT** `IS_FNC(d)` | — |
| `TESTFI d,type,off,eq,ne` | indirect type test | **RT** | — |
| `VEQLC d,T,t,f` | if (d.v == T) goto t else f | **RT** `IS_TYPE(d,T)` | — |
| `VEQL d1,d2,t,f` | if (d1.v == d2.v) | **RT** `SAME_TYPE(a,b)` | — |
| `DEQL d1,d2,t,f` | if (d1==d2) full descr equal | **RT** `DEQL(a,b)` | — |
| `AEQLC d,val,t,f` | if (d.a == constant) | **RT** `AEQLC(d,v)` | — |
| `AEQL d1,d2,t,f` | if (d1.a == d2.a) | **RT** `AEQL(a,b)` | — |
| `ACOMP d1,d2,lt,eq,gt` | compare integers/addresses | **RT** `ACOMP(a,b)` | **SM** `SM_ACOMP` |
| `ACOMPC d,val,lt,eq,gt` | compare address vs constant | **RT** `ACOMPC(d,v)` | — |
| `RCOMP d1,d2,lt,eq,gt` | compare reals | **RT** `RCOMP(a,b)` | **SM** `SM_RCOMP` |
| `LEQLC sp,n,t,f` | if (sp.len == n) | **RT** `SP_LEN_EQ(sp,n)` | — |
| `LCMP sp1,sp2,lt,eq,gt` | compare string lengths | **RT** `LCMP(a,b)` | — |
| `LCOMP sp1,sp2,lt,eq,gt` | lexicographic compare | **RT** `LCOMP_fn(a,b)` → `lexcmp()` | **SM** `SM_LCOMP` |
| `VCMPIC d,T,off,t,f` | type compare indirect | **RT** | — |
| `VCOMPC d,T,t,f` | value compare constant | **RT** | — |
| `PCOMP d,val,lt,eq,gt` | compare as pointer (unsigned) | **RT** `PCOMP(a,b)` | — |

**SM rationale:** `SM_ACOMP` replaces `SM_CALL "EQ"/"GT"/"LT"` for integer predicates.
`SM_RCOMP` replaces `SM_CALL "GE"/"LE"` for real predicates.
`SM_LCOMP` replaces `SM_CALL "LGT"/"LLT"/"LGE"/"LLE"` for string predicates.
All three are hot paths; making them native SM ops eliminates INVOKE overhead.

**sil_macros.h action:** `IS_INT`, `IS_REAL`, `IS_STR`, `IS_PAT`, `IS_NAME`, `IS_KW`,
`IS_EXPR`, `IS_CODE`, `IS_FNC`, `TESTF`, `VEQLC`, `DEQL`, `AEQLC`.

---

## Group 3 — Arithmetic on Addresses/Integers

**Axis: RT (all inline ops); SM (INCR, DECR only as dedicated ops; ADD/SUB/MUL/DIV already DONE).**

| SIL Macro | SIL Semantics | scrip-interp | SM_Program |
|-----------|---------------|:---:|:---:|
| `INCRA d,n` | d.a += n | **RT** `INCRA(d,n)` → `d += n` | **SM** `SM_INCR n` |
| `DECRA d,n` | d.a -= n | **RT** `DECRA(d,n)` → `d -= n` | **SM** `SM_DECR n` |
| `SUM d,a,b` | d = a + b (integer) | **RT** | SM `SM_ADD` (**DONE**) |
| `MULT d,a,b` | d = a * b | **RT** | SM `SM_MUL` (**DONE**) |
| `MULTC d,a,c` | d = a * constant | **RT** | — |
| `DIVIDE d,a,b` | d = a / b | **RT** | SM `SM_DIV` (**DONE**) |
| `SUBTRT d,a,b` | d = a - b | **RT** | SM `SM_SUB` (**DONE**) |
| `ADDLG d,sp` | d += sp.len | **RT** `ADDLG(d,sp)` | — |
| `ADREAL d,x,y` | d = x + y (real) | **RT** | — (covered by SM_ADD with type dispatch) |
| `MPREAL d,x,y` | d = x * y (real) | **RT** | — |
| `DVREAL d,x,y` | d = x / y (real) | **RT** | — |
| `SBREAL d,x,y` | d = x - y (real) | **RT** | — |
| `MNSINT d,x` | d = -x (integer, overflow check) | **RT** `NEG_I_fn(d)` | — (SM_NEG handles) |
| `MNREAL d,x` | d = -x (real) | **RT** `NEG_R_fn(d)` | — |
| `INTRL d,x` | d = (real)x int→real | **RT** `INT_TO_REAL_fn(d)` | — |
| `RLINT d,x,f,ok` | d = (int)x real→int, fail→f | **RT** `REAL_TO_INT_fn(d)` | — |
| `EXREAL d,x,y,err` | d = x**y (reals) | **RT** `EXP_R_fn(d,e)` | — (SM_EXP handles) |

**SM rationale:** `SM_INCR`/`SM_DECR` model SIL's ubiquitous `INCRA OCICL,DESCR` / `DECRA XCL,2*DESCR` — advancing/retreating the instruction pointer and loop counters. These appear literally hundreds of times in v311.sil. As SM ops they let `sm_interp.c` advance its own PC without a full INVOKE.

---

## Group 4 — String / Specifier Operations

**Axis: RT (all C function calls); SM (TRIM, SPCINT, SPREAL only).**
The specifier ops (LOCSP, GETLG, etc.) are C inline helpers.
Only the three that appear in hot SM-level paths earn SM status.

| SIL Macro | SIL Semantics | C Translation | scrip-interp | SM_Program |
|-----------|---------------|---------------|:---:|:---:|
| `LOCSP sp,d` | sp = specifier from descriptor | `X_LOCSP(sp,d)` in macros.h | **RT** | — |
| `GETSPC d,base,off` | sp = *(base+off) | struct access | **RT** | — |
| `PUTSPC base,off,sp` | *(base+off) = sp | struct assign | **RT** | — |
| `GETLG d,sp` | d = sp.len | `S_L(sp)` | **RT** | — |
| `PUTLG sp,d` | sp.len = d | `S_L(sp) = d` | **RT** | — |
| `GETSIZ d,base` | d = block.title.v | `D_V(base)` | **RT** | — |
| `SETSIZ base,d` | block.title.v = d | `D_V(base) = d` | **RT** | — |
| `SETLC sp,n` | sp.len = constant | `S_L(sp) = n` | **RT** | — |
| `SETSP sp1,sp2` | sp1 = sp2 (copy) | `_SPEC(sp1) = _SPEC(sp2)` | **RT** | — |
| `SHORTN sp,n` | sp.len -= n | `S_L(sp) -= n` | **RT** | — |
| `FSHRTN sp,n` | sp.off += n; sp.len -= n | `S_O(sp)+=n; S_L(sp)-=n` | **RT** | — |
| `TRIMSP sp1,sp2` | trim trailing blanks | `trimsp(sp1,sp2)` in macros.h | **RT** `TRIM_fn` | **SM** `SM_TRIM` |
| `REMSP sp1,sp2` | sp1 = sp2 minus leading sp | `X_REMSP(sp1,sp2,sp)` | **RT** | — |
| `SUBSP sp,d,n` | substring | `substr(sp,sp2,descr)` | **RT** `SUBSTR_fn` | — |
| `APDSP sp1,sp2` | append sp2 to sp1 | `APDSP(sp1,sp2)` in macros.h | **RT** | — |
| `LEXCMP sp1,sp2` | lexicographic compare → int | `lexcmp(sp1,sp2)` | **RT** → `SM_LCOMP` | via SM_LCOMP |
| `SPCINT d,sp,f,ok` | parse integer from string | `spcint(d,sp)` | **RT** `SPCINT_fn` | **SM** `SM_SPCINT` |
| `SPREAL d,sp,f,ok` | parse real from string | `spreal(d,sp)` | **RT** `SPREAL_fn` | **SM** `SM_SPREAL` |
| `REALST sp,d` | format real → string | `realst(sp,d)` | **RT** `REALST_fn` | — |
| `INTSP sp,d` | format integer → string | `intspc(sp,d)` | **RT** `INTSP_fn` | — |
| `LVALUE sp,d` | get l-value specifier | `lvalue(sp,d)` | **RT** | — |
| `LEQLC sp,n,t,f` | sp.len == n? | `S_L(sp) == n` | **RT** | — |

**SM rationale for TRIM/SPCINT/SPREAL:**
- `SM_TRIM` — appears in VARVAL (string cleanup before use). Very common in pattern matching setup.
- `SM_SPCINT`/`SM_SPREAL` — appear in INTVAL and EVAL's numeric coercion path. Making them SM ops eliminates a `SM_CALL "spcint"` round-trip. EVAL uses both in sequence; an SM instruction can branch on parse failure directly (the `f_label` operand in SCRIP-SM.md).

---

## Group 5 — Control Flow

**Axis: mostly SM (already DONE); key additions are JUMP_INDIR, SELBRA, STATE_PUSH/POP.**

| SIL Macro | SIL Semantics | scrip-interp | SM_Program |
|-----------|---------------|:---:|:---:|
| `BRANCH label` | unconditional goto | goto | SM `SM_JUMP` (**DONE**) |
| `RCALL ret,proc,args,exits` | call procedure with exit table | call dispatch | SM `SM_CALL` (**DONE**) |
| `RRTURN ret,n` | return via exit n | return/longjmp | SM `SM_RETURN`/`SM_FRETURN` (**DONE**) |
| `BRANIC d,off` | branch indirect via descriptor | `((FnPtr)d.ptr)()` | SM **`SM_JUMP_INDIR`** |
| `SELBRA d,table` | select branch by integer index | switch(d.v){table[i]} | SM **`SM_SELBRA`** |
| `PUSH d` | push descriptor onto stack | cstack++ | SM `SM_PUSH_VAR`/lit (**DONE**) |
| `POP d` | pop descriptor from stack | cstack-- | SM `SM_POP` (**DONE**) |
| `SPUSH sp` | push specifier (2 descriptors) | cstack += SPEC/DESCR | **RT** (used in EXPVAL save) |
| `SPOP sp` | pop specifier | cstack -= SPEC/DESCR | **RT** (used in EXPVAL restore) |
| `ISTACKPUSH` | push 14 descriptors + 4 specs | full state save | SM **`SM_STATE_PUSH`** |
| `PSTACK x` | save pattern stack ptr | `x.a = cstack-1` | **RT** (bb_pool context) |
| `ISTACK` | init stack pointer | cstack = stack base | **RT** (init only) |

**SM_JUMP_INDIR use:** `GOTG` (`:(<VAR>)` computed goto) — pops a CODE descriptor,
jumps to its code block. Also `INVK1` `BRANIC INCL,0` — indirect dispatch to function.
In `sm_interp.c` this is: `pc = (SM_Instr*)descr.ptr; continue;`

**SM_SELBRA use:** `EXPVAL`'s `SELBRA SCL,(FAIL,RTXNAM,RTZPTR)` — selects exit
based on integer index. In `sm_interp.c`: `goto *exit_table[instr.u.table[d.ival]]`
or equivalent computed goto. Also used in `INTERP`'s `INVOKE` exit dispatch.

**SM_STATE_PUSH/POP use:** `EXPVAL` saves 14 descriptors + 4 specifiers before
executing a nested EXPRESSION, restores them after. In `sm_interp.c` this becomes
a memcpy of the interpreter's register file to a save stack.

---

## Group 6 — Pattern Building (SM — DONE)

All `SM_PAT_*` instructions are already designed in SCRIP-SM.md.

`SM_PAT_LIT`, `SM_PAT_ANY`, `SM_PAT_NOTANY`, `SM_PAT_SPAN`, `SM_PAT_BREAK`,
`SM_PAT_LEN`, `SM_PAT_POS`, `SM_PAT_RPOS`, `SM_PAT_TAB`, `SM_PAT_RTAB`,
`SM_PAT_ARB`, `SM_PAT_REM`, `SM_PAT_BAL`, `SM_PAT_FENCE`, `SM_PAT_ABORT`,
`SM_PAT_FAIL`, `SM_PAT_SUCCEED`, `SM_PAT_ALT`, `SM_PAT_CAT`, `SM_PAT_DEREF`,
`SM_PAT_CAPTURE`.

SIL equivalents: `ANY`, `BREAK`, `BREAKX`, `NOTANY`, `SPAN`, `LEN`, `POS`,
`RPOS`, `RTAB`, `TAB`, `ARBNO`.

---

## Group 7 — Byrd Box Construction (RT — DONE)

| SIL Proc | Our BB box | scrip-interp | SM_Program |
|----------|-----------|:---:|:---:|
| `NAM` (.VAR conditional assign) | `bb_capture.c` | **DONE** | — |
| `DOL` ($VAR immediate assign) | `bb_capture.c` (immed) | **DONE** | — |
| `SCAN`/`SJSR`/`SCNR` (scan loop) | `BB-DRIVER` | **DONE** | via `SM_EXEC_STMT` |
| `ATOP` (@ cursor assign) | `bb_capture.c` (cursor) | **DONE** | — |
| `ANY`/`BREAK`/`BREAKX`/`NOTANY`/`SPAN` | `bb_*.c` | **DONE** | — |
| `LEN`/`POS`/`RPOS`/`RTAB`/`TAB` | `bb_*.c` | **DONE** | — |
| `ARBNO` | `bb_arbno.c` | **DONE** | — |

---

## Group 8 — Named Builtins (RT via INVOKE table)

All become C functions registered via `register_fn()`.
None are SM instructions — they are called through `SM_CALL name, nargs`.
SM instruction `SM_CALL` dispatches to the INVOKE table.

| SIL Proc | Builtin | scrip-interp | SM_Program | RT milestone |
|----------|---------|:---:|:---:|------|
| `INVOKE`/`INVK1`/`INVK2` | dispatch core | **RT** `INVOKE_fn` | via `SM_CALL` | RUNTIME-1 |
| `ARGVAL` | arg evaluator (untyped) | **RT** `ARGVAL_fn` | via SM dispatch | RUNTIME-1 |
| `VARVAL` | arg → STRING | **RT** `VARVAL_fn` | via SM dispatch | RUNTIME-2 |
| `INTVAL` | arg → INTEGER | **RT** `INTVAL_fn` | via SM dispatch | RUNTIME-2 |
| `PATVAL` | arg → PATTERN | **RT** `PATVAL_fn` | via SM dispatch | RUNTIME-2 |
| `VARVUP` | arg → uppercase STRING | **RT** `VARVUP_fn` | via SM dispatch | RUNTIME-2 |
| `NAME` | .X → DT_N descriptor | **RT** `NAME_fn` | via SM dispatch | RUNTIME-3 |
| `ASGN`/`ASGNV`/`ASGNIC` | assignment with hooks | **RT** `ASGN_fn` | via SM dispatch | RUNTIME-5 |
| `NMD`/`NMD1`–`NMD5`/`NMDIC` | naming list commit | **RT** `NMD_fn` | via SM dispatch | RUNTIME-4 |
| `EXPVAL`/`EXPEVL` | EXPRESSION execute | **RT** `EXPVAL_fn` | `SM_STATE_PUSH/POP` | RUNTIME-6 |
| `CONVE`/`CODER` | string→EXPRESSION/CODE | **RT** `CONVE_fn` | via SM dispatch | RUNTIME-7 |
| `CNVRT` | CONVERT(X,T) | **RT** `CONVERT_fn` | via SM dispatch | RUNTIME-7 |
| `EVAL`/`EVAL1` | EVAL() builtin | **RT** `EVAL_fn` | via SM dispatch | RUNTIME-8 |
| `INTERP`/`INTRP0` | interpreter core | `execute_program()` | `sm_interp.c` loop | RUNTIME-9 |
| `INIT` | statement header | per-stmt setup | SM header decode | RUNTIME-9 |
| `GOTO` | offset goto | goto dispatch | `SM_JUMP` target | RUNTIME-9 |
| `GOTL` | label goto + special labels | label lookup | `SM_JUMP` + INVOKE | RUNTIME-9 |
| `GOTG` | `:(<VAR>)` computed goto | — | `SM_JUMP_INDIR` | RUNTIME-9 |
| `BASE` | code basing | — | `SM_CALL` setup | RUNTIME-9 |
| `PLS` | unary +X (NOT identity) | ⚠️ missing | via SM dispatch | RUNTIME-2 fix |
| `INTGER` | INTEGER(X) | ✅ | via SM dispatch | — |
| `EQ`/`NE`/`GT`/`LT`/`GE`/`LE` | numeric predicates | ✅ | via `SM_ACOMP` | — |
| `LEQ`/`LNE`/`LGT`/`LLT`/`LGE`/`LLE` | string predicates | ✅ | via `SM_LCOMP` | — |
| `DIFFER`/`IDENT` | identity tests | ✅ | via SM dispatch | — |
| `SIZE`/`TRIM`/`DUPL` | string ops | ✅ | via SM dispatch | — |
| `SUBSTR`/`RPLACE`/`REVERS` | string ops | ✅ | via SM dispatch | — |
| `LPAD`/`RPAD`/`CHAR` | string ops | ✅ | via SM dispatch | — |
| `ARRAY`/`ASSOC`/`ITEM` | array/table ops | ✅ | via SM dispatch | — |
| `COPY`/`APPLY`/`DEFINE`/`OPSYN` | control | ✅ | via SM dispatch | — |
| `TRACE`/`STOPTR` | trace hooks | ⬜ stub | via SM dispatch | RUNTIME-5 |
| `LABEL` | LABEL(X) | partial | via SM dispatch | RUNTIME-3 |
| `IND` | $X indirect | ✅ | via SM dispatch | — |
| `KEYWRD` | &KW access | partial | via SM dispatch | RUNTIME-3 |
| `ARG`/`LOCAL`/`FIELD`/`FIELDS` | introspection | ✅ | via SM dispatch | — |
| `DATDEF`/`FUNCTN`/`SORT`/`RSORT` | meta | ✅ | via SM dispatch | — |
| `EVAL` stub→full | EVAL() | ⚠️ | via SM dispatch | RUNTIME-8 |
| `DATE`/`TIME` | system | ✅ | via SM dispatch | — |

---

## Group 9 — BLOCK-mode Operations (SKIP)

Lines 7160–10211 of v311.sil: BLAND, BOX, BOXIN, AFRAME, etc.
**Decision: SKIP.** No corpus tests use SNOBOL4B blocks.

---

## Group 10 — Compiler Internals (SKIP)

`CMPILE`, `ELEMNT`, `EXPR`, `FORWRD`, `FORRUN`, `FORBLK`, `NEWCRD`,
`CTLADV`, `BLOCK` (allocator), `GC`, `GCM`, `SPLIT`, `BINOP`, etc.
**Decision: SKIP.** We have `CMPILE.c`.

---

## The Two-Axis Master Table — SM Instructions

These are the SM_Program instructions that exist or are added.

**Two completely different backends — different languages:**
- `scrip-interp (C)` column: what `sm_interp.c` does in C when it dispatches
  this op. Calls C RT functions from `sil_macros.h` / `snobol4.c` / `argval.c`.
- `x86 emitter` column: the **x86 assembly instructions** that `emit_x64.c`
  writes into the code buffer when it sees this SM op. `call lexcmp` here means
  the emitter writes the bytes for an x86 `call` instruction targeting the
  `lexcmp` runtime symbol — not a C function call. `jmp [rax]` means the emitter
  writes an indirect-jump encoding. These are assembly mnemonics, not C.

| SM Instruction | SIL Origin | scrip-interp (C) | x86 emitter (asm) | Status |
|----------------|------------|------------------|-------------|--------|
| `SM_PUSH_LIT_S` | `PUSH` literal | push string descr | `mov`+`call push_str` | DONE |
| `SM_PUSH_LIT_I` | `PUSH` integer | push int descr | `mov`+`call push_int` | DONE |
| `SM_PUSH_LIT_F` | `PUSH` real | push real descr | `mov`+`call push_real` | DONE |
| `SM_PUSH_NULL` | `MOVD d,NULVCL` | push null descr | `call push_null` | DONE |
| `SM_PUSH_VAR` | `ARGVAL`/`GETDC` | `NV_GET_fn(name)` | `call NV_GET_fn` | DONE |
| `SM_STORE_VAR` | `PUTDC`/`ASGN` | `NV_SET_fn(name,val)` | `call NV_SET_fn` | DONE |
| `SM_POP` | `POP` | discard top | `sub rsp,DESCR` | DONE |
| `SM_ADD` | `SUM` | `add_fn(a,b)` | `call add_fn` | DONE |
| `SM_SUB` | `SUBTRT` | `sub_fn(a,b)` | `call sub_fn` | DONE |
| `SM_MUL` | `MULT` | `mul_fn(a,b)` | `call mul_fn` | DONE |
| `SM_DIV` | `DIVIDE` | `div_fn(a,b)` | `call div_fn` | DONE |
| `SM_EXP` | `EXREAL` | `exp_fn(a,b)` | `call exp_fn` | DONE |
| `SM_NEG` | `MNSINT`/`MNREAL` | `neg_fn(a)` | `call neg_fn` | DONE |
| `SM_CONCAT` | `APDSP` | `concat_fn(a,b)` | `call concat_fn` | DONE |
| `SM_JUMP` | `BRANCH` | `pc = target` | `jmp target` | DONE |
| `SM_JUMP_S` | `BRANCH` on success | `if(ok) pc=target` | `test/jnz` | DONE |
| `SM_JUMP_F` | `BRANCH` on failure | `if(!ok) pc=target` | `test/jz` | DONE |
| `SM_LABEL` | label def | label table entry | label: | DONE |
| `SM_HALT` | `BRANCH END` | `return` | `ret` | DONE |
| `SM_CALL` | `RCALL`/`INVOKE` | `INVOKE_fn(name,args)` | `call invoke_fn` | DONE |
| `SM_RETURN` | `RRTURN ,6` | longjmp RETURN | `ret`+exit6 | DONE |
| `SM_FRETURN` | `RRTURN ,4` | longjmp FRETURN | `ret`+exit4 | DONE |
| `SM_DEFINE` | `DEFINE` call | `register_fn()` | `call register_fn` | DONE |
| `SM_PAT_*` (21 ops) | pattern procs | `bb_build()` | `call bb_build_*` | DONE |
| `SM_EXEC_STMT` | `SCAN`/BB-DRIVER | `stmt_exec_dyn()` | `call stmt_exec_dyn` | DONE |
| **`SM_JUMP_INDIR`** | `BRANIC d,0` | `pc=(SM_Instr*)d.ptr` | `jmp [rax]` | **ADD** |
| **`SM_SELBRA`** | `SELBRA d,table` | `goto table[d.ival]` | `jmp [table+rax*8]` | **ADD** |
| **`SM_STATE_PUSH`** | `PUSH (OCBSCL…)` + `SPUSH` | memcpy regs to save-stack | `call state_push` | **ADD** |
| **`SM_STATE_POP`** | `POP (…)` + `SPOP` | memcpy from save-stack | `call state_pop` | **ADD** |
| **`SM_INCR`** | `INCRA d,n` | `d += n` (inline) | `add rax,n` | **ADD** |
| **`SM_DECR`** | `DECRA d,n` | `d -= n` (inline) | `sub rax,n` | **ADD** |
| **`SM_ACOMP`** | `ACOMP d1,d2` | `cmp_int(a,b)→-1/0/1` | `cmp rax,rbx` | **ADD** |
| **`SM_RCOMP`** | `RCOMP d1,d2` | `cmp_real(a,b)→-1/0/1` | `ucomisd` | **ADD** |
| **`SM_LCOMP`** | `LEXCMP sp1,sp2` | `lexcmp(a,b)→-1/0/1` | `call lexcmp` | **ADD** |
| **`SM_TRIM`** | `TRIMSP sp1,sp2` | `trimsp(sp1,sp2)` | `call trimsp` | **ADD** |
| **`SM_SPCINT`** | `SPCINT d,sp,f` | `spcint(d,sp)` + branch | `call spcint`+`jz f` | **ADD** |
| **`SM_SPREAL`** | `SPREAL d,sp,f` | `spreal(d,sp)` + branch | `call spreal`+`jz f` | **ADD** |

**12 new SM instructions. Additive — no existing SM_Instr layout change.**

---

## The Two-Axis Master Table — RT Functions (sil_macros.h + RT files)

Functions that exist only in C, called from scrip-interp and SM dispatch — not SM instructions.

| C Function | SIL Origin | File | Used by SM? | RT milestone |
|-----------|-----------|------|:---:|------|
| `TESTF(d,T)` macro | `TESTF` | `sil_macros.h` | dispatch only | now |
| `VEQLC(d,T)` macro | `VEQLC` | `sil_macros.h` | dispatch only | now |
| `DEQL(a,b)` macro | `DEQL` | `sil_macros.h` | dispatch only | now |
| `AEQLC(d,v)` macro | `AEQLC` | `sil_macros.h` | dispatch only | now |
| `IS_INT/REAL/STR/PAT/…` | type shorthands | `sil_macros.h` | dispatch only | now |
| `INCRA(d,n)` / `DECRA(d,n)` | `INCRA`/`DECRA` | `sil_macros.h` | `SM_INCR`/`SM_DECR` | now |
| `SPCINT_fn(d,sp)` | `SPCINT` | `argval.c` | `SM_SPCINT` dispatch | RUNTIME-2 |
| `SPREAL_fn(d,sp)` | `SPREAL` | `argval.c` | `SM_SPREAL` dispatch | RUNTIME-2 |
| `REALST_fn(sp,d)` | `REALST` | `argval.c` | via `SM_CALL` | RUNTIME-2 |
| `INTSP_fn(sp,d)` | `INTSP` / `INTSPC` | `argval.c` | via `SM_CALL` | RUNTIME-2 |
| `TRIM_fn(sp,sp)` | `TRIMSP` | `snobol4.c` | `SM_TRIM` dispatch | now |
| `LCOMP_fn(sp,sp)` | `LEXCMP` | `snobol4.c` | `SM_LCOMP` dispatch | now |
| `INVOKE_fn(name,args,n)` | `INVOKE` | `invoke.c` | `SM_CALL` dispatch | RUNTIME-1 |
| `ARGVAL_fn(d)` | `ARGVAL` | `argval.c` | SM arg fetch | RUNTIME-1 |
| `VARVAL_fn(d)` | `VARVAL` | `argval.c` | `SM_PUSH_VAR` coerce | RUNTIME-2 |
| `INTVAL_fn(d)` | `INTVAL` | `argval.c` | `SM_PUSH_VAR`→INT | RUNTIME-2 |
| `PATVAL_fn(d)` | `PATVAL` | `argval.c` | `SM_PAT_DEREF` | RUNTIME-2 |
| `VARVUP_fn(d)` | `VARVUP` | `argval.c` | `SM_CALL "VARVUP"` | RUNTIME-2 |
| `NAME_fn(varname)` | `NAME` | `snobol4.c` | `SM_CALL ".X"` | RUNTIME-3 |
| `ASGNIC_fn(kw,val)` | `ASGNIC` | `snobol4.c` | `SM_STORE_VAR` DT_K | RUNTIME-3 |
| `NAM_push/commit/discard` | `NMD` | `nmd.c` | `SM_EXEC_STMT` | RUNTIME-4 |
| `ASGN_fn(name,val)` | `ASGN` | `snobol4.c` | `SM_STORE_VAR` hook | RUNTIME-5 |
| `EXPVAL_fn(d)` | `EXPVAL` | `eval_code.c` | `SM_STATE_PUSH/POP` | RUNTIME-6 |
| `EXPEVL_fn(d)` | `EXPEVL` | `eval_code.c` | via `SM_CALL` | RUNTIME-6 |
| `CONVE_fn(str_d)` | `CONVE` | `snobol4.c` | via `SM_CALL` | RUNTIME-7 |
| `CODE_fn(args,n)` | `CODER` | `snobol4.c` | via `SM_CALL "CODE"` | RUNTIME-7 |
| `CONVERT_fn(args,n)` | `CNVRT` | `snobol4.c` | via `SM_CALL "CONVERT"` | RUNTIME-7 |
| `EVAL_fn(args,n)` | `EVAL` | `snobol4.c` | via `SM_CALL "EVAL"` | RUNTIME-8 |
| `state_push()`/`state_pop()` | `ISTACKPUSH` | `eval_code.c` | `SM_STATE_PUSH/POP` | RUNTIME-6 |

---

## sil_macros.h — Complete Design

Create `src/runtime/snobol4/sil_macros.h`. This is the **RT axis** header.
The **SM axis** changes are in `sm_interp.c` enum + dispatch (RUNTIME-9).

```c
/*
 * sil_macros.h — C translations of SIL macro instructions
 *
 * Axis 1 (scrip-interp / RT functions):
 *   Used by snobol4.c, argval.c, invoke.c, nmd.c, eval_code.c, stmt_exec.c
 *
 * Axis 2 (SM_Program dispatch):
 *   SM_INCR/SM_DECR dispatch calls INCRA/DECRA defined here.
 *   SM_ACOMP/SM_RCOMP/SM_LCOMP dispatch calls ACOMP/RCOMP/LCOMP.
 *   SM_TRIM/SM_SPCINT/SM_SPREAL dispatch calls TRIM_fn/SPCINT_fn/SPREAL_fn.
 *   SM_STATE_PUSH/POP dispatch calls state_push()/state_pop().
 *
 * Authors: Lon Jones Cherryholmes · Claude Sonnet 4.6
 * Date: 2026-04-05
 */
#ifndef SIL_MACROS_H
#define SIL_MACROS_H

#include "snobol4.h"   /* DESCR_t, DT_* constants */

/* ── Group 1: Descriptor field access ── */
#define GETDC(d, base, off)    ((d) = *((DESCR_t*)(base) + (off)/sizeof(DESCR_t)))
#define PUTDC(base, off, d)    (*((DESCR_t*)(base) + (off)/sizeof(DESCR_t)) = (d))
#define MOVD(dst, src)         ((dst) = (src))
#define MOVV(dst, src)         ((dst).v = (src).v)
#define MOVA(dst, src)         ((dst).ptr = (src).ptr)
#define SETAC(d, val)          ((d).ptr = (void*)(intptr_t)(val))
#define SETAV(d, src)          ((d).ptr = (void*)(intptr_t)(src).v)

/* ── Group 2: Type tests — scrip-interp RT axis ── */
#define TESTF(d, T)            ((d).f & (T))
#define IS_FNC(d)              TESTF((d), FNC)
#define VEQLC(d, T)            ((d).v == (T))
#define DEQL(a, b)             ((a).v == (b).v && (a).ptr == (b).ptr)
#define AEQLC(d, val)          ((intptr_t)(d).ptr == (intptr_t)(val))
#define AEQL(a, b)             ((a).ptr == (b).ptr)
#define SAME_TYPE(a, b)        ((a).v == (b).v)

/* Type shorthands — use DT_* constants from snobol4.h */
#define IS_INT(d)    ((d).v == DT_I)
#define IS_REAL(d)   ((d).v == DT_R)
#define IS_STR(d)    ((d).v == DT_S || (d).v == DT_SNUL)
#define IS_PAT(d)    ((d).v == DT_P)
#define IS_NAME(d)   ((d).v == DT_N)
#define IS_KW(d)     ((d).v == DT_K)
#define IS_EXPR(d)   ((d).v == DT_E)
#define IS_CODE(d)   ((d).v == DT_C)
#define IS_ARR(d)    ((d).v == DT_A)
#define IS_TBL(d)    ((d).v == DT_T)

/* ── Group 2: Comparison — both RT and SM dispatch axis ── */
/* ACOMP: returns -1/0/1 like strcmp; SM_ACOMP dispatches to this */
static inline int ACOMP(DESCR_t a, DESCR_t b) {
    intptr_t la = (intptr_t)a.ptr, lb = (intptr_t)b.ptr;
    return (la > lb) - (la < lb);
}
/* ACOMPC: compare descriptor address vs constant */
#define ACOMPC(d, val) \
    (((intptr_t)(d).ptr > (intptr_t)(val)) - ((intptr_t)(d).ptr < (intptr_t)(val)))

/* RCOMP: real compare; SM_RCOMP dispatches to this */
static inline int RCOMP(DESCR_t a, DESCR_t b) {
    return (a.dval > b.dval) - (a.dval < b.dval);
}

/* LCOMP: lexicographic string compare; SM_LCOMP dispatches to lexcmp() */
/* Declaration — defined in snobol4.c or string RT */
int LCOMP_fn(const char *sp1, int len1, const char *sp2, int len2);

/* ── Group 3: Address arithmetic — SM_INCR/SM_DECR dispatch here ── */
#define INCRA(d, n)   ((d) += (n))
#define DECRA(d, n)   ((d) -= (n))

/* ── Group 4: String/specifier coercions — SM_SPCINT/SPREAL dispatch here ── */
/* Returns 1 on success, 0 on failure (SM_SPCINT branches on 0) */
int SPCINT_fn(DESCR_t *out, const char *sp, int len);
int SPREAL_fn(DESCR_t *out, const char *sp, int len);
/* Format functions */
int REALST_fn(char *out, int maxlen, DESCR_t d);
int INTSP_fn(char *out, int maxlen, DESCR_t d);
/* SM_TRIM dispatches to TRIM_fn */
void TRIM_fn(const char *in, int inlen, const char **out, int *outlen);

/* ── Group 5: State save/restore — SM_STATE_PUSH/POP dispatch here ── */
/* For EXPVAL (RUNTIME-6): save/restore full interpreter register file */
void state_push(void);   /* ISTACKPUSH — push OCBSCL,OCICL,… */
void state_pop(void);    /* restore from state stack */

/* ── Descriptor null/fail sentinels ── */
/* FAILDESCR: the canonical failure descriptor (DT_FAIL type) */
extern DESCR_t FAILDESCR;
extern DESCR_t NULLDESCR;

#endif /* SIL_MACROS_H */
```

---

## Relationship to RT Milestones (updated)

| RT Milestone | Uses (scrip-interp axis) | Uses (SM axis) |
|-------------|--------------------------|----------------|
| RUNTIME-1 INVOKE | `TESTF`, `VEQLC`, `BRANIC`→`INVOKE_fn` | `SM_CALL` dispatches `INVOKE_fn` |
| RUNTIME-2 VARVAL/INTVAL/PATVAL | `SPCINT_fn`, `SPREAL_fn`, `INTRL`, `RLINT`, `LOCSP`, `GETLG` | `SM_SPCINT`, `SM_SPREAL`, `SM_PUSH_VAR` coerce |
| RUNTIME-3 NAME/KEYWORD | `VEQLC` DT_K, `GETDC`/`PUTDC`, `NAME_fn` | `SM_STORE_VAR` DT_K path, `SM_CALL ".X"` |
| RUNTIME-4 NMD | `GETLG`, `ACOMP`, `GETSPC`, `PUTDC`, `SPCINT_fn` | `SM_EXEC_STMT` calls `NAM_commit`/`NAM_discard` |
| RUNTIME-5 ASGN | `TESTF`, `VEQLC`, `PUTDC`, `AEQLC` trace check | `SM_STORE_VAR` extended with output/trace hooks |
| RUNTIME-6 EXPVAL | `SM_STATE_PUSH/POP`, `SPUSH`/`SPOP` | `SM_STATE_PUSH` + `SM_STATE_POP` instructions |
| RUNTIME-7 CONVE/CODER | `SPCINT_fn`, `SPREAL_fn`, `LOCSP`, `GETLG` | `SM_CALL "CODE"`, `SM_CALL "CONVERT"` |
| RUNTIME-8 EVAL | `VEQLC` dispatch, `SPCINT_fn`, `SPREAL_fn`, `CONVE_fn`, `EXPVAL_fn` | `SM_CALL "EVAL"` → `SM_SPCINT`/`SM_SPREAL` inline |
| RUNTIME-9 INTERP | `INCRA`/`DECRA`, `TESTF`, `BRANIC`, `SELBRA`, `ACOMP`/`RCOMP` | ALL SM instructions — `sm_interp.c` dispatch loop |

---

## Actions Required (Priority Order)

### Now (this session)
1. **Create `sil_macros.h`** — the header above. Verified against `macros.h`.
2. **Update SCRIP-SM.md** — add 12 new SM ops to the instruction table.
3. **Fix PLS** — `register_fn("PLS", _b_pls, 1, 1)` — unary `+X` is NOT identity.

### Per RT Milestone
Each RT-N reads the corresponding SIL proc from `v311.sil`, implements in C
using `sil_macros.h` type tests and field accessors, registers in INVOKE table.

### RUNTIME-9 — sm_interp.c (The Architecture Target)
When `sm_interp.c` is written, every SM instruction in the master table above
gets a dispatch case. The 12 new SM ops each call the corresponding RT function
defined in `sil_macros.h`. The emitter maps each SM op to native code.

---

## Summary — Counts by Axis

| Group | Count | scrip-interp axis | SM_Program axis |
|-------|-------|:-:|:-:|
| Descriptor access macros | 13 | `sil_macros.h` C macros | — |
| Type test / compare | 16 | `sil_macros.h` + 3 SM ops | `SM_ACOMP`, `SM_RCOMP`, `SM_LCOMP` |
| Address arithmetic | 2 inline + rest RT | `sil_macros.h` INCRA/DECRA | `SM_INCR`, `SM_DECR` |
| String / specifier | 21 RT functions | `argval.c`, `snobol4.c` | `SM_TRIM`, `SM_SPCINT`, `SM_SPREAL` |
| Control flow | 12 | goto/longjmp/call | `SM_JUMP_INDIR`, `SM_SELBRA`, `SM_STATE_PUSH/POP` |
| Pattern building | 21 | bb_build() | `SM_PAT_*` (DONE) |
| Byrd box construction | 15 | bb_*.c (DONE) | via `SM_EXEC_STMT` |
| Named builtins | ~50 | RT functions via INVOKE | via `SM_CALL` |
| SNOBOL4B blocks | ~50 | SKIP | SKIP |
| Compiler internals | ~25 | SKIP | SKIP |

**Total useful: ~120 of 211 procedures**
**SM_Program instructions: 12 new + 36 existing = 48 total**
**RT-only functions: ~70 (sil_macros.h + argval.c + invoke.c + nmd.c + snobol4.c extensions)**

---

*MILESTONE-RT-SIL-MACROS.md — revised sprint 99, 2026-04-05*
*Key addition: dual-axis table (scrip-interp vs SM_Program) for every macro.*
*C translations verified against csnobol4 `include/macros.h` and generated `snobol4.c`.*
