# SESSION-icon-wasm.md — Icon × WASM (one4all)

**Repo:** one4all · **Frontend:** Icon (JCON four-port model) · **Backend:** WebAssembly
**Session prefix:** `IW` · **Trigger:** "playing with ICON WASM" / "Icon × WASM" / "IW-session"
**Driver:** `scrip-cc -icn -wasm -o prog.wat prog.icn` → `wat2wasm --enable-tail-call prog.wat -o prog.wasm` → `node test/wasm/run_wasm.js prog.wasm`
**Oracle:** `icont` / `iconx` (standard Icon interpreter)
**Emitter files:**
  - `src/backend/emit_wasm.c`        ← shared (SNOBOL4 + Prolog + Icon shared nodes)
  - `src/backend/emit_wasm_icon.c`   ← Icon-specific ICN_* cases  ← **main work file**
  - `src/backend/emit_wasm_icon.h`   ← public interface

---

## ⚠ DISAMBIGUATION

This is **IW** (Icon × WASM), NOT:
- **IX** = Icon × x86  (`emit_x64_icon.c`)
- **IJ** = Icon × JVM  (`emit_jvm_icon.c`)
- **SW** = SNOBOL4 × WASM  (`emit_wasm.c` SNOBOL4 path)

Check `RULES.md §ICON vs IJ DISAMBIGUATION` when in doubt.

**Own-backend invariant rule (RULES.md):**
```bash
CORPUS=/home/claude/corpus bash test/run_invariants.sh icon_wasm   # ONLY this cell
```
Never run snobol4_wasm, prolog_wasm, icon_x86, icon_jvm, or any other cell.

---

## §NOW — IW-2

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **ICON WASM** | IW-2 `098706b` | one4all `098706b` | **M-IW-A02**: write(str) + ICN_STR data segment → rung01 6/6 |

---

## §BUILD

```bash
FRONTEND=icon BACKEND=wasm TOKEN=TOKEN_SEE_LON bash /home/claude/.github/SESSION_SETUP.sh
```

Installs: `gcc make curl unzip wabt(wat2wasm) node icont/iconx`
Skips:    `nasm libgc-dev java javac mono ilasm swipl`

Manual build check:
```bash
cd /home/claude/one4all
make -j$(nproc) 2>&1 | tail -5      # must build clean
```

---

## §TEST GATE (run every session, own cell only)

```bash
cd /home/claude/one4all
CORPUS=/home/claude/corpus bash test/run_emit_check.sh          # always — 738/0+
CORPUS=/home/claude/corpus bash test/run_invariants.sh icon_wasm  # WASM ICON ONLY
```

`icon_wasm` cell starts at SKIP → 0/0 once `run_icon_wasm()` is added → grows per milestone.

Per-test manual verification:
```bash
./scrip-cc -icn -wasm -o /tmp/t.wat corpus/programs/icon/rung01_paper_mult.icn
wat2wasm --enable-tail-call /tmp/t.wat -o /tmp/t.wasm
node test/wasm/run_wasm.js /tmp/t.wasm
# expect: 1 2 2 4 3 6
```

---

## §ARCHITECTURE — How Icon WASM works

### The oracle chain

```
Proebsting 1996 paper (§4.1–4.5)
    ↓  four-port templates per operator
irgen.icn  (jcon-master/tran/irgen.icn)
    ↓  authoritative wiring for every Icon AST node
byrd_box.py  genc()  — flat-goto C for each node
    ↓
test_icon-4.py  — each Python function returns a function → direct WAT map
    ↓
emit_wasm_icon.c  — (func $nodeN_α ...) with return_call
```

### Key structural fact

`test_icon-4.py` is the **direct structural blueprint** for `emit_wasm_icon.c`:

```python
# Python (test_icon-4.py):
def to1_start():  return x1_start
def to1_resume(): global to1_I; to1_I += 1; return to1_code
```

