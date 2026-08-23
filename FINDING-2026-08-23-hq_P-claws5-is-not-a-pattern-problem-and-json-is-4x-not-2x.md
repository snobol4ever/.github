# FINDING: CLAWS5 is NOT a pattern problem (the engine already WINS 1.63x); the loss is entirely the action + TABLE build — and JSON is a 4.35x problem, not a 2x one

**Seat:** hq_P · **Date:** 2026-08-23 (s264) · **Tree:** SCRIP `ce48e3bb` (cures landed and pushed) from `a0859f7e`
**Instrument:** callgrind Ir at FIXED WORK, SCRIP **mode-4 native binary** vs `/home/resources/spitbol-bench-oracle/sbl -bf -d512m -i64m -s16m`, **RT_OPT=`-O0`** (FACT RULE — no `-O2` builds, ever).
**Method:** every ratio is a SLOPE — Ir(N=k) minus Ir(N=1), divided by k−1 — so process startup, dynamic linking, input read and (for SPITBOL) compile are removed from BOTH engines by construction. Output verified equal to the `.ref` on every arm before any number was believed.

## Lon's task (in-chat, s264)
*"Get CLAWS and JSON demos working faster than SPITBOL. Concentrate on just those two."*

## ⭐⭐⭐ THE RESULT THAT REDIRECTS THE WHOLE CLAWS5 EFFORT
`claws5-match.sno` is the same grammar with **zero captures and no `token()`**. It was already sitting in the corpus, and the delta against `claws5.sno` is therefore EXACTLY the cost of the deferred action + the 3-level TABLE build:

| arm | SCRIP Ir/iter | SPITBOL Ir/iter | verdict |
|---|---|---|---|
| grammar only (`claws5-match`) | 1,087,882 | 1,770,532 | ⭐ **SCRIP 1.63x FASTER** |
| full program (`claws5`) | 74,294,806 | 36,477,603 | 2.04x slower |
| **the delta — the action** | **73,206,924** | **34,707,071** | **2.11x slower** |

⭐ **THE PATTERN ENGINE IS NOT OUR PERFORMANCE PROBLEM ON THIS WORKLOAD — IT IS OUR BEST SUBSYSTEM.** 98.5% of claws5's cost is the deferred action and the table build. Per token (6,469 tokens/parse): SCRIP 11,317 Ir vs SPITBOL 5,365 Ir. ⛔ Anyone who opens claws5 expecting a pattern-engine campaign is optimising the 1.5% that already wins.

## THREE CURES LANDED — 74,294,806 → 61,233,041 Ir/iter, **−17.6%**, gap 2.04x → **1.68x**
Fixed cost cross-checks unchanged across the change (5,110,059 → 5,109,193), which is what says the slope is clean.

1. **`descr.h` — `always_inline` on the descriptor predicates.** `RT_OPT` is `-O0` by FACT RULE and **at `-O0` gcc inlines nothing**, so `IS_VARREF_fn`/`IS_FAIL_fn`/`IS_NAMETRAP_fn` were real calls with full prologues: **32.7 calls per token at ~13 Ir each** to answer `v.v == DT_N`. `aggregates.c` already knew this (`_tbl_hkey`/`_tbl_eq_d`/`_tbl_lower` all carry it); `descr.h` never did. **79,404,865 → 77,349,470** (N=1 basis).
2. **String hash word-at-a-time, in BOTH spellings** (`aggregates.c:_tbl_h_str` + `rtx_table.S:.Ltf_h_str`). djb2 was one byte per iteration and the ASM compiled to **eleven instructions per byte**. Now eight bytes per multiply, with an **overlapping** 4/2/1-byte tail so no load ever reaches past `p+n` — the one-load-and-mask alternative can cross into an unmapped page. Counted-string discipline (Lon s263) preserved exactly: every load is length-driven, nothing tests a byte for zero. **77,349,470 → 75,531,499.**
3. ⭐ **The table READ path no longer allocates, and no longer looks the key up twice.** `rt_subscript_var_container_only` looked the key up and — unless the hit was a nested TABLE/ARRAY — allocated a `VCELL_t`, filled seven fields and returned a NAMETRAP, whose only consumer is the `rt_deref` the emitter emits on the very next instruction, which walked into `rt_deref_slow`'s `if (vc->tbl)` arm and **looked the same key up again**. One read of one table cost two hashed lookups, one heap allocation and a GC root. It now returns the value directly. **75,531,499 → 66,342,234**, and `table_find_pair_d` calls fall **109,360 → 90,566 per parse**.
   ⛔ **Why returning a bare value is safe, and the proof is in the LOWERER, not the runtime:** `container-only` is set at exactly two sites in `lower_snobol4.c` — line 392 (every link of an RVALUE chain) and line 860 (`k < nidx - 1`, the NON-FINAL links of an lvalue chain). The final link of an lvalue chain lowers to `rt_subscript_var`, which still builds the assignable nametrap. **Nothing is ever assigned through this function's result.** If a third `container-only` site is ever added it must obey that rule or this is wrong.

