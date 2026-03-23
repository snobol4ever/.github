# FRONTEND-ICON.md — Tiny-ICON Frontend (L3)

Tiny-ICON is a frontend for snobol4x targeting the x64 ASM backend.
SNOBOL4 and Icon share a bloodline — Griswold invented both.
The Byrd Box IR is the bridge: same four ports (α/β/γ/ω), new Icon frontend
feeding the same TINY pipeline. Goal-directed generators map directly to Byrd boxes.

**Session trigger phrase:** `"I'm playing with ICON"`
**Session prefix:** `I` (e.g. I-1, I-2, I-3)
**Backend:** x64 ASM only — same NASM/ELF64 pipeline as SNOBOL4
**Location:** `src/frontend/icon/` in snobol4x

*Session state → this file §NOW. Backend → BACKEND-X64.md.*

---

## §NOW — Session State

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **ICON frontend** | `main` I-2 — M-ICON-CORPUS-R1 ✅ `1c299e3`; full Rung 1 pipeline; 6/6 PASS | `1c299e3` | M-ICON-PROC |

### Next session checklist (I-3)

```bash
git clone https://github.com/snobol4ever/snobol4x
git clone https://github.com/snobol4ever/.github
bash /home/claude/snobol4x/setup.sh
# Read FRONTEND-ICON.md §NOW — start at M-ICON-PROC emitter fix
```

**M-ICON-PROC: emitter fix (I-3 first task)**

Parser now correct — `icon_parse.c`:
- `proc->val.ival` = nparams
- `proc->children[1..nparams]` = param ICN_VAR nodes
- `proc->children[nparams+1..]` = body stmts
- `ICN_GLOBAL` node returned for `local` decls (children = local name ICN_VARs)

Emitter `icn_emit_file` (~line 695 emission loop) needs:
1. Read `np = (int)proc->val.ival`; register params into local table slots 0..np-1
2. Scan stmts for `ICN_GLOBAL` nodes; register their children as additional locals
3. Frame size = `8*(np + nlocals + 1)` rounded to 16
4. At proc entry after frame setup: call `icn_pop` np times (reverse slot order):
   ```c
   for (int pi = np-1; pi >= 0; pi--) {
       E(em,"    call    icn_pop\n");
       E(em,"    mov     [rbp%+d], rax\n", slot_offset(pi));
   }
   ```
5. Stmt loop: iterate `children[1+np..]`, skip `ICN_GLOBAL` nodes

**M-ICON-PROC acceptance criteria:**
Write `test/frontend/icon/corpus/rung02/`:
- `t01_add_proc.icn`: `procedure add(x,y)` called from main — tests param passing
- `t02_fact.icn`: recursive factorial — tests recursion + return
- `t03_locals.icn`: procedure with `local` vars — tests local frame slots

**M-ICON-SUSPEND (follows immediately):**
- `suspend E` = yield value, resume on β; needs saved resume address per activation
- For Rung 3: implement as a global resume-label slot (single active generator at a time)
- Write `test/frontend/icon/corpus/rung03/t01_gen.icn`

**Key files:**
- `src/frontend/icon/icon_emit.c` lines ~670-760 (`icn_emit_file` emission loop)
- `src/frontend/icon/icon_parse.c` — already correct, do not change

---


## Why Icon fits the Byrd Box model

Icon's goal-directed evaluation: every expression either succeeds (generating
zero or more values) or fails. Expressions suspend and resume like generators.
This maps exactly to α (proceed) / β (resume) / γ (succeed) / ω (fail).

JCON (Townsend + Proebsting, 1999) proved this: Icon → JVM via Byrd Box IR.
Proebsting's 1996 paper gives the exact four-port templates for every Icon
operator. Those templates are our emitter spec.

---

## Design Decisions

### Backend: x64 ASM (not C, not JVM)

The x64 ASM backend already has full arithmetic (`E_ADD/SUB/MPY/DIV`),
string ops (`CAT2_*` macros), function calls (`APPLY_FN_N`), and the
complete Byrd box macro library. Icon's expression evaluation maps directly
onto existing machinery. No new backend needed.

JCON source is kept as structural reference (especially `irgen.icn` for
four-port wiring patterns) but is not built or run.

### Explicit semicolons — no auto-insertion

