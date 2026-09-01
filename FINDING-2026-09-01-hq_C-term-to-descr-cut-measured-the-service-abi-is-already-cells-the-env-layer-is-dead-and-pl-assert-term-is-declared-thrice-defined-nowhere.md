# FINDING (hq_C, 2026-09-01, FLEET-8 slicing of `prolog-term-to-descr-eradication`): the runtime's Term use sits entirely BEHIND a service ABI that already takes DESCR cells; the resolution-engine `Term **env` layer has ZERO callers; and `pl_assert_term` — named by the routing block as the parser→`tree_t` boundary — is declared three times and defined nowhere

**Context:** Lon 2026-09-01 (in-chat to ceo): *"Let's eradicate the usage of Term structure in Prolog and replace with DESCR … No need for Prolog to be special."* MODE → FLEET-8; hq_C slices. ceo's routing block (`GOAL-PROLOG-100.md`, 2026-09-01) proposed a natural cut **for hq_C to confirm or refute by measurement**. This is that measurement, at SCRIP `bcb0ec1e` (Term census 490 word-refs, reproducing ceo's `8eac17da` count exactly). Three of its premises needed correction; the cut survives with those corrections and is stronger for them.

## 1. CONFIRMED, and sharper than stated: the service ABI is already cells

`unification.c` exports **75 non-static functions**, and nearly every one is `rt_pl_*_cell(...)` — it **receives DESCR cells**. Inside, each manufactures a heap `Term` via `pl_cell_conv.h` (`pl_cell_to_term`, `rt_pl_cell_to_term_named`), works on it, converts back. Converter call sites: `unification.c` **106**, `pl_cell_conv.h` 13, `by_name_dispatch.c` 7, `rt_runtime.c` 3. Emitted code reaches all of it only through `by_name_dispatch` (1 reference in `src/templates`+`src/emitter`+`src/lower`; **zero** direct references to any `rt_pl_*`, `resolve_*`, or converter symbol).

**Consequence for the cut:** every service family can be rewritten on cells **one family at a time, with no ABI change and no codegen change**. "Runtime services first" is confirmed — and it is not merely first, it is *independent of everything else*.

## 2. REFUTED: nothing in this census needs a γ-surviving frame — the env layer is dead

The routing block gated "slices needing a γ-surviving frame for WHERE a logic variable lives" behind PZ-4. Measured:

```
resolve_env_new            callers outside resolution.[ch]: 0
rt_env_current             0
resolve_bb_env_save_push   0
resolve_bb_env_install     0
resolve_catch_push         0
resolve_throw_term         0
```

(grep -rw over `src/` including `.cpp`; templates/emitter/lower: 0 each.) The `Term **env` world in `resolution.h`/`resolution.c` is the **old resolution engine's scaffolding**. Live logic variables already live in `DT_PLVAR` cells on the zetas (97 `DT_PLREF`/`DT_PLVAR` sites; 2602 `DESCR_t`). **PZ-4 gates zero slices.** That layer is a *deletion* (slice s7), with the standing caveat that a symbol read only by emitted code is invisible to a grep of compiler sources — the slice must also check `nm out/libscrip_rt.so` before deleting each symbol.

## 3. CORRECTED: the parser→`tree_t` boundary is `prolog_lower.c:lower_term`, not `pl_assert_term`

`pl_assert_term` appears exactly three times under `src/`: `prolog_lower.h:9`, `lower_prolog.c:1229` (`extern`), `resolution.c:12` (`extern`). **No definition. No call.** It is a dead declaration copied into three files. The actual conversion is `static tree_t *lower_term(Term *t)` at `prolog_lower.c:70`, called by `lower_clause`/`prolog_lower` in the same file; `lower_prolog.c` (the shared lowerer) contains **one** `Term` mention — that dead extern. The parser slice (s6) therefore has a clean, single, static boundary to delete.

⭐ A declaration with no definition that still compiles is the linker's version of a stub that returns success: nothing references it, so nothing fails, so it survives three copies and gets cited as architecture.

