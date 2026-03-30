# SESSION-snobol4-wasm.md — SNOBOL4 × WASM (one4all)

**Repo:** one4all · **Frontend:** SNOBOL4/SPITBOL · **Backend:** WebAssembly (wat2wasm + Node.js)
**Session prefix:** `SW` · **Trigger:** "playing with SNOBOL4 WASM" / Byrd-box WASM
**Driver:** `scrip-cc -wasm prog.sno > prog.wat` → `wat2wasm prog.wat -o prog.wasm` → `node run_wasm.js prog.wasm`
**Oracle:** `snobol4 prog.sno` (CSNOBOL4 2.3.3)
**Deep reference:** `BACKEND-WASM.md` · `ARCH-index.md`

---

## Subsystems

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| SNOBOL4 language, IR nodes | `FRONTEND-SNOBOL4.md` | language/parser questions |
| WASM backend architecture | `BACKEND-WASM.md` | encoding strategy, runtime layout |
| x64 emitter (structural oracle) | `BACKEND-X64.md` | Byrd-box wiring reference |
| Corpus layout | `ARCH-corpus.md` | rung numbering, .ref protocol |

---

## §NOW — SW-1

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **SNOBOL4 WASM** | SW-1 — runtime stub | `645f402` one4all · `44af7e8` corpus | **M-SW-1: RUNTIME-STUB** |

---

## §BUILD

```bash
FRONTEND=snobol4 BACKEND=wasm TOKEN=TOKEN_SEE_LON bash /home/claude/.github/SESSION_SETUP.sh
```

Installs: `gcc make curl unzip wabt(wat2wasm) node snobol4(CSNOBOL4)`
Skips: `nasm libgc-dev java javac mono ilasm icont swipl`

**Note:** `wabt` and `node` must be added to SESSION_SETUP.sh BACKEND=wasm block.
`wabt`: `apt-get install -y wabt` · `node`: already present on Ubuntu 24 as `nodejs`.

---

## §TEST

```bash
cd /home/claude/one4all
CORPUS=/home/claude/corpus bash test/run_emit_check.sh          # always — 738/0
CORPUS=/home/claude/corpus bash test/run_wasm_corpus_rung.sh W01 # per-rung during session
CORPUS=/home/claude/corpus bash test/run_invariants.sh snobol4_wasm  # wasm session: own cell only
```

**Node WASM runner** (`test/wasm/run_wasm.js` — created M-SW-0):
```js
const fs = require('fs');
const bytes = fs.readFileSync(process.argv[2]);
WebAssembly.instantiate(bytes).then(r => {
  const { main, memory } = r.instance.exports;
  const len = main();
  process.stdout.write(Buffer.from(new Uint8Array(memory.buffer, 0, len)));
});
```

---

## Key Files

| File | Role |
|------|------|
| `src/backend/emit_wasm.c` | WASM emitter — main work file (scaffold → full) |
| `src/runtime/wasm/` | WASM runtime (string heap, OUTPUT) — created M-SW-1 |
| `test/wasm/run_wasm.js` | Node runner shim — created M-SW-0 |
| `test/run_wasm_corpus_rung.sh` | Per-rung test runner — created M-SW-0 |
| `corpus/crosscheck/rung2/` … `rung11/` | Source + .ref + .s/.j/.il/.wat — all artifacts flat in same dir |
| `corpus/crosscheck/rungW01/` … `rungW07/` | New pattern-test rungs — same flat layout: .sno .ref .s .j .il .wat |

---

## Byrd-Box Encoding — WASM vs x64

x64 encodes each Byrd port as a flat label + jmp:
```nasm
node_α:   ...           ; start
          jmp node_γ    ; succeed → continuation
node_β:   jmp ...       ; fail → caller's β
```

WASM encodes each port as a tail-call function:
```wat
(func $node_α (result i32)   ;; α = start
  ...
  return_call $node_γ)       ;; succeed → continuation
(func $node_β (result i32)   ;; β = fail
  return_call $caller_β)     ;; propagate failure up
```

`return_call` is zero-overhead (no stack growth). Requires `--enable-tail-call` flag
to `wat2wasm`. Supported natively in Node v22+ (V8), Chrome 112+, Firefox 121+, Safari 17+.

**The `byrd_box.py` `genc()` function is the direct blueprint** for `emit_wasm.c`:
same α/β/γ/ω four-port structure, same EKind switch, same wiring — output syntax differs.

---

## Sprint Map

