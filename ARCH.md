# ARCH.md — Architecture Reference (L3)

Stable decisions. Updated only when architecture changes, not when sprints change.
For sprint status → TINY.md. For session history → SESSIONS_ARCHIVE.md.

---

## Core Execution Model — Statement IS a Byrd Box (Session 27 Eureka)

```
label:  subject  pattern  =replacement  :S(x)  :F(y)
          α          →          γ           γ      ω
```
- **α** — evaluate subject → initialize Σ (string), Δ (cursor=0)
- **pattern** — Byrd box proper: labeled gotos through match nodes
- **γ** — success: apply replacement, follow :S() goto
- **ω** — failure: follow :F() goto

**Hot path:** pure C labeled gotos. Zero overhead. No setjmp.
**Cold path:** `longjmp` for ABORT, FENCE bare, runtime errors ONLY.

---

## Byrd Box Layout (Session 16, permanent)

```
┌─────────────────────────┐
│  DATA: cursor, locals,  │
│        captures, ports  │
├─────────────────────────┤
│  CODE: α/β/γ/ω gotos   │
└─────────────────────────┘
Boxes in memory:
  DATA section: [ box0.data | box1.data | box2.data | ... ]
  TEXT section: [ box0.code | box1.code | box2.code | ... ]
```

---

## Four Techniques for *X (Byrd box instantiation)

### Technique 1 — Struct-passing (CURRENT — C target, for M-BEAUTY-FULL)

Each named pattern becomes a C function. ALL locals go in a typed struct —
declared before the first `goto` to satisfy C99 §6.8.6.1 (no jump over declarations).
Child frame for `*Y` is a POINTER field in the parent struct (size known at compile time).

```c
typedef struct pat_snoParse_t {
    int64_t  saved_7;               /* cursor saves */
    int      arbno_depth;
    int64_t  arbno_stack[64];       /* ARBNO depth stack */
    struct pat_snoCommand_t *snoCommand_z;  /* child frame pointer */
} pat_snoParse_t;

static SnoVal pat_snoParse(pat_snoParse_t **zz, int entry) {
    pat_snoParse_t *z = *zz;
    if (entry == 0) { z = *zz = calloc(1, sizeof(*z)); goto snoParse_alpha; }
    if (entry == 1) { goto snoParse_beta; }
    snoParse_alpha: ...Byrd box labeled gotos using z->field...
    snoParse_gamma: return matched_val;
    snoParse_omega: return FAIL_VAL;
}
```

`*snoCommand` inside snoParse emits `pat_snoCommand(&z->snoCommand_z, 0/1)`.
calloc on entry==0. beta dispatch on entry==1. Recursion: each call gets own struct.

### Technique 2 — mmap + memcpy + relocate (FUTURE — ASM/native, after M-BOOTSTRAP)

When `*X` fires at match time:
1. `memcpy(new_text, box_X.text_start, len)` — copy CODE section
2. `memcpy(new_data, box_X.data_start, len)` — copy DATA section (locals)
3. `relocate(new_text, delta)` — patch relative jumps + absolute DATA refs
4. Jump to `new_text[PROCEED]` — enter the copy

TEXT: PROTECTED (RX), mprotect→RWX during copy+relocate, back to RX after.
DATA: UNPROTECTED (RW), one copy per dynamic instance.
No heap. No GC. ~20 lines. LIFO discipline = discard copy on failure.
Two relocation cases: relative refs (add delta) + absolute DATA refs (patch to new copy).

### Technique 3 — Iota functions (concept only, revisit after M-BEAUTY-FULL)

Every labeled Byrd box block becomes its own tiny C function (purely for addressability).
Sequence wrapped in one outer C function. One flat concatenated struct for all locals.
Bridges Technique 1 and 2: each labeled block has an address → dynamic box = memcpy+relocate.

### Technique 4 — GCC &&label port table (concept only, nonstandard)

Entire named pattern stays in ONE C function. GCC `&&label` extension gives label addresses
as `void*`. Port table: `void *pat_X_ports[2] = {&&alpha, &&beta}`.
Caller dispatches: `goto *pat_X_ports[entry]`. Nonstandard — GCC/Clang only.

---

## Block Function Execution Model ("The New Plan", 2026-03-14)

Every SNOBOL4 statement → C function returning address of next block:
```c
typedef block_fn_t (*block_fn_t)(void);
block_fn_t pc = block_START;
while (pc) pc = pc();    /* the entire engine — one loop */
```

| Construct | Mechanism |
|-----------|-----------|
| `:(L42)` | return `block_L42` |
| `*X` static | call `block_X` directly (known at compile time) |
| `*X` dynamic | X holds a `block_fn_t` — call it directly |
| `EVAL(str)` | TCC compile str → degenerate stmt fn → call it, get value |
| `CODE(str)` | TCC compile str → block fn sequence → return entry block_fn_t |

