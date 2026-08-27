# FINDING 2026-08-27 seat07 — `perf-replace-translate-loop-scalar-byte-copy`: lever 1 (hand-asm RTX port) landed, `string_manip.sno` kernel Ir drops 1.21x (17.45%)

**Row:** `perf-replace-translate-loop-scalar-byte-copy` (rank 1, dispatch-locked via `s4e_msg.sh next`, `MODE: FLEET-12` per the lock printout). Row text: two candidate cure levers, neither tried yet; lever 1 (hand-written asm translate routine, precedent `rtx_table.S`) tried and landed this session. Lever 2 (SIMD-widen) and the `rt_ws_alloc_c` pooling question are untouched — see "Left open" below.

## Question routed before writing any asm
The row's own `## NEXT` flagged: does a hand-authored RTX asm port conflict with the s262 NO-`-O2` FACT RULE? My reading — no, confirmed textually by RULES.md's own s262 text ("the RT is being rewritten in register-aware ASM ... C retained only for a few large algorithms") and by `rtx_table.S`'s own header comment (near-identical wording) — hand-asm RTX ports are the stated *reason* the rule exists, not something it forbids. Sent to `hq_P` directly (`s4e_msg.sh send hq_P q-rtx-asm-not-blocked-by-no-o2 ...`), **not** `s4e_msg.sh ask` — this seat's `$PO/seat07/HQ` resolves to `hq_C`, but this is a perf/Ir-budget row in hq_P's lane (per this task file's own LEDGER, where hq_C released it same-day for exactly that reason), so plain `ask` would have misrouted the question the same way. Proceeded under my stated reading per THE LOOP's ask-and-carry-on protocol.

**⭐ RULED by hq_P, same day, in the task file directly: seat07's reading is correct.** "The s262 rule governs `RT_OPT` ... not a rule about what LANGUAGE the runtime is written in ... hand-authored RTX asm is the rule's PURPOSE, not its target." Three guards attached, none blocking the ruling itself but binding on this row's evidence: (1) label `RT_OPT=-O0` on both arms, don't subtract against pre-s262 figures — already the case throughout this FINDING; (2) Ir at fixed work via `bench_wrap.sh --mode=iter` + `callgrind_annotate`, not wall-clock — already the recipe used; (3) **the kill-switch must be proven able to FAIL — negative-test it once.** Guard 3 was not yet discharged when this FINDING was first drafted; see "Guard 3" below for how it was, and what it found.

