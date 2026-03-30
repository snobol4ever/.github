# SESSION-prolog-wasm.md — Prolog × WASM (one4all)

**Repo:** one4all · **Frontend:** Prolog · **Backend:** WebAssembly (wat2wasm + Node.js)
**Session prefix:** `PW` · **Trigger:** "Prolog frontend with WASM backend"
**Driver:** `scrip-cc -pl -wasm foo.pl -o foo.wat` → `wat2wasm --enable-tail-call foo.wat -o foo.wasm` → `node test/wasm/run_wasm.js foo.wasm`
**Oracle:** `swipl foo.pl` (SWI-Prolog)
**Deep reference:** `BACKEND-WASM.md` · `FRONTEND-PROLOG.md` · `ARCH-prolog-jvm.md` (Byrd-box wiring)

---

## Subsystems

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| Prolog language, IR nodes | `FRONTEND-PROLOG.md` | parser/AST questions |
| WASM backend architecture | `BACKEND-WASM.md` | encoding strategy, runtime layout, tail-call model |
| WASM SNOBOL4 session (sibling) | `SESSION-snobol4-wasm.md` | shared emit_wasm.c helpers |
| Prolog JVM (structural oracle) | `SESSION-prolog-jvm.md` | Byrd-box clause dispatch reference |
| x64 Prolog emitter (structural oracle) | `ARCH-prolog-x64.md` | four-port wiring notes |

---

## §NOW — PW-1

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Prolog WASM** | PW-1 | `(new)` | **M-PW-SCAFFOLD** |

---

## §BUILD

```bash
FRONTEND=prolog BACKEND=wasm TOKEN=TOKEN_SEE_LON bash /home/claude/.github/SESSION_SETUP.sh
```

Installs: `gcc make wabt(wat2wasm) node swipl`
Skips: `nasm libgc-dev java javac mono ilasm icont csnobol4`

---

## §TEST

```bash
cd /home/claude/one4all
CORPUS=/home/claude/corpus bash test/run_emit_check.sh                    # always — 738/0
CORPUS=/home/claude/corpus bash test/run_invariants.sh prolog_wasm        # own cell only
```

**Own-backend-only rule:** This session runs `prolog_wasm` invariants ONLY.
Never run `prolog_x86`, `prolog_jvm`, `snobol4_wasm`, or any x86/JVM cells.

---

## Key Files

| File | Role |
|------|------|
| `src/backend/emit_wasm_prolog.c` | Prolog-specific WASM emitter — **main work file** |
| `src/backend/emit_wasm.c` | Shared WASM emitter (SNOBOL4/ICON/Prolog common nodes) — **do not modify** unless promoting a shared helper |
| `src/frontend/prolog/prolog_lower.c` | Lowers Prolog AST → E_CHOICE/E_CLAUSE/E_UNIFY/E_CUT IR |
| `src/frontend/prolog/term.h` | TERM_t definition |
| `src/frontend/prolog/prolog_runtime.h` | Trail, EnvLayout declarations |
| `test/wasm/run_wasm.js` | Node runner shim (created SW-1) |
| `corpus/programs/prolog/rung01_hello_hello.pl` … `rung10_*` | Source + .ref oracles |

---

## Emitter Architecture — Shared vs. Prolog-Specific

Three WASM sessions share one WASM backend. The split is clean:

| File | Contains | Owned by |
|------|----------|----------|
| `emit_wasm.c` | `E_QLIT/ILIT/FLIT`, `E_ADD/SUB/MPY/DIV/MOD`, `E_CONCAT`, `E_NEG`, `E_VAR/KW`, OUTPUT dispatch, runtime imports, string literal table, `emit_wasm_expr()` | SW (SNOBOL4 WASM) — do not modify |
| `emit_wasm_prolog.c` | `E_CHOICE`, `E_CLAUSE`, `E_UNIFY`, `E_CUT`, `E_TRAIL_MARK`, `E_TRAIL_UNWIND`, `prolog_emit_wasm()` entry | **PW (this session)** |
| `emit_wasm_icon.c` | ICN_* nodes (future) | IW session (future) |

