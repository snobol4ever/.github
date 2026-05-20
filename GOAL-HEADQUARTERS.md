# GOAL-HEADQUARTERS.md — one4all Maintenance HQ

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-ICON-BB-NATIVE ✅ `7efdf09a`

## Invariants

1. **No AST walking in modes 2/3/4.** `[NO-AST] FOO` → write fresh SM/BB lowering, do not restore AST-walking call.
2. **Zero C Byrd-box functions.** No `DESCR_t foo(void *zeta, int entry)`. Only permitted: `icn_bb_dcg`.
3. **Cross-language:** SM↔SM via `g_user_call_hook`; BB↔BB via universal α/β/γ/ω contract. Never invoke language-A SM-bridge with language-B BB object.
4. **Four ports hard-wired.** `BB_node_alloc` bakes α=nd, β=nd, γ=NULL, ω=NULL. Zero call sites depend on NULL α/β as sentinel.
5. **Three orthogonal constructs per session max**, separate commits, single gate run at end.
6. **Builder/consumer case rule.** UPPERCASE prefix builds IR (`SM_*`, `BB_*`). lowercase consumes it (`sm_*`, `bb_*`).
7. **EC-UNI matrix.** Backends are columns (X86/JVM/JS/NET/WASM). Text-vs-binary lives inside each `IS_<BE>` arm in the encoder layer below — never as a matrix dimension.
8. **Unified dispatch owns mode-setting.** Per-opcode iteration calls `emit_mode_set(TEXT_MODE(), out)` at entry. Individual dispatchers stay idempotent.

## Session Setup

```
cd /home/claude/one4all && bash scripts/build_scrip.sh
```

## Architecture

```
AST --(lower)--> SM_sequence_t  [SM_BB_XXX bridge opcodes]
                 BB_graph_t*    [pre-built per bridge op, single-structure via SM_sequence_t.bb_table]
```

Mode 2 (`--interp`) is the reference path for Icon at 194/265. Mode 4 (`--compile`) emits wired x86 — no `bb_broker`.

## Gates

```
GATE-1  bash scripts/test_smoke_icon.sh                        # PASS=5
GATE-2  bash scripts/test_smoke_unified_broker.sh              # PASS >= 23
GATE-3  bash scripts/test_icon_all_rungs.sh --interp           # PASS=194
```

## Watermark

```
one4all: 3088dcba    (EC-UNI-10 ✅ COMPLETE — three orthogonal commits 7835fb9d/5e607294/3088dcba: g_emit single global struct + parameterless SM/BB templates)
corpus:  b10933c
.github: (this commit — EC-UNI-10 close-out ledger; EC-UNI-11 advanced to NEXT)
--interp:      PASS (hello.sno, hello.icn)
smoke icon:    5/0    smoke prolog: 5/0    smoke rebus: 4/0
smoke raku:    5/0    smoke snobol4: 7/0    smoke snocone: 5/0
broker:        23/26
icon rungs:    194/36/35
matrix gate:   0/365 PASS
DAI-BOMB fires: 0
firewall lower:   9 includes / 6 allowlisted
firewall runtime: 16 includes / 8 allowlisted
firewall stage2:  10 allowlist entries (token gate; honest-scope: not link-time)
beauty.sno --compile md5: 40df9e004c3e963c99af716c65f2c970  (baseline 2026-05-20, 882901 bytes)
```

---

## Active rungs

### EC-UNI — x86 text/binary into SM_templates; unify all walkers

**Target:** one fn per SM opcode, one fn per BB kind; each carries one arm per backend (5 cols: X86/JVM/JS/NET/WASM). Text-vs-binary hides inside the encoder below the dispatcher. `emit_walk_codegen`, `emit_jvm_from_sm`, `emit_js_from_sm`, `emit_net_from_sm`, `emit_wasm_from_sm` all delete.

Completed: EC-UNI-0 through EC-UNI-9d. 52 SM_template fns across 5 files carry `IS_X86` arms, reachable via `SCRIP_UNIFIED_DISPATCH=1`. Matrix gate passes 0/365. Commits: `f29c95e9`/`e2491770`/`fc9d0122`/`609dac51`/`bfa65968`/`b1711529`/`42908963`/`63708215`/`7d792c59`/`073f3711`/`8308a457`.

**EC-UNI is now a single ladder (EC-UNI-10 through EC-UNI-22).**  The previously-listed open rungs EC-UNI-3-beauty / EC-UNI-4 / EC-UNI-5 / EC-UNI-6 / EC-UNI-7 / EC-UNI-8.4-fix / 8.5 / 8.6 / 8.7 and the separate EC-PHASE-A ladder (EC-PA-1 through EC-PA-8) are replaced by this re-laid sequence.  The work is the same work, ordered around a sharper end-state design (recorded in the next subsection).  No previously-completed step (EC-UNI-0 through EC-UNI-9d) is touched.

---

#### End-state design (locked 2026-05-20)

The post-EC-UNI shape of the emitter is the **three-layer cake** that the x86 path already demonstrates — extended to all five backends, with one critical correction relative to today's x86 path.

