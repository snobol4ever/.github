# RULES.md — snobol4ever Working Rules

## ⛔ ABSOLUTE RULES (violations = rejection)

**DO NOT READ BB-REVAMP-TRACKER.md.** Large, unrelated. Never open it.

**DO NOT READ UNRELATED GOAL FILES.** Read only the goal Lon names.

**TEMPLATE-ONLY EMISSION.** Every x86 instruction — BINARY and TEXT — produced ONLY inside `x86(...)` encoder internals (`x86_asm.h`). Templates speak ONLY `x86(...)`, emit ZERO binary anywhere. If an instruction has no `x86()` form, ADD the encoder to `x86_asm.h` — never hand-encode in a template. Raw-byte producers (`x86_Lrec`, `x86_Jrec`, `x86_b1(`, `bytes(`, `u8(`, `u32le`, `u64le`) PRIVATE to `x86_asm.h`; sole legacy exception: `bomb_bytes` in `emit_str.cpp`. FORBIDDEN outside templates and `emit_core.c`: `seg_byte(SEG_CODE`, `SL_B(`, `sl_emit_one`, `emit_standard_blob`, `bake_blob_call`. Completion tests: (a) grep above == 0 outside templates/emit_core.c; (b) `scripts/test_gate_template_medium_invisible.sh --strict` green; (c) `bytes\(|u32le|u64le|u8\(` in `src/emitter/` outside `x86_asm.h` matches only `bomb_bytes`.

**BOTH-MEDIUM MANDATORY.** Every code-outputting function MUST produce correct output for BOTH TEXT and BINARY. `x86("ins1")`, `x86("ins2")`, `x86("ins3")`, `x86("Lins1")`, `x86("Lins2")` DELETED (2c81233). Any function gating output on `MEDIUM_TEXT` or `MEDIUM_BINARY` is an absolute violation. Completion: `grep -rn '"ins[0-9]\+\"\|"Lins[0-9]\+\"' src/emitter/` == 0.

**NO MEDIUM_* IN TEMPLATES.** Zero `MEDIUM_*` in any `bb_*.cpp`. `x86("label")` and `x86("comment")` are medium-complete in `x86_asm.h`. All asm-producing free functions (`x86_reg_disp32_load64`, `x86_frame_store64`, `x86_frame_lea`, `x86_ro_load_q`, `x86_ro_seal_str`, etc.) move INSIDE `x86()` dispatch. Completion: (a) `grep -rn 'MEDIUM_' src/emitter/BB_templates/` == 0; (b) `grep -rnE 'x86_(frame|ro|reg)_[a-z0-9_]*\(' src/emitter/BB_templates/` == 0.

**ICON STACKLESS ONE-REGISTER FRAME.** Every Icon BB graph stackless: no `g_vstack`/`vstack`/`rt_push_*`/`rt_pop_*`/`r12`-as-TOS. All per-box RW storage in ONE per-sequence LOCAL frame `[reg+off]`. Completion: `scripts/test_gate_icn_no_stack.sh` == 0; `scripts/test_gate_icn_one_reg_frame.sh` == 0.

**ICON READ-ONLY LOCALS ARE IP-RELATIVE.** Per-box compile-time constants live sealed adjacent to blob, reached `[rip+disp]`. RW locals use `[reg+off]`.

**NO C BYRD-BOX FUNCTIONS.** Zero `DESCR_t foo(void*, int entry)`. Only `icn_bb_dcg` exempt.

**FOUR PORTS = FOUR GREEK NAMES ALWAYS.** `α` `β` `γ` `ω`. No English synonyms.

**NO AST WALKING IN MODES 2/3/4.** No `->t`, `->c[]`, `->n`, `->v` in SM/emitter code.

**NO SM/BB WALKING AT RUNTIME IN MODES 3/4.** Exception: Prolog `--run` via `sm_interp_run` until bb_pl_*.cpp templates land.

**SCRIP FOLLOWS SPITBOL SEMANTICS** for SNOBOL4/Snocone. **SCRIP IS CASE-SENSITIVE.**

**X86 ONLY FOR NOW.** IS_JVM/IS_JS/IS_NET/IS_WASM arms stub out.

**ICON SM = ZERO OPCODES.** Completion: `SCRIP_ICN_BB=1 ./scrip --dump-sm prog.icn` → `count=0`.

**PEERS RULE.** BB_t stays LEAN. Operand-value refs go in `BB_graph_t.operand_aux` via `bb_operand_aux_set/get`. DO NOT add fields to BB_t.

**CONSULT CANONICAL SOURCES RULE.** For ANY new SM/BB or Icon feature: grep/read canonical procedures FIRST. Authority: `refs/jcon-master/tran/irgen.icn` and `refs/icon-master/src/runtime/*.r`. m2 oracle is a transcription, not truth.

## Commit identity
```bash
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
```

## Handoff sequence
1. DELETE completed steps from Goal file
2. Update watermark in Goal file only
3. Do NOT edit PLAN.md goals table on routine handoff
4. `git add -A && git commit -m "<description>"` each touched repo
5. `git pull --rebase && git push` — code repos first, `.github` last
6. Confirm: `git log origin/main --oneline -1` shows your hash

## Oracles
**SPITBOL x64:** `git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64`. Invoke: `/home/claude/x64/bin/sbl -b file.sno`.

## Testing
- Run goal's gate before every commit. No broken commits.
- `timeout 8s` unit/smoke; `timeout 30s` corpus runners.
- Scripts in `SCRIP/scripts/`; `< /dev/null` on scrip calls.

## C code style
- **200-char line max. Zero blank lines.**
- **EXACTLY ONE COMMENT:** the 200-char `/*` + dashes + `*/` separator between every function/major block; `/*===*/` (equals, 200 total) between larger sections. Nothing else — no block/inline comments, no `//`, no prose.
