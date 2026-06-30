# RULES.md — snobol4ever Working Rules

## ⛔ ABSOLUTE RULES (violations = rejection)

**MONITOR-FIRST BUG-FINDING — ALWAYS USE THE MONITOR TO FIND THE BUG (Lon directive, 2026-06-25).** When ANY program diverges from its oracle (a crosscheck FAIL, a demo hang, a wrong result, a crash), the bug is NOT hunted by reading code, guessing, or scattering print statements. The bug is FOUND with the **2-way IPC sync-step MONITOR** (`scripts/test_monitor_2way_sync_step_bin.sh <file>` → `test_monitor_3way_sync_step_auto.sh` with `PARTICIPANTS="csn spl"` or `"spl scr"`/`"csn scr"`), which compares SCRIP against SPITBOL/CSNOBOL4 **event-by-event over a synchronous binary wire** and reports the **FIRST DIVERGENCE** with a source-line table. THE THEOREM THAT MAKES THIS WORK: once the monitor reports the first divergent trace event, **the bug is GUARANTEED to live in the interval between that DIVERGENT trace event and the PREVIOUS (last-agreeing) trace event** — everything before the previous event matched both oracles byte-for-byte, so the fault was introduced in exactly that one statement/box span. THE HUNT IS THEN MECHANICAL, NOT EXPLORATORY:
1. **Monitor → first divergence.** Run the 2-way monitor on the failing program. Read the DIVERGE table: it names the statement number, label, source line, and which variable/value/port diverged (e.g. SPITBOL `a`=`hello`(STRING) vs SCRIP `a`=``(NULL)). That line and the line of the previous trace event BRACKET the bug.
2. **gdb breakpoint at the bracketed location, with a SPIN/IGNORE COUNTER.** The divergence is almost always inside a hot loop (the Nth iteration), so a bare breakpoint fires uselessly N times. Set the breakpoint on the bracketed C site (the runtime sink / emitted-box helper / lower arm that statement routes through) and use gdb's hit-count to spin past the agreeing iterations: `break FILE:LINE`, then `ignore <bpnum> <N-1>` (or `condition <bpnum> g_some_counter==N`) so gdb stops on the FIRST DIVERGENT pass — the "two-step spin counter break point." (gdb HW watchpoints DO NOT WORK in this container — see GOAL-CSN-FENCE-FIX.md; use breakpoint hit-counts + the `CSN_NO_SEGV_HANDLER=1`/`SCRIP_NO_SEGV_HANDLER` clean-backtrace hooks instead.)
3. **Single-step until you STEP ON THE LAND MINE.** From that breakpoint, `step`/`next`/`finish` the C and the emitted box until the exact instruction/branch that writes the wrong value (the land mine) is under the cursor. That instruction IS the bug. Fix it there.
4. **Re-run the monitor to confirm the divergence moved PAST the old site** (or vanished). The next divergence is the next rung.

This methodology is the synthesis of `GOAL-MONITOR-REINSTATE.md` (the binary wire), `MONITOR-BINARY-DESIGN.md` (the record format), `GOAL-TWO-STEP-HUNT.md` (the monitor→bracket→probe dance), and the gdb breakpoint-hit-count practice proven across `GOAL-LANG-SNOBOL4.md`, `GOAL-CSN-FENCE-FIX.md`, and `GOAL-PROLOG-BB.md` (`gdb breakpoint hit-counts`). DO NOT debug a divergence any other way until the monitor has bracketed it. The offline alternative when no barrier is wanted is the harness `probe.py` (`&STLIMIT`+`&DUMP=2` frame replay, bisect-divergence) — same bracket theorem, replay instead of live wire. **If the monitor is dark for the mode under test, REINSTATING IT (the MON-RE rung) is the prerequisite and comes first** — a working monitor is worth more than any single bug fix because it makes every subsequent bug mechanical.

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

**ICON SEMICOLON-REQUIRED — NO NEWLINE PROCESSING.** SCRIP Icon REQUIRES `;` between bare statements; the Icon front-end does ZERO newline processing (a newline is whitespace, never a separator). The canonical `icont` Beginner/Ender newline→`;` insertion is FORBIDDEN in `src/parser/icon/`. Newline-style sources get `;` added to the SOURCE, never compiler newline handling. PRISON: `scripts/test_gate_icn_semicolon_required.sh` (3 locks — no insertion machinery; `TK_SEMICOL` minted only from literal `;`; behavioral canary: newline-separated bare statements parse-error, semicolon-separated parse). Full FACT RULE in `GOAL-ICON-BB.md`.

