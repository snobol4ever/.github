# FINDING 2026-09-16 hq_snocone — defect B is NOT a Snocone defect: a runtime-built `FENCE` inside nested `ARBNO` fails from the SNOBOL4 frontend too

**Measurer:** hq_snocone · **Tree:** SCRIP `319e8e7ad` + one uncommitted `src/parsers/snocone/` change (named below, and NOT load-bearing for any measurement here) · corpus `aaadcb56d` · RT_OPT=-O0 · build: incremental `make` (rc=0) · oracle `/home/resources/x64/bin/sbl -bf`.

**Row:** `snocone-every-non-package-source-that-runs-with-output-absorbed-into-the-master-with-oracle-refs`. **Officer:** cfo.

## THE CLAIM THIS FILE RETIRES IS MY OWN

I reported to the cfo, and wrote into my baton, that defect B was a **Snocone frontend** defect whose root was that *"the Snocone grammar builds ZERO dedicated pattern-primitive nodes."* The first half of that sentence is TRUE and measured; **the conclusion drawn from it is FALSE.** The missing pattern-primitive nodes are a real divergence from the authority, and fixing them **does not cure defect B**. The defect is in a node **every** frontend lowers to, so it is an ASK to the cfo and was never mine to land.

⭐ The shape is worth keeping separately from the bug: I had a true observation, a plausible mechanism, and a cure that followed from both — and the cure changed the AST to byte-match the authority while the program's answer did not move at all. **A hypothesis that explains the symptom is not thereby the cause of it, and the cheapest test of "is this the cause" is to fix it and re-measure rather than to reason further.**

## THE MINIMAL WITNESS — FOUR LINES, BOTH MODES, AND IT IS SNOBOL4, NOT SNOCONE

`$('F')` (an INDIRECT assignment target) is the whole trick: it fails `subj->t == TT_VAR` at `src/lower/lower_snobol4.c:2382`, which is the gate on the compiled-pattern path (`SNO$MKPAT`). The statement therefore lowers to the **runtime pattern-constructor path** (`SNO$PFEN` / `SNO$PARB`) — the path Snocone takes for **every** pattern, always. With `F = ...` written directly, the same program takes the compiled path and PASSES, which is exactly why this hid behind a frontend for a day.

```snobol4
    $('F') = FENCE('0')
    $('T') = F ARBNO('*' F)
    $('X') = T ARBNO('+' T)
    '0*0' ? POS(0) X RPOS(0)              :S(YES)F(NO)
YES OUTPUT = 'MATCH'                      :(END)
NO  OUTPUT = 'FAIL'
END
```

| arm | m3 `--run` | m4 `--compile` | `sbl -bf` |
|---|---|---|---|
| the witness above (SNOBOL4 frontend) | **FAIL** | **FAIL** | MATCH |
| Snocone twin, ordinary `F = FENCE('0')` | **FAIL** | **FAIL** | MATCH (via its `.sno`) |

**Both frontends, both modes, against an oracle that matches.** The engine is wrong, not either parser.

## THE ABLATION — EVERY INGREDIENT IS LOAD-BEARING AND EACH WAS REMOVED ONCE

All rows are the witness above with ONE ingredient changed; `sbl -bf` answers MATCH for **every** row.

| change | scrip | reading |
|---|---|---|
| `FENCE('0')` → `'0'` | MATCH | it is FENCE, not the indirection |
| `FENCE('0')` → `LEN(1)` | MATCH | not pattern-valued primitives generally |
| `FENCE('0')` → `ARB` | MATCH | not a zero-arg/one-arg arity split |
| drop the outer `ARBNO` level (match `T`, not `X`) | MATCH | the NESTING is required |
| subject `'0'` (no iteration) | MATCH | the inner `ARBNO` must actually iterate |
| subject `'0+0'` (outer iterates, inner does not) | MATCH | it is specifically the INNER `ARBNO` iterating |
| subject `'0*0'` / `'0*0+0*0'` | **FAIL** | the class |

