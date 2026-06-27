# GOAL-CHUNKS-STEP17.md — proc/pred tables to entry_pcs

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ NO AST WALKING IN MODES 2/3/4 — see RULES.md § "NO AST WALKING IN MODES 2, 3, OR 4"         ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  Sess 2026-05-15g removed all tree_t* dereferences from sm_interp.c (mode 2) and                ║
║  sm_jit_interp.c (mode 3). Stubs print [NO-AST] <opcode> on stderr.                              ║
║                                                                                                  ║
║  If a gate breaks with [NO-AST] FOO — write fresh SM/BB lowering for FOO.                       ║
║  Do NOT restore the AST-walking call.  Do NOT route through proc_table_call or any              ║
║  other back-door that hands a tree_t* to mode-2/3/4 code.                                       ║
║                                                                                                  ║
║  Mode 1 (`--run` standalone AST interp) is unchanged and remains the reference path.        ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝


╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** SCRIP (primary) + .github (this file)
**Tracker:** sub-goal carved out of GOAL-CHUNKS.md Step 17
(session #75, 2026-05-07).  Step 17 is described in one paragraph
in the parent goal but is a multi-rung subsystem migration.

**Done when:** `IcnProcEntry` carries `int entry_pc` (no
`EXPR_t *proc` field); `g_pl_pred_table` keys map names to
`entry_pc`s (no `EXPR_t *` payload); `coro_call(entry_pc, args,
nargs)` runs proc bodies via SM dispatch on the chunk; same for
Prolog clause execution; `polyglot.c` stores no IR pointers; the
isolation gate forbids `EXPR_t *` in the gated runtime files'
function signatures.  Standard CHUNKS gate set + full Icon corpus
+ Prolog smoke (extended to `--run` once consumer-side migrations
land).

> **CH-17i-survey-mode3 LANDED 2026-05-09** — `docs/CHUNKS-step17i-survey-mode3.md`.
> 177 Icon --run PASS → 111 --run diverge (all semantic; root cause: generator
> kinds inside proc bodies emit SM_PUSH_EXPR+SM_BB_PUMP, incompatible with SM dispatch).
> Prolog: 4 PASS → 1 fail (initialization/2 bridge gap). Sub-rungs: CH-17i-every-suspend,
> CH-17i-bang-concat, CH-17i-section, CH-17i-limit-random, CH-17i-prolog-initialization.
> SCRIP @ `dfe68c5b`.
>
> **CH-17i-every LANDED 2026-05-10** — first half of CH-17i-every-suspend.  AST_EVERY
> migrated off legacy `emit_push_expr + SM_BB_PUMP` onto new `SM_BB_PUMP_EVERY <every_id>`
> (mirrors CH-17f's `SM_BB_ONCE_PROC name/arity` pattern).  AST registered in
> `g_every_table` at lower-time; SM bytecode and value stack carry only the integer id.
> Runtime handler does `every_table_lookup → coro_eval → bb_broker(BB_PUMP, NULL, NULL)` —
> body_fn NULL because `coro_bb_every` already runs the do-clause via `bb_exec_stmt`
> (passing `pump_print` would double-print, verified empirically).  Pushes NULVCL to
> balance proc-body's trailing `SM_VOID_POP` (legacy was net-stack-zero — root cause
> of the 111 --run divergences).  Files: `sm_prog.h/c` (+enum +name), `sm_interp.h/c`
> (+every_table API + handler), `sm_codegen.c` (+JIT mirror), `sm_lower.c` (carve case
> out of legacy fallthrough).  Gates byte-identical: smoke ×6 PASS (7/7, 5/5, 5/5,
> 5/5, 5/5, 4/4), isolation PASS, unified_broker PASS=49, broad_unified_broker PASS=6,
> scrip_all_modes PASS=2, Icon `--run` PASS=177 FAIL=56 XFAIL=30 TOTAL=263.
> New gain: `--run` rung01–04 5/24 → 17/24 (+12). All six rung01_paper_*
> byte-identical. rung02 6/8 (the 2 FAILs are pre-existing under `--run` too).
> rung03/04 (7) still fail on AST_SUSPEND — that's the next sub-rung.  Documented in
> `docs/CHUNKS-step17i-every-validation.md`.  SCRIP @ `8a85285e`.
>
> **CH-17i-suspend LANDED 2026-05-10** — second half of CH-17i-every-suspend.
> AST_SUSPEND migrated off legacy `emit_push_expr + SM_BB_PUMP` onto a new
> direct-yield primitive `SM_SUSPEND_VALUE` (NOT the g_*_table pattern of
> CH-17i-every / CH-17f).  Rationale: AST_SUSPEND has no `bb_node_t` shape —
> its existing semantics (coro_stmt.c:88) are pure in-frame state mutation,
> and the actual yield is performed by the *outer* loop's swapcontext.
> Under SM dispatch (proc bodies routed through `sm_call_proc` since CH-17g)
> there is no outer-loop AST walker to observe `FRAME.suspending`, so the
> SM-side equivalent is a primitive opcode that does the swapcontext directly.
> Mirrors JCON's `ir_Succeed` (irgen.icn:962, 970) and the swapcontext half
> of `coro_bb_suspend` (icon_gen.c:211–240).  New helper `sm_yield_to_caller(v)`
> in coro_runtime.c stashes `v` in `active_coro->yielded` and `swapcontext`s
> to caller_ctx; on resume control falls back to the SM dispatch loop, where
> the do-clause SM runs next.  Lowering shape: `[expr] / SM_JUMP_F L_end /
> SM_SUSPEND_VALUE / [do-clause] / SM_VOID_POP / SM_PUSH_NULL / SM_JUMP /
> L_end / L_finally`.  Net stack delta +1 either path; outer proc-body
> SM_VOID_POP balances.  Files: `sm_prog.h/c` (+enum +name), `sm_lower.c`
> (carve case out of legacy fallthrough), `coro_runtime.c` (+yield helper),
> `sm_interp.c` (+handler), `sm_codegen.c` (+JIT mirror).  Gates byte-identical:
> smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4), isolation PASS, unified_broker
> PASS=49, scrip_all_modes PASS=2, Icon `--run` PASS=177 FAIL=56 XFAIL=30
> TOTAL=263.  New gain: `--run` rung01–04 17/24 → 20/24 (+3) — exactly
> rung03_suspend_gen, rung03_suspend_gen_compose, rung03_suspend_gen_filter
> flipping from FATAL to PASS.  `--run` rung01–04 same 17/24 → 20/24
> (+3) via the `h_suspend_value` JIT mirror.  Remaining 4 FAILs in rung01–04
> are pre-existing (rung02_proc_fact JIT segfault, rung03_suspend_fail and
> rung03_suspend_return on `return E` — separate territory).  Documented in
> `docs/CHUNKS-step17i-suspend-validation.md`.  SCRIP @ `fd1c2b6a`.
>
> **CURRENT RUNG: CH-17i-bang-concat** — Phase 1 ✅ LANDED 2026-05-10
> (SCRIP `a8a064a0`).  Phases 2 / 3 / 4 ✅ SEQUENCED 2026-05-10
> (audit doc `CHUNKS-step17i-bang-concat-phase234-audit.md` ; SCRIP
> `f78d366c`).  Phase 1 closed rung15_real_swap_lconcat
> (the empirical anchor) by adding a scalar value-path lowering for
> AST_LCONCAT mirroring AST_CAT.  Phases 2 (AST_LCONCAT generative),
> 3 (AST_BANG_BINARY scalar), and 4 (AST_BANG_BINARY generative) are
> all sequenced behind CH-17g-irrun-execution on the same basis: a
> 706-program audit sweep across Icon (271) + Raku (186) + Snocone
> (114) + Prolog (135) under `--run` with `SCRIP_EXPRS_AUDIT=1`
> shows **zero** SM_PUSH_EXPR fires for any of these kinds today —
> precisely because proc bodies are still tree-walked via
> `coro_pump_proc_by_name` → `coro_eval`, an in-host-process AST
> walker that Mode 4 cannot embed in a standalone binary.  Mirrors
> CH-15-SURVEY's deferral of CH-15b on identical reasoning.
>
> ⚠ **Sequenced ≠ optional.**  These phases are **required** for
> CH-17i-mode4-icon-prolog (Mode 4 for Icon/Prolog).  An emitted asm
> binary cannot fall back to `coro_eval`; every kind a 177-PASS
> Icon program uses must be in compiled SM by the time Mode 4
> ships.  Same finding applies to sister rungs CH-17i-section and
> CH-17i-limit-random.  Sequence:
> CH-17g-irrun-execution → CH-17i-bang-concat-{2,3,4} +
> -section + -limit-random + -prolog-initialization →
> CH-17i-mode3-completeness → CH-17i-mode4-icon-prolog →
> CH-17i-final-isolation.  Re-trigger for the per-kind rungs:
> any non-zero `FIRES:` count from the canonical audit script
> after CH-17g lands (see audit doc §"Audit script" /
> §"Architectural sequencing").
>
> Original framing of the rung as a single migration off the legacy
> `emit_push_expr + SM_BB_PUMP` fallthrough block (sm_lower.c:1371–1380)
> covered AST_BANG_BINARY + AST_LCONCAT both ways (scalar + generative).
> Phase 1 closed the most-impactful slice (AST_LCONCAT scalar = the
> rung15 anchor); the remaining phases are an open follow-on rung set.
> Both AST kinds have existing `bb_node_t` shapes in `coro_eval`
> (icn_bang_binary_state_t / icn_binop_gen_state_t with op=ICN_BINOP_CONCAT)
> for the generative paths — Phases 2 and 4 will use those shapes via
> the unified opcode pattern.
>
> **AUDIT 2026-05-10 (orientation session, no code written):**
>
> 1. **Reachability confirmed via empirical sweep.** Across the 271-program
>    Icon corpus under `--run` with `SCRIP_EXPRS_AUDIT=1`: zero programs fire
>    SM_PUSH_EXPR, six fire SM_PUSH_EXPRESSION (rung33_case_* + rung36_jcon_kwds,
>    all expression-shaped — not legacy fallthrough).  But targeted probes on
>    programs using `|||` (AST_LCONCAT) and `!` (AST_BANG_BINARY) show the
>    legacy fallthrough DOES fire on real programs not exercised by the sweep:
>    - `rung15_real_swap_lconcat.icn` — IR PASS, SM FAIL (rc=134, "sm_interp:
>      stack underflow" then SIGABRT).  Audit reports
>      `[CHUNKS-AUDIT] SM_PUSH_EXPR fired at pc=3 (legacy AST_t* path)`.
>      This is the cleanest empirical anchor: AST_LCONCAT in `main`'s body
>      hits the legacy fallthrough, SM_BB_PUMP is net-stack-zero, trailing
>      proc-body SM_VOID_POP underflows.  Same root cause CH-17i-every and
>      CH-17i-suspend addressed for their kinds.
>    - `rung11_bang_augconcat_*` (4 of 5 programs) — IR PASS, SM FAIL but
>      mostly via a different mechanism (no SM_PUSH_EXPR fire visible in
>      the audit).  Investigation deferred — likely augmented-concat (`||:=`)
>      lowering issue separate from the bang-concat rung.  rung11_bang_str
>      already PASSes both modes.
>    - `rung22_lists_bang_list` and `rung13_table_iterate` — IR FAIL too;
>      out of scope per "FAIL/XFAIL programs stay there".
>
> 2. **Stale claim corrected.** The previous version of this note said
>    "Expected gain: rung04_string_* programs".  All five rung04_string_*
>    programs already PASS in all three modes — pulled across by
>    CH-17i-every+suspend.  The actual headline gain for this rung is
>    `rung15_real_swap_lconcat` flipping FAIL→PASS.
>
> 3. **DESIGN DECISION (Lon, sess 2026-05-10): UNIFIED opcode + table.**
>    Instead of CH-17i-every's per-kind shape (one opcode per AST kind, one
>    `g_<kind>_table` per kind), this rung introduces a SINGLE generic
>    opcode + SINGLE shared table that handles AST_BANG_BINARY, AST_LCONCAT,
>    and (in subsequent rungs) AST_SECTION*, AST_LIMIT, AST_RANDOM.  Rationale:
>    five upcoming rungs all have identical handler bodies modulo the table
>    they index — a clean refactor avoids five rounds of copy-paste.
>
>    **Proposed shape** (next session decides final names):
>      - **Opcode:** `SM_BB_PUMP_AST` with `a[0].i = ast_id`.
>      - **Table:** `g_ast_pump_table` (AST_t** array), with API
>        `ast_pump_table_register(AST_t *)` / `ast_pump_table_lookup(int)` /
>        `ast_pump_table_reset()`.  Same lifetime model as g_every_table:
>        borrowed AST pointers, populated by sm_lower at lower-time, reset
>        on sm_program_free.
>      - **Handler:** `lookup → coro_eval → bb_broker(BB_PUMP, NULL, NULL);
>        push NULVCL` — identical to h_bb_pump_every.  Body-fn NULL
>        because coro_bb_binop / coro_bb_bang_binary already run their
>        own discovery via bb_exec_stmt or yield to caller — passing
>        pump_print would double-print (verify empirically per kind).
>      - **JIT mirror:** `h_bb_pump_ast` in sm_codegen.c, mirroring
>        h_bb_pump_every modulo the table function.
>      - **sm_lower.c:1371–1380:** carve AST_BANG_BINARY and AST_LCONCAT
>        cases out of the fallthrough; emit
>        `sm_emit_i(p, SM_BB_PUMP_AST, ast_pump_table_register(e))`.
>        Leave AST_LIMIT, AST_RANDOM, AST_SECTION* in the fallthrough for
>        their own rungs (CH-17i-section, CH-17i-limit-random) which will
>        carve them out and use the same opcode/table.
>      - **Open question — should CH-17i-every be retroactively migrated
>        onto the unified opcode/table?** No.  Keep CH-17i-every's
>        SM_BB_PUMP_EVERY as-is to preserve its already-validated test
>        coverage; AST_EVERY's existing per-kind shape works and has
>        proof-of-correctness.  The unified opcode is for the kinds
>        that haven't yet migrated.  If later a uniform refactor wants
>        to consolidate, that's its own (much smaller) cleanup rung.
>
> 4. **Validation plan for the rung.**
>      - Smoke ×6 byte-identical (7/7, 5/5, 5/5, 5/5, 5/5, 4/4)
>      - Isolation gate PASS
>      - **Headline:** `rung15_real_swap_lconcat --run` FAIL→PASS
>        byte-identical to `--run` output ("hello world\n")
>      - `rung15_real_swap_lconcat --run` same (via JIT mirror)
>      - `--run` rung01–04 byte-identical or +N (no regression)
>      - Icon corpus 263 byte-identical to post-CH-17i-suspend baseline
>        (177 PASS / 56 FAIL / 30 XFAIL)
>      - unified_broker 49/0 unchanged
>      - scrip_all_modes 2/0 unchanged
>      - Document in `docs/CHUNKS-step17i-bang-concat-validation.md`
>
> 5. **rung11_bang_augconcat_* deferred.** Those failures are not blocked
>    by AST_BANG_BINARY/LCONCAT lowering per the audit (no SM_PUSH_EXPR fire).
>    Likely separate territory (augmented assignment in proc body); revisit
>    after CH-17i-bang-concat lands to see if any flip as side effect, then
>    file a separate rung for whatever remains.
>
> 6. **SCOPE DISCOVERY (sess 2026-05-10, second pass):** the rung is wider
>    than the unified-opcode model alone covers.  Two findings forced this:
>
>    **(a) `--run` and `--run` do NOT share runtime today.**
>    CH-17g-irrun-execution is `- [ ]` (NOT landed).  Under `--run`
>    non-SNO programs still go through `polyglot_execute`'s legacy AST
>    walker.  Under `--run` they go through SM dispatch.  This is why
>    rung15 PASSes under `--run` (legacy walker handles AST_LCONCAT
>    via `interp_eval.c:3827` — a clean value-context computation:
>    `interp_eval(c0) ++ interp_eval(c1)`) but FAILs under `--run`
>    (legacy fallthrough fires SM_PUSH_EXPR + SM_BB_PUMP, which is
>    net-stack-zero — the proc-body trailing SM_VOID_POP underflows).
>    The "modes 2 and 3 share the runtime" property is ASPIRATIONAL
>    until CH-17g-irrun-execution lands.
>
>    **(b) AST_LCONCAT and AST_BANG_BINARY have a NON-GENERATIVE case
>    that needs proper value-context lowering, not broker dispatch.**
>    `coro_eval` only enters the bb_node_t path when at least one child
>    is `is_suspendable`; otherwise it `break`s and "lets interp_eval
>    handle it".  Today `lower_expr` for AST_LCONCAT has NO scalar path
>    — it falls straight to the legacy fallthrough.  rung15
>    (`s := "hello" ||| " world"`) is the trivial scalar case and has
>    been broken under `--run` since these opcodes existed.
>
>    AST_CAT (line 740) demonstrates the right shape for the scalar case:
>    `lower_expr(c0); lower_expr(c1); SM_CONCAT;` — pure value-context.
>    AST_LCONCAT can mirror this exactly; the SPITBOL semantics
>    (Icon ||| is a string-concat alias when both operands are strings —
>    see interp_eval.c:3827) match SM_CONCAT's behavior 1:1.
>
>    AST_BANG_BINARY is harder.  Even in scalar context (one-shot value)
>    it's `proc ! list` — apply proc to each element of list.  No SM
>    opcode mirrors this directly; the runtime helper would still need
>    to walk the list and call proc.  Likely needs its own opcode
>    `SM_BANG_BINARY` taking proc-name + arg-from-stack and producing
>    one yielded value (or the runtime calls coro_bb_bang_binary directly).
>
>    **REVISED rung structure (proposed; awaits Lon decision):**
>      - **Phase 1 — AST_LCONCAT scalar value path.**  ✅ LANDED 2026-05-10.
>        Mirrors AST_CAT: `lower_expr(c_i); SM_CONCAT` between adjacent pairs.
>        No new opcode.  Headline: `rung15_real_swap_lconcat` flips
>        `--run` / `--run` FAIL→PASS byte-identical to `--run`.
>        Icon `--run` corpus: 100→101 PASS, +1 (zero regressions).
>        Audit clean: zero SM_PUSH_EXPR fires post-rung anywhere on the
>        Icon corpus.  Documented in
>        `docs/CHUNKS-step17i-bang-concat-phase1-validation.md`.
>        SCRIP @ `a8a064a0`.
>      - **Phase 2 — generative path via unified opcode.**  When at
>        least one child of AST_LCONCAT is `is_suspendable`, emit the
>        unified `SM_BB_PUMP_AST` opcode + `g_ast_pump_table` registration
>        (the option-B refactor described in (3) above).  **SEQUENCED
>        2026-05-10** behind CH-17g-irrun-execution — 706-program audit
>        (Icon 271 + Raku 186 + Snocone 114 + Prolog 135) under `--run`
>        reports zero SM_PUSH_EXPR fires today, but the kind is required
>        for Mode 4 on Icon (emitted binary cannot tree-walk).
>        Re-trigger when the canonical audit script
>        (`docs/CHUNKS-step17i-bang-concat-phase234-audit.md` §"Audit
>        script") returns a non-zero `FIRES:` line — which becomes
>        possible once CH-17g lands.  Same precedent as CH-15-SURVEY's
>        deferral of CH-15b.
>      - **Phase 3 — AST_BANG_BINARY scalar value path.**  Add value-
>        context handling.  Even scalar `!list` is iteration (apply
>        per-element); needs runtime helper invocation, not a single
>        opcode.  **SEQUENCED 2026-05-10** behind CH-17g-irrun-execution;
>        same audit basis as Phase 2.  Required for Mode 4 on Icon.
>        See `docs/CHUNKS-step17i-bang-concat-phase234-audit.md`
>        §"Architectural sequencing".
>      - **Phase 4 — AST_BANG_BINARY generative path.**  Same unified
>        opcode pattern as Phase 2 if/when it lands.  **SEQUENCED
>        2026-05-10** behind CH-17g-irrun-execution; same audit basis.
>        Required for Mode 4 on Icon.
>
>    This is still ONE rung in spec but lands as 2–4 commits internally.
>    Or carve into two adjacent rungs: CH-17i-lconcat (phases 1+2) and
>    CH-17i-bang (phases 3+4).  Lon's call.
>
>    **Empirical anchor unchanged:** rung15_real_swap_lconcat flips
>    FAIL→PASS under `--run` after Phase 1 alone (because rung15's
>    children are scalar string literals — the generative path doesn't
>    fire).  Phase 2 unblocks programs with `gen ||| gen` shapes;
>    inventory needed once Phase 1 is in.
>
> The ByrdBox `test_icon.c` reference (≈80 lines for the multi-generator
> example) and Proebsting "Simple Translation of Goal-Directed Evaluation"
> show the four-port wiring at the assembly level — useful as a sanity check
> that the lowering produces the right control flow shape.  Both available
> as uploaded artifacts in the originating session.
>
> **Sub-rung order from CH-17i-survey-mode3.md:**
>   - CH-17i-bang-concat — AST_BANG_BINARY + AST_LCONCAT (next; introduces unified opcode/table)
>   - CH-17i-section — AST_SECTION + AST_SECTION_PLUS + AST_SECTION_MINUS (reuse unified opcode)
>   - CH-17i-limit-random — AST_LIMIT + AST_RANDOM (reuse unified opcode)
>   - CH-17i-prolog-initialization — initialization/2 bridge
>
> When all sub-rungs land, the legacy `emit_push_expr + SM_BB_PUMP` fallthrough
> block in sm_lower.c contains zero kinds.  At that point CH-17i-mode4-icon-prolog
> + CH-17i-final-isolation (the closing rungs of CH-17i) become unblocked.

---

## Why this file exists

GOAL-CHUNKS.md Step 17 reads:

> In `polyglot_init`, replace `proc_table[i].proc = proc;` with:
> lower the proc body as a named SM chunk during the same pass,
> record `proc_table[i].entry_pc = chunk_pc`.  Same for
> `pl_pred_table_insert(name, entry_pc)`.  Migrate `coro_call`
> ...  Delete `EXPR_t *proc` from proc_table struct.

That single paragraph touches:

- `polyglot.c` (proc_table / pred_table population)
- `sm_lower.c` (must emit named proc-body chunks)
- `coro_runtime.c` / `coro_runtime.h` (proc_table struct, `coro_call`)
- `coro_value.c`, `coro_stmt.c`, `raku_builtins.c`, `interp_hooks.c`,
  `interp_eval.c` (every consumer of `proc_table[i].proc` /
  `pl_pred_table_lookup`)
- `pl_runtime.c` + `pl_broker.h` (Prolog BB engine entry points
  that today take `EXPR_t *`)
- Two static-storage subsystems keyed on EXPR_t identity
  (`static_get` / `static_set` for Icon `static` vars; trail-mark
  semantics in Prolog)

This is a multi-session ladder, not a single rung.  Splitting it
into named rungs in this file gives each session a clean target
and gates.  Mirrors the precedent of `GOAL-MODE4-EMIT.md`
(carve-out of Step 8 + 19 from the same parent goal).

GOAL-CHUNKS.md Step 17 stays as a pointer — this file owns the
destination.

---

## Architectural target

**Today (pre-CH-17a):**

```
                       polyglot_init                sm_lower
                            │                          │
   prog (CODE_t*) ──► proc_table[i].proc=EXPR_t*  ──► SM_Program
                       g_pl_pred_table[name]=EXPR_t*    (skips ICN/PL stmts;
                                                         their proc bodies
                                                         walked at runtime
                                                         by coro_call /
                                                         pl_box_choice)
```

**After this sub-goal closes:**

```
                       polyglot_init           sm_lower (extended)
                            │                          │
   prog (CODE_t*) ──► proc_table[i].name      ──► SM_Program containing
                                                   named proc-body chunks
                                                   (forward-jumped around)
                            │                          │
                            └──► entry_pcs resolved ──►┘
                                 from sm_label_pc_lookup

                            ▼
                       coro_call(entry_pc, args, nargs)
                            │
                            ▼
                       SM dispatch on chunk; frame setup unchanged;
                       generators use the SUSPEND/RESUME machinery
                       laid down in CH-14
```

**The proc_table struct after migration:**

```c
typedef struct {
    const char *name;
    int         entry_pc;     /* SM_Program pc of named proc-body chunk */
    int         nparams;      /* parameter count (was: read from proc->ival) */
    /* No EXPR_t* — IR is gone after sm_preamble for non-SNO too */
} IcnProcEntry;
```

**Frame-slot resolution** moves from runtime (`icn_scope_patch`
mutates `E_VAR.ival` in place during `coro_call`) to lower-time
(scope built when the proc body's chunk is emitted; SM ops carry
slot indices already).  This eliminates the in-place IR mutation
flagged in GOAL-CHUNKS truth-telling preamble item 4.

**Static-variable storage** for Icon `static` vars switches keys
from EXPR_t identity to entry_pc + name pairs.

---

## Rungs (in order; one per session)

### CH-17a — Scaffolding: add entry_pc field, populate via existing labels

**Scope:** Pure addition.  Two file changes only.

- Add `int entry_pc` to `IcnProcEntry` (after `proc`, not
  replacing it).  Initialise to `-1` in `polyglot_init` alongside
  the existing `proc` write.
- Add a new helper `sm_resolve_proc_entry_pcs(SM_Program *p)` in
  scrip_sm.c that, after `sm_lower` returns, walks `proc_table`
  and `g_pl_pred_table` (with a parallel `entry_pc` slot added
  to the latter) and populates `entry_pc` via
  `sm_label_pc_lookup(prog, name)`.  When the lookup returns -1
  (i.e. sm_lower didn't emit a named chunk for this proc — the
  baseline today for every Icon proc and Prolog clause), leave
  the field as -1.  No assertion failure: this rung does not
  require any chunks to exist.
- Optional env-gated diagnostic `SCRIP_PROC_ENTRY_PCS=1` prints
  proc_table and pred_table contents after resolution, showing
  which procs got entry_pcs (none, in this rung).
- No consumer-side changes.  `coro_call` etc. still take
  `EXPR_t *proc` as today.

**Gates:** standard CHUNKS set + smoke ×6 + isolation gate +
unified_broker.  Because CH-17a is pure addition with no producer
or consumer flips, all gates are byte-identical to baseline.

**Rationale for landing this first:** subsequent rungs need the
entry_pc field to populate.  Splitting the scaffolding from the
real lowering work keeps each rung small enough to gate cleanly.

### CH-17b — sm_lower emits named-chunk SKELETONS for Icon/Raku procs

**Scope:** sm_lower.c only.  Pre-loop pass over `prog`'s
statements: for each `LANG_ICN`/`LANG_RAKU` stmt whose subject is
an `E_FNC` proc-def, emit a chunk SKELETON (no body):

  `SM_JUMP skip_proc_<name>`
  `SM_LABEL "<name>"`            (named, via sm_label_named)
  `SM_RETURN`
  `SM_LABEL skip_proc_<name>`    (anonymous skip target)

**Skeleton-only deliberate choice (sess #75):** body lowering is
non-trivial — Icon proc bodies are EXPR_t chains, not STMT_t,
and frame-slot resolution via `icn_scope_patch` happens at
runtime inside `coro_call` today.  Migrating that to lower-time
is its own architectural decision that deserves its own rung
(CH-17b').  The skeleton-only rung lands first because it is the
minimal change that lets `sm_resolve_proc_entry_pcs` (CH-17a)
populate non-(-1) entry_pcs, validating the resolver end-to-end
on real corpora.

**Producer fires; body is empty; consumer is dormant.**  CH-17a's
resolver now finds entry_pcs for every Icon/Raku proc.  Verify
via `SCRIP_PROC_ENTRY_PCS=1`.  But nothing yet calls those
chunks — `coro_call` still walks IR.  And even if a future
consumer called them today, they'd return immediately (empty
body), which is fine because no consumer flip has happened yet.

**Gates:** standard set + Icon corpus baseline (must be
byte-identical: 186/47/30 of 263).  Skeleton chunks are
forward-jumped over so execution falls through them.

### CH-17b' — Lower Icon/Raku proc bodies into the chunks

**Scope:** the actual body work.  For each chunk emitted by
CH-17b, replace the immediate `SM_RETURN` with the lowered body
SM ops (then `SM_RETURN`).  Body lowering re-uses `lower_expr`
machinery, but wrapped in a per-proc context that pre-builds the
scope so frame-slot indices are baked in instead of resolved at
runtime by `icn_scope_patch`.

**Gating note:** the body lowering hits `E_EVERY`, `E_SUSPEND`,
etc. — kinds CH-15b will later migrate.  For CH-17b', those still
emit the legacy `SM_PUSH_EXPR + SM_BB_PUMP` shape.  That's
acceptable here because (a) consumer-side proc dispatch isn't
flipped yet — these chunks won't be executed; (b) once they are
flipped (CH-17c), the `SM_PUSH_EXPR + SM_BB_PUMP` paths inside
proc bodies will start firing on real corpora, which is exactly
what unblocks CH-15b's validation (per CH-15-SURVEY).

**Gates:** standard set + Icon corpus baseline byte-identical.

### CH-17b'' — Bake frame-slot resolution into chunks at lower-time

**Scope:** the second half of CH-17b's original "scope built when
the proc body's chunk is emitted; SM ops carry slot indices already"
goal text — split out into its own rung when CH-17b' (sess #78)
deferred frame-slot baking and left chunks emitting `SM_PUSH_VAR
<name>` for params and locals.  That deferred shape would have
broken CH-17c on consumer flip: `SM_PUSH_VAR` reads the global NV
table, missing the IcnFrame.env values that `coro_call` populates
with arguments.

**Why a separate rung was carved (sess #80, 2026-05-07):** CH-17b'
landed with the closing note "Frame-slot resolution stays at runtime
(`icn_scope_patch` unchanged); E_VAR lowers to `SM_PUSH_VAR <name>`
name-keyed via NV_GET_fn — no scope-patch needed at lower-time."
That deferral, while letting CH-17b' land cleanly, leaves the
chunks semantically wrong for SM dispatch — the params/locals point
at NV instead of FRAME.env.  CH-17c was about to inherit a broken
chunk shape.  Carving CH-17b'' into its own rung (per the sub-goal
file's precedent of CH-17a / CH-17b / CH-17b' splits) keeps each
step small and gateable while honouring the original Step 17 spec.

**Implementation:**

- Two new opcodes in `sm_prog.h`: `SM_LOAD_FRAME` / `SM_STORE_FRAME`
  with `a[0].i = slot index`.  Handlers in `sm_interp.c` route
  through three pure-DESCR_t forwarders defined in `coro_runtime.c`
  (`icn_frame_env_active`, `icn_frame_env_load`, `icn_frame_env_store`)
  — no EXPR_t leakage across the SM/IR boundary.  Outside an Icon
  frame (frame_depth == 0), both opcodes push FAILDESCR / clear
  last_ok, mirroring SM_LOAD_GLOCAL's outside-of-generator
  semantics.  JIT codegen stubs are named-FATAL (M5 territory).

- `sm_lower.c` chunk-body emission loop builds a per-proc
  `IcnScope` mirroring `icn_scope_patch` but without IR mutation:
  params first (slots 0..nparams-1), then E_GLOBAL-decl names,
  then body E_VAR walk.  Globals (registered via `global_register`
  at polyglot_init) are excluded from the scope — they bridge to
  the SNO NV store, matching the IR walker's slot=-1 → NV_GET_fn
  fallback.  Keywords (`&`-prefixed names) are also excluded.
  Stored in file-static `g_chunk_scope`, gated on
  `g_chunk_body_lowering`.

- `lower_expr`'s E_VAR and E_ASSIGN(LHS=E_VAR) cases consult
  `g_chunk_scope`.  In-scope names emit `SM_LOAD_FRAME slot` /
  `SM_STORE_FRAME slot`; out-of-scope names (globals, keywords,
  unscoped) fall through to `SM_PUSH_VAR` / `SM_STORE_VAR` —
  unchanged emission for stmt-level lowering and for true globals
  inside chunks.

**Producer-side empirical proof:** `--dump-sm --run
test/icon/palindrome.icn` shows the chunk for `palindrome` (pc 1–52)
now emits `SM_LOAD_FRAME` / `SM_STORE_FRAME` for `s`, `i`, `j` —
was `SM_PUSH_VAR "s"` / `SM_STORE_VAR "i"` etc. in CH-17b'.
Builtin / proc-name function references inside E_FNC argument
position (e.g. `write`, `palindrome`) also currently get slot
indices — this mirrors how `icn_scope_patch` adds them at runtime;
the slot is dead because the IR walker dispatches E_FNC by
`children[0]->sval` string before evaluating the function-name
child as a value.  CH-17c's E_FNC-shape rework will fix this in
the lowering (don't lower children[0] as a value when the call
target is name-resolvable).

**Pre-existing E_FNC malform note (uncovered by this rung,
inherited from CH-17b'):** the `case E_FNC` lowering at
sm_lower.c:832–834 does `lower_expr(children[0..nargs-1])` then
`SM_CALL s=e->sval nargs` — pushing `nargs+1` values but popping
only `nargs`.  Result: chunks containing E_FNC have a stack-leak
shape that would corrupt execution if reached.  Pre-existing in
CH-17b'; not introduced here.  CH-17c must fix.

**Chunks remain dead code.**  `coro_call` still walks IR
(`coro_value.c:495–501`); chunks are forward-jumped over by
SM_JUMP.  Gates byte-identical because the chunks are unreachable
from any real program path until CH-17c flips the consumer.

**Gates:** standard set byte-identical to baseline.  Smoke ×6
PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4); isolation gate PASS;
csnobol4 Budne PASS=61; unified_broker PASS=49; full Icon corpus
PASS=186 FAIL=47 XFAIL=30 TOTAL=263.

### CH-17c — Flip Icon/Raku consumers: coro_call(entry_pc)

**Scope:** the consumer-side migration.  `coro_call` gains a
companion `sm_call_proc(int entry_pc, DESCR_t *args, int nargs)`
that runs the chunk via SM dispatch.  Per-call-site flip:
`coro_call(proc_table[i].proc, ...)` becomes
`sm_call_proc(proc_table[i].entry_pc, ...)`, gated by
`entry_pc != -1` (fall back to the legacy `coro_call` if -1).

Per goal spec: "frame setup unchanged."  `coro_call`'s scope
build, env init, static-var persistence, and frame-stack push
move to a shared `proc_frame_setup` helper that both `coro_call`
and `sm_call_proc` use.  `sm_call_proc`'s body executes the
chunk via the existing SM dispatch loop; `coro_call`'s body
still walks IR (legacy fallback for procs whose chunks didn't
land — increasingly empty as CH-15b proceeds).

**Gates:** standard set + full Icon corpus PASS=186 +
`unified_broker` PASS≥48 + Raku full suite at baseline.

### CH-17d — sm_lower emits named chunks for Prolog predicates

**Scope:** symmetrical to CH-17b but for Prolog.  For each
`LANG_PL` stmt whose subject is `E_CHOICE` or `E_CLAUSE`, emit a
named chunk for the body.  Multi-clause predicates fold into a
single E_CHOICE chunk that internally dispatches across clauses
(SM analog of `pl_box_choice`).

Wire `pl_pred_table_insert` to record the entry_pc instead of
the raw EXPR_t.  For the OR-box semantics, the chunk's body is
itself a sequence of clause-chunks chained via SM analogs of
`bb_seq` / `pl_box_cat`.

**Producer fires; consumer is dormant** for the same reason as
CH-17b.  Standard gates pass because nothing reads the new
entry_pcs yet.

### CH-17e — Flip Prolog consumers: pl_box_choice_pc and friends

**Scope:** the consumer-side migration for Prolog.  Add chunk-
shaped variants:

  `pl_box_choice_pc(int entry_pc, Term **args, int arity)`
  `pl_box_clause_pc(int entry_pc, Term **args, int arity)`
  `pl_box_builtin_pc(int entry_pc, Term **env)`

`pl_box_cut()` already takes no args, no change.

Flip `pl_pred_table_lookup` to return `entry_pc` (or a struct
carrying it).  Each consumer site
(`interp_eval.c:2300`, `pl_runtime.c:1885,1960`,
`interp_hooks.c:163`, `polyglot.c:292`, `interp_eval.c:2749`) is
flipped; legacy `_box_*(EXPR_t *)` variants stay only for the
duration of this rung's two-system swap.

After this rung lands, **`--run` Prolog should work end-to-end
for the first time** because the SM_BB_ONCE → coro_eval → bb_eval_value
crash path is replaced with proper Prolog box dispatch on chunks.
This unblocks Step 16.  Step 16 reactivates here.

**Gates:** standard set + Prolog smoke extended to `--run` +
representative Prolog corpus subset.

### CH-17f — Migrate Step 16 (Prolog clause kinds at sm_lower.c:1213)

**Scope:** as per GOAL-CHUNKS.md Step 16 spec, but executed with
the entry_pc + chunk-shaped consumer infrastructure now
available.  Each of the six kinds (E_CHOICE, E_CLAUSE, E_CUT,
E_UNIFY, E_TRAIL_MARK, E_TRAIL_UNWIND) gets per-kind SM lowering;
the legacy `emit_push_expr + SM_BB_ONCE` path is deleted at the
producer; the consumer reads entry_pcs via the helpers from
CH-17e.

**Gates:** as per Step 16 + the now-reachable Prolog `--run`
crosscheck against the SPITBOL oracle (well, against `--run`,
since SPITBOL doesn't run Prolog).

### CH-17g — Drop EXPR_t *proc from IcnProcEntry; lift code_free gate

**CARVED into three sub-rungs sess 2026-05-09** — empirical state at
CH-17f close: eight `coro_call(proc_table[i].proc, args, nargs)` consumer
sites still read `.proc` directly outside the trampoline (CH-17c only
flipped `proc_trampoline` / `gather_trampoline`).  Static-variable
storage in `coro_runtime.c:155–183` is still keyed on `EXPR_t*`.  Chunk
bodies still emit `SM_PUSH_EXPR + SM_BB_PUMP` for unmigrated generator
kinds (per CH-17b' close note).  Each precondition for the field-drop
needs its own rung.  Mirrors how CH-17b/b'/b'' were carved.

#### CH-17g-call-sites — flip the eight residual consumer sites

**Scope:** mirror CH-17c's trampoline-side flip for the call sites it
didn't reach.  Add a small dispatch helper `proc_table_call(int pi,
DESCR_t *args, int nargs)` next to `sm_call_proc` in `coro_runtime.{c,h}`:

  - if `proc_table[pi].entry_pc >= 0`, call `sm_call_proc`
  - else, fall back to `coro_call(proc_table[pi].proc, args, nargs)`

Replace `coro_call(proc_table[i].proc, args, nargs)` with
`proc_table_call(i, args, nargs)` at the eight non-trampoline call sites
in `coro_value.c`, `raku_builtins.c`, `interp_eval.c` (×3),
`interp_hooks.c`, `interp_exec.c` (×3), `polyglot.c`.  Trampoline-layer
sites in `coro_runtime.c` (lines 1125, 1213, 1503) stay as-is —
CH-17c's flip already lives inside the trampolines, reading entry_pc
out of the staging struct.

`coro_drive_fnc` (the suspend-aware generator driver,
`coro_runtime.c:1721`) is intentionally NOT flipped — it's an IR walker
by design and waits for CH-17h to migrate the remaining generator kinds.

`sm_lower.c:1742` is producer-side (sm_lower needs to read proc->...
to lower the body into a chunk) — it stays.

Pure routing reorganisation, no behavioural change: every flipped site
reaches one of the same two paths it was reaching before, just now
with the chunk path as a first-class option at the call site instead
of only at the trampoline.

**Gates:** standard CHUNKS set + full Icon corpus 186/47/30 +
unified_broker + isolation gate, all byte-identical.

#### CH-17g-statics — re-key static-variable storage off EXPR_t*

**Scope:** `coro_runtime.c:155–183` `static_tab[]` table keyed on
`(EXPR_t *proc, const char *name)` — used by `coro_call`'s param-load
preamble (line 447) and frame-pop epilogue (line 500) to persist Icon
`static x` declarations across calls.  Re-key onto `(int entry_pc,
const char *name)` (when entry_pc is resolved) or
`(const char *proc_name, const char *name)` (universal fallback).
Once this rung lands, no live runtime path keys storage on EXPR_t
identity.

**Gates:** standard set + the smoke programs that exercise Icon
`static` vars (e.g. `wordcount.icn` if present in corpus).

#### CH-17g-final — drop EXPR_t *proc; lift code_free gate

**Scope:** the actual closure.  Preconditions: CH-17g-call-sites
(eight sites flipped), CH-17g-statics (storage re-keyed), CH-17h
(remaining generator kinds migrated so chunk bodies no longer emit
`SM_PUSH_EXPR + SM_BB_PUMP`), **CH-17g-runtime-bridge** (chunks
dispatch builtins so `--run` of any Icon hello-world produces
correct output instead of FATAL "Undefined function" — added as a
precondition by CH-17g-final-SURVEY 2026-05-09), **CH-17g-irrun-lowers**
(invoke `sm_lower` / `sm_resolve_proc_entry_pcs` from `--run` path
before `polyglot_execute` so `entry_pc >= 0` for every proc regardless
of mode — added by the same survey).  When all five are met:

  - delete `EXPR_t *proc` field from `IcnProcEntry`
  - delete the legacy body of `coro_call(EXPR_t*, ...)` (its scope
    build, its `interp_eval` body loop) and the `coro_drive_fnc`
    wrapper
  - delete `pl_pred_table_lookup`'s legacy EXPR_t-returning overload
  - lift `lang_mask == (1u << LANG_SNO)` gate on `code_free` in
    `scrip_sm.c` — IR freed unconditionally for all six frontends
  - strengthen `test_isolation_ir_sm.sh` with the structural check
    forbidding `EXPR_t *` in `polyglot.c`, `coro_runtime.c`,
    `pl_runtime.c` proc/pred-table fields

This is the GOAL-CHUNKS.md Step 17 closure point.

**Gates:** standard set + full Icon corpus + Prolog smoke
+ structural check that `polyglot.c`, `coro_runtime.c`,
`pl_runtime.c` contain zero `EXPR_t *` field accesses on
proc_table / pred_table data.

#### CH-17g-irrun-execution — collapse `--run` non-SNO onto the SM dispatch path

**Carved sess 2026-05-09 from CH-17g-final-SURVEY-2 + Lon decision Option A.**

**Why this rung exists.** CH-17g-irrun-lowers delivered observability
(entry_pcs visible under `--run`) but not execution: under
`--run` non-SNO the SM_Program is freed by `sm_resolve_irrun_entry_pcs`
immediately after entry_pcs are populated, dispatch guards
(`g_current_sm_prog != NULL`) short-circuit the SM path, and execution
runs through `coro_call(proc_table[pi].proc, ...)` — the legacy AST
walker that CH-17g-final wants to delete.  Lon's principle: AST and SM
both deleted between phases for separation/isolation.  The only path
forward that satisfies that principle is to route `--run` non-SNO
through the same `sm_preamble` + `sm_run_with_recovery` pipeline as
`--run`.  This rung delivers that.

**Done when:** under `--run`, every Icon/Raku/Prolog program reaches
the SM interpreter dispatch loop (not `polyglot_execute`'s legacy AST
walker), produces output byte-identical to its current `--run`
baseline, and the Icon corpus 186/47/30 + Prolog smoke gates are
byte-identical to the pre-rung baseline.  The `g_irrun_lowers` flag and
`sm_resolve_irrun_entry_pcs` helper are deleted.  SNOBOL4 `--run`
path is unchanged (it has its own non-SM interpreter, `execute_program`,
that is not the AST walker this goal retires).

**Active steps:**

- [ ] **Step 1 — baseline capture.**  Build clean.  Run smoke ×6,
  isolation gate, unified_broker, scrip_all_modes, Icon corpus
  `--run`.  Capture pre-rung output for the trivial probes:
  `--run /tmp/probe.icn` and `--run /tmp/probe.icn` (a
  `procedure main() write("hello from icon") end` program).  Capture
  byte counts and md5s for at least three Icon corpus programs and
  three Prolog corpus programs under `--run`.  These are the
  byte-identity targets for Step 4.

- [ ] **Step 2 — route `--run` non-SNO through `sm_preamble`.**
  In `src/driver/scrip.c:557–565`, replace the current `else if
  (has_non_sno) { g_irrun_lowers = 1; polyglot_execute(prog);
  g_irrun_lowers = 0; }` arm with a path that mirrors the `--run`
  arm above it: call `sm_preamble(prog)` to get the SM_Program with
  IR freed (the gate at `scrip_sm.c:128` lifts in CH-17g-final, but
  works fine here because `sm_preamble` already populates proc/pred
  tables before lowering), then `sm_run_with_recovery(sm,
  sm_interp_run)`, then `sm_prog_free(sm)`.  SNOBOL4 (`!has_non_sno`)
  arm continues to call `execute_program(prog)` unchanged.

- [ ] **Step 3 — delete the superseded irrun-lowers infrastructure.**
  Once Step 2 is in place, the discard-after-resolve mechanism is
  unreachable on the `--run` non-SNO path.  Delete:
    - `g_irrun_lowers` definition + `extern` in `polyglot.h/c`
    - `sm_resolve_irrun_entry_pcs` declaration in `scrip_sm.h` and
      definition in `scrip_sm.c` (the function that does
      `sm_lower → sm_resolve_proc_entry_pcs → sm_prog_free`)
    - the `if (g_irrun_lowers) sm_resolve_irrun_entry_pcs(prog);` hook
      in `polyglot_execute` (`polyglot.c:269–270`)
    - the set/clear of `g_irrun_lowers` in `scrip.c:560,562`
    - the `#include` chain that pulled `scrip_sm.h` into `polyglot.c`
      for this single helper (verify nothing else in `polyglot.c`
      needs it; if so, leave the include)

  Eight dispatch-site guards on `g_current_sm_prog != NULL` (one in
  `proc_table_call`, one in `pl_chunk_fn`, two in `pl_runtime.c`,
  one in `interp_hooks.c`, two in `interp_eval.c`, one in
  `polyglot.c`) are now sufficient on their own — under `--run`,
  `g_current_sm_prog` is the live SM_Program (set by `sm_preamble`),
  so the guards take the SM path.  Leave them in place; they remain
  correct.

- [ ] **Step 4 — verify byte-identity against the pre-rung baseline.**
  Build.  Run the smoke ×6, isolation, unified_broker,
  scrip_all_modes, Icon corpus `--run` (target 186/47/30), and
  Prolog smoke gates.  Confirm `--run /tmp/probe.icn` produces
  byte-identical output to the Step 1 capture.  Confirm the three
  Icon and three Prolog corpus programs from Step 1 produce
  byte-identical output (md5 match) under `--run`.  Investigate
  any divergence before proceeding — divergence means a non-SNO
  feature that the legacy `polyglot_execute` walker handled and the
  SM dispatch path does not.  Likely surfaces (from
  CH-17g-runtime-bridge-4's open list): scan-context builtins
  (`tab`/`move`/`find`/`upto`/`match`/`any`/`many`), array
  composition outside the cases bridge-acomp/lcomp covered, any
  Raku-specific dispatch.  Each surface becomes its own follow-on
  rung (bridge-5 et seq.) before this rung lands.

- [ ] **Step 5 — confirm SNOBOL4 `--run` unchanged.**  Run
  `bash scripts/test_smoke_snobol4.sh` and any SNOBOL4-specific
  baselines.  The SNOBOL4 path goes through `execute_program(prog)`
  via `else { execute_program(prog); }` (`scrip.c:565`) and is not
  touched by this rung — gate is sanity-only.

- [ ] **Step 6 — handoff.**  Per RULES.md: validation doc at
  `docs/CHUNKS-step17g-irrun-execution-validation.md`; mark steps
  complete in this Goal file; update PLAN.md row tail; commit each
  touched repo with a clear message; rebase + push (SCRIP first,
  `.github` last); confirm `git log origin/main --oneline -1`
  shows the new hash on remote.

**Files touched:**
  - `src/driver/scrip.c` — Step 2 dispatch arm, Step 3 flag
    set/clear deletion
  - `src/driver/polyglot.c` — Step 3 hook deletion + flag definition
    deletion
  - `src/driver/polyglot.h` — Step 3 `extern` deletion
  - `src/driver/scrip_sm.c` — Step 3 helper definition deletion
  - `src/driver/scrip_sm.h` — Step 3 helper declaration deletion
  - `docs/CHUNKS-step17g-irrun-execution-validation.md` — Step 6 (new)

**Files NOT touched in this rung:**
  - `coro_runtime.c` — `proc_table_call` legacy fallback stays in
    place; deletion is CH-17g-final's job
  - `IcnProcEntry` struct — `AST_t *proc` field stays; deletion is
    CH-17g-final's job
  - `scrip_sm.c:128` `code_free` gate — lifting is CH-17g-final's job
  - `sm_lower.c:1757` — `proc_table[pi].proc` producer-side read
    stays; cleanup is CH-17g-final or follow-on

**Gates:**
  - smoke ×6 PASS (SNO 7/7, ICN 5/5, PL 5/5, RK 5/5, RB 4/4, SC 5/5)
  - isolation PASS
  - unified_broker PASS=49
  - scrip_all_modes PASS=2 (or current baseline if it has shifted)
  - Icon corpus `--run` PASS=186 FAIL=47 XFAIL=30 TOTAL=263
    (byte-identical, not just same pass count)
  - Prolog smoke PASS=5
  - Specific gate: `--run /tmp/probe.icn` byte-identical to
    pre-rung capture
  - Specific gate: at least three Icon and three Prolog corpus
    programs byte-identical (md5 match) under `--run` between
    pre-rung and post-rung

**Rollback signal:** if any byte-identity check in Step 4 diverges
and the cause cannot be traced to a known SM-side gap with a clear
follow-on rung path, revert the Step 2 dispatch change (one-line
revert) and surface the divergence as a survey doc before
re-attempting.  The rung is small enough that a clean revert + try
again is cheaper than partial landings.

**After this rung lands:** CH-17g-final's preconditions are
genuinely met (no `--run` path reads `proc_table[i].proc` at
runtime; the only remaining reader is `sm_lower.c:1757`, which is
producer-side and runs while IR is alive in all modes).
CH-17g-final closes Step 17.

**SESSION 2026-05-10 — probe-and-revert findings (no rungs landed).**
Lon directed an attempt at the rung; probe applied Step 2 (route
non-SNO `--run` through `sm_preamble + sm_run_with_recovery`),
measured, reverted.  Working tree restored byte-clean against
`f78d366c`.  Three concrete findings worth recording before next
attempt:

1. **Probe baselines.**  Pre-rung gates all green: smoke ×6 (7/7,
   5/5, 5/5, 5/5, 5/5, 4/4), isolation, unified_broker 49/0,
   scrip_all_modes 2/0, Icon `--run` PASS=177 FAIL=56 XFAIL=30,
   Prolog smoke 5/5.  Three-Icon and three-Prolog md5s captured.
   Step 1 baseline target captured cleanly.

2. **Step 2 alone — 72-program Icon regression, not 0.**  Routing
   `--run` non-SNO through `sm_preamble + sm_run_with_recovery`
   drops Icon corpus from 177 PASS → 105 PASS (76 PASS→FAIL, 4
   FAIL→PASS, net −72).  The `/tmp/probe.icn` and three Icon
   `rung01_paper_*` programs ARE byte-identical (the rung's
   nominal Step 1 probe targets), but the broader corpus diverges.
   Distribution of the 76 regressed programs by category:
   tables 11, scan-context 9, records 5, str-retval 4, loops 4,
   jcon-meander 4, global-initial 4, cset-builtin 4, case 4,
   bang-concat 4, augop 4, section 3, real-relop 3, lists 3,
   real-arith 2, null-test 2, block-body 2, suspend 1, str-builtins
   1, read-loop 1, alt 1.  Prolog `hello.pl`/`palindrome.pl`/
   `plunit.pl` all diverge (initialization/2 directive — maps
   cleanly to CH-17i-prolog-initialization).

3. **Root cause is upstream of `_usercall_hook`, not at it.**
   CH-17b'' lowers Icon proc bodies into SM bytecode; function
   calls become `SM_CALL_FN s="<name>"` which routes through
   `g_user_call_hook → _usercall_hook` (in `interp_hooks.c`).
   That hook tries SNOBOL4 label, sc_dat, FNCEX_fn, proc_table,
   pl_pred_table, SM-body lookup — but never `icn_call_builtin`'s
   chain (raku/scan/by-name/user-proc/smart-fallback).  So Icon
   builtin invocations from lowered proc bodies (find, tab, match,
   upto, any, many, move, bal, key, integer, real, string, type,
   image, copy, write/writes, table, insert, delete, push, pop,
   get, pull, put, …) cannot reach their handlers via this
   dispatch path.

   A targeted patch was tried: insert a two-step Icon-builtin
   dispatch (`icn_try_call_builtin_by_name` + synthesized-AST
   `scan_try_call_builtin`) into `_usercall_hook` between the
   proc_table cross-call and the pl_pred_table cross-call.
   Patch was clean on baseline (Icon corpus stays 177 PASS;
   `find()` works standalone under `--run`) but only delivered
   +1 PASS under Step 2 (105 → 106), and introduced a flake on
   programs that previously worked.  Reverted.  The fix is small
   and locally correct, but does NOT unblock the regression alone
   because the residual mutators (insert/delete/push/pop/get/pull
   /put), table indexing `t["x"]` (its own SM opcode), records,
   augops, and case constructs each represent SM-side gaps
   beyond just builtin dispatch.

4. **Recommendation: re-sequence ahead of Step 2.**  CH-17g-final-
   SURVEY-2's Option A is correct in *principle* (AST and SM both
   deleted between phases; route `--run` through SM dispatch).
   But Step 2 as written assumes the SM dispatch path covers the
   Icon `--run` PASS surface, and empirically it does not.
   The 76 regressed programs are not random — they bucket cleanly
   onto the sequenced sub-rungs already named in this Goal file:
   CH-17i-bang-concat phases 2/3/4 (bang-concat 4 + lconcat
   subset of records/lists), CH-17i-section (section 3),
   CH-17i-limit-random (likely overlaps loops/case), CH-17i-prolog-
   initialization (Prolog 3 of 3).  Tables, records, and Icon
   mutators (insert/delete/push/pop/get/pull/put) need their own
   sub-rungs that don't yet exist by name.  Suggest: file
   CH-17i-table-mutators and CH-17i-icn-list-mutators as
   prerequisites; close all CH-17i sub-rungs first; THEN attempt
   CH-17g-irrun-execution.  Alternative path (smaller):
   `_usercall_hook` learns about Icon builtin dispatch (the patch
   tried this session — close to landing on its own merits as
   `CH-17g-irrun-prep` even before Step 2), shrinking the
   regression set to those features that can't be solved at the
   `_usercall_hook` layer (table indexing opcode, records, augops).

**Working tree state at session end:** clean against `f78d366c`.
No code commits, no docs landed.  Next session can re-attempt with
the sequenced sub-rungs landed first, or carve a `CH-17g-irrun-prep`
rung that lands the `_usercall_hook` builtin-dispatch patch on its
own merits (it's correct standalone — the issue was that it doesn't
unblock the rung *alone*).

### CH-17h — Migrate Step 15 remaining kinds (CH-15b)

**CH-17h-SURVEY LANDED sess 2026-05-09** — `docs/CHUNKS-step17h-survey.md`
documents that the line-1303 dispatcher arm (`E_EVERY`, `E_SUSPEND`,
`E_BANG_BINARY`, `E_LCONCAT`, `E_LIMIT`, `E_RANDOM`, `E_SECTION`,
`E_SECTION_PLUS`, `E_SECTION_MINUS`) is **dead code on real corpora today**:
zero fires across smoke ×6 + Icon corpus 263 + unified_broker 49 +
broad/regression runs + a hand-crafted `every`/`suspend`/section program
that produced correct output.  Same diagnosis as CH-15-SURVEY: stmt-context
generators lower via `lower_stmt`'s dedicated paths; chunk-body generators
sit in chunks that are forward-jumped over until CH-17g-final makes them
live.  **Recommendation in the survey doc: reverse the original sequencing
— land CH-17g-final first** (its legacy-body deletion is the act that
*creates* the test surface for these kinds, not the act that requires them
gone), then migrate per-kind with real corpus validation.  Awaits Lon
decision on sequencing.

**Scope (when migration starts):** as per CH-15-SURVEY's recommendation: with proc bodies
now lowered through sm_lower (CH-17b/d), every-bodies and
generator expressions inside Icon procs reach the line-1192
dispatcher arm.  E_EVERY, E_SUSPEND, E_BANG_BINARY, E_LCONCAT,
E_LIMIT, E_RANDOM, E_SECTION, E_SECTION_PLUS, E_SECTION_MINUS
each migrate per-kind with corpus validation now possible.

This is CH-15b's reactivation point.

### CH-17i — Icon/Prolog: complete the currently-supported surface in all four modes

**Why this umbrella exists.**  The four-mode-isolation property has
been GOAL-CHUNKS's done-when from the start.  SNOBOL4 and Snocone
reached it via M1 (modes 2/3 isolated) and M2 (mode 4).  Icon and
Prolog lag because the proc/pred-table side channel and the AST-driven
BB engine kept them out of the SM dispatch path.  CH-17 is the
architectural unblock; CH-17i is the rung set that finishes the *same*
property for Icon and Prolog the way M1+M2 finished it for
SNOBOL4+Snocone.  No new scope, no new property — execution of the
existing goal for the frontends that haven't reached it yet.

**The directive in one sentence.** Take the Icon and Prolog feature
surface that SCRIP supports *today* — defined empirically by the
programs that pass under `--run` today (Icon corpus 186 PASS;
Prolog `test/prolog/*.pl` baseline) — and make that *same* surface
run correctly through modes 2, 3, and 4 with each mode structurally
isolated from any AST walk.  Not feature expansion; the same property
SNOBOL4 already enjoys, applied to Icon and Prolog.

**What "isolated" means in this codebase** (this matches the parent
goal's existing definition; restated here for in-line reference):

  - **Mode 1** (compile-only).  Produces SM_Program.  No execution.
    AST freed after `sm_lower` returns.  Isolated by construction.

  - **Mode 2** (`--run`).  Runs the SM_Program — same as mode 3 —
    after `sm_lower` returns and AST is freed.  The `--run` /
    `--run` distinction is a driver-side flag that affects
    diagnostics and oracle behaviour, not a different runtime.
    CH-17g-irrun-execution makes this true for Icon and Prolog by
    routing `--run` non-SNO through `sm_preamble` +
    `sm_run_with_recovery` exactly as `--run` does.  SNOBOL4's
    `execute_program` path is its own non-SM interpreter; it is
    unchanged by this work.

  - **Mode 3** (`--run`).  Runs the SM_Program.  AST freed before
    execution begins.  No `interp_eval` / `interp_eval_pat` /
    `interp_eval_ref` / `call_user_function` / `polyglot_execute`
    reachable from any non-SNO runtime path.  proc_table and
    g_pl_pred_table hold `entry_pc` integers, not `IR_t *`.

  - **Mode 4** (`--compile`).  Emits native code from the
    SM_Program.  AST and SM_Program both consumed at emit time.
    Resulting native code links against `libscrip_rt.so` which has
    no AST walker symbols and no SM interpreter symbols reachable
    from the emitted code's call graph.

**Done when:**

  1. **Modes 2 and 3 cover the supported surface** — and they cover
     it *together*, because under CH-17g-irrun-execution they share
     the SM dispatch runtime.  Every Icon program in the
     `--run` PASS subset today (186 of 263) runs correctly under
     both modes byte-identical to its current `--run` baseline.
     Every Prolog program in `test/prolog/*.pl`'s `--run` PASS
     subset runs correctly under both modes byte-identical.
     Programs that currently FAIL/XFAIL under `--run` stay there.

  2. **Mode 4 (`--compile`) covers the supported surface.**
     The same Icon and Prolog `--run` PASS subset runs through
     `--compile` byte-identical.  This is the parent goal's
     M5 / Step 19 work for Icon+Prolog, brought forward as a
     deliverable of CH-17i because "all four modes" includes mode 4.

  3. **Mode 3 is structurally AST-free.** No `interp_eval` /
     `interp_eval_pat` / `interp_eval_ref` / `call_user_function` /
     `polyglot_execute` reachable from any `--run` runtime path.
     No `IR_t *` field accesses in the SM-mode runtime files
     (`coro_runtime.c`, `coro_value.c`, `coro_stmt.c`, `pl_runtime.c`,
     `sm_interp.c`, `sm_lower.c`, `bb_*` files).  Strengthened
     isolation gate enforces this structurally.  (Mode 2 inherits
     this because it shares the runtime.)

  4. **Mode 4 is structurally host-free.** Emitted code's link
     graph closes against `libscrip_rt.so` only; no SCRIP host
     symbols (`scrip.c`, `polyglot.c`, `interp_eval.c`,
     `sm_interp.c`) referenced from the emitted artifact.  New
     gate added to verify with `nm`/`readelf`.

**What this umbrella is NOT:**

  - NOT adding Icon language features beyond what `--run`
    handles today.  The 47 FAILs in Icon corpus stay FAIL.
  - NOT adding Prolog builtins SCRIP doesn't already support.
  - NOT widening the SM opcode set beyond what the current
    `sm_lower` already emits for Icon and Prolog.  If `sm_lower`
    emits `SM_ACOMP` and `sm_interp.c` has no handler, that's a
    completeness gap (in scope).  If `sm_lower` doesn't emit some
    opcode at all and the `--run` walker handled a feature via
    a code path that has no SM equivalent today, then either
    `sm_lower` grows to emit it (in scope, mechanical) or the
    feature is genuinely out of scope and the program in question
    moves to the XFAIL list (documented decision, in scope).

**Sequencing:**

  - **CH-17g-irrun-execution** lands first (already carved; routes
    `--run` non-SNO through `sm_preamble`).  After this, modes 2
    and 3 share the runtime, so the survey below covers both.
  - **CH-17i-survey-mode3** lands next — empirical audit of the
    Icon+Prolog `--run` PASS subset under SM dispatch, producing
    the prioritised gap list with one bucket per failure mode
    (missing builtin → name; missing opcode handler → opcode;
    producer gap → AST kind; semantic divergence → program).
  - **CH-17i-mode3-completeness** rungs land per bucket from the
    survey, until the Icon and Prolog `--run` PASS subsets pass
    byte-identical under SM dispatch.
  - **CH-17g-final** lands, deleting the legacy AST walker bodies
    that are now unreachable (`coro_call`'s scope build + body loop;
    `pl_pred_table_lookup`'s legacy overload; lifting the
    `lang_mask == (1u << LANG_SNO)` gate on `code_free`).
  - **CH-17i-mode4-icon-prolog** lands the `--compile`
    coverage: extend `GOAL-MODE4-EMIT.md`'s rung set to cover the
    SM opcodes Icon and Prolog use; Icon and Prolog `--compile
    --target=x86` PASS == `--run` PASS exactly.
  - **CH-17i-final-isolation** locks the property in CI: strengthened
    isolation gate covers the full SM-mode runtime file set; mode 4
    link-graph check; coverage matrix doc records the four-mode ×
    {Icon, Prolog} matrix all-green.

#### CH-17i-survey-mode3 — Icon+Prolog `--run` gap audit against the supported surface

**Scope.**  Define "supported surface" empirically: capture under
`--run` the PASS/FAIL/XFAIL set for the Icon corpus 263 and
the Prolog `test/prolog/*.pl` set as the snapshot baseline.  Then,
with CH-17g-irrun-execution landed, run the PASS subset under SM
dispatch (`--run` and `--run` should produce identical output
post-CH-17g-irrun-execution; either flag works for the survey).
Capture every divergence: FATAL, wrong output, hang.

**Categorise each divergence into one bucket:**
  - **Missing builtin** — FATAL "Undefined function NAME".  Bucket
    by name.  Each name maps to "extend `icn_try_call_builtin_by_name`
    with a verbatim port of the `interp_eval.c` E_FNC arm" — same
    recipe as bridge-1..4.
  - **Missing opcode handler** — FATAL "Unhandled SM opcode N".
    Bucket by opcode.  Each opcode maps to "add the dispatch case
    in `sm_interp.c` mirroring the `interp_eval.c` arm for the
    corresponding kind."
  - **Producer gap** — `sm_lower` doesn't emit anything for some
    AST kind that the `--run` walker handled.  Bucket by kind.
    Each maps to "add lowering rule in `sm_lower.c` for that kind."
  - **Semantic divergence** — output differs without FATAL.  Bucket
    by program.  Each requires individual diagnosis: AST walker and
    SM dispatch implement the same feature differently.

**Done when:** `docs/CHUNKS-step17i-survey-mode3.md` records the
PASS-subset definition (corpus snapshot + md5s), the divergence
buckets with counts, and the prioritised sub-rung list (one rung
per bucket).  Same for Prolog in the same doc or a sibling
`...-prolog.md`.

**Gates:** survey-only.  No source touched.  The doc is the artifact.

#### CH-17i-mode3-completeness — close the buckets one rung at a time

**Scope.**  For each bucket in the survey, one sub-rung.  Naming:
  - `CH-17i-mode3-builtin-NAME` for missing-builtin buckets
    (e.g. `CH-17i-mode3-builtin-tab`)
  - `CH-17i-mode3-opcode-NAME` for missing-opcode buckets
    (e.g. `CH-17i-mode3-opcode-acomp`)
  - `CH-17i-mode3-lower-KIND` for producer-gap buckets
    (e.g. `CH-17i-mode3-lower-section`)
  - `CH-17i-mode3-semantic-PROGRAM` for semantic-divergence buckets
    (e.g. `CH-17i-mode3-semantic-meander`)

Each sub-rung's recipe is in the survey doc.  Each lands with
byte-identical gates for its own corpus subset.  This sub-rung
collection IS the work — it's not predictable in advance how many
rungs there are; the survey produces the list.

**Done when:** the Icon `--run` PASS subset and Prolog `--run`
PASS subset run byte-identical under SM dispatch.  The Icon corpus
gate gains a new line: `--run PASS=N` where N matches the
`--run` PASS count exactly (post-CH-17g-irrun-execution the two
flags share a runtime, so the counts must be exactly equal — any
divergence is a regression).

**Gates:** standard set + per-bucket corpus subset byte-identical
+ terminal Icon `--run` PASS count == `--run` PASS count
exactly + Prolog twin.

#### CH-17i-mode4-icon-prolog — `--compile` covers the Icon+Prolog supported surface

**Scope.**  Extend `GOAL-MODE4-EMIT.md`'s rung set to handle the
SM opcodes that Icon and Prolog use.  After CH-17i-mode3-completeness,
the SM_Program for any supported Icon or Prolog program is
well-formed end-to-end; the codegen needs to emit the Icon/Prolog
opcode set the same way it emits the SNOBOL4 set today.

**Sub-rungs (carved as gaps surface in the mode-4 audit):**
  - `CH-17i-mode4-icon-survey` — empirical audit: which Icon SM
    opcodes does `sm_codegen_x64` not yet handle?
  - `CH-17i-mode4-icon-opcode-NAME` — one per gap, mirroring
    EM-7 series.
  - `CH-17i-mode4-prolog-survey` — Prolog twin.
  - `CH-17i-mode4-prolog-opcode-NAME` — one per gap.

**Coordination with `GOAL-MODE4-EMIT.md`.**  The mode-4 emit goal
is owned separately and runs in parallel.  This sub-rung does not
duplicate it — it carves the Icon-and-Prolog-specific opcode work
as named rungs that point INTO `GOAL-MODE4-EMIT.md` for execution
detail.  When in doubt about file ownership, see `GOAL-MODE4-EMIT.md`.

**Done when:** the Icon `--run` PASS subset and Prolog `--run`
PASS subset run byte-identical under `--compile`.  Same
exactness rule as mode 3: PASS count exactly equal across modes.

**Gates:** standard set + Icon `--compile` PASS == Icon
`--run` PASS + Prolog twin + structural mode-4 isolation
(emitted artifact's link graph closes against `libscrip_rt.so`
only).

#### CH-17i-final-isolation — lock the four-mode-isolation property structurally for Icon and Prolog

**Scope.**  All sub-rungs above land mode-by-mode coverage.  This
terminal rung locks the structural property in CI:

  - **Mode 3 isolation gate (Icon+Prolog files added):** files
    reachable from `sm_interp_run`'s call graph (transitively) MUST
    NOT reference any symbol from `interp_eval.c`,
    `interp_eval_pat.c`, `interp_eval_ref.c`, `polyglot_execute`,
    `call_user_function`, or `execute_program` — extending the
    existing M1 gate (which covers the SNOBOL4 file set) to cover
    `coro_runtime.c`, `coro_value.c`, `coro_stmt.c`, `pl_runtime.c`,
    `interp_hooks.c`, `polyglot.c`.  The exception is
    `icn_try_call_builtin_by_name` and the helpers it forwards to —
    those are SM-side adapters, not the AST walker, but they live
    in `interp_eval.c`'s file for historical reasons.  The gate
    distinguishes by symbol name, not file name.

  - **Mode 4 isolation gate:** the emitted artifact's link graph
    (extracted via `nm` / `readelf`) closes against
    `libscrip_rt.so` only.  No SCRIP host symbols.  Enforced
    via a smoke test that links the emitted artifact and
    `nm --undefined-only` checks the symbol set.

  - **Structural field-access check:** `IR_t *` (or the post-rename
    name) does not appear in any function signature in the SM-mode
    runtime files.  No SM-mode file walks AST node fields.

  - **Documentation deliverable:** `docs/CHUNKS-step17i-coverage-matrix.md`
    records the coverage table:

    |              | Mode 1 | Mode 2 (`--run`) | Mode 3 (`--run`) | Mode 4 (`--compile`) |
    |--------------|:------:|:-------------------:|:-------------------:|:---------------------------:|
    | **Icon**     |   ✓    | PASS=186 (baseline) |  PASS=186 (==)      |       PASS=186 (==)         |
    | **Prolog**   |   ✓    | PASS=N (baseline)   |  PASS=N (==)        |       PASS=N (==)           |
    | **Isolation**|  N/A   |  shares mode-3 runtime  |  AST-free call graph ✓  |  host-free link graph ✓  |

**Done when:** all four cells of the {Icon, Prolog} × {mode 2, 3, 4}
matrix are PASS=baseline-count, the structural isolation gates
PASS, and the coverage doc lands.

**Gates:** all of the above, simultaneously, in one CI run.

**After CH-17i-final-isolation lands:** the umbrella's done-when is
met.  The four-mode-isolation property — which has always been
GOAL-CHUNKS's done-when — is now structurally enforced for Icon
and Prolog as well as for SNOBOL4 and Snocone.  Future regressions
are caught by the gates, not by manual inspection.  Step 18.5 of
the parent goal closes.

### CH-17-RENAME — Rename `EXPR_t`/`EXPR_e` → `IR_t`/`IR_e`; `chunk` → `expression`

**Status:** ✅ CH-17-RENAME-a through CH-17-RENAME-h LANDED sess 2026-05-09 (g-cleanup: `g_chunk_scope` → `g_expression_scope`, `chunk_scope_walk` → `expression_scope_walk`, `SCRIP_CHUNKS_AUDIT` → `SCRIP_EXPRS_AUDIT`, `g_chunks_audit_*` → `g_exprs_audit_*`, `CHUNK_REG_MAX` → `EXPRESSION_REG_MAX`, `g_chunk_reg_count` → `g_expression_reg_count`; h: EM-5a test echo string updated).  CH-17-RENAME-FINAL is next — preconditions MET.  Carved from "next rung
options" after the bridge-acomp/lcomp pair landed and surfaced the
naming inconsistency the rest of GOAL-CHUNKS exists to retire.

**Why this rung exists.**  The codebase carries two semantically
inverted names:

1. **`EXPR_t` / `EXPR_e` is the *unified IR node*** (defined at
   `src/ir/ir.h:251–262`).  Every parse-derived AST node is one —
   statements, declarations, scopes, labels, goto targets, type
   nodes, frame-slot descriptors, Prolog clauses, Icon proc bodies.
   Most of the kinds in the EXPR_e enum are not "expressions" by
   any reasonable definition.  The Prolog runtime even stores raw
   Term pointers in `E_VAR.ival` (per `pl_runtime.c:660`) — these
   IR nodes are doing IR-node duty, not expression duty.  The name
   misleads every reader new to the codebase.

2. **`SmChunk_t` (and the `chunk` vocabulary built around it) is the
   *compiled expression*** — a contiguous range of SM ops addressed
   by `entry_pc`, callable as a unit, generator-capable when driven
   through `bb_broker_drive_sm`.  This is what code that says
   "evaluate this expression" actually means: a pure functional
   region with inputs (arity args on the SM stack), outputs (TOS +
   `last_ok`), and no IR walking at runtime.  Calling it a "chunk"
   obscures what it does and why GOAL-CHUNKS exists.

The rename restores the architectural truth that the bridge-acomp/
bridge-lcomp pair made plain to read: information that *was* implicit
in `EXPR_t.kind` at runtime is now explicit in the SM_Program.  The
parse tree is IR; the runtime-callable compiled SM region IS the
expression.  Calling them by their right names makes the rest of the
ladder (CH-17g-final, CH-17h, the M3 cells of GOAL-CHUNKS Milestone 3)
read clearly instead of fighting a layer of mislabeling.

**Done when:** `EXPR_t` and `EXPR_e` are no longer referenced anywhere
in `src/`, `test/`, or `scripts/`; `IR_t` and `IR_e` are the names; the
`SmChunk_t` typedef and the `chunk` vocabulary in opcode names, helper
functions, comments, env vars, and validation docs are renamed to use
`Expression` / `EXPR` / `expression` consistently; gates byte-identical
to baseline at every sub-rung; documentation in
`docs/CHUNKS-step17-rename-validation.md` records the mapping table and
the two carving decisions (why split into sub-rungs, why this order).

**Why a multi-rung carve.**  Surface size from this session's audit:
~73 files reference `EXPR_t`, ~23 reference `EXPR_e`, ~17 reference
chunk-flavor identifiers; total impact crosses every layer (ir →
frontend parsers → driver/interp → runtime/x86 → runtime/interp →
runtime/rt → docs → tests → scripts).  A single-session monolithic
rename would (a) blow the per-session test-gate budget, (b) hide any
subtle behavioural divergence in the diff noise, (c) collide with
ongoing parallel sessions on the same files (per the FI-11 ownership
table in RULES.md).  Carved into eight sub-rungs that each pass the
standard CHUNKS gate set byte-identical and can be landed independently.

**Sequencing decision.**  IR rename comes BEFORE expression rename.
Reasoning: `EXPR_t` is the more pervasive name (~73 files vs ~17), so
landing it first removes the ambiguity that would otherwise dog the
expression rename ("does this `EXPR` mean the IR-side `EXPR_t` or the
new compiled-expression vocabulary?").  Once IR-side is `IR_t`/`IR_e`,
the chunk-side rename to `Expression` is unambiguous and the audit
becomes a clean find-and-fix per file.

#### CH-17-RENAME-a — IR header rename (`src/ir/ir.h`)

**Scope:** Single file.  Add new typedefs alongside the old ones; do
NOT delete the old typedefs in this rung.  Both names compile and refer
to the same struct/enum.

```c
typedef struct EXPR_t IR_t;       /* alias — preferred name */
typedef enum   EXPR_e IR_e;       /* alias — preferred name */
/* and #define EXPR_t IR_t for transitional source-text compatibility
 * is NOT done — ambiguity is the point we're removing.  Keep the old
 * struct tag visible so existing files compile unchanged this rung;
 * each subsequent rung migrates one ownership-section's files. */
```

The `EXPR_e` enum values (`E_QLIT`, `E_VAR`, etc.) keep their `E_`
prefix in this rung — those are 100+ identifiers and they're already
short.  Question for end-of-rung review: do they become `IR_QLIT` /
`IR_VAR` etc. in a follow-on rung, or stay as `E_*`?  The `E_` prefix
arguably reads more naturally than `IR_QLIT` / `IR_VAR` (Icon literature
uses "E-codes" pervasively); leaving them is the conservative call.
Decide at landing.

**Gates:** standard CHUNKS gate set byte-identical.

#### CH-17-RENAME-b — Frontend parsers (Icon, Raku, Snocone, SNOBOL4, Prolog, Rebus)

**Scope:** All files under `src/frontend/`.  Each file's `EXPR_t` →
`IR_t`, `EXPR_e` → `IR_e`.  Generated files (`*.tab.c`, `*.tab.h`,
`*.lex.c`) regenerated via `regenerate_parser_and_lexer_from_sources.sh`
after editing the `.y`/`.l` source per RULES.md.

Per FI-11 file ownership, each frontend's files are owned by their
session; this sub-rung coordinates a one-time pass and notes the
ownership boundaries crossed for the merge gate.

**Gates:** standard set + frontend-specific smoke ×6 byte-identical.

#### CH-17-RENAME-c — IR layer + driver (`src/ir/`, `src/driver/`)

**Scope:** Files in `src/ir/` (the printer, helpers) and `src/driver/`
(`interp_eval.c`, `interp_exec.c`, `interp_hooks.c`, `polyglot.c`,
`scrip.c`, the `interp_private.h` declarations).  This is the largest
single-file batch (`interp_eval.c` alone has 63 references).

**Gates:** standard set + Icon corpus `--run` 186/47/30 byte-identical.

#### CH-17-RENAME-d — Runtime-interp layer (`src/runtime/interp/`)

**Scope:** `coro_runtime.{c,h}`, `coro_value.c`, `coro_stmt.c`,
`pl_runtime.{c,h}`, `pl_broker.{c,h}`, `icn_runtime.c`, `interp_eval`
adapters.  Note: `pl_chunk_t` (the local typedef in `pl_broker.c:560`)
is renamed in CH-17-RENAME-g together with the broader chunk vocabulary,
not here.

**Gates:** standard set + unified_broker PASS=49 byte-identical.

#### CH-17-RENAME-e — Runtime-x86 layer (`src/runtime/x86/`)

**Scope:** `sm_lower.c`, `sm_interp.c`, `sm_codegen.c`, `sm_prog.{c,h}`,
`bb_broker.c`, `bb_emit.c`, `bb_flat.c`, `eval_*.c`, `snobol4_stmt_rt.c`,
`scrip_sm.c`, `name_t.c`, etc.  This is the layer where `EXPR_t` is most
hostile to the GOAL-CHUNKS narrative (the "no IR pointers in SM runtime
files" isolation gate enforces structural distance from the IR; calling
the residual call-out parameter `IR_t *` rather than `EXPR_t *` makes
the gate's job legible).

Update the isolation-gate script if it greps for `EXPR_t` literally.

**Gates:** standard set + isolation PASS byte-identical.

#### CH-17-RENAME-f — Runtime-rt + cross-host bindings (`src/runtime/rt/`,
`src/runtime/net/`, `src/runtime/jvm/`, `src/runtime/js/`, `src/silly/`)

**Scope:** Native-host runtimes and the residual Silly subsystem.  Lower
risk because most of these are oracle-mode hosts not on the live SM path.

**Gates:** standard set + JVM/.NET smoke if installed (skip-on-absent
otherwise).

#### CH-17-RENAME-g — `chunk` → `expression` vocabulary in code

**Scope:** opcode renames (`SM_PUSH_CHUNK` → `SM_PUSH_EXPRESSION`;
`SM_CALL_CHUNK` → `SM_CALL_EXPRESSION`); type rename (`SmChunk_t` →
`SmExpression_t`; `pl_chunk_t` → `pl_expression_t`); helper renames
(`sm_call_chunk` → `sm_call_expression`; `sm_label_pc_lookup` keeps its
name — pc lookup is mode-neutral); env var renames (`SCRIP_PROC_ENTRY_PCS`
keeps its name; `SCRIP_*_CHUNK*` env vars become `SCRIP_*_EXPR*`);
function-local variables and field names (`entry_pc` keeps its name —
pc is mode-neutral, expression and chunk both have entry_pcs).

**Old short-form `EXPR` use audit:** check that every occurrence of
`EXPR` as a bare token in the post-RENAME-a–f tree refers to the new
vocabulary, not residue from EXPR_t (e.g. `pl_runtime.c:642` comment
"Term→EXPR bridge" is residual; either rewrite or rename consistently).

**Gates:** standard set byte-identical.  New gate: grep for `\bchunk\b`
(case-insensitive) in `src/runtime/`, `src/driver/`, `src/frontend/`
returns zero outside historical commit messages and validation-doc
references.

#### CH-17-RENAME-h — `chunk` → `expression` vocabulary in docs, scripts, gate names

**Scope:** validation docs under `docs/CHUNKS-step*`, gate scripts under
`scripts/test_*chunk*`, `.github` PLAN.md / GOAL-CHUNKS.md / GOAL-CHUNKS-STEP17.md
references — but NOT the file names of the goal files themselves
(`GOAL-CHUNKS.md` and `GOAL-CHUNKS-STEP17.md`) for git-history continuity.
Convention recorded in the rename validation doc: the goal filename
remains historical; the goal's *content* uses the new vocabulary;
references to closed rungs (CH-15a, CH-17b, etc.) keep their
"CHUNKS-step*" naming because those rungs landed under that name.

Future goal files should use the new vocabulary in their filenames.

**Gates:** none beyond the standard set.  This is a documentation-only
sweep.

#### CH-17-RENAME-FINAL — Drop the legacy aliases

**Status:** ✅ LANDED sess 2026-05-09.  SCRIP `bcdc7e2c` (g-cleanup +
h) + validation doc `docs/CHUNKS-step17-rename-final-validation.md`.

**Scope:** delete the `typedef ... IR_t;` aliases from `src/ir/ir.h`
introduced in CH-17-RENAME-a (or rather: rename the actual struct/enum
to the new names and delete the aliases).  No file in the tree should
still compile against `EXPR_t` after this rung lands.

**Finding:** AR-1 renamed struct/enum in-place; no shim aliases were
introduced.  FINAL closes by confirming zero `EXPR_t`/`EXPR_e` in
src/ test/ scripts/ and publishing the mapping table validation doc.

**Precondition:** sub-rungs a–h all green.  Empirical check: `grep -rn
"\bEXPR_t\b\|\bEXPR_e\b" src/ test/ scripts/` returns zero hits (or only
hits in historical commit references inside comments, which are kept
verbatim).  ✅ CONFIRMED.

**Gates:** standard set byte-identical.  ✅ PASS (build, smoke ×6,
isolation, unified_broker=49).

---

## Per-rung gates summary (delta from CHUNKS standard set)

| Rung    | Adds gate                                            |
|---------|------------------------------------------------------|
| CH-17a  | `SCRIP_PROC_ENTRY_PCS=1` shows -1 for every proc     |
| CH-17b  | `SCRIP_PROC_ENTRY_PCS=1` shows non-(-1) for ICN/Raku (chunks are skeletons) |
| CH-17b' | proc-body chunks contain the actual lowered ops      |
| CH-17b''| chunk E_VARs emit SM_LOAD_FRAME / SM_STORE_FRAME for params+locals; gates byte-identical (chunks still dead code) |
| CH-17c  | Icon corpus 186/47/30 byte-identical                 |
| CH-17d  | `SCRIP_PROC_ENTRY_PCS=1` shows non-(-1) for PL       |
| CH-17e  | Prolog smoke extended to `--run`                  |
| CH-17f  | Prolog `--run` crosscheck vs `--run`           |
| CH-17g-call-sites | Icon corpus 186/47/30 byte-identical (8 sites flipped) |
| CH-17g-statics | static-var storage no longer keyed on EXPR_t* |
| CH-17g-final-SURVEY | finding: legacy `coro_call` body is live in `--run`; CH-17g-final preconditions amended |
| CH-17g-runtime-bridge-DESIGN | architectural plan: extract `icn_try_call_builtin_by_name`; wire into `SM_CALL_FN` after `INVOKE_fn` |
| CH-17g-runtime-bridge-1 | refactor: `icn_call_builtin` split into name-based helper + EXPR_t tail; corpus byte-identical |
| CH-17g-runtime-bridge-2 | `--run` of trivial Icon proc produces output identical to `--run` |
| CH-17g-runtime-bridge-3 | Raku/SCAN bridges (only if corpus crosscheck reveals need) |
| CH-17g-irrun-lowers | `--run` invokes `sm_lower` / `sm_resolve_proc_entry_pcs`; entry_pc resolves regardless of mode |
| CH-17g-final | structural: no EXPR_t* in proc_table / pred_table    |
| CH-17h  | Icon corpus per-kind crosscheck                      |
| CH-17i-survey-mode3 | survey doc + prioritised gap list per bucket (`docs/CHUNKS-step17i-survey-mode3.md`) |
| CH-17i-mode3-completeness | terminal: Icon `--run` PASS == `--run` PASS exactly; Prolog twin |
| CH-17i-mode4-icon-prolog | Icon and Prolog `--compile` PASS == `--run` PASS exactly |
| CH-17i-final-isolation | mode 3 AST-free call graph + mode 4 host-free link graph + zero `IR_t *` accesses in SM-mode files + coverage matrix doc all-green for Icon × {2,3,4} and Prolog × {2,3,4} |

---

## File ownership

This sub-goal is **not parallelizable with M4 or M5** the way
GOAL-MODE4-EMIT.md is.  CH-17 rungs touch the same files as the
parent goal's M4 cleanup work (`coro_runtime.c`, `polyglot.c`,
`pl_runtime.c`).  Sequential execution required.

CH-17 rungs are file-disjoint from CH-15b (Icon generator kinds)
and from Step 16 (Prolog cluster), but those steps land DOWNSTREAM
of CH-17e (Step 16) and CH-17h (CH-15b).

---

## Closed rungs

**CH-17a LANDED sess #75, 2026-05-07** — Scaffolding.  `IcnProcEntry`
and `Pl_PredEntry` gain `int entry_pc` (init -1).  New
`sm_resolve_proc_entry_pcs(SM_Program*)` in scrip_sm.c walks both
tables after sm_lower returns and populates entry_pcs via
`sm_label_pc_lookup`.  Today every entry resolves to -1 (no chunks
yet).  Pure addition; byte-identical gates.  Diagnostic env
`SCRIP_PROC_ENTRY_PCS=1`.  SCRIP @ `0cb31ca4`.

**CH-17b LANDED sess #75, 2026-05-07** — sm_lower emits named-chunk
skeletons (SM_JUMP + SM_LABEL + SM_RETURN + SM_LABEL) for every
entry in proc_table.  CH-17a's resolver now finds non-(-1) entry_pcs
end-to-end (Icon hello.icn: main@1; Raku rk_given: day_type@1,
season@5, main@9).  Empty bodies; chunks forward-jumped over.
Scope-reduced from "skeleton + body" mid-session — body lowering
split into CH-17b' to keep this rung small and risk-free.  SCRIP
@ HEAD (post `0cb31ca4`).

**CH-17b' LANDED sess #78, 2026-05-07** — proc-body lowering.  The
per-proc emission loop in sm_lower.c (CH-17b's skeleton site) now
walks `proc->children[1+nparams..nchildren-1]` and calls `lower_expr`
on each body child, followed by `SM_POP`, then a trailing `SM_RETURN`.
Chunks now contain real lowered SM ops.  Verified via `--dump-sm` on
`test/icon/palindrome.icn`: chunk 1–52 holds the full palindrome
proc body (map call, while loop with E_LCOMP, SM_AUGOP, etc.); chunk
55–74 holds main's three write+palindrome calls.  Raku rk_given:
three procs with substantial chunk bodies (day_type@1, season@81,
main@161).  Chunks remain unreachable — coro_call still walks IR,
forward-jumps skip every chunk.  Soft addition: a file-static
`g_chunk_body_lowering` flag set/cleared around the loop suppresses
lower_expr's "unhandled expr kind" stderr warning during proc-body
emission only — kinds without explicit cases (E_ALTERNATE, E_ITERATE,
E_CSET_*, E_REVASSIGN, E_REVSWAP) emit harmless SM_PUSH_NULL inside
the dead chunk; warning still fires for executable code via
lower_stmt.  Frame-slot resolution stays at runtime (`icn_scope_patch`
unchanged); E_VAR lowers to `SM_PUSH_VAR <name>` name-keyed via
NV_GET_fn — no scope-patch needed at lower-time.  Static-variable
persistence in coro_call unchanged.  Generator kinds (E_EVERY,
E_SUSPEND, E_BANG_BINARY, E_LCONCAT, E_LIMIT, E_RANDOM, E_SECTION*)
emit legacy `SM_PUSH_EXPR + SM_BB_PUMP` inside chunks — the gating
note in the spec; CH-17h reactivates CH-15b once CH-17c flips
consumers.  Gates byte-identical to baseline: smoke ×6 PASS
(7/7, 5/5, 5/5, 5/5, 5/5, 4/4), isolation gate PASS, csnobol4 Budne
PASS=61, Icon corpus PASS=186 FAIL=47 XFAIL=30 TOTAL=263,
unified_broker PASS=49, scrip_all_modes PASS=2.  Documented in
`docs/CHUNKS-step17b-prime-validation.md`.  Files touched:
`src/runtime/x86/sm_lower.c` only.  Next rung: **CH-17c** —
flip `coro_call` consumer sites to dispatch via entry_pc when
non-(-1); add companion `sm_call_proc(int entry_pc, ...)`.

**CH-17b'' LANDED sess #80, 2026-05-07** — frame-slot baking at
lower-time.  Carved as a separate rung when CH-17b' deferred
frame-slot resolution and left chunks emitting `SM_PUSH_VAR <name>`
for params/locals — a shape that would have broken CH-17c on
consumer flip (NV table reads instead of FRAME.env reads).  Two
new opcodes `SM_LOAD_FRAME` / `SM_STORE_FRAME` (a[0].i = slot)
added to `sm_prog.h`; handlers in `sm_interp.c` route through
three pure-DESCR_t forwarders in `coro_runtime.c`
(`icn_frame_env_active`, `icn_frame_env_load`, `icn_frame_env_store`)
— no EXPR_t leakage across the SM/IR boundary.  Outside an Icon
frame, both opcodes push FAILDESCR (mirrors SM_LOAD_GLOCAL).  JIT
codegen named-FATAL stubs (M5 territory).

In `sm_lower.c`, chunk-body emission loop builds a per-proc
IcnScope mirroring `icn_scope_patch` without IR mutation (params
0..nparams-1, then E_GLOBAL-decl names, then body E_VAR walk;
globals via `global_register` are excluded from scope so they
bridge to NV).  `lower_expr`'s E_VAR / E_ASSIGN(LHS=E_VAR) cases
consult the scope under `g_chunk_body_lowering`; in-scope names
emit SM_LOAD_FRAME / SM_STORE_FRAME, out-of-scope names fall
through to SM_PUSH_VAR / SM_STORE_VAR (unchanged at stmt-level).

Empirical proof: `--dump-sm --run test/icon/palindrome.icn`
shows the palindrome chunk now emits SM_LOAD_FRAME / SM_STORE_FRAME
for `s`, `i`, `j` (was SM_PUSH_VAR / SM_STORE_VAR in CH-17b').

Pre-existing E_FNC malform note (inherited from CH-17b', NOT
introduced here): the `case E_FNC` lowering at sm_lower.c:832–834
does `lower_expr(children[0..nargs-1])` then `SM_CALL s=e->sval
nargs` — pushing nargs+1 values but popping only nargs.  Result:
chunks containing E_FNC have a stack-leak shape that would
corrupt execution if reached.  Chunks remain dead code today so
this is unreachable; CH-17c must fix it when wiring the consumer.

Chunks remain unreachable — `coro_call` still walks IR; chunks
forward-jumped over by SM_JUMP.  Gates byte-identical to baseline:
smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4), isolation gate PASS,
csnobol4 Budne PASS=61, unified_broker PASS=49, full Icon corpus
PASS=186 FAIL=47 XFAIL=30 TOTAL=263.

Files touched:
`src/runtime/x86/sm_prog.h`, `src/runtime/x86/sm_prog.c`,
`src/runtime/x86/sm_interp.c`, `src/runtime/x86/sm_codegen.c`,
`src/runtime/x86/sm_lower.c`, `src/runtime/x86/sm_interp_test.c`,
`src/runtime/interp/coro_runtime.c`.

Next rung: **CH-17c** — flip `coro_call` consumer sites to
dispatch via entry_pc when non-(-1); add companion
`sm_call_proc(int entry_pc, ...)`; fix the E_FNC stack-leak shape
inherited from CH-17b'.

**CH-17c LANDED sess #82, 2026-05-07** — consumer-side flip.
`sm_call_proc(int entry_pc, int nparams, DESCR_t *args, int nargs)`
added to `coro_runtime.c`: pushes `IcnFrame` with param slots bound
from args, delegates body execution to `sm_call_chunk(entry_pc)` (nested
SM_State; `SM_LOAD_FRAME`/`SM_STORE_FRAME` see the live frame via
`icn_frame_env_load/store`), pops frame on return.  `nparams` added to
`IcnProcEntry` (populated from `proc->ival` in `polyglot.c`);
`gather_entry_pc`/`gather_nparams` added to `coro_t` (icon_gen.h).
`Icn_coro_stage_t` gains `entry_pc`/`nparams`.  All three staging sites
flipped; `proc_trampoline` and `gather_trampoline` dispatch via
`sm_call_proc` when `entry_pc >= 0`, fall back to `coro_call` when `-1`.
E_FNC lowering in `sm_lower.c` fixed for Icon-style nodes (`e->sval == NULL`,
name in `children[0]->sval`): now emits `SM_CALL(fn, real_nargs)` — fixes
the empty-name / stack-shape bug in proc-body chunks.  Empirical proof:
`SCRIP_PROC_ENTRY_PCS=1 --run palindrome.icn` shows palindrome@1 /
main@54; `proc_trampoline` dispatches via `sm_call_proc` for both.
Static-variable persistence deferred to CH-17g (keyed on `EXPR_t*`).
`coro_drive_fnc` left for CH-17g cleanup.  Gates byte-identical to
baseline: smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4), isolation PASS,
csnobol4 Budne PASS=61, unified_broker PASS=49, Icon corpus PASS=186
FAIL=47 XFAIL=30 TOTAL=263, scrip_all_modes PASS=2.
Documented in `docs/CHUNKS-step17c-validation.md`.
Files: `src/runtime/interp/coro_runtime.h`, `src/runtime/interp/coro_runtime.c`,
`src/driver/polyglot.c`, `src/frontend/icon/icon_gen.h`,
`src/runtime/x86/sm_lower.c`.  Next rung: **CH-17d** (sm_lower emits
named chunks for Prolog predicates).
**CH-17d LANDED sess #83, 2026-05-07** — producer-side: `sm_lower.c` now
emits named-chunk skeletons (SM_JUMP+SM_LABEL+SM_RETURN+SM_LABEL) for every
entry in `g_pl_pred_table`; loop added immediately after the Icon/Raku
proc-chunk loop.  `sm_resolve_proc_entry_pcs` (CH-17a) now finds non-(-1)
entry_pcs for all Prolog predicates: `palindrome/2@1`, `main/0@5` confirmed
via `SCRIP_PROC_ENTRY_PCS=1`.  Consumer dormant (chunks forward-jumped over).
Gates byte-identical: smoke ×5 PASS, isolation PASS, unified_broker PASS=49,
Budne PASS=61, Icon corpus PASS=186 FAIL=47 XFAIL=30 TOTAL=263.
Documented in `docs/CHUNKS-step17d-validation.md`.
Files: `src/runtime/x86/sm_lower.c`.  Next rung: **CH-17e** (flip Prolog
consumers: pl_box_choice_pc and friends; --run Prolog end-to-end).
**CH-17e LANDED sess #84, 2026-05-07** — consumer-side flip. `pl_box_choice_pc(int entry_pc, Term **caller_args, int arity)` added to `pl_broker.h/c` (one-shot box calling `sm_call_chunk(entry_pc)`). `pl_pred_entry_lookup(const char*)` added to `pl_runtime.h/c`. Five consumer sites flipped: `interp_eval.c` E_FNC Prolog dispatch + E_CHOICE case; `pl_runtime.c` msort/predsort + general user-pred dispatch; `interp_hooks.c` polyglot hook; `polyglot.c` main/0 entry (sm_call_chunk when epc>=0). All sites: entry_pc>=0 → chunk path, else legacy IR fallback. Chunks skeleton-only (SM_RETURN from CH-17d); sm_call_chunk returns FAILDESCR (correct 'no solution'). No crash. Gates byte-identical: smoke x5 PASS, isolation PASS, unified_broker PASS=49, Budne PASS=61, Icon PASS=186/47/30 TOTAL=263. SCRIP HEAD `7cfa0a96`. Next rung: **CH-17f** (fill E_CHOICE/E_CLAUSE bodies in sm_lower.c; --run Prolog produces correct output).

**CH-17f LANDED sess #85, 2026-05-07** — new `SM_BB_ONCE_PROC` opcode (`a[0].s = "name/arity"`, `a[1].i = arity`) replaces the legacy `lower_expr(E_CHOICE) + SM_BB_ONCE` path that pushed raw `EXPR_t*` to the SM value stack and called `coro_eval(E_CHOICE)` at runtime → FATAL "unhandled kind 59". `lower_stmt` LANG_PL branch emits `SM_BB_ONCE_PROC key, arity` directly from `s->subject->sval`; `lower_expr` E_CHOICE case same. Non-E_CHOICE directive subjects fall through to legacy path. Runtime: `pl_pred_table_lookup_global(key)` → `pl_box_choice(IR, g_pl_env, arity)` → `bb_broker(BB_ONCE)` — fully correct Prolog execution via the existing IR broker. No EXPR_t* pushed or walked at the SM statement-dispatch layer. Predicate chunk bodies remain skeleton-only (CH-17d SM_RETURN); chunk body fill deferred to follow-on rung. `--run` Prolog programs now produce correct output: hello.pl → "Hello, World!", roman.pl → correct. Gates: smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4), isolation PASS, Budne PASS=61, unified_broker PASS=49, Icon corpus 186/47/30 TOTAL=263 (byte-identical). Documented in `docs/CHUNKS-step17f-validation.md`. Files: `sm_prog.h`, `sm_prog.c`, `sm_interp.c`, `sm_codegen.c`, `sm_lower.c`. SCRIP @ `a2c6c089`. Next rung: **CH-17g** (drop `EXPR_t *proc` from `IcnProcEntry`; lift `code_free` gate).

**CH-17g-call-sites LANDED sess 2026-05-09** — first of three carved sub-rungs (CH-17g-call-sites / CH-17g-statics / CH-17g-final).  CH-17g as written assumed CH-17c had flipped every `proc_table[i].proc` consumer, but empirically CH-17c flipped only the trampoline layer (`proc_trampoline`, `gather_trampoline`).  Eight `coro_call(proc_table[i].proc, args, nargs)` consumer call sites still read `.proc` directly: `coro_value.c` (E_FNC user-proc dispatch), `raku_builtins.c` (Raku method-call dispatch), `interp_eval.c` ×3 (user-proc value-context, fallback, U-22 cross-language), `interp_hooks.c` (SNO→Icon usercall), `interp_exec.c` ×3 (top-level main dispatch), `polyglot.c` (single-language Icon main).  This rung adds `proc_table_call(int pi, DESCR_t *args, int nargs)` to `coro_runtime.{c,h}` — `entry_pc >= 0 ? sm_call_proc : coro_call` — and flips the eight call sites to use it.  Trampoline-layer staging at `coro_runtime.c:1125, 1213, 1503` left as-is (CH-17c's flip already lives inside the trampolines).  `coro_drive_fnc` (`coro_runtime.c:1721`) intentionally NOT flipped — IR walker by design, M4-cleanup territory (CH-17h).  `sm_lower.c:1742` is producer-side, stays.  Pure routing reorganisation; no behavioural change because every flipped site still reaches the same two paths (chunk via `sm_call_proc` when `entry_pc >= 0`, IR via `coro_call` otherwise).  Gates byte-identical to baseline: smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4), isolation PASS, unified_broker PASS=49, csnobol4 Budne PASS=50 (this session's pre-flip baseline; differs from CH-17f's recorded PASS=61, environmental — investigation deferred), Icon corpus PASS=186 FAIL=47 XFAIL=30 TOTAL=263, scrip_all_modes PASS=2 FAIL=0.  Documented in `docs/CHUNKS-step17g-call-sites-validation.md`.  Files: `src/runtime/interp/coro_runtime.h` + `coro_runtime.c` (helper); `coro_value.c`, `raku_builtins.c`, `interp_eval.c`, `interp_hooks.c`, `interp_exec.c`, `polyglot.c` (call-site flips).  Next rung: **CH-17g-statics** (re-key static-variable storage off EXPR_t*).
**CH-17g-statics LANDED sess 2026-05-09** — `static_ent_t` struct in `coro_runtime.c` re-keyed: `EXPR_t *proc` field replaced by `int entry_pc` + `const char *proc_name`.  New file-static helper `static_proc_entry_pc(name)` walks `proc_table[]` and returns the resolved entry_pc (or -1 if not yet lowered).  New `static_entry_matches(...)` predicate: primary key `(entry_pc, var_name)` when both sides have `entry_pc >= 0`; fallback to `(proc_name, var_name)` for the legacy coro_call path where entry_pc is still -1.  Icon proc names are interned (unique per source proc), so name-string identity under `strcmp` provides the same scoping guarantee that EXPR_t* pointer identity did.  `static_get` / `static_set` signatures unchanged (still take `EXPR_t *proc` — compatible with coro_call); internally extract `proc->sval` + resolve entry_pc.  No external callers of static_get/static_set exist outside coro_runtime.c.  On set-update: if a slot was stored with entry_pc==-1 and entry_pc has since been resolved, the slot is upgraded in place.  Gates byte-identical: smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4), isolation PASS, unified_broker PASS=49, scrip_all_modes PASS=2, Icon --run PASS=186 FAIL=47 XFAIL=30 TOTAL=263, rung36_jcon_statics PASS.  Documented in `docs/CHUNKS-step17g-statics-validation.md`.  Files: `src/runtime/interp/coro_runtime.c`.  Next rung: **CH-17g-final** (drop `EXPR_t *proc` from `IcnProcEntry`; lift `code_free` gate — precondition: CH-17h must land first to migrate remaining generator kinds so coro_call legacy body can be deleted).

**CH-17g-final-SURVEY LANDED sess 2026-05-09** — `docs/CHUNKS-step17g-final-survey.md` documents that **CH-17h-SURVEY's "land CH-17g-final first" recommendation is empirically wrong**.  The legacy `coro_call` body is the live, hot, only consumer of Icon/Raku user-proc dispatch in `--run` mode — the same mode that the Icon corpus baseline gate (186/47/30) runs every program through.  Probe instrumentation (reverted before commit) showed that for `procedure main() write("hello") end` under `--run`, `proc_table_call` is reached with `entry_pc=-1`, the `if (entry_pc >= 0)` chunk-dispatch branch is skipped, and the fallback `coro_call(proc_table[pi].proc, args, nargs)` produces the program's output.  Root cause: `sm_resolve_proc_entry_pcs` (CH-17a's resolver) is invoked from `sm_preamble`, which `--run` does not call (`scrip.c:557–561` dispatches to `polyglot_execute` directly for non-SNO `--run`, never reaching `sm_lower`).  Therefore every `proc_table[i].entry_pc` stays at `-1` in `--run` mode and the legacy body is the only path.  CH-17h-SURVEY's audit of `sm_lower.c:1303` was correct as a lowering-site finding; its inferred runtime-side claim was not, because the lowering-site dead arm and the runtime-side `coro_call` body are different code paths.  Recommendation in the survey doc: split CH-17g-final's preconditions into two new rungs (**CH-17g-runtime-bridge** — chunks dispatch builtins so `--run` of trivial Icon programs produces output instead of FATAL "Undefined function"; and **CH-17g-irrun-lowers** — invoke `sm_lower`/`sm_resolve_proc_entry_pcs` from `--run` before `polyglot_execute` so `entry_pc >= 0` for every proc regardless of mode).  Once both land, CH-17g-final's deletions become safe.  Alternative: merge CH-17h, CH-17g-runtime-bridge, and CH-17g-irrun-lowers into CH-17g-final as a single coupled rung.  Gates re-confirmed byte-identical post-revert: smoke ×6 PASS, isolation PASS, unified_broker PASS=49.  Files (all reverted): `src/runtime/interp/coro_runtime.c` (probe).  Awaits Lon decision on sequencing.

**CH-17g-runtime-bridge-DESIGN LANDED sess 2026-05-09** — `docs/CHUNKS-step17g-runtime-bridge-design.md` records the architectural investigation behind the bridge rung.  Empirical mechanism of the FATAL: `--run --dump-sm` shows the chunk emits `SM_PUSH_LIT_S "hello..." / SM_CALL_FN s="write" nargs=1 / SM_POP / SM_RETURN` — clean lowering, no IR leakage.  Dispatch fails because `SM_CALL_FN`'s handler in `sm_interp.c:931–1212` walks: special pseudo-calls → DATA dispatch → SM-native user fn (`sm_label_pc_lookup`) → `INVOKE_fn`/`APPLY_fn` (SNOBOL4 builtin registry).  Icon's `write` lives in `interp_eval.c:309` inside `icn_call_builtin(EXPR_t *call, DESCR_t *args, int nargs)`, which is on the legacy IR-walker path and never registered through `register_fn`.  `APPLY_fn` returns FAIL → chunk surfaces "Error 5: Undefined function or operation."  Two solutions weighed: (A) extract a name-based helper `icn_try_call_builtin_by_name(fn, args, nargs, &out)` covering ~30 EXPR_t-free Icon builtins (write, writes, integer, string, real, char, type, copy, list, table, read, repl, upto, find, any, many, tab, move, match, …) and wire it into `SM_CALL_FN` after `INVOKE_fn`'s FAIL; (B) register Icon builtins in the SNOBOL4 fn table.  Recommendation: A (B causes cross-language pollution — `write` would resolve in SNOBOL4-only programs).  Implementation split into three sub-rungs: **CH-17g-runtime-bridge-1** (refactor: extract `icn_try_call_builtin_by_name`; gate=corpus byte-identical, pure refactor); **CH-17g-runtime-bridge-2** (wire into `SM_CALL_FN`; gate=`--run` of trivial Icon proc produces output identical to `--run`); **CH-17g-runtime-bridge-3** (Raku/SCAN bridges if needed).  Files: `src/driver/interp_eval.{c,h}`, `src/runtime/x86/sm_interp.c`.  No new opcodes, no IR fields, no `sm_lower.c` changes.  Once the bridge lands, CH-17g-irrun-lowers can invoke `sm_lower` from `--run` with chunk dispatch gated behind a runtime flag (off by default to preserve existing behavior; on for end-to-end migration).  Each line-1303 generator kind (E_EVERY, E_SUSPEND, …) becomes its own per-kind migration: a chunk-side producer (lower into pure SM) + a chunk-side consumer (new SM opcode mirroring CH-17f's `SM_BB_ONCE_PROC`).  Gates this session: smoke ×6 PASS, isolation PASS, unified_broker PASS=49 (no source touched).

**CH-17g-runtime-bridge-1 LANDED sess 2026-05-09** — pure refactor as scoped.  Added `int icn_try_call_builtin_by_name(const char *fn, DESCR_t *args, int nargs, DESCR_t *out)` to `src/driver/interp_eval.c` covering `write` and `writes` — verbatim copies of the same logic that lived inline in `icn_call_builtin`.  Reorganised `icn_call_builtin` to delegate to the new helper after the Raku/SCAN dispatch but before the user-proc / clone-or-fallback paths.  Declaration added to `src/driver/interp_private.h` next to the existing `icn_call_builtin` decl.  Behaviour identical to baseline: `icn_call_builtin` still takes `EXPR_t *call` and dispatches the same set of builtins it always did; dispatch order inside it is unchanged (Raku → SCAN → write/writes via helper → user proc → clone-or-fallback); every existing caller (`coro_bb_fnc`, BB adapters in `coro_value.c` and `coro_runtime.c`) sees identical results.  Helper's branches are exact copies of the inlined code they replace; future drift prevented by `icn_call_builtin` calling the helper directly.  Gates byte-identical: smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4), isolation PASS, unified_broker PASS=49, scrip_all_modes PASS=2, Icon corpus `--run` PASS=186 FAIL=47 XFAIL=30 TOTAL=263.  `--run /tmp/probe.icn` still FATALs (helper defined but not yet wired into `SM_CALL_FN`; that's CH-17g-runtime-bridge-2).  Documented in `docs/CHUNKS-step17g-runtime-bridge-1-validation.md`.  Files: `src/driver/interp_eval.c` (+79 −26), `src/driver/interp_private.h` (+5 −0), `docs/CHUNKS-step17g-runtime-bridge-1-validation.md` (new).

**CH-17g-runtime-bridge-2 LANDED sess 2026-05-09** — `icn_try_call_builtin_by_name` wired into `SM_CALL_FN`.  `./scrip --run /tmp/probe.icn` now produces `hello from icon proc`, byte-identical to `--run`.  Multi-call Icon programs (write + writes + numeric arg) also byte-identical.  Important placement subtlety discovered by probe: bridge-DESIGN proposed placing the helper call *after* `INVOKE_fn` returned FAIL, but `APPLY_fn` raises a SNOBOL4 runtime error via `sno_err` and **`longjmp`s out** through `g_sno_err_jmp` when a name is not in any registry — control never returns to the post-INVOKE_fn fallback.  Corrected placement: helper tried *first*, falls through to `INVOKE_fn` only when helper returns 0 (unknown name).  Safety: helper recognises only a fixed list (`write`, `writes` today); for any other name it returns 0 and `INVOKE_fn` runs unchanged.  No SNOBOL4 builtin is shadowed: SNOBOL4 has no `write`/`writes` builtin, helper's recognition list restricted to Icon-unique names.  If a future Icon builtin name overlaps with a SNOBOL4 builtin (none today), order would need to flip back with a `setjmp` wrapper around `INVOKE_fn`.  Single file change: `src/runtime/x86/sm_interp.c` (+24 −1).  Local `extern` decl of the helper inline at the call site (consistent with sm_interp.c's existing style for cross-module externs).  No new opcodes, no IR fields, no `sm_lower.c` changes.  Gates byte-identical: smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4), isolation PASS, unified_broker PASS=49, scrip_all_modes PASS=2, Icon corpus `--run` PASS=186 FAIL=47 XFAIL=30 TOTAL=263.  New gate (Icon `--run` of trivial program byte-identical to `--run`): PASS — explicit success criterion from bridge plan met.  What still doesn't work: `--run` of programs using Icon builtins not yet in helper (read, integer, string, type, copy, list, table, …) still FATAL.  Coverage extends one builtin at a time.  Documented in `docs/CHUNKS-step17g-runtime-bridge-2-validation.md`.
**CH-17g-runtime-bridge-3 LANDED sess 2026-05-09** — extended `icn_try_call_builtin_by_name` from 2 names (`write`, `writes`) to 10, adding eight pure value-transform Icon builtins: `integer`, `real`, `string`, `numeric`, `char`, `ord`, `type`, `image` (0 or 1 arg).  Each new branch is a verbatim port of the equivalent in-eval branch in `interp_eval.c`'s E_FNC switch with two mechanical changes: `interp_eval(e->children[i])` → `args[i-1]` (already pre-evaluated by the SM_CALL_FN handler before invoking the helper), and `return X;` → `*out = X; return 1;` to honour the helper's 1=handled / 0=fall-through contract.  In-eval branches retained — pure additive, legacy `--run` IR-walker path unchanged.  Selection rationale: each of the eight is EXPR_t-free, single-pass arg evaluation, no write-back through `e->children[i]` lvalue identity, no `&pos`/`&subject` mutation, frame-independent.  Builtins explicitly deferred: `read`/`tab`/`move`/`find`/`upto`/`match`/`any`/`many` (scan-context state), `repl`/`left`/`right`/`center`/`reverse`/`map`/`trim`/`copy`/`list`/`table` (multi-arg with default-handling — queue for follow-on), `push`/`pop`/`pull`/`get`/`put` (write back through children[1] lvalue identity — need EXPR_t-aware path or per-kind chunk migration under CH-17h).  Gates byte-identical to baseline: smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4), isolation PASS, unified_broker PASS=49 FAIL=0, scrip_all_modes PASS=2 FAIL=0, Icon corpus `--run` PASS=186 FAIL=47 XFAIL=30 TOTAL=263, csnobol4 Budne PASS=50 FAIL=100 SKIP=8 (matches CH-17g-call-sites baseline; environmental variance vs CH-17f's recorded 61).  New gate (trivial Icon proc using all 8 new builtins, `--run` byte-identical to `--run`): PASS — 11 calls covering all eight names.  `test/icon/generators.icn` now byte-identical between modes (previously diverged on `--run`); `test/icon/meander.icn` and `test/icon/queens.icn` still diverge under `--run` because they use unbridged builtins (`read`, `tab`, `find`, `move`, `repl`, `list`).  Single file change: `src/driver/interp_eval.c` (+162 −1).  No new opcodes, no IR fields, no `sm_lower.c` changes, no `sm_interp.c` changes (bridge-2's wire-up at SM_CALL_FN already routes every name through the helper).  Documented in `docs/CHUNKS-step17g-runtime-bridge-3-validation.md`.  SCRIP @ `57a90476`.

**CH-17g-runtime-bridge-4 LANDED sess 2026-05-09** — extended `icn_try_call_builtin_by_name` from 10 names (post-bridge-3) to 27 by adding 17 more EXPR_t-free Icon builtins: multi-arg pure transforms (`repl`, `reverse`, `map`, `trim`, `left`, `right`, `center`), math (`abs`, `max`, `min`, `sqrt`), containers (`copy`, `list`, `table`), I/O (`read`, `reads`), process control (`stop`).  Each branch verbatim-ported from in-eval E_FNC switch with `interp_eval(e->children[i])` → `args[i-1]`; in-eval branches retained; pure additive.  Subtleties handled inline: `trim`'s `g_lang` read (safe — `polyglot_execute` sets `g_lang=1` before any Icon proc in either mode); `max`/`min` loop bounds (0-indexed `args[]` vs 1-indexed `children[]`); `stop()`'s ignore-args-exit(0) behavior matched verbatim (Icon-spec gap pre-existing).  Gates byte-identical: smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4), isolation PASS, unified_broker PASS=49 FAIL=0, scrip_all_modes PASS=2 FAIL=0, Icon corpus `--run` PASS=186 FAIL=47 XFAIL=30 TOTAL=263.  New gates: 14-call multi-arg probe under `--run` byte-identical to `--run`; `read()` under `--run` byte-identical (pipe stdin).  Surfaces (not regressions): `test/icon/queens.icn` now reaches further; FATALs on `SM_ACOMP` opcode (separate `sm_interp` gap, not bridge); `test/icon/meander.icn` reaches further, FATALs on `tab()` (scan-context family — bridge-5).  Single file change: `src/driver/interp_eval.c` (+261 −1).  No new opcodes, no IR fields, no `sm_lower.c` or `sm_interp.c` changes.  Documented in `docs/CHUNKS-step17g-runtime-bridge-4-validation.md`.  SCRIP @ `5e526155`.  Cumulative bridge coverage: 27 names (write, writes, integer, real, string, numeric, char, ord, type, image{0,1}, repl, reverse, map, trim, left, right, center, abs, max, min, sqrt, copy, list, table, read, reads, stop).  Next rung options: (a) **bridge-5 scan-context** (`tab`/`move`/`find`/`upto`/`match`/`any`/`many` — needs `&pos`/`&subject` care, may interact with existing `scan_try_call_builtin`); (b) **CH-17g-irrun-lowers** (`--run` invokes `sm_lower` so entry_pc resolves regardless of mode); (c) **SM_ACOMP opcode handler** in `sm_interp.c` (surfaced by queens.icn — small fix unblocks array-composition under chunks).