| Sprint | Milestones | Description |
|--------|-----------|-------------|
| SW-1 | M-SW-0, M-SW-1 | Toolchain + runtime stub |
| SW-2 | M-SW-A01 – M-SW-A03 | Hello, literals, arithmetic |
| SW-3 | M-SW-A04 – M-SW-A06 | Variables, goto, concat |
| SW-4 | M-SW-B01 – M-SW-B03 | Pattern: LIT, SEQ, ALT |
| SW-5 | M-SW-B04 – M-SW-B06 | Pattern: ARBNO, ANY/SPAN/BREAK, POS/RPOS |
| SW-6 | M-SW-C01 – M-SW-C02 | Captures, DATA/ARRAY/TABLE |
| SW-7 | M-SW-C03, M-SW-PARITY | Functions + full 106/106 parity |

---

## Milestone Ladder

### Infrastructure (Sprint SW-1)

#### M-SW-0: TOOLCHAIN ⬜
**Goal:** Full pipeline `source → .wat → .wasm → node → stdout` proven end-to-end.

**Work:**
1. `apt-get install -y wabt` in SESSION_SETUP.sh BACKEND=wasm block
2. Update SETUP-tools.md WASM row: `wabt(wat2wasm), node`
3. Write `test/wasm/run_wasm.js` — Node runner shim (exports `main` + `memory`)
4. Write `test/run_wasm_corpus_rung.sh` — mirrors `run_sc_corpus_rung.sh`:
   - Takes rung dir, iterates `.sno` files
   - Compiles each: `scrip-cc -wasm $f > $stem.wat`
   - Assembles: `wat2wasm --enable-tail-call $stem.wat -o $stem.wasm`
   - Runs: `node test/wasm/run_wasm.js $stem.wasm > $stem.got`
   - Diffs: `diff $stem.ref $stem.got`
5. Hand-write `corpus/crosscheck/rung2/W01_hello_proof.wat` (not emitter-generated)
   — confirms pipeline works before emitter produces any output

**Gate:** hand-written hello.wat produces `HELLO WORLD\n` via `node run_wasm.js` ✅
**Commit:** `SW-1: M-SW-0 — WASM toolchain: wat2wasm + node runner + rung script`

---

#### M-SW-1: RUNTIME-STUB ⬜
**Goal:** `src/runtime/wasm/` skeleton compiles clean; emitter can call into it.

**Work:**
1. Create `src/runtime/wasm/sno_runtime.wat` — inline WAT module fragment:
   - `(memory (export "memory") 4)` — 256KB output buffer at offset 0
   - `sno_output_str` — write string + `\n` to memory, advance pos
   - `sno_output_int` — format i64 integer → string → write
   - `sno_output_flush` — return current pos (used by `main` return value)
   - `sno_string_concat` — inline concat in memory
2. `emit_wasm.c`: add `emit_wasm_runtime_header()` — inlines the above into every `.wat`
3. Build clean; emit-diff still 738/0 (no SNOBOL4 source emits WASM yet — scaffold)

**Gate:** `make` clean, 738/0 ✅
**Commit:** `SW-1: M-SW-1 — WASM runtime stub: memory layout, sno_output_str/int/flush`

---

### Partition A — Output, Literals, Arithmetic (Sprint SW-2 – SW-3)

Corpus: **existing** `corpus/crosscheck/rung2/` through `rung4/` + hello + arith dirs.
Oracles: `.ref` files already exist (generated by CSNOBOL4 2.3.3). **Zero new oracle work.**
Artifacts: add `.wat` flat alongside existing `.sno` / `.ref` / `.s` / `.j` / `.il` in each rung dir.

---

#### M-SW-A01: HELLO ⬜  `[Sprint SW-2]`
**Rung:** `corpus/crosscheck/hello/` (3 tests: hello, literals, empty_string)
**IR nodes:** `E_QLIT` (string literal), `E_ASSIGN` → OUTPUT, `E_NUL` (null)
**Key emitter work:**
- `emit_wasm_program()` skeleton: `(module`, imports, `(func $main ...)`, `(export "main")`
- `E_ASSIGN` to OUTPUT → calls `sno_output_str`
- `E_QLIT` → inline string constant in data segment
- `E_NUL` → assign empty string ""

**WASM shape:**
```wat
(module
  (memory (export "memory") 4)
  (data (i32.const 1024) "HELLO WORLD\00")
  (func $main (export "main") (result i32)
    call $sno_output_str_1024_11   ;; inline helper
    call $sno_output_flush)
)
```

