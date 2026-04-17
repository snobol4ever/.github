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

## Known state (2026-04-17 — post C5-3)

**BAL is implemented** on main. Pull at session start.

**C5-3 FIXED** (bb_seq accumulation bug, see step below).
**C5-4 DIAGNOSED NOT FIXED** — typed SORT comparator landed, but keys reach
sort as DT_S because `_aset_impl` uses `table_set` (string-coerce) rather than
`table_set_descr`. Next session: route `_aset_impl` through `table_set_descr`
with the live key descriptor.

**ref file note:** `claws5.ref` is currently 95 lines (sentences 1-4 only).
Full 989-line input under scrip now runs to completion producing 5622 lines.
To validate the whole output, extend claws5.ref against CSNOBOL4 `-bf -P 500k`
after C5-4 lands (string vs numeric sort order will otherwise differ).

---

## Steps

- [x] **C5-1** — `label_lookup` strcasecmp→strcmp applied. BB-3 (bb_callcap
  DESCR_t return type UB) also fixed. Both landed on main HEAD 6ee09b7f.
  Gates: smoke PASS=7, broker PASS=49. claws5 now produces output.

- [x] **C5-2** — NAM_commit callcap-boundary fix landed. Sentence 1
  byte-perfect; 830 good lines on 142-line input prefix.
  HEAD 58e642f1.

- [x] **C5-3 DONE** — bb_seq `left_γ` now replaces ζ->matched with the latest
  left result instead of accumulating via spec_cat.
  Root cause: on the `SEQ_β → right_ω → left_γ` retry loop,
  `ζ->matched = spec_cat(ζ->matched, lr)` added left's absolute-length
  result to the prior matched δ each iteration, producing runaway match
  lengths (δ=22 on 7-char subject "enough'"). That made
  `match_start = Δ − δ = −15`, passed as `size_t` to memcpy in
  stmt_exec.c Phase 5 → SEGV mid-pp_mem at sentence 37. The canonical
  Boehm signature `Failed to expand heap by 0x3FFFFFFFFFFFFC KiB` came
  from the matching `GC_MALLOC((size_t)new_len + 1)` where new_len = −15.
  Fix: single-line change, `ζ->matched = lr` at left_γ (bb_boxes.c).
  Verified:
    * 16-line input: byte-match vs ref preserved
    * 143-line input: was SEGV 617 trunc → now exit 0, 837 lines
    * full 989-line input: was SEGV 0 lines → now exit 0, 5622 lines
    * smoke PASS=7, broker PASS=49, broad corpus+beauty PASS=218/228 (unchanged)
    * Both `--ir-run` and default SM-mode benefit (shared box code).

- [~] **C5-4 PARTIAL** — Typed SORT comparator written in
  `src/runtime/x86/snobol4_pattern.c` per SPITBOL manual pp.240–241
  (int-int algebraic, str-str lex, cross-type by type-rank ordering
  `array, code, expression, integer, keyword, name, pattern, real, string, table`).
  Preserves DESCR_t key types in result array col 1.
  Compiles clean, no regressions.
  **BUT output still in string order** because the outer `mem[sentno]=TABLE()`
  store coerces the DT_I key to DT_S before it reaches the table.
  Minimal repro:
  ```snobol4
    T=TABLE(); T[1]='a'; T[10]='b'; T[2]='c'; S=SORT(T)
    * DATATYPE(S[1,1]) → 'STRING' in both --ir-run and SM modes
  ```
  Root cause: `stmt_aset` → `_aset_impl` → `table_set` (string-coerce),
  not `table_set_descr`. `table_ptr` (used by other paths) already
  preserves the descriptor.
  Next session: edit `_aset_impl` (in `snobol4.c`, binary-flagged file —
  use `grep -an` on already-located call chain) to call `table_set_descr`
  with the original key DESCR when setting a TABLE slot. Then re-run
  full 989-line input and regenerate `claws5.ref` from CSNOBOL4.

---

## Key files

| File | Role |
|------|------|
| `src/driver/interp.c` | `label_lookup`, TABLE/array eval |
| `src/runtime/x86/bb_boxes.c` | `bb_seq` (C5-3 fix), `bb_bal` |
| `src/runtime/x86/snobol4_pattern.c` | `sort_fn` (C5-4 typed comparator) |
| `src/runtime/x86/snobol4.c` | `table_set` / `table_set_descr` / `table_ptr` / `_aset_impl` (C5-4 store-side fix target) |
| `src/runtime/x86/snobol4_stmt_rt.c` | `stmt_aset` / `stmt_aset2` |
| `corpus/programs/snobol4/demo/claws5.sno` | Program under test |
| `corpus/programs/snobol4/demo/claws5.ref` | Expected output (currently scoped to sentences 1-4) |
| `corpus/programs/snobol4/demo/CLAWS5inTASA.dat` | Input data |

---

## Invariants

- CSNOBOL4 `-bf -P 500k` is oracle (SPITBOL `-f` broken).
- Never patch corpus source. Fix the runtime.
- Smoke PASS=7, Broker PASS=49 after every commit.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.
- Pull --rebase before every push (parallel sessions active).

---

## Current state (2026-04-17, one4all HEAD 2fa59c88 — post C5-3)

C5-3 DONE. C5-4 partial (typed sort landed; store-side key-descr
preservation in `_aset_impl` next). Full 989-line CLAWS5inTASA.dat
now runs to completion in both --ir-run and --sm-run with 5622 lines of
well-formed output. Byte-match vs the scoped 4-sentence ref is preserved
on the 16-line input prefix in both modes.
