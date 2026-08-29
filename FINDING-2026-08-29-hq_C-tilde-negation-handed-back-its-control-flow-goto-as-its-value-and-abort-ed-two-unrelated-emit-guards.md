# FINDING — `~X` handed back its control-flow GOTO as its VALUE, and abort()ed two unrelated emit guards

**hq_C · 2026-08-29 · MODE FLEET-8 · SCRIP `ee3c3697` (fix) · row `snoflake-suite-scrip-only-gap`**

## The defect

`src/lower/lower_snobol4.c` `case TT_NOT:` built the negation's success edge as an `IR_GOTO` and then set `*res`
— `sx_lower`'s **value** out-param — to that same GOTO.

The control flow was always correct (inner's γ→ω, inner's ω→gate). The defect is purely the VALUE contract: an
`IR_GOTO` is not a value producer, `ir_node_produces_value()` excludes it, so `ir_drive_slot_assign()` never grants
it a ZLS slot. The node reported as "the value of `~X`" had no slot to read.

## Why it survived

⭐ **It is invisible in every context that uses `~X` only for control flow — which is the common case.** Bare
`~F()` compiles clean in both modes. The guard fires only when a VALUE consumer touches the result. Measured
controls that isolate the pair of required ingredients:

| program | rc |
|---|---|
| `~TRY() CUT(2)` (negation **and** a following pattern) | **134, abort** |
| `TRY() CUT(2)` (no `~`) | 0 |
| `~TRY()` (no pattern) | 0 |

## One cause, two guards that look unrelated

The same missing slot reaches emit down two different paths, printing two messages that name different ops and
read as different bugs:

- `~X` as a **match subject** → `emit.cpp:1541` `IR_MATCH_BEGIN` → `drive_value_slot(op=36 IR_GOTO)` →
  `[TE] GOUGE ... non-value-producer asked for a slot with no LOWER grant`
- `~X` as a **binop operand** → `emit.cpp:1490` → `emit_binop_opnd_slot() < 0` → `drive_unowned(op=3 IR_BINOP)` →
  `FATAL emit_drive: IR op=3 has no template in the universal driver`

⭐ **The second message is actively misleading and the guard says so itself**: `IR_BINOP` plainly *has* a template
(5 cases). `drive_unowned` is a shared sink, so "op=N has no template" is emitted for both "unimplemented op" and
"an implemented op's internal guard refused". Only the BACKTRACE LINE separates them — the message's own NOTE
says this, and it is right. **A shared error sink makes two different defects print the same sentence.**

## The cure

The gate becomes an `IR_LIT_STRING` with `sval ""` and the same γ. Oracle-confirmed semantics, not inferred:
SPITBOL gives `~F()` the **null string** on success — `X = ~F()` yields `SIZE(X)`=0, `DATATYPE(X)`=STRING. SCRIP
now reproduces that byte-for-byte. `IR_LIT_STRING` is a value producer, so the existing graph pass grants the slot
and TMP-ERADICATE holds — no emit-time allocation was added.

## ⛔ What this did NOT do

**It is not a pass-count gain and must not be quoted as one.** snoflake m3 PASS 75 → **75**; m4 PASS 74 → **74**.
What moved: SKIP(cc) 54→52, FAIL-M4 46→48 — `word-ending-analysis` and `arbitrarily-long-integers` went from
*would not compile* to *compiles, runs, still answers wrong*. A crash became a wrong answer. That is strictly
better and it is what unblocks the next diagnosis, but the board is unmoved and saying otherwise would be the
TRANSCRIPTION failure this org already has a rule about.

Residue, named rather than left to be rediscovered:
- `word-ending-analysis` now gets 5 of 22 lines right then diverges (`LEAVE`→`LEAV`, `DANCE`→`DANC`,
  `KISS`→`KISSE`). An `ADDON("E")` side-effect defect in `~TRY() ADDON("E")`, **separate from this one**.
- `fullscan-overlap` still aborts, `FATAL emit_drive: IR op=78` = `IR_MATCH_POS`, at `emit.cpp:1670` —
  `bb_slot_get(a0) < 0` for a non-literal `POS()` argument. Same *family* (a missing LOWER slot grant), different
  guard, still open.

## Graded

Pristine, `RT_OPT=-O0`. SHARED-NODE VERDICT SCOPE: `TT_NOT` is emitted by the **SNOBOL4, Snocone, Raku, Rebus and
Icon** frontends, so all five are arms.

`SNOBOL4 corpus m3 1299/1299 · m4 1299/1299 · FAIL=0 SKIP=0 MISSING=0` · `test_gate_emit_no_lang` rc=0 ·
`test_gate_template_medium_invisible` rc=0 · `test_gate_corpus_coverage_classified` rc=0 · icon 14/14 m4 FAIL=0 ·
snocone 5/5 · rebus 4/4 · prolog 5/5 · raku 51/51 FAIL=0 SKIP=0. Re-proved after rebase onto `ee3c3697`
(verified mechanically first: the incoming commits changed **0** files outside `scripts/`, so no build input moved).

## Method note

The witness came from **greedy delta-debugging keyed on the exact GOUGE string**, not from reading the program.
⚠️ Its first output was degenerate — orphan `+` continuation lines, undefined labels — and still reproduced the
abort, which is its own (unfiled) defect: the compiler `abort()`s on malformed input it should diagnose. The
well-formed witness above was rebuilt from the reduced one and confirmed against the oracle. **A reducer optimises
for the signature you gave it, not for a valid program; check the reduction is legal input before believing it
localises your bug.**