**Gate:** `run_wasm_corpus_rung.sh hello` → 3/3 pass
**Invariant cell:** `snobol4_wasm` added to `run_invariants.sh` at 3 tests
**Commit:** `SW-2: M-SW-A01 — WASM hello: E_QLIT + OUTPUT assign, 3/3`

---

#### M-SW-A02: ARITHMETIC ⬜  `[Sprint SW-2]`
**Rung:** `corpus/crosscheck/rung4/` (5 tests: arith_int, arith_unary, arith_real, arith_mixed, remdr)
**IR nodes:** `E_ILIT`, `E_FLIT`, `E_ADD`, `E_SUB`, `E_MPY`, `E_DIV`, `E_MOD`, `E_NEG`, `E_PLS`
**Key emitter work:**
- Integer arithmetic: WASM `i64.add` / `i64.sub` / `i64.mul` / `i64.div_s` / `i64.rem_s`
- Float arithmetic: WASM `f64.add` etc.
- Mixed promotion: `i64` → `f64` via `f64.convert_i64_s`
- Unary minus: `i64.const 0; i64.sub` or `f64.neg`
- Result formatting: call `sno_output_int` / `sno_output_float`

**Gate:** `run_wasm_corpus_rung.sh rung4` → 5/5 pass · invariant cell 8 tests
**Commit:** `SW-2: M-SW-A02 — WASM arithmetic: E_ILIT/FLIT/ADD/SUB/MPY/DIV/MOD/NEG, 5/5`

---

#### M-SW-A03: CONCAT + STRING ASSIGN ⬜  `[Sprint SW-2]`
**Rung:** `corpus/crosscheck/rung3/` (3 tests: concat_strings, concat_numeric, concat_null)
**IR nodes:** `E_CONCAT`, `E_QLIT` (in value ctx), `E_VAR` (assign + read)
**Key emitter work:**
- `E_CONCAT` n-ary: emit children, call `sno_string_concat` for each pair
- `E_VAR` as lvalue: allocate WASM global per variable name (`(global $var_X (mut i32) i32.const 0)`)
- `E_VAR` as rvalue: `global.get $var_X`
- Numeric coerce for concat: int/float → string before concat

**Gate:** `run_wasm_corpus_rung.sh rung3` → 3/3 pass · invariant cell 11 tests
**Commit:** `SW-2: M-SW-A03 — WASM concat: E_CONCAT + E_VAR globals, 3/3`

---

#### M-SW-A04: VARIABLES + KEYWORDS ⬜  `[Sprint SW-3]`
**Rung:** `corpus/crosscheck/rung2/` (3 tests: indirect_ref, indirect_assign, indirect_array)
**IR nodes:** `E_VAR`, `E_KW` (&ALPHABET etc.), `E_INDR` ($-indirect), `E_ASSIGN` (var-to-var)
**Key emitter work:**
- `E_KW`: constant globals for &ALPHABET, &DIGITS, &UCASE, &LCASE, &NULL, &ANCHOR
- `E_INDR`: indirect lookup — `call $sno_var_get` with string key into variable table
- Variable table: linear scan over named globals (small programs, acceptable)

**Gate:** `run_wasm_corpus_rung.sh rung2` → 3/3 pass · invariant cell 14 tests
**Commit:** `SW-3: M-SW-A04 — WASM vars/keywords: E_VAR/KW/INDR, 3/3`

---

#### M-SW-A05: GOTO / BRANCHING ⬜  `[Sprint SW-3]`
**Rung:** `corpus/crosscheck/rung8/` (3 tests: replace, size, dupl)
**IR nodes:** `E_FNC` (REPLACE, SIZE, DUPL calls), STMT goto `:S/:F`
**Key emitter work:**
- SNOBOL4 `:S(label)/:F(label)` → WASM `if/else` block dispatch
- `E_FNC` builtins: REPLACE → `call $sno_replace`, SIZE → `call $sno_size`, DUPL → `call $sno_dupl`
- Each builtin is a WAT function in the runtime stub
- Failure value: WASM `i32.const 0` (null/fail sentinel), success `i32.const 1`

**Gate:** `run_wasm_corpus_rung.sh rung8` → 3/3 pass · invariant cell 17 tests
**Commit:** `SW-3: M-SW-A05 — WASM goto/builtins: :S/:F dispatch + REPLACE/SIZE/DUPL, 3/3`

---

