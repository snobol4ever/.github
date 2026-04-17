# GOAL-SNOCONE-CLAWS5.md — claws5.sc under scrip

**Repo:** one4all + corpus
**Done when:** `scrip --ir-run claws5.sc < claws5.input` produces output
matching `claws5.ref` exactly (diff zero), all three modes
(--ir-run, --sm-run, --jit-run).

**Oracle:** `csnobol4 -bf claws5.sno < claws5.input` matches `claws5.ref`.
claws5.sno is the reference implementation. claws5.sc must match it.

**Parallel session note:** This goal runs concurrently with
GOAL-SNOCONE-TREEBANK-LIST. Both probe the same SC-26 pattern engine bug
from different angles. Fix in one4all/runtime — share via main, no branches.

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
bash /home/claude/one4all/scripts/test_smoke_snocone.sh   # PASS=5
```

---

## Key files

```
corpus/programs/snobol4/demo/claws5.sc        — Snocone program under test
corpus/programs/snobol4/demo/claws5.sno       — SNOBOL4 oracle reference
corpus/programs/snobol4/demo/claws5.input   — 4-sentence test input
corpus/programs/snobol4/demo/claws5.ref       — expected output (95 lines, pprint format)
corpus/programs/snobol4/demo/CLAWS5inTASA.dat — full corpus (989 lines, needs -P 34000)
```

---

## Architecture reminder

```
claws5.sc → snocone_compile() → Program* [LANG_SNO]
    --ir-run  → execute_program() → interp_eval()
    --sm-run  → sm_lower() → SM_Program → sm_interp_run()
    --jit-run → sm_lower() → SM_Program → sm_codegen() → sm_jit_run()

Key pattern construct:
    ARBNO( (header . *new_sent()) | (token . *add_tok()) )
    where header/token use (PAT . var) . *fn(var) capture+call chains
```

---

## Known blocker going in

SC-26: `(PAT . var) . *fn(var)` — the chained outer indirect call `*fn`
is NOT invoked at match time under scrip. Both SPITBOL and CSNOBOL4 do
invoke it. Earlier description ("arg not passed correctly") was wrong;
the call itself never fires. Bug lives in the pattern engine —
likely bb_boxes.c (XCALLCAP lowering) or snobol4_pattern.c (match-time
side-effect firing).

---

## Step ladder

- [ ] **CL-1** — Diagnose SC-26 for claws5.sc.
  Run `scrip --ir-run claws5.sc < claws5.input` and capture error.
  Identify which `(PAT . var) . *fn(var)` call fails first.
  Write a minimal isolated test case in `test/snocone/test_capture_call.sc`.
  Gate: understand exactly where arg value goes wrong in bb_boxes.c / snobol4_pattern.c.

- [ ] **CL-2** — Fix SC-26 in the pattern engine (coordinate with GOAL-SNOCONE-TREEBANK-LIST).
  The fix lives in one4all runtime. Once found, one fix serves both goals.
  Gate: `test/snocone/test_capture_call.sc` PASS all 3 modes.
  Gate: `test_smoke_snocone.sh` PASS=5.

- [ ] **CL-3** — claws5.sc PASS --ir-run.
  `scrip --ir-run claws5.sc < claws5.input | diff - claws5.ref` → empty.
  Gate: zero diff.

- [ ] **CL-4** — claws5.sc PASS --sm-run and --jit-run.
  Gate: zero diff both modes.

- [ ] **CL-5** — Full corpus smoke: claws5.sc on CLAWS5inTASA.dat.
  `scrip --ir-run -P 34000 claws5.sc < CLAWS5inTASA.dat` — no crash, sane output.
  (No ref for full corpus — just verify no errors and output count is reasonable.)

---

## Current state (corpus HEAD pending, one4all HEAD abf17001)

All 3 .sno oracles pass diff-zero under csnobol4 -bf:
  claws5.sno            95/95 lines (used -P 34000)
  treebank-list.sno     24/24 lines
  treebank-array.sno    24/24 lines

CL-1 diagnosis complete. Findings:

  1. `?= <-` is not a Koenig/Snocone operator (not in his `bconv` table)
     and is also not in our lexer. It was a proposed tertiary for the
     SNOBOL4 `subj pat = repl` statement-as-boolean idiom. Unimplemented.
     REMOVED from the two sites that used it:
       claws5.sc line 75  -> plain `line = INPUT; while (DIFFER(line)) { ... }`
       treebank-array.sc line 128 -> `while (src ? (spat && REM . rest))`
                                      with src = rest after match.

  2. `test/snocone/test_capture_call.sc` created with 5 numbered tests
     (epsilon-star, plain capture, capture-call, alt-wrd, alt-num).
     Under scrip --ir-run: 4 PASS (1, 2, 3, 4a). 4b missing — program
     terminated silently mid-test with no output. Still to diagnose.

  3. Minimal `(LEN(3) . w) . *show(w)` in isolation: scrip matches but
     does NOT invoke `show`. Both SPITBOL -b and CSNOBOL4 -bf invoke it
     (verified: prints `got: foo`). So the SC-26 bug is real and the
     symptom is `*fn` not firing at all, not an argument-value bug as
     the prior goal-file text said. The earlier text was wrong.

  4. claws5.sc hangs (timeout 124) under both --ir-run and --sm-run,
     with `Error 3 in statement 9 — erroneous array or table reference`
     on stderr and empty stdout. Root cause traced: Error 3 originates in
     snobol4_pattern.c NONARY path (lines 475, 492) — subscript on
     non-array/non-table. Fires because *new_sent() never runs (SC-26),
     so sentno/mem[sentno] are uninitialized when add_tok() tries to
     subscript them. Error 3 is non-fatal (FTLTST); hang is separate.

  5. treebank-array.sc (post-tertiary-removal) exits cleanly but prints
     `stmt_exec: unimplemented XKIND 17 — using epsilon` — XBAL is not
     implemented in the runtime. That is a SEPARATE missing feature,
     owned by the treebank goals, not by CLAWS5.

  6. pp_mem in claws5.sc produces different output format from claws5.sno
     pp_mem. The .sno pp_mem produces the compact Python-dict pprint in
     claws5.ref. The .sc pp_mem uses a different indented format and will
     NOT match .ref even when the tokenizer is fixed. claws5.sc pp_mem
     must be rewritten as a faithful Snocone translation of the .sno
     pp_mem before CL-3 can pass.

  7. bb_boxes.c reviewed. The capture box (bb_capture) correctly buffers
     pending spec on γ. The callcap / chained-call box is the next focus:
     need to find where (PAT . var) . *fn(var) lowers to in bb_boxes.c
     and snobol4_pattern.c — the outer *fn call is not being constructed
     or invoked at match commit time.

Snocone extensions vs Koenig (answered Q): binary ops 28 -> 39 (+11:
six compound assigns, `**`, `&`, `@`, `~`, `:`); unary ops unchanged;
keywords 11 -> 14 (+3: break, continue, struct); comments gained `//`.

Blocker: SC-26 — `. *fn(arg)` chained after `(PAT . var)` not firing.
Next: CL-2 — find the callcap/chained-call box in bb_boxes.c (truncated
last session at line 155). Read the full capture/callcap section. Trace
how (PAT . var) . *fn(var) lowers through snocone_lower.c into IR, then
into bb_build.c. Fix the missing *fn invocation. Then rewrite pp_mem in
claws5.sc to match .sno pp_mem output format.