Statements grouped into `block_L` by label reachability. New block at every labeled statement.
Flat concatenated locals struct per block — all stmt locals in one struct, allocated once.

## setjmp Model

| Feature | Status | Location |
|---------|--------|----------|
| Per-function setjmp | ✅ done | emit.c emit_fn() |
| push/pop_abort_handler macros | ✅ done | runtime_shim.h |
| Per-statement setjmp | ❌ todo | emit.c emit_stmt() |
| Glob-sequence optimization | ❌ todo | needs reachability pass |
| Non-Gimpel DEFINE special case | ❌ todo | emit.c emit_stmt() |

Glob-sequence: consecutive stmts in a DEFINE body with NO internal label targets
share ONE setjmp boundary. Stmts that ARE label targets start a new boundary.
Non-Gimpel DEFINE: bare `DEFINE(...)` appearing mid-program as executable statement
gets its OWN standalone setjmp guard — never merged into surrounding glob sequence.

---

## Bootstrap Strategy

Stage 0: C `sno2c` (exists). Stage 1: compile `sno2c.sno` via C `sno2c` → `sno2c_stage1`.
Stage 2: compile `sno2c.sno` via `sno2c_stage1` → `sno2c_stage2`.
Verification: diff output of stage1 vs stage2 on beauty.sno → **empty = M-BOOTSTRAP fires**.
C runtime stays C permanently (correct — GCC's runtime is also C).
Front-end (lex.c, parse.c, emit.c, emit_byrd.c, emit_cnode.c) moves to `sno2c.sno`.

## compiler.sno Strategy (Architecture B — bootstrap path)

`compiler.sno` = `beauty.sno` grammar + `compile(sno)` replacing `pp(sno)`.
Same parse tree, same Shift/Reduce machinery (proven by M-BEAUTY-FULL).
Final action emits C Byrd boxes instead of pretty-printed SNOBOL4.
One new function (`compile()`) walking the proven tree. Minimal delta.

Architecture A (alternative, post-bootstrap): sprinkle emit actions directly into pattern
alternations using `epsilon . *action(...)` — like iniParse assigns table entries inline.
Reference: `SNOBOL4-corpus/programs/inc/ini.sno`. Hard; pursue after M-BOOTSTRAP.

---

## Three-Column Generated C Format

```
Col 1  Label   chars 0..17    (4-space indent + label + ":" + padding)
Col 2  Stmt    chars 18..59   (C statement body)
Col 3  Goto    chars 60+      (goto target)
```
Macros: `PLG(label, goto)`, `PL(label, goto, stmt)`, `PS(goto, cond)`, `PG(goto)`.
Shared header `emit_pretty.h` — included by both `emit.c` and `emit_byrd.c`.
Applies to ALL generated C, not just pattern blocks. Replaces all raw `E(...)` calls.

## Save/Restore in DEFINE Functions

WRONG (current): C-local `var_get/var_set` preamble/postamble in `emit_fn()`.
RIGHT (target): α port saves caller locals into struct; γ/ω ports restore.
Byrd box form makes save/restore explicit in 3-column format. Prerequisite for M-COMPILED-SELF.

---

## SIL Naming Convention (Session 84–85, canonical)

Types: `DESCR_t`, `DTYPE_t`. Fields: `.v` (type tag), `.a` (address), `.f` (flags).
Values: `NULVCL`, `STRVAL(s)`, `INTVAL(i)`, `FAILDESCR`, `IS_FAIL_fn()`.
Vars: `NV_GET_fn` / `NV_SET_fn`. Functions: `APLY_fn`, `DEFINE_fn`, `CONC_fn`, `FNCEX_fn`.
Trees: `MAKE_TREE_fn`, `NPUSH_fn/NPOP_fn/NINC_fn/NDEC_fn`, `PUSH_fn/POP_fn/TOP_fn`.
Pattern codes: `XCHR` (lit), `XARBN` (arbno), `XNME` (cond assign `.`), `XDNME`/`XFNME` (imm `$`).
Expression IR: `E_MPY` (not E_MUL), `E_OR` (not E_ALT), `E_NAM` (not E_COND), `E_DOL`, `E_FNC`.

**Known bug:** `ARRAY_VAL` macro uses `.a` field, should be `.arr` — dormant until ARRAY_VAL called.
Fix: `snobol4.h:399` — one character change from `.a =` to `.arr =`.

**Intentional partial renames (not bugs):**
- `lpad_fn/rpad_fn/real_fn/string_fn` — lowercase, inconsistent (minor, fix later)
- `eq/ne/lt/le/gt/ge`, `add/sub/mul/divyde/powr/neg`, `ident/differ`, `to_int/to_real` — intentional (domain primitives)
- `pat_lit/pat_span/pat_arbno` etc. — `pat_` prefix intentional (pattern constructors)
