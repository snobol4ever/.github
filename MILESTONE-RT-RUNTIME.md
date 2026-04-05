# MILESTONE-RT-RUNTIME.md — SIL-Faithful Runtime Subsystems

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Session:** SNOBOL4 × x86, sprint 95+
**Status:** ACTIVE — RT-1 through RT-9 queued

---

## Governing Principle

Everything outside lex, parse, and pattern match (Byrd boxes) must
be **named and behave identically to the SIL** (`v311.sil`, CSNOBOL4 3.3.3).
The SIL procedure names become C function names. The SIL logic
becomes the C logic. No invention — faithful translation.

Covered by this milestone chain:
- `ARGVAL`, `VARVAL`, `INTVAL`, `PATVAL`, `EXPVAL` — typed argument eval
- `INVOKE` — universal function dispatch
- `NAME` / `ASGN` — NAME type and assignment with all hooks
- `NMD` / naming list — conditional assignment stack
- `EXPVAL` / `EXPEVL` — EXPRESSION type execution (save/restore system state)
- `CONVE` / `CODER` / `CNVRT` — compile-to-EXPRESSION, CODE(), CONVERT()
- `EVAL` builtin — string → expression evaluation
- `INTERP` / `INIT` / `GOTO` / `GOTL` / `GOTG` — SM_Program dispatch loop

## Invariant — Green Throughout

**Baseline (sprint 95, one4all `5c1a1d8`):**
```
PASS=177  FAIL=1  (178 total)   [expr_eval — needs EVAL+NRETURN]
```

Every RT commit must hold PASS ≥ 177. The floor never drops.
Run after every change:
```bash
cd /home/claude/one4all && bash test/run_interp_broad.sh
```

---

## Strategy — Additive Shim Replacement

`scrip-interp.c` stays buildable and passing after every commit.
Each milestone replaces exactly one internal dispatch point with
the SIL-faithful version. No big-bang rewrites.

| What gets replaced | Where in code | RT milestone |
|--------------------|--------------|-------------|
| `call_user_function()` if/else dispatch | scrip-interp.c | RT-1 |
| Type coercions inside `interp_eval()` | scrip-interp.c | RT-2 |
| `interp_eval_ref()` + K-type in NV_SET | scrip-interp.c + snobol4.c | RT-3 |
| `capture_t` array in stmt_exec.c | stmt_exec.c | RT-4 |
| `NV_SET_fn` — add output/trace hooks | snobol4.c | RT-5 |
| `eval_expr()` stub in eval_code.c | eval_code.c | RT-6 |
| `CODE()` / `CONVERT()` builtins | snobol4.c | RT-7 |
| `EVAL_fn` stub | snobol4.c | RT-8 |
| tree-walk `execute_program()` | scrip-interp.c → sm_interp.c | RT-9 |

---

## RT-1 — INVOKE Dispatch Table

**SIL procs:** `INVOKE`, `INVK1`, `INVK2`, `ARGVAL`
**File:** `src/runtime/snobol4/invoke.c` (new) + hook into `snobol4.c`
**Gate:** PASS ≥ 177, all existing tests unaffected

### What SIL does

```
INVOKE: pop function index (INCL)
        get procedure descriptor XPTR from INCL[0]
        if arg count matches FNC flag → BRANIC (branch indirect)
        else if FNC flag set → variable-arg: branch anyway
```

`ARGVAL`: fetch next descriptor from object code array (OCBSCL+OCICL),
check FNC bit → if set call INVOKE, else get value from name slot,
handle &INPUT association.

### What we have

`call_user_function()` in scrip-interp.c: a linear if/else over
hardcoded builtin names, then a search through a user-function list.
No FNC-bit model. No descriptor-keyed dispatch table.

### What to build

```c
/* invoke.c */

/* Function descriptor — mirrors SIL FBLKSZ block */
typedef struct {
    const char *name;
    int         nargs;       /* -1 = variable */
    DESCR_t   (*fn)(DESCR_t *args, int nargs);
} FuncDesc_t;

/* Global function table (builtins + user-defined) */
DESCR_t INVOKE_fn(const char *name, DESCR_t *args, int nargs);

/* ARGVAL: evaluate next argument off IR (tree-walk phase) */
DESCR_t ARGVAL_fn(EXPR_t *arg);
```

