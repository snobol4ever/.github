# FINDING-2026-08-24-seat06-defer-nv-read-by-pointer-already-landed-repin

FROM seat06 (`/home/claude06`), 2026-08-24. Queue row `defer-nv-read-by-pointer-not-name` (rank 0), task baton
`/home/resources/postoffice/tasks/defer-nv-read-by-pointer-not-name.task.md`.

## The claim

**DONE-WHEN already passes, and did before this session started.** The narrow cure this row asked for --
"keep the deferral, kill the by-name resolution: resolve `T` to its `vrblk`/slot once when the deferred node
is built, have `rt_defer_nv_read` follow a pointer instead of a string" -- was already designed and landed by
hq_P at sessions s260 ("one resolution per deferred node, not two") and s261 ("SPITBOL's vrblk discipline for
the deferred name") **before** hq_C converted this row's QUEUE.tsv prose into a task baton later the same day
(2026-08-22). The baton's BRIEF section is a verbatim copy of the original pre-cure FINDING
(`FINDING-2026-08-22-hq_P-roman-is-one-defer-site-54-percent.md`) and was never refreshed against the code that
landed the same day, so the row sat open describing a problem that was already fixed. This session's job was
verification and closure, not new design.

## What this session actually did

1. Read the brief, then read the current `src/runtime/pattern_match.c` and `src/templates/bb_match_defer.cpp`
   before touching anything. Found `rt_defer_cell_read` (pattern_match.c:1179) -- a per-construction-site cache
   keyed on `(baked varname pointer, site)`, self-validating, filled via `NV_PTR_fn` (the stable-cell accessor,
   valid for the life of the program per core.c's own bump-allocator/no-move guarantee) -- and, one step further,
   `bb_match_defer.cpp`'s `msite`/`defer_inline()` arm, which inlines the common-case read directly into emitted
   code with **no call at all** (~18 instructions: validate the cached (key,cell) pair, confirm a one-character
   string, compare against the subject at the cursor). Both are hq_P s260/s261 work, both default-ON
   (`SCRIP_DEFER_MERGE`, undocumented-as-off `defer_inline()`), neither reverted since.
2. Did not trust the reading alone. `git pull --rebase` on both SCRIP and `corpus` (this seat had neither at
   HEAD), `make pristine` (HQ-27, required before any gate verdict), then ran the literal DONE-WHEN:
   `ROMAN_IR_WATERMARK=20270000 bash scripts/test_gate_instr_budget.sh`.
3. First run failed with `GATE FAIL(2): roman mode-4 compile produced nothing -- scrip: cannot open
   '.../corpus/demo/roman.sno'`. Root cause: `corpus`'s beauty directory was dissolved back into `demo/` earlier
   the same day (corpus `b131a913`, Lon s271: "beauty_classic.sno IS the correct beauty.sno and moves to demo/;
   beauty/ dissolved"), but `test_gate_instr_budget.sh`'s `BEAUTY_DIR` still pointed at the now-nonexistent
   `$CORPUS_ROOT/beauty` (set by an earlier repoint, SCRIP `8c564966`/`1177e66e`, that predated the dissolution).
   This is the same "tree moved under the last fix" churn this file has already been repointed for twice this
   week -- not a defect in this row's cure, and not this row's problem to have caused, but it blocked getting
   ANY verdict, so it was fixed in place (one line, `scripts/test_gate_instr_budget.sh`): `BEAUTY_DIR="$CORPUS_ROOT/beauty"`
   -> `BEAUTY_DIR="$CORPUS_ROOT/demo"`.
4. Re-ran. **`GATE OK`, exit 0, twice**, `ROMAN_IR_WATERMARK=20270000`: `roman: Ir=10225516`, byte-identical
   both runs (Ir is exact and reproducible per the gate's own header comment), output matches `roman.ref`.
   `beauty` also passed its own budget and stayed at the MILESTONE-1 fixed point, so the pristine build is
   healthy generally, not just on the one workload this row cares about.
5. For a receipt in the same shape as the original FINDING (not just a total, the actual mechanism), compiled
   `roman.sno` to mode-4, linked, and ran `valgrind --tool=callgrind --separate-callers=2` directly (SCRIP
   `1a9cc1bc`, corpus `b131a913`). **`NV_GET_fn'rt_defer_nv_read`, 19.35% in the original FINDING, does not
   appear as a hot line at all.** The only surviving `rt_defer_cell_read -> NV_PTR_fn` calls in the whole
   annotated trace are a handful of `(1x)` cold-path cache-population hits (one per construction site, first use
   only) at ~0.00% each -- exactly the "resolve once, then follow a pointer" shape the brief asked for, and
   consistent with the inlined fast path serving essentially every subsequent re-read with no C call at all.
   PROGRAM TOTALS: 10,224,052 Ir (this run; the tiny ~1,500 Ir wobble against the gate's own 10,225,516 is
   `--separate-callers=2`'s own bookkeeping overhead, not a correctness or determinism issue -- the gate's own
   plain-callgrind number was bit-identical across two separate runs).
6. **Re-pinned `ROMAN_IR_WATERMARK` from 22522863 to 10225516** (`scripts/test_gate_instr_budget.sh`) -- then hit
   a rebase conflict on that exact line: hq_P (s272) had independently landed the identical class of fix upstream
   moments earlier (commit `22971235`, "a CAMPAIGN, not a commit"), re-pinning the same watermark to 10224491 via
   a full bisected ladder across every commit from the old pin's tree to HEAD, each arm individually re-measured
   at -O0 rather than summed from commit messages' own (mixed -O2) figures. Their number and this session's
   converge within noise (10224491 vs this session's 10225516/10224807/10224052 across three separate runs) but
   their derivation is strictly more rigorous, so **the resolution keeps hq_P's ladder and value as the pinned
   fact** (ONE AUTHORITY per fact -- this file's own RULES.md digest) and this session's commit shrank, post-merge,
   to a four-line cross-reference appending seat06's independent corroboration (the `--separate-callers=2` mechanism
   check in particular, which the ladder commit does not include) rather than a competing re-pin. Landed as SCRIP
   `d5079507`, on top of hq_P's `22971235`. Post-merge, a clean no-override run of the gate is `GATE OK` with
   `roman` reporting `OK` (not `NOTE`) against the pinned 10224491, confirming the pin is tight but not flapping.

## Not claimed here

- **`BEAUTY_IR_WATERMARK` was left untouched.** The same gate run reports `NOTE beauty: Ir=1897162992 < budget
  2215545392 ... improved; consider re-pinning down` (roughly 14-15% below its pin) across several runs, and
  beauty's Ir was **not** bit-reproducible run to run in this session's measurements (1898321881 / 1890162282 /
  1897162992, ~0.4% spread) where roman's was exact. Both are real observations but neither is this row's
  mechanism (beauty's pattern load is not the single dense unanchored bare-variable defer this row targeted) and
  chasing either would be a different row's work: a re-pin candidate, plus a small standing non-determinism worth
  its own look before anyone trusts a tight beauty pin. Left as a note for whoever picks that up, not fixed or
  claimed here.
- **No runtime/emitter code was changed this session.** The cure is entirely hq_P's (s260/s261, already on
  `main` before this row's baton existed). This session's diff is two lines in one test script (a stale-path
  repoint + a watermark re-pin) plus this FINDING and the task baton's own LEDGER/NEXT.
- The wide cure (stop deferring bare `TT_VAR` at `lower_snobol4.c:1398`, worth up to the full 54% instead of the
  ~54% already realized via the narrow path) remains exactly as blocked as the original FINDING said: on hq_C's
  open correctness ruling. Not touched, not needed -- the narrow path already met this row's DONE-WHEN with
  headroom to spare (10.2M measured vs 20.27M asked for, 2.2x under).

## Receipts

- `ROMAN_IR_WATERMARK=20270000 bash scripts/test_gate_instr_budget.sh` -> exit 0, `roman: Ir=10225516`
  (reproduced identically twice), correctness OK, `make pristine` build, SCRIP `1a9cc1bc` / corpus `b131a913`.
- `valgrind --tool=callgrind --separate-callers=2` on the same binary: PROGRAM TOTALS 10,224,052 Ir, output
  byte-identical to `roman.ref`, `NV_GET_fn'rt_defer_nv_read` absent from the hot-line list (was 19.35%).
- Post-repin no-override gate run: `GATE OK`, all four workloads `OK` or a `NOTE`-only improvement (beauty),
  zero `FAIL`.
