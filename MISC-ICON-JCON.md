# ARCH-icon-jcon.md — Icon/JCON Deep Analysis

Analysis from Session I-0 (2026-03-23). Reference material for Icon emitter work.
Do NOT append sprint content here — this is a static reference doc.

**Primary sources analyzed:**
- `jcon-master/tran/irgen.icn` — four-port wiring patterns
- `jcon-master/tran/ir.icn` — complete IR vocabulary
- `jcon-master/tran/optimize.icn` — three optimization passes
- `icon-master/src/icont/tcode.c` — stack-VM bytecode emitter (structural ref only)
- `jcon-master/ByrdBox/test_icon.c` — golden C reference (Figure 1 + Figure 2)
- `jcon-master/ByrdBox/test_icon-1.py`, `test_icon-4.py` — execution model refs

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