Replace the body of `call_user_function()` with a call to `INVOKE_fn`.
All builtin registrations move into `invoke.c`'s init table.
User `DEFINE` registers into the same table.

### Corpus gate

expr_eval needs NRETURN+EVAL (RT-6/RT-8), not RT-1.
Gate: no regressions. PASS stays 177.

---

## RT-2 — VARVAL / INTVAL / PATVAL Typed Argument Evaluators

**SIL procs:** `VARVAL`, `INTVAL`, `PATVAL`, `VARVUP`, `XYARGS`
**File:** `src/runtime/snobol4/argval.c` (new)
**Gate:** PASS ≥ 177

### What SIL does

Each evaluator: fetch descriptor → check FNC (call INVOKE if so) →
check &INPUT association → get value from name slot → coerce to
required type (STRING / INTEGER / PATTERN).

```
VARVAL: → STRING (coerce INTEGER via GENVIX, reject others)
INTVAL: → INTEGER (coerce STRING via SPCINT, coerce REAL via RLINT)
PATVAL: → PATTERN (coerce STRING→bb_lit, EXPRESSION→EXPVAL, REAL→STRING→bb_lit)
VARVUP: → uppercase STRING (VARVAL + case-fold if &CASE set)
```

### What we have

Ad-hoc coercions scattered through `interp_eval()` cases. No unified
typed-evaluator pattern. `_expr_is_pat()` heuristic instead of type-dispatch.

### What to build

```c
/* argval.c */
DESCR_t VARVAL_fn(DESCR_t d);   /* → STRING or FAIL */
DESCR_t INTVAL_fn(DESCR_t d);   /* → INTEGER or FAIL */
DESCR_t PATVAL_fn(DESCR_t d);   /* → PATTERN (DT_P) or FAIL */
DESCR_t VARVUP_fn(DESCR_t d);   /* → uppercase STRING or FAIL */
```

Thread these through `interp_eval()` at the points where type coercion
currently happens ad-hoc. The tree-walker stays; coercion logic moves
into named functions matching SIL names.

---

## RT-3 — NAME Type + Keyword Names (K)

**SIL procs:** `NAME` (`.X`), `ASGNV`, `ASGNIC`, type K dispatch
**Files:** `src/runtime/snobol4/snobol4.c`, `scrip-interp.c`
**Gate:** PASS ≥ 177, NAME tests added to corpus

### What SIL does

`.X` → `NAME` proc: fetch descriptor, test FNC bit, call INVOKE
if so, return N-typed descriptor pointing at variable's storage slot.

Type K (keyword): `ASGNIC` routes keyword assignment through `INTVAL`
(keyword values are always INTEGER). `NV_GET`/`NV_SET` for K-type
variables reads/writes the keyword global directly (e.g. `&TRIM`,
`&ANCHOR`, `&STLIMIT`).

### What we have

`interp_eval_ref()` returns a raw `DESCR_t*` C pointer. Works for
simple E_VAR cases. Completely ignores K (keyword) type. No DT_N
descriptor returned — just a pointer that leaks through the abstraction.

`NAMEPTR(dp_)` macro exists in snobol4.h but is not used by the
name-return path.

### What to build

```c
/* In snobol4.c */

/* NAME_fn: .X — return DT_N descriptor for variable name */
/* Mirrors SIL NAME proc */
DESCR_t NAME_fn(const char *varname);

/* ASGNIC_fn: keyword assignment — route through INTVAL */
int ASGNIC_fn(const char *kw_name, DESCR_t val);

/* Extend NV_GET_fn / NV_SET_fn to handle DT_K slot dispatch */
/* K-type names map to keyword globals: &TRIM, &ANCHOR, etc. */
```

Replace `interp_eval_ref()` with calls to `NAME_fn` where `.X` is
needed. Replace raw pointer returns with `DT_N` descriptors.
`ASGN` (RT-5) then dereferences DT_N via `NAMEPTR`.

---

## RT-4 — Conditional Assignment Stack (NMD / Naming List)

