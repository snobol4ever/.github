# RULES.md — snobol4ever Working Rules

## ✅ COMMIT AND PUSH FREELY — NO CONCURRENCY GATING (Lon, 2026-08-10)
**Any session may edit ANY file at ANY time and push whenever it has something worth saving.** No routed windows, no reserved files, no "not-concurrency-safe" rungs, no concurrent set, no waiting on another seat. Git merges; `git pull --rebase` before pushing and resolve normally. **Push mid-session, per rung — do not save it all for the handoff.** A pushed rung is never lost; an unpushed one routinely is (s9/s10 lost two sessions of RTCC work; s19–s26 stranded eight sessions and BUG-7 was re-derived from scratch). ⛔ **NEVER park work, defer a commit, or decline an edit on concurrency grounds.** If two seats touch one file, merge it. Semantic collisions (two seats claiming one register) are caught MECHANICALLY by the claim gates, not by scheduling.
Surviving, because they are about CORRECTNESS not scheduling: re-prove your goal's gate/watermark after a rebase; push code repos before `.github` so a FINDING never describes an unpushed tree; `handoff_status.sh` verbatim is the only push truth.

## ⛔ ABSOLUTE RULES (violations = rejection)

**ASM-DIFF-FIRST BUG-FINDING (Lon, 2026-08-17 s132, SUPERSEDES MONITOR-FIRST 2026-06-25).** MONITOR-FIRST is RETIRED as the mandated opening move. Reason, measured: the monitor's own env gate (`MONITOR_BIN`) forces GVA off and diverges optimizer behavior from the shipped build — s132 found and partly fixed this (dead_goto/branch_chain), but the deeper defect (GVA-off correctness itself, kept per Lon's ruling as the class routed through NV functions) means a monitor verdict is a verdict on a DIFFERENT program until every one of its differences from the shipped build is independently proven inert. On beauty specifically the monitor reported `Error 22` where the plain build reports `Parse Error` — a monitor artifact, not a beauty bug — and the session's real progress (localizing the `IR_MATCH_DEFER` bare-`[rsp]` mechanism) came entirely from the asm diff, not the monitor. New order: (1) **mint the smallest repro** (ablate the failing program toward a minimal witness; a passing sibling with one ingredient removed is worth more than a trace); (2) **diff the emitted `.s`** between the passing sibling and the failing witness (`--compile`, TEXT mode — human-readable, no gdb needed) — an instruction byte-identical across both is exonerated; look for the port/record-shape mismatch directly; (3) if the asm diff doesn't answer it, THEN gdb: breakpoint at the implicated C/template site with a SPIN/IGNORE COUNTER (`ignore <bp> <N-1>` or `condition`; HW watchpoints DO NOT WORK in this container — use hit-counts + `CSN_NO_SEGV_HANDLER=1`/`SCRIP_NO_SEGV_HANDLER` clean-backtrace hooks); single-step to the land mine. **The IPC sync-step MONITOR remains available and is not deprecated as a tool** — `scripts/test_monitor_2way_sync_step_bin.sh` / `test_monitor_3way_sync_step_auto.sh` — but reaching for it is a choice made when a witness genuinely needs multi-statement trace bracketing AND has been proven monitor-safe first (default-arm md5 unchanged under `MONITOR_BIN`), never the reflexive first step, and never trusted on a program (like beauty) that has not been individually proven monitor-safe.

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
0a. **PUSH IS NOT A HANDOFF-ONLY STEP.** Push as soon as a rung is buildable and green. The sequence below is what you do at session END; it is not permission to have waited.

0. **UPDATE THE GOAL FILE'S `LIVE CURSOR` (next rung + watermark + last session). No cursor move = no handoff.**
1. DELETE completed steps from Goal file. 2. Update watermark in Goal file only. 3. Do NOT edit PLAN.md goals table on routine handoff.
4. **If the session touched codegen** (`emit.cpp`, `emit.h`, `src/templates/*.cpp`, `x86_asm.h`, `lower_snobol4.c`, or runtime sinks): run in order `bash scripts/util_regen_benchmark_s_artifacts.sh "<rung>"` · `util_regen_feature_s_artifacts.sh` (commits to SCRIP) · `util_regen_demo_s_artifacts.sh`. Each regenerates the mode-4 `.s` beside every `.sno`, committing only changed bytes. **`.s` = HONEST CURRENT compiler output, never a pinned golden** — bomb stubs commit as-is; never wire `.s` byte-identity into a gate. Icon emitter/lowerer touched ⇒ also `update_icon_bench_asm.sh` (DEMO+BENCHMARK corpora ONLY — ⛔ NEVER `corpus/programs/icon/` rung tests; the script refuses it). To know what the compiler emits, sweep the COMPILER, never the artifacts.
5. `git add -A && git commit` each touched repo. 6. `git pull --rebase && git push` — code repos first, `.github` last. (You should already have pushed most of this mid-session.) **6b. ⛔ CREDENTIAL (Lon 2026-08-09): push needs a credential ⇒ ASK LON IN-CHAT AND WAIT — he supplies it EVERY session when asked.** **AMENDED 2026-08-19 (Lon in-chat, SSH ruling): on Lon's box the GNOME keyring SSH agent (`SSH_AUTH_SOCK=/run/user/1000/keyring/ssh`) holds the GitHub key from login onward — the three push repos ride SSH remotes and any LOCAL seat inherits the agent and pushes without asking; login after a reboot re-arms it automatically. The ask-in-chat law still binds any seat whose environment lacks the agent (fresh containers / cloud seats): test with `ssh -T -o BatchMode=yes git@github.com`.** Ending the session unpushed without having asked, or writing "push pending" into any doc or commit message (STALE-ORIENTATION a), is a protocol violation. Conviction: s19–s26 stranded eight sessions of MECH work and BUG-7 was re-derived from scratch. 7. Run `handoff_status.sh`, paste verbatim; done IFF it prints HANDOFF COMPLETE.

