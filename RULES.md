# RULES.md — snobol4ever Working Rules

## ⛔ ABSOLUTE RULES (violations = rejection)

**TEMPLATE-ONLY EMISSION (FACT RULE).** Every byte of emitted x86 lives in a template function in `src/emitter/BB_templates/`, `SM_templates/`, or `XA_templates/`, reached only via `emit_core.c` dispatch. FORBIDDEN outside templates: `seg_byte(SEG_CODE`, `SL_B(`, `sl_emit_one`, `emit_standard_blob`, `bake_blob_call`. COMPLETION TEST: `grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob' src/` outside `*_templates/` and `emit_core.c` == 0.

**NO C BYRD-BOX FUNCTIONS.** Zero `DESCR_t foo(void*, int entry)`. Only `icn_bb_dcg` exempt.

**FOUR PORTS = FOUR GREEK NAMES ALWAYS.** `α` fresh-entry, `β` retry, `γ` success, `ω` failure. No English synonyms anywhere.

**NO AST WALKING IN MODES 2/3/4.** No `->t`, `->c[]`, `->n`, `->v` in SM/emitter code.

**NO SM/BB WALKING AT RUNTIME IN MODES 3/4.** No `bb_exec_once/resume/node` from mode-3/4 run path. Exception: Prolog `--run` via `sm_interp_run` until bb_pl_*.cpp templates land.

**SCRIP FOLLOWS SPITBOL SEMANTICS** for SNOBOL4/Snocone. **SCRIP IS CASE-SENSITIVE.**

**X86 ONLY FOR NOW.** IS_JVM/IS_JS/IS_NET/IS_WASM arms stub out.

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
