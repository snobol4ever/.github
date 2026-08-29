# GOAL-HISTORY-INTERP-CHUNKS-BROKER.md — the pre-Byrd-box execution architectures

This is a consolidated historical record, not a live design doc — **nothing in this file describes current
architecture.** It replaces fourteen separate `GOAL-*.md` files, all now deleted, whose entire subject was one
or another now-fully-replaced execution architecture that predates today's flat-wired x86 Byrd-box pipeline
(mode-3 `--run` / mode-4 `--compile`, one shared emitter, `src/templates/bb/*.cpp` templates through the
`x86(...)` encoder — see root `CLAUDE.md` § Architecture for what actually ships today). See RETIRED NAMES at
the end for the old→new mapping every stale cross-reference should resolve through.

Landed via `goal-files-major-consolidation` (task file, `/home/resources/postoffice/tasks/`), executing Lon's
2026-08-28 ruling steps (1)/(3) — grade against live source, consolidate by clustering — for the single most
unanimous, lowest-risk cluster the survey phase found: fourteen files, twelve verdicted **STALE
MANDATE/SUPERSEDED** outright (their entire target architecture confirmed gone from `src/`, zero grep hits on
every named symbol), plus two with a live loose end each, explicitly preserved below rather than dropped. The
survey (12+ sessions, `goal-files-major-consolidation`'s own LEDGER) did the source-verification this file's
claims rest on; this landing re-confirmed the core claims (zero-hit spot checks on the shared dead symbols,
the one still-existing branch) rather than trusting the survey blind, but does not repeat every individual
grep here — see the task file's LEDGER for the full per-file verification trail if a claim below is doubted.

**Reserved, deliberately not touched by this landing:** `GOAL-IR-IMMUTABLE-EMIT.md` (its Layer-1 title-goal is
a currently-PASSING live gate, `test_gate_emit_no_ir_mutation.sh`, confirmed green this same survey — not pure
history) and `GOAL-IR-REDESIGN.md` (mixed: its lower-rewrite claim is genuinely current, only its verification
harness is dead) both need their own, more careful split-handling, not a blanket fold — left for a follow-up
pass. Also untouched: everything in this row's other clusters (NET-*/TEMPLATES/README-SNOBOL4* ports family,
SILLY family, the reserved human/HQ calls on MODE34-IDENTICAL/SCRIP-BOOTSTRAP/NET-BEAUTY-SELF/README
process-shape) — this file is one cluster landing, not the whole consolidation.

## The AST-interpreter era

The earliest layer: SNOBOL4/Icon source executed by walking an AST directly at runtime.

- **`interp_eval()` / `icn_interp_eval()` / `pl_execute_program_unified()`** were the per-language AST-walking
  interpreter entry points. **Confirmed gone — zero hits anywhere in `src/`, this landing's own re-check.**
  Superseded wholesale by the current mode-3/mode-4 flat-wired compilation pipeline: source compiles to native
  x86 (in-process JIT slab, or standalone `.s`/binary), never interpreted.
- **`GOAL-SCRIP-INTERP-SPLIT.md`** (was: 151 ln) proposed extracting this interpreter out of `scrip.c` into a
  new `ir_interp.c`. Never started — `ir_interp.c` was never created, and the interpreter it would have
  extracted had already stopped existing by the time anyone read this file again. `scrip.c` today (2003 ln at
  last measurement) is driver/proc-registration/emission-dispatch code with nothing resembling an interpreter.
- **`GOAL-IR-EMITTER-PREREQ.md`** (was: 163 ln) was the JVM/JS-emission prerequisite for that same generation —
  built on `SM_Program`/`dcg_table`/`emit_ir_block`/`ir_walk`/`IR_emit_vtable_t`/`sm_prog_free`, all zero hits.
  Its cited canonical-header location, `src/include/`, doesn't exist either (root `CLAUDE.md` independently
  confirms `src/include/` "no longer exists on disk").