#### M-SW-A06: CONVERT + TYPE PREDICATES ⬜  `[Sprint SW-3]`
**Rung:** `corpus/crosscheck/rung9/` (5 tests: convert, datatype, num_pred, integer_pred, lgt)
**IR nodes:** `E_FNC` (CONVERT, DATATYPE, INTEGER, LGT, EQ/NE/LT/GT/LE/GE)
**Key emitter work:**
- CONVERT: string↔int↔real coercions via WAT helpers
- DATATYPE: tag inspection (string/integer/real/pattern)
- Numeric predicates: LT/GT/LE/GE/EQ/NE as WASM `i64.lt_s` etc.
- LGT: string comparison via byte-by-byte loop

**Gate:** `run_wasm_corpus_rung.sh rung9` → 5/5 pass · invariant cell 22 tests
**Commit:** `SW-3: M-SW-A06 — WASM type/convert: CONVERT/DATATYPE/predicates, 5/5`

---

### Partition B — Pattern Primitives / Byrd Boxes (Sprint SW-4 – SW-5)

**This is the core of the session.** Each milestone introduces one Byrd-box IR node.
The four-port α/β/γ/ω wiring becomes four WAT functions per node.
`byrd_box.py` `genc()` is the structural oracle for every case.

Corpus: **existing** `corpus/crosscheck/rung10/` (functions/recursion — exercises pattern match).
New rungs: `corpus/crosscheck/rungW01/` through `rungW06/` — new SNOBOL4 pattern tests,
flat layout: `.sno` + `.ref` (CSNOBOL4 2.3.3) + `.s` + `.j` + `.il` + `.wat` all in same dir.

---

#### M-SW-B01: PATTERN LIT ⬜  `[Sprint SW-4]`
**Rung:** `corpus/crosscheck/rungW01/` (3 new tests)
**Programs:** `W01_pat_lit_basic.sno`, `W01_pat_lit_anchor.sno`, `W01_pat_lit_fail.sno`
**IR nodes:** `E_QLIT` in pattern context (literal string match), `E_MATCH` (subject ? pattern)
**Byrd-box shape (4 WAT functions per node):**
```wat
(func $lit_α (param $cursor i32) (result i32)   ;; α = try match
  ;; compare subject[cursor..] against literal
  ;; succeed: return_call $continuation_γ with new cursor
  ;; fail:    return_call $caller_β)
(func $lit_β  ...)  ;; retry — for LIT, always fail (no backtrack)
(func $lit_γ  ...)  ;; success continuation (receives new cursor)
(func $lit_ω  ...)  ;; resume from parent (into β)
```
**Gate:** `run_wasm_corpus_rung.sh rungW01` → 3/3 pass · invariant cell 25 tests
**Commit:** `SW-4: M-SW-B01 — WASM Byrd LIT: E_QLIT pattern, 4-fn α/β/γ/ω, 3/3`

---

#### M-SW-B02: PATTERN SEQ ⬜  `[Sprint SW-4]`
**Rung:** `corpus/crosscheck/rungW02/` (3 new tests)
**Programs:** `W02_seq_basic.sno`, `W02_seq_nested.sno`, `W02_seq_fail_propagate.sno`
**IR nodes:** `E_SEQ` (goal-directed sequence)
**Byrd-box wiring:** `lα → lγ → rα → rγ → seq_γ` ; `rβ → lβ` (backtrack left on right-fail)
```wat
;; SEQ: left then right, backtrack left if right fails
(func $seq_α  ...  return_call $left_α)
(func $left_γ ...  return_call $right_α)   ;; left succeeded, try right
(func $right_β ...  return_call $left_β)   ;; right failed, retry left
(func $seq_γ  ...  ...)                    ;; both succeeded
```
**Gate:** `run_wasm_corpus_rung.sh rungW02` → 3/3 pass · invariant cell 28 tests
**Commit:** `SW-4: M-SW-B02 — WASM Byrd SEQ: E_SEQ lγ→rα/rβ→lβ wiring, 3/3`

---

#### M-SW-B03: PATTERN ALT ⬜  `[Sprint SW-4]`
**Rung:** `corpus/crosscheck/rungW03/` (3 new tests)
**Programs:** `W03_alt_basic.sno`, `W03_alt_second.sno`, `W03_alt_both_fail.sno`
**IR nodes:** `E_ALT` (alternation — try left, on fail try right)
**Byrd-box wiring:** `alt_α → left_α` ; `left_β → right_α` ; `right_β → alt_β`
**Gate:** `run_wasm_corpus_rung.sh rungW03` → 3/3 pass · invariant cell 31 tests
**Commit:** `SW-4: M-SW-B03 — WASM Byrd ALT: E_ALT left→right fallback, 3/3`