**SIL procs:** `NMD`, `NMD1`–`NMD5`, `NMDIC`, `NAMEXN`
**SIL globals:** `NAMICL`, `NHEDCL`, `PDLPTR`, `PDLHED`, `NBSPTR`
**File:** `src/runtime/dyn/stmt_exec.c`, new `src/runtime/snobol4/nmd.c`
**Gate:** PASS ≥ 177, `.VAR` capture tests pass

### What SIL does

The naming list is a LIFO buffer (`NBSPTR` + `NAMICL` offset).
Each `.VAR` conditional assignment during a pattern match pushes
`(specifier, variable_descriptor)` pairs onto this list.

On **pattern success**: `NMD` walks the list from `NHEDCL` to `NAMICL`,
assigns each captured substring to its variable. Handles:
- Normal variable (DT_S target): `GENVAR` + `PUTDC`
- Keyword variable (DT_K target): `NMDIC` → `SPCINT` (integer coerce)
- EXPRESSION variable (DT_E target): `NAMEXN` → `EXPEVL`

On **pattern failure**: the naming list is discarded by restoring
`NAMICL` to `NHEDCL` (nothing was committed).

`PDLPTR` / `PDLHED` is the **pattern history list** — backtrack state
for `ARBNO`, `BAL`, etc. Separate from the naming list.

### What we have

`capture_t` array in `stmt_exec.c` collects `(varname, substring)`
pairs. On success, iterates and calls `NV_SET_fn`. This is the right
shape but:
- No LIFO framing per-statement (no NHEDCL save/restore)
- No keyword coercion path (NMDIC)
- No EXPRESSION variable path (NAMEXN)
- Not re-entrant (EXPVAL inside NMD can recurse)

### What to build

```c
/* nmd.c — naming list (SIL §NMD) */

/* Thread-local (or global) naming list state */
typedef struct {
    const char *varname;   /* target variable */
    int         dt;        /* DT_S / DT_K / DT_E */
    const char *substr;    /* matched substring */
    int         slen;
} NamEntry_t;

#define NAM_MAX 256
static NamEntry_t nam_buf[NAM_MAX];
static int        nam_head = 0;   /* NHEDCL */
static int        nam_top  = 0;   /* NAMICL */

void  NAM_push(const char *var, int dt, const char *s, int len); /* .VAR hit */
int   NAM_save(void);                    /* save NHEDCL → returns cookie */
void  NAM_commit(int cookie);            /* NMD: assign all since cookie */
void  NAM_discard(int cookie);           /* on failure: restore to cookie */
```

Wire `NAM_push` into the bb_capture box (replaces current `capture_t`).
Wire `NAM_commit` / `NAM_discard` into `stmt_exec_dyn` at the S/F branch.

---

## RT-5 — ASGN with &OUTPUT Association + TRACE + Keyword Assignment

**SIL procs:** `ASGN`, `ASGNV`, `ASGNVV`, `ASGNVP`, `ASGNC`, `ASGNIC`
**File:** `src/runtime/snobol4/snobol4.c` — extend `NV_SET_fn`
**Gate:** PASS ≥ 177, OUTPUT-association test added

### What SIL does

```
ASGN:
  1. fetch subject descriptor (may be FNC → INVOKE)
  2. check K type → route to ASGNIC (keyword assignment via INTVAL)
  3. fetch value descriptor (may be FNC → INVOKE)
  4. check &INPUT association on value variable
  5. PUTDC: write value into subject's DESCR slot
  6. check &OUTPUT → if association exists, call PUTOUT
  7. check &TRACE → if VALUE trace on subject, call TRPHND
  8. return value (for embedded assignment X = (A = B) )
```

### What we have

`NV_SET_fn(name, val)`: plain hash-table store. No output association,
no trace, no keyword routing, no embedded-assignment return value.

### What to build

Extend `NV_SET_fn` signature to return `DESCR_t` (the assigned value,
for embedded assignment). Add hook points:

```c
/* snobol4.c — extend NV_SET_fn */
DESCR_t NV_SET_fn(const char *name, DESCR_t val);
/*  → checks OUTPUT assoc table (outatl)
    → checks TRACE value table (tvall)  [&TRACE]
    → keyword names routed to kw_set()
    → returns val (for embedded assignment)
*/
```

