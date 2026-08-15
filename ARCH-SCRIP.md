# ARCH-SCRIP.md — SCRIP Frontend + Execution Modes

(Pruned 2026-07-01 per Lon: the former 3-mode `sm_lower`→`sm_interp_run`/`sm_jit_run` body, its strikethrough corrections, and the dead-symbol inventory are deleted — recover from git. What follows is the verified current reality; for registers see `src/templates/x86_asm.h` and `ARCH-ICON.md`, for corpus paths see `CORPUS-LOCATIONS.md`. The former ORIENTATION SYNOPSIS pointer was removed 2026-07-08 — that section was deleted 2026-07-05 and the pointer had gone stale.)

## Frontend
SCRIP. Produces the shared AST (tree_t/STMT_t). See ARCH-IR.md.

## Execution modes — EXACTLY TWO (modes 1 and 2 DELETED; see GOAL-MODE34-IDENTICAL.md)
| Flag | Mode | Pipeline |
|------|------|----------|
| `--run` | 3 — native x86 BINARY in-process | IR → `src/emitter/emit.cpp` (`emit_drive` + dispatch) → BINARY → jump in |
| `--compile` | 4 — standalone binary via toolchain | IR → `emit.cpp` → x86 TEXT `.s` → `gcc -no-pie` + `libscrip_rt.so` → exec |
An OPTIMIZER stage (`src/optimizer/`, `optimizer_run(g)`) sits between LOWER and the emitter since 2026-07-01, ON by default per RULES.md's 2026-07-03 FACT RULE — `SCRIP_OPT=0` is an emergency-only escape hatch, not a supported configuration.

## Isolation invariant (current statement)
Neither mode walks the AST or IR at runtime. `emit.cpp` walks the IR graph exactly once, at EMIT TIME, then the IR is never referenced again — the running program is pure emitted x86: zero per-opcode C dispatch, zero `BB_t`-graph traversal. Runtime stubs print `[NO-SM-BB] <opcode>` and set `last_ok=0`. (Check GOAL-PROLOG-BB.md directly for any Prolog-side temporary exception.)

## Shared substrate — symbols verified live (2026-06-30)
`INVOKE_fn`/`APPLY_fn` (builtin dispatch — re-grep location) · `NV_GET_fn`/`NV_SET_fn` (name-value table) · `exec_stmt`/`bb_build` (`src/runtime/core/stmt_exec.c`) · `eval_node` (`src/runtime/runtime_eval.c`) · `coerce.c` (`src/runtime/core/`) · `sm_lower` (vestigial failure-message reference in `src/driver/scrip_sm.c` only). Dead, do not cite: `bb_broker`, `bb_boxes`, `sm_interp_run`, `sm_jit_run`, `SM_sequence_t`, `bb_exec_*`, `g_jit_prog`.

## SNOBOL4 native pattern matching (modes 3 & 4)
The 5-phase `SUBJ ? PAT [= REPL]` model is specified in ARCH-SNOBOL4.md §"Native pattern architecture — modes 3 & 4"; ladder in GOAL-SNOBOL4-BB.md (SBL-PAT-BB). Read before mode-3/4 SNOBOL4 pattern work.

## The three ζ (zeta) storage tiers — NAMING OF RECORD (Lon in-chat, GOAL-RBP-EARN s77/s78/s80; formalized here s81 so it lives beside the architecture it names, not only in goal-file cursor prose)
Everything a running match touches lives in one of three tiers, split on ONE axis — **motion**:

| Tier | Motion | Register | Lifetime / shape | House words already in `src/` |
|------|--------|----------|-------------------|-------------------------------|
| **ζ-STANDING** | never moves | RBP (one instance) | established once at `MATCH_BEGIN`/`S ? P`, pinned for the life of the match; the MARK + outer Σ/δ/Δ + retry cursor + RESULT — a tiny match-level stub, not a general frame | `mrbp` (0 files use `STANDING` yet — free, chosen for scope-neutrality: do NOT name this tier "MATCH", the frame expansion puts other constructs at this tier and that name goes wrong the moment one lands) |
| **ζ-FRAME** (= ζ-ACTIVATION) | framed, comes and goes | RBP (N chained) | one per `*PATTERN_VARIABLE` dereference / per ARBNO site that can't use the frameless mechanism; static offsets, dynamic base | `ZFRAME` (32 files) — already the house word, confirmed by grep before choosing it |
| **ζ-SPINE** | slides | RSP | ordinary FORTH-cell storage: ALPHA allocates, OMEGA self-frees on failure, WHACK frees on FENCE'd/final success; offset itself shifts as RSP moves | `spine` (36+13 files) — already the house word |

Both RBP tiers (STANDING, FRAME) are "the same kind of thing" — both hold allocations — differing only in whether the base ever relocates. Rejected names, so they aren't reproposed: `ζ-MARK` (MARK already names one specific banked quad; overloading makes every existing "the MARK" comment ambiguous) and `ζ-ANCHOR` (collides with `&ANCHOR`, the SPITBOL anchored-matching keyword).

**Census at s78 HEAD** (60-program sweep, every `push rbp` site attributed): 9 total — 5 `match_begin` (ζ-STANDING) + 4 `match_arbno` (ζ-FRAME) + 0 statement + 0 function. RBP's only job, at this HEAD, is the MATCH INTERIOR (`MATCH_BEGIN..MATCH_END`); everything outside it is pure ζ-SPINE with compile-time-known whacks. See GOAL-RBP-EARN.md's LIVE CURSOR for the ladder that gets there and what's still open (S-3/mrbp→ζ-STANDING chain root, E-6/E-7/E-8, the CAPTURE-family nested-hazard gap found s81).
