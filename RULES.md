# RULES.md — snobol4ever Working Rules

## ⛔ ABSOLUTE RULES (violations = rejection)

**⚡ ONE PRODUCER — THE TEMPLATE-ONLY EMISSION FACT RULE.** Not one single x86 instruction — binary OR text — is emitted anywhere except inside a template function keyed to a BB, SM, or XA opcode. A "template function" lives in `src/emitter/BB_templates/`, `src/emitter/SM_templates/`, or `src/emitter/XA_templates/`, is named `bb_<kind>` / `sm_<opcode>` / `xa_<kind>`, and is reached ONLY through the `emit_core.c` dispatch switch (`case BB_FOO: bb_foo(nd);`). Every byte of machine code the project produces — for `--run` (mode 3, in-proc) AND `--compile` (mode 4, standalone) — comes from these template functions via the shared `emit_core.c` serializer sink (`bb_emit_byte`/`bb_emit_u32`/`ef_b*`) or its TEXT equivalent. There is exactly ONE x86 producer. FORBIDDEN anywhere outside a template function: raw opcode bytes (`\x48`, `seg_byte(SEG_CODE,…)`, `SL_B`, `bb_emit_byte` called directly), assembled mnemonics in a non-template string, per-opcode `switch` emitters (`sl_emit_one`, `emit_standard_blob`), and bespoke byte-emitter families (`sl_*`/`SL_*`/`bake_blob_call_*`). A second producer ALWAYS drifts from the first (FACT 4). If you find machine-code emission outside a template — DELETE IT and route the opcode through its template. The in-proc runner (mode 3) may ONLY load template-produced bytes into a PROT_EXEC buffer and jump in; it emits nothing itself. COMPLETION TEST: `grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob' src/` outside `*_templates/` and `emit_core.c` (the sanctioned sink) == 0.

**NO C BYRD-BOX FUNCTIONS.** A C Byrd box is any `DESCR_t foo(void *zeta, int entry)` implementing α/β/γ/ω. ZERO permitted. All Byrd boxes are x86 assembly emitted by the emitter. Only `icn_bb_dcg` is exempt (infrastructure DCG driver). Write a C function like this → DELETE IT; implement as `IR_block_t` DCG in `ir_exec.c` + `lower_icn.c`.

**FOUR PORTS = FOUR ONE-CHARACTER GREEK NAMES. ALWAYS.** Every reference to a Byrd-box port — in struct fields, emitter C/C++ code, and in emitted assembly labels — must use the single Greek character name: `α` (alpha, fresh entry), `β` (beta, retry entry), `γ` (gamma, success exit), `ω` (omega, failure exit). No English synonyms (`succ`, `fail`, `back`, `retry`, `done`, `exit`) are permitted for port names anywhere. The `g_emit` struct fields are `lbl_γ`, `lbl_ω`, `lbl_β` (and `lbl_γ_p`, `lbl_ω_p`, `lbl_β_p`). Emitted TEXT labels are `.Lfoo<id>_β:`, `.Lfoo<id>_γ`, `.Lfoo<id>_ω`. Internal non-port loop labels may keep descriptive names.

**NO AST WALKING IN MODES 2/3/4.** `sm_interp_run`, `sm_jit_run`, and all `src/emitter/*.c` code may not dereference `tree_t*` — no `->t`, `->c[]`, `->n`, `->v`. Mode 1 is DELETED (CLI-3M-9, 2026-05-18). `--interp` = mode 2 (SM dispatch). Stub sites print `[NO-AST] <opcode>` and set `last_ok=0`. Fix: write fresh SM/BB lowering. Never restore the AST call.

**NO SM/BB WALKING AT RUNTIME IN MODES 3/4.** Modes 3 (`--run`, SB-LINEAR) and 4 (`--compile --target=x86`) run **native x86 only** at runtime. Their running code may not, at runtime, (a) index the SM array by program counter — no `g_jit_prog->instrs[STATE->pc]` opcode-dispatch loop, no per-opcode C handler (`h_*` trampoline in `sm_jit_interp.c`) — nor (b) traverse a `BB_t` graph in C — no `bb_exec_once` / `bb_exec_resume` / `bb_exec_node` / `bb_broker` reached from a mode-3/4 run path. Mode 3 = `sm_emit_linear` → `sm_run_linear` (enters the linear native blob). Mode 4 = the emitter walks SM/BB **at emit time** (that walk is REQUIRED and permitted) and then frees the graph via `stage2_free_bb_after_emit`; the emitted standalone binary holds no SM array or BB graph. The reference SM/BB walkers (`sm_interp_run`, `bb_exec_*`) are the **mode-2 (`--interp`) path only** — that walk is sanctioned there and nowhere else. Runtime stub sites in modes 3/4 print `[NO-SM-BB] <opcode>` and set `last_ok=0`. Fix: emit the opcode/port logic as inline x86 (SB-LINEAR `sl_emit_one` for mode 3; `bb_*.cpp` / `sm_*.cpp` templates for mode 4) — never call back into the C walker. **Documented temporary exception:** Prolog `--run` is routed through `sm_interp_run` (AGW-1c) until the `bb_pl_*.cpp` templates land (AGW-8..10); this is the *only* sanctioned mode-3 SM/BB-walk and must be deleted when the templates are complete. No new exceptions without a Lon directive recorded here.