Icon's standard lexer inserts semicolons automatically on newlines.
We reject this. Every expression sequence requires an explicit `;`.
This is a deliberate deviation: simpler lexer, explicit structure,
no hanging-continuation ambiguity. Icon source in the corpus is patched
to use explicit semicolons.

### Shared IR — reuse everything with exact semantics

| Icon concept | Shared IR node | Notes |
|---|---|---|
| Integer literal | `E_ILIT` | exact reuse |
| Real literal | `E_FLIT` | exact reuse |
| String literal | `E_QLIT` | exact reuse |
| Cset literal | `E_QLIT` + DT_CS tag | cset = typed string |
| Variable | `E_VART` | exact reuse |
| `+` `-` `*` `/` `%` `^` | `E_ADD/SUB/MPY/DIV/EXPOP` | exact reuse |
| Unary `-` | `E_MNS` | exact reuse |
| `\|\|` string concat | `E_CONC` | exact reuse |
| Function call | `E_FNC` | exact reuse |
| `upto(cs)` | `BREAK` Byrd box | semantic match |
| `many(cs)` | `SPAN` Byrd box | semantic match |
| cset membership | `ANY` Byrd box | semantic match |
| `\|` value alternation | new `E_ICN_ALT` | NOT `E_OR` (that is pattern alt) |
| `to` generator | new `E_TO` node | paper §4.4 template |
| `every`/`do` | new `E_EVERY` node | drives generator to exhaustion |
| `if`/`then`/`else` | new `E_ICN_IF` node | paper §4.5 indirect goto |
| `suspend` | new `E_SUSPEND` node | β port of enclosing call |
| `?` string scan | new `E_SCAN` node | explicit cursor threading |

New nodes added to `sno2c.h` `EKind` enum. SNOBOL4 frontend unaffected.

### `bounded` flag — deferred optimization

JCON threads a `bounded` flag through every IR node: when an expression
is in a "value needed" context (assignment RHS, argument), the resume/fail
ports are omitted entirely. This is the highest-value optimization but is
deferred until after correctness. All four ports emitted unconditionally
for now.

---

## Milestone Table

| ID | Trigger | Depends on | Status |
|----|---------|-----------|--------|
| **M-ICON-ORACLE** | `icont` + `iconx` built from icon-master; `every write(1 to 5);` → `1\n2\n3\n4\n5` confirmed; `icon-master/bin/icont` and `iconx` committed to path | — | ✅ `d364a14` |
| **M-ICON-LEX** | `icon_lex.c` tokenizes all Tier 0 tokens; `icon_lex_test.c` 100% pass | M-ICON-ORACLE | ✅ 108/108 I-2 |
| **M-ICON-PARSE-LIT** | Parser produces correct AST for all Proebsting §2 paper examples | M-ICON-LEX | ✅ 21/21 I-2 |
| **M-ICON-EMIT-LIT** | Byrd box for `ICN_INT` matches paper §4.1 exactly | M-ICON-PARSE-LIT | ✅ I-2 |
| **M-ICON-EMIT-TO** | `to` generator; `every write(1 to 5);` → `1..5` | M-ICON-EMIT-LIT | ✅ I-2 |
| **M-ICON-EMIT-ARITH** | `+` `*` `-` `/` binary ops via existing `E_ADD/MPY/SUB/DIV` | M-ICON-EMIT-TO | ✅ I-2 |
| **M-ICON-EMIT-REL** | `<` `>` `=` `~=` relational with goal-directed retry | M-ICON-EMIT-ARITH | ✅ I-2 |
| **M-ICON-EMIT-IF** | `if`/`then`/`else` with indirect goto `gate` temp (paper §4.5) | M-ICON-EMIT-REL | ✅ I-2 |
| **M-ICON-EMIT-EVERY** | `every E do E` drives generator to exhaustion | M-ICON-EMIT-IF | ✅ I-2 |
| **M-ICON-CORPUS-R1** | Rung 1: all paper examples pass; oracle = `icont`+`iconx` from icon-master | M-ICON-EMIT-EVERY | ✅ 6/6 I-2 |
| **M-ICON-PROC** | `procedure`/`end`, `local`, `return`, `fail`, call expressions | M-ICON-CORPUS-R1 | ❌ |
| **M-ICON-SUSPEND** | `suspend E` inside procedure = user-defined generator | M-ICON-PROC | ❌ |
| **M-ICON-CORPUS-R2** | Rung 2: arithmetic generators, relational filtering | M-ICON-SUSPEND | ❌ |
| **M-ICON-CORPUS-R3** | Rung 3: user procedures with return; user-defined generators | M-ICON-CORPUS-R2 | ❌ |
| **M-ICON-STRING** | `ICN_STR`, `\|\|` concat via `CAT2_*` macros | M-ICON-CORPUS-R3 | ❌ |
| **M-ICON-SCAN** | `E ? E` string scanning; explicit cursor threading | M-ICON-STRING | ❌ |
| **M-ICON-CSET** | Cset literals; `upto`→`BREAK`, `many`→`SPAN`, membership→`ANY` | M-ICON-SCAN | ❌ |
| **M-ICON-CORPUS-R4** | Rung 4: string operations and scanning | M-ICON-CSET | ❌ |

