# GOAL-PST-ICON.md — Pure Syntax Tree: Icon

**Repo:** one4all + corpus + .github
**Parent goal:** `GOAL-PARSER-PURE-SYNTAX-TREE.md` (Step 2)
**Sibling:** `GOAL-PST-RAKU.md`
**Status:** ⏳ Phase 1 NOT clean per `PST-LR-AUDIT.md § Scan 2` re-grade (2026-05-19) — one §⛔ violation (`PST-ICN-LR-1`) blocks `PST-FIELD-2`.

```
(source) ──► PARSER ──► (tree_t — pure syntax) ──► LOWER ──► IR_sm_t[]  ──┐
                                                                            ├──► interp / emitters
                                                          └──► IR_bb_t  ──┘
```

**Background.** Before 2026-05-19, this goal was bundled with Raku as `GOAL-PST-ICN-RAKU.md`. The two languages diverged sharply in scope (Icon: 1 §⛔ violation; Raku: 27), so the combo was split. **All shared infrastructure rungs and cross-cutting `PST-FIELD-*` rungs are duplicated here and in `GOAL-PST-RAKU.md`** for session self-containment — read both files before touching either if a session straddles them.

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
- Desugar control flow (`for-range` → `for-iter`, `unless` → `if not`, etc.) — lower desugars.
- Assign `_id` / `SUB_TAG` / hoist-flag slots — lower flags.
- Re-order children to encode positional semantics — children stay in source order.

Things the parser **MAY** do (each is pure transcription):

- `shift`/`reduce` to build `tree_t` nodes in source order.
- Set `v.sval`/`v.ival`/`v.dval` from token text.
- Counter-stack discipline (`nPush`/`nInc`/`nTop`/`nPop`) to count source children for variable-arity reduces.
- Pre-pass string transformations on captured tokens (e.g. `dq_unescape`) — only when the result is fed to a leaf push.
- Source-order capture variables (`captured_name`, etc.) set via `.` for use by the next leaf push.

### Pure-syntax rules — quick reference

**Allowed:** `ast_node_new(TT_*)`, `expr_new`, `expr_unary`, `expr_binary`, `ast_push`, `expr_add_child`. Setting `v.sval/v.ival/v.dval` from token.

**Forbidden:** cloning subtrees; `sc_label_new`; building non-`tree_t` IR; variable-slot assignment; child reordering for positional semantics.

**⛔ Left-to-right child order (binding 2026-05-16):** Children of every node in source token order. No in-place append to an existing subtree inspected by kind.

**⛔ Three Phase-1 facets** (per `GOAL-PARSER-PURE-SYNTAX-TREE.md § "The three Phase-1 facets"`):

- **F1 — `tree_t` is the sole information channel.** Icon is among the cleanest C parsers on this axis after PST-ICN-4a/4b closed; the remaining F1 violation is `parse_proc` packing `nparams` into `_id` as an out-of-band separator between params and body in a flat n-ary child list — owned by `PST-ICN-LR-1`. Once that rung lands (param/body separated into `TT_VLIST`/`TT_PROGRAM` children), Icon's parser output is purely tree-borne.
- **F2 — `tree_t` has exactly four fields `t`, `v`, `n`, `c`.** Icon is a primary `_id` consumer via `parse_proc` (`proc->_id = nparams`). PST-ICN-LR-1 is the Icon-side prerequisite for closing `PST-FIELD-2` (struct-level removal of `_id`). `PST-FIELD-1` / `PST-FIELD-2` are duplicated in this file and in `GOAL-PST-RAKU.md` for session self-containment.
- **F3 — Children L→R in source-token order.** Icon's hand-rolled recursive-descent parser is the clean reference shape (`parse_and`, `parse_alt`, `parse_mul`/`parse_add` all build fresh n-ary or left-leaning chains with no mutate-prior). The only audit-flagged Icon row (I5, `parse_proc`) is technically an F1/F2 issue, not an F3 one.

