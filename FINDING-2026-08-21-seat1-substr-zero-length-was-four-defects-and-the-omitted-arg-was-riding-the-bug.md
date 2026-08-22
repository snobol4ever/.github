# FINDING — seat1, substr-zero-length: the brief predicted two defects, the oracle probe found four, and the omitted-`N` form was only working *because* of one of them

**Date:** 2026-08-21 · **Seat:** seat1 (`/home/claude1`, Claude Opus 5) · **Topic:** `substr-zero-length`

## 1. The contract, measured before any code was changed

The brief required the probe table first, and warned: *"do not special-case 0 without checking what -1 and out-of-range must do."* That warning paid for itself — a 0-only fix would have been wrong three ways.

`SUBSTR(S,I,N)` probed at `S = "hello world"` (`M = 11`). **SPITBOL `x64/bin/sbl`, CSNOBOL4 `csnobol4-clean`, and the live csnobol4 all produced byte-identical output** — a genuine three-way oracle agreement, not a `.ref` diff:

| I | N | oracle | I | N | oracle |
|---|---|---|---|---|---|
| 1 | −1 | FAILS | 5 | 7 | `"o world"` |
| 1 | 0 | `"hello world"` | 5 | 8 | FAILS |
| 1 | 1 | `"h"` | 11 | 1 | `"d"` |
| 1 | 99 | FAILS | 11 | 2 | FAILS |
| 1 | omitted | `"hello world"` | 12 | 0 | `""` |
| 5 | −1 | FAILS | 12 | 1 | FAILS |
| 5 | 0 | `"o world"` | 12 | omitted | `""` |
| 5 | 1 | `"o"` | 13 | 0 / 1 / omitted | FAILS |
| 5 | 99 | FAILS | 0 / −1 | any | FAILS |

It reduces to one rule:

> **`SUBSTR` succeeds iff `1 ≤ I ≤ M+1` and `0 ≤ N ≤ M−I+1`. `N = 0` and `N` omitted are the SAME contract — both mean *to the end of the string*. Everything else fails.**

`N = 0` and omitted being one contract is a measured fact, not an assumption — the brief flagged it as an open question ("zero-vs-omitted may be two different contracts"), and the probe closed it.

## 2. Four defects, not two

| # | Case | Oracle | SCRIP was | In the rung program |
|---|---|---|---|---|
| 1 | `N = 0` | to end of string | `""` | `1,0: ""` — the reported defect |
| 2 | `N < 0` | FAILS | `""` | the extra `1,-1` / `2,-1` rows |
| 3 | `N > M−I+1` | FAILS | **silently clamped** | extra `2,11`, `3,10`, `3,11`, … rows |
| 4 | `I > M+1` | FAILS | `""` | not reachable from this program |

Defects 3 and 4 were not in the brief. Defect 3 is the one that mattered most, because of §3.

## 3. ⛔ Why a naive fix would have broken the working case: the omitted form was riding defect 3

`SUBSTR_fn` never had a way to say "to the end". The two-argument form was implemented by **passing a magic huge length and relying on the clamp to cut it back**:

- `src/runtime/core/core.c:984` — `DESCR_t big = { .v = DT_I, .slen = 0, .i = 999999999 };`
- `src/runtime/by_name_dispatch.c:5098` — `(nargs == 3) ? args[2] : INTVAL(1000000000)`

So `SUBSTR(S,I)` was correct **only because** overlong lengths silently clamped. Fixing defect 3 in isolation — making overlong `N` fail, as the oracle demands — would have made every two-argument `SUBSTR` in the corpus start failing. The two facts are coupled, and the coupling is invisible unless you probe the omitted form, which is exactly what the brief's first step required.

## 4. The fix

The oracle says `N = 0` and omitted are one contract, so the code now says so too. `src/runtime/string_builtins.c`:

```c
if (start < 1 || (size_t)start > ncpts + 1) return FAILDESCR;
int64_t avail = (int64_t)ncpts - start + 1;
if (len_ < 0 || len_ > avail) return FAILDESCR;
if (len_ == 0) len_ = avail;
```

and both synthesised defaults become the zero that now genuinely means to-end — `big`/`1000000000` are deleted rather than re-tuned. Four lines replace four, and two magic numbers leave the tree.

**One caller had to be insulated.** `by_name_dispatch.c:551` implements the *Raku method form* `s.substr(from, len)` — a different language surface with 0-based `from`, its own default, and its own "negative means empty" clamping. It shares `SUBSTR_fn` but not its contract. It now clamps into range and returns empty for a zero span itself, so the SNOBOL4 contract change cannot leak into it. `corpus/programs/raku/parser/str_substr.raku` still prints `world`, byte-identical to baseline.

## 5. Verification

- **The rung program matches `corpus/programs/csnobol4-suite/substr.ref` in BOTH modes** (m3 `--run` and m4 `--compile`), from a 111-line diff to empty.
- **All 27 probe cases match SPITBOL exactly** in both probe programs.
- **Corpus fail-set no worse — it improved.** `test_corpus_snobol4.sh`, `make pristine` first per HQ-27 (`PRISTINE_RC=0`, `RT_OPT` left at the `-O0` default per O0-DEV-O2-BENCH):

  | | m3 `--run` | m4 `--compile` | total |
  |---|---|---|---|
  | before | `PASS=338 FAIL=2` | `PASS=337 FAIL=2 SKIP=1` | 340 |
  | after | `PASS=339 FAIL=2` | `PASS=338 FAIL=2 SKIP=1` | 341 |

  The fail-set is the *same two names* (`160_pat_alt_inner_gen_resume`, `demo_treebank`); the +1 total is the new crosscheck test of §7, which passes in both modes.
- **Gates.** `test_gate_emit_no_lang` rc=0, `test_gate_rtx_inventory_live` rc=0. `test_gate_no_lang_names` and `test_gate_lower_isolation` return rc=1 — **pre-existing, not mine, and proven so**: both return rc=1 with my change stashed, and they flag `src/emitter/emit.cpp` and `src/lower/lower_pascal.c → parser/pascal/pascal_driver.h`, files this rung never touched.
- **No codegen touched.** Re-emitting `crosscheck/strings/066_builtin_substr.s` is byte-identical to the committed artifact, so no `.s` regeneration is owed — the change lives entirely behind the `call` in already-emitted code, which is also why one fix covers both modes.
- **Differential over every corpus program that calls `SUBSTR(`** (61 of them), pre-change binary vs post-change binary: **4 changed**, and all four are accounted for — `substr.sno` (the fix), `SUBSTR_driver.sno` (§6), and `json.sno` / `porter.sno` whose only deltas are benchmark timing fields (`match_ms`, `ns`, `ms`). The other 57 are byte-identical.

## 6. The fix repaired a second program that was quietly wrong

`corpus/programs/gimpel/SUBSTR_driver.sno` exists to test exactly this — its last case is commented *"a request past the end"*. Its `.ref` and SPITBOL both say `past the end: fails`. SCRIP printed `[BC]`: defect 3 clamped `SUBSTR('ABC',2,5)` to `"BC"` instead of failing, so the `:S(DONE)` branch was taken and the failure message never printed. It now matches. **The corpus already contained a witness for defect 3 and it was sitting red.**

## 7. Checked in

`corpus/crosscheck/strings/076_builtin_substr_bounds.sno` + `.ref` — the boundary grid as a permanent crosscheck test. **The `.ref` was generated from the live SPITBOL oracle**, then independently confirmed byte-identical against both CSNOBOL4 binaries, so it is an oracle ref and not a snapshot of SCRIP's own output.