**The correction (x86's lesson):** today's x86 path uses too many helper C functions (`emit_macro_begin`, `emit_mov_rdi_imm64`, `emit_call_sym_plt`, `emit_pad_to_blob_size`, `emit_sm_int_arg`, `emit_sm_op`) that hide the actual GAS lines being emitted.  (Terminology: these are *helper template C functions* — not GAS `.macro`/`.endm` assembler macros, which are fine and stay.  The objection is to the C-side layering that wraps macro invocations.)  Reading `emit_macro_begin("INCR", params, 1); emit_mov_rdi_imm64((uint64_t)n); emit_call_sym_plt("rt_incr", 0); emit_macro_end(); emit_pad_to_blob_size();` doesn't tell you what string lands in the output.  The JVM/JS/NET/WASM arms in today's templates are the opposite — they emit `fprintf(out, "    goto_w sm_pc_%d\n", target)` directly, and you can *read* what comes out.  **The new templates are explicit and verbose; helper template C functions are extracted later, deliberately, and only when they don't obscure logic.**  Sub-expression-level helpers ("optimize the call site by hiding three lines behind a name") are the wrong kind of helper.  Real helpers hide ugly *cross-mode* logic (e.g. JVM's body/method gate that decides between `goto_w sm_pc_N` and `halt+exit`), not formatting convenience.

**Three layers, end state:**

```
Layer 1 — Top-level templates       SM_templates/sm_<op>.c, BB_templates/bb_<kind>.c
                                    One fn per opcode/kind, signature `void sm_<op>(void)` / `void bb_<kind>(void)`.
                                    Reads g_emit.* freely.  Uses ONLY IS_X86/JVM/JS/NET/WASM as branching.
                                    Body is verbose and explicit — the literal output strings are visible.
                                    Five `if (IS_<BE>)` arms, side-by-side, all backends on one screen.

Layer 2 — Per-backend helpers       Same file as the template, file-scope `static`.
                                    Hides cross-mode logic only (TEXT/BIN, body/method gates, fallbacks).
                                    Reads g_emit.* AND uses IS_TEXT/IS_BIN freely.
                                    Takes parameters for values that vary per call site.
                                    Extracted in EC-UNI-16 — deliberately, where it earns its keep.

Layer 3 — String-builder primitives  src/emitter/emit_io.{c,h}.
                                    emit_text / emit_textf / emit_byte / emit_bytes.
                                    Funnel for all output.  Per-backend buffers internally.
```

**Tables drive families** where opcodes share structure (nullary, arith, int-arg-with-rt-call).  One row per opcode per backend.  Adding a member of the family = one row edit, not a new helper.  See EC-UNI-18.

**The single global structure `g_emit`:** all template state lives in one `sm_emit_t` struct, instance `g_emit`, declared in `src/emitter/emit_globals.{c,h}`.  Top-level templates and Layer-2 helpers freely read it.  Snocone bootstrap maps `g_emit` 1:1 to a flat `DATA('Sm_emit(BACKEND, OUT, I, N, INSTR, NODE, SID, NID, IN_BODY, IN_MY_METHOD, PC_TO_FN, FN_NAMES, FN_COUNT, PROG, SRCLINES, IS_BINARY)')` declaration.  Per-instruction / per-node fields are set by the dispatcher loop in `emit_program` (and the corresponding BB walker) once per iteration.  Pass-wide fields are set once before the loop.

**Re-entrancy:** `g_emit` is not re-entrant.  Single-threaded by construction.  If a template ever calls another template (none today), the caller must save/restore the fields it owns.  Documented in `emit_globals.h`.

**Verbose then reduce — the explicit two-phase shape (EC-UNI-13 → EC-UNI-15 → EC-UNI-16):**

1. **EC-UNI-13 — collect.**  Every opcode emitted by any silo walker today gets its template fn.  Bodies are the *verbatim union* of the silo arms wrapped in `if (IS_<BE>) { ... }`.  Verbose.  Explicit.  Maybe duplicative.  This is the collect phase.
2. **EC-UNI-15 — top-level shape.**  Top-level templates become the verbose side-by-side `IS_<BE>` switch.  Still explicit.  No premature helper extraction.  The literal output strings are visible in every arm.
3. **EC-UNI-16 — REDUCE phase.**  Now we look at the verbose templates and extract Layer-2 helpers — carefully, with the explicit constraint that **a helper must hide ugly logic, not hide formatting**.  Rule: a Layer-2 helper is justified iff it carries a real conditional (TEXT/BIN, body/method gate, fallback path) or de-duplicates a non-trivial computation that appears in ≥2 templates.  Mere string-concat shortening is NOT a reason.  The literal output, once reduced, must still be readable from the helper definition itself — Layer 2 emits visible strings via Layer 3 primitives.

This ordering is the explicit lesson from the x86 path: extracting helpers *before* you can see the full verbose form leads to the macro-soup that today's x86 has.  Verbose first, reduce second, with a sharp justification rule.

---

#### Scope inventory (measured 2026-05-20)