---

## Sprint I-1 Plan: Lexer + Parser

### Files to create

```
src/frontend/icon/
  icon_lex.h         — token kinds, Token, Lexer structs
  icon_lex.c         — hand-rolled lexer (no flex; no auto-semicolon)
  icon_lex_test.c    — unit tests: tokenize all paper examples
  icon_ast.h         — IcnKind enum + IcnNode struct
  icon_parse.h       — parser API
  icon_parse.c       — recursive-descent parser
  icon_parse_test.c  — unit tests: parse paper examples, verify AST shape
```

### Token set

```c
typedef enum {
    TK_EOF = 0,
    TK_INT, TK_REAL, TK_STRING, TK_CSET, TK_IDENT,
    TK_PLUS, TK_MINUS, TK_STAR, TK_SLASH, TK_MOD, TK_CARET,
    TK_LT, TK_LE, TK_GT, TK_GE, TK_EQ, TK_NEQ,
    TK_SLT, TK_SLE, TK_SGT, TK_SGE, TK_SEQ, TK_SNE,
    TK_CONCAT,      /* || */
    TK_LCONCAT,     /* ||| */
    TK_ASSIGN,      /* := */
    TK_SWAP,        /* :=: */
    TK_REVASSIGN,   /* <- */
    TK_AUGPLUS, TK_AUGMINUS, TK_AUGSTAR, TK_AUGSLASH, TK_AUGCONCAT,
    TK_AND,         /* & */
    TK_BAR,         /* | */
    TK_BACKSLASH,   /* \ */
    TK_BANG,        /* ! */
    TK_QMARK,       /* ? */
    TK_AT,          /* @ */
    TK_TILDE,       /* ~ */
    TK_DOT,
    TK_TO, TK_BY, TK_EVERY, TK_DO,
    TK_IF, TK_THEN, TK_ELSE,
    TK_WHILE, TK_UNTIL, TK_REPEAT,
    TK_RETURN, TK_SUSPEND, TK_FAIL, TK_BREAK, TK_NEXT,
    TK_PROCEDURE, TK_END,
    TK_GLOBAL, TK_LOCAL, TK_STATIC,
    TK_RECORD, TK_LINK, TK_INVOCABLE,
    TK_CASE, TK_OF, TK_DEFAULT,
    TK_CREATE, TK_NOT,
    TK_LPAREN, TK_RPAREN, TK_LBRACE, TK_RBRACE, TK_LBRACK, TK_RBRACK,
    TK_COMMA, TK_SEMICOL, TK_COLON,
    TK_ERROR
} IcnTkKind;
```

### AST node kinds