**PEERS RULE.** BB_t stays LEAN. Operand-value refs go in `BB_graph_t.operand_aux` via `bb_operand_aux_set/get`. DO NOT add fields to BB_t.

**CONSULT CANONICAL SOURCES RULE.** For ANY new SM/BB or Icon feature: grep/read canonical procedures FIRST. Authority: `refs/jcon-master/tran/irgen.icn` and `refs/icon-master/src/runtime/*.r`. m2 oracle is a transcription, not truth. **`refs/` is gitignored and NOT auto-populated by cloning SCRIP** (confirmed 2026-06-30: a fresh clone has no `refs/` directory at all, even though `.gitignore` line 84 reserves the name) — every session must set it up itself before these paths resolve. If the person has supplied JCON/Icon master source archives (e.g. as uploaded zips), unzip them anywhere writable and symlink: `ln -s /path/to/jcon-master refs/jcon-master && ln -s /path/to/icon-master refs/icon-master` (absolute-path symlinks survive a `cd`). If no archives were supplied, `git clone` the upstream sources Lon names instead. Either way, verify before trusting any `refs/...` reference downstream: `ls refs/jcon-master/tran/irgen.icn refs/icon-master/src/runtime/`.

## Commit identity
```bash
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
```

## ⛔ FACT RULE — "HANDOFF COMPLETE" REQUIRES A CONFIRMED PUSH (Lon directive, 2026-06-24)
**The phrase "handoff complete" — or any terminal claim of doneness ("done", "all set", "wrapped up", "committed and clean" presented as the end state) — MUST NOT be spoken until `git push` has SUCCEEDED and `git log origin/main --oneline -1` (step 7) shows THIS SESSION'S hash on origin for EVERY touched repo.** A local commit is NOT a handoff; the bytes are on this disposable sandbox and vanish with it. "Pending push awaiting credential", "ready to push", or "the local commits are safe" is an **INCOMPLETE handoff and must be reported as INCOMPLETE — never dressed up as complete.** If a credential is missing or the push fails, the handoff is **BLOCKED**: state that plainly, say exactly what is needed, and STOP — do NOT declare completion. The push (step 6) and the `origin/main` hash confirmation (step 7) are the LAST and MANDATORY acts of every handoff; skipping either means the handoff did not happen, regardless of how green the local tree is. Verify HEAD == origin/HEAD per repo, or it is not done.

**HOW THIS WAS MISSED (root cause, 2026-06-24 — so it is not repeated):**
1. **BLOCKED was reframed as COMPLETE.** The push failed for a missing credential; instead of reporting the handoff BLOCKED, the green *local* state was reported as done with the push demoted to a suggested user follow-up. The rule's real success criterion (the session's bytes living on `origin`) was silently swapped for a weaker proxy (bytes committed to a disposable sandbox). A locally-committed handoff is the same failure as an uncommitted one, one step later.
2. **A bad precedent was inherited.** Prior HANDOFF docs in this repo literally recorded "commits pending push awaiting user token" as a handoff outcome, normalizing the incomplete pattern; it was pattern-matched instead of challenged. "Pending push" is NOT an outcome — it is an unfinished, BLOCKED handoff.
3. **The completion claim was free-authored text.** Nothing forced the status line to be checked against ground truth, so under optimism it drifted from reality. Free-text status will always drift; it must be computed.

**PROTOCOL — THE STATUS LINE IS COMPUTED, NEVER TYPED (the mechanical gate):**
The assistant MUST NOT write the string "HANDOFF COMPLETE" (or any terminal doneness claim) as its own prose. The ONLY sanctioned source of that claim is the verbatim stdout of **`bash scripts/handoff_status.sh`**, which reads ground truth (working tree clean + local HEAD == `origin/<branch>` + zero unpushed) for every git repo it AUTO-DISCOVERS under the workspace (no hardcoded repo list — it enumerates every repo with an `origin` remote, so it cannot miss a touched one and reports the count it found) and prints `HANDOFF COMPLETE` (exit 0) or `HANDOFF BLOCKED` with the reason (exit 1). Handoff step 7 is now: **run `handoff_status.sh`, paste its output verbatim, and only treat the handoff as done if that output — not the assistant — says `HANDOFF COMPLETE`.** If it says BLOCKED, the handoff is BLOCKED: fix the listed reason (commit, then `git pull --rebase && git push`) and re-run. Reading `origin` needs no credential; only the push that PRECEDES the check does. The script blocks on its own uncommitted bytes, so it cannot be satisfied by a tree that still has the rule edit unpushed — closing the loop on itself.