**Gates (`ce48e3bb`):** corpus m3 358/2, m4 357/2+1SKIP — both fails are the STANDING reds only (`160_pat_alt_inner_gen_resume`, hq_C/seat01's open altgen row, and the deliberate `demo_treebank`) plus the standing SKIP `132_pat_fence_eps_recur_shallow`. `test_gate_emit_no_lang` rc=0, `test_gate_template_medium_invisible` rc=0. **C/ASM hash agreement negative-tested both directions** (`SCRIP_RTX_TABLE=1` and `=0` both answer `check: 6469`) — that is what proves the two spellings of the new hash are one algorithm.

## ⛔ JSON IS A DIFFERENT AND WORSE PROBLEM — 4.35x, MEASURED FOR THE FIRST TIME
`json.sno` HANGS on any realistic input (hq_C's altgen defect, seat01's row, verified independently here at `a0859f7e` pristine: ladder 2 pass / 5 red, json m3 rc=124). ⭐ **It is still measurable today** on inputs where every object/array has exactly ONE member — that never reaches the second ARBNO iteration, so it dodges the defect entirely while still driving TABLE creation, ARRAY building, the shift/reduce value stack, string decode and the deferred captures. 400 nested single-member objects, both engines agreeing on `check: 400/0/1/0/0/0/0/400`:

| | SCRIP Ir/iter | SPITBOL Ir/iter | verdict |
|---|---|---|---|
| json (400 nested objects) | **8,474,055** | 1,949,584 | ⛔ **4.35x slower** |

**Where it goes (SCRIP, N=11 profile):** `sno_array_from_proto` 7.94% + `array_new` 6.73% = **14.7% in ARRAY CREATION**, on an input containing **zero JSON arrays** — the cost is the per-object key-order `ARRAY(n)`. 4,405 calls (exactly 400/iteration) for **one-element** arrays. Then the by-name dispatch cluster (`try_call_builtin_by_name_bl` 5.62% + `rt_call_arr_impl` 2.08% + `rt_call_arr_bl` 1.79%) = **9.5%**, `patv_slot` 2.80%, `NV_SET_fn` 2.41%, `rt_ws_strdup` 2.22%.
⭐ `ARRAY(n)` reaches the runtime as a **STRING prototype** that `sno_array_from_proto` re-parses with `strchr` + `strtol` on **every single call** (4,405 `strtol` calls per 11 iterations, measured). That is the next JSON rung and it needs no semantic ruling.

## ⛔ A MEASUREMENT CONFLICT I DID NOT RESOLVE — READ BEFORE "FIXING" `_tbl_grow`
`_tbl_grow` fires on **10,520 of 17,973 table inserts (59%)** in claws5 and costs ~1.5M Ir with its allocator and memcpy. The obvious cure is raising the first-allocation floor above 1. ⛔ **DO NOT DO IT BLIND.** `aggregates.c:342` records that floor 1 vs floor 4 was **already measured, on CLAWS5 itself**, and floor 4 lost: 499K cache misses vs 375K, at a cost of 1.6% Ir on the integer kernel. So Ir and cache-misses **disagree in opposite directions here**, my instrument is Ir only, and hardware counters are recorded as unusable on this box. Lowering Ir here could flatter the published number while costing real time. Left alone deliberately; it needs an arm that can measure both.

## NEXT, IN ORDER
1. **JSON `ARRAY(n)` prototype re-parse** — pass the bounds as integers instead of re-parsing a string per call. No semantic ruling needed. 14.7% of json.
2. **By-name builtin dispatch** — ~9.2% of claws5, ~9.5% of json. `IDENT()` costs ~237 Ir of dispatch machinery before it does its one-instruction job. ⛔ The cure must be **class-wide**: NO-PER-OP-FILTER (Lon 2026-08-20) forbids an exception list of hot builtins.
3. `table_set_descr_d` at 253 Ir/call and `table_find_pair_d` at 79 Ir/call are the remaining table cost; both are `-O0` C/ASM and are the natural GOAL-RTCC targets.
4. json's realistic (multi-member) numbers stay blocked on seat01's altgen row.


---

## ⛔⛔ ADDENDUM, SAME SESSION (s264, SCRIP `3a644af1`) — A SELF-CORRECTION, AN UNEXPLAINED UNBLOCK, AND TWO NEW DEFECTS

### 1. ⛔ SELF-CORRECTION: "ARRAY creation is 14.7% of json" WAS WRONG
I read that off the function-level profile. It is mostly the **five ONE-TIME startup arrays** (`vs`/`ks` are `ARRAY(262144)`), not per-iteration cost. `ARRAY(n)` with an integer bound did snprintf → strchr/strtol → strdup, a full round trip through text for bounds we already had; `sno_array_from_proto` then refilled every element AFTER `array_new` had already laid down NULVCL — a second pass over 524,288 descriptors at startup. Cured (calls `array_new(1,n)` directly):
- json **N=1: 30,944,003 → 21,989,356 Ir (−29%)** — almost all of it startup
- json **slope: 8,474,055 → 8,110,738 Ir/iter (−4.3%)**, gap **4.35x → 4.16x**
**The honest per-iteration number is 4.3%, not 14.7%.** `->proto` is no longer stored; `agg_prototype()` already reconstructs it lazily and all four `PROTOTYPE()` forms were negative-tested against `x64/bin/sbl -bf`.

### 2. ⭐⭐ json NO LONGER HANGS — AND I AM NOT CLAIMING THE CURE
With that commit the standing front red goes GREEN: corpus **m3 358/2 → 359/1, m4 357/2 → 358/1+1SKIP**, `corpus/probe/altgen` goes **2/7 → 7/7**, and `json.sno` parses the **REAL 631 KB benchmark input** to `check: 1264/1050/4754/2108/1/2791/1946/10` — byte-identical to the SPITBOL oracle AND to the committed `json.ref`.
⛔ **I cannot explain the mechanism and the row is not mine.** `160_pat_alt_inner_gen_resume` contains **zero** `ARRAY` calls, so there is no direct path from this edit to that test. Either it cures a heap corruption whose downstream symptom was the alternation failure, or it is allocation-timing masking. **Evidence against fragile masking:** 160 passes at `SCRIP_GC_STRESS` off / 25 / 7 / 1, all four. hq_C and seat01 own the row and the mechanism is theirs to confirm before anyone calls it closed.

### 3. ⛔ TWO NEW DEFECTS FOUND, BOTH ROUTED TO hq_C (correctness lane)
- **m3/m4 DIVERGENCE on real json.dat.** mode-3 answers correctly; the mode-4 native binary floods `rt_dcap_pump: CORRUPT CAPTURE ENTRY refused — len=2054018274 saved_delta=2240949032 end=4294967306 exceeds subject length 371 (target 'seg', frame depth 2)` and never produces the check line. Reachable only now that json runs at all.
- **`SCRIP_GC_STRESS=7` SIGSEGV.** json on the 5-byte witness `[1,2]` dumps core at stress 7; passes at off / 25 / 1.

### 4. ⛔ INSTRUMENT GAP — REAL json.dat IS NOT YET CALLGRIND-MEASURABLE
Under valgrind, json on the 631 KB input dies before printing its check line, and **N=1 and N=3 return the same Ir** (395,206,490 vs 395,206,511 in m3; 33,534,491 vs 33,534,552 in m4) — the signature of a program that quit early, not a fast one. It runs correctly OUTSIDE valgrind. So the only quotable json ratio remains the 400-nested-object workload above. ⛔ Do not publish a real-input json ratio until this is resolved; SPITBOL's own real-input slope IS measurable and is **70,808,448 Ir/iter** (N=1 74,783,170, N=3 216,400,066) for whoever gets SCRIP's arm working.
