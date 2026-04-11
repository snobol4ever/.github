# SESSION-prolog-wasm.md — Prolog × WASM (one4all) ⛔ INACTIVE — parked 2026-03-31, see MILESTONE_ARCHIVE.md

**Repo:** one4all · **Frontend:** Prolog · **Backend:** WebAssembly (wat2wasm + Node.js)
**Session prefix:** `PW` · **Trigger:** "Prolog frontend with WASM backend"
**Driver:** `scrip-cc -pl -wasm foo.pl -o foo.wat` → `wat2wasm --enable-tail-call foo.wat -o foo.wasm` → `node test/wasm/run_wasm.js foo.wasm`
**Oracle:** `swipl foo.pl` (SWI-Prolog)
**Deep reference:** `ARCHIVE-WASM-BACKEND.md` · `PARSER-PROLOG.md` · `INTERP-JVM.md` (Byrd-box wiring)

---

## Subsystems

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| Prolog language, IR nodes | `PARSER-PROLOG.md` | parser/AST questions |
| WASM backend architecture | `ARCHIVE-WASM-BACKEND.md` | encoding strategy, runtime layout, tail-call model |
| WASM SNOBOL4 session (sibling) | `SESSION-snobol4-wasm.md` | shared emit_wasm.c helpers |
| Prolog JVM (structural oracle) | `SESSION-prolog-jvm.md` | Byrd-box clause dispatch reference |
| x64 Prolog emitter (structural oracle) | `ARCHIVE-PROLOG-X64-HISTORY.md` | four-port wiring notes |

---

## §NOW — PW-12 (end of session)

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Prolog WASM** | PW-12 | `443dae2` one4all · `.github` this commit | **M-PW-B01** — choice-point stack in pl_runtime.wat → rung05 `a\nb\nc` |

**Status:** rung01 ✅ rung02 ✅ rung03 ✅ rung04 ✅ rung05 ❌ (outputs `a\nb`, needs CP stack)
**GT infrastructure** (loop+flag+_call) committed and working for flat predicates.
**Recursive predicates** require choice-point stack — see SESSIONS_ARCHIVE PW-12 for full design.

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