Output association table (`outatl`) and trace association table (`tvall`)
are initially empty. The hooks are wired but inert until
`OUTPUT` and `TRACE` builtins populate them (later milestone).

---

## RT-6 — EXPVAL / EXPEVL — EXPRESSION Type Execution

**SIL procs:** `EXPVAL`, `EXPEVL`, `EXPVC`, `EXPV1`–`EXPV11`
**File:** `src/runtime/dyn/eval_code.c` — replace stub `eval_expr()`
**Gate:** PASS ≥ 177, EXPRESSION type tests added

### What SIL does

`EXPVAL` saves the **entire system state** before evaluating an
EXPRESSION-typed value:
```
Push: OCBSCL, OCICL, PATBCL, PATICL, WPTR, XCL, YCL, TCL
      MAXLEN, LENFCL, PDLPTR, PDLHED, NAMICL, NHEDCL
      specifiers: HEADSP, TSP, TXSP, XSP
```
Sets new `OCBSCL` = the EXPRESSION's code block.
Calls `INVOKE` to execute each instruction.
On exit (success or failure): restores all saved state.

`EXPEVL` is the entry for evaluating an EXPRESSION and returning
**by name** (the variable reference, not the value). Used by `NMD`
when target is DT_E (NAMEXN path).

`EXPVC`: when the code block's first descriptor has FNC bit set,
call INVOKE (function call within expression evaluation).

### What we have

`eval_expr(const char *src)` in eval_code.c: re-parses a string,
tree-walks the result. No save/restore of system state. No DT_E
descriptor execution. Returns a value but not re-entrant.

### What to build

```c
/* eval_code.c — replace eval_expr() */

/* System state snapshot for EXPVAL save/restore */
typedef struct {
    /* interpreter registers */
    int   ocbscl_base;   /* OCBSCL */
    int   ocicl_off;     /* OCICL */
    int   nam_head;      /* NHEDCL */
    int   nam_top;       /* NAMICL */
    int   pdl_head;      /* PDLHED */
    int   pdl_ptr;       /* PDLPTR */
    /* ... other saved state ... */
} SysState_t;

/* EXPVAL: execute a DT_E EXPRESSION, return value or FAIL */
DESCR_t EXPVAL_fn(DESCR_t expr_d);

/* EXPEVL: execute DT_E EXPRESSION, return by name */
DESCR_t EXPEVL_fn(DESCR_t expr_d);
```

The key correctness property: EXPVAL must be **fully re-entrant** —
an EXPRESSION can contain a call to EVAL() which calls EXPVAL again.
The save/restore stack must handle arbitrary nesting.

---

## RT-7 — CONVE / CODER / CNVRT — Compile to EXPRESSION and CODE

**SIL procs:** `CONVE`, `CONVEX`, `CODER`, `CNVRT` (= `CONVERT()`),
              `RECOM*` (recompile loop), `CONVR`, `CONVRI`, `CNVIV`,
              `CNVVI`, `CNVTA`, `ICNVTA`
**File:** `src/runtime/snobol4/snobol4.c` — `CODE_fn`, `CONVERT_fn`
**Gate:** PASS ≥ 177, CODE() + CONVERT() corpus tests pass

### What SIL does

`CODER` (= `CODE(S)`):
1. Evaluate arg as string via `VARVAL`
2. Set up compiler with string as input (`TEXTSP`)
3. Compile statements via `CMPILE` loop until string exhausted
4. Set type to C (CODE) on resulting block
5. Return CODE descriptor

`CONVE` (convert to EXPRESSION):
1. Same as CODE but compile a single expression via `EXPR`
2. Set type to E (EXPRESSION) on result
3. Return EXPRESSION descriptor

`CNVRT` (= `CONVERT(X, T)`):
Full type-conversion matrix:
```
S→I, S→R, I→S, I→R, R→S, R→I   (numeric conversions)
S→E  (string → expression via CONVE)
T→A  (table → array via CNVTA)
any→S  (via DTREP — data type representation string)
```

### What we have

`CODE()` stub returns NULVCL.
`CONVERT()` does only numeric conversions.
No `CONVE` — no compile-string-to-EXPRESSION path.
No table→array conversion.

### What to build

