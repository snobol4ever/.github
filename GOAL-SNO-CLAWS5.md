# GOAL-SNO-CLAWS5.md — demo_claws5 PASS

**Repo:** one4all
**Parallel:** This goal runs in its own session simultaneously with GOAL-SNO-TREEBANK-ARRAY
and GOAL-SNO-TREEBANK-LIST. All three sessions share main — pull --rebase before every push.
Fixes to shared files (interp.c, bb_boxes.c, stmt_exec.c) benefit all sessions immediately.

**Done when:** `demo_claws5` passes in `test_interp_broad_corpus_and_beauty.sh`;
output matches `corpus/programs/snobol4/demo/claws5.ref` under `--ir-run`.

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
bash /home/claude/one4all/scripts/test_smoke_snobol4.sh          # PASS=7
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh   # PASS=49
```

---

## Program

```
corpus/programs/snobol4/demo/claws5.sno
Input:  corpus/programs/snobol4/demo/CLAWS5inTASA.dat
Ref:    corpus/programs/snobol4/demo/claws5.ref
Oracle: CSNOBOL4 -bf -P 500k  (double-function trick; SPITBOL -f is broken)
```

Run to test:
```bash
DEMO=/home/claude/corpus/programs/snobol4/demo
timeout 30 /home/claude/one4all/scrip --ir-run $DEMO/claws5.sno \
    < $DEMO/CLAWS5inTASA.dat 2>/dev/null | diff - $DEMO/claws5.ref
```

---

## Known state (2026-04-17)

**BAL is implemented** on main. Pull at session start.

**Blocker 1: case-sensitive label dispatch.**
claws5.sno uses `push_list`/`Push_list` (and `push_item`/`Push_item`,
`pop_list`/`Pop_list`). Same root cause as treebank-array/list.
`label_lookup()` in `src/driver/interp.c` uses `strcasecmp` — fix to `strcmp`.
Check if GOAL-SNO-TREEBANK-ARRAY has already landed this; pull and check.

**Blocker 2: TABLE of TABLE subscript (claws5-specific).**
claws5.sno builds `tag_freq[sentence][word/tag]` — a TABLE whose values are
TABLEs, subscripted with string keys. Verify this works after the label fix;
isolate if a further bug exists.

**Current scrip symptom:** `Pattern match failed` — the main parse pattern
fails entirely, producing no output. Likely the `push_list`/`Pop_list` mis-dispatch
causes the pattern-function stack to corrupt, which then causes a match failure.
After the label fix, re-run and re-diagnose.

**ref file note:** `claws5.ref` was verified against CSNOBOL4 `-bf -P 500k`.
The ref contains output for the full `CLAWS5inTASA.dat` input (5622 lines in ref).
SPITBOL cannot run claws5.sno (broken `-f`); CSNOBOL4 is the sole oracle.

---

## Steps

- [x] **C5-1** — `label_lookup` strcasecmp→strcmp applied. BB-3 (bb_callcap
  DESCR_t return type UB) also fixed. Both landed on main HEAD 6ee09b7f.
  Gates: smoke PASS=7, broker PASS=49. claws5 now produces output.

- [ ] **C5-2** — Diff claws5 output against ref. Fix divergences.
  BLOCKER: first ARBNO iteration delivers empty wrd/tag to add_tok().
  Subsequent iterations correct. Minimal reproducer:
    ARBNO( (NOTANY('_') BREAK('_')) . wrd '_' (ANY(UCASE) SPAN(DIGITS UCASE)) . tag
           (epsilon . *add_tok()) ' ' )
  on 'That_CJT the_AT0 ' — first iteration: wrd=[], tag=[] (scrip) vs
  wrd=[That], tag=[CJT] (oracle).
  Root cause: bb_arbno iteration-boundary save/restore in stmt_exec.c ~line 908
  appears to shadow first-iteration captures before NAM_commit fires callcap.
  Investigate bb_arbno, focus on capture state at ARBNO iteration 1 vs 2+.

---

## Key files

| File | Role |
|------|------|
| `src/driver/interp.c` | `label_lookup`, TABLE/array eval |
| `src/runtime/x86/bb_boxes.c` | `bb_bal` (already implemented) |
| `corpus/programs/snobol4/demo/claws5.sno` | Program under test |
| `corpus/programs/snobol4/demo/claws5.ref` | Expected output |
| `corpus/programs/snobol4/demo/CLAWS5inTASA.dat` | Input data |

---

## Invariants

- CSNOBOL4 `-bf -P 500k` is oracle (SPITBOL `-f` broken).
- Never patch corpus source. Fix the runtime.
- Smoke PASS=7, Broker PASS=49 after every commit.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.
- Pull --rebase before every push (parallel sessions active).

---

## Current state (2026-04-17, one4all HEAD 6ee09b7f)

C5-2 next. C5-1 done + BB-3 (bb_callcap UB) fixed.
BLOCKER: ARBNO first-iteration captures empty in scrip — see C5-2 above.