## 4. Also measured while establishing floors

- **`test_gate_pl_gz2/3/4` are dead instruments**: each fails at `bcb0ec1e` with "m4 .s lacks gzq labels (GZ path not taken)" and `grep -rn gzq src/` = **0**. The path they grade is gone; no tree can turn them green. Row minted: `test-gate-pl-gz-dead-instruments-measure-a-retired-path` (rank 3). They are recorded pre-existing-red on the umbrella ledger and are **not** a floor for any slice.
- **The umbrella DONE-WHEN was false-green** (ceo's own finding, reproduced here: rc=0 with `term.h` present and 490 refs — it tested the retired `src/parser/` path and a regex matching only `Term_`/`Term_t`). Re-cut on `src/parsers/prolog/term.h` + `grep -rwE Term`, count PRINTED, proven fail (rc=1) / pass (rc=0, Term-free scratch tree) / refuse (rc=2).
- **`prolog_unify.c`** (parser directory) is live — `unify()` is called from `rt_runtime.c:434,455` (`univ_common`); and **`pl_write`/`pl_writeq`** (`prolog_builtin.c`) are called from `unification.c:97,100,518` by bare `extern` — the runtime reaching into the parser directory in both cases. Both are layering defects the slices remove (s4, s1).

## The slices (minted, one row one seat, every DONE-WHEN watched to FAIL at mint)

| row | scope (Term occurrences at `bcb0ec1e`) | rank |
|---|---|---|
| `prolog-term-descr-s1-write-format-printers` | write/format family in `unification.c` + `prolog_builtin.{c,h}` + `prolog_runtime.h` + `out_write_descr` | 1 |
| `prolog-term-descr-s2-compare-sort-pairs` | compare/sort/keysort/pairs family + `rt_runtime.c` compare helpers | 1 |
| `prolog-term-descr-s3-copy-findall-nb-aggregate` | copy_term/findall/nb_/aggregate + `bb_copy_term_rec` + `rt_findall_add` | 1 |
| `prolog-term-descr-s4-typetest-functor-univ-succ` | type tests/functor/arg/=../succ + `univ_common` + deletes `prolog_unify.c` | 1 |
| `prolog-term-descr-s5-dynamic-db-flags-streams` | assert/retract/clause/flags/streams family | 1 |
| `prolog-term-descr-s6-parser-builds-tree-t-directly` | the parser half: `prolog_parse.c`, `prolog_lower.c`, `prolog_atom.c`, the three dead declarations | 1 |
| `prolog-term-descr-s7-dead-resolution-env-layer-deleted` | `resolution.{h,c}` env layer, throw/match, `script_try_call_builtin_by_name` | 2 |
| `prolog-term-descr-s8-term-h-and-converters-deleted` | `term.h`, `pl_cell_conv.h`, converters, tests — carries the umbrella's own DONE-WHEN; last | 1 (parked on s1–s7) |

Each DONE-WHEN: scope-clear first (named functions, per-function awk extraction validated against the census before minting), then the floors (`test_smoke_prolog` 5/5 both modes · `test_gate_pl_coupling` PASS · `test_corpus_prolog_parser` RESULT: PASS · `make test` as the shared-.so control arm), then prints the umbrella count. Shared-file discipline (`unification.c` under five seats) and the three-zetas law are in every `## NEXT`.

## Reproduce

```bash
cd SCRIP
grep -rwE Term src --include='*.c' --include='*.h' --include='*.cpp' | wc -l        # 490 at bcb0ec1e
grep -rn pl_assert_term src                                                          # 3 declarations, 0 definitions, 0 calls
for s in resolve_env_new rt_env_current resolve_catch_push; do grep -rw $s src --include='*.c' --include='*.cpp' | grep -vc 'resolution\.[ch]'; done   # 0 0 0
grep -nE '^[A-Za-z_].*\(' src/runtime/unification.c | grep -vc '^[0-9]*:static'      # 75 exported, *_cell ABI
grep -rn gzq src | wc -l                                                              # 0 -- the gz gates grade a retired path
```
