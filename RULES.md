# RULES.md — snobol4ever Working Rules

## ⛔ ABSOLUTE RULES (violations = rejection)

**TEMPLATE-ONLY EMISSION (FACT RULE).** Every byte of emitted x86 lives in a template function in `src/emitter/BB_templates/`, `SM_templates/`, or `XA_templates/`, reached only via `emit_core.c` dispatch. FORBIDDEN outside templates: `seg_byte(SEG_CODE`, `SL_B(`, `sl_emit_one`, `emit_standard_blob`, `bake_blob_call`. **ALSO FORBIDDEN OUTSIDE TEMPLATES:** any helper that returns x86 opcode bytes — `bytes()`, `u8()`, `u32le()`, `u64le()` may appear in `emit_str.cpp` ONLY inside `bomb_bytes` and `bb_emit_asm_result`; nowhere else outside `*_templates/` may construct an x86 byte sequence and return it for templates to splice in. If multiple templates need the same byte pattern, **duplicate the byte-producing code into each template file** — that duplication is the point. A shared `*_str` helper in `emit_str.cpp` that returns templated x86 bytes is the SAME violation as `emit_standard_blob` with extra steps. COMPLETION TEST: `grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob' src/` outside `*_templates/` and `emit_core.c` == 0; AND every match of `bytes\(|u32le|u64le|u8\(` in `src/emitter/` outside `*_templates/` must be inside `bomb_bytes` or `bb_emit_asm_result`.

**NO C BYRD-BOX FUNCTIONS.** Zero `DESCR_t foo(void*, int entry)`. Only `icn_bb_dcg` exempt.

**FOUR PORTS = FOUR GREEK NAMES ALWAYS.** `α` fresh-entry, `β` retry, `γ` success, `ω` failure. No English synonyms anywhere.

**NO AST WALKING IN MODES 2/3/4.** No `->t`, `->c[]`, `->n`, `->v` in SM/emitter code.

**NO SM/BB WALKING AT RUNTIME IN MODES 3/4.** No `bb_exec_once/resume/node` from mode-3/4 run path. Exception: Prolog `--run` via `sm_interp_run` until bb_pl_*.cpp templates land.

**SCRIP FOLLOWS SPITBOL SEMANTICS** for SNOBOL4/Snocone. **SCRIP IS CASE-SENSITIVE.**

**X86 ONLY FOR NOW.** IS_JVM/IS_JS/IS_NET/IS_WASM arms stub out.

**ICON SM = ZERO OPCODES.** When `SCRIP_ICN_BB=1` (Icon-BB path), an Icon program emits ZERO SM instructions. No `SM_BB_INVOKE`, no `SM_HALT`, no `SM_CALL_FN`, no anything. The driver detects Icon-BB and calls `bb_exec_once(main_bb_graph)` directly, bypassing `sm_interp_run` entirely. Completion test: `SCRIP_ICN_BB=1 ./scrip --dump-sm any_icon_program.icn` prints `; SM_sequence_t  count=0`. Icon has no use for the SM dispatch loop. See `GOAL-ICON-BB.md` for the canonical statement.

**PEERS RULE (HQ Invariant 17).** BB_t stays LEAN. Operand-value refs go in `BB_graph_t.operand_aux` sidecar via `bb_operand_aux_set/get`. DO NOT add fields to BB_t.

**CONSULT CANONICAL SOURCES (JCON + Icon) RULE.** For ANY new SM or BB development, or any new Icon feature work, the canonical uploaded sources are the authority — NOT memory, NOT the mode-2 oracle alone, NOT assumption. The references live at `refs/jcon-master/` (esp. `tran/irgen.icn` — the `ir_a_*` IR-generation procedures define control-flow/port topology: `ir_a_Every`, `ir_a_Limitation`, `ir_a_Call`, `ir_a_Alt`, …) and `refs/icon-master/src/runtime/*.r` (canonical builtin/runtime semantics: `fstranl.r` for find/upto/many/any/match/bal, `ocomp.r` for relops, `fscan.r` for scanning, etc.). You do NOT read the whole files every time — but EVERY TIME a question arises about how a feature should behave, what ports connect where, what the resume/backtrack topology is, or what a builtin's exact semantics are, you `grep`/read the relevant canonical procedure FIRST and ground the implementation in it. The mode-2 oracle (`bb_exec.c`) is a transcription, not the source of truth; when in doubt the canonical source wins. Assuming you know the answer without checking is the failure mode this rule exists to prevent: you do not know — verify against JCON/Icon.

## Commit identity
```bash
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
```

## Handoff sequence
1. Mark completed steps (`- [x]`) in Goal file
2. Update watermark (HEAD hash, pass counts, current step) **in the Goal file only — this is the single source of truth**
3. **Do NOT edit the PLAN.md goals table on routine handoff.** Each row is a permanent pointer to its Goal file; the live state lives in the Goal file. Touch PLAN.md only on a `grand master reorg` (add/remove a goal, change a file path).
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
