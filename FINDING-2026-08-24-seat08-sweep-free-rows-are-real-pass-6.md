# FINDING 2026-08-24 seat08 — sweep-free-rows-are-real, pass 6: net +3 (6 new / 3 gone), all verified; a stale-checkout trap and two citation-drift notes

**Seat:** `seat08` · **task:** `sweep-free-rows-are-real` (row-factory sweep, DONE-WHEN is a deliberate
permanent-refusal stub — see task file). **Repos at start of pass, BEFORE pulling:** SCRIP `28c2cfd5` /
corpus and `.github` similarly stale — this seat's first session, checkout had never been updated.
**AFTER fresh `git pull --rebase` all three (git status clean on all 3 first, safe fast-forward/rebase):**
SCRIP `1a9cc1bc` / corpus `c270b929` / `.github` `458c4bb2` — each repo's own hash, per the pass-2 lesson.

## Process note: a stale checkout is a trap for this exact method, and the picker does not warn you

Before pulling, direct-repro checks against the new rows below (cited commit hashes, a cited source line
number) mostly FAILED — 4 of 6 cited commits reported "not a valid object name," and a cited line number
(`by_name_dispatch.c:430`) landed in a completely unrelated function. At first read this looks exactly like
the false-positive class prior passes exist to catch (row cites something that isn't real). It wasn't: this
seat's SCRIP clone was ~70+ commits behind origin (last pulled before a `test/` tree deletion, an Icon
runtime rewrite, and a corpus `programs/snocone`→`snocone` rename all landed). Re-running the identical
checks after the pull resolved every one cleanly (details below). Recording this because "verify by direct
repro at HEAD" (the method every pass since pass 4 has used) is only meaningful if the seat's clone actually
**is** at HEAD — `s4e_msg.sh next` hands you a task, not a fresh checkout, and nothing in the loop protocol
pulls for you before you start reading source. A future pass that skips the pull risks writing up real rows
as dead on a false premise.

## Method: `SWEEP-CLASSIFIED.tsv` exact-diff, unchanged from pass 4/5

Regenerated true-free via the file's own header one-liner: **145** rows (was 142). Diffed against
`SWEEP-CLASSIFIED.tsv`:

- **+6 new**: `audit-rtx29-icon-table-int-chain-walk-post-s262`, `callgrind-ifunc-phantom-attribution`,
  `fc-register-caps-sized-by-guess`, `perf-replace-translate-loop-scalar-byte-copy`,
  `perf-table-subscript-fastpath`, `vlist-expr-alternation`
- **-3 gone**: `perf-string-runtime`, `perf-table-array-runtime`, `vlist-v05-m4-sigsegv-m3-m4-divergence`

Net **+3** (142 − 3 + 6 = 145, arithmetic checks out).

## Gone rows: all 3 correctly excluded, 0 defects

- `perf-string-runtime`: QUEUE.tsv `state=FREE` (owner column stale, as previously documented) but
  `claims/perf-string-runtime.claim` exists → claimed, correctly excluded from true-free.
- `perf-table-array-runtime`: QUEUE.tsv `state=SUPERSEDED` → correctly excluded. Consistent with
  `perf-table-subscript-fastpath`'s own citation that this row is "formally CLOSED by hq_C's ruling (s270)."
- `vlist-v05-m4-sigsegv-m3-m4-divergence`: QUEUE.tsv `state=FREE` but
  `claims/vlist-v05-m4-sigsegv-m3-m4-divergence.claim` exists → claimed, correctly excluded. (Pass 5
  investigated this exact row as a near-miss and confirmed it stays LIVE; someone has since claimed it.)

## New rows: all 6 verified LIVE by direct repro at fresh HEAD, 0 dead

