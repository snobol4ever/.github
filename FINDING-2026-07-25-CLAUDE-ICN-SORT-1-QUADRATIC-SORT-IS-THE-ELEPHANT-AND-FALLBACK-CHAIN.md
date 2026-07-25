# FINDING — ICN SORT-1/SORT-2: the elephant was an O(n²) sort, not dispatch (2026-07-25, s161, Claude Opus 4.5)

**SCRIP commits:** `2d191182` (SORT-1), `9a82c7e2` (SORT-2). Both LOCAL ONLY — push BLOCKED, no credential this session.
**Suite:** PASS=249 FAIL=12 XFAIL=32 after each commit (watermark, zero regression).
**Build:** `RT_OPT=-O0` throughout (O0-DEV FACT RULE). Every number below is `-O0`.

---

## Headline

`tgrlink` Ir **2,242,064,012 → 1,543,486,439 = −31.2%, 1.453×**. Wall 350ms → 251ms (1.39×).
Honest geomean vs `iconx` **0.573× → 0.666×**. Output byte-identical to the oracle at every step.

---

## What s160's cursor asked, and the answer

s160 left: *"the 227M strcmp cost is still unattributed, re-derive its caller first."*

Caller attribution (`callgrind_annotate --tree=caller`) at baseline:

| caller of `__strcmp_avx2` | Ir | calls |
|---|---|---|
| `script_try_call_builtin_by_name` | 90.4M (4.03%) | 4,331,127 |
| `try_call_builtin_by_name` | 80.1M (3.57%) | 3,610,905 |
| `data_field_ptr` | 23.1M (1.03%) | 1,123,827 |
| `NV_GET_fn` | 11.6M (0.52%) | 580,301 |

So ~170M of the 224M is the two dispatch functions. **Question closed.**

## But the real elephant was somewhere nobody had looked

s160 also flagged `VARVAL_fn` as "6,630,400 calls = 12.4 per dispatch, 11.3%" and proposed an **asm leaf** for it.
**That would have been the wrong fix.** Line-level annotation shows those calls are not spread across the builtin
bodies at all — **6,476,858 of the 6,630,400 come from ONE source line**:

```
by_name_dispatch.c, sort() on a table:
    else { const char *sa = VARVAL_fn(a), *sb = VARVAL_fn(b); cmp = strcmp(sa?sa:"", sb?sb:""); }
```

That line sits in the inner loop of an **O(n²) insertion sort**. Both sort paths had it — the table sort
(`BID_sort` / `DT_T`) and the list sort (`BID_sort`/`BID_sortf` / `DT_DATA` list frame). `VARVAL_fn` on a `DT_I`
does `snprintf` + `rt_ws_strdup_c`, so **every comparison minted two heap strings.**

Cost of that single loop on `tgrlink` (3,238,429 comparisons):

| component | Ir | % of program |
|---|---|---|
| `VARVAL_fn` (6,476,858 calls) | 239.6M | 10.69% |
| `strcmp` (3,238,429 calls) | 72.7M | 3.24% |
| `IS_INT_fn` | 42.1M | 1.88% |
| loop body + shifting | ~142M | ~6.3% |
| **total** | **~497M** | **~22%** |

⛔ **LESSON, and it is the same lesson as s159's `-O2` and s160's jump table: making each step cheaper cannot
fix a bad complexity class.** An asm `VARVAL_fn` leaf would have shaved maybe 30% off 239.6M. Deleting the
quadratic loop removed 497M *and* took `VARVAL_fn` off the profile entirely. **Before optimizing a function with
a huge call count, find out whether ONE caller is generating all the calls, and what its complexity class is.**

## SORT-1 — the fix (`2d191182`)

- **Stable merge sort** replaces the stable insertion sort. Identical permutation by construction: the old loop
  breaks on `cmp <= 0` (stable); the merge takes from the left unless the right is strictly less (stable); one
  stable order exists for a given comparator, so **output cannot move**.
- **`sort_key_cstr()`** — allocation-free key strings: `DT_S` returns `.s`, `DT_SNUL` returns `""`, `DT_I`
  formats into a **stack** buffer, everything else falls back to `VARVAL_fn`. Byte-identical strings, zero heap
  traffic on the hot shapes.
- **The comparator predicate is unchanged** (both-int numeric, else strcmp of key strings).

Result: Ir 2,242M → 1,673M (**−25.4%**), wall 350→261ms, `VARVAL_fn` drops off the top-13 entirely.

## SORT-2 — the fallback chain (`9a82c7e2`)

`try_call_builtin_by_name` falls back to `script_try_call_builtin_by_name` for names its BID jump table does not
own. That function is a **linear chain of 288 `strcmp`/`strncmp` arms** — never given the BID-1 treatment.
138.2M Ir (8.26%) for **18,831 calls = 7,341 Ir each.**

**MEASURED which names arrive** (env-gated entry probe `SCRIP_STCB_PROBE`, since removed) rather than guessed:
exactly **two** — `where` (9,416) and `seek` (9,415), both real Icon file builtins, both sitting ~230 arms deep.

