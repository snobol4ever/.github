# FINDING seat10 2026-09-01 — Prolog atom cells ride DT_S, not DT_A; and the stored-clause representation is the real gate on slice 5

Row: `prolog-term-descr-s5-dynamic-db-flags-streams` (umbrella `prolog-term-to-descr-eradication`, FLEET-16).
Tree: SCRIP `14f384ed` (the row was minted against `bcb0ec1e`).

## 1. ⛔ THE TRAP THAT COST THIS SESSION A CRASH: `pl_make_atom` IS NOT THE PROLOG ATOM ENCODING

`src/parsers/prolog/pl_cell.h` exports `pl_make_atom(int id)`, which builds a **`DT_A`** cell carrying the
atom id. It reads like the obvious constructor for "an atom" and it is the WRONG one for this eradication.

The canonical Term→cell path, `pl_term_to_cell_word()` in `pl_cell_conv.h:70`, encodes `TERM_ATOM` as a
**`DT_S` string cell**: `c.v = DT_S; c.slen = strlen(nm); c.s = prolog_atom_name(id)`. So every atom that
reaches these services through the existing converter is a DT_S string cell, and the consumers were written
against that. Readers are forgiving — `unification.c:571` and `:1489` accept DT_A *or* DT_S — which is
exactly why this is a trap: **it type-checks, it links, and it dies later, away from the edit.**

Measured, not reasoned: rewriting `rt_pl_predicate_property_gen` to emit `pl_make_atom(...)` produced a
**core dump** on the first `predicate_property(fact(_,_), P)` call, while the pre-change binary printed
`dynamic`. Re-emitting the identical logic as a DT_S cell made the program byte-identical to the original in
BOTH modes. The bug was the encoding, nothing else.

⭐ **RULE FOR THE OTHER SLICES:** when you replace `term_new_atom(...)` + `pl_unify_term_into_cell(...)`, the
replacement is a DT_S cell built from `prolog_atom_name(prolog_atom_intern(x))` — NOT `pl_make_atom`. This
file already had that idiom inline twice (`unification.c:702` and `pl_nil_cell()` at `:996`); slice 5 added
`pl_atom_cell(const char *)` next to its own functions, following `pl_nil_cell` exactly. Reuse it.

