# RULES.md — snobol4ever Working Rules

## ⛔ ABSOLUTE RULES (violations = rejection)

**MONITOR-FIRST BUG-FINDING (Lon, 2026-06-25).** Any divergence from oracle (FAIL, hang, wrong result, crash) is found with the **2-way IPC sync-step MONITOR** (`scripts/test_monitor_2way_sync_step_bin.sh <file>`; 3-way: `test_monitor_3way_sync_step_auto.sh` with `PARTICIPANTS="csn spl"|"spl scr"|"csn scr"`) — never by reading code, guessing, or print-scattering. THEOREM: the bug lives between the FIRST DIVERGENT trace event and the previous (last-agreeing) one. The hunt is mechanical: (1) monitor → first divergence (statement/label/line/variable named); (2) gdb breakpoint at the bracketed C site with a SPIN/IGNORE COUNTER (`ignore <bp> <N-1>` or `condition`; HW watchpoints DO NOT WORK in this container — use hit-counts + `CSN_NO_SEGV_HANDLER=1`/`SCRIP_NO_SEGV_HANDLER` clean-backtrace hooks); (3) single-step to the land mine; fix there; (4) re-run monitor, divergence must move past. Offline alternative: harness `probe.py` (&STLIMIT+&DUMP=2 replay bisect). **If the monitor is dark for the mode under test — OR blind to the divergence CLASS (e.g. stdout-only divergence with every trace event agreeing: exit 0 is then NOT exoneration) — reinstating/extending it (MON-RE / MON-CAP) comes first.** Before reading any code: run the cheapest discriminating experiment — nearest passing sibling vs the failing probe, made to swap paths where possible, and a diff of their emitted asm; an instruction byte-identical in the passing sibling is exonerated, and a passing sibling is NOT evidence an offset is right (CLIMB s23/s24 convictions).

**DO NOT READ BB-REVAMP-TRACKER.md.** Large, unrelated. Never open it.

**DO NOT READ UNRELATED GOAL FILES.** Read only the goal Lon names.

**TEMPLATE-ONLY EMISSION.** Every x86 instruction — BINARY and TEXT — produced ONLY inside `x86(...)` encoder internals (`x86_asm.h`). Templates speak ONLY `x86(...)`, emit ZERO binary. Missing instruction ⇒ ADD the encoder, never hand-encode. Raw-byte producers (`x86_Lrec`, `x86_Jrec`, `x86_b1(`, `bytes(`, `u8(`, `u32le`, `u64le`) PRIVATE to `x86_asm.h`; sole legacy exception `bomb_bytes` in `emit_str.cpp`. FORBIDDEN outside templates/emit_core.c: `seg_byte(SEG_CODE`, `SL_B(`, `sl_emit_one`, `emit_standard_blob`, `bake_blob_call`. Gates: greps == 0; `scripts/test_gate_template_medium_invisible.sh --strict` green.

**BOTH-MEDIUM MANDATORY.** Every code-outputting function correct for BOTH TEXT and BINARY. Any function gating output on `MEDIUM_TEXT`/`MEDIUM_BINARY` is a violation. Gate: `grep -rn '"ins[0-9]\+\"\|"Lins[0-9]\+\"' src/emitter/` == 0.

**NO MEDIUM_* IN TEMPLATES.** Zero `MEDIUM_*` in any `bb_*.cpp`; `x86("label")`/`x86("comment")` are medium-complete; asm-producing free helpers live INSIDE `x86()` dispatch. Gates: `grep -rn 'MEDIUM_' src/emitter/BB_templates/` == 0 and no `x86_(frame|ro|reg)_*(` in templates.

**ICON STACKLESS ONE-REGISTER FRAME.** No `g_vstack`/`rt_push_*`/`rt_pop_*`/r12-as-TOS in Icon graphs; all per-box RW in ONE local frame `[reg+off]`. Gates: `test_gate_icn_no_stack.sh` == 0; `test_gate_icn_one_reg_frame.sh` == 0. **ICON READ-ONLY LOCALS ARE IP-RELATIVE** (`[rip+disp]` sealed beside blob); RW uses `[reg+off]`.