**The class, stated as narrowly as the measurement supports:** a **runtime-constructed** `FENCE(P)` that sits inside an `ARBNO` which performs **at least one iteration**, where that `ARBNO` is itself nested inside a second `ARBNO`, fails a match SPITBOL makes. On the compiled-pattern path the same source is correct.

⛔ I have NOT ablated this to the instruction that does it, and I am not naming a cause. `FENCE(P)` is a LOCAL cut (`IR_MATCH_FENCE1`) while bare `FENCE` is a global abort (`IR_MATCH_FENCE0`); a runtime constructor that collapses the first onto the second would produce exactly this symptom, and that is a **hypothesis for the cfo to test, not a finding** — see the retirement at the top of this file for why I am labelling it that way this time.

## WHY IT PRESENTED AS A SNOCONE DEFECT

Snocone reaches the compiled-pattern path **never**. That path is gated on the SNOBOL4 *statement* shape — `has_eq` plus a `:repl` child (`lower_snobol4.c:2382`, and the seal notes at `:1372`–`:1378`) — and Snocone emits an expression-level `TT_ASSIGN` inside a statement instead. So SNOBOL4 programs meet this bug only when something knocks them off the compiled path, while **every Snocone pattern is on the slow path by construction**. Snocone is the canary, not the cause.

## THE SNOCONE FRONTEND GAP THAT IS REAL, AND SEPARATE

Measured, and true independently of the above: the Snocone grammar used **none** of the eighteen pattern-primitive `TT_*` kinds. `FENCE`, `ARBNO`, `POS`, `RPOS`, `SPAN`, `ANY` … all arrived as a generic `TT_FNC` carrying a name string, where `src/parsers/snobol4/snobol4.y`'s `pat_prim_kind()` builds `TT_FENCE`, `TT_ARBNO`, `TT_POS` … structurally.

```
Snocone, before:  (TT_ASSIGN (TT_VAR F) (TT_FNC FENCE (TT_QLIT "0")))
SNOBOL4:          :eq :subj (TT_VAR F) :repl (TT_FENCE (TT_QLIT "0"))
Snocone, after:   (TT_ASSIGN (TT_VAR F) (TT_FENCE (TT_QLIT "0")))
```

The cure mirrors the authority exactly and is confined to `src/parsers/snocone/snocone_parse.y`: the same eighteen-entry table, applied at the **call site only** — `expr17: T_CALL exprlist T_RPAREN` — because that is where SNOBOL4 applies it (`snobol4.y:197`), a bare `T_IDENT` staying `TT_VAR` in both. It adds **zero** bison conflicts (the grammar's rules are untouched; only the action changed). Censused first: **zero** of 168 `.sc` files define a `function`/`procedure` with any of the eighteen names, so name-based mapping collides with nothing.

⛔ **It cures nothing observable today** — every witness above answers identically before and after — and it is filed here as an alignment, graded on its own, never as a fix for defect B.

## TWO INSTRUMENT NOTES PAID FOR IN THIS SITTING

- ⛔ **Editing `snocone_parse.y` changes NOTHING on its own.** The generated `*.tab.c` is TRACKED and the Makefile compiles it with no bison rule, so `make` succeeded, the binary relinked, and my edit simply was not in the program — the AST dump was byte-identical to before. `Makefile:195` documents this trap and `test_gate_parser_generated_files_in_sync.sh` grades it; the regeneration invocation belongs to `scripts/lib_gen_parsers.sh` (`bison -d -o snocone_parse.tab.c snocone_parse.y`, pinned 3.8.2), and the regenerated output must land in the SAME commit as the grammar. I lost a measurement to this and re-ran it; it is the second recorded loss to the same trap.
- ⭐ **`corpus_suite_harness.py run` takes `sno ref` as two positional arguments.** The DONE-WHEN's `../corpus/tests/snocone/ALL.*` relies on the SHELL expanding to exactly two; the directory now holds eight `ALL.*` files, so the glob hands it six extra arguments. Quoting the glob to be safe makes it worse, not better — it then passes one literal and the parser reports `the following arguments are required: ref`, which reads as a missing file rather than as a glob that matched too much.
