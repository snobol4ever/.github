# RULES.md — snobol4ever Working Rules

## ⛔ ABSOLUTE RULES (violations = rejection)

**NO C BYRD-BOX FUNCTIONS.** A C Byrd box is any `DESCR_t foo(void *zeta, int entry)` implementing α/β/γ/ω. ZERO permitted. All Byrd boxes are x86 assembly emitted by the emitter. Only `icn_bb_dcg` is exempt (infrastructure DCG driver). Write a C function like this → DELETE IT; implement as `IR_block_t` DCG in `ir_exec.c` + `lower_icn.c`.

**NO AST WALKING IN MODES 2/3/4.** `sm_interp_run`, `sm_jit_run`, and all `src/emitter/*.c` code may not dereference `tree_t*` — no `->t`, `->c[]`, `->n`, `->v`. Mode 1 is DELETED (CLI-3M-9, 2026-05-18). `--interp` = mode 2 (SM dispatch). Stub sites print `[NO-AST] <opcode>` and set `last_ok=0`. Fix: write fresh SM/BB lowering. Never restore the AST call.

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
