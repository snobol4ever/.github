# SESSION-icon-wasm.md — Icon × WASM (one4all) ⛔ INACTIVE — parked 2026-03-31, see MILESTONE_ARCHIVE.md

**Repo:** one4all · **Frontend:** Icon (JCON four-port model) · **Backend:** WebAssembly
**Session prefix:** `IW` · **Trigger:** "playing with ICON Programming Language" / "Icon × WASM" / "IW-session"
**Driver:** `scrip-cc -icn -wasm -o prog.wat prog.icn` → `wat2wasm --enable-tail-call prog.wat -o prog.wasm` → `node test/wasm/run_wasm.js prog.wasm`
**Oracle:** `icont` / `iconx` (standard Icon interpreter)
**Emitter files:**
  - `src/backend/emit_wasm.c`       ← shared (SNOBOL4 + Prolog + Icon shared nodes)
  - `src/backend/emit_wasm_icon.c`  ← Icon-specific ICN_* cases ← **main work file**
  - `src/backend/emit_wasm_icon.h`  ← public interface

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

## Subsystems

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| Icon language, IR nodes, four-port model | `MISC-ICON-JCON.md` | AST/IR questions, Byrd-box wiring |
| WASM backend architecture | `ARCHIVE-WASM-BACKEND.md` | encoding strategy, runtime layout, tail-call model |
| WASM SNOBOL4 session (sibling) | `SESSION-snobol4-wasm.md` | shared emit_wasm.c helpers |
| Icon x86 emitter (structural oracle) | `SESSION-icon-x64.md` | four-port wiring reference |

---

## §NOW — IW-12

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **ICON WASM** | IW-12 | one4all `ab0ac8f` · `.github` this commit | **IW-13**: M-IW-R01 rung02_proc_fact — E_EVERY exhaustion infinite loop |

**IW-12 completed:** Fixed NULL `wasm_out` in `emit_wasm_icon_file()` — 126 compile segfaults → 9 (rung36 parse gaps). Added dual-set_out contract to `emit_wasm.h`. Gate 981/4 ✅. Baseline: 0p/214f (9 compile, 124 output, 80 wat2wasm, 1 timeout).

**IW-13 first action:** `./scrip-cc -icn -wasm -o /tmp/fact.wat corpus/programs/icon/rung02_proc_fact.icn && cat /tmp/fact.wat` — trace the E_EVERY efail chain to find the infinite loop. The `emit_frame_push/pop` + `icn_proc_reg_*` infrastructure is already in place (IW-10). Fix the exhaustion path → expect `[run/timeout]` → `[pass]` or `[output]`.

---

## §BUILD

```bash
FRONTEND=icon BACKEND=wasm TOKEN=TOKEN_SEE_LON bash /home/claude/.github/SESSION_SETUP.sh
```

Installs: `gcc make curl unzip wabt(wat2wasm) node icont/iconx`
Skips:    `nasm libgc-dev java javac mono ilasm swipl`

---

## §TEST GATE (run every session, own cell only)

```bash
cd /home/claude/one4all
CORPUS=/home/claude/corpus bash test/run_emit_check.sh            # always — 719/19 baseline
CORPUS=/home/claude/corpus bash test/run_invariants.sh icon_wasm  # WASM ICON ONLY
```

Per-test manual verification:
```bash
./scrip-cc -icn -wasm -o /tmp/t.wat corpus/programs/icon/rung01_paper_mult.icn
wat2wasm --enable-tail-call /tmp/t.wat -o /tmp/t.wasm
node test/wasm/run_wasm.js /tmp/t.wasm
# expect: 1 2 2 4 3 6
```

---

## §MILESTONE TABLE (active only)

| Milestone | ICN nodes | Rung | Status |
|-----------|-----------|------|--------|
| M-IW-SCAFFOLD | all → stub-fail | build | ✅ IW-1 |
| M-IW-A01 | ICN_INT/VAR/ASSIGN/CALL(write)/PROC/RETURN/FAIL/TO/EVERY/ALT/arith/relops | rung01 5/6 | ✅ IW-2 |
| M-IW-A02 | ICN_STR + write(str) | rung01 6/6 | ✅ IW-4 |
| **M-IW-P01** | EXPR_t rewrite + `$icn_retcont` trampoline | rung02 add_proc ✅; fact/locals ❌ (need E_IF + vars) | 🔶 partial IW-8 |
| M-IW-P03 | ICN_SUSPEND | rung02 suspend | ❌ |
| M-IW-G01–G06 | ICN_TO/TO_BY/EVERY/ALT/BANG/LIMIT | rung01–14 | ❌ |
| M-IW-S01–S04 | ICN_CONCAT/strrelops/SIZE/NULL/SCAN | rung04–12 | ❌ |
| M-IW-C01–C04 | ICN_IF/WHILE/UNTIL/REPEAT/BREAK/AUGOP | rung07–10 | ❌ |
| M-IW-B01 | ICN_CALL(string builtins) | rung08 | ❌ |
| M-IW-D01–D05 | ICN_SUBSCRIPT/SECTION/LIST/TABLE/FIELD/CASE | rung16–33 | ❌ |
| M-IW-PARITY | icon_wasm ≥ icon_x86 baseline (94p/164f) | — | ❌ |

---

## §M-IW-V01 — Local variable table (next fix)

**Root cause:** `emit_wasm_icon_proc()` line 1355 chains last stmt to `"icn_prog_end"` for ALL procs. Non-main procs exit the program instead of returning to the call site's esucc.

**Fix:** Add `$icn_retcont (mut i32)` global + `(table funcref)` to module. Before `$iconN_docall`, call site sets `$icn_retcont` to its `esucc` table index. `emit_wasm_icon_proc()` chains non-main final stmt to `$icn_proc_NAME_retcont` which does `return_call_indirect` through `$icn_retcont`. Verified: `return_call_indirect` works with `--enable-tail-call`.

**Files:** `src/backend/emit_wasm_icon.c` — `emit_wasm_icon_globals()` + `emit_wasm_icon_proc()` + ICN_CALL user-proc handler (~line 1088).

---

## §KEY FILES

| File | Role |
|------|------|
| `src/backend/emit_wasm_icon.c` | **Main work file** — Icon ICN_* WAT emission |
| `src/backend/emit_wasm.c` | Shared WASM emitter (SNOBOL4/Prolog/Icon shared nodes) |
| `ByrdBox/test_icon-4.py` | Return-function Python = direct WAT structural blueprint |
| `jcon-master/tran/irgen.icn` | Authoritative four-port wiring per AST node |

---

## §SESSION START (every IW session)

```bash
# 1. Clone
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

*SESSION-icon-wasm.md — created IW-1 2026-03-30. Trimmed IW-7 2026-03-31. Updated IW-8 2026-03-31.*