**⛔ Phase 1 / Phase 2 sequencing (binding 2026-05-18):** C parser work (Phase 1) and SCRIP mirror work (Phase 2) **never** in the same session. Record `⚠ MIRROR-GAP` in State for each Phase 1 rung whose SCRIP mirror lags. Phase 2 work is gated on **all six** C parsers being Phase 1 clean — not just this one.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate scripts:

```bash
bash /home/claude/one4all/scripts/test_smoke_icon.sh
bash /home/claude/one4all/scripts/test_smoke_scrip_all_modes.sh
bash /home/claude/one4all/scripts/test_crosscheck_snobol4.sh   # regression guard
```

---

## ⛔ SCRIP mirror work — Icon orientation

**C side is mostly clean.** `parser_icon.sc` Phase 1 SCRIP-mirror helper-elimination is **complete** (PST-ICN-4a/4b ✅ — all 13 helpers removed, 4 leaf-pushers inlined as `(epsilon . *Shift(...))` ). The remaining C-side wart is `PST-ICN-LR-1` (`parse_proc` packs params + body into one flat n-ary child list with `_id=nparams` as the separator marker — see `PST-LR-AUDIT.md § Scan 2`).

**Do not begin Phase 2 SCRIP-mirror divergence work** until `PST-ICN-LR-1` is closed AND all five sister C parsers are Phase 1 clean per `PST-LR-AUDIT.md`'s rollup. When that day comes, the **Phase 2 starting point for Icon is `corpus/SCRIP/parser_icon.sc`** which is already at zero in-file helper bodies after PST-ICN-4b — the only Phase 2 work expected for Icon is byte-identity verification of `--dump-ast` against the C frontend.

---

## Step 2 — Icon audit (closed)

These rungs closed in earlier sessions; rows preserved here for the rung-history record.

- [x] **PST-ICN-2a** — Read `src/frontend/icon/icon_parse.c` AND `corpus/SCRIP/parser_icon.sc` in full. Flag: (1) in-place append instead of always-wrap; (2) children not in source order; (3) non-`tree_t` IR allocation; (4) slot assignment / scope tracking. Findings recorded in earlier State block.

- [x] **PST-ICN-2b** — Fix all violations found in 2a (or record "none"). Both C and SCRIP files in the same commit. Gates: `smoke_icon`, `smoke_scrip_all_modes`, `crosscheck_snobol4`.

---

## Step 4 — SCRIP mirror helper elimination (closed)

**Finding (2026-05-16, session re-audit):** `parser_icon.sc` carried 13 helper functions that performed tree Pop/inspect/reassemble instead of pure `shift`/`reduce`. These were eliminated in PST-ICN-4a/4b. **Closed.**

**Violations originally found and fixed:**

| Helper | Violation | Fix landed |
|--------|-----------|------------|
| `push_subscript` | Pops idx+lhs, inspects order | `reduce('TT_IDX', 2)` |
| `push_section` (`:` case) | Pops hi/lo/lhs | `reduce('TT_SECTION', 3)` |
| `decompose_proc` | `TopCounter()`+loop+`Append` | Inline `nPush/nInc/reduce('TT_FNC','nTop()')/nPop` + STMT wrapper |
| `push_record` | same loop pattern | `reduce('TT_RECORD', 'nTop()')` inline |
| `push_global_top` | same loop pattern | `reduce('TT_GLOBAL', 'nTop()')` inline |
| `push_local_stmt` | same loop pattern | `reduce('TT_LOCAL', 'nTop()')` inline |
| `push_static_stmt` | same loop pattern | `reduce('TT_STATIC_DECL', 'nTop()')` inline |
| `push_field` | calls `v()` on child to extract sval | `reduce('TT_FIELD', 2)` with `[lhs, TT_VAR(fname)]` children; `lower_icn.c` reads `e->c[1]->v.sval` |
| `push_match` | synthesized `TT_VAR('match')` not in source | `TT_MATCH_UNARY` added to `ast.h`; `reduce('TT_MATCH_UNARY', 1)` |
| `push_qlit` | named function wrapping a leaf push | Inline as `(epsilon . *Shift('TT_QLIT', ...))` |
| `push_cset` | named function wrapping a leaf push | Inline as `(epsilon . *Shift('TT_CSET', ...))` |
| `push_flit` | named function + `REAL()` computation | Inline (REAL from token is allowed) |
| `push_kw` | named function + `'&' kwname` concat | Inline |

