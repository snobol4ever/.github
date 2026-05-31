# HANDOFF — 2026-05-27 — Opus 4.7 — GOAL-ICON-BB: LFJ (LOWER FROM JCON) staircase begun

**SCRIP** `f79ea9ba` · **.github** `bcf38418` · **goal:** GOAL-ICON-BB · **mode priority:** mode 2 then mode 3

---

## WATERMARK

GATES: smoke_icon **5/5** · broker **24** · rungs **198** · smoke_prolog **5/5** — ALL UNCHANGED

---

## ⛔ CONTEXT FOR NEXT SESSION (READ THIS FIRST)

The AG-PURE staircase (steps 1 through 8.2) was the **wrong substrate**. Lon
identified this mid-session — `LOWER-REWRITE-FROM-JCON.md` in `.github` is the
authoritative directive document, **issued 4 times** by Lon, that the previous
attempts kept failing to honor. The directive: do **NOT** patch the
`lower_icn_expr_node` mega-switch with intercept branches and discriminator
markers (`nd->ival = 1`, sval "ag"/"ai"/"ar"). Instead transcribe `irgen.icn`'s
`ir_a_*` procedures directly into C, building a new lowerer from the ground up.

AG-PURE 1–8.2 stay in the tree as the **legacy green-gate baseline** but no new
work goes into that substrate. They are frozen at `7acc7849`.

The LFJ (LOWER FROM JCON) staircase now supersedes AG-PURE. See
`GOAL-ICON-BB.md` for the full 17-rung definition.

**THE PERSONAL FAILURE TO ACKNOWLEDGE:** This session began by faithfully
executing the prior handoff's "Step 8.2-followup" — adding yet another
TT_ASSIGN-wrapped routing branch to `lower_icn_expr_threaded_b`. That was
the 4th repeat of the anti-pattern. Lon caught it. The branch was reverted
(it never got committed to SCRIP). The LFJ staircase is the corrected path.

---

## WHAT WAS DONE THIS SESSION

### LFJ-0 ✅ `.github` `bc7dae2a`

Created `LOWER-IRGEN-MAPPING.md` — the authoritative mapping document from
JCON's `irgen.icn` model to SCRIP's port-graph BB model. 306 lines, 10
sections. Covers:

- §2 — the four labels (start/resume/failure/success) ↔ four ports (α/β/γ/ω)
- §4 — every JCON `ir_*` record → matching SCRIP `BB_op_t` enum value (table)
- §5 — JCON helper procedures → C helper functions
- §6 — why SCRIP's lowering signature omits `inuse`, `target`, `rval`
- §7 — the `lower_kind_table[TT_MAX]` dispatch machinery
- §9 — 5 open questions (Q1–Q5) deliberately deferred to the rung that needs them

**This document is the contract.** Every LFJ rung must consult it. If a
transcription cannot be expressed via the mappings, STOP and update the
mapping first — do not invent new shape on the BB substrate.

### LFJ-1a-i ✅ `SCRIP` `f79ea9ba`

Mechanical extraction of 9 leaf cases from `lower_icn_expr_node`'s mega-switch
into `static BB_t *lower_icn_legacy_<KIND>(BB_graph_t *cfg, tree_t *e)` functions.
ZERO logic change. Switch arms collapse to one-line dispatches:

```c
case TT_ILIT:    return lower_icn_legacy_ILIT(cfg, e);
case TT_FLIT:    return lower_icn_legacy_FLIT(cfg, e);
... [9 cases]
```

Extracted: TT_ILIT, TT_FLIT, TT_QLIT, TT_CSET, TT_VAR, TT_KEYWORD, TT_LOOP_BREAK,
TT_LOOP_NEXT, TT_PROC_FAIL.

All four gates green and unchanged. Rebased onto concurrent commits (`471ab202`
CAT-A-2 and `2b68dc44` SBL-DCG-DEFER) cleanly — zero file overlap.

### HQ updates ✅ `.github` `bcf38418`

