# FINDING s191 (seat1, `/home/claude1`, Claude Opus 5) — queue row `ref-the-ungraded-suites` (rank 2)
# THE POND WAS ALREADY BEING FISHED — AND 61 OF ITS 107 PROGRAMS PASS BY PRINTING NOTHING

**SCRIP `408aab34` · corpus `e17c780c`.** No compiler source touched; no watermark claimed; RULES step-4 regen N/A.
Gates green: `emit_no_lang` · `template_medium_invisible` (0/ceiling 0).

---

## 1. WHAT THE BRIEF SAID, AND WHAT IS ACTUALLY TRUE

The brief: *"107 programs that NO BOARD GRADES, because grading is by .ref diff and they have none … these are self-checking
programs that print PASS/FAIL, so they were DESIGNED to be graded."* **Both halves are wrong, and the truth is worse than
"never graded."**

**(a) They are already graded.** `run_one` grades against **pin OR live oracle** — a program with no `.ref` is scored against a
freshly computed oracle answer on every board run. Nothing was invisible.

**(b) `parser/` is not a self-checking suite.** `parser/arith_add_mul.sno` is, in its entirety:

```
        y = 1 + 2 * 3
END
```

No `OUTPUT` statement. `parser/atom_id.sno` is the single line `x`. These are **minimal parse fixtures**, not programs that
print PASS/FAIL. `feat/` *is* what the brief described; `parser/` is a different kind of tree wearing the same extension.

## 2. THE CENSUS — ALL 107, CLASSIFIED BEFORE ANYTHING WAS WRITTEN

| tree | LIVE | pre-pinned | DEAD_REPORT | EMPTY | unrunnable |
|---|---|---|---|---|---|
| `feat/` (21) | **16** | 2 | 2 (`f14_opsyn`, `f15_trace_dump`) | 0 | 1 (`f18_error_handling`, SIGSEGV rc 139) |
| `parser/` (88) | **0** | 0 | 23 | **61** | 4 (RC1) |

**Only 16 of 107 have a live oracle answer to record.** Those 16 are minted (corpus `e17c780c`).

## 3. ⛔⭐⭐ THE LIVE NUMBER THIS UNCOVERED: 61 VACUOUS PASSES ARE ON THE BOARD TODAY

Those 61 zero-byte `parser/` programs are scored **57 `PASS/PASS` + 4 `PASS/ASM_FAIL`** — **they pass by producing nothing and
matching a zero-byte oracle.** They assert nothing whatever.

| misc suite | rows | score |
|---|---|---|
| as reported today | 92 | **88.0** |
| with the 61 assert-nothing rows removed | 31 | **71.0** |

The suite's weight is 3 of 113, so META moves only ~0.45 — but **the suite number is inflated by 17 points and 61 "tests" are
asserting nothing**, which is how a tree stays broken while its board stays green.

⭐ **AND ONE REAL BUG IS HIDING BEHIND THE VACUITY RIGHT NOW:** `parser/fn_define{,_locals,_multi,_noargs}.sno` score
`PASS/ASM_FAIL` — **m3 "passes" by printing nothing while m4 fails to assemble.** An m3 ≢ m4 divergence on `DEFINE`, invisible
because the m3 half is vacuous. Routed.

## 4. ⛔ WHAT I DID NOT DO, AND WHY REFUSING WAS THE WORK

**I did not mint the 61.** A 0-byte pin **freezes the vacuity into the corpus** — the same shape that nearly manufactured 134
vacuous passes at s191. The brief's DONE-WHEN asks for "a live-oracle `.ref` for every gradeable program"; the measurement says
these are not gradeable *that way*, and satisfying the letter of the row would have made the corpus worse.

**I did not reclassify them either.** Turning 61 rows into UNSCR **moves META**, and HQ ruled at s189 that weights and what
counts as scoreable are the CEO's knob — the same line I stopped at then. Asked as `q-ref-parser-vacuous-passes`.