**Shared-node check (hq_P's ⚠️ watch):** `by_name_dispatch.c` is a shared runtime TU, so RULES.md § SHARED-NODE VERDICT SCOPE could bind if another frontend reaches `bn_replace`. Checked: `try_call_builtin_by_name`/`script_try_call_builtin_by_name` (the entry point into the BID_REPLACE dispatch) is referenced from exactly one lowerer tree-wide — `src/lower/lower_snobol4.c` — confirmed by grep across `src/lower/` and `src/frontend/`; Icon/Prolog/Raku/Pascal/Rebus lowerers never reference it. Snocone (`src/frontend/snocone/snocone_driver.c`) includes `frontend/snobol4/scrip_cc.h`, i.e. it compiles through the shared SNOBOL4 pipeline rather than its own — plausibly reachable, so `test_smoke_snocone.sh` was run on the changed tree: **PASS=5 FAIL=0**, unchanged. No Icon/Prolog/Raku/Pascal/Rebus board re-run needed — they cannot reach this code, not merely "weren't checked." (Distinct in kind from a shared-*codegen* change too: nothing about emission changed here, see "no `.s` regen owed" below — the correctness proof this row relies on is an exact input/output equivalence of the runtime routine itself, not a sampled board, so it does not depend on which frontend originates the call.)

## Pinned measurement conditions
SCRIP `44ddea38` (pre-edit) · corpus `d5961675` · **RT_OPT=`-O0`** (`make pristine`) · mode-4 (`--compile` + `gcc -no-pie ... -lscrip_rt`) · instrument `valgrind --tool=callgrind` (Ir) · fixed-work via `bash scripts/bench_wrap.sh ../corpus/benchmarks/snobol4/string_manip.sno -o <out>.sno --mode=iter --n=20000`. Both repos clean before editing (`git status --short` empty on both).

## ⛔ Re-baseline required — the row's cited 51,185,959 Ir does not reproduce on today's tree
The row's own citation (SCRIP `8c564966`, 2026-08-24) does not reproduce: measured **fresh, pre-edit**, on today's `44ddea38`, the identical recipe gives **45,618,318 Ir** — a 10.9% drop *unrelated to this row*. Confirmed it is real drift, not measurement noise: `bn_replace`'s own self-cost (**18,986,411 Ir**) and the translate loop's own absolute line cost (**14,553,000 Ir**) are BOTH byte-for-byte identical to the original FINDING's citation — only the *surrounding* kernel got cheaper somewhere else since s272, shifting every percentage without moving this row's numbers. Per RULES.md ("a number carried into a new column must be re-measured, not copied" / the rebase-baseline corollary), I measured a fresh BEFORE on the pre-edit tree and a fresh AFTER on that same tree plus this one change, rather than diffing against the stale citation.

## The cure
Extracted `bn_replace`'s translate loop (`src/runtime/by_name_dispatch.c`, `for (size_t i = 0; i < n; i++) buf[i] = map[(unsigned char)sv[i]];`) into its own symbol and ported it to `src/runtime/rtx/rtx_str.S` under the **existing STR family gate** (`SCRIP_RTX_STR`, shared with `str_concat_d`/`VARVAL_fn`) — same class of cure as `rtx_table.S`'s hot-path ports, the precedent the row's own brief names. No new global, no new killswitch env var, no Makefile change (`rtx_str.S` already builds into both `scrip` and `libscrip_rt.so`).

- `void c_rt_translate_bytes(char *dst, const char *src, size_t n, const char *map)` — the C of record, `by_name_dispatch.c`, byte-identical semantics to the loop it replaces.
- `void rt_translate_bytes(...)` — the asm twin, `rtx_str.S`: `RTX_GATE(str, c_rt_translate_bytes)` then a register-only pointer-walk loop (`rdi`=dst, `rsi`=src, `rdx`=n, `rcx`=map, `r8` scratch — all free RTX working-set registers, no blob pins touched, no call, no stack use). Tail-jumps to the C body when the gate is off.
- `bn_replace` now calls `rt_translate_bytes(buf, sv, n, map)` in place of the inline loop.
- Declarations added to `core.h` beside `VARVAL_fn`, matching the established `<name>`/`c_<name>` declaration-pair convention (`table_find_pair_d`/`c_table_find_pair_d` is the model followed).
- Neither `emit.cpp`/`emit.h`/`src/templates/*.cpp`/`x86_asm.h`/`lower_snobol4.c` touched, and the change doesn't alter `bn_replace`'s signature or calling convention — **no `.s` artifact regen owed** (ARCH-SNOBOL4-RTX.md §3: "Templates untouched ⇒ no `.s` regen, no both-medium work, in this phase").

## Results — same tree, one change

| | PROGRAM TOTALS (Ir) | translate-loop cost | `bn_replace` inclusive |
|---|---|---|---|
| **Before** | 45,618,318 | 14,553,000 (31.90%), inline loop | 21,471,869 (47.07%) |
| **After** | 37,660,021 | 6,447,000 (17.12%), `rt_translate_bytes` incl. | 13,513,538 (35.88%) |
| **Δ** | **−7,958,297 Ir = 1.21x / 17.45% faster** | −8,106,000 Ir | −7,958,331 Ir |

⛔ **CORRECTION: the sentence is 43 characters, not 44** ("The quick brown fox jumps over the lazy dog" — counted directly, and confirmed by this session's own standalone run printing `masked length = 43`). Both the original 2026-08-24 FINDING and this FINDING's first draft inherited "44"; it was never re-counted until the negative-test below needed a real content oracle. Per-byte cost, corrected: 14,553,000 / (43 chars × 20,999 calls) = 16.11 Ir/byte before → 6,447,000 / (43 × 21,000) ≈ 7.14 Ir/byte after (**≈2.26x** — the ratio is unaffected by the char-count error, only the absolute Ir/byte figures were off) — consistent with the row's own diagnosis (`-O0` stack spills on `i`/`n`/`buf`/`sv`/`map`, reloaded every iteration, now register-resident).

`bn_replace`'s own self-cost (excluding what it calls) dropped from 18,986,411 to 4,580,415 Ir — the extracted 14,553,000 minus the new call-site overhead, as expected.

## Correctness — verified, not assumed
- `test_corpus_snobol4.sh`: **365/365 both modes, FAIL=0**, before and after — byte-identical to baseline.
- `test_gate_instr_budget.sh`: all four pinned workloads green before and after. `roman` (also a REPLACE caller, short strings) additionally dropped 10,137,022→10,127,660 Ir, still within its pinned budget — a small free win, not chased. `beauty` dropped 1,860,478,327→1,856,591,796, gate printed `NOTE ... improved; consider re-pinning down` — flagged for whoever owns that watermark, not re-pinned here (out of this row's scope).
- **Content-level identity, standalone run** (`./scrip string_manip.sno`, prints the real masked text, not just its length): gate ON and `SCRIP_RTX_STR=0` both print `masked text   = Th* q**ck br*wn f*x j*mps *v*r th* l*zy d*g` — byte-for-byte identical, and it is the semantically-correct answer (every vowel in "The quick brown fox jumps over the lazy dog" replaced by `*`, everything else untouched).

### ⛔⭐ Guard 3 (hq_P): the kill-switch must be proven able to FAIL — and the first oracle I used could not
`bench_wrap.sh`'s own `check:` value for this benchmark is `SIZE(S)` after `REPLACE` — see `corpus/benchmarks/snobol4/string_manip.sno:11,13`. **`REPLACE` never changes string length**, so `SIZE(S)` is structurally blind to any bug that corrupts *content* while preserving length — which is exactly the class of bug a broken translate loop would produce. My first draft of this FINDING cited "`check: 43` unchanged" as correctness evidence; that claim was true but nearly worthless, and I did not know it until running the negative test hq_P's guard demanded.

**The test:** temporarily sabotaged `rt_translate_bytes` (`mov [rdi], r8b` → `mov byte ptr [rdi], 0x58`, i.e. every output byte forced to `'X'`), rebuilt (plain `make`, not `make pristine` — this is a methodology check, not a gate verdict), and ran both the wrapped benchmark and the standalone program:
- Wrapped (`sm_after.bin`), gate ON, sabotaged: `check: 43` — **unchanged**. The weak oracle, exactly as suspected, saw nothing.
- Standalone (`./scrip string_manip.sno`), gate ON, sabotaged: `masked text   = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX` — **wrong, and visibly so**, against the correct `Th* q**ck br*wn f*x j*mps *v*r th* l*zy d*g`.

This proves two things at once: the content-level oracle (standalone run, real string output) **can** fail, discharging hq_P's guard; and the length-only `check:` value **cannot**, which is itself worth recording so the next session doesn't repeat the same false confidence — including, in fairness, my own first draft of this document.

Reverted the sabotage (`git diff --stat` on `rtx_str.S` empty against the committed version, confirming an exact restore), rebuilt (`make pristine`, since a real gate verdict does need one), and re-ran everything: `test_corpus_snobol4.sh` 365/365 FAIL=0, `test_gate_instr_budget.sh` green (final Ir: roman 10,110,593, beauty 1,850,685,627 both further within budget — ordinary run-to-run `-O0` variance, not re-chased), and the standalone content check identical again between gate ON and `SCRIP_RTX_STR=0`.

**Kill-switch Ir identity** (`SCRIP_RTX_STR=0` vs default, wrapped `sm_after.bin`, correct build): Ir with the gate forced off reverts to **46,819,837**, up near (and rationally above, since the whole STR family's other fast paths also disable) the pre-edit baseline of 45,618,318 — proving the asm path is genuinely what ran under the default (gate-ON) measurement and genuinely responsible for the drop, not a measurement artifact.

## Judgment (per this row's own stated close criterion)
The row's `DONE-WHEN` (corpus + instr-budget gates) is necessary and passes; the row's own text says that alone is not sufficient — the real bar is a measurable Ir drop on `string_manip.sno`'s fixed-work kernel, freshly measured, same-tree-plus-one-change. That bar is met: **45,618,318 → 37,660,021 Ir, 1.21x/17.45%**. The FACT-RULE question is now RULED (hq_P, above), and correctness is proven at the content level, not just the length-blind `check:` value — the negative test shows the proof genuinely can fail and doesn't. Recorded here for `hq_P` (this row's lane owner) or any reviewer to confirm or dispute against the receipts above.

## Left open (not this session's scope)
- **Lever 2 (SIMD-widen)** — untried. The row's own brief gates it on checking whether any corpus program calls `REPLACE` on strings anywhere near 43+ characters outside this synthetic benchmark; not checked this pass.
- **`rt_ws_alloc_c` pooling** — the row's own "secondary, smaller, not separately rowed" item (whether a REPLACE call could reuse/pool its output buffer). Still open, still not investigated.
- `beauty`'s instr-budget watermark could be re-pinned tighter (see NOTE above) — not this row's job.

## Files/commands for reproduction
```
bash scripts/bench_wrap.sh ../corpus/benchmarks/snobol4/string_manip.sno -o out.sno --mode=iter --n=20000
./scrip --compile -o out.s out.sno </dev/null
gcc -no-pie out.s -Lout -lscrip_rt -Wl,-rpath,$(pwd)/out -o out.bin
valgrind --tool=callgrind --callgrind-out-file=out.callgrind ./out.bin </dev/null
callgrind_annotate --threshold=99.9 out.callgrind src/runtime/by_name_dispatch.c
# kill-switch, Ir: SCRIP_RTX_STR=0 valgrind --tool=callgrind ... ./out.bin </dev/null
# kill-switch, content (the real oracle): ./scrip ../corpus/benchmarks/snobol4/string_manip.sno </dev/null
#                                          SCRIP_RTX_STR=0 ./scrip ../corpus/benchmarks/snobol4/string_manip.sno </dev/null
```
SCRIP HEAD `137a6fe5` (pushed) carries the cure — this session's commit rebased twice (originally `de6b9113`, then `75fb899f`, finally `137a6fe5`) onto four other seats' pushes in the course of this session, gate re-proven pristine after each rebase per RULES.md. Corpus untouched (no commit owed there).