**CH-17g-runtime-bridge-acomp LANDED sess 2026-05-09** — closes the SM_ACOMP runtime gap surfaced by `queens.icn` after bridge-4 widened Icon builtin reach.  Two coupled changes — neither sufficient alone.  (1) Lowering bug at `sm_lower.c:859`: all six numeric comparison EKinds (E_EQ/E_NE/E_LT/E_LE/E_GT/E_GE) collapsed onto a single argument-less `SM_ACOMP` opcode; comparator unrecoverable at runtime.  Emit changed to `sm_emit_i(p, SM_ACOMP, (int64_t)e->kind)` so `a[0].i` carries the operator EKind.  (2) Missing `case SM_ACOMP:` in `sm_interp.c`'s switch — fell through to `default` FATAL "unhandled opcode 82".  Handler added: pops `r`/`l`, coerces SNUL→0 (matches SM_ADD convention), reads via `to_real`-shape promotion, dispatches on the EKind argument, and applies Icon-style relop semantics — on success push the RIGHT operand and set `last_ok=1` (so `every write(2 < (1 to 4))` yields `3, 4`); on failure push FAILDESCR and clear `last_ok`.  `SM_JUMP_F` already tests `last_ok` (sm_interp.c:276) so dispatch wires up automatically.  Mirrors the `NUMREL` macro at `interp_eval.c:3162–3171` line for line.  Default arm in the switch is a safety net for any pre-bridge-acomp SM_Program (unreachable on freshly lowered code).  `sm_prog.c:222` extended to print the operator EKind under `--dump-sm` (`SM_ACOMP i=67` for E_EQ, `i=63` for E_LT).  Stale `sm_codegen.c:1177` comment refreshed: SM_ACOMP/SM_LCOMP were lumped together as "stubbed by design because Icon bypasses sm_lower" — that rationale dissolved in CH-17b' (sess #78); SM_ACOMP entry removed, SM_LCOMP entry narrowed and noted as a follow-on rung (SM_LCOMP has the same shape bug for E_LLT/E_LLE/E_LGT/E_LGE/E_LEQ/E_LNE collapse, deferred to bridge-lcomp).  JIT codegen for SM_ACOMP remains `h_unimpl` (M5 territory; named-FATAL pattern).  Probe verified: `if i = 0 then write("eq"); if i < 1 then write("lt")` under `--run` produces `eq\nlt\n`, byte-identical to `--run` modulo the pre-existing if-then trailing-value leak (a separate, reproducible-without-SM_ACOMP issue, not introduced by this rung).  `queens.icn --run` no longer FATALs on opcode 82 — runs to `0 solutions total.` (a different correctness surface; queens.icn under `--run` ALSO produces wrong output, "Error 3 Erroneous array or table reference" — pre-existing).  Gates byte-identical to baseline: smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 4/4, 5/5), isolation PASS, unified_broker PASS=49, scrip_all_modes PASS=2 (NET emit SKIP — no ilasm/mono), Icon corpus `--run` PASS=186 FAIL=47 XFAIL=30 TOTAL=263.  Documented in `docs/CHUNKS-step17g-runtime-bridge-acomp-validation.md`.  Files: `src/runtime/x86/sm_lower.c` (1-line behavioural), `src/runtime/x86/sm_interp.c` (+39 SM_ACOMP handler), `src/runtime/x86/sm_prog.c` (1-line print case), `src/runtime/x86/sm_codegen.c` (comment refresh, no behavioural change).  Next rung options unchanged from bridge-4's list, minus (c): (a) **bridge-5 scan-context** (`tab`/`move`/`find`/`upto`/`match`/`any`/`many`); (b) **CH-17g-irrun-lowers** (`--run` invokes `sm_lower` so `entry_pc` resolves regardless of mode); (d) **bridge-lcomp** (sibling of acomp for SM_LCOMP — string relops have the same shape bug; surfaces will arrive when corpus reaches one under `--run`).

**CH-17g-runtime-bridge-lcomp LANDED sess 2026-05-09** — sibling of bridge-acomp; closes the asymmetry that doc explicitly flagged as a follow-on rung.  Mirrors bridge-acomp for the string/lexicographic relops: same shape bug, same fix pattern.  (1) Lowering at `sm_lower.c:872` had collapsed all six string comparison EKinds (E_LLT/E_LLE/E_LGT/E_LGE/E_LEQ/E_LNE) onto a single argument-less `SM_LCOMP`; emit changed to `sm_emit_i(p, SM_LCOMP, (int64_t)e->kind)`.  (2) `case SM_LCOMP:` added to `sm_interp.c` switch: pops `r`/`l`, runs `strcmp(VARVAL_fn(l), VARVAL_fn(r))`, dispatches on EKind, applies Icon-style relop semantics — on success push the RIGHT operand and set `last_ok=1`; on failure push FAILDESCR and clear `last_ok`.  Mirrors the STRREL macro at `interp_eval.c:3184–3194` line for line.  Default arm in the switch is a safety net for any pre-bridge-lcomp SM_Program (unreachable on freshly lowered code).  No change to `sm_prog.c` (SM_LCOMP was already in the `i=` print case, predating bridge-acomp).  `sm_codegen.c` comment further refreshed: SM_LCOMP entry removed from the "stubbed by design" list and folded into the bridge-acomp/lcomp closing note (JIT codegen still `h_unimpl` for both — M5 territory).  No corpus surface today (no Icon program in `test/icon` reaches a string relop under `--run`); landed preventatively for symmetry with bridge-acomp — half-fixed pair would leave `sm_codegen.c` telling an inconsistent story to the next reader.  Probe verified: `s := "abc"; if s == "abc" then write("seq"); if s << "abd" then write("slt"); if s >> "abb" then write("sgt")` under `--run` produces `seq\nslt\nsgt\n`, byte-identical to `--run` modulo the pre-existing trailing-value-after-if-then leak documented in bridge-acomp (same artifact, not introduced by this rung).  Gates byte-identical to baseline: smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 4/4, 5/5), isolation PASS, unified_broker PASS=49, scrip_all_modes PASS=2, Icon corpus `--run` PASS=186 FAIL=47 XFAIL=30 TOTAL=263.  Documented in `docs/CHUNKS-step17g-runtime-bridge-lcomp-validation.md`.  Files: `src/runtime/x86/sm_lower.c` (1-line behavioural), `src/runtime/x86/sm_interp.c` (+47 SM_LCOMP handler), `src/runtime/x86/sm_codegen.c` (comment refresh).  Next rung options: (a) **bridge-5 scan-context** (`tab`/`move`/`find`/`upto`/`match`/`any`/`many` — needs `&pos`/`&subject` care, may interact with existing `scan_try_call_builtin`); (b) **CH-17g-irrun-lowers** (`--run` invokes `sm_lower` so `entry_pc` resolves regardless of mode — a structural change to `scrip.c:557–561` non-SNO `--run` dispatch; awaiting Lon decision per CH-17g-final-SURVEY's recommendation to split CH-17g-final's preconditions into runtime-bridge and irrun-lowers rungs).