`emit_wasm_prolog.c` calls `emit_wasm_expr(e, wasm_out)` for arithmetic/literal
subexpressions inside Prolog goals — the shared path from `emit_wasm.c`.
If `emit_wasm_expr` is not yet exported as a symbol, the first PW task is
to make it `extern` in `emit_wasm.c` and declare it in a new `emit_wasm.h`.

---

## Byrd Box → WASM Encoding (Prolog-specific)

x64/JVM encode α/β/γ/ω as flat labels + jmp/goto.
WASM has no arbitrary goto — each port is a **tail-call WAT function**.

### E_CHOICE + E_CLAUSE (predicate with N clauses)

```wat
;; foo/1 with two clauses
(func $foo_1_α (param $env i32) (param $trail i32) (result i32)
  ;; trail mark
  (call $trail_mark (local.get $trail))
  ;; unify head arg against clause-1 pattern
  ;; on unify success:
  ;;   emit body goals → return_call $foo_1_γ
  ;; on unify fail:
  return_call $foo_1_β)     ;; try next clause

(func $foo_1_β (param $env i32) (param $trail i32) (result i32)
  (call $trail_unwind (local.get $trail))
  (call $trail_mark   (local.get $trail))
  ;; unify head arg against clause-2 pattern
  ;; on success: body → return_call $foo_1_γ
  return_call $foo_1_ω)     ;; all clauses exhausted

(func $foo_1_γ (param $val i32) (result i32)
  return_call $continuation_γ)   ;; succeed to caller

(func $foo_1_ω (result i32)
  return_call $caller_β)         ;; fail to caller's retry
```

### E_UNIFY

Unification binds variables and pushes to trail.  On failure, `return_call` to
enclosing clause's β path (which calls `trail_unwind` before retrying next clause).

### E_CUT

Seals β — after cut, `return_call $foo_1_ω` directly (bypasses remaining clauses).
Exactly FENCE semantics, identical to SNOBOL4 FENCE in emit_wasm.c pattern nodes.

### E_TRAIL_MARK / E_TRAIL_UNWIND

Inline WAT calls to `$trail_mark` / `$trail_unwind` helpers in the Prolog WASM runtime.
These live in `src/runtime/wasm/pl_runtime.wat` (new file, created M-PW-SCAFFOLD).

---

## Runtime: Prolog WASM Linear Memory Layout

```
offset 0        : output buffer (8KB — shared with sno_runtime.wat layout)
offset 8192     : string/atom heap (growing upward)
offset 32768    : variable env frames (growing upward, 16KB)
offset 49152    : trail stack (growing upward, 8KB)
offset 57344    : term heap (growing upward, 64KB)
offset 131072   : end of 2-page (128KB) allocation
```

Prolog WASM programs use a **separate module** from SNOBOL4 WASM programs —
different runtime imports (`"pl"` namespace, not `"sno"` namespace).
The node runner shim (`run_wasm.js`) is shared unchanged.

---

## Sprint Map

| Sprint | Milestones | Description |
|--------|-----------|-------------|
| PW-1 | M-PW-SCAFFOLD, M-PW-HELLO | Toolchain wire-up, first output |
| PW-2 | M-PW-A01 – M-PW-A03 | Deterministic: facts, unify, arith |
| PW-3 | M-PW-B01 – M-PW-B03 | Backtracking: member, lists, cut |
| PW-4 | M-PW-C01 – M-PW-C03 | Recursion, builtins, puzzle programs |
| PW-5 | M-PW-PARITY | Full invariant cell parity with x86 |

---

## Milestone Ladder

### Sprint PW-1 — Infrastructure

#### M-PW-SCAFFOLD ⬜
**Goal:** `scrip-cc -pl -wasm null.pl` builds + exits 0, no output.

**Work:**
1. Create `src/backend/emit_wasm_prolog.c` — stub `prolog_emit_wasm(Program*, FILE*, const char*)` that emits an empty `.wat` module `(module)`.
2. Create `src/backend/emit_wasm.h` — export `emit_wasm_expr(const EXPR_t*, FILE*)` so `emit_wasm_prolog.c` can call shared arithmetic/literal emission.
3. Wire in `driver/main.c`: when `-pl` AND `-wasm` flags both set → call `prolog_emit_wasm()`.
4. Add `emit_wasm_prolog.c` to `Makefile`.
5. Create `src/runtime/wasm/pl_runtime.wat` — stub: memory export, `$trail_mark`, `$trail_unwind`, `$pl_output_str`, `$pl_output_flush`.
6. Compile stub runtime: `wat2wasm --enable-tail-call src/runtime/wasm/pl_runtime.wat -o src/runtime/wasm/pl_runtime.wasm`

