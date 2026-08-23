# FINDING — ONE ROOT DEFECT, TWO HATS: WE KEY EVERYTHING BY STRING AND COMPARE WITH `strcmp`

**Seat:** hq_P · **2026-08-22 s258** · **Class:** MEASURED · **RT_OPT=`-O2 …`**, pristine, SCRIP `3f951354`
**Outputs verified before any number was believed:** `roman` check 1102 · `table_access` check 250500 — both match the clean oracle.

| kernel | SCRIP Ir/iter `-O2` | SPITBOL clean | ratio `-O2` | inherited `-O0` |
|---|---|---|---|---|
| `roman` | 52,455 | 7,966 | **6.58x** | 8.4x |
| `table_access` | 754,973 | 359,532 | **2.10x** | 2.8x |

`-O2` buys 1.28x on `roman` and 1.33x on `table_access`. **The gap is not an `-O0` artifact.**

## The two profiles say the same thing

**`roman`** — variable resolution by NAME: `_var_bucket_find` 21.65% (3,174,837 calls, **71 Ir/call**, 159/iter) +
`NV_GET_fn` 10.44% + `NV_SET_fn` 2.82% + `__strcmp_avx2` 9.64% (**250 strcmp per iteration**) ≈ **44%**.
Our emitted BB slab is **11.80%**. SPITBOL's variable access `b_vra` is **3.97%**.

**`table_access`** — key resolution by STRING: `tbl_key_str` 13.57% + `table_find_pair` 10.34% + `__strcmp_avx2`
6.87% ≈ **31%**, plus `rt_agg_alloc` 8.84%. Emitted slab 23.50%.

⛔ **NO LINEAR SCAN ANYWHERE. Every Ir-per-call is 20–80.** The functions are well written. **The defect is the call
count and the representation, not the callee.**

## The mechanism, from the source

```c
#define TABLE_BUCKETS 256                    /* core.h:96 -- compile-time constant, NEVER resized */
#define VAR_BUCKETS   512                    /* core.c:2191 */
#define FUNC_BUCKETS  128                    /* core.c:2493 */
static unsigned _tbl_hash(const char *key) { unsigned h=5381; while(*key) h=h*33^(unsigned char)*key++; return h % TABLE_BUCKETS; }
TBPAIR_t *table_find_pair(TBBLK_t *tbl, const char *key) { unsigned h=_tbl_hash(key);
    for (TBPAIR_t *e=tbl->buckets[h]; e; e=e->next) if (strcmp(e->key,key)==0) return e; return 0; }
```

Every table access on an **integer** key runs `tbl_key_str`: a **division loop** to render decimal
(`do { t[n++]='0'+u%10; u/=10; } while(u)`), a `\001i` datatype prefix, a djb2 hash **over the digits**, then
`strcmp` on chain match. Variable access does the identical thing with the variable's NAME.

⭐ **The `\001i`/`\001n`/`\001r`/`\001l`/`\001t` prefixes are SNOBOL4's required ordering — datatype first, then
value (Lon s258).** The encoding is SEMANTICALLY CORRECT. It is the REPRESENTATION that is expensive. Any cure must
preserve datatype-then-value ordering — a tagged key compared natively does, a raw integer compare does not.

## Ruled priorities for the RT campaign

1. ⭐⭐⭐ **BAKE VARIABLE CELL ADDRESSES AT COMPILE TIME — worth ~40% of `roman`.** This is exactly
   `byname-bake-cell-address` (`8c1f2d41`), which moved beauty **2.26x** by baking **procedure** name resolution.
   **The identical defect exists for VARIABLES and the cure was never applied.** It also explains why that fleet-day
   moved beauty and left `roman` at 1.01x: beauty is procedure-dense, `roman` is variable-dense.
2. ⭐⭐ **TAGGED TABLE KEYS — worth ~30% of `table_access`.** Replace the formatted-string key with a
   `{datatype, value}` key hashed and compared natively, preserving datatype-then-value ordering. Deletes the
   division loop, the digit hashing, and the `strcmp`.
3. ⭐ **`TABLE(512)` IS IGNORED and the bucket count never grows.** `table_new_args(init,inc)` stores `init`/`inc`
   but always allocates the fixed 256 buckets. Latently **O(n²/256)** — benign at the benchmark's 500 entries
   (~2/chain), 390 `strcmp` per lookup at 100k. A semantic gap *and* an asymptotic one.
4. ⚠️ **Hand-ASM + free r10/r11 + drop the RTCC veneer — REAL BUT BOUNDED, 10–15%.** With ~600 runtime calls per
   `roman` iteration the boundary cost is genuinely multiplied, so it is worth having; but it makes a 71-instruction
   function perhaps 50. **It cannot reach a 44% cluster that should not be called at all.**
5. ✅ **ARRAY IS CLEAN — nothing to do.** `array_get`/`array_set` are O(1) (`a->data[i - a->lo]`), bounds-checked;
   `rt_table_idx_get/set` guard on `base.v != DT_T` so arrays never enter the table path. Lon's O(n²) suspicion was
   correct for TABLE asymptotically and **wrong for ARRAY** — checked, not assumed.

## Corrections owed

- **My own P-0 hypothesis was DISPROVEN.** I predicted ~5,600 Ir per pattern operation and a pattern-engine
  bottleneck, derived by dividing aggregates by an assumed operation count. The pattern-defer cluster is 22.3% at
  35–64 Ir/call. **Arithmetic on aggregates produced a confident wrong answer; the profile produced the right one.**
- **A 21x wall-clock "win" I reported was invalid** — SPITBOL's 1048 ms was measured *under callgrind*, SCRIP's
  48 ms natively. Native, same fixed work: SCRIP 51 ms, SPITBOL 23 ms. Retracted within the minute.