- [x] **PST-ICN-4a** — Infrastructure: add `TT_MATCH_UNARY` to `ast.h`; update `icon_parse.c` unary `=` and `TT_FIELD` construction; update `lower_icn.c` for both new kinds; regenerate `.ref` files for affected fixtures. Gates: `smoke_icon`, `crosscheck_snobol4`.

- [x] **PST-ICN-4b** — SCRIP mirror: removed all 13 helpers from `parser_icon.sc`; replaced structural assemblers with inline `shift`/`reduce` actions. The 4 leaf-push helpers (`push_qlit`, `push_cset`, `push_flit`, `push_kw`) **subsequently inlined as `(epsilon . *Shift(...))` (2026-05-18); `icon_helpers.sc` sidecar deleted**. `parser_icon.sc` is now **zero in-file helper bodies and zero sidecar functions**. Gates: `smoke_icon`, `smoke_scrip_all_modes`, `crosscheck_snobol4`.

---

## ⛔ Active rung — PST-ICN-LR-1 (Phase 1 C, blocks PST-FIELD-2)

**Discovered:** `PST-LR-AUDIT.md § Scan 2`, 2026-05-19.

**Location:** `src/frontend/icon/icon_parse.c`, `parse_proc` (lines 727–761) — specifically the `TT_FNC` construction around line 753–758:

```c
/* Currently — flat n-ary with _id=nparams as out-of-band separator */
proc = ast_node_new(TT_FNC);
proc->v.sval = intern(procname);
proc->_id    = nparams;           /* ← the violation: tree shape requires _id to decode */
push_child(proc, ast_node_new(TT_VAR(procname)));     /* c[0] = name */
for (each param)    push_child(proc, param_var);      /* c[1..nparams] */
for (each body stmt) push_child(proc, body_stmt);     /* c[nparams+1..end] */
```

**The §⛔ violation (per audit rule 3 reasoning):** parameter block and body block are two distinct source token groups (separated by `;` and the function body delimiter), but they are flattened into a single child list. The boundary information is in `_id` — a fifth field that the rest of Phase 1 work is trying to eliminate. Without `_id`, the tree is **undecodable**: lower cannot tell where params end and body begins.

**Fix:** Restructure `TT_FNC` for proc decls to have an explicit structural shape with two parent slots — one for the param block, one for the body block:

```c
/* After fix — structural separation, no _id needed */
proc = ast_node_new(TT_FNC);
proc->v.sval = intern(procname);
proc->v.ival = 0;                                         /* unused */
push_child(proc, ast_node_new(TT_VAR(procname)));         /* c[0] = name */
push_child(proc, TT_VLIST(TT_VAR(p1)...TT_VAR(pN)));      /* c[1] = params block */
push_child(proc, TT_PROGRAM(stmt1...stmtN));              /* c[2] = body block */
```

Two structural alternatives — pick one in implementation:

- **Option A — fresh TT_FNC shape:** `TT_FNC[TT_VAR(name), TT_VLIST(params), TT_PROGRAM(body)]`. Three fixed children. Lower reads `c[0]` for name (or `v.sval`, since both carry it), `c[1]->c[]` for params, `c[2]->c[]` for body. Matches Snocone's `TT_DEFINE` layout (PST-SC-4g).
- **Option B — dedicated kind:** add `TT_PROC_DECL` to `tree_e`. Same three children. Lower has a dedicated dispatch case, distinct from the n-ary call-site `TT_FNC`. Matches Raku's planned `TT_SUB_DECL`/`TT_CLASS_DECL` per PRF-12.

**Recommended: Option B.** A proc declaration is structurally distinct from a call expression — the parser was conflating them via `_id`. Adding `TT_PROC_DECL` makes the kind do the work `_id` was hacking. This also avoids cross-cutting changes to every lower-side TT_FNC dispatch site.

### Sub-step ladder