**NO RESTORED DELETED INTERPRETER CODE.** `sno_engine.js` and pattern-interpreter sections of `sno_runtime.js` are gone forever. JS/JVM/NET/WASM emitters use Byrd-box factory functions only.

**SCRIP FOLLOWS SPITBOL SEMANTICS** for SNOBOL4 and Snocone. Divergences must be documented in this file. Icon/Prolog/Rebus/Raku follow their own native semantics.

**SCRIP IS CASE-SENSITIVE.** All six languages. No folding anywhere in `one4all`. Forbidden: `sno_fold_name`, `strcasecmp` on identifier paths, `tolower/toupper` in lookup, `--fold-case` flag, `&CASE` assignment. SPITBOL/CSNOBOL4 oracles are exempt.

**X86 ONLY FOR NOW.** BB and SM templates: implement `IS_X86` arms only. `IS_JVM / IS_JS / IS_NET / IS_WASM` arms stub out (return immediately). Do not write JVM/JS/NET/WASM arms until explicitly directed.

## Commit identity

```bash
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
```
Set in every repo at session start.

## Token — never on disk.

## Handoff sequence

1. Mark completed steps (`- [x]`) in Goal file
2. Update watermark (HEAD hash, pass counts, current step)
3. Update step in PLAN.md goals table
4. `git add -A && git commit -m "<description>"` each touched repo
5. `git pull --rebase && git push` — code repos first, `.github` last
6. Confirm: `git log origin/main --oneline -1` shows your hash

Emergency handoff: same, but note breakage in commit message; leave step `- [ ]`.

## Session setup

Run only what the Goal file's `## Session Setup` lists. Fallback: `REPO-one4all.md`.

## Session trigger phrases

| Lon says | Meaning |
|----------|---------|
| "here we go" | Session starting — run session start protocol |
| "perform hand off" | End of session — update, commit, push |
| "perform emergency hand off" | Same, note breakage |
| "grand master reorg" | HQ system work |

## Oracles

**SPITBOL x64** — primary. `git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64`. Binary ships in repo. Invoke: `/home/claude/x64/bin/sbl -b file.sno`. Always `-bf` for case-sensitive mode. `SETL4PATH` for include path.

**CSNOBOL4** — RETIRED except for Silly goals. `/home/claude/csnobol4/snobol4 -bf file.sno`.

Never patch oracle binaries. Edit source, regenerate.

## Testing

- Run goal's gate before every commit. No broken commits.
- Parallel gates: run independent scripts with `&` + `wait`.
- Flaky gates: median of 3–5 runs, not single runs.
- `timeout 8s` for unit/smoke; `timeout 30s` for corpus runners.

## Scripts

All scripts in `one4all/scripts/`. Naming: `install_` / `build_` / `regenerate_` / `run_` / `test_` / `util_`. Every script: paths from `$0`, `< /dev/null` on scrip calls, `timeout N`, corpus path `/home/claude/corpus` (SKIP if missing).

## C code style

- **200-char line max.** Zero blank lines. Separator lines: `/*---...---*/` minor, `/*===...===*/` major (each 200 chars).
- No inline comments. Block comments above function, after separator.
- `if (!p) return NULL;` one-liners fine. Braces omitted for single-statement bodies.
- One space around `*` everywhere. `snake_case` new functions. `IR_` prefix for IR subsystem.

## Naming conventions

| Origin | Convention | Example |
|--------|-----------|---------|
| SIL label → C fn | `NAME_fn` | `APPLY_fn` |
| New C struct/enum | `Xxxx_yyy` one-cap | `Invoke_entry` |
| New C fn | `snake_case` | `arena_init` |
| IR subsystem | `IR_` uppercase prefix | `IR_exec_once` |

## File rules

