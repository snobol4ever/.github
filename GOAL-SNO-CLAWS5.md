# GOAL-SNO-CLAWS5.md — demo_claws5 PASS

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** SCRIP
**Parallel:** This goal runs in its own session simultaneously with GOAL-SNO-TREEBANK-ARRAY
and GOAL-SNO-TREEBANK-LIST. All three sessions share main — pull --rebase before every push.
Fixes to shared files (interp.c, bb_boxes.c, stmt_exec.c) benefit all sessions immediately.

**Done when:** `demo_claws5` passes in `test_interp_broad_corpus_and_beauty.sh`;
output matches `corpus/programs/snobol4/demo/claws5.ref` under `--interp`.

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh
bash /home/claude/SCRIP/scripts/build_csnobol4_oracle.sh
```

Gate after setup:
```bash
bash /home/claude/SCRIP/scripts/test_smoke_snobol4.sh          # PASS=7
bash /home/claude/SCRIP/scripts/test_smoke_unified_broker.sh   # PASS=49
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
timeout 30 /home/claude/SCRIP/scrip --interp $DEMO/claws5.sno \
    < $DEMO/CLAWS5inTASA.dat 2>/dev/null | diff - $DEMO/claws5.ref
```

---

## Known state (2026-04-17 — post C5-4)

**BAL is implemented** on main. Pull at session start.

**C5-1, C5-2, C5-3, C5-4 all DONE.**

**claws5.ref note:** extended from 95 lines (scoped to sentences 1-4) to the
full 5622-line authoritative CSNOBOL4 `-bf -P 500k` output. SCRIP
`--interp` and `--interp` are byte-identical to the oracle across the full
989-line input.

**demo_claws5 now PASS** in `test_interp_broad_corpus_and_beauty.sh`
(219/228, up from 218/228 baseline). Goal complete.

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
    * Both `--interp` and default SM-mode benefit (shared box code).

- [x] **C5-4 DONE** — subscript_set (snobol4_pattern.c) now preserves key
  descriptor for DT_T, routing through `table_set_descr(tbl, k, idx, val)`
  instead of `table_set(tbl, VARVAL_fn(idx), val)` which hardcoded
  key_descr to STRING.

  **Diagnosis differed from prior C5-4 plan.** Previous plan targeted
  `_aset_impl` in `snobol4_runtime_shim.h`, but instrumentation proved
  `_aset_impl` is off the path for statement-level T<k>=v: both --interp
  and --interp flow through `subscript_set()` in `snobol4_pattern.c:481`.
  `_aset_impl` already calls `table_set_descr` correctly but is dead code
  for this path. The one-line fix was at `snobol4_pattern.c:489` (plus
  explanatory comment).

  Typed SORT comparator (landed earlier in C5-4 partial) now sees typed
  keys and applies SPITBOL pp.240-241 ordering (int-int algebraic,
  str-str lex, type-rank cross-type).

  Verified:
    * Minimal repro T<1>='a';T<10>='b';T<2>='c';S=SORT(T):
      DATATYPE(S<i,1>) = INTEGER (was STRING); sort order 1,2,10 (was 1,10,2);
      byte-match vs CSNOBOL4 -bf in both --interp and --interp.
    * claws5 full 989-line CLAWS5inTASA.dat:
      --interp == --interp == CSNOBOL4 oracle (5622 lines, diff = 0).
    * `claws5.ref` extended from 95 lines (sentences 1-4) to authoritative
      5622-line CSNOBOL4 `-bf -P 500k` output.
    * smoke PASS=7, broker PASS=49 (unchanged).
    * broad corpus+beauty 219/228 (was 218/228 — demo_claws5 now PASS).

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

## Current state (2026-04-17, SCRIP HEAD 6c63908 — post C5-4)

C5-4 DONE. Fix: `subscript_set` (snobol4_pattern.c:489) preserves key
descriptor through `table_set_descr` instead of stringifying via
`VARVAL_fn(idx)` → `table_set`. Both interpreter modes now byte-match
CSNOBOL4 oracle across the full 989-line CLAWS5inTASA.dat (5622 lines,
diff = 0). `claws5.ref` regenerated from oracle.

Goal complete. demo_claws5 PASS in broad corpus suite (219/228).