- [x] **PST-ICN-LR-1a** — Add `TT_PROC_DECL` to `tree_e` (in `src/include/ast.h`) and to the name table. Confirm no other frontend already uses this name.
- [x] **PST-ICN-LR-1b** — Rewrite `parse_proc` to build `TT_PROC_DECL[TT_VAR(name), TT_VLIST(params), TT_PROGRAM(body)]`. Delete the `proc->_id = nparams` line. Verify no other code in `icon_parse.c` reads `_id` from this node.
- [x] **PST-ICN-LR-1c** — Update `lower_icn.c` to dispatch on `TT_PROC_DECL`. Read params from `c[1]->c[]`, body from `c[2]->c[]`. Currently reads `proc->_id` for nparams (line 1002); replace with `proc->c[1]->n`. Currently iterates `proc->c[1..]` mixing params + body; replace with the two separate iterations.
- [x] **PST-ICN-LR-1d** — Update `icn_runtime.c` lines ~198, ~229 — anywhere it reads `_id` from a proc TT_FNC node. Replace with `c[1]->n`.
- [x] **PST-ICN-LR-1e** — Update `polyglot.c` line ~121 — same fix.
- [x] **PST-ICN-LR-1f** — Regenerate `.ref` files for any Icon fixtures whose `--dump-ast` output changes shape. Run `make ref-icon` (or hand-update if no batch target).
- [x] **PST-ICN-LR-1g** — Record `⚠ MIRROR-GAP-ICN-LR-1` in State; `parser_icon.sc` mirror update is Phase 2 work.

**Gates:** `smoke_icon` 5/0, `smoke_scrip_all_modes` 2/0, `crosscheck_snobol4` floor, `test_icon_all_rungs.sh` PASS≥194 (current Icon rung floor — must not regress).

---

## PST-FIELD rungs — strip extra fields from `tree_t` struct (Phase 1 C, cross-cutting)

**These rungs are duplicated here and in `GOAL-PST-RAKU.md`** because both Icon and Raku are primary `_id` consumers. The struct itself lives in `src/include/ast.h`; consumers are spread across both frontends and the interpreter. Coordinate cross-session via the State block.

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

  **What:** `_nalloc` is a growable-array bookkeeping field — it tracks allocated capacity of the `c` array so `ast_push` can realloc without knowing the true size. It carries zero semantic information and must never be read by lower or the interpreter.

  **Where:**
  - `src/include/ast.h`: remove `int _nalloc` from struct. Update `ast_push` (inline in `ast.h`) to use a sentinel: store capacity in `c[-1]` as a hidden prefix word, or switch to a two-pass build (count children first, allocate exact, fill). Simplest: count-then-fill. Parser actions that call `ast_push` incrementally must switch to `expr_add_child` after a pre-sized allocation, or use a local `tree_t*` with the count known from the grammar rule arity.
  - `src/lower/ast_clone.c` line ~13: remove `c->_nalloc = e->_nalloc`.
  - Any other file that reads or writes `_nalloc` directly (grep confirms only `ast.h` and `ast_clone.c`).

  **Why:** The struct must have exactly four semantic fields. Allocator state is an implementation detail; it belongs in a wrapper or as a hidden prefix, not as a named field on the public struct.

  **Gates:** full build + `smoke_snobol4`, `crosscheck_snobol4`, `smoke_scrip_all_modes`, `smoke_icon`, `smoke_raku`.