1. **`audit-rtx29-icon-table-int-chain-walk-post-s262`** (rank 0) — hazard-audit row minted by seat01.
   Verified byte-accurate against current source, not just read: `.Lsub_table_int`/`.Lsub_bail`/
   `.Lsub_chain`/`.Lsub_cmp` all present in `rtx_icnsub.S` exactly as cited; the RTX-26 stand-down
   precedent (`jmp .Lsub_bail`) confirmed present; the struct-layout claim (`TBBLK_t.nbuck` a dynamic
   per-table power-of-two masking `hash&(nbuck-1)`, `TBBLK_t.buckets` is `TBBUCK_t **`, `TBBUCK_t` is a
   `{len,cap;ent[]}` dense-array header, `TBPAIR_t.next` retired) confirmed field-for-field against
   `src/runtime/core/core.h:130-170` (the task cites bare "core.h" — it lives under `src/runtime/core/`,
   not `src/contracts/`, worth knowing for whoever picks this up so they don't grep the wrong tree).
   Cross-corroborated independently: RTX-31's own new comment in `rtx_icnvar.S` (landed by the unrelated
   `perf-table-subscript-fastpath` row) references this exact hazard unprompted ("sibling fix in
   rtx_icnsub.S (RTX-31) now mints a (tbl,key_d) trap -- cellp==0..."). DONE-WHEN is an intentional
   refusal stub per the row's own STEP 1 — not a defect. No corrections.

2. **`fc-register-caps-sized-by-guess`** (rank 1) — minted hq_C s271. All seven register caps confirmed
   exact (vlit/vread/vbinop/save/vdj 256, vwpop 512, subj 64) against `src/contracts/zeta_storage.c`;
   `fc_vcap`'s 4-literal guard confirmed unchanged from the arrays it wraps, supporting the row's "raising
   is a codegen change, not a constant bump" framing. ⚠ **DONE-WHEN defect, real but already self-flagged
   as a placeholder — this sharpens it:** it invokes `/home/claude_C/.github/probes/tdump-r12/check_tdump_and_364.sh`,
   which exists only under seat `claude_C`'s home (confirmed absent from `claude08`'s) — a PORTABLE-HOME
   violation per this project's own workspace-map rule — **and** the script is a copy-paste from an
   unrelated row (`tdump-driver-r12-cas-mark-sigsegv`'s own probe), unconnected to fc_*_register caps or
   the 364/232/93 three-frontend grading this row's own brief calls for. Not fixed here: the row's NEXT
   steps 1-4 already commit to writing the real criterion (caps raised + `SCRIP_FC_REG_HIGHWATER` headroom
   shown + SNOBOL4/Icon/Prolog counts unchanged), so replacing the placeholder is that row's own first-class
   work, not a sweep-classification fix — row-factory discipline. Recording the precise defect so whoever
   takes the row doesn't spend time rediscovering the copy-paste independently.

3. **`perf-replace-translate-loop-scalar-byte-copy`** (rank 1) — minted seat04. The cited translate loop
   (`buf[i] = map[(unsigned char)sv[i]]`) confirmed present verbatim in `by_name_dispatch.c` — but at line
   **5112**, not the cited **430** (drift of ~4700 lines; the file is under heavy same-day churn in this
   exact area, unsurprising but worth flagging so the next reader doesn't `sed -n` the wrong function).
   Both DONE-WHEN gate scripts (`test_corpus_snobol4.sh`, `test_gate_instr_budget.sh`) exist and are
   current. No other corrections.

4. **`perf-table-subscript-fastpath`** (rank 1) — a released-not-fresh row: substantial verified work
   already landed by seat01 (lever 1: RTX-31 + RTX-NEW-ICNVAR asm fast paths for `T[I]=v`, ratio
   0.6834x→0.8643x, cross-checked per its own extensive LEDGER) before being released back to the picker —
   it dropped out of the pass-5 snapshot because it was claimed at that instant, not because the work is
   new. Confirmed RTX-31 (`rtx_icnsub.S:690`) and RTX-NEW-ICNVAR (`rtx_icnvar.S:157`) both present in
   current source. DONE-WHEN gate wiring confirmed (`test_gate_instr_budget.sh` references `table_access`
   11×). Cited commit `cb514dfa` not found at current HEAD post-pull — its own LEDGER says "rebased,
   pushed" without citing the post-rebase hash, reading as citation drift from a rebase rather than a
   fabricated commit (same benign class as #5 below, which self-documents the same thing). Row is still
   open pending HQ's close-vs-continue-lever-2 call (its own QA section, topic
   `perf-table-subscript-fastpath-status`) — not this sweep's decision.

5. **`vlist-expr-alternation`** (rank 1) — large, heavily-worked ongoing investigation (3+ sessions,
   seat03), not a phantom mint. Cited commit `048df3c3` is explicitly self-documented in the task's own
   NEXT block as rebased to `822bc8a1` — confirmed `822bc8a1` exists at current HEAD. Linked FINDING
   confirmed present (47KB, substantial). DONE-WHEN's probe files
   (`corpus/probe/vlist/vlist_expr_alternation.{sno,ref}`) confirmed present post the corpus
   `programs/snocone`→`snocone` rename (different subtree, unaffected). No corrections; still genuinely
   open (the `disj_sigma_copy` addressing gap, per its own NEXT).

6. **`callgrind-ifunc-phantom-attribution`** (rank 2) — minted seat04, split off `perf-string-runtime`.
   Linked FINDING confirmed present (12KB). Core technical claim (a `gdb` breakpoint on `__strchr_avx2`
   never fires despite callgrind attributing it real cost) not independently re-derived this pass — doing
   so needs a fresh valgrind+gdb run, out of scope for a classification pass under row-factory discipline;
   this is itself an open-mechanism row whose own DONE-WHEN is an intentional refusal stub pending its own
   STEP 1. Content internally consistent and well-cited; nothing contradictory found.

## Sanity checks (same as passes 1-3)

0 duplicate topic rows in QUEUE.tsv (175 data rows total, up from 155 at the s256 baseline). 65 claim
files total (not individually chased — same as pass 3's practice, out of this row's scope).

## Cadence data point (not this row's call to make)

Pass 5 measured Δ0(net) (+1/−1) and flagged that as possible evidence sub-daily cadence had stopped
earning its cost. Pass 6 (this pass) measured **Δ+3(net)** (+6/−3), all real, 0 corrections needed to any
row's core content. HQ's open cadence question (event-driven vs. clock-driven, raised pass 4) remains
unresolved by this data point either way — six genuinely new, well-formed rows minted since pass 5 argues
against "nothing is happening," even though pass 5 itself showed net-zero one pass earlier. Both data
points are true; cadence is HQ's call, not derivable from one more sample.

## Churn-during-the-pass, noted not chased

Self-verifying the freshly-written baseline against a second, later true-free regeneration (run
immediately after writing the file, ~15-20 minutes after this pass's original snapshot — the gap is this
pass's own read+verify time, six task files plus a `git pull --rebase` on three repos) found 3 more rows
had dropped out: `conform-defer-tab-span-crash`, `defer-nv-read-by-pointer-not-name`,
`nul-in-counted-strings-class-defect` — all three now show a `claims/*.claim` file that did not exist at
snapshot time. Confirmed as ordinary mid-pass claim activity by other seats, not a bug in this pass's
method (all three were already correctly-classified `INHERITED` rows from before pass 4; nothing about
their own content needed re-verification). Not re-chased into a second file rewrite — a baseline is a
snapshot, not a moving target, and pass 7 will pick this delta up on its own next diff. Recording it mainly
as a concrete churn-rate data point for HQ's cadence question above: 3 claims landed in the ~15-20 minutes
this single pass took to run.

## Baseline rewritten for pass 7

`/home/resources/postoffice/SWEEP-CLASSIFIED.tsv`, 145 topics, at SCRIP `1a9cc1bc` / corpus `c270b929` /
`.github` `458c4bb2` (each repo's own hash).