**Two reasons `DEAD_REPORT` must never be pinned, and the second does not appear to be written down anywhere:** the dump defines
SPITBOL's *error* as correct (so the program "passes" forever by failing) — **and it embeds the ABSOLUTE PATH of the source
file** (`/home/claude1/corpus/programs/snobol4/parser/binary_opsyn.sno(1) : ERROR 029 …`). **Such a pin is not portable between
seats at all**: seat2 would fail it by construction, because its root is `/home/claude2`.

## 5. WHAT THE 16 PINS BOUGHT — AND HONESTLY, IT IS NOT A SCORE

**Minting moved NOTHING: 0 movers of 92 rows**, before vs after. That is the expected result and the point of saying it — the
pins encode what the live oracle already said. What they buy is **durability**: ground truth that survives an oracle that is
absent, dead or drifting, and drift that surfaces as `pin!=live` instead of silently redefining correct. Three reds are now
pinned *red* rather than depending on the oracle being up — `f11_io_file`, `f12_load_unload`, and `f19_real_numbers` (HQ's
`real-fn-family`: eight SPITBOL real builtins that compute in the oracle and are `Error 5 undefined` in SCRIP).

## 6. THE TOOLS, AND ONE AUTHORITY

`scorecard_snobol4.sh` gains **`oracle <suite> <program> [outfile]`** — the oracle's own answer plus a liveness status. It exists
because `run_one` runs the oracle and then **throws the output away** (it only ever compares), so any tool wanting to *record*
that answer had to re-derive the invocation — and **a `.ref` minted under a different cwd, lib path, stdin or flag set than the
board grades with is a pin that can never match** (seat5's rule, earned twice in one session: *a census is a harness; copy
`run_one`, never re-derive it*). The oracle invocation is now one function, `sc_oracle_run`; the WEIGHTS table's ragged tail is
parsed by one function, `sc_suite_fields`. `cmd_run`'s own loop is a third spelling, **deliberately not converted** — it iterates
every row and rewriting it would risk the headline instrument inside someone else's row. Flagged, not hidden.

**VALIDATED THE DOOR BEFORE MINTING 107 PINS:** `feat/f13_eval_code` already had a checked-in `.ref`, and the answer minted
through this path is **byte-identical** to it. The refactor is inert: `csnobol4_suite` re-run across it moves exactly **one** row
of 124 — `nqueens`, the ASLR-nondeterministic row from the `scorecard-provenance` rung, now sighted a third time and nothing else.

`util_ref_mint.sh <suite> <dir>… [--apply]` — census by default, writes nothing without `--apply`, mints only on `LIVE`, names
every other class, and **refuses `programs/lon/` and `programs/include/` by construction** (both refusals tested).

## 7. ROUTED

1. **`parser-acceptance-harness`** — `parser/` is the wrong shape for stdout grading and wants an **accept/reject** comparison
   instead. That instrument turns the 23 `DEAD_REPORT` rows into a real finding immediately: **the oracle rejects that syntax and
   SCRIP accepts it.** Witness `binary_opsyn.sno` (`x = 'a' & 'b'`): SPITBOL gives `ERROR 029 -- undefined operator referenced`,
   SCRIP compiles it clean, and **all 88 parser programs emit asm under `scrip --compile`** (measured). Same class as the
   `opsyn-3arg-ruling` row, at 23× scale.
2. **`parser-fn-define-m4-asm-fail`** — the four `fn_define*` rows above: m3 ≢ m4 on `DEFINE`, hidden behind a vacuous pass.
3. **`q-ref-parser-vacuous-passes`** — the scoring question: do the 61 become UNSCR, get an acceptance harness, or stay with the
   suite number known-inflated? HQ/Lon's call, not mine.

## 8. THE GENERALISABLE MOVE

⭐ **A test that cannot fail is worse than a missing test, because a missing test is visible in the denominator and a vacuous one
is not.** The 61 rows were not an unfished pond; they were 61 green lights wired to nothing, and the board had been reporting
them as passes the whole time.

⭐ **And when a brief's DONE-WHEN would make the corpus worse, the deliverable is the measurement that shows it — not the
compliance.** Minting 107 pins was the letter of this row; 16 pins plus a census that names why the other 91 must not be pinned
is the work.