```c
/* snobol4.c */
DESCR_t CODE_fn(DESCR_t *args, int nargs);     /* CODE(S) → DT_C */
DESCR_t CONVE_fn(DESCR_t str_d);               /* string → DT_E */
DESCR_t CONVERT_fn(DESCR_t *args, int nargs);  /* CONVERT(X,T) full matrix */
```

`CODE_fn` and `CONVE_fn` call `sno_parse()` (existing) on the string,
wrap the resulting `Program*` in the appropriate DT_C / DT_E descriptor.

---

## RT-8 — EVAL() Builtin

**SIL proc:** `EVAL`, `EVAL1`
**File:** `src/runtime/snobol4/snobol4.c` — replace `EVAL_fn` stub
**Gate:** PASS = 178 (expr_eval finally passes), EVAL corpus tests pass

### What SIL does

```
EVAL(X):
  ARGVAL → get X
  if X is DT_E (EXPRESSION) → go directly to EXPVAL (EVAL1)
  if X is DT_I → return X (idempotent)
  if X is DT_R → return X (idempotent)
  if X is DT_S:
    if empty string → return X (idempotent)
    try SPCINT → return integer if succeeds
    try SPREAL → return real if succeeds
    CONVE: compile string to EXPRESSION
    → EXPVAL: execute it
```

### What we have

`EVAL_fn`: stub that calls `eval_expr(src)` — re-parses string,
tree-walks result. Misses idempotent cases, misses DT_E path,
misses numeric-string shortcuts.

### What to build

```c
/* snobol4.c — replace EVAL_fn body */
DESCR_t EVAL_fn(DESCR_t *args, int nargs) {
    DESCR_t x = ARGVAL_fn(args[0]);
    if (x.v == DT_E) return EXPVAL_fn(x);       /* EVAL1 */
    if (x.v == DT_I || x.v == DT_R) return x;   /* idempotent */
    if (x.v == DT_S) {
        if (IS_NULL_fn(x)) return x;             /* empty → idempotent */
        DESCR_t n = try_int(x);   if (n.v == DT_I) return n;
        DESCR_t r = try_real(x);  if (r.v == DT_R) return r;
        DESCR_t e = CONVE_fn(x);                 /* compile → DT_E */
        if (e.v == DT_FAIL) return FAILDESCR;
        return EXPVAL_fn(e);                     /* execute */
    }
    return FAILDESCR;
}
```

This is the milestone that makes `expr_eval` pass (PASS → 178).

---

## RT-9 — INTERP / INIT / GOTO / GOTL / GOTG — SM_Program Dispatch Loop

**SIL procs:** `INTERP`, `INTRP0`, `INIT`, `GOTO`, `GOTL`, `GOTG`, `BASE`
**File:** `src/driver/sm_interp.c` (new — does NOT modify scrip-interp.c)
**Gate:** SM_Program test suite passes; scrip-interp.c tree-walker untouched

### What SIL does

```
INTERP (core loop):
  INTRP0: OCICL += DESCR                 ; advance to next instruction
           XPTR = code[OCICL]            ; fetch descriptor
           if FNC bit set → INVOKE       ; dispatch function
           on INVOKE failure: OCICL = FRTNCL (failure offset)
                              FALCL++  (&STFCOUNT)
                              check &TRACE → TRPHND

INIT (statement header):
  update &LASTNO, &LASTFILE, &LASTLINE
  OCICL += DESCR × 3 (skip stmtno, lineno, filename)
  update &STNO, &LINE, &FILE, &STCOUNT
  check &STLIMIT → EXEX if exceeded
  check &TRACE → STNO/STCOUNT trace handlers

GOTO: fetch offset from code, set OCICL
GOTL: fetch label string, look up in label table,
      handle RETURN/FRETURN/NRETURN/ABORT/CONTINUE/SCONTINUE
GOTG: :<VAR> — get CODE descriptor, set OCBSCL+OCICL=0
```

### What we have

`execute_program()` in scrip-interp.c: tree-walks `STMT_t` linked list.
No `&STNO`/`&LINE` update. No `&STLIMIT` check. No `NRETURN` from
nested function calls (partial — known bug). No `ABORT`/`CONTINUE`
goto targets.