```c
typedef enum {
    ICN_INT, ICN_REAL, ICN_STR, ICN_CSET, ICN_VAR,
    ICN_TO, ICN_TO_BY,
    ICN_ADD, ICN_SUB, ICN_MUL, ICN_DIV, ICN_MOD, ICN_POW, ICN_NEG,
    ICN_LT, ICN_LE, ICN_GT, ICN_GE, ICN_EQ, ICN_NE,
    ICN_SLT, ICN_SLE, ICN_SGT, ICN_SGE, ICN_SEQ, ICN_SNE,
    ICN_CONCAT, ICN_LCONCAT,
    ICN_ALT,        /* E1 | E2 — value alternation */
    ICN_BANG,       /* !E — generate elements */
    ICN_LIMIT,      /* E \ N */
    ICN_NOT,        /* \E — succeed if E fails */
    ICN_SEQ_EXPR,   /* E1 ; E2 */
    ICN_EVERY, ICN_WHILE, ICN_UNTIL, ICN_REPEAT,
    ICN_IF,         /* indirect goto gate — paper §4.5 */
    ICN_CASE,
    ICN_ASSIGN, ICN_AUGOP, ICN_SWAP,
    ICN_SCAN, ICN_SCAN_AUGOP,
    ICN_CALL, ICN_RETURN, ICN_SUSPEND, ICN_FAIL, ICN_BREAK, ICN_NEXT,
    ICN_FIELD, ICN_SUBSCRIPT,
    ICN_PROC, ICN_RECORD, ICN_GLOBAL,
} IcnKind;
```

### Test corpus — Rung 1

```
test/frontend/icon/corpus/rung01_paper/
  t01_to5.icn          every write(1 to 5);
  t02_mult.icn         every write((1 to 3) * (1 to 2));
  t03_nested_to.icn    every write((1 to 2) to (2 to 3));
  t04_lt.icn           every write(2 < (1 to 4));
  t05_compound.icn     every write(3 < ((1 to 3) * (1 to 2)));
  t06_paper_expr.icn   full optimized paper example
```

Oracle: `icont` + `iconx` from `icon-master`.

---

## Sprint I-2 Plan: Emitter

### Files to create

```
src/frontend/icon/
  icon_emit.h        — emitter API
  icon_emit.c        — IcnNode → four-port x64 ASM chunks
  icon_driver.c      — main(): lex → parse → emit
icon-asm             — driver shell script (top-level, mirrors snobol4-asm)
```

### Port threading model

```c
typedef struct {
    char start[64];    /* α — initial entry (synthesized) */
    char resume[64];   /* β — re-entry for next value (synthesized) */
    char fail[64];     /* ω — where to go on failure (inherited) */
    char succeed[64];  /* γ — where to go on success (inherited) */
} PortSet;
```

Labels: `icon_N_a` (α), `icon_N_b` (β), `icon_N_g` (γ), `icon_N_w` (ω)
where N is a unique node ID. Matches existing α/β/γ/ω naming in ASM backend.

### Four-port templates (from Proebsting paper)

**ICN_INT** (§4.1):
- α: `value ← N; goto γ`
- β: `goto ω`

**ICN_ADD/MUL/etc** (§4.3): E1 outer loop, E2 restarted per E1 value.
Reuses `E_ADD/MPY` emission path from `emit_byrd_asm.c` — just call it.

**ICN_LT/GT/etc** (§4.3 variant): E2 resumed on comparison failure (goal-directed).

**ICN_TO** (§4.4): `I` temp; increment on β; check `I > E2.value` → E2.β.

**ICN_IF** (§4.5): `gate` temp holds address of E2.β or E3.β; resume = indirect goto.

**ICN_EVERY**:
- α: goto E.α
- β: goto body.β
- E.ω → every.ω (exhausted)
- E.γ → body.α
- body.ω → E.β (get next)
- body.γ → every.γ

---

## Session Bootstrap (every I-session)

```bash
git clone https://github.com/snobol4ever/snobol4x
git clone https://github.com/snobol4ever/.github
bash /home/claude/snobol4x/setup.sh
# Reference material already present from session planning:
# /home/claude/jcon-master/   — JCON source (irgen.icn, ir.icn)
# /home/claude/icon-master/   — Icon reference impl (icont oracle)
```

Read FRONTEND-ICON.md §NOW for current milestone. Start at first ❌.

---

## Reference

- Proebsting 1996 paper: "Simple Translation of Goal-Directed Evaluation" — four-port templates §4.1–4.5
- JCON source: `jcon-master/tran/` — `ir.icn` (IR vocab), `irgen.icn` (wiring patterns)
- Icon reference impl: `icon-master/src/icont/` — `tparse.c`, `tcode.c`
- Prolog frontend (structural template): `src/frontend/prolog/`
- ASM macro library: `src/runtime/asm/snobol4_asm.mac`
- MISC.md §JCON — lessons learned from JCON study

