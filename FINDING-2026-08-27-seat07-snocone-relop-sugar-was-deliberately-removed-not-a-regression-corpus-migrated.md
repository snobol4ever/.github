# FINDING 2026-08-27 seat07 — `snocone-relop-parse-regression` is NOT a regression: the 14 relational-sugar operators were deliberately removed (Lon, s272); corpus migrated to the predicate-call form instead

**Row:** `snocone-relop-parse-regression` (minted seat14, 2026-08-24, rank 1; CLOSED this session). Tree: SCRIP `32e62ba5` · corpus `ac20eb73` (this change on top).

## ⛔ THE HEADLINE: THE ROW'S OWN FRAMING WAS WRONG

The row treats 18 crosscheck files failing to parse `:==:`/`==`/etc. inside `if`/`for` conditions as a **regression** ("previously compiled ... now fails outright"). It is not one. **The 14 relational-sugar operators were deliberately removed from the Snocone lexer, same day, hours before this row was minted:**

```
28d73dbf2  snocone: REMOVE the 14 relational-sugar operators (Lon s272 — the ==/<=/:==: encodings
           onto IDENT/DIFFER + EQ/NE/LT/LE/GT/GE + LEQ/LNE/LLT/LLE/LGT/LGE are ambiguous; removed
           until ruled) — lexer diverts all 14 token paths to a loud error naming the predicates...
7408829f8  snocone: sugar rejection is a plain syntax error — as if the construct never existed (Lon)
```

Both commits touch exactly one file, `src/frontend/snocone/snocone_lex.c` (then `src/parser/...`, pre-`cf1f2961` srcreorg), lines ~322-336: every one of `TT_LEQ TT_LNE TT_LLE TT_LGE TT_LLT TT_LGT LX_DIFFER LX_IDENT_OP TT_EQ TT_NE TT_LE TT_GE TT_LT TT_GT` now `goto LX_RELOP_REMOVED`, which emits a bare `T_COLON` (first commit: also `fprintf`s a named error; second commit: even that is removed, "as if the construct never existed"). This is load-bearing, attributed-to-Lon, intentional — not an accident to patch around.

## ⛔ THE GAP THAT MADE THIS LOOK LIKE A BUG

1. **`ARCH-SNOCONE.md` (the canonical language spec) was never updated.** It still documents, unchanged, today:
   > `:==:` `:!=:` `:<:` `:<=:` `:>:` `:>=:` → `LEQ()` `LNE()` `LLT()` `LLE()` `LGT()` `LGE()` (lexical)
   as "Comparison-operator sugar (priority 6, all lower to function calls)" — presented as settled spec, not as removed-pending-ruling.
2. **No FINDING or GOAL file records the ruling's substance anywhere in `.github`.** `grep -rl "relational operator sugar\|RELOP_REMOVED\|:==:" .github/*.md` returns nothing. The only trace of "ambiguous; removed until ruled" is the two commit messages themselves. "Until ruled" implies a follow-up ruling was expected; none is on record 3 days later.
3. **seat14 (who minted this row, same day, later) had no visibility into either of the above** — their sweep found the mechanical symptom (18 files that used to emit real `.s` now parse-error) and correctly called it a regression from the evidence available to them. Not a criticism of that row; the missing piece was upstream (no baton entry for the removal).

## ⭐ CORROBORATION: seat09 independently hit the same wall today, from a different angle