**NO C BYRD-BOX FUNCTIONS.** Zero `DESCR_t foo(void*, int entry)`. Only `icn_bb_dcg` exempt.

**FOUR PORTS = FOUR GREEK NAMES ALWAYS.** `α` `β` `γ` `ω`. No English synonyms.

**NO AST WALKING IN MODES 2/3/4.** No `->t`, `->c[]`, `->n`, `->v` in SM/emitter code.

**NO SM/BB WALKING AT RUNTIME IN MODES 3/4.** Exception: Prolog `--run` via `sm_interp_run` until bb_pl_*.cpp lands.

**SCRIP FOLLOWS SPITBOL SEMANTICS** for SNOBOL4/Snocone. **SCRIP IS CASE-SENSITIVE.**

**X86 ONLY FOR NOW.** IS_JVM/IS_JS/IS_NET/IS_WASM arms stub out.

**ICON SM = ZERO OPCODES.** Gate: `SCRIP_ICN_BB=1 ./scrip --dump-sm prog.icn` → `count=0`.

**ICON SEMICOLON-REQUIRED — NO NEWLINE PROCESSING.** SCRIP Icon requires `;` between bare statements; the front-end does ZERO newline processing (newline = whitespace). icont-style Beginner/Ender insertion FORBIDDEN in `src/parser/icon/`. Prison: `scripts/test_gate_icn_semicolon_required.sh` (3 locks). Full FACT RULE in `GOAL-ICON-BB.md`.

**PEERS RULE.** BB_t/IR_t stays LEAN. Operand refs live in `IR_t.operands/n_operands` via `ir_operand_push` (`bb_operand_aux_*` DELETED, SCRIP `a3de01d2`). DO NOT add fields to BB_t.

**CONSULT CANONICAL SOURCES.** For any new SM/BB/Icon feature: grep/read canonical procedures FIRST. Authority: `refs/jcon-master/tran/irgen.icn` + `refs/icon-master/src/runtime/*.r`. `refs/` is gitignored and NOT auto-populated — each session sets it up (unzip supplied archives or clone upstream, symlink, verify `ls refs/...` before trusting).

## Commit identity
```bash
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
```

## ⛔ FACT RULE — "HANDOFF COMPLETE" REQUIRES A CONFIRMED PUSH (Lon, 2026-06-24)
The phrase "handoff complete" (or any terminal doneness claim) MUST NOT be spoken until `git push` has SUCCEEDED for EVERY touched repo. A local commit is NOT a handoff. Credential missing / push failed ⇒ handoff is **BLOCKED** — state it plainly, say what's needed, STOP. **THE STATUS LINE IS COMPUTED, NEVER TYPED:** the ONLY sanctioned source of "HANDOFF COMPLETE" is the verbatim stdout of `bash scripts/handoff_status.sh` (auto-discovers every repo with an origin remote; tree-clean + HEAD==origin + zero unpushed; exit 0 = COMPLETE, exit 1 = BLOCKED with reason). Paste its output verbatim; the handoff is done IFF the script says so.

## Handoff sequence
0. **UPDATE THE GOAL FILE'S `LIVE CURSOR` (next rung + watermark + last session). No cursor move = no handoff.**
1. DELETE completed steps from Goal file. 2. Update watermark in Goal file only. 3. Do NOT edit PLAN.md goals table on routine handoff.
4. **If the session touched codegen** (`emit.cpp`, `emit.h`, `src/templates/*.cpp`, `x86_asm.h`, `lower_snobol4.c`, or runtime sinks): run in order `bash scripts/util_regen_benchmark_s_artifacts.sh "<rung>"` · `util_regen_feature_s_artifacts.sh` (commits to SCRIP) · `util_regen_demo_s_artifacts.sh`. Each regenerates the mode-4 `.s` beside every `.sno`, committing only changed bytes. **`.s` = HONEST CURRENT compiler output, never a pinned golden** — bomb stubs commit as-is; never wire `.s` byte-identity into a gate. Icon emitter/lowerer touched ⇒ also `update_icon_bench_asm.sh` (DEMO+BENCHMARK corpora ONLY — ⛔ NEVER `corpus/programs/icon/` rung tests; the script refuses it). To know what the compiler emits, sweep the COMPILER, never the artifacts.
5. `git add -A && git commit` each touched repo. 6. `git pull --rebase && git push` — code repos first, `.github` last. **6b. ⛔ CREDENTIAL (Lon 2026-08-09): push needs a credential ⇒ ASK LON IN-CHAT AND WAIT — he supplies it EVERY session when asked.** Ending the session unpushed without having asked, or writing "push pending" into any doc or commit message (STALE-ORIENTATION a), is a protocol violation. Conviction: s19–s26 stranded eight sessions of MECH work and BUG-7 was re-derived from scratch. 7. Run `handoff_status.sh`, paste verbatim; done IFF it prints HANDOFF COMPLETE.

