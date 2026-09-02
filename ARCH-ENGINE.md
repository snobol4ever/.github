# ARCH-ENGINE.md — the SCRIP engine: IR → lower → optimizer → emitter → templates/x86 encoder → ζ storage → driver

This is the consolidated architecture doc for SCRIP's language-agnostic compiler engine — the machinery every frontend (SNOBOL4, Icon, Prolog, Snocone, Rebus, Raku/Pascal in progress) lowers into and every backend emission path shares. It replaces nine separate docs, retired the same session this file was minted (`ARCH-IR.md`, `ARCH-x86.md`, `ARCH-EMITTER.md`, `ARCH-ZETA-LOCAL-STORAGE.md`, `ARCH-PATTERN-CHOICE-CARRIER.md`, `ARCH-PASSTHRU.md`, `ARCH-SCRIP.md`, `ARCH-SILLY.md`, `ARCH-PROFILE-BOX-HISTOGRAM.md`) — see RETIRED NAMES at the end for what moved where. Per-language architecture (SNOBOL4/Icon/Prolog/etc. frontends, register contracts, language-specific corrections) lives in the separate LANGUAGES-subset consolidation, not here.

**Method note (binds every section below):** each source doc was truth-checked in both directions against current HEAD — (1) doc-vs-source: does the named path/symbol/mechanism still exist where claimed; (2) ruling-vs-code: does a design the doc presents as settled/landed still hold in the code, since a landed-then-silently-regressed mechanism is a regression to name, not a stale doc to relabel. True content moved close to verbatim; false content is corrected with its evidence cited inline. Three sections (IR, x86, ζ Local Storage) had a same-day CEO audit FINDING as a seed worklist (`FINDING-2026-08-27-ceo-arch-audit-*`); the rest had no prior audit and were verified fresh. Several corrections found in this pass are *more* current than even that same-day audit — the tree moved again while the audit was being written, which is itself the standing lesson: verify against HEAD, not against the last thing that verified against HEAD.

