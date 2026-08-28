# The profile could not say which BOX KIND, and mode-3 could not say anything — both cured, and `match_begin` β is 18% of cycles

**Seat:** hq_P · **Date:** 2026-08-28 (s280) · **Mode:** FLEET-8 (`MODE` file computed) · **Row:** `perf-symbol-attribution-tooling` (rank 1, **Lon direct**)
**Lon, in-chat to CEO, verbatim in substance:** *"Make sure HQ-PERFORM is using one of the nice tools we have. By making the symbols accessible by the perf tools you can do per-statement, and per-BB or per-BB-type statistics for which statement or BB is hogging the time."*
**SHARED AXES:** `perf` cycles:u @999Hz · `PERF_BIN=/usr/lib/linux-tools-6.8.0-138/perf` · m4 unless stated · `RT_OPT=-O0` · `porter` on `porter.input` · SCRIP `476a8ae3`.

## The starting state, measured not assumed

| level | before | after |
|---|---|---|
| per-BB (m4) | worked — 3,036 `n<id>_<family>_<port>` symbols reach the binary's symtab | unchanged |
| **per-BB-TYPE** | ⛔ **absent** — a profile named individual boxes, so the top row was one of 3,036 | ✅ `util_perf_bb_rollup.sh` |
| per-STATEMENT | ⛔ absent — **zero** `.loc`/`.file` in emitted `.s` | ⛔ still absent (slice 2, not taken) |
| **per-box (m3)** | ⛔ **anonymous `[JIT]`** — mode-3 seals into an anon mmap slab; perf could name nothing | ✅ `SCRIP_PERF_MAP=1` |

## Slice 1 — `scripts/util_perf_bb_rollup.sh`

Rolls a perf report's per-symbol rows into a **BB FAMILY × PORT** table. Measured vocabulary across `porter`/`treebank`/`pattern_bt`: **41 families**, ports **α β af as s0…s20**.

⭐ **THE PORT NAMES ARE LITERAL UTF-8 GREEK IN THE EMITTED LABEL** (`emit_label_alloc("n%d_%s_α", …)`, `emit.cpp:2935`) — an ASCII-only census sees `af/as/sN` and **silently misses 4,880 of 4,957 labels**, because α and β are 98% of them. My first census did exactly that and reported a port vocabulary with no α in it at all. ⛔ **A regex over emitted labels that assumes ASCII is not a narrower measurement, it is a wrong one** — the two most common ports simply do not appear, and the table still looks plausible.

**Instrument discipline, all negative-tested:**
- ⛔ **Identity-anchored, not substring.** Matched whole against `^n<id>_<family>_<port>$`; family is what remains after **both** ends are stripped. Substring matching folds `match_assign_save` into `match_assign` — the selftest asserts they stay separate at 25.00% and 8.00%.
- ⛔ **REFUSES `rc=2`** on: no input · missing file · unparseable text · **zero BB symbols matched**. ⭐ That last one is the trap this tool exists inside: **an empty BB table looks exactly like a program that spends no time in boxes.** It is a refusal, with the three real causes named (stripped binary / m3 `[JIT]` profile / label scheme changed).
- ⭐ **COVERAGE is always printed**, so the BB total is never read as the whole profile.
- ⭐ **The selftest carries a POISON arm** that mutates the canned report and asserts the check then FAILS — so the assertions are provably not tautological. 1 positive + 4 negative arms.
- ⛔ This box has **`mawk` only**; `asorti` is gawk-only. Hand-rolled the sort rather than depend on an absent interpreter — **a tool that needs a missing tool is the instrument-cannot-measure class wearing a different hat.** Caught because the selftest failed, not because I checked.

## ⭐ THE FIRST RESULT IT PRODUCED — AND IT NAMES A LEVER

`porter`, m4, cycles (`--min 0.4`):

| BB FAMILY × PORT | α | β | af | TOTAL |
|---|---:|---:|---:|---:|
| **`match_begin`** | 5.38% | **18.18%** | 1.28% | **24.84%** |
| `match_defer` | 6.39% | . | . | 6.39% |
| `match_alternate` | 4.09% | . | . | 4.09% |
| `call` | 1.32% | . | . | 1.32% |
| `differ` | 1.28% | . | . | 1.28% |
| `match_assign_imm` | 1.27% | . | . | 1.27% |
| **TOTAL (per port)** | **19.73%** | **18.18%** | **1.28%** | **39.19%** |

*COVERAGE: 18 BB symbols = 39.19% of profile · 26 non-BB = 60.82% · 44 rows parsed, 100.01% accounted.*

