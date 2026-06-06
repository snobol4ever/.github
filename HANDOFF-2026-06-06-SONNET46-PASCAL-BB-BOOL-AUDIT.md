# HANDOFF — 2026-06-06 — Sonnet 4.6 — Pascal Boolean Semantics Audit

**Session 18. No code committed. Prior 36/36 holds. Repos: .github only (this doc + goal watermark).**

## What this session did

Stopped a half-baked boolean fix, read pcom.pas and pint.pas cover-to-cover, and established the
ground truth for every Pascal construct. Found three latent boolean bugs invisible to all existing probes.
Designed the PB-10a/10b/10c fix ladder. No code changed in SCRIP or corpus.

---

## P4 Pascal boolean semantics — what pcom.pas/pint.pas actually say

Relational operators (`<`, `>`, `<=`, `>=`, `=`, `<>`) in P4 Pascal produce a **boolean value** stored as
`.vb` on the P-machine stack (pint opcode `grt`/`les`/etc. → `store[sp].vb := comparison_result`). They are
NOT goal-directed success/failure. The result is a first-class value, storable in variables, passable to
procs, comparable with `=`/`<>`.

`and` = boolean AND (pint opcode 43): `store[sp].vb := vb1 AND vb2`
`or` = boolean OR (pint opcode 44): `store[sp].vb := vb1 OR vb2`
`not` = boolean NOT (pint opcode 42): `store[sp].vb := NOT vb`
`fjp` = false-jump (pint opcode 24): `if NOT store[sp].vb then pc := q` — used by if/while/repeat/until

`writeln(boolean_expr)` is **error(399)** in pcom — the write procedure rejects scalar types (boolean
is `form=scalar`). There is no wri/wrr/wrc counterpart for boolean. A probe testing writeln of a
boolean is invalid P4 Pascal.

`true` → `ldc p=3, q=1` → `store[sp].vb := true`; `false` → `ldc p=3, q=0`.
Booleans are stored as `.vb`, NOT as integers. SCRIP maps them to INTVAL(0/1) which works for
condition checks (`if b then` via `pas_cond` → `b != 0`) but fails for the bugs below.

---

## The three bugs (none covered by existing probes)

### Bug 1: `not b` — goal-directed inversion, not boolean NOT

```pascal
var a: boolean; begin a := true; if not a then writeln('ok') end.
```

`NOTSY factor { $$ = un(TT_NOT, $2); }` → `v_not` swaps γ and ω. `not true` → goal-directed NOT of a
truthy value → FAILS → program dies silently. Zero output.

Correct: `not b` should compute `b=0 ? 1 : 0`. Fix: replace the grammar arm with
`TT_IF(pas_cond($2), ilit(0), ilit(1))` — if factor truthy return 0, else return 1.

### Bug 2: `b := relop_false` — program dies silently

```pascal
var x,y: integer; b: boolean; begin x:=5; y:=3; b := x < y; if b then writeln('ok') end.
```

`x < y` is false → in the interpreter, the relop subgraph's `binop_apply` returns FAILDESCR → the
IR_ASSIGN node takes ω → PFAIL → program terminates with no output. b was never assigned.

Correct: `b := (x < y)` should assign INTVAL(0) (false). Fix: apply `pas_bool($3)` to the RHS in the
`assignment:` grammar rule. `pas_bool(relop)` → `TT_IF(relop, ilit(1), ilit(0))` → IR_IF with then=1
and else=0 → the subgraph always produces INTVAL(1) or INTVAL(0), never fails.

### Bug 3: `b := relop_true` — assigns rv (rhs value), not 1

When `x > y` is true, `binop_apply(BINOP_GT, 5, 3)` returns INTVAL(3) (the rhs). So `b` gets
INTVAL(3), not INTVAL(1). For `if b then ...` via `pas_cond` → `b != 0` this accidentally succeeds, but
the value is semantically wrong and will break boolean arithmetic (`b and c` = `3 * 1 = 3` ≠ 1 for
"true and true"). Same fix as Bug 2.

---

## Construct grid — Pascal → TT_* → IR_* → status