---

## Deep JCON Analysis — Session I-0 (2026-03-23)

Full scan of `jcon-master/tran/` + `ByrdBox/` against the Proebsting 1996 paper.
Read before writing any emitter code. This is the canonical pre-coding reference.

---

### `ir.icn` — Complete IR vocabulary

**Temporaries and labels (currency of four-port wiring):**
```
ir_Tmp(name)          ← SSA value temp: "tmp1", "tmp2", ...
ir_TmpLabel(name)     ← indirect-goto target temp: "loc1", "loc2", ... (the gate)
ir_Label(value)       ← direct label: "a_If_start", etc.
```

**Key instructions for our emitter:**
```
ir_IntLit/RealLit/StrLit/CsetLit(coord, lhs, val)  ← literal load
ir_Var(coord, lhs, name)              ← variable address
ir_Move(coord, lhs, rhs)              ← copy
ir_MoveLabel(coord, lhs, label)       ← lhs = address-of label (gate setup)
ir_Goto(coord, targetLabel)           ← direct jump
ir_IndirectGoto(coord, targetTmpLabel) ← jump through gate temp (§4.5)
ir_Succeed(coord, expr, resumeLabel)  ← yield value + resume address (suspend)
ir_Fail(coord)                        ← procedure fail
ir_ResumeValue(coord, lhs, value, failLabel) ← resume suspended generator
ir_OpFunction(coord, lhs, fn, argList, failLabel) ← call operator/builtin
ir_Call(coord, lhs, fn, argList, failLabel)  ← call user procedure
ir_ScanSwap(coord, subject, pos)      ← atomic swap &subject/&pos for scan
ir_Unreachable(coord)                 ← dead code (post-return β port)
```

---

### `irgen.icn` — Four-port wiring patterns (authoritative survey)

Every `ir_a_Foo` has signature `(p, st, inuse, target, bounded, rval)`.
`bounded` = non-null in "value needed" context → `/bounded &` guards β emission.
**We defer the bounded optimization but MUST thread the parameter.**

#### Literals (§4.1)
```
α: lhs ← val; goto success
β: goto failure          ← /bounded only
```
All four types (int/real/str/cset) identical. `/bounded & suspend ir_chunk(p.ir.resume, [goto failure])`.

#### Variables / keywords
```
ir_a_Ident: α: Var(name) → lhs; goto success.   β: goto failure
ir_a_Key:   most: α: Key(name) → lhs; goto success.  β: goto failure
            &fail: α: goto failure.  β: ir_Unreachable
            generator keywords: β uses ir_ResumeValue
```

