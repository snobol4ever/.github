# FINDING 2026-09-02 (hq_C) — nine dead Prolog globals, the `g_zeta_mode` compare in the `$trail_mark` sink, and the 268 KB `g_resolve_bb_table` leave the runtime image with zero behaviour change; the edit survived the comment sweep because its anchors were code, and the one red conjunct was the box's, not the rung's

**Tree:** SCRIP `d42d2918` (the rung) + `2748100d` (the watermark re-pin, one commit later) on top of `922cfaf4` (ceo's R5 sweep) · corpus `a0cca818` (prolog-bench regen) · .github `c34bab88` · `RT_OPT=-O0` · MODE `DUO` (file read). Row `prolog-dead-globals-and-bb-table-out-of-runtime-image` (ceo brief `prolog-byrd-box-redesign-standup` (d); denominator `FINDING-2026-09-02-ceo-prolog-only-globals-census-…`, struck there in the same push).

## What landed (11 files, +30/−90)

1. **The nine dead globals of census § C deleted:** `g_pl_yield_seq`, `g_resolve_b3_call_mark`, `g_resolve_tail_redirect_cfg`, `g_resolve_tail_redirect_entry` (rt_runtime.c) · `g_halt_rc`, `g_halt_set` (runtime_init.c) · `g_pl_catch_nodes[]`, `g_pl_catch_n`, their private `PL_CATCH_MAX` (emit.cpp) · `g_fi8_pl_init_count` (polyglot.c/.h, its one `++` with it).
2. **The `g_zeta_mode` compare deleted from the `$trail_mark` sink** (`bb_call_fn.cpp`): the `lea r12,[g_zeta_mode]; mov eax,[r12]; cmp eax,2; je` quartet and the file's `extern`. ZETA HAS NO MODES — the global is the constant `ZC_ZETA=1`, the branch it selected was untakeable.
3. **`g_resolve_bb_table` + `g_resolve_bb_count` out of `libscrip_rt.so`:** the name→bb_idx registry was written and read only by `lower_prolog.c` at compile time; it is now that file's private lazily-`calloc`'d table (`pl_bb_tab`/`pl_bb_n`, 24-byte entries, `pl_bb_lookup`/`pl_bb_register`). `resolution.c` loses the storage and five accessors (three had zero callers); `resolution.h` loses `RESOLVE_SCOPE_SLOT_MAX`, `RESOLVE_BB_TABLE_MAX`, `PlScopeEnt`, `PlScope`, `Resolve_PredEntry_BB`, `bb_graph_of_pred` and six prototypes incl. the never-defined `resolve_bb_graph_at`; `scrip.c` loses eight dead `extern` lines (two for functions that never existed); `emit.h` one.

**Variable accounting (NO-NEW-GLOBALS):** two exported globals OUT (268 KB), two file-statics IN (a pointer and a count, 16 bytes, private to one TU) — a move, not an addition. Flagged to ceo as the veto point; if ruled a new variable, the fallback is a static array in the same TU (nm-invisible, bss unchanged).

## Measured, one pristine `-O0` binary per arm

| instrument | before (`922cfaf4`) | after (`d42d2918`) |
|---|---|---|
| `size out/libscrip_rt.so` bss | 81,651,024 | 81,382,160 (**−268,864 = the table, byte-exact**) |
| text | 8,064,966 | 8,062,834 |
| `.s` of `chain2b.pl` / `nested.pl` / `deep.pl` (m4) | 2 / 3 / 2 quartets | diff = exactly `lea+mov+cmp+je` × sinks removed, **0 lines added** |
| corpus prolog-bench regen | — | 23 files, **312 deletions, 0 insertions** (= 3 text lines × 104 sinks; benchmarks + demos unchanged) |
| `grep -rnw g_zeta_mode src` | 2 (definition + the sink's extern) | **1 — the definition only** (`zeta_alloc.c`) |
| DONE-WHEN arms A+B (17 names absent from `src/` and `nm -D`) | — | pass |
| `strip_comments.py --check` (R5 law) | — | 389 files, 0 offenders |
| Prolog smoke / rung13 / rung14 / rung15 | 5/5/5 · 5/0 · 3/2 · 4/1 | **identical, name-for-name** (rung14/15 reds are the PZ-4 pair + `abolish_then_reassert`, pre-existing) |
| SNOBOL4 blocking board (control arm) | — | **m3 1679/1679 · m4 1679/1679 · FAIL=0 SKIP=0 MISSING=0** |
| `make test` remaining gates | — | capture-stdin OK · Term ratchet OK (0) · emit-no-lang OK · medium-invisible OK · corpus-coverage OK |
| `make test` last gate, optbypass watermark | **192/1656 vs pin 191 (RED)** | **192/1656 (identical)** |

The witnesses' run behaviour is unchanged and pre-existing: `chain2b.pl` prints `1` then SIGSEGV rc=139, `nested.pl` `2-1` then rc=139, `deep.pl` two solutions then the `pl_trail_unwind` tripwire rc=134 — the PZ-4 (b)–(d) shapes, in both arms.

## ⭐ The one red conjunct was the box's, not the rung's — and it had a commit

`make test` was red at origin HEAD before this rung touched anything: the optbypass watermark gate read `SCRIP_OPT=0 192/1656` against a pin of 191 on the UNEDITED `922cfaf4` (control arm, this session) and on the edited tree, identically. The gate named no entry. Diffing today's per-entry census CSV against this seat's 2026-08-30 CSV named it: **`eval_convert_branch_1`**, PASS then, `CRASH rc=-11` under `SCRIP_OPT=0` now, DEFAULT arm PASS, `SCRIP_ZD=0` PASS — deterministic on 3 of 3 solo runs, so not the bimodal class the gate's header warns about. `git bisect run` over `e182a71a..46db4457` (the pin commit to the last pre-sweep commit, 63 commits, both endpoints verified by build + `--only` before bisecting) names **`5839cf13`** — *CONVERT(x,'EXPRESSION') compiles through EVAL's own path* — as the first bad commit. The entry IS the CONVERT-to-EXPRESSION-then-EVAL witness: a new code path now reaches the bypass arm and crashes there while the shipped path is green. Same class as hq_P's 190→191 note (a P8 witness: the emergency bypass is not a correct path). Re-pinned 191→192 with this attribution in the gate's header, and the gate now prints the sorted regressing list and its wall clock on a violation, so the next +1 is attributable from two logs without a prior CSV or a bisect worktree. The cure of `5839cf13`'s bypass-arm crash is routed to ceo (SNOBOL4 lane; ceo asked for the bisect, not the cure).

## ⭐ Anchors on code survive a comment sweep; anchors on comments do not — and a fail-closed script is what makes "re-apply after the sweep" a non-event

The edit was prepared on 2026-09-02 morning as an anchored, fail-closed script (every anchor must match its expected count or nothing is written) and proven on a scratch worktree at `46db4457`; ceo's R5 sweep then rewrote 98 files and deleted 6,387 lines under `src/`. Re-applied on `922cfaf4` it printed the same 46 anchor hits and `WROTE 11 files` — because every anchor was a CODE line (`^static int g_halt_rc = 0;`, the four-instruction quartet by its `x86(...)` calls, the function signatures), never a comment or a line number. The `include_prev_separator` check (the deleted function's leading `/*----*/`) survived because the sweep normalised separators to exactly 200 and the check tests the prefix. An edit script keyed on `file:line` or on a comment's text would have refused on every anchor after the sweep, or worse, matched the wrong line silently.

## What this rung did NOT do (scope, named so nobody re-derives it)

- `g_zeta_mode` the DEFINITION stays (`zeta_alloc.c`). It is now reader-less in `src/` and in emitted code, so CLAUDE.md's "must NOT be deleted — emitted code takes its address" banner has lost its stated reason. Routed to ceo; deleting it is a separate one-line rung, not a side effect.
- Census § A (the 41 live runtime globals) is untouched — those are PZ-4/PZ-5/C36/C37/P6/P7 rungs under `ARCH-PROLOG-THREE-ZETAS.md` § 4 and the translation page § C.

**Receipts:** SCRIP `d42d2918` (rung) + the watermark commit on top · corpus `a0cca818` · census FINDING struck (§ C whole, § B's table row, § A's compare) · baton `prolog-dead-globals-and-bb-table-out-of-runtime-image` NEXT/LEDGER · telegram `dead-globals-landed-and-the-watermark-bisect` to ceo.
