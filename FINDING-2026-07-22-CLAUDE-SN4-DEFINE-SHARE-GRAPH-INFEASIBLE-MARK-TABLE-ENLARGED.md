# FINDING 2026-07-22 (Claude) — SN4: the DEFINE share-graph prescription is INFEASIBLE; mark table enlarged instead; beauty self-host has deeper walls

**Goal:** GOAL-SNOBOL4-BB. **Continues:** FINDING-2026-07-22-CLAUDE-SN4-BEAUTY-SELFHOST-ZLS-MARK-OVERFLOW.md (s124's "remaining fix").

## TL;DR
- The prior finding + LIVE CURSOR prescribed fixing beauty's zls mark-table overflow by making entry-in-main DEFINEs **share main's graph** (bb_idx + `proc_entry_node`), "IDENTICAL pattern to the LBL__ fix (s124)." **This is empirically INFEASIBLE for DEFINE procs** — proven below. It works for LBL__ (goto targets) but NOT for DEFINEs (called procs).
- **LANDED (safe, DIVERGE=0):** enlarge `ZLS_MAX_MARKS` 8192 → 65536 in `src/contracts/zeta_storage.c`. Keeps the original, correctly-framed per-DEFINE graphs; right-sizes the table for beauty-scale programs. Crosscheck unchanged from baseline (m3 302/8, m4 302/6, DIVERGE=0); sno smokes 7/7 ×2.
- **This removes the mark-overflow wall but does NOT achieve beauty self-host** — two deeper walls remain (optimizer O(n²) on the redundant DEFINE re-lower graphs; and a real frame-decoupling prerequisite). Mapped below.

## WHY SHARE-GRAPH IS WRONG FOR DEFINE PROCS (the core discovery)
LBL__ pseudo-procs and entry-in-main DEFINE procs look similar (both point at a main-program label), but they differ fundamentally:
- **LBL__ proc** = a *goto target*. `rt_goto_transfer` JUMPS to it; it runs **in main's existing frame** (nparams=0, dyn_scope=0). Sharing main's graph AND main's frame is correct.
- **DEFINE proc** = a *called* proc. It ALLOCATES its own frame on call (dynamic scope, dyn_scope=1, formals/locals). Its frame size comes from the emitted graph's `nslots`. Sharing **main's** graph hands the DEFINE **main's `nslots`** — i.e. main's whole-program frame.

For a tiny main this is merely wasteful and works. For beauty (huge main) it is fatal:
- Minimal repro `/tmp/def_entry.sno` (one `DEFINE('DBL(X)')` entry-in-main): share-graph + the mode-3 `proc_entry_node` change (below) → m3 outputs `42`/`200`, **byte-matches SPITBOL oracle**. Correct.
- beauty (after clearing mark overflow + pool): **SIGBUS** at emitted instruction `mov %rsp, 0x3b3f8(%rsp)` — a frame-setup store 0x3b3f8 (≈240 KB = main's frame) above rsp, past the stack top. rip is in the sealed RX code pool (valid JIT), so it is a **frame-size mismatch**, not corrupt code. A called DEFINE inheriting main's 240 KB frame also blows the stack under beauty's recursion even if the store were in-bounds.

Conclusion: sharing main's graph conflates "which code to emit" with "how big a frame to allocate." That is acceptable for goto-targets (LBL__) and wrong for called procs (DEFINE). **Keep per-DEFINE graphs** (each gets its own correctly-scoped frame) and solve the mark overflow by capacity, not by sharing.

## WHAT WAS LANDED
`src/contracts/zeta_storage.c`: `#define ZLS_MAX_MARKS 8192` → `65536`.
- `zls_group_mark(g,label)` (the sole call site is `sno_build_graph`, lower_snobol4.c:~1740) pushes one mark per label per graph build; `zls_reset` zeroes the counter per compilation, so 8192 is the ceiling WITHIN one compile.
- beauty: main (163 labels) + ~39 entry-in-main DEFINEs each re-lowering the full array (×163 marks) + patterns ⇒ > 8192, aborting mid-lowering before any output.
- 65536 (~24 B/entry ≈ 1.5 MB static) comfortably covers beauty with headroom. Capacity-only: emitted code (.s) is byte-identical; the crosscheck (small programs) is unaffected — validated identical to baseline.

## VALIDATION (landed change only)
- `scripts/test_smoke_snobol4.sh`: PASS=7 FAIL=0, both modes.
- `scripts/test_crosscheck_snobol4.sh`: **m3 302/8, m4 302/6, DIVERGE=0** — IDENTICAL to pristine HEAD (mark-enlarge is invisible to these programs). No regression. (Pre-existing fails 140/141 pat_eval, 214/215/216 indirect_goto, and m3 1020/1021 code_* are tracked, not introduced here.)

## READY, HIGH-VALUE FOLLOW-UP: the mode-3 LBL__ `proc_entry_node` fix (NOT landed — needs a paired m4 fix)
Mode-4 emits procs from `proc_table[_pi].proc_entry_node` (scrip.c:~1150). **Mode-3 sno emits from `s2->bbp.table[idx]->entry` (scrip.c:~1331) — it IGNORES `proc_entry_node`.** So LBL__ pseudo-procs (which share main's bb_idx and carry their true entry in `proc_entry_node`) emit from main statement 0 in mode-3 — latently WRONG. One-line fix:
```c
IR_t * _pentry = s2->proc_table[_pi].proc_entry_node ? s2->proc_table[_pi].proc_entry_node : s2->bbp.table[idx]->entry;
bb_box_fn pfn = emit_chain(_pentry, NULL, "proc_flat");   // was: emit_chain(s2->bbp.table[idx]->entry, ...)
```
Measured effect (crosscheck): **m3 FAIL 8 → 3** — FIXES `1020_code_label_transfer`, `1021_code_direct_goto`, `214/215/216_indirect_goto`. BUT it then **exposes DIVERGE=3**: m3 now PASSES 214/215/216 while **m4 still FAILS them** (a pre-existing, independent m4 indirect-goto bug — m4 already honors proc_entry_node, so its failure is unrelated to LBL__). To land with DIVERGE=0, pair this with an **m4 indirect_goto fix (214/215/216)**. High value: net +5 m3, +3 m4 once paired. Fallback hatch not needed — NULL proc_entry_node falls back to `->entry` unchanged (Icon/Prolog/Raku/body-DEFINEs unaffected).

## REMAINING WALLS TO BEAUTY SELF-HOST (in the order beauty hits them, all previously hidden behind the mark overflow)
1. **Mark overflow** — FIXED here (enlarge table).
2. **Optimizer O(n²) blowup (timeout).** `optimizer_run` (scrip.c:1303) runs on every bbp graph. Own-graph DEFINEs mean ~39 FULL 163-statement graphs. Each optimizer pass uses a linear `*_index_of` (`for i in g->n: if g->all[i]==p`) called per-node-operand ⇒ O(n²) per graph × 39. gdb-sampled hangs in `dp_run` (dead_pure.c) and `bc_run` (branch_chain.c). **Six identical sites:** `dp_index_of`, `bc_index_of`, `cp_index_of` (copy_prop), `dg_index_of` (dead_goto), `pf_index_of` (pat_fold), `rr_idx_of` (region_report). Fix: make index_of O(1). IR_t has no spare id field (adding one is invasive — layout/GC), so the safe route is a per-graph node→index map built once per pass, or dedup the ~39 structurally-identical DEFINE graphs (they differ ONLY in entry). NOTE: beauty was NOT run past this wall, so the correctness of own-graph DEFINE frames at beauty scale is UNVERIFIED — check for a frame issue here too once the optimizer is fast.
3. **Emit buffer pool (4 MB) exhaustion** for CODE programs. LBL__ procs share main's graph and each emits a SUFFIX ⇒ O(n²) emitted bytes. With shared DEFINEs the measured peak was 7.80 MB; `BB_POOL_SIZE` is 4 MB (bb_pool.h). Trivial bump (mmap is lazy) once emission is reached; re-measure with own-graph DEFINEs. `emit_chain` returns NULL only on `bb_alloc` NULL (pool) or blob > `FLAT_BUF_MAX` (256 KB) — both reset per call, so it is purely a pool-size issue.
4. **LBL__ m3 correctness + m4 indirect_goto parity** — the follow-up above.

## RECOMMENDATION
Two coherent paths to beauty self-host; pick per appetite:
- **(A) Frame-decoupling for share-graph.** Let a DEFINE proc emit from a shared graph BUT size its frame to only the slots reachable from its entry (not main's total nslots). This single change would collapse walls 1–3 together (one graph, few marks, few blobs, correct small frames) and matches the LBL__ comment's stated intent ("one graph, N entry points"). Larger, architectural (slot assignment is currently graph-global). Best long-term.
- **(B) Own-graphs, incremental.** Keep the landed mark-enlarge; then (b1) make optimizer index_of O(1) (or dedup identical DEFINE graphs); (b2) bump the emit pool; (b3) land the mode-3 LBL__ `proc_entry_node` fix + an m4 indirect_goto fix. Several small rungs; each independently testable. Lower risk, more commits.

## KEY PATHS
- `src/contracts/zeta_storage.c:17` — `ZLS_MAX_MARKS` (landed 65536); `:40` overflow abort; `:38` `zls_group_mark`.
- `src/lower/lower_snobol4.c:2116-2146` — DEFINE loop; `:2129-2133` entry-in-main branch (KEPT as original own-graph re-lower); `:2096-2115` landed LBL__ share (correct — goto targets).
- `src/driver/scrip.c:1331` — mode-3 sno proc emit from `->entry` (the proc_entry_node gap); `:1150` mode-4 uses proc_entry_node; `:1303` optimizer_run loop.
- `src/machine/bb_pool.c` / `bb_pool.h:7` — `BB_POOL_SIZE` (4 MB); `bb_alloc` bump-alloc; `bb_pool_trim_last` reclaims each blob's unused tail.
- `src/optimizer/{dead_pure,branch_chain,copy_prop,dead_goto,pat_fold,region_report}.c` — the six O(n) index_of sites.
- Acceptance: `scrip --run beauty.sno < beauty.sno` (from corpus/programs/snobol4/demo/beauty/) → 622 lines, md5 `9cddff2534472b822438801d8db58a99`. Oracle: `/home/claude/x64/bin/sbl -b`.

## BUILD/ENV NOTES
- Toolchain via `scripts/install_system_packages.sh` (build-essential, libgmp-dev, m4, nasm, wabt, bison, flex). gdb also needed for segfault triage: `apt-get install -y gdb`.
- `emit.o` and `bb_pool.o` link into `scrip` (mode-3 emits in-process), so emitter/pool debugging only needs `make -j4 scrip` (fast), not the ~111 s `libscrip_rt.so` build. `zeta_storage.c` is a contract — rebuild both for a coherent runtime.
- `time` is unavailable in dash (harmless).