---

#### M-SW-B04: PATTERN ARBNO ⬜  `[Sprint SW-5]`
**Rung:** `corpus/crosscheck/rungW04/` (3 new tests)
**Programs:** `W04_arbno_basic.sno`, `W04_arbno_zero.sno`, `W04_arbno_backtrack.sno`
**IR nodes:** `E_ARBNO` (zero-or-more repetition)
**Key concern:** zero-advance guard — if inner pattern matches empty string, must not loop
**Byrd-box wiring:** cursor saved on entry; inner_β → restore + advance one; zero-advance check
**Gate:** `run_wasm_corpus_rung.sh rungW04` → 3/3 pass · invariant cell 34 tests
**Commit:** `SW-5: M-SW-B04 — WASM Byrd ARBNO: zero-advance guard, cursor stack, 3/3`

---

#### M-SW-B05: ANY / SPAN / BREAK ⬜  `[Sprint SW-5]`
**Rung:** `corpus/crosscheck/rungW05/` (5 new tests)
**Programs:** `W05_any.sno`, `W05_span.sno`, `W05_break.sno`, `W05_notany.sno`, `W05_breakx.sno`
**IR nodes:** `E_ANY`, `E_NOTANY`, `E_SPAN`, `E_BREAK`, `E_BREAKX`
**Key emitter work:** character-class membership test via WASM table or inline byte loop
All are cursor-advancing, no backtrack within single advance (except BREAKX)
**Gate:** `run_wasm_corpus_rung.sh rungW05` → 5/5 pass · invariant cell 39 tests
**Commit:** `SW-5: M-SW-B05 — WASM Byrd ANY/SPAN/BREAK/NOTANY/BREAKX, 5/5`

---

#### M-SW-B06: POS / RPOS / LEN / TAB ⬜  `[Sprint SW-5]`
**Rung:** `corpus/crosscheck/rungW06/` (4 new tests)
**Programs:** `W06_pos.sno`, `W06_rpos.sno`, `W06_len.sno`, `W06_tab.sno`
**IR nodes:** `E_POS`, `E_RPOS`, `E_LEN`, `E_TAB`, `E_RTAB`, `E_REM`
**Key emitter work:** cursor-assertion patterns — compare cursor value to constant or subject-length-offset
No cursor advance for POS/RPOS; fixed advance for LEN; absolute position for TAB
**Gate:** `run_wasm_corpus_rung.sh rungW06` → 4/4 pass · invariant cell 43 tests
**Commit:** `SW-5: M-SW-B06 — WASM Byrd POS/RPOS/LEN/TAB/RTAB/REM, 4/4`

---

### Partition C — Captures, Data Structures, Functions (Sprint SW-6 – SW-7)

---

#### M-SW-C01: CAPTURES ⬜  `[Sprint SW-6]`
**Rung:** `corpus/crosscheck/rungW07/` (5 new tests)
**Programs:** `W07_capt_cond.sno`, `W07_capt_imm.sno`, `W07_capt_cur.sno`, `W07_capt_chain.sno`, `W07_capt_fail.sno`
**IR nodes:** `E_CAPT_COND` (`.var`), `E_CAPT_IMM` (`$var`), `E_CAPT_CUR` (`@var`)
**Key concern:** conditional capture must not fire on backtrack through the node
WASM: capture value staged in local, committed only on γ-path; abandoned on β-path
**Gate:** `run_wasm_corpus_rung.sh rungW07` → 5/5 pass · invariant cell 48 tests
**Commit:** `SW-6: M-SW-C01 — WASM Byrd captures: ./$/@var conditional/immediate/cursor, 5/5`

---

#### M-SW-C02: DATA / ARRAY / TABLE ⬜  `[Sprint SW-6]`
**Rung:** `corpus/crosscheck/rung11/` (7 tests — existing corpus, free oracles)
**IR nodes:** `E_IDX` (subscript), `E_FNC` (ARRAY, TABLE, DATA, FIELD)
**Key emitter work:**
- WASM linear memory allocator for array/table entries
- `sno_array_get` / `sno_array_set` WAT functions
- TABLE: hash map in linear memory (open addressing, string keys)
- DATA: synthesizes constructor + field accessor functions
- Null-slot coerce: uninitialized slot → empty string (mirrors JVM null→"" rule)
**Gate:** `run_wasm_corpus_rung.sh rung11` → 7/7 pass · invariant cell 55 tests
**Commit:** `SW-6: M-SW-C02 — WASM DATA/ARRAY/TABLE: linear memory allocator, 7/7`

