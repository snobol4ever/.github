# FINDING-2026-07-31-CLAUDE-SN4-TAG3-ZERO-PRESERVING-DTYPE-RENUMBER.md

**Session s229 (2026-07-31). SCRIP branch `tag-renumber-s229`, commit `50689805`. NOT BUILT, NOT CROSSCHECKED.**

## 1. THE DECISION

Two prior designs existed. Both were evaluated by brute-forcing every predicate over the full live tag set + 64 user datatypes rather than arguing:

| predicate | s212 (A) | s228 (B) | s229 (chosen) |
|---|---|---|---|
| is numeric | `test al,1` | `test al,1` | `test eax,1` |
| is string | `test al,4` | **IMPOSSIBLE** | `test eax,DT_NOTSTR_MASK →Z` |
| BOTH INT | `or;cmp eax,1` | `or;cmp eax,1` | `and;cmp eax,DT_I` |
| BOTH REAL | `and;cmp eax,3` | `and;cmp eax,3` | `and;cmp eax,DT_R` |
| BOTH NUMERIC | `and;test al,1` | `and;test al,1` | `and;test eax,1` |
| BOTH STRING | `and;test al,4` | **IMPOSSIBLE** | `or;test eax,DT_NOTSTR_MASK →Z` |
| SNUL vs S | `test al,8 →Z` | `test al,4 →Z` | `test eax,DT_CHARS_BIT →Z` |

**s228 (B) is disqualified**: cannot express `is string` or `BOTH STRING` at any mask/constant. Lexical comparison and concatenation are both-string consumers — the gap is not cosmetic.

**s212 (A) requires DT_SNUL ≠ 0**, which destroys the bulk memset init that mints null strings for free. `rt_gva_island` memsets the entire global variable area; `by_name_dispatch` memsets grown descriptor heap; `gc_heap` zeroes aggregate payload. All three rely on zero == null string. Moving SNUL off zero converts all three to descriptor-pattern fill loops — same O(n), but the init cost is real and the win is available without it.

**The zero-tag constraint is structural, not stylistic.** 0 is the OR-identity and AND-annihilator. With SNUL=0: `or eax,ecx ; cmp eax,DT_I` admits `(INT, 0)` as both-int. And SNUL cannot carry a STRING class bit while being 0, so `BOTH STRING` via `and/test` dies. Brute-forced over all assignments of I/R/S with SNUL pinned 0: **7 of 8 predicates are simultaneously achievable, never 8.**

**The surrendered predicate is the cheap one.** The SPITBOL joint-real identity `result tag = (L|R)` only pays for code that does NOT branch. Inlining the add requires branching on BOTH-INT first; the result tag is then a per-arm compile-time constant (`mov [slot], DT_I` / `mov [slot], DT_R`). So surrendering `L|R` costs nothing. `I|R = 0x07` is deliberately not a tag.

## 2. THE LAYOUT

```
bit0 = NUMERIC    bit1 = CHARS    bit2 = REAL    aggregates: stride 8 from 0x08

DT_SNUL = 0x00    DT_P  = 0x08   DT_E     = 0x38   DT_X    = 0x58
DT_S    = 0x02    DT_A  = 0x10   DT_FH    = 0x40   DT_BLK  = 0x60
DT_I    = 0x03    DT_T  = 0x18   DT_PLVAR = 0x48   DT_FAIL = 0x68
DT_R    = 0x05    DT_C  = 0x20   DT_PLREF = 0x50   DT_DATA = 0x70 (stride 8)
                  DT_N  = 0x28
                  DT_K  = 0x30
```

A/T adjacent at stride 8 → array+table share one subscript range guard: `lea eax,[v-DT_A]; cmp eax,8; jbe`.

## 3. TWO PREREQUISITES FIXED IN THE SAME COMMIT

**⛔ The asm-is-symbolic claim was false (neither design doc records this).** `GOAL-DESCR-TAG-ENCODING.md §5` states "No hand-edited immediates." `rtx_match.S:963,965` compared tags against literal `99` and `1`. A renumber trusting that claim builds clean, passes every `_Static_assert`, and silently corrupts `rt_dcap_step`'s arm selection at runtime. Now symbolic.

**`rtx_arith.S`'s range trick was dead on any renumber.** The `tag <= DT_S` unsigned test (`cmp eax,DT_S; ja`) was only valid while `DT_SNUL==0 && DT_S==1`. Replaced with the `(a|b) & DT_NOTSTR_MASK == 0` combined form, which is simultaneously cheaper (two instructions, no per-operand branch) and correct under any string-class assignment.

## 4. GATES RUN

- ✅ Layout gate: `scripts/util_tag_layout_verify.py` 11/11 PASS (tree-reading, not hardcoded)
- ✅ 11 `_Static_assert`s compile clean, `sizeof(DESCR_t)` still 16
- ✅ `descr.h` ↔ `rtx_abi.inc` cross-check: 18 tags, zero mismatch (`rtx_abi.inc` was carrying only 10 of 19 tags; now all 18 plus class masks)
- ✅ `rtx_arith.S` and `rtx_match.S` assemble clean
- ⛔ NO FULL BUILD — NOT RUN
- ⛔ NO CROSSCHECK — WATERMARK NOT RE-PROVEN
- ⛔ NO `.s` REGEN — templates emit `(long)DT_I` etc. as literal immediates; emitted bytes change tree-wide once this lands on main

## 5. WHAT IS OWED BEFORE MAIN

1. **TAG-0** — `GOAL-DESCR-TAG-ENCODING.md §7` mandates: run 0(d) on the arith benchmarks to confirm the dispatcher is actually entered. s203 recorded integer inlining made `rt_num_arith` go cold. If it is still cold, this rung optimizes a bypassed path.
2. **Full build + both-mode crosscheck**, watermark re-proven at session start and held exactly.
3. **`.s` regen ×3** (`util_regen_benchmark_s_artifacts.sh`, `util_regen_feature_s_artifacts.sh`, `util_regen_demo_s_artifacts.sh`).
4. **NOT concurrency-safe with the ζ ladder** (41 red pattern programs at HEAD). Lon's routing.

## 6. FILES CHANGED (6)

`src/contracts/descr.h` · `src/runtime/rtx/rtx_abi.inc` · `src/runtime/rtx/rtx_init.c` · `src/runtime/rtx/rtx_arith.S` · `src/runtime/rtx/rtx_match.S` · `scripts/util_tag_layout_verify.py` (new gate)