⭐ **`match_begin` is a quarter of all cycles, and 18.18 of its 24.84 points sit on ONE port — β, recede.** That is the backtrack path, and no per-symbol profile said so: the same cost was spread across `n2819_match_begin_β`, `n2794_…`, `n2869_…` as three unrelated 8%/4%/3% rows. ⛔ **The rollup is not a prettier view of the same information — it is the difference between three mid-table rows and the top lever.**

## Slice 3 — `SCRIP_PERF_MAP=1`

Writes `/tmp/perf-<pid>.map` (perf jit convention, `addr size symbol`) at slab-seal time. **Measured: `m3_pat_flat` resolves at 11.20%** on `porter` where it was previously an anonymous `[JIT]` address.

- ✅ **PRINT-ONLY, PROVEN:** emitted `.s` **byte-identical** arm-on vs arm-off (1219 lines), and m3 stdout identical. ⭐ With a **negative control**: a 1-line poison makes `cmp` fire, so the identity is not vacuous.
- ⛔ **NO NEW GLOBALS** — no cached static, no held `FILE*`. `getenv` + `fopen(append)` per seal, once per graph, never on a hot path. (No banner grant exists this session, so the arm was written to need none.)
- ⚠️ **GRANULARITY IS PER-GRAPH, NOT PER-BOX, AND I AM NAMING THAT RATHER THAN CLAIMING IT.** The seal site (`emit.cpp:3552`) knows the chain prefix, not each box's offset; per-box m3 naming needs the emitter to record box offsets. Follow-up, not delivered.
- ⚠️ **The map is APPENDED, and perf reads `/tmp/perf-<pid>.map` regardless of `TMPDIR`.** A stale map from a recycled pid mis-names samples **silently** — worse than `[JIT]`, because it is plausible. The driver prints the path so the caller can delete it first.
- ⚠️ **An m3 profile mixes COMPILE and RUN** — `xop_frame_member` 11.96%, `frame_need_of` 9.02%, `zd_chase` 5.92% are compiler symbols, because mode-3 compiles in-process. ⛔ **m3 and m4 profiles are not comparable as run-time measurements**, and this instrument makes that visible for the first time rather than introducing it.

## ⛔ THE ROW'S OWN DONE-WHEN HAS A STRUCTURALLY DEAD BRANCH — REPORTED, NOT WORKED AROUND

The baton's `DONE-WHEN` tests slice 2 by compiling `corpus/../corpus/benchmarks/snobol4/pattern_bt.sno` **from `$S4E_HOME/SCRIP`**. ⛔ **`SCRIP/corpus` does not exist** — the corpus is a *sibling* of `SCRIP`, not a child — so the path cannot resolve, the `.s` is never written, and `grep -qE "^\s*\.loc"` runs against a missing file.

⭐ **CONSEQUENCE: slice 2 could land perfectly and this DONE-WHEN would never detect it.** The row can only ever close through the `SCRIP_PERF_MAP` branch — which is how it closed today, legitimately, but by the *other* arm. ⛔ **A DONE-WHEN with a dead branch is the vacuous-test class in the acceptance criterion itself**, and it fails toward "closed", which is the expensive direction. The correct path is `../corpus/benchmarks/snobol4/pattern_bt.sno`. Raised with `ceo` (baton owner); **not silently patched**, because an acceptance criterion is not the graded party's to rewrite.

## Gate verdict

**Pristine**, then re-proven after rebase onto `43fa94a0`:
- SNOBOL4 blocking set: **m3 PASS=893 FAIL=0 · m4 PASS=893 FAIL=0 SKIP=0 · MISSING=0**, rc=0.
- Icon smoke **14/14 both modes** (shared-node control arm — `emit.cpp` is language-blind and shared).
- `test_gate_emit_no_lang.sh` OK · `test_gate_template_medium_invisible.sh` OK (0 sites).
- Rollup selftest PASS.

⚠️ **`make test` returns rc=2 on a PRE-EXISTING red I did not cause and am not curing under this row:** `test_gate_corpus_coverage_classified.sh` fails on unclassified corpus subtrees and on `benchmarks/pascal` being covered only by row `pas-display-revival`, state **DONE**. ⭐ **Control-armed rather than asserted:** with my three edits stashed the gate returns the **identical `rc=1` and identical message**, and the gate never invokes the compiler. Reported to `ceo`.

## What this does not claim

- ⛔ **No speed claim, and no cure.** These are instruments. The `match_begin` β number is **one unqualified sample on a shared box** — seat05's noise protocol is still the announcement blocker, and this table is a LEVER RANKING, not a measurement anyone should quote as a share.
- ⛔ Slice 2 (`.loc` per statement) is **not delivered**, so **per-STATEMENT attribution — the first thing Lon's sentence names — still does not exist.** Slices 1 and 3 close the per-BB-type and m3 halves only.
- ⛔ The 39.19% BB coverage on `porter` is not a claim that 60.81% is unattributable — it is runtime and libc, already named by symbol.