## Oracles
SPITBOL x64: `git clone https://github.com/snobol4ever/x64 /home/claude/x64`; invoke `/home/claude/x64/bin/sbl -b file.sno`.

## Testing
- Run goal's gate before every commit. No broken commits.
- `timeout 8s` unit/smoke; `timeout 30s` corpus runners.
- Scripts in `SCRIP/scripts/`; `< /dev/null` on scrip calls.

## C code style
- **200-char line max. Zero blank lines.**
- **EXACTLY ONE COMMENT:** the 200-char `/*`+dashes+`*/` separator between functions; `/*===*/` (200 equals) between sections. Nothing else.

## FACT RULES (each: rule + enforcement; shared LIMITATION at end)
- **NO LANGUAGE-IDENTITY GLOBALS PAST LOWER (2026-07-03):** no global naming the language may EXIST where EMITTER/TEMPLATES could reach it. Language is implicit in PARSER/LOWER; downstream dispatch is per IR KIND only. Enforcement: visibility (file-static in driver/parser/lower) + `scripts/test_gate_emit_no_lang.sh`.
- **NO LANGUAGE SENTINEL PAST FIRST DISPATCH (2026-07-03):** language is a variable ONLY at first dispatch (driver reads extension string from the closed list `.sno .icn .pl .sc .reb .raku .pas`). No LANG_* enums/defines, no `:lang` AST attr, no extension string passed into LOWER+, no language global. Shared helpers branch on WHAT differs (behavioral description), never a language name. Enforcement: `test_gate_emit_no_lang.sh` + `grep -rn 'LANG_\|:lang\|IR_LANG_' src/` → 0.
- **OPTIMIZER STAYS ON (2026-07-03):** `optimizer_run` sits between LOWER and EMITTER on every compile — the structural wall against emitter re-absorbing their jobs. `SCRIP_OPT=0` is emergency-only; nothing may depend on it.
- **TIME-BOXED EXPLORATION (2026-07-06):** open-ended reading is bounded by COMPUTED wall-clock (`date +%s` at start, diff every few rounds; default threshold 10 min unless changed aloud). Crossing = CHECK-IN (report, let the human decide), not auto-abort. Depth matches the ask.
- **STALE-ORIENTATION (2026-07-13 s47):** (a) NEVER write push status into a doc — `handoff_status.sh` is the only push truth (11 false "PUSH PENDING" banners voided s47). (b) THE HANDOFF MUST MOVE THE CURSOR — one `LIVE CURSOR` per goal file, top, updated every handoff; orientation trusts it, never PLAN.md's table (stale BY DESIGN under 3–4 parallel sessions; `git pull --rebase` at handoff + `handoff_status.sh` catch parallel pushes). (c) Newest session state at top; prune below the last ~3.
- **O2-DIRECTED-ONLY (Lon, 2026-07-22 s126):** no `-O2`/`-O1` on ANY build unless Lon directs it this session. Every perf number labeled with RT_OPT level. If directed: detached+polled build, verify worktree populated + `.so` mtime moved before/after.

LIMITATION (all rules above): a markdown rule cannot coerce compliance; it makes the correct thing cheap, visible, and checkable. The human reviewer is the enforcer — reject handoffs that violate them.