**Retired law, project-wide, relevant everywhere below:** "stackless" is a void term (Lon, 2026-08-27) — all three zetas live ON the machine stack (ζ-SPINE/RSP, ζ-ACTIVATION-FRAME/RBP, ζ-STANDING/root); "no software value stack" means no *extra* hand-rolled stack beside those, never "off the hardware stack." Frame placement (RSP vs RBP) is governed by RULES.md § BB FRAME-PLACEMENT CRITERION — a behavioral, language-blind test (unbounded growth between a box's γ-exit and β-resume, or an unknowable operator→operand offset) — never by box-kind or language directly; any older box-kind/language framing surviving below is documented as a *consequence* of that criterion, not an independent rule.

---

## ⛔⭐⭐ THE CALLING-CONVENTION RULING (Lon, in-chat to ceo, 2026-08-30: "make the convention safe.")

The bypass census (seat10: SCRIP_OPT=0 regresses 187/1649, SCRIP_ZD=0 306/1649, DEFAULT 0/1649) traced to ONE architectural weakness at four named implementers of the push-continuations/jmp calling convention — **a fixed rsp-relative offset trusted across a call/return boundary with nothing tracking accumulated depth**, an invariant never enforced, only usually satisfied by what the optimizer happens to eliminate. A FOURTH site turned out to be PRIOR ART: the codebase had already patched one instance, tuned to "arrive at today's post-carve depth" — proof that site-by-site patching is the path that produced the disease. **Lon ruled: make the convention safe — depth is TRACKED structurally, never assumed; site patches are not the cure.** Execution row: `calling-convention-depth-tracked` (hq_P). Acceptance instrument: seat10's census — a safe convention collapses both bypass arms toward the DEFAULT arm's 0, and the flags become genuinely safe fallbacks instead of documented-but-broken escape hatches. Until it lands, the fleet caution stands: a bypass arm is NOT a control.

### ⛔⭐⭐ THE PORT-EXIT VALUE CONTRACT (hq_C ruling 2026-09-01, on seat02's census — the companion clause to the ruling above, and the SAME law: the convention is made safe STRUCTURALLY, not site by site.)

**A PORT TRANSFER CARRIES NO VALUE. `rax` IS SCRATCH ACROSS EVERY PORT (α, β, γ, ω). The ONE site that promotes `rax` from scratch to the DESCR return register is procedure-exit wiring — a transfer whose target is the enclosing chain's own γ label — and that site MUST be preceded by an explicit tagged-`DESCR_t` write.**

**Why it is a contract and not a style note.** A procedure's γ exit opens `mov rdi, rax` / `mov rsi, rdx`: it forwards `rax:rdx` as the returned `DESCR_t`. The caller's landing then tells success from failure with `cmp al, DT_FAIL`. `DESCR_t.v` is a `uint8_t`, so **the tag IS the low byte of `rax`** and `DT_FAIL` is `0x68` = 104 — an ordinary number. Any untagged value reaching that exit whose low byte happens to be 104 **forges a failure**, and the caller cascades a spurious ω one frame at a time up the entire live call chain, silently abandoning every not-yet-made recursive call above the origin. It is a silent wrong answer, not a crash.

**Why the cure is at the chokepoint and not at the sites** (seat02's census is the evidence): the raw-`rax` port exits found in `src/templates/bb/` are **all one benign shape** — `rax` used as scratch in a two-word DESCR copy or a payload test — and **every one is correct** under "a port is control-flow only". Normalizing each site is a patch list over a population that is not wrong, and it re-arms the moment a new template uses `rax` as scratch, which is the normal and correct thing to do. ⭐ **The defect was never the templates: the ABI simply never specified `rax`, and procedure-exit wiring silently promotes it from scratch to a return register — two contracts on one label, with nothing checking which is in force.** Enforcement therefore belongs at `x86_jmp`/`x86_jcc` in `x86_asm.h`, the one chokepoint every port transfer already passes and the only place holding both the concrete target and the promotion site's identity.

⛔ **The forgeable-sentinel cure (moving `DT_FAIL` out of the data value space) is held IN RESERVE, deliberately.** It is the larger blast radius and is not needed while this contract holds, because nothing untagged can arrive at the promotion site. It becomes the answer only if a legitimate exit is found that must promote `rax` with no preceding tagged write — decided in advance so it is not re-litigated then.

⚠️ **Status, stated so this section is not read as describing a finished world:** the generation-time check exists at the chokepoint as an **audit that reports and does not yet refuse** (`SCRIP_PORT_EXIT_AUDIT=1`; it emits zero bytes and is proven byte-identical to the pre-change compiler). The graded instrument is `scripts/test_gate_port_exit_value_contract.sh`, which is **RED at 18 sites / 36 transfers across 3 languages** at the time of writing (seat03's corrected count — the original 9 undercounted by half; see the task file's LEDGER) and is not wired into `make test`. ⭐ **Emitter-side coverage is now 100%** (seat05, 2026-09-02, tree `0cb5aa13`) — was measured incomplete at 86% because the chokepoint compared a jump's target only against the CURRENT chain's own `g_emit.flat_lbl_γ`, structurally blind to a jump into ANOTHER chain's promoting γ (the fbench.pas cross-procedure case). Closed via a whole-program label pre-pass (`port_exit_prepass_build()`, `src/emitter/emit.cpp`) over `g_stage2.proc_table[]`/`bbp.table[]`, spending Lon's in-chat NO-NEW-GLOBALS grant on exactly one file-static `std::unordered_set<std::string>` — the gate's cross-check against the post-hoc TEXT scan is retained as a live self-test, not removed, and continues to prove the two views agree. Refusal (obligation 1) still needs emit-time `rax` provenance — a SEPARATE, larger new-state question from the label set, not yet asked or granted.

⭐ **This law is deliberately written in TWO places and neither may move alone** — here, and as the banner comment beside `x86_port_hook` in `src/templates/x86/x86_asm.h`. A rule kept in one file goes stale in the other; that is the standing thirteenth-batch clause, applied to itself.

---

## ⛔⭐⭐ THE RUNTIME-GOAL RULING (Lon, in-chat to ceo, 2026-09-01 ~20:53: *"Remove that Prolog runtime interpreter, we already decided that Prolog should be re-using EVAL and CODE."*)

Prolog has NO runtime interpreter. A goal unknown at compile time (`call/N`, `catch/3`'s goal, the goal arm of the all-solutions and negation builtins, later-invoked asserted bodies) is compiled AT RUN TIME through the one runtime-compilation path the engine already has — the EVAL/CODE path (`src/runtime/runtime_eval.c`: graph → `optimizer_run` → `emit_chain` → jump) and the pattern JIT's shape (`src/runtime/rt/bb_pat_build.cpp:84-110`: compile once at construction, cache the blob) — and then runs as wired Byrd boxes like every other goal. The `plc_*` solver family in `src/runtime/by_name_dispatch.c` (a solver tree built by `strcmp` on functor names and driven by a `switch` — the last dispatch loop over data in the tree, measured 2026-09-01) is deleted under this ruling. Corollary of RULES.md:84 (NO SM/BB WALKING AT RUNTIME): a dispatch loop over runtime-constructed goal terms is walking by another name. Same order, same minute: the dead AST walkers still linked into `libscrip_rt.so` (`scope_patch`, `static_get/set`, `driver_call.c:139-380`, the `eval_*`/`exec_stmt` stubs) are deleted, never re-stubbed. Rungs: MASTER-PLAN ⭐C36 and ⭐I14. Evidence: `FINDING-2026-09-01-ceo-modes-3-4-no-ast-or-ir-walking-emission-path-clean-runtime-evaluators-bomb-prolog-call-n-solver-is-the-one-live-interpreter.md`.

## ⭐⭐ THE CO-EXPRESSION STACK RULING (Lon, in-chat to ceo, 2026-09-02 08:45: *"The pthread's storage was meant to be MMAP'd. Like any thread it needs a proper stack just like the RSP stack."*)

A co-expression is a thread and gets a thread's stack: the pthread's own, mmap'd, a proper stack like the main RSP stack — never a GC-heap block (the compactor moves live stacks; pinning is out by s263) and never the slab. SCRIP allocates no stack block for it; size rides `pthread_attr_setstacksize` when the default is too small; the GC scans the thread's stack as a root set with bounds from `pthread_getattr_np`. This is the same law as THE THREE ZETAS' frame placement (activation frames on the machine stack; only genuine escapers on the heap) applied to a second machine stack. Row: `coexpr-stack-leaves-the-compacting-gc-heap` (GOAL-ICON-100 carries the ruling for its lane).

## ⛔⭐⭐⭐ THE PROLOG ACTIVATION-ζ RULING (Lon, in-chat to ceo, 2026-09-02 09:55: *"So what are we waiting for, give Prolog its activation ZETA like all the rest. OMG! Go fix it."*)

Prolog is not a special case of THE THREE ZETAS; it is the language the Byrd box came from, and it gets the same frame law as Icon: a predicate call is a box with a ζ-ACTIVATION-FRAME on RBP that survives γ so β can resume it (FRAME-PLACEMENT CRITERION — the γ→β window is the canonical unbounded-growth case). Clause alternatives are the choice box's β path; cut is its ω; the trail is β's undo and lives in the frame. Measured before the ruling (hq_B, FINDING `a4a7cfff`): a two-clause `fact/2` emitted zero rbp-relative instructions — Prolog had no activation frame at all, which is why the shallow board reads 351/371 while the backtracking rungs read 3/15. Consequence for the runtime: control that a port should carry leaves `by_name_dispatch.c` — the call/N solver (C36), string dispatch (P6), setjmp failure (P7), the polled exception flag (C37) — after the frame lands. Rung: MASTER-PLAN C21, hq_C, first in the order.

## Intermediate Representation

The shared IR every frontend compiles to. Two distinct node types live here, both under `src/ir/` (moved off `src/contracts/`/`src/include/`/`src/lower/` in the srcreorg — see Retired names below): `tree_t` (the parse-time expression/AST node, `src/ir/ast.h`) and `IR_t` (the Byrd-box graph node, `src/ir/IR.h:178`, the thing the pipeline actually lowers to and templates consume). ARCH-IR historically documented only `tree_t`; `IR_t` is added here since it is this doc's namesake structure and was previously undocumented.

### `tree_t` — the AST expression node

Source of truth: `src/ir/ast.h:97`.

```c
struct tree_t {
    tree_e      t;       /* node kind */
    union {
        char      *sval; /* TT_QLIT text, TT_VAR/TT_FNC/TT_IDX name */
        long long  ival;  /* TT_ILIT value */
        double     dval;  /* TT_FLIT value */
    } v;
    int         n;        /* child count */
    tree_t    **c;        /* children array */
    int         line;
};
```
No `ast_left`/`ast_right`/`ast_arg`/`ast_nargs` accessor wrappers exist anywhere in `src/` — a prior version of this doc named them; they were never built. Callers use `->c[i]`/`->n` directly (parse/lower time only — RULES.md's NO AST WALKING ban is scoped to SM/emitter code in modes 3/4, not the frontend/lower stage that owns this struct). Builders: `ast_node_new(kind)`, `ast_push(parent, child)` (`ast.h:113,131`).

**Node kinds** — unchanged groupings, current as of this pass:
**Leaves:** TT_QLIT, TT_ILIT, TT_FLIT, TT_NUL, TT_VAR, TT_KEYWORD
**Unary:** TT_MNS, TT_NOT, TT_IND ($), TT_NAME (.), TT_ATP (@), TT_STR (*), TT_TILDE
**Binary:** TT_ADD, TT_SUB, TT_MUL, TT_DIV, TT_EXP, TT_SEQ, TT_CAT, TT_ALT, TT_CAPT_COND_ASGN, TT_CAPT_IMM_ASGN, TT_IDX, TT_CHOICE (Icon/Prolog), TT_CLAUSE (Prolog), TT_UNIFY (Prolog), TT_CUT (Prolog)
**N-ary:** TT_FNC, TT_CONCAT, TT_LIST, TT_APPLY
**Pattern:** TT_ARBNO, TT_ARBN, TT_SCAN, TT_POS, TT_RPOS, TT_LEN, TT_RLEN, TT_REM, TT_ARB, TT_FENCE, TT_FAIL, TT_SUCCEED, TT_ABORT, TT_BAL

### `IR_t` — the Byrd-box graph node

Source of truth: `src/ir/IR.h:178`.

```c
struct IR_t {
    IR_e         op;
    IR_ref_t     γ;          /* succeed edge */
    IR_ref_t     ω;          /* concede edge */
    IR_t       **operands;   /* PEERS RULE: grow operands here, never add IR_t fields */
    int          n_operands;
    int          in_scan;
    int          seal;
    int          pat_static;
    union { const char *sval; int64_t ival; double dval; };
};
```
Only γ/ω are struct fields (α-proceed/β-recede are edge-walk concepts at the wiring layer, not stored refs on the node itself). `ir_operand_push(IR_t *nd, IR_t *child)` (`IR.h:271`, `scrip_ir.c:170`) is the sole operand-growth path — PEERS RULE, keep `IR_t` lean, do not add fields.

`IR_graph_t` (`IR.h:198`, was `BB_graph_t`) wraps a graph: `entry` (IR_t*) plus an `all` array.

### `STMT_t` — the statement

Source of truth: `src/frontend/snobol4/scrip_cc.h:13`. Current fields — **no `lang` field or `LANG_*` macros exist**; see Deleted section below.

```c
struct STMT_t {
    char    *label;
    tree_t  *subject, *pattern, *replacement;
    char    *goto_s, *goto_f, *goto_u;
    tree_t  *goto_s_expr, *goto_f_expr, *goto_u_expr;
    int      lineno, stno, is_end, has_eq, nofail;
    STMT_t  *next;
};
```

### Five phases of a SNOBOL4 statement

```
Label:  Subject  Pattern  =Replacement  :S(goto)  :F(goto)
```

| Phase | Name | Can Fail | Backtracks |
|-------|------|----------|------------|
| 1 | Subject eval | yes | no |
| 2 | Pattern build | yes | no |
| 3 | Match | yes | YES — the IR/Byrd-box graph |
| 4 | Replacement eval | yes | no |
| 5 | Assign | no | no |

Phases 1,2,4,5 are straight-line; phase 3 is a Byrd box graph. Icon carries no separate value-stack machine at all — an Icon program is one connected Byrd box graph, values live in per-box DATA slots, inter-box transitions are direct jumps, zero SM opcodes are emitted (verified: `SCRIP_ICN_BB=1 ./scrip --dump-sm prog.icn` → `count=0`, per RULES.md ICON SM = ZERO OPCODES). This was previously worded as Icon boxes carrying "no software value stack" — keep that phrasing; "stackless" is a retired/void term project-wide (RULES.md, Lon 2026-08-27: all three zetas are ON the machine stack — ζ-SPINE/RSP, ζ-ACTIVATION-FRAME/RBP, ζ-STANDING/root — "no software value stack" means no *extra*, hand-rolled value stack beside those, not "off the stack").

### Drive modes (BrokerMode) — ⚠ verify before relying on the call chain

`BrokerMode` (`src/ir/bb_box.h:69`) still exists as an enum — `bb_scan, bb_pump, bb_once` (lower-case now; the prior `BB_SCAN`/`BB_PUMP`/`BB_ONCE` spelling is retired). The three drive-mode *semantics* below are still descriptively accurate to how SNOBOL4/Icon/Prolog scan/generate/prove, respectively:

| Mode | Language | Drive behaviour |
|------|----------|----------------|
| `bb_scan` | SNOBOL4 | Try cursor positions 0..Ω; stop on first match |
| `bb_pump` | Icon | Produce every value until ω |
| `bb_once` | Prolog | Enter once; report γ or ω; OR-box handles retry |

**What could not be verified this pass:** the old doc's dispatch chain (`SM_EXEC_STMT → exec_stmt() → bb_broker(root, BB_SCAN, ...)`, one shared `bb_broker()` entry point in `src/runtime/x86/bb_broker.c`) is dead — `bb_broker` has **zero hits anywhere in `src/`**, and `src/runtime/x86/` does not exist as a directory. `SM_BB_PUMP`/`SM_BB_ONCE` opcodes are also gone (grep: zero hits including in comments); only `SM_EXEC_STMT` survives (`src/ir/SM.h:64`). Per CLAUDE.md's Byrd-box description, ports are wired at *compile time* into straight-line jumps — "the wiring IS the execution, no runtime dispatch" — which is consistent with a runtime broker function no longer existing, but this pass did not locate and confirm the specific compile-time mechanism that replaced `bb_broker()`'s role for the three drive modes. Flagging as an open question rather than guessing a replacement: **how do `bb_scan`/`bb_pump`/`bb_once` actually get selected/wired per box graph today?** — worth a follow-up FINDING before anyone designs against this section.

### Polyglot `CODE_t*`

A single `CODE_t*` may contain statements from multiple source languages. `parse_scrip_polyglot()` in `scrip.c` parses a `.scrip` fenced-block file, compiling each block with its own frontend, appending all `STMT_t` chains in source order into one `CODE_t*`.

Fence syntax (tags case-insensitive: `SNOBOL4`, `Icon`, `Prolog`; unknown tags skipped):
````
```SNOBOL4
  ... snobol4 source ...
```
```Icon
  ... icon source ...
```
```Prolog
  ... prolog source ...
```
````

### ⛔ Deleted: `STMT_t.lang` / `LANG_*` (was documented at old :100-116)

The prior version of this doc taught a `STMT_t.lang` field and a `LANG_SNO`/`LANG_ICN`/`LANG_PL` macro family as the live per-statement language discriminator, dispatched by `sm_lower`/`polyglot_init`. **Neither exists.** Confirmed by direct read of the live `STMT_t` (above, `scrip_cc.h:13-22`) — no `lang` field — and by `grep -rn LANG_ src/` returning zero hits in any live file (the only hits are `IR_LANG_SNO`/`LANG_SNO` inside `src/lower/lower_snobol4.gz5-parked-41b53078.c`, a parked, non-live file — a different, unrelated IR-level tag, not this field). This is exactly the shape RULES.md's `emit_no_lang` gate (NO LANGUAGE SENTINEL PAST FIRST DISPATCH) forbids, and the doc was teaching the forbidden shape as current design — a reader implementing against it would have written a gate violation from the architecture doc itself. Language dispatch downstream of lower is IR-kind-only, per RULES.md.

### IR consolidation — single-structure lowering output

**Invariant.** Every BB/IR graph produced by lowering reaches engines through one storage location: `g_stage2.bbp.table[bb_idx]` (was `g_stage2.sm.bb_table[bb_idx]` — the `sm` field is gone, replaced by `bbp`, a `bb_program_t`). The registry entries carry an `int bb_idx` and nothing else for graph access.

```c
int bb_program_add(bb_program_t *p, IR_graph_t *bbg);   /* src/ir/bb_program.h:11, scrip_ir.c:194 */
```
Callers: `lower_icon.c:1226`, `lower_pascal.c:733`, `lower_prolog.c:850,856` — all `bb_program_add(&g_stage2.bbp, ...)`. (Was `SM_seq_bb_add`; that name is gone.)

The proc/predicate registry types are `ProcEntry` and `Resolve_PredTable` (`src/ir/stage2.h:20,39` — were `IcnProcEntry`/`Pl_PredEntry_BB`/`Pl_PredTable`); the lookup helpers live in `src/runtime/builtins/resolution.{c,h}` as `resolve_pred_table_insert`/`resolve_pred_table_lookup` (was the `icn_runtime.h`/`pl_runtime.h` strangler pair, `bb_graph_of_proc`/`bb_graph_of_pred` — those directories/names are gone). `rt_pl_b_end_register`, the old doc's standalone-mode-4 registration entry point, has **zero hits** in `src/` — dead, unreplaced-or-unfound this pass; do not cite it.

### Emitter / templates

One driver: `src/emitter/emit.cpp` (3,572 lines) + `emit.h` (789 lines) — folds every former `emit_core`/`emit_bb`/`emit_drive`/etc. silo, per `emit.h`'s own top-of-file merge comment. `src/emitter/emit_str.cpp` and `sil_macros.h` survive unmerged; **`emit_io.c` does not exist** (a prior correction claimed it "survives unmerged" — it does not; drop the citation).

Templates are no longer flat. As of the 2026-08-27 srcreorg, `src/templates/` holds **zero top-level `.cpp` files** and three subdirectories:
- `bb/` — 134 `bb_*.cpp` files, one per Byrd-box kind
- `x86/` — `x86_asm.h` (encoder primitives, the register-contract source of truth) + `x86_arg_roles.h`
- `xa/` — 17 `xa_*.cpp` files (flat-emission machinery: prologue/epilogue, macro libraries, blob builders)

Any prior count ("161 files, no subdirs") is stale; re-derive with `ls src/templates/{bb,xa}/*.cpp | wc -l` rather than trust a fixed number here, since this tree reorganizes often (re-gridded twice this project so far).

The EC-series architecture (`emit_core.c/.h`, `emit_sm.c`, `emit_bb.c`, `BB_templates/`, `SM_templates/`, `sm_dispatch.c`, `bb_regs.h`, `emit_defs.h`) does not exist and never will again — this has now been correctly flagged stale twice (2026-06-30, and reconfirmed in this pass); its "one template per kind, no per-target silos" design intent survived into the current `emit.cpp`/`bb/`+`xa/` structure even though none of its concrete names did.

## Retired names (IR)

- `src/contracts/`, `src/include/`, parts of `src/lower/` (IR/ast/SM/stage2 pieces) → `src/ir/`
- `src/include/ast.h` → `src/ir/ast.h`
- `src/lower/SM.h` → `src/ir/SM.h`
- `src/include/stage2.h` → `src/ir/stage2.h`
- `src/lower/sm_prog.c` → `src/ir/sm_prog.c`
- `src/runtime/x86/{sm_prog.h,sm_interp.c,bb_box.h,bb_broker.c}` → directory gone; `bb_box.h` → `src/ir/bb_box.h`; `bb_broker.c`/`bb_broker()` — no live replacement located this pass
- `src/runtime/interp/icn_runtime.h`, `pl_runtime.h` → `src/runtime/builtins/resolution.{c,h}` (+ `gen_runtime.h` for Icon generator runtime support)
- `BB_graph_t` → `IR_graph_t`
- `IcnProcEntry` / `Pl_PredEntry_BB` → `ProcEntry`
- `Pl_PredTable` → `Resolve_PredTable`
- `g_stage2.sm.bb_table` → `g_stage2.bbp.table`
- `SM_seq_bb_add` → `bb_program_add`
- `bb_graph_of_proc` / `bb_graph_of_pred` → `resolve_pred_table_lookup` (+ insert)
- `rt_pl_b_end_register` → no live symbol found (flag, don't cite)
- `SM_BB_PUMP`, `SM_BB_ONCE` → deleted, no replacement opcodes; only `SM_EXEC_STMT` survives
- `BB_SCAN`/`BB_PUMP`/`BB_ONCE` (enum members) → lower-case `bb_scan`/`bb_pump`/`bb_once`
- `ast_left`/`ast_right`/`ast_arg`/`ast_nargs` → never existed; direct `->c[i]`/`->n` access
- `emit_core.c/.h`, `emit_sm.c`, `emit_bb.c`, `emit_drive.c`, `BB_templates/`, `XA_templates/`, `SM_templates/`, `sm_dispatch.c`, `bb_regs.h`, `emit_defs.h` → all deleted (EC-series), no replacement files (concepts live in `emit.cpp`/`emit.h`)
- `emit_io.c` → does not exist (prior doc wrongly said "survives unmerged")
- flat `src/templates/*.cpp` (161 files) → `src/templates/{bb,x86,xa}/` (134 + 2 + 17 = 153 files, re-count don't trust this number long-term)
- "stackless" (Icon) → "no software value stack" (VOID term project-wide per RULES.md)
- `GOAL-ICON-BB.md` cross-ref → superseded by `GOAL-ICON-100.md`
## Emitter

⛔ **MAJOR DRIFT, undetected until this pass — no prior CEO audit covered this file.** ARCH-EMITTER.md's entire "Current compiled units (3 + 1 frozen)" table is dead: `emit_core.c`, `emit_bb.c`, `emit_sm.c`, `sm_jit_interp.c` — **zero hits anywhere under `src/`** (`find src -iname 'emit_core.c' -o -iname 'emit_bb.c' -o -iname 'emit_sm.c' -o -iname 'sm_jit_interp.c'` → empty). Its key macros `IS_TEXT`/`IS_BIN`/`IS_WIRED`/`IS_BROKERED` and globals `g_emit_mode`/`g_emit_out` are likewise zero-hit. `emit_str.h`, `sm_template_common.h`, `strtab_label_s` (cited as the template-purity helpers) do not exist either. This is not a path rename — the file split the whole doc organizes itself around was consolidated away by a later rewrite, and nobody re-pointed the doc. Cost if trusted: a session asked to add or debug an emission function would search for `emit_core.c`/`emit_bb.c`/`emit_sm.c`, find nothing, and either stall or (worse) recreate the split the codebase already left behind.

**Verified current reality.** `src/emitter/` holds exactly four files: `emit.cpp` (3,572 lines), `emit.h` (789 lines), `emit_str.cpp` (214 lines — string-formatting helpers, e.g. `emit_fmt`, the `vsnprintf`-based varargs formatter), `sil_macros.h` (83 lines — small `DESCR_t` field-access/data-move macros: `MOVD`/`MOVV`/`MOVA`/`GETDC`/`PUTDC`/`MOVBLK`/`VEQL`/`DEQL`; despite the name this is unrelated to the `SILLY` subsystem below — do not conflate the two `sil`-prefixed things).

One universal dispatcher drives everything: `emit_drive(IR_t *nd, bb_label_t *lbl_α, bb_label_t *lbl_γ, bb_label_t *lbl_ω, bb_label_t *lbl_β)` (declared emit.h:652, defined emit.cpp:1441), `switch`es on `nd->op`, and refuses to compile silently — an unhandled op is a `FATAL` abort with a message naming the op (emit.cpp:1434): *"Every op must be handled; the driver never refuses silently."* This is the mechanism behind ARCH-SCRIP.md's isolation invariant: the IR graph is walked exactly once, at EMIT TIME, by this one function, and never again at runtime.

Byte production itself does not happen in `emit_drive`'s dispatch logic — every actual x86 instruction, TEXT and BINARY medium alike, goes through the `x86(...)` encoder (RULES.md § TEMPLATE-ONLY EMISSION), which now lives at `src/templates/x86/x86_asm.h` (the 2026-08-27 srcreorg re-gridded `src/templates/` into three subdirectories: `bb/` — 134 `.cpp` box templates, `x86/` — the encoder plus `x86_arg_roles.h`, `xa/`; zero top-level `.cpp` remain in `src/templates/` itself). `emit.cpp` itself calls `x86(...)` directly 156 times for driver-level emission, alongside dispatching into the `bb/` templates for box-specific code.

TEXT vs. BINARY branching runs through `g_medium` (type `bb_medium_t`, values `BB_MEDIUM_TEXT`/`BB_MEDIUM_BINARY`) tested via the `MEDIUM_BINARY` predicate (e.g. emit.cpp:129, :155, :247) — **not** an `IS_TEXT` macro; that name is one of the dead ones above. `MEDIUM_TEXT`/`MEDIUM_BINARY`/`g_medium` appearing inside `src/emitter/emit.cpp` is correct and expected: RULES.md's "NO MEDIUM_* IN TEMPLATES" rule binds `bb_*.cpp` templates specifically (which must be medium-complete via `x86(...)`), not the one driver file that owns `g_medium` in the first place.

The old **layer-prefix naming convention partially survives**, but only as a function-naming habit inside the now-unified `emit.cpp`/`emit.h` — not as the file-level split it was originally keyed to. Confirmed alive: `emit_label_*` (`emit_label_alloc`, `emit_label_define_bb`, `emit_label_intern`, `emit_label_lookup_offset`, ...), `emit_bb_*` (`emit_bb_dispatch_jne_jmp`, `emit_bb_zeta_rdi`), `emit_sm_*` (`emit_sm_bb_pump_case`, `emit_sm_call_fn`, `emit_sm_define`, ...). Not found in the same pass: `insn_`, `emit_text_`, `emit_mode_`, `emit_seq_` — treat these four as likely retired rather than asserting it outright; nobody has re-derived the naming rules from the current single-file architecture, and that re-derivation is real follow-up work, not something this pass completed. The "Template purity invariant" section (pure `_str()` functions built from CONCAT/IF/FOR, no side effects) and the "Flat-box DATA pattern" TEXT/BINARY code example are **carried forward as OPEN, UNVERIFIED** for the same reason — they described the pre-consolidation architecture and nobody has confirmed whether the purity discipline still holds, or where, in today's `emit.cpp`. Flag for a follow-up pass with its own worklist; do not present either as current fact.

## x86 Backend

**Current layout** (re-verified this pass, srcreorg is active and moves this often): one driver `src/emitter/emit.cpp`+`emit.h`; templates split into `src/templates/bb/` (134 `bb_*.cpp` Byrd-box bodies), `src/templates/x86/` (`x86_asm.h` + `x86_arg_roles.h`, the encoder/register-contract source of truth), `src/templates/xa/` (17 `xa_*.cpp` cross-cutting wrapper files) — zero top-level `.cpp` remain directly under `src/templates/`. Two modes only: `--run` (BINARY, in-process) / `--compile` (TEXT, as+gcc; `--target` implies it). `bb_pool` (`src/ir/bb_pool.{c,h}`) is **live** and referenced tree-wide — a prior version of this doc's prune banner incorrectly listed it as deleted; that was a self-contradiction (its own body cites `bb_pool` three lines later) and is corrected here.

### Byrd Box model

Each pattern node compiles to a self-contained x86 code+data blob in `bb_pool`. Four ports, Greek names always: α (proceed), β (resume/recede), γ (succeed), ω (concede/fail).

### Boxes carry no software value stack — and the frame is NOT r12

⛔ **Corrected this pass — the doc previously taught an r12-based ζ-frame ABI that does not exist in source.** A box has CODE and DATA — no `push`/`pop` of working state in the body. That part stands. But the DATA does not live behind a dedicated "ζ frame register" `r12`; **r12 is an ordinary register**, string-matched like any other GPR in the encoder tables (`x86_asm.h:49`, `:1259`) with no special role. The real model, confirmed live in `src/templates/x86/x86_asm.h` and governed by RULES.md § BB FRAME-PLACEMENT CRITERION:

- **ζ-SPINE (RSP)** — the default. `x86_zref(off, w)` (`x86_asm.h:891`) is the spine accessor family that `ZRES`/`ZRESD`/`ZOPQ`/`ZOPD`/`ZLOC` all bottom out on when there is no activation-frame slot (`op_xf_off == -1`).
- **ζ-ACTIVATION-FRAME (RBP)** — a box is promoted here only when unbounded stack growth can intervene between a γ-exit and its β-resume (the FRAME-PLACEMENT CRITERION's operational test — canonically γ-SUSPEND, but the criterion is the growth property, not "is this a suspend box"). `zone_ref(rbp_off, spine_base, d, w)` (`x86_asm.h:949`) and `ZRES`/`ZRESD` (`:900-901`) switch to `RDQ("rbp", ...)`/`RDD("rbp", ...)` exactly when `op_xf_off != -1`.
- **ζ-STANDING** — the root/outermost frame, same ladder, one level up.

All three are machine-stack resident (never a separate pushed/popped value-stack structure, and never a heap workspace island — RULES.md, Lon 2026-08-27, "the island is dead"). "No software value stack" describes the *absence of an extra hand-rolled stack beside these*, not an absence of the machine stack — the retired word for this is "stackless" and it is void project-wide; do not use it.

> **Prolog note (2026-05-30, re-cited not re-verified this pass — status current as of last check).** The Prolog path shares one mutable `IR_graph_t` across recursive activations and uses `bb_snapshot_state`/`bb_restore_state` (`src/emitter/emit.h:237-238` — both confirmed live) to copy node slots in and out across a call — a copy-in/copy-out that is itself a form of the "push/pop of working state" this section otherwise forbids. Lon's s273 ruling (`GOAL-PROLOG-100.md`) is the current authority on where Prolog structure should live (DESCR + the three zetas, never `Term`/heap) — treat this note as a known area to re-audit against that ruling, not as settled. Cross-refs corrected: `GOAL-SNOBOL4-BB.md`/`GOAL-PROLOG-BB.md` (absent) → `GOAL-SNOBOL4-100.md`/`GOAL-PROLOG-100.md`; `SCRIP/archive/frontend/prolog/prolog_emit.c` → `one4all/archive/...` (per the 2026-08-27 x86/Prolog audit; not independently re-verified this pass).

Re-entry is handled by **allocating a fresh DATA block on every α-port entry** and chaining the old one onto a save-list reachable from the new one's header — a box "three deep" is three sibling DATA blocks with one shared CODE address, not a call stack. Box CODE is reusable but not necessarily re-entrant: two simultaneous matches against the same box address are fine iff each gets its own DATA block; the allocator's job at α-entry is guaranteeing that.

### Two block TYPES the emitter outputs (BB vs XA)

Independent of medium (BINARY for mode 3 / GAS TEXT for mode 4), every emitter template outputs exactly one of two kinds of code block:
- **BB code block** (`src/templates/bb/bb_*.cpp`) — a Byrd box: the per-IR-kind four-port (α/β/γ/ω) body that does actual WORK. In modes 3/4 a BB is the only vehicle that can build a subject, build a pattern, or build a replacement — no interpreter does it.
- **XA code block** (`src/templates/xa/xa_*.cpp`, dispatched via `xa_dispatch(XA_op_t)` — confirmed live: `emit.cpp:356`, declared `emit.h:162`, `XA_op_t` at `src/ir/XA.h:32`) — cross-cutting assembly-level wrapping: file header/footer, flat prologue/epilogue, data/rodata section, entry dispatch, pattern-blob framing, cap fixup. XA blocks do not build operands; they only wrap and link.

Medium (bytes vs text) is orthogonal: each BB or XA block is materialized as BINARY or TEXT by the same template's two arms (RULES.md BOTH-MEDIUM MANDATORY / TEMPLATE-ONLY EMISSION).

SNOBOL4 native pattern matching (5-phase `SUBJ ? PAT [= REPL]`) is specified in the LANGUAGES-subset doc covering SNOBOL4 (outside this ENGINE consolidation row's scope) — cross-ref by content (native pattern architecture, modes 3 & 4), not by the old `ARCH-LANGUAGES.md`/`GOAL-SNOBOL4-BB.md` filenames, which this pass could not confirm still exist under those names.

### Flat-BB ABI

A glob of invariant boxes is emitted as one contiguous run of straight-line x86 (`src/templates/bb/bb_glue_flat.cpp`, `src/templates/xa/xa_flat.cpp` — was `bb_flat.c`, now split and relocated under the bb/xa subdirs). Inter-box transitions are `jmp`s within the same slot — no `call`, no `ret`, no port-discriminator argument. α-entry to the glob is by jumping at the glob's first byte; γ/ω exits `jmp` outside the glob. Boxes inside a glob have no per-box prologue and no port-test register — the glob's structure encodes which port each box is entered at, statically.

```
Buffer layout (glob = N concatenated boxes' code + 1 sealed read-only region):
  [0 .. CODE_END)   x86 code — position-independent via rel8/rel32 jumps
  [CODE_END .. end) RO DATA — per-box compile-time constants, sealed adjacent,
                    reached RIP-relative as [rip + disp].
                    RW box-locals live on the ζ ladder (RSP by default,
                    promoted to RBP per the FRAME-PLACEMENT CRITERION) —
                    NOT behind a fixed register.

Entry convention:
  Control enters at the glob's first instruction (the α port of the first box).
  No port-test register; the glob's structure is static.
  The real glob preamble restores the anchor: `mov rsp, [anchor]` (xa_flat.cpp:119,
  verified live) — there is no `push r12`/`mov r12,rdi` prologue; that claim in a
  prior version of this doc does not match source.
```

### Intra-BLOB vs extra-BLOB jumps

Every emitted jump from inside a BLOB knows statically whether its target lies inside the same BLOB or outside it — a compile-time property of the generated `jmp`, not a runtime check.

**Intra-BLOB jump** — target within `[blob_start, blob_end)`. The ζ ladder and RIP base are unchanged across the jump; no save, no restore. Plain `jmp rel32 target` — the common case, every α→β/γ/ω port transition inside a glob.

**Extra-BLOB jump** — target outside `[blob_start, blob_end)`. The destination BLOB's α-preamble establishes its own ζ placement; RSP/RIP continuity is what actually survives the transition (not a callee-saved r12 — see correction above).
- **Tail extra-jump** (γ/ω exits the glob, no return) — plain `jmp rel32 target`; the common case.
- **Call-style extra-jump** (rare in flat-BB land; a capture-function callback that re-enters the broker, resuming inside the source BLOB) — needs no special save: source-BLOB RW state lives on the ζ ladder, RO constants are RIP-relative. (Historically a consolidated DATA block rode `r10`, with explicit `push r10`/`pop r10` here; r10 is retired — see the R10-OUT ladder in `GOAL-SNOBOL4-100.md`, not the absent `-BB` name.)

The invariant the emitter must hold: **never jump into the middle of a BLOB from outside** — every cross-BLOB entry lands on the α-preamble, which is the contract that the destination BLOB's locals are correctly placed before any ζ reference fires.

## Four-column box layout

Every box (text `.s` or bytes directly into `bb_pool`) follows the canonical four-column LABEL/OPERATOR/OPERANDS/GOTO form (the condensed LABEL/ACTION/GOTO notation fuses OPERATOR+OPERANDS). GAS text convention (`x86_4col`): label col 0 · operator col 24 · operands col 41 · GOTO col 88. (Not independently re-measured this pass — carried forward from the prior verified sweep.)

```
proc BIRD
    .alpha:     LIT_CHECK "Bird", 4, .gamma, .omega
    .beta:      LIT_UNDO  4,         .omega
    .gamma:     ret                                 ; γ — eax=1
    .omega:     xor     eax, eax                   ; ω — eax=0
                ret
endp
```

**Globbing:** named patterns concatenate sub-box labels into one proc, internal port wiring expressed as `jmp`. C function → NASM proc; C label → NASM local label (`.name`); goto → `jmp`; return → `ret` (or `jmp` to caller's γ/ω); α/β entry → `cmp esi, 0; je .alpha`.

## Cache coherence

After writing x86 bytes into a buffer and before jumping into it, the I-cache must be flushed. The `mprotect` RW→RX transition is the fence — verified live, `src/ir/bb_pool.c:45` (`bb_seal`): `mprotect(lo, len, PROT_READ|PROT_EXEC)`. The reverse direction exists too, for pool lifecycle: `bb_pool.c:67` (`bb_free`, RX→RW) and `:77` (`bb_pool_release`, partial RX→RW) — not in the prior version of this doc, added here since they're the natural companions to the seal.

## "Everything is dynamic"

Every sub-phase of every SNOBOL4 statement has a γ port and an ω port — the α/β/γ/ω wiring IS the execution model, all the way from the outermost statement to the innermost literal match. A statically-compiled box sequence and a dynamically-built one are the same thing; the static case is the degenerate case where the builder's output is invariant across executions. EVAL/CODE fall out for free — the runtime doing what it always does, with source text that arrived late.

## Retired names (x86)

- `BB_templates/bb_*.cpp` → `src/templates/bb/bb_*.cpp`
- `XA_templates/xa_*.cpp` → `src/templates/xa/xa_*.cpp`
- `bb_flat.c` → split into `src/templates/bb/bb_glue_flat.cpp` + `src/templates/xa/xa_flat.cpp`
- `SCRIP/archive/frontend/prolog/prolog_emit.c` → `one4all/archive/...` (per 2026-08-27 audit, not independently re-verified this pass)
- `GOAL-SNOBOL4-BB.md` → `GOAL-SNOBOL4-100.md`
- `GOAL-PROLOG-BB.md` → `GOAL-PROLOG-100.md`
- r12-as-ζ-frame-register ("`mov r12,rdi`", "`[r12+off]`") → no such role; ζ lives on RSP (spine, `x86_zref`) or RBP (activation frame, `zone_ref`/`ZRES` when `op_xf_off != -1`) per RULES.md § BB FRAME-PLACEMENT CRITERION; r12 is an ordinary encodable register
- "stackless" → "no software value stack" (VOID term project-wide)
- bb_pool "DELETED" (prune-banner self-contradiction) → live, `src/ir/bb_pool.{c,h}`
## ζ Local Storage

Byrd-box local storage — everything that today flows through `zls_build()` / `src/ir/zeta_storage.{h,c}`. This section is the authority on ζ design: what the current fixed shape is, why it took this shape, and where the design history lives for the next reset nobody wants to repeat.

### Terms

| Term | Meaning |
|---|---|
| **ζ (zeta)** | Per-activation READ-WRITE local storage of a Byrd box / box sequence. The RW half of PER-BOX LOCAL STORAGE. |
| **rZ** | The ζ base register. **Fixed = RSP.** `x86_zr()` (`src/templates/x86/x86_asm.h:489`) returns the literal string `"rsp"` unconditionally — no per-graph choice, no r12 ζ-frame register, no r12 prologue anywhere in the emitted spine. |
| **ZLS — Zeta Local Storage** | The per-activation ζ region itself. ZLS is internal and completely TYPED data — heterogeneous compiler-known struct layouts (ints, cursors, code-address continuations, DESCR t·p pairs, pointers) — NOT a homogeneous run of DESCR slots. Deliberately different from the GST/GVA concept (a uniform 16-byte-DESCR-per-variable table). |
| **COLLECTION** | Per-iteration storage for a re-entrant box (ARBNO et al.). Historically: heap-`realloc`-backed, reached by pointer from the owner's ZLS fields (§ Design history). **Current state is mixed, not a single story** — see Re-entrant storage below. |
| **zls[]** | The parallel layout table (node-id → scope_id, offset, kind), built by `zls_build()` post-optimizer. PEERS-clean: zero new `IR_t` fields. `src/ir/zeta_storage.{h,c}` (moved from `src/contracts/`), API prefix `zls_*`. `--dump-zeta` prints it. |
| **t·p** | The 16-byte DESCR_t slot unit (`{DTYPE_t v; uint32_t slen; union{s,i,r,p,arr,tbl,u}}`, `src/ir/descr.h`, moved from `src/contracts/`). All ζ offsets are multiples of 16. |
| **Frame offset grant** | The LOWER-computed offset a node is given (`src/ir/zeta_storage.c`; `IR_t` itself, `src/ir/IR.h:178`, carries no `tmp` field or any other storage-offset field — layout lives entirely in the parallel `zls[]` table, per PEERS). `IR_t`'s real fields: `op, γ, ω, operands, n_operands, in_scan, seal, pat_static`, plus a literal-value union (`sval`/`ival`/`dval`). |
| **ψ (psi)** | The moving element pointer into a COLLECTION (seed-2 idiom: `ψ13 = &ζ->_13_a[i]`). Distinct from the enclosing frame's ζ. |
| **λ (lambda)** | The landing port: post-child-call emptiness test routing to γ/ω (seed-2/3/4 idiom). |

**The typed principle.** ZLS is not a value store; it is the compiler's own per-activation struct, with individual field types and sizes known at zls-build time. Consequences: (1) `zls[]` is a per-FIELD typed map, not a per-slot DESCR/non-DESCR bit; (2) GC scanning of live ZLS uses those typed maps and skips code-address and raw fields precisely (see GC below); (3) the mode-4 `struc`/`endstruc` overlays are literally these type declarations printed — zero storage, pure documentation; (4) never reason about ζ by analogy to GVA/GST — the resemblance (both `[reg+off]`) is addressing only, not shape.

### The three zetas — the fixed shape (axes closed)

**Per RULES.md § ZETA HAS NO MODES (Lon, 2026-08-27): the multi-axis selector space this document used to describe as a live design tool is retired.** What follows is not one arm of a switch — it is the only code that exists.

Verified at HEAD: `zeta_choices.h` (`src/ir/zeta_choices.h`) still names every historical axis value as a constant (so old names stay greppable) but binds exactly one value per axis, unconditionally — `ZC_STORAGE = ZC_STORAGE_CELL_STACK`, `ZC_PORT = ZC_PORT_FORTH`, `ZC_ZETA = ZC_ZETA_ZLS2`, `ZC_FRAME = ZC_FRAME_RSP`. `grep -rn '#if.*ZC_\|#ifdef ZC_' src/` returns **zero** — no conditional axis code survives anywhere in the tree (commit `6da13973`, "ZETA HAS NO MODES: eradicate the ZC_* selector machinery").

The CLI selector trio (`--zeta-storage=`, `--zeta-port=`, `--zeta=`) **does not exist at all** in the current driver — not even as a refusing stub, and CLAUDE.md's session-start digest still teaching these three flags is itself stale as of this consolidation. An intermediate state existed briefly: commit `ad56bb88` ("the zeta selector is collapsed to ONE config; the CLI trio retires as hard errors") made them refuse with an explanatory message — the state the 2026-08-27 CEO audit FINDING for this file still cites (at scrip.c's then-`:818-820`). That refusal code was itself deleted the same day by `6da13973`, so an unrecognized `--zeta*` flag today just falls into the driver's ordinary unknown-option error, exactly as the RULES.md ruling specifies in so many words: *"a refusal that explains the old modes is itself memory of modes."* The one surviving zeta-specific flag is `--dump-zeta` — a pure inspector (`zls_dump`, gated on `dump_zeta` in `scrip.c`) printing the scope tree, typed field maps, and vslots, post-optimizer. `SCRIP_ZETA_TELEM` (pure print-only telemetry) and `SCRIP_ZETA_OMEGA_TRACE` survive too, per the same ruling's telemetry carve-out.

**THE THREE ZETAS names the shape, not a configuration:**

- **ζ-SPINE — RSP.** Fixed-size cells, LIFO, `sub rsp,K` at α / `add rsp,K` at ω (`x86_alpha_carve()`, `src/templates/x86/x86_asm.h:1764`). The default home for any box whose result and locals are reachable at a fixed, compile-time-known offset on every path.
- **ζ-ACTIVATION-FRAME — RBP.** Used exactly when the Frame-Placement Criterion (below) admits a box: unbounded γ→β growth (γ-SUSPEND is the canonical instance), or an operator→operand distance no longer statically fixed.
- **ζ-STANDING — the root / program-lifetime frame.** Persistent statics and program-lifetime state (Icon `static`/`initial` live in the GVA arena, not ζ, under this same root umbrella).

Every box reference is (RO) `[rip+disp]` or (RW) `[rZ+off]` — never a ring, never a software value stack, never an NV round-trip for an intermediate. "Stackless" is a retired term for this law (it never meant off-the-machine-stack; it meant no *software* value stack layered on top of it) — all three zetas live ON the machine stack or its heap-promoted overflow, never in a separate structure.

### Re-entrant storage — ARBNO and friends (current state is mixed, not a single story)

The original design (below, § Design history) specified ONE mechanism: a re-entrant box's per-iteration data lives in a heap-`realloc`-backed COLLECTION, owned by the box, reached by pointer from its ZLS fields (owner quad `{ptr, cap, i, prev_rZ}`), with a RELOAD LAW forbidding any cached pointer into it across a push. **That is no longer the whole truth for SNOBOL4.** The 2026-07-13 SNOBOL4-IS-ALL-STACK ruling (§ Design history) reclassified ARBNO's variable per-iteration data onto the spine itself, as a linked frame chain living on RSP, on the grounds that variable *population* is a dynamic-extent problem and dynamic extent is what the machine stack is for — the heap-flavor client set was narrowed to Icon's genuinely escaping activations (co-expressions, generator procedures) only.

Verified at HEAD, the live template (`src/templates/bb/bb_match_arbno.cpp`) carries **more than one shape**, selected per op-variant rather than a single scheme:
- `IR_MATCH_ARBNO_FRAMELESS` — "one cell, two compares, no chain" — a single fixed `sub rsp,16` cell, no heap involvement at all.
- `IR_MATCH_ARBNO_NARY`, gated on `_.op_arbno_chain` — the "ZB-FC-4 rsp linked-frame-chain" the all-stack ruling specified: `sub rsp,48` per extension, chained via a `prev`-style link, matching §14's reclassification.
- A still-live call to `rt_zcol_push` (declared `void * rt_zcol_push(void **, int *, int, long)`) — a growable-storage push, coexisting with the two rsp-resident shapes above. **This is NOT the same symbol as the original design's `rt_zcol_grow`**, which is confirmed zero-hit dead tree-wide; `rt_zcol_push` is a different, apparently narrower mechanism.

Read honestly: the migration off heap-backed COLLECTIONS for SNOBOL4 landed for at least two ARBNO shapes and is real, but a live call into a push-style growable helper in the same template file means the heap path has not been fully retired from this one box family. Whether `rt_zcol_push`'s surviving call site is dead-but-unreached code, a deliberately-kept fallback, or a genuine gap in the all-stack migration is **not resolved by this consolidation pass** — flagged here as an open question for whoever next touches ARBNO codegen, rather than asserted either way.

### GC — the 3-stage collector

SNOBOL4's SIL implementation allocated sequentially from a free pointer — bump was SNOBOL4's *original* allocator — and ran storage regeneration when exhausted; SPITBOL kept the design. SCRIP's collector is the same three stages, built to the same heritage, precise where SIL had to be conservative:

1. **MARK** — trace from the roots; set the mark flag in each live block's header.
2. **ADJUST** — one linear sweep computes each marked block's slid-down address, then rewrites every relocatable word (per-block-type maps) in marked blocks and in the roots by its target's displacement.
3. **SLIDE** — one linear memmove compacts marked blocks downward; the free pointer resets to the end.

Allocation stays pure bump between collections; zero fragmentation; allocation order preserved; no free lists; cost linear in live+heap.

**Why SCRIP can do this more precisely than SIL could:** SIL discriminated pointers from small integers **by magnitude** (hence `&MAXLNGTH`, an object-size cap, and a memory-address floor below which allocation is wasted). SCRIP's `DESCR_t{v, slen, union}` tags discriminate by **type** — no size cap, no address floor. `&MAXLNGTH` survives only as a compatibility keyword, never a real limit. The `zls[]` typed field maps ARE the collector's stack maps: for each live frame, its scope's field map says which fields are DESCR (trace the payload), `PTR_GC` (trace and fix), `PTR_CODE` (skip — continuations never relocate), or `RAW` (skip). ZLS frames themselves do not move in the v1 hybrid (the ζ-stack is not the heap); only heap blocks slide.

**Root set:** the GVA slab (all DESCR slots) · NV dictionary buckets · the live ζ chain via zls kind maps · COLLECTION owner quads (where they still apply) plus their per-activation grown-collection lists · heap-promoted ζ blocks (coexpr/suspend, each carrying its scope's kind-map id in its header) · the call-args marshaling window · machine registers at a safe point only. Two known conservative-root additions from the audit burndown: the C-side `scan_saved[]` array (nested-scan save of outer scan cursors — a heap-interior string pointer held live across an entire inner scan) and coexpr `ctx`/`pkg` structs (plain `malloc`, holding a captured register snapshot for the coexpr's whole lifetime — a documented latent gap: a string reachable *only* via a suspended coexpr's captured scan cursor can be collected today; fix home is the coexpr promotion rungs).

**Ladder status** (`src/runtime/rt/gc_heap.{h,c}`):
- **GC-0 HEADERS — landed.** Scrip-owned bump heap (mmap NORESERVE, 512MB, loud bomb on exhaustion). One 16B header per block (the SIL title-word reborn: forward-address, size, type, flags). Payloads zero-initialized. Coexistence with libgc is explicit and transitional (`ZC_HEAP_STRINGS` switch stays for testing; full retirement is GC-6). Strings (`rt_str_alloc`/`rt_str_dup`) are the proof family and are fully migrated, including the copy-site tail.
- **GC-1/2/3 MARK+ADJUST+SLIDE — landed.** Two root layers: PRECISE (marked and adjusted — NV buckets, call-args window, scan cursors, aggregate-internal DESCR cells, the live ζ chain in validated-adjust mode) and CONSERVATIVE (marked and pinned, never moved — C stack + register spill, exhaustion-flavor only). Gateway collections (triggered at runtime seams: call, assign, scan-enter, zls-alloc) are fully precise; only the rare in-allocator exhaustion fallback stays conservative.
- **GC-4 COLLECTIONS-ONTO-HEAP — open.** COLLECTION backing (where it still exists) moves from `realloc`/free to GC blocks with owner-quad fixup.
- **GC-5 VALUE-WORLD MIGRATION — partial.** Strings row landed (including its copy-site tail). `ARBLK`/`TBBLK`/`DATINST`/`VCELL` remain on libgc.
- **GC-6 RETIRE-LIBGC (SNOBOL4 path) — open.** Icon's coexpr transport may keep libgc longer than the SNOBOL4 path.
- **GC-7 PACING — open.** Allocation-threshold trigger, `&STLIMIT` semantics, `COLLECT(i)` wired to a real regeneration.

### Icon — procedure and co-expression partitioning

Icon needs two explicit partitions ζ doesn't otherwise require, because it is the one language whose activations can genuinely escape LIFO:

- **Procedure level.** Params at ABI `16*(i+1)`, locals above, a resume cell for generator procedures, return-continuation cells in the frame header. `static`/`initial` stay OUT of ζ entirely — persistent state lives in the GVA arena. **Icon suspend:** a suspended activation outlives its return; its frame heap-promotes at suspend (or at the α of a procedure statically known to suspend).
- **Co-expression level.** A co-expression is a captured activation — `create e` snapshots an environment, `@` transfers control into it, results transfer back, `^e` refreshes it to its creation state. It breaks LIFO at birth, so a co-expression's block is heap-lifetime from creation, never bump-lifetime. Live substrate: pthreads (`rt_coexpr.c`) — each co-expression owns a thread with its own machine stack; `bb_create`/`bb_activate`/`bb_coret`/`bb_cofail` templates. The design intent is for the ζ-plane to be the real abstraction and the thread to be replaceable transport underneath it, but the thread substrate is what is actually load-bearing today.

This is exactly the box-kind/language split the Frame-Placement Criterion below now governs generally — Icon needs it because Icon is the language with genuine escapers, not because "Icon" is itself a valid test anywhere in the emitter.

### ⭐ THE FRAME-PLACEMENT CRITERION — governing law (supersedes any box-kind or language test above)

*(Lon, 2026-08-27, in-chat to CEO, verbatim in substance):* **"the determining factor for whether to place a BB RESULT and/or BB LOCALS [in an activation frame] is the UNBOUNDED — i.e. unknown at compile-time — stack growth between the time a BB box leaves at GAMMA and is resumed at BETA. Or any time UNBOUNDED growth prevents an OPERAND from being loaded by its OPERATOR with a fixed offset."**

Operationalized, per box, language-blind: RESULT/LOCALS stay on ζ-SPINE (RSP) **iff** every consumer reaches them at a fixed, compile-time-known offset on every path. The moment unbounded growth can intervene — a γ→β window with arbitrary activity between (γ-SUSPEND is the canonical instance, not the criterion itself), or dynamic growth making the operator→operand distance unknowable — the box moves up the ladder to ζ-ACTIVATION-FRAME (RBP). Program-lifetime state goes to ζ-STANDING.

This is a **behavioral** predicate — it satisfies the language-blindness law by construction, and it, not any language- or box-kind-keyed test, is what admits a graph to rbp re-homing. Every place above that still reads as "SNOBOL4 is all-stack" or "Icon needs rbp for suspend/coexpr" is a *consequence* of applying this criterion to those languages' actual boxes, not an independent rule — SNOBOL4 happens to have no boxes the criterion admits to rbp; Icon does. Authority: RULES.md § BB FRAME-PLACEMENT CRITERION.

---

### Design history

Six-then-more storage models were tried across 3+ months and two repos before the shape above settled. Carried forward so it never has to be re-excavated from git again.

**M1 — Interp-era heap ζ per box instance (one4all, 2026-03/04).** `bb_node_t` C graph; box = `str_t fn(void *zeta, int entry)`; ζ struct calloc'd per box instance; ports were C function pointers. Trivially correct, but heap churn per instance, pointer-chasing dispatch, and C functions as boxes — later ruled out entirely (NO C BYRD-BOX FUNCTIONS). **Reset:** RT-120 voided dispatch-into-C wholesale — blobs must be self-contained x86.

**M2 — The 4/28 chunk model (one4all@`4757bbcd`, the beauty self-host milestone).** Two-tier registers: rbp = SM statement frame, r12 = the *moving* ζ block base. Activation = template-clone: a `.data` init image per block family, cloned via `mmap`-per-call (`blk_alloc`). It shipped the milestone — the chunk *structure* (what fields each activation carries, per statement/pattern/DEFINE body/ARBNO) is the asset that survived; the mmap-per-activation and two-register cost did not. **Reset:** SCRIP fresh-started from the one4all tree without its history — the lesson that produced this document.

**M3 — One-register frame ratification (one4all GZ3, 2026-05-30/31).** Icon's software value stack demolished; ζ register switched r15→r12 as the ratified *addressing* layout (not allocation — M5's later mistake was reading "[r12+off]" as "r12 is set once").

**M4 — The seed ladder (`corpus/library/probe_reference/bb/test_sno_1..6.c`, `test_icon.c`).** Hand-written C goldens, each pinning one allocation law: per-iteration moving-ζ-pointer (seed 1, the distilled COLLECTION); caller-stack-allocated callee ζ with typed per-iteration element storage (seed 2, the ψ/λ precedent); lazy calloc-or-memset reuse (seeds 3/4); one code body time-multiplexing two ζ planes through one register (seed 5, the two-plane law); the C-call-stack-as-broker pattern (seed 6). No reset — permanent references.

**M5 — The flat model (TMP-ERADICATE era).** A single compile-time bump cursor granting every node a static offset for the *life of the program*. TMP-ERADICATE itself was a genuine, kept victory (LOWER owns the layout; emit-time allocators deleted). Its cost: one lifetime for everything meant no home for per-iteration state (the ARBNO wall), cumulative-backtracking frame clobber, and scan-scratch overrun patched case-by-case. **Reset lesson:** lifetime is a first-class property of storage — a single program-lifetime cursor cannot express activation or iteration lifetimes no matter how many patches it receives.

**M6 — The ZETA-BLOCKS pivot (2026-07-05).** Brought the 4/28 chunk *structure* forward onto the live spine minus its costs: a bump ζ-stack, `.prev`-link nesting instead of push-r12, no `.bss` in emitted programs, layouts computed pre-emit into the parallel `zls[]` table, heap-backed COLLECTIONs for re-entrant boxes (cap removed), heap promotion for suspendable scopes. This generation produced the ZL-GROUP/ZL-FN/ZL-PAT/ZL-ITER/ZL-COEXPR layout classes, the bump-allocator design-space exploration (arena sizing, `.prev` nesting, the now-fully-retired `ZC_*` choice-macro axes), and the SIL-heritage GC design above. Its GC and layout-class thinking is still live; its *allocation register* (moving-r12-with-`.prev`-chains) was superseded by M7.

**M7 — The FORTH-cell / region consolidation (2026-07-11 onward, s21/s22/s28/s29/s37/s39/s40/s41, culminating in the 2026-08-27 Frame-Placement Criterion above).** The eureka: "we have full control of everything hanging off a moving RSP and index from it much like FORTH does." Locked-in core: every ζ cell is one variable-length, 16-byte-aligned unit on RSP, direct-indexed, result always at cell-relative offset zero, every operand offset generated statically. Operands *suspend* rather than pop (the one bend in the FORTH analogy) — α pushes, the cell stays live through every γ/β cycle, ω pops, and LIFO holds because ω order reverses α order along every control path. Alternation pads every arm to the max footprint (ANS FORTH's own IF-arms-must-match-stack-effect law, reused). UNWIND (`mov rsp,[anchor]; jmp target`) is the one dynamic escape hatch, for ARBNO teardown, bare-FENCE cut, and statement/driver return.

Three further ratifications completed the shape:
- **Three-region memory (s37):** R1 = the C/ζ stack (a walkable frame chain, root-scanned at α/ω); R2 = one reserved-VA data workspace, bump-allocated with GC title words, mark→forward→adjust→slide on exhaustion (refcounting ruled out — slide already needs the tracer, and cycles exist); R3 = a dual-mapped RW/RX code slab that never moves (a deliberate divergence from SPITBOL, which collects code in-workspace).
- **Register-anchored islands (s39):** any register-anchored structure whose base must never move — the GVA slot table is the landed instance — gets its own reserved VA island (reserve big, commit on demand), because an emitted graph self-loads its anchor register at entry and cannot patch a live copy already held in running frames if the backing relocates. Islands are infrastructure, not a fourth collector region.
- **The two-flavor law, amended (s40, then reclassified s50 → the Frame-Placement Criterion, 2026-08-27):** STACK flavor (fixed-size cells, one per box, nothing else on the spine) vs HEAP flavor (escapable boxes — ζ and any variable collection data both on GC). The 2026-07-13 ruling narrowed the heap-flavor client set to Icon-only (co-expressions, generator procedures) on the grounds that SNOBOL4 has no genuinely escaping activations — stored patterns are values, `DEFINE` is pure LIFO pushdown, `DEFER`/EVAL/CODE only ever looked like escapes because the old C trampoline forced a return. The 2026-08-27 criterion above subsumes this: it replaced the language/box-kind test with a behavioral one, of which the s50 ruling is the SNOBOL4 special case.

---

### Reading list (primary sources, path-verified this session)

Seeds: `corpus/library/probe_reference/bb/test_sno_1..6.c`, `test_icon.c`. 4/28 era (one4all@`4757bbcd`, archival, not in this tree): `artifacts/asm/beauty_prog.s`, `archive/backend/snobol4_asm.mac`, `archive/backend/blk_alloc.c`, `archive/backend/emit_emitters/emit_x64.c`. **The original document's two "current-tree study set" artifacts (`SCRIP/artifacts/asm/fixtures/arbno_alt.s`, `SCRIP/archive/backend/bb_boxes.s`) do not exist — do not cite them.** Live spine, verified at HEAD: `src/ir/zeta_storage.{h,c}` (the zls[] builder), `src/ir/IR.h:178` (`IR_t`), `src/ir/zeta_choices.h` (the retired-axis constants), `src/templates/xa/xa_flat.cpp` (the anchor-slot prologue/epilogue, not an r12 prologue), `src/emitter/emit.cpp` (`x86_scratch_off` assignment sites in the IR-dispatch switch; **the audit FINDING's `:1620/1628` citation is already stale — current HEAD carries at least six assignment sites, ~`:1623–1668`, plus multiple `fc_geom`-gated read sites in the `IR_MATCH_*` arms around `:1126–1136`; re-grep rather than trust either number**), `src/templates/bb/bb_match_arbno.cpp` (the mixed ARBNO shapes, see Re-entrant storage above), `src/runtime/rt/gc_heap.{h,c}` (the collector), `src/runtime/builtins/gen_runtime.c:23` (`scan_saved[]`). History: one4all `03acf1be` `50a6d07a` `267429d0` `254dedb9` `dd17db1a` `2ede32bd`; SCRIP `e8e728cc` `a8993f46` `aa587c99` `b27e06ee` `d671e68f` `ad613052` `ed0ac777` `79448a32` `261cbbcb` `ad56bb88` `6da13973`. SPITBOL manual v3.7 (uploaded, plain text despite the `.pdf`-looking header — `grep` it directly, don't run it through a PDF extractor): ch.5/`&MAXLNGTH`, the storage-regeneration and external-functions chapters, `COLLECT(i)`.

## Retired names (zeta)

| Old | New / status |
|---|---|
| `src/contracts/` (zeta_storage.{h,c}, descr.h, IR.h, scrip_ir.c, zeta_choices.h) | `src/ir/` (srcreorg move `d4312e86`) |
| `IR.h:156` (old `IR_t` line) | `IR.h:178` |
| `scrip_ir.c:206` (`ir_drive_slot_assign`) | `scrip_ir.c:267`; the function itself is retired-in-spirit — LOWER via `zls_build()` owns the layout now |
| `IR_t.tmp` | Does not exist. Frame offsets are looked up via the parallel `zls[]` table (`zeta_storage.c`), never a node field. |
| `artifacts/asm/fixtures/arbno_alt.s`, `archive/backend/bb_boxes.s` | Do not exist — drop from any reading list |
| `g_proc_arena`, `PROC_FRAME_DEPTH`/`PROC_FRAME_QWORDS` | Zero hits — folded away by the FORTH-cell/region model |
| `bb_callee_frame.cpp` | The `.cpp` is gone; a bare declaration (`bb_callee_frame()`) survives as dead residue in `src/templates/bb/bb_templates.h:168` |
| `rt_zcol_grow` | Zero hits. A related but distinct symbol, `rt_zcol_push`, is live in `bb_match_arbno.cpp` — do not treat the two as the same function |
| `x86_zeta_selfload_*` | `x86_selfload_mode()`, `src/templates/x86/x86_asm.h:485` |
| `scan_stack[]` | `scan_saved[]`, `src/runtime/builtins/gen_runtime.c:23` |
| rZ = r12 / "Ratified = r12" | rZ = RSP, unconditionally (`x86_zr()`, `x86_asm.h:489`) |
| `ZC_ALLOC` axis (`BUMP_INFINITE`/`BUMP_LIFO`/`MALLOC`/`GC`) | Does not exist in `zeta_choices.h`. Superseded by `ZC_STORAGE` (fixed = `CELL_STACK`) and `ZC_ZETA` (fixed = `ZLS2`) |
| `--zeta-storage=`, `--zeta-port=`, `--zeta=` (as live selector flags, or even as refusing stubs) | Deleted outright (commit `6da13973`); an unrecognized `--zeta*` is now an ordinary unknown-option error. Only `--dump-zeta` survives, as a pure inspector |
| "stackless" (as applied to ζ/BB storage) | Retired term. All three zetas live on the machine stack (or its heap-promoted overflow) — the retired law was about a *software* value stack, never about being off the hardware stack |
| Frame choice "by box-kind" / "by language" (SNOBOL4-is-all-stack, Icon-needs-rbp, as independent rules) | Consequences of the 2026-08-27 Frame-Placement Criterion applied to each language's actual boxes, not independent rules in their own right |
## Pattern-Choice Carrier — the ALT/DEFER/ARBNO depth story

Recovered rationale (originally recovered 2026-08-23 by seat05 from pre-strip git history at `git show e25a5daf^:...`, the 200-col/zero-comment style pass that deleted 6,919 comments fleet-wide; re-verified against HEAD as part of this consolidation). Path corrected: `src/contracts/zeta_depth.{c,h}` → **`src/ir/zeta_depth.{c,h}`** (srcreorg). Comment text below is preserved close to verbatim from the pre-strip source, as the original recovery deliberately did — session tags (`sNNN`), witness program names, and measured numbers are load-bearing.

⚠️ **This is a recovered historical record layered with re-verified current status, not a pure live spec.** Function-level grounding re-checked this pass: `sn4_alt_carrier`, `sn4_blob_choice_scan`, `resume_carrier_ok`, `blob_choice_rbp_scan`, `blob_frame_bytes` all confirmed present in `src/emitter/emit.cpp`; `zdp_tier` confirmed present in `src/ir/zeta_depth.{c,h}`. `SCRIP_ALT_CARRIER`/`SCRIP_ALT_SEAM_TIER` killswitches both still referenced in source. Before trusting any claim of "what currently calls what" beyond this, re-run the verification grep — architecture drifts.

### 1. The problem

A SNOBOL4 pattern match suspends and resumes constantly — `ALTERNATE`/`DISJUNCTION` choice points, `ARBNO` retry, `*P` deferred/recursive pattern calls — and every suspension pushes a resume record that a later β (backtrack) port has to read back at the **same stack depth** it was written at. If anything between the push and the read moves the stack (an arm that carves its own scratch space, a nested choice node, a recursive re-entry), the read lands on the wrong bytes — silently wrong on a good day, `rip=0`/SIGSEGV on a bad one. Nearly everything below is a different corner of "how do we know, at compile time, that the depth is still what it was when the record was written."

### 2. The historical arc — read before the per-function sections

**s121–s131: hand-written admission estimators, one per corner.** Each rung convicted a specific unsafe case and wrote a specific predicate to refuse it, then discovered the next corner the previous predicate didn't cover:
- **s121** — board conviction that a bare ALT/DISJUNCTION carrier is unsafe (an arm with interior carves shifts the 32B arm record under a fixed `res` offset). `resume_carrier_ok` refuses it into the seam-walk leaf-generator path.
- **s124** — `resume_carrier_ok`'s tier-1/tier-2 carrier op-filter stated *behaviourally* (RULES.md NO-LANGUAGE-IDENTITY): leaf generators admitted unconditionally, deterministic seam elements admitted by walking a leftward beta chain the element templates already build. Everything else refused — an unlisted op is safe by construction, never a blacklist that can miss a case.
- **s125–s127** — `sn4_alt_carrier`/`sn4_blob_choice_scan`: the ALT-carrier depth story — a stored blob whose body is a single unsealed ALTERNATE with all-leaf arms is admitted because leaf arms carve nothing, so `res`'s fixed `-32` lands exactly on the arm record. Shipped behind `SCRIP_ALT_CARRIER` (default ON since s127, killswitch never deleted, RULES.md rule R-7).
- **s128** — `blob_choice_rbp_scan`/`sn4_choice_rbp_off`: widens admission to the non-leaf single-choice case by moving the arm record off the volatile `rsp` frontier onto the blob's own `rbp` activation frame, making the read depth-immune by construction instead of by leaf-only restriction. Guarded so it never frames a zero-demand blob (§4).
- **s136** — the ZDP lattice (below), meant to retire all of the above into one predicate.
- **s177 (PF-1b)** — the pass-thru-frame law retires most of s128's tightenings (every scratch-cell leaf now homes in the blob's own frame), leaving only the genuinely semantic refusals: multi-record composition (`_nc>1`) and FENCE.
- **s189 (ruling HQ-73)** — `resume_carrier_ok`'s tier 3: a disjunction whose beta re-yields at the same cursor, admitted on a class predicate (choice-node COUNT, not leaf/fence shape — RULES.md NO-PER-OP-FILTER). This is the rung with the exact rationale seat04 needed (§3.3).

**s136: the ZETA-DEPTH (ZDP) lattice — an attempt to unify all of the above.** `zeta_depth.h`'s intent, as recovered: *"Replaces the hand-written admission estimators (leaf_frame_member, blob_choice_rbp_scan, the s128 5-term gate, the s130 8-byte window law, the s131 BAL refuse) with the predicate every one of them was approximating: is the rsp depth at this program point statically known?"* `zdp_tier()` computes one three-way verdict (`ZDP_TIER_STANDING`/`ZDP_TIER_ACTIVATION`/`ZDP_TIER_SPINE`) from a lattice.

A companion methodology warning from the same rung, worth preserving on its own: the first ZDP cut asked the frame-slot registry functions *during planning*, and the diff it produced was not an offset but a **label-counter mismatch** — because the registry functions have emit-time side effects, so merely *observing* the plan perturbed the compiler (the s132 monitor lesson — a verdict on a different program — recurring in a new spot). The fix: keep the registry as the offset authority, let the planner (`zdp_tier`) supply only the tier, touching nothing.

**⛔ Re-verified this pass, still true: the s136 unification is not the live path.** `grep -rn "zdp_tier(" src/` outside `zeta_depth.h`'s own declaration returns nothing — no caller anywhere invokes it. `emit.cpp` still calls `sn4_alt_carrier`, `sn4_blob_choice_scan`, `resume_carrier_ok`, and `blob_choice_rbp_scan` directly. **Both systems still coexist as of this consolidation pass**, unchanged from the original recovery's finding: the s121–s189 estimators are what actually gates codegen; ZDP is a computed-but-unconsumed second opinion. Whether that's deliberate (staged for a future migration) or drift (a stalled migration) is still not resolved by anything available to this pass — if you're about to change either system, grep both call sites fresh before assuming either one is "the" authority.

### 3. Per-function rationale (recovered, preserved close to verbatim)

**3.1 `sn4_alt_carrier()`** (`src/emitter/emit.cpp`) — the ALT-carrier killswitch. TWO READERS, one function, flip in lockstep (the s124 two-reader law): (1) the ARBNO span scan — an unsealed DEFER span member becomes the admitted choice carrier for the `af->PAIR(1)` edge; (2) the blob β-dispatch — a stored blob whose `body_root` is a single unsealed ALTERNATE with all-leaf siblings routes β to the ALT's own interior β. **Residual hazard, opt-in only, stated honestly:** `ARBNO(*p)` where `p` resolves at match time to a refused-carrier blob that γ-suspends retained interior — the admitted `af` edge's second lap can jump through the retained record's cursor field (`rip=0` bomb) where OFF silently wrong-answers; the honest-bomb-over-silent-wrong trade is deliberate (RULES.md) and the class is a named, still-open next rung. `=1` opt-in was later made the **default-ON grant** (s127, Lon in-chat: *"All your choices. I'm with you on this."*) over the full gate table: crosscheck 318 m3 A/B +1/-0 zero regressions, arbnostore ON 10/10 m3+m4, seam 4/4, arbnofence 4/4, named movers 8/8 incl. 150/151 both arms, OFF byte-identity 122/122 by git-stash pristine manifest. Killswitch inverted, never deleted (rule R-7): `SCRIP_ALT_CARRIER=0` restores pre-s127 emission byte-identically.

**3.2 `sn4_blob_choice_scan()`** — the one classification scan, ONE SCAN / TWO READERS (β-dispatch admission + `blob_frame_bytes` widening — never spell the classification twice, the s68/s70 disease). Walks the blob graph counting unsealed choice nodes, flagging FENCE1, verifying every non-choice member is a pure scanner-register leaf (same op-filter as the ARBNO span scan — an unrecognised op refuses by construction). Exit ports (SUCCEED/FAIL terminal pair) are excluded from the count by construction — routing, not matchers, neutral to the depth story.

**3.3 `resume_carrier_ok()`** — the tier-1/2/3 admission predicate. Tier 1 = leaf generators whose beta extends (s121 class), admitted unconditionally. Tier 2 (seam walk) = deterministic elements whose beta is a self-undo fail-through jumping leftward to the previous element's beta — the seam is already built by the element templates; this predicate only stops refusing to enter it. Refused (left at the omega default): DISJUNCTION/ALTERNATE, DEFER, FENCE1, ASSIGN_* capture wrappers, BREAKX, and every unnamed op.

**Tier 3** (s189, ruling HQ-73) — a disjunction whose beta re-yields at the same cursor. Not a seam walk (nothing to walk); one killswitch (`SCRIP_ALT_SEAM_TIER`) at the lattice, all four consumers flip in lockstep. Every `IR_MATCH_ALTERNATE` is admitted on the same question — is the 32B arm record this blob's beta will read still at the depth it was written. **Measured, three witnesses, one field apart:** `probe/passthru/ptw_min_fence_left_altresume` and `ptw_min_fence_alttop` read `nc=1` and cure (oracle-equal match); `ptw_min_alttop_nofence_ctl` reads `nc=2` (an ALT arm carrying a nested ALT, whose own `sub rsp,32` shifts the frontier under the outer record) and SIGSEGVs — `lf=0` and `fn=1` on both cures, so neither leaf_ok nor has_fence separates a cure from the crash; the choice-node COUNT alone does. The second conjunct was earned the same way, one crash later: `crosscheck/patterns/150_pat_star_var_fence_alts_no_arbno` (a standing green whose own header says any future FENCE fix must keep it passing) SIGSEGV'd at `nc=1`, `sd=1` — a right-sealed DEFER's beta *is* the fence-demarcation frame unwind, correct only in its own activation context, so an arm ending in one jumps that unwind against a foreign activation (s177 PF-1b already documented why). `_sd` is computed once at this function's one caller and passed in — one spelling, not re-derived. **The s127/s128 gates are not interchangeable with this tier-3 gate** — their own wider `!_fn && (_lf || cro)` conjuncts would have refused both tier-3 cures (both read `lf=0 fn=1`); the two answer different questions and must not be collapsed into one predicate.

**3.4 `blob_choice_rbp_scan()`/`sn4_choice_rbp_off()`** (s128) — the rbp-resident choice record. Admits exactly the refused-leaf single-choice blob (`_nc==1, !_lf, !_fn`) and only when the blob is already framed by existing law (registry demand or wire-clobber) — the s127 zero-demand conviction stands verbatim: this predicate never frames a zero-demand blob, so no zero-demand-priced caller-territory cell ever meets a frame it wasn't priced against. Record home: `[rbp - blob_frame_bytes() .. +31]`, strictly below every registry slot, preserving 16B parity. Depth-immunity: `res` re-seats rbp from `record[+24]`, `alternate_β` reads `[rbp+cro+8]`, and the winning arm's interior carve — retained on the spine across γ, unwound by its own β chain — can no longer shift the read. **s177 PF-1b later retired most of this widening** (every scratch-cell leaf now homes in the blob's own frame) — but `blob_choice_rbp_scan` remains the frame-sizing/offset authority; §2 above is the current summary of what still gates on it.

**3.5 `blob_frame_bytes()`** — the one authority for the activation carve below the pushed caller rbp: 24 (entry wires + pad, 16B parity) + 16 × (registry candidates in this blob graph); 0 when the blob has neither slot demand nor a wire-clobbering interior (the byte-identical legacy shape — every such blob untouched). Read by the α_body prologue, the CLASS D γ record, `res` landing, and ω whack — all four agree by construction, one scan, four sites. s128 adds +32 for the rbp-resident choice record when `blob_choice_rbp_scan()` admits.

**3.6 `zdp_tier()` and the ZDP lattice** (`src/ir/zeta_depth.{c,h}`, s136) — ONE traversal, one verdict per node, consumed by one accessor. Before this, the tree had five unrelated spellings of "where does this node's storage live": `zone_ref` (leaf cell only), `x86_zop`/`FRQ`/`FR` (rsp-only), and direct `RDQ("rbp",..)` sites scattered across the ζ-family templates. THE THREE ZETAS are the three answers (Lon's register ruling s81): ζ-STANDING → rbp, match-lifetime root; ζ-ACTIVATION-FRAME → rbp, per `*P` defer/re-entrant site; ζ-SPINE → rsp, compile-time-constant FORTH/LIFO. (This s81 naming is the same origin point the SCRIP-top-level section of this doc cites — see there for the naming rationale, and the ζ Local Storage section for the now-unconditional current shape.)

### 4. Warnings — do not re-learn these the hard way

- **s127 conviction:** do not widen the choice-record safety-floor frame by blob shape. The first cut measured five OFF=PASS → ON=SEGV movers (120/131/165/181/182, all rc=139) — a zero-demand blob's interior is priced by the caller's own carve; framing it collided with the frame head's own wire slot. A safety-floor frame for refused-carrier choice blobs needs the pricing to see the frame bytes first.
- **FENCE cannot be re-entered from outside its own activation.** A `seal==1` DEFER's beta *is* the fence-demarcation frame unwind — an arm ending in one that jumps that unwind against a foreign activation is the s177-documented hazard tier 3 (§3.3) had to account for.
- **Residual, opt-in-only hazard in `sn4_alt_carrier`** (§3.1): named as its own next rung, not yet closed as of the source recovered here or this re-verification pass.
- **The s127/s128 gates are not interchangeable with the s189 tier-3 gate** — they answer different questions (§3.3, last sentence).

## Retired names (pattern-choice carrier)

- `src/contracts/zeta_depth.{c,h}` → `src/ir/zeta_depth.{c,h}`
## Passthru — the one crossing law between BB graphs

(Lon 2026-08-20 in-chat, PRIORITY ONE.) *"Get a reliable way to go between BB's. Each BB graph has TWO continuations. Moving between them should be simply a matter of switching these TWO and switching back as they move. … You have EVERY SINGLE BB have a RESULT, so that you are forced to put it somewhere, because when it is needed that will be a problem caught ahead of time. Now some BB results are in REGISTERS."*

⚠️ **This section preserves Lon's crossing LAW close to verbatim (enduring architecture) plus a dated STATUS log (a 2026-08-20 snapshot, ~100+ sessions before this consolidation pass) — treat the two halves differently.** The law is design intent; the status numbers below are a historical measurement and were not re-run this pass. Path corrected throughout: `src/contracts/descr.h` → **`src/ir/descr.h`** (confirmed live, `struct DESCR_t` at `:52`, closes `:67`, matching this doc's claimed 16-byte layout exactly — `v` DTYPE_t 4B @0, `slen` uint32 4B @4, payload union 8B @8, no padding hole). ⚠️ A second `descr.h` also now exists at `src/runtime/core/descr.h`, not diffed against the `src/ir/` copy this pass — worth a follow-up to confirm which is canonical for this doc's claims before treating them as interchangeable.

### The law (amended per Lon 2026-08-20 in-chat, verbatim in substance)

**0. Partition by activation.** The unit of pass-thru is the ACTIVATION — a closed set with exactly two exits (γ succeed, ω concede). Every seam question is asked and answered at an activation boundary, never mid-box.

**0a. The push-pair move.** At a crossing, push γ and ω on the stack as return locations; the exit chooses by a pop/ret combo (RETURN/FRETURN). **⛔ Ruled: the stack pair wins, r10/r11 are freed.** The pair is stored once, at RBP (`[rbp+8]=γ, [rbp+16]=ω`, pushed by the caller before entry); exits are the RETURN/FRETURN adjust/ret trick (γ: `mov rsp,rbp; pop rbp; ret` + landing owns `add rsp,8`; ω: `mov rsp,rbp; pop rbp; add rsp,8; ret`); γ-suspend keeps the frame and pushes the retained rbp as the one-slot β-handle; β re-entry = `mov rbp,[rsp]; jmp [rbp-16]`. Rationale: (1) the pair is activation state and the stack is where activation state lives — pushing IS the banking; (2) registers do not survive interior C calls (the rtccb veneer tax) while stack slots need no protection; (3) exits get cheaper; (4) the machine is register-starved.
- ⛔ **FACT (Lon 2026-09-02, in-chat to ceo): `r10` = statement number, `r11` = BB node id** (`x86_asm.h` emits `mov r11, nid` at box entry, today under the diag-regs arm). **And (same day): `r13`, `r14`, `r15` — the SNOBOL4/Icon string-scanning registers — are granted to Prolog for its internal transmission: ceo assigned `r13` = B (youngest choice frame), `r14` = TR (binding-log cursor), `r15` = exception ball or 0; saved/restored as a triple at polyglot language boundaries (`ARCH-PROLOG-BYRD-BOX-TRANSLATION.md`, top).** "Freed" above means freed from the continuation pair, not free for a new design to claim: any new wire (the Prolog B pointer, the exception ball, `ARCH-PROLOG-BYRD-BOX-TRANSLATION.md`) takes a register from the plane in `src/ir/zeta_choices.h` or a frame slot, never `r10`/`r11`.

**0a′. Two exit forms, not one — RETIRE vs SUSPEND.** *"The CALLER will do PUSH F; PUSH S... if you are yielding, i.e. suspending, it is different. Then you just load the address and JUMP."* Opposite frame lifetimes, cannot share one exit: **RETURN (γ, done)** — frame retires, restore depth, `ret` (pops S), landing owns `add rsp,8`. **FRETURN (ω, done)** — retires, restore depth, `add rsp,8; ret` (pops F). **γ-SUSPEND (yield)** — frame stays alive, load address and `jmp`; pair and frame both stay put because β must still find them. **β re-entry** = `mov rbp,[rsp]; jmp [rbp-16]`. Measured (s195): the tree at that time emitted ONE form for both, with no depth restoration — `SCRIP_WIRE_STACK=1` measured 1/82 on the class 0-9 grid (both modes), default arm 82/82. The discrimination precedent already existed in one box — confirmed this pass at **`src/templates/bb/bb_call_proc_staged.cpp:76,252`** (`AB_OFF_ERSP` store/restore: `mov [rsp+BASE+AB_OFF_ERSP], rax` / `mov rsp, [rsi+AB_OFF_ERSP]`) — corrected citation: the original doc pointed to `bb_define.cpp:250-255`, which this pass could not confirm carries the same mechanism; `bb_call_proc_staged.cpp` is where it was actually found. See `FINDING-2026-08-20-s195-the-stack-pair-was-never-run-and-one-exit-form-cannot-serve-return-and-yield.md`.

**0b. RBP correct at β, every box.** Save/restore logic ties to the γ/ω transitions; a box whose β runs with a stale RBP is a defect regardless of whether the run happens to survive.

**0c. The three-tier escalation ladder** (storage is a ladder, never a choice): (1) **RSP** — fixed offsets computed from position in the operand-box sequence. (2) An operator BB reaching past an unknown number/type of BBs cannot use RSP — escalate to a slot in the **RBP activation frame**. (3) When both fail, the slot allocates at the **STANDING (base) frame** with one indirection — the standing pointer rides down every frame precisely so this tier always exists; `S ? P`'s standing activation is special, its pointer serves MATCH_BEGIN housekeeping. (This ladder is the same ζ-SPINE/ζ-ACTIVATION-FRAME/ζ-STANDING shape documented in full in the ζ Local Storage section — this is the crossing-law motivation for it.)

**0d. No-deny law.** A failure case is never denied — no admission filter, no shape refusal, no "unsupported" arm. Stop the world, minimize, fix it.

**1. Two continuations, one discipline.** Every BB graph's external contract is the pair {γ-continuation, ω-continuation}. Every crossing = bank the caller's pair, install the callee-relative pair, run; the callee's γ/ω restore the banked pair. Nothing else may carry cross-graph linkage.

**2. The pair is activation state, not a call artifact.** Graphs suspend (γ) and are re-entered (β); whatever holds the suspension holds the banked pair, and β re-entry reinstalls it. Existence proof in-tree: the PAT$ blob head (`blob_frame_bytes`: saved rbp @+0, γ wire r10 @-8, ω wire r11 @-16).

**3/3a. The RESULT law, stabilization form.** Every BB allocates a RESULT slot uniformly — register-resident results included — temporary until stabilized: slot number = box index, carve = n_boxes × granule, so offset math has no per-box cases and no candidacy. A register result may stay cached in its register; the cell exists regardless, so a consumer can never find no home. Frame bloat is accepted scaffolding; cells un-allocate box-by-box once the ladder stabilizes, each with its own measurement. Every BB has a RESULT and a DECLARED HOME (register or lattice-named cell), declared at compile time — the s174 conviction (a needle read resolving to caller territory inside an ALT arm) was a result whose home was an assumption. Enforcement joins the ZDP lattice (`src/ir/zeta_depth.c` — see the Pattern-Choice Carrier section) and the ZSM/canary instruments, which check declared-vs-actual.

### The four protocols in the tree (the disease, as measured 2026-08-20)

1. **Blob crossing** — conformant (banks the pair in its head; the model).
2. **Pushed-pair landing** (`bb_call_proc_staged` slim/legacy: `[rsp+0]=γ [rsp+8]=ω`) — a historical root-cause class.
3. **DTP record road** (DEFER β = `jmp qword ptr [rsp]`) — record-held continuation.
4. **TINY shim** — a third call shape with its own admission/exits.

Not re-audited this pass whether all four still coexist unreconciled — flag for a follow-up sweep before assuming this list is exhaustive today.

### The ladder — nine classes

Every class exercised through both `*PATTERN_var` and `PATTERN_func()` roads:

| class | boxes | state character |
|---|---|---|
| (0) | POS · RPOS · LITERAL · LEN · ANY · NOTANY | zero-local; result = r14d; β reverses arithmetically or is a pure predicate |
| (1) | TAB · RTAB · REM · BREAK · SPAN | one 4-8B cell (entry-cursor β-restore + SPAN's loop counter); semantic minimum ~0 once the β convention is fixed |
| (2) | ARB · BAL · BREAKX | genuine retry state — extending-β generators |
| (3) | ALT · ARBNO | choice/iteration records (32B rsp record · 16B registry slot per activation) |
| (4) | CAPTURE (SAVE/COND/IMM) | the RESULT-law hot case: result lands in a variable's cell, not a register |
| (5) | FENCE0 · FENCE1 | cut semantics across graphs (0B · 16B watermark) |
| (6) | EVAL | runtime fragment compile + crossing |
| (7) | CODE | runtime statement-graph compile + crossing |
| (8) | MEGA | ARBNO/DEFER/EVAL/CODE stacked combinations — the beauty grammar shape |
| (9) | BEAUTY-CONJUNCTION | class-8 stacks embedded in context — failure modes appearing only in conjunction, never in any ingredient alone |

⛔ **PATH CORRECTED 2026-08-28 (seat08, probe-consolidate-passthru total conversion):** Witness home is now `corpus/tests/snobol4/probe/passthru.{sno,ref}` (corpus-suites-consolidation suite format) — the loose `corpus/probe/passthru/pt<class>_*.sno` files this line used to name are gone, `git rm`'d the same commit as the conversion. Read a witness with `python3 SCRIP/scripts/corpus_suite_harness.py extract passthru.sno passthru.ref <name> <out.sno> --out-ref <out.ref>` (or `names` to enumerate); never assume the old loose path. Runner: `SCRIP/scripts/board_passthru_combo.sh` — re-pointed to the suite in the same commit (extracts every entry via the harness, then runs the SAME per-row + per-class rollup, proper m4 lane logic as before, unchanged; before/after board proven byte-identical, both modes). 5 witnesses (`ptw_min_arbno_alt_fence_L1`, `ptw_min_defer2_hang`, `ptw_min_rseal_arbno`, `ptw_min_rseal_commands`, `ptw_min_rseal_unsealed_ctl`) are pre-existing, documented reds and convert as XFAIL entries (harness's new xfail/xpass bucketing) so they stay visibly red on this board without registering as a regression on test_corpus_snobol4.sh's aggregate gate. Gate: the class's whole witness family oracle-identical both modes before the next class opens (unchanged).

### The RESULT grid (measured 2026-08-20, HQ — historical baseline, not re-measured this pass)

`r13` = subject base · `r15d` = subject length · **`r14d` = cursor delta, the result register of the matcher family** · `r10`/`r11` = the two continuations (superseded by the stack-pair ruling in §0a above — treat as the pre-ruling register names, not current allocation). POS/RPOS/LIT/LEN/ANY/NOTANY: 0 locals, result r14d. TAB/RTAB/REM/BREAK: 4B entry-cursor β-restore only. SPAN(lit): 8B. SPAN(*expr): 16B (needle pair, ABI forces the fill call's out-params into memory). BREAKX 8B / ARB 8B / BAL 12B: genuine retry state. ARBNO 16B slot; ALT 32B rsp record; CAPTURE 16B slot; FENCE0 0; FENCE1 16B watermark; DEFER = the crossing state itself (DTP + resume + banked pair).

**The β convention decision:** the machine mixed two β disciplines — relative boxes reverse r14 arithmetically, absolute movers restore from their cell — and a non-restoring TAB β chaining into a reversing LIT β reverses from the wrong value. The fixed law: every β re-derives r14 from its own knowledge, absolutely — then the 4B cells vanish and class 1 collapses into class 0. (Landed/open status not re-verified this pass.)

### Instruments

- **ZSM (ζ state machine)** — the checking tool of record, audited against known-good/known-bad witnesses before being trusted. Must compare the EXPECTED offset of a box's RESULT to the ACTUAL offset at runtime — declared-vs-actual is what catches this class; existence-tracking alone is not enough (a broken road can emit zero events).
- **BB 4-port tracing** — every transition logged FROM (inside which α/β block) → TO (exact α/β label) → VIA (γ or ω). All four ports, no sampling.
- **STACK DOPING** — seed the stack with recognizable markers so a wrong landing measures how far off it is, instead of "it went somewhere unknown."

### The namespace law

*"DEFER *P2 goes through GVA cell — that is NAMESPACE POLLUTION."* The defer road may touch a GVA cell only for a real, mutable USER variable, by INDEX — late binding is what `*` means. Pollution that dies: (1) match-time string-name lookups (name→cell resolves at compile); (2) synthetic names (`EXPR$N`, `PAT$N`, `PAT$n$V<i>`) interned as real variables beside user names — they become anonymous handles (DTP/graph refs), never named cells; (3) constant-paired defers touch no cell — compile-time stitch. (4) **DEFER's locals are frame slots** — `BB_DEFER` stores its resolved DTP handle, entry cursor, and suspension state as locals in the enclosing activation's RBP frame; GVA touched once at α, by index, only for a real mutable user target; β and the write-once cache read the local. `g_sno_defer_cells` was ruled to die under this law (per-site, not per-activation — two live activations of one defer site would share a cell, broken under recursion by construction). **⚠ Not confirmed landed this pass** — `grep g_sno_defer_cells src/` returns 11 hits tree-wide as of this consolidation, so either the removal hasn't happened yet or those hits are non-live (comments/tests) — worth a direct follow-up rather than assuming the ruling is implemented.

### Compile-time stitching — the subgraph partition

A whole-graph traversal partitions the pattern BBs into subgraphs keyed by `*P`/`P()` paired with the constant definition each resolves to. Constant chains stitch at compile time, not runtime — e.g. a whole calculator expression folds to one pattern by traversing the references. The fold can never yield a known depth: at the bottom of a purely-constant pattern sits one `'(' *X ')'` defer, the one unknown inside the known whole — but the bottom `*X`'s size IS the whole pattern's size, so every offset needed above it is known, and the last `*X` is inconsequential. Glue survives only at that bottom defer.

### Provenance stamping — why the byte cannot go in the DESCR, and where it must go instead

The idea: stamp the producing BB's node ID into the DESCR, so a value says who made it. The governing constraint: *"at β you want to check something ... you cannot depend on RBP to check RBP. Chicken-egg."* A check whose witness is reached through the register under test is not a check — the witness must be out of band. (ZSM already obeys this: the node id arrives as an immediate in the emitted event call, the expected frame lives in a side table keyed by that id.)

Three candidate homes for a value-borne stamp: **(1) high bits of `v`** — re-opened: `DT_NOTSTR_MASK` is a constant, not a hard constraint; narrowing it from `0xFFFFFFFD` to `0x0000FFFD` frees bits 16-31 of `v` (exactly the 16 bits the ZSM already hashes a node id to, `node & 65535`). Confirmed this pass: `DT_NOTSTR_MASK` has exactly **9 references tree-wide** (matches the doc's own count precisely) — 7 inside `descr.h`, 2 RTX asm readers (`rtx_match.S`, `rtx_arith.S`) that inherit the narrowing by macro name. Real cost: the joint-tag forms (`and eax,ecx; cmp eax,DT_I`) compare the full 32 bits and would need to become 16-bit operand forms at ~20 candidate template-only sites; the bit-test forms are unaffected. **(2) `slen`** — closed, fully used for strings and overloaded as a DT_N discriminator. **(3) payload union** — closed, holds pointers.

**Remaining real item — value identity:** `runtime/values.c`'s fallback arm compares descriptors with a whole-struct `memcmp`; a provenance byte would make two semantically-equal values compare unequal. Census at time of writing: exactly 2 `memcmp` sites touch a DESCR tree-wide, no table-key path hashes the struct wholesale — the fix is a one-function explicit-field compare with `v` masked to its low half, not a systemic sweep. (Not re-counted this pass.)

**⭐ The ruling that followed: stamp the CELL, not the VALUE.** A ζ cell is compiler-private — never compared, hashed, or GC-identity-checked — and its size/offsets are computed by one authority (`zdp`/`zw_carve_k`), so widening it under a killswitch is a planner change, not a 129-template edit. Write `{magic, nid16, op8, depth}` at α-carve; at every operand read, compare the header against the compile-time immediate the consumer already knows. This satisfies the chicken-egg constraint exactly — the consumer derefs the address it was already going to use, and a wrong address shows up as a magic/nid mismatch, no correct RBP required for the check itself to be valid. It also catches what a value-borne stamp structurally cannot: reading something that isn't a descriptor at all (a banked γ wire read as a value, for instance).

What a value-borne stamp would still buy, kept for the record: provenance that survives escape (a value copied into a GVA cell/table/array/stored pattern outlives its cell) — cell doping answers PLACEMENT, value stamping answers PROVENANCE across time. If the time axis is ever needed: do not carve into the 16 bytes — a DEBUG-WIDENED 24-byte DESCR behind a build flag is mechanically reachable (the 16-byte stride is baked into emitted code but computed by the emitter everywhere, so a compile-time widening recompiles and re-emits cleanly).

### Status (2026-08-20, HQ — a dated snapshot, ~100+ sessions before this consolidation; re-verify before quoting as current)

- **s195 (Opus 5 1M, pristine, HQ-27 satisfied):** the witness plan was complete at 82/82 rows (classes 0-9 × {f,b} × {var,fn} × {2,3} + 2 class-7 extras), both modes, on the default arm. Arming law 0b (`SCRIP_ZSM=1 SCRIP_ZSM_ALL=1`) turned 3 of those greens fatal (m3 79/82, m4 80/82) — all three backtrack rows, each preceded by an `ω·`. Two instrument caveats were owed before quoting these as defects (a skew-80 vs. ZSM shim's own 10-push depth ambiguity, and a missing whack-owner exemption on the β arm). `SCRIP_WIRE_STACK=1` measured 1/82 both modes. r10/r11 census: 232 sites, 79 pure save-restore tax, 30 wire-carry, 70 runtime asm, ~53 RTCC/decls.
- **s177 (HQ, Fable):** the s176 "operand-home" wall and most of the s175 census were the PT-2 dead-build elision — the lowerer suppressed the MKPAT chain + GVA store + blob graph on a census blind to `*X` consumers inside kept patprocs and MKEXPR fragments. Elision deleted; passthru 10/17 → 16/17 both modes, corpus +1 both modes, zero regressions. Residual honest red at that time: bare `MID = *INNER` class (`DT_P` reaches `c_rt_defer_close`, which has no pattern arm).

**This pass could not confirm whether the above is still the live board state, whether `SCRIP_ZSM`/`SCRIP_WIRE_STACK` gates are still wired the same way (a quick grep found only one combined hit for both names, fewer than this section's description implies — worth a direct follow-up rather than trusting the count either way), or how many of the four crossing protocols (§ above) have since been unified. Whoever next touches pass-thru work should re-run `board_passthru_combo.sh` before trusting any number on this page.**

## Retired names (passthru)

- `src/contracts/descr.h` → `src/ir/descr.h` (a second copy exists at `src/runtime/core/descr.h`, not reconciled this pass)
- `bb_define.cpp:250-255` (AB_OFF_ERSP discrimination precedent) → confirmed instead at `src/templates/bb/bb_call_proc_staged.cpp:76,252`; the original citation could not be confirmed
## SCRIP Frontend + Execution Modes

Mostly accurate, verified against current HEAD; corrections below are small and path-only — the substance (two execution modes, the emit-time-only isolation invariant, the shared-substrate symbol table) holds up.

**Frontend.** Produces the shared AST (`tree_t`/`STMT_t`) — confirmed at `src/ir/ast.h` (not `src/include/ast.h`; matches the IR-doc audit's same correction, same srcreorg move).

**Execution modes — unchanged, verified:** `--run` (mode 3) and `--compile` (mode 4) both route through `src/emitter/emit.cpp` (`emit_drive` + dispatch — see § Emitter above); `GOAL-MODE34-IDENTICAL.md` exists and is the live authority. `optimizer_run(g)` sits between LOWER and the emitter, on by default, `SCRIP_OPT=0` emergency-only per RULES.md.

**Isolation invariant** — accurate and independently confirmed this pass: `emit_drive` walks the IR graph via one `switch (nd->op)`, at emit time only; runtime carries zero per-opcode C dispatch. ⛔ Its "Check GOAL-PROLOG-BB.md directly" pointer is dead — that file does not exist; the live file is `GOAL-PROLOG-100.md`.

**Shared substrate table — re-verified, essentially correct.** `INVOKE_fn`/`APPLY_fn` live in `src/runtime/core/core.{c,h}` (+ `by_name_dispatch.c` for `APPLY_fn`). `NV_GET_fn`/`NV_SET_fn` are exactly as billed — genuinely load-bearing, referenced from driver, optimizer, a half-dozen `bb/` templates, and both `.S` runtime assembly files. `exec_stmt`/`bb_build` confirmed in `src/runtime/core/stmt_exec.c` (plus driver call sites; `bb_build` also appears in `emit.cpp` itself — a citation the doc could add but isn't wrong for omitting). `eval_node` → `src/runtime/runtime_eval.c` only, as stated. `coerce.c` → `src/runtime/core/coerce.c`, confirmed. `sm_lower` → confirmed vestigial, sole hit `src/driver/scrip_sm.c`. **Dead-symbol list independently reconfirmed, all zero hits:** `bb_broker`, `bb_boxes`, `sm_interp_run` (also independently confirmed absent by the CEO's x86/Prolog audit FINDING), `sm_jit_run`, `SM_sequence_t`, `g_jit_prog`.

**SNOBOL4 native pattern matching pointer:** `ARCH-LANGUAGES.md` exists (reference good) but cites `GOAL-SNOBOL4-BB.md`, which is dead — the live consolidated file is `GOAL-SNOBOL4-100.md`.

**The "three ζ storage tiers" section (s77–s81 naming-of-record) — historically important, mechanically stale, kept short here on purpose.** This is the ORIGIN of the current ζ-STANDING / ζ-ACTIVATION-FRAME / ζ-SPINE naming (compare RULES.md's ICON ladder: "ζ-SPINE (RSP) → ζ-ACTIVATION-FRAME (RBP) → root/standing activation frame") — worth preserving as naming provenance: **why** these three names were chosen (motion is the split axis: never-moves / framed-but-relocatable / slides), and the two rejected names on record (`ζ-MARK` — collides with the banked-quad "the MARK"; `ζ-ANCHOR` — collides with SPITBOL's `&ANCHOR` keyword). The doc's own mechanism snapshot ("Census at s78 HEAD: 9 total push rbp sites...") is a stale point-in-time count from a much earlier, SNOBOL4-pattern-scoped, still-being-earned version of this design, superseded by the current unconditional three-zeta reality (RULES.md § ZETA HAS NO MODES) and by the full current mechanism, which belongs in — and this pass defers to — the ζ Local Storage section of ARCH-ENGINE.md. Do not duplicate the mechanism here; keep only the naming rationale, cross-reference the rest.

## Mode-4 Link Mode — PIE is correct; `-no-pie` is REFUSED (ruling)

RULING on row `m4-pie-vs-no-pie-changes-behaviour-not-just-signal` (rank 1, minted by hq_C 2026-08-28, from seat03's `corpus-suite-harness-compile-m4-missing-no-pie`). Ruled by seat10, 2026-08-28, on a `make pristine` tree (`adda4391`), RT_OPT `-O0`.

**Ruling: mode-4 (`--compile`) binaries link PIE — the current default, no extra flag. `-no-pie` must NOT be added to `compile_m4()` (`SCRIP/scripts/corpus_suite_harness.py`) or `compile_mode4()` (`SCRIP/scripts/test_corpus_snobol4.sh`).** Both already default to PIE; this ruling is a no-op for behavior and replaces their "UNRESOLVED, do not add `-no-pie`" banners with the finding below.

**Why — from the faulting address, not the absolute-address premise (the method the row demanded):**

Witnesses `fz_red_m2a_fence_cap_gen` and `fz_segv_10` (`corpus/tests/snobol4/probe/fuzz.sno:21-22`) are **not** crash-expected — `.ref` says `match` for both. Extracted standalone, `scrip --compile` → `gcc -c` → linked twice off the identical `.o` (PIE default vs `+ -no-pie`):

| witness | PIE | `-no-pie` |
|---|---|---|
| `fz_red_m2a_fence_cap_gen` | `match`, rc=0 — 20/20 | SIGSEGV rc=139 — 20/20 |
| `fz_segv_10` | `match`, rc=0 — 20/20 | SIGSEGV rc=139 — 20/20 |

N=20 per witness per arm — fully deterministic both ways at this N (the row's own caution that 3 runs can't separate "always" from "11-of-12" is answered: this pair is "always").

gdb on both `-no-pie` binaries: both fault on the first instruction of a `*`-indirect pattern continuation (`n1_match_rem_bx` / `n1_match_fence1_bx`) that touches `(%rsp)`. **RSP is `0x0` at fault** (`fz_segv_10`), or `0xfffffffffffffff0` — `0x0 - 0x10` wrapped, from the callee's own `sub $0x10,%rsp` prologue — for `fz_red_m2a_fence_cap_gen`. Breakpointing the **identical function by symbol** (ASLR-safe) on the **PIE** binary instead: RSP on entry is `0x7fffffffe168` / `0x7fffffffe188` — an ordinary valid thread-stack address — and the program runs to completion, breakpoint hit exactly once (clean match, no backtrack re-entry).

This is the row's branch (b), not (a). `0x0` is not "a plausible absolute address the codegen emitted" that PIE's layout merely leaves mapped by luck — it is the signature of a value that was never populated, and it is wrong **only** under `-no-pie`, at the identical program point, on the identical object file. Zero does not depend on load address: if this were a genuine wild-pointer defect baked into the codegen (the sibling row's shape, see below), the same corruption would reach RSP under PIE too — measurably, it does not. So mode-4's `*`-indirect pattern-application path has a real, currently-undiagnosed dependency on being linked PIE (plausibly somewhere in how control returns into the pattern continuation through `libscrip_rt.so`, itself always position-independent as a `.so` — not chased further, out of this row's scope). This also directly refutes the flag's original justification: the claim was that PIE breaks mode-4's embedded absolute addresses (the `.rodata → FN__PAT$0` pattern-descriptor `.quad` the linker's own `creating DT_TEXTREL in a PIE` warning names); empirically PIE is the *passing* arm on exactly this mechanism, backwards from the prediction.

**Cross-check, sibling row `pascal-m4-intermittent-segv-layout-sensitive` (seat06, in progress at ruling time):** Pascal's witnesses (`boolmix`/`boolchain`/`pb30`) are non-deterministic **in both link modes**, and `-no-pie` there only lowers the crash rate without curing it. Different defect shape (flaky-both-ways vs. this row's deterministic one-arm-only pair) but the same policy conclusion: `-no-pie` is not a free stabilizer, and for at least one shape (this row's) it turns a correct program into a guaranteed crash. Two independent witness classes agree PIE is the safer default.

**Gate:** `test_corpus_snobol4.sh` on the ruling tree (`adda4391`, `make pristine`): `mode-3 PASS=1299 FAIL=0` · `mode-4 PASS=1299 FAIL=0 SKIP=0` (1299 total, MISSING=0).

**Control arm (SHARED-NODE VERDICT SCOPE):** Icon does **not** route mode-4 grading through `compile_m4()`/`compile_mode4()` — its pinned watermark comes from the independent `test_icon_x64_all_rungs.sh`, which hardcodes its own `-no-pie` link and is structurally untouched by this ruling (no functional change lands in the shared functions either way). Measured once for the record, same tree (`adda4391`, clean): `bash scripts/test_icon_x64_all_rungs.sh` → `Icon --compile: PASS=249 FAIL=18 XFAIL=30 TOTAL=297`, m4 dirt `EMIT=2 LINK=0 CRASH=8 TIMEOUT=0 OUTPUT=8`. One run, not the two-agreeing-runs bar RULES.md sets for a *mover* — this is a control-arm citation for a change that doesn't touch Icon's code path, not a claimed movement. ⛔ **Open item, flagged not fixed:** this script's own `-no-pie` is now a live suspect given this row's finding that `-no-pie` can corrupt a `*`-indirect continuation's RSP — Icon's generator/co-expression path rides the same ζ-SPINE-on-RSP mechanism (RULES.md § THREE ZETAS). Out of scope here (this row's witnesses are SNOBOL4-only); routed to hq_C.

## SILLY (Silly SNOBOL4)

⛔ **Wrong home directory, one-line fix, load-bearing for anyone who goes looking.** The doc says SILLY "Lives in `SCRIP/src/silly/`" — that path does not exist (`ls src/silly/` → No such file or directory). The real location, confirmed and matching CLAUDE.md's own Workspace map ("`bootstrap/` ... and `SILLY/` ... live as top-level side trees" of SCRIP): **`SCRIP/SILLY/`** — top-level, capitalized, a sibling of `src/`, not nested inside it. Contents confirmed (`arena.c/h`, `argval.c/h`, `arith.c/h`, `arrays.c/h`, `asgn.c/h`, `cmpile.c/h`, `data.c/h`, `define.c/h`, `errors.c/h`, `expr.c/h`, `extern.c/h`, `forwrd.c/h`, `func.c/h`, `interp.c/h`, `io.c/h`, `main.c`, `Makefile`, `nmd.c/h`, `patval.c/h`, `platform.c`, `pred.c/h`, `scan.c`, ...) — SIL-abbreviated file names, consistent with "ground-up faithful C rewrite" of the SIL source. Cost if trusted: a session pointed at `src/silly/` gets a plain directory-not-found and no clue the tree moved one level up and out.

⛔ **Source-oracle paths are HQ-only absolutes, unreachable from this seat — same drift class CLAUDE.md already names for other assets.** `/home/claude/work/snobol4-2.3.3/{v311.sil,snobol4.c}` and `/home/claude/work/spitbol-docs-master/` both fail to resolve here (`ls` → No such file or directory) — `/home/claude` is HQ's root, not this sibling-root's (`/home/claude12`), exactly the "older docs hardcode `/home/claude`" pattern CLAUDE.md's Workspace map already flags for other oracle assets (`x64/`). Unlike `x64/`, this pass found **no confirmed shared-asset fallback or env var** for the SILLY source oracles (no `S4E_ASSETS`-equivalent verified) — leave this as an open item rather than inventing a resolution mechanism; a follow-up should either confirm one exists or get a ruling on where these three reference files are meant to live for a non-HQ seat.

Everything else — the 32-bit-on-64-bit platform model (`int_t=int32_t`, `real_t=float`, one 128MB `mmap` arena, `A2P`/`P2A`), zero-goto control-flow discipline, the three-way `v311.sil`/`snobol4.c`/`src/silly/sil_*.c` diff method (note: the doc's own internal path here — `src/silly/sil_*.c` — needs the same `SCRIP/SILLY/` fix), the naming-convention table, the CSNOBOL4-not-SPITBOL oracle-exception rule, and the explicitly-unimplemented BLOCKS section — is prose/methodology, not a source-path claim, and this pass found nothing to contradict it. Move as-is aside from the two path fixes above.

## Per-Box Profiling (cyc-proxy histogram)

Verified, essentially unchanged — this doc describes a measurement methodology rather than internal source paths, so it's the least drift-prone of the four. Confirmed live: `scripts/profile_box_histogram.sh` (the tool itself) and `scripts/bench_sno_match4.sh` (the same-moment interleaved A/B protocol it calls out for proving a win). No claim in this file was found to be false; move as-is. The cyc-proxy formula, the two LAWS (Ir lies on rep-string ops; absolute ms drifts with host load), the callgrind format traps, and the reading-the-table guidance are all tool-behavior descriptions this pass had no evidence against — flagging that as "not falsified" rather than "positively re-verified line-by-line," since re-deriving the callgrind mechanics from scratch was out of scope for this pass.

## Retired names (small cluster)

| Old | New / status |
|---|---|
| `emit_core.c`, `emit_bb.c`, `emit_sm.c`, `sm_jit_interp.c` | retired — consolidated into `src/emitter/emit.cpp` + `emit.h` (+ `emit_str.cpp`, `sil_macros.h`) |
| `IS_TEXT` / `IS_BIN` / `IS_WIRED` / `IS_BROKERED` | retired — TEXT/BINARY branching is `g_medium` (`bb_medium_t`) tested via `MEDIUM_BINARY`/`MEDIUM_TEXT` |
| `g_emit_mode`, `g_emit_out` | zero hits — believed retired; not re-derived what (if anything) replaced them beyond `g_medium` |
| `emit_str.h`, `sm_template_common.h`, `strtab_label_s` | zero hits — retired or renamed; not re-derived |
| `GOAL-PURE-TEMPLATES.md` | does not exist as a file — likely folded into a `GOAL-*-100.md` consolidation; not confirmed which |
| `src/include/ast.h` | → `src/ir/ast.h` |
| `GOAL-PROLOG-BB.md` | → `GOAL-PROLOG-100.md` |
| `GOAL-SNOBOL4-BB.md` | → `GOAL-SNOBOL4-100.md` |
| `GOAL-RBP-EARN.md` | retired — content resolves into `GOAL-SNOBOL4-100.md` (confirmed: that file references RBP-EARN) |
| `SCRIP/src/silly/` | → `SCRIP/SILLY/` (top-level, capitalized, sibling of `src/`) |
| `/home/claude/work/snobol4-2.3.3/`, `/home/claude/work/spitbol-docs-master/` | HQ-only paths, unresolved on non-HQ seats — open item, no fallback confirmed |
---

## RETIRED NAMES

Master path index for everything the nine source docs (`ARCH-IR.md`, `ARCH-x86.md`, `ARCH-EMITTER.md`, `ARCH-ZETA-LOCAL-STORAGE.md`, `ARCH-PATTERN-CHOICE-CARRIER.md`, `ARCH-PASSTHRU.md`, `ARCH-SCRIP.md`, `ARCH-SILLY.md`, `ARCH-PROFILE-BOX-HISTOGRAM.md`) cited that has since moved, renamed, or been deleted — for `grep`-ability from a stale reference anywhere else in the tree. Symbol-level renames not listed here (there are many more) live in each section's own "Retired names" subsection above; this table is the directory/file layer, the one most likely to break an external cross-reference.

**This file itself.** All nine docs above → `ARCH-ENGINE.md` (this file). They are deleted, not archived — their content moved here per-section (see each section's own attribution note); nothing in them was true-and-uncaptured.

**Directory moves (the 2026-08-27 srcreorg, still landing in places as of this pass):**

| Old | New |
|---|---|
| `src/contracts/` | `src/ir/` (commit `d4312e86`) — `ast.h`, `SM.h`, `stage2.h`, `IR.h`, `descr.h`, `zeta_storage.{h,c}`, `zeta_choices.h`, `zeta_depth.{h,c}`, `scrip_ir.c`, `bb_pool.{c,h}`, `bb_program.h` all confirmed here |
| `src/include/` | folded into `src/ir/` (same move) |
| `src/lower/` (IR/SM/stage2-owning pieces) | `src/ir/`; the lowering logic proper (`lower_*.c`) stays under `src/lower/` |
| `src/runtime/x86/` | does not exist — contents dispersed (`bb_box.h` → `src/ir/`; `sm_prog.h`/`sm_interp.c`/`bb_broker.c` — no confirmed live replacement located, do not cite) |
| `src/runtime/interp/` (`icn_runtime.h`, `pl_runtime.h`) | `src/runtime/builtins/resolution.{c,h}` (+ `gen_runtime.h` for Icon generator support) |
| `src/templates/*.cpp` (flat, was 161 files as of the 2026-07 prune) | `src/templates/bb/` (134 Byrd-box templates) · `src/templates/xa/` (17 cross-cutting wrapper templates) · `src/templates/x86/` (`x86_asm.h`, `x86_arg_roles.h`) — re-gridded 2026-08-27 08:52, zero top-level `.cpp` remain; re-count with `find src/templates -name '*.cpp' \| wc -l` rather than trust any fixed number, this tree has re-gridded twice |
| `BB_templates/`, `XA_templates/`, `SM_templates/` (pre-2026-07 names) | absorbed into the above; never existed as of this pass |
| `emit_core.c/.h`, `emit_bb.c`, `emit_sm.c`, `emit_drive.c`, `sm_dispatch.c`, `bb_regs.h`, `emit_defs.h`, `sm_jit_interp.c` (the EC-series split) | `src/emitter/emit.cpp` + `emit.h` (one driver; `emit_str.cpp` and `sil_macros.h` survive unmerged) |
| `bb_flat.c` | split: `src/templates/bb/bb_glue_flat.cpp` (glues BB bodies) + `src/templates/xa/xa_flat.cpp` (glob prologue/epilogue, ζ-carve, anchor) |
| `SCRIP/archive/frontend/prolog/prolog_emit.c` | `one4all/archive/...` |
| `SCRIP/src/silly/` | `SCRIP/SILLY/` (top-level, capitalized, sibling of `src/`, not nested inside it) |
| `GOAL-SNOBOL4-BB.md`, `GOAL-PROLOG-BB.md`, `GOAL-ICON-BB.md` | `GOAL-SNOBOL4-100.md`, `GOAL-PROLOG-100.md`, `GOAL-ICON-100.md` respectively |
| `GOAL-RBP-EARN.md` | retired into `GOAL-SNOBOL4-100.md` |

**Load-bearing model corrections (not renames — claims that were simply wrong, most costly if trusted literally):**

- **The ζ frame is not `r12`.** No prior doc's `mov r12,rdi` / `[r12+off]` ABI exists in source. ζ-SPINE is RSP-relative by default (`sub rsp,K` carve, `x86_zref`/`x86_zop` accessor families); a box promotes to ζ-ACTIVATION-FRAME (RBP-relative) only per RULES.md § BB FRAME-PLACEMENT CRITERION. r12 is an ordinary encodable register with no reserved role. See § x86 Backend.
- **The zeta CLI selector trio is gone, not merely refusing.** `--zeta-storage=`, `--zeta-port=`, `--zeta=` do not exist in the driver at all as of this pass (commit `6da13973`) — an unrecognized `--zeta*` flag is now an ordinary unknown-option error. Only `--dump-zeta` (inspector) survives. See § ζ Local Storage.
- **`STMT_t` carries no `lang` field; `LANG_SNO`/`LANG_ICN`/`LANG_PL` are dead**, surviving only in one parked, unbuilt lower file — a prior doc taught this as the live polyglot dispatch mechanism, which is exactly the shape RULES.md's `emit_no_lang` gate forbids. See § Intermediate Representation.
- **`bb_pool` is live** (`src/ir/bb_pool.{c,h}`) — a prior doc's prune banner listed it as deleted; that was a self-contradiction, not a fact. See § x86 Backend.
- **"Stackless" is a void term project-wide** (Lon, 2026-08-27) — all three zetas (ζ-SPINE/RSP, ζ-ACTIVATION-FRAME/RBP, ζ-STANDING/root) live ON the machine stack or its heap-promoted overflow; the retired law was about a *software* value stack layered on top, never about being off the hardware stack. Reworded everywhere in this doc as "no software value stack."
- **Frame placement is a behavioral criterion, not a box-kind or language rule.** RULES.md § BB FRAME-PLACEMENT CRITERION (unbounded γ→β growth, or an unknowable operator→operand offset) is the one governing test; "SNOBOL4 is all-stack" / "Icon needs rbp for suspend" are consequences of applying it, not independent rules. See § ζ Local Storage.

**What did not get a clean answer this pass — do not treat these as resolved:**

- Whether the ZDP lattice (`zdp_tier()`, `src/ir/zeta_depth.{h,c}`) is a stalled migration or a deliberately-staged second system alongside the s121–s189 hand-written admission estimators it was meant to replace — both are live in source, only one is called. See § Pattern-Choice Carrier.
- Whether `rt_zcol_push` (live, `bb_match_arbno.cpp`) is dead-but-unreached, a deliberate fallback, or a genuine gap in the SNOBOL4-all-stack ARBNO migration. See § ζ Local Storage.
- Whether `g_sno_defer_cells` (11 tree-wide hits) is actually still live or those hits are non-live residue — the namespace-pollution ruling that was supposed to retire it was not confirmed landed. See § Passthru.
- Which of the two `descr.h` copies (`src/ir/descr.h` vs `src/runtime/core/descr.h`) is canonical. See § Passthru.
- How the three drive modes (`bb_scan`/`bb_pump`/`bb_once`, lower-case now) actually get wired per box graph today — the old `bb_broker()` dispatch chain this doc used to describe is confirmed dead, and no replacement mechanism was located this pass. See § Intermediate Representation.

Follow-up FINDINGs worth minting from this pass (not minted here — flagged for whoever picks them up): the ARBNO mixed-shape situation, the `g_sno_defer_cells` non-removal, the dangling `bb_callee_frame()` declaration in `bb_templates.h`, and the unconfirmed drive-mode dispatch mechanism above.
