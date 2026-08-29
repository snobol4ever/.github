# FINDING 2026-08-29 seat08: `rung36_jcon_proto.icn` is not one bug — it's an exhaustive Icon-syntax stress test surfacing at least 8 distinct, unrelated frontend/emitter gaps

Row: `tests-consolidate-icon`. `proto` was the one file among the row's standing 9 loose-but-undeclared files never previously traced (every session's notes read "frontend parse gap (`proto`), not traced" verbatim). This session traced it. **Not fixed — out of this row's lane, same discipline as every other bug this row has found (`args`/`level`/`scan`/`var`).**

## Headline
`rung36_jcon_proto.icn` is Icon's classic V9GEN "one of every syntactic form" stress test (record/global decls, then `expr1`..`expr4` procedures each packed with one-liner exercises of a specific operator or statement form). It does not fail at one point — it fails, sequentially, at **6 distinct precisely-pinned parser gaps**, and **at least 2 further emitter-level gaps** beyond those (imprecisely pinned — see below). This is a genuine, broad Icon-language-completeness gap, not a single localized defect, and not something a test-consolidation row should be fixing piecemeal.

## Parser-level gaps (6, each verified individually by patching-and-rerunning until the next distinct error appeared — single-variable, fully reliable)
| # | line | source | error |
|---|---|---|---|
| 1 | 47 | `^x;` | `expected expression (got ^)` — unary prefix `^` (REFRESH) unsupported; binary `^` (exponentiation, used elsewhere in this same file at `i ^ j;`) is fine |
| 2 | 106 | `a1 |||:= a2;` | `expected expression (got :=)` — augmented `|||:=` (concat-assign) |
| 3 | 107 | `x ===:= y;` | same — augmented `===:=` (value-equal-assign) |
| 4 | 108 | `x ~===:= y;` | same — augmented `~===:=` (value-not-equal-assign) |
| 5 | 109 | `x &:= y;` | same — augmented `&:=` (conjunction-assign) |
| 6 | 110 | `x @:= y;` | same — augmented `@:=` (activate-assign) |

Note what's adjacent and NOT broken, so the gap is precisely scoped: `i ^ j` (binary power) and the augmented forms `<<=:=`, `==:=`, `>>=:=`, `>>:=`, `~==:=`, `?:=` (lines 100-105, immediately before #2) all parse fine. This is a small, enumerable set of missing tokens in the augmented-assignment family plus one missing unary prefix operator — not a wholesale category failure.

## Emitter-level gaps (at least 2, beyond the parser gaps — NOT precisely pinned, flagged honestly rather than guessed)
With all 6 parser gaps patched (replaced with `1;`), the file gets past parsing entirely and into emission, where it hits:
```
[TE] GOUGE drive_value_slot(op=120): non-value-producer asked for a slot with no LOWER grant — emit-time allocation is ERADICATED (TMP-ERADICATE); add an ir_drive_slot_assign grant for this op
```
Removing `expr1`'s entire body (lines 15-36, the block of one-liner expression-statements: `();`, `{}`, `[];`, `[,];`, `x.y;`, `x[i]`, `x[i:j]`, `x[i+:j]`, `x[i-:j]`, `(,,,);`, `x(,,,);`, `x!y;`, `not x;`, `|x;`, `!x;`, `*x;`, `+x;`, `-x;`) makes the op=120 crash disappear — but a **different** crash immediately takes its place:
```
FATAL emit_drive: IR op=122 has no template in the universal driver. Every op must be handled — Implement op=122.
```
**Attempted to bisect op=120 to a single line within `expr1` and could not get a clean, monotonic result** — splitting lines 15-36 into halves, then quarters, gave inconsistent results (op=120 disappearing when either half is removed alone in some splits, reappearing in others), which reads as either more than one line in that block independently triggering the same guard, or some shared/positional state (slot numbering, statement count) shifting which specific node hits the guard first depending on what surrounds it. Recorded honestly as unresolved rather than asserting a specific single-line cause I could not actually reproduce cleanly. `op=122`'s trigger is somewhere in `expr2` or later — not investigated at all this session (time-boxed out; the parser-level gaps and the existence of these two further emitter gaps is already a strong enough signal without exhaustively mapping the whole file).

## Why this doesn't belong to `tests-consolidate-icon`
This is implementing missing Icon language features (an obscure unary operator, five augmented-assignment operators, and at least two IR-op-to-emission-template gaps), not test-suite housekeeping. Consistent with this row's own established discipline for every other real bug it has surfaced (`args`, `level`, `scan`, `var` — root-caused, documented, explicitly left unfixed and out-of-lane): `proto` gets the same treatment. **Not added to `KEEP.md`** for the same reason `var` wasn't (per seat14's ruling on that file, preserved here): these are active, fixable gaps, not permanent design exclusions, so declaring them permanently-excluded would be dishonest. It also has no existing live row to `PENDING.md`-defer to (unlike `cxprimes`/`scan2` → `icon-n2-generator-activation-frames`) — recommending HQ consider minting one (something like "icon-frontend-v9gen-operator-coverage-gaps"), since this is unusually broad for a single loose test file and likely represents a real, user-visible completeness gap in the Icon frontend, not just this one stress-test file's problem.

## Scope reminder for the row
This brings all 9 of the row's standing loose-but-undeclared files to the same level of characterization: 4 real bugs owned elsewhere (`args`/`level`/`scan`/`var`), 3 blocked on `icon-n2-generator-activation-frames` (`genqueen`/`recogn` directly or via `icn-recogn-genqueen-suspend-shape`; `cxprimes`/`scan2` already `PENDING.md`-deferred there), 1 now-traced multi-gap language-completeness issue with no owning row yet (`proto`, this FINDING), and 1 still awaiting a fix/xfail/permanent-loose policy call nobody has made (`rung38_cset_embedded_nul` — `scan1` turns out to already be in the `args`/`level`/`scan`/`var` "real bug, root-caused" bucket per the ledger, not the policy-call bucket; re-read the ledger's own most recent characterization before assuming otherwise). **Still nothing safely convertible in this row's own charter this session** — same honest non-outcome as the last several sessions, now with one fewer genuinely-unknown file.