**CH-17g-irrun-lowers LANDED sess 2026-05-09** — `g_irrun_lowers` flag (polyglot.h/c, default 0); `sm_resolve_irrun_entry_pcs(prog)` (scrip_sm.h/c) runs sm_lower→resolve→free without keeping SM live; `polyglot_execute` calls it after `polyglot_init` when flag set; `scrip.c` sets/clears flag around non-SNO `--run` dispatch. Guard at every SM-dispatch site (`g_current_sm_prog != NULL`): `proc_table_call` (coro_runtime.c), `pl_chunk_fn` (pl_broker.c), two sites pl_runtime.c, interp_hooks.c, two sites interp_eval.c, polyglot.c main/0. Entry_pcs resolve under `--run`; execution falls through to legacy path (correct — SM freed). Gates: smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4), isolation PASS, unified_broker PASS=49. Specific gate: `SCRIP_PROC_ENTRY_PCS=1 --run hello.icn` → `main entry_pc=1`; `SCRIP_PROC_ENTRY_PCS=1 --run hello.pl` → `main/0 entry_pc=1`. Docs: `docs/CHUNKS-step17g-irrun-lowers-validation.md`. SCRIP @ `5d6de5f7`. **Next rung: CH-17g-final** (drop `AST_t *proc` from IcnProcEntry; lift code_free gate — both preconditions now met).

