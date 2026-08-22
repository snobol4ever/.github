# FINDING — s251 HQ: the JSON de-serializer hangs on ANY comma, in BOTH modes, and no corpus row covers it

**Date:** 2026-08-21 · **Seat:** HQ (`/home/claude`, Claude Opus 5) · **Topic:** BEAUTY-10X → JSON workhorse · **Status:** MEASURED, repro minted at 5 bytes, NOT fixed — queued as rank-0 `json-arbno-comma-hang`
**Context:** Lon moved the campaign from beauty to the workhorse demos, naming the de-serializer as the target because *"It has both sides, parser and object creation."* `json.sno` is the WORK member of the json family (`json-match.sno` / `json-match-fence.sno` are recognize-only). Benchmarking never started — the program does not run.

## 1. THE DEFECT

`corpus/programs/snobol4/demo/json.sno`, mode-4 binary, timings from a 10 s cap:

| input | bytes | result |
|---|---|---|
| `[]` | 2 | ✅ 11 ms |
| `{}` | 2 | ✅ 11 ms |
| `{"a":1}` | 7 | ✅ 12 ms |
| `[{"a":1}]` | 9 | ✅ 11 ms |
| **`[1,2]`** | **5** | ❌ **HANG** |
| **`{"a":1,"b":2}`** | 13 | ❌ **HANG** |
| **`[{"a":1},2]`** | 11 | ❌ **HANG** |

**Every input containing a comma hangs; every comma-free input passes.** The comma appears in exactly two places in the grammar — `ARBNO(',' jmember)` in `jobject` and `ARBNO(',' *jelement)` in `jarray` — so the suspect is the ARBNO retry, not the fences.

**Minimal witness: `[1,2]`, five bytes.**

## 2. WHAT IS RULED OUT

- ⛔ **Not caused by the s251 optimizer/emitter work.** The checked-in `json.s` artifact (mtime 21:34, predating `8ffcd5ea` and `1a812667`) was linked and run: it hangs identically. **Pre-existing.**
- **Not mode-4-specific.** m3 hangs on `[1,2]` too — consistent with the m3 ≡ m4 design invariant, so this is shared codegen/runtime, not an emit-path divergence.
- **Not the grammar.** SPITBOL `-bf` runs every one of these inputs at rc=0 on the same `json.sno`.
- **Not FENCE0.** `[1,2]` contains no object and no array-of-object, so neither `'}' … FENCE` nor `']' … FENCE` is reachable. Only the FENCE1s in `ws` and `jnumber` are in play. See §4.

## 3. ⛔ ZERO CORPUS COVERAGE — WHY A TOTAL HANG WENT UNNOTICED

`scripts/test_corpus_snobol4.sh` runs demo programs by explicit `run_test` lines: `demo_wordcount`, `demo_treebank`, `demo_claws5`. **There is no `json` row anywhere in the runner** — `grep -n json scripts/test_corpus_snobol4.sh` returns nothing. The 293-line JSON de-serializer, one of the named workhorse demos, has never been under the corpus gate. A program that hangs on a 5-byte input sat green because nothing ran it.

**Whatever fixes the hang must also land a corpus row**, or the next regression is equally invisible. `citm_catalog.json` (1.7 MB) is too slow for the 30 s corpus budget; the row should use a small deterministic input with commas, objects, arrays and escapes, and a `.ref` from the live oracle.

## 4. FENCE PLACEMENT — LON'S QUESTION, ANSWERED

Lon asked in-chat whether the **FENCE0** (bare `FENCE`) he had put after a right-curly / right-bracket might be *invalid* — *"Would that ever prevent a correct form?"* — noting that **FENCE1** (`FENCE(P)`) is the easier one to distribute, since you place it wherever the left context makes every alternative an exclusive possibility.

**Answer: the FENCE0s in `json.sno` are sound and cannot reject a well-formed JSON text.** Two independent reasons:

1. **A FENCE0 is only reached after every choice point to its RIGHT is exhausted.** In `[{"a":1},2]` the `ARBNO(',' …)` choice point is created *after* the fence was passed, so it is the newer alternative and is retried first. On valid input something to the right always succeeds, and the fence is never touched.
2. **Lon's own exclusivity criterion already holds at that alternation.** `jvalue` is discriminated by exactly one character of left context — `"` → string, `-`|digit → number, `{` → object, `[` → array, `t`/`f`/`n` → the literals — all mutually exclusive. There is no sibling alternative a cut could wrongly foreclose, and a balanced `{…}` has exactly one parse.

Two refinements worth making anyway:

- **Definition-site vs use-site.** `json.sno` fences *inside* the `jobject`/`jarray` definitions (after the close token and its deferred action), so the cut binds at every use. `json-match-fence.sno` instead fences at the use site (`| jobject FENCE` inside `jvalue`). Definition-site is broader and is safe *today* because `jobject`/`jarray` occur only inside `jvalue` — but FENCE0 is a **global** cut: back into it and the whole match dies rather than failing locally. Reuse either pattern in a context with a genuine outer alternative and that becomes a silent wrong answer. Use-site placement is correct-by-construction; definition-site rests on an invariant nothing checks.
- **⭐ A fence is MISSING on strings.** `jstrbody = jchunk ARBNO(jescape jchunk)` is unfenced in *both* files. Once inside the quotes a JSON string is fully deterministic — textbook exclusive left context — so a `FENCE` after the closing `dq` is sound by Lon's rule and retires one choice point per string. On `citm_catalog.json` that is the largest single CAS reduction available, and it is the one fence the family does not yet have.

## 5. SIDE OBSERVATION — `match_ms` LOOKS WRONG AFTER THE NS-TIME CHANGE

SCRIP prints a leading `match_ms=675791` line on `[1]` (3 bytes of input); SPITBOL prints no such line at all. 675,791 "ms" is 11 minutes for a 3-byte parse, so the figure is not milliseconds. s249 moved SCRIP, SPITBOL and CSNOBOL4 to a nanosecond `TIME()` (`x64` commit `ec80390e3`); this looks like a unit mismatch left behind in the demo's own arithmetic, or in SCRIP's `TIME()`. Cheap to check, and it matters because `match_ms` is exactly the number a JSON benchmark would quote.

## 6. RELATED, ALREADY QUEUED

Rank-0 row `table-int-keys-and-nd-subscript` (*"TABLES STRINGIFY EVERY INTEGER KEY, AND N-D ARRAY ACCESS RE-ENTERS THE SUBSCRIPT DISPATCHER ONCE PER DIMENSION"*, HQ s249) lands directly on this workload: the de-serializer builds one TABLE per JSON object, so the object-creation half of Lon's "both sides" is gated by that row. Sequence the hang first (nothing runs without it), then the table row, then measure.