- **`GOAL-CROSS-LANG-VERIFY.md`** (was: 138 ln) proposed proving SNOBOL4/Icon/Prolog interoperate by routing all
  three through the one `interp_eval()` — the premise interpreter doesn't exist, its "already demonstrated"
  evidence (`test/beauty-sc/`) doesn't exist, and its blocking prerequisite (`GOAL-PROLOG-IR-RUN.md`) was never
  even minted. The underlying INTENT (prove the three languages share one execution model) may be worth
  revisiting once Prolog's own BB port lands (see root `CLAUDE.md`: Prolog still runs `--run` via
  `sm_interp_run` "until `bb_pl_*.cpp` lands," the one place this era's naming survives as a real, current,
  narrowly-scoped exception) — but the concrete S-1..S-7 plan here assumed the wrong architecture throughout
  and would need a full rewrite, not a path-fix, to resume.
- **`GOAL-ONE-EVAL.md`** (was: 368 ln) self-stamped "GOAL COMPLETE" (2026-04-14) for unifying the per-language
  interpreters into one AST-switch plus an SM opcode layer (`SM_BB_PUMP`/`SM_BB_ONCE`, `sm_lower.c`,
  `sm_interp.c`, `polyglot_execute`, `bb_broker.c`) — real, carefully-executed work whose entire target
  architecture was later replaced wholesale by the current pipeline. Nothing here to salvage; the completion
  itself is a genuine historical fact, just about a generation that no longer exists.

## The SM bytecode-VM / CHUNKS era

The AST-interpreter's own successor: a compiled "SM chunk" bytecode-VM sitting between IR and execution.