## Oracles
SPITBOL x64: `git clone https://github.com/snobol4ever/x64 /home/claude/x64`; invoke `/home/claude/x64/bin/sbl -b file.sno` (⛔ beauty.sno needs `-bf`; plain `-b` SIGSEGVs rc=139 after 34 lines — s122).

## Testing
- Run goal's gate before every commit. No broken commits.
- `timeout 8s` unit/smoke; `timeout 30s` corpus runners.
- Scripts in `SCRIP/scripts/`; `< /dev/null` on scrip calls.

## C code style
- **200-char line max. Zero blank lines.**
- **EXACTLY ONE COMMENT:** the 200-char `/*`+dashes+`*/` separator between functions; `/*===*/` (200 equals) between sections. Nothing else.

## FACT RULES (each: rule + enforcement; shared LIMITATION at end)
- **⛔⛔⛔ NO NEW GLOBAL VARIABLES WITHOUT LON'S EXPLICIT PERMISSION (Lon, 2026-08-13 in-chat):** no session creates ANY new global variable — file-scope mutable state, pinned VA slot, exported cell, parallel array, or equivalent — in ANY repo without FIRST asking Lon in-chat and receiving permission that session. Linkage/state ride registers (r10/r11 wires) and the stack. We do not do that here. Enforcement: diffs checked for new file-scope definitions; a commit adding one without a cited in-chat grant is REJECTED. Precedent: the g_pcall/g_pcall_wires/RT_AB_ANCHOR eradication (s55). THE ASK ITSELF MUST BE A BANNER: the requesting session displays the ask in-chat as a large unmissable ⛔ banner (proposed global name, type, owning file, purpose, why registers/the stack cannot carry it); a quiet or inline ask does not count as asking.
- **NO LANGUAGE-IDENTITY GLOBALS PAST LOWER (2026-07-03):** no global naming the language may EXIST where EMITTER/TEMPLATES could reach it. Language is implicit in PARSER/LOWER; downstream dispatch is per IR KIND only. Enforcement: visibility (file-static in driver/parser/lower) + `scripts/test_gate_emit_no_lang.sh`.
- **NO LANGUAGE SENTINEL PAST FIRST DISPATCH (2026-07-03):** language is a variable ONLY at first dispatch (driver reads extension string from the closed list `.sno .icn .pl .sc .reb .raku .pas`). No LANG_* enums/defines, no `:lang` AST attr, no extension string passed into LOWER+, no language global. Shared helpers branch on WHAT differs (behavioral description), never a language name. Enforcement: `test_gate_emit_no_lang.sh` + `grep -rn 'LANG_\|:lang\|IR_LANG_' src/` → 0.
- **OPTIMIZER STAYS ON (2026-07-03):** `optimizer_run` sits between LOWER and EMITTER on every compile — the structural wall against emitter re-absorbing their jobs. `SCRIP_OPT=0` is emergency-only; nothing may depend on it.
- **TIME-BOXED EXPLORATION (2026-07-06):** open-ended reading is bounded by COMPUTED wall-clock (`date +%s` at start, diff every few rounds; default threshold 10 min unless changed aloud). Crossing = CHECK-IN (report, let the human decide), not auto-abort. Depth matches the ask.
- **STALE-ORIENTATION (2026-07-13 s47):** (a) NEVER write push status into a doc — `handoff_status.sh` is the only push truth (11 false "PUSH PENDING" banners voided s47). (b) THE HANDOFF MUST MOVE THE CURSOR — one `LIVE CURSOR` per goal file, top, updated every handoff; orientation trusts it, never PLAN.md's table (stale BY DESIGN under 3–4 parallel sessions; `git pull --rebase` at handoff + `handoff_status.sh` catch parallel pushes). (c) Newest session state at top; prune below the last ~3.
- **O2-DIRECTED-ONLY (Lon, 2026-07-22 s126):** no `-O2`/`-O1` on ANY build unless Lon directs it this session. Every perf number labeled with RT_OPT level. If directed: detached+polled build, verify worktree populated + `.so` mtime moved before/after.

LIMITATION (all rules above): a markdown rule cannot coerce compliance; it makes the correct thing cheap, visible, and checkable. The human reviewer is the enforcer — reject handoffs that violate them.