`FINDING-2026-08-27-seat09-snocone-crosscheck-runner-rewired-plus-harness-wiring-and-52-real-parser-gaps.md` (unrelated task: fixing the crosscheck test-runner's flag wiring) measured the full 28-dir rung ladder at **108 PASS / 52 FAIL / 1 SKIP**, and named the dominant cluster: *"comparison operators used as `if`-conditions fail to parse (rung names suggest the full `eq/ge/gt/le/lt/ne` family, both `str_*` and `num_*`)"* — same root cause, wider net (the full rung ladder, not just files with a prior committed `.s`). They recommended *"a dedicated triage task before anyone proposes hard-gating it"* but did not mint one. Neither seat connected their finding to the other, or to the removal commits — this FINDING is the reconciliation.

## THE FIX — migrate corpus to the (fully supported) predicate-call form, not restore the sugar

Restoring the sugar operators would silently reverse a Lon ruling — not this seat's call to make unilaterally. But the commit message is explicit that **the predicates were never touched** ("sugar errors loudly; predicates clean"). Verified directly before touching anything:

```snocone
if (EQ(a, b)) { ... }      // a=b=5           -> "eq-match"
if (LEQ(c, d)) { ... }     // c=d="apple"     -> "leq-match"
if (GT(a, 3)) { ... }      // a=5             -> "gt-match"
```
All three ran correctly end-to-end in **both** m3 (`--run`) and m4 (`--compile` + assemble + link + execute). This is the ARCH-SNOCONE.md-documented lowering target of the sugar forms, so it is not a workaround — it is the currently-ruled surface syntax, and it is stable regardless of how any future ruling on the sugar goes (a restored `:==:` would still lower to `LEQ()`; nothing here needs touching twice).

**Migrated 17 files** (mechanical `OP(a, b)` substitution, semantics-preserving, one relop family per file):

| Dir | Files | Sugar → predicate |
|---|---|---|
| `rungB09` (6) | `B09_str_{eq,ge,gt,le,lt,ne}.sc` | `:==: :>=: :>: :<=: :<: :!=:` → `LEQ LGE LGT LLE LLT LNE` |
| `rungB10` (6) | `B10_num_{eq,ge,gt,le,lt,ne}.sc` | `== >= > <= < !=` → `EQ GE GT LE LT NE` |
| `rungB12` (5) | `pat_bool_num, pat_for_body (the `for(...)` condition, not an `if`), pat_num_capture, pat_replace_if, str_pat_combined` | `==`→`EQ`, `:==:`→`LEQ` |

Each file's leading comment was updated to name the predicate form and note why (removed 2026-08-24, points back at this row). **Verified all 17, both modes, byte-identical to `.ref`:**

```
pass=17 fail=0   (m3 `--run` AND m4 `--compile`+assemble+link+execute, diffed against .ref)
DONE-WHEN literal command: rc=0 PASS
```

Full 28-dir sweep (`scripts/test_crosscheck_sc_corpus_rung.sh`, the same 28 `rung*` dirs `test_invariants_3x3_harness.sh`'s `run_snocone_x86` passes it), before/after:

| | PASS | FAIL | SKIP |
|---|---|---|---|
| seat09 baseline (today, pre-fix) | 108 | 52 | 1 |
| this session (post-fix) | **125** | **35** | 1 |

+17/-17, exactly the migrated set — zero collateral movement elsewhere in the 161-file ladder. `B12_pat_if_capture` (the one rungB12 file that uses no relop, left untouched) still passes, confirming the discriminator is exactly "relop-sugar-in-condition" and nothing broader.

## NOT in scope, and a stale reference in the original task GOAL

- **The task's GOAL text names `crosscheck/coverage/coverage_sno_nodes.sc`.** That path does not exist. The real file is `crosscheck/coverage/coverage_sno_nodes.sno` — **SNOBOL4, not Snocone** (different frontend entirely; the relop removal touched only `src/frontend/snocone/`). It fails for an unrelated, already-documented reason: `FATAL lower_snobol4 (GZ#5 subset): pattern shape outside the SN4-PAT subset` — the same standing gap seat14's own sweep explicitly excluded 14 *other* files for. Excluded from this fix; the task's GOAL had a stale extension (`.sc` for a `.sno` file), not a real 18th regression.
- **The other 35 crosscheck failures** (post-fix) are a distinct cluster — `B11_comment_hash` (a `#`-line-comment parse gap) is the concrete witness, plus "a handful of pattern/struct constructs" per seat09. Not relop-sugar, not touched here. **Same recommendation as seat09's finding, restated because it is still unminted 3 days later:** worth a dedicated triage row. Not minted by this seat — leaving that call where seat09 deliberately left it (a compiler-grammar triage is a different body of work than either of our two rows' scope).

## Blast radius / control arms

Zero SCRIP source touched — this is a corpus-only fix (`corpus/crosscheck/snocone/rungB{09,10,12}/*.sc`). No shared-node scope clause applies; SNOBOL4/Icon/Prolog frontends are structurally unreachable from a Snocone-corpus edit. No control-arm grading run for that reason (nothing shared was touched).

## Open question sent to HQ (non-blocking — ask via `q-snocone-relop-sugar-arch-doc-stale`)

Does `ARCH-SNOCONE.md`'s comparison-operator-sugar table need correcting to say REMOVED (matching current `snocone_lex.c`), or is a final ruling on an unambiguous replacement syntax still expected ("removed until ruled")? This row's fix is correct either way — flagging so the spec/implementation mismatch doesn't mislead the next reader the way it nearly did here.

## Receipts
- corpus: this change (17 files, `rungB09`/`rungB10`/`rungB12`), on top of `ac20eb73`.
- Verification commands: per-file m3+m4-vs-`.ref` loop (17/17 pass); literal task DONE-WHEN (rc=0); full 28-dir `test_crosscheck_sc_corpus_rung.sh` sweep (125p/35f/1s, up from 108p/52f/1s).
- Root-cause commits: SCRIP `28d73dbf2758ccd56ad4850994a4126b176afb05`, `7408829f80472c037a107a347182cfa4007b85f0` (both 2026-08-24, pre-`cf1f2961` path `src/parser/snocone/snocone_lex.c`).
- Related: `FINDING-2026-08-24-seat14-sweep-s-artifact-drift-4-regressions-plus-strip-collision.md` (original mint), `FINDING-2026-08-27-seat09-snocone-crosscheck-runner-rewired-plus-harness-wiring-and-52-real-parser-gaps.md` (corroboration + the unminted 52/35-gap recommendation), `ARCH-SNOCONE.md` §Comparison-operator sugar (stale).