- **`GOAL-CHUNKS.md`** (was: 980 ln) — roughly fifteen real engineering sessions (#62–#75) eliminating
  `SM_PUSH_EXPR` in favor of a compiled SM-chunk bytecode VM (`sm_lower.c`/`sm_interp.c`/`sm_codegen.c`/
  `SM_Program`). All confirmed gone (files don't exist, zero opcode hits, this landing's own re-check). Four of
  its five declared sub-goal files (`GOAL-MODE4-EMIT.md`, `GOAL-NATIVE-SNOCONE-{DOTNET,JVM,JS}.md`) are also
  simply gone with no retired-names trace anywhere prior to this file. The file's own "Truth-telling preamble"
  section was, per the surveying session, "a model of honest self-critique" — worth knowing existed even
  though the architecture it audited is gone. Its empirical corpus baselines (Icon 186/47/30, etc.) may still
  have residual value as a historical regression-baseline reference; flagged, not reproduced here.
- **`GOAL-CHUNKS-STEP17.md`** (was: 1685 ln, the largest of the fourteen) — CHUNKS' own Step-17 carve-out:
  dozens of meticulously-gated rungs (CH-17a through CH-17g-irrun-execution) on the identical dead
  `sm_lower.c`/`sm_interp.c` substrate. Its own opening banner ("NO AST WALKING IN MODES 2/3/4") independently
  dates it — today's equivalent rule says "modes 3/4" only, mode 2 having been deleted since. Displayed unusual
  self-correction rigor (two separate "-SURVEY-2" ledger entries retract an earlier rung's own claim after
  empirical re-probing) — noted as a possible methodology reference even post-archival, not for its content.
  The final rung recorded had just received a Lon decision ("AST and SM both deleted between phases") pointing
  the same direction the eventual real replacement took, just not via the same mechanism.

## The BB-template ladder and formatting era

The successor generation: per-language C template stubs mechanically translated from an interpreter, and the
text-formatting indirection layer that sat over them before the current C++ template / `x86(...)` encoder.

- **`GOAL-BB-TEMPLATE-LADDER.md`** (was: 424 ln) — the founding-era document of the whole template-ladder
  concept: filling `BB_templates/bb_icn_<name>.c`/`bb_pl_<name>.c` stubs via mechanical translation from
  `ir_exec.c` (its cited canonical semantics source), plus a `FREE-BB-BEFORE-RUN` sub-goal deleting BB/SM
  graphs before a three-mode (2/3/4) execution split. `ir_exec.c`/`sm_jit_interp.c`/`emit_core.c` are all gone;
  `bb_build_brokered`/`stage2_free_bb_only` have zero hits. Of the ten specific per-language template
  filenames this file names, only three survive under the same name (`bb_to_by.cpp`, `bb_iterate.cpp`,
  `bb_arith.cpp`), and even those three's content is unverified against this file's description given the
  intervening `BB_ICN_*`→`BB_*` rename this file itself documents, plus later reorgs. The earliest layer of a
  lineage that runs founding-doc → COMMAND-CENTRAL → today's `src/templates/bb/`.
- **`GOAL-TEXTF-TEMPLATES.md`** (was: 173 ln) — a pre-C++-template-encoder emission-formatting layer
  (`bb3c_format`/`emit_bb_x*`/`emit_flat_ir`/`emit_bb_node` over old-style `bb_pos.c`/`bb_tab.c`/`bb_capture.c`,
  plain `.c` files, not today's `.cpp` template convention). All zero hits; the file's own gate,
  `test_per_kind_diff.sh`, doesn't exist either. Was genuinely live and actively worked as late as its own
  "Session #8" (G1–G6 done, G7–G9 surveyed clean) — not abandoned mid-stream so much as the entire target
  formatting-indirection system got replaced outright by the current `x86(...)`-encoder templates, mooting
  G11–G14 rather than them finishing on the old substrate.
- **`GOAL-COMMAND-CENTRAL.md`** (was: 410 ln) — the template ladder's CAPS-CONCAT/LOCAL-PURGE methodology, built
  on `MEDIUM_TEXT`/`MEDIUM_BINARY`/`MEDIUM_MACRO_DEF` multi-arm templates and a per-kind byte-identity oracle
  (`test_per_kind_diff.sh`, `baselines/per_kind/`). Confirmed gone: **zero** `MEDIUM_*` tokens exist anywhere in
  `src/templates/bb/*.cpp` today — the current hard rule (root `CLAUDE.md` § BOTH-MEDIUM MANDATORY /
  NO MEDIUM_* IN TEMPLATES) is the exact opposite of this file's premise. `SM_templates/`/`BB_templates/`
  directories are gone (now `src/templates/bb/`). The file's own CC-3 section had already self-documented one
  reversal mid-file before this landing (its "even an empty arm must keep its slot" lesson struck out
  in-place, citing s173/HQ-55).
  ⚠️ **LIVE LOOSE END, PRESERVED, NOT DROPPED:** the `descr8-macro-funnel` branch this file's DESCR-WIDTH rung
  lived on **still exists on `origin` today** (commit `3d761449`, re-confirmed by this landing directly via
  `git ls-remote`) — real, unmerged, historical width-parity work, not confirmed abandoned. Archiving this
  GOAL file does **not** imply that branch should be deleted; whoever eventually triages stale branches should
  treat it as its own open question, not settled by this consolidation.

## The broker and mode-isolation era

- **`GOAL-UNIFIED-BROKER.md`** (was: 380 ln) — ONE-EVAL's predecessor: builds `bb_broker()`/`univ_box_fn`/
  `BrokerMode`. The broker dispatch mechanism itself is dead (`bb_broker()` zero call sites; `univ_box_fn` zero
  uses beyond its own typedef, though the TYPES still sit in `src/ir/bb_box.h`).
  ⚠️ **LIVE THREAD, PRESERVED, NOT DROPPED:** this file's LATER Phase 7 insight —
  `ScripModule`/`ScripModuleRegistry`, "module boundary = link unit" — is genuinely alive and foundational
  TODAY, used in `src/driver/polyglot.c` (`polyglot_init(stage2_t*, ...)` still exists by that name) and in all
  five current per-language lowerers. Completed-via-a-different-implementation-than-planned: the broker
  mechanism died, but its Phase-7 architectural idea shipped, just inside `polyglot.c`/`stage2.h`/the
  lowerers rather than as a standalone broker. Anyone tracing the *origin* of today's module-boundary model
  should know it started here.
- **`GOAL-REWRITE-SCRIP.md`** (was: 774 ln) — four-mode isolation (mode 1 IR-interp / mode 2 SM-interp / mode 3
  SM-JIT / mode 4 compile) enforced by `scripts/test_isolation_ir_sm.sh` grepping for IR-walker leakage into
  SM-mode files (`coro_value.c`, `coro_stmt.c`, `sm_interp.c`, `sm_codegen.c`, `sm_prog.c` under the
  since-moved `src/runtime/x86/`). Unusually self-aware: the gate script's own header comment (dated CLI-3M-9,
  2026-05-18) already recorded *"execute_program, eval_ast, ... are ALL DELETED from the codebase ... This
  gate is trivially satisfied ... kept for documentation"* — confirmed still true (`interp_eval` zero hits,
  `coro_value.c`/`coro_stmt.c` zero hits, `sm_interp.c`/`sm_codegen.c` gone). Even the one file the gate
  script's own path list still names as surviving, `sm_prog.c`, has since moved again
  (`src/runtime/x86/` → `src/ir/`) — the gate's hardcoded paths are stale on top of its premise already being
  moot. A documented, self-aware vacuous-gate case in its own right, worth cross-referencing if
  `test_isolation_ir_sm.sh` itself is ever cleaned up.