- SM: 76 opcodes touched by at least one walker.  52 templates exist (carrying IS_X86 arms) → ~20 to add (many *_S/*_F variants foldable into base fns; ~10 truly new fns).
- BB: 21 opcodes touched.  16 templates exist (PAT_* via one-file-per-op) → 4 new templates (BB_PL_ARITH/ATOM/BUILTIN/CALL absorbing ad-hoc arms in `emit_sm.c`) + reorg of 16 single-file PAT templates into one `bb_pat.c`.
- Walkers to delete after coverage lands: `emit_walk_codegen` (x86 legacy), `emit_jvm_one_instr` + `emit_jvm_from_sm`, `emit_js_from_sm`, `emit_net_from_sm`, `emit_wasm_from_sm`, `dispatch_one_x86`, plus ~30 `emit_sm_*_dispatch` helpers in `emit_sm.c`.  Net LOC: estimated −2500 to −3500 once all silos delete.

**Unblocks Phase B** (five per-backend GOAL files: GOAL-SN4-X86-EMIT [new], GOAL-SN4-JVM-EMIT, GOAL-SN4-JS-EMIT, GOAL-SN4-NET-EMIT, GOAL-SN4-WASM-EMIT — each fills the `IS_<BE>` arms across the full opcode set, including ops nobody emits today: BB_AUGOP, BB_GOTO, BB_UNOP, BB_PROC, BB_SCAN, BB_INTERROGATE, BB_PAT_CALLOUT, BB_ICN_EVERY).  After EC-UNI: "fix backend X for opcode Y" = "open `sm_<y>.c`, find the `IS_X` arm, edit it."  Single file, single fn, side-by-side with the four other backends' working code.

---

#### Active rungs (EC-UNI-10 onward)

- [x] **EC-UNI-10 ✅ COMPLETE 2026-05-20** — `g_emit` single global struct; templates are parameterless.  Three commits per RULES.md "Three-construct":

  - **EC-UNI-10(a)** `7835fb9d` — Created `src/emitter/emit_globals.{c,h}` defining `sm_emit_t` and the single `g_emit` instance.  Field layout mirrors the Snocone `DATA('Sm_emit(BACKEND, IS_BINARY, OUT, I, N, INSTR, NODE, SID, NID, IN_BODY, IN_MY_METHOD, PC_TO_FN, FN_NAMES, FN_COUNT, PROG, SRCLINES)')` shape.  `emit_program()` populates pass-wide fields at entry; save/restore for re-entrancy.  No template body changes.
  - **EC-UNI-10(b)** `5e607294` — Migrated the 7 ctx-bearing SM templates (`sm_jump`/`sm_jump_s`/`sm_jump_f`/`sm_halt`/`sm_return`/`sm_freturn`/`sm_nreturn`) to parameterless `int sm_<name>(void)` reading from `g_emit`.  Layer-2 helpers `jvm_ret_guard`/`net_ret_guard` updated to read `g_emit.out` / `g_emit.i` (keep op/sfx as call-site variants).  Producer call sites updated in 5 dispatchers (`emit_wasm_from_sm`, `emit_jvm_one_instr`, `emit_js_from_sm`, `emit_net_from_sm`, `dispatch_one_x86`).  `sm_ctx.h` deleted.  The EC-UNI-3-beauty deliverable is structurally absorbed — `g_emit.prog`/`srclines` are real globals now.
  - **EC-UNI-10(c)** `3088dcba` — Migrated all 16 BB templates (parameterless `void bb_<kind>(void)`, `bb_capture(int imm)` keeps `imm` as a genuine per-call-site discriminator) and the 7 remaining SM template family files (~40 fns across `sm_arith`/`sm_compare`/`sm_push_pop_lits`/`sm_pat_anchors`/`sm_pat_combine`/`sm_pat_control`/`sm_pat_position`).  The 4 previously-i-bearing pat templates (`sm_pat_any_i`/`sm_pat_notany`/`sm_pat_span`/`sm_pat_break`) become `void(void)` reading `g_emit.i`.  Forward decls in `sm_templates.h`/`bb_templates.h`/`emit_core.h` updated.  ~113 call sites rewritten across `emit_core.c`/`emit_sm.c`/`emit_bb.c`.  `emit_bb_node` sets `g_emit.node`/`out`/`sid`/`nid` before each call.

  Watermark: `3088dcba`.  Beauty md5: `40df9e004c3e963c99af716c65f2c970` (unchanged at every commit).  Smoke 5/5/5/4/7/5; broker 23/26; icon all-rungs 194/36/35.  ARCH-IR.md and Phase-B GOAL files not yet updated — that's EC-UNI-22.

- [ ] **EC-UNI-11 (NEXT)** — emit primitives.  Add `src/emitter/emit_io.{c,h}` with `emit_text(const char *)`, `emit_textf(const char *fmt, ...)`, `emit_byte(unsigned char)`, `emit_bytes(const unsigned char *, int len)`.  Per-backend buffers internally (`g_text_buf`, `g_bin_buf`).  Flush hook in `emit_program` writes the buffer to `g_emit.out` at completion.  Self-test that round-trips a synthetic byte stream.  No template body changes yet.  Gates unchanged.

- [ ] **EC-UNI-12** — sweep `fprintf(g_emit.out, ...)` → `emit_textf(...)` across all current templates.  Mechanical text-only sweep over `SM_templates/*.c` and `BB_templates/*.c`.  Every direct `fputc`/`fwrite` in binary-x86 arms → `emit_byte`/`emit_bytes`.  Drop `g_emit.out` reads inside templates entirely; the buffer abstraction owns the sink.  Gate: byte-identical beauty.sno after final flush.  Full smoke.

- [ ] **EC-UNI-13** — collect: pull all remaining template code into `SM_templates/` and `BB_templates/`.

  Inventory: `emit_sm.c` (151955 bytes) contains ~30 `emit_sm_<op>_dispatch` helpers and the per-op `case` arms of `dispatch_one_x86` that emit GAS lines directly.  `emit_core.c` (76646 bytes) contains the four silo walkers (`emit_jvm_one_instr`, `emit_js_from_sm`, `emit_net_from_sm`, `emit_wasm_from_sm`) plus inline switch bodies for JVM/JS/NET.  `emit_bb.c` contains four `case BB_PL_*:` arms with ad-hoc dispatch.

  For every SM opcode currently emitted by any silo walker but lacking a template fn: create the template fn in the appropriate `SM_templates/sm_<family>.c` (new families: `sm_calls.c`, `sm_defines.c`, `sm_bb_calls.c`, possibly `sm_suspend.c`).  Body is **verbatim union of the four silo arms** wrapped in `if (IS_X86) { ... } if (IS_JVM) { ... } if (IS_JS) { ... } if (IS_NET) { ... } if (IS_WASM) { ... }`.  No refactor.  No helper extraction.  Pure motion.  Verbose by intent.

  For every BB kind currently in an `emit_sm.c` `case BB_PL_*:` arm: create `BB_templates/bb_pl.c` with `bb_pl_arith`, `bb_pl_atom`, `bb_pl_builtin`, `bb_pl_call`.  Bodies copied verbatim.

  Consolidate the 16 single-file PAT BB templates into `BB_templates/bb_pat.c` (one file, same fn names; deletes 16 files; the directory hierarchy stays the same — `BB_templates/`).

  At end of step: every template fn exists in `SM_templates/` or `BB_templates/`.  `emit_sm.c` and `emit_core.c` still call them via the old silo walkers (silos not deleted yet — that's EC-UNI-14).  Gate floor unchanged.

- [ ] **EC-UNI-14** — single dispatcher.  Build `emit_sm_dispatch(void)` in `emit_core.c`: one switch on `g_emit.instr->op`, 91 arms, each calling `sm_<name>()`.  No backend conditional at the dispatcher level — that's inside each template.  Expand `emit_bb_node(void)` to cover all 21 BB kinds reachable today.  The per-iteration loop in `emit_program` becomes: set `g_emit.*` per iteration, call `emit_sm_dispatch()`.

  Delete `emit_walk_codegen`, `emit_jvm_one_instr`, `emit_js_from_sm`, `emit_net_from_sm`, `emit_wasm_from_sm`, `dispatch_one_x86`, and the ~30 `emit_sm_<op>_dispatch` helpers in `emit_sm.c`.  Switch `SCRIP_UNIFIED_DISPATCH=1` to always-on, then delete the flag.

  Net LOC: estimated −2500 to −3500.  Gate: floor unchanged; beauty.sno byte-identical.

- [ ] **EC-UNI-15** — top-level shape: verbose side-by-side `IS_<BE>` switch.

  Each top-level SM/BB template fn becomes ideally one `if (IS_<BE>)` line per backend, side-by-side.  Five lines, one screen, all backends visible.  The top-level fn reads `g_emit.*` freely.  The top-level fn uses `IS_<BE>` for the backend switch and **should not contain other backend-specific branching logic** — push that into Layer 2 helpers (next step).

  At this step the bodies are still verbose and explicit.  No premature helper extraction.  Multi-statement `IS_<BE>` arms are fine; we just want the top-level fn to be a five-arm switch with each arm clearly readable.

  Done family-by-family per RULES.md three-construct: one commit per family file (`sm_jumps.c`, `sm_returns.c`, `sm_arith.c`, `sm_halts.c`, `sm_pushes.c`, …; then `bb_pat.c`, `bb_pl.c`, `bb_lit.c`, etc.).  Gate floor unchanged.

- [ ] **EC-UNI-16** — REDUCE phase: extract Layer-2 helpers, carefully.

  Now (and only now) we look at the verbose templates from EC-UNI-15 and extract Layer-2 helpers.  Rule:

  > **A Layer-2 helper is justified iff it carries a real conditional (IS_TEXT/IS_BIN, body/method gate, fallback path) OR de-duplicates a non-trivial computation that appears in ≥2 templates.**
  >
  > **Mere string-concat shortening is NOT a reason.**
  >
  > After reduction, the literal output must remain readable from the helper definition itself.  Layer 2 emits visible strings via Layer 3 primitives (`emit_text`/`emit_textf`).  No further layers below Layer 3.

  Examples of justified Layer-2 helpers:
  - JVM `jvm_jump_to_pc(target)` — encapsulates the in-method / cross-method / out-of-range three-way decision with the `halt+exit` fallback.
  - JVM `jvm_ret_guard(op, sfx)` — `_S` and `_F` variants of return ops with `last_ok` test (already exists as `static inline` in `sm_template_common.h`; promote into Layer 2 properly).
  - NET `net_ret_guard(op)` — same pattern as above.
  - JVM `jvm_pat_str_push(tag, method)` — shared pat-helper shape (already exists; document it as Layer 2).

  Examples of unjustified extraction (do NOT do):
  - `jvm_invokestatic(class, method, sig)` — hides one line behind a name; the literal `    invokestatic rt/SnoRt/halt_tos()V\n` is more readable than `jvm_invokestatic("rt/SnoRt", "halt_tos", "()V")`.
  - x86 `emit_macro_begin/emit_macro_end` style wrappers — already in tree as legacy; do NOT propagate to other backends.  (The x86 cleanup itself is out of scope for EC-UNI; it stays as-is for behavior preservation.  Phase B per-backend goals may revisit.)

  Done family-by-family, separate commits.  Each commit lists the helpers extracted and the justification per helper.  Gate floor unchanged, beauty.sno byte-identical at every commit.

- [ ] **EC-UNI-17** — Layer-3 primitives audit.  Audit `emit_io.{c,h}` against EC-UNI-12 sweep.  Add a small set of Layer-3 primitives **only if** the same multi-line string pattern recurs in ≥3 places across ≥2 backends.  Document the rule in `emit_io.h`:

  > A Layer-3 primitive emits a fixed multi-character sequence with parameter substitution.  It carries no conditional logic.  It exists iff the pattern recurs in ≥3 call sites across ≥2 backends.

  If no patterns earn it: EC-UNI-17 is a no-op step; skip and proceed.  This step exists to *limit* primitive proliferation — the answer "we don't need more primitives" is acceptable and expected.

- [ ] **EC-UNI-18** — table-driven dispatch where it earns its keep.  x86 already shows `g_sm_nullary` and `g_sm_arith` work.  Extend the pattern to other backends ONLY where the table-driven form is shorter than the verbose form *and* the table itself reads cleanly:

  - JVM nullaries → `g_jvm_nullary[]` mapping `op → "rt/SnoRt/<fn>()V"` invokestatic string.  Single helper `jvm_emit_nullary(op)` walks the table.
  - Same for NET (`g_net_nullary[]` → `"call void SnoRt::<fn>()"`), WASM (`g_wasm_nullary[]` → `"(call $sno_<fn>)"`), JS (`g_js_nullary[]` → `"rt.<fn>(); "`).

  Adding a nullary opcode becomes a five-row edit (one row per backend) instead of five function bodies.  Tables become `DATA(...)` arrays in the Snocone bootstrap.

  Only families where this earns its keep are touched.  Apply to nullary + arith only at this step; other families (calls, returns, jumps) stay verbose because their per-op variation is real, not table-shaped.

- [ ] **EC-UNI-19** — add-a-backend test (`EMIT_NULL=99`).  Mechanical patch: add `EMIT_NULL` to the backend enum and `IS_NULL` to the macros.  Add stub `IS_NULL` arms per template family (and rows to the nullary/arith tables from EC-UNI-18).  Verify cost: N template edits + 1 header enum entry + 1 macro + N table-row inserts.  Revert at end of step.  Documents the invariant claim and records exact LOC cost.

- [ ] **EC-UNI-20** — add-an-opcode test (`SM_NOP`).  Mechanical patch: `SM_NOP` enum value + `SM_templates/sm_nop.c` + arm in `emit_sm_dispatch`.  Verify cost: 1 new file + 1 enum value + 1 dispatcher arm.  Revert.

- [ ] **EC-UNI-21** — beauty.sno byte-identity oracle + cross-language byte-identity gate.  Codify the gate matrix as a single script `scripts/test_gate_ec_uni_complete.sh` that runs all five gates listed below + the m1 beauty oracle (`md5 abfd19a7a834484a96e824851caee159` if that re-converges) + the current baseline (`40df9e004c3e963c99af716c65f2c970`).  Document divergence between the two md5s explicitly.

- [ ] **EC-UNI-22** — close: arch docs, GOAL updates, Phase B unblocked.  Update `ARCH-IR.md`, `ARCH-SCRIP.md`, and this file's invariant block to reflect the three-layer cake + `g_emit`.  Update each of `GOAL-SN4-JVM-EMIT.md`, `GOAL-SN4-JS-EMIT-BB-REWRITE.md`, `GOAL-SN4-NET-EMIT.md`, `GOAL-SN4-WASM-EMIT.md` to point at the new template ABI (`void name(void)`, helpers parameterized with `g_emit.*` reads, `emit_text`/`emit_byte` primitives).  Create `GOAL-SN4-X86-EMIT.md`.  Mark EC-UNI complete.  Phase B per-backend goals become active.

---

#### EC-UNI gate (must pass at every step from EC-UNI-10 onward)

```
GATE-1  beauty.sno --compile  →  md5 40df9e004c3e963c99af716c65f2c970  (882901 bytes; current baseline 2026-05-20)
GATE-2  bash scripts/test_smoke_icon.sh                                  # PASS=5
GATE-3  bash scripts/test_smoke_unified_broker.sh                        # PASS≥23
GATE-4  bash scripts/test_icon_all_rungs.sh --interp                     # PASS=194/36/35
GATE-5  bash scripts/test_smoke_{snobol4,snocone,prolog,rebus,raku}.sh   # 7/0 5/0 5/0 4/0 5/0
```

The M1 oracle md5 (`abfd19a7a834484a96e824851caee159`) from 2026-04-28 has since drifted; current baseline tracks `40df9e0...`.  EC-UNI-21 documents the divergence and either re-converges or formally retires the M1 oracle.

#### Why this is worth doing before Phase B

The five existing per-backend GOAL files (JS/JVM/NET/WASM) all describe "fix backend X" work, but today there is no clean place to put that fix — it threads through a silo walker, ad-hoc dispatchers, and partial template arms.  After EC-UNI: "fix backend X for opcode Y" is "open `SM_templates/sm_<y>.c`, find the `IS_X` arm, edit it (the literal output strings are right there in the arm)."  Single file, single fn, side-by-side with the four other backends' working code, helpers extracted only where they hide real complexity.

**Authors recorded per RULES.md "Three-construct" exception (Three-developer agreement, Milestone 1):** Lon Jones Cherryholmes · Claude Sonnet 4.7.

---

### ISOLATION — parse->lower / parse->runtime boundary firewalls

**Goal:** lex/parse produces exactly `tree_t *` and nothing else.  Two boundaries to enforce: parse->lower (consumed by `lower()`) and parse->runtime (referenced by interpreters and emitters).  Today the boundaries are partially porous; ratchet shrinks the porosity.

- [x] **ISO-1** — `lower()` signature `lower(const tree_t *prog)`.  `ParserOutput` struct + `parser_output.{c,h}` deleted; sidecar build (`label_table_build`, `prescan_defines`, `polyglot_init`) folded into the top of `lower()`.  Callers (`scrip.c` `dump_sm`/`mode_monitor`, `scrip_sm.c` `sm_preamble`, `sync_monitor_run`) simplified.  `261ff13d`.
- [x] **ISO-2** — `scripts/test_gate_lower_isolation.sh`: header firewall enforcing no `#include` from `src/lower/` into `src/frontend/` except via allowlist.  Initial state: 10 includes / 7 allowlist entries, each entry documenting why it exists and an owning relocation goal.  `1691f44f`.
- [x] **ISO-3** — Relocate `icon_gen.h` (pure Icon Byrd-box generator runtime) from `src/frontend/icon/` to `src/runtime/interp/`.  Lower firewall: 10/7 → 9/6.  Add companion `scripts/test_gate_runtime_isolation.sh` (no `src/runtime/` include into `src/frontend/` except allowlist).  Initial state: 16 includes / 8 allowlist entries.  `cb1738f6`.
- [ ] **ISO-4 (NEXT)** — `scrip_parse` subprocess: break six parsers out into a separate executable.  `scrip_parse` reads stdin (source) and writes stdout (TDump/TLump S-expression, 120 max line length).  SCRIP forks/execs and reads back, then deserializes the S-exp into a `tree_t` to pass to `lower()`.  Hardest unsolved sub-question: TDump format (defined) but no C-side *deserializer* exists yet — that has to be written.  Other sub-question: where exactly the sidecar build runs after the split (in parent after deser, or replayed via S-exp on the wire).  Recommended first sub-step: write the deserializer + roundtrip self-test on existing programs.  Do NOT introduce the process boundary until roundtrip is proven.
- [ ] **ISO-5** — Shrink lower firewall allowlist toward 0:
  - `frontend/icon/icon_lex.h` — extract `IcnTkKind` enum to `src/include/icon_tk.h`.
  - `frontend/raku/raku_driver.h` — split into `raku_parse.h` (stays) + `raku_runtime.h` (move to `src/runtime/`).
  - `frontend/prolog/{term,prolog_runtime,prolog_atom}.h` — relocate to `src/runtime/interp/prolog/`.
  - `frontend/snobol4/scrip_cc.h` — rename + relocate to `src/include/scrip_lang.h` (54 includers tree-wide; mechanical move).
- [ ] **ISO-6** — Shrink runtime firewall allowlist toward 0: same headers; coordinated with ISO-5 since they overlap.
- [ ] **ISO-7** — Stronger guarantee than the header firewall: link-time isolation test (`lower.o` + `lower_*.o` linked against a tree with all `src/frontend/*.o` absent).  Any unresolved symbol = real leakage.  Deferred from this session — proxies (signature + firewall) are weaker than a real link test, and we should be honest about that until ISO-7 lands.

**Honest scope statement (recorded so the next session does not over-trust the gates):** the firewalls are *header* firewalls.  They catch direct `#include` regressions in seconds.  They do **not** prove that `lower` reads only the AST passed to it; symbols reachable through an allowlisted header (most acutely through `scrip_cc.h`) are not detected.  ISO-7 closes that gap.

### IR Rename — builder/consumer case scheme

**Rule:** UPPERCASE builds IR (`SM_t`, `BB_t`, `SM_seq_new`, `BB_alloc`). lowercase consumes (`sm_interp_*`, `bb_print`, `bb_broker`, all `SM_templates/` dispatchers). Case at the call site tells you which side of the pipeline you're on.

- [x] IR-RN-0 — Bulk rename in 3 sed passes. 48 files. Headers `IR.h`→`BB.h`, `sm_prog.h`→`SM.h`. `9ce69899`.
- [x] IR-RN-1 — Audit `lower.c` post-rename. `c710506f`. Single finding: `sm_pat_capture_fn_arg_names` (builder helper, lowercase by mistake from IR-RN-0 Phase 3 sm_pat_* lowercase sweep) → `SM_pat_capture_fn_arg_names`. File-local, 2 sites. Sibling `lower_*.c` files clean.
- [x] IR-RN-2 — Audit emitters (`emit_bb.c`, `emit_sm.c`, `emit_core.c`). `92417a85`. Single cluster: 4 stale `ir_*` consumers (`ir_node_id`, `ir_is_generator`, `ir_walk`, `ir_walk_rec`) → `bb_*` (consume `BB_t`/`BB_graph_t`/`BB_op_t`). 18 files, 32 call sites + 1 header (`src/include/emit_ir.h`) + 4 defs. emit_bb.c and emit_sm.c clean. Apparent builder calls in emit_sm.c (BB_alloc/BB_node_alloc/BB_free, SM_seq_free) are legitimate pattern-window IR construction + destructors.
- [x] IR-RN-3 — Audit runtime (`sm_interp.c`, `sm_jit_interp.c`, `ir_exec.c`).  Two findings: `SM_label_pc_lookup` → `sm_label_pc_lookup` (read-only PC lookup; consumer disguised as builder by UPPERCASE; 13 call sites across 4 files + def in `sm_prog.c` + decl in `SM.h`) and `BB_reset` → `bb_reset` (per-node state reset; consumer-side runtime reset; 5 call sites in `ir_exec.c` + def in `scrip_ir.c` + decl in `BB.h`).  `SM_codegen` audited and kept UPPERCASE (codegen entry point, named-pipeline infrastructure; renaming would ripple beyond rung scope).  `4a1fcc63`.
- [ ] **IR-RN-4 (NEXT)** — Update arch docs (`ARCH-IR.md`, `ARCH-ICON.md`, `ARCH-SCRIP.md`).
- [ ] IR-RN-5 — Full cross-language gate run; close rung.

Reserved (untouched): `IR_LANG_*`, `SM_INTERP_*`, `SM_CALL_STACK_MAX`/`SM_GEN_LOCAL_MAX`/`SM_MAX_OPERANDS`, `BB_POOL_SIZE`, header guards, `SM_*` opcode tags, `SM_templates/`/`BB_templates/` dir names.

---

## Completed ledgers (audit trail)

### IJ-* / DAI-1..7 / IJ-HELLO matrix
All ✅. 6/6 wired hello-world matrix closed 2026-05-18.

**Key established facts:**
- Icon `--interp` (mode 2) = `--ast-run` (mode 1) at 194/265. Mode-1 flag deleted.
- Icon AST walker fully amputated (`bb_eval_value`/`bb_exec_stmt`/`icn_bb_build` gone).
- `rt_bb_once_proc` deleted; `rt_bb_pump_proc` never existed. Bridge shims = `rt_pl_once` + `icn_bb_dcg`.

### DAI-8 dead-code sweep — COMPLETE
All auditable dead code removed across C1–C17. Remaining dead-looking symbols are anchored live (Method 7 chains, @PLT references from emitter text).

| Cluster | What | Commit | LOC |
|---|---|---|---|
| C1 emit_bb.c | 75 fns + 22 decls | `a4fe1c21` | — |
| C2 emit_core+emit_sm byte-emit | ~198 fns | `895ab323` | −877 |
| C3a emit_form.h + ef_greek_port | 14 fns | `c3af9e23` | −23 |
| C3b rt.c | 7 fns + 7 decls | `a7259b9b` | −43 |
| C4 stmt_exec.c | 10 fns + typedef | `de6e7b77` | −248 |
| C5 snobol4_pattern.c | 16 fns + typedef + 9 decls | `af744aaa` | −197 |
| C6 prolog_builtin.c | 15 fns + 14 decls | `607b6aac` | −75 |
| C7 icon_runtime.c (frontend) | 12 fns + 2 globals | `2b7081c5` | −118 |
| C8 icn_runtime.c (interp) | 17 fns + state structs | `881d1a60` | −185 |
| C9 rt.c rt_pop_int | 1 fn | `ff9ee063` | −12 |
| C10 emit_wasm.c | 22 fns | `533c17c3` | −175 |
| C11 lower_icn.c | 9 fns | `04679f20` | −136 |
| C12 bb_boxes+emit_sm+scan_builtins | 20 fns | `5e854341` | −157 |
| C13 prolog_* + raku_re.c | 18 fns | `947ecd7a` | −234 |
| C14 icon_runtime+sm_interp+sm_jit_interp+stmt_exec | 20 fns | `50e025f6` | −168 |
| C15 bb_pool+lower+polyglot+snocone_lex | 10 fns | `06ea32b0` | −75 |
| C16 sm_interp.c every_table_lookup | binary-safe | `f82a34c9` | −324b |
| C17 snobol4_stmt_rt.c | 43 fns (whole file) | `d48681fb` | −447 |

**DAI-8 methodology** (kept for future audits):
- Method 1: `-ffunction-sections -fdata-sections` + `--gc-sections --print-gc-sections`, grep `.text.<name>` discards. Filter generated files + @PLT regex `"NAME(@PLT)?"`.
- Method 6: `grep -rn "\bNAME\b" src/` excluding own file. Zero hits + zero `&NAME` = safe.
- Method 7: linker-GC-dead public fn calling only other GC-dead fns → whole sub-graph deletes together.

### EC (emitter consolidation)
- [x] EC-0/1/2/2b/2c/3/4/5/6/7/WASM-SM — all ✅. Three silo files (emit_jvm.c, emit_js.c, emit_net.c) + emit_ir.c + emit_ir_targets.c deleted. Unified `emit_program(ast_prog, out, mode)`. IR walk + 3 SM-walk loops in `emit_core.c`. Net −2077 LOC at EC-5; further −427 at EC-6. ARCH-IR.md updated. Final commits: `8890d685` (EC-4), `e1c8a4ac` (EC-5), `7c33121c` (EC-6), `268619c1` (EC-WASM-SM).

### EC-UNI (template unification)
- [x] EC-UNI-0 through 9d — all ✅. Commits listed above. Axis correction (false 10-cell text/binary axis collapsed to 5-cell backend matrix) ratified in `63708215`/`7d792c59`/`073f3711`/`8308a457`. Matrix gate passes 0/365.

### IR-RN-0
- [x] Bulk rename in 3 sed passes. Builder/consumer case rule established. `9ce69899`.

### IR-CONSOLIDATE-DCG 1–7 — COMPLETE 2026-05-20
- [x] IR-CD-1/2/3 (`419fce29`), IR-CD-RENAME (`a97be4b0`), IR-CD-4 (`b97b267b`). Side-finding `pl_broker.c:364` stale extern fixed in `a97be4b0`.
- [x] IR-CD-5 (`489ff5b3`) — Deleted `ir_body` field from `IcnProcEntry` and `Pl_PredEntry_BB`. Mode-4 standalone (Option A): `rt_pl_b_end_register` calls `SM_seq_bb_add(&g_stage2.sm, cfg)`; `SM_seq_bb_add` lazy-allocates `bb_table` when `bb_cap == 0`. `pl_bb_register` signature changed to `(name, arity, int bb_idx)`. Strangler helpers simplified to single-structure lookup.
- [x] IR-CD-6 — `ARCH-IR.md` updated with IR-CONSOLIDATE-DCG invariant section and post-IR-CD file map.
- [x] IR-CD-7 — Close-out full gate floor run. Smoke 5/5/7/5/4/5 FAIL=0 each; unified_broker 23/26; test_icon_all_rungs 194/36/35; beauty md5 `40df9e004c3e963c99af716c65f2c970` unchanged. Carve-out: mode-4 standalone binaries keep `ir_body` fallback (no `SM_sequence_t` at runtime; `pl_dcg_register` wires predicates at standalone startup).

### ST2 — Stage 2 handoff is a named struct — COMPLETE 2026-05-20
`stage2_t` is the single named struct lower() hands to interp/emit, with no global shim macros, dynamically-grown sidecars, and a regression-catching firewall gate. Authorship history (ST2-1): Lon walked Claude through three honest pivots — additive `s2_*` fields kludge (retracted), `typedef stage2_t = SM_sequence_t` alias (retracted), finally the right shape: `SM_sequence_t` stays the pure opcode array, `stage2_t` is its own struct that embeds the SM sequence and owns the sidecars, `g_stage2` is a global value not a pointer. RULES.md SR-15c respected — lower's internal pass state stays file-scope `static`; ST2 addresses output-side handoff only.

- [x] **ST2-1** (`871d2f0b`) — `stage2_t` is the baton; `g_stage2` is a global value. `SM_sequence_t` restored to its sequence-only shape. Six reader shim macros (label_table, proc_table, g_pl_pred_table, g_registry, label_count, proc_count) redirect legacy names into `g_stage2`. `polyglot_init` takes `stage2_t *s2`. Canonical typedefs consolidated into `stage2.h`. Renames: `ScripModule.proc_count` → `nprocs`; lower-internal `LabelEntry` → `LabTabEntry`. `g_current_SM_seq` dissolved (40 sites).
- [x] **ST2-1b** — All six reader shim macros burned down across four sub-steps. Producers (s2-bearing) thread `s2->`; readers (deep dispatch, no s2) use `g_stage2.` literally; shim macros deleted after last reader migrates.
  - g_registry (`14655275`): 11 sites in polyglot_init → `s2->module_registry`; shim deleted.
  - label_table / label_count (`4f5d0512`): `label_table_build` threads `s2->`; `label_lookup` reads `g_stage2` literally (interp_call.c × 4, interp_hooks.c × 2). Shims deleted from `interp.h`.
  - g_pl_pred_table (`d73cded0`): 17 sites across 5 files. polyglot.c (2) threads; pl_runtime.c (10), scrip_sm.c (1), interp_hooks.c (1), lower.c (1) literal. Shim deleted from `pl_runtime.h`.
  - proc_table / proc_count (`27ad177b`): 127 sites across 10 files. Producers: polyglot.c (10), scrip_sm.c sm_resolve_proc_entry_pcs signature changed to `(stage2_t *s2)` (4 sites). Readers literal: lower.c (12), sm_interp.c (21), ir_exec.c (15), emit_sm.c (10), icn_runtime.c (32), interp_hooks.c (2), raku_builtins.c (3). Both shims deleted from `icn_runtime.h`.
- [x] **ST2-1c** (`b42b7979`) — `label_table` and `proc_table` in `stage2_t` converted from fixed-size inline arrays to dynamically-grown pointers + cap (mirror of `SM_sequence_t.instrs._grow` pattern). `stage2_reset()` allocates initial buffers at `STAGE2_LABEL_MAX` / `STAGE2_PROC_TABLE_MAX` (now initial-capacity hints). `stage2_label_grow` / `stage2_proc_grow` helpers replace cap checks at the two append sites (`polyglot.c` proc-table, `interp_label.c` label-table). Net: ~150KB .bss freed; programs with >4096 labels or >256 procs no longer silently truncate.
- [x] **ST2-2** (`b733dd13`) — `scripts/test_gate_stage2_isolation.sh` written. Token firewall: each of the six former ST2-1 shim-macro names (`g_registry`, `label_table`, `label_count`, `g_pl_pred_table`, `proc_table`, `proc_count`) must appear in source only as a qualified field reference (`.` or `->` prefix). Allowlist of 10 entries: `stage2.h` field declarations × 6, `interp_private.h` doc comment × 3, `scrip_sm.c` printf format string × 1. Mirror of `test_gate_lower_isolation.sh` / `test_gate_runtime_isolation.sh`. Honest scope: token firewall — link-time isolation analogous to ISO-7 remains a future rung.

**Authors per RULES.md "Three-construct" exception (Three-developer agreement, Milestone 1):** Lon Jones Cherryholmes · Claude Sonnet 4.7.