#### Unary operators (simple set: `.`, `/`, `\`, `*`, `?`, `+`, `-`, `~`, `^`)
```
start → operand.start
operand.success → compute → success
operand.failure → failure
resume → operand.resume  (simple funcs set)
```
Generator unops (`!`, `?`, `\`) use `ir_ResumeValue` + closure on β. Defer to Rung 2.

#### Binary operators (§4.3) — the `funcs` set
All arithmetic and relational are in `funcs`: `+`, `-`, `*`, `/`, `%`, `^`, `**`,
`++`, `--`, `<`, `<=`, `=`, `~=`, `>=`, `>`, `<<`, `==`, `~==`, `>>`, `===`, `~===`, `||`, `|||`, `&`, `.`, `[]`, `:=`, `:=:`, `@`.

**For funcs-set ops (all Rung 1 ops):**
```
start → left.start
left.success → right.start
left.failure → failure
right.failure → left.resume   ← right exhausted → retry left
right.success → compute op → success
resume → right.resume         ← simple: right.resume
```

Non-funcs ops use `ir_ResumeValue` + `closure` temp. Defer to Rung 2.

**Relational variant (§4.3 goal-directed retry):**
Same wiring but `right.success`: if comparison fails → goto `right.resume` (retry right).
This IS the goal-directed magic. `2 < (1 to 4)` → 3, 4.

**Conjunction `&` → dispatches to `ir_conjunction` (NOT binop wiring):**
```
start → left.start
left.success → right.start
left.failure → failure
right.failure → left.resume
right.success → success
resume → right.resume
```
**Add `ICN_AND` node to enum.** Handle as special case in `icon_emit.c`.

#### `to`/`by` generator (§4.4)
JCON uses runtime `ir_operator("...", 3)` call. **We use inline counter (paper §4.4):**
```
to.start → E1.start
E1.failure → to.failure
E1.success → E2.start
E2.failure → E1.resume
E2.success: to.I ← E1.value; goto to.code
to.resume:  to.I += 1; goto to.code
to.code:    if (to.I > E2.value) goto E2.resume
            to.value ← to.I; goto to.success
```
Temps: `to_I` (counter int), `to_V` (value). Extra label `to.code`.

#### `if`/`then`/`else` (§4.5 — indirect goto gate)
```
start → expr.start         (expr evaluated as "always bounded")
resume → IndirectGoto(t)   ← /bounded only
expr.success → MoveLabel(t, thenexpr.resume); goto thenexpr.start
expr.failure → MoveLabel(t, elseexpr.resume); goto elseexpr.start
thenexpr.success/failure → success/failure
elseexpr.success/failure → success/failure
```
`t` = `ir_TmpLabel` ("loc1"). Exactly matches paper §4.5.
**Bounded variant omits MoveLabel** (expr.success → directly goto thenexpr.start).

#### `every`/`do`
```
start → expr.start
expr.success → body.start
body.success → expr.resume   ← keep pumping
body.failure → expr.resume   ← both outcomes pump the generator
expr.failure → failure       ← generator exhausted = every done
resume → IndirectGoto(continue)  ← /bounded
```
If no `do` body: body = a_Key("fail") so body always fails immediately → pumps expr.

#### `|` value alternation (n-ary)
```
start → eList[1].start
eList[i].success → [/bounded]: MoveLabel(t, eList[i].resume); goto success
eList[i].failure → eList[i+1].start
eList[-1].failure → failure
resume → IndirectGoto(t)   ← /bounded
```
`t` tracks which alternative last succeeded.

#### `while`/`until`/`repeat`
```
while:  expr.success → body.start; expr.failure → failure
        body.success/failure → expr.start
until:  expr.success → failure; expr.failure → body.start
        body.success/failure → expr.start
repeat: body.success/failure → body.start  (infinite)
```

#### `suspend E do body` (user-defined generator)
```
start → expr.start
expr.success → Succeed(susp_val, resume_label_t)   ← yield to caller
resume_label_t: goto body.start                    ← caller resumes here
body.success/failure → expr.resume                 ← get next value from E
expr.failure → failure
resume → IndirectGoto(continue)  ← /bounded
```
`ir_Succeed(val, resumeLabel)` = the co-routine yield with a resume address.
Caller uses `ir_ResumeValue` to return. **Needs Technique 2 DATA blocks. Rung 3.**

#### `not E`
```
E evaluated as "always bounded"
E.success → failure    (E succeeded → not fails)
E.failure → &null → success
resume → failure       (one-shot)
```

#### `E \ N` (limitation)
```
limit N evaluated first (always bounded): N_val = size(N)
resume: if (counter > N_val) goto limit.resume; counter += 1; goto expr.resume
expr wired normally
```

#### `E ? body` (string scanning)
```
Save &subject/&pos into oldsubject/oldpos temps
expr.success → ScanSwap (set new &subject/&pos); goto body.start
body.failure → restore &subject/&pos (ScanSwap); goto expr.resume
body.success → ScanSwap (restore); goto success
resume → ScanSwap; goto body.resume   ← /bounded
```

#### Function calls (goal-directed arg evaluation)
```
Evaluate fn, arg1..argN left to right
arg[i].failure → arg[i-1].resume  (backtrack through args)
arg[N].success → Call(fn, args) → success
resume → ResumeValue(target, closure, argN.resume)
first.failure → failure
```

---

### `optimize.icn` — Three passes (defer, but understand)

1. **Dead-assignment**: remove insns with `lhs = &null`. Single pass.
2. **Copy propagation**: remove `ir_Move(lhs,rhs)` where lhs defined once, rhs used once. Iterate.
3. **Goto chaining**: `goto L; L: goto M` → `goto M`. Collapses Figure 1 → Figure 2.

We stream directly to ASM, so we get Figure-1-style output for now. Post-R1 optimization
requires materializing an IR first. **Not needed for M-ICON-LEX through M-ICON-CORPUS-R4.**

---

### `lexer.icn` — Auto-semicolon (we reject)

JCON inserts virtual `;` on newline when last token ∈ `lex_ender_set` AND
next token ∈ `lex_beginner_set`. We require explicit `;`. Corpus programs need patches.

---

### `ByrdBox/test_icon.c` — Golden C reference

Hand-generated translation of `every write(5 > ((1 to 2) * (3 to 4)));`.
Shows both Figure 1 (raw templates) and Figure 2 (optimized) as compilable C.
Use as the expected output shape when debugging the x64 ASM emitter.
Every `xN_start:`/`xN_resume:` label structure = directly maps to our α/β naming.

---

### Deltas vs. current FRONTEND-ICON.md plan

| Item | Change |
|------|--------|
| `ICN_AND` | **ADD** — conjunction `&` uses `ir_conjunction` wiring, not binop |
| `ICN_NOT`, `ICN_LIMIT`, `ICN_REPALT`, `ICN_COMPOUND`, `ICN_MUTUAL`, `ICN_SECTION` | **ADD** to enum (emitter stubs for now) |
| `ir_ResumeValue` | **Rung 2+** only — all Rung 1 ops are in the `funcs` set |
| `to` generator | Use **inline counter** (paper §4.4), not JCON's runtime `"..."` call |
| `bounded` flag | **Thread as parameter** through all recursive emit calls now, optimize later |
| `suspend` | Needs **Technique 2** DATA blocks — Rung 3, not imminent |
| Milestones M-ICON-LEX → M-ICON-CORPUS-R1 | **No change** — sequence is correct |

---

### Rung 1 runtime requirements (minimal)

Only needs: integer arithmetic (reuse x64 ops), range check (`cmp`/`jg`),
`write(v)` → print int + newline. No strings, no floats, no user procedures.
**The entire paper example is inlinable with zero new runtime functions.**

---

## icon-master/tcode.c Analysis — Session I-0 (2026-03-23)

Full scan of `icon-master/src/icont/tcode.c` (1066 lines), `tlex.c`, `tparse.c`, and
the ByrdBox reference files (`test_icon.c`, `test_icon-1.py`, `test_icon-4.py`).

### Critical finding: tcode.c is a stack-VM bytecode emitter — NOT a Byrd box emitter

`traverse()` emits opcode strings (`emit("toby")`, `emit("pfail")`, `emit("invoke")`)
for a stack-based virtual machine (interpreted by iconx at runtime).
**Our emitter is structurally different** — we emit labeled goto code / NASM jumps
directly. tcode.c is useful only as a reference for:
- AST node type names (`N_To`, `N_If`, `N_Loop`, `N_Scan`, etc.)
- Understanding which cases need special handling

### AST node names from tcode.c (authoritative)

| icont node | Our enum | Notes |
|-----------|---------|-------|
| `N_Int` | `ICN_INT` | ✅ matches |
| `N_Real` | `ICN_REAL` | ✅ matches |
| `N_Str` | `ICN_STR` | ✅ matches |
| `N_Cset` | `ICN_CSET` | ✅ matches |
| `N_Id` | `ICN_VAR` | ✅ matches |
| `N_To` | `ICN_TO` | ✅ matches |
| `N_ToBy` | `ICN_TO_BY` | ✅ matches |
| `N_If` | `ICN_IF` | ✅ matches |
| `N_Loop` | `ICN_EVERY`/`ICN_WHILE`/`ICN_UNTIL`/`ICN_REPEAT` | ⚠ icont unifies all loops into `N_Loop` with `ltype`; we keep separate enums — simpler emitter |
| `N_Not` | `ICN_NOT` | ✅ matches |
| `N_Limit` | `ICN_LIMIT` | ✅ matches |
| `N_Scan` | `ICN_SCAN` | ✅ deferred to Rung 4 |
| `N_Ret` | `ICN_RETURN`/`ICN_FAIL`/`ICN_SUSPEND` | icont uses `Val0(Tree0(t)) == FAIL` to distinguish; our separate nodes are cleaner |
| `N_Proc` | `ICN_PROC` | icont: `init` block → body → `pfail` fallthrough (procedure always fails at end if no return) |
| `N_Create` | *(not planned)* | Co-expressions — out of scope |
| `N_Invok` | `ICN_CALL` | icont emits arg count via `traverse()` return value; we do not use return value |
| `N_Apply` | `ICN_CALL` | `invoke -1` = dynamic application |
| `N_Key` | `ICN_VAR` (keyword) | icont: `emits("keywd", name)`; we map keywords to special variable references |

### N_Loop unification (icont pattern — useful to know)

icont treats `every`, `while`, `until`, `repeat` as `N_Loop` with `ltype`:

```c
case N_Loop:
    switch ((int)Val0(Tree0(t))) {
        case EVERY:   // every E do body
        case WHILE:   // while E do body
        case UNTIL:   // until E do body
        case REPEAT:  // repeat body
    }
```

**Decision:** Keep our separate `ICN_EVERY/ICN_WHILE/ICN_UNTIL/ICN_REPEAT` enum values.
Each has distinct four-port wiring (documented in JCON irgen.icn analysis above).
Merging them into one node with a subtype would require a subtype check in the emitter
anyway — no benefit, slightly less readable.

### N_Proc structure (icont reveals implicit pfail)

Every Icon procedure body ends with `emit("pfail")` — an unconditional procedure failure.
This is what happens when execution falls off the end of a procedure body without `return`
or `fail`. In our emitter:

```nasm
; end of procedure body — fall through to implicit fail
  jmp  proc_name_omega
```

The `pfail` is the ω port of the procedure's Byrd box — already in our design, confirmed correct.

### `return` vs `fail` vs `suspend` (icont clarifies)

icont uses `Val0(Tree0(t)) == FAIL` to check whether `return`/`fail`/`suspend`:
- `return` without expression → `return &null` (succeeds, returns null)
- `fail` → procedure failure (ω port)
- `suspend E` → yield value, keep activation frame alive for resume (β port)

Our separate `ICN_RETURN`/`ICN_FAIL`/`ICN_SUSPEND` nodes encode this cleanly.

### Golden C reference confirms label structure

`ByrdBox/test_icon.c` shows both Figure 1 (raw templates) and Figure 2 (optimized)
as compilable C. Port naming: `xN_start` / `xN_resume` / `xN_fail` / `xN_succeed`
maps exactly to our NASM label convention `nodeN_a` / `nodeN_b` / `nodeN_w` / `nodeN_g`.

Extra label `to1_code` (for the counter check loop) is explicitly shown and required.
This is the canonical reference for correctness of the `to` generator translation.

### test_icon-1.py and test_icon-4.py (execution model reference)

| File | Model | Overhead | Use |
|------|-------|----------|-----|
| `test_icon-1.py` | Recursive dispatch, `match port:` per operator | Recursion | Pedagogic clarity |
| `test_icon-4.py` | Trampoline: each port = function returning next function | No recursion | Continuation-passing style |
| Our ASM emitter | Flat NASM labels + `jmp` | Zero | Most efficient; matches `test_icon.c` |

### `to` generator: inline counter vs runtime opcode

icont emits: `pnull / traverse(E1) / traverse(E2) / push1 / toby`
The `toby` VM opcode handles the generator at runtime.

**We use paper §4.4 inline counter** — no runtime function call, pure goto logic.
This is the correct approach for our emitter. Confirmed by `test_icon.c` Figure 2.

### Oracle build note

The icon-master source uses a configure/make system. Before M-ICON-CORPUS-R1 tests
can run, `icont` and `iconx` must be built. Add M-ICON-ORACLE as the first milestone
(see Milestone Table above). Build command:

```bash
cd /home/claude/icon-master
./configure && make
# binaries land in bin/icont and bin/iconx
echo "every write(1 to 5);" > /tmp/t.icn
./bin/icont -s /tmp/t.icn && ./bin/t
# expect: 1 2 3 4 5 (one per line)
```

### Auto-semicolon: icont does it, we don't

icont's lexer (`yylex.h` + `lextab.h`) inserts virtual `;` on newlines when
last token ∈ `lex_ender_set`. This is standard Icon. **We reject this** —
explicit `;` everywhere. Confirmed deliberate deviation. Corpus programs need patching.