GOAL-ICON-BB.md staircase split: LFJ-1a became 6 sub-rungs (1a-i through 1a-vi)
so each commit is small enough to verify mechanically. PLAN.md row updated with
current commit hash and next step pointer.

---

## STAIRCASE STATE (from GOAL-ICON-BB.md, abbreviated)

| Rung | Scope | Status |
|------|-------|--------|
| LFJ-0    | mapping doc                                                       | ✅ `bc7dae2a` |
| LFJ-1a-i | extract 9 leaf cases (ILIT, FLIT, QLIT, CSET, VAR, KEYWORD, LOOP_BREAK, LOOP_NEXT, PROC_FAIL) | ✅ `f79ea9ba` |
| LFJ-1a-ii | extract TT_SCAN, TT_ASSIGN, TT_SWAP, TT_FNC, TT_SEQ, TT_SEQ_EXPR | **NEXT** |
| LFJ-1a-iii | extract TT_IF, TT_TO, TT_TO_BY, TT_EVERY, TT_WHILE, TT_UNTIL, TT_REPEAT, TT_LIMIT | pending |
| LFJ-1a-iv | extract binop group (TT_ADD..TT_NE, TT_CAT, TT_LCONCAT, TT_LLT..TT_LNE), TT_NOT, TT_ALTERNATE, TT_AUGOP | pending |
| LFJ-1a-v  | extract TT_GLOBAL/LOCAL/STATIC_DECL, TT_INITIAL, TT_RETURN, TT_SUSPEND, TT_IDENTICAL, TT_NONNULL, TT_NULL, TT_RANDOM, TT_MATCH_UNARY, TT_MNS, TT_PLS, TT_CSET_*  | pending |
| LFJ-1a-vi | extract TT_SIZE, TT_IDX, TT_SECTION/SECTION_PLUS/SECTION_MINUS, TT_CASE, TT_FIELD, TT_RECORD, TT_MAKELIST, TT_ITERATE — mega-switch now pure dispatcher | pending |
| LFJ-1b   | introduce `lower_kind_table[TT_MAX]`, populate via `lower_kind_table_init()` | pending |
| LFJ-1c   | create empty `lower_icn_new.c` + `lower_icn_new.h`, wire into build | pending |
| LFJ-2 .. LFJ-14 | transcribe `ir_a_*` procedures from `irgen.icn`, one or more per rung, flipping table slots | pending |
| LFJ-15   | delete `lower_icn.c`, rename `lower_icn_new.c` → `lower_icn.c`, remove table indirection, sweep AG-PURE intercept branches from `lower_icn_expr_threaded_b` | pending |

---

## EXACT NEXT STEP — LFJ-1a-ii

**Extract:** TT_SCAN, TT_ASSIGN, TT_SWAP, TT_FNC, TT_SEQ, TT_SEQ_EXPR

**Where:**
- TT_SCAN: lines 182–196 in `src/lower/lower_icn.c`
- TT_ASSIGN: lines 197–244 (the largest of the batch — three sub-forms: FIELD lhs, IDX lhs, VAR lhs)
- TT_SWAP: lines 245–262
- TT_FNC: lines 263–341 (substantial — TT_FNC has builtin-vs-user dispatch and arg odometer setup)
- TT_SEQ: lines 634–651
- TT_SEQ_EXPR: lines 488–513

**Method:** Use the same pattern as LFJ-1a-i:
1. Add `static BB_t *lower_icn_legacy_<KIND>(BB_graph_t *cfg, tree_t *e)` definitions above `lower_icn_expr_node` (insert after the LFJ-1a-i extracted functions, before the comment separator that introduces the dispatcher).
2. Each function body is the **verbatim** case body, with `return nd;` instead of `return X` from the switch context (already that way in most cases).
3. Replace each switch arm with a one-line `case TT_<KIND>: return lower_icn_legacy_<KIND>(cfg, e);`
4. Build, run gates, confirm 198 rungs.

