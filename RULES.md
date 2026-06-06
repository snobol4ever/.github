# RULES.md — snobol4ever Working Rules

## ⛔ ABSOLUTE RULES (violations = rejection)

**TEMPLATE-ONLY EMISSION (FACT RULE).** Every byte of emitted x86 lives in a template fn in `src/emitter/{BB,SM,XA}_templates/`, reached only via `emit_core.c` dispatch. FORBIDDEN outside templates: `seg_byte(SEG_CODE`, `SL_B(`, `sl_emit_one`, `emit_standard_blob`, `bake_blob_call`; and any helper returning x86 opcode bytes — `bytes()/u8()/u32le()/u64le()` may appear in `emit_str.cpp` ONLY inside `bomb_bytes` and `bb_emit_asm_result`. If multiple templates need the same byte pattern, DUPLICATE it into each template (the duplication is the point); a shared `*_str` helper returning templated bytes is the same violation with extra steps. COMPLETION TEST: `grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob' src/` outside `*_templates/`+`emit_core.c` == 0; every `bytes\(|u32le|u64le|u8\(` match in `src/emitter/` outside `*_templates/` is inside `bomb_bytes`/`bb_emit_asm_result`.

**ICON STACKLESS ONE-REGISTER FRAME (FACT RULE).** Every Icon BB graph — flat-wired AND brokered — is stackless: no `g_vstack`/`vstack`/`rt_push_*`/`rt_pop_*`/`r12`-as-TOS in any form. All per-box RW runtime storage (value, counter, state, cursor, backtrack arenas) lives in ONE per-sequence LOCAL frame, addressed register-relative `[reg + emit_time_offset]` through the BB-frame register (set once at sequence entry; distinct from broker `r10` and SM `r13`). Consumers read producers' slots by offset in the SAME frame (the ζ model of `test_sno_1/2/3.c`). FORBIDDEN: threading values via any stack; absolute `movabs … &pBB->value|counter|state` slot addressing (breaks mode-4 relocatability). COMPLETION TESTS: `scripts/test_gate_icn_no_stack.sh` == 0; `scripts/test_gate_icn_one_reg_frame.sh` == 0.

**ICON READ-ONLY LOCALS ARE IP-RELATIVE (FACT RULE).** Per-box compile-time constants (literal int/real/string/cset, fixed bounds, op codes) live SEALED adjacent to the box BLOB and are reached `[rip+disp]` (emit-time `disp`) — never stacked, never `movabs`-absolute. Only RW locals use the one-register frame `[reg+off]`. So every Icon value ref is exactly: (RO) `[rip+disp]` or (RW) `[reg+off]`.

**NO C BYRD-BOX FUNCTIONS.** Zero `DESCR_t foo(void*, int entry)`. Only `icn_bb_dcg` exempt.

**FOUR PORTS = FOUR GREEK NAMES ALWAYS.** `α` fresh-entry, `β` retry, `γ` success, `ω` failure. No English synonyms anywhere.

**NO AST WALKING IN MODES 2/3/4.** No `->t`, `->c[]`, `->n`, `->v` in SM/emitter code.

**NO SM/BB WALKING AT RUNTIME IN MODES 3/4.** No `bb_exec_once/resume/node` from the mode-3/4 run path. Exception: Prolog `--run` via `sm_interp_run` until bb_pl_*.cpp templates land.

**SCRIP FOLLOWS SPITBOL SEMANTICS** for SNOBOL4/Snocone. **SCRIP IS CASE-SENSITIVE.**

**X86 ONLY FOR NOW.** IS_JVM/IS_JS/IS_NET/IS_WASM arms stub out.

**ICON SM = ZERO OPCODES.** With `SCRIP_ICN_BB=1` an Icon program emits ZERO SM instructions; the driver detects Icon-BB and calls `bb_exec_once(main_bb_graph)` directly, bypassing `sm_interp_run`. Completion test: `SCRIP_ICN_BB=1 ./scrip --dump-sm prog.icn` prints `; SM_sequence_t  count=0`. See `GOAL-ICON-BB.md`.

**PEERS RULE (HQ Invariant 17).** BB_t stays LEAN. Operand-value refs go in `BB_graph_t.operand_aux` via `bb_operand_aux_set/get`. DO NOT add fields to BB_t.

**CONSULT CANONICAL SOURCES (JCON + Icon) RULE.** For ANY new SM/BB or Icon feature work, the canonical sources are the authority — NOT memory, NOT the mode-2 oracle, NOT assumption. EVERY TIME a question arises about behavior, port topology, resume/backtrack wiring, or builtin semantics: grep/read the relevant canonical procedure FIRST. Authority: `refs/jcon-master/tran/irgen.icn` (the `ir_a_*` procedures define control-flow/ports; upstream **https://github.com/proebsting/jcon**) and `refs/icon-master/src/runtime/*.r` (`fstranl.r` find/upto/many/any/match/bal, `ocomp.r` relops, `fscan.r` scanning; upstream **https://github.com/gtownsend/icon**). Restore absent refs via `git clone <upstream> refs/<name>-master`. The m2 oracle (`bb_exec.c`) is a transcription, not truth; when in doubt the canonical source wins. You do not know until you check.

## Commit identity
```bash
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
```

## Handoff sequence
1. DELETE completed steps from the Goal file (git history preserves them; Lon directive 2026-06-06)
2. Update watermark **in the Goal file only — the single source of truth**
3. Do NOT edit the PLAN.md goals table on routine handoff; touch PLAN.md only on a `grand master reorg`
4. `git add -A && git commit -m "<description>"` each touched repo
5. `git pull --rebase && git push` — code repos first, `.github` last
6. Confirm: `git log origin/main --oneline -1` shows your hash

## Oracles
**SPITBOL x64:** `git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64`. Invoke: `/home/claude/x64/bin/sbl -b file.sno`.

## Testing
- Run the goal's gate before every commit. No broken commits.
- `timeout 8s` unit/smoke; `timeout 30s` corpus runners.
- Scripts in `SCRIP/scripts/`; paths from `$0`; `< /dev/null` on scrip calls.

## C code style
- **200-char line max. Zero blank lines.**
- **EXACTLY ONE COMMENT EXISTS:** the 120-char `/*` + dashes + `*/` LINE-BREAK separator between every function/major block; `/*=====*/` (equals, 120 chars) between larger sections. Nothing else — no block/inline comments, no `//`, no prose. (Lon directive 2026-06-02.)