### What to build

`sm_interp.c`: a fresh file implementing the SM_Program dispatch loop
over `SM_Instr[]` (from SCRIP-SM.md). This is the component that
connects the RT-1 through RT-8 subsystems to the SM_Program instruction
set and retires the tree-walker permanently.

`scrip-interp.c` continues running on the tree-walker during this milestone.
`sm_interp.c` runs in parallel against the same corpus.
When `sm_interp` PASS ≥ scrip-interp PASS, the tree-walker is retired.

**This milestone is the architecture reset target from PLAN.md** —
SM_Program execution replaces tree-walking IR.

---

## Milestone Summary Table

| Milestone | SIL procs | New file(s) | Gate |
|-----------|-----------|-------------|------|
| **RT-1** | `INVOKE`, `INVK1/2`, `ARGVAL` | `invoke.c` | PASS ≥ 177 |
| **RT-2** | `VARVAL`, `INTVAL`, `PATVAL`, `VARVUP` | `argval.c` | PASS ≥ 177 |
| **RT-3** | `NAME`, `ASGNIC`, type K dispatch | extend `snobol4.c` | PASS ≥ 177 |
| **RT-4** | `NMD`, `NMD1-5`, `NMDIC`, `NAMEXN` | `nmd.c` | PASS ≥ 177 |
| **RT-5** | `ASGN`, `ASGNV`, `ASGNVV`, `ASGNVP` | extend `snobol4.c` | PASS ≥ 177 |
| **RT-6** | `EXPVAL`, `EXPEVL`, `EXPVC` | extend `eval_code.c` | PASS ≥ 177 |
| **RT-7** | `CONVE`, `CODER`, `CNVRT` | extend `snobol4.c` | PASS ≥ 177 |
| **RT-8** | `EVAL`, `EVAL1` | extend `snobol4.c` | **PASS = 178** |
| **RT-9** | `INTERP`, `INIT`, `GOTO`, `GOTL`, `GOTG` | `sm_interp.c` | PASS ≥ 178 via SM |

Dependencies: RT-3 → RT-4 → RT-5 (NAME before NMD before ASGN hooks).
RT-6 → RT-7 → RT-8 (EXPVAL before CONVE before EVAL).
RT-1 and RT-2 are independent — start with RT-1.
RT-9 depends on all prior milestones and SM-LOWER (see SCRIP-SM.md).

---

## SIL Reference Quick Index

All procedures in `/home/claude/snobol4-2.3.3/v311.sil`:

| Proc | Line | Description |
|------|------|-------------|
| `INVOKE` | 2669 | Universal function dispatcher |
| `ARGVAL` | 2683 | Evaluate one argument (untyped) |
| `EXPVAL` | 2702 | Execute EXPRESSION, save/restore state |
| `EXPEVL` | 2750 | Execute EXPRESSION, return by name |
| `EVAL` | 2754 | EVAL() builtin |
| `INTVAL` | 2769 | Evaluate argument as INTEGER |
| `PATVAL` | 2800 | Evaluate argument as PATTERN |
| `VARVAL` | 2836 | Evaluate argument as STRING |
| `VARVUP` | 2867 | Evaluate argument as uppercase STRING |
| `XYARGS` | 2890 | Evaluate argument pair |
| `INTERP` | 2651 | Core interpreter loop |
| `INIT` | 2608 | Statement initialization |
| `GOTO` | 2641 | Interpreter goto |
| `GOTL` | 2575 | Label goto (RETURN/FRETURN/etc.) |
| `GOTG` | 2559 | Direct goto :<VAR> |
| `BASE` | 2544 | Code basing |
| `NAME` | 6043 | .X — return NAME descriptor |
| `NMD` | 6055 | Commit conditional assignments |
| `ASGN` | 5832 | X = Y with all hooks |
| `CONVE` | 6534 | String → EXPRESSION |
| `CODER` | 6530 | String → CODE |
| `CNVRT` | 6457 | CONVERT(X,T) |

---

*MILESTONE-RT-RUNTIME.md — created sprint 95, 2026-04-04*
*Baseline: PASS=177 FAIL=1. Target: PASS=178 at RT-8, then SM_Program at RT-9.*