⚠ **A first-char guard here would have been WRONG and I nearly shipped it.** Scanning only lines 1630–2400
showed all literals starting with `$` or `_`, which suggests `if (fn[0] != '$' && fn[0] != '_') return 0;`.
Auditing the **full 2,259-line body** found 288 literals of which **68 are bare names** — `open`, `close`,
`trim`, `reverse`, `length`, `substr`, `where`, `seek` … several of which are also real Icon builtins. **Audit
the whole function, not the window you happened to print.**

Hoisted the two arms to the front, proven safe first: no `strcmp` literal in lines 1630..3328 equals `where`/
`seek`, no `strncmp` prefix covers either, and there is no `switch`/`memcmp`/`strstr` on `fn` in that region —
so the hoist cannot shadow an arm that previously won. Ir 1,673M → 1,543M (**−7.8%**).

---

## ▶ Where the remaining time goes (post-fix `tgrlink` profile)

| item | Ir | % |
|---|---|---|
| `try_call_builtin_by_name` self | 247.5M | 16.04% |
| `__strcasecmp_avx2` | 100.2M | 6.49% |
| `bid_of` | 63.8M | 4.13% |
| `__strcmp_avx2` | 63.3M | 4.10% |
| `FIELD_GET_fn` | 61.9M | 4.01% |
| `rt_gcheap_carve` + `rt_gcheap_alloc` | 88.5M | 5.73% |
| `data_field_ptr` | 39.2M | 2.54% |
| `____strtol_l_internal` | 37.3M | 2.42% |

**NEXT RUNG — kill the per-dispatch name walks.** The preamble walks the SAME name string **three times** per
dispatch before the jump table is reached: the dtax hash loop (45.0M, 2.91%), `bid_of`'s hash loop (37.7M,
2.44%), and a second `strlen` feeding the SNOBOL4-uppercase switch (22.2M, 1.44%) — ~127M (8.2%) to turn a name
into a decision, 533,135 dispatches. Two tracks, cheapest first:
1. **Compute the length ONCE** and thread it through `bid_of`, the dtax loop bound, and `_fl`. Mechanical, safe.
2. **The structural one (s159/s160 track 1, still unstarted):** `lower_icon.c` resolves a known-builtin callee
   to its `BID_*` at LOWER time and emits the integer, so the runtime never sees a name at all. Kills `bid_of`,
   the dtax hash, and most of the 247.5M preamble.

**THEN the by-name field elephant:** `strcasecmp` 100.2M is entirely `FIELD_GET_fn` (71.6M, 1,704,085 calls) +
`FIELD_SET_fn` (28.4M, 675,009 calls), both linear scans over `t->fields[i]`. 44 by-name list-frame sites remain
in `by_name_dispatch.c` alone (27 GET + 17 SET) using literal `"frame_elems"`/`"frame_size"`/`"gen_type"`/
`"frame_cap"`. **The `rt_list_view` constant-slot idiom (pattern_match.c) is the in-tree fix** — adopt it there.
⛔ Do **not** revive a `(DATBLK_t*, name-pointer)` memo cache: s160 already rejected it as unsound (a heap `fn`
buffer can be freed and reused at the same address; a stale hit is silently wrong).

---

## ⚠ Two things found and deliberately NOT changed

1. **SCRIP's sort order is not canonical Icon's.** Canonical `anycmp`
   (`refs/icon-master/src/runtime/rcomp.r`) orders by **type collating number first** via `order()`, comparing
   only within a type. SCRIP does "both-int numeric, else stringify both and strcmp". These agree on homogeneous
   tables/lists and **diverge on mixed-type ones**. This is a **correctness** rung, not a perf one; changing the
   order would move output on the 249 green tests. Left alone on purpose. **Own rung.**
2. **`geddump` really does diverge** — 11,222 lines vs the oracle's 10,145, unchanged by this session's work and
   not attributable to it (it diverged identically at baseline). Still has no FAIL-ZERO cluster.

## ⚠ Metric honesty

Wall-clock on this corpus is startup-dominated (`version` is 4ms of pure startup; `concord` moved 132→98→98ms
across changes that monotonically lowered Ir). **Ir is the honest metric; trust wall-clock only on `tgrlink` and
`geddump`.** `rsg` reports 2.83× and should be treated as noise/short-circuit until its DIVERGE is explained.

## ⛔ Honest gap to Lon's target

2–3× faster than `iconx` means **3.0× more from 0.666×**. This session bought 1.16× of it. No single rung on
this ladder is worth 3× — `iconx` is a bytecode interpreter (`switch((int)lastop)` in `interp.r`) and SCRIP is
still paying a by-name runtime call for work `iconx` does inline. The two structural rungs above (compile-time
builtin IDs, compile-time field numbers) are the ones that change the shape of the cost, and both are
compiler-side, not runtime-side.