**Gate:** `make` clean · emit-diff 738/0 · `-pl -wasm null.pl` produces `(module)` without crash
**Commit:** `PW-1: M-PW-SCAFFOLD — prolog×wasm stub: emit_wasm_prolog.c + pl_runtime.wat`

---

#### M-PW-HELLO ⬜
**Goal:** `write('hello'), nl.` → WASM output `hello\n`

**Work:**
1. `E_FNC(write/1)` with atom arg → `E_QLIT` via shared `emit_wasm_expr()` → `call $pl_output_str`
2. `nl/0` → `call $pl_output_nl`
3. `E_QLIT` atom interning already works via `emit_wasm.c` string table — just call it
4. `:- initialization(main)` directive → emit `(func $main (export "main") ...)`

**Gate:** `rung01_hello_hello.pl` → `hello\n` via node runner · 1/1
**Invariant:** `prolog_wasm` cell added to `run_invariants.sh` at 1 test
**Commit:** `PW-1: M-PW-HELLO — prolog×wasm hello: write/1 + nl/0, 1/1`

---

### Sprint PW-2 — Deterministic Goals

#### M-PW-A01: FACTS ⬜
**Rung:** `rung02_facts_*` (2 tests)
**IR nodes:** `E_CHOICE`(1 clause) · `E_CLAUSE` · `E_UNIFY`(atom literal)
**Work:** First real E_CHOICE emission: 1-clause predicate = α only (no β needed); `E_UNIFY` atom check.
**Gate:** rung 2: 2/2 · invariant cell 3 tests
**Commit:** `PW-2: M-PW-A01 — facts: E_CHOICE/E_CLAUSE/E_UNIFY atom, 2/2`

---

#### M-PW-A02: HEAD UNIFICATION ⬜
**Rung:** `rung03_unify_*` (3 tests)
**IR nodes:** `E_UNIFY`(compound) · `E_VART` (variable binding + trail push)
**Work:** Trail push on `E_VART` binding; `E_UNIFY` compound recursion.
**Gate:** rung 3: 3/3 · invariant cell 6 tests
**Commit:** `PW-2: M-PW-A02 — unify: compound terms + VART trail, 3/3`

---

#### M-PW-A03: ARITHMETIC `is/2` ⬜
**Rung:** `rung04_arith_*` (2 tests)
**IR nodes:** `E_FNC(is)` → delegates arith subexpr to shared `emit_wasm_expr()` for `E_ADD/SUB/MPY/DIV`
**Work:** Wire `is/2` goal → evaluate RHS via shared emitter → bind LHS var via trail.
**Gate:** rung 4: 2/2 · invariant cell 8 tests
**Commit:** `PW-2: M-PW-A03 — arith is/2: shared emit_wasm_expr + var bind, 2/2`

---

### Sprint PW-3 — Backtracking

#### M-PW-B01: BACKTRACK — `member/2` ⬜
**Rung:** `rung05_backtrack_*` (2 tests)
**IR nodes:** `E_CHOICE`(2 clauses) · `E_TRAIL_MARK` · `E_TRAIL_UNWIND` · β-port retry
**Work:** First multi-clause `E_CHOICE`: α tries clause 1, on fail unwinds trail + `return_call $β`, β tries clause 2, on fail `return_call $ω`. This is the core backtracking wire.
**Gate:** rung 5: 2/2 · invariant cell 10 tests
**Commit:** `PW-3: M-PW-B01 — backtrack: E_CHOICE 2-clause α/β/γ/ω + trail, 2/2`

---

#### M-PW-B02: LISTS ⬜
**Rung:** `rung06_lists_*` (3 tests: append/3, length/2, reverse/2)
**IR nodes:** List `[H|T]` compound · recursive `E_CHOICE`
**Work:** List nil/cons WAT encoding; recursive predicate calls via function table or direct `return_call`.
**Gate:** rung 6: 3/3 · invariant cell 13 tests
**Commit:** `PW-3: M-PW-B02 — lists: append/length/reverse, recursive E_CHOICE, 3/3`