**Watch-out for LFJ-1a-ii specifically:**
- TT_FNC at line 263 is ~80 lines — it allocates several BB nodes and threads args. Extract as one block, do not split. The function uses local helpers (`is_suspendable`) — those stay at file scope.
- TT_ASSIGN at line 197 has three sub-cases (FIELD/IDX/VAR). One extracted function, three internal branches.
- TT_SEQ_EXPR at line 488 is straightforward but uses a buffer — keep its locals inside the extracted function.

**Gate after the commit:**
```bash
cd /home/claude/SCRIP
bash scripts/build_scrip.sh                       # OK
bash scripts/test_smoke_icon.sh                   # PASS=5
bash scripts/test_icon_all_rungs.sh               # PASS=198
bash scripts/test_smoke_prolog.sh                 # PASS=5
bash scripts/test_smoke_unified_broker.sh         # PASS=24
```

If any gate slips below the watermark, the extraction has logic drift. Revert,
diff against `f79ea9ba`, and re-extract more carefully. There should be no
divergence — these are mechanical lifts.

---

## ARCHITECTURAL NOTES (CRITICAL — DO NOT SKIP)

### Why the discriminator-marker pattern is forbidden

The AG-PURE substrate uses `nd->ival = 1` (BB_EVERY passthrough), `nd->sval =
"ag"`/`"ai"`/`"ar"` (BB_TO/BB_TO_BY dynamic-bounds AG-pure mode), and PEERS
sidecar `bb_operand_aux_set` to layer "deep-threaded" behavior on top of the
legacy `lower_icn_expr_node` switch. Each one of these is a **discriminator
flag** — a bit on `BB_t` that says "interpret me using mode X instead of mode Y."

`LOWER-REWRITE-FROM-JCON.md` rejects this pattern explicitly. Reason: every
discriminator marker is one more way the executor can branch behaviorally
based on lowering-mode metadata that shouldn't exist if the lowering was
faithful to `irgen.icn` in the first place. JCON's IR has zero such markers —
every behavioral distinction is structurally encoded (different chunk shape,
different label wiring). SCRIP's port-graph equivalent should be the same:
behavioral distinctions live in **which BB_t kinds and which port wiring**,
not in flag fields.

LFJ rungs 2 through 14 must produce `lower_icn_new_<Kind>` functions that
**never** set `nd->ival`, `nd->sval`, or `nd->state` as a behavior selector.
Those fields carry IR payload (literal values, names) only.

### The PEERS sidecar question

`bb_operand_aux_set/get` is currently used by ICN-Z-ATOMIC Family 1 (BB_ASSIGN)
and Family 2 (BB_CALL) to carry operand references off `BB_t` (PEERS RULE,
HQ Invariant 17). LFJ-2..LFJ-14 will need to decide for each transcribed kind:
keep using the sidecar, or use the cfg ring (AG-PURE step 2 onward), or
something else.

**Recommended convention:** LFJ-2..14 use the **cfg ring** by default
(`ag_ring_push`/`ag_ring_peek`) for operand value flow. The sidecar stays
available for cases the ring cannot cleanly handle, but those cases must be
documented in `LOWER-IRGEN-MAPPING.md` first.

### What "frozen" means for AG-PURE

The AG-PURE intercept branches in `lower_icn_expr_threaded_b` at lines 1237
(BB_ASSIGN), 1259 (BB_CALL), 1305 (BB_BINOP), 1338 (BB_TO), 1355 (BB_TO_BY),
1382 (BB_IF), 1404 (BB_CONJ), 1426 (BB_ALT), 1478 (BB_EVERY) — these are NOT
to be touched during LFJ-1 through LFJ-14. They keep the gates green for kinds
not yet transcribed.