```wat
;; WAT equivalent:
(func $to1_start  (result i32)  return_call $x1_start)
(func $to1_resume (result i32)
  i32.const SLOT_ADDR
  i32.const SLOT_ADDR  i32.load  i32.const 1  i32.add
  i32.store
  return_call $to1_code)
```

Every Python `return X` → WAT `return_call $X`.
Every Python global assignment → WAT `i32/i64.store` into linear memory slot.

### Byrd port names used in this emitter

| Port | irgen.icn name | byrd_box.py | emit_wasm_icon.c WAT suffix |
|------|---------------|-------------|------------------------------|
| α (start)   | `p.ir.start`   | `_start`   | `$iconN_start`  |
| β (resume)  | `p.ir.resume`  | `_resume`  | `$iconN_resume` |
| γ (succeed) | `p.ir.success` | `_succeed` | wired to caller's succ arg  |
| ω (fail)    | `p.ir.failure` | `_fail`    | wired to caller's fail arg  |

"E1.fail" / "E2.fail" etc. are intermediate glue functions with names like `$iconN_e1fail`.

### Generator state memory

Generator counters (ICN_TO's `to.I`, ICN_ALT's branch index, etc.) live in
WASM linear memory at `ICON_GEN_STATE_BASE = 0x10000` (64 KB offset, above the
SNOBOL4 runtime heap).

Each generator node is assigned a unique slot at emit time (`icon_alloc_gen_slot()`).
Slot address = `0x10000 + slot_index * 64`.

This mirrors `test_icon-4.py`'s `global to1_I` variables but places them in
addressable linear memory so tail-call functions can read/write them without
function arguments.

### Shared nodes

Nodes that exist in the SNOBOL4 frontend too (`E_ADD`, `E_SUB`, `E_MPY`, `E_DIV`,
`E_CONCAT`, `E_QLIT`, `E_ILIT`, `E_FLIT`, `E_ASSIGN`, `E_VART`, etc.) stay in
`emit_wasm.c`. Only `ICN_*` nodes belong here.

---

## §MILESTONE TABLE

| Milestone | ICN nodes | Rung target | Status |
|-----------|-----------|-------------|--------|
| M-IW-SCAFFOLD | all → stub-fail | build only | ✅ IW-1 |
| M-IW-A01 | ICN_INT, ICN_VAR, ICN_ASSIGN, ICN_CALL(write-int), ICN_PROC, ICN_RETURN, ICN_FAIL, ICN_TO, ICN_EVERY, ICN_ALT, ICN_ADD/SUB/MUL/DIV/MOD, ICN_NEG/POS, ICN_LT/LE/GT/GE/EQ/NE | rung01 5/6 | ✅ IW-2 |
| M-IW-A02 | ICN_STR data segment + write(str) via $sno_output_str | rung01 6/6 | ❌ |
| M-IW-A03 | ICN_LT/LE/GT/GE/EQ/NE | rung01 relops | ❌ |
| M-IW-G01 | ICN_TO | rung01 to-gen | ❌ |
| M-IW-G02 | ICN_TO_BY | rung01/02 | ❌ |
| M-IW-G03 | ICN_EVERY | rung01/02 every | ❌ |
| M-IW-G04 | ICN_ALT (value alternation) | rung13 | ❌ |
| M-IW-G05 | ICN_BANG (string/list gen) | rung11 | ❌ |
| M-IW-G06 | ICN_LIMIT | rung14 | ❌ |
| M-IW-S01 | ICN_CONCAT (shared $sno_str_concat) | rung04 | ❌ |
| M-IW-S02 | ICN_SLT/SLE/SGT/SGE/SEQ/SNE | rung12 | ❌ |
| M-IW-S03 | ICN_SIZE / ICN_NONNULL / ICN_NULL | rung12/34 | ❌ |
| M-IW-S04 | ICN_SCAN | rung05 | ❌ |
| M-IW-C01 | ICN_IF (§4.5 gate/br_table) | rung07 | ❌ |
| M-IW-C02 | ICN_WHILE / ICN_UNTIL | rung09 | ❌ |
| M-IW-C03 | ICN_REPEAT / ICN_NEXT / ICN_BREAK | rung09 | ❌ |
| M-IW-C04 | ICN_AUGOP / ICN_SWAP / ICN_IDENTICAL | rung10 | ❌ |
| M-IW-P01 | ICN_PROC / ICN_CALL (user) / ICN_RETURN | rung02 proc | ❌ |
| M-IW-P03 | ICN_SUSPEND | rung02 suspend | ❌ |
| M-IW-P04 | ICN_INITIAL | rung21 | ❌ |
| M-IW-CS01 | ICN_CSET literals | rung06 | ❌ |
| M-IW-CS02 | ICN_CSET_UNION/INTER/DIFF/COMPLEMENT | rung06 | ❌ |
| M-IW-B01 | ICN_CALL(string builtins) | rung08 | ❌ |
| M-IW-D01 | ICN_SUBSCRIPT / ICN_SECTION* | rung16/19/20 | ❌ |
| M-IW-D02 | ICN_MAKELIST / ICN_BANG_BINARY | rung22 | ❌ |
| M-IW-D03 | ICN_CALL(table/insert/lookup) | rung23 | ❌ |
| M-IW-D04 | ICN_FIELD + record def | rung24 | ❌ |
| M-IW-D05 | ICN_CASE | rung33 | ❌ |
| M-IW-PARITY | icon_wasm ≥ icon_x86 baseline (94p/164f) | — | ❌ |