---

#### M-SW-C03: FUNCTIONS + RECURSION ⬜  `[Sprint SW-7]`
**Rung:** `corpus/crosscheck/rung10/` (9 tests — existing corpus, free oracles)
**IR nodes:** `E_FNC` (DEFINE, user-call), `E_ASSIGN` to function result, FRETURN/NRETURN
**Key emitter work:**
- DEFINE: emit new WAT function per user-defined SNOBOL4 function
- Call frame: save/restore local variables on a WASM linear-memory stack
- RETURN/FRETURN/NRETURN: return value vs null (fail) vs no-value
- Recursion: WASM supports mutual recursion natively via function table
**Gate:** `run_wasm_corpus_rung.sh rung10` → 9/9 pass · invariant cell 64 tests
**Commit:** `SW-7: M-SW-C03 — WASM functions/recursion: DEFINE + call frame + FRETURN, 9/9`

---

#### M-SW-PARITY: 106/106 ⬜  `[Sprint SW-7]`
**Goal:** SNOBOL4 WASM invariant cell matches x86 at 106/106.
**Work:** Run full crosscheck corpus; fix each failure in isolation.
Remaining gaps after C03 will be in: EVAL, OPSYN, APPLY, ARG/LOCAL,
FENCE/ABORT/SUCCEED builtins, SETEXIT, multi-file INPUT.
Each fix is a targeted patch to `emit_wasm.c` + one new corpus test.
**Gate:** `run_invariants.sh snobol4_wasm` → 106/106 ✅
**Commit:** `SW-7: M-SW-PARITY — SNOBOL4 × WASM 106/106 parity`

---

## Invariant Baseline (projected)

| After milestone | `snobol4_wasm` count |
|----------------|----------------------|
| M-SW-A01 | 3 |
| M-SW-A02 | 8 |
| M-SW-A03 | 11 |
| M-SW-A04 | 14 |
| M-SW-A05 | 17 |
| M-SW-A06 | 22 |
| M-SW-B01 | 25 |
| M-SW-B02 | 28 |
| M-SW-B03 | 31 |
| M-SW-B04 | 34 |
| M-SW-B05 | 39 |
| M-SW-B06 | 43 |
| M-SW-C01 | 48 |
| M-SW-C02 | 55 |
| M-SW-C03 | 64 |
| M-SW-PARITY | 106 |

---

## Known Future Work (post-parity, not SW-1 scope)

- **M-SW-BROWSER:** Package `.wasm` output + JS harness for browser tab execution
- **M-SW-WASI:** WASI-compatible runtime for `wasmtime` (command-line, no Node dependency)
- **M-SW-OPT:** 2nd-pass optimizer matching `byrd_box.py` pass-2 (fold constant TO-ranges etc.)
- **M-SW-ICON:** Icon × WASM (after SNOBOL4 parity — shares emit_wasm.c infrastructure)
- **M-SW-SNOCONE:** Snocone × WASM (after SNOBOL4 parity)

---

## Bootstrap (next session)

```bash
# Step 0 — clone (fresh environment)
for repo in .github one4all harness corpus; do
  git clone "https://TOKEN_SEE_LON@github.com/snobol4ever/${repo}.git"
done

# Step 1 — setup
FRONTEND=snobol4 BACKEND=wasm TOKEN=TOKEN_SEE_LON bash /home/claude/.github/SESSION_SETUP.sh

# Step 2 — gate
cd /home/claude/one4all
CORPUS=/home/claude/corpus bash test/run_emit_check.sh        # expect 738/0
CORPUS=/home/claude/corpus bash test/run_invariants.sh snobol4_wasm  # wasm session: own cell only

# Step 3 — read in order
tail -120 /home/claude/.github/SESSIONS_ARCHIVE.md
cat /home/claude/.github/RULES.md
cat /home/claude/.github/SESSION-snobol4-wasm.md   # this file — §NOW
```

---

*SESSION-snobol4-wasm.md — created SW-1, 2026-03-30, Claude Sonnet 4.6.*
*§NOW lives here. All session state updated at end of each SW session.*