When LFJ-N transcribes a kind, the new function exists in `lower_icn_new.c`,
but `lower_icn_expr_threaded_b` still intercepts. That's OK — the threaded_b
intercepts wrap `lower_icn_expr_node`, which now dispatches through
`lower_kind_table`, which points at either legacy or new. As long as the new
function produces a graph that the threaded_b intercept can layer its
port-wiring on top of, no friction.

**At LFJ-15**, the threaded_b intercepts get swept out wholesale — by then,
every kind's new function does its own port wiring during lowering (the
JCON way), and threaded_b becomes a thin pass-through that just calls into
`lower_kind_table` and stamps inherited γ_in/ω_in onto the returned node.

---

## SESSION SETUP (for next session)

```bash
git clone https://TOKEN@github.com/snobol4ever/.github  /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/SCRIP  /home/claude/SCRIP
git clone https://TOKEN@github.com/snobol4ever/corpus   /home/claude/corpus
cd /home/claude/SCRIP
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
git remote set-url origin https://TOKEN@github.com/snobol4ever/SCRIP.git
cd /home/claude/.github
git remote set-url origin https://TOKEN@github.com/snobol4ever/.github.git

# JCON source (if not in /home/claude/jcon-master already from upload):
#   irgen.icn at /home/claude/corpus/programs/icon/jcon-ref/irgen.icn (the procedures)
#   ir.icn    at /home/claude/jcon-master/tran/ir.icn                 (the record defs)
# Both are also reachable at https://github.com/proebsting/jcon

cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
bash scripts/test_smoke_icon.sh             # PASS=5
bash scripts/test_icon_all_rungs.sh         # PASS=198
bash scripts/test_smoke_prolog.sh           # PASS=5
bash scripts/test_smoke_unified_broker.sh   # PASS=24

# Read in this order before writing any code:
cat /home/claude/.github/PLAN.md
cat /home/claude/.github/RULES.md
cat /home/claude/.github/GOAL-ICON-BB.md
cat /home/claude/.github/LOWER-REWRITE-FROM-JCON.md
cat /home/claude/.github/LOWER-IRGEN-MAPPING.md       # the LFJ-0 contract
cat /home/claude/.github/HANDOFF-2026-05-27-OPUS-LFJ-1A-I.md  # this file

# Then start LFJ-1a-ii (mechanical extraction; see "EXACT NEXT STEP" above).
```

---

## DO NOT (still applies)

- Do not touch SNOBOL4 / Snocone / Rebus / Raku / Prolog lower or BB families.
- Do not edit `lower_icn.c` (the mega-switch) except for the LFJ-1a sub-rung
  extractions and LFJ-1b's dispatcher rewrite.
- Do not add discriminator markers (`nd->ival = N`, sval tags) in new code.
- Do not add `_threaded_b`-style intercept branches to legacy code as a
  workaround. Those exist; don't add more.
- Do not build a "comparator" or "shadow graph." There is one graph, one
  table-slot per kind. (This was explicitly rejected by Lon earlier this
  session — see chat log.)
- Do not resume AG-PURE work below until LFJ-15 lands.
- Do not extract more than one batch of cases per commit. The whole point of
  splitting LFJ-1a into sub-rungs is to keep each commit small and reviewable.

---

## ACCEPTANCE PROGRESS (whole LFJ)

From GOAL-ICON-BB.md, the macro acceptance is: at LFJ-15, `lower_icn.c` is
deleted, `lower_icn_new.c` is the only Icon lowerer, the `_threaded_b`
intercept branches are gone, and rungs PASS≥198 holds.

**Today's contribution:** the substrate refactor began. 9 cases out of ~50
extracted from the mega-switch into named static functions. The dispatcher
collapses to one-line arms. No behavior change.

**Path to LFJ-15:** ~5 more LFJ-1a sub-rungs (mechanical), then LFJ-1b (table),
LFJ-1c (new-file stub), then 13 transcription rungs (LFJ-2 through LFJ-14),
then LFJ-15 sweep. Each rung is one commit, gates checked.

---

**.github** `bcf38418`  ·  **SCRIP** `f79ea9ba`

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7
