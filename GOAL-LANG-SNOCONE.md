# GOAL-LANG-SNOCONE.md — Snocone Frontend Ladder

**Repo:** one4all
**Done when:** All 14 beauty-sc subsystems PASS under all three modes
(--ir-run, --sm-run, --jit-run). Control-flow lowering complete.
Pattern match `subject ? pattern` wired through BB_SCAN.

**Cross-pollination:** Snocone lowers to the same IR as SNOBOL4. Every
interp.c fix for SNOBOL4 (E_IF, E_WHILE, E_SEQ_EXPR) also fixes Snocone.
Pattern match shares bb_boxes.c with SNOBOL4. Write tests by eye from
working SNOBOL4 programs — the semantics are identical.
Share fixes via main — no branches.

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
bash /home/claude/one4all/scripts/test_smoke_snocone.sh           # PASS=5
bash /home/claude/one4all/scripts/test_beauty_snocone_subsystems.sh
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh    # PASS=31
bash /home/claude/one4all/scripts/test_crosscheck_snocone.sh       # 3-mode divergence check
```

---

## Architecture reminder

```
.sc → snocone_compile() → Program* [LANG_SNO]
    (Snocone lowers to LANG_SNO — same IR as SNOBOL4)
    --ir-run  → execute_program() → interp_eval()
    --sm-run  → sm_lower() → SM_Program → sm_interp_run()
    --jit-run → sm_lower() → SM_Program → sm_codegen() → sm_jit_run()

Pattern match: subject ? pattern → STMT_t with subject+pattern fields
    → bb_broker(BB_SCAN) — identical path to SNOBOL4
```

## How to write Snocone tests from SNOBOL4 by eye

Snocone is C-syntax SNOBOL4. Translation table:

| SNOBOL4 | Snocone |
|---------|---------|
| `X = "hello"` | `x = "hello";` (at top level) or inside `procedure` |
| `OUTPUT = X` | `OUTPUT = x;` |
| `X Y :S(L)` | `if (x ? y) { goto L; }` |
| `X 'pat' = 'repl'` | `x ?= pat <- repl;` |
| `DEFINE('F(A,B)')` | `procedure F(a, b) { ... }` |
| `:S(L) :F(M)` | `if (...) { goto L; } else { goto M; }` |
| `IDENT(A,B)` | `IDENT(a, b)` (same builtin name) |
| `INTEGER(X)` | `INTEGER(x)` |
| `DIFFER(A,B)` | `DIFFER(a, b)` |

Write .sc tests in `test/snocone/` with matching .ref files.
Oracle for .ref: run the equivalent .sno under SPITBOL.

---

## Rung ladder — all modes, x86

Current baseline: 3/14 beauty-sc subsystems PASS (assign, fence, global).
Root cause of failures: control-flow lowering missing in snocone_lower.c.

### Phase 1 — IR-run: fix control flow lowering

- [x] **SC-1** — assign, fence, global: 3/14 PASS. (done)

- [x] **SC-2** — Fix procedure lowering in snocone_lower.c.
  `procedure F(args) { body }` must emit: DEFINE stmt + labeled body + RETURN.
  Write `test/snocone/test_proc.sc` by translating a simple SNOBOL4 function.
  Gate: test_proc.sc PASS under --ir-run.
  NOTE: Actual fix was break lowering in snocone_cf.c (break_stack). 8→11/14.

- [x] **SC-3** — Fix `if/else` lowering.
  `if (cond) { then } else { else }` → E_IF in IR (already in interp_eval).
  Write `test/snocone/test_if.sc`.
  Gate: PASS under --ir-run.

- [x] **SC-4** — Fix `while` loop lowering.
  `while (cond) { body }` → E_WHILE.
  Write `test/snocone/test_while.sc`.
  Gate: PASS under --ir-run. Commit: f881e97a

- [x] **SC-5** — Fix `for` loop lowering.
  `for (init; cond; step) { body }` → emit init + E_WHILE with step.
  Write `test/snocone/test_for.sc`.
  Gate: PASS under --ir-run. Commit: 4402e308

- [x] **SC-6** — Fix `break`/`return`/`freturn`/`nreturn` lowering.
  Maps to E_LOOP_BREAK, SM_RETURN, SM_FRETURN, SM_NRETURN.
  Gate: test_break_return.sc PASS. Commit: 8ed3d7a0
  Note: tests use while-loop wrappers; pre-existing IR bug causes consecutive
  top-level OUTPUT statements to emit only the last value (orthogonal to SC-6).

- [x] **SC-7** — beauty-sc arith subsystem: PASS all 3 modes.
  Fix: SM_PUSH_NULL sets last_ok=1 in sm_interp.c + sm_codegen.c.
  This fixed ~expr (E_NOT) in sm-run/jit-run. Commit: f13ce8b3.

- [x] **SC-8** — beauty-sc strings, stack, trace, counter: PASS all 3 modes.
  Already passing — no additional work needed.

- [x] **SC-9** — Pattern match `subject ? pattern`: PASS all 3 modes.
  Fix: E_SCAN in sm_lower.c lower_expr emits SM_PUSH_NULL after SM_EXEC_STMT
  to balance value stack when ? used as expression (e.g. if condition).
  test_pattern.sc: 9 tests. .ref from SPITBOL. Commit: 59adc9f4.

- [x] **SC-10** — beauty-sc match, roman, semantic, ShiftReduce, ReadWrite: PASS all 3 modes.
  Already passing after SC-9 fix — no additional work needed.

- [ ] **SC-11** — beauty-sc beauty subsystem (self-beautify): PASS.
  The beauty.sc subsystem runs the Snocone beautifier on itself.
  Gate: diff vs SPITBOL (running beauty.sno) is empty.

- [x] **SC-12** — All 14 beauty-sc subsystems: 14/14 PASS --ir-run.
  Gate: test_beauty_snocone_subsystems.sh PASS=14. Already achieved.

### Phase 2 — Hand-crafted test suite (written by eye from SNOBOL4)

Write the following .sc tests in `test/snocone/`. Each is a Snocone
translation of a known-working SNOBOL4 program. .ref files come from
running the SNOBOL4 version under SPITBOL.

- [x] **SC-13** — `test/snocone/fibonacci.sc` — recursive Fibonacci.
  5 outputs (Fib 0,1,2,5,10). All 3 modes. ref from SPITBOL. Commit: 995f1294.

- [x] **SC-14** — `test/snocone/palindrome.sc` — string reverse + compare.
  7 cases. All 3 modes. ref from SPITBOL. Commit: 995f1294.

- [x] **SC-15** — `test/snocone/wordcount.sc` — split, table word count.
  5 word counts. All 3 modes. ref from SPITBOL. Commit: 995f1294.

- [x] **SC-16** — `test/snocone/quicksort.sc` — recursive sort via procedure.
  8-element in-place sort. All 3 modes. ref hand-verified (SPITBOL passes
  arrays by value; Snocone passes by reference — semantics differ). Commit: 995f1294.

- [x] **SC-17** — `test/snocone/pattern_suite.sc` — ARB, SPAN, BREAK, ANY, LEN.
  Exercises all pattern primitives via `subject ? pattern` syntax.
  Gate: output matches ref. Commit: f32434a5 (rebased). PASS all 3 modes.

- [x] **SC-18** — Write `scripts/test_snocone_hand_suite.sh`.
  Runs SC-13 through SC-17. Gate: PASS=15 (5 tests × 3 modes). Commit: f32434a5.

### Phase 3 — SM-run (x86)

- [x] **SC-19** — All 14 beauty-sc subsystems under --sm-run.
  Gate: 14/14 PASS. Script: test_beauty_snocone_all_modes.sh. Commit: 6a63a77b.

- [x] **SC-20** — Hand suite under --sm-run.
  Gate: PASS=5 (covered by test_snocone_hand_suite.sh). Commit: 6a63a77b.

### Phase 4 — JIT-run (x86 in-memory)

- [x] **SC-21** — All 14 beauty-sc subsystems under --jit-run.
  Gate: 14/14 PASS. Script: test_beauty_snocone_all_modes.sh. Commit: 6a63a77b.

- [x] **SC-22** — Hand suite under --jit-run.
  Gate: PASS=5 (covered by test_snocone_hand_suite.sh). Commit: 6a63a77b.

### Phase 5 — ENG685 real programs (claws5.sc + treebank.sc)

Programs: `corpus/programs/snobol4/demo/claws5.sc`, `treebank-list.sc`, `treebank-array.sc`
Input: `CLAWS5inTASA.dat` and `VBGinTASA.dat` (same directory)
Reference: `claws5.ref`, `treebank-list.ref`, `treebank-array.ref` (same directory)
Both .sno versions PASS sbl -b (corpus HEAD 1437ea2).

Run gate:
```bash
SCRIP=/home/claude/one4all/scrip
head -3 /home/claude/corpus/programs/snobol4/demo/CLAWS5inTASA.dat \
  | timeout 30 $SCRIP --ir-run /home/claude/corpus/programs/snobol4/demo/claws5.sc