**CH-17g-final-SURVEY-2 LANDED sess 2026-05-09** — `docs/CHUNKS-step17g-final-survey-2.md` documents that the asserted "both CH-17g-final preconditions met" claim at the bottom of `CHUNKS-step17g-irrun-lowers-validation.md` is incorrect.  Empirical probe (`proc_table[proc_count].proc = NULL` in `polyglot.c:178`, reverted before commit) shows three live consumers of the field, two load-bearing.  (i) `sm_lower.c:1757` reads `.proc` producer-side at lowering time; with proc=NULL the SM_Program for `procedure main() write("hello") end` truncates to `SM_BB_PUMP_PROC + SM_HALT` (2 instrs) and `--run` produces empty output, rc=0.  (ii) `coro_runtime.c:603` `proc_table_call` falls back to `coro_call(proc_table[pi].proc, ...)` when `g_current_sm_prog == NULL`, which is exactly the state under `--run` because `sm_resolve_irrun_entry_pcs` discards SM_Program with `sm_prog_free` immediately after populating entry_pcs.  Probe `--run` SIGSEGVs on `coro_call`'s scope-build dereferencing NULL.  (iii) Lines 1179, 1267, 1557, 1775 (trampoline staging + `coro_drive_fnc`) all stage `.proc` for the legacy fallback.  CH-17g-irrun-lowers correctly delivered the *observability* piece — `entry_pc >= 0` resolves under `--run` and is visible under `SCRIP_PROC_ENTRY_PCS=1` — but did not deliver the *execution* piece.  Three options for sequencing forward: A) `--run` non-SNO becomes alias for `--run` (drops a user-facing mode contract); B) `sm_resolve_irrun_entry_pcs` retains SM_Program (sets `g_current_sm_prog = sm`) so dispatch guards take the SM path under `--run` too (smallest code change; risk: `--run`'s known gaps become `--run`'s gaps); C) amend GOAL-CHUNKS Step 17's "IR freed unconditionally for all six frontends" criterion to "conditional on execution mode" (smallest code change but largest spec change).  Producer-side `sm_lower.c:1757` cleanup is independent of A/B/C.  **Lon decision sess 2026-05-09: Option A** — AST and SM both deleted between phases (separation/isolation).  Carved **CH-17g-irrun-execution** as the rung that delivers it: `scrip.c` non-SNO `--run` routes through the same `sm_preamble` + `sm_run_with_recovery` path as `--run`; drop `g_irrun_lowers` flag and `sm_resolve_irrun_entry_pcs` helper (superseded); SNOBOL4 `--run` path unchanged.  After CH-17g-irrun-execution lands, CH-17g-final closes Step 17.  Gates re-confirmed post-revert: smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4), build clean, both `--run` and `--run` of `/tmp/probe.icn` produce `hello from icon` byte-identical.