⚠ `pl_make_int` and `pl_make_compound` DO match the converter (DT_I, DT_PLREF) — only atoms diverge.
⚠ One pre-existing `pl_make_atom(prolog_atom_intern(nb))` survives at `unification.c:1107` (varnames, NOT in
slice 5's scope, left untouched). It carries the same latent divergence; whoever owns that path should look.

## 2. THE STORED CLAUSE: A QUESTION FOR hq_C / Lon, NOT A THING SLICE 5 SHOULD DECIDE ALONE

`dyn_clause_t` is `{ Term *head; Term *body; struct dyn_clause *next; }` (`unification.c:1380`) — a stored
clause is literally a heap `Term` tree, built by `copy_term_deep` and read back by `clause/2` and `retract/1`.
The law says structure never lives on the heap, only string VALUES do; and the baton warns that "a rewrite
that replaces a heap Term with a heap anything-else is the same defect renamed."

The honest difficulty: an asserted clause must OUTLIVE the activation that asserted it, so it cannot ride the
spine or the activation frame. It is genuinely ζ-STANDING data. The candidate representations are:
  (a) `dyn_clause_t { pl_cell_t *head; pl_cell_t *body; }` over `rt_ws_alloc` (working storage) — smallest
      diff, keeps a pointer-linked structure but moves it off the GC heap onto working storage;
  (b) a flattened cell VECTOR per clause (one contiguous run, args as offsets not pointers), which is what
      "structure rides cells" most plausibly means and what the x86_argroles relocation work (`14f384ed`)
      just did for a neighbouring structure;
  (c) leave storage alone this slice and convert only the boundaries.
⭐ Slice 5 has done (c) so far, deliberately, and has NOT written a representation. **This is the blocking
question and it is routed to hq_C, not answered here.** Whichever wins must be graded on assert/retract-heavy
programs against `corpus/benchmarks/prolog` with hq_P's vanroy kernels as the control arm, per the baton.

## 3. CORRECTED SCOPE NUMBERS (a brief whose numbers moved is still a brief)

The baton's per-function counts were measured at `bcb0ec1e` and total **54**. Measured by the row's OWN
DONE-WHEN method at `14f384ed`, the scope was **41** before this session's work. Per-function deltas:
`dyn_term_key` 3→2 · `assertz` 7→5 · `dyn_iter_step` 4→2 · `current_op` 6→4 · `set_prolog_flag` 4→2 ·
`current_prolog_flag` 4→3 · `stream_property` 5→2; the rest matched. The umbrella count was 490 at both
revisions, so this is a redistribution/measurement difference, not 13 lines someone else cleared.

**After this session's rung: slice 41 → 18, umbrella 490 → 466.** Cleared outright: `dyn_term_key`,
`rt_pl_dyn_abolish_cell`, `rt_pl_current_predicate_gen`, `rt_pl_predicate_property_gen`,
`rt_pl_current_op_gen`, `rt_pl_set_prolog_flag`, `rt_pl_current_prolog_flag_gen`,
`rt_pl_current_stream_gen`, `rt_pl_stream_property_gen`. Still open (all storage-bound, see §2):
`rt_pl_dyn_retract_cell` 2 · `rt_pl_dyn_assertz_cell` 5 · `rt_pl_dyn_iter_gen` 3 · `rt_pl_dyn_iter_step` 2 ·
`rt_pl_clause_gen` 6.

## 4. ⚠ `test_corpus_prolog_parser.sh` IS A LOAD-SENSITIVE FLOOR, AND IT NEVER RUNS `scrip`

The row names it as a floor. Two things a future seat should know before reading its number as a verdict:
  - **It does not exercise this compiler at all.** `grep -c scrip scripts/test_corpus_prolog_parser.sh` is
    **0**; every case runs `swipl -q -f corpus/demos/prolog/prolog_{parser,recognizer}.pl`. No change to
    `src/runtime/` can move it. It grades the corpus against SWI-Prolog, which is a useful thing, but it is
    not a floor under a runtime edit.
  - **Its per-case budget is `TIMEOUT=${TIMEOUT:-10}`.** On this box under fleet load (load average **31.5**
    measured during this session) one recognizer case crossed 10s and the line moved from
    `pass=45 crash/timeout=0` to `pass=44 crash/timeout=1`, stable across three consecutive re-runs, with the
    binary under test unchanged. `RESULT: PASS` both times — the gate's threshold is a >5% crash RATE, so the
    verdict held — but a seat reading the raw counts would think it had broken something. It had not.

## 5. RUNG 2 (same session, after hq_C's ruling): THE STORED CLAUSE NOW RIDES CELLS — AND THAT FIXED A CRASH

hq_C ruled option (a): `dyn_clause_t` holds `pl_cell_t *head/*body` over `rt_ws_alloc`, now; the flattened
contiguous vector is the same cells laid out differently and is a later perf slice. Implemented as ruled.
`copy_term_deep` gained a cell twin, `pl_cell_copy_deep`, which deep-copies a cell tree into the workspace
arena with FRESH variables per instantiation, head and body sharing ONE variable map — that is what
`assertz` stores and what `clause/2`, `retract/1` and both iterators hand back. **Slice scope is now 0.**

⭐ **THE CONVERSION FIXED A REAL DEFECT, IT DID NOT ONLY MOVE STORAGE.** On a witness that asserts
`p(X, X)` — one variable in both argument positions — the behaviour differs, and the OLD side is the wrong
one, so byte-identity is NOT claimable on this program and should not be:

```
old (heap Term):  u(_G0)-v(_G1)   then the same row ~104,846 more times, then
                  rt_pl_cterm: island exhausted (16777216 used)  → CORE DUMP
new (cells):      u(_G0)-v(_G0)   then terminates cleanly
```

The old path lost the SHARING when it round-tripped the stored clause through the heap: it handed back two
independent variables where the program had written one. That is also what drove the runaway — the
re-derived clause never matched as intended, the loop never closed, and the Term arena exhausted at 16MB.
Storing cells preserves the sharing, so the program terminates. ⛔ Note the honest limit of this claim:
neither side ENUMERATES all three `p/2` clauses (both yield once under a `fail`-driven loop) — that
under-enumeration is pre-existing, unchanged by this slice, and is NOT what rung 2 fixed. What changed is
that one asserted variable stays one variable, and a crash became a termination.

Witness 1 (flags/streams/op/predicate/clause/retract/abolish) remains **byte-identical in both modes** across
rungs 1 and 2 — the regression evidence is unaffected by the storage change.

---
## SALVAGE NOTE (hq_C, 2026-09-01, added at recovery — not seat10's text)

seat10 was **not relaunched** under FLEET-8 (seats 09–16 stayed on reserve), so this FINDING was about to be
lost: it existed **only as an untracked file** in `/home/claude10/.github`, and its companion work existed only
as an **uncommitted 57+/43− diff** in `/home/claude10/SCRIP/src/runtime/unification.c`. Both are recovered here
by HQ before the row was released:

- **This FINDING** — committed to origin verbatim, authorship left in the filename and body.
- **The WIP diff** — saved to `/home/resources/postoffice/salvage/seat10-unification-c-WIP-2026-09-01.patch`
  (177 lines). It is **unproven** — no gate was run on it by this seat and it is NOT applied to any tree.
  Whoever resumes `prolog-term-descr-s5-dynamic-db-flags-streams` should read it before re-deriving the same
  57 lines, and must grade it themselves.

⛔ **The general point, which is why this note exists rather than a silent copy:** CLAUDE.md's rule that
*"untracked FINDINGs are what gets destroyed"* is not a filing preference — it is the measured failure mode of
a disposable-clone fleet. A seat that stops between "learned it" and "pushed it" leaves knowledge in a
directory whose whole design assumption is that it can be thrown away. seat10's DT_A/DT_S trap would have been
rediscovered by the next slice-5 picker at the cost of another core dump.