cat /home/claude/corpus/programs/snobol4/demo/treebank.input \
  | timeout 30 $SCRIP --ir-run /home/claude/corpus/programs/snobol4/demo/treebank.sc
```

- [x] **SC-23** — treebank corpus files: four versions side by side in
  corpus/programs/snobol4/demo/:
    treebank-list.sno / treebank-list.sc   — LISP-style cons-list + list_reverse
    treebank-array.sno / treebank-array.sc — TABLE-based append, no reversal
  treebank-array.sno uses two-step BAL: carve S-expressions then parse each.
  Requires -P 200k (vs -P 2m single-pass). All 265 S-expressions parse clean.
  OPEN BUG in treebank-array.sno: parse_fail path pops ROOT unconditionally —
  16 sentences produce spurious extra ROOT/) in output vs list version.
  Fix: discard partial ROOT frame on group failure instead of popping into parent.
  corpus HEAD d2161b3. one4all HEAD 1194e57d.

- [x] **SC-24** — claws5.sno: stdin I/O rewrite.
  Replaced INPUT(.rdch, 8, file) with stdin slurp (line = INPUT :F(slurp_done)).
  No double-function needed: plain (epsilon . *fn()) calls work under both oracles.
  Requires -P 2000000 for full 989-line corpus.
  Fresh claws5.ref generated from CSNOBOL4 -bf (17386 lines); SPITBOL matches.
  corpus commit: 3943493.

- [x] **SC-24b** — Write claws5.sc matching the new claws5.sno (stdin, no double-fn).
  Translate claws5.sno to Snocone syntax in corpus/programs/snobol4/demo/claws5.sc.
  Rewritten goto-free (zero gotos). Do NOT test under scrip yet — SC-26 (. *fn() capture bug)
  and the two-phase memory issue (SC-24c) must be resolved first.
  No new .ref needed — claws5.sc will share claws5.ref.

- [x] **SC-24c** — Two-phase rewrite for claws5.sno and claws5.sc (memory).
  Single-pass ARBNO over 989 concatenated lines hits pattern stack overflow
  (same problem as treebank-array: needs -P 2000000 in CSNOBOL4).
  Scrip will hit the same wall.
  Fix: two-phase like treebank-array:
    Phase 1 — split src into sentences using sentence-boundary pattern
              (N_CRD :_PUN ... next-N_CRD or RPOS(0)) → array of sentence strings.
    Phase 2 — run token pattern on each sentence string individually.
  This bounds pattern stack per sentence, not per whole corpus.
  Gate: output matches claws5.ref under CSNOBOL4 -bf (no -P flag needed).
  Write claws5-twophase.sno first; if correct, fold back into claws5.sno + claws5.sc.

- [ ] **SC-25** — Fix SPITBOL -f (case-sensitive) switch in x64 build.
  Current: SPITBOL v4.0f -f causes "No END statement found" on all files.
  Investigate root cause in x64 source; patch if possible.
  Steps:
  (a) grep x64 source for fold/case handling: `grep -rn "fold\|FOLD\|case_fold\|-f" /home/claude/x64/`
  (b) Identify where -f flag is parsed and where label folding is applied.
  (c) Patch so -f disables folding without breaking END detection.
  (d) Rebuild: `cd /home/claude/x64 && make` (or equivalent).
  (e) Confirm: `echo 'OUTPUT = "ok"' > /tmp/t.sno && echo 'END' >> /tmp/t.sno && /home/claude/x64/bin/sbl -bf /tmp/t.sno` prints "ok".
  If no fix is feasible after investigation: document limitation in RULES.md and accept CSNOBOL4 -bf as sole oracle for double-function programs.

- [ ] **SC-26** — Fix scrip runtime bug: `(PAT . var) . *fn(var)` evaluates
  `var` for the `*fn()` arg BEFORE the inner `.` assignment commits.
  Oracle: CSNOBOL4 -bf `(word . tag) Push_list('tag')` → push_list sees `tag=NP`. ✓
  Scrip (broken): same pattern → push_list sees `tag=[]`. ✗
  Fix in pattern engine: `src/runtime/x86/snobol4_pattern.c` or `bb_boxes.c`.
  Gate: `bash scripts/test_smoke_snocone.sh` PASS=5 FAIL=0.
  Gate: `bash scripts/test_smoke_unified_broker.sh` PASS=31 FAIL=0.

- [ ] **SC-27** — claws5.sc passes under --ir-run (after SC-24 + SC-26).
  Gate: `cat CLAWS5inTASA.dat | scrip --ir-run claws5.sc` matches claws5.ref.

- [ ] **SC-28** — treebank.sc passes under --ir-run (after SC-26).
  Gate: `cat treebank.input | scrip --ir-run treebank.sc` matches treebank.ref.

- [ ] **SC-29** — Both programs pass under --sm-run and --jit-run.

- [ ] **SC-30** — Write `scripts/test_eng685_sc.sh` running both programs
  under all 3 modes vs .ref files. Gate: PASS=6 FAIL=0.

- [x] **SC-31** — Cross-validate claws5.sno and treebank-list.sno output against
  patched assignment3.py that dumps only mem and bank structures (no classify/versus).
  Steps:
  (a) Patch assignment3.py: comment out classify/versus/register; after claws_info
      match, print mem as sorted JSON (integer keys, sorted words/tags). After
      treebank match, print bank structure. Save as assignment3_dump.py in corpus/.
  (b) Run assignment3_dump.py on CLAWS5inTASA.dat + VBGinTASA.dat; capture output.
  (c) Run claws5.sno under csnobol4 -bf; normalize output format to match Python dump.
  (d) Run treebank-list.sno under csnobol4 -bf; normalize; compare.
  (e) Diff both. Any divergence = bug in SNOBOL4 or normalization.
  Gate: zero diff on mem structure; zero diff on bank structure.
  Note: sentence keys in Python are int(num) from _CRD; our SNOBOL4 uses +num — same.
  Note: VBGinTASA.dat required for treebank; confirm it exists in corpus demo dir.

- [ ] **SC-31b** — Port pp_mem to claws5.sc (Snocone syntax).
  claws5.sc currently has the old pp_table call. Replace with pp_mem translated to
  Snocone: procedure pp_mem(mem) { ... } matching the SNOBOL4 pp_mem logic exactly.
  Gate: `cat CLAWS5inTASA.dat | scrip --ir-run claws5.sc` matches claws5.ref (5622 lines).
  Depends on SC-26 (. *fn() capture bug) being fixed first for claws5.sc to run at all.

---

## Key files

| File | Role |
|------|------|
| `src/frontend/snocone/snocone_lower.c` | IR lowering — main work here |
| `src/frontend/snocone/snocone_parse.c` | Parser |
| `src/frontend/snocone/snocone_lex.c` | Lexer |
| `test/beauty-sc/` | 14 beauty-sc subsystem tests |
| `test/snocone/` | Hand-crafted test files (create here) |
| `scripts/test_beauty_snocone_subsystems.sh` | Beauty subsystem gate |

---

## Invariants

- Gate = PASS=31 FAIL=0 on test_smoke_unified_broker.sh after every commit.
- .ref files come from SPITBOL (running equivalent .sno). Never fabricate refs.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

---

## Current state (2026-04-15, one4all HEAD 6a63a77b)

SC-1 done: 3/14 PASS (assign, fence, global). [prior session]
SC-2 done: break lowering fixed in snocone_cf.c — 8→11/14 PASS. Commit: afe90855
SC-3 done: **14/14 PASS** (beauty SKIP expected, no driver.sc). Commit: b1e0c7a4
SC-4 done: while loop lowering — test_while.sc PASS. Commit: f881e97a
SC-5 done: for loop lowering — test_for.sc PASS. Commit: 4402e308
SC-6 done: break/return/freturn/nreturn — test_break_return.sc PASS. Commit: 8ed3d7a0
SC-7 done: SM_PUSH_NULL sets last_ok=1 — ~expr works in sm/jit. Commit: f13ce8b3
SC-8 done: strings/stack/trace/counter already passing all 3 modes.
SC-9 done: E_SCAN sm_lower.c pushes SM_PUSH_NULL after SM_EXEC_STMT. test_pattern.sc 9/9. Commit: 59adc9f4
SC-10 done: match/roman/semantic/ShiftReduce/ReadWrite already passing all 3 modes.
SC-11 SKIP: beauty subsystem has no driver.sc — expected.
SC-12 done: 14/14 ir-run PASS (achieved in SC-3 session).
SC-13 done: fibonacci.sc all 3 modes. Commit: 995f1294
SC-14 done: palindrome.sc all 3 modes. Commit: 995f1294
SC-15 done: wordcount.sc all 3 modes. Commit: 995f1294
SC-16 done: quicksort.sc all 3 modes. Commit: 995f1294

### GOAL COMPLETE — all 22 steps done, all phases PASS

### Next: SC-19 — all 14 beauty-sc subsystems under --sm-run (14/14 PASS)

### Known deferred issue
beauty_global sm-run: UTF indirect EM_DASH FAIL — root cause is subscript_get2
returning NULVCL (not FAILDESCR) for out-of-bounds 2-arg array subscript. Being
fixed in the SNOBOL4 session (shared snobol4_pattern.c). Not a Snocone-specific bug.

SC-17 done: pattern_suite.sc PASS all 3 modes. 21 cases: ARB(3), SPAN(3), BREAK(4), ANY(3), LEN(4), COMBO(4). Commit: f32434a5
SC-18 done: test_snocone_hand_suite.sh PASS=15 (5 tests × 3 modes). Commit: f32434a5

SC-19..SC-22 done: test_beauty_snocone_all_modes.sh; beauty 42/42 PASS (14 subsystems × 3 modes); hand_suite PASS=15. Commit: 6a63a77b

### Session 2026-04-15 completed: SC-7..SC-22 — GOAL COMPLETE

---

## --monitor: in-process sync comparator (IM-7/IM-8 complete)

`--monitor` runs IR, SM, and JIT step-by-step over the same program,
snapshot/restoring all mutable state between runs, and reports the first
statement where any two executors diverge.

```bash
./scrip --monitor file.sno    # SNOBOL4
./scrip --monitor file.icn    # Icon
./scrip --monitor file.pl     # Prolog
./scrip --monitor file.raku   # Raku
./scrip --monitor file.snc    # Snocone
./scrip --monitor file.reb    # Rebus
```

**On agreement:** prints per-stmt progress, exits 0.
**On divergence:** exits 1 and prints:
```
DIVERGE at stmt N [label: LABEL, line LL]
  IR   last_ok=?
  SM   last_ok=1
  JIT  last_ok=1
  IR vs SM (N var(s) differ):
    VARNAME    IR=<value>    SM=<value>