- One template file per BB kind (`BB_templates/` folder).
- **NO TEMPLATE CODE IN emit_core.c, emit_bb.c, OR ANY NON-TEMPLATE FILE.** All x86/JVM/JS/NET/WASM emission logic lives exclusively in `BB_templates/`, `SM_templates/`, or `XA_templates/`. `emit_core.c` contains only the dispatch switch (`case BB_FOO: bb_foo(nd); return 0;`). Violations: delete the inline code, move it to the correct template file, re-test.
- **Never emit `.include "bb_macros.s"` in generated `.s` output.** BB macros are inlined by the `MEDIUM_MACRO_DEF` pass; a `.include` would double-define them and cause assembler errors.
- No append-only accumulating files. Git log is the session record.
- No symlinks. No duplicate corpus source files (exception: self-contained demo folders).
- Never patch corpus `.sno`/`.inc` to work around runtime bugs — fix the runtime.
- No large reference files as project attachments.

## Debugging

Hardware watchpoints DO NOT work in this container. Use: C-source `__builtin_trap()` assertions, `mprotect()`, or `set can-use-hw-watchpoints 0` (slow). Never commit diagnostic patches.

## Snocone parser style

Non-terminal names mirror the frontend's `.l`/`.y` parse-function names. Token names mirror `TK_*` enum. IR node tags match `ast_dump` output. No `goto` in new `parser_<lang>.sc` files.

## DATATYPE case

SPITBOL x64 → lowercase. one4all / CSNOBOL4 / snobol4jvm → UPPERCASE. snobol4dotnet → lowercase. Do not modify without an explicit rung. Portable tests: derive from runtime, don't hardcode.

## SNOBOL4 pattern globals — always set both:
```snobol4
&ANCHOR = 0
&FULLSCAN = 1
```

## Permitted SPITBOL divergences
- DATATYPE case (see above; SN-27 will unify)
- Case sensitivity (`&CASE` is no-op in SCRIP)

## Known open divergences (bugs)
- REPLACE 2nd/3rd arg equal-length requirement (SN-REPLACE-EQ)

## Parallel frontend file ownership

| Path | Owner | Merge gate? |
|------|-------|-------------|
| `src/frontend/<lang>/` | that lang session | No |
| `src/runtime/interp/icn_runtime.c` | Icon | Yes |
| `src/runtime/interp/pl_runtime.c` | Prolog | Yes |
| `src/driver/interp.c`, `polyglot.c`, `scrip.c` | Shared | Yes |
| `src/ir/ir.h` | Shared | Yes |
| `src/runtime/x86/sm_lower.c`, `sm_interp.c`, `bb_broker.c` | Shared | Yes |

## Three-way diff for Silly sweep goals

All three simultaneously: `v311.sil` + `snobol4.c` + `src/silly/sil_*.c`. Two-way is wrong.

## Sync-step monitor

Instrumentation lives in C runtime only. User source never modified. Read only the last-agree and first-disagree records — bug lives between them.

## BB/SM deletion is total — zero residue

When any part of the BB or SM representation is deleted (freed, nulled, or dropped from a data
structure), the deletion MUST be 100% complete.  No byte, pointer, index, or reference to the
deleted object may survive anywhere in the process after the free call returns.  Specifically:

- **No dangling pointers.**  Every pointer to the freed object — in tables, globals, side-tables,
  caches, or on the stack — is set to NULL or overwritten before or immediately after the free.
- **No stale indices.**  Any integer index (e.g. `bb_table[i]`, `a[2].i`) that referred to the
  deleted slot is reset to -1 or the owning count field is zeroed so no code can re-derive the
  pointer.
- **No shadow copies.**  Side-tables, snapshots, or caches created to survive a partial free
  (e.g. `g_exec_stmt_bbs[]`) are FORBIDDEN.  If a structure must survive execution it must NOT
  be freed before execution.  Choose one: free early (before run) or free late (after run).
  Never split the object across two free calls with a live alias in between.
- **No partial frees without distinct lifetimes.**  "Free some but not all" at a single moment
  is FORBIDDEN.  However, BB and SM have genuinely distinct lifetimes in mode 3 (JIT): BB is
  consumed by SM_codegen (the emitter) and must be freed immediately after it returns;
  SM instrs are consumed by sm_jit_run (the runner) and must be freed immediately after it
  returns.  Use `stage2_free_bb_after_emit` then `stage2_free_sm_bb` in that order.
  Any other split — or any helper that frees a subset without a documented distinct lifetime
  — is FORBIDDEN.
- **Verification.**  After any free of BB or SM data, ASAN (`detect_use_after_free=1`) must
  report zero errors on all smoke gates.  A smoke gate that passes without ASAN is not
  sufficient proof of correct deletion.
