# GOAL-SNOCONE-BEAUTY — beauty.sc Self-Beautifies via scrip

**Repo:** one4all
**Done when:** `./scrip --ir-run test/beauty-sc/beauty/beauty.sc < input.sno`
produces output byte-for-byte identical to SPITBOL running `beauty.sno` on
the same input. Gate script reports PASS.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_snocone.sh              # PASS=5
bash /home/claude/one4all/scripts/test_beauty_snocone_all_modes.sh   # PASS=42 SKIP=3
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh       # PASS=44
```

---

## Architecture (TWO STEPS)

**Step 1 — .sno subsystem files + beauty.sc:**
scrip handles mixed-extension multi-file linkage natively. Pass subsystem
`.sno` files as libraries, `beauty.sc` as main program:

```bash
./scrip --ir-run \
    corpus/programs/snobol4/beauty/global.sno \
    ... \
    corpus/programs/snobol4/beauty/trace.sno \
    test/beauty-sc/beauty/beauty.sc < input.sno
```

Oracle: `smoke/beauty_oracle.sno` (NOT `demo/beauty.sno` — crashes error 021).

**Step 2 — Replace .sno subsystem files with .sc equivalents:**
Substitute from `corpus/programs/include-sc/` one by one, gate stays green.

---

## Current state (2026-04-29, session #64)

SB-1..SB-3 DONE.

SC sources live at `corpus/programs/snocone/demo/beauty/` (session #62, finalized).
Source modules at top level. Subsystem tests flat in `test/` as `test_<subsys>.sc` + `test_<subsys>.ref`.
Gates green: PASS=5, PASS=42 SKIP=3, PASS=49.

**SB-4a in progress (session #64).** Per-file scrutiny + rewrite of six `.sc`
modules landed against canonical `.inc` sources at
`corpus/programs/snobol4/demo/beauty/`. Identified three systemic Snocone-port
bugs the previous translation pass had baked in:

1. **Predicate-form `subj ? (PAT)` does NOT consume from subject** — only `. var`
   captures named in the pattern. The trailing `&& ''` in many places was a
   no-op. Use statement-form `subj ? (PAT) = ;` for match-and-replace, or
   `RTAB(0) . subj` for capture-the-rest.
2. **`if (~(subj ? PAT_with_captures))` runs the match but discards captures**
   even on success. Use positive-form match with explicit else branch.
   (beauty.sc already noted this; comment at line 23.)
3. **The SNOBOL4 idiom `i = LT(i, n) i + 1` does not compose in Snocone.**
   Bare juxtaposition raises Error 5 — Undefined function or operation.
   Use idiomatic `while (LT(i, n)) { i = i + 1; ... }`.

Files rewritten this session:
- `case.sc` — `icase` infinite-loop fixed (was non-destructive scan).
- `Gen.sc` — buffer-not-advancing fixed (`REM . _rest` capture, plus positive
  match form). Likely a major contributor to the SB-5 "no output" symptom.
- `TDump.sc` — three broken loops, broken conditional separator, tree-type
  test fixed (`IDENT(DATATYPE(x), 'tree')` — Snocone has no deferred-eval
  `*IDENT(n(x))`).
- `XDump.sc` — broken loop, REPLACE-uppercase removed.
- `ReadWrite.sc` — non-destructive scans in Write/LineMap fixed.
- `Qize.sc` — non-destructive scans in Qize/SQize/DQize/SqlSQize/Intize fixed.

Smoke-tested in isolation against SPITBOL oracle on representative inputs.
All three baseline gates remain green after every fix.

**SB-4a remaining:** `omega.sc` (TV/TW/TX/TY/TZ trace-instrumentation —
mixes pattern arithmetic with `&&` concat in ways that need careful
scrutiny), `ShiftReduce.sc` (whitespace-strip in Shift is a no-op since
`whitespace` global is undefined; cosmetic; document and skip),
`global.sc` (clean), and decision on whether `semantic.sc`/`trace.sc`
need to exist as separate library files (current design has them
implicitly inlined into beauty.sc; the runner script `util_run_beauty_sc.sh`
invokes scrip with a single .sc arg, no -INCLUDE-style multi-file linkage).

**SB-5 partial diagnosis:** beauty.sc still produces no output end-to-end
after the Gen.sc fix. Bisection with probe-OUTPUT statements shows
execution dies at line 45 `if (DIFFER(ppAutoMode)) { ... }`. The
condition is FALSE (correctly skipping the body) but the body loads
something the IR lowerer rejects with three "Error 5 Undefined function
or operation" messages — silently when the body is skipped at runtime,
visibly when forced to evaluate.

**Root cause located (end of session #64):** `ppAutoMode` and the entire
~50-line `--auto` two-pass block in beauty.sc (lines 14–97) are
**non-canonical accretions** — not present in `beauty.sno` at all.
A previous session bolted on a HOST(0) CLI-args parser plus an auto-tuning
prepass for stop-column widths. None of that code is part of the SNOBOL4
oracle. The IR-lowerer-rejected constructs (the C-style `for (...; ...; ...)`
loop on line 73, the `goto ppAutoNext`/label pair, the `output__/input__`
calls) all live inside that stowaway block. **Strip the args parser and
the auto-mode block from beauty.sc — that should both restore SB-4a
faithfulness and unblock SB-5 in one move.** Next session opens here.

---

## Steps

- [x] **SB-1** — Diagnose underflows.
- [x] **SB-2** — Fix $'...' lexer.
- [x] **SB-3** — Fix scan+replacement lowering. 0 underflows.
- [ ] **SB-4a** — Careful rewrite: for each `.sno` / `.inc` source file in
  `corpus/programs/snobol4/beauty/`, read the original, read the current `.sc`
  in `corpus/programs/snocone/demo/beauty/`, and regenerate it from scratch.
  Scrutinize every chunk. No `goto` statements unless unavoidable.
  No internal labels inside procedures. Files to cover:
  `global.sno`, `case.sno`, `assign.sno`, `match.sno`, `counter.sno`,
  `stack.sno`, `tree.sno`, `ShiftReduce.sno`, `TDump.sno`, `Gen.sno`,
  `Qize.sno`, `ReadWrite.sno`, `XDump.sno`, `omega.sno`, `semantic.sno`,
  `trace.sno`, and `beauty.sno` (main program body → `beauty.sc`).
  After each file: smoke-test it in isolation with `scrip --ir-run`.
- [ ] **SB-5** — Fix: beauty.sc produces no output with .sno libs.
- [ ] **SB-6** — Self-beautify. Gate: diff empty.
- [ ] **SB-7** — Gate script. Commit. Push.

---

## Invariants

- Gate = PASS=36 FAIL=0 on test_smoke_unified_broker.sh after every commit.
- Oracle: corpus/programs/snobol4/smoke/beauty_oracle.sno
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

---

## Canonical destination — corpus/programs/snocone/demo/beauty/

SC sources live at `corpus/programs/snocone/demo/beauty/` as of session #62.
This is the permanent home.

**Naming distinction (decided in session-#NN with Lon):**

- **BEAUTY** — `demo/beauty/` — SNOBOL4 implementation reading SNOBOL4
  source. Self-host = beauty.sno reads its own .sno source.
- **BEAUTIFY** — `demo/beautify/` — Snocone implementation reading
  SNOBOL4 source. The implementation language is Snocone; the input
  and output language remain SNOBOL4. BEAUTIFY does NOT read or write
  Snocone code (yet — that would be a future BEAUTIFY-extended).

The BEAUTIFY self-host gate produces output matching the BEAUTY md5
`abfd19a7a834484a96e824851caee159` because both pretty-print the same
SNOBOL4 source. This auto-cross-checks the Snocone implementation
against the SNOBOL4 implementation.

**Move plan (when SB-5 is green):**

1. `git mv one4all/test/beauty-sc/beauty/` content into
   `corpus/programs/snobol4/demo/beautify/`. This includes
   `beauty.sc`, `Gen.sc`, `Qize.sc`, `TDump.sc`, `XDump.sc`,
   `case.sc`, `io.sc`, `omega.sc`, `driver.sc` (auto-assembled).
2. `git mv` each of the 14 subsystem folders
   (`arith/`, `assign/`, `counter/`, `fence/`, `global/`, `match/`,
   `roman/`, `semantic/`, `ShiftReduce/`, `ReadWrite/`, `stack/`,
   `strings/`, `trace/`, `tree/`) into the same `beautify/` —
   each carrying its `driver.sc` and `driver.ref`. These are the
   subsystem-level beauty regression tests.
3. Update path constants in:
   - `scripts/test_beauty_snocone_all_modes.sh` —
     `BEAUTY_DIR=$HERE/../test/beauty-sc` →
     `BEAUTY_DIR=$CORPUS/programs/snobol4/demo/beautify`
   - `scripts/test_beauty_snocone_subsystems.sh` — analogous
   - `scripts/util_run_beauty_sc.sh` —
     `DRIVER=$ROOT/test/beauty-sc/beauty/driver.sc` →
     `DRIVER=$CORPUS/programs/snobol4/demo/beautify/driver.sc`
   - `scripts/test_crosscheck_beauty_snocone.sh` — analogous
4. The `.ref` files in each subsystem are byte-identical to the
   BEAUTY oracle outputs (they should be — the Snocone driver
   produces the same SNOBOL4-formatted output). RULES.md
   self-contained-demo exception applies: copies allowed,
   sync discipline required, byte-diff CI verification.
5. Update REPO-corpus.md to document the new `demo/beautify/`
   directory.
6. Gate after move: `test_beauty_snocone_all_modes.sh` PASS=42 SKIP=3
   still green; `test_smoke_unified_broker.sh` total still ≥ 36.

**Why move only when SB-5 is green:** moving broken code into corpus
locks in a debugging session that has to find issues across two
locations. Easier to land the move when the implementation works.

**Compatibility with GOAL-CORPUS-LAYOUT.md:** When the broader
corpus reorg executes (CL-1..CL-8), `demo/beautify/` becomes
`programs/beautify/snocone/` — the language sub-folder pattern the
new layout adopts. The current move is forward-compatible: the
.sc files are already in `beautify/`, just under a different parent.

**Active rung remains SB-5.** The destination decision does not
change what blocks progress — it only documents where the work
lands when unblocked. SB-7 (gate script + commit + push) becomes
the natural place to do the corpus move as part of the same commit
sequence that lands the gate.