## The in-process monitor comparator

- **`GOAL-INPROC-MONITOR.md`** (was: 380 ln) — an IR/SM/JIT/CSNOBOL4 four-way in-process execution comparator
  (`execute_program`, `sm_interp_run`, a JIT trampoline, `sync_monitor_run`). `execute_program` is a dead
  prototype with no definition anywhere; `sm_interp_run`/`sm_codegen.c` zero hits; `sync_monitor.c`/
  `csnobol4_shim.c` do still exist on disk but are reachable only via a vestigial `make scrip-monitor`
  side-target producing a disconnected `scrip-monitor` binary — not part of `make scrip` or any test suite,
  and `sync_monitor_run` has zero callers anywhere.
  ⚠️ **SAME-NAME TRAP, worth stating loudly since it is easy to get backwards:** today's real `--monitor` CLI
  flag (`g_monitor_bin`, referenced throughout current RULES.md's ASM-DIFF-FIRST discussion) is a completely
  different, later mechanism — per-value emission tracing bolted into the x86 emitter (`rt_mon_set_max_stno`,
  `mon_emit_value_bin`) — sharing only the flag name with this file's elaborate four-way comparator. Do not
  assume today's `--monitor` is this file's mechanism; it is not.

## Full Integration milestone

- **`GOAL-FULL-INTEGRATION.md`** (was: 317 ln) — self-stamped "GOAL COMPLETE" 2026-04-14, FI-0 through FI-11,
  concrete and credible.
  ⚠️ **FOOTGUN, EXPLICITLY DEFUSED HERE:** the file's own "Architecture: what we are building toward" diagram
  (`sm_lower()` → `SM_Program` → `sm_interp_run()`/`sm_jit_run()`) describes a pipeline that **does not exist**
  — only `scrip_sm.c` matches any of those names anywhere in `src/`, and `scrip.c` itself actively prints
  `"[SMX] --target=%s removed (Stack-Machine codegen removed)."` at runtime. Root `CLAUDE.md` confirms only
  mode-3 (flat-wired x86 slab) and mode-4 (text asm) exist — no SM intermediate layer, ever, today. A reader
  who consulted only that diagram (not this file's closure stamp) would have walked away with actively wrong
  current architecture; that is exactly the risk this consolidated record exists to remove. Two of its FI-4/
  FI-5 deliverables, `icn_runtime.c`/`pl_runtime.c`, don't exist under those names either, but that is a
  legitimate sequel, not a contradiction: the cross-language runtime dissolution (`RUNTIME-REORG`, still a
  live design doc, not part of this consolidation) later folded exactly these per-language files into shared
  cross-language subsystems (`src/runtime/{unification,rt_runtime}.c` etc.).

## Lower redesign (three-layer file, mostly dead, one layer correctly prophetic)

- **`GOAL-LOWER-REDESIGN.md`** (was: 936 ln) — three chronological layers in one file, oldest at the bottom:
  - **Layer 1** (main body): a dual SM-emitter/BB-emitter architecture over a shared DCG/`IR_t`, four-mode
    split, `sm_interp`/JIT. Dead (`sm_interp.c` gone) — today's real pipeline is one emitter producing both
    binary and text from the same box graph, never two parallel emitters.
  - **Layer 2** (2026-05-31 note): a `lower2.c`/`prove_lower2.c` prototype. Dead, and the note **already
    self-corrected this exact point** before this consolidation ("stale on one point: `lower2.c` ... no longer
    in the tree").
  - **Layer 3** (2026-06-08 note, the file's newest and top-most content): per-language self-contained
    lowerers with γ/ω as `IR_ref_t{node,sz}` pairs. **This layer was right, and still is** —
    `IR_ref_t{node,sz}` is exactly today's live `src/ir/IR.h` structure, and `lower_pascal.c` is a genuine,
    self-contained, `pas_`-prefixed lowerer exactly as this layer describes. But its own named scaffolding
    (a single shared `lower.c` receiving per-level dispatch, `lower_value_shared`, `prove_lower.sh`) is
    *also* now gone — superseded by a further split into fully separate per-language `lower_<lang>.c` files.
  Unlike every other file in this cluster, Layer 3's *destination* was correct — it anticipated where the
  architecture was heading — only the specific transitional vehicle it named has since been superseded by
  continued progress in the same direction it predicted. Anyone wanting the lineage of today's per-language
  `lower_<lang>.c` split should know this file's Layer 3 is where the direction was first written down.

## RETIRED NAMES

Fourteen source files, all deleted, replaced entirely by this one file — nothing in them was true-and-uncaptured
except the live threads flagged with ⚠️ above, which live on as flagged notes here rather than as separate files:

| Retired name | Where its content now lives |
|---|---|
| `GOAL-SCRIP-INTERP-SPLIT.md` | § The AST-interpreter era |
| `GOAL-IR-EMITTER-PREREQ.md` | § The AST-interpreter era |
| `GOAL-CROSS-LANG-VERIFY.md` | § The AST-interpreter era |
| `GOAL-ONE-EVAL.md` | § The AST-interpreter era |
| `GOAL-CHUNKS.md` | § The SM bytecode-VM / CHUNKS era |
| `GOAL-CHUNKS-STEP17.md` | § The SM bytecode-VM / CHUNKS era |
| `GOAL-BB-TEMPLATE-LADDER.md` | § The BB-template ladder and formatting era |
| `GOAL-TEXTF-TEMPLATES.md` | § The BB-template ladder and formatting era |
| `GOAL-COMMAND-CENTRAL.md` | § The BB-template ladder and formatting era (incl. the still-live `descr8-macro-funnel` branch note) |
| `GOAL-UNIFIED-BROKER.md` | § The broker and mode-isolation era (incl. the still-live Phase-7/`polyglot.c` note) |
| `GOAL-REWRITE-SCRIP.md` | § The broker and mode-isolation era |
| `GOAL-INPROC-MONITOR.md` | § The in-process monitor comparator (incl. the `--monitor` same-name-trap warning) |
| `GOAL-FULL-INTEGRATION.md` | § Full Integration milestone |
| `GOAL-LOWER-REDESIGN.md` | § Lower redesign |

**Symbols/paths from the retired files that a stray grep might still turn up** (all confirmed dead, listed once
here rather than per-section): `interp_eval`, `icn_interp_eval`, `pl_execute_program_unified`, `ir_interp.c`,
`SM_Program`, `dcg_table`, `emit_ir_block`, `ir_walk`, `IR_emit_vtable_t`, `sm_prog_free`, `sm_lower.c`,
`sm_interp.c`, `sm_codegen.c`, `SM_PUSH_EXPR`, `bb3c_format`, `emit_bb_xstar`, `emit_flat_ir`, `emit_bb_node`,
`MEDIUM_TEXT`/`MEDIUM_BINARY`/`MEDIUM_MACRO_DEF` (as template arms — see root `CLAUDE.md` for the current,
opposite rule), `bb_broker()`, `univ_box_fn`, `BrokerMode`, `ir_exec.c`, `sm_jit_interp.c`, `emit_core.c`,
`bb_build_brokered`, `stage2_free_bb_only`, `execute_program`, `sync_monitor_run`, `lower2.c`,
`prove_lower2.c`, `lower_value_shared`, `prove_lower.sh`.