---

## §KEY FILES

| File | Role |
|------|------|
| `src/backend/emit_wasm_icon.c` | **Main work file** — Icon ICN_* WAT emission |
| `src/backend/emit_wasm_icon.h` | Public interface |
| `src/backend/emit_wasm.c` | Shared WASM emitter (SNOBOL4/Prolog/Icon shared nodes) |
| `src/frontend/icon/icon_ast.h` | IcnKind enum + IcnNode struct |
| `src/frontend/icon/icon_emit.h` | Icon emitter shared header |
| `test/wasm/run_wasm.js` | Node.js WASM runner (created SW-1) |
| `test/run_invariants.sh` | Invariant suite — `run_icon_wasm()` cell |
| `corpus/programs/icon/rung01_*.icn` | Rung01 Icon test programs |
| `corpus/programs/icon/rung01_*.expected` | Expected output oracles |
| `ByrdBox/byrd_box.py` | `genc()` — flat-goto C structural oracle |
| `ByrdBox/test_icon-4.py` | Return-function Python = direct WAT blueprint |
| `jcon-master/tran/irgen.icn` | Authoritative four-port wiring per AST node |
| `jcon-master/tran/ir.icn` | Complete IR vocabulary |

---

## §SESSION START (every IW session)

```bash
# 1. Clone (fresh environment)
for repo in .github one4all harness corpus; do
  git clone "https://TOKEN_SEE_LON@github.com/snobol4ever/${repo}.git"
done

# 2. Setup
FRONTEND=icon BACKEND=wasm TOKEN=TOKEN_SEE_LON bash /home/claude/.github/SESSION_SETUP.sh

# 3. Gate (own cell only)
cd /home/claude/one4all
CORPUS=/home/claude/corpus bash test/run_emit_check.sh
CORPUS=/home/claude/corpus bash test/run_invariants.sh icon_wasm

# 4. Read HQ docs
tail -80 /home/claude/.github/SESSIONS_ARCHIVE.md   # handoff — FIRST
cat /home/claude/.github/RULES.md
cat /home/claude/.github/PLAN.md
cat /home/claude/.github/SESSION-icon-wasm.md        # this file
```

---

*SESSION-icon-wasm.md — created IW-1, 2026-03-30, Claude Sonnet 4.6.*
*Scaffold committed: emit_wasm_icon.c + emit_wasm_icon.h — all ICN_* stub-fail.*