| Pascal | pcom | SCRIP TT_* | SCRIP IR | Status |
|---|---|---|---|---|
| `a + b` int | adi | TT_ADD | IR_BINOP(ADD) | ✅ |
| `a - b` int | sbi | TT_SUB | IR_BINOP(SUB) | ✅ |
| `a * b` int | mpi | TT_MUL | IR_BINOP(MUL) | ✅ |
| `a div b` | dvi | TT_DIV | IR_BINOP(DIV) | ✅ |
| `a mod b` | mod | TT_MOD | IR_BINOP(MOD) | ✅ |
| `a / b` real | dvr | TT_DIV | IR_BINOP(DIV) | ✅ |
| `-a` | ngi | TT_MNS | IR_BINOP(SUB,0,a) | ✅ |
| `sqr(a)` | sqi | TT_FNC(__pas_sqr) | IR_CALL | ✅ |
| `a > b` **as condition** | grt + fjp | TT_GT in pas_cond/TT_IF | IR_BINOP(GT)→IR_IF | ✅ |
| `a > b` **as value** | grt → vb | TT_GT | IR_BINOP(GT) → rv or FAILDESCR | ❌ wrong |
| `b := relop_false` | grt+str → vb=false | TT_ASSIGN(b, TT_GT) | assignment fails silently | ❌ Bug 2 |
| `b := relop_true` | grt+str → vb=true | TT_ASSIGN(b, TT_GT) | b gets rv not 1 | ❌ Bug 3 |
| **`a and b`** | and → vb=vb∧vb | TT_MUL | IR_BINOP(MUL) | ⚠️ accidental (0*0=0, 1*1=1) |
| **`a or b`** | ior → vb=vb∨vb | TT_ADD | IR_BINOP(ADD) | ⚠️ accidental (0+0=0, 1+0=1) |
| **`not a`** | not → ¬vb | TT_NOT | IR_NOT (swaps γ/ω) | ❌ Bug 1 |
| `writeln(bool)` | **error(399)** | (would call __pas_writeln) | — | ❌ invalid Pascal |
| `writeln(int)` | csp wri | TT_FNC(__pas_writeln) | IR_CALL | ✅ |
| `if e then s` | fjp | TT_IF(pas_cond,s) | IR_IF | ✅ |
| `while e do s` | fjp | TT_WHILE(pas_cond,s) | IR_WHILE | ✅ |
| `repeat s until e` | fjp | TT_REPEAT | v_pascal_repeat | ✅ |
| `for i:=a to b do s` | cup/ret loop | TT_FOR | v_pascal_for | ✅ |
| `case e of` | xjp | TT_SUCCEED | **❌ unimplemented** |
| `goto N` | ujp | TT_SUCCEED | **❌ unimplemented** |
| `a[i]` read | ind | TT_IDX→arr_get | IR_CALL | ✅ |
| `a[i] := v` | str | arr_set_pure | IR_CALL | ✅ |
| `r.field` | ind | TT_IDX→arr_get | IR_CALL | ✅ |
| `r.field := v` | str | __pas_field_set | IR_CALL | ✅ |
| `new(p)` | csp new | __pas_alloc_rec | IR_CALL | ✅ |
| `p^` | ind | __pas_deref | IR_CALL | ✅ |
| `p^ := v` | sto | __pas_deref_set | IR_CALL | ✅ |
| `e in s` | inn | __pas_in | IR_CALL | ✅ |
| set ops | uni/dif/int | __pas_set{uni,dif,int} | IR_CALL | ✅ |
| nested proc | cup+sl | frame-as-BB | IR_VAR_FRAME | ✅ |
| var params | cup sl | cell-address pass | IR_VAR_FRAME_REF | ✅ |

Note: `and`/`or` accidentally correct because inputs from `true`/`false` literals are INTVAL(0/1), and
integer arithmetic preserves the logic. The bug only surfaces when relop results (INTVAL(rv) not 1) are
passed through.

---

## Hop>1 var-param paths confirmed green (not committed — no code change)

Tested `nestvar.pas` (hop=1: nested proc reads/writes outer var-param), `nestvar2.pas` (hop=2: 3-level
nesting with REF traversal), `nestvar3.pas` (hop=1 forwarding: relay proc passes outer's var-param to
another call). All three pass m2+m3+m4. Commit these as part of PB-10a gate suite (no code change needed —
just add the `.pas` files to corpus).

---

## Fix ladder (PB-10a/b/c) — see GOAL-PASCAL-BB.md for full specs

**PB-10a** — parser only, `pascal.y` + regen `pascal.tab.c` (1 s/r = dangling-else, expected):
- Add `pas_bool(e)`: wraps relop in `TT_IF(e, ilit(1), ilit(0))`, pass-through otherwise.
- Fix `not`: `NOTSY factor` → `TT_IF(pas_cond($2), ilit(0), ilit(1))`.
- Fix assignment: apply `pas_bool($3)` in `assignment: selector BECOMES expression`.
- Fix proc arg: apply `pas_bool($1)` to value in `argument:` rule (not to the width `$3`).
- New probes: `boolassign.pas`, `boolnot.pas`, `nestvar.pas`/`nestvar2.pas`/`nestvar3.pas`.
- Gate m2: all probes correct; existing 36/36 unchanged; SNOBOL smoke 19/0.

**PB-10b** — marshal fix in `bb_call.cpp`, m3/m4 for call args:
- Walk γ chain to find the relop IR_BINOP (not just `lf`); confirm fin=IR_LIT_I(1), ω→IR_LIT_I(0).
- Emit CMP + `x86_jcc_id`/`x86_deflabel_id` conditional store of INTVAL(0/1).

**PB-10c** — assignment template fix, m3/m4 for `b := relop`:
- Diagnose the exact IR_ASSIGN subgraph shape from `v_assign(TT_ASSIGN(b, TT_IF(relop, 1, 0)))`.
- Add detection arm in `bb_gvar_assign.cpp` or `bb_assign_frame.cpp`.

---

## Gotchas for next session

- Do NOT start PB-10b/c before PB-10a is green: the IR structure that PB-10b/c target is produced by
  PB-10a's parser changes. Without those changes, the IR is different (raw relop, no TT_IF wrapper).
- `and`/`or` are TT_MUL/TT_ADD → IR_BINOP(MUL/ADD). This is accidentally correct for 0/1 inputs.
  Do NOT change them to TT_AND/TT_OR — those tree types don't exist and the lowering doesn't define them.
  The PB-10a fix produces 0/1 values for relops; once operands are guaranteed 0/1, the accidental
  arithmetic correctness of and/or becomes intentional.
- `case`/`goto` remain unimplemented (TT_SUCCEED). They are out of scope until a probe forces them.
- Parser regen: full regen script aborts at snobol4 flex step. Use
  `cd src/parser/pascal && bison -d -o pascal.tab.c pascal.y` directly.
- The stash from this session (half-baked pb10 attempt) was discarded: `git stash pop` NOT needed —
  the stash was left in place on the SCRIP repo. Next session: `git stash drop` before starting.