---

#### M-PW-B03: CUT ⬜
**Rung:** `rung07_cut_*` (2 tests: differ/N, closed-world negation)
**IR nodes:** `E_CUT` → seal β port
**Work:** Cut emits `return_call $foo_N_ω` directly, bypassing remaining clause β functions. Exactly FENCE semantics.
**Gate:** rung 7: 2/2 · invariant cell 15 tests
**Commit:** `PW-3: M-PW-B03 — cut: E_CUT seals β → ω, 2/2`

---

### Sprint PW-4 — Recursion + Builtins

#### M-PW-C01: RECURSION ⬜
**Rung:** `rung08_recursion_*` (2 tests: fib, factorial)
**Work:** Deep recursive calls — WASM tail calls via `return_call` prevent stack overflow for tail-recursive predicates; non-tail recursion uses WASM call stack (bounded depth).
**Gate:** rung 8: 2/2 · invariant cell 17 tests
**Commit:** `PW-4: M-PW-C01 — recursion: fib/fact, tail-call + bounded-depth, 2/2`

---

#### M-PW-C02: BUILTINS ⬜
**Rung:** `rung09_builtins_*` (4 tests)
**IR nodes:** `E_FNC`: `functor/3`, `arg/3`, `=../2`, `atom/1`, `integer/1`, `var/1`, `nonvar/1`, `compound/1`
**Work:** Each builtin is a WAT helper function in `pl_runtime.wat`; `E_FNC` dispatch calls them.
**Gate:** rung 9: 4/4 · invariant cell 21 tests
**Commit:** `PW-4: M-PW-C02 — builtins: functor/arg/=../type tests, 4/4`

---

#### M-PW-C03: PUZZLE PROGRAMS ⬜
**Rung:** `rung10_programs_*` (Lon's word-puzzle solvers)
**Work:** Full programs exercising all of the above: constraint solving, multiple backtracking levels, write/nl output. Fix any gaps revealed.
**Gate:** rung 10: ≥3/N · invariant cell ≥24 tests
**Commit:** `PW-4: M-PW-C03 — puzzle programs: constraint solvers, ≥3/N`

---

#### M-PW-PARITY ⬜
**Goal:** `prolog_wasm` invariant cell matches or exceeds x86 baseline (13p/94f → aim ≥13p).
**Work:** Run full Prolog corpus; fix remaining gaps in isolation.
**Gate:** `run_invariants.sh prolog_wasm` → ≥13p ✅
**Commit:** `PW-5: M-PW-PARITY — Prolog×WASM parity with x86 baseline`

---

## Invariant Baseline (projected)

| After milestone | `prolog_wasm` count |
|----------------|---------------------|
| M-PW-HELLO | 1 |
| M-PW-A01 | 3 |
| M-PW-A02 | 6 |
| M-PW-A03 | 8 |
| M-PW-B01 | 10 |
| M-PW-B02 | 13 |
| M-PW-B03 | 15 |
| M-PW-C01 | 17 |
| M-PW-C02 | 21 |
| M-PW-C03 | 24+ |
| M-PW-PARITY | ≥13p (x86 baseline) |

---

## Bootstrap (next PW session)

```bash
# Step 0 — clone
for repo in .github one4all harness corpus; do
  git clone "https://TOKEN_SEE_LON@github.com/snobol4ever/${repo}.git"
done

# Step 1 — setup
FRONTEND=prolog BACKEND=wasm TOKEN=TOKEN_SEE_LON bash /home/claude/.github/SESSION_SETUP.sh

# Step 2 — gate
cd /home/claude/one4all
CORPUS=/home/claude/corpus bash test/run_emit_check.sh           # expect 738/0
CORPUS=/home/claude/corpus bash test/run_invariants.sh prolog_wasm  # own cell only

# Step 3 — read in order
tail -120 /home/claude/.github/SESSIONS_ARCHIVE.md
cat /home/claude/.github/RULES.md
cat /home/claude/.github/SESSION-prolog-wasm.md    # this file — §NOW
```

---

*SESSION-prolog-wasm.md — created PW-1, 2026-03-30, Claude Sonnet 4.6.*
*§NOW lives here. All session state updated at end of each PW session.*