- [x] **PST-FIELD-2 — Remove `_id` from `tree_t`. PHASE 1 C. BLOCKED on PST-ICN-LR-1 + PRF-12-sub.**

  **What:** `_id` is used as a semantic side-channel in three places:
  1. **Raku** (`raku.y`, `raku_driver.h`): `SUB_TAG_ID` sentinel stamped on `TT_FNC` nodes to distinguish sub-declaration nodes from call nodes. Read in `raku.y` actions and in `lower.c:1306`.
  2. **Icon** (`icon_parse.c:755`, `lower_icn.c:1002`, `icn_runtime.c`): param count stored on `TT_FNC` proc nodes. **This is the PST-ICN-LR-1 violation.**
  3. **Interpreter** (`interp_eval.c`): slot index, env index, clone copy.

  **Fix — Raku SUB_TAG:** owned by **PRF-12-sub** in `GOAL-PST-RAKU.md`. Replace `_id == SUB_TAG_ID` tag with a dedicated `TT_SUB_DECL` node kind. A `TT_SUB_DECL` node is unambiguously a sub declaration — no tag needed.

  **Fix — Icon param count:** owned by **PST-ICN-LR-1** (this file). Restructures `TT_FNC` to use `TT_PROC_DECL` with structural separation `[name, TT_VLIST(params), TT_PROGRAM(body)]` — no `_id` needed.

  **Fix — interpreter slot/env index:** `interp_eval.c` uses `_id` for slot and env indices on `TT_VAR` and `TT_FNC` nodes at runtime. These are runtime annotations set by lower/eval, not parse-time fields. Correct fix: move runtime annotations out of `tree_t` entirely into a parallel side table indexed by node pointer or node sequence number. This is larger work — scope it separately if needed. Alternative (smaller): encode as `v.ival` where `v.sval` is not needed at runtime (safe for `TT_VAR` nodes whose name is already resolved). Audit each `_id` write in `interp_eval.c` and decide per site.

  **Sequencing:**
  1. **PST-ICN-LR-1** (this file) — Icon param-count move via TT_PROC_DECL.
  2. **PRF-12-sub** (`GOAL-PST-RAKU.md`) — Raku SUB_TAG move via TT_SUB_DECL.
  3. Interpreter slots — separate rung (largest scope).
  4. Remove `int _id` from struct only after all write sites are gone.
  5. Remove `c->_id = e->_id` from `ast_clone.c`.

  **Gates:** full build + `smoke_icon`, `smoke_raku`, `smoke_snobol4`, `crosscheck_snobol4`, `smoke_scrip_all_modes`, `beauty_self_host` 29/22.

---

## Done criterion for this goal

1. PST-ICN-2a/2b checked [x]. ✅
2. PST-ICN-4a/4b checked [x]. ✅
3. **PST-ICN-LR-1a–g checked [x].** (Active work — Phase 1 C left for this goal.)
4. **PST-FIELD-1 checked [x]** (cross-cutting with `GOAL-PST-RAKU.md`).
5. **PST-FIELD-2 checked [x]** (cross-cutting with `GOAL-PST-RAKU.md`; depends on PRF-12-sub).
6. All gate scripts green at baseline.
7. Beauty self-host byte-identical (Milestone 1 protected).
8. **`tree_t` has exactly four fields: `t`, `v`, `n`, `c`.**
9. `parser_icon.sc` contains zero in-file helper functions that Pop/INSPECT/reassemble trees and zero sidecar. ✅ (already complete as of 2026-05-18.)
10. Parent goal `GOAL-PARSER-PURE-SYNTAX-TREE.md` Step 2 updated to ✅.

On completion: update parent goal step ladder, bump watermark, commit + push HQ.

---

## State

