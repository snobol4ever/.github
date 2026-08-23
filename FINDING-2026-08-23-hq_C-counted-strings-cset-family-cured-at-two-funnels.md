# FINDING: the cset-argument family was wrong for CHAR(0) — cured at both funnels; two defects on one line

**Seat:** hq_C · **Date:** 2026-08-23 (s264, FLEET mode) · **Cure:** SCRIP `1f281ace` · **Measured at:** pristine, oracle `/home/resources/x64/bin/sbl -bf`

## Provenance

Lon ruled the class this session, relayed by hq_P, verbatim: *"Using any C function to manipulate strings is INVALID since the NUL character problem. You should tell HQ-Correctness to fix all of them."* hq_P took the TABLE arms (`a0859f7e`, aggregates.c + rtx_table.S). This is hq_C's half.

## What was wrong

`rt_coerce_str_d` (`src/runtime/rt/rt.c`) is the coercion **every pattern primitive funnels its argument through**, and it carried **two defects on one line**:

1. The admission test was `v.s[0]`. A string whose FIRST byte is NUL — `CHAR(0)` itself — read as **empty** and fell into the arm that raises *"argument is not a string or expression"*. That is Error **69** (BREAK), **59** (ANY), **151** (NOTANY), on a legal program the oracle answers in milliseconds.
2. It then **overwrote the incoming `slen` with `strlen()`**, so `'a' CHAR(0) 'b'` arrived correctly stamped at 3 and left at 1.

⭐ **Defect 2 is why `SPAN(CHAR(0))` returned a silent no-match instead of erroring.** Different symptom, same line — which is exactly what makes this **one class and not four bugs**. A per-op patch list would have fixed three loud errors and left the silent one.

`cset_resolve` (`src/runtime/pattern_match.c`) is the second funnel and had the same `strlen` truncation in its non-cset arm. Fixed there too, guarded three ways — see the commit and the in-file comment.

## Measured

| witness | before | after | oracle |
|---|---|---|---|
| `BREAK(z)` over `'a' z 'b'` | **Error 69** | `1` | `1` |
| `ANY(z)` | **Error 59** | `yes` | `yes` |
| `NOTANY(z)` | **Error 151** | `1` | `1` |
| `SPAN(z)` over `z z 'b'` | **silent `nomatch`** | `2` | `2` |

Corpus, pristine: **m3 PASS=358 FAIL=2 · m4 PASS=357 FAIL=2 SKIP=1 (360 total)**. Fail set **unchanged by name** (`160_pat_alt_inner_gen_resume`, `demo_treebank`). Both live emit gates rc=0.

⛔ **The denominator is 360, not 359** — `a0859f7e` added `crosscheck/strings/tbl_counted_string_keys`. Any board still quoting 359 is one commit stale.

## ⭐ THE TRANSFERABLE HALF: the grep was wrong and the ladder was right

The inbound brief said to sweep the idiom `slen ? slen : strlen(s)` and gave a per-file census of raw C string calls (by_name_dispatch.c 830, core.c 106, …). **That idiom does not exist by that spelling anywhere in the tree — `grep -c` returns 0.** The real sites are spelled `X.slen ? (int)X.slen : (int)strlen(...)`, and neither of the two that actually mattered was on the census's top-of-list files.

Both were found instead by: a 14-rung witness ladder (`corpus/probe/nul/`, refs oracle-minted) that put a CHAR(0)-bearing string through one consumer family per rung, then **one gdb backtrace off `core_runtime_error`** to name the raiser. Total: two files, 14 lines.

**Generalise: a class defined by a code idiom is searched with a grep; a class defined by a VALUE is searched with a ladder.** This class is defined by a value — CHAR(0) — so the census was measuring the wrong thing, and a 1,286-call sweep would have read almost every one of those calls without finding either site.

## Still open

- `n11_array_key` — `CONVERT(table,'ARRAY')` with a NUL-bearing key: oracle `3`, SCRIP **Error 235**. Left red in the ladder deliberately; separate row, separate mechanism.
- The 1,286 raw C string calls remain unaudited **as a population**. Most are builtin NAMES (C literals, genuinely safe) but that is still an assumption, not a measurement.

## Receipts

```bash
cd corpus/probe/nul && for f in n*.sno; do b=${f%.sno}; diff <(../../../SCRIP/scrip $f </dev/null 2>&1) $b.ref >/dev/null && echo "OK $b" || echo "RED $b"; done
```
Ladder: corpus `5819942b6`. Cure: SCRIP `1f281ace`.