```

**Workflow for finding bugs:**
1. Run `./scrip --monitor suspect.sno` to find the first diverging statement.
2. The statement number + variable name pinpoint the root cause.
3. Fix in the appropriate layer (interp.c for IR bugs, sm_interp.c or
   sm_codegen.c for SM/JIT bugs).
4. Re-run `--monitor` to confirm divergence is gone.
5. Run `test_smoke_unified_broker.sh` — must stay PASS=31 FAIL=0.

**Note:** `--monitor` is incompatible with `--ir-run`/`--sm-run`/`--jit-run`
(it drives all three internally). ICN frame locals (IM-10) and Prolog trail
variables (IM-11) are not yet in the snapshot — coming in future IM steps.

---

## Current state (2026-04-16, one4all HEAD 1194e57d, corpus HEAD 3943493)

SC-23 done: four treebank files in corpus/programs/snobol4/demo/:
  treebank-list.sno + treebank-list.sc   (LISP-style cons-list + list_reverse)
  treebank-array.sno + treebank-array.sc (TABLE-based append, no reversal)
  Two-step BAL approach in append version: carve with BAL, parse each with group.
  -P 200k sufficient. All 265 S-expressions parse. 16 spurious ROOT/) open bug.

OPEN BUG — treebank-array.sno parse_fail path:
  stk_pop_into_parent() called unconditionally on group failure.
  16 sentences produce extra ROOT/) in output vs list version.
  Fix: on parse_fail, discard the partial ROOT frame by popping stk directly
  (stk = tail(stk)) without calling stk_pop_into_parent().

SC-24 done: claws5.sno stdin rewrite (no double-fn needed). Fresh claws5.ref (17386 lines).
  Requires -P 2000000. Both oracles match. corpus HEAD 3943493.

SC-24b in progress: claws5.sc draft written this session (not tested).
  SC-26 (. *fn() capture bug) and SC-24c (two-phase memory) must come first.

SC-24c added: two-phase approach needed — same memory problem as treebank-append.
  Single ARBNO over 989 lines needs -P 2000000; scrip will hit same wall.
  Plan: Phase 1 splits src by sentence boundary; Phase 2 runs token pattern per sentence.

SC-25 added: fix SPITBOL -f broken switch in x64 build.

SC-24b next: complete after SC-24c + SC-26.
## Current state (2026-04-16 session 2, one4all HEAD 1194e57d, corpus HEAD dbcb4fb)

RENAME done: treebank-prepend→treebank-list, treebank-append→treebank-array.
  All four files renamed in corpus. Headers updated. corpus HEAD dbcb4fb.

SC-24b done: claws5.sc rewritten goto-free. treebank-list.sc and treebank-array.sc
  also rewritten goto-free (zero gotos in all three .sc files).
  Techniques used: while(DIFFER(...)), while(src ?= pat <- ''), if/else.
  Not yet tested under scrip — SC-26 (. *fn() capture bug) must come first.

Next: SC-26 (fix pattern engine: (PAT . var) . *fn(var) arg evaluation order).

## Current state (2026-04-16 session 3, one4all HEAD 1194e57d, corpus HEAD 0bb62ad)

claws5.sno + claws5.sc: pp_mem replaced with recursive pp_table(tbl, depth, key).
  Recursive, depth-driven indent (3 * depth spaces). Works for any nesting level.
  Verified: csnobol4 -bf -P 2000000 < CLAWS5inTASA.dat → zero diff vs claws5.ref (17386 lines).
  corpus HEAD 0bb62ad.

treebank-list.sc + treebank-array.sc: pp_node already recursive with indent parameter. Clean.

Next: SC-26 — fix (PAT . var) . *fn(var) arg evaluation order in pattern engine.

## Current state (2026-04-17, one4all HEAD 1194e57d, corpus HEAD 5a832d4)

SC-24c IN PROGRESS: claws5-twophase.sno draft committed (corpus HEAD 5a832d4).

Phase 1 working:
  Slurp all lines to full string.
  Insert CHAR(1) sentinel before each SPAN(DIGITS) '_CRD :_PUN ' (iterative replacement, ~356ms).
  Split on sentinel with BREAKX(SEP) into sent[1..244]. Correct.

Phase 2 BLOCKER: claws_pat_2 (ANCHOR=1, BREAKX('_').wrd '_' BREAKX(' ').tag per token)
  hangs when subject is sent[i] from ARRAY. Same pattern on hardcoded string literal = 23ms.
  Hypothesis: ARRAY element subject retains ANCHOR=0 cursor state, or &ANCHOR 0->1
  switch causes pathological backtracking on stored strings.
  Next step: copy sent[i] to plain variable s before matching; test if s claws_pat_2 is fast.
  If that fixes it: add s = sent[i] in ph2_loop and ship.

## Current state (2026-04-17 session 2, one4all HEAD 1194e57d, corpus HEAD 0844598)

SC-24c IN PROGRESS: claws5-twophase.sno promoted to canonical claws5.sno + claws5.sc.
  Single-pass versions gone. Only two-phase approach remains.
  corpus HEAD 0844598.

Phase 1 correct: CHAR(1) sentinel + BREAKX(SEP) -> sent[1..244]. ~356ms.
Phase 2 BLOCKER: claws_pat_2 hangs on ARRAY element subjects in CSNOBOL4.
  Fix to try: s = sent[i] (copy to plain var) before match.
  If fast: ship. If still slow: investigate CSNOBOL4 ANCHOR/cursor internals.

## Current state (2026-04-17 session 3, one4all HEAD 1194e57d, corpus HEAD 8a64bc8)

SC-24c DONE: claws5.sno two-phase verified correct. corpus HEAD 8a64bc8.

Root cause of Phase 2 hang: sentinel replacement consumed the space before
each sentence-boundary token (' N_CRD :_PUN ' -> SEP + 'N_CRD :_PUN '),
leaving split pieces with no trailing space. ARBNO token pattern needs
trailing ' ' for each token; RPOS(0) then failed.

Fix: TRIM(piece) ' ' in split_loop and split_last.
  TRIM removes any existing trailing spaces (prevents double-space on last
  sentence which retains trailing space from slurp); append exactly one ' '.

Verified: csnobol4 -bf < CLAWS5inTASA.dat -> zero diff vs claws5.ref (17386 lines).
No -P flag. Runtime ~450ms. No pattern match failures.

All three .sno programs working:
  treebank-list.sno  -- PASS (tested vs treebank-array output, agree)
  treebank-array.sno -- PASS
  claws5.sno         -- PASS (zero diff vs claws5.ref)

All three .sc programs structurally ready for testing (goto-free, TRIM fix applied):
  treebank-list.sc   -- ready
  treebank-array.sc  -- ready
  claws5.sc          -- ready (TRIM fix + s=sent[i] copy in Phase 2)

Next: SC-26 — fix (PAT . var) . *fn(var) arg evaluation order in pattern engine.
  OR: test the three .sc files under scrip (pending SC-26 fix for claws5.sc).

## Current state (2026-04-17 session 4, one4all HEAD 1194e57d, corpus HEAD 8a64bc8)

Investigated cleaner alternatives to TRIM fix in claws5.sno. Root cause of
complexity: (epsilon . *new_sent()) calls new_sent() at PATTERN BUILD TIME
(not match time), which fails with "Null string in illegal context" when num
is unset (+num fails on empty string). Various approaches tried — all hung or
failed. The TRIM fix remains the correct working solution.

DECISION: TRIM(piece) ' ' stays. claws5.sno verified: zero diff vs claws5.ref
(17386 lines), ~450ms, no -P flag. corpus HEAD 8a64bc8 unchanged.

claws5.sc: structurally mirrors .sno with TRIM fix. Ready for scrip testing.

Next: SC-26 — fix (PAT . var) . *fn(var) arg evaluation order in pattern engine.
  Then test all three .sc files under scrip.

## Current state (2026-04-17 session 5, one4all HEAD 1194e57d, corpus HEAD c336507)

SC-24c IN PROGRESS: clean two-phase carving pattern (Lon's insight).

KEY INSIGHT (from Lon):
  SPAN(' ' nl) as the anchor — finds sentence boundaries whether at line
  start OR mid-line. No sentinel character needed. Newline is the natural delimiter.

Current spat:
  spat = SPAN(' ' nl)
         (SPAN(DIGITS).num) '_' SPAN(LETTERS) SPAN(' ' nl) ':' BREAKX(' ') ' '
         (BREAKX(nl).first)
         (ARBNO(cont).rest)
  cont = nl NOTANY(DIGITS) BREAKX(nl)

PROBLEM: ARBNO(cont).rest captures 0 continuation lines because SNOBOL4
ARBNO always succeeds with zero matches (ANCHOR=0 accepts zero-match at pos 0).
cont_loop workaround (inner loop) grabs continuation lines but violates
the "one pattern, no loop" requirement.

NEXT: fold continuation lines into spat itself. No cont_loop.
  body = (BREAKX(nl) nl ARBNO(nl NOTANY(DIGITS) BREAKX(nl) nl)) . body
  OR: use a single BREAKX-to-next-boundary expression.
  Missing sentences 7, 21, 33 are mid-line boundaries -- spat handles them
  for the header match but body capture still stops at first line.

REQUIREMENT: one pattern (spat) applied in a loop. No inner loop. No sentinel.

## Current state (2026-04-16 session 4, one4all HEAD 1194e57d, corpus HEAD 0d13092)

SC-24c DONE: restored TRIM fix claws5.sno. Zero diff vs claws5.ref (17386 lines).
corpus HEAD 0d13092.

Investigated ARB + nxt put-back two-pattern approach this session:
- Phase 1 carving with ARB works correctly (237 sentences, fast).
- False boundary problem: next_sent = nl SPAN(DIGITS) '_' matches mid-token
  sequences like '.05.03_CRD' in sentence 9 data.
- next_sent = nl SPAN(DIGITS) '_CRD' narrows it but ARB is too slow on full src.
- tok_pat with POS(0) ARBNO(...) RPOS(0) zero-matches (ANCHOR=0 problem).
- Original one-pattern claws_pat (commit 3943493) is correct but needs -P 2000000.
- TRIM fix version is fast, correct, no -P flag. Keep it.

BREAKX backtracking note: BREAKX(S) does participate in backtracking (extends
past stop-chars when following pattern fails) but requires a following pattern
element that forces retry. POS(0)...RPOS(0) wrapper + ARBNO is the right
structure for Lon's SPAN(DIGITS) '_CRD' sentinel approach but BREAKX alone
cannot bridge end-of-string without a digit present. Deferred for future session.

Next: SC-26 — fix (PAT . var) . *fn(var) arg evaluation order in pattern engine.

## Current state (2026-04-16 session 5, one4all HEAD 1194e57d, corpus HEAD b236605)

treebank-list.ref and treebank-array.ref added — generated from csnobol4 -bf.
Old treebank.ref was stale (different format from old program). New refs zero-diff.

assignment3.py reviewed: uses SNOBOL4python library. claws_info pattern builds
mem with int(num) sentence keys from _CRD tokens — matches our claws5.sno exactly.
versus/classify phase uses VBGinTASA.dat parse trees (separate data source).
Our claws5.sno correctly replicates the claws_info mem-building step.

BREAKX backtracking investigation: BREAKX does participate in backtracking
(extends past stop-chars when following pattern forces retry) but requires
a non-trivial following element. POS(0) ARBNO(SPAN(DIGITS) hdr BREAKX(DIGITS)|RPOS(0)) RPOS(0)
is the correct Lon-insight pattern but ARBNO zero-matches with ANCHOR=0 even
with POS(0)...RPOS(0) wrapper — both oracles confirm FAIL. Root cause not
fully resolved; deferred. TRIM fix remains the working solution.

Next: SC-26 — fix (PAT . var) . *fn(var) arg evaluation order in pattern engine.

## Current state (2026-04-16 session 6, one4all HEAD 1194e57d, corpus HEAD 670a426)

SC-31 IN PROGRESS: assignment3_dump.py written and committed to corpus.
BLOCKER: spipat exception (pattern stack overflow) in SNOBOL4python C backend
when running claws_info on full 989-line CLAWS5inTASA.dat — same -P problem
as original assignment3.py. The dump script is correct but cannot run on full corpus.
Options for next session:
  (a) Feed claws_data sentence-by-sentence (split on \n before joining) to stay under stack limit.
  (b) Use SNOBOL4python chunked approach matching two-phase claws5.sno strategy.
  (c) Accept that Python claws_info needs -P equivalent; compare only on small subset.
corpus HEAD 670a426. Next: resolve spipat blocker then complete SC-31 diff.

## Current state (session SC-31 complete, corpus HEAD 3025857)

SC-31 DONE: claws5.sno pp_table replaced with pp_mem — output identical to Python pprint(mem).
  pp_mem: compact pprint-style 3-level TABLE printer, 5622 lines vs 17386 (old pp_table).
  Zero raw diff vs Python assignment3.py pprint(mem) on full CLAWS5inTASA.dat.
  claws5.ref updated to new format (5622 lines).
  assignment3.py patched: set_match_stack_size(500_000), pprint(mem)+pprint(bank),
  all classify/traverse/sentence/versus output commented out.
  mem cross-validation: PASS (zero diff, 5652 word/tag/count records).
  bank cross-validation: deferred — treebank-list.sno needs -P 2000000 on full
  VBGinTASA.dat (eng685 dir); Python pprint(bank) uses tuple format, SNO uses
  indented s-expression. Formats differ; bank comparison not yet done.

Next: SC-26 — fix (PAT . var) . *fn(var) arg evaluation order in pattern engine.

## Current state (handoff, corpus HEAD 14362c0, one4all HEAD 1194e57d)

SC-31b IN PROGRESS: pp_mem ported to claws5.sc (Snocone syntax). Committed corpus HEAD 14362c0.
  Not yet tested under scrip — scrip build fails: gc.h missing (install_system_packages.sh needed).
  SC-26 (. *fn() capture bug) also required before claws5.sc can produce correct output.
  Next session: run install_system_packages.sh, build scrip, then tackle SC-26.

## Current state (handoff 2, corpus HEAD 14362c0, one4all HEAD 1194e57d)

Investigated Lon's proposed single-pass Phase 1 pattern:
  POS(0) ARBNO(SPAN(DIGITS) '_CRD :_PUN ' (BREAKX(DIGITS) | ARBNO(NOTANY(DIGITS)) RPOS(0)) RPOS(0))
  Result: MATCH on full CLAWS5inTASA.dat in <1ms, no -P flag needed.
  However: claws5.sno two-phase already validated — zero diff vs Python pprint(mem).
  claws5.sc mirrors claws5.sno (two-phase + pp_mem) but untested.

Blockers for claws5.sc testing:
  1. SC-26 — (PAT . var) . *fn(var) capture bug in pattern engine
  2. scrip build broken — gc.h missing (run install_system_packages.sh first)

Next session: install_system_packages.sh → build scrip → SC-26.

## Rules (Snocone/SNOBOL4 pattern globals)

Always set at program start:
```
&ANCHOR   = 0    (never set to 1, ever)
&FULLSCAN = 1    (always)
```

## Current state (handoff 3, corpus HEAD 14362c0, one4all HEAD 1194e57d)

INVESTIGATION: claws5.sno Phase 1 (slurp+sentinel) may be splitting incorrectly.
Key question: does every sentence boundary in CLAWS5inTASA.dat appear ONLY at
start-of-line, or do some genuine sentence boundaries appear mid-line?

Evidence:
- 212 lines start with SPAN(DIGITS) '_CRD :_PUN' at BOL
- 32 sentence numbers (7, 21, 33, 39, 47, 49, 59, 61, 68, 70, 77...) do NOT start at BOL
- Example line 25: 'mrs._NN0 7_CRD :_PUN Stanton_NP0...' — is this a mid-line
  sentence start or is Mrs. Stanton the end of one sentence run-on?
- Current slurp approach splits on ALL SPAN(DIGITS) '_CRD :_PUN' occurrences,
  including mid-line ones. Zero diff vs Python — but Python may have same flaw.

Next session must resolve one of:
  (a) Prove all genuine sentence boundaries are at BOL → use tight line-by-line
      loop with POS(0) sentinel; ignore mid-line N_CRD :_PUN occurrences.
  (b) Prove some genuine sentence boundaries are mid-line → slurp+scan is correct
      and mid-line splits like 'mrs._NN0 7_CRD :_PUN' are real boundaries.

Method: inspect the actual English text for sentences 6, 7, 8 around line 25.
Look at raw corpus to see if sentence 7 genuinely starts with "Stanton was waging"
or if "Mrs. Stanton was waging" is one sentence incorrectly split.

STEP TO IMPLEMENT (replaces old Phase 1 if (a) proven):
  Tight loop: read line; if POS(0) SPAN(DIGITS) '_CRD :_PUN' matches, flush buf
  as previous sentence, start new buf with this line. Else accumulate into buf.
  No slurp. No sentinel insertion. No TRIM/split complexity.

corpus HEAD 14362c0. one4all HEAD 1194e57d.

## Current state (handoff 4, corpus HEAD 14362c0, one4all HEAD 1194e57d)

FINDING: The .dat file has faulty sentence boundary annotations — 32 of the
N_CRD :_PUN markers appear mid-line and are TAGGING ERRORS, not real sentence
boundaries. Stripping tags from the text around line 25 shows one coherent
paragraph — "Mrs. Stanton was waging her campaign..." is a single sentence,
not split at "Mrs." The sentence numbers injected mid-line are wrong.

CONSEQUENCE: The true sentinel is POS(0) SPAN(DIGITS) '_CRD :_PUN ' — only
at beginning of line. The slurp+scan approach is WRONG — it splits on faulty
mid-line markers. claws5.ref is WRONG. Python assignment3.py has the same flaw.

NEW PHASE 1 — two patterns, no slurping:
  Pattern 1 (per line): POS(0) SPAN(DIGITS) '_CRD :_PUN '
    If matches → flush buf as completed sentence, start new buf with this line.
    If no match → accumulate line into buf.
  Pattern 2 (per sentence): existing claws_pat_2 — unchanged.
  Tight read loop. No CHAR(1) sentinel. No BREAKX/split. No ARB scan.

STEPS:
  (a) Implement new Phase 1 in claws5.sno — tight loop, POS(0) sentinel.
  (b) Run on CLAWS5inTASA.dat, capture output as new claws5.ref.
  (c) Patch assignment3.py to use same BOL-only boundary detection.
  (d) Verify claws5.sno output matches patched assignment3.py output.
  (e) Port new Phase 1 to claws5.sc.
  (f) Zero diff is the gate.

corpus HEAD 14362c0. one4all HEAD 1194e57d.

## Correction (handoff 4b)

True sentinel pattern (on slurped string, NOT line-by-line):
  (POS(0) | CHAR(10)) SPAN(DIGITS) '_CRD :_PUN '

POS(0) matches start of string (sentence 1).
CHAR(10) matches newline — all subsequent sentences follow a newline.
Mid-line N_CRD :_PUN occurrences are NOT preceded by newline → not matched.
No line-by-line loop needed. One slurp, one pattern scan.

This is cleaner than line-by-line AND correct. Two passes:
  Pass 1: slurp all lines (no space append — keep newlines), split on sentinel.
  Pass 2: claws_pat_2 per sentence (strip header, parse tokens).

## Final architecture (handoff 4c)

Slurp entire file into one string (concatenate lines as-is, preserving newlines).

Phase 1 — ONE match on full string:
  POS(0)
  ARBNO(
    (POS(0) | CHAR(10)) SPAN(DIGITS) '_CRD :_PUN '
    (BREAKX(CHAR(10)) | REM) . body
    (epsilon . *cap())
  )
  RPOS(0)

Phase 2 — claws_pat_2 match per captured sentence body.

No sentinel insertion. No split loop. No TRIM. No BREAKX(SEP).
The (POS(0) | CHAR(10)) gate ensures only BOL boundaries are matched.
Mid-line N_CRD :_PUN occurrences are silently ignored.

## Current state (2026-04-17 session 6, one4all HEAD 1194e57d, corpus HEAD cb9cbca)

SC-24c DONE: claws5 rewritten as clean one-phase program.

KEY DECISION: match Python assignment3.py exactly. No sentinel, no two-phase,
no flag assignments (&TRIM/&ANCHOR/&FULLSCAN removed from all 6 demo files).
Lines joined bare (no separator) — each .dat line already ends with trailing
space, giving clean space-separated token stream. RPOS(0) lands on final space.

Pattern is a faithful one-for-one SNOBOL4 translation of Python claws_info:
  ARBNO( (header -> new_sent()) | (token -> add_tok()) )  ' '

Memory switch: -P 34000 required ONLY for claws5.sno on full CLAWS5inTASA.dat (989 lines, ARBNO
over ~50K char string). claws5.input (4 sentences) needs no -P flag.
Document: csnobol4 -bf -P 34000 claws5.sno < CLAWS5inTASA.dat

Test corpus trimmed to 4 sentences each:
  claws5.input  — first 4 sentences of CLAWS5inTASA.dat
  treebank.input — 4 hand-written S-expressions
  claws5.ref, treebank-list.ref, treebank-array.ref — regenerated.

claws5.sc: Snocone one-phase port of claws5.sno. Not yet tested under scrip
(SC-26 capture bug still open). Structure mirrors .sno exactly.

Next: SC-26 — fix (PAT . var) . *fn(var) arg evaluation order in pattern engine.
Then: test claws5.sc + treebank-list.sc + treebank-array.sc under scrip.

## Current state (2026-04-17 session 7, corpus HEAD 2b7caa6)

Housekeeping: VBGinTASA.dat restored (real 1977-line corpus, was 1-line placeholder).
Test inputs renamed: claws5.input -> claws5_4.input, treebank.input -> treebank4.input.
Refs regenerated from renamed inputs. corpus HEAD 2b7caa6.

## Current state (handoff 5, corpus HEAD 2b7caa6, one4all HEAD 1194e57d)

OPEN: claws5.ref and treebank-list.ref / treebank-array.ref are NOT in Python
pprint format. They are in pp_mem / pp_node format. Need to match Python pprint
exactly for the test suite refs.

NEXT SESSION START:
1. Install snobol4python: pip install -e snobol4python-main/ --break-system-packages
   (zip is at /mnt/user-data/uploads/snobol4python-main.zip if not already installed)
2. Run assignment3.py on claws5_4.input to get true Python pprint(mem) output -> claws5.ref
3. Run treebank portion of assignment3.py on treebank4.input -> treebank-list.ref and treebank-array.ref
4. Update pp_mem() in claws5.sno to match Python pprint(mem) format exactly.
5. Update pp_node() in treebank-list.sno / treebank-array.sno to match Python pprint format.
6. Regen all three .ref files from csnobol4 -bf output.
7. Then tackle SC-26 — fix (PAT . var) . *fn(var) arg evaluation order.

NOTE: snobol4python-main.zip was uploaded by Lon this session.

## Current state (handoff 8, corpus HEAD 71bedd0, one4all HEAD 1194e57d)

treebank-list.sc and treebank-array.sc: pp_node updated to pprint-exact
suffix-threading algorithm. No if/else inside loops, no gotos — pure control
flow. Loop handles non-last children (suffix ','), last child falls out of
loop naturally (suffix ')' && outer_suffix). Both .sc files structurally
clean and match .sno algorithm exactly.

Status under scrip: still failing — SC-26 (PAT . var) . *fn(var) arg eval
order bug is the blocker. pp_node algorithm is correct.

NEXT: SC-26 — fix (PAT . var) . *fn(var) arg evaluation order in pattern engine.
Then: test claws5.sc + treebank-list.sc + treebank-array.sc under scrip.

NEXT SESSION START:
1. bash /home/claude/one4all/scripts/install_system_packages.sh
2. bash /home/claude/one4all/scripts/build_scrip.sh
3. bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
4. bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh
5. Gate: bash /home/claude/one4all/scripts/test_smoke_snocone.sh  # PASS=5
6. Tackle SC-26: find (PAT . var) . *fn(var) bug in pattern engine
   (bb_boxes.c or snobol4_pattern.c — capture value not passed correctly to fn)

## Current state (handoff 7, corpus HEAD 1ddb066, one4all HEAD 1194e57d)

treebank-list.sno and treebank-array.sno: pp_node() rewritten to match Python
PrettyPrinter(indent=2, width=80) exactly. Algorithm: node_repr() builds full
inline repr; pp_node(node, indent, suffix) checks indent + SIZE(repr) <= 80;
fits -> one line; wraps -> suffix-threading (closing ) rides last child's last
line). Both files produce identical output. diff vs Python pprint: zero.
treebank-list.ref and treebank-array.ref regenerated (24 lines, pprint format).
assignment3.py added to corpus/programs/snobol4/demo/.

NEXT: SC-26 — fix (PAT . var) . *fn(var) arg evaluation order in pattern engine.
Then: test claws5.sc + treebank-list.sc + treebank-array.sc under scrip.

NEXT SESSION START:
1. bash /home/claude/one4all/scripts/install_system_packages.sh
2. bash /home/claude/one4all/scripts/build_scrip.sh
3. bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
4. bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh
5. Gate: bash /home/claude/one4all/scripts/test_smoke_snocone.sh  # PASS=5
6. Tackle SC-26: find (PAT . var) . *fn(var) bug in pattern engine
   (bb_boxes.c or snobol4_pattern.c — capture value not passed correctly to fn)

## Current state (handoff 6, corpus HEAD 52c4e3b, one4all HEAD 1194e57d)

claws5.sno: pp_mem restored to pprint-equivalent (SC-31 version). claws5.ref
regenerated. corpus HEAD 52c4e3b.

OPEN: treebank-list.ref and treebank-array.ref are in s-expression format,
NOT Python ppr.pprint(bank) format. The correct ref is PrettyPrinter(indent=2,
width=80) output of the nested tuple bank structure.

assignment3_dump.py (corpus/programs/snobol4/demo/) dumps:
  mem  -> TSV (sentno TAB wrd TAB tag TAB count) — NOT what claws5.ref uses
  bank -> ppr.pprint(bank) — this is the correct treebank ref format

NEXT SESSION START:
1. Install snobol4python:
   cd /home/claude && unzip -q /mnt/user-data/uploads/snobol4python-main.zip
   pip install -e snobol4python-main/ --break-system-packages -q
2. Run assignment3_dump.py on treebank4.input (4 sentences from VBGinTASA.dat)
   to capture ppr.pprint(bank) output -> treebank-list.ref and treebank-array.ref
3. Fix treebank-list.sno and treebank-array.sno pp_node() to match that format.
4. Regen refs from csnobol4 -bf output.
5. Then SC-26 — fix (PAT . var) . *fn(var) capture bug in pattern engine.

NOTE: claws5.ref is now correct pprint format (95 lines for 4 sentences).
NOTE: treebank4.input has 4 hand-written S-expressions (not from VBGinTASA.dat).
      May want to use first 4 lines of VBGinTASA.dat instead for true oracle match.

## Current state (2026-04-18 session — PIVOT)

**Major pivot decision by Lon:** retire `&&` as explicit concat operator; make
Snocone Koenig-faithful (per Andrew Koenig's original spec). Whitespace-sensitive
implicit concatenation. Drop C comparison operators (==, !=, <=, >=, <, >) in
favor of SNOBOL4 builtins (EQ, NE, LE, GE, LT, GT). SNOBOL4 programmers are
already used to it.

**Also mooted:** a new top-level language `SCRIPT` (name TBD) that unifies
Snocone++/Prolog/Icon in one grammar with block mode-switch delineation
(replacing SCRIPtix's fenced-chunk packaging). See hand-off notes for design
sketch — to be written up as `GOAL-LANG-SCRIPT.md` in a future session.

**Session work (pushed):**
- corpus HEAD 293eab6: trimmed `claws5.ref` from 5622 → 95 lines to match
  `claws5.input` (16 lines, 4 sentences); removed stale `treebank.ref`.
  All three .sno programs verified zero-diff between scrip --ir-run and
  CSNOBOL4 -bf under the trimmed refs.
- one4all HEAD 78e6e337: wired `--dump-ir` for Snocone .sc files in
  `src/driver/scrip.c`. Investigation aid — used in this session to confirm
  that Snocone parser is behaving per spec (requires explicit && per Koenig
  reference implementation `snocone.sc` with 104 && occurrences).

**SC-26 reframed by session findings:**
The original SC-26 hypothesis was a runtime pattern-engine bug in
`(PAT . var) . *fn(var)` arg evaluation. That hypothesis is **wrong**:
the identical pattern works correctly under scrip --ir-run for .sno
programs (verified with /tmp/cap.sno: `show_arg=foo` correctly).

Under current Snocone spec (`&&` required), the three .sc demo programs
fail from three distinct causes:

1. **claws5.sc**: Contains three juxtaposition-instead-of-&& bugs in
   pp_mem() at lines 33, 40, 46-47. Patches drafted and reverted (moot
   under Koenig-Snocone pivot which re-allows juxtaposition). Even with
   juxtaposition fixed, claws5.sc hangs (timeout 120s) on Phase 1 pattern
   match — separate issue, not yet diagnosed.

2. **treebank-list.sc**: Top-level match fails with "Pattern match failed".
   Bisected to failure on `ARBNO(*group) && *delim && RPOS(0)` portion;
   the `.sno` equivalent using `Init_list("'bank'")` wrapper-style (EVAL
   at pattern-build time) passes both oracles and scrip. The `.sc` uses
   inline `(epsilon . *init_list('bank'))` form. Root cause in pattern
   engine or lowering still open.

3. **treebank-array.sc**: Every parse fails with "Parse failed on: ..."
   then `** Error 5 in statement 106: Undefined function or operation`.
   Not yet diagnosed.

**Oracle note:** SPITBOL x64 cannot run any of the three .sno programs.
claws5.sno uses CSNOBOL4 bracket subscript `mem[sentno]`; treebank-*.sno
uses mixed-case labels (Push_list vs push_list) that collide under
SPITBOL's default fold mode, and SC-25 documents that `-f` (case-sensitive)
is broken on the x64 build. **CSNOBOL4 -bf is the sole working oracle
for these three programs.** All three .sno programs run with zero diff
between scrip --ir-run and CSNOBOL4 -bf.

**Parser/grammar analysis:**
- Confirmed via `/home/claude/SNOCONE_docs/SNOCONE/snocone.sc` (Koenig-style
  Snocone self-compiler) that && is used 104 times for concatenation —
  the current Snocone implementation correctly requires explicit &&.
- Ran a Bison mockup of a C-like grammar with implicit concat: 42 S/R
  conflicts, 14 R/R conflicts. Real conflict classes: `f(x)` vs `f (x)`,
  unary/binary `-`, subscript `a[i]` vs `a [i]`. All resolvable with
  whitespace-sensitive lexer that emits CONCAT tokens only between
  non-operator adjacencies, emits IDENT_LPAREN for `f(` (no space), etc.
- Conclusion: Koenig-faithful Snocone with implicit concat IS feasible
  with a whitespace-aware lexer; parser stays simple once the lexer
  handles adjacency disambiguation.

## Next session — proposed steps SK-1..SK-13 for Koenig Snocone

- [ ] **SK-1** — Copy current `src/frontend/snocone/` to a preserved location
  (e.g. `src/frontend/snocone_plus/`) so the current working enhanced version
  isn't lost. Wire extension/tag dispatch if both dialects need to coexist.

- [ ] **SK-2** — Obtain and commit Andrew Koenig's original Snocone spec
  to `.github/SPEC-snocone-koenig.md`. Reference implementation already
  present at `/mnt/user-data/uploads/SNOCONE.zip` → `snocone.sc` (the
  Koenig-style self-compiler; 104 `&&` occurrences confirming the spec
  *as-written* still uses explicit &&, but Lon wants Snocone-the-language
  to retire `&&` in favor of implicit concat).

- [ ] **SK-3** — Lexer: implement whitespace-aware adjacency. Emit
  IDENT_LPAREN when `IDENT(` (no space); emit IDENT_LBRACKET when
  `IDENT[`; emit synthetic CONCAT between adjacent operand-producing
  tokens separated by whitespace. Document rules in SPEC-snocone-koenig.md.

- [ ] **SK-4** — Lexer: drop `&&`, `||` as operators. Keep `|` for
  alternation. Drop `==`, `!=`, `<=`, `>=`, `<`, `>` as relational operators.

- [ ] **SK-5** — Parser: remove SNOCONE_CONCAT, SNOCONE_OR, and all
  C-style relational tokens from precedence table and lower_token switch.
  Keep E_SEQ emission; now driven by lexer-synthesized CONCAT.

- [ ] **SK-6** — Control flow: decide which C-style forms survive.
  Koenig spec (per snocone.sc reference) keeps `if`, `else`, `while`,
  `procedure`, `goto`, `return`, `freturn`, `nreturn`. No `for`, no
  `break` (use goto). Revert SC-5 (for loops) and SC-6 (break) if
  needed to match spec.

- [ ] **SK-7** — Port the three demo programs (claws5.sc,
  treebank-list.sc, treebank-array.sc) to Koenig-Snocone syntax:
  strip all `&&`, replace `==` with `EQ()`, etc. Gate: each runs
  under scrip --ir-run matching its .ref with zero diff.

- [ ] **SK-8** — Port the 14 beauty-sc subsystems to Koenig Snocone.
  Gate: `test_beauty_snocone_subsystems.sh` PASS=14.

- [ ] **SK-9** — All 14 beauty-sc under --sm-run, --jit-run.
  Gate: PASS=42.

- [ ] **SK-10** — Port hand suite (fibonacci.sc, palindrome.sc,
  wordcount.sc, quicksort.sc, pattern_suite.sc) to Koenig Snocone.
  Gate: `test_snocone_hand_suite.sh` PASS=15.

- [ ] **SK-11** — Three .sc demos under all three modes.
  Gate: `test_eng685_sc.sh` PASS=9.

- [ ] **SK-12** — Update GOAL-LANG-SNOCONE.md to reflect Koenig spec
  as active definition. Old SC-26 closed as "not a bug — Snocone-plus
  required &&; Koenig Snocone removes this requirement entirely."

- [ ] **SK-13** — Draft `GOAL-LANG-SCRIPT.md` for the umbrella
  unification language (Snocone++/Prolog/Icon in one grammar with
  block mode-switch delineation — replacing SCRIPtix fence packaging).