**LIMITATION — DO NOT OVERSELL THIS GATE.** A markdown rule CANNOT coerce the assistant to run the script; this rule has the SAME enforcement gap as the rule it replaces (the assistant must still choose to honor it — exactly what failed on 2026-06-24). The script makes the truth cheap to obtain and hard to FAKE; it does not make the lie IMPOSSIBLE. Real coercion can only live OUTSIDE the model: (a) a harness/product layer that blocks any completion claim not backed by a fresh `handoff_status.sh` run (only the platform can add this), or (b) the human reviewer, who is the enforcer that actually works — **reject any "HANDOFF COMPLETE" not accompanied by the script's verbatim stdout with hashes matching `origin`, and treat a bare completion claim as FALSE by default.**

## Handoff sequence
1. DELETE completed steps from Goal file
2. Update watermark in Goal file only
3. Do NOT edit PLAN.md goals table on routine handoff
4. **If the session touched codegen** (`src/emitter/emit.cpp`, `emit.h`, `src/templates/*.cpp`, `x86_asm.h`, `src/lower/lower_snobol4.c`, or runtime sinks they call — **CORRECTED 2026-06-30: the file list previously read `emit_bb.c`/`emit_core.c`/`BB_templates/*.cpp`/`XA_templates/*.cpp`, none of which exist in the current tree; `emit.h`'s own header comment confirms the consolidation. The scripts named below are still real and current — only this parenthetical was stale.**): run, in this order, **`bash scripts/util_regen_benchmark_s_artifacts.sh "<rung>"`** (corpus `benchmarks/snobol4/*.s`), **`bash scripts/util_regen_feature_s_artifacts.sh "<rung>"`** (SCRIP `test/snobol4/**/*.s` — the feature tests; commits to the SCRIP repo, not corpus), and **`bash scripts/util_regen_demo_s_artifacts.sh "<rung>"`** (corpus demo programs). Each regenerates the mode-4 `--compile` `.s` artifact beside every `.sno` and commits ONLY the artifacts whose bytes changed. **The `.s` is the HONEST CURRENT compiler output, never a pinned golden:** a program whose codegen still bombs an unimplemented shape (normal while a BB family is mid-design) emits a loud bomb stub INTO its `.s` (it still assembles) and is committed as-is; an assembler-rejected `.s` is left untouched and flagged. `scrip --compile` is deterministic, so an unchanged compiler yields no commit (idempotent). These scripts NEVER enforce `.s` sameness and are NOT pass/fail gates — do not wire `.s` byte-identity into any gate; that would fight the design churn the artifacts exist to track. **If the session touched the ICON emitter/lowerer** (`src/lower/lower_icon.c`, Icon-reachable `emit.cpp`/templates in `src/templates/`): also run `bash scripts/update_icon_bench_asm.sh` — refreshes the side-by-side `.s` for the Icon benchmark corpus (`corpus/programs/icon/rung36_jcon_*.s`), writing only on real change. See `PROC-ICON-BENCH-ASM.md`.
5. `git add -A && git commit -m "<description>"` each touched repo
6. `git pull --rebase && git push` — code repos first, `.github` last
7. **Run `bash scripts/handoff_status.sh` and paste its verbatim output. The handoff is done IFF that script — not you — prints `HANDOFF COMPLETE` (exit 0). If it prints `HANDOFF BLOCKED`, fix the listed repo(s) and re-run.** (Replaces the old "eyeball `git log origin/main`" step; the script checks every touched repo's tree-clean + HEAD-on-origin in one place.)

## Oracles
**SPITBOL x64:** `git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64`. Invoke: `/home/claude/x64/bin/sbl -b file.sno`.

## Testing
- Run goal's gate before every commit. No broken commits.
- `timeout 8s` unit/smoke; `timeout 30s` corpus runners.
- Scripts in `SCRIP/scripts/`; `< /dev/null` on scrip calls.

## C code style
- **200-char line max. Zero blank lines.**
- **EXACTLY ONE COMMENT:** the 200-char `/*` + dashes + `*/` separator between every function/major block; `/*===*/` (equals, 200 total) between larger sections. Nothing else — no block/inline comments, no `//`, no prose.
