# GOAL-PST-RAKU.md — Pure Syntax Tree: Raku

**Repo:** one4all + corpus + .github
**Parent goal:** `GOAL-PARSER-PURE-SYNTAX-TREE.md` (Step 3)
**Sibling:** `GOAL-PST-ICON.md`
**Status:** ⏳ Phase 1 NOT clean per `PST-LR-AUDIT.md § Scan 4` (2026-05-19) — 27 §⛔ violations. 5 owned by `PRF-12` family; 22 new sub-rungs proposed.

```
(source) ──► PARSER ──► (tree_t — pure syntax) ──► LOWER ──► IR_sm_t[]  ──┐
                                                                            ├──► interp / emitters
                                                          └──► IR_bb_t  ──┘
```

**Background.** Before 2026-05-19, this goal was bundled with Icon as `GOAL-PST-ICN-RAKU.md`. The two languages diverged sharply in scope (Icon: 1 §⛔ violation; Raku: 27 — mostly parser-side desugaring of Raku-specific syntax to runtime helper calls), so the combo was split. **All shared infrastructure rungs and cross-cutting `PST-FIELD-*` rungs are duplicated here and in `GOAL-PST-ICON.md`** for session self-containment — read both files before touching either if a session straddles them.

---

## ⛔ Separation of concerns (binding 2026-05-18) — THE governing principle

The parser's only job is to **transcribe surface syntax into `tree_t`**. The tree is a faithful, almost photographic image of the source. The parser does not reason about the meaning of what it parsed. Every semantic decision belongs to **lower**; every code-generation decision belongs to the **emitter**.

```
parser  : source                ──►  tree_t (pure syntax mirror, source order)
lower   : tree_t                ──►  SM_Program (semantic decisions, name-fountains, hoisting, desugaring)
emitter : SM_Program            ──►  native code or interpreter step
```

Things the parser **MUST NOT** do (each is a lower-time concern):

- Inspect a child's `t` to choose an operator kind (e.g. `TT_QLIT → TT_LEQ` else `TT_EQ`) — emit children as-is, let lower pick.
- Synthesize names not present in source (e.g. `__gather_N`, `__case_topic__`) — let lower fountain them.
- Hoist sub/method/class/gather definitions into a separate output queue — let lower walk the program and lift.
- Wrap nodes in `STMT(:subj(...))` envelopes for output staging — wrapping is a lower decision.
- Rename methods to `Class__method` form — lower renames during class lowering.
- Desugar control flow (`for-range` → `for-iter`, `unless` → `if not`, etc.) — lower desugars.
- Desugar syntactic sugar to runtime helper calls (`say` → `write`, `@arr[i]=v` → `arr_set`, `Foo.new` → `raku_new`, `try` → `raku_try`, `~~` → `raku_match`, `obj.method(...)` → `raku_mcall`, `map`/`grep`/`sort` → `raku_map`/`grep`/`sort`, `die` → `raku_die`, `$N`/`$<name>` → `raku_capture`/`raku_named_capture`) — lower selects the runtime helper.
- Assign `_id` / `SUB_TAG` / hoist-flag slots — lower flags.
- Re-order children to encode positional semantics — children stay in source order.

Things the parser **MAY** do (each is pure transcription):

- `shift`/`reduce` to build `tree_t` nodes in source order.
- Set `v.sval`/`v.ival`/`v.dval` from token text.
- Counter-stack discipline (`nPush`/`nInc`/`nTop`/`nPop`) to count source children for variable-arity reduces.
- Pre-pass string transformations on captured tokens (e.g. `dq_unescape` converting `\n` escapes to actual `nl`) — only when the result is fed to a leaf push.
- Source-order capture variables (`captured_name`, etc.) set via `.` for use by the next leaf push.

### Pure-syntax rules — quick reference

**Allowed:** `ast_node_new(TT_*)`, `expr_new`, `expr_unary`, `expr_binary`, `ast_push`, `expr_add_child`. Setting `v.sval/v.ival/v.dval` from token.

