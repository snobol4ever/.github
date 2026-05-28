# RULES.md — snobol4ever Working Rules

## ⛔ ABSOLUTE RULES (violations = rejection)

**TEMPLATE-ONLY EMISSION (FACT RULE).** Every byte of emitted x86 lives in a template function in `src/emitter/BB_templates/`, `SM_templates/`, or `XA_templates/`, reached only via `emit_core.c` dispatch. FORBIDDEN outside templates: `seg_byte(SEG_CODE`, `SL_B(`, `sl_emit_one`, `emit_standard_blob`, `bake_blob_call`. **ALSO FORBIDDEN OUTSIDE TEMPLATES:** any helper that returns x86 opcode bytes — `bytes()`, `u8()`, `u32le()`, `u64le()` may appear in `emit_str.cpp` ONLY inside `bomb_bytes` and `bb_emit_asm_result`; nowhere else outside `*_templates/` may construct an x86 byte sequence and return it for templates to splice in. If multiple templates need the same byte pattern, **duplicate the byte-producing code into each template file** — that duplication is the point. A shared `*_str` helper in `emit_str.cpp` that returns templated x86 bytes is the SAME violation as `emit_standard_blob` with extra steps. COMPLETION TEST: `grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob' src/` outside `*_templates/` and `emit_core.c` == 0; AND every match of `bytes\(|u32le|u64le|u8\(` in `src/emitter/` outside `*_templates/` must be inside `bomb_bytes` or `bb_emit_asm_result`.

**NO C BYRD-BOX FUNCTIONS.** Zero `DESCR_t foo(void*, int entry)`. Only `icn_bb_dcg` exempt.

**FOUR PORTS = FOUR GREEK NAMES ALWAYS.** `α` fresh-entry, `β` retry, `γ` success, `ω` failure. No English synonyms anywhere.

**NO AST WALKING IN MODES 2/3/4.** No `->t`, `->c[]`, `->n`, `->v` in SM/emitter code.

**NO SM/BB WALKING AT RUNTIME IN MODES 3/4.** No `bb_exec_once/resume/node` from mode-3/4 run path. Exception: Prolog `--run` via `sm_interp_run` until bb_pl_*.cpp templates land.

**SCRIP FOLLOWS SPITBOL SEMANTICS** for SNOBOL4/Snocone. **SCRIP IS CASE-SENSITIVE.**

**X86 ONLY FOR NOW.** IS_JVM/IS_JS/IS_NET/IS_WASM arms stub out.

**ICON SM = TWO OPCODES ONLY.** When `SCRIP_ICN_BB=1` (Icon-BB path), an Icon program's SM stream may contain ONLY `SM_BB_INVOKE` and `SM_HALT`. Any other SM opcode emitted by the Icon path is a violation. The entire Icon program is one connected port-graph rooted at main's BB graph; the SM around it is a two-op boot. See `GOAL-ICON-BB.md` for the canonical statement.

**PEERS RULE (HQ Invariant 17).** BB_t stays LEAN. Operand-value refs go in `BB_graph_t.operand_aux` sidecar via `bb_operand_aux_set/get`. DO NOT add fields to BB_t.

## Commit identity
```bash
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
```

## Handoff sequence
1. Mark completed steps (`- [x]`) in Goal file
2. Update watermark (HEAD hash, pass counts, current step)
3. Update step in PLAN.md goals table
4. `git add -A && git commit -m "<description>"` each touched repo
5. `git pull --rebase && git push` — code repos first, `.github` last
6. Confirm: `git log origin/main --oneline -1` shows your hash

## Oracles
**SPITBOL x64:** `git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64`. Invoke: `/home/claude/x64/bin/sbl -b file.sno`.

## Testing
- Run goal's gate before every commit. No broken commits.
- `timeout 8s` unit/smoke; `timeout 30s` corpus runners.
- Scripts in `one4all/scripts/`. Every script: paths from `$0`, `< /dev/null` on scrip calls.

## C code style
- **200-char line max.** Zero blank lines. Separators: `/*---*/` minor, `/*===*/` major (200 chars).
- No inline comments. Block comments above function, after separator.