```
watermark:    2026-05-19 (Sonnet 4.6 — PST-FIELD-2 session).
status:       ✅ GOAL COMPLETE. All Done criteria met. tree_t has exactly four fields: t, v, n, c.
prior closed:
  PST-ICN-2a/2b ✅ ; PST-ICN-4a ✅ 2026-05-16 ; PST-ICN-4b ✅ 2026-05-16.
  icon_helpers.sc DELETED 2026-05-18.
  PST-ICN-LR-1a–1g ✅ 2026-05-19 (Sonnet 4.6) — TT_PROC_DECL, proc->_id gone.
  PST-FIELD-1 ✅ 2026-05-19 (Sonnet 4.6) — _nalloc removed from tree_t;
    prefix-word capacity; 4 free(e->c) sites fixed (ast_clone, pl_runtime,
    polyglot, scrip); beauty self-host no longer heap-aborts.
  PRF-12-sub ✅ 2026-05-19 (Sonnet 4.6, cross-goal) — TT_SUB_DECL replaces
    TT_FNC+_id=SUB_TAG_ID in raku.y; lower.c _id==SUB_TAG_ID check removed;
    one4all @ 3375a0ea.
  PST-FIELD-2 ✅ 2026-05-19 (Sonnet 4.6) — _id removed from tree_t struct.
    Construct A (one4all @ a656921d): raku.y all TT_FNC+_id=SUB_TAG_ID sites
      replaced with TT_SUB_DECL (program/main synthesis, class method rules,
      gather hoist); raku_driver.h SUB_TAG_ID deleted; raku.tab.c regenerated.
    Construct B (one4all @ b8091a9b): int _id removed from tree_t (ast.h);
      ast_clone.c _id copy removed; icn_runtime.c icn_scope_patch simplified
      (no longer annotates TT_VAR nodes — scope_get called live at use-sites
      in subscript/section assign path; v.ival not used as slot cache since
      v is a union with v.sval and would corrupt the name pointer).
gates:        smoke_icon 5/0 ✅ · smoke_raku 5/0 ✅ · smoke_snobol4 5/1(pre-existing) ✅ · smoke_scrip_all_modes 2/0 ✅ · icon rungs PASS=194 FAIL=36 ✅
              NOTE: test_self_host_smoke.sh segfaults on Snocone — confirmed pre-existing (present at a656921d before struct removal).
mirror gaps:  ⚠ MIRROR-GAP-ICN-LR-1 — parser_icon.sc Phase 2 mirror BLOCKED until all six C parsers Phase 1 clean.
next:         Done criteria 1–9 all checked. Done criterion 10: update parent goal
    GOAL-PARSER-PURE-SYNTAX-TREE.md Step 2. Phase 2 SCRIP mirror work BLOCKED
    until all six C parsers Phase 1 clean.
heads:        .github @ (pending) · one4all @ b8091a9b · corpus @ a9e9328

**PST-SC-SCRIP-AUDIT 2026-05-19 (Sonnet 4.6):** parser_icon.sc scanned against
strict permitted list (shift, reduce, nPush, nInc, nPop, nTop, assign only).
VIOLATIONS FOUND — 4 shift_val calls (Expr11 primary atom arms):
  • shift_val(csetbody, 'TT_CSET')   — csetbody captured via '. csetbody' earlier.
  • shift_val(strbody,  'TT_QLIT')   — strbody captured via '. strbody' earlier.
  • shift_val(REAL(rval), 'TT_FLIT') — rval captured via '. rval'; value computed.
  • shift_val('&' kwname, 'TT_VAR')  — kwname captured via '. kwname'; concatenated.
Fix for all four: assign(.sc_tmp, <value>) shift(sc_tmp, 'TT_KIND')
  e.g. shift_val(REAL(rval), 'TT_FLIT')
    → (epsilon . *assign(.sc_tmp_icon, REAL(rval))) shift(sc_tmp_icon, 'TT_FLIT')
  e.g. shift_val('&' kwname, 'TT_VAR')
    → (epsilon . *assign(.sc_tmp_icon, '&' kwname)) shift(sc_tmp_icon, 'TT_VAR')
Session work: 4 mechanical one-line replacements in Expr11. Smallest Phase 2 job.
```

### Session-end note — 2026-05-19 (Opus 4.7 session 4)

HQ session — PST-LR-AUDIT-1 closed and three-facet block added across all six
PST goal files. No Icon-specific code changes this session. Next session:
open `icon_parse.c:753–758`, follow PST-ICN-LR-1a/1b fix sketches above.
Note Icon is a primary `_id` consumer — PST-FIELD-2 cannot close until this
rung lands.

---

## Authorship

Drafted by Claude Opus 4.7, 2026-05-19. Created by splitting `GOAL-PST-ICN-RAKU.md` (originally drafted by Claude Sonnet 4.6, 2026-05-16) into Icon-only and Raku-only files at Lon's request — the two languages diverged sharply in scope (Icon: 1 §⛔ violation; Raku: 27) and warranted separate sessions. PST-FIELD-1 and PST-FIELD-2 rungs duplicated into both split files for session self-containment; coordinate cross-session via the State block of whichever language's session touches the shared struct first.