**Forbidden:** cloning subtrees; `sc_label_new`; building non-`tree_t` IR; variable-slot assignment; child reordering for positional semantics; **child-stealing** (re-parenting a previously-built node's children into a fresh wrapper, leaving the original as a hollow shell — same family as `sub_decl`/`gather`/`class_decl` body splicing in `raku.y`).

**⛔ Left-to-right child order (binding 2026-05-16):** Children of every node in source token order. No in-place append to an existing subtree inspected by kind.

**⛔ Three Phase-1 facets** (per `GOAL-PARSER-PURE-SYNTAX-TREE.md § "The three Phase-1 facets"`):

- **F1 — `tree_t` is the sole information channel.** Raku is the heaviest Phase-1 offender (27 §⛔ violations) but the F1 family of failures has a single common shape: **parser-side desugaring of Raku-specific syntactic sugar to runtime helper calls baked into `v.sval` of TT_FNC** (`say` → `"write"`, `@arr[i] = v` → `"arr_set"`, `Foo.new` → `"raku_new"`, `try { } catch { }` → `"raku_try"`, `~~ /re/` → `"raku_match"`, `obj.meth(args)` → `"raku_mcall"`, `die expr` → `"raku_die"`, `map`/`grep`/`sort` → `"raku_map"`/`"raku_grep"`/`"raku_sort"`, etc.). The runtime-helper name is a non-source-token fact that the parser invents. **Every PRF-12 sub-rung's F1 fix is the same shape:** add a dedicated `TT_*` kind for the source construct (`TT_SAY`, `TT_INDEX_SET`, `TT_NEW`, `TT_TRY`, `TT_SMATCH`, `TT_METHCALL`, `TT_DIE`, `TT_MAP/GREP/SORT`, etc.), let lower (or `lower_raku.c`) select the runtime helper. Plus child-stealing in `sub_decl`/`gather`/`class_decl` (Raku-specific Phase-1 family).
- **F2 — `tree_t` has exactly four fields `t`, `v`, `n`, `c`.** Raku is a primary `_id` consumer via `SUB_TAG_ID` (sub_decl marks subs with `_id == SUB_TAG_ID` and lower reads that flag to dispatch). `PRF-12-sub` is the Raku-side prerequisite for `PST-FIELD-2`: once `TT_SUB_DECL` is a dedicated kind, lower reads `t` instead of `_id`, and `_id` can be removed from the struct. `PST-FIELD-1`/`PST-FIELD-2` are duplicated in this file and `GOAL-PST-ICON.md`.
- **F3 — Children L→R in source-token order.** Most Raku expression-cascade productions are clean. The F3-flavored violations cluster in child-stealing (R15 `sub_decl`, R19 `gather`, R27 `gather_hoist_pass` in-place rewrite of node kind) — owned by `PRF-12-sub`, `PRF-12-gather`, `PRF-12-gather-hoist`.

**⛔ Phase 1 / Phase 2 sequencing (binding 2026-05-18):** C parser work (Phase 1) and SCRIP mirror work (Phase 2) **never** in the same session. Record `⚠ MIRROR-GAP` in State for each Phase 1 rung whose SCRIP mirror lags. Phase 2 work is gated on **all six** C parsers being Phase 1 clean — not just this one.

---

## ⛔ Clarification (2026-05-18) — parser actions vs lower concerns

**Grammar actions in raku.y are NOT PST violations per se.** A CFG grammar fires actions at reduce time — inline, as part of the parse. That is correct and normal CFG behavior. "Post-processing" means a separate pass over a completed tree; grammar actions are not that.

**The real issue is interface drift.** `lower.c` reads `_id == SUB_TAG_ID` (a fifth field beyond `t/v/n/c`) and never sees `TT_FOR` / `TT_SUB_DECL` / `TT_CLASS_DECL` because the parser has already desugared them to runtime calls. The lower stage is the correct place to fix the interface — by giving each construct a dedicated TT_* node kind so lower reads only `t/v/n/c`, and by moving desugar (`for-range`, `say` → `write`, `Foo.new` → `raku_new`, etc.) to lower.

**PRF-12 items are therefore `lower.c` (and a small `lower_raku.c` pre-pass) work**, not raw `raku.y` cleanups. Each rung: (1) add a dedicated `TT_*` kind to `ast.h`; (2) write the matching `lower_*` dispatch case; (3) rewrite the `raku.y` action to emit pure tree transcription with the new kind; (4) regenerate `.ref` files; (5) hold all gates. The grammar action itself stays simple — `expr_add_child` calls in source order, no runtime-helper names baked in.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate scripts:

```bash
bash /home/claude/one4all/scripts/test_smoke_raku.sh
bash /home/claude/one4all/scripts/test_smoke_scrip_all_modes.sh
bash /home/claude/one4all/scripts/test_crosscheck_snobol4.sh   # regression guard
bash /home/claude/one4all/scripts/test_smoke_icon.sh           # don't regress Icon
```

---

## ⛔ SCRIP mirror work — Raku orientation

**C side must be clean before parser_raku.sc mirror work proceeds beyond Phase A.** `parser_raku.sc` Phase A (zero function bodies with tree ops) is complete (PRF-S7-1..6 ✅ 2026-05-18: `raku_stubs.sc` deleted; the 94 stubs inlined into `parser_raku.sc` as `(epsilon . *Shift(...))` / `shift_val(...)` / `assign(...)` directly at use sites). Phase B (the work in this file) requires the C side to move semantics to `lower.c` first.

**When starting `parser_raku.sc` mirror work:** Read `SNOBOL4-SNOCONE-PRIMER.md` in full. Learn Snocone expression syntax from the SPITBOL manual and control-flow syntax from `corpus/SCRIP/parser_snocone.sc`. The goal is pure `shift`/`reduce` — no `Push`, `Pop`, `Append`, `Tree`, or helper functions that inspect children. `dq_unescape` (pure string processor) is the only permitted helper.

---

## Step 3 — Raku audit (closed)

These rungs closed in earlier sessions; rows preserved here for the rung-history record.

- [x] **PST-RAKU-3a** — Read `src/frontend/raku/raku.y` AND `corpus/SCRIP/parser_raku.sc` in full. Same four-point checklist as Icon's PST-ICN-2a. Findings V1–V6 recorded in State (`AST_*` aliases, `CODE_t/STMT_t` in `add_proc`, SUB_TAG bitmask, `make_for_range` in-place append, when_list pair `->ival` carrying cmpkind, `->nchildren/->children[]` field access).

- [x] **PST-RAKU-3b** — Fix all six audit-V violations; gates green.

---

## Step 5 — SCRIP mirror helper elimination (closed)

- [x] **PST-RAKU-5a** — Audit `parser_raku.sc` fully; catalogued `flatten_*` as child-inspection violations and `finish_*` that inspect `->kind` of prior nodes. Findings R1–R5 (R1 flatten_add/sub/mul/div/cat; R2 finish_given inspects val type; R3 finish_class inspects item type; R4 finish_for_range copies body children; R5 ~80 push/finish functions).
- [x] **PST-RAKU-5b** — Eliminated `flatten_*` violations: replaced with always-wrap `reduce` (right-leaning chain).
- [x] **PST-RAKU-5c** — Eliminated remaining `finish_*` and `push_*` helpers.

---

## Step 6 — Eliminate all remaining functions from parser_raku.sc (closed)

All PRF-1..PRF-11 rungs ✅ 2026-05-18. `finish_call_body`, `finish_new_body`, `finish_mcall_body`, `finish_sub_body`, `finish_method_body`, `finish_class_body`, `finish_main_body`, `finish_given`, `finish_gather_body` (transitional — replaced by PRF-12-gather), `push_interp_str`, `dq_unescape` (PST-clean, retained). State preserves the per-rung detail.

---

## Step 7 — Eliminate raku_stubs.sc (closed)

PRF-S7-1..6 ✅ 2026-05-18. `corpus/SCRIP/raku_stubs.sc` **DELETED**. All 94 stubs inlined into `parser_raku.sc` as `shift_val`/`shift`/`assign`. **`parser_raku.sc` now has 0 in-file helper bodies and 0 sidecars.** The remaining `dq_unescape` is PST-clean (pure string processor).

---

## ⛔ Active work — PRF-12 family (Phase B: lower.c interface)

`lower.c` currently reads `_id == SUB_TAG_ID` and never sees dedicated kinds for sub/class/gather/for-range. PRF-12 adds the dedicated kinds so lower reads only `t/v/n/c` and the parser stops baking runtime-helper names into `v.sval`. **Each sub-rung:** (1) add a `TT_*` kind to `ast.h`; (2) write `lower_*` dispatch; (3) rewrite the grammar action; (4) regen `.ref` files; (5) hold gates.

### Subset 1 — already named (legacy from combo file)

- [x] **PRF-12-gather** ✅ 2026-05-18 (Claude Sonnet 4.6) — `TT_GATHER` added; `KW_GATHER` rule emits pure `TT_GATHER[body_stmts...]`; `raku_lower_hoist_gather_pass()` post-parse pass fountains `__gather_N` and bulk-prepends defs. Gates held: smoke_raku 5/0, scrip_all_modes 2/0, crosscheck_raku 23/10 (was 21/12).

- [ ] **PRF-13** — SCRIP mirror for PRF-12-gather. Rewrite `GatherBlock` in `parser_raku.sc` to pure `nPush() ARBNO(*SubBlock_body) reduce('TT_GATHER','nTop()') nPop() nInc()`. Create `corpus/SCRIP/raku_helpers.sc` with `gather_hoist_pass(ptree)` (mirrors `raku_lower_hoist_gather_pass` using `tree.sc` API: `t()`, `n()`, `c()`, `Append`, `Prepend`). Update driver tail to call `gather_hoist_pass(ptree)` after `ptree = Pop()`. **Phase 2 — blocked on all six C parsers being Phase 1 clean.**

- [x] **PRF-12-sub** ✅ 2026-05-19 (Sonnet 4.6, one4all `96a7ca59`, corpus `39af2e1`) — `TT_SUB_DECL` added; raku.y `sub_decl` emits `TT_SUB_DECL` (no `_id`, no body-splicing); `program` rule detects `TT_SUB_DECL`; `_id == SUB_TAG_ID` removed from `lower.c`. Gather heap-corruption fixed (`free(prog->c)` → prefix-aware free). 62 corpus `.ref` files regenerated. PST-FIELD-2 Raku-side prerequisite satisfied. PRF-12-body-splice subsumed.

- [x] **PRF-12-class** ✅ 2026-05-19 (Sonnet 4.6, one4all 17a4dc45, corpus 21a4fc1) — `TT_CLASS_DECL` added; `class_decl` emits `TT_CLASS_DECL[TT_VAR(cname), fields..., methods(TT_SUB_DECL)...]`; `lower_class_decl` renames methods to `Cls__method`, registers in lower-side meth table, lowers bodies, emits RECORD_MAKE; `class_body_list` method actions use `ast_node_new(TT_SUB_DECL)` to avoid stale `v.sval` after `v.ival` overwrite; `ast_print.c` excludes `TT_SUB_DECL`/`TT_PROC_DECL` from `v.sval` print (name in `c[0]`); 75 corpus `.ref` files regenerated. Gates held.

- [ ] **PRF-12-for** *(renamed from PRF-12-for-range)* — lower.c: add `TT_FOR_RANGE` (or reuse `TT_FOR`); write `lower_for_range` desugaring to `TT_ASSIGN + TT_WHILE`. raku.y `for_stmt`: emit `TT_FOR[TT_VAR(v), lo, hi, body]` — delete `make_for_range`. Also: stop inspecting `$2->t==TT_VAR` to conditionally wrap in `TT_ITERATE` (audit R13); always emit a pure-syntax shape and let lower decide.

- [ ] **PRF-12-self** — lower.c: `lower_method_decl` injects implicit `self` as first param when lowering a method. raku.y `method_decl`: stop injecting `leaf_sval(TT_VAR, "self")` into the child list (audit R18).

- [x] **PRF-12-program** ✅ 2026-05-19 (Sonnet 4.6, one4all 2fed81d3, corpus 47a8845) — `program` action now calls `add_proc(item)` for all stmt_list items unconditionally; no `main` synthesis, no `TT_SUB_DECL` discrimination. All items emit flat as `TT_STMT` children of `raku_prog_result`. Lower handles `TT_SUB_DECL`/`TT_CLASS_DECL` subjects; orphan stmts run inline. 71 corpus `.ref` files regenerated. Gates held.

### Subset 2 — new from PST-LR-AUDIT-1e (2026-05-19, 14 new sub-rungs)

Each maps to one of the 27 §⛔ violations in `PST-LR-AUDIT.md § 4.10`. See that file for line numbers and current parser shape.

- [ ] **PRF-12-my-type** *(audit R2)* — `my Type $var = expr;`: the `IDENT` (type annotation) is currently `free()`'d in the action (lines 229–240 of `raku.y`). Either preserve as a child of `TT_ASSIGN`, or add a side-channel-free `TT_DECL[TT_VAR(type), TT_VAR(name), expr]` kind. Lower selects runtime behavior (type is documentation-only in current SCRIP, but the parser must not destroy the source token).

- [x] **PRF-12-say** *(audit R3, R4)* ✅ 2026-05-19 (Sonnet 4.6) — `TT_SAY[expr]` / `TT_SAY_FH[fh,expr]` added to ast.h; raku.y actions emit pure tree; lower.c dispatches to `write`/`raku_say_fh`; 35 .ref files regenerated.

- [x] **PRF-12-print** *(audit R5, R6)* ✅ 2026-05-19 (Sonnet 4.6) — `TT_PRINT[expr]` / `TT_PRINT_FH[fh,expr]` added; same session as PRF-12-say.

- [x] **PRF-12-arr-hash-ops** *(audit R7, R8, R9 + atom-side at R29-related)* ✅ 2026-05-19 (Sonnet 4.6, one4all ac0e48f3, corpus 9f4e7af) — `TT_ARR_GET`, `TT_ARR_SET`, `TT_HASH_GET`, `TT_HASH_SET`, `TT_HASH_DELETE`, `TT_HASH_EXISTS` added to ast.h; lower.c dispatches SM_CALL_FN to arr_get/arr_set/hash_get/hash_set/hash_delete/hash_exists; 9 raku.y actions rewritten to ast_node_new+ast_push; raku.tab.c regenerated; 10 corpus .ref files regenerated. lower_baseline.txt rk_arr_get hash updated. Gates held.

- [ ] **PRF-12-try** *(audit R10)* — `try { } catch { }` should produce `TT_TRY[body, opt_catch_body]` kind. `lower_try` selects `raku_try` runtime helper.

- [ ] **PRF-12-unless** *(audit R11)* — explicit decision needed: (a) keep `unless` → `TT_IF(TT_NOT(...))` (synthesized TT_NOT not in source), or (b) introduce `TT_UNLESS` kind and let lower desugar. Decision: prefer (b) for purity (source token `unless` becomes the node kind directly).

- [ ] **PRF-12-given** *(audit R14)* — `given_stmt` should build `TT_CASE` children directly from the `when_list` accumulator items (without wrapping each `(val,body)` pair in a temporary `TT_SEQ_EXPR` that is immediately dismantled and freed). Build pattern: each `when` reduction `expr_add_child(case_node, val); expr_add_child(case_node, body);` directly. No intermediate pair node. (The current `when_list` returns an ExprList ✅ — only the wrap-then-unwrap is the violation.)

- [ ] **PRF-12-smatch** *(audit R20)* — `~~ /regex/` should produce `TT_SMATCH[subj, regex_qlit, flavor]` kind (where `flavor` is one of `TT_QLIT("match")` / `TT_QLIT("match_global")` / `TT_QLIT("subst")` — encoded as kind-or-value, decided in implementation). `lower_smatch` selects runtime helper.

- [ ] **PRF-12-new** *(audit R21)* — `Foo.new(...)` should produce `TT_NEW[TT_QLIT("Foo"), args]` kind. `lower_new` selects `raku_new` runtime helper.

- [ ] **PRF-12-mcall** *(audit R22)* — `obj.method(args)` should produce `TT_METHCALL[obj, TT_QLIT("method"), args]` kind. `lower_mcall` selects `raku_mcall` runtime helper.

- [x] **PRF-12-die** *(audit R23)* ✅ 2026-05-19 (Sonnet 4.6, one4all `c596462d`, corpus `adfdbb6`) — `TT_DIE[expr]` kind added; raku.y emits pure tree; lower.c dispatches SM_CALL_FN "raku_die" 1; sm_interp+sm_jit_interp handle raku_die from stack (sets g_raku_exception, pushes FAILDESCR). Gates held.

- [ ] **PRF-12-hof** *(audit R24)* — `map`/`grep`/`sort` should produce `TT_MAP` / `TT_GREP` / `TT_SORT` kinds with the closure as first child, iterable as second. `lower_hof` selects runtime helper.

- [ ] **PRF-12-capture** *(audit R25)* — `$N` and `$<name>` should produce `TT_CAPTURE[TT_ILIT(N)]` and `TT_NAMED_CAPTURE[TT_QLIT(name)]` kinds. Lower selects `raku_capture` / `raku_named_capture`.

- [ ] **PRF-12-twigil** *(audit R26)* — `$.foo` / `$!foo` should produce `TT_TWIGIL_FIELD(sval=name)` with no synthesized `self` child. `lower_twigil` attaches the `self` reference and dispatches to the field-access helper.

### Subset 3 — body-splicing cleanup (audit R15, R19, R27)

These are **child-stealing** violations distinct from the runtime-helper-name desugaring. The pattern: a wrapper node is built fresh, then the children of one of its inputs (typically a block / TT_SEQ_EXPR) are stolen and re-parented under the wrapper, leaving the input as a hollow shell.

- [x] **PRF-12-body-splice** *(audit R15)* ✅ **Subsumed by PRF-12-sub.**

- [ ] **PRF-12-gather-splice** *(audit R19)* — `expr : KW_GATHER block` splices block children into `TT_GATHER` (lines 472–477). Same fix: keep body as a single child of `TT_GATHER`. **Subsumed by PRF-12-gather follow-up** — current PRF-12-gather may already do this correctly; verify and check the box if so.

- [ ] **PRF-12-gather-hoist** *(audit R27)* — `raku_lower_hoist_gather_pass` rewrites every `TT_GATHER` node's `t` / `v.sval` / `n` / `c` in place (lines 647–653) and splices new TT_STMTs into `prog->c[]` (lines 671–685). This is a parser-internal post-pass — strictly, both the rewrite and the prepend are rule 2 violations. Fix: move the entire hoist pass to `lower.c` as `lower_gather_hoist_pass`, called by `lower` before its main traversal. The parser leaves `TT_GATHER` nodes untouched in the program tree.

### Done criteria

**Phase A — helper elimination (`parser_raku.sc` form):** ✅ COMPLETE. Zero `function` bodies in `parser_raku.sc` that call `Push()`, `Append()`, or `tree()`. Pure string transformers (no tree ops) permitted (`dq_unescape` only).

**Phase B — separation-of-concerns (`lower.c` interface):** lower.c reads only `t/v/n/c` from tree nodes; no `_id` side-channel; all constructs have dedicated `TT_*` node kinds; desugar happens in lower not parser. **Status:** PRF-12-gather done; ~18 sub-rungs remaining (`PRF-12-sub`, `-class`, `-for`, `-self`, `-program`, `-my-type`, `-say`, `-print`, `-arr-hash-ops`, `-try`, `-unless`, `-given`, `-smatch`, `-new`, `-mcall`, `-die`, `-hof`, `-capture`, `-twigil`, `-body-splice`, `-gather-splice`, `-gather-hoist`).

---

## PST-FIELD rungs — strip extra fields from `tree_t` struct (Phase 1 C, cross-cutting)

**These rungs are duplicated here and in `GOAL-PST-ICON.md`** because both Icon and Raku are primary `_id` consumers. The struct itself lives in `src/include/ast.h`; consumers are spread across both frontends and the interpreter. Coordinate cross-session via the State block.

**Current struct** (`src/include/ast.h` lines ~62–73):

```c
struct tree_t {
    tree_e      t;       /* kind — KEEP */
    union { char *sval; long long ival; double dval; } v;  /* value — KEEP */
    int         n;       /* child count — KEEP */
    tree_t   ** c;       /* children — KEEP */
    int         _nalloc; /* allocator bookkeeping — REMOVE */
    int         _id;     /* semantic side-channel — REMOVE */
};
```

- [x] **PST-FIELD-1 — Remove `_nalloc` from `tree_t`. PHASE 1 C.**

  **What:** `_nalloc` is a growable-array bookkeeping field — it tracks allocated capacity of the `c` array so `ast_push` can realloc without knowing the true size. Carries zero semantic information.

  **Where:**
  - `src/include/ast.h`: remove `int _nalloc` from struct. Update `ast_push` to use a hidden capacity prefix word, or two-pass build (count-then-fill).
  - `src/lower/ast_clone.c` line ~13: remove `c->_nalloc = e->_nalloc`.
  - Grep confirms only `ast.h` and `ast_clone.c` reference it directly.

  **Gates:** full build + `smoke_snobol4`, `crosscheck_snobol4`, `smoke_scrip_all_modes`, `smoke_icon`, `smoke_raku`.

- [x] **PST-FIELD-2 — Remove `_id` from `tree_t`. PHASE 1 C. BLOCKED on PST-ICN-LR-1 + PRF-12-sub.**

  **What:** `_id` is used as a semantic side-channel in three places: (1) Raku `SUB_TAG_ID` (the violation closed by `PRF-12-sub`); (2) Icon param count (the violation closed by `PST-ICN-LR-1` in `GOAL-PST-ICON.md`); (3) interpreter slot/env index (larger rework, scope separately).

  **Sequencing:**
  1. **PST-ICN-LR-1** (in `GOAL-PST-ICON.md`) — Icon param-count move via `TT_PROC_DECL`.
  2. **PRF-12-sub** (this file) — Raku SUB_TAG move via `TT_SUB_DECL`.
  3. Interpreter slots — separate rung.
  4. Remove `int _id` from struct only after all write sites are gone.
  5. Remove `c->_id = e->_id` from `ast_clone.c`.

  **Gates:** full build + `smoke_icon`, `smoke_raku`, `smoke_snobol4`, `crosscheck_snobol4`, `smoke_scrip_all_modes`, `beauty_self_host` 29/22.

---

## Done criterion for this goal

1. PST-RAKU-3a/3b checked [x]. ✅
2. PST-RAKU-5a/5b/5c checked [x]. ✅
3. PRF-1..PRF-11 checked [x]. ✅
4. PRF-S7-1..6 checked [x]. ✅ (`raku_stubs.sc` deleted; 0 helpers in `parser_raku.sc` except `dq_unescape`.)
5. **PRF-12 family complete** (Phase B): all 18 sub-rungs above checked [x]; lower.c reads only `t/v/n/c`; `_id == SUB_TAG_ID` reads are gone from lower.
6. **PRF-13** (SCRIP mirror for PRF-12-gather) checked [x] — Phase 2, gated on all six C parsers Phase 1 clean.
7. **PST-FIELD-1 checked [x]** (cross-cutting with `GOAL-PST-ICON.md`).
8. **PST-FIELD-2 checked [x]** (cross-cutting with `GOAL-PST-ICON.md`; depends on PRF-12-sub).
9. All gate scripts green at baseline.
10. Beauty self-host byte-identical (Milestone 1 protected).
11. **`tree_t` has exactly four fields: `t`, `v`, `n`, `c`.**
12. Parent goal `GOAL-PARSER-PURE-SYNTAX-TREE.md` Step 3 updated to ✅.

On completion: update parent goal step ladder, bump watermark, commit + push HQ.

---

## State

```
watermark: 2026-05-19 (Sonnet 4.6) — PRF-12-program ✅; one4all 2fed81d3 corpus 47a8845
           2026-05-19 (Sonnet 4.6) — PRF-12-class ✅; one4all 17a4dc45 corpus 21a4fc1
           2026-05-19 (Sonnet 4.6) — PRF-12-arr-hash-ops ✅; one4all ac0e48f3 corpus 9f4e7af
status: ⏳ Phase 1 NOT clean — 19 §⛔ violations remaining
prior closed rungs (preserved for history):
  PST-RAKU-3a/3b ✅ (Sonnet 4.6) — V1..V6 fixed
  PST-RAKU-5a/5b/5c ✅ 2026-05-16 — flatten_* and finish_* removed
  PRF-1..PRF-7 ✅ 2026-05-18 — finish bodies inlined
  PRF-8 ✅ 2026-05-18 (Opus 4.7) — finish_given; TT_CASE 2-per-arm; cmpkind → lower
  PRF-9 ✅ 2026-05-18 (Opus 4.7) — finish_gather_body replaced by PRF-12-gather
  PRF-10 ✅ 2026-05-18 (Opus 4.7) — push_interp_str; LitStrDQ nPush/reduce/nPop
  PRF-11 ✅ 2026-05-18 — dq_unescape PST-clean, retained
  PRF-12-gather ✅ 2026-05-18 (Sonnet 4.6) — TT_GATHER; raku_lower_hoist_gather_pass()
  PRF-S7-1..6 ✅ 2026-05-18 — raku_stubs.sc DELETED; 94 stubs inlined
  PRF-12-say ✅ 2026-05-19 (Sonnet 4.6) — TT_SAY / TT_SAY_FH
  PRF-12-print ✅ 2026-05-19 (Sonnet 4.6) — TT_PRINT / TT_PRINT_FH
  PRF-12-sub ✅ 2026-05-19 (Sonnet 4.6, one4all 96a7ca59, corpus 39af2e1)
  PRF-12-die ✅ 2026-05-19 (Sonnet 4.6, one4all c596462d, corpus adfdbb6)
  PRF-12-body-splice ✅ subsumed by PRF-12-sub
  PRF-12-arr-hash-ops ✅ 2026-05-19 (Sonnet 4.6, one4all ac0e48f3, corpus 9f4e7af)
  PRF-12-class ✅ 2026-05-19 (Sonnet 4.6, one4all 17a4dc45, corpus 21a4fc1):
    TT_CLASS_DECL; lower_class_decl (rename+register+lower); class_body_list
    uses ast_node_new; ast_print.c TT_SUB_DECL/TT_PROC_DECL excluded from v.sval print;
    75 corpus .ref files regenerated. Gates held.
  PRF-12-program ✅ 2026-05-19 (Sonnet 4.6, one4all 2fed81d3, corpus 47a8845):
    program action: unconditional add_proc for all items; no main synthesis;
    71 corpus .ref files regenerated. Gates held.
audit findings (27 original, 10 closed):
  R1   ✅ closed PRF-12-program
  R2   KW_MY IDENT VAR_* discards type annotation (owned: PRF-12-my-type)
  R3-6 ✅ closed PRF-12-say/print
  R7-9 ✅ closed PRF-12-arr-hash-ops
  R10  KW_TRY/KW_CATCH desugar (owned: PRF-12-try)
  R11  KW_UNLESS desugar (owned: PRF-12-unless)
  R12-13 for_stmt desugar + inspect-kind (owned: PRF-12-for)
  R14  given_stmt pair wrap/unwrap (owned: PRF-12-given)
  R15  ✅ closed PRF-12-sub/PRF-12-body-splice
  R16-17 ✅ closed PRF-12-class
  R18  method_decl synth-self (owned: PRF-12-self)
  R19  KW_GATHER child-stealing (owned: PRF-12-gather-splice)
  R20  OP_SMATCH desugar (owned: PRF-12-smatch)
  R21  KW_NEW desugar (owned: PRF-12-new)
  R22  atom.method() desugar (owned: PRF-12-mcall)
  R23  ✅ closed PRF-12-die
  R24  KW_MAP/GREP/SORT desugar (owned: PRF-12-hof)
  R25  VAR_CAPTURE / VAR_NAMED_CAPTURE desugar (owned: PRF-12-capture)
  R26  VAR_TWIGIL synth-self (owned: PRF-12-twigil)
  R27  gather hoist in-place rewrite (owned: PRF-12-gather-hoist)
mirror gaps: PRF-13 (SCRIP mirror for PRF-12-gather) — Phase 2, gated
next:        PRF-12-for (R12-13, TT_FOR_RANGE desugar) or PRF-12-try (R10)
gates (baseline): smoke_raku 5/0 · scrip_all_modes 2/0 · crosscheck_snobol4 5/1 · smoke_icon 5/0
heads:       .github @ (this commit) · one4all @ 2fed81d3 · corpus @ 47a8845
```

---

### Session-end note — 2026-05-19 (Sonnet 4.6)

PRF-12-die complete. `TT_DIE` is the dedicated kind for Raku `die` expressions —
parser emits pure `TT_DIE[expr]`; lower selects `SM_CALL_FN "raku_die"`; both
sm_interp and sm_jit_interp handle `raku_die` from the SM stack (pop msg,
set `g_raku_exception`, push FAILDESCR). 22 §⛔ violations remain; next:
PRF-12-class or PRF-12-arr-hash-ops.

---

## Authorship

Drafted by Claude Opus 4.7, 2026-05-19. Created by splitting `GOAL-PST-ICN-RAKU.md` (originally drafted by Claude Sonnet 4.6, 2026-05-16; extensive PRF-* history accumulated 2026-05-18 sessions with Sonnet 4.6 and Opus 4.7) into Icon-only and Raku-only files at Lon's request. PRF-12 sub-rungs R1–R27 promoted from `PST-LR-AUDIT.md § Scan 4` per LR-AUDIT-1e completion. PST-FIELD-1 and PST-FIELD-2 rungs duplicated into both split files for session self-containment; coordinate cross-session via the State block of whichever language's session touches the shared struct first.
